#!/usr/bin/env python3
"""Report materials that a report used but never names by ID (stdlib only).

Why this module exists
----------------------
A `read_log` row says a material was read.  A report says what was read in
prose.  These are two different records, and they can disagree: the report
``readings/2026-11-06-five-experiments-on-the-environment-that-makes-the-reader.md``
gives five materials a full four-layer reading each, cites DOI and PMID for
every one, and never writes a single `material_id`.  The rows are complete; the
naming is absent.

That gap is invisible to every existing tool.  `validate_seed.py` checks that a
reference resolves, not that a report makes one.  `read_log_backfill.py` checks
that sessions and read_log agree.  `map_build.py` indexes reports by the IDs
they contain, so a report with no IDs contributes edges to no material — the
five readings exist and are reachable from nowhere.

This tool measures three things and decides nothing:

1. **Naming convention.**  Material IDs come in two spellings, e.g.
   ``MAT-LIT-205`` and ``MAT-20261025-0b9965``.  The second contains lowercase
   hex, so a case-sensitive ``MAT-[A-Z0-9-]+`` search silently fails to match
   most of the ledger.  The report prints both counts so the difference is
   visible; the audit itself always searches case-insensitively.

2. **Named in its own report.**  For every material whose
   ``origin.source_record_path`` is a ``readings/`` file that still exists, does
   that file contain the material's own ID?

3. **Never named anywhere.**  Which materials appear in no ``readings/`` file at
   all, and of those, how many have a hand-written ``read_log`` row (i.e. were
   read but not named) versus a mechanical backfill row only.

Usage:
  python3 tools/naming_coverage.py
  python3 tools/naming_coverage.py --json
  python3 tools/naming_coverage.py --limit 20      # longer lists
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Case-insensitive on purpose.  The uppercase-only variant is offered below only
# to show how much it loses; it must never be the counting convention.
CITE_RE = re.compile(r"MAT-[A-Za-z0-9-]+")
CITE_UPPER_RE = re.compile(r"MAT-[A-Z0-9-]+")
BACKFILL_MARK = "機械的バックフィル"


def _read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def load_collection(root: Path, name: str) -> list[dict[str, Any]]:
    """Load a collection the way the other tools do: base file plus shards."""
    rows = _read_rows(root / "state" / f"{name}.jsonl")
    for shard in sorted((root / "state" / f"{name}.d").glob("*.jsonl")):
        rows.extend(_read_rows(shard))
    return rows


def load_reports(root: Path) -> dict[str, str]:
    """Return ``{relative_path: text}`` for every report under ``readings/``."""
    out: dict[str, str] = {}
    base = root / "readings"
    if not base.exists():
        return out
    for path in sorted(base.glob("*.md")):
        out[f"readings/{path.name}"] = path.read_text(encoding="utf-8")
    return out


def is_backfill(row: dict[str, Any]) -> bool:
    return BACKFILL_MARK in json.dumps(row, ensure_ascii=False)


def hand_read_ids(read_rows: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for row in read_rows:
        if is_backfill(row):
            continue
        target = row.get("target") or {}
        if target.get("type") == "material" and target.get("id"):
            ids.add(target["id"])
    return ids


def audit(root: Path) -> dict[str, Any]:
    materials = {r["material_id"]: r for r in load_collection(root, "materials")
                 if r.get("material_id")}
    reports = load_reports(root)

    full: set[str] = set()
    upper: set[str] = set()
    per_report: dict[str, set[str]] = {}
    for path, text in reports.items():
        found = set(CITE_RE.findall(text))
        per_report[path] = found
        full |= found
        upper |= set(CITE_UPPER_RE.findall(text))

    ids = set(materials)
    never = sorted(ids - full)
    hand = hand_read_ids(load_collection(root, "read_log"))

    own_total = own_named = 0
    own_missing: list[dict[str, str]] = []
    for mid, row in materials.items():
        source = (row.get("origin") or {}).get("source_record_path") or ""
        if source not in per_report:
            continue
        own_total += 1
        if mid in per_report[source]:
            own_named += 1
        else:
            own_missing.append({"material_id": mid, "report": source,
                                "title": (row.get("title") or "")[:70]})

    by_source = Counter((materials[m].get("origin") or {}).get("source_record_path") or "(none)"
                        for m in never)

    return {
        "materials": len(ids),
        "reports": len(reports),
        "cited_case_insensitive": len(ids & full),
        "cited_uppercase_only": len(ids & upper),
        "ids_uppercase_cannot_match": len(ids) - len([m for m in ids if CITE_UPPER_RE.fullmatch(m)]),
        "never_named": len(never),
        "never_named_read_but_unnamed": len([m for m in never if m in hand]),
        "own_report_total": own_total,
        "own_report_named": own_named,
        "own_report_missing": len(own_missing),
        "own_missing_top": own_missing[:50],
        "never_by_source_top": by_source.most_common(12),
        "never_ids": never,
    }


def render(result: dict[str, Any], limit: int) -> str:
    lines = ["=== naming coverage: materials used in reports vs. materials named by ID ==="]
    lines.append(
        f"  materials {result['materials']} / reports {result['reports']}")
    lines.append(
        "  ID spelling: {:d} of {:d} ids contain lowercase hex and cannot be matched "
        "by MAT-[A-Z0-9-]+".format(result["ids_uppercase_cannot_match"], result["materials"]))
    lines.append(
        f"  named by ID (case-insensitive): {result['cited_case_insensitive']} "
        f"/ uppercase-only search would find: {result['cited_uppercase_only']}")
    lines.append(
        f"  never named in any report: {result['never_named']}")
    lines.append(
        f"    of those, with a hand-written read_log row: "
        f"{result['never_named_read_but_unnamed']}  (read, not named)")
    lines.append(
        f"  named in its own source report: {result['own_report_named']}"
        f" / {result['own_report_total']}  (missing {result['own_report_missing']})")
    if result["own_missing_top"]:
        lines.append("  -- materials whose own report does not name them --")
        for item in result["own_missing_top"][:limit]:
            lines.append(f"    {item['material_id']}  {item['report']}  {item['title']}")
    if result["never_by_source_top"]:
        lines.append("  -- never-named, by origin.source_record_path --")
        for source, count in result["never_by_source_top"]:
            lines.append(f"    {count:4d}  {source}")
    lines.append("  A read_log row is a record of reading; a name in a report is a record")
    lines.append("  of what the reading was used for.  This tool counts the second only.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)

    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(render(result, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
