"""Tests that `inspect_inquiry.py --id` shows the corrections filed beside a record.

The archive is append-only: an erratum never rewrites the record it corrects.
That design is only honest if the correction is visible at the moment a later
reader looks the record up. These tests pin the software behaviour of that
visibility, not the truth of any particular correction.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from inspect_inquiry import load_errata, print_record_detail  # noqa: E402


def fixture_data() -> dict:
    return {
        "materials": {
            "MAT-TEST-1": {
                "material_id": "MAT-TEST-1",
                "passage": "【編者による要約】答えない者は数に入らない。",
            }
        },
        "fragments": {
            "FRAG-TEST-1": {
                "fragment_id": "FRAG-TEST-1",
                "text": "「どれでもない」",
                "material_ids": ["MAT-TEST-1"],
            },
            "FRAG-TEST-2": {"fragment_id": "FRAG-TEST-2", "text": "訂正のない断片。"},
        },
        "relations": {},
    }


def erratum(errata_id: str, subject_id: str, **overrides) -> dict:
    record = {
        "errata_id": errata_id,
        "subject_type": "material",
        "subject_id": subject_id,
        "claim": "旧い読みは要約に依存していた。",
        "verdict": "unmeasurable",
        "status": "annotated",
        "created_at": "2026-12-23",
        "corrected_by": "SESSION-TEST / readings/example.md",
        "measured_now": "原典では明示的に否定していた。",
        "note": "既存行は書き換えない。",
    }
    record.update(overrides)
    return record


def capture(func, *args, **kwargs) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = func(*args, **kwargs)
    if code is None:
        return buffer.getvalue()
    return buffer.getvalue() + f"\n<exit {code}>"


class RecordDetailErrataTests(unittest.TestCase):
    def test_material_subject_shows_the_correction(self) -> None:
        out = capture(
            print_record_detail,
            fixture_data(),
            "MAT-TEST-1",
            {"ERR-TEST-1": erratum("ERR-TEST-1", "MAT-TEST-1")},
        )
        self.assertIn("Errata filed beside this record", out)
        self.assertIn("ERR-TEST-1", out)
        self.assertIn("[annotated/unmeasurable]", out)
        self.assertIn("旧い読みは要約に依存していた。", out)
        self.assertIn("corrected_by: SESSION-TEST / readings/example.md", out)

    def test_fragment_id_shortcut_is_followed(self) -> None:
        record = {
            "errata_id": "ERR-TEST-2",
            "fragment_id": "FRAG-TEST-1",
            "claim": "この断片の出典対応は原文に支えられない。",
            "verdict": "contradicted",
            "status": "annotated",
            "created_at": "2026-12-23",
            "note": "創作としては残す。",
        }
        out = capture(print_record_detail, fixture_data(), "FRAG-TEST-1", {"ERR-TEST-2": record})
        self.assertIn("ERR-TEST-2", out)
        self.assertIn("この断片の出典対応は原文に支えられない。", out)

    def test_record_without_errata_has_no_section(self) -> None:
        out = capture(
            print_record_detail,
            fixture_data(),
            "FRAG-TEST-2",
            {"ERR-TEST-1": erratum("ERR-TEST-1", "MAT-TEST-1")},
        )
        self.assertNotIn("Errata filed beside this record", out)
        self.assertIn("FRAG-TEST-2", out)

    def test_corrections_are_one_hop_only(self) -> None:
        """A fragment that cites a corrected material is not shown that correction."""
        out = capture(
            print_record_detail,
            fixture_data(),
            "FRAG-TEST-1",
            {"ERR-TEST-1": erratum("ERR-TEST-1", "MAT-TEST-1")},
        )
        self.assertNotIn("ERR-TEST-1", out)
        self.assertIn("MAT-TEST-1", out)


class LoadErrataTests(unittest.TestCase):
    def test_reads_base_and_shards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state"
            (state / "errata.d").mkdir(parents=True)
            base = {
                "errata_id": "ERR-BASE",
                "claim": "基底シャードの訂正。",
                "verdict": "holds",
                "status": "annotated",
                "created_at": "2026-10-24",
                "note": "test",
            }
            shard = {
                "errata_id": "ERR-SHARD",
                "subject_id": "FRAG-TEST-1",
                "claim": "追記シャードの訂正。",
                "verdict": "contradicted",
                "status": "open",
                "created_at": "2026-12-23",
                "note": "test",
            }
            (state / "errata.jsonl").write_text(
                json.dumps(base, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            (state / "errata.d" / "2026-12-23-test.jsonl").write_text(
                json.dumps(shard, ensure_ascii=False) + "\n", encoding="utf-8"
            )

            with redirect_stderr(io.StringIO()):
                records = load_errata(root)
        self.assertEqual(set(records), {"ERR-BASE", "ERR-SHARD"})

    def test_missing_ledger_returns_empty_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_errata(Path(tmp)), {})


if __name__ == "__main__":
    unittest.main()
