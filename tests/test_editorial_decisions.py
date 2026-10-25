"""Tests for append-only editorial_decisions ledger: schema, FK/type checks, overlay, ID minting."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import new_id  # noqa: E402


def copy_repo(destination: Path) -> Path:
    repo = destination / "repo"
    shutil.copytree(
        ROOT,
        repo,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "tests", "map"),
    )
    return repo


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=repo, capture_output=True, text=True, timeout=300
    )


class EditorialDecisionTests(unittest.TestCase):
    def test_overlay_updates_fragment_and_question_status_without_mutating_shards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            ed_dir = repo / "state" / "editorial_decisions.d"
            ed_dir.mkdir(parents=True, exist_ok=True)
            rows = [
                {
                    "decision_id": "ED-20261025-111111",
                    "session_id": "SESSION-20261024-9dd96f",
                    "target": {"type": "fragment", "id": "FRAG-005"},
                    "status": "selected",
                    "reason": "Promote draft fragment via append-only editorial decision.",
                    "created_at": "2026-10-25",
                },
                {
                    "decision_id": "ED-20261025-222222",
                    "session_id": "SESSION-20261024-9dd96f",
                    "target": {"type": "question", "id": "Q-005"},
                    "status": "paused",
                    "reason": "Pause dormant question in review.",
                    "created_at": "2026-10-25",
                },
            ]
            shard1 = ed_dir / "2026-10-25-aaaaaaaaaaaa.jsonl"
            shard1.write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                encoding="utf-8",
            )
            ok = run(repo, "tools/validate_seed.py")
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

            frags = ledger_io.load_jsonl_union(
                repo / "state" / "fragments.jsonl", "fragment_id", root=repo
            )
            qs = ledger_io.load_jsonl_union(
                repo / "state" / "questions.jsonl", "question_id", root=repo
            )
            self.assertEqual(frags["FRAG-005"]["status"], "selected")
            self.assertEqual(qs["Q-005"]["status"], "paused")

            # Later decision shard supersedes earlier status cleanly.
            shard2 = ed_dir / "2026-10-25-bbbbbbbbbbbb.jsonl"
            shard2.write_text(
                json.dumps(
                    {
                        "decision_id": "ED-20261025-333333",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "question", "id": "Q-005"},
                        "status": "open",
                        "reason": "Reopen question.",
                        "created_at": "2026-10-25",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            qs2 = ledger_io.load_jsonl_union(
                repo / "state" / "questions.jsonl", "question_id", root=repo
            )
            self.assertEqual(qs2["Q-005"]["status"], "open")

    def test_invalid_status_or_unknown_refs_fail_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            ed_dir = repo / "state" / "editorial_decisions.d"
            ed_dir.mkdir(parents=True, exist_ok=True)
            shard = ed_dir / "2026-10-25-badbadbadbad.jsonl"

            # Fragment cannot receive question-only status "paused".
            shard.write_text(
                json.dumps(
                    {
                        "decision_id": "ED-20261025-999999",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "fragment", "id": "FRAG-005"},
                        "status": "paused",
                        "reason": "wrong enum for fragment",
                        "created_at": "2026-10-25",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            bad = run(repo, "tools/validate_seed.py")
            self.assertEqual(bad.returncode, 1)
            self.assertIn("is not valid for target type 'fragment'", bad.stdout)

            # Unknown target ID fails.
            shard.write_text(
                json.dumps(
                    {
                        "decision_id": "ED-20261025-999999",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "fragment", "id": "FRAG-NOPE"},
                        "status": "selected",
                        "reason": "unknown target",
                        "created_at": "2026-10-25",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            bad2 = run(repo, "tools/validate_seed.py")
            self.assertEqual(bad2.returncode, 1)
            self.assertIn("target references unknown fragment ID 'FRAG-NOPE'", bad2.stdout)

    def test_ed_prefix_mints_id(self) -> None:
        minted = new_id.mint("ED", day="20261025", taken=set())
        self.assertRegex(minted, r"^ED-20261025-[0-9a-f]{6}$")


if __name__ == "__main__":
    unittest.main()
