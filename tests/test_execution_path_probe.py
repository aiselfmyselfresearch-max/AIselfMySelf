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
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import execution_path_probe as probe  # noqa: E402

GIT = shutil.which("git") is not None

# HYP-20261113-17ea95's scope_conditions name exactly these three checks.
SCOPE_NAMED = {"validate_seed", "append_only_check", "belief_state_map"}


def _state_snapshot() -> dict[Path, tuple[int, int]]:
    """Identity of every ledger file: mtime and size, base files and shards."""
    return {p: (p.stat().st_mtime_ns, p.stat().st_size) for p in (ROOT / "state").rglob("*.jsonl")}


class ExecutionPathProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One sweep serves every test below, including the "does it write?"
        # checks: each of those used to re-run a second 15 s sweep to compare
        # before/after. The hash is taken once, around the sweep that already
        # exists, so the claim ("the probe writes nothing") is unchanged and the
        # measurement is not paid twice (2026-11-23).
        tmp = Path(tempfile.gettempdir())
        cls.sandboxes_before = set(tmp.glob("execpath-*"))
        cls.state_before = _state_snapshot()
        cls.engine_before = (ROOT / "tools" / "inspect_inquiry.py").read_bytes()
        cls.res = probe.run(ROOT)
        cls.state_after = _state_snapshot()
        cls.sandboxes_after = set(tmp.glob("execpath-*"))
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
        self.assertEqual(self.state_before, self.state_after)

    def test_probe_leaves_the_engine_on_disk_unchanged(self):
        self.assertEqual(self.engine_before,
                         (ROOT / "tools" / "inspect_inquiry.py").read_bytes())

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
        """Every per-intervention sandbox is removed; only the cached template stays.

        The template is one committed sandbox kept for the next run() call -- the
        alternative was committing one per intervention (1.1 s x 11). What this
        test pinned before 2026-11-23 ("no sandbox outlives the sweep") still
        holds for every sandbox the sweep itself creates.
        """
        leftovers = self.sandboxes_after - self.sandboxes_before
        self.assertLessEqual(len(leftovers), 1, f"unexpected sandboxes: {leftovers}")
        if leftovers:
            self.assertEqual(leftovers, {probe._TEMPLATE[1]})

    def test_the_template_is_one_committed_sandbox_not_one_per_intervention(self):
        """The baseline commit is paid once, and every sandbox still starts from it."""
        self.assertEqual(len(self.res["interventions"]), 11)
        self.assertIsNotNone(probe._TEMPLATE)
        self.assertTrue((probe._TEMPLATE[1] / ".git").is_dir())

    def test_in_process_checks_and_packets_match_the_subprocess_path(self):
        """The speed-up must not change what is measured.

        Both the checks and the packet used to be child processes. They are now
        run in this interpreter against the sandbox (see the probe's docstring).
        This pins the two paths equal on one sandbox: same seven exit codes, same
        packet bytes. Without it a refactor could report "nothing noticed" while
        the check it replaced would have failed.
        """
        sb = probe.make_sandbox(ROOT)
        try:
            probe.commit_baseline(sb)
            slow = probe.run_checks(sb, in_process=False)
            fast = probe.run_checks(sb, in_process=True)
            self.assertEqual({k: v["exit"] for k, v in slow.items()},
                             {k: v["exit"] for k, v in fast.items()})
            for target in ("Q-003", "auto"):
                with self.subTest(target=target):
                    old, old_rc = probe._render_packet(sb, target, probe.BASE_SEED, in_process=False)
                    new, new_rc = probe._render_packet(sb, target, probe.BASE_SEED, in_process=True)
                    self.assertEqual((old_rc, old), (new_rc, new))
        finally:
            shutil.rmtree(sb, ignore_errors=True)

    def test_the_in_process_path_survives_a_polluted_interpreter(self):
        """The host's copies of the tools must not leak into a sandbox run.

        The suite imports ``inspect_inquiry`` and its neighbours from THIS
        checkout before this module runs. While that was left in ``sys.modules``,
        the in-process path measured the live ledger and the live defaults, the
        four packet interventions reported "no change", and the I3 positive
        control lost one of its two flipped detectors -- all only when run under
        the suite, never from the CLI (measured 2026-11-23). The comparison is
        against the subprocess path, so the assertion is about equivalence, not
        about a recorded string.
        """
        import importlib

        importlib.import_module("inspect_inquiry")  # the polluting import, on purpose
        sb = probe.make_sandbox(ROOT)
        try:
            probe.commit_baseline(sb)
            old, old_rc = probe._render_packet(sb, "Q-003", probe.BASE_SEED, in_process=False)
            new, new_rc = probe._render_packet(sb, "Q-003", probe.BASE_SEED, in_process=True)
            self.assertEqual((old_rc, old), (new_rc, new))
        finally:
            shutil.rmtree(sb, ignore_errors=True)

    def test_the_sweep_runs_interventions_side_by_side(self):
        """Parallel measurement is the default, and it is equivalent to serial.

        One intervention per worker over independent sandboxes; the comparison
        against the control is done afterwards, in declaration order, so the
        report is the same object either way.
        """
        self.assertGreaterEqual(probe.default_jobs(), 1)
        serial = probe.run(ROOT, only="P1_window", jobs=1)
        parallel = probe.run(ROOT, only="P1_window", jobs=2)
        self.assertEqual(serial["interventions"].keys(), parallel["interventions"].keys())
        self.assertEqual(
            {k: v["checks_flipped"] for k, v in serial["interventions"].items()},
            {k: v["checks_flipped"] for k, v in parallel["interventions"].items()},
        )
        self.assertEqual(serial["interventions"]["P1_window"]["packet"]["sha256"],
                         parallel["interventions"]["P1_window"]["packet"]["sha256"])

    def test_cli_json_and_exit_zero(self):
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "execution_path_probe.py"),
                            "--only", "I0_control", "--json"],
                           capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("I0_control", json.loads(p.stdout)["interventions"])


if __name__ == "__main__":
    unittest.main()
