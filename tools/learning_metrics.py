#!/usr/bin/env python3
"""Quantitative learning-effect metrics and wiring gate for AIselfMySelf (stdlib only).

Measures whether accumulated repository memory produces genuine epistemic learning
(updating conditional hypothesis distributions P_t(H|Q)) rather than mere append-only
growth, and enforces structural wiring invariants in CI (--check).

Five core metrics:
  1. Belief-State Divergence: D_KL(P_t || P_0) and Gen-0 -> Gen-1+ probability mass shift
  2. Memory-Conditioned Divergence: claim/revision distribution shift between k=0
     (no prior notes/hypotheses read) and k>=1 (memory-reading) sessions
  3. Adversarial Falsification Ratio: share of non-confirming verdicts
     (narrows_scope, refutes_unconditioned, subsumes) and comparative evaluations
  4. Dead-Hypothesis Revival Rate: unconditioned support for already-refuted hypotheses
  5. Wiring & Chronology Coverage: 100% readings/*.md -> notes coverage, 0 future shards,
     and current BELIEF_MAP.md

Usage:
  python3 tools/learning_metrics.py
  python3 tools/learning_metrics.py --json
  python3 tools/learning_metrics.py --check
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import belief_state
import date_axis
import ledger_io
import note_index

ROOT = Path(__file__).resolve().parents[1]
NON_CONFIRMING_VERDICTS = frozenset({"narrows_scope", "refutes_unconditioned", "subsumes"})
CLAIM_KINDS = (
    "reading_revised",
    "reading_maintained",
    "reading_held",
    "measured_fact",
    "method_change",
    "handoff",
    "retraction",
)


def _js_divergence_bits(p_counts: Counter[str], q_counts: Counter[str], keys: tuple[str, ...]) -> float:
    tp = sum(p_counts[k] for k in keys)
    tq = sum(q_counts[k] for k in keys)
    if tp == 0 or tq == 0:
        return 0.0
    p = {k: p_counts[k] / tp for k in keys}
    q = {k: q_counts[k] / tq for k in keys}
    m = {k: 0.5 * (p[k] + q[k]) for k in keys}
    kl_pm = sum(p[k] * math.log2(p[k] / m[k]) for k in keys if p[k] > 0 and m[k] > 0)
    kl_qm = sum(q[k] * math.log2(q[k] / m[k]) for k in keys if q[k] > 0 and m[k] > 0)
    return round(0.5 * (kl_pm + kl_qm), 4)


def compute_learning_metrics(
    *,
    root: Path = ROOT,
    today: date | None = None,
) -> dict[str, Any]:
    """Compute all five learning-effect and wiring metrics."""
    root = Path(root)
    today = today or date.today()

    specs = {
        "questions": (root / "state" / "questions.jsonl", "question_id"),
        "materials": (root / "state" / "materials.jsonl", "material_id"),
        "fragments": (root / "state" / "fragments.jsonl", "fragment_id"),
        "sessions": (root / "state" / "sessions.jsonl", "session_id"),
        "read_log": (root / "state" / "read_log.jsonl", "read_id"),
        "notes": (root / "state" / "notes.jsonl", "note_id"),
    }
    for opt_name, id_key in (
        ("hypotheses", "hypothesis_id"),
        ("evaluations", "evaluation_id"),
        ("errata", "errata_id"),
    ):
        base = root / "state" / f"{opt_name}.jsonl"
        if base.exists() or ledger_io.shard_dir(base).is_dir():
            specs[opt_name] = (base, id_key)

    data, errors = ledger_io.load_collections(specs, root=root)
    if errors:
        raise ValueError("ledger load errors:\n  - " + "\n  - ".join(errors[:10]))
    for opt_name in ("hypotheses", "evaluations", "errata"):
        data.setdefault(opt_name, {})

    bstate = belief_state.compute_belief_state(data=data, root=root)

    # 1. Belief-State Divergence across Q-001..Q-003
    core_summaries = {}
    kl_values = []
    gen1_shares = []
    for qid in belief_state.CORE_QUESTIONS:
        qs = bstate["questions"].get(qid, {})
        kl = float(qs.get("kl_from_uniform_bits", 0.0))
        g1 = float(qs.get("gen1_plus_mass", 0.0))
        kl_values.append(kl)
        gen1_shares.append(g1)
        core_summaries[qid] = {
            "hypothesis_count": qs.get("hypothesis_count", 0),
            "active_count": qs.get("active_count", 0),
            "kl_from_uniform_bits": kl,
            "gen1_plus_mass": g1,
            "entropy_bits": qs.get("entropy_bits", 0.0),
            "mean_active_uncertainty": qs.get("mean_active_uncertainty", 1.0),
        }

    # 2. Memory-conditioned k=0 vs k>=1 session comparison
    prior_memory_reads: Counter[str] = Counter()
    active_reinterp_reads: Counter[str] = Counter()
    for r in data["read_log"].values():
        sid = str(r.get("session_id") or "")
        target = r.get("target") or {}
        ttype = target.get("type")
        reading = r.get("reading")
        if ttype in ("note", "hypothesis", "evaluation", "session"):
            prior_memory_reads[sid] += 1
        if reading in ("reinterpreted", "contested"):
            active_reinterp_reads[sid] += 1

    k0_claims: Counter[str] = Counter()
    k1_claims: Counter[str] = Counter()
    k0_sessions: set[str] = set()
    k1_sessions: set[str] = set()

    for nrec in data["notes"].values():
        if nrec.get("index_backfill") is True:
            continue
        sid = str(nrec.get("report_session_id") or nrec.get("session_id") or "")
        has_mem = prior_memory_reads[sid] >= 1
        if has_mem:
            k1_sessions.add(sid)
        else:
            k0_sessions.add(sid)
        for cl in nrec.get("claims") or []:
            kind = str(cl.get("kind") or "")
            if kind in CLAIM_KINDS:
                if has_mem:
                    k1_claims[kind] += 1
                else:
                    k0_claims[kind] += 1

    js_div = _js_divergence_bits(k1_claims, k0_claims, CLAIM_KINDS)
    k0_rev_rate = (
        (k0_claims["reading_revised"] + k0_claims["retraction"]) / max(1, sum(k0_claims.values()))
    )
    k1_rev_rate = (
        (k1_claims["reading_revised"] + k1_claims["retraction"]) / max(1, sum(k1_claims.values()))
    )

    # 3. Adversarial / Non-Confirming Evaluation Ratio & Comparative Ratio
    evals = list(data["evaluations"].values())
    total_evals = len(evals)
    non_confirming = sum(1 for e in evals if e.get("verdict") in NON_CONFIRMING_VERDICTS)
    comparative = sum(1 for e in evals if len(e.get("compared_against_hypothesis_ids") or []) >= 1)
    verdict_breakdown = Counter(str(e.get("verdict") or "") for e in evals)

    # 4. Dead-Hypothesis Revival Detector
    refuted_seen: set[str] = set()
    revival_events: list[dict[str, str]] = []
    for hid, hyp in data["hypotheses"].items():
        if hyp.get("status") == "refuted" and not (hyp.get("parent_hypothesis_ids") or []):
            # Initial Gen-0 refuted roots are treated as refuted once a refuting evaluation lands
            pass
    for eid, evl in sorted(data["evaluations"].items()):
        thid = str(evl.get("target_hypothesis_id") or "")
        verdict = str(evl.get("verdict") or "")
        if verdict == "refutes_unconditioned":
            refuted_seen.add(thid)
        elif verdict == "supports" and thid in refuted_seen:
            revival_events.append({
                "evaluation_id": eid,
                "hypothesis_id": thid,
                "session_id": str(evl.get("session_id") or ""),
            })

    # 5. Repository Wiring & Chronology Coverage
    nview = note_index.build_view(root=root)
    total_reports = len(nview)
    unregistered_paths = sorted(e["path"] for e in nview.values() if not e.get("note_id"))
    curated_reports = sum(
        1 for n in data["notes"].values() if not n.get("index_backfill")
    )
    fwd_shards = date_axis.forward_dated_shards(root, today=today)
    map_ok, map_msg = belief_state.check_belief_map(root)

    return {
        "belief_divergence": {
            "mean_kl_bits": round(sum(kl_values) / max(1, len(kl_values)), 4),
            "mean_gen1_plus_mass": round(sum(gen1_shares) / max(1, len(gen1_shares)), 4),
            "core_questions": core_summaries,
        },
        "memory_conditioning": {
            "k0_curated_sessions": len(k0_sessions),
            "k1_plus_curated_sessions": len(k1_sessions),
            "claim_distribution_js_bits": js_div,
            "k0_revision_or_retraction_share": round(k0_rev_rate, 4),
            "k1_plus_revision_or_retraction_share": round(k1_rev_rate, 4),
            "sessions_with_reinterpreted_or_contested": len(active_reinterp_reads),
        },
        "evaluation_discipline": {
            "total_evaluations": total_evals,
            "non_confirming_count": non_confirming,
            "non_confirming_ratio": round(non_confirming / max(1, total_evals), 4),
            "comparative_count": comparative,
            "comparative_ratio": round(comparative / max(1, total_evals), 4),
            "verdict_counts": dict(verdict_breakdown),
        },
        "dead_hypothesis_revivals": {
            "count": len(revival_events),
            "events": revival_events,
        },
        "wiring_and_chronology": {
            "total_reports": total_reports,
            "registered_reports": total_reports - len(unregistered_paths),
            "report_note_coverage": round(
                (total_reports - len(unregistered_paths)) / max(1, total_reports), 4
            ),
            "curated_note_rows": curated_reports,
            "unregistered_report_paths": unregistered_paths,
            "forward_dated_shards": fwd_shards,
            "belief_map_current": map_ok,
            "belief_map_message": map_msg,
        },
    }


def check_invariants(metrics: dict[str, Any]) -> list[str]:
    """Return CI failure messages if structural learning/wiring gates are violated."""
    failures: list[str] = []
    wc = metrics["wiring_and_chronology"]
    if wc["unregistered_report_paths"]:
        sample = ", ".join(wc["unregistered_report_paths"][:5])
        failures.append(
            f"readings/ wiring incomplete: {len(wc['unregistered_report_paths'])} report(s) lack a NOTE-* row "
            f"(e.g. {sample}); register via tools/note_index.py --register"
        )
    if wc["forward_dated_shards"]:
        sample = ", ".join(wc["forward_dated_shards"][:5])
        failures.append(
            f"forward-dated shard(s) detected: {len(wc['forward_dated_shards'])} (e.g. {sample})"
        )
    if not wc["belief_map_current"]:
        failures.append(wc["belief_map_message"])

    for qid, qinfo in metrics["belief_divergence"]["core_questions"].items():
        if qinfo["active_count"] < 2:
            failures.append(
                f"{qid}: fewer than 2 active competing conditional hypotheses ({qinfo['active_count']})"
            )

    ed = metrics["evaluation_discipline"]
    if ed["total_evaluations"] == 0:
        failures.append("state/evaluations* has 0 evaluation events")
    elif ed["non_confirming_ratio"] < 0.20:
        failures.append(
            f"non_confirming_ratio {ed['non_confirming_ratio']:.3f} < 0.20 floor "
            "(confirmation-only drift; record narrows_scope / refutes_unconditioned / subsumes tests)"
        )

    rev = metrics["dead_hypothesis_revivals"]
    if rev["count"] > 0:
        failures.append(
            f"dead-hypothesis revival detected ({rev['count']} unconditioned support event(s) on refuted hypotheses)"
        )
    return failures


def render_report(metrics: dict[str, Any]) -> str:
    bd = metrics["belief_divergence"]
    mc = metrics["memory_conditioning"]
    ed = metrics["evaluation_discipline"]
    rv = metrics["dead_hypothesis_revivals"]
    wc = metrics["wiring_and_chronology"]
    lines = [
        "# Learning & Memory Wiring Metrics",
        "",
        f"1. 仮説分布の更新量 (Q-001..Q-003 平均): D_KL(P_t || P_0) = {bd['mean_kl_bits']:.4f} bits / 第1世代+質量 = {bd['mean_gen1_plus_mass']*100:.1f}%",
        f"2. 記憶条件付け乖離 (k>=1 vs k=0): JS距離 = {mc['claim_distribution_js_bits']:.4f} bits "
        f"(改訂・撤回率 k=0: {mc['k0_revision_or_retraction_share']*100:.1f}% vs k>=1: {mc['k1_plus_revision_or_retraction_share']*100:.1f}%)",
        f"3. 反証・射程限定規律: 非確証評価率 = {ed['non_confirming_ratio']*100:.1f}% ({ed['non_confirming_count']}/{ed['total_evaluations']}) / "
        f"対立比較率 = {ed['comparative_ratio']*100:.1f}% ({ed['comparative_count']}/{ed['total_evaluations']})",
        f"4. 棄却済み仮説の無条件復活件数: {rv['count']} 件",
        f"5. 台帳配線・時系列健全性: readings/配線率 = {wc['report_note_coverage']*100:.1f}% "
        f"({wc['registered_reports']}/{wc['total_reports']}) / 前倒しシャード = {len(wc['forward_dated_shards'])} 本 / "
        f"BELIEF_MAP同期 = {'OK' if wc['belief_map_current'] else 'NG'}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="output JSON metrics")
    parser.add_argument("--check", action="store_true", help="fail (exit 1) if wiring or learning invariants fail")
    args = parser.parse_args(argv)

    today = date_axis.as_date(args.today) if args.today else date.today()
    metrics = compute_learning_metrics(root=args.root, today=today)

    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        if args.check:
            failures = check_invariants(metrics)
            return 1 if failures else 0
        return 0

    print(render_report(metrics))
    if args.check:
        failures = check_invariants(metrics)
        if failures:
            print("\nFAIL: learning / wiring invariants violated:", file=sys.stderr)
            for msg in failures:
                print(f"  - {msg}", file=sys.stderr)
            return 1
        print("\nPASS: all learning, falsification, chronology, and wiring gates satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
