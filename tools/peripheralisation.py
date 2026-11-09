#!/usr/bin/env python3
"""Measure whether *not* mentioning a record predicts its later re-visit.

Why this tool exists
--------------------
``readings/2026-11-08-ten-experiments-on-labeling-coupling-forgetting-and-
kinship.md`` §14 read Coman et al. (2016, *PNAS* 113:8171-8176,
``MAT-EVD-20261108-270947``) onto this archive and drew a consequence the
archive had not tested:

    引用は中立な接続ではない。特定ノートを反復顕彰することは、同じ問いに属する
    未言及記録への到達確率を押し下げる。

In Coman's paradigm the effect is *retrieval-induced forgetting* across
speakers: an item mentioned twice is reinforced, an item in the same category
that was mentioned **once** and left out is suppressed, and a category-mate
never touched at all is the baseline.  The asymmetry is the finding — suppression
needs one omission, reinforcement needs two mentions.

§15 of that report proposed an archive-level version of the test and deliberately
did **not** run it.  This module is the instrument for that proposal, so the
number is re-runnable as the corpus grows instead of living in a scratch script
that no longer exists (the defect ``tools/inheritance.py`` was written to fix).

What is measured
----------------
For every session ``B`` that names context materials and at least one question:

* the **pool** is every material named in ``context_material_ids`` by an earlier
  session ``A`` (strictly earlier ``started_at`` date) that shares a question
  with ``B``;
* each pool member ``m`` is classified against ``B`` exactly as Coman classifies
  against a conversation:

  - ``Rp+`` — ``m`` is in ``context_material_ids`` of ``B`` (mentioned again);
  - ``Rp-`` — ``m`` is not mentioned by ``B``, but some material ``B`` *did*
    mention shares a ``motif_ids`` entry with ``m`` (a category-mate was
    retrieved, ``m`` was left out);
  - ``Nrp`` — ``m`` is not mentioned by ``B`` and no category-mate of ``m`` was
    mentioned either (baseline).

  ``motif_ids`` is the archive's own category system, so "same category" is not
  imported from the source paper.

* the **outcome** is whether ``m`` comes back on the archive's *next active day*
  after ``B`` — the earliest session date strictly later than ``B`` whose session
  shares a question with ``B``.  Primary outcome: ``m`` is in that day's
  ``context_material_ids``.  Secondary outcome adds hand-written ``read_log``
  rows of that day whose target is ``m``.

Rows whose ``note`` contains ``機械的バックフィル`` are excluded from the
secondary outcome: ``prompts/start.md`` records that those rows are transcribed
mechanically from ``sessions.context_material_ids``, so counting them would
double-count the primary signal rather than corroborate it.

What this is not
----------------
This is a mirror, not a verdict.  Three confounds are structural and are
**reported, not removed**:

1. *Selection.* ``Rp+`` items are in ``context_material_ids`` because a session
   judged them relevant, which may itself predict future relevance.  A higher
   re-visit rate for ``Rp+`` is therefore not evidence of strengthening.
2. *Recency.* ``Rp+`` items were touched at ``B`` by construction; ``Nrp`` items
   may be much older.  The age distribution per condition is printed so the
   reader can see the imbalance rather than trust an adjusted estimate.
3. *Motif breadth.* A material with many ``motif_ids`` is more likely to have a
   category-mate mentioned, so ``Rp-`` over-represents broadly tagged materials.
   The motif-count distribution per condition is printed for the same reason.

Observations cluster inside sessions, so the headline interval is a
**session-clustered bootstrap** over ``B`` sessions, not a per-material interval.
The decision rule that reads these numbers was fixed in the report before the
first run; the tool does not decide anything.

Usage:
  python3 tools/peripheralisation.py
  python3 tools/peripheralisation.py --outcome any_later --json
  python3 tools/peripheralisation.py --bootstrap 20000 --seed 20261108
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

CONDITIONS = ("Rp+", "Rp-", "Nrp")
BACKFILL_MARKER = "機械的バックフィル"
MIN_OBS_DEFAULT = 30
MIN_CLUSTERS_DEFAULT = 10


def _load(collection: str, id_key: str, root: Path) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    rows = ledger_io.load_jsonl_union(
        root / "state" / f"{collection}.jsonl", id_key, errors, root=root
    )
    return rows


def session_date(row: dict[str, Any]) -> str:
    """``started_at`` truncated to a calendar day.

    583 of 602 session rows carry a date-only ``started_at``, so the archive
    cannot order two sessions that share a date.  Every comparison here uses
    strict date inequality and never claims an intra-day order.
    """
    return str(row.get("started_at", ""))[:10]


def _to_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@dataclass
class Cluster:
    """Per-session (``B``) tallies.  Observations are aggregated, not stored."""

    session_id: str
    day: str
    outcome_day: str
    n: dict[str, int] = field(default_factory=lambda: dict.fromkeys(CONDITIONS, 0))
    hit: dict[str, int] = field(default_factory=lambda: dict.fromkeys(CONDITIONS, 0))
    hit_secondary: dict[str, int] = field(default_factory=lambda: dict.fromkeys(CONDITIONS, 0))
    age_sum: dict[str, int] = field(default_factory=lambda: dict.fromkeys(CONDITIONS, 0))
    motif_sum: dict[str, int] = field(default_factory=lambda: dict.fromkeys(CONDITIONS, 0))
    ages: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))


def collect(
    root: Path = ROOT, *, outcome: str = "next_day"
) -> tuple[list[Cluster], dict[str, Any]]:
    """Classify every (session, pool-material) pair and score its re-visit."""
    sessions = _load("sessions", "session_id", root)
    materials = _load("materials", "material_id", root)
    read_log = _load("read_log", "read_id", root)

    motifs: dict[str, frozenset[str]] = {
        mid: frozenset(row.get("motif_ids") or []) for mid, row in materials.items()
    }

    ctx: dict[str, list[str]] = {
        sid: [m for m in (row.get("context_material_ids") or []) if m in materials]
        for sid, row in sessions.items()
    }
    qids: dict[str, set[str]] = {
        sid: set(row.get("question_ids") or []) for sid, row in sessions.items()
    }
    day: dict[str, str] = {sid: session_date(row) for sid, row in sessions.items()}

    # Hand-written read_log rows per session, keyed to material targets.
    hand_reads: dict[str, set[str]] = defaultdict(set)
    backfill_rows = 0
    for row in read_log.values():
        note = row.get("note") or ""
        if BACKFILL_MARKER in note:
            backfill_rows += 1
            continue
        target = row.get("target") or {}
        if target.get("type") == "material":
            hand_reads[str(row.get("session_id"))].add(str(target.get("id")))

    # First day any session mentioned a material, for the recency confound.
    first_mention: dict[str, str] = {}
    for sid, items in ctx.items():
        for mid in items:
            prev = first_mention.get(mid)
            if prev is None or day[sid] < prev:
                first_mention[mid] = day[sid]

    by_day: dict[str, list[str]] = defaultdict(list)
    for sid, d in day.items():
        by_day[d].append(sid)
    ordered_days = sorted(by_day)

    # motif -> materials mentioned by a given session, for the Rp- test.
    def motif_index(items: Iterable[str]) -> set[str]:
        index: set[str] = set()
        for mid in items:
            index |= motifs.get(mid, frozenset())
        return index

    clusters: list[Cluster] = []
    for b in sorted(sessions, key=lambda s: (day[s], s)):
        if not ctx[b] or not qids[b]:
            continue
        b_day = day[b]
        pool: set[str] = set()
        for a in sessions:
            if day[a] >= b_day or not ctx[a]:
                continue
            if qids[a] & qids[b]:
                pool.update(ctx[a])
        if not pool:
            continue

        # Outcome window: sessions strictly later that share a question with B.
        later_days = [
            d for d in ordered_days
            if d > b_day and any(qids[c] & qids[b] for c in by_day[d])
        ]
        if not later_days:
            continue
        window = later_days[:1] if outcome == "next_day" else later_days
        window_sessions = [c for d in window for c in by_day[d] if qids[c] & qids[b]]
        returned = set()
        returned_secondary = set()
        for c in window_sessions:
            returned.update(ctx[c])
            returned_secondary.update(ctx[c])
            returned_secondary.update(hand_reads.get(c, set()))

        mentioned = set(ctx[b])
        touched_motifs = motif_index(mentioned)
        b_date = _to_date(b_day)
        out_day = window[0] if outcome == "next_day" else f"{window[0]}..{window[-1]}"

        cluster = Cluster(session_id=b, day=b_day, outcome_day=out_day)
        for mid in sorted(pool):
            if mid in mentioned:
                cond = "Rp+"
            elif motifs.get(mid, frozenset()) & touched_motifs:
                cond = "Rp-"
            else:
                cond = "Nrp"
            cluster.n[cond] += 1
            if mid in returned:
                cluster.hit[cond] += 1
            if mid in returned_secondary:
                cluster.hit_secondary[cond] += 1
            first = _to_date(first_mention.get(mid, b_day))
            age = (b_date - first).days if (b_date and first) else 0
            cluster.age_sum[cond] += max(age, 0)
            cluster.ages[cond].append(max(age, 0))
            cluster.motif_sum[cond] += len(motifs.get(mid, frozenset()))
        clusters.append(cluster)

    meta = {
        "outcome": outcome,
        "sessions_total": len(sessions),
        "sessions_eligible": len(clusters),
        "materials_total": len(materials),
        "materials_without_motifs": sum(1 for m in motifs.values() if not m),
        "read_log_rows": len(read_log),
        "read_log_backfill_rows_excluded": backfill_rows,
        "distinct_days": len(ordered_days),
    }
    return clusters, meta


def pooled(clusters: list[Cluster], key: str = "hit") -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for cond in CONDITIONS:
        n = sum(c.n[cond] for c in clusters)
        hits = sum(getattr(c, key)[cond] for c in clusters)
        out[cond] = {
            "observations": n,
            "revisited": hits,
            "rate": (hits / n) if n else 0.0,
            "mean_age_days": (sum(c.age_sum[cond] for c in clusters) / n) if n else 0.0,
            "mean_motif_count": (sum(c.motif_sum[cond] for c in clusters) / n) if n else 0.0,
        }
    return out


def _difference(clusters: list[Cluster], left: str, right: str, key: str = "hit") -> float:
    ln = sum(c.n[left] for c in clusters)
    rn = sum(c.n[right] for c in clusters)
    if not ln or not rn:
        return float("nan")
    lh = sum(getattr(c, key)[left] for c in clusters)
    rh = sum(getattr(c, key)[right] for c in clusters)
    return (lh / ln) - (rh / rn)


def clustered_bootstrap(
    clusters: list[Cluster],
    left: str,
    right: str,
    *,
    reps: int = 10000,
    seed: int = 20261108,
    key: str = "hit",
) -> dict[str, Any]:
    """Resample whole ``B`` sessions, because observations cluster inside them."""
    rng = random.Random(seed)
    n = len(clusters)
    diffs: list[float] = []
    for _ in range(reps):
        if not n:
            break
        sample = [clusters[rng.randrange(n)] for _ in range(n)]
        value = _difference(sample, left, right, key)
        if not math.isnan(value):
            diffs.append(value)
    if not diffs:
        return {"reps": 0, "ci_low": None, "ci_high": None, "excludes_zero": False}
    diffs.sort()

    def quantile(q: float) -> float:
        idx = min(len(diffs) - 1, max(0, int(q * (len(diffs) - 1))))
        return diffs[idx]

    low, high = quantile(0.025), quantile(0.975)
    return {
        "reps": len(diffs),
        "ci_low": low,
        "ci_high": high,
        "excludes_zero": (low > 0.0) or (high < 0.0),
        "boot_median": quantile(0.5),
    }


def two_proportion_z(clusters: list[Cluster], left: str, right: str, key: str = "hit") -> dict[str, Any]:
    """Unclustered descriptive z-test.  Reported beside, never instead of, the bootstrap."""
    ln = sum(c.n[left] for c in clusters)
    rn = sum(c.n[right] for c in clusters)
    if not ln or not rn:
        return {"z": None, "p_two_sided": None}
    lh = sum(getattr(c, key)[left] for c in clusters)
    rh = sum(getattr(c, key)[right] for c in clusters)
    p1, p2 = lh / ln, rh / rn
    pooled_p = (lh + rh) / (ln + rn)
    se = math.sqrt(pooled_p * (1 - pooled_p) * (1 / ln + 1 / rn))
    if se == 0:
        return {"z": None, "p_two_sided": None}
    z = (p1 - p2) / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"z": z, "p_two_sided": p}


def verdict(
    clusters: list[Cluster], *, min_obs: int = MIN_OBS_DEFAULT, min_clusters: int = MIN_CLUSTERS_DEFAULT
) -> dict[str, Any]:
    """Apply the decision rule that was pre-registered in the report.

    The rule is quoted here verbatim from §4 of
    ``readings/2026-11-08-a-pre-registered-count-of-what-was-not-mentioned.md``
    so the instrument cannot drift away from the text that fixed it.
    """
    stats = pooled(clusters)
    n_rp_minus = stats["Rp-"]["observations"]
    n_nrp = stats["Nrp"]["observations"]
    n_rp_plus = stats["Rp+"]["observations"]
    if len(clusters) < min_clusters or min(n_rp_minus, n_nrp) < min_obs:
        return {
            "status": "underpowered",
            "reason": (
                f"clusters={len(clusters)} (min {min_clusters}), "
                f"Rp-={n_rp_minus}, Nrp={n_nrp} (min {min_obs} each)"
            ),
        }
    boot = clustered_bootstrap(clusters, "Rp-", "Nrp")
    d = _difference(clusters, "Rp-", "Nrp")
    if not boot["excludes_zero"]:
        status = "undecided"
    elif d < 0:
        status = "supported"
    else:
        status = "contradicted"
    return {
        "status": status,
        "difference_rp_minus_minus_nrp": d,
        "bootstrap": boot,
        "n_rp_plus": n_rp_plus,
    }


def age_histogram(clusters: list[Cluster], buckets=(0, 1, 7, 30, 180, 10**6)) -> dict[str, Counter]:
    labels = ["0d", "1-6d", "7-29d", "30-179d", "180d+"]
    out = {cond: Counter() for cond in CONDITIONS}
    for cluster in clusters:
        for cond in CONDITIONS:
            for age in cluster.ages[cond]:
                for label, upper in zip(labels, buckets[1:]):
                    if age < upper:
                        out[cond][label] += 1
                        break
    return out


def summarize(
    clusters: list[Cluster],
    meta: dict[str, Any],
    *,
    key: str = "hit",
    reps: int = 10000,
    seed: int = 20261108,
) -> dict[str, Any]:
    stats = pooled(clusters, key)
    contrasts = {}
    for left, right in (("Rp-", "Nrp"), ("Rp+", "Nrp"), ("Rp+", "Rp-")):
        contrasts[f"{left}_minus_{right}"] = {
            "difference": _difference(clusters, left, right, key),
            "bootstrap": clustered_bootstrap(clusters, left, right, reps=reps, seed=seed, key=key),
            "unclustered_z": two_proportion_z(clusters, left, right, key),
        }
    hist = age_histogram(clusters)
    return {
        "meta": meta,
        "outcome_key": "context_material_ids" if key == "hit" else "context_or_handwritten_read_log",
        "conditions": stats,
        "contrasts": contrasts,
        "age_histogram": {cond: dict(hist[cond]) for cond in CONDITIONS},
        "verdict": verdict(clusters),
    }


def render(summary: dict[str, Any]) -> str:
    meta = summary["meta"]
    lines = [
        "# 言及されなかった記録の再訪率 — Rp+ / Rp- / Nrp",
        "",
        f"outcome: {meta['outcome']} ({summary['outcome_key']})",
        f"対象セッション: {meta['sessions_eligible']} / {meta['sessions_total']}  "
        f"(distinct days {meta['distinct_days']})",
        f"materials: {meta['materials_total']}  "
        f"(motif_ids を持たない {meta['materials_without_motifs']} 件は常に Nrp 側)",
        f"read_log: {meta['read_log_rows']} 行のうち機械的バックフィル "
        f"{meta['read_log_backfill_rows_excluded']} 行を副次アウトカムから除外",
        "",
        "| 条件 | 観測 | 再訪 | 再訪率 | 平均年齢(日) | 平均motif数 |",
        "|---|---|---|---|---|---|",
    ]
    for cond in CONDITIONS:
        s = summary["conditions"][cond]
        lines.append(
            f"| {cond} | {s['observations']} | {s['revisited']} | {s['rate']:.4f} "
            f"| {s['mean_age_days']:.1f} | {s['mean_motif_count']:.2f} |"
        )
    lines += ["", "## 対比（セッション・クラスタ化ブートストラップ）", ""]
    for name, block in summary["contrasts"].items():
        boot = block["bootstrap"]
        z = block["unclustered_z"]
        diff = block["difference"]
        diff_s = "nan" if diff != diff else f"{diff:+.4f}"
        if boot.get("ci_low") is None:
            ci = "CI n/a"
        else:
            ci = f"95% CI [{boot['ci_low']:+.4f}, {boot['ci_high']:+.4f}]"
        zs = "n/a" if z.get("z") is None else f"z={z['z']:+.2f}, p={z['p_two_sided']:.4g}"
        lines.append(f"- `{name}`: {diff_s}  {ci}  ({boot.get('reps', 0)} reps)  unclustered {zs}")
    lines += ["", "## 年齢分布（交絡の可視化、調整ではない）", ""]
    for cond in CONDITIONS:
        lines.append(f"- {cond}: {summary['age_histogram'][cond]}")
    verdict_block = summary["verdict"]
    lines += ["", "## 事前登録した判定規則の適用", ""]
    lines.append(f"- status: **{verdict_block['status']}**")
    for k, v in verdict_block.items():
        if k != "status":
            lines.append(f"- {k}: {v}")
    lines += [
        "",
        "選択・新近性・motif幅の三交絡は構造的であり、除去していない。",
        "この出力は鏡であって判定ではない。判定規則は報告 §4 に固定した。",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument(
        "--outcome",
        choices=("next_day", "any_later"),
        default="next_day",
        help="next_day = the archive's next active day (primary); any_later = every later day",
    )
    parser.add_argument(
        "--secondary",
        action="store_true",
        help="also count hand-written read_log rows, not just context_material_ids",
    )
    parser.add_argument("--bootstrap", type=int, default=10000, help="clustered bootstrap reps")
    parser.add_argument("--seed", type=int, default=20261108, help="bootstrap seed")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    clusters, meta = collect(args.root, outcome=args.outcome)
    key = "hit_secondary" if args.secondary else "hit"
    summary = summarize(clusters, meta, key=key, reps=args.bootstrap, seed=args.seed)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    else:
        print(render(summary))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
