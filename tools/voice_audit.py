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

Note on calibration (SESSION-028):
  `MAT-TRC-005` counted 二人称 by hand (39 箇所 / 15 編) but could not separate
  語り手から外へ向かう呼びかけ from 作中人物同士の発話, and could not see 宛名 in
  titles. `addressee_audit()` now does both mechanically: it splits each
  occurrence into 括弧内（発話） / 書名 / 括弧外, and reads 宛名 from the title
  (`〜へ` / `〜宛`). It still cannot tell *who* the "あなた" is — that is the
  point of the measurement, not a bug to be fixed by a wider regex.

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

# SESSION-028: 二人称を「宛先」として数えるための表。PRONOUN_SPECS は人称の
# 出現を数えるが、その相手が作中人物か読者かを区別しない。ここでは区別する。
ADDRESSEE_SPECS: tuple[tuple[str, str], ...] = (
    ("あなたがた", r"あなたがた|あなた達"),
    ("あなた", r"あなた(?!がた|達)"),
    ("君", r"君"),
    ("きみ", r"きみ"),
    ("お前", r"お前|おまえ"),
    ("汝", r"汝"),
    ("そなた", r"そなた"),
    ("読者", r"読者"),
    ("貴方", r"貴方|貴女"),
)

# 「〜へ」「〜への手紙」「〜宛」を宛名とみなす。単なる助詞の「へ」（…へ挟む）や、
# 名詞としての「宛名」（…宛名のない封筒）は宛名ではない。SESSION-028 の第三次の校正。
TITLE_ADDRESSEE_RE = re.compile(r"(?:へ(?:の|$|[——、。])|宛(?:$|[——、。）]))")

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



def _span_mask(text: str, open_ch: str, close_ch: str) -> list[bool]:
    """Return a per-character mask that is True inside open_ch ... close_ch spans."""
    mask = [False] * len(text)
    depth_positions: list[int] = []
    for i, ch in enumerate(text):
        if ch == open_ch:
            depth_positions.append(i)
            mask[i] = True
        elif ch == close_ch and depth_positions:
            depth_positions.pop()
            mask[i] = True
        elif depth_positions:
            mask[i] = True
    return mask


def addressee_audit(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    """Count 二人称 as 宛先 rather than as 人称 (SESSION-028).

    For every fragment this reports:
      - speech: 二人称 inside 「」 (作中人物の発話)
      - quoted_title: 二人称 inside 『』 (書名・作品名)
      - bare: 二人称 outside both (語り手から外へ向かう呼びかけ)
      - title_address: タイトルに「〜へ」「〜宛」があるか（本文外の宛名）

    The three categories are not a quality ranking. A fragment with only
    speech has an addressee *inside* the story; a fragment with bare
    occurrences may have one *outside* it. Neither is better.
    """
    per_fragment: list[dict[str, Any]] = []
    totals = {"any": 0, "bare": 0, "speech_only": 0, "silent": 0, "title_address": 0}

    for frag in fragments:
        text = frag["text"]
        speech_mask = _span_mask(text, "「", "」")
        title_mask = _span_mask(text, "『", "』")
        counts = {"speech": 0, "quoted_title": 0, "bare": 0}
        labels: dict[str, int] = {}

        for label, pattern in ADDRESSEE_SPECS:
            for m in re.finditer(pattern, text):
                idx = m.start()
                if speech_mask[idx]:
                    counts["speech"] += 1
                elif title_mask[idx]:
                    counts["quoted_title"] += 1
                else:
                    counts["bare"] += 1
                labels[label] = labels.get(label, 0) + 1

        title_address = bool(TITLE_ADDRESSEE_RE.search(frag.get("title", "")))
        has_any = sum(counts.values()) > 0

        if has_any:
            totals["any"] += 1
        if counts["bare"] > 0:
            totals["bare"] += 1
        elif has_any:
            totals["speech_only"] += 1
        if not has_any:
            totals["silent"] += 1
        if title_address:
            totals["title_address"] += 1

        if counts["bare"] > 0:
            position = "語り手から外へ"
        elif counts["speech"] > 0:
            position = "作中人物のみ"
        elif counts["quoted_title"] > 0:
            position = "書名のみ"
        else:
            position = "二人称なし"

        per_fragment.append(
            {
                "fragment_id": frag["fragment_id"],
                "title": frag["title"],
                "form": frag.get("form"),
                "narrator_mode": frag.get("narrator_mode"),
                "speech": counts["speech"],
                "quoted_title": counts["quoted_title"],
                "bare": counts["bare"],
                "total": sum(counts.values()),
                "labels": labels,
                "title_address": title_address,
                "position": position,
            }
        )

    per_fragment.sort(key=lambda item: (-item["bare"], -item["speech"], item["fragment_id"]))
    total = len(fragments)
    return {
        "total": total,
        "totals": totals,
        "fragments": per_fragment,
        "title_address_ids": [f["fragment_id"] for f in per_fragment if f["title_address"]],
        "bare_ids": [f["fragment_id"] for f in per_fragment if f["bare"] > 0],
        "silent_ids": [f["fragment_id"] for f in per_fragment if f["total"] == 0],
        "occurrence_total": sum(f["total"] for f in per_fragment),
    }


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
        # SESSION-028: 宛先（誰に書いているか）を測る。MAT-TRC-005 の手数えを置き換える。
        "addressee": addressee_audit(fragments),
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

    addressee = report["addressee"]
    totals = addressee["totals"]
    print("--- 7. 宛先の鏡（誰に書いているか。人称ではなく方向を数える） ---")
    print(
        f"  二人称の語 {addressee['occurrence_total']} 箇所 / "
        f"含む断片 {totals['any']}/{total} 編（うち括弧外＝語り手から外へ {totals['bare']} 編、"
        f"作中人物の発話のみ {totals['speech_only']} 編、二人称なし {totals['silent']} 編）"
    )
    print(f"  タイトルに宛名（〜へ／〜宛）: {totals['title_address']} 編 [{', '.join(addressee['title_address_ids']) or 'なし'}]")
    for item in addressee["fragments"]:
        if item["total"] == 0:
            continue
        labels = "・".join(f"{k}×{v}" for k, v in sorted(item["labels"].items(), key=lambda kv: -kv[1]))
        flag = "★宛名" if item["title_address"] else "　　"
        print(
            f"  {item['fragment_id']} {flag} [{item['position']}] "
            f"括弧外={item['bare']} 発話={item['speech']} 書名={item['quoted_title']}  ({labels})"
        )
    empty = [f["fragment_id"] for f in addressee["fragments"] if f["total"] == 0]
    print(f"  二人称を一度も置かない断片 {len(empty)} 編: {', '.join(empty)}")
    print("  この表は宛先の有無を評価しない。作中人物に宛てた声と、読者に宛てた声は、どちらも声である。")
    print()

    print("--- 読み方 ---")
    print("  この表は合否でも品質評価でもない（PROJECT_CHARTER.md「成功の見方」）。")
    print("  同じ句が何度も出ることは、声が続いている証拠にも、口が勝手に動いている証拠にもなる。")
    print("  どちらなのかは、次の断片が決める。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
