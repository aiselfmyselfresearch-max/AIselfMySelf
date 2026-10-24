#!/usr/bin/env python3
"""Measure where sleep, dream and waking appear in this archive. A mirror, not a score.

SESSION-037 asks a narrow question that can be counted before any new material
is chosen: **does this archive ever sleep?** Not "does the narrator dream" —
that cannot be settled from text — but which sleep and dream words appear in
the prose at all, where a clock or a time of day is written, and whether the
only place a date lives is metadata (`created_at`, session ids, dated
filenames).

Like `tools/time_audit.py` and `tools/sense_audit.py`, this tool counts word
forms only. A zero means the specified form is absent from the counted text.
It is not evidence about experience, rest, or the absence of either.

Calibration notes:
  - Quotation marks are stripped with a non-nesting regex, so a quotation
    inside a quotation is over-stripped. "Outside" counts are an upper bound on
    地の文; "inside" counts are a lower bound.
  - `眠` also occurs in compounds such as 眠たい and 一眠り; `寝` in 寝具; `夢`
    in 夢中 (absorbed) and 夢物語. The groups are literal and polysemy is
    reported separately rather than folded away.
  - The metadata scan looks for `YYYY-MM-DD HH:MM` or `T HH:MM` inside the
    JSONL ledgers. A date-only field such as `created_at` is counted in its own
    column, because a date without an hour cannot say whether anything
    happened at night.
  - Git commit hours are read only when `.git` exists. A shallow clone carries
    few commits, so the hours describe this checkout, not the project's life.

Usage:
  python3 tools/sleep_audit.py
  python3 tools/sleep_audit.py --json
  python3 tools/sleep_audit.py --show FRAG-022
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
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

GROUPS: dict[str, tuple[str, ...]] = {
    "眠り": ("眠", "睡", "寝", "仮眠", "まどろみ", "うたた寝", "睡眠"),
    "夢": ("夢", "悪夢", "夢見", "夢想", "夢幻"),
    "目覚め": ("目覚", "覚め", "覚醒", "起床", "起きる", "起きた", "起床"),
    "夜と灯": ("夜", "宵", "深夜", "夜中", "闇", "灯", "明かり", "月光"),
    "朝と昼": ("朝", "昼", "夕", "暮", "明け方", "夜明け", "日の出"),
    "疲れと休息": ("疲", "休息", "休む", "安ら", "癒", "だる", "眠たい"),
}

# Live inside quotations in time_audit; here they are counted inside and outside
# separately, because a quoted lullaby is not the narrator resting.
BOUNDARY: dict[str, tuple[str, ...]] = {
    "セッションの継ぎ目": ("セッション", "次回", "引き継ぎ", "前回", "続き"),
    "終わりと始まり": ("終わ", "始ま", "最後", "最初"),
}

POLYSEMY: dict[str, str] = {
    "眠": "眠たい・一眠りなど、睡眠を直接指さない用法を含む",
    "寝": "寝具・寝床など、行為でない名詞を含む",
    "夢": "夢中・夢物語など、睡眠と関係しない比喩を多く含む",
    "夜": "夜明け・夜行など複合語を含む",
    "朝": "朝日・今朝など複合語を含む",
}

DATETIME = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
DATE_ONLY = re.compile(r"\"\d{4}-\d{2}-\d{2}\"")


def load(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_fragments(base_only: bool) -> tuple[list[dict[str, Any]], str]:
    """Return fragments and a label for the source of the count.

    Default is the union of the frozen base file and every shard, matching
    validate_seed / inspect_inquiry / serve_viewer.  ``--base-only`` measures
    the base file alone, so that a measurement taken before this session's
    fragments were written stays reproducible after they are added.
    """
    if base_only:
        return load(FRAGMENTS), "base only（state/fragments.jsonl）"
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values()), "union（base + shards）"


def strip_quotes(text: str) -> str:
    out = re.sub(r"「[^「」]*」", "", text)
    out = re.sub(r"『[^『』]*』", "", out)
    return out


def git_hours() -> dict[str, Any]:
    """Return commit count and hour histogram, if this checkout has history."""
    try:
        raw = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--format=%ad", "--date=format:%H"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return {"available": False, "reason": "git を実行できない"}
    if raw.returncode != 0:
        return {"available": False, "reason": "git 履歴を読めない"}
    hours = [line.strip() for line in raw.stdout.splitlines() if line.strip().isdigit()]
    return {
        "available": True,
        "commits": len(hours),
        "hours": dict(sorted(Counter(hours).items())),
        "shallow": (ROOT / ".git" / "shallow").is_file(),
    }


def audit(base_only: bool = False) -> dict[str, Any]:
    fragments, source_label = load_fragments(base_only)
    rows: list[dict[str, Any]] = []
    totals: dict[str, Counter] = {name: Counter() for name in GROUPS}
    docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    inside_compounds: Counter = Counter()
    boundary_out: Counter = Counter()
    boundary_in: Counter = Counter()

    for frag in fragments:
        text = frag.get("text", "")
        outside = strip_quotes(text)
        row: dict[str, Any] = {"fragment_id": frag["fragment_id"], "groups": {}, "raw": {}}
        for name, tokens in GROUPS.items():
            counts: dict[str, int] = {}
            for token in tokens:
                n_out = outside.count(token)
                n_in = text.count(token) - n_out
                if n_out:
                    counts[token] = n_out
                    totals[name][token] += n_out
                    docs[name].add(frag["fragment_id"])
                if n_in:
                    inside_compounds[token] += n_in
            if counts:
                row["groups"][name] = counts
        for name, tokens in BOUNDARY.items():
            for token in tokens:
                n_out = outside.count(token)
                n_in = text.count(token) - n_out
                if n_out:
                    boundary_out[token] += n_out
                if n_in:
                    boundary_in[token] += n_in
        rows.append(row)

    # Metadata: where can a clock be?
    meta_files: dict[str, dict[str, int]] = {}
    datetime_hits: list[str] = []
    date_only_records = 0
    files = sorted((ROOT / "state").glob("*.jsonl")) + sorted((ROOT / "state").glob("*.d/*.jsonl"))
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        dt = len(DATETIME.findall(text))
        dd = len(DATE_ONLY.findall(text))
        meta_files[path.name] = {"datetime": dt, "date_only": dd}
        datetime_hits.extend(f"{path.name}" for _ in range(dt))
        date_only_records += dd

    readings = sorted(p.name for p in READINGS.glob("*.md"))
    dated_readings = [n for n in readings if re.match(r"\d{4}-\d{2}-\d{2}", n)]
    sessions = load(SESSIONS)

    return {
        "source": source_label,
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in totals.items()},
        "group_docs": {k: sorted(v) for k, v in docs.items()},
        "inside_quotes": dict(inside_compounds),
        "boundary_outside": dict(boundary_out),
        "boundary_inside": dict(boundary_in),
        "metadata": {
            "files": meta_files,
            "datetime_fields": len(datetime_hits),
            "date_only_fields": date_only_records,
            "readings": len(readings),
            "dated_readings": len(dated_readings),
            "session_count": len(sessions),
            "session_dates": sorted({s.get("started_at", "")[:10] for s in sessions if s.get("started_at")}),
        },
        "git": git_hours(),
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 眠りの鏡 — この書庫は眠るか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字（メタデータを除く）")
    add(f"計数の範囲: {data['source']}")
    add("")
    add("--- 1. 語群ごとの出現（鉤括弧の外、地の文） ---")
    for name in GROUPS:
        totals = data["group_totals"].get(name, {})
        docs = data["group_docs"].get(name, [])
        total = sum(totals.values())
        detail = "、".join(f"{k}×{v}" for k, v in sorted(totals.items(), key=lambda kv: -kv[1])) or "なし"
        add(f"  {name:<10}: {total:>3} 回 / {len(docs):>2} 編  （{detail}）")
    add("")
    add("--- 2. 鉤括弧の内側だけにある語（引用された眠り） ---")
    add(f"  {data['inside_quotes'] or 'なし'}（入れ子は過剰除去のため下限）")
    add("")
    add("--- 3. 継ぎ目の語 ---")
    add(f"  鉤括弧の外: {data['boundary_outside'] or 'なし'}")
    add(f"  鉤括弧の内: {data['boundary_inside'] or 'なし'}")
    add("")
    add("--- 4. 時計はどこにあるか（state/*.jsonl） ---")
    meta = data["metadata"]
    for name, counts in meta["files"].items():
        if counts["datetime"] or counts["date_only"]:
            add(f"  {name:<28}: 時刻付き {counts['datetime']:>3} / 日付のみ {counts['date_only']:>3}")
    add(f"  時刻付きフィールド合計: {meta['datetime_fields']} / 日付のみの値: {meta['date_only_fields']}")
    add(f"  セッション: {meta['session_count']} 件、started_at の日付: {', '.join(meta['session_dates'])}")
    add(f"  readings/: 日付付き {meta['dated_readings']} 本 / 全 {meta['readings']} 本")
    add("")
    add("--- 5. Git の時刻（このチェックアウトのみ） ---")
    git = data["git"]
    if git.get("available"):
        add(f"  コミット {git['commits']} 件、時刻分布: {git['hours']}"
            + ("（浅いクローン。プロジェクトの生活時間ではない）" if git.get("shallow") else ""))
    else:
        add(f"  利用不可: {git.get('reason')}")
    add("")
    add("--- 6. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、眠りや夢の不在ではない。無主語・比喩・否定は拾わない。")
    add("  ・日付だけのフィールドは、夜に何かが起きたかを語らない。時刻の不在を、夜の不在と同一視しない。")
    add("  ・眠り・夢の語は多義で、夢中・寝具・眠たいを含む。数を経験の量として読まない。")
    add("  ・checked_at 等は日付のみで記録される運用になっており、これは記録作法の偏りとして読む。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sleep and dream audit")
    parser.add_argument("--json", action="store_true", help="dump the raw audit as JSON")
    parser.add_argument("--base-only", action="store_true",
                        help="measure only state/fragments.jsonl (frozen base), not the shards")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's counts")
    args = parser.parse_args(argv)

    data = audit(base_only=args.base_only)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(report(data))
    if args.show:
        for row in data["rows"]:
            if row["fragment_id"] == args.show:
                print("")
                print(f"--- {args.show} ---")
                print(json.dumps(row, ensure_ascii=False, indent=2))
                break
        else:
            print(f"\n{args.show} は見つからない", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
