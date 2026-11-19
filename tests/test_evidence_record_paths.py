"""Tests for the evidence-record-path resolution gate (2026-11-19).

The gap these lock down: the ``notes`` ledger has checked since 2026-11-12 that
``path`` names an existing file, but the ``materials`` ledger — the collection whose
whole job is to carry the *evidence pointing* relationship — never did.  Ten rows
could therefore claim ``verified`` while ``origin.evidence_record_path`` named a
report that had been renamed, and no gate, schema, or tool noticed.  Measured in
``readings/2026-11-19-two-registers-of-the-same-dissociation.md`` §4 and repaired
in the same day's follow-up session.

None of these tests pin live ledger counts: they build small fixtures in a temp
root, so append-only growth cannot break them.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ledger_io  # noqa: E402
import validate_seed  # noqa: E402


def _material(material_id: str, evidence_path: str, *, status: str = "verified") -> dict:
    return {
        "material_id": material_id,
        "kind": "research_excerpt",
        "title": "t",
        "source": {
            "source_id": "SRC-" + material_id,
            "title": "t",
            "authors": ["a"],
            "year": 2000,
            "url": "https://example.org/x",
            "version_note": "v",
        },
        "passage": "p",
        "passage_language": "ja",
        "context": "c",
        "source_note": "s",
        "literary_invitation": "i",
        "scope_note": "s",
        "motif_ids": ["MOTIF-001"],
        "origin": {
            "repository": "https://github.com/example/repo",
            "commit": "0123456789abcdef",
            "source_record_id": "SRC-" + material_id,
            "evidence_record_id": material_id,
            "source_record_path": "https://example.org/x",
            "evidence_record_path": evidence_path,
        },
        "verification": {"status": status, "checked_at": "2026-11-19", "method": "m"},
    }


class EvidenceRecordPathGateTests(unittest.TestCase):
    """The gate must catch a new dead in-repo pointer, and only that."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "readings").mkdir()
        (self.root / "state").mkdir()
        self._orig_root = validate_seed.ROOT
        validate_seed.ROOT = self.root

    def tearDown(self) -> None:
        validate_seed.ROOT = self._orig_root
        self._tmp.cleanup()

    def _check(self, materials: dict[str, dict]) -> list[str]:
        errors: list[str] = []
        validate_seed.check_evidence_record_paths(materials, errors)
        return errors

    def test_new_row_with_dead_report_pointer_fails(self) -> None:
        materials = {"MAT-20261119-aaaaaa": _material("MAT-20261119-aaaaaa", "readings/gone.md")}
        errors = self._check(materials)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])
        self.assertIn("corrected_evidence_record_path", errors[0])

    def test_new_row_with_resolving_pointer_passes(self) -> None:
        (self.root / "readings" / "here.md").write_text("x", encoding="utf-8")
        materials = {"MAT-20261119-bbbbbb": _material("MAT-20261119-bbbbbb", "readings/here.md")}
        self.assertEqual(self._check(materials), [])

    def test_url_is_a_label_not_a_claim_about_the_checkout(self) -> None:
        materials = {"MAT-20261119-cccccc": _material("MAT-20261119-cccccc", "https://doi.org/10.1/x")}
        self.assertEqual(self._check(materials), [])

    def test_articles_cache_is_a_dead_in_repo_pointer(self) -> None:
        # ``articles/`` was a fetched-XML cache that is not in the checkout; 54 historical
        # rows point into it.  It is a repository path, not an outside-the-tree label, so
        # it stays inside the gate (those rows are counted against the legacy baseline).
        materials = {"MAT-20261119-dddddd": _material("MAT-20261119-dddddd", "articles/elife-1.xml")}
        self.assertEqual(len(self._check(materials)), 1)

    def test_pointer_outside_every_known_top_level_dir_is_only_labelled(self) -> None:
        materials = {"MAT-20261119-ffffff": _material("MAT-20261119-ffffff", "somedir/file.xml")}
        self.assertEqual(self._check(materials), [])

    def test_self_address_is_provenance_not_a_pointer(self) -> None:
        # A row may record where it was written; shard consolidation moves that file.
        materials = {
            "MAT-20261119-eeeeee": _material(
                "MAT-20261119-eeeeee", "state/materials.d/2026-10-24-4d62308ba2b3.jsonl"
            )
        }
        self.assertEqual(self._check(materials), [])

    def test_pre_rule_row_is_counted_not_failed(self) -> None:
        materials = {"MAT-20261024-ffffff": _material("MAT-20261024-ffffff", "readings/gone.md")}
        errors: list[str] = []
        legacy = validate_seed.check_evidence_record_paths(materials, errors)
        self.assertEqual(errors, [], "an old row must not fail the gate")
        self.assertEqual(legacy, 1, "but it must still be counted")

    def test_baseline_only_moves_down_when_it_grows_past_the_frozen_max(self) -> None:
        # Simulate the count exceeding the frozen baseline without building 1,000 rows.
        many = {
            f"MAT-20261024-{i:06x}": _material(f"MAT-20261024-{i:06x}", "readings/gone.md")
            for i in range(3)
        }
        errors: list[str] = []
        original = validate_seed.EVIDENCE_PATH_LEGACY_MAX
        validate_seed.EVIDENCE_PATH_LEGACY_MAX = 2
        try:
            validate_seed.check_evidence_record_paths(many, errors)
        finally:
            validate_seed.EVIDENCE_PATH_LEGACY_MAX = original
        self.assertEqual(len(errors), 1)
        self.assertIn("above the frozen baseline 2", errors[0])
        self.assertIn("baseline only moves down", errors[0])


class EvidencePathCorrectionTests(unittest.TestCase):
    """An overlay may repair a pointer; it may not create a second dead one."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "readings").mkdir()
        (self.root / "state").mkdir()
        (self.root / "readings" / "right-name.md").write_text("x", encoding="utf-8")
        self._orig_root = validate_seed.ROOT
        validate_seed.ROOT = self.root

    def tearDown(self) -> None:
        validate_seed.ROOT = self._orig_root
        self._tmp.cleanup()

    def _decision(self, path: str, material_id: str = "MAT-20261119-aaaaaa") -> dict:
        return {
            "decision_id": "ED-20261119-000000",
            "session_id": "SESSION-20261119-000000",
            "target": {"type": "material", "id": material_id},
            "status": "partially_verified",
            "corrected_evidence_record_path": path,
            "reason": "r",
            "created_at": "2026-11-19",
        }

    def _write_shard(self, material_id: str, recorded: str) -> dict[str, dict]:
        path = self.root / "state" / "materials.d" / "2026-11-19-shard.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_material(material_id, recorded)) + "\n", encoding="utf-8")
        # The loaded record carries the overlay already applied (ledger_io behaviour).
        loaded = _material(material_id, "readings/right-name.md")
        return {material_id: loaded}

    def _check(self, decisions: dict, materials: dict) -> list[str]:
        errors: list[str] = []
        validate_seed.check_evidence_path_corrections(decisions, materials, errors)
        return errors

    def test_a_real_repair_is_accepted(self) -> None:
        mid = "MAT-20261119-aaaaaa"
        materials = self._write_shard(mid, "readings/old-name.md")
        decisions = {"ED-20261119-000000": self._decision("readings/right-name.md", mid)}
        self.assertEqual(self._check(decisions, materials), [])

    def test_a_no_op_correction_is_rejected(self) -> None:
        # The snapshot already holds the correction, so a check against the snapshot
        # would call every repair a no-op; the gate must read the shard instead.
        mid = "MAT-20261119-aaaaaa"
        materials = self._write_shard(mid, "readings/right-name.md")
        decisions = {"ED-20261119-000000": self._decision("readings/right-name.md", mid)}
        errors = self._check(decisions, materials)
        self.assertEqual(len(errors), 1)
        self.assertIn("identical to the row's existing path", errors[0])

    def test_correction_to_a_missing_file_is_rejected(self) -> None:
        mid = "MAT-20261119-aaaaaa"
        materials = self._write_shard(mid, "readings/old-name.md")
        decisions = {"ED-20261119-000000": self._decision("readings/also-missing.md", mid)}
        errors = self._check(decisions, materials)
        self.assertEqual(len(errors), 1)
        self.assertIn("second dead pointer", errors[0])

    def test_correction_that_keeps_the_same_leaf_name_is_rejected(self) -> None:
        mid = "MAT-20261119-aaaaaa"
        materials = self._write_shard(mid, "readings/old-name.md")
        decisions = {"ED-20261119-000000": self._decision("readings/old-name.md", mid)}
        errors = self._check(decisions, materials)
        self.assertTrue(any("same file name" in e or "does not exist" in e for e in errors))

    def test_correction_on_a_non_material_target_is_rejected(self) -> None:
        decisions = {"ED-20261119-000000": self._decision("readings/right-name.md")}
        decisions["ED-20261119-000000"]["target"] = {"type": "question", "id": "Q-001"}
        errors = self._check(decisions, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("only valid for target type 'material'", errors[0])


class OverlayAppliesCorrectedPathTests(unittest.TestCase):
    """The overlay must change the path every consumer sees, keeping the original."""

    def test_corrected_path_replaces_origin_path(self) -> None:
        record = _material("MAT-20261119-aaaaaa", "readings/old-name.md")
        decision = {
            "decision_id": "ED-20261119-000000",
            "target": {"type": "material", "id": "MAT-20261119-aaaaaa"},
            "status": "partially_verified",
            "corrected_evidence_record_path": "readings/right-name.md",
            "reason": "renamed",
            "created_at": "2026-11-19",
        }
        out = ledger_io._apply_editorial_overlay(record, decision, "material", "partially_verified")
        self.assertEqual(out["origin"]["evidence_record_path"], "readings/right-name.md")
        self.assertEqual(
            record["origin"]["evidence_record_path"],
            "readings/old-name.md",
            "the caller's record (and so the shard on disk) must not be mutated",
        )
        self.assertEqual(out["verification"]["status"], "partially_verified")
        self.assertIn("renamed", out["verification"]["note"])

    def test_overlay_without_a_correction_leaves_the_path_alone(self) -> None:
        record = _material("MAT-20261119-aaaaaa", "readings/old-name.md", status="partially_verified")
        decision = {
            "decision_id": "ED-20261119-000000",
            "target": {"type": "material", "id": "MAT-20261119-aaaaaa"},
            "status": "verified",
            "verification_method": "PMC full text",
            "reason": "re-read",
            "created_at": "2026-11-19",
        }
        out = ledger_io._apply_editorial_overlay(record, decision, "material", "verified")
        self.assertEqual(out["origin"]["evidence_record_path"], "readings/old-name.md")
        self.assertEqual(out["verification"]["status"], "verified")


class DowngradeNeedsAMethodTests(unittest.TestCase):
    """An honest downgrade must say what the re-check found."""

    def _validate(self, status: str, method: str | None) -> list[str]:
        decision = {
            "decision_id": "ED-20261119-000000",
            "session_id": "SESSION-20261119-000000",
            "target": {"type": "material", "id": "MAT-20261119-aaaaaa"},
            "status": status,
            "reason": "r",
            "created_at": "2026-11-19",
        }
        if method is not None:
            decision["verification_method"] = method
        schema = json.loads((ROOT / "schema" / "editorial_decision.schema.json").read_text(encoding="utf-8"))
        errors: list[str] = []
        validate_seed.validate_value(decision, schema, schema, "editorial_decisions:ED", errors)
        return errors

    def test_unverified_without_a_method_is_rejected_by_the_schema_contract(self) -> None:
        # The rule lives in validate_seed's decision checks; this test pins the
        # schema-level shape so a future edit cannot quietly drop the field.
        schema = json.loads((ROOT / "schema" / "editorial_decision.schema.json").read_text(encoding="utf-8"))
        self.assertIn("corrected_evidence_record_path", schema["properties"])
        self.assertIn("verification_method", schema["properties"])

    def test_corrected_status_is_still_accepted_with_a_method(self) -> None:
        self.assertEqual(self._validate("corrected", "re-checked the pointer only"), [])


if __name__ == "__main__":
    unittest.main()
