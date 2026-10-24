#!/usr/bin/env python3
"""Measure how the archive handles words it did not witness. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. This session began with a narrower question that can be counted:
**where does a sentence come from, and does the archive say so?**

Not "can a model know anything at second hand" — that cannot be counted. What
can be counted is which word forms of hearsay (と聞く, 噂, 伝聞, 証言), of
citation (引用, 出典, 註), of summary (要約, 編者, 抜粋) and of checking
(疑い, 照合, 裏付) appear in the fragments' prose; how many of the stored
materials are the editor's summary rather than a quoted passage; and how many
of the close-reading notes' "一節" lines are summaries.

Calibration notes:
  - ``と聞`` / ``聞い`` catch both "heard with the ear" and "heard tell".
    ``聞`` as a bare character is reported separately (:data:`RAW_TOKENS`): it
    also occurs in 聞き手, 聞こえる, 新聞, 伝聞. The tool cannot tell an ear
    from a report, so it does not.
  - ``そうだ`` / ``らしい`` / ``ようだ`` are inference, not hearsay, and are
    counted in a separate group. Folding them into hearsay would inflate the
    number with guesses.
  - ``証`` inside 証拠・証言・保証 is polyvalent; only the explicit tokens are
    counted, and the raw character is listed for hand classification.
  - Quoted spans are removed from the main count and reported separately as
    ``inside_quotes``: a character quoting someone is not the archive speaking
    in its own voice.
  - ``引用`` and ``要約`` in a fragment can describe the act of quoting without
    performing it. The tool counts the word, not the act.
  - For materials, ``passage`` values beginning with 【編者による要約】 are
    counted as summaries. That marker is an editorial convention, not proof
    that the rest of the passage was checked against the original.
  - For readings, a line counts as a summary when the marker appears anywhere
    in it. A line that merely *reports* the marker's frequency is therefore
    counted too; this session hit that trap (see the report's §4) and reworded
    its own 一節 line rather than special-casing the tool.

A zero is the absence of the specified word form, not the absence of testimony,
rumour, trust or doubt.

Usage:
  python3 tools/hearsay_audit.py
  python3 tools/hearsay_audit.py --json
  python3 tools/hearsay_audit.py --show FRAG-032
  python3 tools/hearsay_audit.py --base-only
  python3 tools/hearsay_audit.py --exclude-shard 5c7e2a9b4d10
  python3 tools/hearsay_audit.py --materials
  python3 tools/hearsay_audit.py --readings
  python3 tools/hearsay_audit.py --all

The default count is the union of the frozen base file and every shard
(``state/fragments.d/*.jsonl``), matching ``validate_seed.py`` and
``inspect_inquiry.py``. ``--base-only`` reproduces a measurement taken against
the base file alone. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
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
    "伝聞の標識": (
        "と聞", "聞いた", "聞いて", "聞く", "聞け", "聞こえ", "噂", "うわさ",
        "風聞", "伝聞", "伝え", "曰く", "によれば", "だそう", "と言われ",
        "とされている", "話に", "話では",
    ),
    "証言・証拠": (
        "証言", "証拠", "目撃", "証人", "陳述", "供述", "宣誓", "事実",
    ),
    "引用・要約・出典": (
        "引用", "出典", "註", "注釈", "要約", "編者", "抜粋", "孫引",
        "出所", "書誌", "括弧", "原典", "典拠",
    ),
    "疑い・照合": (
        "疑い", "疑わ", "信じ", "確かめ", "検証", "照合", "裏付", "誤り",
        "訂正", "嘘", "ごまかし",
    ),
    "情報源・経路": (
        "誰か", "ある人", "人が言", "消息", "情報", "筋", "伝手", "続報",
        "報道", "ニュース",
    ),
    "推量（伝聞ではない）": (
        "らしい", "ようだ", "かもしれ", "だろう", "おそらく", "推測",
    ),
    "対照（書庫の常用語）": (
        "書く", "書い", "読む", "読ん", "残す", "残っ", "次", "資料",
        "記録", "断片", "頁",
    ),
}

RAW_TOKENS = ("聞", "噂", "証", "引", "注", "伝")
POLYSEMY_NOTE = {
    "聞": "聞き手・聞こえる・新聞・伝聞を含むため参考値",
    "噂": "噂そのもの（多義ではないが、地の文の数として掲げる）",
    "証": "保証・証明・特徴を含むため参考値",
    "引": "引く・引かれる・引用を含むため参考値",
    "注": "注意・注ぐを含むため参考値",
    "伝": "伝記・手伝い・宣伝を含むため参考値",
}


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans so quoted voices are not counted as prose."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, for the inside_quotes tally."""
    return "".join(QUOTE.findall(text))


def load_union(path: Path, id_key: str, exclude: str | None = None) -> list[dict[str, Any]]:
    """Load the frozen base file plus every shard, as the validators do."""
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT, exclude=exclude)
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
    all_tokens = tuple(t for g in GROUPS.values() for t in g)
    for frag in fragments:
        text = frag.get("text", "")
        prose = strip_quotes(text)
        quote = split_quotes(text)
        row: dict[str, Any] = {"fragment_id": frag.get("fragment_id", "?"), "groups": {}, "raw": {}}
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
        inside.update(count_group(quote, all_tokens))
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


def measure_materials(materials: list[dict[str, Any]]) -> dict[str, Any]:
    """Count how much of the material store is the editor's summary."""
    kinds: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    summary_passages = 0
    quote_passages = 0
    by_kind_summary: Counter[str] = Counter()
    missing_passage = 0
    for m in materials:
        kind = m.get("kind", "?")
        kinds[kind] += 1
        status = (m.get("verification") or {}).get("status", "none")
        statuses[status] += 1
        passage = m.get("passage", "") or ""
        if not passage:
            missing_passage += 1
        is_summary = passage.startswith("【編者による要約】") or "【編者による要約】" in passage[:30]
        if is_summary:
            summary_passages += 1
            by_kind_summary[kind] += 1
        if QUOTE.search(passage):
            quote_passages += 1
    return {
        "materials": len(materials),
        "kinds": dict(kinds),
        "statuses": dict(statuses),
        "summary_passages": summary_passages,
        "summary_by_kind": dict(by_kind_summary),
        "quote_passages": quote_passages,
        "missing_passage": missing_passage,
    }


SECTION = re.compile(r"^- \*\*一節")


def measure_readings(folder: Path = READINGS) -> dict[str, Any]:
    files = sorted(folder.glob("*.md"))
    sections = 0
    summary_sections = 0
    quoted_sections = 0
    chars = 0
    tokens: Counter[str] = Counter()
    per_file: list[dict[str, Any]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        chars += len(text)
        local_sections = local_summary = local_quoted = 0
        for line in text.splitlines():
            if SECTION.match(line):
                local_sections += 1
                if "編者による要約" in line:
                    local_summary += 1
                if QUOTE.search(line):
                    local_quoted += 1
        sections += local_sections
        summary_sections += local_summary
        quoted_sections += local_quoted
        for token in ("原典未閲覧", "未確認", "内部知識", "ウェブ検索"):
            tokens[token] += text.count(token)
        per_file.append(
            {
                "file": path.name,
                "chars": len(text),
                "sections": local_sections,
                "summary_sections": local_summary,
                "quoted_sections": local_quoted,
            }
        )
    return {
        "files": len(files),
        "chars": chars,
        "median_chars": int(statistics.median([p["chars"] for p in per_file])) if per_file else 0,
        "sections": sections,
        "summary_sections": summary_sections,
        "quoted_sections": quoted_sections,
        "tokens": dict(tokens),
        "per_file": per_file,
    }


def report(data: dict[str, Any]) -> str:
    lines = ["=== 伝聞の鏡 — AIselfMySelf 台帳の「聞いた話」を映す（採点ではありません） ==="]
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
        lines.append(f"  {row['fragment_id']}: " + " / ".join(parts))
    lines.append("")
    lines.append("0は指定語形の不在であって、証言・伝聞・信頼・疑いの不在ではありません。")
    return "\n".join(lines)


def materials_report(data: dict[str, Any]) -> str:
    lines = ["=== 素材の鏡 — 「一節」は誰の言葉か ==="]
    lines.append(f"素材 {data['materials']} 件 / 種類: " + "、".join(f"{k}={v}" for k, v in sorted(data["kinds"].items())))
    lines.append("書誌状態: " + "、".join(f"{k}={v}" for k, v in sorted(data["statuses"].items())))
    share = (data["summary_passages"] / data["materials"] * 100) if data["materials"] else 0.0
    lines.append(
        f"【編者による要約】で始まる passage: {data['summary_passages']} 件"
        f"（{share:.1f}%）/ 鉤括弧を含む passage: {data['quote_passages']} 件"
        f" / passage 空: {data['missing_passage']} 件"
    )
    if data["summary_by_kind"]:
        lines.append(
            "種類別: " + "、".join(f"{k}={v}" for k, v in sorted(data["summary_by_kind"].items()))
        )
    lines.append("")
    lines.append("要約の印は、要約であることの表明であって、原典との一致の証明ではありません。")
    return "\n".join(lines)


def readings_report(data: dict[str, Any]) -> str:
    lines = ["=== 精読報告の鏡 — 「一節」の欄は何で埋まっているか ==="]
    lines.append(
        f"報告 {data['files']} 本 / 計 {data['chars']:,} 字（中央値 {data['median_chars']:,} 字）"
    )
    share = (data["summary_sections"] / data["sections"] * 100) if data["sections"] else 0.0
    lines.append(
        f"「一節」行: {data['sections']} 行 / うち編者要約 {data['summary_sections']} 行"
        f"（{share:.1f}%）/ うち鉤括弧を含む {data['quoted_sections']} 行"
    )
    if data["tokens"]:
        lines.append("限界の語: " + "、".join(f"{k}×{v}" for k, v in data["tokens"].items()))
    lines.append("")
    largest = sorted(data["per_file"], key=lambda p: p["sections"], reverse=True)[:5]
    lines.append("「一節」行が多い報告（上位5）:")
    for item in largest:
        lines.append(
            f"  {item['file']}: {item['sections']} 行（要約 {item['summary_sections']}）"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="print the raw measurement as JSON")
    parser.add_argument("--show", metavar="FRAGMENT_ID", help="show one fragment's hits and prose")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base file")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards whose name contains SUFFIX")
    parser.add_argument("--materials", action="store_true", help="measure the material store")
    parser.add_argument("--readings", action="store_true", help="measure the close-reading notes")
    parser.add_argument("--all", action="store_true", help="fragments, materials and readings")
    args = parser.parse_args(argv)

    if args.show:
        fragments = (
            [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
            if args.base_only
            else load_union(FRAGMENTS, "fragment_id", args.exclude_shard)
        )
        for frag in fragments:
            if frag.get("fragment_id") == args.show:
                prose = strip_quotes(frag.get("text", ""))
                lines = [f"=== {args.show} ===", "", frag.get("text", ""), "", "--- 地の文の語 ---"]
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

    payload: dict[str, Any] = {}
    if args.readings:
        payload["readings"] = measure_readings()
    if args.materials:
        payload["materials"] = measure_materials(load_union(MATERIALS, "material_id", args.exclude_shard))
    if args.all or not (args.materials or args.readings):
        fragments = (
            [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
            if args.base_only
            else load_union(FRAGMENTS, "fragment_id", args.exclude_shard)
        )
        payload["fragments"] = measure(fragments)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    blocks: list[str] = []
    if "fragments" in payload:
        blocks.append(report(payload["fragments"]))
    if "materials" in payload:
        blocks.append(materials_report(payload["materials"]))
    if "readings" in payload:
        blocks.append(readings_report(payload["readings"]))
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
