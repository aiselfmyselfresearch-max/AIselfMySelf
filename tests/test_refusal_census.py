"""Tests for tools/refusal_census.py (read-only structural census)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import refusal_census  # noqa: E402


class CensusOnFixtureTests(unittest.TestCase):
    def test_left_and_took_are_split_by_the_offered_question(self) -> None:
        result = refusal_census.census(ROOT, today="20261121")
        self.assertEqual(
            result["left"]["sessions"] + result["took"]["sessions"],
            result["sessions_with_receipt"],
        )
        # Every receipt offering one of the central three questions is inside one
        # of the two groups, so the count can never exceed the receipts.
        self.assertLessEqual(result["central_offers"], result["sessions_with_receipt"])
        self.assertLessEqual(result["central_left"], result["central_offers"])

    def test_forward_stamped_offer_is_detected(self) -> None:
        # Regression for the measurement in
        # readings/2026-11-21-the-refusal-that-was-not-a-refusal.md §1: a session
        # whose own stamp is in the past cannot have been offered a question
        # stamped after it unless that stamp is a label.
        result = refusal_census.census(ROOT, today="20261116")
        offers = {item["session_id"]: item["offered"] for item in result["forward_stamped_offers"]}
        self.assertEqual(offers.get("SESSION-20261116-18e776"), "Q-20261121-198fc8")
        # The bound is an upper limit on the *offerer's* stamp, not on the offered
        # one, so a forward-dated offer keeps being visible at any later date:
        # raising the bound never erases evidence that a question predated its stamp.
        later = refusal_census.census(ROOT, today="20271231")
        earlier_set = {item["session_id"] for item in result["forward_stamped_offers"]}
        later_set = {item["session_id"] for item in later["forward_stamped_offers"]}
        # The bound gates the *offerer's* stamp: raising it only adds offerers
        # whose own dates were previously in the future, and never erases one.
        self.assertTrue(earlier_set <= later_set, "a raised bound cannot erase an offer")
        self.assertGreater(len(later_set), len(earlier_set))

    def test_json_is_serialisable(self) -> None:
        result = refusal_census.census(ROOT, today="20261121")
        json.dumps(result, ensure_ascii=False)


class SplitLogicTests(unittest.TestCase):
    def test_returned_text_states_that_motive_is_not_measured(self) -> None:
        result = refusal_census.census(ROOT, today="20261121")
        text = refusal_census.render(result)
        self.assertIn("not a motive", text)


if __name__ == "__main__":
    unittest.main()
