#!/usr/bin/env python3
"""Create a per-session ledger shard: state/<collection>.d/<date>-<hex>.jsonl.

Parallel sessions must not append to the shared ``state/<collection>.jsonl``
base files: concurrent appends to one file create Git text conflicts and can
interleave bytes.  Each session instead works in its own shard, which every tool
reads as part of the union (``tools/ledger_io.py``).

Usage::

    python3 tools/new_ledger_shard.py fragments --create
    python3 tools/new_ledger_shard.py questions
    python3 tools/new_ledger_shard.py --list fragments

Without ``--create`` the tool only prints the path it would use.  Names follow
``YYYY-MM-DD-<12 hex>.jsonl`` so that sorting shard names approximates the order
in which sessions started.  Standard library only.  See ``docs/parallel-work.md``.
"""
from __future__ import annotations

import argparse
import os
import re
import secrets
import sys
from datetime import date
from pathlib import Path

import ledger_io
from validate_seed import COLLECTIONS, ROOT

# Errata are audited separately from the seed ledgers, but use the same
# append-only base-plus-shard layout and therefore need shard support here.
SHARD_COLLECTIONS = {
    **COLLECTIONS,
    "errata": ("errata.jsonl", "errata_id", "errata.schema.json"),
}

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SUFFIX = re.compile(r"^[0-9a-f]{12}$")


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
    token = suffix or secrets.token_hex(6)
    if not _SUFFIX.fullmatch(token):
        raise ValueError(f"suffix must be 12 lowercase hex characters, got {token!r}")
    return ledger_io.shard_dir(base) / f"{stamp}-{token}.jsonl"


def create_shard(
    collection: str,
    *,
    root: Path = ROOT,
    day: str | None = None,
    suffix: str | None = None,
) -> Path:
    """Create an empty shard with O_EXCL and return its path."""
    base = collection_base(collection, root)
    if not base.is_file():
        raise FileNotFoundError(f"base ledger is missing: {base}")
    path = shard_path(collection, root=root, day=day, suffix=suffix)
    # Serialise with --write-map / import_researchos --write, which hold the
    # same writer lock while they regenerate a base file.
    with ledger_io.exclusive_lock(base):
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        os.close(descriptor)
    return path


def list_shards(collection: str, root: Path = ROOT) -> list[Path]:
    return ledger_io.collection_files(collection_base(collection, root))[1:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", nargs="?", choices=sorted(SHARD_COLLECTIONS), help="ledger name")
    parser.add_argument("--create", action="store_true", help="create the shard file")
    parser.add_argument("--list", action="store_true", help="list existing shards")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD stamp (default: today)")
    parser.add_argument("--suffix", default=None, help="12 lowercase hex characters")
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
