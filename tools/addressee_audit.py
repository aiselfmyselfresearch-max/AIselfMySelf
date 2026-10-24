#!/usr/bin/env python3
"""Count who the archive is writing *to*. A mirror, not a score.

`voice_audit.py` counts how the fragments repeat themselves. This tool counts
something the ledgers have never recorded: the **addressee**. It measures four
things and refuses to grade any of them.

1. **Two-person markers** (あなた / 君 / 汝 / you / thou …) per collection.
2. **Question marks and sentence-final `のか。`** — a question can be written as
   an indirect noun clause, which belongs to nobody in particular.
3. **Address-bearing titles** (`…へ`, `…宛`, 手紙, 書簡).
4. **The schema field inventory**: every leaf field, split into fields that
   point *backward* to an origin (source, session, previous, commit …) and
   fields that would point *forward* to a recipient (addressee, audience,
   recipient, reader …).

Why this tool (SESSION-027):
  SESSION-026 measured the quotation marks and found that nine out of ten
  belonged to the ledger's own voices rather than to sources. Reading that
  result, a simpler question was left over: if the bibliographies live in the
  `material_ids` column, and the questions live in `question`, then *whose eyes
  are any of these rows written for?* The schemas were inspected first, and no
  field in any of the six collections names a recipient. This tool exists to
  keep that absence measurable, not to fill it.

Known blindness (read before trusting the numbers):
  - Japanese drops pronouns. A sentence can address someone with no あなた in it
    (「〜しなさい」「〜だろうか」). The two-person counts are therefore a **lower
    bound**, not a census.
  - `narrator_mode` and `editor_note` matched the substring search for `or`/`e`
    in an early draft of this tool. They are *not* recipient fields. The list
    below is explicit, not a substring match, precisely to avoid that error.
  - English passages count `you`, which in verse may be generic ("you" = anyone).
  - The tool never reads `readings/`, so it cannot see an addressee named only in
    prose notes.

Usage:
  python3 tools/addressee_audit.py
  python3 tools/addressee_audit.py --json
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

COLLECTIONS: tuple[tuple[str, str, str, str], ...] = (
    # (ledger name, schema name, id field, text field(s) separated by |)
    ("questions", "question", "question_id", "question|notes"),
    ("motifs", "motif", "motif_id", "label|description"),
    ("materials", "material", "material_id", "passage|context|literary_invitation"),
    ("fragments", "fragment", "fragment_id", "title|text"),
    ("sessions", "session", "session_id", "human_direction|notes"),
    ("relations", "relation", "relation_id", "note"),
)

SECOND_PERSON_JA = (
    "あなた",
    "貴方",
    "貴女",
    "あんた",
    "君",
    "きみ",
    "お前",
    "おまへ",
    "お前さん",
    "汝",
    "そなた",
    "手前",
    "てめえ",
    "貴様",
)
SECOND_PERSON_EN = ("you", "your", "thou", "thee", "thy")

IMPERATIVE = ("せよ", "しなさい", "してください", "ください", "なさい", "べし", "たまへ", "給へ")

ADDRESS_IN_TITLE_RE = re.compile(r"(へ(——|の|$)|宛|書簡|手紙)")

# Fields that point backward, to where a record came from.
ORIGIN_FIELDS = {
    "created_at",
    "started_at",
    "origin",
    "detail",
    "session_id",
    "previous_question_ids",
    "source",
    "source_id",
    "source_record_id",
    "source_record_path",
    "evidence_record_id",
    "evidence_record_path",
    "repository",
    "commit",
    "material_ids",
    "question_ids",
    "motif_ids",
    "context_material_ids",
    "produced_fragment_ids",
    "new_question_ids",
    "prompt_template",
    "generator",
    "url",
    "authors",
    "year",
    "version_note",
    "type",
    "id",
}

# Fields that would point forward, to whom a record is addressed.
RECIPIENT_FIELDS = {
    "addressed_to",
    "addressee",
    "audience",
    "recipient",
    "reader",
    "readers",
    "for_whom",
    "intended_reader",
    "dedication",
}

CONTENT_FIELDS = {
    "fragment_id",
    "material_id",
    "motif_id",
    "question_id",
    "relation_id",
    "session_id",
    "relation_type",
    "left",
    "right",
    "title",
    "text",
    "passage",
    "passage_language",
    "context",
    "source_note",
    "literary_invitation",
    "scope_note",
    "question",
    "notes",
    "note",
    "label",
    "description",
    "language",
    "form",
    "narrator_mode",
    "status",
    "kind",
    "human_direction",
    "editor_note",
}


def load(ledger: str) -> list[dict[str, Any]]:
    path = ROOT / "state" / f"{ledger}.jsonl"
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def leaf_paths(spec: Any, prefix: str = "") -> Iterable[str]:
    if not isinstance(spec, dict):
        return
    properties = spec.get("properties")
    if isinstance(properties, dict) and properties:
        for key, child in properties.items():
            yield from leaf_paths(child, f"{prefix}.{key}" if prefix else key)
    elif "$ref" in spec:
        # References (relation.left / right) are resolved by the caller.
        yield prefix
    else:
        yield prefix


def schema_fields() -> list[str]:
    fields: set[str] = set()
    for schema_path in sorted((ROOT / "schema").glob("*.schema.json")):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for path in leaf_paths(schema):
            fields.add(path)
        defs = schema.get("$defs", {})
        if isinstance(defs, dict):
            for name, sub in defs.items():
                for path in leaf_paths(sub):
                    fields.add(f"$defs.{name}.{path}")
    return sorted(fields)


def text_of(record: dict[str, Any], spec: str) -> str:
    return "\n".join(str(record.get(key, "")) for key in spec.split("|"))


def ending_kind(text: str) -> str:
    body = text.strip().rstrip("。．.？?！!")
    for suffix in ("のか", "だろうか", "であろうか", "か", "のか。", "だろう"):
        if body.endswith(suffix):
            return f"…{suffix}。"
    return "…（その他）。"


def endings(questions: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in questions:
        counter[ending_kind(str(row.get("question", "")))] += 1
    return counter


def audit() -> dict[str, Any]:
    report: dict[str, Any] = {"collections": {}, "schema": {}, "question_endings": {}}
    for ledger, _schema, _id_field, text_fields in COLLECTIONS:
        rows = load(ledger)
        second_ja = []
        second_en = []
        marks = []
        imperatives = []
        readers = []
        for row in rows:
            text = text_of(row, text_fields)
            if any(token in text for token in SECOND_PERSON_JA):
                second_ja.append(row)
            if any(token in text.lower() for token in SECOND_PERSON_EN):
                second_en.append(row)
            if "?" in text or "？" in text:
                marks.append(row)
            if any(token in text for token in IMPERATIVE):
                imperatives.append(row)
            if "読者" in text:
                readers.append(row)
        report["collections"][ledger] = {
            "records": len(rows),
            "with_second_person_ja": len(second_ja),
            "with_second_person_en": len(second_en),
            "with_question_mark": len(marks),
            "with_imperative": len(imperatives),
            "with_reader_word": len(readers),
            "average_chars": round(sum(len(text_of(r, text_fields)) for r in rows) / len(rows), 1) if rows else 0.0,
        }

    report["fragments_with_address_title"] = [
        {"fragment_id": row.get("fragment_id"), "title": row.get("title", "")}
        for row in load("fragments")
        if ADDRESS_IN_TITLE_RE.search(str(row.get("title", "")))
    ]

    fields = schema_fields()
    origin = [f for f in fields if f.split(".")[-1] in ORIGIN_FIELDS]
    recipient = [f for f in fields if f.split(".")[-1] in RECIPIENT_FIELDS]
    content = [f for f in fields if f.split(".")[-1] in CONTENT_FIELDS]
    unclassified = [f for f in fields if f not in origin and f not in recipient and f not in content]
    report["schema"] = {
        "leaf_fields": len(fields),
        "origin_pointing": origin,
        "recipient_pointing": recipient,
        "content_or_structural": content,
        "unclassified": unclassified,
    }

    report["question_endings"] = dict(endings(load("questions")))
    return report


def print_report(report: dict[str, Any]) -> None:
    print("=== addressee audit — 宛先の鏡（採点しない） ===")
    print()
    print(f"{'ledger':12s} {'n':>4s} {'二人称日':>8s} {'二人称英':>8s} {'?':>4s} {'命令':>4s} {'読者':>4s} {'平均字数':>8s}")
    for ledger, row in report["collections"].items():
        print(
            f"{ledger:12s} {row['records']:4d} {row['with_second_person_ja']:8d} "
            f"{row['with_second_person_en']:8d} {row['with_question_mark']:4d} "
            f"{row['with_imperative']:4d} {row['with_reader_word']:4d} {row['average_chars']:8.1f}"
        )
    print()
    print("断片の題に宛先の印（「へ」「宛」「書簡」）があるもの:")
    if report["fragments_with_address_title"]:
        for row in report["fragments_with_address_title"]:
            print(f"  - {row['fragment_id']}: {row['title']}")
    else:
        print("  （なし）")
    print()
    schema = report["schema"]
    print(f"スキーマの葉の欄: {schema['leaf_fields']} 個")
    print(f"  由来を指す欄（origin-facing）: {len(schema['origin_pointing'])} 個")
    print(f"  宛先を指す欄（recipient-facing）: {len(schema['recipient_pointing'])} 個 -> {schema['recipient_pointing'] or 'なし'}")
    if schema["unclassified"]:
        print(f"  未分類: {schema['unclassified']}")
    print()
    print("問いの文末:")
    for tail, count in sorted(report["question_endings"].items(), key=lambda kv: -kv[1]):
        print(f"  {tail!r}: {count}")
    print()
    print("註: 日本語は二人称を省略しうる。二人称の数は下限であって全数ではない。")
    print("註: この鏡は readings/ を読まない。散文ノートの中だけに書かれた宛先は映らない。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Count addressees in the ledgers (a mirror, not a score).")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args(argv)
    report = audit()
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
