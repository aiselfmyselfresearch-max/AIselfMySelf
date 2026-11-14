#!/usr/bin/env python3
"""Change only the EXECUTION PATH and ask which checks notice. Read-only.

Why this exists
---------------
``HYP-20261113-17ea95`` (provable closure, judgment-content edition) claims that
self-continuity is closed over *judgment content* while the *execution path*
(packet ordering, caps, read order, tool availability) lies outside that closure.
Its exclusion clause has two limbs pointing in opposite directions:

  (a) a path-only controlled experiment leaves the later judgment distribution
      statistically identical                          -> narrowed / refuted
  (b) path wear IS detectable by the judgment-content checks
      (the checks are reading path state)               -> narrowed / refuted

Its ``scope_conditions`` name three checks specifically: ``validate_seed.py``,
``append_only_check.py``, ``belief_state.py --check-map``. Scoring (b) against
*other* checks would test a claim the hypothesis does not make, so this probe
labels every check ``named_in_scope`` or ``other`` and reports them apart.

Method
------
Copy the repository into a throwaway sandbox, apply ONE intervention, re-run the
checks and a fixed-seed Q-003 packet (rather than a variable auto selection).
Two families:

* storage path -- split a shard, rename its suffix, forge a future date, lower a
  size cap. Ledger rows are never edited.
* packet path -- the knobs the hypothesis literally names: inheritance window,
  inheritance limit, material section budget, hypothesis ordering.

A POSIX ``map/`` directory and ``taxonomy/`` must both be copied: ``note_index``
scans ``taxonomy/notes/*.md`` for inbound links, and omitting it makes the
untouched control report STALE. That confound cost one discarded run.

What is NOT evidence
--------------------
Recomputing ``belief_state`` on an unchanged row union is a tautology: identical
rows give identical numbers. It is reported as ``q003_kl`` for completeness and
must never be scored as limb (a). The non-tautological question is whether the
PACKET -- what the next reader actually receives -- changes.

Usage::

    python3 tools/execution_path_probe.py
    python3 tools/execution_path_probe.py --family packet --json
    python3 tools/execution_path_probe.py --only P4_order

Exit status is always 0. A finding that a hypothesis is wrong is a successful
measurement. Sandboxes are removed on completion; the repository is never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent

# taxonomy/ is required: note_index counts inbound links from taxonomy/notes/*.md.
COPY_DIRS = ("state", "tools", "schema", "docs", "prompts", "readings", "taxonomy")

CHECKS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("validate_seed", ("tools/validate_seed.py",), "named_in_scope"),
    ("belief_state_map", ("tools/belief_state.py", "--check-map"), "named_in_scope"),
    ("size_budget_strict", ("tools/size_budget.py", "--strict"), "other"),
    ("date_axis_shards", ("tools/date_axis.py", "--enforce-shards"), "other"),
    ("note_index", ("tools/note_index.py", "--check"), "other"),
    ("learning_metrics", ("tools/learning_metrics.py", "--check"), "other"),
)


def make_sandbox(root: Path) -> Path:
    sb = Path(tempfile.mkdtemp(prefix="execpath-"))
    for d in COPY_DIRS:
        src = root / d
        if src.is_dir():
            shutil.copytree(src, sb / d)
    for f in root.glob("*.md"):
        shutil.copy2(f, sb / f.name)
    return sb


def union_lines(sb: Path, coll: str) -> list[str]:
    """Ledger lines across shards in filename order, plus the base file."""
    out: list[str] = []
    d = sb / "state" / f"{coll}.d"
    if d.is_dir():
        for p in sorted(d.glob("*.jsonl")):
            out.extend(l for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    base = sb / "state" / f"{coll}.jsonl"
    if base.is_file():
        out.extend(l for l in base.read_text(encoding="utf-8").splitlines() if l.strip())
    return out


def fingerprint(sb: Path) -> dict[str, dict[str, Any]]:
    fp: dict[str, dict[str, Any]] = {}
    for d in sorted((sb / "state").glob("*.d")):
        coll = d.name[:-2]
        u = union_lines(sb, coll)
        fp[coll] = {
            "sha256": hashlib.sha256("\n".join(u).encode()).hexdigest()[:16],
            "lines": len(u),
            "files": len(list(d.glob("*.jsonl"))),
        }
    return fp


def _patch(sb: Path, rel: str, old: str, new: str) -> None:
    p = sb / rel
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise RuntimeError(f"knob not found in {rel}: {old!r}; re-read before measuring")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


# ---------------- interventions: storage path ----------------

def iv_split_shard(sb: Path) -> str:
    d = sb / "state" / "errata.d"
    target = max(sorted(d.glob("*.jsonl")), key=lambda p: p.stat().st_size)
    lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
    if len(lines) < 2:
        raise RuntimeError("shard too small to split")
    mid = len(lines) // 2
    target.write_text("".join(lines[:mid]), encoding="utf-8")
    target.with_name(target.stem + "-split.jsonl").write_text("".join(lines[mid:]), encoding="utf-8")
    return f"split {target.name} into two (rows preserved, file count +1)"


def iv_rename_suffix(sb: Path) -> str:
    target = sorted((sb / "state" / "errata.d").glob("*.jsonl"))[0]
    new = target.with_name(target.name.rsplit("-", 1)[0] + "-ffffffffffff.jsonl")
    target.rename(new)
    return f"renamed {target.name} -> {new.name} (same date)"


def iv_future_date(sb: Path) -> str:
    """Positive control: a forged date. Path-only, and SHOULD be caught."""
    target = sorted((sb / "state" / "errata.d").glob("*.jsonl"))[0]
    new = target.with_name("2027-12-31-" + target.name.split("-", 3)[3])
    target.rename(new)
    return f"future-dated {target.name} -> {new.name}"


def iv_lower_cap(sb: Path) -> str:
    _patch(sb, "tools/size_budget.py", "soft_shards=110,", "soft_shards=1,")
    return "lowered one soft_shards default 110 -> 1 (no row, no filename touched)"


# ---------------- interventions: packet path ----------------

def iv_window(sb: Path) -> str:
    _patch(sb, "tools/inspect_inquiry.py",
           "INHERITANCE_WINDOW_DEFAULT = 30", "INHERITANCE_WINDOW_DEFAULT = 3")
    return "inheritance window 30 -> 3"


def iv_limit(sb: Path) -> str:
    _patch(sb, "tools/inspect_inquiry.py", "INHERITANCE_LIMIT = 6", "INHERITANCE_LIMIT = 1")
    return "inheritance limit 6 -> 1"


def iv_budget(sb: Path) -> str:
    _patch(sb, "tools/inspect_inquiry.py",
           "MATERIAL_SECTION_BUDGET = 16_384", "MATERIAL_SECTION_BUDGET = 2_048")
    return "material section budget 16384 -> 2048"


def iv_order(sb: Path) -> str:
    _patch(sb, "tools/inspect_inquiry.py",
           'key=lambda h: str(h.get("hypothesis_id", "")),\n    )\n    dynamic_mids',
           'key=lambda h: str(h.get("hypothesis_id", "")),\n        reverse=True,\n    )\n    dynamic_mids')
    return "reverse the active-hypothesis ordering"


INTERVENTIONS: tuple[tuple[str, str, Callable[[Path], str] | None], ...] = (
    ("I0_control", "storage", None),
    ("I1_split_shard", "storage", iv_split_shard),
    ("I2_rename_suffix", "storage", iv_rename_suffix),
    ("I3_future_date", "storage", iv_future_date),
    ("I4_lower_cap", "storage", iv_lower_cap),
    ("P1_window", "packet", iv_window),
    ("P2_limit", "packet", iv_limit),
    ("P3_budget", "packet", iv_budget),
    ("P4_order", "packet", iv_order),
)


def run_checks(sb: Path) -> dict[str, dict[str, Any]]:
    res: dict[str, dict[str, Any]] = {}
    for name, cmd, kind in CHECKS:
        p = subprocess.run([sys.executable, *cmd], cwd=sb, capture_output=True, text=True)
        lines = p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""]
        res[name] = {"exit": p.returncode, "kind": kind, "last": lines[-1][:200]}
    return res


def run_packet(sb: Path) -> dict[str, Any]:
    # Use a core question and fixed seed: an auto-selected derived question may
    # have no hypotheses or enough materials to exercise the order/budget knobs.
    p = subprocess.run([sys.executable, "tools/inspect_inquiry.py", "--packet", "Q-003",
                        "--seed", "17ea95"], cwd=sb, capture_output=True, text=True)
    return {"sha256": hashlib.sha256(p.stdout.encode()).hexdigest()[:16],
            "bytes": len(p.stdout), "exit": p.returncode}


def run(root: Path | str = ROOT, family: str | None = None,
        only: str | None = None) -> dict[str, Any]:
    root = Path(root)
    out: dict[str, Any] = {"root": str(root), "interventions": {}}
    base_fp = base_checks = base_pkt = None
    for name, fam, fn in INTERVENTIONS:
        if only and name != only:
            continue
        if family and fam != family and name != "I0_control":
            continue
        sb = make_sandbox(root)
        try:
            desc = fn(sb) if fn else "exact copy, no intervention"
            fp, checks, pkt = fingerprint(sb), run_checks(sb), run_packet(sb)
            if base_fp is None:
                base_fp, base_checks, base_pkt = fp, checks, pkt
            out["interventions"][name] = {
                "family": fam, "desc": desc,
                "union_identical": all(fp[c]["sha256"] == base_fp[c]["sha256"] for c in base_fp),
                "line_counts_identical": all(fp[c]["lines"] == base_fp[c]["lines"] for c in base_fp),
                "file_count_delta": {c: fp[c]["files"] - base_fp[c]["files"]
                                     for c in fp if fp[c]["files"] != base_fp[c]["files"]},
                "checks_flipped": [k for k in checks if checks[k]["exit"] != base_checks[k]["exit"]],
                "named_checks_flipped": [k for k in checks
                                         if checks[k]["kind"] == "named_in_scope"
                                         and checks[k]["exit"] != base_checks[k]["exit"]],
                "check_exits": {k: v["exit"] for k, v in checks.items()},
                "packet": pkt, "packet_changed": pkt["sha256"] != base_pkt["sha256"],
            }
        finally:
            shutil.rmtree(sb, ignore_errors=True)
    if base_checks:
        out["baseline"] = {k: {"exit": v["exit"], "kind": v["kind"]}
                           for k, v in base_checks.items()}
        out["baseline_all_pass"] = all(v["exit"] == 0 for v in base_checks.values())
    return out


def render(res: dict[str, Any]) -> str:
    lines = [f"root={res['root']}", ""]
    if not res.get("baseline_all_pass", False):
        lines.append("WARNING: baseline is not all-green; flips below are confounded.")
        lines.append("")
    lines.append(f"{'intervention':18s} {'packet':8s} {'flipped':34s} named")
    for name, v in res["interventions"].items():
        lines.append(f"{name:18s} {str(v['packet_changed']):8s} "
                     f"{(','.join(v['checks_flipped']) or 'none'):34s} "
                     f"{','.join(v['named_checks_flipped']) or 'none'}")
    lines.append("")
    lines.append("belief_state recomputation on an unchanged union is a tautology;")
    lines.append("it is NOT evidence for exclusion limb (a). The packet column is.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--family", choices=["storage", "packet"])
    ap.add_argument("--only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = run(args.root, args.family, args.only)
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else render(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
