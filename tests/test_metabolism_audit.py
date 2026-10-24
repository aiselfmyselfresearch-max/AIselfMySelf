#!/usr/bin/env python3
"""Unit tests for tools/metabolism_audit.py."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import metabolism_audit  # noqa: E402


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


class MetabolismAuditTests(unittest.TestCase):
    def _make_mini_repo(self, tmp: Path) -> Path:
        state = tmp / "state"
        readings = tmp / "readings"
        readings.mkdir(parents=True, exist_ok=True)

        _write_jsonl(
            state / "materials.jsonl",
            [
                {"material_id": "MAT-1", "title": "One"},
                {"material_id": "MAT-2", "title": "Two"},
            ],
        )
        _write_jsonl(
            state / "materials.d" / "2026-10-24-a.jsonl",
            [{"material_id": "MAT-3", "title": "Three (isolated shard)"}],
        )
        _write_jsonl(
            state / "motifs.jsonl",
            [
                {"motif_id": "MOTIF-1", "label": "Covered motif"},
                {"motif_id": "MOTIF-2", "label": "Uncovered motif"},
            ],
        )
        _write_jsonl(
            state / "questions.jsonl",
            [
                {"question_id": "Q-1", "origin": "session", "question": "Connected?", "material_ids": ["MAT-1"]},
                {"question_id": "Q-2", "origin": "session", "question": "Isolated?", "material_ids": []},
            ],
        )
        _write_jsonl(
            state / "fragments.jsonl",
            [
                {
                    "fragment_id": "FRAG-1",
                    "status": "selected",
                    "form": "essay",
                    "title": "First",
                    "material_ids": ["MAT-1"],
                    "motif_ids": ["MOTIF-1"],
                    "question_ids": ["Q-1"],
                }
            ],
        )
        _write_jsonl(
            state / "relations.jsonl",
            [
                {
                    "relation_id": "REL-1",
                    "left": {"type": "fragment", "id": "FRAG-1"},
                    "relation_type": "responds_to",
                    "right": {"type": "question", "id": "Q-1"},
                },
                {
                    "relation_id": "REL-2",
                    "left": {"type": "material", "id": "MAT-1"},
                    "relation_type": "grounds",
                    "right": {"type": "motif", "id": "MOTIF-1"},
                },
                {
                    "relation_id": "REL-3",
                    "left": {"type": "material", "id": "MAT-2"},
                    "relation_type": "grounds",
                    "right": {"type": "motif", "id": "MOTIF-2"},
                },
            ],
        )
        _write_jsonl(
            state / "sessions.jsonl",
            [{"session_id": "S-1", "produced_fragment_ids": ["FRAG-1"], "opened_question_ids": ["Q-1"]}],
        )
        _write_jsonl(
            state / "sessions.d" / "2026-10-24-s2.jsonl",
            [{"session_id": "S-2", "produced_fragment_ids": [], "opened_question_ids": ["Q-2"]}],
        )
        (readings / "2026-10-24-s2.md").write_text(
            "# Report\n\n## 5. 断片を書かなかった理由と、次回の種\n\n- 種A「白紙のテスト」\n",
            encoding="utf-8",
        )
        return tmp

    def test_union_and_base_only_counts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._make_mini_repo(Path(td))
            union = metabolism_audit.analyze(root=repo, base_only=False)
            self.assertEqual(union["counts"]["materials"], 3)
            self.assertEqual(union["sessions_summary"]["with_fragments"], 1)
            self.assertEqual(union["sessions_summary"]["without_fragments"], 1)
            self.assertEqual(union["sessions_summary"]["trailing_zero_fragment_shards"], 1)
            self.assertEqual(union["material_digestion"]["referenced_by_fragments"], 1)
            self.assertEqual(
                union["material_digestion"]["isolated_in_relations_by_shard"],
                {"2026-10-24-a.jsonl": 1},
            )
            self.assertEqual(union["motif_coverage"]["zero_direct_fragments_count"], 1)
            self.assertEqual(
                union["motif_coverage"]["zero_direct_fragments"][0]["motif_id"],
                "MOTIF-2",
            )
            self.assertEqual(union["graph_reciprocity"]["isolated_questions_count"], 1)
            self.assertEqual(
                union["graph_reciprocity"]["isolated_questions"][0]["question_id"],
                "Q-2",
            )
            self.assertEqual(union["graph_reciprocity"]["fragments_incoming_zero_count"], 1)
            self.assertEqual(union["graph_reciprocity"]["fragments_outgoing_zero_count"], 0)
            self.assertEqual(
                union["deferred_seeds_in_readings"]["reports_with_deferred_section"],
                1,
            )

            base = metabolism_audit.analyze(root=repo, base_only=True)
            self.assertEqual(base["counts"]["materials"], 2)
            self.assertEqual(base["material_digestion"]["isolated_in_relations"], 0)
            self.assertEqual(base["sessions_summary"]["shard_sessions_total"], 0)

    def test_real_repository_runs_cleanly(self) -> None:
        res = metabolism_audit.analyze(root=ROOT, base_only=False)
        self.assertGreaterEqual(res["counts"]["materials"], 1400)
        self.assertGreaterEqual(res["counts"]["motifs"], 37)
        text = metabolism_audit.format_report(res)
        self.assertIn("=== Metabolism Audit (union) ===", text)


if __name__ == "__main__":
    unittest.main()
