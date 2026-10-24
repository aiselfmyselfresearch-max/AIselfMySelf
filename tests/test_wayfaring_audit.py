import unittest

from tools.wayfaring_audit import classify_polysemy, measure, split_quotes, strip_quotes


class WayfaringAuditTests(unittest.TestCase):
    def test_empty_archive_reports_zeros(self):
        data = measure([])
        self.assertEqual(data["fragments"], 0)
        self.assertEqual(data["prose_chars"], 0)
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})

    def test_blank_and_empty_cart_do_not_become_sky(self):
        prose = "空欄と空白を残したまま空車が通り、箱は空っぽで、欄は空のままだった。ただ高い空の光があった。"
        bd = classify_polysemy([prose])
        self.assertEqual(bd["空"]["total"], 6)
        self.assertEqual(bd["空"]["blank_or_empty_or_air"], 5)
        self.assertEqual(bd["空"]["remaining_sky_candidates"], 1)

    def test_proper_nouns_and_aozora_bunko_do_not_inflate_landscapes(self):
        fragments = [
            {
                "fragment_id": "TEST-WAY-PROPER",
                "text": "青空文庫で中島敦と三島由紀夫と森鷗外を読み、海馬の記憶を調べた。",
            }
        ]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["外の地形・風景"], {})

    def test_addition_and_sufficiency_do_not_become_walking(self):
        fragments = [
            {
                "fragment_id": "TEST-WAY-001",
                "text": "一行を書き足し、反論を継ぎ足し、それで足りると言った。",
            }
        ]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["歩行・旅・移動"], {})
        self.assertEqual(data["polysemy_breakdown"]["足"]["addition_or_sufficiency"], 3)
        self.assertEqual(data["polysemy_breakdown"]["足"]["remaining_bodily_foot"], 0)

    def test_window_counter_and_negation_are_separated(self):
        prose = "この作業部屋には窓がない。窓口は三度たずね、北側の高窓を押し上げた。"
        bd = classify_polysemy([prose])
        self.assertEqual(bd["窓"]["total"], 3)
        self.assertEqual(bd["窓"]["counter_frame_or_negated"], 2)
        self.assertEqual(bd["窓"]["remaining_architectural_window"], 1)

    def test_quoted_travel_words_are_reported_separately(self):
        text = "「故郷の地図を持って旅に出よう」と誰かが書いたが、机の上には紙しかなかった。"
        self.assertEqual(strip_quotes(text), "と誰かが書いたが、机の上には紙しかなかった。")
        self.assertEqual(split_quotes(text), "「故郷の地図を持って旅に出よう」")
        data = measure([{"fragment_id": "TEST-WAY-002", "text": text}])
        self.assertEqual(data["group_totals"]["歩行・旅・移動"], {})
        self.assertEqual(data["group_totals"]["道・地図・迷子"], {})
        self.assertEqual(data["group_totals"]["故郷・帰郷・亡命"], {})
        self.assertEqual(data["group_totals"]["室内・書記の器（対照）"], {"机": 1, "紙": 1})
        self.assertEqual(data["inside_quotes"], {"旅": 1, "地図": 1, "故郷": 1})

    def test_actual_wayfaring_and_exile_terms_are_counted(self):
        fragments = [
            {
                "fragment_id": "TEST-WAY-003",
                "text": "地図を持たずに坂道を歩いて亡命先の港へ到着し、迷子になった。",
            }
        ]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["歩行・旅・移動"], {"歩いて": 1, "到着": 1})
        self.assertEqual(data["group_totals"]["道・地図・迷子"], {"地図": 1, "迷子": 1, "坂道": 1})
        self.assertEqual(data["group_totals"]["故郷・帰郷・亡命"], {"亡命": 1})
        self.assertEqual(data["group_totals"]["外の地形・風景"], {"港": 1})


if __name__ == "__main__":
    unittest.main()
