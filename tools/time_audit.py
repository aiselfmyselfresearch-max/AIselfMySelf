#!/usr/bin/env python3
"""Measure how time appears in the archive's fragments. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. SESSION-035 began with a narrower question that can be counted:
**where does time live in this archive?** Not "does the narrator experience
duration" — that cannot be measured — but which time words appear in the
prose, whether a calendar or a clock is ever named, whether the future is
written as a lived "tomorrow" or only as a structural "next" (next session,
next page, next reader), how often the prose waits, and where the dates that
order the archive actually sit (in the stories, or only in metadata such as
`created_at`, session ids and dated filenames).

The tool reports only what is written in `state/fragments.jsonl` (prose only,
metadata fields excluded) plus a small metadata comparison against
`state/sessions.jsonl` and the dated filenames in `readings/`. It does not
infer temporal experience, grade the writing, or treat a zero count as the
absence of the thing itself — a zero means the specified word form is absent.

Calibration notes:
  - Japanese `時` / `間` / `とき` are heavily polysemous (人間, 世間, 床の間,
    時間, 時計). They are reported separately and never folded into a group.
  - Quotation marks are stripped with a non-nesting regex, so a quotation
    inside a quotation is over-stripped. "Outside" counts are therefore an
    upper bound on 地の文 and "inside" counts a lower bound.
  - The terminal-past-tense heuristic (た/だ immediately before 。」 or a
    line end) catches adjectives (赤かった), conditionals and light verbs
    too. It is a rough surface signal, not a grammatical parse.
  - `暦` inside an era name such as 建暦二年 is counted by the raw scan but
    flagged manually in the report; the token group's calendar sense is what
    the interpretation rests on.

Usage:
  python3 tools/time_audit.py
  python3 tools/time_audit.py --json
  python3 tools/time_audit.py --show FRAG-018
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
SESSIONS = ROOT / "state" / "sessions.jsonl"
READINGS = ROOT / "readings"

ID_KEYS = {
    "fragments.jsonl": "fragment_id",
    "sessions.jsonl": "session_id",
}

# Explicit token groups. Kept literal and auditable; polysemous characters
# (時, 間, とき) are intentionally not members of any group.
GROUPS: dict[str, tuple[str, ...]] = {
    "暦と時計": (
        "時計", "暦", "カレンダー", "日付", "タイムスタンプ",
        "スケジュール", "期限", "締切", "締め切り",
    ),
    "直示の現在": ("今日", "本日", "今晩", "今朝", "現在", "さっき", "今"),
    "直示の過去": (
        "昨日", "一昨日", "昔", "過去", "昨年", "去年", "先日",
        "かつて", "以前", "あの日", "あの頃",
    ),
    "直示の未来": (
        "明日", "あした", "明後日", "未来", "将来", "いつか", "やがて",
        "そのうち", "今後", "今度", "近いうち", "後で", "のち",
        "予定", "つもり", "約束",
    ),
    "継承の未来（次）": ("次に", "次回", "次の"),
    "待機": (
        "待つ", "待って", "待た", "待ち", "待て", "待とう", "待機", "待つる",
    ),
    "長い時間": (
        "百年", "千年", "万年", "永遠", "永久", "無限", "生涯", "一生", "世代",
    ),
    "瞬間": ("瞬間", "一瞬", "刹那", "突然", "たちまち"),
    "季節と昼夜": (
        "春", "夏", "秋", "冬", "朝", "昼", "夕", "夜", "明け方", "黄昏", "夜明け",
    ),
    "測定された時間": (
        "一分", "一秒", "一時間", "半日", "一日", "一週間", "一か月",
        "一ヶ月", "一年",
    ),
}

# Polysemous raw characters, reported with their common non-temporal compounds.
RAW_TOKENS = ("時", "間", "とき", "時間")
POLYSEMY_NOTE = {
    "間": ("人間", "世間", "床の間", "人間関係"),
    "時": ("時計", "当時", "一時"),
}

DATE_PATTERN = re.compile(r"\d{4}\s*年|\d{1,2}\s*月\s*\d{1,2}\s*日|\d{4}-\d{2}-\d{2}")
TERMINAL_PAST = re.compile(r"[ただ][。、」\n]")
ERA_PATTERN = re.compile(r"[一-龥]{1,4}[元年]\d*年?")


def load(path: Path, *, base_only: bool = False, exclude: str | None = None) -> list[dict[str, Any]]:
    if base_only or path.name not in ID_KEYS:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, ID_KEYS[path.name], errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans, non-nested. Over-strips nested quotes."""
    out = re.sub(r"「[^「」]*」", "", text)
    out = re.sub(r"『[^『』]*』", "", out)
    return out


def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    return {token: text.count(token) for token in tokens if token in text}


def audit(fragments: list[dict[str, Any]], *, base_only: bool = False, exclude: str | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside_wait = Counter()
    outside_wait = Counter()
    dated_prose: list[str] = []
    past_hits = 0
    past_docs: set[str] = set()
    for frag in fragments:
        text = frag.get("text", "")
        outside = strip_quotes(text)
        row: dict[str, Any] = {"fragment_id": frag["fragment_id"], "form": frag["form"],
                               "narrator_mode": frag["narrator_mode"], "groups": {},
                               "raw": {}, "date_strings": DATE_PATTERN.findall(text)}
        for name, tokens in GROUPS.items():
            counts = count_group(outside, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(frag["fragment_id"])
        for token in RAW_TOKENS:
            n = text.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        for token in GROUPS["待機"]:
            inside = text.count(token)
            out = outside.count(token)
            if inside - out:
                inside_wait[token] += inside - out
            if out:
                outside_wait[token] += out
        if DATE_PATTERN.search(text):
            dated_prose.append(frag["fragment_id"])
        n_past = len(TERMINAL_PAST.findall(text))
        if n_past:
            past_hits += n_past
            past_docs.add(frag["fragment_id"])
        rows.append(row)

    created_at = Counter(frag.get("created_at", "?") for frag in fragments)
    sessions = load(SESSIONS, base_only=base_only, exclude=exclude) if SESSIONS.is_file() else []
    session_dates = sorted({s.get("started_at", "")[:10] for s in sessions if s.get("started_at")})
    reading_files = sorted(p.name for p in READINGS.glob("*.md"))
    dated_readings = [name for name in reading_files if re.match(r"\d{4}-\d{2}-\d{2}", name)]
    return {
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "waiting_outside": dict(outside_wait),
        "waiting_inside": dict(inside_wait),
        "dated_prose_fragments": dated_prose,
        "terminal_past_hits": past_hits,
        "terminal_past_docs": sorted(past_docs),
        "metadata": {
            "created_at_values": dict(created_at),
            "session_count": len(sessions),
            "session_started_at_dates": session_dates,
            "dated_reading_files": len(dated_readings),
            "reading_files": reading_files,
        },
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 時間の鏡 — 時間はどこに住んでいるか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字（メタデータを除く）")
    add("")
    add("--- 1. 語群ごとの出現（鉤括弧の外、地の文） ---")
    for name in GROUPS:
        totals = data["group_totals"].get(name, {})
        docs = data["group_docs"].get(name, [])
        total = sum(totals.values())
        detail = "、".join(f"{k}×{v}" for k, v in sorted(totals.items(), key=lambda kv: -kv[1])) or "なし"
        add(f"  {name:<16}: {total:>3} 回 / {len(docs):>2} 編  （{detail}）")
    add("")
    add("--- 2. 待機の語の位置 ---")
    add(f"  鉤括弧の外: {dict(data['waiting_outside']) or 'なし'}")
    add(f"  鉤括弧の内: {dict(data['waiting_inside']) or 'なし'}（入れ子は過剰除去のため下限）")
    add("")
    add("--- 3. 多義の生字（時・間・とき） ---")
    for token, n in data["raw_totals"].items():
        note = POLYSEMY_NOTE.get(token)
        extra = f"  非時間的複合の例: {', '.join(note)}" if note else ""
        add(f"  {token}: {n} 回{extra}")
    add("")
    add("--- 4. 日付と時制 ---")
    add(f"  本文中の日付文字列（\\d{{4}}年 等）: {data['dated_prose_fragments'] or 'なし'}")
    add(f"  終止形のた/だ（粗い走査、形容詞・条件を含む）: {data['terminal_past_hits']} 回 / {len(data['terminal_past_docs'])} 編")
    add("")
    add("--- 5. メタデータに住む時間 ---")
    meta = data["metadata"]
    add(f"  断片の created_at 値: {meta['created_at_values']}")
    add(f"  セッション数: {meta['session_count']} / started_at の日付: {', '.join(meta['session_started_at_dates'])}")
    add(f"  readings/ の日付付きファイル: {meta['dated_reading_files']} / 全 {len(meta['reading_files'])} 本")
    add("")
    add("--- 6. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、時間経験の不在ではない。無主語の文や比喩的な時間は拾わない。")
    add("  ・「次の」は、生きられる明日ではなく、引き継ぎの構造を示す語として別集計にした。")
    add("  ・百年・千年と瞬間・今のあいだ（時計で測れる中間の時間）が薄いかどうかを、この表は示す。")
    add("  ・鉤括弧の除去は入れ子を扱わない。内外の振り分けは方向を示す目安である。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure where time appears in the fragments. A mirror, not a score.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's row")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/*.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    kw = {"base_only": args.base_only, "exclude": args.exclude_shard}
    data = audit(load(FRAGMENTS, **kw), **kw)
    if args.show:
        for row in data["rows"]:
            if row["fragment_id"] == args.show:
                print(json.dumps(row, ensure_ascii=False, indent=2))
                return 0
        print(f"{args.show}: not found", flush=True)
        return 1
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
