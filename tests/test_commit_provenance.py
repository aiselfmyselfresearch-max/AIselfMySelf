"""Tests for tools/commit_provenance.py.

The tool exists because `origin.repository` and `origin.commit` can be filled in
by two different acts and never checked against each other.  These tests build
a throwaway tree with (a) a record whose commit resolves in the named repo,
(b) a record whose commit resolves in a repo its source report names instead,
and (c) a record with prose in the hash field, then check that the three are
kept apart.

The online resolver is stubbed: no network is used by the test suite.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import commit_provenance  # noqa: E402

OWN = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
OTHER = "kumoi-no-fumigura/kyakuraika"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                    encoding="utf-8")


class CommitProvenanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "readings").mkdir()
        (self.root / "readings" / "r.md").write_text(
            f"底本は `kumoi-no-fumigura/sarugaku-dangi`（commit `9a2a3fe`）と"
            f" `{OTHER}`（commit `7763923`）。\n", encoding="utf-8")
        write_jsonl(self.root / "state" / "materials.jsonl", [
            {"material_id": "MAT-A", "origin": {"repository": OWN, "commit": "a" * 40,
                                                "source_record_path": "readings/r.md"}},
            {"material_id": "MAT-B", "origin": {"repository": OWN, "commit": "77639235" + "0" * 32,
                                                "source_record_path": "readings/r.md"}},
            {"material_id": "MAT-C", "origin": {"repository": OWN, "commit": "（web調査のため該当なし）",
                                                "source_record_path": "readings/r.md"}},
        ])

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_prose_in_hash_field_is_not_a_hash(self) -> None:
        result = commit_provenance.audit(self.root, online=False)
        self.assertEqual([x["material_id"] for x in result["not_a_hash"]], ["MAT-C"])

    def test_offline_reports_nothing_as_missing(self) -> None:
        # A shallow clone cannot answer "does this commit exist"; the tool must
        # withhold the answer instead of calling every old commit missing.
        result = commit_provenance.audit(self.root, online=False)
        self.assertEqual(result["clone_is_shallow"], True)
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["cross"], [])

    def test_cross_repository_pointer_is_found_from_the_report(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake(slug: str, sha: str):
            calls.append((slug, sha))
            if sha.startswith("77639235"):
                # Not in the repo the row names; present in one the report names.
                return {"status": "present", "repo": slug} if slug == OTHER else \
                       {"status": "absent", "repo": slug}
            return {"status": "present", "repo": slug}

        original = commit_provenance.resolve_online
        commit_provenance.resolve_online = fake
        try:
            result = commit_provenance.audit(self.root, online=True)
        finally:
            commit_provenance.resolve_online = original

        self.assertEqual([x["material_id"] for x in result["cross"]], ["MAT-B"])
        self.assertEqual(result["cross"][0]["found_in"], OTHER)
        self.assertEqual(result["missing"], [])
        # The resolvable row is probed exactly once, against the repo it names;
        # it must not be sent through the candidate list.
        a_calls = [slug for slug, sha in calls if sha == "a" * 40]
        self.assertEqual(a_calls, ["aiselfmyselfresearch-max/AIselfMySelf"])

    def test_candidate_extraction_reads_both_urls_and_bare_tokens(self) -> None:
        cands = commit_provenance.repo_candidates_from_report(self.root, "readings/r.md")
        self.assertIn("kumoi-no-fumigura/sarugaku-dangi", cands)
        self.assertIn(OTHER, cands)
        self.assertNotIn("aiselfmyselfresearch-max/AIselfMySelf", cands)


if __name__ == "__main__":
    unittest.main()
