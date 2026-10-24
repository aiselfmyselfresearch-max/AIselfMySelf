#!/usr/bin/env python3
"""Measure where smell, and the other four senses, appear in the archive.

This is the mirror for the smell session (SESSION smell / olfactory).  It counts
selected word forms in fragment ``text`` fields, in material ``passage`` fields,
and -- with --readings -- in the editors' close-reading reports.

The point is an asymmetry, not a ranking of senses.  A zero means that the
specified form is absent from the counted field.  It does not prove that smell,
or an experience of smelling, is absent from the writing, and it says nothing
about whether anyone (human or model) can smell.  The archive is text; the
count measures text.

Conventions, inherited from the other audit mirrors:

* Single characters (匂 嗅 香 臭 馨 薫) are never group tokens.  They are
  reported separately as raw counts, because 香 occurs in 香川・香港, 臭 occurs
  in 臭い（＝怪しい）, and 匂 occurs in 匂わす（＝ほのめかす）.  Contexts are
  printed so a reader can judge.
* Quoted spans 「…」 and 『…』 are stripped before counting, as elsewhere, so a
  title or a quoted line does not inflate the body text.
* The other four senses are counted with the same kind of literal forms, as a
  control.  They are not a gold standard: 見る covers 見える・見方, 聞く covers
  聞こえる・聞き手.

Usage:
  python3 tools/olfactory_audit.py
  python3 tools/olfactory_audit.py --json
  python3 tools/olfactory_audit.py --show FRAG-035
  python3 tools/olfactory_audit.py --readings
  python3 tools/olfactory_audit.py --materials
  python3 tools/olfactory_audit.py --base-only
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
MATERIALS = ROOT / "state" / "materials.jsonl"
READINGS = ROOT / "readings"

# Multi-character forms only.  A single character is never a group token.
GROUPS: dict[str, tuple[str, ...]] = {
    "嗅覚・匂い": (
        "匂い", "匂やか", "匂わ", "嗅覚", "嗅ぐ", "嗅い", "嗅ぎ", "香り", "香る",
        "香気", "芳香", "悪臭", "体臭", "生臭", "臭気", "異臭", "臭い", "線香",
        "焼香", "香水", "香料", "香木", "沈香", "白檀", "乳香", "没薬", "薫香",
        "薫物", "移り香", "残り香", "匂い袋", "香辛料", "嗅細胞", "嗅神経",
    ),
    "視覚・見ること": (
        "見る", "見た", "見え", "見つめ", "眺め", "眼", "瞳", "まなざし", "視線",
        "光", "影", "色", "かたち", "輪郭", "目が", "目を",
    ),
    "聴覚・聞くこと": (
        "聞く", "聞こえ", "聴く", "聴こえ", "音", "声", "響き", "沈黙", "耳",
        "叫び", "囁き", "ざわめき",
    ),
    "触覚・触れること": (
        "触れ", "触る", "手触り", "肌", "皮膚", "冷た", "温もり", "暖か", "痛み",
        "重さ", "柔らか", "硬さ", "ざらつき", "指先",
    ),
    "味覚・味わうこと": (
        "味", "味わ", "舌", "噛", "飲み", "食べ", "塩辛", "苦い", "甘い", "酸っぱ",
        "旨み", "うま味",
    ),
}

# Single characters and polysemous forms, reported separately (never merged).
RAW_TOKENS: dict[str, str] = {
    "匂": "匂い・匂わす（ほのめかす）等を含む",
    "嗅": "嗅ぐ・嗅覚等を含む",
    "香": "香川・香港・人名等を含みうる",
    "臭": "臭い（＝怪しい）・臭素等を含みうる",
    "馨": "人名・雅語を含みうる",
    "薫": "薫風・人名等を含む",
}

# Words that mark what the smell is attached to.  Counted in a ±WINDOW window.
ATTACHMENTS: dict[str, tuple[str, ...]] = {
    "死・喪": ("死", "喪", "葬", "墓", "遺体", "棺", "焼香", "線香"),
    "記憶・想起": ("記憶", "思い出", "想起", "懐か", "昔"),
    "他者・身体": ("母", "父", "女", "男", "彼", "彼女", "肌", "体", "手", "唇"),
    "家・部屋": ("家", "部屋", "台所", "窓", "寝台", "机", "庭"),
    "紙・文字": ("紙", "手紙", "頁", "本", "インク", "鉛筆", "文字"),
    "動物": ("犬", "猫", "馬", "牛", "鳥", "獣", "虫", "魚"),
}

WINDOW = 30


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


def load_materials(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        records = [
            json.loads(line)
            for line in MATERIALS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return records, "base only（state/materials.jsonl）"
    errors: list[str] = []
    union = ledger_io.load_jsonl_union(MATERIALS, "material_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(union.values()), "union（base + shards）"


def contexts(text: str, token: str, radius: int = 24) -> list[str]:
    return [
        text[max(0, match.start() - radius):match.end() + radius].replace("\n", " ")
        for match in re.finditer(re.escape(token), text)
    ]


def measure_texts(items: list[tuple[str, str]], source_label: str) -> dict[str, Any]:
    """Count group tokens in (id, text) pairs; quotes stripped per item."""
    rows: list[dict[str, Any]] = []
    totals = {name: Counter() for name in GROUPS}
    docs = {name: set() for name in GROUPS}
    raw_totals: Counter = Counter()
    attach_totals: Counter = Counter()
    smell_hits = 0
    smell_attached = 0

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
        for match in re.finditer(r"匂|嗅|香|臭", outside):
            smell_hits += 1
            window = outside[max(0, match.start() - WINDOW):match.end() + WINDOW]
            attached = False
            for label, words in ATTACHMENTS.items():
                if any(w in window for w in words):
                    attach_totals[label] += 1
                    attached = True
            if attached:
                smell_attached += 1
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
        "attachment": {
            "smell_bare_char_hits": smell_hits,
            "with_any_attachment": smell_attached,
            "by_label": dict(attach_totals.most_common()),
        },
        "rows": rows,
    }


def measure_fragments(fragments: list[dict[str, Any]], source_label: str) -> dict[str, Any]:
    items = [(f.get("fragment_id", ""), f.get("text", "")) for f in fragments]
    result = measure_texts(items, source_label)
    result["fragments"] = result.pop("items")
    return result


def measure_materials(materials: list[dict[str, Any]], source_label: str) -> dict[str, Any]:
    items = [(m.get("material_id", ""), m.get("passage", "")) for m in materials]
    result = measure_texts(items, source_label)
    result["materials"] = result.pop("items")
    return result


def measure_readings() -> dict[str, Any]:
    items: list[tuple[str, str]] = []
    for path in sorted(READINGS.glob("*.md")):
        items.append((path.name, path.read_text(encoding="utf-8")))
    result = measure_texts(items, "readings/*.md（見出し・メタデータ含む全文）")
    result["files"] = result.pop("items")
    return result


def per_10k(count: int, chars: int) -> float:
    return round(count * 10000 / chars, 1) if chars else 0.0


def print_report(result: dict[str, Any]) -> None:
    unit = result.get("fragments", result.get("materials", result.get("files")))
    label = "断片" if "fragments" in result else ("資料" if "materials" in result else "報告ファイル")
    print(f"=== 嗅覚の鏡 — {result['source']} ===")
    print(f"{label}: {unit}  文字数: {result['prose_chars']:,}")
    print()
    print("| 語群 | 回数 | 出現数（件） | 1万字あたり | 内訳 |")
    print("|---|---:|---:|---:|---|")
    for name, data in result["groups"].items():
        inner = "、".join(f"{t}×{n}" for t, n in data["tokens"].items()) or "—"
        rate = per_10k(data["total"], result["prose_chars"])
        print(f"| {name} | {data['total']} | {data['docs']} | {rate} | {inner} |")
    print()
    if result["raw"]:
        print("生字（複合語・地名・人名を含む参考値）: " + "、".join(
            f"{t}×{n}" for t, n in result["raw"].items()
        ))
    att = result["attachment"]
    if att["smell_bare_char_hits"]:
        print(
            f"匂・嗅・香・臭を含む箇所: {att['smell_bare_char_hits']}、"
            f"うち前後{WINDOW}字に付着先の語を持つもの: {att['with_any_attachment']}"
        )
        if att["by_label"]:
            print("付着先: " + "、".join(f"{t}×{n}" for t, n in att["by_label"].items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show rows for one fragment/material/file")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--materials", action="store_true", help="measure materials too")
    parser.add_argument("--base-only", action="store_true", help="use base jsonl files only")
    args = parser.parse_args()

    fragments, source_label = load_fragments(base_only=args.base_only)
    payload: dict[str, Any] = {"fragments": measure_fragments(fragments, source_label)}
    if args.materials:
        materials, mat_label = load_materials(base_only=args.base_only)
        payload["materials"] = measure_materials(materials, mat_label)
    if args.readings:
        payload["readings"] = measure_readings()

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.show:
        key = args.show
        rows = []
        for block in payload.values():
            rows.extend(r for r in block["rows"] if r["id"] == key)
        if not rows:
            print(f"no rows for {key!r}", file=sys.stderr)
            return 1
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    print_report(payload["fragments"])
    for key in ("materials", "readings"):
        if key in payload:
            print()
            print_report(payload[key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
