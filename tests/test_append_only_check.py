"""Tests for tools/append_only_check.py.

The gate exists because every other check parses a ledger row before looking at
it, so a row whose bytes changed (re-serialised) or whose content changed while
staying valid passes them all.  These tests pin the three things the gate must
tell apart -- appended, moved, changed -- and the refusal to guess when the base
commit is not available.
"""
from __future__ import annotations

import collections
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import append_only_check as aoc  # noqa: E402
import validate_seed  # noqa: E402

SPACED = '{"note_id": "NOTE-20261111-aaaaaa", "path": "readings/x.md", "session_id": "SESSION-20261111-aaaaaa"}'
COMPACT = '{"note_id":"NOTE-20261111-aaaaaa","path":"readings/x.md","session_id":"SESSION-20261111-aaaaaa"}'
EDITED = '{"note_id": "NOTE-20261111-aaaaaa", "path": "readings/y.md", "session_id": "SESSION-20261111-aaaaaa"}'
OTHER = '{"note_id": "NOTE-20261111-bbbbbb", "path": "readings/z.md", "session_id": "SESSION-20261111-bbbbbb"}'


def notes(*rows: str, shard: str = "state/notes.d/2026-11-11-aaaaaaaaaaaa.jsonl") -> aoc.Lines:
    result: aoc.Lines = {}
    aoc.add_lines(result, shard, ("\n".join(rows) + "\n").encode("utf-8"))
    return result


class CollectionForPathTest(unittest.TestCase):
    def test_base_file_and_shard_belong_to_the_same_collection(self):
        self.assertEqual(aoc.collection_for_path("state/notes.jsonl"), "notes")
        self.assertEqual(aoc.collection_for_path("state/notes.d/2026-11-11-aaaaaaaaaaaa.jsonl"), "notes")

    def test_files_that_are_not_ledgers_are_ignored(self):
        for path in (
            "state/README.md",
            "state/selection_snapshots.jsonl",
            "state/quarantine/2026-11-08-a7f3b2c1d4e5.original.jsonl",
            "readings/2026-11-11-x.md",
            "state/notes.d/nested/x.jsonl",
        ):
            self.assertIsNone(aoc.collection_for_path(path), path)

    def test_every_validated_collection_is_guarded(self):
        missing = set(validate_seed.COLLECTIONS) - set(aoc.COLLECTIONS)
        self.assertEqual(missing, set(), "a ledger validated by validate_seed.py is not append-only-checked")


class LostLinesTest(unittest.TestCase):
    def test_appending_loses_nothing(self):
        self.assertEqual(aoc.lost_lines(notes(SPACED), notes(SPACED, OTHER)), {})

    def test_reserialised_row_is_reported_even_though_it_parses_the_same(self):
        self.assertEqual(json.loads(SPACED), json.loads(COMPACT))
        report = aoc.lost_lines(notes(SPACED), notes(COMPACT, OTHER))
        self.assertEqual(report, {"notes": [{"id": "NOTE-20261111-aaaaaa", "kind": "reserialised"}]})

    def test_edited_row_is_reported(self):
        report = aoc.lost_lines(notes(SPACED), notes(EDITED))
        self.assertEqual(report["notes"][0]["kind"], "edited")

    def test_removed_row_is_reported(self):
        report = aoc.lost_lines(notes(SPACED, OTHER), notes(OTHER))
        self.assertEqual(report, {"notes": [{"id": "NOTE-20261111-aaaaaa", "kind": "removed"}]})

    def test_moving_a_row_between_shards_of_one_collection_is_not_a_loss(self):
        before = notes(SPACED, shard="state/notes.d/2026-11-11-aaaaaaaaaaaa.jsonl")
        after = notes(SPACED, shard="state/notes.d/2026-11-11-000000000000.jsonl")
        self.assertEqual(aoc.lost_lines(before, after), {})

    def test_moving_a_row_to_another_collection_is_a_loss(self):
        before = notes(SPACED)
        after: aoc.Lines = {}
        aoc.add_lines(after, "state/sessions.d/2026-11-11-aaaaaaaaaaaa.jsonl", (SPACED + "\n").encode())
        self.assertEqual(aoc.lost_lines(before, after)["notes"][0]["kind"], "removed")

    def test_a_duplicated_line_must_keep_its_count(self):
        before = {"notes": collections.Counter({SPACED.encode(): 2})}
        after = {"notes": collections.Counter({SPACED.encode(): 1})}
        self.assertEqual(len(aoc.lost_lines(before, after)["notes"]), 1)

    def test_blank_lines_are_not_rows(self):
        self.assertEqual(aoc.lost_lines(notes(SPACED, "", "  "), notes(SPACED)), {})


def git(root: Path, *args: str) -> str:
    env = dict(
        os.environ,
        GIT_AUTHOR_NAME="t",
        GIT_AUTHOR_EMAIL="t@example.invalid",
        GIT_COMMITTER_NAME="t",
        GIT_COMMITTER_EMAIL="t@example.invalid",
    )
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=env)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
    return done.stdout.strip()


class GitComparisonTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        self.shard = self.root / "state" / "notes.d" / "2026-11-11-aaaaaaaaaaaa.jsonl"
        self.shard.parent.mkdir(parents=True)
        self.shard.write_text(SPACED + "\n", encoding="utf-8")
        self.commit("first row")

    def tearDown(self):
        self._tmp.cleanup()

    def commit(self, message: str) -> str:
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", message)
        return git(self.root, "rev-parse", "HEAD")

    def run_tool(self, *args: str) -> int:
        with open(os.devnull, "w") as devnull:
            stdout, sys.stdout = sys.stdout, devnull
            try:
                return aoc.main([*args, "--root", str(self.root)])
            finally:
                sys.stdout = stdout

    def test_appending_in_the_working_tree_passes(self):
        with self.shard.open("ab") as handle:
            handle.write((OTHER + "\n").encode("utf-8"))
        self.assertEqual(self.run_tool("--base", "HEAD"), 0)

    def test_load_and_dump_of_a_shared_shard_fails(self):
        rows = [json.loads(line) for line in self.shard.read_text(encoding="utf-8").splitlines()]
        rows.append(json.loads(OTHER))
        self.shard.write_text(
            "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )
        self.assertEqual(self.run_tool("--base", "HEAD"), 1)

    def test_default_base_is_head_when_there_is_no_origin_main(self):
        self.shard.write_text(EDITED + "\n", encoding="utf-8")
        self.assertEqual(self.run_tool(), 1)

    def test_own_rows_not_yet_on_main_may_be_fixed(self):
        git(self.root, "update-ref", "refs/remotes/origin/main", "HEAD")
        with self.shard.open("ab") as handle:
            handle.write((OTHER + "\n").encode("utf-8"))
        self.commit("append my row")
        text = self.shard.read_text(encoding="utf-8").replace("readings/z.md", "readings/w.md")
        self.shard.write_text(text, encoding="utf-8")
        self.assertEqual(self.run_tool(), 0, "a row that never reached origin/main is still a draft")
        self.shard.write_text(text.replace(SPACED, COMPACT), encoding="utf-8")
        self.assertEqual(self.run_tool(), 1, "a row that is on origin/main must keep its bytes")

    def test_parents_mode_checks_a_commit_against_what_it_was_built_on(self):
        self.shard.write_text(COMPACT + "\n" + OTHER + "\n", encoding="utf-8")
        self.commit("rewrite while appending")
        self.assertEqual(self.run_tool("--parents"), 1)
        with self.shard.open("ab") as handle:
            handle.write((EDITED.replace("aaaaaa", "cccccc") + "\n").encode("utf-8"))
        self.commit("append only")
        self.assertEqual(self.run_tool("--parents"), 0)

    def test_an_unavailable_base_is_not_a_pass(self):
        self.assertEqual(self.run_tool("--base", "0123456789abcdef0123456789abcdef01234567"), 2)


if __name__ == "__main__":
    unittest.main()
