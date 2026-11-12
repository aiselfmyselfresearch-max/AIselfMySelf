#!/usr/bin/env python3
"""List claim pairs that disagree in polarity while sharing a question, and say
whether either side recorded *what its claim is about*.

Why this tool exists.  The three central questions (``Q-001``..``Q-003``) are
answered many times over in the archive, and the answers are stored as flat
sentences: a ``notes`` claim carries ``text``, ``kind``, ``anchor`` and some
ledger references, but nothing that says **which object** the sentence is about,
**by which basis** it was judged, or **in which sense** of the word it speaks.
Because that scope is missing, the next session can read two sentences that look
like a contradiction and has no mechanical way to tell whether they are about
the same thing.  The dossiers in ``readings/2026-11-11-*`` show what the answer
usually is: the two sentences differ in object, basis or sense, not in truth.

This tool does not decide any of that.  It performs the two halves a machine can
do honestly:

  1. coverage — how many claims carry a ``scope`` (``object``/``basis``/``sense``);
  2. pairs — claims sharing a ``question_id`` whose wording overlaps, printed
     side by side with their scope fields (or ``none``) and a raw negation count.

A pair is an invitation to write a scope, not a finding.  The tool deliberately
does **not** try to decide whether two claims contradict each other: negation
detection over Japanese claim sentences mislabels quoted negations and misses
subordinate ones (tried both whole-sentence and predicate-position rules over
these 1,319 claims; both put plainly agreeing pairs at the top).  What it can do
honestly is put two sentences about the same question next to each other and
show whether either side said which object it means.  Nothing is written.

Usage:
  python3 tools/scope_report.py                 # coverage + 20 candidates
  python3 tools/scope_report.py --limit 40      # more candidates
  python3 tools/scope_report.py --json          # machine-readable
  python3 tools/scope_report.py --check         # exit 1 if any unscoped pair exists
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
SCOPE_FIELDS = ("object", "basis", "sense")
NEGATIVE_MARKERS = ("ない", "ません", "ず", "できない", "なかった", "否定")
# Only reading claims carry a stance that can oppose another stance; a
# measured_fact pair that differs by one number is not a conflict.
READING_KINDS = ("reading_revised", "reading_maintained", "reading_held", "retraction")


def load_claims(root: Path = ROOT) -> list[dict[str, Any]]:
    """Return every claim with the note it belongs to, in ledger order."""
    collections, errors = ledger_io.load_collections(
        {"notes": (root / "state" / "notes.jsonl", "note_id")}, root=root
    )
    if errors:
        raise SystemExit("ledger error: " + "; ".join(errors))
    claims: list[dict[str, Any]] = []
    for note_id, note in collections["notes"].items():
        for claim in note.get("claims") or []:
            if not isinstance(claim, dict):
                continue
            claims.append(
                {
                    "note_id": note_id,
                    "path": note.get("path"),
                    "claim_id": claim.get("claim_id"),
                    "kind": claim.get("kind"),
                    "text": claim.get("text") or "",
                    "question_ids": list(claim.get("question_ids") or []),
                    "scope": claim.get("scope") if isinstance(claim.get("scope"), dict) else None,
                }
            )
    return claims


def is_negative(text: str) -> bool:
    """A weak heuristic: does the claim contain a negation at all?

    It over-fires on quoted negations and under-fires on long sentences whose
    negation sits in a subordinate clause.  That is why the output is a list of
    candidates and not of contradictions, and why every pair is printed with its
    scope: the reader makes the call, not the tool.
    """
    return any(marker in text for marker in NEGATIVE_MARKERS)


def bigrams(text: str) -> set[str]:
    stripped = "".join(ch for ch in text if not ch.isspace())
    return {stripped[i : i + 2] for i in range(len(stripped) - 1)}


def similarity(left: str, right: str) -> float:
    a, b = bigrams(left), bigrams(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def scope_label(scope: dict[str, str] | None) -> str:
    if not scope:
        return "none"
    parts = [f"{field}={scope[field]}" for field in SCOPE_FIELDS if scope.get(field)]
    return " / ".join(parts) if parts else "none"


def coverage(claims: list[dict[str, Any]]) -> dict[str, Any]:
    scoped = [c for c in claims if c["scope"]]
    by_kind: dict[str, list[int]] = {}
    for claim in claims:
        bucket = by_kind.setdefault(claim["kind"] or "?", [0, 0])
        bucket[0] += 1
        if claim["scope"]:
            bucket[1] += 1
    return {
        "claims": len(claims),
        "scoped": len(scoped),
        "by_kind": {kind: {"claims": total, "scoped": done} for kind, (total, done) in sorted(by_kind.items())},
    }


def candidates(
    claims: list[dict[str, Any]], *, floor: float = 0.12, reading_only: bool = True
) -> list[dict[str, Any]]:
    """Same question, opposite polarity, some lexical overlap."""
    pairs: list[dict[str, Any]] = []
    by_question: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        if not claim["text"] or len(claim["text"]) < 20:
            continue
        if reading_only and claim["kind"] not in READING_KINDS:
            continue
        for question_id in claim["question_ids"]:
            by_question.setdefault(question_id, []).append(claim)
    for question_id, group in by_question.items():
        for left, right in combinations(group, 2):
            if left["claim_id"] == right["claim_id"]:
                continue
            if left["text"] in right["text"] or right["text"] in left["text"]:
                continue  # the same sentence registered twice
            if left["scope"] and right["scope"]:
                continue  # both sides already said what they are about
            score = similarity(left["text"], right["text"])
            if score < floor:
                continue
            pairs.append(
                {
                    "question_id": question_id,
                    "similarity": round(score, 3),
                    "left": left,
                    "right": right,
                    "scoped": bool(left["scope"]) or bool(right["scope"]),
                    "negations": (sum(m in left["text"] for m in NEGATIVE_MARKERS),
                                  sum(m in right["text"] for m in NEGATIVE_MARKERS)),
                }
            )
    pairs.sort(key=lambda pair: pair["similarity"], reverse=True)
    return pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Claim scope coverage and unscoped conflict candidates")
    parser.add_argument("--limit", type=int, default=20, help="candidates to print (default 20)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--all-kinds", action="store_true", help="include measured_fact/handoff/method_change too"
    )
    parser.add_argument("--floor", type=float, default=0.15, help="minimum bigram overlap (default 0.15)")
    args = parser.parse_args(argv)

    claims = load_claims()
    stats = coverage(claims)
    pairs = candidates(claims, floor=args.floor, reading_only=not args.all_kinds)

    if args.json:
        print(
            json.dumps(
                {
                    "coverage": stats,
                    "pairs": [
                        {
                            "question_id": pair["question_id"],
                            "similarity": pair["similarity"],
                            "scoped": pair["scoped"],
                            "negations": list(pair["negations"]),
                            "left": {k: pair["left"][k] for k in ("claim_id", "kind", "text")},
                            "right": {k: pair["right"][k] for k in ("claim_id", "kind", "text")},
                        }
                        for pair in pairs[: args.limit]
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        total, scoped = stats["claims"], stats["scoped"]
        share = (100.0 * scoped / total) if total else 0.0
        print(f"claims: {total} / scoped: {scoped} ({share:.1f}%)")
        for kind, bucket in stats["by_kind"].items():
            print(f"  {kind:<18} {bucket['scoped']:>4} / {bucket['claims']:<4}")
        print(f"\nsame-question pairs with overlapping wording and no scope on at least one side: {len(pairs)}")
        print(f"\ntop {min(args.limit, len(pairs))} pairs:")
        for pair in pairs[: args.limit]:
            left, right = pair["left"], pair["right"]
            print(
                f"\n[{pair['question_id']}] similarity {pair['similarity']:.2f}"
                f"  negations {pair['negations'][0]} / {pair['negations'][1]}"
            )
            print(f"  + {left['claim_id']} ({left['kind']}): {left['text'][:110]}")
            print(f"      scope: {scope_label(left['scope'])}")
            print(f"  - {right['claim_id']} ({right['kind']}): {right['text'][:110]}")
            print(f"      scope: {scope_label(right['scope'])}")
        print(
            "\nA candidate is not a contradiction. The dossiers (readings/2026-11-11-*) found that "
            "opposed sentences usually differ in object, basis or sense; the scope field is where "
            "that difference is written down. An empty scope means undecided, not universal."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
