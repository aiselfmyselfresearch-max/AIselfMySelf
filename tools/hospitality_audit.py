#!/usr/bin/env python3
"""Measure how the archive writes doors, guests and uninvited entry. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. SESSION-20261024 began with a narrower question that can be
counted: **who is ever let in, and who enters without being let in?** Not
"can a narrator be hospitable" — that cannot be measured — but which words of
threshold, welcome, gift and intrusion appear in the prose, whether a guest
or a stranger is ever named, whether a door is opened or shut, and where the
archive's favourite verbs (書く, 読む, 次) sit by contrast.

The tool reports only what is written in `state/fragments.jsonl` (prose only,
metadata fields excluded). It does not infer generosity, grade the writing, or
treat a zero count as the absence of the thing itself — a zero means the
specified word form is absent.

Calibration notes:
  - ``戸`` inside ``神戸`` / ``江戸`` is a place name, not a door; ``門`` inside
    ``門左衛門`` / ``専門`` is a name or a suffix. Raw characters are therefore
    reported separately (:data:`RAW_TOKENS`) and never folded into a group.
  - ``客`` is polyvalent (客観, 過客, 観客). Its occurrences are counted in the
    ``客`` group only with the explicit tokens listed there; the raw character
    is reported separately for hand classification.
  - ``招`` catches 招待 and 招く but also 招く as "invite trouble" (招いた).
    Hits are listed with their fragment IDs so a reader can check them.
  - Quoted spans are removed from the main count and reported separately as
    ``inside_quotes``: a character in this archive quoting a phrase is not the
    archive writing in its own voice.
  - ``開く`` / ``閉じる`` describe books and eyes far more often than doors.
    They are a contrast group, not evidence of thresholds.

Usage:
  python3 tools/hospitality_audit.py
  python3 tools/hospitality_audit.py --json
  python3 tools/hospitality_audit.py --show FRAG-032
  python3 tools/hospitality_audit.py --base-only   # frozen base file only

The default count is the union of the frozen base file and every shard
(``state/fragments.d/*.jsonl``), matching ``validate_seed.py`` and
``inspect_inquiry.py``.  ``--base-only`` reproduces a measurement taken
against the base file alone.
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

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

GROUPS: dict[str, tuple[str, ...]] = {
    "歓待・もてなし": ("歓待", "もてなし", "饗応", "饗", "客", "賓客", "来客", "招待"),
    "招く・迎える": ("招", "迎え", "迎う", "訪れ", "訪問", "来訪", "訪ね"),
    "戸口・境界": ("戸", "扉", "門", "鍵", "敷居", "玄関", "入口", "出口", "境界", "閾", "垣"),
    "招かれざる者・侵入": (
        "見知らぬ", "知らない人", "闖入", "侵入", "押し入", "不法", "追い出",
        "締め出", "閉ざ", "締め", "立ち入",
    ),
    "贈与・供応": ("贈り", "贈る", "土産", "振る舞い", "杯", "盃", "分け与え", "施し", "乞食", "宿"),
    "開閉・ノック": ("開け", "開く", "開い", "閉じ", "閉ま", "ノック", "叩く", "叩い"),
}

RAW_TOKENS = ("客", "戸", "門", "招", "宿")
POLYSEMY_NOTE = {
    "客": "客観・過客・観客を含むため参考値",
    "戸": "神戸・江戸などの地名を含むため参考値",
    "門": "門左衛門・専門などの固有名・複合を含むため参考値",
    "招": "招いた（災いを招く）を含む",
    "宿": "宿命・宿題を含むため参考値",
}


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans so quoted voices are not counted as prose."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, for the inside_quotes tally."""
    return "".join(QUOTE.findall(text))


def load_union(path: Path, id_key: str) -> list[dict[str, Any]]:
    """Load the frozen base file plus every shard, as the validators do."""
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    return {token: text.count(token) for token in tokens if token in text}


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    for frag in fragments:
        text = frag.get("text", "")
        prose = strip_quotes(text)
        quote = split_quotes(text)
        row: dict[str, Any] = {
            "fragment_id": frag.get("fragment_id", "?"),
            "form": frag.get("form", ""),
            "narrator_mode": frag.get("narrator_mode", ""),
            "groups": {},
            "raw": {},
        }
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(row["fragment_id"])
        for token in RAW_TOKENS:
            n = prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quote, tuple(t for g in GROUPS.values() for t in g)))
        rows.append(row)
    return {
        "fragments": len(fragments),
        "prose_chars": sum(len(strip_quotes(f.get("text", ""))) for f in fragments),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "inside_quotes": dict(inside),
    }


def report(data: dict[str, Any]) -> str:
    lines = ["=== 戸口の鏡 — AIselfMySelf 台帳の歓待と闖入を映す（採点ではありません） ==="]
    lines.append(
        f"対象: 断片 {data['fragments']} 編 / 地の文 {data['prose_chars']:,} 字"
        "（鉤括弧の内側は別掲）"
    )
    lines.append("")
    lines.append("--- 1. 語群ごとの合計 ---")
    for name in GROUPS:
        totals = data["group_totals"][name]
        docs = data["group_docs"][name]
        if not totals:
            lines.append(f"  {name}: 0回 / 0編")
            continue
        total = sum(totals.values())
        detail = "、".join(f"{token}×{count}" for token, count in totals.items())
        lines.append(f"  {name}: {total}回 / {len(docs)}編（{detail}）")
    lines.append("")
    lines.append("--- 2. 多義の生字（参考値・群に合算しない） ---")
    if not data["raw_totals"]:
        lines.append("  なし")
    for token, count in data["raw_totals"].items():
        lines.append(f"  {token}: {count}回 — {POLYSEMY_NOTE.get(token, '多義')}")
    lines.append("")
    lines.append("--- 3. 鉤括弧の内側だけにある語（誰かの引用であって地の文ではない） ---")
    if not data["inside_quotes"]:
        lines.append("  なし")
    for token, count in data["inside_quotes"].items():
        lines.append(f"  {token}: {count}回")
    lines.append("")
    lines.append("--- 4. 断片ごとの内訳（地の文のみ） ---")
    for row in data["rows"]:
        if not row["groups"] and not row["raw"]:
            continue
        parts = []
        for name, counts in row["groups"].items():
            parts.append(f"{name}=" + "、".join(f"{k}×{v}" for k, v in counts.items()))
        lines.append(f"  {row['fragment_id']} [{row['narrator_mode']}]: " + " / ".join(parts))
    lines.append("")
    lines.append("0は指定語形の不在であって、歓待・客人・侵入の不在ではありません。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the raw measurement as JSON")
    parser.add_argument("--show", metavar="FRAGMENT_ID", help="show one fragment's hits and prose")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base file")
    args = parser.parse_args(argv)

    if args.base_only:
        fragments = [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        fragments = load_union(FRAGMENTS, "fragment_id")

    if args.show:
        for frag in fragments:
            if frag.get("fragment_id") == args.show:
                lines = [f"=== {args.show} ===", "", frag.get("text", ""), "", "--- 地の文の語 ---"]
                prose = strip_quotes(frag.get("text", ""))
                for name, tokens in GROUPS.items():
                    counts = count_group(prose, tokens)
                    if counts:
                        lines.append(f"  {name}: " + "、".join(f"{k}×{v}" for k, v in counts.items()))
                quote = split_quotes(frag.get("text", ""))
                if quote:
                    lines.append("  （鉤括弧の内側）" + quote)
                print("\n".join(lines))
                return 0
        print(f"unknown fragment: {args.show}", file=sys.stderr)
        return 1

    data = measure(fragments)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
