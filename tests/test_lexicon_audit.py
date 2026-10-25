"""Tests for tools/lexicon_audit.py (reusable dictionary-driven lexical mirror)."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import lexicon_audit  # noqa: E402


class LexiconAuditTests(unittest.TestCase):
    def test_longest_match_and_exclude_masking(self) -> None:
        groups = {
            "paper": {"label": "紙", "terms": ["紙片", "紙"]},
            "wind": {"label": "風", "terms": ["強風", "風"]},
        }
        # "手紙" and "風景" are excluded; "紙片" should match once without double-counting "紙".
        groups_res, excluded = lexicon_audit.scan_groups(
            "手紙を読む。紙片が風景のなかを強風と風に舞う。",
            groups,
            exclude_terms=["手紙", "風景"],
        )
        self.assertEqual(excluded, {"手紙": 1, "風景": 1})
        self.assertEqual(groups_res["paper"]["count"], 1)
        self.assertEqual(groups_res["paper"]["terms"], {"紙片": 1})
        self.assertEqual(groups_res["wind"]["count"], 2)
        self.assertEqual(groups_res["wind"]["terms"], {"強風": 1, "風": 1})

    def test_quotes_are_separated_from_prose_and_kanji_kwic_tracks_exclusions(self) -> None:
        fragments = [
            {
                "fragment_id": "FRAG-TEST-1",
                "title": "外へ",
                "text": "潮の匂いがする。「書庫の欄に記入せよ」と誰かが言ったが手紙をポケットに入れた。",
            },
            {
                "fragment_id": "FRAG-TEST-2",
                "title": "帳面",
                "text": "古い台帳の欄を指でなぞる。",
            },
        ]
        preset = lexicon_audit.PRESETS["scriptorium"]
        report = lexicon_audit.audit_corpus(
            fragments=fragments,
            groups=preset["groups"],
            exclude_terms=preset["exclude_terms"],
            kanji="庫帳欄紙",
        )
        self.assertEqual(report["fragments_prose"]["zero_hit_fragment_ids"], ["FRAG-TEST-1"])
        self.assertEqual(report["fragments_prose"]["hit_total"], 2)  # 台帳 + 欄 in FRAG-TEST-2
        self.assertEqual(report["fragments_quotes"]["hit_total"], 3)  # 書庫 + 欄 + 記入 inside quotes
        # "紙" appears once in FRAG-TEST-1 prose inside "手紙" (excluded), so remaining_candidate == 0.
        self.assertEqual(report["kanji_polysemy"]["紙"]["total"], 1)
        self.assertEqual(report["kanji_polysemy"]["紙"]["excluded_compound"], 1)
        self.assertEqual(report["kanji_polysemy"]["紙"]["remaining_candidate"], 0)
        self.assertEqual(report["kanji_polysemy"]["欄"]["remaining_candidate"], 1)

    def test_cli_preset_group_and_spec_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state"
            state.mkdir()
            (state / "fragments.jsonl").write_text(
                json.dumps(
                    {
                        "fragment_id": "FRAG-001",
                        "title": "浜辺",
                        "text": "濡れた砂に足跡がつく。答えはここにある。",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = lexicon_audit.main(["--preset", "scriptorium", "--json", "--root", str(root)])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(data["fragments_prose"]["hit_total"], 0)

            spec_path = root / "spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "groups": {"shore": {"label": "浜", "terms": ["砂", "足跡"]}},
                        "exclude_terms": ["砂時計"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            out2 = io.StringIO()
            with contextlib.redirect_stdout(out2):
                rc2 = lexicon_audit.main(["--spec", str(spec_path), "--json", "--root", str(root)])
            self.assertEqual(rc2, 0)
            data2 = json.loads(out2.getvalue())
            self.assertEqual(data2["fragments_prose"]["hit_total"], 2)


if __name__ == "__main__":
    unittest.main()
