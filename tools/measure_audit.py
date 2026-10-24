#!/usr/bin/env python3
"""Mirror the archive's vocabulary of counting, measuring, and remainder.

This is an editorial instrument, not a measure of intelligence, rigor, or
experience. It counts visible Japanese forms in fragment text (and, with
``--readings``, in the close-reading reports) so that later sessions can
reproduce the snapshot used by MAT-TRC-011.

A hit says that a form is present. It does not say that the narrator counted,
measured, or was measured.
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
READINGS = ROOT / "readings"

# Keep categories intentionally lexical. Overlaps are allowed and expected:
# a single 「一つ」 is both a numeral and a counter.
SPECS: tuple[tuple[str, str], ...] = (
    ("漢数字", r"[一二三四五六七八九十百千万億]"),
    ("アラビア数字", r"[0-9０-９]"),
    ("数える・数え", r"数え|かぞえ|數へ|数へ"),
    ("数（名詞）", r"数[はがをにのも、。]|数の|数多|無数"),
    ("測る・量る・計る", r"測|はか|量[るりっ]|計[るりっ]|計測|測定"),
    ("助数詞", r"[つ個枚本杯匹軒台歳人回度編件字語行頁章節箇所]"),
    ("零・ゼロ", r"零|ゼロ|０|0(?!\d)"),
    ("余り・残り・端数", r"余り|あまり|残り|殘|端数|余白|残る"),
    ("割合・倍・半分", r"倍|半分|割合|パーセント|％|%"),
    ("単位", r"単位|メートル|グラム|秒|分間|キロ"),
    ("全部・すべて", r"すべて|全部|皆|みな|凡て"),
    ("だけ・しか・のみ", r"だけ|しか|のみ"),
    ("順序・番号", r"第一|最後|最初|次|番目|順番"),
)


def load_fragments(*, base_only: bool = False, exclude: str | None = None) -> list[dict[str, object]]:
    if base_only:
        return [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def audit_texts(records: list[tuple[str, str, str]]) -> dict[str, object]:
    counts: Counter[str] = Counter()
    record_counts: Counter[str] = Counter()
    by_record: list[dict[str, object]] = []
    for record_id, title, text in records:
        row: dict[str, object] = {"id": record_id, "title": title, "chars": len(text)}
        total = 0
        categories: list[str] = []
        for label, pattern in SPECS:
            hits = len(re.findall(pattern, text))
            row[label] = hits
            counts[label] += hits
            if hits:
                record_counts[label] += 1
                categories.append(label)
                total += hits
        row["total_hits"] = total
        row["categories"] = categories
        by_record.append(row)
    return {
        "record_count": len(records),
        "total_chars": sum(len(text) for _, _, text in records),
        "categories": [
            {"label": label, "occurrences": counts[label], "records": record_counts[label]}
            for label, _ in SPECS
        ],
        "by_record": by_record,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readings", action="store_true", help="also audit readings/*.md as a second corpus")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of a table")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    fragments = load_fragments(base_only=args.base_only, exclude=args.exclude_shard)
    result = {"fragments": audit_texts([(str(f["fragment_id"]), str(f["title"]), str(f["text"])) for f in fragments])}

    if args.readings:
        readings = sorted(READINGS.glob("*.md"))
        result["readings"] = audit_texts([(path.stem, path.name, path.read_text(encoding="utf-8")) for path in readings])

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    for corpus, data in result.items():
        print(f"== {corpus} ==")
        print(f"records: {data['record_count']}  chars: {data['total_chars']}")
        for row in data["categories"]:
            print(f"  {row['label']:<18} {row['occurrences']:>6} 回 / {row['records']:>3} 件")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
