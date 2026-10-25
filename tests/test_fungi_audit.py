"""Unit tests for tools/fungi_audit.py (54th mirror)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.fungi_audit import (
    FUNGI_GROUPS,
    count_fungi_literal,
    measure_fungi_audit,
    scan_text,
)


class FungiAuditTests(unittest.TestCase):
    def test_empty_corpora_zero_counts(self) -> None:
        report = measure_fungi_audit([], materials=[], readings=[])
        self.assertEqual(report["fragment_count"], 0)
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertEqual(report["fragments_prose"]["control_total"], 0)
        self.assertEqual(len(report["group_order"]), 7)
        self.assertEqual(len(report["living_group_order"]), 5)
        self.assertEqual(len(report["control_group_order"]), 2)

    def test_bacteria_and_hygiene_routed_to_control(self) -> None:
        scanned = scan_text("細菌を殺菌し、滅菌した器具で抗菌コートを除菌する。")
        self.assertEqual(scanned["fungi_body"], {})
        self.assertGreater(sum(scanned["microbe_medicine"].values()), 0)

    def test_fungi_terms_counted_as_living(self) -> None:
        scanned = scan_text("菌糸が倒木に伸び、子実体のキノコが胞子を飛ばす。地衣類は共生体だ。")
        self.assertGreater(sum(scanned["fungi_body"].values()), 0)
        self.assertGreater(sum(scanned["spore_cycle"].values()), 0)
        self.assertGreater(sum(scanned["symbiosis_web"].values()), 0)

    def test_fermentation_terms_counted(self) -> None:
        scanned = scan_text("麹菌が米を糖化し、杜氏がもろみを仕込む。味噌と醤油が発酵する。")
        self.assertGreater(sum(scanned["fermentation_craft"].values()), 0)

    def test_culture_metaphor_routed_to_control(self) -> None:
        scanned = scan_text("細胞培養の培地と培養肉、インキュベーターの錆。")
        living_total = sum(
            sum(scanned[k].values()) for k, v in FUNGI_GROUPS.items() if v["kind"] == "living"
        )
        self.assertGreater(sum(scanned["culture_metaphor"].values()), 0)
        self.assertEqual(scanned["fungi_body"], {})
        self.assertGreaterEqual(living_total, 0)

    def test_count_fungi_literal_strips_bacterial_compounds(self) -> None:
        self.assertEqual(count_fungi_literal("細菌と殺菌と菌糸と麹菌"), 2)
        self.assertEqual(count_fungi_literal("種類と種明かし"), 0)

    def test_measure_shape(self) -> None:
        report = measure_fungi_audit(
            [{"fragment_id": "F1", "text": "発酵が進み、菌が増える「引用の菌」"}],
            materials=[{"material_id": "M1", "title": "菌類", "passage": "胞子", "source_note": ""}],
            readings=[("r.md", "# 報告\n腐敗と朽ち")],
        )
        self.assertEqual(report["fragment_count"], 1)
        self.assertEqual(report["kin_total"], 1)
        self.assertIn("fungi_body", report["group_order"])


if __name__ == "__main__":
    unittest.main()
