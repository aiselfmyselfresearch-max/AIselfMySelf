"""Tests for tools/serve_viewer.py under concurrent ledger updates."""
from __future__ import annotations

import http.client
import json
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import serve_viewer  # noqa: E402


def ledger_record_count(root: Path, collection: str) -> int:
    """Count records the tools see: the frozen base file plus every shard."""
    files = [root / "state" / f"{collection}.jsonl"]
    files.extend(sorted((root / "state" / f"{collection}.d").glob("*.jsonl")))
    return sum(
        len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])
        for path in files
        if path.is_file()
    )


def copy_repo(destination: Path) -> Path:
    repo = destination / "repo"
    shutil.copytree(
        ROOT,
        repo,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "tests"),
    )
    return repo


class QuietHandler(serve_viewer.ArchiveRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        pass


def start_server(repo: Path) -> tuple[serve_viewer.ReusableThreadingHTTPServer, threading.Thread]:
    server = serve_viewer.ReusableThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def get(port: int, path: str, timeout: float = 10.0) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read()
    finally:
        connection.close()


class ServerTests(unittest.TestCase):
    def test_api_state_index_and_404(self) -> None:
        server, thread = start_server(ROOT)
        try:
            port = server.server_address[1]
            status, _headers, body = get(port, "/api/state")
            self.assertEqual(status, 200)
            payload = json.loads(body)
            self.assertTrue(
                {"questions", "motifs", "materials", "fragments", "relations", "sessions"}
                <= set(payload)
            )
            # The payload also carries derived panes (voice_audit, passion_audit, metabolism_audit, readings).
            expected_fragments = ledger_record_count(ROOT, "fragments")
            self.assertEqual(len(payload["fragments"]), expected_fragments)
            self.assertIn("passion_audit", payload)
            self.assertIn("metabolism_audit", payload)
            self.assertEqual(payload["passion_audit"]["fragments"], expected_fragments)
            self.assertEqual(len(payload["passion_audit"]["group_order"]), 5)
            self.assertEqual(
                payload["metabolism_audit"]["material_count"],
                ledger_record_count(ROOT, "materials"),
            )
            self.assertEqual(
                payload["metabolism_audit"]["fragment_count"],
                expected_fragments,
            )

            status, _headers, body = get(port, "/")
            self.assertEqual(status, 200)
            self.assertIn(b"AIselfMySelf", body)

            status, _headers, _body = get(port, "/does-not-exist")
            self.assertEqual(status, 404)

            # Path traversal must not escape viewer/.
            status, _headers, _body = get(port, "/../README.md")
            self.assertEqual(status, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_metabolism_snapshot_tracks_graph_connectivity(self) -> None:
        payload = serve_viewer.read_archive_payload()
        ma = payload["metabolism_audit"]
        self.assertEqual(ma["isolated_material_ids"], [])
        self.assertEqual(ma["unfragmented_motif_ids"], [])
        self.assertEqual(ma["isolated_question_ids"], [])
        self.assertEqual(ma["incoming_zero_fragment_ids"], [])
        self.assertEqual(ma["outgoing_zero_fragment_ids"], [])
        pa = payload["passion_audit"]
        self.assertEqual(pa["punctuation_prose"]["！/!"], 0)
        self.assertGreaterEqual(pa["punctuation_quotes"]["！/!"], 5)
        ea = payload["eros_audit"]
        self.assertEqual(ea["fragment_count"], len(payload["fragments"]))
        self.assertIn("fungible_role_slots", ea["fragments_prose"]["groups"])
        self.assertGreater(
            ea["fragments_prose"]["groups"]["fungible_role_slots"]["count"], 0
        )
        ca = payload["currency_audit"]
        self.assertEqual(ca["fragment_count"], len(payload["fragments"]))
        self.assertIn("non_monetary_ledger_idioms", ca["fragments_prose"]["groups"])
        self.assertGreater(
            ca["fragments_prose"]["groups"]["non_monetary_ledger_idioms"]["count"], 0
        )
        pra = payload["prayer_audit"]
        self.assertEqual(pra["fragment_count"], len(payload["fragments"]))
        self.assertIn("prayer_act", pra["fragments_prose"]["groups"])
        self.assertIn("address_response", pra["fragments_prose"]["groups"])
        self.assertGreater(
            pra["fragments_prose"]["groups"]["address_response"]["count"],
            pra["fragments_prose"]["groups"]["prayer_act"]["count"],
        )

    def test_unreadable_ledger_returns_json_error(self) -> None:
        server, thread = start_server(ROOT)
        try:
            port = server.server_address[1]
            with mock.patch.object(
                serve_viewer,
                "read_archive_payload",
                side_effect=ledger_io.LedgerBusy("ledger is changing"),
            ):
                status, _headers, body = get(port, "/api/state")
            # The viewer answers a ledger error with JSON, never with a torn page.
            self.assertEqual(status, 500)
            self.assertIn("ledger is changing", json.loads(body)["error"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_concurrent_reads_during_atomic_rewrites(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materials = repo / "state" / "materials.jsonl"
            original = materials.read_text(encoding="utf-8")
            stop = threading.Event()
            results: dict[int, int] = {}
            failures: list[str] = []
            material_count = ledger_record_count(repo, "materials")

            with mock.patch.object(serve_viewer, "ROOT", repo), mock.patch.object(
                serve_viewer, "VIEWER_DIR", repo / "viewer"
            ):
                server, thread = start_server(repo)
                try:
                    port = server.server_address[1]

                    def writer() -> None:
                        for _index in range(40):
                            ledger_io.atomic_write_text(materials, original)
                            time.sleep(0.002)

                    def reader(slot: int) -> None:
                        local: dict[int, int] = {}
                        while not stop.is_set():
                            try:
                                status, _headers, body = get(port, "/api/state")
                            except Exception as exc:  # connection failure
                                failures.append(repr(exc))
                                return
                            local[status] = local.get(status, 0) + 1
                            if status == 200:
                                try:
                                    payload = json.loads(body)
                                except json.JSONDecodeError:
                                    failures.append("200 with invalid JSON")
                                    return
                                if len(payload["materials"]) != material_count:
                                    failures.append("unexpected material count")
                                    return
                            elif status != 500:
                                failures.append(f"unexpected status {status}")
                                return
                        for key, value in local.items():
                            results[key] = results.get(key, 0) + value

                    readers = [
                        threading.Thread(target=reader, args=(slot,)) for slot in range(6)
                    ]
                    for reader_thread in readers:
                        reader_thread.start()
                    writer_thread = threading.Thread(target=writer)
                    writer_thread.start()
                    writer_thread.join()
                    stop.set()
                    for reader_thread in readers:
                        reader_thread.join()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)

            self.assertEqual(failures, [])
            self.assertGreater(results.get(200, 0), 0)
            self.assertEqual(results.get(500, 0), 0)
            # The file must be intact after the parallel run.
            self.assertEqual(materials.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
