"""Unit tests for tools/vegetal_audit.py (52nd mirror)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.vegetal_audit import (
    VEGETAL_GROUPS,
    count_seed_literal,
    inspect_raw_kanji_in_fragments,
    measure_vegetal_audit,
    scan_text,
    split_prose_and_quotes,
)


class VegetalAuditTests(unittest.TestCase):
    def test_empty_corpora_zero_counts(self) -> None:
        report = measure_vegetal_audit([], materials=[], readings=[])
        self.assertEqual(report["fragment_count"], 0)
        self.assertEqual(report["fragments_prose"]["living_total"], 0)
        self.assertEqual(report["fragments_prose"]["control_total"], 0)
        self.assertEqual(len(report["group_order"]), 7)
        self.assertEqual(len(report["living_group_order"]), 5)
        self.assertEqual(len(report["control_group_order"]), 2)

    def test_non_botanical_compounds_excluded(self) -> None:
        text = (
            "一種の劇場、気まずい種明かし、百七十二種、火種、違反の種類、人種。"
            "同じ屋根の下、根拠と根元、新幹線と幹部。"
            "絵葉書と万葉集、千葉と前頭葉。"
            "火花と花崗岩と花押。"
            "啄木と松尾芭蕉と森鷗外と小林、木曜と木星。"
            "仕草と浅草、粘土板と国土と土佐。"
            "しばらく立ち止まる。"
        )
        scanned = scan_text(text)
        for group_key, spec in VEGETAL_GROUPS.items():
            if spec["kind"] == "living":
                self.assertEqual(
                    scanned[group_key],
                    {},
                    f"Expected no living plant matches in {group_key}, got {scanned[group_key]}",
                )
        self.assertEqual(scanned["timber_paper_relic"], {"粘土板": 0}.get("x", {}))
        self.assertEqual(scanned["arborescent_meta"], {"根拠": 1})
        self.assertEqual(count_seed_literal(text), 0)

    def test_living_plants_separated_from_timber_and_meta(self) -> None:
        fragments = [
            {
                "fragment_id": "FRAG-TEST-1",
                "text": (
                    "腐葉土のなかに蒔いた種が発芽し、双葉と毛根を伸ばして桜の花が咲いた。"
                    "「実行状態の木と構文木の枝刈り」"
                    "机の木箱には古い草稿と積み木が収められ、言葉と根拠だけが残る。"
                ),
            }
        ]
        report = measure_vegetal_audit(fragments, materials=[], readings=[])
        fp = report["fragments_prose"]
        fq = report["fragments_quotes"]

        self.assertGreaterEqual(fp["groups"]["seed_sprout"]["count"], 3)
        self.assertGreaterEqual(fp["groups"]["root_stem_leaf"]["count"], 1)
        self.assertGreaterEqual(fp["groups"]["flower_fruit"]["count"], 2)
        self.assertGreaterEqual(fp["groups"]["soil_cultivation"]["count"], 1)
        self.assertEqual(fp["groups"]["timber_paper_relic"]["count"], 3)
        self.assertEqual(fp["groups"]["arborescent_meta"]["count"], 2)
        self.assertEqual(report["seed_literal"], 1)

        # Quoted CS tree metaphors stay in fragments_quotes, not fragments_prose
        self.assertEqual(fq["groups"]["arborescent_meta"]["count"], 3)

    def test_split_prose_and_quotes_preserves_unquoted_text(self) -> None:
        prose, quoted = split_prose_and_quotes("庭の土に「次回の種」を埋める。")
        self.assertIn("庭の土", prose)
        self.assertNotIn("次回の種", prose)
        self.assertIn("次回の種", quoted)

    def test_raw_kanji_kwic_tracks_all_twelve_kanji(self) -> None:
        fragments = [{"fragment_id": "F-1", "text": "種の芽と根と幹と枝と葉と花、木と樹と森と草と土。"}]
        kwic = inspect_raw_kanji_in_fragments(fragments)
        self.assertEqual(len(kwic), 12)
        for ch, rows in kwic.items():
            self.assertEqual(len(rows), 1, f"Expected 1 hit for {ch}")

    def test_materials_and_readings_aggregated(self) -> None:
        materials = [
            {
                "material_id": "MAT-1",
                "title": "倒木更新と菌根ネットワーク",
                "passage": "永久凍土の種子庫から発芽したナツメヤシ。",
                "source_note": "接ぎ木と植物標本帳",
            }
        ]
        readings = [("2026-10-25-test.md", "どの枝を伸ばすか、次回の種と構文木と光合成。")]
        report = measure_vegetal_audit([], materials=materials, readings=readings)
        self.assertGreaterEqual(report["materials"]["living_total"], 6)
        self.assertGreaterEqual(report["readings"]["control_total"], 3)
        self.assertGreaterEqual(report["readings"]["living_total"], 1)

    def test_cli_json_runs_cleanly_on_base_ledger(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "vegetal_audit.py"), "--json", "--base-only"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(set(payload["group_order"]), set(VEGETAL_GROUPS.keys()))
        self.assertGreater(payload["fragment_count"], 0)


if __name__ == "__main__":
    unittest.main()
