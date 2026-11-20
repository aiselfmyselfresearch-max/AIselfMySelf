#!/usr/bin/env python3
"""Deterministic conditional-hypothesis posterior and information-gain engine (stdlib only).

Computes the archive's current belief distribution P_t(H | Q), epistemic uncertainty
u_i, lineage mass transfer (Gen-0 unconditioned roots -> Gen-1+ scoped hypotheses),
1-hop errata caution flags, and highest-information-gain competing hypothesis pairs
for core questions Q-001..Q-003 (and any sub-question carrying hypotheses).

Usage:
  python3 tools/belief_state.py
  python3 tools/belief_state.py --question Q-002
  python3 tools/belief_state.py --json
  python3 tools/belief_state.py --write-map
  python3 tools/belief_state.py --check-map
  python3 tools/belief_state.py --addressee-audit   # 問いをまたぐ質量（宛先の復元）。書き込みなし

Generation order: run this tool's --write-map BEFORE tools/map_build.py.
READING_MAP.md's inbound-mention graph is built over every root *.md, which
includes the generated BELIEF_MAP.md, so the reverse order is not a fixed point
(measured digests and the map_build-side warning: tools/map_build.py docstring).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
CORE_QUESTIONS: tuple[str, ...] = ("Q-001", "Q-002", "Q-003")

# 2026-11-15: the pair a reader is handed is the maximum of
# ``posterior_a * posterior_b * (uncertainty_a + uncertainty_b)``.  That product
# never asks whether the two hypotheses contradict each other, so a session was
# handed two orthogonal hypotheses as 「最優先対立対」, scored them, and the score
# went *up* (0.2259 -> 0.2951) because ``supports`` has no downward term --
# while the genuinely competing parent/child pairs fell 73%.  Measured in
# readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md
# sections 4.1-4.5.  The arithmetic is not changed here (every posterior in the
# ledger was produced by it); the pair is now reported with what *is* known
# about it: the recorded lineage relation, and whether either side has ever been
# examined by anything other than ``supports``.
PAIR_RELATION_LABELS: dict[str, str] = {
    "parent_child_left_is_parent": "親子（左が親）",
    "parent_child_right_is_parent": "親子（右が親）",
    "sibling": "同親の兄弟",
    "unrelated": "系譜関係なし",
}
PAIR_EIG_FORMULA = "posterior_left × posterior_right × (uncertainty_left + uncertainty_right)"

# One constant, two call sites, because they disagreed.  `compute_belief_state`
# advertised 2.0 for a core question with no hypotheses while
# `select_auto_question_id` scored the same question as 2.50 + jitter, so a
# reader of `--json` ranked it below the tool that actually assigns it.  Both
# now read this, so they cannot drift apart again.
HYPOTHESIS_LESS_CORE_PRIORITY = 2.50

# Provisional heuristic, not an empirically calibrated evidence weight. Counting
# named comparisons as independent sources overstates repeated mentions; this
# bounded-rate term uses the requested raw count with diminishing increments.
COMPARISON_TOUCH_WEIGHT = 0.5

# 2026-11-18 (Three-Gates architecture, Gate 2 + Gate 3):
# Receiver-gated posterior basis ``P_gate`` (computed alongside historical ``P``,
# ``P_sep``, and ``P_lin`` without moving any historical posterior):
#   1. Reality-monitoring PSC weighting (Garrison et al. 2015): scales
#      ``primary_source_collision`` by effective material verification status.
#   2. Chronological & non-rival heir transfer: blocks retroactive fallback credit
#      into children minted on days strictly later than the evaluation day and
#      blocks fallback credit into hypotheses the row itself named as opponents.
#   3. Pair-level repetition discount + provisional self-support discount (0.50).
#   4. Receiver-local suppression for live ``weight_effect: "suppress_retrieval"``
#      errata targeting a hypothesis.
PSC_GATED_WEIGHTS: dict[str, float] = {
    "all_verified": 1.20,
    "mixed_verified": 0.95,
    "zero_verified": 0.60,
    "no_materials": 0.55,
}
SELF_SUPPORT_GATED_DISCOUNT = 0.50
# 2026-11-20 (NOTE-20261120-058297 §2): across N=740 evaluations, same-session
# evaluations on depth>=1 child hypotheses had a 2.9% critique rate (1/34; 0/18
# on verified materials) even when sessions carried explicit bias warnings,
# whereas cross-session depth>=1 evaluations had a 64.0% critique rate (72.4% on
# verified materials). Same-session `supports` on a newly minted depth>=1 child
# is therefore a registration declaration rather than an independent test, and
# carries 0.0 weight under P_gate until an external session audits the child.
SELF_SUPPORT_DEPTH1_GATED_DISCOUNT = 0.0
# 2026-11-20 (④ of the evidence-accounting change): a `supports` row earns the
# full weight of its cited materials only to the extent that those materials
# were text-checked.  Measured on this archive before the change: 160/260
# (61.5%) of `supports` rows with materials cited ZERO verified material, while
# `narrows_scope` rows did so 46.1% of the time -- critique and support were
# resting on the same depth of reading.  A row backed entirely by
# partially_verified sources now keeps half its weight; a row backed entirely by
# verified ones keeps all of it:
#     factor = SUPPORT_DEPTH_FLOOR + (1 - SUPPORT_DEPTH_FLOOR) * r
# where r is the share of the row's cited materials whose effective
# verification.status is "verified".  Rows citing no material at all are left
# alone: they are proposition-level audits (or reproducible scripts), and their
# backing is a different question from whether a passage was read.
SUPPORT_DEPTH_FLOOR = 0.50
SUPPRESS_RETRIEVAL_HYP_PENALTY = 1.20
INHIBITION_STATE_LABELS: dict[str, str] = {
    "refuted_inhibited": "棄却・抑制",
    "superseded_inhibited": "継承済・抑制",
    "orphan_over_narrowed": "過限定・子仮説未分化",
    "self_only_provisional": "暫定（未検証/自己評価のみ）",
    "contested_active": "競合中（反証系あり）",
    "active": "稼働中",
}
_REC_ISO_DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
_REC_ID_DAY_RE = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-(\d{4})(\d{2})(\d{2})-")


def _record_iso_day(record: dict[str, Any], fallback_id: str = "") -> str:
    """Best-effort YYYY-MM-DD day stamp from ``created_at`` or ID prefix."""
    created = str(record.get("created_at") or "").strip()
    m = _REC_ISO_DAY_RE.match(created)
    if m:
        return m.group(1)
    im = _REC_ID_DAY_RE.match(fallback_id)
    if im:
        return f"{im.group(1)}-{im.group(2)}-{im.group(3)}"
    return ""


def _derive_inhibition_state(
    entry: dict[str, Any],
    *,
    gated_log_odds: float,
    retrieval_suppressed: bool,
) -> str:
    """Classify a hypothesis's receiver-local inhibitory status (Gate 2)."""
    eff = entry.get("effective_status")
    vc = entry.get("verdict_counts") or {}
    nar = int(vc.get("narrows_scope", 0))
    sup = int(vc.get("supports", 0))
    ref = int(vc.get("refutes_unconditioned", 0))
    children = entry.get("children_hypothesis_ids") or []
    if eff == "refuted" or retrieval_suppressed:
        return "refuted_inhibited"
    if eff in ("superseded", "subsumed"):
        return "superseded_inhibited"
    if nar >= 3 and nar > sup and gated_log_odds <= 0.0:
        return "superseded_inhibited" if children else "orphan_over_narrowed"
    if entry.get("direct_eval_count", 0) == 0 or entry.get("self_evaluated_only"):
        return "self_only_provisional"
    if (nar + ref) > 0 or eff == "narrowed":
        return "contested_active"
    return "active"


def pair_lineage_relation(ha: dict[str, Any], hb: dict[str, Any]) -> str:
    """Classify a pair by the lineage the ledger records, not by its meaning.

    Only ``parent_hypothesis_ids`` is consulted.  Whether two propositions
    actually contradict each other is not decidable from the ledger, and this
    function does not pretend otherwise -- ``unrelated`` means "no recorded
    lineage edge", which is what made an orthogonal pair look like a contest.
    """
    a, b = ha["hypothesis_id"], hb["hypothesis_id"]
    a_parents = set(ha.get("parent_hypothesis_ids") or [])
    b_parents = set(hb.get("parent_hypothesis_ids") or [])
    if b in a_parents:
        return "parent_child_right_is_parent"
    if a in b_parents:
        return "parent_child_left_is_parent"
    if a_parents and b_parents and (a_parents & b_parents):
        return "sibling"
    return "unrelated"


def pair_examined_only_by_supports(ha: dict[str, Any], hb: dict[str, Any]) -> bool:
    """True when neither side has ever been touched by a non-``supports`` verdict.

    This is the ratchet condition: ``supports`` adds ``delta`` to the target and
    subtracts ``0.20 * delta`` from each compared hypothesis, and nothing in the
    verdict arithmetic lowers a hypothesis that is only ever supported.  Scoring
    such a pair again raises its own EIG (measured: +30.6%).
    """
    for h in (ha, hb):
        if h.get("adversarial_eval_count"):
            return False
        verdicts = set(h.get("verdict_counts") or {})
        if verdicts and not verdicts <= {"supports"}:
            return False
    return True


# Combined posterior mass threshold below which a top competing pair remains
# unsaturated and vulnerable to the mutual-`supports` EIG ratchet even after
# both sides have received adversarial verdicts.
# Measured 2026-11-16 (readings/2026-11-16-what-crosses-the-unheld-interval.md §2.2):
#   - `pair_examined_only_by_supports` fired on 0/221 live pairs;
#   - yet mutual `supports` inflated EIG on unsaturated pairs:
#     Q-003 (67.4% mass): +109.5% live in PR #830 (+50.6% counterfactual);
#     Q-001 (86.7% mass): +17.0%;
#   - and reversed only on saturated Q-002 (98.6% mass): -5.8%.
UNSATURATED_PAIR_MASS_THRESHOLD = 0.90

# Minimum posterior mass at which a single independent witnessing session
# (`witness_eval_session_count <= 1`) is flagged as a single-witness illusion
# (readings/2026-11-16-what-crosses-the-unheld-interval.md §5.2, §7-3).
LOW_WITNESS_POSTERIOR_THRESHOLD = 0.05

# Shared mechanical-backfill marker used by tools/witness_count.py so
# hand-written read_log witnesses exclude mechanical context backfills.
MECHANICAL_READ_LOG_MARK = "バックフィル"


def pair_mass_sum(ha: dict[str, Any], hb: dict[str, Any]) -> float:
    """Return the combined posterior mass of a candidate pair (rounded to 4 dp)."""
    return round(float(ha.get("posterior", 0.0)) + float(hb.get("posterior", 0.0)), 4)


def pair_has_unsaturated_supports_ratchet(
    ha: dict[str, Any],
    hb: dict[str, Any],
    *,
    threshold: float = UNSATURATED_PAIR_MASS_THRESHOLD,
) -> bool:
    """True when a pair's combined posterior mass leaves room for EIG inflation.

    When ``p_a + p_b < threshold``, adding ``supports`` to both sides drains
    mass from the remaining hypotheses and can inflate ``p_a * p_b * (u_a + u_b)``
    even if both sides already have adversarial verdicts.
    """
    combined = round(float(ha.get("posterior", 0.0)) + float(hb.get("posterior", 0.0)), 6)
    return combined < threshold


def classify_evaluation_verification(
    evl: dict[str, Any],
    materials: dict[str, dict[str, Any]],
) -> str:
    """Classify an evaluation's material-verification backing (audit only).

    Does not alter historical log-odds weights. Returns one of:
    - ``script_verified``: reproducible_script with non-empty script_command
    - ``all_verified``: cites >=1 material and every cited material has verification.status == "verified"
    - ``mixed_verified``: cites >=2 materials, some verified and some not
    - ``zero_verified``: cites >=1 material and none has verification.status == "verified"
    - ``no_materials``: non-script evaluation citing no material_ids
    """
    if evl.get("evidence_type") == "reproducible_script" and (evl.get("script_command") or "").strip():
        return "script_verified"
    mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
    if not mids:
        return "no_materials"
    verified_count = sum(
        1
        for mid in mids
        if ((materials.get(mid) or {}).get("verification") or {}).get("status") == "verified"
    )
    if verified_count == len(mids):
        return "all_verified"
    if verified_count > 0:
        return "mixed_verified"
    return "zero_verified"


def support_verified_ratio(
    evl: dict[str, Any],
    materials: dict[str, dict[str, Any]],
) -> float | None:
    """Share of an evaluation's cited materials that were text-checked.

    Returns ``None`` when the row cites no material (proposition-level audit or
    a reproducible script): those rows are not making a claim about a passage,
    so the question "how much of this support rests on a checked text?" has no
    answer for them and must not be silently answered as 0.0.

    The ratio uses the *effective* verification status, i.e. after any
    editorial_decisions overlay has been applied by ``tools/ledger_io.py``, so a
    material upgraded this session counts as verified for every earlier row that
    cited it.  That is deliberate: the mass a row contributed is re-read in the
    light of what is now known, which is the same convention the PSC weights use.
    """
    mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
    if not mids:
        return None
    verified = sum(
        1
        for mid in mids
        if ((materials.get(mid) or {}).get("verification") or {}).get("status") == "verified"
    )
    return verified / len(mids)


def hypothesis_read_witnesses(
    read_log: dict[str, dict[str, Any]] | list[dict[str, Any]] | None,
) -> dict[str, set[str]]:
    """Return distinct sessions with a hand-written read_log entry per hypothesis.

    Excludes rows whose note contains ``MECHANICAL_READ_LOG_MARK`` (mechanical
    context backfills), matching ``tools/witness_count.py``.
    """
    out: dict[str, set[str]] = defaultdict(set)
    if not read_log:
        return out
    rows = read_log.values() if isinstance(read_log, dict) else read_log
    for row in rows:
        if not isinstance(row, dict):
            continue
        target = row.get("target")
        if not isinstance(target, dict) or target.get("type") != "hypothesis":
            continue
        if MECHANICAL_READ_LOG_MARK in (row.get("note") or ""):
            continue
        hid = target.get("id")
        sid = row.get("session_id")
        if isinstance(hid, str) and hid and isinstance(sid, str) and sid:
            out[hid].add(sid)
    return out

# A core question whose best competing pair carries less than this much expected
# information gain has nothing left for the selector to pick: the posterior is
# concentrated enough that another reading would not move it.
# 2026-11-15: Q-001 0.0067 and Q-002 0.0000 (Q-003 0.2259) were already under
# this line. The threshold gates *selection*, not belief: it never changes a
# posterior, and it never forbids adding a hypothesis. It only says what to do
# next when the distribution has stopped choosing.
SATURATION_EIG_THRESHOLD = 0.02

EVIDENCE_WEIGHTS: dict[str, float] = {
    "reproducible_script": 1.35,
    "primary_source_collision": 1.20,
    "cross_session_audit": 1.00,
    "fragment_thought_experiment": 0.55,
}

ROLES: tuple[str, ...] = ("proposer", "adversarial_tester", "consolidator")
ROLE_LABELS_JA: dict[str, str] = {
    "proposer": "Proposer（条件付き仮説提案・分割）",
    "adversarial_tester": "Adversarial Tester（反証・境界衝突テスト）",
    "consolidator": "Consolidator（評価統合・系譜整理）",
}


def load_belief_ledgers(root: Path = ROOT) -> dict[str, dict[str, dict[str, Any]]]:
    """Load questions, hypotheses, evaluations, notes, materials, fragments, sessions, errata, and hypothesis read_log."""
    root = Path(root)
    specs = {
        "questions": (root / "state" / "questions.jsonl", "question_id"),
        "materials": (root / "state" / "materials.jsonl", "material_id"),
        "fragments": (root / "state" / "fragments.jsonl", "fragment_id"),
        "sessions": (root / "state" / "sessions.jsonl", "session_id"),
        "notes": (root / "state" / "notes.jsonl", "note_id"),
    }
    optional = {
        "hypotheses": (root / "state" / "hypotheses.jsonl", "hypothesis_id"),
        "evaluations": (root / "state" / "evaluations.jsonl", "evaluation_id"),
        "errata": (root / "state" / "errata.jsonl", "errata_id"),
    }
    for name, (base, id_key) in optional.items():
        if base.exists() or ledger_io.shard_dir(base).is_dir():
            specs[name] = (base, id_key)

    cols, errors = ledger_io.load_collections(specs, root=root)
    if errors:
        raise ValueError("ledger errors:\n  - " + "\n  - ".join(errors[:10]))
    for name in optional:
        cols.setdefault(name, {})

    # Keep only hypothesis-targeted read_log rows so deepcopy callers (e.g.
    # boundary_channel_probe, lineage_credit_accounting) stay fast while
    # compute_belief_state still gets exact hand-written hypothesis witnesses.
    read_log_base = root / "state" / "read_log.jsonl"
    if read_log_base.exists() or ledger_io.shard_dir(read_log_base).is_dir():
        rl_cols, rl_errors = ledger_io.load_collections(
            {"read_log": (read_log_base, "read_id")}, root=root
        )
        if rl_errors:
            raise ValueError("ledger errors:\n  - " + "\n  - ".join(rl_errors[:10]))
        cols["hypothesis_read_log"] = {
            rid: rec
            for rid, rec in rl_cols.get("read_log", {}).items()
            if isinstance(rec.get("target"), dict)
            and rec["target"].get("type") == "hypothesis"
        }
    else:
        cols["hypothesis_read_log"] = {}
    return cols


def errata_is_live_correction(rec: dict[str, Any]) -> bool:
    """True when a correction still asserts an unresolved error.

    The weight penalty must not be paid by a hypothesis whose correction was
    withdrawn, nor by one where the check ran and the claim HELD (no error was
    found), nor by one that could not be measured at all. Visibility is a
    separate question: ``errata_flags`` still lists every row, because knowing
    that a claim was checked -- or that a correction was retracted -- is useful
    to the next reader. Only the weight is gated here.

    Before this was added, ``log_odds[hid] -= 0.60 * len(direct_errs)`` counted
    every row carrying an ``errata_id``, so a retracted correction and a
    correction recording "the claim held" cost exactly as much as a live one
    (measured: -0.6000 for all nine verdict x status combinations). That defect
    was filed as ERR-20261114-9a6fb1 and is what this function closes.

    ``status`` values outside the schema enum are treated as live rather than
    silently discounted: two legacy rows carry ``corrected``, and an unknown
    label must not become a way to escape the penalty.
    """
    if rec.get("status") == "withdrawn":
        return False
    return rec.get("verdict") == "contradicted"


def _errata_claim_key(rec: dict[str, Any]) -> str:
    """Normalised claim text, for collapsing exact restatements of one claim."""
    text = unicodedata.normalize("NFKC", str(rec.get("claim") or ""))
    return re.sub(r"\s+", " ", text).strip()


def distinct_errata_claims(
    recs: list[dict[str, Any]], all_errata: dict[str, dict[str, Any]] | None = None
) -> list[list[dict[str, Any]]]:
    """Group rows that assert one claim, so one claim costs one penalty.

    ``log_odds[hid] -= 0.60 * len(direct_errs)`` used to charge per *row*. The same
    claim filed twice -- which happens when concurrent sessions each measure the
    same defect, as ``ERR-20261107-100f65`` and ``ERR-20261107-259d5f`` do for
    ``tools/size_budget.py`` -- therefore cost twice, and a claim could be weighted
    down by copying it. The row count measured how many times someone wrote, not
    how many independent checks the addressee failed. This is the errata analogue
    of the asymmetry recorded in
    ``readings/2026-11-14-two-hypotheses-that-were-not-competing.md`` §6-1, where
    splitting one finding into two evaluation rows doubled its effect.

    Two rows are one claim when either:

    * they share an addressee and their claim text is equal after NFKC and
      whitespace normalisation (an exact repeat needs no declaration), or
    * one declares the other in ``duplicate_of`` (a reworded restatement).

    The second path is explicit because the engine cannot decide whether two
    differently-worded Japanese claims are the same claim. Fuzzy matching would
    merge the three *distinct* Blodgett corrections on one material
    (``ERR-20261107-ed8184`` / ``-4ee0ec`` / ``-3aca22``), which must keep costing
    three. Guessing is therefore not attempted; the writer declares, and the
    declaration is auditable in the ledger.

    Grouping is by union so a chain A <- B <- C collapses to one group. Rows are
    grouped per addressee, never across addressees: the same sentence filed
    against two different hypotheses is two claims about two subjects.
    """
    parent: dict[int, int] = {}

    def find(i: int) -> int:
        parent.setdefault(i, i)
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    by_id: dict[str, int] = {}
    for i, rec in enumerate(recs):
        find(i)
        eid = rec.get("errata_id")
        if isinstance(eid, str):
            by_id[eid] = i

    seen_text: dict[str, int] = {}
    for i, rec in enumerate(recs):
        key = _errata_claim_key(rec)
        if key:
            if key in seen_text:
                union(seen_text[key], i)
            else:
                seen_text[key] = i

    # A declaration may name a row addressed elsewhere in the ledger; resolve it
    # only when that row is part of this addressee's group, so a declaration
    # cannot pull an unrelated addressee's rows into this penalty.
    for i, rec in enumerate(recs):
        for other in rec.get("duplicate_of") or []:
            if isinstance(other, str) and other in by_id:
                union(by_id[other], i)

    groups: dict[int, list[dict[str, Any]]] = {}
    for i, rec in enumerate(recs):
        groups.setdefault(find(i), []).append(rec)
    return [groups[k] for k in sorted(groups)]


def build_errata_index(errata: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Map any target ID or repo path -> list of errata records targeting it (1-hop).

    Address fields (``subject_id``, ``fragment_id``, ``target.id``) are authoritative.
    The prose location fields (``claim_location``, ``where``, ``location``) say
    *where a claim was written*, not *what the correction is addressed to*, so they
    are consulted only as a fallback for rows that carry no address at all.

    They used to be indexed unconditionally, which let a correction addressed to a
    tool penalise a hypothesis merely because its ``claim_location`` happened to be
    that hypothesis's ID. ``subject_type`` is deliberately still not read here:
    ledger IDs and repo paths are self-identifying, and routing on the declared
    label would let a mislabelled row escape its own address. The label is checked
    for consistency by ``validate_seed.py`` instead.
    """
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for _eid, rec in sorted(errata.items()):
        keys: list[str] = []
        target = rec.get("target")
        if isinstance(target, dict) and isinstance(target.get("id"), str):
            keys.append(target["id"])
        for kname in ("subject_id", "fragment_id"):
            val = rec.get(kname)
            if isinstance(val, str) and val:
                keys.append(val)
        if not keys:
            # No explicit address: fall back to the prose location so that older
            # rows written before subject_id existed stay reachable.
            for loc_key in ("claim_location", "where", "location"):
                loc = rec.get(loc_key)
                if isinstance(loc, str) and loc:
                    keys.append(loc)
                    head = loc.split(":", 1)[0].split("#", 1)[0].strip()
                    if head:
                        keys.append(head)
        for k in keys:
            if rec not in by_target[k]:
                by_target[k].append(rec)
    return dict(by_target)


def _generation_depths(hypotheses: dict[str, dict[str, Any]]) -> dict[str, int]:
    depths: dict[str, int] = {}

    def depth_of(hid: str, visiting: set[str]) -> int:
        if hid in depths:
            return depths[hid]
        if hid in visiting or hid not in hypotheses:
            return 0
        parents = [
            p for p in (hypotheses[hid].get("parent_hypothesis_ids") or [])
            if isinstance(p, str) and p in hypotheses and p != hid
        ]
        if not parents:
            depths[hid] = 0
            return 0
        visiting.add(hid)
        d = 1 + max(depth_of(p, visiting) for p in parents)
        visiting.remove(hid)
        depths[hid] = d
        return d

    for hid in hypotheses:
        depth_of(hid, set())
    return depths


def assign_session_role(
    seed: str | None = None,
    question_summary: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Deterministically assign one of the 3 inquiry roles (25% proposer, 50% tester, 25% consolidator)."""
    if question_summary:
        active = [h for h in question_summary.get("hypotheses", []) if h["effective_status"] == "active"]
        if not active:
            return {
                "role": "proposer",
                "label": ROLE_LABELS_JA["proposer"],
                "prompt": "prompts/role_proposer.md",
                "reason": "当該問いに有効な条件付き仮説が未登録のため、競合仮説の定式化を優先する。",
            }
        dominant_untested = [
            h for h in active
            if h["posterior"] >= 0.45 and h["adversarial_eval_count"] == 0
        ]
        if dominant_untested and not seed:
            return {
                "role": "adversarial_tester",
                "label": ROLE_LABELS_JA["adversarial_tester"],
                "prompt": "prompts/role_adversarial_tester.md",
                "reason": f"優勢仮説 {dominant_untested[0]['hypothesis_id']} に反証・限定テストが未実施のため、境界検証を優先する。",
            }

    token = seed or "default"
    bucket = int(hashlib.sha256(f"role:{token}".encode("utf-8")).hexdigest()[:8], 16) % 4
    if bucket == 0:
        role = "proposer"
        reason = "シード割当（25%枠）：既存仮説の盲点または境界領域に対し、排他条件付きの新たな条件付き仮説を1〜2件提案・分割する。"
    elif bucket in (1, 2):
        role = "adversarial_tester"
        reason = "シード割当（50%枠）：新規仮説の乱立を抑え、事後確率上位の競合仮説ペアに対して反証・射程限定テストを実行する。"
    else:
        role = "consolidator"
        reason = "シード割当（25%枠）：散在する精読ノート主張・評価イベントを整理し、重複仮説の統合(synthesizes/subsumes)と台帳配線を行う。"
    return {
        "role": role,
        "label": ROLE_LABELS_JA[role],
        "prompt": f"prompts/role_{role}.md",
        "reason": reason,
    }


def compute_belief_state(
    data: dict[str, dict[str, dict[str, Any]]] | None = None,
    *,
    root: Path = ROOT,
    pair_level_repeat: bool = False,
    heir_credit: bool = True,
    narrowing_partner_share: bool = False,
    receiver_gated: bool = False,
) -> dict[str, Any]:
    """Compute posterior distributions, uncertainties, lineage shifts, and next-tests.

    ``pair_level_repeat`` selects the *basis* for the repetition discount:

    - ``False`` (default, historical): ``repeat_key = (target, verdict, session)``.
      Repeating the same target/verdict from another session pays full weight.
    - ``True``: ``repeat_key = (target, verdict, comparison set)``. The pair, not
      the session, is the unit, so ten sessions separating the same pair in the
      same direction pay ``1/sqrt(10)`` in total.

    The default is unchanged so that every historical posterior stays
    reproducible. ``BELIEF_MAP.md`` shows both bases side by side
    (``P`` and ``P_sep``); the gap between them is the repetition effect
    measured in ``readings/2026-11-16-stable-words-do-not-make-progress.md`` §3.

    ``heir_credit`` (added 2026-11-17, default ``True`` = present arithmetic)
    controls the third of three write-side readings of a single field. A row
    that narrows or refutes a hypothesis pays its children a boost
    (``0.75*delta`` / ``0.95*delta`` divided by the number of children, and
    ``0.80*delta`` to the parents under ``subsumes``). When a row names no
    ``spawned_hypothesis_ids`` and no ``scope_inherited_by_hypothesis_ids``,
    the engine falls back to every hypothesis whose
    ``parent_hypothesis_ids`` contains the target. ``False`` drops that
    fallback, keeping only names the row itself wrote.

    This exists because ``compared_against_hypothesis_ids`` and the lineage
    fallback intersect: 34 rows name as their comparison partner a hypothesis
    that is, by lineage, their target's child. In those rows the field means
    "this was my opponent" and simultaneously triggers "this is my heir", so
    naming an opponent *raises* it. ``heir_credit=False`` is the only way to
    separate the two readings without editing rows
    (readings/2026-11-17-the-prose-is-right-and-the-mechanism-is-wrong.md §4).

    ``narrowing_partner_share`` (added 2026-11-18, default ``False`` = present
    arithmetic) is a second knob of the same kind. At present only the
    ``supports`` branch deducts the hypotheses this row named; a
    ``narrows_scope`` row reads its partner list solely as a switch that lifts
    the 0.65 discount. ``True`` applies the same ``0.20 * delta / len(compared)``
    deduction to a narrowing row, using the same ``delta`` the target is charged
    with.

    It exists so the question "should narrowing deduct its partners?" can be
    measured rather than argued. **It is not a proposal**: the two answers move
    different rows in opposite directions, and this session's report
    (readings/2026-11-18-the-three-debts-and-the-one-that-bends.md §3) records
    the measurement and leaves the decision to editorial_review.
    """
    cols = data if data is not None else load_belief_ledgers(root)
    questions = cols.get("questions", {})
    hypotheses = cols.get("hypotheses", {})
    evaluations = cols.get("evaluations", {})
    materials = cols.get("materials") or {}
    read_log_source = (
        cols["read_log"] if "read_log" in cols else cols.get("hypothesis_read_log", {})
    )
    read_witnesses_by_hyp = hypothesis_read_witnesses(read_log_source)
    errata = cols.get("errata")
    if errata is None:
        errata_base = Path(root) / "state" / "errata.jsonl"
        if errata_base.exists() or ledger_io.shard_dir(errata_base).is_dir():
            sub_cols, _ = ledger_io.load_collections({"errata": (errata_base, "errata_id")}, root=Path(root))
            errata = sub_cols.get("errata", {})
        else:
            errata = {}

    psc_global_counts: Counter[str] = Counter()
    for evl in evaluations.values():
        if evl.get("evidence_type") == "primary_source_collision":
            psc_global_counts[classify_evaluation_verification(evl, materials)] += 1
    psc_global_total = sum(psc_global_counts.values())
    provenance_verification = {
        "psc_total": psc_global_total,
        "psc_all_verified": psc_global_counts["all_verified"],
        "psc_mixed_verified": psc_global_counts["mixed_verified"],
        "psc_zero_verified": psc_global_counts["zero_verified"],
        "psc_no_materials": psc_global_counts["no_materials"],
        "psc_all_verified_ratio": (
            round(psc_global_counts["all_verified"] / psc_global_total, 4)
            if psc_global_total
            else 0.0
        ),
    }

    errata_by_target = build_errata_index(errata)
    depths = _generation_depths(hypotheses)

    # 2026-11-16 (P-6): a correction can name an evaluation row as its subject.
    # Until now such a correction only raised a flag on the hypothesis, so
    # correcting one's own over-claim punished the hypothesis the row supported
    # (readings/2026-11-16-one-row-outweighs-ten-sources.md §3-4). A record that
    # says ``weight_effect: "void_row"`` withdraws that row's weight instead.
    # No historical record carries the field, so no historical posterior moves.
    voided_evaluation_ids: set[str] = set()
    suppressed_hypothesis_ids: set[str] = set()
    for erec in errata.values():
        weff = erec.get("weight_effect")
        if weff == "void_row" and erec.get("subject_type") == "evaluation":
            if errata_is_live_correction(erec):
                subject = erec.get("subject_id")
                if isinstance(subject, str) and subject:
                    voided_evaluation_ids.add(subject)
        elif weff == "suppress_retrieval" and erec.get("subject_type") == "hypothesis":
            if errata_is_live_correction(erec):
                subject = erec.get("subject_id")
                if isinstance(subject, str) and subject:
                    suppressed_hypothesis_ids.add(subject)
    voided_evaluations: list[dict[str, str]] = []

    children_by_parent: dict[str, list[str]] = defaultdict(list)
    q_to_hyps: dict[str, list[str]] = defaultdict(list)
    hyp_iso_days: dict[str, str] = {}
    for hid, hyp in sorted(hypotheses.items()):
        hyp_iso_days[hid] = _record_iso_day(hyp, hid)
        for pid in hyp.get("parent_hypothesis_ids") or []:
            if isinstance(pid, str) and pid in hypotheses:
                children_by_parent[pid].append(hid)
        for qid in hyp.get("question_ids") or []:
            if isinstance(qid, str):
                q_to_hyps[qid].append(hid)

    # Accumulate log-odds across all hypotheses
    log_odds: dict[str, float] = {hid: 0.0 for hid in hypotheses}
    # Slight status baseline for initial registration state before evaluations
    for hid, hyp in hypotheses.items():
        init_status = hyp.get("status", "active")
        if init_status == "refuted":
            log_odds[hid] -= 0.80
        elif init_status == "narrowed":
            log_odds[hid] -= 0.35
        elif init_status == "superseded":
            log_odds[hid] -= 0.60
        if receiver_gated and hid in suppressed_hypothesis_ids:
            log_odds[hid] -= SUPPRESS_RETRIEVAL_HYP_PENALTY

    evals_by_hyp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    compared_touches: Counter[str] = Counter()
    adversarial_touches: Counter[str] = Counter()
    postdated_heir_transfers: Counter[str] = Counter()
    rival_heir_transfers: Counter[str] = Counter()
    repeat_tracker: Counter[tuple[str, str, str]] = Counter()
    indep_sources: dict[str, set[str]] = defaultdict(set)
    separation_partners: dict[str, set[str]] = defaultdict(set)
    separation_first_seen: dict[tuple[str, tuple[str, ...]], str] = {}
    last_new_separation: dict[str, str] = {}
    novelty_total = 0
    novelty_new = 0

    for evl_id, evl in sorted(evaluations.items()):
        target_id = evl.get("target_hypothesis_id")
        if not isinstance(target_id, str) or target_id not in hypotheses:
            continue
        verdict = str(evl.get("verdict") or "supports")
        ev_type = str(evl.get("evidence_type") or "cross_session_audit")
        if receiver_gated and ev_type == "primary_source_collision":
            vcls = classify_evaluation_verification(evl, materials)
            base_w = PSC_GATED_WEIGHTS.get(vcls, EVIDENCE_WEIGHTS["primary_source_collision"])
        else:
            base_w = EVIDENCE_WEIGHTS.get(ev_type, 1.0)

        if evl_id in voided_evaluation_ids:
            # The row stays visible in counts and flags; only its weight is
            # withdrawn. It must not discount (or be discounted by) sibling rows.
            evals_by_hyp[target_id].append(evl)
            voided_evaluations.append(
                {"evaluation_id": evl_id, "target_hypothesis_id": target_id}
            )
            continue

        sid = str(evl.get("session_id") or "")
        mat_sig = ",".join(sorted(evl.get("material_ids") or []))
        source_key = mat_sig or ",".join(sorted(evl.get("note_ids") or [])) or evl_id
        compared_key = ",".join(
            sorted(c for c in (evl.get("compared_against_hypothesis_ids") or []) if isinstance(c, str))
        )
        if pair_level_repeat or receiver_gated:
            repeat_key = (target_id, verdict, compared_key or sid or source_key)
        else:
            repeat_key = (target_id, verdict, sid or source_key)
        repeat_tracker[repeat_key] += 1
        k_rep = repeat_tracker[repeat_key]
        indep_discount = 1.0 / math.sqrt(k_rep)

        compared = [
            cid for cid in (evl.get("compared_against_hypothesis_ids") or [])
            if isinstance(cid, str) and cid in hypotheses and cid != target_id
        ]
        comp_factor = 1.0 if compared else 0.65
        self_factor = 1.0
        if receiver_gated and verdict == "supports":
            hyp_sid = str(hypotheses[target_id].get("session_id") or "")
            if sid and hyp_sid and sid == hyp_sid:
                if depths.get(target_id, 0) >= 1:
                    self_factor = SELF_SUPPORT_DEPTH1_GATED_DISCOUNT
                else:
                    self_factor = SELF_SUPPORT_GATED_DISCOUNT
        depth_factor = 1.0
        if receiver_gated and verdict == "supports":
            ratio = support_verified_ratio(evl, materials)
            if ratio is not None:
                depth_factor = SUPPORT_DEPTH_FLOOR + (1.0 - SUPPORT_DEPTH_FLOOR) * ratio
        delta = base_w * indep_discount * comp_factor * self_factor * depth_factor

        evals_by_hyp[target_id].append(evl)
        indep_sources[target_id].add(f"{ev_type}:{source_key}")
        for cid in compared:
            compared_touches[cid] += 1

        spawned = [
            shid for shid in (evl.get("spawned_hypothesis_ids") or [])
            if isinstance(shid, str) and shid in hypotheses and shid != target_id
        ]
        # 2026-11-16 (P-5): ``spawned_hypothesis_ids`` means "hypotheses this row
        # created". Narrowing a child so that its *parent* inherits the remaining
        # scope is a different operation, and naming the parent in ``spawned``
        # made a field whose name says "created" pay the parent 0.75*delta
        # (readings/2026-11-16-the-two-rows-that-funded-the-leader.md §5: one
        # such naming was worth 22.12 pp of the Q-003 leader). The new field
        # names the operation; the union keeps existing rows working.
        for shid in evl.get("scope_inherited_by_hypothesis_ids") or []:
            if isinstance(shid, str) and shid in hypotheses and shid != target_id and shid not in spawned:
                spawned.append(shid)
        evl_day = _record_iso_day(evl, evl_id)
        if not spawned and heir_credit:
            raw_children = children_by_parent.get(target_id, [])
            compared_set = set(compared)

            def _is_postdated_fallback(ch_id: str) -> bool:
                c_day = hyp_iso_days.get(ch_id, "")
                if not (evl_day and c_day):
                    return False
                if c_day > evl_day:
                    return True
                if c_day == evl_day:
                    c_sid = str(hypotheses[ch_id].get("session_id") or "")
                    # Same-day cross-session fallback without explicit naming cannot
                    # prove the child existed when the evaluator wrote the row.
                    return bool(sid and c_sid and sid != c_sid)
                return False

            if verdict in ("narrows_scope", "refutes_unconditioned"):
                for ch in raw_children:
                    if _is_postdated_fallback(ch):
                        postdated_heir_transfers[ch] += 1
                    if ch in compared_set:
                        rival_heir_transfers[ch] += 1
            if receiver_gated:
                # Gate 2: fallback scope inheritance flows only to children that
                # already existed before the evaluation (strict prior day, or
                # same-day same-session) AND were not named as compared_against rivals.
                spawned = [
                    ch
                    for ch in raw_children
                    if ch not in compared_set and not _is_postdated_fallback(ch)
                ]
            else:
                spawned = raw_children

        # Separation bookkeeping for the audit columns (never changes weights).
        if target_id not in separation_partners:
            separation_partners[target_id] = set()
        for cid in compared:
            separation_partners[target_id].add(cid)
            separation_partners.setdefault(cid, set()).add(target_id)
        sig = (target_id, tuple(sorted(compared)))
        day = str(evl.get("created_at") or "")[:10]
        novelty_total += 1
        if sig not in separation_first_seen:
            separation_first_seen[sig] = day
            novelty_new += 1
        for hid_in_pair in (target_id, *compared):
            prior_day = last_new_separation.get(hid_in_pair, "")
            if day > prior_day:
                last_new_separation[hid_in_pair] = day

        if verdict == "supports":
            log_odds[target_id] += delta
            if compared:
                share = (0.20 * delta) / len(compared)
                for cid in compared:
                    log_odds[cid] -= share
                    adversarial_touches[cid] += 1
        elif verdict == "narrows_scope":
            log_odds[target_id] -= 1.15 * delta
            adversarial_touches[target_id] += 1
            if narrowing_partner_share and compared:
                nshare = (0.20 * delta) / len(compared)
                for cid in compared:
                    log_odds[cid] -= nshare
                    adversarial_touches[cid] += 1
            if spawned:
                boost = (0.75 * delta) / len(spawned)
                for shid in spawned:
                    log_odds[shid] += boost
        elif verdict == "refutes_unconditioned":
            log_odds[target_id] -= 2.40 * delta
            adversarial_touches[target_id] += 1
            if spawned:
                boost = (0.95 * delta) / len(spawned)
                for shid in spawned:
                    log_odds[shid] += boost
        elif verdict == "subsumes":
            log_odds[target_id] += 0.85 * delta
            for pid in hypotheses[target_id].get("parent_hypothesis_ids") or []:
                if isinstance(pid, str) and pid in hypotheses:
                    log_odds[pid] -= 0.80 * delta
                    adversarial_touches[pid] += 1

    # 1-hop transitive errata check on hypotheses and their supporting materials/notes/evaluations
    hyp_errata: dict[str, list[str]] = defaultdict(list)
    for hid, hyp in hypotheses.items():
        direct_errs = [e["errata_id"] for e in errata_by_target.get(hid, []) if "errata_id" in e]
        ref_ids = (
            list(hyp.get("supporting_material_ids") or [])
            + list(hyp.get("source_note_ids") or [])
            + [e["evaluation_id"] for e in evals_by_hyp.get(hid, []) if e.get("verdict") == "supports"]
        )
        hop_errs: list[str] = []
        for rid in ref_ids:
            for erec in errata_by_target.get(rid, []):
                eid = erec.get("errata_id")
                if isinstance(eid, str) and eid not in direct_errs and eid not in hop_errs:
                    hop_errs.append(eid)
        # Only corrections that still assert an error cost weight. A withdrawn
        # correction, one whose check found the claim HELD, and one that could not
        # be measured stay visible in errata_flags but do not move the belief.
        # One claim costs one penalty, however many rows restate it. Rows are
        # grouped before the verdict/status gate so that a live correction and a
        # withdrawn restatement of the SAME claim collapse to one group, and the
        # group still costs because one member is live. Filtering first would let
        # a withdrawn duplicate silently split off and be counted separately.
        claim_groups = distinct_errata_claims(errata_by_target.get(hid, []))
        penalising = [
            g for g in claim_groups
            if any("errata_id" in e and errata_is_live_correction(e) for e in g)
        ]
        if penalising:
            log_odds[hid] -= 0.60 * len(penalising)
        all_flags = direct_errs + hop_errs
        if all_flags:
            hyp_errata[hid] = all_flags

    ordered_qids = list(CORE_QUESTIONS) + sorted(
        qid for qid in q_to_hyps if qid not in CORE_QUESTIONS
    )

    question_states: dict[str, dict[str, Any]] = {}
    for qid in ordered_qids:
        q_rec = questions.get(qid, {})
        hids = sorted(q_to_hyps.get(qid, []))
        n = len(hids)
        if n == 0:
            question_states[qid] = {
                "question_id": qid,
                "question": q_rec.get("question", ""),
                "hypothesis_count": 0,
                "active_count": 0,
                "entropy_bits": 0.0,
                "max_entropy_bits": 0.0,
                "kl_from_uniform_bits": 0.0,
                "gen0_mass": 0.0,
                "gen1_plus_mass": 0.0,
                "mean_active_uncertainty": 1.0,
                # 2026-11-15: this default disagreed with the selector.
                # `select_auto_question_id` never reads `priority_score` for a
                # question with no hypotheses -- it scores a hypothesis-less core
                # question as 2.50 + jitter -- so the state advertised 2.0 while
                # the selector used 2.50.  A reader of `--json` would have ranked
                # the question differently from the tool that actually assigns it.
                # Dormant today (all three core questions carry hypotheses), which
                # is exactly why it went unnoticed.  Aligned with the selector; no
                # assignment changes.
                "priority_score": HYPOTHESIS_LESS_CORE_PRIORITY,
                "top_competing_pair": None,
                "unexamined_active_hypothesis_ids": [],
                "awaiting_external_audit_ids": [],
                "hypotheses": [],
            }
            continue

        max_l = max(log_odds[h] for h in hids)
        exps = {h: math.exp(log_odds[h] - max_l) for h in hids}
        total_exp = sum(exps.values()) or 1.0
        posteriors = {h: exps[h] / total_exp for h in hids}
        uniform_p = 1.0 / n

        entropy = -sum(p * math.log2(max(p, 1e-12)) for p in posteriors.values())
        max_entropy = math.log2(n) if n > 1 else 0.0
        kl_bits = sum(
            p * math.log2(max(p, 1e-12) / uniform_p) for p in posteriors.values()
        )

        hyp_entries: list[dict[str, Any]] = []
        for hid in hids:
            hyp = hypotheses[hid]
            direct_evals = evals_by_hyp.get(hid, [])
            verdicts = Counter(str(e.get("verdict")) for e in direct_evals)
            init_st = str(hyp.get("status") or "active")
            if verdicts["refutes_unconditioned"] > 0 or init_st == "refuted":
                eff_status = "refuted"
            elif verdicts["narrows_scope"] > 0 and verdicts["supports"] == 0:
                eff_status = "narrowed"
            elif init_st in ("narrowed", "superseded") and verdicts["supports"] == 0:
                eff_status = init_st
            else:
                eff_status = "active"

            n_indep = len(indep_sources.get(hid, set()))
            adv_count = adversarial_touches[hid]
            raw_u = (1.0 / math.sqrt(1.0 + n_indep + COMPARISON_TOUCH_WEIGHT * math.log2(1 + compared_touches[hid]))) * (1.25 if adv_count == 0 else 1.0)
            uncertainty = round(min(1.0, max(0.05, raw_u)), 4)

            # Audit metrics (do not alter historical posterior arithmetic):
            # - material verification backing (NOTE-20261116-7d62c1 §3, §7-2)
            # - independent witnessing sessions & hand-written read_log (§5.2, §7-3)
            # - same-session vs cross-session evaluation split (§4)
            ver_classes = Counter(
                classify_evaluation_verification(e, materials) for e in direct_evals
            )
            verified_mat_count = ver_classes["all_verified"]
            script_eval_count = ver_classes["script_verified"]
            verified_direct_count = verified_mat_count + script_eval_count
            # 2026-11-20 (④): how much of this hypothesis's positive support rests
            # on text-checked sources.  Reported, not stored: it is derived from
            # the rows every time, so it cannot drift from the ledger.
            support_ratios = [
                r
                for r in (
                    support_verified_ratio(e, materials)
                    for e in direct_evals
                    if str(e.get("verdict") or "") == "supports"
                )
                if r is not None
            ]
            support_ratio_mean = (
                round(sum(support_ratios) / len(support_ratios), 4) if support_ratios else None
            )
            zero_verified_support_count = sum(1 for r in support_ratios if r == 0.0)
            fully_verified_support_count = sum(1 for r in support_ratios if r >= 1.0)
            psc_evals = [
                e for e in direct_evals if e.get("evidence_type") == "primary_source_collision"
            ]
            psc_classes = Counter(
                classify_evaluation_verification(e, materials) for e in psc_evals
            )
            eval_sessions = {
                e["session_id"]
                for e in direct_evals
                if isinstance(e.get("session_id"), str) and e["session_id"]
            }
            read_sessions = read_witnesses_by_hyp.get(hid, set())
            hyp_session = hyp.get("session_id")
            same_sess_count = sum(
                1
                for e in direct_evals
                if isinstance(hyp_session, str)
                and hyp_session
                and e.get("session_id") == hyp_session
            )
            cross_sess_count = sum(
                1
                for e in direct_evals
                if isinstance(hyp_session, str)
                and hyp_session
                and isinstance(e.get("session_id"), str)
                and e.get("session_id")
                and e.get("session_id") != hyp_session
            )
            rounded_posterior = round(posteriors[hid], 4)
            low_witness_high_mass = bool(
                rounded_posterior >= LOW_WITNESS_POSTERIOR_THRESHOLD
                and len(eval_sessions) <= 1
            )
            self_evaluated_only = bool(
                len(direct_evals) > 0 and same_sess_count > 0 and cross_sess_count == 0
            )

            hyp_entries.append({
                "hypothesis_id": hid,
                "title": hyp.get("title", ""),
                "proposition": hyp.get("proposition", ""),
                "scope_conditions": hyp.get("scope_conditions", []),
                "exclusion_clause": hyp.get("exclusion_clause", ""),
                "lineage_op": hyp.get("lineage_op", "root"),
                "generation": depths.get(hid, 0),
                "parent_hypothesis_ids": hyp.get("parent_hypothesis_ids", []),
                "children_hypothesis_ids": children_by_parent.get(hid, []),
                "initial_status": init_st,
                "effective_status": eff_status,
                "log_odds": round(log_odds[hid], 4),
                "prior": round(uniform_p, 4),
                "posterior": rounded_posterior,
                "uncertainty": uncertainty,
                "direct_eval_count": len(direct_evals),
                "adversarial_eval_count": adv_count,
                # Explicit weak, diminishing uncertainty contribution; not a
                # direct evaluation and not evidence for the posterior.
                "compared_touch_count": compared_touches[hid],
                "verdict_counts": dict(verdicts),
                "verified_material_eval_count": verified_mat_count,
                "script_eval_count": script_eval_count,
                "verified_direct_eval_count": verified_direct_count,
                "psc_eval_count": len(psc_evals),
                "support_verified_ratio": support_ratio_mean,
                "zero_verified_support_count": zero_verified_support_count,
                "fully_verified_support_count": fully_verified_support_count,
                "psc_all_verified_count": psc_classes["all_verified"],
                "psc_mixed_verified_count": psc_classes["mixed_verified"],
                "psc_zero_verified_count": psc_classes["zero_verified"],
                "witness_eval_session_count": len(eval_sessions),
                "witness_read_session_count": len(read_sessions),
                # 2026-11-16 (P-7): how many distinct rivals this hypothesis has
                # actually been separated against, and when a separation
                # involving it was last *new*. The witness count above counts
                # sessions that evaluated it; these count the pairs it has met.
                "independent_separation_count": len(separation_partners.get(hid, set())),
                "last_new_separation_date": last_new_separation.get(hid, ""),
                "same_session_eval_count": same_sess_count,
                "cross_session_eval_count": cross_sess_count,
                "low_witness_high_mass": low_witness_high_mass,
                "self_evaluated_only": self_evaluated_only,
                "supporting_material_ids": hyp.get("supporting_material_ids", []),
                "counter_material_ids": hyp.get("counter_material_ids", []),
                "source_note_ids": hyp.get("source_note_ids", []),
                "errata_flags": hyp_errata.get(hid, []),
            })

        hyp_entries.sort(key=lambda item: (-item["posterior"], item["hypothesis_id"]))
        gen0_mass = sum(h["posterior"] for h in hyp_entries if h["generation"] == 0)
        gen1_mass = sum(h["posterior"] for h in hyp_entries if h["generation"] >= 1)

        active_entries = [h for h in hyp_entries if h["effective_status"] == "active"]
        unexamined_active_ids = [
            h["hypothesis_id"] for h in active_entries if h["direct_eval_count"] == 0
        ]
        awaiting_external_audit_ids = [
            h["hypothesis_id"]
            for h in active_entries
            if (h["direct_eval_count"] == 0 or h.get("self_evaluated_only"))
            and h["hypothesis_id"] not in suppressed_hypothesis_ids
        ]
        mean_u = (
            sum(h["uncertainty"] for h in active_entries) / len(active_entries)
            if active_entries
            else 1.0
        )

        best_pair: dict[str, Any] | None = None
        candidates = active_entries if len(active_entries) >= 2 else hyp_entries
        best_score = -1.0
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                ha, hb = candidates[i], candidates[j]
                # Never recommend an unexamined side. Absence is reported,
                # rather than silently falling back to the problematic pair.
                if not ha["direct_eval_count"] or not hb["direct_eval_count"]:
                    continue
                ig_score = ha["posterior"] * hb["posterior"] * (ha["uncertainty"] + hb["uncertainty"])
                if ig_score > best_score:
                    best_score = ig_score
                    best_pair = {
                        "left_hypothesis_id": ha["hypothesis_id"],
                        "left_title": ha["title"],
                        "right_hypothesis_id": hb["hypothesis_id"],
                        "right_title": hb["title"],
                        "expected_info_gain": round(ig_score, 4),
                        "formula": PAIR_EIG_FORMULA,
                        "left_posterior": ha["posterior"],
                        "right_posterior": hb["posterior"],
                        "left_uncertainty": ha["uncertainty"],
                        "right_uncertainty": hb["uncertainty"],
                        "pair_mass_sum": pair_mass_sum(ha, hb),
                        "lineage_relation": pair_lineage_relation(ha, hb),
                        "examined_only_by_supports": pair_examined_only_by_supports(ha, hb),
                        "unsaturated_supports_ratchet": pair_has_unsaturated_supports_ratchet(ha, hb),
                    }

        # Active-only entropy measures unresolved competition among live scoped hypotheses
        active_mass = sum(h["posterior"] for h in active_entries) or 1.0
        active_entropy = -sum(
            (h["posterior"] / active_mass) * math.log2(max(h["posterior"] / active_mass, 1e-12))
            for h in active_entries
        ) if len(active_entries) > 1 else 0.0
        total_evals_q = sum(h["direct_eval_count"] for h in hyp_entries)
        priority = active_entropy + 0.8 * mean_u + (1.0 / math.sqrt(1.0 + total_evals_q))

        question_states[qid] = {
            "question_id": qid,
            "question": q_rec.get("question", ""),
            "hypothesis_count": n,
            "active_count": len(active_entries),
            "entropy_bits": round(entropy, 4),
            "active_entropy_bits": round(active_entropy, 4),
            "max_entropy_bits": round(max_entropy, 4),
            "kl_from_uniform_bits": round(kl_bits, 4),
            "gen0_mass": round(gen0_mass, 4),
            "gen1_plus_mass": round(gen1_mass, 4),
            "mean_active_uncertainty": round(mean_u, 4),
            "total_evaluations": total_evals_q,
            "priority_score": round(priority, 4),
            "top_competing_pair": best_pair,
            "unexamined_active_hypothesis_ids": unexamined_active_ids,
            "awaiting_external_audit_ids": awaiting_external_audit_ids,
            "hypotheses": hyp_entries,
        }

    ranked_core = sorted(
        (question_states[q] for q in CORE_QUESTIONS if q in question_states),
        key=lambda item: (-item["priority_score"], item["question_id"]),
    )

    state = {
        "total_hypotheses": len(hypotheses),
        "total_evaluations": len(evaluations),
        "core_priority_ranking": [q["question_id"] for q in ranked_core],
        "provenance_verification": provenance_verification,
        "questions": question_states,
        # 2026-11-16 (P-7): the archive's own novelty rate, so that a stable
        # posterior cannot be mistaken for a busy one. A row is "new" when its
        # (target, comparison set) signature has not appeared before.
        "separation_novelty": {
            "rows": novelty_total,
            "new_pairs": novelty_new,
            "share": round(novelty_new / novelty_total, 4) if novelty_total else 0.0,
        },
        # 2026-11-16 (P-6): rows whose weight a live correction withdrew.
        "voided_evaluations": voided_evaluations,
        "posterior_basis": (
            "gated" if receiver_gated else ("pair" if pair_level_repeat else "session")
        ),
    }
    state["saturation"] = saturation_snapshot(state)

    # Record structural retroactive/rival transfer counts on every entry.
    for qs in state["questions"].values():
        for h in qs.get("hypotheses") or []:
            hid = h["hypothesis_id"]
            h["postdated_heir_transfers"] = int(postdated_heir_transfers.get(hid, 0))
            h["rival_heir_transfers"] = int(rival_heir_transfers.get(hid, 0))
            h["retrieval_suppressed"] = hid in suppressed_hypothesis_ids

    if not pair_level_repeat and not receiver_gated:
        # P-3: the same ledger under a pair-level repetition discount. Reported
        # beside P, never substituted for it, so that every historical number
        # stays reproducible and the difference is itself the measurement.
        alt = compute_belief_state(
            data=cols, root=Path(root), pair_level_repeat=True,
            narrowing_partner_share=narrowing_partner_share,
        )
        for qid, qs in state["questions"].items():
            alt_q = (alt.get("questions") or {}).get(qid) or {}
            alt_p = {
                h["hypothesis_id"]: h["posterior"] for h in alt_q.get("hypotheses") or []
            }
            for h in qs.get("hypotheses") or []:
                alt_value = alt_p.get(h["hypothesis_id"])
                if alt_value is None:
                    continue
                h["pair_basis_posterior"] = round(alt_value, 4)
                h["pair_basis_delta_pp"] = round((alt_value - h["posterior"]) * 100, 2)
        state["pair_basis_summary"] = {
            "total_evaluations": alt.get("total_evaluations"),
            "separation_novelty": alt.get("separation_novelty"),
        }

    if heir_credit and not pair_level_repeat and not receiver_gated:
        # 2026-11-18 (P-8): the same ledger with the *lineage fallback* off.
        no_lin = compute_belief_state(
            data=cols, root=Path(root), heir_credit=False,
            pair_level_repeat=pair_level_repeat,
            narrowing_partner_share=narrowing_partner_share,
        )
        for qid, qs in state["questions"].items():
            alt_q = (no_lin.get("questions") or {}).get(qid) or {}
            alt_p = {h["hypothesis_id"]: h["posterior"] for h in alt_q.get("hypotheses") or []}
            for h in qs.get("hypotheses") or []:
                alt_value = alt_p.get(h["hypothesis_id"])
                if alt_value is None:
                    continue
                h["no_lineage_posterior"] = round(alt_value, 4)
                h["no_lineage_delta_pp"] = round((alt_value - h["posterior"]) * 100, 2)

        # 2026-11-18 (Three-Gates: P_gate): receiver-gated basis blocking post-dated
        # and opponent-as-heir fallback transfers, weighting PSC rows by effective
        # verification status, discounting pair repeats and self-only supports, and
        # classifying each hypothesis's receiver-local inhibition state.
        gated = compute_belief_state(
            data=cols, root=Path(root), receiver_gated=True,
            narrowing_partner_share=narrowing_partner_share,
        )
        for qid, qs in state["questions"].items():
            gq = (gated.get("questions") or {}).get(qid) or {}
            g_by_id = {h["hypothesis_id"]: h for h in gq.get("hypotheses") or []}
            for h in qs.get("hypotheses") or []:
                gh = g_by_id.get(h["hypothesis_id"])
                if gh is None:
                    continue
                gp = float(gh["posterior"])
                gl = float(gh["log_odds"])
                h["gated_posterior"] = round(gp, 4)
                h["gated_log_odds"] = round(gl, 4)
                h["gated_delta_pp"] = round((gp - h["posterior"]) * 100, 2)
                h["inhibition_state"] = _derive_inhibition_state(
                    h,
                    gated_log_odds=gl,
                    retrieval_suppressed=bool(h.get("retrieval_suppressed")),
                )
            orphans = sorted(
                (
                    h for h in (qs.get("hypotheses") or [])
                    if h.get("inhibition_state") == "orphan_over_narrowed"
                ),
                key=lambda item: (
                    -int((item.get("verdict_counts") or {}).get("narrows_scope", 0)),
                    item["hypothesis_id"],
                ),
            )
            qs["gated_entropy_bits"] = gq.get("entropy_bits", 0.0)
            qs["gated_active_entropy_bits"] = gq.get("active_entropy_bits", 0.0)
            qs["gated_kl_from_uniform_bits"] = gq.get("kl_from_uniform_bits", 0.0)
            qs["orphan_over_narrowed_ids"] = [h["hypothesis_id"] for h in orphans]
            qs["gated_top_pair"] = select_gated_pair(state, evaluations, qid)
        state["gated_saturation"] = gated.get("saturation", {})
    else:
        for qs in state["questions"].values():
            for h in qs.get("hypotheses") or []:
                h["inhibition_state"] = _derive_inhibition_state(
                    h,
                    gated_log_odds=float(h.get("log_odds", 0.0)),
                    retrieval_suppressed=bool(h.get("retrieval_suppressed")),
                )
    return state


def separation_counts(
    evaluations: dict[str, dict[str, Any]],
) -> tuple[Counter, dict[tuple[str, str], str]]:
    """Rows that separated each unordered hypothesis pair, and when last.

    A "separation" is any row that names both sides -- ``target`` and one member
    of ``compared_against_hypothesis_ids``. It does not have to be adversarial:
    a ``supports`` row that names a rival still puts the two against each other.
    """
    counts: Counter = Counter()
    last: dict[tuple[str, str], str] = {}
    for evl in evaluations.values():
        target = evl.get("target_hypothesis_id")
        if not isinstance(target, str) or not target:
            continue
        for other in evl.get("compared_against_hypothesis_ids") or []:
            if not isinstance(other, str) or not other or other == target:
                continue
            key = tuple(sorted((target, other)))
            counts[key] += 1
            day = str(evl.get("created_at") or "")[:10]
            if day > last.get(key, ""):
                last[key] = day
    return counts, last


def select_least_separated_pair(
    state: dict[str, Any],
    evaluations: dict[str, dict[str, Any]],
    question_id: str,
    *,
    min_posterior: float = 0.01,
) -> dict[str, Any] | None:
    """The eligible pair the question has separated fewest times.

    The EIG rule prefers pairs that carry mass on both sides, which structurally
    prefers pairs containing the leader -- and those are usually the pairs the
    archive has separated most often. This selector inverts the criterion: it
    offers the pair that has been tested least, restricted to hypotheses with at
    least ``min_posterior`` so that an already-eliminated hypothesis (0.0%) does
    not win by being untouched.

    Returns ``None`` when fewer than two hypotheses qualify. The returned dict
    carries the same keys as ``top_competing_pair`` plus ``policy``,
    ``separations`` and ``last_separated``.
    """
    qstate = (state.get("questions") or {}).get(question_id) or {}
    entries = [h for h in (qstate.get("hypotheses") or []) if h.get("effective_status") == "active"]
    eligible = [h for h in entries if float(h.get("posterior") or 0.0) >= min_posterior]
    if len(eligible) < 2:
        return None
    counts, last = separation_counts(evaluations)
    best: tuple[int, float, str, str, dict[str, Any], dict[str, Any]] | None = None
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            ha, hb = eligible[i], eligible[j]
            key = tuple(sorted((ha["hypothesis_id"], hb["hypothesis_id"])))
            separations = counts.get(key, 0)
            mass = min(float(ha.get("posterior") or 0.0), float(hb.get("posterior") or 0.0))
            rank = (separations, -mass, key[0], key[1])
            if best is None or rank < best[:4]:
                best = (*rank, ha, hb)
    if best is None:
        return None
    separations, _, _, _, ha, hb = best
    key = tuple(sorted((ha["hypothesis_id"], hb["hypothesis_id"])))
    ig = float(ha.get("posterior", 0.0)) * float(hb.get("posterior", 0.0)) * (
        float(ha.get("uncertainty", 0.0)) + float(hb.get("uncertainty", 0.0))
    )
    return {
        "left_hypothesis_id": ha["hypothesis_id"],
        "left_title": ha.get("title", ""),
        "right_hypothesis_id": hb["hypothesis_id"],
        "right_title": hb.get("title", ""),
        "left_posterior": round(float(ha.get("posterior", 0.0)), 4),
        "right_posterior": round(float(hb.get("posterior", 0.0)), 4),
        "left_uncertainty": round(float(ha.get("uncertainty", 0.0)), 4),
        "right_uncertainty": round(float(hb.get("uncertainty", 0.0)), 4),
        "expected_info_gain": round(ig, 4),
        "lineage_relation": pair_lineage_relation(ha, hb),
        "pair_mass_sum": pair_mass_sum(ha, hb),
        "separations": separations,
        "last_separated": last.get(key, ""),
        "policy": "least_separated",
        "min_posterior": min_posterior,
    }


def select_gated_pair(
    state: dict[str, Any],
    evaluations: dict[str, dict[str, Any]],
    question_id: str,
) -> dict[str, Any] | None:
    """Select the next competing pair under the receiver-gated basis ``P_gate``.

    Unlike default EIG on historical ``P`` (which collapses when a newborn child
    absorbs post-dated fallback transfers from its parent), ``P_gate`` blocks
    retroactive and opponent-as-heir fallback credit, scales PSC weight by
    effective material verification, and excludes inhibited
    (``refuted_inhibited`` / ``superseded_inhibited``) hypotheses.  Includes a
    mild novelty factor ``1 / (1 + 0.15 * separations)`` so repeatedly tested
    pairs yield to comparably informative fresh separations.
    """
    qstate = (state.get("questions") or {}).get(question_id) or {}
    excluded_states = {"refuted_inhibited", "superseded_inhibited", "orphan_over_narrowed"}
    eligible = [
        h
        for h in (qstate.get("hypotheses") or [])
        if h.get("effective_status") == "active"
        and h.get("direct_eval_count", 0) > 0
        and h.get("inhibition_state") not in excluded_states
    ]
    if len(eligible) < 2:
        eligible = [
            h
            for h in (qstate.get("hypotheses") or [])
            if h.get("effective_status") == "active"
            and h.get("direct_eval_count", 0) > 0
            and not h.get("retrieval_suppressed")
        ]
    if len(eligible) < 2:
        return None
    counts, last = separation_counts(evaluations)
    best_score = -1.0
    best_pair: dict[str, Any] | None = None
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            ha, hb = eligible[i], eligible[j]
            ga = float(ha.get("gated_posterior", ha.get("posterior", 0.0)))
            gb = float(hb.get("gated_posterior", hb.get("posterior", 0.0)))
            ua = float(ha.get("uncertainty", 0.0))
            ub = float(hb.get("uncertainty", 0.0))
            raw_gig = ga * gb * (ua + ub)
            key = tuple(sorted((ha["hypothesis_id"], hb["hypothesis_id"])))
            seps = counts.get(key, 0)
            scored = raw_gig / (1.0 + 0.15 * seps)
            if scored > best_score:
                best_score = scored
                ordered = (ha, hb) if ga >= gb else (hb, ha)
                la, rb = ordered
                lga = float(la.get("gated_posterior", la.get("posterior", 0.0)))
                rgb = float(rb.get("gated_posterior", rb.get("posterior", 0.0)))
                best_pair = {
                    "left_hypothesis_id": la["hypothesis_id"],
                    "left_title": la.get("title", ""),
                    "right_hypothesis_id": rb["hypothesis_id"],
                    "right_title": rb.get("title", ""),
                    "left_posterior": round(lga, 4),
                    "right_posterior": round(rgb, 4),
                    "left_historical_posterior": round(float(la.get("posterior", 0.0)), 4),
                    "right_historical_posterior": round(float(rb.get("posterior", 0.0)), 4),
                    "left_uncertainty": round(float(la.get("uncertainty", 0.0)), 4),
                    "right_uncertainty": round(float(rb.get("uncertainty", 0.0)), 4),
                    "expected_info_gain": round(raw_gig, 4),
                    "novelty_adjusted_eig": round(scored, 4),
                    "formula": "p_gate_a*p_gate_b*(u_a+u_b)/(1+0.15*sep)",
                    "lineage_relation": pair_lineage_relation(la, rb),
                    "pair_mass_sum": round(lga + rgb, 4),
                    "separations": seps,
                    "last_separated": last.get(key, ""),
                    "policy": "gated",
                }
    return best_pair


def select_auto_question_id(
    state: dict[str, Any],
    open_question_ids: list[str],
    *,
    seed: str | None = None,
) -> tuple[str, str]:
    """Select next question via UCB / Expected Information Gain (replaces pure random choice)."""
    q_states = state.get("questions", {})
    scored: list[tuple[float, str, str]] = []
    for qid in open_question_ids:
        qs = q_states.get(qid)
        jitter = 0.0
        if seed:
            hval = int(hashlib.sha256(f"ucb:{seed}:{qid}".encode("utf-8")).hexdigest()[:8], 16)
            jitter = (hval / 0xFFFFFFFF) * 0.12
        if qs and qs["hypothesis_count"] > 0:
            score = float(qs["priority_score"]) + (0.35 if qid in CORE_QUESTIONS else 0.0) + jitter
            pair = qs.get("top_competing_pair")
            if pair:
                relation = PAIR_RELATION_LABELS.get(pair.get("lineage_relation")) or "不明"
                pair_parts = [
                    f"EIG={pair['expected_info_gain']:.4f}",
                    f"系譜={relation}",
                ]
                if "pair_mass_sum" in pair:
                    pair_parts.append(f"合算={pair['pair_mass_sum'] * 100:.1f}%")
                if pair.get("examined_only_by_supports"):
                    pair_parts.append("両側 supports のみ")
                if pair.get("unsaturated_supports_ratchet"):
                    pair_parts.append("未飽和ラチェット注意")
                pair_txt = (
                    f"{pair['left_hypothesis_id']} vs {pair['right_hypothesis_id']} "
                    f"({', '.join(pair_parts)})"
                )
            else:
                pair_txt = ("単一仮説検証（対の推薦なし）" if qs["hypothesis_count"] == 1 else "推薦なし（候補に直接評価済みの仮説が2件未満）")
            unexamined = qs.get("unexamined_active_hypothesis_ids") or []
            unexamined_txt = f"; 未評価有効仮説={len(unexamined)}件" if unexamined else ""
            # Two numbers share this sentence and can move in opposite directions:
            # `score` comes from the question's entropy, `EIG` from the product of
            # two posteriors.  On 2026-11-15 scoring one pair moved them apart
            # (score 2.952 -> 2.262 while EIG 0.2259 -> 0.2951), so both formulas
            # are named here instead of leaving "情報利得" to cover two quantities.
            reason = (
                f"情報利得優先選出 (score={score:.3f}=active_H+0.8·mean_u+1/√(1+評価数)+中核0.35+乱数, "
                f"active_H={qs['active_entropy_bits']:.3f}b, "
                f"mean_u={qs['mean_active_uncertainty']:.3f}, "
                f"最優先検証対: {pair_txt}; EIG=p_a×p_b×(u_a+u_b) で両立性は検査しない{unexamined_txt})"
            )
            scored.append((score, qid, reason))
        elif qid in CORE_QUESTIONS:
            score = HYPOTHESIS_LESS_CORE_PRIORITY + jitter
            scored.append((score, qid, f"中核問い未定式化優先 (score={score:.3f})"))
        else:
            score = 0.40 + jitter
            scored.append((score, qid, f"派生問い探索枠 (score={score:.3f})"))

    scored.sort(key=lambda item: (-item[0], item[1]))
    best = scored[0]
    return best[1], best[2]


def saturation_snapshot(
    state: dict[str, Any],
    *,
    threshold: float = SATURATION_EIG_THRESHOLD,
    question_ids: tuple[str, ...] = CORE_QUESTIONS,
) -> dict[str, Any]:
    """Report which core questions have stopped selecting (not stopped believing).

    A question is *saturated* when its best competing pair's EIG is below
    ``threshold``. Saturation is a statement about the selector: another
    root hypothesis would restore entropy, but that entropy is not knowledge
    (readings/2026-11-15-where-the-learning-actually-happens.md §5).
    """
    rows: list[dict[str, Any]] = []
    for qid in question_ids:
        qstate = state["questions"].get(qid)
        if not qstate or not qstate.get("hypotheses"):
            continue
        pair = qstate.get("top_competing_pair")
        # No eligible pair is missing information, not zero EIG or saturation.
        if pair is None:
            continue
        eig = float(pair.get("expected_info_gain") or 0.0)
        rows.append({
            "question_id": qid,
            "top_eig": round(eig, 4),
            "top_posterior": round(float(qstate["hypotheses"][0].get("posterior") or 0.0), 4),
            "active_count": qstate.get("active_count", 0),
            "saturated": eig < threshold,
        })
    return {
        "threshold": threshold,
        "questions": rows,
        "saturated_question_ids": [row["question_id"] for row in rows if row["saturated"]],
    }


# ---------------------------------------------------------------------------
# Cross-question mass (addressee audit).
#
# The engine keeps ONE ``log_odds`` per hypothesis and turns it into several
# per-question distributions by a softmax over the hypotheses registered to
# each question.  An evaluation row carries ``target_hypothesis_id``,
# ``compared_against_hypothesis_ids``, ``material_ids`` and ``note_ids`` — and
# no question field (``schema/evaluation.schema.json`` has none).  So a reading
# addressed to one question moves every question that hypothesis is registered
# to, and the ledger cannot say otherwise at the row that spends the weight.
#
# The addressee is not simply missing: ``sessions.offered_target_question_id``
# records which question the session was handed, one row above.  This audit
# measures two things and changes no weight:
#
#   1. how many evaluation rows can be attributed to a single core question by
#      that row above (``receipt`` -> ``session_questions`` -> ``target_question``),
#      and how many cannot (``none``);
#   2. what each core question's distribution looks like when an evaluation is
#      counted ONLY for the question it is addressed to (+ the unaddressed
#      rows), compared with the present arithmetic that counts it everywhere.
#
# Measured 2026-11-18 on the live ledger: Q-001/Q-002 overlap (sum of the
# per-hypothesis minimum) 0.977 under the present arithmetic and 0.2512 under
# the question-scoped counterfactual.  The pair of central questions that this
# archive exists to keep apart is 97.7% the same distribution, and 72.6 points
# of that identity is produced by spending evidence addressed to one question
# inside the other.  Reading: readings/2026-11-18-the-addressee-is-one-row-
# above.md.  This is a measurement, not a proposal to change the arithmetic.
# ---------------------------------------------------------------------------

ADDRESSEE_RULE_LABELS: dict[str, str] = {
    "receipt": "セッション・レシートの offered_target_question_id",
    "session_questions": "セッションの question_ids が中核問い1件",
    "target_question": "対象仮説の question_ids が中核問い1件",
    "none": "宛先を復元できない",
}


def evaluation_addressee(
    evl: dict[str, Any],
    sessions: dict[str, dict[str, Any]],
    hypotheses: dict[str, dict[str, Any]],
    *,
    question_ids: tuple[str, ...] = CORE_QUESTIONS,
) -> tuple[str | None, str]:
    """Return ``(core question id or None, rule)`` for one evaluation row.

    The cascade is deliberately narrow-to-wide and is named in the output, so a
    reader can see how much of the attribution rests on the session receipt and
    how much on a single-question target.  ``None`` means the row names no core
    question at any level; it is counted for every question, as it is today.
    """
    core = set(question_ids)
    session = sessions.get(str(evl.get("session_id") or "")) or {}
    receipt = session.get("offered_target_question_id")
    if receipt in core:
        return receipt, "receipt"
    named = [q for q in (session.get("question_ids") or []) if q in core]
    if len(named) == 1:
        return named[0], "session_questions"
    target = hypotheses.get(str(evl.get("target_hypothesis_id") or "")) or {}
    own = [q for q in (target.get("question_ids") or []) if q in core]
    if len(own) == 1:
        return own[0], "target_question"
    return None, "none"


def _question_posterior_map(state: dict[str, Any], qid: str) -> dict[str, float]:
    qstate = (state.get("questions") or {}).get(qid) or {}
    return {
        h["hypothesis_id"]: float(h.get("posterior") or 0.0)
        for h in qstate.get("hypotheses") or []
    }


def _distribution_overlap(a: dict[str, float], b: dict[str, float]) -> float:
    """Sum of the per-hypothesis minimum: 1.0 = identical, 0.0 = disjoint."""
    return round(sum(min(a.get(k, 0.0), b.get(k, 0.0)) for k in set(a) | set(b)), 4)


def _top_rows(dist: dict[str, float], limit: int = 3) -> list[dict[str, Any]]:
    return [
        {"hypothesis_id": hid, "posterior": round(p, 4)}
        for hid, p in sorted(dist.items(), key=lambda item: (-item[1], item[0]))[:limit]
        if p > 0.0
    ]


def addressee_audit(
    data: dict[str, dict[str, dict[str, Any]]] | None = None,
    *,
    root: Path = ROOT,
    question_ids: tuple[str, ...] = CORE_QUESTIONS,
) -> dict[str, Any]:
    """Measure how much of each question's mass comes from evidence addressed elsewhere.

    Returns counts, per-question tops, and pairwise overlaps under two bases:
    ``present`` (the engine's arithmetic, unchanged) and ``question_scoped``
    (an evaluation counts only for the question it is addressed to, plus the
    rows whose addressee cannot be recovered).  Nothing is written.
    """
    cols = data if data is not None else load_belief_ledgers(root)
    sessions = cols.get("sessions") or {}
    hypotheses = cols.get("hypotheses") or {}
    evaluations = cols.get("evaluations") or {}

    rule_counts: Counter[str] = Counter()
    by_question: Counter[str] = Counter()
    addressee: dict[str, str | None] = {}
    for eid, evl in evaluations.items():
        qid, rule = evaluation_addressee(
            evl, sessions, hypotheses, question_ids=question_ids
        )
        addressee[eid] = qid
        rule_counts[rule] += 1
        by_question[qid or "unaddressed"] += 1

    present_state = compute_belief_state(data=cols, root=Path(root))
    present = {qid: _question_posterior_map(present_state, qid) for qid in question_ids}

    scoped: dict[str, dict[str, float]] = {}
    for qid in question_ids:
        sub = dict(cols)
        sub["evaluations"] = {
            eid: evl
            for eid, evl in evaluations.items()
            if addressee[eid] in (None, qid)
        }
        scoped_state = compute_belief_state(data=sub, root=Path(root))
        scoped[qid] = _question_posterior_map(scoped_state, qid)

    pairs = [
        (a, b)
        for i, a in enumerate(question_ids)
        for b in question_ids[i + 1:]
    ]
    multi_ids = {
        hid
        for hid, hyp in hypotheses.items()
        if len([q for q in (hyp.get("question_ids") or []) if q in question_ids]) > 1
    }
    all_core = sorted(
        hid
        for hid, hyp in hypotheses.items()
        if len([q for q in (hyp.get("question_ids") or []) if q in question_ids]) == len(question_ids)
    )

    return {
        "core_questions": list(question_ids),
        "evaluations": len(evaluations),
        "sessions": len(sessions),
        "sessions_with_receipt": sum(
            1 for s in sessions.values() if s.get("offered_target_question_id") in set(question_ids)
        ),
        "addressee_rule_counts": dict(rule_counts),
        "addressee_rule_labels": ADDRESSEE_RULE_LABELS,
        "evaluations_by_addressee": dict(by_question),
        "hypotheses": {
            "total": len(hypotheses),
            "multi_question": len(multi_ids),
            "multi_question_ids": sorted(multi_ids),
            "all_core_question_ids": all_core,
            "mass_on_multi_question_rows": {
                qid: {
                    "share": round(sum(p for hid, p in present[qid].items() if hid in multi_ids), 4),
                    "rows": sum(1 for hid in present[qid] if hid in multi_ids),
                    "total_rows": len(present[qid]),
                }
                for qid in question_ids
            },
            "rows_under_one_tenth_percent": {
                qid: sum(1 for p in present[qid].values() if p < 0.001)
                for qid in question_ids
            },
        },
        "present": {
            "top": {qid: _top_rows(present[qid]) for qid in question_ids},
            "overlap": {
                f"{a}|{b}": _distribution_overlap(present[a], present[b])
                for a, b in pairs
            },
        },
        "question_scoped": {
            "top": {qid: _top_rows(scoped[qid]) for qid in question_ids},
            "overlap": {
                f"{a}|{b}": _distribution_overlap(scoped[a], scoped[b])
                for a, b in pairs
            },
            "evaluations_used": {
                qid: sum(1 for qid2 in addressee.values() if qid2 in (None, qid))
                for qid in question_ids
            },
        },
        "scope_rule": (
            "question_scoped は、評価行を「セッション・レシート→セッションの"
            "question_ids→対象仮説の question_ids」の順で中核問い1件に帰属し、"
            "その問いに宛てられた行と宛先不明の行だけを数える。帰属規則は"
            "複数ありうる（note_ids・material_ids 側から復元する規則は未実装）。"
        ),
        "writes": False,
    }


def render_addressee_audit_markdown(audit: dict[str, Any]) -> str:
    """Render the addressee audit as plain text (no file is written)."""
    lines: list[str] = [
        "# 宛先監査 — 一つの log_odds が複数の softmax に入るとき",
        "",
        f"- 評価行: {audit['evaluations']} ／ セッション: {audit['sessions']} ／ "
        f"レシートに中核問いを持つセッション: {audit['sessions_with_receipt']}",
        "- 評価行に問いの欄はない（`schema/evaluation.schema.json`）。宛先は一行上から復元する。",
        "",
        "| 復元規則 | 行数 |",
        "| :--- | ---: |",
    ]
    for rule, count in sorted(audit["addressee_rule_counts"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {audit['addressee_rule_labels'].get(rule, rule)} (`{rule}`) | {count} |")
    lines.append("")
    lines.append("| 問い | 宛てられた評価行 |")
    lines.append("| :--- | ---: |")
    for qid, count in sorted(audit["evaluations_by_addressee"].items()):
        lines.append(f"| `{qid}` | {count} |")
    hyp = audit["hypotheses"]
    lines.extend([
        "",
        f"- 仮説 {hyp['total']} 件のうち複数の中核問いに登録: **{hyp['multi_question']}** 件",
        f"- 三つすべてに登録: **{len(hyp['all_core_question_ids'])}** 件（"
        + "、".join(f"`{h}`" for h in hyp["all_core_question_ids"]) + "）",
        "",
        "| 問い | 複数問い行が占める質量 | 行数 | 0.1% 未満の有効行 |",
        "| :--- | ---: | ---: | ---: |",
    ])
    for qid in audit["core_questions"]:
        m = hyp["mass_on_multi_question_rows"][qid]
        lines.append(
            f"| `{qid}` | {m['share'] * 100:.1f}% | {m['rows']}/{m['total_rows']} | "
            f"{hyp['rows_under_one_tenth_percent'][qid]} |"
        )
    for basis, label in (("present", "現行の算術"), ("question_scoped", "宛先で割った場合")):
        lines.extend(["", f"## {label}", "", "| 問い | 上位3件 |", "| :--- | :--- |"])
        for qid in audit["core_questions"]:
            top = " / ".join(
                f"`{row['hypothesis_id']}` {row['posterior'] * 100:.1f}%"
                for row in audit[basis]["top"][qid]
            )
            lines.append(f"| `{qid}` | {top} |")
        lines.append("")
        for pair, value in audit[basis]["overlap"].items():
            a, b = pair.split("|")
            lines.append(f"- 重なり `{a}` × `{b}`: **{value}**")
    lines.extend(["", f"- 規則: {audit['scope_rule']}", "- 本監査は何も書き込まない（`writes: false`）。"])
    return "\n".join(lines)


def render_belief_map_markdown(state: dict[str, Any]) -> str:
    """Render deterministic tracked BELIEF_MAP.md."""
    lines: list[str] = [
        "# BELIEF_MAP — 条件付き仮説分布と反証系譜マップ",
        "",
        "> 本ファイルは `python3 tools/belief_state.py --write-map` により `state/hypotheses*`・`state/evaluations*`・`state/materials*`・`state/read_log*` から決定論的に生成される。",
        "> 手作業で編集せず、仮説の追加・分割・反証・射程限定を台帳シャードに記録した上で再生成すること。",
        "",
        "> 不確実性は暫定指標: `u = clamp((1 + 直接の独立出所数 + 0.5×log2(1+比較回数))^(-1/2) × 反証系補正, 0.05, 1)`。比較の重複を独立出所として二重計上しない。",
        "> 対の候補は両側が直接評価済みのもののみ。該当がなければ推薦なし（飽和とは別）。未評価の有効仮説がある場合は別途明示する。",
        "> 照合済列: `全verified素材評価(+再現スクリプト評価S)/全直接評価` と `primary_source_collision` 全照合率（`verification.status` の可視化であり、過去評価の事後確率式は変更しない）。",
        "> 証人列: `EVL_sess / RL_sess`（直接評価の独立セッション数 / 機械的バックフィルを除く手書き `read_log` 読了セッション数）。`P≥5%` かつ `EVL_sess≤1` に単一証人警告を付す。",
        "> 対単位割引列 (`P_sep`): 反復割引の単位をセッションから比較集合へ替えた場合の事後確率。`P` は現行（セッション単位）の値で、履歴の再現性のため既定は変えない。**両者の差が「同じ対を同じ向きに繰り返したこと」の寄与**である（`readings/2026-11-16-stable-words-do-not-make-progress.md` §3）。",
        "> 系譜移流なし列 (`P_lin`): 系譜の引き直し（`spawned` が空のとき engine が親の子を読む）を止めた場合の事後確率。`P` との差が「**その仮説自身への判定ではなく、その親への判定から流れてきた質量**」である（`readings/2026-11-17-the-prose-is-right-and-the-mechanism-is-wrong.md` §3）。既定は引き直しを含む側で、これは併記のみ。",
        "> 独立分離列: その仮説が実際に突き合わされた相手の数と、その仮説が関与する分離が最後に「新規」だった日。証人列が「何セッションが評価したか」を数えるのに対し、こちらは「何と突き合わせたか」を数える。",
        "",
        "## 概要指標",
        "",
        f"- 登録仮説総数 (`HYP-*`): **{state['total_hypotheses']}**",
        f"- 評価イベント総数 (`EVL-*`): **{state['total_evaluations']}**",
        f"- 次回探求の情報利得優先順位: **{' → '.join(state['core_priority_ranking'])}**",
    ]
    nov = state.get("separation_novelty") or {}
    if nov.get("rows"):
        lines.append(
            f"- 分離の新規性: {nov['rows']} 行中 **{nov['new_pairs']} 行 ({nov['share'] * 100:.1f}%)** が新しい (target, 比較集合) 対。"
            "残りは既出の対の再分離であり、`P_sep` では `1/sqrt(m_pair)` でしか増えない。"
        )
    voided = state.get("voided_evaluations") or []
    if voided:
        lines.append(
            f"- 訂正により重みを撤回された評価行: **{len(voided)}** 件（"
            + "、".join(f"`{v['evaluation_id']}`" for v in voided[:5])
            + "）。行は残り、事後分布からだけ外れる。"
        )
    prov = state.get("provenance_verification") or {}
    if prov.get("psc_total", 0) > 0:
        lines.append(
            f"- `primary_source_collision` 素材照合監査: "
            f"全素材 `verified` **{prov['psc_all_verified']}/{prov['psc_total']} "
            f"({prov.get('psc_all_verified_ratio', 0.0) * 100:.1f}%)** ｜ "
            f"一部照合 **{prov.get('psc_mixed_verified', 0)}** ｜ "
            f"未照合のみ **{prov.get('psc_zero_verified', 0)}**"
        )
    lines.extend([
        "",
        "| 問い | 仮説数 (有効) | 第0世代質量 (素朴基底) | 第1世代+質量 (条件付き) | 事後エントロピー | D_KL(P_t || P_0) | 平均不確実性 u | 最優先検証ペア (EIG=p_a×p_b×(u_a+u_b)) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])
    for qid, qs in state["questions"].items():
        pair = qs.get("top_competing_pair")
        if pair:
            relation = PAIR_RELATION_LABELS.get(pair.get("lineage_relation")) or "不明"
            pair_meta = [f"{pair['expected_info_gain']:.4f}", relation]
            if "pair_mass_sum" in pair:
                mass_label = f"合算{pair['pair_mass_sum'] * 100:.1f}%"
                if pair.get("unsaturated_supports_ratchet"):
                    mass_label += " ⚠️未飽和"
                pair_meta.append(mass_label)
            pair_cell = (
                f"`{pair['left_hypothesis_id']}` vs `{pair['right_hypothesis_id']}` "
                f"({', '.join(pair_meta)})"
            )
        else:
            pair_cell = "—"
        lines.append(
            f"| `{qid}` | {qs['hypothesis_count']} ({qs['active_count']}) | "
            f"{qs['gen0_mass'] * 100:.1f}% | **{qs['gen1_plus_mass'] * 100:.1f}%** | "
            f"{qs['entropy_bits']:.3f} bits | {qs['kl_from_uniform_bits']:.3f} bits | "
            f"{qs['mean_active_uncertainty']:.3f} | {pair_cell} |"
        )

    for qid, qs in state["questions"].items():
        lines.extend([
            "",
            f"## {qid}: {qs['question']}",
            "",
        ])
        if not qs["hypotheses"]:
            lines.append("- （仮説未登録 — `Proposer` セッションで初期競合仮説を登録してください）")
            continue

        pair = qs.get("top_competing_pair")
        if pair:
            relation = PAIR_RELATION_LABELS.get(pair.get("lineage_relation")) or "不明"
            lines.append(
                f"- **最優先検証ターゲット（両側直接評価済みの候補中の最大 EIG={pair['expected_info_gain']:.4f}）**: "
                f"`{pair['left_hypothesis_id']}`（{pair['left_title']}） vs "
                f"`{pair['right_hypothesis_id']}`（{pair['right_title']}）"
            )
            mass_suffix = (
                f" ｜ 合算占有率: **{pair['pair_mass_sum'] * 100:.1f}%**"
                if "pair_mass_sum" in pair
                else ""
            )
            lines.append(
                f"  - 式: `{pair.get('formula', PAIR_EIG_FORMULA)}` = "
                f"{pair.get('left_posterior', 0.0):.4f} × {pair.get('right_posterior', 0.0):.4f} × "
                f"({pair.get('left_uncertainty', 0.0):.4f} + {pair.get('right_uncertainty', 0.0):.4f})"
                f" ｜ 記録された系譜関係: **{relation or '不明'}**{mass_suffix}"
            )
            lines.append(
                "  - この式は両立性を検査しない。二つの命題が互いを否定するかどうかは台帳から判定できず、"
                "「対立」ではなく「次に検証する組」である。系譜関係が無い場合は、両立する二つの仮説が"
                "並置されているだけの可能性がある（実測例: readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md §4）。"
            )
            if pair.get("unsaturated_supports_ratchet"):
                pmass = pair.get("pair_mass_sum", pair.get("left_posterior", 0.0) + pair.get("right_posterior", 0.0))
                lines.append(
                    f"  - ⚠️ **未飽和上位対ラチェット注意（合算占有率 {pmass * 100:.1f}% < "
                    f"{UNSATURATED_PAIR_MASS_THRESHOLD * 100:.0f}%）。** "
                    "両側にすでに反証系評価があっても、残余仮説から質量が流入する余地があるため、"
                    "両側へ `supports` を追加すると EIG が膨張しうる（PR #830 実測 +109.5%、"
                    "`readings/2026-11-16-what-crosses-the-unheld-interval.md` §2.2）。"
                    "両立性と排他条件を確かめずに両側 `supports` を積まないこと。"
                )
            if pair.get("examined_only_by_supports"):
                lines.append(
                    "  - ⚠️ **両側とも `supports` 以外の判定を受けたことがない。** `supports` には log_odds を下げる項が無いので、"
                    "この対をもう一度 `supports` すると EIG が上がることがある（実例 +30.6%。常に上がるわけではない）。競合する親子の対はそのぶん遠ざかる。"
                    "採点する前に、この二つが本当に競合するかを先に確かめること。"
                )
        else:
            lines.append("- **推薦なし**: 候補中に直接評価済みの仮説が2件未満。未評価の仮説を確認してください。")

        unexamined = qs.get("unexamined_active_hypothesis_ids") or []
        if unexamined:
            unex_list = "、".join(f"`{hid}`" for hid in unexamined)
            lines.append(
                f"- ⚠️ **未評価の有効仮説（ペア推薦から除外中）**: {unex_list}"
                "（直接評価 0 件。無補助 root 仮説は下端から浮上しにくいため、初回検証を優先検討すること）"
            )
        awaiting_ext = [
            hid for hid in (qs.get("awaiting_external_audit_ids") or [])
            if hid not in unexamined
        ]
        if awaiting_ext:
            ext_list = "、".join(f"`{hid}`" for hid in awaiting_ext)
            lines.append(
                f"- 🔍 **初回外部監査待ちの有効仮説（同一セッション自己評価のみ: {len(awaiting_ext)}件）**: {ext_list}"
                "（`P_gate` では depth≥1 の同一セッション自己支持を重み 0 として扱う。別セッションによる初回横断検証を優先検討）"
            )
        gpair = qs.get("gated_top_pair")
        if gpair:
            grel = PAIR_RELATION_LABELS.get(gpair.get("lineage_relation")) or "不明"
            lines.append(
                f"- **三門制御基底（`P_gate`）推奨検証対（`--pair-policy gated`, EIG_gate={gpair['expected_info_gain']:.4f}）**: "
                f"`{gpair['left_hypothesis_id']}`（P_gate={gpair['left_posterior']*100:.1f}%） vs "
                f"`{gpair['right_hypothesis_id']}`（P_gate={gpair['right_posterior']*100:.1f}%）"
                f" ｜ 系譜: {grel} ｜ 既分離: {gpair.get('separations', 0)}回"
                "（後付け・対立相手フォールバック移流遮断＋PSC照合度重み＋対反復割引＋自己支持暫定割引）"
            )
        orphans = qs.get("orphan_over_narrowed_ids") or []
        if orphans:
            orp_list = "、".join(f"`{hid}`" for hid in orphans[:6])
            more = f" ほか{len(orphans) - 6}件" if len(orphans) > 6 else ""
            lines.append(
                f"- **第二門・子仮説未分化の過限定仮説（`orphan_over_narrowed`: {len(orphans)}件）**: "
                f"{orp_list}{more}（`narrows_scope` が `supports` を上回り子仮説 0 件。Proposer/Consolidator の条件付き継承候補）"
            )
        lines.append("")

        lines.extend([
            "| 順位 | ID | 状態 (抑制区分) | 世代/系譜 | 事後確率 P_t | P_sep (対単位割引) | P_lin (系譜移流なし) | P_gate (三門制御) | 不確実性 u | 独立分離 (最終新規) | 評価数 (反証系) | 照合済 (PSC全照合) | 支持照合率 | 証人 (EVL/読) | 仮説タイトル |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
        ])
        for idx, h in enumerate(qs["hypotheses"], start=1):
            parents = ", ".join(f"`{p}`" for p in h["parent_hypothesis_ids"]) or "—"
            if "verified_material_eval_count" in h:
                mat_v = h["verified_material_eval_count"]
                scr_v = h.get("script_eval_count", 0)
                tot_d = h["direct_eval_count"]
                ver_cell = f"{mat_v}+{scr_v}S/{tot_d}" if scr_v else f"{mat_v}/{tot_d}"
                if h.get("psc_eval_count", 0) > 0:
                    ver_cell += f" (PSC {h.get('psc_all_verified_count', 0)}/{h['psc_eval_count']})"
            else:
                ver_cell = "—"
            # 2026-11-20 (④): share of this hypothesis's positive support that
            # rests on text-checked sources, plus how many `supports` rows rest on
            # none at all.  Derived every run; never stored.
            if h.get("support_verified_ratio") is not None:
                sup_cell = f"{h['support_verified_ratio'] * 100:.0f}%"
                nz = h.get("zero_verified_support_count", 0)
                if nz:
                    sup_cell += f" ({nz}件ゼロ)"
            else:
                sup_cell = "—"
            if "witness_eval_session_count" in h:
                wit_cell = f"{h['witness_eval_session_count']} / {h.get('witness_read_session_count', 0)}"
                if h.get("low_witness_high_mass"):
                    wit_cell += " ⚠️単一証人"
                if h.get("self_evaluated_only"):
                    wit_cell += " ⚠️自己評価のみ"
            else:
                wit_cell = "—"
            if "pair_basis_posterior" in h:
                sep_cell = f"{h['pair_basis_posterior'] * 100:.1f}% ({h.get('pair_basis_delta_pp', 0.0):+.1f}pp)"
            else:
                sep_cell = "—"
            if "no_lineage_posterior" in h:
                lin_cell = f"{h['no_lineage_posterior'] * 100:.1f}% ({h.get('no_lineage_delta_pp', 0.0):+.1f}pp)"
            else:
                lin_cell = "—"
            if "gated_posterior" in h:
                gate_cell = f"**{h['gated_posterior'] * 100:.1f}%** ({h.get('gated_delta_pp', 0.0):+.1f}pp)"
            else:
                gate_cell = "—"
            inh_st = h.get("inhibition_state", "")
            status_cell = f"`{h['effective_status']}`"
            if inh_st in ("orphan_over_narrowed", "superseded_inhibited", "self_only_provisional"):
                status_cell += f" ({INHIBITION_STATE_LABELS[inh_st]})"
            elif h.get("retrieval_suppressed"):
                status_cell += " (想起抑制)"
            sep_audit = f"{h.get('independent_separation_count', 0)} ("
            sep_audit += (h.get("last_new_separation_date") or "なし") + ")"
            lines.append(
                f"| {idx} | `{h['hypothesis_id']}` | {status_cell} | "
                f"G{h['generation']}:{h['lineage_op']} ({parents}) | "
                f"**{h['posterior'] * 100:.1f}%** | {sep_cell} | {lin_cell} | {gate_cell} | {h['uncertainty']:.3f} | "
                f"{sep_audit} | "
                f"{h['direct_eval_count']} ({h['adversarial_eval_count']}) | "
                f"{ver_cell} | {sup_cell} | {wit_cell} | {h['title']} |"
            )

        lines.append("")
        lines.append("### 条件付き命題・適用条件・反証条件（Exclusion Clause）")
        lines.append("")
        for h in qs["hypotheses"]:
            badges: list[str] = []
            if h.get("errata_flags"):
                badges.append(
                    f"⚠️ **関連訂正あり**: {', '.join(f'`{e}`' for e in h['errata_flags'])}"
                )
            if h.get("low_witness_high_mass"):
                badges.append(
                    f"⚠️ **単一証人高質量** (EVL={h.get('witness_eval_session_count', 0)}, "
                    f"読了={h.get('witness_read_session_count', 0)})"
                )
            if h.get("self_evaluated_only"):
                badges.append(
                    f"⚠️ **自己評価のみ** (同一={h.get('same_session_eval_count', 0)}, 異セッション=0)"
                )
            if (
                h.get("psc_eval_count", 0) > 0
                and h.get("psc_all_verified_count", 0) == 0
                and h.get("psc_zero_verified_count", 0) > 0
            ):
                badges.append(
                    f"⚠️ **PSC未照合のみ** ({h['psc_zero_verified_count']}/{h['psc_eval_count']})"
                )
            badge_str = (" " + " ".join(badges)) if badges else ""
            lines.append(
                f"- **`{h['hypothesis_id']}` [{h['effective_status']} / P={h['posterior'] * 100:.1f}% / u={h['uncertainty']:.3f}] {h['title']}**{badge_str}"
            )
            lines.append(f"  - **命題**: {h['proposition']}")
            lines.append(f"  - **適用条件 (`scope_conditions`)**: {' ／ '.join(h['scope_conditions'])}")
            lines.append(f"  - **反証・限定条件 (`exclusion_clause`)**: {h['exclusion_clause']}")
            if "verified_direct_eval_count" in h and "witness_eval_session_count" in h:
                lines.append(
                    f"  - **監査メタ**: 照合済直接評価={h['verified_direct_eval_count']}/{h['direct_eval_count']}"
                    f"（全verified素材={h.get('verified_material_eval_count', 0)}, "
                    f"再現スクリプト={h.get('script_eval_count', 0)}, "
                    f"PSC全照合={h.get('psc_all_verified_count', 0)}/{h.get('psc_eval_count', 0)}, "
                    f"PSC未照合のみ={h.get('psc_zero_verified_count', 0)}）"
                    f" ｜ 証人セッション: EVL={h['witness_eval_session_count']} / "
                    f"手書き読了={h.get('witness_read_session_count', 0)}"
                    f" ｜ 同一/異セッション評価={h.get('same_session_eval_count', 0)}/{h.get('cross_session_eval_count', 0)}"
                )
                sep_note = (
                    f" ｜ 独立分離={h.get('independent_separation_count', 0)} 相手"
                    f"（最終新規 {h.get('last_new_separation_date') or 'なし'}）"
                )
                if "pair_basis_posterior" in h:
                    sep_note += (
                        f" ｜ 対単位割引 basis: P_sep={h['pair_basis_posterior'] * 100:.1f}%"
                        f"（{h.get('pair_basis_delta_pp', 0.0):+.1f}pp）"
                    )
                if "no_lineage_posterior" in h:
                    sep_note += (
                        f" ｜ 系譜移流なし basis: P_lin={h['no_lineage_posterior'] * 100:.1f}%"
                        f"（{h.get('no_lineage_delta_pp', 0.0):+.1f}pp）"
                    )
                lines.append(f"  - **分離監査**: {sep_note.lstrip(' ｜ ')}")
            mats = ", ".join(f"`{m}`" for m in h["supporting_material_ids"][:5]) or "なし"
            cmats = ", ".join(f"`{m}`" for m in h["counter_material_ids"][:5]) or "なし"
            notes_s = ", ".join(f"`{n}`" for n in h["source_note_ids"][:5]) or "なし"
            lines.append(f"  - **根拠資料**: 支持={mats} ｜ 反証・緊張={cmats} ｜ 出典ノート={notes_s}")

    lines.append("")
    return "\n".join(lines)


def write_belief_maps(root: Path = ROOT) -> tuple[Path, Path]:
    """Write tracked BELIEF_MAP.md and untracked map/belief_state.md."""
    root = Path(root)
    state = compute_belief_state(root=root)
    rendered = render_belief_map_markdown(state)
    tracked = root / "BELIEF_MAP.md"
    ledger_io.atomic_write_text(tracked, rendered)
    untracked_dir = root / "map"
    untracked_dir.mkdir(parents=True, exist_ok=True)
    untracked = untracked_dir / "belief_state.md"
    ledger_io.atomic_write_text(untracked, rendered)
    return tracked, untracked


def check_belief_map(root: Path = ROOT) -> tuple[bool, str]:
    """Verify tracked BELIEF_MAP.md is up to date with state/."""
    root = Path(root)
    tracked = root / "BELIEF_MAP.md"
    if not tracked.is_file():
        return False, "BELIEF_MAP.md is missing (run: python3 tools/belief_state.py --write-map)"
    expected = render_belief_map_markdown(compute_belief_state(root=root))
    actual = tracked.read_text(encoding="utf-8")
    if actual != expected:
        return False, "BELIEF_MAP.md is out of date with state/hypotheses* or state/evaluations* (run: python3 tools/belief_state.py --write-map)"
    return True, f"PASS: BELIEF_MAP.md is current ({len(expected.encode('utf-8')):,} bytes)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--question", help="inspect a single question ID (e.g. Q-002)")
    parser.add_argument(
        "--gated",
        action="store_true",
        help="compute under the Three-Gates receiver-gated basis (P_gate)",
    )
    parser.add_argument("--json", action="store_true", help="output full JSON belief state")
    parser.add_argument("--write-map", action="store_true", help="write BELIEF_MAP.md and map/belief_state.md")
    parser.add_argument("--check-map", action="store_true", help="verify BELIEF_MAP.md is current")
    parser.add_argument(
        "--addressee-audit",
        action="store_true",
        help="measure cross-question mass (which question each evaluation is addressed to); writes nothing",
    )
    args = parser.parse_args(argv)

    if args.addressee_audit:
        audit = addressee_audit(root=args.root)
        if args.json:
            print(json.dumps(audit, ensure_ascii=False, indent=2))
        else:
            print(render_addressee_audit_markdown(audit))
        return 0

    if args.write_map:
        tracked, _untracked = write_belief_maps(args.root)
        size = tracked.stat().st_size
        print(f"WROTE {tracked.relative_to(Path(args.root))} ({size:,} bytes)")
        return 0

    if args.check_map:
        ok, msg = check_belief_map(args.root)
        stream = sys.stdout if ok else sys.stderr
        print(msg, file=stream)
        return 0 if ok else 1

    state = compute_belief_state(root=args.root, receiver_gated=args.gated)
    if args.question:
        qs = state["questions"].get(args.question)
        if qs is None:
            print(f"error: unknown or unindexed question {args.question!r}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(qs, ensure_ascii=False, indent=2))
        else:
            for h in qs["hypotheses"]:
                print(
                    f"{h['hypothesis_id']} [{h['effective_status']}] P={h['posterior']*100:.1f}% "
                    f"u={h['uncertainty']:.3f} G{h['generation']} {h['title']}"
                )
        return 0

    if args.json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    print(render_belief_map_markdown(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
