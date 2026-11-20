#!/usr/bin/env python3
"""Read-only probe: same-session vs cross-session verdict distribution.

Used as the reproducible script behind the independence-axis (axis ii) test of
HYP-20261120-26b0c6 (証拠会計の三軸説). For every evaluation whose target
hypothesis exists, classify the evaluation as ``same`` (evaluation session equals
the hypothesis's creating session) or ``cross`` and tabulate the verdicts. A
two-sided Fisher exact test on the 2x2 table ``supports`` vs. not-supports is
reported. Nothing is written.

Usage:
  python3 tools/independence_axis_check.py
  python3 tools/independence_axis_check.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402


def _hyp_pmf(a: int, r1: int, c1: int, n: int) -> float:
    return math.comb(r1, a) * math.comb(n - r1, c1 - a) / math.comb(n, c1)


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the table [[a, b], [c, d]]."""
    n = a + b + c + d
    r1 = a + b
    c1 = a + c
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    p_obs = _hyp_pmf(a, r1, c1, n)
    total = 0.0
    for x in range(lo, hi + 1):
        p = _hyp_pmf(x, r1, c1, n)
        if p <= p_obs * (1 + 1e-9):
            total += p
    return min(1.0, total)


def compute(root: Path = ROOT) -> dict:
    specs = {
        "hypotheses": (root / "state" / "hypotheses.jsonl", "hypothesis_id"),
        "evaluations": (root / "state" / "evaluations.jsonl", "evaluation_id"),
    }
    cols, errors = ledger_io.load_collections(specs, root=root)
    hyps = cols["hypotheses"]
    evals = list(cols["evaluations"].values())
    table: dict[str, Counter] = {"same": Counter(), "cross": Counter()}
    for ev in evals:
        h = hyps.get(ev.get("target_hypothesis_id"))
        if not h:
            continue
        kind = "same" if h.get("session_id") == ev.get("session_id") else "cross"
        table[kind][ev.get("verdict", "")] += 1
    s_sup = table["same"]["supports"]
    s_non = sum(table["same"].values()) - s_sup
    c_sup = table["cross"]["supports"]
    c_non = sum(table["cross"].values()) - c_sup
    crit_same = table["same"]["narrows_scope"] + table["same"]["refutes_unconditioned"]
    crit_cross = table["cross"]["narrows_scope"] + table["cross"]["refutes_unconditioned"]
    n_same = sum(table["same"].values())
    n_cross = sum(table["cross"].values())
    return {
        "evaluations_counted": n_same + n_cross,
        "load_errors": len(errors),
        "same": dict(table["same"]),
        "cross": dict(table["cross"]),
        "supports_share": {
            "same": round(s_sup / n_same, 4) if n_same else None,
            "cross": round(c_sup / n_cross, 4) if n_cross else None,
        },
        "critical_share_narrow_or_refute": {
            "same": round(crit_same / n_same, 4) if n_same else None,
            "cross": round(crit_cross / n_cross, 4) if n_cross else None,
            "same_n": n_same,
            "cross_n": n_cross,
        },
        "fisher_two_sided_p_supports": fisher_two_sided(s_sup, s_non, c_sup, c_non),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = compute()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
