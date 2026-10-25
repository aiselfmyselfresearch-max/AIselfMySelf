"""Tests for tools/secret_audit.py（第37の鏡：秘密・嘘・暗号）."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import secret_audit  # noqa: E402


class TestSecretAudit(unittest.TestCase):
    def test_polysemous_compounds_do_not_trigger_groups(self) -> None:
        sample = (
            "秘書が密度の高い密室で親密に密かに鍵盤を弾き、封筒を同封して封鎖線を越えた。"
            "隠居した隠遁者は電鍵を打った。"
        )
        data = secret_audit.measure([{"fragment_id": "F-TEST-1", "text": sample}])
        for group, total in data["group_sums"].items():
            self.assertEqual(total, 0, f"unexpected hit in {group}: {data['group_totals'][group]}")
        # 生字はあえて補正せず別枠で出る（混在の可視化が目的）
        self.assertTrue(data["raw_totals"].get("密", 0) >= 4)
        self.assertTrue(data["raw_totals"].get("封", 0) >= 3)

    def test_longest_match_does_not_double_count(self) -> None:
        sample = "秘密保持の誓約と、虚偽の証言と、偽造された古文書と、贋作の掛軸。"
        data = secret_audit.measure([{"fragment_id": "F-TEST-2", "text": sample}])
        # 「秘密保持」は守秘の群へ譲り、秘密と隠匿の群からは差し引かれる
        self.assertIsNone(data["group_totals"]["秘密と隠匿"].get("秘密"))
        self.assertEqual(data["group_totals"]["守秘と口止め"].get("秘密保持"), 1)
        self.assertEqual(data["group_totals"]["嘘と偽り"].get("虚偽"), 1)
        self.assertEqual(data["group_totals"]["嘘と偽り"].get("偽造"), 1)
        self.assertEqual(data["group_totals"]["嘘と偽り"].get("贋作"), 1)

    def test_prose_and_quotes_are_separated(self) -> None:
        text = "係は棚の前で口を閉ざした。引用「暗号の鍵は三番目」とだけ書いてあった。"
        outside, inside = secret_audit.strip_quotes(text)
        self.assertNotIn("暗号", outside)
        self.assertIn("暗号", inside)
        self.assertIn("棚の前", outside)

    def test_quote_only_hits_are_not_counted(self) -> None:
        frag = {"fragment_id": "F-TEST-3", "text": "係は何も書かなかった。「嘘と秘密」"}
        data = secret_audit.measure([frag])
        self.assertEqual(data["group_sums"]["嘘と偽り"], 0)
        self.assertEqual(data["group_sums"]["秘密と隠匿"], 0)
        self.assertGreater(data["inside_chars"], 0)

    def test_machine_falsehood_is_a_separate_group_from_lies(self) -> None:
        frag = {"fragment_id": "F-TEST-4", "text": "ハルシネーションと誤情報が混ざる。"}
        data = secret_audit.measure([frag])
        self.assertEqual(data["group_sums"]["嘘と偽り"], 0)
        self.assertEqual(data["group_sums"]["機械の偽り"], 2)

    def test_measure_sums_per_fragment_and_chars(self) -> None:
        frags = [
            {"fragment_id": "F1", "text": "鍵を隠し、誰にも伏せることは誓った。"},
            {"fragment_id": "F2", "text": "何も書かれていない頁。"},
        ]
        data = secret_audit.measure(frags)
        self.assertEqual(data["fragment_count"], 2)
        self.assertEqual(data["group_sums"]["秘密と隠匿"], 1)  # 隠し
        self.assertEqual(data["group_sums"]["守秘と口止め"], 1)  # 伏せる
        self.assertEqual(data["group_sums"]["暗号と鍵"], 1)
        self.assertEqual(data["group_sums"]["漏洩と暴露"], 0)
        self.assertIn("F1", data["per_fragment"])
        self.assertNotIn("F2", data["per_fragment"])

    def test_corpus_document_counting(self) -> None:
        texts = ["秘密の台帳", "秘密の写し", "棚の目録"]
        terms = secret_audit.GROUPS["秘密と隠匿"]
        self.assertEqual(secret_audit.count_corpus_documents(terms, texts), 2)
        self.assertEqual(secret_audit.count_corpus_terms(terms, texts).get("秘密"), 2)

    def test_empty_input_is_zero(self) -> None:
        data = secret_audit.measure([])
        self.assertEqual(data["fragment_count"], 0)
        for total in data["group_sums"].values():
            self.assertEqual(total, 0)
        self.assertEqual(data["raw_totals"], {})


if __name__ == "__main__":
    unittest.main()
