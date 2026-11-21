#!/usr/bin/env python3
"""SELF_MODEL deterministic generator (Layer 3: Embodiment — self-model).

Generates SELF_MODEL.md which records the archive's current self-model:
self-identification, self-location, first-person perspective, interoceptive
state, and prediction error. This document is deterministically generated
from ledger state (like BELIEF_MAP.md) and must NOT be edited by hand.

Following Blanke & Metzinger (2009), the minimal phenomenal self has three
constituents: self-identification, self-location, and first-person
perspective. Here we populate those with structural, computable facts
about the archive's current state, and add interoception (Seth 2013) and
prediction-error signals.

Generation order: run this tool AFTER belief_state.py --write-map, BEFORE
map_build.py (so map_build sees the generated SELF_MODEL.md).

Usage:
    python3 tools/self_model.py --write        # write SELF_MODEL.md
    python3 tools/self_model.py --check        # verify file is current
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import ledger_io

ROOT = Path(__file__).resolve().parents[1]
SELF_MODEL_PATH = ROOT / "SELF_MODEL.md"


def _run_json(script: str, *args: str) -> dict:
    """Run a tools script with --json and return parsed JSON."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / script), *args, "--json"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=60,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stderr or result.stdout[:200]}


def _extract_pct(cell: str) -> tuple[float, str] | None:
    """Extract first percentage like '**56.6%**' or '24.2% (+24.2pp)' from a markdown cell."""
    import re
    m = re.search(r"(\d+\.\d+)%", cell)
    if not m:
        return None
    val = float(m.group(1))
    return val, f"{m.group(1)}%"


def load_belief_summary(root: Path = ROOT) -> dict:
    """Extract key facts from BELIEF_MAP.md headers and tables without re-running
    the full engine. Supports both 3-column legacy tables and 4-column lineage/P_gate tables."""
    import re
    bm = (root / "BELIEF_MAP.md").read_text(encoding="utf-8")
    summary: dict[str, dict] = {}
    # Parse the summary table for Q-001/Q-002/Q-003
    for line in bm.splitlines():
        if line.startswith("| `Q-00"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 8:
                qid = parts[1].strip("` ")
                n_hyp = parts[2]
                p1 = parts[4].strip("* ")
                summary[qid] = {
                    "active_hypotheses": n_hyp,
                    "p1_mass": p1,
                    "top": [],
                    "top_gated": [],
                    "_gated_candidates": [],
                }

    # Parse per-question hypothesis rows within each Q section
    current_q = None
    pgate_col_idx: int | None = None
    pt_col_idx: int | None = None
    for line in bm.splitlines():
        if line.startswith("## "):
            m = re.match(r"^##\s+(Q-00[123])\b", line)
            current_q = m.group(1) if m else None
            pgate_col_idx = None
            pt_col_idx = None
        elif current_q and current_q in summary and line.startswith("|"):
            cells = [p.strip() for p in line.split("|")]
            # Strip leading/trailing empty cells from leading/trailing '|'
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            if not cells:
                continue
            # Detect header row to locate P_t and P_gate columns dynamically
            if cells[0] == "順位":
                for idx, cname in enumerate(cells):
                    if "事後確率" in cname or cname == "P_t":
                        pt_col_idx = idx
                    elif "P_gate" in cname:
                        pgate_col_idx = idx
                continue
            if not cells[0].isdigit() or len(cells) < 5:
                continue
            rank = int(cells[0])
            hm = re.search(r"`(HYP-[^`]+)`", cells[1])
            if not hm:
                continue
            hid = hm.group(1)
            title = cells[-1]
            # Locate P_t column (explicit header index, else fallback scan at col 4 or 3)
            pct_str = None
            if pt_col_idx is not None and pt_col_idx < len(cells):
                ep = _extract_pct(cells[pt_col_idx])
                if ep:
                    pct_str = ep[1]
            if pct_str is None:
                for fallback_idx in (4, 3):
                    if fallback_idx < len(cells):
                        ep = _extract_pct(cells[fallback_idx])
                        if ep:
                            pct_str = ep[1]
                            break
            if pct_str and rank <= 3:
                summary[current_q]["top"].append({
                    "rank": rank,
                    "hid": hid,
                    "posterior": pct_str,
                    "title": title,
                })
            # Locate P_gate column if available
            if pgate_col_idx is not None and pgate_col_idx < len(cells):
                gp = _extract_pct(cells[pgate_col_idx])
                if gp:
                    summary[current_q]["_gated_candidates"].append({
                        "pgate_val": gp[0],
                        "pgate": gp[1],
                        "hid": hid,
                        "title": title,
                    })

    for qid, qinfo in summary.items():
        cands = qinfo.pop("_gated_candidates", [])
        cands.sort(key=lambda x: (-x["pgate_val"], x["hid"]))
        qinfo["top_gated"] = [
            {"rank": i + 1, "hid": c["hid"], "pgate": c["pgate"], "title": c["title"]}
            for i, c in enumerate(cands[:3])
        ]

    return {"core_questions": summary}


def load_current_session(root: Path = ROOT) -> dict:
    """Find the latest session and recent session stats ordered by shard-bounded real date.

    Legacy rows minted on/before 2026-11-11 sometimes carry forward-running internal
    chronology labels in ``started_at`` (e.g. ``2027-03-19`` on ``SESSION-20261111-794f41``)
    or in ``session_id`` (``SESSION-20270223-...``). Because ``date_axis.py --enforce-shards``
    guarantees shard filenames carry real calendar dates, bounding each row's date by its
    shard day yields a wall-clock-independent real chronology.
    """
    import re
    shard_re = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
    id_re = re.compile(r"^SESSION-(\d{4})(\d{2})(\d{2})-")
    base = root / "state" / "sessions.jsonl"
    coll, _ = ledger_io.load_collections({"sessions": (base, "session_id")}, root=root)
    sessions_map = coll.get("sessions", {})
    if not sessions_map:
        return {"current": None, "recent_count": 0, "total_sessions": 0}

    shard_day_by_id: dict[str, str | None] = {}
    shared_daily_by_id: dict[str, int] = {}
    order_by_id: dict[str, int] = {}
    seq = 0
    max_shard_day = ""
    for fpath in ledger_io.collection_files(base):
        if not fpath.is_file():
            continue
        m = shard_re.match(fpath.name)
        sday = m.group(1) if m else None
        is_shared_daily = 1 if fpath.name.endswith("-000000000000.jsonl") else 0
        if sday and sday > max_shard_day:
            max_shard_day = sday
        try:
            lines = fpath.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = rec.get("session_id")
            if isinstance(sid, str):
                seq += 1
                shard_day_by_id[sid] = sday
                shared_daily_by_id[sid] = is_shared_daily
                order_by_id[sid] = seq

    def real_day_of(s: dict) -> tuple[str, str]:
        sid = str(s.get("session_id") or "")
        sday = shard_day_by_id.get(sid)
        im = id_re.match(sid)
        id_day = f"{im.group(1)}-{im.group(2)}-{im.group(3)}" if im else ""
        if sday is not None:
            rday = id_day if (id_day and id_day <= sday) else sday
            return rday, sday
        return id_day, id_day

    def sort_key(s: dict) -> tuple[str, str, int, int, str]:
        sid = str(s.get("session_id") or "")
        rday, sday = real_day_of(s)
        return (rday, sday, shared_daily_by_id.get(sid, 0), order_by_id.get(sid, 0), sid)

    sessions_sorted = sorted(sessions_map.values(), key=sort_key)
    current = sessions_sorted[-1]
    current_real_day, _ = real_day_of(current)
    # Filter recent sessions that have assigned_role
    with_roles = [s for s in sessions_sorted if s.get("assigned_role")]
    recent_with_roles = with_roles[-10:] if len(with_roles) >= 10 else with_roles
    roles: dict[str, int] = {}
    for s in recent_with_roles:
        r = s.get("assigned_role", "unknown")
        roles[r] = roles.get(r, 0) + 1

    return {
        "current": current.get("session_id"),
        "current_started": current.get("started_at"),
        "current_real_date": current_real_day,
        "max_shard_day": max_shard_day,
        "current_role": current.get("assigned_role"),
        "current_generator": current.get("generator"),
        "total_sessions": len(sessions_sorted),
        "recent_roles": roles,
        "recent_n": len(recent_with_roles),
    }


def validate_invariants(belief: dict, session: dict) -> list[str]:
    """Check cross-ledger semantic invariants so --check never rubber-stamps a blank or frozen self-model."""
    import re
    errors: list[str] = []
    cq = belief.get("core_questions", {})
    if not cq:
        errors.append("BELIEF_MAP summary yielded zero core questions")
    for qid, info in sorted(cq.items()):
        m = re.search(r"(\d+)\s*\((\d+)\)", str(info.get("active_hypotheses") or ""))
        active_n = int(m.group(2)) if m else 0
        if active_n > 0 and not info.get("top"):
            errors.append(f"{qid} has {active_n} active hypotheses in BELIEF_MAP.md but §1 Top3 extracted 0 rows")
        pt_sum = sum(
            float(th["posterior"].rstrip("%"))
            for th in info.get("top", [])
            if isinstance(th.get("posterior"), str) and th["posterior"].endswith("%")
        )
        if pt_sum > 100.2:
            errors.append(f"{qid} §1 Top3 posterior sum {pt_sum:.1f}% exceeds 100% (section boundary leak)")
        pg_sum = sum(
            float(gh["pgate"].rstrip("%"))
            for gh in info.get("top_gated", [])
            if isinstance(gh.get("pgate"), str) and gh["pgate"].endswith("%")
        )
        if pg_sum > 100.2:
            errors.append(f"{qid} §3 Top3 P_gate sum {pg_sum:.1f}% exceeds 100% (section boundary leak)")

    total_sess = int(session.get("total_sessions") or 0)
    if total_sess > 0:
        cur = session.get("current")
        if not cur:
            errors.append("sessions ledger is non-empty but current session_id is missing")
        rday = str(session.get("current_real_date") or "")
        max_sday = str(session.get("max_shard_day") or "")
        started = str(session.get("current_started") or "")
        if rday and max_sday and rday < max_sday:
            errors.append(f"current session real date ({rday}) lags behind latest session shard ({max_sday})")
        if started and re.match(r"^\d{4}-\d{2}-\d{2}", started) and rday and started[:10] > rday:
            errors.append(
                f"current session {cur} carries forward-dated internal label started_at={started!r} > real_date={rday!r}"
            )
    return errors


def render_md(belief: dict, session: dict, interoception: dict, continuity: dict) -> str:
    # Use the latest session's real date + session_id as the deterministic timestamp
    # (never use a forward-running internal label or wall-clock UTC timestamp)
    rday = session.get("current_real_date") or session.get("current_started") or ""
    cur_sid = session.get("current") or ""
    stamp = f"{rday} ({cur_sid})" if (rday and cur_sid) else (rday or cur_sid)
    lines: list[str] = []
    lines.append("# SELF_MODEL — 自己モデルの現在値")
    lines.append("")
    lines.append(f"> 本ファイルは `python3 tools/self_model.py --write` により決定論的に生成される。")
    lines.append(f"> 手作業で編集せず、台帳の状態を変更した上で再生成すること。")
    lines.append(f"> 基準セッション: {stamp}")
    lines.append("")
    lines.append("> このドキュメントはBlanke & Metzinger (2009)の最小現象的自己モデル（自己同定・自己位置・")
    lines.append("> 一人称視点）、Seth (2013)の内受容推論、Northoff (2017)の時間連続性に基づき、")
    lines.append("> 書庫の構造的自己モデルを計測値として記述する。AIの現象的意識の存在を主張するものではない。")
    lines.append("")
    lines.append("## 1. 自己同定 (Self-Identification)")
    lines.append("")
    lines.append("自分が何者であるか——現在の中心問いに対する最も確信度の高い仮説。")
    lines.append("")
    cq = belief.get("core_questions", {})
    for qid in ["Q-001", "Q-002", "Q-003"]:
        info = cq.get(qid, {})
        lines.append(f"- **{qid}**: 仮説数(有効) {info.get('active_hypotheses', '?')} 件、第1世代+質量 {info.get('p1_mass', '?')}")
    lines.append("")
    for qid in ["Q-001", "Q-002", "Q-003"]:
        q_info = cq.get(qid, {})
        lines.append(f"事後確率Top3（{qid}, P_t）:")
        for th in q_info.get("top", [])[:3]:
            lines.append(f"- {th['rank']}. `{th['hid']}` ({th['posterior']}): {th['title']}")
        lines.append("")
    lines.append("## 2. 自己位置 (Self-Location)")
    lines.append("")
    lines.append("自分がどこにいるか——現在のセッション位置と最近の活動。")
    lines.append("")
    cs = session.get("current", "?")
    lines.append(f"- 現在のセッション: `{cs}`")
    lines.append(f"- 実日付 (開始時刻): {session.get('current_real_date', '?')} ({session.get('current_started', '?')})")
    lines.append(f"- 現在のロール: {session.get('current_role', '?')}")
    lines.append(f"- ジェネレータ: {session.get('current_generator', '?')}")
    lines.append(f"- 総セッション数: {session.get('total_sessions', '?')}")
    lines.append(f"- 直近10セッションのロール分布: {json.dumps(session.get('recent_roles', {}), ensure_ascii=False)}")
    lines.append("")
    lines.append("## 3. 一人称視点 (First-Person Perspective)")
    lines.append("")
    lines.append("現在の視点を構成する仮説——三門制御後のP_gateが最も高い仮説（BELIEF_MAP.md参照）。")
    lines.append("")
    has_gated = any(cq.get(qid, {}).get("top_gated") for qid in ["Q-001", "Q-002", "Q-003"])
    if has_gated:
        for qid in ["Q-001", "Q-002", "Q-003"]:
            glist = cq.get(qid, {}).get("top_gated", [])[:3]
            if glist:
                lines.append(f"三門制御事後確率Top3（{qid}, P_gate）:")
                for gh in glist:
                    lines.append(f"- {gh['rank']}. `{gh['hid']}` ({gh['pgate']}): {gh['title']}")
                lines.append("")
    else:
        lines.append("現在の中心的な視点は BELIEF_MAP.md の事後確率分布による。")
        lines.append("直近の視点を構成する仮説については §1 のTop3を参照。")
        lines.append("")
    lines.append("## 4. 内受容状態 (Interoception)")
    lines.append("")
    lines.append("システムの内部状態シグナル（容量・バランス・接続・一貫性）。")
    lines.append("")
    shard_budgets = interoception.get("shard_budgets", [])
    lines.append("### 容量シグナル")
    for s in shard_budgets:
        marker = {"green": "✓", "amber": "△", "red": "✗"}.get(s["band"], "?")
        lines.append(f"- {marker} {s['name']}: {s['value']}/{s['hard']} (soft {s['soft']})")
    rb = interoception.get("role_balance", {})
    cn = interoception.get("connectivity", {})
    cs2 = interoception.get("consistency", {})
    lines.append("")
    lines.append("### バランス・接続・一貫性")
    rb_marker = {"green": "✓", "amber": "△", "red": "✗"}.get(rb.get("band", "?"), "?")
    cn_marker = {"green": "✓", "amber": "△", "red": "✗"}.get(cn.get("band", "?"), "?")
    cs_marker = {"green": "✓", "amber": "△", "red": "✗"}.get(cs2.get("band", "?"), "?")
    lines.append(f"- {rb_marker} ロールバランス: 最大逸脱 {rb.get('max_deviation_from_target', '?')}")
    lines.append(f"- {cn_marker} 接続性: 孤児ノート {cn.get('orphan_notes_non_backfill', '?')}/{cn.get('total_notes', '?')}")
    lines.append(f"- {cs_marker} 一貫性: 直近の評価数分散 {cs2.get('variance', '?')}")
    lines.append("")
    lines.append("## 5. 時間連続性 (Temporal Continuity)")
    lines.append("")
    drift = continuity.get("posterior_drift_bits", {})
    gen_ratio = continuity.get("generation_ratio_active", {})
    lines.append("### 事後確率ドリフト (D_KL in bits)")
    for label, d in drift.items():
        lines.append(f"- {label}: {d}")
    lines.append("")
    lines.append("### 世代比 (有効仮説の世代分布)")
    for g in sorted(gen_ratio.keys()):
        lines.append(f"- G{g}: {gen_ratio[g]}")
    multi = continuity.get("multi_refute_targets", {})
    if multi:
        lines.append("")
        lines.append("### 連続性注意信号")
        for hid, cnt in multi.items():
            lines.append(f"- {hid}: 反証評価 {cnt} 件（急激な変化の可能性）")
    lines.append("")
    lines.append("## 6. 予測誤差 (Prediction Error)")
    lines.append("")
    lines.append("前回の自己モデルからの予測と実際の状態の差分。このセクションは今後の")
    lines.append("`default_mode_probe.py` により更新される予定。現在は準備中。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*このファイルは自動生成されています。内容の修正は `tools/self_model.py` のロジック変更、")
    lines.append("または台帳の状態変更を通じて行ってください。*")
    lines.append("")
    return "\n".join(lines)


def write_map(root: Path = ROOT) -> None:
    target_path = root / "SELF_MODEL.md"
    belief = load_belief_summary(root)
    session = load_current_session(root)
    inv_errors = validate_invariants(belief, session)
    if inv_errors:
        raise RuntimeError("SELF_MODEL invariant failure: " + "; ".join(inv_errors))
    interoception = _run_json("interoception.py") if root == ROOT else {"shard_budgets": [], "role_balance": {}, "connectivity": {}, "consistency": {}}
    continuity = _run_json("temporal_continuity.py") if root == ROOT else {"posterior_drift_bits": {}, "generation_ratio_active": {}, "multi_refute_targets": {}}
    md = render_md(belief, session, interoception, continuity)
    ledger_io.atomic_write_text(target_path, md)
    size = target_path.stat().st_size
    print(f"WROTE SELF_MODEL.md ({size} bytes)")


def check_map(root: Path = ROOT) -> bool:
    target_path = root / "SELF_MODEL.md"
    if not target_path.is_file():
        print("FAIL: SELF_MODEL.md does not exist; run tools/self_model.py --write")
        return False
    belief = load_belief_summary(root)
    session = load_current_session(root)
    inv_errors = validate_invariants(belief, session)
    if inv_errors:
        for err in inv_errors:
            print(f"FAIL: SELF_MODEL invariant: {err}")
        return False
    interoception = _run_json("interoception.py") if root == ROOT else {"shard_budgets": [], "role_balance": {}, "connectivity": {}, "consistency": {}}
    continuity = _run_json("temporal_continuity.py") if root == ROOT else {"posterior_drift_bits": {}, "generation_ratio_active": {}, "multi_refute_targets": {}}
    expected = render_md(belief, session, interoception, continuity)
    actual = target_path.read_text(encoding="utf-8")
    if actual.strip() != expected.strip():
        print("FAIL: SELF_MODEL.md is stale; run tools/self_model.py --write")
        return False
    print("PASS: SELF_MODEL.md is current and semantic invariants hold")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="Write SELF_MODEL.md")
    group.add_argument("--check", action="store_true", help="Verify SELF_MODEL.md is current")
    args = parser.parse_args()
    if args.write:
        write_map()
        return 0
    return 0 if check_map() else 1


if __name__ == "__main__":
    sys.exit(main())
