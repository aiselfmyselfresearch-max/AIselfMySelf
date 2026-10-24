#!/usr/bin/env python3
"""SESSION-038 renumbering (one-shot, already applied; do not re-run).

The play-and-laughter session was drafted as SESSION-036 on 19e4103.
While its PR was open, two parallel sessions merged into main first
(PR #28 sense-and-medium, PR #29 voice/listening/silence), taking
SESSION-036/037, MOTIF-018, Q-092..096, MAT-LIT-388..423,
MAT-EVD-20261024-90..104, MAT-TRC-014 and REL up to 779.
This script appended the session's records with fresh IDs:

  MAT-LIT-388..421        -> MAT-LIT-424..457
  MAT-EVD-20261024-90..99 -> MAT-EVD-20261024-105..114
  MAT-TRC-014             -> MAT-TRC-015
  MOTIF-018               -> MOTIF-019
  Q-092..096              -> Q-097..101
  REL-723..817            -> REL-780..874
  SESSION-036             -> SESSION-038
  readings/...session-036-play-and-laughter.md
                          -> readings/...session-038-play-and-laughter.md

The audit in MAT-TRC-015 still describes the 40 fragments at the
branch point 19e4103; FRAG-041..043 were added by the parallel
sessions and are not part of that count. Record of the mapping,
kept so the renumbering itself is auditable.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/tmp/s036")

MAP: dict[str, str] = {}
for i in range(34):
    MAP[f"MAT-LIT-{388+i}"] = f"MAT-LIT-{424+i}"
    MAP[f"SRC-LIT-{388+i}"] = f"SRC-LIT-{424+i}"
for i in range(10):
    MAP[f"MAT-EVD-20261024-{90+i}"] = f"MAT-EVD-20261024-{105+i}"
    MAP[f"SRC-EVD-20261024-{90+i}"] = f"SRC-EVD-20261024-{105+i}"
MAP["MAT-TRC-014"] = "MAT-TRC-015"
MAP["SRC-TRC-014"] = "SRC-TRC-015"
MAP["MOTIF-018"] = "MOTIF-019"
for i in range(5):
    MAP[f"Q-09{2+i}"] = f"Q-{97+i:03d}" if 97+i >= 100 else f"Q-0{97+i}"
for i in range(95):
    MAP[f"REL-{723+i}"] = f"REL-{780+i}"
MAP["SESSION-036"] = "SESSION-038"
MAP["session-036-play-and-laughter"] = "session-038-play-and-laughter"

PATTERN = re.compile("|".join(re.escape(k) for k in sorted(MAP, key=len, reverse=True)))

def transform(obj):
    if isinstance(obj, str):
        return PATTERN.sub(lambda m: MAP[m.group(0)], obj)
    if isinstance(obj, list):
        return [transform(v) for v in obj]
    if isinstance(obj, dict):
        return {k: transform(v) for k, v in obj.items()}
    return obj

def append(name, records):
    path = ROOT / "state" / name
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

def main():
    mats = transform(json.loads((SRC / "materials.json").read_text(encoding="utf-8")))
    motif = transform(json.loads((SRC / "motif.json").read_text(encoding="utf-8")))
    questions = transform(json.loads((SRC / "questions.json").read_text(encoding="utf-8")))
    relations = transform(json.loads((SRC / "relations.json").read_text(encoding="utf-8")))
    session = transform(json.loads((SRC / "session.json").read_text(encoding="utf-8")))
    # fix Q mapping edge (Q-100/Q-101 formatting) if needed
    append("materials.jsonl", mats)
    append("motifs.jsonl", motif)
    append("questions.jsonl", questions)
    append("relations.jsonl", relations)
    append("sessions.jsonl", session)
    print(f"appended {len(mats)} materials, motif, {len(questions)} questions, {len(relations)} relations, session SESSION-038")

if __name__ == "__main__":
    main()
