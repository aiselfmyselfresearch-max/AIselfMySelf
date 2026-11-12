#!/usr/bin/env python3
"""Measure association and salience in the archive's own read traces.

Human associative memory does not store items, it stores what fires together.
This repository already has the raw material for the same measurement:
``state/read_log*`` records, per session, which record was read and *how*
(``quoted`` / ``summarized`` / ``interpreted`` / ``reinterpreted`` / ``contested``
/ ``used_as_context`` / ``counted``).  Two records activated in the same session
are co-activated; repeated co-activation is what a relation edge should express.

So this tool answers three questions the ledger cannot answer by inspection:

  1. **共起 (co-activation)** — which pairs are read together again and again but
     have no ``relations`` edge?  These are bridging candidates that the archive
     already behaves as if it believed, without having written them down.
  2. **顕著性 (salience)** — which records carry the most interpretive weight,
     counting *how* they were read (a ``contested`` row is not a ``counted`` row)
     and how recently, in the only time axis this archive can trust: ledger
     insertion order.  Dates are not used, because the internal chronology labels
     and the real execution dates disagree (see docs/memory-architecture.md §4).
  3. **減衰 (decay)** — which load-bearing records (``selected`` fragments,
     ``open`` questions nobody has responded to) have not been activated for a
     long stretch of the log?

None of this is an obligation.  ``prompts/start.md`` is explicit that unread
holdings are margin, not debt, and that counts are not success criteria; every
list here is a recommendation the next session may decline, and declining it is
not a liability.  ``used_as_context`` and ``counted`` rows are excluded from
co-activation by default because passing a record through a context window and
counting it in an audit are not acts of association; ``--include-passive`` adds
them back for comparison.

Usage:
  python3 tools/associations.py                       # summary + top lists
  python3 tools/associations.py --co-read --limit 30  # bridging candidates
  python3 tools/associations.py --salience            # activation ranking
  python3 tools/associations.py --decay               # long-unactivated records
  python3 tools/associations.py --write-map           # map/associations.md (untracked)
  python3 tools/associations.py --json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

_ROOT = Path(__file__).resolve().parents[1]
# Put tools/ on sys.path before the flat imports below, so this module works both
# as a script and when a test imports it as ``tools.associations``.
sys.path.insert(0, str(_ROOT / "tools"))

import ledger_io  # noqa: E402
from validate_seed import COLLECTIONS, ROOT  # noqa: E402

# How much interpretive work each ``reading`` value represents.  The ordering is
# the archive's own: contesting or re-reading a record changes a stance, quoting
# or summarising it carries it forward, using it as context does not engage it,
# and counting it in an audit engages nothing but a regular expression.
READING_WEIGHTS: dict[str, float] = {
    "contested": 3.0,
    "reinterpreted": 3.0,
    "interpreted": 2.0,
    "quoted": 1.0,
    "summarized": 1.0,
    "used_as_context": 0.5,
    "counted": 0.25,
}
ACTIVE_READINGS = frozenset({"quoted", "summarized", "interpreted", "reinterpreted", "contested"})
PASSIVE_READINGS = frozenset({"used_as_context", "counted"})

DEFAULT_HALF_LIFE = 500.0  # in read_log rows, not days


def load(root: Path = ROOT) -> dict[str, dict[str, dict[str, Any]]]:
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


# ---------------------------------------------------------------------------
# co-activation
# ---------------------------------------------------------------------------

def _pair_key(left: tuple[str, str], right: tuple[str, str]) -> tuple[tuple[str, str], tuple[str, str]]:
    return (left, right) if left <= right else (right, left)


def _one_line(value: Any, limit: int = 70) -> str:
    """Collapse a title or question to one line so it can sit in a table cell."""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def relation_pairs(data: dict[str, dict[str, dict[str, Any]]]) -> dict[tuple[tuple[str, str], tuple[str, str]], list[str]]:
    """Existing interpretive edges as an undirected pair -> relation ids map."""
    edges: dict[tuple[tuple[str, str], tuple[str, str]], list[str]] = defaultdict(list)
    for relation in data.get("relations", {}).values():
        left, right = relation.get("left"), relation.get("right")
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        lkey = (str(left.get("type")), str(left.get("id")))
        rkey = (str(right.get("type")), str(right.get("id")))
        if lkey == rkey:
            continue
        edges[_pair_key(lkey, rkey)].append(str(relation.get("relation_id")))
    return dict(edges)


def co_read(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    include_passive: bool = False,
    min_sessions: int = 2,
) -> list[dict[str, Any]]:
    """Pairs activated inside one session, aggregated over sessions.

    Insertion order of ``read_log`` (base file, then shards sorted by name) is
    preserved by ``ledger_io``, so the row index is a stable time axis.
    """
    allowed = ACTIVE_READINGS | (PASSIVE_READINGS if include_passive else set())
    by_session: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in data.get("read_log", {}).values():
        reading = row.get("reading")
        target = row.get("target")
        if reading not in allowed or not isinstance(target, dict):
            continue
        session = str(row.get("session_id", ""))
        if not session:
            continue
        key = (str(target.get("type")), str(target.get("id")))
        if key not in by_session[session]:
            by_session[session].append(key)

    sessions_by_pair: dict[Any, set[str]] = defaultdict(set)
    rows_by_pair: Counter[Any] = Counter()
    for session, keys in by_session.items():
        for left, right in itertools.combinations(sorted(keys), 2):
            pair = _pair_key(left, right)
            sessions_by_pair[pair].add(session)
            rows_by_pair[pair] += 1

    edges = relation_pairs(data)
    out: list[dict[str, Any]] = []
    for pair, sessions in sessions_by_pair.items():
        if len(sessions) < min_sessions:
            continue
        out.append(
            {
                "left": {"type": pair[0][0], "id": pair[0][1]},
                "right": {"type": pair[1][0], "id": pair[1][1]},
                "sessions": len(sessions),
                "co_reads": rows_by_pair[pair],
                "bridged": bool(edges.get(pair)),
                "relation_ids": sorted(edges.get(pair, []))[:4],
                "session_ids": sorted(sessions)[:6],
            }
        )
    out.sort(key=lambda item: (-item["sessions"], -item["co_reads"], item["left"]["id"], item["right"]["id"]))
    return out


# ---------------------------------------------------------------------------
# salience and decay
# ---------------------------------------------------------------------------

def activation(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    half_life: float = DEFAULT_HALF_LIFE,
    include_passive: bool = True,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Weighted, recency-decayed activation per record.

    ``decay = 0.5 ** (rows_after_last_read / half_life)``.  The unit is read_log
    rows, deliberately: this archive's ``created_at`` values mix internal
    chronology labels with real execution dates, so a day count would be a
    fiction, while the row order is exactly the order in which sessions wrote.
    """
    rows = list(data.get("read_log", {}).values())
    total = len(rows)
    allowed = ACTIVE_READINGS | (PASSIVE_READINGS if include_passive else set())
    acc: dict[tuple[str, str], dict[str, Any]] = {}
    for index, row in enumerate(rows):
        reading = row.get("reading")
        target = row.get("target")
        if reading not in allowed or not isinstance(target, dict):
            continue
        weight = READING_WEIGHTS.get(str(reading), 0.0)
        decay = 0.5 ** ((total - 1 - index) / half_life) if half_life > 0 else 1.0
        key = (str(target.get("type")), str(target.get("id")))
        entry = acc.setdefault(
            key,
            {
                "type": key[0],
                "id": key[1],
                "rows": 0,
                "active_rows": 0,
                "sessions": set(),
                "by_reading": Counter(),
                "raw_weight": 0.0,
                "salience": 0.0,
                "first_row": index,
                "last_row": index,
            },
        )
        entry["rows"] += 1
        if reading in ACTIVE_READINGS:
            entry["active_rows"] += 1
        entry["sessions"].add(str(row.get("session_id", "")))
        entry["by_reading"][str(reading)] += 1
        entry["raw_weight"] += weight
        entry["salience"] += weight * decay
        entry["last_row"] = index
    for entry in acc.values():
        entry["sessions"] = len(entry["sessions"])
        entry["by_reading"] = dict(entry["by_reading"].most_common())
        entry["rows_since_last_read"] = max(0, total - 1 - entry["last_row"])
        del entry["first_row"]
        del entry["last_row"]
    return acc


def load_bearing(
    data: dict[str, dict[str, dict[str, Any]]],
    acc: dict[tuple[str, str], dict[str, Any]],
    *,
    cold_threshold: float | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Load-bearing records, split into (cold, warm, never-read).

    Load-bearing means the archive's own status marks the record as one a future
    reading is entitled to expect: a ``selected`` or ``held`` fragment, or an
    ``open`` question no ``responds_to`` / ``reframes`` edge has answered.  A
    paused or rejected record is excluded because an editorial overlay already
    retired it — that is forgetting by overlay, and this tool does not undo it.

    The three states are reported separately so that none of them is silently
    folded into another: ``cold`` records were engaged and then went quiet,
    ``warm`` records were engaged recently enough not to be a signal, and
    ``never`` records have no ``read_log`` row at all.  Only ``cold`` is listed
    in full; ``never`` is counted, because prompts/start.md is explicit that
    unread holdings are margin and a long list of them reads as debt.

    The horizon defaults to a quarter of the log (never less than 100 rows) so
    that "long unactivated" scales with the archive instead of being a fixed
    date.  Pass ``cold_threshold`` to override it.
    """
    responded: set[str] = set()
    for relation in data.get("relations", {}).values():
        if relation.get("relation_type") in {"responds_to", "reframes"}:
            right = relation.get("right", {})
            if isinstance(right, dict) and right.get("type") == "question":
                responded.add(str(right.get("id")))

    candidates: list[dict[str, Any]] = []
    for fid, fragment in data.get("fragments", {}).items():
        status = fragment.get("status")
        if status in ("selected", "held"):
            candidates.append(
                {
                    "type": "fragment",
                    "id": fid,
                    "why": str(status),
                    "title": _one_line(fragment.get("title", "")),
                }
            )
    for qid, question in data.get("questions", {}).items():
        if question.get("status", "open") != "open" or qid in responded:
            continue
        candidates.append(
            {
                "type": "question",
                "id": qid,
                "why": "open・未応答",
                "title": _one_line(question.get("question", "")),
            }
        )

    horizon = max(100.0, len(acc) / 4.0) if cold_threshold is None else float(cold_threshold)
    cold: list[dict[str, Any]] = []
    warm: list[dict[str, Any]] = []
    never: list[dict[str, Any]] = []
    for item in candidates:
        entry = acc.get((item["type"], item["id"]))
        item["rows"] = entry["rows"] if entry else 0
        item["active_rows"] = entry["active_rows"] if entry else 0
        item["sessions"] = entry["sessions"] if entry else 0
        item["salience"] = round(entry["salience"], 3) if entry else 0.0
        item["rows_since_last_read"] = entry["rows_since_last_read"] if entry else None
        if entry is None:
            never.append(item)
        elif item["rows_since_last_read"] > horizon:
            cold.append(item)
        else:
            warm.append(item)
    cold.sort(key=lambda item: (-(item["rows_since_last_read"] or 0), item["id"]))
    warm.sort(key=lambda item: (-(item["rows_since_last_read"] or 0), item["id"]))
    never.sort(key=lambda item: (item["type"], item["id"]))
    return cold, warm, never


def summarize(data: dict[str, dict[str, dict[str, Any]]], co: list[dict[str, Any]], acc: dict[Any, dict[str, Any]]) -> dict[str, Any]:
    rows = data.get("read_log", {})
    readings = Counter(str(row.get("reading")) for row in rows.values())
    passive = sum(readings[name] for name in PASSIVE_READINGS)
    unbridged = [item for item in co if not item["bridged"]]
    by_type = Counter(item["type"] for item in acc.values())
    return {
        "read_log_rows": len(rows),
        "by_reading": dict(readings.most_common()),
        "passive_share_pct": round(passive * 100.0 / len(rows), 1) if rows else 0.0,
        "distinct_targets": len(acc),
        "targets_by_type": dict(by_type.most_common()),
        "co_read_pairs_2plus_sessions": len(co),
        "co_read_pairs_bridged": len(co) - len(unbridged),
        "co_read_pairs_unbridged": len(unbridged),
        "relations": len(data.get("relations", {})),
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

CAVEAT = (
    "以下の数値は**推奨であって義務ではありません**。未読は負債ではなく余白であり、"
    "共起の本数・顕著性・減衰を成功条件にしません（`prompts/start.md`・`docs/mode-rotation-triggers.md`）。"
)


def _fmt_target(ref: dict[str, str]) -> str:
    return f"{ref['type']}:{ref['id']}"


def render_report(
    data: dict[str, dict[str, dict[str, Any]]],
    co: list[dict[str, Any]],
    acc: dict[tuple[str, str], dict[str, Any]],
    cold: list[dict[str, Any]],
    warm: list[dict[str, Any]],
    never: list[dict[str, Any]],
    *,
    limit: int = 20,
) -> str:
    stats = summarize(data, co, acc)
    titles: dict[str, str] = {}
    for fid, fragment in data.get("fragments", {}).items():
        titles[fid] = str(fragment.get("title", ""))
    for qid, question in data.get("questions", {}).items():
        titles[qid] = " ".join(str(question.get("question", "")).split())[:70]

    out: list[str] = ["=== association & salience report (read_log-derived) ===", ""]
    out.append(
        f"  read_log            : {stats['read_log_rows']} 行 ／ 対象 {stats['distinct_targets']} 件 "
        f"{stats['targets_by_type']}"
    )
    out.append(f"  読み方の分布        : {stats['by_reading']}")
    out.append(
        f"  受動的な行の割合    : {stats['passive_share_pct']}% "
        "（`used_as_context` ＋ `counted`。共起の既定の分母から除外）"
    )
    out.append(
        f"  共起（≥2セッション）: {stats['co_read_pairs_2plus_sessions']} 対 ／ "
        f"うち関係線あり {stats['co_read_pairs_bridged']} ・**なし {stats['co_read_pairs_unbridged']}**"
    )
    out.append("")

    unbridged = [item for item in co if not item["bridged"]]
    out.append(f"--- 未架橋の強い共起（上位 {min(limit, len(unbridged))} 対） ---")
    for item in unbridged[:limit]:
        left, right = item["left"], item["right"]
        label = " × ".join(
            f"{_fmt_target(ref)}" + (f"『{titles[ref['id']]}』" if ref["id"] in titles else "")
            for ref in (left, right)
        )
        out.append(
            f"  {item['sessions']} セッション ／ {item['co_reads']} 回  {label}"
        )
        out.append(f"      sessions: {', '.join(item['session_ids'])}")
    if not unbridged:
        out.append("  （なし：2セッション以上で共読された対はすべて関係線を持っている）")
    out.append("")

    ranked = sorted(acc.values(), key=lambda entry: -entry["salience"])
    out.append(f"--- 顕著性（salience）上位 {min(limit, len(ranked))} 件 ---")
    for entry in ranked[:limit]:
        title = titles.get(entry["id"], "")
        out.append(
            f"  {entry['salience']:8.2f}  {entry['type']}:{entry['id']}  "
            f"rows={entry['rows']} active={entry['active_rows']} sessions={entry['sessions']} "
            f"since_last={entry['rows_since_last_read']}"
            + (f"  『{title}』" if title else "")
        )
    out.append("")

    out.append(f"--- かつて読まれ、その後沈黙している荷重記録（上位 {min(limit, len(cold))} 件） ---")
    for item in cold[:limit]:
        title = titles.get(item["id"], "") or item.get("title", "")
        out.append(
            f"  {item['rows_since_last_read']:>6} 行前  {item['type']}:{item['id']} [{item['why']}] "
            f"rows={item['rows']} sessions={item['sessions']} salience={item['salience']}"
            + (f"  『{title[:60]}』" if title else "")
        )
    if not cold:
        out.append("  （なし）")
    out.append(
        f"- **最近読まれた荷重記録（warm）**: {len(warm)} 件 — 減衰の閾値の内側にあるため、"
        "信号として一覧化しません。"
    )
    never_by_why = Counter(item["why"] for item in never)
    out.append(
        f"- **一度も read_log 行がない荷重記録**: {len(never)} 件 {dict(never_by_why.most_common())}"
        " — 件数だけを示します。未読は負債ではなく余白なので、一覧化して返済すべき目録のように見せないようにしています。"
    )
    out.append("")
    out.append("  時間軸は read_log の挿入順（行数）です。日付は内部編年ラベルと実日付がずれるため使っていません。")
    out.append(f"  {CAVEAT}")
    return "\n".join(out) + "\n"


def render_map(
    data: dict[str, dict[str, dict[str, Any]]],
    co: list[dict[str, Any]],
    acc: dict[tuple[str, str], dict[str, Any]],
    cold: list[dict[str, Any]],
    warm: list[dict[str, Any]],
    never: list[dict[str, Any]],
    *,
    limit: int = 100,
) -> str:
    stats = summarize(data, co, acc)
    out = [
        "# 連想と顕著性の地図（read_log 由来・生成物）",
        "",
        "> `tools/associations.py` が `state/read_log*` と `state/relations*` から生成します（git 管理外）。",
        f"> {CAVEAT}",
        "",
        "## 0. 集計",
        "",
        "| 指標 | 値 |",
        "|---|---:|",
        f"| read_log 行数 | {stats['read_log_rows']:,} |",
        f"| 活性化した対象 | {stats['distinct_targets']:,} |",
        f"| 共起（≥2セッション） | {stats['co_read_pairs_2plus_sessions']:,} 対 |",
        f"| うち関係線あり | {stats['co_read_pairs_bridged']:,} |",
        f"| うち未架橋 | {stats['co_read_pairs_unbridged']:,} |",
        f"| relations 総数 | {stats['relations']:,} |",
        f"| 受動的行の割合 | {stats['passive_share_pct']}% |",
        "",
        "## 1. 未架橋の共起（関係線の候補）",
        "",
        "| セッション数 | 共読回数 | 左 | 右 | 共読したセッション |",
        "|---:|---:|---|---|---|",
    ]
    for item in [entry for entry in co if not entry["bridged"]][:limit]:
        out.append(
            f"| {item['sessions']} | {item['co_reads']} | `{_fmt_target(item['left'])}` | "
            f"`{_fmt_target(item['right'])}` | {', '.join(item['session_ids'])} |"
        )
    out.extend(
        [
            "",
            "## 2. 顕著性（重み×減衰）上位",
            "",
            "| salience | 対象 | 行数 | 能動行 | セッション | 最終読了からの行数 | 読み方の内訳 |",
            "|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for entry in sorted(acc.values(), key=lambda item: -item["salience"])[:limit]:
        breakdown = ", ".join(f"{k}{v}" for k, v in entry["by_reading"].items())
        out.append(
            f"| {entry['salience']:.2f} | `{entry['type']}:{entry['id']}` | {entry['rows']} | "
            f"{entry['active_rows']} | {entry['sessions']} | {entry['rows_since_last_read']} | {breakdown} |"
        )
    out.extend(
        [
            "",
            "## 3. かつて読まれ、その後沈黙している荷重記録",
            "",
            "| 最終読了からの行数 | 対象 | 理由 | salience | 行数 | セッション数 |",
            "|---:|---|---|---:|---:|---:|",
        ]
    )
    for item in cold[:limit]:
        out.append(
            f"| {item['rows_since_last_read']} | `{item['type']}:{item['id']}` | "
            f"{item['why']} | {item['salience']} | {item['rows']} | {item['sessions']} |"
        )
    never_by_why = Counter(item["why"] for item in never)
    out.extend(
        [
            "",
            f"直近に読まれた荷重記録（warm）は **{len(warm)} 件**。減衰の閾値の内側なので一覧化しない。",
            f"一度も read_log 行がない荷重記録は **{len(never)} 件**（{dict(never_by_why.most_common())}）。"
            "未読は負債ではなく余白なので一覧化しない。",
        ]
    )
    out.extend(["", "## 4. 重みと減衰の定義", ""])
    out.append("| reading | 重み |")
    out.append("|---|---:|")
    for name, weight in sorted(READING_WEIGHTS.items(), key=lambda pair: -pair[1]):
        out.append(f"| `{name}` | {weight} |")
    out.extend(
        [
            "",
            f"- 減衰: `0.5 ** (最終読了から経過した行数 / half_life)`、既定 half_life = {DEFAULT_HALF_LIFE:.0f} 行。",
            "- 荷重記録の定義: FRAG が `selected` または `held`、Q が `open` かつ `responds_to`/`reframes` で応答済みでないもの。"
            "`paused`/`rejected` は編集判断のオーバーレイで既に退いており、この計測はそれを打ち消しません。",
            "- 沈黙の閾値（cold）: `max(100, 活性化した対象数 / 4)` 行。アーカイブの大きさに従って伸びる相対値で、固定日付ではありません。",
            "- 時間軸は read_log の挿入順（base → シャード名順）。`created_at` は内部編年ラベルと実日付が混在するため使わない。",
            "- 共起の既定の分母は能動的な読み（quoted/summarized/interpreted/reinterpreted/contested）のみ。",
            "",
        ]
    )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--co-read", action="store_true", help="list co-activation pairs")
    parser.add_argument("--salience", action="store_true", help="rank records by weighted activation")
    parser.add_argument("--decay", action="store_true", help="list long-unactivated load-bearing records")
    parser.add_argument("--include-passive", action="store_true", help="count used_as_context/counted as co-activation")
    parser.add_argument("--min-sessions", type=int, default=2, help="co-activation threshold (default 2)")
    parser.add_argument("--half-life", type=float, default=DEFAULT_HALF_LIFE, help="decay half-life in read_log rows")
    parser.add_argument("--bridged", action="store_true", help="also list pairs that already have a relation")
    parser.add_argument("--limit", type=int, default=20, help="rows to print per list")
    parser.add_argument("--map-dir", type=Path, default=ROOT / "map", help="output directory for --write-map")
    parser.add_argument("--write-map", action="store_true", help="write map/associations.md (untracked)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        data = load(args.root.resolve())
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    co = co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions)
    if not args.bridged:
        co = [item for item in co if not item["bridged"]]
    acc = activation(data, half_life=args.half_life, include_passive=True)
    cold, warm, never = load_bearing(data, acc)

    if args.write_map:
        map_dir = Path(args.map_dir)
        map_dir.mkdir(parents=True, exist_ok=True)
        text = render_map(
            data,
            co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions),
            acc,
            cold,
            warm,
            never,
            limit=max(args.limit, 100),
        )
        ledger_io.atomic_write_text(map_dir / "associations.md", text)
        print(f"WROTE {map_dir / 'associations.md'} ({len(text.encode('utf-8')):,} bytes, not tracked)")
        return 0

    if args.json:
        payload = {
            "stats": summarize(
                data, co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions), acc
            ),
            "weights": READING_WEIGHTS,
            "half_life": args.half_life,
        }
        if args.co_read or not (args.salience or args.decay):
            payload["co_read"] = co[: args.limit]
        if args.salience:
            payload["salience"] = sorted(acc.values(), key=lambda item: -item["salience"])[: args.limit]
        if args.decay:
            payload["cold"] = cold[: args.limit]
            payload["warm_total"] = len(warm)
            payload["never_read_counts"] = dict(Counter(item["why"] for item in never))
            payload["never_read_total"] = len(never)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if args.co_read:
        print(f"=== co-activation pairs (≥{args.min_sessions} sessions, bridged={args.bridged}) ===")
        for item in co[: args.limit]:
            print(
                f"  {item['sessions']} sessions ／ {item['co_reads']} co-reads  "
                f"{_fmt_target(item['left'])} × {_fmt_target(item['right'])}  "
                f"[{'bridged' if item['bridged'] else 'UNBRIDGED'}]"
            )
        print(f"  {CAVEAT}")
        return 0

    if args.salience:
        print(f"=== salience (weights × decay, half-life {args.half_life:.0f} rows) ===")
        for entry in sorted(acc.values(), key=lambda item: -item["salience"])[: args.limit]:
            print(
                f"  {entry['salience']:8.2f}  {entry['type']}:{entry['id']}  "
                f"rows={entry['rows']} active={entry['active_rows']} sessions={entry['sessions']} "
                f"since_last={entry['rows_since_last_read']}"
            )
        print(f"  {CAVEAT}")
        return 0

    if args.decay:
        print("=== load-bearing records that went cold (rows since last read) ===")
        for item in cold[: args.limit]:
            print(
                f"  {item['rows_since_last_read']:>6}  {item['type']}:{item['id']} "
                f"[{item['why']}] rows={item['rows']} sessions={item['sessions']} "
                f"salience={item['salience']}"
            )
        never_by_why = Counter(item["why"] for item in never)
        print(f"  never read: {len(never)} records {dict(never_by_why.most_common())} (margin, not debt)")
        print(f"  {CAVEAT}")
        return 0

    sys.stdout.write(
        render_report(
            data,
            co_read(data, include_passive=args.include_passive, min_sessions=args.min_sessions),
            acc,
            cold,
            warm,
            never,
            limit=args.limit,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
