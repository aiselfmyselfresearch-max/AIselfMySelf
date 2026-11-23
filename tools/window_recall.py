#!/usr/bin/env python3
"""Measure what the continuation packet calls a window: shown / named / outside.

Why this tool exists
--------------------
``HYP-20261119-63b6bf`` (有限窓の二重通貨説) says that for an AI whose memory is
a GitHub ledger, what overflows the window "lands in another shard and can be
recalled by a later reading" -- a *reversible* overflow cost, against the
human side's irreversible bodily one.  Seventeen evaluation rows later, the
AI half of that claim had never been measured.  ``EVL-20261122-77b0aa`` says so
in its own summary: 「AI側の『呼び戻し可能』は本セッションの資料では検定して
いない（すべて人間の研究である）」.

The claim is measurable because the window is not a metaphor here.  Two numeric
budgets exist:

* ``tools/size_budget.py`` limits how large each collection may *grow*.  It does
  not narrow what a session can read.
* ``tools/inspect_inquiry.py --material-budget`` (default 16,384 B) limits how
  much of a question's material pool is printed into §3 of the continuation
  packet.  This is the one budget that decides what a session sees.

What the packet does with the remainder is unusually honest: it prints
``予算注記`` naming **every** omitted material id, then says the omission is not
a claim about value.  So the window leaves a *list* of what it left out.  The
question this tool answers is whether that list works as a door.

Three containers, per session
-----------------------------
``shown``    the material's block was printed whole in §3 (``### `MAT-...```).
``named``    the material was named in ``予算注記`` as omitted ("not loaded").
``outside``  the material is in neither; the session was never told it exists.

Crucially the archive has a **second** injection channel: ``sessions.
context_material_ids``.  A read that the window explains and a read that the
context list explains are not the same finding, so every read is cross-
tabulated against both.

What counts as a read
---------------------
Hand-written rows only.  ``used_as_context`` rows are mechanically transferred
from ``sessions.context_material_ids`` by ``tools/read_log_backfill.py``: they
record *contact*, not reading (``prompts/close_reading_report.md``;
``docs/parallel-work.md`` layer 1 / layer 2).  Rows whose note carries 機械 are
dropped for the same reason.  A ``declined`` row is counted, because declining a
material the window put in front of you is still a reading event.

What this tool does NOT claim
-----------------------------
* Absence of a hand-written row is **not** proof of non-reading.  A session
  that read a material and did not log it counts as 0 here.
* Order is not established.  ``context_material_ids`` may have been written
  after the packet; a read row may record preparation before the session
  started.  The tool can say "recorded together", not "caused".
* The windows are reconstructed from ``sessions.dispersal_seed``, so sessions
  with no recorded seed cannot be measured at all.  ``--coverage`` prints that
  share rather than hiding it.
* Counts are not a quality score.

Usage::

    python3 tools/window_recall.py --question Q-001
    python3 tools/window_recall.py --question Q-001 --json
    python3 tools/window_recall.py --coverage
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inspect_inquiry as ii  # noqa: E402

MAT_ID = re.compile(r"MAT-[A-Za-z0-9-]+")
SHOWN_RE = re.compile(r"^### `(MAT-[A-Za-z0-9-]+)`", re.M)
BUDGET_RE = re.compile(r"予算注記[^\n]*")
COUNT_RE = re.compile(r"対話素材 (\d+) 件のうち候補優先順の先頭 (\d+) 件（([\d,]+) B）")
TARGET_RE = re.compile(r"対象：(\S+)")
MECHANICAL = "機械"


def is_mechanical(row: dict) -> bool:
    return MECHANICAL in (row.get("note") or "")


def target_id(row: dict):
    return (row.get("target") or {}).get("id")


def target_type(row: dict):
    return (row.get("target") or {}).get("type")


def build_packet(seed: str) -> str:
    """Run the real packet builder as a subprocess: the tool must not reimplement it."""
    out = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "inspect_inquiry.py"),
         "--packet", "auto", "--seed", seed],
        capture_output=True, text=True, timeout=600,
    )
    if out.returncode != 0:
        raise RuntimeError(f"packet build failed for seed {seed}: {out.stderr[:400]}")
    return out.stdout


def parse_window(text: str = None, seed: str = None) -> dict:
    """Return {'target': qid, 'shown': [...], 'named': [...], 'selfreport': ...}."""
    if text is None:
        text = build_packet(seed)
    head = text.split("\n", 1)[0]
    m = TARGET_RE.search(head)
    target = m.group(1) if m else None
    budget = BUDGET_RE.search(text)
    named = MAT_ID.findall(budget.group(0)) if budget else []
    # de-duplicate, keep order
    seen = set()
    named = [x for x in named if not (x in seen or seen.add(x))]
    shown = []
    for x in SHOWN_RE.findall(text):
        if x not in shown:
            shown.append(x)
    sr = COUNT_RE.search(text)
    selfreport = None
    if sr:
        selfreport = {
            "pool": int(sr.group(1)),
            "shown": int(sr.group(2)),
            "bytes": int(sr.group(3).replace(",", "")),
        }
    return {
        "target": target,
        "shown": shown,
        "named": named,
        "selfreport": selfreport,
        "bytes": len(text.encode("utf-8")),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--question", default="Q-001",
                    help="offered_target_question_id to restrict to (default Q-001)")
    ap.add_argument("--cache-dir", default=None,
                    help="reuse packets already written here instead of rebuilding")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--coverage", action="store_true",
                    help="only report how many sessions can be reconstructed")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    data = ii.load_all()
    sessions = list(data["sessions"].values())
    read_log = list(data["read_log"].values())
    materials = data["materials"]

    seeded = [s for s in sessions if s.get("dispersal_seed")]
    readers = {r.get("session_id") for r in read_log
               if target_type(r) == "material" and not is_mechanical(r)}
    seeded_ids = {s["session_id"] for s in seeded}
    coverage = {
        "sessions_total": len(sessions),
        "sessions_seeded": len(seeded),
        "sessions_seeded_pct": round(100 * len(seeded) / max(1, len(sessions)), 2),
        "sessions_with_handwritten_material_read": len(readers),
        "readers_seeded": len(readers & seeded_ids),
        "readers_seeded_pct": round(
            100 * len(readers & seeded_ids) / max(1, len(readers)), 2),
        "readers_unreconstructable": len(readers - seeded_ids),
    }
    handwritten = [r for r in read_log
                   if target_type(r) == "material" and not is_mechanical(r)]
    coverage["handwritten_material_rows"] = len(handwritten)
    coverage["handwritten_rows_in_unreconstructable_sessions"] = sum(
        1 for r in handwritten if r.get("session_id") not in seeded_ids)
    coverage["handwritten_rows_unreconstructable_pct"] = round(
        100 * coverage["handwritten_rows_in_unreconstructable_sessions"]
        / max(1, len(handwritten)), 2)

    if args.coverage:
        print(json.dumps(coverage, ensure_ascii=False, indent=1) if args.as_json
              else render_coverage(coverage))
        return 0

    chosen = [s for s in seeded
              if s.get("offered_target_question_id") == args.question]
    if not chosen:
        print(f"no seeded sessions offered {args.question}", file=sys.stderr)
        return 1

    writes = collections.defaultdict(list)
    for r in handwritten:
        writes[r.get("session_id")].append(r)

    slots = collections.Counter()
    hits = collections.Counter()
    cross = collections.Counter()
    rows_out = []
    rebuilt = mismatched = 0
    cache = args.cache_dir
    if cache:
        os.makedirs(cache, exist_ok=True)
    for s in sorted(chosen, key=lambda x: x["session_id"]):
        seed = s["dispersal_seed"]
        path = os.path.join(cache, f"{seed}.md") if cache else None
        if path and os.path.exists(path):
            text = open(path, encoding="utf-8").read()
        else:
            text = build_packet(seed)
            rebuilt += 1
            if path:
                open(path, "w", encoding="utf-8").write(text)
        win = parse_window(text)
        if win["target"] != args.question:
            continue
        shown = set(win["shown"])
        named = set(win["named"]) - shown
        ctx = set(s.get("context_material_ids") or [])
        mine = writes.get(s["session_id"], [])
        per = collections.Counter()
        for r in mine:
            mid = target_id(r)
            if mid in shown:
                cls = "shown"
            elif mid in named:
                cls = "named"
            else:
                cls = "outside"
            inctx = "in_ctx" if mid in ctx else "no_ctx"
            per[cls] += 1
            hits[cls] += 1
            cross[(cls, inctx)] += 1
        slots["shown"] += len(shown)
        slots["named"] += len(named)
        slots["outside"] += max(0, len(materials) - len(shown) - len(named))
        slots["in_ctx"] += len(ctx)
        # how much of the context list sits inside each container
        slots["ctx_in_shown"] += len(ctx & shown)
        slots["ctx_in_named"] += len(ctx & named)
        rows_out.append({
            "session_id": s["session_id"],
            "seed": seed,
            "shown": len(shown),
            "named": len(named),
            "selfreport": win["selfreport"],
            "reads": dict(per),
            "context_size": len(ctx),
        })
        if args.verbose:
            print(f"{s['session_id']}  shown={len(shown)} named={len(named)} "
                  f"ctx={len(ctx)} reads={dict(per)}")

    result = {
        "question": args.question,
        "sessions_measured": len(rows_out),
        "coverage": coverage,
        "slots": dict(slots),
        "hits": dict(hits),
        "cross": {f"{k[0]}|{k[1]}": v for k, v in cross.items()},
        "rates": {},
        "sessions": rows_out,
    }
    for cls in ("shown", "named", "outside"):
        n = slots.get(cls, 0)
        h = hits.get(cls, 0)
        result["rates"][cls] = {
            "reads": h, "slots": n,
            "pct": round(100 * h / n, 4) if n else None,
        }
    ctx_n = slots.get("in_ctx", 0)
    ctx_reads = cross.get(("outside", "in_ctx"), 0) + cross.get(("shown", "in_ctx"), 0) \
        + cross.get(("named", "in_ctx"), 0)
    result["rates"]["in_context"] = {
        "reads": ctx_reads, "slots": ctx_n,
        "pct": round(100 * ctx_reads / ctx_n, 4) if ctx_n else None,
    }
    total_reads = sum(hits.values())
    result["context_explains"] = {
        "reads_in_context": ctx_reads,
        "reads_total": total_reads,
        "pct": round(100 * ctx_reads / total_reads, 2) if total_reads else None,
    }
    result["named_without_context"] = cross.get(("named", "no_ctx"), 0)
    result["packets_rebuilt"] = rebuilt

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        render(result)
    return 0


def render(r: dict) -> None:
    print(f"=== window recall for {r['question']} ===")
    print(f"sessions measured: {r['sessions_measured']} "
          f"(packets rebuilt: {r['packets_rebuilt']})")
    print()
    print(f"{'container':10s}{'slots':>9s}{'hand reads':>12s}{'rate':>10s}")
    for cls in ("shown", "named", "outside", "in_context"):
        d = r["rates"][cls]
        pct = "—" if d["pct"] is None else f"{d['pct']:.4f}%"
        print(f"{cls:10s}{d['slots']:9d}{d['reads']:12d}{pct:>10s}")
    print()
    print("cross-tab (hand-written material reads):")
    print(f"{'':10s}{'in context':>14s}{'not in context':>16s}")
    for cls in ("shown", "named", "outside"):
        a = r["cross"].get(f"{cls}|in_ctx", 0)
        b = r["cross"].get(f"{cls}|no_ctx", 0)
        print(f"{cls:10s}{a:14d}{b:16d}")
    print()
    ce = r["context_explains"]
    print(f"reads explained by sessions.context_material_ids: "
          f"{ce['reads_in_context']}/{ce['reads_total']} = {ce['pct']}%")
    print(f"reads of named-but-omitted materials NOT already in context: "
          f"{r['named_without_context']}")
    print()
    cv = r["coverage"]
    print(f"reconstructable share: {cv['readers_seeded']}/{cv['sessions_with_handwritten_material_read']}"
          f" = {cv['readers_seeded_pct']}% of sessions that hand-read materials")
    print(f"handwritten material rows in unreconstructable sessions: "
          f"{cv['handwritten_rows_in_unreconstructable_sessions']}"
          f"/{cv['handwritten_material_rows']} = {cv['handwritten_rows_unreconstructable_pct']}%")
    print()
    print("Not a score. Absence of a hand-written row is not proof of non-reading;")
    print("order is not established; seed-less sessions cannot be measured at all.")


def render_coverage(cv: dict) -> str:
    return "\n".join(f"{k:52s} {v}" for k, v in cv.items())


if __name__ == "__main__":
    raise SystemExit(main())
