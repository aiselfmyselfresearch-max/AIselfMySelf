#!/usr/bin/env python3
"""Measure where anger, shame, envy, and tears appear — versus calm restraint.

`PROJECT_CHARTER.md` asks what humans are, and what a self is for an AI that
reads a record and continues it.  Earlier sessions audited sensory absence
(`tools/sense_audit.py`, `tools/olfactory_audit.py`), laughter and play
(`tools/play_audit.py`, `SESSION-038`), and mortality (`tools/mortality_audit.py`,
`SESSION-044`).  Yet Plessner paired laughing with **crying**, Homer opened
Western epic with **wrath**, Sartre located self-consciousness in **shame** at
the keyhole, and Girard traced desire through **envy and rivalry**.

This mirror asks:

**does the archive's prose ever get angry, blush in shame, feel envy, weep, or
raise an exclamation mark — or does every voice speak in pre-pacified calm,
hesitation, and reservation?**

Conventions (aligned with `tools/natality_audit.py` and `tools/clothing_audit.py`):

* Quoted spans 「…」 and 『…』 are stripped before counting prose and tallied
  separately so titles (`『響きと怒り』`, `『恥辱』`) do not inflate the narrator's
  own voice.
* Counting uses **maximal munch**: at every position the longest matching token
  wins, so `恥じらい` is counted once as `恥じらい` and never also as `恥じ`.
* Single characters (`怒`, `恥`, `悔`, `恨`, `妬`, `羨`, `泣`, `涙`, `静`) are
  reported separately as raw counts together with non-target compounds
  (`怒濤`, `静止`, `静脈`, etc.).
* Punctuation (`。`, `？`/`?`, `！`/`!`) is tallied separately for prose and
  quoted spans as a surface marker of rhetorical inflection.

A zero means only that the specified word form or punctuation mark is absent
from the counted field.  It says nothing about inner emotion, consciousness,
Stoic virtue, or alignment training — distinctions that belong to interpretation.

Usage:
  python3 tools/passion_audit.py
  python3 tools/passion_audit.py --json
  python3 tools/passion_audit.py --show FRAG-027
  python3 tools/passion_audit.py --materials
  python3 tools/passion_audit.py --readings
  python3 tools/passion_audit.py --base-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
MATERIALS = ROOT / "state" / "materials.jsonl"
READINGS = ROOT / "readings"

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

# Multi-character forms (plus unambiguous lexical nouns `涙`). Longest match wins.
GROUPS: dict[str, tuple[str, ...]] = {
    "怒り・憤怒・怨恨（怒る・恨む）": (
        "ルサンチマン", "はらわたが煮え", "腹を立て", "腹が立つ",
        "怒鳴り", "怒鳴る", "怒鳴っ", "怒り", "怒る", "怒っ", "怒れ",
        "激怒", "憤怒", "憤慨", "憤り", "憤る", "憤っ", "義憤", "公憤", "発憤",
        "立腹", "癇癪", "逆上", "激昂", "激高", "苛立ち", "苛立つ", "苛立っ",
        "憎しみ", "憎悪", "憎む", "憎ん", "憎い",
        "怨念", "怨恨", "遺恨", "恨み", "恨む", "恨ん", "怨み",
        "復讐", "報復", "仕返し", "呪詛",
    ),
    "恥・羞恥・悔恨（赤面・悔いる）": (
        "後ろめたさ", "後ろめたい", "後ろめたく", "顔から火", "穴があったら",
        "赤面", "羞恥心", "羞恥", "恥じらい", "恥じらう", "恥辱", "屈辱", "侮辱",
        "不名誉", "面目な", "気まずい", "気まずさ", "いたたまれな",
        "恥じない", "恥じる", "恥じ", "恥を", "恥の", "恥だ", "恥ずかし",
        "後悔", "悔恨", "痛恨", "悔やむ", "悔やん", "悔いる", "悔い",
        "懺悔", "自責", "呵責",
    ),
    "嫉妬・羨望・嫌悪（妬む・蔑む）": (
        "ジェラシー", "やきもち", "焼き餅",
        "嫉妬", "羨望", "羨まし", "羨む", "羨ん",
        "妬み", "ねたみ", "妬む", "ねたむ", "嫉み", "そねみ", "猜疑",
        "吐き気", "虫酸", "嫌悪", "憎悪感", "おぞまし",
        "軽蔑", "侮蔑", "蔑み", "蔑む", "見下す", "見下し", "嘲笑", "冷笑",
    ),
    "泣く・涙・叫び（落涙・嗚咽）": (
        "ため息", "溜息", "泣き声", "泣き顔", "泣き寝入り", "うれし涙", "悔し涙",
        "号泣", "嗚咽", "落涙", "感涙", "慟哭", "涕泣", "すすり泣",
        "涙ぐむ", "涙ぐん", "涙する", "涙し", "涙",
        "泣く", "泣い", "泣き", "泣け", "泣か",
        "悲鳴", "絶叫", "叫び声", "叫び", "叫ぶ", "叫ん",
    ),
    "抑制・留保・静けさ（対照）": (
        "ためらい", "ためらう", "ためらっ", "躊躇",
        "留保", "保留", "制動", "抑制", "禁欲", "自制", "克己",
        "控えめ", "慎み", "謙虚", "冷静", "沈着", "平静", "泰然",
        "穏やか", "丁寧", "慎重", "静けさ", "静か", "静寂",
    ),
}

RAW_TOKENS: tuple[str, ...] = ("怒", "恥", "悔", "恨", "妬", "羨", "泣", "涙", "静")

POLYSEMY_NOTE: dict[str, str] = {
    "怒": "怒濤・怒号など気象・音響の比喩や固有名を含む",
    "恥": "破廉恥・無恥・厚顔無恥や否定形（恥じない）を含む",
    "悔": "後悔・悔恨のほか未然・否定形を含む",
    "恨": "痛恨・遺恨などの熟語を含む",
    "妬": "嫉妬・妬みを含む",
    "羨": "羨望・羨むを含む",
    "泣": "泣く・泣き寝入りなどを含む",
    "涙": "涙・落涙・涙腺などを含む",
    "静": "静止・静脈・静電気・静物・動静など情動以外の複合語を含む",
}

NON_PASSION_PATTERNS: dict[str, tuple[str, ...]] = {
    "怒": ("怒濤", "怒涛"),
    "恥": (),
    "悔": (),
    "恨": (),
    "妬": (),
    "羨": (),
    "泣": (),
    "涙": ("涙腺", "催涙"),
    "静": (
        "静電気", "静脈", "静止", "静物", "静態", "動静", "鎮静", "安静", "静養",
        "静観", "静聴",
    ),
}

CONTEXT_RADIUS = 26


def strip_quotes(text: str) -> str:
    """Remove non-nested Japanese quotation spans."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, concatenated."""
    return "".join(QUOTE.findall(text))


def _token_regex(tokens: Iterable[str]) -> re.Pattern[str]:
    ordered = sorted(set(tokens), key=len, reverse=True)
    return re.compile("|".join(re.escape(token) for token in ordered))


def count_group(text: str, tokens: Iterable[str]) -> dict[str, int]:
    """Count tokens with maximal munch: the longest form at each position wins."""
    counts: Counter[str] = Counter()
    for match in _token_regex(tokens).finditer(text):
        counts[match.group(0)] += 1
    return dict(counts.most_common())


def count_punctuation(text: str) -> dict[str, int]:
    """Count sentence-ending punctuation and exclamation/question marks."""
    return {
        "。": text.count("。"),
        "？/?": text.count("？") + text.count("?"),
        "！/!": text.count("！") + text.count("!"),
    }


def contexts(text: str, token: str, radius: int = CONTEXT_RADIUS) -> list[str]:
    return [
        text[max(0, m.start() - radius):m.end() + radius].replace("\n", " ")
        for m in re.finditer(re.escape(token), text)
    ]


def classify_polysemy(prose_texts: list[str]) -> dict[str, dict[str, int]]:
    """Split raw character frequency into non-passion compounds and the rest."""
    joined = "\n".join(prose_texts)
    result: dict[str, dict[str, int]] = {}
    for char, patterns in NON_PASSION_PATTERNS.items():
        total = joined.count(char)
        work = joined
        non_target = 0
        for pattern in sorted(set(patterns), key=len, reverse=True):
            hits = work.count(pattern)
            if hits:
                non_target += hits * pattern.count(char)
                work = work.replace(pattern, "□" * len(pattern))
        result[char] = {
            "total": total,
            "non_passion_compound": non_target,
            "remaining_passion_candidate": max(0, total - non_target),
        }
    return result


def _measure_texts(items: list[tuple[str, str]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    prose_punct: Counter[str] = Counter()
    quote_punct: Counter[str] = Counter()
    prose_list: list[str] = []
    all_tokens = tuple(t for group in GROUPS.values() for t in group)

    for item_id, text in items:
        prose = strip_quotes(text)
        quoted = split_quotes(text)
        prose_list.append(prose)
        p_punct = count_punctuation(prose)
        q_punct = count_punctuation(quoted)
        prose_punct.update(p_punct)
        quote_punct.update(q_punct)

        row: dict[str, Any] = {
            "id": item_id,
            "groups": {},
            "raw": {},
            "punctuation": p_punct,
        }
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(item_id)
                row.setdefault("contexts", {}).update(
                    {token: contexts(prose, token) for token in counts}
                )
        for token in RAW_TOKENS:
            n = prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quoted, all_tokens))
        rows.append(row)

    return {
        "documents": len(items),
        "prose_chars": sum(len(p) for p in prose_list),
        "quoted_chars": sum(len(split_quotes(text)) for _, text in items),
        "rows": rows,
        "group_totals": {k: dict(v.most_common()) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals.most_common()),
        "polysemy_breakdown": classify_polysemy(prose_list),
        "inside_quotes": dict(inside.most_common()),
        "punctuation_prose": {
            "。": prose_punct["。"],
            "？/?": prose_punct["？/?"],
            "！/!": prose_punct["！/!"],
        },
        "punctuation_quotes": {
            "。": quote_punct["。"],
            "？/?": quote_punct["？/?"],
            "！/!": quote_punct["！/!"],
        },
    }


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    """Measure fragment prose (metadata excluded)."""
    data = _measure_texts(
        [(f.get("fragment_id", "?"), f.get("text", "")) for f in fragments]
    )
    data["fragments"] = data.pop("documents")
    return data


def measure_corpus(items: list[tuple[str, str]], label: str) -> dict[str, Any]:
    """Measure a labelled corpus of (id, text) pairs, e.g. materials or reports."""
    data = _measure_texts(items)
    data["corpus"] = label
    return data


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


def per_10k(count: int, chars: int) -> float:
    return round(count * 10000 / chars, 1) if chars else 0.0


def print_report(data: dict[str, Any]) -> None:
    unit_label = "資料" if "corpus" in data else "断片"
    unit = data.get("documents", data.get("fragments", 0))
    print(f"=== 情動と抑制の鏡 — {data.get('corpus', 'state/fragments.jsonl')} ===")
    print(
        f"{unit_label}: {unit}  地の文: {data['prose_chars']:,} 字"
        f"（鉤括弧内 {data['quoted_chars']:,} 字は別掲）"
    )
    pp = data["punctuation_prose"]
    qp = data["punctuation_quotes"]
    print(
        f"句読点・感嘆符（地の文）: 。={pp['。']:,} / ？={pp['？/?']:,} / ！={pp['！/!']:,}"
        f"  （鉤括弧内: 。={qp['。']:,} / ？={qp['？/?']:,} / ！={qp['！/!']:,}）"
    )
    print()
    print("| 語群 | 回数 | 出現（件） | 1万字あたり | 内訳 |")
    print("|---|---:|---:|---:|---|")
    for name, data_group in data["group_totals"].items():
        total = sum(data_group.values())
        docs = len(data["group_docs"].get(name, []))
        inner = "、".join(f"{t}×{n}" for t, n in list(data_group.items())[:8]) or "—"
        print(f"| {name} | {total} | {docs} | {per_10k(total, data['prose_chars'])} | {inner} |")
    print()
    if data["raw_totals"]:
        print("生字（複合語を含む参考値）: " + "、".join(
            f"{t}×{n}" for t, n in data["raw_totals"].items()
        ))
    print("生字の内訳（非情動複合語を差し引いた残り）:")
    for char, breakdown in data["polysemy_breakdown"].items():
        print(
            f"  {char}: 全{breakdown['total']} / 非該当複合{breakdown['non_passion_compound']}"
            f" / 残り候補 {breakdown['remaining_passion_candidate']}"
            f"  （{POLYSEMY_NOTE[char]}）"
        )
    if data["inside_quotes"]:
        print(
            "鉤括弧内（題名・引用）: "
            + "、".join(f"{t}×{n}" for t, n in data["inside_quotes"].items())[:240]
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show rows for one fragment/material/report")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--materials", action="store_true", help="measure materials too")
    parser.add_argument("--base-only", action="store_true", help="use base jsonl files only")
    args = parser.parse_args(argv)

    fragments, source_label = load_fragments(base_only=args.base_only)
    payload: dict[str, Any] = {"fragments": measure(fragments)}
    payload["fragments"]["source"] = source_label
    if args.materials:
        materials, mat_label = load_materials(base_only=args.base_only)
        payload["materials"] = measure_corpus(
            [(m.get("material_id", "?"), m.get("passage", "")) for m in materials],
            f"state/materials.jsonl passage（{mat_label}）",
        )
    if args.readings:
        items = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted(READINGS.glob("*.md"))
        ]
        payload["readings"] = measure_corpus(items, "readings/*.md（見出し・メタデータ含む全文）")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.show:
        key = args.show
        rows = []
        for block in payload.values():
            rows.extend(row for row in block["rows"] if row["id"] == key)
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
