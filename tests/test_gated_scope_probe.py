"""Regression tests for read-only scope measurements and tied-rank semantics."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gated_scope_probe as probe


class RankTests(unittest.TestCase):
    def test_average_ties(self):
        self.assertEqual(probe.average_ranks([3, 1, 1, 2]), [4, 1.5, 1.5, 3])

    def test_same_and_reverse(self):
        self.assertAlmostEqual(probe.spearman([1, 2, 3], [1, 2, 3]), 1)
        self.assertAlmostEqual(probe.spearman([1, 2, 3], [3, 2, 1]), -1)

    def test_tied_ranks_are_order_invariant(self):
        x, y = [1, 1, 2, 3], [1, 2, 2, 4]
        order = [2, 0, 3, 1]
        self.assertAlmostEqual(probe.spearman(x, y), probe.spearman(
            [x[i] for i in order], [y[i] for i in order]))

    def test_constant_and_empty_are_undefined(self):
        self.assertIsNone(probe.spearman([1, 1], [2, 3]))
        self.assertIsNone(probe.spearman([], []))
        self.assertIsNone(probe.spearman([1], [1]))

    def test_mismatched_lengths_rejected(self):
        with self.assertRaises(ValueError):
            probe.spearman([1], [1, 2])

    def test_l1_includes_missing_keys(self):
        self.assertAlmostEqual(probe.l1({'a': 1}, {'b': 1}), 2)
        self.assertEqual(probe.l1({'a': 1}, {'a': 1}), 0)


class ProbeIntegrationTests(unittest.TestCase):
    def test_snapshot_controls_and_orphan_provenance(self):
        def hashes():
            paths = list((probe.ROOT / 'state').rglob('*.jsonl'))
            paths += [probe.ROOT / n for n in
                      ('BELIEF_MAP.md', 'SELF_MODEL.md', 'READING_MAP.md')]
            return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        before = hashes()
        result = probe.run(excluded_sessions=('SESSION-20261125-7ad91d',))
        self.assertEqual(hashes(), before)
        self.assertFalse(result['writes'])
        self.assertEqual(len(result['effective_inputs_sha256']), 64)
        self.assertLessEqual(result['effective_status_changed_materials'],
                             result['all_materials'])
        for q in probe.CORE:
            row = result['questions'][q]
            self.assertEqual(row['historical_ablation_l1'], 0)
            self.assertAlmostEqual(row['ed_material_ablation_tvd'] * 2,
                                   row['ed_material_ablation_l1_rounded_posterior'])
            for key in ('rho_later_date_vs_eval_count',
                        'rho_later_date_vs_gated_posterior'):
                if row[key] is not None:
                    self.assertLessEqual(abs(row[key]), 1.000000001)
        for row in result['orphan']['evaluations']:
            # A missing heir is not evidence that a comparison ID inherited it.
            self.assertIn('scope_inherited_by_hypothesis_ids', row)


if __name__ == '__main__':
    unittest.main()
