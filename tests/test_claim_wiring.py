"""Tests for tools/claim_wiring.py — how far the meaning layer reaches belief.

The tool exists because 1,984 claims sat beside 30 hypotheses with only 9.8% of
claims naming one (readings/2026-11-15-where-the-learning-actually-happens.md
§2).  The table is an observation, so what these tests pin is the arithmetic:
which kinds are gated, what counts as wired, and that a declared
``no_hypothesis`` is not counted as wiring.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import claim_wiring  # noqa: E402


def note(note_id: str, claims: list[dict]) -> dict:
    return {"note_id": note_id, "session_id": "SESSION-20261116-aaaaaa", "created_at": "2026-11-16", "claims": claims}


class WiringReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.notes = {
            "NOTE-1": note("NOTE-1", [
                {"claim_id": "C1", "kind": "reading_revised", "text": "改訂", "hypothesis_ids": ["HYP-a"]},
                {"claim_id": "C2", "kind": "reading_revised", "text": "改訂"},
                {"claim_id": "C3", "kind": "retraction", "text": "撤回", "no_hypothesis": True},
                {"claim_id": "C4", "kind": "measured_fact", "text": "実測", "hypothesis_ids": ["HYP-b"]},
            ]),
            "NOTE-2": note("NOTE-2", [{"claim_id": "C5", "kind": "handoff", "text": "申し送り"}]),
            "NOTE-3": {"note_id": "NOTE-3", "session_id": "SESSION-1", "path": "readings/y.md"},
        }

    def test_totals_and_kinds(self) -> None:
        report = claim_wiring.wiring_report(self.notes)
        self.assertEqual(report["total_claims"], 5)
        self.assertEqual(report["notes"], 3)
        self.assertEqual(report["notes_with_claims"], 2)
        self.assertEqual(report["by_kind"]["reading_revised"], 2)
        self.assertEqual(report["wired_by_kind"]["measured_fact"], 1)

    def test_revision_coverage_counts_revision_and_retraction_only(self) -> None:
        report = claim_wiring.wiring_report(self.notes)
        self.assertEqual(report["revision_claims"], 3)
        self.assertEqual(report["revision_wired"], 1)
        self.assertAlmostEqual(report["revision_coverage"], round(1 / 3, 4), places=4)

    def test_declared_none_is_counted_but_not_wired(self) -> None:
        report = claim_wiring.wiring_report(self.notes)
        self.assertEqual(report["declared_no_hypothesis"], 1)
        self.assertEqual(report["wired_total"], 2)

    def test_unwired_examples_respect_the_limit(self) -> None:
        report = claim_wiring.wiring_report(self.notes, limit=1)
        self.assertEqual(len(report["unwired_examples"]), 1)
        self.assertEqual(report["unwired_examples"][0]["claim_id"], "C2")

    def test_handoff_claims_are_not_listed_as_unwired(self) -> None:
        report = claim_wiring.wiring_report(self.notes, limit=10)
        self.assertEqual({row["kind"] for row in report["unwired_examples"]}, {"reading_revised"})

    def test_empty_ledger_does_not_divide_by_zero(self) -> None:
        report = claim_wiring.wiring_report({})
        self.assertEqual(report["coverage"], 0.0)
        self.assertEqual(report["total_claims"], 0)

    def test_render_states_the_number_is_not_a_goal(self) -> None:
        text = claim_wiring.render(claim_wiring.wiring_report(self.notes))
        self.assertIn("notes: 3 (2 carry claims) / claims: 5", text)
        self.assertIn("達成目標ではありません", text)


class LiveLedgerTests(unittest.TestCase):
    def test_live_ledger_is_readable_and_large(self) -> None:
        report = claim_wiring.wiring_report(claim_wiring.load_notes(ROOT), limit=0)
        self.assertGreater(report["total_claims"], 1000)
        self.assertIn("revision_coverage", report)

    def test_check_mode_accepts_the_live_ledger(self) -> None:
        # Every pre-rule claim is history; the mode must pass rather than fail on them.
        self.assertEqual(claim_wiring.check(ROOT), 0)


if __name__ == "__main__":
    unittest.main()
