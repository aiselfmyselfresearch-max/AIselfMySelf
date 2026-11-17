"""Regression tests for tools/pair_identity_probe.py.

Two things are pinned, and they are pinned separately on purpose.

1. **The engine's present arithmetic.** If a future change makes the comparison
   partner's *identity* reach the posterior, ``test_partner_identity_is_not_read``
   fails. That failure is the falsification condition (a) of
   ``HYP-20261117-0b6170`` being met, not a broken test.
2. **The probe's own honesty.** The probe must not write to any ledger, must not
   modify ``belief_state.py`` on disk, and its rendered output must not claim a
   property the numbers do not show. A measuring instrument that silently
   flatters its own finding is worse than no instrument.

A synthetic ledger test pins the arithmetic shape independently of the live
archive, so this file keeps meaning after the live distribution moves.

See readings/2026-11-17-the-comparison-column-does-not-compare.md §2, §9.1.
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
import pair_identity_probe as probe


def _hyp(hid, qid="Q-QA", parents=""):
    return {
        "hypothesis_id": hid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-10T00:00:00Z",
        "question_ids": [qid],
        "title": hid,
        "proposition": hid,
        "scope_conditions": ["test"],
        "exclusion_clause": "test",
        "lineage_op": "root",
        "parent_hypothesis_ids": [parents] if parents else [],
        "status": "active",
    }


def _evl(eid, target, partners, verdict="narrows_scope",
         ev_type="reproducible_script"):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-12T00:00:00Z",
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": ev_type,
        "summary": "synthetic",
        "compared_against_hypothesis_ids": list(partners),
        "material_ids": [],
        "note_ids": [],
    }


def _ledger():
    hyps = {hid: _hyp(hid) for hid in ("H-A", "H-B", "H-C", "H-D")}
    evals = {
        "E-1": _evl("E-1", "H-A", ["H-B"]),
        "E-2": _evl("E-2", "H-A", ["H-C"], verdict="supports", ev_type="cross_session_audit"),
    }
    return {"questions": {}, "hypotheses": hyps, "evaluations": evals,
            "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
            "errata": {}, "hypothesis_read_log": {}}


class PartnerIdentitySyntheticTests(unittest.TestCase):
    """The shape of the finding, on four synthetic hypotheses."""

    def setUp(self):
        self.cols = _ledger()
        self.base = belief_state.compute_belief_state(copy.deepcopy(self.cols))

    def _post(self, cols, hid):
        """Posterior, read through softmax -- so it also carries other rows' moves."""
        return self._field(cols, hid, "posterior")

    def _lo(self, cols, hid):
        """log_odds: the quantity the arithmetic actually adds and subtracts.

        Assertions about *which term moved* are made here, not on the posterior:
        a softmax divides by every hypothesis in the question, so a change to a
        third hypothesis moves the posterior of a pair whose own log-odds did
        not move at all. Comparing posteriors would make a correct engine look
        inconsistent.
        """
        return self._field(cols, hid, "log_odds")

    def _field(self, cols, hid, name):
        state = belief_state.compute_belief_state(copy.deepcopy(cols))
        for q in state["questions"].values():
            for h in q["hypotheses"]:
                if h["hypothesis_id"] == hid:
                    return h[name]
        raise AssertionError(hid)

    def test_partner_identity_does_not_change_the_target(self):
        # H-B and H-C are symmetric at the start; naming either one as the
        # comparison partner must leave H-A's posterior identical, because the
        # engine reads only "is the list empty" and "how many entries".
        a = copy.deepcopy(self.cols)
        a["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-B"])
        b = copy.deepcopy(self.cols)
        b["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-C"])
        self.assertAlmostEqual(self._lo(a, "H-A"), self._lo(b, "H-A"), places=12)

    def test_narrowing_deducts_no_partner_at_all(self):
        # Measured, and worth pinning because it is easy to assume otherwise:
        # the ``share`` deduction lives inside the ``supports`` branch only. A
        # ``narrows_scope`` row uses its partners purely as a discount switch,
        # so naming H-B vs H-C leaves both of them untouched (identical to
        # 1e-12), even though the target moves the same way in both cases.
        a = copy.deepcopy(self.cols)
        a["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-B"])
        b = copy.deepcopy(self.cols)
        b["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-C"])
        self.assertAlmostEqual(self._lo(a, "H-B"), self._lo(b, "H-B"), places=12)
        # and the partner pays nothing compared with not being named at all
        c = copy.deepcopy(self.cols)
        c["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", [])
        self.assertAlmostEqual(self._lo(a, "H-B"), self._lo(c, "H-B"), places=12)

    def test_supporting_deducts_the_named_partner(self):
        a = copy.deepcopy(self.cols)
        a["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-B"], verdict="supports")
        b = copy.deepcopy(self.cols)
        b["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-C"], verdict="supports")
        self.assertLess(self._lo(a, "H-B"), self._lo(b, "H-B"),
                        "the named partner carries the deduction, and only it")

    def test_naming_any_partner_lifts_the_discount(self):
        # comp_factor is 0.65 when the list is empty and 1.0 otherwise, so a row
        # with a partner moves a support target further than the same row without.
        named = copy.deepcopy(self.cols)
        named["evaluations"]["PROBE-S"] = _evl("PROBE-S", "H-D", [], verdict="supports")
        named["evaluations"]["PROBE-S"]["compared_against_hypothesis_ids"] = ["H-C"]
        alone = copy.deepcopy(self.cols)
        alone["evaluations"]["PROBE-S"] = _evl("PROBE-S", "H-D", [], verdict="supports")
        self.assertGreater(self._lo(named, "H-D"), self._lo(alone, "H-D"))

    def test_count_of_partners_divides_the_deduction(self):
        # The division is visible only in the supports branch (0.20*delta/len).
        one = copy.deepcopy(self.cols)
        one["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-B"], verdict="supports")
        two = copy.deepcopy(self.cols)
        two["evaluations"]["PROBE-A"] = _evl("PROBE-A", "H-A", ["H-B", "H-C"],
                                             verdict="supports")
        self.assertGreater(self._lo(two, "H-B"), self._lo(one, "H-B"),
                           "each named partner pays less when two are named")
        self.assertAlmostEqual(self._lo(one, "H-A"), self._lo(two, "H-A"), places=12)


class LiveLedgerArmTests(unittest.TestCase):
    """The live archive: the arms and the ledger scan."""

    @classmethod
    def setUpClass(cls):
        cls.res = probe.run("Q-003", ROOT)

    def test_partner_identity_is_not_read(self):
        # Falsification condition (a) of HYP-20261117-0b6170. A red test here is
        # a successful measurement, not a regression.
        diff = self.res["max_posterior_difference_between_partners"]
        self.assertIsNotNone(diff)
        self.assertLess(diff, 1e-12,
                        "the engine now reads which hypothesis is named as a comparison partner")

    def test_naming_a_partner_beats_naming_none(self):
        self.assertGreater(self.res["no_partner"]["target_delta_vs_named_partner"], 0.0)

    def test_ledger_scan_counts_are_internally_consistent(self):
        d = self.res["ledger"]
        self.assertLessEqual(d["rows_naming_a_partner"], d["evaluation_rows_total"])
        self.assertLessEqual(d["distinct_partner_slots"], d["named_partner_slots"])
        self.assertGreaterEqual(d["max_separations_of_one_pair"], 1)

    def test_render_does_not_overclaim(self):
        text = probe.render(self.res)
        # The renderer must print the measured difference, not a word like
        # "proves". These are wording guards, not style preferences: the whole
        # point of the report is that a field named "compare" did not compare.
        self.assertIn("identity not read", text)
        self.assertNotIn("証明", text)

    def test_probe_writes_nothing(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        probe.run("Q-003", ROOT)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)

    def test_probe_does_not_modify_the_engine_on_disk(self):
        src = (ROOT / "tools" / "belief_state.py").read_bytes()
        probe.run("Q-003", ROOT)
        self.assertEqual(src, (ROOT / "tools" / "belief_state.py").read_bytes())

    def test_json_arm_is_serialisable(self):
        json.dumps(self.res, ensure_ascii=False)

    def test_unknown_question_is_rejected(self):
        with self.assertRaises(SystemExit):
            probe.run("Q-00000000-nosuch", ROOT)


if __name__ == "__main__":
    unittest.main()
