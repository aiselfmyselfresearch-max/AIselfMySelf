"""Shared fixtures for the regression suite: one copy rule, one ledger reader.

Why this file exists
--------------------
Sixteen test modules each carried their own ``shutil.copytree(ROOT, repo,
ignore=...)`` and the ignore lists did not agree. Measured on 2026-11-23
(docs/2026-11-23-test-suite-runtime-analysis.md):

* the suite performed **1,232** ``copytree`` calls;
* ``tests/test_server.py`` copied all 1,163 ``readings/`` files (18 MB) into eight
  sandboxes and asserted nothing about their prose -- the archive build it
  triggers went from 4.0 s (no prose) to 13.2 s (all of it). Its one assertion
  about prose is that the payload's ``readings`` list is NON-empty; it needs two
  files, not eighteen megabytes;
* ``tests/test_read_log.py`` copied it too, ``tests/test_parallel_sessions.py``
  did not, and nobody could tell from the call site which was intended.

So the copy rule lives here, once. The default copies the prose, because
``validate_seed.py`` resolves every ``notes.path`` and fails when a referenced
``readings/*.md`` is missing -- a sandbox without prose is a sandbox where the
gate cannot run. A test that does not need the prose says so at the call site
(``include_readings=False``) and, if it needs a little of it, names the files
(``materialise_readings``). That call site is the one place a reader looks to
see what the test actually depends on.

Nothing here changes what a check decides; it changes how much of the archive a
sandbox carries and how many times the same tool is started to ask one question.
"""
from __future__ import annotations

import io
import shutil
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]

#: Copied by default: the ledgers and everything a rule reads from.
DEFAULT_INCLUDE = (
    "state",
    "schema",
    "tools",
    "taxonomy",
    "prompts",
    "viewer",
    "docs",
    "*.md",
)

#: Never copied: history, caches, the suite itself, and generated output.
DEFAULT_EXCLUDE = (
    ".git",
    "__pycache__",
    "*.pyc",
    "tests",
    "map",
    ".pytest_cache",
    ".arena",
)


def copy_repo(
    destination: Path,
    *,
    include_readings: bool = True,
    include_git: bool = False,
    include_tests: bool = False,
    include_map: bool = False,
    extra_exclude: tuple[str, ...] = (),
) -> Path:
    """Copy this checkout into ``destination/repo`` and return that path.

    ``include_readings=False`` creates an EMPTY ``readings/`` directory rather
    than omitting it: the viewer and ``note_index`` ask whether the directory
    exists, and a missing directory is a different repository from an empty one.
    Use ``materialise_readings`` afterwards to copy just the files a test reads.
    """
    repo = destination / "repo"
    exclude = list(DEFAULT_EXCLUDE) + list(extra_exclude)
    if not include_readings:
        exclude.append("readings")
    if include_git:
        exclude.remove(".git")
    if include_tests:
        exclude.remove("tests")
    if include_map:
        exclude.remove("map")
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(*exclude))
    if not include_readings:
        (repo / "readings").mkdir(exist_ok=True)
    return repo


def materialise_readings(repo: Path, names: list[str] | None = None) -> list[str]:
    """Copy ``readings/*.md`` into a sandbox that was built without it.

    ``names=None`` copies all of them. Returns the filenames copied, so a test
    can state which prose it depended on instead of inheriting the whole archive.
    """
    source = ROOT / "readings"
    target = repo / "readings"
    target.mkdir(parents=True, exist_ok=True)
    chosen = sorted(names if names is not None else (p.name for p in source.glob("*.md")))
    for name in chosen:
        shutil.copy2(source / name, target / name)
    return chosen


# --------------------------------------------------------------------------- run
#: Tools whose ``main()`` accepts an argv list. ``validate_seed.py`` takes none.
ARGV_TOOLS = {
    "append_only_check.py",
    "belief_state.py",
    "date_axis.py",
    "inspect_inquiry.py",
    "learning_metrics.py",
    "note_index.py",
    "size_budget.py",
    "three_gates.py",
    "errata_audit.py",
    "read_log_backfill.py",
    "claim_wiring.py",
    "new_ledger_shard.py",
}


def run_tool(root: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    """Run ``tools/<tool>`` as a child process against ``root`` (the old way).

    Kept for the cases where process isolation is the thing under test: CLI
    argument parsing, concurrent writers, and a tool run from a directory that
    is not this checkout.
    """
    return subprocess.run(
        [sys.executable, *args], cwd=root, capture_output=True, text=True, timeout=timeout
    )


def run_tool_in_process(root: Path, *args: str, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    """Run ``tools/<tool>`` in THIS interpreter against ``root``.

    Why this reproduces the child process
    -------------------------------------
    Each tool binds ``ROOT = Path(__file__).resolve().parents[1]`` when it is
    imported, so importing ``tools/validate_seed.py`` from this checkout would
    read the live ledger, not the sandbox. The tool is therefore imported from a
    path list that starts with the sandbox's own ``tools/`` and with the sandbox
    as the working directory: the module resolved is the sandbox's copy, and its
    ``ROOT`` is the sandbox. The modules are dropped from ``sys.modules``
    afterwards, so one call cannot leak state into the next -- which is what the
    separate process guaranteed.

    ``timeout`` is accepted for signature compatibility and ignored: an
    in-process call cannot be killed from here. Every caller keeps a child
    process for anything long enough to need the deadline.

    Modules the HOST has already imported are displaced for the call. Without
    that, ``import validate_seed`` finds the checkout's own module in
    ``sys.modules`` (the test suite imports it) and the "sandbox" run validates
    the LIVE ledger: measured 2026-11-23, six tests in ``test_read_log`` passed
    rows that must fail. The displacement is by module NAME, because the host
    copy's file lives in this checkout, not under the sandbox.
    """
    tool = Path(args[0])
    argv = list(args[1:])
    module_name = tool.stem
    before_path, before_modules = list(sys.path), dict(sys.modules)
    sandbox_tools = Path(root).resolve() / tool.parent
    sandbox_names = {p.stem for p in sandbox_tools.glob("*.py")}
    shadowed = {n: m for n, m in before_modules.items() if n in sandbox_names}
    cwd = Path.cwd()
    out, err = io.StringIO(), io.StringIO()
    try:
        import os

        os.chdir(root)
        sys.path.insert(0, str(Path(root).resolve() / tool.parent))
        import importlib

        for name in shadowed:
            del sys.modules[name]
        module = importlib.import_module(module_name)
        main: Callable[..., Any] = module.main
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(argv) if tool.name in ARGV_TOOLS else main()
            except SystemExit as exc:
                code = 0 if exc.code is None else (exc.code if isinstance(exc.code, int) else 1)
    except BaseException as exc:  # noqa: BLE001 - reported as a failing exit code
        code = 1
        err.write(f"{type(exc).__name__}: {exc}\n")
    finally:
        import os

        os.chdir(cwd)
        sys.path[:] = before_path
        for name in [n for n in sys.modules if n not in before_modules]:
            del sys.modules[name]
        sys.modules.update(shadowed)
    return subprocess.CompletedProcess(args=list(args), returncode=int(code),
                                       stdout=out.getvalue(), stderr=err.getvalue())
