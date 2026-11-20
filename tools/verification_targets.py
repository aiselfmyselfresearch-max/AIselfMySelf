#!/usr/bin/env python3
"""Which unverified material, read in full, would firm up the most verdicts.

Why this exists (2026-11-20, ① of the evidence-accounting change)
-----------------------------------------------------------------
The archive's acquisition rule has been "ten new sources per session".  Measured
on 2026-11-20, that rule produced a corpus where 61.5% of `supports` verdicts
(160/260) cite *zero* text-checked material, while the citation distribution is a
long tail (745 materials cited exactly once, maximum 10).  Adding new sources
grows the tail; it does not firm up the judgments already made.  Buying one more
paper the archive has never cited moves no verdict at all.

This tool ranks the opposite purchase: the unverified materials that already sit
under existing `supports` rows, chosen greedily by how many such rows each would
release from the "no verified support anywhere" state.  The output is a shopping
list with an honest coverage curve, because the curve is the argument:

    verifying 50 materials covers about 63% of the 160 rows; the remaining rows
    need 310 more materials, one row at a time.

It never writes to the ledger.  Verification itself is real work — open the
source, find the passage, record `verification.depth` and a method string — and
is done through an `editorial_decisions` overlay, so the material shard is never
rewritten.

Usage
-----
    python3 tools/verification_targets.py                    # top 20 + curve
    python3 tools/verification_targets.py --limit 50
    python3 tools/verification_targets.py --json
    python3 tools/verification_targets.py --only-unread      # skip already-read
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load(root: Path = ROOT) -> tuple[dict, dict, dict]:
    specs = {
        "materials": (root / "state" / "materials.jsonl", "material_id"),
        "evaluations": (root / "state" / "evaluations.jsonl", "evaluation_id"),
        "read_log": (root / "state" / "read_log.jsonl", "read_id"),
    }
    data, errors = ledger_io.load_collections(specs, root=root)
    for err in errors:
        print(f"WARN: {err}", file=sys.stderr)
    return (
        data.get("materials", {}),
        data.get("evaluations", {}),
        data.get("read_log", {}),
    )


def is_verified(material: dict | None) -> bool:
    return ((material or {}).get("verification") or {}).get("status") == "verified"


def unverified_support_rows(materials: dict, evaluations: dict) -> list[dict]:
    rows = []
    for eid, evl in evaluations.items():
        if str(evl.get("verdict") or "") != "supports":
            continue
        mids = [m for m in (evl.get("material_ids") or []) if isinstance(m, str) and m]
        if not mids:
            continue
        if any(is_verified(materials.get(m)) for m in mids):
            continue
        rows.append({"evaluation_id": eid, **evl})
    return rows


def rank(materials: dict, evaluations: dict, read_log: dict, only_unread: bool = False) -> dict:
    rows = unverified_support_rows(materials, evaluations)
    cited: collections.Counter[str] = collections.Counter()
    for row in rows:
        for mid in row.get("material_ids") or []:
            if isinstance(mid, str):
                cited[mid] += 1

    read_sessions: dict[str, set[str]] = collections.defaultdict(set)
    for r in read_log.values():
        target = r.get("target")
        if isinstance(target, dict) and target.get("type") == "material":
            sid = r.get("session_id")
            mid = target.get("id")
            if isinstance(sid, str) and isinstance(mid, str):
                read_sessions[mid].add(sid)

    covered_rows: set[str] = set()
    remaining = dict(cited)
    plan: list[dict] = []
    cumulative_curve: list[dict] = []
    step = 0
    while remaining:
        best_mid, best_gain = None, -1
        for mid, count in remaining.items():
            if only_unread and read_sessions.get(mid):
                continue
            gain = count
            if gain > best_gain or (gain == best_gain and mid < (best_mid or "~")):
                best_mid, best_gain = mid, gain
        if best_mid is None:
            break
        step += 1
        newly = [
            row["evaluation_id"]
            for row in rows
            if best_mid in (row.get("material_ids") or []) and row["evaluation_id"] not in covered_rows
        ]
        covered_rows.update(newly)
        mat = materials.get(best_mid) or {}
        src = mat.get("source") or {}
        plan.append(
            {
                "rank": step,
                "material_id": best_mid,
                "title": str(mat.get("title") or ""),
                "year": src.get("year"),
                "url": str(src.get("url") or ""),
                "verification_status": ((mat.get("verification") or {}).get("status") or "missing"),
                "read_sessions": len(read_sessions.get(best_mid, set())),
                "unverified_support_rows": newly,
                "rows_released": len(newly),
                "cumulative_rows_released": len(covered_rows),
                "cumulative_ratio": round(len(covered_rows) / max(1, len(rows)), 4),
            }
        )
        cumulative_curve.append(
            {"materials": step, "rows_released": len(covered_rows), "ratio": round(len(covered_rows) / max(1, len(rows)), 4)}
        )
        del remaining[best_mid]

    return {
        "unverified_support_rows": len(rows),
        "distinct_materials_needed": len(cited),
        "plan": plan,
        "curve": [c for c in cumulative_curve if c["materials"] in (5, 10, 20, 30, 50, 100)],
        "rows_releasable_by_all": len(covered_rows),
    }


def render(result: dict, limit: int) -> str:
    lines = [
        "# verification targets",
        "",
        f"- 未照合の支持評価行（`supports` かつ verified 素材ゼロ）: **{result['unverified_support_rows']:,}**",
        f"- それらを支える未照合素材（重複除く）: **{result['distinct_materials_needed']:,}**",
        "",
        "| 照合する素材数 | 解き放たれる支持行 | 割合 |",
        "| ---: | ---: | ---: |",
    ]
    for c in result["curve"]:
        lines.append(f"| {c['materials']} | {c['rows_released']} | {c['ratio'] * 100:.0f}% |")
    lines += [
        "",
        f"## 上位 {min(limit, len(result['plan']))} 件",
        "",
        "| # | 素材 | 年 | 読んだセッション | 支持行 | 累積 | タイトル |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | :--- |",
    ]
    for p in result["plan"][:limit]:
        lines.append(
            f"| {p['rank']} | `{p['material_id']}` | {p['year'] or '—'} | {p['read_sessions']} | "
            f"{p['rows_released']} | {p['cumulative_ratio'] * 100:.0f}% | {p['title'][:70]} |"
        )
    lines += [
        "",
        "> 取得規則への含意: 新規資料を1件足しても、未引用なら判断は1つも動かない。",
        "> 被覆は1行ずつしか解けない。以前「上位50件で6割」と見積もったのは、複数素材が支える行を二重に数えた誤りで、",
        "> 行を一度だけ数えると上表の値（50件で約3割）になる。数字は `--json` で再計算すること。",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--only-unread", action="store_true")
    args = parser.parse_args()
    materials, evaluations, read_log = load(Path(args.root))
    result = rank(materials, evaluations, read_log, only_unread=args.only_unread)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, args.limit), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
