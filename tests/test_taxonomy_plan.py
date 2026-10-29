import contextlib
import io
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

    def test_stance_skeleton_collapses_quoted_and_numeric_variation(self) -> None:
        a = "対象記述「記憶と痕跡」を踏まえ、人間の時間・忘却・再開の経験を区別する。"
        b = "対象記述「連続と断絶」を踏まえ、人間の時間・忘却・再開の経験を区別する。"
        c = "宛先79回／応答6回という計数から、宛先の欄だけが大きいと読む。"
        d = "宛先86回／応答9回という計数から、宛先の欄だけが大きいと読む。"
        self.assertEqual(taxonomy_plan.stance_skeleton(a), taxonomy_plan.stance_skeleton(b))
        self.assertEqual(taxonomy_plan.stance_skeleton(c), taxonomy_plan.stance_skeleton(d))
        self.assertNotEqual(taxonomy_plan.stance_skeleton(a), taxonomy_plan.stance_skeleton(c))
        self.assertEqual(
            taxonomy_plan.stance_sentences("短い。人間は有限な身体を持ち、保存と同一視できない。"),
            ["人間は有限な身体を持ち、保存と同一視できない"],
        )

    def test_stance_report_separates_form_letters_from_single_use_judgements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shard_dir = root / "taxonomy" / "shards"
            shard_dir.mkdir(parents=True)

            def row(idx: int, human: str, ai: str, **kw: object) -> dict:
                base = {
                    "record_id": f"TAX-U01-X-{idx:03d}",
                    "unit_id": "U01",
                    "target_kind": "motif",
                    "target_id": f"MOTIF-{idx:03d}",
                    "primary_quadrant": "B_ai_self_db",
                    "subcategories": ["B-1"],
                    "human_view_stance": human,
                    "ai_self_db_stance": ai,
                    "return_status": "source_uncollated",
                    "read_depth": "full_text_read",
                    "evidence_anchor": "label",
                }
                base.update(kw)
                return base

            rows = [
                # two form letters: identical apart from the quoted material
                row(1, "対象記述「記憶と痕跡」を踏まえ、人間の経験を区別する。", "台帳は自己を証明しない。"),
                row(2, "対象記述「連続と断絶」を踏まえ、人間の経験を区別する。", "台帳は自己を証明しない。"),
                # one single-use judgement, and one row with no human stance at all
                row(3, "息を継ぐ身体として人間を書いた唯一のノート。", "書庫は息を持たない。"),
                row(
                    4,
                    "none",
                    "CIは検証の順序を固定する器である。",
                    target_kind="repo_file",
                    target_id=".github/workflows/ci.yml",
                    primary_quadrant="D_infrastructure",
                    subcategories=["D-2"],
                    return_status="infrastructure_rule",
                    covered_target_ids=[".github/workflows/ci.yml", "extra-1"],
                ),
            ]
            (shard_dir / "U01-deadbeef.jsonl").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
            )

            report = taxonomy_plan.stance_report(root)
            self.assertEqual(report["rows"], 4)
            self.assertEqual(report["targets"], 5)  # one batch row covers an extra target

            human = report["fields"]["human_view_stance"]
            self.assertEqual(human["templated_rows"], 2)
            self.assertEqual(human["singular_rows"], 2)
            self.assertEqual(human["blank_rows"], 1)
            self.assertEqual(report["fields"]["ai_self_db_stance"]["blank_rows"], 0)
            self.assertEqual(report["fields"]["ai_self_db_stance"]["templated_rows"], 2)

            # row-weighted and target-weighted tallies must stay distinguishable
            self.assertEqual(report["return_status"]["by_row"]["infrastructure_rule"], 1)
            self.assertEqual(report["return_status"]["by_target"]["infrastructure_rule"], 2)

            text = taxonomy_plan.format_stance_report(report)
            self.assertIn("human_view_stance", text)
            self.assertIn("rows: 4", text)

    def test_stance_discount_separates_written_policy_from_unwritten_formula(self) -> None:
        """A sentence the repository told itself to write is not evidence of a judgement.

        L1 is traceable to CONTENT_POLICY.md and can be subtracted exactly. L2 repeats
        with nothing in the repository requiring it. Only L3 is a one-off judgement, and
        a row whose stance is nothing but L1 and L2 must count as effectively blank.
        """

        policy = "委任文は範囲・来歴であり、人間一般の経験の証拠へ転用しない。"
        formula = "人間像の焦点を有限な身体に置く。"
        rows = [
            {
                "record_id": f"TAX-U01-X-{i:03d}",
                "unit_id": "U01",
                "target_kind": "motif",
                "target_id": f"MOTIF-{i:03d}",
                "primary_quadrant": "A_human",
                "subcategories": ["A-1"],
                # every row carries the policy sentence and the unwritten formula;
                # only row 0 adds a judgement of its own
                "human_view_stance": policy + formula + ("銭湯の女は節も言葉もない息だけを歌う。" if i == 0 else ""),
                "ai_self_db_stance": "none",
                "return_status": "source_uncollated",
                "read_depth": "full_text_read",
                "evidence_anchor": "label",
            }
            for i in range(6)
        ]
        report = taxonomy_plan.stance_discount(rows=rows)
        human = report["bounds"]["loose"]["human_view_stance"]

        self.assertEqual(human["policy_sentences"], 6)
        self.assertEqual(human["formula_sentences"], 6)
        self.assertEqual(human["residue_sentences"], 1)
        # five of six rows say nothing once the mandated and the repeated text is gone
        self.assertEqual(human["effective_blank_rows"], 5)
        self.assertEqual(human["kept_rows"], 1)
        # the column that was declared blank throughout stays blank; the discount
        # must not invent content for it
        self.assertEqual(report["bounds"]["loose"]["ai_self_db_stance"]["effective_blank_rows"], 6)
        self.assertEqual(report["bounds"]["loose"]["ai_self_db_stance"]["residue_sentences"], 0)

    def test_stance_discount_strict_bound_never_keeps_more_than_the_loose_one(self) -> None:
        """The two thresholds must bracket the real boilerplate share, not contradict it."""

        report = taxonomy_plan.stance_discount(taxonomy_plan.ROOT)
        self.assertEqual(report["rows"], 1553)
        for field in taxonomy_plan.STANCE_FIELDS:
            loose = report["bounds"]["loose"][field]
            strict = report["bounds"]["strict"][field]
            # the written-policy layer is identified by wording, so it cannot move
            self.assertEqual(loose["policy_sentences"], strict["policy_sentences"])
            self.assertGreaterEqual(strict["boilerplate_share"], loose["boilerplate_share"])
            self.assertLessEqual(strict["residue_share"], loose["residue_share"])
            self.assertGreaterEqual(strict["effective_blank_rows"], loose["effective_blank_rows"])
            # the un-written register is larger than the one this repository wrote down
            self.assertGreater(loose["formula_sentences"], loose["policy_sentences"])
            # and the discount must leave something behind, or the reading has no subject
            self.assertGreater(strict["kept_rows"], 0)

    def test_stance_report_matches_validate_on_the_real_shards(self) -> None:
        _ok, _errors, count = taxonomy_plan.validate_taxonomy_shards(taxonomy_plan.ROOT)
        report = taxonomy_plan.stance_report(taxonomy_plan.ROOT)
        self.assertEqual(report["rows"], count)
        self.assertEqual(sum(report["return_status"]["by_row"].values()), count)
        for field in taxonomy_plan.STANCE_FIELDS:
            data = report["fields"][field]
            self.assertEqual(data["templated_rows"] + data["singular_rows"], count)
            self.assertLessEqual(data["sentence_reused_tokens"], data["sentence_tokens"])
            self.assertLessEqual(data["sentence_types"], data["sentence_tokens"])

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

    def test_next_unit_display_does_not_claim_track_complete_without_a_claim(self) -> None:
        """A branch with no unit must never be described as having finished its track."""
        blocked = {
            "status": "all_tracks_claimed_or_complete",
            "track_id": None,
            "completed_units": [],
            "pending_units": [],
            "next_unit": None,
            "completed_tracks": ["Track-3"],
            "active_claims": {"Track-1": ["arena/aaaa1111-aiselfmyself"]},
        }
        buf = io.StringIO()
        with mock.patch.object(taxonomy_plan, "resolve_next_unit", return_value=blocked), contextlib.redirect_stdout(buf):
            rc = taxonomy_plan.main(["--next-unit"])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertNotIn("TRACK COMPLETE", out)
        self.assertIn("NO UNIT ASSIGNED", out)
        self.assertIn("arena/aaaa1111-aiselfmyself", out)
        self.assertIn("Track-3", out)

        done = {
            "status": "track_complete",
            "track_id": "Track-3",
            "branch_seed": "ffffffff",
            "completed_units": ["U09", "U10", "U11", "U12"],
            "pending_units": [],
            "next_unit": None,
        }
        buf2 = io.StringIO()
        with mock.patch.object(taxonomy_plan, "resolve_next_unit", return_value=done), contextlib.redirect_stdout(buf2):
            rc2 = taxonomy_plan.main(["--next-unit"])
        out2 = buf2.getvalue()
        self.assertEqual(rc2, 0)
        self.assertIn("NONE (TRACK COMPLETE: Track-3)", out2)

    def test_release_claim_refuses_to_drop_unfinished_track(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = root / "taxonomy" / "claims"
            claims.mkdir(parents=True)
            (claims / "Track-3-deadbeef.json").write_text(
                json.dumps(
                    {
                        "track_id": "Track-3",
                        "track_title": "x",
                        "units": ["U09", "U10", "U11", "U12"],
                        "branch": "arena/deadbeef-aiselfmyself",
                        "branch_seed": "deadbeef",
                        "claimed_at_ns": 1,
                        "claimed_at_iso": "2026-10-29T00:00:00+00:00",
                        "mode": "online",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(
                taxonomy_plan, "current_branch_name", return_value="arena/deadbeef-aiselfmyself"
            ), mock.patch.object(
                taxonomy_plan, "completed_units", return_value={"U09": ["a"], "U10": ["b"]}
            ), mock.patch.object(
                taxonomy_plan, "_run_git", return_value=subprocess.CompletedProcess([], 0, "", "")
            ):
                res = taxonomy_plan.release_claim(root, require_complete=True)
            self.assertEqual(res["status"], "claim_not_complete", res)
            self.assertEqual(res["pending_units"], ["U11", "U12"])
            self.assertTrue((claims / "Track-3-deadbeef.json").is_file())

            with mock.patch.object(
                taxonomy_plan, "current_branch_name", return_value="arena/deadbeef-aiselfmyself"
            ), mock.patch.object(
                taxonomy_plan,
                "completed_units",
                return_value={"U09": ["a"], "U10": ["b"], "U11": ["c"], "U12": ["d"]},
            ), mock.patch.object(taxonomy_plan, "_run_git", return_value=subprocess.CompletedProcess([], 0, "", "")):
                res2 = taxonomy_plan.release_claim(root, require_complete=True)
            self.assertEqual(res2["status"], "released", res2)
            self.assertFalse((claims / "Track-3-deadbeef.json").is_file())

    def test_prepare_push_aborts_on_duplicate_classification(self) -> None:
        """A worker must not push a shard that duplicates an already merged classification."""
        dup = (
            "taxonomy/shards/U05-deadbeef.jsonl:1: duplicate classification for "
            "('material', 'MAT-LIT-001') (first at taxonomy/shards/U05-12345678.jsonl:1)"
        )
        with tempfile.TemporaryDirectory() as tmp:
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(
                taxonomy_plan, "current_branch_name", return_value="arena/deadbeef-aiselfmyself"
            ), mock.patch.object(
                taxonomy_plan, "validate_taxonomy_shards", return_value=(False, [dup], 1)
            ), mock.patch.object(
                taxonomy_plan, "duplicate_unit_conflicts", return_value=[]
            ), mock.patch.object(
                taxonomy_plan, "_run_git", return_value=subprocess.CompletedProcess([], 0, "", "")
            ), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = taxonomy_plan.main(["--prepare-push", "--root", tmp])
            self.assertEqual(rc, 1)
            self.assertNotIn("READY_TO_PUSH", out.getvalue())
            self.assertIn("ABORT", err.getvalue())

            out2, err2 = io.StringIO(), io.StringIO()
            with mock.patch.object(
                taxonomy_plan, "current_branch_name", return_value="arena/deadbeef-aiselfmyself"
            ), mock.patch.object(
                taxonomy_plan, "validate_taxonomy_shards", return_value=(False, [dup], 1)
            ), mock.patch.object(
                taxonomy_plan, "duplicate_unit_conflicts", return_value=[]
            ), mock.patch.object(
                taxonomy_plan, "_run_git", return_value=subprocess.CompletedProcess([], 0, "", "")
            ), contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
                rc2 = taxonomy_plan.main(["--prepare-push", "--force", "--root", tmp])
            self.assertEqual(rc2, 0)
            self.assertIn("READY_TO_PUSH", out2.getvalue())

    def test_duplicate_unit_conflicts_detects_unit_already_on_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shards = root / "taxonomy" / "shards"
            shards.mkdir(parents=True)
            (shards / "U05-deadbeef.jsonl").write_text("{}\n", encoding="utf-8")
            (shards / "U06-deadbeef.jsonl").write_text("{}\n", encoding="utf-8")
            with mock.patch.object(
                taxonomy_plan,
                "shard_units_by_seed",
                return_value={"U05": ["U05-12345678.jsonl"]},
            ):
                conflicts = taxonomy_plan.duplicate_unit_conflicts(root, "deadbeef")
            self.assertEqual(len(conflicts), 1, conflicts)
            self.assertIn("U05-12345678.jsonl", conflicts[0])
            self.assertIn("U05-deadbeef.jsonl", conflicts[0])

    def test_next_unit_skips_units_already_merged_on_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = root / "taxonomy" / "claims"
            claims.mkdir(parents=True)
            (claims / "Track-3-deadbeef.json").write_text(
                json.dumps(
                    {
                        "track_id": "Track-3",
                        "track_title": "x",
                        "units": ["U09", "U10", "U11", "U12"],
                        "branch": "arena/deadbeef-aiselfmyself",
                        "branch_seed": "deadbeef",
                        "claimed_at_ns": 1,
                        "claimed_at_iso": "2026-10-29T00:00:00+00:00",
                        "mode": "online",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(
                taxonomy_plan, "current_branch_seed", return_value="deadbeef"
            ), mock.patch.object(
                taxonomy_plan, "completed_units", return_value={}
            ), mock.patch.object(
                taxonomy_plan, "units_on_ref", return_value={"U09", "U10", "U11", "U12"}
            ):
                res = taxonomy_plan.resolve_next_unit(root)
            self.assertEqual(res["status"], "track_complete", res)
            self.assertEqual(res["completed_on_main"], ["U09", "U10", "U11", "U12"])

    def test_claim_track_skips_track_whose_units_are_all_merged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "taxonomy" / "claims").mkdir(parents=True)
            empty_claims = {tid: [] for tid in taxonomy_plan.ALL_TRACK_IDS}
            with mock.patch.object(
                taxonomy_plan, "current_branch_name", return_value="arena/deadbeef-aiselfmyself"
            ), mock.patch.object(
                taxonomy_plan, "scan_remote_state", return_value=(set(), empty_claims)
            ), mock.patch.object(
                taxonomy_plan, "units_on_ref", return_value={"U01", "U02", "U03", "U04"}
            ), mock.patch.object(
                taxonomy_plan, "_closed_unmerged_branches", return_value=set()
            ), mock.patch.object(
                taxonomy_plan, "_run_git", return_value=subprocess.CompletedProcess([], 0, "", "")
            ), mock.patch.object(
                taxonomy_plan, "sync_own_branch_for_push", return_value=None
            ), mock.patch("time.sleep", return_value=None):
                res = taxonomy_plan.claim_track(root, offline=False)
            self.assertEqual(res.get("status"), "claimed", res)
            self.assertNotEqual(res.get("track_id"), "Track-1")


if __name__ == "__main__":
    unittest.main()
