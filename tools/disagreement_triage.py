#!/usr/bin/env python3
"""Sort double-reading disagreements into what needs adjudication and what does not.

Why this exists (2026-11-21)
----------------------------
``tools/double_reading.py`` counts every session pair whose ``read_log.reading``
categories differ (1,848 of 2,615 pairs on 2026-11-21).  Most of those pairs are
not disagreements about the material at all: one session *quoted* the source
while another *reinterpreted* it -- both acts can be true of the same text.  A
count that mixes those with genuine disputes cannot say which reading was
right, and adjudicating all of them would invent conflicts that were never
claimed.

This tool separates three shapes, using only the ``reading`` categories of the
two rows:

* **explicit_dispute** — one side is ``contested``.  A session wrote down that
  it disputes an earlier reading.  These are the pairs where "which reading is
  right" has a determinate answer and needs one: adjudicate them.
* **revision** — one side is ``reinterpreted`` (and neither is ``contested``).
  The reinterpreter claims to read the source differently; whether the two
  readings actually contradict each other is not visible from the categories
  and must be judged from the notes.
* **coexisting_acts** — everything else (``quoted`` vs ``interpreted``,
  ``counted`` vs ``summarized``, ...).  Both acts can hold at once; no
  adjudication is implied.

Honesty limits, in the tool's own words:

* The classes are **category shapes, not verdicts**.  A ``contested`` note can
  be wrong.  Two sessions in ``coexisting_acts`` can still hold contradictory
  claims in their notes; this tool reads categories only and will not find
  those.  Its purpose is to bound the adjudication queue, not to replace
  reading the notes.
* The queue it prints is where a human (or a later session) must actually read
  both notes and, when they conflict, the source.

Usage::

    python3 tools/disagreement_triage.py                  # summary + dispute queue
    python3 tools/disagreement_triage.py --material MAT-… # the paired readings side by side
    python3 tools/disagreement_triage.py --json

Read-only: it never writes to the ledger.  Numbers are meant to be quoted with
the command.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import double_reading  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

CLASS_EXPLICIT = "explicit_dispute"
CLASS_REVISION = "revision"
CLASS_COEXISTING = "coexisting_acts"


def pair_class(reading_a: str, reading_b: str) -> str:
    """Classify one disagreeing session pair by its reading categories."""
    pair = {reading_a, reading_b}
    if "contested" in pair:
        return CLASS_EXPLICIT
    if "reinterpreted" in pair:
        return CLASS_REVISION
    return CLASS_COEXISTING


def triage(materials: dict, read_log: dict, limit: int = 20) -> dict:
    per = double_reading.material_readings(read_log)
    multi: dict[str, list[dict]] = {}
    for mid, rows in per.items():
        sessions = {r.get("session_id") for r in rows if isinstance(r.get("session_id"), str)}
        if len(sessions) >= 2:
            multi[mid] = rows

    pair_counts: collections.Counter = collections.Counter()
    material_rows: list[dict] = []
    for mid, rows in multi.items():
        by_session: dict[str, dict] = {}
        for row in rows:
            sid = row.get("session_id")
            if isinstance(sid, str) and sid not in by_session:
                by_session[sid] = row
        session_rows = list(by_session.values())
        counts = {CLASS_EXPLICIT: 0, CLASS_REVISION: 0, CLASS_COEXISTING: 0}
        for a, b in itertools.combinations(session_rows, 2):
            if a.get("reading") == b.get("reading"):
                continue
            cls = pair_class(str(a.get("reading")), str(b.get("reading")))
            counts[cls] += 1
            pair_counts[cls] += 1
        if not any(counts.values()):
            continue
        mat = materials.get(mid) or {}
        material_rows.append(
            {
                "material_id": mid,
                "title": str(mat.get("title") or "")[:70],
                "sessions": len(by_session),
                "explicit_dispute_pairs": counts[CLASS_EXPLICIT],
                "revision_pairs": counts[CLASS_REVISION],
                "coexisting_pairs": counts[CLASS_COEXISTING],
                "readings": sorted({str(r.get("reading")) for r in rows}),
            }
        )
    material_rows.sort(
        key=lambda r: (
            -r["explicit_dispute_pairs"],
            -r["revision_pairs"],
            -r["coexisting_pairs"],
            r["material_id"],
        )
    )
    with_dispute = sum(1 for r in material_rows if r["explicit_dispute_pairs"])
    return {
        "disagreeing_materials": len(material_rows),
        "materials_with_explicit_dispute": with_dispute,
        "pair_classes": dict(pair_counts),
        "queue": material_rows[:limit],
        "all_rows": material_rows,
    }


def render(result: dict) -> str:
    lines = [
        "# disagreement triage",
        "",
        f"- 食い違いのある素材: **{result['disagreeing_materials']:,}**",
        f"- うち明示的な異議（contested を含む対）のある素材: "
        f"**{result['materials_with_explicit_dispute']:,}**",
        f"- 対のクラス: explicit_dispute **{result['pair_classes'].get(CLASS_EXPLICIT, 0):,}** / "
        f"revision **{result['pair_classes'].get(CLASS_REVISION, 0):,}** / "
        f"coexisting_acts **{result['pair_classes'].get(CLASS_COEXISTING, 0):,}**",
        "",
        "> これは reading カテゴリの形の分類であり、判定ではない。",
        "> contested の側が正しいとは限らず、coexisting_acts の注記が矛盾していない保証もない。",
        "> 裁定（どちらの読みが成り立つか）は、各対の note を読んでから下す。",
        "",
        "## 裁定待ちキュー（explicit_dispute 優先）",
        "",
        "| 素材 | 対 | explicit | revision | coexisting | 読み | タイトル |",
        "| :--- | ---: | ---: | ---: | ---: | :--- | :--- |",
    ]
    for row in result["queue"]:
        lines.append(
            f"| `{row['material_id']}` | {row['sessions']} | {row['explicit_dispute_pairs']} | "
            f"{row['revision_pairs']} | {row['coexisting_pairs']} | "
            f"{','.join(row['readings'])} | {row['title']} |"
        )
    return "\n".join(lines) + "\n"


def show_material(material_id: str, read_log: dict) -> int:
    per = double_reading.material_readings(read_log)
    rows = per.get(material_id)
    if not rows:
        print(f"no manual reading recorded for {material_id}")
        return 1
    by_session: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        sid = row.get("session_id")
        if isinstance(sid, str):
            by_session[sid].append(row)
    for sid, group in by_session.items():
        for row in group:
            print(f"== {sid}  {row.get('created_at')}  {row.get('reading')}")
            print(f"   read_id: {row.get('read_id')}")
            print(f"   note: {row.get('note', '')}")
        print()
    print("# 対のクラス")
    sessions = list(by_session)
    for a, b in itertools.combinations(sessions, 2):
        readings = {by_session[a][0].get("reading"), by_session[b][0].get("reading")}
        if len(readings) == 2:
            print(f"  {a} × {b}: {pair_class(*sorted(str(r) for r in readings))}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--material", help="print every manual reading recorded for one material")
    args = parser.parse_args()
    root = Path(args.root)
    materials, read_log = double_reading.load(root)

    if args.material:
        return show_material(args.material, read_log)

    result = triage(materials, read_log, limit=args.limit)
    if args.json:
        payload = {k: v for k, v in result.items() if k != "all_rows"}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
