#!/usr/bin/env python3
"""What the cognitive-science reports were made of, and what could move them (read-only).

``cogsci_corpus.py`` (report H) measured the *form* of the series.  This tool
measures the layer under it, which H's own §10 left open:

  substrate   what the reports cited: how much is the archive's own Japanese
              paraphrase, how much of its literary holding the series touched.
  abstain     whether ``partially_verified`` / ``depth: abstract`` /
              ``scope_note`` mark a limitation or an acquisition format, and
              what the ``verified`` rows say they actually read.
  grip        whether the series moved the belief distribution, through which
              ledger field, under *both* bases, with a same-day control.
  lineage     the leaders decomposed into own and inherited log-odds.
  person      the grammatical shape of the human: separated, or one thing.

It never writes: every counterfactual is computed in memory through
``belief_state.compute_belief_state``.  It does not judge whether a verdict was
right, and it does not read the sources -- counting a passage's opening marker
is not checking it against the paper.

Determinism: fixed files at a fixed commit, no mtime, no git, no today's date.
The control uses a fixed seed.  Measured 2026-11-23 over four runs: the default
basis is byte-stable (242 of 247 fields), and five ``gated_tvd`` values move by
at most 1e-4 -- the receiver-gated path's arithmetic is order-sensitive.  Read
P_gate comparisons at three decimals, not four.
``SELF_REPORTS_CURRENT`` excludes this session's report and reading record, as
report H did for itself; ``--no-self-exclusion`` reports the sensitivity.

Usage
-----
  python3 tools/cogsci_substrate.py [--section substrate|abstain|grip|lineage|person]
                                    [--json] [--no-self-exclusion]
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import cogsci_corpus as cc  # noqa: E402

# This session's report and its reading record.  Report H did the same with its
# own two files; see its §0.  Both names are stable after this session commits.
SELF_REPORTS_CURRENT = frozenset(
    {
        "COGNITIVE_SCIENCE_REPORT_2026-11-23-I.md",
        "2026-11-23-what-the-cognitive-science-reports-were-made-of.md",
    }
)

# Ledger-id shapes.  Uppercase-agnostic on the suffix: the archive's own
# instructions record that ``MAT-[A-Z0-9-]+`` misses every lower-hex id.
_MAT = re.compile(r"\bMAT-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")
_SESSION = re.compile(r"SESSION-\d{8}-[0-9a-f]{6}")
_SENTENCE = re.compile(r"(?<=[。．！？])")

# How the archive's own summary announces itself.  A passage that opens with a
# paraphrase marker is the archive's Japanese restatement of a source, not a
# quotation from it.  The list is deliberately small and literal.
PARAPHRASE_MARKERS: tuple[str, ...] = ("公開抄録", "二次記録", "要約", "抄録", "編者", "原文", "全文")

# Separation vs identity in the answer to "what is a human": does the corpus say
# the human is several dissociable processes, or one thing with a nature?
# These are the archive's own words for its own findings; the tool counts them
# and does not claim the counts are a philosophical position.
SEPARATION_SHAPES = re.compile(
    r"(分離|解離|二層|独立|別々|分かれ|乖離|二重|切り離|分ける|異なる|区別|二つに分|別の過程)"
)
IDENTITY_SHAPES = re.compile(r"(同一である|同じである|一体|一つの存在|単一の存在|本質|変わらない|等しい)")

# What a verification.method / note says the check actually reached.  A row is
# "deep" when the archive's own prose says it reached the body; "shallow" when it
# says abstract or bibliography.  This is the archive describing itself, not a
# re-check of the source: tools/depth_backfill.py makes the same distinction
# archive-wide and refuses to write, because a downgrade moves P_gate.
_DEEP_CHECK = re.compile(r"(full_text_pdf_read|全 ?chunk|chunk 取得|本文を|本文・|本文の|全文|通読|導入)")
_SHALLOW_CHECK = re.compile(r"(抄録|abstract|Abstract|書誌|bibliograph)")

# Sentinel for "remove this key" in the grip counterfactuals.
_DROP = object()

# Caution words, for the comparison between an annotation and a sentence.
LIMIT_WORDS = re.compile(
    r"(測っていない|検定していない|未測定|未検定|外挿しない|言えない|判断しない|"
    r"行っていない|していない|できない|範囲でしか|限られる|不明|限界|に限る)"
)


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def _load_rows(collection: str, root: Path = ROOT) -> list[dict[str, Any]]:
    base = Path(root) / "state" / f"{collection}.jsonl"
    files = [base] if base.is_file() else []
    shard_dir = Path(root) / "state" / f"{collection}.d"
    if shard_dir.is_dir():
        files.extend(sorted(shard_dir.glob("*.jsonl")))
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            handle = path.open(encoding="utf-8")
        except OSError:
            continue
        with handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _sentences(text: str) -> list[str]:
    return [s for s in _SENTENCE.split(text) if s.strip()]


def discover_reports(root: Path = ROOT, *, exclude_self: bool = True) -> list[dict[str, Any]]:
    """The 90-report corpus, discovered by ``cogsci_corpus``'s lexical rule."""
    reports = cc.discover(root)
    if exclude_self:
        reports = [r for r in reports if r["name"] not in SELF_REPORTS_CURRENT]
    return reports


def corpus_session_ids(reports: list[dict[str, Any]]) -> set[str]:
    """Every session stamp named in the reports.

    A report's own session stamp is what ties it to the rows it wrote, so this
    union is the operational definition of "the sessions that produced the
    corpus". Two reports name no session and one names a session that has no
    row; those are counted in ``substrate.unnamed_sessions`` rather than guessed.
    """
    ids: set[str] = set()
    for report in reports:
        ids |= set(_SESSION.findall(report["text"]))
    return ids


# ---------------------------------------------------------------------------
# section: substrate
# ---------------------------------------------------------------------------

def section_substrate(reports: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """What the series cited, and what it left uncited."""
    materials = {m["material_id"]: m for m in _load_rows("materials", root)}
    sessions = {s["session_id"] for s in _load_rows("sessions", root)}

    cited: Counter[str] = Counter()
    per_report: list[dict[str, Any]] = []
    for report in reports:
        ids = sorted(set(_MAT.findall(report["text"])))
        for mid in ids:
            cited[mid] += 1
        per_report.append({"name": report["name"], "materials": ids})

    by_kind: Counter[str] = Counter()
    for mid in cited:
        by_kind[materials.get(mid, {}).get("kind") or "unresolved"] += 1

    research = [mid for mid in cited if materials.get(mid, {}).get("kind") == "research_excerpt"]
    literary_archive = [mid for mid, rec in materials.items() if rec.get("kind") == "literary_text"]
    literary_cited = [mid for mid in cited if materials.get(mid, {}).get("kind") == "literary_text"]

    # A passage that opens with one of the paraphrase markers is the archive's
    # restatement.  Position matters: the marker is in the first 40 characters.
    para, quoted, other = 0, 0, 0
    lang: Counter[str] = Counter()
    depth: Counter[str] = Counter()
    status: Counter[str] = Counter()
    for mid in research:
        rec = materials.get(mid) or {}
        passage = (rec.get("passage") or "").strip()
        head = passage[:40]
        if any(marker in head for marker in ("編者による要約", "編者", "要約", "抄録", "二次記録")):
            para += 1
        elif "原文" in head or "全文" in head:
            quoted += 1
        else:
            other += 1
        lang[rec.get("passage_language") or "unknown"] += 1
        verification = rec.get("verification") or {}
        depth[verification.get("depth") or "unrecorded"] += 1
        status[verification.get("status") or "unrecorded"] += 1

    # Encounter again: did any *other* session hand-read a cited material?
    # Mechanical backfills are excluded — they are a transcription of
    # sessions.context_material_ids, not a reading.
    cited_set = set(cited)
    read_rows = [
        r
        for r in _load_rows("read_log", root)
        if isinstance(r.get("target"), dict)
        and r["target"].get("type") == "material"
        and r["target"].get("id") in cited_set
        and "機械的バックフィル" not in (r.get("note") or "")
    ]
    by_material: dict[str, set[str]] = defaultdict(set)
    for row in read_rows:
        by_material[row["target"]["id"]].add(row["session_id"])
    re_read = {mid: sess for mid, sess in by_material.items() if len(sess) > 1}

    # Acquisitions in the window, to compare the series' own intake.
    window = {"20261118", "20261119", "20261120", "20261121", "20261122", "20261123"}
    intake: Counter[str] = Counter()
    for mid, rec in materials.items():
        match = re.match(r"MAT-(?:[A-Z]+-)?(\d{8})-", mid) or re.match(r"MAT-(\d{8})-", mid)
        if match and match.group(1) in window:
            intake[rec.get("kind") or "unknown"] += 1

    return {
        "reports": len(reports),
        "citations": sum(cited.values()),
        "distinct_cited": len(cited),
        "distinct_resolved": sum(1 for mid in cited if mid in materials),
        "cited_by_kind": dict(sorted(by_kind.items(), key=lambda kv: -kv[1])),
        "reports_with_no_material": sum(1 for r in per_report if not r["materials"]),
        "research_cited": len(research),
        "research_passage_opening": {
            "paraphrase_marker": para,
            "quotation_marker": quoted,
            "marker_absent": other,
        },
        "research_passage_language": dict(sorted(lang.items(), key=lambda kv: -kv[1])),
        "research_depth": dict(sorted(depth.items(), key=lambda kv: -kv[1])),
        "research_status": dict(sorted(status.items(), key=lambda kv: -kv[1])),
        "archive_literary": len(literary_archive),
        "literary_cited": len(literary_cited),
        "literary_cited_ids": sorted(literary_cited),
        "hand_read_materials": len(by_material),
        "hand_reread_materials": len(re_read),
        "hand_reread_share": round(len(re_read) / len(by_material), 4) if by_material else 0.0,
        "archive_intake_in_window": dict(sorted(intake.items(), key=lambda kv: -kv[1])),
        "unnamed_sessions": list(
            sorted(set(_SESSION.findall("".join(r["text"] for r in reports))) - sessions)
        ),
    }


# ---------------------------------------------------------------------------
# section: abstain
# ---------------------------------------------------------------------------

def section_abstain(reports: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """Is the caution in the annotations, or in the sentences?"""
    materials = {m["material_id"]: m for m in _load_rows("materials", root)}
    notes = _load_rows("notes", root)
    evaluations = _load_rows("evaluations", root)
    session_ids = corpus_session_ids(reports)
    paths = {r["path"] for r in reports}

    cited: Counter[str] = Counter()
    for report in reports:
        for mid in set(_MAT.findall(report["text"])):
            cited[mid] += 1
    research = [mid for mid in cited if materials.get(mid, {}).get("kind") == "research_excerpt"]

    def limit_rate(texts: Iterable[str]) -> tuple[int, int]:
        hits = total = 0
        for text in texts:
            for sentence in _sentences(text):
                total += 1
                if LIMIT_WORDS.search(sentence):
                    hits += 1
        return hits, total

    def neg_rate(texts: Iterable[str]) -> tuple[int, int]:
        hits = total = 0
        for text in texts:
            for sentence in _sentences(text):
                total += 1
                if cc._NEGATION.search(sentence):
                    hits += 1
        return hits, total

    material_prose = [
        (materials[mid].get("passage") or "")
        + (materials[mid].get("context") or "")
        + (materials[mid].get("scope_note") or "")
        for mid in research
    ]
    scope_only = [(materials[mid].get("scope_note") or "") for mid in research]
    corpus_notes = [n for n in notes if n.get("path") in paths]
    other_notes = [n for n in notes if n.get("path") not in paths]
    corpus_claims = [c.get("text") or "" for n in corpus_notes for c in n.get("claims") or []]
    other_claims = [c.get("text") or "" for n in other_notes for c in n.get("claims") or []]
    corpus_evals = [e for e in evaluations if e.get("session_id") in session_ids]
    other_evals = [e for e in evaluations if e.get("session_id") not in session_ids]

    def ratio(pair: tuple[int, int]) -> dict[str, Any]:
        hits, total = pair
        return {"hits": hits, "sentences": total, "rate": round(hits / total, 4) if total else 0.0}

    # The annotation that most looks like a limitation, set against the prose.
    partially = sum(
        1 for mid in research if (materials[mid].get("verification") or {}).get("status") == "partially_verified"
    )
    abstract = sum(
        1 for mid in research if (materials[mid].get("verification") or {}).get("depth") == "abstract"
    )

    # Does a `verified` row's own prose say it reached the body?
    verified = [
        mid for mid in research if (materials[mid].get("verification") or {}).get("status") == "verified"
    ]
    deep = shallow = unclear = 0
    for mid in verified:
        verification = materials[mid].get("verification") or {}
        text = (verification.get("method") or "") + " " + (verification.get("note") or "")
        if _DEEP_CHECK.search(text):
            deep += 1
        elif _SHALLOW_CHECK.search(text):
            shallow += 1
        else:
            unclear += 1

    return {
        "reports": len(reports),
        "corpus_sessions_resolved": len(session_ids),
        "notes_wired": len({n.get("path") for n in corpus_notes}),
        "notes_missing": len(paths - {n.get("path") for n in corpus_notes}),
        "corpus_claims": len(corpus_claims),
        "limit_words": {
            "corpus_claims": ratio(limit_rate(corpus_claims)),
            "other_claims": ratio(limit_rate(other_claims)),
            "cited_material_prose": ratio(limit_rate(material_prose)),
            "cited_scope_note_only": ratio(limit_rate(scope_only)),
        },
        "negation_words": {
            "corpus_claims": ratio(neg_rate(corpus_claims)),
            "other_claims": ratio(neg_rate(other_claims)),
            "cited_material_prose": ratio(neg_rate(material_prose)),
            "corpus_eval_summaries": ratio(neg_rate([e.get("summary") or "" for e in corpus_evals])),
            "other_eval_summaries": ratio(neg_rate([e.get("summary") or "" for e in other_evals])),
        },
        "annotation": {
            "cited_research": len(research),
            "partially_verified": partially,
            "depth_abstract": abstract,
        },
        "verified_self_description": {
            "verified_rows": len(verified),
            "method_says_body": deep,
            "method_says_abstract_or_bibliography": shallow,
            "method_says_neither": unclear,
            "depth_recorded": sum(
                1 for mid in verified if (materials[mid].get("verification") or {}).get("depth")
            ),
        },
    }


# ---------------------------------------------------------------------------
# section: grip
# ---------------------------------------------------------------------------

def _posterior_map(state: dict[str, Any], question_id: str) -> dict[str, float]:
    return {
        h["hypothesis_id"]: float(h["posterior"])
        for h in state["questions"][question_id]["hypotheses"]
    }


def _top(state: dict[str, Any], question_id: str) -> tuple[str, float]:
    rows = state["questions"][question_id]["hypotheses"]
    best = max(rows, key=lambda h: (h["posterior"], h["hypothesis_id"]))
    return best["hypothesis_id"], round(best["posterior"] * 100, 2)


def _tvd(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) | set(b)
    return round(0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys), 4)


def section_grip(reports: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """Did the series move the belief, and through which field?

    Every counterfactual is an in-memory copy of the ledgers handed to
    ``belief_state.compute_belief_state``. Nothing is written.
    """
    import belief_state as bs

    data = bs.load_belief_ledgers(root)
    session_ids = corpus_session_ids(reports)
    # Both bases the archive reports side by side in BELIEF_MAP.md.  Which one
    # is used is a fact about the reader, not about the corpus: the citation
    # fields are read by the receiver-gated basis (P_gate) and ignored by the
    # default one.  Measuring only one would attribute the difference to the
    # corpus.
    baseline = bs.compute_belief_state(data)
    baseline_gated = bs.compute_belief_state(data, receiver_gated=True)

    corpus_rows = [
        eid for eid, rec in data["evaluations"].items() if rec.get("session_id") in session_ids
    ]
    touched = {data["evaluations"][eid]["target_hypothesis_id"] for eid in corpus_rows}
    verdicts = Counter(data["evaluations"][eid]["verdict"] for eid in corpus_rows)
    evidence = Counter(data["evaluations"][eid]["evidence_type"] for eid in corpus_rows)
    QIDS = ("Q-001", "Q-002", "Q-003")

    def run(mutate) -> dict[str, Any]:
        clone = copy.deepcopy(data)
        mutate(clone)
        out: dict[str, Any] = {"top": {}, "tvd": {}, "gated_top": {}, "gated_tvd": {}}
        for tag, state, base in (
            ("", bs.compute_belief_state(clone), baseline),
            ("gated_", bs.compute_belief_state(clone, receiver_gated=True), baseline_gated),
        ):
            for qid in QIDS:
                hid, pct = _top(state, qid)
                out[f"{tag}top"][qid] = {"hypothesis_id": hid, "posterior_pct": pct}
                out[f"{tag}tvd"][qid] = _tvd(_posterior_map(base, qid), _posterior_map(state, qid))
        return out

    def set_field(field: str, value):
        def mutate(clone: dict[str, Any]) -> None:
            for eid in corpus_rows:
                if value is _DROP:
                    clone["evaluations"][eid].pop(field, None)
                else:
                    clone["evaluations"][eid][field] = value

        return mutate

    def removed(clone: dict[str, Any]) -> None:
        for eid in corpus_rows:
            clone["evaluations"].pop(eid, None)

    def score(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """How many of the corpus's attested hypotheses each counterfactual keeps on top.

        The corpus attests a hypothesis when it filed at least one evaluation
        against it. ``top_overlap`` is the count of questions whose top
        hypothesis under the counterfactual is also attested by the corpus.
        """
        attested = touched
        return {
            qid: {
                "top_is_attested_by_corpus": sections["top"][qid]["hypothesis_id"] in attested,
            }
            for qid in sections["top"]
        }

    counterfactuals = {
        "as_recorded": run(lambda clone: None),
        "rows_removed": run(removed),
        "all_supports": run(set_field("verdict", "supports")),
        "all_narrows_scope": run(set_field("verdict", "narrows_scope")),
        "all_primary_source_collision": run(set_field("evidence_type", "primary_source_collision")),
        "all_cross_session_audit": run(set_field("evidence_type", "cross_session_audit")),
        "comparison_cleared": run(set_field("compared_against_hypothesis_ids", [])),
        "script_command_cleared": run(set_field("script_command", _DROP)),
        "material_ids_cleared": run(set_field("material_ids", [])),
        "note_ids_cleared": run(set_field("note_ids", [])),
    }
    for name, section in counterfactuals.items():
        section["top_attested"] = score(section)
    baseline_tops = {
        "default": {qid: _top(baseline, qid) for qid in QIDS},
        "gated": {qid: _top(baseline_gated, qid) for qid in QIDS},
    }

    # Control: the same *number* of evaluation rows drawn at random from the
    # rows of the same calendar days that the corpus did not write.  Without it
    # a large TVD cannot be read: every core question here has few evaluations,
    # so deleting any eighty-odd rows may move it.  What the control measures is
    # whether the corpus' rows are special, not whether removing rows moves the
    # distribution.
    days = sorted({str(data["evaluations"][eid].get("created_at") or "")[:10] for eid in corpus_rows})
    control_pool = [
        eid
        for eid, rec in data["evaluations"].items()
        if eid not in set(corpus_rows) and str(rec.get("created_at") or "")[:10] in days
    ]
    import random

    rng = random.Random(20261123)  # fixed seed: the numbers must be re-runnable
    draws: list[dict[str, Any]] = []
    for _ in range(12):
        picks = rng.sample(control_pool, min(len(corpus_rows), len(control_pool)))
        picks_set = set(picks)

        def drop_control(clone: dict[str, Any], picks_set: set[str] = picks_set) -> None:
            for eid in picks_set:
                clone["evaluations"].pop(eid, None)

        section = run(drop_control)
        draws.append(
            {
                "q001_top": section["top"]["Q-001"]["hypothesis_id"],
                "q001_tvd": section["tvd"]["Q-001"],
                "q002_tvd": section["tvd"]["Q-002"],
                "q003_tvd": section["tvd"]["Q-003"],
            }
        )
    q1 = [d["q001_tvd"] for d in draws]
    return {
        "corpus_rows": len(corpus_rows),
        "evaluation_rows_total": len(data["evaluations"]),
        "hypotheses_attested": len(touched),
        "corpus_days": days,
        "verdicts": dict(sorted(verdicts.items(), key=lambda kv: -kv[1])),
        "evidence_types": dict(sorted(evidence.items(), key=lambda kv: -kv[1])),
        "baseline": baseline_tops,
        "counterfactuals": counterfactuals,
        "control": {
            "pool": len(control_pool),
            "draws": len(draws),
            "q001_tvd_min": min(q1) if q1 else None,
            "q001_tvd_max": max(q1) if q1 else None,
            "q001_top_counts": dict(Counter(d["q001_top"] for d in draws)),
            "q002_tvd_max": max((d["q002_tvd"] for d in draws), default=None),
            "q003_tvd_max": max((d["q003_tvd"] for d in draws), default=None),
        },
    }


# ---------------------------------------------------------------------------
# section: person
# ---------------------------------------------------------------------------

def section_person(reports: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """In what shape the human is written: separated processes or one nature.

    Report prose is read with report H's own convention so the two reports'
    numbers are comparable: table lines are dropped, and a sentence counts when
    the character string 人間 occurs in it.  Claims are a separate population —
    they are what survived into the ledger, not what the report argued.
    """
    notes = _load_rows("notes", root)
    paths = {r["path"] for r in reports}
    corpus_claims = [c.get("text") or "" for n in notes if n.get("path") in paths for c in n.get("claims") or []]
    other_claims = [c.get("text") or "" for n in notes if n.get("path") not in paths for c in n.get("claims") or []]

    def shape(texts: Iterable[str]) -> dict[str, Any]:
        sep = idn = total = 0
        for text in texts:
            for sentence in _sentences(text):
                total += 1
                if SEPARATION_SHAPES.search(sentence):
                    sep += 1
                if IDENTITY_SHAPES.search(sentence):
                    idn += 1
        return {
            "sentences": total,
            "separation": {"count": sep, "rate": round(sep / total, 4) if total else 0.0},
            "identity": {"count": idn, "rate": round(idn / total, 4) if total else 0.0},
            "ratio_sep_over_idn": round(sep / idn, 2) if idn else None,
        }

    # Report prose under H's convention: drop table rows, keep every sentence
    # that contains 人間, and count total sentences for the population.
    human_sentences: list[str] = []
    report_sentences = 0
    for report in reports:
        body = re.sub(r"^[|].*$", "", report["text"], flags=re.M)
        for sentence in _sentences(body):
            report_sentences += 1
            if "人間" in sentence:
                human_sentences.append(sentence)

    sep = sum(1 for s in human_sentences if SEPARATION_SHAPES.search(s))
    idn = sum(1 for s in human_sentences if IDENTITY_SHAPES.search(s))
    return {
        "corpus_notes": sum(1 for n in notes if n.get("path") in paths),
        "corpus_claims": len(corpus_claims),
        "claims": {"corpus": shape(corpus_claims), "other": shape(other_claims)},
        "report_sentences": report_sentences,
        "human_sentences": len(human_sentences),
        "human_sentences_separation": sep,
        "human_sentences_identity": idn,
        "human_sentences_with_negation": sum(1 for s in human_sentences if cc._NEGATION.search(s)),
    }



# ---------------------------------------------------------------------------
# section: lineage
# ---------------------------------------------------------------------------

def section_lineage(reports: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """How much of each leader's mass it wrote, and how much it inherited.

    ``belief_state.compute_belief_state`` keeps one ``log_odds`` per hypothesis
    and adds to it by two routes that this section separates by re-running the
    engine with ``heir_credit=False``:

    * the hypothesis' own rows (evaluations addressed to it);
    * the heir credit a ``narrows_scope`` / ``refutes_unconditioned`` row pays
      to the target's children -- including children registered *after* the row
      was written, because ``children_by_parent`` is built from the hypotheses
      that exist at read time (``tools/lineage_credit_accounting.py``).

    The two bases are both the engine's own: ``heir_credit`` is a documented
    switch, not a counterfactual this tool invented.  The difference between
    them is the increment attributable to heir credit; it is not a decomposition
    into independent causes, and the report says so.
    """
    import belief_state as bs

    data = bs.load_belief_ledgers(root)
    session_ids = corpus_session_ids(reports)
    with_heir = bs.compute_belief_state(data)
    without = bs.compute_belief_state(data, heir_credit=False)

    corpus_rows: Counter[str] = Counter()
    own_verdicts: dict[str, Counter[str]] = defaultdict(Counter)
    for rec in data["evaluations"].values():
        if rec.get("session_id") in session_ids:
            hid = rec.get("target_hypothesis_id")
            corpus_rows[hid] += 1
            own_verdicts[hid][rec.get("verdict")] += 1

    questions: dict[str, Any] = {}
    for qid in ("Q-001", "Q-002", "Q-003"):
        def rows(state: dict[str, Any]) -> list[dict[str, Any]]:
            return state["questions"][qid]["hypotheses"]

        def top(state: dict[str, Any]) -> dict[str, Any]:
            return max(rows(state), key=lambda h: (h["posterior"], h["hypothesis_id"]))

        def find(state: dict[str, Any], hid: str) -> dict[str, Any] | None:
            return next((h for h in rows(state) if h["hypothesis_id"] == hid), None)

        leaders = []
        for hid in [top(with_heir)["hypothesis_id"], top(without)["hypothesis_id"]]:
            a, b = find(with_heir, hid), find(without, hid)
            if a is None or b is None:
                continue
            if any(item["hypothesis_id"] == hid for item in leaders):
                continue
            leaders.append(
                {
                    "hypothesis_id": hid,
                    "log_odds_as_recorded": round(float(a["log_odds"]), 4),
                    "log_odds_without_heir_credit": round(float(b["log_odds"]), 4),
                    "heir_credit_increment": round(float(a["log_odds"]) - float(b["log_odds"]), 4),
                    "own_rows_in_corpus": corpus_rows.get(hid, 0),
                    "own_verdicts_in_corpus": dict(own_verdicts.get(hid, Counter())),
                    "posterior_as_recorded": round(float(a["posterior"]) * 100, 2),
                    "posterior_without_heir_credit": round(float(b["posterior"]) * 100, 2),
                }
            )

        # Every hypothesis of the question, for the count of leaders whose own
        # evidence is negative after the inherited part is set aside.
        own_negative = 0
        own_positive = 0
        for h in rows(with_heir):
            other = find(without, h["hypothesis_id"])
            if other is None:
                continue
            if float(other["log_odds"]) < 0.0:
                own_negative += 1
            else:
                own_positive += 1

        questions[qid] = {
            "top_as_recorded": top(with_heir)["hypothesis_id"],
            "top_without_heir_credit": top(without)["hypothesis_id"],
            "top_changed": top(with_heir)["hypothesis_id"] != top(without)["hypothesis_id"],
            "leaders": leaders,
            "hypotheses_with_negative_own_log_odds": own_negative,
            "hypotheses_with_positive_own_log_odds": own_positive,
        }

    return {
        "corpus_rows": sum(corpus_rows.values()),
        "hypotheses_the_corpus_addressed": len(corpus_rows),
        "questions": questions,
    }

# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def build_report(root: Path = ROOT, *, exclude_self: bool = True) -> dict[str, Any]:
    reports = discover_reports(root, exclude_self=exclude_self)
    return {
        "reports": len(reports),
        "self_excluded": sorted(SELF_REPORTS_CURRENT) if exclude_self else [],
        "substrate": section_substrate(reports, root),
        "abstain": section_abstain(reports, root),
        "grip": section_grip(reports, root),
        "lineage": section_lineage(reports, root),
        "person": section_person(reports, root),
    }


def _pct(pair: dict[str, Any]) -> str:
    return f"{pair['hits']}/{pair['sentences']} = {pair['rate'] * 100:.1f}%"


def render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    sub = report["substrate"]
    lines.append("== 基質（何を引いたか、何を引かなかったか） ==")
    lines.append(f"  報告 {report['reports']} 件 / 引用 {sub['citations']} 回 / 異なり {sub['distinct_cited']} 件（台帳に解決 {sub['distinct_resolved']}）")
    lines.append(f"  種別: {sub['cited_by_kind']}")
    lines.append(f"  素材IDを一つも名指さない報告: {sub['reports_with_no_material']} 件")
    lines.append(f"  研究資料 {sub['research_cited']} 件の passage 冒頭: {sub['research_passage_opening']}")
    lines.append(f"  passage_language: {sub['research_passage_language']}")
    lines.append(f"  depth: {sub['research_depth']}")
    lines.append(f"  status: {sub['research_status']}")
    lines.append(
        f"  書庫の文学資料 {sub['archive_literary']} 件のうち、この群が引いたもの {sub['literary_cited']} 件"
    )
    lines.append(
        f"  手読みされた素材 {sub['hand_read_materials']} 件 / 二セッション以上で読まれた {sub['hand_reread_materials']}"
        f" ({sub['hand_reread_share'] * 100:.1f}%)"
    )
    lines.append(f"  期間中の収蔵: {sub['archive_intake_in_window']}")
    lines.append(f"  台帳に解決しないセッション印: {sub['unnamed_sessions']}")

    abs_ = report["abstain"]
    lines.append("")
    lines.append("== 留保（注記か、文か） ==")
    lines.append(f"  群のセッション（解決分）: {abs_['corpus_sessions_resolved']} / ノート配線 {abs_['notes_wired']} 報告・未配線 {abs_['notes_missing']}")
    for key, pair in abs_["limit_words"].items():
        lines.append(f"  留保語 {key}: {_pct(pair)}")
    for key, pair in abs_["negation_words"].items():
        lines.append(f"  否定・留保語 {key}: {_pct(pair)}")
    lines.append(f"  注記: {abs_['annotation']}")
    vsd = abs_["verified_self_description"]
    lines.append(
        f"  `verified` の自己記述: 全 {vsd['verified_rows']} 件 / 本文に届く記述 {vsd['method_says_body']}"
        f" / 抄録・書誌のみの記述 {vsd['method_says_abstract_or_bibliography']}"
        f" / 判定不能 {vsd['method_says_neither']} / depth 記録あり {vsd['depth_recorded']}"
    )

    grip = report["grip"]
    lines.append("")
    lines.append("== 把持（読解は台帳の何を動かしたか） ==")
    lines.append(f"  群の評価行 {grip['corpus_rows']} / 全体 {grip['evaluation_rows_total']}・触れた仮説 {grip['hypotheses_attested']}")
    lines.append(f"  verdict: {grip['verdicts']}")
    lines.append(f"  evidence_type: {grip['evidence_types']}")
    lines.append("  反事実（書き込みなし・in-memory）:")
    for name, section in grip["counterfactuals"].items():
        tops = " | ".join(
            f"{qid}:{v['hypothesis_id']} {v['posterior_pct']:.1f}% (TVD {section['tvd'][qid]:.3f})"
            for qid, v in section["top"].items()
        )
        attested = "".join("+" if v["top_is_attested_by_corpus"] else "-" for v in section["top_attested"].values())
        gated = " | ".join(
            f"{qid}:{v['hypothesis_id']} {v['posterior_pct']:.1f}% (TVD {section['gated_tvd'][qid]:.3f})"
            for qid, v in section["gated_top"].items()
        )
        lines.append(f"    {name:32s} {tops}  首位が群の触れた仮説か: {attested}")
        lines.append(f"    {'':32s} P_gate: {gated}")
    control = grip["control"]
    lines.append(
        f"  対照（同暦日・同件数の非群評価行を {control['draws']} 回除去）: Q-001 TVD "
        f"{control['q001_tvd_min']}〜{control['q001_tvd_max']}, 首位 {control['q001_top_counts']}; "
        f"Q-002 最大 {control['q002_tvd_max']}, Q-003 最大 {control['q003_tvd_max']}"
    )

    lineage = report["lineage"]
    lines.append("")
    lines.append("== 系譜（首位の質量は、自分で書いたか、受け取ったか） ==")
    lines.append(f"  群が宛先にした仮説 {lineage['hypotheses_the_corpus_addressed']} 件 / 評価行 {lineage['corpus_rows']} 件")
    for qid, block in lineage["questions"].items():
        flag = "（順位が変わる）" if block["top_changed"] else ""
        lines.append(
            f"  {qid} 記録どおり首位 {block['top_as_recorded']} / heir_credit なし首位 "
            f"{block['top_without_heir_credit']} {flag}"
        )
        lines.append(
            f"       自分の log_odds が負の仮説 {block['hypotheses_with_negative_own_log_odds']} / 正 "
            f"{block['hypotheses_with_positive_own_log_odds']}"
        )
        for leader in block["leaders"]:
            lines.append(
                f"       {leader['hypothesis_id']} L={leader['log_odds_as_recorded']:.3f} "
                f"うち継承 {leader['heir_credit_increment']:.3f}（自分の分 "
                f"{leader['log_odds_without_heir_credit']:.3f}）"
                f" P {leader['posterior_as_recorded']:.2f}% → {leader['posterior_without_heir_credit']:.2f}%"
                f" 群の直接行 {leader['own_rows_in_corpus']} {leader['own_verdicts_in_corpus']}"
            )

    person = report["person"]
    lines.append("")
    lines.append("== 人間の現れ方（分離か、同一か） ==")
    for scope in ("corpus", "other"):
        block = person["claims"][scope]
        lines.append(
            f"  {scope} claims: 文 {block['sentences']} / 分離 {block['separation']['count']}"
            f" ({block['separation']['rate'] * 100:.1f}%) / 同一 {block['identity']['count']}"
            f" ({block['identity']['rate'] * 100:.1f}%) / 比 {block['ratio_sep_over_idn']}"
        )
    lines.append(
        f"  報告本文: 文 {person['report_sentences']} / 人間を含む文 {person['human_sentences']}"
        f"（分離 {person['human_sentences_separation']} / 同一 {person['human_sentences_identity']}"
        f" / 否定・留保 {person['human_sentences_with_negation']}）"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument(
        "--section",
        choices=("substrate", "abstain", "grip", "lineage", "person"),
        help="one section only (default: all four)",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--no-self-exclusion",
        action="store_true",
        help="count this session's own report too (the sensitivity check)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root)
    exclude = not args.no_self_exclusion
    if args.section:
        reports = discover_reports(root, exclude_self=exclude)
        payload = {
            "reports": len(reports),
            "self_excluded": sorted(SELF_REPORTS_CURRENT) if exclude else [],
            args.section: {
                "substrate": section_substrate,
                "abstain": section_abstain,
                "grip": section_grip,
                "lineage": section_lineage,
                "person": section_person,
            }[args.section](reports, root),
        }
    else:
        payload = build_report(root, exclude_self=exclude)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
    elif args.section:
        print(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
    else:
        print(render_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
