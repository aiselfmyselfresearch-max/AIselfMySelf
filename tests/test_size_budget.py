"""Tests for tools/size_budget.py (growth budgets for tracked files)."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import size_budget  # noqa: E402


def run(root: Path, *args: str) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = size_budget.main([*args, "--root", str(root)])
    return code, buffer.getvalue()


class SizeBudgetTests(unittest.TestCase):
    def test_within_budget_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("small", encoding="utf-8")
            code, out = run(root)
            self.assertEqual(code, 0, out)
            self.assertIn("PASS: all size budgets are within soft limits", out)

    def test_soft_budget_warns_but_passes_unless_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_bytes(b"x" * 150_000)
            code, out = run(root)
            self.assertEqual(code, 0, out)
            self.assertIn("WARN", out)

            code, out = run(root, "--strict")
            self.assertEqual(code, 1, out)
            self.assertIn("--strict", out)

    def test_hard_budget_fails_even_without_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_bytes(b"x" * 300_000)
            code, out = run(root)
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL", out)

    def test_state_monoliths_use_their_own_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state").mkdir()
            (root / "state" / "materials.jsonl").write_bytes(b"y" * 60_000)
            code, out = run(root)
            self.assertEqual(code, 0, out)
            self.assertIn("state/materials.jsonl", out)

            (root / "state" / "materials.jsonl").write_bytes(b"y" * 10_000_000)
            code, out = run(root)
            self.assertEqual(code, 1, out)
            self.assertIn("FAIL", out)

    def test_repository_root_itself_is_within_soft_budgets(self) -> None:
        code, out = run(ROOT)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)


if __name__ == "__main__":
    unittest.main()
