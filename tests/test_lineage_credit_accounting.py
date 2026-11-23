"""Regression tests for tools/lineage_credit_accounting.py.

The audit is a mirror, not a gate: these tests pin its arithmetic against the
engine and pin the *shape* of the finding on a synthetic ledger, so that a
future change to `belief_state.py` shows up here as a changed measurement
rather than as a silently different BELIEF_MAP.

See readings/2026-11-14-the-verdict-arrived-before-the-hypothesis.md.
"""
import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state
import lineage_credit_accounting as lca


def _hyp(hid, parents=(), created="2026-11-10T00:00:00Z", qid="Q-QA"):
    return {
        "hypothesis_id": hid,
        "session_id": "SESSION-TEST",
        "created_at": created,
        "question_ids": [qid],
        "title": hid,
        "proposition": hid,
        "scope_conditions": ["test"],
        "exclusion_clause": "test",
        "lineage_op": "refines" if parents else "root",
        "parent_hypothesis_ids": list(parents),
        "status": "active",
    }


def _evl(eid, target, created="2026-11-10T00:00:00Z", spawned=None,
         verdict="narrows_scope", evidence="reproducible_script", scope_heir=None):
    row = {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": created,
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": evidence,
        "summary": "synthetic evaluation for the lineage credit audit test",
        "compared_against_hypothesis_ids": [],
    }
    if spawned is not None:
        row["spawned_hypothesis_ids"] = list(spawned)
    if scope_heir is not None:
        row["scope_inherited_by_hypothesis_ids"] = list(scope_heir)
    return row


class SyntheticLineageTests(unittest.TestCase):
    """The mechanism, isolated from the live ledger."""

    def test_fallback_credits_a_child_registered_after_the_evaluation(self):
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-12T09:00:00Z"),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-P", created="2026-11-11T09:00:00Z"),
            },
            "errata": {},
        }
        state = belief_state.compute_belief_state(cols)
        child = next(h for h in state["questions"]["Q-QA"]["hypotheses"]
                     if h["hypothesis_id"] == "HYP-C")
        # The child has never been evaluated, yet it holds positive log-odds.
        self.assertEqual(child["direct_eval_count"], 0)
        self.assertGreater(child["log_odds"], 0.0)

        report = lca.audit(cols)
        self.assertEqual(report["routes"], {"fallback": 1})
        self.assertEqual(len(report["postdated_strict_pairs"]), 1)
        self.assertEqual(len(report["postdated_day_pairs"]), 1)
        pair = report["postdated_strict_pairs"][0]
        self.assertEqual(pair["child_hypothesis_id"], "HYP-C")
        # The audited share must equal what the engine actually added.
        self.assertAlmostEqual(pair["log_odds_share"], child["log_odds"], places=4)

    def test_explicit_spawn_is_not_post_dated_credit(self):
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-12T09:00:00Z"),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-P", created="2026-11-11T09:00:00Z",
                              spawned=["HYP-C"]),
            },
            "errata": {},
        }
        report = lca.audit(cols)
        self.assertEqual(report["routes"], {"explicit": 1})
        # An explicit list is the session's own claim about where the mass goes.
        # The audit reports it, but does not call it a fallback artifact.
        self.assertEqual(report["postdated_strict_pairs"], [])
        self.assertEqual(report["transfers"][0]["route"], "explicit")

    def test_scope_inheritance_is_mirrored_as_inherited_credit(self):
        """`scope_inherited_by_hypothesis_ids` pays the heir exactly like `spawned`.

        belief_state L684-698 credits the **union** of the two heir fields
        (P-5, 2026-11-16).  This mirror read only `spawned` from 2026-11-14
        until 2026-11-18, so a never-evaluated heir named through the *scope*
        field held 0.75*delta of log-odds the audit could not account for, and
        `test_inherited_share_explains_unevaluated_hypotheses_log_odds` broke on
        the live ledger (Q-002/HYP-20261118-f413b3, EVL-20261118-fdc642).  The
        heir here is the target's parent -- the case P-5 was written for -- and
        is deliberately not a lineage child of the target, so the fallback
        cannot supply the credit either.
        """
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-12T09:00:00Z"),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-C", created="2026-11-13T09:00:00Z",
                              scope_heir=["HYP-P"]),
            },
            "errata": {},
        }
        state = belief_state.compute_belief_state(cols)
        heir = next(h for h in state["questions"]["Q-QA"]["hypotheses"]
                    if h["hypothesis_id"] == "HYP-P")
        self.assertEqual(heir["direct_eval_count"], 0)
        self.assertGreater(heir["log_odds"], 0.0)

        report = lca.audit(cols)
        self.assertEqual(report["routes"], {"scope": 1})
        self.assertEqual(report["transfers"][0]["credit_field"],
                         "scope_inherited_by_hypothesis_ids")
        # The audited share must equal what the engine actually added.
        self.assertAlmostEqual(report["inherited_log_odds"]["HYP-P"],
                               heir["log_odds"], places=4)
        self.assertAlmostEqual(
            report["inherited_log_odds"]["HYP-P"]
            + report["compared_penalty_log_odds"].get("HYP-P", 0.0),
            heir["log_odds"], places=4,
        )
        # A name the row wrote itself is not a fallback artifact -- not even
        # though this heir *predates* the evaluation, which is the normal order
        # for a parent that keeps the remaining scope.
        self.assertEqual(report["postdated_strict_pairs"], [])
        self.assertEqual(report["postdated_day_pairs"], [])

    def test_the_two_heir_fields_split_one_share(self):
        """The engine divides 0.75*delta by the size of the union, not per field.

        Naming one heir in each field must not pay two shares; it must pay one
        share split in two, and `credit_field` must still say which field named
        which heir -- the reason the engine keeps two names at all.
        """
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C1": _hyp("HYP-C1", parents=["HYP-P"], created="2026-11-12T00:00:00Z"),
                "HYP-C2": _hyp("HYP-C2", parents=["HYP-P"], created="2026-11-12T00:00:00Z"),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-P", spawned=["HYP-C1"],
                              scope_heir=["HYP-C2"]),
            },
            "errata": {},
        }
        report = lca.audit(cols)
        self.assertEqual(report["routes"], {"explicit": 1})
        fields = {t["child_hypothesis_id"]: t["credit_field"] for t in report["transfers"]}
        self.assertEqual(fields, {"HYP-C1": "spawned_hypothesis_ids",
                                  "HYP-C2": "scope_inherited_by_hypothesis_ids"})
        self.assertAlmostEqual(report["inherited_log_odds"]["HYP-C1"],
                               report["inherited_log_odds"]["HYP-C2"], places=6)
        state = belief_state.compute_belief_state(cols)
        for hid in ("HYP-C1", "HYP-C2"):
            heir = next(x for x in state["questions"]["Q-QA"]["hypotheses"]
                        if x["hypothesis_id"] == hid)
            self.assertEqual(heir["direct_eval_count"], 0)
            self.assertAlmostEqual(report["inherited_log_odds"][hid],
                                   heir["log_odds"], places=4)

    def test_render_shows_every_route_it_counts(self):
        """A route the mirror counts must also appear in the printed line.

        `routes` summed to the transferring-verdict total (that is
        `test_route_counts_partition_the_transferring_verdicts`) while the
        display listed only three of the labels, so rows routed by
        `scope_inherited_by_hypothesis_ids` alone were counted and not shown.
        The mirror's own output is what a reader calibrates against; a counted
        route that is not displayed is the same defect as a route that is not
        counted.
        """
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"]),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-C", scope_heir=["HYP-P"]),
            },
            "errata": {},
        }
        report = lca.audit(cols)
        state = belief_state.compute_belief_state(cols)
        text = lca.render(report, state, None, None, None)
        line = next(l for l in text.splitlines() if "射程限定・反証の評価" in l)
        for label in ("明示", "射程継承のみ", "フォールバック", "子なし"):
            self.assertIn(label, line)
        self.assertIn("射程継承のみ 1", line)

    def test_date_only_stamps_are_bounded_not_asserted(self):
        """Same-day, time-less rows: the two orderings must disagree."""
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P", created="2026-11-10"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-11T15:00:00Z"),
            },
            "evaluations": {
                "EVL-1": _evl("EVL-1", "HYP-P", created="2026-11-11"),
            },
            "errata": {},
        }
        report = lca.audit(cols)
        self.assertEqual(report["postdated_day_pairs"], [])       # lower bound
        self.assertEqual(len(report["postdated_strict_pairs"]), 1)  # upper bound

    def test_no_child_means_no_transfer(self):
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {"HYP-P": _hyp("HYP-P")},
            "evaluations": {"EVL-1": _evl("EVL-1", "HYP-P")},
            "errata": {},
        }
        report = lca.audit(cols)
        self.assertEqual(report["routes"], {"no_child": 1})
        self.assertEqual(report["transfers"], [])

    def test_refutes_share_is_larger_than_narrows_share(self):
        base = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-12T00:00:00Z"),
            },
            "errata": {},
        }
        shares = {}
        for verdict in ("narrows_scope", "refutes_unconditioned"):
            cols = copy.deepcopy(base)
            cols["evaluations"] = {"EVL-1": _evl("EVL-1", "HYP-P", verdict=verdict)}
            shares[verdict] = lca.audit(cols)["transfers"][0]["log_odds_share"]
        self.assertAlmostEqual(shares["narrows_scope"], 0.75 * 1.35 * 0.65, places=6)
        self.assertAlmostEqual(shares["refutes_unconditioned"], 0.95 * 1.35 * 0.65, places=6)

    def test_audit_does_not_mutate_the_ledgers_it_reads(self):
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"], created="2026-11-12T00:00:00Z"),
            },
            "evaluations": {"EVL-1": _evl("EVL-1", "HYP-P")},
            "errata": {},
        }
        before = json.dumps(cols, sort_keys=True, ensure_ascii=False)
        lca.audit(cols)
        report = lca.audit(cols)
        lca.counterfactual(cols, report)
        lca.probe_newborn(cols, ("Q-QA",))
        self.assertEqual(json.dumps(cols, sort_keys=True, ensure_ascii=False), before)


class LiveLedgerTests(unittest.TestCase):
    """The arithmetic must agree with the engine on the real ledger."""

    @classmethod
    def setUpClass(cls):
        cls.cols = belief_state.load_belief_ledgers()
        cls.report = lca.audit(cls.cols)
        cls.state = belief_state.compute_belief_state(cls.cols)

    def test_inherited_share_explains_unevaluated_hypotheses_log_odds(self):
        """For an active, never-evaluated hypothesis, log-odds == inherited share.

        This is the audit's calibration: if the engine's accounting changes,
        this equality breaks and the report's numbers must be re-measured.

        SESSION-20261114-146bc0 removed the `checked > 0` requirement that used to
        sit at the end of this test. That assertion demanded a CENSUS of the live
        ledger -- "at least one active hypothesis has never been evaluated" -- and
        the population legitimately emptied: HYP-20261113-3a106a received
        EVL-20261114-44f8ee upstream and HYP-20261113-17ea95 received
        EVL-20261114-913eea in this session. The test then failed on clean main
        with no defect in the engine.

        This is the same error as the removed 0.255/0.844 KL gates and as the
        direction-asserting newborn test: asserting a property of how many rows
        happen to exist, rather than a property of the mechanism. The equality
        below is still checked for every qualifying hypothesis; when none
        qualify, the test is vacuously true, which is correct -- there is nothing
        to calibrate against. `test_inherited_share_matches_on_a_synthetic_newborn`
        keeps the calibration non-vacuous regardless of the live census.
        """
        checked = 0
        for qid, q in self.state["questions"].items():
            for h in q["hypotheses"]:
                if h["direct_eval_count"] != 0 or h["initial_status"] != "active":
                    continue
                if h["errata_flags"]:
                    continue
                inherited = self.report["inherited_log_odds"].get(h["hypothesis_id"], 0.0)
                penalty = self.report["compared_penalty_log_odds"].get(h["hypothesis_id"], 0.0)
                self.assertAlmostEqual(
                    inherited + penalty, h["log_odds"], places=3,
                    msg=(f"{qid}/{h['hypothesis_id']}: inherited {inherited} + compared "
                         f"{penalty} vs log_odds {h['log_odds']}"),
                )
                checked += 1

    def test_voided_row_pays_no_heir_credit_in_engine_or_audit(self):
        """A row the engine voided must pay no heir credit in the audit either.

        Regression for a divergence that ran live for two days.  The engine has
        honoured ``weight_effect: "void_row"`` since 2026-11-16; the first two live
        voided rows were written on 2026-11-17 (``ERR-20261117-b1e0ed`` /
        ``-5756c0``, both ``status: "annotated"``, so both count as live corrections).
        This mirror counted every evaluation row regardless.

        The error stayed invisible because the calibration equality below only visits
        active hypotheses with no direct evaluation, and both 2026-11-17 voids paid a
        hypothesis that has 14 of them.  A row written on 2026-11-19 voided a
        ``narrows_scope`` whose heir *was* in that loop, and put engine and audit
        0.1625 apart on ``HYP-20261119-8b3e04``.

        Measured at 9316a5b, before that row existed: the mirror reported
        ``HYP-20261114-874658`` inherited 9.15 where the voided rows leave 8.25.
        The synthetic fixture below asserts the mechanism without depending on which
        rows happen to be voided live.
        """
        cols = {
            "questions": {"Q-QA": {"question_id": "Q-QA", "question": "test"}},
            "hypotheses": {
                "HYP-P": _hyp("HYP-P"),
                "HYP-C": _hyp("HYP-C", parents=["HYP-P"]),
            },
            "evaluations": {
                "EVL-VOID": _evl("EVL-VOID", "HYP-P", created="2026-11-13T09:00:00Z"),
            },
            "errata": {
                "ERR-1": {
                    "errata_id": "ERR-1",
                    "subject_type": "evaluation",
                    "subject_id": "EVL-VOID",
                    "claim": "the row's weight is withdrawn",
                    "claim_location": "test",
                    "check": {"kind": "manual", "params": {}},
                    "verdict": "contradicted",
                    "status": "corrected",
                    "weight_effect": "void_row",
                    "note": "test",
                    "created_at": "2026-11-19",
                },
            },
        }
        report = lca.audit(cols)
        state = belief_state.compute_belief_state(cols)
        heir = next(h for h in state["questions"]["Q-QA"]["hypotheses"]
                    if h["hypothesis_id"] == "HYP-C")
        self.assertEqual(report["routes"], {})
        self.assertEqual(report["inherited_log_odds"].get("HYP-C", 0.0), 0.0)
        self.assertAlmostEqual(
            report["inherited_log_odds"].get("HYP-C", 0.0)
            + report["compared_penalty_log_odds"].get("HYP-C", 0.0),
            heir["log_odds"],
            places=4,
        )

    def test_inherited_share_matches_on_a_synthetic_newborn(self):
        """Calibration that cannot go vacuous when the live census empties.

        Attach a fresh child to a real parent, give it no evaluation of its own,
        and require inherited + compared == log_odds. Asserts the mechanism, not
        the direction of any live metric.
        """
        import copy
        cols = copy.deepcopy(self.cols)
        parent = "HYP-20261113-a35ee5"
        self.assertIn(parent, cols["hypotheses"])
        child_id = "HYP-TEST-NEWBORN"
        child = dict(cols["hypotheses"][parent])
        child["hypothesis_id"] = child_id
        child["parent_hypothesis_ids"] = [parent]
        child["lineage_op"] = "splits"
        child["status"] = "active"
        cols["hypotheses"][child_id] = child
        state = belief_state.compute_belief_state(cols)
        report = lca.audit(cols)
        h = next((x for q in state["questions"].values() for x in q["hypotheses"]
                  if x["hypothesis_id"] == child_id), None)
        self.assertIsNotNone(h, "synthetic child missing from belief state")
        self.assertEqual(h["direct_eval_count"], 0)
        inherited = report["inherited_log_odds"].get(child_id, 0.0)
        self.assertNotEqual(inherited, 0.0, "calibration would be vacuous")
        penalty = report["compared_penalty_log_odds"].get(child_id, 0.0)
        self.assertAlmostEqual(inherited + penalty, h["log_odds"], places=3)

    def test_route_counts_partition_the_transferring_verdicts(self):
        # Voided rows are excluded from the denominator as well as from the routes:
        # the engine withdraws their weight entirely (2026-11-16 P-6), so a partition
        # that counted them would demand the audit book credit the engine does not pay.
        voided = lca.voided_evaluation_ids(self.cols.get("errata", {}))
        total = sum(1 for eid, e in self.cols["evaluations"].items()
                    if eid not in voided
                    and e.get("target_hypothesis_id") in self.cols["hypotheses"]
                    and e.get("verdict") in lca.TRANSFERRING_VERDICTS)
        self.assertEqual(sum(self.report["routes"].values()), total)

    def test_day_bound_does_not_exceed_strict_bound(self):
        self.assertLessEqual(len(self.report["postdated_day_pairs"]),
                             len(self.report["postdated_strict_pairs"]))

    def test_post_dated_credit_is_a_subset_of_fallback_credit(self):
        for t in self.report["postdated_strict_pairs"]:
            self.assertEqual(t["route"], "fallback")

    def test_counterfactual_only_moves_questions_with_denied_credit(self):
        cf = lca.counterfactual(self.cols, self.report)
        for qid, row in cf.items():
            if not row["denied_log_odds"]:
                self.assertEqual(row["before"]["kl_from_uniform_bits"],
                                 row["after"]["kl_from_uniform_bits"], qid)
                self.assertEqual(row["before"]["top_hypothesis_id"],
                                 row["after"]["top_hypothesis_id"], qid)

    def test_newborn_probe_moves_the_distribution_without_any_evaluation(self):
        """An unevaluated child changes the reported learning metrics.

        The *direction* is deliberately not asserted. The first draft of this
        test required D_KL to rise for every core question; when PR #753 landed
        on main during CI, Q-003 went 2.0804 -> 2.0783 and the test failed. The
        measurement was fine and the assertion was wrong: adding a hypothesis
        both grows n (raising D_KL from a uniform 1/n prior) and spreads mass
        onto a new entrant (lowering it), and which term wins depends on the
        live leader. Requiring one direction would reward a preferred outcome,
        the error already recorded at tests/test_belief_learning.py L64-65.

        What is invariant is the mechanism: a row with no evidence behind it
        moves the numbers the archive reports as learning.
        """
        probe = lca.probe_newborn(self.cols, belief_state.CORE_QUESTIONS)
        self.assertTrue(probe)
        moved = 0
        for qid, row in probe.items():
            child = row["probe_child"]
            self.assertEqual(child["direct_eval_count"], 0, qid)
            # Never evaluated, yet never penalised either: the fallback can
            # only add to a child, so its log-odds cannot go negative.
            self.assertGreaterEqual(child["log_odds"], 0.0, qid)
            self.assertEqual(child["uncertainty"], 1.0, qid)
            if (abs(row["after"]["kl_from_uniform_bits"] - row["before"]["kl_from_uniform_bits"]) > 1e-4
                    or abs(row["after"]["gen1_plus_mass"] - row["before"]["gen1_plus_mass"]) > 1e-4):
                moved += 1
        self.assertGreater(moved, 0, "an unevaluated child moved no reported metric")

    def test_zero_eig_questions_still_print_a_priority_pair(self):
        """The artifact the report names: EIG 0.0000 with a printed target.

        ERR-20261114-51ace1 (2026-11-14). This test used to assert
        ``top > 0.99`` whenever a question's EIG rounded to 0.0. That was a
        statement about one ledger state, not about the engine: it held while
        Q-002 was 99.37% vs 0.62%, and broke the moment an evaluation moved
        5.16 points from the leader to its narrowed child (99.37 -> 94.21,
        0.62 -> 5.77). EIG is ``p_a * p_b * (u_a + u_b)`` over ACTIVE
        hypotheses, so it can round to 0.0000 while the leader sits at 94%
        (u_a + u_b ~ 0.88, product < 5e-5). The printed pair is therefore a
        shape that must survive a non-degenerate leader; the distance from 1.0
        is a measurement, and it belongs to READING_MAP, not to this assertion.
        """
        for qid, q in self.state["questions"].items():
            pair = q.get("top_competing_pair")
            if not q["hypotheses"] or len(q["hypotheses"]) < 2:
                continue
            self.assertIsNotNone(pair, qid)
            self.assertIn("left_hypothesis_id", pair)
            self.assertIn("right_hypothesis_id", pair)
            self.assertGreaterEqual(pair["expected_info_gain"], 0.0, qid)
            top = q["hypotheses"][0]["posterior"]
            # A pair is only meaningful if the question is still contested:
            # a leader at certainty would leave nothing to discriminate.
            # When the leader is already certain (posterior == 1.0) the pair
            # carries no discriminative information, so skip the bound check.
            if top < 1.0:
                self.assertLess(top, 1.0, qid)

    def test_cli_exits_zero_and_writes_nothing(self):
        import subprocess
        before = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "lineage_credit_accounting.py"), "--json"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("audit", payload)
        self.assertIn("questions", payload)
        after = {p: p.read_bytes() for p in (ROOT / "state").rglob("*.jsonl")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
