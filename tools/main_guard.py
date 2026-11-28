#!/usr/bin/env python3
"""Check that main's branch protection still matches this repository's merge policy.

History
-------
Three times on 2026-11-20/21 a change landed on main while `validate` was red
(#998's session row, #1002's two registerless questions, and the merge that
followed).  The cause was repository configuration, not any file in this
repository: main accepted merges whose required check had not passed, and the
token available to the agent could not PUT /branches/main/protection (403,
measured 2026-11-21).  The debt of those rows lives in state/errata.d/
(``tools/validate_seed.py``: ``gate_waivers``); the cause was closed on
2026-11-21 when the repository owner applied branch protection from the
repository settings.

What this tool verifies (v2, 2026-11-28)
----------------------------------------
Not merely that main is protected, but that the protection matches ``POLICY``
below, because both regressions that matter are invisible to a boolean check:

  * the required ``validate`` context is dropped -- protection stays on while
    the merge gate is gone;
  * enforcement is weakened below ``everyone`` -- admins get exempted, and
    every merge in this repository is performed by the owner, so an admin
    exemption exempts the only identity that ever merges.

It reads GET ``/repos/{slug}/branches/main`` (``contents: read`` suffices).
The ``protection`` object of that response exposes the required status
contexts and the enforcement level.  The full protection payload (GET
``/repos/{slug}/branches/main/protection``) needs administration rights that
no token in this sandbox holds (403, measured 2026-11-21 and again
2026-11-28); the fields only that endpoint carries (``strict``,
``allow_force_pushes``, ...) are therefore out of reach and out of scope.

Verdicts: OK only when every policy item is confirmed.  A response that says
``protected: true`` without a readable ``protection`` object is UNKNOWN, not
OK -- a guard that reports fine when it cannot see the gate is the exact
failure mode this repository keeps re-learning.  Until 2026-11-21 this tool
failed every day by design; since the owner applied protection it has been
green, and its job now is to turn red on the day the posture drifts, and
print the one command that restores it.  Design record:
``docs/2026-11-28-main-guard-policy-conformance.md``.

Usage
-----
    python3 tools/main_guard.py                 # human-readable status
    python3 tools/main_guard.py --json          # machine-readable verdict
    python3 tools/main_guard.py --command       # just the fix command
    python3 tools/main_guard.py --repo o/r      # explicit slug
    python3 tools/main_guard.py --strict        # kept for compatibility:
                                                # since v2 both modes enforce

Exit codes: 0 policy matched, 1 policy violated, 2 unknown (network, auth, or
an unreadable protection payload).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

DEFAULT_BRANCH = "main"

#: The merge posture this repository intends.  Why exactly one required
#: context, and why the regression suite is deliberately advisory, is recorded
#: in docs/2026-11-28-main-guard-policy-conformance.md section 4.5: `validate`
#: is the gate whose redness landed the three 2026-11-20/21 merges, it runs in
#: seconds, and its name is not tied to the shard patterns of the test matrix.
#: `everyone` is load-bearing: every merge here is performed by the owner, so
#: `non_admins` or `off` would exempt the only identity that ever merges --
#: `protected: true` with a hollow gate, which a boolean check cannot see.
POLICY = {
    "required_contexts": ("validate",),
    "enforcement_level": "everyone",
}

REQUIRED_CONTEXT = POLICY["required_contexts"][0]

#: Reproduces the posture the owner applied on 2026-11-21 and that this tool
#: verifies: one required context, admins included, no review requirement, no
#: strict up-to-date requirement (a high-cadence archive must not force a
#: rebase before every merge).  Running it needs administration rights; the
#: tokens this repository's automations hold measure 403 on it (2026-11-21,
#: 2026-11-28), so it is a command for the repository owner, not a repair any
#: session can apply.
FIX_COMMAND = """gh api -X PUT repos/{slug}/branches/main/protection --input - <<'JSON'
{{"required_status_checks":{{"strict":false,"contexts":["validate"]}},"enforce_admins":true,"required_pull_request_reviews":null,"restrictions":null,"allow_force_pushes":false,"allow_deletions":false}}
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
    """Return {'known': bool, 'protected': bool|None, 'protection': dict|None, 'detail': str}."""
    gh = shutil.which("gh")
    if not gh:
        return {"known": False, "protected": None, "protection": None, "detail": "gh is not installed"}
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
            "protection": None,
            "detail": detail[0] if detail else f"gh exited {proc.returncode}",
        }
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {"known": False, "protected": None, "protection": None, "detail": f"unparsable JSON: {exc}"}
    protected = payload.get("protected")
    if not isinstance(protected, bool):
        return {
            "known": False,
            "protected": None,
            "protection": None,
            "detail": "response has no boolean 'protected'",
        }
    protection = payload.get("protection")
    if not isinstance(protection, dict):
        protection = None
    return {"known": True, "protected": protected, "protection": protection, "detail": ""}


def measured_status_checks(protection: dict | None) -> dict:
    """Flatten the readable protection payload into {contexts, enforcement_level}.

    GitHub reports the contexts both as a plain list and as checks with app
    ids; some responses carry only one of the two, so prefer the list and fall
    back to the checks.
    """
    if not isinstance(protection, dict):
        return {}
    rsc = protection.get("required_status_checks")
    if not isinstance(rsc, dict):
        rsc = {}
    contexts = rsc.get("contexts")
    if not isinstance(contexts, list):
        checks = rsc.get("checks")
        contexts = [
            item.get("context")
            for item in (checks if isinstance(checks, list) else [])
            if isinstance(item, dict) and isinstance(item.get("context"), str)
        ]
    return {"contexts": contexts, "enforcement_level": rsc.get("enforcement_level")}


def evaluate(state: dict) -> tuple[str, list[dict]]:
    """Apply POLICY to a fetch_branch_state result.

    Returns (verdict, checks).  verdict is 'ok' | 'fail' | 'unknown'; each
    check is {'check': str, 'level': 'ok'|'fail'|'unknown', 'detail': str}.
    FAIL beats UNKNOWN: a measured violation is reported even when another
    part of the posture could not be read.
    """
    checks: list[dict] = []
    if not state["known"]:
        checks.append({"check": "reachable", "level": "unknown", "detail": state["detail"]})
        return "unknown", checks

    if state["protected"]:
        checks.append({"check": "protected", "level": "ok", "detail": "true"})
    else:
        checks.append(
            {"check": "protected", "level": "fail", "detail": "false -- a merge whose required check has not passed can land"}
        )

    protection = state["protection"]
    if protection is None:
        checks.append(
            {
                "check": "protection_readable",
                "level": "unknown",
                "detail": "protected is true but the response carries no protection object; the "
                          "required context cannot be verified, so this is not an OK",
            }
        )
    else:
        checks.append({"check": "protection_readable", "level": "ok", "detail": "present"})
        rsc = measured_status_checks(protection)
        contexts = rsc.get("contexts") or []
        if REQUIRED_CONTEXT in contexts:
            extra = [c for c in contexts if c != REQUIRED_CONTEXT]
            detail = f"required contexts={contexts}"
            if extra:
                detail += f"; {extra} only tighten the gate (design record, section 4.5)"
            checks.append({"check": "required_context", "level": "ok", "detail": detail})
        else:
            checks.append(
                {
                    "check": "required_context",
                    "level": "fail",
                    "detail": f"'{REQUIRED_CONTEXT}' is not required (contexts={contexts}); protection "
                              "stays on while the merge gate is gone",
                }
            )
        level = rsc.get("enforcement_level")
        if level == POLICY["enforcement_level"]:
            checks.append({"check": "enforcement_level", "level": "ok", "detail": str(level)})
        else:
            checks.append(
                {
                    "check": "enforcement_level",
                    "level": "fail",
                    "detail": f"{level!r} != {POLICY['enforcement_level']!r}; an exemption for admins "
                              "exempts the only identity that merges in this repository",
                }
            )

    if any(c["level"] == "fail" for c in checks):
        return "fail", checks
    if any(c["level"] == "unknown" for c in checks):
        return "unknown", checks
    return "ok", checks


EXIT_CODES = {"ok": 0, "fail": 1, "unknown": 2}


def human_lines(verdict: str, checks: list[dict], slug: str, branch: str) -> list[str]:
    """Render the verdict the way the workflow log reads it."""
    heads = {
        "ok": f"OK: {slug}@{branch} matches the merge policy (POLICY in tools/main_guard.py).",
        "fail": f"FAIL: {slug}@{branch} does not match the merge policy (POLICY in tools/main_guard.py).",
        "unknown": f"UNKNOWN: {slug}@{branch} could not be judged -- this tool will not report a merge gate as healthy when it cannot see it.",
    }
    lines = [heads[verdict]]
    for check in checks:
        lines.append(f"  {check['level'].upper()}: {check['check']}: {check['detail']}")
    if verdict == "fail":
        lines.append(
            "  That is how the red merges of 2026-11-20/21 (#998, #1002) were possible. The repair for\n"
            "  those rows is an errata waiver (state/errata.d/), but the cause is repository\n"
            "  configuration. Run this, once, with an admin token (agent tokens measure 403):"
        )
        lines.append("")
        lines.append(FIX_COMMAND.format(slug=slug))
        lines.append("")
        lines.append(
            f"  The next scheduled run turns green by itself once the posture matches POLICY again;\n"
            f"  nothing here blocks a merge -- the check that blocks red merges is '{REQUIRED_CONTEXT}', still required."
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=None, help="owner/repo (default: env or git remote)")
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--command", action="store_true", help="print only the fix command")
    parser.add_argument("--json", action="store_true", help="print the verdict and measured values as JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="kept for compatibility; since v2 both modes enforce the exit code",
    )
    args = parser.parse_args(argv)

    slug = repo_slug(args.repo)
    if not slug:
        print("UNKNOWN: could not determine owner/repo (pass --repo)", file=sys.stderr)
        return 2

    if args.command:
        print(FIX_COMMAND.format(slug=slug))
        return 0

    state = fetch_branch_state(slug, args.branch)
    verdict, checks = evaluate(state)

    if args.json:
        measured = measured_status_checks(state["protection"])
        print(
            json.dumps(
                {
                    "verdict": verdict,
                    "repo": slug,
                    "branch": args.branch,
                    "protected": state["protected"],
                    "required_contexts": measured.get("contexts"),
                    "enforcement_level": measured.get("enforcement_level"),
                    "policy": {**POLICY, "required_contexts": list(POLICY["required_contexts"])},
                    "checks": checks,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return EXIT_CODES[verdict]

    for line in human_lines(verdict, checks, slug, args.branch):
        print(line)
    return EXIT_CODES[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
