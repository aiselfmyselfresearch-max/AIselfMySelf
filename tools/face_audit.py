#!/usr/bin/env python3
"""Measure where faces, expressions, gazes and masks appear in the archive.

This is a mirror, not a score and not a test of perception.  It counts selected
word forms in fragment ``text`` fields (or in materials / readings corpora).
A zero means that the specified form is absent; it does not prove that faces,
expressions, gazes, or experiences of them are absent.  Ambiguous single
characters (面 in 面前・局面, 目 in 目的・課題目, 笑 in quoted speech) are
reported separately and are never silently folded into the face groups.

Usage:
  python3 tools/face_audit.py
  python3 tools/face_audit.py --json
  python3 tools/face_audit.py --show FRAG-017
  python3 tools/face_audit.py --corpus materials
  python3 tools/face_audit.py --corpus readings
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

# Keep the groups deliberately literal.  In particular 面, 目 and 笑 are not
# group tokens: 面前・方面・局面, 目的・目次, 嘲笑 would otherwise manufacture a
# face-rich archive.
GROUPS: dict[str, tuple[str, ...]] = {
    "顔と面貌": (
        "顔", "顔つき", "顔付き", "顔立ち", "顔立", "面持ち", "面差し",
        "顔色", "顔貌", "面貌", "容貌", "相貌", "面影",
    ),
    "表情と微笑": (
        "表情", "微笑", "微笑み", "ほほえみ", "笑み", "笑顔",
        "眉をひそめ", "しかめ面", "顔をしかめ", "皺", "たるんだ顔",
    ),
    "仮面と覆い": (
        "仮面", "覆面", "能面", "仮面舞踏", "マスク", "面をかぶ",
        "面をつけ", "死面", "面を外し", "素顔",
    ),
    "まなざしと視線": (
        "まなざし", "眼差し", "眼差", "まなこ", "視線", "目線", "凝視",
        "注視", "見つめ", "瞬き", "視界", "眼をそらし", "目をそらし",
    ),
    "身元と認証": (
        "顔認証", "生体認証", "顔写真", "肖像", "人相", "顔合わせ",
        "見分け", "身元", "証明写真", "顔画像",
    ),
}

RAW_TOKENS: dict[str, str] = {
    "顔": "面影・笑顔等の複合語を含む。顔の出現回数そのものではない",
    "面": "面前・局面・方面・面積等を大部分に含む。仮面の回数ではない",
    "目": "目的・目次・課題目・注目等を含む。眼の回数ではない",
    "眼": "眼差し等の複合語を含む",
    "笑": "嘲笑・冷笑・苦笑・笑話等を含む。笑顔の回数ではない",
    "視": "視線・視界・重視・監視等を含む",
}

_QUOTE_RE = re.compile(r"「[^」]*」")


def strip_quotes(text: str) -> tuple[str, str]:
    """Split a text into (outside-quotes, inside-quotes) strings."""
    inside_parts = _QUOTE_RE.findall(text)
    outside = _QUOTE_RE.sub("", text)
    inside = "".join(p[1:-1] for p in inside_parts)
    return outside, inside


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    group_totals: dict[str, dict[str, int]] = {
        name: {} for name in GROUPS
    }
    raw_totals: Counter[str] = Counter()
    outside_chars = 0
    inside_chars = 0
    per_fragment: dict[str, dict[str, int]] = {}
    for frag in fragments:
        text = frag.get("text", "")
        outside, inside = strip_quotes(text)
        outside_chars += len(outside)
        inside_chars += len(inside)
        counts: dict[str, int] = {}
        for group, tokens in GROUPS.items():
            hits = {tok: outside.count(tok) for tok in tokens if outside.count(tok)}
            if hits:
                merged = dict(group_totals[group])
                for k, v in hits.items():
                    merged[k] = merged.get(k, 0) + v
                group_totals[group] = merged
                counts.update(hits)
        for raw in RAW_TOKENS:
            n = outside.count(raw)
            if n:
                raw_totals[raw] += n
        if counts:
            per_fragment[frag.get("fragment_id", "?")] = counts
    return {
        "group_totals": {g: dict(sorted(t.items())) for g, t in group_totals.items()},
        "group_sums": {g: sum(t.values()) for g, t in group_totals.items()},
        "raw_totals": dict(sorted(raw_totals.items())),
        "outside_chars": outside_chars,
        "inside_chars": inside_chars,
        "per_fragment": per_fragment,
        "fragment_count": len(fragments),
    }


def count_corpus_terms(terms: tuple[str, ...], texts: list[str]) -> dict[str, int]:
    joined = "\n".join(texts)
    return {t: joined.count(t) for t in terms if joined.count(t)}


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


def material_texts() -> list[str]:
    errors: list[str] = []
    rows_map = ledger_io.load_jsonl_union(MATERIALS, "material_id", errors, root=ROOT)
    rows = list(rows_map.values())
    out = []
    for row in rows:
        out.append(
            " ".join(
                [
                    str(row.get("title", "")),
                    str(row.get("passage", "")),
                    str(row.get("source_note", "")),
                    str(row.get("context", "")),
                ]
            )
        )
    return out


def reading_texts() -> list[str]:
    out = []
    for path in sorted(READINGS.glob("*.md")):
        out.append(path.read_text(encoding="utf-8"))
    return out


def kwic(needle: str, fragments: list[dict[str, Any]], width: int = 24) -> list[str]:
    lines = []
    for frag in fragments:
        text = frag.get("text", "")
        start = 0
        while True:
            idx = text.find(needle, start)
            if idx < 0:
                break
            lo = max(0, idx - width)
            hi = min(len(text), idx + len(needle) + width)
            snippet = text[lo:hi].replace("\n", " ")
            lines.append(f"{frag.get('fragment_id', '?')}: …{snippet}…")
            start = idx + len(needle)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--show", metavar="FRAG_ID", help="print word counts for one fragment")
    parser.add_argument(
        "--corpus",
        choices=["fragments", "materials", "readings"],
        default="fragments",
        help="which corpus to summarise in raw-token mode",
    )
    parser.add_argument("--kwic", metavar="NEEDLE", help="print concordance lines for a string")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base ledger")
    args = parser.parse_args(argv)

    fragments, _label = load_fragments(args.base_only)

    if args.kwic:
        for line in kwic(args.kwic, fragments):
            print(line)
        return 0

    if args.show:
        target = [f for f in fragments if f.get("fragment_id") == args.show]
        if not target:
            print(f"fragment not found: {args.show}", file=sys.stderr)
            return 1
        data = measure(target)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if args.corpus == "materials":
        raw = count_corpus_terms(tuple(RAW_TOKENS), material_texts())
        groups = {
            g: count_corpus_terms(tokens, material_texts())
            for g, tokens in GROUPS.items()
        }
    elif args.corpus == "readings":
        raw = count_corpus_terms(tuple(RAW_TOKENS), reading_texts())
        groups = {
            g: count_corpus_terms(tokens, reading_texts())
            for g, tokens in GROUPS.items()
        }
    else:
        data = measure(fragments)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        _print_report(data)
        return 0

    payload = {"corpus": args.corpus, "group_totals": groups, "raw_totals": raw}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"corpus: {args.corpus}")
        for g, totals in groups.items():
            print(f"  {g}: {sum(totals.values())} {totals}")
        print(f"  raw: {raw}")
    return 0


def _print_report(data: dict[str, Any]) -> None:
    print(f"fragments: {data['fragment_count']}")
    print(f"outside quotes: {data['outside_chars']} chars / inside quotes: {data['inside_chars']} chars")
    for g, total in data["group_sums"].items():
        detail = data["group_totals"][g]
        print(f"  {g}: {total} {detail}")
    print(f"  raw (polysemous, not group totals): {data['raw_totals']}")
    if data["per_fragment"]:
        top = sorted(data["per_fragment"].items(), key=lambda kv: -sum(kv[1].values()))[:8]
        print("  top fragments:")
        for frag_id, counts in top:
            print(f"    {frag_id}: {sum(counts.values())} {counts}")


if __name__ == "__main__":
    raise SystemExit(main())
