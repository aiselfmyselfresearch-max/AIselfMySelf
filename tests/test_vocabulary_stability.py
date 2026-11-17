"""Tests for tools/vocabulary_stability.py — the measurements, on synthetic ledgers.

The tool reads the real ledgers when run, so these tests build tiny synthetic
ones: the point is that each number fails loudly when the thing it measures
disappears, not that today's archive has today's numbers.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import vocabulary_stability as vs  # noqa: E402


def evl(eid, target, verdict="supports", etype="primary_source_collision",
        compared=None, materials=None, day="2026-01-01"):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-" + eid,
        "created_at": day,
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": etype,
        "compared_against_hypothesis_ids": compared or [],
        "material_ids": materials or [],
        "spawned_hypothesis_ids": [],
    }


def eval_map(*rows):
    return {r["evaluation_id"]: r for r in rows}


class LabelProfileTests(unittest.TestCase):
    def test_counts_and_top_cell(self):
        evals = eval_map(
            evl("E1", "HYP-A"),
            evl("E2", "HYP-A"),
            evl("E3", "HYP-B", verdict="narrows_scope"),
        )
        prof = vs.label_profile(evals)
        self.assertEqual(prof["total"], 3)
        self.assertEqual(prof["verdicts"]["supports"], 2)
        self.assertEqual(prof["top_cell"], "supports/primary_source_collision")
        self.assertAlmostEqual(prof["top_cell_share"], 2 / 3)

    def test_empty_ledger_does_not_divide_by_zero(self):
        prof = vs.label_profile({})
        self.assertEqual(prof["total"], 0)
        self.assertEqual(prof["top_cell_share"], 0.0)


class UnbackedLabelTests(unittest.TestCase):
    def test_row_is_unbacked_when_every_material_is_not_fully_read(self):
        evals = eval_map(evl("E1", "HYP-A", materials=["MAT-1", "MAT-2"]))
        mats = {
            "MAT-1": {"material_id": "MAT-1", "verification": {"status": "partially_verified"}},
            "MAT-2": {"material_id": "MAT-2", "verification": {"status": "unverified"}},
        }
        row = vs.unbacked_label_share(evals, mats)["primary_source_collision"]
        self.assertEqual(row["rows"], 1)
        self.assertEqual(row["unbacked"], 1)
        self.assertEqual(row["share"], 1.0)

    def test_one_fully_read_material_makes_the_row_backed(self):
        evals = eval_map(evl("E1", "HYP-A", materials=["MAT-1", "MAT-2"]))
        mats = {
            "MAT-1": {"material_id": "MAT-1", "verification": {"status": "partially_verified"}},
            "MAT-2": {"material_id": "MAT-2", "verification": {"status": "verified"}},
        }
        row = vs.unbacked_label_share(evals, mats)["primary_source_collision"]
        self.assertEqual(row["unbacked"], 0)

    def test_missing_material_record_counts_as_not_read(self):
        evals = eval_map(evl("E1", "HYP-A", materials=["MAT-absent"]))
        row = vs.unbacked_label_share(evals, {})["primary_source_collision"]
        self.assertEqual(row["unbacked"], 1)

    def test_other_evidence_types_are_not_measured(self):
        evals = eval_map(evl("E1", "HYP-A", etype="reproducible_script", materials=["MAT-1"]))
        mats = {"MAT-1": {"verification": {"status": "unverified"}}}
        self.assertEqual(vs.unbacked_label_share(evals, mats)["primary_source_collision"]["rows"], 0)


class SeparationNoveltyTests(unittest.TestCase):
    def test_repeated_pair_is_not_new(self):
        evals = eval_map(
            evl("E1", "HYP-A", compared=["HYP-B"], day="2026-01-01"),
            evl("E2", "HYP-A", compared=["HYP-B"], day="2026-01-02"),
        )
        nov = vs.separation_novelty(evals)
        self.assertEqual(nov["rows"], 2)
        self.assertEqual(nov["new_pairs"], 1)
        self.assertEqual(nov["by_day"]["2026-01-02"]["new_pairs"], 0)

    def test_comparison_set_order_does_not_make_a_pair_new(self):
        evals = eval_map(
            evl("E1", "HYP-A", compared=["HYP-B", "HYP-C"], day="2026-01-01"),
            evl("E2", "HYP-A", compared=["HYP-C", "HYP-B"], day="2026-01-02"),
        )
        self.assertEqual(vs.separation_novelty(evals)["new_pairs"], 1)

    def test_row_without_target_is_skipped(self):
        evals = eval_map(evl("E1", "", compared=["HYP-B"]))
        self.assertEqual(vs.separation_novelty(evals)["rows"], 0)


def state_for(entries, offered=None):
    return {
        "questions": {
            "Q-003": {
                "hypotheses": [
                    {
                        "hypothesis_id": hid,
                        "posterior": p,
                        "uncertainty": u,
                        "effective_status": status,
                        "direct_eval_count": 1,
                    }
                    for hid, p, u, status in entries
                ],
                "top_competing_pair": offered
                or {
                    "left_hypothesis_id": "HYP-A",
                    "right_hypothesis_id": "HYP-B",
                    "expected_info_gain": 0.03,
                },
            }
        }
    }


class LeastSeparatedPairTests(unittest.TestCase):
    def test_never_separated_pair_outranks_a_heavily_separated_one(self):
        evals = eval_map(
            *[evl(f"E{i}", "HYP-A", compared=["HYP-B"], day="2026-01-01") for i in range(4)],
            evl("E9", "HYP-A", compared=["HYP-C"], day="2026-01-02"),
        )
        state = state_for(
            [("HYP-A", 0.60, -1.2, "active"), ("HYP-B", 0.20, -1.4, "active"), ("HYP-C", 0.10, -1.6, "active")]
        )
        out = vs.least_separated_pairs(state, evals, "Q-003")
        first = out["least_separated"][0]
        self.assertEqual({first["left"], first["right"]}, {"HYP-B", "HYP-C"})
        self.assertEqual(first["separations"], 0)
        self.assertEqual(out["offered_by_eig"]["separations"], 4)

    def test_low_posterior_hypotheses_are_excluded(self):
        state = state_for(
            [("HYP-A", 0.90, -1.2, "active"), ("HYP-B", 0.0005, -1.4, "active"), ("HYP-C", 0.05, -1.6, "active")]
        )
        out = vs.least_separated_pairs(state, eval_map(), "Q-003", min_posterior=0.01)
        self.assertEqual(out["eligible_hypotheses"], 2)

    def test_inactive_hypotheses_are_excluded(self):
        state = state_for(
            [
                ("HYP-A", 0.90, -1.2, "active"),
                ("HYP-B", 0.05, -1.4, "active"),
                ("HYP-C", 0.05, -1.6, "retired"),
            ]
        )
        out = vs.least_separated_pairs(state, eval_map(), "Q-003")
        self.assertEqual(out["eligible_hypotheses"], 2)

    def test_unknown_question_returns_empty_list(self):
        out = vs.least_separated_pairs(state_for([]), eval_map(), "Q-999")
        self.assertEqual(out["least_separated"], [])
        self.assertEqual(out["eligible_pairs"], 0)


class RenderTests(unittest.TestCase):
    def test_render_mentions_every_headline_number(self):
        report = {
            "labels": {
                "total": 10,
                "verdicts": {"supports": 10},
                "evidence_types": {"primary_source_collision": 10},
                "cells": {"supports/primary_source_collision": 10},
                "top_cell": "supports/primary_source_collision",
                "top_cell_share": 1.0,
                "grid_cells_used": 1,
                "grid_cells_possible": 1,
            },
            "unbacked": {
                "primary_source_collision": {
                    "rows": 10,
                    "unbacked": 7,
                    "no_materials": 0,
                    "share": 0.7,
                }
            },
            "novelty": {"rows": 10, "new_pairs": 3, "share": 0.3, "by_day": {}},
        }
        text = vs.render(report)
        self.assertIn("70.0%", text)
        self.assertIn("30.0%", text)
        self.assertIn("supports/primary_source_collision", text)


if __name__ == "__main__":
    unittest.main()


class TestReadingVocabulary(unittest.TestCase):
    """Pins the label x object-type measurement added on 2026-11-17.

    It asks which kind of object gets which reading label, and whether the
    gap between the archive's own records and its sources holds across its
    internal months.  The counting rules are fixed here; the interpretation
    stays in readings/.
    """

    ROWS = (
        # own records: mostly reinterpreted
        [{"read_id": f"READ-o{i}", "target": {"type": "fragment", "id": f"FRAG-{i}"},
          "reading": "reinterpreted", "note": "x", "created_at": "2026-11-01T00:00:00Z"}
         for i in range(25)]
        + [{"read_id": f"READ-n{i}", "target": {"type": "note", "id": f"NOTE-{i}"},
            "reading": "interpreted", "note": "x", "created_at": "2026-11-01T00:00:00Z"}
           for i in range(5)]
        # sources: mostly interpreted
        + [{"read_id": f"READ-m{i}", "target": {"type": "material", "id": f"MAT-{i}"},
            "reading": "interpreted", "note": "x", "created_at": "2026-11-02T00:00:00Z"}
           for i in range(30)]
        # mechanical rows are excluded from the profile
        + [{"read_id": "READ-mech", "target": {"type": "material", "id": "MAT-9"},
            "reading": "used_as_context", "note": "機械的バックフィル: context", "created_at": "2026-11-02T00:00:00Z"}]
        # hypothesis-targeted mechanical row (the engine's marker would keep it)
        + [{"read_id": "READ-mech2", "target": {"type": "hypothesis", "id": "HYP-9"},
            "reading": "used_as_context", "note": "機械的接触行: x", "created_at": "2026-11-02T00:00:00Z"}]
    )

    def report(self):
        return vs.reading_report(root=ROOT, read_log=list(self.ROWS))

    def test_mechanical_rows_are_excluded_from_the_profile(self) -> None:
        report = self.report()
        self.assertEqual(report["rows"], 62)
        self.assertEqual(report["handwritten"], 60)
        self.assertNotIn("hypothesis", report["by_target_type"])

    def test_own_records_and_sources_are_profiled_separately(self) -> None:
        report = self.report()
        self.assertEqual(report["own"]["rows"], 30)
        self.assertEqual(report["own"]["reinterpreted"], 0.833)  # 25/30, rounded to 3dp
        self.assertEqual(report["source"]["rows"], 30)
        self.assertEqual(report["source"]["reinterpreted"], 0.0)

    def test_month_rows_need_twenty_of_each_side(self) -> None:
        by_month = self.report()["by_month"]
        self.assertIn("2026-11", by_month)
        self.assertEqual(by_month["2026-11"]["gap_pp"], 83.3)

    def test_engine_marker_and_prefix_rule_are_counted_apart(self) -> None:
        mech = self.report()["mechanical"]
        self.assertEqual(mech["marker_backfill"], 1)
        self.assertEqual(mech["prefix_both"], 2)
        self.assertEqual(mech["hypothesis_targeted"], 1)
