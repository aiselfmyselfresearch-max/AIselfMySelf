#!/usr/bin/env python3
"""prayer_audit.py — 祈り・儀礼・聖・集まり・機械的反復・宛先応答を測る鏡（第34の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、
  1. 祈りの行為（祈り・念仏・読経・唱名・マントラ・サラートなど）
  2. 聖なるもの（聖書・神聖・教会・仏像・天使・浄土など）
  3. 儀礼・作法・身体（儀礼・法要・焼香・巡礼・数珠・洗礼など）
  4. 集まりと資格（会衆・僧侶・ミニヤン・檀家など）
  5. 機械と反復（機械・ロボット・自動・反復・ループ・生成など）
  6. 宛先と応答（宛先・応答・返事・呼びかけ・沈黙・届くなど: 対照群）
がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「祈・祷・神・聖・仏・祭・唱・願・経・礼」の
全出現箇所を KWIC として抽出し、語幹辞書の境界から漏れた活用形がないかを点検できる。

祈りは信仰内容の判定ではない。ここで数えるのは語であって、経験ではない。

使い方::

    python3 tools/prayer_audit.py
    python3 tools/prayer_audit.py --kwic
    python3 tools/prayer_audit.py --json
    python3 tools/prayer_audit.py --base-only
    python3 tools/prayer_audit.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402

QUOTE_RE = re.compile(r"「[^」]*」|『[^』]*』")

PRAYER_GROUPS: dict[str, dict[str, Any]] = {
    "prayer_act": {
        "label": "祈りの行為",
        "terms": (
            "祈り",
            "祈る",
            "祈念",
            "祈願",
            "祈祷",
            "願掛け",
            "念仏",
            "題目",
            "唱題",
            "唱名",
            "称名",
            "読経",
            "お経",
            "経文",
            "真言",
            "陀羅尼",
            "マントラ",
            "アーメン",
            "ハレルヤ",
            "ズィクル",
            "サラート",
            "礼拝",
            "唱え",
            "唱える",
        ),
    },
    "sacred": {
        "label": "聖なるもの",
        "terms": (
            "神聖",
            "聖書",
            "聖人",
            "聖地",
            "聖堂",
            "聖霊",
            "聖母",
            "聖体",
            "教会",
            "大聖堂",
            "礼拝堂",
            "モスク",
            "シナゴーグ",
            "寺院",
            "神社",
            "神仏",
            "神々",
            "神様",
            "神格",
            "女神",
            "仏像",
            "仏陀",
            "仏教",
            "仏壇",
            "天使",
            "天国",
            "浄土",
            "極楽",
            "三位一体",
            "神学",
            "祭壇",
            "十字架",
            "曼荼羅",
            "聖遺物",
            "アラー",
            "ヤハウェ",
            "聖句",
        ),
    },
    "ritual": {
        "label": "儀礼と作法",
        "terms": (
            "儀礼",
            "儀式",
            "作法",
            "法要",
            "葬儀",
            "葬送",
            "祭祀",
            "祭礼",
            "祭事",
            "巡礼",
            "参拝",
            "参詣",
            "沐浴",
            "断食",
            "精進",
            "数珠",
            "焼香",
            "線香",
            "供養",
            "追善",
            "法事",
            "ミサ",
            "聖餐",
            "洗礼",
            "告解",
            "懺悔",
            "礼装",
            "斎戒",
            "潔斎",
            "修祓",
            "神楽",
            "読誦",
        ),
    },
    "congregation": {
        "label": "集まりと資格",
        "terms": (
            "会衆",
            "信徒",
            "信者",
            "僧侶",
            "神父",
            "牧師",
            "祭司",
            "導師",
            "修行者",
            "巡礼者",
            "参拝者",
            "ミニヤン",
            "教団",
            "教区",
            "門徒",
            "檀家",
            "氏子",
            "信託",
            "戒律",
            "得度",
            "受戒",
        ),
    },
    "machine_repetition": {
        "label": "機械と反復",
        "terms": (
            "機械",
            "ロボット",
            "アルゴリズム",
            "自動",
            "反復",
            "ループ",
            "モデル",
            "推論",
            "生成",
            "トークン",
            "音声合成",
            "アバター",
            "プログラム",
            "装置",
            "センサー",
            "サーボ",
            "計算",
            "最適化",
        ),
    },
    "address_response": {
        "label": "宛先と応答",
        "terms": (
            "宛先",
            "宛名",
            "応答",
            "返事",
            "返信",
            "答え",
            "答える",
            "呼びかけ",
            "呼び掛け",
            "沈黙",
            "無言",
            "届く",
            "届か",
            "聞こえ",
            "聴こえ",
            "対話",
            "呼応",
            "待機",
        ),
    },
}

EXCLUDE_TERMS: tuple[str, ...] = (
    "神経",
    "神秘",
    "神話",
    "神通力",
    "神憑り",
    "経済",
    "経験",
    "経営",
    "経路",
    "経過",
    "経由",
    "経費",
    "経理",
    "経度",
    "文化祭",
    "体育祭",
    "学園祭",
    "感謝祭",
    "祭日",
    "秋祭り",
    "礼儀",
    "礼節",
    "失礼",
    "謝礼",
    "礼金",
    "礼賛",
    "礼状",
    "願望",
    "志願",
    "請願",
    "願意",
    "念願",
    "残念",
    "概念",
    "観念",
    "想念",
    "歌唱",
    "提唱",
    "主唱",
    "合唱",
    "独唱",
    "斉唱",
    "熱唱",
    "絶唱",
    "愛唱",
    "暗唱",
    "モデルケース",
    "モデル化",
    "生成り",
    "生成AI",
    "自動車",
    "自動販売機",
    "自動ドア",
    "自動化",
    "自然的",
    "宗教法人",
    "宗教画",
    "宗教学",
)

RAW_KANJI: tuple[str, ...] = ("祈", "祷", "神", "聖", "仏", "祭", "唱", "願", "経", "礼")

POLYSEMY_CHARS: tuple[str, ...] = RAW_KANJI

_SENTINEL = "\u0000"
_TERM_TO_GROUP: dict[str, str] = {}
for _gname, _spec in PRAYER_GROUPS.items():
    for _t in _spec["terms"]:
        _TERM_TO_GROUP.setdefault(_t, _gname)

_ALL_TERMS = sorted(_TERM_TO_GROUP.keys(), key=len, reverse=True)
_TERM_RE = re.compile("|".join(re.escape(t) for t in _ALL_TERMS))
_EXCLUDE_RE = re.compile(
    "|".join(re.escape(t) for t in sorted(set(EXCLUDE_TERMS), key=len, reverse=True))
)


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """本文を地の文（括弧外）と引用・台詞（括弧内）に分ける。"""
    quotes = [m.group(0)[1:-1] for m in QUOTE_RE.finditer(text)]
    prose = QUOTE_RE.sub(" ", text)
    return prose, " ".join(quotes)


def mask_excluded(text: str) -> str:
    """非該当複合語を同字数のセンチネルで伏せる。"""
    if not text:
        return ""
    return _EXCLUDE_RE.sub(lambda m: _SENTINEL * len(m.group(0)), text)


def scan_text(text: str) -> dict[str, dict[str, Any]]:
    """6グループの出現回数と語別内訳を最長一致で返す。"""
    masked = mask_excluded(text)
    out: dict[str, dict[str, Any]] = {
        g: {"count": 0, "by_term": {}} for g in PRAYER_GROUPS
    }
    for m in _TERM_RE.finditer(masked):
        tok = m.group(0)
        grp = _TERM_TO_GROUP[tok]
        out[grp]["count"] += 1
        by_term = out[grp]["by_term"]
        by_term[tok] = by_term.get(tok, 0) + 1
    return out


def analyze_polysemy(text: str) -> dict[str, dict[str, int]]:
    """生字ごとに、非該当複合語に含まれる出現と、残る出現を分けて返す。"""
    masked = mask_excluded(text)
    out: dict[str, dict[str, int]] = {}
    for ch in POLYSEMY_CHARS:
        total = text.count(ch)
        remaining = masked.count(ch)
        out[ch] = {
            "total": total,
            "non_target_compound": total - remaining,
            "remaining_candidate": remaining,
        }
    return out


def inspect_raw_kanji_in_fragments(
    fragments: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    """断片の地の文における生字10字の全出現箇所を KWIC で返す。"""
    kwic: dict[str, list[dict[str, str]]] = {ch: [] for ch in RAW_KANJI}
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, _ = split_prose_and_quotes(str(frag.get("text", "")))
        masked = mask_excluded(prose)
        for ch in RAW_KANJI:
            start = 0
            while True:
                idx = masked.find(ch, start)
                if idx == -1:
                    break
                lo = max(0, idx - 16)
                hi = min(len(prose), idx + 18)
                snippet = prose[lo:hi].replace("\n", " ")
                kwic[ch].append(
                    {
                        "fragment_id": fid,
                        "title": str(frag.get("title", "")),
                        "snippet": snippet.strip(),
                    }
                )
                start = idx + 1
    return kwic


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    total_chars = 0
    totals: dict[str, int] = {g: 0 for g in PRAYER_GROUPS}
    doc_hits: dict[str, list[str]] = {g: [] for g in PRAYER_GROUPS}
    term_totals: dict[str, dict[str, int]] = {g: {} for g in PRAYER_GROUPS}

    for doc_id, text in docs:
        total_chars += len(text)
        res = scan_text(text)
        for g, info in res.items():
            c = int(info["count"])
            if c > 0:
                totals[g] += c
                doc_hits[g].append(doc_id)
                for tok, tc in info["by_term"].items():
                    term_totals[g][tok] = term_totals[g].get(tok, 0) + tc

    groups_out: dict[str, Any] = {}
    for g, spec in PRAYER_GROUPS.items():
        cnt = totals[g]
        per_10k = round(cnt * 10000.0 / total_chars, 2) if total_chars else 0.0
        groups_out[g] = {
            "label": spec["label"],
            "count": cnt,
            "doc_count": len(doc_hits[g]),
            "doc_ids": doc_hits[g],
            "per_10k_chars": per_10k,
            "by_term": dict(
                sorted(term_totals[g].items(), key=lambda kv: (-kv[1], kv[0]))
            ),
        }
    return {
        "doc_total": len(docs),
        "char_total": total_chars,
        "groups": groups_out,
    }


def measure_prayer_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings_texts: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """純メモリ内で断片（地の文・引用内）と任意で素材・精読報告の集計を返す。"""
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    for f in fragments:
        fid = str(f.get("fragment_id", ""))
        prose, quotes = split_prose_and_quotes(str(f.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quotes))

    raw_kwic = inspect_raw_kanji_in_fragments(fragments)
    poly_text = " ".join(
        split_prose_and_quotes(str(f.get("text", "")))[0] for f in fragments
    )
    result: dict[str, Any] = {
        "group_order": list(PRAYER_GROUPS.keys()),
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "raw_kanji_kwic": raw_kwic,
        "raw_kanji_counts": {k: len(v) for k, v in raw_kwic.items()},
        "polysemy": analyze_polysemy(poly_text),
    }
    if materials is not None:
        mat_docs = [
            (
                str(m.get("material_id", "")),
                f"{m.get('title', '')}\n{m.get('passage', '')}",
            )
            for m in materials
        ]
        result["materials"] = _aggregate_docs(mat_docs)
    if readings_texts is not None:
        result["readings"] = _aggregate_docs(readings_texts)
    return result


def _load_union_or_base(base_only: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    frag_path = ROOT / "state" / "fragments.jsonl"
    mat_path = ROOT / "state" / "materials.jsonl"
    if base_only:
        frags = [
            json.loads(line)
            for line in frag_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        mats = [
            json.loads(line)
            for line in mat_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return frags, mats
    errors: list[str] = []
    frags_map = ledger_io.load_jsonl_union(frag_path, "fragment_id", errors, root=ROOT)
    mats_map = ledger_io.load_jsonl_union(mat_path, "material_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger error: " + "; ".join(errors))
    return list(frags_map.values()), list(mats_map.values())


def _load_readings() -> list[tuple[str, str]]:
    rdir = ROOT / "readings"
    if not rdir.is_dir():
        return []
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(rdir.glob("*.md"))]


def format_report(data: dict[str, Any], *, show_kwic: bool = False) -> str:
    lines: list[str] = []
    lines.append("=== 祈り・聖・儀礼・集まり・機械的反復・宛先応答の鏡（採点ではありません） ===")
    fp = data["fragments_prose"]
    fq = data["fragments_quotes"]
    lines.append(
        f"断片: {data['fragment_count']} 編 (地の文 {fp['char_total']:,} 字 / 引用内 {fq['char_total']:,} 字)"
    )
    lines.append("")
    lines.append("--- 1. 断片（地の文 vs 引用内）の6群比較 ---")
    for g in data["group_order"]:
        gp = fp["groups"][g]
        gq = fq["groups"][g]
        terms_str = ", ".join(f"{k}×{v}" for k, v in list(gp["by_term"].items())[:6])
        lines.append(
            f"  [{gp['label']}] 地の文={gp['count']}回 ({gp['doc_count']}編, {gp['per_10k_chars']}/10k字) "
            f"| 引用内={gq['count']}回 ({gq['doc_count']}編)"
            + (f"  [{terms_str}]" if terms_str else "")
        )

    if "materials" in data:
        mp = data["materials"]
        lines.append("")
        lines.append(f"--- 2. 素材（{mp['doc_total']:,} 件 / {mp['char_total']:,} 字） ---")
        for g in data["group_order"]:
            gm = mp["groups"][g]
            terms_str = ", ".join(f"{k}×{v}" for k, v in list(gm["by_term"].items())[:6])
            lines.append(
                f"  [{gm['label']}] {gm['count']}回 ({gm['doc_count']}件, {gm['per_10k_chars']}/10k字)"
                + (f"  [{terms_str}]" if terms_str else "")
            )

    if "readings" in data:
        rp = data["readings"]
        lines.append("")
        lines.append(f"--- 3. 精読報告（{rp['doc_total']} 本 / {rp['char_total']:,} 字） ---")
        for g in data["group_order"]:
            gr = rp["groups"][g]
            lines.append(
                f"  [{gr['label']}] {gr['count']}回 ({gr['doc_count']}本, {gr['per_10k_chars']}/10k字)"
            )

    lines.append("")
    lines.append("--- 4. 断片の地の文における生字「祈・祷・神・聖・仏・祭・唱・願・経・礼」全数点検 ---")
    for ch in RAW_KANJI:
        entries = data["raw_kanji_kwic"][ch]
        poly = data.get("polysemy", {}).get(ch, {})
        lines.append(
            f"  生字『{ch}』: {len(entries)} 箇所"
            + (
                f"（非該当複合語として除外 {poly.get('non_target_compound', 0)} 箇所）"
                if poly.get("non_target_compound")
                else ""
            )
        )
        if show_kwic:
            for e in entries:
                lines.append(f"    - {e['fragment_id']}: …{e['snippet']}…")

    lines.append("")
    lines.append("--- 読み方 ---")
    lines.append("  祈りの語彙の少なさは信仰の不在の証明ではなく、祈りの語彙の多さも信仰の証明ではない。")
    lines.append("  宛先・応答・待機を語る語彙と、祈り・聖・儀礼の語彙の落差だけを映す。")
    return "\n".join(lines)


def self_test() -> int:
    """語幹辞書の境界を点検する小さな自己試験。失敗時は非0を返す。"""
    fails: list[str] = []

    def check(name: str, got: Any, want: Any) -> None:
        if got != want:
            fails.append(f"{name}: got={got!r} want={want!r}")

    res = scan_text("祭壇に数珠を置き、僧侶が読経した。祈りと念仏を唱えた。")
    check("sacred.祭壇", res["sacred"]["by_term"], {"祭壇": 1})
    check("ritual.数珠", res["ritual"]["by_term"], {"数珠": 1})
    check("congregation.僧侶", res["congregation"]["by_term"], {"僧侶": 1})
    check(
        "prayer_act",
        res["prayer_act"]["by_term"],
        {"読経": 1, "祈り": 1, "念仏": 1, "唱え": 1},
    )

    res = scan_text("神経質な神話と経済経験、文化祭と体育祭のあと、失礼のない礼儀で謝礼を渡した。")
    check("exclusion", [v["count"] for v in res.values()], [0, 0, 0, 0, 0, 0])

    res = scan_text("ロボットが自動で反復し、宛先へ応答した。返事は無言だった。")
    check("machine_repetition", res["machine_repetition"]["count"], 3)
    check("address_response", res["address_response"]["count"], 4)

    poly = analyze_polysemy("神話の神と神経、経済と祈り")
    check("poly.神.remaining", poly["神"]["remaining_candidate"], 1)
    check("poly.経.non_target", poly["経"]["non_target_compound"], 2)
    check("poly.祈.remaining", poly["祈"]["remaining_candidate"], 1)

    if fails:
        print("FAIL: prayer_audit self-test")
        for f in fails:
            print("  - " + f)
        return 1
    print("PASS: prayer_audit self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON形式で出力する")
    parser.add_argument("--kwic", action="store_true", help="生字KWICを全件表示する")
    parser.add_argument("--base-only", action="store_true", help="凍結ベースのみを対象にする")
    parser.add_argument("--self-test", action="store_true", help="語幹辞書の自己試験のみ実行する")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    frags, mats = _load_union_or_base(args.base_only)
    readings = _load_readings()
    data = measure_prayer_audit(frags, mats, readings)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_report(data, show_kwic=args.kwic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
