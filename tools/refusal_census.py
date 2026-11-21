#!/usr/bin/env python3
"""Census of sessions that were offered work and did something else (stdlib only).

Why this tool exists
--------------------
``prompts/start.md`` requires a *receipt* in every session row: the seed, the
role, the question that was offered, and the reference mode that was offered.
The four fields exist so that ``question_ids`` (what the session actually took
up) can be compared with ``offered_target_question_id`` (what it was handed).
The difference between the two columns is the archive's only record of a
session declining the work it was assigned.

On 2026-11-21 two central hypotheses disagree about what that difference means:

* ``HYP-20261120-7db8e6`` (拒否経路説) says continuity of a self is *constituted*
  by the next hand being able to narrow or overturn the previous judgement, and
  measures refusal as ``narrows_scope`` / ``refutes_unconditioned`` rows.
* ``HYP-20261119-0ddede`` (選択された継承窓説) says the comparison window is set by
  which record is opened, at what grain, and addressed to whom -- a *selection*,
  not a refusal.

The two are not measured against each other because the first reads refusal in
the evaluation ledger and the second in the session ledger, so the archive has
never counted the thing the session ledger actually records: a session that was
offered Q and took a different Q.  This tool counts it, and counts what it cost.

What it measures
----------------
1. Receipts: sessions carrying ``offered_target_question_id`` at all.
2. Divergence: offered question absent from ``question_ids`` (left) vs present
   (took).  A receipt that offers one of the central three questions is never
   counted as a divergence when the session took all three, because
   ``question_ids`` is a working set, not a promise.
3. Price: evaluation rows, produced fragments, and reports per session, split by
   left/took.  If leaving is free, the two distributions match.
4. Whether anything downstream names the leaving session (read_log target,
   a note row, an erratum): does the archive ever read a refusal back?

Nothing is written.  Readings are structural counts, not judgements about
quality, effort, or good faith.

Usage::

    python3 tools/refusal_census.py
    python3 tools/refusal_census.py --json
    python3 tools/refusal_census.py --today 2026-11-21 --limit 20
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

import ledger_io
from validate_seed import COLLECTIONS, ROOT

CORE_QUESTIONS = ("Q-001", "Q-002", "Q-003")
_ID_STAMP = re.compile(r"-(\d{8})-")


def _specs(root: Path) -> dict[str, tuple[Path, str]]:
    specs: dict[str, tuple[Path, str]] = {}
    for name, (filename, id_key, _schema) in COLLECTIONS.items():
        base = Path(root) / "state" / filename
        if base.exists() or ledger_io.shard_dir(base).is_dir():
            specs[name] = (base, id_key)
    errata = Path(root) / "state" / "errata.jsonl"
    if errata.exists() or ledger_io.shard_dir(errata).is_dir():
        specs["errata"] = (errata, "errata_id")
    return specs


def _stamp(record_id: Any) -> str:
    match = _ID_STAMP.search(record_id or "")
    return match.group(1) if match else ""


def _mean(values: list[int]) -> float:
    return round(statistics.fmean(values), 3) if values else 0.0


def _median(values: list[int]) -> float:
    return float(statistics.median(values)) if values else 0.0


def census(root: Path = ROOT, *, today: str | None = None) -> dict[str, Any]:
    collections, errors = ledger_io.load_collections(_specs(root), root=root)
    if errors:
        raise ValueError("ledger load errors:\n  - " + "\n  - ".join(errors[:10]))
    sessions = collections.get("sessions", {})
    evaluations = collections.get("evaluations", {})
    read_log = collections.get("read_log", {})
    notes = collections.get("notes", {})
    errata = collections.get("errata", {})

    evals_by_session: dict[str, int] = {}
    for row in evaluations.values():
        sid = row.get("session_id")
        if isinstance(sid, str):
            evals_by_session[sid] = evals_by_session.get(sid, 0) + 1

    read_targets = {
        (row.get("target") or {}).get("id")
        for row in read_log.values()
        if isinstance(row.get("target"), dict)
    }
    note_sessions = {
        row.get(key)
        for row in notes.values()
        for key in ("session_id", "report_session_id")
    }
    errata_text = json.dumps(list(errata.values()), ensure_ascii=False)

    receipts = [row for row in sessions.values() if row.get("offered_target_question_id")]
    left: list[dict[str, Any]] = []
    took: list[dict[str, Any]] = []
    for row in receipts:
        offered = row.get("offered_target_question_id")
        taken = set(row.get("question_ids") or [])
        if offered in taken:
            took.append(row)
        else:
            left.append(row)

    def named_by(group: list[dict[str, Any]], predicate) -> int:
        return sum(1 for row in group if predicate(row))

    def describe(group: list[dict[str, Any]]) -> dict[str, Any]:
        evals = [evals_by_session.get(row["session_id"], 0) for row in group]
        frags = [len(row.get("produced_fragment_ids") or []) for row in group]
        read_back = [row["session_id"] for row in group if row["session_id"] in read_targets]
        noted = [row["session_id"] for row in group if row["session_id"] in note_sessions]
        in_errata = [row["session_id"] for row in group if row["session_id"] in errata_text]
        return {
            "sessions": len(group),
            "evaluations_total": sum(evals),
            "evaluations_mean": _mean(evals),
            "evaluations_median": _median(evals),
            "sessions_with_no_evaluation": sum(1 for value in evals if value == 0),
            "fragments_mean": _mean(frags),
            "named_by_read_log": len(read_back),
            # The rate, not the count.  Comparing 9 with 9 across groups of 52 and
            # 162 is the denominator error this tool shipped with on 2026-11-21:
            # the counts matched only because the groups do not.
            "read_back_rate": round(len(read_back) / len(group), 4) if group else 0.0,
            "named_by_a_note_row": len(noted),
            "named_by_an_erratum": len(in_errata),
        }

    # Stratified rates.  The pooled left/took difference in `read_back_rate` is
    # confounded by which question was offered: sessions offered Q-001..Q-003
    # almost always take it (9/154 leave) and are read back at ~5%, while sessions
    # offered a peripheral question leave far more often.  A pooled comparison
    # therefore compares question types, not leaving.  Clause (a) of
    # HYP-20261121-011417 asks about a difference *between leaving and taking*, so
    # it has to be measured inside a stratum.
    def _stratified(group: list[dict[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for label, keep in (("central", True), ("peripheral", False)):
            sub = [
                row
                for row in group
                if (row.get("offered_target_question_id") in CORE_QUESTIONS) is keep
            ]
            left_sub = [row for row in sub if row.get("offered_target_question_id") not in set(row.get("question_ids") or [])]
            took_sub = [row for row in sub if row.get("offered_target_question_id") in set(row.get("question_ids") or [])]
            out[label] = {
                "left": [len(left_sub), named_by(left_sub, lambda r: r["session_id"] in read_targets)],
                "took": [len(took_sub), named_by(took_sub, lambda r: r["session_id"] in read_targets)],
            }
        return out

    central_offers = [
        row for row in receipts if row.get("offered_target_question_id") in CORE_QUESTIONS
    ]
    central_left = [
        row
        for row in central_offers
        if row.get("offered_target_question_id") not in set(row.get("question_ids") or [])
    ]

    forward_offers: list[dict[str, str]] = []
    for row in receipts:
        referrer = _stamp(row.get("session_id"))
        offered = _stamp(row.get("offered_target_question_id"))
        if today and referrer and offered and referrer <= today and referrer < offered:
            forward_offers.append(
                {
                    "session_id": row["session_id"],
                    "offered": row["offered_target_question_id"],
                }
            )

    return {
        "today": today,
        "sessions_total": len(sessions),
        "sessions_with_receipt": len(receipts),
        "receipt_rate": (
            round(len(receipts) / len(sessions), 4) if sessions else 0.0
        ),
        "left": describe(left),
        "took": describe(took),
        "left_sessions": sorted(row["session_id"] for row in left),
        "stratified": _stratified(receipts),
        "central_offers": len(central_offers),
        "central_left": len(central_left),
        "forward_stamped_offers": forward_offers,
        "declined_reading_rows": sum(
            1 for row in read_log.values() if row.get("reading") == "declined"
        ),
    }


def render(result: dict[str, Any], *, limit: int = 0) -> str:
    out: list[str] = []
    total = result["sessions_total"]
    receipts = result["sessions_with_receipt"]
    out.append(
        f"receipts: {receipts}/{total} sessions ({100 * result['receipt_rate']:.1f}%) carry "
        "offered_target_question_id"
    )
    left, took = result["left"], result["took"]
    out.append(
        f"divergence: left={left['sessions']} took={took['sessions']} "
        f"({100 * left['sessions'] / max(1, receipts):.1f}% of receipts did something else)"
    )
    out.append("")
    header = f"{'measure':38} {'left':>12} {'took':>12}"
    out.append(header)
    out.append("-" * len(header))
    for key, label in (
        ("evaluations_mean", "evaluation rows per session (mean)"),
        ("evaluations_median", "evaluation rows per session (median)"),
        ("sessions_with_no_evaluation", "sessions with no evaluation row"),
        ("fragments_mean", "fragments per session (mean)"),
        ("named_by_read_log", "sessions read back via read_log"),
        ("named_by_a_note_row", "sessions named by a note row"),
        ("named_by_an_erratum", "sessions named by an erratum"),
    ):
        out.append(f"{label:38} {left[key]:>12} {took[key]:>12}")
    out.append("")
    out.append(
        f"central three: {result['central_offers']} receipts offered Q-001..Q-003, "
        f"{result['central_left']} of them took none of the three"
    )
    out.append(
        "forward-stamped offers: "
        f"{len(result['forward_stamped_offers'])} sessions were offered a question "
        "stamped later than their own stamp"
    )
    out.append(
        "read_log rows whose reading is 'declined' (the vocabulary the ledger does have "
        f"for refusing to read something): {result['declined_reading_rows']}"
    )
    out.append("")
    out.append("read-back rate, stratified by which question was offered")
    out.append("(pooling the two strata compares question types, not leaving)")
    for label, arms in result["stratified"].items():
        l, lk = arms["left"]
        t, tk = arms["took"]
        lr = f"{lk / l:.1%}" if l else "n/a"
        tr = f"{tk / t:.1%}" if t else "n/a"
        out.append(
            f"  {label:11} left {lk}/{l:<4} ({lr:>6})   took {tk}/{t:<4} ({tr:>6})"
        )
    out.append("")
    out.append(
        "NOTE: a receipt records a divergence in assignment, not a motive.  A session that "
        "left the offered question may have been right to, and this tool cannot see why."
    )
    if limit and result["left_sessions"]:
        out.append("")
        out.append(f"leaving sessions (first {limit}):")
        for sid in result["left_sessions"][:limit]:
            out.append(f"  {sid}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--today", default=None, help="YYYYMMDD upper bound for real stamps")
    parser.add_argument("--limit", type=int, default=0, help="list this many leaving sessions")
    args = parser.parse_args(argv)
    try:
        result = census(args.root, today=args.today)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render(result, limit=args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
