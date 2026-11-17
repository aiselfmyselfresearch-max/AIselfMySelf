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
