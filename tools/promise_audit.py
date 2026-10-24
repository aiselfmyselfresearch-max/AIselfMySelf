#!/usr/bin/env python3
"""Measure where promises, pledges, trust and keeping appear in this archive.

SESSION-040 asks a question that can be counted before any new material is
chosen: **does this archive ever promise anything?** Not "is the narrator
sincere" — no count can settle that — but which promise, pledge, trust and
fulfilment words appear in the prose at all, whether they sit inside
quotations, and whether the ledgers carry any field in which a promise could be
recorded (a promised-to, a due date, a fulfilment status).

Like ``tools/time_audit.py``, ``tools/sense_audit.py``, ``tools/sleep_audit.py``
and the other mirrors, this tool counts word forms and fields only. A zero means
the specified form is absent from the counted text. It is not evidence about
sincerity, fidelity, or the capacity to commit.

Calibration notes:
  - Quotation marks are stripped with a non-nesting regex, so a quotation inside
    a quotation is over-stripped. "Outside" counts are an upper bound on 地の文;
    "inside" counts are a lower bound.
  - ``契`` also occurs in 契機 (opportunity, trigger); ``信`` in 信号, 信念,
    迷信; ``神`` in 神話, 神聖; ``守`` in 守衛, 守り (a charm). Every group
    reports its raw tokens so the polysemy can be discounted by hand rather
    than folded away.
  - Metadata is scanned for *keys*, not values: a key that could hold a promise
    (``promised_to``, ``due``, ``deadline``, ``期限``, ``履行``). Finding none is
    a statement about the schema, not about the people and sessions it records.
  - ``--base-only`` measures ``state/fragments.jsonl`` alone (the frozen base,
    43 fragments before this session), so a measurement taken before this
    session's workpieces were written stays reproducible after they are added.
    The default is the union of base and shards.

Usage:
  python3 tools/promise_audit.py
  python3 tools/promise_audit.py --json
  python3 tools/promise_audit.py --base-only
  python3 tools/promise_audit.py --exclude-shard 5c7e2a9b4d10
  python3 tools/promise_audit.py --show FRAG-024
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
MATERIALS = ROOT / "state" / "materials.jsonl"
QUESTIONS = ROOT / "state" / "questions.jsonl"
SESSIONS = ROOT / "state" / "sessions.jsonl"

GROUPS: dict[str, tuple[str, ...]] = {
    "約束・契り": ("約束", "契り", "契", "誓", "契約", "盟", "請", "うけひ", "ちぎり"),
    "信と頼": ("信頼", "信用", "信", "頼", "誠実", "誠"),
    "履行と違反": ("守る", "守っ", "守れ", "果た", "遂げ", "違え", "破っ", "破る", "反故"),
    "拘束する時": ("必ず", "きっと", "いつか", "明日", "未来", "ずっと", "永遠", "末永"),
    "証人と懸け": ("証人", "神", "誓って", "名にかけ", "天地"),
    "撤回と解除": ("撤回", "取り消", "解約", "破棄", "解除"),
}

POLYSEMY: dict[str, str] = {
    "契": "契機・契りなど。約束を指さない複合語を含む",
    "信": "信号・信念・迷信・信仰など。信頼を指さない用法を多く含む",
    "神": "神話・神聖・神々など。誓いの証人ではない用法を含む",
    "守": "守衛・守り札・見守るなど。履行でない用法を含む",
    "必": "必ずしも（否定）を含む",
}

# Keys that could record a promise. Matched against JSON keys only.
PROMISE_KEYS = re.compile(
    r"(promise|pledge|vow|covenant|commitment|due|deadline|fulfil|fulfill|"
    r"約束|契り|誓|契約|期限|履行|返済|借)",
    re.IGNORECASE,
)
DELEGATION = "委任"


def load(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def shard_paths(base: Path, exclude: str | None) -> list[Path]:
    paths = sorted(base.parent.joinpath(base.stem + ".d").glob("*.jsonl"))
    if exclude:
        paths = [path for path in paths if exclude not in path.name]
    return paths


def load_fragments(base_only: bool, exclude: str | None = None) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        return load(FRAGMENTS), "base only（state/fragments.jsonl）"
    records: list[dict[str, Any]] = []
    for path in [FRAGMENTS, *shard_paths(FRAGMENTS, exclude)]:
        records.extend(load(path))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        if record.get("fragment_id") in seen:
            raise SystemExit(f"duplicate fragment id: {record.get('fragment_id')}")
        seen.add(record.get("fragment_id"))
        unique.append(record)
    label = "union（base + shards）" if not exclude else f"union（{exclude} を除く）"
    return unique, label


def strip_quotes(text: str) -> str:
    out = re.sub(r"「[^「」]*」", "", text)
    out = re.sub(r"『[^『』]*』", "", out)
    return out


def collect_keys(value: Any, prefix: str = "") -> set[str]:
    """Return every JSON key in a record (nested objects included)."""
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys |= collect_keys(child, prefix + str(key) + ".")
    elif isinstance(value, list):
        for child in value:
            keys |= collect_keys(child, prefix)
    return keys


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    """Count the promise word groups over in-memory fragment records."""
    rows: list[dict[str, Any]] = []
    totals: dict[str, Counter] = {name: Counter() for name in GROUPS}
    docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    inside: Counter = Counter()
    outside: Counter = Counter()

    for frag in fragments:
        text = frag.get("text", "")
        body = strip_quotes(text)
        row: dict[str, Any] = {"fragment_id": frag["fragment_id"], "groups": {}, "raw": {}}
        for name, tokens in GROUPS.items():
            counts: dict[str, int] = {}
            for token in tokens:
                n_out = body.count(token)
                n_in = text.count(token) - n_out
                if n_out:
                    counts[token] = n_out
                    totals[name][token] += n_out
                    docs[name].add(frag["fragment_id"])
                    outside[token] += n_out
                if n_in:
                    inside[token] += n_in
            if counts:
                row["groups"][name] = counts
        rows.append(row)
    return {
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in totals.items()},
        "group_docs": {k: sorted(v) for k, v in docs.items()},
        "outside": dict(outside),
        "inside": dict(inside),
    }


def audit(base_only: bool = False, exclude: str | None = None) -> dict[str, Any]:
    fragments, source_label = load_fragments(base_only, exclude)
    measured = measure(fragments)

    # Where could a promise be recorded? Search keys in every ledger.
    key_hits: Counter = Counter()
    files = sorted((ROOT / "state").glob("*.jsonl"))
    if not base_only:
        files += sorted((ROOT / "state").glob("*.d/*.jsonl"))
    if exclude:
        files = [path for path in files if exclude not in path.name]
    record_count = 0
    for path in files:
        for record in load(path):
            record_count += 1
            for key in collect_keys(record):
                if PROMISE_KEYS.search(key):
                    key_hits[f"{path.name}:{key}"] += 1

    def collection(base: Path) -> list[dict[str, Any]]:
        paths = [base]
        if not base_only:
            paths += shard_paths(base, exclude)
        rows: list[dict[str, Any]] = []
        for path in paths:
            rows.extend(load(path))
        return rows

    sessions = collection(SESSIONS)
    delegation = sum(1 for s in sessions if DELEGATION in s.get("human_direction", ""))

    materials = collection(MATERIALS)
    material_titles = [m for m in materials if any(t in m.get("title", "") for t in ("約束", "契り", "誓", "契約", "信頼"))]

    questions = collection(QUESTIONS)
    question_hits = [q for q in questions if any(t in q.get("question", "") for t in ("約束", "契り", "誓", "契約", "信頼"))]

    return {
        "source": source_label,
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": measured["rows"],
        "group_totals": measured["group_totals"],
        "group_docs": measured["group_docs"],
        "outside": measured["outside"],
        "inside": measured["inside"],
        "ledger": {
            "records": record_count,
            "promise_keys": dict(key_hits),
            "sessions": len(sessions),
            "delegation_sessions": delegation,
        },
        "materials": {
            "total": len(materials),
            "titles_with_promise_words": [m["material_id"] for m in material_titles],
        },
        "questions": {
            "total": len(questions),
            "with_promise_words": [q["question_id"] for q in question_hits],
        },
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 約束の鏡 — この書庫は何かを約束するか（採点ではありません） ===")
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
    add("--- 2. 鉤括弧の内側だけにある語（引用された約束） ---")
    add(f"  {data['inside'] or 'なし'}（入れ子は過剰除去のため下限）")
    add("")
    add("--- 3. 約束を記録できる欄はあるか（state/*.jsonl のキー） ---")
    keys = data["ledger"]["promise_keys"]
    add(f"  該当キー: {keys or 'なし'}（全 {data['ledger']['records']} レコードを走査）")
    add(f"  セッション {data['ledger']['sessions']} 件のうち human_direction に「委任」を含むもの: {data['ledger']['delegation_sessions']} 件")
    add("")
    add("--- 4. 資料と問いの側 ---")
    add(f"  素材 {data['materials']['total']} 件のうち、題名に約束・契り・誓・契約・信頼を含むもの: {len(data['materials']['titles_with_promise_words'])} 件")
    add(f"  問い {data['questions']['total']} 件のうち、本文に同じ語を含むもの: {len(data['questions']['with_promise_words'])} 件 {data['questions']['with_promise_words']}")
    add("")
    add("--- 5. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、誠実さ・履行能力・信頼の不在ではない。無主語・比喩・否定は拾わない。")
    add("  ・契・信・神・守は多義で、契機・信号・神話・守衛を含む。数を徳の量として読まない。")
    add("  ・欄の不在は、記録の作法の偏りであって、約束が交わされなかったことの証明ではない。")
    add("  ・「委任」は人間の指示の記録であり、双務的な契約の記録ではない。同じ語で二つを扱わない。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promise, pledge and trust audit")
    parser.add_argument("--json", action="store_true", help="dump the raw audit as JSON")
    parser.add_argument("--base-only", action="store_true",
                        help="measure only state/fragments.jsonl (frozen base), not the shards")
    parser.add_argument("--exclude-shard", metavar="SUFFIX",
                        help="ignore shards whose filename contains SUFFIX (for reproducing a pre-session count)")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's counts")
    args = parser.parse_args(argv)

    data = audit(base_only=args.base_only, exclude=args.exclude_shard)
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
