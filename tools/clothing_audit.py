#!/usr/bin/env python3
"""Measure where clothing, cloth, mending and adornment appear — or fail to appear.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it.  Earlier mirrors counted what the archive *sees* and *hears*
(``MAT-TRC-014``, 視覚91・聴覚66・触覚150), what it *sings* (``music_audit``),
what it *smells* (``olfactory_audit``), what it *touches* (``sense_audit``).
This tool asks a narrower question that none of them answered:

**does the archive's own prose ever put clothes on anyone?**

The distinction matters because clothes are the one layer between a body and
the world that is *made* (spun, woven, sewn, washed, mended, discarded) and
*inherited* (worn by someone else first, given, stolen, kept after a death).
A text-only archive can describe a body without contradiction, but a garment
leaves a seam, a stain, a size, a handed-down smell.  The archive records 55
fragments, 1,378 materials and 90 reports; if the word for cloth appears only
inside 分布 and 公布, then the archive owns the *characters* of clothing and
not the *practice* of it.

Conventions (inherited from ``music_audit.py`` and ``olfactory_audit.py``):

* Quoted spans 「…」 and 『…』 are stripped before counting and tallied
  separately, so a quoted title does not inflate the prose.
* Counting uses **maximal munch**: at every position the longest matching token
  wins, so ``着る`` is counted once as ``着る`` and never also as ``着``.
* Single characters and polysemous forms (服 衣 布 装 帯 織 洗 裸) are never
  group tokens.  They are reported as raw counts together with how many of
  them sit inside non-clothing compounds (分布, 公布, 服従, 征服, 装置, 武装,
  帯びる, 洗練, 裸の王様), because in this archive those compounds are the rule
  and the clothing sense is the exception.  ``classify_polysemy`` prints the
  actual contexts so a reader can check the subtraction.
* Negation is not excluded.  ``服は要らない`` counts as one 服.  A word named in
  order to be refused is still a word the archive owns.

A zero means only that the specified word form is absent from the counted
field.  It says nothing about anyone's ability to dress, touch, or feel cloth.

Usage:
  python3 tools/clothing_audit.py
  python3 tools/clothing_audit.py --json
  python3 tools/clothing_audit.py --show FRAG-20261024-036346
  python3 tools/clothing_audit.py --materials
  python3 tools/clothing_audit.py --readings
  python3 tools/clothing_audit.py --base-only
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
CONTEXT_RADIUS = 12

# Longest-first ordering is not required (the regex alternation is sorted by
# length at build time), but readability is.
GROUPS: dict[str, tuple[str, ...]] = {
    "着ること・身につける": (
        "着替え", "着替", "着込", "着飾", "着心地", "着慣",
        "着る", "着て", "着た", "着ている", "着ていた",
        "衣服", "衣類", "衣装", "衣裳", "衣擦れ", "衣替え", "衣紋",
        "洋服", "和服", "着物", "上着", "外套", "コート", "羽織", "産着",
        "袖", "襟", "裾", "ボタン", "ポケット", "帽子", "靴", "手袋",
        "眼鏡", "ヴェール", "ベール", "制服", "晴れ着", "喪服", "装束",
        "白衣", "囚人服", "軍服", "学生服",
    ),
    "布・糸・素材": (
        "布地", "反物", "織物", "織機", "機織", "織り", "織る", "織っ", "織",
        "糸", "針", "縫", "綿", "絹", "麻", "羊毛", "毛糸", "テキスタイル",
        "絨毯", "刺繍", "木綿", "麻布", "麻糸", "敷布",
    ),
    "洗う・繕う・捨てる": (
        "洗濯", "洗う", "洗っ", "洗い", "洗濯物", "繕", "綻", "ほつれ", "ほころび",
        "古着", "古布", "襤褸", "ぼろ", "裸足", "素足", "垢", "汚れ",
    ),
    "装い・身なり・流行": (
        "装い", "装う", "装っ", "扮装", "仮装", "化粧", "身なり", "服装",
        "ファッション", "流行", "おしゃれ", "盛装", "武具",
    ),
}

# Single characters whose clothing sense is usually defeated by a compound.
RAW_TOKENS: tuple[str, ...] = (
    "服", "衣", "布", "装", "帯", "織", "洗", "裸", "縫", "袖", "糸", "着", "脱", "染",
)

POLYSEMY_COMPOUNDS: dict[str, tuple[str, ...]] = {
    "服": ("服従", "征服", "屈服", "服す", "服し", "服さ", "服属", "不服", "克服", "服する"),
    "衣": (),
    "布": ("分布", "公布", "布告", "布石", "遍布", "流布", "布陣", "布置", "布教"),
    "装": ("装置", "装備", "武装", "改装", "装着", "装填", "装丁", "装幀", "パッケージ"),
    "帯": ("帯び", "帯びる", "携帯", "地帯", "温帯", "世帯", "熱帯", "寒帯", "帯状", "時間帯"),
    "織": ("組織", "織り成", "織り交", "織り込"),
    "洗": ("洗練", "洗い出", "洗い直", "洗いざら", "脳洗"),
    "裸": ("裸眼", "赤裸", "裸の王様"),
    "縫": ("縫合",),
    "袖": ("袖振",),
    "糸": ("糸口", "蜘蛛の糸", "糸を引"),
    "着": ("愛着", "着地", "到着", "定着", "執着", "落ち着", "着目", "着色",
           "接着", "着実", "着工", "着信", "着席", "着任", "着順", "初着"),
    "脱": ("脱却", "脱線", "脱出", "逸脱", "超脱", "脱構築", "脱力", "脱皮", "脱退"),
    "染": ("感染", "汚染", "染み", "伝染", "浸染"),
}

POLYSEMY_NOTE: dict[str, str] = {
    "服": "服従・征服・屈服・不服が大半を占めれば、服は従うことであって着るものではない",
    "衣": "衣はほぼ衣擦れ・衣装・衣服として現れる。着る行為ではなく、布の音と分類の語である",
    "布": "分布・流布・公布が大半を占めれば、布は統計と伝播の語であって織物ではない",
    "装": "装置・装備・武装が大半を占めれば、装は機械の語であって身なりの語ではない（装うには偽る意もある）",
    "帯": "帯びる・携帯・地帯が大半を占めれば、帯は付着の語であって装身具ではない",
    "織": "組織・織り込むが大半を占めれば、織は制度と比喩の語であって織機の語ではない",
    "洗": "洗練・洗い出すが大半を占めれば、洗は精錬の比喩であって洗濯ではない",
    "裸": "裸は裸眼・赤裸など複合語でのみ現れる",
    "縫": "縫は縫合（医療）でのみ現れる",
    "袖": "袖は袖振り合う（諺）でのみ現れる",
    "糸": "糸は糸口（手がかり）・蜘蛛の糸（比喩）でのみ現れる",
    "着": "愛着・着地・到着・定着が大半を占めれば、着は到着と執心の語であって着衣ではない",
    "脱": "脱却・脱線・逸脱が大半を占めれば、脱は離脱の語であって脱衣ではない",
    "染": "感染・汚染が大半を占めれば、染は病理の語であって染色ではない",
}

# Tokens that are clothing only when NOT preceded by these characters.
TITLE_PREFIXES = ("",)


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans (nested one level), keeping length stable."""
    out: list[str] = []
    depth = 0
    for ch in text:
        if ch in "「『":
            depth += 1
            out.append("□")
            continue
        if ch in "」』":
            depth = max(0, depth - 1)
            out.append("□")
            continue
        out.append("□" if depth else ch)
    return "".join(out)


def split_quotes(text: str) -> str:
    """Return only the contents of 「…」/『…』 spans."""
    out: list[str] = []
    depth = 0
    for ch in text:
        if ch in "「『":
            depth += 1
            continue
        if ch in "」』":
            depth = max(0, depth - 1)
            continue
        if depth:
            out.append(ch)
    return "".join(out)


def _token_regex(tokens: Iterable[str]) -> re.Pattern[str]:
    ordered = sorted({t for t in tokens if t}, key=len, reverse=True)
    return re.compile("|".join(re.escape(t) for t in ordered))


def count_group(text: str, tokens: Iterable[str]) -> dict[str, int]:
    """Count tokens with maximal munch (no overlapping double counts)."""
    counts: Counter[str] = Counter()
    for match in _token_regex(tokens).finditer(text):
        counts[match.group(0)] += 1
    return dict(counts)


def contexts(text: str, token: str, radius: int = CONTEXT_RADIUS) -> list[str]:
    found = []
    for match in re.finditer(re.escape(token), text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        found.append("…" + text[start:end].replace("\n", " ") + "…")
    return found[:5]


def classify_polysemy(prose_texts: list[str]) -> dict[str, dict[str, Any]]:
    """Split raw character counts into non-clothing compounds and candidates."""
    result: dict[str, dict[str, Any]] = {}
    joined = "\n".join(prose_texts)
    for char, compounds in POLYSEMY_COMPOUNDS.items():
        total = joined.count(char)
        if not compounds:
            result[char] = {
                "total": total,
                "non_clothing_compound": 0,
                "remaining_clothing_candidate": total,
                "compounds": {},
                "note": POLYSEMY_NOTE[char],
            }
            continue
        compound_re = _token_regex(compounds)
        compound_hits: Counter[str] = Counter()
        compound_char_total = 0
        for match in compound_re.finditer(joined):
            compound_hits[match.group(0)] += 1
            compound_char_total += match.group(0).count(char)
        result[char] = {
            "total": total,
            "non_clothing_compound": compound_char_total,
            "remaining_clothing_candidate": max(0, total - compound_char_total),
            "compounds": dict(compound_hits.most_common()),
            "note": POLYSEMY_NOTE[char],
        }
    return result


def _measure_texts(items: list[tuple[str, str]]) -> dict[str, Any]:
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    rows: list[dict[str, Any]] = []
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


def load_readings() -> list[tuple[str, str]]:
    items = []
    for path in sorted(READINGS.glob("*.md")):
        items.append((path.name, path.read_text(encoding="utf-8")))
    return items


def material_text(record: dict[str, Any]) -> str:
    """The summary/conversation fields only: passage, context, note, invitation."""
    parts = [
        record.get("passage", ""),
        record.get("context", ""),
        record.get("source_note", ""),
        record.get("literary_invitation", ""),
        record.get("scope_note", ""),
        record.get("title", ""),
    ]
    return "\n".join(p for p in parts if p)


def per_10k(count: int, chars: int) -> float:
    return round(count * 10000 / chars, 1) if chars else 0.0


def print_report(data: dict[str, Any]) -> None:
    unit_label = "資料" if "corpus" in data else "断片"
    unit = data.get("documents", data.get("fragments", 0))
    print(f"=== 着ることの鏡 — {data.get('corpus', 'state/fragments.jsonl')} ===")
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
    print("生字の内訳（着ること以外の複合語を差し引いた残り）:")
    for char, breakdown in data["polysemy_breakdown"].items():
        if not breakdown["total"]:
            continue
        compounds = "、".join(f"{k}×{v}" for k, v in list(breakdown["compounds"].items())[:5])
        print(
            f"  {char}: 全{breakdown['total']} / 非服飾の複合{breakdown['non_clothing_compound']}"
            f" / 服飾候補 {breakdown['remaining_clothing_candidate']}"
            f"  （{breakdown['note']}）"
        )
        if compounds:
            print(f"     複合の内訳: {compounds}")
    if data["inside_quotes"]:
        print(
            "鉤括弧内（題名・引用）: "
            + "、".join(f"{t}×{n}" for t, n in data["inside_quotes"].items())
        )
    print()


def show_row(data: dict[str, Any], target: str) -> None:
    for row in data["rows"]:
        if row["id"] == target:
            print(json.dumps(row, ensure_ascii=False, indent=2))
            return
    print(f"not found: {target}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    parser.add_argument("--show", metavar="ID", help="show rows for one fragment/material/report")
    parser.add_argument("--readings", action="store_true", help="measure readings/*.md too")
    parser.add_argument("--materials", action="store_true", help="measure materials too")
    parser.add_argument("--base-only", action="store_true", help="use base jsonl files only")
    args = parser.parse_args(argv)

    fragments, frag_label = load_fragments(base_only=args.base_only)
    data = measure(fragments)

    output: dict[str, Any] = {"fragments": data}
    corpora: list[dict[str, Any]] = [data]

    if args.materials:
        materials, mat_label = load_materials(base_only=args.base_only)
        mat_data = measure_corpus(
            [(m.get("material_id", "?"), material_text(m)) for m in materials],
            f"state/materials.jsonl（{mat_label}）",
        )
        output["materials"] = mat_data
        corpora.append(mat_data)

    if args.readings:
        read_data = measure_corpus(load_readings(), "readings/*.md")
        output["readings"] = read_data
        corpora.append(read_data)

    if args.json:
        if args.materials:
            output["materials_label"] = mat_label
        if args.readings:
            output["readings_label"] = read_data["corpus"]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    for corpus in corpora:
        print_report(corpus)

    if args.show:
        for corpus in corpora:
            show_row(corpus, args.show)

    print(f"断片の出所: {frag_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
