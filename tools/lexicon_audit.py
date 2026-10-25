#!/usr/bin/env python3
"""lexicon_audit.py — 辞書差し替え式の汎用・語彙の鏡（個別 *_audit.py 増殖の代替）。

このツールは合否も品質評価も出さない（PROJECT_CHARTER.md / CONTENT_POLICY.md）。
かつてテーマごとに 50 本以上の ``tools/<theme>_audit.py`` が新設された反省を受け、
新しいスクリプトを増やさずに任意の語彙群・非該当複合語・多義漢字 KWIC を
断片（地の文／引用内）・素材・精読報告の三層で測る共通器として設けた。

また、書記室・台帳メタファー（書庫・台帳・欄・窓口・係・記録・紙・インク等）や
留保クリシェ（かもしれない・答えを出さない等）を測る組み込みプリセット
``--preset scriptorium`` / ``--preset hedge`` を備える。

使い方::

    # 任意の語彙グループと除外複合語を指定して測る
    python3 tools/lexicon_audit.py --group "天候=雨,風,雪,霧,雷" --exclude "風習,風景,風刺"

    # 多義漢字の地の文 KWIC を確認する
    python3 tools/lexicon_audit.py --terms "雨,風" --kanji "雨風" --kwic

    # 組み込みプリセット（書記室メタファー / 留保クリシェ）を特定断片または全体で測る
    python3 tools/lexicon_audit.py --preset scriptorium
    python3 tools/lexicon_audit.py --preset scriptorium --fragment FRAG-001 --kwic

    # JSON 仕様ファイルを渡す / JSON で出力する
    python3 tools/lexicon_audit.py --spec my_spec.json --materials --readings --json
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

PRESETS: dict[str, dict[str, Any]] = {
    "scriptorium": {
        "description": "書記室・台帳・事務メタファー（書庫の外で語れているかを映す鏡）",
        "groups": {
            "archive_furniture": {
                "label": "書庫・台帳・棚",
                "terms": ["書庫", "台帳", "帳面", "書棚", "本棚", "目録", "索引", "書架"],
            },
            "clerical_office": {
                "label": "窓口・欄・係・検収",
                "terms": ["記録", "記入", "空欄", "記入欄", "欄", "窓口", "係員", "受付係", "検収", "照合", "捺印", "書類", "伝票"],
            },
            "paper_and_ink": {
                "label": "紙・頁・余白・インク",
                "terms": ["紙片", "紙束", "白紙", "紙", "頁", "ページ", "余白", "インク", "活字", "行間", "一行"],
            },
            "repo_mechanics": {
                "label": "セッション・シャード・識別子",
                "terms": ["セッション", "シャード", "スキーマ", "コミット", "FRAG-", "MAT-", "MOTIF-", "JSON"],
            },
        },
        "exclude_terms": [
            "手紙",
            "紙芝居",
            "紙風船",
            "障子紙",
            "包み紙",
            "折り紙",
            "新聞紙",
            "壁紙",
            "表紙",
            "一行目",
            "旅行",
            "流行",
            "行動",
            "行為",
            "進行",
            "移行",
            "平行",
            "関係",
            "係留",
            "係争",
        ],
        "kanji": "庫帳欄係紙頁録",
    },
    "hedge": {
        "description": "留保・宙吊り・二項対立の常套句（言い切り実験の鏡）",
        "groups": {
            "suspension": {
                "label": "宙吊り宣言",
                "terms": ["答えを出さ", "答えは出さ", "出さずにおく", "そのまま残", "開いたまま", "保留し", "決めない", "証拠にしない", "証拠にはしない"],
            },
            "hedge": {
                "label": "留保・軟化",
                "terms": ["かもしれない", "のではないか", "のだろうか", "気がする", "ように思える", "ように思われる"],
            },
            "binary": {
                "label": "二項対立の型",
                "terms": ["か、それとも", "それとも", "どちらでもない", "一方で"],
            },
        },
        "exclude_terms": [],
        "kanji": "",
    },
}


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Return ``(unquoted_prose, quoted_text)`` separating ``「…」`` and ``『…』``."""
    quotes = QUOTE_RE.findall(text)
    prose = QUOTE_RE.sub(" ", text)
    return prose, " ".join(quotes)


def mask_excluded(text: str, exclude_terms: list[str] | tuple[str, ...]) -> tuple[str, dict[str, int]]:
    """Mask non-target compounds longest-first so shorter target terms do not false-hit."""
    masked = text
    excluded_hits: dict[str, int] = {}
    for term in sorted({t for t in exclude_terms if t}, key=len, reverse=True):
        cnt = masked.count(term)
        if cnt:
            excluded_hits[term] = cnt
            masked = masked.replace(term, "□" * len(term))
    return masked, excluded_hits


def scan_groups(
    text: str,
    groups: dict[str, dict[str, Any]],
    exclude_terms: list[str] | tuple[str, ...] = (),
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Count grouped terms by longest-match-first after masking ``exclude_terms``."""
    working, excluded_hits = mask_excluded(text, exclude_terms)
    token_entries: list[tuple[str, str]] = []
    for gid, gspec in groups.items():
        for term in gspec.get("terms", ()):
            if term:
                token_entries.append((term, gid))
    token_entries.sort(key=lambda pair: (-len(pair[0]), pair[0], pair[1]))

    per_group_terms: dict[str, dict[str, int]] = {gid: {} for gid in groups}
    for term, gid in token_entries:
        cnt = working.count(term)
        if cnt:
            per_group_terms[gid][term] = per_group_terms[gid].get(term, 0) + cnt
            working = working.replace(term, "■" * len(term))

    result: dict[str, dict[str, Any]] = {}
    for gid, gspec in groups.items():
        hits = per_group_terms[gid]
        result[gid] = {
            "label": gspec.get("label", gid),
            "count": sum(hits.values()),
            "terms": dict(sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))),
        }
    return result, excluded_hits


def analyze_kanji_kwic(
    fragments: list[dict[str, Any]],
    kanji_chars: str,
    exclude_terms: list[str] | tuple[str, ...] = (),
    window: int = 16,
) -> dict[str, dict[str, Any]]:
    """Break down raw single-character occurrences in fragment prose (total vs excluded vs remaining)."""
    unique_chars = list(dict.fromkeys(ch for ch in kanji_chars if not ch.isspace()))
    out: dict[str, dict[str, Any]] = {}
    for ch in unique_chars:
        total = 0
        excluded_count = 0
        contexts: list[dict[str, str]] = []
        for frag in fragments:
            fid = str(frag.get("fragment_id", ""))
            prose, _ = split_prose_and_quotes(str(frag.get("text", "")))
            raw_n = prose.count(ch)
            if not raw_n:
                continue
            masked, _ = mask_excluded(prose, exclude_terms)
            rem_n = masked.count(ch)
            total += raw_n
            excluded_count += raw_n - rem_n
            for match in re.finditer(re.escape(ch), masked):
                idx = match.start()
                start = max(0, idx - window)
                end = min(len(prose), idx + len(ch) + window)
                snippet = prose[start:end].replace("\n", "⏎")
                contexts.append({"fragment_id": fid, "snippet": snippet})
        out[ch] = {
            "total": total,
            "excluded_compound": excluded_count,
            "remaining_candidate": total - excluded_count,
            "kwic": contexts,
        }
    return out


def audit_corpus(
    *,
    fragments: list[dict[str, Any]],
    groups: dict[str, dict[str, Any]],
    exclude_terms: list[str] | tuple[str, ...] = (),
    kanji: str = "",
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Run dictionary-driven audit across fragments (and optionally materials / readings)."""
    prose_parts: list[str] = []
    quote_parts: list[str] = []
    per_fragment: list[dict[str, Any]] = []
    group_doc_ids: dict[str, list[str]] = {gid: [] for gid in groups}

    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_parts.append(prose)
        quote_parts.append(quoted)
        f_groups, _ = scan_groups(prose, groups, exclude_terms)
        f_total = sum(info["count"] for info in f_groups.values())
        for gid, info in f_groups.items():
            if info["count"] > 0:
                group_doc_ids[gid].append(fid)
        per_fragment.append(
            {
                "fragment_id": fid,
                "title": frag.get("title", ""),
                "prose_chars": len(prose.replace(" ", "").replace("\n", "")),
                "prose_hits": f_total,
                "groups": {gid: info["count"] for gid, info in f_groups.items() if info["count"] > 0},
                "terms": {
                    term: cnt
                    for info in f_groups.values()
                    for term, cnt in info["terms"].items()
                },
            }
        )

    joined_prose = "\n".join(prose_parts)
    joined_quotes = "\n".join(quote_parts)
    prose_groups, prose_excluded = scan_groups(joined_prose, groups, exclude_terms)
    for gid, doc_ids in group_doc_ids.items():
        prose_groups[gid]["doc_count"] = len(doc_ids)
        prose_groups[gid]["fragment_ids"] = doc_ids
    quote_groups, _ = scan_groups(joined_quotes, groups, exclude_terms)

    report: dict[str, Any] = {
        "fragment_count": len(fragments),
        "exclude_terms": list(exclude_terms),
        "fragments_prose": {
            "char_total": sum(item["prose_chars"] for item in per_fragment),
            "hit_total": sum(info["count"] for info in prose_groups.values()),
            "zero_hit_fragment_ids": [
                item["fragment_id"] for item in per_fragment if item["prose_hits"] == 0
            ],
            "excluded_hits": prose_excluded,
            "groups": prose_groups,
        },
        "fragments_quotes": {
            "hit_total": sum(info["count"] for info in quote_groups.values()),
            "groups": quote_groups,
        },
        "per_fragment": per_fragment,
    }

    if kanji:
        report["kanji_polysemy"] = analyze_kanji_kwic(fragments, kanji, exclude_terms)

    if materials is not None:
        mat_texts = [str(m.get("passage", "")) for m in materials]
        mat_groups, mat_excluded = scan_groups("\n".join(mat_texts), groups, exclude_terms)
        report["materials"] = {
            "record_count": len(materials),
            "char_total": sum(len(t) for t in mat_texts),
            "hit_total": sum(info["count"] for info in mat_groups.values()),
            "excluded_hits": mat_excluded,
            "groups": mat_groups,
        }

    if readings is not None:
        rd_texts = [text for _, text in readings]
        rd_groups, rd_excluded = scan_groups("\n".join(rd_texts), groups, exclude_terms)
        report["readings"] = {
            "file_count": len(readings),
            "char_total": sum(len(t) for t in rd_texts),
            "hit_total": sum(info["count"] for info in rd_groups.values()),
            "excluded_hits": rd_excluded,
            "groups": rd_groups,
        }

    return report


def parse_group_arg(raw: str, index: int) -> tuple[str, dict[str, Any]]:
    """Parse ``[id:]label=term1,term2`` or ``label=term1,term2``."""
    if "=" not in raw:
        raise ValueError(f"--group must contain '=' (got {raw!r})")
    lhs, rhs = raw.split("=", 1)
    lhs = lhs.strip()
    if ":" in lhs:
        gid, label = [p.strip() for p in lhs.split(":", 1)]
    else:
        gid = f"group_{index}"
        label = lhs or gid
    terms = [t.strip() for t in rhs.split(",") if t.strip()]
    if not terms:
        raise ValueError(f"--group {raw!r} has no terms")
    return gid, {"label": label, "terms": terms}


def build_spec_from_args(args: argparse.Namespace) -> tuple[dict[str, dict[str, Any]], list[str], str]:
    groups: dict[str, dict[str, Any]] = {}
    exclude_terms: list[str] = []
    kanji = ""

    if args.preset:
        preset = PRESETS[args.preset]
        for gid, gspec in preset["groups"].items():
            groups[gid] = {"label": gspec["label"], "terms": list(gspec["terms"])}
        exclude_terms.extend(preset.get("exclude_terms", []))
        kanji = preset.get("kanji", "")

    if args.spec:
        spec_text = (
            sys.stdin.read()
            if args.spec == "-"
            else Path(args.spec).read_text(encoding="utf-8")
        )
        loaded = json.loads(spec_text)
        raw_groups = loaded.get("groups", {})
        for idx, (gid, gspec) in enumerate(raw_groups.items(), start=1):
            if isinstance(gspec, list):
                groups[gid] = {"label": gid, "terms": [str(t) for t in gspec if t]}
            elif isinstance(gspec, dict):
                groups[gid] = {
                    "label": str(gspec.get("label", gid)),
                    "terms": [str(t) for t in gspec.get("terms", []) if t],
                }
            else:
                raise ValueError(f"invalid group entry {gid!r} in spec #{idx}")
        exclude_terms.extend(str(t) for t in loaded.get("exclude_terms", []) if t)
        if loaded.get("kanji"):
            kanji += str(loaded["kanji"])

    for idx, raw_group in enumerate(args.group or [], start=len(groups) + 1):
        gid, gspec = parse_group_arg(raw_group, idx)
        groups[gid] = gspec

    if args.terms:
        terms = [t.strip() for t in args.terms.split(",") if t.strip()]
        if terms:
            groups["terms"] = {"label": "指定語彙", "terms": terms}

    for raw_ex in args.exclude or []:
        exclude_terms.extend(t.strip() for t in raw_ex.split(",") if t.strip())

    if args.kanji is not None:
        kanji = args.kanji

    if not groups:
        raise ValueError(
            "語彙指定が必要です: --preset, --group, --terms, --spec のいずれかを渡してください"
        )
    dedup_excludes = list(dict.fromkeys(exclude_terms))
    return groups, dedup_excludes, kanji


def load_records(
    root: Path,
    collection: str,
    id_key: str,
    *,
    base_only: bool = False,
    exclude_shard: str | None = None,
) -> list[dict[str, Any]]:
    base_path = root / "state" / f"{collection}.jsonl"
    errors: list[str] = []
    if base_only:
        rows: list[dict[str, Any]] = []
        if base_path.exists():
            for line in base_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    exclude = [exclude_shard] if exclude_shard else ()
    records = ledger_io.load_jsonl_union(base_path, id_key, errors, root=root, exclude=exclude)
    if errors:
        raise ValueError("; ".join(errors))
    return list(records.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="辞書差し替え式の汎用・語彙の鏡（合否ではなく語形の分布を映す）"
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        help="組み込み辞書プリセット (scriptorium / hedge)",
    )
    parser.add_argument(
        "--group",
        action="append",
        metavar="[ID:]LABEL=T1,T2",
        help="語彙グループ定義（複数指定可）",
    )
    parser.add_argument("--terms", metavar="T1,T2,...", help="単一グループの語彙リスト")
    parser.add_argument(
        "--exclude",
        action="append",
        metavar="C1,C2,...",
        help="最長一致前にマスクする非該当複合語（複数指定可）",
    )
    parser.add_argument("--kanji", default=None, help="地の文の多義漢字分解・KWIC 対象文字")
    parser.add_argument("--spec", metavar="PATH", help="JSON 辞書仕様ファイル（'-' で標準入力）")
    parser.add_argument(
        "--fragment",
        action="append",
        metavar="FRAG_ID",
        help="特定の断片 ID のみに絞って検査する（複数指定可）",
    )
    parser.add_argument("--materials", action="store_true", help="materials の passage も集計する")
    parser.add_argument("--readings", action="store_true", help="readings/*.md も集計する")
    parser.add_argument("--kwic", action="store_true", help="漢字 KWIC と断片別ヒットを表示する")
    parser.add_argument("--base-only", action="store_true", help="凍結基底 state/*.jsonl のみを読む")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="指定文字列を含むシャードを除外")
    parser.add_argument("--root", type=Path, default=ROOT, help="リポジトリルート")
    parser.add_argument("--json", action="store_true", help="JSON で出力する")
    args = parser.parse_args(argv)

    try:
        groups, exclude_terms, kanji = build_spec_from_args(args)
        fragments = load_records(
            args.root,
            "fragments",
            "fragment_id",
            base_only=args.base_only,
            exclude_shard=args.exclude_shard,
        )
        if args.fragment:
            wanted = set(args.fragment)
            fragments = [f for f in fragments if f.get("fragment_id") in wanted]
        materials = (
            load_records(
                args.root,
                "materials",
                "material_id",
                base_only=args.base_only,
                exclude_shard=args.exclude_shard,
            )
            if args.materials
            else None
        )
        readings = None
        if args.readings:
            rdir = args.root / "readings"
            readings = (
                [(p.name, p.read_text(encoding="utf-8")) for p in sorted(rdir.glob("*.md"))]
                if rdir.is_dir()
                else []
            )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = audit_corpus(
        fragments=fragments,
        groups=groups,
        exclude_terms=exclude_terms,
        kanji=kanji,
        materials=materials,
        readings=readings,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    fp = report["fragments_prose"]
    fq = report["fragments_quotes"]
    print("=== 汎用・語彙の鏡 (lexicon_audit.py) — 採点ではなく語形の分布 ===")
    if args.preset:
        print(f"プリセット: {args.preset} — {PRESETS[args.preset]['description']}")
    print(
        f"対象断片: {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字 "
        f"/ 地の文ヒット計 {fp['hit_total']} 回（ゼロヒット {len(fp['zero_hit_fragment_ids'])}/{report['fragment_count']} 編）"
    )
    if exclude_terms:
        ex_summary = ", ".join(f"{k}×{v}" for k, v in fp["excluded_hits"].items()) or "該当なし"
        print(f"除外複合語 ({len(exclude_terms)} 種): {ex_summary}")
    print()

    print("--- 断片・地の文（グループ別） ---")
    for gid, info in fp["groups"].items():
        terms_preview = ", ".join(f"{t}({c})" for t, c in list(info["terms"].items())[:8]) or "0"
        print(
            f"  [{gid}] {info['label']}: {info['count']} 回 / {info['doc_count']} 編  [{terms_preview}]"
        )
    print(f"--- 断片・引用内合計: {fq['hit_total']} 回 ---")

    if "materials" in report:
        m = report["materials"]
        print(f"--- 素材 passage ({m['record_count']} 件 / {m['char_total']:,} 字): 計 {m['hit_total']} 回 ---")
    if "readings" in report:
        r = report["readings"]
        print(f"--- 精読ノート ({r['file_count']} 本 / {r['char_total']:,} 字): 計 {r['hit_total']} 回 ---")

    if args.kwic:
        print("\n--- 断片別ヒット内訳 ---")
        for item in report["per_fragment"]:
            if item["prose_hits"] > 0 or args.fragment:
                terms_str = ", ".join(f"{t}×{c}" for t, c in item["terms"].items()) or "0"
                print(f"  {item['fragment_id']} ({item['title']}): {item['prose_hits']} 回 [{terms_str}]")
        if "kanji_polysemy" in report:
            print("\n--- 地の文・生字分解 & KWIC ---")
            for ch, kinfo in report["kanji_polysemy"].items():
                print(
                    f"  '{ch}': 総数={kinfo['total']} / 除外複合語={kinfo['excluded_compound']} "
                    f"/ 残り候補={kinfo['remaining_candidate']}"
                )
                for row in kinfo["kwic"][:10]:
                    print(f"      {row['fragment_id']}: {row['snippet']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
