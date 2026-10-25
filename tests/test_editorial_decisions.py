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

    def test_branch_seed_dispersion_is_deterministic_and_diverges_across_branches(self) -> None:
        import inspect_inquiry

        data = inspect_inquiry.load_all()
        label_a1, int_a1 = inspect_inquiry.resolve_session_seed(
            "arena/6f350638-aiselfmyself", data=data
        )
        label_a2, int_a2 = inspect_inquiry.resolve_session_seed(
            "arena/6f350638-aiselfmyself", data=data
        )
        label_b, int_b = inspect_inquiry.resolve_session_seed(
            "arena/7d235e38-aiselfmyself", data=data
        )
        self.assertEqual((label_a1, int_a1), ("6f350638", 0x6F350638))
        self.assertEqual((label_a1, int_a1), (label_a2, int_a2))
        self.assertNotEqual(int_a1, int_b)

        win_a1 = inspect_inquiry.build_candidate_windows(
            data, seed="arena/6f350638-aiselfmyself"
        )
        win_a2 = inspect_inquiry.build_candidate_windows(
            data, seed="arena/6f350638-aiselfmyself"
        )
        win_b = inspect_inquiry.build_candidate_windows(
            data, seed="arena/7d235e38-aiselfmyself"
        )
        self.assertEqual(win_a1, win_a2)
        self.assertNotEqual(win_a1["rereading_pairs"], win_b["rereading_pairs"])
        self.assertNotEqual(win_a1["revision_drafts"], win_b["revision_drafts"])
        self.assertNotEqual(win_a1["review_drafts"], win_b["review_drafts"])

        pkt_a = inspect_inquiry.build_context_packet(
            data, "auto", seed="arena/6f350638-aiselfmyself"
        )
        pkt_b = inspect_inquiry.build_context_packet(
            data, "auto", seed="arena/7d235e38-aiselfmyself"
        )
        self.assertIn("シード：6f350638", pkt_a)
        self.assertIn("シード：7d235e38", pkt_b)
        self.assertNotEqual(pkt_a.splitlines()[0], pkt_b.splitlines()[0])

    def test_sync_readme_counts_updates_stale_numbers_and_is_idempotent(self) -> None:
        import inspect_inquiry
        import map_build

        data = inspect_inquiry.load_all()
        with tempfile.TemporaryDirectory() as tmp:
            readme_copy = Path(tmp) / "README.md"
            original = (ROOT / "README.md").read_text(encoding="utf-8")
            # Introduce a deliberately stale session count in §1 and §4
            stale = original.replace(
                f"（全{len(data['sessions'])}セッションの要約全文",
                "（全1セッションの要約全文",
            )
            readme_copy.write_text(stale, encoding="utf-8")

            changed = map_build.sync_readme_counts(
                data, readme_path=readme_copy, readings_dir=ROOT / "readings"
            )
            self.assertTrue(changed)
            self.assertEqual(readme_copy.read_text(encoding="utf-8"), original)

            # Second run should be a no-op
            changed_again = map_build.sync_readme_counts(
                data, readme_path=readme_copy, readings_dir=ROOT / "readings"
            )
            self.assertFalse(changed_again)


if __name__ == "__main__":
    unittest.main()
