#!/usr/bin/env python3
"""Report ledger IDs that a commit or a merge did not carry forward (stdlib only).

Why this tool exists
--------------------
The ledger's identifiers are supposed to keep pointing at the same record: an ID
is minted once, and later rows refer to it.  On 2026-10-24 a batch merge kept
``main``'s row whenever two branches used the same ID.  One of those collisions
was not a revision of the same record but a different record: a question numbered
``Q-049`` on one branch and another question numbered ``Q-049`` on the other.
The merge kept one and dropped the other, and nothing in the ledger said so.

This tool reads the first-parent history of the repository and, for every
commit, compares each state file with the same file in each parent.  Any ID that
was in the parent and is not in the commit is reported, together with what the
ID points at now:

``missing``
    No row with that ID exists at HEAD.  The name survives only in the history
    (and, if it was cited, in prose written before the drop).
``same``
    A row with that ID exists at HEAD and is byte-identical after canonical
    JSON serialisation.  The row came back later by another path.
``changed``
    A row with that ID exists at HEAD but its content differs.  The name now
    points at something else.  This is the homonym case; the tool prints both
    snippets and does not decide whether the difference is an edit or a
    different object.

The tool reports; it does not judge and it does not repair.  Rewriting a
collision is an editorial decision, and the ledger's rule is that corrections are
added beside the record, not written over it.

Usage:
  python3 tools/referent_check.py
  python3 tools/referent_check.py --collection questions --limit 10
  python3 tools/referent_check.py --markdown > /tmp/referents.md
  python3 tools/referent_check.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

# Collection name -> the key that identifies a row.  Values name reference keys
# (``session_id`` inside a fragment, for example) and are never used here.
ID_KEYS: dict[str, str] = {
    "fragments": "fragment_id",
    "questions": "question_id",
    "materials": "material_id",
    "relations": "relation_id",
    "sessions": "session_id",
    "read_log": "read_id",
    "motifs": "motif_id",
    "editorial_decisions": "decision_id",
    "errata": "errata_id",
}

TEXT_KEYS = ("question", "text", "title", "claim", "note", "notes", "summary")

# Fields that carry a row's identity, as opposed to its annotations.  A row whose
# ID survives while these change is not the same record edited; it is another
# record wearing the same name.  Edits to ``notes`` or ``material_ids`` do not
# count, which keeps ordinary revisions out of the report.
IDENTITY_KEYS: dict[str, tuple[str, ...]] = {
    "fragments": ("text",),
    "questions": ("question",),
    "materials": ("title",),
    "relations": ("left", "right", "relation_type"),
    "sessions": ("started_at", "session_id"),
    "read_log": ("target",),
    "motivations": (),
    "motifs": ("label", "name", "title"),
    "editorial_decisions": ("decision", "subject_id", "decision_type"),
    "errata": ("claim", "subject_id"),
}


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _collection_of(path: str) -> str | None:
    """Return the collection a state path belongs to, or None."""
    if not path.startswith("state/"):
        return None
    name = path[len("state/") :]
    if "/" in name:
        directory, filename = name.split("/", 1)
        if not directory.endswith(".d"):
            return None
        collection = directory[:-2]
        if collection in ID_KEYS and filename.endswith(".jsonl"):
            return collection
        return None
    if name.endswith(".jsonl"):
        collection = name[: -len(".jsonl")]
        if collection in ID_KEYS:
            return collection
    return None


def _canonical(row: Any) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def identity(collection: str, row: dict[str, Any]) -> str:
    """Canonical form of the fields that say *which* record this is."""
    keys = IDENTITY_KEYS.get(collection, ())
    picked = {key: row[key] for key in keys if key in row}
    return _canonical(picked) if picked else _canonical(row)


def _snippet(row: dict[str, Any]) -> str:
    for key in TEXT_KEYS:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            text = " ".join(value.split())
            return text[:72] + ("…" if len(text) > 72 else "")
    return ""


def parse_rows(text: str, id_key: str) -> dict[str, str]:
    """Parse a JSONL blob into ``{id: canonical json}``, skipping bad lines."""
    rows: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        identifier = row.get(id_key)
        if isinstance(identifier, str) and identifier:
            rows[identifier] = _canonical(row)
    return rows


class BlobCache:
    """Memoised ``git show <rev>:<path>`` lookups."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._cache: dict[tuple[str, str], str] = {}

    def text(self, rev: str, path: str) -> str:
        key = (rev, path)
        if key not in self._cache:
            self._cache[key] = _git(self.root, "show", f"{rev}:{path}")
        return self._cache[key]


def _changed_state_paths(root: Path, parent: str, commit: str) -> list[str]:
    out = _git(
        root, "diff-tree", "-r", "--no-commit-id", "--name-only", parent, commit, "--", "state"
    )
    return [line for line in out.splitlines() if line.strip()]


def _load_file(
    cache: BlobCache, rev: str, path: str, id_key: str
) -> dict[str, str]:
    try:
        text = cache.text(rev, path)
    except RuntimeError:
        return {}
    return parse_rows(text, id_key)


def head_maps(root: Path, rev: str = "HEAD") -> dict[str, dict[str, str]]:
    """Load every collection's ID -> canonical row map at one commit."""
    maps: dict[str, dict[str, str]] = defaultdict(dict)
    listing = _git(root, "ls-tree", "-r", "--name-only", rev, "--", "state")
    cache = BlobCache(root)
    for path in listing.splitlines():
        collection = _collection_of(path)
        if collection is None:
            continue
        maps[collection].update(
            _load_file(cache, rev, path, ID_KEYS[collection])
        )
    return dict(maps)


def collect_events(
    root: Path,
    collections: Iterable[str] | None = None,
    first_parent: bool = False,
) -> list[dict[str, Any]]:
    """Walk the first-parent history and record every dropped ID.

    Each event is ``{collection, id, commit, commit_date, parent, parent_index,
    row}``.  The same ID can be dropped more than once (a row that leaves,
    returns by another merge, and leaves again); callers group the events.
    """
    wanted = set(collections) if collections else set(ID_KEYS)
    cache = BlobCache(root)
    limits = ["--first-parent"] if first_parent else []
    revs = [
        line.strip()
        for line in _git(root, "rev-list", "--topo-order", "--reverse", *limits, "HEAD").splitlines()
        if line.strip()
    ]
    events: list[dict[str, Any]] = []
    dates: dict[str, str] = {}
    for commit in revs:
        parents = _git(root, "rev-list", "--parents", "-n", "1", commit).split()[1:]
        if not parents:
            continue
        if commit not in dates:
            dates[commit] = _git(root, "show", "-s", "--format=%ad", "--date=short", commit).strip()
        if len(parents) == 1:
            parent = parents[0]
            for path in _changed_state_paths(root, parent, commit):
                collection = _collection_of(path)
                if collection is None or collection not in wanted:
                    continue
                id_key = ID_KEYS[collection]
                before = _load_file(cache, parent, path, id_key)
                after = _load_file(cache, commit, path, id_key)
                for identifier in before.keys() - after.keys():
                    events.append(
                        {
                            "collection": collection,
                            "id": identifier,
                            "kind": "dropped",
                            "commit": commit,
                            "commit_date": dates[commit],
                            "parent": parent,
                            "parent_index": 1,
                            "row": before[identifier],
                        }
                    )
            continue

        # A merge can keep the ID and still discard one parent's row: the merge
        # rule "main wins" replaces the row with the other parent's version.  The
        # ID stays, so a presence-only comparison sees nothing.
        changed: dict[str, set[str]] = defaultdict(set)
        for parent in parents:
            for path in _changed_state_paths(root, parent, commit):
                changed[path].add(parent)
        for path, affected in changed.items():
            collection = _collection_of(path)
            if collection is None or collection not in wanted:
                continue
            id_key = ID_KEYS[collection]
            per_parent = {
                parent: _load_file(cache, parent, path, id_key) for parent in parents
            }
            after = _load_file(cache, commit, path, id_key)
            for index, parent in enumerate(parents, start=1):
                if parent not in affected:
                    continue
                others: dict[str, str] = {}
                for other, rows in per_parent.items():
                    if other != parent:
                        others.update(rows)
                for identifier, row in per_parent[parent].items():
                    if identifier not in after:
                        kind = "dropped"
                    elif after[identifier] != row and after[identifier] == others.get(identifier):
                        kind = "overridden"
                    else:
                        continue
                    events.append(
                        {
                            "collection": collection,
                            "id": identifier,
                            "kind": kind,
                            "commit": commit,
                            "commit_date": dates[commit],
                            "parent": parent,
                            "parent_index": index,
                            "row": row,
                        }
                    )
    return events


def classify(
    events: list[dict[str, Any]], head: dict[str, dict[str, str]]
) -> list[dict[str, Any]]:
    """Group events by ID and label what the ID points at now."""
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    history: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        key = (event["collection"], event["id"])
        history[key].append(event)
        if key not in grouped:
            grouped[key] = {
                "collection": event["collection"],
                "id": event["id"],
                "first_commit": event["commit"],
                "first_date": event["commit_date"],
                "first_parent_index": event["parent_index"],
                "kind": event["kind"],
                "count": 0,
                "row": event["row"],
            }
        grouped[key]["count"] += 1
        grouped[key]["last_commit"] = event["commit"]
        grouped[key]["last_date"] = event["commit_date"]

    rows = []
    for key, item in grouped.items():
        current = head.get(item["collection"], {}).get(item["id"])
        item["head_row"] = current
        # Prefer the event whose row is the one that no longer points at HEAD's
        # record: a single ID can be dropped more than once (a row leaves,
        # returns by another merge, leaves again), and the first drop is not
        # necessarily the one that changed what the name means.
        divergent = None
        if current is not None:
            target = identity(item["collection"], json.loads(current))
            for event in history[key]:
                if identity(item["collection"], json.loads(event["row"])) != target:
                    divergent = event
                    break
        if current is None:
            item["status"] = "missing"
        elif divergent is not None:
            item["status"] = "changed"
            item["first_commit"] = divergent["commit"]
            item["first_date"] = divergent["commit_date"]
            item["first_parent_index"] = divergent["parent_index"]
            item["kind"] = divergent["kind"]
            item["row"] = divergent["row"]
        else:
            item["status"] = "same"
        item["before"] = _snippet(json.loads(item["row"]))
        item["after"] = _snippet(json.loads(item["head_row"])) if item["head_row"] else ""
        rows.append(item)

    order = {"missing": 0, "changed": 1, "same": 2}
    rows.sort(key=lambda r: (order.get(r["status"], 3), r["first_date"], r["collection"], r["id"]))
    return rows


def render_text(rows: list[dict[str, Any]], limit: int) -> str:
    shown = rows[:limit] if limit else rows
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["status"]] += 1
    lines = [
        f"dropped or overridden IDs: {len(rows)}  (missing {counts['missing']}, "
        f"changed {counts['changed']}, same {counts['same']})",
        "",
    ]
    for row in shown:
        lines.append(
            f"{row['collection']:<18} {row['id']:<28} {row['kind']:<11} "
            f"{row['status']:<8} {row['first_date']} p{row['first_parent_index']} ×{row['count']}"
        )
        if row["status"] == "changed":
            lines.append(f"    before: {row['before']}")
            lines.append(f"    after : {row['after']}")
        elif row["status"] == "missing":
            lines.append(f"    last  : {row['before']}")
    if limit and len(rows) > limit:
        lines.append("")
        lines.append(f"… {len(rows) - limit} more (--limit 0 to show all)")
    return "\n".join(lines)


def render_markdown(rows: list[dict[str, Any]], limit: int) -> str:
    shown = rows[:limit] if limit else rows
    lines = [
        "| collection | id | kind | at HEAD | first event | parent | repeats | before / after |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for row in shown:
        if row["status"] == "changed":
            detail = f"{row['before']}<br>→ {row['after']}"
        else:
            detail = row["before"]
        detail = detail.replace("|", "\\|")
        lines.append(
            f"| {row['collection']} | `{row['id']}` | {row['kind']} | {row['status']} | "
            f"{row['first_date']} | p{row['first_parent_index']} | {row['count']} | {detail} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=str(ROOT), help="repository root (default: this checkout)")
    parser.add_argument("--collection", action="append", choices=sorted(ID_KEYS))
    parser.add_argument("--limit", type=int, default=40, help="rows to print; 0 = all")
    parser.add_argument(
        "--first-parent",
        action="store_true",
        help="scan only the first-parent spine (faster; misses merges inside side branches)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo).resolve()
    events = collect_events(root, args.collection, first_parent=args.first_parent)
    head = head_maps(root)
    rows = classify(events, head)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    elif args.markdown:
        print(render_markdown(rows, args.limit))
    else:
        print(render_text(rows, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
