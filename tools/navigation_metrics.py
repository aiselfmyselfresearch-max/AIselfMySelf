#!/usr/bin/env python3
"""How the archive walks itself: six measurements deferred by a close reading.

Why this file exists
--------------------
``COGNITIVE_SCIENCE_REPORT_2026-11-23-E.md`` §7 lists nine things that session
did not do.  Five of them (items 1-5) need no new source: they are questions
about the archive's own rows, and the answers were available the moment the
questions were written down.  They were deferred anyway, and a deferred
measurement that nobody instruments is a measurement that quietly never
happens.  This tool is the instrument, so each number in the continuation
report is reproducible by one command instead of by a script that lived in a
chat transcript.

What each flag measures, and the §7 item it discharges
------------------------------------------------------
``--gate`` (item 2, the direct test of ``HYP-20261120-58ddce``'s exclusion
clause (1)).  The clause is falsified if verbatim shard rows that appear in no
index or gist are re-used by later sessions at a *uniform* probability, i.e. if
reachability does not depend on the index layer.  Three designs are reported,
because one design cannot separate "the index makes a row reachable" from "a
row worth indexing is a row worth re-reading":

  * cross-sectional -- over materials already work-read at least once, compare
    the re-read rate of those that had a judgment-layer reference before the
    session day with those that had none.  Confounded: importance drives both.
  * paired within-material -- for each material, split its own timeline at the
    date of its *first* judgment-layer reference and compare re-reads per
    session before and after.  The material is held fixed, so anything that is
    constant about it (topic, quality, verification depth) is controlled.  What
    is *not* controlled: a first reference is usually written by a session that
    has just read the row, so the "after" window opens next to a reading.
  * never-indexed reference -- the re-read rate of materials that appear in no
    judgment-layer record at all.

``--productivity`` (item 1).  Sessions whose ``read_log`` opens on a note
against sessions whose ``read_log`` opens on a material: evaluations, claims,
report bytes, contact rows per session.  Reported twice, once pooled and once
stratified by ``notes.mode``, because the two groups do not have the same task
composition and the pooled difference is mostly that composition.  The
stratified test is Cochran-Mantel-Haenszel on "produced at least one
evaluation".

``--series`` (item 5, Siegel & White's developmental sequence turned on the
archive).  Microgenesis: the median rank at which each reference type is first
touched inside a session.  Ontogeny: the earliest dated row of each collection.
Spearman's rho over the types both orders contain.  A high rho would mean the
archive grows in a session the way it grew in history; a low one means the two
orders are different facts.

``--errata`` (item 4, the "staircase" candidates).  Hölscher et al. (2006)
found 6 of 17 getting-lost episodes directly after a stairway and 5 of 17 in
basement dead ends: losses cluster at transitions, not along corridors.  The
archive has three candidate transitions -- the day boundary between shards, the
integration recorded in ``state/shard_aliases.json``, and the unordered hash
part of an id.  For each, the errata corpus (412 rows with a ``verdict``) gives
an error measure.  The hash part is the negative control: it carries no order,
so a gradient there would mean the measure is an artefact.  Incidence is
reported per 1,000 rows, because a verdict composition alone cannot tell a
high-error region from a heavily-audited one.

``--roles`` (item 3).  Rieser (1989) separates the cost of a rotation from the
cost of a translation; the archive's counterpart is whether re-reading the same
material under a different ``assigned_role`` costs anything.  First question is
sample size, so the tool reports the sample, the observed difference, the
minimum difference it could detect at 80% power, and the per-arm n that the
observed difference would need.

``--siblings`` (item 6's archive-side half).  Whether same-day parallel
sessions partition the materials they touch, which is what
``docs/parallel-work.md`` §3 asks of them.

Nothing here writes.  Standard library only.
"""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_ids  # noqa: E402  (one id recogniser for the whole repository)

ROOT = Path(__file__).resolve().parent.parent

# schema/read_log.schema.json: the six kinds that record work done to a target,
# as against the two that record mere contact.  tools/preservation_layers.py
# draws the same line (its layer 2); the split is copied, not re-derived.
WORK_READINGS = frozenset(
    {"quoted", "summarized", "interpreted", "reinterpreted", "contested", "counted"}
)
CONTACT_READINGS = frozenset({"used_as_context", "declined"})

# Collections whose rows are judgments about other rows.  A material named by
# any of these is "in the index layer": it is reachable without scanning the
# verbatim shards.  read_log is deliberately absent -- a contact row is a trace
# of a reading, not a judgment, and including it would make the gate circular.
JUDGMENT_SOURCES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("hypotheses", ("supporting_material_ids", "counter_material_ids"), "hypothesis_id"),
    ("evaluations", ("material_ids",), "evaluation_id"),
    ("questions", ("material_ids",), "question_id"),
    ("fragments", ("material_ids",), "fragment_id"),
    ("motifs", ("material_ids",), "motif_id"),
)


# ---------------------------------------------------------------------------
# plumbing
# ---------------------------------------------------------------------------
def _day(token: str) -> str:
    """YYYYMMDD from a dated ledger id, or '' (ledger_ids owns the form)."""
    m = ledger_ids.DATE_FORM_RE.match(token or "")
    return "".join(m.groups()[:3]) if m else ""


def _iso_day(value: Any) -> str:
    """YYYYMMDD from an ISO date/datetime string, or ''."""
    if not isinstance(value, str):
        return ""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    return "".join(m.groups()) if m else ""


def load(root: Path, collection: str) -> list[dict[str, Any]]:
    """Every row of one collection: the seed file plus all of its shards."""
    out: list[dict[str, Any]] = []
    paths = [root / "state" / f"{collection}.jsonl"]
    paths += sorted(Path(p) for p in glob.glob(str(root / "state" / f"{collection}.d" / "*.jsonl")))
    for path in paths:
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    out.append(json.loads(line))
    return out


def row_day(row: dict[str, Any], id_key: str) -> str:
    """The row's own day: created_at when it has one, else its id's day."""
    return _iso_day(row.get("created_at")) or _day(row.get(id_key, ""))


def chi2_yates(a: int, b: int, c: int, d: int) -> float:
    """Yates-corrected chi-square for a 2x2 table [[a,b],[c,d]]."""
    n = a + b + c + d
    denom = (a + b) * (c + d) * (a + c) * (b + d)
    if not n or not denom:
        return float("nan")
    return (abs(a * d - b * c) - n / 2) ** 2 * n / denom


def welch_t(x: list[float], y: list[float]) -> float:
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    se = math.sqrt(statistics.variance(x) / len(x) + statistics.variance(y) / len(y))
    if not se:
        return float("nan")
    return (statistics.mean(x) - statistics.mean(y)) / se


def spearman(pairs: Iterable[tuple[float, float]]) -> tuple[float, int]:
    """Spearman rho with average ranks for ties."""
    xs, ys = zip(*list(pairs)) if pairs else ((), ())
    n = len(xs)
    if n < 3:
        return float("nan"), n

    def ranks(values: tuple[float, ...]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (num / den if den else float("nan")), n


class Ledger:
    """The rows this tool needs, read once."""

    def __init__(self, root: Path, exclude: tuple[str, ...] = ()) -> None:
        self.root = Path(root)
        self.exclude = frozenset(exclude)
        self.materials = {r["material_id"]: r for r in load(self.root, "materials")}
        self.sessions = {
            r["session_id"]: r
            for r in load(self.root, "sessions")
            if r["session_id"] not in self.exclude
        }
        self.read_log = [
            r for r in load(self.root, "read_log") if r.get("session_id") not in self.exclude
        ]
        self.notes = [n for n in load(self.root, "notes") if n.get("session_id") not in self.exclude]
        self.evaluations = [
            e for e in load(self.root, "evaluations") if e.get("session_id") not in self.exclude
        ]
        self.errata = load(self.root, "errata")
        self.session_day = {sid: _day(sid) for sid in self.sessions}
        self.sessions_by_day: dict[str, list[str]] = defaultdict(list)
        for sid, day in self.session_day.items():
            if day:
                self.sessions_by_day[day].append(sid)
        for day in self.sessions_by_day:
            self.sessions_by_day[day].sort()
        self.days = sorted(self.sessions_by_day)

    # -- work readings, indexed by material ---------------------------------
    def work_reads(self) -> dict[str, list[tuple[str, str, str]]]:
        """material -> [(day, session_id, read_id)] of work rows."""
        out: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        for row in self.read_log:
            target = row.get("target") or {}
            if target.get("type") != "material" or row.get("reading") not in WORK_READINGS:
                continue
            mid = target.get("id")
            sid = row.get("session_id")
            if mid in self.materials and sid in self.sessions:
                out[mid].append((self.session_day[sid], sid, row.get("read_id", "")))
        for mid in out:
            out[mid].sort()
        return dict(out)

    def by_session(self) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in self.read_log:
            if row.get("session_id") in self.sessions:
                out[row["session_id"]].append(row)
        return dict(out)

    # -- the judgment-layer index -------------------------------------------
    def index_references(self) -> list[tuple[str, str, str]]:
        """(day, material_id, source collection) for every judgment-layer reference."""
        refs: list[tuple[str, str, str]] = []

        def push(day: str, mid: Any, source: str) -> None:
            if isinstance(mid, str) and mid in self.materials and day:
                refs.append((day, mid, source))

        for note in self.notes:
            day = row_day(note, "note_id")
            for claim in note.get("claims") or []:
                for mid in claim.get("material_ids") or []:
                    push(day, mid, "notes")
        for collection, fields, id_key in JUDGMENT_SOURCES:
            for row in load(self.root, collection):
                day = row_day(row, id_key)
                for field in fields:
                    for mid in row.get(field) or []:
                        push(day, mid, collection)
                if collection == "motifs":
                    day = day or _day(row.get(id_key, ""))
        for row in load(self.root, "relations"):
            day = row_day(row, "relation_id")
            for side in ("left", "right"):
                value = row.get(side)
                if isinstance(value, str):
                    push(day, value, "relations")
                elif isinstance(value, dict):
                    for key in ("id", "material_id"):
                        push(day, value.get(key), "relations")
        refs.sort()
        return refs

    def first_index_day(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for day, mid, _ in self.index_references():
            if mid not in out or day < out[mid]:
                out[mid] = day
        return out


# ---------------------------------------------------------------------------
# item 2 -- does the index layer gate re-reading?
# ---------------------------------------------------------------------------
def measure_gate(led: Ledger, cut_margin_days: int, min_exposure: int, gap_days: int = 0, lag_days: int = 0) -> None:
    """Item 2.  Re-use means a work reading dated after the material's first work
    reading, so a row acquired on one day and first read on the next is not
    counted as re-used.  Sessions are ordered by the day in their id, which for
    the forward-dated part of the ledger is the internal chronology, not the
    real execution date; the window edge is therefore taken from the last
    session day and reported, not assumed."""
    reads = led.work_reads()
    first_index = led.first_index_day()
    first_read = {m: min(e[0] for e in ev) for m, ev in reads.items() if ev}
    last_day = led.days[-1] if led.days else ""
    cut = _shift(last_day, -cut_margin_days)
    # prefix sums over session days: how many sessions fall after a given day
    day_counts = [(d, len(v)) for d, v in sorted(led.sessions_by_day.items())]
    cum: list[tuple[str, int]] = []
    running = 0
    for day, count in day_counts:
        running += count
        cum.append((day, running))
    total_sessions = running

    def sessions_after(day: str) -> int:
        import bisect

        keys = [d for d, _ in cum]
        i = bisect.bisect_right(keys, day)
        return total_sessions - (cum[i - 1][1] if i else 0)

    print("=== item 2 / HYP-20261120-58ddce 反証条件(1): 索引は再利用をゲートするか ===")
    print(f"  最終セッション日 {last_day}、素材側の縁 {cut}（{cut_margin_days}日前より古い素材のみ）")
    print("  定義: 再利用 = 最初の手読みより後の日付の手読み。索引 = 判断層（notes の claims・")
    print("        hypotheses・evaluations・questions・fragments・motifs・relations）が素材を指すこと。")

    # ---- cross-sectional: already read once, then indexed or not -------------
    a = b = c = d = 0
    universe = 0
    for mid in sorted(reads):
        fday = first_read.get(mid, "")
        if not fday or fday > cut or _day(mid) > cut:
            continue
        universe += 1
        iday = first_index.get(mid, "")
        lo = _shift(fday, max(lag_days, 1))          # a re-use at least lag_days later
        touched = {e[1] for e in reads[mid] if e[0] >= lo}
        n_after = sessions_after(_shift(lo, -1))      # sessions on or after lo
        if iday:
            gate = max(lo, _shift(iday, 1))           # the index must predate the session
            indexed_after = sessions_after(_shift(gate, -1))
            a_local = sum(1 for sid in touched if led.session_day[sid] >= gate)
        else:
            gate = lo
            indexed_after = 0
            a_local = 0
        c_local = len(touched) - a_local
        b_local = indexed_after - a_local
        d_local = n_after - a_local - b_local - c_local
        a += a_local
        b += b_local
        c += c_local
        d += d_local
    n = a + b + c + d
    print(f"  [横断] 一度は手読み済みの素材 {universe} 件 × それ以降のセッション（lag>={max(lag_days,1)}日、対 {n:,}）")
    print(f"    索引あり {a:,}/{a + b:,} = {_pct(a, a + b)}   索引なし {c:,}/{c + d:,} = {_pct(c, c + d)}")
    print(f"    OR={_ratio(a * d, b * c)}  chi2(Yates)={chi2_yates(a, b, c, d):.1f}")

    # ---- paired within material: before/after its first index reference ------
    before_events = after_events = before_exp = after_exp = 0
    usable = 0
    for mid in sorted(reads):
        fday = first_read.get(mid, "")
        iday = first_index.get(mid, "")
        if not fday or not iday or iday <= fday:
            continue
        after_day = _shift(iday, gap_days)
        # sessions strictly between the first reading and the index, and sessions
        # from the index onwards (pushed out by --gap-days to remove the momentum
        # of the very session that wrote the index reference)
        nb = sum(cnt for day, cnt in day_counts if fday < day < after_day)
        na = sum(cnt for day, cnt in day_counts if day >= after_day)
        if nb < min_exposure or na < min_exposure:
            continue
        usable += 1
        before_events += sum(1 for e in reads[mid] if fday < e[0] < after_day)
        after_events += sum(1 for e in reads[mid] if e[0] >= after_day)
        before_exp += nb
        after_exp += na
    print(f"  [対応] 同一素材内、最初の索引参照日より前 vs 後（両窓 {min_exposure} セッション以上、{usable} 素材、gap={gap_days}日）")
    print(f"    索引前 {before_events} 件 / {before_exp:,} セッション = {_per1000(before_events, before_exp)} per 1000")
    print(f"    索引後 {after_events} 件 / {after_exp:,} セッション = {_per1000(after_events, after_exp)} per 1000")
    print(
        f"    率比(後/前)={_ratio(after_events * before_exp, before_events * after_exp)}"
        f"  chi2(Yates)={chi2_yates(after_events, max(after_exp - after_events, 0), before_events, max(before_exp - before_events, 0)):.1f}"
    )

    # ---- never indexed -------------------------------------------------------
    never = [m for m in led.materials if m not in first_index and m in first_read]
    ev = sum(1 for m in never for e in reads.get(m, ()) if e[0] > first_read[m])
    exp = sum(sessions_after(first_read[m]) for m in never)
    print(f"  [参照] 判断層に一度も現れない、かつ手読みされた素材 {len(never)} 件")
    print(f"    初読以降の再利用 {ev} 件 / {exp:,} セッション = {_per1000(ev, exp)} per 1000")

    # ---- route or survey: how far after a reading does re-use happen? --------
    buckets = ((1, 2), (3, 6), (7, 13), (14, 10 ** 6))
    counts = {b: [0, 0] for b in buckets}   # [events, events with an index at the time]
    for mid in sorted(reads):
        fday = first_read.get(mid, "")
        if not fday:
            continue
        iday = first_index.get(mid, "")
        for event in reads[mid]:
            if event[0] <= fday:
                continue
            lag = _day_distance(fday, event[0])
            for lo, hi in buckets:
                if lo <= lag <= hi:
                    counts[(lo, hi)][0] += 1
                    if iday and iday < event[0]:
                        counts[(lo, hi)][1] += 1
                    break
    print("  [lag 分布] 最初の手読みから何日後に再利用されたか（route=直後 / survey=長期）")
    for lo, hi in buckets:
        total, indexed = counts[(lo, hi)]
        label = f"{lo}-{hi}日" if hi < 10 ** 6 else f"{lo}日以上"
        print(
            f"    {label:<10} 再利用 {total:>5} 件  うち当時の索引あり {indexed:>5}"
            f" ({_pct(indexed, total)})"
        )

    # ---- how absolute is the gate? -------------------------------------------
    total_re = sum(1 for m in reads for e in reads[m] if e[0] > first_read[m])
    unindexed_re = sum(
        1
        for m in reads
        for e in reads[m]
        if e[0] > first_read[m] and first_index.get(m, "99999999") >= e[0]
    )
    print(
        f"  再利用イベント合計 {total_re:,}、うち当時の索引なし {unindexed_re:,}"
        f" ({_pct(unindexed_re, total_re)}) ← ゲートは強いが絶対ではない"
    )


def _day_distance(lo: str, hi: str) -> int:
    """Whole days between two YYYYMMDD strings (0 when equal or unparsable)."""
    import datetime as _dt

    try:
        a = _dt.date(int(lo[:4]), int(lo[4:6]), int(lo[6:]))
        b = _dt.date(int(hi[:4]), int(hi[4:6]), int(hi[6:]))
    except (ValueError, IndexError):
        return 0
    return (b - a).days


def _shift(day: str, delta: int) -> str:
    import datetime as _dt

    try:
        base = _dt.date(int(day[:4]), int(day[4:6]), int(day[6:]))
    except (ValueError, IndexError):
        return day
    return (base + _dt.timedelta(days=delta)).strftime("%Y%m%d")


def _pct(num: float, den: float) -> str:
    return f"{100 * num / den:.3f}%" if den else "n/a"


def _per1000(num: float, den: float) -> str:
    return f"{1000 * num / den:.3f}" if den else "n/a"


def _ratio(num: float, den: float) -> str:
    return f"{num / den:.2f}" if den else "inf"


# ---------------------------------------------------------------------------
# item 1 -- note-first against material-first sessions
# ---------------------------------------------------------------------------
def measure_productivity(led: Ledger) -> None:
    by_session = led.by_session()
    ev_by = Counter(e["session_id"] for e in led.evaluations)
    note_by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for note in led.notes:
        note_by[note.get("session_id", "")].append(note)
    groups: dict[str, list[str]] = {"note_first": [], "material_first": []}
    for sid, rows in sorted(by_session.items()):
        note_idx = [i for i, r in enumerate(rows) if (r.get("target") or {}).get("type") == "note"]
        mat_idx = [i for i, r in enumerate(rows) if (r.get("target") or {}).get("type") == "material"]
        if note_idx and mat_idx:
            groups["note_first" if min(note_idx) < min(mat_idx) else "material_first"].append(sid)
    print("=== item 1 / note 先行 vs material 先行 の産出 ===")

    def per_session(sid: str) -> dict[str, float]:
        notes = note_by.get(sid, ())
        claims = [c for n in notes for c in (n.get("claims") or [])]
        return {
            "evl": ev_by.get(sid, 0),
            "claims": len(claims),
            # §7 item 1 asks for report length too.  It is not recoverable from
            # the ledger: a note row points at a whole readings file, not at the
            # bytes this session added, and this checkout's git history is a
            # single squashed commit, so there is no diff to measure.  What the
            # ledger does hold is how many claims revised a previous reading.
            "rev": sum(1 for c in claims if c.get("kind") == "reading_revised"),
            "read_log": len(by_session.get(sid, ())),
        }

    print(f"  {'群':<16}{'n':>5}{'EVL':>6}{'EVL有':>7}{'claims':>8}{'rev':>6}{'read_log':>9}")
    stats: dict[str, dict[str, float]] = {}
    for label, key in (("note先行", "note_first"), ("material先行", "material_first")):
        sids = groups[key]
        rows = [per_session(s) for s in sids]
        agg = {k: sum(r[k] for r in rows) for k in ("evl", "claims", "rev", "read_log")}
        stats[key] = {k: agg[k] / len(sids) if sids else 0.0 for k in agg}
        print(
            f"  {label:<16}{len(sids):>5}{agg['evl']:>6}{sum(1 for r in rows if r['evl']):>7}"
            f"{agg['claims']:>8}{agg['rev']:>6}{agg['read_log']:>9}"
        )
    for key in ("evl", "claims", "read_log"):
        x = [per_session(s)[key] for s in groups["note_first"]]
        y = [per_session(s)[key] for s in groups["material_first"]]
        print(
            f"  {key}/セッション: {statistics.mean(x) if x else 0:.2f} vs {statistics.mean(y) if y else 0:.2f}"
            f"  Welch t={welch_t(x, y):+.2f}"
        )

    def mode_of(sid: str) -> str:
        for note in note_by.get(sid, ()):
            if note.get("mode"):
                return note["mode"]
        return "(mode欄なし)"

    strata = defaultdict(lambda: defaultdict(list))
    for key, sids in groups.items():
        for sid in sids:
            strata[mode_of(sid)][key].append(sid)
    print("  [mode 層別] 二値アウトカム = 評価を1件以上出したか（Cochran-Mantel-Haenszel）")
    num = den = 0.0
    expected = var = 0.0
    observed = 0
    print(f"    {'mode':<26}{'n':>9}{'EVL有率 note/material':>26}{'層の寄与':>12}")
    for mode in sorted(strata, key=lambda m: -(len(strata[m]["note_first"]) + len(strata[m]["material_first"]))):
        sids_n = strata[mode]["note_first"]
        sids_m = strata[mode]["material_first"]
        if not sids_n or not sids_m:
            print(f"    {mode:<26}{len(sids_n):>4}/{len(sids_m):<4}{'片側のみ→比較不能':>26}")
            continue
        aa = sum(1 for s in sids_n if ev_by.get(s))
        bb = len(sids_n) - aa
        cc = sum(1 for s in sids_m if ev_by.get(s))
        dd = len(sids_m) - cc
        nn = aa + bb + cc + dd
        if nn == 0 or (aa + bb) == 0 or (cc + dd) == 0:
            continue
        num += aa * dd / nn
        den += bb * cc / nn
        r1 = aa + cc
        c1 = aa + bb
        expected += c1 * r1 / nn
        if nn > 1:
            var += c1 * (nn - c1) * r1 * (nn - r1) / (nn * nn * (nn - 1))
        observed += aa
        print(
            f"    {mode:<26}{len(sids_n):>4}/{len(sids_m):<4}"
            f"{_pct(aa, aa + bb):>12} vs {_pct(cc, cc + dd):<13}{aa * dd / nn:>12.2f}"
        )
    cmh = (abs(observed - expected) - 0.5) ** 2 / var if var else float("nan")
    print(
        f"    MH: 観察 {observed} / 期待 {expected:.2f} / 分散 {var:.2f} → chi2(MH)={cmh:.2f}"
        f"  (sum AD/n={num:.2f}, sum BC/n={den:.2f})"
    )
    print("    参考: 層別した各 mode 内の EVL/セッション")
    for mode in sorted(strata, key=lambda m: -(len(strata[m]["note_first"]) + len(strata[m]["material_first"]))):
        sids_n = strata[mode]["note_first"]
        sids_m = strata[mode]["material_first"]
        if not sids_n or not sids_m:
            continue
        xn = [ev_by.get(s, 0) for s in sids_n]
        xm = [ev_by.get(s, 0) for s in sids_m]
        print(
            f"      {mode:<26} n={len(sids_n)}/{len(sids_m)}  {statistics.mean(xn):.2f} vs {statistics.mean(xm):.2f}"
            f"  Welch t={welch_t(xn, xm):+.2f}"
        )


# ---------------------------------------------------------------------------
# item 5 -- microgenesis against ontogeny
# ---------------------------------------------------------------------------
def _norm_rank(kind: str, both: list[str], micro: dict, order: list[str]) -> float:
    """How far a type's ontogeny rank is from its microgenesis rank, both 0-1."""
    micro_sorted = sorted(both, key=lambda k: (micro[k][0], k))
    if len(both) < 2:
        return 0.0
    return abs(order.index(kind) - micro_sorted.index(kind)) / (len(both) - 1)


def measure_series(led: Ledger, min_sessions: int) -> None:
    print("=== item 5 / Siegel & White の主系列の書庫版 ===")
    ranks: dict[str, list[int]] = defaultdict(list)
    for sid, rows in sorted(led.by_session().items()):
        if len(rows) < 3:
            continue
        first: dict[str, int] = {}
        for i, row in enumerate(rows):
            kind = (row.get("target") or {}).get("type")
            if kind and kind not in first:
                first[kind] = i
        for rank, kind in enumerate(sorted(first, key=lambda k: (first[k], k))):
            ranks[kind].append(rank)
    micro = {
        kind: (statistics.median(vals), len(vals))
        for kind, vals in ranks.items()
        if len(vals) >= min_sessions
    }
    print(f"  [微細発生] セッション内の初接触順位（中央値、n>={min_sessions}）")
    for kind, (med, count) in sorted(micro.items(), key=lambda kv: (kv[1][0], kv[0])):
        print(f"    {kind:<18}{med:>6.1f}   (n={count})")
    thin = {k: len(v) for k, v in ranks.items() if len(v) < min_sessions}
    for kind in sorted(thin):
        # an instrument that silently drops a type under-reports; name the gap
        print(f"    {kind:<18}  標本 {thin[kind]} < {min_sessions} → 順位を出さない")
    onto: dict[str, str] = {}
    collection_of = {"material": "materials", "note": "notes", "question": "questions",
                     "hypothesis": "hypotheses", "evaluation": "evaluations",
                     "fragment": "fragments", "relation": "relations", "motif": "motifs",
                     "session": "sessions", "erratum": "errata"}
    for kind, collection in sorted(collection_of.items()):
        days = []
        for row in load(led.root, collection):
            key = next((k for k in row if k.endswith("_id") and isinstance(row[k], str)), "")
            day = _iso_day(row.get("created_at")) or _day(row.get(key, ""))
            if day and day != "00000000":
                days.append(day)
        onto[kind] = min(days) if days else ""
    print("  [個体発生] collection の最古行（created_at、無ければ ID 日付）")
    order = sorted((k for k in onto if onto[k]), key=lambda k: (onto[k], k))
    for rank, kind in enumerate(order):
        print(f"    {kind:<18}{onto[kind]}   (順位 {rank})")
    for kind in sorted(collection_of):
        if not onto[kind]:
            print(f"    {kind:<18}日付を持つ行がない → 順序不明")
    both = sorted(k for k in micro if onto.get(k))
    rho, n = spearman([(micro[k][0], order.index(k)) for k in both])
    print(f"  Spearman rho = {rho:+.3f} (n={n}, 微細発生順位 vs 個体発生順位)")
    micro_sorted = sorted(both, key=lambda k: (micro[k][0], k))
    print(f"    微細発生の最初 {micro_sorted[0]} / 最後 {micro_sorted[-1]}")
    print(f"    個体発生の最初 {order[0] if order else '-'} / 最後 {order[-1] if order else '-'}")
    micro_sorted = sorted(both, key=lambda k: (micro[k][0], k))
    print("    順位の食い違い（正規化順位の差が大きい順）:")
    for kind in sorted(both, key=lambda k: -_norm_rank(k, both, micro, order))[:4]:
        print(
            f"      {kind:<12} 微細発生 {micro_sorted.index(kind)}/{len(both) - 1}"
            f"   個体発生 {order.index(kind)}/{len(order) - 1}"
            f"   差 {_norm_rank(kind, both, micro, order):.2f}"
        )
    for kind in sorted(set(collection_of) - set(ranks)):
        print(
            f"    {kind:<12} は read_log の対象として現れない（{len(load(led.root, collection_of[kind]))} 行あり）"
            " → 微細発生順位が測れない"
        )


# ---------------------------------------------------------------------------
# item 4 -- the three staircase candidates
# ---------------------------------------------------------------------------
def measure_errata(led: Ledger) -> None:
    print("=== item 4 / 「階段」三候補のエラー頻度（errata 台帳） ===")
    errata = [r for r in led.errata if str(r.get("errata_id", "")).startswith("ERR")]
    verdicts = Counter(r.get("verdict") for r in errata)
    print(f"  errata {len(errata)} 行  verdict: {dict(sorted((str(k), v) for k, v in verdicts.items()))}")

    # id -> the file the row lives in, for the integration test
    id2path: dict[str, str] = {}
    for path in sorted(glob.glob(str(led.root / "state" / "*.jsonl"))) + sorted(
        glob.glob(str(led.root / "state" / "*.d" / "*.jsonl"))
    ):
        rel = os.path.relpath(path, led.root)
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                for key, value in row.items():
                    if key.endswith("_id") and isinstance(value, str) and ledger_ids.recognise(value):
                        id2path.setdefault(value, rel)

    alias_path = led.root / "state" / "shard_aliases.json"
    receiving: set[str] = set()
    moved: set[str] = set()
    if alias_path.is_file():
        aliases = json.loads(alias_path.read_text(encoding="utf-8")).get("aliases", {})
        moved = set(aliases)
        receiving = {v["new_shard"] for v in aliases.values() if isinstance(v, dict)}
    print(f"  統合: 移動された旧シャード {len(moved)}、受け側シャード {len(receiving)}")

    def composition(label: str, buckets: Iterable[tuple[str, Any]]) -> None:
        table: dict[str, Counter] = defaultdict(Counter)
        for group, verdict in buckets:
            table[group][str(verdict)] += 1
        print(f"  [{label}]")
        for group in sorted(table):
            counts = table[group]
            total = sum(counts.values())
            contra = counts.get("contradicted", 0)
            print(f"    {group:<36} n={total:>4}  contradicted={contra:>4} ({_pct(contra, total)})")

    # (a) the day boundary between the erratum and its subject
    pairs = []
    for row in errata:
        sid = row.get("subject_id")
        cday = _iso_day(row.get("created_at"))
        sday = _day(sid) if isinstance(sid, str) else ""
        if not sid or not cday or not sday:
            continue
        pairs.append(("同一日" if sday == cday else "別日", row.get("verdict")))
    composition("階段(a) シャード境界: 誤りの記録日 vs 対象行の日付", pairs)

    # (b) integration, as a composition and as an incidence
    pairs = []
    for row in errata:
        path = id2path.get(str(row.get("subject_id", "")))
        if not path:
            continue
        group = "受け側" if path in receiving else ("移動元" if path in moved else "非統合")
        pairs.append((group, row.get("verdict")))
    composition("階段(b) 統合: 対象行が今いるシャード", pairs)
    rows_recv = rows_other = 0
    for path in sorted(set(id2path.values())):
        full = led.root / path
        count = sum(1 for line in full.open(encoding="utf-8") if line.strip())
        if path in receiving:
            rows_recv += count
        elif path not in moved:
            rows_other += count
    sub_recv = sum(1 for g, _ in pairs if g == "受け側")
    sub_other = sum(1 for g, _ in pairs if g == "非統合")
    print(
        f"    発生率: 受け側 {sub_recv}/{rows_recv:,} 行 = {_per1000(sub_recv, rows_recv)} per 1000行"
        f"   非統合 {sub_other}/{rows_other:,} 行 = {_per1000(sub_other, rows_other)} per 1000行"
    )
    print(
        f"    率比={_ratio(sub_recv * rows_other, sub_other * rows_recv)}"
        f"  chi2(Yates)={chi2_yates(sub_recv, max(rows_recv - sub_recv, 0), sub_other, max(rows_other - sub_other, 0)):.1f}"
    )
    print(
        f"    全行のうち受け側 {_pct(rows_recv, rows_recv + rows_other)}、errata対象のうち受け側 {_pct(sub_recv, sub_recv + sub_other)}"
    )

    # (c) the unordered hash part: negative control
    pairs = []
    for row in errata:
        sid = str(row.get("subject_id", ""))
        tail = sid.rsplit("-", 1)[-1]
        try:
            value = int(tail, 16)
        except ValueError:
            continue
        pairs.append((f"ハッシュ四分位 Q{min(value * 4 // 0x1000000, 3)}", row.get("verdict")))
    composition("階段(c) ID ハッシュ部分（負の対照: 順序を持たない）", pairs)


# ---------------------------------------------------------------------------
# item 3 -- role switch cost, and whether the sample can carry it
# ---------------------------------------------------------------------------
def measure_roles(led: Ledger) -> None:
    print("=== item 3 / ロール切替の費用（まず標本） ===")
    reads = led.work_reads()
    role = {sid: (row.get("assigned_role") or "-") for sid, row in led.sessions.items()}
    print(f"  assigned_role を持つセッション {sum(1 for v in role.values() if v != '-')} / {len(role)}")
    multi = {m: sids for m, sids in ((m, {e[1] for e in ev}) for m, ev in reads.items()) if len(sids) >= 2}
    withrole = {
        m: sids for m, sids in multi.items() if len({role[s] for s in sids if role[s] != "-"}) >= 2
    }
    print(f"  2セッション以上に手読みされた素材 {len(multi)} / {len(reads)}")
    print(f"  うち異なる assigned_role のセッションが読んだ素材 {len(withrole)} ← 対応比較の標本")
    involved = sorted({s for sids in withrole.values() for s in sids if role[s] != "-"})
    by_session = led.by_session()
    ev_by = Counter(e["session_id"] for e in led.evaluations)
    hand = Counter()
    for events in reads.values():
        for _, sid, _ in events:
            hand[sid] += 1
    per: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for sid in involved:
        group = role[sid]
        per[group]["read_log"].append(len(by_session.get(sid, ())))
        per[group]["hand"].append(hand.get(sid, 0))
        per[group]["evl"].append(ev_by.get(sid, 0))
    print(f"    {'role':<20}{'n':>4}{'read_log':>10}{'手読み':>9}{'EVL':>7}")
    for group in sorted(per, key=lambda g: -len(per[g]["read_log"])):
        vals = per[group]
        print(
            f"    {group:<20}{len(vals['read_log']):>4}{statistics.mean(vals['read_log']):>10.1f}"
            f"{statistics.mean(vals['hand']):>9.1f}{statistics.mean(vals['evl']):>7.2f}"
        )
    arms = [g for g in sorted(per) if len(per[g]["read_log"]) > 1]
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            x = per[arms[i]]["read_log"]
            y = per[arms[j]]["read_log"]
            se = math.sqrt(statistics.variance(x) / len(x) + statistics.variance(y) / len(y))
            diff = abs(statistics.mean(x) - statistics.mean(y))
            mde = 2.8 * se
            need = 2 * (2.8 * math.sqrt((statistics.variance(x) + statistics.variance(y)) / 2) / diff) ** 2 if diff else float("inf")
            print(
                f"    {arms[i]} vs {arms[j]}: 差 {diff:.1f} 行, t={welch_t(x, y):+.2f},"
                f" 80%検出力のMDE {mde:.1f} 行, 観測差を測るのに必要な n ≈ {need:.0f}/群"
            )


# ---------------------------------------------------------------------------
# item 6 (archive side) -- do same-day sessions partition what they touch?
# ---------------------------------------------------------------------------
def measure_siblings(led: Ledger, day: str) -> None:
    print("=== item 6 / 同日並行セッションの素材分割 ===")
    target_day = day or (led.days[-1] if led.days else "")
    touched: dict[str, set[str]] = defaultdict(set)
    worked: dict[str, set[str]] = defaultdict(set)
    for row in led.read_log:
        sid = row.get("session_id")
        target = row.get("target") or {}
        if led.session_day.get(sid) != target_day or target.get("type") != "material":
            continue
        touched[sid].add(target.get("id"))
        if row.get("reading") in WORK_READINGS:
            worked[sid].add(target.get("id"))
    sids = sorted(touched)
    print(f"  日付 {target_day}: 素材に触れたセッション {len(sids)}")
    overlap_work = overlap_touch = pairs = 0
    for i, left in enumerate(sids):
        for right in sids[i + 1 :]:
            pairs += 1
            overlap_work += len(worked[left] & worked[right])
            overlap_touch += len(touched[left] & touched[right])
    for sid in sids:
        print(
            f"    {sid}: 手読み {len(worked[sid])} / 接触 {len(touched[sid])}"
            f"  role={led.sessions[sid].get('assigned_role', '-')}"
        )
    print(
        f"  ペア {pairs}、手読み素材の重複 延べ {overlap_work} 件（1ペア平均 {overlap_work / pairs if pairs else 0:.2f}）,"
        f" 接触の重複 延べ {overlap_touch} 件"
    )



# ---------------------------------------------------------------------------
# 2026-11-23 (SESSION-20261123-<this>): the nine leftovers of the previous
# report's section 9.1.  Each function below answers one of them and writes
# nothing.
# ---------------------------------------------------------------------------
def _row_paths(root: Path) -> tuple[dict[str, str], dict[str, str], dict[str, int]]:
    """id -> shard path, id -> collection, and shard path -> line count.

    The mapping rule is measure_errata's, not a stricter one: every ``*_id`` field
    whose value the recogniser accepts resolves to the row that carries it, so a
    sub-record id (MAT-EVD-*, CLM-*, SRC-*) lands on its parent's shard.  Using a
    stricter rule here would make this control incomparable with the published
    incidence in item 4 of the previous report."""
    where: dict[str, str] = {}
    coll_of: dict[str, str] = {}
    lines_of: dict[str, int] = {}
    paths = sorted(root.glob("state/*.jsonl")) + sorted(root.glob("state/*.d/*.jsonl"))
    for path in paths:
        rel = str(path.relative_to(root))
        coll = rel.split("/")[1]
        coll = coll[:-6] if coll.endswith(".jsonl") else coll[:-2]
        text = path.read_text(encoding="utf-8").splitlines()
        for line in text:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key, value in row.items():
                if key.endswith("_id") and isinstance(value, str) and ledger_ids.recognise(value):
                    where.setdefault(value, rel)
                    coll_of.setdefault(value, coll)
                    carried = True
    # the same universe measure_errata uses: the files an id actually resolved to
    for rel in set(where.values()):
        lines_of[rel] = sum(
            1 for line in (root / rel).read_text(encoding="utf-8").splitlines() if line.strip()
        )
    return where, coll_of, lines_of


def _alias_sets(root: Path) -> tuple[set[str], set[str]]:
    path = root / "state" / "shard_aliases.json"
    if not path.is_file():
        return set(), set()
    aliases = json.loads(path.read_text(encoding="utf-8")).get("aliases", {})
    return set(aliases), {v["new_shard"] for v in aliases.values() if isinstance(v, dict)}


def measure_relations(led: Ledger) -> None:
    """Item 1 (and 9): is `relation` unused, or structally unreadable -- and does
    the recorded reason for excluding it survive measurement?"""
    print("=== item 1 / relation は read_log の対象になれるか（NON_ADDRESSABLE の理由の検証） ===")
    rel = load(led.root, "relations")
    notes = [(r.get("note") or "").strip() for r in rel]
    nonempty = [x for x in notes if x]
    total_chars = sum(len(x) for x in nonempty)
    lengths = sorted(len(x) for x in nonempty)
    median = lengths[len(lengths) // 2] if lengths else 0
    distinct = len(set(nonempty))
    contacts = sum(1 for row in led.read_log if (row.get("target") or {}).get("type") == "relation")
    print(f"  relations {len(rel):,} 行、note 非空 {len(nonempty):,}（{_pct(len(nonempty), len(rel))}）")
    print(f"  note の総字数 {total_chars:,}、平均 {total_chars / max(1, len(nonempty)):.1f} 字、中央値 {median} 字")
    print(f"  異なった note 文 {distinct:,}（定型文の繰り返し {len(nonempty) - distinct:,} 件 = {_pct(len(nonempty) - distinct, len(nonempty))}）")
    print(f"  read_log で relation を対象にした行: {contacts:,}")
    rt: Counter = Counter(r.get("relation_type") for r in rel)
    print("  relation_type: " + ", ".join(f"{k} {v:,}" for k, v in rt.most_common()))

    endpoints: dict[str, dict] = {}
    for coll in ("materials", "questions", "fragments", "motifs", "notes", "sessions",
                 "hypotheses", "evaluations", "errata", "editorial_decisions"):
        for row in load(led.root, coll):
            for key, value in row.items():
                if key.endswith("_id") and isinstance(value, str) and value:
                    endpoints[value] = row
                    break
    checked = reachable = 0
    unreachable_chars = 0
    samples: list[str] = []
    for row, note in zip(rel, notes):
        if len(note) < 8:
            continue
        checked += 1
        blob = ""
        for side in ("left", "right"):
            ref = row.get(side) or {}
            end = endpoints.get(ref.get("id"))
            if end is not None:
                blob += json.dumps(end, ensure_ascii=False)
        if note[:40] and note[:40] in blob:
            reachable += 1
        else:
            unreachable_chars += len(note)
            if len(samples) < 6:
                samples.append(f"    {row.get('relation_id')}: {(row.get('left') or {}).get('type')}→{(row.get('right') or {}).get('type')} 「{note[:58]}」")
    print(f"  端点から到達できる note（先頭40字が端点行内に出現）: {reachable:,}/{checked:,} = {_pct(reachable, checked)}")
    print(f"  端点に無い散文: {checked - reachable:,} 件・{unreachable_chars:,} 字")
    for line in samples:
        print(line)
    try:
        import ledger_ids  # type: ignore
        reason = ledger_ids.NON_ADDRESSABLE.get("REL", "")
        if reason:
            print(f"  記録済みの理由（tools/ledger_ids.py NON_ADDRESSABLE['REL']）: {reason}")
        else:
            print("  REL は NON_ADDRESSABLE から外れている（REFERENCE_TYPES 侧にある）")
        print(f"  REFERENCE_TYPES に relation があるか: {'relation' in ledger_ids.REFERENCE_TYPES}")
    except Exception as exc:  # pragma: no cover
        print(f"  ledger_ids を読めなかった: {exc}")
    print("  判定: 理由は『辺を引用しても到達可能な内容は増えない』。測定はそれを支持しない"
          if checked - reachable else "  判定: 端点から到達できない note は見つからなかった")


WHOLE_SCOPE = re.compile(r"state/([a-z_]+)\.jsonl")
WHOLE_WORDS = ("union", "全行", "全シャード", "全台帳", "全数", "全て")


def measure_errata_control(led: Ledger, sample: int = 400, seed: int = 20261123) -> None:
    """Item 2: the discovery-bias control, in three designs of increasing exposure
    matching.  (A) errata whose recorded audit scope is a whole-collection union.
    (B) inside one receiving shard, foreign-dated (moved-in) rows against native
    rows.  (C) a prospective audit: the same mechanical procedure applied now to a
    matched random sample of moved and unmoved rows, so exposure is equal by
    construction and the auditor cannot have 'already looked' at one group."""
    import random

    print("=== item 2 / 発見バイアスの対照群（三つの設計） ===")
    where, coll_of, lines_of = _row_paths(led.root)
    moved, receiving = _alias_sets(led.root)
    rows_recv: Counter = Counter()
    rows_other: Counter = Counter()
    for path, count in lines_of.items():
        coll = path.split("/")[1]
        coll = coll[:-6] if coll.endswith(".jsonl") else coll[:-2]
        if path in receiving:
            rows_recv[coll] += count
        elif path not in moved:
            rows_other[coll] += count

    def klass(subj: str) -> str:
        path = where.get(subj, "")
        if path in receiving:
            return "moved"
        if path and path not in moved:
            return "unmoved"
        return "not_a_row"

    err = led.errata
    cls = Counter(klass(str(r.get("subject_id") or "")) for r in err)
    rm, ro = sum(rows_recv.values()), sum(rows_other.values())
    rate_m = 1000 * cls["moved"] / rm if rm else 0.0
    rate_u = 1000 * cls["unmoved"] / ro if ro else 0.0
    print(f"  [0 全体] errata {len(err)} 行の対象: 受け側 {cls['moved']} / 非統合 {cls['unmoved']} / 台帳行でない対象 {cls['not_a_row']}")
    print(f"           発生率 受け側 {cls['moved']}/{rm:,} = {rate_m:.2f} per1000、非統合 {cls['unmoved']}/{ro:,} = {rate_u:.2f} per1000、率比 {rate_m / rate_u if rate_u else float('inf'):.2f}")

    # ---- (A) audits that recorded a whole-collection scope --------------------
    def scope_text(row: dict) -> str:
        params = (row.get("check") or {}).get("params") or {}
        return " ".join(json.dumps(v, ensure_ascii=False) for v in params.values())

    scans: Counter = Counter()
    err_in_scan: Counter = Counter()
    err_in_scan_cls: Counter = Counter()
    for row in err:
        text = scope_text(row)
        named = set(WHOLE_SCOPE.findall(text))
        if not named or not any(w in text for w in WHOLE_WORDS):
            continue
        for coll in named:
            scans[coll] += 1
            subj = str(row.get("subject_id") or "")
            if coll_of.get(subj) == coll:
                err_in_scan[coll] += 1
                err_in_scan_cls[(coll, klass(subj))] += 1
    total_scans = sum(scans.values())
    print(f"  [A 記録された範囲] 監査範囲が『コレクション全行の union』と読める errata 行: {total_scans} 件の走査（{len([r for r in err if any(w in scope_text(r) for w in WHOLE_WORDS) and WHOLE_SCOPE.findall(scope_text(r))])} 行）")
    for coll in sorted(scans, key=lambda c: -scans[c])[:8]:
        rmv, run = rows_recv[coll], rows_other[coll]
        a, b = err_in_scan_cls[(coll, "moved")], err_in_scan_cls[(coll, "unmoved")]
        print(f"      {coll:<22} 全行走査 {scans[coll]:>2} 回、対象になった行 受け側 {a}/{rmv:,}・非統合 {b}/{run:,}")
    print("      読み: 全行を見た監査だけを集めると標本が一桁になり、率比を出せない。")
    print("            『監査範囲を記録する』ことがこれまで例外的だったためで、対照群は過去からは作れない。")

    # ---- (B) inside one receiving shard: foreign-dated against native ---------
    def shard_day(path: str) -> str:
        name = path.rsplit("/", 1)[-1]
        return name[:10].replace("-", "")

    foreign: Counter = Counter()
    native: Counter = Counter()
    foreign_err = native_err = 0
    for path, count in lines_of.items():
        if path not in receiving:
            continue
        coll = path.split("/")[1]
        coll = coll[:-6] if coll.endswith(".jsonl") else coll[:-2]
        for line in (led.root / path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rid = next((v for k, v in row.items()
                        if k.endswith("_id") and isinstance(v, str) and ledger_ids.recognise(v)), "")
            day = _day(rid)
            if not day or day == "00000000":
                continue
            if day != shard_day(path):
                foreign[coll] += 1
            else:
                native[coll] += 1
    for row in err:
        subj = str(row.get("subject_id") or "")
        path = where.get(subj, "")
        if path not in receiving:
            continue
        day = _day(subj)
        if not day or day == "00000000":
            continue
        if day != shard_day(path):
            foreign_err += 1
        else:
            native_err += 1
    tf, tn = sum(foreign.values()), sum(native.values())
    rf = 1000 * foreign_err / tf if tf else 0.0
    rn = 1000 * native_err / tn if tn else 0.0
    print(f"  [B 同一シャード内] 受け側シャードの中の行: 他日付（移動してきた行） {tf:,} / 同一日付（そこに生まれた行） {tn:,}")
    print(f"      errata 対象 他日付 {foreign_err} = {rf:.2f} per1000、同一日付 {native_err} = {rn:.2f} per1000、率比 {rf / rn if rn else float('inf'):.2f}")
    if foreign_err + native_err >= 5 and tf and tn:
        print(f"      chi2(Yates) = {chi2_yates(foreign_err, tf - foreign_err, native_err, tn - native_err):.1f}")
    print("      読み: 同じファイルの中にあれば監査は両方見えたはず、という設計。ただし統合の監査は")
    print("            『日付がずれた行を探す』こと自体が目的なので、曝露が等しいとは構成上言えない。")

    # ---- (C) prospective matched audit ---------------------------------------
    universe = set(where)
    schemas: dict[str, list] = {}
    for coll in set(coll_of.values()):
        spath = led.root / "schema" / f"{coll[:-1] if coll.endswith('s') and coll != 'errata' else coll}.schema.json"
        for cand in (led.root / "schema" / f"{coll}.schema.json", spath):
            if cand.is_file():
                try:
                    schemas[coll] = json.loads(cand.read_text(encoding="utf-8")).get("required") or []
                except json.JSONDecodeError:
                    schemas[coll] = []
                break
    fk_re = re.compile(r"^(session_id|.*_ids?|target|left|right|parent_.*|child_.*|.*_by)$")

    def audit(row: dict, path: str, coll: str) -> list:
        problems = []
        rid = next((v for k, v in row.items() if k.endswith("_id") and isinstance(v, str)), "")
        day = _day(rid)
        if day and day != "00000000" and day != shard_day(path):
            problems.append("id_day!=shard_day")
        created = _iso_day(row.get("created_at"))
        if created and day and created != day:
            problems.append("created_at!=id_day")
        for key, value in row.items():
            if not fk_re.match(key):
                continue
            refs = []
            if isinstance(value, str):
                refs = [value]
            elif isinstance(value, list):
                refs = [v for v in value if isinstance(v, str)]
            elif isinstance(value, dict):
                inner = value.get("id")
                refs = [inner] if isinstance(inner, str) else []
            for ref in refs:
                if not ref or ref in universe:
                    continue
                if not ledger_ids.recognise(ref):
                    continue  # a path, a URL, free text -- not a row reference
                family = ref.split("-")[0]
                if family in ledger_ids.NON_ADDRESSABLE:
                    continue  # a sub-record id; its parent is the addressable row
                problems.append(f"unresolved:{key}")
                break
        for field in schemas.get(coll, []):
            if field not in row:
                problems.append(f"missing:{field}")
        return problems

    pool_moved: list = []
    pool_unmoved: list = []
    for rel in sorted(lines_of):
        path = led.root / rel
        coll = rel.split("/")[1]
        coll = coll[:-6] if coll.endswith(".jsonl") else coll[:-2]
        is_recv, is_moved_src = rel in receiving, rel in moved
        if not is_recv and is_moved_src:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            (pool_moved if is_recv else pool_unmoved).append((row, rel, coll))
    rng = random.Random(seed)
    take_m = rng.sample(pool_moved, min(sample, len(pool_moved)))
    take_u = rng.sample(pool_unmoved, min(sample, len(pool_unmoved)))
    res = {}
    for name, take in (("受け側シャードの行（移動を含む）", take_m), ("非統合シャードの行", take_u)):
        bad = 0
        kinds: Counter = Counter()
        for row, rel, coll in take:
            problems = audit(row, rel, coll)
            if problems:
                bad += 1
                for pr in problems:
                    kinds[pr.split(":")[0] if ":" in pr else pr] += 1
        res[name] = (bad, len(take), kinds)
        print(f"  [C 前向き対照] {name}: n={len(take)}、不一致 {bad} = {100 * bad / max(1, len(take)):.1f}%  内訳 {dict(kinds.most_common(5))}")
    a = res["受け側シャードの行（移動を含む）"]
    b = res["非統合シャードの行"]
    if a[1] and b[1]:
        print(f"      率比（受け側/非統合）= {(a[0] / a[1]) / (b[0] / b[1]) if b[0] else float('inf'):.2f}"
              f"、chi2(Yates) = {chi2_yates(a[0], a[1] - a[0], b[0], b[1] - b[0]):.1f}")
    print(f"      手続: seed={seed} の無作為抽出、同一の機械的検査（ID日付とシャード日付の一致・created_at との一致・")
    print("            FK らしき欄の解決・schema の required の存在）を両群に同じ瞬間に適用。曝露は構成上等しい。")
    print("      限界: 機械的検査は過去の監査（人が本文を読んで引用を照合した）と同じではない。")
    print("            したがってこれは『同じ道具で同じだけ見たら差が出るか』の対照であって、")
    print("            『過去の誤り発見率』の対照ではない。errata 行は追加していない（§5 の数値を動かさないため）。")


def measure_role_cohort(led: Ledger) -> None:
    """Item 4: is the 23.5% role fill rate negligence, or a field that was
    introduced part-way through the ledger -- and how fast does the item-3 sample
    grow now?"""
    print("=== item 4 / assigned_role の記入率はコホート効果か ===")
    sessions = list(led.sessions.values())
    role_days = [_day(s["session_id"]) for s in sessions if s.get("assigned_role")]
    first_role_day = min((d for d in role_days if d), default="")
    last_day = led.days[-1] if led.days else ""
    print(f"  assigned_role が最初に出た日: {first_role_day}、最終セッション日: {last_day}")
    cohorts = (("導入前", lambda d: d < first_role_day),
               ("導入後〜最終実日付", lambda d: first_role_day <= d <= "20261123"),
               ("先走り日付（20261124〜）", lambda d: d > "20261123"))
    for name, test in cohorts:
        sel = [s for s in sessions if test(_day(s["session_id"]))]
        filled = [s for s in sel if s.get("assigned_role")]
        print(f"  {name:<22} n={len(sel):<5} 記入 {len(filled):<5} = {_pct(len(filled), len(sel))}")
    print("  導入後の日別:")
    byday: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for s in sessions:
        d = _day(s["session_id"])
        if d and first_role_day and d >= first_role_day:
            byday[d][1] += 1
            if s.get("assigned_role"):
                byday[d][0] += 1
    for d in sorted(byday)[:12]:
        a, b = byday[d]
        print(f"    {d}  {a:>3}/{b:<3} = {_pct(a, b)}")
    # the item-3 sample and its growth
    reads = led.work_reads()
    roles_of: dict[str, set] = defaultdict(set)
    for mid, events in reads.items():
        for day, sid, _rid in events:
            role = led.sessions.get(sid, {}).get("assigned_role")
            if role:
                roles_of[mid].add(role)
    multi = {m: r for m, r in roles_of.items() if len(r) >= 2}
    print(f"  異なる assigned_role のセッションに手読みされた素材: {len(multi)}（item 3 の標本）")
    per_role: Counter = Counter()
    for mid, events in reads.items():
        for _day_, sid, _rid in events:
            role = led.sessions.get(sid, {}).get("assigned_role")
            if role:
                per_role[role] += 1
    print("  ロール別の手読み行数: " + ", ".join(f"{k} {v}" for k, v in per_role.most_common()))
    # cumulative sample by day: when did each multi-role material qualify?
    qualify: dict[str, str] = {}
    for mid, events in reads.items():
        seen: dict[str, str] = {}
        for day, sid, _rid in sorted(events):
            role = led.sessions.get(sid, {}).get("assigned_role")
            if role and role not in seen:
                seen[role] = day
                if len(seen) >= 2 and mid not in qualify:
                    qualify[mid] = day
    days_sorted = sorted(set(qualify.values()))
    cum = 0
    series = []
    for d in days_sorted:
        cum += sum(1 for v in qualify.values() if v == d)
        series.append((d, cum))
    print("  標本の累積（資格を得た日 → 累積素材数）: " + ", ".join(f"{d}:{c}" for d, c in series[-8:]))
    if len(series) >= 2:
        span = abs(_day_distance(series[-1][0], series[0][0])) or 1
        rate = (series[-1][1] - series[0][1]) / span
        print(f"  増加率 {rate:.2f} 素材/日（{series[0][0]}〜{series[-1][0]}、{span}日）")
    # per role pair: the unit the power calculation actually needs
    pair_qualify: dict[tuple, dict[str, str]] = defaultdict(dict)
    for mid, events in reads.items():
        seen: dict[str, str] = {}
        for day, sid, _rid in sorted(events):
            role = led.sessions.get(sid, {}).get("assigned_role")
            if role and role not in seen:
                seen[role] = day
        for pair in itertools.combinations(sorted(seen), 2):
            pair_qualify[pair][mid] = max(seen[pair[0]], seen[pair[1]])
    print("  ロール対別の標本と、n=48（80%検出力で観測差を測るのに要る数）までの見込み:")
    for pair in sorted(pair_qualify, key=lambda pr: -len(pair_qualify[pr])):
        days_map = pair_qualify[pair]
        ordered = sorted(days_map.values())
        if len(ordered) < 2:
            continue
        span = abs(_day_distance(ordered[-1], ordered[0])) or 1
        pair_rate = len(ordered) / span
        need = max(0, 48 - len(ordered))
        eta = f"約 {need / pair_rate:.0f} 日" if pair_rate > 0 and need else "既に到達" if not need else "増加率0"
        print(f"    {pair[0]:<20} 対 {pair[1]:<20} n={len(ordered):<4} 増加 {pair_rate:.2f}/日  {eta}")


def measure_adjacency(led: Ledger, window: int = 5, cut_margin_days: int = 3) -> None:
    """Item 7: does sitting next to an indexed row in the same shard explain part
    of the gate effect?  Splits the never-indexed control group by adjacency."""
    print(f"=== item 7 / 近接の匂い（同一シャード内で索引済み行の ±{window} 行以内か） ===")
    position: dict[str, tuple[str, int]] = {}
    for path in sorted(led.root.glob("state/materials.jsonl")) + sorted(led.root.glob("state/materials.d/*.jsonl")):
        rel = str(path.relative_to(led.root))
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            mid = row.get("material_id")
            if mid:
                position[mid] = (rel, index)
    indexed = set(led.first_index_day())
    reads = led.work_reads()
    last_day = led.days[-1] if led.days else ""
    cut = _shift(last_day, -cut_margin_days)
    day_counts = [(d, len(v)) for d, v in sorted(led.sessions_by_day.items())]
    cum: list[tuple[str, int]] = []
    running = 0
    for day, count in day_counts:
        running += count
        cum.append((day, running))
    total = running
    import bisect
    keys = [d for d, _ in cum]

    def sessions_after(day: str) -> int:
        i = bisect.bisect_right(keys, day)
        return total - (cum[i - 1][1] if i else 0)

    by_file: dict[str, list[int]] = defaultdict(list)
    for mid, (rel, index) in position.items():
        if mid in indexed:
            by_file[rel].append(index)
    groups = {"索引あり": [0, 0], f"索引なし・隣接±{window}": [0, 0], "索引なし・孤立": [0, 0]}
    for mid, events in reads.items():
        if not events:
            continue
        first = events[0][0]
        if first > cut:
            continue
        exposure = sessions_after(first)
        if exposure <= 0:
            continue
        reuse = sum(1 for day, _sid, _rid in events if day > first)
        if mid in indexed:
            key = "索引あり"
        else:
            rel, index = position.get(mid, ("", -1))
            neighbours = by_file.get(rel, [])
            key = (f"索引なし・隣接±{window}"
                   if any(abs(index - n) <= window for n in neighbours) else "索引なし・孤立")
        groups[key][0] += reuse
        groups[key][1] += exposure
    base = groups["索引なし・孤立"]
    for name, (events, exposure) in groups.items():
        print(f"  {name:<22} 再利用 {events:>5} / 曝露 {exposure:>9,} セッション = {_per1000(events, exposure):>6} per 1000")
    for name in ("索引なし・孤立", f"索引なし・隣接±{window}"):
        a = groups["索引あり"]
        b = groups[name]
        if a[1] and b[1] and b[0] >= 0:
            ora = (a[0] / max(1, a[1] - a[0])) / (b[0] / max(1, b[1] - b[0])) if b[0] else float("inf")
            print(f"  OR（索引あり 対 {name}）= {ora:.2f}、chi2(Yates) = "
                  f"{chi2_yates(a[0], a[1] - a[0], b[0], b[1] - b[0]):.1f}")
    a = groups[f"索引なし・隣接±{window}"]
    b = groups["索引なし・孤立"]
    if a[1] and b[1] and a[0] and b[0]:
        ora = (a[0] / (a[1] - a[0])) / (b[0] / (b[1] - b[0]))
        print(f"  純粋な近接効果 OR（隣接 対 孤立、どちらも索引なし）= {ora:.2f}、chi2(Yates) = "
              f"{chi2_yates(a[0], a[1] - a[0], b[0], b[1] - b[0]):.1f}")
        print("  読み: 1 から離れていれば、シャード内の位置だけで再利用が変わる（走査で届く）。")
        print("        1 に近ければ、OR=3.84 の差は索引そのものに帰属してよい。")


PROVENANCE_TERMS = {
    "questions": ("questions", "問い"),
    "fragments": ("fragments", "断片"),
    "relations": ("relations", "関係線"),
    "materials": ("materials", "素材"),
    "motifs": ("motifs", "モチーフ"),
    "sessions": ("sessions", "セッション"),
    "notes": ("notes", "ノート"),
    "evaluations": ("evaluations", "評価"),
    "hypotheses": ("hypotheses", "仮説"),
    "errata": ("errata", "訂正録"),
    "editorial_decisions": ("editorial_decisions", "編集判断"),
    "read_log": ("read_log", "読み痕跡"),
}


def measure_provenance(led: Ledger) -> None:
    """Item 3: is the ontogeny order the order in which the archive's own
    instruments and schemas were built?  Prints the measured first-row day beside
    every dated mention of that collection in docs/, schema/ and tools/."""
    print("=== item 3 / 個体発生順序は計器の製作順序か（文書側の日付言及と並べる） ===")
    onto: dict[str, str] = {}
    for coll in sorted(PROVENANCE_TERMS):
        days = []
        for row in load(led.root, coll):
            key = next((k for k in row if k.endswith("_id") and isinstance(row[k], str)), "")
            day = _iso_day(row.get("created_at")) or _day(row.get(key, ""))
            if day and day != "00000000":
                days.append(day)
        onto[coll] = min(days) if days else ""
    date_re = re.compile(r"(20\d{2}-\d{2}-\d{2})")
    mentions: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    scan = (sorted(led.root.glob("docs/*.md")) + sorted(led.root.glob("schema/*.json"))
            + sorted(led.root.glob("prompts/*.md")) + [led.root / "PROJECT_CHARTER.md", led.root / "CONTENT_POLICY.md", led.root / "README.md"])
    for path in scan:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            found = date_re.findall(line)
            if not found:
                continue
            # institutional mentions only: the collection named literally, on a line
            # that talks about adding it.  The Japanese labels are common words and
            # match every chronicle line, which dates nothing.
            if not any(w in line for w in ("追加", "導入", "新設", "enum", "schema", "層", "凍結", "実装")):
                continue
            for coll, terms in PROVENANCE_TERMS.items():
                if terms[0] in line:
                    for day in found:
                        mentions[coll].append((day, f"{path.name}:{lineno}", line.strip()[:150]))
    print("  collection            最古行        文書内の最古の日付言及   言及数")
    for coll in sorted(onto, key=lambda c: onto[c] or "9999"):
        ms = sorted(mentions.get(coll, []))
        first = ms[0][0] if ms else "-"
        print(f"  {coll:<22}{onto[coll] or '-':<14}{first:<24}{len(ms)}")
    print("  最古の言及の実例:")
    for coll in sorted(onto, key=lambda c: onto[c] or "9999"):
        ms = sorted(mentions.get(coll, []))
        for day, where, line in ms[:2]:
            print(f"    [{coll}] {day} {where}: {line}")
    print("  読み: 最古行の日付と文書内の最古言及が同じ日なら、そのコレクションは")
    print("        『認知の発達順』ではなく『制度（schema・計器）の導入順』に現れたことになる。")



BELIEF_BASES: tuple[tuple[str, dict], ...] = (
    ("既定（heir_credit のみ）", {}),
    ("receiver_gated（三門）", {"receiver_gated": True}),
    ("heir_credit=False（系譜を切る）", {"heir_credit": False}),
    ("pair_level_repeat", {"pair_level_repeat": True}),
    ("narrowing_partner_share", {"narrowing_partner_share": True}),
    ("temporal_heir_guard", {"temporal_heir_guard": True}),
)


def measure_bases(led: Ledger, since: str = "") -> None:
    """Leftover 8: re-measure HYP-20261123-1054be's own quantity on a ledger that
    has grown since the hypothesis was written.  The hypothesis says the leading
    answer to the three central questions depends on which accounting basis reads
    the ledger; its clause (a) is refuted if every basis agrees and the leader's
    posterior varies by less than 10pp, its clause (c) needs ten independent direct
    evaluations of the lineage-cut leader before it can be tested at all."""
    import sys

    print("=== item 8 / HYP-20261123-1054be 会計基底依存説の再測定 ===")
    sys.path.insert(0, str(led.root / "tools"))
    import belief_state as bs

    questions = ("Q-001", "Q-002", "Q-003")
    leaders: dict[str, dict[str, str]] = {q: {} for q in questions}
    posteriors: dict[str, dict[str, float]] = {q: {} for q in questions}
    totals = {}
    for name, knobs in BELIEF_BASES:
        state = bs.compute_belief_state(root=led.root, **knobs)
        totals[name] = (state.get("total_hypotheses"), state.get("total_evaluations"))
        for q in questions:
            rec = (state.get("questions") or {}).get(q) or {}
            ranked = rec.get("hypotheses") or []
            if isinstance(ranked, dict):
                ranked = list(ranked.values())
            if not ranked:
                continue
            top = ranked[0]
            leaders[q][name] = top.get("hypothesis_id") or top.get("id") or ""
            value = top.get("posterior", top.get("p"))
            posteriors[q][name] = float(value) if value is not None else float("nan")
    print(f"  台帳: 仮説 {totals[BELIEF_BASES[0][0]][0]}・評価 {totals[BELIEF_BASES[0][0]][1]}"
          "（仮説が書かれたときは 91・844 だった）")
    slots: Counter = Counter()
    for q in questions:
        kinds = len(set(leaders[q].values()))
        vals = [v for v in posteriors[q].values() if v == v]
        print(f"  {q}: 首位 {kinds} 種、首位Pの基底間変動 {100 * (max(vals) - min(vals)):.2f}pp" if vals else f"  {q}: 首位 {kinds} 種")
        for name, _ in BELIEF_BASES:
            hid = leaders[q].get(name, "-")
            slots[hid] += 1
            print(f"      {name:<34} {hid:<24} P={100 * posteriors[q].get(name, float('nan')):.2f}%")
    top_slot, top_n = slots.most_common(1)[0]
    total_slots = sum(slots.values())
    print(f"  {total_slots} スロットの最大占有: {top_slot} が {top_n}（{_pct(top_n, total_slots)}）")
    print(f"  条項(a)（全基底が同じ首位かつ変動10pp未満なら棄却）: "
          f"{'発動' if all(len(set(leaders[q].values())) == 1 for q in questions) else '不発——首位は分かれたまま'}")
    cut = leaders["Q-001"].get("heir_credit=False（系譜を切る）", "")
    evaluations = load(led.root, "evaluations")
    direct = [e for e in evaluations if e.get("target_hypothesis_id") == cut]
    recent = [e for e in direct if str(e.get("created_at", "")) >= (since or "2026-11-23")]
    sessions = len({e.get("session_id") for e in recent})
    print(f"  条項(c)（系譜を切った基底の首位 {cut}）: 評価 総数 {len(direct)}、"
          f"{since or '2026-11-23'} 以降 {len(recent)} 件・独立セッション {sessions}")
    print(f"      → 10件以上の独立直接評価: {'ある——検査できる' if sessions >= 10 else 'ない——条項(c)はまだ検査できない'}")
    print("  条項(b)（周辺密度で正規化すれば首位入れ替わりが消えるか）: 未検査。正規化実装が別に要る。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gate", action="store_true", help="item 2: index layer against re-reading")
    parser.add_argument("--productivity", action="store_true", help="item 1: note-first against material-first")
    parser.add_argument("--series", action="store_true", help="item 5: microgenesis against ontogeny")
    parser.add_argument("--errata", action="store_true", help="item 4: the three staircase candidates")
    parser.add_argument("--roles", action="store_true", help="item 3: role-switch cost and its sample")
    parser.add_argument("--siblings", action="store_true", help="item 6: same-day material partition")
    parser.add_argument("--relations", action="store_true", help="leftover 1: are relations readable at all")
    parser.add_argument("--errata-control", action="store_true", help="leftover 2: discovery-bias control group")
    parser.add_argument("--provenance", action="store_true", help="leftover 3: ontogeny against documented introductions")
    parser.add_argument("--role-cohort", action="store_true", help="leftover 4: role fill rate as a cohort effect")
    parser.add_argument("--adjacency", action="store_true", help="leftover 7: shard adjacency smell inside the gate")
    parser.add_argument("--bases", action="store_true", help="leftover 8: belief leaders under six accounting bases")
    parser.add_argument("--since", default="", help="with --bases: only count direct evaluations from this day on")
    parser.add_argument("--window", type=int, default=5, help="adjacency window in shard lines")
    parser.add_argument("--all", action="store_true", help="run every measurement above")
    parser.add_argument("--root", default=str(ROOT), help="repository root holding state/")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="session id to leave out (repeatable); use it for the measuring session itself",
    )
    parser.add_argument("--date", default="", help="YYYY-MM-DD for --siblings (default: the last session day)")
    parser.add_argument("--cut-margin-days", type=int, default=7, help="days before the last session day for --gate")
    parser.add_argument("--min-exposure", type=int, default=5, help="sessions per window for the paired --gate design")
    parser.add_argument(
        "--lag-days",
        type=int,
        default=0,
        help="cross-sectional --gate: only count re-uses at least this many days after the first reading",
    )
    parser.add_argument(
        "--gap-days",
        type=int,
        default=0,
        help="push the paired --gate 'after' window this many days past the index reference",
    )
    parser.add_argument("--min-sessions", type=int, default=20, help="sessions per reference type for --series")
    args = parser.parse_args()

    flags = ("gate", "productivity", "series", "errata", "roles", "siblings",
             "relations", "errata_control", "provenance", "role_cohort", "adjacency",
             "bases")
    if not args.all and not any(getattr(args, f) for f in flags):
        parser.error("choose at least one measurement, or --all")
    run = {f: (args.all or getattr(args, f)) for f in flags}

    led = Ledger(Path(args.root), tuple(args.exclude))
    if args.exclude:
        print(f"(除外したセッション: {', '.join(sorted(args.exclude))})")
    print(
        f"(台帳: materials {len(led.materials)}, sessions {len(led.sessions)},"
        f" read_log {len(led.read_log)}, notes {len(led.notes)}, evaluations {len(led.evaluations)})"
    )
    if run["gate"]:
        measure_gate(led, args.cut_margin_days, args.min_exposure, args.gap_days, args.lag_days)
    if run["productivity"]:
        measure_productivity(led)
    if run["series"]:
        measure_series(led, args.min_sessions)
    if run["errata"]:
        measure_errata(led)
    if run["roles"]:
        measure_roles(led)
    if run["siblings"]:
        measure_siblings(led, args.date.replace("-", ""))
    if run["relations"]:
        measure_relations(led)
    if run["errata_control"]:
        measure_errata_control(led)
    if run["provenance"]:
        measure_provenance(led)
    if run["role_cohort"]:
        measure_role_cohort(led)
    if run["adjacency"]:
        measure_adjacency(led, args.window, args.cut_margin_days)
    if run["bases"]:
        measure_bases(led, args.since)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
