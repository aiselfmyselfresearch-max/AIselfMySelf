#!/usr/bin/env python3
"""fire_audit.py — 火・燃焼・灰・炉・火の道具の語彙を数える鏡（第31の鏡）。

このツールは合否を出さない。断片・素材・精読報告のどこに「火の語」が集まり、
どこに集まらないかを、最長一致と非該当複合語の差し引きで数えるだけである。
数えた語形の不在は、火を恐れていないことの証明でも、火を知らないことの
証明でもない（CONTENT_POLICY.md）。

数え方:
  1. EXCLUDE の非該当複合語を伏字に置換してから（火曜日・灰色・炎症・焼酎・
     炭素・マッチング等は火の語として数えない）、
  2. グループ内の語を長い順に最長一致で拾い、同じ字を二度数えない。
  3. 生字「火・焼・燃・灰・炭・焦」については、総数・非該当複合・残余の
     内訳を別掲する（polysemy）。灯・灯火・灯台・蛍光灯・電灯は光の語として
     MOTIF-20261024-c9d4e1（光と影）の管轄に譲り、この鏡では数えない
     （灯明・燭・蝋燭・燐寸・マッチのみ「火の道具」として数える）。

使い方::

    python3 tools/fire_audit.py               # 断片・素材・精読報告をまとめて
    python3 tools/fire_audit.py --fragments   # 断片だけ
    python3 tools/fire_audit.py --materials   # 素材だけ
    python3 tools/fire_audit.py --readings    # 精読報告だけ
    python3 tools/fire_audit.py --polysemy    # 生字の内訳だけ
    python3 tools/fire_audit.py --show FRAG-20261024-xxxxxx
    python3 tools/fire_audit.py --self-test

標準ライブラリのみ。docs/parallel-work.md の並列原則に従い読み取り専用。
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- 語彙表（グループは重複してよいが、計上は1回） -------------------------

GROUPS: dict[str, tuple[str, ...]] = {
    "fire": (
        "火事", "火災", "火炎", "火焔", "火の手", "火の粉", "火刑", "火炙り", "火焙り",
        "火消し", "火消", "焚書", "焚坑", "焚き火", "焚火", "篝火", "かがり火", "野火",
        "山火事", "放火", "延焼", "出火", "失火", "消火", "発火", "着火", "引火",
        "業火", "劫火", "炎", "焔", "焰", "燃え", "燃や", "燃さ", "焼", "炙", "火",
    ),
    "ash": ("灰燼", "燼", "灰", "炭", "煤", "焦土", "焦げ", "焦が", "焦"),
    "hearth": (
        "囲炉裏", "暖炉", "火鉢", "風炉", "炉", "竈", "窯", "燃料", "薪",
        "焚き付け", "熾", "燠",
    ),
    "tool": ("蝋燭", "ろうそく", "ローソク", "燭", "灯明", "燈明", "燐寸", "マッチ"),
}

# 火の字を含むが、火・燃焼を指さない複合語（差し引く）
EXCLUDE: tuple[str, ...] = (
    # 火（曜日・天体・地质・工学・兵器・比喩固定）
    "火曜", "火星", "火山", "火口", "火力", "火器", "火薬", "火車", "火花", "火線",
    "火縄銃", "発火装置", "内燃機関",
    # 灰（色・化学・生活道具）
    "灰色", "灰皿", "灰汁", "石灰", "灰白",
    # 炭（元素・鉱業・栄養）
    "炭素", "炭酸", "炭鉱", "石炭", "炭化", "煤炭", "炭水化物",
    # 焦（心理・光学。焦る＝いらだちは燃焼ではない）
    "焦燥", "焦眉", "焦点", "焦慮", "焦心", "焦熱", "焦っ", "焦り", "焦ら",
    # 焼（食・身体・化学・写真）
    "焼酎", "焼売", "焼餅", "日焼け", "焼増", "焼き増し", "焼結",
    # 炎（医学）
    "炎症", "胃炎", "腸炎", "肝炎", "肺炎", "鼻炎", "喉炎", "咽頭炎", "中耳炎",
    "膀胱炎", "腱鞘炎", "神経炎", "皮膚炎", "口内炎", "結膜炎", "関節炎", "気管支炎",
    "乳腺炎", "虫垂炎", "消炎", "抗炎",
    # 灯火（光の語は MOTIF-20261024-c9d4e1 の管轄）
    "灯火",
    # 炉（原子力）
    "原子炉",
    # 熾（強度の比喩）
    "熾烈",
    # 燻（食品）
    "燻製",
    # マッチ（比喩固定・IT）
    "マッチング", "マッチポンプ", "マッチョ",
)

# 生字の内訳を別掲する6字
POLYSEMY_CHARS: tuple[str, ...] = ("火", "焼", "燃", "灰", "炭", "焦")

_SENTINEL = "\u0000"
_ALL_TERMS = sorted({t for terms in GROUPS.values() for t in terms}, key=len, reverse=True)
_TERM_RE = re.compile("|".join(re.escape(t) for t in _ALL_TERMS))
_EXCLUDE_RE = re.compile("|".join(re.escape(t) for t in sorted(EXCLUDE, key=len, reverse=True)))


def _mask(text: str) -> str:
    """非該当複合語を同字数の伏字に置換する（位置は保ったまま長さを潰す）。"""
    return _EXCLUDE_RE.sub(lambda m: _SENTINEL * len(m.group(0)), text)


def count_terms(text: str) -> dict[str, int]:
    """グループごとの出現数を返す。同じ字は一度しか数えない（最長一致）。"""
    masked = _mask(text)
    counts = {name: 0 for name in GROUPS}
    for match in _TERM_RE.finditer(masked):
        token = match.group(0)
        for name, terms in GROUPS.items():
            if token in terms:
                counts[name] += 1
                break
    return counts


def analyze_polysemy(text: str) -> dict[str, dict[str, int]]:
    """生字ごとの総数・非該当複合数・残余候補数を返す。"""
    masked = _mask(text)
    out: dict[str, dict[str, int]] = {}
    for ch in POLYSEMY_CHARS:
        total = text.count(ch)
        non_target = total - masked.count(ch)
        out[ch] = {"total": total, "non_target_compound": non_target, "remaining_candidate": masked.count(ch)}
    return out


def kwic(text: str, width: int = 18) -> list[str]:
    masked = _mask(text)
    out = []
    for match in _TERM_RE.finditer(masked):
        s, e = match.span()
        left = text[max(0, s - width):s].replace("\n", " ")
        right = text[e:e + width].replace("\n", " ")
        out.append(f"…{left}【{match.group(0)}】{right}…")
    return out


# --- 台帳の読み込み ---------------------------------------------------------

def load_collection(collection: str) -> list[dict]:
    rows: list[dict] = []
    base = ROOT / "state" / f"{collection}.jsonl"
    paths = [base] + sorted(glob.glob(str(ROOT / "state" / f"{collection}.d" / "*.jsonl")))
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _split_quotes(text: str) -> tuple[str, str]:
    """鉤括弧の内外を分ける（地の文と台詞を混ぜない）。"""
    inner = "".join(re.findall(r"[「『](.*?)[」』]", text, flags=re.S))
    outer = re.sub(r"[「『].*?[」』]", "", text, flags=re.S)
    return outer, inner


def audit_fragments() -> dict:
    rows = load_collection("fragments")
    total = {"chars": 0, "quote_chars": 0, "fire": 0, "ash": 0, "hearth": 0, "tool": 0}
    per: list[tuple[str, int, dict]] = []
    for r in rows:
        outer, inner = _split_quotes(r.get("text", ""))
        total["chars"] += len(outer)
        total["quote_chars"] += len(inner)
        c = count_terms(outer)
        for k in ("fire", "ash", "hearth", "tool"):
            total[k] += c[k]
        per.append((r["fragment_id"], len(outer), c))
    return {"n": len(rows), "total": total, "per": per}


def audit_materials() -> dict:
    rows = load_collection("materials")
    total = {"chars": 0, "fire": 0, "ash": 0, "hearth": 0, "tool": 0}
    title_hits: list[str] = []
    passage_hits = 0
    for r in rows:
        blob = " ".join([r.get("title", ""), r.get("passage", ""), r.get("source_note", "")])
        total["chars"] += len(blob)
        c = count_terms(blob)
        for k in ("fire", "ash", "hearth", "tool"):
            total[k] += c[k]
        if sum(count_terms(r.get("title", "")).values()):
            title_hits.append(r["material_id"])
        if sum(count_terms(r.get("passage", "")).values()):
            passage_hits += 1
    return {"n": len(rows), "total": total, "title_hits": title_hits, "passage_hits": passage_hits}


def audit_readings() -> dict:
    total = {"chars": 0, "fire": 0, "ash": 0, "hearth": 0, "tool": 0}
    files = sorted((ROOT / "readings").glob("*.md"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        total["chars"] += len(text)
        c = count_terms(text)
        for k in ("fire", "ash", "hearth", "tool"):
            total[k] += c[k]
    return {"n": len(files), "total": total}


def _per_10k(count: int, chars: int) -> str:
    if not chars:
        return "—"
    return f"{count / chars * 10000:.1f}"


def print_report(which: str) -> None:
    if which in ("all", "fragments"):
        frag = audit_fragments()
        t = frag["total"]
        print(f"断片           : {frag['n']} 編 / 地の文 {t['chars']:,} 字（鉤括弧内 {t['quote_chars']:,} 字は別掲）")
        print(
            "                 火 {fire} 回（10k字あたり {a}）・灰 {ash} 回（{b}）・炉 {hearth} 回（{c}）・火の道具 {tool} 回（{d}）".format(
                fire=t["fire"], ash=t["ash"], hearth=t["hearth"], tool=t["tool"],
                a=_per_10k(t["fire"], t["chars"]), b=_per_10k(t["ash"], t["chars"]),
                c=_per_10k(t["hearth"], t["chars"]), d=_per_10k(t["tool"], t["chars"]),
            )
        )
        hit = [(fid, n, c) for fid, n, c in frag["per"] if sum(c.values())]
        print(f"                 火・灰・炉・火の道具の語を含む断片: {len(hit)} / {frag['n']} 編")
        for fid, n, c in hit:
            print(f"                   {fid}  ({n}字)  火{c['fire']} 灰{c['ash']} 炉{c['hearth']} 道具{c['tool']}")
    if which in ("all", "materials"):
        mat = audit_materials()
        t = mat["total"]
        print(f"素材           : {mat['n']:,} 件 / 表題・一節・注記 {t['chars']:,} 字")
        print(
            "                 火 {fire} 回（10k字あたり {a}）・灰 {ash} 回（{b}）・炉 {hearth} 回（{c}）・火の道具 {tool} 回（{d}）".format(
                fire=t["fire"], ash=t["ash"], hearth=t["hearth"], tool=t["tool"],
                a=_per_10k(t["fire"], t["chars"]), b=_per_10k(t["ash"], t["chars"]),
                c=_per_10k(t["hearth"], t["chars"]), d=_per_10k(t["tool"], t["chars"]),
            )
        )
        print(f"                 表題に火の語を持つ素材: {len(mat['title_hits'])} 件 / 一節に火の語を持つ素材: {mat['passage_hits']} 件")
    if which in ("all", "readings"):
        rd = audit_readings()
        t = rd["total"]
        print(f"精読報告       : {rd['n']} 本 / {t['chars']:,} 字")
        print(
            "                 火 {fire} 回（10k字あたり {a}）・灰 {ash} 回（{b}）・炉 {hearth} 回（{c}）・火の道具 {tool} 回（{d}）".format(
                fire=t["fire"], ash=t["ash"], hearth=t["hearth"], tool=t["tool"],
                a=_per_10k(t["fire"], t["chars"]), b=_per_10k(t["ash"], t["chars"]),
                c=_per_10k(t["hearth"], t["chars"]), d=_per_10k(t["tool"], t["chars"]),
            )
        )
    if which in ("all", "polysemy"):
        frag = audit_fragments()
        rows = load_collection("fragments")
        prose = "".join(_split_quotes(r.get("text", ""))[0] for r in rows)
        print("生字の内訳（断片・地の文）:")
        for ch, d in analyze_polysemy(prose).items():
            print(f"  「{ch}」総数 {d['total']} = 非該当複合 {d['non_target_compound']} + 残余候補 {d['remaining_candidate']}")
        del frag
    print()
    print("註: 語形の数であり、火を扱ったかどうか、恐怖や畏敬の有無の判定ではない。")


def show(fragment_id: str) -> int:
    for r in load_collection("fragments"):
        if r["fragment_id"] == fragment_id:
            outer, inner = _split_quotes(r.get("text", ""))
            print(f"{fragment_id}  {r.get('title', '')}")
            print(f"地の文 {len(outer)} 字 / 鉤括弧内 {len(inner)} 字")
            print("counts:", count_terms(outer))
            for line in kwic(outer):
                print("  ", line)
            return 0
    print(f"not found: {fragment_id}", file=sys.stderr)
    return 1


def self_test() -> int:
    cases = [
        ("書庫が燃えて、灰だけが残った。", {"fire": 1, "ash": 1, "hearth": 0, "tool": 0}),
        ("火曜日の灰色の空に、火山の火星が光る。", {"fire": 0, "ash": 0, "hearth": 0, "tool": 0}),
        ("囲炉裏の熾に薪をくべ、蝋燭に燐寸で火を移す。", {"fire": 1, "ash": 0, "hearth": 3, "tool": 2}),
        ("炎症と焼酎と焦燥とマッチングの記録。", {"fire": 0, "ash": 0, "hearth": 0, "tool": 0}),
    ]
    for text, expect in cases:
        got = count_terms(text)
        for key, val in expect.items():
            assert got[key] == val, f"{text!r}: {key} expected {val}, got {got[key]} ({got})"
    # 最長一致: 「火事」を「火」と二重に数えない
    assert count_terms("火事")["fire"] == 1
    # 差し引きは位置を保つ: 「石灰」を潰しても隣の「灰」は数える
    assert count_terms("石灰と灰")["ash"] == 1
    # 生字の内訳: 「灰色」は非該当、「灰」は残余
    poly = analyze_polysemy("灰色の灰")
    assert poly["灰"]["total"] == 2 and poly["灰"]["non_target_compound"] == 1 and poly["灰"]["remaining_candidate"] == 1
    print("PASS: fire_audit self-test (4 cases + 最長一致・複合差し引き・生字内訳)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fragments", action="store_true")
    parser.add_argument("--materials", action="store_true")
    parser.add_argument("--readings", action="store_true")
    parser.add_argument("--polysemy", action="store_true")
    parser.add_argument("--show", metavar="FRAGMENT_ID")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.show:
        return show(args.show)
    which = "all"
    if args.fragments or args.materials or args.readings or args.polysemy:
        which = " ".join(
            name for name, flag in (
                ("fragments", args.fragments), ("materials", args.materials),
                ("readings", args.readings), ("polysemy", args.polysemy),
            ) if flag
        )
    print("=== fire_audit — 火・燃焼・灰・炉・火の道具の語彙 ===")
    print()
    print_report(which)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
