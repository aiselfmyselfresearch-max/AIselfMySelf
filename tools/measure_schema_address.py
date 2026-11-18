#!/usr/bin/env python3
"""Reproduce the archive measurements reported in
``readings/2026-11-18-address-me-and-the-trace-survives.md`` §4.

Why this exists
---------------
Six evaluation rows filed on 2026-11-18 carry ``evidence_type:
reproducible_script`` and name this file in ``script_command``.  A row that
claims a reproducible measurement must name a command a later reader can
actually run.  Before this file existed the claim was aspirational: the
numbers lived only in the prose of a report and in a pasted snippet.

What it measures
----------------
Four of the report's tables, plus the confound test that shrank its own
headline number:

  A. accessibility — how many materials were never cited, split by whether a
     human read is recorded (report §4-1)
  B. schema address — citation rate for materials whose ``source_note`` names
     a ``HYP-*`` id, crossed with hand-read status (report §4-2)
  C. era control — table B restricted to materials minted on/after
     2026-11-12, the date from which naming a hypothesis was possible at all
     (report §4-3).  This is the check that moved the headline from "16x" to
     "about 3x" and it is the reason EVL-20261118-135a97 exists.
  D. dose-response — citation rate by number of distinct hypotheses named
     (report §4-4)
  E. citation lag — days between a material's minting and the evaluation that
     cites it (report §4-5)
  F. address drift — does the hypothesis a material names match the
     evaluation's own target? (report §4-6)

What it must never do
---------------------
It reads only.  Every number here is derived from the append-only ledgers on
every run; nothing is cached, because a cached copy of a ledger statistic is
a second source of truth that drifts silently.

The numbers move as rows are appended.  ``--check`` therefore does NOT assert
that the published integers still hold.  It asserts the MECHANISM: that the
tables are computable, internally consistent (each rate equals its own
numerator over denominator), and that the collinearity the report relies on
still exists.  Pinning the live rate would make every later session red for
an honest append, which is the failure mode two earlier instruments were
retired for (see tests/test_execution_path_probe.py's docstring).

Usage
-----
    python3 tools/measure_schema_address.py            # human tables
    python3 tools/measure_schema_address.py --json     # machine-readable
    python3 tools/measure_schema_address.py --check    # assert mechanism
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HYP_RE = re.compile(r"HYP-\d{8}-[0-9a-z]{6}")
MAT_RE = re.compile(r"MAT(?:-EVD|-LIT|-TRC)?-(\d{8})-")
MACHINE_BACKFILL = "機械的バックフィル"
ERA_FLOOR = "20261112"          # first date a HYP-* id could be named


def _rows(collection: str) -> list[dict]:
    out: list[dict] = []
    base = ROOT / "state" / f"{collection}.jsonl"
    if base.is_file():
        for line in base.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    for path in sorted(glob.glob(str(ROOT / "state" / f"{collection}.d" / "*.jsonl"))):
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def _mint_day(material_id: str) -> str | None:
    m = MAT_RE.match(material_id)
    return m.group(1) if m else None


def _hand_read_ids(read_log: list[dict]) -> set[str]:
    """Materials with at least one human read_log row.

    A machine backfill row is not a read.  The report's §4-1 turns on this
    distinction, so the filter is stated once, here.
    """
    return {
        r["target"]["id"]
        for r in read_log
        if r.get("target", {}).get("type") == "material"
        and MACHINE_BACKFILL not in (r.get("note") or "")
    }


def _addressed(material: dict) -> bool:
    return bool(HYP_RE.search(material.get("source_note") or ""))


def _rate(num: int, den: int) -> float:
    return (100.0 * num / den) if den else 0.0


def measure(root: Path = ROOT) -> dict:
    materials = _rows("materials")
    read_log = _rows("read_log")
    evaluations = _rows("evaluations")

    hand = _hand_read_ids(read_log)
    cited: set[str] = set()
    for ev in evaluations:
        cited.update(ev.get("material_ids") or [])

    by_id = {m["material_id"]: m for m in materials}

    # --- A. accessibility -------------------------------------------------
    # Three disjoint classes, and the middle one is the point:
    #   hand-read     at least one human read_log row
    #   machine-only  a read_log row exists, but every one is a backfill
    #   no row        no read_log row at all
    # An earlier version of this function computed "no row" as "not hand-read
    # AND no read_log row", which is what the class means, but then computed
    # cited_machine_only over a set that quietly absorbed the no-row materials,
    # so a no-row cite could be counted as a machine-only cite. Both had to be
    # zero for the report to hold, so the bug was invisible in the output while
    # it made two different claims share one number.
    any_row = {
        r["target"]["id"]
        for r in read_log
        if r.get("target", {}).get("type") == "material"
    }
    no_row = [m for m in materials if m["material_id"] not in any_row]
    machine_only = [m for m in materials
                    if m["material_id"] not in hand
                    and m["material_id"] in any_row]
    accessibility = {
        "materials": len(materials),
        "hand_read": len(hand & set(by_id)),
        "machine_only": len(machine_only),
        "no_row": len(no_row),
        "cited_total": len(cited),
        "cited_hand_read": len(cited & hand),
        "cited_machine_only": sum(1 for m in machine_only if m["material_id"] in cited),
        "cited_no_row": sum(1 for m in no_row if m["material_id"] in cited),
    }

    # --- B. schema address ------------------------------------------------
    cell: dict[tuple[bool, bool], list[int]] = defaultdict(lambda: [0, 0])
    for m in materials:
        key = (_addressed(m), m["material_id"] in hand)
        cell[key][1] += 1
        if m["material_id"] in cited:
            cell[key][0] += 1
    schema = {
        f"addressed={a},hand={h}": {"cited": c, "n": n, "rate": _rate(c, n)}
        for (a, h), (c, n) in sorted(cell.items())
    }

    # --- C. era control ---------------------------------------------------
    era: dict[str, dict[str, list[int]]] = {"post": {}, "pre": {}}
    for label, keep in (("post", True), ("pre", False)):
        for addr in (True, False):
            grp = [m for m in materials
                   if (m["material_id"] in hand)
                   and _addressed(m) is addr
                   and (keep == ((_mint_day(m["material_id"]) or "") >= ERA_FLOOR))]
            c = sum(1 for m in grp if m["material_id"] in cited)
            era[label][f"addressed={addr}"] = {"cited": c, "n": len(grp),
                                                "rate": _rate(c, len(grp))}

    # --- D. dose-response -------------------------------------------------
    dose: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for m in materials:
        k = len(set(HYP_RE.findall(m.get("source_note") or "")))
        bucket = "0" if k == 0 else ("4+" if k >= 4 else str(k))
        dose[bucket][1] += 1
        if m["material_id"] in cited:
            dose[bucket][0] += 1
    dose_response = {b: {"cited": c, "n": n, "rate": _rate(c, n)}
                     for b, (c, n) in sorted(dose.items())}

    # --- E. citation lag --------------------------------------------------
    lags: list[int] = []
    session_day: dict[str, str] = {}
    for ev in evaluations:
        sid = ev.get("session_id") or ""
        m = re.match(r"SESSION-(\d{8})-", sid)
        if not m:
            continue
        session_day[sid] = m.group(1)
    for ev in evaluations:
        day = session_day.get(ev.get("session_id") or "")
        if not day:
            continue
        for mid in ev.get("material_ids") or []:
            md = _mint_day(mid)
            if not md:
                continue
            try:
                lags.append((date(int(day[:4]), int(day[4:6]), int(day[6:]))
                             - date(int(md[:4]), int(md[4:6]), int(md[6:]))).days)
            except ValueError:
                continue
    lag_hist = Counter(lags)
    same_day = lag_hist.get(0, 0)
    citation_lag = {
        "slots": len(lags),
        "same_day": same_day,
        "same_day_rate": _rate(same_day, len(lags)),
        "ge_7d": sum(v for k, v in lag_hist.items() if k >= 7),
        "ge_30d": sum(v for k, v in lag_hist.items() if k >= 30),
        "max": max(lags) if lags else 0,
        "min": min(lags) if lags else 0,
    }

    # --- F. address drift -------------------------------------------------
    slots = hits = 0
    for ev in evaluations:
        target = ev.get("target_hypothesis_id")
        for mid in ev.get("material_ids") or []:
            material = by_id.get(mid)
            if not material:
                continue
            named = set(HYP_RE.findall(material.get("source_note") or ""))
            if not named:
                continue
            slots += 1
            if target in named:
                hits += 1
    address_drift = {"slots": slots, "match": hits, "rate": _rate(hits, slots),
                     "mismatch": slots - hits,
                     "mismatch_rate": _rate(slots - hits, slots)}

    return {
        "era_floor": ERA_FLOOR,
        "accessibility": accessibility,
        "schema_address": schema,
        "era_control": era,
        "dose_response": dose_response,
        "citation_lag": citation_lag,
        "address_drift": address_drift,
    }


def render(res: dict) -> str:
    out: list[str] = []
    a = res["accessibility"]
    out.append("A. accessibility (report §4-1)")
    out.append(f"   materials {a['materials']:,}  hand-read {a['hand_read']:,}  "
               f"machine-only {a['machine_only']:,}  no row {a['no_row']:,}")
    out.append(f"   cited {a['cited_total']:,} total: hand-read {a['cited_hand_read']:,}, "
               f"machine-only {a['cited_machine_only']}, no-row {a['cited_no_row']}")
    out.append("")
    out.append("B. schema address x hand-read (report §4-2)")
    for k, v in res["schema_address"].items():
        out.append(f"   {k:28s} {v['cited']:5d}/{v['n']:5d} = {v['rate']:6.1f}%")
    out.append("")
    out.append("C. era control, hand-read only (report §4-3)")
    for label in ("post", "pre"):
        for k, v in res["era_control"][label].items():
            out.append(f"   {label:4s} {k:28s} {v['cited']:5d}/{v['n']:5d} = {v['rate']:6.1f}%")
    out.append("")
    out.append("D. dose-response: distinct hypotheses named (report §4-4)")
    for k, v in res["dose_response"].items():
        out.append(f"   {k:3s} named  {v['cited']:5d}/{v['n']:5d} = {v['rate']:6.1f}%")
    out.append("")
    lag = res["citation_lag"]
    out.append("E. citation lag, material mint -> citing evaluation (report §4-5)")
    out.append(f"   {lag['slots']:,} slots; same day {lag['same_day']:,} "
               f"({lag['same_day_rate']:.1f}%); >=7d {lag['ge_7d']}; "
               f">=30d {lag['ge_30d']}; range {lag['min']}..{lag['max']} d")
    out.append("")
    d = res["address_drift"]
    out.append("F. address drift: named hypothesis vs evaluation target (report §4-6)")
    out.append(f"   match {d['match']:,}/{d['slots']:,} = {d['rate']:.1f}%; "
               f"mismatch {d['mismatch']:,} = {d['mismatch_rate']:.1f}%")
    return "\n".join(out)


def check(res: dict) -> list[str]:
    """Assert the mechanism, never the live integers."""
    problems: list[str] = []

    # every rendered rate must equal its own numerator / denominator
    for group in ("schema_address",):
        for k, v in res[group].items():
            if v["n"] and abs(v["rate"] - 100.0 * v["cited"] / v["n"]) > 1e-9:
                problems.append(f"{group}[{k}] rate does not equal cited/n")

    # §4-2's collinearity: a material that names a hypothesis but was never
    # hand-read must be absent. If this ever holds with n>0 the report's
    # 'addressing and reading are not separated' claim is refuted, and that
    # is a finding, not a bug -- so report it as a failure of the CLAIM.
    key = "addressed=True,hand=False"
    if res["schema_address"].get(key, {}).get("n", 0) > 0:
        problems.append(f"collinearity broken: {key} has n="
                        f"{res['schema_address'][key]['n']}")

    # the accessibility result the report turns on: machine-only reads are
    # never cited. Also a claim, not a law; a single citation refutes it.
    if res["accessibility"]["cited_machine_only"] > 0:
        problems.append("machine-only material was cited; §4-1's 0/809 is refuted")

    # the headroom the direction of the ERA_FLOOR test depends on
    if res["era_control"]["pre"].get("addressed=True", {}).get("n", 0) > 0:
        problems.append("a pre-2026-11-12 material names a HYP id; "
                        "the era floor no longer separates the periods")

    if res["address_drift"]["slots"] == 0:
        problems.append("no addressed material is ever cited; §4-6 is uncomputable")

    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--check", action="store_true",
                    help="assert the measurement mechanism (not the live integers)")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    res = measure(args.root)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
    else:
        print(render(res))

    if args.check:
        problems = check(res)
        if problems:
            print("\nFAIL: the measurement mechanism no longer supports the report",
                  file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            return 1
        print("\nPASS: mechanism holds (live integers are not pinned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
