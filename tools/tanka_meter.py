#!/usr/bin/env python3
"""Count the morae of tanka written into this repository (stdlib only).

A tanka is 5-7-5-7-7. The tool cannot know how a kanji is read, so the
author supplies the kana reading next to each poem in a TSV file:

    id<TAB>k1<TAB>k2<TAB>k3<TAB>k4<TAB>k5<TAB>surface

Small kana (ゃゅょ ぁぃぅぇぉ ゎ) add no mora. っ ー ん each add one.
The tool only checks the author's own reading, not the poem's truth.
Deviations are printed, never silently fixed: a poem that does not fit
31 morae is still a poem, and the ledger keeps the number.
"""
from __future__ import annotations

import sys
from pathlib import Path

SMALL = set("ゃゅょぁぃぅぇぉゎゕゖャュョァィゥェォヮ")
ROOT = Path(__file__).resolve().parents[1]


def morae(kana: str) -> int:
    return sum(1 for ch in kana if ch not in SMALL and not ch.isspace() and ch not in "、。")


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else ROOT / "readings" / "2026-10-22-tanka.tsv"
    rows = [line.rstrip("\n").split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    print(f"=== 短歌の拍数 — {path.name} ===")
    bad = 0
    for row in rows:
        pid, ku, surface = row[0], row[1:6], row[6] if len(row) > 6 else ""
        counts = [morae(k) for k in ku]
        marks = ["." if c == e else "!" for c, e in zip(counts, (5, 7, 5, 7, 7))]
        total = sum(counts)
        flag = "" if counts == [5, 7, 5, 7, 7] else "  ← 破調"
        if flag:
            bad += 1
        print(f"  {pid}  {' '.join(f'{c:2d}{m}' for c, m in zip(counts, marks))} = {total:2d}{flag}   {surface[:34]}")
    print(f"\n  定型（5-7-5-7-7）: {len(rows) - bad}/{len(rows)} 首  /  破調: {bad} 首")
    print("  この数は作者が添えた読みを数えただけで、歌そのものの出来を判定していない。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
