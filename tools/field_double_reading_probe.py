#!/usr/bin/env python3
"""One field, two opposite meanings: what `compared_against` does to the thing it names.

Read-only. Counterfactuals run on deep copies; nothing is written to a ledger.

Why this tool exists
--------------------
``readings/2026-11-17-the-comparison-column-does-not-compare.md`` measured what
naming a *comparison partner* does to the **target**: it lifts the ``comp_factor``
discount (0.65 -> 1.0). It did not ask what naming a partner does to the
**partner**. This tool asks that, and the answer depends on the verdict, not on
the field:

  supports             the partner is charged ``0.20 * delta / len(partners)``
  narrows_scope        the partner is charged nothing; the target pays ``1.15 * delta``
  refutes_unconditioned  nothing to the partner; the target pays ``2.40 * delta``
  subsumes             nothing to the partner; the target gains ``0.85 * delta``

So on a ``supports`` row the field means "I am arguing against this", and on a
``narrows_scope`` row it means "I mentioned this" — the difference between the
two rows is a word in another field, ``verdict``.

The second reading
------------------
For the verdicts that carry a child-side term, the engine pays a boost to the
target's children::

    for shid in spawned:  log_odds[shid] += 0.75 * delta / len(spawned)   # narrows
                          log_odds[shid] += 0.95 * delta / len(spawned)   # refutes
    if not spawned:
        spawned = children_by_parent.get(target_id, [])   # lineage fallback

That fallback is keyed on lineage, never on this row's partner field. But a
comparison partner is very often a lineage child: 34 of the 68 rows measured
here name, as the hypothesis they are arguing against, the hypothesis that
inherits the target's remaining scope. In those rows one name is read twice —
once as "opponent" (penalty or nothing) and once as "heir" (a boost). Naming an
opponent can therefore *raise* it.

``compute_belief_state(..., heir_credit=False)`` (added this session, default
unchanged) drops the fallback so the two readings can be separated. Neither
number is "the right one": the fallback is deliberate (see
``readings/2026-11-14-the-verdict-arrived-before-the-hypothesis.md``). The point
is that the ledger has no field that distinguishes them, and prose does not
either (``tools/prose_disclaimer_probe.py``: 31 of 530 rows use an opposition
word at all).

Known blindness
  - "Opponent" and "heir" come from different fields, so a row can name a
    partner that is a child *by lineage only* while its prose calls it a rival
    in the argument. This tool does not read prose; it reports the overlap.
  - The lineage fallback credits children registered *after* the row was filed.
    That was measured separately (``tools/lineage_credit_accounting.py``).
  - Per-row effects are measured with every other row held fixed, so they do not
    add up to the aggregate; only the aggregate is the aggregate.
  - Only the four verdicts the engine implements are counted. A row with an
    unknown verdict is skipped by the engine and by this tool.

Usage::

    python3 tools/field_double_reading_probe.py
    python3 tools/field_double_reading_probe.py --json
    python3 tools/field_double_reading_probe.py --rows 40
    python3 tools/field_double_reading_probe.py --quick   # ~1s instead of ~92s

``--quick`` skips the two sections built from one-engine-pass-per-row: the
per-verdict partner sweep (~310 passes, one per row with partners) and the 68
single-row heir counterfactuals. Overlap counts and the aggregate need three
passes in total and are kept (~1 s). The rendered output says which sections
were skipped rather than printing zeros, so a quick run cannot be mistaken for a
measurement of nothing.

Timing, measured 2026-11-18 on this checkout: one engine pass is 0.20 s, so the
full sweep is ~380 passes ≈ 92 s (the figure in the 2026-11-17 report, 63 s, was
taken on a smaller ledger and a faster machine). Run the full sweep when the
per-row numbers are the product; use ``--quick`` for a daily look and in tests.

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

VERDICTS = ("supports", "narrows_scope", "refutes_unconditioned", "subsumes")


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


def partner_effect_by_verdict(cols: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """What naming one partner does to that partner, by verdict.

    Measured, not read off the source: for every row with exactly one partner,
    drop the partner and record the partner's change in ``log_odds``.
    """
    hyps = cols["hypotheses"]
    evals = cols["evaluations"]
    base = bs.compute_belief_state(copy.deepcopy(cols))
    buckets: dict[str, list[float]] = collections.defaultdict(list)
    for eid, evl in sorted(evals.items()):
        target = evl.get("target_hypothesis_id")
        if target not in hyps:
            continue
        verdict = str(evl.get("verdict") or "supports")
        if verdict not in VERDICTS:
            continue
        partners = [p for p in (evl.get("compared_against_hypothesis_ids") or [])
                    if p in hyps and p != target]
        if len(partners) != 1:
            continue
        clipped = copy.deepcopy(cols)
        clipped["evaluations"][eid]["compared_against_hypothesis_ids"] = []
        after = bs.compute_belief_state(clipped)
        b_lo, a_lo = _log_odds(base, partners[0]), _log_odds(after, partners[0])
        if b_lo is None or a_lo is None:
            continue
        buckets[verdict].append(round(b_lo - a_lo, 6))
    out = {}
    for verdict, deltas in buckets.items():
        nonzero = [d for d in deltas if abs(d) > 1e-9]
        out[verdict] = {
            "rows_with_one_partner": len(deltas),
            "rows_where_the_partner_moved": len(nonzero),
            "mean_d_log_odds": round(sum(deltas) / len(deltas), 6) if deltas else 0.0,
            "sum_d_log_odds": round(sum(deltas), 6),
            "sign": ("penalty" if sum(deltas) < 0 else
                     "credit" if sum(deltas) > 0 else "nothing"),
        }
    return out


def heir_overlap(cols: dict[str, Any], heir_credit: bool = True) -> dict[str, Any]:
    """Rows where a named comparison partner is also the target's heir."""
    hyps = cols["hypotheses"]
    evals = cols["evaluations"]
    children: dict[str, list[str]] = collections.defaultdict(list)
    for hid, h in hyps.items():
        for pid in (h.get("parent_hypothesis_ids") or []):
            if pid in hyps:
                children[pid].append(hid)

    rows = []
    for eid, evl in sorted(evals.items()):
        target = evl.get("target_hypothesis_id")
        if target not in hyps:
            continue
        verdict = str(evl.get("verdict") or "supports")
        if verdict not in VERDICTS:
            continue
        partners = [p for p in (evl.get("compared_against_hypothesis_ids") or [])
                    if p in hyps and p != target]
        # Mirror the engine's child list, including the fallback.
        explicit = [s for s in (evl.get("spawned_hypothesis_ids") or []) if s in hyps and s != target]
        explicit += [s for s in (evl.get("scope_inherited_by_hypothesis_ids") or [])
                     if s in hyps and s != target and s not in explicit]
        heirs = list(explicit)
        if not heirs and heir_credit:
            heirs = list(children.get(target, []))
        overlap = [p for p in partners if p in heirs]
        if overlap:
            rows.append({
                "evaluation_id": eid,
                "verdict": verdict,
                "target_hypothesis_id": target,
                "partners": partners,
                "heirs": heirs,
                "overlap": overlap,
                "heir_source": "explicit" if explicit else "lineage-fallback",
                "names_only_the_heir": set(partners) == set(overlap),
            })
    return {
        "rows": rows,
        "n_rows": len(rows),
        "n_overlap_slots": sum(len(r["overlap"]) for r in rows),
        "by_verdict": dict(collections.Counter(r["verdict"] for r in rows)),
        "by_heir_source": dict(collections.Counter(r["heir_source"] for r in rows)),
        "rows_naming_only_the_heir": sum(1 for r in rows if r["names_only_the_heir"]),
    }


def per_row_effects(cols: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each overlap row: remove only the heir from its partner list, re-measure."""
    base = bs.compute_belief_state(copy.deepcopy(cols))
    out = []
    for row in rows:
        eid = row["evaluation_id"]
        clipped = copy.deepcopy(cols)
        clipped["evaluations"][eid]["compared_against_hypothesis_ids"] = [
            p for p in row["partners"] if p not in row["overlap"]
        ]
        after = bs.compute_belief_state(clipped)
        deltas = {}
        for hid in [row["target_hypothesis_id"]] + row["overlap"]:
            b_lo, a_lo = _log_odds(base, hid), _log_odds(after, hid)
            if b_lo is None or a_lo is None:
                continue
            deltas[hid] = {
                "role": "target" if hid == row["target_hypothesis_id"] else "heir",
                "log_odds_as_filed": round(b_lo, 6),
                "log_odds_without_naming": round(a_lo, 6),
                "d_log_odds": round(b_lo - a_lo, 6),
            }
        out.append({"evaluation_id": eid, "verdict": row["verdict"],
                    "heir_source": row["heir_source"], "deltas": deltas})
    return out


def summarize(cols: dict[str, Any], per_row: bool = True) -> dict[str, Any]:
    hyps = cols["hypotheses"]
    overlap = heir_overlap(cols, heir_credit=True)
    effects = per_row_effects(cols, overlap["rows"]) if per_row else []
    heir_sum: dict[str, float] = collections.defaultdict(float)
    for eff in effects:
        for d in eff["deltas"].values():
            if d["role"] == "heir":
                heir_sum[eff["verdict"]] += d["d_log_odds"]

    # The comp_factor route: a narrowing row that names only its heir is paid
    # 1/0.65 = 1.5385x on both sides of the transfer.
    ratio = round(1.0 / 0.65, 6)
    only_heir = [r for r in overlap["rows"] if r["names_only_the_heir"]]
    filing_effect = []
    for row in (only_heir if per_row else []):
        eid = row["evaluation_id"]
        # "as filed" vs "this row had no comparison partner at all"
        clipped = copy.deepcopy(cols)
        clipped["evaluations"][eid]["compared_against_hypothesis_ids"] = []
        after = bs.compute_belief_state(clipped)
        base = bs.compute_belief_state(copy.deepcopy(cols))
        filing_effect.append({
            "evaluation_id": eid,
            "verdict": row["verdict"],
            "heirs": row["overlap"],
            "target": row["target_hypothesis_id"],
            "d_log_odds_target": {
                "as_filed": round(_log_odds(base, row["target_hypothesis_id"]), 6),
                "without_a_partner": round(_log_odds(after, row["target_hypothesis_id"]), 6),
            },
            "d_log_odds_heir": {
                hid: {
                    "as_filed": round(_log_odds(base, hid), 6),
                    "without_a_partner": round(_log_odds(after, hid), 6),
                } for hid in row["overlap"]
            },
        })

    # Aggregate: what the archive would be if the fallback did not exist.
    with_fallback = bs.compute_belief_state(copy.deepcopy(cols))
    without = bs.compute_belief_state(copy.deepcopy(cols), heir_credit=False)
    questions = {}
    for qid in ("Q-001", "Q-002", "Q-003"):
        if qid not in with_fallback["questions"]:
            continue
        a, b = with_fallback["questions"][qid], without["questions"][qid]
        if not a["hypotheses"]:
            continue  # a synthetic ledger may declare only its own question ids
        pa = {h["hypothesis_id"]: h["posterior"] for h in a["hypotheses"]}
        pb = {h["hypothesis_id"]: h["posterior"] for h in b["hypotheses"]}
        leader = max(pa.items(), key=lambda kv: kv[1])
        questions[qid] = {
            "leader": leader[0],
            "leader_posterior_with_fallback": round(leader[1], 6),
            "leader_posterior_without_fallback": round(pb.get(leader[0], 0.0), 6),
            "entropy_with_fallback": round(a["entropy_bits"], 6),
            "entropy_without_fallback": round(b["entropy_bits"], 6),
        }

    return {
        "evaluation_rows": sum(1 for e in cols["evaluations"].values()
                               if e.get("target_hypothesis_id") in hyps),
        "per_row_sections_skipped": not per_row,
        "partner_effect_by_verdict": partner_effect_by_verdict(cols) if per_row else {},
        "heir_overlap": {k: v for k, v in overlap.items() if k != "rows"},
        "heir_effect_sum_by_verdict": {k: round(v, 6) for k, v in heir_sum.items()},
        "comp_factor_ratio": ratio,
        "rows_naming_only_the_heir": filing_effect,
        "aggregate_without_fallback": questions,
        "per_row": effects,
    }


def render(result: dict[str, Any], show: int = 12) -> str:
    lines = ["=== field double-reading probe ===", ""]
    lines.append("WHAT NAMING A PARTNER DOES TO THAT PARTNER (rows with exactly one)")
    if result.get("per_row_sections_skipped"):
        lines.append("  SKIPPED (--quick): this table costs one engine pass per row")
        lines.append(f"  {'verdict':22s} {'rows':>5s} {'moved':>6s} {'sum d':>9s}  sign")
    for verdict in VERDICTS:
        s = result["partner_effect_by_verdict"].get(verdict)
        if not s:
            continue
        lines.append(f"  {verdict:22s} {s['rows_with_one_partner']:5d}"
                     f" {s['rows_where_the_partner_moved']:6d}"
                     f" {s['sum_d_log_odds']:+9.4f}  {s['sign']}")
    lines.append("")
    o = result["heir_overlap"]
    lines.append("WHERE THE NAME IS READ TWICE (partner is also the target's heir)")
    lines.append(f"  rows                          {o['n_rows']}")
    lines.append(f"  name slots                    {o['n_overlap_slots']}")
    lines.append(f"  by verdict                    {o['by_verdict']}")
    lines.append(f"  heir named by the row itself  {o['by_heir_source']}")
    lines.append(f"  rows naming the heir and nobody else   {o['rows_naming_only_the_heir']}")
    lines.append(f"  effect on the heir, summed by verdict  {result['heir_effect_sum_by_verdict']}")
    lines.append("")
    lines.append(f"THE DISCOUNT ROUTE: 1/0.65 = {result['comp_factor_ratio']:.4f}x on both sides")
    for r in result["rows_naming_only_the_heir"]:
        lines.append(f"  {r['evaluation_id']}  {r['verdict']}")
        t = r["d_log_odds_target"]
        lines.append(f"    target {r['target'][-6:]}  {t['as_filed']:+.4f} as filed"
                     f" / {t['without_a_partner']:+.4f} with no partner at all")
        for hid, v in r["d_log_odds_heir"].items():
            lines.append(f"    heir   {hid[-6:]}  {v['as_filed']:+.4f} as filed"
                         f" / {v['without_a_partner']:+.4f} with no partner at all")
    lines.append("")
    lines.append("AGGREGATE: with and without the lineage fallback (heir_credit)")
    for qid, q in result["aggregate_without_fallback"].items():
        lines.append(f"  {qid}  {q['leader']}  {q['leader_posterior_with_fallback']*100:.2f}%"
                     f" -> {q['leader_posterior_without_fallback']*100:.2f}%"
                     f"   entropy {q['entropy_with_fallback']:.4f} -> {q['entropy_without_fallback']:.4f}")
    lines.append("")
    lines.append("  読み方: どちらの数も「正しい」値ではない。台帳に、この二つの読みを")
    lines.append("  区別する欄が無いということが測られている。")
    shown = 0
    if result.get("per_row_sections_skipped"):
        lines.append("PER-ROW EFFECTS: SKIPPED (--quick)")
    for eff in result["per_row"]:
        if shown >= show:
            lines.append("  ... (see --json for all rows)")
            break
        shown += 1
        heirs = [k for k, v in eff["deltas"].items() if v["role"] == "heir"]
        print_line = "  ".join(
            f"{k[-6:]}:{v['d_log_odds']:+.4f}" for k, v in eff["deltas"].items()
        )
        lines.append(f"  {eff['evaluation_id']}  {eff['verdict']:22s} {eff['heir_source']:16s} {print_line}")
    return "\n".join(lines)


def run(root: Path | str = ROOT, per_row: bool = True) -> dict[str, Any]:
    cols = bs.load_belief_ledgers(Path(root))
    return summarize(cols, per_row=per_row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--quick", action="store_true",
                        help="skip both per-row sections (~1s instead of ~92s)")
    args = parser.parse_args(argv)
    result = run(args.root, per_row=not args.quick)
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json
          else render(result, args.rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
