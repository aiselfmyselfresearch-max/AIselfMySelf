#!/usr/bin/env python3
"""Measure association and salience in the archive's own read traces.

Human associative memory does not store items, it stores what fires together.
This repository already has the raw material for the same measurement:
``state/read_log*`` records, per session, which record was read and *how*
(``quoted`` / ``summarized`` / ``interpreted`` / ``reinterpreted`` / ``contested``
/ ``used_as_context`` / ``counted``).  Two records activated in the same session
are co-activated; repeated co-activation is what a relation edge should express.

So this tool answers three questions the ledger cannot answer by inspection:

  1. **共起 (co-activation)** — which pairs are read together again and again but
     have no ``relations`` edge?  These are bridging candidates that the archive
     already behaves as if it believed, without having written them down.
  2. **顕著性 (salience)** — which records carry the most interpretive weight,
     counting *how* they were read (a ``contested`` row is not a ``counted`` row)
     and how recently, in the only time axis this archive can trust: ledger
     insertion order.  Dates are not used, because the internal chronology labels
     and the real execution dates disagree (see docs/memory-architecture.md §4).
  3. **減衰 (decay)** — which load-bearing records (``selected`` fragments,
     ``open`` questions nobody has responded to) have not been activated for a
     long stretch of the log?

None of this is an obligation.  ``prompts/start.md`` is explicit that unread
holdings are margin, not debt, and that counts are not success criteria; every
list here is a recommendation the next session may decline, and declining it is
not a liability.  ``used_as_context`` and ``counted`` rows are excluded from
co-activation by default because passing a record through a context window and
counting it in an audit are not acts of association; ``--include-passive`` adds
them back for comparison.

Usage:
  python3 tools/associations.py                       # summary + top lists
  python3 tools/associations.py --co-read --limit 30  # bridging candidates
  python3 tools/associations.py --salience            # activation ranking
  python3 tools/associations.py --decay               # long-unactivated records
  python3 tools/associations.py --write-map           # map/associations.md (untracked)
  python3 tools/associations.py --json
"""
from __future__ import annotations

import argparse
import itertools
import datetime
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

_ROOT = Path(__file__).resolve().parents[1]
# Put tools/ on sys.path before the flat imports below, so this module works both
# as a script and when a test imports it as ``tools.associations``.
sys.path.insert(0, str(_ROOT / "tools"))

import ledger_io  # noqa: E402
from validate_seed import COLLECTIONS, ROOT  # noqa: E402

# How much interpretive work each ``reading`` value represents.  The ordering is
# the archive's own: contesting or re-reading a record changes a stance, quoting
# or summarising it carries it forward, using it as context does not engage it,
# and counting it in an audit engages nothing but a regular expression.
READING_WEIGHTS: dict[str, float] = {
    "contested": 3.0,
    "reinterpreted": 3.0,
    "interpreted": 2.0,
    "quoted": 1.0,
    "summarized": 1.0,
    "used_as_context": 0.5,
    "counted": 0.25,
}
ACTIVE_READINGS = frozenset({"quoted", "summarized", "interpreted", "reinterpreted", "contested"})
PASSIVE_READINGS = frozenset({"used_as_context", "counted"})

DEFAULT_HALF_LIFE = 500.0  # in read_log rows, not days


def load(root: Path = ROOT) -> dict[str, dict[str, dict[str, Any]]]:
    errors: list[str] = []
    data: dict[str, dict[str, dict[str, Any]]] = {}
    for name, (filename, id_key, _schema) in COLLECTIONS.items():
        base = Path(root) / "state" / filename
        if not base.is_file() and not ledger_io.shard_dir(base).is_dir():
            data[name] = {}
            continue
        data[name] = ledger_io.load_jsonl_union(base, id_key, errors, root=Path(root))
    err_base = Path(root) / "state" / "errata.jsonl"
    if err_base.is_file() or ledger_io.shard_dir(err_base).is_dir():
        data["errata"] = ledger_io.load_jsonl_union(err_base, "errata_id", errors, root=Path(root))
    else:
        data["errata"] = {}
    if errors:
        raise ValueError("; ".join(errors))
    return data


# ---------------------------------------------------------------------------
# co-activation
# ---------------------------------------------------------------------------

def _pair_key(left: tuple[str, str], right: tuple[str, str]) -> tuple[tuple[str, str], tuple[str, str]]:
    return (left, right) if left <= right else (right, left)


def _one_line(value: Any, limit: int = 70) -> str:
    """Collapse a title or question to one line so it can sit in a table cell."""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def relation_pairs(data: dict[str, dict[str, dict[str, Any]]]) -> dict[tuple[tuple[str, str], tuple[str, str]], list[str]]:
    """Existing interpretive edges as an undirected pair -> relation ids map."""
    edges: dict[tuple[tuple[str, str], tuple[str, str]], list[str]] = defaultdict(list)
    for relation in data.get("relations", {}).values():
        left, right = relation.get("left"), relation.get("right")
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        lkey = (str(left.get("type")), str(left.get("id")))
        rkey = (str(right.get("type")), str(right.get("id")))
        if lkey == rkey:
            continue
        edges[_pair_key(lkey, rkey)].append(str(relation.get("relation_id")))
    return dict(edges)


def co_read(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    include_passive: bool = False,
    min_sessions: int = 2,
) -> list[dict[str, Any]]:
    """Pairs activated inside one session, aggregated over sessions.

    Insertion order of ``read_log`` (base file, then shards sorted by name) is
    preserved by ``ledger_io``, so the row index is a stable time axis.
    """
    allowed = ACTIVE_READINGS | (PASSIVE_READINGS if include_passive else set())
    by_session: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in data.get("read_log", {}).values():
        reading = row.get("reading")
        target = row.get("target")
        if reading not in allowed or not isinstance(target, dict):
            continue
        session = str(row.get("session_id", ""))
        if not session:
            continue
        key = (str(target.get("type")), str(target.get("id")))
        if key not in by_session[session]:
            by_session[session].append(key)

    sessions_by_pair: dict[Any, set[str]] = defaultdict(set)
    rows_by_pair: Counter[Any] = Counter()
    for session, keys in by_session.items():
        for left, right in itertools.combinations(sorted(keys), 2):
            pair = _pair_key(left, right)
            sessions_by_pair[pair].add(session)
            rows_by_pair[pair] += 1

    edges = relation_pairs(data)
    out: list[dict[str, Any]] = []
    for pair, sessions in sessions_by_pair.items():
        if len(sessions) < min_sessions:
            continue
        out.append(
            {
                "left": {"type": pair[0][0], "id": pair[0][1]},
                "right": {"type": pair[1][0], "id": pair[1][1]},
                "sessions": len(sessions),
                "co_reads": rows_by_pair[pair],
                "bridged": bool(edges.get(pair)),
                "relation_ids": sorted(edges.get(pair, []))[:4],
                "session_ids": sorted(sessions)[:6],
            }
        )
    out.sort(key=lambda item: (-item["sessions"], -item["co_reads"], item["left"]["id"], item["right"]["id"]))
    return out


# ---------------------------------------------------------------------------
# salience and decay
# ---------------------------------------------------------------------------

def activation(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    half_life: float = DEFAULT_HALF_LIFE,
    include_passive: bool = True,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Weighted, recency-decayed activation per record.

    ``decay = 0.5 ** (rows_after_last_read / half_life)``.  The unit is read_log
    rows, deliberately: this archive's ``created_at`` values mix internal
    chronology labels with real execution dates, so a day count would be a
    fiction, while the row order is exactly the order in which sessions wrote.
    """
    raw_rows = list(data.get("read_log", {}).values())
    sessions_map = data.get("sessions") or {}
    if sessions_map:
        import date_axis

        curated = date_axis.curated_real_dates(data.get("notes") or {})
        sess_dates: dict[str, str] = {}
        for sid, srec in sessions_map.items():
            real_d, _src = date_axis.session_real_date(sid, srec, curated=curated)
            if real_d:
                sess_dates[sid] = real_d
        if sess_dates:
            rows = [
                row
                for _ord, row in sorted(
                    enumerate(raw_rows),
                    key=lambda pair: (sess_dates.get(str(pair[1].get("session_id", "")), "0000-00-00"), pair[0]),
                )
            ]
        else:
            rows = raw_rows
    else:
        rows = raw_rows
    total = len(rows)
    allowed = ACTIVE_READINGS | (PASSIVE_READINGS if include_passive else set())
    acc: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        reading = row.get("reading")
        target = row.get("target")
        if reading not in allowed or not isinstance(target, dict):
            continue
        weight = READING_WEIGHTS.get(str(reading), 0.0)
        decay = 0.5 ** ((total - 1 - index) / half_life) if half_life > 0 else 1.0
        key = (str(target.get("type")), str(target.get("id")))
        entry = acc.setdefault(
            key,
            {
                "type": key[0],
                "id": key[1],
                "rows": 0,
                "active_rows": 0,
                "sessions": set(),
                "by_reading": Counter(),
                "raw_weight": 0.0,
                "salience": 0.0,
                "first_row": index,
                "last_row": index,
            },
        )
        entry["rows"] += 1
        if reading in ACTIVE_READINGS:
            entry["active_rows"] += 1
        entry["sessions"].add(str(row.get("session_id", "")))
        entry["by_reading"][str(reading)] += 1
        entry["raw_weight"] += weight
        entry["salience"] += weight * decay
        entry["last_row"] = index
    for entry in acc.values():
        entry["sessions"] = len(entry["sessions"])
        entry["by_reading"] = dict(entry["by_reading"].most_common())
        entry["rows_since_last_read"] = max(0, total - 1 - entry["last_row"])
        del entry["first_row"]
        del entry["last_row"]
    return acc


def load_bearing(
    data: dict[str, dict[str, dict[str, Any]]],
    acc: dict[tuple[str, str], dict[str, Any]],
    *,
    cold_threshold: float | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Load-bearing records, split into (cold, warm, never-read).

    Load-bearing means the archive's own status marks the record as one a future
    reading is entitled to expect: a ``selected`` or ``held`` fragment, or an
    ``open`` question no ``responds_to`` / ``reframes`` edge has answered.  A
    paused or rejected record is excluded because an editorial overlay already
    retired it — that is forgetting by overlay, and this tool does not undo it.

    The three states are reported separately so that none of them is silently
    folded into another: ``cold`` records were engaged and then went quiet,
    ``warm`` records were engaged recently enough not to be a signal, and
    ``never`` records have no ``read_log`` row at all.  Only ``cold`` is listed
    in full; ``never`` is counted, because prompts/start.md is explicit that
    unread holdings are margin and a long list of them reads as debt.

    The horizon defaults to a quarter of the log (never less than 100 rows) so
    that "long unactivated" scales with the archive instead of being a fixed
    date.  Pass ``cold_threshold`` to override it.
    """
    responded: set[str] = set()
    for relation in data.get("relations", {}).values():
        if relation.get("relation_type") in {"responds_to", "reframes"}:
            right = relation.get("right", {})
            if isinstance(right, dict) and right.get("type") == "question":
                responded.add(str(right.get("id")))

    candidates: list[dict[str, Any]] = []
    for fid, fragment in data.get("fragments", {}).items():
        status = fragment.get("status")
        if status in ("selected", "held"):
            candidates.append(
                {
                    "type": "fragment",
                    "id": fid,
                    "why": str(status),
                    "title": _one_line(fragment.get("title", "")),
                }
            )
    for qid, question in data.get("questions", {}).items():
        if question.get("status", "open") != "open" or qid in responded:
            continue
        candidates.append(
            {
                "type": "question",
                "id": qid,
                "why": "open・未応答",
                "title": _one_line(question.get("question", "")),
            }
        )

    horizon = max(100.0, len(acc) / 4.0) if cold_threshold is None else float(cold_threshold)
    cold: list[dict[str, Any]] = []
    warm: list[dict[str, Any]] = []
    never: list[dict[str, Any]] = []
    for item in candidates:
        entry = acc.get((item["type"], item["id"]))
        item["rows"] = entry["rows"] if entry else 0
        item["active_rows"] = entry["active_rows"] if entry else 0
        item["sessions"] = entry["sessions"] if entry else 0
        item["salience"] = round(entry["salience"], 3) if entry else 0.0
        item["rows_since_last_read"] = entry["rows_since_last_read"] if entry else None
        if entry is None:
            never.append(item)
        elif item["rows_since_last_read"] > horizon:
            cold.append(item)
        else:
            warm.append(item)
    cold.sort(key=lambda item: (-(item["rows_since_last_read"] or 0), item["id"]))
    warm.sort(key=lambda item: (-(item["rows_since_last_read"] or 0), item["id"]))
    never.sort(key=lambda item: (item["type"], item["id"]))
    return cold, warm, never


def summarize(data: dict[str, dict[str, dict[str, Any]]], co: list[dict[str, Any]], acc: dict[Any, dict[str, Any]]) -> dict[str, Any]:
    rows = data.get("read_log", {})
    readings = Counter(str(row.get("reading")) for row in rows.values())
    passive = sum(readings[name] for name in PASSIVE_READINGS)
    unbridged = [item for item in co if not item["bridged"]]
    by_type = Counter(item["type"] for item in acc.values())
    return {
        "read_log_rows": len(rows),
        "by_reading": dict(readings.most_common()),
        "passive_share_pct": round(passive * 100.0 / len(rows), 1) if rows else 0.0,
        "distinct_targets": len(acc),
        "targets_by_type": dict(by_type.most_common()),
        "co_read_pairs_2plus_sessions": len(co),
        "co_read_pairs_bridged": len(co) - len(unbridged),
        "co_read_pairs_unbridged": len(unbridged),
        "relations": len(data.get("relations", {})),
    }


# ---------------------------------------------------------------------------
# Gate 2: receiver-local inhibition & reactive parallel salience dampening
# (Wimber et al. 2015; Gagnepain et al. 2017; Schmitz et al. 2017)
# ---------------------------------------------------------------------------

# Category records are never dampened by item-level suppression (Wimber 2015),
# and materials never inherit inhibition from a narrowed/refuted hypothesis that
# cited them (Cai et al. 2016: linking without shared erasure).
CATEGORY_TYPES = frozenset({"motif"})
INHIBITABLE_ERRATA_TYPES = frozenset({"material", "fragment", "note", "hypothesis"})
_TYPE_TO_COLLECTION = {
    "question": "questions",
    "motif": "motifs",
    "material": "materials",
    "fragment": "fragments",
    "session": "sessions",
    "note": "notes",
    "hypothesis": "hypotheses",
    "evaluation": "evaluations",
    "erratum": "errata",
    "editorial_decision": "editorial_decisions",
}
_ISO_DAY_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")
_STAMP_ID_RE = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-(\d{4})(\d{2})(\d{2})-")


def _norm_claim(text: Any) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(text or "")).split()).casefold()


def _is_live_contradicted_erratum(rec: dict[str, Any]) -> bool:
    """Matches ``belief_state.errata_is_live_correction``: contradicted and not withdrawn.

    In an append-only ledger ``annotated`` / ``corrected_by`` records who placed a
    notice beside the row, not that the row itself was rewritten; only ``withdrawn``
    retracts the correction.
    """
    if rec.get("status") == "withdrawn":
        return False
    return rec.get("verdict") == "contradicted"


def receiver_inhibition(
    data: dict[str, dict[str, dict[str, Any]]],
    errata: dict[str, dict[str, Any]] | None = None,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Compute receiver-local inhibitory gain per ledger target without mutating rows.

    Returns only targets with ``gaba_gain < 1.0`` (default for unlisted targets is
    ``gaba_gain = 1.0, suppressed = False``).  Enforces three biological invariants:

    1. **Item-specific dampening, category preservation** (Wimber et al. 2015):
       ``motif`` and ``open`` ``question`` records never inherit suppression from
       suppressed or refuted items attached to them.
    2. **Non-shared erasure across co-linked materials** (Cai et al. 2016):
       ``material`` rows are dampened only by live contradicted errata naming that
       material itself, never by the narrowing or refutation of a hypothesis that
       cited it.
    3. **Receiver-local GABA gate** (Schmitz et al. 2017): ledger history stays
       intact; inhibition acts solely at retrieval / salience projection time.
    """
    err_map = data.get("errata", {}) if errata is None else errata
    gains: dict[tuple[str, str], float] = {}
    reasons: dict[tuple[str, str], list[str]] = defaultdict(list)
    suppressed_keys: set[tuple[str, str]] = set()

    def _mul(key: tuple[str, str], factor: float, reason: str) -> None:
        if key[0] in CATEGORY_TYPES:
            return
        gains[key] = gains.get(key, 1.0) * factor
        reasons[key].append(reason)

    # Editorial overlays on questions and fragments (paused/archived).
    for qid, q in data.get("questions", {}).items():
        st = q.get("status")
        if st in ("paused", "archived"):
            _mul(("question", qid), 0.20, f"question_{st}")
    for fid, f in data.get("fragments", {}).items():
        if f.get("status") == "archived":
            _mul(("fragment", fid), 0.20, "fragment_archived")

    # Superseded notes give way to their superseding note.
    superseded_notes: set[str] = set()
    for note in data.get("notes", {}).values():
        for sup_id in note.get("supersedes") or ():
            if isinstance(sup_id, str) and sup_id:
                superseded_notes.add(sup_id)
    for nid in sorted(superseded_notes):
        _mul(("note", nid), 0.25, "superseded_note")

    # Voided evaluation rows.
    voided_evals: set[str] = set()
    for erec in err_map.values():
        if (
            erec.get("weight_effect") == "void_row"
            and erec.get("subject_type") == "evaluation"
            and _is_live_contradicted_erratum(erec)
        ):
            sid = str(erec.get("subject_id") or "")
            if sid:
                voided_evals.add(sid)
                _mul(("evaluation", sid), 0.10, "voided_evaluation")

    # Hypothesis-level narrowing / refutation / scope handoff.
    hyps = data.get("hypotheses", {})
    children_of: dict[str, list[str]] = defaultdict(list)
    for hid, hyp in hyps.items():
        for pid in hyp.get("parent_hypothesis_ids") or ():
            if isinstance(pid, str) and pid in hyps:
                children_of[pid].append(hid)
    verdicts_by_hyp: dict[str, Counter[str]] = defaultdict(Counter)
    for eid, evl in data.get("evaluations", {}).items():
        if eid in voided_evals:
            continue
        th = evl.get("target_hypothesis_id")
        vd = evl.get("verdict")
        if isinstance(th, str) and isinstance(vd, str) and th in hyps:
            verdicts_by_hyp[th][vd] += 1

    for hid in hyps:
        vc = verdicts_by_hyp.get(hid)
        if not vc:
            continue
        sup = vc.get("supports", 0)
        nar = vc.get("narrows_scope", 0)
        ref = vc.get("refutes_unconditioned", 0)
        sub = vc.get("subsumes", 0)
        key = ("hypothesis", hid)
        if ref > 0 and sup == 0:
            _mul(key, 0.15, "refuted_unconditioned")
        elif ref > 0:
            _mul(key, 0.45, f"refuted_x{ref}")
        if sub > 0 and sup == 0:
            _mul(key, 0.25, "subsumed")
        if nar > sup:
            excess = nar - sup
            _mul(key, 1.0 / (1.0 + 0.35 * excess), f"narrowed_excess({nar}>{sup})")
            if nar >= 3 and children_of.get(hid):
                _mul(key, 0.75, "scope_handed_to_children")
        elif nar >= 3:
            _mul(key, 1.0 / (1.0 + 0.08 * nar), f"narrowed_x{nar}")

    # Live contradicted errata (deduplicated per addressee + normalized claim).
    errata_claims: dict[tuple[str, str], set[str]] = defaultdict(set)
    suppress_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
    for err_id, erec in err_map.items():
        if not _is_live_contradicted_erratum(erec):
            continue
        stype = erec.get("subject_type")
        sid = erec.get("subject_id")
        if stype is None and isinstance(erec.get("fragment_id"), str):
            stype = "fragment"
            sid = erec.get("fragment_id")
        if stype not in INHIBITABLE_ERRATA_TYPES or not isinstance(sid, str) or not sid:
            continue
        key = (stype, sid)
        dup_of = [d for d in (erec.get("duplicate_of") or ()) if isinstance(d, str) and d]
        claim_sig = sorted(dup_of)[0] if dup_of else _norm_claim(erec.get("claim"))
        errata_claims[key].add(claim_sig or err_id)
        if erec.get("weight_effect") == "suppress_retrieval":
            suppress_ids[key].append(err_id)

    for key, claims in errata_claims.items():
        if key in suppress_ids:
            suppressed_keys.add(key)
            _mul(key, 0.12, f"suppress_retrieval({','.join(sorted(suppress_ids[key]))})")
        else:
            n_claims = min(len(claims), 4)
            _mul(key, 0.65 ** n_claims, f"live_errata_x{len(claims)}")

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for key, raw_gain in gains.items():
        clamped = round(max(0.05, min(1.0, raw_gain)), 4)
        if clamped < 1.0 or key in suppressed_keys:
            out[key] = {
                "gaba_gain": clamped,
                "suppressed": key in suppressed_keys,
                "reasons": reasons[key],
            }
    return out


def inhibited_activation(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    errata: dict[str, dict[str, Any]] | None = None,
    half_life: float = DEFAULT_HALF_LIFE,
    include_passive: bool = True,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Activation modulated by receiver-local inhibition and parallel intrusion control.

    Preserves ``activation()`` untouched for historical stability and adds:
    * ``raw_salience`` / ``gaba_gain`` / ``inhibited_salience``: when a record has
      resolved inhibitory evidence (narrowing excess, refutation, superseded note,
      live contradicted errata, or explicit ``suppress_retrieval``), both its trace
      and its ``contested`` salience boost are dampened in parallel (Gagnepain 2017).
    * ``unresolved_intrusion``: True when ``contested >= 2`` and ``raw_salience >= 2.0``
      with little or no inhibitory resolution (``gaba_gain > 0.85``) — flagging items
      whose conflict keeps boosting exposure without yet receiving a scope verdict or
      correction (low-control intrusion signature).
    """
    base = activation(data, half_life=half_life, include_passive=include_passive)
    inhib = receiver_inhibition(data, errata=errata)
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for key, entry in base.items():
        info = inhib.get(key)
        gain = info["gaba_gain"] if info else 1.0
        suppressed = bool(info["suppressed"]) if info else False
        rlist = list(info["reasons"]) if info else []
        raw_sal = float(entry["salience"])
        inh_sal = round(raw_sal * gain, 4)
        contested_n = int((entry.get("by_reading") or {}).get("contested", 0))
        unresolved = (
            key[0] not in CATEGORY_TYPES
            and key[0] != "question"
            and contested_n >= 2
            and raw_sal >= 2.0
            and gain > 0.85
        )
        out[key] = {
            **entry,
            "raw_salience": raw_sal,
            "gaba_gain": gain,
            "inhibited_salience": inh_sal,
            "suppressed": suppressed,
            "inhibition_reasons": rlist,
            "unresolved_intrusion": unresolved,
        }
    return out


# ---------------------------------------------------------------------------
# Gate 1: closed-loop holistic completion (Horner et al. 2015) and
# temporal-window non-fusing ensemble linkage (Cai et al. 2016)
# ---------------------------------------------------------------------------

def resolve_target_spec(
    data: dict[str, dict[str, dict[str, Any]]], spec: str | tuple[str, str]
) -> tuple[str, str] | None:
    """Resolve ``'type:id'``, ``(type, id)``, or a bare ledger ID to ``(type, id)``."""
    if isinstance(spec, tuple) and len(spec) == 2:
        return (str(spec[0]), str(spec[1]))
    text = str(spec or "").strip()
    if not text:
        return None
    if ":" in text:
        ttype, tid = text.split(":", 1)
        if ttype in _TYPE_TO_COLLECTION and tid:
            return (ttype, tid)
    for ttype, cname in _TYPE_TO_COLLECTION.items():
        if text in (data.get(cname) or {}):
            return (ttype, text)
    return None


def closed_loop_completions(
    data: dict[str, dict[str, dict[str, Any]]],
    seed_targets: list[str | tuple[str, str]] | tuple[str | tuple[str, str], ...],
    *,
    errata: dict[str, dict[str, Any]] | None = None,
    include_passive: bool = False,
    min_sessions: int = 2,
    include_relations: bool = True,
    suppress_inhibited: bool = True,
    allowed_types: frozenset[str] | set[str] | None = None,
    exclude_ids: frozenset[str] | set[str] | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return unretrieved third elements ``C`` closing ``A–B–C–A`` loops for cue set ``S``.

    Models Horner et al. (2015) holistic pattern completion: an open chain
    ``A–B–C`` (where ``C`` links to only one cue, or where cues ``A`` and ``B``
    are themselves unlinked) does NOT qualify.  Every returned candidate ``C``
    participates in at least one closed triad ``(A, B, C)`` with ``A, B in S``
    and all three legs ``A–B``, ``A–C``, ``B–C`` present across ``co_read``
    (``>= min_sessions``) and, when ``include_relations`` is True, explicit
    ``relations``.  Coupled to Gate 2: records carrying ``suppress_retrieval``
    are excluded when ``suppress_inhibited`` is True, and remaining candidates
    are scaled by their receiver-local ``gaba_gain``.
    """
    seeds: list[tuple[str, str]] = []
    seen_seeds: set[tuple[str, str]] = set()
    for raw in seed_targets:
        resolved = resolve_target_spec(data, raw)
        if resolved and resolved not in seen_seeds:
            seen_seeds.add(resolved)
            seeds.append(resolved)
    if len(seeds) < 2:
        return []

    adj: dict[tuple[str, str], dict[tuple[str, str], float]] = defaultdict(dict)
    co_items = co_read(data, include_passive=include_passive, min_sessions=min_sessions)
    rel_map = relation_pairs(data)
    for item in co_items:
        u = (item["left"]["type"], item["left"]["id"])
        v = (item["right"]["type"], item["right"]["id"])
        w = float(item["sessions"])
        adj[u][v] = adj[u].get(v, 0.0) + w
        adj[v][u] = adj[v].get(u, 0.0) + w
    if include_relations:
        for (u, v), rids in rel_map.items():
            bonus = 1.5 * min(len(rids), 3)
            adj[u][v] = adj[u].get(v, 0.0) + bonus
            adj[v][u] = adj[v].get(u, 0.0) + bonus
        # Include explicit belief-layer bindings (hypotheses & non-voided evaluations)
        # so cues naming a question + competing hypotheses complete across materials,
        # notes, fragments, and rival hypotheses as a single associative graph.
        err_map = data.get("errata", {}) if errata is None else errata
        voided = {
            str(e.get("subject_id"))
            for e in err_map.values()
            if e.get("weight_effect") == "void_row"
            and e.get("subject_type") == "evaluation"
            and _is_live_contradicted_erratum(e)
        }
        def _add_struct(u: tuple[str, str], v: tuple[str, str], w: float = 1.0) -> None:
            if u != v and u[1] and v[1]:
                adj[u][v] = adj[u].get(v, 0.0) + w
                adj[v][u] = adj[v].get(u, 0.0) + w
        for hid, hyp in data.get("hypotheses", {}).items():
            hu = ("hypothesis", hid)
            for qid in hyp.get("question_ids") or ():
                if isinstance(qid, str):
                    _add_struct(hu, ("question", qid), 1.0)
            for mid in (hyp.get("supporting_material_ids") or []) + (hyp.get("counter_material_ids") or []):
                if isinstance(mid, str):
                    _add_struct(hu, ("material", mid), 1.2)
            for nid in hyp.get("source_note_ids") or ():
                if isinstance(nid, str):
                    _add_struct(hu, ("note", nid), 1.0)
        for eid, evl in data.get("evaluations", {}).items():
            if eid in voided:
                continue
            th = evl.get("target_hypothesis_id")
            if not isinstance(th, str) or not th:
                continue
            hu = ("hypothesis", th)
            for ch in evl.get("compared_against_hypothesis_ids") or ():
                if isinstance(ch, str):
                    _add_struct(hu, ("hypothesis", ch), 1.0)
            for mid in evl.get("material_ids") or ():
                if isinstance(mid, str):
                    _add_struct(hu, ("material", mid), 1.0)
            for nid in evl.get("note_ids") or ():
                if isinstance(nid, str):
                    _add_struct(hu, ("note", nid), 1.0)

    excluded = set(exclude_ids) if exclude_ids else set()
    inhib = receiver_inhibition(data, errata=errata) if suppress_inhibited else {}

    cand_score: dict[tuple[str, str], float] = defaultdict(float)
    cand_loops: dict[tuple[str, str], int] = defaultdict(int)
    cand_unbridged: dict[tuple[str, str], int] = defaultdict(int)
    cand_witnesses: dict[tuple[str, str], list[tuple[float, tuple[str, str], tuple[str, str]]]] = defaultdict(list)

    linked_seed_pairs: list[tuple[tuple[str, str], tuple[str, str], float]] = []
    for i, a in enumerate(seeds):
        na = adj.get(a)
        if not na:
            continue
        for b in seeds[i + 1 :]:
            w_ab = na.get(b, 0.0)
            if w_ab > 0.0:
                linked_seed_pairs.append((a, b, w_ab))

    for a, b, w_ab in linked_seed_pairs:
        na = adj[a]
        nb = adj[b]
        # Iterate over the smaller neighbourhood for speed.  Use log1p on all three
        # legs so ubiquitous core-question hubs do not drown out specific multi-loop
        # completions anchored on hypotheses, materials, fragments, and notes.
        small, big = (na, nb) if len(na) <= len(nb) else (nb, na)
        hub_factor = math.log1p(w_ab)
        for c, w1 in small.items():
            if c in seen_seeds or c[1] in excluded:
                continue
            if allowed_types is not None and c[0] not in allowed_types:
                continue
            w2 = big.get(c)
            if w2 is None:
                continue
            if suppress_inhibited and (inhib.get(c) or {}).get("suppressed"):
                continue
            contrib = math.log1p(min(w1, w2)) * hub_factor
            cand_score[c] += contrib
            cand_loops[c] += 1
            if _pair_key(a, c) not in rel_map:
                cand_unbridged[c] += 1
            if _pair_key(b, c) not in rel_map:
                cand_unbridged[c] += 1
            cand_witnesses[c].append((contrib, a, b))

    ranked: list[dict[str, Any]] = []
    for c, raw_sc in cand_score.items():
        info = inhib.get(c)
        gain = info["gaba_gain"] if info else 1.0
        eff_sc = raw_sc * gain
        top_w = sorted(cand_witnesses[c], key=lambda t: (-t[0], t[1], t[2]))[:3]
        ranked.append(
            {
                "target": {"type": c[0], "id": c[1]},
                "score": round(eff_sc, 3),
                "raw_score": round(raw_sc, 3),
                "gaba_gain": gain,
                "closed_loops": cand_loops[c],
                "unbridged_legs": cand_unbridged[c],
                "witness_pairs": [
                    {
                        "left": {"type": a[0], "id": a[1]},
                        "right": {"type": b[0], "id": b[1]},
                        "strength": round(sc, 3),
                    }
                    for sc, a, b in top_w
                ],
            }
        )
    ranked.sort(
        key=lambda r: (-r["score"], -r["closed_loops"], r["target"]["type"], r["target"]["id"])
    )
    return ranked[:limit] if limit > 0 else ranked


def closed_loop_summary(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    include_passive: bool = False,
    min_sessions: int = 2,
) -> dict[str, int]:
    """Count exact closed 3-loops (triangles) in the co-read graph."""
    co_items = co_read(data, include_passive=include_passive, min_sessions=min_sessions)
    neighbors: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    bridged_edges: set[tuple[tuple[str, str], tuple[str, str]]] = set()
    for item in co_items:
        u = (item["left"]["type"], item["left"]["id"])
        v = (item["right"]["type"], item["right"]["id"])
        neighbors[u].add(v)
        neighbors[v].add(u)
        if item["bridged"]:
            bridged_edges.add(_pair_key(u, v))
    order = {node: idx for idx, node in enumerate(sorted(neighbors, key=lambda n: (len(neighbors[n]), n)))}
    forward = {
        u: {v for v in vs if order[v] > order[u]}
        for u, vs in neighbors.items()
    }
    total = 0
    fully_bridged = 0
    for u, fu in forward.items():
        for v in fu:
            common = fu & forward[v]
            if not common:
                continue
            uv_b = _pair_key(u, v) in bridged_edges
            for w in common:
                total += 1
                if uv_b and _pair_key(u, w) in bridged_edges and _pair_key(v, w) in bridged_edges:
                    fully_bridged += 1
    return {
        "co_read_edges": len(co_items),
        "closed_triads": total,
        "triads_with_unbridged_edge": total - fully_bridged,
        "fully_bridged_triads": fully_bridged,
    }


def _session_iso_day(sid: str, session_rec: dict[str, Any]) -> datetime.date | None:
    created = str(session_rec.get("created_at") or "").strip()
    m = _ISO_DAY_RE.match(created)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    sm = _STAMP_ID_RE.match(sid)
    if sm:
        try:
            return datetime.date(int(sm.group(1)), int(sm.group(2)), int(sm.group(3)))
        except ValueError:
            pass
    return None


def temporal_cohort_links(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    window_days: int = 1,
    min_shared: int = 2,
    limit: int = 20,
) -> dict[str, Any]:
    """Identify cross-session ensembles formed within a narrow temporal window (Cai et al. 2016).

    Pairs distinct sessions recorded within ``<= window_days`` whose active
    readings overlap on at least ``min_shared`` non-question records (materials,
    fragments, notes, hypotheses, motifs).  Unlike fused summaries, each session
    retains its independent provenance and scope verdicts.
    """
    sessions = data.get("sessions", {})
    day_of: dict[str, datetime.date] = {}
    for sid, srec in sessions.items():
        d = _session_iso_day(sid, srec)
        if d is not None and d <= datetime.date(2026, 12, 31):
            day_of[sid] = d

    targets_by_session: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in data.get("read_log", {}).values():
        if row.get("reading") not in ACTIVE_READINGS:
            continue
        sid = str(row.get("session_id") or "")
        if sid not in day_of:
            continue
        tgt = row.get("target")
        if not isinstance(tgt, dict):
            continue
        ttype = str(tgt.get("type") or "")
        tid = str(tgt.get("id") or "")
        if ttype and tid and ttype != "question":
            targets_by_session[sid].add((ttype, tid))

    by_day: dict[datetime.date, list[str]] = defaultdict(list)
    for sid in sorted(targets_by_session):
        if len(targets_by_session[sid]) >= min_shared:
            by_day[day_of[sid]].append(sid)

    days_sorted = sorted(by_day)
    pairs: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for d in days_sorted:
        cohort: list[str] = []
        for delta in range(0, max(0, window_days) + 1):
            cand_day = d + datetime.timedelta(days=delta)
            cohort.extend(by_day.get(cand_day, ()))
        for s1 in by_day[d]:
            t1 = targets_by_session[s1]
            for s2 in cohort:
                if s1 == s2:
                    continue
                pk = (s1, s2) if s1 < s2 else (s2, s1)
                if pk in seen_pairs:
                    continue
                seen_pairs.add(pk)
                shared = t1 & targets_by_session[s2]
                if len(shared) < min_shared:
                    continue
                gap = abs((day_of[s1] - day_of[s2]).days)
                pairs.append(
                    {
                        "left_session": pk[0],
                        "right_session": pk[1],
                        "day_gap": gap,
                        "left_date": day_of[pk[0]].isoformat(),
                        "right_date": day_of[pk[1]].isoformat(),
                        "shared_count": len(shared),
                        "shared_targets": [
                            {"type": tt, "id": ti} for tt, ti in sorted(shared)[:8]
                        ],
                    }
                )
    pairs.sort(
        key=lambda r: (-r["shared_count"], r["day_gap"], r["left_session"], r["right_session"])
    )
    return {
        "window_days": window_days,
        "min_shared": min_shared,
        "dated_active_sessions": len(targets_by_session),
        "linked_session_pairs": len(pairs),
        "top_pairs": pairs[:limit] if limit > 0 else pairs,
    }


def non_fusing_link_stats(
    data: dict[str, dict[str, dict[str, Any]]],
    errata: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Quantify Cai et al. (2016) non-fusing linkage across material–hypothesis bindings.

    Measures (a) what fraction of repeatedly evaluated materials link >=2 distinct
    hypotheses, and (b) when one linked hypothesis is narrowed or refuted, how
    often co-linked partner hypotheses retain their own unrefuted standing
    (non-shared erasure).
    """
    err_map = data.get("errata", {}) if errata is None else errata
    voided = {
        str(e.get("subject_id"))
        for e in err_map.values()
        if e.get("weight_effect") == "void_row"
        and e.get("subject_type") == "evaluation"
        and _is_live_contradicted_erratum(e)
    }
    mat_eval_count: Counter[str] = Counter()
    mat_hyps: dict[str, set[str]] = defaultdict(set)
    hyp_verdicts: dict[str, Counter[str]] = defaultdict(Counter)
    for eid, evl in data.get("evaluations", {}).items():
        if eid in voided:
            continue
        th = evl.get("target_hypothesis_id")
        vd = evl.get("verdict")
        if not isinstance(th, str) or not isinstance(vd, str):
            continue
        hyp_verdicts[th][vd] += 1
        for mid in evl.get("material_ids") or ():
            if isinstance(mid, str) and mid:
                mat_eval_count[mid] += 1
                mat_hyps[mid].add(th)

    multi = [m for m, c in mat_eval_count.items() if c >= 2]
    cross = [m for m in multi if len(mat_hyps[m]) >= 2]
    erasure_tested = 0
    partner_intact = 0
    for m in cross:
        linked = sorted(mat_hyps[m])
        for h1 in linked:
            v1 = hyp_verdicts[h1]
            if (v1.get("narrows_scope", 0) + v1.get("refutes_unconditioned", 0)) == 0:
                continue
            for h2 in linked:
                if h1 == h2:
                    continue
                erasure_tested += 1
                v2 = hyp_verdicts[h2]
                is_refuted = v2.get("refutes_unconditioned", 0) > 0 and v2.get("supports", 0) == 0
                if not is_refuted and v2.get("supports", 0) > 0:
                    partner_intact += 1
    return {
        "evaluated_materials": len(mat_eval_count),
        "multi_eval_materials": len(multi),
        "cross_hypothesis_materials": len(cross),
        "cross_hypothesis_share_pct": round(100.0 * len(cross) / len(multi), 1) if multi else 0.0,
        "erasure_tested_ordered_pairs": erasure_tested,
        "partner_intact_ordered_pairs": partner_intact,
        "non_shared_erasure_pct": round(100.0 * partner_intact / erasure_tested, 1)
        if erasure_tested
        else 0.0,
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

CAVEAT = (
    "以下の数値は**推奨であって義務ではありません**。未読は負債ではなく余白であり、"
    "共起の本数・顕著性・減衰を成功条件にしません（`prompts/start.md`・`docs/mode-rotation-triggers.md`）。"
)


def _fmt_target(ref: dict[str, str]) -> str:
    return f"{ref['type']}:{ref['id']}"


def render_report(
    data: dict[str, dict[str, dict[str, Any]]],
    co: list[dict[str, Any]],
    acc: dict[tuple[str, str], dict[str, Any]],
    cold: list[dict[str, Any]],
    warm: list[dict[str, Any]],
    never: list[dict[str, Any]],
    *,
    limit: int = 20,
) -> str:
    stats = summarize(data, co, acc)
    titles: dict[str, str] = {}
    for fid, fragment in data.get("fragments", {}).items():
        titles[fid] = str(fragment.get("title", ""))
    for qid, question in data.get("questions", {}).items():
        titles[qid] = " ".join(str(question.get("question", "")).split())[:70]

    out: list[str] = ["=== association & salience report (read_log-derived) ===", ""]
    out.append(
        f"  read_log            : {stats['read_log_rows']} 行 ／ 対象 {stats['distinct_targets']} 件 "
        f"{stats['targets_by_type']}"
    )
    out.append(f"  読み方の分布        : {stats['by_reading']}")
    out.append(
        f"  受動的な行の割合    : {stats['passive_share_pct']}% "
        "（`used_as_context` ＋ `counted`。共起の既定の分母から除外）"
    )
    out.append(
        f"  共起（≥2セッション）: {stats['co_read_pairs_2plus_sessions']} 対 ／ "
        f"うち関係線あり {stats['co_read_pairs_bridged']} ・**なし {stats['co_read_pairs_unbridged']}**"
    )
    out.append("")

    unbridged = [item for item in co if not item["bridged"]]
    out.append(f"--- 未架橋の強い共起（上位 {min(limit, len(unbridged))} 対） ---")
    for item in unbridged[:limit]:
        left, right = item["left"], item["right"]
        label = " × ".join(
            f"{_fmt_target(ref)}" + (f"『{titles[ref['id']]}』" if ref["id"] in titles else "")
            for ref in (left, right)
        )
        out.append(
            f"  {item['sessions']} セッション ／ {item['co_reads']} 回  {label}"
        )
        out.append(f"      sessions: {', '.join(item['session_ids'])}")
    if not unbridged:
        out.append("  （なし：2セッション以上で共読された対はすべて関係線を持っている）")
    out.append("")

    ranked = sorted(acc.values(), key=lambda entry: -entry["salience"])
    out.append(f"--- 顕著性（salience）上位 {min(limit, len(ranked))} 件 ---")
    for entry in ranked[:limit]:
        title = titles.get(entry["id"], "")
        out.append(
            f"  {entry['salience']:8.2f}  {entry['type']}:{entry['id']}  "
            f"rows={entry['rows']} active={entry['active_rows']} sessions={entry['sessions']} "
            f"since_last={entry['rows_since_last_read']}"
            + (f"  『{title}』" if title else "")
        )
    out.append("")

    out.append(f"--- かつて読まれ、その後沈黙している荷重記録（上位 {min(limit, len(cold))} 件） ---")
    for item in cold[:limit]:
        title = titles.get(item["id"], "") or item.get("title", "")
        out.append(
            f"  {item['rows_since_last_read']:>6} 行前  {item['type']}:{item['id']} [{item['why']}] "
            f"rows={item['rows']} sessions={item['sessions']} salience={item['salience']}"
            + (f"  『{title[:60]}』" if title else "")
        )
    if not cold:
        out.append("  （なし）")
    out.append(
        f"- **最近読まれた荷重記録（warm）**: {len(warm)} 件 — 減衰の閾値の内側にあるため、"
        "信号として一覧化しません。"
    )
    never_by_why = Counter(item["why"] for item in never)
    out.append(
        f"- **一度も read_log 行がない荷重記録**: {len(never)} 件 {dict(never_by_why.most_common())}"
        " — 件数だけを示します。未読は負債ではなく余白なので、一覧化して返済すべき目録のように見せないようにしています。"
    )
    out.append("")
    out.append("  時間軸は read_log の挿入順（行数）です。日付は内部編年ラベルと実日付がずれるため使っていません。")
    out.append(f"  {CAVEAT}")
    return "\n".join(out) + "\n"


def render_map(
    data: dict[str, dict[str, dict[str, Any]]],
    co: list[dict[str, Any]],
    acc: dict[tuple[str, str], dict[str, Any]],
    cold: list[dict[str, Any]],
    warm: list[dict[str, Any]],
    never: list[dict[str, Any]],
    *,
    limit: int = 100,
) -> str:
    stats = summarize(data, co, acc)
    out = [
        "# 連想と顕著性の地図（read_log 由来・生成物）",
        "",
        "> `tools/associations.py` が `state/read_log*` と `state/relations*` から生成します（git 管理外）。",
        f"> {CAVEAT}",
        "",
        "## 0. 集計",
        "",
        "| 指標 | 値 |",
        "|---|---:|",
        f"| read_log 行数 | {stats['read_log_rows']:,} |",
        f"| 活性化した対象 | {stats['distinct_targets']:,} |",
        f"| 共起（≥2セッション） | {stats['co_read_pairs_2plus_sessions']:,} 対 |",
        f"| うち関係線あり | {stats['co_read_pairs_bridged']:,} |",
        f"| うち未架橋 | {stats['co_read_pairs_unbridged']:,} |",
        f"| relations 総数 | {stats['relations']:,} |",
        f"| 受動的行の割合 | {stats['passive_share_pct']}% |",
        "",
        "## 1. 未架橋の共起（関係線の候補）",
        "",
        "| セッション数 | 共読回数 | 左 | 右 | 共読したセッション |",
        "|---:|---:|---|---|---|",
    ]
    for item in [entry for entry in co if not entry["bridged"]][:limit]:
        out.append(
            f"| {item['sessions']} | {item['co_reads']} | `{_fmt_target(item['left'])}` | "
            f"`{_fmt_target(item['right'])}` | {', '.join(item['session_ids'])} |"
        )
    out.extend(
        [
            "",
            "## 2. 顕著性（重み×減衰）上位",
            "",
            "| salience | 対象 | 行数 | 能動行 | セッション | 最終読了からの行数 | 読み方の内訳 |",
            "|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for entry in sorted(acc.values(), key=lambda item: -item["salience"])[:limit]:
        breakdown = ", ".join(f"{k}{v}" for k, v in entry["by_reading"].items())
        out.append(
            f"| {entry['salience']:.2f} | `{entry['type']}:{entry['id']}` | {entry['rows']} | "
            f"{entry['active_rows']} | {entry['sessions']} | {entry['rows_since_last_read']} | {breakdown} |"
        )
    out.extend(
        [
            "",
            "## 3. かつて読まれ、その後沈黙している荷重記録",
            "",
            "| 最終読了からの行数 | 対象 | 理由 | salience | 行数 | セッション数 |",
            "|---:|---|---|---:|---:|---:|",
        ]
    )
    for item in cold[:limit]:
        out.append(
            f"| {item['rows_since_last_read']} | `{item['type']}:{item['id']}` | "
            f"{item['why']} | {item['salience']} | {item['rows']} | {item['sessions']} |"
        )
    never_by_why = Counter(item["why"] for item in never)
    out.extend(
        [
            "",
            f"直近に読まれた荷重記録（warm）は **{len(warm)} 件**。減衰の閾値の内側なので一覧化しない。",
            f"一度も read_log 行がない荷重記録は **{len(never)} 件**（{dict(never_by_why.most_common())}）。"
            "未読は負債ではなく余白なので一覧化しない。",
        ]
    )
    out.extend(["", "## 4. 重みと減衰の定義", ""])
    out.append("| reading | 重み |")
    out.append("|---|---:|")
    for name, weight in sorted(READING_WEIGHTS.items(), key=lambda pair: -pair[1]):
        out.append(f"| `{name}` | {weight} |")
    out.extend(
        [
            "",
            f"- 減衰: `0.5 ** (最終読了から経過した行数 / half_life)`、既定 half_life = {DEFAULT_HALF_LIFE:.0f} 行。",
            "- 荷重記録の定義: FRAG が `selected` または `held`、Q が `open` かつ `responds_to`/`reframes` で応答済みでないもの。"
            "`paused`/`rejected` は編集判断のオーバーレイで既に退いており、この計測はそれを打ち消しません。",
            "- 沈黙の閾値（cold）: `max(100, 活性化した対象数 / 4)` 行。アーカイブの大きさに従って伸びる相対値で、固定日付ではありません。",
            "- 時間軸は read_log の挿入順（base → シャード名順）。`created_at` は内部編年ラベルと実日付が混在するため使わない。",
            "- 共起の既定の分母は能動的な読み（quoted/summarized/interpreted/reinterpreted/contested）のみ。",
            "",
        ]
    )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--co-read", action="store_true", help="list co-activation pairs")
    parser.add_argument("--salience", action="store_true", help="rank records by weighted activation")
    parser.add_argument(
        "--inhibited",
        action="store_true",
        help="Gate 2: rank records by receiver-local inhibited salience and surface unresolved intrusions",
    )
    parser.add_argument(
        "--complete",
        nargs="+",
        metavar="ID",
        help="Gate 1: closed-loop pattern completion (third elements closing A–B–C–A loops for >=2 cue IDs)",
    )
    parser.add_argument(
        "--temporal-links",
        action="store_true",
        help="Gate 1: list cross-session temporal-window ensembles and non-fusing link retention",
    )
    parser.add_argument("--window-days", type=int, default=1, help="day window for --temporal-links (default 1)")
    parser.add_argument("--decay", action="store_true", help="list long-unactivated load-bearing records")
    parser.add_argument("--include-passive", action="store_true", help="count used_as_context/counted as co-activation")
    parser.add_argument("--min-sessions", type=int, default=2, help="co-activation threshold (default 2)")
    parser.add_argument("--half-life", type=float, default=DEFAULT_HALF_LIFE, help="decay half-life in read_log rows")
    parser.add_argument("--bridged", action="store_true", help="also list pairs that already have a relation")
    parser.add_argument("--limit", type=int, default=20, help="rows to print per list")
    parser.add_argument("--map-dir", type=Path, default=ROOT / "map", help="output directory for --write-map")
    parser.add_argument("--write-map", action="store_true", help="write map/associations.md (untracked)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        data = load(args.root.resolve())
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    co = co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions)
    if not args.bridged:
        co = [item for item in co if not item["bridged"]]
    acc = activation(data, half_life=args.half_life, include_passive=True)
    cold, warm, never = load_bearing(data, acc)

    if args.write_map:
        map_dir = Path(args.map_dir)
        map_dir.mkdir(parents=True, exist_ok=True)
        text = render_map(
            data,
            co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions),
            acc,
            cold,
            warm,
            never,
            limit=max(args.limit, 100),
        )
        ledger_io.atomic_write_text(map_dir / "associations.md", text)
        print(f"WROTE {map_dir / 'associations.md'} ({len(text.encode('utf-8')):,} bytes, not tracked)")
        return 0

    if args.json:
        specific = args.co_read or args.salience or args.decay or args.inhibited or bool(args.complete) or args.temporal_links
        payload: dict[str, Any] = {
            "stats": summarize(
                data, co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions), acc
            ),
            "weights": READING_WEIGHTS,
            "half_life": args.half_life,
        }
        if args.co_read or not specific:
            payload["co_read"] = co[: args.limit]
        if args.salience:
            payload["salience"] = sorted(acc.values(), key=lambda item: -item["salience"])[: args.limit]
        if args.inhibited:
            inh = inhibited_activation(data, half_life=args.half_life, include_passive=True)
            payload["inhibited_salience"] = sorted(
                inh.values(), key=lambda item: -item["inhibited_salience"]
            )[: args.limit]
            payload["most_dampened"] = sorted(
                (v for v in inh.values() if v["gaba_gain"] < 1.0),
                key=lambda item: -(item["raw_salience"] - item["inhibited_salience"]),
            )[: args.limit]
            payload["unresolved_intrusions"] = sorted(
                (v for v in inh.values() if v["unresolved_intrusion"]),
                key=lambda item: -item["raw_salience"],
            )[: args.limit]
        if args.complete:
            payload["closed_loop_completions"] = closed_loop_completions(
                data,
                args.complete,
                include_passive=args.include_passive,
                min_sessions=args.min_sessions,
                limit=args.limit,
            )
            payload["closed_loop_summary"] = closed_loop_summary(
                data, include_passive=args.include_passive, min_sessions=args.min_sessions
            )
        if args.temporal_links:
            payload["temporal_links"] = temporal_cohort_links(
                data, window_days=args.window_days, limit=args.limit
            )
            payload["non_fusing_links"] = non_fusing_link_stats(data)
        if args.decay:
            payload["cold"] = cold[: args.limit]
            payload["warm_total"] = len(warm)
            payload["never_read_counts"] = dict(Counter(item["why"] for item in never))
            payload["never_read_total"] = len(never)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.complete:
        comps = closed_loop_completions(
            data,
            args.complete,
            include_passive=args.include_passive,
            min_sessions=args.min_sessions,
            limit=args.limit,
        )
        print(f"=== Gate 1: closed-loop completions (A–B–C–A) for cues {args.complete} ===")
        for item in comps:
            t = item["target"]
            wp = item["witness_pairs"][0] if item["witness_pairs"] else None
            via = f" via {_fmt_target(wp['left'])}×{_fmt_target(wp['right'])}" if wp else ""
            print(
                f"  score={item['score']:7.2f} (gain={item['gaba_gain']:.2f}, loops={item['closed_loops']}, "
                f"unbridged={item['unbridged_legs']})  {_fmt_target(t)}{via}"
            )
        if not comps:
            print("  (no closed 3-loops found for this cue set — provide >=2 linked cues)")
        print(f"  {CAVEAT}")
        return 0

    if args.inhibited:
        inh = inhibited_activation(data, half_life=args.half_life, include_passive=True)
        print(f"=== Gate 2: receiver-inhibited salience (half-life {args.half_life:.0f} rows) ===")
        for entry in sorted(inh.values(), key=lambda item: -item["inhibited_salience"])[: args.limit]:
            why = f"  inhibited={entry['inhibition_reasons']}" if entry["inhibition_reasons"] else ""
            intr = "  [UNRESOLVED-INTRUSION]" if entry["unresolved_intrusion"] else ""
            print(
                f"  {entry['inhibited_salience']:8.2f} (raw={entry['raw_salience']:6.2f}, gain={entry['gaba_gain']:.2f})  "
                f"{entry['type']}:{entry['id']}{why}{intr}"
            )
        dampened = sorted(
            (v for v in inh.values() if v["gaba_gain"] < 1.0 and v["raw_salience"] >= 1.0),
            key=lambda item: -(item["raw_salience"] - item["inhibited_salience"]),
        )[: min(10, args.limit)]
        if dampened:
            print("--- largest receiver-local dampings (raw -> inhibited) ---")
            for entry in dampened:
                print(
                    f"  {entry['raw_salience']:6.2f} -> {entry['inhibited_salience']:6.2f} (gain={entry['gaba_gain']:.2f})  "
                    f"{entry['type']}:{entry['id']}  {entry['inhibition_reasons']}"
                )
        intrusions = sorted(
            (v for v in inh.values() if v["unresolved_intrusion"]),
            key=lambda item: -item["raw_salience"],
        )[: min(10, args.limit)]
        if intrusions:
            print("--- unresolved intrusions (contested>=2 without inhibitory resolution) ---")
            for entry in intrusions:
                c_n = (entry.get("by_reading") or {}).get("contested", 0)
                print(
                    f"  raw={entry['raw_salience']:6.2f} contested={c_n}  {entry['type']}:{entry['id']}"
                )
        print(f"  {CAVEAT}")
        return 0

    if args.temporal_links:
        tl = temporal_cohort_links(data, window_days=args.window_days, limit=args.limit)
        nf = non_fusing_link_stats(data)
        print(
            f"=== Gate 1: temporal-window ensembles (<= {tl['window_days']}d) & non-fusing links ==="
        )
        print(
            f"  non-fusing material links: {nf['cross_hypothesis_materials']}/{nf['multi_eval_materials']} "
            f"({nf['cross_hypothesis_share_pct']}%) multi-eval materials span >=2 hypotheses; "
            f"partner intact after narrowing/refutation: "
            f"{nf['partner_intact_ordered_pairs']}/{nf['erasure_tested_ordered_pairs']} "
            f"({nf['non_shared_erasure_pct']}%)"
        )
        print(
            f"  temporal cohort pairs (<= {tl['window_days']}d, shared>={tl['min_shared']}): "
            f"{tl['linked_session_pairs']} across {tl['dated_active_sessions']} dated active sessions"
        )
        for p in tl["top_pairs"][: args.limit]:
            sample = ", ".join(_fmt_target(t) for t in p["shared_targets"][:4])
            print(
                f"  shared={p['shared_count']:>2} (gap={p['day_gap']}d, {p['left_date']})  "
                f"{p['left_session']} × {p['right_session']}  [{sample}]"
            )
        print(f"  {CAVEAT}")
        return 0

    if args.co_read:
        print(f"=== co-activation pairs (≥{args.min_sessions} sessions, bridged={args.bridged}) ===")
        for item in co[: args.limit]:
            print(
                f"  {item['sessions']} sessions ／ {item['co_reads']} co-reads  "
                f"{_fmt_target(item['left'])} × {_fmt_target(item['right'])}  "
                f"[{'bridged' if item['bridged'] else 'UNBRIDGED'}]"
            )
        print(f"  {CAVEAT}")
        return 0

    if args.salience:
        print(f"=== salience (weights × decay, half-life {args.half_life:.0f} rows) ===")
        for entry in sorted(acc.values(), key=lambda item: -item["salience"])[: args.limit]:
            print(
                f"  {entry['salience']:8.2f}  {entry['type']}:{entry['id']}  "
                f"rows={entry['rows']} active={entry['active_rows']} sessions={entry['sessions']} "
                f"since_last={entry['rows_since_last_read']}"
            )
        print(f"  {CAVEAT}")
        return 0

    if args.decay:
        print("=== load-bearing records that went cold (rows since last read) ===")
        for item in cold[: args.limit]:
            print(
                f"  {item['rows_since_last_read']:>6}  {item['type']}:{item['id']} "
                f"[{item['why']}] rows={item['rows']} sessions={item['sessions']} "
                f"salience={item['salience']}"
            )
        never_by_why = Counter(item["why"] for item in never)
        print(f"  never read: {len(never)} records {dict(never_by_why.most_common())} (margin, not debt)")
        print(f"  {CAVEAT}")
        return 0

    sys.stdout.write(
        render_report(
            data,
            co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions),
            acc,
            cold,
            warm,
            never,
            limit=args.limit,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
