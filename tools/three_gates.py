#!/usr/bin/env python3
"""Three-Gates memory, inhibition, and reality-monitoring engine (stdlib only).

Operationalises the three dissociable mechanisms diagnosed in
``readings/2026-11-18-three-gates-between-trace-and-self.md`` (§4, §5.3, §6.2)
without rewriting any existing append-only ledger line:

* **Gate 1 — Binding, closed-loop completion & non-fusing temporal linkage**
  (Horner et al. 2015; Cai et al. 2016; Vaz et al. 2019): closed 3-loop triad
  completion, 1-day cross-session ensemble linkage, non-shared erasure rate
  across co-linked materials, and §3 active verified evidence coverage.
* **Gate 2 — Receiver-local inhibition & reactive intrusion control**
  (Wimber et al. 2015; Gagnepain et al. 2017; Schmitz et al. 2017): receiver-
  gated posterior ``P_gate`` (blocking post-dated and rival-as-heir fallback
  transfers), ``orphan_over_narrowed`` handoff queue, item-specific salience
  dampening with category preservation, and exposure-matched pre/post cohort
  re-citation tracking (testing ``HYP-20261118-21461e`` exclusion clause (d)).
* **Gate 3 — Reality monitoring, external grounding & DN-A / DN-B separation**
  (Garrison et al. 2015; Parvizi et al. 2021; Braga & Buckner 2017; DiNicola
  et al. 2020; Sormaz et al. 2018): pre-acquisition DOI/PMID/PMCID/title
  collision checker ("falling pen"), append-only material verification overlay
  accounting and high-leverage upgrade queue, and DN-A vs DN-B channel balance.

Usage:
    python3 tools/three_gates.py
    python3 tools/three_gates.py --check
    python3 tools/three_gates.py --check-source --doi 10.1038/ncomms8499 --title "Retrieval induces adaptive forgetting"
    python3 tools/three_gates.py --upgrade-candidates --limit 15
    python3 tools/three_gates.py --cohort-suppression
    python3 tools/three_gates.py --complete Q-002 HYP-20261118-21461e
    python3 tools/three_gates.py --json
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

import associations  # noqa: E402
import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402
import ledger_io  # noqa: E402
import validate_seed  # noqa: E402

DNA_TYPES = frozenset({"material", "fragment", "motif"})
DNB_TYPES = frozenset({"note", "hypothesis", "evaluation", "erratum", "session", "editorial_decision"})
_FULLTEXT_HINT_RE = re.compile(
    r"(全文|full[\s_-]?text|PMC\d{5,}|原典精読|本文照合|open[\s_-]?access\s+full)",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[0-9a-z\u3040-\u30ff\u4e00-\u9fff]+")
_TITLE_STOP = frozenset({"the", "and", "for", "with", "from", "that", "this", "into", "over", "are", "of", "in", "on", "to", "a", "an", "by"})


def load_archive(root: Path = _ROOT) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, dict[str, Any]]]:
    root = Path(root).resolve()
    errors: list[str] = []
    specs: dict[str, tuple[Path, str]] = {}
    for name, (filename, id_key, _schema) in validate_seed.COLLECTIONS.items():
        base = root / "state" / filename
        if base.is_file() or ledger_io.shard_dir(base).is_dir():
            specs[name] = (base, id_key)
    data, lerrs = ledger_io.load_collections(specs, root=root)
    errors.extend(lerrs)
    for name in validate_seed.COLLECTIONS:
        data.setdefault(name, {})
    err_base = root / "state" / "errata.jsonl"
    errata: dict[str, dict[str, Any]] = {}
    if err_base.is_file() or ledger_io.shard_dir(err_base).is_dir():
        errata = ledger_io.load_jsonl_union(err_base, "errata_id", errors, root=root)
    data["errata"] = errata
    return data, errata


def _normalize_title(title: str) -> tuple[str, set[str]]:
    norm = unicodedata.normalize("NFKC", str(title or "")).casefold()
    tokens = [t for t in _WORD_RE.findall(norm) if t not in _TITLE_STOP and len(t) >= 2]
    return " ".join(tokens), set(tokens)


def check_source(
    materials: dict[str, dict[str, Any]],
    *,
    doi: str = "",
    pmid: str = "",
    pmcid: str = "",
    url: str = "",
    title: str = "",
    title_threshold: float = 0.72,
) -> dict[str, Any]:
    """Check a candidate primary source against all archived materials (Gate 3)."""
    probe = {
        "source": {
            "url": " ".join(x for x in (url, f"https://doi.org/{doi}" if doi else "", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "", pmcid) if x),
            "source_id": doi or pmcid or pmid or "",
        }
    }
    wanted_ids = validate_seed.extract_material_identifiers(probe)
    if doi and "doi" not in wanted_ids:
        cleaned = doi.strip()
        cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned, flags=re.I)
        cleaned = re.sub(r"^doi:\s*", "", cleaned, flags=re.I).rstrip(".,;:)/").lower()
        if cleaned:
            wanted_ids["doi"] = cleaned
    if pmid and "pmid" not in wanted_ids:
        digits = re.sub(r"\D", "", pmid)
        if digits:
            wanted_ids["pmid"] = digits
    if pmcid and "pmcid" not in wanted_ids:
        cm = re.search(r"(PMC\d+)", pmcid, re.I)
        if cm:
            wanted_ids["pmcid"] = cm.group(1).upper()

    q_norm, q_tokens = _normalize_title(title)
    exact_matches: list[dict[str, Any]] = []
    title_matches: list[dict[str, Any]] = []

    for mid, rec in materials.items():
        m_ids = validate_seed.extract_material_identifiers(rec)
        # Also detect PMCID recorded in version_note for pre-acquisition advisories.
        vnote = str(((rec.get("source") or {}).get("version_note")) or "")
        if "pmcid" not in m_ids:
            cm = re.search(r"\b(PMC\d{5,10})\b", vnote, re.I)
            if cm:
                m_ids["pmcid"] = cm.group(1).upper()
        matched_on = [
            f"{k}:{wanted_ids[k]}"
            for k in ("doi", "pmcid", "pmid")
            if k in wanted_ids and m_ids.get(k) == wanted_ids[k]
        ]
        vstat = str(((rec.get("verification") or {}).get("status")) or "unrecorded")
        src = rec.get("source") or {}
        if matched_on:
            exact_matches.append(
                {
                    "material_id": mid,
                    "matched_on": matched_on,
                    "title": str(rec.get("title") or ""),
                    "year": src.get("year"),
                    "verification_status": vstat,
                    "url": str(src.get("url") or ""),
                    "can_upgrade_via_editorial_decision": vstat != "verified",
                }
            )
            continue
        if q_tokens and len(q_tokens) >= 3:
            m_norm, m_tokens = _normalize_title(str(rec.get("title") or ""))
            if not m_tokens:
                continue
            if q_norm == m_norm:
                sim = 1.0
            else:
                inter = len(q_tokens & m_tokens)
                union = len(q_tokens | m_tokens)
                sim = inter / union if union else 0.0
            if sim >= title_threshold:
                title_matches.append(
                    {
                        "material_id": mid,
                        "title_similarity": round(sim, 3),
                        "title": str(rec.get("title") or ""),
                        "year": src.get("year"),
                        "verification_status": vstat,
                        "url": str(src.get("url") or ""),
                        "can_upgrade_via_editorial_decision": vstat != "verified",
                    }
                )

    title_matches.sort(key=lambda r: (-r["title_similarity"], r["material_id"]))
    status = "DUPLICATE_ID" if exact_matches else ("SIMILAR_TITLE" if title_matches else "CLEAR")
    upgrade_hint = None
    first_non_v = next(
        (m for m in exact_matches + title_matches if m["can_upgrade_via_editorial_decision"]),
        None,
    )
    if first_non_v:
        upgrade_hint = {
            "decision_id": "ED-YYYYMMDD-xxxxxx",
            "session_id": "SESSION-YYYYMMDD-xxxxxx",
            "target": {"type": "material", "id": first_non_v["material_id"]},
            "status": "verified",
            "verification_method": "Primary full text verified directly at <DOI/PMCID/edition>",
            "reason": "Full-text re-verification of archived material without duplicating MAT row.",
            "created_at": datetime.date.today().isoformat(),
        }
    return {
        "status": status,
        "queried_identifiers": wanted_ids,
        "queried_title": title,
        "exact_identifier_matches": exact_matches,
        "similar_title_matches": title_matches[:5],
        "editorial_upgrade_template": upgrade_hint,
    }


def duplicate_identifier_summary(materials: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Inventory historical duplicate DOIs, PMCIDs, and PMIDs in ``materials``."""
    buckets: dict[str, dict[str, list[str]]] = {
        "doi": defaultdict(list),
        "pmcid": defaultdict(list),
        "pmid": defaultdict(list),
    }
    for mid, rec in materials.items():
        ids = validate_seed.extract_material_identifiers(rec)
        for kind, val in ids.items():
            buckets[kind][val].append(mid)
    out: dict[str, Any] = {}
    for kind in ("doi", "pmcid", "pmid"):
        dups = {v: mids for v, mids in buckets[kind].items() if len(mids) >= 2}
        extra = sum(len(mids) - 1 for mids in dups.values())
        sample = [
            {"value": v, "material_ids": mids}
            for v, mids in sorted(dups.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:8]
        ]
        out[kind] = {
            "distinct_duplicated": len(dups),
            "extra_rows": extra,
            "top_groups": sample,
        }
    out["gate_enforced_from"] = validate_seed.THREE_GATES_RULE_FROM
    return out


def upgrade_candidates(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    limit: int = 15,
) -> dict[str, Any]:
    """Rank non-verified archived materials by PSC verification leverage (Gate 3)."""
    materials = data.get("materials", {})
    evaluations = data.get("evaluations", {})
    read_log = data.get("read_log", {})

    psc_cites: Counter[str] = Counter()
    psc_unlock_1step: Counter[str] = Counter()
    eval_cites: Counter[str] = Counter()
    for evl in evaluations.values():
        mids = [m for m in (evl.get("material_ids") or ()) if isinstance(m, str) and m in materials]
        for mid in mids:
            eval_cites[mid] += 1
        if evl.get("evidence_type") != "primary_source_collision" or not mids:
            continue
        non_v = [
            mid for mid in mids
            if ((materials[mid].get("verification") or {}).get("status")) != "verified"
        ]
        for mid in non_v:
            psc_cites[mid] += 1
        if len(non_v) == 1:
            psc_unlock_1step[non_v[0]] += 1

    fulltext_reads: dict[str, list[str]] = defaultdict(list)
    for row in read_log.values():
        tgt = row.get("target")
        if not isinstance(tgt, dict) or tgt.get("type") != "material":
            continue
        mid = str(tgt.get("id") or "")
        note = str(row.get("note") or "")
        if mid in materials and _FULLTEXT_HINT_RE.search(note):
            sid = str(row.get("session_id") or "")
            if sid and sid not in fulltext_reads[mid]:
                fulltext_reads[mid].append(sid)

    non_verified_with_hint = 0
    rows: list[dict[str, Any]] = []
    for mid, rec in materials.items():
        vstat = str(((rec.get("verification") or {}).get("status")) or "unrecorded")
        if vstat == "verified":
            continue
        hints = fulltext_reads.get(mid, [])
        if hints:
            non_verified_with_hint += 1
        pc = psc_cites.get(mid, 0)
        u1 = psc_unlock_1step.get(mid, 0)
        ec = eval_cites.get(mid, 0)
        if pc == 0 and not hints:
            continue
        src = rec.get("source") or {}
        rows.append(
            {
                "material_id": mid,
                "title": str(rec.get("title") or "")[:90],
                "year": src.get("year"),
                "current_status": vstat,
                "psc_citations": pc,
                "psc_single_blocker_rows": u1,
                "total_eval_citations": ec,
                "fulltext_hint_sessions": len(hints),
                "url": str(src.get("url") or ""),
            }
        )
    rows.sort(
        key=lambda r: (
            -r["psc_single_blocker_rows"],
            -r["psc_citations"],
            -r["fulltext_hint_sessions"],
            -r["total_eval_citations"],
            r["material_id"],
        )
    )
    material_overlays = [
        did
        for did, ed in (data.get("editorial_decisions") or {}).items()
        if isinstance(ed.get("target"), dict) and ed["target"].get("type") == "material"
    ]
    status_counts = Counter(
        str(((m.get("verification") or {}).get("status")) or "unrecorded")
        for m in materials.values()
    )
    return {
        "total_materials": len(materials),
        "status_counts": dict(status_counts),
        "material_overlay_decisions": len(material_overlays),
        "non_verified_with_fulltext_read_hint": non_verified_with_hint,
        "psc_cited_non_verified_materials": sum(1 for r in rows if r["psc_citations"] > 0),
        "top_candidates": rows[:limit] if limit > 0 else rows,
    }


def cohort_suppression_audit(
    data: dict[str, dict[str, dict[str, Any]]],
    errata: dict[str, dict[str, Any]],
    *,
    window_sessions: int = 40,
) -> dict[str, Any]:
    """Exposure-matched longitudinal pre/post re-citation audit (Gate 2, §6.2(2)).

    Directly measures ``HYP-20261118-21461e`` exclusion clause (d): after a
    record first receives ``narrows_scope``, ``refutes_unconditioned``, a live
    ``contradicted`` erratum, ``void_row``, or ``suppress_retrieval``, does its
    active cross-session re-citation rate in the next ``window_sessions`` drop,
    stay flat, or amplify via Gagnepain-style intrusion exposure?
    """
    sessions = list((data.get("sessions") or {}).keys())
    sess_idx = {sid: i for i, sid in enumerate(sessions)}
    n_sess = len(sessions)

    # Map each target ID to the session indices where it was actively read or evaluated.
    touch_indices: dict[str, list[int]] = defaultdict(list)
    first_seen_idx: dict[str, int] = {}

    def _note_birth(tid: str, sid: str) -> None:
        idx = sess_idx.get(sid)
        if idx is not None and (tid not in first_seen_idx or idx < first_seen_idx[tid]):
            first_seen_idx[tid] = idx

    for fid, f in (data.get("fragments") or {}).items():
        _note_birth(fid, str(f.get("session_id") or ""))
    for hid, h in (data.get("hypotheses") or {}).items():
        _note_birth(hid, str(h.get("session_id") or ""))
    for nid, n in (data.get("notes") or {}).items():
        _note_birth(nid, str(n.get("report_session_id") or n.get("session_id") or ""))

    seen_sess_target: set[tuple[int, str]] = set()
    for row in (data.get("read_log") or {}).values():
        if row.get("reading") not in associations.ACTIVE_READINGS:
            continue
        sid = str(row.get("session_id") or "")
        idx = sess_idx.get(sid)
        tgt = row.get("target")
        if idx is None or not isinstance(tgt, dict):
            continue
        tid = str(tgt.get("id") or "")
        if not tid:
            continue
        if tid not in first_seen_idx or idx < first_seen_idx[tid]:
            first_seen_idx[tid] = idx
        if (idx, tid) not in seen_sess_target:
            seen_sess_target.add((idx, tid))
            touch_indices[tid].append(idx)

    for evl in (data.get("evaluations") or {}).values():
        sid = str(evl.get("session_id") or "")
        idx = sess_idx.get(sid)
        if idx is None:
            continue
        for tid in (
            [evl.get("target_hypothesis_id")]
            + list(evl.get("compared_against_hypothesis_ids") or ())
            + list(evl.get("material_ids") or ())
        ):
            if isinstance(tid, str) and tid:
                if tid not in first_seen_idx or idx < first_seen_idx[tid]:
                    first_seen_idx[tid] = idx
                if (idx, tid) not in seen_sess_target:
                    seen_sess_target.add((idx, tid))
                    touch_indices[tid].append(idx)

    for tid in touch_indices:
        touch_indices[tid].sort()

    # Map YYYY-MM-DD -> median session index for errata rows lacking session_id.
    day_to_indices: dict[str, list[int]] = defaultdict(list)
    for sid, idx in sess_idx.items():
        srec = data["sessions"][sid]
        day = belief_state._record_iso_day(srec, sid)
        if day:
            day_to_indices[day].append(idx)
    day_anchor = {d: idxs[len(idxs) // 2] for d, idxs in day_to_indices.items()}

    cohorts: dict[str, dict[str, int]] = {
        "narrows_scope": {},
        "refutes_unconditioned": {},
        "errata_contradicted": {},
        "errata_void_row": {},
        "errata_suppress_retrieval": {},
    }
    for eid, evl in sorted((data.get("evaluations") or {}).items()):
        vd = evl.get("verdict")
        th = evl.get("target_hypothesis_id")
        idx = sess_idx.get(str(evl.get("session_id") or ""))
        if idx is None or not isinstance(th, str):
            continue
        if vd in ("narrows_scope", "refutes_unconditioned"):
            prev = cohorts[vd].get(th)
            if prev is None or idx < prev:
                cohorts[vd][th] = idx

    for err_id, erec in sorted(errata.items()):
        if not associations._is_live_contradicted_erratum(erec):
            continue
        sid = erec.get("subject_id") or erec.get("fragment_id")
        if not isinstance(sid, str) or not sid:
            continue
        day = belief_state._record_iso_day(erec, err_id)
        idx = day_anchor.get(day)
        if idx is None:
            continue
        weff = erec.get("weight_effect")
        if weff == "void_row":
            bucket = "errata_void_row"
        elif weff == "suppress_retrieval":
            bucket = "errata_suppress_retrieval"
        else:
            bucket = "errata_contradicted"
        prev = cohorts[bucket].get(sid)
        if prev is None or idx < prev:
            cohorts[bucket][sid] = idx

    results: dict[str, dict[str, Any]] = {}
    for cname, events in cohorts.items():
        measured = decreased = increased = unchanged_zero = unchanged_pos = 0
        pre_rates: list[float] = []
        post_rates: list[float] = []
        for tid, ev_idx in events.items():
            birth = first_seen_idx.get(tid, ev_idx)
            pre_start = max(birth, ev_idx - window_sessions)
            pre_span = ev_idx - pre_start
            post_end = min(n_sess - 1, ev_idx + window_sessions)
            post_span = post_end - ev_idx
            if pre_span < 3 or post_span < 3:
                continue
            touches = touch_indices.get(tid, [])
            pre_hits = sum(1 for x in touches if pre_start <= x < ev_idx)
            post_hits = sum(1 for x in touches if ev_idx < x <= post_end)
            pr = pre_hits / pre_span
            qr = post_hits / post_span
            measured += 1
            pre_rates.append(pr)
            post_rates.append(qr)
            if qr < pr - 1e-9:
                decreased += 1
            elif qr > pr + 1e-9:
                increased += 1
            elif pr == 0.0 and qr == 0.0:
                unchanged_zero += 1
            else:
                unchanged_pos += 1
        mean_pre = sum(pre_rates) / measured if measured else 0.0
        mean_post = sum(post_rates) / measured if measured else 0.0
        results[cname] = {
            "total_targets": len(events),
            "measured_targets": measured,
            "mean_pre_rate_per_session": round(mean_pre, 4),
            "mean_post_rate_per_session": round(mean_post, 4),
            "post_to_pre_ratio": round(mean_post / mean_pre, 3) if mean_pre > 0 else None,
            "decreased": decreased,
            "increased_intrusion": increased,
            "quiet_both": unchanged_zero,
            "unchanged_active": unchanged_pos,
        }
    return {
        "window_sessions": window_sessions,
        "total_sessions": n_sess,
        "cohorts": results,
    }


def dn_channel_balance(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    recent_sessions: int = 50,
) -> dict[str, Any]:
    """Measure DN-A (scene/archive retrieval) vs DN-B (state/reply/belief monitoring) balance."""
    session_ids = list((data.get("sessions") or {}).keys())
    recent_set = set(session_ids[-recent_sessions:]) if recent_sessions > 0 else set(session_ids)

    def _tally(filter_set: set[str] | None) -> dict[str, Any]:
        dna = dnb = reply_rows = active_total = 0
        sess_dna: set[str] = set()
        sess_dnb: set[str] = set()
        active_sess: set[str] = set()
        for row in (data.get("read_log") or {}).values():
            sid = str(row.get("session_id") or "")
            if filter_set is not None and sid not in filter_set:
                continue
            if row.get("in_reply_to"):
                reply_rows += 1
            if row.get("reading") not in associations.ACTIVE_READINGS:
                continue
            tgt = row.get("target")
            if not isinstance(tgt, dict):
                continue
            ttype = str(tgt.get("type") or "")
            active_total += 1
            if sid:
                active_sess.add(sid)
            if ttype in DNA_TYPES:
                dna += 1
                if sid:
                    sess_dna.add(sid)
            elif ttype in DNB_TYPES:
                dnb += 1
                if sid:
                    sess_dnb.add(sid)
        both = len(sess_dna & sess_dnb)
        return {
            "active_reads": active_total,
            "dn_a_scene_reads": dna,
            "dn_b_state_reads": dnb,
            "dn_a_share_pct": round(100.0 * dna / max(1, dna + dnb), 1),
            "dn_b_share_pct": round(100.0 * dnb / max(1, dna + dnb), 1),
            "in_reply_to_rows": reply_rows,
            "active_sessions": len(active_sess),
            "dual_channel_sessions": both,
            "dual_channel_session_pct": round(100.0 * both / max(1, len(active_sess)), 1),
        }

    return {
        "all_time": _tally(None),
        "recent_window": {"sessions": len(recent_set), **_tally(recent_set)},
    }


def compute_report(root: Path = _ROOT) -> dict[str, Any]:
    data, errata = load_archive(root)
    bstate = belief_state.compute_belief_state(data=data, root=Path(root))
    inh_act = associations.inhibited_activation(data, errata=errata)
    inhib_map = associations.receiver_inhibition(data, errata=errata)

    # Gate 1 metrics
    triads = associations.closed_loop_summary(data)
    non_fusing = associations.non_fusing_link_stats(data, errata=errata)
    temp_links = associations.temporal_cohort_links(data, window_days=1, limit=5)
    s3_cov: dict[str, dict[str, Any]] = {}
    for qid in belief_state.CORE_QUESTIONS:
        if qid not in data["questions"]:
            continue
        top15 = inspect_inquiry._candidate_materials_for_question(data, qid, errata=errata)[:15]
        denom = len(top15)
        v_cnt = sum(
            1 for m in top15
            if ((data["materials"][m].get("verification") or {}).get("status")) == "verified"
        )
        e_cnt = sum(
            1 for m in top15 if inspect_inquiry._has_live_contradicted_erratum(m, errata)
        )
        s3_cov[qid] = {
            "window": denom,
            "verified": v_cnt,
            "verified_pct": round(100.0 * v_cnt / max(1, denom), 1),
            "live_errata": e_cnt,
        }

    # Gate 2 metrics
    unique_hyps: dict[str, dict[str, Any]] = {}
    core_belief: dict[str, dict[str, Any]] = {}
    hist_sat = {
        r["question_id"]: bool(r["saturated"])
        for r in (bstate.get("saturation", {}).get("questions") or [])
    }
    gate_sat = {
        r["question_id"]: bool(r["saturated"])
        for r in (bstate.get("gated_saturation", {}).get("questions") or [])
    }
    for qid, qs in bstate["questions"].items():
        for h in qs.get("hypotheses") or []:
            unique_hyps.setdefault(h["hypothesis_id"], h)
        if qid in belief_state.CORE_QUESTIONS:
            p_pair = qs.get("top_competing_pair")
            g_pair = qs.get("gated_top_pair")
            core_belief[qid] = {
                "historical_saturated": hist_sat.get(qid, False),
                "gated_saturated": gate_sat.get(qid, False),
                "entropy_bits": qs.get("entropy_bits", 0.0),
                "gated_entropy_bits": qs.get("gated_entropy_bits", 0.0),
                "historical_eig": p_pair["expected_info_gain"] if p_pair else 0.0,
                "gated_eig": g_pair["expected_info_gain"] if g_pair else 0.0,
                "gated_top_pair": (
                    f"{g_pair['left_hypothesis_id']} ({g_pair['left_posterior']*100:.1f}%) vs "
                    f"{g_pair['right_hypothesis_id']} ({g_pair['right_posterior']*100:.1f}%)"
                    if g_pair
                    else None
                ),
                "orphan_over_narrowed_count": len(qs.get("orphan_over_narrowed_ids") or []),
            }

    inh_counts = Counter(h.get("inhibition_state", "unknown") for h in unique_hyps.values())
    orphans = sorted(
        (h for h in unique_hyps.values() if h.get("inhibition_state") == "orphan_over_narrowed"),
        key=lambda h: (-int((h.get("verdict_counts") or {}).get("narrows_scope", 0)), h["hypothesis_id"]),
    )
    postdated_hyps = sum(1 for h in unique_hyps.values() if h.get("postdated_heir_transfers", 0) > 0)
    postdated_total = sum(int(h.get("postdated_heir_transfers", 0)) for h in unique_hyps.values())
    rival_heir_total = sum(int(h.get("rival_heir_transfers", 0)) for h in unique_hyps.values())

    cat_violations = [
        f"{tt}:{tid}"
        for (tt, tid), info in inhib_map.items()
        if tt == "motif"
        or (tt == "question" and (data["questions"].get(tid) or {}).get("status") == "open")
    ]
    mat_violations = [
        tid
        for (tt, tid), _info in inhib_map.items()
        if tt == "material" and not inspect_inquiry._has_live_contradicted_erratum(tid, errata)
    ]
    dampened = sorted(
        (v for v in inh_act.values() if v["gaba_gain"] < 1.0 and v["raw_salience"] >= 1.0),
        key=lambda v: -(v["raw_salience"] - v["inhibited_salience"]),
    )
    intrusions = sorted(
        (v for v in inh_act.values() if v["unresolved_intrusion"]),
        key=lambda v: -v["raw_salience"],
    )
    suppressed_items = sorted(
        f"{tt}:{tid}" for (tt, tid), info in inhib_map.items() if info.get("suppressed")
    )
    cohorts = cohort_suppression_audit(data, errata)

    # Gate 3 metrics
    upgrades = upgrade_candidates(data, limit=10)
    dups = duplicate_identifier_summary(data["materials"])
    dn_bal = dn_channel_balance(data)
    prov = bstate.get("provenance_verification") or {}

    return {
        "gate_1_binding_and_completion": {
            "closed_loops": triads,
            "non_fusing_links": non_fusing,
            "temporal_cohorts_1d": {
                "dated_active_sessions": temp_links["dated_active_sessions"],
                "linked_session_pairs": temp_links["linked_session_pairs"],
            },
            "packet_s3_top15_verification": s3_cov,
        },
        "gate_2_receiver_local_inhibition": {
            "core_questions": core_belief,
            "postdated_fallback_hypotheses": postdated_hyps,
            "postdated_fallback_transfers_blocked": postdated_total,
            "rival_as_heir_transfers_blocked": rival_heir_total,
            "hypothesis_inhibition_states": dict(inh_counts),
            "orphan_over_narrowed": [
                {
                    "hypothesis_id": h["hypothesis_id"],
                    "narrows_scope": int((h.get("verdict_counts") or {}).get("narrows_scope", 0)),
                    "supports": int((h.get("verdict_counts") or {}).get("supports", 0)),
                    "title": h.get("title", "")[:70],
                }
                for h in orphans[:10]
            ],
            "orphan_over_narrowed_total": len(orphans),
            "dampened_salient_records": len(dampened),
            "suppress_retrieval_active": suppressed_items,
            "top_dampened": [
                {
                    "target": f"{v['type']}:{v['id']}",
                    "raw_salience": v["raw_salience"],
                    "inhibited_salience": v["inhibited_salience"],
                    "gaba_gain": v["gaba_gain"],
                    "reasons": v["inhibition_reasons"],
                }
                for v in dampened[:6]
            ],
            "unresolved_intrusions": [
                {
                    "target": f"{v['type']}:{v['id']}",
                    "raw_salience": v["raw_salience"],
                    "contested": int((v.get("by_reading") or {}).get("contested", 0)),
                }
                for v in intrusions[:8]
            ],
            "category_preservation_ok": len(cat_violations) == 0,
            "non_shared_material_erasure_ok": len(mat_violations) == 0,
            "cohort_suppression": cohorts,
        },
        "gate_3_reality_and_attribution": {
            "materials": {
                "total": upgrades["total_materials"],
                "status_counts": upgrades["status_counts"],
                "editorial_verification_overlays": upgrades["material_overlay_decisions"],
                "non_verified_with_fulltext_read_hint": upgrades["non_verified_with_fulltext_read_hint"],
                "psc_cited_non_verified_materials": upgrades["psc_cited_non_verified_materials"],
            },
            "psc_verification": prov,
            "write_gates_enforced_from": validate_seed.THREE_GATES_RULE_FROM,
            "duplicate_identifiers": dups,
            "top_upgrade_candidates": upgrades["top_candidates"][:8],
            "dn_channel_balance": dn_bal,
        },
    }


def check_invariants(root: Path = _ROOT, *, today: datetime.date | None = None) -> list[str]:
    """Verify structural Three-Gates invariants without policing inquiry aesthetics."""
    data, errata = load_archive(root)
    errors: list[str] = []
    validate_seed.check_psc_verification_gate(
        data["evaluations"], data["materials"], errors, today=today
    )
    validate_seed.check_material_duplicate_identifiers(
        data["materials"], errors, today=today
    )
    validate_seed.check_evaluation_descendant_collision(
        data["evaluations"], data["hypotheses"], errors, today=today
    )
    bstate = belief_state.compute_belief_state(data=data, root=Path(root))
    for qid, qs in bstate["questions"].items():
        hyps = qs.get("hypotheses") or []
        if not hyps:
            continue
        probs = [float(h.get("gated_posterior", -1.0)) for h in hyps]
        if any(p < 0.0 or p > 1.0 for p in probs):
            errors.append(f"belief_state:{qid}: gated_posterior outside [0, 1]")
        total_p = sum(probs)
        # Rounded to 4 decimals per entry; tolerance scales cleanly with hypothesis count.
        if abs(total_p - 1.0) > max(0.01, 0.0005 * len(hyps)):
            errors.append(f"belief_state:{qid}: gated_posterior sum {total_p:.4f} != 1.0")
    inhib = associations.receiver_inhibition(data, errata=errata)
    for (tt, tid), info in inhib.items():
        if tt == "motif":
            errors.append(f"associations: category motif {tid!r} must never be inhibited ({info})")
        elif tt == "question" and (data["questions"].get(tid) or {}).get("status") == "open":
            errors.append(f"associations: open question {tid!r} must never be inhibited ({info})")
        elif tt == "material" and not inspect_inquiry._has_live_contradicted_erratum(tid, errata):
            errors.append(
                f"associations: material {tid!r} inhibited without own live erratum ({info})"
            )
    return errors


def render_summary(report: dict[str, Any]) -> str:
    g1 = report["gate_1_binding_and_completion"]
    g2 = report["gate_2_receiver_local_inhibition"]
    g3 = report["gate_3_reality_and_attribution"]
    cl = g1["closed_loops"]
    nf = g1["non_fusing_links"]
    tc = g1["temporal_cohorts_1d"]
    lines = [
        "=== Three-Gates Memory, Inhibition & Reality-Monitoring Report ===",
        "",
        "[Gate 1] 束ね・閉ループ補完・時間窓非融合連結 (Horner 2015 / Cai 2016 / Vaz 2019)",
        f"  閉ループ三角形 (co_read>=2) : {cl['closed_triads']:,} 個 (未架橋辺あり {cl['triads_with_unbridged_edge']:,} / 全辺架橋 {cl['fully_bridged_triads']:,})",
        f"  非融合素材連結 (評価>=2回)  : {nf['cross_hypothesis_materials']}/{nf['multi_eval_materials']} ({nf['cross_hypothesis_share_pct']}%) が複数仮説を連結 / 片方限定後の他方無傷率 {nf['non_shared_erasure_pct']}%",
        f"  実日付1日窓アンサンブル対   : {tc['linked_session_pairs']:,} 対 ({tc['dated_active_sessions']} セッション)",
        "  パケット §3 先頭15件の照合率: "
        + " / ".join(
            f"{q}={v['verified']}/{v['window']} ({v['verified_pct']}%, 生訂正{v['live_errata']})"
            for q, v in g1["packet_s3_top15_verification"].items()
        ),
        "",
        "[Gate 2] 受け手局所の抑制・並列鎮静・遡及移流遮断 (Wimber 2015 / Gagnepain 2017 / Schmitz 2017)",
        f"  P_gate 遮断件数             : 後付けフォールバック移流 {g2['postdated_fallback_transfers_blocked']} 件 ({g2['postdated_fallback_hypotheses']} 仮説) / 対立相手=子移流 {g2['rival_as_heir_transfers_blocked']} 件",
        f"  仮説抑制状態内訳            : {g2['hypothesis_inhibition_states']}",
        f"  過限定・子仮説0 (継承待ち)  : {g2['orphan_over_narrowed_total']} 件"
        + (
            " (上位: "
            + ", ".join(
                f"{o['hypothesis_id']}[{o['narrows_scope']}N/{o['supports']}S]"
                for o in g2["orphan_over_narrowed"][:4]
            )
            + ")"
            if g2["orphan_over_narrowed"]
            else ""
        ),
    ]
    for qid, qb in g2["core_questions"].items():
        lines.append(
            f"  {qid} P -> P_gate             : H {qb['entropy_bits']:.3f}b({'飽和' if qb['historical_saturated'] else '非飽和'}) -> "
            f"{qb['gated_entropy_bits']:.3f}b({'飽和' if qb['gated_saturated'] else '非飽和'}) | "
            f"EIG {qb['historical_eig']:.4f} -> {qb['gated_eig']:.4f} | 推奨対: {qb['gated_top_pair']}"
        )
    lines.append(
        f"  顕著性局所減衰 (raw>=1.0)   : {g2['dampened_salient_records']} 件減衰 / "
        f"suppress_retrieval={len(g2['suppress_retrieval_active'])} 件 / "
        f"未決着侵入={len(g2['unresolved_intrusions'])} 件 / "
        f"カテゴリ温存={'OK' if g2['category_preservation_ok'] else 'NG'}"
    )
    cs = g2["cohort_suppression"]["cohorts"]
    ns_c = cs["narrows_scope"]
    er_c = cs["errata_contradicted"]
    lines.append(
        f"  前後{g2['cohort_suppression']['window_sessions']}回コホート再浮上実測  : "
        f"narrows_scope 前{ns_c['mean_pre_rate_per_session']:.3f}->後{ns_c['mean_post_rate_per_session']:.3f}/回 "
        f"(減{ns_c['decreased']}/増{ns_c['increased_intrusion']}) | "
        f"contradicted訂正 前{er_c['mean_pre_rate_per_session']:.3f}->後{er_c['mean_post_rate_per_session']:.3f}/回 "
        f"(減{er_c['decreased']}/増{er_c['increased_intrusion']})"
    )

    mt = g3["materials"]
    pv = g3["psc_verification"]
    dp = g3["duplicate_identifiers"]
    rw = g3["dn_channel_balance"]["recent_window"]
    lines.extend(
        [
            "",
            "[Gate 3] 現実識別・来歴オーバーレイ・DN-A/DN-B二系統 (Garrison 2015 / Parvizi 2021 / Braga 2017 / DiNicola 2020)",
            f"  素材照合状態 ({mt['total']:,}件)     : {mt['status_counts']} (ED照合オーバーレイ {mt['editorial_verification_overlays']} 件)",
            f"  PSC 原典衝突照合率          : 全照合 {pv.get('psc_all_verified', 0)}/{pv.get('psc_total', 0)} "
            f"({pv.get('psc_all_verified_ratio', 0.0)*100:.1f}%) / 一部 {pv.get('psc_mixed_verified', 0)} / 未照合のみ {pv.get('psc_zero_verified', 0)} "
            f"(新規門発効: {g3['write_gates_enforced_from']})",
            f"  既収蔵昇格余地              : PSC引用の非verified {mt['psc_cited_non_verified_materials']} 件 / 全文言及あり非verified {mt['non_verified_with_fulltext_read_hint']} 件",
            f"  識別子重複 (歴史在庫)       : DOI {dp['doi']['distinct_duplicated']}組(+{dp['doi']['extra_rows']}行) / "
            f"PMCID {dp['pmcid']['distinct_duplicated']}組(+{dp['pmcid']['extra_rows']}行) / "
            f"PMID {dp['pmid']['distinct_duplicated']}組(+{dp['pmid']['extra_rows']}行)",
            f"  直近{rw['sessions']}回 DN-A / DN-B 比率  : DN-A(場面/素材) {rw['dn_a_share_pct']}% vs DN-B(状態/ノート/仮説) {rw['dn_b_share_pct']}% "
            f"| 両系統併用 {rw['dual_channel_session_pct']}% | in_reply_to {rw['in_reply_to_rows']} 行",
            "",
            "  注意: 観測値は次の読解・照合・条件付き継承を選ぶための鏡であり、件数目標ではありません（docs/mode-rotation-triggers.md §2）。",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=_ROOT, help="repository root")
    parser.add_argument("--check", action="store_true", help="verify structural Three-Gates invariants (exit 1 on failure)")
    parser.add_argument("--check-source", action="store_true", help="Gate 3: check candidate DOI/PMID/PMCID/URL/title against archived materials")
    parser.add_argument("--doi", default="", help="candidate DOI for --check-source")
    parser.add_argument("--pmid", default="", help="candidate PubMed ID for --check-source")
    parser.add_argument("--pmcid", default="", help="candidate PMC ID (e.g. PMC4506998) for --check-source")
    parser.add_argument("--url", default="", help="candidate primary URL for --check-source")
    parser.add_argument("--title", default="", help="candidate source title for --check-source")
    parser.add_argument("--fail-on-match", action="store_true", help="exit 1 if --check-source finds an exact identifier match")
    parser.add_argument("--upgrade-candidates", action="store_true", help="Gate 3: list high-leverage non-verified materials to re-verify via editorial_decisions")
    parser.add_argument("--cohort-suppression", action="store_true", help="Gate 2: run exposure-matched pre/post re-citation cohort audit")
    parser.add_argument("--window-sessions", type=int, default=40, help="session window for --cohort-suppression (default 40)")
    parser.add_argument("--complete", nargs="+", metavar="ID", help="Gate 1: closed-loop A–B–C–A completions with titles")
    parser.add_argument("--limit", type=int, default=15, help="max items to display (default 15)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    if args.check:
        failures = check_invariants(args.root)
        if args.json:
            print(json.dumps({"ok": not failures, "failures": failures}, ensure_ascii=False, indent=2))
            return 1 if failures else 0
        if failures:
            print("FAIL: Three-Gates structural invariant violation(s):", file=sys.stderr)
            for msg in failures:
                print(f"  - {msg}", file=sys.stderr)
            return 1
        print(
            f"PASS: Three-Gates invariants hold (PSC/dedup/lineage gates active from "
            f"{validate_seed.THREE_GATES_RULE_FROM}, P_gate normalized, category & non-fusing link preservation OK)"
        )
        return 0

    if args.check_source:
        data, _err = load_archive(args.root)
        res = check_source(
            data["materials"],
            doi=args.doi,
            pmid=args.pmid,
            pmcid=args.pmcid,
            url=args.url,
            title=args.title,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS: {res['status']}  (queried={res['queried_identifiers']})")
            for m in res["exact_identifier_matches"]:
                print(
                    f"  EXACT  {m['material_id']} [{m['verification_status']}] "
                    f"matched={m['matched_on']}  {m['title'][:75]}"
                )
            for m in res["similar_title_matches"]:
                print(
                    f"  TITLE  {m['material_id']} [{m['verification_status']}] "
                    f"sim={m['title_similarity']:.2f}  {m['title'][:75]}"
                )
            if res["editorial_upgrade_template"]:
                print(
                    "  HINT : Cite the existing MAT-* directly; if you verified its full text, "
                    "append an editorial_decisions overlay (target.type='material', status='verified')."
                )
        if args.fail_on_match and res["exact_identifier_matches"]:
            return 1
        return 0

    if args.upgrade_candidates:
        data, _err = load_archive(args.root)
        up = upgrade_candidates(data, limit=args.limit)
        if args.json:
            print(json.dumps(up, ensure_ascii=False, indent=2))
        else:
            print(
                f"=== Gate 3: non-verified materials ranked by PSC verification leverage "
                f"(top {min(args.limit, len(up['top_candidates']))}) ==="
            )
            for r in up["top_candidates"]:
                print(
                    f"  {r['material_id']} [{r['current_status']:18s}] "
                    f"1-step_PSC={r['psc_single_blocker_rows']} PSC={r['psc_citations']} "
                    f"ft_hints={r['fulltext_hint_sessions']}  {r['title'][:58]}"
                )
        return 0

    if args.cohort_suppression:
        data, errata = load_archive(args.root)
        cs = cohort_suppression_audit(data, errata, window_sessions=args.window_sessions)
        if args.json:
            print(json.dumps(cs, ensure_ascii=False, indent=2))
        else:
            print(
                f"=== Gate 2: pre/post re-citation cohort audit "
                f"(window={cs['window_sessions']} sessions across {cs['total_sessions']} total) ==="
            )
            for name, c in cs["cohorts"].items():
                ratio = f"{c['post_to_pre_ratio']:.2f}x" if c["post_to_pre_ratio"] is not None else "n/a"
                print(
                    f"  {name:26s} n={c['measured_targets']:>3}/{c['total_targets']:<3}  "
                    f"pre={c['mean_pre_rate_per_session']:.4f} -> post={c['mean_post_rate_per_session']:.4f}/sess ({ratio})  "
                    f"dec={c['decreased']} inc={c['increased_intrusion']} quiet={c['quiet_both']}"
                )
        return 0

    if args.complete:
        data, errata = load_archive(args.root)
        comps = associations.closed_loop_completions(
            data, args.complete, errata=errata, limit=args.limit
        )
        if args.json:
            print(json.dumps(comps, ensure_ascii=False, indent=2))
        else:
            print(f"=== Gate 1: closed-loop completions for {args.complete} ===")
            for item in comps:
                t = item["target"]
                tt, tid = t["type"], t["id"]
                title = ""
                if tt == "material":
                    m = data["materials"].get(tid, {})
                    vs = ((m.get("verification") or {}).get("status")) or "?"
                    title = f"{m.get('title', '')[:55]} [{vs}]"
                elif tt in ("fragment", "hypothesis"):
                    coll = "fragments" if tt == "fragment" else "hypotheses"
                    title = str(data[coll].get(tid, {}).get("title", ""))[:60]
                elif tt == "note":
                    title = str(data["notes"].get(tid, {}).get("path", ""))[:60]
                print(
                    f"  score={item['score']:6.2f} loops={item['closed_loops']} gain={item['gaba_gain']:.2f}  "
                    f"{tt}:{tid}  {title}"
                )
        return 0

    report = compute_report(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_summary(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
