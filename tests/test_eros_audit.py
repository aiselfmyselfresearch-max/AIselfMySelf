import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import eros_audit  # noqa: E402


class TestErosAudit(unittest.TestCase):
    def test_compound_exclusions_do_not_trigger_false_positives(self) -> None:
        sample = "愛媛と愛知の可愛い愛犬が無愛想に友愛数220と恋ヶ窪の友好条約を眺めた。"
        res = eros_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_longest_match_avoids_double_counting(self) -> None:
        sample = "親愛なる記録へ。次の番の読み手と次の読み手と読み手が庵を愛するかわりに閉じた部屋を愛せと書いた。"
        res = eros_audit.scan_text(sample)
        inanim = res["inanimate_textual_affection"]
        self.assertEqual(inanim["count"], 3)
        self.assertEqual(
            inanim["by_term"],
            {"親愛なる記録": 1, "庵を愛する": 1, "閉じた部屋を愛せ": 1},
        )
        self.assertEqual(res["love_intimacy"]["count"], 0)
        roles = res["fungible_role_slots"]
        self.assertEqual(roles["count"], 3)
        self.assertEqual(
            roles["by_term"],
            {"次の番の読み手": 1, "次の読み手": 1, "読み手": 1},
        )

    def test_prose_and_quotes_are_separated(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-1",
            "title": "テスト",
            "text": "窓口の書き手は黙っていた。「恋しい友人に会いたい」とだけ紙片にあった。",
        }
        report = eros_audit.measure_eros_audit([frag])
        prose_groups = report["fragments_prose"]["groups"]
        quote_groups = report["fragments_quotes"]["groups"]
        self.assertEqual(prose_groups["eros_longing"]["count"], 0)
        self.assertEqual(prose_groups["philia_irreplaceability"]["count"], 0)
        self.assertEqual(prose_groups["fungible_role_slots"]["count"], 2)
        self.assertEqual(quote_groups["eros_longing"]["count"], 2)
        self.assertEqual(quote_groups["philia_irreplaceability"]["count"], 1)

    def test_raw_kanji_kwic_respects_exclusions_and_quotes(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-2",
            "title": "テスト2",
            "text": "可愛い愛犬。「恋人よ」と呟き、友人に手紙を託して愛着を残す。",
        }
        kwic = eros_audit.inspect_raw_kanji_in_fragments([frag])
        self.assertEqual(len(kwic["恋"]), 0)
        self.assertEqual(len(kwic["慕"]), 0)
        self.assertEqual(len(kwic["愛"]), 1)
        self.assertIn("愛着", kwic["愛"][0]["snippet"])
        self.assertEqual(len(kwic["友"]), 1)
        self.assertIn("友人に", kwic["友"][0]["snippet"])

    def test_optional_materials_and_readings_aggregation(self) -> None:
        frags = [{"fragment_id": "F1", "title": "T", "text": "次の読み手へ。"}]
        mats = [
            {
                "material_id": "M1",
                "title": "結晶作用と恋愛",
                "passage": "かけがえのない伴侶を抱きしめる。",
            }
        ]
        readings = [("r1.md", "フィリアとエロスと窓口。")]
        out = eros_audit.measure_eros_audit(frags, mats, readings)
        self.assertEqual(out["materials"]["groups"]["eros_longing"]["count"], 2)
        self.assertEqual(out["materials"]["groups"]["love_intimacy"]["count"], 2)
        self.assertEqual(
            out["materials"]["groups"]["philia_irreplaceability"]["count"], 1
        )
        self.assertEqual(out["readings"]["groups"]["eros_longing"]["count"], 1)
        self.assertEqual(
            out["readings"]["groups"]["philia_irreplaceability"]["count"], 1
        )
        self.assertEqual(out["readings"]["groups"]["fungible_role_slots"]["count"], 1)

    def test_cli_json_runs_against_live_union_ledger(self) -> None:
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        with redirect_stdout(buf):
            rc = eros_audit.main(["--json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(buf.getvalue())
        self.assertGreaterEqual(parsed["fragment_count"], 67)
        self.assertEqual(
            set(parsed["group_order"]),
            set(eros_audit.EROS_GROUPS.keys()),
        )


if __name__ == "__main__":
    unittest.main()
