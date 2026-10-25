"""Tests for tools/war_audit.py（第36の鏡）."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import war_audit  # noqa: E402


class TestWarAudit(unittest.TestCase):
    def test_non_military_compounds_do_not_trigger(self) -> None:
        sample = (
            "新しい企画への挑戦は善戦し、舌戦と論戦を経て作戦を立て、"
            "相殺して爆速で爆笑をとり、傷心の読者を殴り書きで慰めた。"
            "兵庫の会社は敵対的攻撃と監視あり学習と教師あり学習を研究し、"
            "防御のための探索戦略を論じた。"
        )
        res = war_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_supervision_compound_but_plain_kanshi_is_counted(self) -> None:
        sample = "監視あり学習ではなく、街路の監視を軍事利用する。"
        res = war_audit.scan_text(sample)
        self.assertEqual(res["machine_war"]["by_term"].get("監視"), 1)
        self.assertEqual(res["machine_war"]["count"], 2)  # 「監視」＋「軍事」
        self.assertEqual(res["machine_war"]["by_term"].get("軍事"), 1)

    def test_longest_match_does_not_double_count(self) -> None:
        sample = "戦争と戦場で銃撃があり、虐殺と拷問の記録が残った。"
        res = war_audit.scan_text(sample)
        self.assertEqual(res["combat"]["by_term"].get("戦争"), 1)
        self.assertEqual(res["combat"]["by_term"].get("戦場"), 1)
        self.assertEqual(res["combat"]["by_term"].get("銃撃"), 1)
        self.assertEqual(res["combat"]["count"], 3)
        self.assertEqual(res["violence"]["by_term"].get("虐殺"), 1)
        self.assertEqual(res["violence"]["by_term"].get("拷問"), 1)

    def test_prose_and_quotes_are_separated(self) -> None:
        text = "彼は黙って戸を閉めた。引用「戦場の銃声を聞いた」のあと、また黙った。"
        prose, quotes = war_audit.split_prose_and_quotes(text)
        self.assertNotIn("戦場", prose)
        self.assertIn("戦場", quotes)
        self.assertIn("黙って", prose)

    def test_raw_kanji_kwic_uses_prose_only(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-WAR-1",
            "title": "試験断片",
            "text": "戦のあとの戸の前で立ち止まる。引用「銃」と書かれた紙を見た。",
        }
        kwic = war_audit.inspect_raw_kanji_in_fragments([frag])
        self.assertEqual(len(kwic["戦"]), 1)
        self.assertEqual(kwic["戦"][0]["fragment_id"], "FRAG-TEST-WAR-1")
        self.assertEqual(len(kwic["銃"]), 0)

    def test_measure_counts_layers(self) -> None:
        frags = [
            {"fragment_id": "F1", "title": "a", "text": "平和を願うと書いたが、戦争には触れなかった。"},
            {"fragment_id": "F2", "title": "b", "text": "引用「兵士の遺体」だけが残った。"},
        ]
        mats = [
            {"material_id": "M1", "title": "戦場の記録", "passage": "空襲と虐殺の記録。", "source_note": ""},
        ]
        res = war_audit.measure_war_audit(frags, mats, readings=[("r.md", "追悼と慰霊。")])
        self.assertEqual(res["fragment_count"], 2)
        self.assertEqual(res["fragments_prose"]["groups"]["combat"]["count"], 1)
        self.assertEqual(res["fragments_prose"]["groups"]["peace"]["count"], 1)
        self.assertEqual(res["fragments_quotes"]["groups"]["casualty"]["count"], 1)
        self.assertEqual(res["materials"]["groups"]["combat"]["count"], 2)  # 表題「戦場」＋本文「空襲」
        self.assertEqual(res["materials"]["groups"]["violence"]["count"], 1)
        self.assertEqual(res["readings"]["groups"]["memorial"]["count"], 2)
        self.assertIn("machine_war", res["group_order"])

    def test_empty_input_is_zero(self) -> None:
        res = war_audit.measure_war_audit([], [], readings=[])
        for block in ("fragments_prose", "fragments_quotes", "materials", "readings"):
            self.assertEqual(res[block]["char_total"], 0)
            for info in res[block]["groups"].values():
                self.assertEqual(info["count"], 0)


if __name__ == "__main__":
    unittest.main()
