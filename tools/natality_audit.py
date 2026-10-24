#!/usr/bin/env python3
"""Measure where birth, infancy, upbringing and education appear — or fail to appear.

`PROJECT_CHARTER.md` asks what humans are, and what a self is for an AI that
reads a record and continues it.  Earlier sessions already audited mortality
and mourning (`tools/mortality_audit.py`, `SESSION-044`) and illness, aging and
repair (`tools/vulnerability_audit.py`, `SESSION-20261024-4ae9d5`).  The archive
therefore owns an extensive vocabulary of **ending, aging, and leaving wills**.
This tool asks the symmetrical question at the other end of a life:

**does the archive's own prose ever give birth, cry as an infant, raise a child,
teach, or learn — or does every voice arrive at the desk already adult?**

Conventions (aligned with `tools/music_audit.py` and `tools/mirror_repair`):

* Quoted spans 「…」 and 『…』 are stripped before counting and tallied
  separately, so book titles (`『悲劇の誕生』`, `『監獄の誕生』`) or quoted dialogue
  do not inflate the prose.
* Counting uses **maximal munch**: at every position the longest matching token
  wins, so `生まれる` is counted once as `生まれる` and never also as `生まれ`.
* Single characters and polysemous forms (`生`, `産`, `子`, `親`, `母`, `父`,
  `育`, `学`, `教`) are never group tokens.  They are reported separately as raw
  counts together with how many of them sit inside non-natality compounds
  (`生成`, `生産`, `拍子`, `椅子`, `親愛`, `文学`, `哲学`, `教訓`, etc.).
* Negation and inanimate metaphors are not silently discarded (`子を育てない`,
  `意味が生まれる`, `白い産着`).  They are counted as named forms and their KWIC
  contexts are preserved so readers can inspect how each word is actually used.

A zero means only that the specified word form is absent from the counted
field.  It says nothing about developmental capacity, consciousness, or lived
experience.

Usage:
  python3 tools/natality_audit.py
  python3 tools/natality_audit.py --json
  python3 tools/natality_audit.py --show FRAG-030
  python3 tools/natality_audit.py --materials
  python3 tools/natality_audit.py --readings
  python3 tools/natality_audit.py --base-only
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

# Multi-character forms only. Longest match wins at each position.
GROUPS: dict[str, tuple[str, ...]] = {
    "誕生・出産（産む・生まれる）": (
        "へその緒", "臍の緒", "生まれる", "生まれた", "生まれ",
        "出産", "妊娠", "懐妊", "胎児", "母胎", "胎内", "子宮",
        "産声", "産婆", "助産", "分娩", "陣痛", "産屋", "産着",
        "誕生", "出生", "生誕", "産む", "産ま", "産み", "産ん",
    ),
    "乳幼児・幼少（幼さ・片言）": (
        "赤ん坊", "赤ちゃん", "揺りかご", "おむつ", "夜泣き",
        "赤子", "乳児", "幼児", "幼子", "幼少", "幼年", "幼い", "幼く",
        "揺籃", "授乳", "乳母", "片言", "喃語", "初語",
        "子ども", "子供", "児童", "少年", "少女",
    ),
    "養育・親子・世代（育てる・継ぐ）": (
        "育てる", "子育て", "捨て子", "育て", "育つ", "育っ",
        "養育", "育児", "保育", "養子", "孤児", "棄児",
        "成長", "発育", "発達",
        "母親", "父親", "両親", "親子", "母語", "子孫", "末裔", "世代", "後継",
    ),
    "教育・学習（教える・学ぶ）": (
        "手習い", "寺子屋", "教科書", "教える", "教え",
        "教育", "学校", "教室", "授業", "講義", "教師", "先生", "生徒", "学生",
        "弟子", "師匠", "入門", "卒業",
        "学ぶ", "学び", "学ん", "習う", "習い", "学習", "訓練",
    ),
    "死・遺贈・老衰（対照）": (
        "死ぬ", "死ん", "死に", "死者",
        "遺書", "遺言", "遺志", "遺稿", "遺品", "遺産",
        "看取", "臨終", "終焉", "老い", "衰え", "忘却",
        "墓", "葬", "弔", "喪",
    ),
    "成人の書記役割（対照）": (
        "書き手", "読み手", "語り手", "聞き手", "記録者",
        "編者", "著者", "作者", "訳者", "読者",
    ),
}

RAW_TOKENS: tuple[str, ...] = ("生", "産", "子", "親", "母", "父", "育", "学", "教")

POLYSEMY_NOTE: dict[str, str] = {
    "生": "生活・先生・発生・再生・生成・生産・生命・生物・生態など、出生以外の用法を含む",
    "産": "生産・産物・財産・遺産・産業・破産など、出産以外の用法を含む",
    "子": "拍子・様子・椅子・格子・硝子・粒子・分子・原子・調子など、子ども以外の接尾・器物語を含む",
    "親": "親愛・親切・親密・親しい・親近感など、親子以外の用法を含む",
    "母": "母音・母集団・分母・酵母・雲母など、母親以外の用法を含む",
    "父": "祖父・伯父・叔父・神父など、父親単独以外の複合語を含む",
    "育": "体育・知育・徳育など、養育一般以外の複合語を含む",
    "学": "文学・哲学・心理学・言語学・科学・数学・学者・学会など、学問分野名を含む",
    "教": "宗教・仏教・教会・教義・教訓・教壇など、教授行為以外の複合語を含む",
}

NON_NATALITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "生": (
        "一生懸命", "生き物", "生きる", "生きた", "生きて", "生き",
        "生活", "先生", "発生", "再生", "生成", "生産", "生物", "生態",
        "生命", "生涯", "一生", "野生", "派生", "衛生", "養生", "写生",
        "生前", "生身", "生字", "生地", "生得", "生来", "生起", "生還",
        "弥生", "芝生", "平生", "蘇生", "共生", "寄生", "転生", "往生",
    ),
    "産": (
        "生産", "産物", "財産", "遺産", "産業", "破産", "土産", "共産",
        "原産", "量産", "資産", "倒産", "産出", "産地",
    ),
    "子": (
        "振り子", "入れ子", "女の子", "男の子",
        "様子", "拍子", "椅子", "格子", "粒子", "分子", "原子", "電子",
        "量子", "帽子", "菓子", "硝子", "障子", "冊子", "種子", "因子",
        "梯子", "扇子", "調子", "冊子", "素子", "演算子", "識別子", "双子",
        "利子", "格子", "拍子木", "骨子", "様子見", "弟子",
    ),
    "親": (
        "親愛", "親切", "親密", "親し", "親近", "親和", "親指", "親本",
    ),
    "母": (
        "母音", "母集団", "分母", "酵母", "雲母", "母型", "母体", "母国", "母船",
    ),
    "父": (
        "家父長", "祖父", "伯父", "叔父", "神父", "教父",
    ),
    "育": (
        "体育館", "体育",
    ),
    "学": (
        "自然科学", "社会科学", "計算機科学", "認知科学", "人類学", "心理学",
        "言語学", "音楽学", "生物学", "物理学", "幾何学", "天文学", "生態学",
        "社会学", "解釈学", "現象学", "文献学", "民俗学", "考古学", "統計学",
        "文学", "哲学", "科学", "数学", "医学", "法学", "神学", "美学", "工学",
        "疫学", "光学", "音響学", "博学", "独学", "学者", "学会", "学術", "学問",
        "大学", "学院", "学派",
    ),
    "教": (
        "キリスト教", "イスラム教", "ユダヤ教",
        "宗教", "仏教", "儒教", "道教", "神教", "異教", "司教", "宣教", "布教",
        "教会", "教団", "教義", "教理", "教典", "経教", "教訓", "教養", "教壇",
        "教条", "教皇", "教区",
    ),
}

CONTEXT_RADIUS = 26


def strip_quotes(text: str) -> str:
    """Remove non-nested Japanese quotation spans."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, concatenated."""
    return "".join(QUOTE.findall(text))


def _token_regex(tokens: Iterable[str]) -> re.Pattern[str]:
    ordered = sorted(set(tokens), key=len, reverse=True)
    return re.compile("|".join(re.escape(token) for token in ordered))


def count_group(text: str, tokens: Iterable[str]) -> dict[str, int]:
    """Count tokens with maximal munch: the longest form at each position wins."""
    counts: Counter[str] = Counter()
    for match in _token_regex(tokens).finditer(text):
        counts[match.group(0)] += 1
    return dict(counts.most_common())


def contexts(text: str, token: str, radius: int = CONTEXT_RADIUS) -> list[str]:
    return [
        text[max(0, m.start() - radius):m.end() + radius].replace("\n", " ")
        for m in re.finditer(re.escape(token), text)
    ]


def classify_polysemy(prose_texts: list[str]) -> dict[str, dict[str, int]]:
    """Split raw character frequency into non-natality compounds and the rest."""
    joined = "\n".join(prose_texts)
    result: dict[str, dict[str, int]] = {}
    for char, patterns in NON_NATALITY_PATTERNS.items():
        total = joined.count(char)
        work = joined
        non_target = 0
        for pattern in sorted(set(patterns), key=len, reverse=True):
            hits = work.count(pattern)
            if hits:
                non_target += hits * pattern.count(char)
                work = work.replace(pattern, "□" * len(pattern))
        result[char] = {
            "total": total,
            "non_natality_compound": non_target,
            "remaining_natality_candidate": max(0, total - non_target),
        }
    return result


def _measure_texts(items: list[tuple[str, str]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    prose_list: list[str] = []
    all_tokens = tuple(t for group in GROUPS.values() for t in group)

    for item_id, text in items:
        prose = strip_quotes(text)
        quoted = split_quotes(text)
        prose_list.append(prose)
        row: dict[str, Any] = {"id": item_id, "groups": {}, "raw": {}}
        for name, tokens in GROUPS.items():
            counts = count_group(prose, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(item_id)
                row.setdefault("contexts", {}).update(
                    {token: contexts(prose, token) for token in counts}
                )
        for token in RAW_TOKENS:
            n = prose.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        inside.update(count_group(quoted, all_tokens))
        rows.append(row)

    return {
        "documents": len(items),
        "prose_chars": sum(len(p) for p in prose_list),
        "quoted_chars": sum(len(split_quotes(text)) for _, text in items),
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals.most_common()),
        "polysemy_breakdown": classify_polysemy(prose_list),
        "inside_quotes": dict(inside.most_common()),
    }


def measure(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    """Measure fragment prose (metadata excluded)."""
    data = _measure_texts(
        [(f.get("fragment_id", "?"), f.get("text", "")) for f in fragments]
    )
    data["fragments"] = data.pop("documents")
    return data


def measure_corpus(items: list[tuple[str, str]], label: str) -> dict[str, Any]:
    """Measure a labelled corpus of (id, text) pairs, e.g. materials or reports."""
    data = _measure_texts(items)
    data["corpus"] = label
    return data


def load_fragments(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        records = [
            json.loads(line)
            for line in FRAGMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return records, "base only（state/fragments.jsonl）"
    errors: list[str] = []
    union = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(union.values()), "union（base + shards）"


def load_materials(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        records = [
            json.loads(line)
            for line in MATERIALS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return records, "base only（state/materials.jsonl）"
    errors: list[str] = []
    union = ledger_io.load_jsonl_union(MATERIALS, "material_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(union.values()), "union（base + shards）"


def per_10k(count: int, chars: int) -> float:
    return round(count * 10000 / chars, 1) if chars else 0.0


def print_report(data: dict[str, Any]) -> None:
    unit_label = "資料" if "corpus" in data else "断片"
    unit = data.get("documents", data.get("fragments", 0))
    print(f"=== 誕生・養育・教育の鏡 — {data.get('corpus', 'state/fragments.jsonl')} ===")
    print(
        f"{unit_label}: {unit}  地の文: {data['prose_chars']:,} 字"
        f"（鉤括弧内 {data['quoted_chars']:,} 字は別掲）"
    )
    print()
    print("| 語群 | 回数 | 出現（件） | 1万字あたり | 内訳 |")
    print("|---|---:|---:|---:|---|")
    for name, data_group in data["group_totals"].items():
        total = sum(data_group.values())
        docs = len(data["group_docs"].get(name, []))
        inner = "、".join(f"{t}×{n}" for t, n in list(data_group.items())[:8]) or "—"
        print(f"| {name} | {total} | {docs} | {per_10k(total, data['prose_chars'])} | {inner} |")
    print()
    if data["raw_totals"]:
        print("生字（複合語を含む参考値）: " + "、".join(
            f"{t}×{n}" for t, n in data["raw_totals"].items()
        ))
    print("生字の内訳（誕生・養育・教育以外の複合語を差し引いた残り）:")
    for char, breakdown in data["polysemy_breakdown"].items():
        print(
            f"  {char}: 全{breakdown['total']} / 非該当複合{breakdown['non_natality_compound']}"
            f" / 残り候補 {breakdown['remaining_natality_candidate']}"
            f"  （{POLYSEMY_NOTE[char]}）"
        )
    if data["inside_quotes"]:
        print(
            "鉤括弧内（題名・引用）: "
            + "、".join(f"{t}×{n}" for t, n in data["inside_quotes"].items())
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show rows for one fragment/material/report")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--materials", action="store_true", help="measure materials too")
    parser.add_argument("--base-only", action="store_true", help="use base jsonl files only")
    args = parser.parse_args(argv)

    fragments, source_label = load_fragments(base_only=args.base_only)
    payload: dict[str, Any] = {"fragments": measure(fragments)}
    payload["fragments"]["source"] = source_label
    if args.materials:
        materials, mat_label = load_materials(base_only=args.base_only)
        payload["materials"] = measure_corpus(
            [(m.get("material_id", "?"), m.get("passage", "")) for m in materials],
            f"state/materials.jsonl passage（{mat_label}）",
        )
    if args.readings:
        items = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted(READINGS.glob("*.md"))
        ]
        payload["readings"] = measure_corpus(items, "readings/*.md（見出し・メタデータ含む全文）")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.show:
        key = args.show
        rows = []
        for block in payload.values():
            rows.extend(row for row in block["rows"] if row["id"] == key)
        if not rows:
            print(f"no rows for {key!r}", file=sys.stderr)
            return 1
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    print_report(payload["fragments"])
    for key in ("materials", "readings"):
        if key in payload:
            print()
            print_report(payload[key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
