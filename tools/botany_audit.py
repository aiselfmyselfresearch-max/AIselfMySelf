#!/usr/bin/env python3
"""botany_audit.py — 植物・樹木・種子・根・花の語彙と「書記・計算への吸収」を測る鏡（第53の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、

  1. 草木・花葉・器官（flora_organ——植物・樹木・草木・街路樹・花びら・新芽・年輪・種子等）
  2. 種を蒔く・根を張る・枯れ枝（root_and_seed——播種・発芽・根を張る・結実・枯れ枝・小枝等）
  3. 耕す・植える・接ぐ・刈る（cultivation——栽培・耕す・接ぎ木・剪定・刈り取る・輪作・収穫等）
  4. 森林・菌糸・光合成（forest_and_mycelium——森林・森を・菌糸・菌根・粘菌・腐った茸・光合成等）
  5. 木材・木枠・積み木・標本（timber_and_relic——木材・木枠・積み木・木箱・添え木・木片・押し花・紙漉等）
  6. 書記と論理に吸われた植物字（scribal_absorption——**モチーフに束ねない対照群**。言葉・草稿・草子・花押・種類・根拠・屋根・煙草等）
  7. 計算と台帳の植物比喩（tree_and_graph——状態の木・探索木・決定木・系統樹・系譜ツリー・問いの枝・枝葉・シード・ブランチ・枝刈り等）

がどこに集まり、どこに現れないかを、最長一致＋非該当複合語の差し引きで数える。
あわせて断片の地の文における生字9字「葉・草・種・根・花・枝・木・森・林」の KWIC と、
各生字が「書記・論理・木工・計算比喩・固有名」にどれだけ吸収され、生きた植物や
実物の花・種子・根として何回残るかの差し引き内訳（`raw_kanji_breakdown`）を出す。

なぜ単漢字「葉・草・種・根・花・枝・木」をそのまま植物群に入れないのか
----------------------------------------------------------------------
日本語では植物の器官を表す漢字が、そのまま書記・分類・建築・計算の基礎語彙に
転用されている。実際に収蔵前の断片95編（地の文45,222字）を剥がすと、
  - 「葉」32回のうち30回は「言葉（28）・合言葉（1）・合い言葉（1）」、1回は「枝葉」
  - 「草」9回のうち8回は「草稿（4）・草子（2）・煙草（2）」
  - 「種」6回はすべて「種類（2）・一種（1）・百七十二種（1）・種明かし（1）・火種（1）」
  - 「根」4回はすべて「屋根（2）・根拠（1）・（時計の針が）根元から（1）」
  - 「花」4回は「世阿弥の芸の花（2）・花押（1）・蜜蝋から失われた花の香り（1）」
  - 「枝」12回のうち8回は「問いの枝・探索の枝・怒りの枝・枝葉」、残り4回は瓶詰・塩漬けの枯れ枝
  - 「木」18回のうち15回は「状態の木（2）」と木工品（積み木4・木枠2・木材1・横木1・木箱1・添え木1・木の塊1・沈水木片1・木片1）、2回は「啄木」「木曜」
であった。単漢字をそのまま植物群に入れると、「言葉」が葉に、「草稿」が草に、「種類」が種子に、
「根拠」が根に化ける。そのため本鏡では、複合語を7群に分けたうえで、生字9字については
非植物複合語を差し引いた「残余（net_botanical）」を別枠で検算する。

差し引きの設計
--------------
- 「言葉」から「合言葉」「合い言葉」を引く（どちらも scribal_absorption 群内で一度だけ数える）。
- 「木片」から「沈水木片」を引く（「沈水木」と「木片」が同一箇所で二重計上されるのを防ぐ）。
- 「シード」から「初期シード」を引く（tree_and_graph 群内で一度だけ数える）。
- 「枯れ枝」「小枝」は root_and_seed 群に置き、timber_and_relic 群と重複させない。
- `scribal_absorption` 群は `motif_bound: False` とし、植物モチーフそのものには束ねない。

数えるのは語形であって、自然への関心・季節感・主観的経験の有無の判定ではない。
「0」は、その語形がその集合に現れなかったことだけを意味する。

使い方::

    python3 tools/botany_audit.py
    python3 tools/botany_audit.py --kwic
    python3 tools/botany_audit.py --json
    python3 tools/botany_audit.py --base-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402

QUOTE_RE = re.compile(r"「[^」]*」|『[^』]*』")

BOTANY_GROUPS: dict[str, dict[str, Any]] = {
    "flora_organ": {
        "label": "草木・花葉・器官",
        "terms": (
            "植物",
            "樹木",
            "草木",
            "街路樹",
            "野草",
            "雑草",
            "花びら",
            "開花",
            "落花",
            "つぼみ",
            "新芽",
            "若葉",
            "青葉",
            "紅葉",
            "落葉",
            "枯れ葉",
            "樹皮",
            "年輪",
            "球根",
            "地下茎",
            "花粉",
            "花弁",
            "果実",
            "木の実",
            "種子",
            "蘚苔",
            "羊歯",
            "シダ",
        ),
        "note": "単漢字「花・草・葉・木」は多義のためここに入れず、生字分解で別に検算する。",
        "motif_bound": True,
    },
    "root_and_seed": {
        "label": "種を蒔く・根を張る・枯れ枝",
        "terms": (
            "種を蒔",
            "種まき",
            "播種",
            "発芽",
            "芽吹",
            "芽を出",
            "根を張",
            "根づ",
            "根付",
            "根ざ",
            "根差",
            "根こそぎ",
            "根絶",
            "宿根",
            "発根",
            "実を結",
            "結実",
            "実り",
            "実る",
            "枯れ枝",
            "枯れ木",
            "小枝",
        ),
        "note": "発生・定着の句と、枯死した枝。「枯れ枝」「小枝」はここで一度だけ数える。",
        "motif_bound": True,
    },
    "cultivation": {
        "label": "耕す・植える・接ぐ・刈る",
        "terms": (
            "栽培",
            "耕す",
            "耕し",
            "農耕",
            "苗床",
            "温室",
            "植物園",
            "庭園",
            "花壇",
            "鉢植",
            "盆栽",
            "接ぎ木",
            "挿し木",
            "剪定",
            "刈り取",
            "摘み取",
            "収穫",
            "輪作",
            "休閑",
            "肥料",
            "堆肥",
            "水やり",
            "灌漑",
            "除草",
        ),
        "note": "農耕・園芸・管理の語。「刈り取」は辞書の枝の比喩にも使われる。",
        "motif_bound": True,
    },
    "forest_and_mycelium": {
        "label": "森林・菌糸・光合成",
        "terms": (
            "森林",
            "原生林",
            "雑木林",
            "竹林",
            "松林",
            "林間",
            "森の",
            "森を",
            "森に",
            "森へ",
            "菌糸",
            "菌根",
            "粘菌",
            "きのこ",
            "腐った茸",
            "地衣",
            "腐葉土",
            "光合成",
            "蒸散",
            "受粉",
        ),
        "note": "群落と地下網・菌類・植物生理。「星の林」は天体の比喩のため含めない。",
        "motif_bound": True,
    },
    "timber_and_relic": {
        "label": "木材・木枠・積み木・標本",
        "terms": (
            "木材",
            "木枠",
            "積み木",
            "横木",
            "木箱",
            "添え木",
            "木の塊",
            "木片",
            "押し花",
            "腊葉",
            "植物標本",
            "木簡",
            "紙漉",
        ),
        "note": "伐採・加工された木工品、香木片（沈水木片を含む）、乾燥標本、植物繊維の紙漉き。",
        "motif_bound": True,
    },
    "scribal_absorption": {
        "label": "書記・論理に吸われた植物字（対照・束ねない）",
        "terms": (
            "言葉",
            "合言葉",
            "合い言葉",
            "草稿",
            "草子",
            "花押",
            "種類",
            "一種",
            "種明かし",
            "火種",
            "根拠",
            "屋根",
            "根元",
            "煙草",
        ),
        "note": "植物の字を含むが書記・分類・建築・嗜好品を表す対照群。モチーフには束ねない。",
        "motif_bound": False,
    },
    "tree_and_graph": {
        "label": "計算と台帳の植物比喩",
        "terms": (
            "状態の木",
            "探索木",
            "決定木",
            "構文木",
            "系統樹",
            "系譜ツリー",
            "問いの枝",
            "怒りの枝",
            "閉じられた枝",
            "枝葉",
            "初期シード",
            "シード",
            "ブランチ",
            "プルーニング",
            "枝刈り",
        ),
        "note": "計算機科学・Git・本台帳の自己記述における木・枝・種・剪定。",
        "motif_bound": True,
    },
}

EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "言葉": ("合言葉", "合い言葉"),
    "合言葉": (),
    "合い言葉": (),
    "シード": ("初期シード",),
    "初期シード": (),
    "植物": ("植物園", "植物標本"),
    "落花": ("落花生",),
}

RAW_KANJI: dict[str, str] = {
    "葉": "言葉・合言葉・枝葉を含む。植物の葉の回数ではない",
    "草": "草稿・草子・煙草を含む。野草の回数ではない",
    "種": "種類・一種・種明かし・火種を含む。種子の回数ではない",
    "根": "屋根・根拠・時計の針の根元を含む。植物の根の回数ではない",
    "花": "花押・世阿弥の芸の花を含む。実物の花の回数ではない",
    "枝": "問いの枝・探索の枝・枝葉・枯れ枝を含む",
    "木": "状態の木・積み木・木枠・木材・啄木・木曜を含む",
    "森": "森・森林・固有名を含む",
    "林": "林・竹林・星の林を含む",
}

# 生字から「非植物（書記・分類・建築・木工・計算比喩・固有名・曜日）」を差し引くための語表
NON_LIVING_COMPOUNDS_BY_KANJI: dict[str, tuple[str, ...]] = {
    "葉": ("言葉", "合言葉", "合い言葉", "枝葉", "万葉", "千葉", "言葉遣い"),
    "草": ("草稿", "草子", "煙草", "仕草", "道草"),
    "種": ("種類", "一種", "二種", "三種", "四種", "五種", "六種", "七種", "八種", "十種", "百七十二種", "種明かし", "火種", "変種", "人種", "職種", "業種", "種別", "各種"),
    "根": ("屋根", "根拠", "根元", "根底", "根本", "根気", "根性", "羽根", "垣根"),
    "花": ("花押", "花火", "火花", "花形", "花道"),
    "枝": ("問いの枝", "怒りの枝", "閉じられた枝", "枝葉", "どの枝", "七の枝"),
    "木": ("状態の木", "探索木", "決定木", "構文木", "積み木", "木枠", "木材", "横木", "木箱", "添え木", "木の塊", "沈水木片", "木片", "木簡", "啄木", "木曜", "拍子木", "版木"),
    "森": (),
    "林": ("星の林",),
}


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Split a fragment into (outside quotes, inside quotes)."""
    quoted = QUOTE_RE.findall(text)
    prose = QUOTE_RE.sub("", text)
    inner = "".join(piece[1:-1] for piece in quoted)
    return prose, inner


def count_term(text: str, term: str) -> int:
    """Count ``term`` after subtracting longer forms listed in EXCLUSIONS."""
    if term not in text:
        return 0
    count = text.count(term)
    for longer in EXCLUSIONS.get(term, ()):
        count -= text.count(longer)
    return max(count, 0)


def scan_text(text: str) -> dict[str, int]:
    """Return the per-term counts of every group that occurs in ``text``."""
    hits: dict[str, int] = {}
    for group in BOTANY_GROUPS.values():
        for term in group["terms"]:
            n = count_term(text, term)
            if n:
                hits[term] = n
    return hits


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    groups: dict[str, Any] = {
        key: {
            "label": spec["label"],
            "note": spec["note"],
            "motif_bound": spec["motif_bound"],
            "count": 0,
            "doc_count": 0,
            "terms": {},
        }
        for key, spec in BOTANY_GROUPS.items()
    }
    char_total = 0
    for _doc_id, text in docs:
        char_total += len(text)
        for key, spec in BOTANY_GROUPS.items():
            group_hits = 0
            for term in spec["terms"]:
                n = count_term(text, term)
                if n:
                    groups[key]["terms"][term] = groups[key]["terms"].get(term, 0) + n
                    group_hits += n
            if group_hits:
                groups[key]["count"] += group_hits
                groups[key]["doc_count"] += 1
    for key in groups:
        groups[key]["terms"] = dict(sorted(groups[key]["terms"].items()))
    return {"doc_total": len(docs), "char_total": char_total, "groups": groups}


def _snippet(text: str, index: int, width: int = 22) -> str:
    low = max(0, index - width)
    high = min(len(text), index + width + 1)
    return text[low:high].replace("\n", " ")


def inspect_raw_kanji_in_fragments(
    fragments: list[dict[str, Any]], width: int = 22
) -> dict[str, list[dict[str, str]]]:
    """Return KWIC rows for each raw kanji, from fragment prose only."""
    rows: dict[str, list[dict[str, str]]] = {ch: [] for ch in RAW_KANJI}
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, _quoted = split_prose_and_quotes(str(frag.get("text", "")))
        for ch in RAW_KANJI:
            start = 0
            while True:
                index = prose.find(ch, start)
                if index < 0:
                    break
                rows[ch].append({"fragment_id": fid, "snippet": _snippet(prose, index, width)})
                start = index + len(ch)
    return rows


def inspect_raw_kanji_breakdown(fragments: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Break down each raw kanji in fragment prose into non-botanical compounds vs residual occurrences."""
    prose_all = "\n".join(
        split_prose_and_quotes(str(frag.get("text", "")))[0] for frag in fragments
    )
    breakdown: dict[str, dict[str, Any]] = {}
    for ch in RAW_KANJI:
        total = prose_all.count(ch)
        compounds = NON_LIVING_COMPOUNDS_BY_KANJI.get(ch, ())
        # Sort longest first so e.g. 合言葉 doesn't double-subtract with 言葉
        ordered = sorted(compounds, key=lambda s: (-len(s), s))
        scrubbed = prose_all
        absorbed_detail: dict[str, int] = {}
        absorbed_total = 0
        for comp in ordered:
            c = scrubbed.count(comp)
            if c > 0:
                ch_in_comp = comp.count(ch) * c
                absorbed_detail[comp] = ch_in_comp
                absorbed_total += ch_in_comp
                scrubbed = scrubbed.replace(comp, "□" * len(comp))
        residual = scrubbed.count(ch)
        breakdown[ch] = {
            "raw_total": total,
            "absorbed_count": absorbed_total,
            "absorbed_by": absorbed_detail,
            "residual_count": residual,
        }
    return breakdown


def measure_botany_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure botanical, arboreal, and scribal-absorption vocabulary across the archive."""
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
    material_docs: list[tuple[str, str]] = []
    for mat in materials or []:
        mid = str(mat.get("material_id", ""))
        blob = " ".join(
            [
                str(mat.get("title", "")),
                str(mat.get("passage", "")),
                str(mat.get("source_note", "")),
            ]
        )
        material_docs.append((mid, blob))
    if readings is None:
        readings = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "readings").glob("*.md"))
        ]
    kwic = inspect_raw_kanji_in_fragments(fragments)
    breakdown = inspect_raw_kanji_breakdown(fragments)
    prose_summary = _aggregate_docs(prose_docs)
    return {
        "fragment_count": len(fragments),
        "fragments_prose": prose_summary,
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "raw_kanji_breakdown": breakdown,
        "motif_bound_groups": [
            key for key, spec in BOTANY_GROUPS.items() if spec["motif_bound"]
        ],
        "unbound_groups": [
            key for key, spec in BOTANY_GROUPS.items() if not spec["motif_bound"]
        ],
        "group_order": list(BOTANY_GROUPS.keys()),
    }


def _load_union(collection: str, key: str, base_only: bool) -> list[dict[str, Any]]:
    errors: list[str] = []
    path = ROOT / "state" / f"{collection}.jsonl"
    if base_only:
        records = ledger_io.load_jsonl(path, key, errors)
    else:
        records = ledger_io.load_jsonl_union(path, key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return list(records.values())


def _print_human(report: dict[str, Any], kwic: bool) -> None:
    fp = report["fragments_prose"]
    print("=== botany_audit — 植物・樹木・種子・根・花と「書記への吸収」の鏡 ===")
    print()
    print(f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字")
    for key in report["group_order"]:
        info = fp["groups"][key]
        bound = "" if info["motif_bound"] else "（束ねない）"
        detail = "、".join(f"{k}×{v}" for k, v in info["terms"].items()) or "なし"
        print(
            f"                 {info['label']}{bound}: {info['count']} 回 / {info['doc_count']} 編 （{detail}）"
        )
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print("生字の吸収と残余（地の文）:")
    for ch, b in report["raw_kanji_breakdown"].items():
        abs_str = "、".join(f"{k}×{v}" for k, v in b["absorbed_by"].items()) or "なし"
        print(
            f"  「{ch}」総数 {b['raw_total']:>2} → 非植物複合語 {b['absorbed_count']:>2}（{abs_str}） / 残余 {b['residual_count']:>2}"
        )
    qp = report["fragments_quotes"]
    print(f"引用内         : {qp['char_total']:,} 字")
    for key in report["group_order"]:
        info = qp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    mp = report["materials"]
    print(f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字")
    for key in report["group_order"]:
        info = mp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件")
    rp = report["readings"]
    print(f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字")
    for key in report["group_order"]:
        info = rp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本")
    print()
    print("註: 語形の数であり、自然への関心・季節感・主観的経験の有無の判定ではない。")
    if kwic:
        print()
        for ch, rows in report["raw_kanji_kwic"].items():
            print(f"--- 生字「{ch}」{len(rows)} 箇所（{RAW_KANJI[ch]}）---")
            for row in rows[:40]:
                print(f"  {row['fragment_id']}: …{row['snippet']}…")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--kwic", action="store_true")
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args(argv)
    fragments = _load_union("fragments", "fragment_id", args.base_only)
    materials = _load_union("materials", "material_id", args.base_only)
    report = measure_botany_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
