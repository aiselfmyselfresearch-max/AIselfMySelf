#!/usr/bin/env python3
"""Ask the engine whether *which* hypothesis you name as a comparison partner matters.

Read-only. Nothing is written to any ledger. Every variant is a deep copy of the
loaded collections, and one synthetic evaluation row is appended in memory only.

Why this exists
---------------
``prompts/role_adversarial_tester.md`` tells a session to pick the highest
expected-information-gain pair and "put the two hypotheses in one row", so that
the pair is *separated*. ``HYP-20261115-d4e873`` already measured that the pair
the engine recommends is not selected by opposition. This probe asks the next
question down: when a row does name a partner, does the engine read *which*
partner it is?

It does not. In ``compute_belief_state`` the comparison set enters the arithmetic
in exactly three places, none of which reads an identity:

  * ``compared_key`` -- the sorted tuple of partner IDs, used only to build the
    repetition key for the ``1/sqrt(k)`` discount;
  * ``comp_factor`` -- ``1.0`` if the list is non-empty, else ``0.65``;
  * a fixed ``share = 0.20 * delta / len(compared)`` subtracted from every named
    partner.

So the partner is a *place to put a deduction*, not a term in a comparison. This
tool makes that statement measurable instead of asserted: it holds the target,
the verdict and the weight fixed and swaps only the partner.

Arms
----
swap      Same target, same verdict, three different partners -- one never
          separated from the target, one adjacent in rank, one from a different
          question. If the posterior vector is identical across all three, the
          partner's identity is not read. Only the verdict's sign reaches the
          target, and only a fixed deduction reaches each partner.
none      The same row with ``compared_against_hypothesis_ids: []``. The
          difference against ``swap`` is the whole of what "naming a partner"
          does: the discount is lifted (0.65 -> 1.0) and the target keeps more.
          This is the only term in the row that is about comparison at all.
leader    One row, one previously unseparated pair, injected once. Reports how
          many hypotheses change posterior, by how much the entropy moves, and
          whether the question's leader changes. A flat distribution can change
          leader on a single row; that is a property of the distribution's
          flatness, not evidence that the archive learned something.

Ledger scan
-----------
Over the live ledger: how many evaluation rows name a partner, how many distinct
(named partner, target) pairs were ever separated, how many named partners do
not share a question with the target, and how many pairs were separated more
than once. These are counts, not verdicts.

Known blindness (read before trusting the numbers)
  - The synthetic rows use one fixed verdict (``narrows_scope``) and one fixed
    evidence type. A ``supports`` row would move the target up instead of down;
    the partner arithmetic is the same, but the token is not, so the arm is
    named ``narrows_scope`` in the output.
  - "Leader changes" is measured at the present distribution. A flatter
    question would flip on a smaller row; a peaked one would not flip at all.
    The probe prints entropy alongside so the two are never read apart.
  - This measures the engine, not the archive. Nothing here says any hypothesis
    is false.

Usage::

    python3 tools/pair_identity_probe.py
    python3 tools/pair_identity_probe.py --question Q-002
    python3 tools/pair_identity_probe.py --json

Exit status is always 0: this is a measuring instrument, not a gate.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402

DEFAULT_QUESTION = "Q-003"
PROBE_EVAL_ID = "EVL-PROBE-0000"


def _ranked(state: dict[str, Any], question: str) -> list[tuple[str, float]]:
    hyps = state["questions"][question]["hypotheses"]
    return [(h["hypothesis_id"], h["posterior"])
            for h in sorted(hyps, key=lambda h: -h["posterior"])]


def _vector(state: dict[str, Any], question: str) -> dict[str, float]:
    return {h["hypothesis_id"]: h["posterior"]
            for h in state["questions"][question]["hypotheses"]}


def _probe_row(target: str, partners: list[str], question: str) -> dict[str, Any]:
    """One synthetic evaluation. Only ``compared_against_hypothesis_ids`` varies."""
    return {
        "evaluation_id": PROBE_EVAL_ID,
        "session_id": "SESSION-PROBE-0000",
        "created_at": "2026-11-17T00:00:00Z",
        "target_hypothesis_id": target,
        "verdict": "narrows_scope",
        "evidence_type": "reproducible_script",
        "summary": "synthetic probe row; never written to a ledger",
        "compared_against_hypothesis_ids": list(partners),
        "material_ids": [],
        "note_ids": [],
        "question_ids": [question],
    }


def _with_row(cols: dict[str, Any], target: str, partners: list[str],
              question: str) -> dict[str, Any]:
    c = copy.deepcopy(cols)
    c["evaluations"][PROBE_EVAL_ID] = _probe_row(target, partners, question)
    return bs.compute_belief_state(c)


def _pick_partners(cols: dict[str, Any], question: str,
                   target: str) -> dict[str, str]:
    """Three partners chosen by rank and question membership, not by content."""
    ranked = [hid for hid, _p in _ranked(bs.compute_belief_state(copy.deepcopy(cols)), question)]
    others = [h for h in ranked if h != target]
    target_q = set(cols["hypotheses"][target].get("question_ids") or [])

    def shares(hid: str) -> bool:
        return bool(target_q & set(cols["hypotheses"][hid].get("question_ids") or []))

    picked: dict[str, str] = {}
    if others:
        picked["adjacent_in_rank"] = others[1] if len(others) > 1 else others[0]
    for hid in others:
        if not shares(hid):
            picked["different_question"] = hid
            break
    # last-ranked active hypothesis in the same question: the least touched one
    for hid in reversed(others):
        if shares(hid) and hid not in picked.values():
            picked["same_question_low_rank"] = hid
            break
    return picked


def sweep(cols: dict[str, Any], cols_eval: dict[str, Any], question: str,
          target: str) -> dict[str, Any]:
    """Row-level counts over the live ledger. No simulation."""
    hyps = cols["hypotheses"]
    q_of = {hid: set(h.get("question_ids") or []) for hid, h in hyps.items()}
    rows = 0
    named: list[str] = []
    pairs: set[tuple[str, str]] = set()
    cross = 0
    repeats: dict[tuple[str, str], int] = {}
    for evl in cols_eval["evaluations"].values():
        tid = evl.get("target_hypothesis_id")
        if not isinstance(tid, str) or tid not in hyps:
            continue
        partners = [c for c in (evl.get("compared_against_hypothesis_ids") or [])
                    if isinstance(c, str)]
        if not partners:
            continue
        rows += 1
        for c in partners:
            if c not in hyps:
                continue
            named.append(c)
            if not (q_of.get(tid, set()) & q_of.get(c, set())):
                cross += 1
            key = (tid, c) if tid < c else (c, tid)
            pairs.add(key)
            repeats[key] = repeats.get(key, 0) + 1
    ordered = sorted(repeats.values(), reverse=True)
    return {
        "evaluation_rows_total": len(cols_eval["evaluations"]),
        "rows_naming_a_partner": rows,
        "named_partner_slots": len(named),
        "distinct_partner_slots": len(pairs),
        "named_partners_sharing_no_question_with_target": cross,
        "pairs_separated_more_than_once": sum(1 for v in ordered if v > 1),
        "max_separations_of_one_pair": ordered[0] if ordered else 0,
    }


def run(question: str = DEFAULT_QUESTION, root: Path | str = ROOT) -> dict[str, Any]:
    cols = bs.load_belief_ledgers(Path(root))
    state = bs.compute_belief_state(copy.deepcopy(cols))
    if question not in state["questions"]:
        raise SystemExit(f"unknown question: {question}")
    ranked = _ranked(state, question)
    if not ranked:
        raise SystemExit(f"no active hypothesis on {question}")
    target = ranked[0][0]
    base_vec = _vector(state, question)

    partners = _pick_partners(cols, question, target)
    swap: dict[str, Any] = {}
    for label, pid in partners.items():
        after = _with_row(cols, target, [pid], question)
        swap[label] = {
            "partner": pid,
            "partner_posterior_before": round(base_vec.get(pid, 0.0), 6),
            "partner_posterior_after": round(_vector(after, question).get(pid, 0.0), 6),
            "target_posterior_after": round(_vector(after, question)[target], 6),
            "vector": _vector(after, question),
        }

    vectors = [v["vector"] for v in swap.values()]
    invariance = None
    if len(vectors) > 1:
        invariance = max(
            abs(vectors[0][hid] - other[hid])
            for other in vectors[1:]
            for hid in vectors[0]
        )

    none_state = _with_row(cols, target, [], question)
    none_vec = _vector(none_state, question)

    leader_state = None
    leader_name = None
    if partners:
        leader_name = next(iter(partners))
        leader_state = _with_row(cols, target, [partners[leader_name]], question)
    moved = 0
    if leader_state is not None:
        after_vec = _vector(leader_state, question)
        moved = sum(1 for hid in base_vec if abs(base_vec[hid] - after_vec[hid]) > 1e-9)

    out: dict[str, Any] = {
        "question": question,
        "target": target,
        "target_posterior_before": round(base_vec[target], 6),
        "partners": partners,
        "swap": {k: {kk: vv for kk, vv in v.items() if kk != "vector"}
                 for k, v in swap.items()},
        "max_posterior_difference_between_partners": (
            None if invariance is None else round(invariance, 12)
        ),
        "no_partner": {
            "target_posterior_after": round(none_vec[target], 6),
            "target_delta_vs_named_partner": round(
                none_vec[target] - (swap[leader_name]["target_posterior_after"]
                                    if leader_name else none_vec[target]), 6),
        },
        "leader": {
            "before": ranked[0][0],
            "before_posterior": round(ranked[0][1], 6),
            "after": (sorted(_vector(leader_state, question).items(),
                             key=lambda kv: -kv[1])[0][0] if leader_state else None),
            "after_posterior": (round(sorted(_vector(leader_state, question).items(),
                                             key=lambda kv: -kv[1])[0][1], 6)
                                if leader_state else None),
            "hypotheses_moved": moved,
            "hypotheses_total": len(base_vec),
            "entropy_bits_before": round(state["questions"][question]["entropy_bits"], 6),
            "entropy_bits_after": (round(bs.compute_belief_state(
                copy.deepcopy({**cols, "evaluations": {
                    **cols["evaluations"],
                    PROBE_EVAL_ID: _probe_row(target, [partners[leader_name]], question)}})
            )["questions"][question]["entropy_bits"], 6) if leader_name else None),
        },
        "ledger": sweep(cols, cols, question, target),
    }
    return out


def render(result: dict[str, Any]) -> str:
    q = result["question"]
    t = result["target"]
    lines = [
        f"=== pair identity probe — {q} ===",
        f"  target: {t} (P={result['target_posterior_before'] * 100:.2f}%)",
        "",
        "ARM swap -- same row, different partner",
    ]
    for label, row in result["swap"].items():
        lines.append(
            f"  {label:26s} partner={row['partner']:22s} "
            f"target P={row['target_posterior_after'] * 100:6.2f}%  "
            f"partner P={row['partner_posterior_before'] * 100:5.2f}%"
            f" -> {row['partner_posterior_after'] * 100:5.2f}%"
        )
    inv = result["max_posterior_difference_between_partners"]
    if inv is not None:
        lines.append(
            f"  max |posterior difference| between partners: {inv:.3e}"
            + ("   <- identity not read" if inv < 1e-12 else "   <- identity IS read")
        )
    lines += [
        "",
        "ARM none -- the same row with no partner named",
        f"  target P={result['no_partner']['target_posterior_after'] * 100:6.2f}%  "
        f"(difference vs naming a partner: "
        f"{result['no_partner']['target_delta_vs_named_partner'] * 100:+.2f} pp)",
        "",
        "ARM leader -- one row, one previously unseparated pair",
        f"  before: {result['leader']['before']} ({result['leader']['before_posterior'] * 100:.2f}%)",
        f"  after : {result['leader']['after']} ({result['leader']['after_posterior'] * 100:.2f}%)"
        if result["leader"]["after"] else "  after : —",
        f"  hypotheses moved: {result['leader']['hypotheses_moved']}"
        f"/{result['leader']['hypotheses_total']}",
        f"  entropy: {result['leader']['entropy_bits_before']:.4f} -> "
        f"{result['leader']['entropy_bits_after']:.4f} bits"
        if result["leader"]["entropy_bits_after"] is not None else "",
        "",
        "LEDGER scan (counts, not verdicts)",
    ]
    for k, v in result["ledger"].items():
        lines.append(f"  {k:48s} {v}")
    lines.append("")
    lines.append("  読み方: 一つの行が「二つの仮説を比べる」操作は、この台帳に存在しない。")
    lines.append("  比べる相手は、減点を置く場所としてのみ読まれる。")
    return "\n".join(line for line in lines if line != "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run(args.question, args.root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
