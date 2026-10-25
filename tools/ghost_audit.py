"""Audit ghost / haunting vocabulary across fragments, materials, and readings.

Counts surface word forms for ghosts and haunting alongside the archive's
machine-ghost and lexical-ghost vocabulary:

Entity / lore groups (5):
- ghost_apparition : 幽霊・亡霊・死霊・生霊・お化け・妖怪・物の怪
- haunting_action  : 憑依・祟り・呪い・怨霊・未練
- ghost_lore       : 怪談・心霊スポット・霊能者・除霊・成仏
- afterlife_world  : 黄泉・冥界・彼岸・あの世・三途の川・地獄・極楽
- uncanny_fear     : 怪異・怪奇・不気味・身の毛がよだつ

Control groups (2):
- machine_ghost    : ゴースト・グリーフボット・デジタル遺産・追悼アカウント
- lexical_ghost    : 幽霊文字・幽霊部員・幽霊会社・ゴーストタウン・ゴーストライター

設計上の制動（植物・菌類に続く形式的な分離）：幽霊の実体・ lore の語と、
機械の比喩としての幽霊と、語にだけ残る幽霊（幽霊文字など）は機械的に
別の群へ入れ、合算しない。幽霊の数を「書庫が幽霊を書いた」ことの証拠に
せず、比喩と制度の語で水増しもしない。また「霊」の素カウントは、心霊・
霊感・霊媒など lore の複合語を含むため、裸の「幽霊」の内訳（幽霊文字等を
除いた残り）を別に示す。

All numbers are counts of surface strings. Nothing here measures whether
ghosts exist, whether a text is haunted, or whether a machine dreams.
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


GHOST_GROUPS: dict[str, dict[str, Any]] = {
    "ghost_apparition": {
        "label": "幽霊・亡霊の姿",
        "kind": "living",
        "note": "幽霊・亡霊・死霊・生霊・幽鬼・お化け・妖怪・物の怪（幽霊文字など語だけの幽霊は対照群へ）",
        "terms": [
            "物の怪",
            "もののけ",
            "お化け屋敷",
            "お化け",
            "化け物",
            "幽霊",
            "亡霊",
            "死霊",
            "生霊",
            "幽鬼",
            "ゆうれい",
            "霊魂",
            "魂魄",
            "妖怪",
            "あやかし",
            "変化",
        ],
    },
    "haunting_action": {
        "label": "憑く・祟る・呪う",
        "kind": "living",
        "note": "憑依・取り憑く・祟り・呪い・怨霊・怨念・未練（幽霊の側の働きかけ）",
        "terms": [
            "取り憑く",
            "取り憑か",
            "憑依",
            "憑く",
            "祟り",
            "祟る",
            "呪い",
            "呪う",
            "呪縛",
            "怨霊",
            "怨念",
            "恨み",
            "未練",
        ],
    },
    "ghost_lore": {
        "label": "怪談・心霊の語りと実践",
        "kind": "living",
        "note": "怪談・心霊スポット・心霊写真・霊能者・霊媒・除霊・お祓い・成仏",
        "terms": [
            "心霊スポット",
            "心霊写真",
            "心霊現象",
            "怪談話",
            "怪談",
            "霊能者",
            "霊媒",
            "霊感",
            "霊視",
            "除霊",
            "お祓い",
            "御祓い",
            "成仏",
            "浮かばれ",
            "冥福",
        ],
    },
    "afterlife_world": {
        "label": "あの世・黄泉の世界",
        "kind": "living",
        "note": "黄泉・冥界・幽界・彼岸・あの世・三途の川・地獄・極楽・浄土（宗教的他界の語彙）",
        "terms": [
            "三途の川",
            "黄泉比良坂",
            "黄泉",
            "冥界",
            "幽界",
            "彼岸",
            "あの世",
            "地獄",
            "極楽",
            "浄土",
            "天国",
        ],
    },
    "uncanny_fear": {
        "label": "怪し・不気味・気配の感覚",
        "kind": "living",
        "note": "怪異・怪奇・不気味・身の毛がよだつ・鳥肌（怖れの側の語彙。「気配」は汎用的なため含めない）",
        "terms": [
            "身の毛がよだつ",
            "身の毛",
            "怪異",
            "怪奇",
            "怪現象",
            "不気味",
            "おどろおどろ",
            "鳥肌",
            "ぞっと",
            "総毛立つ",
        ],
    },
    "machine_ghost": {
        "label": "機械・デジタルの幽霊（対照）",
        "kind": "control",
        "note": "ゴースト・グリーフボット・デジタル遺産・追悼アカウント——機械と制度の比喩",
        "terms": [
            "機械の中の幽霊",
            "グリーフボット",
            "デジタル遺産",
            "故人のアカウント",
            "追悼アカウント",
            "メモリアルアカウント",
            "ゴースト",
        ],
    },
    "lexical_ghost": {
        "label": "語にだけ残る幽霊（対照）",
        "kind": "control",
        "note": "幽霊文字・幽霊漢字・幽霊部員・幽霊会社・ゴーストタウン・ゴーストライター——実体のない語の幽霊",
        "terms": [
            "幽霊文字",
            "幽霊漢字",
            "幽霊部員",
            "幽霊会社",
            "幽霊船",
            "幽霊人口",
            "幽霊候補",
            "ゴーストタウン",
            "ゴーストライター",
        ],
    },
}


RAW_KANJI: dict[str, str] = {
    "幽": "幽霊・幽暗などの複合語を含む（差し引きなし）",
    "霊": "心霊・霊感・英霊・慰霊などの複合語を含む（差し引きなし）",
    "魂": "魂・霊魂・魂魄を含む",
    "怪": "怪談・妖怪・怪我（けが）などの複合語を含む（差し引きなし）",
    "怨": "怨霊・怨念を含む",
    "祟": "祟りそのもの",
    "憑": "憑依・憑くを含む",
    "妖": "妖怪・妖しいを含む",
    "冥": "冥界・冥福・冥いを含む",
    "魄": "魂魄そのもの",
}


EXCLUDED_COMPOUNDS: tuple[str, ...] = ()

_GROUP_TERM_SET = {t for g in GHOST_GROUPS.values() for t in g["terms"]}
EFFECTIVE_EXCLUSIONS: tuple[str, ...] = tuple(
    w for w in EXCLUDED_COMPOUNDS if w not in _GROUP_TERM_SET
)


YUREI_LEXICAL_COMPOUNDS: tuple[str, ...] = (
    "幽霊文字", "幽霊漢字", "幽霊部員", "幽霊会社", "幽霊船", "幽霊人口", "幽霊候補",
)


def _build_scanner() -> tuple[re.Pattern[str], dict[str, tuple[str, ...]], dict[str, str]]:
    term_to_group: dict[str, str] = {}
    for group_key, spec in GHOST_GROUPS.items():
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


def count_yurei_literal(text: str) -> int:
    """裸の「幽霊」を、幽霊文字・幽霊部員などの語だけの複合語を除いて数える。"""
    masked = text
    for compound in YUREI_LEXICAL_COMPOUNDS:
        masked = masked.replace(compound, "　" * len(compound))
    return masked.count("幽霊")


def scan_text(text: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {key: {} for key in GHOST_GROUPS}
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
    group_totals: dict[str, int] = {key: 0 for key in GHOST_GROUPS}
    group_docs: dict[str, list[str]] = {key: [] for key in GHOST_GROUPS}
    term_totals: dict[str, dict[str, int]] = {key: {} for key in GHOST_GROUPS}
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
                if GHOST_GROUPS[key]["kind"] == "living":
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
    for key, spec in GHOST_GROUPS.items():
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


def measure_ghost_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure ghost / haunting vocabulary across fragments, materials, and readings.

    Everything is a count of surface word forms. Nothing here measures whether
    ghosts exist, whether a text is haunted, or whether a machine perceives.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    yurei_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        total_yurei = prose.count("幽霊")
        literal_yurei = count_yurei_literal(prose)
        if total_yurei:
            yurei_rows.append(
                {
                    "fragment_id": fid,
                    "yurei_total": total_yurei,
                    "yurei_literal": literal_yurei,
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
    living_keys = [k for k, v in GHOST_GROUPS.items() if v["kind"] == "living"]
    control_keys = [k for k, v in GHOST_GROUPS.items() if v["kind"] == "control"]

    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "yurei_rows": yurei_rows,
        "yurei_total": sum(row["yurei_total"] for row in yurei_rows),
        "yurei_literal": sum(row["yurei_literal"] for row in yurei_rows),
        "group_order": list(GHOST_GROUPS.keys()),
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
    print("=== ghost_audit — 幽霊・亡霊・怪談の語彙 ===")
    print()
    print(
        f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字 "
        f"（幽霊・怪5群 計 {fp['living_total']} 回・{fp['living_doc_count']} 編 / "
        f"機械・語の幽霊対照2群 計 {fp['control_total']} 回・{fp['control_doc_count']} 編）"
    )
    for key in report["group_order"]:
        info = fp["groups"][key]
        tag = "幽霊" if info["kind"] == "living" else "対照"
        print(f"                 [{tag}] {info['label']}: {info['count']} 回 / {info['doc_count']} 編  {info['top_terms']}")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(
        f"「幽霊」の内訳      : 全 {report['yurei_total']} 回 / 幽霊文字などを除く "
        f"{report['yurei_literal']} 回"
    )
    qp = report["fragments_quotes"]
    print(
        f"引用内         : {qp['char_total']:,} 字 "
        f"（幽霊・怪5群 {qp['living_total']} 回 / 機械・語の幽霊対照2群 {qp['control_total']} 回）"
    )
    for key in report["group_order"]:
        info = qp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    mp = report["materials"]
    print(
        f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字 "
        f"（幽霊・怪5群 {mp['living_total']:,} 回 / 機械・語の幽霊対照2群 {mp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = mp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件")
    rp = report["readings"]
    print(
        f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字 "
        f"（幽霊・怪5群 {rp['living_total']:,} 回 / 機械・語の幽霊対照2群 {rp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = rp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本")
    print()
    print("註: 語形の数であり、幽霊の実在・機械の知覚の判定ではない。")
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
    report = measure_ghost_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
