"""Tests for tools/boundary_channel_probe.py.

These assert MECHANISMS (which field the engine reads, which relation admits a
flag), never the direction of a live-ledger metric. SESSION-20261114-a6beb7e6
learned that the hard way: a test asserting that Q-003's KL must rise when a child
is added failed on main when an upstream evaluation moved the leader, and had to
be rewritten. Live KL and generation mass are not stable enough to gate on.

The invariants here are structural and hold regardless of what the ledger says:
  * the direct penalty depends on the ADDRESS, not on the row's content;
  * the 1-hop channel changes visibility but never log-odds;
  * the probe writes nothing.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402
import boundary_channel_probe as probe  # noqa: E402

TARGET = "HYP-20261113-ccc1d8"
QUESTION = "Q-003"


class BoundaryChannelProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cols = bs.load_belief_ledgers(ROOT)
        cls.base = bs.compute_belief_state(copy.deepcopy(cls.cols))
        cls.res = probe.run(TARGET, QUESTION, ROOT)

    def _delta(self, rec):
        c = copy.deepcopy(self.cols)
        c["errata"][rec["errata_id"]] = rec
        st = bs.compute_belief_state(c)
        b = probe._hyp(self.base, QUESTION, TARGET)
        a = probe._hyp(st, QUESTION, TARGET)
        return a["log_odds"] - b["log_odds"], a["errata_flags"]

    def test_target_and_rival_exist_and_share_a_question(self):
        for hid in (TARGET, probe.DEFAULT_RIVAL):
            self.assertIn(hid, self.cols["hypotheses"])
            self.assertIn(QUESTION, self.cols["hypotheses"][hid]["question_ids"])

    def test_address_decides_the_direct_penalty(self):
        """Same content on the hypothesis costs; on a bystander tool costs nothing."""
        judged, jf = self._delta(probe.errata_row(TARGET, "hypothesis"))
        bystander, bf = self._delta(probe.errata_row("tools/belief_state.py", "tool"))
        self.assertLess(judged, 0.0)
        self.assertEqual(bystander, 0.0)
        self.assertEqual(len(jf), 1)
        self.assertEqual(bf, [])

    def test_direct_penalty_now_reads_verdict_and_status(self):
        """The engine reads verdict/status; this test used to assert that it did not.

        SESSION-20261114-11d148 measured the old uniformity and filed it as
        ERR-20261114-9a6fb1. The previous version of this test asserted the defect
        on purpose ("so that a future fix trips this test and forces the fix to be
        recorded rather than silent"). It tripped. This is that record.

        A correction costs weight only while it still asserts an error: verdict
        `contradicted` and status not `withdrawn`. A withdrawn correction, one whose
        check found the claim HELD, and one that could not be measured remain
        visible in errata_flags but no longer move the belief.
        """
        for verdict in ("contradicted", "holds", "unmeasurable"):
            for status in ("open", "annotated", "withdrawn"):
                with self.subTest(verdict=verdict, status=status):
                    d, flags = self._delta(probe.errata_row(TARGET, "hypothesis",
                                                            verdict=verdict, status=status))
                    should_pay = verdict == "contradicted" and status != "withdrawn"
                    if should_pay:
                        self.assertLess(d, 0.0)
                    else:
                        self.assertEqual(d, 0.0)
                    # Visibility is not gated: every row stays flagged.
                    self.assertEqual(len(flags), 1)

    def test_unknown_status_does_not_escape_the_penalty(self):
        """Two legacy rows carry status `corrected`, outside the schema enum.

        An unrecognised status must not become a way to dodge the weight: only the
        explicitly named `withdrawn` discounts a live contradiction.
        """
        d, _ = self._delta(probe.errata_row(TARGET, "hypothesis", status="corrected"))
        self.assertLess(d, 0.0)

    def test_penalty_scales_with_distinct_claims_not_row_count(self):
        """One claim costs one penalty; k distinct claims cost k.

        Renamed from test_penalty_scales_with_row_count_not_distinct_claims, which
        asserted that k *identical* rows cost k x one row. That was the defect: the
        weight measured how many times a claim was written down, so copying a row
        deepened the penalty. It is the errata analogue of the evaluation asymmetry
        recorded in readings/2026-11-14-two-hypotheses-that-were-not-competing.md
        §6-1. The old assertion tripped when the engine was fixed; this is the
        record of that change, not a silenced guard.
        """
        base_h = probe._hyp(self.base, QUESTION, TARGET)
        one_row, _ = self._delta(probe.errata_row(TARGET, "hypothesis"))
        self.assertLess(one_row, 0.0)
        for k in (1, 2, 3):
            with self.subTest(identical_rows=k):
                c = copy.deepcopy(self.cols)
                for i in range(k):
                    c["errata"][f"ERR-PROBE-{i}"] = probe.errata_row(
                        TARGET, "hypothesis", errata_id=f"ERR-PROBE-{i}")
                h = probe._hyp(bs.compute_belief_state(c), QUESTION, TARGET)
                d = h["log_odds"] - base_h["log_odds"]
                self.assertAlmostEqual(d, one_row, places=6,
                                       msg=f"{k} identical rows are one claim, not {k}")
                self.assertEqual(len(h["errata_flags"]), k,
                                 "every row must stay visible even when collapsed")
        for k in (1, 2, 3):
            with self.subTest(distinct_claims=k):
                c = copy.deepcopy(self.cols)
                for i in range(k):
                    c["errata"][f"ERR-PROBE-{i}"] = probe.errata_row(
                        TARGET, "hypothesis", errata_id=f"ERR-PROBE-{i}",
                        claim=f"独立した検定 {i}。異なる主張。")
                h = probe._hyp(bs.compute_belief_state(c), QUESTION, TARGET)
                d = h["log_odds"] - base_h["log_odds"]
                self.assertAlmostEqual(d, k * one_row, places=6,
                                       msg=f"{k} distinct claims should cost {k}x one row")

    def test_one_hop_channel_changes_visibility_never_weight(self):
        """Across all three admission rules, log-odds is identical; only flags move."""
        arm = self.res["arms"]["rule_powered"]
        self.assertIn("via_supports_evaluation", arm)
        for tag, per_rule in arm.items():
            deltas = {round(v["d_log_odds"], 6) for v in per_rule.values()}
            self.assertEqual(deltas, {0.0}, f"{tag}: 1-hop altered log-odds")
        sup = arm["via_supports_evaluation"]
        self.assertEqual(sup["closed"]["errata_flags"], [])
        self.assertEqual(len(sup["current"]["errata_flags"]), 1)

    def test_widening_the_rule_admits_a_narrowing_evaluation(self):
        nar = self.res["arms"]["rule_powered"]["via_narrows_evaluation"]
        self.assertEqual(nar["current"]["errata_flags"], [])
        self.assertEqual(len(nar["widened"]["errata_flags"]), 1)

    def test_mix_arm_holds_row_count_fixed(self):
        arm = self.res["arms"]["mix"]
        counts = {v["evaluation_rows_held_fixed"] for v in arm.values()}
        self.assertEqual(len(counts), 1)
        self.assertGreater(next(iter(counts)), 0)

    def test_mix_arm_moves_weight_so_selection_is_not_inert(self):
        """Selection rules DO govern weight in the evaluation channel.

        Asserts only that the mix matters, not which mix wins or by how much.
        """
        arm = self.res["arms"]["mix"]
        kls = {round(v["kl_bits"], 4) for v in arm.values()}
        self.assertGreater(len(kls), 1, "verdict mix had no effect on the distribution")

    def test_content_arm_now_separates_live_from_spent_corrections(self):
        """Content used to be invisible to the penalty; now verdict/status matter.

        Renamed from test_content_arm_is_uniform_because_the_branch_is_blind, which
        asserted the defect. The arm holds the address fixed and varies only the
        judgement, so it is exactly the measurement that shows the fix works.
        """
        arm = self.res["arms"]["content"]
        vals = {round(v["d_log_odds"], 6) for v in arm.values()}
        self.assertGreater(len(vals), 1, "verdict/status still ignored by the penalty")
        for label, val in arm.items():
            with self.subTest(arm=label):
                live = label in ("contradicted_open", "contradicted_annotated")
                if live:
                    self.assertLess(val["d_log_odds"], 0.0)
                else:
                    self.assertEqual(val["d_log_odds"], 0.0)

    def test_direct_branch_is_latent_on_the_live_ledger(self):
        d = self.res["direct_penalty_branch"]
        self.assertEqual(d["live_hypotheses_with_a_direct_errata_row"], 0)
        self.assertGreater(d["live_errata_rows"], 0)

    def test_probe_writes_nothing(self):
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        probe.run(TARGET, QUESTION, ROOT)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)

    def test_rule_variant_does_not_modify_the_engine_on_disk(self):
        src = (ROOT / "tools" / "belief_state.py").read_bytes()
        probe.run(TARGET, QUESTION, ROOT)
        self.assertEqual(src, (ROOT / "tools" / "belief_state.py").read_bytes())

    def test_unknown_target_is_rejected(self):
        with self.assertRaises(SystemExit):
            probe.run("HYP-00000000-nosuch", QUESTION, ROOT)

    def test_cli_json_and_exit_zero(self):
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "boundary_channel_probe.py"),
                            "--arm", "position", "--json"],
                           capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertIn("position", data["arms"])

    def test_guard_fires_if_the_engine_line_changes(self):
        with self.assertRaises(RuntimeError):
            probe._with_rule("current", "# engine rewritten\n")


if __name__ == "__main__":
    unittest.main()
