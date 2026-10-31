#!/usr/bin/env python3
"""Validate the seed ledgers and their cross-references (stdlib only).

Implements the JSON-Schema subset used in schema/*.schema.json plus checks
that IDs referenced across JSONL collections actually exist.
"""
from __future__ import annotations

import json
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
}


def is_existing_reading_note(root: Path, ref_id: object) -> bool:
    """Return True only for a safe ``readings/<filename>.md`` id naming a real file.

    Reading notes are prose files, not a JSONL collection, so a
    ``reading_note`` read_log target cannot be resolved through
    ``endpoint_collections``.  The id must be the repository-relative path
    already used by ``tools/taxonomy_plan.py``; a bare filename, a path
    traversal, or a missing file is an unknown target, exactly like an
    unknown ledger ID.  This checks that the note exists, never that it
    was read or endorsed.
    """
    if not isinstance(ref_id, str) or not ref_id.startswith("readings/"):
        return False
    name = ref_id[len("readings/") :]
    if (
        not name
        or not name.endswith(".md")
        or "/" in name
        or "\\" in name
        or ".." in name
        or "\x00" in name
    ):
        return False
    readings_dir = (root / "readings").resolve()
    candidate = (readings_dir / name).resolve()
    return candidate.parent == readings_dir and candidate.is_file()


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

    endpoint_collections = {
        "question": questions,
        "motif": motifs,
        "material": materials,
        "fragment": fragments,
        "session": sessions,
    }
    for read_id, record in read_logs.items():
        session_id = record.get("session_id")
        if session_id and session_id not in sessions:
            errors.append(f"read_log:{read_id}: session_id references unknown session {session_id!r}")
        ref = record.get("target")
        if isinstance(ref, dict):
            if ref.get("type") == "reading_note":
                # Prose target: resolve against readings/ on disk, not a
                # ledger collection. Relations and editorial decisions
                # below intentionally keep the five ledger types only.
                if not is_existing_reading_note(ROOT, ref.get("id")):
                    errors.append(
                        f"read_log:{read_id}: target references unknown "
                        f"{ref.get('type')} ID {ref.get('id')!r}"
                    )
            else:
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
    for decision_id, record in collections.get("editorial_decisions", {}).items():
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
