"""Tests for the 2026-11-20 evidence-accounting change (②③④).

These pin software behaviour, not the literary corpus:

* ② a `supports` row backed entirely by unverified material keeps half its
  P_gate weight, and a row backed entirely by verified material keeps all of it.
* ③ `verification.depth` cannot claim more than the status it carries, and new
  rows must record a depth.
* ④ a number must be recomputed, traced to a verified material, or explained.
* the two new report tools count what they say they count.
"""

from __future__ import annotations

import datetime
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state
import depth_backfill
import double_reading
import validate_seed
import verification_targets


def mat(status: str, depth: str | None = None) -> dict:
    v = {"status": status, "checked_at": "2026-11-20", "method": "x"}
    if depth:
        v["depth"] = depth
    return {"material_id": "MAT-x", "verification": v}


class SupportDepthRatioTests(unittest.TestCase):
    def test_no_materials_is_none_not_zero(self):
        self.assertIsNone(belief_state.support_verified_ratio({"material_ids": []}, {}))

    def test_all_unverified_is_zero(self):
        materials = {"A": mat("partially_verified"), "B": mat("unverified")}
        ratio = belief_state.support_verified_ratio({"material_ids": ["A", "B"]}, materials)
        self.assertEqual(ratio, 0.0)

    def test_half_verified(self):
        materials = {"A": mat("verified"), "B": mat("partially_verified")}
        self.assertEqual(belief_state.support_verified_ratio({"material_ids": ["A", "B"]}, materials), 0.5)

    def test_missing_material_counts_as_unverified(self):
        materials = {"A": mat("verified")}
        self.assertEqual(belief_state.support_verified_ratio({"material_ids": ["A", "Z"]}, materials), 0.5)

    def test_floor_arithmetic(self):
        # factor = 0.5 + 0.5 * r, with SUPPORT_DEPTH_FLOOR == 0.5
        floor = belief_state.SUPPORT_DEPTH_FLOOR
        self.assertAlmostEqual(floor + (1 - floor) * 0.0, 0.5)
        self.assertAlmostEqual(floor + (1 - floor) * 1.0, 1.0)


class VerificationDepthTests(unittest.TestCase):
    TODAY = datetime.date(2026, 11, 22)

    def check(self, materials: dict, today=None) -> list[str]:
        errors: list[str] = []
        validate_seed.check_verification_depth(materials, errors, today=today or self.TODAY)
        return errors

    def test_abstract_cannot_be_verified(self):
        errors = self.check({"M": mat("verified", "abstract")})
        self.assertTrue(any("cannot carry status 'verified'" in e for e in errors), errors)

    def test_full_text_requires_verified(self):
        errors = self.check({"M": mat("partially_verified", "full_text")})
        self.assertTrue(any("requires status 'verified'" in e for e in errors), errors)

    def test_legacy_row_without_depth_is_not_an_error(self):
        legacy = {"material_id": "MAT-20261101-aaaaaa", "verification": {"status": "verified", "checked_at": "2026-11-01", "method": "x"}}
        self.assertEqual(self.check({"MAT-20261101-aaaaaa": legacy}), [])

    def test_new_row_without_depth_is_an_error(self):
        row = {
            "material_id": "MAT-20261121-aaaaaa",
            "verification": {"status": "verified", "checked_at": "2026-11-21", "method": "x"},
        }
        errors = self.check({"MAT-20261121-aaaaaa": row})
        self.assertTrue(any("must say how far the check went" in e for e in errors), errors)


class NumberTraceabilityTests(unittest.TestCase):
    def run_check(self, evaluations: dict, notes: dict, materials: dict) -> list[str]:
        errors: list[str] = []
        validate_seed.check_number_traceability(
            evaluations, notes, materials, errors, today=datetime.date(2026, 11, 22)
        )
        return errors

    def test_numbers_detected_and_ids_dates_ignored(self):
        self.assertTrue(validate_seed._numbers_in("61.5% of supports rows"))
        self.assertTrue(validate_seed._numbers_in("160/260 rows"))
        self.assertFalse(validate_seed._numbers_in("見た目は 2026-11-20 の記録で、ID は EVL-20261120-e2ad4f"))

    def test_gated_row_without_route_fails(self):
        evals = {
            "EVL-20261121-aaaaaa": {
                "summary": "支持率は 61.5% だった",
                "material_ids": ["M1"],
                "evidence_type": "cross_session_audit",
            }
        }
        errors = self.run_check(evals, {}, {"M1": mat("partially_verified")})
        self.assertTrue(any("no_recompute_reason" in e for e in errors), errors)

    def test_each_of_three_routes_passes(self):
        base = {"summary": "支持率は 61.5% だった", "material_ids": ["M1"], "evidence_type": "cross_session_audit"}
        self.assertEqual(self.run_check({"EVL-20261121-aaaaaa": {**base, "script_command": "python3 x.py"}}, {}, {"M1": mat("partially_verified")}), [])
        self.assertEqual(self.run_check({"EVL-20261121-bbbbbb": base}, {}, {"M1": mat("verified")}), [])
        self.assertEqual(self.run_check({"EVL-20261121-cccccc": {**base, "no_recompute_reason": "図から読んだ値で再計算できない"}}, {}, {"M1": mat("partially_verified")}), [])

    def test_legacy_row_is_not_gated(self):
        evals = {"EVL-20261101-aaaaaa": {"summary": "61.5%", "material_ids": ["M1"], "evidence_type": "cross_session_audit"}}
        self.assertEqual(self.run_check(evals, {}, {"M1": mat("partially_verified")}), [])

    def test_measured_fact_claim_needs_recomputer(self):
        notes = {
            "NOTE-20261121-aaaaaa": {
                "claims": [{"claim_id": "C1", "kind": "measured_fact", "text": "70.6% の対で食い違った"}]
            }
        }
        errors = self.run_check({}, notes, {})
        self.assertTrue(any("recomputer" in e for e in errors), errors)
        notes["NOTE-20261121-aaaaaa"]["claims"][0]["recomputer"] = "python3 tools/double_reading.py --json"
        self.assertEqual(self.run_check({}, notes, {}), [])


class ToolTests(unittest.TestCase):
    def test_double_reading_counts_disagreement_once_per_pair(self):
        materials = {"M": {"material_id": "M", "title": "t", "verification": {"status": "partially_verified"}}}
        read_log = {
            "R1": {"reading": "interpreted", "session_id": "S1", "target": {"type": "material", "id": "M"}, "created_at": "2026-11-01"},
            "R2": {"reading": "contested", "session_id": "S2", "target": {"type": "material", "id": "M"}, "created_at": "2026-11-02"},
            "R3": {"reading": "used_as_context", "session_id": "S3", "target": {"type": "material", "id": "M"}, "created_at": "2026-11-03"},
        }
        result = double_reading.analyse(materials, read_log)
        self.assertEqual(result["materials_read_by_two_or_more_sessions"], 1)
        self.assertEqual(result["session_pairs"], 1)  # S3 is machine context, not a manual reading
        self.assertEqual(result["direction_change_pairs"], 1)

    def test_verification_targets_prefers_the_row_releasing_material(self):
        materials = {
            "M1": {"material_id": "M1", "title": "a", "source": {"year": 2000, "url": "u"}, "verification": {"status": "partially_verified"}},
            "M2": {"material_id": "M2", "title": "b", "source": {"year": 2001, "url": "u"}, "verification": {"status": "partially_verified"}},
        }
        evaluations = {
            "E1": {"evaluation_id": "E1", "verdict": "supports", "material_ids": ["M1"]},
            "E2": {"evaluation_id": "E2", "verdict": "supports", "material_ids": ["M1", "M2"]},
            "E3": {"evaluation_id": "E3", "verdict": "supports", "material_ids": ["M2"]},
            "E4": {"evaluation_id": "E4", "verdict": "supports", "material_ids": ["M2"]},
            "E5": {"evaluation_id": "E5", "verdict": "narrows_scope", "material_ids": ["M1"]},
        }
        result = verification_targets.rank(materials, evaluations, {})
        self.assertEqual(result["unverified_support_rows"], 4)
        self.assertEqual(result["plan"][0]["material_id"], "M2")
        self.assertEqual(result["plan"][0]["rows_released"], 3)
        # rows released are counted once even when both materials backed them
        self.assertEqual(result["rows_releasable_by_all"], 4)


class ReceiptDefectTests(unittest.TestCase):
    """The named defect must stay visible and must not weaken the gate."""

    def test_known_defect_is_advisory_but_still_reported(self):
        sessions = {"SESSION-20261120-a45e52": {"dispersal_seed": "abb76c70", "assigned_role": "proposer"}}
        errors: list[str] = []
        advisories: list[str] = []
        validate_seed.check_role_receipts(
            sessions, errors, advisories, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(advisories), 1)
        self.assertIn("a45e52", advisories[0])

    def test_unknown_session_still_errors(self):
        sessions = {"SESSION-20261121-ffffff": {"dispersal_seed": "x", "assigned_role": "proposer"}}
        errors: list[str] = []
        advisories: list[str] = []
        validate_seed.check_role_receipts(
            sessions, errors, advisories, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(advisories, [])
        self.assertEqual(len(errors), 1)


class DepthBackfillTests(unittest.TestCase):
    def cls(self, method: str, note: str = "") -> str:
        material = {"verification": {"status": "verified", "method": method, "note": note}}
        return depth_backfill.classify(material)[0]

    def test_negation_blocks_full_text(self):
        self.assertNotEqual(self.cls("出版社ページのみ確認。本文は未読。"), "full_text_claim")

    def test_partial_read_is_not_full_text(self):
        self.assertEqual(self.cls("全文のうち第1章のみ読んだ"), "unknown")

    def test_table_only_read_is_results(self):
        self.assertEqual(self.cls("PMC 全文の表3・表4を取得し、数値を照合"), "results_claim")

    def test_abstract_only_is_shallow(self):
        self.assertEqual(self.cls("arXiv 要旨と掲載情報で確認"), "shallow_claim")

    def test_plain_full_text_claim(self):
        self.assertEqual(self.cls("本文を通読し、引用句を確認"), "full_text_claim")

    def test_section_read_is_not_full_text(self):
        # 通読 + 節指定 is contradictory prose; the conservative reading wins.
        self.assertEqual(self.cls("本文を通読し、§3の引用句を確認"), "unknown")

    def test_emit_preserves_status_and_records_inference(self):
        materials = {"M": {"material_id": "M", "verification": {"status": "verified", "method": "本文を通読", "note": "全文"}}}
        rows = depth_backfill.overlay_rows(
            [{"material_id": "M", "reason_clause": "本文を通読"}], materials, "SESSION-x", "2026-11-20"
        )
        self.assertEqual(rows[0]["status"], "verified")
        self.assertEqual(rows[0]["verification_depth"], "full_text")
        self.assertIn("推定", rows[0]["reason"])


if __name__ == "__main__":
    unittest.main()
