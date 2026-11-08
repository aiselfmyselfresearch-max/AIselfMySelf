#!/usr/bin/env python3
"""Observe how gathered materials, motifs, questions, and deferred seeds are digested into fragments.

A mirror, not a quota.

Many sessions in this archive deliberately refrained from writing fragments in
the same turn that gathered 40+ materials, so as not to imitate freshly read
summaries or fabricate bodily sensations (`CONTENT_POLICY.md`). Several of
those sessions left explicit "next seeds" (`次回の種`) in `readings/*.md` for a
later reader to pick up.

Until now, no single mirror read that cycle across the ledger and `readings/`:
how many materials have been gathered versus taken up into fragments, which
motifs still have zero fragments (`fragment.motif_ids` directly, or via
`state/relations.jsonl`), which shards left isolated questions or materials
outside the relation graph, which fragments remain one-way (`incoming = 0` or
`outgoing = 0`), and which reading reports recorded deferred fragment seeds.

Low fragment counts or unredeemed seeds are not errors; `exit 0` always (unless
ledger JSON itself fails to parse). The point is to make accumulation,
restraint, isolation, and uptake visible in one place.

Usage:
  python3 tools/metabolism_audit.py
  python3 tools/metabolism_audit.py --json
  python3 tools/metabolism_audit.py --base-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

DEFERRED_HEADING_RE = re.compile(
    r"^#{2,4}\s+.*(?:断片を書かなかった|断片を見送った|次回の種|断片の種|書かなかった理由|次セッションへの手渡し|次回に返す負債).*$",
    re.MULTILINE,
)
SEED_ITEM_RE = re.compile(
    r"(?:種[A-C1-3１-３①-③]|^\s*[1-3]\.\s*\*\*「[^」]+」\*\*|①\*\*「[^」]+」\*\*)",
    re.MULTILINE,
)


def _load_records(
    state_dir: Path, filename: str, id_field: str, *, base_only: bool, root: Path
) -> dict[str, dict[str, Any]]:
    base_path = state_dir / filename
    if base_only:
        out: dict[str, dict[str, Any]] = {}
        if not base_path.exists():
            return out
        for line in base_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s:
                continue
            rec = json.loads(s)
            out[rec[id_field]] = rec
        return out
    errors: list[str] = []
    data = ledger_io.load_jsonl_union(base_path, id_field, errors, root=root)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def _material_shard_sources(state_dir: Path, *, base_only: bool) -> dict[str, str]:
    sources: dict[str, str] = {}
    base_path = state_dir / "materials.jsonl"
    if base_path.exists():
        for line in base_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s:
                rec = json.loads(s)
                sources[rec["material_id"]] = "materials.jsonl"
    if not base_only:
        shard_dir = state_dir / "materials.d"
        if shard_dir.is_dir():
            for shard in sorted(shard_dir.glob("*.jsonl")):
                for line in shard.read_text(encoding="utf-8").splitlines():
                    s = line.strip()
                    if s:
                        rec = json.loads(s)
                        sources[rec["material_id"]] = shard.name
    return sources


def _session_shard_records(state_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    shard_dir = state_dir / "sessions.d"
    if not shard_dir.is_dir():
        return out
    for shard in sorted(shard_dir.glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s:
                out.append((shard.name, json.loads(s)))
    return out


def analyze(root: Path = ROOT, *, base_only: bool = False) -> dict[str, Any]:
    state_dir = root / "state"
    materials = _load_records(state_dir, "materials.jsonl", "material_id", base_only=base_only, root=root)
    motifs = _load_records(state_dir, "motifs.jsonl", "motif_id", base_only=base_only, root=root)
    questions = _load_records(state_dir, "questions.jsonl", "question_id", base_only=base_only, root=root)
    fragments = _load_records(state_dir, "fragments.jsonl", "fragment_id", base_only=base_only, root=root)
    relations = _load_records(state_dir, "relations.jsonl", "relation_id", base_only=base_only, root=root)
    sessions = _load_records(state_dir, "sessions.jsonl", "session_id", base_only=base_only, root=root)

    # 1. Sessions: fragment-producing vs zero-fragment
    with_frags = [
        sid for sid, s in sessions.items() if len(s.get("produced_fragment_ids", [])) > 0
    ]
    without_frags = [
        sid for sid, s in sessions.items() if len(s.get("produced_fragment_ids", [])) == 0
    ]

    shard_sessions: list[dict[str, Any]] = []
    trailing_zero_frag_shards = 0
    if not base_only:
        raw_shards = _session_shard_records(state_dir)
        for shard_name, srec in raw_shards:
            frags_out = srec.get("produced_fragment_ids", [])
            shard_sessions.append(
                {
                    "shard": shard_name,
                    "session_id": srec["session_id"],
                    "produced_fragments": len(frags_out),
                    "opened_questions": len(srec.get("opened_question_ids", [])),
                }
            )
        for item in reversed(shard_sessions):
            if item["produced_fragments"] == 0:
                trailing_zero_frag_shards += 1
            else:
                break

    def _origin_label(rec: dict[str, Any]) -> str:
        orig = rec.get("origin", "")
        if isinstance(orig, dict):
            return str(orig.get("kind", ""))
        return str(orig)

    # 2. Material uptake across channels
    frag_mat_ids: set[str] = set()
    for f in fragments.values():
        frag_mat_ids.update(mid for mid in f.get("material_ids", []) if mid in materials)

    q_mat_ids: set[str] = set()
    for q in questions.values():
        q_mat_ids.update(mid for mid in q.get("material_ids", []) if mid in materials)

    rel_nodes: set[str] = set()
    frag_incoming: Counter[str] = Counter()
    frag_outgoing: Counter[str] = Counter()
    rel_motif_to_frag: dict[str, set[str]] = {m: set() for m in motifs}

    for r in relations.values():
        left = r["left"]
        right = r["right"]
        rel_nodes.add(left["id"])
        rel_nodes.add(right["id"])
        if left["type"] == "fragment" and left["id"] in fragments:
            frag_outgoing[left["id"]] += 1
        if right["type"] == "fragment" and right["id"] in fragments:
            frag_incoming[right["id"]] += 1
        if left["type"] == "fragment" and right["type"] == "motif" and right["id"] in rel_motif_to_frag:
            rel_motif_to_frag[right["id"]].add(left["id"])
        if right["type"] == "fragment" and left["type"] == "motif" and left["id"] in rel_motif_to_frag:
            rel_motif_to_frag[left["id"]].add(right["id"])

    untouched_by_frag_or_q = sorted(
        mid for mid in materials if mid not in frag_mat_ids and mid not in q_mat_ids
    )
    isolated_materials = sorted(mid for mid in materials if mid not in rel_nodes)
    mat_sources = _material_shard_sources(state_dir, base_only=base_only)
    isolated_materials_by_shard = dict(
        sorted(Counter(mat_sources.get(mid, "unknown") for mid in isolated_materials).items())
    )

    # 3. Motif-to-fragment coverage
    direct_motif_to_frag: dict[str, set[str]] = {m: set() for m in motifs}
    for fid, f in fragments.items():
        for mid in f.get("motif_ids", []):
            if mid in direct_motif_to_frag:
                direct_motif_to_frag[mid].add(fid)

    zero_direct_motifs = [
        {"motif_id": mid, "label": motifs[mid]["label"]}
        for mid in motifs
        if len(direct_motif_to_frag[mid]) == 0
    ]
    zero_any_motifs = [
        {"motif_id": mid, "label": motifs[mid]["label"]}
        for mid in motifs
        if len(direct_motif_to_frag[mid] | rel_motif_to_frag[mid]) == 0
    ]

    # 4. Isolated questions & one-way fragments
    isolated_questions = [
        {
            "question_id": qid,
            "origin": _origin_label(questions[qid]),
            "question": questions[qid].get("question", ""),
        }
        for qid in sorted(questions)
        if qid not in rel_nodes
    ]
    one_way_incoming_zero = [
        {
            "fragment_id": fid,
            "status": fragments[fid]["status"],
            "form": fragments[fid]["form"],
            "title": fragments[fid]["title"],
        }
        for fid in sorted(fragments)
        if frag_incoming[fid] == 0
    ]
    outgoing_zero_fragments = [
        {
            "fragment_id": fid,
            "status": fragments[fid]["status"],
            "form": fragments[fid]["form"],
            "title": fragments[fid]["title"],
        }
        for fid in sorted(fragments)
        if frag_outgoing[fid] == 0
    ]

    # 5. Readings mentioning deferred seeds / refraining from fragments
    readings_dir = root / "readings"
    deferred_reports: list[dict[str, Any]] = []
    total_readings = 0
    if readings_dir.is_dir():
        for md in sorted(readings_dir.glob("*.md")):
            total_readings += 1
            txt = md.read_text(encoding="utf-8")
            headings = [h.strip() for h in DEFERRED_HEADING_RE.findall(txt)]
            if headings:
                seed_markers = len(SEED_ITEM_RE.findall(txt))
                deferred_reports.append(
                    {
                        "file": md.name,
                        "headings": headings,
                        "seed_marker_hits": seed_markers,
                    }
                )

    total_mats = len(materials)
    frag_uptake_ratio = round(len(frag_mat_ids) / total_mats, 4) if total_mats else 0.0

    return {
        "scope": "base_only" if base_only else "union",
        "counts": {
            "materials": total_mats,
            "motifs": len(motifs),
            "questions": len(questions),
            "fragments": len(fragments),
            "relations": len(relations),
            "sessions": len(sessions),
            "readings": total_readings,
        },
        "sessions_summary": {
            "with_fragments": len(with_frags),
            "without_fragments": len(without_frags),
            "shard_sessions_total": len(shard_sessions),
            "shard_sessions_without_fragments": sum(
                1 for x in shard_sessions if x["produced_fragments"] == 0
            ),
            "trailing_zero_fragment_shards": trailing_zero_frag_shards,
        },
        "material_digestion": {
            "referenced_by_fragments": len(frag_mat_ids),
            "fragment_uptake_ratio": frag_uptake_ratio,
            "referenced_by_questions": len(q_mat_ids),
            "untouched_by_fragment_or_question": len(untouched_by_frag_or_q),
            "isolated_in_relations": len(isolated_materials),
            "isolated_in_relations_by_shard": isolated_materials_by_shard,
        },
        "motif_coverage": {
            "with_direct_fragments": len(motifs) - len(zero_direct_motifs),
            "zero_direct_fragments_count": len(zero_direct_motifs),
            "zero_direct_fragments": zero_direct_motifs,
            "zero_any_fragment_link_count": len(zero_any_motifs),
            "zero_any_fragment_link": zero_any_motifs,
        },
        "graph_reciprocity": {
            "isolated_questions_count": len(isolated_questions),
            "isolated_questions": isolated_questions,
            "fragments_incoming_zero_count": len(one_way_incoming_zero),
            "fragments_incoming_zero": one_way_incoming_zero,
            "fragments_outgoing_zero_count": len(outgoing_zero_fragments),
            "fragments_outgoing_zero": outgoing_zero_fragments,
        },
        "deferred_seeds_in_readings": {
            "reports_with_deferred_section": len(deferred_reports),
            "reports": deferred_reports,
        },
    }


def format_report(data: dict[str, Any]) -> str:
    c = data["counts"]
    ss = data["sessions_summary"]
    md = data["material_digestion"]
    mc = data["motif_coverage"]
    gr = data["graph_reciprocity"]
    ds = data["deferred_seeds_in_readings"]

    lines = [
        f"=== Metabolism Audit ({data['scope']}) ===",
        (
            f"Ledger: materials={c['materials']}, motifs={c['motifs']}, "
            f"questions={c['questions']}, fragments={c['fragments']}, "
            f"relations={c['relations']}, sessions={c['sessions']}, readings={c['readings']}"
        ),
        "",
        "[1] Session Production & Restraint",
        f"  Sessions producing fragments : {ss['with_fragments']} / {c['sessions']}",
        f"  Sessions with 0 fragments    : {ss['without_fragments']} / {c['sessions']}",
    ]
    if data["scope"] == "union":
        lines.append(
            f"  Shard sessions (0 fragments) : {ss['shard_sessions_without_fragments']} / {ss['shard_sessions_total']} "
            f"(trailing streak = {ss['trailing_zero_fragment_shards']})"
        )
    lines.extend(
        [
            f"  Readings with deferred seeds : {ds['reports_with_deferred_section']} / {c['readings']}",
            "",
            "[2] Material Digestion",
            f"  Taken up in fragments        : {md['referenced_by_fragments']} / {c['materials']} ({md['fragment_uptake_ratio']*100:.1f}%)",
            f"  Referenced in questions      : {md['referenced_by_questions']} / {c['materials']}",
            f"  Untouched by frag or question: {md['untouched_by_fragment_or_question']} / {c['materials']}",
            f"  Isolated in relations graph  : {md['isolated_in_relations']} / {c['materials']} {md['isolated_in_relations_by_shard']}",
            "",
            "[3] Motif-to-Fragment Coverage",
            f"  Motifs with >=1 direct frag  : {mc['with_direct_fragments']} / {c['motifs']}",
            f"  Motifs with 0 direct frags   : {mc['zero_direct_fragments_count']} / {c['motifs']}",
        ]
    )
    for item in mc["zero_direct_fragments"]:
        lines.append(f"    - {item['motif_id']}: {item['label']}")
    lines.extend(
        [
            f"  Motifs with 0 frag (any rel) : {mc['zero_any_fragment_link_count']} / {c['motifs']}",
            "",
            "[4] Graph Reciprocity & Islands",
            f"  Isolated questions (0 rels)  : {gr['isolated_questions_count']}",
        ]
    )
    for q in gr["isolated_questions"]:
        lines.append(f"    - {q['question_id']} ({q['origin']}): {q['question'][:68]}")
    lines.append(f"  Fragments with incoming = 0  : {gr['fragments_incoming_zero_count']}")
    for f in gr["fragments_incoming_zero"]:
        lines.append(f"    - {f['fragment_id']} [{f['status']}/{f['form']}]: {f['title']}")
    lines.append(f"  Fragments with outgoing = 0  : {gr['fragments_outgoing_zero_count']}")
    for f in gr["fragments_outgoing_zero"]:
        lines.append(f"    - {f['fragment_id']} [{f['status']}/{f['form']}]: {f['title']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    parser.add_argument(
        "--base-only",
        action="store_true",
        help="Read only frozen base state/*.jsonl without state/*.d/ shards",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root directory (defaults to repo root)",
    )
    args = parser.parse_args(argv)
    data = analyze(root=args.root.resolve(), base_only=args.base_only)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
