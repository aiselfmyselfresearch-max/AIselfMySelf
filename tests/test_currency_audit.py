import json
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import currency_audit  # noqa: E402


class TestCurrencyAudit(unittest.TestCase):
    def test_compound_exclusions_do_not_trigger_false_positives(self) -> None:
        sample = (
            "金曜日の金沢で金色の金属と富士山の豊富な円環の観測値・平均値を読売新聞で見た。"
            "フランツ・カフカとアンネ・フランクがフランスでミドルマーチを100パーセント読み、"
            "報酬モデルと報酬予測誤差を計算した。"
        )
        res = currency_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_non_monetary_ledger_vs_monetary_terms(self) -> None:
        sample = "台帳の留め金と掛け金を外し、金石の数値と評価を記すが、硬貨も賃金も値札もない。"
        res = currency_audit.scan_text(sample)
        self.assertEqual(
            res["non_monetary_ledger_idioms"]["by_term"],
            {"台帳": 1, "留め金": 1, "掛け金": 1, "金石": 1, "数値": 1, "評価": 1},
        )
        self.assertEqual(res["currency_price_market"]["by_term"], {"硬貨": 1, "値札": 1})
        self.assertEqual(res["wage_debt_poverty"]["by_term"], {"賃金": 1})

    def test_longest_match_avoids_double_counting(self) -> None:
        sample = "トークン予算とトークン課金とトークンを測り、あらゆる価格を超えた無償の贈与と尊厳を守る。"
        res = currency_audit.scan_text(sample)
        self.assertEqual(
            res["compute_token_metering"]["by_term"],
            {"トークン予算": 1, "トークン課金": 1, "トークン": 1},
        )
        self.assertEqual(
            res["gift_dignity_unpriceable"]["by_term"],
            {"あらゆる価格を超え": 1, "無償の贈与": 1, "尊厳": 1},
        )
        self.assertEqual(res["currency_price_market"]["count"], 0)

    def test_prose_and_quotes_are_separated(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-CUR-1",
            "title": "テスト",
            "text": "台帳の帳面を閉じた。「二円の借金と銀貨の釣銭を返せ」と声があった。",
        }
        report = currency_audit.measure_currency_audit([frag])
        pg = report["fragments_prose"]["groups"]
        qg = report["fragments_quotes"]["groups"]
        self.assertEqual(pg["currency_price_market"]["count"], 0)
        self.assertEqual(pg["wage_debt_poverty"]["count"], 0)
        self.assertEqual(pg["non_monetary_ledger_idioms"]["count"], 2)
        self.assertEqual(qg["currency_price_market"]["count"], 3)
        self.assertEqual(qg["wage_debt_poverty"]["count"], 1)

    def test_raw_kanji_kwic_respects_exclusions_and_quotes(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-CUR-2",
            "title": "テスト2",
            "text": "読売新聞を畳む。「金貨を売れ」と叫ぶ声の横で、小銭で紙を買い贈与する。",
        }
        kwic = currency_audit.inspect_raw_kanji_in_fragments([frag])
        self.assertEqual(len(kwic["売"]), 0)
        self.assertEqual(len(kwic["貨"]), 0)
        self.assertEqual(len(kwic["銭"]), 1)
        self.assertEqual(len(kwic["買"]), 1)
        self.assertEqual(len(kwic["贈"]), 1)

    def test_cli_json_runs_against_live_union_ledger(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            rc = currency_audit.main(["--json"])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertGreaterEqual(data["fragment_count"], 70)
        self.assertIn("materials", data)
        self.assertIn("readings", data)
        self.assertEqual(len(data["group_order"]), 5)


if __name__ == "__main__":
    unittest.main()
