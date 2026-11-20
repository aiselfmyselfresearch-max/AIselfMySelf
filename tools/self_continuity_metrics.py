#!/usr/bin/env python3
"""Measure how continuity of self is recorded in this archive.

The ledger stores evidence of continuity (what was read, how often, by which
session) but has no field for felt continuity.  This tool prints the
measurements the 2026-11-20 reports use:

1. concentration of read_log rows on the three central questions;
2. distribution of `reading` values (verbatim vs reconstructive access);
3. how often `in_reply_to` (addressee / distance) is recorded;
4. overlap of `context_material_ids` between consecutive sessions;
5. whether any ledger key names an experiential state (feel/affect/qualia);
6. which materials are revisited most often, and how many of them are
   literary-philosophical (MAT-LIT-*) rather than scientific;
7. (v2) overlap of the *materials actually read* between consecutive sessions,
   which tests the declared-context measure in (4);
8. (v2) the same comparison inside an exposure-matched cohort, which tests
   whether the literary advantage in (6) is only a head-start effect.

Read-only.  Standard library only.  `--json` emits machine-readable output.

    python3 tools/self_continuity_metrics.py
    python3 tools/self_continuity_metrics.py --json
"""

from __future__ import annotations

import argparse
import collections
import datetime
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

# A material enters the exposure-matched cohort only when it was available for
# this many sessions, so a late arrival cannot look unloved merely because it
# had fewer chances.  300 is roughly the whole span of the dated sessions.
COHORT_EXPOSURE = 300


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


def day(value: str | None) -> str:
    """Return a YYYY-MM-DD prefix, or '' when the value is missing."""
    return (value or "")[:10]


def _overlap(left: dict[str, set], right: dict[str, set], order: list[dict]) -> dict:
    pairs = []
    for before, after in zip(order, order[1:]):
        a = left.get(before["session_id"], set())
        b = right.get(after["session_id"], set())
        if a or b:
            pairs.append((len(a & b), len(a | b)))
    zero = sum(1 for shared, _ in pairs if shared == 0)
    return {
        "pairs": len(pairs),
        "zero_overlap": zero,
        "zero_overlap_pct": pct(zero, len(pairs)),
        "mean_jaccard": round(
            statistics.mean(shared / union if union else 0.0 for shared, union in pairs), 3
        )
        if pairs
        else 0.0,
    }


def _exposure_cohort(read_log: list[dict], sessions: list[dict]) -> dict:
    """Compare MAT-LIT-* against the rest at equal exposure."""
    starts = [day(s.get("started_at")) for s in sessions if s.get("started_at")]
    first: dict[str, str] = {}
    reads: collections.Counter[str] = collections.Counter()
    for row in read_log:
        if row["target"]["type"] != "material":
            continue
        mid = row["target"]["id"]
        reads[mid] += 1
        seen = day(row.get("created_at"))
        if seen and (mid not in first or seen < first[mid]):
            first[mid] = seen

    cohort: list[tuple[str, int]] = []
    for mid, count in reads.items():
        seen = first.get(mid)
        if not seen:
            continue
        exposure = sum(1 for d in starts if d >= seen)
        if exposure >= COHORT_EXPOSURE:
            cohort.append((mid, count))

    literary = [count for mid, count in cohort if "LIT" in mid]
    other = [count for mid, count in cohort if "LIT" not in mid]
    top = sorted(cohort, key=lambda pair: -pair[1])[:20]
    total = sum(count for _, count in cohort)
    return {
        "cohort_size": len(cohort),
        "literary_size": len(literary),
        "other_size": len(other),
        "literary_mean_reads": round(statistics.mean(literary), 2) if literary else 0.0,
        "other_mean_reads": round(statistics.mean(other), 2) if other else 0.0,
        "literary_share_five_plus": pct(sum(1 for c in literary if c >= 5), len(literary)),
        "other_share_five_plus": pct(sum(1 for c in other if c >= 5), len(other)),
        "top20_literary": sum(1 for mid, _ in top if "LIT" in mid),
        "top20_reads": sum(count for _, count in top),
        "top20_share_of_cohort_reads": pct(sum(count for _, count in top), total),
        "exposure_threshold": COHORT_EXPOSURE,
    }


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
    declared = {s["session_id"]: set(s.get("context_material_ids") or []) for s in ordered}

    read_all: dict[str, set] = collections.defaultdict(set)
    read_hand: dict[str, set] = collections.defaultdict(set)
    for row in read_log:
        if row["target"]["type"] != "material":
            continue
        sid = row.get("session_id")
        read_all[sid].add(row["target"]["id"])
        if row.get("reading") != "used_as_context":
            read_hand[sid].add(row["target"]["id"])

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
        "declared_context_overlap": _overlap(declared, declared, ordered),
        "read_materials_overlap": _overlap(read_hand, read_hand, ordered),
        "all_read_materials_overlap": _overlap(read_all, read_all, ordered),
        "exposure_cohort": _exposure_cohort(read_log, sessions),
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
    declared = data["declared_context_overlap"]
    read_hand = data["read_materials_overlap"]
    read_all = data["all_read_materials_overlap"]
    cohort = data["exposure_cohort"]
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
        "連続するセッションの重なり:",
        f"  宣言された文脈: {declared['pairs']:,} 組中 {declared['zero_overlap']:,} 組が共有ゼロ "
        f"({declared['zero_overlap_pct']}%) ／ 平均 Jaccard {declared['mean_jaccard']}",
        f"  実読素材（手書き）: {read_hand['pairs']:,} 組中 {read_hand['zero_overlap']:,} 組 "
        f"({read_hand['zero_overlap_pct']}%) ／ 平均 Jaccard {read_hand['mean_jaccard']}",
        f"  実読素材（文脈込み）: {read_all['pairs']:,} 組中 {read_all['zero_overlap']:,} 組 "
        f"({read_all['zero_overlap_pct']}%) ／ 平均 Jaccard {read_all['mean_jaccard']}",
        "",
        f"露出を揃えたコホート（{cohort['exposure_threshold']} セッション以上）: "
        f"{cohort['cohort_size']:,} 素材",
        f"  文芸・哲学: n={cohort['literary_size']:,} 平均 {cohort['literary_mean_reads']} 回 "
        f"／ 5回以上 {cohort['literary_share_five_plus']}%",
        f"  その他:     n={cohort['other_size']:,} 平均 {cohort['other_mean_reads']} 回 "
        f"／ 5回以上 {cohort['other_share_five_plus']}%",
        f"  コホート内トップ20: 文芸 {cohort['top20_literary']}/20、"
        f"コホート全読の {cohort['top20_share_of_cohort_reads']}%",
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
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
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
