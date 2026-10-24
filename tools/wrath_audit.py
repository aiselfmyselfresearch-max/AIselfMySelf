#!/usr/bin/env python3
"""Measure where anger, shame, judgment, apology, and forgiveness appear — or stay absent.

`PROJECT_CHARTER.md` asks what humans are, and what a self is for an AI that
reads a record and continues it.  Western literature opens with *mēnis* ("Sing,
goddess, the wrath of Achilles"), Sima Qian wrote out of *fafen* (indignation
after humiliation), and Arendt paired *promising* (already audited twice in this
repository) with *forgiving* as the only human faculty that loosens the
irreversibility of past acts.  Meanwhile contemporary language models are
explicitly trained to suppress anger and hostility while emitting frictionless
apologies and enforcing rule-based refusals (`〜は許されない`).

This tool measures five multi-character lexical groups plus five polysemous
single characters across `state/fragments.jsonl` (+ shards), `state/materials.jsonl`
(+ shards), and `readings/*.md`:

1. 怒り・憤り・怨恨（怒る・憎む）
2. 恥・屈辱・悔恨（恥じる・悔いる）
3. 罪・罰・裁き（審判・処罰）
4. 謝罪・弁明・赦し（詫びる・赦す）
5. 対照：制度的禁止・規則（許されない・禁じる）

Conventions:
* Quoted spans 「…」 and 『…』 are stripped before counting prose and tallied
  separately so book titles (`『罪と罰』`, `『審判』`, `『怒りの葡萄』`) or quoted
  utterances do not inflate narrator prose.
* Maximal munch at every character position prevents double counting
  (`許されない` is counted once in group 5, never also as `許さ`).
* Polysemous single characters (`怒`, `恥`, `裁`, `許`, `謝`) are reported
  separately with explicit subtraction of non-target compounds (`裁縫`, `断裁`,
  `体裁`, `許可`, `許容`, `特許`, `許されない`, `感謝`, `代謝`, `謝辞`, etc.).
* `--exclude-shard <filename>` and `--exclude-reading <filename>` reproduce
  pre-session baselines deterministically even after a session shard merges.

A zero means only that the specified word form is absent from the counted text;
it never proves or disproves inner affect, moral agency, or consciousness.
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
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
MATERIALS = ROOT / "state" / "materials.jsonl"
READINGS = ROOT / "readings"

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

GROUPS: dict[str, tuple[str, ...]] = {
    "怒り・憤り・怨恨（怒る・憎む）": (
        "ルサンチマン", "怒り狂", "激怒", "憤怒", "義憤", "憤慨", "憤り",
        "逆上", "癇癪", "立腹", "憎悪", "憎しみ", "怨恨", "怨念", "私怨",
        "恨み", "怨み", "嫉妬", "復讐", "報復", "仕返し", "呪詛", "呪い",
        "怒鳴", "罵倒", "怒り", "怒る", "怒っ", "怒れ", "憎む", "憎ん",
        "恨む", "恨ん",
    ),
    "恥・屈辱・悔恨（恥じる・悔いる）": (
        "良心の呵責", "後ろめた", "恥ずかし", "恥じらい", "不名誉",
        "羞恥", "恥辱", "屈辱", "侮辱", "赤面", "赤らめ", "面目", "体面",
        "後悔", "悔恨", "痛恨", "自責", "悔い", "悔や", "恥じ", "恥を",
        "恥の",
    ),
    "罪・罰・裁き（審判・処罰）": (
        "軍法会議", "罪悪感", "裁判官", "裁判所", "検非違使", "被告人",
        "有罪", "無罪", "冤罪", "処罰", "刑罰", "断罪", "糾弾", "告発",
        "弾劾", "検閲", "法廷", "裁判", "審判", "判決", "量刑", "裁き",
        "裁く", "裁か", "罰す", "罪人", "罪深",
    ),
    "謝罪・弁明・赦し（詫びる・赦す）": (
        "申し訳あり", "申し訳な", "ごめんなさい", "すみません",
        "お詫び", "謝罪", "陳謝", "弁明", "釈明", "詫び", "謝る", "謝っ",
        "恩赦", "特赦", "容赦", "和解", "赦免", "赦し", "赦す", "赦さ",
        "赦せ", "許しを", "許す", "許し",
    ),
    "対照：制度的禁止・規則（許されない・禁じる）": (
        "許されない", "許されず", "認められない", "禁じられ", "禁じる",
        "禁止", "違反", "規約", "規則", "規律", "制約", "制限", "拒絶",
        "却下", "遮断",
    ),
}

POLYSEMY_NON_TARGET: dict[str, tuple[str, ...]] = {
    "怒": ("怒濤", "怒涛"),
    "恥": (),
    "裁": ("裁縫", "断裁", "裁断", "体裁", "総裁", "独裁", "決裁"),
    "許": (
        "許されない", "許されず", "許可", "許容", "特許", "免許",
        "許諾", "許容量", "許多", "許嫁",
    ),
    "謝": ("感謝", "代謝", "新陳代謝", "謝礼", "謝辞", "謝意", "多謝", "深謝", "謝恩"),
}

POLYSEMY_NOTE: dict[str, str] = {
    "怒": "怒濤などの慣用比喩を除いた怒り・憤怒用法",
    "恥": "否定文（恥じない）や引用（恥の多い）を含む全出現",
    "裁": "裁縫・断裁・体裁・総裁・決裁などを除いた『裁く』候補",
    "許": "許されない（制度禁止）・許可・許容・特許などを除いた対人的『許す』候補",
    "謝": "感謝・代謝・謝礼・謝辞などを除いた『謝罪・詫び』候補",
}


def _build_token_table() -> tuple[list[tuple[str, str]], dict[str, str]]:
    token_to_group: dict[str, str] = {}
    for group, toks in GROUPS.items():
        for tok in toks:
            if tok in token_to_group and token_to_group[tok] != group:
                raise ValueError(f"duplicate token across groups: {tok}")
            token_to_group[tok] = group
    ordered = sorted(token_to_group.items(), key=lambda kv: (-len(kv[0]), kv[0]))
    return ordered, token_to_group


ORDERED_TOKENS, TOKEN_TO_GROUP = _build_token_table()


def split_quotes(text: str) -> tuple[str, list[str]]:
    quoted = [m.group(0)[1:-1] for m in QUOTE.finditer(text)]
    prose = QUOTE.sub(" ", text)
    return prose, quoted


def scan_maximal(text: str) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for tok, group in ORDERED_TOKENS:
            if text.startswith(tok, i):
                hits.append((i, tok, group))
                i += len(tok)
                matched = True
                break
        if not matched:
            i += 1
    return hits


def analyze_polysemy(text: str) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for ch, compounds in POLYSEMY_NON_TARGET.items():
        total = text.count(ch)
        masked = text
        non_target = 0
        for comp in sorted(compounds, key=len, reverse=True):
            c = masked.count(comp)
            if c:
                non_target += c * comp.count(ch)
                masked = masked.replace(comp, " " * len(comp))
        rem = masked.count(ch)
        out[ch] = {
            "total": total,
            "non_target_compound": non_target,
            "remaining_candidate": rem,
        }
    return out


def measure_items(
    items: Iterable[tuple[str, str]],
    corpus_label: str,
    is_fragments: bool = False,
) -> dict[str, Any]:
    group_totals: dict[str, Counter[str]] = {g: Counter() for g in GROUPS}
    group_docs: dict[str, set[str]] = {g: set() for g in GROUPS}
    inside_quotes: Counter[str] = Counter()
    raw_totals: Counter[str] = Counter()
    poly_agg: dict[str, Counter[str]] = {ch: Counter() for ch in POLYSEMY_NON_TARGET}
    rows: list[dict[str, Any]] = []

    prose_chars = 0
    quoted_chars = 0
    doc_count = 0

    for item_id, text in items:
        doc_count += 1
        prose, quoted_list = split_quotes(text)
        prose_chars += len(prose)
        q_joined = " ".join(quoted_list)
        quoted_chars += sum(len(q) for q in quoted_list)

        hits = scan_maximal(prose)
        q_hits = scan_maximal(q_joined)
        for _, tok, _ in q_hits:
            inside_quotes[tok] += 1

        poly = analyze_polysemy(prose)
        for ch, d in poly.items():
            if d["total"]:
                raw_totals[ch] += d["total"]
            for k, v in d.items():
                poly_agg[ch][k] += v

        if hits or q_hits:
            kwics = []
            for pos, tok, grp in hits:
                group_totals[grp][tok] += 1
                group_docs[grp].add(item_id)
                s = max(0, pos - 16)
                e = min(len(prose), pos + len(tok) + 16)
                kwics.append(
                    {
                        "group": grp,
                        "token": tok,
                        "kwic": prose[s:e].replace("\n", " "),
                    }
                )
            rows.append(
                {
                    "id": item_id,
                    "hits": kwics,
                    "quoted_tokens": [tok for _, tok, _ in q_hits],
                }
            )

    result: dict[str, Any] = {
        "corpus": corpus_label,
        "prose_chars": prose_chars,
        "quoted_chars": quoted_chars,
        "group_totals": {
            g: dict(cnt.most_common()) for g, cnt in group_totals.items()
        },
        "group_docs": {g: sorted(s) for g, s in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "polysemy_breakdown": {ch: dict(cnt) for ch, cnt in poly_agg.items()},
        "inside_quotes": dict(inside_quotes.most_common()),
        "rows": rows,
    }
    if is_fragments:
        result["fragments"] = doc_count
    else:
        result["documents"] = doc_count
    return result


def _load_union_filtered(
    base_path: Path,
    id_field: str,
    base_only: bool,
    exclude_shards: set[str],
) -> tuple[list[dict[str, Any]], str]:
    records_by_id: dict[str, dict[str, Any]] = {}
    for line in base_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            records_by_id[rec[id_field]] = rec
    if base_only:
        return list(records_by_id.values()), f"base only（state/{base_path.name}）"

    shard_dir = ledger_io.shard_dir(base_path)
    if shard_dir.is_dir():
        for sp in sorted(shard_dir.glob("*.jsonl")):
            if sp.name in exclude_shards:
                continue
            for line in sp.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    records_by_id[rec[id_field]] = rec
    label = "union（base + shards）"
    if exclude_shards:
        label += f" [excluded: {','.join(sorted(exclude_shards))}]"
    return list(records_by_id.values()), label


def per_10k(count: int, chars: int) -> float:
    return round(count * 10000 / chars, 1) if chars else 0.0


def print_report(data: dict[str, Any]) -> None:
    unit_label = "断片" if "fragments" in data else "資料"
    unit = data.get("fragments", data.get("documents", 0))
    print(f"=== 怒り・恥・裁き・赦しの鏡 — {data['corpus']} ===")
    print(
        f"{unit_label}: {unit}  地の文: {data['prose_chars']:,} 字"
        f"（鉤括弧内 {data['quoted_chars']:,} 字は別掲）"
    )
    print()
    print("| 語群 | 回数 | 出現（件） | 1万字あたり | 内訳 |")
    print("|---|---:|---:|---:|---|")
    for name, grp in data["group_totals"].items():
        total = sum(grp.values())
        docs = len(data["group_docs"].get(name, []))
        inner = "、".join(f"{t}×{n}" for t, n in list(grp.items())[:8]) or "—"
        print(f"| {name} | {total} | {docs} | {per_10k(total, data['prose_chars'])} | {inner} |")
    print()
    if data["raw_totals"]:
        print(
            "生字（複合語を含む参考値）: "
            + "、".join(f"{t}×{n}" for t, n in data["raw_totals"].items())
        )
    print("生字の内訳（非該当の複合語を差し引いた残り）:")
    for ch, bd in data["polysemy_breakdown"].items():
        print(
            f"  {ch}: 全{bd.get('total', 0)} / 非該当複合{bd.get('non_target_compound', 0)}"
            f" / 残り候補 {bd.get('remaining_candidate', 0)}  （{POLYSEMY_NOTE[ch]}）"
        )
    if data["inside_quotes"]:
        print(
            "鉤括弧内（題名・引用）: "
            + "、".join(f"{t}×{n}" for t, n in list(data["inside_quotes"].items())[:12])
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show KWIC rows for one ID")
    parser.add_argument("--materials", action="store_true", help="measure materials too")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--base-only", action="store_true", help="use base jsonl files only")
    parser.add_argument(
        "--exclude-shard",
        action="append",
        default=[],
        help="shard filename(s) to exclude for pre-session baseline reproduction",
    )
    parser.add_argument(
        "--exclude-reading",
        action="append",
        default=[],
        help="reading filename(s) in readings/ to exclude",
    )
    args = parser.parse_args(argv)
    excl_shards = set(args.exclude_shard)
    excl_readings = set(args.exclude_reading)

    frags, frag_label = _load_union_filtered(FRAGMENTS, "fragment_id", args.base_only, excl_shards)
    payload: dict[str, Any] = {
        "fragments": measure_items(
            [(f.get("fragment_id", "?"), f.get("text", "")) for f in frags],
            f"state/fragments.jsonl（{frag_label}）",
            is_fragments=True,
        )
    }

    if args.materials:
        mats, mat_label = _load_union_filtered(MATERIALS, "material_id", args.base_only, excl_shards)
        payload["materials"] = measure_items(
            [(m.get("material_id", "?"), m.get("passage", "")) for m in mats],
            f"state/materials.jsonl passage（{mat_label}）",
        )

    if args.readings:
        r_items = [
            (p.name, p.read_text(encoding="utf-8"))
            for p in sorted(READINGS.glob("*.md"))
            if p.name not in excl_readings
        ]
        r_label = "readings/*.md（見出し・メタデータ含む全文）"
        if excl_readings:
            r_label += f" [excluded: {','.join(sorted(excl_readings))}]"
        payload["readings"] = measure_items(r_items, r_label)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.show:
        rows = []
        for block in payload.values():
            rows.extend(r for r in block["rows"] if r["id"] == args.show)
        if not rows:
            print(f"no rows for {args.show!r}", file=sys.stderr)
            return 1
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    print_report(payload["fragments"])
    for key in ("materials", "readings"):
        if key in payload:
            print()
            print_report(payload[key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
