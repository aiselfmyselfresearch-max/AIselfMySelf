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
labels every check ``named_in_scope`` or ``other`` and reports them apart. All
three named checks are run; until 2026-11-14 only two of them were, so (b) had
been scored against an incomplete named set.

Method
------
Copy the repository into a throwaway sandbox, apply ONE intervention, re-run the
checks and render the packet twice: once pinned to Q-003 so the knobs can be read
off a stable question, and once with ``--packet auto`` so an intervention that
changes WHICH question is answered cannot hide. Three families:

* storage path -- split a shard, rename its suffix, forge a future date, lower a
  size cap. Ledger rows are never edited.
* packet path -- the knobs the hypothesis literally names: inheritance window,
  inheritance limit, material section budget, hypothesis ordering.
* seed path -- the dispersal seed itself. No file is touched and the ledger union
  stays byte-identical, yet the seed chooses the role, the reference mode and the
  candidate window. Every finding in the two families above was measured at one
  pinned seed until 2026-11-14, which made the largest path parameter invisible.

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
    python3 tools/execution_path_probe.py --family seed

Exit status is always 0. A finding that a hypothesis is wrong is a successful
measurement. Sandboxes are removed on completion; the repository is never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent

# The hypothesis this probe was built to test. Named explicitly so that
# tests/test_instrument_coverage.py can read that hypothesis's scope_conditions,
# extract the checks it names, and assert that every one of them is in CHECKS
# below and labelled named_in_scope. Before 2026-11-15 the subject was only
# implied by the docstring, so when CHECKS omitted append_only_check -- one of the
# three checks the docstring itself listed -- nothing could notice.
SUBJECT_HYPOTHESIS = "HYP-20261113-17ea95"

# taxonomy/ is required: note_index counts inbound links from taxonomy/notes/*.md.
COPY_DIRS = ("state", "tools", "schema", "docs", "prompts", "readings", "taxonomy")

# The dispersal seed is itself an execution-path parameter: inspect_inquiry.py takes
# --seed and uses it to pick the role, the reference mode and the candidate window.
# It was pinned to one literal here until 2026-11-14, so every "packet path" finding
# below was conditional on that one seed and the seed axis was structurally invisible
# to the instrument that HYP-20261114-27fd10's refutation condition rests on.
# Two alternatives are enough: the claim measured is "distinct seeds give distinct
# packets while no check notices", which needs a pair, not a sweep.
BASE_SEED = "17ea95"
ALT_SEEDS = ("00000000", "ffffffff")

_HDR = re.compile(r"対象：(\S+)\s*／\s*参考モード：(\S+)")
_ROLE = re.compile(r"\*\*割り当て探求ロール\*\*:\s*\*\*([^*（]+)")
_HYP = re.compile(r"\*\*`(HYP-[0-9]{8}-[0-9a-z]{6})`\*\*")

# append_only_check was named in HYP-20261113-17ea95's scope_conditions and in this
# file's own docstring, but was absent from this list until 2026-11-14: limb (b) had
# been scored against 2 of the 3 named checks. An instrument that omits a member of
# the very set its hypothesis names can only under-report a refutation.
CHECKS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("validate_seed", ("tools/validate_seed.py",), "named_in_scope"),
    ("append_only_check", ("tools/append_only_check.py",), "named_in_scope"),
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


def _git(sb: Path, *args: str) -> int:
    return subprocess.run(["git", "-C", str(sb), *args], capture_output=True, text=True).returncode


def commit_baseline(sb: Path) -> bool:
    """Commit the pristine ledger INSIDE the sandbox so append_only_check can run.

    ``append_only_check.py`` compares the working ledger against a git revision
    (``git archive <rev> state``). A plain sandbox copy has no ``.git``, so the
    check exits 2 with "CANNOT COMPARE" -- an inability to run, which is not a
    detection and must never be silently counted as a pass. Committing the
    untouched copy first makes the comparison the one the experiment actually
    wants: intervention versus pristine, independent of the outer repository's
    commit state (which carries uncommitted work mid-session).

    MUST be called before the intervention is applied, or the baseline absorbs it.
    """
    if _git(sb, "init", "-q") != 0:
        return False
    _git(sb, "config", "user.email", "probe@localhost")
    _git(sb, "config", "user.name", "execution_path_probe")
    _git(sb, "add", "-A", "--", "state")
    return _git(sb, "commit", "-q", "-m", "pristine ledger baseline") == 0


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
    _patch(
        sb,
        "tools/inspect_inquiry.py",
        'key=lambda h: gated_rank.get(str(h.get("hypothesis_id", "")), (1, 0.0, str(h.get("hypothesis_id", "")))),\n    )',
        'key=lambda h: gated_rank.get(str(h.get("hypothesis_id", "")), (1, 0.0, str(h.get("hypothesis_id", "")))),\n        reverse=True,\n    )',
    )
    return "reverse the active-hypothesis ordering"


INTERVENTIONS: tuple[tuple[str, str, Callable[[Path], str] | None, str], ...] = (
    ("I0_control", "storage", None, BASE_SEED),
    ("I1_split_shard", "storage", iv_split_shard, BASE_SEED),
    ("I2_rename_suffix", "storage", iv_rename_suffix, BASE_SEED),
    ("I3_future_date", "storage", iv_future_date, BASE_SEED),
    ("I4_lower_cap", "storage", iv_lower_cap, BASE_SEED),
    ("P1_window", "packet", iv_window, BASE_SEED),
    ("P2_limit", "packet", iv_limit, BASE_SEED),
    ("P3_budget", "packet", iv_budget, BASE_SEED),
    ("P4_order", "packet", iv_order, BASE_SEED),
    # seed family: no file is touched, the ledger union is byte-identical, and the
    # only thing that changes is the dispersal seed the reader was handed.
    ("S1_seed_low", "seed", None, ALT_SEEDS[0]),
    ("S2_seed_high", "seed", None, ALT_SEEDS[1]),
)


def run_checks(sb: Path) -> dict[str, dict[str, Any]]:
    res: dict[str, dict[str, Any]] = {}
    for name, cmd, kind in CHECKS:
        p = subprocess.run([sys.executable, *cmd], cwd=sb, capture_output=True, text=True)
        lines = p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""]
        res[name] = {"exit": p.returncode, "kind": kind, "last": lines[-1][:200]}
    return res


def _render_packet(sb: Path, target: str, seed: str) -> tuple[str, int]:
    p = subprocess.run([sys.executable, "tools/inspect_inquiry.py", "--packet", target,
                        "--seed", seed], cwd=sb, capture_output=True, text=True)
    return p.stdout, p.returncode


def run_packet(sb: Path, seed: str = BASE_SEED) -> dict[str, Any]:
    """Pinned-target packet: the knobs can be read off a stable question.

    The seed is now a parameter rather than a literal. ``hyp_order`` is the
    §0.2 ranking, extracted so that "the packet changed" can be separated from
    "the belief ranking changed" -- the second is what limb (a) is about.
    """
    out, rc = _render_packet(sb, "Q-003", seed)
    sec = out.split("## 0.2")[-1].split("\n## 1.")[0]
    return {"sha256": hashlib.sha256(out.encode()).hexdigest()[:16],
            "bytes": len(out), "exit": rc, "seed": seed,
            "hyp_order": _HYP.findall(sec)}


def run_packet_auto(sb: Path, seed: str = BASE_SEED) -> dict[str, Any]:
    """Unpinned packet: what a reader who does not choose their own target gets.

    This is the only measurement that can show an intervention changing WHICH
    question is answered rather than how it is answered. The pinned packet above
    cannot show that, by construction -- which is why the target-level reach of
    the path was understated while only the pinned packet was measured.
    """
    out, rc = _render_packet(sb, "auto", seed)
    first = out.splitlines()[0] if out else ""
    hdr, role = _HDR.search(first), _ROLE.search(out)
    return {"sha256": hashlib.sha256(out.encode()).hexdigest()[:16],
            "bytes": len(out), "exit": rc, "seed": seed,
            "target": hdr.group(1) if hdr else None,
            "mode": hdr.group(2) if hdr else None,
            "role": role.group(1).strip() if role else None}


def run(root: Path | str = ROOT, family: str | None = None,
        only: str | None = None) -> dict[str, Any]:
    root = Path(root)
    out: dict[str, Any] = {"root": str(root), "interventions": {}}
    base_fp = base_checks = base_pkt = base_auto = None
    for name, fam, fn, seed in INTERVENTIONS:
        if only and name != only:
            continue
        if family and fam != family and name != "I0_control":
            continue
        sb = make_sandbox(root)
        try:
            git_ok = commit_baseline(sb)
            if fn:
                desc = fn(sb)
            elif seed != BASE_SEED:
                desc = f"dispersal seed {BASE_SEED} -> {seed} (no file touched)"
            else:
                desc = "exact copy, no intervention"
            fp, checks = fingerprint(sb), run_checks(sb)
            pkt, auto = run_packet(sb, seed), run_packet_auto(sb, seed)
            if base_fp is None:
                base_fp, base_checks, base_pkt, base_auto = fp, checks, pkt, auto
            out["interventions"][name] = {
                "family": fam, "desc": desc, "seed": seed,
                "baseline_committed": git_ok,
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
                # The belief ranking is separated from the packet bytes: a path
                # change that moves what the reader receives but not the ranking
                # is the only kind that can bear on limb (a).
                "hyp_order_identical": pkt["hyp_order"] == base_pkt["hyp_order"],
                "packet_auto": auto,
                "packet_auto_changed": auto["sha256"] != base_auto["sha256"],
                "auto_target_changed": auto["target"] != base_auto["target"],
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
    if any(not v.get("baseline_committed", False) for v in res["interventions"].values()):
        lines.append("WARNING: no sandbox git baseline was committed, so")
        lines.append("append_only_check could not run and its 'no flip' is meaningless.")
        lines.append("")
    lines.append(f"{'intervention':18s} {'seed':10s} {'packet':8s} {'auto':6s} "
                 f"{'tgt':6s} {'rank':6s} {'flipped':30s} named")
    for name, v in res["interventions"].items():
        lines.append(f"{name:18s} {v['seed']:10s} {str(v['packet_changed']):8s} "
                     f"{str(v['packet_auto_changed']):6s} "
                     f"{str(v['auto_target_changed']):6s} "
                     f"{str(v['hyp_order_identical']):6s} "
                     f"{(','.join(v['checks_flipped']) or 'none'):30s} "
                     f"{','.join(v['named_checks_flipped']) or 'none'}")
    lines.append("")
    lines.append("belief_state recomputation on an unchanged union is a tautology;")
    lines.append("it is NOT evidence for exclusion limb (a). The packet column is.")
    lines.append("auto=the unpinned packet changed; tgt=it changed WHICH question is")
    lines.append("answered; rank=the §0.2 belief ordering stayed identical.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--family", choices=["storage", "packet", "seed"])
    ap.add_argument("--only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    res = run(args.root, args.family, args.only)
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else render(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
