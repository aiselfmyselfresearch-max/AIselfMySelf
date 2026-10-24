import unittest

from tools.face_audit import measure, strip_quotes, count_corpus_terms


class FaceAuditTests(unittest.TestCase):
    def test_polysemous_characters_do_not_become_faces(self):
        fragments = [{
            "fragment_id": "TEST-001",
            "text": "局面の面前で目的を見失い、冷笑した面積の目次。",
        }]
        data = measure(fragments)
        for group in ("顔と面貌", "表情と微笑", "まなざしと視線", "身元と認証"):
            self.assertEqual(data["group_totals"][group], {})
        self.assertEqual(data["raw_totals"]["面"], 3)
        self.assertEqual(data["raw_totals"]["目"], 2)
        self.assertEqual(data["raw_totals"]["笑"], 1)

    def test_literal_face_words_are_counted_per_group(self):
        fragments = [{
            "fragment_id": "TEST-002",
            "text": "表情のない顔を仮面で覆い、視線をそらした。肖像写真の顔認証。",
        }]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["顔と面貌"].get("顔"), 2)
        self.assertEqual(data["group_totals"]["表情と微笑"].get("表情"), 1)
        self.assertEqual(data["group_totals"]["仮面と覆い"].get("仮面"), 1)
        self.assertEqual(data["group_totals"]["まなざしと視線"].get("視線"), 1)
        self.assertEqual(data["group_totals"]["身元と認証"].get("顔認証"), 1)

    def test_quoted_speech_is_separated(self):
        fragments = [{
            "fragment_id": "TEST-003",
            "text": "地の文には表情と書かない。「表情がある」とだけ受信文が言う。",
        }]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["表情と微笑"].get("表情"), 1)
        self.assertEqual(data["inside_chars"] > 0, True)

    def test_strip_quotes_keeps_outside_only(self):
        outside, inside = strip_quotes("外側「内側」外側")
        self.assertEqual(outside, "外側外側")
        self.assertEqual(inside, "内側")

    def test_count_corpus_terms_is_plain_occurrence(self):
        counts = count_corpus_terms(("顔", "仮面"), ["顔と仮面、顔。", "別の顔"])
        self.assertEqual(counts, {"顔": 3, "仮面": 1})


if __name__ == "__main__":
    unittest.main()
