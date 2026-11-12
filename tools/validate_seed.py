#!/usr/bin/env python3
"""Validate the seed ledgers and their cross-references (stdlib only).

Implements the JSON-Schema subset used in schema/*.schema.json plus checks
that IDs referenced across JSONL collections actually exist.
"""
from __future__ import annotations

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
}

# Optional claim scope: the three distinctions a claim can be silent about.
# Values are free text (must appear verbatim in the report) or a ledger ID, so
# the validator never has to know the archive's vocabulary.
NOTE_CLAIM_SCOPE_FIELDS = ("object", "basis", "sense")
NOTE_CLAIM_SCOPE_LIMIT = 200
LEDGER_ID_PATTERN = re.compile(r"^(Q|MAT|FRAG|MOTIF|REL|SESSION|NOTE|ED|ERR)-[0-9A-Za-z-]+$")

# Fields of a note claim that must point at existing ledger records.
NOTE_CLAIM_REF_FIELDS = (
    ("question_ids", "questions"),
    ("fragment_ids", "fragments"),
    ("material_ids", "materials"),
    ("motif_ids", "motifs"),
)


def claim_scope_errors(claim: dict[str, Any], body: str) -> list[str]:
    """Check a claim's optional ``scope`` against the report body it cites.

    The scope records which object a claim speaks about, by which basis, in
    which sense. Its values must be anchored: either a verbatim fragment of the
    report body (so the words come from the report, not from a new vocabulary),
    or a ledger ID (so the scope points at an existing record). An absent scope
    is legal and means undecided.
    """
    scope = claim.get("scope")
    if not isinstance(scope, dict):
        return []
    errors: list[str] = []
    for field in NOTE_CLAIM_SCOPE_FIELDS:
        value = scope.get(field)
        if not isinstance(value, str) or not value.strip():
            continue  # schema validation reports the shape error
        if len(value) > NOTE_CLAIM_SCOPE_LIMIT:
            errors.append(f"scope.{field} is too long ({len(value)} > {NOTE_CLAIM_SCOPE_LIMIT})")
        elif value not in body and not LEDGER_ID_PATTERN.match(value):
            errors.append(
                f"scope.{field} must quote the report verbatim or name a ledger ID "
                f"(quote the words, do not describe them): {value!r}"
            )
    return errors


NOTE_AS_OF_PATTERN = re.compile(r"20\d\d-\d\d-\d\d|20\d\d年|時点|現在の")
NOTE_DATED_ID_PATTERN = re.compile(
    r"(?:SESSION|READ|NOTE|NOTE-TMP|ERR|ED|REL|MAT|MAT-LIT|MAT-EVD|MAT-TRC|MAT-ARC|FRAG)"
    r"-20\d{6}"
)
NOTE_NUMBER_PATTERN = re.compile(r"[0-9]")


def claim_needs_as_of(claim: dict[str, Any]) -> bool:
    """True when a claim states a number but says nothing about *when*.

    A ``measured_fact`` count describes the ledger at one moment.  Nothing in the
    record used to carry that moment, so a later reader could not tell a current
    figure from a stale one (see ``readings/2026-11-11-numbers-carry-no-date.md``
    and ``readings/2026-11-11-the-third-audit-and-the-case-for-one-field.md``).
    The check is a WARNING, not an error: making it an error would turn every
    pre-existing claim of this shape invalid at once, which stops the ledger
    instead of improving it.  ``tools/claim_dates.py`` lists the same claims.
    """
    if claim.get("kind") != "measured_fact":
        return False
    text = claim.get("text")
    if not isinstance(text, str) or not NOTE_NUMBER_PATTERN.search(text):
        return False
    if NOTE_AS_OF_PATTERN.search(text) or NOTE_DATED_ID_PATTERN.search(text):
        return False
    measured_at = claim.get("measured_at")
    return not (isinstance(measured_at, str) and measured_at.strip())


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
    if isinstance(value, str) and isinstance(spec.get("minLength"), int) and len(value) < spec["minLength"]:
        errors.append(f"{path}: string shorter than minLength {spec['minLength']}")
    pattern = spec.get("pattern")
    if isinstance(value, str) and isinstance(pattern, str) and not re.search(pattern, value):
        errors.append(f"{path}: string does not match pattern {pattern!r}")

    if isinstance(value, list):
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
    specs = {
        name: (ROOT / "state" / filename, id_key)
        for name, (filename, id_key, _schema) in COLLECTIONS.items()
    }
    try:
        collections, load_errors = ledger_io.load_collections(specs, root=ROOT)
    except ledger_io.LedgerBusy as exc:
        print("FAIL: ledgers are being rewritten concurrently; retry in a moment")
        print(f"  - {exc}")
        return 2
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
    undated_claims: list[str] = []

    # --- notes: curated judgments about readings/*.md ---------------------
    # The report body is the source of truth for derived facts (harvested by
    # tools/note_index.py); here we only check that a row points at a real file,
    # a real session, real ledger IDs, and a real earlier row it supersedes.
    report_bodies: dict[str, str] = {}
    for note_id, record in notes.items():
        body_path = record.get("path")
        report_body = ""
        if isinstance(body_path, str) and body_path in report_bodies:
            report_body = report_bodies[body_path]
        elif isinstance(body_path, str) and (ROOT / body_path).is_file():
            try:
                report_body = (ROOT / body_path).read_text(encoding="utf-8")
            except OSError:
                report_body = ""
            report_bodies[body_path] = report_body
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
                for problem in claim_scope_errors(claim, report_body):
                    errors.append(f"notes:{note_id}: claims[{position}].{problem}")
                if claim_needs_as_of(claim):
                    undated_claims.append(str(claim.get("claim_id") or f"{note_id}[{position}]"))
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

    endpoint_collections = {
        "question": questions,
        "motif": motifs,
        "material": materials,
        "fragment": fragments,
        "session": sessions,
        "note": notes,
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

    if undated_claims:
        print(
            f"WARN: {len(undated_claims)} measured_fact claims state a number without an "
            f"as-of date (text or measured_at)"
        )
        print("      list them with: python3 tools/claim_dates.py --list")

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
