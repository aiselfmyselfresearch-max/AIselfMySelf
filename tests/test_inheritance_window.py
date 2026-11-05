"""Tests for packet §4.8 — the un-inherited window.

§4.8 exists so that "who did a later session read?" is visible at the moment a
session chooses what to read, not only in a report written after the fact.  The
constraints that keep it from disturbing measurements already recorded:

  * §4.7 must not inherit the new section's bytes (``packet_sections`` keys it
    separately as ``4.8``);
  * the section must not move with the branch seed, because a §-size that shifts
    per branch cannot be compared across branches;
  * a report without a ``notes`` row is *unmeasurable*, not unread.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import inspect_inquiry  # noqa: E402
from tests import test_inquiry_guidance as base  # noqa: E402


def with_notes(data: dict, rows: list[dict], read_rows: list[dict]) -> dict:
    """Attach ``notes``/``read_log`` fixtures to the shared packet fixture."""
    data = dict(data)
    data["notes"] = {row["note_id"]: row for row in rows}
    data["read_log"] = {row["read_id"]: row for row in read_rows}
    return data


NOTE_A = {
    "note_id": "NOTE-20261105-aaaaaa",
    "path": "readings/a.md",
    "session_id": "SESSION-20261105-aaaaaa",
    "report_session_id": "SESSION-20261105-aaaaaa",
    "date_real": "2026-11-05",
    "created_at": "2026-11-05",
}
NOTE_B = dict(
    NOTE_A,
    note_id="NOTE-20261105-bbbbbb",
    path="readings/b.md",
    session_id="SESSION-20261105-bbbbbb",
    report_session_id="SESSION-20261105-bbbbbb",
    date_real="2026-11-04",
)


def read_row(read_id: str, session_id: str, note_id: str) -> dict:
    return {
        "read_id": read_id,
        "session_id": session_id,
        "target": {"type": "note", "id": note_id},
        "reading": "interpreted",
        "note": "",
        "created_at": "2026-11-05",
    }


class InheritanceWindowTests(unittest.TestCase):
    def test_section_is_present_and_lists_unread_reports(self) -> None:
        data = with_notes(base.fixture(), [NOTE_A, NOTE_B], [])
        packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        self.assertIn("## 4.8 未継承の窓", packet)
        self.assertIn("`readings/a.md`", packet)
        self.assertIn("後続なし", packet)

    def test_an_inherited_report_drops_out_of_the_window(self) -> None:
        data = with_notes(
            base.fixture(), [NOTE_A, NOTE_B],
            [read_row("READ-1", "SESSION-20261105-bbbbbb", "NOTE-20261105-aaaaaa")],
        )
        packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        window = packet.split("## 4.8", 1)[1]
        self.assertNotIn("`readings/a.md`", window)
        self.assertIn("`readings/b.md`", window)

    def test_self_read_is_not_inheritance(self) -> None:
        data = with_notes(
            base.fixture(), [NOTE_A],
            [read_row("READ-1", "SESSION-20261105-aaaaaa", "NOTE-20261105-aaaaaa")],
        )
        packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        self.assertIn("`readings/a.md`", packet.split("## 4.8", 1)[1])

    def test_section_does_not_move_with_the_branch_seed(self) -> None:
        data = with_notes(base.fixture(), [NOTE_A, NOTE_B], [])
        a = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        b = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000002")
        self.assertEqual(
            inspect_inquiry.packet_sections(a)["4.8"],
            inspect_inquiry.packet_sections(b)["4.8"],
        )

    def test_section_is_charged_to_4_8_and_not_to_4_7(self) -> None:
        data = with_notes(base.fixture(), [NOTE_A], [])
        packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        sizes = inspect_inquiry.packet_sections(packet)
        self.assertIn("4.8", sizes)
        # §4.7 may be empty in a hermetic fixture; the regression this guards is
        # that §4.8 is not merged into its neighbour.
        self.assertNotEqual(sizes["4.7"], sizes.get("4.8"))

    def test_window_size_is_bounded(self) -> None:
        notes = [
            dict(NOTE_A, note_id=f"NOTE-2026110{idx}-abcdef", path=f"readings/r{idx}.md")
            for idx in range(1, 9)
        ]
        data = with_notes(base.fixture(), notes, [])
        packet = inspect_inquiry.build_context_packet(
            data, "Q-001", seed="00000001", inheritance_window=8
        )
        listed = [
            line for line in packet.split("## 4.8", 1)[1].splitlines()
            if line.startswith("  - `readings/")
        ]
        self.assertEqual(len(listed), inspect_inquiry.INHERITANCE_LIMIT)

    def test_no_notes_rows_says_unmeasurable(self) -> None:
        data = with_notes(base.fixture(), [], [])
        packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="00000001")
        window = packet.split("## 4.8", 1)[1]
        self.assertIn("窓内に未継承の報告はありません", window)
        self.assertIn("notes 行を持たない報告はそもそも継承を測れません", window)


if __name__ == "__main__":
    unittest.main()
