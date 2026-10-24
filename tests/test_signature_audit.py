"""Unit tests for tools/signature_audit.py."""
from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import signature_audit  # noqa: E402


class TestSignatureAudit(unittest.TestCase):
    def test_exclusions_do_not_trigger(self) -> None:
        sample = "筆者が執筆し、鉛筆で印象派の印刷物とインドの印税を記す。"
        res = signature_audit.scan_text(sample)
        for grp, info in res.items():
            self.assertEqual(info["count"], 0, f"unexpected hit in {grp}: {info}")

    def test_groups_and_longest_match(self) -> None:
        sample = "真跡の筆跡と花押を電子署名と印鑑登録で照合し、偽書の真贋を見る。"
        res = signature_audit.scan_text(sample)
        self.assertEqual(res["handwriting_trace"]["by_term"].get("真跡"), 1)
        self.assertEqual(res["handwriting_trace"]["by_term"].get("筆跡"), 1)
        self.assertEqual(res["signature_mark"]["by_term"].get("花押"), 1)
        self.assertGreaterEqual(res["signature_mark"]["count"], 1)
        self.assertEqual(res["seal_stamp"]["by_term"].get("印鑑登録"), 1)
        self.assertEqual(res["forgery_authorship"]["by_term"].get("偽書"), 1)
        self.assertEqual(res["forgery_authorship"]["by_term"].get("真贋"), 1)
        # 電子署名は signature_mark に最長一致で入り、machine と二重計上しない
        self.assertEqual(res["signature_mark"]["by_term"].get("電子署名"), 1)
        self.assertEqual(res["machine_signature"]["count"], 0)

    def test_prose_and_quotes_separated(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-SIG-1",
            "title": "テスト",
            "text": "窓口は静かだった。「これは直筆の署名である」と声があった。",
        }
        report = signature_audit.measure_signature_audit([frag])
        pg = report["fragments_prose"]["groups"]
        qg = report["fragments_quotes"]["groups"]
        self.assertEqual(pg["handwriting_trace"]["count"], 0)
        self.assertEqual(pg["signature_mark"]["count"], 0)
        self.assertEqual(qg["handwriting_trace"]["count"], 1)
        self.assertEqual(qg["signature_mark"]["count"], 1)

    def test_raw_kanji_kwic_respects_exclusions(self) -> None:
        frag = {
            "fragment_id": "FRAG-TEST-SIG-2",
            "title": "テスト2",
            "text": "筆者が印象を書く。印を押す係は偽書を見る。",
        }
        kwic = signature_audit.inspect_raw_kanji_in_fragments([frag])
        self.assertEqual(len(kwic["筆"]), 0)
        self.assertEqual(len(kwic["印"]), 1)
        self.assertEqual(len(kwic["偽"]), 1)

    def test_cli_json_runs(self) -> None:
        buf = StringIO()
        with redirect_stdout(buf):
            rc = signature_audit.main(["--json"])
        self.assertEqual(rc, 0)
        self.assertIn("fragments_prose", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
