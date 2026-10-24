#!/usr/bin/env python3
"""Measure how this archive *repairs* a wrong sentence. A mirror, not a verdict.

SESSION-041 asks a question that can be counted before any new material is
chosen: **when this archive records an error, does the record name anyone the
error was owed to, and does the record ever close?** The ledgers already hold
``state/errata.jsonl`` — sixteen claims, verdicts and notes written by earlier
sessions. This tool reads that layer as data and counts what it does *not*
contain, without deciding whether any particular correction is right.

What is counted
---------------
``level``
    Who or what is being corrected: the fragment's prose (``本文``), the
    measuring instrument or a project trace (``計器・痕跡``), another errata
    record (``訂正録``), or a record that points at neither.
``corrected_by``
    Whether the record says which later fragment or errata entry carries the
    repair, and whether that target exists.
``chain``
    Corrections of corrections. A chain that terminates in an ``open`` record is
    a repair that has not landed; the tool reports the depth and the terminal
    status rather than resolving it.
``addressee``
    Whether any field or sentence names a party the error was owed to. The
    errata schema has no such field, so this counts words in ``claim`` and
    ``note`` as a weak secondary signal, clearly labelled as such.
``remedy``
    Whether the record states an action (rewrite, withdraw, relabel, apologise,
    compensate) beyond describing the error.
``reproducibility``
    Whether the ``check`` block carries enough to re-run the measurement
    (``manual`` checks and missing ``as_of_*`` / range parameters are listed).
``recheck``
    The recorded checks are re-run against the current union of base and shards,
    and the recorded value is compared with the recomputed one. A mismatch is
    drift or error; the tool does not say which.

Calibration notes
-----------------
  - Every count is a count of word forms or JSON fields. A zero for 宛先 means
    the specified words and keys are absent, not that no reader was owed an
    explanation.
  - Keyword scanning of Japanese prose over-counts (償 in 償還, 相手 in 相談相手)
    and under-counts (silence). The tool prints the matching strings.
  - ``--base-only`` and ``--exclude-shard`` reproduce a count taken before this
    session wrote anything, as in the other mirrors.

Usage:
  python3 tools/repair_audit.py
  python3 tools/repair_audit.py --json
  python3 tools/repair_audit.py --base-only
  python3 tools/repair_audit.py --exclude-shard 8f21c0d4be77
  python3 tools/repair_audit.py --show ERR-015
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402
import errata_audit  # noqa: E402

ERRATA = ROOT / "state" / "errata.jsonl"
FRAGMENTS = ROOT / "state" / "fragments.jsonl"
MATERIALS = ROOT / "state" / "materials.jsonl"

ADDRESSEE_WORDS = ("宛先", "宛名", "相手", "被害", "被った", "読者へ", "あなたへ", "誰に", "誰の")
REMEDY_WORDS = ("訂正した", "訂正する", "書き換え", "差し替え", "撤回", "取り消", "謝罪", "陳謝",
                "弁明", "弁償", "賠償", "償い", "贖", "許し", "赦し", "免責", "復旧", "修理")
PRESERVED_WORDS = ("書き換えない", "残す", "保存", "そのまま")


def load(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def shard_paths(base: Path, exclude: str | None) -> list[Path]:
    paths = sorted(base.parent.joinpath(base.stem + ".d").glob("*.jsonl"))
    if exclude:
        paths = [path for path in paths if exclude not in path.name]
    return paths


def load_union(base: Path, exclude: str | None, base_only: bool = False) -> list[dict[str, Any]]:
    paths = [base] if base_only else [base, *shard_paths(base, exclude)]
    records: list[dict[str, Any]] = []
    for path in paths:
        records.extend(load(path))
    return records


def level_of(record: dict[str, Any]) -> str:
    subject = str(record.get("subject_id") or "")
    if subject.startswith("ERR-"):
        return "訂正録"
    if record.get("subject_type") == "material" or subject.startswith(("MAT-", "SRC-")):
        return "計器・痕跡"
    if record.get("fragment_id"):
        return "本文"
    return "特定なし"


def keyword_hits(text: str, words: tuple[str, ...]) -> list[str]:
    return [word for word in words if word in text]


def chains(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {r["errata_id"]: r for r in records}
    edges: dict[str, str] = {}
    for record in records:
        subject = str(record.get("subject_id") or "")
        if subject.startswith("ERR-") and subject in by_id:
            edges[subject] = record["errata_id"]

    def walk(start: str) -> tuple[int, str, list[str]]:
        seen = [start]
        node = start
        while node in edges and edges[node] not in seen:
            node = edges[node]
            seen.append(node)
        return len(seen) - 1, by_id[node].get("status", ""), seen

    detail = []
    for subject, corrector in edges.items():
        depth, terminal_status, path = walk(subject)
        detail.append({
            "from": subject,
            "to": corrector,
            "depth": depth,
            "terminal_status": terminal_status,
            "path": path,
        })
    return {
        "edges": len(edges),
        "depth_max": max((d["depth"] for d in detail), default=0),
        "open_terminals": sum(1 for d in detail if d["terminal_status"] == "open"),
        "detail": detail,
    }


def repro(record: dict[str, Any]) -> dict[str, Any]:
    check = record.get("check") or {}
    params = check.get("params") or {}
    kind = check.get("kind", "")
    has_range = any(key in params for key in ("from", "to", "as_of_fragments", "as_of_materials"))
    manual = kind == "manual"
    return {
        "kind": kind,
        "params": params,
        "manual": manual,
        "has_range": has_range,
        "referenced_object": has_range,
    }


def audit(base_only: bool = False, exclude: str | None = None, recheck: bool = True) -> dict[str, Any]:
    errata = load_union(ERRATA, exclude, base_only)
    fragments = load_union(FRAGMENTS, exclude, base_only)
    materials = load_union(MATERIALS, exclude, base_only)
    frag_ids = {f["fragment_id"] for f in fragments}

    levels = Counter(level_of(r) for r in errata)
    matrix = Counter((r.get("verdict", ""), r.get("status", "")) for r in errata)

    corrected_by = Counter()
    dangling: list[str] = []
    for record in errata:
        target = str(record.get("corrected_by") or "")
        if not target:
            corrected_by["空"] += 1
        elif target.startswith("ERR-"):
            corrected_by["訂正録"] += 1
        elif target in frag_ids:
            corrected_by["断片（現存）"] += 1
        else:
            corrected_by["断片（不在）"] += 1
            dangling.append(f"{record['errata_id']}->{target}")

    addressee_rows = []
    remedy_rows = []
    preserved_rows = []
    for record in errata:
        text = f"{record.get('claim', '')}\n{record.get('note', '')}"
        hits = keyword_hits(text, ADDRESSEE_WORDS)
        remedy = keyword_hits(text, REMEDY_WORDS)
        preserved = keyword_hits(text, PRESERVED_WORDS)
        if hits:
            addressee_rows.append({"errata_id": record["errata_id"], "words": hits})
        if remedy:
            remedy_rows.append({"errata_id": record["errata_id"], "words": remedy})
        if preserved:
            preserved_rows.append({"errata_id": record["errata_id"], "words": preserved})

    subjects = sorted({str(r.get("subject_id")) for r in errata if str(r.get("subject_id") or "").startswith("ERR-")})
    records_with_reproducibility = sum(1 for r in errata if repro(r)["has_range"])
    manual = sum(1 for r in errata if repro(r)["manual"])

    recheck_rows = []
    if recheck:
        for record in errata:
            try:
                result = errata_audit.run_check(record.get("check") or {}, fragments, materials)
            except Exception as exc:  # the mirror must not fail the whole audit
                recheck_rows.append({"errata_id": record["errata_id"], "measurable": False,
                                     "detail": f"再実行できなかった: {exc}"})
                continue
            recheck_rows.append({"errata_id": record["errata_id"], **result})

    return {
        "errata": len(errata),
        "fragments": len(fragments),
        "levels": dict(levels),
        "matrix": {f"{v}/{s}": n for (v, s), n in sorted(matrix.items())},
        "corrected_by": dict(corrected_by),
        "dangling": dangling,
        "chains": chains(errata),
        "addressee": {"fields": 0, "word_hits": addressee_rows},
        "remedy": {"word_hits": remedy_rows},
        "preserved": {"word_hits": preserved_rows},
        "reproducibility": {
            "manual_checks": manual,
            "with_object_range": records_with_reproducibility,
            "without_object_range": len(errata) - records_with_reproducibility,
        },
        "errata_subjects": subjects,
        "recheck": recheck_rows,
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 修復の鏡 — この書庫は誤りをどう償うか（採点ではありません） ===")
    add(f"対象: errata {data['errata']} 件 / 断片 {data['fragments']} 編（メタデータを除く）")
    add("")
    add("--- 1. 何が訂正されているか（訂正の対象の層） ---")
    for level, count in sorted(data["levels"].items(), key=lambda kv: -kv[1]):
        add(f"  {level:<8}: {count:>2} 件")
    add("")
    add("--- 2. 判定と状態 ---")
    for key, count in sorted(data["matrix"].items()):
        add(f"  {key:<22}: {count:>2} 件")
    add("")
    add("--- 3. 訂正の引き受け先（corrected_by） ---")
    for key, count in sorted(data["corrected_by"].items(), key=lambda kv: -kv[1]):
        add(f"  {key:<12}: {count:>2} 件")
    if data["dangling"]:
        add(f"  不在の参照: {', '.join(data['dangling'])}")
    add("")
    add("--- 4. 訂正の訂正（連鎖） ---")
    chain = data["chains"]
    add(f"  連鎖 {chain['edges']} 本 / 最大の深さ {chain['depth_max']} / 末端が open のもの {chain['open_terminals']} 本")
    for row in chain["detail"]:
        add(f"  {row['from']} → {row['to']}（深さ {row['depth']}・末端 {row['terminal_status']}）: {' → '.join(row['path'])}")
    add("")
    add("--- 5. 宛先（誰に詫びるか） ---")
    add(f"  スキーマの欄: {data['addressee']['fields']} 件（errata.schema.json に宛先・被害者の欄はない）")
    add(f"  語の拾い（弱い信号）: {data['addressee']['word_hits'] or 'なし'}")
    add("")
    add("--- 6. 償いの動作 ---")
    add(f"  語の拾い: {data['remedy']['word_hits'] or 'なし'}")
    add(f"  保存の語: {data['preserved']['word_hits'] or 'なし'}")
    add("")
    add("--- 7. 再実行の条件 ---")
    repro = data["reproducibility"]
    add(f"  手続き未記録（manual）: {repro['manual_checks']} 件")
    add(f"  測定対象の範囲（from/to/as_of_*）あり: {repro['with_object_range']} 件 / なし: {repro['without_object_range']} 件")
    add("")
    add("--- 8. 記録の再実行（現在の台帳に対して） ---")
    for row in data["recheck"]:
        value = row.get("value", "—")
        add(f"  {row['errata_id']:<8} 今回={value}  {row.get('detail', '')[:90]}")
    add("")
    add("--- 9. 読むための注意 ---")
    add("  ・見出しの語（宛先・償い）は、句のなかの文字列を拾っただけであり、謝罪の有無の判定ではない。")
    add("  ・「訂正録」の層は本文を書き換えない。欄の不在は、詫びる相手がいないことの証明ではない。")
    add("  ・連鎖の末端が open であることは、修復の失敗の証明ではない。閉じないことを選んだ記録でもある。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repair, addressee and errata-chain audit")
    parser.add_argument("--json", action="store_true", help="dump the raw audit as JSON")
    parser.add_argument("--base-only", action="store_true",
                        help="measure only the frozen base files, not the shards")
    parser.add_argument("--exclude-shard", metavar="SUFFIX",
                        help="ignore shards whose filename contains SUFFIX")
    parser.add_argument("--no-recheck", action="store_true", help="skip re-running the recorded checks")
    parser.add_argument("--show", metavar="ERR_ID", help="show one errata record with its audit row")
    args = parser.parse_args(argv)

    data = audit(base_only=args.base_only, exclude=args.exclude_shard, recheck=not args.no_recheck)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(report(data))
    if args.show:
        records = {r["errata_id"]: r for r in load_union(ERRATA, args.exclude_shard, args.base_only)}
        record = records.get(args.show)
        if record is None:
            print(f"\n{args.show} は見つからない", flush=True)
            return 1
        print("")
        print(f"--- {args.show} ---")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        row = next((r for r in data["recheck"] if r["errata_id"] == args.show), None)
        if row:
            print(f"今回の再実行: {row.get('value')}  {row.get('detail', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
