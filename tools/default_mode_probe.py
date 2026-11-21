#!/usr/bin/env python3
"""Default-mode probe (Layer 5: Common Network / DMN-like simulation).

Advisory tool that, without adding new materials or hypotheses, simulates
what would happen if the next session addressed the highest-EIG hypothesis
pair. Following Spreng, Mar & Kim (2009): the default mode network is
active during internally directed cognition (remembering the past,
imagining the future, theory of mind, spatial navigation) — the archive's
analogue is simulating the consequences of its own next steps without
actually committing them.

Currently this tool reports potential consequences; it does NOT write
any rows (simulations are not evaluations). Output can feed into
SELF_MODEL.md §6 (prediction error) in future iterations.

Usage:
    python3 tools/default_mode_probe.py          # print simulation
    python3 tools/default_mode_probe.py --json   # JSON output
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import ledger_io

ROOT = Path(__file__).resolve().parents[1]


def find_top_eig_pair(bm_text: str) -> tuple[str, str, float] | None:
    """Parse the highest-EIG pair from BELIEF_MAP.md (first Q-001 entry)."""
    import re
    # The EIG pair appears on the same line as "最優先検証ターゲット", in format:
    # `HYP-xxx`（description） vs `HYP-yyy`（description）
    for line in bm_text.splitlines():
        if "最優先検証ターゲット" in line and "Q-001" not in line:
            # Found first occurrence (which is Q-001)
            m = re.search(r"`(HYP-[0-9a-f-]+)`[^`]*vs `(HYP-[0-9a-f-]+)`", line)
            if m:
                return (m.group(1), m.group(2), 0.0)
    return None


def run_probe(as_json: bool = False, root: Path = ROOT) -> int:
    bm = (root / "BELIEF_MAP.md").read_text(encoding="utf-8")
    pair = find_top_eig_pair(bm)
    result: dict = {}
    if pair is None:
        result = {"status": "no_eig_pair_found", "simulation": None}
    else:
        h1, h2, _ = pair
        # Load hypothesis titles
        base = root / "state" / "hypotheses.jsonl"
        hyps_coll, _ = ledger_io.load_collections({"hypotheses": (base, "hypothesis_id")}, root=root)
        h1_title = ""
        h2_title = ""
        for h in hyps_coll.get("hypotheses", {}).values():
            if h.get("hypothesis_id") == h1:
                h1_title = h.get("title", "")
            if h.get("hypothesis_id") == h2:
                h2_title = h.get("title", "")
        result = {
            "status": "ok",
            "next_highest_eig_pair": {
                "left": h1, "left_title": h1_title,
                "right": h2, "right_title": h2_title,
            },
            "simulation_note": (
                "If the next session directly tests this pair by reading one "
                "or more materials relevant to the opposition, the expected "
                "outcome is either: (a) one hypothesis gains mass at the "
                "expense of the other, narrowing their joint scope; (b) a "
                "synthesis is proposed, creating a child hypothesis with "
                "lineage_op=synthesizes; (c) a contradiction is found in the "
                "current framing, requiring a splits child. This is a "
                "simulation only; no evaluation is created."
            ),
        }

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("=== Default Mode Probe (simulation, no writes) ===")
    print()
    if result["status"] == "no_eig_pair_found":
        print("No high-EIG pair found in BELIEF_MAP.md.")
        return 0
    pair = result["next_highest_eig_pair"]
    print(f"Next highest-EIG pair to test:")
    print(f"  (A) {pair['left']}: {pair['left_title']}")
    print(f"  (B) {pair['right']}: {pair['right_title']}")
    print()
    print(f"Simulation: {result['simulation_note']}")
    print()
    print("(This is a structural thought experiment in default mode. No rows are written.)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    return run_probe(as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
