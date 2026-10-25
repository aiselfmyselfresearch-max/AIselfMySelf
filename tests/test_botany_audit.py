import unittest

from tools.botany_audit import (
    BOTANY_GROUPS,
    count_term,
    inspect_raw_kanji_breakdown,
    inspect_raw_kanji_in_fragments,
    measure_botany_audit,
    scan_text,
    split_prose_and_quotes,
)


class BotanyAuditTests(unittest.TestCase):
    def test_aikotoba_is_not_double_counted_with_kotoba(self):
        text = "合言葉と合い言葉は、普通の言葉と分けて一度だけ数える。"
        self.assertEqual(count_term(text, "合言葉"), 1)
        self.assertEqual(count_term(text, "合い言葉"), 1)
        self.assertEqual(count_term(text, "言葉"), 1)
        scanned = scan_text(text)
        self.assertEqual(scanned.get("合言葉"), 1)
        self.assertEqual(scanned.get("合い言葉"), 1)
        self.assertEqual(scanned.get("言葉"), 1)

    def test_shokubutsuen_and_hyohon_subtracted_from_shokubutsu(self):
        text = "植物園で植物標本と生きた植物を見る。"
        self.assertEqual(count_term(text, "植物園"), 1)
        self.assertEqual(count_term(text, "植物標本"), 1)
        self.assertEqual(count_term(text, "植物"), 1)
        scanned = scan_text(text)
        self.assertEqual(scanned.get("植物園"), 1)
        self.assertEqual(scanned.get("植物標本"), 1)
        self.assertEqual(scanned.get("植物"), 1)

    def test_shoki_seed_is_subtracted_from_seed(self):
        text = "初期シードから別のシードを作る。"
        self.assertEqual(count_term(text, "初期シード"), 1)
        self.assertEqual(count_term(text, "シード"), 1)

    def test_scribal_absorption_is_unbound(self):
        self.assertFalse(BOTANY_GROUPS["scribal_absorption"]["motif_bound"])
        data = measure_botany_audit(
            [{"fragment_id": "T-1", "text": "草稿の言葉を種類ごとに根拠づける。"}],
            materials=[],
            readings=[],
        )
        groups = data["fragments_prose"]["groups"]
        self.assertEqual(groups["flora_organ"]["count"], 0)
        self.assertEqual(groups["scribal_absorption"]["count"], 4)
        self.assertIn("scribal_absorption", data["unbound_groups"])
        self.assertNotIn("scribal_absorption", data["motif_bound_groups"])

    def test_raw_kanji_breakdown_separates_scribal_from_botanical(self):
        fragments = [
            {
                "fragment_id": "T-2",
                "text": "言葉と合言葉の横に、街路樹の葉が一枚ある。草稿と煙草の横に草木がある。",
            }
        ]
        bd = inspect_raw_kanji_breakdown(fragments)
        self.assertEqual(bd["葉"]["raw_total"], 3)
        self.assertEqual(bd["葉"]["absorbed_count"], 2)
        self.assertEqual(bd["葉"]["residual_count"], 1)
        self.assertEqual(bd["草"]["raw_total"], 3)
        self.assertEqual(bd["草"]["absorbed_count"], 2)
        self.assertEqual(bd["草"]["residual_count"], 1)

    def test_quotes_are_separated_from_prose(self):
        prose, quotes = split_prose_and_quotes("地の文には草稿しかない。「植物の種子と花びら」と引用する。")
        self.assertEqual(quotes, "植物の種子と花びら")
        data = measure_botany_audit(
            [{"fragment_id": "T-3", "text": "地の文には草稿しかない。「植物の種子と花びら」と引用する。"}],
            materials=[],
            readings=[],
        )
        self.assertEqual(data["fragments_prose"]["groups"]["flora_organ"]["count"], 0)
        self.assertEqual(data["fragments_quotes"]["groups"]["flora_organ"]["count"], 3)

    def test_timber_and_tree_graph_are_separated(self):
        data = measure_botany_audit(
            [{"fragment_id": "T-4", "text": "状態の木と問いの枝を閉じ、積み木と木箱と沈水木片を並べる。"}],
            materials=[],
            readings=[],
        )
        groups = data["fragments_prose"]["groups"]
        self.assertEqual(groups["tree_and_graph"]["count"], 2)
        self.assertEqual(groups["timber_and_relic"]["count"], 3)

    def test_count_term_matches_aggregate_for_all_terms(self):
        sample = (
            "植物園の植物標本と植物。初期シードとシード。合言葉と合い言葉と言葉。"
            "沈水木片と木片。枯れ枝と小枝。街路樹の葉と腐った茸。"
        )
        data = measure_botany_audit(
            [{"fragment_id": "T-5", "text": sample}], materials=[], readings=[]
        )
        groups = data["fragments_prose"]["groups"]
        for key, spec in BOTANY_GROUPS.items():
            for term in spec["terms"]:
                self.assertEqual(
                    count_term(sample, term),
                    groups[key]["terms"].get(term, 0),
                    f"mismatch on {term}",
                )
        kwic = inspect_raw_kanji_in_fragments([{"fragment_id": "T-5", "text": sample}])
        self.assertGreaterEqual(len(kwic["木"]), 2)


if __name__ == "__main__":
    unittest.main()
