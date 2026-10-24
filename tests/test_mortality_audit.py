import unittest

from tools.mortality_audit import measure, split_quotes, strip_quotes


class MortalityAuditTests(unittest.TestCase):
    def test_grave_and_funeral_are_counted(self):
        fragments = [{"fragment_id": "TEST-DEATH-001", "text": "墓に花を置き、葬式のあとで弔辞を読んだ。"}]
        data = measure(fragments)
        # 墓 and 墓参-style compounds overlap; the tool counts tokens, not passages.
        self.assertEqual(data["group_totals"]["遺体・埋葬"]["墓"], 1)
        self.assertEqual(data["group_totals"]["遺体・埋葬"]["葬式"], 1)
        self.assertEqual(data["group_totals"]["遺体・埋葬"]["弔辞"], 1)
        self.assertEqual(data["group_docs"]["遺体・埋葬"], ["TEST-DEATH-001"])

    def test_polysemous_wan_is_not_a_death(self):
        fragments = [{"fragment_id": "TEST-DEATH-002", "text": "言葉が亡び、記録は亡失し、彼は亡命した。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["死の告知・臨終"], {})
        self.assertEqual(data["raw_totals"], {"亡": 3})

    def test_loss_is_not_bereavement(self):
        fragments = [{"fragment_id": "TEST-DEATH-003", "text": "文脈の喪失と、記憶の喪失。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["喪・悲嘆"], {})
        self.assertEqual(data["raw_totals"], {"喪": 2})

    def test_quoted_epitaph_is_reported_separately(self):
        self.assertEqual(strip_quotes("「ここに眠る」と墓標にあった。"), "と墓標にあった。")
        self.assertEqual(split_quotes("「ここに眠る」と墓標にあった。"), "「ここに眠る」")
        fragments = [{"fragment_id": "TEST-DEATH-004", "text": "「墓碑銘は消えた」とだけ記録にあった。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["遺体・埋葬"], {})
        self.assertEqual(data["inside_quotes"], {"墓": 1, "墓碑": 1})

    def test_sleep_is_a_contrast_not_a_death(self):
        fragments = [{"fragment_id": "TEST-DEATH-005", "text": "眠り、夢を見て、目覚めた。"}]
        data = measure(fragments)
        self.assertEqual(data["raw_totals"], {"眠": 1})
        self.assertEqual(data["group_totals"]["生きる（対照）"], {})

    def test_empty_archive_reports_zeros_without_error(self):
        data = measure([])
        self.assertEqual(data["records"], 0)
        self.assertEqual(data["group_totals"]["遺す・継ぐ"], {})
        self.assertEqual(data["prose_chars"], 0)


if __name__ == "__main__":
    unittest.main()
