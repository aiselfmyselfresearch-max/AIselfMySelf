#!/usr/bin/env python3
"""signature_audit.py — 署名・筆跡・印章・偽書・機械の署名を測る鏡。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、
  1. 筆跡・真跡・手書き（handwriting_trace）
  2. 署名・自署・花押・落款（signature_mark）
  3. 印章・印鑑・捺印（seal_stamp）
  4. 偽書・贋作・真贋鑑定（forgery_authorship）
  5. 電子署名・透かし・コミット署名（machine_signature）
がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「署・筆・印・偽・贋」の KWIC を出す。

使い方::

    python3 tools/signature_audit.py
    python3 tools/signature_audit.py --kwic
    python3 tools/signature_audit.py --json
    python3 tools/signature_audit.py --base-only
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

SIGNATURE_GROUPS: dict[str, dict[str, Any]] = {
    "handwriting_trace": {
        "label": "筆跡・真跡・手書き",
        "terms": (
            "手書き",
            "直筆",
            "真跡",
            "真蹟",
            "肉筆",
            "筆跡",
            "能書",
            "悪筆",
            "臨書",
            "摹本",
            "双鉤",
            "行書",
            "草書",
            "楷書",
            "書法",
            "書道",
            "筆致",
            "筆順",
            "筆圧",
            "自筆",
            "墨跡",
            "墨蹟",
            "手澤",
        ),
    },
    "signature_mark": {
        "label": "署名・自署・花押・落款",
        "terms": (
            "電子署名",
            "デジタル署名",
            "デジタルサイン",
            "自署",
            "連署",
            "副署",
            "花押",
            "落款",
            "署名",
            "サイン",
        ),
    },
    "seal_stamp": {
        "label": "印章・印鑑・捺印",
        "terms": (
            "印鑑登録",
            "印鑑証明",
            "実印",
            "認印",
            "三文判",
            "印章",
            "印鑑",
            "朱印",
            "捺印",
            "押印",
            "契印",
            "割印",
            "印を押",
        ),
    },
    "forgery_authorship": {
        "label": "偽書・贋作・真贋鑑定",
        "terms": (
            "筆跡鑑定",
            "真贋",
            "偽書",
            "贋作",
            "偽作",
            "贋物",
            "偽物",
            "偽造",
            "鑑定",
            "真作",
        ),
    },
    "machine_signature": {
        "label": "電子署名・透かし・コミット署名",
        "terms": (
            "電子署名",
            "デジタル署名",
            "コミット署名",
            "ウォーターマーク",
            "コンテンツ認証",
            "公開鍵",
            "秘密鍵",
            "透かし",
            "GPG",
            "PGP",
            "RSA",
            "ECDSA",
            "C2PA",
        ),
    },
}

EXCLUDE_TERMS: tuple[str, ...] = (
    "筆者",
    "執筆",
    "鉛筆",
    "筆頭",
    "筆談",
    "筆記試験",
    "筆記用具",
    "印刷",
    "印象派",
    "印象",
    "印字",
    "印税",
    "インド",
    "印欧",
    "印加",
    "サインを出",
    "サイン会",
    "交通標識",
    "道路標識",
    "偽陽性",
    "偽陰性",
    "偽物の",
)

RAW_KANJI: tuple[str, ...] = ("署", "筆", "印", "偽", "贋")

_SENTINEL = "\u0000"
_TERM_TO_GROUP: dict[str, str] = {}
for _gname, _spec in SIGNATURE_GROUPS.items():
    for _t in _spec["terms"]:
        _TERM_TO_GROUP.setdefault(_t, _gname)

_ALL_TERMS = sorted(_TERM_TO_GROUP.keys(), key=len, reverse=True)
_TERM_RE = re.compile("|".join(re.escape(t) for t in _ALL_TERMS))
_EXCLUDE_RE = re.compile(
    "|".join(re.escape(t) for t in sorted(set(EXCLUDE_TERMS), key=len, reverse=True))
)


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    quotes = [m.group(0)[1:-1] for m in QUOTE_RE.finditer(text)]
    prose = QUOTE_RE.sub(" ", text)
    return prose, " ".join(quotes)


def mask_excluded(text: str) -> str:
    if not text:
        return ""
    return _EXCLUDE_RE.sub(lambda m: _SENTINEL * len(m.group(0)), text)


def scan_text(text: str) -> dict[str, dict[str, Any]]:
    masked = mask_excluded(text)
    out: dict[str, dict[str, Any]] = {g: {"count": 0, "by_term": {}} for g in SIGNATURE_GROUPS}
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
        for g, spec in SIGNATURE_GROUPS.items()
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


def measure_signature_audit(
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
        "group_order": list(SIGNATURE_GROUPS.keys()),
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
    print("=== signature_audit — 署名・筆跡・印章・偽書・機械の署名 ===")
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
    print("註: 語形の数であり、真正性・作者性・意識の有無の判定ではない。")
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
    report = measure_signature_audit(frags, mats)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
