"""Tests for tools/verdict_form_effect.py — the counterfactual arithmetic, not the archive."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import verdict_form_effect as vfe  # noqa: E402


def ledgers():
    """Two competing hypotheses on one question, with one supports row each."""
    hypotheses = {
        "HYP-A": {
            "hypothesis_id": "HYP-A",
            "question_ids": ["Q-003"],
            "status": "active",
            "parent_hypothesis_ids": [],
            "title": "A",
            "proposition": "a",
        },
        "HYP-B": {
            "hypothesis_id": "HYP-B",
            "question_ids": ["Q-003"],
            "status": "active",
            "parent_hypothesis_ids": [],
            "title": "B",
            "proposition": "b",
        },
    }
    evaluations = {
        "EVL-1": {
            "evaluation_id": "EVL-1",
            "session_id": "SESSION-X",
            "created_at": "2026-01-01",
            "target_hypothesis_id": "HYP-A",
            "verdict": "supports",
            "evidence_type": "cross_session_audit",
            "summary": "s",
            "compared_against_hypothesis_ids": ["HYP-B"],
            "material_ids": ["MAT-1"],
        },
        "EVL-2": {
            "evaluation_id": "EVL-2",
            "session_id": "SESSION-Y",
            "created_at": "2026-01-01",
            "target_hypothesis_id": "HYP-B",
            "verdict": "supports",
            "evidence_type": "cross_session_audit",
            "summary": "s",
            "compared_against_hypothesis_ids": ["HYP-A"],
            "material_ids": ["MAT-2"],
        },
    }
    return {
        "questions": {"Q-003": {"question_id": "Q-003", "question": "q"}},
        "hypotheses": hypotheses,
        "evaluations": evaluations,
        "materials": {},
        "notes": {},
        "sessions": {},
        "fragments": {},
        "errata": {},
    }


class DiffMapTests(unittest.TestCase):
    def test_identical_maps_do_not_move(self) -> None:
        same = {"HYP-A": 0.5, "HYP-B": 0.5}
        out = vfe.diff_maps(same, dict(same))
        self.assertEqual(out["tvd"], 0.0)
        self.assertEqual(out["max_delta_pp"], 0.0)
        self.assertEqual(out["moved"], 0)

    def test_total_variation_distance_is_half_the_l1_distance(self) -> None:
        out = vfe.diff_maps({"HYP-A": 0.75, "HYP-B": 0.25}, {"HYP-A": 0.25, "HYP-B": 0.75})
        self.assertAlmostEqual(out["tvd"], 0.5, places=6)
        self.assertEqual(out["max_delta_id"], "HYP-A")
        self.assertEqual(out["moved"], 2)


class MeasureTests(unittest.TestCase):
    def test_removing_a_session_restores_the_untouched_state(self) -> None:
        data = ledgers()
        report = vfe.measure(data, "SESSION-X", questions=("Q-003",))
        self.assertEqual(report["selected_rows"], 1)
        self.assertGreater(report["counterfactuals"]["Q-003"]["removed"]["tvd"], 0.0)

    def test_verdict_string_alone_changes_the_distribution(self) -> None:
        data = ledgers()
        rows = vfe.measure(data, "SESSION-X", questions=("Q-003",))["counterfactuals"]["Q-003"]
        self.assertGreater(rows["all_narrows"]["tvd"], rows["all_supports"]["tvd"])
        self.assertEqual(rows["all_supports"]["tvd"], 0.0)

    def test_retargeting_moves_the_other_way(self) -> None:
        data = ledgers()
        plain = vfe.measure(data, "SESSION-X", questions=("Q-003",))
        moved = vfe.measure(data, "SESSION-X", questions=("Q-003",), retarget="HYP-B")
        self.assertIn("retargeted", moved["counterfactuals"]["Q-003"])
        self.assertEqual(moved["counterfactuals"]["Q-003"]["retargeted"]["top_after"], "HYP-B")
        self.assertEqual(plain["counterfactuals"]["Q-003"]["removed"]["top_after"], "HYP-B")


class ScanTests(unittest.TestCase):
    def test_supports_scan_rises_then_saturates(self) -> None:
        data = ledgers()
        scan = vfe.supports_scan(data, "HYP-A", "Q-003", limit=5)
        values = [row["posterior"] for row in scan["curve"]]
        self.assertEqual(values, sorted(values))
        self.assertLess(values[0], 1.0)

    def test_attribution_counts_touching_sessions(self) -> None:
        data = ledgers()
        out = vfe.attribute(data, "HYP-A", "Q-003")
        self.assertEqual(out["sessions"], 2)  # EVL-1 targets A, EVL-2 names A as a comparison
        self.assertEqual(out["top"][0]["rows"], 1)


if __name__ == "__main__":
    unittest.main()
