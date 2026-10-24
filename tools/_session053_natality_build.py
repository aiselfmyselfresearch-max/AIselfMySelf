#!/usr/bin/env python3
"""Build the SESSION-20261024-227ac3 ledger rows (natality, infancy, upbringing, education).

Writes to per-session shards only; the frozen ``state/*.jsonl`` bases are never
touched (see docs/parallel-work.md).  Run with ``--write``.  Standard library
only.  The material summaries live in ``_session053_natality_data*.py`` and are
editorial summaries (【編者による要約】) or reproducible audit measurements
(【実測】), never verbatim quotations presented as full original texts.
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
from _session053_natality_data import (  # noqa: E402
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

# 75 relation IDs minted with tools/new_id.py REL --count 75 (2026-10-24).
RELATION_IDS = [
    "REL-20261024-b24dcf", "REL-20261024-b7cc33", "REL-20261024-af1381",
    "REL-20261024-ed7e7d", "REL-20261024-d7865c", "REL-20261024-700e6f",
    "REL-20261024-c6b488", "REL-20261024-4105f9", "REL-20261024-076799",
    "REL-20261024-b3ae49", "REL-20261024-4fc5f0", "REL-20261024-45c553",
    "REL-20261024-e2705e", "REL-20261024-f3243f", "REL-20261024-650b0c",
    "REL-20261024-bebe8c", "REL-20261024-ac85a9", "REL-20261024-5b5417",
    "REL-20261024-23b0cf", "REL-20261024-dcd5c0", "REL-20261024-c1f502",
    "REL-20261024-8d589d", "REL-20261024-17bb47", "REL-20261024-8792f4",
    "REL-20261024-85d072", "REL-20261024-52e67b", "REL-20261024-427c4b",
    "REL-20261024-f31304", "REL-20261024-8ca9a1", "REL-20261024-cdd0a4",
    "REL-20261024-49d1d1", "REL-20261024-c32aca", "REL-20261024-317d5e",
    "REL-20261024-d0f5cf", "REL-20261024-71a810", "REL-20261024-4de1ab",
    "REL-20261024-7bcbf9", "REL-20261024-d931b3", "REL-20261024-c3e8f9",
    "REL-20261024-a63d6b", "REL-20261024-2619c7", "REL-20261024-763ea0",
    "REL-20261024-5fe384", "REL-20261024-664ef4", "REL-20261024-779938",
    "REL-20261024-f54e14", "REL-20261024-a503dd", "REL-20261024-f1f18f",
    "REL-20261024-875133", "REL-20261024-4bdf54", "REL-20261024-cf7254",
    "REL-20261024-2d668b", "REL-20261024-3f5783", "REL-20261024-bf7ee6",
    "REL-20261024-4a0423", "REL-20261024-55e6d4", "REL-20261024-672054",
    "REL-20261024-c6e5f3", "REL-20261024-3ae62a", "REL-20261024-9d956d",
    "REL-20261024-afebc8", "REL-20261024-53d047", "REL-20261024-76640a",
    "REL-20261024-e76020", "REL-20261024-fe9a6a", "REL-20261024-e0f99b",
    "REL-20261024-5b5b7e", "REL-20261024-faffa6", "REL-20261024-1040a5",
    "REL-20261024-90744d", "REL-20261024-5f7c27", "REL-20261024-ed758f",
    "REL-20261024-17a0cb", "REL-20261024-1b0ef5", "REL-20261024-43d51d",
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
            "evidence_record_id": f"EVD-{mid}",
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
            "notes": note + " 答えを閉じない。語形の0回を能力・意識・経験の不在の判定に変換しない。",
        }
        for qid, text, note in QUESTIONS
    ]


def relation_records() -> list[dict]:
    relations: list[dict] = []
    if len(MATERIAL_NOTES) != len(ALL_ITEMS):
        raise ValueError(f"MATERIAL_NOTES={len(MATERIAL_NOTES)} != ALL_ITEMS={len(ALL_ITEMS)}")
    expected_total = (
        len(ALL_ITEMS)
        + len(MATERIAL_PAIRS)
        + len(MOTIF_LINKS)
        + len(QUESTIONS)
        + len(EXISTING_QUESTION_LINKS)
    )
    if expected_total != len(RELATION_IDS):
        raise ValueError(f"expected {expected_total} relation IDs, have {len(RELATION_IDS)}")

    ids = iter(RELATION_IDS)

    # 47: material -> motif
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
    # 12: material <-> material (new or existing)
    for left_id, right_id, rtype, note in MATERIAL_PAIRS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "material", "id": left_id},
                "relation_type": rtype,
                "right": {"type": "material", "id": right_id},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 6: motif -> existing motifs
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
    # 5: existing question -> new motif
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
