#!/usr/bin/env python3
"""List ``reading_held`` claims, and say which of them a later note may have closed.

Why this tool exists.  ``reading_held`` records that a judgment was left open.
The ledger has no field that records the *closing* of it: ``supersedes`` is the
only pointer between notes, and it is used by 11 of 350 notes (3.1%).  So a held
claim keeps its original tense forever, and a later session can read a
nine-month-old hold as a present-tense gap.  That happened: ``READ-20261111-020288``
records a session that executed another session's ``reading_held`` homework on
the same real date (``SESSION-20261105-8986a3``), while the hold was left standing
because the closing note was ``AB_crossed`` and had no ``supersedes``.

This tool does not decide whether a hold is closed.  Japanese claim polarity
cannot be classified by rule here (two attempts failed; see
``tools/scope_report.py``).  What it does is put two mechanical facts next to each
hold:

  1. **closed_by** — a later note whose ``supersedes`` names the holding note;
  2. **touched_by** — later notes that mention one of the ledger IDs appearing in
     the held claim's own text, or that read such an ID (``read_log``).

A ``touched_by`` entry is a candidate to read, not a finding.  Nothing is written.

Usage:
  python3 tools/held_report.py                 # summary + 20 candidates
  python3 tools/held_report.py --limit 60      # more rows
  python3 tools/held_report.py --open-only     # only holds with no candidate
  python3 tools/held_report.py --json          # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
HELD_KIND = "reading_held"
# Ledger IDs are the only tokens a machine can match without reading Japanese.
ID_PATTERN = re.compile(
    r"\b(?:MAT|MAT-LIT|MAT-EVD|MAT-TRC|MAT-ARC|FRAG|Q|REL|NOTE|READ|MOTIF|ERR|SESS)"
    r"-[0-9A-Za-z][0-9A-Za-z-]*"
)


def _ids_in(text: str) -> set[str]:
    return {m.group(0) for m in ID_PATTERN.finditer(text or "")}


def _specific(ids: set[str]) -> set[str]:
    """Drop question IDs: every claim about a central question shares one, so a
    shared ``Q-00x`` says nothing about whether *this* hold was touched."""
    return {i for i in ids if not i.startswith("Q-")}


def load(root: Path = ROOT) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    collections, errors = ledger_io.load_collections(
        {
            "notes": (root / "state" / "notes.jsonl", "note_id"),
            "read_log": (root / "state" / "read_log.jsonl", "read_id"),
        },
        root=root,
    )
    if errors:
        for problem in errors:
            print(f"ledger error: {problem}", file=sys.stderr)
    notes = list(collections.get("notes", {}).values())
    reads = list(collections.get("read_log", {}).values())
    return notes, reads


def _stamp(note: dict[str, Any]) -> str:
    return str(note.get("created_at") or "")


def build(notes: list[dict[str, Any]], reads: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the hold inventory.  Pure function of the two collections."""
    by_id = {n.get("note_id"): n for n in notes}
    superseded_by: dict[str, list[str]] = {}
    for note in notes:
        for target in note.get("supersedes") or []:
            superseded_by.setdefault(target, []).append(note.get("note_id"))

    # What each note touched: IDs it read, and IDs its claims mention.
    touch: dict[str, dict[str, Any]] = {}
    for read in reads:
        target = read.get("target") or {}
        tid = target.get("id") if isinstance(target, dict) else None
        sid = read.get("session_id")
        if not tid or not sid:
            continue
        entry = touch.setdefault(sid, {"at": str(read.get("created_at") or ""), "ids": set()})
        entry["ids"].add(tid)
        if str(read.get("created_at") or "") > entry["at"]:
            entry["at"] = str(read.get("created_at") or "")
    note_tokens: dict[str, set[str]] = {}
    for note in notes:
        tokens: set[str] = set()
        for claim in note.get("claims") or []:
            tokens |= _ids_in(claim.get("text", ""))
            for field in ("question_ids", "fragment_ids", "material_ids", "motif_ids"):
                for value in claim.get(field) or []:
                    tokens.add(value)
        note_tokens[note.get("note_id")] = tokens

    rows: list[dict[str, Any]] = []
    for note in notes:
        nid = note.get("note_id")
        stamp = _stamp(note)
        for claim in note.get("claims") or []:
            if claim.get("kind") != HELD_KIND:
                continue
            ids = _ids_in(claim.get("text", ""))
            ids |= set(claim.get("material_ids") or [])
            ids |= set(claim.get("question_ids") or [])
            specific = _specific(ids)
            closed_by = sorted(set(superseded_by.get(nid, [])))
            touched_by: list[dict[str, Any]] = []
            for other in notes:
                oid = other.get("note_id")
                if oid == nid or _stamp(other) <= stamp:
                    continue
                shared = specific & _specific(note_tokens.get(oid, set()))
                if shared:
                    touched_by.append(
                        {"note_id": oid, "path": other.get("path"), "shared": sorted(shared)}
                    )
            for sid, entry in touch.items():
                if not _specific(entry["ids"]) & specific:
                    continue
                if entry["at"] and stamp and entry["at"] <= stamp:
                    continue
                hit = {
                    "session_id": sid,
                    "at": entry["at"],
                    "shared": sorted(_specific(entry["ids"]) & specific),
                }
                if not any(t.get("session_id") == sid for t in touched_by):
                    touched_by.append(hit)
            rows.append(
                {
                    "note_id": nid,
                    "claim_id": claim.get("claim_id"),
                    "path": note.get("path"),
                    "created_at": stamp,
                    "text": claim.get("text", ""),
                    "ids": sorted(ids),
                    "specific_ids": sorted(specific),
                    "closed_by": closed_by,
                    "touched_by": touched_by,
                }
            )
    return {
        "held": rows,
        "unmatchable": [r for r in rows if not r["specific_ids"]],
        "closed": [r for r in rows if r["closed_by"]],
        "touched": [r for r in rows if not r["closed_by"] and r["touched_by"]],
        "open": [r for r in rows if not r["closed_by"] and not r["touched_by"]],
        "notes": len(notes),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--open-only", action="store_true", help="list only holds with no candidate")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    notes, reads = load(args.root)
    report = build(notes, reads)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0

    held = report["held"]
    print("held claims (reading_held)")
    print(f"  notes                : {report['notes']}")
    print(f"  held claims          : {len(held)}")
    print(f"  closed by supersedes : {len(report['closed'])}")
    print(f"  later note/session touches the same IDs : {len(report['touched'])}")
    print(f"  no candidate at all  : {len(report['open'])}")
    print(f"  of which the held text mentions no material/record ID (matching impossible) : "
          f"{len(report['unmatchable'])}")
    print("")
    print("  註: 「候補」は保留が閉じたという判定ではありません。保留の文に現れる台帳 ID を、")
    print("      後のノートや read_log が触っている、という機械的な事実だけを示します。")
    print("      極性（閉じた／閉じていない）は機械では判定していません。")
    print("")

    rows = report["open"] if args.open_only else report["closed"] + report["touched"]
    if not rows:
        print("  （該当なし）")
        return 0
    for row in rows[: args.limit]:
        mark = "closed" if row["closed_by"] else "touched"
        print(f"[{mark}] {row['note_id']}  {row['claim_id']}")
        print(f"    at : {row['created_at'][:10]}  {row['path']}")
        print(f"    ids: {', '.join(row['specific_ids']) or '（素材・記録の ID なし）'}")
        text = row["text"].replace("\n", " ")
        print(f"    「{text[:96]}{'…' if len(text) > 96 else ''}」")
        if row["closed_by"]:
            print(f"    closed_by : {', '.join(row['closed_by'])}")
        for other in row["touched_by"][:3]:
            label = other.get("note_id") or other.get("session_id")
            print(f"    touched_by: {label}  shared {', '.join(other['shared'])}")
        print("")
    if len(rows) > args.limit:
        print(f"  ... {len(rows) - args.limit} more (--limit)")
    print("  Nothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
