#!/usr/bin/env python3
"""abjection_audit.py — 汚れ・排泄・浄化・廃棄・腐敗を測る鏡。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、
  1. 排泄・厠・汲み取り（excretion）
  2. 汚れ・穢れ・不潔（defilement）
  3. 浄め・洗浄・祓い（purification）
  4. 廃棄・屑・捨てる（discard）
  5. 腐敗・死骸・蛆（decay）
  6. 機械の排出・保守・削除（machine_waste）
がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「糞・尿・便・汚・穢・浄・腐・捨・屑」の KWIC を出す。

数えるのは語形であって、汚染の実在・清潔さ・道徳・意識の有無ではない。
「0」は、その語形がその集合に現れなかったことだけを意味する。

使い方::

    python3 tools/abjection_audit.py
    python3 tools/abjection_audit.py --kwic
    python3 tools/abjection_audit.py --json
    python3 tools/abjection_audit.py --base-only
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

ABJECTION_GROUPS: dict[str, dict[str, Any]] = {
    "excretion": {
        "label": "排泄・厠・汲み取り",
        "terms": (
            "糞尿",
            "屎尿",
            "大小便",
            "排便",
            "糞便",
            "排泄",
            "汲み取り",
            "汲取",
            "便所",
            "トイレ",
            "厠",
            "便器",
            "おまる",
            "尿瓶",
            "尿",
            "糞",
            "嘔吐",
            "吐瀉",
            "下痢",
            "おしっこ",
            "うんこ",
            "浄化槽",
        ),
    },
    "defilement": {
        "label": "汚れ・穢れ・不潔",
        "terms": (
            "汚穢",
            "穢れ",
            "穢多",
            "不潔",
            "不浄",
            "汚物",
            "汚辱",
            "汚名",
            "汚職",
            "汚水",
            "汚泥",
            "汚染",
            "汚れ",
            "汚い",
            "垢",
            "染み",
            "泥",
            "埃",
            "塵",
            "黴",
            "カビ",
        ),
    },
    "purification": {
        "label": "浄め・洗浄・祓い",
        "terms": (
            "浄化",
            "浄水",
            "浄不浄",
            "清め",
            "清潔",
            "清掃",
            "掃除",
            "洗浄",
            "洗濯",
            "消毒",
            "殺菌",
            "除菌",
            "滅菌",
            "入浴",
            "沐浴",
            "禊",
            "祓",
            "大祓",
            "潔斎",
            "斎戒",
            "洗い流",
            "水洗",
        ),
    },
    "discard": {
        "label": "廃棄・屑・捨てる",
        "terms": (
            "廃棄物",
            "廃棄",
            "廃物",
            "不用品",
            "ごみ",
            "ゴミ",
            "塵芥",
            "残渣",
            "屑",
            "くず",
            "埋立",
            "焼却",
            "リサイクル",
            "再資源",
            "投棄",
            "捨てる",
            "捨てられ",
            "捨て場",
            "処分場",
            "産廃",
            "し尿処理",
        ),
    },
    "decay": {
        "label": "腐敗・死骸・蛆",
        "terms": (
            "腐敗",
            "腐朽",
            "腐る",
            "腐った",
            "腐れ",
            "朽ちる",
            "朽ち果て",
            "発酵",
            "分解",
            "死骸",
            "屍",
            "骸",
            "蛆",
            "蝿",
            "蠅",
            "悪臭",
            "腐臭",
        ),
    },
    "machine_waste": {
        "label": "機械の排出・保守・削除",
        "terms": (
            "ガベージコレクション",
            "ガベージコレクト",
            "garbage collection",
            "メモリ解放",
            "キャッシュ",
            "ログローテーション",
            "ローテーション",
            "削除",
            "破棄",
            "非推奨",
            "デプリケート",
            "deprecated",
            "__pycache__",
            ".gitignore",
            "gitignore",
            "廃熱",
            "排熱",
            "排水",
            "廃水",
            "電子廃棄物",
            "e-waste",
            "データポイズニング",
        ),
    },
}

# 最長一致で拾った語のうち、この主題として数えない複合語（差し引く）。
EXCLUDE_TERMS: tuple[str, ...] = (
    "不便",
    "便利",
    "便宜",
    "便益",
    "便乗",
    "郵便",
    "便箋",
    "穏便",
    "軽便",
    "至便",
    "両便",
    "便り",
    "便宜上",
    "泥棒",
    "泥沼",
    "泥仕合",
    "雲泥",
    "泥臭",
    "洗練",
    "洗練され",
    "洗いざらい",
    "清少納言",
    "清涼",
    "清朝",
    "浄瑠璃",
    "腐れ縁",
    "腐っても",
    "分解者",
    "分解能",
    "分析",
    "処分",
    "処分は",
    "削除依頼",
    "キャッシュカード",
    "キャッシュレス",
    "回収",
)

RAW_KANJI: tuple[str, ...] = ("糞", "尿", "便", "汚", "穢", "浄", "腐", "捨", "屑")

_SENTINEL = "\u0000"
_TERM_TO_GROUP: dict[str, str] = {}
for _gname, _spec in ABJECTION_GROUPS.items():
    for _t in _spec["terms"]:
        _TERM_TO_GROUP.setdefault(_t, _gname)

_ALL_TERMS = sorted(_TERM_TO_GROUP.keys(), key=len, reverse=True)
_TERM_RE = re.compile("|".join(re.escape(t) for t in _ALL_TERMS))
_EXCLUDE_RE = re.compile(
    "|".join(re.escape(t) for t in sorted(set(EXCLUDE_TERMS), key=len, reverse=True))
)

# 「第四便」「二便」のような便番号（列車・便船・作業バッチの便）は排泄ではない。
EXCLUDE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"第[一二三四五六七八九十百千0-9０-９]+便"),
    re.compile(r"[0-9０-９]+便"),
)


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    quotes = [m.group(0)[1:-1] for m in QUOTE_RE.finditer(text)]
    prose = QUOTE_RE.sub(" ", text)
    return prose, " ".join(quotes)


def mask_excluded(text: str) -> str:
    if not text:
        return ""
    masked = _EXCLUDE_RE.sub(lambda m: _SENTINEL * len(m.group(0)), text)
    for pat in EXCLUDE_PATTERNS:
        masked = pat.sub(lambda m: _SENTINEL * len(m.group(0)), masked)
    return masked


def scan_text(text: str) -> dict[str, dict[str, Any]]:
    masked = mask_excluded(text)
    out: dict[str, dict[str, Any]] = {g: {"count": 0, "by_term": {}} for g in ABJECTION_GROUPS}
    for m in _TERM_RE.finditer(masked):
        tok = m.group(0)
        grp = _TERM_TO_GROUP[tok]
        out[grp]["count"] += 1
        by_term = out[grp]["by_term"]
        by_term[tok] = by_term.get(tok, 0) + 1
    return out


def inspect_raw_kanji_in_fragments(
    fragments: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    kwic: dict[str, list[dict[str, str]]] = {ch: [] for ch in RAW_KANJI}
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, _ = split_prose_and_quotes(str(frag.get("text", "")))
        masked = mask_excluded(prose)
        for ch in RAW_KANJI:
            start = 0
            while True:
                idx = masked.find(ch, start)
                if idx == -1:
                    break
                lo = max(0, idx - 16)
                hi = min(len(prose), idx + 18)
                snippet = prose[lo:hi].replace("\n", " ")
                kwic[ch].append(
                    {
                        "fragment_id": fid,
                        "title": str(frag.get("title", "")),
                        "snippet": snippet.strip(),
                    }
                )
                start = idx + 1
    return kwic


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    total_chars = 0
    groups: dict[str, dict[str, Any]] = {
        g: {
            "label": spec["label"],
            "count": 0,
            "doc_count": 0,
            "doc_ids": [],
            "by_term": {},
        }
        for g, spec in ABJECTION_GROUPS.items()
    }
    for doc_id, text in docs:
        total_chars += len(text)
        scanned = scan_text(text)
        for g, info in scanned.items():
            if info["count"]:
                groups[g]["count"] += info["count"]
                groups[g]["doc_count"] += 1
                groups[g]["doc_ids"].append(doc_id)
                for term, n in info["by_term"].items():
                    groups[g]["by_term"][term] = groups[g]["by_term"].get(term, 0) + n
    return {"char_total": total_chars, "doc_total": len(docs), "groups": groups}


def measure_abjection_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    frag_prose_docs: list[tuple[str, str]] = []
    frag_quote_docs: list[tuple[str, str]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quotes = split_prose_and_quotes(str(frag.get("text", "")))
        frag_prose_docs.append((fid, prose))
        frag_quote_docs.append((fid, quotes))
    mat_docs: list[tuple[str, str]] = []
    for mat in materials or []:
        mid = str(mat.get("material_id", ""))
        blob = " ".join(
            [
                str(mat.get("title", "")),
                str(mat.get("passage", "")),
                str(mat.get("source_note", "")),
            ]
        )
        mat_docs.append((mid, blob))
    if readings is None:
        readings = [
            (p.name, p.read_text(encoding="utf-8"))
            for p in sorted((ROOT / "readings").glob("*.md"))
        ]
    kwic = inspect_raw_kanji_in_fragments(fragments)
    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(frag_prose_docs),
        "fragments_quotes": _aggregate_docs(frag_quote_docs),
        "materials": _aggregate_docs(mat_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "group_order": list(ABJECTION_GROUPS.keys()),
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
    print("=== abjection_audit — 汚れ・排泄・浄化・廃棄・腐敗 ===")
    print()
    print(
        f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字"
    )
    for g in report["group_order"]:
        info = fp["groups"][g]
        print(
            f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編"
        )
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    qp = report["fragments_quotes"]
    print(f"引用内         : {qp['char_total']:,} 字")
    for g in report["group_order"]:
        info = qp["groups"][g]
        print(
            f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編"
        )
    mp = report["materials"]
    print(f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字")
    for g in report["group_order"]:
        info = mp["groups"][g]
        print(
            f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件"
        )
    rp = report["readings"]
    print(f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字")
    for g in report["group_order"]:
        info = rp["groups"][g]
        print(
            f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本"
        )
    print()
    print("註: 語形の数であり、汚染・清潔・道徳・意識の有無の判定ではない。")
    if kwic:
        print()
        for ch, rows in report["raw_kanji_kwic"].items():
            print(f"--- 生字「{ch}」{len(rows)} 箇所 ---")
            for row in rows[:40]:
                print(f"  {row['fragment_id']}: …{row['snippet']}…")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--kwic", action="store_true")
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args(argv)
    frags = _load_union("fragments", "fragment_id", args.base_only)
    mats = _load_union("materials", "material_id", args.base_only)
    report = measure_abjection_audit(frags, mats)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
