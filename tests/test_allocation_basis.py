#!/usr/bin/env python3
"""Tests for the 2026-11-23 allocation-basis change (proposals 1-4).

What these pin, and why each one has to exist:

  * The defect: ``active_entropy`` was taken over ``active`` only, so a question
    whose mass sat on a ``narrowed`` hypothesis reported ``H = 0`` and was never
    selected.  The statuses are pinned *by name* because a check that only
    asserted "bigger now" would pass if ``refuted`` were silently added.
  * The invariant (proposal 3): ``readable`` is false exactly when the counted
    set holds less than the floor of the mass.
  * The regression: ``historical`` reproduces the pre-change ranking, so the new
    basis cannot rewrite a number a reader already cited.
  * The rejected alternative: normalising by log2(n) reverses the top question
    here.  Recorded as a measurement, because proposal 2 as designed was wrong
    and the reason must survive its correction.
  * The bootstrap (proposal 4): a question with no hypothesis cannot receive an
    EVL, so it must not outrank a question that can by an arithmetic accident.
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import ledger_io  # noqa: E402


class LiveStatusTests(unittest.TestCase):
    def test_the_counted_statuses_are_pinned_by_name(self) -> None:
        # ``narrowed`` is a live competitor ("true under stated conditions");
        # ``refuted`` is not.  Widening this tuple to ``refuted`` would make the
        # defect disappear while making the arithmetic wrong.
        self.assertEqual(
            belief_state.LIVE_EFFECTIVE_STATUSES, ("active", "narrowed")
        )
        self.assertNotIn("refuted", belief_state.LIVE_EFFECTIVE_STATUSES)


class LiveLedgerTests(unittest.TestCase):
    """These read the real ledger: the numbers below are measurements, not fixtures."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = belief_state.compute_belief_state(root=ROOT)

    def _q(self, qid: str) -> dict:
        return self.state["questions"][qid]

    def test_the_centre_reports_more_entropy_than_the_active_only_reading(self) -> None:
        # Measured 2026-11-23: Q-001 active-only 0.658 b, scope-inclusive 1.364 b
        # over 26 live hypotheses.  The point is the *relation*, not the digits.
        q = self._q("Q-001")
        # Q-001's live set is its active hypotheses plus the narrowed ones; the
        # remainder are refuted and must not be counted.  Stated as relations,
        # not as frozen counts: this session's own hypothesis lands on Q-001, so
        # the absolute numbers move with the ledger (measured 2026-11-23 before /
        # after: 30 -> 31 hypotheses, 26 -> 27 live, H 1.364 b both times).
        self.assertGreater(q["live_count"], q["active_count"])
        self.assertLess(q["live_count"], q["hypothesis_count"])
        self.assertGreater(q["hypothesis_count"] - q["live_count"], 0)
        self.assertGreater(q["live_entropy_bits"], q["active_entropy_bits"] + 0.5)

    def test_a_question_whose_mass_is_outside_the_counted_set_is_not_readable(self) -> None:
        # Q-002/Q-003: 99.92% of the mass sits on one ``narrowed`` hypothesis and
        # the live set holds 0.05%.  This is the condition the pre-change map
        # rendered as ``H = 0.000 b`` with no warning at all.
        for qid in ("Q-002", "Q-003"):
            q = self._q(qid)
            self.assertLess(q["live_mass_share"], 0.5, qid)
            self.assertFalse(q["readable"], qid)
            self.assertGreater(q["live_count"], 30, qid)

    def test_readable_is_exactly_the_floor_comparison(self) -> None:
        for qid, q in self.state["questions"].items():
            if q.get("hypothesis_count", 0) == 0:
                continue
            expected = q["live_mass_share"] >= belief_state.UNREADABLE_MASS_SHARE_FLOOR
            self.assertEqual(q["readable"], expected, qid)

    def test_the_historical_fields_are_still_published(self) -> None:
        # A reader who cited 0.658 b for Q-001 on 2026-11-22 must still find
        # ``active_entropy_bits`` under that name, computed the way it was
        # computed then.  This used to assert the *value* (0.658 within 3
        # places), which was a live measurement masquerading as a pin: it
        # forbade any later session from registering a hypothesis on Q-001,
        # because one new row moves the digits.  Measured 2026-11-23: adding
        # two rows to Q-001 moved it 0.6577 -> 0.7359 and the pin failed, so
        # the check was blocking the ledger from growing rather than
        # protecting an arithmetic.  What is pinned now is the *formula*:
        # H over active posteriors, normalised within the active set, plus
        # 0.8*mean_u plus 1/sqrt(1+n_evals).  The historical value stays
        # reachable as a measurement in
        # readings/2026-11-23-the-allocation-reads-the-question-not-the-leftovers.md
        # and in BELIEF_MAP.md, both of which are dated.
        q = self._q("Q-001")
        self.assertIn("active_entropy_bits", q)
        self.assertIn("priority_score", q)
        active = [h["posterior"] for h in q["hypotheses"] if h["effective_status"] == "active"]
        mass = sum(active)
        expected = -sum((p / mass) * math.log2(max(p / mass, 1e-12)) for p in active)
        self.assertAlmostEqual(q["active_entropy_bits"], round(expected, 4), places=3)
        n_evals = sum(h["direct_eval_count"] for h in q["hypotheses"])
        self.assertAlmostEqual(
            q["priority_score"],
            expected + 0.8 * q["mean_active_uncertainty"] + 1 / math.sqrt(1 + n_evals),
            places=3,
        )

    def test_the_new_score_is_additive_not_a_replacement(self) -> None:
        for qid, q in self.state["questions"].items():
            self.assertIn("priority_score", q, qid)
            self.assertIn("priority_scoped", q, qid)
            self.assertIn("priority_scoped_normalized", q, qid)


class AllocationBasisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = belief_state.compute_belief_state(root=ROOT)
        cls.open_qids = [
            qid
            for qid, q in ledger_io.load_jsonl_union(
                ROOT / "state" / "questions.jsonl", "question_id", root=ROOT
            ).items()
            if q.get("status", "open") == "open"
        ]
        cls.seeds = sorted(
            {
                s["dispersal_seed"]
                for s in ledger_io.load_jsonl_union(
                    ROOT / "state" / "sessions.jsonl", "session_id", root=ROOT
                ).values()
                if s.get("dispersal_seed")
            }
        )

    def test_scoped_is_the_default_basis(self) -> None:
        self.assertEqual(belief_state.ALLOCATION_BASIS_DEFAULT, "scoped")
        self.assertIn("scoped", belief_state.ALLOCATION_BASES)
        self.assertIn("historical", belief_state.ALLOCATION_BASES)

    def test_the_default_assigns_the_centre(self) -> None:
        # Measured 2026-11-23: before, 248/248 seeds went to
        # Q-20261024-6bdafd, a 2-hypothesis peripheral question.  The centre,
        # which holds 26 live hypotheses and 1.364 unresolved bits, never got a
        # session.  After: 248/248 seeds go to Q-001.
        picks = {
            belief_state.select_auto_question_id(
                self.state, self.open_qids, seed=s
            )[0]
            for s in self.seeds
        }
        self.assertEqual(picks, {"Q-001"})

    def test_the_historical_basis_still_reproduces_the_old_choice(self) -> None:
        picks = {
            belief_state.select_auto_question_id(
                self.state, self.open_qids, seed=s, allocation_basis="historical"
            )[0]
            for s in self.seeds
        }
        self.assertEqual(picks, {"Q-20261024-6bdafd"})

    def test_the_normalised_basis_is_kept_and_still_reverses_the_ranking(self) -> None:
        # Proposal 2 as designed was wrong.  Recorded as measurement so the
        # correction is reproducible and cannot be re-proposed as new.
        norm_q = self.state["questions"]["Q-001"]
        lead_q = self.state["questions"]["Q-20261024-6bdafd"]
        self.assertLess(
            norm_q["live_entropy_normalized"], lead_q["live_entropy_normalized"]
        )
        self.assertGreater(norm_q["live_entropy_bits"], lead_q["live_entropy_bits"])
        picks = {
            belief_state.select_auto_question_id(
                self.state, self.open_qids, seed=s, allocation_basis="scoped_norm"
            )[0]
            for s in self.seeds
        }
        self.assertEqual(picks, {"Q-20261024-6bdafd"})

    def test_an_unknown_basis_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            belief_state.select_auto_question_id(
                self.state, self.open_qids, allocation_basis="vibes"
            )


class BootstrapSlotTests(unittest.TestCase):
    def test_the_bootstrap_priority_is_below_any_measurable_question(self) -> None:
        # A question that cannot receive an EVL must not outrank one that can,
        # however decayed.  The old 0.40 floor could beat a centre question once
        # its entropy fell below 0.259 b.
        self.assertLess(belief_state.PROPOSER_BOOTSTRAP_PRIORITY, 0.40)
        state = belief_state.compute_belief_state(root=ROOT)
        self.assertGreater(
            min(
                q["priority_scoped"]
                for q in state["questions"].values()
                if q.get("priority_scoped") is not None
            ),
            0.0,
        )

    def test_an_empty_question_is_scored_on_the_bootstrap_slot(self) -> None:
        a = _bare_state()
        qid, reason = belief_state.select_auto_question_id(
            a, ["Q-999"], seed="proposer-seed"
        )
        self.assertEqual(qid, "Q-999")
        self.assertIn("提題者ブートストラップ枠", reason)
        self.assertIn("EVL は仮説を指す", reason)
        # Zero jitter without a seed: the score must be exactly the constant.
        _qid, reason_noseed = belief_state.select_auto_question_id(a, ["Q-999"])
        self.assertIn(
            f"score={belief_state.PROPOSER_BOOTSTRAP_PRIORITY:.3f}", reason_noseed
        )

    def test_a_core_question_with_no_hypotheses_keeps_its_standing_priority(self) -> None:
        a = _bare_state()
        _qid, reason = belief_state.select_auto_question_id(a, ["Q-001"])
        self.assertIn("中核問い未定式化優先", reason)
        self.assertIn(
            f"score={belief_state.HYPOTHESIS_LESS_CORE_PRIORITY:.3f}", reason
        )


class AllocatedAuditTests(unittest.TestCase):
    def test_the_audit_names_the_unreadable_questions(self) -> None:
        audit = belief_state.allocation_audit(root=ROOT)
        self.assertIn("Q-002", audit["unreadable_question_ids"])
        self.assertIn("Q-003", audit["unreadable_question_ids"])
        self.assertNotIn("Q-001", audit["unreadable_question_ids"])

    def test_the_audit_reports_whether_the_warning_moves_the_assignment(self) -> None:
        audit = belief_state.allocation_audit(root=ROOT)
        self.assertEqual(set(audit["basis_leaders"]), set(belief_state.ALLOCATION_BASES))
        # The warning is about display *and* assignment: the bases disagree here,
        # which is exactly why the audit reports the spread rather than one choice.
        self.assertFalse(audit["basis_leaders_agree"])

    def test_the_audit_renders_the_warning_in_japanese(self) -> None:
        text = belief_state.render_allocation_audit_markdown(
            belief_state.allocation_audit(root=ROOT)
        )
        self.assertIn("決着の印ではなく", text)
        self.assertIn("質量が数えた集合の外にある印", text)


def _bare_state() -> dict:
    """A minimal state dict, so the bootstrap path is tested without the ledger."""
    return {
        "questions": {
            "Q-999": {
                "question_id": "Q-999",
                "hypothesis_count": 0,
                "priority_score": None,
                "readable": False,
                "priority_scoped": None,
            },
            "Q-001": {
                "question_id": "Q-001",
                "hypothesis_count": 0,
                "priority_score": belief_state.HYPOTHESIS_LESS_CORE_PRIORITY,
                "readable": False,
                "priority_scoped": None,
            },
        }
    }


if __name__ == "__main__":
    unittest.main()
