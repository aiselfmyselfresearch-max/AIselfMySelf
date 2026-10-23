#!/usr/bin/env python3
"""Reconstruct a lost procedure from its numbers (stdlib only).

A measurement whose procedure was never written down looks unreproducible. But
a number is not only a result: it is a constraint on the procedure that could
have produced it. This tool sweeps a small grid of plausible rules and reports
which of them reproduce the numbers an old record claims.

It cannot prove that the original measured this way. It can show that the
numbers fit one family of rules and not another, and it can show how wide the
fit is. The threshold it reports is chosen from the result, and says so.

Usage:
  python3 tools/reconstruct.py
  python3 tools/reconstruct.py --target 88,12,8 --fragments 31 --trace-scope own
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from errata_audit import load_jsonl, normalize, number  # noqa: E402


def collect(fragments, min_len):
    return [
        (f["fragment_id"], set(f.get("material_ids") or []), quote)
        for f in fragments
        for quote in re.findall(r"「([^」]*)」", f["text"])
        if len(quote) >= min_len
    ]


def classify(quotes, materials, literary_min_len, trace_min_len, trace_scope):
    """Return (originals, traces, unmatched) as lists of (fragment_id, quote, material_id)."""
    normalized = [(m["material_id"], normalize(m["passage"])) for m in materials]
    originals, traces, unmatched = [], [], 0
    for fragment_id, cited, quote in quotes:
        key = normalize(quote)
        if not key:
            unmatched += 1
            continue
        hits = [mid for mid, passage in normalized if key in passage]
        trace_hits = [
            mid for mid in hits
            if mid.startswith("MAT-TRC") and (trace_scope != "own" or mid in cited)
        ]
        lit_hits = [mid for mid in hits if not mid.startswith("MAT-TRC")]
        if len(key) >= trace_min_len and trace_hits:
            traces.append((fragment_id, quote, trace_hits[0]))
        elif len(key) >= literary_min_len and lit_hits:
            originals.append((fragment_id, quote, lit_hits[0]))
        else:
            unmatched += 1
    return originals, traces, unmatched


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconstruct a lost counting procedure from its numbers.")
    parser.add_argument("--target", default="88,12,8",
                        help="recorded numbers: quotations, matches, originals (default 88,12,8)")
    parser.add_argument("--fragments", type=int, default=31, help="fragment population at the time")
    parser.add_argument("--min-len", type=int, default=4, help="length at which quotations were counted")
    parser.add_argument("--trace-scope", choices=["any", "own"], default="own")
    args = parser.parse_args()

    target_total, target_matched, target_originals = (int(x) for x in args.target.split(","))
    fragments = [f for f in load_jsonl("fragments.jsonl") if number(f["fragment_id"]) <= args.fragments]
    materials = load_jsonl("materials.jsonl")
    quotes = collect(fragments, args.min_len)

    print("=== 復元 — 失われた測り方を、数の側から探す（証明ではありません） ===\n")
    print(f"対象: 断片 {len(fragments)} 編 / 素材 {len(materials)} 件 / 記録された数 {args.target}\n")

    print("[1] 第一の数 — 引用の総数")
    print(f"    「」{args.min_len}文字以上を数える → {len(quotes)}  （記録 {target_total}）"
          f" {'✓' if len(quotes) == target_total else '✗'}")
    all_fragments = load_jsonl("fragments.jsonl")
    print(f"    いま全 {len(all_fragments)} 編で数えると {len(collect(all_fragments, args.min_len))}。"
          "総数は台帳が伸びたぶんだけ動く。\n")

    print("[2] 一本の物差しで、12 と 8 に届くか（文学と台帳自身を同じ下限で測る）")
    one_ruler = []
    for length in range(args.min_len, 13):
        originals, traces, _ = classify(quotes, materials, length, length, "any")
        one_ruler.append((length, len(originals), len(traces)))
        mark = " ← 記録と一致" if (len(originals), len(traces)) == (target_originals, target_matched - target_originals) else ""
        print(f"    下限 {length:2d}: 原典 {len(originals):2d} / 台帳自身 {len(traces):2d} / 計 {len(originals) + len(traces):2d}{mark}")
    reached = [r for r in one_ruler if (r[1], r[2]) == (target_originals, target_matched - target_originals)]
    print(f"    → 記録（原典 {target_originals} ／ 台帳自身 {target_matched - target_originals}）に届く下限: "
          f"{'なし' if not reached else ', '.join(str(r[0]) for r in reached)}\n")

    print("[3] 二本の物差しに分ける（文学は長め、台帳自身は短め）")
    print(f"    前提: 台帳自身は {args.trace_scope}（断片が実際に引いている素材のみ）・{args.min_len}文字以上")
    plateau = []
    for length in range(args.min_len, 13):
        originals, traces, _ = classify(quotes, materials, length, args.min_len, args.trace_scope)
        hit = (len(originals), len(traces)) == (target_originals, target_matched - target_originals)
        if hit:
            plateau.append(length)
        print(f"    文学の下限 {length:2d}: 原典 {len(originals):2d} / 台帳自身 {len(traces):2d} / 計 "
              f"{len(originals) + len(traces):2d}{' ✓' if hit else ''}")

    if plateau:
        originals, traces, _ = classify(quotes, materials, plateau[0], args.min_len, args.trace_scope)
        # what the second ruler dropped: genuine literary matches that are
        # shorter than the literary threshold (not all unmatched quotations).
        dropped = []
        traced = {(d[0], d[1]) for d in traces}
        for fragment_id, _cited, quote in quotes:
            key = normalize(quote)
            if len(key) >= plateau[0] or (fragment_id, quote) in traced:
                continue
            hits = [m["material_id"] for m in materials
                    if key in normalize(m["passage"]) and not m["material_id"].startswith("MAT-TRC")]
            if hits:
                dropped.append((fragment_id, quote, hits))
        print("\n[4] 二本目の物差しが落としたもの（一致はするが、文学の下限より短い）")
        for fragment_id, quote, hits in sorted(dropped, key=lambda r: len(normalize(r[1]))):
            print(f"    {fragment_id}  {len(normalize(quote)):2d}文字  {quote[:18]!r} → {', '.join(hits)}")
        kept_short = [(d[0], d[1], len(normalize(d[1]))) for d in traces if len(normalize(d[1])) < plateau[0]]
        print(f"\n    落ちた {len(dropped)} 箇所はいずれも短い引用である。長さで切るというより、"
              "短い一致を一致と呼ばなかった、と読むほうが近い。")
        for fragment_id, quote, length in kept_short:
            print(f"    ただし {fragment_id} の {length}文字 {quote[:14]!r} は落ちずに残る。"
                  "台帳自身の記録と一致したからで、同じ短さでも扱いが違う。")
        print("\n[5] この復元が示すこと／示さないこと")
        print("    示す: 記録された三つの数は、一本の物差しでは同時に届かない。"
              f"二本に分ければ、文学の下限 {plateau[0]}〜{plateau[-1]} 文字の範囲で届く。")
        print("    示さない: 当時の測定者が本当にその下限を使ったこと。"
              "下限は結果から選ばれた値であり、復元ではなく整合である。")
    else:
        print("\n    → 二本に分けても届かない。この格子の外に手続きがある。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
