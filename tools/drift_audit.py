#!/usr/bin/env python3
"""Show how the ledger's own measurements age (stdlib only).

Reads the errata records whose subject is a `project_trace` material — that is,
claims the archive made about itself — and re-runs their checks against the
current ledger. The point is not to catch errors. It is to show that a number
can stop being true without anyone correcting it, because the denominator grew.

Usage:
  python3 tools/drift_audit.py
  python3 tools/drift_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from errata_audit import load_jsonl, run_check  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-measure the archive's claims about itself, and show the drift.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    errata = load_jsonl("errata.jsonl")
    fragments = load_jsonl("fragments.jsonl")
    materials = load_jsonl("materials.jsonl")
    questions = load_jsonl("questions.jsonl")
    relations = load_jsonl("relations.jsonl")
    sessions = load_jsonl("sessions.jsonl")

    now = {
        "fragments": len(fragments),
        "materials": len(materials),
        "questions": len(questions),
        "relations": len(relations),
        "sessions": len(sessions),
        "errata": len(errata),
    }

    # materials that hold the ledger's measurements of itself, plus records that
    # take another errata record as their subject (corrections of corrections).
    drift = [r for r in errata if r.get("subject_type") in ("material", "other")]
    rows = []
    for record in sorted(drift, key=lambda r: r["errata_id"]):
        measured = run_check(record.get("check", {}), fragments, materials)
        params = record.get("check", {}).get("params", {}) or {}
        rows.append(
            {
                "errata_id": record["errata_id"],
                "subject": record.get("subject_id"),
                "claim": record["claim"],
                "verdict": record["verdict"],
                "status": record["status"],
                "recorded": record.get("measured_now", ""),
                "measured": measured,
                "as_of_fragments": params.get("as_of_fragments"),
                "as_of_materials": params.get("as_of_materials"),
            }
        )

    if args.json:
        print(json.dumps({"now": now, "rows": rows}, ensure_ascii=False, indent=1))
        return 0

    print("=== 経年検査 — 台帳が自分について書いた数を、いま測り直す（採点ではありません） ===")
    print(f"現在: 断片 {now['fragments']} 編 / 素材 {now['materials']} 件 / 問い {now['questions']} 件 / "
          f"関係 {now['relations']} 本 / セッション {now['sessions']} 回 / 訂正 {now['errata']} 件\n")

    for row in rows:
        as_of = "—"
        if row["as_of_fragments"]:
            as_of = f"断片{row['as_of_fragments']}編"
            if row["as_of_materials"]:
                as_of += f"・素材{row['as_of_materials']}件"
        print(f"[{row['errata_id']}] {row['subject']}  記録時: {as_of}  判定: {row['verdict']} / {row['status']}")
        print(f"   主張 : {row['claim']}")
        print(f"   記録 : {row['recorded']}")
        print(f"   今回 : {row['measured']['value']}  ({row['measured']['detail']})")
        growth = []
        if row["as_of_fragments"]:
            growth.append(f"断片 {row['as_of_fragments']}→{now['fragments']}（×{now['fragments']/row['as_of_fragments']:.2f}）")
        if row["as_of_materials"]:
            growth.append(f"素材 {row['as_of_materials']}→{now['materials']}（×{now['materials']/row['as_of_materials']:.2f}）")
        if growth:
            print("   分母 : " + " / ".join(growth))
        print()

    contradicted = sum(1 for r in rows if r["verdict"] == "contradicted")
    holds = sum(1 for r in rows if r["verdict"] == "holds")
    unmeasurable = sum(1 for r in rows if r["verdict"] == "unmeasurable")
    print("--- 集計 ---")
    print(f"  自分の測定についての errata {len(rows)} 件: 成り立たない {contradicted} / 成り立つ {holds} / 再測定不能 {unmeasurable}")
    print("  成り立たないもののうち、当時の手続きが誤っていたのは ERR-009（計器の不備）。")
    print("  残りは、測ったあとに台帳が伸びたことによる経年。誰も本文を書き換えていない。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
