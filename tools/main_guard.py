#!/usr/bin/env python3
"""Report whether main is protected enough to keep a red pull request out.

Why this exists
---------------
Three times on 2026-11-20/21 a change landed on main while `validate` was red
(#998's session row, #1002's two registerless questions, and the merge that
followed).  Each time the repair cost a session an hour, and each time the
only append-only-safe response was an exception carried somewhere.  The
exceptions are now errata rows (``tools/validate_seed.py``: ``gate_waivers``),
which is the right home for *the debt*, but errata rows are not a fix for
*the cause*.  The cause is that main accepts merges whose required check has
not passed, and no file in this repository can close that: it is repository
configuration.

What this tool can and cannot do
--------------------------------
It reads ``/repos/{slug}/branches/main`` and looks at ``protected``.  Reading
that field needs only ``contents: read``; *setting* protection needs
administration write, which the token in this sandbox does not have
(measured 2026-11-21: PUT ``/branches/main/protection`` and POST ``/rulesets``
both return 403 "Resource not accessible by integration", while
``branches/main`` reports ``protected: false``).

So the tool does not pretend to fix anything.  It fails, loudly, while main
is unprotected, and prints the exact command that closes it.  A run that
cannot reach the API exits 2 and says so -- it does not report "fine" when it
does not know.

Usage
-----
    python3 tools/main_guard.py                 # human-readable status
    python3 tools/main_guard.py --command       # just the fix command
    python3 tools/main_guard.py --repo o/r      # explicit slug
    python3 tools/main_guard.py --strict        # exit 1 unless protected

Exit codes: 0 protected, 1 unprotected, 2 unknown (network or auth).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

DEFAULT_BRANCH = "main"
REQUIRED_CONTEXT = "validate"

FIX_COMMAND = """gh api -X PUT repos/{slug}/branches/main/protection --input - <<'JSON'
{{"required_status_checks":{{"strict":false,"contexts":["validate"]}},"enforce_admins":false,"required_pull_request_reviews":null,"restrictions":null}}
JSON"""


def repo_slug(explicit: str | None = None) -> str | None:
    """Work out owner/repo from the argument, the environment, or the remote."""
    if explicit:
        return explicit
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not url:
        return None
    if url.startswith("git@github.com:"):
        url = url.split("git@github.com:", 1)[1]
    elif "github.com/" in url:
        url = url.split("github.com/", 1)[1]
    else:
        return None
    return url.removesuffix(".git").strip("/") or None


def fetch_branch_state(slug: str, branch: str = DEFAULT_BRANCH) -> dict:
    """Return {'known': bool, 'protected': bool|None, 'detail': str}."""
    gh = shutil.which("gh")
    if not gh:
        return {"known": False, "protected": None, "detail": "gh is not installed"}
    proc = subprocess.run(
        [gh, "api", f"repos/{slug}/branches/{branch}"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return {
            "known": False,
            "protected": None,
            "detail": detail[0] if detail else f"gh exited {proc.returncode}",
        }
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"known": False, "protected": None, "detail": f"unparsable JSON: {exc}"}
    protected = payload.get("protected")
    if not isinstance(protected, bool):
        return {"known": False, "protected": None, "detail": "response has no boolean 'protected'"}
    return {"known": True, "protected": protected, "detail": ""}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=None, help="owner/repo (default: env or git remote)")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--command", action="store_true", help="print only the fix command")
    parser.add_argument("--strict", action="store_true", help="exit 0 only when main is protected")
    args = parser.parse_args(argv)

    slug = repo_slug(args.repo)
    if not slug:
        print("UNKNOWN: could not determine owner/repo (pass --repo)", file=sys.stderr)
        return 2

    if args.command:
        print(FIX_COMMAND.format(slug=slug))
        return 0

    state = fetch_branch_state(slug, args.branch)
    if not state["known"]:
        print(f"UNKNOWN: could not read {slug}@{args.branch}: {state['detail']}")
        print("  This tool will not report a merge gate as healthy when it cannot see it.")
        return 2

    if state["protected"]:
        print(
            f"OK: {slug}@{args.branch} is protected. "
            f"(Check that the required status context is {REQUIRED_CONTEXT!r}; "
            "reading the context list needs admin rights this token does not have.)"
        )
        return 0

    print(f"FAIL: {slug}@{args.branch} is NOT protected -- a red merge can land.")
    print(
        "  That is how #998 and #1002 reached main. The repair for those rows is now an\n"
        "  errata waiver (state/errata.d/), but the cause is repository configuration and\n"
        "  no file in this repository can close it. Run this, once, with an admin token:"
    )
    print()
    print(FIX_COMMAND.format(slug=slug))
    print()
    print(
        f"  After that, protect the branch and require the {REQUIRED_CONTEXT!r} check; this\n"
        "  guard turns green by itself and the errata waivers can be closed."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
