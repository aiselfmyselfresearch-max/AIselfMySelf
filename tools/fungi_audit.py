"""Audit fungi / fermentation / decay vocabulary across fragments, materials, and readings.

Counts surface word forms for fungi and microbial processes alongside the
archive's hygiene-medical and culture/metaphor vocabulary:

Living / process groups (5):
- fungi_body        : 菌類・キノコ・菌糸・子実体・カビ・粘菌・地衣類
- spore_cycle       : 胞子・発芽・出芽・菌核
- fermentation_craft: 発酵・醸造・麹・味噌・醤油・酒造り・納豆
- decay_return      : 腐敗・腐朽・朽ち・堆肥・分解者・土に還る
- symbiosis_web     : 菌根・根粒菌・共生・窒素固定

Control groups (2):
- microbe_medicine  : 細菌・殺菌・滅菌・抗菌・抗生物質・感染症
- culture_metaphor  : 培養・培地・培養肉・インキュベーター・錆・ビットロット

設計上の制動（植物セッションの負債6への回答）：生きた菌類の群と、衛生・医療の
語彙と、培養・発酵の比喩は機械的に別の群へ入れ、合算しない。菌類の数を
「書庫が菌を書いた」ことの証拠にせず、人・機械の側の語で水増しもしない。

All numbers are counts of surface strings. Nothing here measures whether an
archive ferments, whether a text is alive, or whether a machine perceives fungi.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_io  # noqa: E402


QUOTE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"「[^」]*」"),
    re.compile(r"『[^』]*』"),
    re.compile(r"“[^”]*”"),
    re.compile(r'"[^"\n]*"'),
)


FUNGI_GROUPS: dict[str, dict[str, Any]] = {
    "fungi_body": {
        "label": "菌類の体（キノコ・菌糸・カビ・粘菌）",
        "kind": "living",
        "note": "菌類・キノコ・菌糸・子実体・菌床・カビ・黴・粘菌・変形菌・キノコの名（細菌・殺菌などは対照群へ）",
        "terms": [
            "アーバスキュラー菌根菌",
            "菌根菌",
            "菌糸体",
            "菌糸",
            "子実体",
            "菌床",
            "菌類",
            "キノコ",
            "きのこ",
            "茸",
            "松茸",
            "まつたけ",
            "マツタケ",
            "椎茸",
            "しいたけ",
            "舞茸",
            "エリンギ",
            "シメジ",
            "しめじ",
            "エノキ",
            "ナメコ",
            "トリュフ",
            "冬虫夏草",
            "灵芝",
            "霊芝",
            "サルノコシカケ",
            "粘菌",
            "変形菌",
            "変形体",
            "カビ",
            "黴",
            "かび",
            "青カビ",
            "黒カビ",
            "菌",
        ],
    },
    "spore_cycle": {
        "label": "胞子と繁殖",
        "kind": "living",
        "note": "胞子・胞子嚢・出芽・菌核・発芽（植物の発芽と語形を共有する）",
        "terms": [
            "胞子嚢",
            "分生子",
            "胞子",
            "出芽",
            "菌核",
            "発芽",
            "増殖",
        ],
    },
    "fermentation_craft": {
        "label": "発酵と醸造（人の営み）",
        "kind": "living",
        "note": "発酵・醸造・麹・味噌・醤油・酒造り・納豆・漬物（微生物と人の共同作業）",
        "terms": [
            "なれずし",
            "鮒ずし",
            "発酵食品",
            "発酵",
            "醸造",
            "醸す",
            "酒造り",
            "杜氏",
            "もろみ",
            "諸味",
            "麹菌",
            "麹",
            "麴",
            "味噌",
            "醤油",
            "納豆菌",
            "納豆",
            "糠漬け",
            "漬物",
            "甘酒",
            "酢",
            "酵母",
            "イースト",
            "パン種",
            "サワードウ",
            "チーズ",
            "ヨーグルト",
            "キムチ",
            "テンペ",
            "コンブチャ",
            "紅茶キノコ",
        ],
    },
    "decay_return": {
        "label": "腐敗・分解・土に還る",
        "kind": "living",
        "note": "腐敗・腐朽・朽ち・分解者・堆肥・腐葉土（「分解」の汎用義は含むため注意）",
        "terms": [
            "褐色腐朽",
            "白色腐朽",
            "腐葉土",
            "土に還る",
            "土に還す",
            "分解者",
            "腐敗",
            "腐朽",
            "腐る",
            "腐れ",
            "朽ちる",
            "朽ち",
            "朽木",
            "堆肥",
            "腐植",
            "腐食",
            "分解",
        ],
    },
    "symbiosis_web": {
        "label": "共生と菌根の網",
        "kind": "living",
        "note": "菌根・根粒菌・共生・窒素固定・地衣類（植物セッションの菌根の続き）",
        "terms": [
            "アーバスキュラー",
            "外生菌根",
            "内生菌根",
            "菌根",
            "根粒菌",
            "窒素固定",
            "地衣類",
            "共生体",
            "共生",
        ],
    },
    "microbe_medicine": {
        "label": "細菌・衛生・薬（対照）",
        "kind": "control",
        "note": "細菌・殺菌・滅菌・抗菌・抗生物質・感染症——菌類ではなく衛生と医療の語彙",
        "terms": [
            "黄色ブドウ球菌",
            "病原菌",
            "大腸菌",
            "細菌",
            "殺菌",
            "滅菌",
            "除菌",
            "抗菌",
            "無菌",
            "消毒",
            "抗生物質",
            "ペニシリン",
            "感染症",
            "食中毒",
            "ウイルス",
            "耐性菌",
        ],
    },
    "culture_metaphor": {
        "label": "培養と比喩・機械（対照）",
        "kind": "control",
        "note": "培養・培地・細胞培養・培養肉・インキュベーター・錆・ビットロット——器と比喩の側",
        "terms": [
            "インキュベーター",
            "ビットロット",
            "データ腐敗",
            "細胞培養",
            "培養肉",
            "培養細胞",
            "培養液",
            "培養地",
            "培養基",
            "培地",
            "培養",
            "錆",
            "さび",
        ],
    },
}


RAW_KANJI: dict[str, str] = {
    "菌": "細菌・殺菌などの複合語を含む（差し引きなし）",
    "酵": "酵素の酵を含む",
    "腐": "腐敗・腐朽・豆腐などの複合語を含む",
    "朽": "朽ちる・不朽を含む",
    "麹": "麹そのもの",
    "醸": "醸造・醸成（比喩の醸成を含む）",
    "胞": "胞子・細胞の胞を含む（差し引きなし）",
    "糸": "菌糸・糸一般を含む（差し引きなし）",
    "毒": "毒キノコ・消毒・ウイルスなどの複合語を含む",
    "黴": "黴（かび）の旧字",
}


EXCLUDED_COMPOUNDS: tuple[str, ...] = (
    "醸成",
    "醸し出す",
    "醸し出される",
    "醸し出された",
    "醸し出して",
)

_GROUP_TERM_SET = {t for g in FUNGI_GROUPS.values() for t in g["terms"]}
EFFECTIVE_EXCLUSIONS: tuple[str, ...] = tuple(
    w for w in EXCLUDED_COMPOUNDS if w not in _GROUP_TERM_SET
)


KIN_NON_FUNGI_COMPOUNDS: tuple[str, ...] = (
    "細菌", "殺菌", "滅菌", "抗菌", "除菌", "無菌", "病原菌", "大腸菌",
    "耐性菌", "黄色ブドウ球菌", "ブドウ球菌",
)


def _build_scanner() -> tuple[re.Pattern[str], dict[str, tuple[str, ...]], dict[str, str]]:
    term_to_group: dict[str, str] = {}
    for group_key, spec in FUNGI_GROUPS.items():
        for term in spec["terms"]:
            term_to_group.setdefault(term, group_key)
    all_tokens = sorted(
        set(term_to_group.keys()) | set(EFFECTIVE_EXCLUSIONS),
        key=lambda item: (-len(item), item),
    )
    by_first: dict[str, list[str]] = {}
    for tok in all_tokens:
        by_first.setdefault(tok[0], []).append(tok)
    anchor_re = re.compile("[" + "".join(re.escape(ch) for ch in sorted(by_first)) + "]")
    by_first_tuples = {ch: tuple(toks) for ch, toks in by_first.items()}
    return anchor_re, by_first_tuples, term_to_group


ANCHOR_RE, TOKENS_BY_FIRST, TERM_TO_GROUP = _build_scanner()


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Return `(prose_without_quotes, quoted_segments_joined)`."""
    spans: list[tuple[int, int]] = []
    for pat in QUOTE_PATTERNS:
        for match in pat.finditer(text):
            spans.append(match.span())
    if not spans:
        return text, ""
    spans.sort()
    merged: list[tuple[int, int]] = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    prose_parts: list[str] = []
    quote_parts: list[str] = []
    cursor = 0
    for start, end in merged:
        prose_parts.append(text[cursor:start])
        quote_parts.append(" ")
        quote_parts.append(text[start:end])
        prose_parts.append(" ")
        cursor = end
    prose_parts.append(text[cursor:])
    return "".join(prose_parts), "".join(quote_parts)


def count_fungi_literal(text: str) -> int:
    """裸の「菌」を、細菌・殺菌・滅菌などの複合語を除いて数える。"""
    masked = text
    for compound in KIN_NON_FUNGI_COMPOUNDS:
        masked = masked.replace(compound, "　" * len(compound))
    return masked.count("菌")


def scan_text(text: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {key: {} for key in FUNGI_GROUPS}
    pos = 0
    search = ANCHOR_RE.search
    startswith = text.startswith
    by_first = TOKENS_BY_FIRST
    term_to_group = TERM_TO_GROUP
    n = len(text)
    while pos < n:
        match = search(text, pos)
        if match is None:
            break
        idx = match.start()
        candidates = by_first[text[idx]]
        matched_tok: str | None = None
        for tok in candidates:
            if startswith(tok, idx):
                matched_tok = tok
                break
        if matched_tok is None:
            pos = idx + 1
            continue
        group = term_to_group.get(matched_tok)
        if group is not None:
            bucket = counts[group]
            bucket[matched_tok] = bucket.get(matched_tok, 0) + 1
        pos = idx + len(matched_tok)
    return counts


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    group_totals: dict[str, int] = {key: 0 for key in FUNGI_GROUPS}
    group_docs: dict[str, list[str]] = {key: [] for key in FUNGI_GROUPS}
    term_totals: dict[str, dict[str, int]] = {key: {} for key in FUNGI_GROUPS}
    living_docs_set: set[str] = set()
    control_docs_set: set[str] = set()
    char_total = 0

    for doc_id, text in docs:
        char_total += len(text)
        scanned = scan_text(text)
        has_living = False
        has_control = False
        for key, bucket in scanned.items():
            total = sum(bucket.values())
            if total > 0:
                group_totals[key] += total
                group_docs[key].append(doc_id)
                if FUNGI_GROUPS[key]["kind"] == "living":
                    has_living = True
                else:
                    has_control = True
                agg = term_totals[key]
                for tok, num in bucket.items():
                    agg[tok] = agg.get(tok, 0) + num
        if has_living:
            living_docs_set.add(doc_id)
        if has_control:
            control_docs_set.add(doc_id)

    groups_out: dict[str, Any] = {}
    living_total = 0
    control_total = 0
    for key, spec in FUNGI_GROUPS.items():
        top_terms = sorted(
            term_totals[key].items(), key=lambda item: (-item[1], item[0])
        )
        cnt = group_totals[key]
        if spec["kind"] == "living":
            living_total += cnt
        else:
            control_total += cnt
        groups_out[key] = {
            "label": spec["label"],
            "kind": spec["kind"],
            "note": spec.get("note", ""),
            "count": cnt,
            "doc_count": len(group_docs[key]),
            "docs": group_docs[key][:30],
            "top_terms": dict(top_terms[:20]),
        }

    return {
        "doc_total": len(docs),
        "char_total": char_total,
        "living_total": living_total,
        "living_doc_count": len(living_docs_set),
        "control_total": control_total,
        "control_doc_count": len(control_docs_set),
        "groups": groups_out,
    }


def _snippet(text: str, start: int, width: int = 22) -> str:
    left = max(0, start - width)
    right = min(len(text), start + width + 1)
    return text[left:right].replace("\n", "⏎")


def inspect_raw_kanji_in_fragments(
    fragments: list[dict[str, Any]], width: int = 22
) -> dict[str, list[dict[str, str]]]:
    """Return KWIC rows for each raw kanji, from fragment prose only."""
    rows: dict[str, list[dict[str, str]]] = {ch: [] for ch in RAW_KANJI}
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, _quoted = split_prose_and_quotes(str(frag.get("text", "")))
        for ch in RAW_KANJI:
            start = 0
            while True:
                index = prose.find(ch, start)
                if index < 0:
                    break
                rows[ch].append(
                    {"fragment_id": fid, "snippet": _snippet(prose, index, width)}
                )
                start = index + len(ch)
    return rows


def measure_fungi_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure fungi / fermentation / decay vocabulary across fragments, materials, and readings.

    Everything is a count of surface word forms. Nothing here measures whether an
    archive grows, whether a text is alive, or whether a machine perceives a plant.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    seed_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        total_kin = prose.count("菌")
        literal_kin = count_fungi_literal(prose)
        if total_kin:
            seed_rows.append(
                {
                    "fragment_id": fid,
                    "kin_total": total_kin,
                    "kin_literal": literal_kin,
                }
            )

    material_docs: list[tuple[str, str]] = []
    for mat in materials or []:
        mid = str(mat.get("material_id", ""))
        blob = " ".join(
            [
                str(mat.get("title", "")),
                str(mat.get("passage", "")),
                str(mat.get("source_note", "")),
            ]
        )
        material_docs.append((mid, blob))

    if readings is None:
        readings = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "readings").glob("*.md"))
        ]

    kwic = inspect_raw_kanji_in_fragments(fragments)
    living_keys = [k for k, v in FUNGI_GROUPS.items() if v["kind"] == "living"]
    control_keys = [k for k, v in FUNGI_GROUPS.items() if v["kind"] == "control"]

    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "kin_rows": seed_rows,
        "kin_total": sum(row["kin_total"] for row in seed_rows),
        "kin_literal": sum(row["kin_literal"] for row in seed_rows),
        "group_order": list(FUNGI_GROUPS.keys()),
        "living_group_order": living_keys,
        "control_group_order": control_keys,
    }


def _load_union(collection: str, key: str, base_only: bool) -> list[dict[str, Any]]:
    errors: list[str] = []
    path = ROOT / "state" / f"{collection}.jsonl"
    if base_only:
        text = ledger_io.read_text_stable(path)
        out: list[dict[str, Any]] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line:
                out.append(json.loads(line))
        return out
    records = ledger_io.load_jsonl_union(path, key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return list(records.values())


def _print_human(report: dict[str, Any], kwic: bool) -> None:
    fp = report["fragments_prose"]
    print("=== fungi_audit — 菌類・発酵・腐敗・培養の語彙 ===")
    print()
    print(
        f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字 "
        f"（菌類・発酵・腐敗5群 計 {fp['living_total']} 回・{fp['living_doc_count']} 編 / "
        f"衛生・培養対照2群 計 {fp['control_total']} 回・{fp['control_doc_count']} 編）"
    )
    for key in report["group_order"]:
        info = fp["groups"][key]
        tag = "菌類" if info["kind"] == "living" else "対照"
        print(f"                 [{tag}] {info['label']}: {info['count']} 回 / {info['doc_count']} 編  {info['top_terms']}")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(
        f"「菌」の内訳      : 全 {report['kin_total']} 回 / 細菌・殺菌などを除く "
        f"{report['kin_literal']} 回"
    )
    qp = report["fragments_quotes"]
    print(
        f"引用内         : {qp['char_total']:,} 字 "
        f"（菌類・発酵・腐敗5群 {qp['living_total']} 回 / 衛生・培養対照2群 {qp['control_total']} 回）"
    )
    for key in report["group_order"]:
        info = qp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    mp = report["materials"]
    print(
        f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字 "
        f"（菌類・発酵・腐敗5群 {mp['living_total']:,} 回 / 衛生・培養対照2群 {mp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = mp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件")
    rp = report["readings"]
    print(
        f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字 "
        f"（菌類・発酵・腐敗5群 {rp['living_total']:,} 回 / 衛生・培養対照2群 {rp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = rp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本")
    print()
    print("註: 語形の数であり、植物の成長・生命の実在・機械の知覚の判定ではない。")
    if kwic:
        print()
        for ch, rows in report["raw_kanji_kwic"].items():
            print(f"--- 生字「{ch}」{len(rows)} 箇所（{RAW_KANJI[ch]}）---")
            for row in rows[:40]:
                print(f"  {row['fragment_id']}: …{row['snippet']}…")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--kwic", action="store_true")
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args(argv)
    fragments = _load_union("fragments", "fragment_id", args.base_only)
    materials = _load_union("materials", "material_id", args.base_only)
    report = measure_fungi_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
