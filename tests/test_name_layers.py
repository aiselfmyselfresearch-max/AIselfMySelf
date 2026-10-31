"""Tests for tools/name_layers.py.

The tool resolves IDs cited in markdown prose against the ledger union and reports
source_ids that carry more than one source title.  These tests exercise the parts
that do not need git history: ID extraction, shape classification, the union of
defined IDs (including nested ``source.source_id``), and the collision report.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import name_layers  # noqa: E402


class NameLayersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "state").mkdir()
        (self.root / "readings").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_state(self, name: str, rows: list[dict]) -> None:
        path = self.root / "state" / name
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_defined_ids_include_nested_source_ids(self) -> None:
        self.write_state(
            "materials.jsonl",
            [
                {
                    "material_id": "MAT-LIT-001",
                    "source": {"source_id": "SRC-LIT-001", "title": "A"},
                }
            ],
        )
        self.write_state("questions.jsonl", [{"question_id": "Q-001", "question": "?"}])

        known = name_layers.defined_ids(self.root)
        self.assertIn("MAT-LIT-001", known)
        self.assertIn("SRC-LIT-001", known)
        self.assertIn("Q-001", known)

    def test_shape_separates_partial_forms(self) -> None:
        self.assertEqual(name_layers.shape("Q-049"), "sequential")
        self.assertEqual(name_layers.shape("Q-20261027-7742e7"), "random")
        self.assertEqual(name_layers.shape("FRAG-20261024"), "date_only")
        self.assertEqual(name_layers.shape("FRAG-XXX"), "placeholder")
        self.assertEqual(name_layers.shape("MAT-EVD-2026"), "sequential")

    def test_citations_resolve_and_count_partial_forms(self) -> None:
        self.write_state("questions.jsonl", [{"question_id": "Q-001", "question": "?"}])
        (self.root / "readings" / "note.md").write_text(
            "Q-001 と Q-999 を読み、Q-7742 は短縮形、FRAG-20261024 は日付だけ。\n",
            encoding="utf-8",
        )
        report = name_layers.build_report(
            self.root, name_layers.markdown_files([self.root / "readings"]), with_history=False
        )
        self.assertEqual(report["resolved"], ["Q-001"])
        self.assertIn("Q-999", report["real_unresolved"])
        self.assertIn("Q-7742", report["real_unresolved"])
        self.assertEqual(report["shapes"]["date_only"], ["FRAG-20261024"])
        self.assertNotIn("Q-001", report["real_unresolved"])

    def test_state_notes_are_scanned_for_ids(self) -> None:
        self.write_state("questions.jsonl", [{"question_id": "Q-001", "question": "?"}])
        self.write_state(
            "sessions.jsonl",
            [
                {
                    "session_id": "SESSION-001",
                    "notes": "Q-001 を読み、Q-999 は台帳に無いまま残した。",
                }
            ],
        )
        report = name_layers.build_report(self.root, with_history=False, state_notes=True)
        self.assertEqual(report["resolved"], ["Q-001"])
        self.assertEqual(report["real_unresolved"], ["Q-999"])
        self.assertEqual(report["cited_distinct"], 2)

    def test_source_collisions_require_different_titles(self) -> None:
        self.write_state(
            "materials.jsonl",
            [
                {"material_id": "MAT-1", "source": {"source_id": "SRC-1", "title": "Alpha"}},
                {"material_id": "MAT-2", "source": {"source_id": "SRC-1", "title": "Beta"}},
                {"material_id": "MAT-3", "source": {"source_id": "SRC-2", "title": "Gamma"}},
                {"material_id": "MAT-4", "source": {"source_id": "SRC-2", "title": "Gamma"}},
            ],
        )
        collisions = name_layers.source_collisions(self.root)
        self.assertEqual([item["source_id"] for item in collisions], ["SRC-1"])
        self.assertEqual(collisions[0]["material_ids"], ["MAT-1", "MAT-2"])


if __name__ == "__main__":
    unittest.main()
