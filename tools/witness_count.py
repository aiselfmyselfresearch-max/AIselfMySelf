#!/usr/bin/env python3
"""Count what the ledger counts, and count what it does not.

A mirror, not a score. `PROJECT_CHARTER.md` asks what a self is, for an AI that
reads a record and continues it. `HYP-20261116-5b55ae` (同定費説) claims that the
size and boundary of the unit a system calls "one self" is decided by the *shape
of the cost it paid to identify individuals* — not by content. This script tests
that claim against the archive's own ledgers, in three counts the archive never
takes:

1. **works vs rows.** How many *rows* (`MAT-*`) record a work already present,
   and how many *distinct works* are behind them. Union-find over
   `source.url` OR normalised `source.title`.
2. **witnesses vs rows.** A row exists because someone minted an ID; a work is
   *witnessed* when a hand-written `read_log` row in some session reads it.
   Rows are minted per device; witnesses are paid in sessions. How far apart do
   the two move?
3. **naming scheme vs survival.** The archive used two ID devices: early
   `MAT-LIT-###` (a three-digit counter, so the identity of a work is a small
   number) and later `MAT-<date>-<hash>` (a six-hex digest). Do works named by
   the coarse device survive to be read as often?

None of these counts is a verdict on the archive. Each is a place where a claim
about units can be checked.

Two limits, stated so the numbers are not read as more than they are:

  * ``read_log`` rows whose ``note`` says 機械的バックフィル are excluded from
    the witness count. They record that a material was in a session's context
    list, not that anyone read it (``docs/parallel-work.md``). Including them
    would multiply every witness count by whatever the packet happened to pull.
  * same-URL rows are **not** assumed to be duplicates. ``--passages`` reports
    how many same-URL pairs share an identical ``passage`` and how many do not.
    On the archive at 2026-11-16 the answer was 0 identical and 564 distinct: the
    repetition is re-excerpting, and a tool that called it duplication would be
    wrong about what the rows are.

Usage:
    python3 tools/witness_count.py              # all counts (materials + hypotheses)
    python3 tools/witness_count.py --works      # rows vs distinct works
    python3 tools/witness_count.py --witnesses  # witnesses per work
    python3 tools/witness_count.py --naming     # naming scheme vs survival
    python3 tools/witness_count.py --passages   # are same-URL rows duplicates?
    python3 tools/witness_count.py --hypotheses # hypothesis EVL_sess / RL_sess / single-witness audit
    python3 tools/witness_count.py --json       # machine-readable
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import datetime
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MECHANICAL_MARK = "バックフィル"


# ---------------------------------------------------------------- loading


def load_rows(collection: str, id_key: str) -> list[dict]:
    """Load a frozen base file plus its shards, skipping unparsable lines."""
    paths = [ROOT / "state" / f"{collection}.jsonl"]
    paths += sorted(glob.glob(str(ROOT / "state" / f"{collection}.d" / "*.jsonl")))
    rows: list[dict] = []
    for path in paths:
        p = Path(path)
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict) and rec.get(id_key):
                rows.append(rec)
    return rows


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())


def norm_url(url: str) -> str:
    return (url or "").strip().rstrip("/").lower()


# ---------------------------------------------------------------- union-find


class _UF:
    def __init__(self, ids: list[str]) -> None:
        self.p = {i: i for i in ids}

    def find(self, x: str) -> str:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def work_clusters(materials: list[dict]) -> list[list[str]]:
    """Group material IDs into works by shared URL or shared normalised title.

    A row with neither a usable URL nor a usable title is its own work: the tool
    will not guess an identity it cannot check.
    """
    ids = [m["material_id"] for m in materials]
    uf = _UF(ids)
    by_url: dict[str, list[str]] = defaultdict(list)
    by_title: dict[str, list[str]] = defaultdict(list)
    for m in materials:
        src = m.get("source") or {}
        u = norm_url(src.get("url"))
        t = norm_title(src.get("title"))
        if len(u) > 15:
            by_url[u].append(m["material_id"])
        if len(t) > 12:
            by_title[t].append(m["material_id"])
    for bucket in (by_url, by_title):
        for group in bucket.values():
            for other in group[1:]:
                uf.union(group[0], other)
    clusters: dict[str, list[str]] = defaultdict(list)
    for i in ids:
        clusters[uf.find(i)].append(i)
    return list(clusters.values())


# ---------------------------------------------------------------- witnesses


def witnesses_by_material(read_log: list[dict]) -> dict[str, set[str]]:
    """Sessions with a *hand-written* read of each material.

    ``used_as_context`` rows written by the mechanical backfill are dropped; a
    hand-written ``used_as_context`` row is kept, because a session that chose a
    material as context did pay attention to it.
    """
    out: dict[str, set[str]] = defaultdict(set)
    for r in read_log:
        target = r.get("target") or {}
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        if MECHANICAL_MARK in (r.get("note") or ""):
            continue
        mid = target.get("id")
        sid = r.get("session_id")
        if mid and sid:
            out[mid].add(sid)
    return out


def witnesses_by_hypothesis(read_log: list[dict]) -> dict[str, set[str]]:
    """Sessions with a *hand-written* read of each hypothesis (excludes mechanical backfills)."""
    out: dict[str, set[str]] = defaultdict(set)
    for r in read_log:
        target = r.get("target") or {}
        if not isinstance(target, dict) or target.get("type") != "hypothesis":
            continue
        if MECHANICAL_MARK in (r.get("note") or ""):
            continue
        hid = target.get("id")
        sid = r.get("session_id")
        if hid and sid:
            out[hid].add(sid)
    return out


# ---------------------------------------------------------------- naming


def naming_scheme(material_id: str) -> str:
    if re.fullmatch(r"MAT-(LIT|EVD|TRC)-\d{3}", material_id):
        return "coarse-3digit"
    if re.fullmatch(r"MAT-[A-Z]+-2026\d{4}-[0-9a-f]{4}", material_id):
        return "date-seq"
    if re.search(r"-[0-9a-f]{12}$", material_id):
        return "hash-12hex"
    if re.search(r"-[0-9a-f]{6}$", material_id):
        return "hash-6hex"
    return "other"


# ---------------------------------------------------------------- reports


def report_works(materials: list[dict], *, out) -> dict:
    clusters = work_clusters(materials)
    multi = [c for c in clusters if len(c) > 1]
    redundant = sum(len(c) - 1 for c in multi)
    out(f"material rows             : {len(materials)}")
    out(f"distinct works (url|title) : {len(clusters)}")
    out(f"works holding >1 row       : {len(multi)}")
    out(f"rows inside those works    : {sum(len(c) for c in multi)}")
    out(f"redundant rows             : {redundant}"
        f"  ({redundant / max(len(materials), 1) * 100:.1f}% of rows)")
    out("")
    by_id = {m["material_id"]: m for m in materials}
    out("largest works (rows):")
    for c in sorted(multi, key=len, reverse=True)[:10]:
        src = (by_id[c[0]].get("source") or {})
        out(f"  x{len(c):<3} {src.get('year')} {(src.get('title') or '')[:52]}")
    return {
        "material_rows": len(materials),
        "distinct_works": len(clusters),
        "multi_row_works": len(multi),
        "redundant_rows": redundant,
    }


def report_witnesses(materials: list[dict], read_log: list[dict], *, out) -> dict:
    wit = witnesses_by_material(read_log)
    ids = {m["material_id"] for m in materials}
    read = [i for i in ids if wit.get(i)]
    never = ids - {i for i in ids if wit.get(i)}
    counts = [len(wit[i]) for i in read]
    dist = Counter(min(c, 5) for c in counts)
    out(f"material rows                    : {len(ids)}")
    out(f"hand-read at least once          : {len(read)}"
        f"  ({len(read) / max(len(ids), 1) * 100:.1f}%)")
    out(f"never hand-read                  : {len(never)}"
        f"  ({len(never) / max(len(ids), 1) * 100:.1f}%)")
    out(f"median witnesses per read row    : {statistics.median(counts) if counts else 0}")
    out(f"read by exactly one session only : {sum(1 for c in counts if c == 1)}")
    out("")
    out("works by number of witnessing sessions (5 = 5 or more):")
    for k in sorted(dist):
        label = f"{k}+" if k == 5 else str(k)
        out(f"  {label:>3} : {dist[k]}")
    return {
        "rows": len(ids),
        "hand_read": len(read),
        "never_read": len(never),
        "median_witnesses": statistics.median(counts) if counts else 0,
        "read_by_one_session": sum(1 for c in counts if c == 1),
    }


def report_naming(materials: list[dict], read_log: list[dict], *, out) -> dict:
    wit = witnesses_by_material(read_log)
    grouped: dict[str, list[str]] = defaultdict(list)
    for m in materials:
        grouped[naming_scheme(m["material_id"])].append(m["material_id"])
    out(f"{'scheme':<15} {'rows':>5} {'read%':>7} {'mean witnesses':>15}")
    result = {}
    for scheme in sorted(grouped, key=lambda s: -len(grouped[s])):
        rows = grouped[scheme]
        read = [i for i in rows if wit.get(i)]
        mean_w = (sum(len(wit[i]) for i in read) / len(read)) if read else 0.0
        out(f"{scheme:<15} {len(rows):>5} {len(read) / len(rows) * 100:>6.1f}% "
            f"{mean_w:>15.2f}")
        result[scheme] = {
            "rows": len(rows),
            "read_rate": round(len(read) / len(rows), 4),
            "mean_witnesses": round(mean_w, 3),
        }
    out("")
    out("Note: the two schemes are also two eras. A gap here is a gap between")
    out("devices AND between when the rows were written. This tool reports it and")
    out("does not separate them.")
    return result


def report_passages(materials: list[dict], *, out) -> dict:
    by_url: dict[str, list[dict]] = defaultdict(list)
    for m in materials:
        u = norm_url((m.get("source") or {}).get("url"))
        if len(u) > 15:
            by_url[u].append(m)
    same = diff = pairs = 0
    for group in by_url.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                pairs += 1
                a = (group[i].get("passage") or "").strip()
                b = (group[j].get("passage") or "").strip()
                if a and b and a == b:
                    same += 1
                else:
                    diff += 1
    out(f"same-URL row pairs             : {pairs}")
    out(f"  identical passage            : {same}")
    out(f"  different passage            : {diff}")
    out("")
    out("Identical passages would be true duplication. Different passages are")
    out("re-excerpting: the same work, read again from another place. The tool")
    out("reports both and calls neither one an error.")
    return {"pairs": pairs, "identical": same, "different": diff}


def report_hypotheses(root: Path, *, out) -> dict:
    """Report independent witnessing sessions (EVL_sess & hand-written RL_sess) per hypothesis."""
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import belief_state

    state = belief_state.compute_belief_state(root=root)
    rows: list[dict[str, object]] = []
    single_witness_high_mass: list[str] = []
    self_eval_only: list[str] = []
    unexamined_active: list[str] = []

    for qid, qs in state["questions"].items():
        for hid in qs.get("unexamined_active_hypothesis_ids") or []:
            unexamined_active.append(f"{qid}:{hid}")
        for h in qs["hypotheses"]:
            item = {
                "question_id": qid,
                "hypothesis_id": h["hypothesis_id"],
                "effective_status": h["effective_status"],
                "posterior": h["posterior"],
                "direct_eval_count": h["direct_eval_count"],
                "verified_direct_eval_count": h.get("verified_direct_eval_count", 0),
                "psc_all_verified_count": h.get("psc_all_verified_count", 0),
                "psc_eval_count": h.get("psc_eval_count", 0),
                "witness_eval_session_count": h.get("witness_eval_session_count", 0),
                "witness_read_session_count": h.get("witness_read_session_count", 0),
                "same_session_eval_count": h.get("same_session_eval_count", 0),
                "cross_session_eval_count": h.get("cross_session_eval_count", 0),
                "low_witness_high_mass": bool(h.get("low_witness_high_mass")),
                "self_evaluated_only": bool(h.get("self_evaluated_only")),
            }
            rows.append(item)
            if item["low_witness_high_mass"]:
                single_witness_high_mass.append(f"{qid}:{h['hypothesis_id']}")
            if item["self_evaluated_only"]:
                self_eval_only.append(f"{qid}:{h['hypothesis_id']}")

    out(f"hypotheses audited                   : {len(rows)}")
    out(
        f"single-witness high-mass (P>=5%,EVL<=1): {len(single_witness_high_mass)}"
        + (f"  ({', '.join(single_witness_high_mass)})" if single_witness_high_mass else "")
    )
    out(
        f"self-evaluated only (cross_sess==0)  : {len(self_eval_only)}"
        + (f"  ({', '.join(self_eval_only)})" if self_eval_only else "")
    )
    out(
        f"unexamined active hypotheses         : {len(unexamined_active)}"
        + (f"  ({', '.join(unexamined_active)})" if unexamined_active else "")
    )
    if rows:
        out("")
        out(f"{'Q':<6} {'HYP':<20} {'P%':>5} {'EVL_s':>5} {'RL_s':>4} {'ver/dir':>7} {'same/x':>6} flags")
        for item in sorted(rows, key=lambda r: (str(r["question_id"]), -float(r["posterior"]), str(r["hypothesis_id"]))):
            flags: list[str] = []
            if item["low_witness_high_mass"]:
                flags.append("SINGLE_WITNESS")
            if item["self_evaluated_only"]:
                flags.append("SELF_ONLY")
            if item["direct_eval_count"] == 0 and item["effective_status"] == "active":
                flags.append("UNEXAMINED")
            out(
                f"{str(item['question_id']):<6} {str(item['hypothesis_id']):<20} "
                f"{float(item['posterior']) * 100:5.1f} {int(item['witness_eval_session_count']):>5} "
                f"{int(item['witness_read_session_count']):>4} "
                f"{int(item['verified_direct_eval_count']):>3}/{int(item['direct_eval_count']):<3} "
                f"{int(item['same_session_eval_count']):>2}/{int(item['cross_session_eval_count']):<3} "
                f"{','.join(flags)}"
            )
    return {
        "total_hypotheses": len(rows),
        "single_witness_high_mass": single_witness_high_mass,
        "self_evaluated_only": self_eval_only,
        "unexamined_active": unexamined_active,
        "hypotheses": rows,
    }


# ---------------------------------------------------------------- main



READ_ID_RE = re.compile(r"READ-\d{8}-[0-9a-f]{6}")
CONTEST_NAMING_RE = re.compile(r"READ-\d{8}-[0-9a-f]{6}|異議|反論|contest|前回|以前|§|「|主張")
# A later reading *answers* a contest only if it names the contest itself: the
# contested READ id, or an explicit word for disagreeing.  Quotation marks and
# section references are deliberately excluded here; they made the count rise
# from 98 to 265 without any reading changing.
CONTEST_ANSWER_RE = re.compile(r"異議|反論|contest|問い直|疑いを|却下|斥け")


def _is_mechanical(row: dict) -> bool:
    return str(row.get("note") or "").startswith("機械的")


def _forward_label_ids(sessions: list[dict], *, root: Path) -> set[str]:
    """Session IDs whose date stamp is an internal chronology label, not a date.

    Two pieces of ledger evidence, both independent of today's date (the same two
    `validate_seed` uses; see `_is_internal_label` and
    `build_forward_label_evidence`):

    1. **Where the row sits.** A row stamped 2026-12-05 cannot have been written
       into a shard named 2026-11-21 -- the shard date is when it was written, the
       stamp is what the writer chose. A stamp later than its own shard is a label.
    2. **What a real-dated session was offered.** If a session whose shard proves
       it ran on day D was offered a question stamped after D, that question
       already existed on D, so its stamp is a label. Nothing else explains a
       receipt naming a future question.

    Returns the set of session IDs to exempt. A row the evidence does not reach is
    left gated, which is the safe direction: the gate stays on where it can be
    trusted, and nothing is exempted merely because it is old.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import ledger_io

    ids: set[str] = set()
    base = Path(root) / "state" / "sessions.jsonl"
    shard_stamp: dict[str, str] = {}
    # Anchor to the leading YYYY-MM-DD. A bare search for 8 digits matches the
    # shard's hex suffix as often as its date (2026-11-21-abc12345.jsonl would
    # yield "abc12345" only if it were digits, and 2026-11-08-0f7d4cfd78ce yields
    # "0f7d4cfd" never but "20261108" only when anchored) -- the same trap that
    # made an early version of this fix report zero labels.
    for path in ledger_io.collection_files(base):
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})-", path.name)
        if not match:
            continue
        day = "".join(match.groups())
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = row.get("session_id")
            if isinstance(sid, str):
                shard_stamp.setdefault(sid, day)

    def stamp_of(record_id: str) -> str:
        match = re.search(r"(\d{8})", record_id or "")
        return match.group(1) if match else ""

    # (1) stamp later than the shard it sits in
    for session in sessions:
        sid = str(session.get("session_id") or "")
        stamp, shard = stamp_of(sid), shard_stamp.get(sid, "")
        if stamp and shard and stamp > shard:
            ids.add(sid)

    # (2) a real-dated session was offered a forward-stamped question
    for session in sessions:
        sid = str(session.get("session_id") or "")
        shard = shard_stamp.get(sid, "")
        offered = session.get("offered_target_question_id")
        if not shard or not isinstance(offered, str):
            continue
        off_stamp = stamp_of(offered)
        if off_stamp and off_stamp > shard:
            ids.add(sid)
    return ids


def report_contests(read_log: list[dict], *, out) -> dict:
    """How often the archive contests its own records, and whether the contest lands.

    A ``contested`` row is a reading with a sign: it says the record was read
    against itself.  Three things are counted, because they come apart: how
    many readings are contests; how many contests name the claim they contest
    (a READ-* id is the only machine-readable address the ledger has); and how
    many are *answered* — followed, in another session, by a reading whose note
    names the contest.  Nothing here judges whether a contest was right.
    """
    hand = [r for r in read_log if not _is_mechanical(r)]
    contests = [r for r in hand if r.get("reading") == "contested"]
    by_type = Counter(_target_type_of(r) for r in contests)

    citing = [r for r in contests if READ_ID_RE.search(str(r.get("note") or ""))]
    naming = [r for r in contests if CONTEST_NAMING_RE.search(str(r.get("note") or ""))]
    any_citing = [r for r in hand if READ_ID_RE.search(str(r.get("note") or ""))]

    rows_by_target: dict[tuple[str, str], list[dict]] = {}
    for row in hand:
        target = row.get("target") or {}
        if not isinstance(target, dict) or not target.get("id"):
            continue
        rows_by_target.setdefault((str(target.get("type")), str(target["id"])), []).append(row)

    addressed = [r for r in contests if r.get("in_reply_to")]
    field_cited = [r for r in hand if r.get("in_reply_to")]

    followed = answered = answered_by_field = 0
    for rows in rows_by_target.values():
        rows = sorted(rows, key=lambda r: str(r.get("created_at") or ""))
        for i, row in enumerate(rows):
            if row.get("reading") != "contested":
                continue
            later = [x for x in rows[i + 1:] if x.get("session_id") != row.get("session_id")]
            if later:
                followed += 1
                rid = str(row.get("read_id") or "")
                if any((rid and rid in str(x.get("note") or "")) or
                       CONTEST_ANSWER_RE.search(str(x.get("note") or "")) for x in later):
                    answered += 1
                if rid and any(rid in (x.get("in_reply_to") or []) for x in later):
                    answered_by_field += 1

    out(f"hand-written readings           : {len(hand)}")
    out(f"contested readings              : {len(contests)}"
        f"  ({len(contests) / max(len(hand), 1) * 100:.1f}% of hand-written)")
    out("  by target type: " + ", ".join(f"{k}={v}" for k, v in by_type.most_common()))
    out(f"contest names what it contests   : {len(naming)} / {len(contests)}"
        f"  ({len(naming) / max(len(contests), 1) * 100:.1f}%)")
    out(f"contest cites a READ-* id        : {len(citing)} / {len(contests)}"
        f"  ({len(citing) / max(len(contests), 1) * 100:.1f}%)")
    out(f"rows anywhere citing a READ-* id : {len(any_citing)} / {len(hand)}"
        f"  ({len(any_citing) / max(len(hand), 1) * 100:.1f}%)")
    out(f"contest addressed via in_reply_to           : {len(addressed)} / {len(contests)}"
        f"  ({len(addressed) / max(len(contests), 1) * 100:.1f}%)")
    out(f"any hand row addressed via in_reply_to      : {len(field_cited)} / {len(hand)}"
        f"  ({len(field_cited) / max(len(hand), 1) * 100:.1f}%)")
    out(f"contest followed by another session's reading : {followed} / {len(contests)}"
        f"  ({followed / max(len(contests), 1) * 100:.1f}%)")
    out(f"contest named by that later reading           : {answered} / {len(contests)}"
        f"  ({answered / max(len(contests), 1) * 100:.1f}%)")
    out(f"contest answered through in_reply_to          : {answered_by_field} / {len(contests)}"
        f"  ({answered_by_field / max(len(contests), 1) * 100:.1f}%)")
    out("  註: 「名指す」は註の語彙（READ id・異議・前回・§・引用）で判定した近似的な数。")
    out("  註: in_reply_to は 2026-11-17 に足した欄なので、それ以前の行は 0 件で正しい。")
    return {
        "handwritten": len(hand),
        "contested": len(contests),
        "by_target_type": dict(by_type),
        "naming": len(naming),
        "citing_read_id": len(citing),
        "any_citing_read_id": len(any_citing),
        "addressed_by_field": len(addressed),
        "any_addressed_by_field": len(field_cited),
        "followed": followed,
        "answered": answered,
        "answered_by_field": answered_by_field,
    }


def _target_type_of(row: dict) -> str:
    target = row.get("target") or {}
    return str(target.get("type") or "(none)") if isinstance(target, dict) else "(none)"


ROLE_FIELDS = ("dispersal_seed", "assigned_role", "offered_target_question_id",
               "offered_reference_mode")


def report_roles(sessions: list[dict], read_log: list[dict], *, root: Path, out) -> dict:
    """Who was told to do what, and did the ledger keep the receipt?

    The charter splits inquiry into proposer 25 / adversarial tester 50 /
    consolidator 25. The ledger can only check that split if session rows carry
    ``assigned_role``, which they mostly do not. Two numbers are printed: the
    coverage of the receipt (all sessions, and only those minted since the
    receipt became required on 2026-11-18) and the contested-reading rate inside
    each role. The second is the one that matters: if the role label did not
    predict anything, recording it would be decoration.
    """
    roles: dict[str, int] = Counter()
    contested: dict[str, int] = Counter()
    rows_by_role: dict[str, int] = Counter()
    missing_recent: list[str] = []
    session_ids = {s.get("session_id") for s in sessions}
    by_session = {s.get("session_id"): s for s in sessions}

    for session in sessions:
        role = str(session.get("assigned_role") or "")
        if role:
            roles[role] += 1

    for row in read_log:
        if str(row.get("note") or "").startswith("機械的"):
            continue
        session = by_session.get(row.get("session_id")) or {}
        role = str(session.get("assigned_role") or "(no role recorded)")
        rows_by_role[role] += 1
        if row.get("reading") == "contested":
            contested[role] += 1

    # Only real dates count, and "real" is decided by the ledger, not by the
    # clock. 187 session IDs carry internal chronology labels in 2026-12..2027 and
    # are exempt everywhere else in the repository (tools/date_axis.py,
    # validate_seed._is_new_row), so they are exempt here.
    #
    # This used to be `"20261118" <= stamp <= datetime.date.today()`. That is a
    # MOVING bound: a session stamped 2026-12-05 was exempt on 2026-11-21 and
    # became a "recent" compliance failure the moment the calendar passed it, with
    # no commit changing. The same defect was repaired in validate_seed on
    # 2026-11-21 (readings/2026-11-21-the-refusal-that-was-not-a-refusal.md §2) and
    # this tool was named as still carrying it in that report's §6 and twice more
    # after. It is repaired here the same way: a label is a stamp that disagrees
    # with where the row physically sits.
    label_ids = _forward_label_ids(sessions, root=root)
    for session in sessions:
        sid = str(session.get("session_id") or "")
        match = re.search(r"(\d{8})", sid)
        stamp = match.group(1) if match else ""
        if not stamp or stamp < "20261118":
            continue
        if sid in label_ids:
            # A forward label is not a recent row, so it cannot be a recent gap.
            continue
        gaps = [f for f in ROLE_FIELDS if not str(session.get(f) or "").strip()]
        if gaps:
            missing_recent.append(sid)

    total = len(session_ids)
    with_role = sum(roles.values())
    out(f"sessions                        : {total}")
    out(f"assigned_role recorded          : {with_role}"
        f"  ({with_role / max(total, 1) * 100:.1f}%)")
    out(f"all four receipt fields         : "
        f"{sum(1 for s in sessions if all(str(s.get(f) or '').strip() for f in ROLE_FIELDS))}")
    if roles:
        out("  recorded roles: " + ", ".join(f"{k}={v}" for k, v in roles.most_common()))
        out("  charter split : proposer 25% / adversarial_tester 50% / consolidator 25%")
        out("")
        out("contested share of hand-written readings, by the role of the reading session:")
        for role, n in rows_by_role.most_common():
            out(f"  {role:<20} {contested[role]:>4} / {n:>5}  "
                f"({contested[role] / max(n, 1) * 100:5.1f}%)")
    out("")
    if missing_recent:
        out(f"new session rows (2026-11-18+) missing a receipt: {len(missing_recent)}")
        for sid in missing_recent[:5]:
            out(f"  - {sid}")
    else:
        out("new session rows (2026-11-18+) missing a receipt: 0 "
            "(validate_seed now refuses them)")
    return {
        "sessions": total,
        "with_role": with_role,
        "roles": dict(roles),
        "readings_by_role": dict(rows_by_role),
        "contested_by_role": dict(contested),
        "missing_receipts_recent": missing_recent,
    }

def main(argv: list[str] | None = None) -> int:
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--works", action="store_true")
    ap.add_argument("--witnesses", action="store_true")
    ap.add_argument("--naming", action="store_true")
    ap.add_argument("--passages", action="store_true")
    ap.add_argument("--hypotheses", action="store_true")
    ap.add_argument("--roles", action="store_true",
                    help="how many session rows record the assignment receipt, and whether "
                         "the recorded role predicts anything (report only)")
    ap.add_argument("--contests", action="store_true",
                    help="how often readings contest their target, and whether the contest is "
                         "addressed or answered (report only)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)

    ROOT = Path(args.root)

    materials = load_rows("materials", "material_id")
    read_log = load_rows("read_log", "read_id")
    if not materials and not args.hypotheses:
        print("no materials found", file=sys.stderr)
        return 1

    every = not (args.works or args.witnesses or args.naming or args.passages
                 or args.hypotheses or args.contests or args.roles)
    payload: dict[str, object] = {}
    lines: list[str] = []

    def out(text: str = "") -> None:
        lines.append(text)

    if not args.json:
        out("=== 台帳が数えているものと、数えていないもの ===")
        out(f"materials {len(materials)} / read_log {len(read_log)}")
        out("")

    if every or args.works:
        if not args.json:
            out("--- 1. works vs rows ---")
        payload["works"] = report_works(materials, out=out)
        if not args.json:
            out("")
    if args.roles:
        if not args.json:
            out("--- 割り当ては、記録されたか ---")
        payload["roles"] = report_roles(load_rows("sessions", "session_id"), read_log, root=ROOT, out=out)
        if not args.json:
            out("")
    if args.contests:
        if not args.json:
            out("--- 異議は、届いているか ---")
        payload["contests"] = report_contests(read_log, out=out)
        if not args.json:
            out("")
    if every or args.witnesses:
        if not args.json:
            out("--- 2. witnesses vs rows ---")
        payload["witnesses"] = report_witnesses(materials, read_log, out=out)
        if not args.json:
            out("")
    if every or args.naming:
        if not args.json:
            out("--- 3. naming scheme vs survival ---")
        payload["naming"] = report_naming(materials, read_log, out=out)
        if not args.json:
            out("")
    if every or args.passages:
        if not args.json:
            out("--- 4. are same-URL rows duplicates? ---")
        payload["passages"] = report_passages(materials, out=out)
        if not args.json:
            out("")
    if every or args.hypotheses:
        if not args.json:
            out("--- 5. hypothesis witnesses (EVL_sess vs hand-written RL_sess) ---")
        payload["hypotheses"] = report_hypotheses(ROOT, out=out)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print("\n".join(lines))
        print()
        print("Which of these is a defect is not something this tool decides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
