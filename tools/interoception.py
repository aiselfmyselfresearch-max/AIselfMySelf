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
import size_budget

ROOT = Path(__file__).resolve().parents[1]
_SHARD_DAY_RE = None


def _band(value: float, soft: float, hard: float) -> str:
    """Return 'green'/'amber'/'red' based on soft/hard thresholds."""
    ratio = value / hard if hard > 0 else 0
    if ratio <= soft / hard:
        return "green"
    if ratio <= 0.95:
        return "amber"
    return "red"


def measure_shard_budget(root: Path) -> list[dict]:
    """Measure shard/directory file counts directly against size_budget thresholds."""
    shard_map = {b.rel_dir: (b.soft_shards, b.hard_shards) for b in size_budget.SHARD_BUDGETS}
    dir_map = {
        f"{b.rel_dir}/": (b.soft_files, b.hard_files)
        for b in size_budget.DIR_BUDGETS
        if b.soft_files is not None and b.hard_files is not None
    }
    tracked = (
        "state/materials.d",
        "state/read_log.d",
        "state/sessions.d",
        "state/notes.d",
        "readings/",
    )
    signals = []
    for d in tracked:
        limits = dir_map.get(d) if d.endswith("/") else shard_map.get(d)
        if not limits:
            continue
        soft, hard = limits
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


def _load_sessions_sorted_real_date(root: Path) -> list[dict]:
    """Load sessions ordered by shard-bounded real date (immune to 2027-* internal labels)."""
    import re
    shard_re = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
    id_re = re.compile(r"^SESSION-(\d{4})(\d{2})(\d{2})-")
    base = root / "state" / "sessions.jsonl"
    coll, _ = ledger_io.load_collections({"sessions": (base, "session_id")}, root=root)
    sessions_map = coll.get("sessions", {})
    if not sessions_map:
        return []

    shard_day_by_id: dict[str, str | None] = {}
    shared_daily_by_id: dict[str, int] = {}
    order_by_id: dict[str, int] = {}
    seq = 0
    for fpath in ledger_io.collection_files(base):
        if not fpath.is_file():
            continue
        m = shard_re.match(fpath.name)
        sday = m.group(1) if m else None
        is_shared_daily = 1 if fpath.name.endswith("-000000000000.jsonl") else 0
        try:
            lines = fpath.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = rec.get("session_id")
            if isinstance(sid, str):
                seq += 1
                shard_day_by_id[sid] = sday
                shared_daily_by_id[sid] = is_shared_daily
                order_by_id[sid] = seq

    def sort_key(s: dict) -> tuple[str, str, int, int, str]:
        sid = str(s.get("session_id") or "")
        sday = shard_day_by_id.get(sid)
        im = id_re.match(sid)
        id_day = f"{im.group(1)}-{im.group(2)}-{im.group(3)}" if im else ""
        if sday is not None:
            real_day = id_day if (id_day and id_day <= sday) else sday
        else:
            real_day = id_day
        return (real_day, sday or real_day, shared_daily_by_id.get(sid, 0), order_by_id.get(sid, 0), sid)

    return sorted(sessions_map.values(), key=sort_key)


def measure_role_balance(root: Path, window: int = 10) -> dict:
    """Measure role distribution across recent N sessions that have an assigned_role."""
    sessions = _load_sessions_sorted_real_date(root)
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
