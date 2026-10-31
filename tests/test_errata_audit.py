"""Tests for the two re-runnable check kinds added to tools/errata_audit.py.

SESSION-062 added ``audit_group_count`` and ``term_occurrence_count`` so that an
errata record about a number written into a fragment can be re-run against the
ledger as it stands now. These tests pin the behaviour of both kinds.
"""
from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
