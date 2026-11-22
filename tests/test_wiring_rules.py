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


class LabelEvidenceTests(unittest.TestCase):
    """The gate must not depend on the wall clock (measured 2026-11-21).

    Two questions merged by PR #1002 carry the stamp 20261121 but sit in a shard
    named 2026-10-24; on the merge day the wall clock had not reached the stamp's
    midnight in every timezone and `validate_seed.py` failed on main.  Left alone,
    57 more rows would have crossed a moving `stamp <= today` bound one by one
    until 65 failed, with no commit changing anything.  These tests pin the
    evidence-based reading that replaces the moving bound.
    """

    LABEL = "Q-20261121-198fc8"
    SHARD = Path("state/questions.d/2026-10-24-000000000000.jsonl")

    def test_earlier_shard_than_stamp_is_a_label(self) -> None:
        self.assertTrue(validate_seed._is_internal_label(self.LABEL, self.SHARD))
        self.assertFalse(
            validate_seed._is_new_row(
                self.LABEL, "20261116", today=datetime.date(2026, 11, 21), shard=self.SHARD
            )
        )

    def test_a_real_row_in_its_own_shard_still_fails(self) -> None:
        # Same stamp, same day, but the row sits in the shard named for that day:
        # no evidence of a label, so the gate keeps working.
        errors: list[str] = []
        validate_seed.check_registers(
            {"questions": {"Q-20261121-abcdef": {"question_id": "Q-20261121-abcdef"}}},
            errors,
            today=datetime.date(2026, 11, 21),
            shard_of={"Q-20261121-abcdef": Path("state/questions.d/2026-11-21-aaaaaaaaaaaa.jsonl")},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("register is missing", errors[0])

    def test_undated_shard_proves_nothing(self) -> None:
        self.assertFalse(validate_seed._is_internal_label(self.LABEL, Path("state/questions.jsonl")))
        self.assertFalse(validate_seed._is_internal_label(self.LABEL, None))

    def test_tomorrows_stamp_is_still_hidden(self) -> None:
        # Unchanged behaviour: a stamp later than today is never judged new.
        self.assertFalse(
            validate_seed._is_new_row(
                "Q-20261201-abcdef", "20261116", today=datetime.date(2026, 11, 21)
            )
        )

    def test_offer_evidence_finds_labels(self) -> None:
        collections = {
            "sessions": {
                "SESSION-20261116-18e776": {
                    "session_id": "SESSION-20261116-18e776",
                    "offered_target_question_id": "Q-20261121-198fc8",
                }
            }
        }
        labels = validate_seed.build_forward_label_evidence(
            collections, today=datetime.date(2026, 11, 21)
        )
        self.assertIn("Q-20261121-198fc8", labels)

    def test_offer_evidence_ignores_a_forward_dated_offerer(self) -> None:
        # If the session holding the receipt is itself in the future, the offer
        # proves nothing about an earlier day.
        collections = {
            "sessions": {
                "SESSION-20270101-aaaaaa": {
                    "session_id": "SESSION-20270101-aaaaaa",
                    "offered_target_question_id": "Q-20270201-bbbbbb",
                }
            }
        }
        labels = validate_seed.build_forward_label_evidence(
            collections, today=datetime.date(2026, 11, 21)
        )
        self.assertEqual(labels, frozenset())


class SessionSelfLayerGateTests(unittest.TestCase):
    """The six-layer session gate must read the same evidence as the register gate.

    Measured 2026-11-22: ``SESSION-20261122-11b1d3`` sits in a shard named
    2026-11-10, so ``_is_internal_label`` proves its stamp is a chronology label;
    the register gate exempts it, but the session gate read only the stamp and
    the wall clock, so the same bytes passed on 2026-11-21 and failed on
    2026-11-22 with no commit in between.  These tests pin both halves: the
    proven label stays exempt, and a real-dated or unprovable stamp is still
    required to carry the two fields.
    """

    ROW = {
        "session_type": "other",
        "self_layer_checks": {
            "source_attributed": True,
            "agency_stance_recorded": True,
            "self_model_rebuilt": True,
            "veto_considered": True,
        },
    }
    TODAY = datetime.date(2026, 11, 22)

    def _run(self, shard, row=None):
        errors: list[str] = []
        shard_of = {"SESSION-20261122-abcdef": shard} if shard else {}
        new, _, _, _ = validate_seed.check_session_self_layer(
            {"SESSION-20261122-abcdef": row if row is not None else {}},
            errors,
            today=self.TODAY,
            shard_of=shard_of,
        )
        return new, errors

    def test_row_in_earlier_named_shard_is_treated_as_a_label(self) -> None:
        new, errors = self._run(Path("state/sessions.d/2026-11-10-000000000000.jsonl"))
        self.assertEqual(new, 0)
        self.assertEqual(errors, [])

    def test_row_in_same_day_shard_is_still_required(self) -> None:
        new, errors = self._run(Path("state/sessions.d/2026-11-22-aaaa.jsonl"))
        self.assertEqual(new, 1)
        self.assertEqual(len(errors), 2)

    def test_row_with_no_shard_evidence_is_still_required(self) -> None:
        new, errors = self._run(None)
        self.assertEqual(new, 1)
        self.assertEqual(len(errors), 2)

    def test_complete_row_passes_in_a_same_day_shard(self) -> None:
        new, errors = self._run(Path("state/sessions.d/2026-11-22-aaaa.jsonl"), self.ROW)
        self.assertEqual(new, 1)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
