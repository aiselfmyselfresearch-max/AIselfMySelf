#!/usr/bin/env python3
"""Build the SESSION-20261024-24f052 ledger rows (clothing, cloth, mending, dress).

Writes to per-session shards only; the frozen ``state/*.jsonl`` bases are never
touched (see docs/parallel-work.md).  Run with ``--write``.  Standard library
only.  The material summaries live in ``_session052_clothing_data*.py`` and are
editorial summaries (【編者による要約】), never verbatim quotations.

Rows produced:
  materials 46 (36 literary/philosophical, 9 research, 1 project trace)
  motifs     1 (MOTIF-20261024-7274b5)
  questions  5
  relations 70 (46 material→motif, 10 material↔material, 5 motif↔motif,
                5 question→motif, 4 existing question→motif)
  sessions   1
  read_log  46 (one per new material)
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
from _session052_clothing_data1 import ITEMS_1  # noqa: E402
from _session052_clothing_data2 import ITEMS_2  # noqa: E402
from _session052_clothing_data3 import (  # noqa: E402
    CHECKED_AT,
    COMMIT,
    EXISTING_QUESTION_LINKS,
    HUMAN_DIRECTION,
    ITEMS_3,
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

ALL_ITEMS = ITEMS_1 + ITEMS_2 + ITEMS_3

# 80 relation IDs minted with tools/new_id.py REL --count 80 (2026-10-24).
RELATION_IDS = [
    "REL-20261024-2326c1", "REL-20261024-3b84d8", "REL-20261024-1be904",
    "REL-20261024-ed75e1", "REL-20261024-c09f8b", "REL-20261024-b834f8",
    "REL-20261024-bb0cb5", "REL-20261024-76ceec", "REL-20261024-995522",
    "REL-20261024-a1f3bf", "REL-20261024-41dcca", "REL-20261024-93f684",
    "REL-20261024-d6ca4c", "REL-20261024-65af21", "REL-20261024-e08050",
    "REL-20261024-de20af", "REL-20261024-ddf4f5", "REL-20261024-7e30b2",
    "REL-20261024-2da219", "REL-20261024-5b2c15", "REL-20261024-0c9579",
    "REL-20261024-7446bf", "REL-20261024-f1e2a9", "REL-20261024-8b8a0d",
    "REL-20261024-4e611b", "REL-20261024-4bf700", "REL-20261024-556906",
    "REL-20261024-752432", "REL-20261024-c4f9de", "REL-20261024-2790cd",
    "REL-20261024-b710fa", "REL-20261024-217912", "REL-20261024-d26431",
    "REL-20261024-b30782", "REL-20261024-8274fc", "REL-20261024-04a993",
    "REL-20261024-95c45c", "REL-20261024-d782e9", "REL-20261024-e71270",
    "REL-20261024-6d4fb2", "REL-20261024-40eeaa", "REL-20261024-6e9a8f",
    "REL-20261024-44400f", "REL-20261024-c754d9", "REL-20261024-367c46",
    "REL-20261024-174c74", "REL-20261024-d50afa", "REL-20261024-f169ac",
    "REL-20261024-ae929b", "REL-20261024-26c9c2", "REL-20261024-6e1d75",
    "REL-20261024-36f941", "REL-20261024-b6ba16", "REL-20261024-390bcb",
    "REL-20261024-911830", "REL-20261024-f20b76", "REL-20261024-9281bd",
    "REL-20261024-9af1e1", "REL-20261024-ba901e", "REL-20261024-a816f6",
    "REL-20261024-eb8374", "REL-20261024-830bd0", "REL-20261024-f2d7cb",
    "REL-20261024-8b124b", "REL-20261024-f9900e", "REL-20261024-c63738",
    "REL-20261024-77d50a", "REL-20261024-ba0002", "REL-20261024-d003dd",
    "REL-20261024-d558b7", "REL-20261024-e11002", "REL-20261024-648dbb",
    "REL-20261024-9d43e9", "REL-20261024-0bc879", "REL-20261024-c9a5be",
    "REL-20261024-7f3e03", "REL-20261024-3dd39c", "REL-20261024-991593",
    "REL-20261024-44721a", "REL-20261024-a9ef3b",
]

# 46 read_log IDs minted with tools/new_id.py READ --count 50 (2026-10-24).
READ_IDS = [
    "READ-20261024-b0d50c", "READ-20261024-36a0f2", "READ-20261024-7e8164",
    "READ-20261024-2c7796", "READ-20261024-e28a2a", "READ-20261024-3f4d70",
    "READ-20261024-e09991", "READ-20261024-ccd7f7", "READ-20261024-72d4be",
    "READ-20261024-52c66e", "READ-20261024-9fdc19", "READ-20261024-19bc5f",
    "READ-20261024-5c3c34", "READ-20261024-fa30a6", "READ-20261024-826e39",
    "READ-20261024-75f37f", "READ-20261024-c27b24", "READ-20261024-a9769f",
    "READ-20261024-ef2f2b", "READ-20261024-0d95e5", "READ-20261024-25b0cc",
    "READ-20261024-42f99b", "READ-20261024-273e72", "READ-20261024-5aa73d",
    "READ-20261024-4064ee", "READ-20261024-164f7f", "READ-20261024-f802b4",
    "READ-20261024-f2b5d9", "READ-20261024-19d80d", "READ-20261024-113273",
    "READ-20261024-e24871", "READ-20261024-b06a27", "READ-20261024-46c608",
    "READ-20261024-3a3c81", "READ-20261024-ef2e09", "READ-20261024-1d23ff",
    "READ-20261024-80ef0d", "READ-20261024-7f433d", "READ-20261024-428fab",
    "READ-20261024-99642e", "READ-20261024-2abd17", "READ-20261024-9f1c63",
    "READ-20261024-322ea7", "READ-20261024-d2e135", "READ-20261024-9e1568",
    "READ-20261024-53ac52",
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
            "version_note": item["vnote"],
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
                "vnote2",
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
    for item in ALL_ITEMS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "material", "id": item["mid"]},
                "relation_type": "echo",
                "right": {"type": "motif", "id": MOTIF_ID},
                "note": item["rel"],
                "created_at": CHECKED_AT,
            }
        )
    # 10: material <-> material
    for left_mid, right_mid, rtype, note in MATERIAL_PAIRS:
        relations.append(
            {
                "relation_id": next(ids),
                "left": {"type": "material", "id": left_mid},
                "relation_type": rtype,
                "right": {"type": "material", "id": right_mid},
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    # 5: new motif -> existing motifs
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
    extra = list(ids)
    if extra:
        print(f"note: {len(extra)} minted relation IDs left unused", file=sys.stderr)
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


def read_log_records() -> list[dict]:
    rows = []
    for read_id, item in zip(READ_IDS, ALL_ITEMS):
        if item["kind"] == "project_trace":
            reading = "counted"
            note = "監査ツールの出力そのものを、資料と同じ層で読み直した。"
        elif item["kind"] == "research_excerpt":
            reading = "summarized"
            note = "題名・著者・年・主要な主張を照合し、編者要約を作った。本文は未取得。"
        else:
            reading = "summarized"
            note = "内部知識から編者要約を作り、四層（一節／解釈／考え／感じたこと）で読んだ。原典は未閲覧。"
        rows.append(
            {
                "read_id": read_id,
                "session_id": SESSION_ID,
                "target": {"type": "material", "id": item["mid"]},
                "reading": reading,
                "note": note,
                "created_at": CHECKED_AT,
            }
        )
    return rows


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
        "read_log": (read_log_records(), "read_log"),
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
