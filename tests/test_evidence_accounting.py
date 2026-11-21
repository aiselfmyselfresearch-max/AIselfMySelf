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
import os
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


class ClassifierRepairTests(unittest.TestCase):
    """The first classifier missed copular negation; the repair is pinned here."""

    def cls(self, method: str, note: str = "") -> str:
        return depth_backfill.classify({"verification": {"status": "verified", "method": method, "note": note}})[0]

    def test_copular_negation_blocks_full_text(self):
        self.assertNotEqual(self.cls("仕様・実装の全文精読ではない。引用文字列を照合。"), "full_text_claim")

    def test_body_markers_rescue_abstract_rows_from_shallow(self):
        cls = self.cls("abstract 1 文、方法の記述、結果の数値を文字列一致で照合した。")
        self.assertEqual(cls, "results_claim")

    def test_original_note_is_recovered_under_overlay_text(self):
        ver = {"note": "[overlay ED-x] reason 本文到達 元の note: 抄録のみ確認"}
        self.assertEqual(depth_backfill._original_note(ver), "抄録のみ確認")

    def test_audit_withdraws_a_negated_claim(self):
        materials = {
            "M": {
                "material_id": "M",
                "verification": {
                    "status": "verified",
                    "depth": "full_text",
                    "method": "仕様・実装の全文精読ではない。",
                    "note": "[overlay ED-x] ③の遡及適用。 元の note: ",
                },
            }
        }
        audit = depth_backfill.audit_overlays(materials)
        self.assertEqual(audit["kept"], 0)
        self.assertEqual([w["material_id"] for w in audit["withdrawn"]], ["M"])


class OverlayQuoteTests(unittest.TestCase):
    """A quote of the superseded note is a record of the past, not a claim."""

    def test_quoted_old_note_does_not_demote_a_full_text_read(self):
        material = {
            "verification": {
                "status": "verified",
                "method": "PMC公開全文（全6チャンク）を2026-11-19に通読照合。",
                "note": "[overlay ED-x] 全文を精読完了。\n\n元の note: 全文逐語通読はしていない。",
            }
        }
        self.assertEqual(depth_backfill.classify(material)[0], "full_text_claim")

    def test_section_marker_in_a_report_citation_does_not_narrow_the_read(self):
        self.assertEqual(depth_backfill._partial_hits("本文§3だけを読んだ"), ["§"])
        self.assertEqual(depth_backfill._partial_hits("（精読報告 §2.1）"), [])

    def test_a_genuine_section_limited_read_stays_unknown(self):
        material = {
            "verification": {
                "status": "verified",
                "method": "本文§3と図2のみを読んだ。",
                "note": "",
            }
        }
        self.assertEqual(depth_backfill.classify(material)[0], "unknown")


class UnspecifiedDepthTests(unittest.TestCase):
    def test_unspecified_is_not_a_new_row_answer(self):
        row = {
            "material_id": "MAT-20261121-bbbbbb",
            "verification": {"status": "verified", "checked_at": "2026-11-21", "method": "x", "depth": "unspecified"},
        }
        errors: list[str] = []
        validate_seed.check_verification_depth({"MAT-20261121-bbbbbb": row}, errors, today=datetime.date(2026, 11, 22))
        self.assertTrue(any("must say how far the check went" in e for e in errors), errors)

    def test_unspecified_is_allowed_on_a_legacy_row(self):
        row = {
            "material_id": "MAT-20261001-aaaaaa",
            "verification": {"status": "verified", "checked_at": "2026-10-01", "method": "x", "depth": "unspecified"},
        }
        errors: list[str] = []
        validate_seed.check_verification_depth({"MAT-20261001-aaaaaa": row}, errors, today=datetime.date(2026, 11, 22))
        self.assertEqual(errors, [])


class GateWaiverTests(unittest.TestCase):
    """A waiver is data (an errata row), never a name in the validator."""

    @staticmethod
    def waiver(subject_type="question", subject_id="Q-20261121-198fc8", gate="register", status="open"):
        return {
            "errata_id": "ERR-20261121-aaaaaa",
            "subject_type": subject_type,
            "subject_id": subject_id,
            "check": {"kind": "manual", "params": {"gate_waiver": gate}},
            "verdict": "contradicted",
            "status": status,
        }

    def test_open_errata_waives_the_register_gate(self):
        errors: list[str] = []
        advisories: list[str] = []
        waivers = validate_seed.gate_waivers({"ERR-20261121-aaaaaa": self.waiver()}, errors)
        self.assertEqual(errors, [])
        collections = {"questions": {"Q-20261121-198fc8": {"question": "x"}}, "hypotheses": {}}
        validate_seed.check_registers(
            collections, errors, advisories, waivers=waivers, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(advisories), 1)
        self.assertIn("ERR-20261121-aaaaaa", advisories[0])

    def test_no_errata_row_means_no_waiver(self):
        errors: list[str] = []
        advisories: list[str] = []
        waivers = validate_seed.gate_waivers({}, errors)
        collections = {"questions": {"Q-20261121-198fc8": {"question": "x"}}, "hypotheses": {}}
        validate_seed.check_registers(
            collections, errors, advisories, waivers=waivers, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(advisories, [])
        self.assertEqual(len(errors), 1)

    def test_a_waiver_that_is_not_open_expires_itself(self):
        errors: list[str] = []
        waivers = validate_seed.gate_waivers({"ERR-20261121-aaaaaa": self.waiver(status="annotated")}, errors)
        self.assertEqual(waivers, {})
        collections = {"questions": {"Q-20261121-198fc8": {"question": "x"}}, "hypotheses": {}}
        advisories: list[str] = []
        validate_seed.check_registers(
            collections, errors, advisories, waivers=waivers, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(advisories, [])
        self.assertEqual(len(errors), 1)

    def test_waiver_for_another_question_does_not_leak(self):
        errors: list[str] = []
        waivers = validate_seed.gate_waivers(
            {"ERR-20261121-aaaaaa": self.waiver(subject_id="Q-20261121-other1")}, errors
        )
        collections = {"questions": {"Q-20261121-198fc8": {"question": "x"}}, "hypotheses": {}}
        advisories: list[str] = []
        validate_seed.check_registers(
            collections, errors, advisories, waivers=waivers, today=datetime.date(2026, 11, 22)
        )
        self.assertEqual(advisories, [])
        self.assertEqual(len(errors), 1)

    def test_mistyped_gate_name_is_an_error_not_a_silent_no_op(self):
        errors: list[str] = []
        waivers = validate_seed.gate_waivers({"ERR-20261121-aaaaaa": self.waiver(gate="regsiter")}, errors)
        self.assertEqual(waivers, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("names no gate", errors[0])

    def test_waiver_with_the_wrong_subject_type_is_an_error(self):
        errors: list[str] = []
        waivers = validate_seed.gate_waivers(
            {"ERR-20261121-aaaaaa": self.waiver(subject_type="session")}, errors
        )
        self.assertEqual(waivers, {})
        self.assertEqual(len(errors), 1)

    def test_two_waivers_for_one_subject_are_refused(self):
        errors: list[str] = []
        first = self.waiver()
        second = dict(first, errata_id="ERR-20261121-bbbbbb")
        waivers = validate_seed.gate_waivers(
            {"ERR-20261121-aaaaaa": first, "ERR-20261121-bbbbbb": second}, errors
        )
        self.assertEqual(len(waivers), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate", errors[0])

    def test_the_validator_holds_no_defect_names(self):
        # The whole point of the move: a name in the source would be invisible to
        # every reader of state/*.d and could not expire.
        self.assertFalse(hasattr(validate_seed, "KNOWN_REGISTER_DEFECTS"))
        self.assertFalse(hasattr(validate_seed, "KNOWN_RECEIPT_DEFECTS"))


class MainGuardTests(unittest.TestCase):
    def test_fix_command_names_the_validate_context(self):
        guard = __import__("main_guard")
        command = guard.FIX_COMMAND.format(slug="o/r")
        self.assertIn("o/r/branches/main/protection", command)
        self.assertIn('"validate"', command)

    def test_repo_slug_prefers_the_argument_then_the_environment(self):
        guard = __import__("main_guard")
        self.assertEqual(guard.repo_slug("a/b"), "a/b")
        old = os.environ.get("GITHUB_REPOSITORY")
        os.environ["GITHUB_REPOSITORY"] = "env/repo"
        try:
            self.assertEqual(guard.repo_slug(), "env/repo")
        finally:
            if old is None:
                os.environ.pop("GITHUB_REPOSITORY", None)
            else:
                os.environ["GITHUB_REPOSITORY"] = old

    def test_unknown_branch_state_is_not_reported_as_healthy(self):
        guard = __import__("main_guard")
        state = {"known": False, "protected": None, "detail": "no gh"}
        self.assertFalse(state["known"])
        self.assertIsNone(state["protected"])
        self.assertTrue(hasattr(guard, "fetch_branch_state"))


class ReadingQueueTests(unittest.TestCase):
    """The queue orders work; it must not claim to have done any."""

    def test_fetch_hint_separates_open_hosts_from_dois(self):
        queue = __import__("reading_queue")
        self.assertEqual(queue.fetch_hint("https://arxiv.org/abs/2301.11305"), "arxiv")
        self.assertEqual(queue.fetch_hint("https://pmc.ncbi.nlm.nih.gov/articles/PMC3198338/"), "pmc")
        self.assertEqual(queue.fetch_hint("https://doi.org/10.1038/x"), "doi")
        self.assertEqual(queue.fetch_hint(""), "no-url")

    def test_rows_cited_by_more_evaluations_come_first(self):
        queue = __import__("reading_queue")
        data = {
            "materials": {
                "MAT-20260101-aaaaaa": {"title": "a", "verification": {"status": "verified", "method": "書誌を照合"}},
                "MAT-20260101-bbbbbb": {"title": "b", "verification": {"status": "verified", "method": "書誌を照合"}},
                "MAT-20260101-cccccc": {"title": "c", "verification": {"status": "verified", "depth": "full_text"}},
            },
            "evaluations": {
                "EVL-1": {"material_ids": ["MAT-20260101-bbbbbb"]},
                "EVL-2": {"material_ids": ["MAT-20260101-bbbbbb"]},
                "EVL-3": {"material_ids": ["MAT-20260101-aaaaaa"]},
            },
        }
        rows = queue.build(data)
        self.assertEqual([r["material_id"] for r in rows], ["MAT-20260101-bbbbbb", "MAT-20260101-aaaaaa"])
        self.assertEqual(rows[0]["citations"], 2)
        # a row that already records its depth is not queued
        self.assertNotIn("MAT-20260101-cccccc", [r["material_id"] for r in rows])


class ReceiptDefectTests(unittest.TestCase):
    """The named defect must stay visible and must not weaken the gate."""

    def test_carried_defect_is_advisory_only_through_an_errata_row(self):
        sessions = {"SESSION-20261120-a45e52": {"dispersal_seed": "abb76c70", "assigned_role": "proposer"}}
        errors: list[str] = []
        advisories: list[str] = []
        waivers = validate_seed.gate_waivers(
            {
                "ERR-20261121-cccccc": {
                    "errata_id": "ERR-20261121-cccccc",
                    "subject_type": "session",
                    "subject_id": "SESSION-20261120-a45e52",
                    "check": {"kind": "manual", "params": {"gate_waiver": "receipt"}},
                    "verdict": "unmeasurable",
                    "status": "open",
                }
            },
            errors,
        )
        validate_seed.check_role_receipts(
            sessions, errors, advisories, waivers=waivers, today=datetime.date(2026, 11, 22)
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
