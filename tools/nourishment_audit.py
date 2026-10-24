#!/usr/bin/env python3
"""Measure where eating, hunger and nourishment appear in the archive's prose.

This is a mirror, not a score and not a test of embodiment.  It counts selected
word forms in fragment ``text`` fields.  A zero means that the specified form is
absent; it does not prove that hunger, food, taste, or an experience of them is
absent.  Ambiguous single characters (食 in 食い違う, 味 in 意味, 皿 in 油皿)
are reported separately and are never silently folded into the food groups.

Usage:
  python3 tools/nourishment_audit.py
  python3 tools/nourishment_audit.py --json
  python3 tools/nourishment_audit.py --show FRAG-017
  python3 tools/nourishment_audit.py --base-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"

# Keep the groups deliberately literal.  In particular, 味 and 食 are not group
# tokens: 意味 and 食い違い would otherwise manufacture a food-rich archive.
GROUPS: dict[str, tuple[str, ...]] = {
    "食事の動作": (
        "食事", "食卓", "食べる", "食べた", "食べて", "食べない", "食べよう",
        "食われる", "食われた", "喰う", "喰らう", "給食", "朝食", "昼食", "夕食", "晩餐",
    ),
    "飢えと栄養": (
        "飢え", "飢餓", "飢饉", "空腹", "餓え", "餓死", "栄養", "滋養", "糧", "餌",
    ),
    "飲む・消化": (
        "飲む", "飲んだ", "飲んで", "飲料", "嚥下", "咀嚼", "消化", "吸収", "代謝", "渇き",
    ),
    "味わい": (
        "味わう", "味わい", "味覚", "甘い", "甘み", "苦み", "辛み", "旨い",
        "美味", "不味", "酸っぱい", "塩辛", "食味",
    ),
    "食物・調理": (
        "パン", "ご飯", "白米", "玄米", "お粥", "粥", "味噌汁", "料理", "台所",
        "厨房", "食器", "茶碗", "箸", "食材", "牛肉", "魚肉", "野菜", "果物",
        "林檎", "牛乳", "卵", "菓子", "砂糖", "塩", "酢", "醤油",
    ),
    "拒否・供儀": ("断食", "絶食", "拒食", "不食", "供物", "供養", "生贄", "犠牲"),
    "取り込み・消費": ("摂取", "取り込", "吸い込", "消費", "燃料"),
}

RAW_TOKENS: dict[str, str] = {
    "食": "食い違う・気に食わない等を含む。食事の回数ではない",
    "味": "意味を大部分に含む。味覚の回数ではない",
    "飲": "飲み込む等の比喩を含みうる",
    "飢": "飢渇等の複合を含みうる",
    "皿": "油皿など食事と無関係の器を含む",
    "米": "米寿など食料以外の複合を含みうる",
    "肉": "筋肉など食物でない身体語を含む",
    "魚": "比喩・固有名を含みうる",
}


def strip_quotes(text: str) -> str:
    """Remove non-nested Japanese quotation spans, as in the other audit mirrors."""
    out = re.sub(r"「[^「」]*」", "", text)
    return re.sub(r"『[^『』]*』", "", out)


def load_base() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in FRAGMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_fragments(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        return load_base(), "base only（state/fragments.jsonl）"
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values()), "union（base + shards）"


def contexts(text: str, token: str, radius: int = 24) -> list[str]:
    return [
        text[max(0, match.start() - radius):match.end() + radius].replace("\n", " ")
        for match in re.finditer(re.escape(token), text)
    ]


def measure(fragments: list[dict[str, Any]], source_label: str = "test") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    totals = {name: Counter() for name in GROUPS}
    docs = {name: set() for name in GROUPS}
    raw_totals: Counter = Counter()
    inside: Counter = Counter()

    for fragment in fragments:
        text = fragment.get("text", "")
        outside = strip_quotes(text)
        row: dict[str, Any] = {
            "fragment_id": fragment.get("fragment_id", ""),
            "groups": {},
            "raw": {},
            "contexts": {},
        }
        for name, tokens in GROUPS.items():
            counts: dict[str, int] = {}
            for token in tokens:
                n_out = outside.count(token)
                n_in = text.count(token) - n_out
                if n_out:
                    counts[token] = n_out
                    totals[name][token] += n_out
                    docs[name].add(row["fragment_id"])
                    row["contexts"][token] = contexts(outside, token)
                if n_in:
                    inside[token] += n_in
            if counts:
                row["groups"][name] = counts
        for token in RAW_TOKENS:
            n = text.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        rows.append(row)

    return {
        "source": source_label,
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": rows,
        "group_totals": {name: dict(counter) for name, counter in totals.items()},
        "group_docs": {name: sorted(ids) for name, ids in docs.items()},
        "inside_quotes": dict(inside),
        "raw_totals": dict(raw_totals),
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 栄養の鏡 — 食べる語と飢える語はどこにあるか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字（メタデータを除く）")
    add(f"計数の範囲: {data['source']}")
    add("")
    add("--- 1. 語群ごとの出現（鉤括弧の外、地の文） ---")
    for name in GROUPS:
        counts = data["group_totals"].get(name, {})
        identifiers = data["group_docs"].get(name, [])
        total = sum(counts.values())
        detail = "、".join(
            f"{token}×{number}"
            for token, number in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ) or "なし"
        add(f"  {name:<14}: {total:>3} 回 / {len(identifiers):>2} 編  （{detail}）")
    add("")
    add("--- 2. 多義の生字（食事・味覚へ合算しない参考値） ---")
    for token in RAW_TOKENS:
        add(f"  {token}: {data['raw_totals'].get(token, 0)} 回  注意: {RAW_TOKENS[token]}")
    add("")
    add("--- 3. 鉤括弧の内側だけにある語 ---")
    add("  " + ("、".join(f"{k}×{v}" for k, v in sorted(data["inside_quotes"].items())) or "なし"))
    add("")
    add("--- 4. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、食事・空腹・味覚の経験や主題の不在を証明しない。")
    add("  ・『意味』の『味』、『食い違い』の『食』は食物として数えない。生字は多義の確認用に別掲する。")
    add("  ・『燃料』『取り込む』は食物以外の比喩を含む。実際の文脈は --show で確かめる。")
    add("  ・鉤括弧の除去は非入れ子の正規表現による近似で、地の文／引用の厳密な構文解析ではない。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's matches and contexts")
    parser.add_argument("--base-only", action="store_true", help="exclude session shards")
    args = parser.parse_args()

    fragments, label = load_fragments(args.base_only)
    data = measure(fragments, label)
    if args.show:
        for row in data["rows"]:
            if row["fragment_id"] == args.show:
                print(json.dumps(row, ensure_ascii=False, indent=2))
                return 0
        print(f"{args.show}: not found", flush=True)
        return 1
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
