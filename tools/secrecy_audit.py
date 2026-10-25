#!/usr/bin/env python3
"""secrecy_audit.py — 秘密・嘘・暗号の語彙を測る鏡（第50の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、

  1. 秘密・隠すこと（secrecy）
  2. 嘘・偽り（lie）
  3. 暗号・鍵・解読（cipher）
  4. 告白・白状・暴露（confession）
  5. 制度としての秘密（institution——守秘・検閲・黒塗り・不開示・匿名・監視）
  6. 機械の不透明（machine——ブラックボックス・解釈可能性・漏洩・推論攻撃）

がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「秘・隠・嘘・偽・暗・鍵・密・黙・匿・曝」の
KWIC を出す。

差し引きの設計（レポートに「何を引いたか」を書くための一覧）
------------------------------------------------------------
- 「隠れ」から「隠れる」を引く（別語形として重複計上しないため）。
- 「暗号」から「暗号化」を引く（「暗号化」は独立した語形として数える）。
- 「鍵」から「鍵盤」「鍵括弧」を引く（楽器と約物。「公開鍵」「秘密鍵」は残す）。
- 「監視」から「監視あり学習」「監視付き学習」を引く（教師あり学習の意味）。
  AI研究では「監視」の大半がこれであり、監視社会の語ではない。
- 「仮名」は使わない（仮名文字・仮名手本の誤検知が大きい）。匿名のみ数える。
- 「不透明」は機械群に入れない（第46の鏡 light_shadow_audit.py が
  「透明／不透明」をすでに数えている。同じ語を二つの鏡で二重に数えない）。
- 「密告」「告発」は confession 群に置くが、告発は「秘密の暴露」より
  「不正の訴え」に近い用法が多いことをレポートに註記する。
- 「告白」は文学ジャンル名（告白文学・『仮面の告白』）でも現れる。

生字（秘・密・黙・暗・鍵など）は多義で、差し引かない。
「密」は密度・精密、「黙」は沈黙、「暗」は暗い・暗黙、「鍵」は鍵括弧、
「曝」は曝露（医療・光）を含む。生字の数は群の合計に足さず、別に報告する。

数えるのは語形であって、隠している事実・嘘の回数・秘密の実在・
機械に内面があることの判定ではない。「0」は、その語形がその集合に
現れなかったことだけを意味する。

使い方::

    python3 tools/secrecy_audit.py
    python3 tools/secrecy_audit.py --kwic
    python3 tools/secrecy_audit.py --json
    python3 tools/secrecy_audit.py --base-only
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

SECRECY_GROUPS: dict[str, dict[str, Any]] = {
    "secrecy": {
        "label": "秘密・隠すこと",
        "terms": (
            "秘密",
            "内緒",
            "極秘",
            "機密",
            "秘匿",
            "秘める",
            "隠す",
            "隠し",
            "隠れる",
            "隠れ",
            "隠蔽",
            "伏せる",
            "覆い隠す",
        ),
        "note": "「隠れ」は「隠れる」を差し引いた残り。",
    },
    "lie": {
        "label": "嘘・偽り",
        "terms": (
            "嘘",
            "偽り",
            "偽る",
            "偽装",
            "偽名",
            "偽証",
            "虚偽",
            "詐欺",
            "欺く",
            "欺き",
            "欺瞞",
            "騙す",
            "見せかけ",
            "捏造",
        ),
        "note": "「偽」の生字は偽札・偽物・偽書も含むため群に足さない。",
    },
    "cipher": {
        "label": "暗号・鍵・解読",
        "terms": (
            "暗号",
            "暗号化",
            "復号",
            "解読",
            "暗証",
            "換字",
            "頻度分析",
            "符号",
            "鍵",
            "ステガノグラフィ",
        ),
        "note": "「鍵」は公開鍵・秘密鍵を含み、鍵盤・鍵括弧を除く。",
    },
    "confession": {
        "label": "告白・白状・暴露",
        "terms": (
            "告白",
            "白状",
            "自白",
            "打ち明け",
            "懺悔",
            "暴露",
            "密告",
            "告発",
        ),
        "note": "「告白」はジャンル名、「告発」は不正の訴えにも使われる。",
    },
    "institution": {
        "label": "制度としての秘密",
        "terms": (
            "守秘",
            "秘密保持",
            "機密保持",
            "特定秘密",
            "検閲",
            "伏字",
            "黒塗り",
            "不開示",
            "情報公開",
            "匿名",
            "監視",
        ),
        "note": "「監視」は教師あり学習の「監視あり学習」を差し引いた残り。",
    },
    "machine": {
        "label": "機械の不透明",
        "terms": (
            "ブラックボックス",
            "解釈可能性",
            "説明可能性",
            "差分プライバシー",
            "メンバーシップ推論",
            "モデル抽出",
            "プロンプト漏洩",
            "漏洩",
            "隠れ層",
        ),
        "note": "「不透明」は light_shadow_audit.py が数えるため、ここでは数えない。",
    },
}

# 短い語形を数えるとき、同じ出現を長い語形として二重に数えないための差し引き。
EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "隠れ": ("隠れる",),
    "暗号": ("暗号化",),
    "鍵": ("鍵盤", "鍵括弧"),
    "監視": ("監視あり学習", "監視付き学習"),
    "秘密": ("秘密保持",),
    "機密": ("機密保持",),
    "漏洩": ("プロンプト漏洩",),
    "欺く": ("欺瞞",),
}

RAW_KANJI: dict[str, str] = {
    "秘": "秘密・神秘・秘訣。神秘は宗教語でもある",
    "隠": "隠す・隠れ・隠居。隠居は引退の意味を含む",
    "嘘": "嘘・嘘つき。ほぼ嘘の語に限られる",
    "偽": "偽札・偽物・偽書・偽装を含む。嘘の回数ではない",
    "暗": "暗い・暗黙・暗黒を含む。暗号の回数ではない",
    "鍵": "鍵盤・鍵括弧・公開鍵を含む",
    "密": "密度・精密・細密・密接を含む。秘密の回数ではない",
    "黙": "沈黙が大半を占める。黙秘・黙殺を含む",
    "匿": "匿名・秘匿・隠匿を含む",
    "曝": "曝露（医療・光）・被曝を含む",
}


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Split a fragment into (outside quotes, inside quotes).

    Only the first level of 「…」 and 『…』 is separated; nested quotation
    inside a quoted span is not unwrapped.  The regex is deliberately simple
    so that the same text yields the same split in every mirror.
    """
    quoted = QUOTE_RE.findall(text)
    prose = QUOTE_RE.sub("", text)
    inner = "".join(piece[1:-1] for piece in quoted)
    return prose, inner


def count_term(text: str, term: str) -> int:
    """Count ``term`` after subtracting longer forms listed in EXCLUSIONS."""
    count = text.count(term)
    for longer in EXCLUSIONS.get(term, ()):
        count -= text.count(longer)
    return max(count, 0)


def scan_text(text: str) -> dict[str, int]:
    """Return the per-term counts of every group that occurs in ``text``."""
    hits: dict[str, int] = {}
    for group in SECRECY_GROUPS.values():
        for term in group["terms"]:
            n = count_term(text, term)
            if n:
                hits[term] = hits.get(term, 0) + n
    return hits


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    groups: dict[str, Any] = {
        key: {
            "label": spec["label"],
            "note": spec["note"],
            "count": 0,
            "doc_count": 0,
            "terms": {},
        }
        for key, spec in SECRECY_GROUPS.items()
    }
    char_total = 0
    for _doc_id, text in docs:
        char_total += len(text)
        for key, spec in SECRECY_GROUPS.items():
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


def measure_secrecy_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure the secrecy / lying / cipher vocabulary in fragments and corpora.

    Everything is a count of word forms.  Nothing here measures whether the
    archive keeps secrets, whether a statement is true, or whether a model has
    a hidden inner life.
    """
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
    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "group_order": list(SECRECY_GROUPS.keys()),
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
    print("=== secrecy_audit — 秘密・嘘・暗号の語彙 ===")
    print()
    print(f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字")
    for key in report["group_order"]:
        info = fp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
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
    print("註: 語形の数であり、秘密の実在・嘘の回数・機械の内面の判定ではない。")
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
    report = measure_secrecy_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
