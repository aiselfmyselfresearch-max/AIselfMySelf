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
_ID_STAMP = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-(\d{8})-")


def id_stamp(record_id: Any) -> str | None:
    """Return the YYYYMMDD stamp inside a ledger ID, or None when it has none."""
    match = _ID_STAMP.match(record_id) if isinstance(record_id, str) else None
    return match.group(1) if match else None


def _as_day(stamp: str) -> datetime.date | None:
    try:
        return datetime.date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8]))
    except ValueError:
        return None


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
}
_LEDGER_ID_RE = re.compile(r"^(?:HYP|MAT|NOTE|Q|SESSION|EVL|FRAG|MOTIF)-")


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


def main() -> int:
    errors: list[str] = []
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

    hypotheses = collections.get("hypotheses", {})
    evaluations = collections.get("evaluations", {})
    errata_base = ROOT / "state" / "errata.jsonl"
    errata_records: dict[str, dict[str, Any]] = {}
    if errata_base.exists() or ledger_io.shard_dir(errata_base).is_dir():
        errata_records = ledger_io.load_jsonl_union(errata_base, "errata_id", errors, root=ROOT)

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
    check_refs("evaluations", evaluations, "material_ids", "material", materials, errors)
    check_refs("evaluations", evaluations, "fragment_ids", "fragment", fragments, errors)
    check_refs("evaluations", evaluations, "note_ids", "note", notes, errors)
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

    ed_valid_status = {
        "fragment": {"draft", "selected", "archived"},
        "question": {"open", "paused", "archived"},
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
        return 1

    counts = ", ".join(f"{name}={len(records)}" for name, records in collections.items())
    print(f"PASS: literary inquiry seed valid ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
