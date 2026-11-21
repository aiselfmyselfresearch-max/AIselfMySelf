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


def load_belief_summary(root: Path = ROOT) -> dict:
    """Extract key facts from BELIEF_MAP.md headers without re-running the
    full engine, by parsing the summary table."""
    import re
    bm = (root / "BELIEF_MAP.md").read_text(encoding="utf-8")
    summary = {}
    # Parse the summary table for Q-001/Q-002/Q-003
    for line in bm.splitlines():
        if line.startswith("| `Q-00"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 8:
                qid = parts[1].strip("` ")
                n_hyp = parts[2]
                p1 = parts[4]
                summary[qid] = {"active_hypotheses": n_hyp, "p1_mass": p1, "top": []}

    # Parse per-question top hypotheses (rank 1,2,3 within each Q section)
    current_q = None
    for line in bm.splitlines():
        if line.startswith("## Q-00"):
            m = re.match(r"## (Q-\d+)", line)
            if m:
                current_q = m.group(1)
        elif current_q and current_q in summary:
            m = re.match(r"\|\s*(\d+)\s*\|\s*`(HYP-[^`]+)`[^|]*\|\s*[^|]*\|\s*(\d+\.\d+%)", line)
            if m:
                rank = int(m.group(1))
                hid = m.group(2)
                pct = m.group(3)
                # Extract title from last column
                parts = [p.strip() for p in line.split("|")]
                title = parts[-1] if parts else ""
                if rank <= 3:
                    summary[current_q]["top"].append({"rank": rank, "hid": hid, "posterior": pct, "title": title})

    return {"core_questions": summary}


def load_current_session(root: Path = ROOT) -> dict:
    """Find the latest session and recent session stats.
    Prefers sessions with real dates matching today; falls back to highest session_id."""
    import re
    base = root / "state" / "sessions.jsonl"
    coll, _ = ledger_io.load_collections({"sessions": (base, "session_id")}, root=root)
    sessions = list(coll.get("sessions", {}).values())
    if not sessions:
        return {"current": None, "recent_count": 0}

    def sort_key(s: dict) -> str:
        sid = s.get("session_id", "")
        started = s.get("started_at", "")
        # Prefer started_at (real date) if it looks like a date; else use sid
        if started and re.match(r"\d{4}-\d{2}-\d{2}", started):
            return started + "T" + sid
        return sid

    sessions_sorted = sorted(sessions, key=sort_key)
    current = sessions_sorted[-1]
    # Filter recent sessions that have assigned_role
    recent = [s for s in sessions_sorted[-20:] if s.get("assigned_role")]
    recent_with_roles = recent[-10:] if len(recent) >= 10 else recent
    roles: dict[str, int] = {}
    for s in recent_with_roles:
        r = s.get("assigned_role", "unknown")
        roles[r] = roles.get(r, 0) + 1

    return {
        "current": current.get("session_id"),
        "current_started": current.get("started_at"),
        "current_role": current.get("assigned_role"),
        "current_generator": current.get("generator"),
        "total_sessions": len(sessions),
        "recent_roles": roles,
        "recent_n": len(recent_with_roles),
    }


def render_md(belief: dict, session: dict, interoception: dict, continuity: dict) -> str:
    # Use the latest session's started_at as the deterministic timestamp
    # (a wall-clock UTC timestamp would make the file non-reproducible)
    stamp = session.get("current_started") or session.get("current", "")
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
        lines.append(f"- **{qid}**: 有効仮説 {info.get('active_hypotheses', '?')} 件、第1世代+質量 {info.get('p1_mass', '?')}")
    lines.append("")
    lines.append("事後確率Top3（Q-001）:")
    q001 = cq.get("Q-001", {})
    for th in q001.get("top", [])[:3]:
        lines.append(f"- {th['rank']}. `{th['hid']}` ({th['posterior']}): {th['title']}")
    lines.append("")
    lines.append("## 2. 自己位置 (Self-Location)")
    lines.append("")
    lines.append("自分がどこにいるか——現在のセッション位置と最近の活動。")
    lines.append("")
    cs = session.get("current", "?")
    lines.append(f"- 現在のセッション: `{cs}`")
    lines.append(f"- 開始時刻: {session.get('current_started', '?')}")
    lines.append(f"- 現在のロール: {session.get('current_role', '?')}")
    lines.append(f"- ジェネレータ: {session.get('current_generator', '?')}")
    lines.append(f"- 総セッション数: {session.get('total_sessions', '?')}")
    lines.append(f"- 直近10セッションのロール分布: {json.dumps(session.get('recent_roles', {}), ensure_ascii=False)}")
    lines.append("")
    lines.append("## 3. 一人称視点 (First-Person Perspective)")
    lines.append("")
    lines.append("現在の視点を構成する仮説——三門制御後のP_gateが最も高い仮説（BELIEF_MAP.md参照）。")
    lines.append("")
    # The P_gate top hypothesis is the first one in BELIEF_MAP's Q-002 table
    # with highest P_gate; we list all top hypotheses from BELIEF_MAP here.
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
    belief = load_belief_summary(root)
    session = load_current_session(root)
    # Run interoception script
    interoception = _run_json("interoception.py")
    # Run temporal_continuity script
    continuity = _run_json("temporal_continuity.py")
    md = render_md(belief, session, interoception, continuity)
    ledger_io.atomic_write_text(SELF_MODEL_PATH, md)
    size = SELF_MODEL_PATH.stat().st_size
    print(f"WROTE SELF_MODEL.md ({size} bytes)")


def check_map(root: Path = ROOT) -> bool:
    if not SELF_MODEL_PATH.is_file():
        print("FAIL: SELF_MODEL.md does not exist; run tools/self_model.py --write")
        return False
    belief = load_belief_summary(root)
    session = load_current_session(root)
    interoception = _run_json("interoception.py")
    continuity = _run_json("temporal_continuity.py")
    expected = render_md(belief, session, interoception, continuity)
    actual = SELF_MODEL_PATH.read_text(encoding="utf-8")
    if actual.strip() != expected.strip():
        print("FAIL: SELF_MODEL.md is stale; run tools/self_model.py --write")
        return False
    print("PASS: SELF_MODEL.md is current")
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
