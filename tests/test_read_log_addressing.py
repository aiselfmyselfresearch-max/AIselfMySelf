"""Tests for the two fields added on 2026-11-17.

``read_log.in_reply_to`` (規則11) and the required assignment receipt on new
session rows (規則10).  The read_log checks run the real validator on a copy of
the repository; the role-receipt check is called directly with an explicit
``today`` because the effective date is 2026-11-18 and a gate that cannot be
tested before it fires is not a gate.
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_seed  # noqa: E402


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


def read_row(read_id: str, **overrides: object) -> dict:
    row = {
        "read_id": read_id,
        "session_id": "SESSION-20261024-9dd96f",
        "target": {"type": "material", "id": "MAT-20261024-3c4443"},
        "reading": "contested",
        "note": "test",
        "created_at": "2026-10-24",
    }
    row.update(overrides)
    return row


class InReplyToTests(unittest.TestCase):
    def _write(self, repo: Path, rows: list[dict]) -> None:
        shard = repo / "state" / "read_log.d" / "2026-10-24-addressingtest.jsonl"
        shard.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_an_address_to_an_existing_earlier_reading_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(
                repo,
                [
                    read_row("READ-20261024-aaaaaa", reading="interpreted"),
                    read_row("READ-20261024-bbbbbb", in_reply_to=["READ-20261024-aaaaaa"]),
                ],
            )
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_an_unknown_address_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(repo, [read_row("READ-20261024-bbbbbb", in_reply_to=["READ-20261024-ffffff"])])
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("in_reply_to references unknown reading", result.stdout)

    def test_a_row_cannot_address_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(repo, [read_row("READ-20261024-bbbbbb", in_reply_to=["READ-20261024-bbbbbb"])])
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("in_reply_to names the row itself", result.stdout)

    def test_a_forward_address_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(
                repo,
                [
                    read_row("READ-20261024-aaaaaa", reading="interpreted"),
                    read_row("READ-20261023-bbbbbb", in_reply_to=["READ-20261024-aaaaaa"]),
                ],
            )
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("dated later", result.stdout)

    def test_a_malformed_address_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(repo, [read_row("READ-20261024-bbbbbb", in_reply_to=["READ-2026"])])
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("is not a READ-<YYYYMMDD>-<hex> id", result.stdout)

    def test_the_field_is_optional(self) -> None:
        """Every row written before 2026-11-17 must stay valid."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            self._write(repo, [read_row("READ-20261024-cccccc")])
            result = run(repo, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class RoleReceiptTests(unittest.TestCase):
    RECEIPT = {
        "dispersal_seed": "050f6b7e",
        "assigned_role": "adversarial_tester",
        "offered_target_question_id": "Q-002",
        "offered_reference_mode": "close_reading_report",
    }

    def test_a_new_session_without_a_receipt_is_an_error(self) -> None:
        errors: list[str] = []
        validate_seed.check_role_receipts(
            {"SESSION-20261118-abcdef": {"session_id": "SESSION-20261118-abcdef"}},
            errors,
            today=datetime.date(2026, 11, 19),
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("missing assignment receipt", errors[0])
        self.assertIn("assigned_role", errors[0])

    def test_a_named_missing_field_is_reported_as_missing(self) -> None:
        errors: list[str] = []
        record = {"session_id": "SESSION-20261118-abcdef", **self.RECEIPT}
        record["offered_reference_mode"] = ""
        validate_seed.check_role_receipts(
            {"SESSION-20261118-abcdef": record}, errors, today=datetime.date(2026, 11, 19)
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("offered_reference_mode", errors[0])
        self.assertNotIn("dispersal_seed", errors[0])

    def test_a_complete_receipt_passes(self) -> None:
        errors: list[str] = []
        record = {"session_id": "SESSION-20261118-abcdef", **self.RECEIPT}
        validate_seed.check_role_receipts(
            {"SESSION-20261118-abcdef": record}, errors, today=datetime.date(2026, 11, 19)
        )
        self.assertEqual(errors, [])

    def test_rows_before_the_effective_date_are_exempt(self) -> None:
        errors: list[str] = []
        validate_seed.check_role_receipts(
            {"SESSION-20261117-abcdef": {"session_id": "SESSION-20261117-abcdef"}},
            errors,
            today=datetime.date(2026, 11, 19),
        )
        self.assertEqual(errors, [])

    def test_forward_dated_labels_are_exempt(self) -> None:
        """187 session IDs carry internal chronology labels in 2026-12..2027."""
        errors: list[str] = []
        validate_seed.check_role_receipts(
            {"SESSION-20270211-db3691": {"session_id": "SESSION-20270211-db3691"}},
            errors,
            today=datetime.date(2026, 11, 19),
        )
        self.assertEqual(errors, [])

    def test_a_same_day_internal_label_with_no_receipt_is_exempt_only_by_id(self) -> None:
        """Two 2026-10-26 rows carry the internal label 20261118.

        On the real day 2026-11-18 the ``today`` upper bound can no longer hide
        them, but widening it would hide every genuine same-day row too.  Only
        the named legacy IDs pass; an otherwise identical new ID still fails.
        """
        legacy = "SESSION-20261118-1be029"
        new = "SESSION-20261118-abcdef"
        errors: list[str] = []
        validate_seed.check_role_receipts(
            {legacy: {"session_id": legacy}, new: {"session_id": new}},
            errors,
            today=datetime.date(2026, 11, 18),
        )
        self.assertEqual(len(errors), 1)
        self.assertIn(new, errors[0])
        self.assertNotIn(legacy, errors[0])
        self.assertIn(legacy, validate_seed.ROLE_RECEIPT_LEGACY_EXEMPT_IDS)
        self.assertIn(
            "SESSION-20261118-291f45", validate_seed.ROLE_RECEIPT_LEGACY_EXEMPT_IDS
        )

    def test_the_live_ledger_passes_today(self) -> None:
        """The gate must not fire before its effective date on the real ledgers."""
        errors: list[str] = []
        sessions: dict[str, dict] = {}
        base = ROOT / "state" / "sessions.jsonl"
        paths = [base] + sorted((ROOT / "state" / "sessions.d").glob("*.jsonl"))
        for path in paths:
            if not path.is_file():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    sessions[row["session_id"]] = row
        validate_seed.check_role_receipts(sessions, errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
