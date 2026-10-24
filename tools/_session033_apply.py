# -*- coding: utf-8 -*-
"""Apply SESSION-033 records to the state ledgers (append-only, guarded).

Run from repo root:  python3 tools/_session033_apply.py
Fails loudly on any ID collision so it cannot double-append.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from _session033_data1 import MATERIALS as M1  # noqa: E402
from _session033_data2 import MATERIALS as M2  # noqa: E402
from _session033_data3 import MATERIALS as M3  # noqa: E402
from _session033_data4 import FRAGMENTS, MOTIF, QUESTIONS, RELATIONS, SESSION  # noqa: E402

STATE = ROOT / "state"

ALL_MATERIALS = M1 + M2 + M3


def load(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(path: Path, records: list[dict], id_key: str) -> None:
    existing = {r[id_key] for r in load(path)}
    for record in records:
        if record[id_key] in existing:
            raise SystemExit(f"COLLISION in {path.name}: {record[id_key]} already exists; aborting")
    with path.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"appended {len(records):>3} -> {path.relative_to(ROOT)}")


def main() -> int:
    # Materials
    append(STATE / "materials.jsonl", ALL_MATERIALS, "material_id")

    # Motif
    append(STATE / "motifs.jsonl", [MOTIF], "motif_id")

    # Questions
    append(STATE / "questions.jsonl", QUESTIONS, "question_id")

    # Fragments
    append(STATE / "fragments.jsonl", FRAGMENTS, "fragment_id")

    # Relations, auto-numbered after the current maximum REL id.
    relations_path = STATE / "relations.jsonl"
    existing_relations = load(relations_path)
    max_n = max(int(r["relation_id"].split("-")[1]) for r in existing_relations)
    new_relations = []
    for index, (left_id, left_type, rtype, right_id, right_type, note) in enumerate(RELATIONS, start=1):
        new_relations.append(
            {
                "relation_id": f"REL-{max_n + index:03d}",
                "left": {"type": left_type, "id": left_id},
                "relation_type": rtype,
                "right": {"type": right_type, "id": right_id},
                "note": note,
                "created_at": "2026-10-24",
            }
        )
    append(relations_path, new_relations, "relation_id")

    # Session
    append(STATE / "sessions.jsonl", [SESSION], "session_id")

    counts = {
        "materials": len(load(STATE / "materials.jsonl")),
        "motifs": len(load(STATE / "motifs.jsonl")),
        "questions": len(load(STATE / "questions.jsonl")),
        "fragments": len(load(STATE / "fragments.jsonl")),
        "relations": len(load(STATE / "relations.jsonl")),
        "sessions": len(load(STATE / "sessions.jsonl")),
    }
    print("new totals:", json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
