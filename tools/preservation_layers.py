#!/usr/bin/env python3
"""Measure the three preservation layers of the read_log (stdlib only).

The 2026-11-13 close-reading report ("The Class of Allowed Transformations")
splits what the archive preserves into three layers:

  layer 1 (exposure)   ``used_as_context`` -- the record was in the context of a
                       session, but nothing was done to it.
  layer 2 (work)       ``interpreted`` / ``reinterpreted`` / ``summarized`` /
                       ``quoted`` / ``counted`` / ``contested`` -- something was
                       done to the record.
  layer 3 (re-execution)
                       a work row whose note names *another* record (an id that
                       is not the row's own target) **and** carries a
                       disagreement or re-reading marker.  Only this layer
                       records that a judgement contradicted, re-scored or
                       replaced a *previous* judgement.

Why layer 3 is separate: the report's pre-registered prediction P1 treated the
reading kinds as a contact/work split and predicted that contact would exceed
45% of all rows.  It did not (33.9%), because the kinds do not encode whether
anything was actually done.  ``interpreted`` alone is 3,146 rows, but only a
small fraction of them name another record.  Layer 3 was added *after* that
miss, and the report says so; this tool exists so the post-hoc number is at
least reproducible.

Usage:
  python3 tools/preservation_layers.py
  python3 tools/preservation_layers.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_io  # noqa: E402

EXPOSURE = {"used_as_context", "absorbed", "received"}
WORK = {"interpreted", "reinterpreted", "summarized", "quoted", "counted", "contested"}

# An id anywhere in the note body.  We only need to know whether the note names
# *some* record other than its own target, so the prefix set is deliberately
# broad; a false positive here inflates layer 3, which the report exposes.
ID_RE = re.compile(r"\b(?:MAT|NOTE|HYP|FRG|SES|SESSION|EVL|Q|MOT)-[0-9]{8}-[0-9a-z]{6}\b|\bQ-[0-9]{3}\b")
# Looser variant: the id prefixes the earlier hand count used (no date required).
LOOSE_ID_RE = re.compile(r"\b(?:MAT|NOTE|HYP|FRG|SES|EVL|Q)-")
# Disagreement / re-reading markers (English + Japanese).
NEG_RE = re.compile(
    r"contested|disagree|refut|reject|contradict|wrong|mistaken|supersed|"
    r"overstat|understat|誤り|異議|反論|否定|矛盾|撤回|行き過ぎ|言い過ぎ"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--census",
        action="store_true",
        help="also report the materials/errata/notes figures the report cites",
    )
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument(
        "--loose",
        action="store_true",
        help="accept any id-shaped token (prefix without a date) as naming another "
        "record; the strict default requires a full dated id or Q-nnn",
    )
    args = ap.parse_args()

    root = Path(args.root)
    base = root / "state" / "read_log.jsonl"
    data, problems = ledger_io.load_collections({"read_log": (base, "read_id")}, root=root)
    records = list(data.get("read_log", {}).values())
    if problems:
        for p in problems:
            print(f"WARN: {p}", file=sys.stderr)

    kinds = Counter()
    layer = Counter()
    layer3_rows = []
    named_other = Counter()

    for r in records:
        kind = r.get("reading") or ""
        kinds[kind] += 1
        note = r.get("note") or ""
        own = (r.get("target") or {}).get("id") or ""
        finder = LOOSE_ID_RE if args.loose else ID_RE
        others = {i for i in finder.findall(note) if i != own}
        if others:
            named_other[kind] += 1

        if kind in EXPOSURE:
            layer["1_exposure"] += 1
        elif kind in WORK:
            if others and NEG_RE.search(note):
                layer["3_reexecution"] += 1
                layer3_rows.append(r)
            else:
                layer["2_work"] += 1
        else:
            layer["unclassified"] += 1

    total = len(records)
    out = {
        "total": total,
        "kinds": dict(kinds.most_common()),
        "layers": dict(layer),
        "share": {k: round(v / total, 4) for k, v in layer.items()} if total else {},
        "named_other_record": dict(named_other.most_common()),
        "contested_naming_other": named_other.get("contested", 0),
    }
    if args.census:
        out["census"] = census(root)

    if args.json:
        print(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        print(f"read_log rows: {total}")
        print("\nlayers:")
        for k in ("1_exposure", "2_work", "3_reexecution", "unclassified"):
            v = layer.get(k, 0)
            print(f"  {k:<16} {v:>6}  {100.0 * v / total:5.2f}%" if total else f"  {k}")
        print("\nby reading kind (rows naming another record / total):")
        for k, v in kinds.most_common():
            print(f"  {k:<16} {v:>6}  ({named_other.get(k, 0)} name another record)")
        if args.census:
            c = out["census"]
            print(f"\nmaterials: {c['materials_total']}")
            for k, v in c["verification_status"].items():
                print(f"  {k:<22} {v:>5}")
            print(f"\nerrata: {c['errata_total']}")
            for k, v in c["errata_check_kind"].items():
                print(f"  {k:<22} {v:>5}")
            print(f"\nnotes: {c['notes_total']}")
            print(f"  with supersedes        {c['notes_supersedes']:>5}")
            print(f"  claims total           {c['claims_total']:>5}")
            print(f"  claims kind=retraction {c['claims_retraction']:>5}")
            for k, v in c["claims_kind"].items():
                print(f"    {k:<20} {v:>5}")
    return 0


SPECS = [
    ("materials", "material_id"),
    ("errata", "errata_id"),
    ("notes", "note_id"),
]


def census(root: Path) -> dict:
    """Counts the report cites, from the ledgers themselves."""
    specs = {}
    for name, id_key in SPECS:
        base = root / "state" / f"{name}.jsonl"
        if base.exists() or ledger_io.shard_dir(base).is_dir():
            specs[name] = (base, id_key)
    data, errors = ledger_io.load_collections(specs, root=root)
    if errors:
        print("WARN: " + "; ".join(errors[:5]), file=sys.stderr)

    mats = list(data.get("materials", {}).values())
    vstat = Counter()
    for m in mats:
        v = (m.get("verification") or {}).get("status") or "(absent)"
        vstat[v] += 1

    err = list(data.get("errata", {}).values())
    ekind = Counter()
    for e in err:
        ekind[((e.get("check") or {}).get("kind")) or "(absent)"] += 1

    notes = list(data.get("notes", {}).values())
    supersedes = sum(1 for n in notes if n.get("supersedes"))
    ckind = Counter()
    ctotal = 0
    for n in notes:
        for c in n.get("claims") or []:
            ctotal += 1
            ckind[c.get("kind") or "(absent)"] += 1

    return {
        "materials_total": len(mats),
        "verification_status": dict(vstat.most_common()),
        "errata_total": len(err),
        "errata_check_kind": dict(ekind.most_common(10)),
        "notes_total": len(notes),
        "notes_supersedes": supersedes,
        "claims_total": ctotal,
        "claims_retraction": ckind.get("retraction", 0),
        "claims_kind": dict(ckind.most_common()),
    }


if __name__ == "__main__":
    raise SystemExit(main())
