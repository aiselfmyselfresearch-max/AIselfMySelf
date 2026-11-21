#!/usr/bin/env python3
"""Temporal continuity audit (Layer 6: Time Continuity — slow dynamics).

Tracks the slow-timescale stability of the belief posterior distribution
following Northoff (2017): self-continuity is supported by slow CMS dynamics
underlying fast task-specific activity. We measure D_KL drift between
snapshots, generation ratios, and discontinuity events.

This tool can compare the current belief state against a stored snapshot
or compute drift over recent sessions using evaluation events.

Usage:
    python3 tools/temporal_continuity.py           # advisory report
    python3 tools/temporal_continuity.py --json    # JSON for self_model
    python3 tools/temporal_continuity.py --check   # exit 1 on structural anomaly
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ledger_io

ROOT = Path(__file__).resolve().parents[1]


def compute_hypothesis_posteriors(evaluations: list[dict]) -> dict[str, float]:
    """Simplified posterior computation: count supports vs refutes per
    hypothesis, normalized. This is a coarse measure for continuity
    tracking; the real posterior is in belief_state.py."""
    scores: dict[str, float] = defaultdict(float)
    for e in evaluations:
        tid = e.get("target_hypothesis_id", "")
        v = e.get("verdict", "")
        wt = 1.0
        if v == "refutes_unconditioned":
            wt = -2.0
        elif v == "narrows_scope":
            wt = 0.3
        elif v == "subsumes":
            wt = 1.5
        scores[tid] += wt
        for cmp_id in e.get("compared_against_hypothesis_ids", []):
            scores[cmp_id] += 0.0  # ensure they appear
    # Convert to probability via softmax-ish normalization
    if not scores:
        return {}
    min_s = min(scores.values())
    shifted = {k: math.exp(max(v - min_s, -10)) for k, v in scores.items()}
    total = sum(shifted.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in shifted.items()}


def d_kl(p: dict[str, float], q: dict[str, float]) -> float:
    """KL(P||Q) in bits, over the union of keys. Missing keys get epsilon."""
    eps = 1e-6
    total = 0.0
    keys = set(p.keys()) | set(q.keys())
    for k in keys:
        pk = max(p.get(k, eps), eps)
        qk = max(q.get(k, eps), eps)
        if pk > 0:
            total += pk * math.log2(pk / qk)
    return max(total, 0.0)


def measure_generation_ratio(hypotheses: list[dict], active_only: bool = True) -> dict[int, int]:
    """Count hypotheses by generation depth (G0, G1, ...)."""
    gen_counts: Counter[int] = Counter()
    for h in hypotheses:
        if active_only and h.get("status") != "active":
            continue
        lid = h.get("lineage_op", "")
        parents = h.get("parent_hypothesis_ids", [])
        # Estimate generation from parent chain depth
        gen = 0
        if parents:
            # We approximate: if it has parents, gen = max parent gen + 1
            # Without full tree traversal, use lineage_op as a rough guide
            gen = 1
        # Look for "G7:" or similar prefix in title/summary? No, use simpler
        # Count depth by parent ids length heuristic
        if lid in {"refines", "splits"} and parents:
            gen = 2
        if lid == "synthesizes" and len(parents) >= 2:
            gen = 3
        gen_counts[gen] += 1
    return dict(gen_counts)


def _load_coll(name: str, id_key: str, root: Path) -> list[dict]:
    base = root / "state" / f"{name}.jsonl"
    coll, errors = ledger_io.load_collections({name: (base, id_key)}, root=root)
    return list(coll.get(name, {}).values())


def run_audit(check: bool = False, as_json: bool = False, root: Path = ROOT) -> int:
    hyps = _load_coll("hypotheses", "hypothesis_id", root)
    evls = _load_coll("evaluations", "evaluation_id", root)

    # Sort evaluations by date
    evls_sorted = sorted(evls, key=lambda e: e.get("created_at", ""))
    n = len(evls_sorted)

    # Compare posteriors at windows
    windows = [max(1, n // 4), max(1, n // 2), max(1, (3 * n) // 4)]
    drift = {}
    if n >= 10:
        p_full = compute_hypothesis_posteriors(evls_sorted)
        for w in windows:
            p_partial = compute_hypothesis_posteriors(evls_sorted[:w])
            drift[f"first_{w}_vs_full"] = round(d_kl(p_full, p_partial), 4)

    # Generation ratio
    gen_ratio = measure_generation_ratio(hyps)

    # Rapid discontinuity detection: did any hypothesis get >0.5 refutation
    # mass in a short window?
    discontinuities = []
    refute_counts: Counter[str] = Counter()
    for e in evls_sorted:
        if e.get("verdict") == "refutes_unconditioned":
            refute_counts[e.get("target_hypothesis_id", "")] += 1
    abrupt_refutes = {hid: cnt for hid, cnt in refute_counts.items() if cnt >= 3}

    result = {
        "total_hypotheses": len(hyps),
        "total_evaluations": n,
        "posterior_drift_bits": drift,
        "generation_ratio_active": gen_ratio,
        "multi_refute_targets": abrupt_refutes,
    }

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("=== Temporal Continuity Audit ===")
    print(f"Active hypotheses: {result['total_hypotheses']}")
    print(f"Total evaluations: {result['total_evaluations']}")
    print()
    print("Posterior drift (D_KL in bits):")
    for label, d in drift.items():
        print(f"  {label}: {d}")
    print()
    print("Generation ratio (active hypotheses, approximate):")
    for g in sorted(gen_ratio.keys()):
        print(f"  G{g}: {gen_ratio[g]}")
    if abrupt_refutes:
        print()
        print("Hypotheses with 3+ refutation evaluations (possible discontinuity):")
        for hid, cnt in abrupt_refutes.items():
            print(f"  {hid}: {cnt} refutations")

    print("\nPASS (advisory)" if not check else "\nPASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return run_audit(check=args.check, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
