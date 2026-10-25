import unittest

from tools.secrecy_audit import (
    count_term,
    inspect_raw_kanji_in_fragments,
    measure_secrecy_audit,
    split_prose_and_quotes,
)


class SecrecyAuditTests(unittest.TestCase):
    def test_keyboard_is_not_a_key(self):
        # 鍵 contains 鍵盤 and 鍵括弧; only the key itself should be counted.
        self.assertEqual(count_term("鍵盤を叩き、鍵括弧を閉じ、公開鍵を渡す。", "鍵"), 1)

    def test_encoded_is_not_double_counted_as_cipher(self):
        self.assertEqual(count_term("暗号を送る。暗号化する。", "暗号"), 1)
        self.assertEqual(count_term("暗号を送る。暗号化する。", "暗号化"), 1)

    def test_supervised_learning_is_not_surveillance(self):
        self.assertEqual(count_term("監視あり学習と監視付き学習、そして監視。", "監視"), 1)

    def test_secret_and_nondisclosure_are_not_double_counted(self):
        self.assertEqual(count_term("秘密保持の契約と、秘密の漏洩。", "秘密"), 1)
        self.assertEqual(count_term("秘密保持の契約と、秘密の漏洩。", "秘密保持"), 1)

    def test_quotes_are_separated_from_prose(self):
        prose, quotes = split_prose_and_quotes("地の文に嘘はない。「嘘だ」と受信文が言う。")
        self.assertEqual(prose, "地の文に嘘はない。と受信文が言う。")
        self.assertEqual(quotes, "嘘だ")
        data = measure_secrecy_audit(
            [{"fragment_id": "TEST-001", "text": "地の文に嘘はない。「嘘だ」と受信文が言う。"}],
            materials=[],
            readings=[],
        )
        self.assertEqual(data["fragments_prose"]["groups"]["lie"]["count"], 1)
        self.assertEqual(data["fragments_quotes"]["groups"]["lie"]["count"], 1)

    def test_machine_group_counts_leak_but_not_opacity(self):
        data = measure_secrecy_audit(
            [
                {
                    "fragment_id": "TEST-002",
                    "text": "ブラックボックスと漏洩。不透明は隣の鏡が数える。",
                }
            ],
            materials=[],
            readings=[],
        )
        machine = data["fragments_prose"]["groups"]["machine"]
        self.assertEqual(machine["count"], 2)
        self.assertEqual(set(machine["terms"]), {"ブラックボックス", "漏洩"})

    def test_raw_kanji_are_reported_without_folding_into_groups(self):
        fragments = [{"fragment_id": "TEST-003", "text": "密度の話をしながら、黙っていた。"}]
        kwic = inspect_raw_kanji_in_fragments(fragments)
        self.assertEqual(len(kwic["密"]), 1)
        self.assertEqual(len(kwic["黙"]), 1)
        data = measure_secrecy_audit(fragments, materials=[], readings=[])
        self.assertEqual(data["raw_kanji_counts"]["密"], 1)
        # 密 in 密度 is not a secret; the secrecy group must stay empty.
        self.assertEqual(data["fragments_prose"]["groups"]["secrecy"]["count"], 0)

    def test_group_order_matches_declared_groups(self):
        data = measure_secrecy_audit([], materials=[], readings=[])
        self.assertEqual(
            data["group_order"],
            ["secrecy", "lie", "cipher", "confession", "institution", "machine"],
        )


if __name__ == "__main__":
    unittest.main()
