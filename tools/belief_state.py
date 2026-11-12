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
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
CORE_QUESTIONS: tuple[str, ...] = ("Q-001", "Q-002", "Q-003")

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
    """Load questions, hypotheses, evaluations, notes, materials, fragments, sessions, errata."""
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
    return cols


def build_errata_index(errata: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Map any target ID or repo path -> list of errata records targeting it (1-hop)."""
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
) -> dict[str, Any]:
    """Compute posterior distributions, uncertainties, lineage shifts, and next-test targets."""
    cols = data if data is not None else load_belief_ledgers(root)
    questions = cols.get("questions", {})
    hypotheses = cols.get("hypotheses", {})
    evaluations = cols.get("evaluations", {})
    errata = cols.get("errata")
    if errata is None:
        errata_base = Path(root) / "state" / "errata.jsonl"
        if errata_base.exists() or ledger_io.shard_dir(errata_base).is_dir():
            sub_cols, _ = ledger_io.load_collections({"errata": (errata_base, "errata_id")}, root=Path(root))
            errata = sub_cols.get("errata", {})
        else:
            errata = {}

    errata_by_target = build_errata_index(errata)
    depths = _generation_depths(hypotheses)

    children_by_parent: dict[str, list[str]] = defaultdict(list)
    q_to_hyps: dict[str, list[str]] = defaultdict(list)
    for hid, hyp in sorted(hypotheses.items()):
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

    evals_by_hyp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    compared_touches: Counter[str] = Counter()
    adversarial_touches: Counter[str] = Counter()
    repeat_tracker: Counter[tuple[str, str, str]] = Counter()
    indep_sources: dict[str, set[str]] = defaultdict(set)

    for evl_id, evl in sorted(evaluations.items()):
        target_id = evl.get("target_hypothesis_id")
        if not isinstance(target_id, str) or target_id not in hypotheses:
            continue
        verdict = str(evl.get("verdict") or "supports")
        ev_type = str(evl.get("evidence_type") or "cross_session_audit")
        base_w = EVIDENCE_WEIGHTS.get(ev_type, 1.0)

        sid = str(evl.get("session_id") or "")
        mat_sig = ",".join(sorted(evl.get("material_ids") or []))
        source_key = mat_sig or ",".join(sorted(evl.get("note_ids") or [])) or evl_id
        repeat_key = (target_id, verdict, sid or source_key)
        repeat_tracker[repeat_key] += 1
        k_rep = repeat_tracker[repeat_key]
        indep_discount = 1.0 / math.sqrt(k_rep)

        compared = [
            cid for cid in (evl.get("compared_against_hypothesis_ids") or [])
            if isinstance(cid, str) and cid in hypotheses and cid != target_id
        ]
        comp_factor = 1.0 if compared else 0.65
        delta = base_w * indep_discount * comp_factor

        evals_by_hyp[target_id].append(evl)
        indep_sources[target_id].add(f"{ev_type}:{source_key}")
        for cid in compared:
            compared_touches[cid] += 1
            indep_sources[cid].add(f"cmp:{ev_type}:{source_key}")

        spawned = [
            shid for shid in (evl.get("spawned_hypothesis_ids") or [])
            if isinstance(shid, str) and shid in hypotheses and shid != target_id
        ]
        if not spawned:
            spawned = children_by_parent.get(target_id, [])

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
        if direct_errs:
            log_odds[hid] -= 0.60 * len(direct_errs)
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
                "priority_score": 2.0,
                "top_competing_pair": None,
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
            raw_u = (1.0 / math.sqrt(1.0 + n_indep)) * (1.25 if adv_count == 0 else 1.0)
            uncertainty = round(min(1.0, max(0.05, raw_u)), 4)

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
                "posterior": round(posteriors[hid], 4),
                "uncertainty": uncertainty,
                "direct_eval_count": len(direct_evals),
                "adversarial_eval_count": adv_count,
                "verdict_counts": dict(verdicts),
                "supporting_material_ids": hyp.get("supporting_material_ids", []),
                "counter_material_ids": hyp.get("counter_material_ids", []),
                "source_note_ids": hyp.get("source_note_ids", []),
                "errata_flags": hyp_errata.get(hid, []),
            })

        hyp_entries.sort(key=lambda item: (-item["posterior"], item["hypothesis_id"]))
        gen0_mass = sum(h["posterior"] for h in hyp_entries if h["generation"] == 0)
        gen1_mass = sum(h["posterior"] for h in hyp_entries if h["generation"] >= 1)

        active_entries = [h for h in hyp_entries if h["effective_status"] == "active"]
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
                ig_score = ha["posterior"] * hb["posterior"] * (ha["uncertainty"] + hb["uncertainty"])
                if ig_score > best_score:
                    best_score = ig_score
                    best_pair = {
                        "left_hypothesis_id": ha["hypothesis_id"],
                        "left_title": ha["title"],
                        "right_hypothesis_id": hb["hypothesis_id"],
                        "right_title": hb["title"],
                        "expected_info_gain": round(ig_score, 4),
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
            "hypotheses": hyp_entries,
        }

    ranked_core = sorted(
        (question_states[q] for q in CORE_QUESTIONS if q in question_states),
        key=lambda item: (-item["priority_score"], item["question_id"]),
    )

    return {
        "total_hypotheses": len(hypotheses),
        "total_evaluations": len(evaluations),
        "core_priority_ranking": [q["question_id"] for q in ranked_core],
        "questions": question_states,
    }


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
            pair_txt = (
                f"{pair['left_hypothesis_id']} vs {pair['right_hypothesis_id']} (EIG={pair['expected_info_gain']:.4f})"
                if pair else "単一仮説検証"
            )
            reason = (
                f"情報利得優先選出 (score={score:.3f}, active_H={qs['active_entropy_bits']:.3f}b, "
                f"mean_u={qs['mean_active_uncertainty']:.3f}, 最優先対立対: {pair_txt})"
            )
            scored.append((score, qid, reason))
        elif qid in CORE_QUESTIONS:
            score = 2.50 + jitter
            scored.append((score, qid, f"中核問い未定式化優先 (score={score:.3f})"))
        else:
            score = 0.40 + jitter
            scored.append((score, qid, f"派生問い探索枠 (score={score:.3f})"))

    scored.sort(key=lambda item: (-item[0], item[1]))
    best = scored[0]
    return best[1], best[2]


def render_belief_map_markdown(state: dict[str, Any]) -> str:
    """Render deterministic tracked BELIEF_MAP.md."""
    lines: list[str] = [
        "# BELIEF_MAP — 条件付き仮説分布と反証系譜マップ",
        "",
        "> 本ファイルは `python3 tools/belief_state.py --write-map` により `state/hypotheses*` と `state/evaluations*` から決定論的に生成される。",
        "> 手作業で編集せず、仮説の追加・分割・反証・射程限定を台帳シャードに記録した上で再生成すること。",
        "",
        "## 概要指標",
        "",
        f"- 登録仮説総数 (`HYP-*`): **{state['total_hypotheses']}**",
        f"- 評価イベント総数 (`EVL-*`): **{state['total_evaluations']}**",
        f"- 次回探求の情報利得優先順位: **{' → '.join(state['core_priority_ranking'])}**",
        "",
        "| 問い | 仮説数 (有効) | 第0世代質量 (素朴基底) | 第1世代+質量 (条件付き) | 事後エントロピー | D_KL(P_t || P_0) | 平均不確実性 u | 最優先対立ペア (EIG) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for qid, qs in state["questions"].items():
        pair = qs.get("top_competing_pair")
        pair_cell = (
            f"`{pair['left_hypothesis_id']}` vs `{pair['right_hypothesis_id']}` ({pair['expected_info_gain']:.4f})"
            if pair else "—"
        )
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
            lines.append(
                f"- **最優先検証ターゲット（最大期待情報利得 EIG={pair['expected_info_gain']:.4f}）**: "
                f"`{pair['left_hypothesis_id']}`（{pair['left_title']}） vs "
                f"`{pair['right_hypothesis_id']}`（{pair['right_title']}）"
            )
            lines.append("")

        lines.extend([
            "| 順位 | ID | 状態 | 世代/系譜 | 事後確率 P_t | 不確実性 u | 評価数 (反証系) | 仮説タイトル |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |",
        ])
        for idx, h in enumerate(qs["hypotheses"], start=1):
            parents = ", ".join(f"`{p}`" for p in h["parent_hypothesis_ids"]) or "—"
            lines.append(
                f"| {idx} | `{h['hypothesis_id']}` | `{h['effective_status']}` | "
                f"G{h['generation']}:{h['lineage_op']} ({parents}) | "
                f"**{h['posterior'] * 100:.1f}%** | {h['uncertainty']:.3f} | "
                f"{h['direct_eval_count']} ({h['adversarial_eval_count']}) | {h['title']} |"
            )

        lines.append("")
        lines.append("### 条件付き命題・適用条件・反証条件（Exclusion Clause）")
        lines.append("")
        for h in qs["hypotheses"]:
            err_badge = (
                f" ⚠️ **関連訂正あり**: {', '.join(f'`{e}`' for e in h['errata_flags'])}"
                if h["errata_flags"] else ""
            )
            lines.append(
                f"- **`{h['hypothesis_id']}` [{h['effective_status']} / P={h['posterior'] * 100:.1f}% / u={h['uncertainty']:.3f}] {h['title']}**{err_badge}"
            )
            lines.append(f"  - **命題**: {h['proposition']}")
            lines.append(f"  - **適用条件 (`scope_conditions`)**: {' ／ '.join(h['scope_conditions'])}")
            lines.append(f"  - **反証・限定条件 (`exclusion_clause`)**: {h['exclusion_clause']}")
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
    parser.add_argument("--json", action="store_true", help="output full JSON belief state")
    parser.add_argument("--write-map", action="store_true", help="write BELIEF_MAP.md and map/belief_state.md")
    parser.add_argument("--check-map", action="store_true", help="verify BELIEF_MAP.md is current")
    args = parser.parse_args(argv)

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

    state = compute_belief_state(root=args.root)
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
