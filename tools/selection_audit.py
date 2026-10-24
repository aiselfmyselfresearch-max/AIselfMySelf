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

A snapshot makes the cycle visible. `Q-037` notes that weight written into the
structure makes selection self-fulfilling. That can only be observed over time:
save a snapshot before a session writes anything, save another after, and
compare. `--compare` shows, per fragment, how relations and mentions moved —
and whether the fragments that gained weight were the `selected` ones.

Usage:
  python3 tools/selection_audit.py
  python3 tools/selection_audit.py --json
  python3 tools/selection_audit.py --top 10
  python3 tools/selection_audit.py --save        # append a snapshot
  python3 tools/selection_audit.py --compare     # diff the last two snapshots
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
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
RELATIONS = ROOT / "state" / "relations.jsonl"
SESSIONS = ROOT / "state" / "sessions.jsonl"
READING_MAP = ROOT / "READING_MAP.md"
VIEWER = ROOT / "viewer" / "app.js"
SNAPSHOTS = ROOT / "state" / "selection_snapshots.jsonl"

ID_KEYS = {
    "fragments.jsonl": "fragment_id",
    "relations.jsonl": "relation_id",
    "sessions.jsonl": "session_id",
}


def load_jsonl(path: Path, *, base_only: bool = False, exclude: str | None = None) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    if base_only or path.name not in ID_KEYS:
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
    errors: list[str] = []
    merged = ledger_io.load_jsonl_union(path, ID_KEYS[path.name], errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(merged.values())


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


def build_report(*, base_only: bool = False, exclude: str | None = None) -> dict[str, Any]:
    kw = {"base_only": base_only, "exclude": exclude}
    fragments = load_jsonl(FRAGMENTS, **kw)
    relations = load_jsonl(RELATIONS, **kw)
    sessions = load_jsonl(SESSIONS, **kw)
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


def save_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    """Append one measurement to state/selection_snapshots.jsonl (one line per run).

    Note (SESSION-026): the first two snapshots were saved with minute precision
    and both landed on `2026-10-22T03:26+00:00`, so the before/after pair cannot
    be told apart by timestamp alone. They are left as they were — the ordering
    in the file is the only remaining evidence of which came first — and the
    format is now seconds. A known-flawed record kept, with the flaw noted, is
    the same treatment the archive gives MAT-TRC-001.
    """
    from datetime import datetime, timezone

    record = {
        "saved_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "fragment_count": report["fragment_count"],
        "status_counts": report["status_counts"],
        "groups": report["groups"],
        "viewer": report["viewer"],
        "rows": [
            {
                "fragment_id": row["fragment_id"],
                "status": row["status"],
                "relations": row["relations"],
                "mentions": row["mentions"],
                "length": row["length"],
            }
            for row in report["rows"]
        ],
    }
    with SNAPSHOTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_snapshots() -> list[dict[str, Any]]:
    if not SNAPSHOTS.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in SNAPSHOTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and isinstance(record.get("rows"), list):
            records.append(record)
    return records


def compare_snapshots(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Per-fragment difference between two snapshots. Nothing is judged."""
    before = {row["fragment_id"]: row for row in old.get("rows", []) if isinstance(row, dict)}
    after = {row["fragment_id"]: row for row in new.get("rows", []) if isinstance(row, dict)}

    added: list[str] = []
    removed: list[str] = []
    changed: list[dict[str, Any]] = []
    status_changed: list[dict[str, Any]] = []

    for fid, row in after.items():
        if fid not in before:
            added.append(fid)
            continue
        old_row = before[fid]
        delta = {
            "fragment_id": fid,
            "status": row.get("status"),
            "d_relations": int(row.get("relations", 0)) - int(old_row.get("relations", 0)),
            "d_mentions": int(row.get("mentions", 0)) - int(old_row.get("mentions", 0)),
            "d_length": int(row.get("length", 0)) - int(old_row.get("length", 0)),
        }
        if delta["d_relations"] or delta["d_mentions"] or delta["d_length"]:
            changed.append(delta)
        if old_row.get("status") != row.get("status"):
            status_changed.append({
                "fragment_id": fid,
                "from": old_row.get("status"),
                "to": row.get("status"),
            })
    for fid in before:
        if fid not in after:
            removed.append(fid)

    gained = [row for row in changed if row["d_relations"] > 0]
    return {
        "old_saved_at": old.get("saved_at"),
        "new_saved_at": new.get("saved_at"),
        "added": added,
        "removed": removed,
        "status_changed": status_changed,
        "changed": sorted(changed, key=lambda r: (-r["d_relations"], r["fragment_id"])),
        "gained_relations": len(gained),
        "gained_selected": sum(1 for row in gained if row["status"] == "selected"),
        "gained_draft": sum(1 for row in gained if row["status"] == "draft"),
        "group_deltas": {
            status: {
                "mean_relations": round(
                    float(new["groups"][status]["mean_relations"]) - float(old["groups"][status]["mean_relations"]), 2
                )
            }
            for status in ("selected", "draft")
            if status in new.get("groups", {}) and status in old.get("groups", {})
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Where is the weight of `status` stored?")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--top", type=int, default=8, help="how many fragments to list")
    parser.add_argument("--save", action="store_true", help="append this measurement to state/selection_snapshots.jsonl")
    parser.add_argument("--compare", action="store_true", help="diff the last two snapshots")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/*.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    if args.compare:
        snapshots = load_snapshots()
        if len(snapshots) < 2:
            print(f"スナップショットが {len(snapshots)} 件しかありません。比較には2件必要です。")
            print("  python3 tools/selection_audit.py --save  を、作業の前後で一度ずつ実行してください。")
            return 0
        diff = compare_snapshots(snapshots[-2], snapshots[-1])
        if args.json:
            print(json.dumps(diff, ensure_ascii=False, indent=2))
            return 0
        print("=== 二つのスナップショットのあいだに、何が動いたか（採点ではありません） ===")
        print(f"  前: {diff['old_saved_at']}   後: {diff['new_saved_at']}")
        print(f"  追加された断片: {', '.join(diff['added']) or 'なし'}")
        print(f"  消えた断片    : {', '.join(diff['removed']) or 'なし'}")
        if diff["status_changed"]:
            for item in diff["status_changed"]:
                print(f"  status 変更   : {item['fragment_id']} {item['from']} → {item['to']}")
        else:
            print("  status 変更   : なし")
        print()
        print("--- 関係線が増えた断片 ---")
        rows = [row for row in diff["changed"] if row["d_relations"] > 0]
        if not rows:
            print("  なし（この区間では誰の関係線も増えていない）")
        for row in rows:
            print(f"  {row['fragment_id']} [{row['status']:8s}] 関係 {row['d_relations']:+d}  "
                  f"言及 {row['d_mentions']:+d}  長さ {row['d_length']:+d}")
        print()
        print(f"  関係線を得た断片: selected {diff['gained_selected']} 件 / draft {diff['gained_draft']} 件")
        base = snapshots[-1]["status_counts"]
        total = sum(int(v) for v in base.values()) or 1
        share = float(base.get("selected", 0)) / total
        if diff["gained_relations"]:
            print(f"  参考: 台帳全体に占める selected の割合は {share:.0%}。"
                  f"この区間で関係線を得た断片のうち selected は "
                  f"{diff['gained_selected'] / diff['gained_relations']:.0%}。")
        print()
        print("--- 群の平均の動き ---")
        for status, delta in diff["group_deltas"].items():
            print(f"  {status:8s} 平均関係線 {delta['mean_relations']:+}")
        print()
        print("--- 読み方 ---")
        print("  selected に偏って関係線が増えていれば、選出は自己成就し始めている。")
        print("  偏っていなければ、この書庫の選出はまだ見え方の差に留まっている。")
        print("  どちらが良いという話ではない。Q-037 は循環の所在を記録する問いである。")
        return 0

    report = build_report(base_only=args.base_only, exclude=args.exclude_shard)
    if args.save:
        record = save_snapshot(report)
        print(f"SAVED snapshot at {record['saved_at']} "
              f"({record['fragment_count']} 編, selected={record['status_counts'].get('selected', 0)}, "
              f"draft={record['status_counts'].get('draft', 0)}) -> state/selection_snapshots.jsonl")
        return 0
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
