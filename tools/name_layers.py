#!/usr/bin/env python3
"""Check whether the names the archive writes down still reach a record (stdlib only).

Why this tool exists
--------------------
The ledger validates its own structured fields: every ``question_ids`` entry, every
``material_ids`` entry is checked against the union.  Nothing checks the prose.
``readings/*.md`` is where the archive talks to itself and to a later reader, and it
cites records by ID in running text.  An ID written there can be:

* **resolved** — a record with that ID exists in the current union;
* **lost** — the ID existed in the git history of ``state/`` and no longer does;
* **unknown** — the ID never appeared in ``state/`` at all (a draft ID, a typo, a
  truncated form such as ``Q-7742`` for ``Q-20261027-7742e7``).

The tool also reports a second naming layer.  Every material carries a
``source.source_id``; the schema calls it a string identifier and does not require
it to be unique.  ``sources`` lists the IDs that are attached to more than one
different source title — one name, two sources.

This tool reports; it does not repair and does not judge.  Whether a citation that
resolves still points at the *same* record is not decided here; that is what
``tools/referent_check.py`` measures over time.

Usage:
  python3 tools/name_layers.py citations
  python3 tools/name_layers.py citations --history
  python3 tools/name_layers.py sources
  python3 tools/name_layers.py citations --json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parents[1]

# Prefixes are ordered longest-first so that ``MAT-LIT-…`` is not read as ``MAT-…``.
ID_RE = re.compile(
    r"\b(?:FRAG|Q|MAT-LIT|MAT-TRC|MAT-EVD|MAT|REL|SESSION|MOTIF|ERR|READ|ED|EVD|SRC)"
    r"-[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\b"
)
DATE_ONLY_RE = re.compile(r"^[A-Z-]+-\d{8}$")
RANDOM_RE = re.compile(r"^[A-Z-]+-\d{8}-[0-9a-f]{6}$")
SEQUENTIAL_RE = re.compile(r"^[A-Z-]+-\d{1,6}$")
PLACEHOLDER_RE = re.compile(r"[xX]")


def state_files(root: Path, pattern: str = "state/*.jsonl") -> list[Path]:
    base = sorted(root.glob(pattern))
    shards = sorted(root.glob(pattern.replace(".jsonl", ".d/*.jsonl")))
    return base + shards


def defined_ids(root: Path) -> set[str]:
    """Every ID the ledger defines: top-level ``*_id`` values and ``source.source_id``."""
    known: set[str] = set()
    for path in state_files(root):
        if not path.is_file():
            continue
        for line in path.open(encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            for key, value in row.items():
                if key.endswith("_id") and isinstance(value, str):
                    known.add(value)
            source = row.get("source")
            if isinstance(source, dict):
                source_id = source.get("source_id")
                if isinstance(source_id, str):
                    known.add(source_id)
    return known


def markdown_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.suffix == ".md" and path.is_file():
            files.append(path)
    return files


def shape(token: str) -> str:
    if PLACEHOLDER_RE.search(token):
        return "placeholder"
    if DATE_ONLY_RE.match(token):
        return "date_only"
    if RANDOM_RE.match(token):
        return "random"
    if SEQUENTIAL_RE.match(token):
        return "sequential"
    return "other"


def extract(text: str) -> collections.Counter[str]:
    return collections.Counter(ID_RE.findall(text))


def scan(files: Iterable[Path]) -> tuple[dict[str, set[str]], collections.Counter[str]]:
    """Map each cited token to the files that cite it, and count its occurrences."""
    seen: dict[str, set[str]] = collections.defaultdict(set)
    counts: collections.Counter[str] = collections.Counter()
    for path in files:
        for token in ID_RE.findall(path.read_text(encoding="utf-8")):
            seen[token].add(str(path))
            counts[token] += 1
    return dict(seen), counts


def _token_is_defined(root: Path, commit: str, token: str) -> bool:
    """True if ``token`` is the value of a ``*_id`` field anywhere in ``commit``."""
    listing = subprocess.run(
        ["git", "grep", "-l", "--fixed-strings", token, commit, "--", "state"],
        cwd=str(root),
        capture_output=True,
        text=True,
    ).stdout
    for line in listing.splitlines():
        path = line.split(":", 1)[1] if ":" in line else ""
        if not path:
            continue
        blob = subprocess.run(
            ["git", "show", f"{commit}:{path}"], cwd=str(root), capture_output=True, text=True
        ).stdout
        for row in blob.splitlines():
            row = row.strip()
            if not row or token not in row:
                continue
            try:
                record = json.loads(row)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and any(
                key.endswith("_id") and value == token for key, value in record.items()
            ):
                return True
    return False


def history_status(root: Path, token: str) -> str:
    """Classify an unresolved ID by what the history of ``state/`` says about it.

    ``lost``      the token was a defined ID in some commit and is not one now;
    ``text_only`` the token appears in ``state/`` only inside prose (a note, a
                  source string) and was never a record ID;
    ``unknown``   the token never appears in ``state/`` at all.
    """
    proc = subprocess.run(
        [
            "git", "log", "--all", "--format=%H", "--max-count=8", "-S", token, "--", "state",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    commits = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not commits:
        return "unknown"
    for commit in commits:
        if _token_is_defined(root, commit, token):
            return "lost"
    return "text_only"


def source_collisions(root: Path) -> list[dict[str, object]]:
    """source_ids attached to more than one distinct source title."""
    titles: dict[str, set[str]] = collections.defaultdict(set)
    materials: dict[str, set[str]] = collections.defaultdict(set)
    for path in state_files(root, "state/materials.jsonl"):
        if not path.is_file():
            continue
        for line in path.open(encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = row.get("source")
            if not isinstance(source, dict):
                continue
            source_id = source.get("source_id")
            if not isinstance(source_id, str):
                continue
            titles[source_id].add((source.get("title") or "").strip())
            materials[source_id].add(row.get("material_id", ""))
    return [
        {
            "source_id": source_id,
            "titles": sorted(t for t in titles[source_id] if t),
            "material_ids": sorted(m for m in materials[source_id] if m),
        }
        for source_id in sorted(titles)
        if len(titles[source_id]) > 1
    ]


NOTE_KEYS = ("notes", "note", "editor_note")


def scan_state_notes(root: Path) -> tuple[dict[str, set[str]], collections.Counter[str]]:
    """ID-shaped tokens written inside the ledger's own commentary fields.

    The structured fields are validated; ``notes`` is prose.  A session can write
    ``ED-…`` into its notes for a decision it never added as a row.
    """
    seen: dict[str, set[str]] = collections.defaultdict(set)
    counts: collections.Counter[str] = collections.Counter()
    for path in state_files(root):
        if not path.is_file():
            continue
        label = path.name
        for line in path.open(encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            owner = next(
                (str(row[key]) for key in row if key.endswith("_id") and isinstance(row[key], str)),
                label,
            )
            for key in NOTE_KEYS:
                value = row.get(key)
                if not isinstance(value, str):
                    continue
                for token in ID_RE.findall(value):
                    seen[token].add(f"{label}:{owner}")
                    counts[token] += 1
    return dict(seen), counts


def build_report(
    root: Path,
    files: list[Path] | None = None,
    with_history: bool = False,
    state_notes: bool = False,
) -> dict[str, object]:
    known = defined_ids(root)
    if state_notes:
        cited, counts = scan_state_notes(root)
    else:
        cited, counts = scan(files or [])
    resolved = sorted(token for token in cited if token in known)
    unresolved = sorted(token for token in cited if token not in known)
    buckets: dict[str, list[str]] = collections.defaultdict(list)
    for token in unresolved:
        buckets[shape(token)].append(token)
    real = buckets["random"] + buckets["sequential"]
    status: dict[str, str] = {}
    if with_history:
        for token in real:
            status[token] = history_status(root, token)
    return {
        "files": len(files or []),
        "cited_distinct": len(cited),
        "cited_occurrences": sum(counts.values()),
        "resolved": resolved,
        "unresolved": {token: sorted(cited[token]) for token in unresolved},
        "shapes": {name: sorted(tokens) for name, tokens in buckets.items()},
        "real_unresolved": real,
        "history": status,
        "source_collisions": source_collisions(root),
    }


def render_citations(report: dict[str, object], limit: int) -> str:
    shapes = report["shapes"]
    history = report["history"]
    lost = [t for t, s in history.items() if s == "lost"]
    text_only = [t for t, s in history.items() if s == "text_only"]
    unknown = [t for t, s in history.items() if s == "unknown"]
    lines = [
        f"files scanned: {report['files']}",
        f"distinct IDs cited: {report['cited_distinct']} "
        f"(occurrences {report['cited_occurrences']})",
        f"resolved at HEAD: {len(report['resolved'])}",
        f"unresolved, ID-shaped: {len(report['real_unresolved'])}",
    ]
    if history:
        lines.append(f"  lost (was a defined ID): {len(lost)}")
        lines.append(f"  text only (never a defined ID): {len(text_only)}")
        lines.append(f"  unknown (never in state/): {len(unknown)}")
    lines.append(
        "partial forms (not counted as broken): "
        f"date-only {len(shapes.get('date_only', []))}, "
        f"placeholder {len(shapes.get('placeholder', []))}, "
        f"other {len(shapes.get('other', []))}"
    )
    if not history:
        lines.append("(pass --history to separate lost IDs from never-existing IDs)")
    rows = lost + text_only + unknown if history else report["real_unresolved"]
    if rows:
        lines.append("")
        for token in rows[:limit]:
            tag = history.get(token, "?")
            files = report["unresolved"][token]
            lines.append(f"{token:<32} {tag:<8} {files[0]}" + (f" (+{len(files)-1})" if len(files) > 1 else ""))
        if limit and len(rows) > limit:
            lines.append(f"… {len(rows) - limit} more (--limit 0 to show all)")
    return "\n".join(lines)


def render_sources(collisions: list[dict[str, object]], limit: int) -> str:
    lines = [f"source_ids with more than one source title: {len(collisions)}", ""]
    for item in collisions[: limit or len(collisions)]:
        titles = " ／ ".join(str(t) for t in item["titles"])
        lines.append(f"{item['source_id']}  {', '.join(str(m) for m in item['material_ids'])}")
        lines.append(f"    {titles}")
    if limit and len(collisions) > limit:
        lines.append(f"… {len(collisions) - limit} more (--limit 0 to show all)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=str(ROOT))
    common.add_argument("--limit", type=int, default=20)
    common.add_argument("--json", action="store_true")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    cite = sub.add_parser("citations", parents=[common], help="resolve IDs cited in markdown prose")
    cite.add_argument("paths", nargs="*", default=["readings"])
    cite.add_argument("--history", action="store_true", help="check git history for unresolved IDs")

    notes = sub.add_parser(
        "state-notes", parents=[common], help="resolve IDs written inside the ledger's notes fields"
    )
    notes.add_argument("--history", action="store_true", help="check git history for unresolved IDs")

    sub.add_parser(
        "sources", parents=[common], help="list source_ids that carry more than one source title"
    )

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if args.command == "sources":
        collisions = source_collisions(root)
        if args.json:
            print(json.dumps(collisions, ensure_ascii=False, indent=2))
        else:
            print(render_sources(collisions, args.limit))
        return 0

    if args.command == "state-notes":
        report = build_report(root, with_history=args.history, state_notes=True)
    else:
        paths = [Path(p) if Path(p).is_absolute() else root / p for p in args.paths]
        report = build_report(root, markdown_files(paths), args.history)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_citations(report, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
