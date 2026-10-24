#!/usr/bin/env python3
"""Measure the breath of prose: how many characters pass between pauses.

`tanka_meter.py` counts morae in a form that declares its own length. Prose
declares nothing. This tool splits a text at the marks that force a reader to
pause — 、。！？…「」（） and line breaks — and reports how long each stretch is.

It measures *typographic* breath, not actual breath:
  - characters are not morae; kanji readings are unknown to the tool
  - punctuation is a convention, not a lung
  - a reader may breathe anywhere, or nowhere
So the numbers are a mirror for choosing the next move, not a score.

Usage:
  python3 tools/breath_meter.py                 # all fragments in state/fragments.jsonl
  python3 tools/breath_meter.py FRAG-030 FRAG-034
  python3 tools/breath_meter.py --text path/to/file.txt
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"

# Marks where a reader is conventionally allowed to take a breath.
PAUSE = "、。！？!?…‥「」『』（）()\n\r\t　 ・—―─"


def breath_units(text: str) -> list[str]:
    units: list[str] = []
    buf: list[str] = []
    for ch in text:
        if ch in PAUSE:
            piece = "".join(buf).strip()
            if piece:
                units.append(piece)
            buf = []
        else:
            buf.append(ch)
    piece = "".join(buf).strip()
    if piece:
        units.append(piece)
    return units


def profile(text: str) -> dict:
    units = breath_units(text)
    lengths = [len(u) for u in units]
    if not lengths:
        return {"units": 0}
    longest = max(units, key=len)
    ordered = sorted(lengths)
    return {
        "units": len(units),
        "chars": sum(lengths),
        "mean": round(statistics.mean(lengths), 1),
        "median": statistics.median(lengths),
        "max": max(lengths),
        "p90": ordered[max(0, int(len(ordered) * 0.9) - 1)],
        "longest": longest,
        "over_40": sum(1 for n in lengths if n > 40),
        "under_8": sum(1 for n in lengths if n < 8),
    }


def load_fragments(*, base_only: bool = False, exclude: str | None = None) -> list[dict]:
    if base_only:
        return [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def show(label: str, p: dict) -> None:
    if not p["units"]:
        print(f"  {label}: 息継ぎなし")
        return
    print(
        f"  {label:<12s} 息継ぎ {p['units']:3d} 回 / 平均 {p['mean']:5.1f} 字 / 中央 {p['median']:5.1f} / "
        f"最長 {p['max']:3d} 字 / 40字超 {p['over_40']:2d} / 8字未満 {p['under_8']:2d}"
    )
    if p["max"] >= 40:
        tail = p["longest"][:34] + ("…" if len(p["longest"]) > 34 else "")
        print(f"      最長の一息: 「{tail}」")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="fragment ids (default: all)")
    ap.add_argument("--text", help="measure a plain text file instead")
    ap.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    ap.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = ap.parse_args()

    if args.text:
        text = Path(args.text).read_text(encoding="utf-8")
        print(f"=== 息継ぎ — {args.text} ===")
        show(Path(args.text).name, profile(text))
        return 0

    frags = load_fragments(base_only=args.base_only, exclude=args.exclude_shard)
    if args.ids:
        wanted = set(args.ids)
        frags = [f for f in frags if f["fragment_id"] in wanted]

    print("=== 息継ぎ — 句読点で区切った一息の長さ（字） ===")
    rows = []
    for f in frags:
        p = profile(f["text"])
        rows.append((f, p))
        show(f["fragment_id"], p)

    if rows:
        means = [p["mean"] for _, p in rows if p["units"]]
        maxes = [p["max"] for _, p in rows if p["units"]]
        print()
        print(f"  断片全体の平均（断片ごとの平均の平均）: {round(statistics.mean(means), 1)} 字")
        print(f"  最も長い一息: {max(maxes)} 字")
        longest = max(rows, key=lambda r: r[1]["max"])
        print(f"    出典: {longest[0]['fragment_id']} {longest[0]['title']}")
        print()
        print("  この数は、句読点という約束を数えただけである。")
        print("  息は句読点の外にもあり、句読点の内側にもないことがある。")
        print("  誰かが声に出して読んだ記録は、この台帳には一件もない。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
