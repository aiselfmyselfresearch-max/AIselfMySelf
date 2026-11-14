#!/usr/bin/env python3
"""Measure whether POSITION or SELECTION RULE carries a correction through the ledger.

Read-only. Nothing is written to any ledger. Every variant is a deep copy, and the
rule variants recompile ``belief_state`` in a private module object rather than
editing the file on disk.

Why this exists
---------------
``HYP-20261113-ccc1d8`` (position asymmetry) and ``HYP-20261113-20fa8c`` (boundary
selection rules) are the top expected-information-gain pair on Q-003. Both carry an
exclusion clause that explicitly demands a measurement on the ledger and says
「今回は測っていない」. ``readings/2026-11-13-compartment-boundary-and-relational-self.md``
§14 specifies the two protocols (選別規則の一貫性 / 位置の保持). This runs them.

Arms
----
position   Same errata content, addressed to different positions relative to the
           target. Tests ccc1d8 limb 1.
content    Same address, wildly different content (including verdict=holds and
           status=withdrawn). Tests ccc1d8 limb 2 -- and exposes that the engine
           reads neither field, so limb 2 CANNOT be settled by this channel.
rule       Vary only the 1-hop admission predicate, every ledger row untouched.
           Requires injected traffic: the live ledger has no evaluation-borne
           1-hop flag, so an unpowered run returns a meaningless all-zero.
mix        Evaluation channel: hold row count, targets and positions fixed;
           change only the verdict mix. Tests 20fa8c limb 1.

Usage::

    python3 tools/boundary_channel_probe.py
    python3 tools/boundary_channel_probe.py --arm position --json
    python3 tools/boundary_channel_probe.py --target HYP-20261113-20fa8c

Exit status is always 0: this is a measuring instrument, not a gate. A finding
that a hypothesis is wrong is a successful measurement.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402

DEFAULT_TARGET = "HYP-20261113-ccc1d8"
DEFAULT_RIVAL = "HYP-20261113-20fa8c"
QUESTION = "Q-003"

# The engine line that decides which relations admit a 1-hop errata flag.
ADMISSION_LINE = (
    '            + [e["evaluation_id"] for e in evals_by_hyp.get(hid, []) '
    'if e.get("verdict") == "supports"]'
)
RULE_REPLACEMENTS = {
    "closed": "            + []",
    "current": ADMISSION_LINE,
    "widened": '            + [e["evaluation_id"] for e in evals_by_hyp.get(hid, [])]',
}


def errata_row(subject_id: str, subject_type: str = "hypothesis", **over: Any) -> dict[str, Any]:
    """One synthetic correction. Only the fields named in ``over`` change."""
    rec = {
        "errata_id": "ERR-PROBE-0000",
        "subject_type": subject_type,
        "subject_id": subject_id,
        "claim": "当該の主張は再実行すると成立しなかった。",
        "claim_location": "probe:1",
        "check": {"kind": "manual", "params": {"scope": "boundary_channel_probe"}},
        "verdict": "contradicted",
        "status": "open",
        "created_at": "2026-11-14",
        "note": "synthetic probe row; never written to a ledger",
    }
    rec.update(over)
    return rec


def _with_rule(channel: str, source: str) -> Any:
    """Recompile belief_state with a different admission rule. File is not touched."""
    if ADMISSION_LINE not in source:
        raise RuntimeError(
            "belief_state.py no longer contains the expected 1-hop admission line; "
            "re-read the engine before trusting this probe"
        )
    mod = types.ModuleType("belief_state_rule_" + channel)
    mod.__dict__["__file__"] = bs.__file__
    code = source.replace(ADMISSION_LINE, RULE_REPLACEMENTS[channel])
    exec(compile(code, "<rule-" + channel + ">", "exec"), mod.__dict__)
    return mod


def _qstate(state: dict[str, Any], question: str) -> dict[str, Any]:
    return state["questions"][question]


def _hyp(state: dict[str, Any], question: str, hid: str) -> dict[str, Any] | None:
    for h in _qstate(state, question)["hypotheses"]:
        if h["hypothesis_id"] == hid:
            return h
    return None


def _delta(before: dict[str, Any], after: dict[str, Any], question: str,
           hid: str) -> dict[str, Any]:
    b, a = _hyp(before, question, hid), _hyp(after, question, hid)
    if b is None or a is None:
        return {"present": False}
    return {
        "present": True,
        "d_log_odds": round(a["log_odds"] - b["log_odds"], 4),
        "d_posterior": round(a["posterior"] - b["posterior"], 4),
        "errata_flags": a["errata_flags"],
        "kl_bits": _qstate(after, question)["kl_from_uniform_bits"],
    }


def run(target: str = DEFAULT_TARGET, question: str = QUESTION,
        root: Path | str = ROOT) -> dict[str, Any]:
    cols = bs.load_belief_ledgers(Path(root))
    base = bs.compute_belief_state(copy.deepcopy(cols))
    source = (Path(root) / "tools" / "belief_state.py").read_text(encoding="utf-8")

    hyp = cols["hypotheses"].get(target)
    if hyp is None:
        raise SystemExit(f"unknown hypothesis: {target}")

    sup_mat = (hyp.get("supporting_material_ids") or [None])[0]
    src_note = (hyp.get("source_note_ids") or [None])[0]
    evals = cols["evaluations"]
    sup_evl = next((eid for eid, e in sorted(evals.items())
                    if e.get("target_hypothesis_id") == target
                    and e.get("verdict") == "supports"), None)
    nar_evl = next((eid for eid, e in sorted(evals.items())
                    if e.get("target_hypothesis_id") == target
                    and e.get("verdict") == "narrows_scope"), None)

    out: dict[str, Any] = {"target": target, "question": question, "arms": {}}

    # ---- arm: position -------------------------------------------------
    positions = [
        ("judged_hypothesis", "hypothesis", target),
        ("cited_material", "material", sup_mat),
        ("cited_source_note", "note", src_note),
        ("cited_supports_evaluation", "evaluation", sup_evl),
        ("cited_narrows_evaluation", "evaluation", nar_evl),
        ("bystander_tool", "tool", "tools/belief_state.py"),
        ("bystander_session", "session", hyp.get("session_id")),
    ]
    arm: dict[str, Any] = {}
    for label, kind, sid in positions:
        if not sid:
            continue
        c = copy.deepcopy(cols)
        c["errata"]["ERR-PROBE-0000"] = errata_row(sid, kind)
        arm[label] = _delta(base, bs.compute_belief_state(c), question, target)
    out["arms"]["position"] = arm

    # ---- arm: content --------------------------------------------------
    variants = [
        ("contradicted_open", {"verdict": "contradicted", "status": "open"}),
        ("holds_open", {"verdict": "holds", "status": "open"}),
        ("unmeasurable_open", {"verdict": "unmeasurable", "status": "open"}),
        ("contradicted_withdrawn", {"verdict": "contradicted", "status": "withdrawn"}),
        ("contradicted_annotated", {"verdict": "contradicted", "status": "annotated"}),
        ("holds_withdrawn_praise", {"verdict": "holds", "status": "withdrawn",
                                    "claim": "当該の主張は再実行しても成立した。"}),
    ]
    arm = {}
    for label, over in variants:
        c = copy.deepcopy(cols)
        c["errata"]["ERR-PROBE-0000"] = errata_row(target, "hypothesis", **over)
        arm[label] = _delta(base, bs.compute_belief_state(c), question, target)
    out["arms"]["content"] = arm

    # ---- arm: rule (powered) -------------------------------------------
    powered = {}
    for tag, sid in (("via_supports_evaluation", sup_evl),
                     ("via_narrows_evaluation", nar_evl)):
        if not sid:
            continue
        c = copy.deepcopy(cols)
        c["errata"]["ERR-PROBE-0000"] = errata_row(sid, "evaluation")
        per_rule = {}
        for channel in RULE_REPLACEMENTS:
            mod = _with_rule(channel, source)
            per_rule[channel] = _delta(base, mod.compute_belief_state(copy.deepcopy(c)),
                                       question, target)
        powered[tag] = per_rule
    out["arms"]["rule_powered"] = powered

    # ---- arm: mix ------------------------------------------------------
    qh = [hid for hid, h in cols["hypotheses"].items()
          if question in (h.get("question_ids") or [])]
    eids = [eid for eid, e in sorted(evals.items()) if e.get("target_hypothesis_id") in qh]
    mixes = {
        "all_supports": lambda i: "supports",
        "all_narrows_scope": lambda i: "narrows_scope",
        "all_refutes_unconditioned": lambda i: "refutes_unconditioned",
        "alternating": lambda i: "supports" if i % 2 else "narrows_scope",
    }
    arm = {}
    for label, fn in mixes.items():
        c = copy.deepcopy(cols)
        for i, eid in enumerate(eids):
            c["evaluations"][eid]["verdict"] = fn(i)
            c["evaluations"][eid]["spawned_hypothesis_ids"] = []
        st = bs.compute_belief_state(c)
        d = _delta(base, st, question, target)
        d["evaluation_rows_held_fixed"] = len(eids)
        arm[label] = d
    out["arms"]["mix"] = arm

    # ---- live reachability of the direct-penalty branch -----------------
    idx = bs.build_errata_index(cols["errata"])
    direct = [hid for hid in cols["hypotheses"] if idx.get(hid)]
    out["direct_penalty_branch"] = {
        "live_hypotheses_with_a_direct_errata_row": len(direct),
        "live_hypothesis_count": len(cols["hypotheses"]),
        "live_errata_rows": len(cols["errata"]),
        # Measured, not hardcoded: these used to be literal False, which went stale
        # the moment the engine was fixed. Derive them from the content arm so the
        # probe cannot report a property the engine no longer has.
        "reads_verdict": len({
            round(v["d_log_odds"], 6) for k, v in out["arms"]["content"].items()
            if k in ("contradicted_open", "holds_open", "unmeasurable_open")
        }) > 1,
        "reads_status": len({
            round(v["d_log_odds"], 6) for k, v in out["arms"]["content"].items()
            if k in ("contradicted_open", "contradicted_withdrawn")
        }) > 1,
        "comment": "The -0.60 branch is latent on the live ledger: no live hypothesis "
                   "carries a direct errata row. Whether the branch reads verdict and "
                   "status is measured from the content arm above, not asserted here.",
    }
    return out


def render(res: dict[str, Any]) -> str:
    lines = [f"target={res['target']} question={res['question']}", ""]
    pos = res["arms"]["position"]
    lines.append("ARM position -- same content, different address")
    for k, v in pos.items():
        if v.get("present"):
            lines.append(f"  {k:28s} dlog_odds={v['d_log_odds']:+.4f} "
                         f"flags={len(v['errata_flags'])}")
    lines.append("")
    lines.append("ARM content -- same address, different content")
    for k, v in res["arms"]["content"].items():
        if v.get("present"):
            lines.append(f"  {k:28s} dlog_odds={v['d_log_odds']:+.4f}")
    lines.append("")
    lines.append("ARM rule (powered) -- only the admission predicate changes")
    for tag, per in res["arms"]["rule_powered"].items():
        lines.append(f"  {tag}")
        for ch, v in per.items():
            if v.get("present"):
                lines.append(f"      {ch:8s} dlog_odds={v['d_log_odds']:+.4f} "
                             f"flags={len(v['errata_flags'])}")
    lines.append("")
    lines.append("ARM mix -- row count/targets/positions fixed, verdict mix varies")
    for k, v in res["arms"]["mix"].items():
        if v.get("present"):
            lines.append(f"  {k:28s} dlog_odds={v['d_log_odds']:+.4f} "
                         f"KL={v['kl_bits']:.4f} P={v['d_posterior']:+.4f}")
    lines.append("")
    d = res["direct_penalty_branch"]
    lines.append(f"direct -0.60 branch: {d['live_hypotheses_with_a_direct_errata_row']}"
                 f"/{d['live_hypothesis_count']} hypotheses reachable, "
                 f"{d['live_errata_rows']} errata rows live")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--target", default=DEFAULT_TARGET)
    ap.add_argument("--question", default=QUESTION)
    ap.add_argument("--arm", choices=["position", "content", "rule_powered", "mix"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = run(args.target, args.question, args.root)
    if args.arm:
        res = {"target": res["target"], "question": res["question"],
               "arms": {args.arm: res["arms"][args.arm]}}
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else render(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
