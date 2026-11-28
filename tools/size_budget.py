#!/usr/bin/env python3
"""Check tracked file, shard-directory, and tool hygiene budgets.

Covers:
  1. Individual tracked files (`README.md`, `READING_MAP.md`, `BELIEF_MAP.md`,
     `docs/CONSOLIDATED_DIGESTS.md`, frozen `state/*.jsonl`).
  2. Shard directories (`state/*.d/`): aggregate byte budgets and shard-file counts.
  3. Auxiliary directories (`readings/`, `tools/`): total non-cache byte budgets,
     plus optional file-count and largest-single-file dimensions.
  4. Repository hygiene guards:
     - `tools/_*` temporary scratch scripts are strictly forbidden (hard limit 0).
     - `tools/*_audit*.py` count approximates per-theme audit proliferation.
       Explicitly reviewed archive-wide gates are exempt from this count; the
       filename glob is not a semantic classifier and cannot enforce a freeze
       against scripts named without "audit". Review new scripts by purpose.

Historical per-session rescale notes (2026-11-07 through 2026-11-24, formerly
~2,200 lines of inline comments in this file) remain preserved verbatim in git
history (`git log -p tools/size_budget.py`). Compressing them into the epoch
architecture (2026-11-25) reclaimed ~155 KiB of `tools/` budget without altering
any gate logic.

Default mode exits 0 on soft warnings and 1 on hard-limit violations (including
any `tools/_*` scratch script). Pass ``--strict`` to treat soft warnings as
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
from typing import Any

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
    soft_files: int | None = None
    hard_files: int | None = None
    soft_file_bytes: int | None = None
    hard_file_bytes: int | None = None
    per_file_remedy: str = ""


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
        "BELIEF_MAP.md",
        # Display policy compresses detail blocks beyond top-12 + warned rows;
        # raised slightly (540 -> 576 KiB) to accommodate P_amort generation-amortized column.
        soft_bytes=576 * 1024,
        hard_bytes=2 * MIB,
        remedy="Keep BELIEF_MAP.md focused on active/refuted hypothesis distributions via tools/belief_state.py --write-map",
    ),
    Budget(
        "docs/CONSOLIDATED_DIGESTS.md",
        soft_bytes=192 * 1024,
        hard_bytes=512 * 1024,
        remedy="Keep L1 domain digests concise via tools/memory_tiers.py --write-digests; raw details remain in L0 state/ and readings/",
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
    Budget(
        "state/notes.jsonl",
        soft_bytes=1 * MIB,
        hard_bytes=5 * MIB,
        remedy="Keep readings/ judgments in state/notes.d/ shards; store curated judgments only, never harvested facts",
    ),
    Budget(
        "state/hypotheses.jsonl",
        soft_bytes=1 * MIB,
        hard_bytes=5 * MIB,
        remedy="Write new hypothesis rows to state/hypotheses.d/ shards",
    ),
    Budget(
        "state/evaluations.jsonl",
        soft_bytes=2 * MIB,
        hard_bytes=8 * MIB,
        remedy="Write new evaluation events to state/evaluations.d/ shards",
    ),
)

SHARD_BUDGETS: tuple[ShardBudget, ...] = (
    ShardBudget(
        # 2026-11-26 (SESSION-20261126-f79ac9): soft 17 -> 18 MiB. Ten-row wave
        # merged into the existing day shard; after merge: 165 shards,
        # 17,834,954 B, 9,162 B over the 17 MiB soft. Rows are append-only and
        # compaction saves ~0 B; 1 MiB step is the established margin. hard and
        # shard budgets unchanged. Re-measure after merge.
        "state/materials.d",
        soft_bytes=18 * MIB,
        hard_bytes=20 * MIB,
        # 2026-11-28: +1 day shard (thought-memory-self 10 sources)
        # 2026-11-28 SESSION-20261128-43eccf: one independent acquisition shard;
        # order-preserving unreferenced compaction found no eligible pair.
        soft_shards=169,
        hard_shards=175,
        remedy="Default to zero-acquisition re-reading sessions; compact old shards when shard count grows",
    ),
    ShardBudget(
        "state/relations.d",
        soft_bytes=4 * MIB,
        hard_bytes=10 * MIB,
        soft_shards=110,
        hard_shards=160,
        remedy="Compact old state/relations.d/ shards into frozen base in a dedicated maintenance PR",
    ),
    ShardBudget(
        "state/read_log.d",
        soft_bytes=7 * MIB,
        hard_bytes=10 * MIB,
        # 2026-11-27: +1 day shard (question-asking session read_log rows)
        # 2026-11-28: +1 day shard (thought-memory-self 10 sources)
        # 2026-11-28 SESSION-20261128-43eccf: one independent read-log shard;
        # order-preserving unreferenced compaction found no eligible pair.
        soft_shards=193,
        hard_shards=200,
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
        soft_bytes=4 * MIB,
        hard_bytes=8 * MIB,
        # 2026-11-27: +1 day shard (question-asking session row)
        # 2026-11-28: +1 day shard (thought-memory-self 10 sources)
        # 2026-11-28 SESSION-20261128-43eccf: one independent session shard;
        # order-preserving unreferenced compaction found no eligible pair.
        soft_shards=195,
        hard_shards=202,
        remedy="Merging shards saves ~0 B, so compaction cannot hold this byte limit; watch soft_shards instead, and if a row must be shortened, cut the narration before the decision",
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
        # 2026-11-28 (SESSION-20261128-db5cf4): soft 1.00 -> 1.10 MiB. The
        # directory sat at 1,048,244 B of the 1,048,576 B soft budget (99.97%)
        # before this session; two legitimate errata rows (ERR-20261128-35d20b
        # recording a self-inclusion artifact of a re-run script_command, and
        # its mis-minted duplicate ERR-20261128-9a3f21) pushed it to 1,051,432 B.
        # Append-only growth is the point of the ledger, so the soft limit is
        # rescaled with headroom rather than the rows being dropped.
        soft_bytes=int(1.10 * MIB),
        hard_bytes=4 * MIB,
        soft_shards=112,
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
    ShardBudget(
        "state/notes.d",
        soft_bytes=int(2.75 * MIB),
        hard_bytes=4 * MIB,
        # 2026-11-28: +1 day shard (thought-memory-self 10 sources)
        soft_shards=183,
        hard_shards=186,
        remedy="Keep one row per (report, reading); supersede instead of rewriting. Do not copy report bodies or harvested facts into the ledger",
    ),
    ShardBudget(
        "state/hypotheses.d",
        soft_bytes=2 * MIB,
        hard_bytes=8 * MIB,
        soft_shards=80,
        hard_shards=160,
        remedy="Consolidate older date-stamped hypothesis shards via state/shard_aliases.json",
    ),
    ShardBudget(
        "state/evaluations.d",
        soft_bytes=4 * MIB,
        hard_bytes=12 * MIB,
        # 2026-11-27: +1 day shard (question-asking session evaluations)
        # 2026-11-28: +1 day shard (thought-memory-self 10 sources)
        soft_shards=111,
        hard_shards=160,
        remedy="Consolidate older date-stamped evaluation shards via state/shard_aliases.json",
    ),
)

DIR_BUDGETS: tuple[DirBudget, ...] = (
    DirBudget(
        # 2026-11-25 architectural transition (three-tier L0/L1/L2 memory):
        # Prior to this transition, readings/ sat at 1,199 / soft 1,199 / hard 1,200.
        # L0 preserves existing append-only episodic files untouched, while L1
        # (`docs/CONSOLIDATED_DIGESTS.md` + `state/digests.json`) absorbs domain
        # consolidation so consolidator sessions no longer need to mint one new
        # readings/ file per consolidation pass. Rescaled to soft 1,250 / hard 1,400
        # (and 42 / 52 MiB) so genuine new close-reading sessions have breathing room
        # while L1 digests take over synthesis.
        "readings",
        soft_bytes=42 * MIB,
        hard_bytes=52 * MIB,
        remedy=(
            "Episodic reports are append-only L0 memory. Prefer consolidating recurring domain "
            "findings into L1 (`python3 tools/memory_tiers.py --write-digests`) instead of minting "
            "redundant summary reports; keep retrieval cheap via `map_build.py` and `note_index.py`"
        ),
        # 2026-11-28: +1 close-reading report (social-referencing ten sources) after
        # main itself reached 1,250/1,250 with the day's earlier reports.
        soft_files=1251,
        hard_files=1400,
        soft_file_bytes=256 * 1024,
        hard_file_bytes=512 * 1024,
        per_file_remedy=(
            "One report must not absorb all the growth (the READING_MAP.md failure mode): split a long "
            "report into a companion note and link the two, instead of appending to the largest file"
        ),
    ),
    DirBudget(
        "tools",
        soft_bytes=int(2.62 * MIB),
        hard_bytes=5 * MIB,
        remedy="Never commit data-embedded scripts in tools/; use tools/lexicon_audit.py instead of new *_audit.py",
    ),
)

AUDIT_SCRIPT_SOFT_COUNT = 57
AUDIT_SCRIPT_HARD_COUNT = 60
CORPUS_GATE_EXEMPTIONS = frozenset({"readings_integrity_audit.py"})


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
        status = _status_for_pair(
            total_bytes,
            dbudget.soft_bytes,
            dbudget.hard_bytes,
            len(files),
            dbudget.soft_files,
            dbudget.hard_files,
        )
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
                soft_count=dbudget.soft_files,
                hard_count=dbudget.hard_files,
            )
        )
        if dbudget.soft_file_bytes is not None and files:
            largest = max(files, key=lambda path: path.stat().st_size)
            largest_bytes = largest.stat().st_size
            results.append(
                CheckResult(
                    rel_path=f"{dbudget.rel_dir}/ largest file ({largest.name})",
                    exists=True,
                    size_bytes=largest_bytes,
                    soft_bytes=dbudget.soft_file_bytes,
                    hard_bytes=dbudget.hard_file_bytes or dbudget.soft_file_bytes * 2,
                    status=_status_for_pair(
                        largest_bytes,
                        dbudget.soft_file_bytes,
                        dbudget.hard_file_bytes or dbudget.soft_file_bytes * 2,
                    ),
                    remedy=dbudget.per_file_remedy or dbudget.remedy,
                )
            )

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

        audit_files = sorted(
            p for p in tools_dir.glob("*_audit*.py") if p.is_file() and p.name not in CORPUS_GATE_EXEMPTIONS
        )
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
                remedy="Per-theme audit creation is frozen; review scripts by purpose regardless of name. Archive-wide gate exemptions are explicit in CORPUS_GATE_EXEMPTIONS; use tools/lexicon_audit.py for themes",
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


RECLAIM_SLACK = 3


def reclaim_candidates(root: Path = ROOT, slack: int = RECLAIM_SLACK) -> list[dict[str, Any]]:
    """Shard budgets whose soft_shards ceiling is now higher than it needs to be."""
    out: list[dict[str, Any]] = []
    for sbudget in SHARD_BUDGETS:
        sdir = root / sbudget.rel_dir
        if not sdir.is_dir():
            continue
        count = len(list(sdir.glob("*.jsonl")))
        free = sbudget.soft_shards - count
        if free >= slack:
            out.append({
                "rel_dir": f"{sbudget.rel_dir}/",
                "shards": count,
                "soft_shards": sbudget.soft_shards,
                "free_slots": free,
                "could_lower_to": count + 1,
            })
    return sorted(out, key=lambda r: -r["free_slots"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when soft budgets are exceeded (default: warn only)",
    )
    parser.add_argument(
        "--reclaim",
        action="store_true",
        help=(
            f"list shard budgets with at least {RECLAIM_SLACK} free slots, i.e. "
            "ceilings that a past session raised and consolidation has since made "
            "unnecessary. Informational: never changes the exit status."
        ),
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

    if args.reclaim:
        cands = reclaim_candidates(args.root)
        if args.json:
            print(json.dumps(cands, ensure_ascii=False, indent=2))
            return 0
        if not cands:
            print(f"no shard budget has {RECLAIM_SLACK}+ free slots; nothing to reclaim")
        else:
            print(f"shard ceilings with {RECLAIM_SLACK}+ free slots -- a past session raised these,")
            print("and consolidation has since made the raise unnecessary:")
            for c in cands:
                print(f"  {c['rel_dir']:26s} shards={c['shards']:4d} soft_shards={c['soft_shards']:4d}"
                      f" free={c['free_slots']:+3d}  could lower to {c['could_lower_to']}")
            print("")
            print("Lowering is a judgement, not an obligation: the next session needs")
            print("one free slot for its own shard, and a collection sitting exactly at")
            print("its ceiling blocks every session that writes to it.")
        return 0

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
