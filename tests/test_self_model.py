"""Tests for tools/self_model.py, tools/interoception.py, tools/source_monitoring.py, and tools/agency_trace.py.

Pins the software behavior of the six-layer self-model generators/auditors without
hard-coding live archive counts or posteriors:
  1. 4-column + bold percentage BELIEF_MAP.md rows extract Top-3 P_t and P_gate leaders
     with non-empty titles (and 3-column legacy rows remain readable).
  2. Shard-bounded real chronology prevents forward-dated legacy labels (e.g.
     started_at='2027-03-19' on SESSION-20261111-794f41 or SESSION-20270223-* in a
     2026-11-02 shard) from freezing current self-location or role-balance windows.
  3. Cross-ledger semantic invariants reject blank Top-3 extractions even when
     SELF_MODEL.md matches a broken generator output byte-for-byte.
  4. Source-monitoring and agency-trace audits distinguish provable forward-dated
     internal labels from genuine post-cutoff missing tags.
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
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import agency_trace  # noqa: E402
import interoception  # noqa: E402
import self_model  # noqa: E402
import source_monitoring  # noqa: E402


SAMPLE_BELIEF_MAP_V2 = """# BELIEF_MAP

| 問い | 仮説数 (有効) | 第0世代質量 (素朴基底) | 第1世代+質量 (条件付き) | 事後エントロピー | D_KL(P_t || P_0) | 平均不確実性 u | 最優先検証ペア |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `Q-001` | 4 (3) | 0.0% | **100.0%** | 1.0 bits | 1.0 bits | 0.3 | — |
| `Q-002` | 3 (2) | 0.0% | **100.0%** | 1.0 bits | 1.0 bits | 0.3 | — |
| `Q-003` | 2 (2) | 0.0% | **100.0%** | 1.0 bits | 1.0 bits | 0.3 | — |

## Q-001: 人間とは何か

| 順位 | ID | 状態 (抑制区分) | 世代/系譜 | 事後確率 P_t | P_sep | P_lin | P_gate (三門制御) | 不確実性 u | 仮説タイトル |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `HYP-20261119-aaaaaa` | `active` | G2:refines (`HYP-1`) | **60.0%** | 10.0% | 5.0% | **10.0%** (-50.0pp) | 0.25 | 第一仮説タイトル |
| 2 | `HYP-20261121-bbbbbb` | `active` | G3:synthesizes (`HYP-1`) | **40.0%** | 90.0% | 95.0% | **90.0%** (+50.0pp) | 0.35 | 第二仮説タイトル |

## Q-002: AIにとって自己とは何か

| 順位 | ID | 状態 (抑制区分) | 世代/系譜 | 事後確率 P_t | P_sep | P_lin | P_gate (三門制御) | 不確実性 u | 仮説タイトル |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `HYP-20261120-cccccc` | `active` | G1:refines (`HYP-0`) | **75.0%** | 75.0% | 75.0% | **75.0%** (+0.0pp) | 0.30 | 自己モデル仮説 |

## Q-003: 記録は自己を保存するか

| 順位 | ID | 状態 (抑制区分) | 世代/系譜 | 事後確率 P_t | P_sep | P_lin | P_gate (三門制御) | 不確実性 u | 仮説タイトル |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `HYP-20261117-dddddd` | `active` | G1:refines (`HYP-0`) | **80.0%** | 80.0% | 80.0% | **80.0%** (+0.0pp) | 0.20 | 記録保存仮説 |

## Q-20261116-3872ec: 周辺派生問（Q-003へ漏洩してはならない）

| 順位 | ID | 状態 (抑制区分) | 世代/系譜 | 事後確率 P_t | P_sep | P_lin | P_gate (三門制御) | 不確実性 u | 仮説タイトル |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `HYP-20261116-085f33` | `active` | G1:refines (`HYP-0`) | **100.0%** | 100.0% | 100.0% | **100.0%** (+0.0pp) | 0.10 | 周辺問単独仮説 |
"""


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


class SelfModelTests(unittest.TestCase):
    def test_load_belief_summary_parses_4col_bold_and_pgate_leaders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "BELIEF_MAP.md").write_text(SAMPLE_BELIEF_MAP_V2, encoding="utf-8")
            belief = self_model.load_belief_summary(root)
            cq = belief["core_questions"]
            self.assertEqual(cq["Q-001"]["p1_mass"], "100.0%")
            self.assertEqual(len(cq["Q-001"]["top"]), 2)
            self.assertEqual(cq["Q-001"]["top"][0]["hid"], "HYP-20261119-aaaaaa")
            self.assertEqual(cq["Q-001"]["top"][0]["posterior"], "60.0%")
            self.assertEqual(cq["Q-001"]["top"][0]["title"], "第一仮説タイトル")
            # P_gate leader must invert order when rank 2 has higher P_gate (90.0% > 10.0%)
            self.assertEqual(cq["Q-001"]["top_gated"][0]["hid"], "HYP-20261121-bbbbbb")
            self.assertEqual(cq["Q-001"]["top_gated"][0]["pgate"], "90.0%")
            # Peripheral question after Q-003 must not leak into Q-003
            self.assertEqual(len(cq["Q-003"]["top_gated"]), 1)
            self.assertEqual(cq["Q-003"]["top_gated"][0]["hid"], "HYP-20261117-dddddd")

    def test_shard_bounded_chronology_ignores_forward_started_at_and_id_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "BELIEF_MAP.md").write_text(SAMPLE_BELIEF_MAP_V2, encoding="utf-8")
            _write_jsonl(root / "state" / "sessions.jsonl", [])
            # Legacy shard from 2026-11-11 carrying forward label 2027-03-19
            _write_jsonl(
                root / "state" / "sessions.d" / "2026-11-11-000000000000.jsonl",
                [
                    {
                        "session_id": "SESSION-20261111-794f41",
                        "started_at": "2027-03-19",
                        "assigned_role": None,
                    },
                    {
                        "session_id": "SESSION-20270223-ec4af5",
                        "started_at": "2027-02-23",
                        "assigned_role": "consolidator",
                    },
                ],
            )
            # Earlier per-branch shard on 2026-11-21 (sorts ASCII-after 000000000000, but predates shared daily)
            _write_jsonl(
                root / "state" / "sessions.d" / "2026-11-21-self-memory-neuro10.jsonl",
                [
                    {
                        "session_id": "SESSION-20261121-self-memory-neuro10",
                        "started_at": "2026-11-21",
                        "assigned_role": "consolidator",
                    }
                ],
            )
            # Genuine 2026-11-21 shared daily shard (later-appended row with smaller hex ID wins)
            _write_jsonl(
                root / "state" / "sessions.d" / "2026-11-21-000000000000.jsonl",
                [
                    {
                        "session_id": "SESSION-20261121-self-memory-10",
                        "started_at": "2026-11-21",
                        "assigned_role": "consolidator",
                    },
                    {
                        "session_id": "SESSION-20261121-4f2caf",
                        "started_at": "2026-11-21",
                        "assigned_role": "proposer",
                    },
                ],
            )
            sess = self_model.load_current_session(root)
            self.assertEqual(sess["current"], "SESSION-20261121-4f2caf")
            self.assertEqual(sess["current_real_date"], "2026-11-21")
            self.assertEqual(sess["current_role"], "proposer")

            rb = interoception.measure_role_balance(root, window=1)
            self.assertEqual(rb["distribution"], {"proposer": 1})

    def test_semantic_invariants_reject_empty_top3_even_when_rendered_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Summary says 3 active hypotheses on Q-001, but table section has no rows
            broken_bm = "\n".join(SAMPLE_BELIEF_MAP_V2.splitlines()[:8]) + "\n"
            (root / "BELIEF_MAP.md").write_text(broken_bm, encoding="utf-8")
            _write_jsonl(
                root / "state" / "sessions.jsonl",
                [{"session_id": "SESSION-20261121-aaaaaa", "started_at": "2026-11-21", "assigned_role": "proposer"}],
            )
            belief = self_model.load_belief_summary(root)
            sess = self_model.load_current_session(root)
            errs = self_model.validate_invariants(belief, sess)
            self.assertTrue(any("Q-001" in e for e in errs), errs)

            # Even if someone writes the broken markdown verbatim, check_map must return False
            md = self_model.render_md(belief, sess, {"shard_budgets": []}, {})
            (root / "SELF_MODEL.md").write_text(md, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertFalse(self_model.check_map(root))

    def test_source_monitoring_and_agency_trace_separate_forward_labels_from_new_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_jsonl(root / "state" / "notes.jsonl", [])
            _write_jsonl(root / "state" / "read_log.jsonl", [])
            _write_jsonl(root / "state" / "evaluations.jsonl", [])
            # Forward-dated internal label sitting in an older 2026-11-02 shard -> legacy, NOT violation
            _write_jsonl(
                root / "state" / "notes.d" / "2026-11-02-000000000000.jsonl",
                [{"note_id": "NOTE-20270220-aaaaaa", "session_id": "SESSION-20261102-aaaaaa"}],
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(source_monitoring.run_audit(check=True, root=root), 0)

            # Genuine 2026-11-21 shard row missing cognitive_operation -> MUST fail --check
            _write_jsonl(
                root / "state" / "notes.d" / "2026-11-21-000000000000.jsonl",
                [{"note_id": "NOTE-20261121-zzzzzz", "session_id": "SESSION-20261121-zzzzzz"}],
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(source_monitoring.run_audit(check=True, root=root), 1)

            # Genuine 2026-11-21 evaluation missing agency_stance -> MUST fail --check
            _write_jsonl(
                root / "state" / "evaluations.d" / "2026-11-21-000000000000.jsonl",
                [{"evaluation_id": "EVL-20261121-zzzzzz", "session_id": "SESSION-20261121-zzzzzz"}],
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(agency_trace.run_audit(check=True, root=root), 1)


if __name__ == "__main__":
    unittest.main()
