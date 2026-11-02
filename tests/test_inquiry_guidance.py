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
    MATERIAL_SECTION_BUDGET,
    build_context_packet,
    material_block,
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
            # readings/ is part of the fixture, not decoration: state/notes.d/
            # holds curated rows whose `path` is a foreign key into readings/, so
            # validate_seed.py checks those files exist.  Copying only the
            # referenced files would make this test break every time a new note
            # row is registered.
            for directory in ("state", "schema", "tools", "readings"):
                shutil.copytree(ROOT / directory, repo / directory)
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


def budget_fixture(count: int = 5, passage_chars: int = 400) -> dict:
    """A question linked to ``count`` materials whose blocks have known sizes.

    Sizes are controlled through the passage only; the scaffold (title, authors,
    kind, url, invitation, version, verification, scope note) is what every
    material pays regardless, and on the real corpus that scaffold -- not the
    passage -- is what multiplies (43 materials x ~1,290 B).
    """
    order = [f"MAT-{i:03d}" for i in range(count)]
    materials = {}
    for mid in order:
        materials[mid] = {
            "material_id": mid,
            "kind": "literary_text",
            "title": f"Source {mid}",
            "source": {
                "authors": ["Test author"],
                "year": 1900,
                "url": f"https://example.org/{mid}",
                "version_note": "編者要約",
            },
            "passage": f"{mid} " + "あ" * passage_chars,
            "context": "第1章",
            "source_note": "",
            "verification": {"status": "partially_verified"},
            "scope_note": f"留保 {mid}",
            "literary_invitation": "この要約では何が抜けるか",
            "motif_ids": [],
        }
    question = {
        "question_id": "Q-001",
        "question": "人間とは何か",
        "status": "open",
        "origin": {"kind": "human_seed", "detail": "test fixture"},
        "previous_question_ids": [],
        "motif_ids": [],
        "material_ids": list(order),
    }
    return {
        "questions": {"Q-001": question},
        "materials": materials,
        "fragments": {},
        "motifs": {},
        "relations": {},
        "sessions": {},
        "editorial_decisions": {},
        "read_log": {},
    }, order


def block_size(data: dict, mid: str) -> int:
    """Bytes one §3 block costs, measured with the renderer itself."""
    block = material_block(mid, data["materials"][mid], {})
    return len(("\n".join(block) + "\n").encode("utf-8"))


def section_three(packet: str) -> str:
    """The §3 slice of a packet, up to the next section heading."""
    lines = packet.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## 3."))
    end = next((i for i, l in enumerate(lines[start + 1:], start + 1) if l.startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


class MaterialBudgetTests(unittest.TestCase):
    """§3 is the only evidence section that grew without limit.

    These fix the behaviour measured on the real corpus at commit d133bbe,
    before the budget existed: packet max 82,727 B, §3 max 55,631 B, 28 of 408
    questions over 48 KB.  The budget trims the tail and must not reorder,
    split or silently drop anything.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        # An empty readings/ keeps the harvest hermetic: §4.7 must not read the
        # real 410 reports while testing §3.
        self.root = Path(self._tmp.name)
        (self.root / "readings").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def packet(self, data: dict, *, budget: int, seed: str = "00000001") -> str:
        return build_context_packet(
            data, "Q-001", seed=seed, errata={}, root=self.root, material_budget=budget
        )

    def test_zero_budget_is_unlimited_and_prints_no_note(self) -> None:
        data, order = budget_fixture(count=6)
        packet = self.packet(data, budget=0)
        for mid in order:
            self.assertIn(f"### `{mid}`", packet)
        self.assertNotIn("予算注記", packet)

    def test_default_budget_keeps_a_ledger_order_prefix(self) -> None:
        data, order = budget_fixture(count=6)
        sizes = [block_size(data, m) for m in order]
        budget = sizes[0] + sizes[1]
        packet = self.packet(data, budget=budget)
        for mid in order[:2]:
            self.assertIn(f"### `{mid}`", packet)
        for mid in order[2:]:
            self.assertNotIn(f"### `{mid}`", packet)

    def test_omitted_materials_are_named_with_the_command_to_fetch_them(self) -> None:
        """Reachability into the archive survives the budget; bytes do not."""
        data, order = budget_fixture(count=6)
        sizes = [block_size(data, m) for m in order]
        packet = self.packet(data, budget=sizes[0] + sizes[1])
        note = [l for l in packet.splitlines() if "予算注記" in l]
        self.assertEqual(len(note), 1, packet)
        for mid in order[2:]:
            self.assertIn(f"`{mid}`", note[0])
        self.assertIn("対話素材 6 件", note[0])
        self.assertIn("台帳順の先頭 2 件", note[0])
        self.assertIn("窓外の 4 件", note[0])
        self.assertIn("--id", packet)
        self.assertIn("価値や関連度の判断ではなく", packet)

    def test_blocks_are_carried_whole_never_split(self) -> None:
        """A half-quoted passage could be mistaken for the full quote."""
        data, order = budget_fixture(count=5)
        sizes = [block_size(data, m) for m in order]
        packet = self.packet(data, budget=sizes[0] + sizes[1])
        for mid in order[:2]:
            self.assertIn(f"留保 {mid}", packet)          # last line of the block
            self.assertIn(data["materials"][mid]["passage"], packet)
        for mid in order[2:]:
            self.assertNotIn(f"留保 {mid}", packet)
            self.assertNotIn(data["materials"][mid]["passage"], packet)

    def test_first_material_is_carried_even_when_alone_over_budget(self) -> None:
        data, order = budget_fixture(count=4)
        packet = self.packet(data, budget=1)
        self.assertIn(f"### `{order[0]}`", packet)
        self.assertNotIn(f"### `{order[1]}`", packet)
        self.assertIn("予算注記", packet)

    def test_selection_is_prefix_not_best_fit(self) -> None:
        """A huge first material is kept and a tiny later one is dropped.

        Best-fit packing would do the opposite and make "which materials did I
        see" depend on passage lengths instead of on the question's own record.
        """
        data, order = budget_fixture(count=3, passage_chars=50)
        data["materials"][order[0]]["passage"] = "あ" * 4000   # huge, first
        budget = block_size(data, order[0])                    # fits only the first
        packet = self.packet(data, budget=budget)
        self.assertIn(f"### `{order[0]}`", packet)
        for mid in order[1:]:                                  # tiny, but later
            self.assertNotIn(f"### `{mid}`", packet)

    def test_section_three_stays_within_budget_when_it_trims(self) -> None:
        data, order = budget_fixture(count=8)
        budget = MATERIAL_SECTION_BUDGET
        packet = self.packet(data, budget=budget)
        carried = len(section_three(packet).encode("utf-8"))
        if "予算注記" in packet:
            first = block_size(data, order[0])
            self.assertLessEqual(carried, budget + first + 400)

    def test_section_three_does_not_move_with_the_branch_seed(self) -> None:
        """The evidence layer is seed-stable; only the recommendation layer moves.

        Measured on the real corpus: for Q-001 the evidence layer was byte
        identical across two branch seeds (45,163 B) while the recommendation
        layer moved 9,070 -> 10,520 B.  A budget on the whole packet would make
        the same question pass on one branch and fail on another, so the budget
        belongs on the evidence section.
        """
        data, _ = budget_fixture(count=6, passage_chars=900)
        budget = block_size(data, "MAT-000") * 3
        a = section_three(self.packet(data, budget=budget, seed="00000001"))
        b = section_three(self.packet(data, budget=budget, seed="00000002"))
        self.assertEqual(a, b)

    def test_same_input_and_seed_is_byte_identical(self) -> None:
        data, _ = budget_fixture(count=6)
        self.assertEqual(self.packet(data, budget=9000), self.packet(data, budget=9000))

    def test_question_without_materials_renders_an_empty_section_without_a_note(self) -> None:
        data, _ = budget_fixture(count=1)
        data["questions"]["Q-001"]["material_ids"] = []
        packet = self.packet(data, budget=MATERIAL_SECTION_BUDGET)
        self.assertIn("## 3. 対話素材", packet)
        self.assertNotIn("予算注記", packet)

    def test_cli_exposes_the_budget_flag(self) -> None:
        proc = subprocess.run(
            [sys.executable, "tools/inspect_inquiry.py", "--help"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--material-budget", proc.stdout)
        self.assertIn(str(MATERIAL_SECTION_BUDGET), proc.stdout)

if __name__ == "__main__":
    unittest.main()
