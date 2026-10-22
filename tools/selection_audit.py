#!/usr/bin/env python3
"""Measure what `status` actually changes in the archive. A mirror, not a verdict.

`SESSION-024` wrote `Q-036`: when selected fragments and unselected drafts sit
on the same shelf, what perspective does the archive make? That question sounds
like an editorial one, but part of it is measurable. This tool counts, for each
fragment, four kinds of weight that the ledger itself records:

  1. relations  — how many `relations.jsonl` edges touch the fragment
  2. sessions   — how many sessions name it in `produced_fragment_ids`
  3. mentions   — how often its ID appears in the generated `READING_MAP.md`
  4. length     — characters of body text

It then compares the `selected` group with the `draft` group, and — because
`MAT-TRC-002` showed that what a reader sees is decided by `viewer/app.js` as
much as by the ledger — it also reads the drawing constants out of the viewer.

The tool does not say that selection is right or wrong, and the numbers are not
a quality score. It only makes visible where the difference between "selected"
and "draft" is stored, and where it is not stored at all.

Usage:
  python3 tools/selection_audit.py
  python3 tools/selection_audit.py --json
  python3 tools/selection_audit.py --top 10
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = ROOT / "state" / "fragments.jsonl"
RELATIONS = ROOT / "state" / "relations.jsonl"
SESSIONS = ROOT / "state" / "sessions.jsonl"
READING_MAP = ROOT / "READING_MAP.md"
VIEWER = ROOT / "viewer" / "app.js"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def relation_counts(relations: list[dict[str, Any]]) -> tuple[Counter, dict[str, Counter]]:
    degree: Counter = Counter()
    by_type: dict[str, Counter] = defaultdict(Counter)
    for relation in relations:
        rtype = str(relation.get("relation_type", "?"))
        for side in ("left", "right"):
            endpoint = relation.get(side)
            if not isinstance(endpoint, dict) or endpoint.get("type") != "fragment":
                continue
            fid = str(endpoint.get("id", ""))
            if not fid:
                continue
            degree[fid] += 1
            by_type[fid][rtype] += 1
    return degree, by_type


def session_counts(sessions: list[dict[str, Any]]) -> Counter:
    produced: Counter = Counter()
    for session in sessions:
        ids = session.get("produced_fragment_ids", [])
        if not isinstance(ids, list):
            continue
        for fid in ids:
            produced[str(fid)] += 1
    return produced


def mention_counts(fragment_ids: list[str]) -> Counter:
    if not READING_MAP.is_file():
        return Counter()
    text = READING_MAP.read_text(encoding="utf-8")
    return Counter({fid: len(re.findall(re.escape(fid), text)) for fid in fragment_ids})


def viewer_constants() -> dict[str, Any]:
    """Read how the viewer draws the two statuses. Returns {} when unreadable."""
    if not VIEWER.is_file():
        return {}
    source = VIEWER.read_text(encoding="utf-8")
    constants: dict[str, Any] = {}
    radius = re.search(r"radius:\s*[^;]*f\.status\s*===\s*\"selected\"\s*\?\s*([0-9.]+)\s*:\s*([0-9.]+)", source)
    if radius:
        constants["constellation_radius_selected"] = float(radius.group(1))
        constants["constellation_radius_draft"] = float(radius.group(2))
    constants["has_status_filter"] = 'filter-status' in source
    constants["has_status_badge"] = "badge-selected" in source
    return constants


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def build_report() -> dict[str, Any]:
    fragments = load_jsonl(FRAGMENTS)
    relations = load_jsonl(RELATIONS)
    sessions = load_jsonl(SESSIONS)
    ids = [str(f.get("fragment_id", "")) for f in fragments if f.get("fragment_id")]

    degree, rel_types = relation_counts(relations)
    produced = session_counts(sessions)
    mentions = mention_counts(ids)

    rows: list[dict[str, Any]] = []
    for fragment in fragments:
        fid = str(fragment.get("fragment_id", ""))
        if not fid:
            continue
        rows.append({
            "fragment_id": fid,
            "status": str(fragment.get("status", "")),
            "form": str(fragment.get("form", "")),
            "narrator_mode": str(fragment.get("narrator_mode", "")),
            "title": str(fragment.get("title", "")),
            "length": len(str(fragment.get("text", ""))),
            "relations": degree[fid],
            "relation_types": dict(rel_types[fid]),
            "sessions": produced[fid],
            "mentions": mentions[fid],
        })

    groups: dict[str, dict[str, Any]] = {}
    for status in ("selected", "draft", "archived"):
        group = [row for row in rows if row["status"] == status]
        if not group:
            continue
        groups[status] = {
            "count": len(group),
            "mean_relations": mean([row["relations"] for row in group]),
            "mean_length": mean([row["length"] for row in group]),
            "mean_mentions": mean([row["mentions"] for row in group]),
            "sessions_citing": sum(1 for row in group if row["sessions"]),
        }

    status_counts = Counter(row["status"] for row in rows)
    return {
        "fragment_count": len(rows),
        "status_counts": dict(status_counts),
        "groups": groups,
        "viewer": viewer_constants(),
        "rows": sorted(rows, key=lambda r: (-r["relations"], r["fragment_id"])),
        "most_connected_drafts": [r["fragment_id"] for r in rows if r["status"] == "draft" and r["relations"] >= 5],
        "least_connected_selected": [
            r["fragment_id"] for r in sorted(rows, key=lambda r: r["relations"])
            if r["status"] == "selected"
        ][:5],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Where is the weight of `status` stored?")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--top", type=int, default=8, help="how many fragments to list")
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    counts = report["status_counts"]
    print("=== 選出の重さはどこに保存されているか — 棚の遠近法を測る（採点ではありません） ===")
    print(f"対象: state/fragments.jsonl {report['fragment_count']} 編 "
          f"(selected={counts.get('selected', 0)}, draft={counts.get('draft', 0)}, archived={counts.get('archived', 0)})")
    print()

    print("--- 1. 関係線の本数（多い順） ---")
    for row in report["rows"][: args.top]:
        print(f"  {row['fragment_id']}  [{row['status']:8s}] {row['form']:9s} "
              f"{row['narrator_mode']:24s} 関係={row['relations']:2d}  "
              f"言及={row['mentions']:2d}  長さ={row['length']:4d}")
    print()

    print("--- 2. 群ごとの平均 ---")
    for status, group in report["groups"].items():
        print(f"  {status:8s} n={group['count']:2d}  "
              f"関係={group['mean_relations']:>4}  "
              f"READING_MAP言及={group['mean_mentions']:>5}  "
              f"本文長={group['mean_length']:>6}  "
              f"セッション記録あり={group['sessions_citing']}/{group['count']}")
    print()

    viewer = report["viewer"]
    if viewer.get("constellation_radius_selected") is not None:
        sel = viewer["constellation_radius_selected"]
        draft = viewer["constellation_radius_draft"]
        print("--- 3. 閲覧器（viewer/app.js）が実際に描き分けているもの ---")
        print(f"  星座図の半径: selected={sel} / draft={draft}  (比 {sel / draft:.2f} 倍)")
        print(f"  状態フィルタ: {'あり' if viewer.get('has_status_filter') else 'なし'} / "
              f"状態バッジ: {'あり' if viewer.get('has_status_badge') else 'なし'}")
        print()
        print("  つまり、この書庫で selected と draft を分けているのは、"
              f"関係線の {report['groups'].get('selected', {}).get('mean_relations', 0)} 対 "
              f"{report['groups'].get('draft', {}).get('mean_relations', 0)} ではなく、"
              f"描画の半径 {sel} 対 {draft} である。")
        print()

    if report["most_connected_drafts"]:
        print("--- 4. 選ばれていないのに、よく線が集まっている草稿 ---")
        print("  " + ", ".join(report["most_connected_drafts"]))
        print("  選出は関係の多さで決まっていない。逆に言えば、関係の多さは選出を押し上げない。")
        print()

    if report["least_connected_selected"]:
        print("--- 5. 選ばれているのに、線の少ない断片 ---")
        print("  " + ", ".join(report["least_connected_selected"]))
        print()

    print("--- 読み方 ---")
    print("  この表は合否でも品質評価でもない（PROJECT_CHARTER.md「成功の見方」）。")
    print("  数えるのは、status という一語が書庫のどこに効いているかだけである。")
    print("  どこにも効いていないなら、それは選出が無効だという意味ではなく、")
    print("  選出の重みがまだ文章になっていないという意味になる。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
