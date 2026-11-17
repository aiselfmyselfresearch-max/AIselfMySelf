#!/usr/bin/env python3
"""Measure whether a row's prose disclaims the partner its own field names.

Read-only. Nothing is written to any ledger; every variant is a deep copy.

Why this exists
---------------
``readings/2026-11-17-the-comparison-column-does-not-compare.md`` §9.1(c) left its
own falsification condition unmeasured:

    (c) 行を書いた者が対立を本文に書いているなら、「台帳が対立を記録していない」
        は言い過ぎになる。記録はしている。読まれていないだけである。

This tool settles (c) for the narrow case where the prose and the field point in
**opposite directions**. It searches every evaluation ``summary`` for two shapes:

  * **disclaimer** -- the prose says the named partner is *not* in opposition
    ("とは排他的でない", "比較対象には入れない", "値は…動かない", ...), while
    ``compared_against_hypothesis_ids`` lists a hypothesis anyway;
  * **assertion** -- the prose says the two *are* in opposition ("と衝突する",
    "と対立する", ...), so the field is doing what its name says.

Each hit is then re-measured against the engine: what happens to the target and
to each named partner if the field is emptied. That difference is the only thing
"naming a partner" does, so it is also the size of the contradiction between the
row's prose and the row's arithmetic.

The asymmetry this exposes
--------------------------
For a ``supports`` row, a named partner is *not* read as a comparison either, but
the row still moves that partner down, so the prose and the arithmetic at least
point the same way by accident. For a ``narrows_scope`` row the partner moves
nothing at all; the only effect is that ``comp_factor`` rises from 0.65 to 1.0,
which makes the **target's own penalty 1.5385x larger**. So a row whose prose says
"this partner is not what I am arguing against" is, for a narrowing row,
*buying itself a harsher penalty* by naming something it just said was irrelevant.

Known blindness
  - Japanese negation is not regular. The patterns below are a lower bound: a row
    can disclaim a partner in words no pattern here matches ("別物", "射程が違う",
    "同一視しない"). Absence of a hit is not absence of a disclaimer.
  - A disclaimer may be *correct*: the row may name a partner solely to register
    that it was considered and rejected. That is exactly the case measured here,
    and it is why the finding is about what the field *does*, not about intent.
  - This reads the summary only. ``note_ids``, materials and reports may say more.
  - Substring matching cannot tell "A is not opposed to B" (disclaimer about a
    partner) from "C is not opposed to B" (a statement about a third hypothesis
    that happens to sit near a partner ID). Every hit is printed with its context
    so a reader can reject a false positive by eye.

Usage::

    python3 tools/prose_disclaimer_probe.py
    python3 tools/prose_disclaimer_probe.py --json
    python3 tools/prose_disclaimer_probe.py --show 5

Exit status is always 0: this is a measuring instrument, not a gate.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402

# Prose that says "the thing I named is not my opponent".
DISCLAIMERS: tuple[tuple[str, str], ...] = (
    (r"とは排他的でない", "explicitly not exclusive"),
    (r"排他的ではない", "explicitly not exclusive"),
    (r"比較対象には入れない", "declined as a comparison target"),
    (r"比較対象に入れない", "declined as a comparison target"),
    (r"比較対象に置かな", "declined as a comparison target"),
    (r"比較対象にしな", "declined as a comparison target"),
    (r"比較しない", "declined as a comparison target"),
    (r"比較しなか", "declined as a comparison target"),
    (r"値は.{0,15}動かない", "says the partner's value does not move"),
    (r"とは対立しない", "explicitly not opposed"),
    (r"対立するとは限らない", "explicitly not necessarily opposed"),
)

# Prose that says "the thing I named is my opponent".
ASSERTIONS: tuple[tuple[str, str], ...] = (
    (r"と衝突する", "says the partner collides"),
    (r"と対立する", "says the partner is opposed"),
    (r"とは対立する", "says the partner is opposed"),
)


def _log_odds(state: dict[str, Any], hid: str) -> float | None:
    for q in state["questions"].values():
        for h in q["hypotheses"]:
            if h["hypothesis_id"] == hid:
                return h["log_odds"]
    return None


def _posterior(state: dict[str, Any], hid: str) -> float | None:
    for q in state["questions"].values():
        for h in q["hypotheses"]:
            if h["hypothesis_id"] == hid:
                return h["posterior"]
    return None


def scan(cols: dict[str, Any]) -> list[dict[str, Any]]:
    """Rows whose prose uses one of the patterns, with a disclaimed-partner check."""
    hyps = cols["hypotheses"]
    evals = cols["evaluations"]
    hits: list[dict[str, Any]] = []
    for eid, evl in sorted(evals.items()):
        target = evl.get("target_hypothesis_id")
        if not isinstance(target, str) or target not in hyps:
            continue
        partners = [p for p in (evl.get("compared_against_hypothesis_ids") or [])
                    if isinstance(p, str) and p in hyps]
        text = evl.get("summary") or ""
        found: list[dict[str, str]] = []
        for pat, label in DISCLAIMERS:
            m = re.search(pat, text)
            if m:
                found.append({"kind": "disclaimer", "label": label, "pattern": pat,
                              "context": text[max(0, m.start() - 90):m.end() + 90]})
        for pat, label in ASSERTIONS:
            m = re.search(pat, text)
            if m:
                found.append({"kind": "assertion", "label": label, "pattern": pat,
                              "context": text[max(0, m.start() - 90):m.end() + 90]})
        if not found:
            continue
        hits.append({
            "evaluation_id": eid,
            "target_hypothesis_id": target,
            "target_title": (hyps[target].get("title") or "")[:40],
            "verdict": evl.get("verdict"),
            "evidence_type": evl.get("evidence_type"),
            # "disclaimed" is the interesting shape: prose and field disagree.
            "disclaimed_partner": any(f["kind"] == "disclaimer" for f in found) and bool(partners),
            "partner_hypothesis_ids": partners,
            "partner_titles": [(hyps[p].get("title") or "")[:40] for p in partners],
            "matches": found,
        })
    return hits


def measure(cols: dict[str, Any], hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each hit, re-run the engine with that one row's partner field emptied."""
    base = bs.compute_belief_state(copy.deepcopy(cols))
    out: list[dict[str, Any]] = []
    for hit in hits:
        eid = hit["evaluation_id"]
        clipped = copy.deepcopy(cols)
        clipped["evaluations"][eid]["compared_against_hypothesis_ids"] = []
        after = bs.compute_belief_state(clipped)
        watched = [hit["target_hypothesis_id"]] + hit["partner_hypothesis_ids"]
        deltas = {}
        for hid in watched:
            b_lo, a_lo = _log_odds(base, hid), _log_odds(after, hid)
            if b_lo is None or a_lo is None:
                continue
            deltas[hid] = {
                "log_odds_as_filed": round(b_lo, 6),
                "log_odds_without_partners": round(a_lo, 6),
                # Signed as "what naming the partner did to this hypothesis":
                # positive = naming it raised it. Without naming, the name
                # cannot act at all, so this is the size of the name's effect.
                "effect_of_the_name": round(b_lo - a_lo, 6),
                "kind": "target" if hid == hit["target_hypothesis_id"] else "partner",
            }
        out.append({
            "evaluation_id": eid,
            "verdict": hit["verdict"],
            "evidence_type": hit["evidence_type"],
            "disclaimed_partner": hit["disclaimed_partner"],
            "deltas": deltas,
        })
    return out


def summarize(cols: dict[str, Any], hits: list[dict[str, Any]],
              measured: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts over the whole ledger, including the aggregation counterfactual."""
    hyps = cols["hypotheses"]
    evals = cols["evaluations"]
    q_of = {h: set(v.get("question_ids") or []) for h, v in hyps.items()}

    rows = [e for e in evals.values() if e.get("target_hypothesis_id") in hyps]
    def cross(e: dict[str, Any]) -> bool:
        t = e["target_hypothesis_id"]
        return any(p in hyps and not (q_of[t] & q_of[p])
                   for p in (e.get("compared_against_hypothesis_ids") or []))

    narrows_cross = [e for e in rows
                     if e.get("verdict") == "narrows_scope" and cross(e)]
    # comp_factor is 1.0 with a partner and 0.65 without, so for a narrowing row
    # the difference in the target's own penalty is exactly this ratio.
    ratio = round(1.0 / 0.65, 6)

    base = bs.compute_belief_state(copy.deepcopy(cols))
    stripped = copy.deepcopy(cols)
    for e in narrows_cross:
        stripped["evaluations"][e["evaluation_id"]]["compared_against_hypothesis_ids"] = []
    after = bs.compute_belief_state(stripped)

    moved = 0
    total = 0.0
    for hid in hyps:
        b_lo, a_lo = _log_odds(base, hid), _log_odds(after, hid)
        if b_lo is None or a_lo is None:
            continue
        if abs(b_lo - a_lo) > 1e-9:
            moved += 1
            total += b_lo - a_lo

    per_question = {}
    for qid in ("Q-001", "Q-002", "Q-003"):
        if qid not in base["questions"] or not base["questions"][qid]["hypotheses"]:
            continue  # a synthetic ledger may declare only its own question ids
        b = sorted(((h["hypothesis_id"], h["posterior"]) for h in base["questions"][qid]["hypotheses"]),
                   key=lambda x: -x[1])
        a = sorted(((h["hypothesis_id"], h["posterior"]) for h in after["questions"][qid]["hypotheses"]),
                   key=lambda x: -x[1])
        per_question[qid] = {
            "leader_before": b[0][0], "leader_before_posterior": round(b[0][1], 6),
            "leader_after": a[0][0], "leader_after_posterior": round(a[0][1], 6),
            "entropy_before": round(base["questions"][qid]["entropy_bits"], 6),
            "entropy_after": round(after["questions"][qid]["entropy_bits"], 6),
        }

    return {
        "evaluation_rows": len(rows),
        "rows_matching_a_pattern": len(hits),
        "rows_with_a_disclaimed_partner": sum(1 for h in hits if h["disclaimed_partner"]),
        "rows_with_an_asserted_opponent": sum(
            1 for h in hits if any(m["kind"] == "assertion" for m in h["matches"])),
        "narrows_scope_rows_naming_a_cross_question_partner": len(narrows_cross),
        "comp_factor_ratio_with_without_partner": ratio,
        "aggregate_counterfactual": {
            "what": "empty the partner field of every narrows_scope row that names a cross-question partner",
            "hypotheses_moved": moved,
            "hypotheses_total": len(hyps),
            "sum_d_log_odds": round(total, 6),
            "per_question": per_question,
        },
        "measured": measured,
    }


def run(root: Path | str = ROOT) -> dict[str, Any]:
    cols = bs.load_belief_ledgers(Path(root))
    hits = scan(cols)
    return summarize(cols, hits, measure(cols, hits))


def render(result: dict[str, Any], show: int = 10) -> str:
    lines = ["=== prose disclaimer probe ===", ""]
    lines.append("ROWS (prose about the partner vs the field that names it)")
    lines.append(f"  evaluation rows                                {result['evaluation_rows']}")
    lines.append(f"  rows matching an opposition pattern            {result['rows_matching_a_pattern']}")
    lines.append(f"  rows whose prose DISCLAIMS a named partner     "
                 f"{result['rows_with_a_disclaimed_partner']}")
    lines.append(f"  rows whose prose ASSERTS a named opponent      "
                 f"{result['rows_with_an_asserted_opponent']}")
    lines.append("")
    lines.append("THE DISCOUNT (what naming a partner is worth to a narrowing row)")
    lines.append(f"  comp_factor with a partner / without          1.0 / 0.65 = "
                 f"{result['comp_factor_ratio_with_without_partner']:.4f}x")
    lines.append(f"  narrows_scope rows naming a cross-question partner "
                 f"{result['narrows_scope_rows_naming_a_cross_question_partner']}")
    lines.append("")
    agg = result["aggregate_counterfactual"]
    lines.append("AGGREGATE COUNTERFACTUAL")
    lines.append(f"  {agg['what']}")
    lines.append(f"  hypotheses moved  {agg['hypotheses_moved']}/{agg['hypotheses_total']}"
                 f"   sum d_log_odds {agg['sum_d_log_odds']:+.4f}")
    for qid, q in agg["per_question"].items():
        lines.append(f"  {qid}  {q['leader_before']} {q['leader_before_posterior']*100:.2f}%"
                     f" -> {q['leader_after']} {q['leader_after_posterior']*100:.2f}%"
                     f"   entropy {q['entropy_before']:.4f} -> {q['entropy_after']:.4f}")
    lines.append("")
    lines.append("DISCLAIMED PARTNERS, MEASURED (prose says 'not my opponent'; field names it)")
    shown = 0
    for m in result["measured"]:
        if not m["disclaimed_partner"]:
            continue
        if shown >= show:
            lines.append("  ... (see --json for the rest)")
            break
        shown += 1
        lines.append(f"  {m['evaluation_id']}  {m['verdict']} / {m['evidence_type']}")
        for hid, d in m["deltas"].items():
            lines.append(f"    {d['kind']:7s} {hid}  {d['log_odds_as_filed']:+.4f} as filed"
                         f" / {d['log_odds_without_partners']:+.4f} without"
                         f"   name's effect {d['effect_of_the_name']:+.4f}")
    if shown == 0:
        lines.append("  none")
    lines.append("")
    lines.append("  読み方: この欄を空にすると動く量が、「相手を名指した」ことの全効果である。")
    lines.append("  本文が『相手ではない』と言っている行でも、欄は同じだけ効く。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--show", type=int, default=10,
                        help="how many disclaimed-partner rows to print")
    args = parser.parse_args(argv)
    result = run(args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(render(result, args.show))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
