#!/usr/bin/env python3
"""Read-only gated-scope experiment; never edits ledgers or engine weights.

Reproduce the 2026-11-25 c647ba34 pre-evaluation snapshot on this checkout:
  python3 tools/gated_scope_probe.py --exclude-session SESSION-20261125-7ad91d
Exclusion removes this session's rows in memory, not on disk. Later sessions
are NOT excluded: reproduce an exact historical result using its Git commit.
The material-only arm restores raw materials; the full arm also restores raw
questions/fragments. Neither erases initial material verification claims.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

try:
    from . import belief_state, ledger_io
except ImportError:
    import belief_state
    import ledger_io

ROOT = Path(__file__).resolve().parents[1]
CORE = ("Q-001", "Q-002", "Q-003")
TARGETS = ("HYP-20261121-6e83a4", "HYP-20261124-6622b8",
           "HYP-20261125-8a5b51", "HYP-20261122-c8df23")


def average_ranks(values: list[Any]) -> list[float]:
    """Ascending ranks, averaging ties (no arbitrary ID tie-breaking)."""
    ranks = [0.0] * len(values)
    order = sorted(range(len(values)), key=values.__getitem__)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2
        for i in order[start:end]:
            ranks[i] = rank
        start = end
    return ranks


def spearman(x: list[Any], y: list[Any]) -> float | None:
    """Pearson correlation of average ranks, including tied dates/counts."""
    if len(x) != len(y):
        raise ValueError("rank vectors must have equal lengths")
    if len(x) < 2:
        return None
    a, b = average_ranks(x), average_ranks(y)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    aa = sum((v - ma) ** 2 for v in a)
    bb = sum((v - mb) ** 2 for v in b)
    if aa == 0 or bb == 0:
        return None
    return sum((v - ma) * (w - mb) for v, w in zip(a, b)) / math.sqrt(aa * bb)


def raw_collection(root: Path, name: str, id_key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in ledger_io.collection_files(root / "state" / f"{name}.jsonl"):
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    if row[id_key] in rows:
                        raise ValueError(f"duplicate {name}: {row[id_key]}")
                    rows[row[id_key]] = row
    return rows


def distribution(result: dict, q: str) -> dict[str, float]:
    return {h["hypothesis_id"]: h["posterior"]
            for h in result["questions"][q]["hypotheses"]}


def l1(a: dict[str, float], b: dict[str, float]) -> float:
    return sum(abs(a.get(k, 0) - b.get(k, 0)) for k in a.keys() | b.keys())


def run(root: Path = ROOT, excluded_sessions: tuple[str, ...] = ()) -> dict:
    data = belief_state.load_belief_ledgers(root)
    data = {name: {key: row for key, row in rows.items()
                   if row.get("session_id") not in excluded_sessions}
            for name, rows in data.items()}
    # Hash the actual effective inputs, not mtimes or nondeterministic paths.
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False)
                            .encode("utf-8")).hexdigest()
    raw = raw_collection(root, "materials", "material_id")
    assert raw.keys() == data["materials"].keys()
    base = belief_state.compute_belief_state(data, root=root, receiver_gated=True)
    unoverlaid = copy.deepcopy(data)
    unoverlaid["materials"] = raw
    ablated = belief_state.compute_belief_state(unoverlaid, root=root, receiver_gated=True)
    full_unoverlaid = copy.deepcopy(unoverlaid)
    for name, key in (("questions", "question_id"), ("fragments", "fragment_id")):
        full_unoverlaid[name] = raw_collection(root, name, key)
    full_ablated = belief_state.compute_belief_state(
        full_unoverlaid, root=root, receiver_gated=True)
    historical = belief_state.compute_belief_state(data, root=root)
    historical_ablated = belief_state.compute_belief_state(unoverlaid, root=root)

    eds, errors = ledger_io.load_collections(
        {"editorial_decisions": (root / "state/editorial_decisions.jsonl", "decision_id")},
        root=root)
    if errors:
        raise ValueError("; ".join(errors))
    material_eds = [e for e in eds["editorial_decisions"].values()
                    if e["target"]["type"] == "material"]
    changed = [mid for mid in raw
               if raw[mid].get("verification", {}).get("status") !=
               data["materials"][mid].get("verification", {}).get("status")]
    outcome = {}
    for q in CORE:
        hs = base["questions"][q]["hypotheses"]
        dates = [data["hypotheses"][h["hypothesis_id"]]["created_at"] for h in hs]
        evals = [h["direct_eval_count"] for h in hs]
        posterior = [h["posterior"] for h in hs]
        ql1 = l1(distribution(base, q), distribution(ablated, q))
        outcome[q] = {
            "n": len(hs),
            "ed_material_ablation_l1_rounded_posterior": round(ql1, 6),
            "ed_material_ablation_tvd": round(ql1 / 2, 6),
            "ed_all_overlays_ablation_l1": round(l1(
                distribution(base, q), distribution(full_ablated, q)), 6),
            "historical_ablation_l1": round(l1(distribution(historical, q),
                                             distribution(historical_ablated, q)), 6),
            "rho_later_date_vs_eval_count": spearman(dates, evals),
            "rho_later_date_vs_gated_posterior": spearman(dates, posterior),
            "targets": {h["hypothesis_id"]: {
                k: h[k] for k in ("posterior", "effective_status", "direct_eval_count",
                                 "log_odds", "independent_separation_count")}
                for h in hs if h["hypothesis_id"] in TARGETS},
        }
    own = data["hypotheses"][TARGETS[3]]
    return {
        "writes": False,
        "excluded_sessions": list(excluded_sessions),
        "effective_inputs_sha256": digest,
        "engine_sha256": hashlib.sha256((root / "tools/belief_state.py").read_bytes()).hexdigest(),
        "counts": {name: len(rows) for name, rows in data.items()},
        "material_ed_rows": len(material_eds),
        "effective_status_changed_materials": len(changed),
        "all_materials": len(raw),
        "changed_material_ids": sorted(changed),
        "questions": outcome,
        "clause_c_all_core_l1_below_0_05": all(
            outcome[q]["ed_all_overlays_ablation_l1"] < 0.05 for q in CORE),
        "orphan": {
            "id": TARGETS[3],
            "initial_scope_conditions": own["scope_conditions"],
            "parent_link_children": [h["hypothesis_id"] for h in data["hypotheses"].values()
                                     if TARGETS[3] in h.get("parent_hypothesis_ids", [])],
            "evaluations": [{k: e.get(k, []) for k in
                             ("evaluation_id", "verdict", "spawned_hypothesis_ids",
                              "scope_inherited_by_hypothesis_ids")}
                            for e in data["evaluations"].values()
                            if e["target_hypothesis_id"] == TARGETS[3]],
        },
        "limitations": [
            "Full ED arm removes material/question/fragment overlays, not raw verification.",
            "L1 uses engine-exported posterior rounded to four decimals.",
            "All registered hypotheses included; status, age and lineage confound correlations.",
            "Posterior and evaluation count are proxies, not validated developmental outcomes.",
            "Excluding one session does not freeze future additions; use the Git snapshot.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--exclude-session", action="append", default=[])
    args = parser.parse_args()
    print(json.dumps(run(args.root, tuple(args.exclude_session)), ensure_ascii=False,
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
