#!/usr/bin/env python3
"""Measure how continuity of self is recorded in this archive.

The ledger stores evidence of continuity (what was read, how often, by which
session) but has no field for felt continuity.  This tool prints the six
measurements that the 2026-11-20 report
(readings/2026-11-20-where-continuity-is-recorded-a-measurement.md) uses:

1. concentration of read_log rows on the three central questions;
2. distribution of `reading` values (verbatim vs reconstructive access);
3. how often `in_reply_to` (addressee / distance) is recorded;
4. overlap of `context_material_ids` between consecutive sessions;
5. whether any ledger key names an experiential state (feel/affect/qualia);
6. which materials are revisited most often, and how many of them are
   literary-philosophical (MAT-LIT-*) rather than scientific.

Read-only.  Standard library only.  `--json` emits machine-readable output.

    python3 tools/self_continuity_metrics.py
    python3 tools/self_continuity_metrics.py --json
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLLECTIONS = (
    "materials",
    "sessions",
    "read_log",
    "notes",
    "evaluations",
    "hypotheses",
    "fragments",
    "relations",
    "questions",
    "motifs",
    "errata",
    "editorial_decisions",
)

EXPERIENTIAL_TOKENS = (
    "feel",
    "affect",
    "emotion",
    "qualia",
    "subjectiv",
    "sentien",
    "suffer",
    "interocept",
)


def load(name: str) -> list[dict]:
    rows: list[dict] = []
    paths = [os.path.join(ROOT, "state", f"{name}.jsonl")]
    paths += sorted(glob.glob(os.path.join(ROOT, "state", f"{name}.d", "*.jsonl")))
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def pct(part: int, total: int) -> float:
    return round(100.0 * part / total, 1) if total else 0.0


def measure() -> dict:
    read_log = load("read_log")
    sessions = load("sessions")
    materials = {row["material_id"]: row for row in load("materials")}

    total = len(read_log)
    readings = collections.Counter(row.get("reading") for row in read_log)
    targets = collections.Counter(row["target"]["id"] for row in read_log)
    central = sum(targets[q] for q in ("Q-001", "Q-002", "Q-003"))

    material_targets = collections.Counter(
        row["target"]["id"] for row in read_log if row["target"]["type"] == "material"
    )
    top_materials = [
        {
            "material_id": mid,
            "title": (materials.get(mid, {}).get("title") or "")[:70],
            "reads": count,
            "literary": "LIT" in mid,
        }
        for mid, count in material_targets.most_common(20)
    ]

    ordered = sorted(sessions, key=lambda r: (r.get("started_at") or "", r["session_id"]))
    overlaps: list[tuple[int, int]] = []
    for before, after in zip(ordered, ordered[1:]):
        left = set(before.get("context_material_ids") or [])
        right = set(after.get("context_material_ids") or [])
        if left or right:
            overlaps.append((len(left & right), len(left | right)))
    zero_overlap = sum(1 for shared, _ in overlaps if shared == 0)

    keys: set[str] = set()
    for name in COLLECTIONS:
        for row in load(name):
            keys.update(row)
    experiential = sorted(k for k in keys if any(t in k.lower() for t in EXPERIENTIAL_TOKENS))

    verified = collections.Counter(
        ((row.get("verification") or {}).get("status") or "none") for row in materials.values()
    )

    return {
        "read_log_rows": total,
        "unique_targets": len(targets),
        "targets_read_once": sum(1 for v in targets.values() if v == 1),
        "targets_read_three_or_more": sum(1 for v in targets.values() if v >= 3),
        "central_question_rows": central,
        "central_question_pct": pct(central, total),
        "reading_counts": dict(readings),
        "verbatim_pct": pct(readings.get("quoted", 0), total),
        "reconstructive_pct": pct(
            readings.get("interpreted", 0) + readings.get("reinterpreted", 0), total
        ),
        "context_only_pct": pct(readings.get("used_as_context", 0), total),
        "in_reply_to_rows": sum(1 for row in read_log if row.get("in_reply_to")),
        "in_reply_to_pct": pct(sum(1 for row in read_log if row.get("in_reply_to")), total),
        "session_pairs": len(overlaps),
        "zero_overlap_pairs": zero_overlap,
        "zero_overlap_pct": pct(zero_overlap, len(overlaps)),
        "mean_jaccard": round(
            statistics.mean(shared / union if union else 0.0 for shared, union in overlaps), 3
        )
        if overlaps
        else 0.0,
        "top_level_keys": len(keys),
        "experiential_keys": experiential,
        "material_status": dict(verified),
        "materials_read": len(material_targets),
        "materials_read_three_or_more": sum(1 for v in material_targets.values() if v >= 3),
        "top_materials": top_materials,
        "top20_literary": sum(1 for row in top_materials if row["literary"]),
        "top20_reads": sum(row["reads"] for row in top_materials),
    }


def render(data: dict) -> str:
    lines = [
        "# 自己の連続は、どこに記録されているか（台帳の自己測定）",
        "",
        f"read_log 行数: {data['read_log_rows']:,}",
        f"  対象の種類: {data['unique_targets']:,} ／ 一度だけ {data['targets_read_once']:,} "
        f"／ 3回以上 {data['targets_read_three_or_more']:,}",
        f"  中心三問への行: {data['central_question_rows']:,} "
        f"({data['central_question_pct']}%)",
        "",
        "読み方の分布:",
    ]
    for kind, count in sorted(data["reading_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"  {str(kind):<18} {count:>7,}  ({pct(count, data['read_log_rows'])}%)")
    lines += [
        "",
        f"逐語（quoted）: {data['verbatim_pct']}% ／ 再構成（interpreted+reinterpreted）: "
        f"{data['reconstructive_pct']}% ／ 文脈のみ: {data['context_only_pct']}%",
        f"宛先（in_reply_to）: {data['in_reply_to_rows']:,} 行 ({data['in_reply_to_pct']}%)",
        "",
        f"連続するセッションの context 素材: {data['session_pairs']:,} 組のうち "
        f"{data['zero_overlap_pairs']:,} 組が共有ゼロ ({data['zero_overlap_pct']}%)"
        f" ／ 平均 Jaccard {data['mean_jaccard']}",
        "",
        f"台帳のトップレベル鍵: {data['top_level_keys']} 種"
        f" ／ 感覚・感情を名指す鍵: {len(data['experiential_keys'])} 種 {data['experiential_keys']}",
        "",
        f"素材の検証状態: {data['material_status']}",
        f"読まれた素材: {data['materials_read']:,}（3回以上 {data['materials_read_three_or_more']:,}）",
        "",
        f"最も繰り返し読まれた素材トップ20（うち文芸・哲学 {data['top20_literary']}/20、"
        f"合計 {data['top20_reads']:,} 行）:",
    ]
    for row in data["top_materials"][:10]:
        lines.append(f"  {row['reads']:>3}  {row['material_id']:<28} {row['title']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = parser.parse_args(argv)
    data = measure()
    if args.json:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=1)
        sys.stdout.write("\n")
    else:
        print(render(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
