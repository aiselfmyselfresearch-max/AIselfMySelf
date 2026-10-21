#!/usr/bin/env python3
"""Serve the interactive AIselfMySelf archive viewer over HTTP (stdlib only).

Reads state/*.jsonl dynamically on every /api/state request so ledger updates
appear immediately on page refresh. Binds to 0.0.0.0 by default for browser
preview compatibility.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from validate_seed import COLLECTIONS, ROOT, load_jsonl

VIEWER_DIR = ROOT / "viewer"


def read_archive_payload() -> dict[str, list[dict]]:
    errors: list[str] = []
    payload: dict[str, list[dict]] = {}
    for name, (filename, id_key, _) in COLLECTIONS.items():
        records = load_jsonl(ROOT / "state" / filename, id_key, errors)
        payload[name] = list(records.values())
    if errors:
        raise RuntimeError("; ".join(errors))
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
