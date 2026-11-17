"""`witness_count.py --contests` の数え方だけを検める（台帳には触れない）。

数えているのは「異議が宛先を持ち、返答されるか」であって、異議の正しさではない。
ここで固定するのは判定の境界——とくに、後の読みが異議を名指した場合と、
単に独立に読み直した場合が混ざらないこと。
"""

import unittest

from tools import witness_count as wc


def _row(read_id, ref, *, session="S-1", reading="read", note="", created="2026-11-17T00:00:00Z"):
    return {
        "read_id": read_id,
        "session_id": session,
        "target": {"type": "material" if ref.startswith("MAT-") else "fragment", "id": ref},
        "reading": reading,
        "note": note,
        "created_at": created,
    }


class ContestReportTests(unittest.TestCase):
    def _report(self, rows):
        lines = []
        payload = wc.report_contests(rows, out=lines.append)
        return payload, "\n".join(lines)

    def test_counts_contested_share_and_target_types(self):
        rows = [
            _row("READ-20260101-000001", "FRAG-1", reading="contested"),
            _row("READ-20260101-000002", "FRAG-1"),
            _row("READ-20260101-000003", "MAT-1", reading="contested"),
        ]
        payload, _ = self._report(rows)
        self.assertEqual(payload["handwritten"], 3)
        self.assertEqual(payload["contested"], 2)
        self.assertEqual(payload["by_target_type"], {"fragment": 1, "material": 1})

    def test_mechanical_rows_are_not_hand_written(self):
        rows = [
            _row("READ-20260101-000001", "FRAG-1", reading="contested"),
            _row("READ-20260101-000002", "FRAG-1", reading="contested",
                 note="機械的バックフィル: 既存行の補完"),
        ]
        payload, _ = self._report(rows)
        self.assertEqual(payload["handwritten"], 1)
        self.assertEqual(payload["contested"], 1)

    def test_a_later_reading_only_answers_when_it_names_the_contest(self):
        contested = _row("READ-20260101-000001", "FRAG-1", reading="contested",
                         note="前回の読みに異議。")
        silent = _row("READ-20260102-000001", "FRAG-1", session="S-2",
                      created="2026-11-18T00:00:00Z")
        named = _row("READ-20260103-000001", "FRAG-1", session="S-3",
                     note="異議として受け取る。", created="2026-11-19T00:00:00Z")

        payload, _ = self._report([contested, silent])
        self.assertEqual(payload["followed"], 1)
        self.assertEqual(payload["answered"], 0)

        payload, _ = self._report([contested, silent, named])
        self.assertEqual(payload["followed"], 1)
        self.assertEqual(payload["answered"], 1)

    def test_citing_the_contested_read_id_also_counts_as_an_answer(self):
        contested = _row("READ-20260101-000001", "FRAG-1", reading="contested")
        answer = _row("READ-20260102-000001", "FRAG-1", session="S-2",
                      note="READ-20260101-000001 を退ける。",
                      created="2026-11-18T00:00:00Z")
        payload, _ = self._report([contested, answer])
        self.assertEqual(payload["citing_read_id"], 0)  # the contest itself cites nothing
        self.assertEqual(payload["answered"], 1)

    def test_same_session_reading_does_not_count_as_a_follow_up(self):
        contested = _row("READ-20260101-000001", "FRAG-1", reading="contested")
        same = _row("READ-20260101-000002", "FRAG-1", session="S-1",
                    created="2026-11-18T00:00:00Z")
        payload, _ = self._report([contested, same])
        self.assertEqual(payload["followed"], 0)


if __name__ == "__main__":
    unittest.main()
