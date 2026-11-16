"""Tests for belief-state audit visibility repairs (NOTE-20261116-7d62c1 §7).

Why this file exists
--------------------
Empirical measurement on 2026-11-16 (readings/2026-11-16-what-crosses-the-unheld-interval.md)
exposed five visibility blind spots in ``tools/belief_state.py``,
``tools/inspect_inquiry.py``, ``tools/validate_seed.py``, and ``tools/witness_count.py``:

1. ``pair_examined_only_by_supports`` fired on 0/221 live pairs even while mutual
   ``supports`` still inflated EIG whenever the top pair's combined mass was
   unsaturated (< 90%).
2. ``belief_state.py`` never read ``materials[*].verification.status`` even
   though 206/313 (65.8%) ``primary_source_collision`` evaluations cited zero
   verified materials while carrying the full 1.20 evidence weight.
3. ``BELIEF_MAP.md`` showed raw evaluation counts rather than distinct
   witnessing sessions (``EVL_sess``) and hand-written non-backfill ``read_log``
   sessions (``RL_sess``), hiding single-witness high-mass hypotheses.
4. Active hypotheses with ``direct_eval_count == 0`` were silently omitted from
   ``top_competing_pair`` without any visible queue in ``BELIEF_MAP.md`` or
   session packets.
5. Same-session self-evaluations (90.5% confirmatory on G1+) were
   indistinguishable from cross-session evaluations.

These tests pin the software behaviour of all five repairs without altering
historical posterior arithmetic or pinning volatile live ledger counts.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402
import validate_seed  # noqa: E402
import witness_count  # noqa: E402


def _make_hyp(
    hid: str,
    *,
    qid: str = "Q-001",
    session_id: str = "SESSION-1",
    parents: list[str] | None = None,
    status: str = "active",
    title: str = "仮説",
) -> dict:
    return {
        "hypothesis_id": hid,
        "question_ids": [qid],
        "session_id": session_id,
        "title": title,
        "proposition": f"{hid} の命題。",
        "scope_conditions": ["条件A"],
        "exclusion_clause": "反証条件A。",
        "lineage_op": "refines" if parents else "root",
        "parent_hypothesis_ids": parents or [],
        "status": status,
        "supporting_material_ids": [],
        "counter_material_ids": [],
        "source_note_ids": [],
    }


def _make_evl(
    eid: str,
    target_hid: str,
    *,
    session_id: str = "SESSION-2",
    verdict: str = "supports",
    evidence_type: str = "primary_source_collision",
    material_ids: list[str] | None = None,
    compared: list[str] | None = None,
    script_command: str | None = None,
) -> dict:
    rec = {
        "evaluation_id": eid,
        "session_id": session_id,
        "target_hypothesis_id": target_hid,
        "compared_against_hypothesis_ids": compared or [],
        "verdict": verdict,
        "evidence_type": evidence_type,
        "material_ids": material_ids if material_ids is not None else [],
        "fragment_ids": [],
        "note_ids": [],
        "errata_ids": [],
        "created_at": "2026-11-16",
    }
    if script_command is not None:
        rec["script_command"] = script_command
    return rec


def _make_mat(mid: str, status: str | None) -> dict:
    rec: dict = {"material_id": mid, "source": {"title": mid}}
    if status is not None:
        rec["verification"] = {"status": status}
    return rec


def _make_read(rid: str, hid: str, session_id: str, *, note: str = "精読メモ", target_type: str = "hypothesis") -> dict:
    return {
        "read_id": rid,
        "session_id": session_id,
        "target": {"type": target_type, "id": hid},
        "note": note,
    }


def _base_data(
    *,
    hypotheses: dict[str, dict],
    evaluations: dict[str, dict],
    materials: dict[str, dict] | None = None,
    read_log: dict[str, dict] | None = None,
) -> dict[str, dict[str, dict]]:
    return {
        "questions": {"Q-001": {"question_id": "Q-001", "question": "テスト問い。"}},
        "hypotheses": hypotheses,
        "evaluations": evaluations,
        "materials": materials or {},
        "read_log": read_log or {},
        "errata": {},
        "fragments": {},
        "sessions": {},
        "notes": {},
    }


class UnsaturatedRatchetTests(unittest.TestCase):
    """§7-1 / §2.2: Top pairs below 90% combined mass flag unsaturated EIG ratchet."""

    def test_threshold_boundary_avoids_float_drift(self) -> None:
        # In IEEE-754 float, 0.6 + 0.3 == 0.8999999999999999 < 0.90;
        # rounding to 6 dp keeps the exact 90% boundary saturated.
        a = {"posterior": 0.60}
        b = {"posterior": 0.30}
        self.assertEqual(belief_state.pair_mass_sum(a, b), 0.9)
        self.assertFalse(belief_state.pair_has_unsaturated_supports_ratchet(a, b))
        self.assertTrue(
            belief_state.pair_has_unsaturated_supports_ratchet(
                {"posterior": 0.5999}, {"posterior": 0.30}
            )
        )

    def test_unsaturated_pair_warns_even_after_adversarial_verdicts(self) -> None:
        # Three active hypotheses with roughly balanced mass so the top two
        # hold < 90% even though both have narrows_scope (adversarial) verdicts.
        hyps = {
            "HYP-A": _make_hyp("HYP-A", session_id="S-1", title="甲"),
            "HYP-B": _make_hyp("HYP-B", session_id="S-1", title="乙"),
            "HYP-C": _make_hyp("HYP-C", session_id="S-1", title="丙"),
        }
        evls = {
            "EVL-1": _make_evl("EVL-1", "HYP-A", session_id="S-2", verdict="supports"),
            "EVL-2": _make_evl("EVL-2", "HYP-A", session_id="S-3", verdict="narrows_scope"),
            "EVL-3": _make_evl("EVL-3", "HYP-B", session_id="S-2", verdict="supports"),
            "EVL-4": _make_evl("EVL-4", "HYP-B", session_id="S-3", verdict="narrows_scope"),
            "EVL-5": _make_evl("EVL-5", "HYP-C", session_id="S-2", verdict="supports"),
            "EVL-6": _make_evl("EVL-6", "HYP-C", session_id="S-3", verdict="narrows_scope"),
        }
        state = belief_state.compute_belief_state(_base_data(hypotheses=hyps, evaluations=evls))
        pair = state["questions"]["Q-001"]["top_competing_pair"]
        self.assertIsNotNone(pair)
        self.assertFalse(pair["examined_only_by_supports"])
        self.assertLess(pair["pair_mass_sum"], belief_state.UNSATURATED_PAIR_MASS_THRESHOLD)
        self.assertTrue(pair["unsaturated_supports_ratchet"])

        rendered = belief_state.render_belief_map_markdown(state)
        self.assertIn("合算占有率:", rendered)
        self.assertIn("未飽和上位対ラチェット注意", rendered)

        _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
        self.assertIn("合算=", reason)
        self.assertIn("未飽和ラチェット注意", reason)

    def test_saturated_pair_stays_quiet_on_unsaturated_ratchet(self) -> None:
        # Two hypotheses share 100% of mass (>= 90%), so no unsaturated ratchet warning.
        hyps = {
            "HYP-A": _make_hyp("HYP-A", session_id="S-1"),
            "HYP-B": _make_hyp("HYP-B", session_id="S-1"),
        }
        evls = {
            "EVL-1": _make_evl("EVL-1", "HYP-A", session_id="S-2", verdict="supports"),
            "EVL-2": _make_evl("EVL-2", "HYP-A", session_id="S-3", verdict="narrows_scope"),
            "EVL-3": _make_evl("EVL-3", "HYP-B", session_id="S-2", verdict="supports"),
            "EVL-4": _make_evl("EVL-4", "HYP-B", session_id="S-3", verdict="narrows_scope"),
        }
        state = belief_state.compute_belief_state(_base_data(hypotheses=hyps, evaluations=evls))
        pair = state["questions"]["Q-001"]["top_competing_pair"]
        self.assertIsNotNone(pair)
        self.assertGreaterEqual(pair["pair_mass_sum"], belief_state.UNSATURATED_PAIR_MASS_THRESHOLD)
        self.assertFalse(pair["unsaturated_supports_ratchet"])

        rendered = belief_state.render_belief_map_markdown(state)
        self.assertNotIn("未飽和上位対ラチェット注意", rendered)

        _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
        self.assertNotIn("未飽和ラチェット注意", reason)


class VerificationAuditTests(unittest.TestCase):
    """§7-2 / §3: Surface material verification.status without altering posteriors."""

    def test_classify_evaluation_verification_covers_all_classes(self) -> None:
        mats = {
            "MAT-V1": _make_mat("MAT-V1", "verified"),
            "MAT-V2": _make_mat("MAT-V2", "verified"),
            "MAT-P1": _make_mat("MAT-P1", "partially_verified"),
            "MAT-U1": _make_mat("MAT-U1", "unverified"),
            "MAT-N1": _make_mat("MAT-N1", None),
        }
        self.assertEqual(
            belief_state.classify_evaluation_verification(
                _make_evl("E1", "H", evidence_type="reproducible_script", script_command="python3 tools/x.py"),
                mats,
            ),
            "script_verified",
        )
        self.assertEqual(
            belief_state.classify_evaluation_verification(
                _make_evl("E2", "H", material_ids=["MAT-V1", "MAT-V2"]), mats
            ),
            "all_verified",
        )
        self.assertEqual(
            belief_state.classify_evaluation_verification(
                _make_evl("E3", "H", material_ids=["MAT-V1", "MAT-P1"]), mats
            ),
            "mixed_verified",
        )
        self.assertEqual(
            belief_state.classify_evaluation_verification(
                _make_evl("E4", "H", material_ids=["MAT-P1", "MAT-U1", "MAT-N1", "MAT-MISSING"]), mats
            ),
            "zero_verified",
        )
        self.assertEqual(
            belief_state.classify_evaluation_verification(
                _make_evl("E5", "H", evidence_type="cross_session_audit", material_ids=[]), mats
            ),
            "no_materials",
        )

    def test_verification_audit_does_not_alter_posteriors_and_renders_badges(self) -> None:
        hyps = {
            "HYP-VER": _make_hyp("HYP-VER", session_id="S-0", title="照合済仮説"),
            "HYP-UNV": _make_hyp("HYP-UNV", session_id="S-0", title="未照合PSC仮説"),
        }
        evls = {
            "EVL-1": _make_evl("EVL-1", "HYP-VER", session_id="S-1", material_ids=["MAT-V"]),
            "EVL-2": _make_evl(
                "EVL-2",
                "HYP-VER",
                session_id="S-2",
                evidence_type="reproducible_script",
                script_command="python3 tools/check.py",
            ),
            "EVL-3": _make_evl("EVL-3", "HYP-UNV", session_id="S-1", material_ids=["MAT-U"]),
        }
        mats_before = {
            "MAT-V": _make_mat("MAT-V", "verified"),
            "MAT-U": _make_mat("MAT-U", "unverified"),
        }
        mats_after = {
            "MAT-V": _make_mat("MAT-V", "verified"),
            "MAT-U": _make_mat("MAT-U", "verified"),
        }
        s_before = belief_state.compute_belief_state(
            _base_data(hypotheses=hyps, evaluations=evls, materials=mats_before)
        )
        s_after = belief_state.compute_belief_state(
            _base_data(hypotheses=hyps, evaluations=evls, materials=mats_after)
        )

        by_id_before = {h["hypothesis_id"]: h for h in s_before["questions"]["Q-001"]["hypotheses"]}
        by_id_after = {h["hypothesis_id"]: h for h in s_after["questions"]["Q-001"]["hypotheses"]}

        # Historical posterior arithmetic must remain invariant under verification.status edits.
        for hid in ("HYP-VER", "HYP-UNV"):
            self.assertEqual(by_id_before[hid]["log_odds"], by_id_after[hid]["log_odds"])
            self.assertEqual(by_id_before[hid]["posterior"], by_id_after[hid]["posterior"])

        self.assertEqual(by_id_before["HYP-VER"]["verified_material_eval_count"], 1)
        self.assertEqual(by_id_before["HYP-VER"]["script_eval_count"], 1)
        self.assertEqual(by_id_before["HYP-VER"]["verified_direct_eval_count"], 2)
        self.assertEqual(by_id_before["HYP-UNV"]["psc_eval_count"], 1)
        self.assertEqual(by_id_before["HYP-UNV"]["psc_zero_verified_count"], 1)
        self.assertEqual(by_id_after["HYP-UNV"]["psc_all_verified_count"], 1)

        prov = s_before["provenance_verification"]
        self.assertEqual(prov["psc_total"], 2)
        self.assertEqual(prov["psc_all_verified"], 1)
        self.assertEqual(prov["psc_zero_verified"], 1)

        rendered = belief_state.render_belief_map_markdown(s_before)
        self.assertIn("照合済 (PSC全照合)", rendered)
        self.assertIn("1+1S/2 (PSC 1/1)", rendered)
        self.assertIn("0/1 (PSC 0/1)", rendered)
        self.assertIn("PSC未照合のみ", rendered)
        self.assertIn("`primary_source_collision` 素材照合監査", rendered)

    def test_validate_seed_psc_advisory_reports_counts_and_is_none_when_empty(self) -> None:
        self.assertIsNone(validate_seed.psc_verification_advisory({}, {}))
        mats = {
            "M1": _make_mat("M1", "verified"),
            "M2": _make_mat("M2", "partially_verified"),
        }
        evls = {
            "E1": _make_evl("E1", "H", material_ids=["M1"]),
            "E2": _make_evl("E2", "H", material_ids=["M1", "M2"]),
            "E3": _make_evl("E3", "H", material_ids=["M2"]),
            "E4": _make_evl("E4", "H", evidence_type="cross_session_audit", material_ids=["M2"]),
        }
        msg = validate_seed.psc_verification_advisory(evls, mats)
        self.assertIsNotNone(msg)
        self.assertIn("1/3 (33.3%) all-verified", msg)
        self.assertIn("1 mixed", msg)
        self.assertIn("1 zero-verified", msg)


class WitnessAndSelfEvaluationTests(unittest.TestCase):
    """§7-3 / §5.2 / §4: Independent EVL_sess, non-backfill RL_sess, and self-eval flags."""

    def test_hypothesis_read_witnesses_excludes_mechanical_backfill_and_non_hypotheses(self) -> None:
        read_log = {
            "R1": _make_read("R1", "HYP-A", "S-1", note="精読により検証"),
            "R2": _make_read("R2", "HYP-A", "S-1", note="同一セッションの2行目"),
            "R3": _make_read("R3", "HYP-A", "S-2", note="機械的バックフィル（コンテキスト）"),
            "R4": _make_read("R4", "HYP-A", "S-3", note="手書きで文脈参照"),
            "R5": _make_read("R5", "MAT-1", "S-4", note="資料精読", target_type="material"),
        }
        wit = belief_state.hypothesis_read_witnesses(read_log)
        self.assertEqual(wit["HYP-A"], {"S-1", "S-3"})
        self.assertNotIn("MAT-1", wit)
        # witness_count.py uses the exact same filter
        self.assertEqual(witness_count.witnesses_by_hypothesis(list(read_log.values()))["HYP-A"], {"S-1", "S-3"})

    def test_single_witness_and_self_evaluated_flags_trigger_and_clear_accurately(self) -> None:
        hyps = {
            "HYP-SELF": _make_hyp("HYP-SELF", session_id="S-OWNER", title="自己評価のみ仮説"),
            "HYP-MULTI": _make_hyp("HYP-MULTI", session_id="S-OWNER", title="複数証人仮説"),
        }
        # HYP-SELF has 2 direct evaluations, BOTH from its own creating session (EVL_sess=1, cross=0).
        # HYP-MULTI has 2 evaluations from 2 distinct external sessions (EVL_sess=2, cross=2).
        evls = {
            "E1": _make_evl("E1", "HYP-SELF", session_id="S-OWNER", verdict="supports"),
            "E2": _make_evl("E2", "HYP-SELF", session_id="S-OWNER", verdict="supports"),
            "E3": _make_evl("E3", "HYP-MULTI", session_id="S-EXT1", verdict="supports"),
            "E4": _make_evl("E4", "HYP-MULTI", session_id="S-EXT2", verdict="narrows_scope"),
        }
        rlog = {
            "R1": _make_read("R1", "HYP-SELF", "S-EXT1", note="機械的バックフィル"),
            "R2": _make_read("R2", "HYP-MULTI", "S-EXT1", note="手書き読了"),
            "R3": _make_read("R3", "HYP-MULTI", "S-EXT2", note="手書き読了"),
        }
        state = belief_state.compute_belief_state(
            _base_data(hypotheses=hyps, evaluations=evls, read_log=rlog)
        )
        by_id = {h["hypothesis_id"]: h for h in state["questions"]["Q-001"]["hypotheses"]}

        h_self = by_id["HYP-SELF"]
        self.assertEqual(h_self["direct_eval_count"], 2)
        self.assertEqual(h_self["witness_eval_session_count"], 1)
        self.assertEqual(h_self["witness_read_session_count"], 0)
        self.assertEqual(h_self["same_session_eval_count"], 2)
        self.assertEqual(h_self["cross_session_eval_count"], 0)
        self.assertTrue(h_self["low_witness_high_mass"])
        self.assertTrue(h_self["self_evaluated_only"])

        h_multi = by_id["HYP-MULTI"]
        self.assertEqual(h_multi["witness_eval_session_count"], 2)
        self.assertEqual(h_multi["witness_read_session_count"], 2)
        self.assertEqual(h_multi["same_session_eval_count"], 0)
        self.assertEqual(h_multi["cross_session_eval_count"], 2)
        self.assertFalse(h_multi["low_witness_high_mass"])
        self.assertFalse(h_multi["self_evaluated_only"])

        rendered = belief_state.render_belief_map_markdown(state)
        self.assertIn("証人 (EVL/読)", rendered)
        self.assertIn("1 / 0 ⚠️単一証人 ⚠️自己評価のみ", rendered)
        self.assertIn("単一証人高質量", rendered)
        self.assertIn("自己評価のみ", rendered)
        self.assertIn("監査メタ", rendered)


class UnexaminedActiveVisibilityTests(unittest.TestCase):
    """§2.1 / §5.1: Active hypotheses with 0 direct evaluations are explicitly surfaced."""

    def test_unexamined_active_hypothesis_surfaces_alongside_top_pair(self) -> None:
        hyps = {
            "HYP-A": _make_hyp("HYP-A", session_id="S-1", title="評価済A"),
            "HYP-B": _make_hyp("HYP-B", session_id="S-1", title="評価済B"),
            "HYP-NEW": _make_hyp("HYP-NEW", session_id="S-2", title="未評価新規仮説"),
        }
        # Both HYP-A and HYP-B remain active (have supports + narrows_scope),
        # while HYP-NEW stays unexamined (direct_eval_count == 0).
        evls = {
            "E1": _make_evl("E1", "HYP-A", session_id="S-3", verdict="supports"),
            "E2": _make_evl("E2", "HYP-A", session_id="S-4", verdict="narrows_scope"),
            "E3": _make_evl("E3", "HYP-B", session_id="S-3", verdict="supports"),
            "E4": _make_evl("E4", "HYP-B", session_id="S-4", verdict="narrows_scope"),
        }
        data = _base_data(hypotheses=hyps, evaluations=evls)
        state = belief_state.compute_belief_state(data)
        qs = state["questions"]["Q-001"]

        self.assertEqual(qs["unexamined_active_hypothesis_ids"], ["HYP-NEW"])
        # Still excluded from top_competing_pair
        pair = qs["top_competing_pair"]
        self.assertIsNotNone(pair)
        self.assertNotIn("HYP-NEW", (pair["left_hypothesis_id"], pair["right_hypothesis_id"]))
        self.assertTrue(pair["unsaturated_supports_ratchet"])

        rendered = belief_state.render_belief_map_markdown(state)
        self.assertIn("未評価の有効仮説（ペア推薦から除外中）", rendered)
        self.assertIn("`HYP-NEW`", rendered)

        _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
        self.assertIn("未評価有効仮説=1件", reason)

        briefing_lines, _role = inspect_inquiry._belief_briefing_lines(
            data, "Q-001", seed_label="test-seed", errata={}
        )
        briefing = "\n".join(briefing_lines)
        self.assertIn("未評価有効仮説", briefing)
        self.assertIn("`HYP-NEW`", briefing)
        self.assertIn("未飽和ラチェット注意", briefing)

    def test_unexamined_active_hypothesis_also_surfaces_when_no_pair_exists(self) -> None:
        hyps = {
            "HYP-A": _make_hyp("HYP-A", session_id="S-1", title="評価済A"),
            "HYP-NEW": _make_hyp("HYP-NEW", session_id="S-2", title="未評価新規仮説"),
        }
        evls = {
            "E1": _make_evl("E1", "HYP-A", session_id="S-3", verdict="supports"),
        }
        state = belief_state.compute_belief_state(_base_data(hypotheses=hyps, evaluations=evls))
        qs = state["questions"]["Q-001"]
        self.assertIsNone(qs["top_competing_pair"])
        self.assertEqual(qs["unexamined_active_hypothesis_ids"], ["HYP-NEW"])

        rendered = belief_state.render_belief_map_markdown(state)
        self.assertIn("推薦なし", rendered)
        self.assertIn("未評価の有効仮説（ペア推薦から除外中）", rendered)
        self.assertIn("`HYP-NEW`", rendered)


class WitnessCountCliHypothesesTests(unittest.TestCase):
    """Verify witness_count.py --hypotheses connects cleanly to belief_state."""

    def test_witness_count_hypotheses_json_matches_belief_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "state").mkdir(parents=True)
            for name in ("fragments", "sessions", "notes"):
                (root / "state" / f"{name}.jsonl").write_text("", encoding="utf-8")
            (root / "state" / "questions.jsonl").write_text(
                json.dumps({"question_id": "Q-001", "question": "問い。"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (root / "state" / "materials.jsonl").write_text(
                json.dumps(_make_mat("MAT-1", "verified"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (root / "state" / "hypotheses.jsonl").write_text(
                json.dumps(_make_hyp("HYP-1", session_id="S-1"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (root / "state" / "evaluations.jsonl").write_text(
                json.dumps(
                    _make_evl("EVL-1", "HYP-1", session_id="S-1", material_ids=["MAT-1"]),
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "state" / "read_log.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(_make_read("R-1", "HYP-1", "S-2", note="手書き精読"), ensure_ascii=False),
                        json.dumps(_make_read("R-2", "HYP-1", "S-3", note="機械的バックフィル"), ensure_ascii=False),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(TOOLS / "witness_count.py"), "--hypotheses", "--json", "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            h_report = payload["hypotheses"]
            self.assertEqual(h_report["total_hypotheses"], 1)
            self.assertEqual(h_report["single_witness_high_mass"], ["Q-001:HYP-1"])
            self.assertEqual(h_report["self_evaluated_only"], ["Q-001:HYP-1"])
            row = h_report["hypotheses"][0]
            self.assertEqual(row["witness_eval_session_count"], 1)
            self.assertEqual(row["witness_read_session_count"], 1)
            self.assertEqual(row["verified_direct_eval_count"], 1)


if __name__ == "__main__":
    unittest.main()
