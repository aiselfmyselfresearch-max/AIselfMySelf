#!/usr/bin/env python3
"""Get the ledger shard to append to: state/<collection>.d/<date>-<12 hex>.jsonl.

Background (2026-11-21, ERR-20261121-8d2b41)
--------------------------------------------
The ledger base files ``state/<collection>.jsonl`` are frozen: sessions append
to shards, and every tool reads the base-plus-shards union
(``tools/ledger_io.py``).  Until today each *call* minted a new file
``YYYY-MM-DD-<random hex>.jsonl``, so shard count grew with every session and
``tools/size_budget.py`` hard limits were reached and cleared again by manual
consolidation -- delay, not a fix (the history is in ``docs/parallel-work.md``).

The default is now the **day shard**: one canonical file per collection per
day, ``<date>-000000000000.jsonl`` (the zero suffix that consolidation already
used as its anchor).  ``create_shard()`` creates it once and later calls return
the same path to append to.  Sessions on the same day share the file, which is
what consolidation was doing after the fact, without moving any bytes.

Concurrency: appends within one checkout are serialised by
``ledger_io.exclusive_lock``.  Two *branches* appending to the same day shard
can produce a Git conflict at merge; the resolution is to keep both sides'
lines (rows are append-only and id-keyed, so the union is the correct
content), then re-run ``tools/validate_seed.py`` and
``tools/append_only_check.py``.  A session that is racing another open branch
can ask for a **dedicated** shard instead by passing ``--suffix``: that keeps
the old one-call-one-file behaviour, including the refusal to create the same
shard twice.

Usage::

    python3 tools/new_ledger_shard.py fragments --create      # the day shard
    python3 tools/new_ledger_shard.py questions               # print the path
    python3 tools/new_ledger_shard.py fragments --create --suffix abcdefabcdef
    python3 tools/new_ledger_shard.py --list fragments

Without ``--create`` the tool only prints the path it would use.  Standard
library only.  See ``docs/parallel-work.md``.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

import ledger_io
from validate_seed import COLLECTIONS, ROOT

import date_axis

# Errata are audited separately from the seed ledgers, but use the same
# append-only base-plus-shard layout and therefore need shard support here.
SHARD_COLLECTIONS = {
    **COLLECTIONS,
    "errata": ("errata.jsonl", "errata_id", "errata.schema.json"),
}

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SUFFIX = re.compile(r"^[0-9a-f]{12}$")

#: The canonical per-day shard suffix.  Consolidation anchored on this name
#: (state/shard_aliases.json); it is now the default append target.
DAY_SHARD_SUFFIX = "000000000000"


def collection_base(collection: str, root: Path = ROOT) -> Path:
    if collection not in SHARD_COLLECTIONS:
        raise ValueError(
            f"unknown collection {collection!r}; expected one of {sorted(SHARD_COLLECTIONS)}"
        )
    filename = SHARD_COLLECTIONS[collection][0]
    return Path(root) / "state" / filename


def shard_path(
    collection: str,
    *,
    root: Path = ROOT,
    day: str | None = None,
    suffix: str | None = None,
) -> Path:
    """Return the shard path for ``collection`` (does not create it)."""
    base = collection_base(collection, root)
    stamp = day or date.today().isoformat()
    if not _DATE.fullmatch(stamp):
        raise ValueError(f"day must be YYYY-MM-DD, got {stamp!r}")
    try:
        date.fromisoformat(stamp)
    except ValueError as exc:
        raise ValueError(f"day must be a real calendar date, got {stamp!r}") from exc
    # A shard name is a date on the one axis (tools/date_axis.py): parallel
    # sessions used to name shards with internal-chronology labels, which sort
    # after later real dates. New shards carry the real date only.
    date_axis.assert_writable_day(stamp)
    if suffix is not None and not _SUFFIX.fullmatch(suffix):
        raise ValueError(f"suffix must be 12 lowercase hex characters, got {suffix!r}")
    token = suffix or DAY_SHARD_SUFFIX
    return ledger_io.shard_dir(base) / f"{stamp}-{token}.jsonl"


def create_shard(
    collection: str,
    *,
    root: Path = ROOT,
    day: str | None = None,
    suffix: str | None = None,
) -> Path:
    """Return the shard to append to.

    Without ``suffix`` this is the day shard: created once, reused afterwards.
    With ``suffix`` this is a dedicated shard: created with O_EXCL and refused
    if it already exists, which is the pre-2026-11-21 behaviour kept for
    sessions that need isolation from other branches.
    """
    base = collection_base(collection, root)
    if not base.is_file():
        raise FileNotFoundError(f"base ledger is missing: {base}")
    dedicated = suffix is not None
    path = shard_path(collection, root=root, day=day, suffix=suffix)
    # Serialise with --write-map / import_researchos --write, which hold the
    # same writer lock while they regenerate a base file.
    with ledger_io.exclusive_lock(base):
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.close(descriptor)
        except FileExistsError:
            if dedicated:
                raise
            # The day shard exists: it is the shared append target.
            return path
    return path


def list_shards(collection: str, root: Path = ROOT) -> list[Path]:
    return ledger_io.collection_files(collection_base(collection, root))[1:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", nargs="?", choices=sorted(SHARD_COLLECTIONS), help="ledger name")
    parser.add_argument("--create", action="store_true", help="create the shard file")
    parser.add_argument("--list", action="store_true", help="list existing shards")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD stamp (default: today)")
    parser.add_argument(
        "--suffix",
        default=None,
        help="12 lowercase hex characters: request a dedicated shard instead of the shared day shard",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root containing state/ (default: this checkout)",
    )
    args = parser.parse_args(argv)

    if not args.collection:
        parser.error("a collection name is required")
    if args.create and args.list:
        parser.error("--create and --list are mutually exclusive")

    try:
        if args.list:
            for path in list_shards(args.collection, args.root):
                print(ledger_io.display_path(path, args.root))
            return 0
        if args.create:
            path = create_shard(
                args.collection,
                root=args.root,
                day=args.date,
                suffix=args.suffix,
            )
        else:
            path = shard_path(
                args.collection,
                root=args.root,
                day=args.date,
                suffix=args.suffix,
            )
    except FileExistsError as exc:
        print(f"error: {exc.filename} already exists; choose another shard", file=sys.stderr)
        return 1
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(ledger_io.display_path(path, args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
