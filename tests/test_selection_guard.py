"""Tests for the saturation rule (2026-11-15).

The rule is deliberately narrow: when a core question's best competing pair
carries less than ``belief_state.SATURATION_EIG_THRESHOLD`` expected information
gain, the packet says so and names three destinations (open errata, a re-reading
wired to an evaluation, new material).  It never changes a posterior and never
forbids a hypothesis; it removes "mint a root hypothesis to restore EIG" from the
default path (readings/2026-11-15-where-the-learning-actually-happens.md §5, §7-1).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402

HYPO = {
    "hypothesis_id": "HYP-20261112-5dc940",
    "title": "時間粒度に相対的な選択窓と代謝的消化説",
    "proposition": "記憶と忘却が私を作るのは保持量の多寡によってではない。",
    "scope_conditions": ["知覚・注意資源が有限である認知条件"],
    "exclusion_clause": "完全逐語再生でも同等の判断形成が成立する実証例が出れば棄却される。",
    "lineage_op": "splits",
    "generation": 1,
    "effective_status": "active",
    "uncertainty": 0.143,
    "posterior": 0.9082,
    "errata_flags": [],
}


def qstate(eig: float) -> dict:
    return {
        "question_id": "Q-001",
        "hypothesis_count": 1,
        "active_count": 1,
        "gen1_plus_mass": 0.955,
        "kl_from_uniform_bits": 1.713,
        "top_competing_pair": {
            "left_hypothesis_id": "HYP-20261112-5dc940",
            "right_hypothesis_id": "HYP-20261112-46456a",
            "expected_info_gain": eig,
        },
        "hypotheses": [dict(HYPO)],
    }


def briefing(state: dict) -> str:
    data = {"hypotheses": {"HYP-20261112-5dc940": {}}}
    role = {"role": "consolidator", "label": "Consolidator", "prompt": "prompts/role_consolidator.md", "reason": "テスト"}
    with mock.patch.object(belief_state, "compute_belief_state", return_value=state), \
         mock.patch.object(belief_state, "assign_session_role", return_value=role):
        lines, _ = inspect_inquiry._belief_briefing_lines(
            data, "Q-001", seed_label="00000000", errata={"ERR-1": {"status": "open"}}
        )
    return "\n".join(lines)


class SaturationSnapshotTests(unittest.TestCase):
    def test_flags_low_eig_question_only(self) -> None:
        state = {"questions": {"Q-001": qstate(0.0067), "Q-003": qstate(0.2259)}}
        snap = belief_state.saturation_snapshot(state, question_ids=("Q-001", "Q-003"))
        self.assertEqual(snap["saturated_question_ids"], ["Q-001"])
        rows = {row["question_id"]: row for row in snap["questions"]}
        self.assertTrue(rows["Q-001"]["saturated"])
        self.assertFalse(rows["Q-003"]["saturated"])

    def test_threshold_is_respected(self) -> None:
        state = {"questions": {"Q-001": qstate(0.05)}}
        self.assertFalse(belief_state.saturation_snapshot(state, threshold=0.02)["questions"][0]["saturated"])
        self.assertTrue(belief_state.saturation_snapshot(state, threshold=0.20)["questions"][0]["saturated"])

    def test_unknown_question_is_skipped(self) -> None:
        snap = belief_state.saturation_snapshot({"questions": {}})
        self.assertEqual(snap["questions"], [])
        self.assertEqual(snap["saturated_question_ids"], [])

    def test_default_threshold_is_two_percent(self) -> None:
        self.assertEqual(belief_state.SATURATION_EIG_THRESHOLD, 0.02)

    def test_snapshot_does_not_touch_the_posteriors(self) -> None:
        state = {"questions": {"Q-001": qstate(0.0067)}}
        before = state["questions"]["Q-001"]["hypotheses"][0]["posterior"]
        belief_state.saturation_snapshot(state)
        self.assertEqual(state["questions"]["Q-001"]["hypotheses"][0]["posterior"], before)


class BriefingSaturationTests(unittest.TestCase):
    def test_saturated_question_names_three_destinations(self) -> None:
        state = {
            "questions": {"Q-001": qstate(0.0067)},
            "saturation": {
                "threshold": 0.02,
                "questions": [{"question_id": "Q-001", "top_eig": 0.0067, "saturated": True}],
                "saturated_question_ids": ["Q-001"],
            },
        }
        text = briefing(state)
        self.assertIn("飽和（最大EIG < 0.02）", text)
        self.assertIn("新しい根仮説を足してEIGを回復させないでください", text)
        self.assertIn("未解決 `errata` **1件**", text)
        self.assertIn("配線を伴う再読", text)
        self.assertIn("新規資料", text)

    def test_unsaturated_target_is_said_to_still_select(self) -> None:
        state = {
            "questions": {"Q-001": qstate(0.2259)},
            "saturation": {
                "threshold": 0.02,
                "questions": [
                    {"question_id": "Q-002", "top_eig": 0.0, "saturated": True},
                    {"question_id": "Q-001", "top_eig": 0.2259, "saturated": False},
                ],
                "saturated_question_ids": ["Q-002"],
            },
        }
        text = briefing(state)
        self.assertIn("`Q-002`", text)
        self.assertIn("対象の `Q-001` は非飽和（最大EIG 0.2259）", text)

    def test_unsaturated_briefing_says_nothing_about_saturation(self) -> None:
        state = {
            "questions": {"Q-001": qstate(0.2259)},
            "saturation": {"threshold": 0.02, "questions": [], "saturated_question_ids": []},
        }
        self.assertNotIn("飽和", briefing(state))

    def test_guidance_asks_for_a_register(self) -> None:
        self.assertIn("register", inspect_inquiry.INQUIRY_GUIDANCE)
        self.assertIn("docs/registers.md", inspect_inquiry.INQUIRY_GUIDANCE)
        self.assertIn("反証条件", inspect_inquiry.INQUIRY_GUIDANCE)


if __name__ == "__main__":
    unittest.main()
