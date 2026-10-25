"""Unit tests for tools/genealogy_audit.py (56th mirror)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.genealogy_audit import (
    GENEALOGY_GROUPS,
    count_raireki_literal,
    measure_genealogy_audit,
    scan_text,
)


class GenealogyAuditTests(unittest.TestCase):
    def test_empty_corpora_zero_counts(self) -> None:
        report = measure_genealogy_audit([], materials=[], readings=[])
        self.assertEqual(report["fragment_count"], 0)
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertEqual(report["fragments_prose"]["control_total"], 0)
        self.assertEqual(len(report["group_order"]), 7)
        self.assertEqual(len(report["living_group_order"]), 5)
        self.assertEqual(len(report["control_group_order"]), 2)

    def test_text_transmission_counted(self) -> None:
        scanned = scan_text("写本の異本を底本と校本に分け、原典の写しを取る。")
        self.assertGreater(sum(scanned["text_transmission"].values()), 0)

    def test_record_provenance_counted(self) -> None:
        scanned = scan_text("この冊子の来歴は、旧蔵者の蔵書印と寄贈の記録で辿れる。出典を明記する。")
        self.assertGreater(sum(scanned["record_provenance"].values()), 0)

    def test_machine_provenance_routed_to_control(self) -> None:
        scanned = scan_text("ブランチを切り、コミットしてマージする。バージョン管理の履歴。")
        self.assertGreater(sum(scanned["machine_provenance"].values()), 0)
        living_total = sum(
            sum(scanned[k].values()) for k, v in GENEALOGY_GROUPS.items() if v["kind"] == "living"
        )
        self.assertEqual(living_total, 0)

    def test_metaphor_origin_routed_to_control(self) -> None:
        scanned = scan_text("生みの親と呼ばれる温床の話。")
        self.assertGreater(sum(scanned["metaphor_origin"].values()), 0)

    def test_raireki_literal(self) -> None:
        self.assertEqual(count_raireki_literal("来歴と履歴と歴史"), 1)

    def test_quoted_not_in_prose(self) -> None:
        frag = {"fragment_id": "FRAG-TEST", "text": "彼は「来歴不明」とだけ書いた。"}
        report = measure_genealogy_audit([frag], materials=[], readings=[])
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertGreater(report["fragments_quotes"]["living_total"], 0)


if __name__ == "__main__":
    unittest.main()
