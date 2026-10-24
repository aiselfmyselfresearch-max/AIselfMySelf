#!/usr/bin/env python3
"""Field-separated lexical audit for revision/erasure inquiry.

Counts exact surface patterns, not semantic annotations. A zero means only that
the pattern is absent from that field; it does not prove that the practice,
idea, or a synonym is absent. No historical ledgers are modified.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = OrderedDict([
    ("誤・間違・過ち（接辞を含む）", r"誤|間違|過ち"),
    ("訂正・修正（厳密）", r"訂正|修正"),
    ("校訂・校勘", r"校訂|校勘"),
    ("書き換え・書き直し・推敲", r"書き換|書き直|書き改め|推敲"),
    ("抹消・削除・消去・塗りつぶし（狭義）", r"抹消|削除|消去|塗りつぶ"),
])
EXPECTED_SESSION_MATERIALS = (
    [f"MAT-LIT-{i:03d}" for i in range(320, 354)]
    + [f"MAT-EVD-20261024-{i:02d}" for i in range(72, 82)]
    + ["MAT-TRC-012"]
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def count_field(rows: list[dict], field: str, pattern: str) -> tuple[int, int, list[str]]:
    regex = re.compile(pattern)
    occurrences = 0
    matched: list[str] = []
    for row in rows:
        hits = regex.findall(row.get(field, ""))
        if hits:
            occurrences += len(hits)
            matched.append(row["fragment_id"])
    return occurrences, len(matched), matched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-session-034", action="store_true",
        help="also require all 45 SESSION-034 material IDs and their report entries",
    )
    args = parser.parse_args()

    fragments = read_jsonl(ROOT / "state" / "fragments.jsonl")
    chars = sum(len(row.get("text", "")) for row in fragments)
    print(f"fragments={len(fragments)} chars={chars} fields=text,editor_note")
    print("category\tbody_occurrences/body_fragments\tnote_occurrences/note_fragments\tbody_ids\tnote_ids")
    for label, pattern in PATTERNS.items():
        body = count_field(fragments, "text", pattern)
        note = count_field(fragments, "editor_note", pattern)
        print(
            f"{label}\t{body[0]}/{body[1]}\t{note[0]}/{note[1]}"
            f"\t{','.join(body[2]) or '-'}\t{','.join(note[2]) or '-'}"
        )
    print("NOTE: exact-pattern counts only; zero occurrences do not prove absence of a practice or idea.")

    if args.check_session_034:
        materials = read_jsonl(ROOT / "state" / "materials.jsonl")
        material_ids = {row["material_id"] for row in materials}
        missing = [mid for mid in EXPECTED_SESSION_MATERIALS if mid not in material_ids]
        report_path = ROOT / "readings" / "2026-10-24-session-034-revision-and-erasure.md"
        report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
        report_missing = [mid for mid in EXPECTED_SESSION_MATERIALS if f"### {mid}" not in report]
        errors = []
        if missing:
            errors.append("missing materials: " + ", ".join(missing))
        if report_missing:
            errors.append("missing close readings: " + ", ".join(report_missing))
        required_fields = ("**一節**", "**解釈**", "**考え**", "**感じたこと**")
        for field in required_fields:
            if report.count(field) != len(EXPECTED_SESSION_MATERIALS):
                errors.append(f"{field}: expected {len(EXPECTED_SESSION_MATERIALS)}, found {report.count(field)}")
        if errors:
            print("SESSION-034 CHECK: FAIL")
            for error in errors:
                print("  " + error)
            return 1
        print(f"SESSION-034 CHECK: PASS ({len(EXPECTED_SESSION_MATERIALS)} materials, each with four reading fields)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
