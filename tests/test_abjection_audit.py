"""Tests for tools/abjection_audit.py（第35の鏡）."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import abjection_audit  # noqa: E402


class TestAbjectionAudit(unittest.TestCase):
    def test_compounds_and_ordinals_do_not_trigger(self) -> None:
        sample = (
            "夜間バッチ第四便は不便になったからではなく、郵便の便箋と穏便な便りを"
            "便利にしたためで、泥棒の泥沼や雲泥の差、洗練された清朝の浄瑠璃を語る。"
        )
        res = abjection_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_longest_match_does_not_double_count(self) -> None:
        sample = "糞尿と屎尿を汲み取り、汚物と廃棄物を捨て場へ運ぶ。"
        res = abjection_audit.scan_text(sample)
        self.assertEqual(res["excretion"]["by_term"].get("糞尿"), 1)
        self.assertEqual(res["excretion"]["by_term"].get("屎尿"), 1)
        self.assertEqual(res["excretion"]["by_term"].get("汲み取り"), 1)
        # 「糞」「尿」「便」単独では二重計上しない
        self.assertNotIn("糞", res["excretion"]["by_term"])
        self.assertNotIn("尿", res["excretion"]["by_term"])
        self.assertEqual(res["defilement"]["by_term"].get("汚物"), 1)
        self.assertEqual(res["discard"]["by_term"].get("廃棄物"), 1)
        self.assertEqual(res["discard"]["by_term"].get("捨て場"), 1)

    def test_prose_and_quotes_are_separated(self) -> None:
        text = "彼は黙って水を流した。引用「糞尿を運ぶ者を見上げて」のあと、また黙った。"
        prose, quotes = abjection_audit.split_prose_and_quotes(text)
        self.assertNotIn("糞尿", prose)
        self.assertIn("糞尿", quotes)
        self.assertIn("黙って", prose)
        self.assertNotIn("黙って", quotes)

    def test_raw_kanji_kwic_uses_prose_only(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-ABJ-1",
            "title": "試験断片",
            "text": "便所の前で立ち止まる。引用「糞」と書かれた紙を見た。",
        }
        kwic = abjection_audit.inspect_raw_kanji_in_fragments([frag])
        self.assertEqual(len(kwic["便"]), 1)
        self.assertEqual(len(kwic["糞"]), 0)
        self.assertEqual(kwic["便"][0]["fragment_id"], "FRAG-TEST-ABJ-1")

    def test_measure_counts_layers(self) -> None:
        frags = [
            {"fragment_id": "F1", "title": "a", "text": "汚れを見ないふりをして、ごみを捨てると言った。"},
            {"fragment_id": "F2", "title": "b", "text": "引用「腐った茸」だけが残った。"},
        ]
        mats = [
            {"material_id": "M1", "title": "浄化槽の記録", "passage": "汲み取りと祓いの記録。", "source_note": ""},
        ]
        res = abjection_audit.measure_abjection_audit(frags, mats, readings=[("r.md", "下水と腐敗。")])
        self.assertEqual(res["fragment_count"], 2)
        self.assertGreaterEqual(res["fragments_prose"]["groups"]["discard"]["count"], 2)
        self.assertEqual(res["fragments_quotes"]["groups"]["decay"]["count"], 1)
        self.assertEqual(res["materials"]["groups"]["excretion"]["count"], 2)  # 表題の「浄化槽」＋本文の「汲み取り」
        self.assertEqual(res["readings"]["groups"]["defilement"]["count"], 0)
        self.assertIn("machine_waste", res["group_order"])

    def test_empty_input_is_zero(self) -> None:
        res = abjection_audit.measure_abjection_audit([], [], readings=[])
        for block in ("fragments_prose", "fragments_quotes", "materials", "readings"):
            self.assertEqual(res[block]["char_total"], 0)
            for info in res[block]["groups"].values():
                self.assertEqual(info["count"], 0)


if __name__ == "__main__":
    unittest.main()
