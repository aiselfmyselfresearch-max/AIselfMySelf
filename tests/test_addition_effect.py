"""Tests for tools/addition_effect.py — classification output against reading.

The tool answers one question without judging prose: after an addition, did the
archive produce more classification-shaped rows per handwritten reading?  These
tests pin the bucketing, the exclusion of the mechanical ``used_as_context``
backfill, and the ``--since`` filter, because all three decide the number.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import addition_effect  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


class CohortTests(unittest.TestCase):
    def test_cohorts_are_fixed_width(self) -> None:
        self.assertEqual(
            addition_effect.cohort_of("2026-11-01", 7),
            addition_effect.cohort_of("2026-11-03", 7),
        )

    def test_adjacent_days_can_fall_in_different_cohorts(self) -> None:
        self.assertNotEqual(
            addition_effect.cohort_of("2026-11-07", 7),
            addition_effect.cohort_of("2026-11-08", 7),
        )

    def test_day_parses_iso_and_rejects_garbage(self) -> None:
        self.assertEqual(addition_effect._day({"created_at": "2026-11-15T00:00:00Z"}), "2026-11-15")
        self.assertEqual(addition_effect._day({"created_at": "20260601"}), "2026-06-01")
        self.assertIsNone(addition_effect._day({"created_at": "not a date"}))


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        state = self.root / "state"
        state.mkdir()
        write_jsonl(state / "notes.jsonl", [
            {"note_id": "NOTE-1", "session_id": "S", "path": "readings/a.md", "created_at": "2026-11-02",
             "claims": [
                 {"claim_id": "C1", "kind": "reading_revised", "text": "人間の分類をやり直した"},
                 {"claim_id": "C2", "kind": "measured_fact", "text": "測った"},
             ]},
            {"note_id": "NOTE-2", "session_id": "S", "path": "readings/b.md", "created_at": "2026-11-20",
             "claims": [{"claim_id": "C3", "kind": "reading_held", "text": "保留した"}]},
        ])
        write_jsonl(state / "read_log.jsonl", [
            {"read_id": "R1", "session_id": "S", "target": {"type": "material", "id": "MAT-1"},
             "reading": "interpreted", "note": "本文を読んだ", "created_at": "2026-11-02"},
            {"read_id": "R2", "session_id": "S", "target": {"type": "material", "id": "MAT-2"},
             "reading": "used_as_context", "note": "機械的バックフィル（接触の記録）", "created_at": "2026-11-02"},
            {"read_id": "R3", "session_id": "S", "target": {"type": "material", "id": "MAT-3"},
             "reading": "interpreted", "note": "読んだ", "created_at": "2026-11-20"},
        ])
        write_jsonl(state / "errata.jsonl", [{"errata_id": "ERR-1", "created_at": "2026-11-03", "status": "open"}])
        write_jsonl(state / "editorial_decisions.jsonl", [{"decision_id": "ED-1", "created_at": "2026-11-21"}])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_counts_and_backfill_exclusion(self) -> None:
        report = addition_effect.build_effect_report(root=self.root, cohort_days=7)
        self.assertEqual(report["totals"]["claims"], 3)
        self.assertEqual(report["totals"]["classification_claims"], 1)
        self.assertEqual(report["totals"]["adjudication_rows"], 2)
        # Two interpreted rows; the backfill row is contact, not reading.
        self.assertEqual(report["totals"]["handwritten_reads"], 2)

    def test_since_filters_rows(self) -> None:
        report = addition_effect.build_effect_report(root=self.root, since="2026-11-15", cohort_days=7)
        self.assertEqual(report["totals"]["claims"], 1)
        self.assertEqual(report["totals"]["adjudication_rows"], 1)
        self.assertEqual(report["totals"]["handwritten_reads"], 1)

    def test_ratio_is_none_without_reads(self) -> None:
        report = addition_effect.build_effect_report(root=self.root, since="2027-01-01", cohort_days=7)
        self.assertEqual(report["cohorts"], [])
        self.assertEqual(report["totals"]["handwritten_reads"], 0)
        self.assertIsNone(report["totals"]["per_read"])

    def test_examples_respect_limit_and_carry_text(self) -> None:
        report = addition_effect.build_effect_report(root=self.root, cohort_days=7, limit=1)
        self.assertEqual(len(report["examples"]), 1)
        self.assertIn("分類", report["examples"][0]["text"])

    def test_render_keeps_the_disclaimer(self) -> None:
        text = addition_effect.render(addition_effect.build_effect_report(root=self.root))
        self.assertIn("達成目標でも品質判定でもありません", text)
        self.assertIn("2027-", text)


if __name__ == "__main__":
    unittest.main()
