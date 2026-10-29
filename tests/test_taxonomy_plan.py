import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import inspect_inquiry  # noqa: E402
import taxonomy_plan  # noqa: E402


class TaxonomyPlanTests(unittest.TestCase):
    def test_motif_subclusters_cover_all_real_motifs_bijectively(self) -> None:
        data = inspect_inquiry.load_all()
        real_motifs = set(data["motifs"].keys())
        assigned = [
            mid
            for _label, mids in taxonomy_plan.MOTIF_SUBCLUSTERS.values()
            for mid in mids
        ]
        self.assertEqual(len(assigned), len(set(assigned)), "Duplicate motif in subclusters")
        self.assertEqual(set(assigned), real_motifs)

    def test_units_partition_real_repository_without_overlap_or_omission(self) -> None:
        units = taxonomy_plan.build_units(taxonomy_plan.ROOT)
        self.assertEqual([u.unit_id for u in units], [f"U{i:02d}" for i in range(1, 17)])

        seen: set[tuple[str, str]] = set()
        for unit in units:
            self.assertGreater(len(unit.items), 0, f"{unit.unit_id} should not be empty")
            for item in unit.items:
                key = (item.target_kind, item.target_id)
                self.assertNotIn(key, seen, f"Duplicate target across units: {key}")
                seen.add(key)

        data = inspect_inquiry.load_all()
        for qid in data["questions"]:
            self.assertIn(("question", qid), seen)
        for mid in data["motifs"]:
            self.assertIn(("motif", mid), seen)
        for mat_id in data["materials"]:
            self.assertIn(("material", mat_id), seen)
        for fid in data["fragments"]:
            self.assertIn(("fragment", fid), seen)
        for rid in data["relations"]:
            self.assertIn(("relation", rid), seen)
        for sid in data["sessions"]:
            self.assertIn(("session", sid), seen)
        for rlid in data["read_log"]:
            self.assertIn(("read_log", rlid), seen)
        for eid in data["editorial_decisions"]:
            self.assertIn(("editorial_decision", eid), seen)

        for rfile in sorted((taxonomy_plan.ROOT / "readings").iterdir()):
            if rfile.is_file():
                self.assertIn(("reading_note", f"readings/{rfile.name}"), seen)

    def test_validate_and_build_map_in_temp_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shard_dir = root / "taxonomy" / "shards"
            shard_dir.mkdir(parents=True)
            row = {
                "record_id": "TAX-U02-FRAG-001",
                "unit_id": "U02",
                "target_kind": "fragment",
                "target_id": "FRAG-001",
                "primary_quadrant": "B_ai_self_db",
                "subcategories": ["B-1"],
                "human_view_stance": "会話記憶を持続する主体との対照としてのみ参照される。",
                "ai_self_db_stance": "無記名の断片を読み返す行為そのものが語り手を立ち上げる。",
                "return_status": "returned_to_core",
                "read_depth": "full_text_read",
                "evidence_anchor": "FRAG-001 冒頭対話 A/B",
            }
            (shard_dir / "U02-deadbeef.jsonl").write_text(
                json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            ok, errors, count = taxonomy_plan.validate_taxonomy_shards(root)
            self.assertTrue(ok, errors)
            self.assertEqual(count, 1)

            index_path = taxonomy_plan.build_taxonomy_map(root)
            self.assertTrue(index_path.is_file())
            content = index_path.read_text(encoding="utf-8")
            self.assertIn("`B_ai_self_db`", content)
            self.assertIn("`returned_to_core`", content)

            # Duplicate target across parallel shards must be caught
            (shard_dir / "U02-cafebabe.jsonl").write_text(
                json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            ok2, errors2, _ = taxonomy_plan.validate_taxonomy_shards(root)
            self.assertFalse(ok2)
            self.assertTrue(any("duplicate classification" in e for e in errors2))


if __name__ == "__main__":
    unittest.main()
