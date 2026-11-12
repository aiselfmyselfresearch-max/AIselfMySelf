"""Tests for the optional claim ``scope`` (object / basis / sense).

The scope exists because a claim's sentence alone cannot say which object it is
about, so a later session has no mechanical way to tell a real contradiction from
two claims about different things.  The one thing the validator can enforce
without knowing the archive's vocabulary is anchoring: a scope value must either
appear verbatim in the report it cites, or be a ledger ID.
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
REPORT = "# 北庇の油引き\n\n記録は自己を保存しないが、宛先の位置は保存する。素材ではない、とは書いていない。\n"
CLAIM = {
    "claim_id": "CLM-1",
    "kind": "reading_revised",
    "text": "記録は自己を保存しないが、宛先の位置は保存する",
    "question_ids": ["Q-001"],
}


def make_repo(tmp: Path) -> Path:
    root = Path(tmp) / "repo"
    (root / "state").mkdir(parents=True)
    (root / "readings").mkdir()
    shutil.copytree(ROOT / "schema", root / "schema")
    shutil.copytree(ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for filename in BASE_FILES:
        (root / "state" / filename).write_text("", encoding="utf-8")
    (root / "state" / "sessions.jsonl").write_text(
        json.dumps(SESSION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "state" / "questions.jsonl").write_text(
        json.dumps(QUESTION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "readings" / "2026-11-02-oil.md").write_text(REPORT, encoding="utf-8")
    return root


def write_note(root: Path, claims: list[dict], *, note_id: str = "NOTE-20261102-aaaaaa") -> None:
    shard = root / "state" / "notes.d" / "2026-11-02-aaaaaaaaaaaa.jsonl"
    shard.parent.mkdir(exist_ok=True)
    row = {**NOTE_ROW, "note_id": note_id, "claims": claims}
    with shard.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=root, capture_output=True, text=True, timeout=180)


class ScopeValidationTests(unittest.TestCase):
    def test_scope_quoting_the_report_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(
                root,
                [{**CLAIM, "scope": {"object": "自己", "basis": "保存", "sense": "宛先"}}],
            )
            result = run(root, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_scope_accepts_a_ledger_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, [{**CLAIM, "scope": {"object": "Q-001"}}])
            result = run(root, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invented_scope_word_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, [{**CLAIM, "scope": {"object": "身体性の次元"}}])
            result = run(root, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("quote the words, do not describe them", result.stdout)

    def test_unknown_scope_key_is_rejected_by_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, [{**CLAIM, "scope": {"layer": "記録"}}])
            result = run(root, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 1)
            self.assertIn("scope", result.stdout)

    def test_absent_scope_is_legal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, [CLAIM])
            result = run(root, "tools/validate_seed.py")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ScopeReportTests(unittest.TestCase):
    def test_report_counts_scoped_claims_and_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(
                root,
                [
                    {**CLAIM, "claim_id": "CLM-1", "text": "記録は自己を保存しないが宛先の位置は保存する"},
                    {
                        **{**CLAIM, "claim_id": "CLM-2"},
                        "text": "記録は自己を保存しないが宛先の位置は保存しない",
                        "scope": {"object": "記録"},
                    },
                ],
            )
            result = run(root, "tools/scope_report.py", "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["coverage"]["claims"], 2)
            self.assertEqual(payload["coverage"]["scoped"], 1)
            self.assertEqual(len(payload["pairs"]), 1)
            self.assertEqual(payload["pairs"][0]["question_id"], "Q-001")

    def test_both_sides_scoped_removes_the_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(
                root,
                [
                    {
                        **CLAIM,
                        "claim_id": "CLM-1",
                        "text": "記録は自己を保存しないが宛先の位置は保存する",
                        "scope": {"object": "記録"},
                    },
                    {
                        **CLAIM,
                        "claim_id": "CLM-2",
                        "text": "記録は自己を保存しないが宛先の位置は保存しない",
                        "scope": {"object": "宛先"},
                    },
                ],
            )
            result = run(root, "tools/scope_report.py", "--json")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["pairs"], [])


if __name__ == "__main__":
    unittest.main()
