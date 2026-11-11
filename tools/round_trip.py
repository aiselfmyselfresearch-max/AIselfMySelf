#!/usr/bin/env python3
"""Measure *when* a report's first successor arrives, not only whether one does (stdlib only).

Why this tool exists
--------------------
``tools/inheritance.py`` answers **whether** a later session logged a reading of an
earlier report: it counts ``read_log`` rows that target a ``note`` written for a
report, excluding rows by the report's own authoring session(s). That count is the
archive's only ledger-visible evidence of a return path.

It does not answer **when**. A count without a time axis cannot distinguish two
very different archives:

  * one where successors read within the same day — a *simultaneous* archive, many
    sessions arriving at once and reading each other, with little carried across days;
  * one where successors arrive weeks later — a *cumulative* archive, a chain in time.

The difference decides what "the next session" means for ``Q-002``. A return that
arrives the same day is not a return *across* a gap; it is a reading by a
contemporary. Under the definition Einstein gives in the 1905 §1 (a common time
exists only where a signal can travel out and back), a same-day return is the
easiest case and says little about continuity.

What is measured here
---------------------
For every report that has at least one successor row (the set ``inheritance.py``
already defines, reused by import so the two tools cannot drift apart):

  * ``lag`` = reading session's real date minus the report's real date, in days,
    taken from the **first** successor (the minimum). Reader dates come from
    ``SESSION-YYYYMMDD`` ids and are rejected when later than *today* — a future
    internal-chronology label is not a date (see ``tools/read_log_backfill.py``).
  * **survival by age**: among reports at least *N* days old, the share that had a
    successor within *N* days. This is the honest form of the question — a report
    written today cannot yet fail to be read on day 10.

Nothing here is a gate, and the number is not a quality score. The ledger sees only
readers who chose to write a row; a report with no successor is *unmeasured*, not
unread. Reports with no ``notes`` row cannot be addressed by a ``note``-targeted
read_log row at all and are reported separately, never as zero.

Usage::

    python3 tools/round_trip.py                 # summary + lag table + survival
    python3 tools/round_trip.py --unmeasured    # which reports cannot be measured
    python3 tools/round_trip.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import date_axis  # noqa: E402
import inheritance  # noqa: E402

_SESSION_DATE = re.compile(r"SESSION-(\d{4})(\d{2})(\d{2})-")

#: Ages at which "read within N days" is asked. Small on purpose: the archive's
#: own records mostly fit inside a week, so a 30-day cut answers a question the
#: corpus cannot yet support (only a handful of reports are that old).
AGES = (0, 1, 3, 7, 14)


def reader_date(session_id: str | None, today: date) -> date | None:
    """The real date a reading session started, or ``None`` if none can be had."""
    if not isinstance(session_id, str):
        return None
    match = _SESSION_DATE.match(session_id)
    if not match:
        return None
    try:
        stamped = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None
    return stamped if stamped <= today else None


def report_date(real_date: str | None, today: date) -> date | None:
    parsed = date_axis.as_date(real_date)
    if parsed is None or parsed > today:
        return None
    return parsed


def measure(root: Path = ROOT, today: date | None = None) -> dict:
    today = today or date.today()
    rows, stats = inheritance.collect(root)
    lags: list[int] = []
    per_report: list[dict] = []
    undated_readers = 0
    no_note = 0
    for row in rows:
        if not row.note_ids:
            no_note += 1
            continue
        base = report_date(row.real_date, today)
        if base is None:
            continue
        found = []
        for hit in row.inherited_rows:
            when = reader_date(hit.get("session_id"), today)
            if when is None:
                undated_readers += 1
                continue
            found.append((when - base).days)
        if not found:
            continue
        first = min(found)
        lags.append(first)
        per_report.append(
            {
                "path": row.path,
                "real_date": base.isoformat(),
                "first_lag_days": first,
                "successors": len(found),
            }
        )
    lags.sort()
    survival = {}
    for age in AGES:
        cut = today - timedelta(days=age)
        cohort = [
            r for r in rows
            if r.note_ids and (d := report_date(r.real_date, today)) is not None and d <= cut
        ]
        hit = 0
        for r in cohort:
            base = report_date(r.real_date, today)
            assert base is not None
            for h in r.inherited_rows:
                when = reader_date(h.get("session_id"), today)
                if when is not None and (when - base).days <= age:
                    hit += 1
                    break
        survival[age] = {"cohort": len(cohort), "read_within": hit,
                         "share": round(hit / len(cohort), 4) if cohort else None}
    shares = {}
    if lags:
        for age in AGES:
            shares[age] = round(sum(1 for v in lags if v <= age) / len(lags), 4)
    return {
        "today": today.isoformat(),
        "reports": len(rows),
        "reports_with_notes": len(rows) - no_note,
        "reports_without_notes": no_note,
        "successor_rows": stats.get("inherited_rows"),
        "self_rows": stats.get("self_rows"),
        "reports_with_successor": sum(1 for r in rows if r.inherited_rows),
        "measured_with_dates": len(lags),
        "undated_reader_rows": undated_readers,
        "lag": {
            "median": median(lags) if lags else None,
            "min": lags[0] if lags else None,
            "max": lags[-1] if lags else None,
            "distribution": dict(sorted(Counter(lags).items())),
            "share_within": shares,
        },
        "survival_by_age": survival,
        "first_lags": sorted(per_report, key=lambda r: (-r["first_lag_days"], r["path"]))[:10],
    }


def render(result: dict) -> str:
    lag = result["lag"]
    out = []
    out.append("=== 往復の速さ（報告→後続の読み） ===")
    out.append(
        f"  報告 {result['reports']} 本 ／ notes 行のある報告 {result['reports_with_notes']} 本"
        f"（notes 無し {result['reports_without_notes']} 本は note 型の行で指せない＝未測定）"
    )
    out.append(
        f"  後続行 {result['successor_rows']} ／ 自セッション行 {result['self_rows']}"
        f" ／ 後続のある報告 {result['reports_with_successor']} 本"
    )
    out.append(f"  日付の取れた後続 {result['measured_with_dates']} 本（読者日付の取れない行 {result['undated_reader_rows']}）")
    if result["measured_with_dates"]:
        out.append(
            f"  初回の遅れ：中央値 {lag['median']} 日 ／ 最小 {lag['min']} ／ 最大 {lag['max']}"
        )
        for age in AGES:
            share = lag["share_within"].get(age)
            if share is not None:
                out.append(f"    {age} 日以内に最初の後続: {share * 100:.1f}%")
    out.append("")
    out.append("  年齢別（その年齢に達した報告だけを分母にする）")
    for age in AGES:
        s = result["survival_by_age"][age]
        if s["share"] is None:
            out.append(f"    {age:>2} 日: 分母 0（判定できない）")
        else:
            out.append(
                f"    {age:>2} 日: {s['read_within']}/{s['cohort']} = {s['share'] * 100:.1f}%"
            )
    out.append("")
    out.append("  註: 台帳は記帳された読みしか見ない。後続0は「読まれていない」ではなく「誰も書かなかった」。")
    out.append("      分母は notes 行を持ち、実日付の確定した報告だけ。未来の内部編年ラベルは日付として読まない。")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--today", help="override the real date (YYYY-MM-DD; for re-runs)")
    parser.add_argument("--unmeasured", action="store_true", help="list reports that carry no notes row")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else None
    result = measure(args.root, today)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(render(result))
    if args.unmeasured:
        rows, _ = inheritance.collect(args.root)
        print("")
        print("  notes 行を持たない報告（note 型の read_log で指せない）")
        for row in rows:
            if not row.note_ids:
                print(f"    {row.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
