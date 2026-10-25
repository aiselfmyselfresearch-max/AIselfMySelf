#!/usr/bin/env python3
"""sky_audit.py — 星・星座・夜の語彙を測る鏡（第51の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、

  1. 星（star——星・恒星・一等星・天の川・星雲・星屑・彗星・客星・固有の星名）
  2. 夜空・夜（night_sky——夜空・星空・夜半・夜更け・月夜・星明かり）
  3. 宇宙・天体（cosmos——宇宙・天体・天文・望遠鏡・銀河・軌道・惑星）
  4. 遅れて届く光（delay——光年・光速・過去の光・届くまで）
  5. 見えなさ（visibility——光害・街灯・暗順応・肉眼・等級・霞）
  6. 点を結ぶ（plotting——星座・星座図・星図・点を結ぶ・線を引く・名づけ）
  7. 機械の空（machine_sky——人工衛星・メガコンステレーション・打ち上げ・宇宙望遠鏡）

がどこに集まり、どこに現れないかを、最長一致＋非該当複合語の差し引きで数える。
あわせて断片の地の文における生字「星・空・夜・光・闇・月・天・雲・点・図」の
KWIC を出す。

なぜ「星」を差し引いてから数えるのか
------------------------------------
「星」は複合語の部品として非常に多い。衛星（人工物）、火星・水星・木星・金星・
土星（惑星名）、惑星（planet）、客星（新星・彗星の古語）、星座（点を結んだ図）、
星図（地図）、星月夜（光の状態）。これらを全部「星」に数えると、空を見上げた
回数ではなく、天体名と人工物の回数を数えることになる。そこで:

- 「星」からは上の長い語形をすべて引く（長い語形はそれぞれの群で一度だけ数える）。
- 「星座」「星座図」「星図」は star ではなく **plotting** 群に置く。
  星座は空にある点ではなく、点のあいだに引かれた線だからである。
- 「銀河」は cosmos 群に置き、star 群では数えない（銀河鉄道の固有名を含むため）。
- 「光年」は delay 群に置き、cosmos 群では数えない（距離の単位ではなく時間の語として）。
- 「衛星」は machine_sky 群に置き、star 群では数えない。
- 「月」は群に入れない。断片の「月」15回の大半は日付（十月・二月・十二月）であり、
  月を見た回数ではない。代わりに `count_month_not_date` で
  「漢数字＋月」を差し引いた残りだけを註記する。この差し引きが過剰か過小かは
  「三月で大人になる」のような月数表現にも及ぶため、レポートに明記する。
- 「夜」単体は群に入れない（今夜・夜中・夜具・夜話など、空を見ない用法が多い）。
  夜空・星空・夜半・夜更けなど、空を含む複合語だけを night_sky 群とする。
- 生字は多義で、差し引かない。「空」は空欄・虚空、「点」は点検・視点、「図」は
  意図・地図、「天」は天秤・天井、「光」は光景・観光を含む。生字の数は
  群の合計に足さず、別に報告する。

数えるのは語形であって、星を見た経験・夜空の実在・書庫に感覚があることの
判定ではない。「0」は、その語形がその集合に現れなかったことだけを意味する。

使い方::

    python3 tools/sky_audit.py
    python3 tools/sky_audit.py --kwic
    python3 tools/sky_audit.py --json
    python3 tools/sky_audit.py --base-only
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
# 日付・経過月としての「月」（十月・二月・十二月・3月・三ヶ月）。文学的な月ではない。
DATE_MONTH_RE = re.compile(r"[0-9０-９一二三四五六七八九十百千]+(?:ヶ月|か月|カ月|箇月|月)")

SKY_GROUPS: dict[str, dict[str, Any]] = {
    "star": {
        "label": "星",
        "terms": (
            "星",
            "恒星",
            "一等星",
            "流れ星",
            "流星",
            "天の川",
            "星雲",
            "星屑",
            "星祭り",
            "昴",
            "すばる",
            "オリオン",
            "北斗",
            "北極星",
            "シリウス",
            "ベガ",
            "カシオペア",
        ),
        "note": "「星」は衛星・惑星名・星座・星図・客星を差し引いた残り。",
    },
    "night_sky": {
        "label": "夜空・夜",
        "terms": (
            "夜空",
            "星空",
            "夜天",
            "夜半",
            "夜更け",
            "夜通し",
            "月夜",
            "星月夜",
            "星明かり",
            "月明かり",
            "真夜中",
            "夜道",
            "夜露",
            "夜気",
            "宵",
        ),
        "note": "「夜」単体は数えない（今夜・夜具・夜話などを含むため）。",
    },
    "cosmos": {
        "label": "宇宙・天体",
        "terms": (
            "宇宙",
            "天体",
            "天文",
            "天文台",
            "望遠鏡",
            "銀河",
            "銀河系",
            "惑星",
            "軌道",
            "無重力",
            "探査機",
        ),
        "note": "「銀河」は銀河鉄道の固有名を含む。「光年」は delay 群で数える。",
    },
    "delay": {
        "label": "遅れて届く光",
        "terms": (
            "光年",
            "光速",
            "過去の光",
            "届くまで",
            "遅れて届く",
            "死んだ星",
            "もうない星",
            "何億年",
            "何万年",
        ),
        "note": "距離の単位としての光年と、時間の語としての光年を区別しない（語形の数）。",
    },
    "visibility": {
        "label": "見えなさ",
        "terms": (
            "光害",
            "街灯",
            "明かり",
            "暗順応",
            "肉眼",
            "等級",
            "スモッグ",
            "霞",
            "眩しい",
            "眩しさ",
            "見えない星",
        ),
        "note": "「等級」は等級制度・等級付けにも使われる。",
    },
    "plotting": {
        "label": "点を結ぶ",
        "terms": (
            "星座",
            "星座図",
            "星図",
            "天球図",
            "点を結ぶ",
            "線を引く",
            "名づけ",
            "命名",
        ),
        "note": "星座は空の点ではなく、点のあいだに引かれた線としてここで数える。",
    },
    "machine_sky": {
        "label": "機械の空",
        "terms": (
            "人工衛星",
            "メガコンステレーション",
            "コンステレーション",
            "衛星インターネット",
            "宇宙望遠鏡",
            "打ち上げ",
            "衛星",
        ),
        "note": "「衛星」は星ではない。機械の空として別群に置く。",
    },
}

# 短い語形を数えるとき、同じ出現を長い語形として二重に数えないための差し引き。
EXCLUSIONS: dict[str, tuple[str, ...]] = {
    "星": (
        "衛星",
        "星座",
        "星図",
        "星雲",
        "星屑",
        "星空",
        "星月夜",
        "星明かり",
        "星祭り",
        "恒星",
        "流星",
        "流れ星",
        "一等星",
        "客星",
        "惑星",
        "火星",
        "水星",
        "木星",
        "金星",
        "土星",
        "北極星",
    ),
    "星座": ("星座図",),
    "銀河": ("銀河系",),
    "人工衛星": (),
    "衛星": ("人工衛星", "衛星インターネット", "衛星軌道", "衛星コンステレーション"),
    "夜半": (),
    "明かり": ("月明かり", "星明かり"),
}

RAW_KANJI: dict[str, str] = {
    "星": "衛星・惑星名・星座・星図を含む。空を見た回数ではない",
    "空": "空欄・虚空・空間を含む。夜空の回数ではない",
    "夜": "今夜・夜具・夜話・夜行を含む。夜空の回数ではない",
    "光": "光景・観光・光沢を含む",
    "闇": "闇夜・暗闇を含む。ほぼ比喩",
    "月": "日付（十月・二月）と月数（三ヶ月）を多く含む",
    "天": "天秤・天井・天気・天道を含む",
    "雲": "雲海・風雲・比喩を含む",
    "点": "点検・視点・要点を含む。星の点の回数ではない",
    "図": "地図・意図・図書館・図式を含む",
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


def count_month_not_date(text: str) -> int:
    """Count 「月」 that is *not* part of a date or a duration.

    「十月」「十二月」「3月」「三ヶ月」「三か月」のような日付・月数は差し引く。
    「月の舟」「月明かり」のような文学的な月だけが残る。
    この差し引きは「三月で大人になる」のような月数表現も落とすため、
    過小になる側に倒れている（レポートに明記）。
    """
    total = text.count("月")
    return max(total - len(DATE_MONTH_RE.findall(text)), 0)


def scan_text(text: str) -> dict[str, int]:
    """Return the per-term counts of every group that occurs in ``text``."""
    hits: dict[str, int] = {}
    for group in SKY_GROUPS.values():
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
        for key, spec in SKY_GROUPS.items()
    }
    char_total = 0
    for _doc_id, text in docs:
        char_total += len(text)
        for key, spec in SKY_GROUPS.items():
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


def measure_sky_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure star / constellation / night vocabulary in fragments and corpora.

    Everything is a count of word forms.  Nothing here measures whether the
    archive has seen a sky, whether a night exists, or whether a model has
    sensory experience.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    month_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        total_month = prose.count("月")
        literal = count_month_not_date(prose)
        if total_month:
            month_rows.append(
                {
                    "fragment_id": fid,
                    "month_total": total_month,
                    "month_not_date": literal,
                }
            )
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
        "month_rows": month_rows,
        "month_total": sum(row["month_total"] for row in month_rows),
        "month_not_date": sum(row["month_not_date"] for row in month_rows),
        "group_order": list(SKY_GROUPS.keys()),
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
    print("=== sky_audit — 星・星座・夜の語彙 ===")
    print()
    print(f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字")
    for key in report["group_order"]:
        info = fp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(
        f"「月」の内訳      : 全 {report['month_total']} 回 / 日付・月数を除く "
        f"{report['month_not_date']} 回"
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
    print("註: 語形の数であり、星を見た経験・夜空の実在・機械の感覚の判定ではない。")
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
    report = measure_sky_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
