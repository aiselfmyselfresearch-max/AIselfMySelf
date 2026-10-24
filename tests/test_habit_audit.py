import unittest

from tools.habit_audit import measure_texts, strip_quotes


class HabitAuditTests(unittest.TestCase):
    def test_quoted_habit_word_is_not_counted_as_prose(self):
        items = [("TEST-001", "「習慣」と書かれた地の文の癖。")]
        data = measure_texts(items, "test")
        self.assertEqual(data["groups"]["習慣・慣れ"]["total"], 1)  # 引用内の「習慣」は数えず、地の文の癖のみ
        self.assertNotIn("習慣", data["groups"]["習慣・慣れ"]["tokens"])
        self.assertIn("癖", data["groups"]["習慣・慣れ"]["tokens"])

    def test_polysemous_characters_stay_out_of_groups(self):
        # 学習・典型・鍛練 are raw tokens (習/型/練), never silently folded in.
        items = [("TEST-002", "学習と典型と鍛練。")]
        data = measure_texts(items, "test")
        self.assertEqual(data["groups"]["稽古・練習・修行"]["total"], 0)
        self.assertEqual(data["raw"], {"習": 1, "型": 1, "練": 1})

    def test_absence_is_form_absence_not_theme_absence(self):
        items = [("TEST-003", "稽古も練習も日課も、ここには書いていない。")]
        data = measure_texts(items, "test")
        self.assertGreater(data["groups"]["稽古・練習・修行"]["total"], 0)
        items2 = [("TEST-004", "ただ続けている。")]
        data2 = measure_texts(items2, "test")
        self.assertEqual(data2["groups"]["稽古・練習・修行"]["total"], 0)
        self.assertEqual(data2["groups"]["稽古・練習・修行"]["docs"], 0)

    def test_continuity_formulas_are_counted_apart(self):
        items = [("TEST-005", "次のセッションに引き継ぎ、続きを書く。")]
        data = measure_texts(items, "test")
        self.assertEqual(data["continuity"], {"次の": 1, "次のセッション": 1, "引き継": 1, "続き": 1})

    def test_quote_stripping_is_non_nested(self):
        self.assertEqual(strip_quotes("地の文「習慣」だけ"), "地の文だけ")
        self.assertEqual(strip_quotes("『稽古』と「練習」"), "と")


if __name__ == "__main__":
    unittest.main()
