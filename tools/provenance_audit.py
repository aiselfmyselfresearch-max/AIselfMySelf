#!/usr/bin/env python3
"""Audit how each material reached this ledger (stdlib only).

For every record in state/materials.jsonl, report:

  * the language of the original work,
  * the language in which the editor actually read it,
  * who carried it across languages (translator, compiler, transcriber),
  * and whether the passage is a quotation or the editor's summary.

Records added before SESSION-024 have no `provenance` block, so the tool
falls back to a keyword scan of `version_note` and prints both counts.  It
does not grade anything: it only makes the carriers visible and countable.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "state" / "materials.jsonl"

CARRIER_HINTS = re.compile(
    r"(trans\.|translated by|translation|訳|翻訳|拙訳|英訳|編訳|校訂|採録|聞き書き)"
)
SUMMARY_HINTS = re.compile(r"(要約|以下は.*要約)")
NAME_HINT = re.compile(r"([A-Z][A-Za-z.\-]+(?:\s+[A-Z][A-Za-z.\-]+){0,3})")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def guess_carrier_from_note(note: str) -> str:
    """Best-effort: return a named person if the note names one, else ''."""
    if not CARRIER_HINTS.search(note):
        return ""
    names = [n for n in NAME_HINT.findall(note) if len(n.split()) >= 2]
    return names[0] if names else ""


def main() -> int:
    rows = load(MATERIALS)
    lit = [r for r in rows if r["kind"] == "literary_text"]

    print("=== 来歴の監査 — 声はどの言語を通って、誰の手でこの台帳に来たか ===")
    print(f"対象: materials {len(rows)} 件（うち literary_text {len(lit)} 件）\n")

    has_block = [r for r in rows if isinstance(r.get("provenance"), dict)]
    print(f"provenance 欄をもつ記録      : {len(has_block)}/{len(rows)}")
    print(f"provenance 欄のない記録      : {len(rows) - len(has_block)}/{len(rows)}")

    # --- before/fallback view -------------------------------------------------
    fallback_carriers = 0
    for r in rows:
        if "provenance" not in r and guess_carrier_from_note(r["source"]["version_note"]):
            fallback_carriers += 1
    print(f"欄のない記録のうち version_note から運び手の名を拾えるもの : {fallback_carriers} 件")

    # --- provenance view ------------------------------------------------------
    if has_block:
        print("\n--- 1. 原語と参照言語 ---")
        pairs = Counter((p["original_language"], p["access_language"]) for p in (r["provenance"] for r in has_block))
        for (orig, access), n in sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0])):
            mark = "" if orig == access else "  ← 別言語経由"
            print(f"  原語 {orig:>3} / 参照 {access:>3} : {n:>2} 件{mark}")

        across = [r for r in has_block if r["provenance"]["original_language"] != r["provenance"]["access_language"]]
        print(f"\n  別言語を経由して読まれた記録 : {len(across)}/{len(has_block)}")

        print("\n--- 2. 運び手（carrier） ---")
        named = [r for r in has_block if r["provenance"]["carrier"].strip()]
        blank = [r for r in has_block if not r["provenance"]["carrier"].strip()]
        print(f"  名前のある運び手 : {len(named)}/{len(has_block)}")
        print(f"  空欄の運び手     : {len(blank)}/{len(has_block)}  "
              f"(うち別言語経由 {len([r for r in blank if r['provenance']['original_language'] != r['provenance']['access_language']])} 件)")
        for r in named:
            print(f"    {r['material_id']:<26} {r['provenance']['carrier']}")
        unnamed_across = [r["material_id"] for r in blank
                          if r["provenance"]["original_language"] != r["provenance"]["access_language"]]
        if unnamed_across:
            print("    別言語経由なのに運び手が空欄:", ", ".join(unnamed_across))

        print("\n--- 3. 引用か要約か ---")
        summ = [r for r in has_block if SUMMARY_HINTS.search(r.get("passage", "")[:40])]
        print(f"  編者要約（直接引用なし） : {len(summ)}/{len(has_block)}")
        print("   " + ", ".join(r["material_id"] for r in summ))

        print("\n--- 4. 綴りのずれ（passage_language と access_language） ---")
        # 要約の passage は日本語で書かれているので、綴りのずれとして数えない
        drift = [r for r in has_block
                 if not SUMMARY_HINTS.search(r.get("passage", "")[:40])
                 and r.get("passage_language") != r["provenance"]["access_language"]]
        if drift:
            for r in drift:
                print(f"  {r['material_id']}: passage_language={r['passage_language']} / access={r['provenance']['access_language']}")
        else:
            print("  なし（要約の日本語 passage は除く）")
    else:
        print("\n(provenance 欄がまだ無いため、来歴は version_note の散文からのみ読める)")

    print("\nこの表は合否ではない。誰の手を経て声が来たかを、数えられる形にしただけである。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
