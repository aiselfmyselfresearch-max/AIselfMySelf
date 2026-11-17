#!/usr/bin/env python3
"""Which verdict came last? The engine cannot say, and the ledger often cannot either.

Read-only. Nothing is written; every counterfactual runs on a deep copy.

Why this tool exists
--------------------
A directed pair (target -> partner) can carry both ``supports`` and
``narrows_scope`` rows. The two do different things — a support raises the target
and charges the partner, a narrowing lowers the target and charges the partner
nothing (see ``tools/field_double_reading_probe.py``) — and both are applied, in
the order the engine happens to iterate.

That order is ``sorted(evaluations.items())``, i.e. **by evaluation id**, which
begins with the creation date and then a hex suffix. So:

  * across days, id order and time order agree;
  * within one day, the hex suffix decides, and it is random.

The engine never reads ``created_at`` for weighting at all: it reads it only to
date the separation-audit columns (:711). This tool reports how much weight that
choice carries, and how much of the ledger is even *eligible* for a time order:

  rows whose ``created_at`` carries a time (``YYYY-MM-DDTHH:MM:SS``) can be
  ordered; rows with a date only cannot. A date-only row that ties with another
  row on the same day is **not ordered by the ledger**, whatever a reader assumes.

What it reports
---------------
1. how many directed pairs carry both verdicts, and how many of those have a
   strict time order across all their rows.
2. the share of verdict-bearing rows whose ``created_at`` is date-only.
3. **the counterfactual**: if every strictly-ordered pair were decided by time
   alone — the later verdict stands, an earlier row of the other verdict on the
   same pair is suppressed — how far does the belief map move?

The third section replaces a first draft that re-keyed the evaluation dict in
reverse-id order. That draft was vacuous: the engine loops over
``sorted(evaluations.items())``, so re-keying changes nothing, and the measured
difference was 0.00e+00 across every question. A probe that reports zero because
it cannot move anything is worse than no probe; it looks like evidence that order
does not matter. The honest statement is the other way round — the engine's sum
is **order-independent** (I verified: 0 differences under re-keying), which is
exactly why "read ``created_at`` order" cannot be implemented as a sort. It has
to be implemented as a decision that *drops* rows, and that is what section 3
measures.

What it does NOT do
-------------------
It does not add a time term, and it does not sort by ``created_at``. Both would
change every historical number, and ``readings/2026-11-18-the-three-debts-and-
the-one-that-bends.md`` §4 argues that the ordering question cannot be answered
from the ledger as it stands: a quarter of the rows cannot be placed in time at
all. Sorting by ``created_at`` would *look* like a fix while silently demoting
those rows to ties decided by dict order — the same arbitrariness with an extra
step. The knob is a session-level decision, not a probe-level one.

Known blindness
  - Reverse-id order is one alternative, not the space of alternatives. Agreement
    between two orders is evidence that the sum is commutative here, not proof.
  - "Strict time order" reads a date-only stamp as T00:00:00Z, which is an
    assumption, not a measurement. It is reported as an upper bound on how many
    pairs are orderable; the lower bound is the count that survives when date-only
    rows are treated as unplaceable.
  - Ties are counted only within a pair. Two rows on the same pair with the same
    day are a tie even if one is date-only and the other has a time.

Usage::

    python3 tools/verdict_order_probe.py
    python3 tools/verdict_order_probe.py --json
    python3 tools/verdict_order_probe.py --question Q-003

Exit status is always 0: this is a measuring instrument, not a gate.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402

CONFLICT = {"supports", "narrows_scope"}


def _has_time(stamp: str) -> bool:
    return len(stamp or "") >= 19


def orderable_pairs(cols: dict[str, Any]) -> dict[str, Any]:
    """Directed pairs carrying both verdicts, and whether time can order them."""
    hyps = cols["hypotheses"]
    evals = cols["evaluations"]
    directed: dict[tuple[str, str], list[dict[str, str]]] = collections.defaultdict(list)
    for eid, evl in sorted(evals.items()):
        target = evl.get("target_hypothesis_id")
        if target not in hyps:
            continue
        verdict = str(evl.get("verdict") or "supports")
        for pid in (evl.get("compared_against_hypothesis_ids") or []):
            if isinstance(pid, str) and pid in hyps and pid != target:
                directed[(target, pid)].append({
                    "evaluation_id": eid,
                    "verdict": verdict,
                    "created_at": str(evl.get("created_at") or ""),
                })

    conflicting = {k: v for k, v in directed.items()
                   if {r["verdict"] for r in v} >= CONFLICT}
    strict = 0
    tie = 0
    unplaceable = 0
    for rows in conflicting.values():
        stamps = [r["created_at"] for r in rows]
        if not all(_has_time(s) for s in stamps):
            unplaceable += 1
        elif len(set(stamps)) < len(stamps):
            tie += 1
        else:
            strict += 1

    return {
        "directed_pairs": len(directed),
        "conflicting_pairs": len(conflicting),
        "strictly_ordered_by_time": strict,
        "tied_on_the_same_stamp": tie,
        "not_placeable_in_time": unplaceable,
        "examples": [
            {
                "target": k[0], "partner": k[1],
                "rows": sorted(v, key=lambda r: r["created_at"]),
            }
            for k, v in sorted(conflicting.items())[:5]
        ],
    }


def stamp_granularity(cols: dict[str, Any]) -> dict[str, Any]:
    verdict_rows = [e for e in cols["evaluations"].values()
                    if e.get("target_hypothesis_id") in cols["hypotheses"]]
    date_only = sum(1 for e in verdict_rows if not _has_time(str(e.get("created_at") or "")))
    return {
        "evaluation_rows": len(verdict_rows),
        "date_only": date_only,
        "with_a_time": len(verdict_rows) - date_only,
        "share_date_only": round(date_only / len(verdict_rows), 4) if verdict_rows else 0.0,
    }


def _posteriors(state: dict[str, Any]) -> dict[tuple[str, str], float]:
    """Posterior keyed by (question, hypothesis).

    Keyed by hypothesis alone the map collapses: 52 hypotheses fill 67 slots
    across five questions, so a shared hypothesis would silently report the last
    question it appeared in. A first draft did exactly that and reported three
    questions whose leader held 100.00%.
    """
    return {(qid, h["hypothesis_id"]): h["posterior"]
            for qid, q in state["questions"].items() for h in q["hypotheses"]}


def _suppress(cols: dict[str, Any], evaluation_ids: list[str]) -> dict[str, Any]:
    """Return a copy in which the given rows carry no weight.

    The engine has no "drop this row" input, and rewriting a historical row is
    forbidden. The copy is therefore *not a ledger*: each suppressed row is
    replaced by a row with an unknown verdict and no comparison partners. The
    engine skips unknown verdicts, so the row costs exactly nothing — which is
    what "the earlier reading loses to the later one" means arithmetically.

    This is why the tool cannot be a gate or a mode: it measures a hypothetical
    ledger that contradicts the append-only rule.
    """
    out = copy.deepcopy(cols)
    for eid in evaluation_ids:
        row = out["evaluations"].get(eid)
        if row is None:
            continue
        out["evaluations"][eid] = {
            "evaluation_id": eid,
            "session_id": row.get("session_id", ""),
            "created_at": row.get("created_at", ""),
            "target_hypothesis_id": row.get("target_hypothesis_id", ""),
            "verdict": "suppressed_by_time_order",
            "evidence_type": row.get("evidence_type", ""),
            "summary": "suppressed: the probe keeps only the later verdict of a pair",
            "compared_against_hypothesis_ids": [],
        }
    return out


def time_decided_counterfactual(cols: dict[str, Any]) -> dict[str, Any]:
    """Keep only the later verdict of each strictly time-ordered pair.

    Only pairs where *every* row carries a time can be decided this way; the
    rest stay as filed. The result is an upper-vs-middle bracket, not a forecast:
    it says what a date-decided archive would look like, on the subset where a
    date decision is even possible.
    """
    pairs = orderable_pairs(cols)
    evals = cols["evaluations"]
    hyps = cols["hypotheses"]
    directed: dict[tuple[str, str], list[tuple[str, dict[str, Any]]]] = collections.defaultdict(list)
    for eid, evl in sorted(evals.items()):
        target = evl.get("target_hypothesis_id")
        if target not in hyps:
            continue
        for pid in (evl.get("compared_against_hypothesis_ids") or []):
            if isinstance(pid, str) and pid in hyps and pid != target:
                directed[(target, pid)].append((eid, evl))

    strict_pairs = 0
    suppressed: list[str] = []
    for (target, pid), rows in directed.items():
        verdicts = {r[1].get("verdict") for r in rows}
        if not verdicts >= CONFLICT:   # >= not < : a set literal is a proper subset test
            continue
        stamps = [str(r[1].get("created_at") or "") for r in rows]
        if not all(_has_time(s) for s in stamps) or len(set(stamps)) != len(stamps):
            continue
        strict_pairs += 1
        ordered = sorted(rows, key=lambda r: str(r[1].get("created_at")))
        last_verdict = ordered[-1][1].get("verdict")
        for eid, row in ordered[:-1]:
            if row.get("verdict") != last_verdict and eid not in suppressed:
                suppressed.append(eid)

    base = bs.compute_belief_state(copy.deepcopy(cols))
    alt = bs.compute_belief_state(_suppress(cols, suppressed))
    pa, pb = _posteriors(base), _posteriors(alt)
    worst_key = max(pa, key=lambda k: abs(pa[k] - pb.get(k, 0.0))) if pa else None
    per_question = {}
    for qid in base["questions"]:
        keys = [(qid, h["hypothesis_id"]) for h in base["questions"][qid]["hypotheses"]
                if (qid, h["hypothesis_id"]) in pa]
        if not keys:
            # A synthetic ledger with no question row leaves the state empty.
            per_question[qid] = {"leader_as_filed": None, "leader_time_decided": None,
                                 "leader_changed": False, "leader_as_filed_pct": 0.0,
                                 "leader_time_decided_pct": 0.0, "max_abs_dP": 0.0}
            continue
        leader_a = max(keys, key=lambda k: pa[k])[1]
        leader_b = max(keys, key=lambda k: pb[k])[1]
        per_question[qid] = {
            "leader_as_filed": leader_a,
            "leader_time_decided": leader_b,
            "leader_changed": leader_a != leader_b,
            "leader_as_filed_pct": round(pa[(qid, leader_a)] * 100, 2),
            "leader_time_decided_pct": round(pb[(qid, leader_b)] * 100, 2),
            "max_abs_dP": round(max(abs(pa[k] - pb[k]) for k in keys), 6),
        }
    return {
        "pairs_decidable_by_time": strict_pairs,
        "rows_suppressed": len(suppressed),
        "max_abs_dP": round(abs(pa[worst_key] - pb[worst_key]), 6) if worst_key else 0.0,
        "hypothesis_with_largest_move": worst_key[1] if worst_key else None,
        "hypotheses_moved": sum(1 for k in pa if abs(pa[k] - pb.get(k, 0.0)) > 1e-12),
        "hypotheses_total": len(pa),
        "per_question": per_question,
        "suppressed_evaluation_ids": suppressed,
        "pairs_carried_both_verdicts": pairs["conflicting_pairs"],
    }


def run(root: Path | str = ROOT) -> dict[str, Any]:
    cols = bs.load_belief_ledgers(Path(root))
    return {
        "rows": stamp_granularity(cols),
        "orderable": orderable_pairs(cols),
        "time_decided": time_decided_counterfactual(cols),
        "engine_reads_created_at_for_weight": False,
    }


def render(result: dict[str, Any]) -> str:
    lines = ["=== verdict order probe ===", ""]
    r = result["rows"]
    lines.append("TIMESTAMP GRANULARITY (can the ledger be ordered at all?)")
    lines.append(f"  verdict-bearing rows            {r['evaluation_rows']}")
    lines.append(f"  with a time (YYYY-MM-DDTHH:..)  {r['with_a_time']}")
    lines.append(f"  date only                       {r['date_only']}  ({r['share_date_only']*100:.1f}%)")
    lines.append("")
    o = result["orderable"]
    lines.append("DIRECTED PAIRS CARRYING BOTH supports AND narrows_scope")
    lines.append(f"  directed pairs                  {o['directed_pairs']}")
    lines.append(f"  carrying both verdicts          {o['conflicting_pairs']}")
    lines.append(f"  strictly ordered by time        {o['strictly_ordered_by_time']}")
    lines.append(f"  tied on the same stamp          {o['tied_on_the_same_stamp']}")
    lines.append(f"  not placeable in time at all    {o['not_placeable_in_time']}")
    for ex in o["examples"]:
        lines.append(f"  · {ex['target'][-6:]} -> {ex['partner'][-6:]}")
        for row in ex["rows"]:
            lines.append(f"      {row['created_at']:<20s} {row['verdict']:<14s} {row['evaluation_id']}")
    lines.append("")
    t = result["time_decided"]
    lines.append("IF EACH ORDERABLE PAIR WERE DECIDED BY DATE (later verdict wins)")
    lines.append(f"  pairs decided by time           {t['pairs_decidable_by_time']}"
                 f" of {t['pairs_carried_both_verdicts']} carrying both verdicts")
    lines.append(f"  rows that would be suppressed   {t['rows_suppressed']}")
    lines.append(f"  hypotheses moved                {t['hypotheses_moved']}/{t['hypotheses_total']}")
    lines.append(f"  largest move                    {t['max_abs_dP']*100:.2f}pp"
                 f" ({t['hypothesis_with_largest_move']})")
    for qid, q in t["per_question"].items():
        if not q.get("leader_as_filed"):
            lines.append(f"  {qid}  (no hypothesis row for this question)")
            continue
        mark = "  <-- leader changes" if q["leader_changed"] else ""
        lines.append(f"  {qid}  {q['leader_as_filed'][-6:]} {q['leader_as_filed_pct']:.2f}%"
                     f" -> {q['leader_time_decided'][-6:]} {q['leader_time_decided_pct']:.2f}%{mark}")
    lines.append("")
    lines.append("  読み方: engine は重み付けに created_at を読まない。日付だけの行は")
    lines.append("  台帳の上で『同じ日』の内側に順序を持たない。だからこの欄は")
    lines.append("  『順序を直せば良い』とは言わない——順序を持たない行が残る。")
    lines.append("  第三節は予測ではなく範囲である: 日付で決められる対だけを日付で決め、")
    lines.append("  残りは登記どおりに残した台帳の姿。engine は加算のみで順序に依らないから、")
    lines.append("  『created_at 順に読む』はソートでは実装できない（差は 0 になる）。")
    lines.append("  実装するなら、それは行を落とす決定になる。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
