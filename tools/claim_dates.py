#!/usr/bin/env python3
"""List ``measured_fact`` claims that state a number without saying *when*.

Why this tool exists
--------------------
A count written into a claim ("relations: 6,111") describes the ledger at the
moment it was measured.  Nothing in ``note.schema.json`` records that moment, and
claims are written in the present tense, so a later reader -- including a later
session of the same archive -- cannot tell a current fact from a stale one.  On
2026-11-11 five sampled claims of this kind were re-measured and all five had
moved (``readings/2026-11-11-numbers-carry-no-date.md``).

The operation chosen then was prose, not schema: whenever a claim states a
number, write the date in the claim text.  The next two rounds did not follow it
(13 of 15 numbered claims had no date;
``readings/2026-11-11-the-rule-did-not-reach-the-next-round.md``).  This tool is
the check that prose could not provide.  It reports; it never edits.

What counts as a date
---------------------
An ISO date (``2026-11-11``), a Japanese year (``2026年``), the words 時点 /
現在の, or a ledger ID that carries its own date stamp (``SESSION-20261110-…``,
``READ-20261031-…``, ``MAT-LIT-20261024-…``).  Anything else is reported.  The
detector is a regex, so the reported rate is an upper bound: relative wording
(「先月」「前回」) is not recognised.

Usage::

    python3 tools/claim_dates.py               # summary
    python3 tools/claim_dates.py --list        # every undated claim
    python3 tools/claim_dates.py --since 2026-11-13   # only newer notes
    python3 tools/claim_dates.py --strict      # exit 1 if any are found

Standard library only.  See ``state/notes.d/`` and ``schema/note.schema.json``.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

DATE_PATTERN = re.compile(
    r"20\d\d-\d\d-\d\d"      # ISO date
    r"|20\d\d年"             # Japanese year
    r"|時点|現在の"           # explicit as-of wording
)
DATED_ID_PATTERN = re.compile(
    r"(?:SESSION|READ|NOTE|NOTE-TMP|ERR|ED|REL|MAT|MAT-LIT|MAT-EVD|MAT-TRC|MAT-ARC|FRAG)"
    r"-20\d{6}"
)
DIGIT_PATTERN = re.compile(r"[0-9]")


def load_notes(root: Path = ROOT) -> list[dict[str, Any]]:
    collections, errors = ledger_io.load_collections(
        {"notes": (root / "state" / "notes.jsonl", "note_id")},
        root=root,
    )
    if errors:
        for problem in errors:
            print(f"ledger error: {problem}", file=sys.stderr)
    return list(collections.get("notes", {}).values())


def undated_claims(
    notes: list[dict[str, Any]], *, since: str | None = None
) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, int]]:
    counts = {"notes": 0, "claims": 0, "measured": 0, "numbered": 0, "undated": 0}
    undated: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for note in notes:
        if since and str(note.get("created_at") or "") < since:
            continue
        counts["notes"] += 1
        for claim in note.get("claims") or []:
            counts["claims"] += 1
            if claim.get("kind") != "measured_fact":
                continue
            counts["measured"] += 1
            text = str(claim.get("text") or "")
            if not DIGIT_PATTERN.search(text):
                continue
            counts["numbered"] += 1
            if DATE_PATTERN.search(text) or DATED_ID_PATTERN.search(text):
                continue
            counts["undated"] += 1
            undated.append((note, claim))
    return undated, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="print every undated claim")
    parser.add_argument("--since", default=None, help="only notes created on/after this date")
    parser.add_argument("--limit", type=int, default=20, help="lines shown with --list")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any are found")
    args = parser.parse_args(argv)

    notes = load_notes()
    undated, counts = undated_claims(notes, since=args.since)

    scope = "all notes" if not args.since else f"notes created on/after {args.since}"
    print(f"checked: {scope}")
    print(f"  notes             : {counts['notes']}")
    print(f"  claims            : {counts['claims']}")
    print(f"  measured_fact     : {counts['measured']}")
    print(f"  ... with a digit  : {counts['numbered']}")
    print(f"  ... without a date: {counts['undated']}")
    if counts["numbered"]:
        share = 100.0 * counts["undated"] / counts["numbered"]
        print(f"  undated share     : {share:.1f}%")
    print("  (dates are detected by regex, so the undated share is an upper bound)")

    if args.list and undated:
        print("")
        for note, claim in undated[: args.limit]:
            text = str(claim.get("text") or "").replace("\n", " ")
            cut = text if len(text) <= 110 else text[:109] + "…"
            print(f"  {claim.get('claim_id')}  {note.get('path')}")
            print(f"    {cut}")
        if len(undated) > args.limit:
            print(f"  ... {len(undated) - args.limit} more (--limit)")

    print("Nothing was written. This tool counts; it does not judge.")
    if args.strict and undated:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
