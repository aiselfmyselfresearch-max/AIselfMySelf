#!/usr/bin/env python3
"""List the ledger rows a range of commits removed, and who they belonged to (stdlib only).

Why this tool exists
--------------------
``tools/referent_check.py`` walks the first-parent history and asks, for each
commit, which IDs did not come forward.  That answers "did a commit drop a row".
It does not answer three questions that a *revert* raises:

* how many rows of each collection the range removed, and which sessions they
  belonged to — one session's rows, or many sessions' rows;
* whether a removed row was **replaced** by a row with the same ID and different
  content (a rewrite that looks like a removal when only presence is compared);
* whether the removed IDs are still **cited in prose**.  A removed row whose name
  nobody wrote down leaves no trace in ``readings/*.md``; a removed row that was
  quoted leaves a name that resolves to nothing.

The tool reports these three things between any two refs.  It does not restore,
rewrite, or judge whether the removal was right.  The reason for a removal is not
in the diff; the diff only shows the shape of what is gone.

Usage:
  python3 tools/removed_rows.py --old 646e3ba^ --new 646e3ba
  python3 tools/removed_rows.py --old 646e3ba^ --new 646e3ba --json
  python3 tools/removed_rows.py --old 646e3ba^ --new 646e3ba --no-citations
"""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent

COLLECTIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "materials": ("material_id", ("state/materials.d", "state/materials.jsonl")),
    "questions": ("question_id", ("state/questions.d", "state/questions.jsonl")),
    "relations": ("relation_id", ("state/relations.d", "state/relations.jsonl")),
    "sessions": ("session_id", ("state/sessions.d", "state/sessions.jsonl")),
    "read_log": ("read_id", ("state/read_log.d", "state/read_log.jsonl")),
    "errata": ("errata_id", ("state/errata.d", "state/errata.jsonl")),
    "editorial_decisions": (
        "decision_id",
        ("state/editorial_decisions.d", "state/editorial_decisions.jsonl"),
    ),
}


def collection_for_path(path: str) -> str | None:
    """Return the collection a state path belongs to, or None for unmanaged files."""
    parts = path.split("/")
    if len(parts) < 2 or parts[0] != "state":
        return None
    name = parts[1].split(".")[0]
    return name if name in COLLECTIONS else None


def load_rows(rev: str, collection: str, root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Read a collection at a ref through ``git grep``; later rows win on duplicate IDs."""
    key, paths = COLLECTIONS[collection]
    pattern = '"%s"' % key
    existing = [
        p for p in paths if (root / p).exists() or subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", "%s:%s" % (rev, p)],
            capture_output=True,
        ).returncode == 0
    ]
    if not existing:
        return {}
    proc = subprocess.run(
        ["git", "-C", str(root), "grep", "-h", pattern, rev, "--", *existing],
        capture_output=True,
        text=True,
    )
    rows: dict[str, dict[str, Any]] = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        identifier = row.get(key)
        if isinstance(identifier, str):
            rows[identifier] = row
    return rows


def diff_rows(
    old: dict[str, dict[str, Any]], new: dict[str, dict[str, Any]]
) -> dict[str, list[str]]:
    """Split the difference between two snapshots into removed / added / changed."""
    return {
        "removed": sorted(set(old) - set(new)),
        "added": sorted(set(new) - set(old)),
        "changed": sorted(k for k in set(old) & set(new) if old[k] != new[k]),
    }


def group_by(rows: dict[str, dict[str, Any]], ids: Iterable[str], field: str) -> dict[str, int]:
    """Count removed IDs by one field of their old row (e.g. ``session_id``)."""
    counter: collections.Counter[str] = collections.Counter()
    for identifier in ids:
        row = rows.get(identifier) or {}
        value = row.get(field)
        counter[str(value) if value is not None else "(none)"] += 1
    return dict(counter.most_common())


def cite_counts(ids: Iterable[str], root: Path = ROOT) -> dict[str, list[str]]:
    """For each ID, list the ``readings/*.md`` files that mention it (empty lists omitted)."""
    texts: dict[str, str] = {}
    for path in sorted((root / "readings").glob("*.md")):
        texts[path.name] = path.read_text(encoding="utf-8", errors="replace")
    found: dict[str, list[str]] = {}
    for identifier in ids:
        hits = [name for name, text in texts.items() if identifier in text]
        if hits:
            found[identifier] = hits
    return found


def report(old_ref: str, new_ref: str, with_citations: bool = True, root: Path = ROOT) -> dict[str, Any]:
    """Build the full report for one pair of refs."""
    out: dict[str, Any] = {"old": old_ref, "new": new_ref, "collections": {}}
    for collection in COLLECTIONS:
        old = load_rows(old_ref, collection, root)
        new = load_rows(new_ref, collection, root)
        delta = diff_rows(old, new)
        entry: dict[str, Any] = {
            "old_rows": len(old),
            "new_rows": len(new),
            "removed": len(delta["removed"]),
            "added": len(delta["added"]),
            "changed": len(delta["changed"]),
            "removed_ids": delta["removed"],
            "by_session": group_by(old, delta["removed"], "session_id"),
        }
        if with_citations and delta["removed"]:
            entry["cited"] = cite_counts(delta["removed"], root)
        out["collections"][collection] = entry
    return out


def format_report(data: dict[str, Any]) -> str:
    lines = ["# rows removed: %s -> %s" % (data["old"], data["new"]), ""]
    for name, entry in data["collections"].items():
        if not (entry["removed"] or entry["added"] or entry["changed"]):
            continue
        lines.append(
            "%-20s %5d -> %5d  removed %3d  added %3d  changed %3d"
            % (name, entry["old_rows"], entry["new_rows"], entry["removed"], entry["added"], entry["changed"])
        )
        for session, count in entry["by_session"].items():
            lines.append("    by %s: %d" % (session, count))
        if "cited" in entry:
            if not entry["cited"]:
                lines.append("    cited in prose: 0 of %d" % entry["removed"])
            else:
                lines.append("    cited in prose: %d of %d" % (len(entry["cited"]), entry["removed"]))
                for identifier, files in sorted(entry["cited"].items()):
                    lines.append("      %s -> %s" % (identifier, ", ".join(files)))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--old", required=True, help="ref before the change")
    parser.add_argument("--new", required=True, help="ref after the change")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--no-citations", action="store_true", help="skip the prose scan")
    parser.add_argument("--root", default=str(ROOT), help="repository root (default: this checkout)")
    args = parser.parse_args(argv)

    data = report(args.old, args.new, with_citations=not args.no_citations, root=Path(args.root))
    print(json.dumps(data, ensure_ascii=False, indent=2) if args.json else format_report(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
