#!/usr/bin/env python3
"""Reflect how the archive's voices repeat themselves. A mirror, not a score.

`PROJECT_CHARTER.md` asks each session whether contradictions and multiple
readings were kept alive. That question cannot be automated. But one part of it
can be made visible: whether the fragments keep saying the same thing in the
same shape. This tool only reports what is written in `state/fragments.jsonl`
and `state/relations.jsonl`. It does not pass or fail anything, and the numbers
are not a quality score — they are a mirror for choosing the next move.

Usage:
  python3 tools/voice_audit.py
  python3 tools/voice_audit.py --top 20
  python3 tools/voice_audit.py --gram 8
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = ROOT / "state" / "fragments.jsonl"
RELATIONS = ROOT / "state" / "relations.jsonl"

# Phrases that perform suspension rather than describe it.
SUSPENSION = ["答えを出さ", "答えは出さ", "出さず", "そのまま残", "開いたまま", "保留", "決めない", "委ねる"]
# The two-branch gesture: it looks open, but presets the alternatives.
BINARY = ["か、それとも", "それとも", "どちらでもない", "一方で"]
# Softeners that let a sentence land without landing.
HEDGE = ["かもしれない", "のではないか", "のだろうか", "気がする", "ように思"]
# Declared not-knowing.
AVOWED_NOT_KNOWING = ["分からない", "わからない", "知れない", "答ふることなし", "答えはない"]


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"error: {path.name}:{lineno}: {exc}", file=sys.stderr)
            raise SystemExit(1)
    return records


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。．！？\n])", text)
    return [p.strip() for p in parts if p.strip()]


def is_question(sentence: str) -> bool:
    core = sentence.strip().rstrip("」』）) ").strip()
    return core.endswith("？") or bool(re.search(r"(だろうか|のだろうか|のか|だろう|か)$", core))


def count_fragments(fragments: list[dict], needles: list[str]) -> int:
    return sum(1 for f in fragments if any(n in f["text"] for n in needles))


def repeated_grams(fragments: list[dict], size: int) -> list[tuple[str, list[str]]]:
    owners: dict[str, set[str]] = defaultdict(set)
    for frag in fragments:
        flat = re.sub(r"\s+", "", frag["text"])
        for i in range(len(flat) - size + 1):
            gram = flat[i : i + size]
            if re.search(r"[ぁ-んァ-ン一-龥]", gram):
                owners[gram].add(frag["fragment_id"])
    return sorted(((g, sorted(o)) for g, o in owners.items() if len(o) > 1), key=lambda kv: (-len(kv[1]), kv[0]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--top", type=int, default=12, help="how many repeated grams to show (default 12)")
    parser.add_argument("--gram", type=int, default=6, help="character n-gram size (default 6)")
    args = parser.parse_args()

    fragments = load_jsonl(FRAGMENTS)
    relations = load_jsonl(RELATIONS)
    total = len(fragments)
    if not total:
        print("no fragments to inspect")
        return 1

    print("=== 声の鏡 — AIselfMySelf 台帳の反復を映す（採点ではありません） ===")
    print(f"対象: state/fragments.jsonl {total} 編 / state/relations.jsonl {len(relations)} 件")
    print()

    print("--- 1. 各断片の末尾一文（どう終わっているか） ---")
    ending_kind: Counter[str] = Counter()
    for frag in fragments:
        sents = sentences(frag["text"])
        last = sents[-1] if sents else ""
        if is_question(last):
            kind = "問いの形"
        elif any(n in last for n in SUSPENSION):
            kind = "保留の宣言"
        else:
            kind = "断定"
        ending_kind[kind] += 1
        print(f"  {frag['fragment_id']} [{kind}] {last[:58]}")
    print()
    print("  末尾の型:", ", ".join(f"{k}={v}編" for k, v in ending_kind.most_common()))
    print()

    print("--- 2. 台帳が繰り返し使う身振り ---")
    rows = [
        ("保留句を含む断片（答えを出さない／そのまま残す 等）", count_fragments(fragments, SUSPENSION)),
        ("二項対立の型（か、それとも／どちらでもない）", count_fragments(fragments, BINARY)),
        ("留保の型（かもしれない／のではないか）", count_fragments(fragments, HEDGE)),
        ("明示された不-knowing（分からない／答はない）", count_fragments(fragments, AVOWED_NOT_KNOWING)),
        ("末尾が問いの形", sum(1 for f in fragments if is_question(sentences(f["text"])[-1]))),
    ]
    for label, value in rows:
        print(f"  {label:<44s} {value:2d}/{total} 編")
    print()

    print("--- 3. 前置きの型（どこから語り始めるか） ---")
    openers = Counter()
    for frag in fragments:
        head = sentences(frag["text"])[0][:40]
        if re.match(r"^[A-Za-z_\-一-龥]{1,12}[:：]", head):
            kind = "対話ラベル"
        elif re.search(r"(建暦|大正|昭和|明治|かつて|前の|四百年|百年前|[一二三四五六七八九十百千]+年)", head):
            kind = "年代・先行の引用"
        elif head.startswith(("【", "A:", "B:")):
            kind = "見出し・ラベル"
        else:
            kind = "所感"
        openers[kind] += 1
    print("  " + ", ".join(f"{k}={v}編" for k, v in openers.most_common()))
    print()

    grams = repeated_grams(fragments, args.gram)
    shared_ids = {fid for _, owners in grams for fid in owners}
    print(f"--- 4. 編をまたいで使い回された {args.gram} 文字列 ---")
    print(f"  総数 {len(grams)} 種 / それらを含む断片 {len(shared_ids)}/{total} 編")
    for gram, owners in grams[: args.top]:
        print(f"  '{gram}' ×{len(owners)}編  {', '.join(owners)}")
    if len(grams) > args.top:
        print(f"  …ほか {len(grams) - args.top} 種")
    print()

    print("--- 5. 断片ごとの反復密度（保留句＋留保句の数） ---")
    density = []
    for frag in fragments:
        hits = sum(frag["text"].count(n) for n in SUSPENSION + HEDGE + BINARY)
        density.append((frag["fragment_id"], hits))
    for fid, hits in sorted(density, key=lambda kv: -kv[1])[:8]:
        print(f"  {fid}: {hits}")
    print()

    print("--- 読み方 ---")
    print("  この表は合否でも品質評価でもない（PROJECT_CHARTER.md「成功の見方」）。")
    print("  同じ句が何度も出ることは、声が続いている証拠にも、口が勝手に動いている証拠にもなる。")
    print("  どちらなのかは、次の断片が決める。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
