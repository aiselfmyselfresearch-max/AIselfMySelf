"""Tests for tools/cogsci_corpus.py — measuring the report series as a series.

The 2026-11-23 meta-report (``readings/2026-11-23-the-cognitive-science-reports-as-a-corpus.md``)
cites these numbers: corpus size, the apparatus density by date, the reuse-once
share, the verification-depth coverage, the same-day share of note reads, and
the verdict distribution.  The tests pin the arithmetic on a small fixture and
pin the shape of the real-tree output, so a refactor cannot silently change a
number an evaluation rests on.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import cogsci_corpus as cc  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


class FixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # Two reports: one title match, one filename match, one non-match.
        write(
            self.root / "readings" / "a.md",
            "# 認知科学レポート：A\n\n## 要旨\nSESSION-20261123-text\n"
            "MAT-20261123-aaaaaa MAT-20261123-aaaaaa MAT-20261120-bbbbbb\n",
        )
        write(
            self.root / "docs" / "2026-11-22-cognitive-science-b.md",
            "# 別の題\n\n## 要旨\nMAT-20261122-cccccc MAT-20261123-aaaaaa\n",
        )
        write(self.root / "docs" / "c.md", "# 無関係\n\nMAT-20261122-dddddd\n")
        # Self-exclusion: a file named like the meta-report must not be counted.
        write(self.root / "COGNITIVE_SCIENCE_REPORT_2026-11-23-H.md", "# 認知科学レポート（H）\n")
        write_jsonl(
            self.root / "state" / "materials.jsonl",
            [
                {"material_id": "MAT-20261123-aaaaaa", "verification": {"status": "verified", "depth": "full_text"}},
                {"material_id": "MAT-20261120-bbbbbb", "verification": {"status": "partially_verified"}},
                {"material_id": "MAT-20261122-cccccc", "verification": {"status": "partially_verified", "depth": "abstract"}},
            ],
        )
        write_jsonl(
            self.root / "state" / "notes.jsonl",
            [{"note_id": "NOTE-1", "created_at": "2026-11-23", "path": "readings/a.md"}],
        )
        write_jsonl(
            self.root / "state" / "read_log.jsonl",
            [
                {"read_id": "R1", "session_id": "S1", "target": {"type": "note", "id": "NOTE-1"}, "reading": "used_as_context", "created_at": "2026-11-23"},
                {"read_id": "R2", "session_id": "S2", "target": {"type": "note", "id": "NOTE-1"}, "reading": "used_as_context", "created_at": "2026-11-24"},
                {"read_id": "R3", "session_id": "S3", "target": {"type": "material", "id": "MAT-X"}, "reading": "quoted", "created_at": "2026-11-24"},
            ],
        )
        write_jsonl(
            self.root / "state" / "evaluations.jsonl",
            [
                {"evaluation_id": "E1", "verdict": "narrows_scope", "evidence_type": "cross_session_audit"},
                {"evaluation_id": "E2", "verdict": "supports", "evidence_type": "primary_source_collision"},
                {"evaluation_id": "E3", "verdict": "narrows_scope", "evidence_type": "cross_session_audit"},
            ],
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_discovery_rule_and_self_exclusion(self) -> None:
        names = [row["name"] for row in cc.discover(self.root)]
        self.assertEqual(names, ["a.md", "2026-11-22-cognitive-science-b.md"])
        # title-only drops the filename match
        titles = [row["name"] for row in cc.discover(self.root, title_only=True)]
        self.assertEqual(titles, ["a.md"])

    def test_reuse_counts_full_ids_once(self) -> None:
        corpus = cc.discover(self.root)
        reuse = cc.section_reuse(corpus, self.root)
        # three distinct dated ids: aaaaaa, bbbbbb, cccccc
        self.assertEqual(reuse["corpus"]["distinct_ids"], 3)
        self.assertEqual(reuse["corpus"]["cited_by_one_report"], 2)
        self.assertAlmostEqual(reuse["corpus"]["share_pct"], 66.7)
        # report date for a.md is the session stamp 20261123
        self.assertEqual(reuse["mint_vs_report_date"]["same_day"], 3)

    def test_depth_join_counts_unrecorded_depth(self) -> None:
        depth = cc.section_depth(cc.discover(self.root), self.root)
        self.assertEqual(depth["corpus_cited_rows"], 3)
        self.assertEqual(depth["depth_recorded"], 2)
        self.assertAlmostEqual(depth["depth_recorded_pct"], 66.7)

    def test_verified_and_full_text_are_separate_columns(self) -> None:
        # The third axis of HYP-20261120-26b0c6 equates verified with full-text
        # reading.  The fixture shows the ledger does not: one verified row has
        # no depth, one has full_text.
        depth = cc.section_depth(cc.discover(self.root), self.root)
        self.assertEqual(depth["verified_rows"], 1)
        self.assertEqual(depth["verified_with_full_text_depth"], 1)
        archive = cc.section_depth(cc.discover(), Path(__file__).resolve().parents[1])
        self.assertLessEqual(archive["verified_with_full_text_depth"], archive["verified_rows"])
        self.assertGreater(archive["archive_verified_without_full_text"], 0)

    def test_chain_lag(self) -> None:
        chain = cc.section_chain(self.root)
        self.assertEqual(chain["note_read_rows"], 2)
        self.assertEqual(chain["same_day"], 1)
        self.assertAlmostEqual(chain["same_day_pct"], 50.0)

    def test_verdict_distribution(self) -> None:
        verdicts = cc.section_verdicts(self.root)
        self.assertEqual(verdicts["verdicts"]["narrows_scope"], 2)
        self.assertAlmostEqual(verdicts["share_pct"]["narrows_scope"], 66.7)

    def test_collect_is_deterministic(self) -> None:
        self.assertEqual(
            json.dumps(cc.collect(self.root), sort_keys=True, ensure_ascii=False),
            json.dumps(cc.collect(self.root), sort_keys=True, ensure_ascii=False),
        )


class RealTreeTests(unittest.TestCase):
    """Shape of the numbers a reader will meet in the report, at this tree."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = cc.collect()

    def test_corpus_is_large_and_dated(self) -> None:
        self.assertGreater(self.payload["form"]["corpus_reports"], 50)
        self.assertIn("20261123", self.payload["form"]["dates"])

    def test_shares_are_percentages(self) -> None:
        for section, key in (("reuse", "corpus"), ("reuse", "archive_wide")):
            share = self.payload[section][key]["share_pct"]
            self.assertGreaterEqual(share, 0.0)
            self.assertLessEqual(share, 100.0)
        self.assertGreaterEqual(self.payload["depth"]["depth_recorded_pct"], 0.0)
        self.assertLessEqual(self.payload["depth"]["depth_recorded_pct"], 100.0)

    def test_verdicts_sum_to_evaluations(self) -> None:
        verdicts = self.payload["verdicts"]
        self.assertEqual(sum(verdicts["verdicts"].values()), verdicts["evaluations"])

    def test_self_excluded(self) -> None:
        # The path is declared in `basis` (so a reader knows it was excluded) but
        # must not appear among the measured reports.
        self.assertIn(
            "2026-11-23-the-cognitive-science-reports-as-a-corpus.md",
            self.payload["basis"]["self_excluded"],
        )
        names = {row["name"] for row in cc.discover()}
        self.assertNotIn("2026-11-23-the-cognitive-science-reports-as-a-corpus.md", names)
        self.assertNotIn("COGNITIVE_SCIENCE_REPORT_2026-11-23-H.md", names)


if __name__ == "__main__":
    unittest.main()
