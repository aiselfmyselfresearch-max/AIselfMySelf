#!/usr/bin/env python3
"""Unit tests for tools/fire_audit.py（第31の鏡）。"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fire_audit  # noqa: E402


class FireAuditTests(unittest.TestCase):
    def test_maximal_munch_and_groups(self) -> None:
        got = fire_audit.count_terms("書庫が燃えて、灰だけが残った。")
        self.assertEqual(got, {"fire": 1, "ash": 1, "hearth": 0, "tool": 0})
        # 灰燼と灰は最長一致で別々に1回ずつ
        got2 = fire_audit.count_terms("灰燼と灰")
        self.assertEqual(got2["ash"], 2)
        # 「火事」は「火」と二重に数えない（最長一致）
        self.assertEqual(fire_audit.count_terms("火事")["fire"], 1)

    def test_non_target_compounds_are_subtracted(self) -> None:
        # 火曜日・灰色・火山・火星・炎症・焼酎・焦燥・マッチングは火の語ではない
        got = fire_audit.count_terms("火曜日の灰色の空に、火山の火星が光る。")
        self.assertEqual(sum(got.values()), 0)
        got2 = fire_audit.count_terms("炎症と焼酎と焦燥とマッチングの記録。")
        self.assertEqual(sum(got2.values()), 0)
        # 差し引きは位置を保つ: 「石灰」を潰しても隣の「灰」は数える
        self.assertEqual(fire_audit.count_terms("石灰と灰")["ash"], 1)

    def test_hearth_and_tools(self) -> None:
        got = fire_audit.count_terms("囲炉裏の熾に薪をくべ、蝋燭に燐寸で火を移す。")
        self.assertEqual(got["hearth"], 3)  # 囲炉裏・熾・薪
        self.assertEqual(got["tool"], 2)    # 蝋燭・燐寸
        self.assertEqual(got["fire"], 1)    # 火（移す側）

    def test_polysemy_breakdown(self) -> None:
        poly = fire_audit.analyze_polysemy("灰色の灰")
        self.assertEqual(poly["灰"]["total"], 2)
        self.assertEqual(poly["灰"]["non_target_compound"], 1)
        self.assertEqual(poly["灰"]["remaining_candidate"], 1)

    def test_quote_splitting(self) -> None:
        outer, inner = fire_audit._split_quotes("地の文。「台詞の中で燃える」と言う。")
        self.assertNotIn("燃える", outer)
        self.assertIn("燃える", inner)

    def test_cli_runs_on_live_ledger(self) -> None:
        self.assertEqual(fire_audit.main(["--self-test"]), 0)
        self.assertEqual(fire_audit.main([]), 0)


if __name__ == "__main__":
    unittest.main()
