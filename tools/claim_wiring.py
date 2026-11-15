#!/usr/bin/env python3
"""How far the meaning layer reaches the belief layer (stdlib only).

A note's ``claims`` say what a session changed.  A hypothesis is what the archive
believes.  On 2026-11-15 there were 1,984 claims and 30 hypotheses, and only 194
of the claims (9.8%) named a hypothesis; among the 676 claims that say a reading
was revised or retracted, 112 named one (16.6%).  The rest changed the text
without changing the distribution — which is why the archive can grow without
learning (readings/2026-11-15-where-the-learning-actually-happens.md §2).

This tool only counts.  It does not judge whether a claim is true, and a low
ratio is not a failure of inquiry: many readings revise how a source is cited
and touch no hypothesis at all, which is what ``no_hypothesis`` is for.  What the
ratio makes visible is the case in between — a claim that says a judgment changed
while naming no judgment.

Usage:
  python3 tools/claim_wiring.py                 # the table
  python3 tools/claim_wiring.py --json
  python3 tools/claim_wiring.py --check         # the rule only (see below)

``--check`` delegates to ``validate_seed.check_claim_wiring`` so the rule lives in
one place: from 2026-11-16, a ``reading_revised`` or ``retraction`` claim must name
a hypothesis or set ``no_hypothesis: true`` (docs/registers.md §2).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
GATED_KINDS = ("reading_revised", "retraction")
TEXT_LIMIT = 60


def load_notes(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Load the notes ledger (base plus shards) keyed by note_id."""
    base = Path(root) / "state" / "notes.jsonl"
    collections, errors = ledger_io.load_collections(
        {"notes": (base, "note_id")},
        root=Path(root),
    )
    if errors:
        raise SystemExit("notes ledger unreadable: " + "; ".join(errors[:3]))
    return collections.get("notes", {})


def _claim_rows(notes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for note_id, record in notes.items():
        claims = record.get("claims")
        if not isinstance(claims, list):
            continue
        for position, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            rows.append({"note_id": note_id, "position": position, "claim": claim})
    return rows


def wiring_report(notes: dict[str, dict[str, Any]], *, limit: int = 5) -> dict[str, Any]:
    """Count claims per kind and how many name a hypothesis."""
    by_kind: dict[str, int] = {}
    wired_by_kind: dict[str, int] = {}
    notes_with_claims = 0
    total = 0
    wired_total = 0
    declared_none = 0
    revision_claims = 0
    revision_wired = 0
    unwired: list[dict[str, Any]] = []

    for note_id, record in notes.items():
        claims = record.get("claims")
        if not isinstance(claims, list) or not claims:
            continue
        notes_with_claims += 1
        for position, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            kind = claim.get("kind") or "unknown"
            total += 1
            by_kind[kind] = by_kind.get(kind, 0) + 1
            named = bool(claim.get("hypothesis_ids"))
            if named:
                wired_total += 1
                wired_by_kind[kind] = wired_by_kind.get(kind, 0) + 1
            elif claim.get("no_hypothesis") is True:
                declared_none += 1
            if kind in GATED_KINDS:
                revision_claims += 1
                if named:
                    revision_wired += 1
                elif claim.get("no_hypothesis") is not True and len(unwired) < limit:
                    unwired.append({
                        "note_id": note_id,
                        "claim_id": claim.get("claim_id") or f"claims[{position}]",
                        "kind": kind,
                        "text": (claim.get("text") or "")[:TEXT_LIMIT],
                    })

    return {
        "notes": len(notes),
        "notes_with_claims": notes_with_claims,
        "total_claims": total,
        "wired_total": wired_total,
        "coverage": round(wired_total / total, 4) if total else 0.0,
        "by_kind": dict(sorted(by_kind.items())),
        "wired_by_kind": dict(sorted(wired_by_kind.items())),
        "revision_claims": revision_claims,
        "revision_wired": revision_wired,
        "revision_coverage": round(revision_wired / revision_claims, 4) if revision_claims else 0.0,
        "declared_no_hypothesis": declared_none,
        "unwired_examples": unwired,
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "=== claim -> hypothesis wiring (2026-11-15 reading §2) ===",
        f"notes: {report['notes']} ({report['notes_with_claims']} carry claims) / "
        f"claims: {report['total_claims']}",
        f"claims naming a hypothesis: {report['wired_total']} "
        f"({report['coverage']*100:.1f}%) / declared no_hypothesis: {report['declared_no_hypothesis']}",
        f"revision+retraction claims: {report['revision_claims']}, naming a hypothesis: "
        f"{report['revision_wired']} ({report['revision_coverage']*100:.1f}%)",
        "",
        f"{'kind':<18}{'claims':>8}{'names HYP':>11}",
    ]
    for kind, count in report["by_kind"].items():
        lines.append(f"{kind:<18}{count:>8}{report['wired_by_kind'].get(kind, 0):>11}")
    if report["unwired_examples"]:
        lines.append("")
        lines.append("unwired revision claims (examples; not errors before 2026-11-16):")
        for row in report["unwired_examples"]:
            lines.append(f"  - {row['note_id']} / {row['claim_id']} [{row['kind']}] {row['text']}")
    lines.append("")
    lines.append(
        "この比は達成目標ではありません。読み替えが仮説に触れないことはあります（そのときは no_hypothesis）。"
        "見たいのは、判定を変えたと言いながら判定を名指さない claim です（docs/registers.md §2）。"
    )
    return "\n".join(lines)


def check(root: Path = ROOT) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import validate_seed

    collections, load_errors = ledger_io.load_collections(
        {"notes": (Path(root) / "state" / "notes.jsonl", "note_id")},
        root=Path(root),
    )
    errors: list[str] = list(load_errors)
    validate_seed.check_claim_wiring(collections.get("notes", {}), errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: every post-cutoff revision claim names a hypothesis or declares no_hypothesis")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--limit", type=int, default=5, help="unwired examples to show")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.check:
        return check(args.root)

    report = wiring_report(load_notes(args.root), limit=max(args.limit, 0))
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
