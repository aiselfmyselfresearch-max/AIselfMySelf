#!/usr/bin/env python3
"""Serve the interactive AIselfMySelf archive viewer over HTTP (stdlib only).

Reads state/*.jsonl, tools/voice_audit.py metrics, and readings/*.md dynamically
on every /api/state request so updates appear immediately on page refresh.
Binds to 0.0.0.0 by default for browser preview compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import ledger_io
from abjection_audit import measure_abjection_audit
from war_audit import measure_war_audit
from secrecy_audit import measure_secrecy_audit
from secret_audit import measure as measure_secret_audit
from boredom_audit import measure_boredom_audit
from sky_audit import measure_sky_audit
from vegetal_audit import measure_vegetal_audit
from currency_audit import measure_currency_audit
from eros_audit import measure_eros_audit
from signature_audit import measure_signature_audit
from inspect_inquiry import build_context_packet, load_all
from passion_audit import GROUPS as PASSION_GROUPS, measure as measure_passion_audit
from prayer_audit import measure_prayer_audit
from validate_seed import COLLECTIONS, ROOT, load_jsonl
from voice_audit import compute_voice_audit

VIEWER_DIR = ROOT / "viewer"
READINGS_DIR = ROOT / "readings"


def compute_metabolism_snapshot(payload: dict[str, object]) -> dict[str, object]:
    """Compute pure in-memory archive metabolism metrics from an already-loaded payload."""
    materials: list[dict[str, object]] = payload["materials"]  # type: ignore[assignment]
    motifs: list[dict[str, object]] = payload["motifs"]  # type: ignore[assignment]
    questions: list[dict[str, object]] = payload["questions"]  # type: ignore[assignment]
    fragments: list[dict[str, object]] = payload["fragments"]  # type: ignore[assignment]
    relations: list[dict[str, object]] = payload["relations"]  # type: ignore[assignment]
    sessions: list[dict[str, object]] = payload["sessions"]  # type: ignore[assignment]

    mat_ids = {str(m["material_id"]) for m in materials}
    motif_ids = {str(m["motif_id"]) for m in motifs}
    q_ids = {str(q["question_id"]) for q in questions}
    frag_ids = {str(f["fragment_id"]) for f in fragments}

    frag_mats: set[str] = set()
    direct_frag_motifs: set[str] = set()
    for f in fragments:
        frag_mats.update(str(mid) for mid in (f.get("material_ids") or []))  # type: ignore[union-attr]
        direct_frag_motifs.update(str(mid) for mid in (f.get("motif_ids") or []))  # type: ignore[union-attr]

    q_mats: set[str] = set()
    for q in questions:
        q_mats.update(str(mid) for mid in (q.get("material_ids") or []))  # type: ignore[union-attr]

    rel_mats: set[str] = set()
    rel_qs: set[str] = set()
    frag_in: set[str] = set()
    frag_out: set[str] = set()
    for rel in relations:
        left = rel.get("left") or {}
        right = rel.get("right") or {}
        lt, lid = str(left.get("type", "")), str(left.get("id", ""))  # type: ignore[union-attr]
        rt, rid = str(right.get("type", "")), str(right.get("id", ""))  # type: ignore[union-attr]
        if lt == "material":
            rel_mats.add(lid)
        if rt == "material":
            rel_mats.add(rid)
        if lt == "question":
            rel_qs.add(lid)
        if rt == "question":
            rel_qs.add(rid)
        if lt == "fragment":
            frag_out.add(lid)
        if rt == "fragment":
            frag_in.add(rid)

    producing = sum(1 for s in sessions if s.get("produced_fragment_ids"))
    total_mats = len(mat_ids)
    digested_mats = len(frag_mats & mat_ids)
    return {
        "material_count": total_mats,
        "motif_count": len(motif_ids),
        "question_count": len(q_ids),
        "fragment_count": len(frag_ids),
        "relation_count": len(relations),
        "session_count": len(sessions),
        "producing_sessions": producing,
        "zero_fragment_sessions": len(sessions) - producing,
        "materials_in_fragments": digested_mats,
        "materials_in_fragments_pct": round(digested_mats * 100.0 / total_mats, 1) if total_mats else 0.0,
        "materials_in_questions": len(q_mats & mat_ids),
        "untouched_materials": len(mat_ids - frag_mats - q_mats),
        "isolated_material_ids": sorted(mat_ids - rel_mats),
        "direct_fragment_motifs": len(direct_frag_motifs & motif_ids),
        "unfragmented_motif_ids": sorted(motif_ids - direct_frag_motifs),
        "isolated_question_ids": sorted(q_ids - rel_qs),
        "incoming_zero_fragment_ids": sorted(frag_ids - frag_in),
        "outgoing_zero_fragment_ids": sorted(frag_ids - frag_out),
    }


def read_readings_list() -> list[dict[str, str]]:
    if not READINGS_DIR.is_dir():
        return []
    notes: list[dict[str, str]] = []
    for md_path in sorted(READINGS_DIR.glob("*.md"), reverse=True):
        content = md_path.read_text(encoding="utf-8")
        title = md_path.stem
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        notes.append(
            {
                "filename": md_path.name,
                "title": title,
                "content": content,
            }
        )
    return notes


_DERIVED_LOCK = threading.Lock()
_DERIVED_CACHE: tuple[str, dict[str, object], bytes] | None = None


def _readings_signature(readings_dir: Path) -> list[tuple[str, int, int]]:
    sig: list[tuple[str, int, int]] = []
    if readings_dir.is_dir():
        for path in sorted(readings_dir.glob("*.md")):
            try:
                st = path.stat()
                sig.append((path.name, st.st_size, st.st_mtime_ns))
            except OSError:
                continue
    return sig


def _load_raw_collections() -> tuple[dict[str, object], str, Path]:
    errors: list[str] = []
    payload: dict[str, object] = {}
    for name, (filename, id_key, _) in COLLECTIONS.items():
        records = load_jsonl(ROOT / "state" / filename, id_key, errors)
        payload[name] = list(records.values())
    if errors:
        raise RuntimeError("; ".join(errors))

    readings_dir = ROOT / "readings"
    digest_input = json.dumps(
        {
            "root": str(ROOT),
            "collections": payload,
            "readings_sig": _readings_signature(readings_dir),
        },
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    cache_key = hashlib.sha256(digest_input).hexdigest()
    return payload, cache_key, readings_dir


def _ensure_derived(
    payload: dict[str, object], cache_key: str, readings_dir: Path
) -> tuple[dict[str, object], bytes]:
    global _DERIVED_CACHE
    with _DERIVED_LOCK:
        if _DERIVED_CACHE is not None and _DERIVED_CACHE[0] == cache_key:
            # Serve the identical payload object for unchanged ledger content
            # (the handler only serialises it; callers must not mutate it).
            return _DERIVED_CACHE[1], _DERIVED_CACHE[2]

        fragments = payload["fragments"]  # type: ignore[assignment]
        relations = payload["relations"]  # type: ignore[assignment]
        readings_docs = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted(readings_dir.glob("*.md"))
        ]
        derived: dict[str, object] = {}
        derived["voice_audit"] = compute_voice_audit(fragments, relations, top=16, gram=6)  # type: ignore[arg-type]
        pa = measure_passion_audit(fragments)  # type: ignore[arg-type]
        pa["group_order"] = list(PASSION_GROUPS.keys())
        derived["passion_audit"] = pa
        derived["eros_audit"] = measure_eros_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["currency_audit"] = measure_currency_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["signature_audit"] = measure_signature_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["prayer_audit"] = measure_prayer_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["abjection_audit"] = measure_abjection_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["war_audit"] = measure_war_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["secrecy_audit"] = measure_secrecy_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["sky_audit"] = measure_sky_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["vegetal_audit"] = measure_vegetal_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        derived["secret_audit"] = measure_secret_audit(fragments)  # type: ignore[arg-type]
        derived["boredom_audit"] = measure_boredom_audit(fragments, payload["materials"], readings_docs)  # type: ignore[arg-type]
        payload.update(derived)
        derived["metabolism_audit"] = compute_metabolism_snapshot(payload)
        derived["readings"] = [
            {
                "filename": name,
                "title": next(
                    (line[2:].strip() for line in content.splitlines() if line.startswith("# ")),
                    name,
                ),
                "content": content,
            }
            for name, content in readings_docs
        ]
        payload["metabolism_audit"] = derived["metabolism_audit"]
        payload["readings"] = derived["readings"]
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        _DERIVED_CACHE = (cache_key, payload, encoded)
        return payload, encoded


def _read_archive_payload_once() -> dict[str, object]:
    payload, cache_key, readings_dir = _load_raw_collections()
    full_payload, _encoded = _ensure_derived(payload, cache_key, readings_dir)
    return full_payload


def read_archive_payload(retries: int = 6, delay: float = 0.02) -> dict[str, object]:
    """Serve one consistent snapshot, retrying while a writer keeps replacing files.

    ``load_jsonl`` already retries a fixed number of times inside
    ``ledger_io.read_snapshot``.  As the archive grows, one read takes longer and
    a writer that replaces a base ledger every few milliseconds can exhaust that
    budget (observed in tests/test_server.py at 815 materials).  Retrying the
    whole payload here keeps the viewer's promise of a 200-or-JSON-error answer
    without weakening the snapshot check: the retry only waits for the writer to
    finish, and a persistent failure still surfaces as LedgerBusy.
    """
    last: ledger_io.LedgerBusy | None = None
    for attempt in range(retries + 1):
        try:
            return _read_archive_payload_once()
        except ledger_io.LedgerBusy as exc:
            last = exc
            if attempt >= retries:
                break
            time.sleep(delay)
    assert last is not None
    raise last


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class ArchiveRequestHandler(BaseHTTPRequestHandler):
    def send_cors_and_embed_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/packet":
            qs = parse_qs(parsed.query)
            qid = (qs.get("question_id") or ["auto"])[0]
            try:
                packet_text = build_context_packet(load_all(), qid)
                body = json.dumps({"question_id": qid, "packet": packet_text}, ensure_ascii=False).encode("utf-8")
            except Exception as exc:
                err_body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_body)))
                self.send_cors_and_embed_headers()
                self.end_headers()
                self.wfile.write(err_body)
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_and_embed_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if route in ("/api/state", "/data.json"):
            try:
                body = json.dumps(read_archive_payload(), ensure_ascii=False).encode("utf-8")
            except Exception as exc:
                err_body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_body)))
                self.send_cors_and_embed_headers()
                self.end_headers()
                self.wfile.write(err_body)
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_and_embed_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        rel = "index.html" if route in ("", "/") else route.lstrip("/")
        candidate = (VIEWER_DIR / rel).resolve()
        if not str(candidate).startswith(str(VIEWER_DIR.resolve())) or not candidate.is_file():
            not_found = b"Not Found"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(not_found)))
            self.send_cors_and_embed_headers()
            self.end_headers()
            self.wfile.write(not_found)
            return

        content = candidate.read_bytes()
        ctype, _ = mimetypes.guess_type(str(candidate))
        if not ctype:
            ctype = "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype = f"{ctype}; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.send_cors_and_embed_headers()
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[viewer] {self.address_string()} - {fmt % args}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="TCP port (default: 8000)")
    args = parser.parse_args()

    server = ReusableThreadingHTTPServer((args.host, args.port), ArchiveRequestHandler)
    print(f"Serving AIselfMySelf archive viewer at http://{args.host}:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
