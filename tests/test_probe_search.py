"""Tests for tools/probe_search.py: search-failure measurement on the viewer surface."""

import json
import tempfile
import unittest
from pathlib import Path

from tools import probe_search


class ViewerHaystackTests(unittest.TestCase):
    def test_haystack_matches_viewer_fields_and_lowercases(self):
        row = {
            "material_id": "MAT-A",
            "title": " 保持 の理論",
            "source": {"authors": ["Alpha", "Beta"]},
            "passage": "痕跡の維持。",
            "literary_invitation": "なぜ残るのか。",
        }
        hay = probe_search.viewer_haystack(row)
        self.assertIn("mat-a", hay)
        self.assertIn("alpha beta", hay)
        self.assertIn("なぜ残るのか。", hay)

    def test_missing_source_and_fields_do_not_crash(self):
        hay = probe_search.viewer_haystack({"material_id": "MAT-B"})
        self.assertTrue(hay.startswith("mat-b"))
        self.assertEqual(hay.strip(), "mat-b")


class SearchTests(unittest.TestCase):
    ROWS = [
        {"material_id": "MAT-A", "title": "保持の理論", "passage": "維持する。"},
        {"material_id": "MAT-B", "title": "忘却の理論", "passage": "減衰する。"},
        {"material_id": "MAT-C", "title": "保持の練習", "passage": "検索練習は保持を高める。"},
    ]

    def test_hits_are_in_collection_order(self):
        self.assertEqual(probe_search.search(self.ROWS, "保持"), ["MAT-A", "MAT-C"])

    def test_no_match_and_empty_query(self):
        self.assertEqual(probe_search.search(self.ROWS, "存在しない"), [])
        self.assertEqual(probe_search.search(self.ROWS, "  "), [])

    def test_case_insensitive_like_the_viewer(self):
        rows = [{"material_id": "MAT-D", "title": "Forgetting Curves", "passage": ""}]
        self.assertEqual(probe_search.search(rows, "forgetting"), ["MAT-D"])


class RunProbesTests(unittest.TestCase):
    def test_summary_counts_and_rank(self):
        rows = [
            {"material_id": "MAT-A", "title": "保持", "passage": "x"},
            {"material_id": "MAT-B", "title": "保持", "passage": "x"},
            {"material_id": "MAT-C", "title": "保持", "passage": "x"},
        ]
        probes = [
            {"target_id": "MAT-B", "kind": "ledger", "query": "保持"},
            {"target_id": "MAT-B", "kind": "paraphrase", "query": "記銘"},
            {"target_id": "MAT-B", "kind": "hypernym", "query": "記憶過程"},
        ]
        per_probe, summary, problems = probe_search.run_probes(rows, probes)
        self.assertEqual(problems, [])
        self.assertEqual(summary["ledger"]["reach"], 1)
        self.assertEqual(summary["ledger"]["first_page"], 1)
        self.assertEqual(summary["ledger"]["median_rank"], 2)
        # paraphrase/hypernym wordings are validated absent from the target's own
        # haystack, so a substring filter can never reach the target with them.
        self.assertEqual(summary["paraphrase"]["reach"], 0)
        self.assertEqual(summary["paraphrase"]["zero"], 1)
        self.assertEqual(summary["hypernym"]["zero"], 1)

    def test_in_haystack_nonledger_wording_is_flagged(self):
        rows = [{"material_id": "MAT-A", "title": "保持", "passage": "x"}]
        probes = [{"target_id": "MAT-A", "kind": "paraphrase", "query": "保持"}]
        _, _, problems = probe_search.run_probes(rows, probes)
        self.assertTrue(any("occurs in the target's own haystack" in p for p in problems))

    def test_missing_target_is_flagged(self):
        rows = [{"material_id": "MAT-A", "title": "保持", "passage": "x"}]
        probes = [{"target_id": "MAT-Z", "kind": "ledger", "query": "保持"}]
        per_probe, _, problems = probe_search.run_probes(rows, probes)
        self.assertEqual(len(per_probe), 0)
        self.assertTrue(any("not in ledger" in p for p in problems))


class CoverageGapTests(unittest.TestCase):
    def test_open_questions_without_fragment_materials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state"
            state.mkdir()
            (state / "questions.jsonl").write_text(
                "\n".join([
                    json.dumps({"question_id": "Q-1", "status": "open"}, ensure_ascii=False),
                    json.dumps({"question_id": "Q-2"}, ensure_ascii=False),
                    json.dumps({"question_id": "Q-3", "status": "closed"}, ensure_ascii=False),
                ]) + "\n",
                encoding="utf-8",
            )
            (state / "fragments.jsonl").write_text(
                json.dumps(
                    {"fragment_id": "FRAG-1", "question_ids": ["Q-1"],
                     "material_ids": ["MAT-A"]},
                    ensure_ascii=False,
                ) + "\n",
                encoding="utf-8",
            )
            gaps = probe_search.coverage_gaps(root)
            self.assertEqual(gaps["open_questions"], 2)
            self.assertEqual(gaps["coverage_gaps"], 1)
            self.assertEqual(gaps["question_ids"], ["Q-2"])

    def test_gap_ids_are_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state"
            state.mkdir()
            (state / "questions.jsonl").write_text(
                "\n".join([
                    json.dumps({"question_id": "Q-b"}),
                    json.dumps({"question_id": "Q-a"}),
                ]) + "\n",
                encoding="utf-8",
            )
            (state / "fragments.jsonl").write_text("", encoding="utf-8")
            gaps = probe_search.coverage_gaps(root)
            self.assertEqual(gaps["question_ids"], ["Q-a", "Q-b"])


class RealRepositoryTests(unittest.TestCase):
    """The shipped probe set must stay valid against the real, append-only ledger."""

    def test_shipped_probe_set_replays_without_problems(self):
        root = Path(probe_search.ROOT)
        rows = probe_search.load_materials(root)
        probes = probe_search.load_probes(root / "docs" / "search-probe-set.json")
        _, summary, problems = probe_search.run_probes(rows, probes)
        self.assertEqual(problems, [], str(problems))
        self.assertEqual(set(summary), {"ledger", "paraphrase", "hypernym"})
        # The pre-registered prediction (readings/2026-11-27-retrieval-failure-
        # probes-and-adoption.md §2) must keep holding as the ledger grows:
        # ledger wordings reach their own rows; paraphrase/hypernym wordings
        # cannot (substring match over each row's own words).
        self.assertEqual(summary["ledger"]["reach"], summary["ledger"]["probes"])
        self.assertEqual(summary["paraphrase"]["reach"], 0)
        self.assertEqual(summary["hypernym"]["reach"], 0)

    def test_coverage_gap_rate_is_wellformed(self):
        gaps = probe_search.coverage_gaps(Path(probe_search.ROOT))
        self.assertGreaterEqual(gaps["open_questions"], gaps["coverage_gaps"])
        self.assertTrue(0.0 <= (gaps["gap_rate"] or 0.0) <= 1.0)
        self.assertEqual(gaps["question_ids"], sorted(gaps["question_ids"]))


if __name__ == "__main__":
    unittest.main()
