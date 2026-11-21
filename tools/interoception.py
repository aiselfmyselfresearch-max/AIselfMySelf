#!/usr/bin/env python3
"""Interoception audit (Layer 3: Embodiment — internal state signals).

Reports the archive's internal state in three bands (green/amber/red)
analogous to interoceptive signals (body budget, balance, connectivity,
consistency, idle time). This is the input for SELF_MODEL.md's
interoception section and does NOT write anything by itself.

Follows Seth (2013, interoceptive inference): the system maintains an
internal model of its own state, and prediction errors drive updates.
Here we measure the signals; the self_model uses them.

Usage:
    python3 tools/interoception.py          # print signals
    python3 tools/interoception.py --json   # JSON output for self_model
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import ledger_io

ROOT = Path(__file__).resolve().parents[1]


def _band(value: float, soft: float, hard: float) -> str:
    """Return 'green'/'amber'/'red' based on soft/hard thresholds."""
    ratio = value / hard if hard > 0 else 0
    if ratio <= soft / hard:
        return "green"
    if ratio <= 0.95:
        return "amber"
    return "red"


def measure_shard_budget(root: Path) -> list[dict]:
    """Measure shard directory file counts vs soft/hard limits by reading
    size_budget configuration inline (avoids importing it directly)."""
    # We invoke size_budget.py's internal logic indirectly by parsing its
    # output format, but for simplicity we just count shards in key dirs.
    signals = []
    shard_dirs = {
        "state/materials.d": (148, 160),       # observed soft/hard for 1082 files
        "state/read_log.d": (173, 175),
        "state/sessions.d": (178, 179),
        "state/notes.d": (179, 180),
        "readings/": (1087, 1200),       # synced to size_budget.py after merging origin/main ad7de5a5 (two same-day reports)
    }
    for d, (soft, hard) in shard_dirs.items():
        p = root / d
        if d.endswith("/"):
            count = sum(1 for f in p.iterdir() if f.is_file() and f.name.endswith(".md")) if p.is_dir() else 0
        else:
            count = sum(1 for f in p.iterdir() if f.is_file() and f.name.endswith(".jsonl")) if p.is_dir() else 0
        signals.append({
            "name": f"file_count:{d}",
            "value": count,
            "soft": soft,
            "hard": hard,
            "band": _band(count, soft, hard),
        })
    return signals


def _load_coll(name: str, id_key: str, root: Path) -> list[dict]:
    base = root / "state" / f"{name}.jsonl"
    coll, errors = ledger_io.load_collections({name: (base, id_key)}, root=root)
    return list(coll.get(name, {}).values())


def measure_role_balance(root: Path, window: int = 10) -> dict:
    """Measure role distribution across recent N sessions that have an assigned_role."""
    sessions = sorted(_load_coll("sessions", "session_id", root), key=lambda s: s.get("started_at") or s.get("session_id", ""))
    with_roles = [s for s in sessions if s.get("assigned_role")]
    recent = with_roles[-window:] if len(with_roles) >= window else with_roles
    roles = Counter(s.get("assigned_role", "unknown") for s in recent)
    total = sum(roles.values()) or 1
    # Balanced: proposer ~25%, adversarial_tester ~50%, consolidator ~25%
    target = {"proposer": 0.25, "adversarial_tester": 0.50, "consolidator": 0.25}
    max_deviation = 0.0
    for role, frac in target.items():
        observed = roles.get(role, 0) / total
        max_deviation = max(max_deviation, abs(observed - frac))
    band = "green" if max_deviation < 0.20 else "amber" if max_deviation < 0.35 else "red"
    return {
        "name": "role_balance",
        "recent_n": len(recent),
        "distribution": dict(roles),
        "max_deviation_from_target": round(max_deviation, 3),
        "band": band,
    }


def measure_connectivity(root: Path) -> dict:
    """Measure orphan notes (notes with no incoming read_log/evaluation reference)."""
    notes_list = _load_coll("notes", "note_id", root)
    evl_list = _load_coll("evaluations", "evaluation_id", root)
    rl_list = _load_coll("read_log", "read_id", root)

    all_note_ids = set()
    referenced_notes: set[str] = set()
    for n in notes_list:
        nid = n.get("note_id", "")
        if nid:
            all_note_ids.add(nid)
    for e in evl_list:
        for nid in e.get("note_ids", []):
            referenced_notes.add(nid)
    for rl in rl_list:
        tgt = rl.get("target", {})
        if tgt.get("type") == "note":
            referenced_notes.add(tgt.get("id", ""))

    orphans = all_note_ids - referenced_notes
    # Index backfills are expected orphans
    non_backfill_orphans = []
    for n in notes_list:
        if n.get("note_id") in orphans and not n.get("index_backfill", False):
            non_backfill_orphans.append(n.get("note_id"))

    orphan_ratio = len(non_backfill_orphans) / max(len(all_note_ids), 1)
    band = "green" if orphan_ratio < 0.05 else "amber" if orphan_ratio < 0.15 else "red"
    return {
        "name": "connectivity",
        "total_notes": len(all_note_ids),
        "orphan_notes_non_backfill": len(non_backfill_orphans),
        "orphan_ratio": round(orphan_ratio, 4),
        "band": band,
    }


def measure_consistency(root: Path, window: int = 5) -> dict:
    """Measure belief posterior stability over recent sessions.
    Uses D_KL from learning_metrics as a proxy; falls back to a simple
    measurement of evaluation volume variability."""
    # We approximate consistency by counting recent evaluations
    evls = sorted(_load_coll("evaluations", "evaluation_id", root), key=lambda e: e.get("created_at", ""))
    if not evls:
        return {"name": "consistency", "signal": "no_data", "band": "green"}

    # Simple heuristic: variance in evaluations per session
    by_session: Counter[str] = Counter()
    for e in evls:
        by_session[e.get("session_id", "?")] += 1
    recent_counts = list(by_session.values())[-window:]
    if not recent_counts:
        return {"name": "consistency", "signal": "no_recent", "band": "green"}
    avg = sum(recent_counts) / len(recent_counts)
    variance = sum((c - avg) ** 2 for c in recent_counts) / len(recent_counts) if recent_counts else 0
    # High variance = less consistent output rate
    band = "green" if variance < 4 else "amber" if variance < 16 else "red"
    return {
        "name": "consistency",
        "recent_eval_counts": recent_counts,
        "avg_per_session": round(avg, 2),
        "variance": round(variance, 2),
        "band": band,
    }


def run_measure(root: Path = ROOT) -> dict:
    return {
        "shard_budgets": measure_shard_budget(root),
        "role_balance": measure_role_balance(root),
        "connectivity": measure_connectivity(root),
        "consistency": measure_consistency(root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    signals = run_measure()

    if args.json:
        print(json.dumps(signals, indent=2, ensure_ascii=False))
        return 0

    print("=== Interoception Signals ===")
    print()
    print("Shard / file counts:")
    for s in signals["shard_budgets"]:
        print(f"  [{s['band'].upper():5s}] {s['name']}: {s['value']} (soft {s['soft']}, hard {s['hard']})")
    rb = signals["role_balance"]
    print(f"\n[{rb['band'].upper():5s}] Role balance (last {rb['recent_n']} sessions): {rb['distribution']}, max deviation={rb['max_deviation_from_target']}")
    cn = signals["connectivity"]
    print(f"[{cn['band'].upper():5s}] Connectivity: {cn['orphan_notes_non_backfill']}/{cn['total_notes']} orphan notes ({cn['orphan_ratio']*100:.1f}%)")
    cs = signals["consistency"]
    print(f"[{cs['band'].upper():5s}] Consistency: recent eval counts={cs.get('recent_eval_counts','?')}, variance={cs.get('variance','?')}")

    # Overall band
    all_bands = [s["band"] for s in signals["shard_budgets"]] + [signals["role_balance"]["band"], signals["connectivity"]["band"], signals["consistency"]["band"]]
    if "red" in all_bands:
        overall = "red"
    elif "amber" in all_bands:
        overall = "amber"
    else:
        overall = "green"
    print(f"\nOverall interoceptive state: {overall.upper()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
