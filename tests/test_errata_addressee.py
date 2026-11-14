"""Regression tests for the errata addressee fixes.

Two defects, both measured on 85c400f before the change; the rules are documented
in docs/memory-architecture.md, section on the belief map:

1. The -0.60 weight penalty counted every row carrying an ``errata_id``, so a
   withdrawn correction, one whose check found the claim HELD, and one that could
   not be measured all cost exactly as much as a live contradiction (filed as
   ERR-20261114-9a6fb1).
2. ``claim_location`` -- a required *prose* field saying where a claim was written
   -- was indexed as an address, so a correction addressed to a tool penalised a
   hypothesis whose ID happened to appear there.

A third behaviour is deliberately NOT changed: ``subject_type`` has no routing
power, because IDs and repo paths are self-identifying and routing on the label
would let a mislabelled row escape its address. Instead the label is validated for
consistency, which is what ``validate_seed.check_errata_addressee_labels`` does.

These tests assert mechanism on synthetic rows. They never assert the direction of
a live metric, and they do not write to the repository.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402
import validate_seed as vs  # noqa: E402

HYP = "HYP-20261113-ccc1d8"
QUESTION = "Q-003"


def row(**over) -> dict:
    rec = {
        "errata_id": "ERR-PROBE-ADDR",
        "subject_type": "hypothesis",
        "subject_id": HYP,
        "claim": "合成行。機構のテストであり、実在の主張ではない。",
        "claim_location": "probe:1",
        "check": {"kind": "manual"},
        "verdict": "contradicted",
        "status": "open",
        "created_at": "2026-11-14",
        "note": "synthetic; never written to a ledger",
    }
    rec.update(over)
    return rec


class ErrataWeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cols = bs.load_belief_ledgers()
        cls.base = cls._measure(cls.cols)

    @classmethod
    def _measure(cls, cols) -> tuple[float, list[str]]:
        state = bs.compute_belief_state(cols)
        hyp = next(h for h in state["questions"][QUESTION]["hypotheses"]
                   if h["hypothesis_id"] == HYP)
        return hyp["log_odds"], hyp["errata_flags"]

    def _with(self, rec) -> tuple[float, list[str]]:
        cols = copy.deepcopy(self.cols)
        cols["errata"][rec["errata_id"]] = rec
        lo, flags = self._measure(cols)
        return round(lo - self.base[0], 6), flags

    def test_live_contradiction_still_costs_weight(self):
        for status in ("open", "annotated"):
            with self.subTest(status=status):
                delta, flags = self._with(row(status=status))
                self.assertLess(delta, 0.0)
                self.assertEqual(len(flags), 1)

    def test_withdrawn_correction_costs_nothing_but_stays_visible(self):
        delta, flags = self._with(row(status="withdrawn"))
        self.assertEqual(delta, 0.0)
        self.assertEqual(len(flags), 1, "a retracted correction must remain visible")

    def test_correction_that_found_no_error_costs_nothing(self):
        for verdict in ("holds", "unmeasurable"):
            with self.subTest(verdict=verdict):
                delta, flags = self._with(row(verdict=verdict))
                self.assertEqual(delta, 0.0)
                self.assertEqual(len(flags), 1)

    def test_unknown_status_cannot_be_used_to_dodge_the_penalty(self):
        # Two live rows carry `corrected`, which is outside the schema enum.
        delta, _ = self._with(row(status="corrected"))
        self.assertLess(delta, 0.0)

    def test_only_live_rows_count_when_several_address_one_hypothesis(self):
        cols = copy.deepcopy(self.cols)
        for i, over in enumerate((
            {"verdict": "contradicted", "status": "open"},
            {"verdict": "holds", "status": "open"},
            {"verdict": "contradicted", "status": "withdrawn"},
        )):
            rec = row(**over)
            rec["errata_id"] = f"ERR-PROBE-MIX{i}"
            cols["errata"][rec["errata_id"]] = rec
        lo, flags = self._measure(cols)
        delta = round(lo - self.base[0], 6)
        live, _ = self._with(row())
        self.assertEqual(delta, live, "spent corrections were counted toward the weight")
        self.assertEqual(len(flags), 3, "all three rows should still be visible")

    def test_prose_location_is_not_an_address_when_one_is_present(self):
        delta, flags = self._with(row(
            subject_type="tool", subject_id="tools/belief_state.py", claim_location=HYP,
        ))
        self.assertEqual(delta, 0.0)
        self.assertEqual(flags, [])

    def test_prose_location_still_routes_a_row_with_no_address(self):
        # ERR-20261101-d7caa6 is a live row with no subject_id at all; the fallback
        # must keep such rows reachable.
        rec = row(claim_location=HYP)
        del rec["subject_id"]
        del rec["subject_type"]
        delta, flags = self._with(rec)
        self.assertLess(delta, 0.0)
        self.assertEqual(len(flags), 1)

    def test_index_ignores_prose_but_keeps_every_address_field(self):
        recs = {
            "E1": row(errata_id="E1", subject_id="MAT-X", claim_location="HYP-OTHER"),
            "E2": row(errata_id="E2", subject_id="", fragment_id="FRAG-X"),
            "E3": {"errata_id": "E3", "target": {"type": "note", "id": "NOTE-X"},
                   "claim_location": "HYP-OTHER2", "verdict": "contradicted",
                   "status": "open"},
        }
        idx = bs.build_errata_index(recs)
        self.assertIn("MAT-X", idx)
        self.assertIn("FRAG-X", idx)
        self.assertIn("NOTE-X", idx)
        self.assertNotIn("HYP-OTHER", idx)
        self.assertNotIn("HYP-OTHER2", idx)

    def test_live_penalty_branch_is_still_latent(self):
        # Mechanism guard, not a metric: if a future row addresses a hypothesis
        # directly, this fails and the live map must be re-measured deliberately.
        idx = bs.build_errata_index(self.cols["errata"])
        direct = [h for h in self.cols["hypotheses"] if idx.get(h)]
        self.assertEqual(direct, [], "a live hypothesis now carries a direct errata row")

    def test_tests_do_not_write_to_the_ledger(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").glob("errata.d/*.jsonl")}
        self._with(row(status="withdrawn"))
        for p, data in before.items():
            self.assertEqual(p.read_bytes(), data)


class AddresseeLabelTests(unittest.TestCase):
    def _errors(self, rec) -> list[str]:
        errors: list[str] = []
        vs.check_errata_addressee_labels({"ERR-T": rec}, errors)
        return errors

    def test_label_must_not_contradict_a_ledger_address(self):
        for stype, sid in (
            ("tool", HYP),
            ("report", "NOTE-20261114-ef60a5"),
            ("hypothesis", "tools/belief_state.py"),
            ("material", "readings/2026-11-14-x.md"),
        ):
            with self.subTest(subject_type=stype):
                self.assertTrue(self._errors({"subject_type": stype, "subject_id": sid}))

    def test_truthful_labels_are_accepted(self):
        for stype, sid in (
            ("tool", "tools/belief_state.py"),
            ("report", "readings/2026-11-14-x.md"),
            ("hypothesis", HYP),
            ("material", "MAT-LIT-005"),
            ("evaluation", "EVL-20261114-913eea"),
            ("other", "ERR-20261114-ff7f16 / ERR-20261114-9a6fb1"),
        ):
            with self.subTest(subject_type=stype):
                self.assertEqual(self._errors({"subject_type": stype, "subject_id": sid}), [])

    def test_composite_address_needs_only_one_matching_token(self):
        self.assertEqual(self._errors({
            "subject_type": "material",
            "subject_id": "MAT-LIT-005 / MAT-LIT-001 の記述",
        }), [])

    def test_legacy_rows_without_label_or_address_are_untouched(self):
        self.assertEqual(self._errors({"subject_id": "tools/x.py"}), [])
        self.assertEqual(self._errors({"subject_type": "other"}), [])

    def test_every_live_errata_row_satisfies_the_gate(self):
        cols = bs.load_belief_ledgers()
        errors: list[str] = []
        vs.check_errata_addressee_labels(cols["errata"], errors)
        self.assertEqual(errors, [], "the new gate rejects rows already on main")


if __name__ == "__main__":
    unittest.main()
