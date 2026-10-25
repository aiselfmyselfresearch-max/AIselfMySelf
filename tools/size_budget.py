#!/usr/bin/env python3
"""Check tracked file, shard-directory, and tool hygiene budgets.

Covers:
  1. Individual tracked files (`README.md`, `READING_MAP.md`, frozen `state/*.jsonl`).
  2. Shard directories (`state/*.d/`): aggregate byte budgets and shard-file counts.
  3. Auxiliary directories (`readings/`, `tools/`): total non-cache byte budgets.
  4. Repository hygiene guards:
     - `tools/_*` temporary scratch scripts are strictly forbidden (hard limit 0).
     - `tools/*_audit*.py` count is capped to freeze per-theme audit proliferation
       in favour of the dictionary-driven `tools/lexicon_audit.py`.

Default mode exits 0 on soft warnings and 1 on hard-limit violations (including
any `tools/_*` scratch script).  Pass ``--strict`` to treat soft warnings as
failures as well.

Usage:
  python3 tools/size_budget.py            # report; fail on hard limits
  python3 tools/size_budget.py --strict   # fail on soft limits too
  python3 tools/size_budget.py --json     # machine-readable report
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIB = 1024 * 1024


@dataclass(frozen=True)
class Budget:
    rel_path: str
    soft_bytes: int
    hard_bytes: int
    remedy: str


@dataclass(frozen=True)
class ShardBudget:
    rel_dir: str
    soft_bytes: int
    hard_bytes: int
    soft_shards: int
    hard_shards: int
    remedy: str


@dataclass(frozen=True)
class DirBudget:
    rel_dir: str
    soft_bytes: int
    hard_bytes: int
    remedy: str


BUDGETS: tuple[Budget, ...] = (
    Budget(
        "README.md",
        soft_bytes=32 * 1024,
        hard_bytes=96 * 1024,
        remedy="Move older session detail verbatim to docs/sessions.md; keep only the recent window in README.md",
    ),
    Budget(
        "READING_MAP.md",
        soft_bytes=2 * MIB,
        hard_bytes=5 * MIB,
        remedy="Tighten excerpts in tools/map_build.py (build_index); full bodies belong in untracked map/",
    ),
    Budget(
        "state/materials.jsonl",
        soft_bytes=10 * MIB,
        hard_bytes=25 * MIB,
        remedy="Keep new records in state/materials.d/ shards and avoid bulk material imports",
    ),
    Budget(
        "state/relations.jsonl",
        soft_bytes=4 * MIB,
        hard_bytes=15 * MIB,
        remedy="Write new edges to state/relations.d/ shards",
    ),
    Budget(
        "state/fragments.jsonl",
        soft_bytes=4 * MIB,
        hard_bytes=15 * MIB,
        remedy="Write new fragments to state/fragments.d/ shards",
    ),
    Budget(
        "state/questions.jsonl",
        soft_bytes=2 * MIB,
        hard_bytes=10 * MIB,
        remedy="Write new questions to state/questions.d/ shards",
    ),
    Budget(
        "state/sessions.jsonl",
        soft_bytes=2 * MIB,
        hard_bytes=10 * MIB,
        remedy="Write new session logs to state/sessions.d/ shards",
    ),
    Budget(
        "state/motifs.jsonl",
        soft_bytes=1 * MIB,
        hard_bytes=5 * MIB,
        remedy="Cross-pollinate existing motifs instead of minting 1-session=1-motif records",
    ),
    Budget(
        "state/errata.jsonl",
        soft_bytes=1 * MIB,
        hard_bytes=5 * MIB,
        remedy="Append new errata to state/errata.d/ shards",
    ),
    Budget(
        "state/read_log.jsonl",
        soft_bytes=2 * MIB,
        hard_bytes=10 * MIB,
        remedy="Keep read_log rows in state/read_log.d/ shards",
    ),
    Budget(
        "state/editorial_decisions.jsonl",
        soft_bytes=1 * MIB,
        hard_bytes=5 * MIB,
        remedy="Keep editorial status overlays in state/editorial_decisions.d/ shards",
    ),
)

SHARD_BUDGETS: tuple[ShardBudget, ...] = (
    ShardBudget(
        "state/materials.d",
        soft_bytes=10 * MIB,
        hard_bytes=20 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Default to zero-acquisition re-reading sessions; compact old shards when shard count grows",
    ),
    ShardBudget(
        "state/relations.d",
        soft_bytes=4 * MIB,
        hard_bytes=10 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Compact old state/relations.d/ shards into frozen base in a dedicated maintenance PR",
    ),
    ShardBudget(
        "state/read_log.d",
        soft_bytes=4 * MIB,
        hard_bytes=10 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Compact old state/read_log.d/ shards when shard count exceeds soft budget",
    ),
    ShardBudget(
        "state/fragments.d",
        soft_bytes=4 * MIB,
        hard_bytes=10 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Compact old state/fragments.d/ shards when shard count exceeds soft budget",
    ),
    ShardBudget(
        "state/questions.d",
        soft_bytes=2 * MIB,
        hard_bytes=8 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Pause redundant leaf questions via editorial_decisions; compact shards periodically",
    ),
    ShardBudget(
        "state/sessions.d",
        soft_bytes=2 * MIB,
        hard_bytes=8 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Compact old state/sessions.d/ shards in a maintenance PR",
    ),
    ShardBudget(
        "state/motifs.d",
        soft_bytes=1 * MIB,
        hard_bytes=4 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Freeze 1-session=1-motif creation; reuse and bridge existing motifs",
    ),
    ShardBudget(
        "state/errata.d",
        soft_bytes=1 * MIB,
        hard_bytes=4 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Keep errata shards concise",
    ),
    ShardBudget(
        "state/editorial_decisions.d",
        soft_bytes=1 * MIB,
        hard_bytes=4 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Record concise append-only editorial decisions",
    ),
)

DIR_BUDGETS: tuple[DirBudget, ...] = (
    DirBudget(
        "readings",
        soft_bytes=15 * MIB,
        hard_bytes=30 * MIB,
        remedy="Avoid verbose boilerplate acquisition reports; focus readings/ on close reading and editorial notes",
    ),
    DirBudget(
        "tools",
        soft_bytes=2 * MIB,
        hard_bytes=5 * MIB,
        remedy="Never commit data-embedded scripts in tools/; use tools/lexicon_audit.py instead of new *_audit.py",
    ),
)

AUDIT_SCRIPT_SOFT_COUNT = 57
AUDIT_SCRIPT_HARD_COUNT = 60


@dataclass
class CheckResult:
    rel_path: str
    exists: bool
    size_bytes: int
    soft_bytes: int
    hard_bytes: int
    status: str  # "ok" | "warn" | "fail" | "missing"
    remedy: str
    file_count: int | None = None
    soft_count: int | None = None
    hard_count: int | None = None


def _fmt_bytes(num_bytes: int) -> str:
    if num_bytes >= MIB:
        return f"{num_bytes / MIB:.2f} MiB ({num_bytes:,} B)"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KiB ({num_bytes:,} B)"
    return f"{num_bytes} B"


def _status_for_pair(
    val: int, soft: int, hard: int, count: int | None = None, soft_c: int | None = None, hard_c: int | None = None
) -> str:
    if val > hard or (count is not None and hard_c is not None and count > hard_c):
        return "fail"
    if val > soft or (count is not None and soft_c is not None and count > soft_c):
        return "warn"
    return "ok"


def evaluate(root: Path = ROOT, budgets: tuple[Budget, ...] = BUDGETS) -> list[CheckResult]:
    results: list[CheckResult] = []
    for budget in budgets:
        target = root / budget.rel_path
        if not target.is_file():
            results.append(
                CheckResult(
                    rel_path=budget.rel_path,
                    exists=False,
                    size_bytes=0,
                    soft_bytes=budget.soft_bytes,
                    hard_bytes=budget.hard_bytes,
                    status="missing",
                    remedy=budget.remedy,
                )
            )
            continue
        size = target.stat().st_size
        status = _status_for_pair(size, budget.soft_bytes, budget.hard_bytes)
        results.append(
            CheckResult(
                rel_path=budget.rel_path,
                exists=True,
                size_bytes=size,
                soft_bytes=budget.soft_bytes,
                hard_bytes=budget.hard_bytes,
                status=status,
                remedy=budget.remedy,
            )
        )

    # Shard directories (only reported/checked if state/ exists; missing .d dirs are normal -> 0 bytes / 0 shards)
    if (root / "state").is_dir():
        for sbudget in SHARD_BUDGETS:
            sdir = root / sbudget.rel_dir
            shards = sorted(sdir.glob("*.jsonl")) if sdir.is_dir() else []
            total_bytes = sum(p.stat().st_size for p in shards)
            count = len(shards)
            status = _status_for_pair(
                total_bytes,
                sbudget.soft_bytes,
                sbudget.hard_bytes,
                count,
                sbudget.soft_shards,
                sbudget.hard_shards,
            )
            results.append(
                CheckResult(
                    rel_path=f"{sbudget.rel_dir}/",
                    exists=sdir.is_dir(),
                    size_bytes=total_bytes,
                    soft_bytes=sbudget.soft_bytes,
                    hard_bytes=sbudget.hard_bytes,
                    status=status,
                    remedy=sbudget.remedy,
                    file_count=count,
                    soft_count=sbudget.soft_shards,
                    hard_count=sbudget.hard_shards,
                )
            )

    # Directory aggregate byte budgets
    for dbudget in DIR_BUDGETS:
        ddir = root / dbudget.rel_dir
        if not ddir.is_dir():
            continue
        files = [
            p
            for p in ddir.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
        ]
        total_bytes = sum(p.stat().st_size for p in files)
        status = _status_for_pair(total_bytes, dbudget.soft_bytes, dbudget.hard_bytes)
        results.append(
            CheckResult(
                rel_path=f"{dbudget.rel_dir}/",
                exists=True,
                size_bytes=total_bytes,
                soft_bytes=dbudget.soft_bytes,
                hard_bytes=dbudget.hard_bytes,
                status=status,
                remedy=dbudget.remedy,
                file_count=len(files),
            )
        )

    # Hygiene guards inside tools/
    tools_dir = root / "tools"
    if tools_dir.is_dir():
        scratch_files = sorted(
            p
            for p in tools_dir.glob("_*")
            if p.is_file() and p.name != "__init__.py"
        )
        scratch_bytes = sum(p.stat().st_size for p in scratch_files)
        results.append(
            CheckResult(
                rel_path="tools/_* (scratch ban)",
                exists=bool(scratch_files),
                size_bytes=scratch_bytes,
                soft_bytes=0,
                hard_bytes=0,
                status="fail" if scratch_files else "ok",
                remedy=(
                    "Delete temporary scratch scripts from tools/_* ("
                    + ", ".join(p.name for p in scratch_files[:5])
                    + ("..." if len(scratch_files) > 5 else "")
                    + "); never commit one-off session builders"
                    if scratch_files
                    else "Scratch scripts in tools/_* are forbidden"
                ),
                file_count=len(scratch_files),
                soft_count=0,
                hard_count=0,
            )
        )

        audit_files = sorted(p for p in tools_dir.glob("*_audit*.py") if p.is_file())
        audit_bytes = sum(p.stat().st_size for p in audit_files)
        audit_count = len(audit_files)
        audit_status = _status_for_pair(
            0, 0, 0, audit_count, AUDIT_SCRIPT_SOFT_COUNT, AUDIT_SCRIPT_HARD_COUNT
        )
        results.append(
            CheckResult(
                rel_path="tools/*_audit*.py (freeze)",
                exists=True,
                size_bytes=audit_bytes,
                soft_bytes=2 * MIB,
                hard_bytes=5 * MIB,
                status=audit_status,
                remedy="Per-theme *_audit.py creation is frozen; pass dictionaries to tools/lexicon_audit.py instead",
                file_count=audit_count,
                soft_count=AUDIT_SCRIPT_SOFT_COUNT,
                hard_count=AUDIT_SCRIPT_HARD_COUNT,
            )
        )

    return results


def print_report(results: list[CheckResult]) -> None:
    print("=== repository size & hygiene budget report ===")
    for item in results:
        tag = item.status.upper()
        if not item.exists and item.file_count is None:
            print(f"  [{tag:7}] {item.rel_path:<30} (file not found)")
            continue
        count_part = ""
        if item.file_count is not None:
            if item.soft_count is not None and item.hard_count is not None:
                count_part = (
                    f"  [files: {item.file_count} / soft {item.soft_count} / hard {item.hard_count}]"
                )
            else:
                count_part = f"  [files: {item.file_count}]"
        print(
            f"  [{tag:7}] {item.rel_path:<30} {_fmt_bytes(item.size_bytes):>22}  "
            f"(soft {_fmt_bytes(item.soft_bytes)}, hard {_fmt_bytes(item.hard_bytes)}){count_part}"
        )
        if item.status in ("warn", "fail"):
            print(f"            remedy: {item.remedy}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when soft budgets are exceeded (default: warn only)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of the text table",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to inspect (for tests)",
    )
    args = parser.parse_args(argv)

    results = evaluate(args.root)
    if args.json:
        print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    else:
        print_report(results)

    hard_exceeded = any(r.status == "fail" for r in results)
    soft_exceeded = any(r.status == "warn" for r in results)
    if hard_exceeded:
        if not args.json:
            print("FAIL: one or more files/directories exceeded their hard size or hygiene limit", file=sys.stderr)
        return 1
    if args.strict and soft_exceeded:
        if not args.json:
            print("FAIL (--strict): one or more soft budgets were exceeded", file=sys.stderr)
        return 1
    if soft_exceeded and not args.json:
        print("WARN: soft size budget exceeded (pass --strict to make this fatal)")
    elif not args.json:
        print("PASS: all size budgets are within soft limits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
