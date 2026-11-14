"""Tests for tools/layer2_accounting.py (stdlib only)."""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import layer2_accounting  # noqa: E402


def session(session_id: str, materials: list[str], notes: str = "") -> dict:
    return {
        "session_id": session_id,
        "started_at": "2026-11-10",
        "human_direction": "test",
        "question_ids": [],
        "context_material_ids": materials,
        "produced_fragment_ids": [],
        "new_question_ids": [],
        "prompt_template": "test",
        "notes": notes,
    }


def read(read_id: str, session_id: str, material_id: str, reading: str) -> dict:
    return {
        "read_id": read_id,
        "session_id": session_id,
        "target": {"type": "material", "id": material_id},
        "reading": reading,
        "note": "test",
        "created_at": "2026-11-10",
    }


class Layer2AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m1 = "MAT-20261110-aaaaaa"
        self.m2 = "MAT-20261110-bbbbbb"
        self.m3 = "MAT-20261110-cccccc"
        self.m4 = "MAT-20261110-dddddd"
        self.sessions = {
            "SESSION-20261110-aaaaaa": session(
                "SESSION-20261110-aaaaaa", [self.m1, self.m2]
            ),
            "SESSION-20261110-bbbbbb": session(
                "SESSION-20261110-bbbbbb", [self.m3, self.m4]
            ),
        }
        self.read_log = {
            "READ-20261110-000001": read(
                "READ-20261110-000001", "SESSION-20261110-aaaaaa", self.m1, "interpreted"
            ),
            "READ-20261110-000002": read(
                "READ-20261110-000002", "SESSION-20261110-aaaaaa", self.m2, "summarized"
            ),
            "READ-20261110-000003": read(
                "READ-20261110-000003", "SESSION-20261110-bbbbbb", self.m3, "used_as_context"
            ),
        }

    def test_unmet_and_context_only_are_distinguished(self) -> None:
        rows = layer2_accounting.audit_records(
            self.sessions, self.read_log, date(2026, 11, 10)
        )
        by_id = {row["session_id"]: row for row in rows}
        first = by_id["SESSION-20261110-aaaaaa"]
        second = by_id["SESSION-20261110-bbbbbb"]
        self.assertEqual((first["handwritten"], first["unmet"]), (2, 0))
        self.assertEqual((second["handwritten"], second["unmet"]), (0, 2))
        self.assertEqual(second["context_only"], 1)
        self.assertEqual(second["unmet_without_row"], 1)

    def test_unread_choice_is_counted_as_excused_not_unmet(self) -> None:
        self.sessions["SESSION-20261110-bbbbbb"]["notes"] = (
            f"未読の選択: {self.m3}, {self.m4}"
        )
        rows = layer2_accounting.audit_records(
            self.sessions, self.read_log, date(2026, 11, 10)
        )
        second = {row["session_id"]: row for row in rows}["SESSION-20261110-bbbbbb"]
        self.assertEqual((second["excused"], second["unmet"]), (2, 0))

    def test_rows_are_ordered_by_date_then_session_id(self) -> None:
        self.sessions["SESSION-20261109-cccccc"] = session(
            "SESSION-20261109-cccccc", [self.m1]
        )
        rows = layer2_accounting.audit_records(
            self.sessions, self.read_log, date(2026, 11, 9)
        )
        self.assertEqual(
            [row["session_id"] for row in rows],
            [
                "SESSION-20261109-cccccc",
                "SESSION-20261110-aaaaaa",
                "SESSION-20261110-bbbbbb",
            ],
        )

    def test_summary_keeps_first_ten_and_totals(self) -> None:
        rows = layer2_accounting.audit_records(
            self.sessions, self.read_log, date(2026, 11, 10)
        )
        summary = layer2_accounting.summarize(rows)
        self.assertEqual(summary["eligible_sessions"], 2)
        self.assertEqual(summary["total_pairs"], 4)
        self.assertEqual(summary["handwritten_pairs"], 2)
        self.assertEqual(summary["unmet_pairs"], 2)
        self.assertEqual(summary["context_only_pairs"], 1)
        self.assertEqual(len(summary["first_ten"]), 2)


if __name__ == "__main__":
    unittest.main()
