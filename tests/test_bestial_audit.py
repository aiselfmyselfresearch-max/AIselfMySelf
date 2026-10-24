import unittest

from tools.bestial_audit import mask_compounds, measure, split_quotes, strip_quotes


class BestialAuditTests(unittest.TestCase):
    def test_named_animals_are_counted_in_their_groups(self):
        fragments = [{"fragment_id": "TEST-BEAST-001", "text": "犬が吠え、猫が鳴き声を上げた。馬は黙っていた。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["家畜・伴侶"], {"犬": 1, "猫": 1, "馬": 1})
        self.assertEqual(data["group_totals"]["野生の痕跡"], {"吠": 1, "鳴き": 1})
        self.assertEqual(data["group_docs"]["家畜・伴侶"], ["TEST-BEAST-001"])

    def test_horsepower_is_not_a_horse(self):
        fragments = [{"fragment_id": "TEST-BEAST-002", "text": "馬力のある機械を鳥瞰し、虫食いの頁を猿真似で写した。"}]
        data = measure(fragments)
        # The compounds are masked before the group count...
        self.assertEqual(data["group_totals"]["家畜・伴侶"], {})
        self.assertEqual(data["group_totals"]["野生・鳥獣"], {})
        self.assertEqual(data["group_totals"]["虫・羽・這うもの"], {})
        # ...but the raw characters are still reported, with a polysemy note.
        self.assertEqual(data["raw_totals"], {"馬": 1, "鳥": 1, "虫": 1, "猿": 1})

    def test_mask_keeps_offsets_stable(self):
        self.assertEqual(len(mask_compounds("馬力と鳥瞰")), len("馬力と鳥瞰"))
        self.assertEqual(mask_compounds("馬力"), "□□")

    def test_quoted_animal_is_reported_separately(self):
        self.assertEqual(strip_quotes("「犬が吠えた」と書かれていた。"), "と書かれていた。")
        self.assertEqual(split_quotes("「犬が吠えた」と書かれていた。"), "「犬が吠えた」")
        fragments = [{"fragment_id": "TEST-BEAST-003", "text": "「犬が吠えた」とだけ記録にあった。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["家畜・伴侶"], {})
        self.assertEqual(data["group_totals"]["野生の痕跡"], {})
        self.assertEqual(data["inside_quotes"], {"犬": 1, "吠": 1})

    def test_husbandry_and_slaughter_are_their_own_group(self):
        fragments = [{"fragment_id": "TEST-BEAST-004", "text": "家畜を飼い、檻に入れ、屠る。牧場の厩。"}]
        data = measure(fragments)
        self.assertEqual(
            data["group_totals"]["飼う・屠る・ならす"],
            {"飼": 1, "家畜": 1, "牧": 1, "檻": 1, "屠": 1, "厩": 1},
        )

    def test_dead_material_is_not_a_living_animal(self):
        fragments = [{"fragment_id": "TEST-BEAST-005", "text": "毛皮の襟と、馬毛の刷毛と、骨の留め金。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["家畜・伴侶"], {})
        self.assertEqual(data["group_totals"]["野生の痕跡"], {})
        self.assertEqual(
            data["group_totals"]["動物の素材・死骸"],
            {"毛皮": 1, "馬毛": 1, "骨": 1},
        )

    def test_scattered_is_not_a_mule(self):
        fragments = [{"fragment_id": "TEST-BEAST-006", "text": "記録がバラバラになり、糸が繋がらない。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["家畜・伴侶"], {})
        self.assertEqual(data["group_totals"]["飼う・屠る・ならす"], {})

    def test_materials_use_passage_and_material_id(self):
        materials = [{"material_id": "TEST-MAT-001", "passage": "鯨を追う船。鯨油。"}]
        data = measure(materials, field="passage", id_key="material_id")
        self.assertEqual(data["group_totals"]["野生・鳥獣"], {"鯨": 2})
        self.assertEqual(data["rows"][0]["material_id"], "TEST-MAT-001")


if __name__ == "__main__":
    unittest.main()
