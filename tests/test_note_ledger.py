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


OTHER_SESSION_ROW = dict(SESSION_ROW, session_id="SESSION-20261103-bbbbbb", started_at="2026-11-03")


def note(suffix: str, *, day: str = "20261102", session: str = SESSION_ROW["session_id"], **extra) -> dict:
    row = {
        "note_id": f"NOTE-{day}-{suffix}",
        "path": NOTE_ROW["path"],
        "session_id": session,
        "created_at": f"{day[:4]}-{day[4:6]}-{day[6:]}",
    }
    row.update(extra)
    return row


class NoteBrakeTests(unittest.TestCase):
    """The three brakes added on 2026-11-12 (tools/validate_seed.py, check_note_brakes).

    One session wrote 859 note rows in two days.  Most were made from excerpts,
    56 of them sat on top of another session's deeper reading of the same
    report, and 318 carried a created_at later than the day they were written.
    Nothing stopped it, because each row was valid on its own.
    """

    def make(self, tmp: str) -> Path:
        root = make_repo(Path(tmp))
        write_row(root, "sessions", OTHER_SESSION_ROW)
        return root

    def test_twelve_rows_from_one_session_pass_and_the_thirteenth_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            for index in range(13):
                (root / "readings" / f"r{index:02d}.md").write_text("# r\n", encoding="utf-8")
            for index in range(12):
                write_row(root, "notes", note(f"{index:06x}", path=f"readings/r{index:02d}.md"))
            self.assertEqual(validate(root).returncode, 0)
            write_row(root, "notes", note(f"{12:06x}", path="readings/r12.md"))
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("has 13 note rows; one session may write at most 12", result.stdout)

    def test_a_shallower_reading_cannot_be_put_over_another_sessions_deeper_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="full_text_read"))
            later = note(
                "bbbbbb", day="20261103", session=OTHER_SESSION_ROW["session_id"],
                read_depth="excerpt_and_metadata_read",
            )
            write_row(root, "notes", later)
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("NOTE-20261103-bbbbbb: read_depth 'excerpt_and_metadata_read' is shallower", result.stdout)

    def test_omitting_read_depth_does_not_get_around_the_depth_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="excerpt_and_metadata_read"))
            write_row(root, "notes", note("bbbbbb", day="20261103", session=OTHER_SESSION_ROW["session_id"]))
            self.assertEqual(validate(root).returncode, 1)

    def test_an_equally_deep_or_deeper_reading_may_follow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="excerpt_and_metadata_read"))
            write_row(
                root, "notes",
                note("bbbbbb", day="20261103", session=OTHER_SESSION_ROW["session_id"],
                     read_depth="full_text_read", supersedes=["NOTE-20261102-aaaaaa"]),
            )
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_a_session_may_follow_its_own_deeper_row_with_a_shallower_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="full_text_read"))
            write_row(root, "notes", note("bbbbbb", day="20261103", read_depth="excerpt_and_metadata_read"))
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)

    def test_same_day_rows_are_compared_only_when_one_names_the_other(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="full_text_read"))
            same_day = note(
                "bbbbbb", session=OTHER_SESSION_ROW["session_id"], read_depth="excerpt_and_metadata_read"
            )
            write_row(root, "notes", same_day, name="2026-11-02-bbbbbbbbbbbb")
            self.assertEqual(validate(root).returncode, 0, "two sessions working on the same day cannot see each other")
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", read_depth="full_text_read"))
            write_row(root, "notes", dict(same_day, supersedes=["NOTE-20261102-aaaaaa"]))
            self.assertEqual(validate(root).returncode, 1, "naming a row in supersedes is a claim to replace it")

    def test_created_at_may_not_run_ahead_of_the_day_in_the_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", day="20261112", created_at="2026-11-20T00:00:00Z"))
            result = validate(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("created_at '2026-11-20T00:00:00Z' is later than the date in its own ID", result.stdout)

    def test_created_at_just_after_midnight_and_old_labelled_rows_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make(tmp)
            write_row(root, "notes", note("aaaaaa", day="20261112", created_at="2026-11-13T00:05:00Z"))
            (root / "readings" / "old.md").write_text("# old\n", encoding="utf-8")
            write_row(
                root, "notes",
                note("bbbbbb", day="20261103", path="readings/old.md", created_at="2027-01-22"),
            )
            self.assertEqual(validate(root).returncode, 0, validate(root).stdout)


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
