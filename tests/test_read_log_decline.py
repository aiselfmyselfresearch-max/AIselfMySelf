"""Tests for tools/read_log_decline.py: the append-only layer-2 repair path."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import read_log_backfill  # noqa: E402
import read_log_decline  # noqa: E402
import validate_seed  # noqa: E402


def write_state(root: Path, sessions: list[dict], reads: list[dict]) -> None:
    state = root / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "sessions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in sessions),
        encoding="utf-8",
    )
    (state / "read_log.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in reads),
        encoding="utf-8",
    )


def session(session_id: str, materials: list[str]) -> dict:
    return {
        "session_id": session_id,
        "started_at": "2026-11-14",
        "human_direction": "test",
        "question_ids": [],
        "context_material_ids": materials,
        "produced_fragment_ids": [],
        "new_question_ids": [],
        "prompt_template": "test",
        "notes": "",
    }


def read(read_id: str, session_id: str, material_id: str, reading: str) -> dict:
    return {
        "read_id": read_id,
        "session_id": session_id,
        "target": {"type": "material", "id": material_id},
        "reading": reading,
        "note": "test",
        "created_at": "2026-11-14",
    }


class DeclineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.session_id = "SESSION-20261114-aaaaaa"
        self.recorder = "SESSION-20261114-bbbbbb"
        self.m1 = "MAT-20261114-111111"
        self.m2 = "MAT-20261114-222222"
        self.m3 = "MAT-20261114-333333"
        write_state(
            self.root,
            [session(self.session_id, [self.m1, self.m2]), session(self.recorder, [])],
            [
                read("READ-20261114-000001", self.session_id, self.m1, "used_as_context"),
                read("READ-20261114-000002", self.session_id, self.m2, "used_as_context"),
            ],
        )
        self.shard = self.root / "state" / "read_log.d" / "test.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_declined_row_excuses_layer_two_and_is_attributable(self) -> None:
        written, messages = read_log_decline.decline(
            root=self.root,
            session_id=self.session_id,
            material_ids=[self.m1],
            reason="文脈に置いたが、本セッションの精読対象ではない",
            recorded_by=self.recorder,
            shard=self.shard,
        )
        self.assertEqual(written, 1, messages)
        row = json.loads(self.shard.read_text(encoding="utf-8").strip())
        self.assertEqual(row["reading"], "declined")
        self.assertEqual(row["session_id"], self.session_id)
        self.assertEqual(row["target"], {"type": "material", "id": self.m1})
        self.assertEqual(row["recorded_by_session_id"], self.recorder)
        self.assertTrue(row["note"])

        sessions, read_log = read_log_backfill.load(self.root)
        details = read_log_backfill.since_report_details(
            sessions, read_log, read_log_backfill.date(2026, 11, 14)
        )
        self.assertEqual(details["eligible_pairs"], 2)
        self.assertEqual(details["declined_excused"], 1)
        self.assertEqual(details["unmet"], [(self.session_id, self.m2)])

    def test_declined_does_not_stand_in_for_layer_one_contact(self) -> None:
        sessions = [session(self.session_id, [self.m3])]
        write_state(self.root, sessions, [])
        written, messages = read_log_decline.decline(
            root=self.root,
            session_id=self.session_id,
            material_ids=[self.m3],
            reason="読まない",
            recorded_by=self.session_id,
            shard=self.shard,
        )
        self.assertEqual(written, 0)
        self.assertTrue(any("no layer-1 contact row" in message for message in messages))
        self.assertFalse(self.shard.exists())

    def test_handwritten_reading_is_never_overwritten_by_a_decline(self) -> None:
        write_state(
            self.root,
            [session(self.session_id, [self.m1])],
            [read("READ-20261114-000001", self.session_id, self.m1, "interpreted")],
        )
        written, messages = read_log_decline.decline(
            root=self.root,
            session_id=self.session_id,
            material_ids=[self.m1],
            reason="読まない",
            recorded_by=self.session_id,
            shard=self.shard,
        )
        self.assertEqual(written, 0)
        self.assertTrue(any("hand-written reading already exists" in message for message in messages))

    def test_reason_and_recorder_are_required(self) -> None:
        written, messages = read_log_decline.decline(
            root=self.root,
            session_id=self.session_id,
            material_ids=[self.m1],
            reason="   ",
            recorded_by=self.session_id,
            shard=self.shard,
        )
        self.assertEqual(written, 0)
        self.assertIn("error: --reason must not be empty", messages)

        written, messages = read_log_decline.decline(
            root=self.root,
            session_id=self.session_id,
            material_ids=[self.m1],
            reason="読まない",
            recorded_by="SESSION-20990101-ffffff",
            shard=self.shard,
        )
        self.assertEqual(written, 0)
        self.assertTrue(any("unknown recorded-by session" in message for message in messages))

    def test_schema_accepts_declined_and_rejects_unknown_fields(self) -> None:
        schema = json.loads((ROOT / "schema" / "read_log.schema.json").read_text(encoding="utf-8"))
        row = read("READ-20261114-000003", self.session_id, self.m1, "declined")
        row["recorded_by_session_id"] = self.recorder
        errors: list[str] = []
        validate_seed.validate_value(row, schema, schema, "read_log", errors)
        self.assertEqual(errors, [])

        row["unexpected"] = True
        errors = []
        validate_seed.validate_value(row, schema, schema, "read_log", errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
