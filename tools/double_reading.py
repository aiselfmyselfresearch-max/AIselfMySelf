#!/usr/bin/env python3
"""How much of the archive has been read twice, and where the two readings differ.

Why this exists (2026-11-20, ④ of the evidence-accounting change)
-----------------------------------------------------------------
An Arena session cannot choose which model it gets.  Model capability varies,
so the same archive is written by a shifting mixture of readers.  Almost every
mitigation available to a ledger like this one assumes the reader is a fixed
instrument; the only handle on a *changing* instrument is repetition.  When two
different sessions read the same material and record what they did with it, the
pair is a (weak, uncontrolled) two-draw experiment, and the disagreement rate
between draws is an estimate of how much of the corpus is model-dependent.

This tool measures that, and nothing more:

* **coverage** — how many materials have been read by two or more sessions.
  Materials read once have an agreement rate that is unknown, not perfect.
* **category disagreement** — the pairs where the two sessions recorded a
  different ``read_log.reading`` (``interpreted`` vs ``reinterpreted``,
  ``summarized`` vs ``contested``, ...).  Two readers who both wrote
  ``interpreted`` may still disagree about the content; agreement here is an
  upper bound on real agreement, never a lower one.
* **stratified disagreement** — the disagreement rate split by the material's
  ``verification.depth``.  Read depth of the *source* and agreement about the
  *reading act* are different axes; this split shows whether deeper source
  verification comes with fewer category mismatches (2026-11-21: it does not).
* **adjudication coverage** — among materials with a disagreeing pair, how many
  are touched by an errata row or an editorial-decision overlay.  ``touched`` is
  coverage, not resolution: a row that merely names the material counts.
* **direction changes** — pairs where an earlier reading was ``interpreted`` and
  the later one is ``contested`` or ``reinterpreted``.  That is the shape a
  genuine correction takes, and it is also the shape an unlucky model draw takes.
  The tool cannot tell them apart; it only counts them, so a later session knows
  how much of the archive was already re-read rather than merely re-cited.

It never modifies the ledger.  The numbers it prints are meant to be quoted with
the command, the way ``EVL-*`` rows quote ``script_command``.

Usage
-----
    python3 tools/double_reading.py                 # summary + top materials
    python3 tools/double_reading.py --json          # machine-readable
    python3 tools/double_reading.py --limit 40      # longer table
    python3 tools/double_reading.py --material MAT-20261120-53daa6
"""

from __future__ import annotations

import argparse
import collections
import re
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MANUAL_READINGS = frozenset(
    {"quoted", "summarized", "interpreted", "reinterpreted", "contested", "counted"}
)
#: Readings that carry an explicit verdict about an earlier reading.
REVISING_READINGS = frozenset({"reinterpreted", "contested"})


def load(root: Path = ROOT) -> tuple[dict, dict]:
    specs = {
        "materials": (root / "state" / "materials.jsonl", "material_id"),
        "read_log": (root / "state" / "read_log.jsonl", "read_id"),
    }
    data, errors = ledger_io.load_collections(specs, root=root)
    if errors:
        for err in errors:
            print(f"WARN: {err}", file=sys.stderr)
    return data.get("materials", {}), data.get("read_log", {})


def material_readings(read_log: dict) -> dict[str, list[dict]]:
    """Manual readings per material, ordered by date then session."""
    per: dict[str, list[dict]] = collections.defaultdict(list)
    for row in read_log.values():
        if row.get("reading") not in MANUAL_READINGS:
            continue
        target = row.get("target")
        if not isinstance(target, dict) or target.get("type") != "material":
            continue
        mid = target.get("id")
        if not isinstance(mid, str) or not mid:
            continue
        per[mid].append(row)
    for rows in per.values():
        rows.sort(key=lambda r: (str(r.get("created_at") or ""), str(r.get("session_id") or "")))
    return per


def adjudicated_materials(root: Path) -> set[str]:
    """Material ids named by an errata row or an editorial-decision overlay.

    Coverage, not resolution: a row that merely names the material counts.
    """
    touched: set[str] = set()
    specs = (
        (root / "state" / "errata.jsonl", root / "state" / "errata.d"),
        (root / "state" / "editorial_decisions.jsonl", root / "state" / "editorial_decisions.d"),
    )
    for base, shard_dir in specs:
        paths = [base]
        if shard_dir.is_dir():
            paths.extend(sorted(shard_dir.glob("*.jsonl")))
        for path in paths:
            if not path.is_file():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                blob = json.dumps(row, ensure_ascii=False)
                target = row.get("target")
                if isinstance(target, dict) and isinstance(target.get("id"), str):
                    touched.add(target["id"])
                subject = row.get("subject_id")
                if isinstance(subject, str) and subject.startswith("MAT-"):
                    touched.add(subject)
                for mid in re.findall(r"MAT-[A-Za-z0-9-]+", blob):
                    touched.add(mid)
    return touched


def analyse(materials: dict, read_log: dict, limit: int = 15, adjudication_coverage: dict | None = None) -> dict:
    per = material_readings(read_log)
    multi: dict[str, list[dict]] = {}
    for mid, rows in per.items():
        sessions = {r.get("session_id") for r in rows if isinstance(r.get("session_id"), str)}
        if len(sessions) >= 2:
            multi[mid] = rows

    pair_total = 0
    pair_disagree = 0
    direction_changes = 0
    label_pairs: collections.Counter = collections.Counter()
    by_depth: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    disagree_materials: set[str] = set()
    rows_out: list[dict] = []
    for mid, rows in multi.items():
        by_session: dict[str, dict] = {}
        for r in rows:
            sid = r.get("session_id")
            if isinstance(sid, str) and sid not in by_session:
                by_session[sid] = r
        session_rows = list(by_session.values())
        disagree_here = 0
        changed_here = 0
        for i in range(len(session_rows)):
            for j in range(i + 1, len(session_rows)):
                a, b = session_rows[i], session_rows[j]
                pair_total += 1
                if a.get("reading") != b.get("reading"):
                    pair_disagree += 1
                    disagree_here += 1
                    disagree_materials.add(mid)
                    label_pairs[tuple(sorted((str(a.get("reading")), str(b.get("reading")))))] += 1
                depth_now = ((materials.get(mid) or {}).get("verification") or {}).get("depth") or "—"
                by_depth[str(depth_now)][1 if a.get("reading") != b.get("reading") else 0] += 1
                ords = {a.get("reading"), b.get("reading")}
                if "interpreted" in ords and (ords & REVISING_READINGS):
                    direction_changes += 1
                    changed_here += 1
        mat = materials.get(mid) or {}
        ver = (mat.get("verification") or {})
        rows_out.append(
            {
                "material_id": mid,
                "title": str(mat.get("title") or ""),
                "sessions": len(by_session),
                "readings": len(rows),
                "disagreements": disagree_here,
                "direction_changes": changed_here,
                "verification_status": ver.get("status") or "missing",
                "verification_depth": ver.get("depth"),
                "categories": sorted({str(r.get("reading")) for r in rows}),
            }
        )
    rows_out.sort(key=lambda r: (-r["disagreements"], -r["sessions"], r["material_id"]))

    return {
        "materials_with_manual_reading": len(per),
        "materials_read_by_two_or_more_sessions": len(multi),
        "coverage_ratio": round(len(multi) / max(1, len(per)), 4),
        "session_pairs": pair_total,
        "pairs_with_different_reading_category": pair_disagree,
        "category_disagreement_ratio": round(pair_disagree / max(1, pair_total), 4),
        "direction_change_pairs": direction_changes,
        "materials_with_direction_change": sum(1 for r in rows_out if r["direction_changes"]),
        "materials_with_full_text_depth": sum(
            1 for r in rows_out if r["verification_depth"] in ("full_text", "re_derived")
        ),
        "disagreement_by_depth": {
            d: {"agree": v[0], "disagree": v[1], "total": v[0] + v[1]}
            for d, v in sorted(by_depth.items())
        },
        "disagreeing_label_pairs": [
            {"readings": list(k), "pairs": v} for k, v in label_pairs.most_common(12)
        ],
        "adjudication_coverage": adjudication_coverage,
        "disagreeing_materials": len(disagree_materials),
        "_disagree_ids": disagree_materials,
        "top_materials": rows_out[:limit],
    }


def render(result: dict, materials: dict) -> str:
    lines = [
        "# double reading",
        "",
        f"- 手読みのある素材: **{result['materials_with_manual_reading']:,}**",
        f"- うち 2 セッション以上が読んだ素材: **{result['materials_read_by_two_or_more_sessions']:,}** "
        f"({result['coverage_ratio'] * 100:.1f}%)",
        f"- セッション対: **{result['session_pairs']:,}** / 読みの種類が食い違う対: "
        f"**{result['pairs_with_different_reading_category']:,}** "
        f"({result['category_disagreement_ratio'] * 100:.1f}%)",
        f"- 方向転換の対（interpreted → reinterpreted/contested）: **{result['direction_change_pairs']:,}** "
        f"/ 該当素材 **{result['materials_with_direction_change']:,}**",
        f"- そのうち verification.depth が full_text/re_derived の素材: "
        f"**{result['materials_with_full_text_depth']:,}**",
        "",
        "## 食い違いの層別（verification.depth ごとの対）",
        "",
        "| depth | 一致 | 食い違い | 食い違い率 |",
        "| :--- | ---: | ---: | ---: |",
    ]
    for d, v in result["disagreement_by_depth"].items():
        ratio = v["disagree"] / max(1, v["total"])
        lines.append(f"| {d} | {v['agree']} | {v['disagree']} | {ratio * 100:.1f}% |")
    lines += [
        "",
        "> `reading` の種類はそのセッションが**した作業**（引用・要約・再解釈・異議）であって内容の判定ではない。",
        "> 原文の読了深度と作業の一致は別の軸であり、深い照合が食い違い率を下げることをこの表は示さない。",
        "",
        "## 食い違う組み合わせ上位",
        "",
        "| 読みの組 | 対数 |",
        "| :--- | ---: |",
    ]
    for r in result["disagreeing_label_pairs"]:
        lines.append(f"| {r['readings'][0]} × {r['readings'][1]} | {r['pairs']} |")
    lines += [
        "",
        "## 裁定の届き方（coverage, not resolution）",
        "",
    ]
    if result.get("adjudication_coverage") is not None:
        cov = result["adjudication_coverage"]
        lines.append(
            f"- 食い違いのある素材 **{result['disagreeing_materials']:,}** のうち、訂正録または編集判断が"
            f"名指しているもの: **{cov['touched']:,}**（{cov['ratio'] * 100:.1f}%）。"
        )
        lines.append("")
        lines.append("> 「名指しされている」だけの数え方である。対立する二つの読みのどちらが正しいと裁定されたかは数えていない。")
    else:
        lines.append("- （このカバレッジは errata / editorial_decisions を読む必要がある。`adjudicated_materials()` を参照。）")
    lines += [
        "",
        "> 一致率は**上限**である。二人が同じ `interpreted` と書いても内容が同じとは限らない。",
        "> 方向転換は「訂正」と「不運なモデル抽選」の両方の形をしており、この道具は区別しない。",
        "",
        "## 食い違いの多い素材",
        "",
        "| 素材 | セッション | 読み | 食い違い | 方向転換 | 照合 | タイトル |",
        "| :--- | ---: | ---: | ---: | ---: | :--- | :--- |",
    ]
    for r in result["top_materials"]:
        depth = r["verification_depth"] or "—"
        lines.append(
            f"| `{r['material_id']}` | {r['sessions']} | {r['readings']} | {r['disagreements']} | "
            f"{r['direction_changes']} | {r['verification_status']}/{depth} | {r['title'][:60]} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--material", help="print every manual reading recorded for one material")
    args = parser.parse_args()
    root = Path(args.root)
    materials, read_log = load(root)

    if args.material:
        per = material_readings(read_log)
        rows = per.get(args.material)
        if not rows:
            print(f"no manual reading recorded for {args.material}")
            return 1
        for r in rows:
            print(f"{r.get('created_at')} {r.get('session_id')} {r.get('reading'):14s} {r.get('note', '')[:70]}")
        return 0

    result = analyse(materials, read_log, limit=args.limit)
    disagree_ids = result.pop("_disagree_ids", set())
    touched = adjudicated_materials(root) & disagree_ids
    dis = result["disagreeing_materials"]
    result["adjudication_coverage"] = {
        "touched": len(touched),
        "ratio": round(len(touched) / max(1, dis), 4),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, materials), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
