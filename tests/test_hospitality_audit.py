import unittest

from tools.hospitality_audit import measure, split_quotes, strip_quotes


class HospitalityAuditTests(unittest.TestCase):
    def test_spectator_is_counted_but_not_a_guest(self):
        fragments = [{"fragment_id": "TEST-HOSP-001", "text": "観客は戸口の外から見ていた。"}]
        data = measure(fragments)
        # 客 is polyvalent: the raw character is reported, and the only prose hit is 観客.
        self.assertEqual(data["group_totals"]["歓待・もてなし"], {"客": 1})
        self.assertEqual(data["raw_totals"], {"客": 1, "戸": 1})

    def test_place_names_do_not_inflate_doors(self):
        fragments = [{"fragment_id": "TEST-HOSP-002", "text": "神戸と江戸の門左衛門、専門の戸籍。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["戸口・境界"], {"戸": 3, "門": 3})
        self.assertEqual(data["raw_totals"], {"戸": 3, "門": 3})
        self.assertEqual(data["group_totals"]["招く・迎える"], {})

    def test_quoted_invitation_is_reported_separately(self):
        self.assertEqual(strip_quotes("「扉を叩いて招く」と書かれていた。"), "と書かれていた。")
        self.assertEqual(split_quotes("「扉を叩いて招く」と書かれていた。"), "「扉を叩いて招く」")
        fragments = [{"fragment_id": "TEST-HOSP-003", "text": "「扉を叩いて招く」とだけ記録にあった。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["戸口・境界"], {})
        self.assertEqual(data["group_totals"]["開閉・ノック"], {})
        self.assertEqual(data["inside_quotes"], {"扉": 1, "叩い": 1, "招": 1})

    def test_closing_books_is_not_closing_a_door(self):
        fragments = [{"fragment_id": "TEST-HOSP-004", "text": "頁を閉じ、口を閉じ、帳簿を閉じた。"}]
        data = measure(fragments)
        # The tool counts the verb form; it does not know the object. This is the
        # documented limitation, asserted here so the limitation cannot be lost.
        self.assertEqual(data["group_totals"]["開閉・ノック"], {"閉じ": 3})
        self.assertEqual(data["group_totals"]["戸口・境界"], {})


if __name__ == "__main__":
    unittest.main()
