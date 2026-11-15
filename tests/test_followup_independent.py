"""Regression tests for comparison uncertainty and eligible-pair selection."""
import math
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import belief_state
import size_budget


def data():
    return {
        'questions': {'Q-001': {'question': '問い', 'status': 'open'}},
        'hypotheses': {h: {'hypothesis_id': h, 'question_ids': ['Q-001'], 'title': h, 'status': 'active'} for h in ('A', 'B', 'C')},
        'evaluations': {}, 'errata': {},
    }


def evaluation(target, compared=(), material='m'):
    return {'target_hypothesis_id': target, 'verdict': 'supports', 'evidence_type': 'cross_session_audit', 'material_ids': [material], 'compared_against_hypothesis_ids': list(compared)}


class IndependentFollowup(unittest.TestCase):
    def state(self, d):
        return belief_state.compute_belief_state({**d, 'evaluations': {k: {'evaluation_id': k, **v} for k, v in d['evaluations'].items()}})

    def test_unevaluated_pair_is_never_recommended(self):
        d = data()
        q = self.state(d)['questions']['Q-001']
        self.assertIsNone(q['top_competing_pair'])
        self.assertNotIn('Q-001', self.state(d)['saturation']['saturated_question_ids'])
        d['evaluations']['1'] = evaluation('A')
        self.assertIsNone(self.state(d)['questions']['Q-001']['top_competing_pair'])
        d['evaluations']['2'] = evaluation('B')
        q = self.state(d)['questions']['Q-001']
        pair = q['top_competing_pair']
        self.assertEqual({pair['left_hypothesis_id'], pair['right_hypothesis_id']}, {'A', 'B'})

    def test_touch_count_uses_diminishing_term_without_changing_posterior_formula(self):
        d = data()
        d['evaluations']['1'] = evaluation('A', ['B'])
        d['evaluations']['2'] = evaluation('A', ['B'])
        state = self.state(d)['questions']['Q-001']
        b = next(h for h in state['hypotheses'] if h['hypothesis_id'] == 'B')
        self.assertEqual(b['compared_touch_count'], 2)
        self.assertAlmostEqual(b['uncertainty'], round(1 / math.sqrt(1 + 0.5 * math.log2(3)), 4))
        original = belief_state.COMPARISON_TOUCH_WEIGHT
        try:
            belief_state.COMPARISON_TOUCH_WEIGHT = 0.0
            without = self.state(d)['questions']['Q-001']
        finally:
            belief_state.COMPARISON_TOUCH_WEIGHT = original
        self.assertEqual([h['posterior'] for h in state['hypotheses']],
                         [h['posterior'] for h in without['hypotheses']])
        self.assertNotEqual(b['uncertainty'], next(h for h in without['hypotheses'] if h['hypothesis_id'] == 'B')['uncertainty'])
        # Each mention has a smaller uncertainty effect at larger counts.
        self.assertLess(math.log2(3)-math.log2(2), math.log2(2))

    def test_cross_question_comparison_remains_allowed(self):
        d = data()
        d['questions']['Q-002'] = {'question': '別の問い', 'status': 'open'}
        d['hypotheses']['B']['question_ids'] = ['Q-002']
        d['evaluations']['1'] = evaluation('A', ['B'])
        b = self.state(d)['questions']['Q-002']['hypotheses'][0]
        self.assertEqual(b['compared_touch_count'], 1)

    def test_only_explicit_corpus_gate_exempted_from_theme_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); tools = root / 'tools'; tools.mkdir()
            for n in range(size_budget.AUDIT_SCRIPT_SOFT_COUNT):
                (tools / f'theme{n}_audit.py').write_text('')
            (tools / 'readings_integrity_audit.py').write_text('')
            result = next(r for r in size_budget.evaluate(root) if r.rel_path == 'tools/*_audit*.py (freeze)')
            self.assertEqual(result.file_count, size_budget.AUDIT_SCRIPT_SOFT_COUNT)
            self.assertEqual(result.status, 'ok')
            (tools / 'another_audit.py').write_text('')
            result = next(r for r in size_budget.evaluate(root) if r.rel_path == 'tools/*_audit*.py (freeze)')
            self.assertEqual(result.status, 'warn')

if __name__ == '__main__':
    unittest.main()
