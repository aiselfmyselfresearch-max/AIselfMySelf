"""Unit tests for tools/ghost_audit.py (55th mirror)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.ghost_audit import (
    GHOST_GROUPS,
    count_yurei_literal,
    measure_ghost_audit,
    scan_text,
)


class GhostAuditTests(unittest.TestCase):
    def test_empty_corpora_zero_counts(self) -> None:
        report = measure_ghost_audit([], materials=[], readings=[])
        self.assertEqual(report["fragment_count"], 0)
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertEqual(report["fragments_prose"]["control_total"], 0)
        self.assertEqual(len(report["group_order"]), 7)
        self.assertEqual(len(report["living_group_order"]), 5)
        self.assertEqual(len(report["control_group_order"]), 2)

    def test_apparition_counted_as_living(self) -> None:
        scanned = scan_text("幽霊が廊下に立ち、亡霊が物の怪の話をした。")
        self.assertGreater(sum(scanned["ghost_apparition"].values()), 0)

    def test_lexical_ghost_routed_to_control(self) -> None:
        scanned = scan_text("幽霊文字と幽霊部員、ゴーストタウンの記録。")
        self.assertEqual(scanned["ghost_apparition"], {})
        self.assertGreater(sum(scanned["lexical_ghost"].values()), 0)

    def test_machine_ghost_routed_to_control(self) -> None:
        scanned = scan_text("グリーフボットと追悼アカウント、機械の中の幽霊という比喩。")
        self.assertGreater(sum(scanned["machine_ghost"].values()), 0)
        living_total = sum(
            sum(scanned[k].values()) for k, v in GHOST_GROUPS.items() if v["kind"] == "living"
        )
        self.assertEqual(living_total, 0)

    def test_haunting_and_afterlife_terms(self) -> None:
        scanned = scan_text("怨霊が取り憑き、祟りを恐れて成仏を祈る。三途の川と黄泉の話。")
        self.assertGreater(sum(scanned["haunting_action"].values()), 0)
        self.assertGreater(sum(scanned["ghost_lore"].values()), 0)
        self.assertGreater(sum(scanned["afterlife_world"].values()), 0)

    def test_yurei_literal_excludes_lexical_compounds(self) -> None:
        text = "幽霊文字の一覧と、本物の幽霊の話。"
        self.assertEqual(text.count("幽霊"), 2)
        self.assertEqual(count_yurei_literal(text), 1)

    def test_quoted_ghost_not_in_prose(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST",
            "text": "彼は「幽霊が出た」とだけ書いた。",
        }
        report = measure_ghost_audit([frag], materials=[], readings=[])
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertGreater(report["fragments_quotes"]["living_total"], 0)


if __name__ == "__main__":
    unittest.main()
