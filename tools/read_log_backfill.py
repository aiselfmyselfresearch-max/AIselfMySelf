#!/usr/bin/env python3
"""Fill and check ``state/read_log.d/`` rows derived from the sessions ledger.

背景（docs/map-architecture.md §7・README「編集規約」）:
台帳は「何を集めたか」（素材）と「どう解釈したか」（関係）を記録するが、
「どの記録を・どのセッションが・どう読み返したか」という網羅的な痕跡は持たない。
read_log はその痕跡のための追記専用コレクションで、このスクリプトはうち
機械的に確定できる部分——各セッションの ``context_material_ids``——を転記する。

- ``--check``  : (セッション, 文脈素材) の全ペアに read_log 行があるかを確認する。
                 欠落があれば exit 1（新セッションが読みの痕跡を書き忘れた合図）。
- ``--write``  : 欠落ペアだけに ``reading="used_as_context"`` の行を新しい
                 セッション用シャードへ追記する（冪等。既存行は触らない）。

``--check`` は**二層**を別々に報告する（2026-11-10 に追加）。層2 の強制は
``--since`` ＋ ``--enforce`` の二段構えである（同日、A案の段階1 として追加）。

- ``--since YYYY-MM-DD``：層2 を発効日以降／以前に分けて表示する。**これだけでは落とさない。**
- ``--since D --enforce``：発効日以降で未充足（手書き行も ``未読の選択:`` も無い）ペアがあれば exit 1。

判定器は ``session_id`` の YYYYMMDD（``tools/new_id.py`` の実日付採番）を第一に、
次に ``started_at[:10]``、どちらも取れなければ**免除**とする。``started_at`` には未来の
内部編年ラベルが混在しており、それを適格にすると規則が空になるため、この順序にしてある
（実測：``started_at`` 方式では適格 4/632、``session_id`` 方式では 109/632）。


- **層1 接触**：各セッションの ``context_material_ids`` に read_log の行があるか。
  行の種類は問わない（機械的バックフィルを含む）。**失敗すると exit 1。**
- **層2 読書**：同じペアに**手書き**の読み（上記6種）があるか。
  **失敗にしない。数値として表示するだけである。**

層2 を落とさないのは、落とすと 2,000 件を超える過去ペアに事後記入が要り、
「読んでいないものに読んだと書く」誘因を作るためである（実測は
``readings/2027-03-14-counting-the-remainder.md`` §2 と、本スクリプトの
2026-11-10 変更の根拠）。層2 の数値は CI のログに毎回出る。

手で書く読み（quoted / summarized / interpreted / reinterpreted / contested /
counted）はこのスクリプトの対象外。手書き行が既にあるペアには何も追加しない。

使い方::

    python3 tools/read_log_backfill.py --check
    python3 tools/read_log_backfill.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io
import new_id
import new_ledger_shard
from validate_seed import COLLECTIONS, ROOT, load_jsonl

NOTE = (
    "機械的バックフィル：session.context_material_ids からの転記。"
    "読解の詳細は各セッションの精読報告・台帳 notes を参照"
)

#: readings that record an act of reading, as opposed to ``used_as_context``,
#: which records only that a material was in a session's context list.
HANDWRITTEN_READINGS = frozenset(
    {"quoted", "summarized", "interpreted", "reinterpreted", "contested", "counted"}
)


def load(root: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (sessions, read_log) ID maps for the union view under ``root``."""
    errors: list[str] = []
    sessions = load_jsonl(root / "state" / "sessions.jsonl", "session_id", errors)
    read_log = load_jsonl(root / "state" / "read_log.jsonl", "read_id", errors)
    if errors:
        raise ValueError("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return sessions, read_log


def derived_pairs(sessions: dict[str, dict]) -> set[tuple[str, str]]:
    """Every (session_id, material_id) pair the sessions ledger vouches for."""
    pairs: set[tuple[str, str]] = set()
    for session_id, record in sessions.items():
        for material_id in record.get("context_material_ids") or []:
            pairs.add((session_id, material_id))
    return pairs


def covered_pairs(read_log: dict[str, dict]) -> set[tuple[str, str]]:
    """Every (session_id, material_id) pair that already has at least one read row."""
    pairs: set[tuple[str, str]] = set()
    for record in read_log.values():
        target = record.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        session_id = record.get("session_id")
        material_id = target.get("id")
        if isinstance(session_id, str) and isinstance(material_id, str):
            pairs.add((session_id, material_id))
    return pairs


def handwritten_pairs(read_log: dict[str, dict]) -> set[tuple[str, str]]:
    """Pairs with at least one *hand-written* reading row (layer 2)."""
    pairs: set[tuple[str, str]] = set()
    for record in read_log.values():
        if record.get("reading") not in HANDWRITTEN_READINGS:
            continue
        target = record.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        session_id = record.get("session_id")
        material_id = target.get("id")
        if isinstance(session_id, str) and isinstance(material_id, str):
            pairs.add((session_id, material_id))
    return pairs


def missing_pairs(sessions: dict[str, dict], read_log: dict[str, dict]) -> list[tuple[str, str]]:
    return sorted(derived_pairs(sessions) - covered_pairs(read_log))


_SID_DATE = re.compile(r"SESSION-(\d{4})(\d{2})(\d{2})-")


def session_date(session_id: str, record: dict) -> date | None:
    """The real date a session started, or ``None`` if it cannot be established.

    ``session_id`` first: ``tools/new_id.py`` stamps it from the real date.
    ``started_at`` second: it may carry a future internal-chronology label.

    In both cases **a future date is not a date**.  Measured 2026-11-10: 102 of
    632 session IDs already carry a future internal label (``SESSION-20270220-…``),
    so accepting a future ID date would both credit the rule with sessions that
    have not happened and turn the internal chronology into a compliance record.
    Anything that cannot be resolved is exempt — an unparsable timestamp must not
    manufacture a violation.
    """
    match = _SID_DATE.match(session_id)
    if match:
        try:
            stamped = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            stamped = None
        if stamped is not None and stamped <= date.today():
            return stamped
    value = record.get("started_at")
    if isinstance(value, str) and value:
        try:
            parsed = date.fromisoformat(value[:10])
        except ValueError:
            return None
        return parsed if parsed <= date.today() else None
    return None


_UNREAD = re.compile(
    r"未読の選択\s*[:：]\s*(?P<ids>MAT-[A-Za-z0-9-]+(?:[、,]\s*MAT-[A-Za-z0-9-]+)*)"
)


def unread_choices(sessions: dict[str, dict]) -> set[tuple[str, str]]:
    """(session, material) pairs a session explicitly recorded as not read.

    The ID pattern is case-insensitive on purpose: ``MAT-[A-Z0-9-]+`` misses IDs
    containing lower-case hex, which was 2,482 of 3,243 materials on 2026-11-06
    (see ``prompts/start.md``).  Class-name fragments such as
    ``MAT-LIT-20261024-`` are dropped because they do not resolve to a material.
    """
    pairs: set[tuple[str, str]] = set()
    for session_id, record in sessions.items():
        notes = record.get("notes")
        if not isinstance(notes, str):
            continue
        for match in _UNREAD.finditer(notes):
            for raw in re.split(r"[、,]", match.group("ids")):
                material_id = raw.strip()
                if re.fullmatch(r"MAT-[A-Za-z0-9-]*[0-9a-f][A-Za-z0-9-]*", material_id) and material_id[-1] != "-":
                    pairs.add((session_id, material_id))
    return pairs


def since_report(
    sessions: dict[str, dict],
    read_log: dict[str, dict],
    since: date,
) -> tuple[int, int, int, int, list[tuple[str, str]]]:
    """Return (eligible_pairs, hand_covered, unread_excused, exempt_sessions, unmet)."""
    hand = handwritten_pairs(read_log)
    excused = unread_choices(sessions)
    eligible = 0
    covered = 0
    used_excuse = 0
    exempt = 0
    unmet: list[tuple[str, str]] = []
    for session_id, record in sessions.items():
        started = session_date(session_id, record)
        if started is None or started < since:
            exempt += 1
            continue
        context = record.get("context_material_ids") or []
        if not context:
            exempt += 1
            continue
        for material_id in context:
            pair = (session_id, material_id)
            eligible += 1
            if pair in hand:
                covered += 1
            elif pair in excused:
                covered += 1
                used_excuse += 1
            else:
                unmet.append(pair)
    return eligible, covered, used_excuse, exempt, sorted(unmet)


def check(root: Path, since: date | None = None, enforce: bool = False) -> int:
    sessions, read_log = load(root)
    missing = missing_pairs(sessions, read_log)
    total = len(derived_pairs(sessions))

    # --- layer 1: contact. This is the gate. ---
    print(
        "read_log coverage: {covered}/{total} (session, context material) pairs".format(
            covered=total - len(missing), total=total
        )
    )
    gate_failed = bool(missing)
    if missing:
        print(f"FAIL: {len(missing)} pairs have no read_log row; run tools/read_log_backfill.py --write")
        for session_id, material_id in missing[:10]:
            print(f"  - {session_id} -> {material_id}")
        if len(missing) > 10:
            print(f"  - … and {len(missing) - 10} more")
    else:
        print("PASS: every session context material has a read_log row")

    # --- layer 2: reading. Reported, never gated. ---
    hand = handwritten_pairs(read_log)
    derived = derived_pairs(sessions)
    hand_covered = len(derived & hand)
    rate = (hand_covered / total) if total else 0.0
    print(
        "read_log layer2 (hand-written reading): {c}/{t} pairs = {r:.1f}%".format(
            c=hand_covered, t=total, r=rate * 100
        )
    )
    if since is None:
        print(
            "  note: layer2 is informational and never fails this check. "
            "A context-only row means the material was in the session's context list, "
            "not that it was read. See docs/parallel-work.md."
        )
        return 1 if gate_failed else 0

    # --- layer 2 since the effective date. Enforced only with --enforce. ---
    eligible, covered, excused, exempt, unmet = since_report(sessions, read_log, since)
    rate = (covered / eligible) if eligible else 0.0
    print(
        "read_log layer2 since {d}: {c}/{e} pairs = {r:.1f}%".format(
            d=since.isoformat(), c=covered, e=eligible, r=rate * 100
        )
    )
    print(f"  eligible sessions: {len(sessions) - exempt}   exempt: {exempt}")
    print(f"  excused by 未読の選択: {excused}")
    if not enforce:
        print(
            "  note: --since alone never fails. Add --enforce to make unmet pairs "
            "exit 1 (this is how the rule takes effect, not by writing a date)."
        )
        if unmet:
            print(f"  unmet (not yet enforced): {len(unmet)}")
        return 1 if gate_failed else 0
    if unmet:
        print(f"FAIL: {len(unmet)} pairs since {since.isoformat()} have neither a hand-written reading nor 未読の選択")
        for session_id, material_id in unmet[:10]:
            print(f"  - {session_id} -> {material_id}")
        if len(unmet) > 10:
            print(f"  - … and {len(unmet) - 10} more")
        print("  remedy: write a hand-written read_log row, or add `未読の選択: <id>` to sessions.notes")
        return 1
    print("PASS: every eligible pair since the effective date is accounted for")
    return 1 if gate_failed else 0


def _id_stamp(created_at: str) -> str | None:
    """Extract YYYYMMDD from ``created_at`` for the ID stamp, if it starts with a date."""
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", created_at)
    return "".join(match.groups()) if match else None


def _row_date(started_at: object, today: date) -> str:
    """The date to stamp on a backfilled row.

    ``started_at`` is provenance, and a future one is an internal chronology
    label rather than a date (see ``tools/date_axis.py``).  Minting an ID from it
    would put the row on a day that has not happened, so the row is dated the day
    the backfill actually wrote it.  What the row asserts — "this session had this
    material in context" — is true either way; only the timestamp changes owner.
    """
    if isinstance(started_at, str) and started_at:
        try:
            if date.fromisoformat(started_at[:10]) <= today:
                return started_at
        except ValueError:
            pass
    return today.isoformat()


def write(root: Path, today: date | None = None) -> int:
    today = today or date.today()
    sessions, read_log = load(root)
    missing = missing_pairs(sessions, read_log)
    if not missing:
        print("WROTE nothing: every (session, context material) pair already has a read_log row")
        return 0

    taken = set(read_log)
    rows: list[dict] = []
    for session_id, material_id in missing:
        created_at = _row_date(sessions[session_id].get("started_at"), today)
        read_id = new_id.mint("READ", day=_id_stamp(created_at), taken=taken)
        taken.add(read_id)
        rows.append(
            {
                "read_id": read_id,
                "session_id": session_id,
                "target": {"type": "material", "id": material_id},
                "reading": "used_as_context",
                "note": NOTE,
                "created_at": created_at,
            }
        )

    shard = new_ledger_shard.create_shard("read_log", root=root)
    body = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    with ledger_io.exclusive_lock(root / "state" / "read_log.jsonl"):
        ledger_io.atomic_write_text(shard, body)
    print(f"WROTE {len(rows)} read_log rows to {shard}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify coverage; exit 1 on gaps")
    parser.add_argument(
        "--since",
        help="effective date (YYYY-MM-DD) for the layer-2 rule; report layer 2 from this date on",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="with --since: exit 1 when a pair since that date has neither a hand-written reading nor 未読の選択",
    )
    mode.add_argument("--write", action="store_true", help="append rows for uncovered pairs")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    parser.add_argument("--today", help="write-side reference date (default: today; tests pin it)")
    args = parser.parse_args(argv)

    # New collections are wired through validate_seed.COLLECTIONS.
    if "read_log" not in COLLECTIONS:
        print("error: read_log collection is not registered in validate_seed.COLLECTIONS", file=sys.stderr)
        return 2

    try:
        today = date.fromisoformat(args.today) if args.today else None
        since = date.fromisoformat(args.since) if args.since else None
        if args.enforce and since is None:
            print("error: --enforce requires --since", file=sys.stderr)
            return 2
        if args.check:
            return check(args.root, since=since, enforce=args.enforce)
        return write(args.root, today=today)
    except (ValueError, OSError, ledger_io.LedgerBusy) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
