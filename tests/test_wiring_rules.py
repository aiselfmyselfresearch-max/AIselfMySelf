"""Tests for the two rules added on 2026-11-15 (docs/registers.md §2).

Both rules are date-gated: they apply to rows whose ID carries a date at or after
2026-11-16 and no later than today.  The upper bound matters because legacy rows
keep internal chronology labels (some in 2027) in their IDs; without it the rule
would fail dozens of questions that were written before the rule existed.
"""
from __future__ import annotations

import datetime
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_seed  # noqa: E402

TODAY = datetime.date(2026, 12, 31)


def note(note_id: str, claims: list[dict]) -> dict:
    return {"note_id": note_id, "session_id": "SESSION-20261116-aaaaaa", "path": "readings/x.md", "claims": claims}


class IsNewRowTests(unittest.TestCase):
    def test_row_at_cutoff_is_new(self) -> None:
        self.assertTrue(validate_seed._is_new_row("Q-20261116-abcdef", "20261116", today=TODAY))

    def test_old_row_is_not_new(self) -> None:
        self.assertFalse(validate_seed._is_new_row("Q-20261115-abcdef", "20261116", today=TODAY))

    def test_row_without_date_is_not_new(self) -> None:
        self.assertFalse(validate_seed._is_new_row("Q-001", "20261116", today=TODAY))

    def test_forward_dated_legacy_row_is_not_new(self) -> None:
        # A legacy row whose internal chronology label sits in 2027 must stay out
        # of the gate; date_axis.py refuses *new* forward-dated shards instead.
        self.assertFalse(validate_seed._is_new_row("Q-20270221-abcdef", "20261116", today=TODAY))

    def test_today_bounds_are_inclusive(self) -> None:
        self.assertTrue(validate_seed._is_new_row("Q-20261231-abcdef", "20261116", today=TODAY))
        self.assertFalse(validate_seed._is_new_row("Q-20270101-abcdef", "20261116", today=TODAY))


class ClaimWiringTests(unittest.TestCase):
    def check(self, notes: dict) -> list[str]:
        errors: list[str] = []
        validate_seed.check_claim_wiring(notes, errors, today=TODAY)
        return errors

    def test_new_revision_claim_without_hypothesis_fails(self) -> None:
        errors = self.check({"NOTE-20261116-aaaaaa": note("NOTE-20261116-aaaaaa", [
            {"claim_id": "C1", "kind": "reading_revised", "text": "改訂した"},
        ])})
        self.assertEqual(len(errors), 1)
        self.assertIn("no_hypothesis", errors[0])

    def test_new_revision_claim_with_hypothesis_passes(self) -> None:
        errors = self.check({"NOTE-20261116-aaaaaa": note("NOTE-20261116-aaaaaa", [
            {"claim_id": "C1", "kind": "reading_revised", "text": "改訂した", "hypothesis_ids": ["HYP-20261112-5dc940"]},
        ])})
        self.assertEqual(errors, [])

    def test_declared_none_passes(self) -> None:
        errors = self.check({"NOTE-20261116-aaaaaa": note("NOTE-20261116-aaaaaa", [
            {"claim_id": "C1", "kind": "retraction", "text": "撤回した", "no_hypothesis": True},
        ])})
        self.assertEqual(errors, [])

    def test_other_kinds_are_not_gated(self) -> None:
        errors = self.check({"NOTE-20261116-aaaaaa": note("NOTE-20261116-aaaaaa", [
            {"claim_id": "C1", "kind": "measured_fact", "text": "測った"},
            {"claim_id": "C2", "kind": "handoff", "text": "申し送り"},
        ])})
        self.assertEqual(errors, [])

    def test_old_rows_are_history(self) -> None:
        errors = self.check({"NOTE-20261114-aaaaaa": note("NOTE-20261114-aaaaaa", [
            {"claim_id": "C1", "kind": "reading_revised", "text": "改訂した"},
        ])})
        self.assertEqual(errors, [])

    def test_note_without_claims_is_skipped(self) -> None:
        errors = self.check({"NOTE-20261116-bbbbbb": {"note_id": "NOTE-20261116-bbbbbb"}})
        self.assertEqual(errors, [])


class RegisterTests(unittest.TestCase):
    def check(self, collections: dict) -> list[str]:
        errors: list[str] = []
        validate_seed.check_registers(collections, errors, today=TODAY)
        return errors

    def test_new_question_without_register_fails(self) -> None:
        errors = self.check({"questions": {"Q-20261116-abcdef": {"question_id": "Q-20261116-abcdef"}}})
        self.assertEqual(len(errors), 1)
        self.assertIn("register is missing", errors[0])

    def test_new_question_with_register_passes(self) -> None:
        errors = self.check({"questions": {"Q-20261116-abcdef": {"question_id": "Q-20261116-abcdef", "register": "judgment"}}})
        self.assertEqual(errors, [])

    def test_unknown_register_fails(self) -> None:
        errors = self.check({"hypotheses": {"HYP-20261116-abcdef": {"hypothesis_id": "HYP-20261116-abcdef", "register": "tidying"}}})
        self.assertEqual(len(errors), 1)
        self.assertIn("'tidying'", errors[0])

    def test_both_collections_are_checked(self) -> None:
        errors = self.check({
            "questions": {"Q-20261116-abcdef": {"question_id": "Q-20261116-abcdef"}},
            "hypotheses": {"HYP-20261116-abcdef": {"hypothesis_id": "HYP-20261116-abcdef"}},
        })
        self.assertEqual(len(errors), 2)

    def test_old_questions_are_not_gated(self) -> None:
        errors = self.check({"questions": {"Q-20261114-abcdef": {"question_id": "Q-20261114-abcdef"}}})
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
