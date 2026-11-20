"""Tests for tools/self_continuity_metrics.py — the archive's self-measurement.

The two 2026-11-20 reports depend on these numbers: the central-question
share, the reading-label share, the label-ordered session overlap (declared
context and typed material records), the threshold cohort, and the count of
matching top-level keys. The tests pin the arithmetic on a fixture and the
shape of the real-tree output, so a refactor
cannot silently change a number that an evaluation cites.
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
                    "session_id": "S1",
                    "target": {"type": "material", "id": "MAT-X"},
                    "reading": "quoted",
                    "created_at": "2026-11-01",
                },
                {
                    "read_id": "R2",
                    "session_id": "S2",
                    "target": {"type": "question", "id": "Q-002"},
                    "reading": "interpreted",
                    "created_at": "2026-11-02",
                },
                {
                    "read_id": "R3",
                    "session_id": "S3",
                    "target": {"type": "material", "id": "MAT-LIT-001"},
                    "reading": "used_as_context",
                    "created_at": "2026-11-03",
                    "in_reply_to": ["R1"],
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
        self.assertEqual(data["central_question_rows"], 1)
        self.assertAlmostEqual(data["central_question_pct"], 33.3)
        self.assertAlmostEqual(data["verbatim_pct"], 33.3)
        self.assertAlmostEqual(data["reconstructive_pct"], 33.3)
        self.assertEqual(data["in_reply_to_rows"], 1)
        self.assertAlmostEqual(data["in_reply_to_pct"], 33.3)

    def test_declared_context_overlap_counts_disjoint_pairs(self) -> None:
        data = scm.measure()
        declared = data["declared_context_overlap"]
        self.assertEqual(declared["pairs"], 2)
        self.assertEqual(declared["zero_overlap"], 2)
        self.assertAlmostEqual(declared["zero_overlap_pct"], 100.0)
        self.assertEqual(declared["mean_jaccard"], 0.0)

    def test_read_materials_overlap_ignores_context_only_rows(self) -> None:
        data = scm.measure()
        handwritten = data["read_materials_overlap"]
        every = data["all_read_materials_overlap"]
        # S1 read MAT-X by hand; S3 only carried MAT-LIT-001 as context, so the
        # pair (S2, S3) has no handwritten material on either side and is not a
        # pair at all, while (S1, S2) is a pair with zero shared materials.
        self.assertEqual(handwritten["pairs"], 1)
        self.assertEqual(handwritten["zero_overlap"], 1)
        self.assertEqual(every["pairs"], 2)
        self.assertEqual(every["zero_overlap"], 2)

    def test_declined_is_not_a_layer2_read_but_counted_is_an_audit_record(self) -> None:
        path = self.root / "state" / "read_log.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        rows.extend([
            {"read_id": "R4", "session_id": "S2", "target": {"type": "material", "id": "MAT-X"},
             "reading": "declined", "created_at": "2026-11-02"},
            {"read_id": "R5", "session_id": "S3", "target": {"type": "material", "id": "MAT-LIT-001"},
             "reading": "counted", "created_at": "2026-11-03"},
        ])
        write_jsonl(path, rows)
        data = scm.measure()
        self.assertEqual(data["read_materials_overlap"]["pairs"], 2)
        self.assertEqual(data["read_materials_overlap"]["zero_overlap"], 2)
        self.assertEqual(data["all_read_materials_overlap"]["zero_overlap"], 1)
        self.assertIn("including counted", data["method"]["read_materials_overlap"])
        self.assertIn("both sets empty are excluded", data["method"]["overlap_pairs"])
        self.assertIn("not matched", data["method"]["exposure_cohort"])

    def test_key_search_is_top_level_only_and_does_not_assume_no_matches(self) -> None:
        path = self.root / "state" / "read_log.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        rows[0]["emotion_signal"] = "present as a key name"
        rows[0]["nested"] = {"affect_only_inside": True}
        write_jsonl(path, rows)
        data = scm.measure()
        self.assertEqual(data["experiential_keys"], ["emotion_signal"])
        self.assertIn("top-level key names only", data["method"]["experiential_keys"])

    def test_exposure_cohort_is_empty_when_the_archive_is_too_short(self) -> None:
        cohort = scm.measure()["exposure_cohort"]
        self.assertEqual(cohort["cohort_size"], 0)
        self.assertEqual(cohort["top20_literary"], 0)


class ExposureCohortTests(unittest.TestCase):
    def test_minimum_exposure_cohort_splits_literary_from_other(self) -> None:
        sessions = [
            {"session_id": f"S{i}", "started_at": f"2026-01-{1 + i % 28:02d}"} for i in range(305)
        ]
        read_log = [
            {"session_id": "S1", "target": {"type": "material", "id": "MAT-LIT-001"},
             "reading": "interpreted", "created_at": "2026-01-01"},
            {"session_id": "S2", "target": {"type": "material", "id": "MAT-LIT-001"},
             "reading": "interpreted", "created_at": "2026-01-02"},
            {"session_id": "S3", "target": {"type": "material", "id": "MAT-LIT-001"},
             "reading": "interpreted", "created_at": "2026-01-03"},
            {"session_id": "S1", "target": {"type": "material", "id": "MAT-20260101-aaaaaa"},
             "reading": "interpreted", "created_at": "2026-01-01"},
            {"session_id": "S4", "target": {"type": "material", "id": "MAT-LIT-001"},
             "reading": "declined", "created_at": "2026-01-04"},
            {"session_id": "S5", "target": {"type": "material", "id": "MAT-20260101-aaaaaa"},
             "reading": "used_as_context", "created_at": "2026-01-05"},
        ]
        cohort = scm._exposure_cohort(read_log, sessions)
        self.assertEqual(cohort["cohort_size"], 2)
        self.assertEqual(cohort["literary_size"], 1)
        self.assertEqual(cohort["other_size"], 1)
        # Cohort statistics count rows, including declined and context rows;
        # they do not claim to measure reading or equal actual exposure.
        self.assertAlmostEqual(cohort["literary_mean_reads"], 4.0)
        self.assertAlmostEqual(cohort["other_mean_reads"], 2.0)
        self.assertEqual(cohort["top20_literary"], 1)


class RealTreeTests(unittest.TestCase):
    def test_real_tree_measures_the_metrics_in_range(self) -> None:
        data = scm.measure()
        self.assertGreater(data["read_log_rows"], 0)
        for key in ("central_question_pct", "verbatim_pct", "reconstructive_pct"):
            self.assertGreaterEqual(data[key], 0.0)
            self.assertLessEqual(data[key], 100.0)
        for key in ("declared_context_overlap", "read_materials_overlap", "all_read_materials_overlap"):
            self.assertGreater(data[key]["pairs"], 0)
            self.assertGreaterEqual(data[key]["zero_overlap_pct"], 0.0)
            self.assertLessEqual(data[key]["zero_overlap_pct"], 100.0)
        self.assertGreater(data["exposure_cohort"]["cohort_size"], 0)
        self.assertLessEqual(len(data["top_materials"]), 20)
        self.assertTrue(all(any(t in key.lower() for t in scm.EXPERIENTIAL_TOKENS)
                            for key in data["experiential_keys"]))

    def test_render_names_the_report_and_carries_the_numbers(self) -> None:
        text = scm.render(scm.measure())
        self.assertIn("自己の連続は、どこに記録されているか", text)
        self.assertIn("read_log 行数", text)
        self.assertIn("感覚関連の指定語に一致する鍵", text)
        self.assertIn("層2素材記録", text)
        self.assertIn("実際の露出は未測定", text)
        self.assertIn("実時間順とは限らない", text)
        self.assertIn("両集合が空の組は除外", text)
        self.assertIn("文脈・辞退を含む", text)


if __name__ == "__main__":
    unittest.main()
