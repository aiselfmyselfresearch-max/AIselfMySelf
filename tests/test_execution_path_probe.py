"""Tests for tools/execution_path_probe.py.

Assert MECHANISMS, never the direction of a live-ledger metric. Two earlier
sessions learned this the hard way: a test asserting that Q-003's KL must rise
failed on main when an upstream evaluation moved the leader. Live KL, posteriors
and rankings are not stable enough to gate on.

The important test here is the POSITIVE CONTROL. A probe reporting "no check
noticed" is only meaningful if the same checks DO notice a real content change.
Without that control, a broken detector and a content-only detector look alike.

The full eleven-intervention sweep costs ~140s, so the class-level fixture runs it
once and the assertions read that result.

Three assertions below are about the INSTRUMENT rather than about the ledger, and
they exist because the instrument was twice found to under-report what would have
falsified the hypothesis it was built to test: it omitted one of the three checks
its own docstring names, and it pinned the dispersal seed to a literal so that the
largest execution-path parameter could not appear at all. A test that pins the
named-check set and the seed parameterisation is what keeps those two defects from
returning silently.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import execution_path_probe as probe  # noqa: E402

GIT = shutil.which("git") is not None

# HYP-20261113-17ea95's scope_conditions name exactly these three checks.
SCOPE_NAMED = {"validate_seed", "append_only_check", "belief_state_map"}


class ExecutionPathProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = probe.run(ROOT)
        cls.iv = cls.res["interventions"]

    def test_baseline_is_all_green(self):
        """If the untouched control fails, every flip below is confounded."""
        self.assertTrue(self.res["baseline_all_pass"],
                        f"confounded baseline: {self.res['baseline']}")

    def test_control_changes_nothing(self):
        c = self.iv["I0_control"]
        self.assertTrue(c["union_identical"])
        self.assertFalse(c["packet_changed"])
        self.assertEqual(c["checks_flipped"], [])

    def test_storage_interventions_preserve_every_ledger_line(self):
        """Path-only means the row multiset size never changes."""
        for name in ("I1_split_shard", "I2_rename_suffix", "I3_future_date", "I4_lower_cap"):
            with self.subTest(intervention=name):
                self.assertTrue(self.iv[name]["line_counts_identical"])

    def test_named_checks_never_notice_a_path_only_change(self):
        """The three checks in the hypothesis's own scope stay invariant.

        This is where limb (b) does NOT fire, and it is the finding that counts
        against the probe author's expectation.
        """
        for name, v in self.iv.items():
            with self.subTest(intervention=name):
                self.assertEqual(v["named_checks_flipped"], [],
                                 f"{name} moved a scope-named check")

    def test_checks_that_flip_are_only_the_unnamed_ones(self):
        for name, v in self.iv.items():
            for k in v["checks_flipped"]:
                with self.subTest(intervention=name, check=k):
                    self.assertEqual(self.res["baseline"][k]["kind"], "other")

    def test_forged_date_is_caught_positive_control(self):
        """A path change that SHOULD be caught is caught, so detectors work."""
        v = self.iv["I3_future_date"]
        self.assertIn("date_axis_shards", v["checks_flipped"])

    def test_lowered_cap_is_caught_positive_control(self):
        v = self.iv["I4_lower_cap"]
        self.assertIn("size_budget_strict", v["checks_flipped"])
        self.assertTrue(v["union_identical"], "cap change must not touch rows")

    def test_packet_knobs_change_what_the_next_reader_receives(self):
        for name in ("P1_window", "P2_limit", "P3_budget", "P4_order"):
            with self.subTest(intervention=name):
                v = self.iv[name]
                self.assertTrue(v["packet_changed"])
                self.assertEqual(v["packet"]["exit"], 0, "packet must still render")
                self.assertGreater(v["packet"]["bytes"], 0)

    def test_packet_knobs_are_invisible_to_every_check(self):
        for name in ("P1_window", "P2_limit", "P3_budget", "P4_order"):
            with self.subTest(intervention=name):
                self.assertEqual(self.iv[name]["checks_flipped"], [])

    def test_anticorrelation_between_packet_change_and_detection(self):
        """No intervention both changes the packet and trips a check.

        Stated as a property of this measurement, not a law: a future check that
        reads packet knobs would falsify it, and that is the point of recording it.
        """
        for name, v in self.iv.items():
            with self.subTest(intervention=name):
                self.assertFalse(v["packet_changed"] and bool(v["checks_flipped"]),
                                 f"{name} both reached the reader and was detected")

    def test_scope_named_check_set_is_complete(self):
        """The probe must run every check the hypothesis names, not a subset.

        Until 2026-11-14 ``append_only_check`` appeared in this file's subject
        hypothesis and in the probe's own docstring but not in probe.CHECKS, so
        limb (b) had been scored against 2 of 3 named checks. An instrument that
        omits a member of the set its claim is about can only under-report a
        refutation. This asserts the SET, never any check's exit status.
        """
        named = {n for n, _, kind in probe.CHECKS if kind == "named_in_scope"}
        self.assertEqual(named, SCOPE_NAMED)
        self.assertEqual({n for n, _, _ in probe.CHECKS} - named,
                         {"size_budget_strict", "date_axis_shards", "note_index",
                          "learning_metrics"})

    @unittest.skipUnless(GIT, "git is required to give the sandbox a baseline revision")
    def test_append_only_check_actually_runs_in_the_sandbox(self):
        """A check that cannot run is not a check that found nothing.

        ``append_only_check.py`` compares against ``git archive <rev> state``, and
        a plain sandbox copy has no ``.git``, so it exits 2 with CANNOT COMPARE.
        The sandbox therefore commits the pristine ledger first. Asserting the
        baseline exit code here is what stops "no flip" from meaning "never ran".
        """
        for name, v in self.iv.items():
            with self.subTest(intervention=name):
                self.assertTrue(v["baseline_committed"], f"{name} had no git baseline")
        self.assertEqual(self.res["baseline"]["append_only_check"]["exit"], 0)

    def test_seed_is_parameterised_not_pinned(self):
        """The dispersal seed must be a measured axis, not a hardcoded literal."""
        self.assertNotIn(probe.BASE_SEED, probe.ALT_SEEDS)
        self.assertEqual(len(set(probe.ALT_SEEDS)), len(probe.ALT_SEEDS))
        seeds = {name: seed for name, _, _, seed in probe.INTERVENTIONS}
        self.assertEqual({s for s in seeds.values() if s != probe.BASE_SEED},
                         set(probe.ALT_SEEDS))
        self.assertEqual([n for n, f, _, _ in probe.INTERVENTIONS if f == "seed"],
                         ["S1_seed_low", "S2_seed_high"])

    def test_seed_family_never_touches_the_ledger(self):
        """Definitional: a seed change edits no row and no filename.

        This is the control that makes the seed family a PATH intervention rather
        than a content intervention, and it does not depend on the live ledger.
        """
        for name in ("S1_seed_low", "S2_seed_high"):
            with self.subTest(intervention=name):
                v = self.iv[name]
                self.assertTrue(v["union_identical"])
                self.assertTrue(v["line_counts_identical"])
                self.assertEqual(v["file_count_delta"], {})

    def test_seed_family_reaches_the_reader(self):
        """A distinct seed must yield a distinct packet, or the axis is inert."""
        shas = {self.iv[n]["packet"]["sha256"] for n in ("I0_control", "S1_seed_low",
                                                         "S2_seed_high")}
        self.assertEqual(len(shas), 3, "seeds did not produce distinct packets")
        for name in ("S1_seed_low", "S2_seed_high"):
            with self.subTest(intervention=name):
                self.assertTrue(self.iv[name]["packet_changed"])
                self.assertEqual(self.iv[name]["checks_flipped"], [])

    def test_every_record_carries_the_reach_and_rank_columns(self):
        """Guard the keys, not their values: a refactor must not drop a measurement.

        ``auto_target_changed`` is the only column that can show an intervention
        changing WHICH question is answered, and ``hyp_order_identical`` is the only
        one that separates reach from belief ranking. Both were absent before.
        """
        for name, v in self.iv.items():
            with self.subTest(intervention=name):
                for k in ("seed", "baseline_committed", "hyp_order_identical",
                          "packet_auto", "packet_auto_changed", "auto_target_changed"):
                    self.assertIn(k, v)
                for k in ("target", "mode", "role"):
                    self.assertIn(k, v["packet_auto"])

    def test_no_path_intervention_moves_the_belief_ranking(self):
        """Stated as a property of this measurement, not a law.

        Every path intervention moved what the reader receives while leaving the
        §0.2 posterior ranking identical -- which is why limb (a) does not fire:
        the path moves reach, not rank. A future check or knob that reorders the
        ranking would falsify this, and recording it is the point.
        """
        for name, v in self.iv.items():
            with self.subTest(intervention=name):
                self.assertTrue(v["hyp_order_identical"], f"{name} reordered §0.2")

    def test_probe_does_not_write_to_the_repository(self):
        before = {p: p.stat().st_mtime_ns for p in (ROOT / "state").rglob("*.jsonl")}
        probe.run(ROOT, only="I0_control")
        after = {p: p.stat().st_mtime_ns for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)

    def test_sandbox_copies_taxonomy_so_the_control_is_not_stale(self):
        """Omitting taxonomy/ makes note_index report STALE on an untouched copy."""
        self.assertIn("taxonomy", probe.COPY_DIRS)
        sb = probe.make_sandbox(ROOT)
        try:
            self.assertTrue((sb / "taxonomy").is_dir())
        finally:
            shutil.rmtree(sb, ignore_errors=True)

    def test_missing_knob_raises_instead_of_silently_measuring_nothing(self):
        sb = probe.make_sandbox(ROOT)
        try:
            with self.assertRaises(RuntimeError):
                probe._patch(sb, "tools/inspect_inquiry.py", "NO_SUCH_KNOB = 1", "x")
        finally:
            shutil.rmtree(sb, ignore_errors=True)

    def test_sandboxes_are_cleaned_up(self):
        import tempfile
        tmp = Path(tempfile.gettempdir())
        before = set(tmp.glob("execpath-*"))
        probe.run(ROOT, only="I0_control")
        self.assertEqual(set(tmp.glob("execpath-*")) - before, set())

    def test_cli_json_and_exit_zero(self):
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "execution_path_probe.py"),
                            "--only", "I0_control", "--json"],
                           capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("I0_control", json.loads(p.stdout)["interventions"])


if __name__ == "__main__":
    unittest.main()
