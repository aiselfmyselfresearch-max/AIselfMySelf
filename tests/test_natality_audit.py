import unittest

from tools.natality_audit import (
    classify_polysemy,
    count_group,
    measure,
    split_quotes,
    strip_quotes,
)


class NatalityAuditTests(unittest.TestCase):
    def test_empty_archive_reports_zeros(self):
        data = measure([])
        self.assertEqual(data["fragments"], 0)
        self.assertEqual(data["prose_chars"], 0)
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})

    def test_longest_match_wins_so_birth_and_upbringing_are_not_double_counted(self):
        counts = count_group(
            "生まれることと生まれた日を書き、育てる手と育てない父を分けた。",
            ("生まれる", "生まれた", "生まれ", "育てる", "育て"),
        )
        self.assertEqual(
            counts,
            {"生まれる": 1, "生まれた": 1, "育てる": 1, "育て": 1},
        )

    def test_academic_fields_and_utensils_are_not_counted_as_childhood_or_learning(self):
        prose = (
            "文学と哲学と心理学の学者が椅子に座り、格子の向こうで拍子を取り、"
            "生産された産物の分布を親愛なる読者へ送る。"
        )
        data = measure([{"fragment_id": "TEST-NAT-001", "text": prose}])
        self.assertEqual(data["group_totals"]["誕生・出産（産む・生まれる）"], {})
        self.assertEqual(data["group_totals"]["乳幼児・幼少（幼さ・片言）"], {})
        self.assertEqual(data["group_totals"]["養育・親子・世代（育てる・継ぐ）"], {})
        self.assertEqual(data["group_totals"]["教育・学習（教える・学ぶ）"], {})
        self.assertEqual(data["group_totals"]["成人の書記役割（対照）"], {"読者": 1})
        breakdown = data["polysemy_breakdown"]
        self.assertEqual(breakdown["学"]["remaining_natality_candidate"], 0)
        self.assertEqual(breakdown["産"]["remaining_natality_candidate"], 0)
        self.assertEqual(breakdown["子"]["remaining_natality_candidate"], 0)
        self.assertEqual(breakdown["親"]["remaining_natality_candidate"], 0)

    def test_quoted_book_titles_with_tanjo_are_separated_from_prose(self):
        text = "『悲劇の誕生』と『監獄の誕生』を棚に戻し、書き手は黙った。"
        self.assertEqual(strip_quotes(text), "とを棚に戻し、書き手は黙った。")
        self.assertEqual(split_quotes(text), "『悲劇の誕生』『監獄の誕生』")
        data = measure([{"fragment_id": "TEST-NAT-002", "text": text}])
        self.assertEqual(data["group_totals"]["誕生・出産（産む・生まれる）"], {})
        self.assertEqual(data["inside_quotes"], {"誕生": 2})

    def test_negated_upbringing_still_counts_as_named_form_with_context(self):
        data = measure(
            [{"fragment_id": "TEST-NAT-003", "text": "節約の原理として立つ父は、子を育てない。孤児を黙らせない。"}]
        )
        self.assertEqual(
            data["group_totals"]["養育・親子・世代（育てる・継ぐ）"],
            {"育て": 1, "孤児": 1},
        )
        self.assertIn("育て", data["rows"][0]["contexts"])

    def test_actual_birth_infancy_upbringing_and_learning_are_counted(self):
        data = measure(
            [
                {
                    "fragment_id": "TEST-NAT-004",
                    "text": "出産を終えた産屋で赤ん坊が産声を上げ、母親に育てられた幼児はやがて学校で文字を学ぶ。",
                }
            ]
        )
        self.assertEqual(
            data["group_totals"]["誕生・出産（産む・生まれる）"],
            {"出産": 1, "産屋": 1, "産声": 1},
        )
        self.assertEqual(
            data["group_totals"]["乳幼児・幼少（幼さ・片言）"],
            {"赤ん坊": 1, "幼児": 1},
        )
        self.assertEqual(
            data["group_totals"]["養育・親子・世代（育てる・継ぐ）"],
            {"母親": 1, "育て": 1},
        )
        self.assertEqual(
            data["group_totals"]["教育・学習（教える・学ぶ）"],
            {"学校": 1, "学ぶ": 1},
        )

    def test_polysemy_breakdown_never_goes_negative(self):
        breakdown = classify_polysemy(["文学と哲学、椅子と拍子、生産と産物、親愛と親切。"])
        for values in breakdown.values():
            self.assertGreaterEqual(values["remaining_natality_candidate"], 0)


if __name__ == "__main__":
    unittest.main()
