#!/usr/bin/env python3
"""Validate the seed ledgers and their cross-references (stdlib only).

Implements the JSON-Schema subset used in schema/*.schema.json plus checks
that IDs referenced across JSONL collections actually exist.
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any

import ledger_ids
import ledger_io

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = {
    "questions": ("questions.jsonl", "question_id", "question.schema.json"),
    "motifs": ("motifs.jsonl", "motif_id", "motif.schema.json"),
    "materials": ("materials.jsonl", "material_id", "material.schema.json"),
    "fragments": ("fragments.jsonl", "fragment_id", "fragment.schema.json"),
    "relations": ("relations.jsonl", "relation_id", "relation.schema.json"),
    "sessions": ("sessions.jsonl", "session_id", "session.schema.json"),
    "read_log": ("read_log.jsonl", "read_id", "read_log.schema.json"),
    "editorial_decisions": (
        "editorial_decisions.jsonl",
        "decision_id",
        "editorial_decision.schema.json",
    ),
    # Curated judgments about the episodic reports in readings/.  The report
    # bodies stay in readings/*.md; this collection only carries what a reader
    # asserts, so a report can be cited from read_log and relations.
    "notes": ("notes.jsonl", "note_id", "note.schema.json"),
    "hypotheses": ("hypotheses.jsonl", "hypothesis_id", "hypothesis.schema.json"),
    "evaluations": ("evaluations.jsonl", "evaluation_id", "evaluation.schema.json"),
}

OPTIONAL_EMPTY_COLLECTIONS = frozenset({"hypotheses", "evaluations"})

# Fields of a note claim that must point at existing ledger records.
NOTE_CLAIM_REF_FIELDS = (
    ("question_ids", "questions"),
    ("fragment_ids", "fragments"),
    ("material_ids", "materials"),
    ("motif_ids", "motifs"),
    ("hypothesis_ids", "hypotheses"),
)

_TRIVIAL_EXCLUSION_PATTERNS = (
    "なし",
    "特になし",
    "反証不能",
    "常に成立",
    "none",
    "n/a",
    "tbd",
    "todo",
)

# Three brakes on the notes ledger, added on 2026-11-12 after one session wrote
# 859 note rows in two days (PR #655, closed without merging).  They are set so
# that ordinary work never meets them: on that date the most note rows any one
# session had written was 8, and no row on main broke the other two rules.
# docs/memory-architecture.md §4.2 and
# readings/2026-11-12-what-pr-655-did-and-what-now-stops-it.md give the reasons.
NOTE_ROWS_PER_SESSION = 12
NOTE_DEPTH_RANK = {
    "metadata_and_structure_only": 1,
    "excerpt_and_metadata_read": 2,
    "full_text_read": 3,
}
# Rows minted before this day carry internal chronology labels in created_at
# (34 of them on 2026-11-12); they are history and are not checked.
NOTE_CREATED_AT_RULE_FROM = "20261112"
# Two rules added on 2026-11-15 from readings/2026-11-15-where-the-learning-actually-happens.md.
# (a) A claim that says a reading was revised must name the hypothesis it revised,
#     or say plainly that no hypothesis was involved.  Until this date only 194 of
#     1,984 claims named a hypothesis, so the meaning layer and the belief layer
#     grew apart (9.8% wiring).
# (b) A new Q/HYP must declare its register (description / judgment / inheritance).
#     The failure mode the archive guards against is not the number of rows but a
#     judgment moving between registers without saying so.
CLAIM_WIRING_RULE_FROM = "20261116"
REGISTER_RULE_FROM = "20261116"
# Rows minted under the archive's *internal chronology* labels are not new rows,
# even when the label happens to equal the real date on which the rule first runs.
# Measured on 2026-11-16 (UTC): SESSION-20261116-de57d9 recorded in
# state/sessions.d/2026-11-10-000000000000.jsonl that its real execution date was
# 2026-10-26 and that its 2026-11-16 IDs were internal labels; its four questions
# were merged on 2026-11-15T18:44Z (#816), i.e. before this rule's first UTC day.
# _is_new_row() cannot tell a label from a real date, so these four are exempt by
# ID rather than by weakening the rule for every future 2026-11-16 row.  Removing
# this set must not be done without re-measuring that the rows are real-dated.
# See ERR-20261116-0b162a.
REGISTER_RULE_EXEMPT_IDS = frozenset({
    "Q-20261116-0fd4fd",
    "Q-20261116-3872ec",
    "Q-20261116-522540",
    "Q-20261116-6eec38",
    # Minted by a parallel session during the one day (2026-11-16) when the
    # upper bound above still hid the row, so the gate let it through without a
    # register.  The next day the same row fails, and an append-only row cannot
    # be given the field afterwards.  Exempted by ID rather than by widening the
    # window, which would hide every future same-day row too.
    "Q-20261117-1d7864",
    # Minted by SESSION-20261119-38e624 in a shard named 2026-10-24-000000000000
    # (internal chronology label) while its ID stamp is 20261119, so _is_new_row
    # treats it as new on 2026-11-19 but the row was written without register.
    # Append-only rows cannot be given the field afterwards; exempt by ID
    # rather than by weakening the rule for every future 2026-11-19 row.
    # See readings/2026-11-19-the-second-seventy-two-and-the-first-sound.md.
    "Q-20261119-4cf82a",
})
CLAIM_WIRING_KINDS = ("reading_revised", "retraction")
READ_ID_RE = re.compile(r"^READ-\d{8}-[0-9a-f]{6}$")

#: Shards minted on or after this day are named with the real execution date
#: (docs/time-axis.md rule 2); a shard named before it may carry an internal
#: chronology label, which is exactly the case the ID stamp cannot be trusted for.
#: From this day ``tools/new_ledger_shard.py`` also refuses forward-dated shard
#: names, so "the shard name is not earlier than the ID stamp" is a usable
#: label detector for everything newer, and remains the only detector for
#: everything older.
REAL_DATE_SHARD_FROM = "2026-11-12"

#: (The two registerless questions from PR #1002 used to be carried here as a dict.
#:  As of 2026-11-21 they are errata rows instead: see ``gate_waivers`` below and
#:  state/errata.d/2026-11-21-18bc5097f3f5.jsonl. The debt is now data: it prints
#:  an INFO naming the erratum, and it expires when that erratum stops being open.)

#: Sessions minted on or after this day must carry the assignment receipt.
#: The receipt exists since 2026-11-15 (``inspect_inquiry.py --assignment-json``)
#: but was optional, and optional meant unrecorded: of 920 sessions only 69
#: (7.5%) carry ``assigned_role``. The charter's 25/50/25 role split cannot be
#: checked against a ledger that does not record the treatment, so from this
#: date the four fields are required on new session rows and their absence is
#: an error rather than a note. Rows minted earlier are exempt: they cannot be
#: rewritten, and back-dating a role would manufacture a receipt that was never
#: issued (the role is a function of the seed, and 91% of old rows record none).
ROLE_RECEIPT_REQUIRED_FROM = "20261118"
# Frozen from the 2026-11-17 20:07 UTC main tree (10b5088): session IDs
# already present there whose internal stamp is >= the cutoff. Unlike the
# moving "today" upper bound, this still distinguishes old and new rows when
# the wall clock catches up. Never infer an exemption from a row's own prose.
PRE_RECEIPT_SESSION_IDS = frozenset(
    Path(__file__).with_name("pre_receipt_session_ids.txt").read_text().splitlines()
)
# 2026-11-20: one post-cutoff session row reached main without two of the four
# receipt fields (PR #998, SESSION-20261120-a45e52).  A sessions row cannot be
# superseded -- a second row with the same session_id is a duplicate, whether it
# sits in the same shard or in another one -- so the append-only repair available
# to every other collection does not exist here, and rewriting the line would
# break the byte-compare step.  Back-filling the two fields would mean issuing a
# receipt nobody issued: the role that `inspect_inquiry --assignment-json`
# recomputes for this seed (adversarial_tester) already disagrees with the role
# Gate waivers live in the ledger, not in this file (2026-11-21).
#
# Until today three defects (two registerless questions from PR #1002, one session
# row from PR #998 without its receipt) were carried as Python literals: a dict in
# this file, printed as an INFO line on every run. The intent was honest -- a gate
# that no session can turn green stops being read -- but the effect was that the
# debt lived in the gate and not in the data. Anyone reading state/questions.d
# would not learn that two rows there are known-defective; anyone auditing the
# gate had to read its source; and the count of exceptions was whatever the file
# happened to contain, invisible to every other tool in tools/.
#
# A waiver is now an errata row (state/errata.d/, schema/errata.schema.json) that
# names the subject, the gate, what was expected and what was observed:
#
#   {"errata_id": "ERR-...", "subject_type": "question", "subject_id": "Q-...",
#    "check": {"kind": "manual", "params": {"gate_waiver": "register", ...}},
#    "verdict": "contradicted", "status": "open", ...}
#
# This gate reads those rows. Consequences, all of them intended:
#   * the waiver is data -- `grep Q-20261121-198fc8 state/errata.d/*.jsonl` finds it;
#   * `status: "open"` is what makes it live; a later erratum can annotate or
#     correct it without touching this file, and a row that is not `open` no
#     longer waives anything, so the gate comes back on by itself;
#   * a waiver for an unknown gate name, or for a subject_type the gate does not
#     own, is an ERROR, not a silent no-op. A mistyped waiver must not read as one;
#   * there is no fallback list in code. If the errata shard is lost, the gate goes
#     red -- which is the correct behaviour for a lost record of a known defect.
ROLE_RECEIPT_FIELDS = (
    "dispersal_seed",
    "assigned_role",
    "offered_target_question_id",
    "offered_reference_mode",
)
REGISTER_VALUES = ("description", "judgment", "inheritance")

GATE_WAIVER_SUBJECT: dict[str, str] = {"register": "question", "receipt": "session"}


def gate_waivers(
    errata: dict[str, dict[str, Any]], errors: list[str] | None = None
) -> dict[tuple[str, str], str]:
    """Return {(gate, subject_id): errata_id} for the waivers currently in force."""
    waivers: dict[tuple[str, str], str] = {}
    for errata_id, record in sorted(errata.items()):
        check = record.get("check") or {}
        params = check.get("params") or {}
        gate = params.get("gate_waiver")
        if not isinstance(gate, str) or not gate:
            continue
        if check.get("kind") != "manual":
            continue
        if record.get("status") != "open":
            continue
        subject_type = record.get("subject_type")
        subject_id = record.get("subject_id")
        expected = GATE_WAIVER_SUBJECT.get(gate)
        if expected is None:
            if errors is not None:
                errors.append(
                    f"errata:{errata_id}: check.params.gate_waiver={gate!r} names no gate in "
                    f"this validator (known: {', '.join(sorted(GATE_WAIVER_SUBJECT))}); "
                    "a waiver that names nothing waives nothing"
                )
            continue
        if subject_type != expected or not isinstance(subject_id, str) or not subject_id:
            if errors is not None:
                errors.append(
                    f"errata:{errata_id}: gate_waiver={gate!r} must name subject_type="
                    f"{expected!r} and a subject_id; got subject_type={subject_type!r}, "
                    f"subject_id={subject_id!r}"
                )
            continue
        key = (gate, subject_id)
        if key in waivers:
            if errors is not None:
                errors.append(
                    f"errata:{errata_id}: duplicate gate_waiver for {gate}:{subject_id} "
                    f"(already waived by {waivers[key]})"
                )
            continue
        waivers[key] = errata_id
    return waivers

_ID_STAMP = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-(\d{8})-")

#: Three-Gates forward-dated write rules (2026-11-18, readings/2026-11-18-three-gates-between-trace-and-self.md §4):
#: (1) New primary_source_collision rows must cite >=1 material with effective verification.status == 'verified'
#:     (directly or via an append-only editorial_decisions material overlay).
#: (2) New materials must not duplicate an existing record's canonical DOI, PMID, or PMCID;
#:     re-read or upgrade the existing MAT-* via editorial_decisions instead.
#: (3) New narrows_scope / refutes_unconditioned evaluations without explicit successor routing
#:     must not list a direct child of target_hypothesis_id in compared_against_hypothesis_ids.
#: Rows minted before this date stay valid without rewrite (append-only invariant).
THREE_GATES_RULE_FROM = "20261119"
SUPPRESS_RETRIEVAL_SUBJECT_TYPES = ("material", "fragment", "note", "hypothesis")

#: Evidence-record-path resolution gate (2026-11-19, added after the measurement in
#: readings/2026-11-19-two-registers-of-the-same-dissociation.md §4).  The note ledger
#: has checked since 2026-11-12 that ``path`` names an existing file; the material
#: ledger, which is the collection that carries the *evidence* pointing relationship,
#: never did — so a row could claim ``verified`` while its ``origin.evidence_record_path``
#: named a report that had been renamed (10 rows) or a shard consolidated away.
#: The rule is source-blind: it does not care *which* collection the label came from,
#: only that a label which names a location inside this repository resolves to a file,
#: or is a URL, or is the row's own recorded location (a self-address, which is
#: provenance rather than a pointer), or is recorded in state/shard_aliases.json.
#: Anything else may be repaired with an editorial_decisions overlay
#: (``corrected_evidence_record_path``) instead of rewriting the shard.
EVIDENCE_PATH_RULE_FROM = "20261119"
#: Rows this gate tolerates before it fails.  Measured, not chosen (2026-11-19, after
#: the ten renamed-report rows were repaired): 24 rows point at a repository path that
#: no longer exists — 14 at ``state/evidence*`` (a ledger directory that was removed
#: before the current layout) and 10 at ``readings/`` reports that predate the note
#: index.  A *count*, deliberately not a list of IDs: a list would licence exactly the
#: rows on it, and the next dead pointer would then be measured against a roster
#: instead of against the rule.  The baseline only moves down — repair rows, then lower
#: it in the same change.  A row minted before the rule that this gate "cannot fail" is
#: still visible here as a number, so the debt is a quantity rather than an amnesty.
EVIDENCE_PATH_LEGACY_MAX = 24
_REPO_TOP_LEVEL = frozenset(
    {"articles", "docs", "map", "prompts", "readings", "schema", "state", "tests", "tools", "viewer"}
)
_DOI_RE = re.compile(r"(?:doi\.org/|doi:\s*|^)(10\.\d{4,9}/[^\s\"'<>?#]+)", re.IGNORECASE)
_PMID_RE = re.compile(r"(?:pubmed\.ncbi\.nlm\.nih\.gov/|pmid[:\s]*)(\d{5,10})(?:\b|/)", re.IGNORECASE)
_PMCID_RE = re.compile(r"\b(PMC\d{5,10})\b", re.IGNORECASE)


def extract_material_identifiers(record: dict[str, Any]) -> dict[str, str]:
    """Extract canonical external identifiers (doi, pmid, pmcid) from a material row.

    Inspects ``source.url`` and ``source.source_id`` only (never ``passage`` or
    ``scope_note``, which legitimately cite related papers). Used by both the
    forward-dated duplicate gate and ``tools/three_gates.py --check-source``.
    """
    src = record.get("source")
    if not isinstance(src, dict):
        return {}
    url = str(src.get("url") or "").strip()
    sid = str(src.get("source_id") or "").strip()
    out: dict[str, str] = {}
    for text in (url, sid):
        if not text:
            continue
        if "doi" not in out:
            dm = _DOI_RE.search(text)
            if dm:
                doi = dm.group(1).rstrip(".,;:)/]}>").lower()
                for suffix in ("/full", "/abstract", "/pdf", "/fulltext", "/meta"):
                    if doi.endswith(suffix) and "/" in doi[: -len(suffix)]:
                        doi = doi[: -len(suffix)]
                if doi:
                    out["doi"] = doi
        if "pmid" not in out:
            pm = _PMID_RE.search(text)
            if pm:
                out["pmid"] = pm.group(1)
        if "pmcid" not in out:
            cm = _PMCID_RE.search(text)
            if cm:
                out["pmcid"] = cm.group(1).upper()
    return out


def id_stamp(record_id: Any) -> str | None:
    """Return the YYYYMMDD stamp inside a ledger ID, or None when it has none."""
    match = _ID_STAMP.match(record_id) if isinstance(record_id, str) else None
    return match.group(1) if match else None


def _as_day(stamp: str) -> datetime.date | None:
    try:
        return datetime.date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8]))
    except ValueError:
        return None


def _shard_day(path: Path | None) -> str | None:
    """Return the YYYYMMDD date a shard file is named with, or None for none."""
    if path is None:
        return None
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", Path(path).name)
    return "".join(match.groups()) if match else None


def _is_internal_label(record_id: Any, shard: Path | None) -> bool:
    """True when this record's ID stamp is provably an internal chronology label.

    The archive used to stamp IDs with an internal chronology that ran ahead of
    the real execution date (2026-11-05: 224 session IDs carried labels into the
    2027s; docs/time-axis.md §0).  Such a record was written on or before the day
    of the shard it sits in, so a shard named *earlier* than the record's own
    stamp is proof that the stamp is a label rather than the date the row was
    written.  This is a proof, not a heuristic: no writer can put a row into a
    shard that is named before the day the row is minted.

    Rows in the frozen base file, or in a shard with no date in its name, carry
    no such proof and are never exempted here.
    """
    stamp = id_stamp(record_id)
    shard_stamp = _shard_day(shard)
    if not stamp or not shard_stamp:
        return False
    return shard_stamp < stamp


def build_forward_label_evidence(
    collections: dict[str, dict[str, dict[str, Any]]],
    *,
    today: datetime.date | None = None,
) -> frozenset[str]:
    """IDs whose stamped date is provably not the day the row was written.

    A session row records the question it was *offered* before it chose anything
    (``offered_target_question_id``, docs/parallel-work.md rule 10).  If a session
    whose own stamp is not in the future was offered a question whose stamp is,
    then that question already existed on the earlier day: its stamp is an
    internal chronology label, not a date.

    Measured 2026-11-21: 22 such offers exist, the clearest being
    ``SESSION-20261116-18e776`` (own notes: 実作業日 2026-11-16) which was offered
    ``Q-20261121-198fc8``..  Under the old ``stamp <= today`` bound that question
    was read as written today, and the two questions merged by PR #1002 turned
    the whole gate red without any commit changing a row.
    """
    today_stamp = (today or datetime.date.today()).strftime("%Y%m%d")
    labels: set[str] = set()
    for record in collections.get("sessions", {}).values():
        offered = record.get("offered_target_question_id")
        if not isinstance(offered, str) or not offered:
            continue
        referrer = id_stamp(record.get("session_id"))
        target = id_stamp(offered)
        # The offerer must be a row we can date (at or before today), and the
        # offered row must be stamped strictly later than the offer.  A
        # same-day offer proves nothing: both stamps could be real dates.
        if referrer and target and referrer <= today_stamp and referrer < target:
            labels.add(offered)
    return frozenset(labels)


def _is_new_row(
    record_id: Any,
    cutoff: str,
    *,
    today: datetime.date | None = None,
    shard: Path | None = None,
    label_ids: frozenset[str] | None = None,
) -> bool:
    """True when the row's ID carries a real date at or after ``cutoff``.

    Legacy rows carry internal chronology labels in their IDs (some are in 2027),
    and the old implementation kept them out with an upper bound on *today*.
    That bound is a moving target: as the wall clock advances, label-stamped rows
    that were written long ago cross it one by one and are re-read as new rows
    that broke a rule they predate.  Measured on 2026-11-21: 57 such rows sat in
    the tree, 2 already failed the register gate and the set was scheduled to
    reach 65 by 2027-03-01 with no commit changing anything.

    The bound is therefore replaced by evidence in the record itself:
    ``_is_internal_label`` (the row cannot be newer than the shard it sits in)
    and ``_future_labels_are_unreachable`` (no real-dated record can have been
    offered or linked from a stamp the writer could not yet mint).  A row of
    unknown provenance is judged by its stamp, as before, so the gate keeps
    every one of its current verdicts except where a forward stamp is provably
    a label.
    """
    stamp = id_stamp(record_id)
    if not stamp or stamp < cutoff:
        return False
    if _is_internal_label(record_id, shard):
        return False
    today_stamp = (today or datetime.date.today()).strftime("%Y%m%d")
    if stamp > today_stamp:
        # Unchanged from every previous version: a stamp later than today is
        # label territory, and no such row is judged new.
        return False
    # Stamp is at or before today.  Every earlier version called this a new row.
    # It stops being one only when a record in the ledger proves the stamp is a
    # label -- see build_forward_label_evidence.
    return not (label_ids and record_id in label_ids)


def check_claim_wiring(
    notes: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    today: datetime.date | None = None,
) -> None:
    """A claim that revises a reading must name a hypothesis or say it names none.

    Rows minted before ``CLAIM_WIRING_RULE_FROM`` are history and are not checked.
    """
    for note_id, record in sorted(notes.items()):
        if not _is_new_row(note_id, CLAIM_WIRING_RULE_FROM, today=today):
            continue
        claims = record.get("claims")
        if not isinstance(claims, list):
            continue
        for position, claim in enumerate(claims):
            if not isinstance(claim, dict):
                continue
            if claim.get("kind") not in CLAIM_WIRING_KINDS:
                continue
            wired = claim.get("hypothesis_ids") or []
            if wired or claim.get("no_hypothesis") is True:
                continue
            errors.append(
                f"notes:{note_id}: claims[{position}] has kind {claim.get('kind')!r} but names no "
                "hypothesis. Add hypothesis_ids, or set no_hypothesis=true when no registered "
                "hypothesis was revised (docs/registers.md)"
            )


def check_registers(
    collections: dict[str, dict[str, dict[str, Any]]],
    errors: list[str],
    advisories: list[str] | None = None,
    *,
    waivers: dict[tuple[str, str], str] | None = None,
    today: datetime.date | None = None,
    shard_of: dict[str, Path] | None = None,
    label_ids: frozenset[str] | None = None,
) -> None:
    """New questions and hypotheses must declare which register they are written in.

    ``shard_of`` maps a record ID to the file it was read from.  It is optional so
    that a caller holding only parsed rows (a test fixture) still gets the rule;
    without it, a row whose ID stamp is a legacy internal label is reported like
    any other, because there is no evidence in the record that it is old.
    """
    shard_of = shard_of or {}
    for collection in ("questions", "hypotheses"):
        for record_id, record in sorted(collections.get(collection, {}).items()):
            if record_id in REGISTER_RULE_EXEMPT_IDS:
                continue
            if not _is_new_row(
                record_id,
                REGISTER_RULE_FROM,
                today=today,
                shard=shard_of.get(record_id),
                label_ids=label_ids,
            ):
                continue
            register = record.get("register")
            if register in REGISTER_VALUES:
                continue
            waiver = (waivers or {}).get(("register", record_id))
            if waiver:
                if advisories is not None:
                    advisories.append(
                        f"INFO: register defect waived by {waiver} (advisory): {collection}:{record_id} "
                        "carries no register; questions cannot be superseded, so the debt is recorded "
                        "as an errata row instead of a rewrite. Set that erratum's status away from "
                        "`open` (or annotate it) and this line disappears; the gate itself is unchanged"
                    )
                continue
            shown = "missing" if register is None else repr(register)
            errors.append(
                f"{collection}:{record_id}: register is {shown}; declare one of "
                f"{', '.join(REGISTER_VALUES)} (docs/registers.md). description=what was read, "
                "judgment=a refutable criterion, inheritance=what the next session carries."
            )


def check_note_brakes(notes: dict[str, dict[str, Any]], errors: list[str]) -> None:
    """Apply the three brakes: rows per session, reading depth, created_at."""
    per_session: dict[str, int] = {}
    by_path: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for note_id, record in notes.items():
        session_id = record.get("session_id")
        is_backfill_stub = record.get("index_backfill") is True
        if is_backfill_stub:
            if record.get("read_depth") != "metadata_and_structure_only":
                errors.append(
                    f"notes:{note_id}: index_backfill stub must use read_depth='metadata_and_structure_only'"
                )
            if record.get("claims"):
                errors.append(
                    f"notes:{note_id}: index_backfill stub must not assert curated claims"
                )
        elif isinstance(session_id, str):
            per_session[session_id] = per_session.get(session_id, 0) + 1
        path = record.get("path")
        if isinstance(path, str):
            by_path.setdefault(path, []).append((note_id, record))

    # 1. One session writes a bounded number of note rows.  A note is a judgment
    #    about a report that was read; registering every report is not one.
    for session_id, count in sorted(per_session.items()):
        if count > NOTE_ROWS_PER_SESSION:
            errors.append(
                f"notes: session {session_id} has {count} note rows; one session may write at most "
                f"{NOTE_ROWS_PER_SESSION}. Covering every report is not a goal (PROJECT_CHARTER.md); "
                "a report without a note row is not a debt."
            )

    for note_id, record in notes.items():
        stamp = id_stamp(note_id)

        # 2. A row may not put a shallower reading over a deeper one that another
        #    session recorded earlier about the same report.
        path = record.get("path")
        session_id = record.get("session_id")
        superseded = record.get("supersedes")
        superseded_ids = set(superseded) if isinstance(superseded, list) else set()
        deepest_rank, deepest_id = 0, None
        for other_id, other in by_path.get(path, []) if isinstance(path, str) else []:
            if other_id == note_id or other.get("session_id") == session_id:
                continue
            other_stamp = id_stamp(other_id)
            earlier = stamp is not None and other_stamp is not None and other_stamp < stamp
            if not earlier and other_id not in superseded_ids:
                continue
            rank = NOTE_DEPTH_RANK.get(other.get("read_depth"), 0)
            if rank > deepest_rank:
                deepest_rank, deepest_id = rank, other_id
        if deepest_id is not None and NOTE_DEPTH_RANK.get(record.get("read_depth"), 0) < deepest_rank:
            errors.append(
                f"notes:{note_id}: read_depth {record.get('read_depth')!r} is shallower than "
                f"{notes[deepest_id].get('read_depth')!r} in {deepest_id}, which another session wrote "
                "about the same report; read the report at least as deeply, or record the partial "
                "reading in read_log instead of a note row"
            )

        # 3. created_at is the real time of writing, not an ordering label.
        if stamp is not None and stamp >= NOTE_CREATED_AT_RULE_FROM:
            minted = _as_day(stamp)
            digits = re.sub(r"\D", "", str(record.get("created_at") or ""))[:8]
            written = _as_day(digits) if len(digits) == 8 else None
            if minted and written and written > minted + datetime.timedelta(days=1):
                errors.append(
                    f"notes:{note_id}: created_at {record.get('created_at')!r} is later than the date in "
                    "its own ID; created_at is the real time of writing, not an ordering label "
                    "(docs/time-axis.md)"
                )
            salience = record.get("salience")
            if isinstance(salience, int) and salience > 3:
                errors.append(
                    f"notes:{note_id}: salience {salience} exceeds maximum 3 for rows minted from 2026-11-12 onward"
                )


def matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def resolve_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    node: Any = root_schema
    for piece in ref[2:].split("/"):
        piece = piece.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or piece not in node:
            return None
        node = node[piece]
    return node if isinstance(node, dict) else None


def validate_value(value: Any, spec: dict[str, Any], root_schema: dict[str, Any], path: str, errors: list[str]) -> None:
    ref = spec.get("$ref")
    if isinstance(ref, str):
        target = resolve_ref(root_schema, ref)
        if target is None:
            errors.append(f"{path}: unresolved schema reference {ref}")
            return
        validate_value(value, target, root_schema, path, errors)
        return

    expected = spec.get("type")
    if isinstance(expected, str) and not matches_type(value, expected):
        errors.append(f"{path}: expected {expected}, got {type(value).__name__}")
        return

    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum {spec['enum']!r}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(spec.get("minimum"), (int, float)) and value < spec["minimum"]:
            errors.append(f"{path}: value {value!r} is less than minimum {spec['minimum']}")
        if isinstance(spec.get("maximum"), (int, float)) and value > spec["maximum"]:
            errors.append(f"{path}: value {value!r} exceeds maximum {spec['maximum']}")
    if isinstance(value, str) and isinstance(spec.get("minLength"), int) and len(value) < spec["minLength"]:
        errors.append(f"{path}: string shorter than minLength {spec['minLength']}")

    if isinstance(value, list):
        if isinstance(spec.get("minItems"), int) and len(value) < spec["minItems"]:
            errors.append(f"{path}: array shorter than minItems {spec['minItems']}")
        if spec.get("uniqueItems") is True:
            try:
                if len(value) != len({json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value}):
                    errors.append(f"{path}: array items must be unique")
            except TypeError:
                errors.append(f"{path}: array items are not JSON-serializable")
        item_spec = spec.get("items")
        if isinstance(item_spec, dict):
            for index, item in enumerate(value):
                validate_value(item, item_spec, root_schema, f"{path}[{index}]", errors)

    if isinstance(value, dict):
        required = spec.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{path}: missing required field {key!r}")
        properties = spec.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        if spec.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected field {key!r}")
        for key, child_spec in properties.items():
            if key in value and isinstance(child_spec, dict):
                validate_value(value[key], child_spec, root_schema, f"{path}.{key}", errors)


def load_jsonl(path: Path, id_key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    """Load one ledger (frozen base file plus its session shards) into an ID map.

    The actual reading, retrying and duplicate detection live in ``ledger_io`` so
    that every tool sees the same union view.  Errors are appended to ``errors``
    in the same shape as before; a ledger that keeps changing raises
    ``ledger_io.LedgerBusy`` instead of reporting a torn read as corruption.
    """
    return ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)


ERRATA_ID_PREFIXES = {
    "hypothesis": "HYP-",
    "material": "MAT-",
    "note": "NOTE-",
    "question": "Q-",
    "session": "SESSION-",
    "evaluation": "EVL-",
    "fragment": "FRAG-",
    "motif": "MOTIF-",
    # 2026-11-15: eleven errata whose subject is another erratum had to say
    # subject_type="other", because this enum and the one in
    # schema/errata.schema.json had no name for it.
    "erratum": "ERR-",
    "editorial_decision": "ED-",
}
# 2026-11-15: this guard listed eight families while the ledger carries twenty,
# so subject_type="tool" with subject_id="ERR-..." passed silently. The family
# list now comes from tools/ledger_ids.py. Measured before the change: zero of
# the 282 existing errata rows are newly flagged, so nothing had to be rewritten.
_LEDGER_ID_RE = re.compile(r"^(?:" + "|".join(ledger_ids.ALL_PREFIXES) + r")-")


def check_errata_addressee_labels(
    errata: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    """Require ``subject_type`` to agree with the address it is attached to.

    ``belief_state.build_errata_index`` routes on the address, not on this label,
    and that is deliberate: IDs and repo paths are self-identifying, so routing on
    the declared type would let a mislabelled row escape its own address. The cost
    of that choice was that the label could lie unchecked -- ``subject_type=tool``
    pointing at a hypothesis paid the full penalty, while ``subject_type=hypothesis``
    pointing at a file path was silently inert. Both were accepted by every check.

    This makes the label mean what it says without giving it routing power.
    ``other`` and ``report`` are exempt as declared escape hatches, except that they
    must not be used to disguise a ledger ID (use the specific type for that).
    Composite addresses are allowed: a row may name several targets in one string,
    so the check asks whether *some* token carries the right prefix.
    """
    for errata_id, record in sorted(errata.items()):
        subject_type = record.get("subject_type")
        subject_id = record.get("subject_id")
        if not isinstance(subject_type, str) or not isinstance(subject_id, str) or not subject_id:
            continue
        expected = ERRATA_ID_PREFIXES.get(subject_type)
        if expected is not None:
            tokens = re.split(r"[\s/,;]+", subject_id)
            if not any(tok.startswith(expected) for tok in tokens):
                errors.append(
                    f"errata:{errata_id}: subject_type={subject_type!r} but subject_id "
                    f"{subject_id!r} carries no {expected} address"
                )
        elif subject_type in ("tool", "report") and _LEDGER_ID_RE.match(subject_id):
            errors.append(
                f"errata:{errata_id}: subject_type={subject_type!r} but subject_id "
                f"{subject_id!r} is a ledger ID; use the matching subject_type"
            )


def check_errata_duplicate_claims(
    errata: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    """Require ``duplicate_of`` to name a real row about the same addressee.

    ``duplicate_of`` collapses several rows into one penalty, so a dangling or
    cross-addressee declaration would quietly reduce weight. The engine ignores
    such a declaration rather than crashing; this makes it a reported error
    instead of a silent no-op. Self-reference is rejected as meaningless.

    A declaration is not required for exact repeats, and is never inferred from
    similar wording: the three distinct Blodgett corrections on one material must
    keep costing three. Only the writer can assert that a rewording restates an
    earlier claim, and that assertion is what this checks.
    """
    def addresses(rec: dict[str, Any]) -> set[str]:
        out: set[str] = set()
        target = rec.get("target")
        if isinstance(target, dict) and isinstance(target.get("id"), str):
            out.add(target["id"])
        for kname in ("subject_id", "fragment_id"):
            val = rec.get(kname)
            if isinstance(val, str) and val:
                out.add(val)
        return out

    for errata_id, record in sorted(errata.items()):
        declared = record.get("duplicate_of")
        if declared is None:
            continue
        if not isinstance(declared, list):
            errors.append(f"errata:{errata_id}: duplicate_of must be an array of errata IDs")
            continue
        for other_id in declared:
            if not isinstance(other_id, str) or other_id not in errata:
                errors.append(
                    f"errata:{errata_id}: duplicate_of references unknown errata ID {other_id!r}"
                )
                continue
            if other_id == errata_id:
                errors.append(f"errata:{errata_id}: duplicate_of references itself")
                continue
            mine, theirs = addresses(record), addresses(errata[other_id])
            if mine and theirs and not (mine & theirs):
                errors.append(
                    f"errata:{errata_id}: duplicate_of {other_id!r} has a different addressee; "
                    "one claim about two subjects is two claims"
                )


def errata_schema_advisory(errata: dict[str, dict[str, Any]], root: Path = ROOT) -> str | None:
    """One advisory line: how many errata rows disagree with their own schema.

    ``errata`` is not in ``COLLECTIONS``, so ``schema/errata.schema.json`` is
    never loaded by this gate -- errata rows are the only ledger rows nothing
    here compares to the schema written for them.  The comparison itself has
    existed since 2026-11-08 as ``tools/errata_audit.py --schema`` ("a report,
    not a gate"), but that tool is in no workflow, so the number reached only a
    session that happened to run it.  Measured 2026-11-15: 286 rows, 273
    conforming, **13 rows carrying 17 disagreements** -- 6 rows whose
    ``check.kind`` is not in the enum (``external_source_lookup`` x4,
    ``audit_group_count`` x2), 4 with an ``unexpected field 'session_id'``, 2
    with ``status: "corrected"`` (the enum is open/annotated/withdrawn), 2
    missing ``claim_location`` and ``check``, 1 missing ``created_at``.

    This reuses that validator instead of writing a second one, and it never
    changes the exit status: turning a disagreement into a failure would demand
    13 correction rows for rows that are append-only, and deciding whether the
    row or the schema is wrong is ``editorial_review``'s call, not a gate's.
    """
    if not errata:
        return None
    try:
        import errata_audit
    except Exception:  # pragma: no cover - advisory only, never break the gate
        return None
    try:
        report = errata_audit.schema_report(list(errata.values()), root=root)
    except Exception:  # pragma: no cover
        return None
    if not report.get("available"):
        return None
    bad = len(report.get("violations") or [])
    return (
        f"INFO: errata schema (advisory, never a failure): {report.get('conforming', 0)}/"
        f"{report.get('rows', 0)} rows conform to schema/errata.schema.json, {bad} row(s) disagree; "
        f"errata is not in COLLECTIONS, so this gate does not enforce it -- "
        f"run `python3 tools/errata_audit.py --schema` for the list"
    )


def psc_verification_advisory(
    evaluations: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
) -> str | None:
    """One advisory line: material verification backing of primary_source_collision rows.

    Measured 2026-11-16 (readings/2026-11-16-what-crosses-the-unheld-interval.md §3):
    206/313 (65.8%) of historical ``primary_source_collision`` rows cite zero
    materials with ``verification.status == "verified"`` while receiving the
    full 1.20 evidence weight. Because historical rows are append-only, this
    mirror reports the ratio without failing the gate.
    """
    all_v = mixed_v = zero_v = no_mat = 0
    for evl in evaluations.values():
        if evl.get("evidence_type") != "primary_source_collision":
            continue
        mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
        if not mids:
            no_mat += 1
            continue
        vc = sum(
            1
            for mid in mids
            if ((materials.get(mid) or {}).get("verification") or {}).get("status") == "verified"
        )
        if vc == len(mids):
            all_v += 1
        elif vc > 0:
            mixed_v += 1
        else:
            zero_v += 1
    total = all_v + mixed_v + zero_v + no_mat
    if not total:
        return None
    pct = (all_v / total) * 100.0
    extra = f", {no_mat} with no material_ids" if no_mat else ""
    return (
        f"INFO: primary_source_collision verification (advisory, never a failure): "
        f"{all_v}/{total} ({pct:.1f}%) all-verified, {mixed_v} mixed, {zero_v} zero-verified{extra}; "
        f"see BELIEF_MAP.md for per-hypothesis verification backing"
    )


PSC_NEW_ROW_ADVISORY_CUTOFF = "2026-11-16"


def psc_new_row_advisory(
    evaluations: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
    *,
    cutoff: str = PSC_NEW_ROW_ADVISORY_CUTOFF,
) -> str | None:
    """Name the *new* primary_source_collision rows that cite nothing fully read.

    The aggregate ratio above hides the row being written right now: an author
    reads "27.7% all-verified" and cannot tell whether their own row is one of
    the 216. This lists rows filed on or after ``cutoff`` whose cited materials
    are all non-``verified``, so that the label and its backing are visible at
    filing time (P-2 in readings/2026-11-16-stable-words-do-not-make-progress.md).
    Advisory only: it never fails the gate, and it never changes a weight.
    """
    flagged: list[str] = []
    for eid, evl in evaluations.items():
        if evl.get("evidence_type") != "primary_source_collision":
            continue
        stamp = str(evl.get("created_at") or "")[:10]
        if stamp and stamp < cutoff:
            continue
        mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
        if not mids:
            flagged.append(f"{eid}(no material_ids)")
            continue
        if all(
            ((materials.get(mid) or {}).get("verification") or {}).get("status") != "verified"
            for mid in mids
        ):
            flagged.append(eid)
    if not flagged:
        return None
    shown = ", ".join(flagged[:8]) + (", …" if len(flagged) > 8 else "")
    return (
        f"INFO: primary_source_collision rows filed since {cutoff} with no fully-verified "
        f"material (advisory): {len(flagged)} row(s) — {shown}. "
        "The label claims a collision of primary texts; the material ledger says the "
        "texts were not read in full. Say which you did (reading depth lives in the "
        "materials' verification.status, not in a new label)."
    )


def check_read_log_addressing(
    read_logs: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    """A reply must name a reading that exists, is not itself, and is already written.

    ``in_reply_to`` (2026-11-17) is the address of a reply: ``target`` says what
    was read, ``in_reply_to`` says which earlier reading the row answers. The
    field is optional, so every row written before it stays valid; what the gate
    refuses is an address that points nowhere, points at itself, or points
    forward in time. It does not check that a claimed reply is really a reply —
    that is a reading question, not a schema one.
    """
    for read_id, record in read_logs.items():
        addresses = record.get("in_reply_to")
        if addresses is None:
            continue
        if not isinstance(addresses, list):
            continue  # the schema reports the shape error
        for address in addresses:
            if not isinstance(address, str) or not address:
                continue  # ditto
            if not READ_ID_RE.match(address):
                errors.append(
                    f"read_log:{read_id}: in_reply_to entry {address!r} is not a "
                    "READ-<YYYYMMDD>-<hex> id"
                )
                continue
            if address == read_id:
                errors.append(f"read_log:{read_id}: in_reply_to names the row itself")
                continue
            if address not in read_logs:
                errors.append(
                    f"read_log:{read_id}: in_reply_to references unknown reading {address!r}"
                )
                continue
            own_stamp = id_stamp(read_id)
            other_stamp = id_stamp(address)
            if own_stamp and other_stamp and other_stamp > own_stamp:
                errors.append(
                    f"read_log:{read_id}: in_reply_to references {address!r}, which is "
                    "dated later; a reading can answer only one already written"
                )


def check_role_receipts(
    sessions: dict[str, dict[str, Any]],
    errors: list[str],
    advisories: list[str] | None = None,
    *,
    waivers: dict[tuple[str, str], str] | None = None,
    cutoff: str = ROLE_RECEIPT_REQUIRED_FROM,
    today: datetime.date | None = None,
) -> None:
    """Refuse a new session row that does not carry the assignment it was given.

    The archive decides a role, a target question and a reference mode from the
    dispersal seed every session, and used to discard all three: 69 of 920
    sessions (7.5%) record ``assigned_role``, and among those the measured
    contested-reading rate is *inverted* against the charter (consolidator 12.7%,
    adversarial_tester 4.3% — ``witness_count.py --roles``). A distribution that
    is never written down cannot be checked, corrected, or argued with, so from
    ``cutoff`` a session row without the four receipt fields is an error. Rows
    before the cutoff are exempt because they cannot be rewritten (append-only)
    and because the seed is not recorded for 91% of them: a role filled in
    afterwards would be a manufactured receipt, not a recovered one.
    """
    for session_id, record in sessions.items():
        if session_id in PRE_RECEIPT_SESSION_IDS or not _is_new_row(session_id, cutoff, today=today):
            continue
        missing = [
            field for field in ROLE_RECEIPT_FIELDS
            if not str(record.get(field) or "").strip()
        ]
        if missing:
            waiver = (waivers or {}).get(("receipt", session_id))
            if waiver:
                if advisories is not None:
                    advisories.append(
                        f"INFO: receipt defect waived by {waiver} (advisory): sessions:{session_id} "
                        f"is missing {', '.join(missing)}; sessions rows cannot be superseded and rule 10 "
                        "forbids back-filling a receipt nobody issued, so the debt lives in the errata "
                        "ledger. A waiver that is not `open` brings this gate back on"
                    )
                continue
            errors.append(
                f"sessions:{session_id}: missing assignment receipt field(s) "
                f"{', '.join(missing)}; the seed decided the role, the target question "
                "and the reference mode before the session chose anything, and an "
                "unrecorded treatment cannot be joined to its outcome. Run "
                "`python3 tools/inspect_inquiry.py --assignment-json` and paste its "
                "session_row_fields into the row (docs/parallel-work.md 規則10)"
            )


def check_psc_verification_gate(
    evaluations: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    cutoff: str = THREE_GATES_RULE_FROM,
    today: datetime.date | None = None,
) -> None:
    """Gate 3 (reality monitoring): refuse new zero-verified primary_source_collision rows.

    Historical rows minted before ``cutoff`` remain untouched and are reported by
    ``psc_verification_advisory`` instead.  An existing non-verified material that
    a session reads in full can be upgraded in place via an append-only
    ``editorial_decisions`` row with ``target.type == "material"`` and
    ``status == "verified"`` before filing the collision row.
    """
    for eid, evl in evaluations.items():
        if evl.get("evidence_type") != "primary_source_collision":
            continue
        if not _is_new_row(eid, cutoff, today=today):
            continue
        mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
        if not mids:
            errors.append(
                f"evaluations:{eid}: primary_source_collision minted on/after {cutoff} "
                "must cite at least one material_id with verification.status == 'verified' "
                "(use 'cross_session_audit' or 'fragment_thought_experiment' when no primary text is collided)"
            )
            continue
        has_verified = any(
            ((materials.get(mid) or {}).get("verification") or {}).get("status") == "verified"
            for mid in mids
        )
        if not has_verified:
            errors.append(
                f"evaluations:{eid}: primary_source_collision minted on/after {cutoff} cites "
                f"no verified material ({', '.join(mids)}); verify at least one primary text "
                "(or append an editorial_decisions material verification overlay) or record "
                "evidence_type as 'fragment_thought_experiment' / 'cross_session_audit'"
            )


def check_material_duplicate_identifiers(
    materials: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    cutoff: str = THREE_GATES_RULE_FROM,
    today: datetime.date | None = None,
) -> None:
    """Gate 3 (external grounding): refuse new materials that duplicate an archived DOI/PMID/PMCID.

    Legacy duplicates filed before ``cutoff`` (and legacy ``MAT-LIT-2027*`` internal
    chronology stamps) are preserved as history.  New acquisitions must check
    ``python3 tools/three_gates.py --check-source`` and cite or upgrade the existing
    ``MAT-*`` record rather than minting a second copy of the same primary source.
    """
    first_seen: dict[tuple[str, str], str] = {}
    for mid, record in materials.items():
        idents = extract_material_identifiers(record)
        if not idents:
            continue
        is_legacy_chronology = isinstance(mid, str) and mid.startswith("MAT-LIT-2027")
        enforce = (not is_legacy_chronology) and _is_new_row(mid, cutoff, today=today)
        reported = False
        for kind in ("doi", "pmcid", "pmid"):
            val = idents.get(kind)
            if not val:
                continue
            key = (kind, val)
            prev = first_seen.get(key)
            if prev is None:
                first_seen[key] = mid
            elif enforce and not reported and prev != mid:
                errors.append(
                    f"materials:{mid}: duplicate {kind.upper()} {val!r} already archived as "
                    f"{prev!r}; cite {prev!r} directly (and append an editorial_decisions "
                    "material verification overlay if you newly verified its full text) — "
                    "check beforehand with `python3 tools/three_gates.py --check-source`"
                )
                reported = True


def check_evaluation_descendant_collision(
    evaluations: dict[str, dict[str, Any]],
    hypotheses: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    cutoff: str = THREE_GATES_RULE_FROM,
    today: datetime.date | None = None,
) -> None:
    """Gate 2 (lineage routing hygiene): refuse ambiguous narrowing against an own direct child.

    When a ``narrows_scope`` or ``refutes_unconditioned`` evaluation leaves both
    ``spawned_hypothesis_ids`` and ``scope_inherited_by_hypothesis_ids`` empty, the
    historical belief engine falls back to every active direct child of the target —
    turning a hypothesis named as ``compared_against`` into an undeclared beneficiary.
    On/after ``cutoff``, declare explicit ``scope_inherited_by_hypothesis_ids`` /
    ``spawned_hypothesis_ids`` when a child inherits the narrowed scope, or compare
    against a non-child rival.
    """
    direct_children: dict[str, set[str]] = {}
    for hid, hyp in hypotheses.items():
        for pid in hyp.get("parent_hypothesis_ids") or ():
            if isinstance(pid, str) and pid in hypotheses:
                direct_children.setdefault(pid, set()).add(hid)
    for eid, evl in evaluations.items():
        if evl.get("verdict") not in ("narrows_scope", "refutes_unconditioned"):
            continue
        if not _is_new_row(eid, cutoff, today=today):
            continue
        if evl.get("spawned_hypothesis_ids") or evl.get("scope_inherited_by_hypothesis_ids"):
            continue
        target_hid = evl.get("target_hypothesis_id")
        if not isinstance(target_hid, str):
            continue
        children = direct_children.get(target_hid)
        if not children:
            continue
        compared = [
            cid for cid in (evl.get("compared_against_hypothesis_ids") or ())
            if isinstance(cid, str) and cid in children
        ]
        if compared:
            errors.append(
                f"evaluations:{eid}: {evl.get('verdict')} on {target_hid!r} lists its direct "
                f"child(ren) {compared} in compared_against_hypothesis_ids without explicit "
                "scope_inherited_by_hypothesis_ids or spawned_hypothesis_ids; declare the "
                "inheritor explicitly or compare against a non-child rival"
            )


def check_evidence_record_paths(
    materials: dict[str, dict[str, Any]], errors: list[str]
) -> int:
    """Every in-repository ``origin.evidence_record_path`` must resolve (2026-11-19).

    Returns the number of historical rows the baseline still tolerates.  New rows
    (``MAT-YYYYMMDD-*`` minted on or after ``EVIDENCE_PATH_RULE_FROM``) must resolve
    immediately; older rows are counted against ``EVIDENCE_PATH_LEGACY_MAX`` so the
    gate fails only if the number of unresolvable pointers *grows*.
    """
    import ledger_io

    legacy = 0
    for material_id, record in materials.items():
        origin = record.get("origin")
        if not isinstance(origin, dict):
            continue  # schema validation reports the shape error
        path = origin.get("evidence_record_path")
        if not isinstance(path, str) or not path.strip():
            continue
        if path.startswith(("http://", "https://")):
            continue  # a URL is a label, not a claim about this checkout
        if (ROOT / path).is_file():
            continue
        # A self-address points at the row's own recorded location.  It is provenance
        # (where the row was written), not a pointer to an evidence record, and shard
        # consolidation is allowed to move that location.
        if path == origin.get("source_record_path") or path.startswith("state/materials"):
            continue
        if ledger_io.resolve_shard_alias(path, root=ROOT) is not None:
            continue
        head = path.split("/", 1)[0]
        if head not in _REPO_TOP_LEVEL:
            continue  # outside the checkout: unverifiable here, but not a dead in-repo pointer
        stamp = _ID_STAMP.match(material_id)
        if stamp and stamp.group(1) >= EVIDENCE_PATH_RULE_FROM:
            errors.append(
                f"materials:{material_id}: origin.evidence_record_path {path!r} does not exist "
                f"(add the file, or repair the pointer with an editorial_decisions "
                f"corrected_evidence_record_path overlay; do not rewrite the shard)"
            )
        else:
            legacy += 1
    if legacy > EVIDENCE_PATH_LEGACY_MAX:
        errors.append(
            f"materials: {legacy} pre-{EVIDENCE_PATH_RULE_FROM} rows have an unresolvable "
            f"origin.evidence_record_path, above the frozen baseline {EVIDENCE_PATH_LEGACY_MAX} "
            f"(+{legacy - EVIDENCE_PATH_LEGACY_MAX}). The baseline only moves down: repair rows "
            f"with editorial_decisions corrected_evidence_record_path overlays, and lower "
            f"EVIDENCE_PATH_LEGACY_MAX in the same change."
        )
    return legacy


def _read_shard_evidence_paths() -> dict[str, str]:
    """``material_id -> origin.evidence_record_path`` exactly as the shards record it.

    Read from disk rather than from the loaded snapshot, because the snapshot has the
    editorial overlay already applied.  Malformed lines are skipped: schema validation
    reports them separately.
    """
    out: dict[str, str] = {}
    for path in ledger_io.collection_files(ROOT / "state" / "materials.jsonl"):
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = record.get("material_id")
            origin = record.get("origin")
            if isinstance(mid, str) and isinstance(origin, dict):
                recorded = origin.get("evidence_record_path")
                if isinstance(recorded, str):
                    out[mid] = recorded
    return out


def check_evidence_path_corrections(
    decisions: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    """An overlay that corrects a path must correct it to something that exists.

    Without this, ``corrected_evidence_record_path`` would be a second way to write
    an unresolvable pointer — the gate would be defeated by its own repair mechanism.
    """
    shard_recorded_evidence_paths = _read_shard_evidence_paths()
    for decision_id, record in decisions.items():
        path = record.get("corrected_evidence_record_path")
        if path is None:
            continue
        target = record.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            errors.append(
                f"editorial_decisions:{decision_id}: corrected_evidence_record_path is only "
                f"valid for target type 'material'"
            )
            continue
        material_id = target.get("id")
        material = materials.get(material_id) if isinstance(material_id, str) else None
        if material is None:
            continue  # check_refs already reports the unknown target
        if not isinstance(path, str) or not path.strip():
            continue  # schema reports the shape error
        path = path.strip()
        if path.startswith(("http://", "https://")):
            continue
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(
                f"editorial_decisions:{decision_id}: corrected_evidence_record_path must be "
                f"repository-relative without '..': {path!r}"
            )
            continue
        if not (ROOT / candidate).is_file():
            errors.append(
                f"editorial_decisions:{decision_id}: corrected_evidence_record_path "
                f"{path!r} does not exist; an overlay may not introduce a second dead pointer"
            )
            continue
        # Compare against the path AS RECORDED IN THE SHARD.  The records handed to this
        # function already carry the overlay (ledger_io.load_collections applies it on
        # load), so reading ``material["origin"]["evidence_record_path"]`` back would
        # return the correction itself and make every valid repair look like a no-op.
        # The shard value is therefore read from the ledger files directly.
        original = shard_recorded_evidence_paths.get(material_id, "")
        if path == original:
            errors.append(
                f"editorial_decisions:{decision_id}: corrected_evidence_record_path is "
                f"identical to the row's existing path {path!r}; an overlay that changes "
                f"nothing hides the fact that the pointer is still dead"
            )
        elif candidate.name == Path(original).name:
            errors.append(
                f"editorial_decisions:{decision_id}: corrected_evidence_record_path keeps the "
                f"same file name {candidate.name!r} as the recorded path; the two must be "
                f"distinguishable or the correction cannot be audited"
            )



# ---------------------------------------------------------------------------
# 2026-11-20 (③④ of the evidence-accounting change)
#
# ③ verification.depth: "did a check happen" and "how far into the text did it
#    go" were the same field.  A session that read a results table had to choose
#    between claiming `verified` (an overclaim) and staying `partially_verified`
#    (which reads in reports as "did not read").  `depth` separates the two, and
#    only binds rows checked on or after DEPTH_CUTOFF, because 5,564 existing
#    rows cannot acquire a field that was invented after they were written.
#
# ④ every number must be recomputed, traced to a checked text, or explained.
#    `script_command` already covered the first route and `material_ids` the
#    second; `no_recompute_reason` names the third.  Only rows from the cutoff
#    on are gated, for the same append-only reason.
# ---------------------------------------------------------------------------
VERIFICATION_DEPTHS = frozenset({"metadata", "abstract", "results", "full_text", "re_derived", "unspecified"})
#: `unspecified` records that the archive does not know.  It is allowed on legacy
#: rows and as a correction that withdraws an inferred depth, but it never
#: satisfies the new-row requirement: a session that checked a source must say
#: how far it got, and "I do not know" is not an answer to "how far did you go?".
CONCRETE_DEPTHS = VERIFICATION_DEPTHS - {"unspecified"}
TRACEABILITY_CUTOFF = "20261121"  # YYYYMMDD, the same stamp format as CLAIM_WIRING_RULE_FROM

# 2026-11-21 (six-layer self model): new notes require cognitive_operation and
# new evaluations require agency_stance for structural source attribution and
# judgment-of-agency (Layer 1 and Layer 2 of the six-layer self model).
# Same date stamp as TRACEABILITY_CUTOFF since they were introduced together.
COGNITIVE_OP_CUTOFF = "20261121"
AGENCY_STANCE_CUTOFF = "20261121"
VALID_COGNITIVE_OPS = frozenset({"quotation", "paraphrase", "inference", "imagination", "self_observation", "received_direction"})
VALID_AGENCY_STANCES = frozenset({"endorse", "report_only", "dissent", "self_correction"})
# Rows already on origin/main as of this rule's introduction cannot be given
# the field retroactively (writing a field that the original session never
# asserted would be fabricating provenance, which rule 10 forbids).  Listed by
# ID; any later row from COGNITIVE_OP_CUTOFF onward must carry the field.
COGNITIVE_OP_EXEMPT_IDS = frozenset({
    "NOTE-20261121-d42149",
    "NOTE-20261121-d71aa2",
    "NOTE-20261121-3971c2",
    "NOTE-20261121-a47d92",
    "NOTE-20261121-3ddaac",
    "NOTE-20261121-1a6958",
    "NOTE-20261121-fc74cd",
    "NOTE-20261121-83c7c4",  # from concurrent PR #1017 merged to main
    "NOTE-20261121-bce449",  # from concurrent PR #1019 (SESSION-20261121-faaab0, authored pre-gate)
    "NOTE-20261121-b3259d",  # from concurrent PR #1020, minted before the six-layer rule merged
})
AGENCY_STANCE_EXEMPT_IDS = frozenset({
    "EVL-20261121-2a793d",
    "EVL-20261121-2b7615",
    "EVL-20261121-88e2f8",
    "EVL-20261121-bcb691",
    "EVL-20261121-defb3d",
    "EVL-20261121-c77d14",
    "EVL-20261121-41b8e2",
    "EVL-20261121-59c3f1",
    "EVL-20261121-63d7a9",
    "EVL-20261121-78e4b6",
    "EVL-20261121-85f1c3",
    "EVL-20261121-dc5c02",  # from concurrent PR #1017 merged to main
    "EVL-20261121-f8a8cf",  # from concurrent PR #1017 merged to main
    "EVL-20261121-8aac6f",  # from concurrent PR #1019 (SESSION-20261121-faaab0, authored pre-gate)
    "EVL-20261121-f07af6",  # from concurrent PR #1019 (SESSION-20261121-faaab0, authored pre-gate)
    "EVL-20261121-8a0d09",  # from concurrent PR #1020, minted before the six-layer rule merged
    "EVL-20261121-c96454",  # from concurrent PR #1020, minted before the six-layer rule merged
    "EVL-20261121-946d73",  # from concurrent PR #1020, minted before the six-layer rule merged
})

# 2026-11-21 six-layer self model (Layer 3/4/5): new sessions must carry
# session_type and self_layer_checks. Same cutoff date as above.
SESSION_TYPE_CUTOFF = "20261121"
SELF_LAYER_CHECKS_CUTOFF = "20261121"
VALID_SESSION_TYPES = frozenset({"acquisition", "close_reading", "re_reading", "infrastructure", "default_mode_simulation", "evaluation_only", "other"})
REQUIRED_CHECK_KEYS = frozenset({"source_attributed", "agency_stance_recorded", "self_model_rebuilt", "veto_considered"})
# Sessions already on origin/main as of rule introduction are exempt.
# All sessions minted before this rule was introduced are listed explicitly by ID.
# These sessions cannot be retroactively given session_type/self_layer_checks fields
# (rule 10: writing a receipt nobody issued). Any session minted after this rule
# takes effect must carry both fields.
SESSION_TYPE_EXEMPT_IDS = frozenset({
    "SESSION-20261121-0723fd", "SESSION-20261121-2b7615", "SESSION-20261121-3831aa",
    "SESSION-20261121-75acab", "SESSION-20261121-98bf13", "SESSION-20261121-9c41e8",
    "SESSION-20261121-a34277", "SESSION-20261121-d0e4d6", "SESSION-20261121-d414f0",
    "SESSION-20261121-d512b3", "SESSION-20261121-d83dd7", "SESSION-20261121-e3b180",
    "SESSION-20261121-e7565a", "SESSION-20261121-f937bd", "SESSION-20261121-fdf447",
    "SESSION-20261121-002438",  # from PR #1018
    "SESSION-20261121-faaab0",  # from concurrent PR #1019 (SESSION-20261121-faaab0, authored pre-gate)
    "SESSION-20261121-004556",  # from concurrent PR #1020, minted before the six-layer rule merged
    "SESSION-20261122-11b1d3",  # from PR #1031, on main before six-layer rule merged; shard 2026-11-10 < stamp 20261122 proves internal label
})
# The frozen pre-receipt snapshot (2026-11-17, above) also predates these
# hooks. Reuse that provenance, not the current date or a row's own timestamp:
# legacy future-labelled IDs must not become new obligations as time catches up.
SESSION_TYPE_EXEMPT_IDS = SESSION_TYPE_EXEMPT_IDS | PRE_RECEIPT_SESSION_IDS
SELF_LAYER_CHECKS_EXEMPT_IDS = SESSION_TYPE_EXEMPT_IDS  # same set: both rules take effect together
_NUMBER_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*%|\bp\s*[=<]\s*0?\.\d+|\d+\.\d+|\b\d+\s*(?:件|行|回|種|人|資料|評価|セッション|仮説|素材)"
    r"|\bn\s*=\s*\d+|\b\d{2,}\b)"
)
_DATE_RE = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b")


def _numbers_in(text: str) -> bool:
    """True when the prose asserts a quantity (IDs, dates and years excluded)."""
    if not isinstance(text, str) or not text:
        return False
    stripped = _DATE_RE.sub(" ", text)
    stripped = re.sub(r"\b[A-Z]{2,}-\d{4,}-[0-9a-z]+", " ", stripped)
    stripped = re.sub(r"\b\d{4}/\d{1,2}/\d{1,2}\b", " ", stripped)
    return bool(_NUMBER_RE.search(stripped))


def check_verification_depth(
    materials: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    today: datetime.date | None = None,
) -> tuple[int, int]:
    """Depth must exist where a check was recorded, and must agree with status."""
    depth_recorded = 0
    legacy_missing = 0
    for mid, record in materials.items():
        ver = record.get("verification")
        if not isinstance(ver, dict):
            continue
        status = ver.get("status")
        depth = ver.get("depth")
        checked_at = str(ver.get("checked_at") or "")
        if depth is not None and depth not in VERIFICATION_DEPTHS:
            # The schema enum already rejects this; kept so a future enum widening
            # cannot silently accept a depth the rest of the archive cannot read.
            errors.append(
                f"materials:{mid}: verification.depth {depth!r} is not one of {sorted(VERIFICATION_DEPTHS)}"
            )
            continue
        if depth in ("metadata", "abstract") and status == "verified":
            errors.append(
                f"materials:{mid}: verification.depth {depth!r} cannot carry status 'verified' — "
                "a bibliographic or abstract-level check is 'partially_verified' (or 'verified' "
                "only once the passage itself was read in the paper's own text)"
            )
        if depth in ("full_text", "re_derived") and status not in ("verified", "corrected"):
            errors.append(
                f"materials:{mid}: verification.depth {depth!r} requires status 'verified' "
                f"(got {status!r})"
            )
        # Gate on the row's own ID stamp, not on checked_at: legacy rows carry
        # internal-chronology dates (some in 2027) that _is_new_row already knows
        # to exclude, and a forward-dated checked_at must not turn a 2026 row into
        # a rule that only binds tomorrow.
        if depth:
            depth_recorded += 1
        is_new = _is_new_row(mid, TRACEABILITY_CUTOFF, today=today) and checked_at[:10] >= (
            f"{TRACEABILITY_CUTOFF[:4]}-{TRACEABILITY_CUTOFF[4:6]}-{TRACEABILITY_CUTOFF[6:]}"
        )
        if is_new:
            if status in ("verified", "partially_verified") and (not depth or depth == "unspecified"):
                errors.append(
                    f"materials:{mid}: verification.checked_at {checked_at[:10]} is on or after "
                    f"{TRACEABILITY_CUTOFF[:4]}-{TRACEABILITY_CUTOFF[4:6]}-{TRACEABILITY_CUTOFF[6:]}, so verification.depth must say how far the check went "
                    f"({sorted(CONCRETE_DEPTHS)}); status alone cannot distinguish "
                    "'read the abstract' from 'read the passage'"
                )
        elif status == "verified" and not depth:
            legacy_missing += 1
    return depth_recorded, legacy_missing


def check_number_traceability(
    evaluations: dict[str, dict[str, Any]],
    notes: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    today: datetime.date | None = None,
) -> tuple[int, int]:
    """A number must be recomputed, traced to a checked text, or explained.

    Returns (gated_rows_checked, legacy_numeric_rows_measured) so the caller can
    print how large the un-recomputed backlog still is.
    """
    def verified(mids: Any) -> bool:
        return any(
            ((materials.get(m) or {}).get("verification") or {}).get("status") == "verified"
            for m in (mids or [])
            if isinstance(m, str)
        )

    gated = 0
    legacy = 0
    for eid, evl in evaluations.items():
        summary = evl.get("summary") or ""
        if not _numbers_in(summary):
            continue
        if _is_new_row(eid, TRACEABILITY_CUTOFF, today=today):
            gated += 1
            if not str(evl.get("script_command") or "").strip():
                if not verified(evl.get("material_ids")):
                    if not str(evl.get("no_recompute_reason") or "").strip():
                        errors.append(
                            f"evaluations:{eid}: summary asserts a number, but the row has no "
                            "script_command, cites no verified material, and gives no "
                            "no_recompute_reason — a number no later session can reproduce is a "
                            "memory, not a measurement"
                        )
        else:
            legacy += 1
    for nid, note in notes.items():
        claims = note.get("claims")
        if not isinstance(claims, list):
            continue
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            if claim.get("kind") != "measured_fact":
                continue
            text = claim.get("text") or ""
            if not _numbers_in(text):
                continue
            if _is_new_row(nid, TRACEABILITY_CUTOFF, today=today):
                if str(claim.get("recomputer") or "").strip():
                    continue
                if verified(claim.get("material_ids")):
                    continue
                errors.append(
                    f"notes:{nid}: claim {claim.get('claim_id')!r} is a measured_fact asserting a "
                    "number without a recomputer (a command, or 'path#section') and without citing "
                    "a verified material"
                )
            else:
                legacy += 1
    return gated, legacy


def check_self_layer_attribution(
    notes: dict[str, dict[str, Any]],
    evaluations: dict[str, dict[str, Any]],
    errors: list[str],
    today: datetime.date | None = None,
) -> tuple[int, int, int, int]:
    """Check cognitive_operation on new notes and agency_stance on new evaluations.

    Layer 1 (source attribution) and Layer 2 (agency) of the six-layer self model.
    Returns (cogop_new, cogop_legacy, agency_new, agency_legacy).
    Legacy rows (pre-cutoff) are counted but not errored.
    """
    cogop_new = 0
    cogop_legacy = 0
    agency_new = 0
    agency_legacy = 0
    for nid, note in notes.items():
        if note.get("index_backfill"):
            continue
        if nid in COGNITIVE_OP_EXEMPT_IDS:
            cogop_legacy += 1
            continue
        if _is_new_row(nid, COGNITIVE_OP_CUTOFF, today=today):
            cogop_new += 1
            op = note.get("cognitive_operation")
            if op is None:
                errors.append(
                    f"notes:{nid}: post-cutoff note is missing cognitive_operation "
                    "(required from 2026-11-21 for source attribution, see docs/"
                    "2026-11-21-six-layer-self-model-improvement-proposals.md §1-A)"
                )
            elif op not in VALID_COGNITIVE_OPS:
                errors.append(
                    f"notes:{nid}: cognitive_operation {op!r} is not one of {sorted(VALID_COGNITIVE_OPS)}"
                )
        else:
            cogop_legacy += 1
    for eid, evl in evaluations.items():
        if eid in AGENCY_STANCE_EXEMPT_IDS:
            agency_legacy += 1
            continue
        if _is_new_row(eid, AGENCY_STANCE_CUTOFF, today=today):
            agency_new += 1
            stance = evl.get("agency_stance")
            if stance is None:
                errors.append(
                    f"evaluations:{eid}: post-cutoff evaluation is missing agency_stance "
                    "(required from 2026-11-21 for judgment of agency, see docs/"
                    "2026-11-21-six-layer-self-model-improvement-proposals.md §2-A)"
                )
            elif stance not in VALID_AGENCY_STANCES:
                errors.append(
                    f"evaluations:{eid}: agency_stance {stance!r} is not one of {sorted(VALID_AGENCY_STANCES)}"
                )
        else:
            agency_legacy += 1
    return cogop_new, cogop_legacy, agency_new, agency_legacy


def check_session_self_layer(
    sessions: dict[str, dict[str, Any]],
    errors: list[str],
    today: datetime.date | None = None,
    shard_of: dict[str, Path] | None = None,
    label_ids: frozenset[str] | None = None,
) -> tuple[int, int, int, int]:
    """Check session_type and self_layer_checks on new sessions.

    Layer 3 (embodiment) session typing and Layer I/II (preparation/verification)
    checklist enforcement. Returns (type_new, type_legacy, checks_new, checks_legacy).

    ``shard_of`` / ``label_ids`` are forwarded to ``_is_new_row`` exactly as
    ``check_registers`` already forwards them (2026-11-22).  This gate was the
    one ID-based check that read only the stamp and the wall clock, and the
    consequence was measured: ``SESSION-20261122-11b1d3`` sits in the shard
    ``state/sessions.d/2026-11-10-000000000000.jsonl``, so its stamp is provably
    an internal chronology label by ``_is_internal_label`` -- yet on 2026-11-21
    the wall clock still read the day before and the whole gate passed, while on
    2026-11-22 the same bytes, with no commit, turned it red.  A label row that
    was written before this rule existed cannot be given the two fields it
    predates, and a gate that flips on a clock tick rather than on a commit
    stops being read.  Two mechanisms already existed to express this (the
    shard proof and the errata waiver); the session gate was simply not wired
    to the first one.  The rule itself is unchanged and still covers every row
    whose stamp this test cannot prove to be a label.
    """
    shard_of = shard_of or {}
    type_new = 0
    type_legacy = 0
    checks_new = 0
    checks_legacy = 0
    for sid, s in sessions.items():
        if sid in SESSION_TYPE_EXEMPT_IDS:
            type_legacy += 1
        elif _is_new_row(
            sid,
            SESSION_TYPE_CUTOFF,
            today=today,
            shard=shard_of.get(sid),
            label_ids=label_ids,
        ):
            type_new += 1
            st = s.get("session_type")
            if st is None:
                errors.append(
                    f"sessions:{sid}: post-cutoff session is missing session_type "
                    "(required from 2026-11-21, see docs/"
                    "2026-11-21-six-layer-self-model-improvement-proposals.md §5-A)"
                )
            elif st not in VALID_SESSION_TYPES:
                errors.append(
                    f"sessions:{sid}: session_type {st!r} is not one of {sorted(VALID_SESSION_TYPES)}"
                )
        else:
            type_legacy += 1

        if sid in SELF_LAYER_CHECKS_EXEMPT_IDS:
            checks_legacy += 1
        elif _is_new_row(
            sid,
            SELF_LAYER_CHECKS_CUTOFF,
            today=today,
            shard=shard_of.get(sid),
            label_ids=label_ids,
        ):
            checks_new += 1
            slc = s.get("self_layer_checks")
            if slc is None:
                errors.append(
                    f"sessions:{sid}: post-cutoff session is missing self_layer_checks "
                    "(required from 2026-11-21 for six-layer verification hook)"
                )
            elif not isinstance(slc, dict):
                errors.append(f"sessions:{sid}: self_layer_checks must be an object")
            else:
                missing_keys = REQUIRED_CHECK_KEYS - set(slc.keys())
                if missing_keys:
                    errors.append(
                        f"sessions:{sid}: self_layer_checks missing keys: {sorted(missing_keys)}"
                    )
                for k, v in slc.items():
                    if k not in REQUIRED_CHECK_KEYS:
                        errors.append(f"sessions:{sid}: self_layer_checks has unknown key {k!r}")
                    elif not isinstance(v, bool):
                        errors.append(f"sessions:{sid}: self_layer_checks.{k} must be boolean")
        else:
            checks_legacy += 1
    return type_new, type_legacy, checks_new, checks_legacy


def double_reading_advisory(
    read_log: dict[str, dict[str, Any]],
    materials: dict[str, dict[str, Any]],
) -> str | None:
    """How much of the corpus has been read twice, by different sessions.

    The archive cannot choose which model a session gets, so the only handle on
    model-to-model variance is repetition: the same material read from two
    session draws.  Agreement and disagreement are both informative, and the
    count is what makes the variance estimable at all.
    """
    manual = frozenset({"quoted", "summarized", "interpreted", "reinterpreted", "contested", "counted"})
    readers: dict[str, set[str]] = {}
    readings: dict[str, set[tuple[str, str]]] = {}
    for row in read_log.values():
        if row.get("reading") not in manual:
            continue
        target = row.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        mid = target.get("id")
        sid = row.get("session_id")
        if not isinstance(mid, str) or not isinstance(sid, str):
            continue
        readers.setdefault(mid, set()).add(sid)
        readings.setdefault(mid, set()).add((sid, str(row.get("reading"))))
    multi = {m: s for m, s in readers.items() if len(s) >= 2}
    if not multi:
        return None
    upgraded = sum(
        1
        for m in multi
        if ((materials.get(m) or {}).get("verification") or {}).get("depth") in ("full_text", "re_derived")
    )
    return (
        f"INFO: double reading (advisory): {len(multi)}/{len(readers)} materials read by >=2 sessions "
        f"({100 * len(multi) / max(1, len(readers)):.1f}%); {upgraded} of those carry a full_text/re_derived "
        "verification.depth. This count is the only handle on model-to-model variance — a material read "
        "once has an unknown agreement rate"
    )


def check_refs(
    collection_name: str,
    records: dict[str, dict[str, Any]],
    field: str,
    target_name: str,
    target_records: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for record_id, record in records.items():
        values = record.get(field, [])
        if not isinstance(values, list):
            continue  # schema validation reports the shape error
        for value in values:
            if value not in target_records:
                errors.append(f"{collection_name}:{record_id}: {field} references unknown {target_name} ID {value!r}")


def main(argv: list[str] | None = None) -> int:
    import argparse as _argparse

    _parser = _argparse.ArgumentParser(add_help=True)
    _parser.add_argument(
        "--active-epoch-only",
        action="store_true",
        help=(
            "Verify frozen epochs (<= 2026-11-20) via state/epoch_manifest.json SHA-256 "
            "rollup and run per-row JSON Schema validation only on active-epoch shards (>= 2026-11-21)."
        ),
    )
    _args, _unknown = _parser.parse_known_args(argv)
    active_epoch_only = bool(_args.active_epoch_only)

    errors: list[str] = []
    if active_epoch_only:
        import memory_tiers

        ep_ok, ep_msg = memory_tiers.check_epoch_manifest(ROOT)
        if not ep_ok:
            errors.append(ep_msg)
    # 2026-11-21: named gate defects are reported, not raised (see KNOWN_* dicts).
    gate_advisories: list[str] = []
    specs: dict[str, tuple[Path, str]] = {}
    for name, (filename, id_key, _schema) in COLLECTIONS.items():
        base_path = ROOT / "state" / filename
        if name in OPTIONAL_EMPTY_COLLECTIONS and not base_path.exists() and not ledger_io.shard_dir(base_path).is_dir():
            continue
        specs[name] = (base_path, id_key)
    try:
        collections, load_errors = ledger_io.load_collections(specs, root=ROOT)
    except ledger_io.LedgerBusy as exc:
        print("FAIL: ledgers are being rewritten concurrently; retry in a moment")
        print(f"  - {exc}")
        return 2
    for name in COLLECTIONS:
        collections.setdefault(name, {})
    errors.extend(load_errors)
    # Where each row was read from.  A row's shard is evidence about the day it
    # was written (see _is_internal_label); parsed rows alone cannot show it.
    record_shards: dict[str, Path] = {}
    for name, (filename, id_key, _schema) in COLLECTIONS.items():
        base_path = ROOT / "state" / filename
        for path in ledger_io.collection_files(base_path):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for line in text.splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and isinstance(record.get(id_key), str):
                    record_shards.setdefault(record[id_key], path)

    for name, (_filename, _id_key, schema_filename) in COLLECTIONS.items():
        records = collections[name]
        schema_path = ROOT / "schema" / schema_filename
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{schema_path.relative_to(ROOT)}: cannot load schema: {exc}")
            continue
        if not isinstance(schema, dict):
            errors.append(f"{schema_path.relative_to(ROOT)}: schema must be a JSON object")
            continue
        for record_id, record in records.items():
            if active_epoch_only:
                sp = record_shards.get(record_id)
                if sp is not None and memory_tiers.is_frozen_shard(sp):
                    continue
            validate_value(record, schema, schema, f"{name}:{record_id}", errors)

    questions = collections.get("questions", {})
    motifs = collections.get("motifs", {})
    materials = collections.get("materials", {})
    fragments = collections.get("fragments", {})
    relations = collections.get("relations", {})
    sessions = collections.get("sessions", {})

    check_refs("questions", questions, "motif_ids", "motif", motifs, errors)
    check_refs("questions", questions, "material_ids", "material", materials, errors)
    check_refs("questions", questions, "previous_question_ids", "question", questions, errors)
    check_refs("motifs", motifs, "question_ids", "question", questions, errors)
    check_refs("motifs", motifs, "material_ids", "material", materials, errors)
    check_refs("materials", materials, "motif_ids", "motif", motifs, errors)
    check_refs("fragments", fragments, "question_ids", "question", questions, errors)
    check_refs("fragments", fragments, "motif_ids", "motif", motifs, errors)
    check_refs("fragments", fragments, "material_ids", "material", materials, errors)
    check_refs("sessions", sessions, "question_ids", "question", questions, errors)
    check_refs("sessions", sessions, "context_material_ids", "material", materials, errors)
    check_refs("sessions", sessions, "produced_fragment_ids", "fragment", fragments, errors)
    check_refs("sessions", sessions, "new_question_ids", "question", questions, errors)

    for fragment_id, record in fragments.items():
        session_id = record.get("session_id")
        if session_id and session_id not in sessions:
            errors.append(f"fragments:{fragment_id}: session_id references unknown session {session_id!r}")

    read_logs = collections.get("read_log", {})
    notes = collections.get("notes", {})

    # --- notes: curated judgments about readings/*.md ---------------------
    # The report body is the source of truth for derived facts (harvested by
    # tools/note_index.py); here we only check that a row points at a real file,
    # a real session, real ledger IDs, and a real earlier row it supersedes.
    for note_id, record in notes.items():
        for field in ("session_id", "report_session_id"):
            value = record.get(field)
            if isinstance(value, str) and value and value not in sessions:
                errors.append(f"notes:{note_id}: {field} references unknown session {value!r}")
        path = record.get("path")
        if isinstance(path, str):
            candidate = Path(path)
            if candidate.is_absolute() or ".." in candidate.parts:
                errors.append(f"notes:{note_id}: path must be repository-relative without '..': {path!r}")
            elif not (ROOT / candidate).is_file():
                errors.append(f"notes:{note_id}: path references a missing file {path!r}")
        claims = record.get("claims")
        if isinstance(claims, list):
            seen_claims: set[str] = set()
            for position, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    continue  # schema validation reports the shape error
                claim_id = claim.get("claim_id")
                if isinstance(claim_id, str):
                    if claim_id in seen_claims:
                        errors.append(f"notes:{note_id}: duplicate claim_id {claim_id!r}")
                    seen_claims.add(claim_id)
                for field, target_name in NOTE_CLAIM_REF_FIELDS:
                    values = claim.get(field, [])
                    if not isinstance(values, list):
                        continue
                    targets = collections.get(target_name, {})
                    for value in values:
                        if value not in targets:
                            errors.append(
                                f"notes:{note_id}: claims[{position}].{field} references unknown "
                                f"{target_name} ID {value!r}"
                            )
        supersedes = record.get("supersedes")
        if isinstance(supersedes, list):
            for sup_id in supersedes:
                if not isinstance(sup_id, str):
                    continue
                if sup_id == note_id:
                    errors.append(f"notes:{note_id}: supersedes cannot reference itself")
                elif sup_id not in notes:
                    errors.append(f"notes:{note_id}: supersedes references unknown note ID {sup_id!r}")
                elif notes[sup_id].get("path") != path:
                    errors.append(
                        f"notes:{note_id}: supersedes note {sup_id!r} is about "
                        f"{notes[sup_id].get('path')!r}, expected {path!r}"
                    )

    note_visit_state: dict[str, int] = {}
    for start_id in notes:
        if note_visit_state.get(start_id, 0) != 0:
            continue
        stack: list[tuple[str, int]] = [(start_id, 0)]
        note_visit_state[start_id] = 1
        while stack:
            cur_id, idx = stack[-1]
            sup_list = notes[cur_id].get("supersedes")
            neighbors = [
                s for s in (sup_list if isinstance(sup_list, list) else [])
                if isinstance(s, str) and s in notes and s != cur_id
            ]
            if idx < len(neighbors):
                stack[-1] = (cur_id, idx + 1)
                nxt_id = neighbors[idx]
                st = note_visit_state.get(nxt_id, 0)
                if st == 1:
                    errors.append(f"notes:{cur_id}: cycle detected in supersedes chain via {nxt_id!r}")
                elif st == 0:
                    note_visit_state[nxt_id] = 1
                    stack.append((nxt_id, 0))
            else:
                note_visit_state[cur_id] = 2
                stack.pop()

    check_note_brakes(notes, errors)
    check_claim_wiring(notes, errors)
    hypotheses = collections.get("hypotheses", {})
    evaluations = collections.get("evaluations", {})
    errata_base = ROOT / "state" / "errata.jsonl"
    errata_records: dict[str, dict[str, Any]] = {}
    if errata_base.exists() or ledger_io.shard_dir(errata_base).is_dir():
        errata_records = ledger_io.load_jsonl_union(errata_base, "errata_id", errors, root=ROOT)
    gate_waivers_in_force = gate_waivers(errata_records, errors)

    # 2026-11-21 merge: origin/main added forward-label evidence to the register
    # check (PR #1005) while this branch moved the register waivers from a dict in
    # this file into state/errata.d/. Both survive: the call passes the label
    # evidence main introduced *and* the waivers this branch reads from the
    # ledger. A waiver is therefore still data, and the new label rule is still on.
    forward_labels = build_forward_label_evidence(collections)
    check_registers(
        collections,
        errors,
        gate_advisories,
        waivers=gate_waivers_in_force,
        shard_of=record_shards,
        label_ids=forward_labels,
    )

    check_refs("hypotheses", hypotheses, "question_ids", "question", questions, errors)
    check_refs("hypotheses", hypotheses, "parent_hypothesis_ids", "hypothesis", hypotheses, errors)
    check_refs("hypotheses", hypotheses, "supporting_material_ids", "material", materials, errors)
    check_refs("hypotheses", hypotheses, "counter_material_ids", "material", materials, errors)
    check_refs("hypotheses", hypotheses, "source_note_ids", "note", notes, errors)

    for hyp_id, hyp in hypotheses.items():
        session_id = hyp.get("session_id")
        if isinstance(session_id, str) and session_id not in sessions:
            errors.append(f"hypotheses:{hyp_id}: session_id references unknown session {session_id!r}")
        parents = hyp.get("parent_hypothesis_ids")
        lineage_op = hyp.get("lineage_op")
        if isinstance(parents, list):
            if hyp_id in parents:
                errors.append(f"hypotheses:{hyp_id}: parent_hypothesis_ids cannot reference itself")
            if lineage_op == "root" and parents:
                errors.append(f"hypotheses:{hyp_id}: lineage_op 'root' must have empty parent_hypothesis_ids")
            elif lineage_op in ("refines", "splits", "synthesizes") and not parents:
                errors.append(
                    f"hypotheses:{hyp_id}: lineage_op {lineage_op!r} requires at least one parent_hypothesis_id"
                )
        excl = str(hyp.get("exclusion_clause") or "").strip().lower()
        if excl in _TRIVIAL_EXCLUSION_PATTERNS:
            errors.append(f"hypotheses:{hyp_id}: exclusion_clause must state a concrete falsification criterion")

    hyp_visit: dict[str, int] = {}
    for start_id in hypotheses:
        if hyp_visit.get(start_id, 0) != 0:
            continue
        stack: list[tuple[str, int]] = [(start_id, 0)]
        hyp_visit[start_id] = 1
        while stack:
            cur_id, idx = stack[-1]
            p_list = hypotheses[cur_id].get("parent_hypothesis_ids")
            neighbors = [
                p for p in (p_list if isinstance(p_list, list) else [])
                if isinstance(p, str) and p in hypotheses and p != cur_id
            ]
            if idx < len(neighbors):
                stack[-1] = (cur_id, idx + 1)
                nxt_id = neighbors[idx]
                st = hyp_visit.get(nxt_id, 0)
                if st == 1:
                    errors.append(f"hypotheses:{cur_id}: cycle detected in parent_hypothesis_ids via {nxt_id!r}")
                elif st == 0:
                    hyp_visit[nxt_id] = 1
                    stack.append((nxt_id, 0))
            else:
                hyp_visit[cur_id] = 2
                stack.pop()

    check_refs("evaluations", evaluations, "compared_against_hypothesis_ids", "hypothesis", hypotheses, errors)
    check_refs("evaluations", evaluations, "spawned_hypothesis_ids", "hypothesis", hypotheses, errors)
    # 2026-11-16 (P-5): "narrowing the child hands the remaining scope to the
    # parent" got its own field. It must point at real hypotheses, and never at
    # the row's own target.
    check_refs(
        "evaluations",
        evaluations,
        "scope_inherited_by_hypothesis_ids",
        "hypothesis",
        hypotheses,
        errors,
    )
    check_refs("evaluations", evaluations, "material_ids", "material", materials, errors)
    check_refs("evaluations", evaluations, "fragment_ids", "fragment", fragments, errors)
    check_refs("evaluations", evaluations, "note_ids", "note", notes, errors)
    depth_new, depth_legacy = check_verification_depth(materials, errors)
    num_gated, num_legacy = check_number_traceability(evaluations, notes, materials, errors)
    today = datetime.date.today()
    cogop_new, cogop_legacy, agency_new, agency_legacy = check_self_layer_attribution(
        notes, evaluations, errors, today=today
    )
    stype_new, stype_legacy, slc_new, slc_legacy = check_session_self_layer(
        collections.get("sessions", {}),
        errors,
        today=today,
        shard_of=record_shards,
        label_ids=forward_labels,
    )
    errata_advisory = errata_schema_advisory(errata_records)
    psc_advisory = psc_verification_advisory(evaluations, materials)
    psc_new_advisory = psc_new_row_advisory(evaluations, materials)
    # 2026-11-16 (P-6): a correction may withdraw an evaluation row's weight.
    # 2026-11-18 (Gate 2): 'suppress_retrieval' dampens retrieval of a contradicted
    # material/fragment/note/hypothesis without erasing the ledger record.
    suppress_collections = {
        "material": materials,
        "fragment": fragments,
        "note": notes,
        "hypothesis": hypotheses,
    }
    for err_id, erec in errata_records.items():
        weff = erec.get("weight_effect")
        if weff == "void_row":
            if erec.get("subject_type") != "evaluation":
                errors.append(
                    f"errata:{err_id}: weight_effect 'void_row' requires subject_type 'evaluation' "
                    f"(got {erec.get('subject_type')!r})"
                )
                continue
            subject = erec.get("subject_id")
            if not isinstance(subject, str) or subject not in evaluations:
                errors.append(
                    f"errata:{err_id}: weight_effect 'void_row' names unknown evaluation {subject!r}"
                )
        elif weff == "suppress_retrieval":
            stype = erec.get("subject_type")
            subject = erec.get("subject_id")
            if stype is None and isinstance(erec.get("fragment_id"), str):
                stype = "fragment"
                subject = erec.get("fragment_id")
            if stype not in suppress_collections:
                errors.append(
                    f"errata:{err_id}: weight_effect 'suppress_retrieval' requires subject_type in "
                    f"{list(SUPPRESS_RETRIEVAL_SUBJECT_TYPES)} (got {stype!r})"
                )
                continue
            if not isinstance(subject, str) or subject not in suppress_collections[stype]:
                errors.append(
                    f"errata:{err_id}: weight_effect 'suppress_retrieval' names unknown "
                    f"{stype} {subject!r}"
                )
            if erec.get("verdict") != "contradicted":
                errors.append(
                    f"errata:{err_id}: weight_effect 'suppress_retrieval' requires verdict "
                    f"'contradicted' (got {erec.get('verdict')!r})"
                )
    if errata_records:
        check_refs("evaluations", evaluations, "errata_ids", "errata", errata_records, errors)
        check_errata_addressee_labels(errata_records, errors)
        check_errata_duplicate_claims(errata_records, errors)

    for evl_id, evl in evaluations.items():
        session_id = evl.get("session_id")
        if isinstance(session_id, str) and session_id not in sessions:
            errors.append(f"evaluations:{evl_id}: session_id references unknown session {session_id!r}")
        target_hid = evl.get("target_hypothesis_id")
        if isinstance(target_hid, str) and target_hid not in hypotheses:
            errors.append(
                f"evaluations:{evl_id}: target_hypothesis_id references unknown hypothesis {target_hid!r}"
            )
        inherited = evl.get("scope_inherited_by_hypothesis_ids")
        if isinstance(inherited, list) and target_hid in inherited:
            errors.append(
                f"evaluations:{evl_id}: scope_inherited_by_hypothesis_ids cannot include "
                "target_hypothesis_id (the target is narrowed; the inheritor receives the remainder)"
            )
        compared = evl.get("compared_against_hypothesis_ids")
        if isinstance(compared, list) and target_hid in compared:
            errors.append(
                f"evaluations:{evl_id}: compared_against_hypothesis_ids cannot include target_hypothesis_id"
            )
        if evl.get("evidence_type") == "reproducible_script" and not (evl.get("script_command") or "").strip():
            errors.append(
                f"evaluations:{evl_id}: evidence_type 'reproducible_script' requires non-empty script_command"
            )

    endpoint_collections = {
        "question": questions,
        "motif": motifs,
        "material": materials,
        "fragment": fragments,
        "session": sessions,
        "note": notes,
        "hypothesis": hypotheses,
        "evaluation": evaluations,
        # 2026-11-15: errata and editorial decisions became addressable. Before
        # this, 282 errata could not be the target of any of the 13,656 read_log
        # rows or 7,007 relations, so "corrections are never read" and "reading a
        # correction cannot be written down" were the same observation.
        "erratum": errata_records,
        "editorial_decision": collections.get("editorial_decisions", {}),
        # 2026-11-23: relations became addressable.  The recorded reason for
        # excluding them ("citing the edge adds no reachable content") was measured
        # and is false for 6,796 of 7,097 rows -- 447,494 characters of relation
        # notes appear in neither endpoint.  tools/navigation_metrics.py --relations.
        "relation": collections.get("relations", {}),
    }
    for read_id, record in read_logs.items():
        session_id = record.get("session_id")
        if session_id and session_id not in sessions:
            errors.append(f"read_log:{read_id}: session_id references unknown session {session_id!r}")
        ref = record.get("target")
        if isinstance(ref, dict):
            target = endpoint_collections.get(ref.get("type"))
            if target is None or ref.get("id") not in target:
                errors.append(
                    f"read_log:{read_id}: target references unknown "
                    f"{ref.get('type')} ID {ref.get('id')!r}"
                )

    check_read_log_addressing(read_logs, errors)
    check_role_receipts(sessions, errors, gate_advisories, waivers=gate_waivers_in_force)
    check_psc_verification_gate(evaluations, materials, errors)
    check_material_duplicate_identifiers(materials, errors)
    check_evaluation_descendant_collision(evaluations, hypotheses, errors)
    check_evidence_record_paths(materials, errors)
    check_evidence_path_corrections(
        collections.get("editorial_decisions", {}), materials, errors
    )

    ed_valid_status = {
        "fragment": {"draft", "selected", "archived"},
        "question": {"open", "paused", "archived"},
        "material": {"verified", "partially_verified", "unverified", "corrected"},
    }
    ed_records = collections.get("editorial_decisions", {})
    for decision_id, record in ed_records.items():
        session_id = record.get("session_id")
        if session_id and session_id not in sessions:
            errors.append(
                f"editorial_decisions:{decision_id}: session_id references unknown session {session_id!r}"
            )
        ref = record.get("target")
        if isinstance(ref, dict):
            ttype = ref.get("type")
            target = endpoint_collections.get(ttype)
            if target is None or ref.get("id") not in target:
                errors.append(
                    f"editorial_decisions:{decision_id}: target references unknown "
                    f"{ttype} ID {ref.get('id')!r}"
                )
            allowed = ed_valid_status.get(ttype)
            if allowed and record.get("status") not in allowed:
                errors.append(
                    f"editorial_decisions:{decision_id}: status {record.get('status')!r} "
                    f"is not valid for target type {ttype!r} (expected {sorted(allowed)})"
                )
            vmethod = record.get("verification_method")
            if ttype == "material" and record.get("status") == "verified":
                if not isinstance(vmethod, str) or len(vmethod.strip()) < 8:
                    errors.append(
                        f"editorial_decisions:{decision_id}: material status 'verified' requires "
                        "non-empty verification_method (>= 8 chars) stating how the primary text was checked"
                    )
            elif ttype == "material" and record.get("status") == "unverified":
                # A downgrade must be able to say why it is one (2026-11-19).  Before
                # this, only `verified` demanded a method, so the honest repair of a
                # row whose evidence record had vanished — the one direction the ledger
                # most needs recorded — was the only direction that could stay silent.
                if not isinstance(vmethod, str) or len(vmethod.strip()) < 8:
                    errors.append(
                        f"editorial_decisions:{decision_id}: material status "
                        f"{record.get('status')!r} requires non-empty verification_method "
                        "(>= 8 chars) stating what the re-check found"
                    )
            elif ttype != "material" and vmethod is not None:
                errors.append(
                    f"editorial_decisions:{decision_id}: verification_method is only valid for "
                    f"target type 'material' (got {ttype!r})"
                )
        supersedes = record.get("supersedes")
        if isinstance(supersedes, list):
            for sup_id in supersedes:
                if not isinstance(sup_id, str):
                    continue
                if sup_id == decision_id:
                    errors.append(
                        f"editorial_decisions:{decision_id}: supersedes cannot reference itself"
                    )
                elif sup_id not in ed_records:
                    errors.append(
                        f"editorial_decisions:{decision_id}: supersedes references unknown "
                        f"editorial_decision ID {sup_id!r}"
                    )
                elif ed_records[sup_id].get("target") != ref:
                    errors.append(
                        f"editorial_decisions:{decision_id}: supersedes decision {sup_id!r} "
                        f"targets {ed_records[sup_id].get('target')!r}, expected {ref!r}"
                    )

    ed_visit_state: dict[str, int] = {}
    for start_id in ed_records:
        if ed_visit_state.get(start_id, 0) != 0:
            continue
        stack: list[tuple[str, int]] = [(start_id, 0)]
        ed_visit_state[start_id] = 1
        while stack:
            cur_id, idx = stack[-1]
            sup_list = ed_records[cur_id].get("supersedes")
            neighbors = [
                s for s in (sup_list if isinstance(sup_list, list) else [])
                if isinstance(s, str) and s in ed_records and s != cur_id
            ]
            if idx < len(neighbors):
                stack[-1] = (cur_id, idx + 1)
                nxt_id = neighbors[idx]
                st = ed_visit_state.get(nxt_id, 0)
                if st == 1:
                    errors.append(
                        f"editorial_decisions:{cur_id}: cycle detected in supersedes chain via {nxt_id!r}"
                    )
                elif st == 0:
                    ed_visit_state[nxt_id] = 1
                    stack.append((nxt_id, 0))
            else:
                ed_visit_state[cur_id] = 2
                stack.pop()
    for relation_id, relation in relations.items():
        for endpoint in ("left", "right"):
            ref = relation.get(endpoint)
            if not isinstance(ref, dict):
                continue
            target = endpoint_collections.get(ref.get("type"))
            if target is None or ref.get("id") not in target:
                errors.append(
                    f"relations:{relation_id}: {endpoint} references unknown "
                    f"{ref.get('type')} ID {ref.get('id')!r}"
                )

    if errors:
        print("FAIL: literary inquiry seed has errors")
        for error in errors:
            print("  - " + error)
        if errata_advisory:
            print(errata_advisory)
        if psc_advisory:
            print(psc_advisory)
        if psc_new_advisory:
            print(psc_new_advisory)
        return 1

    counts = ", ".join(f"{name}={len(records)}" for name, records in collections.items())
    print(f"PASS: literary inquiry seed valid ({counts})")
    if errata_advisory:
        print(errata_advisory)
    if psc_advisory:
        print(psc_advisory)
    if psc_new_advisory:
        print(psc_new_advisory)
    for line in gate_advisories:
        print(line)
    # 2026-11-20 (③④): report the backlog the new gates cannot fix retroactively.
    print(
        f"INFO: verification.depth (advisory): {depth_new} material(s) carry a depth; {depth_legacy} legacy `verified` row(s) predate the "
        "field, so on those rows 'verified' still means 'a check happened', not 'the passage was read'"
    )
    print(
        f"INFO: number traceability (advisory): {num_gated} numeric row(s) from {TRACEABILITY_CUTOFF} "
        f"on are gated by script/material/reason; {num_legacy} legacy numeric rows are ungated and "
        "remain un-recomputed history"
    )
    print(
        f"INFO: self-layer attribution (advisory): {cogop_new} post-cutoff notes carry cognitive_operation "
        f"({cogop_legacy} legacy rows ungated); {agency_new} post-cutoff evaluations carry agency_stance "
        f"({agency_legacy} legacy rows ungated)"
    )
    print(
        f"INFO: self-layer session hooks (advisory): {stype_new} post-cutoff sessions carry session_type "
        f"({stype_legacy} legacy sessions ungated); {slc_new} post-cutoff sessions carry self_layer_checks "
        f"({slc_legacy} legacy sessions ungated)"
    )
    dr_advisory = double_reading_advisory(read_logs, materials)
    if dr_advisory:
        print(dr_advisory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
