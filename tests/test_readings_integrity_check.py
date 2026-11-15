"""Tests for tools/readings_integrity_check.py.

Why this file exists
--------------------
On 2026-11-15 an experiment truncated every ``readings/*.md`` to 0 bytes
(30,180,380 B) and all nine gates still passed
(readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md
§3.4.1).  The prose was guarded by nothing but git history.  These tests pin the
three things the new gate must catch -- a body that is gone, a body that lost its
heading, and a note row that points at a file which is not there -- and the two
things it must NOT catch: prose that was legitimately rewritten, and a non-``.md``
target, which is only existence-checked.

Nothing here pins a live count.  Every assertion runs on a temporary fixture, so
writing to the archive cannot break these tests.
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import readings_integrity_check as ric  # noqa: E402

BODY = "# 報告の題\n\n本文がここにある。測定した。\n"


def build_root(tmp: str, bodies: dict[str, str], notes: list[dict] | None = None,
               extra_files: dict[str, str] | None = None) -> Path:
    """Create a minimal repository root: readings/ bodies plus note rows."""
    root = Path(tmp) / "repo"
    (root / "readings").mkdir(parents=True)
    (root / "state").mkdir(parents=True)
    for name, text in bodies.items():
        (root / "readings" / name).write_text(text, encoding="utf-8")
    for name, text in (extra_files or {}).items():
        (root / "readings" / name).write_text(text, encoding="utf-8")
    rows = notes if notes is not None else [
        {"note_id": f"NOTE-20261115-{i:06x}", "path": f"readings/{name}"}
        for i, name in enumerate(sorted(bodies))
    ]
    (root / "state" / "notes.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return root


def run_main(root: Path) -> tuple[int, str]:
    out = io.StringIO()
    with redirect_stdout(out):
        rc = ric.main(["--root", str(root)])
    return rc, out.getvalue()


class HealthyTreeTests(unittest.TestCase):
    def test_bodies_with_headings_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": BODY, "b.md": "# 別の題\n\n本文。\n"})
            report = ric.audit(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["violation_count"], 0)
            self.assertEqual(report["md_file_count"], 2)
            rc, text = run_main(root)
            self.assertEqual(rc, 0)
            self.assertIn("PASS: 0 readings/*.md with no body", text)

    def test_a_root_without_readings_refuses_to_guess(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "state").mkdir(parents=True)
            out = io.StringIO()
            with redirect_stdout(out):
                rc = ric.main(["--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("CANNOT CHECK", out.getvalue())


class ErasureTests(unittest.TestCase):
    def test_zero_byte_body_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": "", "b.md": BODY})
            report = ric.audit(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual([row["path"] for row in report["blank_body"]], ["readings/a.md"])
            rc, _ = run_main(root)
            self.assertEqual(rc, 1)

    def test_whitespace_only_body_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": "\n\n   \n\t\n", "b.md": BODY})
            self.assertEqual([r["path"] for r in ric.audit(root)["blank_body"]], ["readings/a.md"])

    def test_body_without_a_heading_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": "見出しを失った本文だけがここにある。\n", "b.md": BODY})
            report = ric.audit(root)
            self.assertEqual([r["path"] for r in report["no_h1"]], ["readings/a.md"])
            self.assertEqual(report["blank_body"], [])

    def test_the_round_5_total_erasure_is_caught(self) -> None:
        """Every body gone: the violation count is the file count.

        This is the exact shape the nine gates passed on 2026-11-15.
        """
        with tempfile.TemporaryDirectory() as tmp:
            bodies = {f"r{i:03d}.md": BODY for i in range(7)}
            root = build_root(tmp, bodies)
            for path in (root / "readings").glob("*.md"):
                path.write_text("", encoding="utf-8")
            report = ric.audit(root)
            self.assertEqual(report["md_file_count"], 7)
            self.assertEqual(report["md_total_bytes"], 0)
            self.assertEqual(len(report["blank_body"]), 7)
            self.assertEqual(report["violation_count"], 7)
            rc, text = run_main(root)
            self.assertEqual(rc, 1)
            self.assertIn("FAIL: 7 readings/*.md with no body", text)

    def test_one_blank_report_among_many_is_still_caught(self) -> None:
        """The realistic accident: a single body lost among healthy ones."""
        with tempfile.TemporaryDirectory() as tmp:
            bodies = {f"r{i:03d}.md": BODY for i in range(6)}
            bodies["lost.md"] = ""
            root = build_root(tmp, bodies)
            report = ric.audit(root)
            self.assertEqual(len(report["blank_body"]), 1)
            self.assertEqual(report["blank_body"][0]["path"], "readings/lost.md")
            self.assertEqual(report["md_file_count"], 7)


class MissingTargetTests(unittest.TestCase):
    def test_note_row_pointing_at_an_absent_file_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(
                tmp,
                {"a.md": BODY},
                notes=[
                    {"note_id": "NOTE-20261115-aaaaaa", "path": "readings/a.md"},
                    {"note_id": "NOTE-20261115-bbbbbb", "path": "readings/deleted.md"},
                ],
            )
            report = ric.audit(root)
            self.assertEqual(len(report["missing_target"]), 1)
            self.assertEqual(report["missing_target"][0]["note_id"], "NOTE-20261115-bbbbbb")
            rc, text = run_main(root)
            self.assertEqual(rc, 1)
            self.assertIn("NOTE-20261115-bbbbbb -> readings/deleted.md", text)

    def test_non_md_targets_are_existence_checked_only(self) -> None:
        """readings/ legitimately holds data files; an empty one is not a blank body."""
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(
                tmp,
                {"a.md": BODY},
                notes=[
                    {"note_id": "NOTE-20261115-aaaaaa", "path": "readings/a.md"},
                    {"note_id": "NOTE-20261115-cccccc", "path": "readings/data.tsv"},
                ],
                extra_files={"data.tsv": ""},
            )
            report = ric.audit(root)
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(report["distinct_non_md_paths_named_by_notes"], 1)
            self.assertEqual(report["non_md_paths"], ["readings/data.tsv"])

    def test_a_missing_non_md_target_is_still_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(
                tmp,
                {"a.md": BODY},
                notes=[{"note_id": "NOTE-20261115-dddddd", "path": "readings/gone.json"}],
            )
            report = ric.audit(root)
            self.assertEqual(len(report["missing_target"]), 1)

    def test_files_no_note_row_names_are_reported_not_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": BODY, "unregistered.md": BODY}, notes=[
                {"note_id": "NOTE-20261115-aaaaaa", "path": "readings/a.md"},
            ])
            report = ric.audit(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["md_files_never_named_by_a_note"], ["readings/unregistered.md"])


class RewrittenProseTests(unittest.TestCase):
    def test_a_rewritten_body_still_passes(self) -> None:
        """The gate must not demand byte preservation: prose is edited on purpose."""
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": BODY})
            self.assertEqual(ric.audit(root)["status"], "PASS")
            (root / "readings" / "a.md").write_text(
                "# 書き直された題\n\n## §12 追記\n\n全く別の本文。\n", encoding="utf-8"
            )
            self.assertEqual(ric.audit(root)["status"], "PASS")


class OutputTests(unittest.TestCase):
    def test_json_carries_the_status_and_the_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": BODY, "b.md": ""})
            out = io.StringIO()
            with redirect_stdout(out):
                rc = ric.main(["--root", str(root), "--json"])
            self.assertEqual(rc, 1)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["status"], "FAIL")
            self.assertEqual(payload["md_file_count"], 2)
            self.assertEqual(len(payload["blank_body"]), 1)
            self.assertIn("md_total_bytes", payload)

    def test_the_report_says_what_it_does_not_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_root(tmp, {"a.md": BODY})
            _, text = run_main(root)
            self.assertIn("does not check that it is unchanged", text)


if __name__ == "__main__":
    unittest.main()
