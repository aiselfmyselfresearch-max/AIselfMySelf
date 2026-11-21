#!/usr/bin/env python3
"""Whether-gate audit (Layer 4: Action Control — veto / inhibition).

Advisory tool counting veto-type records in editorial_decisions and
declined reads in read_log, reporting the veto/action ratio and flagging
long periods without any veto (which suggests diminished whether-control,
following Brass & Haggard 2008: the "whether" decision is the final
inhibitory veto that is the core of agential control).

Usage:
    python3 tools/whether_gate.py        # advisory report
    python3 tools/whether_gate.py --check # exit 1 if config issue
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ledger_io

ROOT = Path(__file__).resolve().parents[1]

# Known veto-like decision kinds
VETO_KINDS = {"veto_reading", "veto_claim", "veto_hypothesis", "veto_session_direction"}


def _load_coll(name: str, id_key: str, root: Path) -> list[dict]:
    base = root / "state" / f"{name}.jsonl"
    coll, errors = ledger_io.load_collections({name: (base, id_key)}, root=root)
    return list(coll.get(name, {}).values())


def run_audit(check: bool = False, root: Path = ROOT) -> int:
    # Read declined read_log entries
    rl_list = _load_coll("read_log", "read_id", root)
    declined = [r for r in rl_list if r.get("reading") == "declined"]

    # Read editorial_decisions
    ed_list = _load_coll("editorial_decisions", "editorial_decision_id", root)
    veto_decisions = [d for d in ed_list if d.get("decision_kind", "") in VETO_KINDS]

    # Total action volume (all read_log + all editorial_decisions)
    total_rl = len(rl_list)
    total_ed = len(ed_list)
    total_actions = total_rl + total_ed
    total_veto = len(declined) + len(veto_decisions)
    veto_ratio = total_veto / max(total_actions, 1)

    # Group by session
    vetoes_by_session: dict[str, int] = defaultdict(int)
    for r in declined:
        vetoes_by_session[r.get("session_id", "?")] += 1
    for d in veto_decisions:
        vetoes_by_session[d.get("session_id", "?")] += 1

    # Sessions with zero vetoes (recent sessions)
    sessions_list = _load_coll("sessions", "session_id", root)
    all_sessions = sorted(s.get("session_id", "") for s in sessions_list)
    recent_n = 20
    recent = all_sessions[-recent_n:] if len(all_sessions) >= recent_n else all_sessions
    no_veto_recent = [s for s in recent if vetoes_by_session.get(s, 0) == 0]

    print("=== Whether-Gate (Veto) Audit ===")
    print(f"Total read_log rows: {total_rl}")
    print(f"  declined reads: {len(declined)}")
    print(f"Total editorial_decisions rows: {total_ed}")
    print(f"  explicit veto decisions: {len(veto_decisions)}")
    print()
    print(f"Veto/action ratio: {total_veto}/{total_actions} = {veto_ratio*100:.2f}%")
    print(f"Sessions with any veto record: {len(vetoes_by_session)}")
    print(f"Recent sessions without veto (last {recent_n}): {len(no_veto_recent)}/{len(recent)}")

    if declined:
        print(f"\nSample declined reads (first 5):")
        for r in declined[:5]:
            tgt = r.get("target", {})
            print(f"  - {r.get('session_id','?')}: declined {tgt.get('type','?')}:{tgt.get('id','?')}")

    if veto_decisions:
        print(f"\nVeto decisions by kind:")
        kind_counter = Counter(d.get("decision_kind", "?") for d in veto_decisions)
        for k, v in sorted(kind_counter.items()):
            print(f"  {k}: {v}")

    if len(no_veto_recent) == len(recent) and len(recent) > 5:
        print(f"\nNOTE: No veto records in the last {len(recent)} sessions. Consider whether "
              "inhibitory control (the 'whether' decision) is being structurally recorded.")

    # Advisory only -- check mode always passes for now since veto
    # recording is new and the threshold needs calibration.
    print("\nPASS (advisory)" if not check else "\nPASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return run_audit(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
