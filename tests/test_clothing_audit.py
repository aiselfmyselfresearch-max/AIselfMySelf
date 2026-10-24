import unittest

from tools.clothing_audit import (
    classify_polysemy,
    count_group,
    measure,
    split_quotes,
    strip_quotes,
)


class ClothingAuditTests(unittest.TestCase):
    def test_empty_archive_reports_zeros(self):
        data = measure([])
        self.assertEqual(data["fragments"], 0)
        self.assertEqual(data["prose_chars"], 0)
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})

    def test_longest_match_wins_so_dressing_is_not_double_counted(self):
        counts = count_group("着物を着て、着替えた。", ("着物", "着て", "着替え", "着替", "着"))
        self.assertEqual(counts, {"着物": 1, "着て": 1, "着替え": 1})

    def test_distribution_and_obedience_are_not_clothing(self):
        prose = (
            "会話の分布を測り、流布した噂を布置し直し、規範への服従を征服として読み、"
            "装置の装着を記録した。"
        )
        data = measure([{"fragment_id": "TEST-CLO-001", "text": prose}])
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})
        breakdown = data["polysemy_breakdown"]
        self.assertEqual(breakdown["布"]["non_clothing_compound"], 3)
        self.assertEqual(breakdown["布"]["remaining_clothing_candidate"], 0)
        self.assertEqual(breakdown["服"]["non_clothing_compound"], 2)
        self.assertEqual(breakdown["服"]["remaining_clothing_candidate"], 0)
        self.assertEqual(breakdown["装"]["non_clothing_compound"], 2)

    def test_a_worn_garment_is_counted(self):
        prose = "外套の襟を立て、袖に糸を通し、綻びを繕って洗濯物の籠へ置いた。"
        data = measure([{"fragment_id": "TEST-CLO-002", "text": prose}])
        self.assertEqual(data["group_totals"]["着ること・身につける"], {"外套": 1, "襟": 1, "袖": 1})
        self.assertEqual(
            data["group_totals"]["布・糸・素材"],
            {"糸": 1},
        )
        self.assertEqual(
            data["group_totals"]["洗う・繕う・捨てる"],
            {"綻": 1, "繕": 1, "洗濯物": 1},
        )

    def test_quoted_garment_title_is_reported_separately(self):
        text = "「着物」という題だけを書き、本文には何も出さなかった。"
        data = measure([{"fragment_id": "TEST-CLO-003", "text": text}])
        self.assertEqual(data["group_totals"]["着ること・身につける"], {})
        self.assertEqual(data["inside_quotes"], {"着物": 1})
        # 引用の外に衣の語は無いので、題名だけが数えられる。
        self.assertEqual(strip_quotes(text).count("着物"), 0)
        self.assertEqual(split_quotes(text), "着物")

    def test_feigning_and_adorning_share_one_character(self):
        breakdown = classify_polysemy(["顔を装い始める。装いを凝らす。"])
        self.assertEqual(breakdown["装"]["total"], 2)
        self.assertEqual(breakdown["装"]["remaining_clothing_candidate"], 2)
        self.assertIn("偽る", breakdown["装"]["note"])

    def test_contexts_are_kept_for_manual_inspection(self):
        prose = "背表紙の糸が緩んだ帳面を、麻糸で一針だけ縫った。"
        data = measure([{"fragment_id": "TEST-CLO-004", "text": prose}])
        row = data["rows"][0]
        self.assertIn("contexts", row)
        self.assertTrue(any("麻糸" in ctx for ctx in row["contexts"]["糸"]))


if __name__ == "__main__":
    unittest.main()
