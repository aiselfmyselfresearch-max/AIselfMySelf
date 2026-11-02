"""Tests for tools/note_index.py: the episodic index over readings/.

The point of these tests is the split the tool is built on — derived facts are
re-harvested from the files, curated judgments come from the append-only ``notes``
ledger and overlay in ledger order.  Both halves must stay deterministic, because
READING_MAP.md §8 is compared byte for byte by CI.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import note_index  # noqa: E402

BASE_COLLECTIONS = (
    "questions.jsonl",
    "motifs.jsonl",
    "materials.jsonl",
    "fragments.jsonl",
    "relations.jsonl",
    "sessions.jsonl",
    "read_log.jsonl",
    "editorial_decisions.jsonl",
    "errata.jsonl",
    "notes.jsonl",
)

SESSION_ROW = {
    "session_id": "SESSION-20261102-aaaaaa",
    "started_at": "2026-11-02",
    "human_direction": "委任",
    "question_ids": ["Q-001"],
    "context_material_ids": [],
    "produced_fragment_ids": [],
    "new_question_ids": [],
    "prompt_template": "prompts/start.md",
    "notes": "メモ",
}
QUESTION_ROW = {
    "question_id": "Q-001",
    "question": "人間とは何か。",
    "status": "open",
    "created_at": "2026-10-22",
    "origin": {"kind": "human_seed", "detail": "初期シード"},
    "motif_ids": [],
    "material_ids": [],
    "previous_question_ids": [],
}


def make_repo(tmp: Path, *, with_tools: bool = False) -> Path:
    """A minimal repository skeleton: empty ledgers, real schemas, a few notes."""
    root = Path(tmp) / "repo"
    (root / "state").mkdir(parents=True)
    (root / "readings").mkdir()
    shutil.copytree(ROOT / "schema", root / "schema")
    if with_tools:
        shutil.copytree(
            ROOT / "tools",
            root / "tools",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for filename in BASE_COLLECTIONS:
        (root / "state" / filename).write_text("", encoding="utf-8")
    (root / "state" / "sessions.jsonl").write_text(
        json.dumps(SESSION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / "state" / "questions.jsonl").write_text(
        json.dumps(QUESTION_ROW, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return root


def write_note(root: Path, name: str, body: str) -> Path:
    path = root / "readings" / name
    path.write_text(body, encoding="utf-8")
    return path


def sample_data(root: Path) -> dict:
    return {
        "questions": {"Q-001": QUESTION_ROW},
        "sessions": {"SESSION-20261102-aaaaaa": SESSION_ROW},
        "motifs": {},
        "materials": {},
        "fragments": {},
        "relations": {},
        "read_log": {},
        "editorial_decisions": {},
        "notes": {},
    }


NOTE_WITH_REAL_DATE = """# 北庇の油引き（SESSION-20261102-aaaaaa）

- **日付**：`2026-11-02`（実作業 UTC 日付。内部未来日付ラベルは採らない）
- **モード**：`editorial_review`（[`prompts/editorial_review.md`](../prompts/editorial_review.md)）

## 1. 本文

`Q-001` を読み直し、`SESSION-20261102-aaaaaa` の見立てを維持した。
先行ノート [`2026-10-22-breath.md`](2026-10-22-breath.md) と突き合わせた。
"""

NOTE_WITH_INTERNAL_DATE_ONLY = """# 索引だけが残る未来（SESSION-20261102-aaaaaa）

- **日付**：`2026-12-31`（台帳内部編年。既存シャードの辞書順に合わせた）

## 1. 本文

`Q-001` に触れる。
"""


class HarvestTests(unittest.TestCase):
    def test_derives_title_session_mode_and_known_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-oil-on-the-eaves.md", NOTE_WITH_REAL_DATE)
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-11-02-oil-on-the-eaves.md"]
            self.assertEqual(entry["title"], "北庇の油引き（SESSION-20261102-aaaaaa）")
            self.assertEqual(entry["date_label"], "2026-11-02")
            self.assertEqual(entry["date_real"], "2026-11-02")
            self.assertEqual(entry["date_real_source"], "日付+UTC注記")
            self.assertEqual(entry["mode"], "editorial_review")
            self.assertEqual(entry["session_ids"], ["SESSION-20261102-aaaaaa"])
            self.assertEqual(entry["refs"]["questions"], ["Q-001"])
            self.assertEqual(entry["outbound_notes"], ["2026-10-22-breath.md"])
            self.assertEqual(entry["headings"], ["## 1. 本文"])
            self.assertGreater(entry["chars"], 0)
            self.assertEqual(entry["bytes"], len(NOTE_WITH_REAL_DATE.encode("utf-8")))

    def test_internal_chronology_bullet_is_not_read_as_a_real_date(self) -> None:
        """A bare ``**日付**`` bullet usually carries the internal label, not the real date."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-12-31-future-index.md", NOTE_WITH_INTERNAL_DATE_ONLY)
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-12-31-future-index.md"]
            self.assertEqual(entry["date_label"], "2026-12-31")
            self.assertIsNone(entry["date_real"])
            self.assertIsNone(entry["date_real_source"])

    def test_unknown_id_tokens_are_reported_not_silently_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-dangling.md", "# 題\n\n`Q-999` と `FRAG-123456` を参照する。\n")
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-11-02-dangling.md"]
            self.assertEqual(entry["refs"].get("questions", []), [])
            self.assertIn("Q-999", entry["unknown_ids"])
            self.assertEqual(entry["unknown_id_count"], 2)

    def test_trailing_prose_after_an_id_still_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-suffix.md", "# 題\n\nQ-001-based な読み。\n")
            view = note_index.build_view(root, sample_data(root))
            self.assertEqual(view["readings/2026-11-02-suffix.md"]["refs"]["questions"], ["Q-001"])

    def test_harvest_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-a.md", NOTE_WITH_REAL_DATE)
            data = sample_data(root)
            first = json.dumps(note_index.build_view(root, data), ensure_ascii=False, sort_keys=True)
            second = json.dumps(note_index.build_view(root, data), ensure_ascii=False, sort_keys=True)
            self.assertEqual(first, second)


class ReachabilityTests(unittest.TestCase):
    def test_link_mention_and_orphan_are_distinguished(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-linked.md", "# リンクされた側\n")
            write_note(root, "2026-11-02-mentioned.md", "# 言及だけ\n")
            write_note(root, "2026-11-02-orphan.md", "# 孤立\n")
            (root / "README.md").write_text(
                "- [`readings/2026-11-02-linked.md`](readings/2026-11-02-linked.md)\n"
                "- 詳細は `readings/2026-11-02-mentioned.md` にある。\n",
                encoding="utf-8",
            )
            view = note_index.build_view(root, sample_data(root))
            self.assertTrue(view["readings/2026-11-02-linked.md"]["reachable"])
            self.assertEqual(view["readings/2026-11-02-linked.md"]["linked_from"], ["README.md"])
            self.assertTrue(view["readings/2026-11-02-mentioned.md"]["reachable"])
            self.assertEqual(view["readings/2026-11-02-mentioned.md"]["linked_from"], [])
            self.assertEqual(view["readings/2026-11-02-mentioned.md"]["mentioned_in"], ["README.md"])
            self.assertFalse(view["readings/2026-11-02-orphan.md"]["reachable"])
            self.assertEqual(
                [entry["path"] for entry in note_index.orphans(view)],
                ["readings/2026-11-02-orphan.md"],
            )

    def test_generated_index_does_not_make_a_note_reachable(self) -> None:
        """READING_MAP.md is generated *from* this index, so it must not count as a link."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-orphan.md", "# 孤立\n")
            (root / "READING_MAP.md").write_text(
                "| `readings/2026-11-02-orphan.md` | — | — | — | 1 | — | — | 孤立 |\n", encoding="utf-8"
            )
            view = note_index.build_view(root, sample_data(root))
            self.assertFalse(view["readings/2026-11-02-orphan.md"]["reachable"])

    def test_self_mention_does_not_make_a_note_reachable(self) -> None:
        """A report quoting *its own* path is not a route a reader can navigate from.

        Same reason READING_MAP.md is excluded: a report that reproduces its own
        path (a `mv readings/x.md /tmp/` recovery step, a self-citation) would
        otherwise mark itself reachable and shrink the orphan count that the
        metric exists to expose.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(
                root,
                "2026-11-02-self.md",
                "# 自己言及\n\n再現手順:\n\n```sh\n"
                "mv readings/2026-11-02-self.md /tmp/\n```\n",
            )
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-11-02-self.md"]
            self.assertFalse(entry["reachable"])
            self.assertEqual(entry["linked_from"], [])
            self.assertEqual(entry["mentioned_in"], [])
            self.assertEqual(
                [e["path"] for e in note_index.orphans(view)],
                ["readings/2026-11-02-self.md"],
            )

    def test_self_link_is_excluded_but_a_peer_link_still_counts(self) -> None:
        """The exclusion is about the *source*, not about links in general."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-self.md", "# 自分\n\n[自分](2026-11-02-self.md)\n")
            view = note_index.build_view(root, sample_data(root))
            self.assertFalse(view["readings/2026-11-02-self.md"]["reachable"])

            write_note(root, "2026-11-02-peer.md", "# 仲間\n\n[前](2026-11-02-self.md)\n")
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-11-02-self.md"]
            self.assertTrue(entry["reachable"])
            self.assertEqual(entry["linked_from"], ["readings/2026-11-02-peer.md"])

    def test_relative_link_from_a_peer_note_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-peer.md", "# 仲間\n\n[前](2026-11-02-target.md)\n")
            write_note(root, "2026-11-02-target.md", "# 対象\n")
            view = note_index.build_view(root, sample_data(root))
            self.assertEqual(
                view["readings/2026-11-02-target.md"]["linked_from"],
                ["readings/2026-11-02-peer.md"],
            )

    def test_absolute_github_link_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            (root / "taxonomy" / "notes").mkdir(parents=True)
            write_note(root, "2026-11-02-target.md", "# 対象\n")
            (root / "taxonomy" / "notes" / "U09-x.md").write_text(
                "[note](https://github.com/o/r/blob/main/readings/2026-11-02-target.md)\n", encoding="utf-8"
            )
            view = note_index.build_view(root, sample_data(root))
            entry = view["readings/2026-11-02-target.md"]
            self.assertTrue(entry["reachable"])
            self.assertEqual(entry["linked_from"], ["taxonomy/notes/U09-x.md"])

    def test_root_relative_link_from_docs_counts_as_a_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            (root / "docs").mkdir()
            write_note(root, "2026-11-02-target.md", "# 対象\n")
            (root / "docs" / "design.md").write_text(
                "[対象](../readings/2026-11-02-target.md)\n", encoding="utf-8"
            )
            view = note_index.build_view(root, sample_data(root))
            self.assertEqual(
                view["readings/2026-11-02-target.md"]["linked_from"], ["docs/design.md"]
            )

    def test_prompt_link_is_not_counted_as_an_outbound_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-a.md", "# 題\n\n[`prompts/editorial_review.md`](../prompts/editorial_review.md)\n")
            view = note_index.build_view(root, sample_data(root))
            self.assertEqual(view["readings/2026-11-02-a.md"]["outbound_notes"], [])


class CuratedOverlayTests(unittest.TestCase):
    def note_row(self, note_id: str, **overrides) -> dict:
        row = {
            "note_id": note_id,
            "path": "readings/2026-11-02-oil.md",
            "session_id": "SESSION-20261102-aaaaaa",
            "created_at": "2026-11-02",
        }
        row.update(overrides)
        return row

    def test_curated_fields_overlay_the_harvest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-oil.md", "# 題\n")
            data = sample_data(root)
            data["notes"] = {
                "NOTE-1": self.note_row(
                    "NOTE-1",
                    mode="editorial_review",
                    quadrant="B_ai_self_db",
                    return_status="returned_to_core",
                    read_depth="full_text_read",
                    salience=3,
                    claims=[
                        {
                            "claim_id": "CLM-1",
                            "kind": "reading_revised",
                            "text": "見立てを読み替えた。",
                            "anchor": "§4-2",
                            "question_ids": ["Q-001"],
                        }
                    ],
                )
            }
            entry = note_index.build_view(root, data)["readings/2026-11-02-oil.md"]
            self.assertEqual(entry["note_id"], "NOTE-1")
            self.assertEqual(entry["mode"], "editorial_review")
            self.assertEqual(entry["curated"]["quadrant"], "B_ai_self_db")
            self.assertEqual(entry["curated"]["claims"][0]["kind"], "reading_revised")
            self.assertEqual(entry["salience"], 3)

    def test_later_row_for_the_same_path_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-oil.md", "# 題\n")
            data = sample_data(root)
            data["notes"] = {
                "NOTE-1": self.note_row("NOTE-1", return_status="metaphor_unconnected"),
                "NOTE-2": self.note_row("NOTE-2", return_status="returned_to_core"),
            }
            entry = note_index.build_view(root, data)["readings/2026-11-02-oil.md"]
            self.assertEqual(entry["note_id"], "NOTE-2")
            self.assertEqual(entry["return_status"], "returned_to_core")
            self.assertEqual(entry["note_ids"], ["NOTE-1", "NOTE-2"])

    def test_explicit_supersedes_beats_a_forward_dated_ledger_order(self) -> None:
        """The ordering bug editorial_decisions already hit: an internal chronology
        label can sort after the real date that supersedes it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-oil.md", "# 題\n")
            data = sample_data(root)
            data["notes"] = {
                # forward-dated row comes FIRST in ledger order
                "NOTE-20261201": self.note_row(
                    "NOTE-20261201", created_at="2026-12-01", return_status="returned_to_core"
                ),
                "NOTE-20261102": self.note_row(
                    "NOTE-20261102",
                    created_at="2026-11-02",
                    return_status="metaphor_unconnected",
                    supersedes=["NOTE-20261201"],
                ),
            }
            ordered = note_index.order_note_rows(data["notes"])
            self.assertEqual([row["note_id"] for row in ordered], ["NOTE-20261201", "NOTE-20261102"])
            entry = note_index.build_view(root, data)["readings/2026-11-02-oil.md"]
            self.assertEqual(entry["return_status"], "metaphor_unconnected")

    def test_row_for_a_missing_file_stays_visible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            data = sample_data(root)
            data["notes"] = {"NOTE-1": self.note_row("NOTE-1", path="readings/2026-11-02-gone.md")}
            view = note_index.build_view(root, data)
            self.assertTrue(view["readings/2026-11-02-gone.md"]["missing_file"])
            self.assertEqual(note_index.summarize(view)["missing_files"], 1)


class IndexSectionTests(unittest.TestCase):
    def test_one_row_per_note_and_stable_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            for name in ("2026-11-02-a.md", "2026-11-02-b.md"):
                write_note(root, name, f"# {name}\n\n`Q-001`\n")
            view = note_index.build_view(root, sample_data(root))
            section = note_index.build_index_section(view)
            rows = [line for line in section if line.startswith("| `readings/")]
            self.assertEqual(len(rows), 2)
            self.assertEqual(section, note_index.build_index_section(view))
            self.assertIn(note_index.INDEX_SECTION_HEADING, section[0])
            # the index carries no body text, only one truncated title per row
            self.assertNotIn("## 1. 本文", "\n".join(section))

    def test_orphan_marker_and_counts_appear_in_the_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-orphan.md", "# 孤立\n")
            view = note_index.build_view(root, sample_data(root))
            text = "\n".join(note_index.build_index_section(view))
            self.assertIn("どの文書からもリンクされていないノート**：1 本", text)
            self.assertIn("| — | 孤立 |", text)

    def test_map_build_roundtrip_detects_a_new_note(self) -> None:
        """A new report makes the tracked index stale, and CI must say so."""
        sys.path.insert(0, str(ROOT / "tools"))
        import map_build

        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-a.md", "# 一\n")
            data = sample_data(root)
            index = root / "READING_MAP.md"
            map_build.write_all(data, root / "map", index, quiet=True)
            self.assertEqual(map_build.check_index(data, index), 0)
            self.assertTrue(note_index.section_is_current(root, index, note_index.build_view(root, data)))

            write_note(root, "2026-11-02-b.md", "# 二\n")
            self.assertEqual(map_build.check_index(data, index), 1)
            self.assertFalse(note_index.section_is_current(root, index, note_index.build_view(root, data)))
            map_build.write_all(data, root / "map", index, quiet=True)
            self.assertEqual(map_build.check_index(data, index), 0)
            notes_shards = sorted((root / "map").glob("60-notes-*.md"))
            self.assertEqual(len(notes_shards), 1)
            self.assertIn("readings/2026-11-02-b.md", notes_shards[0].read_text(encoding="utf-8"))


class NoteLookupTests(unittest.TestCase):
    def test_for_id_finds_notes_that_reference_a_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-hit.md", "# 当たり\n\n`Q-001` を読む。\n")
            write_note(root, "2026-11-02-miss.md", "# 外れ\n")
            view = note_index.build_view(root, sample_data(root))
            hits = note_index.notes_for_id(view, "Q-001")
            self.assertEqual([entry["path"] for entry in hits], ["readings/2026-11-02-hit.md"])

    def test_ranking_prefers_a_direct_hit_over_a_parent_hit(self) -> None:
        import inspect_inquiry

        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-direct.md", "# 直接\n\n`Q-002`\n")
            write_note(root, "2026-11-02-parent.md", "# 親\n\n`Q-001`\n")
            data = sample_data(root)
            data["questions"]["Q-002"] = {
                **QUESTION_ROW,
                "question_id": "Q-002",
                "question": "子の問い",
                "previous_question_ids": ["Q-001"],
            }
            hits = inspect_inquiry.related_notes(data, "Q-002", root=root)
            self.assertEqual(
                [entry["path"] for entry in hits],
                ["readings/2026-11-02-direct.md", "readings/2026-11-02-parent.md"],
            )

    def test_packet_carries_the_note_section(self) -> None:
        import inspect_inquiry

        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            write_note(root, "2026-11-02-direct.md", "# 直接\n\n`Q-001`\n")
            shutil.copytree(ROOT / "prompts", root / "prompts")
            data = note_index._load_ledgers(root)
            packet = inspect_inquiry.build_context_packet(data, "Q-001", seed="arena/aaaaaa-aiselfmyself", root=root)
            self.assertIn("## 4.7 関連する精読ノート", packet)
            self.assertIn("readings/2026-11-02-direct.md", packet)
            self.assertIn("開いて読んだノートだけ", packet)


class RegistrationTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args], cwd=root, capture_output=True, text=True, timeout=120
        )

    def test_candidates_are_printed_and_nothing_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), with_tools=True)
            write_note(root, "2026-11-02-a.md", NOTE_WITH_REAL_DATE)
            result = self.run_cli(root, "tools/note_index.py", "--candidates", "--date", "2026-11-02")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            row = json.loads(result.stdout.strip().splitlines()[0])
            self.assertTrue(row["note_id"].startswith("NOTE-20261102-"))
            self.assertEqual(row["path"], "readings/2026-11-02-a.md")
            self.assertEqual(row["read_depth"], "metadata_and_structure_only")
            self.assertEqual(row["date_real"], "2026-11-02")
            self.assertEqual(list((root / "state" / "notes.d").glob("*.jsonl")), [])

    def test_register_appends_a_row_and_refuses_a_second_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), with_tools=True)
            write_note(root, "2026-11-02-a.md", NOTE_WITH_REAL_DATE)
            result = self.run_cli(
                root,
                "tools/note_index.py",
                "--register",
                "readings/2026-11-02-a.md",
                "--session",
                "SESSION-20261102-aaaaaa",
                "--read-depth",
                "excerpt_and_metadata_read",
                "--date",
                "2026-11-02",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            shards = sorted((root / "state" / "notes.d").glob("*.jsonl"))
            self.assertEqual(len(shards), 1)
            row = json.loads(shards[0].read_text(encoding="utf-8").strip())
            self.assertEqual(row["path"], "readings/2026-11-02-a.md")
            self.assertEqual(row["session_id"], "SESSION-20261102-aaaaaa")
            self.assertEqual(row["read_depth"], "excerpt_and_metadata_read")
            self.assertEqual(row["report_session_id"], "SESSION-20261102-aaaaaa")
            self.assertEqual(row["mode"], "editorial_review")

            validation = self.run_cli(root, "tools/validate_seed.py")
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            self.assertIn("notes=1", validation.stdout)

            again = self.run_cli(
                root,
                "tools/note_index.py",
                "--register",
                "readings/2026-11-02-a.md",
                "--session",
                "SESSION-20261102-aaaaaa",
            )
            self.assertEqual(again.returncode, 1)
            self.assertIn("already has note row", again.stderr)

    def test_register_refuses_an_unknown_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), with_tools=True)
            result = self.run_cli(
                root,
                "tools/note_index.py",
                "--register",
                "readings/2026-11-02-nope.md",
                "--session",
                "SESSION-20261102-aaaaaa",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("no such report", result.stderr)

    def test_check_passes_after_a_rebuild_and_fails_after_a_new_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), with_tools=True)
            write_note(root, "2026-11-02-a.md", "# 一\n")
            self.assertEqual(self.run_cli(root, "tools/map_build.py").returncode, 0)
            self.assertEqual(self.run_cli(root, "tools/note_index.py", "--check").returncode, 0)
            write_note(root, "2026-11-02-b.md", "# 二\n")
            stale = self.run_cli(root, "tools/note_index.py", "--check")
            self.assertEqual(stale.returncode, 1)
            self.assertIn("STALE", stale.stderr)


if __name__ == "__main__":
    unittest.main()
