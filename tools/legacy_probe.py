#!/usr/bin/env python3
"""Measure what the archive carries forward across a disturbance (stdlib only).

Why this tool exists
--------------------
On 2026-11-14 a close-reading session on ecology (Holling 1973, Connell &
Slatyer 1977, Scheffer et al. 2001, Carpenter et al. 2001, Elmqvist et al. 2003,
Fukami & Morin 2003, Franklin et al. 2000, Nemergut et al. 2013, Standish et al.
2014, Johnstone et al. 2016) needed the ecological questions asked *of the
archive itself* rather than of the papers.  Four of those questions have a
mechanical answer, and this tool computes it:

  hysteresis   Scheffer et al.: the forward switch and the backward switch occur
               at different critical conditions.  If the belief engine were
               memoryless, removing one evaluation would restore the posterior
               that existed before it.  Does it?

  priority     Fukami & Morin: assembly order changes the shape of the relation
               between two variables, not only which endpoint is reached.  Does
               registering a hypothesis that carries *no evidence at all* move
               the distribution?

  response     Elmqvist et al.: a community keeps functioning because its members
               respond differently to the same disturbance.  How diverse is the
               archive's own response to new material?

  legacy       Franklin et al. / Johnstone et al.: material legacies (what is
               physically left) and information legacies (what is still
               articulated) can come apart, and a legacy that is lost becomes a
               debt that is only called in by a later disturbance.  Which
               material rows are still physically present but named by no
               report?

Every measurement is read-only: no ledger row is written, and the two
counterfactual arms are computed on an in-memory copy of the loaded collections.
That is deliberate.  A tool that had to write a row in order to ask "what if this
row were not here" would be unable to ask the question at all, which is itself
part of the answer (see --report).

Usage:
  python3 tools/legacy_probe.py                 # all four measurements
  python3 tools/legacy_probe.py --json
  python3 tools/legacy_probe.py --only hysteresis
  python3 tools/legacy_probe.py --only priority,response,legacy

Exit status: 0 measured, 2 could not measure.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VERDICTS = ("supports", "narrows_scope", "refutes_unconditioned", "subsumes")


def _load_belief(root: Path):
    """Load the belief collections through the engine's own loader."""
    sys.path.insert(0, str(root / "tools"))
    import belief_state as bs  # noqa: PLC0415  (deliberate late import)

    return bs, bs.load_belief_ledgers(root)


def _posteriors(bs, cols) -> dict[str, dict[str, float]]:
    state = bs.compute_belief_state(cols)
    out: dict[str, dict[str, float]] = {}
    for qid, q in state["questions"].items():
        out[qid] = {h["hypothesis_id"]: h["posterior"] for h in q["hypotheses"]}
    return out


def _flat(post: dict[str, dict[str, float]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for q in post.values():
        out.update(q)
    return out


# --------------------------------------------------------------------------
# hysteresis
# --------------------------------------------------------------------------
def hysteresis(bs, cols) -> dict:
    """Does removing an evaluation restore the posterior from before it?

    Scheffer et al. (2001): "the forward and backward switches occur at
    different critical conditions ... known as hysteresis".  The archive's
    analogue is exact: run the engine with a row, remove that row, run again.
    A memoryless engine returns to the earlier value.  A hysteretic one does
    not, and the residue measures how much the removed row is holding.
    """
    base = _flat(_posteriors(bs, cols))
    evals = cols["evaluations"]
    rows = []
    for ev in sorted(evals.values(), key=lambda e: e["evaluation_id"]):
        if ev.get("verdict") != "refutes_unconditioned":
            continue
        target = ev.get("target_hypothesis_id")
        if target not in base:
            continue
        arm = copy.deepcopy(cols)
        del arm["evaluations"][ev["evaluation_id"]]
        without = _flat(_posteriors(bs, arm)).get(target, 0.0)
        rows.append(
            {
                "evaluation_id": ev["evaluation_id"],
                "target_hypothesis_id": target,
                "posterior_with": round(base[target], 6),
                "posterior_without": round(without, 6),
                "delta": round(base[target] - without, 6),
            }
        )
    rows.sort(key=lambda r: -abs(r["delta"]))
    moved = [r for r in rows if abs(r["delta"]) > 1e-9]
    return {
        "refuting_rows": len(rows),
        "rows_whose_removal_moves_the_posterior": len(moved),
        "rows_whose_removal_moves_nothing": len(rows) - len(moved),
        "total_absolute_movement": round(sum(abs(r["delta"]) for r in rows), 6),
        "largest": rows[:6],
    }


# --------------------------------------------------------------------------
# priority
# --------------------------------------------------------------------------
def priority(bs, cols) -> dict:
    """Does a hypothesis carrying no evidence at all move the distribution?

    Fukami & Morin (2003) found that assembly sequence changed the *shape* of
    the productivity-diversity relation, not just its endpoint.  The analogue
    here is sharper than it looks: the probe hypothesis below has no
    evaluations, no supporting material, no notes.  It contributes nothing to
    the likelihood.  If the posterior still moves, then the engine's output
    depends on which possibilities were *registered*, not only on what was
    measured against them.
    """
    qid = "Q-001"
    before = _posteriors(bs, cols)
    if qid not in before:
        return {"measurable": False, "reason": f"{qid} absent"}

    probe_id = "HYP-PROBE-LEGACY"
    probe = {
        "hypothesis_id": probe_id,
        "question_ids": [qid],
        "title": "PROBE (no evidence, never evaluated)",
        "proposition": "registered only to measure arrival-order effect",
        "status": "active",
        "lineage_op": "refines",
        "parent_hypothesis_ids": [],
        "scope_conditions": ["probe"],
        "exclusion_clause": "probe",
        "supporting_material_ids": [],
        "counter_material_ids": [],
        "source_note_ids": [],
    }

    arm = copy.deepcopy(cols)
    arm["hypotheses"][probe_id] = probe
    added = _posteriors(bs, arm)

    back = copy.deepcopy(arm)
    del back["hypotheses"][probe_id]
    restored = _posteriors(bs, back)

    rows = []
    for hid in sorted(set(before[qid]) | set(added[qid])):
        b = before[qid].get(hid, 0.0)
        a = added[qid].get(hid, 0.0)
        r = restored[qid].get(hid, 0.0)
        rows.append(
            {
                "hypothesis_id": hid,
                "before": round(b, 6),
                "with_probe": round(a, 6),
                "after_removal": round(r, 6),
                "shift_pt": round((a - b) * 100, 4),
                "restored_exactly": abs(r - b) < 1e-9,
            }
        )
    rows.sort(key=lambda x: -abs(x["shift_pt"]))
    return {
        "measurable": True,
        "question_id": qid,
        "members_before": len(before[qid]),
        "members_with_probe": len(added[qid]),
        "max_abs_shift_pt": max((abs(r["shift_pt"]) for r in rows), default=0.0),
        "every_before_value_restored_after_removal": all(r["restored_exactly"] for r in rows),
        "ledger_after_removal_identical_to_start": True,
        "rows": rows,
    }


# --------------------------------------------------------------------------
# response
# --------------------------------------------------------------------------
def response(bs, cols) -> dict:
    """How diverse is the archive's response to new material?

    Elmqvist et al. (2003): "Response diversity enables the community to keep
    performing in the same complementary way in the face of stresses and
    disturbances."  A system whose members all answer the same way has high
    redundancy and low response diversity: it is robust to the average
    disturbance and brittle to the one it has no distinct answer to.
    """
    evals = list(cols["evaluations"].values())
    counts = Counter(e.get("verdict") for e in evals)
    total = sum(counts.values())
    entropy = -sum((v / total) * math.log2(v / total) for v in counts.values()) if total else 0.0
    observed = [v for v in counts if v]
    max_entropy = math.log2(len(observed)) if len(observed) > 1 else 0.0

    by_target: dict[str, Counter] = defaultdict(Counter)
    by_session: dict[str, Counter] = defaultdict(Counter)
    for e in evals:
        by_target[e.get("target_hypothesis_id")][e.get("verdict")] += 1
        by_session[e.get("session_id")][e.get("verdict")] += 1

    multi = {s: c for s, c in by_session.items() if sum(c.values()) >= 2}
    single = [s for s, c in multi.items() if len(c) == 1]

    # a hypothesis answered in only one way is a hypothesis the archive has
    # only one kind of reply to
    mono = [t for t, c in by_target.items() if len(c) == 1 and sum(c.values()) >= 3]

    return {
        "evaluations": total,
        "verdict_counts": dict(counts),
        "dominant_verdict": counts.most_common(1)[0][0] if counts else None,
        "dominant_share_pct": round(counts.most_common(1)[0][1] / total * 100, 2) if total else 0.0,
        "refute_share_pct": round(counts.get("refutes_unconditioned", 0) / total * 100, 2) if total else 0.0,
        "narrow_to_refute_ratio": (
            round(counts.get("narrows_scope", 0) / counts["refutes_unconditioned"], 2)
            if counts.get("refutes_unconditioned")
            else None
        ),
        "entropy_bits": round(entropy, 4),
        "max_entropy_bits": round(max_entropy, 4),
        "sessions_with_2plus_evaluations": len(multi),
        "sessions_with_a_single_verdict": len(single),
        "single_verdict_share_pct": round(len(single) / len(multi) * 100, 2) if multi else 0.0,
        "hypotheses_reached_by_one_verdict_only": len(mono),
    }


# --------------------------------------------------------------------------
# legacy
# --------------------------------------------------------------------------
def _load_materials(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    base = root / "state" / "materials.jsonl"
    if base.exists():
        for line in base.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                out[row["material_id"]] = row
    shard_dir = root / "state" / "materials.d"
    if shard_dir.is_dir():
        for path in sorted(shard_dir.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    out[row["material_id"]] = row
    return out


def _blob(root: Path, pattern: str) -> str:
    text = []
    for path in sorted(root.glob(pattern)):
        text.append(path.read_text(encoding="utf-8"))
    return "\n".join(text)


def legacy(root: Path = ROOT) -> dict:
    """Which material rows are still present but no longer articulated?

    Franklin et al. (2000): biological legacies are "the organisms, organic
    materials, and organically-generated environmental patterns that persist
    through a disturbance and are incorporated into the recovering ecosystem".
    Johnstone et al. (2016) split that into *material* and *information*
    legacies, and note that losing legacies "generates a resilience debt that
    manifests only after the system is disturbed".

    A material row is a material legacy: bytes in a shard, which nothing can
    remove.  A report that names it is an information legacy.  The interesting
    rows are the ones with the first and not the second — present, unread.
    """
    materials = _load_materials(root)
    reports = sorted((root / "readings").glob("*.md"))
    report_text = [p.read_text(encoding="utf-8") for p in reports]

    notes = _blob(root, "state/notes.jsonl") + "\n" + _blob(root, "state/notes.d/*.jsonl")
    evals = _blob(root, "state/evaluations.jsonl") + "\n" + _blob(root, "state/evaluations.d/*.jsonl")
    context = _blob(root, "state/sessions.d/*.jsonl") + "\n" + _blob(root, "state/read_log.d/*.jsonl")

    unnamed = [m for m in materials if not any(m in t for t in report_text)]
    in_note = sum(1 for m in unnamed if m in notes)
    in_eval = sum(1 for m in unnamed if m in evals and m not in notes)
    only_context = len(unnamed) - in_note - in_eval
    true_orphan = sum(1 for m in unnamed if m not in notes and m not in evals and m not in context)

    return {
        "materials": len(materials),
        "reports": len(reports),
        "named_by_a_report": len(materials) - len(unnamed),
        "named_share_pct": round((len(materials) - len(unnamed)) / len(materials) * 100, 2)
        if materials
        else 0.0,
        "present_but_unnamed": len(unnamed),
        "of_those_kept_by_a_note": in_note,
        "of_those_kept_only_by_an_evaluation": in_eval,
        "of_those_kept_only_as_context": only_context,
        "of_those_cited_nowhere_at_all": true_orphan,
        "sample_unnamed": unnamed[:8],
    }


# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure what the archive carries forward across a disturbance."
    )
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--only",
        default="hysteresis,priority,response,legacy",
        help="comma-separated subset",
    )
    args = ap.parse_args(argv)

    wanted = [w.strip() for w in args.only.split(",") if w.strip()]
    unknown = [w for w in wanted if w not in ("hysteresis", "priority", "response", "legacy")]
    if unknown:
        print(f"unknown measurement(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    root = args.root.resolve()
    try:
        bs, cols = _load_belief(root)
    except Exception as exc:  # pragma: no cover - environment failure only
        print(f"cannot load belief ledgers: {exc}", file=sys.stderr)
        return 2

    result: dict[str, object] = {}
    if "hysteresis" in wanted:
        result["hysteresis"] = hysteresis(bs, cols)
    if "priority" in wanted:
        result["priority"] = priority(bs, cols)
    if "response" in wanted:
        result["response"] = response(bs, cols)
    if "legacy" in wanted:
        result["legacy"] = legacy(root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if "hysteresis" in result:
        h = result["hysteresis"]
        print("## hysteresis  (Scheffer et al. 2001)")
        print(f"  refuting rows: {h['refuting_rows']}")
        print(f"  removal moves the posterior: {h['rows_whose_removal_moves_the_posterior']}")
        print(f"  removal moves nothing:       {h['rows_whose_removal_moves_nothing']}")
        print(f"  total absolute movement:     {h['total_absolute_movement']:.4f}")
        for r in h["largest"]:
            print(
                f"    {r['evaluation_id']:24s} {r['target_hypothesis_id']:24s}"
                f" {r['posterior_with'] * 100:7.2f}% -> {r['posterior_without'] * 100:7.2f}%"
                f"  ({r['delta']:+.4f})"
            )
        print()

    if "priority" in result:
        p = result["priority"]
        print("## priority  (Fukami & Morin 2003)")
        if not p.get("measurable"):
            print(f"  not measurable: {p.get('reason')}")
        else:
            print(f"  question {p['question_id']}: {p['members_before']} members"
                  f" -> {p['members_with_probe']} with the evidence-free probe")
            print(f"  largest shift from a hypothesis carrying no evidence:"
                  f" {p['max_abs_shift_pt']:.2f} pt")
            print(f"  removal restores every earlier value exactly:"
                  f" {p['every_before_value_restored_after_removal']}")
            for r in p["rows"]:
                if abs(r["shift_pt"]) < 0.01 and r["hypothesis_id"] != "HYP-PROBE-LEGACY":
                    continue
                print(
                    f"    {r['hypothesis_id']:26s} {r['before'] * 100:7.2f}%"
                    f" -> {r['with_probe'] * 100:7.2f}% -> {r['after_removal'] * 100:7.2f}%"
                    f"  ({r['shift_pt']:+.2f} pt)"
                )
        print()

    if "response" in result:
        r = result["response"]
        print("## response  (Elmqvist et al. 2003)")
        print(f"  evaluations: {r['evaluations']}  verdicts: {r['verdict_counts']}")
        print(f"  dominant response: {r['dominant_verdict']} = {r['dominant_share_pct']:.2f}%")
        print(f"  refutation share:  {r['refute_share_pct']:.2f}%"
              f"  (narrow:refute = {r['narrow_to_refute_ratio']}:1)")
        print(f"  entropy: {r['entropy_bits']:.4f} of {r['max_entropy_bits']:.4f} bits")
        print(f"  sessions with >=2 evaluations: {r['sessions_with_2plus_evaluations']},"
              f" of which single-verdict: {r['sessions_with_a_single_verdict']}"
              f" ({r['single_verdict_share_pct']:.1f}%)")
        print(f"  hypotheses answered in only one way (>=3 evaluations):"
              f" {r['hypotheses_reached_by_one_verdict_only']}")
        print()

    if "legacy" in result:
        g = result["legacy"]
        print("## legacy  (Franklin et al. 2000; Johnstone et al. 2016)")
        print(f"  materials: {g['materials']}  reports: {g['reports']}")
        print(f"  named by a report: {g['named_by_a_report']} ({g['named_share_pct']:.2f}%)")
        print(f"  present but unnamed: {g['present_but_unnamed']}")
        print(f"    kept by a note:        {g['of_those_kept_by_a_note']}")
        print(f"    kept only by an eval:  {g['of_those_kept_only_by_an_evaluation']}")
        print(f"    kept only as context:  {g['of_those_kept_only_as_context']}")
        print(f"    cited nowhere at all:  {g['of_those_cited_nowhere_at_all']}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
