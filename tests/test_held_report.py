"""Tests for ``tools/held_report.py`` — the hold inventory.

The tool exists because a ``reading_held`` claim keeps its original tense
forever.  Its contract is narrow: it reports (1) holds closed by an explicit
``supersedes``, (2) holds whose text mentions an ID that a *later* note or
session also touches, and (3) everything else as open.  It never decides whether
a hold is closed — Japanese polarity cannot be classified by rule here — and it
never writes.

The tests below pin those properties: time direction, the question-ID exclusion,
the unmatchable count, and the absence of writes.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import held_report  # noqa: E402


def note(nid, when, claims, supersedes=None, path=None):
    row = {
        "note_id": nid,
        "path": path or f"readings/{nid}.md",
        "session_id": f"SESSION-{nid[-6:]}",
        "created_at": when,
        "claims": claims,
    }
    if supersedes:
        row["supersedes"] = supersedes
    return row


def held(cid, text, **extra):
    claim = {"claim_id": cid, "kind": "reading_held", "text": text}
    claim.update(extra)
    return claim


class HeldReportTest(unittest.TestCase):
    def report(self, notes, reads=()):
        return held_report.build(notes, list(reads))

    def test_hold_with_nothing_later_is_open(self):
        out = self.report([note("NOTE-1", "2026-11-01T00:00:00Z",
                               [held("c1", "素材 MAT-LIT-001 は未読のまま保留。")])])
        self.assertEqual(len(out["held"]), 1)
        self.assertEqual(out["open"][0]["claim_id"], "c1")

    def test_supersedes_closes_a_hold(self):
        notes = [
            note("NOTE-1", "2026-11-01T00:00:00Z", [held("c1", "保留。MAT-LIT-001")]),
            note("NOTE-2", "2026-11-02T00:00:00Z", [], supersedes=["NOTE-1"]),
        ]
        out = self.report(notes)
        self.assertEqual(len(out["closed"]), 1)
        self.assertEqual(out["closed"][0]["closed_by"], ["NOTE-2"])

    def test_later_note_sharing_a_material_is_a_candidate(self):
        notes = [
            note("NOTE-1", "2026-11-01T00:00:00Z", [held("c1", "MAT-LIT-001 を保留。")]),
            note("NOTE-2", "2026-11-03T00:00:00Z",
                 [{"claim_id": "c9", "kind": "reading_revised", "text": "MAT-LIT-001 を読んだ。"}]),
        ]
        out = self.report(notes)
        self.assertEqual(out["touched"][0]["claim_id"], "c1")
        self.assertEqual(out["touched"][0]["touched_by"][0]["note_id"], "NOTE-2")

    def test_earlier_note_is_not_a_candidate(self):
        notes = [
            note("NOTE-2", "2026-11-05T00:00:00Z", [held("c1", "MAT-LIT-001 を保留。")]),
            note("NOTE-1", "2026-11-01T00:00:00Z",
                 [{"claim_id": "c9", "kind": "measured_fact", "text": "MAT-LIT-001 の実測。"}]),
        ]
        out = self.report(notes)
        self.assertEqual(out["open"][0]["claim_id"], "c1")

    def test_shared_question_id_alone_is_not_a_candidate(self):
        # Every claim about a central question shares one; that says nothing.
        notes = [
            note("NOTE-1", "2026-11-01T00:00:00Z",
                 [held("c1", "Q-003 については保留。")]),
            note("NOTE-2", "2026-11-03T00:00:00Z",
                 [{"claim_id": "c9", "kind": "reading_revised", "text": "Q-003 に触れた。"}]),
        ]
        out = self.report(notes)
        self.assertEqual(out["open"][0]["claim_id"], "c1")
        self.assertEqual(out["unmatchable"][0]["claim_id"], "c1")

    def test_read_log_touch_counts(self):
        notes = [note("NOTE-1", "2026-11-01T00:00:00Z", [held("c1", "MAT-LIT-001 を保留。")])]
        reads = [{
            "read_id": "READ-1",
            "session_id": "SESSION-x",
            "created_at": "2026-11-04T00:00:00Z",
            "target": {"type": "material", "id": "MAT-LIT-001"},
        }]
        out = self.report(notes, reads)
        self.assertEqual(out["touched"][0]["touched_by"][0]["session_id"], "SESSION-x")

    def test_only_reading_held_kind_is_listed(self):
        notes = [note("NOTE-1", "2026-11-01T00:00:00Z", [
            held("c1", "保留。"),
            {"claim_id": "c2", "kind": "reading_revised", "text": "改訂。"},
        ])]
        out = self.report(notes)
        self.assertEqual([r["claim_id"] for r in out["held"]], ["c1"])

    def test_main_writes_nothing(self):
        before = {p: p.stat().st_mtime_ns for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(held_report.main(["--limit", "1"]), 0)
        after = {p: p.stat().st_mtime_ns for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
