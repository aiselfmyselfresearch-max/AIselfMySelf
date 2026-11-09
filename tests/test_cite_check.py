"""Report behaviour of tools/cite_check.py: it must never stop early.

The tool prints one line per material. On 2026-11-09 the report raised
``IndexError: list index out of range`` at the first row whose
``source.authors`` was an empty list — ten anonymous texts written on
2026-11-03. ``traceback`` ended the process, so the listing stopped at that
row and the later 700-plus materials, including ``project_trace`` rows whose
first "author" is the archive itself, were never printed. Dividing by zero
and indexing an empty list fail the same way: loudly, but only for whoever
runs the tool.

These tests pin the printed behaviour, not the truth of any citation.
"""
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cite_check  # noqa: E402


def material(mid: str, authors, title: str = "題", kind: str = "literary_text") -> dict:
    return {
        "material_id": mid,
        "kind": kind,
        "title": title,
        "source": {
            "source_id": "SRC-" + mid,
            "title": title,
            "authors": authors,
            "year": 2026,
            "url": "https://example.org/" + mid,
            "version_note": "test",
        },
        "verification": {"status": "verified", "checked_at": "2026-11-09", "method": "test"},
    }


class FirstAuthorTests(unittest.TestCase):
    def test_empty_author_list_gets_a_visible_marker(self):
        self.assertEqual(cite_check.first_author(material("MAT-T-1", [])), "（著者不記載）")

    def test_missing_authors_key_is_treated_as_empty(self):
        record = material("MAT-T-2", ["だれか"])
        del record["source"]["authors"]
        self.assertEqual(cite_check.first_author(record), "（著者不記載）")

    def test_named_author_is_returned_unchanged(self):
        self.assertEqual(cite_check.first_author(material("MAT-T-3", ["Konrad Lorenz"])), "Konrad Lorenz")

    def test_archive_as_author_is_returned_unchanged_not_hidden(self):
        record = material("MAT-TRC-T-4", ["AIselfMySelf Archive"], kind="project_trace")
        self.assertEqual(cite_check.first_author(record), "AIselfMySelf Archive")


class ReportDoesNotStopEarlyTests(unittest.TestCase):
    """A row with no author must not truncate the listing of the rows after it."""

    def setUp(self):
        self._saved = cite_check.load_materials

    def tearDown(self):
        cite_check.load_materials = self._saved

    def run_report(self, materials: dict[str, dict]) -> tuple[int, str]:
        cite_check.load_materials = lambda: materials
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cite_check.main([])
        return code, buffer.getvalue()

    def test_every_material_appears_even_after_an_anonymous_one(self):
        materials = {
            "MAT-T-AAA": material("MAT-T-AAA", [], "名のない祈り"),
            "MAT-T-BBB": material("MAT-T-BBB", ["だれか"], "二番目"),
            "MAT-TR-C": material("MAT-TR-C", [], "三番目", kind="project_trace"),
        }
        code, out = self.run_report(materials)
        self.assertEqual(code, 0)
        for mid in materials:
            self.assertIn(mid, out)
        # The marker is printed, not swallowed: an unnamed row is visible as unnamed.
        self.assertIn("（著者不記載）", out)

    def test_union_count_is_printed_not_the_base_file_count(self):
        materials = {f"MAT-T-{i:03d}": material(f"MAT-T-{i:03d}", ["x"]) for i in range(3)}
        code, out = self.run_report(materials)
        self.assertEqual(code, 0)
        self.assertIn("和集合", out)
        self.assertIn("3 件", out)


if __name__ == "__main__":
    unittest.main()
