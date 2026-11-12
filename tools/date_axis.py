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
  3. the header line of the ``readings/`` report the session wrote
     (``**セッション**：`SESSION-...`（実日付 `2026-11-05`）``). A report is the
     episode itself, so its own header outranks the session's free-text notes;
  4. ``started_at`` itself, *only when it is already a real date* — i.e. a
     calendar-shaped value that is not later than today. This is what makes the
     2026-10-22..11-05 block readable without any curation at all;
  5. otherwise: ``未記録``.

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
_EXECUTION_DATE = re.compile(
    r"実行環境[^0-9]{0,14}?日付[^0-9]{0,14}?(\d{4}-\d{2}-\d{2})"
)

_REAL_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("実日付", re.compile(r"実日付[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実作業日", re.compile(r"実作業日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実UTC日付", re.compile(r"実UTC日付[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実行日", re.compile(r"実行日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    ("実環境日", re.compile(r"実環境日[^0-9]{0,12}`?(\d{4}-\d{2}-\d{2})")),
    # ``実行環境の UTC 日付は 2026-10-26`` -- the archive's own phrase for *the
    # date the machine reported*.  It is the real date even when the header above
    # it carries an internal label, so it is the one marker that is allowed to
    # outrank a header 日付 line.  See ``_EXECUTION_DATE`` and the rule in
    # :func:`session_real_date`.
    ("実行環境日付", _EXECUTION_DATE),
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


def header_marker_date(text: Any) -> tuple[str, str] | None:
    """Like :func:`marker_date`, but never returns the execution-date marker.

    The header states the report's *own* date; ``実行環境の UTC 日付`` is a
    statement about the machine and is read separately (and labelled separately)
    by :func:`report_body_dates`.  Keeping them apart is what stops a header that
    carries an internal label from being read as a real date.
    """
    if not isinstance(text, str) or not text:
        return None
    for rule_name, pattern in _REAL_MARKERS:
        if rule_name == "実行環境日付":
            continue
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


#: The first kilobytes of a report are its header: title, session, mode, date.
#: Reading more than the header would make this a report reader rather than an
#: axis, and would put the axis at the mercy of prose written months later.
_HEADER_BYTES = 4096
_HEADER_LINES = 40


def report_header_dates(root: Path = ROOT) -> dict[str, str]:
    """``session_id -> real date`` read from the **header block** of ``readings/``.

    The header block is what a report says about itself before its first
    horizontal rule (and never more than :data:`_HEADER_LINES` lines).  Two
    shapes exist in the archive and both are accepted:

        **セッション**：`SESSION-20261028-3a4b2d`
        **実行日**：2026-10-28（UTC …）

        **セッション**：`SESSION-20261105-1c1074`（実日付 `2026-11-05`）

    A header that states no real-date marker gives its session nothing -- in
    particular a header whose 日付 line carries the **internal label** and
    mentions the machine's date only as ``実行環境の UTC 日付`` is not read here;
    that case falls through to :func:`report_body_dates`, which reads it and
    labels it as coming from the body.
    """
    out: dict[str, str] = {}
    readings = Path(root) / "readings"
    if not readings.is_dir():
        return out
    for path in sorted(readings.glob("*.md")):
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                head = handle.read(_HEADER_BYTES)
        except OSError:
            continue
        session_ids = _header_session_ids(head)
        if not session_ids:
            continue
        real: str | None = None
        for index, line in enumerate(head.splitlines()):
            if index >= _HEADER_LINES or line.strip() == "---":
                break
            found = header_marker_date(line)
            if found:
                real = found[0]
                break
        if real:
            out.setdefault(session_ids[0], real)
    return out


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


def _is_readable_date(value: Any, today: date) -> bool:
    """True when ``value`` may be read as a real date.

    A calendar-shaped value **later than today** is never one.  This is the
    single rule that separates a label from a date, and it holds for every
    source -- not only for ``started_at``.  Until 2026-11-07 the rule was
    applied only to ``started_at``, so one row (``SESSION-20261027-8bf49b``)
    was read as having a real date of ``2026-11-28``: the notes said
    ``…2026-11-28は…実行日ではない``, and the marker regex walked across the
    ``、`` to attach the marker to the *label* the sentence was denying.
    The archive's own docstring stated the rule for one field; it is a
    property of the reading, so it is applied here to all of them.  A value
    that fails this test falls through to the next source rather than being
    returned, and a marker whose number is not readable is not used at all.
    """
    parsed = as_date(value)
    return parsed is not None and parsed <= today


def session_real_date(
    session_id: str,
    session: dict[str, Any],
    *,
    curated: dict[str, str] | None = None,
    header: dict[str, str] | None = None,
    body: dict[str, dict[str, str]] | None = None,
    today: date | None = None,
) -> tuple[str | None, str]:
    """Best recorded real date for one session, with the rule that produced it.

    Every rule below passes its value through :func:`_is_readable_date`.  A
    source that names a date later than today is skipped, not trusted: the
    archive's forward-running labels are exactly what this axis exists to stop
    reading as dates.
    """
    today = today or date.today()
    curated = curated or {}
    header = header or {}
    body = body or {}

    if _is_readable_date(curated.get(session_id), today):
        return curated[session_id], "notes.date_real"

    # A session that says "the execution environment's date was X" has stated the
    # real date in as many words, and that statement outranks any header: the
    # header of a report written during the era of internal labels carries the
    # *label* on its 日付 line, and labels are exactly what must not be read as
    # dates.  This marker is also why 26 sessions stopped reading as 未記録.
    for field_name in ("notes", "human_direction"):
        found = _EXECUTION_DATE.search(session.get(field_name) or "")
        if found and _is_readable_date(found.group(1), today):
            return found.group(1), f"sessions.{field_name}:実行環境日付"

    for field_name in ("notes", "human_direction"):
        found = marker_date(session.get(field_name))
        if found and _is_readable_date(found[0], today):
            return found[0], f"sessions.{field_name}:{found[1]}"

    if _is_readable_date(header.get(session_id), today):
        return header[session_id], "readings.header"

    if session_id in body:
        for rule_name, value in body[session_id].items():
            if _is_readable_date(value, today):
                return value, rule_name

    started = session.get("started_at")
    if _is_readable_date(started, today):
        return as_date(started).isoformat(), "started_at"

    return None, UNRECORDED


BODY_MARKERS = ("実行環境日付",)


def report_body_dates(root: Path = ROOT) -> dict[str, dict[str, str]]:
    """``session_id -> {rule_name: date}`` for execution-date markers in the body.

    The header is read first, so this only adds what the header could not answer.
    In the internal-label era a report's header carries the *label* on its 日付
    line while the machine's date is mentioned further down as
    ``実行環境の UTC 日付は 2026-10-26``.  Of the markers that appear in bodies,
    only that one is trusted: it is a statement about the execution environment,
    not about the session's own place in the chronology -- which is exactly the
    distinction this axis exists to keep.

    The session is taken from the same header block as
    :func:`report_header_dates` (a ``セッション`` line, else the first ID in the
    header), never from the body, so a report that cites other sessions cannot
    hand its execution date to them.
    """
    out: dict[str, dict[str, str]] = {}
    readings = Path(root) / "readings"
    if not readings.is_dir():
        return out
    pattern = re.compile(
        r"実行環境[^0-9\n]{0,28}?日付[^0-9\n]{0,14}?(\d{4}-\d{2}-\d{2})"
    )
    for path in sorted(readings.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "実行環境" not in text:
            continue
        session_ids = _header_session_ids(text)
        found = pattern.search(text)
        if not session_ids or not found or not as_date(found.group(1)):
            continue
        out.setdefault(session_ids[0], {})["readings.body:実行環境日付"] = found.group(1)
    return out


def _header_session_ids(text: str) -> list[str]:
    """Session IDs named in a report's header block (``セッション`` line first)."""
    lines = text[:_HEADER_BYTES].splitlines()[:_HEADER_LINES]
    fallback: list[str] = []
    for line in lines:
        if line.strip() == "---":
            break
        ids = re.findall(r"SESSION-\d{8}-[0-9a-z]+", line)
        if not ids:
            continue
        if not fallback:
            fallback = ids
        if "セッション" in line:
            return ids
    return fallback


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
    header = report_header_dates(root)
    body = report_body_dates(root)

    rows: dict[str, AxisRow] = {}
    for session_id, session in sessions.items():
        label = str(session.get("started_at") or UNRECORDED)
        row = rows.setdefault(label, AxisRow(label=label))
        row.sessions += 1
        row.session_ids.append(session_id)
        real, source = session_real_date(
            session_id, session, curated=curated, header=header, body=body, today=today
        )
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
    # Counted **per session**, not per label.  A label that covers several real
    # dates (2026-12-31 spans 2026-10-30 and 10-31) used to send all of its
    # sessions into "未記録", which conflated "no date recorded" with "several
    # dates recorded on one label" -- two different holes (docs/time-axis.md §3).
    unrecorded = sum(row.sources.get(UNRECORDED, 0) for row in rows)
    dated = total - unrecorded
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
        "sessions_without_real_date": unrecorded,
        "sessions_with_future_label": provisional,
        "distinct_real_days": len(real_days),
        "real_day_span": [min(real_days), max(real_days)] if real_days else [],
        "sources": dict(sources.most_common()),
        "ambiguous_labels": [row.label for row in rows if len(row.real_span) > 1],
        "undated_labels": [row.label for row in rows if not row.real_date],
    }


def render(rows: list[AxisRow], *, limit_days: int | None = None, filtered: str | None = None) -> str:
    """Human-readable axis: real date first, label second, source last.

    ``filtered`` names the subset when the caller has already dropped rows.
    The header line is otherwise identical for a filtered view and for the
    whole axis, which is how ``--anomalies`` came to print ``sessions 242``
    under a line a reader takes for the archive total (517).  The axis never
    fails on drift, so this is the only place the difference can be said.
    """
    stats = summary(rows)
    out: list[str] = []
    out.append("=== date axis (real date ← internal label) ===")
    if filtered:
        out.append(f"  ※ 絞り込み表示: {filtered}（下の件数は部分集合であって台帳全体ではない）")
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


def check(rows: list[AxisRow], *, today: date | None = None, filtered: str | None = None) -> int:
    """Report, as an observation, how many labels do not equal their real date."""
    today = today or date.today()
    mismatched = [
        row for row in rows
        if row.real_date and row.real_date != row.label
    ]
    future = [row for row in rows if row.provisional]
    print("=== date axis check（合否ではなく、軸のずれの観察） ===")
    if filtered:
        print(f"  ※ 絞り込み表示: {filtered}（以下の数は部分集合のもので、台帳全体の値ではない）")
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


def forward_dated_shards(root: Path = ROOT, *, today: date | None = None) -> list[str]:
    """Return repo-relative paths of any state/*.d/*.jsonl shard whose date prefix exceeds today."""
    today = today or date.today()
    state_dir = Path(root) / "state"
    if not state_dir.is_dir():
        return []
    offenders: list[str] = []
    for shard in sorted(state_dir.glob("*.d/*.jsonl")):
        parsed = as_date(shard.name[:10])
        if parsed is not None and parsed > today:
            offenders.append(shard.relative_to(Path(root)).as_posix())
    return offenders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="One ordered time axis for the archive (labels are not rewritten)."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--anomalies", action="store_true", help="only rows whose label differs from the real date")
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD) for testing")
    parser.add_argument(
        "--check",
        action="store_true",
        help="print only the observation block (for CI); still never fails on drift",
    )
    parser.add_argument(
        "--enforce-shards",
        action="store_true",
        help="fail (exit 1) if any state/*.d/*.jsonl shard filename carries a future date prefix",
    )
    args = parser.parse_args(argv)

    today = as_date(args.today) if args.today else date.today()
    if args.enforce_shards:
        offenders = forward_dated_shards(args.root, today=today)
        if offenders:
            print(f"FAIL: {len(offenders)} forward-dated shard(s) exceed {today.isoformat()}:", file=sys.stderr)
            for rel in offenders:
                print(f"  - {rel}", file=sys.stderr)
            return 1
        print(f"PASS: 0 forward-dated shards in state/*.d/ (today={today.isoformat()})")
        if not args.check and not args.json and not args.anomalies:
            return 0
    try:
        rows = build_axis(root=args.root, today=today)
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        return check(rows, today=today)

    filtered_label = None
    if args.anomalies:
        rows = [
            row for row in rows
            if row.provisional or (row.real_date and row.real_date != row.label)
        ]
        filtered_label = "ラベルと実日付が一致しない行のみ（--anomalies）"
    if args.json:
        print(json.dumps(
            {"summary": summary(rows), "rows": [row.to_dict() for row in rows]},
            ensure_ascii=False,
            indent=1,
        ))
        return check(rows, today=today) if not args.json else 0
    print(render(rows, filtered=filtered_label))
    print()
    check(rows, today=today, filtered=filtered_label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
