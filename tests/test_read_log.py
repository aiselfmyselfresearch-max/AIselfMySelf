"""Tests for the read_log ledger: schema wiring, FK checks, ID minting, backfill."""
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


def read_row(**overrides: object) -> dict:
    row = {
        "read_id": "READ-20261024-aaaaaa",
        "session_id": "SESSION-20261024-9dd96f",
        "target": {"type": "material", "id": "MAT-20261024-3c4443"},
        "reading": "interpreted",
        "note": "test",
        "created_at": "2026-10-24",
    }
    row.update(overrides)
    return row


class ReadLogValidationTests(unittest.TestCase):
    def test_valid_row_passes_and_unknown_refs_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            shard = repo / "state" / "read_log.d" / "2026-10-24-testtesttest.jsonl"
            shard.write_text(
                json.dumps(read_row(), ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            ok = run(repo, "tools/validate_seed.py")
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

            shard.write_text(
                json.dumps(read_row(target={"type": "material", "id": "MAT-NOPE"}), ensure_ascii=False, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            bad = run(repo, "tools/validate_seed.py")
            self.assertEqual(bad.returncode, 1)
            self.assertIn("read_log:READ-20261024-aaaaaa: target references unknown", bad.stdout)

            shard.write_text(
                json.dumps(read_row(session_id="SESSION-NOPE"), ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            bad = run(repo, "tools/validate_seed.py")
            self.assertEqual(bad.returncode, 1)
            self.assertIn("session_id references unknown session", bad.stdout)

    def test_reading_note_target_resolves_against_readings_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            shard = repo / "state" / "read_log.d" / "2026-10-24-testtesttest.jsonl"
            existing = sorted(p.name for p in (repo / "readings").glob("*.md"))
            self.assertTrue(existing, "copied repo should carry readings/*.md")

            shard.write_text(
                json.dumps(
                    read_row(target={"type": "reading_note", "id": f"readings/{existing[0]}"}),
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            ok = run(repo, "tools/validate_seed.py")
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

            for bad_id in (
                "readings/no-such-note-20990101.md",
                existing[0],  # bare filename without the readings/ prefix
                "readings/../README.md",  # traversal must never resolve
            ):
                shard.write_text(
                    json.dumps(
                        read_row(target={"type": "reading_note", "id": bad_id}),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                bad = run(repo, "tools/validate_seed.py")
                self.assertEqual(bad.returncode, 1, f"{bad_id!r} should fail: {bad.stdout}")
                self.assertIn(
                    "read_log:READ-20261024-aaaaaa: target references unknown reading_note",
                    bad.stdout,
                )

    def test_schema_rejects_unknown_reading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            shard = repo / "state" / "read_log.d" / "2026-10-24-testtesttest.jsonl"
            shard.write_text(
                json.dumps(read_row(reading="devoured"), ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            bad = run(repo, "tools/validate_seed.py")
            self.assertEqual(bad.returncode, 1)
            self.assertIn("is not in enum", bad.stdout)


class ReadIdTests(unittest.TestCase):
    def test_read_prefix_mints_and_sees_existing_rows(self) -> None:
        value = new_id.mint("READ", day="20261024", taken=set())
        self.assertRegex(value, r"^READ-20261024-[0-9a-f]{6}$")

        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            shard = repo / "state" / "read_log.d" / "2026-10-24-testtesttest.jsonl"
            shard.write_text(
                json.dumps(read_row(read_id="READ-20261024-00beef"), ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            taken = new_id.existing_ids("READ", root=repo)
            self.assertIn("READ-20261024-00beef", taken)
            # the machine backfill shard already carries one row per (session, context material)
            self.assertGreater(len(taken), 1000)


class BackfillTests(unittest.TestCase):
    def test_check_write_check_roundtrip_and_idempotence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            # A new session whose context materials have no read_log rows yet.
            session = {
                "session_id": "SESSION-20990101-ffffff",
                "started_at": "2099-01-01",
                "human_direction": "test",
                "question_ids": [],
                "context_material_ids": ["MAT-20261024-3c4443"],
                "produced_fragment_ids": [],
                "new_question_ids": [],
                "prompt_template": "test",
            }
            shard = repo / "state" / "sessions.d" / "2099-01-01-ffffffffffff.jsonl"
            shard.write_text(json.dumps(session, ensure_ascii=False) + "\n", encoding="utf-8")

            before = run(repo, "tools/read_log_backfill.py", "--check")
            self.assertEqual(before.returncode, 1, before.stdout + before.stderr)
            self.assertIn("1 pairs have no read_log row", before.stdout)

            wrote = run(repo, "tools/read_log_backfill.py", "--write")
            self.assertEqual(wrote.returncode, 0, wrote.stdout + wrote.stderr)
            self.assertIn("WROTE 1 read_log rows", wrote.stdout)

            after = run(repo, "tools/read_log_backfill.py", "--check")
            self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
            self.assertIn("PASS", after.stdout)

            again = run(repo, "tools/read_log_backfill.py", "--write")
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertIn("WROTE nothing", again.stdout)

            validate = run(repo, "tools/validate_seed.py")
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


if __name__ == "__main__":
    unittest.main()
