#!/usr/bin/env python3
"""Serve the interactive AIselfMySelf archive viewer over HTTP (stdlib only).

Reads state/*.jsonl, tools/voice_audit.py metrics, and readings/*.md dynamically
on every /api/state request so updates appear immediately on page refresh.
Binds to 0.0.0.0 by default for browser preview compatibility.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from inspect_inquiry import build_context_packet, load_all
import ledger_io
from validate_seed import COLLECTIONS, ROOT, load_jsonl
from voice_audit import compute_voice_audit

VIEWER_DIR = ROOT / "viewer"
READINGS_DIR = ROOT / "readings"


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


def read_archive_payload(retries: int = 8, delay: float = 0.02) -> dict[str, object]:
    # A writer may replace a ledger between one collection's read and the next.
    # Retry the whole payload so a browser refresh during an edit sees one
    # consistent snapshot instead of a 500.
    for attempt in range(retries + 1):
        errors: list[str] = []
        payload: dict[str, object] = {}
        try:
            for name, (filename, id_key, _) in COLLECTIONS.items():
                records = load_jsonl(ROOT / "state" / filename, id_key, errors)
                payload[name] = list(records.values())
        except ledger_io.LedgerBusy:
            if attempt >= retries:
                raise
            time.sleep(delay)
            continue
        if errors:
            raise RuntimeError("; ".join(errors))
        break
    fragments = payload["fragments"]  # type: ignore[assignment]
    relations = payload["relations"]  # type: ignore[assignment]
    payload["voice_audit"] = compute_voice_audit(fragments, relations, top=16, gram=6)  # type: ignore[arg-type]
    payload["readings"] = read_readings_list()
    return payload


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
