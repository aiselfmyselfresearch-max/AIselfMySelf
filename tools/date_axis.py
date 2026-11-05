#!/usr/bin/env python3
"""Collapse the archive's two clocks into one ordered axis (stdlib only).

Why this module exists
----------------------
This repository has carried two chronologies since 2026-10-28:

* the **real date** — the date of the execution environment, written into the
  session ID, ``readings/`` headers and ``notes.date_real``;
* the **internal chronology label** — the ``started_at`` value, which after
  2026-10-28 walked on into the future (``2027-02-23``) while the real date
  stayed in November 2026, and which was also used for the *file names* in
  ``readings/`` and for new material/note IDs.

``docs/memory-architecture.md`` §2 recorded the consequence: *"時系列という軸自体が、
この書庫には二つあって、どちらも信用できない"*. A repository whose subject is the
self that continues through a record cannot leave its own timeline unreadable,
so this module builds a single ordered axis out of what the ledgers already
hold, without rewriting a single past row:

  * **no labels are rewritten.** ``started_at`` keeps its value; the axis only
    says where that value actually falls in time, and whether it is a real date
    or a label that ran ahead of one.
  * **nothing is derived by guessing across a gap.** A label whose real date is
    not recorded stays ``未記録`` instead of being interpolated from its
    neighbours. An axis with holes is still ordered; a filled-in hole is a
    fabricated date.
  * **new rows will not be minted in the future.** ``assert_writable_day()``
    is the one write-side rule: the *ID prefix* (``YYYYMMDD`` in ``SESSION-``,
    ``MAT-``, ``NOTE-``, ``ERR-``) is now a real date always, because it is what
    the axis reads. The human-readable label may still be pasted verbatim from
    the delegation (``prompts/start.md`` tells a session not to invent order),
    but it is never the first key of any chronology again.

Sources, in the order this module prefers them (each is recorded per row, so a
reader can see which rule placed a row):

  1. ``notes.date_real`` for the report a session wrote (curated judgment);
  2. an explicit real-date marker inside ``sessions.notes`` / ``human_direction``
     (``実作業日 2026-11-05``, ``実行日（UTC）2026-11-04`` …);
  3. ``started_at`` itself, *only when it is already a real date* — i.e. a
     calendar-shaped value that is not later than today. This is what makes the
     2026-10-22..11-05 block readable without any curation at all;
  4. otherwise: ``未記録``.

A ``started_at`` later than today is never read as a date. That single rule is
what separates the label from the date, and it needs no list of exceptions.

Usage::

    python3 tools/date_axis.py                 # the axis, one line per label
    python3 tools/date_axis.py --json          # machine-readable
    python3 tools/date_axis.py --anomalies     # labels not equal to their real date
    python3 tools/date_axis.py --sort          # unlabeled: label order + verdict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402

UNRECORDED = "未記録"

#: ``SESSION-20261105-c91bde``, ``MAT-LIT-20270222-198b7c``, ``ERR-20261031-...``
_ID_DATE = re.compile(r"^[A-Z][A-Z-]*?-(\d{4})(\d{2})(\d{2})-")

#: Real-date markers actually used in the archive's headers and session notes.
#: Ordered most specific first; the first hit wins and its rule name is kept.
_REAL_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("実日付", re.compile(r"実日付[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実作業日", re.compile(r"実作業日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実UTC日付", re.compile(r"実UTC日付[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実行日", re.compile(r"実行日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実環境日", re.compile(r"実環境日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
)

_DATE_SHAPE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


@dataclass
class AxisRow:
    """One internal-chronology label and where it really sits in time."""

    label: str
    sessions: int = 0
    real_dates: Counter = field(default_factory=Counter)
    sources: Counter = field(default_factory=Counter)
    session_ids: list[str] = field(default_factory=list)
    provisional: bool = False

    @property
    def real_date(self) -> str | None:
        """The single real date for this label, or ``None`` if they disagree."""
        if len(self.real_dates) == 1:
            return next(iter(self.real_dates))
        return None

    @property
    def real_span(self) -> tuple[str, ...]:
        return tuple(sorted(self.real_dates))

    @property
    def source(self) -> str:
        return self.sources.most_common(1)[0][0] if self.sources else UNRECORDED

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "sessions": self.sessions,
            "real_date": self.real_date,
            "real_span": list(self.real_span),
            "source": self.source,
            "sources": dict(self.sources),
            "provisional": self.provisional,
            # A label can cover dozens of parallel sessions; the axis only needs
            # enough to navigate to them (`--json` stays readable).
            "session_ids": self.session_ids[:3],
        }


# ---------------------------------------------------------------------------
# parsing helpers
# ---------------------------------------------------------------------------

def as_date(value: Any) -> date | None:
    """Parse ``YYYY-MM-DD`` or an ISO timestamp prefix; ``None`` otherwise."""
    if not isinstance(value, str):
        return None
    match = _DATE_SHAPE.match(value.strip())
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def id_date(record_id: Any) -> str | None:
    """The ``YYYY-MM-DD`` that a minted ID carries, or ``None``."""
    if not isinstance(record_id, str):
        return None
    match = _ID_DATE.match(record_id)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
    except ValueError:
        return None


def marker_date(text: Any) -> tuple[str, str] | None:
    """First explicit real-date marker in ``text`` as ``(date, rule_name)``."""
    if not isinstance(text, str) or not text:
        return None
    for rule_name, pattern in _REAL_MARKERS:
        found = pattern.search(text)
        if found and as_date(found.group(1)):
            return found.group(1), rule_name
    return None


def is_future(label: str, today: date) -> bool:
    """True when a label is later than today (so it cannot be a real date)."""
    parsed = as_date(label)
    return parsed is not None and parsed > today


# ---------------------------------------------------------------------------
# ledger loading (union of base + shards, as every other tool reads it)
# ---------------------------------------------------------------------------

def _load(collection: str, id_key: str, root: Path = ROOT) -> dict[str, dict[str, Any]]:
    path = Path(root) / "state" / f"{collection}.jsonl"
    if not path.exists() and not ledger_io.shard_dir(path).is_dir():
        return {}
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=Path(root))
    if errors:
        raise ValueError("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return records


def load_sessions(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return _load("sessions", "session_id", root)


def load_notes(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return _load("notes", "note_id", root)


# ---------------------------------------------------------------------------
# the axis
# ---------------------------------------------------------------------------

def curated_real_dates(notes: dict[str, dict[str, Any]]) -> dict[str, str]:
    """``report_session_id`` -> real date, from curated ``notes`` rows.

    Later rows win (notes is append-only and overlaid in ledger order), which is
    the same rule ``tools/note_index.build_view`` uses for every other curated
    field.
    """
    out: dict[str, str] = {}
    for note_id in notes:  # ledger order
        row = notes[note_id]
        subject = row.get("report_session_id") or row.get("session_id")
        value = row.get("date_real")
        if isinstance(subject, str) and isinstance(value, str) and as_date(value):
            out[subject] = value
    return out


def session_real_date(
    session_id: str,
    session: dict[str, Any],
    *,
    curated: dict[str, str] | None = None,
    today: date | None = None,
) -> tuple[str | None, str]:
    """Best recorded real date for one session, with the rule that produced it."""
    today = today or date.today()
    curated = curated or {}

    if session_id in curated:
        return curated[session_id], "notes.date_real"

    for field_name in ("notes", "human_direction"):
        found = marker_date(session.get(field_name))
        if found:
            return found[0], f"sessions.{field_name}:{found[1]}"

    started = session.get("started_at")
    parsed = as_date(started)
    if parsed is not None and parsed <= today:
        return parsed.isoformat(), "started_at"

    return None, UNRECORDED


def build_axis(
    sessions: dict[str, dict[str, Any]] | None = None,
    notes: dict[str, dict[str, Any]] | None = None,
    *,
    root: Path = ROOT,
    today: date | None = None,
) -> list[AxisRow]:
    """One :class:`AxisRow` per internal label, in real-date order."""
    today = today or date.today()
    sessions = load_sessions(root) if sessions is None else sessions
    notes = load_notes(root) if notes is None else notes
    curated = curated_real_dates(notes)

    rows: dict[str, AxisRow] = {}
    for session_id, session in sessions.items():
        label = str(session.get("started_at") or UNRECORDED)
        row = rows.setdefault(label, AxisRow(label=label))
        row.sessions += 1
        row.session_ids.append(session_id)
        real, source = session_real_date(session_id, session, curated=curated, today=today)
        if real:
            row.real_dates[real] += 1
        row.sources[source] += 1
        if is_future(label, today):
            row.provisional = True

    return sorted(rows.values(), key=lambda row: sort_key(row, today))


def sort_key(row: AxisRow, today: date | None = None) -> tuple:
    """Order: dated rows by real date, then undated rows by label.

    ``provisional`` does not come first: a label that ran ahead of the real date
    still happened (its real date is often recorded elsewhere), so it sorts by
    that date like every other row. Only rows with **no** recorded real date are
    pushed to the end, where their label is the only ordering left.
    """
    real = row.real_date
    if real:
        return (0, real, row.label)
    return (1, row.label, row.label)


def axis_sort_key(label: str, axis: Iterable[AxisRow] | None = None) -> tuple:
    """Sort key for a raw label, using an already-built axis when available."""
    for row in axis or ():
        if row.label == label:
            return sort_key(row)
    return (1, label, label)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def summary(rows: list[AxisRow]) -> dict[str, Any]:
    total = sum(row.sessions for row in rows)
    dated = sum(row.sessions for row in rows if row.real_date)
    provisional = sum(row.sessions for row in rows if row.provisional)
    sources = Counter()
    for row in rows:
        for name, count in row.sources.items():
            sources[name] += count
    real_days = {d for row in rows for d in row.real_dates}
    return {
        "labels": len(rows),
        "sessions": total,
        "sessions_with_real_date": dated,
        "sessions_without_real_date": total - dated,
        "sessions_with_future_label": provisional,
        "distinct_real_days": len(real_days),
        "real_day_span": [min(real_days), max(real_days)] if real_days else [],
        "sources": dict(sources.most_common()),
        "ambiguous_labels": [row.label for row in rows if len(row.real_span) > 1],
        "undated_labels": [row.label for row in rows if not row.real_date],
    }


def render(rows: list[AxisRow], *, limit_days: int | None = None) -> str:
    """Human-readable axis: real date first, label second, source last."""
    stats = summary(rows)
    out: list[str] = []
    out.append("=== date axis (real date ← internal label) ===")
    out.append(
        f"  labels {stats['labels']} ／ sessions {stats['sessions']} ／ "
        f"実日付あり {stats['sessions_with_real_date']} ／ 未記録 {stats['sessions_without_real_date']} ／ "
        f"未来ラベル {stats['sessions_with_future_label']}"
    )
    if stats["real_day_span"]:
        out.append(
            f"  実日付の範囲: {stats['real_day_span'][0]} 〜 {stats['real_day_span'][1]}"
        )
    out.append(f"  出所: {stats['sources']}")
    out.append("")
    for row in rows:
        span = row.real_span
        if row.real_date:
            when = row.real_date
        elif span:
            when = "/".join(span) + "（不一致）"
        else:
            when = UNRECORDED
        flag = " [未来ラベル]" if row.provisional else ""
        out.append(
            f"  {when:<12} ← {row.label:<12} {row.sessions:>2} session(s)  "
            f"({row.source}){flag}"
        )
    if stats["ambiguous_labels"]:
        out.append("")
        out.append(
            "  註: 同じラベルに複数の実日付があるもの（並列セッション）: "
            + ", ".join(stats["ambiguous_labels"][:12])
        )
    if stats["undated_labels"]:
        out.append(
            "  註: 実日付が未記録のラベルは補間しない（穴のある軸のまま並べる）: "
            + ", ".join(stats["undated_labels"][:12])
        )
    return "\n".join(out)


def check(rows: list[AxisRow], *, today: date | None = None) -> int:
    """Report, as an observation, how many labels do not equal their real date."""
    today = today or date.today()
    mismatched = [
        row for row in rows
        if row.real_date and row.real_date != row.label
    ]
    future = [row for row in rows if row.provisional]
    print("=== date axis check（合否ではなく、軸のずれの観察） ===")
    print(f"  ラベル総数 {len(rows)} ／ 実日付と一致 {len(rows) - len(mismatched)} ／ 不一致 {len(mismatched)}")
    print(f"  今日より未来のラベル {len(future)}")
    if future:
        print(f"  未来ラベルの範囲: {min(r.label for r in future)} 〜 {max(r.label for r in future)}")
    undated = [row for row in rows if not row.real_date]
    print(f"  実日付未記録のラベル {len(undated)}")
    print(
        "  註: 過去のラベルは書き換えません。新しい記録は tools/new_id.py が今日の実日付で採番します。"
    )
    return 0


# ---------------------------------------------------------------------------
# write-side rule
# ---------------------------------------------------------------------------

class FutureDateError(ValueError):
    """Raised when a caller tries to mint an ID or shard in the future."""


def assert_writable_day(day: str, *, today: date | None = None) -> str:
    """Reject a mint day later than today.

    The ID prefix is the field the axis reads first, so it must be a real date.
    Passing tomorrow's date (or an internal label such as ``20270223``) would
    put a new row outside the axis it is supposed to join. Rejecting it here is
    cheaper than explaining a future-dated row later.
    """
    today = today or date.today()
    parsed = as_date(day if "-" in day else f"{day[:4]}-{day[4:6]}-{day[6:8]}")
    if parsed is None:
        raise ValueError(f"day must be YYYY-MM-DD or YYYYMMDD, got {day!r}")
    if parsed > today:
        raise FutureDateError(
            f"{parsed.isoformat()} is later than today ({today.isoformat()}); "
            "ID prefixes carry the real date, not an internal chronology label "
            "(see tools/date_axis.py)"
        )
    return parsed.isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="One ordered time axis for the archive (labels are not rewritten)."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--anomalies", action="store_true", help="only rows whose label differs from the real date")
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD) for testing")
    args = parser.parse_args(argv)

    today = as_date(args.today) if args.today else date.today()
    try:
        rows = build_axis(root=args.root, today=today)
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.anomalies:
        rows = [
            row for row in rows
            if row.provisional or (row.real_date and row.real_date != row.label)
        ]
    if args.json:
        print(json.dumps(
            {"summary": summary(rows), "rows": [row.to_dict() for row in rows]},
            ensure_ascii=False,
            indent=1,
        ))
        return check(rows, today=today) if not args.json else 0
    print(render(rows))
    print()
    check(rows, today=today)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
