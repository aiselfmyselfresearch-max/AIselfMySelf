"""Tests for the atomic/--write path of tools/import_researchos.py."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import import_researchos  # noqa: E402


class ImportWriteTests(unittest.TestCase):
    def test_write_reports_wrote_without_a_dry_run_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            materials = root / "state" / "materials.jsonl"
            manifest = root / "migration" / "manifest.json"
            materials.parent.mkdir(parents=True)
            manifest.parent.mkdir(parents=True)
            materials.write_text("", encoding="utf-8")

            expected_materials = '{"material_id": "MAT-LIT-001"}\n'
            expected_manifest = json.dumps({"selected_evidence_ids": ["EVD-001"]}) + "\n"

            output = io.StringIO()
            with mock.patch.object(import_researchos, "MATERIALS_PATH", materials), mock.patch.object(
                import_researchos, "MANIFEST_PATH", manifest
            ), mock.patch.object(import_researchos, "KIT_ROOT", root), mock.patch.object(
                import_researchos,
                "build_outputs",
                return_value={materials: expected_materials, manifest: expected_manifest},
            ):
                with contextlib.redirect_stdout(output):
                    code = import_researchos.main(
                        ["--source-root", str(root / "upstream"), "--write"]
                    )

            self.assertEqual(code, 0)
            printed = output.getvalue()
            self.assertIn("WROTE", printed)
            self.assertNotIn("DRY RUN", printed)
            self.assertEqual(materials.read_text(encoding="utf-8"), expected_materials)
            self.assertEqual(manifest.read_text(encoding="utf-8"), expected_manifest)

    def test_empty_materials_shard_does_not_block_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            materials = root / "state" / "materials.jsonl"
            manifest = root / "migration" / "manifest.json"
            materials.parent.mkdir(parents=True)
            manifest.parent.mkdir(parents=True)
            materials.write_text("", encoding="utf-8")
            shard_dir = materials.with_name("materials.d")
            shard_dir.mkdir()
            (shard_dir / "2026-10-21-aaaaaaaaaaaa.jsonl").write_text("", encoding="utf-8")

            expected_materials = '{"material_id": "MAT-LIT-001"}\n'
            expected_manifest = json.dumps({"selected_evidence_ids": ["EVD-001"]}) + "\n"

            with mock.patch.object(import_researchos, "MATERIALS_PATH", materials), mock.patch.object(
                import_researchos, "MANIFEST_PATH", manifest
            ), mock.patch.object(import_researchos, "KIT_ROOT", root), mock.patch.object(
                import_researchos,
                "build_outputs",
                return_value={materials: expected_materials, manifest: expected_manifest},
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = import_researchos.main(
                        ["--source-root", str(root / "upstream"), "--write"]
                    )
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
