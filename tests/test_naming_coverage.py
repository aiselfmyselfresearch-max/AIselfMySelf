"""Tests for tools/naming_coverage.py.

The tool exists because a report can read a material, cite its DOI, and still
never write its `material_id`.  These tests build a throwaway tree with one
lowercase-hex id, one legacy id, one report that names only the legacy one, and
read_log rows of both kinds (hand-written and mechanical backfill), then check
that the counts distinguish all four cases.
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

import naming_coverage  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                    encoding="utf-8")


class NamingAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "readings").mkdir()
        write_jsonl(self.root / "state" / "materials.jsonl", [
            {"material_id": "MAT-LIT-001", "title": "legacy",
             "origin": {"source_record_path": "readings/a.md"}},
            {"material_id": "MAT-20261025-0b9965", "title": "lowercase hex",
             "origin": {"source_record_path": "readings/a.md"}},
            {"material_id": "MAT-EVD-20261106-pavlov-27", "title": "in no report",
             "origin": {"source_record_path": "readings/missing.md"}},
        ])
        (self.root / "readings" / "a.md").write_text(
            "# a\n\nこの資料（MAT-LIT-001）と、あの資料を読んだ。\n", encoding="utf-8")
        write_jsonl(self.root / "state" / "read_log.jsonl", [
            {"read_id": "READ-1", "target": {"type": "material", "id": "MAT-20261025-0b9965"},
             "reading": "interpreted", "note": "手で書いた行"},
            {"read_id": "READ-2", "target": {"type": "material", "id": "MAT-EVD-20261106-pavlov-27"},
             "reading": "used_as_context", "note": "機械的バックフィル"},
        ])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def audit(self) -> dict:
        return naming_coverage.audit(self.root)

    def test_lowercase_hex_id_counts_as_named(self) -> None:
        # MAT-20261025-0b9965 is NOT in a.md, but a case-insensitive search of the
        # whole readings/ tree must still see it when it is present elsewhere.
        (self.root / "readings" / "b.md").write_text(
            "名前は `MAT-20261025-0b9965` である。\n", encoding="utf-8")
        result = self.audit()
        self.assertEqual(result["cited_case_insensitive"], 2)
        # The uppercase-only convention cannot match the lowercase id at all.
        self.assertLess(result["cited_uppercase_only"], result["cited_case_insensitive"])
        # Only the legacy MAT-LIT-001 is matchable by MAT-[A-Z0-9-]+.
        self.assertEqual(result["ids_uppercase_cannot_match"], 2)

    def test_hand_row_without_a_name_is_counted(self) -> None:
        result = self.audit()
        # Neither MAT-20261025-0b9965 nor MAT-EVD-20261106-pavlov-27 is written
        # in a.md; only the pavlov row has a hand-written read_log row.
        self.assertEqual(result["never_named"], 2)
        self.assertEqual(result["never_named_read_but_unnamed"], 1)
        self.assertIn("MAT-EVD-20261106-pavlov-27", result["never_ids"])
        self.assertNotIn("MAT-LIT-001", result["never_ids"])

    def test_backfill_only_row_is_not_a_reading(self) -> None:
        write_jsonl(self.root / "state" / "read_log.jsonl", [
            {"read_id": "READ-2", "target": {"type": "material", "id": "MAT-EVD-20261106-pavlov-27"},
             "reading": "used_as_context", "note": "機械的バックフィル"},
        ])
        result = self.audit()
        self.assertEqual(result["never_named_read_but_unnamed"], 0)

    def test_own_report_naming(self) -> None:
        result = self.audit()
        # MAT-LIT-001 and MAT-20261025-0b9965 both point at readings/a.md,
        # which names only the first.  The third points at a file that is gone.
        self.assertEqual(result["own_report_total"], 2)
        self.assertEqual(result["own_report_named"], 1)
        self.assertEqual([x["material_id"] for x in result["own_missing_top"]],
                         ["MAT-20261025-0b9965"])

    def test_render_mentions_both_counts(self) -> None:
        text = naming_coverage.render(self.audit(), limit=5)
        self.assertIn("case-insensitive", text)
        self.assertIn("uppercase-only", text)


if __name__ == "__main__":
    unittest.main()
