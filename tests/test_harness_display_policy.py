"""Tests for the five harness changes adopted on 2026-11-23.

Why this file exists
--------------------
The six proposals in
``readings/2026-11-23-coarsening-concentrates-and-what-the-harness-should-change.md``
were measured, not guessed: the detail block was 80.6% of ``BELIEF_MAP.md``
while 88 of 93 hypotheses held <1% of the mass; two questions recommended a pair
whose combined mass was 0.0000 and flagged it 「未飽和」; family totals looked like
agreement while 68–99.7% of each family's mass sat in one hypothesis; 34 of 93
hypotheses carried more than one question and no row declared which one it was
primarily about; and no session row said which accounting basis it read.

Each test below pins the *mechanism* the change introduced, never the direction
or the size of a live-ledger quantity -- so writing to the ledger cannot break
this file, which is the mistake three earlier sessions paid for.

What is deliberately not asserted
---------------------------------
* No test compares a rendered byte count against a threshold: the compression
  is checked by "the unselected hypothesis keeps a line and loses its
  proposition", not by "the file is smaller than N".
* No test pins how many hypotheses exist, or which one leads.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402


def hyp(
    hid: str,
    *,
    posterior: float,
    question_ids=("Q-001",),
    parents=(),
    title: str | None = None,
    proposition: str | None = None,
    scope=("条件A",),
    exclusion: str = "この条件が観測されれば棄却される。",
    created_at: str = "2026-11-01",
    **extra,
) -> dict:
    rec = {
        "hypothesis_id": hid,
        "title": title or f"仮説{hid}",
        "proposition": proposition or f"命題{hid}の本文",
        "scope_conditions": list(scope),
        "exclusion_clause": exclusion,
        "lineage_op": "refines" if parents else "root",
        "generation": 1 if parents else 0,
        "effective_status": "active",
        "initial_status": "active",
        "uncertainty": 0.4,
        "posterior": posterior,
        "prior": 0.1,
        "parent_hypothesis_ids": list(parents),
        "children_hypothesis_ids": [],
        "direct_eval_count": 2,
        "adversarial_eval_count": 1,
        "supporting_material_ids": [],
        "counter_material_ids": [],
        "source_note_ids": [],
        "errata_flags": [],
        "question_ids": list(question_ids),
        "created_at": created_at,
        "log_odds": 0.0,
        "primary_question_id": extra.pop("primary_question_id", ""),
        "primary_question_id_source": "declared" if extra.get("primary_question_id") else "undecided",
        "primary_question_id_derived": (list(question_ids) or [""])[0],
        "multi_question": len(question_ids) > 1,
        "family_root_hypothesis_id": extra.pop("family_root_hypothesis_id", hid),
    }
    rec.update(extra)
    return rec


def state_with(hypotheses, *, families=None, multi=None) -> dict:
    total = sum(h["posterior"] for h in hypotheses)
    return {
        "total_hypotheses": len(hypotheses),
        "total_evaluations": 0,
        "core_priority_ranking": ["Q-001"],
        "belief_basis": "default",
        "multi_question_hypotheses": multi or {
            "multi_question": sum(1 for h in hypotheses if h["multi_question"]),
            "with_primary": sum(1 for h in hypotheses if h["primary_question_id"]),
            "without_primary": sum(1 for h in hypotheses if not h["primary_question_id"]),
        },
        "questions": {
            "Q-001": {
                "question_id": "Q-001",
                "question": "人間とは何か。",
                "hypothesis_count": len(hypotheses),
                "active_count": len(hypotheses),
                "entropy_bits": 1.0,
                "max_entropy_bits": 2.0,
                "kl_from_uniform_bits": 0.1,
                "gen0_mass": 0.5,
                "gen1_plus_mass": 0.5,
                "mean_active_uncertainty": 0.4,
                "total_evaluations": 4,
                "priority_score": 2.0,
                "top_competing_pair": None,
                "families": families if families is not None else [
                    {
                        "root_hypothesis_id": "HYP-ROOT",
                        "member_count": len(hypotheses),
                        "mass": total,
                        "mass_share": 1.0,
                        "top_hypothesis_id": hypotheses[0]["hypothesis_id"],
                        "top_hypothesis_mass": hypotheses[0]["posterior"],
                        "top_share_within_family": (
                            hypotheses[0]["posterior"] / total if total else 0.0
                        ),
                        "generations": [0, 1],
                    }
                ],
                "family_count": 1,
                "unexamined_active_hypothesis_ids": [],
                "awaiting_external_audit_ids": [],
                "orphan_over_narrowed_ids": [],
                "gated_top_pair": None,
                "hypotheses": hypotheses,
            }
        },
    }


class DetailCompressionTests(unittest.TestCase):
    """Proposal 2: one line per hypothesis outside the top N, and `--full`."""

    def setUp(self) -> None:
        # 15 hypotheses, strictly decreasing mass, so "top 12" is well defined
        # by rank rather than by float coincidence.
        self.hyps = [
            hyp(f"HYP-{i:02d}", posterior=round(0.15 - i * 0.005, 6))
            for i in range(15)
        ]
        self.state = state_with(self.hyps)

    def test_the_default_render_compresses_past_the_top_n(self) -> None:
        text = belief_state.render_belief_map_markdown(self.state)
        self.assertIn("圧縮表示", text)
        for h in self.hyps[belief_state.DETAIL_TOP_N:]:
            self.assertIn(f"`{h['hypothesis_id']}`", text)

    def test_a_compressed_hypothesis_loses_its_proposition_but_not_its_identity(self) -> None:
        text = belief_state.render_belief_map_markdown(self.state)
        buried = self.hyps[-1]
        self.assertNotIn(f"命題{buried['hypothesis_id']}の本文", text)
        # identity, claim title and backing counts survive
        self.assertIn(f"`{buried['hypothesis_id']}`", text)
        self.assertIn(buried["title"], text)

    def test_full_render_keeps_every_proposition(self) -> None:
        text = belief_state.render_belief_map_markdown(self.state, full=True)
        self.assertNotIn("圧縮表示", text)
        for h in self.hyps:
            self.assertIn(h["proposition"], text)

    def test_a_warned_hypothesis_is_never_compressed_away(self) -> None:
        """The audit information must survive the budget: a buried hypothesis
        that carries a live erratum keeps its full block."""
        hyps = list(self.hyps)
        hyps[-1] = dict(hyps[-1], errata_flags=["ERR-20261123-abcdef"])
        state = state_with(hyps)
        text = belief_state.render_belief_map_markdown(state)
        self.assertIn(hyps[-1]["proposition"], text)

    def test_selection_is_a_pure_function_of_the_state(self) -> None:
        first = belief_state.detail_selection(self.hyps)
        second = belief_state.detail_selection(list(reversed(self.hyps)))
        self.assertEqual(first, second)

    def test_selection_never_exceeds_the_state(self) -> None:
        self.assertLessEqual(
            belief_state.detail_selection(self.hyps), {h["hypothesis_id"] for h in self.hyps}
        )


class PairRecommendationFloorTests(unittest.TestCase):
    """Proposal 5: a pair holding no mass is reported, not recommended."""

    def _pair(self, mass_a: float, mass_b: float) -> dict:
        return {
            "left_hypothesis_id": "HYP-A",
            "right_hypothesis_id": "HYP-B",
            "left_posterior": mass_a,
            "right_posterior": mass_b,
            "left_uncertainty": 0.4,
            "right_uncertainty": 0.4,
            "expected_info_gain": 0.0,
            "pair_mass_sum": round(mass_a + mass_b, 4),
        }

    def test_the_floor_sits_below_the_unsaturated_threshold(self) -> None:
        self.assertLess(
            belief_state.PAIR_RECOMMENDATION_MASS_FLOOR,
            belief_state.UNSATURATED_PAIR_MASS_THRESHOLD,
        )

    def test_a_zero_mass_pair_is_not_recommended(self) -> None:
        pair = self._pair(0.0, 0.0)
        self.assertFalse(belief_state.pair_is_recommendable(pair))

    def test_a_pair_above_the_floor_is_recommended(self) -> None:
        pair = self._pair(0.3, 0.2)
        self.assertTrue(belief_state.pair_is_recommendable(pair))

    def test_a_legacy_pair_without_the_field_still_renders_as_before(self) -> None:
        """Stored pair records predate the field; `None` means 'no opinion', and
        the render must fall back to the old path rather than crash."""
        pair = self._pair(0.0, 0.0)
        pair.pop("pair_mass_sum")
        self.assertIsNone(belief_state.pair_is_recommendable(pair))

    def test_the_ratchet_warning_is_withheld_at_zero_mass(self) -> None:
        """The defect: `unsaturated_supports_ratchet` fired on a 0.0000 pair.
        The arithmetic predicate is unchanged; the *warning* is withheld."""
        a, b = {"posterior": 0.0}, {"posterior": 0.0}
        self.assertTrue(belief_state.pair_has_unsaturated_supports_ratchet(a, b))
        self.assertFalse(
            belief_state.pair_shows_ratchet_warning(
                {"pair_mass_sum": 0.0, "ratchet_warning": False,
                 "unsaturated_supports_ratchet": True}
            )
        )

    def test_a_legacy_pair_keeps_its_warning(self) -> None:
        """Records without `ratchet_warning` must not lose a warning they had."""
        self.assertTrue(
            belief_state.pair_shows_ratchet_warning(
                {"pair_mass_sum": 0.2, "unsaturated_supports_ratchet": True}
            )
        )

    def test_the_rendered_map_says_no_recommendation_and_names_the_holder(self) -> None:
        leader = hyp("HYP-LEAD", posterior=0.99)
        tail_a = hyp("HYP-TAIL-A", posterior=0.0)
        tail_b = hyp("HYP-TAIL-B", posterior=0.0)
        state = state_with([leader, tail_a, tail_b])
        state["questions"]["Q-001"]["top_competing_pair"] = {
            **self._pair(0.0, 0.0),
            "recommended": False,
            "recommendation_floor": belief_state.PAIR_RECOMMENDATION_MASS_FLOOR,
            "ratchet_warning": False,
            "unsaturated_supports_ratchet": True,
        }
        text = belief_state.render_belief_map_markdown(state)
        self.assertIn("推薦なし（質量0の対）", text)
        self.assertIn("`HYP-LEAD`", text)
        self.assertNotIn("未飽和上位対ラチェット注意", text)


class FamilyConcentrationTests(unittest.TestCase):
    """Proposal 3: family mass is never rendered without its concentration."""

    def test_family_mass_and_concentration_are_computed_together(self) -> None:
        hyps = [
            hyp("HYP-ROOT", posterior=0.01, family_root_hypothesis_id="HYP-ROOT"),
            hyp("HYP-C1", posterior=0.80, parents=("HYP-ROOT",),
                family_root_hypothesis_id="HYP-ROOT"),
            hyp("HYP-C2", posterior=0.19, parents=("HYP-ROOT",),
                family_root_hypothesis_id="HYP-ROOT"),
        ]
        roots = {h["hypothesis_id"]: h["family_root_hypothesis_id"] for h in hyps}
        fams = belief_state.question_families(hyps, roots)
        self.assertEqual(len(fams), 1)
        fam = fams[0]
        self.assertAlmostEqual(fam["mass_share"], 1.0, places=4)
        self.assertEqual(fam["top_hypothesis_id"], "HYP-C1")
        self.assertAlmostEqual(fam["top_share_within_family"], 0.80, places=4)
        self.assertIn("top_share_within_family", fam)

    def test_two_families_are_ordered_by_mass(self) -> None:
        hyps = [
            hyp("HYP-R1", posterior=0.1, family_root_hypothesis_id="HYP-R1"),
            hyp("HYP-R2", posterior=0.9, family_root_hypothesis_id="HYP-R2"),
        ]
        fams = belief_state.question_families(
            hyps, {h["hypothesis_id"]: h["family_root_hypothesis_id"] for h in hyps}
        )
        self.assertEqual([f["root_hypothesis_id"] for f in fams], ["HYP-R2", "HYP-R1"])

    def test_root_ancestor_ids_walks_the_first_parent(self) -> None:
        hyps = {
            "HYP-A": {"parent_hypothesis_ids": []},
            "HYP-B": {"parent_hypothesis_ids": ["HYP-A"]},
            "HYP-C": {"parent_hypothesis_ids": ["HYP-B", "HYP-Z"]},
        }
        roots = belief_state.root_ancestor_ids(hyps)
        self.assertEqual(roots["HYP-C"], "HYP-A")

    def test_root_ancestor_ids_survives_a_cycle(self) -> None:
        hyps = {
            "HYP-A": {"parent_hypothesis_ids": ["HYP-B"]},
            "HYP-B": {"parent_hypothesis_ids": ["HYP-A"]},
        }
        roots = belief_state.root_ancestor_ids(hyps)
        self.assertIn(roots["HYP-A"], {"HYP-A", "HYP-B"})

    def test_the_rendered_map_carries_the_concentration_column(self) -> None:
        hyps = [hyp("HYP-ROOT", posterior=1.0, family_root_hypothesis_id="HYP-ROOT")]
        text = belief_state.render_belief_map_markdown(state_with(hyps))
        self.assertIn("家系内集中度", text)
        self.assertIn("家系の質量と集中度は必ず並べて読むこと", text)


class PrimaryQuestionTests(unittest.TestCase):
    """Proposal 4: a declared primary question is shown as declared; an absent
    one is shown as undecided, never silently invented."""

    def test_an_undeclared_row_says_undecided_and_shows_the_derived_candidate(self) -> None:
        h = hyp("HYP-M", posterior=1.0, question_ids=("Q-002", "Q-003"))
        text = belief_state.render_belief_map_markdown(state_with([h]))
        self.assertIn("未決→`Q-002`", text)

    def test_a_declared_row_is_marked_as_declared(self) -> None:
        h = hyp("HYP-M", posterior=1.0, question_ids=("Q-002", "Q-003"))
        h["primary_question_id"] = "Q-003"
        text = belief_state.render_belief_map_markdown(state_with([h]))
        self.assertIn("`Q-003` (宣言)", text)

    def test_the_header_reports_the_attribution_rate(self) -> None:
        hyps = [hyp("HYP-A", posterior=0.5), hyp("HYP-B", posterior=0.5)]
        text = belief_state.render_belief_map_markdown(
            state_with(hyps, multi={"multi_question": 0, "with_primary": 0, "without_primary": 2})
        )
        self.assertIn("一次所属問い (`primary_question_id`)", text)
        self.assertIn("**未決 2 件**", text)

    def test_a_hypothesis_dict_without_the_new_keys_still_renders(self) -> None:
        """The columns added here must not turn a hand-built fixture (or any
        older caller) into a KeyError: five tests in test_pair_honesty.py
        failed exactly this way before the render learned the fallback."""
        bare = {
            "hypothesis_id": "HYP-BARE",
            "title": "素の辞書",
            "proposition": "素の辞書で渡された命題の本文",
            "scope_conditions": ["条件A"],
            "exclusion_clause": "この条件が観測されれば棄却される。",
            "lineage_op": "root",
            "generation": 0,
            "effective_status": "active",
            "uncertainty": 0.4,
            "posterior": 1.0,
            "parent_hypothesis_ids": [],
            "children_hypothesis_ids": [],
            "direct_eval_count": 0,
            "adversarial_eval_count": 0,
            "supporting_material_ids": [],
            "counter_material_ids": [],
            "source_note_ids": [],
            "errata_flags": [],
        }
        text = belief_state.render_belief_map_markdown(
            state_with([bare], multi={"multi_question": 0, "with_primary": 0, "without_primary": 1})
        )
        self.assertIn("`HYP-BARE`", text)
        self.assertIn("未決→`Q-001`", text)

    def test_the_schema_accepts_the_field_and_does_not_require_it(self) -> None:
        schema = json.loads((ROOT / "schema" / "hypothesis.schema.json").read_text(encoding="utf-8"))
        self.assertIn("primary_question_id", schema["properties"])
        self.assertNotIn("primary_question_id", schema["required"])


class BeliefBasisTests(unittest.TestCase):
    """Proposal 1: a posterior is quoted with the basis that produced it."""

    def test_default_basis_is_named(self) -> None:
        self.assertEqual(belief_state.belief_basis_label(), "default")

    def test_knobs_are_named_in_the_label(self) -> None:
        self.assertEqual(
            belief_state.belief_basis_label(temporal_heir_guard=True, pair_level_repeat=True),
            "temporal_heir_guard+pair_level_repeat",
        )
        self.assertEqual(
            belief_state.belief_basis_label(receiver_gated=True), "receiver_gated"
        )

    def test_the_render_prints_the_basis(self) -> None:
        state = state_with([hyp("HYP-A", posterior=1.0)])
        state["belief_basis"] = "temporal_heir_guard"
        text = belief_state.render_belief_map_markdown(state)
        self.assertIn("使用基底 (`belief_basis`)", text)
        self.assertIn("`temporal_heir_guard`", text)

    def test_the_session_schema_carries_the_same_field_name(self) -> None:
        schema = json.loads((ROOT / "schema" / "session.schema.json").read_text(encoding="utf-8"))
        self.assertIn("belief_basis", schema["properties"])
        self.assertNotIn("belief_basis", schema["required"])


class NewbornMassTests(unittest.TestCase):
    """Proposal 6: measure the dilution one registration causes."""

    def _data(self) -> dict:
        def row(hid, qids, parents=(), created="2026-11-01"):
            return {
                "hypothesis_id": hid,
                "session_id": "S-1",
                "created_at": created,
                "question_ids": list(qids),
                "title": f"仮説{hid}",
                "proposition": f"命題{hid}の本文",
                "scope_conditions": ["条件A"],
                "exclusion_clause": "この条件が観測されれば棄却される。",
                "lineage_op": "root" if not parents else "refines",
                "parent_hypothesis_ids": list(parents),
                "status": "active",
            }

        return {
            "hypotheses": {
                "HYP-A": row("HYP-A", ["Q-001"]),
                "HYP-B": row("HYP-B", ["Q-001"]),
                "HYP-NEW": row("HYP-NEW", ["Q-001"], created="2026-11-23"),
            },
            "evaluations": {},
            "materials": {},
            "sessions": {},
            "read_log": {},
            "errata": {},
            "editorial_decisions": {},
            "questions": {"Q-001": {"question": "人間とは何か。"}},
        }

    def test_it_reports_the_softmax_denominator_before_and_after(self) -> None:
        report = belief_state.newborn_mass(self._data())
        self.assertEqual(report["hypothesis_id"], "HYP-NEW")
        q = report["questions"][0]
        self.assertEqual((q["hypotheses_before"], q["hypotheses_after"]), (2, 3))
        self.assertFalse(report["writes"])

    def test_the_surviving_leader_never_gains_mass_from_a_registration(self) -> None:
        """A row with no evaluations enters at the same log-odds as its peers,
        so the leader's share can only fall or stay. This is the dilution the
        instrument exists to report."""
        report = belief_state.newborn_mass(self._data())
        self.assertLessEqual(report["questions"][0]["surviving_leader_delta_pp"], 0.0)

    def test_it_measures_a_named_hypothesis_without_writing(self) -> None:
        """The counterfactual removes the *named* row, so measuring HYP-A asks
        "what if HYP-A had never been registered?" -- three rows collapse to
        two, not two to one."""
        report = belief_state.newborn_mass(self._data(), hypothesis_id="HYP-A")
        self.assertEqual(report["hypothesis_id"], "HYP-A")
        self.assertEqual(report["questions"][0]["hypotheses_before"], 2)
        self.assertEqual(report["questions"][0]["hypotheses_after"], 3)


if __name__ == "__main__":
    unittest.main()
