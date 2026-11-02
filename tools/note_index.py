#!/usr/bin/env python3
"""Index the episodic reports in ``readings/`` without moving or rewriting them.

Why this tool exists.  ``readings/*.md`` are the archive's episodic memory: one
narrative report per session.  They are *not* ledger records, so before this tool
they had no ID, no metadata row, no entry in ``READING_MAP.md`` and no way to be
cited from ``read_log``.  Retrieval was limited to the rotating detail window in
``README.md`` (3+5 entries), ``docs/sessions.md`` (182 of 407 files), grep, and a
taxonomy shard that froze at 63% coverage on 2026-10-29.

The design rule is one source of truth per fact:

  * derived facts (bytes, chars, H1 title, referenced ledger IDs, inbound links,
    headings) are re-harvested from the files every run and are **never** stored
    in the ledger, because a copy of a derivable fact is a fact that can drift;
  * curated judgments (mode, quadrant, return_status, read_depth, consolidated
    claims, salience) live in the append-only ``notes`` collection
    (``state/notes.jsonl`` + ``state/notes.d/``) and are overlaid onto the
    harvest in ledger order, so a later reading supersedes an earlier one without
    rewriting it.

Determinism: the harvest reads file *contents and names* only.  Git history,
mtimes and today's date never enter the generated index, so a shallow clone and a
full clone produce byte-identical output.

Usage:
  python3 tools/note_index.py                    # summary report
  python3 tools/note_index.py --check            # is READING_MAP.md §8 current?
  python3 tools/note_index.py --orphans          # reports no document links to
  python3 tools/note_index.py --for-id Q-099     # reports that reference an ID
  python3 tools/note_index.py --candidates       # curated-row candidates (stdout)
  python3 tools/note_index.py --register readings/x.md --session SESSION-...
  python3 tools/note_index.py --report --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import ledger_io
from validate_seed import COLLECTIONS, ROOT

NOTES_DIR_NAME = "readings"
INDEX_SECTION_HEADING = "## 8. 精読ノート索引"
NOTES_SHARD_CHUNK = 25

# A ledger ID looks like PREFIX-segment(-segment...).  Tokens are harvested with
# one generic pattern and then filtered against the IDs that actually exist, so a
# new ID shape never needs a new regex.
_TOKEN = re.compile(r"\b(?:Q|FRAG|MOTIF|MAT|REL|ERR|ED|READ|SESSION|NOTE)(?:-[0-9A-Za-z]+)+")
_PREFIX_TO_COLLECTION = {
    "Q": "questions",
    "FRAG": "fragments",
    "MOTIF": "motifs",
    "MAT": "materials",
    "REL": "relations",
    "SESSION": "sessions",
    "READ": "read_log",
    "ERR": "errata",
    "ED": "editorial_decisions",
    "NOTE": "notes",
}
_COLLECTION_LABELS = {
    "questions": "Q",
    "fragments": "F",
    "materials": "M",
    "motifs": "MOT",
    "relations": "R",
    "sessions": "S",
    "read_log": "READ",
    "errata": "ERR",
    "editorial_decisions": "ED",
    "notes": "NOTE",
}
# Ordered for the compact "参照" column of the index table.
_REF_ORDER = ("questions", "fragments", "materials", "motifs", "relations", "sessions", "errata", "editorial_decisions")

_DATE_LABEL = re.compile(r"^(\d{4}-\d{2}-\d{2})")
# The real (execution-environment) date is written in several shapes, and a bare
# ``**日付**`` bullet usually carries the *internal chronology label* instead.
# So only explicitly real-date markers are harvested, the matched rule is kept
# next to the value, and everything else stays None rather than being guessed.
_REAL_DATE_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("実UTC日付", re.compile(r"実(?:行環境の)?(?:実)?UTC日付[^0-9]{0,16}`?(\d{4}-\d{2}-\d{2})")),
    ("実行日", re.compile(r"実行日[^0-9]{0,16}`?(\d{4}-\d{2}-\d{2})")),
    ("日付+UTC注記", re.compile(r"\*\*日付\*\*\s*[：:]\s*`?(\d{4}-\d{2}-\d{2})`?\s*（[^）]{0,24}(?:UTC|実作業|実行日)")),
    ("日付+実作業", re.compile(r"\*\*日付\*\*\s*[：:]\s*`?(\d{4}-\d{2}-\d{2})`?\s*（実作業")),
    ("日付(UTC)", re.compile(r"`?(\d{4}-\d{2}-\d{2})`?\s*（UTC")),
)
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_PROMPT_LINK = re.compile(r"prompts/([a-z_]+)\.md")
_MD_LINK_TARGET = re.compile(r"\]\(([^)\s]+\.md)\)")
_PATH_MENTION = re.compile(r"readings/([A-Za-z0-9._-]+\.(?:md|tsv|json))")

# Documents a reader can navigate from.  READING_MAP.md is excluded on purpose:
# it is generated *from* this index, so counting it would make every report
# "reachable" and hide the orphan problem it is meant to measure.
#
# A report quoting *its own* path is excluded for the same reason: a reader
# standing inside a document cannot navigate to that document from it.  Reports
# that reproduce their own path (a `mv readings/x.md /tmp/` recovery step, a
# citation of the file they are writing) would otherwise mark themselves
# reachable and silently shrink the orphan count they are meant to grow.
_GENERATED_DOCS = frozenset({"READING_MAP.md"})


# ---------------------------------------------------------------------------
# known ledger IDs
# ---------------------------------------------------------------------------

def known_ids(data: dict[str, dict[str, dict[str, Any]]], root: Path = ROOT) -> dict[str, set[str]]:
    """Return the existing IDs per collection, including errata (not in COLLECTIONS)."""
    known: dict[str, set[str]] = {}
    for name, records in data.items():
        known[name] = set(records)
    if "errata" not in known:
        base = Path(root) / "state" / "errata.jsonl"
        if base.is_file() or ledger_io.shard_dir(base).is_dir():
            known["errata"] = set(
                ledger_io.load_jsonl_union(base, "errata_id", [], root=Path(root))
            )
        else:
            known["errata"] = set()
    known.setdefault("notes", set())
    return known


def _resolve_token(token: str, flat_known: set[str]) -> str | None:
    """Match a harvested token to a real ID, tolerating trailing prose.

    ``Q-001-based`` is not an ID but ``Q-001`` is, so progressively drop the
    trailing ``-segment`` until the remainder is known.
    """
    if token in flat_known:
        return token
    parts = token.split("-")
    while len(parts) > 2:
        parts.pop()
        candidate = "-".join(parts)
        if candidate in flat_known:
            return candidate
    return None


# ---------------------------------------------------------------------------
# inbound links (reachability)
# ---------------------------------------------------------------------------

def _link_source_paths(root: Path) -> list[Path]:
    root = Path(root)
    sources: list[Path] = []
    for path in sorted(root.glob("*.md")):
        if path.name not in _GENERATED_DOCS:
            sources.append(path)
    for pattern in ("docs/*.md", "prompts/*.md", f"{NOTES_DIR_NAME}/*.md", "taxonomy/notes/*.md"):
        sources.extend(sorted(root.glob(pattern)))
    return sources


def _normalise_link(source_dir: Path, target: str, root: Path) -> Path | None:
    """Resolve one Markdown link target to a path under ``readings/``, or None.

    Handles every shape this archive actually uses: a bare sibling filename
    (``[前](2026-11-01-x.md)``), a rooted path (``](readings/x.md)``), a parent
    step out of docs/ or prompts/ (``](../readings/x.md)``) and an absolute
    GitHub blob URL (``…/blob/main/readings/x.md``).
    """
    cleaned = target.split("#", 1)[0].strip()
    if not cleaned or cleaned.startswith("mailto:"):
        return None
    if cleaned.startswith(("http://", "https://")):
        marker = f"/{NOTES_DIR_NAME}/"
        position = cleaned.rfind(marker)
        if position == -1:
            return None
        cleaned = cleaned[position + 1 :]
    candidate = Path(cleaned)
    if candidate.is_absolute():
        return None
    # A target that already carries the readings/ prefix is root-relative (that is
    # how README.md, docs/ and an absolute GitHub blob URL all write it); anything
    # else is relative to the document that contains the link.
    base = Path(root) if candidate.parts[:1] == (NOTES_DIR_NAME,) else Path(source_dir)
    resolved = Path(os.path.normpath(str(base / candidate)))
    try:
        relative = resolved.relative_to(Path(root))
    except ValueError:
        return None
    if relative.parts[:1] != (NOTES_DIR_NAME,) or len(relative.parts) != 2:
        return None
    return relative


def inbound_links(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Map ``readings/<file>`` -> {linked: [...], mentioned: [...]}.

    ``linked`` means a Markdown link target a reader can click through;
    ``mentioned`` means the path appears in prose or a code span, which an agent
    can still open but a human reader cannot click.  Both count as reachable, and
    the two are reported separately because the difference is exactly the gap
    between "navigable" and "greppable".
    """
    root = Path(root)
    inbound: dict[str, dict[str, set[str]]] = {}
    for source in _link_source_paths(root):
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            rel_source = str(source.relative_to(root))
        except ValueError:
            rel_source = source.name
        linked_targets: set[str] = set()
        for target in _MD_LINK_TARGET.findall(text):
            resolved = _normalise_link(source.parent, target, root)
            if resolved is not None and str(resolved) != rel_source:
                linked_targets.add(str(resolved))
        for name in _PATH_MENTION.findall(text):
            rel = f"{NOTES_DIR_NAME}/{name}"
            if rel == rel_source:
                continue
            bucket = inbound.setdefault(rel, {"linked": set(), "mentioned": set()})
            if rel in linked_targets:
                bucket["linked"].add(rel_source)
            else:
                bucket["mentioned"].add(rel_source)
        # a bare sibling link (](x.md)) never matches the `readings/` mention
        # pattern, so record it here or it is lost
        for rel in linked_targets:
            bucket = inbound.setdefault(rel, {"linked": set(), "mentioned": set()})
            bucket["linked"].add(rel_source)
    return {
        rel: {"linked": sorted(v["linked"]), "mentioned": sorted(v["mentioned"])}
        for rel, v in inbound.items()
    }


# ---------------------------------------------------------------------------
# harvest (derived facts)
# ---------------------------------------------------------------------------

def _harvest_one(path: Path, rel: str, flat_known: set[str]) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    title = path.stem
    headings: list[str] = []
    for line in lines:
        match = _HEADING.match(line)
        if not match:
            continue
        level, body = match.group(1), match.group(2).strip()
        if level == "#" and title == path.stem:
            title = body
        elif level in ("##", "###"):
            headings.append(f"{level} {body}")

    date_match = _DATE_LABEL.match(path.name)
    date_real: str | None = None
    date_rule: str | None = None
    for rule_name, pattern in _REAL_DATE_RULES:
        found = pattern.search(text[:8000])
        if found:
            date_real, date_rule = found.group(1), rule_name
            break
    # The declared mode sits in the header block; fall back to the whole file
    # only when the header names no prompt template.
    modes = Counter(_PROMPT_LINK.findall(text[:2500])) or Counter(_PROMPT_LINK.findall(text))

    refs: dict[str, list[str]] = {}
    unknown: list[str] = []
    seen_tokens: set[str] = set()
    for token in _TOKEN.findall(text):
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        resolved = _resolve_token(token, flat_known)
        if resolved is None:
            unknown.append(token)
            continue
        collection = _PREFIX_TO_COLLECTION.get(resolved.split("-", 1)[0])
        if collection is None:
            continue
        bucket = refs.setdefault(collection, [])
        if resolved not in bucket:
            bucket.append(resolved)

    session_ids = refs.get("sessions", [])
    outbound = sorted(
        {
            _normalise_link(path.parent, target, path.parent.parent).name
            for target in _MD_LINK_TARGET.findall(text)
            if (resolved := _normalise_link(path.parent, target, path.parent.parent)) is not None
            and resolved.name != path.name
        }
    )

    return {
        "path": rel,
        "name": path.name,
        "ext": path.suffix or "",
        "bytes": len(raw),
        "chars": len(text),
        "lines": len(lines),
        "title": title,
        "date_label": date_match.group(1) if date_match else None,
        "date_real": date_real,
        "date_real_source": date_rule,
        "mode": modes.most_common(1)[0][0] if modes else None,
        "session_ids": session_ids,
        "refs": {name: sorted(ids) for name, ids in refs.items()},
        "ref_count": sum(len(ids) for ids in refs.values()),
        "unknown_ids": sorted(unknown)[:12],
        "unknown_id_count": len(unknown),
        "headings": headings[:60],
        "outbound_notes": outbound,
    }


def harvest(root: Path = ROOT, data: dict[str, dict[str, dict[str, Any]]] | None = None) -> dict[str, dict[str, Any]]:
    """Re-derive every fact about every file in ``readings/`` from its content."""
    root = Path(root)
    notes_dir = root / NOTES_DIR_NAME
    if not notes_dir.is_dir():
        return {}
    if data is None:
        data = _load_ledgers(root)
    known = known_ids(data, root)
    flat_known: set[str] = set()
    for ids in known.values():
        flat_known |= ids
    harvested: dict[str, dict[str, Any]] = {}
    for path in sorted(p for p in notes_dir.iterdir() if p.is_file()):
        if path.name.startswith(".") or "__pycache__" in path.parts:
            continue
        rel = f"{NOTES_DIR_NAME}/{path.name}"
        harvested[rel] = _harvest_one(path, rel, flat_known)
    return harvested


# ---------------------------------------------------------------------------
# curated overlay
# ---------------------------------------------------------------------------

def order_note_rows(notes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Order note rows in ledger order, honouring explicit ``supersedes``.

    Same reason ``ledger_io._order_editorial_decisions`` exists: a shard written
    under a forward-dated internal chronology label can sort *after* the real-date
    shard that supersedes it.
    """
    rows = list(notes.values())
    by_id = {row.get("note_id"): index for index, row in enumerate(rows)}
    outgoing: list[list[int]] = [[] for _ in rows]
    indegree = [0] * len(rows)
    edges = False
    for j, row in enumerate(rows):
        supersedes = row.get("supersedes")
        if not isinstance(supersedes, list):
            continue
        nid = row.get("note_id")
        for sup_id in supersedes:
            if not isinstance(sup_id, str) or sup_id == nid:
                continue
            i = by_id.get(sup_id)
            if i is None or rows[i].get("path") != row.get("path"):
                continue
            outgoing[i].append(j)
            indegree[j] += 1
            edges = True
    if not edges:
        return rows
    order: list[int] = []
    ready = [i for i in range(len(rows)) if indegree[i] == 0]
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in outgoing[current]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
    order.extend(i for i in range(len(rows)) if i not in set(order))
    return [rows[i] for i in order]


_CURATED_FIELDS = (
    "title",
    "date_real",
    "mode",
    "quadrant",
    "subcategories",
    "return_status",
    "read_depth",
    "claims",
    "salience",
    "reason",
    "notes",
)


def build_view(
    root: Path = ROOT,
    data: dict[str, dict[str, dict[str, Any]]] | None = None,
    *,
    harvested: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Merge the harvest with the curated ``notes`` ledger: one entry per file."""
    root = Path(root)
    if data is None:
        data = _load_ledgers(root)
    if harvested is None:
        harvested = harvest(root, data)
    inbound = inbound_links(root)
    notes = data.get("notes", {})

    rows_by_path: dict[str, list[dict[str, Any]]] = {}
    for row in order_note_rows(notes):
        path = row.get("path")
        if isinstance(path, str) and path:
            rows_by_path.setdefault(path, []).append(row)

    view: dict[str, dict[str, Any]] = {}
    for rel, facts in harvested.items():
        rows = rows_by_path.get(rel, [])
        curated: dict[str, Any] = {}
        for row in rows:  # later rows win
            for field in _CURATED_FIELDS:
                if field in row:
                    curated[field] = row[field]
        entry = dict(facts)
        inbound_here = inbound.get(rel, {"linked": [], "mentioned": []})
        entry["linked_from"] = inbound_here["linked"]
        entry["mentioned_in"] = inbound_here["mentioned"]
        entry["inbound"] = inbound_here["linked"] + [
            source for source in inbound_here["mentioned"] if source not in inbound_here["linked"]
        ]
        entry["reachable"] = bool(entry["inbound"])
        entry["note_ids"] = [row.get("note_id") for row in rows if row.get("note_id")]
        entry["note_id"] = rows[-1].get("note_id") if rows else None
        entry["report_session_id"] = rows[-1].get("report_session_id") if rows else None
        entry["curated"] = curated
        for field in _CURATED_FIELDS:
            if field in curated:
                entry[field] = curated[field]
        view[rel] = entry

    # curated rows whose file is gone (or whose path is wrong) stay visible
    for rel, rows in rows_by_path.items():
        if rel in view:
            continue
        view[rel] = {
            "path": rel,
            "name": rel.split("/")[-1],
            "ext": Path(rel).suffix,
            "bytes": 0,
            "chars": 0,
            "lines": 0,
            "title": rows[-1].get("title") or rel,
            "date_label": None,
            "date_real": rows[-1].get("date_real"),
            "mode": rows[-1].get("mode"),
            "session_ids": [],
            "refs": {},
            "ref_count": 0,
            "unknown_ids": [],
            "unknown_id_count": 0,
            "headings": [],
            "outbound_notes": [],
            "linked_from": inbound.get(rel, {"linked": [], "mentioned": []})["linked"],
            "mentioned_in": inbound.get(rel, {"linked": [], "mentioned": []})["mentioned"],
            "inbound": inbound.get(rel, {"linked": [], "mentioned": []})["linked"]
            + inbound.get(rel, {"linked": [], "mentioned": []})["mentioned"],
            "reachable": bool(inbound.get(rel, {}).get("linked") or inbound.get(rel, {}).get("mentioned")),
            "note_ids": [row.get("note_id") for row in rows if row.get("note_id")],
            "note_id": rows[-1].get("note_id"),
            "report_session_id": rows[-1].get("report_session_id"),
            "curated": {k: v for k, v in rows[-1].items() if k in _CURATED_FIELDS},
            "missing_file": True,
        }
    return view


# ---------------------------------------------------------------------------
# generated documents
# ---------------------------------------------------------------------------

def _compact_refs(entry: dict[str, Any]) -> str:
    parts = []
    for name in _REF_ORDER:
        ids = entry.get("refs", {}).get(name)
        if ids:
            parts.append(f"{_COLLECTION_LABELS[name]}{len(ids)}")
    return " ".join(parts) or "—"


def _one_line(text: str, limit: int) -> str:
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def build_index_section(view: dict[str, dict[str, Any]]) -> list[str]:
    """The tracked Tier 2 table: one row per report, no body text."""
    entries = [view[key] for key in sorted(view)]
    curated_count = sum(1 for entry in entries if entry.get("note_id"))
    orphan_count = sum(1 for entry in entries if not entry.get("reachable"))
    real_dates = sum(1 for entry in entries if entry.get("date_real"))
    total_bytes = sum(entry.get("bytes", 0) for entry in entries)

    out: list[str] = [
        f"{INDEX_SECTION_HEADING}（{NOTES_DIR_NAME}/・{len(entries)}本・{total_bytes:,} B）",
        "",
        (
            "> 各行は `tools/note_index.py` が**ファイルから毎回読み直す導出事実**"
            "（題・字量・参照ID・到達性）と、`state/notes.jsonl`＋`state/notes.d/` の"
            "**追記専用の判断**（モード・象限・固定された主張）を合わせたものです。"
            "本文はこの索引に複製しません（正本は `readings/` 自身）。"
            "全文詳細は `map/60-notes-*.md`（git 管理外）。設計は "
            "[`docs/memory-architecture.md`](docs/memory-architecture.md) 参照。"
        ),
        "> **ファイル名順は作業順ではありません。** 名前の日付は内部編年ラベルで、"
        "実行環境の実日付とずれます（実日付の記載があるのは "
        f"{real_dates}/{len(entries)} 本）。`実日付` 列が `—` の行は、"
        "そのノートが実日付を書いていないことを示します。",
        "",
        f"- **判断が台帳化されたノート**：{curated_count} 本（`state/notes*` に `NOTE-` 行がある）",
        f"- **どの文書からもリンクされていないノート**：{orphan_count} 本"
        "（`python3 tools/note_index.py --orphans`）",
        "",
        "| ファイル | 実日付 | ラベル | セッション | 字 | 参照 | 到達 | 題 |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for entry in entries:
        sessions = entry.get("session_ids") or []
        session_cell = f"`{sessions[0]}`" if sessions else "—"
        if len(sessions) > 1:
            session_cell += f" +{len(sessions) - 1}"
        out.append(
            f"| `{entry['path']}` | {entry.get('date_real') or '—'} | "
            f"{entry.get('date_label') or '—'} | {session_cell} | {entry.get('chars', 0):,} | "
            f"{_compact_refs(entry)} | {'✓' if entry.get('reachable') else '—'} | "
            f"{_one_line(entry.get('title') or entry['name'], 60)} |"
        )
    out.append("")
    return out


def build_note_bodies(view: dict[str, dict[str, Any]], paths: list[str]) -> str:
    """One Tier 3 shard: the full harvested detail for a range of reports."""
    out: list[str] = [
        f"# 精読ノート詳細（{len(paths)}本・{paths[0] if paths else ''} 〜）",
        "",
        "> `tools/note_index.py` が `readings/` から生成した全文詳細シャードです（git 管理外）。",
        "",
    ]
    for rel in paths:
        entry = view.get(rel)
        if entry is None:
            continue
        out.append(f"## `{rel}`")
        out.append("")
        out.append(f"- **題**: {entry.get('title') or entry['name']}")
        out.append(
            f"- **規模**: {entry.get('bytes', 0):,} B ／ {entry.get('chars', 0):,} 字 ／ "
            f"{entry.get('lines', 0):,} 行"
        )
        out.append(
            f"- **日付**: 実日付 {entry.get('date_real') or '—'} ／ "
            f"内部編年ラベル {entry.get('date_label') or '—'}"
        )
        sessions = entry.get("session_ids") or []
        out.append(f"- **セッション**: {', '.join(f'`{s}`' for s in sessions) or '—'}")
        if entry.get("mode"):
            out.append(f"- **モード（導出）**: `{entry['mode']}`")
        curated = entry.get("curated") or {}
        for field in ("quadrant", "return_status", "read_depth", "salience"):
            if curated.get(field) is not None:
                out.append(f"- **{field}（台帳判断）**: `{curated[field]}`")
        if curated.get("subcategories"):
            out.append(f"- **subcategories（台帳判断）**: {', '.join(f'`{s}`' for s in curated['subcategories'])}")
        if entry.get("note_ids"):
            out.append(f"- **台帳行**: {', '.join(f'`{n}`' for n in entry['note_ids'])}")
        for name in _REF_ORDER:
            ids = entry.get("refs", {}).get(name)
            if ids:
                shown = ", ".join(f"`{i}`" for i in ids[:24])
                more = f" ほか{len(ids) - 24}件" if len(ids) > 24 else ""
                out.append(f"- **参照 {_COLLECTION_LABELS[name]}（{len(ids)}）**: {shown}{more}")
        if entry.get("unknown_id_count"):
            out.append(
                f"- **台帳に存在しないID字串**: {entry['unknown_id_count']} 種"
                f"（例 {', '.join(f'`{u}`' for u in entry.get('unknown_ids', [])[:6])}）"
            )
        linked_from = entry.get("linked_from") or []
        mentioned_in = entry.get("mentioned_in") or []
        out.append(
            f"- **ここへリンクする文書（{len(linked_from)}）**: "
            + (", ".join(f"`{s}`" for s in linked_from[:8]) or "なし")
        )
        if mentioned_in:
            out.append(
                f"- **パスを本文中に書くだけの文書（{len(mentioned_in)}）**: "
                + ", ".join(f"`{s}`" for s in mentioned_in[:8])
            )
        if not linked_from and not mentioned_in:
            out.append("- **到達手段**: ファイル名・grep・Git 履歴のみ（孤立）")
        if entry.get("outbound_notes"):
            out.append(
                f"- **ここからリンクするノート（{len(entry['outbound_notes'])}）**: "
                + ", ".join(f"`{o}`" for o in entry["outbound_notes"][:8])
            )
        claims = curated.get("claims") or []
        if claims:
            out.append("- **固定された主張（エピソード→意味記憶）**: ")
            for claim in claims:
                anchor = f"（{claim['anchor']}）" if claim.get("anchor") else ""
                out.append(f"  - `{claim.get('claim_id')}` [{claim.get('kind')}]{anchor} {claim.get('text')}")
        if curated.get("reason"):
            out.append(f"- **記録理由**: {_one_line(curated['reason'], 300)}")
        headings = entry.get("headings") or []
        if headings:
            out.append(f"- **見出し（{len(headings)}）**: " + " ／ ".join(_one_line(h, 60) for h in headings[:24]))
        if entry.get("missing_file"):
            out.append("- **警告**: 台帳行はあるがファイルが見つからない（パスの誤りか未マージ）")
        out.append("")
    return "\n".join(out)


def shard_plan(view: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Range-partition the index by sorted path so new reports land in the tail."""
    paths = sorted(view)
    plan: list[dict[str, Any]] = []
    if not paths:
        return plan
    chunks = [paths[i:i + NOTES_SHARD_CHUNK] for i in range(0, len(paths), NOTES_SHARD_CHUNK)]
    for index, chunk in enumerate(chunks, 1):
        plan.append({"file": f"60-notes-{index:02d}.md", "kind": "notes", "ids": chunk})
    return plan


# ---------------------------------------------------------------------------
# checks and reports
# ---------------------------------------------------------------------------

def _load_ledgers(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    errors: list[str] = []
    data: dict[str, dict[str, dict[str, Any]]] = {}
    for name, (filename, id_key, _schema) in COLLECTIONS.items():
        base = Path(root) / "state" / filename
        if not base.is_file() and not ledger_io.shard_dir(base).is_dir():
            data[name] = {}
            continue
        data[name] = ledger_io.load_jsonl_union(base, id_key, errors, root=Path(root))
    if errors:
        raise ValueError("; ".join(errors))
    return data


def orphans(view: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [view[key] for key in sorted(view) if not view[key].get("reachable")]


def notes_for_id(view: dict[str, dict[str, Any]], target_id: str) -> list[dict[str, Any]]:
    """Reports that reference one ledger ID (used by the continuation packet)."""
    hits = []
    for key in sorted(view):
        entry = view[key]
        for ids in entry.get("refs", {}).values():
            if target_id in ids:
                hits.append(entry)
                break
    return hits


def summarize(view: dict[str, dict[str, Any]]) -> dict[str, Any]:
    entries = list(view.values())
    by_ext = Counter(entry.get("ext") or "(none)" for entry in entries)
    refs_total = Counter()
    for entry in entries:
        for name, ids in entry.get("refs", {}).items():
            refs_total[name] += len(ids)
    unknown_total = sum(entry.get("unknown_id_count", 0) for entry in entries)
    curated = [entry for entry in entries if entry.get("note_id")]
    claims = sum(len(entry.get("curated", {}).get("claims") or []) for entry in entries)
    return {
        "notes": len(entries),
        "bytes": sum(entry.get("bytes", 0) for entry in entries),
        "chars": sum(entry.get("chars", 0) for entry in entries),
        "by_extension": dict(by_ext.most_common()),
        "reachable": sum(1 for entry in entries if entry.get("reachable")),
        "linked": sum(1 for entry in entries if entry.get("linked_from")),
        "mentioned_only": sum(
            1 for entry in entries if entry.get("mentioned_in") and not entry.get("linked_from")
        ),
        "orphans": sum(1 for entry in entries if not entry.get("reachable")),
        "with_real_date": sum(1 for entry in entries if entry.get("date_real")),
        "with_session_id": sum(1 for entry in entries if entry.get("session_ids")),
        "with_derived_mode": sum(1 for entry in entries if entry.get("mode")),
        "curated_rows": len(curated),
        "curated_paths": len({entry["path"] for entry in curated}),
        "consolidated_claims": claims,
        "referenced_ids": dict(refs_total.most_common()),
        "unknown_id_tokens": unknown_total,
        "missing_files": sum(1 for entry in entries if entry.get("missing_file")),
    }


def section_is_current(root: Path, index_path: Path, view: dict[str, dict[str, Any]]) -> bool:
    """True when READING_MAP.md carries exactly the section this view generates."""
    index_path = Path(index_path)
    if not index_path.is_file():
        return False
    lines = index_path.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(INDEX_SECTION_HEADING):
            start = i
            break
    if start is None:
        return False
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## ") and not lines[i].startswith(INDEX_SECTION_HEADING):
            end = i
            break
    current = lines[start:end]
    while current and not current[-1].strip():
        current.pop()
    expected = build_index_section(view)
    while expected and not expected[-1].strip():
        expected.pop()
    return current == expected


# ---------------------------------------------------------------------------
# registration (append-only curated rows)
# ---------------------------------------------------------------------------

def candidate_rows(
    view: dict[str, dict[str, Any]],
    paths: Iterable[str] | None = None,
    *,
    day: str | None = None,
    session_id: str | None = None,
) -> list[dict[str, Any]]:
    """Minimal curated rows for reports that have none yet (nothing is written)."""
    import new_id

    stamp = (day or date.today().isoformat()).replace("-", "")
    taken: set[str] = set()
    rows: list[dict[str, Any]] = []
    selected = sorted(view) if paths is None else sorted({p for p in paths if p in view})
    for rel in selected:
        entry = view[rel]
        if entry.get("note_id"):
            continue
        row: dict[str, Any] = {
            "note_id": new_id.mint("NOTE", day=stamp, taken=taken),
            "path": rel,
            "created_at": day or date.today().isoformat(),
        }
        if session_id:
            row["session_id"] = session_id
        if entry.get("mode"):
            row["mode"] = entry["mode"]
        if entry.get("date_real"):
            row["date_real"] = entry["date_real"]
        sessions = [s for s in entry.get("session_ids") or []]
        if sessions:
            row["report_session_id"] = sessions[0]
        row["read_depth"] = "metadata_and_structure_only"
        taken.add(row["note_id"])
        rows.append(row)
    return rows


def register(
    root: Path,
    paths: list[str],
    *,
    session_id: str,
    shard: Path | None = None,
    read_depth: str | None = None,
    mode: str | None = None,
    day: str | None = None,
) -> tuple[Path, list[dict[str, Any]]]:
    """Append one curated row per path to this session's ``notes`` shard."""
    import new_id
    import new_ledger_shard

    root = Path(root)
    data = _load_ledgers(root)
    view = build_view(root, data)
    created_at = day or date.today().isoformat()
    stamp = created_at.replace("-", "")
    taken = set(data.get("notes", {}))
    rows: list[dict[str, Any]] = []
    for rel in paths:
        entry = view.get(rel)
        if entry is None:
            raise ValueError(f"no such report: {rel} (expected a file under {NOTES_DIR_NAME}/)")
        if entry.get("note_id"):
            raise ValueError(f"{rel} already has note row {entry['note_id']}; append a superseding row by hand")
        row: dict[str, Any] = {
            "note_id": new_id.mint("NOTE", day=stamp, taken=taken),
            "path": rel,
            "session_id": session_id,
            "created_at": created_at,
        }
        if mode or entry.get("mode"):
            row["mode"] = mode or entry["mode"]
        if entry.get("date_real"):
            row["date_real"] = entry["date_real"]
        if read_depth:
            row["read_depth"] = read_depth
        report_sessions = entry.get("session_ids") or []
        if report_sessions:
            row["report_session_id"] = report_sessions[0]
        taken.add(row["note_id"])
        rows.append(row)

    if not rows:
        raise ValueError("nothing to register")

    target = Path(shard) if shard else new_ledger_shard.create_shard("notes", root=root)
    body = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    with ledger_io.exclusive_lock(root / "state" / "notes.jsonl"):
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.is_file() else ""
        if existing and not existing.endswith("\n"):
            existing += "\n"
        ledger_io.atomic_write_text(target, existing + body)
    return target, rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(view: dict[str, dict[str, Any]], stats: dict[str, Any]) -> None:
    print("=== readings/ episodic index report ===")
    print(f"  notes              : {stats['notes']} files, {stats['bytes']:,} B, {stats['chars']:,} chars")
    print(f"  extensions         : {stats['by_extension']}")
    print(
        f"  reachable          : {stats['reachable']} "
        f"(link {stats['linked']} ／ path mention only {stats['mentioned_only']}) ／ orphan {stats['orphans']}"
    )
    print(f"  real date written  : {stats['with_real_date']} ／ session id found {stats['with_session_id']}")
    print(f"  derived mode       : {stats['with_derived_mode']}")
    print(f"  curated ledger rows: {stats['curated_rows']} rows covering {stats['curated_paths']} paths")
    print(f"  consolidated claims: {stats['consolidated_claims']}")
    print(f"  referenced ledger ids: {stats['referenced_ids']}")
    print(f"  id tokens not in any ledger: {stats['unknown_id_tokens']}")
    if stats["missing_files"]:
        print(f"  WARN curated rows pointing at a missing file: {stats['missing_files']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--index", type=Path, default=ROOT / "READING_MAP.md", help="tracked Tier 2 index")
    parser.add_argument("--check", action="store_true", help="verify the READING_MAP.md note section is current")
    parser.add_argument("--orphans", action="store_true", help="list reports no document links to")
    parser.add_argument("--report", action="store_true", help="print the aggregate report")
    parser.add_argument("--for-id", metavar="ID", help="list reports that reference one ledger ID")
    parser.add_argument("--candidates", nargs="*", metavar="PATH", help="print curated-row candidates as JSONL")
    parser.add_argument("--register", nargs="+", metavar="PATH", help="append curated rows for these reports")
    parser.add_argument("--session", metavar="SESSION_ID", help="session id for --register")
    parser.add_argument("--shard", type=Path, help="append to this shard instead of creating one")
    parser.add_argument("--read-depth", choices=["full_text_read", "excerpt_and_metadata_read", "metadata_and_structure_only"])
    parser.add_argument("--mode", help="working mode for --register (prompts/ vocabulary)")
    parser.add_argument("--date", help="YYYY-MM-DD for created_at (default: today's real date)")
    parser.add_argument("--limit", type=int, default=40, help="max rows to print for --orphans/--for-id")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    try:
        data = _load_ledgers(root)
        view = build_view(root, data)
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    stats = summarize(view)

    if args.check:
        if section_is_current(root, args.index, view):
            print(f"PASS: note index section in {args.index.name} is current ({stats['notes']} notes)")
            return 0
        print(
            f"STALE: the note index section in {args.index.name} does not match {NOTES_DIR_NAME}/; "
            "run `python3 tools/map_build.py`",
            file=sys.stderr,
        )
        return 1

    if args.register:
        if not args.session:
            print("error: --register needs --session SESSION-ID", file=sys.stderr)
            return 2
        try:
            shard, rows = register(
                root,
                args.register,
                session_id=args.session,
                shard=args.shard,
                read_depth=args.read_depth,
                mode=args.mode,
                day=args.date,
            )
        except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        for row in rows:
            print(f"  {row['note_id']}  {row['path']}")
        print(f"WROTE {len(rows)} note rows to {ledger_io.display_path(shard, root)}")
        print("next: python3 tools/map_build.py  (re-generates READING_MAP.md §8)")
        return 0

    if args.candidates is not None:
        rows = candidate_rows(view, args.candidates or None, day=args.date, session_id=args.session)
        for row in rows:
            print(json.dumps(row, ensure_ascii=False, sort_keys=True))
        if not args.json:
            print(f"# {len(rows)} candidate rows (nothing written)", file=sys.stderr)
        return 0

    if args.for_id:
        hits = notes_for_id(view, args.for_id)
        if args.json:
            print(json.dumps([{k: v for k, v in h.items() if k != "headings"} for h in hits], ensure_ascii=False, indent=1))
            return 0
        print(f"=== reports referencing {args.for_id}: {len(hits)} ===")
        for entry in hits[: args.limit]:
            print(
                f"  {entry['path']}  [{entry.get('date_real') or entry.get('date_label') or '?'}] "
                f"{entry.get('chars', 0):,}字  {'linked' if entry.get('reachable') else 'ORPHAN'}"
            )
            print(f"      {_one_line(entry.get('title') or '', 100)}")
        if len(hits) > args.limit:
            print(f"  ... {len(hits) - args.limit} more (--limit)")
        return 0 if hits else 1

    if args.orphans:
        found = orphans(view)
        if args.json:
            print(json.dumps([{"path": e["path"], "chars": e.get("chars"), "title": e.get("title")} for e in found], ensure_ascii=False, indent=1))
            return 0
        print(f"=== reports no document links to: {len(found)} of {stats['notes']} ===")
        for entry in found[: args.limit]:
            sessions = ", ".join(entry.get("session_ids") or []) or "no session id"
            print(f"  {entry['path']}  {entry.get('chars', 0):,}字  [{sessions}]")
        if len(found) > args.limit:
            print(f"  ... {len(found) - args.limit} more (--limit)")
        print(
            "  註: 孤立は価値の低さを意味しません。到達手段がファイル名と grep しかないことを示します。"
        )
        return 0

    if args.json:
        print(json.dumps({"stats": stats}, ensure_ascii=False, indent=1))
        return 0
    print_report(view, stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
