"""Regression tests for mirror union repair and backward-compatible load_jsonl."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import errata_audit  # noqa: E402


class MirrorRepairTests(unittest.TestCase):
    def test_errata_load_jsonl_accepts_one_argument_for_neighbors(self) -> None:
        """Calling load_jsonl(name) without id_key must not break drift_audit or reconstruct."""
        frags_union = errata_audit.load_jsonl("fragments.jsonl")
        frags_base = errata_audit.load_jsonl("fragments.jsonl", base_only=True)
        self.assertEqual(len(frags_base), 43)
        self.assertGreater(len(frags_union), len(frags_base))

    def test_drift_and_reconstruct_cli_run_cleanly(self) -> None:
        for script in ("drift_audit.py", "reconstruct.py"):
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / script)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=f"{script} failed: {proc.stderr}")

    def test_json_mirrors_distinguish_union_from_frozen_base(self) -> None:
        json_checks = [
            ("voice_audit.py", lambda d: d["fragment_count"], 43),
            ("address_audit.py", lambda d: d["fragments"], 43),
            ("addressee_audit.py", lambda d: d["collections"]["fragments"]["records"], 43),
            ("gate_audit.py", lambda d: d["materials"], 677),
            ("measure_audit.py", lambda d: d["fragments"]["record_count"], 43),
            ("relation_audit.py", lambda d: d["relation_total"], 874),
            ("selection_audit.py", lambda d: d["fragment_count"], 43),
            ("sense_audit.py", lambda d: d["fragments"], 43),
            ("time_audit.py", lambda d: d["fragments"], 43),
            ("uncertainty_audit.py", lambda d: d["fragment_count"], 43),
        ]
        for script, getter, expected_base in json_checks:
            with self.subTest(script=script):
                u = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / script), "--json"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                b = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / script), "--json", "--base-only"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                du = json.loads(u.stdout)
                db = json.loads(b.stdout)
                self.assertEqual(getter(db), expected_base)
                self.assertGreater(getter(du), expected_base)

    def test_text_mirrors_support_union_and_base_only(self) -> None:
        for script, extra in (
            ("breath_meter.py", []),
            ("measure_texture.py", []),
            ("provenance_audit.py", []),
            ("revision_audit.py", ["--check-session-034"]),
            ("roundtrip_audit.py", []),
            ("translation_audit.py", []),
        ):
            with self.subTest(script=script):
                u = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / script), *extra],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                b = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / script), "--base-only", *extra],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(u.returncode, 0, msg=u.stderr)
                self.assertEqual(b.returncode, 0, msg=b.stderr)


if __name__ == "__main__":
    unittest.main()
