"""Tests for tools/new_ledger_shard.py (per-session shard creation)."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import new_ledger_shard  # noqa: E402
from validate_seed import COLLECTIONS  # noqa: E402


def make_root(tmp: Path) -> Path:
    state = tmp / "state"
    state.mkdir(parents=True)
    for _name, (filename, _id_key, _schema) in COLLECTIONS.items():
        (state / filename).write_text("", encoding="utf-8")
    return tmp


class ShardPathTests(unittest.TestCase):
    def test_path_uses_date_and_12_hex_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            path = new_ledger_shard.shard_path(
                "fragments",
                root=root,
                day="2026-10-21",
                suffix="abcdefabcdef",
            )
            self.assertEqual(
                path,
                root / "state" / "fragments.d" / "2026-10-21-abcdefabcdef.jsonl",
            )

    def test_invalid_inputs_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            with self.assertRaises(ValueError):
                new_ledger_shard.shard_path("nope", root=root)
            with self.assertRaises(ValueError):
                new_ledger_shard.shard_path("fragments", root=root, day="2026-02-30")
            with self.assertRaises(ValueError):
                new_ledger_shard.shard_path("fragments", root=root, suffix="ABC")
            with self.assertRaises(ValueError):
                new_ledger_shard.shard_path("fragments", root=root, suffix="a" * 11)

    def test_missing_base_ledger_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state").mkdir()
            with self.assertRaises(FileNotFoundError):
                new_ledger_shard.create_shard("fragments", root=root)


class ShardCliTests(unittest.TestCase):
    def test_errata_shards_use_the_errata_base_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            (root / "state" / "errata.jsonl").write_text("", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = new_ledger_shard.main(
                    [
                        "errata",
                        "--create",
                        "--date",
                        "2026-10-21",
                        "--suffix",
                        "cccccccccccc",
                        "--root",
                        str(root),
                    ]
                )
            self.assertEqual(code, 0)
            path = root / output.getvalue().strip()
            self.assertEqual(
                path,
                root / "state" / "errata.d" / "2026-10-21-cccccccccccc.jsonl",
            )
            self.assertTrue(path.is_file())

    def test_create_then_second_create_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            arguments = [
                "fragments",
                "--create",
                "--date",
                "2026-10-21",
                "--suffix",
                "aaaaaaaaaaaa",
                "--root",
                str(root),
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                first = new_ledger_shard.main(arguments)
            self.assertEqual(first, 0)
            path = root / output.getvalue().strip()
            self.assertTrue(path.is_file())
            self.assertTrue(str(path).endswith("2026-10-21-aaaaaaaaaaaa.jsonl"))

            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                second = new_ledger_shard.main(arguments)
            self.assertEqual(second, 1)
            self.assertIn("already exists", error.getvalue())

    def test_dry_run_prints_without_creating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = new_ledger_shard.main(
                    [
                        "questions",
                        "--date",
                        "2026-10-21",
                        "--suffix",
                        "bbbbbbbbbbbb",
                        "--root",
                        str(root),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("2026-10-21-bbbbbbbbbbbb.jsonl", output.getvalue())
            self.assertFalse((root / "state" / "questions.d").exists())

    def test_list_returns_existing_shards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            base = root / "state" / "fragments.jsonl"
            directory = base.with_name("fragments.d")
            directory.mkdir()
            (directory / "2026-10-21-bbbbbbbbbbbb.jsonl").write_text("", encoding="utf-8")
            (directory / "2026-10-21-aaaaaaaaaaaa.jsonl").write_text("", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = new_ledger_shard.main(
                    ["fragments", "--list", "--root", str(root)]
                )
            self.assertEqual(code, 0)
            self.assertEqual(
                output.getvalue().split(),
                [
                    "state/fragments.d/2026-10-21-aaaaaaaaaaaa.jsonl",
                    "state/fragments.d/2026-10-21-bbbbbbbbbbbb.jsonl",
                ],
            )


if __name__ == "__main__":
    unittest.main()
