"""Tests for tools/new_id.py (collision-resistant ID minting)."""
from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import new_id  # noqa: E402
from validate_seed import COLLECTIONS  # noqa: E402


def make_root(tmp: Path) -> Path:
    state = tmp / "state"
    state.mkdir(parents=True)
    for _name, (filename, _id_key, _schema) in COLLECTIONS.items():
        (state / filename).write_text("", encoding="utf-8")
    return tmp


def fragment(fragment_id: str) -> dict:
    return {
        "fragment_id": fragment_id,
        "created_at": "2026-10-21",
        "language": "ja",
        "form": "fragment",
        "title": "t",
        "text": "body",
        "narrator_mode": "other",
        "question_ids": ["Q-001"],
        "motif_ids": ["MOTIF-002"],
        "material_ids": [],
        "status": "draft",
    }


class MintTests(unittest.TestCase):
    def test_format_is_prefix_date_and_hex(self) -> None:
        value = new_id.mint("FRAG", day="20261021", taken=set())
        self.assertRegex(value, r"^FRAG-20261021-[0-9a-f]{6}$")
        self.assertRegex(
            new_id.mint("MAT-LIT", day="20261021", taken=set(), hex_bytes=2),
            r"^MAT-LIT-20261021-[0-9a-f]{4}$",
        )

    def test_taken_ids_are_skipped(self) -> None:
        taken = {f"FRAG-20261021-{index:06x}" for index in range(5000)}
        value = new_id.mint("FRAG", day="20261021", taken=taken)
        self.assertNotIn(value, taken)

    def test_unknown_prefix_and_bad_date_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            new_id.mint("NOPE", day="20261021")
        with self.assertRaises(ValueError):
            new_id.mint("FRAG", day="2026-10-21")

    def test_existing_ids_include_shards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            base = root / "state" / "fragments.jsonl"
            base.write_text(json.dumps(fragment("FRAG-20261021-aaaaaa")) + "\n", encoding="utf-8")
            shard = base.with_name("fragments.d") / "2026-10-21-bbbbbbbbbbbb.jsonl"
            shard.parent.mkdir()
            shard.write_text(json.dumps(fragment("FRAG-20261021-bbbbbb")) + "\n", encoding="utf-8")

            ids = new_id.existing_ids("FRAG", root)
            self.assertIn("FRAG-20261021-aaaaaa", ids)
            self.assertIn("FRAG-20261021-bbbbbb", ids)

    def test_cli_mints_requested_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = new_id.main(
                    ["FRAG", "--count", "5", "--date", "20261021", "--root", str(root)]
                )
            self.assertEqual(code, 0)
            values = output.getvalue().split()
            self.assertEqual(len(values), 5)
            self.assertEqual(len(set(values)), 5)
            for value in values:
                self.assertRegex(value, r"^FRAG-20261021-[0-9a-f]{6}$")

    def test_cli_refuses_a_corrupt_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            (root / "state" / "fragments.jsonl").write_text("{not json}\n", encoding="utf-8")
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                code = new_id.main(["FRAG", "--root", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("error:", error.getvalue())

    def test_concurrent_processes_mint_unique_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        str(ROOT / "tools" / "new_id.py"),
                        "FRAG",
                        "--count",
                        "25",
                        "--date",
                        "20261021",
                        "--hex-bytes",
                        "3",
                        "--root",
                        str(root),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for _ in range(4)
            ]
            results = [process.communicate(timeout=30) for process in processes]
            for process, (stdout, stderr) in zip(processes, results):
                self.assertEqual(process.returncode, 0, stderr)
            values = [line for stdout, _ in results for line in stdout.split()]
            self.assertEqual(len(values), 100)
            self.assertEqual(len(set(values)), 100)
            for value in values:
                self.assertTrue(re.fullmatch(r"FRAG-20261021-[0-9a-f]{6}", value), value)


if __name__ == "__main__":
    unittest.main()
