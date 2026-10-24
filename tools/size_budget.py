#!/usr/bin/env python3
"""Check size budgets for the tracked files that grow with every session.

背景（docs/map-architecture.md §7）:
この書庫では「単一ファイルが全成長を吸収する」ことが READING_MAP.md 36.9MB の
事故で確認された。予防のため、同じ病になりやすい追跡ファイルに予算を置く。

予算（バイト）::

    README.md               soft 150,000    hard 300,000
    READING_MAP.md          soft 2,000,000   hard 5,000,000
    state/<collection>.jsonl（各モノリス） soft 5,000,000  hard 10,000,000

- soft 超過 : WARN を表示。README はローテーション（docs/sessions.md へ移動）の、
  モノリスは生成物化（shard を正本に）の合図。--strict では exit 1。
- hard 超過 : 常に exit 1（CI が停止）。移行が済むまでマージしない。

リポジトリ全体のサイズ（git pack）は参考値として表示するのみ。指針は 1GB
（docs/map-architecture.md §6 参照）。

使い方::

    python3 tools/size_budget.py            # 予算どおり（hard 超過のみ失敗）
    python3 tools/size_budget.py --strict   # WARN も失敗にする
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_seed import ROOT

# (表示名, パス（root からの相対。glob 可）, soft, hard)
FILE_BUDGETS: tuple[tuple[str, str, int, int], ...] = (
    ("README.md", "README.md", 150_000, 300_000),
    ("READING_MAP.md", "READING_MAP.md", 2_000_000, 5_000_000),
    ("state/*.jsonl（モノリス）", "state/*.jsonl", 5_000_000, 10_000_000),
)

REPO_SOFT = 500_000_000  # 参考値：GitHub 指針は 1GB 未満推奨


def check_files(root: Path) -> tuple[list[str], bool, bool]:
    """Return (report lines, any_warn, any_fail) for every budgeted file."""
    lines: list[str] = []
    any_warn = False
    any_fail = False
    for label, pattern, soft, hard in FILE_BUDGETS:
        matches = sorted(root.glob(pattern)) if any(ch in pattern for ch in "*?[") else [root / pattern]
        if not matches:
            lines.append(f"  - {label}: 対象なし（スキップ）")
            continue
        for path in matches:
            if not path.is_file():
                continue
            size = path.stat().st_size
            if size >= hard:
                status = "FAIL"
                any_fail = True
            elif size >= soft:
                status = "WARN"
                any_warn = True
            else:
                status = "OK"
            try:
                shown = str(path.relative_to(root))
            except ValueError:
                shown = path.name
            lines.append(
                "  - {label}: {size:,} B / soft {soft:,} / hard {hard:,} → {status}".format(
                    label=shown,
                    size=size,
                    soft=soft,
                    hard=hard,
                    status=status,
                )
            )
    return lines, any_warn, any_fail


def repo_pack_bytes(root: Path) -> int | None:
    """git pack size in bytes, or None when git is unavailable."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "count-objects", "-v"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        if line.startswith("size-pack:"):
            return int(line.split()[1]) * 1024
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="treat WARN as failure")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = parser.parse_args(argv)

    root = args.root
    lines, any_warn, any_fail = check_files(root)

    print("size budgets:")
    for line in lines:
        print(line)

    pack = repo_pack_bytes(root)
    if pack is not None:
        note = "（指針 1GB。超過時は docs/map-architecture.md §6 の留保を参照）"
        mark = " WARN" if pack >= REPO_SOFT else ""
        print(f"  - git pack（参考値）: {pack:,} B{mark} {note}")

    if any_fail:
        print("FAIL: hard size budget exceeded — 移行（ローテーション／生成物化）が済むまでマージしない")
        return 1
    if any_warn and args.strict:
        print("FAIL (--strict): soft size budget exceeded — ローテーション／生成物化を検討する")
        return 1
    if any_warn:
        print("WARN: soft size budget exceeded — ローテーション／生成物化の合図（docs/map-architecture.md §7）")
        return 0
    print("PASS: all size budgets are within soft limits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
