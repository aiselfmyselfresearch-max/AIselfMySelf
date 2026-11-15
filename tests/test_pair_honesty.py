"""Tests for the honesty of the pair the engine hands a session (2026-11-15).

Why this file exists
--------------------
`belief_state.compute_belief_state` ranks candidate pairs by
``posterior_a * posterior_b * (uncertainty_a + uncertainty_b)``.  That product
never asks whether the two propositions contradict each other, and the renderer
called the winner 「最優先対立対」.  A session was handed two *orthogonal*
hypotheses under that label, scored them, and its own score rose
(EIG 0.2259 -> 0.2951) because `supports` has no downward term, while the
genuinely competing parent/child pairs fell 73%
(readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md §4).

These tests pin the software behaviour of the correction, never a live number:

* a pair carries the lineage relation the ledger records, and the formula;
* nothing in the rendered output still calls the winner 対立;
* a pair both of whose sides have only ever been `supports`-ed is labelled as the
  ratchet it is;
* the selector's sentence names both formulas, because its two numbers move in
  opposite directions;
* a question with no hypotheses is advertised at the same priority the selector
  actually scores it at (they disagreed: 2.0 against 2.50).
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402


def hyp(hid: str, *, parents: list[str] | None = None, posterior: float = 0.5,
        uncertainty: float = 0.5, adv: int = 0, verdicts: dict | None = None,
        title: str = "題") -> dict:
    return {
        "hypothesis_id": hid,
        "title": title,
        "proposition": "命題。",
        "scope_conditions": ["条件"],
        "exclusion_clause": "反証条件。",
        "generation": 1 if parents else 0,
        "lineage_op": "refines" if parents else "root",
        "parent_hypothesis_ids": parents or [],
        "effective_status": "active",
        "posterior": posterior,
        "uncertainty": uncertainty,
        "direct_eval_count": sum((verdicts or {}).values()),
        "adversarial_eval_count": adv,
        "compared_touch_count": 0,
        "verdict_counts": verdicts or {},
        "supporting_material_ids": [],
        "counter_material_ids": [],
        "source_note_ids": [],
        "errata_flags": [],
    }


class LineageRelationTests(unittest.TestCase):
    def test_each_recorded_shape_gets_its_own_label(self) -> None:
        a = hyp("HYP-A")
        child = hyp("HYP-B", parents=["HYP-A"])
        sibling = hyp("HYP-C", parents=["HYP-A"])
        stranger = hyp("HYP-D")
        self.assertEqual(belief_state.pair_lineage_relation(child, a), "parent_child_right_is_parent")
        self.assertEqual(belief_state.pair_lineage_relation(a, child), "parent_child_left_is_parent")
        self.assertEqual(belief_state.pair_lineage_relation(child, sibling), "sibling")
        self.assertEqual(belief_state.pair_lineage_relation(a, stranger), "unrelated")

    def test_every_label_the_function_can_return_is_renderable(self) -> None:
        """A label with no Japanese rendering would print as an empty cell."""
        for key in ("parent_child_left_is_parent", "parent_child_right_is_parent",
                    "sibling", "unrelated"):
            self.assertIn(key, belief_state.PAIR_RELATION_LABELS, key)
            self.assertTrue(belief_state.PAIR_RELATION_LABELS[key])

    def test_the_relation_is_read_from_the_ledger_not_inferred(self) -> None:
        """Two propositions that plainly contradict each other are still 系譜関係なし."""
        left = hyp("HYP-L", title="A である")
        right = hyp("HYP-R", title="A ではない")
        self.assertEqual(belief_state.pair_lineage_relation(left, right), "unrelated")


class RatchetTests(unittest.TestCase):
    def test_both_sides_supports_only_is_the_ratchet(self) -> None:
        a = hyp("HYP-A", verdicts={"supports": 2}, posterior=0.6)
        b = hyp("HYP-B", verdicts={"supports": 1}, posterior=0.4)
        self.assertTrue(belief_state.pair_examined_only_by_supports(a, b))

    def test_an_adversarial_touch_on_either_side_ends_it(self) -> None:
        a = hyp("HYP-A", verdicts={"supports": 2}, adv=1)
        b = hyp("HYP-B", verdicts={"supports": 1})
        self.assertFalse(belief_state.pair_examined_only_by_supports(a, b))
        self.assertFalse(belief_state.pair_examined_only_by_supports(b, a))

    def test_a_non_supports_verdict_ends_it(self) -> None:
        a = hyp("HYP-A", verdicts={"narrows_scope": 1})
        b = hyp("HYP-B", verdicts={"supports": 1})
        self.assertFalse(belief_state.pair_examined_only_by_supports(a, b))

    def test_never_examined_at_all_counts_as_supports_only(self) -> None:
        """An unevaluated pair has no downward term either, so the warning applies."""
        self.assertTrue(belief_state.pair_examined_only_by_supports(hyp("HYP-A"), hyp("HYP-B")))


def state_with(pair: dict | None, entries: list[dict]) -> dict:
    return {
        "total_hypotheses": len(entries),
        "total_evaluations": sum(e["direct_eval_count"] for e in entries),
        "core_priority_ranking": ["Q-001"],
        "questions": {
            "Q-001": {
                "question_id": "Q-001",
                "question": "問い。",
                "hypothesis_count": len(entries),
                "active_count": len(entries),
                "entropy_bits": 1.0,
                "active_entropy_bits": 1.0,
                "max_entropy_bits": 1.0,
                "kl_from_uniform_bits": 0.1,
                "gen0_mass": 0.0,
                "gen1_plus_mass": 1.0,
                "mean_active_uncertainty": 0.5,
                "total_evaluations": sum(e["direct_eval_count"] for e in entries),
                "priority_score": 1.5,
                "top_competing_pair": pair,
                "hypotheses": entries,
            }
        },
    }


def pair_of(a: dict, b: dict, eig: float = 0.5, **extra) -> dict:
    pair = {
        "left_hypothesis_id": a["hypothesis_id"],
        "left_title": a["title"],
        "right_hypothesis_id": b["hypothesis_id"],
        "right_title": b["title"],
        "expected_info_gain": eig,
        "formula": belief_state.PAIR_EIG_FORMULA,
        "left_posterior": a["posterior"],
        "right_posterior": b["posterior"],
        "left_uncertainty": a["uncertainty"],
        "right_uncertainty": b["uncertainty"],
        "lineage_relation": belief_state.pair_lineage_relation(a, b),
        "examined_only_by_supports": belief_state.pair_examined_only_by_supports(a, b),
    }
    pair.update(extra)
    return pair


class RenderedMapTests(unittest.TestCase):
    def test_the_winner_is_no_longer_called_a_disagreement(self) -> None:
        a, b = hyp("HYP-A"), hyp("HYP-B")
        text = belief_state.render_belief_map_markdown(state_with(pair_of(a, b), [a, b]))
        self.assertNotIn("最優先対立ペア", text)
        self.assertNotIn("最優先対立対", text)
        self.assertIn("最優先検証ペア", text)
        self.assertIn("EIG=p_a×p_b×(u_a+u_b)", text)

    def test_the_formula_and_the_recorded_relation_are_printed(self) -> None:
        a, b = hyp("HYP-A", posterior=0.25, uncertainty=0.5), hyp("HYP-B", posterior=0.5, uncertainty=0.25)
        text = belief_state.render_belief_map_markdown(state_with(pair_of(a, b, eig=0.0938), [a, b]))
        self.assertIn(belief_state.PAIR_EIG_FORMULA, text)
        self.assertIn("0.2500 × 0.5000 × (0.5000 + 0.2500)", text)
        self.assertIn("系譜関係なし", text)
        self.assertIn("両立性を検査しない", text)

    def test_a_parent_child_pair_says_which_side_is_the_parent(self) -> None:
        parent = hyp("HYP-P", posterior=0.6)
        child = hyp("HYP-C", parents=["HYP-P"], posterior=0.3)
        text = belief_state.render_belief_map_markdown(state_with(pair_of(parent, child), [parent, child]))
        self.assertIn("親子（左が親）", text)
        # the same pair written the other way round must not read the same
        text2 = belief_state.render_belief_map_markdown(state_with(pair_of(child, parent), [child, parent]))
        self.assertIn("親子（右が親）", text2)
        self.assertNotIn("親子（左が親）", text2)

    def test_the_ratchet_warning_appears_only_for_a_supports_only_pair(self) -> None:
        warned_a = hyp("HYP-A", verdicts={"supports": 1})
        warned_b = hyp("HYP-B", verdicts={"supports": 1})
        text = belief_state.render_belief_map_markdown(
            state_with(pair_of(warned_a, warned_b), [warned_a, warned_b])
        )
        self.assertIn("supports` 以外の判定を受けたことがない", text)
        self.assertIn("+30.6%", text)

        examined_a = hyp("HYP-A", verdicts={"supports": 1})
        examined_b = hyp("HYP-B", verdicts={"narrows_scope": 1})
        text2 = belief_state.render_belief_map_markdown(
            state_with(pair_of(examined_a, examined_b), [examined_a, examined_b])
        )
        self.assertNotIn("supports` 以外の判定を受けたことがない", text2)

    def test_a_pair_record_without_the_new_keys_still_renders(self) -> None:
        """Older callers and test fixtures pass a bare pair; nothing may KeyError."""
        a, b = hyp("HYP-A"), hyp("HYP-B")
        bare = {
            "left_hypothesis_id": "HYP-A", "left_title": a["title"],
            "right_hypothesis_id": "HYP-B", "right_title": b["title"],
            "expected_info_gain": 0.5,
        }
        text = belief_state.render_belief_map_markdown(state_with(bare, [a, b]))
        self.assertIn("不明", text)
        self.assertIn(belief_state.PAIR_EIG_FORMULA, text)


class SelectorReasonTests(unittest.TestCase):
    def test_the_reason_names_both_formulas_and_the_relation(self) -> None:
        a, b = hyp("HYP-A"), hyp("HYP-B")
        state = state_with(pair_of(a, b), [a, b])
        _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
        self.assertIn("score=", reason)
        self.assertIn("active_H+0.8·mean_u+1/√(1+評価数)", reason)
        self.assertIn("EIG=p_a×p_b×(u_a+u_b)", reason)
        self.assertIn("両立性は検査しない", reason)
        self.assertIn("最優先検証対", reason)
        self.assertIn("系譜=系譜関係なし", reason)
        self.assertNotIn("最優先対立対", reason)

    def test_a_supports_only_pair_is_flagged_inside_the_receipt(self) -> None:
        a = hyp("HYP-A", verdicts={"supports": 1})
        b = hyp("HYP-B", verdicts={"supports": 1})
        _qid, reason = belief_state.select_auto_question_id(
            state_with(pair_of(a, b), [a, b]), ["Q-001"]
        )
        self.assertIn("両側 supports のみ", reason)

    def test_a_single_hypothesis_still_reads_as_single_hypothesis_testing(self) -> None:
        a = hyp("HYP-A")
        _qid, reason = belief_state.select_auto_question_id(state_with(None, [a]), ["Q-001"])
        self.assertIn("単一仮説検証", reason)


class HypothesisLessPriorityTests(unittest.TestCase):
    """The advertised default and the score the selector uses must be one number."""

    def _repo(self, tmp: str) -> Path:
        root = Path(tmp) / "repo"
        (root / "state").mkdir(parents=True)
        for name in ("questions", "materials", "fragments", "sessions", "notes"):
            (root / "state" / f"{name}.jsonl").write_text("", encoding="utf-8")
        (root / "state" / "questions.jsonl").write_text(
            json.dumps({
                "question_id": "Q-001",
                "question": "人間とは何か。",
                "status": "open",
                "created_at": "2026-10-24",
                "origin": {"kind": "human_seed", "detail": "d"},
                "motif_ids": [], "material_ids": [], "previous_question_ids": [],
            }, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return root

    def test_advertised_priority_equals_the_score_the_selector_uses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            state = belief_state.compute_belief_state(root=root)
            advertised = state["questions"]["Q-001"]["priority_score"]
            self.assertEqual(advertised, belief_state.HYPOTHESIS_LESS_CORE_PRIORITY)
            # jitter is 0 without a seed, so the selector's own score is exact
            _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
            self.assertIn(f"score={advertised:.3f}", reason)
            self.assertIn("中核問い未定式化優先", reason)

    def test_the_two_call_sites_read_one_constant(self) -> None:
        source = (ROOT / "tools" / "belief_state.py").read_text(encoding="utf-8")
        self.assertIn('"priority_score": HYPOTHESIS_LESS_CORE_PRIORITY', source)
        self.assertIn("score = HYPOTHESIS_LESS_CORE_PRIORITY + jitter", source)
        self.assertNotIn('"priority_score": 2.0', source)


def _hyp_row(hid: str, *, parents=(), qid: str = "Q-QA", created: str = "2026-11-10T00:00:00Z"):
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


def _evl_row(eid: str, target: str, *, compared=(), created: str = "2026-11-10T01:00:00Z",
             verdict: str = "supports", evidence: str = "reproducible_script"):
    return {
        "evaluation_id": eid,
        "session_id": "SESSION-TEST",
        "created_at": created,
        "target_hypothesis_id": target,
        "verdict": verdict,
        "evidence_type": evidence,
        "summary": "synthetic evaluation for the compared-touch wiring test",
        "compared_against_hypothesis_ids": list(compared),
    }


def _cols(hyps, evls, qid: str = "Q-QA"):
    return {
        "questions": {qid: {"question_id": qid, "question": "問い。"}},
        "hypotheses": {h["hypothesis_id"]: h for h in hyps},
        "evaluations": {e["evaluation_id"]: e for e in evls},
        "errata": {},
    }


class ComparedTouchWiringTests(unittest.TestCase):
    """2026-11-15: compared_touch_count is wired into uncertainty, damped."""

    def test_compared_touches_lower_uncertainty_below_the_unevaluated_default(self):
        hyps = [_hyp_row("HYP-A"), _hyp_row("HYP-B"), _hyp_row("HYP-C")]
        evls = [
            _evl_row("EVL-1", "HYP-A", compared=["HYP-B"], created="2026-11-10T01:00:00Z"),
            _evl_row("EVL-2", "HYP-A", compared=["HYP-B"], created="2026-11-11T01:00:00Z"),
        ]
        state = belief_state.compute_belief_state(_cols(hyps, evls))
        entries = {h["hypothesis_id"]: h for h in state["questions"]["Q-QA"]["hypotheses"]}

        # HYP-C: never evaluated, never named. adv == 0, so the 1.25x cap applies.
        self.assertEqual(entries["HYP-C"]["uncertainty"], 1.0)
        self.assertEqual(entries["HYP-C"]["compared_touch_count"], 0)

        # HYP-B: named twice, never examined itself. A comparison during a
        # supports evaluation is also an adversarial touch on the rival
        # (-0.20*delta/n), so the 1.25x "never examined" multiplier does not
        # apply; the damped comparison term is what moves the value:
        # 1.0 / sqrt(1 + 0.5 * 2) = 0.7071.
        expected_b = round(1.0 / math.sqrt(1.0 + 0.5 * 2), 4)
        self.assertEqual(entries["HYP-B"]["compared_touch_count"], 2)
        self.assertEqual(entries["HYP-B"]["adversarial_eval_count"], 2)
        self.assertEqual(entries["HYP-B"]["uncertainty"], expected_b)
        self.assertLess(entries["HYP-B"]["uncertainty"], entries["HYP-C"]["uncertainty"])

        # HYP-A: examined twice from two sources, nobody's named rival.
        expected_a = round(1.25 / math.sqrt(1.0 + 2), 4)
        self.assertEqual(entries["HYP-A"]["uncertainty"], expected_a)

    def test_a_naming_is_weaker_than_an_examination(self):
        """A rival named in a supports evaluation (adv touch + one naming) keeps higher uncertainty than the same rival directly examined with one narrows_scope."""
        hyps = [_hyp_row("HYP-SRC"), _hyp_row("HYP-NAMED"), _hyp_row("HYP-EXAMINED")]
        evls = [
            _evl_row("EVL-1", "HYP-SRC", compared=["HYP-NAMED"]),
            _evl_row("EVL-2", "HYP-EXAMINED", verdict="narrows_scope"),
        ]
        state = belief_state.compute_belief_state(_cols(hyps, evls))
        entries = {h["hypothesis_id"]: h for h in state["questions"]["Q-QA"]["hypotheses"]}
        # NAMED: 1 comparison -> adv 1; 1.0 / sqrt(1 + 0.5 * 1) = 0.8165
        self.assertEqual(entries["HYP-NAMED"]["uncertainty"], round(1.0 / math.sqrt(1.5), 4))
        # EXAMINED: no comparison; adv 1 (narrows_scope); 1.0 / sqrt(1 + 1) = 0.7071
        self.assertEqual(entries["HYP-EXAMINED"]["uncertainty"], round(1.0 / math.sqrt(2.0), 4))
        self.assertGreater(entries["HYP-NAMED"]["uncertainty"], entries["HYP-EXAMINED"]["uncertainty"])
        self.assertEqual(belief_state.COMPARISON_TOUCH_WEIGHT, 0.5)


class EvaluatedPairPreferenceTests(unittest.TestCase):
    """2026-11-15: a pair with an unevaluated side is never preferred as the top pair."""

    def test_both_evaluated_pair_wins_over_higher_uncertainty_newborn_pair(self):
        hyps = [_hyp_row("HYP-A"), _hyp_row("HYP-B"), _hyp_row("HYP-C")]
        evls = [
            _evl_row("EVL-1", "HYP-A"),
            _evl_row("EVL-2", "HYP-C"),
        ]
        state = belief_state.compute_belief_state(_cols(hyps, evls))
        pair = state["questions"]["Q-QA"]["top_competing_pair"]
        ids = {pair["left_hypothesis_id"], pair["right_hypothesis_id"]}
        self.assertEqual(ids, {"HYP-A", "HYP-C"})
        self.assertFalse(pair["contains_unevaluated"])
        self.assertEqual(pair["left_direct_eval_count"] + pair["right_direct_eval_count"], 2)

    def test_all_unevaluated_pool_falls_back_and_says_so(self):
        hyps = [_hyp_row("HYP-A"), _hyp_row("HYP-B")]
        state = belief_state.compute_belief_state(_cols(hyps, []))
        pair = state["questions"]["Q-QA"]["top_competing_pair"]
        self.assertTrue(pair["contains_unevaluated"])
        self.assertIn("selection_note", pair)
        self.assertIn("直接評価0件", pair["selection_note"])

    def test_unevaluated_side_is_marked_in_the_rendered_map(self):
        hyps = [_hyp_row("HYP-A"), _hyp_row("HYP-B")]
        state = belief_state.compute_belief_state(_cols(hyps, []))
        pair = state["questions"]["Q-QA"]["top_competing_pair"]
        text = belief_state.render_belief_map_markdown(state)
        self.assertIn("少なくとも一方が直接評価0件", text)
        self.assertIn("直接評価0件の仮説を含む対しか候補に残らなかった", text)

    def test_the_receipt_marks_a_pair_with_an_unevaluated_side(self):
        a, b = hyp("HYP-A", verdicts={"supports": 1}), hyp("HYP-B")
        pair = pair_of(a, b, eig=0.5, left_direct_eval_count=0, right_direct_eval_count=0,
                       contains_unevaluated=True)
        state = state_with(pair, [a, b])
        _qid, reason = belief_state.select_auto_question_id(state, ["Q-001"])
        self.assertIn("直接評価0件を含む", reason)


if __name__ == "__main__":
    unittest.main()
