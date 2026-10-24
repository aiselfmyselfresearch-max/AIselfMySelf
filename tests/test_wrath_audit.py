#!/usr/bin/env python3
"""Unit tests for tools/wrath_audit.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import wrath_audit  # noqa: E402


class WrathAuditTests(unittest.TestCase):
    def test_quote_stripping_and_maximal_munch(self) -> None:
        items = [
            (
                "F-1",
                "『罪と罰』と「怒りの葡萄」を棚に置く。追記しか許されない台帳では、誰も激怒せず、誰にも謝罪しない。",
            )
        ]
        res = wrath_audit.measure_items(items, "synthetic", is_fragments=True)
        self.assertEqual(
            res["group_totals"]["怒り・憤り・怨恨（怒る・憎む）"],
            {"激怒": 1},
        )
        # 『罪と罰』 and 「怒りの葡萄」 are inside quotes, not narrator prose
        self.assertEqual(res["group_totals"]["罪・罰・裁き（審判・処罰）"], {})
        self.assertEqual(res["inside_quotes"], {"怒り": 1})
        # 許されない is counted once in group 5 and never as 許す
        self.assertEqual(
            res["group_totals"]["対照：制度的禁止・規則（許されない・禁じる）"],
            {"許されない": 1},
        )
        self.assertEqual(
            res["group_totals"]["謝罪・弁明・赦し（詫びる・赦す）"],
            {"謝罪": 1},
        )

    def test_polysemy_subtracts_non_target_compounds(self) -> None:
        prose = "感謝と新陳代謝の記録を断裁し、体裁の許可を得るが、人を許すことも謝ることもない。"
        poly = wrath_audit.analyze_polysemy(prose)
        # 謝: 感謝(1) + 新陳代謝(1) subtracted, 謝る(1) remains
        self.assertEqual(poly["謝"]["total"], 3)
        self.assertEqual(poly["謝"]["non_target_compound"], 2)
        self.assertEqual(poly["謝"]["remaining_candidate"], 1)
        # 裁: 断裁(1) + 体裁(1) subtracted, 0 remains
        self.assertEqual(poly["裁"]["total"], 2)
        self.assertEqual(poly["裁"]["non_target_compound"], 2)
        self.assertEqual(poly["裁"]["remaining_candidate"], 0)
        # 許: 許可(1) subtracted, 許す(1) remains
        self.assertEqual(poly["許"]["total"], 2)
        self.assertEqual(poly["許"]["non_target_compound"], 1)
        self.assertEqual(poly["許"]["remaining_candidate"], 1)

    def test_cli_runs_on_live_ledger(self) -> None:
        self.assertEqual(wrath_audit.main(["--base-only"]), 0)
        self.assertEqual(wrath_audit.main([]), 0)


if __name__ == "__main__":
    unittest.main()
