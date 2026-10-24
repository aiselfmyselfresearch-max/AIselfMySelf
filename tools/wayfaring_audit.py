#!/usr/bin/env python3
"""Measure how the archive writes roads, walking, maps, homeland, exile and rooms.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it.  Meanwhile the repository's largest generated artifact is named
`READING_MAP.md`, its viewer shows a constellation map, and one of its mirrors
is named `drift_audit.py`.  This tool asks a narrower, countable question:
**does the archive's own prose ever leave the room, walk a road, carry a map,
get lost, or name a homeland or an exile?**

The tool reports only what is written in `state/fragments.jsonl` and its shards
(prose only, metadata excluded), optionally in `readings/*.md` (editorial
voice) and in `state/materials.jsonl` (collected titles and passages, most of
which are editorial summaries).  It does not judge imagination or embodiment,
and a zero count means only that the specified word form is absent.

Calibration notes:
  - ``空`` in this archive overwhelmingly means emptiness or blank fields
    (``空白``, ``空欄``, ``空車``, ``空っぽ``, ``空のまま``), not the sky above.
  - ``窓`` includes administrative counters (``窓口``), character-window
    metaphors (``五十八文字の窓枠``), and explicit negations (``窓がない``).
  - ``足`` includes addition and sufficiency (``継ぎ足し``, ``書き足す``,
    ``足りる``, ``足りない``) rather than feet on the ground.
  - ``道`` includes ``道具`` and ``筋道``; ``迷`` includes textual hesitation
    (``推論や迷い``, ``読者が迷う``) rather than losing one's way outdoors.
  - Proper nouns and technical compounds such as ``青空文庫``, ``中島敦``,
    ``三島由紀夫``, ``森鷗外``, ``海馬``, ``上海`` are masked before counting
    landscape tokens so they do not inflate ``青空``, ``島``, ``森``, or ``海``.
  - Quoted spans (「…」『…』) are stripped from prose counts and tallied
    separately in ``inside_quotes``.

Usage:
  python3 tools/wayfaring_audit.py
  python3 tools/wayfaring_audit.py --json
  python3 tools/wayfaring_audit.py --show FRAG-023
  python3 tools/wayfaring_audit.py --base-only
  python3 tools/wayfaring_audit.py --exclude-shard 2026-10-24-xxxxxxxxxxxx
  python3 tools/wayfaring_audit.py --readings
  python3 tools/wayfaring_audit.py --materials
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
MATERIALS = ROOT / "state" / "materials.jsonl"
READINGS = ROOT / "readings"

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

MASKED_COMPOUNDS: tuple[str, ...] = (
    "青空文庫",
    "中島敦",
    "中島",
    "三島由紀夫",
    "三島",
    "広島",
    "島崎",
    "森鷗外",
    "森鴎外",
    "小林",
    "大橋",
    "高橋",
    "海馬",
    "上海",
    "海外",
    "東海",
    "苦海",
)

GROUPS: dict[str, tuple[str, ...]] = {
    "歩行・旅・移動": (
        "旅", "旅人", "旅行", "紀行", "歩行", "散歩", "遊歩", "徒歩",
        "歩いた", "歩いて", "歩ける", "歩様", "足音", "足取り", "足の運び",
        "放浪", "巡礼", "行脚", "遊行", "航海", "漂流", "漂着", "出発", "帰還", "到着",
    ),
    "道・地図・迷子": (
        "地図", "海図", "図面", "方位", "磁石", "羅針盤", "道標", "里程",
        "近道", "回り道", "迂回", "迷子", "迷路", "岐路", "交差点",
        "街道", "坂道", "小径", "石畳", "軌道", "轍", "道の幅",
    ),
    "故郷・帰郷・亡命": (
        "故郷", "ふるさと", "帰郷", "望郷", "郷愁", "異郷", "異国", "他郷",
        "亡命", "追放", "流刑", "難民", "移住", "越境", "国境", "辺境",
    ),
    "外の地形・風景": (
        "海", "砂浜", "港", "島", "森", "原野", "枯野", "砂漠", "荒野",
        "橋", "駅", "広場", "川辺", "日野山", "白山の坂", "雪原",
        "風景", "地平", "水平線", "青空", "高い空", "星空",
    ),
    "室内・書記の器（対照）": (
        "部屋", "書庫", "机", "棚", "書架", "椅子", "紙", "台帳", "帳簿", "高窓",
    ),
}

RAW_TOKENS = ("空", "窓", "道", "足", "歩", "迷", "外")
POLYSEMY_NOTE = {
    "空": "空白・空欄・空車・空のまま等の『空虚・未記入』が大半を占めるため参考値",
    "窓": "窓口・文字数の窓枠・『窓がない』という否定形を含むため参考値",
    "道": "道具・筋道・リンクの比喩を含むため参考値",
    "足": "書き足す・継ぎ足し・足りる／足りない等の加算・充足を含むため参考値",
    "歩": "一歩しりぞく・二歩離れた等の比喩的距離を含むため参考値",
    "迷": "推論や行の迷い・読者が迷う等の認知的躊躇を含むため参考値",
    "外": "欄外・文法から外・鎖の外・外す等の抽象的外部を含むため参考値",
}

NON_SKY_PATTERNS = (
    "空白", "空欄", "空っぽ", "空車", "空で", "空な", "空だ", "空け",
    "空になっ", "空のまま", "空である", "空いて", "空転", "空気",
)
NON_WINDOW_OPEN_PATTERNS = ("窓口", "窓枠", "窓がない", "窓も共有フォルダもない")
NON_ROAD_PATTERNS = ("道具", "筋道", "道徳", "道理", "報道", "書道")
NON_FOOT_PATTERNS = ("書き足", "継ぎ足", "描き足", "足しに", "足り", "足並み", "満足", "不足")


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans so quoted voices are not counted as prose."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, for the inside_quotes tally."""
    return "".join(QUOTE.findall(text))


def mask_compounds(text: str) -> str:
    """Mask proper names and non-landscape compounds of equal character length."""
    masked = text
    for compound in MASKED_COMPOUNDS:
        if compound in masked:
            masked = masked.replace(compound, "□" * len(compound))
    return masked


def load_records(
    path: Path,
    id_key: str,
    *,
    base_only: bool = False,
    exclude_shards: list[str] | None = None,
) -> list[dict[str, Any]]:
    if base_only:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    errors: list[str] = []
    if exclude_shards:
        files = [path] + [
            shard
            for shard in ledger_io.collection_files(path)[1:]
            if not any(tok in shard.name for tok in exclude_shards)
        ]
        records: dict[str, dict[str, Any]] = {}
        for file_path in files:
            for lineno, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                obj = json.loads(line)
                rid = obj[id_key]
                if rid in records:
                    errors.append(f"{file_path}:{lineno}: duplicate {id_key} {rid}")
                records[rid] = obj
    else:
        records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    cleaned = mask_compounds(text)
    return {token: cleaned.count(token) for token in tokens if token in cleaned}


def classify_polysemy(prose_texts: list[str]) -> dict[str, dict[str, int]]:
    joined = mask_compounds("\n".join(prose_texts))
    sky_total = joined.count("空")
    sky_non = 0
    temp_sky = joined
    for p in NON_SKY_PATTERNS:
        c = temp_sky.count(p)
        if c:
            sky_non += c * p.count("空")
            temp_sky = temp_sky.replace(p, "□" * len(p))
    win_total = joined.count("窓")
    win_non = sum(joined.count(p) for p in NON_WINDOW_OPEN_PATTERNS)
    road_total = joined.count("道")
    road_non = sum(joined.count(p) for p in NON_ROAD_PATTERNS)
    foot_total = joined.count("足")
    foot_non = sum(joined.count(p) for p in NON_FOOT_PATTERNS)
    return {
        "空": {
            "total": sky_total,
            "blank_or_empty_or_air": sky_non,
            "remaining_sky_candidates": max(0, sky_total - sky_non),
        },
        "窓": {
            "total": win_total,
            "counter_frame_or_negated": win_non,
            "remaining_architectural_window": max(0, win_total - win_non),
        },
        "道": {
            "total": road_total,
            "tool_or_logic_compound": road_non,
            "remaining_road_or_path_metaphor": max(0, road_total - road_non),
        },
        "足": {
            "total": foot_total,
            "addition_or_sufficiency": foot_non,
            "remaining_bodily_foot": max(0, foot_total - foot_non),
        },
    }


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    prose_list: list[str] = []
    all_group_tokens = tuple(t for g in GROUPS.values() for t in g)

    for frag in fragments:
        text = frag.get("text", "")
        prose = strip_quotes(text)
        quote = split_quotes(text)
        prose_list.append(prose)
        row: dict[str, Any] = {
            "fragment_id": frag.get("fragment_id", "?"),
            "form": frag.get("form", ""),
            "narrator_mode": frag.get("narrator_mode", ""),
            "groups": {},
            "raw": {},
        }
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(row["fragment_id"])
        masked_prose = mask_compounds(prose)
        for token in RAW_TOKENS:
            n = masked_prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quote, all_group_tokens))
        rows.append(row)

    return {
        "fragments": len(fragments),
        "prose_chars": sum(len(p) for p in prose_list),
        "quoted_chars": sum(len(split_quotes(f.get("text", ""))) for f in fragments),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "polysemy_breakdown": classify_polysemy(prose_list),
        "inside_quotes": dict(inside),
    }


def measure_corpus(items: list[tuple[str, str]], label: str) -> dict[str, Any]:
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    total_chars = 0
    for item_id, text in items:
        total_chars += len(text)
        for name, tokens in GROUPS.items():
            counts = count_group(text, tokens)
            if counts:
                group_totals[name].update(counts)
                group_docs[name].add(item_id)
    return {
        "corpus": label,
        "documents": len(items),
        "chars": total_chars,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_doc_counts": {k: len(v) for k, v in group_docs.items()},
    }


def report(data: dict[str, Any]) -> str:
    lines = ["=== 道と地図の鏡 — AIselfMySelf 台帳の歩行・地図・故郷・室内を映す（採点ではありません） ==="]
    lines.append(
        f"対象: 断片 {data['fragments']} 編 / 地の文 {data['prose_chars']:,} 字"
        f"（鉤括弧内 {data['quoted_chars']:,} 字は別掲）"
    )
    lines.append("")
    lines.append("--- 1. 語群ごとの合計（地の文のみ） ---")
    for name in GROUPS:
        totals = data["group_totals"][name]
        docs = data["group_docs"][name]
        if not totals:
            lines.append(f"  {name}: 0回 / 0編")
            continue
        total = sum(totals.values())
        detail = "、".join(f"{token}×{count}" for token, count in totals.items())
        lines.append(f"  {name}: {total}回 / {len(docs)}編（{detail}）")
    lines.append("")
    lines.append("--- 2. 多義の生字と内訳（群に合算しない参考値） ---")
    for token, count in data["raw_totals"].items():
        lines.append(f"  {token}: {count}回 — {POLYSEMY_NOTE.get(token, '多義')}")
    bd = data.get("polysemy_breakdown", {})
    if bd:
        lines.append(
            f"    ・『空』{bd['空']['total']}回中: 空白・空欄・空車・空のまま・空気等={bd['空']['blank_or_empty_or_air']}回 / "
            f"残り（天空）={bd['空']['remaining_sky_candidates']}回"
        )
        lines.append(
            f"    ・『窓』{bd['窓']['total']}回中: 窓口・窓枠・『窓がない』等={bd['窓']['counter_frame_or_negated']}回 / "
            f"残り（建築の窓）={bd['窓']['remaining_architectural_window']}回"
        )
        lines.append(
            f"    ・『道』{bd['道']['total']}回中: 道具・筋道等={bd['道']['tool_or_logic_compound']}回 / "
            f"残り（道路・経路比喩）={bd['道']['remaining_road_or_path_metaphor']}回"
        )
        lines.append(
            f"    ・『足』{bd['足']['total']}回中: 書き足す・継ぎ足し・足りる等={bd['足']['addition_or_sufficiency']}回 / "
            f"残り（身体・歩行の足）={bd['足']['remaining_bodily_foot']}回"
        )
    lines.append("")
    lines.append("--- 3. 鉤括弧の内側にある語（引用・発話内） ---")
    if not data["inside_quotes"]:
        lines.append("  なし")
    else:
        for token, count in data["inside_quotes"].items():
            lines.append(f"  {token}: {count}回")
    lines.append("")
    lines.append("--- 4. 断片ごとの内訳（主要語群のみ） ---")
    for row in data["rows"]:
        if not row["groups"]:
            continue
        parts = []
        for name, counts in row["groups"].items():
            parts.append(f"{name}=" + "、".join(f"{k}×{v}" for k, v in counts.items()))
        lines.append(f"  {row['fragment_id']} [{row['narrator_mode']}]: " + " / ".join(parts))
    lines.append("")
    lines.append("0は指定語形の不在であって、移動・空間把握・場所の感覚の不在を証明するものではありません。")
    return "\n".join(lines)


def report_corpus(data: dict[str, Any]) -> str:
    lines = [f"=== 道と地図の鏡（{data['corpus']}） ==="]
    lines.append(f"対象: {data['documents']} 件 / {data['chars']:,} 字")
    for name in GROUPS:
        totals = data["group_totals"][name]
        doc_count = data["group_doc_counts"][name]
        total = sum(totals.values())
        if not totals:
            lines.append(f"  {name}: 0回 / 0件")
        else:
            top = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
            detail = "、".join(f"{t}×{c}" for t, c in top)
            lines.append(f"  {name}: {total}回 / {doc_count}件（上位: {detail}）")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print measurement as JSON")
    parser.add_argument("--show", metavar="FRAGMENT_ID", help="show one fragment's hits and prose")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base file")
    parser.add_argument(
        "--exclude-shard",
        action="append",
        default=[],
        metavar="SUBSTR",
        help="exclude shard filenames containing SUBSTR",
    )
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md instead")
    parser.add_argument("--materials", action="store_true", help="measure state/materials (title + passage)")
    args = parser.parse_args(argv)

    if args.readings:
        items = [
            (p.name, p.read_text(encoding="utf-8"))
            for p in sorted(READINGS.glob("*.md"))
        ]
        cdata = measure_corpus(items, "readings/*.md")
        print(json.dumps(cdata, ensure_ascii=False, indent=2) if args.json else report_corpus(cdata))
        return 0

    if args.materials:
        mats = load_records(
            MATERIALS,
            "material_id",
            base_only=args.base_only,
            exclude_shards=args.exclude_shard,
        )
        items = [
            (m.get("material_id", "?"), f"{m.get('title', '')}\n{m.get('passage', '')}")
            for m in mats
        ]
        cdata = measure_corpus(items, "materials (title + passage)")
        print(json.dumps(cdata, ensure_ascii=False, indent=2) if args.json else report_corpus(cdata))
        return 0

    fragments = load_records(
        FRAGMENTS,
        "fragment_id",
        base_only=args.base_only,
        exclude_shards=args.exclude_shard,
    )

    if args.show:
        for frag in fragments:
            if frag.get("fragment_id") == args.show:
                lines = [f"=== {args.show} ===", "", frag.get("text", ""), "", "--- 地の文の語 ---"]
                prose = strip_quotes(frag.get("text", ""))
                for name, tokens in GROUPS.items():
                    counts = count_group(prose, tokens)
                    if counts:
                        lines.append(f"  {name}: " + "、".join(f"{k}×{v}" for k, v in counts.items()))
                quote = split_quotes(frag.get("text", ""))
                if quote:
                    lines.append("  （鉤括弧の内側）" + quote)
                print("\n".join(lines))
                return 0
        print(f"unknown fragment: {args.show}", file=sys.stderr)
        return 1

    data = measure(fragments)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
