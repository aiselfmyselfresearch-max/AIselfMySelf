"""Tests for main_guard v2: policy conformance, not merely the protected flag.

The 2026-11-20/21 red merges (#998, #1002) landed while no protection was in
force; the repair (2026-11-21, repository settings) and every way it could
silently regress are invisible to a tool that only reads the boolean
`protected`.  These tests pin the v2 contract from
docs/2026-11-28-main-guard-policy-conformance.md section 4.2:

* OK only when the required `validate` context is present AND enforcement is
  `everyone`;
* a dropped context or a weakened enforcement level is FAIL -- protection can
  stay on while the merge gate is gone;
* `protected: true` without a readable protection payload is UNKNOWN, never
  OK -- a guard that reports fine when it cannot see the gate is the exact
  failure this repository keeps re-learning;
* extra required contexts only tighten the gate and are reported, not failed;
* exit codes are 0/1/2 and enforced in every mode (`--strict` is a kept
  compatibility flag, not a second code path).

No test in this module touches the network: `fetch_branch_state` is mocked at
the call boundary, and everything under test is a pure function of its result.
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def guard():
    return __import__("main_guard")


def protected_state(**overrides) -> dict:
    """A fetch_branch_state result shaped like the measured 2026-11-28 response.

    GET /repos/.../branches/main returned protected=true with a protection
    object carrying contexts=["validate"] (app_id 15368 is GitHub Actions) and
    enforcement_level="everyone" -- the posture the owner applied on
    2026-11-21.
    """
    state = {
        "known": True,
        "protected": True,
        "protection": {
            "enabled": True,
            "required_status_checks": {
                "enforcement_level": "everyone",
                "contexts": ["validate"],
                "checks": [{"context": "validate", "app_id": 15368}],
            },
        },
        "detail": "",
    }
    state.update(overrides)
    return state


def unknown_state(detail: str = "gh is not installed") -> dict:
    return {"known": False, "protected": None, "protection": None, "detail": detail}


def drop_protection(state: dict) -> dict:
    """protected stays true while the payload carries no readable posture."""
    return dict(state, protection=None)


class PolicyTests(unittest.TestCase):
    def test_the_policy_pins_validate_and_everyone(self):
        g = guard()
        self.assertEqual(
            g.POLICY,
            {"required_contexts": ("validate",), "enforcement_level": "everyone"},
        )

    def test_matching_posture_is_ok(self):
        verdict, checks = guard().evaluate(protected_state())
        self.assertEqual(verdict, "ok")
        self.assertEqual({c["level"] for c in checks}, {"ok"})

    def test_unprotected_is_fail_even_when_a_payload_is_present(self):
        state = protected_state(protected=False)
        verdict, checks = guard().evaluate(state)
        self.assertEqual(verdict, "fail")
        protected_check = next(c for c in checks if c["check"] == "protected")
        self.assertEqual(protected_check["level"], "fail")
        self.assertIn("required check has not passed", protected_check["detail"])

    def test_a_dropped_required_context_is_fail(self):
        # The regression the critique names: protected stays true, the gate is
        # gone.  A boolean-only guard reported this posture as OK.
        state = protected_state()
        state["protection"]["required_status_checks"]["contexts"] = ["tests"]
        verdict, checks = guard().evaluate(state)
        self.assertEqual(verdict, "fail")
        context_check = next(c for c in checks if c["check"] == "required_context")
        self.assertEqual(context_check["level"], "fail")
        self.assertIn("'validate'", context_check["detail"])
        self.assertIn("['tests']", context_check["detail"])

    def test_a_weakened_enforcement_level_is_fail(self):
        # Every merge in this repository is performed by the owner, so both
        # weakened levels exempt the only identity that ever merges.
        for level in ("non_admins", "off", None):
            with self.subTest(enforcement_level=level):
                state = protected_state()
                state["protection"]["required_status_checks"]["enforcement_level"] = level
                verdict, checks = guard().evaluate(state)
                self.assertEqual(verdict, "fail")
                enforcement = next(c for c in checks if c["check"] == "enforcement_level")
                self.assertEqual(enforcement["level"], "fail")

    def test_protected_but_unreadable_posture_is_unknown_not_ok(self):
        verdict, checks = guard().evaluate(drop_protection(protected_state()))
        self.assertEqual(verdict, "unknown")
        readable = next(c for c in checks if c["check"] == "protection_readable")
        self.assertEqual(readable["level"], "unknown")
        self.assertIn("not an OK", readable["detail"])

    def test_unknown_api_state_is_unknown(self):
        verdict, checks = guard().evaluate(unknown_state(detail="rate limited"))
        self.assertEqual(verdict, "unknown")
        self.assertEqual(checks[0]["check"], "reachable")
        self.assertEqual(checks[0]["detail"], "rate limited")

    def test_extra_required_contexts_are_reported_not_failed(self):
        state = protected_state()
        state["protection"]["required_status_checks"]["contexts"] = ["validate", "tests"]
        verdict, checks = guard().evaluate(state)
        self.assertEqual(verdict, "ok")
        context_check = next(c for c in checks if c["check"] == "required_context")
        self.assertEqual(context_check["level"], "ok")
        self.assertIn("tighten", context_check["detail"])

    def test_contexts_fall_back_to_the_checks_list(self):
        # Some responses carry only checks[{context, app_id}]; the flattened
        # view must read the context from there rather than fail blind.
        state = protected_state()
        del state["protection"]["required_status_checks"]["contexts"]
        verdict, checks = guard().evaluate(state)
        self.assertEqual(verdict, "ok")
        context_check = next(c for c in checks if c["check"] == "required_context")
        self.assertEqual(context_check["level"], "ok")


class ExitCodeAndOutputTests(unittest.TestCase):
    def run_main(self, argv: list[str], state: dict) -> tuple[int, str]:
        g = guard()
        out = io.StringIO()
        with mock.patch.object(g, "fetch_branch_state", return_value=state), redirect_stdout(out):
            code = g.main(argv)
        return code, out.getvalue()

    def test_exit_codes_are_enforced_in_every_mode(self):
        cases = [
            ([], protected_state(), 0),
            (["--strict"], protected_state(), 0),
            ([], protected_state(protected=False), 1),
            (["--strict"], protected_state(protected=False), 1),
            ([], drop_protection(protected_state()), 2),
            ([], unknown_state(), 2),
        ]
        for argv, state, expected in cases:
            with self.subTest(argv=argv, expected=expected):
                code, _ = self.run_main(["--repo", "o/r", *argv], state)
                self.assertEqual(code, expected)

    def test_json_mode_carries_verdict_and_measured_values(self):
        code, out = self.run_main(["--repo", "o/r", "--json"], protected_state())
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["verdict"], "ok")
        self.assertEqual(payload["repo"], "o/r")
        self.assertEqual(payload["protected"], True)
        self.assertEqual(payload["required_contexts"], ["validate"])
        self.assertEqual(payload["enforcement_level"], "everyone")
        self.assertEqual(payload["policy"]["required_contexts"], ["validate"])
        self.assertTrue(payload["checks"])

    def test_json_mode_reports_a_fail_as_a_fail(self):
        code, out = self.run_main(["--repo", "o/r", "--json"], protected_state(protected=False))
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["verdict"], "fail")

    def test_human_fail_names_the_fix_command_and_the_blocking_gate(self):
        code, out = self.run_main(["--repo", "o/r"], protected_state(protected=False))
        self.assertEqual(code, 1)
        self.assertIn("FAIL: o/r@main", out)
        self.assertIn("gh api -X PUT repos/o/r/branches/main/protection", out)
        self.assertIn("'validate', still required", out)

    def test_human_ok_names_the_measured_posture(self):
        _, out = self.run_main(["--repo", "o/r"], protected_state())
        self.assertIn("OK: o/r@main", out)
        self.assertIn("required contexts=['validate']", out)
        self.assertIn("OK: enforcement_level: everyone", out)

    def test_command_mode_prints_only_the_fix_command(self):
        code, out = self.run_main(["--repo", "o/r", "--command"], unknown_state())
        self.assertEqual(code, 0)
        self.assertIn("gh api -X PUT repos/o/r/branches/main/protection", out)

    def test_fix_command_reproduces_the_applied_posture(self):
        # The command must restore exactly what the owner applied on
        # 2026-11-21: one required context, admins included.  v1 proposed
        # enforce_admins:false, which would have hollowed the gate for the
        # only identity that merges here.
        g = guard()
        command = g.FIX_COMMAND.format(slug="o/r")
        self.assertIn("repos/o/r/branches/main/protection", command)
        self.assertIn('"contexts":["validate"]', command)
        self.assertIn('"enforce_admins":true', command)
        self.assertIn('"strict":false', command)


if __name__ == "__main__":
    unittest.main()
