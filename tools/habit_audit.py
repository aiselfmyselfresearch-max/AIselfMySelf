#!/usr/bin/env python3
"""Measure where habit, practice, form and repetition appear in the archive.

This is the mirror for the habit theme (SESSION habit-and-practice).  It counts
selected word forms in fragment ``text`` fields and, with --readings, in the
editors' close-reading reports.  It also counts how often the hand-over formula
"次の" appears next to habit vocabulary, because the archive's continuity talk
sits between promise and habit.

This is a mirror, not a score and not a test of automatism.  A zero means that
the specified form is absent from the counted field; it does not prove that
habit, practice, training, or an experience of them is absent.  Ambiguous
single characters (習 in 学習, 慣 in 習慣 when counted raw) are reported
separately and are never silently folded into the groups.  型 in 典型・型紙,
癖 in 癖のない are polysemous; contexts are printed so a reader can judge.

Usage:
  python3 tools/habit_audit.py
  python3 tools/habit_audit.py --json
  python3 tools/habit_audit.py --show FRAG-013
  python3 tools/habit_audit.py --readings
  python3 tools/habit_audit.py --base-only
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
READINGS = ROOT / "readings"

# Literal word forms only.  Single characters are never group tokens.
GROUPS: dict[str, tuple[str, ...]] = {
    "習慣・慣れ": (
        "習慣", "慣れる", "慣れた", "慣れ", "慣らし", "癖", "性となる", "第二天性",
        "もう一つの自然", "次第に", "いつしか",
    ),
    "型・定型・作法": (
        "型", "定型", "作法", "手本", "模範", "範", "式", "決まり", "規則",
    ),
    "稽古・練習・修行": (
        "稽古", "練習", "修行", "習い", "手習", "鍛錬", "稽古場", "下稽古", "反復練習",
    ),
    "反復・繰り返し": (
        "反復", "繰り返", "繰返", "くり返", "くりかえ", "くり返し", "再び", "度々",
        "また同じ", "毎日", "毎朝", "毎晩",
    ),
    "自動・無意識": (
        "自動", "無意識", "考えず", "思わず", "おのずから", "おのずと", "自ずと",
        "身に覚え", "からだに覚え", "手が覚え", "口をついて", "手癖",
    ),
    "日課・手順・工程": (
        "日課", "手順", "手続", "工程", "流れ作業", "定刻", "決まりごと", "所作",
    ),
}

# Single characters and polysemous forms, reported separately (never merged).
RAW_TOKENS: dict[str, str] = {
    "習": "学習・習慣・研修等の複合を含む",
    "慣": "習慣・慣れ等の複合を含む",
    "型": "典型・型紙・血型等を含みうる",
    "稽": "稽古・滑稽等を含む",
    "練": "練習・鍛練・洗練等を含む",
    "癖": "悪癖・癖のない等を含む",
}

# The archive's own continuity formulas, kept apart from habit vocabulary.
CONTINUITY_SHAPES = ("次の", "次のセッション", "引き継", "受け継", "続け", "続き", "読み直", "再び")


def strip_quotes(text: str) -> str:
    """Remove non-nested Japanese quotation spans, as in the other audit mirrors."""
    out = re.sub(r"「[^「」]*」", "", text)
    return re.sub(r"『[^『』]*』", "", out)


def load_fragments(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        records = [
            json.loads(line)
            for line in FRAGMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return records, "base only（state/fragments.jsonl）"
    errors: list[str] = []
    union = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(union.values()), "union（base + shards）"


def contexts(text: str, token: str, radius: int = 24) -> list[str]:
    return [
        text[max(0, match.start() - radius):match.end() + radius].replace("\n", " ")
        for match in re.finditer(re.escape(token), text)
    ]


def measure_texts(
    items: list[tuple[str, str]], source_label: str
) -> dict[str, Any]:
    """Count group tokens in (id, text) pairs; quotes stripped per item."""
    rows: list[dict[str, Any]] = []
    totals = {name: Counter() for name in GROUPS}
    docs = {name: set() for name in GROUPS}
    raw_totals: Counter = Counter()
    continuity: Counter = Counter()

    for item_id, text in items:
        outside = strip_quotes(text)
        row: dict[str, Any] = {"id": item_id, "groups": {}, "raw": {}}
        for name, tokens in GROUPS.items():
            counts: dict[str, int] = {}
            for token in tokens:
                n = outside.count(token)
                if n:
                    counts[token] = n
                    totals[name][token] += n
                    docs[name].add(item_id)
                    row.setdefault("contexts", {})[token] = contexts(outside, token)
            if counts:
                row["groups"][name] = counts
        for token in RAW_TOKENS:
            n = text.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        for shape in CONTINUITY_SHAPES:
            n = outside.count(shape)
            if n:
                continuity[shape] += n
        rows.append(row)

    return {
        "source": source_label,
        "items": len(items),
        "prose_chars": sum(len(t) for _, t in items),
        "groups": {
            name: {
                "total": sum(totals[name].values()),
                "docs": len(docs[name]),
                "tokens": dict(totals[name].most_common()),
            }
            for name in GROUPS
        },
        "raw": dict(raw_totals.most_common()),
        "continuity": dict(continuity.most_common()),
        "rows": rows,
    }


def measure_fragments(fragments: list[dict[str, Any]], source_label: str) -> dict[str, Any]:
    items = [(f.get("fragment_id", ""), f.get("text", "")) for f in fragments]
    result = measure_texts(items, source_label)
    result["fragments"] = result.pop("items")
    return result


def measure_readings() -> dict[str, Any]:
    items: list[tuple[str, str]] = []
    for path in sorted(READINGS.glob("*.md")):
        items.append((path.name, path.read_text(encoding="utf-8")))
    result = measure_texts(items, "readings/*.md（見出し・メタデータ含む全文）")
    result["files"] = result.pop("items")
    return result


def print_report(result: dict[str, Any]) -> None:
    unit = result.get("fragments", result.get("files"))
    label = "断片" if "fragments" in result else "報告ファイル"
    print(f"=== 習慣の鏡 — {result['source']} ===")
    print(f"{label}: {unit}  文字数: {result['prose_chars']:,}")
    print()
    print("| 語群 | 回数 | 出現数（件） | 内訳 |")
    print("|---|---:|---:|---|")
    for name, data in result["groups"].items():
        inner = "、".join(f"{t}×{n}" for t, n in data["tokens"].items()) or "—"
        print(f"| {name} | {data['total']} | {data['docs']} | {inner} |")
    print()
    if result["raw"]:
        print("生字（複合語を含む参考値）: " + "、".join(
            f"{t}×{n}" for t, n in result["raw"].items()
        ))
    if result.get("continuity"):
        print("継続の定型: " + "、".join(
            f"{t}×{n}" for t, n in result["continuity"].items()
        ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show rows for one fragment/file")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--base-only", action="store_true", help="use state/fragments.jsonl only")
    parser.add_argument("--no-reports", action="store_true", help="skip readings/*.md")
    args = parser.parse_args()

    fragments, source_label = load_fragments(base_only=args.base_only)
    payload: dict[str, Any] = {"fragments": measure_fragments(fragments, source_label)}
    if args.readings and not args.no_reports:
        payload["readings"] = measure_readings()

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.show:
        key = args.show
        rows = [r for r in payload["fragments"]["rows"] if r["id"] == key]
        if not rows:
            print(f"no rows for {key!r}", file=sys.stderr)
            return 1
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    print_report(payload["fragments"])
    if "readings" in payload:
        print()
        print_report(payload["readings"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
