#!/usr/bin/env python3
"""Measure whether later sessions actually read earlier reports (stdlib only).

Why this tool exists
--------------------
``docs/memory-architecture.md`` diagnosed the archive's one structural gap: it
holds an unusually thick semantic and procedural memory, a large episodic memory,
and almost no *path back into the episodes*. Two reports measured that gap by
hand and wrote the number into their own text:

  * ``readings/2027-02-21-the-reservation-that-did-not-become-a-mystery.md``
    — "2027-02-16 報告クラスタを対象とする read_log は9,191行中2行のみで、両方とも自セッション"
  * ``readings/2027-02-22-counting-the-stock-without-a-new-column.md``
    — "前回報告クラスタへの後続読みは9,238行中2行のみで、両方とも前回セッション自身"

Both numbers were produced by a scratch script that no longer exists, so they
cannot be re-run as the corpus grows. This module makes the measurement a
fixture of the toolset instead:

  * **inherited** — a ``read_log`` row whose ``target.type`` is ``note`` and
    whose reading session *differs from* the session that recorded the note row.
    That is the only row shape that proves a report was read by someone other
    than its author: prose citations, hops through ``inspect_inquiry --packet``
    and the README window are all invisible to the ledger.
  * **self-read** — the same session reading its own report. Counted, but never
    counted as inheritance (an author re-reading a draft is not a successor).
  * **prose-cited** — a later report links or names the path. Wider than the
    ledger (it leaves no row), so it is reported separately and never added to
    the inherited count. Mixing them would let a citation inflate a number that
    is supposed to mean "a later session could find this again".

Nothing here is a gate. A report with zero successors is *unmeasured*, not
unread: the ledger only sees readers who chose to log the reading. The output
says which of those two it is.

Usage::

    python3 tools/inheritance.py                     # summary + recent cohorts
    python3 tools/inheritance.py --cohorts           # per-session-block table
    python3 tools/inheritance.py --unread 20         # reports nobody logged
    python3 tools/inheritance.py --json
    python3 tools/inheritance.py --until 2026-11-05  # cutoff for report age
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import date_axis  # noqa: E402
import ledger_io  # noqa: E402
import note_index  # noqa: E402

#: A cohort is one calendar block on the real axis. Six days is the width the
#: archive's own "数十回" spans used (2027-02-16..02-21, 2027-02-19..02-23), and
#: it keeps each block large enough that a single successor is visible as a rate
#: rather than as an anecdote.
DEFAULT_COHORT_DAYS = 6


@dataclass
class ReportRow:
    """One file in ``readings/`` and what the ledger says about its readers."""

    path: str
    session_ids: list[str]
    real_date: str | None
    label: str | None
    chars: int
    note_ids: list[str]
    note_sessions: list[str] = None  # type: ignore[assignment]
    self_reads: int = 0
    inherited_rows: list[dict[str, Any]] = None  # type: ignore[assignment]
    prose_cited_by: list[str] = None  # type: ignore[assignment]
    outbound: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.note_sessions = self.note_sessions or []
        self.inherited_rows = self.inherited_rows or []
        self.prose_cited_by = self.prose_cited_by or []
        self.outbound = self.outbound or []

    @property
    def author_sessions(self) -> set[str]:
        """Sessions that may legitimately have written this report.

        Two sources, because neither alone is reliable: the ``SESSION-`` IDs the
        report body cites (harvested), and the sessions recorded on its ``notes``
        rows (curated).  A report that cites no session ID still has an author,
        and treating it as authorless would score its own re-reading as a
        successor.
        """
        return {s for s in [*self.session_ids, *self.note_sessions] if s}

    @property
    def inherited(self) -> int:
        return len(self.inherited_rows)

    @property
    def successor_sessions(self) -> list[str]:
        return sorted({row["session_id"] for row in self.inherited_rows})


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def _load(collection: str, id_key: str, root: Path) -> dict[str, dict[str, Any]]:
    path = Path(root) / "state" / f"{collection}.jsonl"
    if not path.exists() and not ledger_io.shard_dir(path).is_dir():
        return {}
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=Path(root))
    if errors:
        raise ValueError("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return records


def load_read_log(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return _load("read_log", "read_id", root)


def note_paths(notes: dict[str, dict[str, Any]]) -> dict[str, str]:
    """``note_id`` -> report path, for resolving ``target.type == 'note'``."""
    return {
        note_id: row["path"]
        for note_id, row in notes.items()
        if isinstance(row.get("path"), str)
    }


def collect(
    root: Path = ROOT,
    *,
    until: str | None = None,
) -> tuple[list[ReportRow], dict[str, Any]]:
    """Join ``readings/`` with ``notes`` and ``read_log`` into one row per report."""
    root = Path(root)
    data = note_index._load_ledgers(root)  # noqa: SLF001 - same private loader note_index uses
    view = note_index.build_view(root, data)
    notes = data.get("notes", {})
    by_note = note_paths(notes)
    read_log = load_read_log(root)

    reports: dict[str, ReportRow] = {}
    for rel, entry in view.items():
        reports[rel] = ReportRow(
            path=rel,
            session_ids=list(entry.get("session_ids") or []),
            real_date=entry.get("date_real"),
            label=entry.get("date_label"),
            chars=int(entry.get("chars") or 0),
            note_ids=list(entry.get("note_ids") or []),
            note_sessions=sorted(
                {
                    row.get("report_session_id") or row.get("session_id")
                    for row in notes.values()
                    if row.get("path") == rel
                    and isinstance(row.get("report_session_id") or row.get("session_id"), str)
                }
            ),
            outbound=sorted(entry.get("outbound_notes") or []),
            prose_cited_by=sorted(
                {source for source in (entry.get("inbound") or []) if source.startswith("readings/")}
            ),
        )

    name_by_path = {rel: Path(rel).name for rel in reports}
    path_by_name = {name: rel for rel, name in name_by_path.items()}

    stats: Counter = Counter()
    for read_id, row in read_log.items():
        target = row.get("target") or {}
        if not isinstance(target, dict):
            continue
        if target.get("type") == "note":
            rel = by_note.get(target.get("id"))
        elif target.get("type") == "session":
            # Reading a *session row* is not reading the *report* that session
            # wrote: the row is a compact record, the report is the episode.
            # Counted apart so it can never inflate the inherited number.
            stats["session_target_rows"] += 1
            continue
        else:
            continue
        stats["read_rows"] += 1
        if rel is None or rel not in reports:
            stats["unresolved_rows"] += 1
            continue
        report = reports[rel]
        reading_session = row.get("session_id")
        if reading_session and reading_session in report.author_sessions:
            report.self_reads += 1
            stats["self_rows"] += 1
            continue
        report.inherited_rows.append(
            {
                "read_id": read_id,
                "session_id": reading_session,
                "reading": row.get("reading"),
                "created_at": row.get("created_at"),
                "note": row.get("note"),
            }
        )
        stats["inherited_rows"] += 1

    # prose citations are a wider net; resolve them to report paths
    for rel, report in reports.items():
        cited: list[str] = []
        for source in report.prose_cited_by:
            resolved = path_by_name.get(Path(source).name, source)
            if resolved in reports:
                cited.append(resolved)
        report.prose_cited_by = sorted(set(cited))
        stats["prose_edges"] += len(report.prose_cited_by)

    rows = list(reports.values())
    if until:
        rows = [
            row for row in rows
            if (row.real_date or "") and row.real_date <= until
        ] or rows
    return rows, {
        "read_rows": stats["read_rows"],
        "self_rows": stats["self_rows"],
        "inherited_rows": stats["inherited_rows"],
        "unresolved_rows": stats["unresolved_rows"],
        "session_target_rows": stats["session_target_rows"],
        "prose_edges": stats["prose_edges"],
        "reports": len(rows),
        "notes_rows": len(notes),
        "read_log_rows": len(read_log),
    }


# ---------------------------------------------------------------------------
# cohorts
# ---------------------------------------------------------------------------

def cohort_key(real_date: str | None, *, width: int = DEFAULT_COHORT_DAYS) -> str:
    """Name a cohort by the block of real days it falls in.

    Blocks are anchored at 2026-10-22 (the first real date on the axis) rather
    than at month boundaries: the archive's work is not monthly, and anchoring
    makes the label reproducible from any row instead of from the calendar.
    """
    parsed = date_axis.as_date(real_date or "")
    if parsed is None:
        return "未記録"
    anchor = date(2026, 10, 22)
    index = max(0, (parsed - anchor).days // width)
    start = date.fromordinal(anchor.toordinal() + index * width)
    end = date.fromordinal(start.toordinal() + width - 1)
    return f"{start.isoformat()}..{end.isoformat()}"


def cohorts(
    rows: Iterable[ReportRow],
    *,
    width: int = DEFAULT_COHORT_DAYS,
) -> list[dict[str, Any]]:
    """Group reports into real-date blocks and count successors per block."""
    grouped: dict[str, list[ReportRow]] = defaultdict(list)
    for row in rows:
        grouped[cohort_key(row.real_date, width=width)].append(row)
    out: list[dict[str, Any]] = []
    for key in sorted(grouped):
        members = grouped[key]
        inheriting = [row for row in members if row.inherited]
        out.append(
            {
                "cohort": key,
                "reports": len(members),
                "notes_rows": sum(1 for row in members if row.note_ids),
                "unmeasurable": sum(1 for row in members if not row.note_ids),
                "chars": sum(row.chars for row in members),
                "inherited_rows": sum(row.inherited for row in members),
                "inheriting_reports": len(inheriting),
                "successor_sessions": len({s for row in members for s in row.successor_sessions}),
                "self_reads": sum(row.self_reads for row in members),
                "prose_edges": sum(len(row.prose_cited_by) for row in members),
            }
        )
    return out


def summarize(rows: list[ReportRow], totals: dict[str, Any]) -> dict[str, Any]:
    reports = len(rows)
    inheriting = [row for row in rows if row.inherited]
    prose = [row for row in rows if row.prose_cited_by]
    return {
        "reports": reports,
        "read_log_rows": totals.get("read_log_rows"),
        "note_target_rows": totals.get("read_rows"),
        "self_read_rows": totals.get("self_rows"),
        "inherited_rows": totals.get("inherited_rows"),
        "session_target_rows": totals.get("session_target_rows"),
        "inheriting_reports": len(inheriting),
        "inheriting_rate": round(len(inheriting) / reports, 4) if reports else 0.0,
        "prose_cited_reports": len(prose),
        "prose_cited_rate": round(len(prose) / reports, 4) if reports else 0.0,
        "reports_with_note_row": sum(1 for row in rows if row.note_ids),
        # The two denominators are different, and the headline rate used to hide
        # it: a report with no ``notes`` row cannot be pointed at by
        # ``read_log.target.type == "note"`` at all, so it is not "unread" --
        # it is unmeasurable.  Both numbers are reported side by side.
        "reports_without_note_row": sum(1 for row in rows if not row.note_ids),
        "inheriting_rate_of_measurable": (
            round(len(inheriting) / sum(1 for row in rows if row.note_ids), 4)
            if any(row.note_ids for row in rows)
            else 0.0
        ),
        "notes_rows": totals.get("notes_rows"),
        "successor_sessions": len({s for row in rows for s in row.successor_sessions}),
        "unmeasured_reports": reports - len(inheriting),
        "inherited_share_of_note_rows": (
            round(totals.get("inherited_rows", 0) / totals["read_rows"], 4)
            if totals.get("read_rows")
            else 0.0
        ),
    }


def render(summary: dict[str, Any], blocks: list[dict[str, Any]], *, limit: int = 12) -> str:
    out: list[str] = ["=== inheritance over readings/ (ledger-visible successors) ==="]
    out.append(
        f"  報告 {summary['reports']} 本 ／ notes 行 {summary['notes_rows']} ／ "
        f"read_log 全 {summary['read_log_rows']:,} 行"
    )
    out.append(
        f"  note を指す行 {summary['note_target_rows']} "
        f"（自セッション {summary['self_read_rows']} ／ 後続 {summary['inherited_rows']}）"
    )
    out.append(
        f"  後続に読まれた報告 {summary['inheriting_reports']} 本 "
        f"（全 {summary['reports']} 本の {summary['inheriting_rate']:.1%}）"
    )
    out.append(
        f"  継承を測れる報告 {summary['reports_with_note_row']} 本 のうち "
        f"{summary['inheriting_rate_of_measurable']:.1%} ／ "
        f"notes 行を持たず測れない報告 {summary['reports_without_note_row']} 本"
    )
    out.append(
        f"  別報告からリンクされた報告 {summary['prose_cited_reports']} 本 "
        f"（{summary['prose_cited_rate']:.1%}・台帳外なので上とは足さない）"
    )
    out.append(f"  後続セッション数 {summary['successor_sessions']}")
    out.append("")
    out.append(
        "  cohort (実日付)            reports  notes    notes0  後続行  読まれた  prose辺  自読み"
    )
    for block in blocks:
        out.append(
            f"  {block['cohort']:<24} {block['reports']:>7} {block['notes_rows']:>6} "
            f"{block['unmeasurable']:>9} {block['inherited_rows']:>7} "
            f"{block['inheriting_reports']:>9} {block['prose_edges']:>8} {block['self_reads']:>7}"
        )
    out.append("")
    out.append(
        "  註: 後続0は「読まれていない」ではなく「誰も read_log に書かなかった」。"
        "台帳は記帳した読みしか見ない。prose辺は本文リンクで、行を残さない。"
        "notes0 は notes 行を持たない報告で、note 型の read_log からは指せない＝未測定。"
        "全体の率はこの分母を含むため、継承を測れる報告だけの率を併記する。"
    )
    return "\n".join(out)


def unread(rows: list[ReportRow], *, limit: int = 20) -> list[ReportRow]:
    """Reports with no ledger-visible successor and no prose citation."""
    return [
        row for row in sorted(
            (r for r in rows if not r.inherited and not r.prose_cited_by),
            key=lambda r: (-r.chars, r.path),
        )
    ][:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--cohorts", action="store_true", help="per real-date block table")
    parser.add_argument("--unread", nargs="?", const=20, type=int, metavar="N",
                        help="list reports with no successor (default 20)")
    parser.add_argument("--width", type=int, default=DEFAULT_COHORT_DAYS, help="cohort width in days")
    parser.add_argument("--until", help="only reports with a real date <= this (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        rows, totals = collect(args.root, until=args.until)
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = summarize(rows, totals)
    blocks = cohorts(rows, width=args.width)

    if args.unread is not None:
        found = unread(rows, limit=args.unread)
        if args.json:
            print(json.dumps(
                [{"path": r.path, "chars": r.chars, "real_date": r.real_date} for r in found],
                ensure_ascii=False, indent=1,
            ))
            return 0
        print(f"=== 後続もリンクも持たない報告: {len(found)} 本（表示上限） ===")
        for row in found:
            print(f"  {row.path}  {row.chars:,}字  [実日付 {row.real_date or '未記録'}]")
        print("  註: 未測定であって未読ではない。次に読む候補として並べているだけである。")
        return 0

    if args.json:
        print(json.dumps({"summary": summary, "cohorts": blocks}, ensure_ascii=False, indent=1))
        return 0

    print(render(summary, blocks))
    if args.cohorts:
        print()
        print("=== 後続を持つ報告（台帳可視） ===")
        for row in sorted(rows, key=lambda r: (-r.inherited, r.path))[:20]:
            if not row.inherited:
                continue
            who = ", ".join(f"`{s}`" for s in row.successor_sessions)
            print(f"  {row.path}  ← {row.inherited} 行 / {who}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
