#!/usr/bin/env python3
"""Reflect how the archive's voices repeat themselves. A mirror, not a score.

`PROJECT_CHARTER.md` asks each session whether contradictions and multiple
readings were kept alive. That question cannot be automated. But one part of it
can be made visible: whether the fragments keep saying the same thing in the
same shape. This tool only reports what is written in `state/fragments.jsonl`
and `state/relations.jsonl`. It does not pass or fail anything, and the numbers
are not a quality score — they are a mirror for choosing the next move.

Note on calibration (SESSION-020):
  In SESSION-018/019, `is_question()` did not strip trailing Japanese periods
  (`。` / `．`), and preview lines truncated at 58 leading characters hid the
  actual sentence endings (`…青い光の方なの[だろうか。]`). As a result, period-ended
  questions such as FRAG-016's final sentence were counted as assertions (`0/17`
  instead of `1/17`). `question_kind()` now distinguishes question-mark endings
  (`？`) from period-ended questions (`〜だろうか。` / `〜のか。` / `〜か。`), and previews
  preserve the sentence tail so the mirror shows what it actually classifies.

Usage:
  python3 tools/voice_audit.py
  python3 tools/voice_audit.py --top 20
  python3 tools/voice_audit.py --gram 8
  python3 tools/voice_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

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

NARRATOR_MODE_ENUM = (
    "reflective_literary_voice",
    "fictional_first_person",
    "dialogue",
    "third_person",
    "other",
    "human_narrator",
)

# SESSION-027: the mirror had no column for laughter. Q-047 asks whether the
# thing this tool has always counted (repetition) is the very thing that makes
# a machine visible, and whether a library with no laughter has put something
# outside the human. Both questions are rhetorical until the count exists.
# The classification below is deliberately crude: it cannot tell whether
# anybody actually laughed, only which characters were written next to 笑.
LAUGH_CHAR = "笑"
LAUGH_MODIFIERS = ("冷", "苦", "嘲", "微", "失", "哄", "爆", "談")
LAUGH_ACTS = ("笑う", "笑った", "笑って", "笑い声", "笑い出", "笑え", "笑われ", "笑い合", "笑み")

# For section 8: how wide a window to keep on each side of a reused string.
CONTEXT_WIDTH = 10

PRONOUN_SPECS: tuple[tuple[str, str], ...] = (
    ("私（単数）", r"私(?!たち|達|的|物|記|見|小説|語|言|事|法|信|生活|自身|文書|家|鉄|立|権|益)"),
    ("わたし", r"わたし(?!たち)"),
    ("わたくし", r"わたくし(?!たち)"),
    ("僕", r"僕"),
    ("俺", r"俺"),
    # SESSION-024: `自分` was absent from this table, so the mirror could not see it.
    # Nine of the first 25 fragments used it, and FRAG-009 was therefore counted as
    # 人称代名詞ゼロ（無主語）even though its 地の文 contains `自分`.
    ("自分", r"自分"),
    ("おのれ", r"おのれ"),
    ("私たち・われわれ", r"(?:私たち|私達|わたしたち|わたくしたち|われわれ|我々)"),
    ("あなた", r"あなた"),
    ("君", r"君"),
    ("彼・彼女", r"(?:彼(?!女)|彼女)"),
)

FIRST_PERSON_UNQUOTED_RE = re.compile(
    r"(?:私たち|私達|わたしたち|わたくしたち|われわれ|我々|わたし|わたくし|僕|俺|自分|私(?!たち|達|的|物|記|見|小説|語|言|事|法|信|生活|自身|文書|家|鉄|立|権|益))"
)

# Stems ending in か that are nouns/adjectives rather than sentence-final question particles.
NON_QUESTION_KA_SUFFIXES = (
    "のなか",
    "のほか",
    "わずか",
    "さなか",
    "おろか",
    "たしか",
    "しずか",
    "はるか",
    "かすか",
    "ほのか",
    "さだか",
    "あきらか",
    "なだらか",
    "やわらか",
    "あたたか",
    "こまやか",
    "ひそやか",
    "おだやか",
    "すみやか",
    "ゆるやか",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
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
    parts = re.split(r"(?<=[。．！？\?\n])", text)
    return [p.strip() for p in parts if p.strip()]


def question_kind(sentence: str) -> str | None:
    """Return 'question_mark', 'period_question', or None."""
    trimmed_quotes = sentence.strip().rstrip("」』）) ")
    if trimmed_quotes.endswith(("？", "?")):
        return "question_mark"
    core = re.sub(r"[。．.」』）)\s]+$", "", sentence.strip())
    if not core or core.endswith(NON_QUESTION_KA_SUFFIXES):
        return None
    if re.search(r"(だろうか|のだろうか|のか|か)$", core):
        return "period_question"
    return None


def is_question(sentence: str) -> bool:
    return question_kind(sentence) is not None


def format_tail_preview(sentence: str, max_chars: int = 62) -> str:
    """Keep both head and actual sentence ending visible so endings are never hidden."""
    clean = re.sub(r"\s+", " ", sentence.strip())
    if len(clean) <= max_chars:
        return clean
    head_len = max_chars - 31
    return f"{clean[:head_len]}…{clean[-30:]}"


def count_fragments(fragments: list[dict[str, Any]], needles: list[str]) -> int:
    return sum(1 for f in fragments if any(n in f["text"] for n in needles))


def repeated_grams(fragments: list[dict[str, Any]], size: int) -> list[tuple[str, list[str]]]:
    owners: dict[str, set[str]] = defaultdict(set)
    for frag in fragments:
        flat = re.sub(r"\s+", "", frag["text"])
        for i in range(len(flat) - size + 1):
            gram = flat[i : i + size]
            if re.search(r"[ぁ-んァ-ン一-龥]", gram):
                owners[gram].add(frag["fragment_id"])
    return sorted(((g, sorted(o)) for g, o in owners.items() if len(o) > 1), key=lambda kv: (-len(kv[1]), kv[0]))


def laugh_audit(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    """Report every 笑 in the ledger with its neighbourhood (SESSION-027).

    The tool cannot decide whether a laugh happened. It can only show whether
    the ledger ever wrote one down, and what was written beside it.
    """
    hits: list[dict[str, Any]] = []
    fragments_with_laugh: list[str] = []
    for frag in fragments:
        text = frag["text"]
        found = False
        for match in re.finditer(LAUGH_CHAR, text):
            found = True
            start, end = match.start(), match.end()
            before = text[max(0, start - 12) : start]
            after = text[end : end + 12]
            # The character immediately following 笑 decides the kind.
            nxt = text[end : end + 2]
            prv = text[max(0, start - 1) : start]
            if prv and prv in LAUGH_MODIFIERS:
                kind = "修飾された笑い（冷笑・苦笑・嘲笑・微笑 など）"
            elif any(nxt.startswith(act[1:]) for act in LAUGH_ACTS) or any(a in text[start : start + 4] for a in LAUGH_ACTS):
                kind = "笑いの行為（笑う・笑った・笑い声 など）"
            else:
                kind = "その他"
            hits.append(
                {
                    "fragment_id": frag["fragment_id"],
                    "kind": kind,
                    "before": re.sub(r"\s+", " ", before),
                    "after": re.sub(r"\s+", " ", after),
                }
            )
        if found:
            fragments_with_laugh.append(frag["fragment_id"])
    kind_counts = Counter(hit["kind"] for hit in hits)
    return {
        "fragment_count": len(fragments_with_laugh),
        "fragments": fragments_with_laugh,
        "occurrences": len(hits),
        "kinds": dict(kind_counts.most_common()),
        "hits": hits,
    }


def repetition_contexts(
    fragments: list[dict[str, Any]], size: int, limit: int = 8
) -> list[dict[str, Any]]:
    """Do the reused strings sit in the same place, or in new ones? (SESSION-027)

    Q-044 asks which theory of repetition the mirror is actually measuring.
    A string that always appears in the same surrounding words is being
    recited; the same string in many different surroundings is being used as
    stock. This section cannot tell which is better. It can tell them apart.

    Overlapping n-grams from one shared sentence would flood the table, so a
    gram is dropped when it is a substring of a longer gram already kept.
    """
    owners: dict[str, set[str]] = defaultdict(set)
    lefts: dict[str, list[str]] = defaultdict(list)
    rights: dict[str, list[str]] = defaultdict(list)
    for frag in fragments:
        flat = re.sub(r"\s+", "", frag["text"])
        for i in range(len(flat) - size + 1):
            gram = flat[i : i + size]
            if not re.search(r"[ぁ-んァ-ン一-龥]", gram):
                continue
            owners[gram].add(frag["fragment_id"])
            lefts[gram].append(flat[max(0, i - CONTEXT_WIDTH) : i])
            rights[gram].append(flat[i + size : i + size + CONTEXT_WIDTH])

    candidates = [g for g, ids in owners.items() if len(ids) > 1 and len(lefts[g]) > 1]
    candidates.sort(key=lambda g: (-len(g), g))
    kept: list[str] = []
    for gram in candidates:
        if any(gram in longer for longer in kept):
            continue
        # Drop near-duplicates produced by sliding windows of the same sentence
        # ("かもしれない" / "のかもしれな"). A shared run of len-1 characters is
        # enough to call them the same phrase seen through two windows.
        if any(gram[:-1] in longer or gram[1:] in longer for longer in kept):
            continue
        kept.append(gram)

    rows = []
    for gram in kept:
        rows.append(
            {
                "gram": gram,
                "fragment_count": len(owners[gram]),
                "occurrences": len(lefts[gram]),
                "distinct_left": len(set(lefts[gram])),
                "distinct_right": len(set(rights[gram])),
                "sample": (lefts[gram][0], gram, rights[gram][0]),
            }
        )
    rows.sort(key=lambda r: (-r["occurrences"], -r["fragment_count"], r["gram"]))
    return rows[:limit]


def context_summary(fragments: list[dict[str, Any]], size: int) -> dict[str, Any]:
    """One number for section 8: are reused strings wearing new surroundings?"""
    owners: dict[str, set[str]] = defaultdict(set)
    lefts: dict[str, set[str]] = defaultdict(set)
    rights: dict[str, set[str]] = defaultdict(set)
    for frag in fragments:
        flat = re.sub(r"\s+", "", frag["text"])
        for i in range(len(flat) - size + 1):
            gram = flat[i : i + size]
            if not re.search(r"[ぁ-んァ-ン一-龥]", gram):
                continue
            owners[gram].add(frag["fragment_id"])
            lefts[gram].add(flat[max(0, i - CONTEXT_WIDTH) : i])
            rights[gram].add(flat[i + size : i + size + CONTEXT_WIDTH])
    ratios = []
    for gram, ids in owners.items():
        if len(ids) > 1 and len(lefts[gram]) > 1:
            ratios.append((len(lefts[gram]) + len(rights[gram])) / len(lefts[gram]))
    ratios.sort()
    if not ratios:
        return {"median_ratio": 0.0, "count": 0}
    mid = len(ratios) // 2
    median = ratios[mid] if len(ratios) % 2 else (ratios[mid - 1] + ratios[mid]) / 2
    return {"median_ratio": round(median, 2), "count": len(ratios), "max_ratio": round(ratios[-1], 2)}


def compute_voice_audit(
    fragments: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    *,
    top: int = 12,
    gram: int = 6,
) -> dict[str, Any]:
    total = len(fragments)
    ending_kind: Counter[str] = Counter()
    ending_subkind: Counter[str] = Counter()
    endings: list[dict[str, Any]] = []

    total_sentences = 0
    question_mark_sentences = 0
    period_question_sentences = 0
    fragments_with_any_question = 0

    for frag in fragments:
        sents = sentences(frag["text"])
        total_sentences += len(sents)
        frag_has_q = False
        for s in sents:
            qk = question_kind(s)
            if qk == "question_mark":
                question_mark_sentences += 1
                frag_has_q = True
            elif qk == "period_question":
                period_question_sentences += 1
                frag_has_q = True
        if frag_has_q:
            fragments_with_any_question += 1

        last = sents[-1] if sents else ""
        qk_last = question_kind(last)
        if qk_last is not None:
            kind = "問いの形"
            sub = "疑問符『？』" if qk_last == "question_mark" else "句点『。』の問い"
            ending_subkind[sub] += 1
        elif any(n in last for n in SUSPENSION):
            kind = "保留の宣言"
            sub = "保留の宣言"
        else:
            kind = "断定"
            sub = "断定"
        ending_kind[kind] += 1
        endings.append(
            {
                "fragment_id": frag["fragment_id"],
                "title": frag["title"],
                "kind": kind,
                "subkind": sub,
                "last_sentence": last,
                "preview": format_tail_preview(last),
            }
        )

    gestures = [
        {
            "label": "保留句を含む断片（答えを出さない／そのまま残す 等）",
            "count": count_fragments(fragments, SUSPENSION),
            "total": total,
        },
        {
            "label": "二項対立の型（か、それとも／どちらでもない）",
            "count": count_fragments(fragments, BINARY),
            "total": total,
        },
        {
            "label": "留保の型（かもしれない／のではないか）",
            "count": count_fragments(fragments, HEDGE),
            "total": total,
        },
        {
            "label": "明示された不-knowing（分からない／答はない）",
            "count": count_fragments(fragments, AVOWED_NOT_KNOWING),
            "total": total,
        },
        {
            "label": "本文中に問いの文を含む断片",
            "count": fragments_with_any_question,
            "total": total,
            "note": f"全 {total_sentences} 文中 {question_mark_sentences + period_question_sentences} 文（『？』={question_mark_sentences}, 句点『。』={period_question_sentences}）",
        },
        {
            "label": "末尾の一文が問いの形",
            "count": ending_kind["問いの形"],
            "total": total,
            "note": ", ".join(f"{k}={v}" for k, v in ending_subkind.items()) or "なし",
        },
    ]

    openers: Counter[str] = Counter()
    for frag in fragments:
        head = sentences(frag["text"])[0][:40]
        if re.match(r"^[A-Za-z0-9_\-一-龥ぁ-んァ-ン]{1,14}[:：]", head):
            kind = "対話ラベル"
        elif re.search(r"(建暦|大正|昭和|明治|承平|長保|かつて|前の|四百年|八百年|百年前|二千年|[一二三四五六七八九十百千]+年)", head):
            kind = "年代・先行の引用"
        elif head.startswith(("【", "A:", "B:")):
            kind = "見出し・ラベル"
        else:
            kind = "所感"
        openers[kind] += 1

    grams = repeated_grams(fragments, gram)
    shared_ids = {fid for _, owners in grams for fid in owners}

    density = []
    for frag in fragments:
        hits = sum(frag["text"].count(n) for n in SUSPENSION + HEDGE + BINARY)
        unquoted = re.sub(r"「[^」]*」|『[^』]*』", "", frag["text"])
        bare_hits = sum(unquoted.count(n) for n in SUSPENSION + HEDGE + BINARY)
        density.append(
            {
                "fragment_id": frag["fragment_id"],
                "title": frag["title"],
                "hits": hits,
                "unquoted_hits": bare_hits,
            }
        )
    density.sort(key=lambda item: (-item["hits"], item["fragment_id"]))

    pronouns = []
    for label, pattern in PRONOUN_SPECS:
        rx = re.compile(pattern)
        all_fids = [f["fragment_id"] for f in fragments if rx.search(f["text"])]
        bare_fids = [f["fragment_id"] for f in fragments if rx.search(re.sub(r"「[^」]*」|『[^』]*』", "", f["text"]))]
        pronouns.append(
            {
                "label": label,
                "count": len(all_fids),
                "unquoted_count": len(bare_fids),
                "fragment_ids": all_fids,
                "unquoted_fragment_ids": bare_fids,
            }
        )

    zero_pronoun_ids = []
    mode_counts = {m: 0 for m in NARRATOR_MODE_ENUM}
    mode_mismatches = []
    for frag in fragments:
        mode = frag["narrator_mode"]
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        if not any(re.search(pat, frag["text"]) for _, pat in PRONOUN_SPECS):
            zero_pronoun_ids.append(frag["fragment_id"])
        if mode == "third_person":
            unquoted = re.sub(r"「[^」]*」|『[^』]*』", "", frag["text"])
            fp_matches = sorted(set(FIRST_PERSON_UNQUOTED_RE.findall(unquoted)))
            if fp_matches:
                mode_mismatches.append(
                    {
                        "fragment_id": frag["fragment_id"],
                        "narrator_mode": mode,
                        "found": fp_matches,
                    }
                )

    return {
        "fragment_count": total,
        "relation_count": len(relations),
        "endings": endings,
        "ending_summary": dict(ending_kind.most_common()),
        "ending_subsummary": dict(ending_subkind.most_common()),
        "gestures": gestures,
        "openers": dict(openers.most_common()),
        "gram_size": gram,
        "repeated_gram_total": len(grams),
        "shared_fragment_count": len(shared_ids),
        "top_grams": [{"gram": g, "count": len(owners), "owners": owners} for g, owners in grams[:top]],
        "density": density,
        "pronouns": pronouns,
        "zero_pronoun_fragment_ids": zero_pronoun_ids,
        "narrator_mode_counts": mode_counts,
        "mode_mismatches": mode_mismatches,
        "laughter": laugh_audit(fragments),
        "repetition_contexts": repetition_contexts(fragments, gram),
        "context_summary": context_summary(fragments, gram),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--top", type=int, default=12, help="how many repeated grams to show (default 12)")
    parser.add_argument("--gram", type=int, default=6, help="character n-gram size (default 6)")
    parser.add_argument("--json", action="store_true", help="emit audit report as JSON")
    args = parser.parse_args()

    fragments = load_jsonl(FRAGMENTS)
    relations = load_jsonl(RELATIONS)
    if not fragments:
        print("no fragments to inspect")
        return 1

    report = compute_voice_audit(fragments, relations, top=args.top, gram=args.gram)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    total = report["fragment_count"]
    print("=== 声の鏡 — AIselfMySelf 台帳の反復を映す（採点ではありません） ===")
    print(f"対象: state/fragments.jsonl {total} 編 / state/relations.jsonl {report['relation_count']} 件")
    print()

    print("--- 1. 各断片の末尾一文（どう終わっているか） ---")
    for item in report["endings"]:
        tag = item["subkind"] if item["kind"] == "問いの形" else item["kind"]
        print(f"  {item['fragment_id']} [{tag}] {item['preview']}")
    print()
    summary_parts = [f"{k}={v}編" for k, v in report["ending_summary"].items()]
    print("  末尾の型:", ", ".join(summary_parts))
    print()

    print("--- 2. 台帳が繰り返し使う身振り ---")
    for row in report["gestures"]:
        extra = f"  ({row['note']})" if row.get("note") else ""
        print(f"  {row['label']:<42s} {row['count']:2d}/{row['total']} 編{extra}")
    print()

    print("--- 3. 前置きの型（どこから語り始めるか） ---")
    print("  " + ", ".join(f"{k}={v}編" for k, v in report["openers"].items()))
    print()

    print(f"--- 4. 編をまたいで使い回された {report['gram_size']} 文字列 ---")
    print(f"  総数 {report['repeated_gram_total']} 種 / それらを含む断片 {report['shared_fragment_count']}/{total} 編")
    for entry in report["top_grams"]:
        print(f"  '{entry['gram']}' ×{entry['count']}編  {', '.join(entry['owners'])}")
    rest = report["repeated_gram_total"] - len(report["top_grams"])
    if rest > 0:
        print(f"  …ほか {rest} 種")
    print()

    print("--- 5. 断片ごとの反復密度（保留句＋留保句＋二項対立句の数） ---")
    for item in report["density"][:8]:
        note = (
            f"  (括弧外={item['unquoted_hits']} / 引用内={item['hits'] - item['unquoted_hits']})"
            if item["hits"] != item["unquoted_hits"]
            else ""
        )
        print(f"  {item['fragment_id']}: {item['hits']}{note}")
    print()

    print("--- 6. 人称と名札の鏡（どの人称に寄りかかっているか） ---")
    for p in report["pronouns"]:
        note = (
            f" (括弧外={p['unquoted_count']}編)"
            if p["count"] != p["unquoted_count"]
            else ""
        )
        print(f"  {p['label']:<18s} {p['count']:2d}/{total} 編{note}")
    z_ids = ", ".join(report["zero_pronoun_fragment_ids"]) or "なし"
    print(f"  {'人称代名詞ゼロ（無主語）':<14s} {len(report['zero_pronoun_fragment_ids']):2d}/{total} 編  [{z_ids}]")
    empty_modes = [m for m, c in report["narrator_mode_counts"].items() if c == 0]
    print(f"  未使用の narrator_mode : {', '.join(empty_modes) if empty_modes else 'なし'}")
    for mm in report["mode_mismatches"]:
        print(f"  名札と地の文のずれ     : {mm['fragment_id']} (narrator_mode={mm['narrator_mode']} だが地の文に {mm['found']})")
    print()

    laugh = report["laughter"]
    print("--- 7. 笑いの鏡（書かれた笑いと、その隣にあった語） ---")
    if laugh["occurrences"] == 0:
        print(f"  笑いを含む断片 0/{total} 編 —— 31編のどこにも、誰も笑っていない。")
    else:
        print(
            f"  笑いを含む断片 {laugh['fragment_count']}/{total} 編"
            f"（延べ {laugh['occurrences']} 箇所: "
            + ", ".join(f"{k}={v}" for k, v in laugh["kinds"].items())
            + "）"
        )
        for hit in laugh["hits"]:
            print(f"    {hit['fragment_id']} [{hit['kind']}] …{hit['before']}【笑】{hit['after']}…")
    print("  ※ この欄は、誰かが実際に笑ったかどうかを判定できない。笑の字の隣に何が書かれていたかだけを映す。")
    print()

    print("--- 8. 反復の位置（同じ句は、同じ場所に置かれているか） ---")
    print("  反復の回数に対して、前後の文脈がどれだけ違うか。文脈が少ないほど暗唱、多いほど在庫からの作曲。")
    for row in report["repetition_contexts"]:
        ratio = (row["distinct_left"] + row["distinct_right"]) / max(1, row["occurrences"])
        print(
            f"  '{row['gram']}' ×{row['fragment_count']}編/{row['occurrences']}回"
            f"  左文脈{row['distinct_left']}種・右文脈{row['distinct_right']}種"
            f"（比 {ratio:.2f}）= {row['sample'][0]}【{row['gram']}】{row['sample'][2]}"
        )
    summary = report["context_summary"]
    if summary.get("count"):
        print(
            f"  → 使い回された {summary['count']} 種の中央値は {summary['median_ratio']}"
            f"（2.00 に近いほど、同じ句が毎回ちがう前後の語と組んでいる＝在庫、1.00 に近いほど暗唱）"
        )
    print("  ※ 比が小さいことは悪ではない。定型句がなければ歌えない（MAT-LIT-060）。")
    print()

    print("--- 読み方 ---")
    print("  この表は合否でも品質評価でもない（PROJECT_CHARTER.md「成功の見方」）。")
    print("  同じ句が何度も出ることは、声が続いている証拠にも、口が勝手に動いている証拠にもなる。")
    print("  どちらなのかは、次の断片が決める。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
