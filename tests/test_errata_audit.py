"""Tests for the two re-runnable check kinds added to tools/errata_audit.py.

SESSION-062 added ``audit_group_count`` and ``term_occurrence_count`` so that an
errata record about a number written into a fragment can be re-run against the
ledger as it stands now. These tests pin the behaviour of both kinds.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import errata_audit  # noqa: E402


FRAGMENTS = [
    {"fragment_id": "FRAG-001", "text": "宛先の欄は空のままだ。応答はない。"},
    {"fragment_id": "FRAG-002", "text": "「宛先」と書き、宛先を消した。"},
    {"fragment_id": "FRAG-20261024-abc123", "text": "応答だけが残った。"},
]


class TestTermOccurrenceCount(unittest.TestCase):
    def test_counts_prose_and_quotes_separately(self) -> None:
        prose = errata_audit.run_check(
            {"kind": "term_occurrence_count", "params": {"terms": ["宛先", "応答"], "scope": "prose"}},
            FRAGMENTS,
        )
        self.assertTrue(prose["measurable"])
        self.assertEqual(prose["detail"], "宛先=2 / 応答=2")

        quotes = errata_audit.run_check(
            {"kind": "term_occurrence_count", "params": {"terms": ["宛先", "応答"], "scope": "quotes"}},
            FRAGMENTS,
        )
        self.assertEqual(quotes["detail"], "宛先=1 / 応答=0")

    def test_exclude_fragments_removes_a_document(self) -> None:
        res = errata_audit.run_check(
            {
                "kind": "term_occurrence_count",
                "params": {
                    "terms": ["応答"],
                    "scope": "prose",
                    "exclude_fragments": ["FRAG-20261024-abc123"],
                },
            },
            FRAGMENTS,
        )
        self.assertEqual(res["value"], 1)

    def test_range_limits_the_subset(self) -> None:
        res = errata_audit.run_check(
            {"kind": "term_occurrence_count", "params": {"terms": ["宛先"], "from": 1, "to": 1}},
            FRAGMENTS,
        )
        self.assertEqual(res["value"], 1)


class TestAuditGroupCount(unittest.TestCase):
    def test_prayer_group_is_counted_through_the_mirror(self) -> None:
        res = errata_audit.run_check(
            {
                "kind": "audit_group_count",
                "params": {"module": "prayer_audit", "group": "address_response", "scope": "prose"},
            },
            FRAGMENTS,
        )
        self.assertTrue(res["measurable"])
        self.assertGreaterEqual(res["value"], 3)
        self.assertIn("prayer_audit:address_response", res["detail"])

    def test_unknown_module_is_reported_not_raised(self) -> None:
        res = errata_audit.run_check(
            {"kind": "audit_group_count", "params": {"module": "no_such_mirror", "group": "x"}},
            FRAGMENTS,
        )
        self.assertFalse(res["measurable"])

    def test_missing_group_is_reported_not_raised(self) -> None:
        res = errata_audit.run_check(
            {"kind": "audit_group_count", "params": {"module": "prayer_audit", "group": "no_such_group"}},
            FRAGMENTS,
        )
        self.assertFalse(res["measurable"])

    def test_unknown_kind_stays_unevaluated(self) -> None:
        res = errata_audit.run_check({"kind": "external_source_lookup", "params": {}}, FRAGMENTS)
        self.assertFalse(res["measurable"])


    def test_git_deletions_covers_the_whole_history_by_default(self) -> None:
        cmd = errata_audit.git_deletions_cmd({})
        self.assertEqual(cmd, ["git", "log", "--numstat", "--format=", "--", "state/"])

    def test_git_deletions_honours_a_commit_range_and_paths(self) -> None:
        cmd = errata_audit.git_deletions_cmd(
            {"old": "A^", "new": "A", "paths": ["state/read_log.d", "state/sessions.d"]}
        )
        self.assertEqual(cmd[-4:], ["A^..A", "--", "state/read_log.d", "state/sessions.d"])
        self.assertIn("state/sessions.d", cmd)

    def test_git_deletions_path_and_paths_are_not_mixed(self) -> None:
        cmd = errata_audit.git_deletions_cmd({"path": "readings"})
        self.assertEqual(cmd[-2:], ["--", "readings"])


class TestSchemaReport(unittest.TestCase):
    """The errata ledger is outside validate_seed.COLLECTIONS.

    These tests pin the reporting mirror added on 2026-11-08: it compares rows
    to schema/errata.schema.json, names the disagreements, and never raises,
    never edits, and never turns a disagreement into a failure.
    """

    @staticmethod
    def _row(**over: object) -> dict:
        row = {
            "errata_id": "ERR-TEST-0001",
            "claim": "數が合わない。",
            "claim_location": "readings/2026-11-08-example.md §2",
            "check": {"kind": "manual"},
            "verdict": "contradicted",
            "status": "annotated",
            "created_at": "2026-11-08",
            "note": "テスト用の行。",
        }
        row.update(over)
        return row

    def test_conforming_row_is_counted_not_flagged(self) -> None:
        report = errata_audit.schema_report([self._row()])
        self.assertTrue(report["available"])
        self.assertEqual(report["rows"], 1)
        self.assertEqual(report["conforming"], 1)
        self.assertEqual(report["violations"], [])

    def test_unknown_status_is_named_without_raising(self) -> None:
        report = errata_audit.schema_report([self._row(status="corrected")])
        self.assertEqual(report["conforming"], 0)
        self.assertEqual(len(report["violations"]), 1)
        self.assertEqual(report["violations"][0]["errata_id"], "ERR-TEST-0001")
        self.assertIn("status", report["violations"][0]["errors"][0])

    def test_missing_required_field_and_extra_field_are_both_reported(self) -> None:
        row = self._row(session_id="SESSION-20261108-000000")
        del row["claim_location"]
        report = errata_audit.schema_report([row])
        joined = " ".join(report["violations"][0]["errors"])
        self.assertIn("claim_location", joined)
        self.assertIn("session_id", joined)

    def test_input_rows_are_not_mutated(self) -> None:
        rows = [self._row(status="corrected"), self._row(errata_id="ERR-TEST-0002")]
        before = [dict(r) for r in rows]
        errata_audit.schema_report(rows)
        self.assertEqual(rows, before)

    def test_empty_ledger_reports_zero_without_dividing(self) -> None:
        report = errata_audit.schema_report([])
        self.assertEqual(report["rows"], 0)
        self.assertEqual(report["conforming"], 0)
        self.assertEqual(report["violations"], [])

    def test_missing_schema_degrades_to_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = errata_audit.schema_report([self._row()], root=Path(tmp))
        self.assertFalse(report["available"])
        self.assertEqual(report["rows"], 1)
        self.assertEqual(report["violations"], [])

    def test_errata_stays_outside_the_gated_collections(self) -> None:
        # The mirror is non-blocking precisely because gating would fail on rows
        # that already exist and may not be rewritten. If errata is ever added to
        # COLLECTIONS, this test is the place to reconsider that decision.
        import validate_seed

        self.assertNotIn("errata", validate_seed.COLLECTIONS)


if __name__ == "__main__":
    unittest.main()
