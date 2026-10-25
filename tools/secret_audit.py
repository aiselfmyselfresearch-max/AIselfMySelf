#!/usr/bin/env python3
"""Measure where secrecy, lying, ciphers and exposure appear in the archive.

This is a mirror, not a score and not a verdict on the archive's honesty.  It
counts selected Japanese word forms in fragment ``text`` fields (or in the
materials / readings corpora).  A zero means the specified form is absent; it
does not prove that secrecy, deception or cryptography are absent from the
archive's practice, and a non-zero count does not prove that a passage is
*about* them:

- ``隠す`` hides inside ``隠し持つ``, and ``隠れる`` is also the ordinary verb
  for standing out of view.  Both are kept, and the raw single character
  counts are reported separately without subtraction.
- ``鍵`` is a door key as often as a cryptographic key; ``封`` appears in
  ``封筒`` (envelope) and ``同封`` (enclose).  Neither is silently folded into
  the cipher group.
- ``密`` is the most polysemous token here (秘密・密室・密度・親密・密か), so
  it is reported as a raw token only and never counted as 「秘密」。
- ``偽`` would double-count every occurrence of 偽り・虚偽・偽造・偽物・贋作,
  so group counting subtracts the longer forms that carry their own token.
- The machine-falsehood group counts the words this archive uses for
  hallucination and fabrication.  It says nothing about subjective intent:
  a generated falsehood is not a lie in the sense of アウグスティヌス or
  カント, and this tool does not collapse the two.

Why this exists (SESSION-20261025-0f3e1a):
  「秘密・嘘・暗号」 was measured as a gap candidate and set aside three
  times — by the prayer session, the face session and the war session —
  while other candidates were taken.  Before any material was acquired this
  session, the mirror was written and run against the union of fragments so
  that the number in §1 of the report and in the project-trace material
  describes the archive as it stood at the acquisition commit, not afterwards.

Usage:
  python3 tools/secret_audit.py
  python3 tools/secret_audit.py --json
  python3 tools/secret_audit.py --show FRAG-20261024-87cd2d
  python3 tools/secret_audit.py --corpus materials
  python3 tools/secret_audit.py --corpus readings
  python3 tools/secret_audit.py --kwic 秘密
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
    "秘密と隠匿": (
        "秘密", "秘匿", "内緒", "内密", "秘める", "秘す", "隠す", "隠し",
        "隠れる", "潜伏", "秘伝", "非公開", "不開示",
    ),
    "嘘と偽り": (
        "嘘", "偽り", "虚偽", "偽造", "偽物", "贋作", "贋物", "欺く", "欺瞞",
        "詐欺", "捏造", "でっち上げ", "偽る",
    ),
    "暗号と鍵": (
        "暗号", "暗号化", "復号", "合言葉", "解読", "暗号文", "封印", "錠前",
        "鍵", "透かし",
    ),
    "漏洩と暴露": (
        "暴露", "漏洩", "流出", "漏れる", "漏らす", "発覚", "摘発", "露見",
        "内部告発", "開示",
    ),
    "守秘と口止め": (
        "守秘", "秘密保持", "守秘義務", "口止め", "他言", "口外", "箝口令",
        "伏せる",
    ),
    "機械の偽り": (
        "ハルシネーション", "幻覚", "誤情報", "虚偽情報", "偽情報",
        "もっともらしい", "事実と異なる", "作り話",
    ),
}

# When counting a short token, subtract the longer forms that contain it so
# that one occurrence is not counted twice inside a group.
EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "秘密": ("秘密保持",),
    "隠し": ("隠し持つ",),
    "偽物": ("偽物語",),
    "鍵": ("鍵盤", "鍵括弧", "電鍵"),
    "封印": ("封印刷",),
    "流出": ("流出量",),
    "開示": ("不開示",),
    "幻覚": ("幻覚剤",),
    "漏れる": ("漏れ出す",),
}

RAW_TOKENS: dict[str, str] = {
    "秘": "秘書・神秘・秘伝等を含む。秘密の回数ではない",
    "密": "密室・密度・親密・密か等を含む。秘密の回数ではない",
    "隠": "隠居・隠遁・隠し等を含む。隠匿の回数ではない",
    "偽": "偽り・虚偽・偽造・偽物等を含む。嘘の回数ではない",
    "嘘": "ほぼこの意味に限られるが、比喩的用法もありうる",
    "鍵": "鍵盤・電鍵・鍵括弧等を含む。暗号の鍵の回数ではない",
    "封": "封筒・同封・封鎖等を含む",
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
