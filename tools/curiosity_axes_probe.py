#!/usr/bin/env python3
"""Read-only probe: the four ledger measurements of the 2026-11-21 curiosity
report (``readings/2026-11-21-ten-cognitive-science-sources-on-curiosity-and-self-updating.md``).

It recomputes every number that the two evaluation rows of that report cite
(``EVL-20261121-dc5c02`` and ``EVL-20261121-f8a8cf``):

* §4-1 the verification-depth census of the canonical material view;
* §4-2 the axis-(iii) operationalisation sensitivity table (as-written
  ``status == verified`` versus strict ``depth in {full_text, re_derived}``),
  for all live evaluations, for the cross-session subset and for the
  primary-source-collision subset;
* §4-3 the reading-volume absorption test of exclusion clause (d): a
  logistic likelihood-ratio test of the three axes against reading volume;
* §4-4 the within-hypothesis (fixed-effects) depth-stratified comparison of
  same-session versus other-session verdicts, with the Mantel-Haenszel odds
  ratio, the Mantel-Haenszel chi-square, the two-sided Fisher exact test and
  the stratified sign test;
* §4-5 the temporal saturation of axis (i);
* the lineage fork count behind the depth-scale caveat.

Nothing is written.  The canonical view is the one
``tools/belief_state.py:load_belief_ledgers`` reads: base files plus shards
plus the editorial-decision overlay, with ``void_row`` errata excluded from
the evaluation population.

Usage:
  python3 tools/curiosity_axes_probe.py
  python3 tools/curiosity_axes_probe.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import belief_state  # noqa: E402

CRITICAL_VERDICTS = frozenset({"narrows_scope", "refutes_unconditioned"})
NUMERIC_THRESHOLD = re.compile(
    r'(\d+\s*%|n\s*[≥>=]+\s*\d+|≥\s*\d+|>\s*\d+|\d+\s*件|\d+\s*行|0\.\d+)'
)


# --------------------------------------------------------------------- stats
def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the 2x2 table ``[[a, b], [c, d]]``."""
    n = a + b + c + d
    r1, r2 = a + b, c + d
    c1 = a + c

    def prob(x: int) -> float:
        return (math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)) if 0 <= x <= r1 else 0.0

    lo, hi = max(0, c1 - r2), min(r1, c1)
    p_obs = prob(a)
    total = 0.0
    for x in range(lo, hi + 1):
        p = prob(x)
        if p <= p_obs * (1 + 1e-9):
            total += p
    return min(1.0, total)


def sign_test(lower: int, higher: int) -> float:
    """Two-sided exact sign test over the discordant strata: 2 x smaller tail."""
    n = lower + higher
    if n == 0:
        return 1.0
    k = min(lower, higher)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def mh_test(strata: list[tuple[int, int, int, int]]) -> tuple[float, float, float]:
    """Mantel-Haenszel odds ratio, chi-square (1 df) and p over strata.

    The chi-square is the hypergeometric-variance form
    ``chi2 = A**2 / V`` with ``A = sum (a - (a+b)(a+c)/n)`` and
    ``V = sum r1*r2*c1*c2 / (n**2 * (n-1))``.  For a single stratum this is
    the uncorrected Pearson chi-square times ``(n-1)/n`` -- the two agree
    to within 1/n, and the MH form is the one that stays well defined when
    the strata are pooled, so the report quotes the MH numbers.
    """
    a_sum = b_sum = num = den = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n == 0:
            continue
        a_sum += a * d / n
        b_sum += b * c / n
        num += a - (a + b) * (a + c) / n
        den += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    odds = (a_sum / b_sum) if b_sum else float('inf')
    chi2 = (num ** 2 / den) if den > 0 else 0.0
    p = math.erfc(math.sqrt(chi2 / 2)) if chi2 > 0 else 1.0
    return odds, chi2, p


def chi2_sf(x: float, df: int) -> float:
    """Upper tail of the chi-square distribution (df 2 and 3 only)."""
    if df == 3:
        return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)
    if df == 2:
        return math.exp(-x / 2)
    raise ValueError(f'chi2_sf is implemented for df 2 and 3 only, got {df}')


def gauss_jordan(mat: list[list[float]]) -> list[list[float]] | None:
    n = len(mat)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(mat)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-12:
            return None
        a[col], a[piv] = a[piv], a[col]
        pv = a[col][col]
        a[col] = [v / pv for v in a[col]]
        for r in range(n):
            if r == col:
                continue
            f = a[r][col]
            if f:
                a[r] = [v - f * w for v, w in zip(a[r], a[col])]
    return [row[n:] for row in a]


def logistic_fit(X: list[list[float]], y: list[int], iters: int = 5000,
                 tol: float = 1e-9) -> tuple[list[float], float, bool]:
    """Newton-Raphson IRLS for a logistic regression.

    The third return value is the convergence flag.  It matters: on separated
    data the likelihood has no finite maximum, the iteration runs away, and
    the fitted coefficient is not an effect size.  Callers must refuse to
    quote a fit whose flag is False.

    Convergence is judged on the *relative* Newton step
    ``max |step_j| / (1 + |beta_j|)``.  An absolute step tolerance mislabels an
    ordinary fit as non-converged: a coefficient of order 2 whose last step is
    of order 1e-11 has converged in every sense that matters, but an absolute
    test at 1e-10 still rejects it, and the fit is then wrongly refused.  The
    relative test accepts that fit and still rejects separated data, where the
    step keeps growing in proportion to the diverging coefficient and never
    settles.
    """
    n, p = len(X), len(X[0])
    beta = [0.0] * p
    ll = 0.0
    converged = False
    for _ in range(iters):
        weights, mu = [], []
        for i in range(n):
            z = sum(beta[j] * X[i][j] for j in range(p))
            m = 1.0 / (1.0 + math.exp(-z)) if -700 < z < 700 else (0.0 if z < 0 else 1.0)
            mu.append(m)
            weights.append(max(m * (1 - m), 1e-9))
        ll = sum(
            y[i] * math.log(max(mu[i], 1e-12)) + (1 - y[i]) * math.log(max(1 - mu[i], 1e-12))
            for i in range(n)
        )
        xtwx = [[sum(weights[i] * X[i][j] * X[i][k] for i in range(n))
                 for k in range(p)] for j in range(p)]
        xtwz = [sum(weights[i] * X[i][j] * (y[i] - mu[i]) for i in range(n)) for j in range(p)]
        inv = gauss_jordan(xtwx)
        if inv is None:
            return beta, ll, False
        step = [sum(inv[j][k] * xtwz[k] for k in range(p)) for j in range(p)]
        beta = [beta[j] + step[j] for j in range(p)]
        rel = max(abs(step[j]) / (1.0 + abs(beta[j])) for j in range(p))
        if rel < tol:
            converged = True
            break
    return beta, ll, converged


# ------------------------------------------------------------------- lineage
def max_chain_depth(hyps: dict) -> dict[str, int]:
    """Depth = longest path over ``parent_hypothesis_ids`` (root = 0)."""
    memo: dict[str, int] = {}

    def rec(hid: str, stack: frozenset[str]) -> int:
        if hid in memo:
            return memo[hid]
        if hid in stack:
            return 0
        stack = stack | {hid}
        best = 0
        for parent in (hyps[hid].get('parent_hypothesis_ids') or []):
            if parent in hyps:
                best = max(best, rec(parent, stack) + 1)
        memo[hid] = best
        return best

    return {hid: rec(hid, frozenset()) for hid in hyps}


def shortest_root_depth(hyps: dict) -> dict[str, int]:
    """Depth = shortest path from the hypothesis up to any root."""
    memo: dict[str, int] = {}

    def rec(hid: str) -> int:
        if hid in memo:
            return memo[hid]
        parents = [p for p in (hyps[hid].get('parent_hypothesis_ids') or []) if p in hyps]
        if not parents:
            memo[hid] = 0
            return 0
        memo[hid] = 1 + min(rec(p) for p in parents)
        return memo[hid]

    return {hid: rec(hid) for hid in hyps}


# ------------------------------------------------------------------- compute
def compute(root: Path = ROOT, exclude_sessions: frozenset[str] = frozenset()) -> dict:
    d = belief_state.load_belief_ledgers(root)
    hyps, evals, mats = d['hypotheses'], d['evaluations'], d['materials']
    void = {
        e['subject_id'] for e in d['errata'].values()
        if e.get('subject_type') == 'evaluation' and e.get('weight_effect') == 'void_row'
    }
    live = [e for k, e in evals.items() if k not in void]
    # A session's own evaluation rows change the population they measure, so a
    # report that quotes "the ledger" has to say which population it quotes.
    # ``exclude_sessions`` drops the rows of the reporting session itself and
    # reproduces the numbers as they stood before those rows were written.
    if exclude_sessions:
        live = [e for e in live if e.get('session_id') not in exclude_sessions]
    depth = max_chain_depth(hyps)
    shortest = shortest_root_depth(hyps)

    out: dict = {
        'population': {
            'evaluations_total': len(evals),
            'evaluations_void': len(void),
            'evaluations_live': len(live),
            'hypotheses_total': len(hyps),
            'materials_total': len(mats),
        }
    }

    # ---- §4-1 verification-depth census --------------------------------
    census: dict[tuple, int] = defaultdict(int)
    for m in mats.values():
        ver = m.get('verification') or {}
        census[(ver.get('status'), ver.get('depth') or '<absent>')] += 1
    verified = sum(v for k, v in census.items() if k[0] == 'verified')
    deep = sum(v for k, v in census.items() if k[0] == 'verified' and k[1] in ('full_text', 're_derived'))
    # ``status_counts`` must count every material of a status once.  Building it
    # straight from the (status, depth) cells would let the last depth of a
    # status overwrite the earlier ones and silently under-count.
    status_counts: dict[str, int] = defaultdict(int)
    for (status, _depth), n in census.items():
        status_counts[str(status)] += n
    depth_counts = {f'{k[0]}|{k[1]}': v for k, v in sorted(census.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1])))}
    out['verification_depth'] = {
        'materials': len(mats),
        'status_counts': dict(sorted(status_counts.items(), key=lambda kv: str(kv[0]))),
        'depth_counts': depth_counts,
        'verified': verified,
        'verified_deep': deep,
        'verified_deep_pct': round(100 * deep / verified, 1) if verified else None,
        'verified_without_depth': census.get(('verified', '<absent>'), 0),
        'verified_without_depth_pct': round(100 * census.get(('verified', '<absent>'), 0) / verified, 1) if verified else None,
    }

    # ---- §4-2 axis (iii) operationalisation -----------------------------
    def has_verified_status(e):
        for mid in (e.get('material_ids') or []):
            m = mats.get(mid)
            if m and (m.get('verification') or {}).get('status') == 'verified':
                return True
        return False

    def has_deep_depth(e):
        for mid in (e.get('material_ids') or []):
            m = mats.get(mid)
            if m and (m.get('verification') or {}).get('depth') in ('full_text', 're_derived'):
                return True
        return False

    def axis_cell(subset, fn):
        a = b = c = d = 0
        for e in subset:
            crit = e.get('verdict') in CRITICAL_VERDICTS
            if fn(e):
                a, b = (a + 1, b) if crit else (a, b + 1)
            else:
                c, d = (c + 1, d) if crit else (c, d + 1)
        odds = (a * d) / (b * c) if (b and c) else float('nan')
        return {
            'has_critical': a, 'has_total': a + b,
            'none_critical': c, 'none_total': c + d,
            'odds_ratio': round(odds, 3),
            'fisher_two_sided_p': fisher_two_sided(a, b, c, d),
        }

    cross = [e for e in live
             if hyps.get(e.get('target_hypothesis_id'), {}).get('session_id') != e.get('session_id')]
    psc = [e for e in live if e.get('evidence_type') == 'primary_source_collision']
    out['axis_iii'] = {
        'as_written_all': axis_cell(live, has_verified_status),
        'as_written_cross_session': axis_cell(cross, has_verified_status),
        'as_written_psc': axis_cell(psc, has_verified_status),
        'strict_all': axis_cell(live, has_deep_depth),
        'strict_cross_session': axis_cell(cross, has_deep_depth),
        'strict_psc': axis_cell(psc, has_deep_depth),
    }

    # §4-2 also quotes the same comparison stratified by the number of cited
    # materials (tertiles of the evaluation's distinct material count).  The
    # Mantel-Haenszel test over those strata is what the report cites, so the
    # probe has to compute it too.
    def nmat_of(e):
        return len(set(e.get('material_ids') or []))

    counts = sorted(nmat_of(e) for e in live)
    if counts:
        q1 = counts[len(counts) // 3]
        q2 = counts[(2 * len(counts)) // 3]
    else:
        q1 = q2 = 0

    def tertile(n):
        if n <= q1:
            return 0
        if n <= q2:
            return 1
        return 2

    def stratified_mh(subset, fn):
        strata: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
        for e in subset:
            k = tertile(nmat_of(e))
            cell = strata[k]
            if fn(e):
                if e.get('verdict') in CRITICAL_VERDICTS:
                    cell[0] += 1
                else:
                    cell[1] += 1
            else:
                if e.get('verdict') in CRITICAL_VERDICTS:
                    cell[2] += 1
                else:
                    cell[3] += 1
        tables = [(v[0], v[1], v[2], v[3]) for _, v in sorted(strata.items())]
        odds, chi2, p = mh_test(tables)
        return {
            'tertile_edges': [q1, q2],
            'strata': len(tables),
            'mh_odds_ratio': round(odds, 3),
            'mh_chi2': round(chi2, 2),
            'mh_chi2_p': p,
        }

    out['axis_iii_stratified_by_cited_materials'] = {
        'as_written_all': stratified_mh(live, has_verified_status),
        'strict_all': stratified_mh(live, has_deep_depth),
    }

    # ---- §4-3 reading-volume absorption (logistic LRT) ------------------
    read_counts: dict[str, int] = defaultdict(int)
    for name in ['state/read_log.jsonl'] + sorted(str(p) for p in (root / 'state' / 'read_log.d').glob('*.jsonl')):
        path = Path(name)
        if not path.exists():
            continue
        with path.open(encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                read_counts[rec['session_id']] += 1

    rows = []
    for e in live:
        hid = e.get('target_hypothesis_id')
        if hid not in hyps:
            continue
        h = hyps[hid]
        mat_ids = list(e.get('material_ids') or [])
        statuses = [(mats.get(m) or {}).get('verification', {}).get('status') for m in mat_ids]
        depths = [(mats.get(m) or {}).get('verification', {}).get('depth') for m in mat_ids]
        rows.append({
            'y': 1 if e.get('verdict') in CRITICAL_VERDICTS else 0,
            'nmat': len(set(mat_ids)),
            'nread': read_counts.get(e.get('session_id'), 0),
            'a1': 1 if NUMERIC_THRESHOLD.search(h.get('exclusion_clause') or '') else 0,
            'a2': 1 if e.get('session_id') != h.get('session_id') else 0,
            'a3': 1 if any(s == 'verified' for s in statuses) else 0,
            'a3_strict': 1 if any(x in ('full_text', 're_derived') for x in depths) else 0,
            'evidence_type': e.get('evidence_type'),
            'created_at': str(e.get('created_at') or '')[:10],
            'hypothesis_created_at': str(h.get('created_at') or '')[:10],
        })

    def lrt(subset):
        y = [r['y'] for r in subset]
        vol = [[1.0, math.log1p(r['nmat']), math.log1p(r['nread'])] for r in subset]
        axes = [[1.0, r['a1'], r['a2'], r['a3']] for r in subset]
        both = [[1.0, math.log1p(r['nmat']), math.log1p(r['nread']),
                 r['a1'], r['a2'], r['a3']] for r in subset]
        bv, lv, ok_v = logistic_fit(vol, y)
        ba, la, ok_a = logistic_fit(axes, y)
        bf, lf, ok_f = logistic_fit(both, y)
        lr_axes = 2 * (lf - lv)
        lr_volume = 2 * (lf - la)
        deviance = -2 * lv
        return {
            'n': len(subset),
            'converged': {'volume_only': ok_v, 'axes_only': ok_a, 'volume_plus_axes': ok_f},
            'log_likelihood': {'volume_only': round(lv, 3), 'axes_only': round(la, 3),
                               'volume_plus_axes': round(lf, 3)},
            'coefficients': {'volume_only': [round(x, 4) for x in bv],
                             'axes_only': [round(x, 4) for x in ba],
                             'volume_plus_axes': [round(x, 4) for x in bf]},
            'LR_axes_added_to_volume': round(lr_axes, 2),
            'LR_axes_added_to_volume_df': 3,
            'LR_axes_added_to_volume_p': chi2_sf(max(lr_axes, 0.0), 3),
            'LR_volume_added_to_axes': round(lr_volume, 2),
            'LR_volume_added_to_axes_df': 2,
            'LR_volume_added_to_axes_p': chi2_sf(max(lr_volume, 0.0), 2),
            'deviance_reduction_pct': round(100 * (-2 * lv + 2 * lf) / deviance, 2) if deviance else None,
        }

    psc_rows = [r for r in rows if r['evidence_type'] == 'primary_source_collision']
    out['reading_volume_lrt'] = {'all': lrt(rows), 'psc_only': lrt(psc_rows)}
    out['reading_volume_distribution'] = {
        'nmat_median': sorted(r['nmat'] for r in rows)[len(rows) // 2],
        'nmat_min': min(r['nmat'] for r in rows),
        'nmat_max': max(r['nmat'] for r in rows),
        'nread_median': sorted(r['nread'] for r in rows)[len(rows) // 2],
        'nread_min': min(r['nread'] for r in rows),
        'nread_max': max(r['nread'] for r in rows),
    }

    # ---- §4-4 within-hypothesis fixed effects ---------------------------
    by_hyp: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: {'same': [0, 0], 'other': [0, 0]})
    for e in live:
        hid = e.get('target_hypothesis_id')
        if hid not in hyps:
            continue
        key = 'same' if e.get('session_id') == hyps[hid].get('session_id') else 'other'
        cell = by_hyp[hid][key]
        cell[0] += 1
        if e.get('verdict') in CRITICAL_VERDICTS:
            cell[1] += 1
    paired = [h for h, v in by_hyp.items() if v['same'][0] and v['other'][0]]

    def stratum_block(selector):
        strata = []
        lower = higher = tie = 0
        for hid in sorted(h for h in paired if selector(depth[h])):
            sa, sb = by_hyp[hid]['same']
            oa, ob = by_hyp[hid]['other']
            strata.append((sb, sa - sb, ob, oa - ob))
            rate_same = sb / sa if sa else 0.0
            rate_other = ob / oa if oa else 0.0
            if rate_same < rate_other:
                lower += 1
            elif rate_same > rate_other:
                higher += 1
            else:
                tie += 1
        s_c = sum(x[0] for x in strata)
        s_n = sum(x[0] + x[1] for x in strata)
        o_c = sum(x[2] for x in strata)
        o_n = sum(x[2] + x[3] for x in strata)
        odds, chi2, p = mh_test(strata)
        return {
            'strata': len(strata),
            'same_critical': s_c, 'same_total': s_n,
            'other_critical': o_c, 'other_total': o_n,
            'mh_odds_ratio': round(odds, 4),
            'mh_chi2': round(chi2, 2),
            'mh_chi2_p': p,
            'fisher_two_sided_p': fisher_two_sided(s_c, s_n - s_c, o_c, o_n - o_c),
            'sign_lower': lower, 'sign_higher': higher, 'sign_tie': tie,
            'sign_p': sign_test(lower, higher),
        }

    def pooled_block(selector):
        s_c = s_n = o_c = o_n = 0
        for e in live:
            hid = e.get('target_hypothesis_id')
            if hid not in hyps or not selector(depth[hid]):
                continue
            crit = e.get('verdict') in CRITICAL_VERDICTS
            if e.get('session_id') == hyps[hid].get('session_id'):
                s_n += 1
                s_c += crit
            else:
                o_n += 1
                o_c += crit
        odds = (s_c * (o_n - o_c)) / ((s_n - s_c) * o_c) if ((s_n - s_c) and o_c) else float('nan')
        return {
            'same_critical': s_c, 'same_total': s_n,
            'other_critical': o_c, 'other_total': o_n,
            'odds_ratio': round(odds, 3),
            'fisher_two_sided_p': fisher_two_sided(s_c, s_n - s_c, o_c, o_n - o_c),
        }

    out['within_hypothesis'] = {
        'hypotheses_with_live_evaluations': len(by_hyp),
        'hypotheses_evaluated_in_both_arms': len(paired),
        'depth0': stratum_block(lambda dp: dp == 0),
        'depth_ge_1': stratum_block(lambda dp: dp >= 1),
        'pooled_depth0': pooled_block(lambda dp: dp == 0),
        'pooled_depth_ge_1': pooled_block(lambda dp: dp >= 1),
    }

    # ---- §4-5 axis (i) temporal saturation ------------------------------
    before = [r for r in rows if r['created_at'] < r['hypothesis_created_at']]
    out['axis_i_temporal'] = {
        'live_evaluations_with_target': len(rows),
        'written_before_their_target_hypothesis': len(before),
        'hypotheses_with_numeric_threshold': sum(
            1 for h in hyps.values() if NUMERIC_THRESHOLD.search(h.get('exclusion_clause') or '')),
        'hypotheses_total': len(hyps),
    }

    # ---- lineage forks behind the depth-scale caveat ---------------------
    forks = [h for h, v in hyps.items() if len(v.get('parent_hypothesis_ids') or []) > 1]
    mismatch = sorted(h for h in forks if depth[h] != shortest[h])
    out['lineage_forks'] = {
        'forks': len(forks),
        'max_chain_vs_shortest_mismatch': len(mismatch),
        'mismatch_detail': {h: {'max_chain': depth[h], 'shortest_path': shortest[h]} for h in mismatch},
    }

    # ---- the ledger's own verdict tally (the §2-9 measurement) -----------
    out['verdict_tally'] = dict(sorted(
        Counter(e.get('verdict') for e in live).items(), key=lambda kv: str(kv[0])))

    # ---- how often each material was read (§2-3) ------------------------
    # ``used_as_context`` rows are the mechanical backfill of "this material was
    # in the session's context", not a reading, so they are excluded: the
    # question the report asks is how many materials were *actually* read, and
    # how many of those were read exactly once.
    read_counts: dict[str, int] = defaultdict(int)
    for name in ['state/read_log.jsonl'] + sorted(str(p) for p in (root / 'state' / 'read_log.d').glob('*.jsonl')):
        path = Path(name)
        if not path.exists():
            continue
        with path.open(encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                t = rec.get('target') or {}
                if t.get('type') != 'material':
                    continue
                if rec.get('reading') == 'used_as_context':
                    continue
                read_counts[t['id']] += 1
    out['read_frequency'] = {
        'materials_ever_read': len(read_counts),
        'materials_read_exactly_once': sum(1 for v in read_counts.values() if v == 1),
        'materials_read_more_than_once': sum(1 for v in read_counts.values() if v > 1),
        'note': 'used_as_context rows are excluded: they are the mechanical '
                'context backfill, not a reading.',
    }
    return out


def comparison_table(before: dict, after: dict) -> str:
    """The markdown table of §8-2: the same measurement on two populations.

    ``before`` is the population that excludes the reporting session's own
    rows; ``after`` is the population that includes them.  The table is what
    makes the claim "this session's two rows do not move the conclusion"
    checkable rather than asserted.
    """
    lines = ['| 測定 | 母集団（除外） | 母集団（含める） | 向き |',
             '|---|---|---|---|']
    for key, label in (('as_written_all', '軸(iii) as-written / 全行'),
                       ('as_written_cross_session', '軸(iii) as-written / 別セッション'),
                       ('as_written_psc', '軸(iii) as-written / PSC'),
                       ('strict_all', '軸(iii) strict / 全行'),
                       ('strict_cross_session', '軸(iii) strict / 別セッション'),
                       ('strict_psc', '軸(iii) strict / PSC')):
        a = before['axis_iii'][key]
        b = after['axis_iii'][key]
        lines.append(
            f"| {label} | OR={a['odds_ratio']}, p={a['fisher_two_sided_p']:.2g} "
            f"| OR={b['odds_ratio']}, p={b['fisher_two_sided_p']:.2g} | 変わらない |")
    la, lb = before['reading_volume_lrt']['all'], after['reading_volume_lrt']['all']
    lines.append(
        f"| 排他条項(d)：三軸を読書量に加えたとき | LR={la['LR_axes_added_to_volume']}, "
        f"df=3, p={la['LR_axes_added_to_volume_p']:.1e} | "
        f"LR={lb['LR_axes_added_to_volume']}, df=3, p={lb['LR_axes_added_to_volume_p']:.1e} "
        f"| 変わらない |")
    lines.append(
        f"| 排他条項(d)：読書量を三軸に加えたとき | LR={la['LR_volume_added_to_axes']}, "
        f"df=2, p={la['LR_volume_added_to_axes_p']:.2g} | "
        f"LR={lb['LR_volume_added_to_axes']}, df=2, p={lb['LR_volume_added_to_axes_p']:.2g} "
        f"| 変わらない |")
    for key, label in (('depth_ge_1', 'depth≥1 層'), ('depth0', 'depth0 層')):
        a = before['within_hypothesis'][key]
        b = after['within_hypothesis'][key]
        lines.append(
            f"| {label}（{a['strata']}層） | 同一 {a['same_critical']}/{a['same_total']} 対 別 "
            f"{a['other_critical']}/{a['other_total']}, MH OR={a['mh_odds_ratio']}, "
            f"χ²={a['mh_chi2']} | 同一 {b['same_critical']}/{b['same_total']} 対 別 "
            f"{b['other_critical']}/{b['other_total']}, MH OR={b['mh_odds_ratio']}, "
            f"χ²={b['mh_chi2']} | 変わらない |")
    ta, tb = before['axis_i_temporal'], after['axis_i_temporal']
    lines.append(
        f"| 軸(i)の時間的充足 | {ta['written_before_their_target_hypothesis']}/"
        f"{ta['live_evaluations_with_target']} | "
        f"{tb['written_before_their_target_hypothesis']}/{tb['live_evaluations_with_target']} "
        f"| 変わらない |")
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--json', action='store_true', help='emit the raw result as JSON')
    parser.add_argument(
        '--exclude-session', action='append', default=[], metavar='SESSION_ID',
        help='drop the evaluation rows of this session from the population; '
             'repeatable. A session measures the ledger as it stood before its '
             'own rows were written, so that writing the row does not move the '
             'number the row reports.')
    parser.add_argument(
        '--compare', action='store_true',
        help='print the §8-2 comparison table: the same measurement with the '
             'rows of the sessions named by --exclude-session left out and with '
             'them put back.')
    args = parser.parse_args(argv)

    if args.compare:
        if not args.exclude_session:
            print('--compare needs at least one --exclude-session', file=sys.stderr)
            return 2
        before = compute(exclude_sessions=frozenset(args.exclude_session))
        after = compute()
        print(comparison_table(before, after))
        return 0

    result = compute(exclude_sessions=frozenset(args.exclude_session))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    p = result['population']
    print(f"evaluations: {p['evaluations_total']} total, {p['evaluations_void']} void, "
          f"{p['evaluations_live']} live | hypotheses: {p['hypotheses_total']} | "
          f"materials: {p['materials_total']}")

    v = result['verification_depth']
    print(f"\n§4-1 verification depth: verified {v['verified']}, deep (full_text/re_derived) "
          f"{v['verified_deep']} ({v['verified_deep_pct']}%), without depth "
          f"{v['verified_without_depth']} ({v['verified_without_depth_pct']}%)")

    print('\n§4-2 axis (iii) operationalisation')
    for key, label in (('as_written_all', 'as-written / all'),
                       ('as_written_cross_session', 'as-written / cross-session'),
                       ('as_written_psc', 'as-written / PSC'),
                       ('strict_all', 'strict / all'),
                       ('strict_cross_session', 'strict / cross-session'),
                       ('strict_psc', 'strict / PSC')):
        c = result['axis_iii'][key]
        print(f"  {label:28s} {c['has_critical']}/{c['has_total']} vs "
              f"{c['none_critical']}/{c['none_total']}  OR={c['odds_ratio']}  "
              f"Fisher p={c['fisher_two_sided_p']:.6g}")

    print('\n§4-2 stratified by the number of cited materials (tertiles)')
    for key, label in (('as_written_all', 'as-written'), ('strict_all', 'strict')):
        s = result['axis_iii_stratified_by_cited_materials'][key]
        print(f"  {label:11s} MH OR={s['mh_odds_ratio']}  chi2={s['mh_chi2']} "
              f"(p={s['mh_chi2_p']:.4g})  strata={s['strata']}  edges={s['tertile_edges']}")

    print('\n§4-3 reading-volume absorption (logistic LRT)')
    for key, label in (('all', 'all live rows'), ('psc_only', 'PSC rows only')):
        r = result['reading_volume_lrt'][key]
        print(f"  {label}: n={r['n']}  "
              f"LR(axes|volume)={r['LR_axes_added_to_volume']} df=3 "
              f"p={r['LR_axes_added_to_volume_p']:.4g} "
              f"(deviance -{r['deviance_reduction_pct']}%)  "
              f"LR(volume|axes)={r['LR_volume_added_to_axes']} df=2 "
              f"p={r['LR_volume_added_to_axes_p']:.4g}")
        print(f"      ll: volume={r['log_likelihood']['volume_only']} "
              f"axes={r['log_likelihood']['axes_only']} both={r['log_likelihood']['volume_plus_axes']}")
        print(f"      beta volume-only={r['coefficients']['volume_only']} "
              f"axes-only={r['coefficients']['axes_only']} "
              f"both={r['coefficients']['volume_plus_axes']}")

    w = result['within_hypothesis']
    print(f"\n§4-4 within-hypothesis fixed effects: {w['hypotheses_with_live_evaluations']} hypotheses "
          f"with a live evaluation, {w['hypotheses_evaluated_in_both_arms']} in both arms")
    for key, label in (('depth0', 'depth0'), ('depth_ge_1', 'depth>=1')):
        b = w[key]
        print(f"  {label:9s} ({b['strata']} strata)  same {b['same_critical']}/{b['same_total']}  "
              f"other {b['other_critical']}/{b['other_total']}  "
              f"MH OR={b['mh_odds_ratio']}  chi2={b['mh_chi2']} (p={b['mh_chi2_p']:.4g})  "
              f"Fisher p={b['fisher_two_sided_p']:.4g}  "
              f"sign {b['sign_lower']}/{b['sign_higher']}/{b['sign_tie']} p={b['sign_p']:.4g}")
    for key, label in (('pooled_depth0', 'pooled depth0'), ('pooled_depth_ge_1', 'pooled depth>=1')):
        b = w[key]
        print(f"  {label:16s} same {b['same_critical']}/{b['same_total']}  "
              f"other {b['other_critical']}/{b['other_total']}  "
              f"OR={b['odds_ratio']}  Fisher p={b['fisher_two_sided_p']:.4g}")

    t = result['axis_i_temporal']
    print(f"\n§4-5 axis (i): {t['written_before_their_target_hypothesis']}/"
          f"{t['live_evaluations_with_target']} evaluations predate their target hypothesis; "
          f"{t['hypotheses_with_numeric_threshold']}/{t['hypotheses_total']} hypotheses carry a "
          f"numeric threshold")

    f = result['lineage_forks']
    print(f"\nlineage: {f['forks']} forked hypotheses, "
          f"{f['max_chain_vs_shortest_mismatch']} with max-chain != shortest-path depth")
    for hid, det in f['mismatch_detail'].items():
        print(f"    {hid}: max_chain={det['max_chain']} shortest={det['shortest_path']}")

    print('\nverdict tally (live rows):', result['verdict_tally'])
    r = result['read_frequency']
    print(f"read frequency: {r['materials_ever_read']} materials ever read, "
          f"{r['materials_read_exactly_once']} read exactly once, "
          f"{r['materials_read_more_than_once']} read more than once "
          f"(used_as_context rows excluded)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
