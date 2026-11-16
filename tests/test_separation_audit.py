"""Tests for the 2026-11-16 audit adoption (P-3, P-4, P-5, P-6, P-7).

Each test isolates one mechanism and asserts the arithmetic, not the archive:

- P-3 pair-level repetition discount (``pair_level_repeat``)
- P-4 least-separated pair selection
- P-5 ``scope_inherited_by_hypothesis_ids`` (narrowing a child funds its parent)
- P-6 ``errata.weight_effect: "void_row"`` (a correction withdraws a row, not a hypothesis)
- P-7 separation audit fields (independent separations, novelty)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402
import validate_seed as vseed  # noqa: E402


def hyp(hid, *, status="active", parents=None, session="SESSION-1", question="Q-003"):
    return {
        "hypothesis_id": hid,
        "question_ids": [question],
        "status": status,
        "parent_hypothesis_ids": parents or [],
        "lineage_op": "refines" if parents else "root",
        "title": f"title-{hid}",
        "proposition": f"proposition-{hid}",
        "scope_conditions": ["c"],
        "exclusion_clause": "a concrete falsifier",
        "session_id": session,
        "created_at": "2026-01-01",
        "supporting_material_ids": [],
        "counter_material_ids": [],
        "source_note_ids": [],
    }


def evl(
    eid,
    *,
    target,
    verdict="supports",
    etype="cross_session_audit",
    session="SESSION-1",
    compared=None,
    spawned=None,
    inherited=None,
    materials=None,
    day="2026-01-01",
):
    row = {
        "evaluation_id": eid,
        "session_id": session,
        "created_at": day,
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": etype,
        "summary": "synthetic row for arithmetic tests",
        "compared_against_hypothesis_ids": compared or [],
        "spawned_hypothesis_ids": spawned or [],
        "material_ids": materials or [],
        "note_ids": [],
    }
    if inherited is not None:
        row["scope_inherited_by_hypothesis_ids"] = inherited
    return row


def dataset(hyps, evals, *, errata=None, materials=None):
    return {
        "questions": {
            "Q-003": {"question_id": "Q-003", "question": "q"}
        },
        "hypotheses": {h["hypothesis_id"]: h for h in hyps},
        "evaluations": {e["evaluation_id"]: e for e in evals},
        "materials": materials or {},
        "read_log": {},
        "errata": errata or {},
    }


def posteriors(state, question="Q-003"):
    return {h["hypothesis_id"]: h["posterior"] for h in state["questions"][question]["hypotheses"]}


class PairLevelRepeatTests(unittest.TestCase):
    def test_same_pair_from_another_session_is_discounted_only_under_pair_basis(self):
        # Two identical supports rows on HYP-A against HYP-B, from two sessions.
        # Session basis: both pay full weight. Pair basis: the second pays 1/sqrt(2).
        data = dataset(
            [hyp("HYP-A"), hyp("HYP-B")],
            [
                evl("EVL-1", target="HYP-A", compared=["HYP-B"], session="SESSION-1"),
                evl("EVL-2", target="HYP-A", compared=["HYP-B"], session="SESSION-2"),
            ],
        )
        base = posteriors(bs.compute_belief_state(data=data))["HYP-A"]
        pair = posteriors(bs.compute_belief_state(data=data, pair_level_repeat=True))["HYP-A"]
        self.assertGreater(base, pair, "pair basis must not pay the repeat in full")

    def test_basis_is_reported_and_default_is_session(self):
        data = dataset(
            [hyp("HYP-A"), hyp("HYP-B")],
            [evl("EVL-1", target="HYP-A", compared=["HYP-B"])],
        )
        state = bs.compute_belief_state(data=data)
        self.assertEqual(state["posterior_basis"], "session")
        self.assertEqual(state["questions"]["Q-003"]["hypotheses"][0]["pair_basis_posterior"] is not None, True)
        alt = bs.compute_belief_state(data=data, pair_level_repeat=True)
        self.assertEqual(alt["posterior_basis"], "pair")

    def test_a_second_pair_is_not_discounted(self):
        # Different comparison sets are different pairs, so pair basis keeps full weight.
        data = dataset(
            [hyp("HYP-A"), hyp("HYP-B"), hyp("HYP-C")],
            [
                evl("EVL-1", target="HYP-A", compared=["HYP-B"], session="SESSION-1"),
                evl("EVL-2", target="HYP-A", compared=["HYP-C"], session="SESSION-2"),
            ],
        )
        state = bs.compute_belief_state(data=data, pair_level_repeat=True)
        row = next(h for h in state["questions"]["Q-003"]["hypotheses"] if h["hypothesis_id"] == "HYP-A")
        self.assertEqual(row["log_odds"], round(1.0 + 1.0, 4))


class ScopeInheritedTests(unittest.TestCase):
    def test_naming_the_parent_funds_the_parent(self):
        data = dataset(
            [hyp("HYP-PARENT"), hyp("HYP-CHILD", parents=["HYP-PARENT"])],
            [
                evl(
                    "EVL-1",
                    target="HYP-CHILD",
                    verdict="narrows_scope",
                    inherited=["HYP-PARENT"],
                )
            ],
        )
        got = posteriors(bs.compute_belief_state(data=data))
        self.assertGreater(got["HYP-PARENT"], 0.5)

    def test_without_the_field_the_childless_target_funds_less(self):
        hyps = [hyp("HYP-PARENT"), hyp("HYP-CHILD", parents=["HYP-PARENT"])]
        without = dataset(hyps, [evl("EVL-1", target="HYP-CHILD", verdict="narrows_scope")])
        with_field = dataset(
            hyps,
            [evl("EVL-1", target="HYP-CHILD", verdict="narrows_scope", inherited=["HYP-PARENT"])],
        )
        # HYP-CHILD has no children of its own, so the fallback names no recipient:
        # the parent still gains from the child being narrowed, but it gains the
        # explicit 0.75*delta only when the record names it.
        plain = posteriors(bs.compute_belief_state(data=without))["HYP-PARENT"]
        named = posteriors(bs.compute_belief_state(data=with_field))["HYP-PARENT"]
        self.assertGreater(named, plain)

    def test_field_and_spawned_union_are_not_double_counted(self):
        data = dataset(
            [hyp("HYP-PARENT"), hyp("HYP-CHILD", parents=["HYP-PARENT"])],
            [
                evl(
                    "EVL-1",
                    target="HYP-CHILD",
                    verdict="narrows_scope",
                    spawned=["HYP-PARENT"],
                    inherited=["HYP-PARENT"],
                )
            ],
        )
        union = posteriors(bs.compute_belief_state(data=data))
        data_spawned_only = dataset(
            [hyp("HYP-PARENT"), hyp("HYP-CHILD", parents=["HYP-PARENT"])],
            [evl("EVL-1", target="HYP-CHILD", verdict="narrows_scope", spawned=["HYP-PARENT"])],
        )
        single = posteriors(bs.compute_belief_state(data=data_spawned_only))
        self.assertAlmostEqual(union["HYP-PARENT"], single["HYP-PARENT"], places=4)


class VoidRowErrataTests(unittest.TestCase):
    def _errata(self, weight_effect, subject="EVL-SUP", status="open"):
        rec = {
            "errata_id": "ERR-1",
            "subject_type": "evaluation",
            "subject_id": subject,
            "claim": "the row over-claimed",
            "claim_location": "summary",
            "check": {"kind": "manual"},
            "verdict": "contradicted",
            "status": status,
            "created_at": "2026-01-02",
            "note": "measured against the material ledger",
        }
        if weight_effect is not None:
            rec["weight_effect"] = weight_effect
        return {"ERR-1": rec}

    def _data(self, errata):
        return dataset(
            [hyp("HYP-A"), hyp("HYP-B")],
            [
                evl("EVL-SUP", target="HYP-A", compared=["HYP-B"]),
                evl("EVL-B", target="HYP-B", compared=["HYP-A"]),
            ],
            errata=errata,
        )

    def test_void_row_removes_the_rows_weight(self):
        voided = bs.compute_belief_state(data=self._data(self._errata("void_row")))
        self.assertEqual([v["evaluation_id"] for v in voided["voided_evaluations"]], ["EVL-SUP"])
        with_row = bs.compute_belief_state(data=self._data(self._errata(None)))
        self.assertNotEqual(posteriors(voided)["HYP-A"], posteriors(with_row)["HYP-A"])

    def test_flag_is_the_default_and_moves_nothing(self):
        flagged = bs.compute_belief_state(data=self._data(self._errata("flag")))
        plain = bs.compute_belief_state(data=self._data({}))
        self.assertEqual(flagged["voided_evaluations"], [])
        self.assertAlmostEqual(posteriors(flagged)["HYP-A"], posteriors(plain)["HYP-A"], places=6)

    def test_withdrawn_correction_does_not_void(self):
        withdrawn = self._errata("void_row", status="withdrawn")
        state = bs.compute_belief_state(data=self._data(withdrawn))
        self.assertEqual(state["voided_evaluations"], [])

    def test_errata_on_a_hypothesis_is_untouched(self):
        rec = self._errata("void_row")
        rec["ERR-1"]["subject_type"] = "hypothesis"
        rec["ERR-1"]["subject_id"] = "HYP-A"
        state = bs.compute_belief_state(data=self._data(rec))
        self.assertEqual(state["voided_evaluations"], [])


class LeastSeparatedPairTests(unittest.TestCase):
    def _state(self, entries):
        return {
            "questions": {
                "Q-003": {
                    "hypotheses": [
                        {
                            "hypothesis_id": hid,
                            "posterior": p,
                            "uncertainty": u,
                            "effective_status": "active",
                            "direct_eval_count": 1,
                            "title": hid,
                            "parent_hypothesis_ids": [],
                        }
                        for hid, p, u in entries
                    ]
                }
            }
        }

    def test_it_prefers_the_pair_separated_fewest_times(self):
        evals = {}
        for i in range(4):
            row = evl(f"EVL-{i}", target="HYP-A", compared=["HYP-B"], session=f"S-{i}")
            evals[row["evaluation_id"]] = row
        # A-vs-C has been separated once; B-vs-C never. Both sides of B-vs-C carry
        # real mass, so it wins despite carrying less mass than A-vs-C.
        once = evl("EVL-AC", target="HYP-A", compared=["HYP-C"], session="S-AC")
        evals[once["evaluation_id"]] = once
        state = self._state([("HYP-A", 0.6, 0.2), ("HYP-B", 0.2, 0.3), ("HYP-C", 0.1, 0.4)])
        pair = bs.select_least_separated_pair(state, evals, "Q-003")
        self.assertEqual({pair["left_hypothesis_id"], pair["right_hypothesis_id"]}, {"HYP-B", "HYP-C"})
        self.assertEqual(pair["separations"], 0)
        self.assertEqual(pair["policy"], "least_separated")

    def test_it_ignores_hypotheses_with_negligible_mass(self):
        state = self._state([("HYP-A", 0.9, 0.2), ("HYP-B", 0.09, 0.3), ("HYP-Z", 0.001, 0.9)])
        pair = bs.select_least_separated_pair(state, {}, "Q-003", min_posterior=0.01)
        self.assertNotIn("HYP-Z", {pair["left_hypothesis_id"], pair["right_hypothesis_id"]})

    def test_none_when_fewer_than_two_qualify(self):
        state = self._state([("HYP-A", 0.99, 0.2), ("HYP-Z", 0.001, 0.9)])
        self.assertIsNone(bs.select_least_separated_pair(state, {}, "Q-003", min_posterior=0.01))


class SeparationAuditTests(unittest.TestCase):
    def test_counts_distinct_partners_and_novelty(self):
        data = dataset(
            [hyp("HYP-A"), hyp("HYP-B"), hyp("HYP-C")],
            [
                evl("EVL-1", target="HYP-A", compared=["HYP-B"], day="2026-01-01"),
                evl("EVL-2", target="HYP-A", compared=["HYP-B"], session="S-2", day="2026-01-02"),
                evl("EVL-3", target="HYP-A", compared=["HYP-C"], session="S-3", day="2026-01-03"),
            ],
        )
        state = bs.compute_belief_state(data=data)
        row = next(h for h in state["questions"]["Q-003"]["hypotheses"] if h["hypothesis_id"] == "HYP-A")
        self.assertEqual(row["independent_separation_count"], 2)
        self.assertEqual(row["last_new_separation_date"], "2026-01-03")
        nov = state["separation_novelty"]
        self.assertEqual(nov["rows"], 3)
        self.assertEqual(nov["new_pairs"], 2)


class NewRowAdvisoryTests(unittest.TestCase):
    def test_it_names_only_new_unbacked_primary_source_rows(self):
        evaluations = {
            "EVL-NEW": evl(
                "EVL-NEW", target="HYP-A", etype="primary_source_collision",
                materials=["MAT-1"], day="2026-11-16",
            ),
            "EVL-OLD": evl(
                "EVL-OLD", target="HYP-A", etype="primary_source_collision",
                materials=["MAT-1"], day="2026-11-01", session="S-2",
            ),
            "EVL-OK": evl(
                "EVL-OK", target="HYP-A", etype="primary_source_collision",
                materials=["MAT-2"], day="2026-11-16", session="S-3",
            ),
        }
        materials = {
            "MAT-1": {"verification": {"status": "partially_verified"}},
            "MAT-2": {"verification": {"status": "verified"}},
        }
        text = vseed.psc_new_row_advisory(evaluations, materials, cutoff="2026-11-16")
        self.assertIn("EVL-NEW", text)
        self.assertNotIn("EVL-OLD", text)
        self.assertNotIn("EVL-OK", text)

    def test_none_when_every_new_row_is_backed(self):
        evaluations = {
            "EVL-OK": evl(
                "EVL-OK", target="HYP-A", etype="primary_source_collision",
                materials=["MAT-2"], day="2026-11-16",
            )
        }
        materials = {"MAT-2": {"verification": {"status": "verified"}}}
        self.assertIsNone(vseed.psc_new_row_advisory(evaluations, materials, cutoff="2026-11-16"))


if __name__ == "__main__":
    unittest.main()
