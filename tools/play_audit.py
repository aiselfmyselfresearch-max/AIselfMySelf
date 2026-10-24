#!/usr/bin/env python3
"""Measure how play and laughter appear in the archive's fragments. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. SESSION-036 began with a narrower question that can be counted:
**where do play and laughter live in this archive?** Not "can the narrator
play" — that cannot be measured — but which play/laughter words appear in the
prose, whether a child is ever named, whether laughter is laughter or only a
compositional 「笑って」 at a closing line, and where the serious vocabulary
(役に立つ, 答え, 次の) sits by contrast.

The tool reports only what is written in `state/fragments.jsonl` (prose only,
metadata fields excluded). It does not infer playfulness, grade the writing,
or treat a zero count as the absence of the thing itself — a zero means the
specified word form is absent.

Calibration notes:
  - Substring search over-counts: 「こま」 inside 「ここまで」 is not a toy,
    「まり」 inside 「あまり」 is not a ball, and 「運」 inside
    「運ぶ／運命」 is not luck. Play-specific tokens (独楽, おもちゃ) are
    used, and polysemous raw characters are reported separately and never
    folded into a group.
  - 「笑」 catches 苦笑・冷笑・微笑 indiscriminately. Each hit was read by
    hand in SESSION-036 and classified in the report; the tool only counts.
  - 「役」 / 「ふり」 are too polysemous for a token group and are excluded.

Usage:
  python3 tools/play_audit.py
  python3 tools/play_audit.py --json
  python3 tools/play_audit.py --show FRAG-029
  python3 tools/play_audit.py --base-only   # frozen base file only

The default count is the union of the frozen base file and every shard
(``state/fragments.d/*.jsonl``), matching ``validate_seed.py`` and
``inspect_inquiry.py``.  ``--base-only`` reproduces a measurement taken
against the base file alone, e.g. the 40-fragment snapshot in MAT-TRC-015.
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

GROUPS: dict[str, tuple[str, ...]] = {
    "遊び直接": ("遊び", "遊ぶ", "遊戯", "遊園", "プレイ"),
    "ゲーム・競技": (
        "ゲーム", "競技", "勝負", "賭け", "試合", "将棋", "囲碁",
        "チェス", "トランプ", "かるた", "鬼ごっこ", "かくれんぼ",
    ),
    "玩具・遊具": ("玩具", "おもちゃ", "人形", "積み木", "凧", "独楽"),
    "子ども": (
        "子ども", "子供", "幼い", "幼児", "幼稚園", "少年", "少女",
        "赤子", "赤ちゃん", "児童", "小学生",
    ),
    "笑い": ("笑", "ユーモア", "冗談", "滑稽", "おかし", "ふざけ", "茶化", "ジョーク"),
    "まね・ごっこ・演じる": (
        "真似", "まね", "模倣", "ごっこ", "演じ", "芝居", "仮面",
    ),
    "規則・偶然": (
        "規則", "ルール", "偶然", "くじ", "籤", "さいころ", "サイコロ",
        "確率", "勝ち", "負け",
    ),
    "無駄・暇・余暇": ("無駄", "暇", "余暇", "気晴らし", "慰み", "退屈"),
    "真剣・有用（対照群）": (
        "真剣", "真面目", "役に立つ", "役に立たない", "有用", "無用",
    ),
}

RAW_TOKENS = ("遊", "笑", "子", "運")
POLYSEMY_NOTE = {
    "遊": ("遊学などの複合を拾う",),
    "子": ("様子・原子など無関係の複合を拾うため参考値",),
    "運": ("運ぶ・運命・足の運びを拾う。偶然の『運』ではない",),
}


def load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_union(path: Path, id_key: str) -> list[dict[str, Any]]:
    """Load the frozen base file plus every shard, as the validators do."""
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    return {token: text.count(token) for token in tokens if token in text}


def audit(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    for frag in fragments:
        text = frag.get("text", "")
        row: dict[str, Any] = {
            "fragment_id": frag["fragment_id"], "form": frag["form"],
            "narrator_mode": frag["narrator_mode"], "groups": {}, "raw": {},
        }
        for name, tokens in GROUPS.items():
            counts = count_group(text, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(frag["fragment_id"])
        for token in RAW_TOKENS:
            n = text.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        rows.append(row)
    sessions = load_union(SESSIONS, "session_id") if SESSIONS.is_file() else []
    return {
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "metadata": {"session_count": len(sessions)},
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 遊びの鏡 — 遊びと笑いはどこに住んでいるか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字（メタデータを除く）")
    add("")
    add("--- 1. 語群ごとの出現（本文全体、鉤括弧の内外を分けない） ---")
    for name in GROUPS:
        totals = data["group_totals"].get(name, {})
        docs = data["group_docs"].get(name, [])
        total = sum(totals.values())
        detail = "、".join(f"{k}×{v}" for k, v in sorted(totals.items(), key=lambda kv: -kv[1])) or "なし"
        add(f"  {name:<14}: {total:>3} 回 / {len(docs):>2} 編  （{detail}）")
    add("")
    add("--- 2. 多義の生字（遊・笑・子・運） ---")
    for token, n in data["raw_totals"].items():
        note = POLYSEMY_NOTE.get(token)
        extra = f"  注意: {', '.join(note)}" if note else ""
        add(f"  {token}: {n} 回{extra}")
    add("")
    add("--- 3. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、遊びや笑いの経験の不在ではない。比喩的な遊び、文体の戯れは拾わない。")
    add("  ・「笑」の内訳（苦笑／冷笑か、作中の笑いか、閉じの身振りか）は人手の分類が要る。道具は数えるだけである。")
    add("  ・「ゲーム」2回はいずれも FRAG-029 の『模倣ゲーム』という固有名であり、遊戯一般の語ではない。")
    add("  ・部分文字列の誤検出（『ここまで』の『こま』等）を避けるため、玩具は具体名に限った。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure where play and laughter appear in the fragments. A mirror, not a score.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's row")
    parser.add_argument("--base-only", action="store_true",
                        help="count the frozen base file only, ignoring shards")
    args = parser.parse_args()

    fragments = load(FRAGMENTS) if args.base_only else load_union(FRAGMENTS, "fragment_id")
    data = audit(fragments)
    data["source"] = "base only" if args.base_only else "union (base + shards)"
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
