"""Smoke tests against this checkout: the ledgers and generated map stay valid."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=repo, capture_output=True, text=True, timeout=120
    )


class RepositorySmokeTests(unittest.TestCase):
    def test_ledgers_validate_and_reading_map_is_current(self) -> None:
        validation = run(ROOT, "tools/validate_seed.py")
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
        self.assertIn("PASS: literary inquiry seed valid", validation.stdout)

        check = run(ROOT, "tools/inspect_inquiry.py", "--check-map")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertIn("PASS:", check.stdout)

    def test_import_write_refuses_materials_shards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(
                ROOT,
                repo,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "tests"),
            )
            shard_dir = repo / "state" / "materials.d"
            shard_dir.mkdir()
            (shard_dir / "2026-10-21-aaaaaaaaaaaa.jsonl").write_text(
                '{"material_id": "MAT-LIT-999"}\n', encoding="utf-8"
            )

            result = run(
                repo,
                "tools/import_researchos.py",
                "--source-root",
                str(Path(tmp) / "does-not-matter"),
                "--write",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("materials.d", result.stderr)
            self.assertIn("Consolidate", result.stderr)


if __name__ == "__main__":
    unittest.main()
