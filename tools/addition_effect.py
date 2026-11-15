#!/usr/bin/env python3
"""Did an addition produce classification, or only more rows? (stdlib only)

The worry behind P2/P3 of readings/2026-11-15-where-the-learning-actually-happens.md
is that 整備 (tidying) quietly replaces 探究 (inquiry): the archive keeps producing
tables, criteria, and adjudications while the readings that could falsify them
thin out.  This tool makes that comparison with two countable rows:

  * classification-shaped claims — a ``notes.claims`` row whose text names a
    classification act (分類・類型・判定・基準・カテゴリ・仕分け・区分け);
  * adjudication rows — ``errata`` plus ``editorial_decisions``;
  * handwritten reads — ``read_log`` rows where a session actually read
    something, excluding the mechanical ``used_as_context`` backfill.

Grouped in fixed-width cohorts (default 7 days), that gives "classification per
read" before and after an addition.  It is a description, not a score: a rising
share can mean the archive is learning to sort, or that it has stopped reading.

Usage:
  python3 tools/addition_effect.py
  python3 tools/addition_effect.py --since 2026-11-01 --cohort 7
  python3 tools/addition_effect.py --json
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_WORDS = re.compile(
    r"分類|類型|判定|基準|カテゴリ|仕分け|区分け|クラスタ"
)
MECHANICAL_NOTE = "機械的バックフィル"


def _day(record: dict[str, Any]) -> str | None:
    """Return YYYY-MM-DD from created_at (ISO or compact), or None."""
    raw = record.get("created_at") or ""
    text = str(raw)
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", text) or re.match(r"^(\d{4})(\d{2})(\d{2})$", text)
    if not match:
        return None
    try:
        return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
    except ValueError:
        return None


def cohort_of(day: str, days: int = 7) -> str:
    """The first day of the fixed-width cohort that ``day`` falls in."""
    date = datetime.date.fromisoformat(day)
    if days <= 0:
        return date.isoformat()
    ordinal = date.toordinal()
    start = ordinal - (ordinal % days)
    return datetime.date.fromordinal(start).isoformat()


def _load(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    state = Path(root) / "state"
    specs = {
        "notes": (state / "notes.jsonl", "note_id"),
        "read_log": (state / "read_log.jsonl", "read_id"),
        "errata": (state / "errata.jsonl", "errata_id"),
        "editorial_decisions": (state / "editorial_decisions.jsonl", "decision_id"),
    }
    existing = {name: spec for name, spec in specs.items() if spec[0].exists()}
    collections, errors = ledger_io.load_collections(existing, root=Path(root))
    if errors:
        raise SystemExit("ledger unreadable: " + "; ".join(errors[:3]))
    return collections


def _in_range(day: str | None, since: str | None) -> bool:
    return bool(day) and (since is None or day >= since)


def build_effect_report(
    *,
    root: Path = ROOT,
    since: str | None = None,
    cohort_days: int = 7,
    limit: int = 5,
) -> dict[str, Any]:
    collections = _load(root)
    buckets: dict[str, dict[str, Any]] = {}

    def bump(day: str, field: str, amount: int = 1) -> None:
        key = cohort_of(day, cohort_days)
        row = buckets.setdefault(
            key,
            {"cohort": key, "claims": 0, "classification_claims": 0,
             "adjudication_rows": 0, "handwritten_reads": 0},
        )
        row[field] += amount

    examples: list[dict[str, Any]] = []
    for note_id, note in collections.get("notes", {}).items():
        day = _day(note)
        if not _in_range(day, since):
            continue
        claims = note.get("claims")
        if not isinstance(claims, list):
            continue
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            bump(day, "claims")
            text = claim.get("text") or ""
            if CLASSIFICATION_WORDS.search(text):
                bump(day, "classification_claims")
                if len(examples) < limit:
                    examples.append({
                        "cohort": cohort_of(day, cohort_days),
                        "note_id": note_id,
                        "claim_id": claim.get("claim_id"),
                        "kind": claim.get("kind"),
                        "text": text[:120],
                    })

    for name in ("errata", "editorial_decisions"):
        for _record_id, record in collections.get(name, {}).items():
            day = _day(record)
            if _in_range(day, since):
                bump(day, "adjudication_rows")

    for _read_id, record in collections.get("read_log", {}).items():
        day = _day(record)
        if not _in_range(day, since):
            continue
        if record.get("reading") == "used_as_context" or MECHANICAL_NOTE in str(record.get("note") or ""):
            continue
        bump(day, "handwritten_reads")

    cohorts = [buckets[key] for key in sorted(buckets)]
    for row in cohorts:
        reads = row["handwritten_reads"]
        row["classification_share"] = round(row["classification_claims"] / row["claims"], 4) if row["claims"] else 0.0
        row["per_read"] = round(row["classification_claims"] / reads, 3) if reads else None

    totals = {
        "claims": sum(row["claims"] for row in cohorts),
        "classification_claims": sum(row["classification_claims"] for row in cohorts),
        "adjudication_rows": sum(row["adjudication_rows"] for row in cohorts),
        "handwritten_reads": sum(row["handwritten_reads"] for row in cohorts),
    }
    totals["classification_share"] = (
        round(totals["classification_claims"] / totals["claims"], 4) if totals["claims"] else 0.0
    )
    totals["per_read"] = (
        round(totals["classification_claims"] / totals["handwritten_reads"], 3)
        if totals["handwritten_reads"] else None
    )

    return {
        "since": since,
        "cohort_days": cohort_days,
        "cohorts": cohorts,
        "totals": totals,
        "examples": examples,
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "=== addition effect: classification per handwritten read ===",
        f"cohort width: {report['cohort_days']}日 / since: {report['since'] or '(all)'}",
        "",
        f"{'cohort':<12}{'claims':>8}{'分類語':>8}{'判定行':>8}{'手書き読':>10}{'分類語割合':>12}{'読書あたり':>12}",
    ]
    for row in report["cohorts"]:
        per_read = "—" if row["per_read"] is None else f"{row['per_read']:.2f}"
        lines.append(
            f"{row['cohort']:<12}{row['claims']:>8}{row['classification_claims']:>8}"
            f"{row['adjudication_rows']:>8}{row['handwritten_reads']:>10}"
            f"{row['classification_share']*100:>11.1f}%{per_read:>12}"
        )
    totals = report["totals"]
    per_read = "—" if totals["per_read"] is None else f"{totals['per_read']:.2f}"
    lines.extend([
        "",
        f"total: claims {totals['claims']} / 分類語 {totals['classification_claims']} "
        f"({totals['classification_share']*100:.1f}%) / 判定行 {totals['adjudication_rows']} / "
        f"手書き読書 {totals['handwritten_reads']} / 読書あたり {per_read}",
    ])
    if report["examples"]:
        lines.append("")
        lines.append("分類語を含む claim の例:")
        for row in report["examples"]:
            lines.append(f"  - {row['cohort']} `{row['note_id']}` / `{row['claim_id']}` {row['text']}")
    lines.extend([
        "",
        "この比は達成目標でも品質判定でもありません。追加の前後で同じ表を出し、**どちらが増えたか**を"
        "記録するための観測です（読書を減らして分類を増やすことは、探究の進展ではありません）。",
        "`2027-…` の cohort は、旧い行の内部編年ラベルを含みます（実日付ではありません。`docs/time-axis.md`）。",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", help="only rows created on or after this YYYY-MM-DD")
    parser.add_argument("--cohort", type=int, default=7, help="cohort width in days")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    report = build_effect_report(
        root=args.root, since=args.since, cohort_days=args.cohort, limit=max(args.limit, 0)
    )
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
