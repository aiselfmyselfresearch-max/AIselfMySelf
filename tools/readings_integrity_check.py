#!/usr/bin/env python3
"""Check that the archive's prose bodies exist. A gate, not a mirror.

Why this tool exists
--------------------
On 2026-11-15 an experiment truncated **all 802 `readings/*.md` files to 0
bytes** (30,180,380 B removed) and re-ran the whole gate battery: all nine
gates still PASSed, and `validate_seed`, `append_only_check`,
`BELIEF_MAP.md` and the assignment receipt were byte-identical to the
untruncated tree. Measured in
`readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md`
sections 3.4.1 and 9.3-8.

The reason is structural, not an oversight in any one check:

* `append_only_check` guards the *bytes of ledger lines* under `state/`. It
  never opens `readings/`.
* `learning_metrics`' 「readings/配線率」 counts note rows against files that
  exist, i.e. the ledger->index direction. It does not read a body.
* `referent_check` resolves ids inside `state/` paths only
  (`_collection_of` returns None for anything that does not start with
  `state/`), so a missing report file is invisible to it.
* `note_index --check` compares a generated section against note rows.

So the prose -- the part of the archive a human actually reads -- was guarded
by nothing but git history. That protection is real, but it is not a check, and
it does not fail a build. This tool makes the gap a gate: if the bodies are
gone, CI says so.

What it checks
--------------
1. ``blank_body``  - a ``readings/*.md`` file with no non-whitespace content.
2. ``no_h1``       - a ``readings/*.md`` file with no ``# `` heading. Every
                     report in the archive opens with one; a body that lost its
                     heading has usually lost more.
3. ``missing_target`` - a note row whose ``path`` points into ``readings/`` at a
                     file that is not on disk. This is the ledger->file
                     direction no other check walks.

Exit status is 1 when any of the three is non-empty, 0 otherwise.

What it deliberately does NOT check
-----------------------------------
* **Whether a body was rewritten.** Prose is edited on purpose -- sections get
  appended, errata get corrected in place. Only ``state/`` lines are
  append-only, and `append_only_check` owns that. Requiring byte preservation
  here would break legitimate revision.
* **Whether a body is true, complete, or well argued.** No instrument can check
  that, and this one does not pretend to.
* **Non-``.md`` targets.** ``readings/`` legitimately holds two data files named
  by note rows (a ``.tsv`` and a ``.json``). They are counted and reported, not
  body-checked.

A PASS from this tool means "the prose exists and has a heading". It does not
mean the prose is guarded against being *changed* -- see the report above, and
`readings/2026-11-15-the-assignment-was-run-and-then-discarded.md`.

Usage
-----
  python3 tools/readings_integrity_check.py
  python3 tools/readings_integrity_check.py --json
  python3 tools/readings_integrity_check.py --root /path/to/checkout
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402

# Only the head of each file is read: 30 MB of prose is 806 files and a body
# check does not need the tail. 64 KiB covers every report's front matter by a
# wide margin (the median file is ~30 KB, the smallest is ~2.4 KB).
HEAD_BYTES = 64 * 1024
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)


def _head(path: Path) -> str:
    """Read up to HEAD_BYTES of a file as text, tolerating undecodable tails."""
    try:
        with path.open("rb") as fh:
            raw = fh.read(HEAD_BYTES)
    except OSError:
        return ""
    return raw.decode("utf-8", errors="replace")


def audit(root: Path = ROOT) -> dict[str, Any]:
    readings = root / "readings"
    md_files = sorted(readings.glob("*.md")) if readings.is_dir() else []

    blank_body: list[dict[str, Any]] = []
    no_h1: list[dict[str, Any]] = []
    sizes: list[int] = []
    for path in md_files:
        size = path.stat().st_size
        sizes.append(size)
        head = _head(path)
        rel = str(path.relative_to(root))
        if not head.strip():
            blank_body.append({"path": rel, "size_bytes": size})
        elif not H1_RE.search(head):
            no_h1.append({"path": rel, "size_bytes": size})

    # ledger -> file: note rows naming a readings/ path
    notes_base = root / "state" / "notes.jsonl"
    notes: dict[str, Any] = {}
    if notes_base.exists() or ledger_io.shard_dir(notes_base).is_dir():
        notes = ledger_io.load_jsonl_union(notes_base, "note_id")
    missing_target: list[dict[str, Any]] = []
    named_md: set[str] = set()
    named_other: set[str] = set()
    for note_id, row in notes.items():
        path = row.get("path")
        if not isinstance(path, str) or not path.startswith("readings/"):
            continue
        if path.endswith(".md"):
            named_md.add(path)
        else:
            named_other.add(path)
        if not (root / path).is_file():
            missing_target.append({"note_id": note_id, "path": path})

    sizes.sort()
    violations = len(blank_body) + len(no_h1) + len(missing_target)
    return {
        "readings_dir_exists": readings.is_dir(),
        "md_file_count": len(md_files),
        "md_total_bytes": sum(sizes),
        "md_min_bytes": sizes[0] if sizes else 0,
        "md_median_bytes": sizes[len(sizes) // 2] if sizes else 0,
        "blank_body": blank_body,
        "no_h1": no_h1,
        "missing_target": missing_target,
        "note_rows": len(notes),
        "distinct_md_paths_named_by_notes": len(named_md),
        "distinct_non_md_paths_named_by_notes": len(named_other),
        "non_md_paths": sorted(named_other),
        "md_files_never_named_by_a_note": sorted(
            {f"readings/{p.name}" for p in md_files} - named_md
        ),
        "violation_count": violations,
        "status": "PASS" if violations == 0 else "FAIL",
    }


def render(report: dict[str, Any], limit: int = 12) -> str:
    lines: list[str] = []
    for key, label in (
        ("blank_body", "readings/*.md with no body"),
        ("no_h1", "readings/*.md with no '# ' heading"),
        ("missing_target", "note rows pointing at a readings/ file that does not exist"),
    ):
        rows = report[key]
        if rows:
            lines.append(f"FAIL: {len(rows)} {label}:")
            for row in rows[:limit]:
                detail = row.get("path", "")
                if "note_id" in row:
                    detail = f"{row['note_id']} -> {row['path']}"
                lines.append(f"  - {detail}")
            if len(rows) > limit:
                lines.append(f"  ... and {len(rows) - limit} more")
        else:
            lines.append(f"PASS: 0 {label}")
    lines.append(
        f"INFO: {report['md_file_count']} readings/*.md, "
        f"{report['md_total_bytes']:,} B total, smallest {report['md_min_bytes']:,} B, "
        f"median {report['md_median_bytes']:,} B; "
        f"{report['distinct_md_paths_named_by_notes']} named by {report['note_rows']} note rows, "
        f"{report['distinct_non_md_paths_named_by_notes']} non-.md target(s) (existence only), "
        f"{len(report['md_files_never_named_by_a_note'])} file(s) no note row names"
    )
    lines.append(
        "INFO: this gate checks that the prose EXISTS. It does not check that it is "
        "unchanged (only state/ lines are append-only) and not that it is correct."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--limit", type=int, default=12, help="violations listed per kind")
    args = parser.parse_args(argv)

    if not (args.root / "readings").is_dir():
        print(f"CANNOT CHECK: {args.root / 'readings'} is not a directory")
        return 2

    report = audit(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report, limit=args.limit))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
