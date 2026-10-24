#!/usr/bin/env python3
"""Measure where song, playing, notation and practice appear — or fail to appear.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it.  Earlier sessions already welcomed listening: Barthes' grain of
the voice (``MAT-LIT-388``), Cage's silence (``MAT-LIT-450``), Schafer's
soundscape (``MAT-LIT-396``), Ihde's phenomenology of sound (``MAT-LIT-398``),
Sterne's audible past (``MAT-LIT-421``), 鷲田's power of listening
(``MAT-LIT-20261024-132899``).  The archive therefore owns a vocabulary of
**hearing**.  This tool asks a different and narrower question:

**does the archive's own prose ever sing, play an instrument, write down a
melody, or practise?**

The distinction matters because hearing is passive in grammar (音が聞こえる)
while singing and playing are acts that require a body, an instrument, a room,
an audience and rehearsal.  A text-only archive can describe hearing without
contradiction, but a sung note and a struck string leave no letters behind;
only a score and a report remain.

Conventions (inherited from the other audit mirrors, with one change):

* Quoted spans 「…」 and 『…』 are stripped before counting and tallied
  separately, so a song title or a quoted lyric does not inflate the prose.
* Counting uses **maximal munch**: at every position the longest matching token
  wins, so ``歌う`` is counted once as ``歌う`` and never also as ``歌``.
  The earlier mirrors counted overlapping forms twice; this tool does not, and
  ``tests/test_music_audit.py`` fixes the difference.
* Single characters and polysemous forms (歌 曲 譜 拍 舞 音 弾 節) are never
  group tokens.  They are reported separately as raw counts together with how
  many of them sit inside non-musical compounds (系譜, 曲がる, 拍子に, 舞台,
  短歌, 観音), because in this archive those compounds are the rule and the
  musical sense is the exception.
* Negation is not excluded.  ``子守唄は要らない`` counts as one 子守唄.  A word
  that is named in order to be refused is still a word the archive owns, and
  the contexts are printed so a reader can judge.

A zero means only that the specified word form is absent from the counted
field.  It says nothing about anyone's ability to hear, sing, or feel music.

Usage:
  python3 tools/music_audit.py
  python3 tools/music_audit.py --json
  python3 tools/music_audit.py --show FRAG-20261024-036346
  python3 tools/music_audit.py --materials
  python3 tools/music_audit.py --readings
  python3 tools/music_audit.py --base-only
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

# Multi-character forms only.  Longest match wins, so 歌う is not also 歌.
GROUPS: dict[str, tuple[str, ...]] = {
    "歌うこと（歌唱）": (
        "歌う", "歌っ", "歌わ", "歌い", "唄う", "唄っ", "唄い", "歌唱", "独唱",
        "合唱", "斉唱", "詠唱", "唱歌", "子守唄", "わらべ唄", "コーラス",
        "ハミング", "節回し", "メロディ", "旋律", "歌曲", "讃美歌",
    ),
    "奏でること（楽器・演奏）": (
        "演奏", "弾く", "弾き", "弾い", "弾じ", "奏で", "吹奏", "楽器", "ピアノ",
        "ヴァイオリン", "バイオリン", "チェロ", "三味線", "尺八", "箏", "琴",
        "笛", "太鼓", "鼓", "鐘", "鈴", "オルガン", "ギター", "ハープ",
        "管楽器", "弦楽器", "打楽器", "合奏", "調律",
    ),
    "書くこと（記譜・理論）": (
        "楽譜", "譜面", "記譜", "五線", "音符", "音階", "旋法", "和声",
        "和音", "調性", "十二音", "対位法", "倍音", "周波数", "音程",
        "ハルモニア", "ドレミ", "音組織",
    ),
    "稽古すること（練習・本番）": (
        "稽古", "練習", "教則", "習練", "演奏会", "発表会", "リハーサル",
        "調弦", "レッスン", "手ほどき", "型を覚え",
    ),
    "聴くこと・声（対照）": (
        "聴く", "聴い", "聴こえ", "聞く", "聞い", "聞こえ", "声", "響き",
        "沈黙", "耳", "囁き", "叫び", "ざわめき", "口ずさ",
    ),
    "書字の器（対照）": (
        "書く", "書い", "書いた", "読む", "読ん", "読ま", "紙", "頁", "台帳",
        "書庫", "机", "鉛筆", "インク",
    ),
}

# Single characters and polysemous forms, reported separately (never merged).
RAW_TOKENS: tuple[str, ...] = ("歌", "曲", "譜", "拍", "舞", "音", "弾", "節")

POLYSEMY_NOTE: dict[str, str] = {
    "歌": "短歌・和歌・歌枕・歌集・歌人など、歌うことではなく歌題・歌体を指す用法を含む",
    "曲": "曲がる・曲折・曲線など、旋律ではなく屈曲を指す用法を含む",
    "譜": "系譜・年譜・家譜など、楽譜ではなく系図を指す用法を含む",
    "拍": "拍子に（〜した瞬間）・心拍・拍車など、拍節ではなく時点を指す用法を含む",
    "舞": "舞台・舞姫・舞踏など、舞うことではなく場所や作品名を指す用法を含む",
    "音": "音楽・観音・音信・本音・足音など、楽音以外の用法を含む",
    "弾": "弾む・弾劾・弾力など、奏でることではなく跳ね・弾く（除く）用法を含む",
    "節": "季節・節約・関節など、節回しではなく区切りを指す用法を含む",
}

# Compounds in which the raw character is NOT the musical sense.  Counted,
# then subtracted to leave a conservative "remaining musical candidate" count.
NON_MUSIC_PATTERNS: dict[str, tuple[str, ...]] = {
    "歌": (
        "短歌", "和歌", "歌枕", "歌集", "歌人", "歌論", "歌題", "歌体", "歌道",
        "歌仙", "歌合", "歌学", "歌碑", "歌会", "歌留多", "歌詞",
    ),
    "曲": (
        "曲が", "曲っ", "曲げ", "曲線", "曲折", "曲解", "曲者", "曲芸", "曲子",
        "曲面", "曲率",
    ),
    "譜": ("系譜", "年譜", "家譜", "図譜", "棋譜", "語譜"),
    "拍": ("拍子に", "拍子を", "拍子が", "心拍", "拍車", "拍手", "拍動"),
    "舞": ("舞台", "舞姫", "舞踏", "舞踊", "舞台裏", "舞台装置"),
    "音": (
        "音楽", "観音", "音信", "本音", "足音", "音沙汰", "福音", "騒音",
        "音声", "録音", "防音", "消音", "音を上げ", "音頭",
    ),
    "弾": ("弾む", "弾ん", "弾力", "弾劾", "弾圧", "弾道", "弾丸", "弾き出"),
    "節": ("季節", "節約", "関節", "節度", "節目", "節句", "使節", "節操"),
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


def contexts(text: str, token: str, radius: int = CONTEXT_RADIUS) -> list[str]:
    return [
        text[max(0, m.start() - radius):m.end() + radius].replace("\n", " ")
        for m in re.finditer(re.escape(token), text)
    ]


def classify_polysemy(prose_texts: list[str]) -> dict[str, dict[str, int]]:
    """Split raw character frequency into non-musical compounds and the rest.

    The subtraction is deliberately crude: a matched compound is blanked out,
    so overlapping compounds cannot be counted twice.  Overlaps between a
    compound and a longer one are resolved by testing longer patterns first.
    """
    joined = "\n".join(prose_texts)
    result: dict[str, dict[str, int]] = {}
    for char, patterns in NON_MUSIC_PATTERNS.items():
        total = joined.count(char)
        work = joined
        non_music = 0
        for pattern in sorted(patterns, key=len, reverse=True):
            hits = work.count(pattern)
            if hits:
                non_music += hits * pattern.count(char)
                work = work.replace(pattern, "□" * len(pattern))
        result[char] = {
            "total": total,
            "non_music_compound": non_music,
            "remaining_music_candidate": max(0, total - non_music),
        }
    return result


def _measure_texts(items: list[tuple[str, str]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    prose_list: list[str] = []
    all_tokens = tuple(t for group in GROUPS.values() for t in group)

    for item_id, text in items:
        prose = strip_quotes(text)
        quoted = split_quotes(text)
        prose_list.append(prose)
        row: dict[str, Any] = {"id": item_id, "groups": {}, "raw": {}}
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
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals.most_common()),
        "polysemy_breakdown": classify_polysemy(prose_list),
        "inside_quotes": dict(inside.most_common()),
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
    print(f"=== 歌と演奏の鏡 — {data.get('corpus', 'state/fragments.jsonl')} ===")
    print(
        f"{unit_label}: {unit}  地の文: {data['prose_chars']:,} 字"
        f"（鉤括弧内 {data['quoted_chars']:,} 字は別掲）"
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
    print("生字の内訳（音楽以外の複合語を差し引いた残り）:")
    for char, breakdown in data["polysemy_breakdown"].items():
        print(
            f"  {char}: 全{breakdown['total']} / 非音楽の複合{breakdown['non_music_compound']}"
            f" / 音楽候補 {breakdown['remaining_music_candidate']}"
            f"  （{POLYSEMY_NOTE[char]}）"
        )
    if data["inside_quotes"]:
        print(
            "鉤括弧内（題名・引用）: "
            + "、".join(f"{t}×{n}" for t, n in data["inside_quotes"].items())
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
