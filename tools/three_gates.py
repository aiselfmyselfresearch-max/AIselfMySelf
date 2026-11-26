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
    python3 tools/three_gates.py --verify-span --source-file /tmp/paper.txt --passage "Organisms adapt well enough..."
    python3 tools/three_gates.py --upgrade-candidates --limit 15
    python3 tools/three_gates.py --cohort-suppression
    python3 tools/three_gates.py --complete Q-002 HYP-20261118-21461e
    python3 tools/three_gates.py --json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
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
from read_log_backfill import HANDWRITTEN_READINGS  # noqa: E402

normalize_source_span = validate_seed.normalize_source_span
compute_passage_span_witness = validate_seed.compute_passage_span_witness
verify_passage_against_source = validate_seed.verify_passage_against_source

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


# Title index for --check-source (2026-11-27,
# docs/2026-11-26-check-source-title-blindspot-proposal.md).  The display ``title`` is a
# Japanese gloss on most rows, so an original title passed with --title matched only
# 22.4% of rows' own source.title; indexing source.title (split into its works, a
# trailing "(Journal 12, 2016)" dropped) raised that to 99.9% and caught all 22 rows
# minted after the 20261119 identifier gate that duplicate an earlier row.
_TITLE_SPLIT_RE = re.compile(r"\s*(?:／|；|\s/\s|;\s)\s*")
_TITLE_TAIL_RE = re.compile(r"\s*[(（][^()（）]*\d{4}[^()（）]*[)）]\s*$")
_ROMAN_RE = re.compile(r"\b(?=[MDCLXVI]{2,}\b)M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\b")
_RESPONSE_RE = re.compile(
    r"^\W*(comment(?:ary)?\s+on|response\s+to|reply\s+to|corrigendum|erratum|correction|retraction)\b(?:\s+(?:to|of|note))?\W*",
    re.IGNORECASE,
)
_QUOTED_TITLE_RE = re.compile(r"[「『“]([^」』”]+)[」』”]")
_NOTE_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>?#、。，「」（）()\[\]]+)", re.IGNORECASE)
_ROMAN_VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_to_int(text: str) -> int:
    vals = [_ROMAN_VAL[c] for c in text]
    return sum(-v if i + 1 < len(vals) and v < vals[i + 1] else v for i, v in enumerate(vals))


def _title_locators(text: str) -> frozenset[str]:
    """Chapter/verse/hymn numbers in a title (trailing citation year dropped, Roman numerals read)."""
    body = _TITLE_TAIL_RE.sub("", unicodedata.normalize("NFKC", text))
    body = _ROMAN_RE.sub(lambda m: f" {_roman_to_int(m.group(0))} " if m.group(0) else "", body)
    return frozenset(str(int(n)) for n in re.findall(r"\d+", body))


def _response_chain(text: str) -> tuple[str, ...]:
    """('comment',) for 'Comment on X', ('response', 'comment') for 'Response to Comment on X'."""
    chain: list[str] = []
    rest = unicodedata.normalize("NFKC", text)
    while (m := _RESPONSE_RE.match(rest)) and len(chain) < 4:
        chain.append(m.group(1).split()[0].casefold())
        rest = rest[m.end():]
    return tuple(chain)


def title_variants(text: str, *, min_tokens: int = 3, split: bool = True) -> list[dict[str, Any]]:
    """Index keys for one title: each work of a combined title, with and without a citation tail."""
    text = str(text or "")
    parts = [p for p in (_TITLE_SPLIT_RE.split(text) if split else [text]) if p.strip()] or [text]
    if split:  # 'Sparrow, Liu & Wegner (2011)「Google Effects on Memory…」' -> the quoted title too
        parts += _QUOTED_TITLE_RE.findall(text)
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for part in parts:
        for variant in (part, _TITLE_TAIL_RE.sub("", part)):
            norm, toks = _normalize_title(variant)
            if len(toks) < min_tokens or norm in seen:
                continue
            seen.add(norm)
            out.append({"text": part.strip(), "norm": norm, "tokens": toks,
                        "locators": _title_locators(part), "chain": _response_chain(part)})
    return out


def _material_title_index(rec: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    src = rec.get("source") if isinstance(rec.get("source"), dict) else {}
    keys = [("title", v) for v in title_variants(str(rec.get("title") or ""), min_tokens=1, split=False)]
    keys += [("source.title", v) for v in title_variants(str(src.get("title") or ""))]
    return keys


def _best_title_match(
    queries: list[dict[str, Any]], keys: list[tuple[str, dict[str, Any]]], threshold: float
) -> tuple[float, str, str, bool]:
    """(similarity, field, matched text, same_response_chain) of the best guarded match."""
    best = (0.0, "", "", True)
    for q in queries:
        for field, k in keys:
            if q["locators"] and k["locators"] and q["locators"] != k["locators"]:
                continue  # Psalm 23 is not Psalm 24; Hymn XIV is not Hymn CXXXV
            if q["norm"] == k["norm"]:
                sim = 1.0
            else:
                union = len(q["tokens"] | k["tokens"])
                sim = len(q["tokens"] & k["tokens"]) / union if union else 0.0
            same_chain = q["chain"] == k["chain"]
            cand = (sim, field, k["text"], same_chain)
            if sim >= threshold and (best[0] < threshold or (same_chain, sim) > (best[3], best[0])):
                best = cand
            elif best[0] < threshold and sim > best[0]:
                best = cand
    return best


def note_dois(rec: dict[str, Any]) -> set[str]:
    """DOIs written only in ``source.version_note`` (may name related papers, so advisory only)."""
    vnote = str(((rec.get("source") or {}).get("version_note")) or "")
    return {m.rstrip(".,;:)/]}>").lower() for m in _NOTE_DOI_RE.findall(vnote)}


def _author_hit(rec: dict[str, Any], author_tokens: list[str], year: int | None) -> bool:
    src = rec.get("source") if isinstance(rec.get("source"), dict) else {}
    authors = src.get("authors") if isinstance(src.get("authors"), list) else []
    if not any(
        all((t in name) if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", t) else (t in set(_WORD_RE.findall(name))) for t in author_tokens)
        for name in (unicodedata.normalize("NFKC", str(a)).casefold() for a in authors)
    ):
        return False
    return year is None or src.get("year") == year or str(year) in str(src.get("title") or "")


def check_source(
    materials: dict[str, dict[str, Any]],
    *,
    doi: str = "",
    pmid: str = "",
    pmcid: str = "",
    url: str = "",
    title: str = "",
    author: str = "",
    year: int | None = None,
    title_threshold: float = 0.72,
) -> dict[str, Any]:
    """Check a candidate primary source against all archived materials (Gate 3).

    Matches identifiers (``source.url``/``source_id``; DOIs only in ``version_note``
    are reported separately), titles (display ``title`` and every work in
    ``source.title``, guarded by numeric locators and Comment/Response prefixes)
    and, with ``author``, first-author surname plus ``year``.  Every title/author
    hit is advisory: CLEAR means "not found in these indexes", not "new".
    """
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

    queries = title_variants(title)
    author_tokens = [t for t in _WORD_RE.findall(unicodedata.normalize("NFKC", author).casefold()) if len(t) >= 2]
    exact_matches: list[dict[str, Any]] = []
    note_matches: list[dict[str, Any]] = []
    title_matches: list[dict[str, Any]] = []
    related_matches: list[dict[str, Any]] = []
    author_matches: list[dict[str, Any]] = []

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
        base = {
            "material_id": mid,
            "title": str(rec.get("title") or ""),
            "source_title": str(src.get("title") or ""),
            "year": src.get("year"),
            "verification_status": vstat,
            "url": str(src.get("url") or ""),
            "can_upgrade_via_editorial_decision": vstat != "verified",
        }
        if matched_on:
            exact_matches.append({**base, "matched_on": matched_on})
            continue
        if "doi" in wanted_ids and wanted_ids["doi"] in note_dois(rec):
            note_matches.append({**base, "matched_on": [f"version_note.doi:{wanted_ids['doi']}"]})
            continue
        sim, field, matched, same_chain = (0.0, "", "", True)
        if queries:
            sim, field, matched, same_chain = _best_title_match(queries, _material_title_index(rec), title_threshold)
        if sim >= title_threshold:
            row = {**base, "title_similarity": round(sim, 3), "matched_field": field, "matched_title": matched}
            (title_matches if same_chain else related_matches).append(row)
        elif author_tokens and _author_hit(rec, author_tokens, year):
            author_matches.append({**base, "title_similarity": round(sim, 3)})

    title_matches.sort(key=lambda r: (-r["title_similarity"], r["material_id"]))
    related_matches.sort(key=lambda r: (-r["title_similarity"], r["material_id"]))
    author_matches.sort(key=lambda r: (-r["title_similarity"], r["material_id"]))
    status = next(
        (name for name, rows in (("DUPLICATE_ID", exact_matches), ("NOTE_IDENTIFIER", note_matches),
                                 ("SIMILAR_TITLE", title_matches), ("AUTHOR_YEAR", author_matches),
                                 ("RELATED", related_matches)) if rows),
        "CLEAR",
    )
    advisories: list[str] = []
    if status == "CLEAR":
        advisories.append("CLEAR means no hit in the identifier/title/author indexes; it is not proof that the source is new.")
    if not queries:
        advisories.append("No original title (>=3 words) was given; pass --title with the source's original-language title.")
    if not author_tokens:
        advisories.append("Pass --author <first-author surname> --year <year> to reach rows whose source.title is a translation.")
    if note_matches:
        advisories.append("NOTE_IDENTIFIER: the DOI appears only in version_note, which may cite a related paper; read the row.")
    upgrade_hint = None
    first_non_v = next(
        (m for m in exact_matches + note_matches + title_matches if m["can_upgrade_via_editorial_decision"]),
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
        "queried_author": author,
        "queried_year": year,
        "exact_identifier_matches": exact_matches,
        "note_identifier_matches": note_matches,
        "similar_title_matches": title_matches[:8],
        "author_year_matches": author_matches[:10],
        "related_title_matches": related_matches[:8],
        "advisories": advisories,
        "editorial_upgrade_template": upgrade_hint,
    }


def source_duplicate_audit(
    materials: dict[str, dict[str, Any]],
    *,
    cutoff: str = validate_seed.THREE_GATES_RULE_FROM,
    today: datetime.date | None = None,
) -> dict[str, Any]:
    """Same-source clusters by shared identifier or identical work title (read-only audit).

    Lists rows minted on/after ``cutoff`` that repeat an earlier row (the identifier
    gate cannot see them when the earlier row has no identifier or the DOIs disagree)
    and clusters holding two or more different DOIs (misrecorded, or a genuine second
    DOI after a publisher move).  Literary-only clusters are skipped: same translator
    and title pattern with different chapters is the norm there, not duplication.
    """
    parent = {mid: mid for mid in materials}

    def root(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    ids = {mid: validate_seed.extract_material_identifiers(rec) for mid, rec in materials.items()}
    groups: dict[Any, list[str]] = defaultdict(list)
    for mid, rec in materials.items():
        for v in title_variants(str((rec.get("source") or {}).get("title") or ""), min_tokens=4):
            groups[("title", v["norm"])].append(mid)
        for kind, val in ids[mid].items():
            groups[(kind, val)].append(mid)
    for members in groups.values():
        for other in members[1:]:
            parent[root(other)] = root(members[0])
    clusters: dict[str, list[str]] = defaultdict(list)
    for mid in materials:
        clusters[root(mid)].append(mid)

    def literary(mid: str) -> bool:
        return mid.startswith("MAT-LIT") or materials[mid].get("kind") == "literary_text"

    def stamp(mid: str) -> str:
        return validate_seed.id_stamp(mid) or "00000000"

    dup_clusters = [sorted(c, key=lambda m: (stamp(m), m)) for c in clusters.values()
                    if len(c) >= 2 and not all(literary(m) for m in c)]
    post_gate: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for c in dup_clusters:
        dois = sorted({ids[m]["doi"] for m in c if ids[m].get("doi")})
        if len(dois) >= 2:
            conflicts.append({"material_ids": c, "dois": dois})
        for i, mid in enumerate(c[1:], start=1):
            if not validate_seed._is_new_row(mid, cutoff, today=today):
                continue
            earlier = c[:i]
            mine = ids[mid].get("doi")
            if mine and any(ids[e].get("doi") and ids[e]["doi"] != mine for e in earlier):
                cause = "doi_disagreement"
            elif not ids[mid]:
                cause = "new_row_has_no_identifier"
            else:
                cause = "earlier_row_has_no_identifier"
            post_gate.append({"material_id": mid, "earlier": earlier, "cause": cause,
                              "source_title": str((materials[mid].get("source") or {}).get("title") or "")})
    return {
        "clusters": len(dup_clusters),
        "extra_rows": sum(len(c) - 1 for c in dup_clusters),
        "post_gate_cutoff": cutoff,
        "post_gate_duplicates": post_gate,
        "doi_conflict_clusters": conflicts,
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


def memory_temperature_and_gate_audit(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    limit: int = 15,
) -> dict[str, Any]:
    """Describe retrospective wiring and read/evaluation *co-occurrence*.

    For compatibility the JSON retains the old ``stage*`` and ``subseq*`` keys,
    but neither they nor Hot/Warm/Cold establish a chronological sequence,
    conversion, causation, or actual absence of reading. The anchor is only the
    first context mention in ledger order, falling back to the first layer-2
    reading in that order; ledger order is not real time or proof of birth.
    R and E each mean a recorded layer-2 read, respectively evaluation citation,
    in any session different from this anchor. They need not be in the same
    session, and no order between them is inferred. Unknown anchors are reported
    separately and excluded from the R/E denominators.

    Tier 1/2 is determined from all current notes/hypotheses, possibly written
    after the events being counted. ``counted`` is included as an audit record,
    not equated to interpretation; ``declined`` and ``used_as_context`` are not
    layer-2 reading records. See the 2026-11-20 audit of NOTE-20261120-058297.
    """
    materials = data.get("materials", {})
    notes = data.get("notes", {})
    hypotheses = data.get("hypotheses", {})
    evaluations = data.get("evaluations", {})
    read_log = data.get("read_log", {})
    sessions = data.get("sessions", {})
    questions = data.get("questions", {})

    q_by_mat: dict[str, list[str]] = defaultdict(list)
    for qid, qrec in questions.items():
        for mid in qrec.get("material_ids") or ():
            if isinstance(mid, str) and mid in materials and qid not in q_by_mat[mid]:
                q_by_mat[mid].append(qid)

    tier1_claim_mids: set[str] = set()
    for nrec in notes.values():
        for cl in nrec.get("claims") or ():
            if isinstance(cl, dict):
                for mid in cl.get("material_ids") or ():
                    if isinstance(mid, str) and mid in materials:
                        tier1_claim_mids.add(mid)

    tier2_hyp_mids: set[str] = set()
    for hrec in hypotheses.values():
        for field in ("supporting_material_ids", "counter_material_ids"):
            for mid in hrec.get(field) or ():
                if isinstance(mid, str) and mid in materials:
                    tier2_hyp_mids.add(mid)

    sess_order = {sid: idx for idx, sid in enumerate(sessions.keys())}
    hand_read_sessions: dict[str, list[str]] = defaultdict(list)
    active_read_sessions: dict[str, set[str]] = defaultdict(set)
    for rrec in read_log.values():
        tgt = rrec.get("target")
        if not isinstance(tgt, dict) or tgt.get("type") != "material":
            continue
        # The archive's layer-2 vocabulary includes counted but explicitly
        # excludes both declined and used_as_context. Searching the note for the
        # word バックフィル alone also misses manual context/decline rows and can
        # wrongly discard a real quotation *about* backfills.
        if rrec.get("reading") not in HANDWRITTEN_READINGS:
            continue
        mid = str(tgt.get("id") or "")
        sid = str(rrec.get("session_id") or "")
        if mid in materials and sid:
            if sid not in hand_read_sessions[mid]:
                hand_read_sessions[mid].append(sid)
            if rrec.get("reading") in associations.ACTIVE_READINGS:
                active_read_sessions[mid].add(sid)

    anchor_session: dict[str, str] = {}
    for sid, srec in sessions.items():
        for mid in srec.get("context_material_ids") or ():
            if isinstance(mid, str) and mid in materials and mid not in anchor_session:
                anchor_session[mid] = sid
    for mid, sids in hand_read_sessions.items():
        if mid not in anchor_session and sids:
            sids_sorted = sorted(sids, key=lambda s: sess_order.get(s, 10**9))
            anchor_session[mid] = sids_sorted[0]

    eval_sessions_by_mat: dict[str, set[str]] = defaultdict(set)
    for evl in evaluations.values():
        esid = str(evl.get("session_id") or "")
        for mid in evl.get("material_ids") or ():
            if isinstance(mid, str) and mid in materials and esid:
                eval_sessions_by_mat[mid].add(esid)

    tier_stats: dict[str, Counter[str]] = {
        "tier0_unwired": Counter(),
        "tier1_note_claim": Counter(),
        "tier2_hypothesis": Counter(),
    }
    temperature_counts: Counter[str] = Counter()
    pre_2026_11_counts: Counter[str] = Counter()
    any_session_counts: Counter[str] = Counter()
    tier0_candidates: list[dict[str, Any]] = []

    for mid, mrec in materials.items():
        any_read = bool(hand_read_sessions.get(mid))
        any_eval = bool(eval_sessions_by_mat.get(mid))
        any_session_counts[
            "read_and_eval" if any_read and any_eval else
            "read_only" if any_read else "eval_only" if any_eval else "neither"
        ] += 1
        anchor = anchor_session.get(mid)
        # An unknown anchor does not make every recorded session "different".
        read_sessions = set(hand_read_sessions.get(mid, ())) - {anchor} if anchor else set()
        eval_sessions = eval_sessions_by_mat.get(mid, set()) - {anchor} if anchor else set()
        has_read = bool(read_sessions)
        has_eval = bool(eval_sessions)
        rec_day = belief_state._record_iso_day(mrec, mid)
        # This is a record/ID label, which may differ from the execution date.
        is_early = bool(rec_day and rec_day < "2026-11-01") or mid.startswith(("MAT-0", "MAT-1", "MAT-202610", "MAT-LIT-202610", "MAT-TRC-202610"))

        if mid in tier2_hyp_mids:
            tkey = "tier2_hypothesis"
            temp = "hot_gist"
        elif mid in tier1_claim_mids:
            tkey = "tier1_note_claim"
            temp = "hot_gist"
        else:
            tkey = "tier0_unwired"
            temp = "warm_unwired" if has_read else "cold_verbatim"

        stats = tier_stats[tkey]
        stats["total"] += 1
        if not anchor:
            stats["anchor_unknown"] += 1
            if eval_sessions_by_mat.get(mid):
                stats["unknown_anchor_with_any_eval"] += 1
        else:
            stats["anchor_known"] += 1
            if has_read and not (active_read_sessions.get(mid, set()) - {anchor}):
                stats["non_anchor_counted_only"] += 1
            if has_read and has_eval:
                stats["read_and_eval"] += 1
                if read_sessions & eval_sessions:
                    stats["read_and_eval_shared_session"] += 1
            elif has_read:
                stats["read_only"] += 1
            elif has_eval:
                stats["eval_only"] += 1
            else:
                stats["neither"] += 1

        temperature_counts[temp] += 1
        if is_early:
            pre_2026_11_counts["total"] += 1
            pre_2026_11_counts[temp] += 1

        if tkey == "tier0_unwired" and (has_read or is_early):
            vstat = str(((mrec.get("verification") or {}).get("status")) or "unrecorded")
            qids = q_by_mat.get(mid, [])
            core_qids = [q for q in qids if q in belief_state.CORE_QUESTIONS]
            if has_read or (vstat == "verified" and core_qids):
                tier0_candidates.append(
                    {
                        "material_id": mid,
                        "title": str(mrec.get("title") or "")[:85],
                        "verification_status": vstat,
                        "temperature": temp,
                        "pre_2026_11": is_early,
                        # Legacy key names: these are different from the anchor,
                        # not necessarily subsequent in real time.
                        "subseq_read_sessions": len(read_sessions),
                        "subseq_eval_sessions": len(eval_sessions),
                        "question_ids": qids[:4],
                        "core_question_ids": core_qids,
                    }
                )

    def _rate_summary(d: Counter[str]) -> dict[str, Any]:
        def pct(numerator: int, denominator: int) -> float | None:
            return round(100.0 * numerator / denominator, 2) if denominator else None

        known = d["anchor_known"]
        both = d["read_and_eval"]
        read = both + d["read_only"]
        evaluation = both + d["eval_only"]
        return {
            "total": d["total"],
            "anchor_known": known,
            "anchor_unknown": d["anchor_unknown"],
            "unknown_anchor_with_any_eval": d["unknown_anchor_with_any_eval"],
            "read_and_eval": both,
            "read_only": d["read_only"],
            "eval_only": d["eval_only"],
            "neither": d["neither"],
            "read_and_eval_shared_session": d["read_and_eval_shared_session"],
            "read_and_eval_no_shared_session": both - d["read_and_eval_shared_session"],
            "non_anchor_counted_only": d["non_anchor_counted_only"],
            "eval_in_non_anchor_session": evaluation,
            "eval_rate_pct": pct(evaluation, known),
            # Existing JSON keys kept for callers; see method note in output.
            "stage1_subseq_read": read,
            "stage1_rate_pct": pct(read, known),
            "stage2_subseq_eval_given_stage1": both,
            "stage2_conversion_pct": pct(both, read),
        }

    tier0_candidates.sort(
        key=lambda r: (
            0 if r["verification_status"] == "verified" else 1,
            0 if r["core_question_ids"] else 1,
            -r["subseq_read_sessions"],
            0 if r["pre_2026_11"] else 1,
            r["material_id"],
        )
    )

    return {
        "total_materials": len(materials),
        "method": {
            "anchor": "first context mention in ledger order, else first layer-2 read in ledger order; not a birth date",
            "read_types": sorted(HANDWRITTEN_READINGS),
            "counted_is_not_interpretation": True,
            "event_order": "not established; non-anchor sessions can be the same, earlier, or later",
            "evaluations": "rows with a session ID, including voided evaluations; citation does not prove a posterior update",
            "tiers": "retrospective current notes/hypotheses; wiring may have been written after the read or evaluation",
            "temperature": "cold includes unknown anchors and means no qualifying non-anchor read record, not proof of non-reading",
            "pre_2026_11": "record/ID label, not necessarily real execution date",
            "denominators": "known anchors only; null when denominator is zero",
            "legacy_keys": "stage/subseq/conversion keys are associations, not evidence of a temporal or causal gate",
        },
        "temperature_tiers": dict(temperature_counts),
        "pre_2026_11_cohort": dict(pre_2026_11_counts),
        # Across all sessions; no record is not proof that reading did not occur.
        "any_session_read_eval": {k: any_session_counts[k] for k in ("read_and_eval", "read_only", "eval_only", "neither")},
        "two_stage_gate_by_tier": {k: _rate_summary(v) for k, v in tier_stats.items()},
        "top_tier0_candidates": tier0_candidates[:limit] if limit > 0 else tier0_candidates,
    }


def compact_unreferenced_shards(
    root: Path = _ROOT,
    *,
    apply: bool = False,
    max_per_collection: int = 5,
    before_date: str = "2026-11-15",
) -> dict[str, Any]:
    """Order-preserving non-destructive compaction of unreferenced same-day adjacent shards.

    Follows ``docs/parallel-work.md`` §3: merges adjacent same-day shards
    ``(s1, s2)`` strictly prior to ``before_date`` where ``s2.name`` has zero
    textual references anywhere in the repository (and no self-reference), while
    verifying that the collection's raw-byte union SHA-256 and record order are
    100% invariant before and after compaction.
    """
    root = Path(root).resolve()
    target_collections = (
        ("materials", "materials.jsonl"),
        ("read_log", "read_log.jsonl"),
        ("sessions", "sessions.jsonl"),
        ("notes", "notes.jsonl"),
        ("evaluations", "evaluations.jsonl"),
    )
    shard_names: set[str] = set()
    for _cname, fname in target_collections:
        sdir = root / "state" / f"{fname[:-6]}.d"
        if sdir.is_dir():
            for p in sdir.glob("*.jsonl"):
                shard_names.add(p.name)

    referenced: set[str] = set()
    scan_roots = [
        root / "readings",
        root / "docs",
        root / "taxonomy",
        root / "tools",
        root / "tests",
        root / "state",
        root / "prompts",
    ]
    top_mds = list(root.glob("*.md"))
    files_to_scan: list[Path] = list(top_mds)
    for sr in scan_roots:
        if sr.is_dir():
            files_to_scan.extend(p for p in sr.rglob("*") if p.is_file())

    NamePattern = re.compile(r"\b(2026-\d{2}-\d{2}-[A-Za-z0-9_.-]+\.jsonl)\b")
    for fpath in files_to_scan:
        try:
            txt = fpath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in NamePattern.finditer(txt):
            sname = m.group(1)
            if sname in shard_names:
                referenced.add(sname)

    def _collection_raw_digest(base_path: Path) -> tuple[str, int]:
        h = hashlib.sha256()
        total_bytes = 0
        for sp in ledger_io.collection_files(base_path):
            if not sp.is_file():
                continue
            raw = sp.read_bytes()
            h.update(raw)
            total_bytes += len(raw)
        return h.hexdigest(), total_bytes

    summary: dict[str, Any] = {}
    total_merged = 0
    for cname, fname in target_collections:
        base_path = root / "state" / fname
        sdir = ledger_io.shard_dir(base_path)
        if not sdir.is_dir():
            continue
        shards = sorted(sdir.glob("*.jsonl"))
        before_count = len(shards)
        before_sha, before_bytes = _collection_raw_digest(base_path)
        candidates: list[tuple[Path, Path]] = []
        idx = 0
        while idx < len(shards) - 1:
            s1, s2 = shards[idx], shards[idx + 1]
            d1, d2 = s1.name[:10], s2.name[:10]
            if (
                re.match(r"^\d{4}-\d{2}-\d{2}$", d1)
                and d1 == d2
                and d1 < before_date
                and s2.name not in referenced
            ):
                b1 = s1.read_bytes()
                b2 = s2.read_bytes()
                if b1.endswith(b"\n") and b2.endswith(b"\n"):
                    candidates.append((s1, s2))
                    if len(candidates) >= max_per_collection:
                        break
                    # Advance by 2 so planned pairs are disjoint in a single pass
                    idx += 2
                    continue
            idx += 1

        merged_pairs: list[dict[str, str]] = []
        if apply and candidates:
            for s1, s2 in candidates:
                b2 = s2.read_bytes()
                with s1.open("ab") as fh:
                    fh.write(b2)
                s2.unlink()
                merged_pairs.append({"into": s1.name, " absorbed": s2.name})
                total_merged += 1
            after_sha, after_bytes = _collection_raw_digest(base_path)
            if after_sha != before_sha or after_bytes != before_bytes:
                raise RuntimeError(
                    f"compaction digest mismatch on {cname}: {before_sha} != {after_sha}"
                )
        else:
            after_sha, after_bytes = before_sha, before_bytes

        summary[cname] = {
            "shards_before": before_count,
            "shards_after": len(sorted(sdir.glob("*.jsonl"))),
            "safe_disjoint_pairs_found": len(candidates),
            "merged_count": len(merged_pairs),
            "merged_pairs": [
                {"into": s1.name, "absorbed": s2.name} for s1, s2 in candidates
            ] if not apply else [
                {"into": p["into"], "absorbed": p[" absorbed"]} for p in merged_pairs
            ],
            "union_sha256": after_sha,
            "union_bytes": after_bytes,
        }

    return {
        "applied": apply,
        "before_date": before_date,
        "max_per_collection": max_per_collection,
        "total_shards_merged": total_merged,
        "collections": summary,
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
    mem_temp = memory_temperature_and_gate_audit(data, limit=10)
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
            "memory_temperature_and_two_stage_gate": mem_temp,
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


def _material_shard_map(root: Path) -> dict[str, Path]:
    base = Path(root).resolve() / "state" / "materials.jsonl"
    out: dict[str, Path] = {}
    paths = [base]
    sdir = ledger_io.shard_dir(base)
    if sdir.is_dir():
        paths.extend(sorted(sdir.glob("*.jsonl")))
    for p in paths:
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = obj.get("material_id")
            if isinstance(mid, str) and mid:
                out[mid] = p
    return out


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
    validate_seed.check_material_source_recording(data["materials"], errors, today=today)
    validate_seed.check_evaluation_descendant_collision(
        data["evaluations"], data["hypotheses"], errors, today=today
    )
    validate_seed.check_material_span_witness(
        data["materials"],
        errors,
        today=today,
        shard_of=_material_shard_map(root),
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


def _display_pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}%"


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
        *(
            [
                "  配線と読書・評価の共起     : "
                f"Hot(配線)={g1['memory_temperature_and_two_stage_gate']['temperature_tiers'].get('hot_gist', 0)} / "
                f"Warm(別セッション記録)={g1['memory_temperature_and_two_stage_gate']['temperature_tiers'].get('warm_unwired', 0)} / "
                f"Cold(別セッション記録なし・不明を含む)={g1['memory_temperature_and_two_stage_gate']['temperature_tiers'].get('cold_verbatim', 0)} | "
                f"評価記録∩読書記録 / 読書記録 Tier0={_display_pct(g1['memory_temperature_and_two_stage_gate']['two_stage_gate_by_tier']['tier0_unwired']['stage2_conversion_pct'])} / "
                f"Tier1={_display_pct(g1['memory_temperature_and_two_stage_gate']['two_stage_gate_by_tier']['tier1_note_claim']['stage2_conversion_pct'])} / "
                f"Tier2={_display_pct(g1['memory_temperature_and_two_stage_gate']['two_stage_gate_by_tier']['tier2_hypothesis']['stage2_conversion_pct'])}",
                "  注意: 同じ素材の記録の共起であり、読書→評価の時間順・変換・因果を示さない。現在の配線による事後分類。"
            ]
            if "memory_temperature_and_two_stage_gate" in g1
            else []
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
    parser.add_argument("--title", default="", help="candidate original-language title for --check-source")
    parser.add_argument("--author", default="", help="candidate first-author surname for --check-source")
    parser.add_argument("--year", type=int, default=None, help="candidate publication year for --check-source (with --author)")
    parser.add_argument("--source-audit", action="store_true", help="Gate 3: list same-source clusters, post-gate duplicates and DOI conflicts (read-only)")
    parser.add_argument("--fail-on-match", action="store_true", help="exit 1 if --check-source finds an exact identifier match")
    parser.add_argument("--verify-span", action="store_true", help="Gate 3: verify verbatim passage span(s) against fetched primary-source text and emit span_sha256 witness")
    parser.add_argument("--source-file", type=Path, default=None, help="path to fetched primary-source text/HTML file for --verify-span")
    parser.add_argument("--passage", default="", help="candidate material passage string for --verify-span")
    parser.add_argument("--passage-file", type=Path, default=None, help="path to file holding candidate material passage for --verify-span")
    parser.add_argument("--quote-status", default="verbatim", choices=sorted(validate_seed.QUOTE_STATUSES), help="quote_status mode for --verify-span (default: verbatim)")
    parser.add_argument("--upgrade-candidates", action="store_true", help="Gate 3: list high-leverage non-verified materials to re-verify via editorial_decisions")
    parser.add_argument("--tier0-candidates", action="store_true", help="describe retrospective read/evaluation overlap and list unwired candidates (not a temporal or causal gate)")
    parser.add_argument("--compact-shards", action="store_true", help="Maintenance: inspect or apply order-preserving same-day unreferenced shard compaction")
    parser.add_argument("--apply", action="store_true", help="when used with --compact-shards, execute compaction and verify SHA-256 invariance")
    parser.add_argument("--max-per-collection", type=int, default=5, help="max disjoint shard pairs to merge per collection under --compact-shards (default 5)")
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

    if args.source_audit:
        data, _err = load_archive(args.root)
        res = source_duplicate_audit(data["materials"])
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"same-source clusters: {res['clusters']} (extra rows {res['extra_rows']})")
            print(f"rows minted on/after {res['post_gate_cutoff']} repeating an earlier row: {len(res['post_gate_duplicates'])}")
            for r in res["post_gate_duplicates"]:
                print(f"  DUP   {r['material_id']} <- {', '.join(r['earlier'])} [{r['cause']}] {r['source_title'][:60]}")
            print(f"clusters with two or more DOIs: {len(res['doi_conflict_clusters'])}")
            for r in res["doi_conflict_clusters"]:
                print(f"  DOI   {', '.join(r['material_ids'])}: {' | '.join(r['dois'])}")
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
            author=args.author,
            year=args.year,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS: {res['status']}  (queried={res['queried_identifiers']})")
            for label, key in (("EXACT", "exact_identifier_matches"), ("NOTE ", "note_identifier_matches")):
                for m in res[key]:
                    print(
                        f"  {label}  {m['material_id']} [{m['verification_status']}] "
                        f"matched={m['matched_on']}  {m['title'][:75]}"
                    )
            for label, key in (("TITLE", "similar_title_matches"), ("RELTD", "related_title_matches")):
                for m in res[key]:
                    print(
                        f"  {label}  {m['material_id']} [{m['verification_status']}] "
                        f"sim={m['title_similarity']:.2f} via {m['matched_field']}  {m['matched_title'][:75]}"
                    )
            for m in res["author_year_matches"]:
                print(
                    f"  AUTHR  {m['material_id']} [{m['verification_status']}] "
                    f"year={m['year']}  {(m['source_title'] or m['title'])[:75]}"
                )
            if res["editorial_upgrade_template"]:
                print(
                    "  HINT : Cite the existing MAT-* directly; if you verified its full text, "
                    "append an editorial_decisions overlay (target.type='material', status='verified')."
                )
            for line in res["advisories"]:
                print(f"  NOTE : {line}")
        if args.fail_on_match and res["exact_identifier_matches"]:
            return 1
        return 0

    if args.verify_span:
        passage = args.passage
        if args.passage_file is not None:
            passage = args.passage_file.read_text(encoding="utf-8")
        source_text = ""
        if args.source_file is not None:
            source_text = args.source_file.read_text(encoding="utf-8")
        res = verify_passage_against_source(
            passage,
            source_text,
            quote_status=args.quote_status,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        elif res["ok"]:
            print(f"STATUS: {res['status']}  (quote_status={res['quote_status']})")
            print("  verification snippet:")
            print("  " + json.dumps(res["verification_fields"], ensure_ascii=False))
        else:
            print(f"STATUS: {res['status']}  (quote_status={res['quote_status']})", file=sys.stderr)
            print(f"  REASON: {res.get('reason', '')}", file=sys.stderr)
            if "missing_segment" in res:
                print(f"  MISSING_SEGMENT: {res['missing_segment']!r}", file=sys.stderr)
        return 0 if res["ok"] else 1

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

    if args.tier0_candidates:
        data, _err = load_archive(args.root)
        mt = memory_temperature_and_gate_audit(data, limit=args.limit)
        if args.json:
            print(json.dumps(mt, ensure_ascii=False, indent=2))
        else:
            tiers = mt["temperature_tiers"]
            g = mt["two_stage_gate_by_tier"]
            print(f"=== Retrospective read/evaluation overlap (total={mt['total_materials']:,} materials) ===")
            print(
                f"  Temperature: Hot(wired)={tiers.get('hot_gist', 0)} | "
                f"Warm(unwired, non-anchor read record)={tiers.get('warm_unwired', 0)} | "
                f"Cold(no such record or unknown anchor)={tiers.get('cold_verbatim', 0)}"
            )
            print("  R = layer-2 read record; E = evaluation citation, each in a session != heuristic anchor.")
            print("  Different sessions are not necessarily later; R and E may precede each other or share a session.")
            print("  Tiers use current wiring; counted is included, declined and used_as_context are excluded.")
            all_s = mt["any_session_read_eval"]
            print(
                "  Any session (no anchor): "
                f"R∩E={all_s['read_and_eval']} R-only={all_s['read_only']} "
                f"E-only={all_s['eval_only']} neither={all_s['neither']} "
                "(no record ≠ proof of no reading; citations include voided rows)."
            )
            for k, v in g.items():
                print(
                    f"  {k:18s}: total={v['total']:>4} anchored={v['anchor_known']:>4} unknown={v['anchor_unknown']:>3} | "
                    f"R∩E={v['read_and_eval']:>3} R-only={v['read_only']:>4} "
                    f"E-only={v['eval_only']:>3} neither={v['neither']:>4} | "
                    f"same-session={v['read_and_eval_shared_session']:>3} "
                    f"no-shared-session={v['read_and_eval_no_shared_session']:>3} | "
                    f"counted-only in R={v['non_anchor_counted_only']:>3} | "
                    f"(R∩E)/R={_display_pct(v['stage2_conversion_pct'])}"
                )
            print("  Same-session overlap does not establish event order; no rate here is an intervention effect.")
            print(
                f"\n  Top {min(args.limit, len(mt['top_tier0_candidates']))} unwired candidates (manual review, not an automatic wiring mandate):"
            )
            for r in mt["top_tier0_candidates"]:
                early_tag = "label<11" if r["pre_2026_11"] else "other-label"
                q_tag = ",".join(r["core_question_ids"] or r["question_ids"]) or "-"
                print(
                    f"  {r['material_id']} [{r['verification_status']:18s}] "
                    f"temp={r['temperature']:13s} {early_tag:11s} "
                    f"non-anchor-read-sessions={r['subseq_read_sessions']:>2} Q={q_tag:11s}  {r['title'][:52]}"
                )
        return 0

    if args.compact_shards:
        comp = compact_unreferenced_shards(
            args.root,
            apply=args.apply,
            max_per_collection=args.max_per_collection,
        )
        if args.json:
            print(json.dumps(comp, ensure_ascii=False, indent=2))
        else:
            mode = "APPLIED" if comp["applied"] else "DRY-RUN"
            print(
                f"=== Order-Preserving Same-Day Unreferenced Shard Compaction ({mode}, before={comp['before_date']}) ==="
            )
            for cname, info in comp["collections"].items():
                print(
                    f"  {cname:12s}: shards {info['shards_before']:>3} -> {info['shards_after']:>3}  "
                    f"candidates={info['safe_disjoint_pairs_found']}  merged={info['merged_count']}  "
                    f"sha256={info['union_sha256'][:12]}..."
                )
                for p in info["merged_pairs"]:
                    print(f"    - {p['into']}  <=  {p['absorbed']}")
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
