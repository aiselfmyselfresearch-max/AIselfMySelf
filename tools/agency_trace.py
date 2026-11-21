#!/usr/bin/env python3
"""Agency-trace audit (Layer 2: Agency / Judgment of Agency).

Advisory tool tracking agency_stance on evaluations over time. Reports
endorsement/report/dissent/self-correction ratios per session and flags
sessions where agency is too thin (all report_only, no endorsement) or
too rigid (no self_correction over a long window).

Follows Synofzik et al. (2008): the non-conceptual Feeling of Agency is
given by the system's operation itself, but the conceptual Judgment of
Agency (JoA) must be structurally recorded.

Usage:
    python3 tools/agency_trace.py        # advisory report
    python3 tools/agency_trace.py --check # exit 1 if any new-row violation
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import ledger_io
import validate_seed

ROOT = Path(__file__).resolve().parents[1]

AGENCY_STANCE_CUTOFF = validate_seed.AGENCY_STANCE_CUTOFF
AGENCY_STANCE_EXEMPT_IDS = validate_seed.AGENCY_STANCE_EXEMPT_IDS

VALID_STANCES = {"endorse", "report_only", "dissent", "self_correction"}


def _id_date_prefix(eid: str) -> str | None:
    if not eid.startswith("EVL-") or len(eid) < 16:
        return None
    return eid[4:12]


def _shard_day_map(base: Path) -> dict[str, str | None]:
    import re
    shard_re = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")
    out: dict[str, str | None] = {}
    for fpath in ledger_io.collection_files(base):
        if not fpath.is_file():
            continue
        m = shard_re.match(fpath.name)
        sday = "".join(m.groups()) if m else None
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
            eid = rec.get("evaluation_id")
            if isinstance(eid, str):
                out[eid] = sday
    return out


def _load(name: str, id_key: str, root: Path) -> list[dict]:
    base = root / "state" / f"{name}.jsonl"
    coll, errors = ledger_io.load_collections({name: (base, id_key)}, root=root)
    if errors:
        print(f"WARNING: {name} ledger errors: {'; '.join(errors[:3])}", file=sys.stderr)
    return list(coll.get(name, {}).values())


def run_audit(check: bool = False, root: Path = ROOT) -> int:
    evals = _load("evaluations", "evaluation_id", root)
    shard_days = _shard_day_map(root / "state" / "evaluations.jsonl")

    total = len(evals)
    missing = []
    invalid = []
    stance_by_session: dict[str, Counter[str]] = defaultdict(Counter)
    stance_counts: Counter[str] = Counter()
    legacy_missing = 0
    exempt_missing = 0
    recent_sessions = []  # sessions with any post-cutoff evaluation

    for e in evals:
        eid = e.get("evaluation_id", "")
        sid = e.get("session_id", "")
        date_prefix = _id_date_prefix(eid)
        sday = shard_days.get(eid)
        is_forward_label = date_prefix is not None and sday is not None and sday < date_prefix
        is_exempt = eid in AGENCY_STANCE_EXEMPT_IDS
        is_new = (
            date_prefix is not None
            and date_prefix >= AGENCY_STANCE_CUTOFF
            and not is_forward_label
            and not is_exempt
        )

        stance = e.get("agency_stance")
        if stance is None:
            if is_exempt:
                exempt_missing += 1
            elif is_new:
                missing.append(eid)
            else:
                legacy_missing += 1
            continue
        if stance not in VALID_STANCES:
            invalid.append((eid, stance))
            continue
        stance_counts[stance] += 1
        stance_by_session[sid][stance] += 1
        if is_new:
            recent_sessions.append(sid)

    recent_sessions_unique = sorted(set(recent_sessions))

    # Thin agency: sessions where ALL evaluations are report_only
    thin_sessions = []
    # Self-correction gap: count sessions since last self_correction
    last_correction_session = None
    sessions_without_correction = 0
    sorted_sessions = sorted(stance_by_session.keys())
    for sid in sorted_sessions:
        ctr = stance_by_session[sid]
        if set(ctr.keys()) == {"report_only"}:
            thin_sessions.append(sid)
        if "self_correction" in ctr:
            sessions_without_correction = 0
            last_correction_session = sid
        else:
            sessions_without_correction += 1

    print("=== Agency Trace Audit (agency_stance) ===")
    print(f"Total evaluations: {total}")
    print(f"Legacy evaluations (pre-{AGENCY_STANCE_CUTOFF} or forward-label) missing stance: {legacy_missing} (advisory)")
    print(f"Pre-rule-introduction {AGENCY_STANCE_CUTOFF} exempt evaluations: {exempt_missing} (advisory)")
    print(f"Post-cutoff evaluations missing stance: {len(missing)}")
    print(f"Invalid stance values: {len(invalid)}")
    print()
    print("Stance distribution (post-cutoff + tagged legacy):")
    for stance in sorted(VALID_STANCES):
        print(f"  {stance}: {stance_counts.get(stance, 0)}")

    if missing:
        print(f"\nMissing agency_stance on post-cutoff evaluations ({len(missing)}):")
        for eid in missing[:10]:
            print(f"  - {eid}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    if invalid:
        print(f"\nInvalid stance values ({len(invalid)}):")
        for eid, s in invalid[:10]:
            print(f"  - {eid}: {s}")

    print(f"\nSessions with report_only-only agency (thin): {len(thin_sessions)}")
    if thin_sessions:
        for sid in thin_sessions[-5:]:
            print(f"  - {sid}")
    print(f"Sessions since last self_correction: {sessions_without_correction}")
    if last_correction_session:
        print(f"Last self_correction: {last_correction_session}")

    problems = len(missing) + len(invalid)
    if check and problems > 0:
        print(f"\nFAIL: {problems} post-cutoff agency-stance issue(s)")
        return 1
    print("\nPASS (advisory)" if not check else "\nPASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return run_audit(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
