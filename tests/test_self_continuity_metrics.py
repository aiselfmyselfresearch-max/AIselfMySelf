"""Tests for tools/self_continuity_metrics.py — the archive's self-measurement.

The report readings/2026-11-20-where-continuity-is-recorded-a-measurement.md
depends on four numbers this tool computes: the central-question share, the
verbatim share, the consecutive-session overlap, and the count of experiential
ledger keys.  These tests pin the arithmetic on a tiny fixture and the shape of
the real-tree output, so a future refactor cannot silently change the numbers
that the evaluations cite.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import self_continuity_metrics as scm  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )


class FixtureMeasureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_jsonl(
            self.root / "state" / "read_log.jsonl",
            [
                {
                    "read_id": "R1",
                    "target": {"type": "question", "id": "Q-001"},
                    "reading": "quoted",
                },
                {
                    "read_id": "R2",
                    "target": {"type": "question", "id": "Q-002"},
                    "reading": "interpreted",
                },
                {
                    "read_id": "R3",
                    "target": {"type": "material", "id": "MAT-X"},
                    "reading": "reinterpreted",
                    "in_reply_to": "R1",
                },
            ],
        )
        write_jsonl(
            self.root / "state" / "sessions.jsonl",
            [
                {"session_id": "S1", "started_at": "2026-11-01", "context_material_ids": ["MAT-A"]},
                {"session_id": "S2", "started_at": "2026-11-02", "context_material_ids": ["MAT-B"]},
                {"session_id": "S3", "started_at": "2026-11-03", "context_material_ids": ["MAT-C"]},
            ],
        )
        write_jsonl(
            self.root / "state" / "materials.jsonl",
            [
                {"material_id": "MAT-X", "title": "A text", "verification": {"status": "verified"}},
                {"material_id": "MAT-LIT-001", "title": "Another"},
            ],
        )
        self._saved = scm.ROOT
        scm.ROOT = str(self.root)

    def tearDown(self) -> None:
        scm.ROOT = self._saved
        self.tmp.cleanup()

    def test_shares_are_computed_from_rows(self) -> None:
        data = scm.measure()
        self.assertEqual(data["read_log_rows"], 3)
        self.assertEqual(data["central_question_rows"], 2)
        self.assertAlmostEqual(data["central_question_pct"], 66.7)
        self.assertAlmostEqual(data["verbatim_pct"], 33.3)
        self.assertAlmostEqual(data["reconstructive_pct"], 66.7)
        self.assertEqual(data["in_reply_to_rows"], 1)
        self.assertAlmostEqual(data["in_reply_to_pct"], 33.3)

    def test_consecutive_sessions_with_disjoint_context_count_as_zero_overlap(self) -> None:
        data = scm.measure()
        self.assertEqual(data["session_pairs"], 2)
        self.assertEqual(data["zero_overlap_pairs"], 2)
        self.assertAlmostEqual(data["zero_overlap_pct"], 100.0)
        self.assertEqual(data["mean_jaccard"], 0.0)

    def test_materials_and_keys_are_summarised(self) -> None:
        data = scm.measure()
        self.assertEqual(data["materials_read"], 1)
        self.assertEqual(data["top_materials"][0]["material_id"], "MAT-X")
        self.assertEqual(data["experiential_keys"], [])
        self.assertGreater(data["top_level_keys"], 0)


class RealTreeTests(unittest.TestCase):
    def test_real_tree_measures_six_metrics_in_range(self) -> None:
        data = scm.measure()
        self.assertGreater(data["read_log_rows"], 0)
        for key in (
            "central_question_pct",
            "verbatim_pct",
            "reconstructive_pct",
            "zero_overlap_pct",
        ):
            self.assertGreaterEqual(data[key], 0.0)
            self.assertLessEqual(data[key], 100.0)
        self.assertLessEqual(len(data["top_materials"]), 20)
        self.assertEqual(data["experiential_keys"], [])

    def test_render_names_the_report_and_carries_the_numbers(self) -> None:
        text = scm.render(scm.measure())
        self.assertIn("自己の連続は、どこに記録されているか", text)
        self.assertIn("read_log 行数", text)
        self.assertIn("感覚・感情を名指す鍵", text)


if __name__ == "__main__":
    unittest.main()
