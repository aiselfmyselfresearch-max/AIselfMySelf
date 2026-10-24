import tempfile
import unittest
from pathlib import Path

from tools.hearsay_audit import (
    measure,
    measure_materials,
    measure_readings,
    split_quotes,
    strip_quotes,
)


class HearsayAuditTests(unittest.TestCase):
    def test_hearsay_and_inference_are_separate_groups(self):
        fragments = [{"fragment_id": "TEST-HEAR-001", "text": "噂によれば雨だそうだ。たぶん晴れるだろう。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["伝聞の標識"], {"噂": 1, "によれば": 1, "だそう": 1})
        self.assertEqual(data["group_totals"]["推量（伝聞ではない）"], {"だろう": 1})
        self.assertEqual(data["group_totals"]["証言・証拠"], {})

    def test_quoted_hearsay_is_not_prose(self):
        self.assertEqual(strip_quotes("「誰かから聞いた」と書かれていた。"), "と書かれていた。")
        self.assertEqual(split_quotes("「誰かから聞いた」と書かれていた。"), "「誰かから聞いた」")
        fragments = [{"fragment_id": "TEST-HEAR-002", "text": "「噂を聞いた」とだけ記録にあった。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["伝聞の標識"], {})
        self.assertEqual(data["inside_quotes"]["噂"], 1)
        self.assertEqual(data["inside_quotes"]["聞いた"], 1)

    def test_polysemous_character_is_reported_but_not_counted(self):
        fragments = [{"fragment_id": "TEST-HEAR-003", "text": "新聞の聞き手は証文を見た。"}]
        data = measure(fragments)
        # 聞く/聞いた are not present; the bare character is only a reference value.
        self.assertEqual(data["group_totals"]["伝聞の標識"], {})
        self.assertEqual(data["raw_totals"], {"聞": 2, "証": 1})

    def test_summary_marker_is_counted_but_quotes_are_not(self):
        materials = [
            {"material_id": "M-1", "kind": "literary_text", "passage": "【編者による要約】要約の文。"},
            {"material_id": "M-2", "kind": "literary_text", "passage": "「原文の引用」だけ。"},
            {"material_id": "M-3", "kind": "research_excerpt", "passage": "【編者による要約】研究の要約。"},
        ]
        data = measure_materials(materials)
        self.assertEqual(data["summary_passages"], 2)
        self.assertEqual(data["quote_passages"], 1)
        self.assertEqual(data["summary_by_kind"], {"literary_text": 1, "research_excerpt": 1})

    def test_readings_count_only_section_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.md").write_text(
                "## 1\n- **一節（編者による要約）**：要約\n- **解釈**：これは数えない\n"
                "- **一節**：「引用」\n",
                encoding="utf-8",
            )
            data = measure_readings(folder)
        self.assertEqual(data["sections"], 2)
        self.assertEqual(data["summary_sections"], 1)
        self.assertEqual(data["quoted_sections"], 1)

    def test_zero_means_absent_word_form(self):
        fragments = [{"fragment_id": "TEST-HEAR-004", "text": "書いて、読んで、残った。"}]
        data = measure(fragments)
        self.assertEqual(data["group_totals"]["伝聞の標識"], {})
        self.assertEqual(sum(data["group_totals"]["対照（書庫の常用語）"].values()), 3)


if __name__ == "__main__":
    unittest.main()
