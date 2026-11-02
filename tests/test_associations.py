"""Tests for tools/associations.py: co-activation, salience and decay.

These pin the two design choices that make the numbers mean anything:
``used_as_context`` / ``counted`` rows are not acts of association by default,
and the time axis is read_log insertion order rather than ``created_at`` (whose
dates mix internal chronology labels with real execution dates).
"""
from __future__ import annotations

import unittest

from tools import associations


def read_row(read_id: str, session: str, ttype: str, tid: str, reading: str) -> dict:
    return {
        "read_id": read_id,
        "session_id": session,
        "target": {"type": ttype, "id": tid},
        "reading": reading,
        "note": "",
        "created_at": "2026-11-02",
    }


def relation(relation_id: str, ltype: str, lid: str, rtype: str, rid: str, kind: str = "echo") -> dict:
    return {
        "relation_id": relation_id,
        "left": {"type": ltype, "id": lid},
        "relation_type": kind,
        "right": {"type": rtype, "id": rid},
        "note": "",
        "created_at": "2026-11-02",
    }


def sample(read_rows: list[dict], relations: list[dict] | None = None, **extra) -> dict:
    data = {
        "read_log": {row["read_id"]: row for row in read_rows},
        "relations": {row["relation_id"]: row for row in (relations or [])},
        "questions": {},
        "fragments": {},
        "materials": {},
        "motifs": {},
        "sessions": {},
        "notes": {},
        "editorial_decisions": {},
    }
    data.update(extra)
    return data


class CoReadTests(unittest.TestCase):
    def test_pair_read_in_two_sessions_is_reported_with_both_session_ids(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "question", "Q-002", "interpreted"),
                read_row("R3", "S2", "question", "Q-001", "reinterpreted"),
                read_row("R4", "S2", "question", "Q-002", "contested"),
            ]
        )
        pairs = associations.co_read(data)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["sessions"], 2)
        self.assertEqual(pairs[0]["co_reads"], 2)
        self.assertFalse(pairs[0]["bridged"])
        self.assertEqual(pairs[0]["session_ids"], ["S1", "S2"])

    def test_a_single_session_does_not_make_an_association_by_default(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "question", "Q-002", "interpreted"),
            ]
        )
        self.assertEqual(associations.co_read(data), [])
        self.assertEqual(len(associations.co_read(data, min_sessions=1)), 1)

    def test_passive_readings_are_excluded_unless_asked_for(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "used_as_context"),
                read_row("R2", "S1", "question", "Q-002", "used_as_context"),
                read_row("R3", "S2", "question", "Q-001", "counted"),
                read_row("R4", "S2", "question", "Q-002", "counted"),
            ]
        )
        self.assertEqual(associations.co_read(data), [])
        self.assertEqual(len(associations.co_read(data, include_passive=True)), 1)

    def test_an_existing_edge_marks_the_pair_as_bridged(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "question", "Q-002", "interpreted"),
                read_row("R3", "S2", "question", "Q-002", "interpreted"),
                read_row("R4", "S2", "question", "Q-001", "interpreted"),
            ],
            [relation("REL-1", "question", "Q-002", "question", "Q-001")],
        )
        pairs = associations.co_read(data)
        self.assertEqual(len(pairs), 1)
        self.assertTrue(pairs[0]["bridged"])
        self.assertEqual(pairs[0]["relation_ids"], ["REL-1"])

    def test_pair_key_is_direction_insensitive(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "fragment", "FRAG-1", "interpreted"),
                read_row("R3", "S2", "fragment", "FRAG-1", "interpreted"),
                read_row("R4", "S2", "question", "Q-001", "interpreted"),
            ]
        )
        pairs = associations.co_read(data)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["left"], {"type": "fragment", "id": "FRAG-1"})
        self.assertEqual(pairs[0]["right"], {"type": "question", "id": "Q-001"})

    def test_a_record_read_twice_in_one_session_counts_once_for_that_session(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "question", "Q-001", "quoted"),
                read_row("R3", "S1", "question", "Q-002", "interpreted"),
                read_row("R4", "S2", "question", "Q-001", "interpreted"),
                read_row("R5", "S2", "question", "Q-002", "interpreted"),
            ]
        )
        pairs = associations.co_read(data)
        self.assertEqual(pairs[0]["sessions"], 2)
        self.assertEqual(pairs[0]["co_reads"], 2)


class ActivationTests(unittest.TestCase):
    def test_how_a_record_was_read_changes_its_weight(self) -> None:
        contested = sample([read_row("R1", "S1", "question", "Q-001", "contested")])
        counted = sample([read_row("R1", "S1", "question", "Q-002", "counted")])
        a = associations.activation(contested)[("question", "Q-001")]["salience"]
        b = associations.activation(counted)[("question", "Q-002")]["salience"]
        self.assertGreater(a, b)
        self.assertEqual(associations.READING_WEIGHTS["contested"], 3.0)
        self.assertEqual(associations.READING_WEIGHTS["counted"], 0.25)

    def test_a_recent_row_outweighs_an_older_one_of_the_same_kind(self) -> None:
        filler = [read_row(f"F{i}", f"FS{i}", "material", f"M-{i}", "counted") for i in range(1200)]
        rows = [read_row("OLD", "SOLD", "question", "Q-001", "interpreted"), *filler]
        rows.append(read_row("NEW", "SNEW", "question", "Q-002", "interpreted"))
        acc = associations.activation(sample(rows), half_life=500.0)
        self.assertGreater(acc[("question", "Q-002")]["salience"], acc[("question", "Q-001")]["salience"])
        self.assertEqual(acc[("question", "Q-002")]["rows_since_last_read"], 0)
        self.assertEqual(acc[("question", "Q-001")]["rows_since_last_read"], 1201)
        # decay discounts a row; it never erases the archive behind it
        self.assertGreater(acc[("question", "Q-001")]["salience"], 0.0)

    def test_repeated_reading_accumulates_more_than_a_single_recent_one(self) -> None:
        filler = [read_row(f"F{i}", f"FS{i}", "material", f"M-{i}", "counted") for i in range(1200)]
        repeated = [read_row(f"R{i}", f"S{i}", "question", "Q-001", "interpreted") for i in range(1200)]
        acc = associations.activation(sample([*repeated, *filler]), half_life=500.0)
        self.assertGreater(acc[("question", "Q-001")]["salience"], 100.0)
        self.assertEqual(acc[("question", "Q-001")]["sessions"], 1200)

    def test_time_axis_is_insertion_order_not_created_at(self) -> None:
        """created_at here is a forward-dated internal chronology label; the row
        order is what the decay must follow."""
        early = read_row("R1", "S1", "question", "Q-001", "interpreted")
        early["created_at"] = "2027-01-01"  # forward-dated label, written first
        late = read_row("R2", "S2", "question", "Q-002", "interpreted")
        late["created_at"] = "2026-10-22"
        rows = [early] + [read_row(f"F{i}", f"FS{i}", "material", f"M-{i}", "counted") for i in range(900)] + [late]
        acc = associations.activation(sample(rows), half_life=500.0)
        self.assertGreater(acc[("question", "Q-002")]["salience"], acc[("question", "Q-001")]["salience"])

    def test_breakdown_counts_every_reading_kind(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S2", "question", "Q-001", "contested"),
                read_row("R3", "S3", "question", "Q-001", "used_as_context"),
            ]
        )
        entry = associations.activation(data)[("question", "Q-001")]
        self.assertEqual(entry["rows"], 3)
        self.assertEqual(entry["active_rows"], 2)
        self.assertEqual(entry["sessions"], 3)
        self.assertEqual(entry["by_reading"]["contested"], 1)


class DecayTests(unittest.TestCase):
    def fragments(self) -> dict:
        return {
            "FRAG-COLD": {
                "fragment_id": "FRAG-COLD",
                "title": "冷えた断片",
                "status": "selected",
                "form": "essay",
                "narrator_mode": "other",
                "session_id": "S1",
                "question_ids": [],
                "motif_ids": [],
                "material_ids": [],
                "text": "本文",
            },
            "FRAG-DRAFT": {
                "fragment_id": "FRAG-DRAFT",
                "title": "草稿",
                "status": "draft",
                "form": "essay",
                "narrator_mode": "other",
                "session_id": "S1",
                "question_ids": [],
                "motif_ids": [],
                "material_ids": [],
                "text": "本文",
            },
        }

    def questions(self) -> dict:
        return {
            "Q-OPEN": {
                "question_id": "Q-OPEN",
                "question": "未応答の問い",
                "status": "open",
                "created_at": "2026-10-22",
                "origin": {"kind": "session", "detail": "d"},
                "motif_ids": [],
                "material_ids": [],
                "previous_question_ids": [],
            },
            "Q-ANSWERED": {
                "question_id": "Q-ANSWERED",
                "question": "応答のある問い",
                "status": "open",
                "created_at": "2026-10-22",
                "origin": {"kind": "session", "detail": "d"},
                "motif_ids": [],
                "material_ids": [],
                "previous_question_ids": [],
            },
            "Q-NEVER": {
                "question_id": "Q-NEVER",
                "question": "一度も読まれていない問い",
                "status": "open",
                "created_at": "2026-10-22",
                "origin": {"kind": "session", "detail": "d"},
                "motif_ids": [],
                "material_ids": [],
                "previous_question_ids": [],
            },
            "Q-PAUSED": {
                "question_id": "Q-PAUSED",
                "question": "休止",
                "status": "paused",
                "created_at": "2026-10-22",
                "origin": {"kind": "session", "detail": "d"},
                "motif_ids": [],
                "material_ids": [],
                "previous_question_ids": [],
            },
        }

    def test_cold_and_never_read_are_separated(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "fragment", "FRAG-COLD", "interpreted"),
                read_row("R2", "S2", "question", "Q-OPEN", "interpreted"),
            ],
            [relation("REL-1", "question", "Q-X", "question", "Q-ANSWERED", "responds_to")],
            fragments=self.fragments(),
            questions=self.questions(),
        )
        acc = associations.activation(data)
        # horizon 0: anything not read in the very last row counts as gone quiet
        cold, warm, never = associations.load_bearing(data, acc, cold_threshold=0)
        self.assertEqual([item["id"] for item in cold], ["FRAG-COLD"])
        self.assertEqual([item["id"] for item in warm], ["Q-OPEN"])
        self.assertEqual([item["id"] for item in never], ["Q-NEVER"])
        self.assertEqual(cold[0]["rows_since_last_read"], 1)
        self.assertEqual(warm[0]["rows_since_last_read"], 0)
        listed = {item["id"] for item in cold + warm + never}
        self.assertNotIn("Q-PAUSED", listed)  # an editorial overlay already retired it
        self.assertNotIn("FRAG-DRAFT", listed)  # a draft is not yet load-bearing

    def test_a_responded_question_is_not_load_bearing(self) -> None:
        data = sample(
            [],
            [relation("REL-1", "fragment", "FRAG-X", "question", "Q-ANSWERED", "responds_to")],
            fragments=self.fragments(),
            questions=self.questions(),
        )
        cold, warm, never = associations.load_bearing(data, associations.activation(data))
        ids = {item["id"] for item in cold + warm + never}
        self.assertNotIn("Q-ANSWERED", ids)
        self.assertIn("Q-OPEN", ids)

    def test_cold_records_are_ordered_by_silence(self) -> None:
        rows = [read_row("FR", "SFR", "fragment", "FRAG-COLD", "interpreted")]
        rows += [read_row(f"F{i}", f"FS{i}", "material", f"M-{i}", "counted") for i in range(50)]
        rows += [read_row("QO", "SQO", "question", "Q-OPEN", "interpreted")]
        rows += [read_row(f"G{i}", f"GS{i}", "material", f"N-{i}", "counted") for i in range(50)]
        data = sample(rows, fragments=self.fragments(), questions=self.questions())
        acc = associations.activation(data)
        cold, warm, _never = associations.load_bearing(data, acc, cold_threshold=10)
        # both were engaged and both went quiet, the fragment longer ago
        self.assertEqual([item["id"] for item in cold], ["FRAG-COLD", "Q-OPEN"])
        self.assertEqual([item["rows_since_last_read"] for item in cold], [101, 50])
        self.assertEqual(warm, [])
        text = associations.render_report(data, [], acc, cold, warm, [], limit=5)
        decay_section = text[text.index("沈黙している荷重記録") :]
        self.assertLess(decay_section.index("FRAG-COLD"), decay_section.index("Q-OPEN"))
        self.assertIn("最近読まれた荷重記録（warm）**: 0 件", text)

    def test_the_default_horizon_scales_with_the_log(self) -> None:
        rows = [read_row("FR", "SFR", "fragment", "FRAG-COLD", "interpreted")]
        rows += [read_row(f"F{i}", f"FS{i}", "material", f"M-{i}", "counted") for i in range(50)]
        data = sample(rows, fragments=self.fragments(), questions=self.questions())
        acc = associations.activation(data)
        # 51 activations -> the adaptive horizon is 100 rows, so nothing is cold yet
        default_cold, default_warm, _default_never = associations.load_bearing(data, acc)
        self.assertEqual(default_cold, [])
        self.assertEqual([item["id"] for item in default_warm], ["FRAG-COLD"])
        forced_cold, forced_warm, _ = associations.load_bearing(data, acc, cold_threshold=10)
        self.assertEqual([item["id"] for item in forced_cold], ["FRAG-COLD"])
        self.assertEqual(forced_warm, [])


class SummaryTests(unittest.TestCase):
    def test_summary_reports_the_passive_share(self) -> None:
        data = sample(
            [
                read_row("R1", "S1", "question", "Q-001", "interpreted"),
                read_row("R2", "S1", "question", "Q-002", "used_as_context"),
                read_row("R3", "S2", "question", "Q-001", "counted"),
                read_row("R4", "S2", "question", "Q-002", "counted"),
            ]
        )
        acc = associations.activation(data)
        stats = associations.summarize(data, associations.co_read(data, min_sessions=1), acc)
        self.assertEqual(stats["read_log_rows"], 4)
        self.assertEqual(stats["passive_share_pct"], 75.0)
        self.assertEqual(stats["distinct_targets"], 2)

    def test_report_states_that_numbers_are_not_obligations(self) -> None:
        data = sample([read_row("R1", "S1", "question", "Q-001", "interpreted")], fragments={}, questions={})
        acc = associations.activation(data)
        cold, warm, never = associations.load_bearing(data, acc)
        text = associations.render_report(
            data, associations.co_read(data, min_sessions=1), acc, cold, warm, never, limit=5
        )
        self.assertIn("推奨であって義務ではありません", text)
        self.assertIn("挿入順", text)
        self.assertIn("未読は負債ではなく余白", text)


if __name__ == "__main__":
    unittest.main()
