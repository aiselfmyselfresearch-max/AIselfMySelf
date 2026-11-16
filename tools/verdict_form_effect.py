#!/usr/bin/env python3
"""Did the evidence move the belief, or only the label? (stdlib only)

Why this tool exists
--------------------
On 2026-11-16 a session added ten comparative-zoology materials, wrote a
close-reading report, and recorded eight evaluations. The materials are rich;
the evaluations are eight short rows with ``verdict`` and ``evidence_type``
fields. ``belief_state.py`` reads the second and never reads the first: a
material row enters the posterior only through the hypothesis it is attached
to, and the attachment itself is written by an evaluation row.

So the archive's response to a reading session can be decomposed exactly:

  * *content* — what was read (materials, report body). The engine is blind to
    it. Adding ten materials with zero evaluations changes every posterior by
    exactly 0.0000.
  * *form* — how the reading was filed (verdict string, evidence_type,
    whether a comparison target was named, how many rows the same session
    filed). The engine reads all of these.

This tool measures the second half, so that a session can see what its own
filing did to the distribution, and what a different filing of the same
reading would have done. It is a counterfactual instrument, not a verdict on
whether the reading was any good: a precise, well-argued reading filed as
``supports`` and a hasty one filed as ``supports`` are worth the same delta.

What it computes
----------------
For a selected set of evaluation rows (default: all rows; ``--session`` limits
to one session), the posterior distribution of each core question is
recomputed under:

  baseline           every row as recorded
  removed            the selected rows deleted (i.e. the same reading, unfiled)
  all_supports       every selected row rewritten as ``supports``
  all_narrows        every selected row rewritten as ``narrows_scope``
  all_refutes        every selected row rewritten as ``refutes_unconditioned``
  no_comparison      ``compared_against_hypothesis_ids`` stripped from each row
  downgraded         ``evidence_type`` set to ``cross_session_audit``
  single_row         only the first selected row kept

Reported per question: the top hypothesis, its posterior under baseline and
under the counterfactual, the change in percentage points, and the total
variation distance between the two distributions (0..1). ``--json`` emits the
same numbers.

``--supports-scan HYP-ID`` answers a narrower question: how many identical
``supports`` rows (same session, same materials, so that the engine's
``1/sqrt(k)`` repeat discount applies) does it take to move one hypothesis by
one percentage point?

What it deliberately does NOT do
--------------------------------
* It does not judge whether a verdict was *correct*. Only the arithmetic.
* It does not change any ledger row. Counterfactuals are computed in memory.
* It does not model ``materials`` or ``readings/``. That is the point: the
  engine does not read them, and this tool makes that fact visible rather than
  asserting it.

Usage
-----
  python3 tools/verdict_form_effect.py
  python3 tools/verdict_form_effect.py --session SESSION-20261116-41c924
  python3 tools/verdict_form_effect.py --session SESSION-... --json
  python3 tools/verdict_form_effect.py --supports-scan HYP-20261114-0396ce
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state as bs  # noqa: E402


def posterior_map(state: dict[str, Any], question_id: str) -> dict[str, float]:
    """{hypothesis_id: posterior} for one question, from a belief-state dict."""
    question = (state.get("questions") or {}).get(question_id) or {}
    return {
        h["hypothesis_id"]: float(h["posterior"])
        for h in question.get("hypotheses") or []
    }


def diff_maps(before: dict[str, float], after: dict[str, float]) -> dict[str, Any]:
    """Total variation distance plus the largest single move, in percentage points."""
    keys = sorted(set(before) | set(after))
    if not keys:
        return {"tvd": 0.0, "max_delta_pp": 0.0, "max_delta_id": None, "moved": 0}
    deltas = {k: (after.get(k, 0.0) - before.get(k, 0.0)) * 100.0 for k in keys}
    l1 = sum(abs(after.get(k, 0.0) - before.get(k, 0.0)) for k in keys)
    worst = max(keys, key=lambda k: abs(deltas[k]))
    return {
        "tvd": round(0.5 * l1, 6),
        "max_delta_pp": round(deltas[worst], 3),
        "max_delta_id": worst,
        "moved": sum(1 for k in keys if abs(deltas[k]) >= 0.05),
    }


def top_of(state: dict[str, Any], question_id: str) -> str | None:
    question = (state.get("questions") or {}).get(question_id) or {}
    entries = question.get("hypotheses") or []
    if not entries:
        return None
    return max(entries, key=lambda h: (h["posterior"], h["hypothesis_id"]))["hypothesis_id"]


def attribute(
    data: dict[str, dict[str, dict[str, Any]]],
    target: str,
    question_id: str,
    top: int = 8,
    by_row: bool = False,
) -> dict[str, Any]:
    """Which session's rows hold up one hypothesis? Drop each session in turn.

    Every session that files a row on the target (or names it as a comparison)
    is removed on its own and the target's posterior is recomputed. The drop is
    not additive: rows are discounted by ``1/sqrt(k)`` per (target, verdict,
    session) and competitors recover when a comparison is withdrawn.
    """
    evaluations = data.get("evaluations") or {}
    base = bs.compute_belief_state(data=data)
    start = posterior_map(base, question_id).get(target, 0.0)
    by_session: dict[str, list[str]] = {}
    for eid, rec in evaluations.items():
        touched = rec.get("target_hypothesis_id") == target or target in (
            rec.get("compared_against_hypothesis_ids") or []
        )
        if touched:
            by_session.setdefault(str(rec.get("session_id")), []).append(eid)
    groups: dict[str, list[str]] = dict(by_session)
    if by_row:
        # one group per row, labelled by its own id, so a session's two rows
        # (one narrowing the rival, one supporting the target) stop being
        # reported as a single anonymous drop.
        groups = {
            eid: [eid]
            for eids in by_session.values()
            for eid in eids
        }
    rows = []
    for label, eids in groups.items():
        selected = {eid: evaluations[eid] for eid in eids}
        state = bs.compute_belief_state(data=_with_rows(data, selected, None))
        value = posterior_map(state, question_id).get(target, 0.0)
        rows.append({
            "session_id": label,
            "rows": len(eids),
            "without": round(value, 4),
            "drop_pp": round((start - value) * 100, 3),
            "verdict": (evaluations[label].get("verdict") if by_row else None),
            "target": (evaluations[label].get("target_hypothesis_id") if by_row else None),
        })
    rows.sort(key=lambda r: (-r["drop_pp"], r["session_id"]))
    return {
        "target": target,
        "question_id": question_id,
        "baseline": round(start, 4),
        "sessions": len(rows),
        "top": rows[:top],
        "total_drop_if_all_removed_pp": round(
            (start - posterior_map(
                bs.compute_belief_state(
                    data=_with_rows(
                        data,
                        {e: evaluations[e] for eids in by_session.values() for e in eids},
                        None,
                    )
                ),
                question_id,
            ).get(target, 0.0)) * 100,
            3,
        ),
    }


def select_rows(
    evaluations: dict[str, dict[str, Any]], session_id: str | None
) -> dict[str, dict[str, Any]]:
    """The rows a counterfactual is run on."""
    if not session_id:
        return dict(evaluations)
    return {
        eid: rec for eid, rec in evaluations.items()
        if str(rec.get("session_id")) == session_id
    }


def _with_rows(
    data: dict[str, dict[str, dict[str, Any]]],
    selected: dict[str, dict[str, Any]],
    replacement: dict[str, dict[str, Any]] | None,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Copy the ledgers, swapping the selected rows for ``replacement`` (or none)."""
    clone = {name: dict(rows) for name, rows in data.items()}
    evaluations = dict(clone.get("evaluations") or {})
    for eid in selected:
        evaluations.pop(eid, None)
    if replacement:
        evaluations.update(replacement)
    clone["evaluations"] = evaluations
    return clone


def _rewrite(selected: dict[str, dict[str, Any]], **changes: Any) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for eid, rec in selected.items():
        new = copy.deepcopy(rec)
        for key, value in changes.items():
            if value is None:
                new.pop(key, None)
            else:
                new[key] = value
        out[eid] = new
    return out


def counterfactuals(
    data: dict[str, dict[str, dict[str, Any]]],
    selected: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Every named counterfactual, computed from the same ledgers."""
    first = None
    if selected:
        first = {sorted(selected)[0]: selected[sorted(selected)[0]]}
    return {
        "baseline": _with_rows(data, {}, None),
        "removed": _with_rows(data, selected, None),
        "all_supports": _with_rows(data, selected, _rewrite(selected, verdict="supports")),
        "all_narrows": _with_rows(
            data, selected, _rewrite(selected, verdict="narrows_scope")
        ),
        "all_refutes": _with_rows(
            data, selected, _rewrite(selected, verdict="refutes_unconditioned")
        ),
        "no_comparison": _with_rows(
            data, selected, _rewrite(selected, compared_against_hypothesis_ids=[])
        ),
        "downgraded": _with_rows(
            data, selected, _rewrite(selected, evidence_type="cross_session_audit")
        ),
        "single_row": _with_rows(data, selected, first),
    }


def measure(
    data: dict[str, dict[str, dict[str, Any]]],
    session_id: str | None = None,
    questions: tuple[str, ...] = bs.CORE_QUESTIONS,
    retarget: str | None = None,
) -> dict[str, Any]:
    """Run every counterfactual and return the comparison table."""
    evaluations = data.get("evaluations") or {}
    selected = select_rows(evaluations, session_id)
    plans = counterfactuals(data, selected)
    if retarget:
        plans["retargeted"] = _with_rows(
            data, selected, _rewrite(selected, target_hypothesis_id=retarget)
        )
    states = {name: bs.compute_belief_state(data=clone) for name, clone in plans.items()}
    base = states["baseline"]
    table: dict[str, Any] = {
        "selected_rows": len(selected),
        "selected_ids": sorted(selected),
        "session_id": session_id,
        "questions": {},
        "counterfactuals": {},
    }
    for qid in questions:
        base_map = posterior_map(base, qid)
        top = top_of(base, qid)
        table["questions"][qid] = {
            "top_hypothesis_id": top,
            "top_posterior": base_map.get(top or "", 0.0) if top else 0.0,
            "hypotheses": len(base_map),
        }
        rows: dict[str, Any] = {}
        for name, state in states.items():
            if name == "baseline":
                continue
            after = posterior_map(state, qid)
            delta = diff_maps(base_map, after)
            delta["top_after"] = top_of(state, qid)
            delta["top_after_posterior"] = round(after.get(top or "", 0.0), 4) if top else 0.0
            rows[name] = delta
        table["counterfactuals"][qid] = rows
    return table


def supports_scan(
    data: dict[str, dict[str, dict[str, Any]]],
    target: str,
    question_id: str,
    limit: int = 12,
    step_pp: float = 1.0,
) -> dict[str, Any]:
    """How many repeated ``supports`` rows move the target by one percentage point?"""
    base = bs.compute_belief_state(data=data)
    base_map = posterior_map(base, question_id)
    start = base_map.get(target, 0.0)
    synthetic: dict[str, dict[str, Any]] = {}
    reached_at = None
    curve: list[dict[str, Any]] = []
    for k in range(1, limit + 1):
        eid = "EVL-SCAN-%02d" % k
        synthetic[eid] = {
            "evaluation_id": eid,
            "session_id": "SESSION-SCAN",
            "created_at": "1970-01-01",
            "target_hypothesis_id": target,
            "verdict": "supports",
            "evidence_type": "cross_session_audit",
            "summary": "scan",
            "compared_against_hypothesis_ids": [],
            "material_ids": ["MAT-SCAN"],
        }
        state = bs.compute_belief_state(data=_with_rows(data, {}, synthetic))
        value = posterior_map(state, question_id).get(target, 0.0)
        curve.append({"rows": k, "posterior": round(value, 4), "delta_pp": round((value - start) * 100, 3)})
        if reached_at is None and (value - start) * 100 >= step_pp:
            reached_at = k
    return {
        "target": target,
        "question_id": question_id,
        "start_posterior": round(start, 4),
        "step_pp": step_pp,
        "rows_to_step": reached_at,
        "curve": curve,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session", help="restrict the counterfactual to one session's evaluation rows")
    parser.add_argument("--supports-scan", metavar="HYP-ID", help="scan repeated supports rows for one hypothesis")
    parser.add_argument("--question", default="Q-003", help="question for --supports-scan / --attribute (default Q-003)")
    parser.add_argument("--retarget", metavar="HYP-ID", help="re-file every selected row against one hypothesis")
    parser.add_argument("--attribute", metavar="HYP-ID", help="per-session drop when that session's rows are removed")
    parser.add_argument("--by-row", action="store_true", help="with --attribute: one group per row instead of per session")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--root", default=str(ROOT), help="checkout to read (default: this one)")
    args = parser.parse_args(argv)

    data = bs.load_belief_ledgers(Path(args.root))
    if args.supports_scan:
        report = supports_scan(data, args.supports_scan, args.question)
    elif args.attribute:
        report = attribute(data, args.attribute, args.question, by_row=args.by_row)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True))
            return 0
        print("=== attribution: %s on %s ===" % (report["target"], report["question_id"]))
        print("baseline P=%.4f over %d touching sessions" % (report["baseline"], report["sessions"]))
        for row in report["top"]:
            extra = ""
            if row.get("target"):
                extra = "  [%s on %s]" % (row.get("verdict"), row.get("target"))
            print("  %-30s %2d row(s)  drop %+7.3f pp%s" % (row["session_id"], row["rows"], row["drop_pp"], extra))
        print("dropping every touching row at once: %+0.3f pp -> P=%.4f"
              % (-report["total_drop_if_all_removed_pp"], report["baseline"] - report["total_drop_if_all_removed_pp"] / 100))
        return 0
    else:
        report = measure(data, args.session, retarget=args.retarget)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True))
        return 0

    if args.supports_scan:
        print("=== supports scan: %s on %s ===" % (report["target"], report["question_id"]))
        print("start posterior: %.4f" % report["start_posterior"])
        for row in report["curve"]:
            print("  %2d row(s): P=%.4f  (%+.3f pp)" % (row["rows"], row["posterior"], row["delta_pp"]))
        if report["rows_to_step"] is None:
            print("no row count reached %+.1f pp within the scan" % report["step_pp"])
        else:
            print("reaches %+.1f pp at %d row(s)" % (report["step_pp"], report["rows_to_step"]))
        return 0

    print("=== verdict-form effect ===")
    print("session: %s" % (report["session_id"] or "(all evaluations)"))
    print("rows in counterfactual: %d" % report["selected_rows"])
    for qid, info in report["questions"].items():
        print("\n%s  top=%s  P=%.4f  (n=%d)" % (qid, info["top_hypothesis_id"], info["top_posterior"], info["hypotheses"]))
        for name, row in report["counterfactuals"][qid].items():
            print(
                "  %-12s TVD=%.4f  max %+7.3f pp (%s)  top_after=%s"
                % (name, row["tvd"], row["max_delta_pp"], row["max_delta_id"], row["top_after"])
            )
    print("\nThis measures the filing, not the reading. Materials are not read by the engine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
