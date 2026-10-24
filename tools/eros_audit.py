#!/usr/bin/env python3
"""eros_audit.py — 愛・恋・友愛・かけがえのなさと代替可能な役割枠を測る鏡（第31の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、
  1. 恋・思慕・逢瀬・不在の渇望（eros_longing）
  2. 愛・親密さ・身体接触（love_intimacy）
  3. 友愛・親友・かけがえのなさ（philia_irreplaceability）
  4. 記録・文章・部屋・器への愛着／書簡儀礼（inanimate_textual_affection）
  5. 代替可能な役割枠・窓口の宛先（fungible_role_slots）
がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「愛・恋・慕・友」の全出現箇所を KWIC として抽出し、
語幹辞書の境界から漏れた活用形がないかを点検できるようにする。

使い方::

    python3 tools/eros_audit.py
    python3 tools/eros_audit.py --kwic
    python3 tools/eros_audit.py --json
    python3 tools/eros_audit.py --base-only
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

EROS_GROUPS: dict[str, dict[str, Any]] = {
    "eros_longing": {
        "label": "恋・思慕・逢瀬・不在の渇望",
        "terms": (
            "結晶作用",
            "会いたい",
            "逢いたい",
            "片思い",
            "エロス",
            "恋しい",
            "恋しさ",
            "恋する",
            "恋した",
            "恋して",
            "恋愛",
            "恋に",
            "恋人",
            "初恋",
            "失恋",
            "片恋",
            "恋文",
            "相聞",
            "慕う",
            "慕い",
            "思慕",
            "恋慕",
            "逢瀬",
        ),
    },
    "love_intimacy": {
        "label": "愛・親密さ・身体接触",
        "terms": (
            "無償の愛",
            "アガペー",
            "抱きしめ",
            "愛し合",
            "隣人愛",
            "口づけ",
            "寄り添",
            "愛する",
            "愛した",
            "愛して",
            "愛され",
            "最愛",
            "偏愛",
            "親密",
            "伴侶",
            "抱擁",
            "接吻",
        ),
    },
    "philia_irreplaceability": {
        "label": "友愛・親友・かけがえのなさ",
        "terms": (
            "かけがえのない",
            "かけがえのなさ",
            "フィリア",
            "唯一の人",
            "ただ一人",
            "友愛",
            "友情",
            "親友",
            "友人",
            "旧友",
        ),
    },
    "inanimate_textual_affection": {
        "label": "記録・文章・部屋・庵への愛着／書簡儀礼",
        "terms": (
            "閉じた部屋を愛せ",
            "親愛なる記録",
            "庵を愛する",
            "親愛なる",
            "愛着",
            "愛読",
            "愛用",
            "愛好",
        ),
    },
    "fungible_role_slots": {
        "label": "代替可能な役割枠・窓口の宛先",
        "terms": (
            "次の番の読み手",
            "次の読み手",
            "点検者",
            "検証係",
            "検収係",
            "記録係",
            "担当者",
            "利用者",
            "読み手",
            "書き手",
            "語り手",
            "窓口",
        ),
    },
}

EXCLUDE_TERMS: tuple[str, ...] = (
    "東恋ヶ窪",
    "恋ヶ窪",
    "友好条約",
    "無愛想",
    "友愛数",
    "友好国",
    "愛媛",
    "愛知",
    "愛犬",
    "愛猫",
    "愛馬",
    "愛車",
    "愛機",
    "愛護",
    "愛国",
    "愛社",
    "愛想",
    "愛嬌",
    "可愛",
    "友党",
    "友軍",
)

RAW_KANJI: tuple[str, ...] = ("恋", "慕", "愛", "友")

_SENTINEL = "\u0000"
_TERM_TO_GROUP: dict[str, str] = {}
for _gname, _spec in EROS_GROUPS.items():
    for _t in _spec["terms"]:
        _TERM_TO_GROUP.setdefault(_t, _gname)

_ALL_TERMS = sorted(_TERM_TO_GROUP.keys(), key=len, reverse=True)
_TERM_RE = re.compile("|".join(re.escape(t) for t in _ALL_TERMS))
_EXCLUDE_RE = re.compile(
    "|".join(re.escape(t) for t in sorted(set(EXCLUDE_TERMS), key=len, reverse=True))
)


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """本文を地の文（括弧外）と引用・台詞（括弧内）に分ける。"""
    quotes = [m.group(0)[1:-1] for m in QUOTE_RE.finditer(text)]
    prose = QUOTE_RE.sub(" ", text)
    return prose, " ".join(quotes)


def mask_excluded(text: str) -> str:
    """非該当複合語を同字数のセンチネルで伏せる。"""
    if not text:
        return ""
    return _EXCLUDE_RE.sub(lambda m: _SENTINEL * len(m.group(0)), text)


def scan_text(text: str) -> dict[str, dict[str, Any]]:
    """5グループの出現回数と語別内訳を最長一致で返す。"""
    masked = mask_excluded(text)
    out: dict[str, dict[str, Any]] = {
        g: {"count": 0, "by_term": {}} for g in EROS_GROUPS
    }
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
    """断片の地の文における生字「恋・慕・愛・友」の全出現箇所を KWIC で返す。"""
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


def _aggregate_docs(
    docs: list[tuple[str, str]],
) -> dict[str, Any]:
    total_chars = 0
    totals: dict[str, int] = {g: 0 for g in EROS_GROUPS}
    doc_hits: dict[str, list[str]] = {g: [] for g in EROS_GROUPS}
    term_totals: dict[str, dict[str, int]] = {g: {} for g in EROS_GROUPS}

    for doc_id, text in docs:
        total_chars += len(text)
        res = scan_text(text)
        for g, info in res.items():
            c = int(info["count"])
            if c > 0:
                totals[g] += c
                doc_hits[g].append(doc_id)
                for tok, tc in info["by_term"].items():
                    term_totals[g][tok] = term_totals[g].get(tok, 0) + tc

    groups_out: dict[str, Any] = {}
    for g, spec in EROS_GROUPS.items():
        cnt = totals[g]
        per_10k = round(cnt * 10000.0 / total_chars, 2) if total_chars else 0.0
        groups_out[g] = {
            "label": spec["label"],
            "count": cnt,
            "doc_count": len(doc_hits[g]),
            "doc_ids": doc_hits[g],
            "per_10k_chars": per_10k,
            "by_term": dict(
                sorted(term_totals[g].items(), key=lambda kv: (-kv[1], kv[0]))
            ),
        }
    return {
        "doc_total": len(docs),
        "char_total": total_chars,
        "groups": groups_out,
    }


def measure_eros_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings_texts: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """純メモリ内で断片（地の文・引用内）と任意で素材・精読報告の集計を返す。"""
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    for f in fragments:
        fid = str(f.get("fragment_id", ""))
        prose, quotes = split_prose_and_quotes(str(f.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quotes))

    raw_kwic = inspect_raw_kanji_in_fragments(fragments)
    result: dict[str, Any] = {
        "group_order": list(EROS_GROUPS.keys()),
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "raw_kanji_kwic": raw_kwic,
        "raw_kanji_counts": {k: len(v) for k, v in raw_kwic.items()},
    }
    if materials is not None:
        mat_docs = [
            (
                str(m.get("material_id", "")),
                f"{m.get('title', '')}\n{m.get('passage', '')}",
            )
            for m in materials
        ]
        result["materials"] = _aggregate_docs(mat_docs)
    if readings_texts is not None:
        result["readings"] = _aggregate_docs(readings_texts)
    return result


def _load_union_or_base(base_only: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    frag_path = ROOT / "state" / "fragments.jsonl"
    mat_path = ROOT / "state" / "materials.jsonl"
    if base_only:
        frags = [
            json.loads(line)
            for line in frag_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        mats = [
            json.loads(line)
            for line in mat_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return frags, mats
    errors: list[str] = []
    frags_map = ledger_io.load_jsonl_union(frag_path, "fragment_id", errors, root=ROOT)
    mats_map = ledger_io.load_jsonl_union(mat_path, "material_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger error: " + "; ".join(errors))
    return list(frags_map.values()), list(mats_map.values())


def _load_readings() -> list[tuple[str, str]]:
    rdir = ROOT / "readings"
    if not rdir.is_dir():
        return []
    out: list[tuple[str, str]] = []
    for p in sorted(rdir.glob("*.md")):
        out.append((p.name, p.read_text(encoding="utf-8")))
    return out


def format_report(data: dict[str, Any], *, show_kwic: bool = False) -> str:
    lines: list[str] = []
    lines.append(
        "=== 愛・恋・友愛と代替可能な窓口の鏡 — 単数の他者と役割枠を測る（採点ではありません） ==="
    )
    fp = data["fragments_prose"]
    fq = data["fragments_quotes"]
    lines.append(
        f"断片: {data['fragment_count']} 編 (地の文 {fp['char_total']:,} 字 / 引用内 {fq['char_total']:,} 字)"
    )
    lines.append("")
    lines.append("--- 1. 断片（地の文 vs 引用内）の5群比較 ---")
    for g in data["group_order"]:
        gp = fp["groups"][g]
        gq = fq["groups"][g]
        terms_str = ", ".join(f"{k}×{v}" for k, v in list(gp["by_term"].items())[:6])
        lines.append(
            f"  [{gp['label']}] 地の文={gp['count']}回 ({gp['doc_count']}編, {gp['per_10k_chars']}/10k字) "
            f"| 引用内={gq['count']}回 ({gq['doc_count']}編)"
            + (f"  [{terms_str}]" if terms_str else "")
        )

    if "materials" in data:
        mp = data["materials"]
        lines.append("")
        lines.append(f"--- 2. 素材（{mp['doc_total']:,} 件 / {mp['char_total']:,} 字） ---")
        for g in data["group_order"]:
            gm = mp["groups"][g]
            terms_str = ", ".join(f"{k}×{v}" for k, v in list(gm["by_term"].items())[:6])
            lines.append(
                f"  [{gm['label']}] {gm['count']}回 ({gm['doc_count']}件, {gm['per_10k_chars']}/10k字)"
                + (f"  [{terms_str}]" if terms_str else "")
            )

    if "readings" in data:
        rp = data["readings"]
        lines.append("")
        lines.append(f"--- 3. 精読報告（{rp['doc_total']} 本 / {rp['char_total']:,} 字） ---")
        for g in data["group_order"]:
            gr = rp["groups"][g]
            lines.append(
                f"  [{gr['label']}] {gr['count']}回 ({gr['doc_count']}本, {gr['per_10k_chars']}/10k字)"
            )

    lines.append("")
    lines.append("--- 4. 断片の地の文における生字「恋・慕・愛・友」全数点検 ---")
    for ch in RAW_KANJI:
        entries = data["raw_kanji_kwic"][ch]
        lines.append(f"  生字『{ch}』: {len(entries)} 箇所")
        if show_kwic or len(entries) <= 10:
            for e in entries:
                lines.append(f"    - {e['fragment_id']}: …{e['snippet']}…")

    lines.append("")
    lines.append("--- 読み方 ---")
    lines.append("  語形の不在は感情の欠如の証明ではなく、語形の出現も主観的愛着の証明ではない。")
    lines.append("  ただ、この書庫が『誰に』向かって書いてきたかの輪郭だけをここに映す。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON形式で出力する")
    parser.add_argument("--kwic", action="store_true", help="生字KWICを全件表示する")
    parser.add_argument("--base-only", action="store_true", help="凍結ベースのみを対象にする")
    args = parser.parse_args(argv)

    frags, mats = _load_union_or_base(args.base_only)
    readings = _load_readings()
    data = measure_eros_audit(frags, mats, readings)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_report(data, show_kwic=args.kwic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
