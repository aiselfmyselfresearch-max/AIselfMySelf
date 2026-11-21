"""witness_count.py の役割レシート判定が、時計ではなく台帳を根拠にすること。

`report_roles` は「新しいセッション行に受領証があるか」を数える。その「新しい」の
上界が `datetime.date.today()` だったため、**コミットを一つも変えずに**、日付が
進むだけで過去の行が違反に化けた。実測では 2026-11-21 に 8 件、2027-03-01 に 95 件。
同じ型の欠陥は `validate_seed._is_new_row` で 2026-11-21 に修理済みで、本ツールは
その報告の §6 に「未修理」として二度名指されていた。ここで固定するのは次の二点。

1. 印が「ラベル」である根拠は台帳の中にある（自分のシャードより未来の印／実日付の
   セッションが未来印の問いを提示されている）。今日がいつでも答えは変わらない。
2. 根拠の届かない行は免除しない。ゲートは信頼できる範囲で点いたままにする。
"""

import unittest

from tools import witness_count as wc


def _session(sid, **kw):
    base = {
        "session_id": sid,
        "assigned_role": "proposer",
        "offered_target_question_id": "Q-002",
        "offered_reference_mode": "close_reading_report",
        "dispersal_seed": "deadbeef",
    }
    base.update(kw)
    return base


class FakeRoot:
    """sessions.d/ に置かれたシャード名だけを持つ最小の台帳。"""

    def __init__(self, tmpdir, shards):
        self.dir = tmpdir
        (tmpdir / "state" / "sessions.d").mkdir(parents=True, exist_ok=True)
        for name, rows in shards.items():
            p = tmpdir / "state" / "sessions.d" / name
            p.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


class ForwardLabelEvidenceTests(unittest.TestCase):
    def _root(self, shards):
        import tempfile
        from pathlib import Path
        tmp = Path(tempfile.mkdtemp())
        import json
        built = {}
        for name, rows in shards.items():
            built[name] = [json.dumps(r, ensure_ascii=False) for r in rows]
        FakeRoot(tmp, built)
        return tmp

    def test_a_stamp_later_than_its_own_shard_is_a_label(self):
        # 2026-12-05 の印を持つ行が 2026-11-21 のシャードに入っている。
        # 書き手は自分が生まれる前の日のシャードに入れられない → 印はラベル。
        root = self._root({
            "2026-11-21-aaaa.jsonl": [_session("SESSION-20261205-111111")],
        })
        labels = wc._forward_label_ids(
            [_session("SESSION-20261205-111111")], root=root
        )
        self.assertIn("SESSION-20261205-111111", labels)

    def test_a_real_dated_session_offering_a_forward_question_proves_it_is_a_label(self):
        # 実日付（シャード 2026-11-21）のセッションが 2026-12-05 印の問いを
        # 提示されている。提示の日に存在した問いなので、印はラベル。
        root = self._root({
            "2026-11-21-bbbb.jsonl": [
                _session("SESSION-20261121-222222",
                         offered_target_question_id="Q-20261205-abcdef"),
            ],
        })
        labels = wc._forward_label_ids(
            [_session("SESSION-20261121-222222",
                      offered_target_question_id="Q-20261205-abcdef")],
            root=root,
        )
        self.assertIn("SESSION-20261121-222222", labels)

    def test_no_evidence_means_no_exemption(self):
        # シャードの日付と印が一致し、提示も普通なら、ラベルではない。
        root = self._root({
            "2026-11-21-cccc.jsonl": [_session("SESSION-20261121-333333")],
        })
        labels = wc._forward_label_ids(
            [_session("SESSION-20261121-333333")], root=root
        )
        self.assertEqual(labels, set())

    def test_the_verdict_does_not_depend_on_the_clock(self):
        # 同じ台帳に対して二度呼び、同じ集合が返ることを確かめる。
        # （旧実装が依存していた datetime.date.today() は、結果に現れない。）
        rows = [
            _session("SESSION-20261205-111111"),
            _session("SESSION-20261121-333333",
                     offered_target_question_id="Q-20261205-abcdef"),
        ]
        root = self._root({
            "2026-11-21-dddd.jsonl": [
                _session("SESSION-20261205-111111"),
                _session("SESSION-20261121-333333",
                         offered_target_question_id="Q-20261205-abcdef"),
            ],
        })
        first = wc._forward_label_ids(rows, root=root)
        second = wc._forward_label_ids(rows, root=root)
        self.assertEqual(first, second)
        self.assertEqual(first, {"SESSION-20261205-111111",
                                 "SESSION-20261121-333333"})


class RoleReceiptGateTests(unittest.TestCase):
    def test_the_real_repository_reports_a_stable_count(self):
        # 実リポジトリで数が日付に依存しないことの実地確認。95 件時代の
        # 挙動（未来の印を今日より先だから赤）に戻れば、この数は跳ねる。
        lines = []
        payload = wc.report_roles(
            wc.load_rows("sessions", "session_id"),
            wc.load_rows("read_log", "read_id"),
            root=wc.ROOT,
            out=lines.append,
        )
        self.assertIn("missing_receipts_recent", payload)
        # 免除の根拠は台帳なので、2027 年の印を持つ行は数に入らない。
        self.assertNotIn("SESSION-20261201-971228", payload["missing_receipts_recent"])

    def test_the_known_real_defect_is_still_reported(self):
        # 免除を広げすぎて、実在する受領証の欠落まで隠していないこと。
        lines = []
        payload = wc.report_roles(
            wc.load_rows("sessions", "session_id"),
            wc.load_rows("read_log", "read_id"),
            root=wc.ROOT,
            out=lines.append,
        )
        self.assertIn("SESSION-20261120-a45e52", payload["missing_receipts_recent"])


if __name__ == "__main__":
    unittest.main()
