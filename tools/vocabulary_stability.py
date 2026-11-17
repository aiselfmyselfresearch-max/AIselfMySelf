#!/usr/bin/env python3
"""Measure whether a stable evaluation vocabulary is doing any work.

The belief engine reads only the *form* of an evaluation row: verdict,
evidence_type, the named comparison set, the materials touched. It never reads
the prose. So an archive can keep filing well-formed rows, keep every label
appearing at the same rate, and look like it is converging while the rows stop
separating anything that was not already separated.

This tool measures that gap. It reads the ledgers and writes nothing.

Four numbers:

1. **Label concentration** — how few cells the verdict x evidence_type grid
   actually occupies. A stable vocabulary is, arithmetically, a small one.
2. **Unbacked label share** — rows labelled ``primary_source_collision`` whose
   cited materials the material ledger itself says were not read in full. The
   label claims a collision of primary texts; the verification status says the
   text was not read. This is a label-vs-ledger check, not a judgement of the
   reading.
3. **Separation novelty** — the share of rows that introduce a (target,
   comparison-set) pair no earlier row had separated. Repetition is not
   forbidden; the engine discounts it only within a session, so a cross-session
   repeat still pays.
4. **Least-separated pairs** — the pairs a given question has never put against
   each other, restricted to hypotheses with real posterior mass. This is the
   alternative to offering the highest expected-information-gain pair, which
   structurally prefers pairs containing the leader.

Usage:
  python3 tools/vocabulary_stability.py
  python3 tools/vocabulary_stability.py --question Q-003 --min-posterior 0.01
  python3 tools/vocabulary_stability.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import belief_state as bs  # noqa: E402

# A material counts as read in full only when the ledger says so. Anything else
# (partially_verified, unverified, absent) means the cited text was not fully
# read, whatever the evaluation row's label says.
FULL_READ_STATUSES = frozenset({"verified"})
UNBACKED_EVIDENCE_TYPES = ("primary_source_collision",)


def _verification(mats: dict[str, dict[str, Any]], material_id: str) -> str:
    rec = mats.get(material_id) or {}
    return str((rec.get("verification") or {}).get("status") or "none")


def label_profile(evals: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """How concentrated is the label grid, and in which cell?"""
    total = len(evals)
    if not total:
        return {"total": 0, "verdicts": {}, "evidence_types": {}, "cells": {}, "top_cell_share": 0.0}
    verdicts = Counter(str(e.get("verdict") or "supports") for e in evals.values())
    ev_types = Counter(str(e.get("evidence_type") or "cross_session_audit") for e in evals.values())
    cells = Counter(
        (str(e.get("verdict") or "supports"), str(e.get("evidence_type") or "cross_session_audit"))
        for e in evals.values()
    )
    top_cell, top_n = cells.most_common(1)[0]
    return {
        "total": total,
        "verdicts": dict(verdicts),
        "evidence_types": dict(ev_types),
        "cells": {f"{v}/{t}": n for (v, t), n in cells.most_common()},
        "top_cell": f"{top_cell[0]}/{top_cell[1]}",
        "top_cell_share": top_n / total,
        "grid_cells_used": len(cells),
        "grid_cells_possible": len(verdicts) * len(ev_types),
    }


def unbacked_label_share(
    evals: dict[str, dict[str, Any]],
    mats: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Rows whose label claims more about the sources than the sources' status allows."""
    per_type: dict[str, dict[str, Any]] = {}
    for etype in UNBACKED_EVIDENCE_TYPES:
        rows = [e for e in evals.values() if str(e.get("evidence_type") or "") == etype]
        unbacked = 0
        no_mats = 0
        for e in rows:
            mids = [m for m in (e.get("material_ids") or []) if isinstance(m, str)]
            if not mids:
                no_mats += 1
                continue
            if all(_verification(mats, m) not in FULL_READ_STATUSES for m in mids):
                unbacked += 1
        per_type[etype] = {
            "rows": len(rows),
            "unbacked": unbacked,
            "no_materials": no_mats,
            "share": (unbacked / len(rows)) if rows else 0.0,
        }
    return per_type


def separation_novelty(evals: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Share of rows that separate a (target, comparison-set) pair for the first time."""
    seen: set[tuple[str, tuple[str, ...]]] = set()
    ordered = sorted(
        evals.values(),
        key=lambda e: (str(e.get("created_at") or ""), str(e.get("evaluation_id") or "")),
    )
    total = new = 0
    by_day: dict[str, Counter] = defaultdict(Counter)
    for e in ordered:
        target = e.get("target_hypothesis_id")
        if not isinstance(target, str) or not target:
            continue
        compared = tuple(sorted(c for c in (e.get("compared_against_hypothesis_ids") or []) if isinstance(c, str)))
        key = (target, compared)
        day = str(e.get("created_at") or "")[:10]
        is_new = key not in seen
        seen.add(key)
        total += 1
        new += 1 if is_new else 0
        by_day[day]["rows"] += 1
        by_day[day]["new"] += 1 if is_new else 0
    return {
        "rows": total,
        "new_pairs": new,
        "share": (new / total) if total else 0.0,
        "by_day": {
            day: {
                "rows": c["rows"],
                "new_pairs": c["new"],
                "share": c["new"] / c["rows"] if c["rows"] else 0.0,
            }
            for day, c in sorted(by_day.items())
        },
    }


def separation_counts(evals: Iterable[dict[str, Any]]) -> tuple[Counter, dict[tuple[str, str], str]]:
    """How many rows have separated each unordered hypothesis pair, and when last."""
    counts: Counter = Counter()
    last: dict[tuple[str, str], str] = {}
    for e in evals:
        target = e.get("target_hypothesis_id")
        if not isinstance(target, str) or not target:
            continue
        for other in (e.get("compared_against_hypothesis_ids") or []):
            if not isinstance(other, str) or not other or other == target:
                continue
            key = tuple(sorted((target, other)))
            counts[key] += 1
            day = str(e.get("created_at") or "")[:10]
            if day > last.get(key, ""):
                last[key] = day
    return counts, last


def least_separated_pairs(
    state: dict[str, Any],
    evals: dict[str, dict[str, Any]],
    question_id: str,
    min_posterior: float = 0.01,
    limit: int = 5,
) -> dict[str, Any]:
    """Live pairs the question has never (or rarely) put against each other.

    ``min_posterior`` keeps the list from being dominated by hypotheses the
    archive has already eliminated: a pair with 0.0% on one side is unseparated
    but uninteresting -- separating it would not change what the archive
    currently holds.
    """
    qstate = (state.get("questions") or {}).get(question_id) or {}
    entries = [h for h in (qstate.get("hypotheses") or []) if h.get("effective_status") == "active"]
    posteriors = {h["hypothesis_id"]: float(h.get("posterior") or 0.0) for h in entries}
    eligible = [h["hypothesis_id"] for h in entries if float(h.get("posterior") or 0.0) >= min_posterior]
    counts, last = separation_counts(evals.values())
    rows = []
    for a, b in combinations(sorted(eligible), 2):
        key = tuple(sorted((a, b)))
        rows.append(
            {
                "left": key[0],
                "right": key[1],
                "separations": counts.get(key, 0),
                "last_separated": last.get(key, ""),
                "left_posterior": posteriors[key[0]],
                "right_posterior": posteriors[key[1]],
                "min_posterior": min(posteriors[key[0]], posteriors[key[1]]),
            }
        )
    rows.sort(key=lambda r: (r["separations"], -r["min_posterior"], r["left"], r["right"]))
    offered = qstate.get("top_competing_pair") or {}
    offered_pair = None
    if offered.get("left_hypothesis_id"):
        okey = tuple(sorted((offered["left_hypothesis_id"], offered["right_hypothesis_id"])))
        offered_pair = {
            "left": okey[0],
            "right": okey[1],
            "separations": counts.get(okey, 0),
            "expected_info_gain": offered.get("expected_info_gain"),
        }
    return {
        "question_id": question_id,
        "eligible_hypotheses": len(eligible),
        "eligible_pairs": len(rows),
        "never_separated_pairs": sum(1 for r in rows if r["separations"] == 0),
        "pairs_below_four_separations": sum(1 for r in rows if r["separations"] < 4),
        "least_separated": rows[:limit],
        "offered_by_eig": offered_pair,
    }


def build_report(
    root: Path = Path("."),
    question_id: str | None = None,
    min_posterior: float = 0.01,
) -> dict[str, Any]:
    data = bs.load_belief_ledgers(Path(root))
    evals = data.get("evaluations") or {}
    mats = data.get("materials") or {}
    state = bs.compute_belief_state(data=data)
    report: dict[str, Any] = {
        "labels": label_profile(evals),
        "unbacked": unbacked_label_share(evals, mats),
        "novelty": separation_novelty(evals),
    }
    if question_id:
        report["pairs"] = least_separated_pairs(state, evals, question_id, min_posterior=min_posterior)
    return report


def render(report: dict[str, Any]) -> str:
    out: list[str] = []
    labels = report["labels"]
    out.append("## 語彙の集中")
    out.append(
        f"- 評価行 {labels['total']} 件、使われたセル {labels['grid_cells_used']} 個"
        f"（観測された語の組み合わせに対して）。最頻セル `{labels.get('top_cell', '-')}` が "
        f"{labels['top_cell_share'] * 100:.1f}%。"
    )
    out.append(f"- verdict: {labels['verdicts']}")
    out.append(f"- evidence_type: {labels['evidence_types']}")
    out.append("")
    out.append("## ラベルが台帳に追いついているか")
    for etype, row in report["unbacked"].items():
        out.append(
            f"- `{etype}` {row['rows']} 行のうち {row['unbacked']} 行（{row['share'] * 100:.1f}%）は、"
            f"引用した素材がすべて全文未検証。素材を一つも引かない行は {row['no_materials']} 行。"
        )
    out.append("")
    nov = report["novelty"]
    out.append("## 分離の新規性")
    out.append(f"- 全 {nov['rows']} 行のうち、新しい (target, 比較集合) 対を持つ行は {nov['new_pairs']} 行（{nov['share'] * 100:.1f}%）。")
    for day, row in nov["by_day"].items():
        if row["rows"] >= 5:
            out.append(f"  - {day}: {row['rows']} 行中 {row['new_pairs']} 行が新規（{row['share'] * 100:.1f}%）")
    pairs = report.get("pairs")
    if pairs:
        out.append("")
        out.append(f"## まだ分離していない対（{pairs['question_id']}）")
        out.append(
            f"- P≥{0.01:.0%} の仮説 {pairs['eligible_hypotheses']} 件、対 {pairs['eligible_pairs']} 組。"
            f"うち一度も分離していない対 {pairs['never_separated_pairs']} 組、"
            f"分離 4 回未満 {pairs['pairs_below_four_separations']} 組。"
        )
        offered = pairs.get("offered_by_eig")
        if offered:
            out.append(
                f"- 現在 EIG 規則が提示する対: `{offered['left']}` vs `{offered['right']}` "
                f"（分離 {offered['separations']} 回、EIG {offered['expected_info_gain']}）"
            )
        out.append("- 分離回数の少ない順:")
        for row in pairs["least_separated"]:
            out.append(
                f"  - `{row['left']}` ({row['left_posterior'] * 100:.1f}%) vs "
                f"`{row['right']}` ({row['right_posterior'] * 100:.1f}%) — 分離 {row['separations']} 回、"
                f"最終 {row['last_separated'] or 'なし'}"
            )
    return "\n".join(out)



# --- reading vocabulary (2026-11-17, SESSION-20261117-...) -----------------
# The evaluation vocabulary above is read by the belief engine.  The *reading*
# vocabulary is not read by any engine: nothing compares `read_log.reading` to
# the note that accompanies it.  This section measures whether that vocabulary
# is doing work anyway, by asking which kind of object gets which label, and
# whether the pattern holds across the archive's internal months.
OWN_TYPES = ("fragment", "note", "question")
SOURCE_TYPES = ("material",)
READING_LABELS = ("interpreted", "reinterpreted", "summarized", "quoted",
                  "contested", "used_as_context", "counted", "declined")
MECHANICAL_PREFIXES = ("機械的バックフィル", "機械的接触行")


def _load_read_log(root: Path) -> list[dict[str, Any]]:
    import ledger_io
    specs = {"read_log": (Path(root) / "state" / "read_log.jsonl", "read_id")}
    collections, _errors = ledger_io.load_collections(specs, root=Path(root))
    return list(collections.get("read_log", {}).values())


def _target_type(row: dict[str, Any]) -> str:
    target = row.get("target") or {}
    return str(target.get("type") or "(none)") if isinstance(target, dict) else "(none)"


def reading_report(root: Path = Path(__file__).resolve().parent.parent,
                   read_log: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Label x object-type profile of the reading vocabulary, plus its stability.

    Mechanical rows (notes beginning 機械的…) are excluded, matching how the
    ledger's own tools treat hand-written readings.  The engine's exclusion
    marker is a single substring ("バックフィル"); this function reports how many
    rows each rule excludes, so that the difference is visible rather than
    assumed.
    """
    rows = read_log if read_log is not None else _load_read_log(root)
    hand = [r for r in rows if not str(r.get("note") or "").startswith(MECHANICAL_PREFIXES)]
    table: dict[str, dict[str, int]] = {}
    for row in hand:
        table.setdefault(_target_type(row), {}).setdefault(str(row.get("reading")), 0)
        table[_target_type(row)][str(row.get("reading"))] += 1

    def share(subset: list[dict[str, Any]], label: str) -> float:
        return sum(1 for r in subset if r.get("reading") == label) / len(subset) if subset else 0.0

    months: dict[str, dict[str, Any]] = {}
    for row in hand:
        stamp = str(row.get("created_at") or "")[:7]
        kind = _target_type(row)
        if kind in OWN_TYPES:
            months.setdefault(stamp, {"own": [], "source": []})["own"].append(row)
        elif kind in SOURCE_TYPES:
            months.setdefault(stamp, {"own": [], "source": []})["source"].append(row)
    by_month = {}
    for stamp, slot in sorted(months.items()):
        own, source = slot["own"], slot["source"]
        if len(own) < 20 or len(source) < 20:
            continue
        by_month[stamp] = {
            "own_rows": len(own),
            "source_rows": len(source),
            "own_reinterpreted": round(share(own, "reinterpreted"), 3),
            "source_reinterpreted": round(share(source, "reinterpreted"), 3),
            "gap_pp": round(100 * (share(own, "reinterpreted") - share(source, "reinterpreted")), 1),
        }

    own_rows = [r for r in hand if _target_type(r) in OWN_TYPES]
    source_rows = [r for r in hand if _target_type(r) in SOURCE_TYPES]
    marked_backfill = sum(1 for r in rows if "バックフィル" in str(r.get("note") or ""))
    marked_prefix = sum(1 for r in rows if str(r.get("note") or "").startswith(MECHANICAL_PREFIXES))
    hyp_mechanical = sum(1 for r in rows
                         if _target_type(r) == "hypothesis"
                         and str(r.get("note") or "").startswith(MECHANICAL_PREFIXES))
    return {
        "rows": len(rows),
        "handwritten": len(hand),
        "labels": {label: sum(1 for r in hand if r.get("reading") == label) for label in READING_LABELS},
        "by_target_type": table,
        "own": {"rows": len(own_rows), "reinterpreted": round(share(own_rows, "reinterpreted"), 3),
                "interpreted": round(share(own_rows, "interpreted"), 3),
                "contested": round(share(own_rows, "contested"), 3)},
        "source": {"rows": len(source_rows), "reinterpreted": round(share(source_rows, "reinterpreted"), 3),
                   "interpreted": round(share(source_rows, "interpreted"), 3),
                   "contested": round(share(source_rows, "contested"), 3)},
        "by_month": by_month,
        "mechanical": {"marker_backfill": marked_backfill, "prefix_both": marked_prefix,
                       "hypothesis_targeted": hyp_mechanical},
    }


def render_reading(report: dict[str, Any]) -> str:
    out = ["## 読みの語彙——どの対象に、どのラベルが付くか"]
    out.append(f"- 読みの行 {report['rows']} 行、うち手書き {report['handwritten']} 行。")
    labels = report["labels"]
    out.append(f"- 全体: {', '.join(f'{k}={v}' for k, v in labels.items())}")
    out.append("")
    out.append("| 対象 | 行数 | " + " | ".join(l[:10] for l in READING_LABELS) + " |")
    out.append("| :--- | ---: | " + " | ".join("---:" for _ in READING_LABELS) + " |")
    for kind, counts in sorted(report["by_target_type"].items(), key=lambda kv: -sum(kv[1].values())):
        total = sum(counts.values())
        cells = " | ".join(f"{100 * counts.get(l, 0) / total:.1f}%" for l in READING_LABELS)
        out.append(f"| {kind} | {total} | {cells} |")
    own, source = report["own"], report["source"]
    out.append("")
    out.append("### 自分の記録と素材で、読み方は違うか")
    out.append(f"- 自分の記録（断片・ノート・問い）{own['rows']} 行: 再解釈 {own['reinterpreted'] * 100:.1f}%、"
               f"解釈 {own['interpreted'] * 100:.1f}%、異議 {own['contested'] * 100:.1f}%")
    out.append(f"- 素材 {source['rows']} 行: 再解釈 {source['reinterpreted'] * 100:.1f}%、"
               f"解釈 {source['interpreted'] * 100:.1f}%、異議 {source['contested'] * 100:.1f}%")
    out.append("- 月ごとの差（自分の記録 − 素材、再解釈の比率）:")
    for stamp, row in report["by_month"].items():
        out.append(f"  - {stamp}: {row['gap_pp']:+.1f}pp（自分の記録 {row['own_reinterpreted'] * 100:.1f}% / "
                   f"素材 {row['source_reinterpreted'] * 100:.1f}%、n={row['own_rows']}/{row['source_rows']}）")
    mech = report["mechanical"]
    out.append("")
    out.append("### 算術が読むのは語彙ではなく、註の部分文字列")
    out.append(f"- `belief_state.py` は手書き判定に `バックフィル` という部分文字列だけを使う："
               f"この規則が除く行 {mech['marker_backfill']}、接頭辞（機械的…）で除く行 {mech['prefix_both']}"
               f"（差 {abs(mech['marker_backfill'] - mech['prefix_both'])} 行は、註の途中に語がある行）。")
    out.append(f"- 仮説を対象にした機械的行は {mech['hypothesis_targeted']} 行。"
               "したがって証人列の数値は今のところ変わらないが、規則が語彙ではなく註に依存していることは変わらない。")
    out.append("- `read_log.reading` を読む道具は、この台帳に一つもない（この節が初めて数える）。")
    return "\n".join(out)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure label concentration, unbacked labels, and separation novelty.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--question", default=None, help="question id for the least-separated pair list (e.g. Q-003)")
    parser.add_argument("--min-posterior", type=float, default=0.01)
    parser.add_argument("--reading", action="store_true",
                        help="measure the read_log reading vocabulary by target type instead of the "
                             "evaluation vocabulary (report only)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.reading:
        reading = reading_report(root=args.root)
        print(json.dumps(reading, ensure_ascii=False, indent=2, sort_keys=True) if args.json
              else render_reading(reading))
        return 0
    report = build_report(root=args.root, question_id=args.question, min_posterior=args.min_posterior)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
