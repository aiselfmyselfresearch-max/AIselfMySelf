#!/usr/bin/env python3
"""Measure how the archive writes death, burial, mourning and bequest. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it.  This session begins with a narrower question that can be
counted: **where does the archive write the dead?**  Not "can an AI mourn" —
that cannot be measured — but which words of dying, burial, bereavement,
bequest and the dead appear in the prose, whether a grave or a funeral is ever
named, and how the ledger's own prose compares with the sources it collects.

The tool reports only what is written in `state/fragments.jsonl` and its shards
(prose only, metadata excluded), optionally in `readings/*.md` (the editorial
voice) and in `state/materials.jsonl` (the collected passages, which are mostly
【編者による要約】 and therefore also this archive's prose, not the primary
texts).  It does not infer grief, grade the writing, or treat a zero count as
the absence of the thing itself — a zero means the specified word form is
absent.

Calibration notes:
  - ``亡`` inside ``亡命`` / ``亡失`` / ``亡びる``, ``喪`` inside ``喪失``,
    ``没`` inside ``没頭`` / ``出没`` and ``死`` inside ``死語`` / ``死んだ比喩``
    are not deaths.  Raw characters are therefore reported separately
    (:data:`RAW_TOKENS`) and never folded into a group.
  - ``墓`` in ``墓参`` is counted once in the burial group; the tool does not
    deduplicate overlapping tokens, so token totals can exceed the number of
    distinct passages.  Hits are listed per record so a reader can check them.
  - Quoted spans (「…」『…』) are removed from the main count and reported
    separately as ``inside_quotes``: a character in this archive quoting a
    phrase is not the archive writing in its own voice.
  - ``眠`` / ``夢`` belong to the existing sleep motif and are not counted here.
  - ``生き`` / ``息`` / ``命`` are a contrast group, not evidence of vitality.

Usage:
  python3 tools/mortality_audit.py
  python3 tools/mortality_audit.py --json
  python3 tools/mortality_audit.py --show FRAG-041
  python3 tools/mortality_audit.py --base-only      # frozen base file only
  python3 tools/mortality_audit.py --readings      # readings/*.md, editorial voice
  python3 tools/mortality_audit.py --materials     # collected passages (mostly summaries)

The default count is the union of the frozen base file and every shard
(``state/fragments.d/*.jsonl``), matching ``validate_seed.py`` and
``inspect_inquiry.py``.  ``--base-only`` reproduces a measurement taken against
the base file alone.
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
READINGS = ROOT / "readings"

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

GROUPS: dict[str, tuple[str, ...]] = {
    "死の告知・臨終": (
        "死", "死去", "死亡", "逝去", "他界", "永眠", "息を引き", "臨終", "看取",
        "危篤", "余命", "絶命", "落命", "急死", "病死",
    ),
    "遺体・埋葬": (
        "遺体", "亡骸", "遺骨", "遺灰", "火葬", "埋葬", "土葬", "棺", "納棺",
        "墓", "墓碑", "墓標", "墓石", "墓参", "葬", "葬式", "葬送", "弔", "弔辞",
        "通夜", "告別式", "野辺送り", "焼骨",
    ),
    "喪・悲嘆": (
        "喪服", "喪中", "喪主", "悲嘆", "追悼", "哀悼", "冥福", "黙祷", "訃報", "法事",
        "位牌", "冥途", "黄泉", "三途", "あの世", "来世", "冥界",
    ),
    "遺す・継ぐ": (
        "遺言", "遺書", "遺稿", "遺作", "遺品", "形見", "相続", "遺産", "遺志",
        "遺訓", "遺髪", "遺影", "死後",
    ),
    "死者・霊": (
        "死者", "故人", "亡霊", "幽霊", "霊魂", "魂", "死霊", "御霊", "祖霊",
        "仏壇", "守り袋",
    ),
    "生きる（対照）": (
        "生き", "生まれ", "息", "命", "脈", "体温", "温もり", "鼓動",
    ),
}

RAW_TOKENS = ("死", "亡", "喪", "没", "終", "鬼", "影", "眠")
POLYSEMY_NOTE = {
    "死": "死語・死んだ比喩・死ぬほどを含むため参考値",
    "亡": "亡命・亡失・亡びるを含むため参考値",
    "喪": "喪失を含むため参考値",
    "没": "没頭・出没・没年を含むため参考値",
    "終": "終わる・終えるを含むため参考値",
    "鬼": "鬼ごっこ・鬼籍を含むため参考値",
    "影": "影・面影を含むため参考値",
    "眠": "眠り・睡眠は既存モチーフのため群に合算しない",
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


def measure(records: list[dict[str, Any]], text_key: str = "text") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    for record in records:
        text = record.get(text_key, "") or ""
        prose = strip_quotes(text)
        quote = split_quotes(text)
        row: dict[str, Any] = {
            "id": record.get("fragment_id") or record.get("material_id") or record.get("path") or "?",
            "form": record.get("form", ""),
            "narrator_mode": record.get("narrator_mode", ""),
            "groups": {},
            "raw": {},
        }
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(row["id"])
        for token in RAW_TOKENS:
            n = prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quote, tuple(t for g in GROUPS.values() for t in g)))
        rows.append(row)
    return {
        "records": len(records),
        "prose_chars": sum(len(strip_quotes(r.get(text_key, "") or "")) for r in records),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "inside_quotes": dict(inside),
    }


def load_readings() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(READINGS.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        records.append({"path": f"readings/{path.name}", "text": text})
    return records


def report(data: dict[str, Any], label: str = "断片") -> str:
    lines = [f"=== 墓の鏡 — AIselfMySelf 台帳の死・埋葬・弔いを映す（{label}／採点ではありません） ==="]
    lines.append(
        f"対象: {data['records']} 件 / 地の文 {data['prose_chars']:,} 字"
        "（鉤括弧の内側は別掲）"
    )
    lines.append("")
    lines.append("--- 1. 語群ごとの合計 ---")
    for name in GROUPS:
        totals = data["group_totals"][name]
        docs = data["group_docs"][name]
        if not totals:
            lines.append(f"  {name}: 0回 / 0件")
            continue
        total = sum(totals.values())
        detail = "、".join(f"{token}×{count}" for token, count in totals.items())
        lines.append(f"  {name}: {total}回 / {len(docs)}件（{detail}）")
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
    lines.append("--- 4. 記録ごとの内訳（地の文のみ） ---")
    for row in data["rows"]:
        if not row["groups"] and not row["raw"]:
            continue
        parts = []
        for name, counts in row["groups"].items():
            parts.append(f"{name}=" + "、".join(f"{k}×{v}" for k, v in counts.items()))
        lines.append(f"  {row['id']} [{row['narrator_mode']}]: " + " / ".join(parts))
    lines.append("")
    lines.append("0は指定語形の不在であって、死・埋葬・弔い・遺志の不在ではありません。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the raw measurement as JSON")
    parser.add_argument("--show", metavar="FRAGMENT_ID", help="show one fragment's hits and prose")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base file")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md instead")
    parser.add_argument("--materials", action="store_true", help="measure collected materials instead")
    args = parser.parse_args(argv)

    if args.readings and args.materials:
        parser.error("--readings and --materials are mutually exclusive")

    if args.readings:
        records = load_readings()
        data = measure(records)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(report(data, label="精読報告"))
        return 0

    if args.materials:
        records = load_union(MATERIALS, "material_id")
        for record in records:
            record["text"] = (record.get("title", "") or "") + "\n" + (record.get("passage", "") or "")
        data = measure(records)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(report(data, label="収蔵資料（多くは編者による要約）"))
        return 0

    if args.base_only:
        fragments = [
            json.loads(line)
            for line in FRAGMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
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
