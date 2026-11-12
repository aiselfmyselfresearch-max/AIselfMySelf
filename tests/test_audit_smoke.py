#!/usr/bin/env python3
"""Smoke tests: the audit tools that no other test mentions must at least run.

These five tools were the only `tools/*_audit*.py` whose module name appeared in
no test file. Each test runs the tool as a subprocess against the real
repository state and asserts that it exits successfully and prints something.

The tests do not assert any particular counts: those change every round. They
only pin down the weaker property "the tool still executes", which is what the
archive had never checked for these five.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SMOKE_TOOLS = [
    "light_shadow_audit.py",
    "olfactory_audit.py",
    "play_audit.py",
    "sleep_audit.py",
    "weather_audit.py",
]


class AuditSmokeTests(unittest.TestCase):
    def _run(self, name: str) -> str:
        path = ROOT / "tools" / name
        self.assertTrue(path.is_file(), f"{name} is missing")
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"{name} exited {proc.returncode}\nstderr:\n{proc.stderr[-2000:]}",
        )
        out = proc.stdout.strip()
        self.assertTrue(out, f"{name} printed nothing")
        return out

    def test_light_shadow_audit_runs(self) -> None:
        self.assertTrue(self._run("light_shadow_audit.py"))

    def test_olfactory_audit_runs(self) -> None:
        self.assertTrue(self._run("olfactory_audit.py"))

    def test_play_audit_runs(self) -> None:
        self.assertTrue(self._run("play_audit.py"))

    def test_sleep_audit_runs(self) -> None:
        self.assertTrue(self._run("sleep_audit.py"))

    def test_weather_audit_runs(self) -> None:
        self.assertTrue(self._run("weather_audit.py"))

    def test_every_audit_tool_is_named_by_a_test(self) -> None:
        """No new mirror may be added without some test touching its name."""
        tools = sorted(p.stem for p in (ROOT / "tools").glob("*_audit*.py"))
        self.assertTrue(tools)
        corpus = "\n".join(
            p.read_text(encoding="utf-8") for p in (ROOT / "tests").glob("*.py")
        )
        unnamed = [t for t in tools if t not in corpus]
        self.assertEqual(unnamed, [], f"audit tools named by no test: {unnamed}")


if __name__ == "__main__":
    unittest.main()
