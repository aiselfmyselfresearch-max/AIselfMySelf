import unittest

from tools.sky_audit import (
    count_month_not_date,
    count_term,
    inspect_raw_kanji_in_fragments,
    measure_sky_audit,
    split_prose_and_quotes,
)


class SkyAuditTests(unittest.TestCase):
    def test_satellite_is_not_a_star(self):
        # 衛星 contains 星; only the star itself should be counted.
        self.assertEqual(count_term("人工衛星が星を隠す。", "星"), 1)
        self.assertEqual(count_term("人工衛星を打ち上げる。", "星"), 0)

    def test_planet_names_are_not_stars(self):
        self.assertEqual(count_term("火星と金星と木星と土星と水星。", "星"), 0)

    def test_constellation_is_counted_once_as_plotting(self):
        # 星座 must not also be counted as 星, and 星座図 must not double count 星座.
        text = "星座を結び、星座図を開く。"
        self.assertEqual(count_term(text, "星"), 0)
        self.assertEqual(count_term(text, "星座"), 1)
        self.assertEqual(count_term(text, "星座図"), 1)

    def test_galaxy_and_light_year_live_in_one_group_each(self):
        data = measure_sky_audit([], materials=[], readings=[])
        # empty corpus sanity check
        self.assertEqual(data["fragments_prose"]["groups"]["star"]["count"], 0)
        text = "銀河系の銀河と、光年の距離。"
        measured = measure_sky_audit(
            [{"fragment_id": "TEST-001", "text": text}], materials=[], readings=[]
        )
        groups = measured["fragments_prose"]["groups"]
        self.assertEqual(groups["cosmos"]["terms"].get("銀河"), 1)
        self.assertEqual(groups["cosmos"]["terms"].get("銀河系"), 1)
        self.assertEqual(groups["delay"]["terms"].get("光年"), 1)
        self.assertNotIn("光年", groups["cosmos"]["terms"])

    def test_date_months_are_subtracted(self):
        self.assertEqual(count_month_not_date("十月二十二日と十二月三十一日、二月。"), 0)
        self.assertEqual(count_month_not_date("三ヶ月ぶりに月を見た。"), 1)
        self.assertEqual(count_month_not_date("天の海に月の舟。"), 1)

    def test_quotes_are_separated_from_prose(self):
        prose, quotes = split_prose_and_quotes("地の文に星はない。「星が落ちた」と声が言う。")
        self.assertEqual(prose, "地の文に星はない。と声が言う。")
        self.assertEqual(quotes, "星が落ちた")
        data = measure_sky_audit(
            [{"fragment_id": "TEST-001", "text": "地の文に星はない。「星が落ちた」と声が言う。"}],
            materials=[],
            readings=[],
        )
        self.assertEqual(data["fragments_prose"]["groups"]["star"]["count"], 1)
        self.assertEqual(data["fragments_quotes"]["groups"]["star"]["count"], 1)

    def test_raw_kanji_counts_blank_field_as_sky(self):
        fragments = [{"fragment_id": "TEST-002", "text": "空欄のまま返す。空白を埋めない。"}]
        data = measure_sky_audit(fragments, materials=[], readings=[])
        # 生字「空」は数えるが、夜空群は0のまま（空欄は空ではない）
        self.assertEqual(data["raw_kanji_counts"]["空"], 2)
        self.assertEqual(data["fragments_prose"]["groups"]["night_sky"]["count"], 0)
        rows = inspect_raw_kanji_in_fragments(fragments)
        self.assertEqual(len(rows["空"]), 2)

    def test_materials_and_readings_are_counted_separately(self):
        data = measure_sky_audit(
            [{"fragment_id": "TEST-003", "text": "星を見ない。"}],
            materials=[{"material_id": "MAT-1", "title": "星座の話", "passage": "光年", "source_note": ""}],
            readings=[("r.md", "夜空と星の報告")],
        )
        self.assertEqual(data["materials"]["groups"]["plotting"]["terms"].get("星座"), 1)
        self.assertEqual(data["materials"]["groups"]["delay"]["terms"].get("光年"), 1)
        self.assertEqual(data["readings"]["groups"]["night_sky"]["terms"].get("夜空"), 1)
        self.assertEqual(data["fragments_prose"]["groups"]["star"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
