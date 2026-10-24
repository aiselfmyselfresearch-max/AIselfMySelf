#!/usr/bin/env python3
"""Read the shape of the relation graph. A map, not a verdict.

`state/relations.jsonl` is the only place where the archive says that two
records have something to do with each other. That file has grown to several
hundred lines, and until now nothing read it as a whole: `inspect_inquiry.py`
counts how many materials a fragment names, `voice_audit.py` looks at the
fragments' prose, `validate_seed.py` checks that every endpoint exists. None of
them reports which nodes are connected and which are not.

That gap has already produced one wrong statement. In SESSION-028 the note said
the three new fragments (FRAG-032..034) had been given relations, resolving
their `incoming = 0`; in fact they were measured only inside a range that
happened to exclude their relations, and they were still islands. Measuring
"nothing points here" by hand, over a growing file, is exactly the kind of
measurement that reports its own blind spot as a fact.

This tool reports:

  * how many relations exist, and of which type (no ranking implied)
  * nodes of each kind that appear in no relation at all
  * fragments that point at something but are pointed at by nothing (片道)
  * pairs that are recorded twice, and any self-loop
  * for `echo`, whether the reverse direction is also recorded — it need not be,
    so this is printed as a list to look at, never as an error
  * a second channel: question lineage as recorded in `previous_question_ids`

The last one exists because the first version of this tool read only
`relations.jsonl` and reported that 37 of 51 questions never point anywhere.
That figure was true of the file and false of the archive: a question's descent
is recorded in its own record, not as a relation. Measuring one channel and
reporting it as the whole is the same error this tool was built to prevent.

It does not pass or fail anything, and a low degree is not a fault. A fragment
with no incoming relation may be one nobody has answered yet; that is a state
the archive allows. The point is to see it rather than to guess it.

Usage:
  python3 tools/relation_audit.py
  python3 tools/relation_audit.py --json
  python3 tools/relation_audit.py --kind fragment
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

STATE = ROOT / "state"

FILES = {
    "fragment": ("fragments.jsonl", "fragment_id"),
    "question": ("questions.jsonl", "question_id"),
    "material": ("materials.jsonl", "material_id"),
    "motif": ("motifs.jsonl", "motif_id"),
    "session": ("sessions.jsonl", "session_id"),
}

RELATION_TYPES = (
    "echo",
    "contrast",
    "transforms",
    "metaphorically_resonates",
    "interrupts",
    "responds_to",
    "leaves_open",
    "reframes",
)


def load(path: Path, key: str, *, base_only: bool = False, exclude: str | None = None) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return records
    if base_only:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"error: {path.name}:{lineno}: {exc}", file=sys.stderr)
                raise SystemExit(1)
            records[rec[key]] = rec
        return records
    errors: list[str] = []
    merged = ledger_io.load_jsonl_union(path, key, errors, root=ROOT, exclude=exclude)
    if errors:
        print("error: " + "; ".join(errors), file=sys.stderr)
        raise SystemExit(1)
    return merged


def audit(*, base_only: bool = False, exclude: str | None = None) -> dict[str, Any]:
    nodes: dict[str, dict[str, dict[str, Any]]] = {}
    for kind, (filename, key) in FILES.items():
        nodes[kind] = load(STATE / filename, key, base_only=base_only, exclude=exclude)

    relations = load(STATE / "relations.jsonl", "relation_id", base_only=base_only, exclude=exclude)

    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    type_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str, str]] = Counter()
    unresolved: list[dict[str, str]] = []
    self_loops: list[str] = []

    for rel in relations.values():
        left = rel.get("left", {})
        right = rel.get("right", {})
        lid, rid = left.get("id", ""), right.get("id", "")
        rtype = rel.get("relation_type", "")
        type_counts[rtype] += 1
        outgoing[lid].append(rel)
        incoming[rid].append(rel)
        pair_counts[(lid, rid, rtype)] += 1
        if lid == rid:
            self_loops.append(rel["relation_id"])
        for side in (left, right):
            kind, nid = side.get("type", ""), side.get("id", "")
            if kind in nodes and nid not in nodes[kind]:
                unresolved.append({"relation_id": rel["relation_id"], "side": kind, "id": nid})

    duplicates = [
        {"left": lid, "right": rid, "type": rtype, "count": count}
        for (lid, rid, rtype), count in pair_counts.items()
        if count > 1
    ]

    kinds_report: dict[str, dict[str, Any]] = {}
    for kind, records in nodes.items():
        isolated = [nid for nid in records if not outgoing.get(nid) and not incoming.get(nid)]
        one_way = [
            nid
            for nid in records
            if outgoing.get(nid) and not incoming.get(nid) and kind == "fragment"
        ]
        no_outgoing = [nid for nid in records if not outgoing.get(nid)]
        kinds_report[kind] = {
            "count": len(records),
            "isolated": isolated,
            "one_way_fragments": one_way,
            "no_outgoing_from_here": no_outgoing,
            "incoming_total": sum(len(incoming.get(nid, [])) for nid in records),
            "outgoing_total": sum(len(outgoing.get(nid, [])) for nid in records),
        }

    echo_pairs = sorted(
        (rel["left"].get("id", ""), rel["right"].get("id", ""))
        for rel in relations.values()
        if rel.get("relation_type") == "echo"
    )
    echo_set = set(echo_pairs)
    one_direction_echo = [p for p in echo_pairs if (p[1], p[0]) not in echo_set]

    degree = []
    for kind, records in nodes.items():
        for nid in records:
            degree.append(
                {
                    "id": nid,
                    "kind": kind,
                    "in": len(incoming.get(nid, [])),
                    "out": len(outgoing.get(nid, [])),
                }
            )
    degree.sort(key=lambda row: (-(row["in"] + row["out"]), row["id"]))

    questions = nodes["question"]
    children: dict[str, list[str]] = defaultdict(list)
    for qid, q in questions.items():
        for parent in q.get("previous_question_ids") or []:
            children[parent].append(qid)
    lineage = {
        "questions": len(questions),
        "with_previous": sum(1 for q in questions.values() if q.get("previous_question_ids")),
        "parents_named": len([p for p in children if p in questions]),
        "childless": [qid for qid in questions if not children.get(qid)],
        "orphan_parents": [p for p in children if p not in questions],
    }

    return {
        "relation_total": len(relations),
        "question_lineage": lineage,
        "by_type": {t: type_counts.get(t, 0) for t in RELATION_TYPES},
        "unused_types": [t for t in RELATION_TYPES if not type_counts.get(t)],
        "by_kind": kinds_report,
        "duplicate_pairs": duplicates,
        "self_loops": self_loops,
        "unresolved_endpoints": unresolved,
        "one_direction_echo": one_direction_echo,
        "top_degree": degree[:15],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="emit the audit as JSON")
    parser.add_argument("--kind", choices=sorted(FILES), help="show only one kind in the degree table")
    parser.add_argument("--base-only", action="store_true", help="read frozen state/*.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()

    report = audit(base_only=args.base_only, exclude=args.exclude_shard)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print("=== 関係の地勢 — state/relations.jsonl を一つの網として読む（採点ではありません） ===")
    print(f"関係 {report['relation_total']} 件")
    print()
    print("--- 1. 型ごとの件数 ---")
    for t in RELATION_TYPES:
        print(f"  {t:<24s} {report['by_type'][t]:3d}")
    if report["unused_types"]:
        print(f"  未使用の型: {', '.join(report['unused_types'])}")
    print()

    print("--- 2. 網に一度も出てこないもの（孤立） ---")
    for kind, row in report["by_kind"].items():
        isolated = row["isolated"]
        label = f"{kind}（{row['count']} 件中 {len(isolated)}）"
        print(f"  {label:<32s} {', '.join(isolated) if isolated else 'なし'}")
    print()

    print("--- 3. 断片の片道（こちらからは指すが、誰も指していない） ---")
    row = report["by_kind"]["fragment"]
    print(f"  {len(row['one_way_fragments'])}/{row['count']} 編  {', '.join(row['one_way_fragments']) or 'なし'}")
    print()
    print("--- 4. どこからも出ていないもの（この記録が何も指していない） ---")
    for kind, row in report["by_kind"].items():
        ids = row["no_outgoing_from_here"]
        if not ids:
            continue
        shown = ", ".join(ids[:12])
        more = f" …ほか {len(ids) - 12} 件" if len(ids) > 12 else ""
        print(f"  {kind:<10s} {len(ids):3d}/{row['count']} 件  {shown}{more}")
    print()

    print("--- 5. 同じ組が二度以上 ---")
    if report["duplicate_pairs"]:
        for d in report["duplicate_pairs"]:
            print(f"  {d['left']} → {d['right']} [{d['type']}] ×{d['count']}")
    else:
        print("  なし")
    if report["self_loops"]:
        print(f"  自分自身への関係: {', '.join(report['self_loops'])}")
    print()

    print("--- 6. echo の片方向（逆向きは書かれていない組） ---")
    print(f"  {len(report['one_direction_echo'])} 組 / echo 全 {report['by_type']['echo']} 件")
    print("  echo は逆向きが無くても誤りではない。目で見るための一覧。")
    print()

    if report["unresolved_endpoints"]:
        print("--- 7. 存在しない ID を指している関係 ---")
        for u in report["unresolved_endpoints"]:
            print(f"  {u['relation_id']}: {u['side']} {u['id']}")
        print()

    ln = report["question_lineage"]
    print("--- 8. もう一つの経路: previous_question_ids による問いの系譜 ---")
    print(f"  previous_question_ids を持つ問い {ln['with_previous']}/{ln['questions']} 件")
    print(f"  親として名前を挙がっている問い {ln['parents_named']} 件")
    print(f"  どの問いからも子を持たない問い {len(ln['childless'])} 件  {', '.join(ln['childless']) or 'なし'}")
    if ln["orphan_parents"]:
        print(f"  存在しない親を指している: {', '.join(ln['orphan_parents'])}")
    print("  問いの関係は relations.jsonl ではなく、問い自身の欄に書かれている。")
    print("  片方のファイルだけを読んで「問いは関係を持たない」と結論すると、測った範囲の外を無いことにする。")
    print()

    print("--- 9. 次数の多い順（in / out） ---")
    rows = report["top_degree"]
    if args.kind:
        rows = [r for r in rows if r["kind"] == args.kind] or [
            r for r in report["top_degree"] if r["kind"] == args.kind
        ]
    for r in rows:
        print(f"  {r['id']:<24s} {r['kind']:<9s} in={r['in']:2d} out={r['out']:2d}")
    print()

    print("--- 読み方 ---")
    print("  孤立は欠陥ではない。まだ誰も応えていない断片、まだ断片に使われていない素材も、")
    print("  この台帳では許されている状態である。見えていないことだけが問題なので、ここに出す。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
