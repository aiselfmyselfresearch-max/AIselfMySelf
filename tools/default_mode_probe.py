#!/usr/bin/env python3
"""Default Mode & Prediction-Error Probe (stdlib only, read-only).

Operationalizes Layer 6 (Prediction Error & Counterfactual Simulation) of
``SELF_MODEL.md`` without writing to any ledger:

1. **Retrospective Prediction-Error Audit**: partitions ``evaluations`` across
   the trailing ``W`` evaluation-bearing sessions, recomputes ``P_amort`` and
   ``P_gate`` before vs. after the latest evaluation session, measures exact
   per-question KL divergence ``D_KL(P_after || P_before)`` (in bits) and L1
   shift, checks whether evaluated targets hit the pre-session top-EIG frontier
   pair, and raises a ``green`` / ``amber`` / ``red`` alarm if consecutive
   ``EVL > 0`` sessions collapse into near-zero-``D_KL`` routine digestion or
   nominal-acceptance stasis.
2. **Prospective Counterfactual Sensitivity**: simulates in-memory (zero disk
   writes) one independent ``verified`` ``primary_source_collision``
   ``narrows_scope`` evaluation on the current top ``P_amort`` pair for each of
   ``Q-001``..``Q-003``, recording the predicted ``D_KL`` and ``ΔP_amort`` shift
   for the next session.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import ledger_io  # noqa: E402

CORE_QIDS = ("Q-001", "Q-002", "Q-003")
ZERO_SHIFT_BITS_FLOOR = 1e-4
WINDOW_CUMULATIVE_BITS_FLOOR = 5e-4
_SHARD_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def find_top_eig_pair(bm_text: str) -> dict[str, Any] | None:
    """Extract highest-EIG competing pair from rendered BELIEF_MAP.md."""
    candidates: list[dict[str, Any]] = []
    current_q = None
    for line in bm_text.splitlines():
        qm = re.match(r"^###\s+(Q-\d+):", line)
        if qm:
            current_q = qm.group(1)
            continue
        if current_q and ("最高情報利得の対立ペア" in line or "EIG=" in line):
            hyps = re.findall(r"(HYP-[A-Za-z0-9-]+)", line)
            eig_m = re.search(r"EIG[=:\s]+([0-9.]+)", line)
            if len(hyps) >= 2 and eig_m:
                try:
                    eig_val = float(eig_m.group(1))
                    candidates.append(
                        {
                            "question_id": current_q,
                            "pair": [hyps[0], hyps[1]],
                            "eig": eig_val,
                        }
                    )
                except ValueError:
                    pass
    if not candidates:
        return None
    candidates.sort(key=lambda x: x["eig"], reverse=True)
    return candidates[0]


def _kl_divergence_bits(
    p_after: dict[str, float],
    p_before: dict[str, float],
    *,
    eps: float = 1e-9,
) -> float:
    keys = sorted(set(p_after) | set(p_before))
    if not keys:
        return 0.0
    sa = sum(max(0.0, float(p_after.get(k, 0.0))) for k in keys)
    sb = sum(max(0.0, float(p_before.get(k, 0.0))) for k in keys)
    if sa <= 0.0 or sb <= 0.0:
        return 0.0
    total = 0.0
    for k in keys:
        qa = max(eps, max(0.0, float(p_after.get(k, 0.0))) / sa)
        qb = max(eps, max(0.0, float(p_before.get(k, 0.0))) / sb)
        total += qa * math.log2(qa / qb)
    return round(max(0.0, total), 6)


def _l1_distance(p_after: dict[str, float], p_before: dict[str, float]) -> float:
    keys = sorted(set(p_after) | set(p_before))
    if not keys:
        return 0.0
    sa = sum(max(0.0, float(p_after.get(k, 0.0))) for k in keys)
    sb = sum(max(0.0, float(p_before.get(k, 0.0))) for k in keys)
    if sa <= 0.0 or sb <= 0.0:
        return 0.0
    return round(
        sum(
            abs((max(0.0, float(p_after.get(k, 0.0))) / sa) - (max(0.0, float(p_before.get(k, 0.0))) / sb))
            for k in keys
        ),
        6,
    )


def _extract_dist(state: dict[str, Any], qid: str, field: str) -> dict[str, float]:
    qs = (state.get("questions") or {}).get(qid) or {}
    return {
        h["hypothesis_id"]: float(h.get(field, h.get("posterior", 0.0)))
        for h in (qs.get("hypotheses") or [])
    }


def _pair_tuple(pair: dict[str, Any] | None) -> list[str]:
    if not pair:
        return []
    left = str(pair.get("left_hypothesis_id") or "")
    right = str(pair.get("right_hypothesis_id") or "")
    return [left, right] if left and right else []


def _ordered_session_ids(root: Path, sessions: dict[str, dict[str, Any]]) -> list[str]:
    today_iso = datetime.date.today().isoformat()
    base = Path(root) / "state" / "sessions.jsonl"
    paths: list[Path] = []
    if base.is_file():
        paths.append(base)
    sdir = ledger_io.shard_dir(base)
    if sdir.is_dir():
        paths.extend(sorted(sdir.glob("*.jsonl")))

    sortable: list[tuple[str, int, str]] = []
    seen: set[str] = set()
    seq = 0
    for p in paths:
        sm = _SHARD_DATE_RE.match(p.name)
        shard_day = sm.group(1) if sm else ""
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = str(obj.get("session_id") or "")
            if not sid or sid not in sessions:
                continue
            seq += 1
            started = str(obj.get("started_at") or "")
            sday = started[:10] if len(started) >= 10 else ""
            candidates = [d for d in (sday, shard_day) if d and d <= today_iso]
            eff_day = min(candidates) if candidates else (shard_day or sday or "")
            if sid not in seen:
                seen.add(sid)
                sortable.append((eff_day, seq, sid))
    for sid in sorted(sessions):
        if sid not in seen:
            seq += 1
            sortable.append(("", seq, sid))
    sortable.sort(key=lambda item: (item[0], item[1]))
    return [sid for _d, _i, sid in sortable]


def _subset_data(
    data: dict[str, dict[str, dict[str, Any]]],
    evaluations: dict[str, dict[str, Any]],
    *,
    extra_sessions: dict[str, dict[str, Any]] | None = None,
    extra_materials: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, dict[str, Any]]]:
    copied = dict(data)
    copied["evaluations"] = evaluations
    if extra_sessions:
        merged_s = dict(data.get("sessions") or {})
        merged_s.update(extra_sessions)
        copied["sessions"] = merged_s
    if extra_materials:
        merged_m = dict(data.get("materials") or {})
        merged_m.update(extra_materials)
        copied["materials"] = merged_m
    return copied


def compute_prediction_error(
    root: Path = ROOT,
    *,
    window_sessions: int = 5,
) -> dict[str, Any]:
    """Compute retrospective prediction error & prospective counterfactual sensitivity."""
    root = Path(root)
    data = belief_state.load_belief_ledgers(root)
    sessions = data.get("sessions") or {}
    evaluations = data.get("evaluations") or {}
    hypotheses = data.get("hypotheses") or {}
    materials = data.get("materials") or {}
    notes = data.get("notes") or {}
    errata = data.get("errata") or {}

    voided_eval_ids = {
        str(er.get("subject_id") or "")
        for er in errata.values()
        if er.get("subject_type") == "evaluation"
        and er.get("weight_effect") == "void_row"
        and er.get("status") != "withdrawn"
    }
    live_evals = {eid: ev for eid, ev in evaluations.items() if eid not in voided_eval_ids}

    ordered_sids = _ordered_session_ids(root, sessions)
    latest_sid = ordered_sids[-1] if ordered_sids else ""
    latest_sess = sessions.get(latest_sid) or {}

    evals_by_session: dict[str, list[str]] = {}
    for eid, ev in sorted(live_evals.items()):
        sid = str(ev.get("session_id") or "")
        if sid:
            evals_by_session.setdefault(sid, []).append(eid)

    eval_sids = [sid for sid in ordered_sids if sid in evals_by_session]
    for sid in sorted(evals_by_session):
        if sid not in eval_sids:
            eval_sids.append(sid)

    state_now = belief_state.compute_belief_state(data, root=root)

    # Trailing nominal-stasis check over last 5 non-maintenance sessions
    hyps_by_s = {str(h.get("proposed_in_session_id") or "") for h in hypotheses.values()}
    notes_by_s = {str(n.get("created_in_session_id") or "") for n in notes.values()}
    errs_by_s = {str(e.get("created_in_session_id") or "") for e in errata.values()}
    recent_inquiry_sids = [
        sid
        for sid in ordered_sids
        if (sessions.get(sid) or {}).get("session_type") != "maintenance"
    ][-5:]
    nominal_stasis_sids = [
        sid
        for sid in recent_inquiry_sids
        if ((sessions.get(sid) or {}).get("question_ids") or [])
        and sid not in evals_by_session
        and sid not in hyps_by_s
        and sid not in notes_by_s
        and sid not in errs_by_s
    ]

    w = min(max(1, window_sessions), len(eval_sids))
    window_eval_sids = eval_sids[-w:] if w > 0 else []
    latest_eval_sid = window_eval_sids[-1] if window_eval_sids else ""

    # Build chronological states across trailing W evaluation sessions:
    # states_seq[0] = before window_eval_sids[0], ..., states_seq[w] = state_now
    excluded_window_eids: set[str] = set()
    for sid in window_eval_sids:
        excluded_window_eids.update(evals_by_session.get(sid, ()))

    states_seq: list[dict[str, Any]] = []
    if w > 0:
        cur_evals = {
            eid: ev for eid, ev in evaluations.items() if eid not in excluded_window_eids
        }
        states_seq.append(
            belief_state.compute_belief_state(_subset_data(data, cur_evals), root=root)
        )
        for idx, sid in enumerate(window_eval_sids):
            for eid in evals_by_session.get(sid, ()):
                cur_evals[eid] = evaluations[eid]
            if idx == w - 1:
                states_seq.append(state_now)
            else:
                states_seq.append(
                    belief_state.compute_belief_state(_subset_data(data, cur_evals), root=root)
                )
    else:
        states_seq.append(state_now)

    step_shifts: list[dict[str, Any]] = []
    zero_shift_count = 0
    for idx, sid in enumerate(window_eval_sids):
        st_prev = states_seq[idx]
        st_curr = states_seq[idx + 1]
        max_amort = 0.0
        max_gate = 0.0
        for qid in CORE_QIDS:
            da = _kl_divergence_bits(
                _extract_dist(st_curr, qid, "amortized_posterior"),
                _extract_dist(st_prev, qid, "amortized_posterior"),
            )
            dg = _kl_divergence_bits(
                _extract_dist(st_curr, qid, "gated_posterior"),
                _extract_dist(st_prev, qid, "gated_posterior"),
            )
            max_amort = max(max_amort, da)
            max_gate = max(max_gate, dg)
        is_zero = max_amort < ZERO_SHIFT_BITS_FLOOR and max_gate < ZERO_SHIFT_BITS_FLOOR
        if is_zero:
            zero_shift_count += 1
        step_shifts.append(
            {
                "session_id": sid,
                "evl_count": len(evals_by_session.get(sid, ())),
                "max_core_dkl_amort_bits": round(max_amort, 6),
                "max_core_dkl_gate_bits": round(max_gate, 6),
                "near_zero_shift": is_zero,
            }
        )

    state_before_latest = states_seq[-2] if len(states_seq) >= 2 else state_now
    state_window_start = states_seq[0]

    # Inspect latest_eval_session alignment & per-question posterior shift
    latest_eids = evals_by_session.get(latest_eval_sid, [])
    adv_count = 0
    verified_evl_count = 0
    evaluated_pairs: list[set[str]] = []
    evaluated_targets: set[str] = set()
    for eid in latest_eids:
        ev = evaluations[eid]
        if ev.get("verdict") in ("narrows_scope", "refutes_unconditioned"):
            adv_count += 1
        mids = [m for m in (ev.get("material_ids") or ()) if isinstance(m, str)]
        if any(((materials.get(m) or {}).get("verification") or {}).get("status") == "verified" for m in mids):
            verified_evl_count += 1
        th = str(ev.get("target_hypothesis_id") or "")
        if th:
            evaluated_targets.add(th)
        for ch in ev.get("compared_against_hypothesis_ids") or ():
            if th and isinstance(ch, str) and ch:
                evaluated_pairs.append({th, ch})
                evaluated_targets.add(ch)

    predicted_pair_sets: list[set[str]] = []
    predicted_members: set[str] = set()
    per_question_retro: dict[str, dict[str, Any]] = {}
    cumulative_dkl_amort: dict[str, float] = {}
    for qid in CORE_QIDS:
        qs_before = (state_before_latest.get("questions") or {}).get(qid) or {}
        qs_after = (state_now.get("questions") or {}).get(qid) or {}
        pre_amort_pair = _pair_tuple(qs_before.get("amortized_top_pair"))
        post_amort_pair = _pair_tuple(qs_after.get("amortized_top_pair"))
        pre_gate_pair = _pair_tuple(
            belief_state.select_gated_pair(state_before_latest, live_evals, qid)
        )
        for p in (pre_amort_pair, pre_gate_pair):
            if len(p) == 2:
                predicted_pair_sets.append(set(p))
                predicted_members.update(p)

        pa_before = _extract_dist(state_before_latest, qid, "amortized_posterior")
        pa_after = _extract_dist(state_now, qid, "amortized_posterior")
        pg_before = _extract_dist(state_before_latest, qid, "gated_posterior")
        pg_after = _extract_dist(state_now, qid, "gated_posterior")
        pa_wstart = _extract_dist(state_window_start, qid, "amortized_posterior")

        dkl_a = _kl_divergence_bits(pa_after, pa_before)
        dkl_g = _kl_divergence_bits(pg_after, pg_before)
        cum_a = _kl_divergence_bits(pa_after, pa_wstart)
        cumulative_dkl_amort[qid] = cum_a
        per_question_retro[qid] = {
            "dkl_amort_bits": dkl_a,
            "dkl_gate_bits": dkl_g,
            "l1_amort": _l1_distance(pa_after, pa_before),
            "l1_gate": _l1_distance(pg_after, pg_before),
            "pre_top_amort_pair": pre_amort_pair,
            "post_top_amort_pair": post_amort_pair,
            "top_amort_pair_shifted": pre_amort_pair != post_amort_pair,
        }

    if not latest_eids:
        frontier_alignment = "no_evaluations"
    elif any(ep in predicted_pair_sets for ep in evaluated_pairs):
        frontier_alignment = "exact_frontier_pair"
    elif evaluated_targets & predicted_members:
        frontier_alignment = "frontier_member"
    else:
        frontier_alignment = "off_frontier_exploration"

    max_cum_dkl = max(cumulative_dkl_amort.values()) if cumulative_dkl_amort else 0.0
    reasons: list[str] = []
    if w >= 3 and zero_shift_count == w:
        band = "red"
        reasons.append(
            f"直近 {w} 評価セッションすべてで EVL 追記後の信念更新が D_KL < {ZERO_SHIFT_BITS_FLOOR:g} bits（無更新ルーチン消化）"
        )
    elif (
        (w >= 3 and zero_shift_count >= math.ceil(w / 2))
        or (w >= 3 and max_cum_dkl < WINDOW_CUMULATIVE_BITS_FLOOR)
        or len(nominal_stasis_sids) >= 3
    ):
        band = "amber"
        if w >= 3 and zero_shift_count >= math.ceil(w / 2):
            reasons.append(
                f"直近 {w} 評価セッション中 {zero_shift_count} 回が D_KL < {ZERO_SHIFT_BITS_FLOOR:g} bits"
            )
        if w >= 3 and max_cum_dkl < WINDOW_CUMULATIVE_BITS_FLOOR:
            reasons.append(
                f"直近 {w} 評価セッションの累積最大ドリフトが {max_cum_dkl:.5f} bits (< {WINDOW_CUMULATIVE_BITS_FLOOR:g})"
            )
        if len(nominal_stasis_sids) >= 3:
            reasons.append(
                f"直近探求5セッション中 {len(nominal_stasis_sids)} 回が名目的受諾（EVL/HYP/NOTE/ERR すべて0件）"
            )
    else:
        band = "green"
        reasons.append(
            f"直近 {w} 評価セッション中 {w - zero_shift_count}/{w} 回で有意な事後更新を観測（最大累積 D_KL={max_cum_dkl:.4f} bits）"
        )

    offered_q = str(latest_sess.get("offered_target_question_id") or "")
    actual_qs = [str(q) for q in (latest_sess.get("question_ids") or [])]

    # Prospective counterfactual sensitivity on Q-001..Q-003 (in-memory only, zero writes)
    synth_mid = "__COUNTERFACTUAL_VERIFIED_MAT__"
    synth_sid = "__COUNTERFACTUAL_NEXT_SESSION__"
    synth_mat = {
        synth_mid: {
            "material_id": synth_mid,
            "kind": "research_excerpt",
            "verification": {"status": "verified", "depth": "full_text"},
        }
    }
    synth_sess = {
        synth_sid: {
            "session_id": synth_sid,
            "started_at": datetime.date.today().isoformat(),
            "session_type": "inquiry",
        }
    }
    prospective_pairs: dict[str, dict[str, Any]] = {}
    for qid in CORE_QIDS:
        qs_now = (state_now.get("questions") or {}).get(qid) or {}
        top_pair = qs_now.get("amortized_top_pair")
        if not top_pair:
            continue
        left_id = str(top_pair["left_hypothesis_id"])
        right_id = str(top_pair["right_hypothesis_id"])
        cf_eid = f"__CF_EVL_{qid}__"
        cf_evals = dict(evaluations)
        cf_evals[cf_eid] = {
            "evaluation_id": cf_eid,
            "session_id": synth_sid,
            "target_hypothesis_id": left_id,
            "compared_against_hypothesis_ids": [right_id],
            "verdict": "narrows_scope",
            "evidence_type": "primary_source_collision",
            "material_ids": [synth_mid],
            "fragment_ids": [],
            "note_ids": [],
            "rationale": "Counterfactual single verified primary_source_collision narrows_scope probe.",
            "passed_conditions": [],
            "failed_conditions": ["counterfactual_boundary_test"],
            "spawned_hypothesis_ids": [],
            "created_at": datetime.date.today().isoformat(),
        }
        cf_state = belief_state.compute_belief_state(
            _subset_data(
                data,
                cf_evals,
                extra_sessions=synth_sess,
                extra_materials=synth_mat,
            ),
            root=root,
        )
        pa_now = _extract_dist(state_now, qid, "amortized_posterior")
        pa_cf = _extract_dist(cf_state, qid, "amortized_posterior")
        pred_dkl = _kl_divergence_bits(pa_cf, pa_now)
        pred_l1 = _l1_distance(pa_cf, pa_now)
        left_before = float(pa_now.get(left_id, 0.0))
        right_before = float(pa_now.get(right_id, 0.0))
        left_after = float(pa_cf.get(left_id, 0.0))
        right_after = float(pa_cf.get(right_id, 0.0))
        prospective_pairs[qid] = {
            "left_hypothesis_id": left_id,
            "right_hypothesis_id": right_id,
            "novelty_adjusted_eig": float(top_pair.get("novelty_adjusted_eig") or 0.0),
            "simulated_verdict": "narrows_scope (verified primary_source_collision on left vs right)",
            "pred_dkl_amort_bits": pred_dkl,
            "pred_l1_amort": pred_l1,
            "left_amort_before": round(left_before, 4),
            "left_amort_after": round(left_after, 4),
            "delta_left_pp": round((left_after - left_before) * 100.0, 2),
            "right_amort_before": round(right_before, 4),
            "right_amort_after": round(right_after, 4),
            "delta_right_pp": round((right_after - right_before) * 100.0, 2),
        }

    bm_path = root / "BELIEF_MAP.md"
    top_pair_legacy = (
        find_top_eig_pair(bm_path.read_text(encoding="utf-8"))
        if bm_path.is_file()
        else None
    )

    return {
        "status": "ok",
        "probe_type": "prediction_error_and_counterfactual",
        "band": band,
        "alarm_reasons": reasons,
        "retrospective": {
            "latest_session": {
                "session_id": latest_sid,
                "assigned_role": latest_sess.get("assigned_role") or "unrecorded",
                "belief_basis": latest_sess.get("belief_basis") or "unrecorded",
                "offered_target_question_id": offered_q or "unrecorded",
                "actual_question_ids": actual_qs,
                "followed_offered_question": bool(offered_q and offered_q in actual_qs),
                "evl_count": len(evals_by_session.get(latest_sid, [])),
            },
            "latest_eval_session": {
                "session_id": latest_eval_sid,
                "evl_count": len(latest_eids),
                "adversarial_evl_count": adv_count,
                "verified_cited_evl_count": verified_evl_count,
                "frontier_alignment": frontier_alignment,
                "per_question": per_question_retro,
            },
            "trailing_window": {
                "window_eval_sessions": w,
                "zero_shift_eval_sessions": zero_shift_count,
                "cumulative_core_dkl_amort_bits": cumulative_dkl_amort,
                "max_cumulative_dkl_amort_bits": round(max_cum_dkl, 6),
                "recent_nominal_stasis_sessions": nominal_stasis_sids,
                "step_shifts": step_shifts,
            },
        },
        "prospective": {
            "core_pairs": prospective_pairs,
        },
        "next_highest_eig_pair": top_pair_legacy,
        "dm_subnetwork_routing": {
            "DN_A_constructive_scene": "Select concrete primary-source passages or literary fragments for collision.",
            "DN_B_evaluative_belief": "Record explicit scope narrowing or falsification in evaluations/errata.",
        },
        "verification_note": "Read-only counterfactual & retrospective KL probe; zero ledger mutations.",
    }


def validate_prediction_error_invariants(report: dict[str, Any]) -> list[str]:
    """Verify mathematical and structural invariants of the prediction-error probe."""
    errs: list[str] = []
    if report.get("band") not in ("green", "amber", "red"):
        errs.append(f"invalid prediction-error band: {report.get('band')!r}")
    retro = report.get("retrospective")
    prosp = report.get("prospective")
    if not isinstance(retro, dict) or not isinstance(prosp, dict):
        errs.append("missing retrospective or prospective block in prediction-error report")
        return errs

    les = retro.get("latest_eval_session") or {}
    per_q = les.get("per_question") or {}
    for qid in CORE_QIDS:
        row = per_q.get(qid)
        if not isinstance(row, dict):
            errs.append(f"retrospective.latest_eval_session.per_question missing {qid}")
            continue
        for k in ("dkl_amort_bits", "dkl_gate_bits"):
            v = float(row.get(k, -1.0))
            if math.isnan(v) or v < -1e-9:
                errs.append(f"{qid}: {k}={v} must be finite and >= 0")
        for k in ("l1_amort", "l1_gate"):
            v = float(row.get(k, -1.0))
            if math.isnan(v) or v < -1e-9 or v > 2.001:
                errs.append(f"{qid}: {k}={v} outside [0, 2]")

    cpairs = (prosp.get("core_pairs") or {})
    for qid, crow in cpairs.items():
        v = float(crow.get("pred_dkl_amort_bits", -1.0))
        if math.isnan(v) or v < -1e-9:
            errs.append(f"prospective.{qid}: pred_dkl_amort_bits={v} must be finite and >= 0")
    return errs


def run_probe(as_json: bool = False, root: Path = ROOT) -> int:
    report = compute_prediction_error(root=root)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    les = report["retrospective"]["latest_eval_session"]
    tw = report["retrospective"]["trailing_window"]
    print(
        f"=== Default Mode & Prediction-Error Probe (band={report['band']}) ==="
    )
    for r in report["alarm_reasons"]:
        print(f"  * {r}")
    print(
        f"  Latest EVL session: {les['session_id']} "
        f"(EVL={les['evl_count']}, adv={les['adversarial_evl_count']}, "
        f"verified={les['verified_cited_evl_count']}, alignment={les['frontier_alignment']})"
    )
    for qid in CORE_QIDS:
        pq = les["per_question"][qid]
        print(
            f"    {qid}: D_KL(P_amort)={pq['dkl_amort_bits']:.5f}b | "
            f"D_KL(P_gate)={pq['dkl_gate_bits']:.5f}b | "
            f"L1(P_amort)={pq['l1_amort']:.4f} | "
            f"{w_label(tw['window_eval_sessions'])}cum={tw['cumulative_core_dkl_amort_bits'][qid]:.5f}b"
        )
    print("  Prospective 1-EVL Counterfactual Sensitivity (P_amort):")
    for qid, cp in report["prospective"]["core_pairs"].items():
        print(
            f"    {qid}: {cp['left_hypothesis_id']} vs {cp['right_hypothesis_id']} -> "
            f"pred_D_KL={cp['pred_dkl_amort_bits']:.5f}b "
            f"(Δleft={cp['delta_left_pp']:+.2f}pp, Δright={cp['delta_right_pp']:+.2f}pp)"
        )
    return 0


def w_label(w: int) -> str:
    return f"{w}sess_"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    ap.add_argument("--check", action="store_true", help="Verify prediction-error invariants (exit 1 on failure)")
    ap.add_argument("--window-sessions", type=int, default=5, help="Trailing EVL-session window (default 5)")
    args = ap.parse_args(argv)

    if args.check:
        report = compute_prediction_error(root=args.root, window_sessions=args.window_sessions)
        errs = validate_prediction_error_invariants(report)
        if args.json:
            print(json.dumps({"ok": not errs, "band": report.get("band"), "errors": errs}, ensure_ascii=False, indent=2))
            return 1 if errs else 0
        if errs:
            for e in errs:
                print(f"FAIL: {e}", file=sys.stderr)
            return 1
        print(
            f"OK: prediction-error invariants hold "
            f"(band={report['band']}, latest_eval={report['retrospective']['latest_eval_session']['session_id']})"
        )
        return 0

    if args.json:
        report = compute_prediction_error(root=args.root, window_sessions=args.window_sessions)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    return run_probe(as_json=False, root=args.root)


if __name__ == "__main__":
    raise SystemExit(main())
