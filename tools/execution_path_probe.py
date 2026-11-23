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
import concurrent.futures
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import importlib
import inspect
import tempfile
import threading
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


# In-process checks make the sweep affordable; EXECUTION_PATH_PROBE_SUBPROCESS=1
# restores the spawned path (the tests compare the two).
IN_PROCESS = os.environ.get("EXECUTION_PATH_PROBE_SUBPROCESS") != "1"


def make_sandbox(root: Path) -> Path:
    sb = Path(tempfile.mkdtemp(prefix="execpath-"))
    for d in COPY_DIRS:
        src = root / d
        if src.is_dir():
            shutil.copytree(src, sb / d)
    for f in root.glob("*.md"):
        shutil.copy2(f, sb / f.name)
    return sb


def clone_committed_template(template: Path, root: Path) -> Path:
    """Copy the committed template into a fresh sandbox and re-copy ``state/``.

    A commit per sandbox cost 0.83 s x 11; copying is 0.35 s (2026-11-23).
    """
    sb = Path(tempfile.mkdtemp(prefix="execpath-"))
    shutil.copytree(template, sb, dirs_exist_ok=True, symlinks=True)
    shutil.rmtree(sb / "state", ignore_errors=True)
    shutil.copytree(root / "state", sb / "state")
    return sb


_TEMPLATE_LOCK = threading.Lock()
_TEMPLATE: tuple[str, Path] | None = None


def make_template(root: Path) -> Path:
    """One sandbox with ``.git`` already committed, reused by every intervention.

    Committing a template per probe run cost 1.1 s x the number of runs. The
    template is keyed on the root it was built from.
    """
    global _TEMPLATE
    key = str(Path(root).resolve())
    with _TEMPLATE_LOCK:
        if _TEMPLATE is not None and _TEMPLATE[0] == key and _TEMPLATE[1].is_dir():
            return _TEMPLATE[1]
        template = make_sandbox(root)
        if not commit_baseline(template):
            shutil.rmtree(template, ignore_errors=True)
            raise RuntimeError("could not commit the sandbox template; append_only_check needs it")
        _TEMPLATE = (key, template)
        return template


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


def ledger_collections(root: Path) -> list[str]:
    """Ledger collections, from the validator's COLLECTIONS rather than assumed.

    fingerprint saw only ``state/*.d/`` directories before, so a collection
    living only in its frozen base was invisible to it.
    """
    with _sandbox_tools(root):
        return sorted(importlib.import_module("validate_seed").COLLECTIONS)


def fingerprint(sb: Path) -> dict[str, dict[str, Any]]:
    fp: dict[str, dict[str, Any]] = {}
    for coll in ledger_collections(sb):
        u = union_lines(sb, coll)
        d = sb / "state" / f"{coll}.d"
        fp[coll] = {
            "sha256": hashlib.sha256("\n".join(u).encode()).hexdigest()[:16],
            "lines": len(u),
            "files": len(list(d.glob("*.jsonl"))) if d.is_dir() else 0,
        }
    return fp


@contextlib.contextmanager
def _sandbox_tools(root: Path):
    """Import a tool from ``root``'s ``tools/`` and undo the import after.

    Modules already in ``sys.modules`` under a tool's name are displaced for the
    call: restoring the path alone left the host's copies in place, so a probe
    under the suite measured the LIVE ledgers (2026-11-23).
    """
    before_path, before_modules, before_cwd = list(sys.path), dict(sys.modules), os.getcwd()
    # By NAME: the host copies live in this checkout, so a path test fails.
    sandbox_names = {p.stem for p in (Path(root) / "tools").glob("*.py")}
    shadowed = {n: m for n, m in before_modules.items() if n in sandbox_names}
    try:
        for name in shadowed:
            del sys.modules[name]
        os.chdir(root)
        sys.path[0:0] = [str(Path(root).resolve() / "tools")]
        yield
    finally:
        for name in [n for n in sys.modules if n not in before_modules]:
            del sys.modules[name]
        sys.modules.update(shadowed)
        os.chdir(before_cwd)
        sys.path[:] = before_path


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


def _exit_of(fn: Callable[[], int]) -> int:
    """Run a tool's ``main()`` and turn its exit path into an exit code.

    The tools print their report themselves; only the status is needed here.
    ``SystemExit`` is how both ``sys.exit`` and ``argparse`` end, and a tool that
    raises is reported as a failure rather than crashing the probe: a broken
    check is a detection, not an absence of one.
    """
    try:
        code = fn()
    except SystemExit as exc:
        code = 0 if exc.code is None else int(exc.code) if isinstance(exc.code, int) else 1
    except Exception:  # noqa: BLE001 - a crashing check must not abort the sweep
        code = 1
    return int(code)


def run_checks(sb: Path, in_process: bool = IN_PROCESS) -> dict[str, dict[str, Any]]:
    """Run the seven checks. Each was a child process until 2026-11-23 (86 s per
    sweep); calling ``main()`` gave identical exits on all 77 runs."""
    if not in_process:
        res: dict[str, dict[str, Any]] = {}
        for name, cmd, kind in CHECKS:
            p = subprocess.run([sys.executable, *cmd], cwd=sb, capture_output=True, text=True)
            lines = p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or [""]
            res[name] = {"exit": p.returncode, "kind": kind, "last": lines[-1][:200]}
        return res
    res: dict[str, dict[str, Any]] = {}
    for name, cmd, kind in CHECKS:
        res[name] = _run_one_in_sandbox(sb, name, cmd, kind)
    return res


def _run_one_in_sandbox(sb: Path, name: str, cmd: tuple[str, ...], kind: str) -> dict[str, Any]:
    """Run one check inside the sandbox, isolated from this process's imports.

    A tool binds ``ROOT`` at import time to its own location; loading it fresh
    under a sandbox-only ``sys.path`` keeps what the subprocess gave us (a check
    that reads the sandbox), and the import is re-paid per check.
    """
    script = Path(cmd[0]).name
    args = list(cmd[1:])
    before_modules = set(sys.modules)
    out = io.StringIO()
    try:
        with _sandbox_tools(sb):
            module = importlib.import_module(script[:-3])
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                # The flags ARE passed (without them every check exited 2); ROOT
                # comes from the tool's own path, so `--root` is not added.
                code = _call_main(module.main, args)
    except Exception:  # noqa: BLE001 - an unimportable check is a failed check
        code = 1
    finally:
        # Drop modules first imported here, so no sandbox-bound module is left.
        for name_ in set(sys.modules) - before_modules:
            del sys.modules[name_]
    lines = out.getvalue().strip().splitlines() or [""]
    return {"exit": code, "kind": kind, "last": lines[-1][:200]}


def _call_main(fn: Callable[..., Any], args: list[str]) -> int:
    """Call a tool's main() with the check's flags.

    ``validate_seed.main()`` takes no argv; passing one raises TypeError, which
    would be read as a failed check, so the arity is inspected.
    """
    if not _takes_argv(fn):
        return _exit_of(fn)
    return _exit_of(lambda: fn(args))


def _takes_argv(fn: Callable[..., Any]) -> bool:
    """Whether main() accepts argv."""
    try:
        return bool(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        return False


def _render_packet(sb: Path, target: str, seed: str, in_process: bool = IN_PROCESS) -> tuple[str, int]:
    """Render the packet the next reader receives (pinned equal by tests)."""
    if not in_process:
        p = subprocess.run([sys.executable, "tools/inspect_inquiry.py", "--packet", target,
                            "--seed", seed], cwd=sb, capture_output=True, text=True)
        return p.stdout, p.returncode
    return _packet_in_process(sb, target, seed)


def _packet_in_process(sb: Path, target: str, seed: str) -> tuple[str, int]:
    """Render one packet, reusing the sandbox's parsed ledgers across calls.

    ``--packet`` parses the ledgers, then harvests every ``readings/*.md`` into a
    note view. Two packets are rendered per intervention over an unchanged
    sandbox, so this is done once per RUN; the cache is keyed on the root and the
    ``state/`` stat signature.
    """
    key = str(Path(sb).resolve())
    signature = _state_stat_signature(Path(sb))
    entry = _PACKET_CACHE.get(key)
    out: list[str] = []
    code = 1
    try:
        with _sandbox_tools(sb):
            import inspect_inquiry as ii
            import note_index
            if entry is None or entry[0] != signature:
                _PACKET_CACHE.clear()
                data = ii.load_all()
                harvested = note_index.harvest(Path(sb), data)
                _PACKET_CACHE[key] = (signature, data, harvested)
            else:
                _signature, data, harvested = entry
            out.append(
                ii.build_context_packet(
                    data, target, seed=seed,
                note_view=note_index.build_view(Path(sb), data, harvested=harvested),
                )
            )
            code = 0
    except SystemExit as exc:          # load_all() prints and exits on a bad ledger
        code = 0 if exc.code is None else 1
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        out.append(f"error: {exc}\n")
    return ("".join(out) if out else ""), code


_PACKET_CACHE: dict[str, tuple[Any, Any, Any]] = {}


def _state_stat_signature(sb: Path) -> tuple[tuple[str, int, int], ...]:
    """Each ledger file's path, size and mtime."""
    return tuple(
        (str(p.relative_to(sb)), p.stat().st_size, p.stat().st_mtime_ns)
        for p in sorted((sb / "state").rglob("*.jsonl"))
    )


def run_packet(sb: Path, seed: str = BASE_SEED, in_process: bool = IN_PROCESS) -> dict[str, Any]:
    """Pinned-target packet: the knobs can be read off a stable question.

    The seed is a parameter, not a literal; ``hyp_order`` is the §0.2 ranking.
    """
    out, rc = _render_packet(sb, "Q-003", seed, in_process)
    sec = out.split("## 0.2")[-1].split("\n## 1.")[0]
    return {"sha256": hashlib.sha256(out.encode()).hexdigest()[:16],
            "bytes": len(out), "exit": rc, "seed": seed,
            "hyp_order": _HYP.findall(sec)}


def run_packet_auto(sb: Path, seed: str = BASE_SEED, in_process: bool = IN_PROCESS) -> dict[str, Any]:
    """Unpinned packet: what a reader who does not choose their own target gets.

    This is the only measurement that can show an intervention changing WHICH
    question is answered rather than how it is answered. The pinned packet above
    cannot show that, by construction -- which is why the target-level reach of
    the path was understated while only the pinned packet was measured.
    """
    out, rc = _render_packet(sb, "auto", seed, in_process)
    first = out.splitlines()[0] if out else ""
    hdr, role = _HDR.search(first), _ROLE.search(out)
    return {"sha256": hashlib.sha256(out.encode()).hexdigest()[:16],
            "bytes": len(out), "exit": rc, "seed": seed,
            "target": hdr.group(1) if hdr else None,
            "mode": hdr.group(2) if hdr else None,
            "role": role.group(1).strip() if role else None}


def _measure_one(
    template: Path, root: Path, fam: str,
    fn: Callable[[Path], str] | None, seed: str, in_process: bool = IN_PROCESS,
) -> dict[str, Any]:
    """Measure one intervention in its own sandbox (worker-process safe)."""
    sb = clone_committed_template(template, root)
    try:
        if fn:
            desc = fn(sb)
        elif seed != BASE_SEED:
            desc = f"dispersal seed {BASE_SEED} -> {seed} (no file touched)"
        else:
            desc = "exact copy, no intervention"
        return {
            "family": fam, "desc": desc, "seed": seed,
            "fingerprint": fingerprint(sb),
            "checks": run_checks(sb, in_process),
            "packet": run_packet(sb, seed, in_process),
            "packet_auto": run_packet_auto(sb, seed, in_process),
        }
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def default_jobs() -> int:
    """Sandboxes at once: CPU count capped. Two workers: 139 s -> 77 s
    (2026-11-23). ``EXECUTION_PATH_PROBE_JOBS=1`` is the sequential sweep."""
    env = os.environ.get("EXECUTION_PATH_PROBE_JOBS")
    if env:
        try:
            return max(1, int(env))
        except ValueError:
            pass
    return max(1, min(4, os.cpu_count() or 1))


def run(root: Path | str = ROOT, family: str | None = None,
        only: str | None = None, in_process: bool = IN_PROCESS,
        jobs: int | None = None) -> dict[str, Any]:
    """Sweep the interventions and report what each one moved.

    One template is copied per intervention, each sandbox's ``state/`` is the
    caller's. With ``jobs > 1`` (default) measurements run in parallel; the
    comparison against the control happens here in declaration order.
    """
    root = Path(root)
    selected = [
        (name, fam, fn, seed) for name, fam, fn, seed in INTERVENTIONS
        if (not only or name == only) and (not family or fam == family or name == "I0_control")
    ]
    out: dict[str, Any] = {"root": str(root), "interventions": {}}
    if not selected:
        return out
    # make_template takes the template lock itself; holding it here deadlocked.
    template = make_template(root)
    workers = default_jobs() if jobs is None else max(1, int(jobs))
    results: dict[str, dict[str, Any]] = {}
    if workers == 1 or len(selected) == 1:
        for name, fam, fn, seed in selected:
            results[name] = _measure_one(template, root, fam, fn, seed, in_process)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_measure_one, template, root, fam, fn, seed, in_process): name
                for name, fam, fn, seed in selected
            }
            for future in concurrent.futures.as_completed(futures):
                results[futures[future]] = future.result()

    base_fp = base_checks = base_pkt = base_auto = None
    for name, _fam, _fn, _seed in selected:  # declaration order, not finish order
        v = results[name]
        fp, checks, pkt, auto = v["fingerprint"], v["checks"], v["packet"], v["packet_auto"]
        if base_fp is None:
            base_fp, base_checks, base_pkt, base_auto = fp, checks, pkt, auto
        out["interventions"][name] = {
            "family": v["family"], "desc": v["desc"], "seed": v["seed"],
            "baseline_committed": True,
            "union_identical": all(fp[c]["sha256"] == base_fp[c]["sha256"] for c in base_fp),
            "line_counts_identical": all(fp[c]["lines"] == base_fp[c]["lines"] for c in base_fp),
            "file_count_delta": {c: fp[c]["files"] - base_fp[c]["files"]
                                 for c in fp if fp[c]["files"] != base_fp[c]["files"]},
            "checks_flipped": [k for k in checks if checks[k]["exit"] != base_checks[k]["exit"]],
            "named_checks_flipped": [k for k in checks
                                     if checks[k]["kind"] == "named_in_scope"
                                     and checks[k]["exit"] != base_checks[k]["exit"]],
            "check_exits": {k: v2["exit"] for k, v2 in checks.items()},
            "packet": pkt, "packet_changed": pkt["sha256"] != base_pkt["sha256"],
            # The ranking is separated from the packet bytes: a path change that
            # moves what the reader receives but not the ranking is what limb (a)
            # is about.
            "hyp_order_identical": pkt["hyp_order"] == base_pkt["hyp_order"],
            "packet_auto": auto,
            "packet_auto_changed": auto["sha256"] != base_auto["sha256"],
            "auto_target_changed": auto["target"] != base_auto["target"],
        }
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


def main(argv: list[str] | None = None) -> int:  # noqa: D401 - CLI entry
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--family", choices=["storage", "packet", "seed"])
    ap.add_argument("--only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--subprocess-checks",
        action="store_true",
        help="run each check and packet as a child process (the pre-2026-11-23 path; slower)",
    )
    args = ap.parse_args(argv)
    res = run(args.root, args.family, args.only, in_process=not args.subprocess_checks)
    print(json.dumps(res, ensure_ascii=False, indent=1) if args.json else render(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
