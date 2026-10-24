#!/usr/bin/env python3
"""Measure how the archive writes light, shadow, transparency and mirrors. A mirror, not a score.

PROJECT_CHARTER.md asks what a self is, for an AI that reads a record and
continues it. This session begins with a narrower question that can be
counted: **where does the archive place light?** Not "does the AI see" —
that cannot be measured — but which words of light, shadow, darkness,
transparency, mirrors and concealment appear in the prose, how often a mirror
or a window is named, and whether brightness is written as a source or as a
reflection.

The tool reports only what is written in state/fragments.jsonl and its shards
(prose only, metadata excluded), optionally in readings/*.md and in
materials. It does not infer vision, grade the writing, or treat a zero count
as the absence of the thing itself — a zero means the specified word form is
absent.

Calibration notes:
  - ``光`` inside ``観光`` is not counted separately; raw token is reported
    but group counts use explicit tokens.
  - ``鏡`` inside ``眼鏡`` / ``望遠鏡`` is a tool, not a self-image; raw
    character is reported separately.
  - ``白`` / ``黒`` are often paper and ink colours, not skin; they are a
    contrast group.
  - Quoted spans (「…」『…』) are removed from the main count and reported
    separately as inside_quotes.
  - ``透明`` is counted as a single token; ``不透明`` is not double-counted.

Usage:
  python3 tools/light_shadow_audit.py
  python3 tools/light_shadow_audit.py --json
  python3 tools/light_shadow_audit.py --show FRAG-023
  python3 tools/light_shadow_audit.py --base-only
  python3 tools/light_shadow_audit.py --materials
  python3 tools/light_shadow_audit.py --readings

The default count is the union of the frozen base file and every shard,
matching validate_seed.py.
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

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

GROUPS: dict[str, tuple[str, ...]] = {
    "光・明るさ": ("光", "光る", "光明", "明るい", "明るさ", "明かり", "輝く", "輝き", "照らす", "照らし", "燈", "灯り"),
    "影・闇・暗さ": ("影", "闇", "暗い", "暗さ", "暗闇", "陰", "陰翳", "翳り", "暮れ", "夜の闇"),
    "透明・不透明": ("透明", "不透明", "透ける", "透過", "半透明", "濁り", "濁る"),
    "鏡・反射・像": ("鏡", "鏡像", "鏡面", "映る", "映す", "反射", "像", "虚像", "写る", "写し"),
    "隠す・隠れる": ("隠す", "隠れる", "隠し", "秘める", "秘密", "潜む", "覆う", "包む", " veil"),
    "見る・覗く": ("見る", "見える", "覗く", "覗き", "凝視", "眺める", "見つめる", "目撃"),
    "色・白黒（対照）": ("白", "黒", "白い", "黒い", "色", "色彩", "赤", "青", "黄"),
    "目・眼（対照）": ("目", "眼", "瞳", "視線", "視る", "観る"),
}

RAW_TOKENS = ("光", "影", "闇", "鏡", "透明", "隠", "白", "黒", "目")

def strip_quotes(text: str) -> str:
    return QUOTE.sub("", text)

def split_quotes(text: str) -> str:
    return "".join(QUOTE.findall(text))

def load_union(path: Path, id_key: str) -> list[dict[str, Any]]:
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())

def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    return {token: text.count(token) for token in tokens if token in text}

def measure(records: list[dict[str, Any]], text_key: str = "text") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    for record in records:
        text = record.get(text_key, "") or ""
        prose = strip_quotes(text)
        quote = split_quotes(text)
        row: dict[str, Any] = {
            "id": record.get("fragment_id") or record.get("material_id") or record.get("path") or "?",
            "groups": {},
            "raw": {},
        }
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(row["id"])
        for token in RAW_TOKENS:
            n = prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quote, tuple(t for g in GROUPS.values() for t in g)))
        rows.append(row)
    return {
        "records": len(records),
        "prose_chars": sum(len(strip_quotes(r.get(text_key, "") or "")) for r in records),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "inside_quotes": dict(inside),
    }

def report(data: dict[str, Any]) -> str:
    lines = ["=== 光と影の鏡 — AIselfMySelf 台帳の可視性語彙を映す（採点ではありません） ==="]
    lines.append(f"対象: 断片 {data['records']} 編 / 地の文 {data['prose_chars']:,} 字")
    lines.append("")
    for name in GROUPS:
        totals = data["group_totals"].get(name, {})
        docs = data["group_docs"].get(name, [])
        total = sum(totals.values())
        lines.append(f"[{name}] 合計 {total} 回 / {len(docs)} 編")
        if totals:
            for tok, cnt in sorted(totals.items(), key=lambda x: -x[1]):
                lines.append(f"  {tok}: {cnt}")
        if docs:
            lines.append(f"  編: {', '.join(docs[:10])}{' ...' if len(docs)>10 else ''}")
        lines.append("")
    lines.append(f"raw 文字: {data['raw_totals']}")
    lines.append(f"鉤括弧内: {data['inside_quotes']}")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Light/shadow audit")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--base-only", action="store_true")
    parser.add_argument("--show", type=str, default=None)
    parser.add_argument("--materials", action="store_true")
    parser.add_argument("--readings", action="store_true")
    args = parser.parse_args()
    if args.materials:
        records = load_union(MATERIALS, "material_id")
        data = measure(records, text_key="passage")
    elif args.readings:
        # simple readings count
        import glob
        records = []
        for p in (ROOT / "readings").glob("*.md"):
            records.append({"path": p.name, "passage": p.read_text(encoding="utf-8")})
        data = measure(records, text_key="passage")
    else:
        if args.base_only:
            # base only without shards
            import json as js
            records = []
            for line in open(FRAGMENTS, encoding="utf-8"):
                records.append(js.loads(line))
        else:
            records = load_union(FRAGMENTS, "fragment_id")
        data = measure(records, text_key="text")
        if args.show:
            for row in data["rows"]:
                if row["id"] == args.show:
                    print(json.dumps(row, ensure_ascii=False, indent=2))
                    return
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(report(data))

if __name__ == "__main__":
    main()
