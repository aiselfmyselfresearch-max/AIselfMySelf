"""Tests for tools/prayer_audit.py (第34の鏡)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import prayer_audit  # noqa: E402


class TestPrayerAudit(unittest.TestCase):
    def test_compound_exclusions_do_not_trigger_false_positives(self) -> None:
        sample = (
            "神経質な神話と経済経験の話をし、文化祭と体育祭のあと、失礼のない礼儀で謝礼を渡した。"
            "勤務先で提唱された願望のモデルケースを礼賛した。"
        )
        res = prayer_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_prayer_ritual_and_congregation_groups(self) -> None:
        sample = "祭壇に数珠を置き、僧侶が読経した。祈りと念仏を唱えた。"
        res = prayer_audit.scan_text(sample)
        self.assertEqual(res["sacred"]["by_term"], {"祭壇": 1})
        self.assertEqual(res["ritual"]["by_term"], {"数珠": 1})
        self.assertEqual(res["congregation"]["by_term"], {"僧侶": 1})
        self.assertEqual(
            res["prayer_act"]["by_term"], {"読経": 1, "祈り": 1, "念仏": 1, "唱え": 1}
        )

    def test_longest_match_avoids_double_counting(self) -> None:
        sample = "読経と経文とお経を唱え、唱名した。"
        res = prayer_audit.scan_text(sample)
        self.assertEqual(res["prayer_act"]["count"], 5)

    def test_machine_and_address_groups_are_separate(self) -> None:
        sample = "ロボットが自動で反復し、宛先へ応答した。返事は無言だった。"
        res = prayer_audit.scan_text(sample)
        self.assertEqual(res["machine_repetition"]["count"], 3)
        self.assertEqual(res["address_response"]["count"], 4)

    def test_polysemy_breakdown_keeps_positions(self) -> None:
        poly = prayer_audit.analyze_polysemy("神話の神と神経、経済と祈り")
        self.assertEqual(poly["神"]["total"], 3)
        self.assertEqual(poly["神"]["non_target_compound"], 2)
        self.assertEqual(poly["神"]["remaining_candidate"], 1)
        self.assertEqual(poly["経"]["non_target_compound"], 2)  # 神経・経済
        self.assertEqual(poly["祈"]["remaining_candidate"], 1)

    def test_measure_prayer_audit_splits_prose_and_quotes(self) -> None:
        fragments = [
            {"fragment_id": "F1", "text": "「祈り」と書いて、宛先を空にした。"},
            {"fragment_id": "F2", "text": "機械が反復する。"},
        ]
        data = prayer_audit.measure_prayer_audit(fragments)
        self.assertEqual(data["fragment_count"], 2)
        self.assertEqual(data["fragments_prose"]["groups"]["prayer_act"]["count"], 0)
        self.assertEqual(data["fragments_quotes"]["groups"]["prayer_act"]["count"], 1)
        self.assertEqual(data["fragments_prose"]["groups"]["address_response"]["count"], 1)
        self.assertEqual(data["fragments_prose"]["groups"]["machine_repetition"]["count"], 2)
        self.assertEqual(data["raw_kanji_counts"]["祈"], 0)  # 生字KWICは地の文のみ（祈りは引用内）


if __name__ == "__main__":
    unittest.main()
