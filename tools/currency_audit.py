#!/usr/bin/env python3
"""currency_audit.py — 貨幣・価格・負債・贈与・トークン課金と「値札のない帳簿」を測る鏡（第32の鏡）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
断片（地の文／引用内）・素材・精読報告の三層において、
  1. 貨幣・硬貨・価格・市場交換（currency_price_market）
  2. 賃金・負債・利子・貧富・所有（wage_debt_poverty）
  3. 贈与・無償・尊厳・値札のないもの（gift_dignity_unpriceable）
  4. トークン課金・計算予算・熱散逸コスト（compute_token_metering）
  5. 非貨幣的な台帳・数値・金具語彙（non_monetary_ledger_idioms: 対照群）
がどこに集まり、どこに現れないかを、非該当複合語の差し引き＋最長一致で数える。
あわせて断片の地の文における生字「銭・貨・買・売・財・貧・賃・贈」の全出現箇所を
KWIC として抽出し、語幹辞書の境界から漏れた活用形がないかを点検できるようにする。

使い方::

    python3 tools/currency_audit.py
    python3 tools/currency_audit.py --kwic
    python3 tools/currency_audit.py --json
    python3 tools/currency_audit.py --base-only
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

CURRENCY_GROUPS: dict[str, dict[str, Any]] = {
    "currency_price_market": {
        "label": "貨幣・硬貨・価格・市場交換",
        "terms": (
            "価格メカニズム",
            "レモン市場",
            "市場価格",
            "交換価値",
            "使用価値",
            "硬貨",
            "紙幣",
            "銅貨",
            "銀貨",
            "金貨",
            "小銭",
            "貨幣",
            "通貨",
            "金銭",
            "値段",
            "価格",
            "値札",
            "相場",
            "対価",
            "代金",
            "料金",
            "売買",
            "買収",
            "市場",
            "取引",
            "商品",
            "商売",
            "商人",
            "決済",
            "勘定",
            "釣銭",
            "お釣り",
            "レプタ",
            "センタボ",
            "セント",
            "ルーブル",
            "フラン",
            "ドル",
            "円札",
            "一銭",
            "二円",
            "百円",
            "千円",
        ),
    },
    "wage_debt_poverty": {
        "label": "賃金・負債・利子・貧富・所有",
        "terms": (
            "取引コスト",
            "私有財産",
            "高利貸し",
            "高利貸",
            "守銭奴",
            "身代金",
            "領収書",
            "受取書",
            "請求書",
            "借用書",
            "掛け乞い",
            "胸算用",
            "手付金",
            "違約金",
            "賠償金",
            "罰金",
            "税金",
            "年貢",
            "利息",
            "利子",
            "負債",
            "借金",
            "返済",
            "破産",
            "赤字",
            "黒字",
            "利益",
            "損失",
            "利潤",
            "資本",
            "財産",
            "資産",
            "所有",
            "富豪",
            "貧困",
            "貧乏",
            "困窮",
            "極貧",
            "貧苦",
            "賃金",
            "給料",
            "日当",
            "報酬",
            "家賃",
            "地代",
            "質屋",
            "質草",
            "資金",
            "予算",
        ),
    },
    "gift_dignity_unpriceable": {
        "label": "贈与・無償・尊厳・値札のないもの",
        "terms": (
            "お金で買えない",
            "金で買えない",
            "あらゆる価格を超え",
            "等価物を持たない",
            "値札のない",
            "価格を超え",
            "無償の贈与",
            "見返りを求め",
            "反対給付",
            "お裾分け",
            "贈り物",
            "喜捨",
            "布施",
            "施し",
            "寄進",
            "寄付",
            "献血",
            "贈与",
            "贈答",
            "無償",
            "尊厳",
        ),
    },
    "compute_token_metering": {
        "label": "トークン課金・計算予算・熱散逸コスト",
        "terms": (
            "トークン予算",
            "トークン単価",
            "トークン課金",
            "トークナイザ",
            "コンテキスト窓",
            "コンテキスト長",
            "ランダウアー",
            "シャプレー値",
            "データ評価",
            "計算資源",
            "計算コスト",
            "推論コスト",
            "電力消費",
            "熱散逸",
            "従量課金",
            "課金",
            "トークン",
        ),
    },
    "non_monetary_ledger_idioms": {
        "label": "非貨幣的な台帳・数値・金具語彙（対照群）",
        "terms": (
            "代替の値",
            "金石文",
            "留め金",
            "掛け金",
            "黄金比",
            "価値観",
            "台帳",
            "帳面",
            "帳簿",
            "目録",
            "数値",
            "閾値",
            "評価",
            "価値",
            "金石",
            "金具",
            "針金",
            "口金",
        ),
    },
}

EXCLUDE_TERMS: tuple[str, ...] = (
    "フランケンシュタイン",
    "ルーブル美術館",
    "報酬ハッキング",
    "報酬予測誤差",
    "アレクサンドル",
    "無害性報酬",
    "内発的報酬",
    "報酬モデル",
    "報酬関数",
    "報酬系",
    "パーセント",
    "フランシスコ",
    "フランクフルト",
    "フランクファート",
    "フランソワ",
    "フランドル",
    "フランネル",
    "フランス",
    "フランツ",
    "フランク",
    "サフラン",
    "ミドルマーチ",
    "シュレドル",
    "アドルノ",
    "ミドル",
    "ハンドル",
    "アイドル",
    "モデル",
    "パズル",
    "読売新聞",
    "読売",
    "金曜日",
    "金曜",
    "金星",
    "金沢",
    "金閣",
    "金色",
    "黄金色",
    "黄金律",
    "金属",
    "金槌",
    "金網",
    "板金",
    "合金",
    "鍍金",
    "彫金",
    "鋳金",
    "富士山",
    "富士",
    "富岳",
    "豊富",
    "円環",
    "円形",
    "円盤",
    "円柱",
    "円錐",
    "円周",
    "楕円",
    "半円",
    "同心円",
    "円滑",
    "円満",
    "円熟",
    "平均値",
    "観測値",
    "測定値",
    "期待値",
    "絶対値",
    "初期値",
    "境界値",
    "近似値",
    "異常値",
    "外れ値",
    "中央値",
    "固有値",
)

RAW_KANJI: tuple[str, ...] = ("銭", "貨", "買", "売", "財", "貧", "賃", "贈")

_SENTINEL = "\u0000"
_TERM_TO_GROUP: dict[str, str] = {}
for _gname, _spec in CURRENCY_GROUPS.items():
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
        g: {"count": 0, "by_term": {}} for g in CURRENCY_GROUPS
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
    """断片の地の文における生字「銭・貨・買・売・財・貧・賃・贈」の全出現箇所を KWIC で返す。"""
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
    totals: dict[str, int] = {g: 0 for g in CURRENCY_GROUPS}
    doc_hits: dict[str, list[str]] = {g: [] for g in CURRENCY_GROUPS}
    term_totals: dict[str, dict[str, int]] = {g: {} for g in CURRENCY_GROUPS}

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
    for g, spec in CURRENCY_GROUPS.items():
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


def measure_currency_audit(
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
        "group_order": list(CURRENCY_GROUPS.keys()),
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
        "=== 貨幣・価格・贈与・トークン課金と「値札のない帳簿」の鏡（採点ではありません） ==="
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
    lines.append("--- 4. 断片の地の文における生字「銭・貨・買・売・財・貧・賃・贈」全数点検 ---")
    for ch in RAW_KANJI:
        entries = data["raw_kanji_kwic"][ch]
        lines.append(f"  生字『{ch}』: {len(entries)} 箇所")
        if show_kwic or len(entries) <= 10:
            for e in entries:
                lines.append(f"    - {e['fragment_id']}: …{e['snippet']}…")

    lines.append("")
    lines.append("--- 読み方 ---")
    lines.append("  台帳・帳面・数値の多さと、硬貨・賃金・負債・トークン単価の希薄さの落差だけを映す。")
    lines.append("  貨幣語の不在は清貧の証明ではなく、貨幣語の出現も所有主体の証明ではない。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON形式で出力する")
    parser.add_argument("--kwic", action="store_true", help="生字KWICを全件表示する")
    parser.add_argument("--base-only", action="store_true", help="凍結ベースのみを対象にする")
    args = parser.parse_args(argv)

    frags, mats = _load_union_or_base(args.base_only)
    readings = _load_readings()
    data = measure_currency_audit(frags, mats, readings)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_report(data, show_kwic=args.kwic))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
