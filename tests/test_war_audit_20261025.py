import unittest

from tools.war_audit_20261025 import count_corpus_terms, count_token, measure, strip_quotes


class WarAuditTests(unittest.TestCase):
    def test_wonderful_is_not_an_enemy(self):
        # 素敵 contains 敵 but is not an enemy; raw counting would invent one.
        self.assertEqual(count_token("素敵な敵意のない、素敵な朝。敵が来た。", "敵"), 1)
        fragments = [{"fragment_id": "TEST-001", "text": "素敵な素敵な日だった。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["敵と同盟"], {})
        self.assertEqual(data["raw_totals"]["敵"], 2)

    def test_nonviolence_is_not_counted_as_violence(self):
        fragments = [{"fragment_id": "TEST-002", "text": "非暴力と平和を選ぶ。暴力は選ばない。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["暴力と殺害"].get("暴力"), 1)
        self.assertEqual(data["group_totals"]["平和と停戦"].get("非暴力"), 1)
        self.assertEqual(data["group_totals"]["平和と停戦"].get("平和"), 1)

    def test_literal_war_words_are_counted_per_group(self):
        fragments = [
            {
                "fragment_id": "TEST-003",
                "text": "戦争の戦場で兵士が武器を置き、停戦ののち平和が来た。自律兵器とドローン。",
            }
        ]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["戦争と戦闘"].get("戦争"), 1)
        self.assertEqual(data["group_totals"]["戦争と戦闘"].get("戦場"), 1)
        self.assertEqual(data["group_totals"]["軍隊と兵器"].get("兵士"), 1)
        self.assertEqual(data["group_totals"]["平和と停戦"].get("停戦"), 1)
        self.assertEqual(data["group_totals"]["機械の戦争"].get("自律兵器"), 1)
        self.assertEqual(data["group_totals"]["機械の戦争"].get("ドローン"), 1)
        # 兵器 inside 自律兵器 must not be double-counted as a plain weapon.
        self.assertNotIn("兵器", data["group_totals"]["軍隊と兵器"])

    def test_quoted_speech_is_separated(self):
        fragments = [
            {
                "fragment_id": "TEST-004",
                "text": "地の文には戦争と書かない。「戦争」とだけ受信文が言う。",
            }
        ]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["戦争と戦闘"].get("戦争"), 1)
        self.assertGreater(data["inside_chars"], 0)

    def test_strip_quotes_keeps_outside_only(self):
        outside, inside = strip_quotes("外側「内側」外側")
        self.assertEqual(outside, "外側外側")
        self.assertEqual(inside, "内側")

    def test_count_corpus_terms_applies_exclusions(self):
        counts = count_corpus_terms(("敵", "平和"), ["素敵な平和、敵と平和。"])
        self.assertEqual(counts, {"敵": 1, "平和": 2})


if __name__ == "__main__":
    unittest.main()
