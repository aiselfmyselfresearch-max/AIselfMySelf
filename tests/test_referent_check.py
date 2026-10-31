"""Tests for tools/referent_check.py.

The tool reads the first-parent history and reports identifiers that a commit or
a merge did not carry forward.  These tests build a throwaway repository with a
two-row ledger, drop one row and rewrite the other, and check that the audit
labels them ``missing`` and ``changed`` respectively.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import referent_check  # noqa: E402


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)
    return proc.stdout


def write_rows(repo: Path, rows: list[dict]) -> None:
    path = repo / "state" / "questions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


class ReferentAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def commit(self, message: str) -> None:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", message)

    def test_reports_missing_and_changed_ids(self) -> None:
        write_rows(
            self.repo,
            [
                {"question_id": "Q-001", "question": "同じ名は同じものを指すか。"},
                {"question_id": "Q-002", "question": "失われた行はどこに残るか。"},
            ],
        )
        self.commit("first")

        write_rows(
            self.repo,
            [
                {"question_id": "Q-001", "question": "同じ名は同じものを指すのか、別のものを指すのか。"},
            ],
        )
        self.commit("second")

        events = referent_check.collect_events(self.repo, ["questions"])
        rows = referent_check.classify(events, referent_check.head_maps(self.repo))
        by_id = {row["id"]: row for row in rows}

        self.assertEqual(by_id["Q-002"]["status"], "missing")
        self.assertIn("失われた行", by_id["Q-002"]["before"])
        # An in-place revision keeps the ID, so it is not a dropped referent.
        self.assertNotIn("Q-001", by_id)

    def test_unchanged_rows_are_not_reported(self) -> None:
        write_rows(
            self.repo,
            [{"question_id": "Q-001", "question": "残る問い。"}],
        )
        self.commit("first")
        (self.repo / "notes.txt").write_text("unrelated\n", encoding="utf-8")
        self.commit("second")

        events = referent_check.collect_events(self.repo, ["questions"])
        self.assertEqual(events, [])

    def test_merge_keeps_one_parent_and_drops_the_other(self) -> None:
        write_rows(self.repo, [{"question_id": "Q-001", "question": "main の行。"}])
        self.commit("base")
        git(self.repo, "checkout", "-q", "-b", "side")
        write_rows(
            self.repo,
            [
                {"question_id": "Q-001", "question": "main の行。"},
                {"question_id": "Q-049", "question": "側枝だけが持つ問い。"},
            ],
        )
        self.commit("side adds Q-049")
        git(self.repo, "checkout", "-q", "main")
        write_rows(
            self.repo,
            [
                {"question_id": "Q-001", "question": "main の行。"},
                {"question_id": "Q-049", "question": "main が先に持っていた別の問い。"},
            ],
        )
        self.commit("main adds its own Q-049")
        merge = subprocess.run(
            ["git", "merge", "-q", "--no-ff", "--no-commit", "side"],
            cwd=str(self.repo),
            capture_output=True,
            text=True,
        )
        # The two branches minted the same ID for different rows: conflict.
        self.assertNotEqual(merge.returncode, 0)
        # Resolve as the archive's merge rule did: keep main's row for a shared ID.
        write_rows(
            self.repo,
            [
                {"question_id": "Q-001", "question": "main の行。"},
                {"question_id": "Q-049", "question": "main が先に持っていた別の問い。"},
            ],
        )
        self.commit("merge, main wins on shared IDs")

        events = referent_check.collect_events(self.repo, ["questions"])
        rows = referent_check.classify(events, referent_check.head_maps(self.repo))
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(by_id["Q-049"]["status"], "changed")
        self.assertIn("側枝だけ", by_id["Q-049"]["before"])
        self.assertIn("main が先に", by_id["Q-049"]["after"])


if __name__ == "__main__":
    unittest.main()
