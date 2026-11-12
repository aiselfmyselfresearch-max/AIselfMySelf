"""Tests for ``tools/claim_dates.py`` — undated ``measured_fact`` claims.

The tool exists because a count in a claim describes the ledger at the moment it
was measured, and nothing in the note schema records that moment.  Its contract
is narrow: it counts ``measured_fact`` claims that contain a digit but no date,
time wording, or date-stamped ledger ID.  It never edits and never judges.

The tests below pin those properties: the three ways a claim can look dated, the
exclusion of other claim kinds and of digit-free claims, the ``since`` filter,
and the absence of writes.
"""
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import claim_dates  # noqa: E402


def note(note_id: str, created_at: str, claims: list[dict]) -> dict:
    return {
        "note_id": note_id,
        "path": f"readings/{note_id}.md",
        "created_at": created_at,
        "claims": claims,
    }


def claim(claim_id: str, kind: str, text: str) -> dict:
    return {"claim_id": claim_id, "kind": kind, "text": text}


class UndatedClaimTests(unittest.TestCase):
    def test_counts_numbered_claim_without_date(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "measured_fact", "関係線は 6,111 本")])]
        undated, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["measured"], 1)
        self.assertEqual(counts["numbered"], 1)
        self.assertEqual(counts["undated"], 1)
        self.assertEqual(len(undated), 1)

    def test_iso_date_counts_as_dated(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "measured_fact", "2026-11-11 時点で 6,746 本")])]
        _, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["numbered"], 1)
        self.assertEqual(counts["undated"], 0)

    def test_japanese_year_counts_as_dated(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "measured_fact", "2026年に 6,746 本")])]
        _, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["undated"], 0)

    def test_dated_ledger_id_counts_as_dated(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "measured_fact", "SESSION-20261110-43ee9f の 12 行")])]
        _, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["undated"], 0)

    def test_other_kinds_are_ignored(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "reading_revised", "6,111 本")])]
        _, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["measured"], 0)
        self.assertEqual(counts["undated"], 0)

    def test_digit_free_claim_is_not_numbered(self) -> None:
        notes = [note("NOTE-1", "2026-11-11", [claim("c1", "measured_fact", "数は書かれていない")])]
        _, counts = claim_dates.undated_claims(notes)
        self.assertEqual(counts["numbered"], 0)

    def test_since_filters_older_notes(self) -> None:
        notes = [
            note("NOTE-1", "2026-11-10", [claim("c1", "measured_fact", "6,111 本")]),
            note("NOTE-2", "2026-11-13", [claim("c2", "measured_fact", "6,746 本")]),
        ]
        _, filtered = claim_dates.undated_claims(notes, since="2026-11-13")
        self.assertEqual(filtered["notes"], 1)
        self.assertEqual(filtered["undated"], 1)


class RunnerTests(unittest.TestCase):
    def test_main_reports_and_writes_nothing(self) -> None:
        before = sorted(p.name for p in (ROOT / "state").iterdir())
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = claim_dates.main([])
        self.assertEqual(code, 0)
        self.assertIn("Nothing was written", buffer.getvalue())
        after = sorted(p.name for p in (ROOT / "state").iterdir())
        self.assertEqual(before, after)

    def test_strict_exits_nonzero_when_undated_exist(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            claim_dates.main([])
        if "without a date: 0" in buffer.getvalue():
            self.skipTest("ledger currently has no undated numbered claims")
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = claim_dates.main(["--strict"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
