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

    def test_since_reports_but_enforce_gates(self) -> None:
        """--since reports layer 2 from a date; only --enforce turns it into rc=1.

        A rule takes effect by adding --enforce, not by writing a date, so that
        existing --check callers (including CI) keep their behaviour.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            session = {
                "session_id": "SESSION-20261110-dddddd",
                "started_at": "2026-11-10",
                "human_direction": "test",
                "question_ids": [],
                "context_material_ids": ["MAT-20261024-3c4443"],
                "produced_fragment_ids": [],
                "new_question_ids": [],
                "prompt_template": "test",
            }
            shard = repo / "state" / "sessions.d" / "2026-11-10-dddddddddddd.jsonl"
            shard.write_text(json.dumps(session, ensure_ascii=False) + "\n", encoding="utf-8")
            run(repo, "tools/read_log_backfill.py", "--write")  # fill layer 1 only

            plain = run(repo, "tools/read_log_backfill.py", "--check")
            self.assertEqual(plain.returncode, 0, plain.stdout)
            self.assertNotIn("layer2 since", plain.stdout)

            reported = run(repo, "tools/read_log_backfill.py", "--check", "--since", "2026-11-10")
            self.assertEqual(reported.returncode, 0, reported.stdout)
            self.assertIn("layer2 since 2026-11-10", reported.stdout)
            self.assertIn("never fails", reported.stdout)

            enforced = run(
                repo, "tools/read_log_backfill.py", "--check", "--since", "2026-11-10", "--enforce"
            )
            self.assertEqual(enforced.returncode, 1, enforced.stdout)
            self.assertIn("neither a hand-written reading nor", enforced.stdout)

            # Recording the choice in sessions.notes satisfies the rule.
            row = json.loads(shard.read_text(encoding="utf-8").splitlines()[0])
            row["notes"] = "未読の選択: MAT-20261024-3c4443"
            shard.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
            excused = run(
                repo, "tools/read_log_backfill.py", "--check", "--since", "2026-11-10", "--enforce"
            )
            # The checked-in archive already has unrelated unresolved pairs
            # from SESSION-20261113-1650a1. The fixture must not treat those
            # historical debts as if they were fixed here; it verifies only
            # that its own pair leaves the unresolved count when marked unread.
            self.assertEqual(excused.returncode, 1, excused.stdout)
            self.assertIn("excused by 未読の選択:", excused.stdout)
            self.assertIn("FAIL: 29 pairs since 2026-11-10", excused.stdout)
            self.assertIn("layer2 since 2026-11-10:", excused.stdout)
            self.assertNotIn("SESSION-20261110-dddddd -> MAT-20261024-3c4443", excused.stdout)

    def test_enforce_requires_since(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            proc = run(repo, "tools/read_log_backfill.py", "--check", "--enforce")
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("--enforce requires --since", proc.stderr)

    def test_future_session_id_date_is_not_eligible(self) -> None:
        """A future internal label in the ID must not be treated as a real date.

        Measured 2026-11-10: 102 of 632 session IDs already carry a future
        internal-chronology label. Crediting them would turn the internal
        chronology into a compliance record for sessions that have not happened.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            session = {
                "session_id": "SESSION-20990104-cccccc",
                "started_at": "2099-01-04",
                "human_direction": "test",
                "question_ids": [],
                "context_material_ids": ["MAT-20261024-3c4443"],
                "produced_fragment_ids": [],
                "new_question_ids": [],
                "prompt_template": "test",
            }
            shard = repo / "state" / "sessions.d" / "2099-01-04-cccccccccccc.jsonl"
            shard.write_text(json.dumps(session, ensure_ascii=False) + "\n", encoding="utf-8")
            run(repo, "tools/read_log_backfill.py", "--write")

            proc = run(
                repo, "tools/read_log_backfill.py", "--check", "--since", "2026-11-10", "--enforce"
            )
            # The base fixture has 29 unrelated unresolved layer-2 pairs.
            # The future-dated session must not add a thirtieth eligible pair.
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("exempt", proc.stdout)
            self.assertIn("FAIL: 29 pairs since 2026-11-10", proc.stdout)
            self.assertNotIn("SESSION-20990104-cccccc", proc.stdout)

    def test_layer2_is_reported_but_never_gates(self) -> None:
        """Layer 2 (hand-written readings) must be printed and must not change rc.

        2026-11-10: the check reports two layers. Layer 1 (contact) gates;
        layer 2 (a hand-written reading) is informational only, because gating
        on it would demand retroactive rows for thousands of past pairs and
        create an incentive to record readings that did not happen.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            # A new session whose context material has no read_log row at all:
            # layer 1 fails, and layer 2 is 0 for that pair too.
            session = {
                "session_id": "SESSION-20990102-eeeeee",
                "started_at": "2099-01-02",
                "human_direction": "test",
                "question_ids": [],
                "context_material_ids": ["MAT-20261024-3c4443"],
                "produced_fragment_ids": [],
                "new_question_ids": [],
                "prompt_template": "test",
            }
            shard = repo / "state" / "sessions.d" / "2099-01-02-eeeeeeeeeeee.jsonl"
            shard.write_text(json.dumps(session, ensure_ascii=False) + "\n", encoding="utf-8")

            proc = run(repo, "tools/read_log_backfill.py", "--check")
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("layer2 (hand-written reading)", proc.stdout)

            # Fill only layer 1 with a machine row; layer 2 stays at zero for
            # that pair, and the check must pass with the layer-2 number shown.
            wrote = run(repo, "tools/read_log_backfill.py", "--write")
            self.assertEqual(wrote.returncode, 0, wrote.stdout + wrote.stderr)
            after = run(repo, "tools/read_log_backfill.py", "--check")
            self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
            self.assertIn("layer2 (hand-written reading)", after.stdout)
            self.assertIn("never fails this check", after.stdout)


if __name__ == "__main__":
    unittest.main()
