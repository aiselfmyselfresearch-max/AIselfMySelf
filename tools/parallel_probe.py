#!/usr/bin/env python3
"""Measure how concurrent readers behave while a JSONL ledger is rewritten.

This is a diagnostic, not a workflow tool.  It writes only to a temporary
directory (or to --path when given explicitly), so it never touches state/*.jsonl
unless you ask it to.

For each (writer, reader) pair it reports how many reads saw:

``json``   a partial line that could not be parsed
``short``  a valid but incomplete/empty file (fewer records than written)
``busy``   ledger_io refused to return data because the file kept changing
``ok``     the full expected number of records

The "naive" writer is ``Path.write_text()`` (truncate, then write), which is what
the tools did before this branch.  The "atomic" writer is
``ledger_io.atomic_write_text()``.  The "naive" reader does a plain read and
``json.loads`` per line; the "stable" reader uses ``ledger_io``.

Example::

    python3 tools/parallel_probe.py
    python3 tools/parallel_probe.py --records 800 --readers 8 --iterations 60

Standard library only.  See docs/parallel-safety-audit.md.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import ledger_io


@dataclass
class Stats:
    reads: int = 0
    json_errors: int = 0
    short: int = 0
    busy: int = 0
    ok: int = 0


def make_payload(records: int, record_bytes: int) -> tuple[str, int]:
    lines = [
        json.dumps(
            {"fragment_id": f"FRAG-{index:05d}", "text": "x" * record_bytes},
            ensure_ascii=False,
        )
        for index in range(records)
    ]
    return "\n".join(lines) + "\n", records


def naive_read(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            json.loads(line)
            count += 1
    return count


def stable_read(path: Path, root: Path) -> int:
    data, errors = ledger_io.load_collections(
        {"fragments": (path, "fragment_id")}, root=root, retries=5, delay=0.02
    )
    if errors:
        raise RuntimeError(errors[0])
    return len(data["fragments"])


def run_case(
    *,
    writer_mode: str,
    reader_mode: str,
    records: int,
    record_bytes: int,
    iterations: int,
    readers: int,
) -> Stats:
    payload, expected = make_payload(records, record_bytes)
    stats = Stats()

    with tempfile.TemporaryDirectory(prefix="parallel-probe-") as tmp:
        root = Path(tmp)
        path = root / "fragments.jsonl"
        path.write_text(payload, encoding="utf-8")
        stop = threading.Event()
        lock = threading.Lock()

        def writer() -> None:
            for index in range(iterations):
                if writer_mode == "atomic":
                    ledger_io.atomic_write_text(path, payload)
                else:
                    path.write_text(payload, encoding="utf-8")
                time.sleep(0.002)

        def reader() -> None:
            while not stop.is_set():
                try:
                    count = (
                        stable_read(path, root)
                        if reader_mode == "stable"
                        else naive_read(path)
                    )
                except ledger_io.LedgerBusy:
                    with lock:
                        stats.busy += 1
                    continue
                except json.JSONDecodeError:
                    with lock:
                        stats.json_errors += 1
                    continue
                except Exception:
                    with lock:
                        stats.short += 1
                    continue
                with lock:
                    stats.reads += 1
                    if count == expected:
                        stats.ok += 1
                    else:
                        stats.short += 1

        threads = [threading.Thread(target=reader) for _ in range(readers)]
        for thread in threads:
            thread.start()
        writer_thread = threading.Thread(target=writer)
        writer_thread.start()
        writer_thread.join()
        stop.set()
        for thread in threads:
            thread.join()

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stress-test concurrent ledger reads")
    parser.add_argument("--records", type=int, default=400, help="records per file (default 400)")
    parser.add_argument(
        "--record-bytes", type=int, default=2000, help="text bytes per record (default 2000)"
    )
    parser.add_argument("--iterations", type=int, default=40, help="rewrites (default 40)")
    parser.add_argument("--readers", type=int, default=6, help="reader threads (default 6)")
    args = parser.parse_args(argv)

    if args.records < 1 or args.record_bytes < 1 or args.iterations < 1 or args.readers < 1:
        parser.error("all numeric options must be at least 1")

    print(
        f"ledger≈{(args.records * (args.record_bytes + 40)) / 1e6:.1f} MB, "
        f"rewrites={args.iterations}, readers={args.readers}"
    )
    header = f"{'writer':8} {'reader':8} {'parsed':>7} {'json':>7} {'short':>7} {'busy':>7} {'ok':>7}"
    print(header)
    print("-" * len(header))
    for writer_mode in ("naive", "atomic"):
        for reader_mode in ("naive", "stable"):
            stats = run_case(
                writer_mode=writer_mode,
                reader_mode=reader_mode,
                records=args.records,
                record_bytes=args.record_bytes,
                iterations=args.iterations,
                readers=args.readers,
            )
            print(
                f"{writer_mode:8} {reader_mode:8} {stats.reads:7d} {stats.json_errors:7d} "
                f"{stats.short:7d} {stats.busy:7d} {stats.ok:7d}"
            )
    print()
    print(
        "Note: a non-cooperating writer that truncates the file (the 'naive' row) can "
        "still expose a valid but short view; the protocol is append to shards or use "
        "ledger_io.atomic_write_text()."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
