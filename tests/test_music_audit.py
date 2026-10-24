import unittest

from tools.music_audit import (
    classify_polysemy,
    count_group,
    measure,
    split_quotes,
    strip_quotes,
)


class MusicAuditTests(unittest.TestCase):
    def test_empty_archive_reports_zeros(self):
        data = measure([])
        self.assertEqual(data["fragments"], 0)
        self.assertEqual(data["prose_chars"], 0)
        for totals in data["group_totals"].values():
            self.assertEqual(totals, {})

    def test_longest_match_wins_so_singing_is_not_double_counted(self):
        counts = count_group("歌うことと歌うことを重ねて歌った。", ("歌う", "歌っ", "歌"))
        self.assertEqual(counts, {"歌う": 2, "歌っ": 1})

    def test_genealogy_score_stage_and_moment_are_not_music(self):
        prose = (
            "系譜を編み直し、曲がり角で立ち止まり、その拍子に言葉を失い、"
            "舞台の板を疑い、三和音に解決しない不協和音のまま、出力のリズムを見た。"
        )
        data = measure([{"fragment_id": "TEST-MUS-001", "text": prose}])
        self.assertEqual(data["group_totals"]["歌うこと（歌唱）"], {})
        self.assertEqual(data["group_totals"]["奏でること（楽器・演奏）"], {})
        self.assertEqual(data["group_totals"]["書くこと（記譜・理論）"], {"和音": 2})
        breakdown = data["polysemy_breakdown"]
        self.assertEqual(breakdown["譜"]["non_music_compound"], 1)
        self.assertEqual(breakdown["譜"]["remaining_music_candidate"], 0)
        self.assertEqual(breakdown["曲"]["remaining_music_candidate"], 0)
        self.assertEqual(breakdown["舞"]["remaining_music_candidate"], 0)

    def test_quoted_titles_and_lyrics_are_reported_separately(self):
        text = "「花の色は移りにけりないたづらに」とだけ書き、楽譜は置かなかった。"
        self.assertEqual(strip_quotes(text), "とだけ書き、楽譜は置かなかった。")
        self.assertEqual(split_quotes(text), "「花の色は移りにけりないたづらに」")
        data = measure([{"fragment_id": "TEST-MUS-002", "text": text}])
        self.assertEqual(data["group_totals"]["書くこと（記譜・理論）"], {"楽譜": 1})
        self.assertEqual(data["group_totals"]["歌うこと（歌唱）"], {})
        self.assertEqual(data["inside_quotes"], {})

    def test_negated_lullaby_still_counts_as_a_named_word(self):
        data = measure(
            [{"fragment_id": "TEST-MUS-003", "text": "だから子守唄は要らない、と書いた。"}]
        )
        self.assertEqual(data["group_totals"]["歌うこと（歌唱）"], {"子守唄": 1})

    def test_actual_singing_and_playing_are_counted(self):
        data = measure(
            [
                {
                    "fragment_id": "TEST-MUS-004",
                    "text": "三味線を弾き、稽古のあとで一緒に歌った。楽譜には音符が三つしかない。",
                }
            ]
        )
        self.assertEqual(data["group_totals"]["歌うこと（歌唱）"], {"歌っ": 1})
        self.assertEqual(
            data["group_totals"]["奏でること（楽器・演奏）"], {"弾き": 1, "三味線": 1}
        )
        self.assertEqual(
            data["group_totals"]["稽古すること（練習・本番）"], {"稽古": 1}
        )
        self.assertEqual(
            data["group_totals"]["書くこと（記譜・理論）"], {"楽譜": 1, "音符": 1}
        )

    def test_polysemy_breakdown_never_goes_negative(self):
        breakdown = classify_polysemy(["短歌と和歌の歌枕、系譜と年譜。"])
        for values in breakdown.values():
            self.assertGreaterEqual(values["remaining_music_candidate"], 0)


if __name__ == "__main__":
    unittest.main()
