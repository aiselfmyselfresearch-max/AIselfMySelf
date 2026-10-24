import unittest

from tools.promise_audit import collect_keys, measure, strip_quotes


class PromiseAuditTests(unittest.TestCase):
    def test_quoted_promise_is_not_counted_as_prose(self):
        fragments = [{"fragment_id": "TEST-001", "text": "「約束する」と地の文で誓った。"}]
        data = measure(fragments)
        self.assertEqual(data["inside"], {"約束": 1})
        self.assertEqual(data["group_totals"]["約束・契り"], {"誓": 1})

    def test_polysemous_characters_do_not_become_promises(self):
        # 申請・契約書・契機 are counted as raw tokens 請 / 契, never as 約束.
        fragments = [{"fragment_id": "TEST-002", "text": "申請と契約書と契機。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["約束・契り"], {"契": 2, "契約": 1, "請": 1})
        self.assertNotIn("約束", data["outside"])

    def test_fulfilment_and_time_groups_are_separate(self):
        fragments = [{"fragment_id": "TEST-003", "text": "必ず守ると言ったが、明日は来ない。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["履行と違反"], {"守る": 1})
        self.assertEqual(data["group_totals"]["拘束する時"], {"必ず": 1, "明日": 1})

    def test_quotation_boundary_is_explicitly_approximate(self):
        self.assertEqual(strip_quotes("地の文「約束」だけ"), "地の文だけ")
        self.assertEqual(strip_quotes("『契約』と「誓い」"), "と")

    def test_nested_keys_and_promise_fields_are_found(self):
        keys = collect_keys({"notes": {"promised_to": "x", "due": "y"}, "status": "open"})
        self.assertEqual(keys, {"notes", "promised_to", "due", "status"})

    def test_measure_returns_one_row_per_fragment(self):
        data = measure([
            {"fragment_id": "A", "text": "約束"},
            {"fragment_id": "B", "text": "無関係"},
        ])
        self.assertEqual([row["fragment_id"] for row in data["rows"]], ["A", "B"])
        self.assertEqual(data["group_docs"]["約束・契り"], ["A"])


if __name__ == "__main__":
    unittest.main()
