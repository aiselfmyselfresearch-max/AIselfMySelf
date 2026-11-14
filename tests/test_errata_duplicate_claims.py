"""Regression tests: one claim costs one penalty, however many rows restate it.

Before this, ``log_odds[hid] -= 0.60 * len(direct_errs)`` charged per row, so the
same claim filed twice cost twice. Concurrent sessions do file the same defect
twice: ERR-20261107-100f65 and ERR-20261107-259d5f both assert that shard merging
cannot recover the state/sessions.d byte budget, in different words. Meanwhile
ERR-20261107-ed8184 / -4ee0ec / -3aca22 are three *distinct* claims about one
material and must keep costing three.

So the rule cannot be "one penalty per addressee", and it cannot be fuzzy text
matching either. Exact repeats collapse mechanically; a reworded restatement is
declared with ``duplicate_of`` and the declaration is validated. These tests
assert that mechanism on synthetic rows. They never assert the direction of a
live metric, and they do not write to the repository.
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
OTHER = "HYP-20261113-20fa8c"
QUESTION = "Q-003"


def row(i: int, **over) -> dict:
    rec = {
        "errata_id": f"ERR-PROBE-DUP{i}",
        "subject_type": "hypothesis",
        "subject_id": HYP,
        "claim": "同一の主張。",
        "claim_location": "probe:1",
        "check": {"kind": "manual"},
        "verdict": "contradicted",
        "status": "open",
        "created_at": "2026-11-14",
        "note": "synthetic; never written to a ledger",
    }
    rec.update(over)
    return rec


class DuplicateClaimWeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cols = bs.load_belief_ledgers()
        cls.base = cls._measure(cls.cols)[0]

    @classmethod
    def _measure(cls, cols) -> tuple[float, list[str]]:
        state = bs.compute_belief_state(cols)
        hyp = next(h for h in state["questions"][QUESTION]["hypotheses"]
                   if h["hypothesis_id"] == HYP)
        return hyp["log_odds"], hyp["errata_flags"]

    def _delta(self, rows) -> tuple[float, int]:
        cols = copy.deepcopy(self.cols)
        for rec in rows:
            cols["errata"][rec["errata_id"]] = rec
        lo, flags = self._measure(cols)
        return round(lo - self.base, 6), len(flags)

    def test_identical_rows_cost_one_penalty_and_all_stay_visible(self):
        one, _ = self._delta([row(1)])
        self.assertLess(one, 0.0)
        for k in (2, 3, 5):
            with self.subTest(rows=k):
                d, flags = self._delta([row(i) for i in range(k)])
                self.assertEqual(d, one)
                self.assertEqual(flags, k, "collapsed rows must remain visible")

    def test_distinct_claims_still_cost_one_each(self):
        one, _ = self._delta([row(1)])
        for k in (2, 3):
            with self.subTest(claims=k):
                d, _ = self._delta([row(i, claim=f"独立した主張 {i}。") for i in range(k)])
                self.assertAlmostEqual(d, k * one, places=6)

    def test_normalisation_collapses_only_cosmetic_difference(self):
        d, _ = self._delta([row(1), row(2, claim="  同一の主張。 "),
                            row(3, claim="同一の主張。\t")])
        one, _ = self._delta([row(1)])
        self.assertEqual(d, one)

    def test_rewording_is_not_inferred_and_must_be_declared(self):
        one, _ = self._delta([row(1)])
        reworded = "書き換え版。"
        undeclared, _ = self._delta([row(1), row(2, claim=reworded)])
        self.assertAlmostEqual(undeclared, 2 * one, places=6,
                               msg="the engine must not guess that two wordings match")
        declared, _ = self._delta([
            row(1), row(2, claim=reworded, duplicate_of=["ERR-PROBE-DUP1"]),
        ])
        self.assertEqual(declared, one)

    def test_declaration_chains_collapse_transitively(self):
        one, _ = self._delta([row(1)])
        d, _ = self._delta([
            row(1),
            row(2, claim="B", duplicate_of=["ERR-PROBE-DUP1"]),
            row(3, claim="C", duplicate_of=["ERR-PROBE-DUP2"]),
        ])
        self.assertEqual(d, one)

    def test_cycle_terminates_and_collapses(self):
        one, _ = self._delta([row(1)])
        d, _ = self._delta([
            row(1, claim="X", duplicate_of=["ERR-PROBE-DUP2"]),
            row(2, claim="Y", duplicate_of=["ERR-PROBE-DUP1"]),
        ])
        self.assertEqual(d, one)

    def test_same_text_against_two_addressees_is_two_claims(self):
        one, _ = self._delta([row(1)])
        d, flags = self._delta([row(1), row(2, subject_id=OTHER)])
        self.assertEqual(d, one, "only the row addressed here may cost here")
        self.assertEqual(flags, 1)

    def test_grouping_precedes_the_verdict_gate_so_dedup_cannot_escape(self):
        one, _ = self._delta([row(1)])
        # A live correction plus a withdrawn restatement is still one live claim.
        d, flags = self._delta([row(1), row(2, status="withdrawn")])
        self.assertEqual(d, one)
        self.assertEqual(flags, 2)
        # Declaring a live row a duplicate of a withdrawn one does not dodge it.
        d, _ = self._delta([
            row(1, status="withdrawn"),
            row(2, duplicate_of=["ERR-PROBE-DUP1"]),
        ])
        self.assertEqual(d, one)

    def test_all_withdrawn_repeats_cost_nothing(self):
        d, flags = self._delta([row(i, status="withdrawn") for i in (1, 2, 3)])
        self.assertEqual(d, 0.0)
        self.assertEqual(flags, 3)

    def test_unknown_declaration_is_inert_in_the_engine(self):
        one, _ = self._delta([row(1)])
        d, _ = self._delta([
            row(1), row(2, claim="別。", duplicate_of=["ERR-NOT-IN-LEDGER"]),
        ])
        self.assertAlmostEqual(d, 2 * one, places=6)

    def test_grouping_helper_is_pure(self):
        rows = [row(1), row(2)]
        before = copy.deepcopy(rows)
        groups = bs.distinct_errata_claims(rows)
        self.assertEqual(len(groups), 1)
        self.assertEqual(rows, before, "grouping must not mutate its input")

    def test_live_penalty_branch_is_still_latent(self):
        idx = bs.build_errata_index(self.cols["errata"])
        direct = [h for h in self.cols["hypotheses"] if idx.get(h)]
        self.assertEqual(direct, [], "a live hypothesis now carries a direct errata row")

    def test_tests_do_not_write_to_the_ledger(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").glob("errata.d/*.jsonl")}
        self._delta([row(1), row(2)])
        for p, data in before.items():
            self.assertEqual(p.read_bytes(), data)


class DuplicateDeclarationValidationTests(unittest.TestCase):
    def _errors(self, recs) -> list[str]:
        errors: list[str] = []
        vs.check_errata_duplicate_claims(recs, errors)
        return errors

    def test_valid_declaration_passes(self):
        a = {"subject_type": "hypothesis", "subject_id": HYP}
        self.assertEqual(self._errors({
            "E1": dict(a), "E2": dict(a, duplicate_of=["E1"]),
        }), [])

    def test_dangling_self_and_cross_addressee_are_rejected(self):
        a = {"subject_type": "hypothesis", "subject_id": HYP}
        with self.subTest(case="dangling"):
            self.assertTrue(self._errors({"E2": dict(a, duplicate_of=["NOPE"])}))
        with self.subTest(case="self"):
            self.assertTrue(self._errors({"E1": dict(a, duplicate_of=["E1"])}))
        with self.subTest(case="cross-addressee"):
            self.assertTrue(self._errors({
                "E1": dict(a),
                "E2": {"subject_type": "hypothesis", "subject_id": OTHER,
                       "duplicate_of": ["E1"]},
            }))

    def test_non_array_declaration_is_rejected(self):
        self.assertTrue(self._errors({
            "E1": {"subject_id": HYP},
            "E2": {"subject_id": HYP, "duplicate_of": "E1"},
        }))

    def test_legacy_rows_are_untouched(self):
        self.assertEqual(self._errors({"E1": {"subject_id": HYP}}), [])
        self.assertEqual(self._errors({"E1": {}, "E2": {"duplicate_of": ["E1"]}}), [])

    def test_every_live_errata_row_satisfies_the_gate(self):
        errors: list[str] = []
        vs.check_errata_duplicate_claims(bs.load_belief_ledgers()["errata"], errors)
        self.assertEqual(errors, [], "the new gate rejects rows already on main")

    def test_schema_declares_the_field(self):
        import json
        schema = json.loads((ROOT / "schema" / "errata.schema.json").read_text(encoding="utf-8"))
        prop = schema["properties"]["duplicate_of"]
        self.assertEqual(prop["type"], "array")
        self.assertTrue(prop.get("uniqueItems"))
        self.assertNotIn("duplicate_of", schema["required"], "must stay optional")


if __name__ == "__main__":
    unittest.main()
