#!/usr/bin/env python3
"""Measure the archive's admission gate. A mirror, not a score.

`state/materials.jsonl` has two fields that decide what a source becomes once it
enters the archive:

  literary_invitation  the required sentence that hands the source on
  passage              the excerpt itself

Neither field is constrained by `schema/material.schema.json` beyond
`minLength: 1`. This tool reports what the archive has actually written there,
so that the gap between the rule and the habit can be seen.

Why this exists (SESSION-026):
  Before SESSION-026, all 77 literary_invitation values ended in a question
  form ("か。" / "か？"), although the schema asked only for one character. The
  gate was not in the rule but in the hand of the writer. The same session also
  found that 32 of 77 passages contained no quotation mark at all: a field
  named "passage" held paraphrase without a marker in about four cases out of
  ten.

Usage:
  python3 tools/gate_audit.py
  python3 tools/gate_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

MATERIALS = ROOT / "state" / "materials.jsonl"
FRAGMENTS = ROOT / "state" / "fragments.jsonl"
QUESTIONS = ROOT / "state" / "questions.jsonl"

ID_KEYS = {
    "materials.jsonl": "material_id",
    "fragments.jsonl": "fragment_id",
    "questions.jsonl": "question_id",
}

QUESTION_TAIL = re.compile(r"か[。？]\s*$")
QUOTE_CHARS = "「」『』\"'“”‘’"

TAIL_KINDS = [
    ("のか。", re.compile(r"のか。\s*$")),
    ("だろうか。", re.compile(r"だろうか。\s*$")),
    ("か。", re.compile(r"か。\s*$")),
    ("か？", re.compile(r"か？\s*$")),
]


def load(path: Path, *, base_only: bool = False, exclude: str | None = None) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    if base_only or path.name not in ID_KEYS:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, ID_KEYS[path.name], errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def measure(materials: list[dict[str, Any]], fragments: list[dict[str, Any]],
            questions: list[dict[str, Any]]) -> dict[str, Any]:
    frag_ids = {m for f in fragments for m in f.get("material_ids", [])}
    question_ids = {m for q in questions for m in q.get("material_ids", [])}
    ids = {row["material_id"] for row in materials}

    tails = {label: 0 for label, _ in TAIL_KINDS}
    ends_in_question = 0
    no_quote = 0
    marked_summary = 0
    marked_original = 0
    per_kind: dict[str, dict[str, int]] = {}

    for row in materials:
        invitation = row.get("literary_invitation", "")
        passage = row.get("passage", "")
        ends = bool(QUESTION_TAIL.search(invitation.strip()))
        ends_in_question += ends
        for label, pattern in TAIL_KINDS:
            if pattern.search(invitation.strip()):
                tails[label] += 1
                break
        has_quote = any(ch in passage for ch in QUOTE_CHARS)
        no_quote += not has_quote
        marked_summary += "要約" in passage
        marked_original += "【原文】" in passage

        kind = row.get("kind", "unknown")
        bucket = per_kind.setdefault(kind, {"count": 0, "ends_in_question": 0, "no_quote": 0})
        bucket["count"] += 1
        bucket["ends_in_question"] += ends
        bucket["no_quote"] += not has_quote

    return {
        "materials": len(materials),
        "fragments": len(fragments),
        "ends_in_question": ends_in_question,
        "tails": tails,
        "no_quote_in_passage": no_quote,
        "marked_summary": marked_summary,
        "marked_original": marked_original,
        "referenced_by_fragment": len(frag_ids & ids),
        "referenced_by_question": len(question_ids & ids),
        "referenced_by_either": len((frag_ids | question_ids) & ids),
        "orphan_materials": sorted(ids - frag_ids - question_ids),
        "per_kind": per_kind,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="print the measurement as JSON")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/*.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    kw = {"base_only": args.base_only, "exclude": args.exclude_shard}
    materials = load(MATERIALS, **kw)
    if not materials:
        print(f"error: no materials found at {MATERIALS.relative_to(ROOT)}", file=sys.stderr)
        return 1
    result = measure(materials, load(FRAGMENTS, **kw), load(QUESTIONS, **kw))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True))
        return 0

    total = result["materials"]
    print("=== The admission gate of state/materials.jsonl ===")
    print(f"Materials : {total}")
    print()
    print("literary_invitation ending in a question form")
    print(f"  {result['ends_in_question']}/{total}")
    for label, count in result["tails"].items():
        if count:
            print(f"    {label:<10} {count}")
    print()
    print("passage without any quotation mark (paraphrase, possibly unmarked)")
    print(f"  {result['no_quote_in_passage']}/{total}")
    print(f"  marked with 【要約】/「要約」 : {result['marked_summary']}")
    print(f"  marked with 【原文】         : {result['marked_original']}")
    print()
    print("where the sources are referenced")
    print(f"  by a fragment           : {result['referenced_by_fragment']}/{total}")
    print(f"  by a question           : {result['referenced_by_question']}/{total}")
    print(f"  by a fragment or question: {result['referenced_by_either']}/{total}")
    if result["orphan_materials"]:
        print(f"  referenced by neither   : {', '.join(result['orphan_materials'])}")
    print()
    print("by kind")
    for kind in sorted(result["per_kind"]):
        bucket = result["per_kind"][kind]
        print(f"  {kind:<18} n={bucket['count']:<4} question-tail={bucket['ends_in_question']:<4} no-quote={bucket['no_quote']}")
    print()
    print("These are counts of what is written, not a quality score.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
