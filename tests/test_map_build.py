import json
import tempfile
import unittest
from pathlib import Path

from tools import map_build


def sample_data() -> dict:
    def question(qid, prevs, text):
        return {
            "question_id": qid,
            "question": text,
            "status": "open",
            "created_at": "2026-10-24",
            "origin": {"kind": "session", "detail": "t"},
            "motif_ids": [],
            "material_ids": [],
            "previous_question_ids": prevs,
        }

    questions = {
        "Q-001": question("Q-001", [], "根の問い。" * 30),
        "Q-002": question("Q-002", ["Q-001"], "子の問いその一。"),
        "Q-003": question("Q-003", ["Q-001", "Q-002"], "子の問いその二。"),
    }
    motifs = {
        "MOTIF-1": {
            "motif_id": "MOTIF-1",
            "label": "試験の糸",
            "description": "説明",
            "material_ids": [],
            "question_ids": ["Q-001"],
            "status": "active",
        }
    }
    materials = {
        "MAT-LIT-1": {
            "material_id": "MAT-LIT-1",
            "kind": "literary_text",
            "title": "試作",
            "source": {
                "source_id": "S1", "title": "試作", "authors": ["誰か"],
                "year": 2000, "url": "https://example.org", "version_note": "版",
            },
            "passage": "【編者による要約】要約。",
            "passage_language": "ja",
            "context": "箇所",
            "source_note": "メモ",
            "literary_invitation": "招き",
            "scope_note": "留保",
            "motif_ids": [],
            "origin": {
                "repository": "https://github.com/x/y", "commit": "abc1234",
                "source_record_id": "S1", "evidence_record_id": "E1",
                "source_record_path": "readings/a.md", "evidence_record_path": "readings/a.md",
            },
            "verification": {"status": "verified", "checked_at": "2026-10-24", "method": "m"},
        }
    }
    fragments = {
        "FRAG-001": {
            "fragment_id": "FRAG-001",
            "title": "試作断片",
            "status": "draft",
            "form": "essay",
            "narrator_mode": "reflective_literary_voice",
            "session_id": "SESSION-1",
            "question_ids": ["Q-001"],
            "motif_ids": [],
            "material_ids": [],
            "text": "本文の段落。\n\n二段落目。",
        }
    }
    relations = {
        "REL-001": {
            "relation_id": "REL-001",
            "left": {"type": "question", "id": "Q-001"},
            "relation_type": "leaves_open",
            "right": {"type": "question", "id": "Q-002"},
            "note": "備考",
            "created_at": "2026-10-24",
        }
    }
    sessions = {
        "SESSION-1": {
            "session_id": "SESSION-1",
            "started_at": "2026-10-24",
            "human_direction": "委任",
            "question_ids": ["Q-001"],
            "context_material_ids": [],
            "produced_fragment_ids": ["FRAG-001"],
            "new_question_ids": ["Q-002"],
            "prompt_template": "prompts/first_session.md",
            "notes": "メモ",
        }
    }
    return {
        "questions": questions, "motifs": motifs, "materials": materials,
        "fragments": fragments, "relations": relations, "sessions": sessions,
    }


class MapBuildTests(unittest.TestCase):
    def test_question_bodies_appear_exactly_once(self):
        data = sample_data()
        plan = map_build.shard_plan(data)
        body_text = ""
        for entry in plan:
            if entry["kind"] == "question_bodies":
                body_text += map_build.render_shard(data, entry)
        for qid, q in data["questions"].items():
            self.assertEqual(body_text.count(q["question"]), 1, qid)
        # the index keeps only truncated excerpts, never the full body
        index_text = map_build.build_index(data, {"shards": []})
        self.assertNotIn("根の問い。" * 30, index_text)
        self.assertIn("根の問い。", index_text)

    def test_dag_has_one_row_per_question(self):
        data = sample_data()
        rows = [line for line in map_build.build_question_index(data).splitlines() if line.startswith("| `Q-")]
        self.assertEqual(len(rows), len(data["questions"]))
        # a child with two parents lists both — still one row
        self.assertIn("`Q-001` `Q-002`", rows[2])

    def test_write_all_and_check_roundtrip(self):
        data = sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            map_dir = Path(tmp) / "map"
            index = Path(tmp) / "READING_MAP.md"
            manifest = map_build.write_all(data, map_dir, index, quiet=True)
            self.assertTrue((map_dir / "manifest.json").is_file())
            self.assertTrue(index.is_file())
            self.assertEqual(map_build.check_index(data, index), 0)
            # every manifest entry has a matching file and sha256
            import hashlib
            for shard in manifest["shards"]:
                text = (map_dir / shard["file"]).read_text(encoding="utf-8")
                self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), shard["sha256"])
            # tamper -> check fails
            index.write_text(index.read_text(encoding="utf-8") + "\n改ざん", encoding="utf-8")
            self.assertEqual(map_build.check_index(data, index), 1)

    def test_chunks_are_respected(self):
        data = sample_data()
        plan = map_build.shard_plan(data)
        for entry in plan:
            if entry["kind"] in ("question_bodies", "fragments", "materials", "relations", "sessions"):
                limit = map_build.CHUNKS[{"question_bodies": "questions", "fragments": "fragments",
                                          "materials": "materials", "relations": "relations",
                                          "sessions": "sessions"}[entry["kind"]]]
                self.assertLessEqual(len(entry["ids"]), limit, entry["file"])

    def test_manifest_records_counts(self):
        data = sample_data()
        with tempfile.TemporaryDirectory() as tmp:
            manifest = map_build.write_all(data, Path(tmp) / "map", Path(tmp) / "READING_MAP.md", quiet=True)
            self.assertEqual(manifest["counts"]["questions"], 3)
            self.assertEqual(manifest["counts"]["fragments"], 1)
            loaded = json.loads((Path(tmp) / "map" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded["counts"], manifest["counts"])


if __name__ == "__main__":
    unittest.main()
