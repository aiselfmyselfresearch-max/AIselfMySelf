"""Tests for tools/removed_rows.py.

The tool compares two snapshots of the ledger and reports what a range removed,
who the removed rows belonged to, and whether their names are still cited in
``readings/*.md``.  These tests exercise the parts that do not need git history.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import removed_rows as rr  # noqa: E402


def row(identifier: str, key: str = "read_id", **extra):
    base = {key: identifier}
    base.update(extra)
    return base


class DiffRowsTest(unittest.TestCase):
    def test_detects_removed_rows(self):
        old = {"R-1": row("R-1"), "R-2": row("R-2")}
        new = {"R-1": row("R-1")}
        delta = rr.diff_rows(old, new)
        self.assertEqual(delta["removed"], ["R-2"])
        self.assertEqual(delta["added"], [])
        self.assertEqual(delta["changed"], [])

    def test_same_id_with_different_content_is_changed_not_removed(self):
        old = {"R-1": row("R-1", note="before")}
        new = {"R-1": row("R-1", note="after")}
        delta = rr.diff_rows(old, new)
        self.assertEqual(delta["removed"], [])
        self.assertEqual(delta["changed"], ["R-1"])

    def test_added_rows_are_separate_from_removed(self):
        delta = rr.diff_rows({}, {"R-9": row("R-9")})
        self.assertEqual(delta["added"], ["R-9"])
        self.assertEqual(delta["removed"], [])


class GroupByTest(unittest.TestCase):
    def test_counts_removed_rows_per_session_most_common_first(self):
        old = {
            "R-1": row("R-1", session_id="S-A"),
            "R-2": row("R-2", session_id="S-B"),
            "R-3": row("R-3", session_id="S-B"),
        }
        counts = rr.group_by(old, ["R-1", "R-2", "R-3"], "session_id")
        self.assertEqual(counts, {"S-B": 2, "S-A": 1})

    def test_missing_field_is_labelled_not_dropped(self):
        counts = rr.group_by({"R-1": {"read_id": "R-1"}}, ["R-1"], "session_id")
        self.assertEqual(counts, {"(none)": 1})


class CollectionForPathTest(unittest.TestCase):
    def test_maps_shard_and_single_file_to_same_collection(self):
        self.assertEqual(rr.collection_for_path("state/read_log.d/2026-12-15-x.jsonl"), "read_log")
        self.assertEqual(rr.collection_for_path("state/read_log.jsonl"), "read_log")

    def test_unmanaged_state_file_has_no_collection(self):
        self.assertIsNone(rr.collection_for_path("state/README.md"))
        self.assertIsNone(rr.collection_for_path("readings/x.md"))


class CiteCountsTest(unittest.TestCase):
    def test_finds_files_that_mention_an_id_and_omits_silent_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "readings").mkdir()
            (root / "readings" / "a.md").write_text("citing R-1 here", encoding="utf-8")
            (root / "readings" / "b.md").write_text("nothing", encoding="utf-8")
            self.assertEqual(rr.cite_counts(["R-1", "R-2"], root), {"R-1": ["a.md"]})


class FormatReportTest(unittest.TestCase):
    def test_reports_zero_citations_and_session_attribution(self):
        data = {
            "old": "A",
            "new": "B",
            "collections": {
                "read_log": {
                    "old_rows": 3,
                    "new_rows": 1,
                    "removed": 2,
                    "added": 0,
                    "changed": 0,
                    "removed_ids": ["R-1", "R-2"],
                    "by_session": {"S-A": 2},
                    "cited": {},
                }
            },
        }
        text = rr.format_report(data)
        self.assertIn("removed   2", text)
        self.assertIn("by S-A: 2", text)
        self.assertIn("cited in prose: 0 of 2", text)


if __name__ == "__main__":
    unittest.main()
