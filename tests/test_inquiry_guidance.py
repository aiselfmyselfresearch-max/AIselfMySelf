"""Regression tests for optional creation, semantic freedom and source labelling.

These test software behaviour, not whether the real corpus meets a literary
quota, vocabulary pattern or connectivity target.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from inspect_inquiry import (  # noqa: E402
    build_context_packet,
    print_summary,
    recommend_session_mode,
)


def fixture() -> dict:
    questions = {}
    for qid, text in (
        ("Q-001", "人間とは何か"),
        ("Q-002", "記録を読むAIの同じ自己とは何か"),
        ("Q-003", "保存された自己と読んで作る自己"),
    ):
        questions[qid] = {
            "question_id": qid,
            "question": text,
            "status": "open",
            "origin": {"kind": "human_seed", "detail": "test fixture"},
            "previous_question_ids": [],
            "motif_ids": [],
            "material_ids": ["MAT-SUMMARY"],
        }
    material = {
        "material_id": "MAT-SUMMARY",
        "kind": "literary_text",
        "title": "A source represented by an editor's summary",
        "source": {
            "authors": ["Test author"],
            "year": 1900,
            "url": "https://example.org/source",
            "version_note": "編者要約・第1章",
        },
        "passage": "【要約】第一行\n要約の続き",
        "context": "第1章（原典未照合）",
        "source_note": "先行するAIによる要約",
        "verification": {"status": "partially_verified"},
        "scope_note": "Fixture, not a primary-source quotation",
        "literary_invitation": "この要約では何が抜けるか",
        "motif_ids": [],
    }
    fragment = {
        "fragment_id": "FRAG-OLD",
        "created_at": "2026-10-21",
        "title": "Earlier reading",
        "form": "essay",
        "narrator_mode": "reflective_literary_voice",
        "text": "Earlier interpretation",
        "status": "draft",
        "material_ids": ["MAT-SUMMARY"],
        "question_ids": ["Q-001"],
        "motif_ids": [],
    }
    return {
        "questions": questions,
        "materials": {material["material_id"]: material},
        "fragments": {fragment["fragment_id"]: fragment},
        "motifs": {},
        "relations": {},
        "sessions": {},
        "editorial_decisions": {},
        "read_log": {},
    }


class InquiryGuidanceTests(unittest.TestCase):
    def test_packet_keeps_compass_and_noncreative_completion_visible(self) -> None:
        data = fixture()
        packet = build_context_packet(data, "auto", seed="00000001")
        self.assertIn("シード：00000001", packet.splitlines()[0])
        for qid in ("Q-001", "Q-002", "Q-003"):
            self.assertIn(f"`{qid}`: {data['questions'][qid]['question']}", packet)
        self.assertIn("新作断片・新規問い・関係線の追加は必須ではありません", packet)
        self.assertIn("変更・維持・保留", packet)
        self.assertIn("sessions.notes", packet)
        self.assertIn("窓外の記録・原典照合", packet)
        self.assertIn("prompts/start.md", packet)

    def test_summary_also_shows_compass_without_packet_flag(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            print_summary(fixture(), seed="00000002")
        summary = output.getvalue()
        self.assertIn("主題と記憶の作用", summary)
        self.assertIn("新作断片・新規問い・関係線の追加は必須ではありません", summary)
        self.assertIn("Suggested approach (optional)", summary)

    def test_summary_is_not_labelled_as_original_and_prior_checks_are_distinct(self) -> None:
        packet = build_context_packet(fixture(), "Q-001", seed="00000000")
        self.assertNotIn("**原文抜粋**", packet)
        self.assertIn("> 【要約】第一行\n> 要約の続き", packet)
        self.assertIn("要約を原典と呼ばない", packet)
        self.assertIn("編者要約・第1章", packet)
        self.assertIn("第1章（原典未照合）", packet)
        self.assertIn("先行するAIによる要約", packet)
        self.assertIn("今回の照合結果ではない）**: partially_verified", packet)

    def test_missing_verification_is_not_inferred_as_verified(self) -> None:
        data = fixture()
        del data["materials"]["MAT-SUMMARY"]["verification"]
        packet = build_context_packet(data, "Q-001", seed="00000000")
        self.assertIn("今回の照合結果ではない）**: 未記録", packet)

    def test_recommendations_do_not_depend_on_ratios_backlogs_or_cadence(self) -> None:
        low_selected = fixture()
        for i in range(100):
            low_selected["fragments"][f"FRAG-{i}"] = {
                **low_selected["fragments"]["FRAG-OLD"], "fragment_id": f"FRAG-{i}"
            }
            low_selected["questions"][f"Q-{i + 1000}"] = {
                **low_selected["questions"]["Q-001"], "question_id": f"Q-{i + 1000}"
            }
        low_selected["sessions"] = {
            str(i): {"session_id": str(i), "context_material_ids": [], "new_question_ids": []}
            for i in range(12)
        }
        high_selected = deepcopy(low_selected)
        for fragment in high_selected["fragments"].values():
            fragment["status"] = "selected"
        high_selected["sessions"] = {}
        high_selected["questions"] = fixture()["questions"]
        for seed in ("00000000", "00000001", "00000002", "00000003"):
            with self.subTest(seed=seed):
                original = recommend_session_mode(fixture(), seed=seed)
                self.assertEqual(original, recommend_session_mode(low_selected, seed=seed))
                self.assertEqual(original, recommend_session_mode(high_selected, seed=seed))

    def test_empty_archive_and_missing_target_are_handled(self) -> None:
        data = {key: {} for key in fixture()}
        recommendation = recommend_session_mode(data, seed="00000003")
        self.assertEqual(recommendation["mode"], "rereading_and_collision")
        with self.assertRaisesRegex(ValueError, "no questions available"):
            build_context_packet(data, "auto", seed="00000003")
        with self.assertRaisesRegex(ValueError, "unknown question"):
            build_context_packet(fixture(), "Q-MISSING", seed="00000003")

    def test_rereading_session_with_empty_output_arrays_validates_and_maps(self) -> None:
        """The real schema and map pipeline allow completing without new works."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            for directory in ("state", "schema", "tools"):
                shutil.copytree(ROOT / directory, repo / directory)
            # read_log may target prose under readings/ (type reading_note).
            # The real validator resolves those ids against the files, so a
            # minimal copy must bring along just the notes actually cited.
            read_log_files = [repo / "state" / "read_log.jsonl", *sorted((repo / "state" / "read_log.d").glob("*.jsonl"))]
            for ledger in read_log_files:
                if not ledger.is_file():
                    continue
                for line in ledger.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    target = json.loads(line).get("target") or {}
                    if target.get("type") != "reading_note":
                        continue
                    rel = str(target.get("id") or "")
                    source = ROOT / rel
                    dest = repo / rel
                    if rel.startswith("readings/") and source.is_file():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, dest)
            session = {
                "session_id": "SESSION-TEST-REREAD",
                "started_at": "2026-10-28",
                "generator": "test fixture",
                "question_ids": ["Q-001"],
                "human_direction": "test fixture only",
                "context_material_ids": [],
                "prompt_template": "prompts/start.md",
                "produced_fragment_ids": [],
                "new_question_ids": [],
                "notes": "Test fixture: reread, retained the prior interpretation, no new work.",
            }
            shard = repo / "state" / "sessions.d" / "2026-10-28-test.jsonl"
            shard.parent.mkdir(exist_ok=True)
            shard.write_text(json.dumps(session) + "\n", encoding="utf-8")
            for command in (
                ("tools/validate_seed.py",),
                ("tools/map_build.py",),
                ("tools/inspect_inquiry.py", "--check-map"),
            ):
                with self.subTest(command=command):
                    proc = subprocess.run(
                        [sys.executable, *command], cwd=repo,
                        capture_output=True, text=True,
                    )
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            manifest = json.loads((repo / "map" / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue((repo / "READING_MAP.md").is_file())
            session_text = "\n".join(
                (repo / "map" / entry["file"]).read_text(encoding="utf-8")
                for entry in manifest["shards"] if entry["kind"] == "sessions"
            )
            self.assertIn("SESSION-TEST-REREAD", session_text)


if __name__ == "__main__":
    unittest.main()
