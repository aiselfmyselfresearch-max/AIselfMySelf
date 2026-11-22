"""Tests for the two measurement knobs added on 2026-11-18.

Both knobs exist so that a *question* can be measured instead of argued:

  ``heir_credit=False``            drops the lineage fallback (spawned = children)
  ``narrowing_partner_share=True`` makes a narrowing row deduct its named partners

Neither is a proposal. Both default to the present arithmetic, and the first
test in each class is the guard that says so: with the default, the engine must
reproduce the historical posteriors exactly. If a future session decides to flip
one of these, the flip has to change those tests on purpose, not by accident.

Also pinned: ``render_belief_map_markdown`` prints the third basis column
(``P_lin``) for every hypothesis that has one, and prints ``—`` when it does not.
A column silently falling back to the raw ``P`` would make the two bases look
identical, which is the one reading the column exists to prevent.

See readings/2026-11-18-the-three-debts-and-the-one-that-bends.md §2, §3.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state as bs


def _hyp(hid, parents=()):
    return {
        "hypothesis_id": hid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-10T00:00:00Z",
        "question_ids": ["Q-QA"],
        "title": hid,
        "proposition": hid,
        "scope_conditions": ["test"],
        "exclusion_clause": "test",
        "lineage_op": "refines" if parents else "root",
        "parent_hypothesis_ids": list(parents),
        "status": "active",
    }


def _evl(eid, target, partners, verdict="narrows_scope", spawned=(), session="S-1"):
    return {
        "evaluation_id": eid,
        "session_id": session,
        "created_at": "2026-11-12T00:00:00Z",
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": "reproducible_script",
        "summary": "synthetic row for the knob tests",
        "compared_against_hypothesis_ids": list(partners),
        "spawned_hypothesis_ids": list(spawned),
        "material_ids": [],
        "note_ids": [],
    }


def _ledger(rows):
    hyps = {
        "H-P": _hyp("H-P"),
        "H-C": _hyp("H-C", parents=["H-P"]),
        "H-O": _hyp("H-O"),
    }
    return {"questions": {}, "hypotheses": hyps, "evaluations": {r["evaluation_id"]: r for r in rows},
            "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
            "errata": {}, "hypothesis_read_log": {}}


def _lo(cols, hid, **kw):
    state = bs.compute_belief_state(copy.deepcopy(cols), **kw)
    for q in state["questions"].values():
        for h in q["hypotheses"]:
            if h["hypothesis_id"] == hid:
                return h["log_odds"]
    raise AssertionError(hid)


class HeirCreditKnobTests(unittest.TestCase):
    def setUp(self):
        self.cols = _ledger([_evl("E-1", "H-P", ["H-O"])])

    def test_default_pays_the_lineage_child(self):
        self.assertGreater(_lo(self.cols, "H-C"), 0.0)

    def test_false_removes_the_fallback(self):
        self.assertAlmostEqual(_lo(self.cols, "H-C", heir_credit=False), 0.0, places=12)

    def test_an_explicitly_named_child_is_paid_either_way(self):
        cols = _ledger([_evl("E-1", "H-P", ["H-O"], spawned=["H-C"])])
        self.assertAlmostEqual(_lo(cols, "H-C"), _lo(cols, "H-C", heir_credit=False), places=12)
        self.assertGreater(_lo(cols, "H-C", heir_credit=False), 0.0)

    def test_it_does_not_change_a_supporting_row(self):
        cols = _ledger([_evl("E-1", "H-P", ["H-O"], verdict="supports")])
        self.assertAlmostEqual(_lo(cols, "H-O"), _lo(cols, "H-O", heir_credit=False), places=12)


class NarrowingPartnerShareKnobTests(unittest.TestCase):
    def setUp(self):
        self.cols = _ledger([_evl("E-1", "H-P", ["H-O"])])

    def test_default_deducts_nothing(self):
        bare = _ledger([_evl("E-1", "H-P", [])])
        self.assertAlmostEqual(_lo(self.cols, "H-O"), _lo(bare, "H-O"), places=12)

    def test_true_deducts_the_named_partner(self):
        # The deduction is 0.20 * delta / len(compared), with the same delta the
        # target is charged; delta is positive here (comp_factor 1.0), so the
        # partner falls by 0.20 * delta.
        self.assertLess(_lo(self.cols, "H-O", narrowing_partner_share=True),
                        _lo(self.cols, "H-O"))

    def test_the_target_is_unaffected_by_the_knob(self):
        self.assertAlmostEqual(_lo(self.cols, "H-P"),
                               _lo(self.cols, "H-P", narrowing_partner_share=True), places=12)

    def test_two_partners_split_the_deduction(self):
        two = _ledger([_evl("E-1", "H-P", ["H-O", "H-C"])])
        one = self.cols
        self.assertGreater(_lo(two, "H-O", narrowing_partner_share=True),
                           _lo(one, "H-O", narrowing_partner_share=True))

    def test_it_does_not_change_a_supporting_row(self):
        cols = _ledger([_evl("E-1", "H-P", ["H-O"], verdict="supports")])
        self.assertAlmostEqual(_lo(cols, "H-O"),
                               _lo(cols, "H-O", narrowing_partner_share=True), places=12)


class ThirdBasisColumnTests(unittest.TestCase):
    def test_render_prints_the_column_and_a_dash_when_absent(self):
        cols = _ledger([_evl("E-1", "H-P", ["H-O"])])
        state = bs.compute_belief_state(copy.deepcopy(cols))
        text = bs.render_belief_map_markdown(state)
        self.assertIn("P_lin", text)
        self.assertIn("no_lineage_posterior", str(state["questions"]["Q-QA"]["hypotheses"][0]))
        self.assertIn("—", text)

    def test_an_untouched_hypothesis_keeps_its_log_odds(self):
        # H-O is neither a target nor a child, so turning the fallback off must
        # not move it. Asserted on log_odds, not on the posterior: the softmax
        # divides by every hypothesis in the question, so H-O's *posterior* does
        # move when H-C's mass changes. Comparing posteriors here would make a
        # correct engine look inconsistent (see test_pair_identity_probe's note).
        cols = _ledger([_evl("E-1", "H-P", ["H-O"])])
        on = _lo(cols, "H-O")
        off = _lo(cols, "H-O", heir_credit=False)
        self.assertAlmostEqual(on, off, places=12)
        state = bs.compute_belief_state(copy.deepcopy(cols))
        for h in state["questions"]["Q-QA"]["hypotheses"]:
            if h["hypothesis_id"] == "H-O":
                self.assertNotAlmostEqual(h["no_lineage_posterior"], h["posterior"], places=9)

    def test_child_posterior_moves_between_the_two_bases(self):
        cols = _ledger([_evl("E-1", "H-P", ["H-O"])])
        state = bs.compute_belief_state(copy.deepcopy(cols))
        for h in state["questions"]["Q-QA"]["hypotheses"]:
            if h["hypothesis_id"] == "H-C":
                self.assertGreater(h["posterior"], h["no_lineage_posterior"])


class LiveLedgerArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cols = bs.load_belief_ledgers(ROOT)
        cls.base = bs.compute_belief_state(copy.deepcopy(cls.cols))

    def test_both_knobs_leave_the_default_alone(self):
        same = bs.compute_belief_state(copy.deepcopy(self.cols), heir_credit=True,
                                       narrowing_partner_share=False)
        for qid, q in self.base["questions"].items():
            for h in q["hypotheses"]:
                other = next(x for x in same["questions"][qid]["hypotheses"]
                             if x["hypothesis_id"] == h["hypothesis_id"])
                self.assertAlmostEqual(h["posterior"], other["posterior"], places=12)

    def test_every_hypothesis_in_the_map_has_the_third_basis(self):
        # If the column ever stops being emitted, the map silently loses the
        # measurement it was added for.
        for qid, q in self.base["questions"].items():
            for h in q["hypotheses"]:
                self.assertIn("no_lineage_posterior", h)

    def test_the_two_knobs_are_not_the_same_measurement(self):
        # heir_credit moves mass between parent and child; the partner-share knob
        # moves it between the target and everyone it named. Confusing them would
        # make the report's §2 and §3 look interchangeable.
        a = bs.compute_belief_state(copy.deepcopy(self.cols), heir_credit=False)
        b = bs.compute_belief_state(copy.deepcopy(self.cols), narrowing_partner_share=True)
        moved_by_heir = {h["hypothesis_id"] for q in a["questions"].values()
                         for h in q["hypotheses"]
                         if abs(h["log_odds"] - next(
                             x["log_odds"] for x in self.base["questions"][
                                 next(k for k, v in self.base["questions"].items()
                                      if any(y["hypothesis_id"] == h["hypothesis_id"]
                                             for y in v["hypotheses"]))]["hypotheses"]
                             if x["hypothesis_id"] == h["hypothesis_id"])) > 1e-9}
        moved_by_share = {h["hypothesis_id"] for q in b["questions"].values()
                          for h in q["hypotheses"]}
        self.assertTrue(moved_by_heir)
        self.assertTrue(moved_by_share)
        self.assertNotEqual(moved_by_heir, moved_by_share)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# 2026-11-22: ``temporal_heir_guard`` -- the third knob, and the narrowest.
#
# The fallback reads ``children_by_parent``, which is built from the hypotheses
# that exist *at read time*. A row recorded before a child was registered
# therefore pays that child anyway. This knob drops only those credits whose
# child day is strictly later than the evaluation's day.
#
# See readings/2026-11-22-the-question-that-closed-itself.md
# ---------------------------------------------------------------------------


def _hyp_dated(hid, created_at, parents=()):
    h = _hyp(hid, parents=parents)
    h["created_at"] = created_at
    return h


def _ledger_dated(hyps, rows):
    return {"questions": {}, "hypotheses": hyps, "evaluations": {r["evaluation_id"]: r for r in rows},
            "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
            "errata": {}, "hypothesis_read_log": {}}


class TemporalHeirGuardTests(unittest.TestCase):
    """The guard denies exactly one thing: credit that post-dates the row."""

    def _post_dated(self):
        hyps = {
            "H-P": _hyp_dated("H-P", "2026-11-10T00:00:00Z"),
            # child registered two days AFTER the evaluation below
            "H-LATE": _hyp_dated("H-LATE", "2026-11-14T00:00:00Z", parents=["H-P"]),
        }
        return _ledger_dated(hyps, [_evl("E-1", "H-P", [])])  # E-1 is dated 2026-11-12

    def _prior(self):
        hyps = {
            "H-P": _hyp_dated("H-P", "2026-11-10T00:00:00Z"),
            # child already existed when the row was written
            "H-EARLY": _hyp_dated("H-EARLY", "2026-11-11T00:00:00Z", parents=["H-P"]),
        }
        return _ledger_dated(hyps, [_evl("E-1", "H-P", [])])

    def test_default_still_pays_a_post_dated_child(self):
        # Pinned deliberately: the default is the historical arithmetic, so this
        # test must fail if someone flips the default without meaning to.
        self.assertGreater(_lo(self._post_dated(), "H-LATE"), 0.0)

    def test_guard_denies_credit_that_post_dates_the_row(self):
        self.assertAlmostEqual(
            _lo(self._post_dated(), "H-LATE", temporal_heir_guard=True), 0.0, places=12
        )

    def test_guard_keeps_credit_for_a_child_that_already_existed(self):
        self.assertGreater(
            _lo(self._prior(), "H-EARLY", temporal_heir_guard=True), 0.0
        )

    def test_guard_does_not_touch_the_target(self):
        # The row's own verdict on its own target is a measurement, not an
        # inheritance, so it must survive the guard unchanged.
        for cols in (self._post_dated(), self._prior()):
            self.assertAlmostEqual(
                _lo(cols, "H-P", temporal_heir_guard=True),
                _lo(cols, "H-P"),
                places=12,
            )

    def test_guard_does_not_touch_explicitly_named_heirs(self):
        hyps = {
            "H-P": _hyp_dated("H-P", "2026-11-10T00:00:00Z"),
            "H-NAMED": _hyp_dated("H-NAMED", "2026-11-20T00:00:00Z", parents=["H-P"]),
        }
        cols = _ledger_dated(hyps, [_evl("E-1", "H-P", [], spawned=["H-NAMED"])])
        self.assertGreater(_lo(cols, "H-NAMED", temporal_heir_guard=True), 0.0)

    def test_guard_is_a_subset_of_dropping_the_fallback(self):
        # Never deny more than heir_credit=False already denies.
        for cols, hid in ((self._post_dated(), "H-LATE"), (self._prior(), "H-EARLY")):
            guarded = _lo(cols, hid, temporal_heir_guard=True)
            no_fallback = _lo(cols, hid, heir_credit=False)
            self.assertGreaterEqual(guarded, no_fallback - 1e-12)
