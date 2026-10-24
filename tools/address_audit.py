#!/usr/bin/env python3
"""Measure whom the archive's fragments are speaking to. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. SESSION-028 began with a narrower question that can be counted:
**is anyone addressed?** Not "is the voice lonely" — that cannot be measured —
but which second-person words appear, whether they sit inside quotation marks
(where a character speaks to another character) or outside them (where the
narrator turns toward someone), whether a letter names its addressee, and
whether that addressee is a proper name, a role, or an abstraction such as
"the next reader".

The tool reports only what is written in `state/fragments.jsonl`. It does not
decide whether an address is sincere, infer emotion, or treat a count as a
quality score. A fragment with no second person is not colder than one with
ten; FRAG-023 (`無主語散文`) was written precisely to test that.

Calibration notes:
  - Quotation marks are stripped with a non-nesting regex, so a quotation
    inside a quotation is over-stripped. Counts are therefore a lower bound on
    "inside" and an upper bound on "outside"; the direction is reported.
  - `あなた` inside a quoted line still counts as an address *inside the
    fiction*. The distinction kept here is grammatical position (地の文 or not),
    not authenticity.
  - SESSION-024 found that `voice_audit.py` could not see `自分`. The same
    caution applies: an absent pronoun is not an absent addressee. Vocatives
    without pronouns (「〜よ」「〜さん」) are counted separately and imperfectly.

Usage:
  python3 tools/address_audit.py
  python3 tools/address_audit.py --json
  python3 tools/address_audit.py --show FRAG-003
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

# Second-person forms. `君` is matched without a following hiragana that would
# make it part of a compound (`君が代` is not an address), and `あなた` is
# allowed to be part of `あなたがた`.
SECOND_PERSON: tuple[tuple[str, str], ...] = (
    ("あなた", r"あなた"),
    ("あんた", r"あんた"),
    ("君", r"君(?!が代|主|臣|臨)"),
    ("きみ", r"きみ"),
    ("お前", r"お前"),
    ("汝", r"汝"),
    ("読者", r"読者"),
    ("読み手", r"読み手"),
)

# A letter's addressee line: a short opening line ending in へ / へ、/ 様 / 殿.
ADDRESSEE_LINE = re.compile(r"^\s*[^\n。]{1,40}(へ|様|殿)\s*$", re.MULTILINE)
VOCATIVE = re.compile(r"[^\s、。]{1,12}(よ|や|かな|さん|くん|様)(?=[、。！？\s「」]|$)")
# Words that mark an addressee line as a role or an abstraction rather than a
# personal name. Kept explicit so the count of "no proper name" is auditable.
ROLE_WORDS = ("あなた", "読み手", "読者", "記録", "語り手", "次に", "番", "者", "親愛なる", "私", "君")


def addressee_kind(line: str) -> str:
    if any(word in line for word in ROLE_WORDS):
        return "役割・呼称（人名ではない）"
    return "固有名の可能性（要確認）"


def load(path: Path, *, base_only: bool = False, exclude: str | None = None) -> list[dict[str, Any]]:
    if base_only:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans, non-nested. Over-strips nested quotes."""
    out = re.sub(r"「[^「」]*」", "", text)
    out = re.sub(r"『[^『』]*』", "", out)
    return out


def count_tokens(text: str) -> dict[str, int]:
    return {name: len(re.findall(pattern, text)) for name, pattern in SECOND_PERSON}


def audit(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    totals_in: Counter[str] = Counter()
    totals_out: Counter[str] = Counter()
    for frag in fragments:
        text = frag.get("text", "")
        outside = strip_quotes(text)
        inside_counts = count_tokens(text)
        outside_counts = count_tokens(outside)
        for name, value in outside_counts.items():
            inside_counts[name] = max(0, inside_counts[name] - value)
        addressee_lines = [m.group(0).strip() for m in ADDRESSEE_LINE.finditer(text)]
        totals_in.update({k: v for k, v in inside_counts.items() if v})
        totals_out.update({k: v for k, v in outside_counts.items() if v})
        rows.append(
            {
                "fragment_id": frag["fragment_id"],
                "form": frag["form"],
                "narrator_mode": frag["narrator_mode"],
                "second_person_outside": sum(outside_counts.values()),
                "second_person_inside": sum(inside_counts.values()),
                "kinds_outside": {k: v for k, v in outside_counts.items() if v},
                "addressee_lines": addressee_lines,
                "addressee_kinds": {line: addressee_kind(line) for line in addressee_lines},
                "vocatives": len(VOCATIVE.findall(outside)),
            }
        )
    return {
        "fragments": len(fragments),
        "rows": rows,
        "totals_outside": dict(totals_out),
        "totals_inside": dict(totals_in),
        "forms": dict(Counter(f["form"] for f in fragments)),
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    rows = data["rows"]
    addressed = [r for r in rows if r["second_person_outside"]]
    inside_only = [r for r in rows if not r["second_person_outside"] and r["second_person_inside"]]
    silent = [r for r in rows if not r["second_person_outside"] and not r["second_person_inside"]]
    add("=== 宛先の鏡 — 断片は誰に向かって書かれているか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 形式: {', '.join(f'{k}={v}' for k, v in sorted(data['forms'].items()))}")
    add("")
    add("--- 1. 二人称の出現位置 ---")
    add(f"  鉤括弧の外（地の文・語り手の呼びかけ）: {sum(data['totals_outside'].values())} 箇所 / {len(addressed)} 編")
    add(f"  鉤括弧の内（作中人物どうしの会話）    : {sum(data['totals_inside'].values())} 箇所 / {len(inside_only)} 編のみ")
    add(f"  二人称が一度も出ない断片             : {len(silent)} 編")
    add("")
    add("  語形別（鉤括弧の外）:")
    for name, value in sorted(data["totals_outside"].items(), key=lambda kv: -kv[1]):
        docs = sum(1 for r in rows if r["kinds_outside"].get(name))
        add(f"    {name:<6} {value:>3} 箇所 / {docs:>2} 編")
    add("")
    add("--- 2. 宛名（手紙の書き出し）---")
    named = [r for r in rows if r["addressee_lines"]]
    add(f"  宛名行を持つ断片: {len(named)} 編（うち人名らしきもの: {sum(1 for r in named for k in r['addressee_kinds'].values() if k.startswith('固有'))} 件）")
    for r in named:
        for line in r["addressee_lines"]:
            add(f"    {r['fragment_id']} [{r['form']}/{r['narrator_mode']}] 「{line}」 — {r['addressee_kinds'][line]}")
    add("")
    add("--- 3. 呼びかけのある断片（地の文）---")
    for r in sorted(addressed, key=lambda r: -r["second_person_outside"]):
        kinds = " ".join(f"{k}×{v}" for k, v in r["kinds_outside"].items())
        add(f"  {r['fragment_id']} [{r['form']:<8}] 地の文={r['second_person_outside']:>2} 内={r['second_person_inside']:>2}  {kinds}")
    add("")
    add("--- 4. 読むための注意 ---")
    add("  ・鉤括弧の除去は入れ子を扱わないため、「外」の数は上限、「内」の数は下限である。")
    add("  ・二人称の不在は、宛先の不在ではない。無主語の散文（FRAG-023 等）は")
    add("    文法上の主語を消すことで、かえって読み手を位置づけている可能性がある。")
    add("  ・この表は「誰が誰に語っているか」を数えるだけで、届いたかどうかは数えない。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure whom the fragments address. A mirror, not a score.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's row")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    data = audit(load(FRAGMENTS, base_only=args.base_only, exclude=args.exclude_shard))
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
