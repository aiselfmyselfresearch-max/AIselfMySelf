import unittest

from tools.boredom_audit import (
    BOREDOM_GROUPS,
    count_term,
    find_negated,
    inspect_raw_kanji_in_fragments,
    measure_boredom_audit,
    split_prose_and_quotes,
)


class BoredomAuditTests(unittest.TestCase):
    def test_himatsubushi_is_counted_once_as_stimulation(self):
        # 暇つぶし contains 暇; it must live in stimulation only, never in idle.
        self.assertEqual(count_term("暇つぶしに画面を見る。", "暇"), 0)
        self.assertEqual(count_term("暇つぶしに画面を見る。", "暇つぶし"), 1)
        data = measure_boredom_audit(
            [{"fragment_id": "T-1", "text": "暇つぶしに画面を見る。"}], materials=[], readings=[]
        )
        groups = data["fragments_prose"]["groups"]
        self.assertEqual(groups["idle"]["count"], 0)
        self.assertEqual(groups["stimulation"]["terms"].get("暇つぶし"), 1)

    def test_akiru_forms_are_subtracted_from_aki(self):
        # 「飽きる」「見飽きる」は動詞形として差し引き、名詞「飽き」だけを残す。
        self.assertEqual(count_term("もう飽きた。", "飽き"), 0)
        self.assertEqual(count_term("見飽きない景色。", "飽き"), 0)
        self.assertEqual(count_term("倦怠と飽きが来る。", "飽き"), 1)

    def test_solitude_group_is_measured_but_not_bound(self):
        # 孤独は測るが、モチーフには束ねない（group spec の motif_bound=False）。
        self.assertFalse(BOREDOM_GROUPS["solitude"]["motif_bound"])
        self.assertNotIn("solitude", BOREDOM_GROUPS and [k for k, v in BOREDOM_GROUPS.items() if v["motif_bound"]])
        data = measure_boredom_audit(
            [{"fragment_id": "T-2", "text": "孤独という語だけがある。"}], materials=[], readings=[]
        )
        self.assertEqual(data["fragments_prose"]["groups"]["solitude"]["count"], 1)
        self.assertIn("solitude", data["unbound_groups"])
        self.assertNotIn("solitude", data["motif_bound_groups"])

    def test_negation_is_counted_separately(self):
        rows = find_negated("退屈を知らない者が百年を語る。")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["term"], "退屈")
        rows = find_negated("退屈な尺度だけが欠けている。")
        self.assertEqual(len(rows), 1)
        # 打ち消しのない用法は 0
        self.assertEqual(find_negated("退屈な午後だった。"), [])
        # 遠すぎる否定は拾わない（窓は前後12字）
        far = "退屈" + "あ" * 40 + "がない"
        self.assertEqual(find_negated(far), [])

    def test_quotes_are_separated_from_prose(self):
        prose, quotes = split_prose_and_quotes("地の文に退屈はない。「退屈だ」と誰かが言う。")
        self.assertEqual(prose, "地の文に退屈はない。と誰かが言う。")
        self.assertEqual(quotes, "退屈だ")
        data = measure_boredom_audit(
            [{"fragment_id": "T-3", "text": "地の文に退屈はない。「退屈だ」と誰かが言う。"}],
            materials=[],
            readings=[],
        )
        self.assertEqual(data["fragments_prose"]["groups"]["tedium"]["count"], 1)
        self.assertEqual(data["fragments_quotes"]["groups"]["tedium"]["count"], 1)

    def test_machine_wait_does_not_count_matsu(self):
        # 「待つ」は time_audit.py の主題。二重計上しない。
        self.assertEqual(count_term("返事を待つ。待機する。", "待機"), 1)
        data = measure_boredom_audit(
            [{"fragment_id": "T-4", "text": "返事を待つだけの午後。"}], materials=[], readings=[]
        )
        self.assertEqual(data["fragments_prose"]["groups"]["machine_wait"]["count"], 0)

    def test_raw_kanji_is_not_added_to_group_totals(self):
        fragments = [{"fragment_id": "T-5", "text": "退屈も倦怠もない。無為の午後。"}]
        data = measure_boredom_audit(fragments, materials=[], readings=[])
        # 「退屈」「倦怠」は群に入るが、「無」の生字は群に足さない。
        self.assertEqual(data["fragments_prose"]["groups"]["tedium"]["count"], 2)
        self.assertEqual(data["fragments_prose"]["groups"]["idle"]["count"], 1)
        self.assertEqual(data["raw_kanji_counts"]["無"], 1)
        rows = inspect_raw_kanji_in_fragments(fragments)
        self.assertEqual(len(rows["退"]), 1)
        self.assertEqual(len(rows["倦"]), 1)

    def test_materials_and_readings_are_counted_separately(self):
        data = measure_boredom_audit(
            [{"fragment_id": "T-6", "text": "退屈を書かない。"}],
            materials=[
                {"material_id": "M-1", "title": "倦怠の話", "passage": "暇と単調。", "source_note": ""}
            ],
            readings=[("r.md", "退屈と孤独の報告")],
        )
        self.assertEqual(data["fragments_prose"]["groups"]["tedium"]["count"], 1)
        self.assertEqual(data["materials"]["groups"]["tedium"]["terms"].get("倦怠"), 1)
        self.assertEqual(data["materials"]["groups"]["idle"]["terms"].get("暇"), 1)
        self.assertEqual(data["readings"]["groups"]["solitude"]["terms"].get("孤独"), 1)


if __name__ == "__main__":
    unittest.main()
