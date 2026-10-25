#!/usr/bin/env python3
"""Serve the interactive AIselfMySelf archive viewer over HTTP (stdlib only).

Reads state/*.jsonl, the mirror audits in tools/, and readings/*.md, and rebuilds
the payload whenever the ledger content changes (a content hash of every base and
shard file; see ``state_signature``).  Updates still appear on page refresh, but an
unchanged ledger is served from the in-process cache.
Binds to 0.0.0.0 by default for browser preview compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import ledger_io
from abjection_audit import measure_abjection_audit
from war_audit import measure_war_audit
from secret_audit import measure as measure_secret_audit
from secrecy_audit import measure_secrecy_audit
from sky_audit import measure_sky_audit
from boredom_audit import measure_boredom_audit
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


# 精読報告の全走査は 3MB を超え、リクエストごとにやり直すと台帳の再読に
# 並ぶ費用になる。ディレクトリの署名（名前・大きさ・mtime）が変わったときだけ
# 読み直し、本文と鏡の「精読報告」層を一度だけ作って共有する。
_READINGS_MEMO: dict[tuple[tuple[str, int, int], ...], dict[str, object]] = {}


def readings_signature() -> tuple[tuple[str, int, int], ...]:
    if not READINGS_DIR.is_dir():
        return ()
    signature: list[tuple[str, int, int]] = []
    for md_path in sorted(READINGS_DIR.glob("*.md")):
        stat = md_path.stat()
        signature.append((md_path.name, stat.st_size, stat.st_mtime_ns))
    return tuple(signature)


def readings_memo() -> dict[str, object]:
    """Return the cached readings docs, UI list, and per-mirror aggregate layers."""
    signature = readings_signature()
    cached = _READINGS_MEMO.get(signature)
    if cached is not None:
        return cached
    docs: list[tuple[str, str]] = []
    notes: list[dict[str, str]] = []
    if READINGS_DIR.is_dir():
        for md_path in sorted(READINGS_DIR.glob("*.md")):
            content = md_path.read_text(encoding="utf-8")
            docs.append((md_path.name, content))
    for name, content in sorted(docs, key=lambda item: item[0], reverse=True):
        title = name.rsplit(".", 1)[0]
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        notes.append({"filename": name, "title": title, "content": content})
    aggregate = {
        "sky": measure_sky_audit([], [], docs)["readings"],
        "boredom": measure_boredom_audit([], [], docs)["readings"],
    }
    entry = {"docs": docs, "notes": notes, "aggregate": aggregate}
    _READINGS_MEMO.clear()
    _READINGS_MEMO[signature] = entry
    return entry


def read_readings_list() -> list[dict[str, str]]:
    return readings_memo()["notes"]  # type: ignore[return-value]


_PAYLOAD_CACHE: dict[str, dict[str, object]] = {}


def state_signature() -> str:
    """Content hash of every ledger file (base + shards) under ``ROOT/state``.

    The viewer rebuilds a ~15MB payload from ~2,200 materials and eleven mirrors
    on every request; under several concurrent readers that rebuild is the bulk
    of the latency.  Keying the cache on file *content* rather than mtime means
    a writer that replaces a ledger with identical bytes does not force a
    rebuild, while any real change still invalidates it.
    """
    digest = hashlib.blake2b(digest_size=16)
    state_dir = ROOT / "state"
    digest.update(str(state_dir).encode("utf-8"))
    paths = sorted(state_dir.glob("*.jsonl")) + sorted(state_dir.glob("*.d/*.jsonl"))
    for path in paths:
        try:
            data = path.read_bytes()
        except OSError:
            continue
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest()


def _read_archive_payload_once() -> dict[str, object]:
    signature = state_signature()
    cached = _PAYLOAD_CACHE.get(signature)
    if cached is not None:
        # The payload is treated as immutable after construction: the request
        # handler only serialises it.  Callers must not mutate the returned dict.
        return cached
    payload = _build_archive_payload()
    _PAYLOAD_CACHE.clear()
    _PAYLOAD_CACHE[signature] = payload
    return payload


def _build_archive_payload() -> dict[str, object]:
    errors: list[str] = []
    payload: dict[str, object] = {}
    for name, (filename, id_key, _) in COLLECTIONS.items():
        records = load_jsonl(ROOT / "state" / filename, id_key, errors)
        payload[name] = list(records.values())
    if errors:
        raise RuntimeError("; ".join(errors))
    fragments = payload["fragments"]  # type: ignore[assignment]
    relations = payload["relations"]  # type: ignore[assignment]
    payload["voice_audit"] = compute_voice_audit(fragments, relations, top=16, gram=6)  # type: ignore[arg-type]
    pa = measure_passion_audit(fragments)  # type: ignore[arg-type]
    pa["group_order"] = list(PASSION_GROUPS.keys())
    payload["passion_audit"] = pa
    payload["eros_audit"] = measure_eros_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["currency_audit"] = measure_currency_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["signature_audit"] = measure_signature_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["prayer_audit"] = measure_prayer_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["abjection_audit"] = measure_abjection_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["war_audit"] = measure_war_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    payload["secret_audit"] = measure_secret_audit(fragments)  # type: ignore[arg-type]
    payload["secrecy_audit"] = measure_secrecy_audit(fragments, payload["materials"])  # type: ignore[arg-type]
    # 精読報告の層はディレクトリ署名でメモ化する（readings_memo）。
    # 断片と素材の層だけを毎回数え、報告層はキャッシュした集計を差し込む。
    memo = readings_memo()
    aggregate = memo["aggregate"]  # type: ignore[index]
    sky_report = measure_sky_audit(fragments, payload["materials"], [])  # type: ignore[arg-type]
    sky_report["readings"] = aggregate["sky"]  # type: ignore[index]
    payload["sky_audit"] = sky_report
    boredom_report = measure_boredom_audit(  # type: ignore[arg-type]
        fragments, payload["materials"], []
    )
    boredom_report["readings"] = aggregate["boredom"]  # type: ignore[index]
    payload["boredom_audit"] = boredom_report
    payload["metabolism_audit"] = compute_metabolism_snapshot(payload)
    payload["readings"] = read_readings_list()
    return payload


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
