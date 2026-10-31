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
            self.assertIn("vegetal_audit", payload)
            self.assertIn("metabolism_audit", payload)
            self.assertEqual(payload["passion_audit"]["fragments"], expected_fragments)
            self.assertEqual(payload["vegetal_audit"]["fragment_count"], expected_fragments)
            self.assertEqual(len(payload["vegetal_audit"]["group_order"]), 7)
            self.assertIn("fungi_audit", payload)
            self.assertEqual(payload["fungi_audit"]["fragment_count"], expected_fragments)
            self.assertEqual(len(payload["fungi_audit"]["group_order"]), 7)
            self.assertIn("ghost_audit", payload)
            self.assertIn("genealogy_audit", payload)
            self.assertEqual(len(payload["genealogy_audit"]["group_order"]), 7)
            self.assertEqual(payload["ghost_audit"]["fragment_count"], expected_fragments)
            self.assertEqual(len(payload["ghost_audit"]["group_order"]), 7)
            self.assertEqual(len(payload["passion_audit"]["group_order"]), 5)
            self.assertEqual(
                payload["metabolism_audit"]["material_count"],
                ledger_record_count(ROOT, "materials"),
            )
            self.assertEqual(
                payload["metabolism_audit"]["fragment_count"],
                expected_fragments,
            )
            # Lightweight /api/state contract: read_log rows and full reading bodies are stripped.
            self.assertNotIn("read_log", payload)
            self.assertIn("read_log_summary", payload)
            self.assertGreater(payload["read_log_summary"]["total_rows"], 0)
            self.assertTrue(payload["readings"])
            first_note_meta = payload["readings"][0]
            self.assertNotIn("content", first_note_meta)
            self.assertGreater(first_note_meta["chars"], 0)

            # On-demand reading note endpoint + traversal protection.
            status, _headers, note_body = get(port, f"/api/readings/{first_note_meta['filename']}")
            self.assertEqual(status, 200)
            note_doc = json.loads(note_body)
            self.assertEqual(note_doc["filename"], first_note_meta["filename"])
            self.assertEqual(len(note_doc["content"]), first_note_meta["chars"])

            status, _headers, _body = get(port, "/api/readings/does-not-exist.md")
            self.assertEqual(status, 404)
            status, _headers, _body = get(port, "/api/readings/../README.md")
            self.assertEqual(status, 404)
            status, _headers, _body = get(port, "/api/readings/%2e%2e%2fREADME.md")
            self.assertEqual(status, 404)

            # Warm cache serves pre-encoded UTF-8 bytes without re-serialising via json.dumps.
            with mock.patch.object(serve_viewer.json, "dumps", side_effect=AssertionError("should use cached bytes")):
                status, _headers, cached_body = get(port, "/api/state")
            self.assertEqual(status, 200)
            self.assertEqual(cached_body, body)

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
        # Integration checks reflect the current data, not a desired graph shape.
        # Algorithmic edge cases are tested with fixtures below and in test_metabolism_audit.
        rel_nodes = {"material": set(), "question": set()}
        frag_in, frag_out = set(), set()
        for relation in payload["relations"]:
            for side in ("left", "right"):
                node = relation[side]
                if node["type"] in rel_nodes:
                    rel_nodes[node["type"]].add(node["id"])
            if relation["left"]["type"] == "fragment":
                frag_out.add(relation["left"]["id"])
            if relation["right"]["type"] == "fragment":
                frag_in.add(relation["right"]["id"])
        frag_ids = {f["fragment_id"] for f in payload["fragments"]}
        motif_ids = {m["motif_id"] for m in payload["motifs"]}
        used_motifs = {mid for f in payload["fragments"] for mid in f["motif_ids"]}
        self.assertEqual(ma["isolated_material_ids"], sorted(
            {m["material_id"] for m in payload["materials"]} - rel_nodes["material"]
        ))
        self.assertEqual(ma["isolated_question_ids"], sorted(
            {q["question_id"] for q in payload["questions"]} - rel_nodes["question"]
        ))
        self.assertEqual(ma["unfragmented_motif_ids"], sorted(motif_ids - used_motifs))
        self.assertEqual(ma["incoming_zero_fragment_ids"], sorted(frag_ids - frag_in))
        self.assertEqual(ma["outgoing_zero_fragment_ids"], sorted(frag_ids - frag_out))
        pa = payload["passion_audit"]
        expected = serve_viewer.measure_passion_audit(payload["fragments"])
        self.assertEqual(pa["punctuation_prose"], expected["punctuation_prose"])
        self.assertEqual(pa["punctuation_quotes"], expected["punctuation_quotes"])
        ea = payload["eros_audit"]
        self.assertEqual(ea["fragment_count"], len(payload["fragments"]))
        self.assertIn("fungible_role_slots", ea["fragments_prose"]["groups"])
        ca = payload["currency_audit"]
        self.assertEqual(ca["fragment_count"], len(payload["fragments"]))
        self.assertIn("non_monetary_ledger_idioms", ca["fragments_prose"]["groups"])
        sa = payload["signature_audit"]
        self.assertEqual(sa["fragment_count"], len(payload["fragments"]))
        self.assertIn("signature_mark", sa["fragments_prose"]["groups"])
        sea = payload["secret_audit"]
        self.assertEqual(sea["fragment_count"], len(payload["fragments"]))
        self.assertIn("秘密と隠匿", sea["group_sums"])
        self.assertIn("嘘と偽り", sea["group_sums"])
        self.assertIn("暗号と鍵", sea["group_sums"])
        self.assertEqual(
            sum(sea["group_sums"].values()),
            sum(sum(counts.values()) for counts in sea["group_totals"].values()),
        )
        pra = payload["prayer_audit"]
        self.assertEqual(pra["fragment_count"], len(payload["fragments"]))
        self.assertIn("prayer_act", pra["fragments_prose"]["groups"])
        self.assertIn("address_response", pra["fragments_prose"]["groups"])
        bta = payload["botany_audit"]
        self.assertEqual(bta["fragment_count"], len(payload["fragments"]))
        self.assertIn("flora_organ", bta["fragments_prose"]["groups"])
        self.assertIn("scribal_absorption", bta["fragments_prose"]["groups"])

    def test_api_reports_isolation_and_exclamation_instead_of_rejecting_them(self) -> None:
        """A valid new voice must not need artificial edges or punctuation edits."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            fragment_id = "FRAG-TEST-ISOLATED"
            fragment = {
                "fragment_id": fragment_id,
                "created_at": "2026-10-28",
                "language": "ja",
                "form": "fragment",
                "title": "Test fixture",
                "text": "台帳を読み直した！",
                "narrator_mode": "reflective_literary_voice",
                "question_ids": [],
                "motif_ids": [],
                "material_ids": [],
                "status": "draft",
            }
            shard = repo / "state" / "fragments.d" / "2026-10-28-test.jsonl"
            shard.write_text(json.dumps(fragment, ensure_ascii=False) + "\n", encoding="utf-8")
            with mock.patch.object(serve_viewer, "ROOT", repo), mock.patch.object(
                serve_viewer, "VIEWER_DIR", repo / "viewer"
            ):
                server, thread = start_server(repo)
                try:
                    status, _headers, body = get(server.server_address[1], "/api/state")
                    self.assertEqual(status, 200)
                    payload = json.loads(body)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)
            self.assertIn(fragment_id, payload["metabolism_audit"]["incoming_zero_fragment_ids"])
            self.assertIn(fragment_id, payload["metabolism_audit"]["outgoing_zero_fragment_ids"])
            self.assertIn(fragment, payload["fragments"])
            self.assertGreaterEqual(payload["passion_audit"]["punctuation_prose"]["！/!"], 1)

    def test_concurrent_state_requests_share_one_rebuild(self) -> None:
        """Four simultaneous readers must not each rebuild the derived panes."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            calls: list[int] = []
            real_build = serve_viewer._read_payload_with_retries

            def slow_build(*args: object, **kwargs: object) -> dict[str, object]:
                calls.append(1)
                time.sleep(2.0)
                return real_build(*args, **kwargs)  # type: ignore[arg-type]

            with mock.patch.object(serve_viewer, "ROOT", repo), mock.patch.object(
                serve_viewer, "VIEWER_DIR", repo / "viewer"
            ), mock.patch.object(
                serve_viewer, "_read_payload_with_retries", side_effect=slow_build
            ):
                server, thread = start_server(repo)
                try:
                    port = server.server_address[1]
                    statuses: list[int] = []

                    def hit() -> None:
                        status, _headers, _body = get(port, "/api/state", timeout=30.0)
                        statuses.append(status)

                    readers = [threading.Thread(target=hit) for _ in range(4)]
                    for reader_thread in readers:
                        reader_thread.start()
                    for reader_thread in readers:
                        reader_thread.join()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)

            self.assertEqual(statuses, [200, 200, 200, 200])
            self.assertEqual(len(calls), 1)

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

    def test_payload_cache_follows_ledger_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            materials = repo / "state" / "materials.jsonl"
            with mock.patch.object(serve_viewer, "ROOT", repo), mock.patch.object(
                serve_viewer, "VIEWER_DIR", repo / "viewer"
            ):
                first = serve_viewer._read_archive_payload_once()
                again = serve_viewer._read_archive_payload_once()
                self.assertIs(first, again)  # unchanged content is served from cache
                count = len(first["materials"])
                extra = dict(first["materials"][0])
                extra["material_id"] = "MAT-CACHE-TEST"
                with open(materials, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(extra, ensure_ascii=False) + "\n")
                third = serve_viewer._read_archive_payload_once()
            self.assertEqual(len(third["materials"]), count + 1)
            self.assertIsNot(third, first)

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
