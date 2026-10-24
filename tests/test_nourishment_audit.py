import unittest

from tools.nourishment_audit import measure, strip_quotes


class NourishmentAuditTests(unittest.TestCase):
    def test_polysemous_characters_do_not_become_food(self):
        fragments = [{
            "fragment_id": "TEST-001",
            "text": "意味が食い違い、気に食わない。油皿の筋肉と比喩の魚。",
        }]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["食事の動作"], {})
        self.assertEqual(data["group_totals"]["食物・調理"], {})
        self.assertEqual(data["group_totals"]["味わい"], {})
        self.assertEqual(data["raw_totals"], {"食": 2, "味": 1, "皿": 1, "肉": 1, "魚": 1})

    def test_literal_food_and_non_food_fuel_are_separate(self):
        fragments = [{
            "fragment_id": "TEST-002",
            "text": "空腹のまま粥を食べた。問いは燃料になる。紙は酸っぱい。",
        }]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["食事の動作"], {"食べた": 1})
        self.assertEqual(data["group_totals"]["飢えと栄養"], {"空腹": 1})
        self.assertEqual(data["group_totals"]["食物・調理"], {"粥": 1})
        self.assertEqual(data["group_totals"]["取り込み・消費"], {"燃料": 1})
        self.assertEqual(data["group_totals"]["味わい"], {"酸っぱい": 1})

    def test_quotation_boundary_is_explicitly_approximate(self):
        self.assertEqual(strip_quotes("地の文「粥を食べた」だけ"), "地の文だけ")
        fragments = [{"fragment_id": "TEST-003", "text": "「粥を食べた」地の文"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["食事の動作"], {})
        self.assertEqual(data["inside_quotes"], {"食べた": 1, "粥": 1})


if __name__ == "__main__":
    unittest.main()
