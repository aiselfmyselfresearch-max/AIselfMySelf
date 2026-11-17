"""Tests for tools/verdict_order_probe.py.

The probe exists because the engine applies a directed pair's rows in *id* order,
never in ``created_at`` order, and 46% of the ledger's rows carry a date without
a time. Two claims are pinned separately:

1. **The engine's sum does not depend on iteration order today.** A test that
   broke here would mean a change made the dict order load-bearing, which is the
   thing the probe exists to detect (and would be a measurement, not a bug).
2. **Orderability is a property of the ledger, not of the probe.** The counts are
   pinned as relations (placeable + not placeable = conflicting), so the test
   survives the ledger growing without pretending the numbers are frozen.

A synthetic test pins the counting logic; the live arm pins the shape.

See readings/2026-11-18-the-three-debts-and-the-one-that-bends.md §4.
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
import verdict_order_probe as probe


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


def _evl(eid, target, partners, verdict, stamp):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": stamp,
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": "reproducible_script",
        "summary": "synthetic row for the order probe",
        "compared_against_hypothesis_ids": list(partners),
        "material_ids": [],
        "note_ids": [],
    }


def _ledger(rows):
    return {"questions": {}, "hypotheses": {h: _hyp(h) for h in ("H-A", "H-B", "H-C")},
            "evaluations": {r["evaluation_id"]: r for r in rows},
            "materials": {}, "fragments": {}, "sessions": {}, "notes": {},
            "errata": {}, "hypothesis_read_log": {}}


class CountingSyntheticTests(unittest.TestCase):
    def test_two_verdicts_on_one_direction_are_counted_as_conflicting(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-A", ["H-B"], "narrows_scope", "2026-11-12T02:00:00Z"),
        ])
        res = probe.orderable_pairs(cols)
        self.assertEqual(res["conflicting_pairs"], 1)
        self.assertEqual(res["strictly_ordered_by_time"], 1)
        self.assertEqual(res["not_placeable_in_time"], 0)

    def test_a_date_only_row_makes_the_pair_unplaceable(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12"),
            _evl("E-2", "H-A", ["H-B"], "narrows_scope", "2026-11-12T02:00:00Z"),
        ])
        res = probe.orderable_pairs(cols)
        self.assertEqual(res["not_placeable_in_time"], 1)
        self.assertEqual(res["strictly_ordered_by_time"], 0)

    def test_two_rows_with_the_same_stamp_are_a_tie(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-A", ["H-B"], "narrows_scope", "2026-11-12T01:00:00Z"),
        ])
        res = probe.orderable_pairs(cols)
        self.assertEqual(res["tied_on_the_same_stamp"], 1)
        self.assertEqual(res["strictly_ordered_by_time"], 0)

    def test_a_single_verdict_pair_is_not_decided_by_time(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "refutes_unconditioned", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-A", ["H-B"], "refutes_unconditioned", "2026-11-12T02:00:00Z"),
        ])
        res = probe.time_decided_counterfactual(cols)
        self.assertEqual(res["pairs_decidable_by_time"], 0)
        self.assertEqual(res["rows_suppressed"], 0)

    def test_later_verdict_wins_suppresses_the_earlier_row(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-A", ["H-B"], "narrows_scope", "2026-11-12T02:00:00Z"),
        ])
        res = probe.time_decided_counterfactual(cols)
        self.assertEqual(res["pairs_decidable_by_time"], 1)
        self.assertEqual(res["suppressed_evaluation_ids"], ["E-1"])

    def test_one_verdict_only_is_not_conflicting(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-A", ["H-B"], "supports", "2026-11-12T02:00:00Z"),
        ])
        self.assertEqual(probe.orderable_pairs(cols)["conflicting_pairs"], 0)

    def test_the_other_direction_is_a_different_pair(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12T01:00:00Z"),
            _evl("E-2", "H-B", ["H-A"], "narrows_scope", "2026-11-12T02:00:00Z"),
        ])
        self.assertEqual(probe.orderable_pairs(cols)["conflicting_pairs"], 0)

    def test_granularity_counts(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12"),
            _evl("E-2", "H-A", ["H-C"], "supports", "2026-11-12T02:00:00Z"),
        ])
        g = probe.stamp_granularity(cols)
        self.assertEqual(g["date_only"], 1)
        self.assertEqual(g["with_a_time"], 1)
        self.assertAlmostEqual(g["share_date_only"], 0.5, places=6)

    def test_the_probe_says_the_engine_does_not_weight_by_time(self):
        # This is a claim about the engine, checked against the engine's own
        # source rather than against a number: if a session ever adds a time
        # term, this test should fail and §4 of the report should be rewritten.
        src = (TOOLS / "belief_state.py").read_text(encoding="utf-8")
        body = src[src.index("def compute_belief_state"):src.index("def separation_counts")]
        weight_block = body[:body.index("Separation bookkeeping for the audit columns")]
        self.assertNotIn('evl.get("created_at")', weight_block)

    def test_render_does_not_promise_an_ordering_fix(self):
        cols = _ledger([
            _evl("E-1", "H-A", ["H-B"], "supports", "2026-11-12"),
            _evl("E-2", "H-A", ["H-B"], "narrows_scope", "2026-11-12T02:00:00Z"),
        ])
        text = probe.render({
            "rows": probe.stamp_granularity(cols),
            "orderable": probe.orderable_pairs(cols),
            "time_decided": probe.time_decided_counterfactual(cols),
            "engine_reads_created_at_for_weight": False,
        })
        self.assertIn("not placeable in time", text)
        self.assertIn("IF EACH ORDERABLE PAIR WERE DECIDED BY DATE", text)
        # The rendered footer must refuse the fix, not merely avoid the topic.
        self.assertIn("とは言わない", text)
        self.assertIn("順序を持たない行が残る", text)
        self.assertIn("ソートでは実装できない", text)


class LiveLedgerArmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cols = bs.load_belief_ledgers(ROOT)
        cls.res = probe.run(ROOT)


    def test_placeable_and_unplaceable_add_up(self):
        o = self.res["orderable"]
        self.assertEqual(o["conflicting_pairs"],
                         o["strictly_ordered_by_time"] + o["tied_on_the_same_stamp"]
                         + o["not_placeable_in_time"])

    def test_a_large_share_of_rows_cannot_be_ordered(self):
        # The number is not pinned; the *claim* is, because §4 rests on it: an
        # ordering fix would leave a large block of rows unordered. If this ever
        # drops below 10%, the argument in §4 has to be rewritten.
        self.assertGreater(self.res["rows"]["share_date_only"], 0.10)

    def test_decidable_pairs_never_exceed_conflicting_pairs(self):
        # A first draft used `verdicts < CONFLICT`, which is a *proper subset*
        # test, so pairs carrying only refutes_unconditioned were counted as
        # orderable (25 of 71 instead of 17). Pin the invariant.
        t = self.res["time_decided"]
        self.assertLessEqual(t["pairs_decidable_by_time"], t["pairs_carried_both_verdicts"])

    def test_suppressing_rows_actually_moves_the_map(self):
        # The counterfactual must not be vacuous. If this ever reads 0, the
        # suppression path is broken and the probe is reporting nothing while
        # looking like it measured something (the reverse-id draft's failure).
        t = self.res["time_decided"]
        self.assertGreater(t["rows_suppressed"], 0)
        self.assertGreater(t["max_abs_dP"], 0.0)
        self.assertGreater(t["hypotheses_moved"], 0)

    def test_the_engine_reads_no_order_at_all(self):
        # The counterfactual can only exist if the engine is order-independent;
        # otherwise "created_at order" would already be partly implemented by
        # iteration order. Re-keying ids in reverse changes nothing.
        flipped = copy.deepcopy(self.cols)
        keys = sorted(flipped["evaluations"].keys(), reverse=True)
        flipped["evaluations"] = {k: flipped["evaluations"][k] for k in keys}
        a = bs.compute_belief_state(copy.deepcopy(self.cols))
        b = bs.compute_belief_state(flipped)
        pa = {(q, h["hypothesis_id"]): h["posterior"]
              for q, v in a["questions"].items() for h in v["hypotheses"]}
        pb = {(q, h["hypothesis_id"]): h["posterior"]
              for q, v in b["questions"].items() for h in v["hypotheses"]}
        self.assertEqual(pa, pb)

    def test_probe_writes_nothing(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        probe.run(ROOT)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
