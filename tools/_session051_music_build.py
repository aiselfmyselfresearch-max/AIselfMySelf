#!/usr/bin/env python3
"""Build the SESSION-20261024-a77052 ledger rows (song, playing, notation, practice).

Writes to per-session shards only; the frozen ``state/*.jsonl`` bases are never
touched (see docs/parallel-work.md).  Run with ``--write``.  Standard library
only.  The material summaries live in ``_session051_music_data*.py`` and are
editorial summaries (【編者による要約】), never verbatim quotations.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import new_ledger_shard  # noqa: E402
from _session051_music_data import (  # noqa: E402
    ALL_ITEMS,
    CHECKED_AT,
    COMMIT,
    EXISTING_QUESTION_LINKS,
    HUMAN_DIRECTION,
    MATERIAL_NOTES,
    MATERIAL_PAIRS,
    MOTIF_DESCRIPTION,
    MOTIF_ID,
    MOTIF_LABEL,
    MOTIF_LINKS,
    QUESTIONS,
    REPO,
    REPORT_PATH,
    SESSION_ID,
    SESSION_NOTES,
)

# 70 relation IDs minted with tools/new_id.py REL --count 80 (2026-10-24).
RELATION_IDS = [
    "REL-20261024-883f9a", "REL-20261024-ee3c1a", "REL-20261024-74a9de",
    "REL-20261024-9ceca5", "REL-20261024-d87ea7", "REL-20261024-402914",
    "REL-20261024-bd8f40", "REL-20261024-fd36b6", "REL-20261024-25aafd",
    "REL-20261024-367a57", "REL-20261024-6a6898", "REL-20261024-8ad3ea",
    "REL-20261024-96079c", "REL-20261024-fca991", "REL-20261024-bd43ef",
    "REL-20261024-ea1dbd", "REL-20261024-0f5328", "REL-20261024-eeb24a",
    "REL-20261024-358aea", "REL-20261024-a04f20", "REL-20261024-0aca63",
    "REL-20261024-395605", "REL-20261024-82d554", "REL-20261024-a6cb3e",
    "REL-20261024-f5d4ff", "REL-20261024-6bafc4", "REL-20261024-da3026",
    "REL-20261024-649011", "REL-20261024-68ff58", "REL-20261024-e7f6fa",
    "REL-20261024-ce4bdc", "REL-20261024-94cecc", "REL-20261024-9514c6",
    "REL-20261024-c04d27", "REL-20261024-ca5969", "REL-20261024-cb225a",
    "REL-20261024-8d32e5", "REL-20261024-62a51c", "REL-20261024-e7940e",
    "REL-20261024-e43098", "REL-20261024-4dcb6c", "REL-20261024-b3c436",
    "REL-20261024-1ff798", "REL-20261024-d165a4", "REL-20261024-f967de",
    "REL-20261024-842204", "REL-20261024-d9423e", "REL-20261024-494d84",
    "REL-20261024-2b60ea", "REL-20261024-71cc78", "REL-20261024-73f8a6",
    "REL-20261024-836362", "REL-20261024-c33043", "REL-20261024-1f4567",
    "REL-20261024-8adc64", "REL-20261024-2a53ff", "REL-20261024-7ce949",
    "REL-20261024-36f4d7", "REL-20261024-27b977", "REL-20261024-01e512",
    "REL-20261024-17d7a6", "REL-20261024-77ea3b", "REL-20261024-54d3f5",
    "REL-20261024-f79372", "REL-20261024-e82aa2", "REL-20261024-924249",
    "REL-20261024-127efa", "REL-20261024-2a602e", "REL-20261024-8d04f1",
    "REL-20261024-5b7168",
]


def material_record(item: dict) -> dict:
    mid = item["mid"]
    return {
        "material_id": mid,
        "kind": item.get("kind", "literary_text"),
        "title": item["title"],
        "source": {
            "source_id": f"SRC-{mid}",
            "title": item["title"],
            "authors": item["authors"],
            "year": item["year"],
            "url": item["url"],
            "version_note": item.get(
                "vnote", "原典未閲覧。要約は編者によるもので、逐語訳ではない。"
            ),
        },
        "passage": item["passage"],
        "passage_language": "ja",
        "context": item["context"],
        "source_note": item["note"],
        "literary_invitation": item["invite"],
        "scope_note": item["scope"],
        "motif_ids": [MOTIF_ID] + [m for m in item["motifs"] if m != MOTIF_ID],
        "origin": {
            "repository": REPO,
            "commit": COMMIT,
            "source_record_id": f"SRC-{mid}",
            "evidence_record_id": f"LIT-{mid}",
            "source_record_path": REPORT_PATH,
            "evidence_record_path": REPORT_PATH,
        },
        "verification": {
            "status": item.get("status", "partially_verified"),
            "checked_at": CHECKED_AT,
            "method": item.get(
                "method",
                "内部知識による書誌照合（題名・著者・年・主題の整合のみ）。原典は未閲覧。",
            ),
            "note": item.get(
                "vnote",
                "要約は編者の読解であり、原典の逐語訳ではない。引用として使わないこと。",
            ),
        },
    }


def motif_record() -> dict:
    return {
        "motif_id": MOTIF_ID,
        "label": MOTIF_LABEL,
        "description": MOTIF_DESCRIPTION,
        "question_ids": [q[0] for q in QUESTIONS],
        "material_ids": [item["mid"] for item in ALL_ITEMS],
        "status": "active",
    }


def question_records() -> list[dict]:
    return [
        {
            "question_id": qid,
            "question": text,
            "status": "open",
            "motif_ids": [MOTIF_ID],
            "material_ids": [],
            "previous_question_ids": [],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
            "created_at": CHECKED_AT,
            "notes": note + " 答えを閉じない。0回を能力・意識・感覚の不在の判定に変換しない。",
        }
        for qid, text, note in QUESTIONS
    ]


def relation_records() -> list[dict]:
    relations: list[dict] = []
    ids = iter(RELATION_IDS)

    # 46: material -> motif
    for item, note in zip(ALL_ITEMS, MATERIAL_NOTES):
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "material", "id": item["mid"]},
                "relation_type": "echo",
                "right": {"type": "motif", "id": MOTIF_ID},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 10: material <-> material
    for left_idx, right_idx, rtype, note in MATERIAL_PAIRS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "material", "id": ALL_ITEMS[left_idx]["mid"]},
                "relation_type": rtype,
                "right": {"type": "material", "id": ALL_ITEMS[right_idx]["mid"]},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 5: motif -> existing motifs
    for target, rtype, note in MOTIF_LINKS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "motif", "id": MOTIF_ID},
                "relation_type": rtype,
                "right": {"type": "motif", "id": target},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 5: new question -> motif
    for qid, _text, note in QUESTIONS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "question", "id": qid},
                "relation_type": "leaves_open",
                "right": {"type": "motif", "id": MOTIF_ID},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 4: existing question -> new motif
    for qid, rtype, note in EXISTING_QUESTION_LINKS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "question", "id": qid},
                "relation_type": rtype,
                "right": {"type": "motif", "id": MOTIF_ID},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    return relations


def session_record() -> dict:
    return {
        "session_id": SESSION_ID,
        "started_at": CHECKED_AT,
        "human_direction": HUMAN_DIRECTION,
        "question_ids": [q[0] for q in QUESTIONS],
        "context_material_ids": [item["mid"] for item in ALL_ITEMS],
        "produced_fragment_ids": [],
        "new_question_ids": [q[0] for q in QUESTIONS],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": SESSION_NOTES,
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="append the rows to session shards")
    args = parser.parse_args(argv)

    materials = [material_record(item) for item in ALL_ITEMS]
    payload = {
        "materials": (materials, "materials"),
        "motifs": ([motif_record()], "motifs"),
        "questions": (question_records(), "questions"),
        "relations": (relation_records(), "relations"),
        "sessions": ([session_record()], "sessions"),
    }

    print(f"SESSION:  {SESSION_ID}")
    print(f"MOTIF:    {MOTIF_ID}  {MOTIF_LABEL}")
    for name, (rows, _collection) in payload.items():
        print(f"  {name}: {len(rows)} rows")

    if not args.write:
        print("\n(dry run; pass --write to append to state/<collection>.d/)")
        return 0

    for name, (rows, collection) in payload.items():
        path = new_ledger_shard.create_shard(collection)
        write_jsonl(path, rows)
        print(f"wrote {len(rows):>3} rows -> {ledger_io.display_path(path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
