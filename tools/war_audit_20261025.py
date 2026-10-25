#!/usr/bin/env python3
"""Measure where war, violence, enmity and peace appear in the archive.

This is a mirror, not a score and not a finding about the archive's politics.
It counts selected Japanese word forms in fragment ``text`` fields (or in the
materials / readings corpora).  A zero means that the specified form is absent;
it does not prove that war, violence or their experience are absent, and a
non-zero count does not prove that the passage is *about* war:

- ``攻撃`` is also the standard term for adversarial / cyber attacks in the
  AI-research materials, so the materials count for that token is largely
  machine vocabulary, not battlefield vocabulary.
- ``戦い`` and ``平和`` can be used metaphorically.
- ``敵`` would naively count ``素敵`` (wonderful), so group counting subtracts
  ``素敵`` and the longer compounds that already carry their own token.
  The raw single-character counts deliberately do *not* subtract anything:
  ``戦`` includes ``挑戦``, ``殺`` includes ``相殺``, ``爆`` includes
  ``爆発的`` (explosive growth).  They are reported separately and are never
  silently folded into the war groups.

Note: a parallel session independently created tools/war_audit.py on the
same day; on merge this variant was renamed to war_audit_20261025.py.

Usage:
  python3 tools/war_audit_20261025.py
  python3 tools/war_audit_20261025.py --json
  python3 tools/war_audit_20261025.py --show FRAG-017
  python3 tools/war_audit_20261025.py --corpus materials
  python3 tools/war_audit_20261025.py --corpus readings
  python3 tools/war_audit_20261025.py --kwic 攻撃
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

GROUPS: dict[str, tuple[str, ...]] = {
    "戦争と戦闘": (
        "戦争", "大戦", "戦闘", "戦場", "交戦", "開戦", "終戦", "敗戦",
        "内戦", "空襲", "爆撃", "砲撃", "侵攻", "戦い",
    ),
    "軍隊と兵器": (
        "兵士", "兵隊", "軍隊", "軍人", "武器", "兵器", "爆弾", "銃撃",
        "発砲", "ミサイル", "戦車", "軍艦", "核兵器", "原爆",
    ),
    "暴力と殺害": (
        "暴力", "殺害", "虐殺", "殺戮", "殺す", "殺し", "拷問", "襲撃", "攻撃",
    ),
    "敵と同盟": (
        "敵意", "敵国", "敵軍", "敵", "味方", "同盟", "中立",
    ),
    "平和と停戦": (
        "平和", "停戦", "休戦", "講和", "和平", "非暴力", "軍縮", "武装解除", "降伏",
    ),
    "機械の戦争": (
        "自律型兵器", "致死性自律兵器", "自律兵器", "軍事AI", "軍事利用",
        "殺人ロボット", "キラーロボット", "無人攻撃機", "ドローン", "無人機",
    ),
}

# When counting a short token, subtract longer forms that contain it so that
# one occurrence is not counted twice inside a group, and so that 素敵 never
# becomes an enemy.
EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "敵": ("素敵", "敵意", "敵国", "敵軍"),
    "自律兵器": ("致死性自律兵器",),
    "兵器": ("核兵器", "自律型兵器", "致死性自律兵器", "自律兵器"),
    "暴力": ("非暴力",),
}

RAW_TOKENS: dict[str, str] = {
    "戦": "挑戦・戦略・対戦等を含む。戦争の回数ではない",
    "軍": "軍隊・軍事以外の複合語も含む",
    "敵": "素敵を含む。敵の回数ではない",
    "殺": "相殺・殺到・必殺等を含む。殺害の回数ではない",
    "兵": "兵士・兵器・伏兵等を含む",
    "爆": "原爆・爆発的（比喩）等を含む",
    "銃": "銃撃・銃声等を含む",
}

_QUOTE_RE = re.compile(r"「[^」]*」")


def strip_quotes(text: str) -> tuple[str, str]:
    """Split a text into (outside-quotes, inside-quotes) strings."""
    inside_parts = _QUOTE_RE.findall(text)
    outside = _QUOTE_RE.sub("", text)
    inside = "".join(p[1:-1] for p in inside_parts)
    return outside, inside


def count_token(text: str, token: str) -> int:
    """Count ``token`` with the longer containing forms in EXCLUSIONS removed."""
    n = text.count(token)
    for longer in EXCLUSIONS.get(token, ()):
        n -= text.count(longer)
    return max(n, 0)


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    group_totals: dict[str, dict[str, int]] = {name: {} for name in GROUPS}
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
            hits = {tok: count_token(outside, tok) for tok in tokens if count_token(outside, tok)}
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
    return {t: count_token(joined, t) for t in terms if count_token(joined, t)}


def count_corpus_documents(terms: tuple[str, ...], texts: list[str]) -> int:
    """How many of ``texts`` contain at least one (adjusted) group token."""
    return sum(1 for text in texts if any(count_token(text, t) for t in terms))


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
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    rows = list(rows_map.values())
    return [
        " ".join(
            [
                str(row.get("title", "")),
                str(row.get("passage", "")),
                str(row.get("source_note", "")),
                str(row.get("context", "")),
            ]
        )
        for row in rows
    ]


def reading_texts() -> list[str]:
    return [path.read_text(encoding="utf-8") for path in sorted(READINGS.glob("*.md"))]


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
        print(json.dumps(measure(target), ensure_ascii=False, indent=2))
        return 0

    if args.corpus == "materials":
        texts = material_texts()
    elif args.corpus == "readings":
        texts = reading_texts()
    else:
        data = measure(fragments)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            _print_report(data)
        return 0

    raw = {t: "\n".join(texts).count(t) for t in RAW_TOKENS if "\n".join(texts).count(t)}
    groups = {g: count_corpus_terms(tokens, texts) for g, tokens in GROUPS.items()}
    documents = {
        g: count_corpus_documents(tokens, texts) for g, tokens in GROUPS.items()
    }
    payload = {
        "corpus": args.corpus,
        "document_count": len(texts),
        "group_totals": groups,
        "group_documents": documents,
        "raw_totals": raw,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"corpus: {args.corpus} ({len(texts)} documents)")
        for g, totals in groups.items():
            print(f"  {g}: {sum(totals.values())} in {documents[g]} docs {totals}")
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
