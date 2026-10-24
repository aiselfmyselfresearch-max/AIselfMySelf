#!/usr/bin/env python3
"""Report the bibliographic verification state of every material (stdlib only).

Added in SESSION-027 after MAT-TRC-004 showed that `validate_seed.py`
checks schema and reference integrity but never opens a URL, so a
fabricated book title passes validation. This tool does not decide truth;
it only makes the *state of checking* visible.

Usage:
  python3 tools/cite_check.py
  python3 tools/cite_check.py --status unverified
  python3 tools/cite_check.py --check-urls        # opt-in, needs network
  python3 tools/cite_check.py --strict            # exit 1 if any unverified
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_seed import ROOT, load_jsonl  # noqa: E402

STATUS_ORDER = ["verified", "partially_verified", "corrected", "unverified", "unrecorded"]
STATUS_LABELS = {
    "verified": "照合済み（一次情報と一致）",
    "partially_verified": "部分照合（一部のみ確認）",
    "corrected": "訂正済み（誤りを発見し修正）",
    "unverified": "未照合（記録はあるが未確認）",
    "unrecorded": "未記録（verification 欄なし）",
}


def load_materials() -> dict[str, dict]:
    errors: list[str] = []
    return load_jsonl(ROOT / "state" / "materials.jsonl", "material_id", errors)


def status_of(record: dict) -> str:
    ver = record.get("verification")
    if not isinstance(ver, dict):
        return "unrecorded"
    return ver.get("status", "unrecorded")


def url_problems(record: dict) -> list[str]:
    url = record.get("source", {}).get("url", "")
    problems: list[str] = []
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        problems.append("URL が http(s) でない")
    if not parsed.netloc:
        problems.append("URL にホストがない")
    return problems


def probe(url: str, timeout: float = 8.0) -> str:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "AIselfMySelf-cite-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405):  # HEAD refused; not evidence of absence
            return f"HTTP {exc.code}（HEAD 拒否・到達は不明）"
        return f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return f"到達失敗: {exc.reason}"
    except Exception as exc:  # noqa: BLE001 - report, do not crash
        return f"失敗: {type(exc).__name__}"


def main() -> int:
    parser = argparse.ArgumentParser(description="報告書誌の照合状態（採点はしません）")
    parser.add_argument("--status", choices=STATUS_ORDER, help="この状態の素材だけを表示")
    parser.add_argument("--check-urls", action="store_true", help="URL へ HEAD を送る（ネットワーク使用）")
    parser.add_argument("--strict", action="store_true", help="未照合が1件でもあれば終了コード1")
    args = parser.parse_args()

    materials = load_materials()
    counts = Counter(status_of(m) for m in materials.values())
    total = len(materials)

    print("=== 書誌照合の台帳 — material ごとの verification 状態 ===")
    print(f"対象: state/materials.jsonl {total} 件\n")
    for status in STATUS_ORDER:
        if counts[status]:
            print(f"  {STATUS_LABELS[status]:<28} {counts[status]:>3} 件")
    checked = counts["verified"] + counts["partially_verified"] + counts["corrected"]
    print(f"\n  照合に関与した件数: {checked}/{total}（採点ではありません。状態の内訳にすぎません）")

    by_method: dict[str, list[str]] = defaultdict(list)
    for mid, record in materials.items():
        by_method[(record.get("verification") or {}).get("method", "未記録")].append(mid)
    print("\n--- 照合の方法ごと ---")
    for method, ids in sorted(by_method.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(ids):>3} 件 | {method}")

    broken = [(mid, url_problems(m)) for mid, m in materials.items() if url_problems(m)]
    print(f"\n--- URL の形式に問題のある素材: {len(broken)} 件 ---")
    for mid, problems in broken:
        print(f"  {mid}: {'; '.join(problems)}")

    corpus: dict[str, list[str]] = defaultdict(list)
    for mid, m in materials.items():
        corpus[m.get("source", {}).get("url", "")].append(mid)
    dupes = {url: ids for url, ids in corpus.items() if len(ids) > 1}
    if dupes:
        print("\n--- 同じ URL を共有する素材（同一出典の別抜粋か、貼り間違いか） ---")
        for url, ids in dupes.items():
            print(f"  {url} <- {', '.join(sorted(ids))}")

    targets = [m for s, m in materials.items() if not args.status or status_of(m) == args.status]
    target_ids = [mid for mid, m in materials.items() if not args.status or status_of(m) == args.status]
    print(f"\n--- 明細（{len(targets)} 件） ---")
    for mid, record in sorted(zip(target_ids, targets)):
        ver = record.get("verification") or {}
        line = f"  {mid:<26} {status_of(record):<19} {record.get('source', {}).get('authors', [''])[0][:22]:<22}"
        line += f" {(record.get('title') or '')[:34]}"
        print(line)
        note = ver.get("note")
        if note and args.status:
            print(f"      -> {note}")

    if args.check_urls:
        print("\n--- URL 到達確認（HEAD） ---")
        for mid, record in sorted(materials.items()):
            if args.status and status_of(record) != args.status:
                continue
            url = record.get("source", {}).get("url", "")
            print(f"  {mid:<26} {probe(url):<24} {url[:70]}")

    if args.strict:
        unresolved = counts["unverified"] + counts["unrecorded"]
        if unresolved:
            print(f"\nSTRICT: 未照合 {unresolved} 件が残っています（失敗ではなく、残っている測定量です）")
            return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # e.g. piped into `head`
        raise SystemExit(0)
