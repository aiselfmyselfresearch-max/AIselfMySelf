#!/usr/bin/env python3
"""Append an explicit ``declined`` trace for a context material (stdlib only).

Why this tool exists
--------------------
Layer 2 of ``read_log`` asks every session to account for the materials in its
``context_material_ids``: either a hand-written reading, or a
``未読の選択:`` line in ``sessions.notes``.  The second path lives inside the
session row, and the session row is append-only.  A session that fails to write
the line before the row is committed therefore has no repair path at all.

This tool provides one: a ``read_log`` row with ``reading: "declined"`` and a
reason.  It is a *negative* trace, not a reading claim.  It does not replace the
layer-1 contact row; it is an additional row for a pair that already has one.
The checker counts it as an excuse, and ``recorded_by_session_id`` names the
session that recorded the decline.  That field is how a later audit can say
"this is a post-hoc excuse, not the original session's note" without rewriting
the original row.

The design deliberately does **not** retroactively decline every old gap.  The
tool refuses a pair that already has a hand-written reading, and it refuses a
material that was never in the target session's context list.  A reason is
required.  A later session may decline a pair only if it can state why; the
provenance is visible in the row.

Usage
-----
  python3 tools/read_log_decline.py --session SESSION-... --material MAT-... \
      --reason "文脈に置いたが、本セッションの精読対象ではない"
  python3 tools/read_log_decline.py --session SESSION-... --material MAT-... \
      --recorded-by SESSION-... --shard state/read_log.d/2026-11-14-....jsonl \
      --reason "..."

Without ``--shard`` the tool creates a new read-log shard for today.  Prefer
appending to a same-day shard when the directory is at its soft file limit
(``docs/parallel-work.md`` step 8-2).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import new_id  # noqa: E402
import read_log_backfill  # noqa: E402


def _append_rows(path: Path, rows: list[dict]) -> None:
    """Append rows without re-serialising any existing line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def decline(
    *,
    root: Path,
    session_id: str,
    material_ids: list[str],
    reason: str,
    recorded_by: str,
    shard: Path,
    created_at: str | None = None,
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    """Validate and append declined rows. Returns (written, messages)."""
    messages: list[str] = []
    if not reason.strip():
        return 0, ["error: --reason must not be empty"]
    sessions, read_log = read_log_backfill.load(root)
    if session_id not in sessions:
        return 0, [f"error: unknown session {session_id}"]
    if recorded_by not in sessions:
        return 0, [f"error: unknown recorded-by session {recorded_by}"]

    target = sessions[session_id]
    context = {
        material_id
        for material_id in (target.get("context_material_ids") or [])
        if isinstance(material_id, str)
    }
    hand = read_log_backfill.handwritten_pairs(read_log)
    contact = read_log_backfill.covered_pairs(read_log)
    already_declined = read_log_backfill.declined_pairs(read_log)
    taken = new_id.existing_ids("READ", root=root)

    rows: list[dict] = []
    for material_id in material_ids:
        if material_id not in context:
            messages.append(
                f"skip {material_id}: not in {session_id}.context_material_ids "
                "(declined is only for materials the session put in context)"
            )
            continue
        pair = (session_id, material_id)
        if pair in hand:
            messages.append(
                f"skip {material_id}: a hand-written reading already exists; declining it would overwrite a reading"
            )
            continue
        if pair not in contact:
            messages.append(
                f"skip {material_id}: no layer-1 contact row; run tools/read_log_backfill.py --write first "
                "(declined excuses layer 2, it does not stand in for contact)"
            )
            continue
        if pair in already_declined:
            messages.append(f"skip {material_id}: already declined")
            continue
        read_id = new_id.mint(
            "READ", day=(created_at or date.today().isoformat()).replace("-", "")[:8], taken=taken
        )
        taken.add(read_id)
        row = {
            "read_id": read_id,
            "session_id": session_id,
            "target": {"type": "material", "id": material_id},
            "reading": "declined",
            "note": reason.strip(),
            "recorded_by_session_id": recorded_by,
            "created_at": created_at or date.today().isoformat(),
        }
        rows.append(row)

    if dry_run:
        messages.append(f"dry run: would write {len(rows)} row(s) to {shard}")
        return len(rows), messages

    if rows:
        _append_rows(shard, rows)
        messages.append(f"wrote {len(rows)} declined row(s) to {shard}")
    else:
        messages.append("wrote nothing")
    return len(rows), messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append read_log 'declined' rows for context materials (append-only repair path)."
    )
    parser.add_argument("--session", required=True, help="target session whose context pair is declined")
    parser.add_argument(
        "--material", action="append", default=[], help="material ID (repeatable)"
    )
    parser.add_argument("--reason", required=True, help="why the material was not read")
    parser.add_argument(
        "--recorded-by",
        default=None,
        help="session recording the decline (default: same as --session)",
    )
    parser.add_argument(
        "--shard",
        type=Path,
        default=None,
        help="read_log shard to append to (default: new shard for today)",
    )
    parser.add_argument("--created-at", default=None, help="YYYY-MM-DD (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="validate but do not write")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if not args.material:
        print("error: at least one --material is required", file=sys.stderr)
        return 2

    shard = args.shard
    if shard is None:
        import new_ledger_shard

        shard = new_ledger_shard.shard_path("read_log", root=args.root)
    shard = shard if shard.is_absolute() else args.root / shard

    written, messages = decline(
        root=args.root,
        session_id=args.session,
        material_ids=args.material,
        reason=args.reason,
        recorded_by=args.recorded_by or args.session,
        shard=shard,
        created_at=args.created_at,
        dry_run=args.dry_run,
    )
    for message in messages:
        print(message)
    return 0 if written >= 0 and not any(m.startswith("error:") for m in messages) else 1


if __name__ == "__main__":
    raise SystemExit(main())
