#!/usr/bin/env python3
"""Read-only audit of lineage mass transfer in `tools/belief_state.py` (stdlib only).

Why this tool exists
--------------------
`belief_state.compute_belief_state` routes the child-side share of a
``narrows_scope`` / ``refutes_unconditioned`` verdict like this (L249-254)::

    spawned = [s for s in (evl.get("spawned_hypothesis_ids") or []) if ...]
    if not spawned:
        spawned = children_by_parent.get(target_id, [])

``children_by_parent`` is built from the hypotheses that exist **now**. An
evaluation that named no children therefore credits whichever children the
parent has at read time, including children registered after that evaluation
was recorded. The credit is not a measurement of the child; it is the parent's
verdict, re-addressed.

On 2026-11-14 this produced a visible artifact: `HYP-20261113-977052` held
P_t = 1.0000 on Q-002 with **zero** direct evaluations, Q-002's posterior
entropy was 0.0001 bits, and every pair's expected information gain rounded to
0.0000 — while the renderer still printed a 「最優先検証ターゲット」.

What this tool reports
----------------------
1. How many narrowing/refuting verdicts name their children explicitly, how
   many fall back to the live parent-child index, and how many credit nobody.
2. Which fallback credits are **post-dated**: the child's `created_at` is later
   than the evaluation's. Two orderings are reported because the ledger mixes
   granularity (145 of 218 evaluations carry a date without a time):
     * ``day``    - compare the YYYY-MM-DD prefix only. A lower bound.
     * ``strict`` - read a date-only stamp as T00:00:00Z. An upper bound: a
                    date-only evaluation and a same-day child are ordered by
                    assumption, not by a recorded instant.
   The true count lies between the two. Neither is a measurement of intent.
3. The log-odds each child inherited through the fallback, and what the
   posterior would be if post-dated credits were denied.
4. ``--probe-newborn``: what one *unevaluated* child does to a question's
   Gen-1+ mass, D_KL and top-pair EIG. This is the reason the audit exists:
   registering a child is scored like learning, before anything tests it.

It is a mirror, not a gate. Exit status is 0 even when post-dated credits are
found. Nothing here writes to the ledger; the counterfactuals run on deep
copies. The enforcing checks remain `validate_seed.py`, `belief_state.py
--check-map` and `learning_metrics.py --check`.

Usage
-----
  python3 tools/lineage_credit_accounting.py
  python3 tools/lineage_credit_accounting.py --question Q-002
  python3 tools/lineage_credit_accounting.py --probe-newborn
  python3 tools/lineage_credit_accounting.py --json

See `readings/2026-11-14-the-verdict-arrived-before-the-hypothesis.md`.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402

TRANSFERRING_VERDICTS = ("narrows_scope", "refutes_unconditioned")
CHILD_SHARE = {"narrows_scope": 0.75, "refutes_unconditioned": 0.95}


def normalize_stamp(value: Any) -> str:
    """Read a date-only stamp as the start of that day, for strict ordering."""
    text = str(value or "")
    if not text:
        return ""
    return text if "T" in text else f"{text}T00:00:00Z"


def child_index(hypotheses: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Rebuild `children_by_parent` exactly as the engine does (sorted by ID)."""
    index: dict[str, list[str]] = defaultdict(list)
    for hid, hyp in sorted(hypotheses.items()):
        for pid in hyp.get("parent_hypothesis_ids") or []:
            if isinstance(pid, str) and pid in hypotheses:
                index[pid].append(hid)
    return dict(index)


def _repeat_key(evl: dict[str, Any]) -> str:
    """The engine's repeat key: (target, verdict, session-or-source)."""
    target = evl.get("target_hypothesis_id")
    verdict = str(evl.get("verdict") or "supports")
    sid = str(evl.get("session_id") or "")
    mat_sig = ",".join(sorted(evl.get("material_ids") or []))
    source_key = (mat_sig or ",".join(sorted(evl.get("note_ids") or []))
                  or evl.get("evaluation_id", ""))
    return f"{target}\x00{verdict}\x00{sid or source_key}"


def credit_delta(evl: dict[str, Any], hypotheses: dict[str, dict[str, Any]],
                 occurrence: int) -> float:
    """The engine's per-evaluation delta, before the verdict-specific factor.

    Mirrors belief_state L226-241. `occurrence` is this evaluation's 1-based
    count under its repeat key, in the engine's sorted iteration order.
    """
    target = evl.get("target_hypothesis_id")
    ev_type = str(evl.get("evidence_type") or "cross_session_audit")
    base_w = belief_state.EVIDENCE_WEIGHTS.get(ev_type, 1.0)
    discount = 1.0 / math.sqrt(max(1, occurrence))
    compared = [
        cid for cid in (evl.get("compared_against_hypothesis_ids") or [])
        if isinstance(cid, str) and cid in hypotheses and cid != target
    ]
    return base_w * discount * (1.0 if compared else 0.65)


def build_repeat_index(evaluations: dict[str, dict[str, Any]],
                       hypotheses: dict[str, dict[str, Any]]) -> dict[str, int]:
    """Map each evaluation ID to its occurrence count under the repeat key."""
    seen: Counter[str] = Counter()
    out: dict[str, int] = {}
    for evl_id, evl in sorted(evaluations.items()):
        target = evl.get("target_hypothesis_id")
        if not isinstance(target, str) or target not in hypotheses:
            continue
        key = _repeat_key(evl)
        seen[key] += 1
        out[evl_id] = seen[key]
    return out


def audit(cols: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    """Classify every child-side mass transfer. Writes nothing."""
    hypotheses = cols.get("hypotheses", {})
    evaluations = cols.get("evaluations", {})
    children = child_index(hypotheses)
    repeats = build_repeat_index(evaluations, hypotheses)

    routes: Counter[str] = Counter()
    transfers: list[dict[str, Any]] = []
    inherited: dict[str, float] = defaultdict(float)
    postdated_strict: dict[str, float] = defaultdict(float)
    compared_penalty: dict[str, float] = defaultdict(float)

    for evl_id, evl in sorted(evaluations.items()):
        target = evl.get("target_hypothesis_id")
        if not isinstance(target, str) or target not in hypotheses:
            continue
        verdict = str(evl.get("verdict") or "supports")
        # A hypothesis can also lose log-odds without being evaluated directly:
        # every `supports` verdict subtracts 0.20*delta from each compared
        # rival (belief_state L258-262). That term is needed to reconcile the
        # audited shares with the engine's log_odds.
        if verdict == "supports":
            rivals = [
                cid for cid in (evl.get("compared_against_hypothesis_ids") or [])
                if isinstance(cid, str) and cid in hypotheses and cid != target
            ]
            if rivals:
                penalty = (0.20 * credit_delta(evl, hypotheses, repeats[evl_id])) / len(rivals)
                for cid in rivals:
                    compared_penalty[cid] -= penalty
            continue
        if verdict not in TRANSFERRING_VERDICTS:
            continue
        explicit = [
            s for s in (evl.get("spawned_hypothesis_ids") or [])
            if isinstance(s, str) and s in hypotheses and s != target
        ]
        routed = explicit or children.get(target, [])
        route = "explicit" if explicit else ("fallback" if routed else "no_child")
        routes[route] += 1
        if not routed:
            continue
        share = (CHILD_SHARE[verdict] * credit_delta(evl, hypotheses, repeats[evl_id])) / len(routed)
        e_day = str(evl.get("created_at") or "")[:10]
        e_strict = normalize_stamp(evl.get("created_at"))
        for cid in routed:
            c_day = str(hypotheses[cid].get("created_at") or "")[:10]
            c_strict = normalize_stamp(hypotheses[cid].get("created_at"))
            later_day = bool(e_day and c_day and c_day > e_day)
            later_strict = bool(e_strict and c_strict and c_strict > e_strict)
            inherited[cid] += share
            if later_strict:
                postdated_strict[cid] += share
            transfers.append({
                "evaluation_id": evl_id,
                "target_hypothesis_id": target,
                "child_hypothesis_id": cid,
                "verdict": verdict,
                "route": route,
                "evaluation_created_at": evl.get("created_at"),
                "child_created_at": hypotheses[cid].get("created_at"),
                "log_odds_share": round(share, 6),
                "postdated_day": later_day,
                "postdated_strict": later_strict,
            })

    return {
        "routes": dict(routes),
        "transfers": transfers,
        "inherited_log_odds": {k: round(v, 4) for k, v in sorted(inherited.items())},
        "compared_penalty_log_odds": {k: round(v, 4) for k, v in sorted(compared_penalty.items())},
        "postdated_strict_log_odds": {k: round(v, 4) for k, v in sorted(postdated_strict.items())},
        # Only fallback routing is the artifact. An explicit list is the
        # recording session's own claim about where the mass goes; it is
        # reported in `transfers` but never counted as retroactive credit.
        "postdated_day_pairs": [
            t for t in transfers if t["postdated_day"] and t["route"] == "fallback"
        ],
        "postdated_strict_pairs": [
            t for t in transfers if t["postdated_strict"] and t["route"] == "fallback"
        ],
    }


def question_summary(state: dict[str, Any], qid: str) -> dict[str, Any]:
    q = state["questions"][qid]
    top = q["hypotheses"][0] if q["hypotheses"] else None
    pair = q.get("top_competing_pair") or {}
    return {
        "question_id": qid,
        "gen1_plus_mass": q["gen1_plus_mass"],
        "kl_from_uniform_bits": q["kl_from_uniform_bits"],
        "active_entropy_bits": q["active_entropy_bits"],
        "top_hypothesis_id": top["hypothesis_id"] if top else None,
        "top_posterior": top["posterior"] if top else None,
        "top_direct_eval_count": top["direct_eval_count"] if top else None,
        "top_pair_eig": pair.get("expected_info_gain"),
    }


def counterfactual(cols: dict[str, dict[str, dict[str, Any]]],
                   report: dict[str, Any]) -> dict[str, Any]:
    """Deny post-dated fallback credits; recompute posteriors from log-odds.

    The engine's log_odds already include errata penalties and status baselines,
    so the credits are subtracted from its output rather than re-derived.
    """
    before = belief_state.compute_belief_state(cols)
    deny: dict[str, float] = defaultdict(float)
    for t in report["postdated_strict_pairs"]:
        deny[t["child_hypothesis_id"]] += t["log_odds_share"]
    hypotheses = cols.get("hypotheses", {})
    out: dict[str, Any] = {}
    for qid, q in before["questions"].items():
        hids = [h["hypothesis_id"] for h in q["hypotheses"]]
        if not hids:
            continue
        adj = {h["hypothesis_id"]: h["log_odds"] - deny.get(h["hypothesis_id"], 0.0)
               for h in q["hypotheses"]}
        max_l = max(adj.values())
        exps = {h: math.exp(adj[h] - max_l) for h in hids}
        total = sum(exps.values()) or 1.0
        post = {h: exps[h] / total for h in hids}
        n = len(hids)
        kl = sum(p * math.log2(max(p, 1e-12) / (1.0 / n)) for p in post.values())
        depths = belief_state._generation_depths(hypotheses)
        gen1 = sum(p for h, p in post.items() if depths.get(h, 0) >= 1)
        out[qid] = {
            "before": question_summary(before, qid),
            "after": {
                "kl_from_uniform_bits": round(kl, 4),
                "gen1_plus_mass": round(gen1, 4),
                "top_hypothesis_id": max(post, key=lambda h: post[h]),
                "top_posterior": round(max(post.values()), 4),
            },
            "denied_log_odds": {h: round(v, 4) for h, v in deny.items() if h in hids},
        }
    return out


def probe_newborn(cols: dict[str, dict[str, dict[str, Any]]],
                  questions: tuple[str, ...]) -> dict[str, Any]:
    """Attach one unevaluated child to each question's leader. Deep copies only."""
    out: dict[str, Any] = {}
    for qid in questions:
        base_state = belief_state.compute_belief_state(cols)
        if qid not in base_state["questions"] or not base_state["questions"][qid]["hypotheses"]:
            continue
        leader = base_state["questions"][qid]["hypotheses"][0]["hypothesis_id"]
        mutated = copy.deepcopy(cols)
        hid = "HYP-PROBE-UNREGISTERED"
        mutated["hypotheses"][hid] = {
            "hypothesis_id": hid,
            "session_id": "SESSION-PROBE-NOT-RECORDED",
            "created_at": "2026-11-14T00:00:00Z",
            "question_ids": [qid],
            "title": "probe: an unevaluated child, never written to any ledger",
            "proposition": "probe only",
            "scope_conditions": ["probe only"],
            "exclusion_clause": "probe only",
            "lineage_op": "refines",
            "parent_hypothesis_ids": [leader],
            "status": "active",
        }
        after = belief_state.compute_belief_state(mutated)
        child_row = next(h for h in after["questions"][qid]["hypotheses"]
                         if h["hypothesis_id"] == hid)
        out[qid] = {
            "parent_hypothesis_id": leader,
            "before": question_summary(base_state, qid),
            "after": question_summary(after, qid),
            "probe_child": {
                "posterior": child_row["posterior"],
                "log_odds": child_row["log_odds"],
                "direct_eval_count": child_row["direct_eval_count"],
                "uncertainty": child_row["uncertainty"],
            },
        }
    return out


def render(report: dict[str, Any], state: dict[str, Any],
           cf: dict[str, Any] | None, probe: dict[str, Any] | None,
           only_question: str | None) -> str:
    lines = ["=== lineage credit audit（合否ではなく、質量の出所の観察） ===", ""]
    r = report["routes"]
    total = sum(r.values())
    lines.append(
        f"  射程限定・反証の評価 {total} 件: 明示 {r.get('explicit', 0)} ／ "
        f"フォールバック {r.get('fallback', 0)} ／ 子なし {r.get('no_child', 0)}"
    )
    lines.append(
        f"  子への移転 {len(report['transfers'])} 件: "
        f"日付順序で後付け {len(report['postdated_day_pairs'])} 件（下限） ／ "
        f"厳密順序で後付け {len(report['postdated_strict_pairs'])} 件（上限）"
    )
    lines.append("  ※ 日付のみの行は時刻を持たない。二つの数のあいだに真値があり、どちらかで断定しない。")
    lines.append("")
    if report["postdated_strict_pairs"]:
        lines.append("  後付け移転（厳密順序）:")
        for t in report["postdated_strict_pairs"]:
            lines.append(
                f"    {t['evaluation_id']} ({t['evaluation_created_at']}) "
                f"→ {t['child_hypothesis_id']} ({t['child_created_at']}) "
                f"+{t['log_odds_share']:.4f} [{t['route']}]"
            )
        lines.append("")
    zero = [
        (qid, h) for qid, q in state["questions"].items()
        for h in q["hypotheses"]
        if h["direct_eval_count"] == 0 and h["posterior"] > 0.0
    ]
    if zero:
        lines.append("  直接評価0件で事後確率を持つ仮説:")
        for qid, h in zero:
            inherited = report["inherited_log_odds"].get(h["hypothesis_id"], 0.0)
            lines.append(
                f"    {qid} {h['hypothesis_id']} P={h['posterior']:.4f} "
                f"u={h['uncertainty']:.3f} logodds={h['log_odds']:+.4f} "
                f"継承分={inherited:+.4f}"
            )
        lines.append("")
    saturated = [
        qid for qid, q in state["questions"].items()
        if q["hypotheses"] and (q.get("top_competing_pair") or {}).get("expected_info_gain") == 0.0
    ]
    if saturated:
        lines.append(
            "  全ペア EIG=0.0000 でも「最優先検証ターゲット」を印字する問い: "
            + ", ".join(saturated)
        )
        lines.append("")
    if cf:
        lines.append("  後付け移転を拒んだ場合（台帳は書き換えない）:")
        for qid, row in cf.items():
            if only_question and qid != only_question:
                continue
            b, a = row["before"], row["after"]
            lines.append(
                f"    {qid}: D_KL {b['kl_from_uniform_bits']:.4f} → {a['kl_from_uniform_bits']:.4f} ／ "
                f"第1世代+ {b['gen1_plus_mass']:.4f} → {a['gen1_plus_mass']:.4f} ／ "
                f"首位 {b['top_hypothesis_id']} ({b['top_posterior']:.4f}) → "
                f"{a['top_hypothesis_id']} ({a['top_posterior']:.4f})"
            )
        lines.append("")
    if probe:
        lines.append("  未評価の子を1件足したら（合成行・台帳に書かない）:")
        for qid, row in probe.items():
            b, a = row["before"], row["after"]
            lines.append(
                f"    {qid}: 第1世代+ {b['gen1_plus_mass']:.4f} → {a['gen1_plus_mass']:.4f} ／ "
                f"D_KL {b['kl_from_uniform_bits']:.4f} → {a['kl_from_uniform_bits']:.4f} ／ "
                f"EIG {b['top_pair_eig']} → {a['top_pair_eig']}"
            )
        lines.append("")
    lines.append("  この出力はゲートではない。終了コードは常に0。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--question", help="restrict the counterfactual listing to one question")
    parser.add_argument("--counterfactual", action="store_true",
                        help="also recompute posteriors with post-dated credits denied")
    parser.add_argument("--probe-newborn", action="store_true",
                        help="also measure what one unevaluated child does to each core question")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    cols = belief_state.load_belief_ledgers(args.root)
    report = audit(cols)
    state = belief_state.compute_belief_state(cols)
    cf = counterfactual(cols, report) if args.counterfactual else None
    probe = (probe_newborn(cols, belief_state.CORE_QUESTIONS)
             if args.probe_newborn else None)

    if args.json:
        print(json.dumps({
            "audit": report,
            "questions": {q: question_summary(state, q) for q in state["questions"]},
            "counterfactual": cf,
            "newborn_probe": probe,
        }, ensure_ascii=False, indent=2))
    else:
        print(render(report, state, cf, probe, args.question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
