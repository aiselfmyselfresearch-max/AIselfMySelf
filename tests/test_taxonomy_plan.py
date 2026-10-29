import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_validate_covered_target_ids_and_build_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shard_dir = root / "taxonomy" / "shards"
            shard_dir.mkdir(parents=True)
            row = {
                "record_id": "TAX-U08-REL-BATCH-01",
                "unit_id": "U08",
                "target_kind": "relation",
                "target_id": "REL-001",
                "covered_target_ids": ["REL-002", "REL-003"],
                "primary_quadrant": "B_ai_self_db",
                "subcategories": ["B-1", "B-3"],
                "human_view_stance": "none",
                "ai_self_db_stance": "初期セッションの応答エッジ群。",
                "return_status": "returned_to_core",
                "read_depth": "full_text_read",
                "evidence_anchor": "REL-001..REL-003 note欄",
            }
            (shard_dir / "U08-deadbeef.jsonl").write_text(
                json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            ok, errors, count = taxonomy_plan.validate_taxonomy_shards(root)
            self.assertTrue(ok, errors)
            self.assertEqual(count, 1)

            index_path = taxonomy_plan.build_taxonomy_map(root)
            content = index_path.read_text(encoding="utf-8")
            self.assertIn("対象アイテム総数: **3**", content)

            # Overlapping covered_target_ids across shards must fail
            dup_row = dict(row, record_id="TAX-U08-REL-DUP", target_id="REL-003", covered_target_ids=[])
            (shard_dir / "U08-cafebabe.jsonl").write_text(
                json.dumps(dup_row, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            ok2, errors2, _ = taxonomy_plan.validate_taxonomy_shards(root)
            self.assertFalse(ok2)
            self.assertTrue(any("duplicate classification" in e for e in errors2))

    def test_four_parallel_workers_claim_four_distinct_tracks_on_shared_origin(self) -> None:
        """Simulate 4 Arena worker branches running identical --claim-track against a shared git origin."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            origin = base / "origin.git"
            subprocess.run(["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)

            seed_repo = base / "seed"
            subprocess.run(["git", "init", "-b", "main", str(seed_repo)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(seed_repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(seed_repo), "config", "user.name", "Test"], check=True)
            (seed_repo / "README.md").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(seed_repo), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(seed_repo), "commit", "-m", "init"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(seed_repo), "remote", "add", "origin", str(origin)], check=True)
            subprocess.run(["git", "-C", str(seed_repo), "push", "origin", "main"], check=True, capture_output=True)

            # Deliberately give all 4 branches seeds with the SAME mod-4 remainder (00000000, 00000004, 00000008, 0000000c)
            # to prove remote claim discovery resolves collisions deterministically!
            branches = [
                "arena/00000000-aiselfmyself",
                "arena/00000004-aiselfmyself",
                "arena/00000008-aiselfmyself",
                "arena/0000000c-aiselfmyself",
            ]
            claimed_tracks: list[str] = []

            with mock.patch("time.sleep", return_value=None), mock.patch.object(
                taxonomy_plan, "_closed_unmerged_branches", return_value=set()
            ):
                for idx, bname in enumerate(branches):
                    wdir = base / f"worker_{idx}"
                    subprocess.run(["git", "clone", str(origin), str(wdir)], check=True, capture_output=True)
                    subprocess.run(["git", "-C", str(wdir), "checkout", "-b", bname], check=True, capture_output=True)
                    subprocess.run(["git", "-C", str(wdir), "config", "user.email", "test@example.com"], check=True)
                    subprocess.run(["git", "-C", str(wdir), "config", "user.name", "Test"], check=True)

                    res = taxonomy_plan.claim_track(wdir, offline=False)
                    self.assertEqual(res["status"], "claimed", res)
                    claimed_tracks.append(res["track_id"])

                    # Re-running on same branch is idempotent
                    res_again = taxonomy_plan.claim_track(wdir, offline=False)
                    self.assertEqual(res_again["status"], "already_claimed")
                    self.assertEqual(res_again["track_id"], res["track_id"])

                # A 5th worker sees all 4 tracks already claimed
                w5 = base / "worker_4"
                subprocess.run(["git", "clone", str(origin), str(w5)], check=True, capture_output=True)
                subprocess.run(
                    ["git", "-C", str(w5), "checkout", "-b", "arena/00000010-aiselfmyself"],
                    check=True,
                    capture_output=True,
                )
                res5 = taxonomy_plan.claim_track(w5, offline=False)
                self.assertEqual(res5["status"], "all_tracks_claimed_or_complete")

            self.assertEqual(set(claimed_tracks), {"Track-1", "Track-2", "Track-3", "Track-4"})


if __name__ == "__main__":
    unittest.main()
