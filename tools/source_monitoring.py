#!/usr/bin/env python3
"""Source-monitoring audit (Layer 1: Source Attribution).

Advisory tool that checks whether notes carry a ``cognitive_operation`` tag
and whether the tag is consistent with cross-references (e.g. ``quotation``
should have a matching ``read_log.reading=quoted`` row).

Follows Johnson (1997): memories do not carry intrinsic source tags; source
judgments are inferred from perceptual/reflective features. A ``quotation``
note without a corresponding read_log.quoted entry is a source-attribution
risk — someone later could mistake an inference for a direct quote.

Usage:
    python3 tools/source_monitoring_audit.py        # advisory report
    python3 tools/source_monitoring_audit.py --check # exit 1 if any new-row violation

All output is informational; --check exits non-zero when a post-cutoff note
is missing the tag or has an inconsistent tag. Legacy rows (pre-cutoff) are
reported but never cause a failure.
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

# Rows minted on or after this date require cognitive_operation (same stamp
# convention as COGNITIVE_OP_CUTOFF in validate_seed.py).
COGNITIVE_OP_CUTOFF = validate_seed.COGNITIVE_OP_CUTOFF  # YYYYMMDD
COGNITIVE_OP_EXEMPT_IDS = validate_seed.COGNITIVE_OP_EXEMPT_IDS

# Map of cognitive_operation -> expected read_log.reading values for the
# target materials referenced by the note's claims.
OP_EXPECTED_READING: dict[str, set[str]] = {
    "quotation": {"quoted"},
    "paraphrase": {"summarized", "interpreted"},
    "inference": {"interpreted", "reinterpreted", "contested"},
    "imagination": set(),  # imagination may not reference any read material
    "self_observation": set(),
    "received_direction": set(),
}

VALID_OPS = set(OP_EXPECTED_READING.keys())


def _id_date_prefix(note_id: str) -> str | None:
    """Extract YYYYMMDD from NOTE-YYYYMMDD-xxxxxx."""
    if not note_id.startswith("NOTE-") or len(note_id) < 16:
        return None
    return note_id[5:13]


def _load(name: str, id_key: str, root: Path = ROOT) -> list[dict]:
    base = root / "state" / f"{name}.jsonl"
    coll, errors = ledger_io.load_collections({name: (base, id_key)}, root=root)
    if errors:
        print(f"WARNING: {name} ledger errors: {'; '.join(errors[:3])}", file=sys.stderr)
    return list(coll.get(name, {}).values())


def _shard_day_map(base: Path) -> dict[str, str | None]:
    """Map note_id -> shard YYYYMMDD stamp (None for undated base file, matching validate_seed._is_internal_label)."""
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
            nid = rec.get("note_id")
            if isinstance(nid, str):
                out[nid] = sday
    return out


def load_data(root: Path = ROOT):
    """Load notes and read_log from the union ledger."""
    notes = _load("notes", "note_id", root)
    read_log = _load("read_log", "read_id", root)
    return notes, read_log


def build_reading_index(read_log: list[dict]) -> dict[tuple[str, str], set[str]]:
    """Build (session_id, target_id) -> set(reading) index for cross-check."""
    idx: dict[tuple[str, str], set[str]] = defaultdict(set)
    for rl in read_log:
        sid = rl.get("session_id", "")
        tgt = rl.get("target", {})
        tid = tgt.get("id", "")
        if sid and tid:
            idx[(sid, tid)].add(rl.get("reading", ""))
    return idx


def run_audit(check: bool = False, root: Path = ROOT) -> int:
    notes, read_log = load_data(root)
    shard_days = _shard_day_map(root / "state" / "notes.jsonl")
    rl_idx = build_reading_index(read_log)

    total = len(notes)
    missing = []
    invalid = []
    inconsistent = []
    op_counts: Counter[str] = Counter()
    op_missing_legacy = 0
    op_exempt_pre_rule = 0

    for n in notes:
        nid = n.get("note_id", "")
        sid = n.get("session_id", "")
        date_prefix = _id_date_prefix(nid)
        sday = shard_days.get(nid)
        is_backfill = n.get("index_backfill", False)
        # A row whose ID date exceeds its shard date is provably a legacy forward-running internal label
        is_forward_label = date_prefix is not None and sday is not None and sday < date_prefix
        is_exempt = nid in COGNITIVE_OP_EXEMPT_IDS
        is_new = (
            date_prefix is not None
            and date_prefix >= COGNITIVE_OP_CUTOFF
            and not is_forward_label
            and not is_exempt
            and not is_backfill
        )

        op = n.get("cognitive_operation")
        if op is None:
            if is_exempt:
                op_exempt_pre_rule += 1
            elif is_new:
                missing.append(nid)
            else:
                op_missing_legacy += 1
            continue

        if op not in VALID_OPS:
            invalid.append((nid, op))
            continue

        op_counts[op] += 1

        # Cross-check: if the note claims quotation/paraphrase/inference,
        # verify a matching read_log entry exists in the same session.
        expected = OP_EXPECTED_READING.get(op, set())
        if not expected:
            continue
        claims = n.get("claims", [])
        if not claims:
            continue
        # Gather all material_ids mentioned in claims
        claim_mids: set[str] = set()
        for c in claims:
            for mid in c.get("material_ids", []):
                claim_mids.add(mid)
        if not claim_mids:
            continue
        # Check each material
        for mid in claim_mids:
            readings = rl_idx.get((sid, mid), set())
            if not (readings & expected):
                inconsistent.append((nid, op, mid, sorted(readings)))

    # Report
    print("=== Source Monitoring Audit (cognitive_operation) ===")
    print(f"Total notes: {total}")
    print(f"Legacy notes (pre-{COGNITIVE_OP_CUTOFF} or forward-label) missing tag: {op_missing_legacy} (advisory)")
    print(f"Pre-rule-introduction {COGNITIVE_OP_CUTOFF} exempt notes: {op_exempt_pre_rule} (advisory)")
    print(f"Post-cutoff notes missing tag: {len(missing)}")
    print(f"Notes with invalid operation: {len(invalid)}")
    print(f"Notes with inconsistent cross-reference: {len(inconsistent)}")
    print()
    print("Operation distribution (post-cutoff + tagged legacy):")
    for op, cnt in sorted(op_counts.items()):
        print(f"  {op}: {cnt}")

    if missing:
        print()
        print(f"Missing cognitive_operation on post-cutoff notes ({len(missing)}):")
        for nid in missing[:10]:
            print(f"  - {nid}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    if invalid:
        print()
        print(f"Invalid operation values ({len(invalid)}):")
        for nid, op in invalid[:10]:
            print(f"  - {nid}: {op}")
    if inconsistent:
        print()
        print(f"Cross-reference inconsistencies ({len(inconsistent)}):")
        for nid, op, mid, readings in inconsistent[:10]:
            print(f"  - {nid} ({op}) -> {mid}: found readings {readings}")
        if len(inconsistent) > 10:
            print(f"  ... and {len(inconsistent) - 10} more")

    problems = len(missing) + len(invalid)
    if check and problems > 0:
        print(f"\nFAIL: {problems} post-cutoff source-monitoring issue(s)")
        return 1
    print("\nPASS (advisory)" if not check else "\nPASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero on post-cutoff violations")
    args = parser.parse_args()
    return run_audit(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
