#!/usr/bin/env python3
"""Mirror the archive's vocabulary of possibility, prediction, and refusal.

This is an editorial instrument, not a measure of uncertainty, free will, or
conscious experience. It counts visible Japanese forms in fragment text only so
that later sessions can reproduce the snapshot used by MAT-TRC-009.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"

# Keep categories intentionally lexical. A hit says that a form is present, not
# that the narrator has the corresponding capacity or feeling.
SPECS: tuple[tuple[str, str], ...] = (
    ("未来・先", r"未来|明日|これから|いつか|やがて|次の|次へ|後で|その後"),
    ("予測・予告", r"予測|予言|予告|予想|見通し|先を読む|見越"),
    ("可能・条件", r"可能|かもしれない|かも知れない|だろうか|のではないか|もし|ならば|なら"),
    ("不知・保留", r"分からない|わからない|知れない|答えはない|答へはない|未定|保留"),
    ("確率・不確実", r"確率|不確実|不確か|曖昧|偶然|必然|運命"),
    ("選択・決定", r"選ぶ|選ん|選択|決める|決め|決定|断つ|棄て|捨て"),
    ("問いの終止", r"(?:だろうか|のだろうか|のか|か)[。！？?]?$"),
)


def load(*, base_only: bool = False, exclude: str | None = None) -> list[dict[str, object]]:
    if base_only:
        return [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def audit(fragments: list[dict[str, object]]) -> dict[str, object]:
    counts: Counter[str] = Counter()
    fragment_counts: Counter[str] = Counter()
    by_fragment: list[dict[str, object]] = []
    for frag in fragments:
        text = str(frag["text"])
        row: dict[str, object] = {"fragment_id": frag["fragment_id"], "title": frag["title"]}
        total = 0
        categories: list[str] = []
        for label, pattern in SPECS:
            hits = len(re.findall(pattern, text))
            row[label] = hits
            counts[label] += hits
            if hits:
                fragment_counts[label] += 1
                categories.append(label)
                total += hits
        row["total_hits"] = total
        row["categories"] = categories
        by_fragment.append(row)
    return {
        "fragment_count": len(fragments),
        "categories": [
            {"label": label, "occurrences": counts[label], "fragments": fragment_counts[label]}
            for label, _ in SPECS
        ],
        "by_fragment": by_fragment,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON (default)")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()
    result = audit(load(base_only=args.base_only, exclude=args.exclude_shard))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
