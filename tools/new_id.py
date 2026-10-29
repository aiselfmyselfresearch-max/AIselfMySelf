#!/usr/bin/env python3
"""Mint collision-resistant record IDs for parallel inquiry sessions.

Sequential IDs (``FRAG-013``) assume a single writer: two sessions that read the
same ledger both compute ``FRAG-013`` and produce a duplicate after merging.  This
tool mints ``PREFIX-YYYYMMDD-xxxxxx`` IDs instead (six random hex characters by
default), checks the candidate against the union of the frozen base file and all
``state/<collection>.d/*.jsonl`` shards, and prints one ID per line.

Typical use::

    python3 tools/new_id.py FRAG
    python3 tools/new_id.py Q --count 3

The ID format is not sequential, so do not sort records by ID to infer
chronology; append-only file order and ``created_at`` carry that information.
Standard library only.  See ``docs/parallel-work.md``.
"""
from __future__ import annotations

import argparse
import re
import secrets
import sys
from datetime import date
from pathlib import Path
from typing import Iterable

import ledger_io
from validate_seed import ROOT

# prefix -> (ledger file name, ID field)
PREFIXES: dict[str, tuple[str, str]] = {
    "Q": ("questions.jsonl", "question_id"),
    "MOTIF": ("motifs.jsonl", "motif_id"),
    "MAT": ("materials.jsonl", "material_id"),
    "MAT-LIT": ("materials.jsonl", "material_id"),
    "FRAG": ("fragments.jsonl", "fragment_id"),
    "REL": ("relations.jsonl", "relation_id"),
    "SESSION": ("sessions.jsonl", "session_id"),
    "READ": ("read_log.jsonl", "read_id"),
    "ED": ("editorial_decisions.jsonl", "decision_id"),
    "ERR": ("errata.jsonl", "errata_id"),
}

_ID_SUFFIX = re.compile(r"^[0-9a-f]+$")


def existing_ids(prefix: str, root: Path = ROOT) -> set[str]:
    """Return every ID already present in the collection's base file and shards."""
    prefix = prefix.upper()
    if prefix not in PREFIXES:
        raise ValueError(f"unknown prefix {prefix!r}; expected one of {sorted(PREFIXES)}")
    filename, id_key = PREFIXES[prefix]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(
        Path(root) / "state" / filename, id_key, errors, root=Path(root)
    )
    if errors:
        raise ValueError("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return set(records)


def mint(
    prefix: str,
    *,
    day: str | None = None,
    taken: Iterable[str] = (),
    hex_bytes: int = 3,
) -> str:
    """Return one unused ``PREFIX-YYYYMMDD-<hex>`` ID."""
    prefix = prefix.upper()
    if prefix not in PREFIXES:
        raise ValueError(f"unknown prefix {prefix!r}; expected one of {sorted(PREFIXES)}")
    if not 1 <= hex_bytes <= 16:
        raise ValueError("hex_bytes must be between 1 and 16")
    stamp = day or date.today().strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", stamp):
        raise ValueError(f"day must be YYYYMMDD, got {stamp!r}")
    seen = set(taken)
    for _ in range(1000):
        candidate = f"{prefix}-{stamp}-{secrets.token_hex(hex_bytes)}"
        if candidate not in seen:
            return candidate
    raise RuntimeError("could not mint a unique ID; check the ledger for corruption")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mint a ledger record ID")
    parser.add_argument("prefix", choices=sorted(PREFIXES), help="record prefix")
    parser.add_argument("--count", type=int, default=1, help="how many IDs to mint (default 1)")
    parser.add_argument("--date", default=None, help="YYYYMMDD stamp (default: today)")
    parser.add_argument(
        "--hex-bytes",
        type=int,
        default=3,
        help="random bytes in the suffix (default 3 = 6 hex characters)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root containing state/ (default: this checkout)",
    )
    args = parser.parse_args(argv)

    if args.count < 1:
        parser.error("--count must be at least 1")

    try:
        taken = existing_ids(args.prefix, args.root)
        minted: list[str] = []
        for _ in range(args.count):
            value = mint(
                args.prefix,
                day=args.date,
                taken=taken,
                hex_bytes=args.hex_bytes,
            )
            minted.append(value)
            taken.add(value)
    except (ValueError, RuntimeError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for value in minted:
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
