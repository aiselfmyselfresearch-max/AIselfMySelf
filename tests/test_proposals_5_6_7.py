#!/usr/bin/env python3
"""Tests for the 2026-11-23 proposals 5-7 (role-target binding, saturation
valve, frontier-expansion metric).

What these pin, and why each one has to exist:

  * Proposal 6 (saturation valve): a question the allocator itself has diagnosed
    as saturated (best competing pair EIG below ``SATURATION_EIG_THRESHOLD``)
    leaves the ranked pool when ``exclude_saturated`` is on, and is re-admitted
    with an explicit reason only if the valve would otherwise empty the pool.
    A question with no eligible pair is *not* saturated -- missing information
    is not a settled question, and the two must not be conflated.
  * Proposal 5 (role-target binding): under ``role_binding`` the role is a
    function of the target's own state -- empty -> proposer, untested top mass
    holder (``narrowed`` included, since proposal 1 made it live) ->
    adversarial_tester, lineage duplicates -> consolidator -- and the default
    (``role_binding=False``) keeps the seed-bucket assignment unchanged.
  * Proposal 7 (frontier expansion): the standing metric is present, internally
    consistent, and an observation rather than a gate (the charter forbids
    turning counts into success conditions).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import learning_metrics  # noqa: E402


def _hyp(hid, posterior, status="active", adv=0, lineage_op="root", parents=None):
    return {
        "hypothesis_id": hid,
        "posterior": posterior,
        "effective_status": status,
        "adversarial_eval_count": adv,
        "lineage_op": lineage_op,
        "parent_hypothesis_ids": parents or [],
    }


def _qstate(qid, hyps, eig=0.5, hypothesis_count=None):
    return {
        "question_id": qid,
        "hypothesis_count": hypothesis_count if hypothesis_count is not None else len(hyps),
        "priority_scoped": 1.0,
        "priority_score": 1.0,
        "priority_scoped_normalized": 0.9,
        "active_entropy_bits": 0.5,
        "live_entropy_bits": 0.9,
        "live_entropy_max_bits": 1.0,
        "live_entropy_normalized": 0.9,
        "mean_active_uncertainty": 0.5,
        "top_competing_pair": {
            "expected_info_gain": eig,
            "left_hypothesis_id": hyps[0]["hypothesis_id"] if hyps else "H-x",
            "right_hypothesis_id": hyps[1]["hypothesis_id"] if len(hyps) > 1 else "H-y",
            "pair_mass_sum": 0.5,
        },
        "hypotheses": hyps,
    }


class SaturationPredicateTests(unittest.TestCase):
    def test_a_pair_below_the_threshold_is_saturated(self) -> None:
        qs = _qstate("Q-900", [_hyp("H-a", 0.6), _hyp("H-b", 0.4)], eig=0.001)
        self.assertTrue(belief_state.is_saturated_question(qs))

    def test_a_pair_at_or_above_the_threshold_is_not(self) -> None:
        qs = _qstate("Q-900", [_hyp("H-a", 0.6), _hyp("H-b", 0.4)], eig=0.5)
        self.assertFalse(belief_state.is_saturated_question(qs))

    def test_no_eligible_pair_is_missing_information_not_saturation(self) -> None:
        qs = _qstate("Q-900", [_hyp("H-a", 1.0)])
        qs["top_competing_pair"] = None
        self.assertFalse(belief_state.is_saturated_question(qs))


class SaturationValveTests(unittest.TestCase):
    def test_a_saturated_question_leaves_the_ranked_pool(self) -> None:
        # Q-SAT is saturated but would win on score; Q-OK is not saturated.
        # With the valve on, Q-SAT must not be picked.
        state = {"questions": {
            "Q-SAT": _qstate("Q-SAT", [_hyp("H-a", 0.9), _hyp("H-b", 0.1)], eig=0.0),
            "Q-OK": _qstate("Q-OK", [_hyp("H-c", 0.6), _hyp("H-d", 0.4)], eig=0.5),
        }}
        for excl, expected in ((False, "Q-SAT"), (True, "Q-OK")):
            qid, _ = belief_state.select_auto_question_id(
                state, ["Q-SAT", "Q-OK"], seed="seed-1", exclude_saturated=excl
            )
            self.assertEqual(qid, expected, f"exclude_saturated={excl}")

    def test_the_valve_re_admits_explicitly_when_the_pool_would_empty(self) -> None:
        state = {"questions": {
            "Q-SAT": _qstate("Q-SAT", [_hyp("H-a", 0.9), _hyp("H-b", 0.1)], eig=0.0),
        }}
        qid, reason = belief_state.select_auto_question_id(
            state, ["Q-SAT"], seed="seed-2", exclude_saturated=True
        )
        self.assertEqual(qid, "Q-SAT")
        self.assertIn("飽和のため再掲", reason)
        self.assertIn("EIG=", reason)

    def test_the_default_keeps_the_saturated_question_ranked(self) -> None:
        state = {"questions": {
            "Q-SAT": _qstate("Q-SAT", [_hyp("H-a", 0.9), _hyp("H-b", 0.1)], eig=0.0),
        }}
        qid, _ = belief_state.select_auto_question_id(state, ["Q-SAT"], seed="seed-3")
        self.assertEqual(qid, "Q-SAT")


class RoleBindingTests(unittest.TestCase):
    def test_an_empty_question_binds_the_proposer(self) -> None:
        role = belief_state.assign_session_role(
            seed="seed-x", question_summary={"hypotheses": []}, role_binding=True
        )
        self.assertEqual(role["role"], "proposer")

    def test_an_untested_narrowed_mass_holder_binds_the_tester(self) -> None:
        # The case the seed-only rule could not see: the mass sits on a
        # ``narrowed`` holder that has never been adversarially evaluated.
        qs = {"hypotheses": [_hyp("H-n", 0.99, status="narrowed", adv=0)]}
        role = belief_state.assign_session_role(
            seed="seed-y", question_summary=qs, role_binding=True
        )
        self.assertEqual(role["role"], "adversarial_tester")
        self.assertIn("H-n", role["reason"])

    def test_a_tested_mass_holder_does_not_bind_the_tester(self) -> None:
        qs = {"hypotheses": [_hyp("H-n", 0.99, status="narrowed", adv=4)]}
        role = belief_state.assign_session_role(
            seed="seed-z", question_summary=qs, role_binding=True
        )
        # The binding's tester branch does not fire: the holder is already
        # adversarially evaluated.  The role falls through to the default path
        # (an all-narrowed question has no ``active`` hypothesis, so the
        # historical rule sends a proposer) -- the point is that the *binding*
        # did not produce a tester.
        self.assertNotEqual(role["role"], "adversarial_tester")
        self.assertNotIn("対象の質量保持者", role["reason"])

    def test_lineage_duplicates_bind_the_consolidator(self) -> None:
        # The top mass holder is already tested, so the tester binding does not
        # fire and the lineage-duplicate binding does.
        qs = {"hypotheses": [
            _hyp("H-a", 0.5, adv=2, lineage_op="synthesizes", parents=["H-root"]),
            _hyp("H-b", 0.3, adv=1, lineage_op="subsumes", parents=["H-root"]),
        ]}
        role = belief_state.assign_session_role(
            seed="seed-w", question_summary=qs, role_binding=True
        )
        self.assertEqual(role["role"], "consolidator")

    def test_the_default_keeps_the_seed_bucket_assignment(self) -> None:
        qs = {"hypotheses": [
            _hyp("H-a", 0.5, adv=2, lineage_op="synthesizes", parents=["H-root"]),
            _hyp("H-b", 0.3, adv=1, lineage_op="subsumes", parents=["H-root"]),
        ]}
        role = belief_state.assign_session_role(seed="seed-v", question_summary=qs)
        self.assertIn("シード割当", role["reason"])

    def test_binding_precedes_the_seed_only_override(self) -> None:
        # A narrowed holder with mass and no adversarial evaluation binds the
        # tester even when a seed is present (the seed-only override required
        # ``not seed`` and looked at ``active`` only).
        qs = {"hypotheses": [_hyp("H-n", 0.9, status="narrowed", adv=0)]}
        role = belief_state.assign_session_role(
            seed="seed-u", question_summary=qs, role_binding=True
        )
        self.assertEqual(role["role"], "adversarial_tester")


class FrontierExpansionMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = learning_metrics.compute_learning_metrics(root=ROOT)

    def test_the_metric_is_present_and_internally_consistent(self) -> None:
        fe = self.metrics["frontier_expansion"]
        presented = fe["sessions_presented_peripheral"]
        registered = fe["sessions_registered_on_offered"]
        self.assertGreaterEqual(presented, 0)
        self.assertLessEqual(registered, presented)
        self.assertAlmostEqual(
            fe["expansion_rate"], round(registered / max(1, presented), 4), places=4
        )
        self.assertGreaterEqual(fe["registered_subsequently_evaluated"], 0)
        self.assertLessEqual(
            fe["registered_subsequently_evaluated"], max(1, registered)
        )

    def test_the_metric_is_an_observation_not_a_gate(self) -> None:
        # The charter forbids turning counts into success conditions: the
        # metric must not appear in the invariant checks.
        failures = learning_metrics.check_invariants(self.metrics)
        for msg in failures:
            self.assertNotIn("前線拡大", msg)
            self.assertNotIn("frontier", msg.lower())


if __name__ == "__main__":
    unittest.main()
