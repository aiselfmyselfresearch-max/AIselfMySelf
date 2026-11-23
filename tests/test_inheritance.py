"""Tests for tools/inheritance.py — ledger-visible succession between reports.

The measurement this pins was made twice by hand and written into report text
("9,191行中2行", "9,238行中2行") without the scratch script that produced it.  If
those figures are to be re-runnable, three distinctions must not blur:

  * reading a **note row** is not reading a **session row**;
  * a session reading its **own** report is not a successor;
  * a prose citation is not a ledger row (it is reported, never added).
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

import inheritance  # noqa: E402

BASE = "2026-11-05"

SESSION_ROW = {
    "session_id": "SESSION-20261105-aaaaaa",
    "started_at": "2026-11-05",
    "human_direction": "委任",
    "question_ids": ["Q-001"],
    "context_material_ids": [],
    "produced_fragment_ids": [],
    "new_question_ids": [],
    "prompt_template": "prompts/start.md",
    "notes": "実作業日2026-11-05",
}
SUCCESSOR_ROW = dict(SESSION_ROW, session_id="SESSION-20261105-bbbbbb")
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


def note_row(note_id: str, path: str, session_id: str, *, date_real: str = BASE, **extra) -> dict:
    row = {
        "note_id": note_id,
        "path": path,
        "session_id": session_id,
        "report_session_id": session_id,
        "date_real": date_real,
        "created_at": date_real,
    }
    row.update(extra)
    return row


def read_row(read_id: str, session_id: str, target_type: str, target_id: str) -> dict:
    return {
        "read_id": read_id,
        "session_id": session_id,
        "target": {"type": target_type, "id": target_id},
        "reading": "interpreted",
        "note": "test",
        "created_at": BASE,
    }


def make_repo(tmp: Path, notes: list[dict], read_log: list[dict], reports: dict[str, str]) -> Path:
    root = Path(tmp) / "repo"
    (root / "state").mkdir(parents=True)
    (root / "readings").mkdir()
    shutil.copytree(ROOT / "schema", root / "schema")
    for name in (
        "questions", "motifs", "materials", "fragments", "relations",
        "sessions", "read_log", "editorial_decisions", "errata", "notes",
    ):
        (root / "state" / f"{name}.jsonl").write_text("", encoding="utf-8")
    (root / "state" / "questions.jsonl").write_text(
        json.dumps(QUESTION_ROW, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (root / "state" / "sessions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in (SESSION_ROW, SUCCESSOR_ROW)),
        encoding="utf-8",
    )
    (root / "state" / "notes.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in notes), encoding="utf-8"
    )
    (root / "state" / "read_log.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in read_log), encoding="utf-8"
    )
    for name, body in reports.items():
        (root / "readings" / name).write_text(body, encoding="utf-8")
    return root


class InheritanceTests(unittest.TestCase):
    def test_note_row_read_by_another_session_is_inheritance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                notes=[note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa")],
                read_log=[
                    read_row("READ-1", "SESSION-20261105-bbbbbb", "note", "NOTE-20261105-aaaaaa")
                ],
                reports={"a.md": "# A\n\n実日付 2026-11-05\n"},
            )
            rows, totals = inheritance.collect(root)
            report = next(row for row in rows if row.path == "readings/a.md")
            self.assertEqual(report.inherited, 1)
            self.assertEqual(report.successor_sessions, ["SESSION-20261105-bbbbbb"])
            self.assertEqual(totals["inherited_rows"], 1)

    def test_self_read_is_counted_apart_and_never_as_inheritance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                notes=[note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa")],
                read_log=[
                    read_row("READ-1", "SESSION-20261105-aaaaaa", "note", "NOTE-20261105-aaaaaa")
                ],
                reports={"a.md": "# A\n\n実日付 2026-11-05\n"},
            )
            rows, totals = inheritance.collect(root)
            report = next(row for row in rows if row.path == "readings/a.md")
            self.assertEqual(report.inherited, 0)
            self.assertEqual(report.self_reads, 1)
            self.assertEqual(totals["self_rows"], 1)
            self.assertEqual(totals["inherited_rows"], 0)

    def test_mentioned_session_is_not_assumed_to_be_the_report_author(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            author = "SESSION-20261105-aaaaaa"
            other = "SESSION-20261105-bbbbbb"
            target = "NOTE-20261105-aaaaaa"
            root = make_repo(
                Path(tmp), notes=[note_row(target, "readings/a.md", author)],
                read_log=[read_row("READ-1", other, "note", target)],
                reports={"a.md": f"# A\n\n実日付 2026-11-05\n\n{author} cites {other}.\n"},
            )
            rows, totals = inheritance.collect(root)
            self.assertIn(other, rows[0].session_ids)  # harvested mention, not authorship
            self.assertNotIn(other, rows[0].author_sessions)
            self.assertEqual(totals["self_rows"], 0)
            self.assertEqual(totals["inherited_rows"], 1)

    def test_session_target_rows_are_not_inheritance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                notes=[note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa")],
                read_log=[
                    read_row("READ-1", "SESSION-20261105-bbbbbb", "session", "SESSION-20261105-aaaaaa")
                ],
                reports={"a.md": "# A\n\n実日付 2026-11-05\n"},
            )
            rows, totals = inheritance.collect(root)
            report = next(row for row in rows if row.path == "readings/a.md")
            self.assertEqual(report.inherited, 0)
            self.assertEqual(totals["session_target_rows"], 1)

    def test_prose_citation_is_reported_but_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                notes=[
                    note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa"),
                    note_row("NOTE-20261105-bbbbbb", "readings/b.md", "SESSION-20261105-bbbbbb"),
                ],
                read_log=[],
                reports={
                    "a.md": "# A\n\n実日付 2026-11-05\n",
                    "b.md": "# B\n\n実日付 2026-11-05\n\n[a を読んだ](a.md)\n",
                },
            )
            rows, totals = inheritance.collect(root)
            report = next(row for row in rows if row.path == "readings/a.md")
            self.assertEqual(report.inherited, 0)
            self.assertEqual(report.prose_cited_by, ["readings/b.md"])
            self.assertEqual(totals["prose_edges"], 1)
            summary = inheritance.summarize(rows, totals)
            self.assertEqual(summary["inheriting_reports"], 0)
            self.assertEqual(summary["prose_cited_reports"], 1)

    def test_declined_note_rows_are_kept_but_never_counted_as_reading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = "NOTE-20261105-aaaaaa"
            author = "SESSION-20261105-aaaaaa"
            other = "SESSION-20261105-bbbbbb"
            negative = dict(read_row("READ-NEG", other, "note", target), reading="declined")
            self_negative = dict(read_row("READ-SELF-NEG", author, "note", target), reading="declined")
            root = make_repo(
                Path(tmp), notes=[note_row(target, "readings/a.md", author)],
                read_log=[negative, self_negative],
                reports={"a.md": "# A\n\n実日付 2026-11-05\n"},
            )
            rows, totals = inheritance.collect(root)
            self.assertEqual(rows[0].inherited, 0)
            self.assertEqual(rows[0].self_reads, 0)
            self.assertEqual(totals["declined_note_rows"], 2)
            self.assertEqual(totals["read_rows"], 0)
            self.assertEqual(len(inheritance.load_read_log(root)), 2)
            self.assertIn("readings/a.md", [r.path for r in inheritance.unread(rows)])

            # A valid replacement is one reading, not two; its negative remains.
            replacement = read_row("READ-REPLACEMENT", other, "note", target)
            with (root / "state" / "read_log.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(replacement) + "\n")
            rows, totals = inheritance.collect(root)
            self.assertEqual(rows[0].inherited, 1)
            self.assertEqual(totals["read_rows"], 1)
            self.assertEqual(totals["declined_note_rows"], 2)
            self.assertEqual(len(inheritance.load_read_log(root)), 3)

    def test_until_is_a_report_cohort_not_a_historical_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            note_a = note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa")
            note_b = note_row("NOTE-20261105-bbbbbb", "readings/b.md", "SESSION-20261105-bbbbbb",
                              date_real="2026-11-07")
            later_read = dict(read_row("READ-1", "SESSION-20261105-bbbbbb", "note", note_a["note_id"]),
                              created_at="2026-11-10")
            read_b = read_row("READ-2", "SESSION-20261105-aaaaaa", "note", note_b["note_id"])
            negative = dict(read_row("READ-3", "SESSION-20261105-bbbbbb", "note", note_a["note_id"]),
                            reading="declined")
            root = make_repo(
                Path(tmp), notes=[note_a, note_b], read_log=[later_read, read_b, negative],
                reports={"a.md": "# A\n\n実日付 2026-11-05\n",
                         "b.md": "# B\n\n実日付 2026-11-07\n\n[A](a.md)\n"},
            )
            rows, totals = inheritance.collect(root, until="2026-11-05")
            summary = inheritance.summarize(rows, totals)
            self.assertEqual([r.path for r in rows], ["readings/a.md"])
            self.assertEqual(summary["report_date_until"], "2026-11-05")
            self.assertEqual(summary["read_log_rows"], 3)  # explicitly whole ledger
            self.assertEqual(summary["note_target_rows"], 1)  # selected report only
            self.assertEqual(summary["inherited_rows"], 1)  # even though read after cutoff
            self.assertEqual(summary["declined_note_target_rows"], 1)
            self.assertEqual(summary["inherited_rows"],
                             sum(block["inherited_rows"] for block in inheritance.cohorts(rows)))
            self.assertEqual(summary["prose_cited_reports"], 1)  # citer outside cohort
            self.assertIn("スナップショットではない", inheritance.render(summary, inheritance.cohorts(rows)))

            empty, empty_totals = inheritance.collect(root, until="1900-01-01")
            self.assertEqual(empty, [])
            self.assertEqual(empty_totals["read_rows"], 0)
            self.assertEqual(empty_totals["inherited_rows"], 0)
            self.assertEqual(empty_totals["declined_note_rows"], 0)
            self.assertEqual(empty_totals["read_log_rows"], 3)

    def test_passive_and_interpretive_labels_are_reported_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa")
            b = note_row("NOTE-20261105-bbbbbb", "readings/b.md", "SESSION-20261105-aaaaaa")
            other = "SESSION-20261105-bbbbbb"
            reads = [
                dict(read_row("READ-A", other, "note", a["note_id"]), reading="used_as_context"),
                dict(read_row("READ-B1", other, "note", b["note_id"]), reading="counted"),
                dict(read_row("READ-B2", other, "note", b["note_id"]), reading="reinterpreted"),
            ]
            root = make_repo(Path(tmp), [a, b], reads,
                             {"a.md": "# A\n\n実日付 2026-11-05\n",
                              "b.md": "# B\n\n実日付 2026-11-05\n"})
            rows, totals = inheritance.collect(root)
            summary = inheritance.summarize(rows, totals)
            self.assertEqual(summary["inheriting_reports"], 2)
            self.assertEqual(summary["reports_with_active_trace"], 1)
            self.assertEqual(summary["reports_only_passive_traces"], 1)
            self.assertEqual(summary["reports_only_unclassified_or_mixed_unclassified"], 0)
            self.assertEqual(summary["other_session_rows_by_reading"],
                             {"counted": 1, "reinterpreted": 1, "used_as_context": 1})
            self.assertIn("台帳上のラベル", inheritance.render(summary, inheritance.cohorts(rows)))

    def test_invalid_until_is_rejected_by_api_and_cli(self) -> None:
        for bad in ("2026-02-30", "not-a-date", "20261105", ""):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                    inheritance.collect(until=bad)
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/inheritance.py"), "--until", "not-a-date", "--json"],
            text=True, capture_output=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("YYYY-MM-DD", result.stderr)
        self.assertFalse(result.stdout)

    def test_cohort_key_is_anchored_and_reproducible(self) -> None:
        self.assertEqual(inheritance.cohort_key("2026-10-22"), "2026-10-22..2026-10-27")
        self.assertEqual(inheritance.cohort_key("2026-10-27"), "2026-10-22..2026-10-27")
        self.assertEqual(inheritance.cohort_key("2026-10-28"), "2026-10-28..2026-11-02")
        self.assertEqual(inheritance.cohort_key(None), "未記録")

    def test_unread_excludes_cited_and_inherited_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                notes=[
                    note_row("NOTE-20261105-aaaaaa", "readings/a.md", "SESSION-20261105-aaaaaa"),
                    note_row("NOTE-20261105-bbbbbb", "readings/b.md", "SESSION-20261105-bbbbbb"),
                    note_row("NOTE-20261105-cccccc", "readings/c.md", "SESSION-20261105-aaaaaa"),
                ],
                read_log=[
                    read_row("READ-1", "SESSION-20261105-bbbbbb", "note", "NOTE-20261105-aaaaaa")
                ],
                reports={
                    "a.md": "# A\n\n実日付 2026-11-05\n",  # inherited
                    "b.md": "# B\n\n実日付 2026-11-05\n",  # nobody reads it
                    "c.md": "# C\n\n実日付 2026-11-05\n\n[d](b.md)\n",  # cites b
                },
            )
            rows, _ = inheritance.collect(root)
            found = [row.path for row in inheritance.unread(rows, limit=10)]
            self.assertNotIn("readings/a.md", found)
            self.assertNotIn("readings/b.md", found)  # cited by c
            self.assertIn("readings/c.md", found)


if __name__ == "__main__":
    unittest.main()
