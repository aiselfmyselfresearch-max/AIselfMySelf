"""The two meanings of the 「裏切り」 heading must not be conflated in the count.

ERR-023: the heading first meant "the point where the material refuses my
reading" (a refutation).  From 2026-10-25 it is also used for "the range this
material does not vouch for" (a scope note).  The tool keeps the two forms and
the two counting methods apart, and says so in the printed note.
"""

import unittest

from tools.pledge_audit import (
    HEADING_LEGACY,
    HEADING_LINE_RE,
    HEADING_NEW,
    HEADING_NOTE,
    measure_reports,
)


class PledgeHeadingTests(unittest.TestCase):
    def test_heading_line_re_matches_both_forms(self):
        self.assertTrue(HEADING_LINE_RE.match("- **裏切り**：小説であり、ロシア社会論として要約しない。"))
        self.assertTrue(HEADING_LINE_RE.match("  - **この資料が裏切るもの**: 通念を裏切る。"))
        self.assertTrue(HEADING_LINE_RE.match("- **裏切り**:半角コロンも許す。"))
        # 見出しの形をしていない強調は、行頭見出しとしては数えない。
        self.assertIsNone(HEADING_LINE_RE.match("本文の途中で**裏切り**を強調する。"))

    def test_heading_strings_do_not_overlap(self):
        # 旧型の文字列は新型を含まない。だから二つの count は二重計上しない。
        self.assertNotIn(HEADING_NEW, HEADING_LEGACY)
        self.assertNotIn("裏切り", HEADING_LEGACY)

    def test_report_counts_heading_lines_and_bold_mentions_apart(self):
        reports = measure_reports()
        self.assertEqual(
            reports["uragiri_headings"],
            reports["uragiri_headings_legacy"] + reports["uragiri_headings_new"],
        )
        self.assertEqual(
            reports["uragiri_lines_total"],
            reports["uragiri_lines_legacy"] + reports["uragiri_lines_new"],
        )
        # 行頭の見出しは、太字の言及より少ない（強調だけの箇所がある）。
        self.assertLessEqual(reports["uragiri_lines_total"], reports["uragiri_headings"])
        self.assertGreater(reports["uragiri_lines_total"], 0)
        # 旧型は 2026-10-24 の一連の報告にだけ現れる。
        self.assertGreater(reports["uragiri_lines_legacy"], 0)

    def test_note_says_the_total_is_not_a_count_of_refutations(self):
        self.assertIn("保証しない範囲", HEADING_NOTE)
        self.assertIn("ERR-023", HEADING_NOTE)


if __name__ == "__main__":
    unittest.main()
