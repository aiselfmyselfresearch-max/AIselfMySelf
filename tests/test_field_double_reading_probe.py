"""Regression tests for tools/field_double_reading_probe.py and heir_credit.

Three things are pinned, and each fails for a different reason.

1. **The engine's present arithmetic.** ``compared_against_hypothesis_ids``
   deducts the named partner only on a ``supports`` row. On ``narrows_scope``
   it deducts nothing. If a future change makes the field behave the same way
   under both verdicts, ``test_the_field_means_different_things_by_verdict``
   changes shape — a measurement, not a regression.

2. **The double reading.** A hypothesis that is both a named opponent and a
   lineage child of the target receives the child-side boost *because* it was
   named. ``test_named_heir_is_paid_as_an_heir`` pins that. If the fallback is
   ever removed from the default arithmetic, that test says so.

3. **``heir_credit`` is a knob, not a fix.** The default must reproduce the
   historical numbers exactly, and ``heir_credit=False`` must not write
   anything. ``test_default_is_byte_identical`` is the guard.

See readings/2026-11-17-the-prose-is-right-and-the-mechanism-is-wrong.md §1-§3.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state
import field_double_reading_probe as probe


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


def _evl(eid, target, partners, verdict="narrows_scope", spawned=()):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-12T00:00:00Z",
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": "reproducible_script",
        "summary": "synthetic row for the probe's own tests",
        "compared_against_hypothesis_ids": list(partners),
        "spawned_hypothesis_ids": list(spawned),
        "material_ids": [],
        "note_ids": [],
    }


def _ledger(verdict="narrows_scope", with_e1=True):
    """H-P (parent) with child H-C; H-O is an unrelated opponent.

    ``with_e1=False`` drops the baseline row so a test can measure **one** row's
    effect on the child. With the baseline present, E-1 already pays H-C through
    the lineage fallback, and two variants that differ only in E-2 look equal.
    """
    hyps = {
        "H-P": _hyp("H-P"),
        "H-C": _hyp("H-C", parents=["H-P"]),
        "H-O": _hyp("H-O"),
        "H-D": _hyp("H-D"),
    }
    evals = {"E-1": _evl("E-1", "H-P", ["H-O"], verdict=verdict)} if with_e1 else {}
    return {"questions": {}, "hypotheses": hyps, "evaluations": evals,
            "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
            "errata": {}, "hypothesis_read_log": {}}


def _lo(cols, hid, **kw):
    state = belief_state.compute_belief_state(copy.deepcopy(cols), **kw)
    for q in state["questions"].values():
        for h in q["hypotheses"]:
            if h["hypothesis_id"] == hid:
                return h["log_odds"]
    raise AssertionError(hid)


class FieldMeaningSyntheticTests(unittest.TestCase):
    def test_the_field_means_different_things_by_verdict(self):
        # supports: naming H-O lowers H-O.
        sup = _ledger("supports")
        sup["evaluations"]["E-2"] = _evl("E-2", "H-P", [], verdict="supports")
        # narrows_scope: naming H-O leaves H-O untouched.
        nar = _ledger("narrows_scope")
        nar["evaluations"]["E-2"] = _evl("E-2", "H-P", [], verdict="narrows_scope")
        self.assertLess(_lo(sup, "H-O"), _lo(nar, "H-O"),
                        "supports deducts the named partner; narrows_scope does not")

    def test_named_heir_is_paid_as_an_heir(self):
        # The child is named as the opponent. The verdict is a narrowing, so the
        # partner side deducts nothing; the child side pays 0.75*delta because
        # the lineage fallback fills `spawned`.
        named = _ledger(with_e1=False)
        named["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-C"])
        # The unnamed variant must leave the list EMPTY, not merely name
        # someone else: comp_factor reads only "is the list empty", so naming
        # H-O would lift the discount just as naming H-C does, and the two
        # variants would differ in nothing.
        unnamed = _ledger(with_e1=False)
        unnamed["evaluations"]["E-2"] = _evl("E-2", "H-P", [])
        self.assertGreater(_lo(named, "H-C"), _lo(unnamed, "H-C"),
                           "naming the heir raises it through the lineage fallback")

    def test_heir_credit_false_removes_the_fallback(self):
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-O"])
        with_fb = _lo(cols, "H-C")
        without = _lo(cols, "H-C", heir_credit=False)
        self.assertGreater(with_fb, without,
                           "the fallback is what pays the unnamed child")
        self.assertAlmostEqual(without, 0.0, places=12,
                               msg="with no heir credit the child is never touched")

    def test_an_explicit_heir_is_still_paid_when_the_fallback_is_off(self):
        # heir_credit only governs the *fallback*. A row that names its child
        # must keep paying it, or the knob would be a rewrite of the engine.
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-O"], spawned=["H-C"])
        self.assertAlmostEqual(_lo(cols, "H-C"), _lo(cols, "H-C", heir_credit=False),
                               places=12)
        self.assertGreater(_lo(cols, "H-C"), 0.0)


class ProbeShapeSyntheticTests(unittest.TestCase):
    def test_overlap_is_detected_with_its_source(self):
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-C"])
        res = probe.summarize(copy.deepcopy(cols))
        self.assertEqual(res["heir_overlap"]["n_rows"], 1)
        self.assertEqual(res["heir_overlap"]["by_heir_source"]["lineage-fallback"], 1)
        self.assertEqual(res["heir_overlap"]["rows_naming_only_the_heir"], 1)

    def test_an_explicit_heir_is_reported_as_explicit(self):
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-C"], spawned=["H-C"])
        res = probe.summarize(copy.deepcopy(cols))
        self.assertEqual(res["heir_overlap"]["by_heir_source"].get("explicit"), 1)

    def test_no_overlap_when_the_partner_is_not_a_child(self):
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-O"])
        res = probe.summarize(copy.deepcopy(cols))
        self.assertEqual(res["heir_overlap"]["n_rows"], 0)
        self.assertEqual(res["rows_naming_only_the_heir"], [])

    def test_partner_effect_is_signed_per_verdict(self):
        sup = _ledger(with_e1=False)
        sup["evaluations"]["E-1"] = _evl("E-1", "H-P", ["H-O"], verdict="supports")
        res = probe.summarize(copy.deepcopy(sup))
        self.assertLess(res["partner_effect_by_verdict"]["supports"]["sum_d_log_odds"], 0.0)
        nar = _ledger(with_e1=False)
        nar["evaluations"]["E-1"] = _evl("E-1", "H-P", ["H-O"], verdict="narrows_scope")
        res = probe.summarize(copy.deepcopy(nar))
        self.assertEqual(res["partner_effect_by_verdict"]["narrows_scope"]
                         ["rows_where_the_partner_moved"], 0)

    def test_quick_mode_says_what_it_skipped(self):
        # A --quick run must not print an empty table as if it were a measured
        # zero (the failure the flag was added to avoid).
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-C"])
        res = probe.summarize(copy.deepcopy(cols), per_row=False)
        self.assertTrue(res["per_row_sections_skipped"])
        text = probe.render(res, show=1)
        self.assertIn("SKIPPED (--quick)", text)

    def test_render_does_not_overclaim(self):
        cols = _ledger(with_e1=False)
        cols["evaluations"]["E-2"] = _evl("E-2", "H-P", ["H-C"])
        text = probe.render(probe.summarize(copy.deepcopy(cols)), show=1)
        self.assertIn("READ TWICE", text)
        self.assertNotIn("証明", text)


class LiveLedgerArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cols = belief_state.load_belief_ledgers(ROOT)
        cls.base = belief_state.compute_belief_state(copy.deepcopy(cls.cols))
        cls.off = belief_state.compute_belief_state(copy.deepcopy(cls.cols), heir_credit=True)

    def test_default_is_unchanged_by_the_knob(self):
        for qid, q in self.base["questions"].items():
            for h in q["hypotheses"]:
                other = next(x for x in self.off["questions"][qid]["hypotheses"]
                             if x["hypothesis_id"] == h["hypothesis_id"])
                self.assertAlmostEqual(h["posterior"], other["posterior"], places=12)

    def test_fallback_credit_exists_somewhere_in_the_live_ledger(self):
        # If the live ledger ever stops relying on the fallback, this test fails
        # and the whole §3 argument becomes about the past. That is information.
        without = belief_state.compute_belief_state(copy.deepcopy(self.cols),
                                                    heir_credit=False)
        moved = 0
        for qid, q in self.base["questions"].items():
            for h in q["hypotheses"]:
                other = next(x for x in without["questions"][qid]["hypotheses"]
                             if x["hypothesis_id"] == h["hypothesis_id"])
                if abs(h["log_odds"] - other["log_odds"]) > 1e-9:
                    moved += 1
        self.assertGreater(moved, 0)

    def test_heir_credit_writes_nothing(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        belief_state.compute_belief_state(copy.deepcopy(self.cols), heir_credit=False)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
