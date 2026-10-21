#!/usr/bin/env python3
"""Concurrency-safe ledger I/O for the state/*.jsonl archives (stdlib only).

Why this module exists
----------------------
The ledgers are read by the viewer server and by the command line tools while
other sessions may be appending to them.  ``Path.read_text()`` is a single open
followed by one or more ``read()`` calls, and ``Path.write_text()`` truncates the
file before writing it.  A reader that arrives in the middle of a rewrite can
therefore see an empty file or a half-written JSON line.  Measured on a 4.5 MB
ledger, 38 of 246 concurrent reads failed that way (see
``docs/parallel-safety-audit.md``).

This module provides the pieces the tools use instead:

``read_text_stable()``
    Read a file only if its identity/size/mtime did not change across the read,
    retrying a few times while a writer is active.  Raises ``LedgerBusy`` if the
    file never settles.

``read_snapshot()``
    Read several files as one best-effort snapshot: every file is re-stat'ed
    after the reads, and the whole snapshot is retried if any of them changed.

``load_collections()``
    Read one or more collections from their frozen base file *and* their session
    shards (``state/<collection>.d/*.jsonl``), parse them, and report malformed
    or duplicate records with file/line labels.  Transient partial lines are
    retried before they are reported.

``atomic_write_text()``
    Write to a temporary file in the same directory, fsync it, then
    ``os.replace()`` it over the destination.  Readers see either the old file
    or the new one, never a truncated mixture, and a crash cannot leave a
    half-written ledger behind.

``exclusive_lock()``
    Advisory cross-process lock used around compound writes and shard creation
    (``--write-map``, ``import_researchos.py --write``,
    ``new_ledger_shard.py``).  It serialises cooperating tools; it
    cannot stop an editor or an ad-hoc ``>>`` redirect that ignores it.

Shard convention
----------------
``state/<collection>.jsonl`` is the frozen base.  A parallel session appends to
its own ``state/<collection>.d/<YYYY-MM-DD>-<12 hex>.jsonl`` shard, created by
``tools/new_ledger_shard.py``.  Every tool reads the union; nothing here
requires shards to exist.
"""
from __future__ import annotations

import contextlib
import errno
import json
import os
import stat
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable, Iterator


class LedgerError(Exception):
    """Base class for ledger I/O failures."""


class LedgerBusy(LedgerError):
    """The ledger kept changing while it was read; retry once the writer stops."""


class LedgerLockTimeout(LedgerError):
    """Another cooperating writer held the ledger lock for too long."""


class _Unstable(Exception):
    """Internal: a snapshot changed while it was being taken."""


_SHARD_SUFFIX = ".d"


def collection_files(base: Path) -> list[Path]:
    """Return the frozen base file followed by its shards, sorted by name.

    Missing base files are still returned so callers can report them; the shard
    directory is optional.
    """
    base = Path(base)
    shard_dir = base.with_name(base.stem + _SHARD_SUFFIX)
    shards: list[Path] = []
    if shard_dir.is_dir():
        shards = sorted(path for path in shard_dir.glob("*.jsonl") if path.is_file())
    return [base, *shards]


def shard_dir(base: Path) -> Path:
    """Return the shard directory belonging to a base ledger path."""
    base = Path(base)
    return base.with_name(base.stem + _SHARD_SUFFIX)


def display_path(path: Path, root: Path | None = None) -> str:
    """Return a repo-relative label when possible, an absolute path otherwise."""
    path = Path(path)
    if root is not None:
        try:
            return path.resolve().relative_to(Path(root).resolve()).as_posix()
        except (OSError, ValueError):
            pass
    return str(path)


def _signature(path: Path) -> tuple[int, int, int, int, int]:
    info = path.stat()
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read_once_stable(path: Path) -> str:
    """Read a file once and require its signature to be unchanged."""
    try:
        before = _signature(path)
        text = path.read_text(encoding="utf-8")
        after = _signature(path)
    except UnicodeDecodeError as exc:
        # A concurrent writer can expose a partial multi-byte sequence at EOF.
        raise _Unstable() from exc
    if before != after:
        raise _Unstable()
    return text


def read_text_stable(path: Path, *, retries: int = 5, delay: float = 0.02) -> str:
    """Read a text file, retrying while its signature changes.

    This avoids torn reads from cooperating writers and reduces (but cannot
    eliminate) the window exposed by a non-cooperating ``write_text()`` that
    truncates the file.  Raises ``FileNotFoundError`` when the file does not
    exist and ``LedgerBusy`` when it never settles.
    """
    path = Path(path)
    for attempt in range(retries + 1):
        try:
            return _read_once_stable(path)
        except _Unstable:
            if attempt >= retries:
                break
            time.sleep(delay)
    raise LedgerBusy(f"{path} changed while it was being read; retry after the writer finishes")


def _try_snapshot(paths: Iterable[Path]) -> dict[Path, str]:
    existing = [path for path in dict.fromkeys(Path(p) for p in paths) if path.is_file()]
    if not existing:
        return {}
    texts: dict[Path, str] = {}
    try:
        before = {path: _signature(path) for path in existing}
        for path in existing:
            texts[path] = path.read_text(encoding="utf-8")
        after = {path: _signature(path) for path in texts}
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        raise _Unstable() from exc
    if before != after:
        raise _Unstable()
    return texts


def read_snapshot(paths: Iterable[Path], *, retries: int = 5, delay: float = 0.02) -> dict[Path, str]:
    """Read several files, retrying the whole set if any file changed meanwhile."""
    paths = [Path(path) for path in dict.fromkeys(paths)]
    for attempt in range(retries + 1):
        try:
            return _try_snapshot(paths)
        except _Unstable:
            if attempt >= retries:
                break
            time.sleep(delay)
    raise LedgerBusy("ledger files changed while they were being read; retry after the writer finishes")


def _parse_collection(
    files: list[Path],
    texts: dict[Path, str],
    id_key: str,
    root: Path | None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    records: dict[str, dict[str, Any]] = {}
    first_seen: dict[str, tuple[Path, int]] = {}
    errors: list[str] = []
    for path in files:
        text = texts.get(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{display_path(path, root)}:{lineno}: invalid JSON: {exc}")
                continue
            if not isinstance(record, dict):
                errors.append(f"{display_path(path, root)}:{lineno}: record must be an object")
                continue
            identity = record.get(id_key)
            if not isinstance(identity, str) or not identity:
                errors.append(f"{display_path(path, root)}:{lineno}: missing {id_key}")
                continue
            if identity in records:
                previous_path, previous_line = first_seen[identity]
                errors.append(
                    f"{display_path(path, root)}:{lineno}: duplicate {id_key} {identity} "
                    f"(first defined at {display_path(previous_path, root)}:{previous_line})"
                )
                continue
            records[identity] = record
            first_seen[identity] = (path, lineno)
    return records, errors


def load_collections(
    specs: dict[str, tuple[Path, str]],
    *,
    root: Path | None = None,
    retries: int = 5,
    delay: float = 0.02,
) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    """Load collections from base files plus shards as one snapshot.

    ``specs`` maps a collection name to ``(base_path, id_key)``.  Returns the
    records per collection (insertion order: base, then shards sorted by name)
    and a list of human-readable errors.  A malformed line is retried a few
    times first, because it may be a writer's partially flushed record.
    """
    errors: list[str] = []
    last_parse_errors: list[str] = []
    for attempt in range(retries + 1):
        files_by_collection = {
            name: collection_files(base) for name, (base, _id_key) in specs.items()
        }
        all_paths: list[Path] = []
        for files in files_by_collection.values():
            for path in files:
                if path not in all_paths:
                    all_paths.append(path)
        try:
            texts = read_snapshot(all_paths, retries=0)
        except LedgerBusy:
            if attempt >= retries:
                raise
            time.sleep(delay)
            continue

        data: dict[str, dict[str, dict[str, Any]]] = {}
        parse_errors: list[str] = []
        for name, (base, id_key) in specs.items():
            records, collection_errors = _parse_collection(
                files_by_collection[name], texts, id_key, root
            )
            data[name] = records
            parse_errors.extend(collection_errors)

        if parse_errors and attempt < retries:
            last_parse_errors = parse_errors
            time.sleep(delay)
            continue

        for name, (base, _id_key) in specs.items():
            if base not in texts:
                errors.append(f"{display_path(base, root)}: ledger file is missing")
        errors.extend(parse_errors)
        return data, errors

    # Unreachable in normal operation; keep the failure explicit if the loop
    # above is ever changed.
    errors.extend(last_parse_errors)
    raise LedgerBusy("ledger files changed while they were being read; retry in a moment")


def load_jsonl_union(
    path: Path,
    id_key: str,
    errors: list[str] | None = None,
    *,
    root: Path | None = None,
    retries: int = 5,
    delay: float = 0.02,
) -> dict[str, dict[str, Any]]:
    """Compatibility wrapper: load one collection (base + shards) into an ID map."""
    data, new_errors = load_collections(
        {"ledger": (Path(path), id_key)}, root=root, retries=retries, delay=delay
    )
    if errors is not None:
        errors.extend(new_errors)
    return data["ledger"]


def atomic_write_text(path: Path, text: str, *, fsync: bool = True) -> None:
    """Replace ``path`` atomically with ``text``.

    The temporary file lives in the destination directory so ``os.replace()``
    stays on one filesystem.  Existing permissions are preserved; new files get
    0644.  On failure the temporary file is removed and the destination is left
    untouched.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            if fsync:
                os.fsync(handle.fileno())
        try:
            mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
            os.chmod(temporary, mode)
        except OSError:
            pass
        os.replace(temporary, path)
        if fsync:
            try:
                directory = os.open(path.parent, os.O_RDONLY)
            except OSError:
                directory = None
            if directory is not None:
                try:
                    os.fsync(directory)
                except OSError:
                    pass
                finally:
                    os.close(directory)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


@contextlib.contextmanager
def exclusive_lock(anchor: Path, *, timeout: float = 10.0, poll: float = 0.05) -> Iterator[None]:
    """Hold an advisory exclusive lock for compound writes and shard creation.

    The lock file is ``<anchor directory>/.ledger.lock`` (one lock for all
    ledgers in a state directory).  It serialises tools that cooperate; it does
    not protect against editors or shell redirections.
    """
    lock_path = Path(anchor).parent / ".ledger.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+b")
    try:
        if handle.tell() == 0 and os.name == "nt":
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                _try_lock(handle)
                break
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    raise LedgerError(f"cannot lock {lock_path}: {exc}") from exc
                if time.monotonic() >= deadline:
                    raise LedgerLockTimeout(
                        f"another writer holds {lock_path.name}; retry once it finishes"
                    ) from exc
                time.sleep(poll)
        try:
            yield
        finally:
            _unlock(handle)
    finally:
        handle.close()


if os.name == "nt":  # pragma: no cover - exercised on Windows only
    import msvcrt

    def _try_lock(handle: Any) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(handle: Any) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _try_lock(handle: Any) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(handle: Any) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
