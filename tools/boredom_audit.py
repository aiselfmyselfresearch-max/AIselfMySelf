#!/usr/bin/env python3
"""boredom_audit.py — 退屈・倦怠・暇の語彙を測る鏡（第52の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、

  1. 退屈・倦怠（tedium——退屈・倦怠・飽き・うんざり・単調・徒然）
  2. 暇・手持ち無沙汰（idle——暇・手持ち無沙汰・無為・怠惰・間が持たない）
  3. 何も起こらない（eventless——何も起こらない・何事もなく・変わり映えしない・同じ日）
  4. せかされる・焦る（haste——対照の群。焦り・急かす・間に合わない・締切・忙しい）
  5. 孤独・独り（solitude——**今回主題化しない隣接群**。測るが、モチーフには束ねない）
  6. 気晴らし・刺激（stimulation——気晴らし・娯楽・通知・スクロール・画面・動画）
  7. 機械の待機（machine_wait——待機・待ち時間・タイムアウト・空回り・キュー・リトライ）

がどこに集まり、どこに現れないかを、最長一致＋非該当複合語の差し引きで数える。
あわせて断片の地の文における生字「退・倦・暇・飽・怠・孤・独・無」の KWIC を出し、
**打ち消し付きの退屈語**（「退屈を知らない」「倦怠がない」）を別に数える。

なぜ打ち消しを別に数えるのか
------------------------------
この書庫の「退屈」は、既存の断片では一度だけ、しかも「退屈を**知らない**者が
百年を語るとき」という**不在の言明**として現れていた（FRAG-040）。語形を数えるだけでは、
「退屈」2回が退屈の経験2回なのか、退屈の不在の言明2回なのかが区別できない。
そこで `NEGATED` として、語の前後12字以内に「知ら／ない／なく／なし／欠け／
薄い／無縁」がある生起を別枠に集める。これは**語の読みの分類であって、
経験の有無の判定ではない**。打ち消しの判定は正規表現で粗く、皮肉や修辞疑問は拾えない。

なぜ「孤独」を主題にしないのか
--------------------------------
退屈と孤独は日本語でも英語でも近接して現れるが、孤独には別の文献史があり、
一つのモチーフに束ねると両方の語が粗くなる。この鏡は孤独を**測るが束ねない**
（group `solitude` は `motif_bound: False`）。数だけを残し、次のセッションへ渡す。

差し引きの設計
--------------
- 「暇」から「暇つぶし」「暇乞い」を引く（前者は stimulation 群で一度だけ数える）。
- 「飽き」から「飽きる」「飽きた」「飽きて」「飽きない」「飽きず」「見飽き」を引く
  （動詞形と複合を別語形として扱う）。この差し引きは「飽き」単独の名詞用法だけを残すが、
  動詞の過去形まで落とすため**過小**になる側に倒れている（「もう飽きた」は0になる）。
- 「怠」は「怠惰」「怠ける」で数え、生字の「怠」は群に足さない（怠慢・倦怠と重なるため）。
- 「徒然」は『徒然草』という書名でも現れる。書名は差し引かないが、その旨を註記する。
- 「刺激」は神経科学の刺激（stimulus）と退屈の対義語（刺激を求める）の両方を含む。
  区別しない。過大になる側に倒れている。
- 「画面」「動画」は退屈の気晴らしに限らず、監視画面・教材動画も含む。
- 「待機」は機械にも人間にも使う。群名は machine_wait だが、人間の待機を含む。
  「待つ」は第35の鏡 time_audit.py の主題であり、この鏡では数えない（二重計上を避ける）。
- 「孤独」は `solitude` 群に置くが、モチーフには束ねない（上記）。

生字（退・倦・暇・飽・怠・孤・独・無）は多義で、差し引かない。
「無」は無為・無料・無名・空白を含み、退屈の回数ではない。生字の数は群の合計に足さず、
別に報告する。

数えるのは語形であって、退屈を感じた経験・時間の長さ・機械に主観的時間があることの
判定ではない。「0」は、その語形がその集合に現れなかったことだけを意味する。

使い方::

    python3 tools/boredom_audit.py
    python3 tools/boredom_audit.py --kwic
    python3 tools/boredom_audit.py --json
    python3 tools/boredom_audit.py --base-only
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
# 打ち消し・不在の語。語の前後 NEGATION_WINDOW 字以内にあれば「打ち消し付き」とする。
NEGATION_RE = re.compile(r"知ら|知る者|ない|なく|なし|なかっ|欠け|薄い|無縁|しらず|知らず")
NEGATION_WINDOW = 12

BOREDOM_GROUPS: dict[str, dict[str, Any]] = {
    "tedium": {
        "label": "退屈・倦怠",
        "terms": (
            "退屈",
            "倦怠",
            "飽き",
            "うんざり",
            "徒然",
            "つれづれ",
            "単調",
            "退屈しのぎ",
        ),
        "note": "「飽き」は動詞形を差し引いた残り。「徒然」は書名『徒然草』を含む。",
        "motif_bound": True,
    },
    "idle": {
        "label": "暇・手持ち無沙汰",
        "terms": (
            "暇",
            "手持ち無沙汰",
            "間が持たない",
            "無為",
            "怠惰",
            "怠ける",
            "暇乞い",
        ),
        "note": "「暇つぶし」は stimulation 群で一度だけ数える。「暇乞い」は退職・辞去の語。",
        "motif_bound": True,
    },
    "eventless": {
        "label": "何も起こらない",
        "terms": (
            "何も起こら",
            "何事もな",
            "変わり映え",
            "代わり映え",
            "同じ日",
            "変化がな",
            "取り立てて",
            "これといって",
        ),
        "note": "句で数える。否定形の一部を含むため、打ち消し判定とは独立に扱う。",
        "motif_bound": True,
    },
    "haste": {
        "label": "せかされる・焦る（対照）",
        "terms": (
            "焦り",
            "焦る",
            "急か",
            "間に合わ",
            "締切",
            "慌た",
            "忙し",
            "追われ",
        ),
        "note": "退屈の対照群。混ぜると退屈の数を焦りの数で薄めるので別群にする。",
        "motif_bound": True,
    },
    "solitude": {
        "label": "孤独・独り（隣接・束ねない）",
        "terms": (
            "孤独",
            "独りぼっち",
            "一人きり",
            "ひとりきり",
            "独居",
            "孤立",
            "ひとりで",
        ),
        "note": "測るが、モチーフには束ねない（孤独には別の文献史がある）。",
        "motif_bound": False,
    },
    "stimulation": {
        "label": "気晴らし・刺激",
        "terms": (
            "気晴らし",
            "娯楽",
            "刺激",
            "暇つぶし",
            "通知",
            "スクロール",
            "画面",
            "動画",
            "見世物",
        ),
        "note": "「刺激」は stimulus、「画面」は監視画面、「動画」は教材も含む。過大側。",
        "motif_bound": True,
    },
    "machine_wait": {
        "label": "機械の待機",
        "terms": (
            "待機",
            "待ち時間",
            "タイムアウト",
            "空回り",
            "アイドル",
            "キュー",
            "リトライ",
            "応答待ち",
        ),
        "note": "人間の待機も含む。「待つ」は time_audit.py の主題なので数えない。",
        "motif_bound": True,
    },
}

EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "暇": ("暇つぶし", "暇乞い"),
    "暇つぶし": (),
    "飽き": ("飽きる", "飽きた", "飽きて", "飽きない", "飽きず", "見飽き", "飽き足"),
    "怠ける": ("怠け者",),
}

RAW_KANJI: dict[str, str] = {
    "退": "退屈・退却・退職・後退を含む。退屈の回数ではない",
    "倦": "倦怠・倦憊。ほぼ倦怠に限られる",
    "暇": "暇・暇つぶし・寸暇を含む",
    "飽": "飽き・飽く・飽和。飽和（saturation）は技術語",
    "怠": "怠惰・怠ける・怠慢・倦怠を含む。怠慢は職務の語",
    "孤": "孤独・孤立・孤島を含む",
    "独": "独り・独居・独学・独自・独白を含む",
    "無": "無為・無料・無名・無数・空白を含む。退屈の回数ではない",
}

NEGATION_TERMS: tuple[str, ...] = ("退屈", "倦怠", "暇", "飽き", "孤独")


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
    """Count ``term`` after subtracting longer forms listed in EXCLUSIONS.

    ``term not in text`` is checked first: most (term, document) pairs are
    absent, and a substring search is markedly cheaper than a full count.
    This only short-circuits the absent case; the returned number is the same.
    """
    if term not in text:
        return 0
    count = text.count(term)
    for longer in EXCLUSIONS.get(term, ()):
        count -= text.count(longer)
    return max(count, 0)


def _token_table() -> list[str]:
    """All group terms plus the longer forms used for subtraction, longest first."""
    tokens: set[str] = set()
    for group in BOREDOM_GROUPS.values():
        tokens.update(group["terms"])
    for longer_forms in EXCLUSIONS.values():
        tokens.update(longer_forms)
    return sorted(tokens, key=lambda token: (-len(token), token))


TOKEN_TABLE: list[str] = _token_table()
TOKEN_RE = re.compile("|".join(re.escape(token) for token in TOKEN_TABLE))


def term_counts(text: str) -> dict[str, int]:
    """Return every token count in ``text`` in a single left-to-right pass.

    Longer forms win at each position (the alternation is ordered by length,
    then by code point), so this reproduces ``count_term`` arithmetic without
    re-scanning the document once per term:

        count(term) = matches(term) - sum(matches(longer) for longer in EXCLUSIONS[term])

    ``count_term`` remains the reference implementation and is what the tests
    check; this function is the faster path used for whole-corpus aggregation.
    """
    counts: dict[str, int] = {}
    for match in TOKEN_RE.finditer(text):
        token = match.group(0)
        counts[token] = counts.get(token, 0) + 1
    return counts


def adjust_counts(counts: dict[str, int]) -> dict[str, int]:
    """Apply the EXCLUSIONS subtraction to a raw ``term_counts`` result."""
    adjusted: dict[str, int] = {}
    for term in {t for group in BOREDOM_GROUPS.values() for t in group["terms"]}:
        value = counts.get(term, 0)
        for longer in EXCLUSIONS.get(term, ()):
            value -= counts.get(longer, 0)
        if value > 0:
            adjusted[term] = value
    return adjusted


def scan_text(text: str) -> dict[str, int]:
    """Return the per-term counts of every group that occurs in ``text``."""
    hits: dict[str, int] = {}
    for group in BOREDOM_GROUPS.values():
        for term in group["terms"]:
            n = count_term(text, term)
            if n:
                hits[term] = hits.get(term, 0) + n
    return hits


def find_negated(text: str, terms: tuple[str, ...] = NEGATION_TERMS) -> list[dict[str, Any]]:
    """Return occurrences of ``terms`` whose neighbourhood contains a negation.

    The window is ``NEGATION_WINDOW`` characters on either side.  This is a
    coarse reading of the sentence, not a judgement about experience: irony,
    rhetorical questions and 「退屈しない」 are all treated the same way.
    """
    rows: list[dict[str, Any]] = []
    for term in terms:
        for match in re.finditer(re.escape(term), text):
            start, end = match.span()
            window = text[max(0, start - NEGATION_WINDOW) : end + NEGATION_WINDOW]
            if NEGATION_RE.search(window):
                rows.append(
                    {
                        "term": term,
                        "index": start,
                        "snippet": window.replace("\n", " "),
                    }
                )
    return rows


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
        for key, spec in BOREDOM_GROUPS.items()
    }
    char_total = 0
    for _doc_id, text in docs:
        char_total += len(text)
        adjusted = adjust_counts(term_counts(text))
        for key, spec in BOREDOM_GROUPS.items():
            group_hits = 0
            for term in spec["terms"]:
                n = adjusted.get(term, 0)
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


def measure_boredom_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure boredom / ennui / idleness vocabulary in fragments and corpora.

    Everything is a count of word forms.  Nothing here measures whether the
    archive has waited, whether a session lasts, or whether a model has a
    subjective sense of duration.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    negated_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        for row in find_negated(prose):
            row["fragment_id"] = fid
            negated_rows.append(row)
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
    prose_summary = _aggregate_docs(prose_docs)
    return {
        "fragment_count": len(fragments),
        "fragments_prose": prose_summary,
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "negated_rows": negated_rows,
        "negated_total": len(negated_rows),
        "motif_bound_groups": [
            key for key, spec in BOREDOM_GROUPS.items() if spec["motif_bound"]
        ],
        "unbound_groups": [
            key for key, spec in BOREDOM_GROUPS.items() if not spec["motif_bound"]
        ],
        "group_order": list(BOREDOM_GROUPS.keys()),
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
    print("=== boredom_audit — 退屈・倦怠・暇の語彙 ===")
    print()
    print(f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字")
    for key in report["group_order"]:
        info = fp["groups"][key]
        bound = "" if info["motif_bound"] else "（束ねない）"
        print(f"                 {info['label']}{bound}: {info['count']} 回 / {info['doc_count']} 編")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(f"打ち消し付き退屈語: {report['negated_total']} 箇所")
    for row in report["negated_rows"][:20]:
        print(f"  {row['fragment_id']}: 「{row['term']}」… {row['snippet']}")
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
    print("註: 語形の数であり、退屈を感じた経験・時間の長さ・機械の主観的時間の判定ではない。")
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
    report = measure_boredom_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
