#!/usr/bin/env python3
"""Serve the interactive AIselfMySelf archive viewer over HTTP (stdlib only).

Reads state/*.jsonl (frozen base files plus any session shards) dynamically on
every /api/state request so ledger updates appear immediately on page refresh.
Reads go through ledger_io's stable snapshot so a concurrent writer cannot turn
a request into a torn JSON parse; if the ledger never settles the server answers
503 with Retry-After instead of 500.  Binds to 0.0.0.0 by default for browser
preview compatibility.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

import ledger_io
from validate_seed import COLLECTIONS, ROOT

VIEWER_DIR = ROOT / "viewer"


def read_archive_payload() -> dict[str, list[dict[str, Any]]]:
    """Return all six ledgers as lists, read as one stable union snapshot."""
    specs = {
        name: (ROOT / "state" / filename, id_key)
        for name, (filename, id_key, _schema) in COLLECTIONS.items()
    }
    payload, errors = ledger_io.load_collections(specs, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return {name: list(records.values()) for name, records in payload.items()}


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 64


class ArchiveRequestHandler(BaseHTTPRequestHandler):
    server_version = "AIselfMySelfViewer/1.1"
    # Do not let a slow or idle client keep a worker thread forever.
    timeout = 30

    def send_common_headers(self, extra_headers: dict[str, str] | None = None) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)

    def send_body(
        self,
        status: int,
        body: bytes,
        content_type: str,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_common_headers(extra_headers)
        self.end_headers()
        self.wfile.write(body)

    def send_json(
        self,
        status: int,
        payload: Any,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_body(status, body, "application/json; charset=utf-8", extra_headers)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route in ("/api/state", "/data.json"):
            try:
                payload = read_archive_payload()
            except ledger_io.LedgerBusy as exc:
                # The ledger is being rewritten; the client may retry shortly.
                self.send_json(
                    503,
                    {"error": str(exc), "retryable": True},
                    {"Retry-After": "1"},
                )
                return
            except Exception as exc:  # malformed ledger or unexpected failure
                self.send_json(500, {"error": str(exc)})
                return
            self.send_json(200, payload)
            return

        rel = "index.html" if route in ("", "/") else route.lstrip("/")
        try:
            candidate = (VIEWER_DIR / rel).resolve()
            candidate.relative_to(VIEWER_DIR.resolve())
        except (OSError, ValueError):
            candidate = None
        if candidate is None or not candidate.is_file():
            self.send_body(404, b"Not Found", "text/plain; charset=utf-8")
            return

        content = candidate.read_bytes()
        ctype, _ = mimetypes.guess_type(str(candidate))
        if not ctype:
            ctype = "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype = f"{ctype}; charset=utf-8"
        self.send_body(200, content, ctype)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[viewer] {self.address_string()} - {fmt % args}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="TCP port (default: 8000)")
    args = parser.parse_args()

    # Initialise the mimetype table once, before request threads can race on it.
    mimetypes.init()

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
