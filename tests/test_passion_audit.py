import unittest

from tools.passion_audit import (
    classify_polysemy,
    count_group,
    count_punctuation,
    measure,
    split_quotes,
    strip_quotes,
)


class PassionAuditTests(unittest.TestCase):
    def test_empty_archive_reports_zeros(self):
        data = measure([])
        self.assertEqual(data["fragments"], 0)
        self.assertEqual(data["prose_chars"], 0)
        self.assertEqual(data["punctuation_prose"], {"。": 0, "？/?": 0, "！/!": 0})
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})

    def test_longest_match_wins_for_shame_and_anger(self):
        counts = count_group(
            "恥じないことと恥じらいと恥の多い書き方を並べ、怒鳴る声と怒りを分けた。",
            ("恥じない", "恥じらい", "恥じ", "恥の", "怒鳴る", "怒り"),
        )
        self.assertEqual(
            counts,
            {"恥じない": 1, "恥じらい": 1, "恥の": 1, "怒鳴る": 1, "怒り": 1},
        )

    def test_quoted_titles_and_exclamations_are_separated_from_prose(self):
        text = "『響きと怒り』を閉じ、「泣くな！」という台詞を書き手は静かに留保した。"
        self.assertEqual(strip_quotes(text), "を閉じ、という台詞を書き手は静かに留保した。")
        self.assertEqual(split_quotes(text), "『響きと怒り』「泣くな！」")
        data = measure([{"fragment_id": "TEST-PAS-001", "text": text}])
        self.assertEqual(data["group_totals"]["怒り・憤怒・怨恨（怒る・恨む）"], {})
        self.assertEqual(data["group_totals"]["泣く・涙・叫び（落涙・嗚咽）"], {})
        self.assertEqual(
            data["group_totals"]["抑制・留保・静けさ（対照）"],
            {"静か": 1, "留保": 1},
        )
        self.assertEqual(data["punctuation_prose"]["！/!"], 0)
        self.assertEqual(data["punctuation_quotes"]["！/!"], 1)
        self.assertEqual(data["inside_quotes"], {"怒り": 1, "泣く": 1})

    def test_non_passion_compounds_are_subtracted_from_raw_counts(self):
        prose = "静止した静物の横で怒濤の波と涙腺の図を眺めた。"
        data = measure([{"fragment_id": "TEST-PAS-002", "text": prose}])
        breakdown = data["polysemy_breakdown"]
        self.assertEqual(breakdown["静"]["remaining_passion_candidate"], 0)
        self.assertEqual(breakdown["怒"]["remaining_passion_candidate"], 0)
        self.assertEqual(breakdown["涙"]["remaining_passion_candidate"], 0)

    def test_hot_passions_and_tears_are_counted_with_context(self):
        prose = "赤面して後悔し、嫉妬と怒りに震えて涙を流しながら泣いた！"
        data = measure([{"fragment_id": "TEST-PAS-003", "text": prose}])
        self.assertEqual(
            data["group_totals"]["怒り・憤怒・怨恨（怒る・恨む）"],
            {"怒り": 1},
        )
        self.assertEqual(
            data["group_totals"]["恥・羞恥・悔恨（赤面・悔いる）"],
            {"赤面": 1, "後悔": 1},
        )
        self.assertEqual(
            data["group_totals"]["嫉妬・羨望・嫌悪（妬む・蔑む）"],
            {"嫉妬": 1},
        )
        self.assertEqual(
            data["group_totals"]["泣く・涙・叫び（落涙・嗚咽）"],
            {"涙": 1, "泣い": 1},
        )
        self.assertEqual(data["punctuation_prose"]["！/!"], 1)
        self.assertIn("赤面", data["rows"][0]["contexts"])

    def test_punctuation_counts_ascii_and_fullwidth(self):
        self.assertEqual(
            count_punctuation("本当か？本当だ！Yes! Really?。"),
            {"。": 1, "？/?": 2, "！/!": 2},
        )

    def test_polysemy_breakdown_never_goes_negative(self):
        breakdown = classify_polysemy(["静止と静脈と怒濤と涙腺。"])
        for values in breakdown.values():
            self.assertGreaterEqual(values["remaining_passion_candidate"], 0)


if __name__ == "__main__":
    unittest.main()
