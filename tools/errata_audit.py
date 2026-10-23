#!/usr/bin/env python3
"""Re-run the checks recorded in state/errata.jsonl (stdlib only).

This is not a grader. It recomputes what can be recomputed, prints the result
beside the recorded judgement, and leaves the fragments untouched. A mismatch
means the errata record and the current ledger disagree; it does not decide
which of them is right.

Usage:
  python3 tools/errata_audit.py
  python3 tools/errata_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# A tail sentence is treated as a question when it ends with a question mark,
# or with one of the interrogative closings that the ledger uses with 句点.
QUESTION_TAIL = re.compile(r"(？|\?|だろうか。|でしょうか。|のか。|ではないか。|のだろうか。)$")


def load_jsonl(name: str) -> list[dict[str, Any]]:
    path = ROOT / "state" / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def number(fragment_id: str) -> int:
    match = re.search(r"(\d+)$", fragment_id)
    return int(match.group(1)) if match else 10**6


def tail_sentence(text: str) -> str:
    parts = [p for p in re.split(r"(?<=[。？！?!])", text.strip()) if p.strip()]
    return parts[-1].strip() if parts else text.strip()


def in_range(fragments: list[dict[str, Any]], low: int, high: int) -> list[dict[str, Any]]:
    return [f for f in fragments if low <= number(f["fragment_id"]) <= high]


def run_check(check: dict[str, Any], fragments: list[dict[str, Any]]) -> dict[str, Any]:
    kind = check.get("kind")
    params = check.get("params") or {}
    by_id = {f["fragment_id"]: f for f in fragments}

    if kind == "tail_question_count":
        subset = in_range(fragments, int(params.get("from", 1)), int(params.get("to", 10**6)))
        hits = [f["fragment_id"] for f in subset if QUESTION_TAIL.search(tail_sentence(f["text"]))]
        return {"measurable": True, "value": len(hits), "detail": ", ".join(hits) or "—"}

    if kind == "phrase_set_count":
        subset = in_range(fragments, int(params.get("from", 1)), int(params.get("to", 10**6)))
        phrases = params.get("phrases", [])
        hits = [f["fragment_id"] for f in subset if any(p in f["text"] for p in phrases)]
        return {"measurable": True, "value": len(hits), "detail": ", ".join(hits) or "—"}

    if kind == "phrase_in_fragments":
        phrases = params.get("phrases", [])
        targets = params.get("fragments", [])
        found, missing = [], []
        for fid in targets:
            text = by_id.get(fid, {}).get("text", "")
            (found if any(p in text for p in phrases) else missing).append(fid)
        return {"measurable": True, "value": f"{len(found)}/{len(targets)}",
                "detail": ("一致: " + (", ".join(found) or "—")) + " / 不一致: " + (", ".join(missing) or "—")}

    if kind == "last_sentence_length":
        fid = params.get("fragment_id", "")
        text = by_id.get(fid, {}).get("text", "")
        return {"measurable": True, "value": len(tail_sentence(text)), "detail": tail_sentence(text)[:40] + "…"}

    return {"measurable": False, "value": "—", "detail": "本文に手続きが記録されていないため再実行しない"}


def recorded_number(value: str) -> str:
    match = re.match(r"\s*(\d+)", value or "")
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run the checks recorded in the errata ledger.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    errata = load_jsonl("errata.jsonl")
    fragments = load_jsonl("fragments.jsonl")

    results = []
    for record in sorted(errata, key=lambda r: r["errata_id"]):
        measured = run_check(record.get("check", {}), fragments)
        agree: bool | None = None
        if measured["measurable"]:
            recorded = recorded_number(record.get("measured_now", ""))
            measured_str = str(measured["value"])
            agree = bool(recorded) and recorded in (measured_str, measured_str.split("/")[0])
        results.append({"errata": record, "measured": measured, "agree": agree})

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return 0

    print("=== 訂正録の再測定 — 訂正そのものを測る（採点ではありません） ===")
    print(f"対象: state/errata.jsonl {len(errata)} 件 / state/fragments.jsonl {len(fragments)} 編\n")
    for row in results:
        rec, mes, agree = row["errata"], row["measured"], row["agree"]
        mark = "再現" if agree else ("不一致" if agree is False else "対象外")
        print(f"[{rec['errata_id']}] {rec['fragment_id']}  verdict={rec['verdict']} / status={rec['status']} / 再測定={mark}")
        print(f"   主張 : {rec['claim']}")
        print(f"   記録 : {rec.get('measured_now','—')}")
        print(f"   今回 : {mes['value']}  ({mes['detail']})")
        print(f"   註   : {rec['note']}\n")

    open_count = sum(1 for r in errata if r["status"] == "open")
    contradicted = sum(1 for r in errata if r["verdict"] == "contradicted")
    agreeing = sum(1 for row in results if row["agree"] is True)
    disagreeing = sum(1 for row in results if row["agree"] is False)
    print("--- 集計 ---")
    print(f"  errata 総数 {len(errata)} / contradicted {contradicted} / open {open_count}")
    print(f"  再測定できたもの {agreeing + disagreeing} 件のうち、記録と一致 {agreeing} 件・不一致 {disagreeing} 件")
    print("  この道具は本文を書き換えない。判定もしない。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
