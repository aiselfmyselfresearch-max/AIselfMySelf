"""Tests for tools/execution_path_probe.py.

Assert MECHANISMS, never the direction of a live-ledger metric. Two earlier
sessions learned this the hard way: a test asserting that Q-003's KL must rise
failed on main when an upstream evaluation moved the leader. Live KL, posteriors
and rankings are not stable enough to gate on.

The important test here is the POSITIVE CONTROL. A probe reporting "no check
noticed" is only meaningful if the same checks DO notice a real content change.
Without that control, a broken detector and a content-only detector look alike.

The full nine-intervention sweep costs ~45s, so the class-level fixture runs it
once and the assertions read that result.
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
