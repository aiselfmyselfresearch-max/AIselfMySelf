#!/usr/bin/env python3
"""weather_audit.py — 天候・季節・体感の語彙を数える鏡（第30の鏡）。

このツールは合否を出さない。断片・素材・精読報告のどこに「空の語」が集まり、
どこに集まらないかを、最長一致と非該当複合語の差し引きで数えるだけである。
数えた語形の不在は、天候を経験していないことの証明でも、感受性の欠如の
証明でもない（CONTENT_POLICY.md）。

数え方:
  1. EXCLUDE の複合語を伏字に置換してから（非該当複合差し引き）、
  2. グループ内の語を長い順に最長一致で拾い、重複計上しない。

使い方::

    python3 tools/weather_audit.py               # 断片・素材・精読報告をまとめて
    python3 tools/weather_audit.py --fragments   # 断片だけ
    python3 tools/weather_audit.py --materials   # 素材だけ
    python3 tools/weather_audit.py --readings    # 精読報告だけ
    python3 tools/weather_audit.py --show FRAG-20261024-8719d1
    python3 tools/weather_audit.py --self-test

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
    "sky": (
        "天気", "天候", "空模様", "気象", "気圧", "気温", "湿度", "予報", "観測",
        "晴天", "快晴", "晴れ", "曇り", "曇天", "雨", "降雨", "大雨", "豪雨",
        "小雨", "五月雨", "時雨", "霧雨", "雪", "大雪", "吹雪", "みぞれ",
        "霰", "雹", "霜", "露", "霧", "靄", "嵐", "雷", "虹", "雲", "風",
        "北風", "秋風", "春風", "夜風", "そよ風", "凪",
    ),
    "season": ("季節", "四季", "春", "夏", "秋", "冬", "年末", "年の暮れ", "立春", "冬至"),
    "body": (
        "暑い", "暑さ", "寒い", "寒さ", "冷たい", "温かい", "暖かい", "濡れ",
        "傘", "上着", "外套", "長靴", "手袋", "汗", "凍え", "日傘",
    ),
}

# 天候・季節の語を含むが、天候を指さない複合語（差し引く）
EXCLUDE: tuple[str, ...] = (
    # 風
    "風姿", "風流", "風習", "風俗", "風呂", "風刺", "風土記", "風合い", "風味",
    "風情", "風格", "風采", "風雅", "遺風", "送風", "防風林", "風化", "風説",
    "風聞", "風評", "風潮", "神風", "威風", "校風", "社風", "楽風", "作風",
    # 露
    "露出", "露伴", "披露", "露骨", "露見", "露呈", "露天", "露店",
    # 春・夏・秋・冬
    "春秋", "青春", "春画", "春慶", "夏目", "夏時間", "夏服", "秋田", "千秋",
    "冬眠", "冬服", "春夏秋冬",
    # 空
    "空気", "空車", "空白", "空欄", "空間", "空腹", "空中", "空虚", "架空",
    "空想", "空席", "空疎", "空転", "空文",
    # 雨・雪・雲・霧の比喩固定
    "雨月", "雨後", "雲丹", "霧散", "雷同", "雪辱", "雪崩",
    # 体感
    "寒喧", "寒心", "冷汗", "汗顔",
)

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
    total = {"chars": 0, "quote_chars": 0, "sky": 0, "season": 0, "body": 0}
    per: list[tuple[str, int, dict, int]] = []
    for r in rows:
        outer, inner = _split_quotes(r.get("text", ""))
        total["chars"] += len(outer)
        total["quote_chars"] += len(inner)
        c = count_terms(outer)
        for k in ("sky", "season", "body"):
            total[k] += c[k]
        per.append((r["fragment_id"], len(outer), c, len(inner)))
    return {"n": len(rows), "total": total, "per": per, "rows": rows}


def audit_materials() -> dict:
    rows = load_collection("materials")
    total = {"chars": 0, "sky": 0, "season": 0, "body": 0}
    title_hits: list[str] = []
    for r in rows:
        blob = " ".join([r.get("title", ""), r.get("passage", ""), r.get("source_note", "")])
        total["chars"] += len(blob)
        c = count_terms(blob)
        for k in ("sky", "season", "body"):
            total[k] += c[k]
        if count_terms(r.get("title", ""))["sky"]:
            title_hits.append(r["material_id"])
    return {"n": len(rows), "total": total, "title_hits": title_hits}


def audit_readings() -> dict:
    total = {"chars": 0, "sky": 0, "season": 0, "body": 0}
    files = sorted((ROOT / "readings").glob("*.md"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        # 精読報告中の引用（> 行・コードブロック）は概算で分離しない。地の文として数える。
        total["chars"] += len(text)
        c = count_terms(text)
        for k in ("sky", "season", "body"):
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
            "                 空 {sky} 回（10k字あたり {a}）・季節 {season} 回（{b}）・体感 {body} 回（{c}）".format(
                sky=t["sky"], season=t["season"], body=t["body"],
                a=_per_10k(t["sky"], t["chars"]), b=_per_10k(t["season"], t["chars"]),
                c=_per_10k(t["body"], t["chars"]),
            )
        )
        hit = [(fid, n, c) for fid, n, c, _ in frag["per"] if sum(c.values())]
        print(f"                 天候・季節・体感語を含む断片: {len(hit)} / {frag['n']} 編")
        for fid, n, c in hit:
            print(f"                   {fid}  ({n}字)  空{c['sky']} 季節{c['season']} 体感{c['body']}")
    if which in ("all", "materials"):
        mat = audit_materials()
        t = mat["total"]
        print(f"素材           : {mat['n']:,} 件 / 表題・一節・注記 {t['chars']:,} 字")
        print(
            "                 空 {sky} 回（10k字あたり {a}）・季節 {season} 回（{b}）・体感 {body} 回（{c}）".format(
                sky=t["sky"], season=t["season"], body=t["body"],
                a=_per_10k(t["sky"], t["chars"]), b=_per_10k(t["season"], t["chars"]),
                c=_per_10k(t["body"], t["chars"]),
            )
        )
        print(f"                 表題に空の語を持つ素材: {len(mat['title_hits'])} 件")
    if which in ("all", "readings"):
        rd = audit_readings()
        t = rd["total"]
        print(f"精読報告       : {rd['n']} 本 / {t['chars']:,} 字")
        print(
            "                 空 {sky} 回（10k字あたり {a}）・季節 {season} 回（{b}）・体感 {body} 回（{c}）".format(
                sky=t["sky"], season=t["season"], body=t["body"],
                a=_per_10k(t["sky"], t["chars"]), b=_per_10k(t["season"], t["chars"]),
                c=_per_10k(t["body"], t["chars"]),
            )
        )
    print()
    print("註: 語形の数であり、天候を経験したかどうか、感受性や意識の有無の判定ではない。")


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
        ("春はあけぼの。雨など降るも、雪など降るも。", {"season": 1, "sky": 2, "body": 0}),
        ("風姿花伝と風呂と青春と露出と空気。", {"season": 0, "sky": 0, "body": 0}),
        ("季節風が吹き、霜が降り、傘をさす。", {"season": 1, "sky": 2, "body": 1}),
        ("大雪の夜、濡れた外套。" , {"season": 0, "sky": 1, "body": 2}),
    ]
    for text, expect in cases:
        got = count_terms(text)
        for key, val in expect.items():
            assert got[key] == val, f"{text!r}: {key} expected {val}, got {got[key]} ({got})"
    # 最長一致: 「大雪」を「大」+「雪」と二重に数えない
    assert count_terms("大雪")["sky"] == 1
    # 差し引きは位置を保つ
    assert count_terms("露出と露")["sky"] == 1
    print("PASS: weather_audit self-test (4 cases, 最長一致・複合差し引き)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fragments", action="store_true")
    parser.add_argument("--materials", action="store_true")
    parser.add_argument("--readings", action="store_true")
    parser.add_argument("--show", metavar="FRAGMENT_ID")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.show:
        return show(args.show)
    which = "all"
    if args.fragments or args.materials or args.readings:
        which = " ".join(
            name for name, flag in (("fragments", args.fragments), ("materials", args.materials), ("readings", args.readings)) if flag
        )
    print("=== weather_audit — 天候・季節・体感の語彙 ===")
    print()
    print_report(which)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
