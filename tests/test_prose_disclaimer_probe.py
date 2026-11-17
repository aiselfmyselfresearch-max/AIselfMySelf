"""Regression tests for tools/prose_disclaimer_probe.py.

The probe counts rows whose **prose about a comparison partner disagrees with
the field that names one**. Two separate claims are pinned:

1. **The scan is a lower bound, not a census.** Japanese negation is not
   regular; the patterns in the tool miss many ways of saying "this is not my
   opponent". A test that demanded coverage would be wrong. What is pinned is
   that the tool reports candidate counts and prints context, so a reader can
   reject a false positive by eye.

2. **The one live row it found is correct for the wrong reason.** This is the
   finding, so it is pinned against the live ledger: ``EVL-20261113-06b38d``
   says its named partner's value "does not move in this row", and that is
   true — because it is a ``narrows_scope`` row, where *no* partner moves.

A synthetic test pins the disagreement shape independently of the archive.

See readings/2026-11-17-the-prose-is-right-and-the-mechanism-is-wrong.md §5.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state
import prose_disclaimer_probe as probe


def _hyp(hid):
    return {
        "hypothesis_id": hid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-10T00:00:00Z",
        "question_ids": ["Q-QA"],
        "title": hid,
        "proposition": hid,
        "scope_conditions": ["test"],
        "exclusion_clause": "test",
        "lineage_op": "root",
        "parent_hypothesis_ids": [],
        "status": "active",
    }


def _evl(eid, target, partners, summary, verdict="narrows_scope"):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": "2026-11-12T00:00:00Z",
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": "reproducible_script",
        "summary": summary,
        "compared_against_hypothesis_ids": list(partners),
        "material_ids": [],
        "note_ids": [],
    }


def _ledger(summary, partners, verdict="narrows_scope"):
    return {
        "questions": {},
        "hypotheses": {h: _hyp(h) for h in ("H-A", "H-B", "H-C")},
        "evaluations": {"E-1": _evl("E-1", "H-A", partners, summary, verdict)},
        "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
        "errata": {}, "hypothesis_read_log": {},
    }


DISCLAIM = "この行では H-B とは排他的でない（比較対象には入れない）。"
ASSERT = "H-B と衝突するが、H-C とは別の層である。"


class ScanShapeSyntheticTests(unittest.TestCase):
    def test_a_disclaimer_with_a_named_partner_is_flagged(self):
        cols = _ledger(DISCLAIM, ["H-B"])
        hits = probe.scan(cols)
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0]["disclaimed_partner"])
        self.assertEqual(hits[0]["partner_hypothesis_ids"], ["H-B"])

    def test_a_disclaimer_with_no_partner_is_not_flagged_as_disclaiming(self):
        # Nothing was named, so nothing can be disclaimed. The pattern still
        # matches, but `disclaimed_partner` must be False.
        cols = _ledger(DISCLAIM, [])
        hits = probe.scan(cols)
        self.assertEqual(len(hits), 1)
        self.assertFalse(hits[0]["disclaimed_partner"])

    def test_a_plain_prose_is_not_flagged(self):
        cols = _ledger("この行は H-B を支持する。", ["H-B"])
        self.assertEqual(probe.scan(cols), [])

    def test_an_assertion_is_reported_separately_from_a_disclaimer(self):
        cols = _ledger(ASSERT, ["H-B"])
        hits = probe.scan(cols)
        self.assertEqual(len(hits), 1)
        kinds = {m["kind"] for m in hits[0]["matches"]}
        self.assertEqual(kinds, {"assertion"})
        self.assertFalse(hits[0]["disclaimed_partner"])

    def test_context_is_printed_so_a_false_positive_can_be_rejected(self):
        cols = _ledger(DISCLAIM, ["H-B"])
        hits = probe.scan(cols)
        self.assertTrue(hits[0]["matches"][0]["context"])
        self.assertIn("H-B", hits[0]["matches"][0]["context"])

    def test_a_disclaimer_moves_nothing_on_a_narrowing_row(self):
        # The whole point of §5: the prose is right, and it is right because the
        # verdict deducts nothing, not because the row told the engine to skip.
        cols = _ledger(DISCLAIM, ["H-B"])
        measured = probe.measure(cols, probe.scan(cols))
        partner = [d for d in measured[0]["deltas"].values() if d["kind"] == "partner"]
        self.assertEqual(len(partner), 1)
        self.assertAlmostEqual(partner[0]["effect_of_the_name"], 0.0, places=12)
        target = [d for d in measured[0]["deltas"].values() if d["kind"] == "target"]
        self.assertNotAlmostEqual(target[0]["effect_of_the_name"], 0.0, places=9)

    def test_the_same_disclaimer_does_move_the_partner_on_a_supporting_row(self):
        cols = _ledger(DISCLAIM, ["H-B"], verdict="supports")
        measured = probe.measure(cols, probe.scan(cols))
        partner = [d for d in measured[0]["deltas"].values() if d["kind"] == "partner"]
        self.assertLess(partner[0]["effect_of_the_name"], 0.0,
                        "on a supporting row the named partner carries a deduction")

    def test_render_does_not_overclaim(self):
        cols = _ledger(DISCLAIM, ["H-B"])
        text = probe.render(probe.summarize(cols, probe.scan(cols),
                                           probe.measure(cols, probe.scan(cols))))
        self.assertIn("DISCLAIMS a named partner", text)
        self.assertNotIn("証明", text)


class LiveLedgerArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cols = belief_state.load_belief_ledgers(ROOT)
        cls.hits = probe.scan(cls.cols)
        cls.res = probe.summarize(cls.cols, cls.hits, [])

    def test_the_scan_is_a_lower_bound_below_ten_percent(self):
        # Measured 2026-11-17: 31 of 530 rows use an opposition word. The bound
        # is stated as a fraction because the ledger grows every session; the
        # claim is "almost none", not "thirty-one".
        share = self.res["rows_matching_a_pattern"] / self.res["evaluation_rows"]
        self.assertLess(share, 0.10)

    def test_the_disclaimed_partner_rows_stay_a_handful(self):
        # The scan is a lower bound on purpose (§5, ERR-20261117-e5777c among
        # them is known to be a false positive: it disclaims a hypothesis the
        # field does not name). What is pinned is that the count stays a handful
        # of rows, not that it stays exactly one: a later session may write
        # another, and that would be a fact about the ledger, not a regression.
        claimed = [h for h in self.hits if h["disclaimed_partner"]]
        self.assertLessEqual(len(claimed), 3)
        self.assertIn("EVL-20261113-06b38d", [h["evaluation_id"] for h in claimed])

    def test_that_row_is_a_narrowing_row_so_its_prose_is_right_by_accident(self):
        state = belief_state.compute_belief_state(copy.deepcopy(self.cols))
        row = state["questions"]
        found = None
        for q in row.values():
            for h in q["hypotheses"]:
                if h["hypothesis_id"] == "HYP-20261112-46456a":
                    found = h
        self.assertIsNotNone(found)
        evl = self.cols["evaluations"]["EVL-20261113-06b38d"]
        self.assertEqual(evl["verdict"], "narrows_scope")
        clipped = copy.deepcopy(self.cols)
        clipped["evaluations"]["EVL-20261113-06b38d"]["compared_against_hypothesis_ids"] = []
        after = belief_state.compute_belief_state(clipped)
        moved = None
        for q in after["questions"].values():
            for h in q["hypotheses"]:
                if h["hypothesis_id"] == "HYP-20261112-46456a":
                    moved = h["log_odds"]
        self.assertAlmostEqual(found["log_odds"], moved, places=12)

    def test_probe_writes_nothing(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        probe.run(ROOT)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
