#!/usr/bin/env python3
"""Per-session audit of `read_log` layer 2 after an effective date (stdlib only).

Why this tool exists
--------------------
`tools/read_log_backfill.py --check --since D --enforce` reports one aggregate
number: how many (session, context material) pairs since ``D`` have either a
hand-written reading or a ``未読の選択:`` line in ``sessions.notes``. That
aggregate hides the shape of the remaining gap. On 2026-11-13, 29 of 949
eligible pairs were unmet, and all 29 belonged to one session with 39 context
materials. A single broad-context session can therefore look like a general
failure of the rule.

This tool prints the same accounting **per session**, so that:

  * the first N eligible sessions can be inspected as a series (the design in
    ``readings/2027-03-15-how-to-make-layer-two-mandatory-without-manufacturing-records.md``
    asked for the first ten sessions to be measured);
  * a session that read some materials but never accounted for the rest is
    visible as a row, not as an anonymous remainder;
  * the difference between "read" (hand-written) and "explicitly not read"
    (``未読の選択:``) stays legible.

It is a mirror, not a gate. Exit status is 0 even when pairs are unmet; the
enforcing check remains ``read_log_backfill.py --since D --enforce``.

Usage
-----
  python3 tools/layer2_audit.py
  python3 tools/layer2_audit.py --since 2026-11-10
  python3 tools/layer2_audit.py --since 2026-11-10 --top 5
  python3 tools/layer2_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import read_log_backfill  # noqa: E402

DEFAULT_SINCE = "2026-11-10"


def context_only_pairs(read_log: dict[str, dict]) -> set[tuple[str, str]]:
    """Pairs whose only row is ``used_as_context`` (contact, not layer 2)."""
    pairs: set[tuple[str, str]] = set()
    for record in read_log.values():
        if record.get("reading") != "used_as_context":
            continue
        target = record.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        session_id = record.get("session_id")
        material_id = target.get("id")
        if isinstance(session_id, str) and isinstance(material_id, str):
            pairs.add((session_id, material_id))
    return pairs


def audit_records(
    sessions: dict[str, dict],
    read_log: dict[str, dict],
    since: date,
) -> list[dict[str, Any]]:
    """Return one row per eligible session, ordered by (date, session_id).

    A session is eligible when ``session_date`` resolves to a real date on or
    after ``since`` and the session lists at least one context material. This
    mirrors ``read_log_backfill.since_report`` so the totals agree.
    """
    hand = read_log_backfill.handwritten_pairs(read_log)
    excused = read_log_backfill.unread_choices(sessions)
    context_only = context_only_pairs(read_log)
    rows: list[dict[str, Any]] = []
    for session_id, record in sessions.items():
        started = read_log_backfill.session_date(session_id, record)
        if started is None or started < since:
            continue
        context = [
            material_id
            for material_id in (record.get("context_material_ids") or [])
            if isinstance(material_id, str) and material_id
        ]
        if not context:
            continue
        hand_pairs = [m for m in context if (session_id, m) in hand]
        excused_pairs = [
            m for m in context if (session_id, m) not in hand and (session_id, m) in excused
        ]
        unmet_pairs = [
            m
            for m in context
            if (session_id, m) not in hand and (session_id, m) not in excused
        ]
        context_only_pairs_here = [
            m for m in unmet_pairs if (session_id, m) in context_only
        ]
        unmet_without_row = [
            m for m in unmet_pairs if (session_id, m) not in context_only
        ]
        rows.append(
            {
                "date": started.isoformat(),
                "session_id": session_id,
                "context": len(context),
                "handwritten": len(hand_pairs),
                "excused": len(excused_pairs),
                "unmet": len(unmet_pairs),
                "context_only": len(context_only_pairs_here),
                "unmet_without_row": len(unmet_without_row),
                "unmet_material_ids": unmet_pairs,
                "notes_excerpt": str(record.get("notes") or "")[:140],
            }
        )
    rows.sort(key=lambda row: (row["date"], row["session_id"]))
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate a row list without hiding the per-session distribution."""
    total_pairs = sum(row["context"] for row in rows)
    handwritten = sum(row["handwritten"] for row in rows)
    excused = sum(row["excused"] for row in rows)
    unmet = sum(row["unmet"] for row in rows)
    with_unmet = [row for row in rows if row["unmet"]]
    return {
        "eligible_sessions": len(rows),
        "total_pairs": total_pairs,
        "handwritten_pairs": handwritten,
        "excused_pairs": excused,
        "unmet_pairs": unmet,
        "context_only_pairs": sum(row["context_only"] for row in rows),
        "unmet_without_row_pairs": sum(row["unmet_without_row"] for row in rows),
        "accounted_rate": round((handwritten + excused) / total_pairs, 4)
        if total_pairs
        else 0.0,
        "sessions_with_unmet": len(with_unmet),
        "first_ten": rows[:10],
        "largest_context": sorted(rows, key=lambda row: (-row["context"], row["session_id"]))[:10],
    }


def render(rows: list[dict[str, Any]], summary: dict[str, Any], top: int) -> str:
    lines: list[str] = []
    lines.append("=== layer 2 per-session audit ===")
    lines.append(
        "eligible sessions: {s} / pairs: {p} / hand-written: {h} / "
        "未読の選択: {e} / unmet: {u} (context-only: {c}, no row: {n}) / accounted: {r:.1f}%".format(
            s=summary["eligible_sessions"],
            p=summary["total_pairs"],
            h=summary["handwritten_pairs"],
            e=summary["excused_pairs"],
            u=summary["unmet_pairs"],
            c=summary["context_only_pairs"],
            n=summary["unmet_without_row_pairs"],
            r=summary["accounted_rate"] * 100,
        )
    )
    lines.append("")
    lines.append("-- first 10 eligible sessions (by date, then session_id) --")
    lines.append("date        session                    ctx  hand  exc  unmet")
    for row in summary["first_ten"]:
        lines.append(
            "{d}  {s:24s} {c:4d}  {h:4d}  {e:3d}  {u:4d}".format(
                d=row["date"], s=row["session_id"], c=row["context"],
                h=row["handwritten"], e=row["excused"], u=row["unmet"],
            )
        )
    lines.append("")
    lines.append("-- sessions with unmet pairs --")
    if not summary["sessions_with_unmet"]:
        lines.append("(none)")
    else:
        lines.append("date        session                    ctx  hand  exc  unmet")
        for row in rows:
            if row["unmet"]:
                lines.append(
                    "{d}  {s:24s} {c:4d}  {h:4d}  {e:3d}  {u:4d}  "
                    "(context-only {co}, no row {nr})".format(
                        d=row["date"], s=row["session_id"], c=row["context"],
                        h=row["handwritten"], e=row["excused"], u=row["unmet"],
                        co=row["context_only"], nr=row["unmet_without_row"],
                    )
                )
                for material_id in row["unmet_material_ids"][:5]:
                    lines.append(f"    - {material_id}")
                if len(row["unmet_material_ids"]) > 5:
                    lines.append(f"    - … and {len(row['unmet_material_ids']) - 5} more")
    lines.append("")
    lines.append(f"-- largest contexts (top {top}) --")
    lines.append("date        session                    ctx  hand  exc  unmet")
    for row in summary["largest_context"][:top]:
        lines.append(
            "{d}  {s:24s} {c:4d}  {h:4d}  {e:3d}  {u:4d}".format(
                d=row["date"], s=row["session_id"], c=row["context"],
                h=row["handwritten"], e=row["excused"], u=row["unmet"],
            )
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Per-session audit of read_log layer 2 (hand-written readings vs 未読の選択)."
    )
    parser.add_argument("--since", default=DEFAULT_SINCE, help="effective date YYYY-MM-DD (default: 2026-11-10)")
    parser.add_argument("--top", type=int, default=10, help="how many largest contexts to print (default: 10)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        since = date.fromisoformat(args.since)
    except ValueError:
        print(f"error: --since must be YYYY-MM-DD, got {args.since!r}", file=sys.stderr)
        return 2

    sessions, read_log = read_log_backfill.load(args.root)
    rows = audit_records(sessions, read_log, since)
    summary = summarize(rows)
    if args.json:
        print(json.dumps({"since": since.isoformat(), "summary": summary, "rows": rows}, ensure_ascii=False, indent=2))
    else:
        print(render(rows, summary, max(1, args.top)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
