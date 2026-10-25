"""Audit provenance / genealogy vocabulary across fragments, materials, and readings.

Counts surface word forms for origins, lineages, and the provenance of records
alongside the archive's machine-lineage and metaphorical-origin vocabulary:

Record / descent groups (5):
- origin_source       : 起源・由来・源流・出自・発祥・ルーツ
- lineage_descent     : 系譜・家系・祖先・子孫・血統・系譜学
- record_provenance   : 来歴・伝来・旧蔵・寄贈・収蔵・典拠・出典
- text_transmission   : 写本・異本・底本・校本・祖本・原典
- self_history        : 自伝・回想・経歴・自分史・年代記

Control groups (2):
- machine_provenance  : コミット・ブランチ・フォーク・マージ・バージョン・リネージ
- metaphor_origin     : 生みの親・温床・震源地・火元

設計上の制動（植物・菌類・幽霊に続く形式的な分離）：記録と血の来歴の語と、
機械のバージョン管理の語と、比喩としての起源の語は機械的に別の群へ入れ、
合算しない。来歴の数を「書庫が出自を書いた」ことの証拠にせず、機械と
比喩の語で水増しもしない。また裸の「来歴」の内訳を示す。

All numbers are counts of surface strings. Nothing here measures where a
text really came from, who wrote it, or whether a machine has a past.
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
    re.compile(r'"[^\n]*"'),
)


GENEALOGY_GROUPS: dict[str, dict[str, Any]] = {
    "origin_source": {
        "label": "起源・由来・源流",
        "kind": "living",
        "note": "起源・由来・源流・源泉・発祥・出自・根源・ルーツ（ものの始まりの語）",
        "terms": [
            "起源", "由来", "源流", "源泉", "発祥", "発祥の地",
            "出自", "根源", "ルーツ", "元祖", "生まれ",
        ],
    },
    "lineage_descent": {
        "label": "系譜・祖先・子孫",
        "kind": "living",
        "note": "系譜・家系・系図・血統・祖先・先祖・子孫・末裔・系譜学（血と家の連なり）",
        "terms": [
            "系譜学", "系譜", "家系図", "家系", "系図",
            "血統書", "血統", "先祖", "祖先", "子孫", "末裔", "一族",
        ],
    },
    "record_provenance": {
        "label": "記録の来歴・伝来",
        "kind": "living",
        "note": "来歴・伝来・伝世・旧蔵・寄贈・収蔵・所蔵・典拠・出典（記録がどう伝わったか）",
        "terms": [
            "来歴", "伝来", "伝世", "旧蔵", "寄贈",
            "収蔵", "所蔵", "典拠", "出典", "旧蔵者",
        ],
    },
    "text_transmission": {
        "label": "写本・版・校訂の系譜",
        "kind": "living",
        "note": "写本・異本・底本・校本・祖本・原本・原典・転写・版本・初版（テクストの伝わり）",
        "terms": [
            "写本", "異本", "底本", "校本", "祖本",
            "原本", "原典", "転写", "版本", "初版", "写し",
        ],
    },
    "self_history": {
        "label": "自伝・回想・自分の歩み",
        "kind": "living",
        "note": "自伝・回想・回顧・経歴・遍歴・足跡・自分史・年代記・クロニクル（自分の来歴を書く）",
        "terms": [
            "自伝", "回想録", "回想", "回顧", "履歴書",
            "経歴", "遍歴", "足跡", "自分史", "年代記", "クロニクル",
        ],
    },
    "machine_provenance": {
        "label": "機械の来歴・バージョン（対照）",
        "kind": "control",
        "note": "コミット・ブランチ・フォーク・マージ・バージョン・リビジョン・リネージ・プロビナンス——機械とデータの系譜",
        "terms": [
            "バージョン管理", "バージョン", "コミット", "ブランチ",
            "フォーク", "マージ", "リビジョン", "スナップショット",
            "リネージ", "プロビナンス",
        ],
    },
    "metaphor_origin": {
        "label": "比喩としての起源（対照）",
        "kind": "control",
        "note": "生みの親・温床・震源地・火元——起源を比喩で言う日常語",
        "terms": [
            "生みの親", "温床", "震源地", "震源", "火元", "苗床",
        ],
    },
}


RAW_KANJI: dict[str, str] = {
    "来": "来歴・以来・将来などの複合語を含む（差し引きなし）",
    "歴": "来歴・履歴・経歴・歴史などの複合語を含む（差し引きなし）",
    "系": "系譜・系統・体系などの複合語を含む（差し引きなし）",
    "譜": "系譜・楽譜・棋譜などの複合語を含む（差し引きなし）",
    "源": "起源・源流・源泉・資源などの複合語を含む（差し引きなし）",
    "祖": "祖先・元祖・祖国などの複合語を含む（差し引きなし）",
    "典": "典拠・出典・古典・辞典などの複合語を含む（差し引きなし）",
    "写": "写本・転写・写真などの複合語を含む（差し引きなし）",
    "伝": "伝来・伝世・伝記・伝統などの複合語を含む（差し引きなし）",
    "跡": "足跡・痕跡・遺跡などの複合語を含む（差し引きなし）",
}


EXCLUDED_COMPOUNDS: tuple[str, ...] = ()

_GROUP_TERM_SET = {t for g in GENEALOGY_GROUPS.values() for t in g["terms"]}
EFFECTIVE_EXCLUSIONS: tuple[str, ...] = tuple(
    w for w in EXCLUDED_COMPOUNDS if w not in _GROUP_TERM_SET
)


RAIREKI_NON_PROVENANCE_COMPOUNDS: tuple[str, ...] = ()


def count_raireki_literal(text: str) -> int:
    """裸の「来歴」を数える（履歴・歴史などは含まない）。"""
    return text.count("来歴")


def _build_scanner() -> tuple[re.Pattern[str], dict[str, tuple[str, ...]], dict[str, str]]:
    term_to_group: dict[str, str] = {}
    for group_key, spec in GENEALOGY_GROUPS.items():
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


def count_raireki_literal(text: str) -> int:
    """裸の「来歴」を数える。来歴そのものの出現であり、履歴・歴史は含まない。"""
    return text.count("来歴")


def scan_text(text: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {key: {} for key in GENEALOGY_GROUPS}
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
    group_totals: dict[str, int] = {key: 0 for key in GENEALOGY_GROUPS}
    group_docs: dict[str, list[str]] = {key: [] for key in GENEALOGY_GROUPS}
    term_totals: dict[str, dict[str, int]] = {key: {} for key in GENEALOGY_GROUPS}
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
                if GENEALOGY_GROUPS[key]["kind"] == "living":
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
    for key, spec in GENEALOGY_GROUPS.items():
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


def measure_genealogy_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure provenance / genealogy vocabulary across fragments, materials, and readings.

    Everything is a count of surface word forms. Nothing here measures whether
    anything really came from somewhere, or whether a machine has a past.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    raireki_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        total_raireki = prose.count("来歴")
        literal_raireki = count_raireki_literal(prose)
        if total_raireki:
            raireki_rows.append(
                {
                    "fragment_id": fid,
                    "raireki_total": total_raireki,
                    "raireki_literal": literal_raireki,
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
    living_keys = [k for k, v in GENEALOGY_GROUPS.items() if v["kind"] == "living"]
    control_keys = [k for k, v in GENEALOGY_GROUPS.items() if v["kind"] == "control"]

    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "raireki_rows": raireki_rows,
        "raireki_total": sum(row["raireki_total"] for row in raireki_rows),
        "raireki_literal": sum(row["raireki_literal"] for row in raireki_rows),
        "group_order": list(GENEALOGY_GROUPS.keys()),
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
    print("=== genealogy_audit — 来歴・系譜・出自の語彙 ===")
    print()
    print(
        f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字 "
        f"（来歴・系譜5群 計 {fp['living_total']} 回・{fp['living_doc_count']} 編 / "
        f"機械・比喩の起源対照2群 計 {fp['control_total']} 回・{fp['control_doc_count']} 編）"
    )
    for key in report["group_order"]:
        info = fp["groups"][key]
        tag = "来歴" if info["kind"] == "living" else "対照"
        print(f"                 [{tag}] {info['label']}: {info['count']} 回 / {info['doc_count']} 編  {info['top_terms']}")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(
        f"「来歴」の内訳      : 全 {report['raireki_total']} 回 / 裸の「来歴」 "
        f"{report['raireki_literal']} 回"
    )
    qp = report["fragments_quotes"]
    print(
        f"引用内         : {qp['char_total']:,} 字 "
        f"（来歴・系譜5群 {qp['living_total']} 回 / 機械・比喩の起源対照2群 {qp['control_total']} 回）"
    )
    for key in report["group_order"]:
        info = qp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    mp = report["materials"]
    print(
        f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字 "
        f"（来歴・系譜5群 {mp['living_total']:,} 回 / 機械・比喩の起源対照2群 {mp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = mp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件")
    rp = report["readings"]
    print(
        f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字 "
        f"（来歴・系譜5群 {rp['living_total']:,} 回 / 機械・比喩の起源対照2群 {rp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = rp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本")
    print()
    print("註: 語形の数であり、来歴の真偽・機械の過去の判定ではない。")
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
    report = measure_genealogy_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
