"""Tests for the concurrency-safe ledger I/O layer (stdlib unittest only)."""
from __future__ import annotations

import json
import os
import stat
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


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


class UnionLoadTests(unittest.TestCase):
    def test_base_and_shards_are_read_in_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "state" / "fragments.jsonl"
            write_jsonl(base, [{"fragment_id": "FRAG-001"}, {"fragment_id": "FRAG-002"}])
            write_jsonl(
                base.with_name("fragments.d") / "2026-10-21-bbbbbbbbbbbb.jsonl",
                [{"fragment_id": "FRAG-004"}],
            )
            write_jsonl(
                base.with_name("fragments.d") / "2026-10-21-aaaaaaaaaaaa.jsonl",
                [{"fragment_id": "FRAG-003"}],
            )

            data, errors = ledger_io.load_collections(
                {"fragments": (base, "fragment_id")}, root=root
            )

            self.assertEqual(errors, [])
            self.assertEqual(
                list(data["fragments"]),
                ["FRAG-001", "FRAG-002", "FRAG-003", "FRAG-004"],
            )

    def test_duplicate_across_shards_is_reported_with_both_locations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "state" / "fragments.jsonl"
            write_jsonl(base, [{"fragment_id": "FRAG-001"}])
            shard = base.with_name("fragments.d") / "2026-10-21-aaaaaaaaaaaa.jsonl"
            write_jsonl(shard, [{"fragment_id": "FRAG-001"}])

            data, errors = ledger_io.load_collections(
                {"fragments": (base, "fragment_id")}, root=root
            )

            self.assertEqual(list(data["fragments"]), ["FRAG-001"])
            self.assertEqual(len(errors), 1)
            self.assertIn("duplicate fragment_id FRAG-001", errors[0])
            self.assertIn("first defined at state/fragments.jsonl:1", errors[0])

    def test_missing_base_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "state" / "fragments.jsonl"
            data, errors = ledger_io.load_collections(
                {"fragments": (base, "fragment_id")}, root=root
            )
            self.assertEqual(data["fragments"], {})
            self.assertIn("state/fragments.jsonl: ledger file is missing", errors)

    def test_paths_outside_root_do_not_crash_labelling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "fragments.jsonl"
            write_jsonl(base, [])
            _data, errors = ledger_io.load_collections(
                {"fragments": (base, "fragment_id")}, root=ROOT
            )
            self.assertEqual(errors, [])
            missing = Path(tmp) / "missing.jsonl"
            _data, errors = ledger_io.load_collections(
                {"fragments": (missing, "fragment_id")}, root=ROOT
            )
            self.assertIn(str(missing), errors[0])

    def test_partial_last_line_is_retried_until_writer_completes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "state" / "fragments.jsonl"
            base.parent.mkdir(parents=True, exist_ok=True)
            complete = (
                json.dumps({"fragment_id": "FRAG-001"}, ensure_ascii=False) + "\n"
                + json.dumps({"fragment_id": "FRAG-002"}, ensure_ascii=False) + "\n"
            )
            partial = complete[: len(complete) - 12]
            base.write_text(partial, encoding="utf-8")

            def finish() -> None:
                time.sleep(0.08)
                ledger_io.atomic_write_text(base, complete)

            thread = threading.Thread(target=finish)
            thread.start()
            try:
                data, errors = ledger_io.load_collections(
                    {"fragments": (base, "fragment_id")},
                    root=root,
                    retries=10,
                    delay=0.02,
                )
            finally:
                thread.join()
            self.assertEqual(errors, [])
            self.assertEqual(list(data["fragments"]), ["FRAG-001", "FRAG-002"])

    def test_stable_read_never_returns_a_mixed_cooperating_rewrite(self) -> None:
        # All shipped writers replace the file atomically (ledger_io).  A reader
        # must never observe a mixture of the old and the new contents.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            first = "a" * 120_000 + "\n"
            second = "b" * 120_000 + "\n"
            path.write_text(first, encoding="utf-8")
            stop = threading.Event()
            failures: list[str] = []

            def writer() -> None:
                for index in range(60):
                    ledger_io.atomic_write_text(path, first if index % 2 else second)
                    time.sleep(0.001)

            def reader() -> None:
                while not stop.is_set():
                    try:
                        value = ledger_io.read_text_stable(path, retries=50, delay=0.005)
                    except ledger_io.LedgerBusy:
                        failures.append("busy")
                        return
                    if value not in (first, second):
                        failures.append(f"partial content: {len(value)} bytes")
                        return

            readers = [threading.Thread(target=reader) for _ in range(4)]
            for thread in readers:
                thread.start()
            writer_thread = threading.Thread(target=writer)
            writer_thread.start()
            writer_thread.join()
            stop.set()
            for thread in readers:
                thread.join()

            self.assertEqual(failures, [])

    def test_append_only_writer_never_corrupts_reads(self) -> None:
        # Shard writers append complete records and never truncate the file.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "state" / "fragments.jsonl"
            write_jsonl(base, [{"fragment_id": "FRAG-001"}])
            shard = base.with_name("fragments.d") / "2026-10-21-aaaaaaaaaaaa.jsonl"
            shard.parent.mkdir()
            shard.write_text("", encoding="utf-8")
            stop = threading.Event()
            failures: list[str] = []
            seen_counts: dict[int, list[int]] = {}

            def writer() -> None:
                with open(shard, "a", encoding="utf-8") as handle:
                    for index in range(2, 40):
                        handle.write(
                            json.dumps({"fragment_id": f"FRAG-{index:03d}"}) + "\n"
                        )
                        handle.flush()
                        time.sleep(0.002)

            def reader(slot: int) -> None:
                counts: list[int] = []
                seen_counts[slot] = counts
                while not stop.is_set():
                    try:
                        data, errors = ledger_io.load_collections(
                            {"fragments": (base, "fragment_id")},
                            root=root,
                            retries=20,
                            delay=0.005,
                        )
                    except ledger_io.LedgerBusy:
                        failures.append("busy")
                        return
                    if errors:
                        failures.append(errors[0])
                        return
                    counts.append(len(data["fragments"]))

            threads = [
                threading.Thread(target=reader, args=(slot,)) for slot in range(3)
            ]
            for thread in threads:
                thread.start()
            writer_thread = threading.Thread(target=writer)
            writer_thread.start()
            writer_thread.join()
            stop.set()
            for thread in threads:
                thread.join()

            self.assertEqual(failures, [])
            self.assertEqual(
                max(count for counts in seen_counts.values() for count in counts), 39
            )
            for counts in seen_counts.values():
                self.assertEqual(counts, sorted(counts))

    def test_stable_read_gives_up_with_ledger_busy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            with mock.patch.object(
                ledger_io, "_read_once_stable", side_effect=ledger_io._Unstable()
            ):
                with self.assertRaises(ledger_io.LedgerBusy):
                    ledger_io.read_text_stable(path, retries=1, delay=0)


class AtomicWriteTests(unittest.TestCase):
    def test_readers_never_see_a_partial_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.md"
            first = "# map\n" + ("a" * 200_000)
            second = "# map\n" + ("b" * 200_000)
            path.write_text(first, encoding="utf-8")
            stop = threading.Event()
            failures: list[str] = []

            def writer() -> None:
                for index in range(50):
                    ledger_io.atomic_write_text(path, first if index % 2 else second)
                    time.sleep(0.001)

            def reader() -> None:
                while not stop.is_set():
                    value = path.read_text(encoding="utf-8")
                    if value not in (first, second):
                        failures.append(f"partial file: {len(value)} bytes")
                        return

            readers = [threading.Thread(target=reader) for _ in range(4)]
            for thread in readers:
                thread.start()
            writer_thread = threading.Thread(target=writer)
            writer_thread.start()
            writer_thread.join()
            stop.set()
            for thread in readers:
                thread.join()

            self.assertEqual(failures, [])

    def test_atomic_write_preserves_mode_and_leaves_no_temp_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            os.chmod(path, 0o640)
            ledger_io.atomic_write_text(path, '{"a": 1}\n')
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            self.assertEqual([entry.name for entry in Path(tmp).iterdir()], [path.name])

    def test_atomic_write_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "file.txt"
            ledger_io.atomic_write_text(path, "hello")
            self.assertEqual(path.read_text(encoding="utf-8"), "hello")


class LockTests(unittest.TestCase):
    def test_lock_serialises_read_modify_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            anchor = root / "state" / "questions.jsonl"
            anchor.parent.mkdir(parents=True, exist_ok=True)
            counter = root / "counter.txt"
            counter.write_text("0", encoding="utf-8")

            def worker() -> None:
                for _ in range(15):
                    with ledger_io.exclusive_lock(anchor, timeout=10):
                        value = int(counter.read_text(encoding="utf-8"))
                        time.sleep(0.002)
                        counter.write_text(str(value + 1), encoding="utf-8")

            threads = [threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(counter.read_text(encoding="utf-8"), "30")

    def test_lock_timeout_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            anchor = Path(tmp) / "state" / "questions.jsonl"
            with ledger_io.exclusive_lock(anchor, timeout=1):
                with self.assertRaises(ledger_io.LedgerLockTimeout):
                    with ledger_io.exclusive_lock(anchor, timeout=0.1, poll=0.01):
                        pass


if __name__ == "__main__":
    unittest.main()
