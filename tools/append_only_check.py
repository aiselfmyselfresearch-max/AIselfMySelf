#!/usr/bin/env python3
"""Fail when a ledger line that existed before is no longer there, byte for byte (stdlib only).

Why this tool exists
--------------------
The ledgers under ``state/`` are append-only: an existing row is never rewritten,
re-serialised or removed, and a correction is a new row (errata, overlay,
``supersedes``).  Every other gate parses the rows before it looks at them.  A
line whose bytes changed while its parsed content stayed the same therefore
passes all of them, and so does an edited row as long as it is still valid.

On 2026-11-12 one branch of 60 commits (PR #655, closed without merging) turned
out to have re-serialised 88 note rows in one commit, nine of them rows that
other sessions had already merged into main.  No gate reported it.  A merge
conflict did.  The same day, a scan of the 177 commits of main then available
found rows that were already on main changed by four merged pull requests in
three days: re-serialised (#654, five relations; #691, seven relations; #631,
two sessions) or edited (#631, three sessions; #645, one session, recorded as
approved by the user).  The account is in
``readings/2026-11-12-what-pr-655-did-and-what-now-stops-it.md``.

What it checks
--------------
For each ledger collection (``state/<name>.jsonl`` plus ``state/<name>.d/*.jsonl``)
the multiset of lines at the base must be contained in the multiset of lines now.
A line may move between files of the same collection, which is what shard
consolidation does (``docs/parallel-work.md`` §3).  It may not change and it may
not disappear.

The base is the shared ledger: ``origin/main``.  Rows that a branch added and
that are not on main yet are that branch's own draft; the tool does not compare
them with anything.

Usage:
  python3 tools/append_only_check.py                # working tree against origin/main: run before committing
  python3 tools/append_only_check.py --base HEAD^1  # CI on a pull request: the merge result against its base
  python3 tools/append_only_check.py --parents      # one commit against each of its parents (history audit)
  python3 tools/append_only_check.py --base REV [--head REV]

How rows get rewritten in practice: a script loads a shard with ``json.loads``,
appends its rows, and writes everything back with ``json.dumps``.  The rows that
were already there come back with different spacing or key order.  Append with
``open(path, "ab")`` (or ``existing_text + new_lines``) instead.

The tool does not say whose rows were lost or whether they are still cited;
``tools/removed_rows.py`` reports that.  It does not restore anything, and it has
no override: when a human has approved changing a row on main, this check stays
red and its output is the list of what is being changed.

Exit status: 0 nothing lost, 1 lines lost, 2 the comparison could not be made.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent

# Every append-only ledger.  tests/test_append_only_check.py asserts that this
# covers tools/validate_seed.py's COLLECTIONS, so a new collection cannot be
# added there and silently left out here.
COLLECTIONS: dict[str, str] = {
    "questions": "question_id",
    "motifs": "motif_id",
    "materials": "material_id",
    "fragments": "fragment_id",
    "relations": "relation_id",
    "sessions": "session_id",
    "read_log": "read_id",
    "editorial_decisions": "decision_id",
    "notes": "note_id",
    "errata": "errata_id",
    "hypotheses": "hypothesis_id",
    "evaluations": "evaluation_id",
}

Lines = dict[str, "collections.Counter[bytes]"]


def collection_for_path(path: str) -> str | None:
    """Return the ledger a path belongs to, or None when it is not a ledger file."""
    parts = path.split("/")
    if len(parts) == 2 and parts[0] == "state" and parts[1].endswith(".jsonl"):
        name = parts[1][: -len(".jsonl")]
    elif len(parts) == 3 and parts[0] == "state" and parts[1].endswith(".d") and parts[2].endswith(".jsonl"):
        name = parts[1][: -len(".d")]
    else:
        return None
    return name if name in COLLECTIONS else None


def add_lines(target: Lines, path: str, payload: bytes) -> None:
    name = collection_for_path(path)
    if name is None:
        return
    counter = target.setdefault(name, collections.Counter())
    for line in payload.split(b"\n"):
        if line.strip():
            counter[line] += 1


def lines_in_worktree(root: Path = ROOT) -> Lines:
    result: Lines = {}
    state = root / "state"
    if not state.is_dir():
        return result
    for path in sorted(state.glob("*.jsonl")) + sorted(state.glob("*.d/*.jsonl")):
        add_lines(result, path.relative_to(root).as_posix(), path.read_bytes())
    return result


class CannotCompare(Exception):
    """A ref needed for the comparison is not available in this checkout."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True)


def lines_at(rev: str, root: Path = ROOT) -> Lines:
    if _git(root, "cat-file", "-e", f"{rev}^{{commit}}").returncode != 0:
        raise CannotCompare(f"commit {rev!r} is not available in this checkout")
    result: Lines = {}
    if _git(root, "cat-file", "-e", f"{rev}:state").returncode != 0:
        return result  # the commit has no state/ directory at all
    archive = _git(root, "archive", "--format=tar", rev, "state")
    if archive.returncode != 0:
        raise CannotCompare(f"cannot read state/ at {rev!r}: {archive.stderr.decode(errors='replace').strip()}")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        for member in tar:
            if not member.isfile():
                continue
            handle = tar.extractfile(member)
            if handle is not None:
                add_lines(result, member.name, handle.read())
    return result


def default_base(root: Path = ROOT) -> tuple[str, str]:
    """Pick the base when none is given: (rev, label for the report)."""
    if _git(root, "cat-file", "-e", "origin/main^{commit}").returncode != 0:
        return "HEAD", "HEAD (origin/main is not available here)"
    if _git(root, "merge-base", "--is-ancestor", "origin/main", "HEAD").returncode == 0:
        return "origin/main", "origin/main"
    merge_base = _git(root, "merge-base", "origin/main", "HEAD")
    rev = merge_base.stdout.decode().strip()
    if merge_base.returncode == 0 and rev:
        return rev, f"{rev[:7]} (merge base of HEAD and origin/main)"
    raise CannotCompare(
        "HEAD does not contain origin/main and their merge base is not in this checkout; "
        "merge origin/main first, or pass --base"
    )


def parents_of(rev: str, root: Path = ROOT) -> list[str]:
    out = _git(root, "rev-list", "--parents", "-n", "1", rev)
    if out.returncode != 0:
        raise CannotCompare(f"commit {rev!r} is not available in this checkout")
    return out.stdout.decode().split()[1:]


def _row_id(name: str, line: bytes) -> str | None:
    try:
        row = json.loads(line)
    except (ValueError, UnicodeDecodeError):
        return None
    value = row.get(COLLECTIONS[name]) if isinstance(row, dict) else None
    return value if isinstance(value, str) else None


def _parsed(line: bytes) -> object:
    try:
        return json.loads(line)
    except (ValueError, UnicodeDecodeError):
        return line


def lost_lines(base: Lines, now: Lines) -> dict[str, list[dict[str, str]]]:
    """Describe every base line that is missing now, per collection.

    ``kind`` is ``reserialised`` (same ID, same parsed content, different
    bytes), ``edited`` (same ID, different content) or ``removed`` (the ID is
    gone, or the line had no ID to follow).
    """
    report: dict[str, list[dict[str, str]]] = {}
    for name, base_counter in base.items():
        now_counter = now.get(name, collections.Counter())
        missing = base_counter - now_counter
        if not missing:
            continue
        current_by_id: dict[str, list[bytes]] = {}
        for line in now_counter:
            identifier = _row_id(name, line)
            if identifier is not None:
                current_by_id.setdefault(identifier, []).append(line)
        entries: list[dict[str, str]] = []
        for line, count in missing.items():
            identifier = _row_id(name, line)
            kind = "removed"
            if identifier is not None and identifier in current_by_id:
                same = any(_parsed(other) == _parsed(line) for other in current_by_id[identifier])
                kind = "reserialised" if same else "edited"
            for _ in range(count):
                entries.append({"id": identifier or "(no id)", "kind": kind})
        entries.sort(key=lambda entry: (entry["kind"], entry["id"]))
        report[name] = entries
    return report


def format_report(label: str, report: dict[str, list[dict[str, str]]], limit: int = 12) -> str:
    out: list[str] = []
    total = sum(len(entries) for entries in report.values())
    out.append(f"FAIL: {total} ledger line(s) that existed at {label} are no longer present byte for byte")
    for name in sorted(report):
        entries = report[name]
        kinds = collections.Counter(entry["kind"] for entry in entries)
        summary = ", ".join(f"{kind} {count}" for kind, count in sorted(kinds.items()))
        out.append(f"  {name}: {len(entries)} ({summary})")
        for entry in entries[:limit]:
            out.append(f"    - {entry['id']}: {entry['kind']}")
        if len(entries) > limit:
            out.append(f"    ... {len(entries) - limit} more")
    out.append("  reserialised = same content, different bytes; edited = same ID, different content; removed = gone")
    out.append("  remedy: put the original line back exactly as it was (git show <base>:<file>), then append.")
    out.append("          A correction is a new row (errata, overlay, supersedes), never a changed one.")
    return "\n".join(out)


def check(pairs: Iterable[tuple[str, Lines, Lines]]) -> tuple[int, list[str]]:
    status = 0
    messages: list[str] = []
    for label, base, now in pairs:
        report = lost_lines(base, now)
        if report:
            status = 1
            messages.append(format_report(label, report))
        else:
            kept = sum(sum(counter.values()) for counter in base.values())
            messages.append(f"PASS: all {kept} ledger lines of {label} are still present byte for byte")
    return status, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument(
        "--base",
        help="ref whose ledger lines must all still exist (default: origin/main, or its merge base with HEAD)",
    )
    parser.add_argument("--head", help="ref to check (default: the working tree)")
    parser.add_argument(
        "--parents",
        action="store_true",
        help="check HEAD (or --head) against each of its parents instead of --base",
    )
    parser.add_argument("--root", default=str(ROOT), help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.parents and args.base:
        parser.error("--parents and --base cannot be combined")

    try:
        if args.parents:
            head = args.head or "HEAD"
            now = lines_at(head, root)
            parents = parents_of(head, root)
            if not parents:
                print(f"PASS: {head} has no parent; nothing to compare")
                return 0
            pairs = [(f"parent {parent[:7]} of {head}", lines_at(parent, root), now) for parent in parents]
        else:
            base, label = (args.base, args.base) if args.base else default_base(root)
            now = lines_at(args.head, root) if args.head else lines_in_worktree(root)
            pairs = [(label, lines_at(base, root), now)]
    except CannotCompare as exc:
        print(f"CANNOT COMPARE: {exc}")
        print("  A shallow checkout needs the commit fetched first (CI: actions/checkout with fetch-depth: 2).")
        return 2

    status, messages = check(pairs)
    print("\n".join(messages))
    return status


if __name__ == "__main__":
    sys.exit(main())
