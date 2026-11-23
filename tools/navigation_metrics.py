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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gate", action="store_true", help="item 2: index layer against re-reading")
    parser.add_argument("--productivity", action="store_true", help="item 1: note-first against material-first")
    parser.add_argument("--series", action="store_true", help="item 5: microgenesis against ontogeny")
    parser.add_argument("--errata", action="store_true", help="item 4: the three staircase candidates")
    parser.add_argument("--roles", action="store_true", help="item 3: role-switch cost and its sample")
    parser.add_argument("--siblings", action="store_true", help="item 6: same-day material partition")
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

    flags = ("gate", "productivity", "series", "errata", "roles", "siblings")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
