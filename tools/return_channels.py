#!/usr/bin/env python3
"""Which channels of this archive are returned to, and by whom? (stdlib only)

Why this tool exists
--------------------
``tools/inheritance.py`` already measures one channel: whether a ``readings/*.md``
report was read by a later session.  The Q-002 hypothesis pair tested on
2026-11-16 (``HYP-20261113-977052`` vs ``HYP-20261114-874658``) needs a wider
instrument, because it is not about reports only.  It asks whether a record of
any kind is *re-entered* by a later session, and whether the presence of a
re-executable path (a stable id plus a procedure) is what causes that.

So this tool counts, per ledger collection, how many records were read back by a
session other than the one that wrote them, and separates two things that the
archive has been treating as one:

``session traversal``
    a handwritten ``read_log`` row (``note`` without ``機械的バックフィル``)
    written by a session that is not the record's author.  This is a later
    reader coming back.

``instrument traversal``
    a ``check`` on an ``errata`` row that a tool can re-execute now (delegated to
    ``tools/errata_audit.run_check``).  This is a procedure coming back, with no
    reader involved.

It also reports whether the materials cited by each ``evaluations`` row were
actually read in the same session, which is the wiring question behind the
citation channel.

Nothing here is a quality gate.  The numbers say where the archive returns and
where it does not; they are not a score.

Usage::

    python3 tools/return_channels.py
    python3 tools/return_channels.py --json
    python3 tools/return_channels.py --today 2026-11-16
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import errata_audit  # noqa: E402

SPECS = {
    "questions": ("question_id", True),
    "notes": ("note_id", True),
    "hypotheses": ("hypothesis_id", True),
    "errata": ("errata_id", True),
    "materials": ("material_id", False),
    "read_log": ("read_id", False),
    "evaluations": ("evaluation_id", False),
    "fragments": ("fragment_id", False),
    "sessions": ("session_id", False),
}

MECHANICAL_PREFIXES = ("機械的バックフィル", "機械的接触行")


def parse_date(value) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def author_session(collection: str, record: dict) -> str | None:
    """The session that wrote a record, when the ledger records it."""
    if collection == "notes":
        return record.get("report_session_id") or record.get("session_id")
    if collection == "hypotheses":
        return record.get("session_id")
    if collection in ("questions", "materials"):
        origin = record.get("origin")
        if isinstance(origin, dict):
            return origin.get("session_id")
    return None


def load() -> dict[str, dict[str, dict]]:
    specs = {
        name: (ROOT / "state" / f"{name}.jsonl", id_key)
        for name, (id_key, _dated) in SPECS.items()
    }
    records, errors = ledger_io.load_collections(specs, root=ROOT)
    if errors:
        for line in errors:
            print(f"[ledger] {line}", file=sys.stderr)
    return records


def first_return(handwritten: list[dict]) -> dict[tuple[str, str], tuple[dt.date | None, str]]:
    """Earliest handwritten read per (target type, target id)."""
    first: dict[tuple[str, str], tuple[dt.date | None, str]] = {}
    for row in handwritten:
        target = row.get("target") or {}
        key = (target.get("type"), target.get("id"))
        when = parse_date(row.get("created_at"))
        prev = first.get(key)
        if prev is None or (when and (prev[0] is None or when < prev[0])):
            first[key] = (when, row.get("session_id") or "")
    return first


def channel_table(records, handwritten, today, cohorts=(1, 7, 10)):
    first = first_return(handwritten)
    table = []
    for collection in ("questions", "notes", "hypotheses", "errata", "materials"):
        rows = list(records.get(collection, {}).values())
        dated = SPECS[collection][1]
        future = new = returned = 0
        within = collections.Counter()
        old = old_never = 0
        for record in rows:
            key = (singular(collection), record.get(SPECS[collection][0]))
            hit = first.get(key)
            author = author_session(collection, record)
            by_other = bool(hit) and (author is None or hit[1] != author)
            created = parse_date(record.get("created_at")) if dated else None
            if created and created > today:
                future += 1
                continue
            new += 1
            if by_other:
                returned += 1
            if created and hit and hit[0]:
                lag = (hit[0] - created).days
                if by_other:
                    for horizon in cohorts:
                        if 0 <= lag <= horizon:
                            within[horizon] += 1
            if created and (today - created).days >= max(cohorts):
                old += 1
                if not by_other:
                    old_never += 1
        table.append({
            "collection": collection,
            "total": len(rows),
            "future_dated": future,
            "dated": dated,
            "new": new,
            "returned": returned,
            "returned_pct": round(100.0 * returned / new, 1) if new else None,
            "within": {str(h): within[h] for h in cohorts},
            "aged": old,
            "aged_never_returned": old_never,
            "aged_never_pct": round(100.0 * old_never / old, 1) if old else None,
        })
    return table


def singular(collection: str) -> str:
    return {
        "questions": "question",
        "notes": "note",
        "hypotheses": "hypothesis",
        "errata": "erratum",
        "materials": "material",
    }[collection]


def obligation_split(records, handwritten):
    """Errata: does a session come back, and can an instrument come back?"""
    first = first_return(handwritten)
    fragments = list(records.get("fragments", {}).values())
    materials = list(records.get("materials", {}).values())
    buckets = {"path": {"records": 0, "session_visits": 0, "instrument_runnable": 0},
               "content_only": {"records": 0, "session_visits": 0, "instrument_runnable": 0}}
    for row in records.get("errata", {}).values():
        try:
            result = errata_audit.run_check(row.get("check") or {}, fragments, materials)
            runnable = bool(result.get("measurable"))
        except Exception:  # a check whose subject is missing is not runnable
            runnable = False
        kind = "path" if runnable else "content_only"
        buckets[kind]["records"] += 1
        buckets[kind]["instrument_runnable"] += int(runnable)
        if first.get(("erratum", row.get("errata_id"))):
            buckets[kind]["session_visits"] += 1
    return buckets


def citation_wiring(records, handwritten):
    """Were the materials cited by an evaluation read by the same session?"""
    read_by_session: dict[str, set[tuple[str, str]]] = collections.defaultdict(set)
    for row in handwritten:
        target = row.get("target") or {}
        read_by_session[row.get("session_id") or ""].add((target.get("type"), target.get("id")))
    counts = {"evaluations_with_materials": 0, "all_read": 0, "partial_read": 0, "none_read": 0}
    verdicts = collections.Counter()
    for row in records.get("evaluations", {}).values():
        cited = [m for m in (row.get("material_ids") or []) if isinstance(m, str)]
        if not cited:
            continue
        counts["evaluations_with_materials"] += 1
        seen = read_by_session.get(row.get("session_id") or "", set())
        hit = sum(1 for m in cited if ("material", m) in seen)
        label = "all_read" if hit == len(cited) else ("none_read" if hit == 0 else "partial_read")
        counts[label] += 1
        verdicts[(label, row.get("verdict"))] += 1
    return counts, {
        f"{label}/{verdict}": n for (label, verdict), n in sorted(verdicts.items())
    }


def build(today: dt.date) -> dict:
    records = load()
    read_log = list(records.get("read_log", {}).values())
    handwritten = [
        r for r in read_log
        if not (r.get("note") or "").startswith(MECHANICAL_PREFIXES)
    ]
    counts, by_verdict = citation_wiring(records, handwritten)
    return {
        "today": today.isoformat(),
        "read_log": {
            "rows": len(read_log),
            "handwritten": len(handwritten),
            "mechanical": len(read_log) - len(handwritten),
        },
        "channels": channel_table(records, handwritten, today),
        "obligations": obligation_split(records, handwritten),
        "citations": {"counts": counts, "by_verdict": by_verdict},
    }


def pct(part: int, whole: int) -> str:
    return f"{100.0 * part / whole:5.1f}%" if whole else "    —"


def print_report(report: dict) -> None:
    logs = report["read_log"]
    print("=== return channels (handwritten read_log only) ===")
    print(f"today={report['today']}  read_log {logs['rows']} rows "
          f"= handwritten {logs['handwritten']} + mechanical {logs['mechanical']}")
    print("returned = read back by a session other than the author\n")
    header = ("collection", "records", "future", "dated", "returned", "  %",
              "within1d", "within7d", "age>=10d", "never", "   %")
    print("{:11s} {:>7s} {:>6s} {:>5s} {:>8s} {:>6s} {:>8s} {:>8s} {:>8s} {:>5s} {:>6s}".format(*header))
    for row in report["channels"]:
        print("{:11s} {:7d} {:6d} {:>5s} {:8d} {:>6s} {:>8d} {:>8d} {:8d} {:5d} {:>6s}".format(
            row["collection"], row["total"], row["future_dated"],
            "yes" if row["dated"] else "no", row["returned"],
            pct(row["returned"], row["new"]),
            row["within"]["1"], row["within"]["7"], row["aged"],
            row["aged_never_returned"], pct(row["aged_never_returned"], row["aged"]),
        ))
    print("\n(dated=no: the collection has no created_at, so only the raw return count is shown)")
    print("\n=== obligations (errata): path vs content only ===")
    for label, title in (("path", "re-executable now"), ("content_only", "no procedure a tool can run")):
        bucket = report["obligations"][label]
        print(f"{label:13s} ({title:28s}) records {bucket['records']:4d}  "
              f"session visits {bucket['session_visits']:3d} "
              f"({pct(bucket['session_visits'], bucket['records'])})  "
              f"instrument-runnable {bucket['instrument_runnable']:3d}")
    print("\n=== citations: were cited materials read in the same session? ===")
    counts = report["citations"]["counts"]
    n = counts["evaluations_with_materials"]
    print(f"evaluations with material_ids {n}")
    for label in ("all_read", "partial_read", "none_read"):
        print(f"  {label:13s} {counts[label]:4d} ({pct(counts[label], n)})")
    print("verdict split by class:")
    for key, value in report["citations"]["by_verdict"].items():
        print(f"  {key:26s} {value:4d}")
    print("\nThis tool writes nothing.  A return is not a reading, and a visit is not agreement.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--today", default=None, help="YYYY-MM-DD (default: environment UTC date)")
    args = parser.parse_args()
    today = parse_date(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    report = build(today)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
