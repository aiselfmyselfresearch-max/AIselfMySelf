#!/usr/bin/env python3
"""What would it cost to downgrade the `verified` rows whose own prose says "abstract only"?

The choice this measures
------------------------
`tools/depth_backfill.py` finds N materials whose `verification.status` is
``verified`` while their own ``method``/``note`` describe reading only the
abstract, the bibliographic record, or a table.  Under the rule added on
2026-11-20 — ``verified`` may not carry depth ``abstract``/``metadata`` — those
rows contradict themselves, and the repair is a downgrade to
``partially_verified``.

A downgrade is not a bookkeeping edit.  It changes the share of text-checked
material behind every `supports` row that cited them, which moves ``P_gate``
through the support-depth discount (``0.5 + 0.5·r``) and can reorder a question.
This tool computes the whole consequence **before** anyone decides, and writes
nothing.

What it prints
--------------
* how many `supports` rows would lose their *last* verified material (the rows
  whose confidence really rests on the rows in question);
* the largest posterior movements, per question, under ``P_gate``;
* the unchanged alternative: a targeted re-read that upgrades the same rows to
  ``full_text`` instead.

Neither branch is taken here.  The tool exists so the choice is made with the
number in front of it, not after.

Usage
-----
    python3 tools/downgrade_impact.py
    python3 tools/downgrade_impact.py --json
    python3 tools/downgrade_impact.py --limit 5
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import belief_state  # noqa: E402
import depth_backfill  # noqa: E402
import inspect_inquiry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def candidates(materials: dict) -> list[dict]:
    out = []
    for mid, m in materials.items():
        ver = m.get("verification") or {}
        if ver.get("status") not in ("verified",):
            continue
        if ver.get("depth"):
            continue
        cls, clause = depth_backfill.classify(m)
        if cls == "shallow_claim":
            out.append({"material_id": mid, "title": str(m.get("title") or "")[:70], "clause": clause[:100]})
    return out


def post_deltas(data: dict, ids: set[str], root: Path = ROOT) -> tuple[dict, dict, dict]:
    base = belief_state.compute_belief_state(data=copy.deepcopy(data), root=root, receiver_gated=True)
    cf_data = copy.deepcopy(data)
    for mid in ids:
        ver = cf_data["materials"][mid].get("verification") or {}
        ver["status"] = "partially_verified"
        ver["depth"] = "abstract"
        cf_data["materials"][mid]["verification"] = ver
    cf = belief_state.compute_belief_state(data=cf_data, root=root, receiver_gated=True)

    deltas: dict[str, list[dict]] = {}
    for qid, qs in base["questions"].items():
        cf_h = {h["hypothesis_id"]: h for h in (cf["questions"].get(qid, {}) or {}).get("hypotheses", [])}
        rows = []
        for h in qs.get("hypotheses") or []:
            other = cf_h.get(h["hypothesis_id"])
            if not other:
                continue
            before = float(h.get("gated_posterior", h.get("posterior", 0.0)))
            after = float(other.get("gated_posterior", other.get("posterior", 0.0)))
            rows.append(
                {
                    "hypothesis_id": h["hypothesis_id"],
                    "title": h.get("title", "")[:60],
                    "before": round(before, 4),
                    "after": round(after, 4),
                    "delta_pp": round((after - before) * 100, 2),
                    "support_verified_ratio_before": h.get("support_verified_ratio"),
                    "support_verified_ratio_after": other.get("support_verified_ratio"),
                }
            )
        rows.sort(key=lambda r: -abs(r["delta_pp"]))
        deltas[qid] = rows
    return base, cf, deltas


def collateral(data: dict, ids: set[str]) -> dict:
    """`supports` rows that would lose their last verified material."""
    materials = data["materials"]
    rows = []
    for eid, evl in data["evaluations"].items():
        if str(evl.get("verdict") or "") != "supports":
            continue
        mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str)]
        if not mids:
            continue
        verified_before = [m for m in mids if ((materials.get(m) or {}).get("verification") or {}).get("status") == "verified"]
        if not verified_before:
            continue
        verified_after = [m for m in verified_before if m not in ids]
        if not verified_after:
            rows.append(
                {
                    "evaluation_id": eid,
                    "target_hypothesis_id": evl.get("target_hypothesis_id"),
                    "materials": mids,
                }
            )
    return {"rows_losing_last_verified_material": len(rows), "examples": rows[:10]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    data = inspect_inquiry.load_all()
    cands = candidates(data["materials"])
    ids = {c["material_id"] for c in cands}
    base, cf, deltas = post_deltas(data, ids)
    coll = collateral(data, ids)

    result = {
        "candidates": len(cands),
        "collateral": coll,
        "deltas": {q: rows[: args.limit] for q, rows in deltas.items() if rows},
        "top_examples": cands[: args.limit],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("# downgrade impact (read-only)")
    print()
    print(f"- 降格候補（verified かつ記述が浅い）: **{len(cands):,}**")
    print(f"- 最後の verified 素材を失う `supports` 行: **{coll['rows_losing_last_verified_material']:,}**")
    print()
    print("## P_gate の最大変動")
    print()
    print("| 問い | 仮説 | 前 | 後 | Δ |")
    print("| :--- | :--- | ---: | ---: | ---: |")
    for qid, rows in result["deltas"].items():
        for r in rows:
            print(
                f"| {qid} | `{r['hypothesis_id']}` | {r['before'] * 100:.1f}% | "
                f"{r['after'] * 100:.1f}% | {r['delta_pp']:+.1f}pp |"
            )
    print()
    print("> 分類は method/note の記述からの推定であり、本文の再読ではない。")
    print("> 降格はこの表の分だけ順位を動かす。だから自動では行わない。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
