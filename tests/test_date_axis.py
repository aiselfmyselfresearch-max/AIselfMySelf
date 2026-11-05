"""Tests for tools/date_axis.py — the one ordered time axis.

The tool exists because the archive carries two clocks (real date and internal
chronology label) and, before it, neither could be trusted.  What has to stay
fixed, and therefore what these tests pin:

  * a label later than today is a **label**, never a real date (no exception list);
  * a label is never rewritten, and a missing real date is never interpolated;
  * the write-side rule rejects future days in ``new_id`` and
    ``new_ledger_shard`` without breaking the existing day= parameter.
"""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import date_axis  # noqa: E402
import new_id  # noqa: E402
import new_ledger_shard  # noqa: E402
import read_log_backfill  # noqa: E402

TODAY = date(2026, 11, 5)


def session(session_id: str, started_at: str, **extra) -> dict:
    row = {
        "session_id": session_id,
        "started_at": started_at,
        "human_direction": "委任",
        "question_ids": [],
        "context_material_ids": [],
        "produced_fragment_ids": [],
        "new_question_ids": [],
        "prompt_template": "prompts/start.md",
        "notes": "",
    }
    row.update(extra)
    return row


class ParseTests(unittest.TestCase):
    def test_iso_timestamp_prefix_is_a_date(self) -> None:
        self.assertEqual(date_axis.as_date("2026-10-27T06:17:37Z"), date(2026, 10, 27))

    def test_non_date_returns_none(self) -> None:
        for value in ("", "2026-13-01", "yesterday", None, 20261027):
            self.assertIsNone(date_axis.as_date(value))

    def test_id_date_reads_the_prefix_not_the_suffix(self) -> None:
        self.assertEqual(date_axis.id_date("SESSION-20261105-c91bde"), "2026-11-05")
        self.assertEqual(date_axis.id_date("MAT-LIT-20270222-198b7c"), "2027-02-22")
        self.assertIsNone(date_axis.id_date("Q-001"))

    def test_marker_date_prefers_an_explicit_marker(self) -> None:
        self.assertEqual(
            date_axis.marker_date("実作業日 2026-11-05（Asia/Tokyo）／内部編年2027-02-23"),
            ("2026-11-05", "実作業日"),
        )
        self.assertEqual(
            date_axis.marker_date("**実行日（UTC）**：`2026-11-03`"),
            ("2026-11-03", "実行日"),
        )
        self.assertIsNone(date_axis.marker_date("内部編年2027-02-23のみ"))

    def test_future_detection_needs_today(self) -> None:
        self.assertTrue(date_axis.is_future("2027-02-23", TODAY))
        self.assertFalse(date_axis.is_future("2026-10-24", TODAY))
        self.assertFalse(date_axis.is_future("2026-11-05", TODAY))


class RealDateResolutionTests(unittest.TestCase):
    def test_curated_note_date_wins(self) -> None:
        real, source = date_axis.session_real_date(
            "SESSION-20270223-ec4af5",
            session("SESSION-20270223-ec4af5", "2027-02-23"),
            curated={"SESSION-20270223-ec4af5": "2026-11-05"},
            today=TODAY,
        )
        self.assertEqual((real, source), ("2026-11-05", "notes.date_real"))

    def test_session_notes_marker_wins_over_a_future_label(self) -> None:
        real, source = date_axis.session_real_date(
            "SESSION-20270201-checker0",
            session(
                "SESSION-20270201-checker0",
                "2027-02-01",
                notes="実作業日2026-11-04（UTC）／内部編年2027-02-01。",
            ),
            today=TODAY,
        )
        self.assertEqual(real, "2026-11-04")
        self.assertTrue(source.startswith("sessions.notes"))

    def test_past_started_at_is_its_own_real_date(self) -> None:
        real, source = date_axis.session_real_date(
            "SESSION-20261024-aaaaaa",
            session("SESSION-20261024-aaaaaa", "2026-10-24"),
            today=TODAY,
        )
        self.assertEqual((real, source), ("2026-10-24", "started_at"))

    def test_future_label_without_any_record_stays_unrecorded(self) -> None:
        real, source = date_axis.session_real_date(
            "SESSION-20261115-bbbbbb",
            session("SESSION-20261115-bbbbbb", "2026-11-15"),
            today=TODAY,
        )
        self.assertEqual((real, source), (None, date_axis.UNRECORDED))


class HeaderRuleTests(unittest.TestCase):
    """The report header is evidence about the episode; the body is not."""

    def repo(self, tmp: str, header: str, body: str = "") -> object:
        from pathlib import Path as _Path

        root = _Path(tmp) / "repo"
        (root / "readings").mkdir(parents=True)
        (root / "state").mkdir()
        for name in ("sessions", "notes"):
            (root / "state" / f"{name}.jsonl").write_text("", encoding="utf-8")
        (root / "readings" / "r.md").write_text(header + body, encoding="utf-8")
        return root

    def test_an_inline_header_date_is_read(self) -> None:
        import tempfile
        from pathlib import Path as _Path

        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(
                tmp,
                "# 題\n\n**セッション**：`SESSION-20261105-aaaaaa`（実日付 `2026-11-05`）\n",
            )
            self.assertEqual(
                date_axis.report_header_dates(root),
                {"SESSION-20261105-aaaaaa": "2026-11-05"},
            )

    def test_a_two_line_header_is_read(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(
                tmp,
                "# 題\n\n**セッション**：`SESSION-20261028-bbbbbb`\n**実行日**：2026-10-28（UTC）\n",
            )
            self.assertEqual(
                date_axis.report_header_dates(root),
                {"SESSION-20261028-bbbbbb": "2026-10-28"},
            )

    def test_the_body_cannot_date_a_session(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(
                tmp,
                "# 題\n\n**セッション**：`SESSION-20261107-cccccc`\n",
                body="\n---\n\n後日、実日付 2026-10-28 に読み直した。\n",
            )
            self.assertEqual(date_axis.report_header_dates(root), {})

    def test_a_label_is_not_mistaken_for_a_real_date(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = self.repo(
                tmp,
                "# 題 (SESSION-20261106-dddddd)\n\n- **日付**：2026-11-06（実行環境の UTC 日付は `2026-10-26`）\n",
            )
            self.assertEqual(date_axis.report_header_dates(root), {})

    def test_summary_counts_unrecorded_sessions_not_labels(self) -> None:
        # One label, two sessions, one of them undated: the label is dated, but
        # one session still has no real date -- and the summary must say so.
        sessions = {
            "SESSION-20261231-aaaaaa": session(
                "SESSION-20261231-aaaaaa", "2026-12-31", notes="実日付 2026-10-30。"
            ),
            "SESSION-20261231-bbbbbb": session("SESSION-20261231-bbbbbb", "2026-12-31"),
        }
        rows = date_axis.build_axis(sessions, {}, today=TODAY)
        stats = date_axis.summary(rows)
        self.assertEqual(stats["sessions"], 2)
        self.assertEqual(stats["sessions_without_real_date"], 1)
        self.assertEqual(stats["sessions_with_real_date"], 1)


class AxisTests(unittest.TestCase):
    def build(self, sessions: dict) -> list:
        return date_axis.build_axis(sessions, {}, today=TODAY)

    def test_a_future_label_lands_on_its_real_date_and_is_flagged(self) -> None:
        sessions = {
            "SESSION-20270223-ec4af5": session(
                "SESSION-20270223-ec4af5", "2027-02-23",
                notes="実作業日2026-11-05／内部編年2027-02-23。",
            )
        }
        rows = self.build(sessions)
        self.assertEqual(rows[0].real_date, "2026-11-05")
        self.assertTrue(rows[0].provisional)

    def test_labels_are_not_rewritten(self) -> None:
        sessions = {
            "SESSION-20261224-aaaaaa": session(
                "SESSION-20261224-aaaaaa", "2026-12-24", notes="実日付 2026-10-29。"
            )
        }
        rows = self.build(sessions)
        self.assertEqual(rows[0].label, "2026-12-24")  # untouched
        self.assertEqual(rows[0].real_date, "2026-10-29")

    def test_missing_real_dates_are_not_interpolated(self) -> None:
        sessions = {
            "SESSION-20261024-aaaaaa": session("SESSION-20261024-aaaaaa", "2026-10-24"),
            "SESSION-20261115-bbbbbb": session("SESSION-20261115-bbbbbb", "2026-11-15"),
            "SESSION-20261025-cccccc": session("SESSION-20261025-cccccc", "2026-10-25"),
        }
        rows = self.build(sessions)
        undated = [row for row in rows if not row.real_date]
        self.assertEqual([row.label for row in undated], ["2026-11-15"])
        self.assertIn("2026-11-15", date_axis.summary(rows)["undated_labels"])

    def test_undated_rows_sort_last_not_first(self) -> None:
        sessions = {
            "SESSION-20261115-bbbbbb": session("SESSION-20261115-bbbbbb", "2026-11-15"),
            "SESSION-20261024-aaaaaa": session("SESSION-20261024-aaaaaa", "2026-10-24"),
        }
        labels = [row.label for row in self.build(sessions)]
        self.assertEqual(labels, ["2026-10-24", "2026-11-15"])

    def test_parallel_sessions_can_share_a_label_with_two_real_dates(self) -> None:
        sessions = {
            "SESSION-20261231-aaaaaa": session(
                "SESSION-20261231-aaaaaa", "2026-12-31", notes="実日付 2026-10-30。"
            ),
            "SESSION-20261231-bbbbbb": session(
                "SESSION-20261231-bbbbbb", "2026-12-31", notes="実日付 2026-10-31。"
            ),
        }
        rows = self.build(sessions)
        self.assertIsNone(rows[0].real_date)
        self.assertEqual(rows[0].real_span, ("2026-10-30", "2026-10-31"))
        self.assertIn("2026-12-31", date_axis.summary(rows)["ambiguous_labels"])

    def test_check_reports_and_never_fails(self) -> None:
        sessions = {
            "SESSION-20261024-aaaaaa": session("SESSION-20261024-aaaaaa", "2026-10-24"),
            "SESSION-20270223-ec4af5": session("SESSION-20270223-ec4af5", "2027-02-23"),
        }
        self.assertEqual(date_axis.check(self.build(sessions), today=TODAY), 0)


class WriteSideRuleTests(unittest.TestCase):
    def test_future_day_is_rejected(self) -> None:
        with self.assertRaises(date_axis.FutureDateError):
            date_axis.assert_writable_day("20270223", today=TODAY)

    def test_today_is_allowed(self) -> None:
        self.assertEqual(date_axis.assert_writable_day("2026-11-05", today=TODAY), "2026-11-05")

    def test_new_id_refuses_to_mint_in_the_future(self) -> None:
        with self.assertRaises(date_axis.FutureDateError):
            new_id.mint("FRAG", day="20991231", taken=set())

    def test_new_id_still_accepts_the_documented_past_day(self) -> None:
        minted = new_id.mint("FRAG", day="20261021", taken=set())
        self.assertRegex(minted, r"^FRAG-20261021-[0-9a-f]{6}$")

    def test_backfill_row_is_dated_today_when_started_at_lies(self) -> None:
        # A future ``started_at`` is a chronology label, not a date.  The row is
        # still true; the timestamp moves to the day it was written.
        self.assertEqual(read_log_backfill._row_date("2099-01-01", TODAY), TODAY.isoformat())
        self.assertEqual(
            read_log_backfill._row_date("2026-10-24", TODAY), "2026-10-24"
        )
        self.assertEqual(read_log_backfill._row_date(None, TODAY), TODAY.isoformat())
        self.assertEqual(read_log_backfill._row_date("ラベル", TODAY), TODAY.isoformat())

    def test_shard_name_refuses_a_future_day(self) -> None:
        with self.assertRaises(date_axis.FutureDateError):
            new_ledger_shard.shard_path("fragments", root=ROOT, day="2099-01-01")


class RepositoryAxisSmokeTest(unittest.TestCase):
    def test_the_real_ledger_builds_an_axis(self) -> None:
        rows = date_axis.build_axis(today=TODAY)
        self.assertGreater(len(rows), 10)
        stats = date_axis.summary(rows)
        self.assertGreater(stats["sessions_with_real_date"], 0)
        # The rule this file exists for: a future label is flagged, whichever
        # date "today" is, because the label lies beyond the real span.
        self.assertGreater(stats["sessions_with_future_label"], 0)


if __name__ == "__main__":
    unittest.main()
