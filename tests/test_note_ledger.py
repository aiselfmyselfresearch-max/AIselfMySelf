"""Tests for the notes ledger wiring: schema, FK checks, ID minting, shard creation.

The ``notes`` collection is what lets an episodic report in ``readings/`` be cited
from ``read_log`` and ``relations`` at all, so the interesting failures here are
the ones that would let a row point at a report that does not exist.
"""
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

BASE_FILES = (
    "questions.jsonl",
    "motifs.jsonl",
    "materials.jsonl",
    "fragments.jsonl",
    "relations.jsonl",
    "sessions.jsonl",
    "read_log.jsonl",
    "editorial_decisions.jsonl",
    "errata.jsonl",
    "notes.jsonl",
)

SESSION_ROW = {
    "session_id": "SESSION-20261102-aaaaaa",
    "started_at": "2026-11-02",
    "human_direction": "委任",
    "question_ids": ["Q-001"],
    "context_material_ids": [],
    "produced_fragment_ids": [],
    "new_question_ids": [],
    "prompt_template": "prompts/start.md",
}
QUESTION_ROW = {
    "question_id": "Q-001",
    "question": "人間とは何か。",
    "status": "open",
    "created_at": "2026-10-22",
    "origin": {"kind": "human_seed", "detail": "初期シード"},
    "motif_ids": [],
    "material_ids": [],
    "previous_question_ids": [],
}
NOTE_ROW = {
    "note_id": "NOTE-20261102-aaaaaa",
    "path": "readings/2026-11-02-oil.md",
    "session_id": "SESSION-20261102-aaaaaa",
    "created_at": "2026-11-02",
}


def make_repo(tmp: Path) -> Path:
    root = Path(tmp) / "repo"
    (root / "state").mkdir(parents=True)
    (root / "readings").mkdir()
    shutil.copytree(ROOT / "schema", root / "schema")
    shutil.copytree(
        ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    for filename in BASE_FILES:
        (root / "state" / filename).write_text("", encoding="utf-8")
    (root / "state" / "sessions.jsonl").write_text(
        json.dumps(SESSION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "state" / "questions.jsonl").write_text(
        json.dumps(QUESTION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "readings" / "2026-11-02-oil.md").write_text("# 北庇の油引き\n", encoding="utf-8")
    return root


def write_row(root: Path, collection: str, row: dict, *, name: str = "2026-11-02-aaaaaaaaaaaa") -> Path:
    shard_dir = root / "state" / f"{collection}.d"
    shard_dir.mkdir(exist_ok=True)
    shard = shard_dir / f"{name}.jsonl"
    existing = shard.read_text(encoding="utf-8") if shard.is_file() else ""
    shard.write_text(
        existing + json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return shard


def validate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/validate_seed.py"], cwd=root, capture_output=True, text=True, timeout=180
    )


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=root, capture_output=True, text=True, timeout=180
    )


class NoteValidationTests(unittest.TestCase):
    def test_a_valid_note_row_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", NOTE_ROW)
            result = validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("notes=1", result.stdout)

    def test_unknown_session_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", {**NOTE_ROW, "session_id": "SESSION-NOPE"})
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("notes:NOTE-20261102-aaaaaa: session_id references unknown session", result.stdout)

    def test_path_pointing_at_a_missing_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", {**NOTE_ROW, "path": "readings/2026-11-02-gone.md"})
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("path references a missing file", result.stdout)

    def test_path_escaping_the_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", {**NOTE_ROW, "path": "../outside.md"})
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("repository-relative without '..'", result.stdout)

    def test_claim_referencing_an_unknown_question_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(
                root,
                "notes",
                {
                    **NOTE_ROW,
                    "claims": [
                        {"claim_id": "CLM-1", "kind": "measured_fact", "text": "実測", "question_ids": ["Q-999"]}
                    ],
                },
            )
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("claims[0].question_ids references unknown questions ID", result.stdout)

    def test_claim_kind_outside_the_enum_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(
                root,
                "notes",
                {**NOTE_ROW, "claims": [{"claim_id": "CLM-1", "kind": "felt", "text": "…"}]},
            )
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("is not in enum", result.stdout)

    def test_supersedes_must_exist_and_target_the_same_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", {**NOTE_ROW, "supersedes": ["NOTE-GONE"]})
            self.assertIn("supersedes references unknown note ID", validate(root).stdout)

            root2 = make_repo(Path(tmp) / "b")
            (root2 / "readings" / "2026-11-02-other.md").write_text("# 他\n", encoding="utf-8")
            write_row(root2, "notes", {**NOTE_ROW, "note_id": "NOTE-1"})
            write_row(
                root2,
                "notes",
                {
                    **NOTE_ROW,
                    "note_id": "NOTE-2",
                    "path": "readings/2026-11-02-other.md",
                    "supersedes": ["NOTE-1"],
                },
                name="2026-11-02-bbbbbbbbbbbb",
            )
            result = validate(root2)
            self.assertEqual(result.returncode, 1)
            self.assertIn("supersedes note 'NOTE-1' is about", result.stdout)

    def test_supersedes_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", {**NOTE_ROW, "note_id": "NOTE-1", "supersedes": ["NOTE-2"]})
            write_row(
                root,
                "notes",
                {**NOTE_ROW, "note_id": "NOTE-2", "supersedes": ["NOTE-1"]},
                name="2026-11-02-bbbbbbbbbbbb",
            )
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("cycle detected in supersedes chain", result.stdout)


class NoteCitationTests(unittest.TestCase):
    """A note row is what makes a report citable from read_log and relations."""

    def test_read_log_can_target_a_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", NOTE_ROW)
            write_row(
                root,
                "read_log",
                {
                    "read_id": "READ-20261102-bbbbbb",
                    "session_id": "SESSION-20261102-aaaaaa",
                    "target": {"type": "note", "id": "NOTE-20261102-aaaaaa"},
                    "reading": "contested",
                    "note": "前の読みへ異議を返した。",
                    "created_at": "2026-11-02",
                },
            )
            result = validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_read_log_targeting_an_unregistered_note_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(
                root,
                "read_log",
                {
                    "read_id": "READ-20261102-bbbbbb",
                    "session_id": "SESSION-20261102-aaaaaa",
                    "target": {"type": "note", "id": "NOTE-20261102-aaaaaa"},
                    "reading": "interpreted",
                    "note": "…",
                    "created_at": "2026-11-02",
                },
            )
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("read_log:READ-20261102-bbbbbb: target references unknown note ID", result.stdout)

    def test_relation_can_join_a_note_and_a_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", NOTE_ROW)
            write_row(
                root,
                "relations",
                {
                    "relation_id": "REL-20261102-cccccc",
                    "left": {"type": "note", "id": "NOTE-20261102-aaaaaa"},
                    "relation_type": "responds_to",
                    "right": {"type": "question", "id": "Q-001"},
                    "note": "報告が問いへ応答した。",
                    "created_at": "2026-11-02",
                },
            )
            result = validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_editorial_decisions_still_cannot_target_a_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_row(root, "notes", NOTE_ROW)
            write_row(
                root,
                "editorial_decisions",
                {
                    "decision_id": "ED-20261102-dddddd",
                    "session_id": "SESSION-20261102-aaaaaa",
                    "target": {"type": "note", "id": "NOTE-20261102-aaaaaa"},
                    "status": "selected",
                    "reason": "…",
                    "created_at": "2026-11-02",
                },
            )
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("is not in enum", result.stdout)


class ToolingTests(unittest.TestCase):
    def test_new_id_mints_note_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            result = run(root, "tools/new_id.py", "NOTE", "--date", "20261102")
            self.assertEqual(result.returncode, 0, result.stderr)
            minted = result.stdout.strip()
            self.assertRegex(minted, r"^NOTE-20261102-[0-9a-f]{6}$")

    def test_new_ledger_shard_supports_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            result = run(root, "tools/new_ledger_shard.py", "notes", "--create", "--date", "2026-11-02")
            self.assertEqual(result.returncode, 0, result.stderr)
            created = list((root / "state" / "notes.d").glob("2026-11-02-*.jsonl"))
            self.assertEqual(len(created), 1)

    def test_notes_collection_is_registered(self) -> None:
        from validate_seed import COLLECTIONS

        self.assertIn("notes", COLLECTIONS)
        self.assertEqual(COLLECTIONS["notes"], ("notes.jsonl", "note_id", "note.schema.json"))


if __name__ == "__main__":
    unittest.main()
