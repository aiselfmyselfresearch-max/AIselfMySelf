"""Regression tests for the limits of the memory-temperature diagnostic.

The fixtures are synthetic: their counts must not depend on the live ledger.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402
import three_gates  # noqa: E402


def _read(session: str, material: str, reading: str, *, note: str = "", at: str = "") -> dict:
    return {
        "session_id": session,
        "target": {"type": "material", "id": material},
        "reading": reading,
        "note": note,
        "created_at": at,
    }


class MemoryOverlapTests(unittest.TestCase):
    def fixture(self) -> dict:
        ids = ("BOTH-DIFFERENT", "BOTH-SAME", "COUNTED", "EVAL-ONLY", "NEITHER", "DECLINED", "CONTEXT", "MARKER-QUOTE", "UNKNOWN")
        materials = {m: {"title": m} for m in ids}
        sessions = {
            "ANCHOR": {"context_material_ids": list(ids[:-1])},
            "READ": {"context_material_ids": [], "started_at": "2026-11-20T15:00:00Z"},
            "EVAL": {"context_material_ids": [], "started_at": "2026-11-20T14:00:00Z"},
        }
        read_log = {
            "r1": _read("READ", "BOTH-DIFFERENT", "interpreted", at="2026-11-20T15:00:00Z"),
            "r2": _read("READ", "BOTH-SAME", "summarized"),
            "r3": _read("READ", "COUNTED", "counted"),
            "r4": _read("READ", "DECLINED", "declined", note="explicitly not read"),
            "r5": _read("READ", "CONTEXT", "used_as_context", note="manual context, no marker"),
            "r6": _read("READ", "MARKER-QUOTE", "quoted", note="a real quote about バックフィル"),
        }
        evaluations = {
            # Earlier timestamp and a different session: co-occurrence is not conversion.
            "e1": {"session_id": "EVAL", "material_ids": ["BOTH-DIFFERENT"], "created_at": "2026-11-20T14:00:00Z"},
            "e2": {"session_id": "READ", "material_ids": ["BOTH-SAME"]},
            "e3": {"session_id": "EVAL", "material_ids": ["EVAL-ONLY", "DECLINED", "UNKNOWN"]},
        }
        return {"materials": materials, "sessions": sessions, "read_log": read_log, "evaluations": evaluations,
                "notes": {}, "hypotheses": {}, "questions": {}}

    def test_four_cells_and_unknown_anchor_do_not_invent_a_sequence(self) -> None:
        result = three_gates.memory_temperature_and_gate_audit(self.fixture())
        tier = result["two_stage_gate_by_tier"]["tier0_unwired"]
        self.assertEqual((tier["total"], tier["anchor_known"], tier["anchor_unknown"]), (9, 8, 1))
        self.assertEqual(tier["unknown_anchor_with_any_eval"], 1)
        self.assertEqual((tier["read_and_eval"], tier["read_only"], tier["eval_only"], tier["neither"]), (2, 2, 2, 2))
        self.assertEqual((tier["read_and_eval_shared_session"], tier["read_and_eval_no_shared_session"]), (1, 1))
        self.assertEqual(tier["stage1_subseq_read"], 4)
        self.assertEqual(tier["non_anchor_counted_only"], 1)
        self.assertEqual(tier["eval_in_non_anchor_session"], 4)
        self.assertEqual(tier["stage2_subseq_eval_given_stage1"], 2)
        self.assertEqual(tier["stage2_conversion_pct"], 50.0)
        self.assertEqual(result["any_session_read_eval"],
                         {"read_and_eval": 2, "read_only": 2, "eval_only": 3, "neither": 2})
        # P(E) = P(R)P(E|R) + P(E and not R), over known anchors.
        self.assertEqual(4 / 8, (4 / 8) * (2 / 4) + 2 / 8)
        self.assertIn("not established", result["method"]["event_order"])
        self.assertTrue(result["method"]["counted_is_not_interpretation"])

    def test_decline_and_context_are_not_reading_but_counted_is(self) -> None:
        result = three_gates.memory_temperature_and_gate_audit(self.fixture(), limit=0)
        ids = {row["material_id"] for row in result["top_tier0_candidates"]}
        self.assertIn("COUNTED", ids)
        self.assertIn("MARKER-QUOTE", ids)  # the marker may describe a real quotation
        self.assertNotIn("DECLINED", ids)
        self.assertNotIn("CONTEXT", ids)
        self.assertEqual(result["temperature_tiers"]["warm_unwired"], 4)
        self.assertEqual(result["temperature_tiers"]["cold_verbatim"], 5)

    def test_no_denominator_is_null_not_a_measured_zero_percent(self) -> None:
        empty = {"materials": {}, "sessions": {}, "read_log": {}, "evaluations": {},
                 "notes": {}, "hypotheses": {}, "questions": {}}
        tier = three_gates.memory_temperature_and_gate_audit(empty)["two_stage_gate_by_tier"]["tier0_unwired"]
        self.assertIsNone(tier["stage1_rate_pct"])
        self.assertIsNone(tier["stage2_conversion_pct"])
        self.assertIsNone(tier["eval_rate_pct"])
        self.assertEqual(three_gates._display_pct(None), "—")

    def test_fallback_anchor_is_not_a_second_witness(self) -> None:
        data = {"materials": {"M": {}}, "sessions": {"S": {"context_material_ids": []}},
                "read_log": {"r": _read("S", "M", "quoted")}, "evaluations": {},
                "notes": {}, "hypotheses": {}, "questions": {}}
        result = three_gates.memory_temperature_and_gate_audit(data)
        tier = result["two_stage_gate_by_tier"]["tier0_unwired"]
        self.assertEqual((tier["anchor_known"], tier["neither"]), (1, 1))
        self.assertEqual(tier["stage1_subseq_read"], 0)

    def test_wiring_is_the_current_retrospective_snapshot(self) -> None:
        data = self.fixture()
        data["notes"] = {"N": {"created_at": "2030-01-01", "claims": [{"material_ids": ["BOTH-DIFFERENT"]}]}}
        data["hypotheses"] = {"H": {"created_at": "2030-01-01", "supporting_material_ids": ["BOTH-SAME"]}}
        result = three_gates.memory_temperature_and_gate_audit(data)
        tiers = result["two_stage_gate_by_tier"]
        self.assertEqual(tiers["tier1_note_claim"]["read_and_eval"], 1)
        self.assertEqual(tiers["tier2_hypothesis"]["read_and_eval"], 1)
        self.assertIn("after", result["method"]["tiers"])

    def test_packet_priority_does_not_promote_declined_or_context(self) -> None:
        mids = ("HEAD-A", "HEAD-B", "DECLINE", "CONTEXT", "ACTUAL", "COUNTED")
        data = {
            "materials": {m: {"verification": {"status": "verified"}} for m in mids},
            "questions": {"Q-001": {"material_ids": list(mids)}},
            "hypotheses": {"H": {"hypothesis_id": "H", "question_ids": ["Q-001"], "status": "active"}},
            "notes": {},
            "read_log": {
                **{f"d{i}": _read(f"S{i}", "DECLINE", "declined") for i in (1, 2)},
                **{f"c{i}": _read(f"S{i}", "CONTEXT", "used_as_context") for i in (1, 2)},
                **{f"a{i}": _read(f"S{i}", "ACTUAL", "interpreted") for i in (1, 2)},
                **{f"n{i}": _read(f"S{i}", "COUNTED", "counted") for i in (1, 2)},
            },
        }
        with patch.object(belief_state, "compute_belief_state", return_value={"questions": {"Q-001": {"hypotheses": []}}}):
            ordered = inspect_inquiry._candidate_materials_for_question(data, "Q-001")
        self.assertEqual(ordered, ["HEAD-A", "HEAD-B", "ACTUAL", "COUNTED", "DECLINE", "CONTEXT"])

    def test_note_wiring_changes_priority_but_does_not_guarantee_window_entry(self) -> None:
        mids = ("HEAD-A", "HEAD-B", "THIRD", "FOURTH")
        data = {"materials": {m: {} for m in mids},
                "questions": {"Q-001": {"material_ids": list(mids)}},
                "hypotheses": {"H": {"hypothesis_id": "H", "question_ids": ["Q-001"], "status": "active"}},
                "notes": {}, "read_log": {}}
        injected = dict(data)
        injected["notes"] = {"SIM": {"claims": [{"material_ids": ["FOURTH"]}]}}
        with patch.object(belief_state, "compute_belief_state", return_value={"questions": {"Q-001": {"hypotheses": []}}}):
            before = inspect_inquiry._candidate_materials_for_question(data, "Q-001")
            after = inspect_inquiry._candidate_materials_for_question(injected, "Q-001")
        self.assertEqual(before, ["HEAD-A", "HEAD-B", "THIRD", "FOURTH"])
        self.assertEqual(after, ["HEAD-A", "HEAD-B", "FOURTH", "THIRD"])
        self.assertEqual(before[:2], after[:2])  # with a two-item window neither tail item is exposed
        self.assertEqual(data["notes"], {})  # the control was not changed

    def test_old_curation_corrections_remain_visible_after_supersession(self) -> None:
        entry = {"path": "readings/example.md", "name": "example.md", "title": "example",
                 "note_id": "NOTE-NEW", "note_ids": ["NOTE-OLD", "NOTE-NEW"], "curated": {}}
        errata = {"ERR-OLD": {"errata_id": "ERR-OLD", "subject_id": "NOTE-OLD",
                              "claim_location": "state/notes, not a path", "created_at": "2026-11-20"}}
        with patch.object(inspect_inquiry, "related_notes", return_value=[entry]):
            lines = inspect_inquiry.related_notes_lines({}, "Q-001", errata=errata)
        self.assertEqual(sum("ERR-OLD" in line for line in lines), 1)


if __name__ == "__main__":
    unittest.main()
