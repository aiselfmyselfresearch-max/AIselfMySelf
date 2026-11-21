# -*- coding: utf-8 -*-
"""Tests for tools/curiosity_axes_probe.py.

The probe is the recomputer behind the two evaluation rows of
``readings/2026-11-21-ten-cognitive-science-sources-on-curiosity-and-self-updating.md``,
so its own numbers have to be trustworthy before anyone quotes them.
"""
import math
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

import curiosity_axes_probe as probe  # noqa: E402


class LogisticFitTest(unittest.TestCase):
    def test_finite_sample_recovers_the_log_odds_ratio(self):
        # x=1 rows: 4 positives / 2 negatives; x=0 rows: 2 positives / 4 negatives.
        X = [[1.0, 1.0], [1.0, 0.0], [1.0, 1.0], [1.0, 0.0],
             [1.0, 1.0], [1.0, 0.0], [1.0, 1.0], [1.0, 0.0],
             [1.0, 1.0], [1.0, 0.0], [1.0, 1.0], [1.0, 0.0]]
        y = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0]
        beta, _ll, converged = probe.logistic_fit(X, y)
        self.assertTrue(converged)
        self.assertAlmostEqual(beta[1], math.log(4.0), places=6)

    def test_separated_sample_is_not_reported_as_converged(self):
        # A completely separated sample has no finite maximum likelihood, so the
        # fitted coefficient is not an effect size and must not be quoted.
        X = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0],
             [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]]
        y = [1, 1, 1, 0, 0, 0]
        _beta, _ll, converged = probe.logistic_fit(X, y)
        self.assertFalse(converged)


class StatsTest(unittest.TestCase):
    def test_fisher_matches_a_hand_computed_table(self):
        # 2x2: [[1, 9], [11, 3]]; the two-sided Fisher p is a small fixed value.
        p = probe.fisher_two_sided(1, 9, 11, 3)
        self.assertTrue(0.0 < p < 0.05)

    def test_fisher_is_symmetric_under_row_swap(self):
        a = probe.fisher_two_sided(5, 10, 20, 40)
        b = probe.fisher_two_sided(20, 40, 5, 10)
        self.assertAlmostEqual(a, b, places=12)

    def test_sign_test_on_a_unanimous_stratum_set(self):
        self.assertAlmostEqual(probe.sign_test(12, 0), 2 * (0.5 ** 12), places=12)

    def test_mh_chi2_matches_uncorrected_pearson_for_one_stratum(self):
        a, b, c, d = 7, 11, 27, 12
        odds, chi2, p = probe.mh_test([(a, b, c, d)])
        # With one stratum the MH odds ratio is the crude odds ratio.
        self.assertAlmostEqual(odds, (a * d) / (b * c), places=9)
        # The MH chi-square is the hypergeometric-variance form, which for a
        # single stratum is the uncorrected Pearson chi-square times
        # (n-1)/n -- not the Pearson value itself.
        n = a + b + c + d
        row1, row2, col1, col2 = a + b, c + d, a + c, b + d
        pearson = n * (a * d - b * c) ** 2 / (row1 * row2 * col1 * col2)
        self.assertAlmostEqual(chi2, pearson * (n - 1) / n, places=9)
        self.assertAlmostEqual(p, math.erfc(math.sqrt(chi2 / 2)), places=12)

    def test_mh_matches_its_documented_formula_over_two_strata(self):
        # A direct check of the formula the docstring states:
        #   num = sum(a - (a+b)(a+c)/n)
        #   den = sum(r1*r2*c1*c2 / (n^2 * (n-1)))
        #   chi2 = num^2 / den
        strata = [(7, 11, 27, 12), (14, 22, 54, 24)]
        odds, chi2, p = probe.mh_test(strata)
        num = den = 0.0
        for a, b, c, d in strata:
            n = a + b + c + d
            num += a - (a + b) * (a + c) / n
            den += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
        self.assertAlmostEqual(chi2, num ** 2 / den, places=9)
        self.assertAlmostEqual(p, math.erfc(math.sqrt(chi2 / 2)), places=12)
        # Both strata carry the same odds ratio, so the pooled MH odds ratio
        # must reproduce it exactly -- that is the point of the MH estimator.
        common = (7 * 12) / (11 * 27)
        self.assertAlmostEqual(odds, common, places=9)

    def test_mh_chi2_grows_with_the_number_of_agreeing_strata(self):
        # Two strata with the same odds ratio must give a larger chi-square
        # than one of them alone (the MH statistic pools evidence).
        s1 = (7, 11, 27, 12)
        s2 = (14, 22, 54, 24)  # exactly double s1
        _, chi2_one, _ = probe.mh_test([s1])
        _, chi2_both, _ = probe.mh_test([s1, s2])
        self.assertGreater(chi2_both, chi2_one)


class ProbeResultTest(unittest.TestCase):
    """The probe must run over the real ledger and stay self-consistent."""

    @classmethod
    def setUpClass(cls):
        cls.result = probe.compute()

    def test_population_is_consistent(self):
        p = self.result['population']
        self.assertEqual(p['evaluations_total'],
                         p['evaluations_void'] + p['evaluations_live'])
        self.assertGreater(p['evaluations_live'], 0)
        self.assertGreater(p['materials_total'], 0)

    def test_status_counts_sum_to_the_material_total(self):
        v = self.result['verification_depth']
        self.assertEqual(sum(v['status_counts'].values()), v['materials'])
        # The bug this guards: ``status_counts`` used to be built straight from
        # the (status, depth) cells, so the last depth of a status overwrote the
        # earlier ones and the table under-counted.
        self.assertEqual(v['status_counts']['verified'], v['verified'])

    def test_depth_counts_sum_to_the_material_total(self):
        v = self.result['verification_depth']
        self.assertEqual(sum(v['depth_counts'].values()), v['materials'])

    def test_verified_deep_is_a_subset_of_verified(self):
        v = self.result['verification_depth']
        self.assertLessEqual(v['verified_deep'], v['verified'])
        self.assertEqual(v['verified_deep'] + v['verified_without_depth'],
                         v['verified'] - v['depth_counts'].get('verified|results', 0)
                         - v['depth_counts'].get('verified|unspecified', 0))

    def test_axis_iii_cells_sum_to_the_live_population(self):
        a = self.result['axis_iii']
        self.assertEqual(a['as_written_all']['has_total'] + a['as_written_all']['none_total'],
                         self.result['population']['evaluations_live'])
        self.assertEqual(a['strict_all']['has_total'] + a['strict_all']['none_total'],
                         self.result['population']['evaluations_live'])
        # strict is a subset of as-written: a deep material is also verified.
        self.assertLessEqual(a['strict_all']['has_total'], a['as_written_all']['has_total'])

    def test_lrt_fits_converged(self):
        for key in ('all', 'psc_only'):
            flags = self.result['reading_volume_lrt'][key]['converged']
            for name, ok in flags.items():
                self.assertTrue(ok, f'{key}/{name} did not converge')

    def test_lrt_deviance_reduction_is_positive(self):
        r = self.result['reading_volume_lrt']['all']
        self.assertGreater(r['LR_axes_added_to_volume'], 0)
        self.assertGreater(r['deviance_reduction_pct'], 0)

    def test_within_hypothesis_arms_are_consistent(self):
        w = self.result['within_hypothesis']
        for key in ('depth0', 'depth_ge_1'):
            b = w[key]
            self.assertEqual(b['sign_lower'] + b['sign_higher'] + b['sign_tie'], b['strata'])
            self.assertLessEqual(b['same_critical'], b['same_total'])
            self.assertLessEqual(b['other_critical'], b['other_total'])

    def test_excluding_a_session_removes_exactly_its_rows(self):
        full = probe.compute()
        excluded = probe.compute(exclude_sessions=frozenset({'SESSION-20261121-e7565a'}))
        drop = full['population']['evaluations_live'] - excluded['population']['evaluations_live']
        self.assertEqual(drop, 2)
        self.assertEqual(excluded['population']['evaluations_live'], 776)


if __name__ == '__main__':
    unittest.main()
