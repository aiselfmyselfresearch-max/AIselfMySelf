#!/usr/bin/env python3
"""Measure search failure on the archive's own retrieval surface (stdlib only, writes nothing).

Why this tool exists
--------------------
The 2026-11-27 analysis (`readings/2026-11-27-retrieval-failure-probes-and-adoption.md`)
applied AI-agent retrieval-failure research (stage attribution, query-retriever
mismatch, position effects, abstention) to this archive.  The archive's only
interactive material search is the viewer's substring filter
(`viewer/app.js` `renderMaterials`): no ranking, no zero-hit record, no log of
failed searches anywhere.  The report's improvement candidates P1/P4/P6 need a
reproducible instrument for that surface, so the failure stages become
measurable instead of invisible:

- **Stage B (query wording)** -- `--run` replays a hand-authored probe set
  (`docs/search-probe-set.json`): per material, three wordings for the same
  information need.  `ledger` reuses words from the row itself;
  `paraphrase` expresses the same need with words the row does not use;
  `hypernym` uses a broader category term the row does not use.  Reach and
  zero-hits per wording quantify the wording dependence.
- **Stage C analog (top-K cut / position)** -- the viewer shows the first 80
  hits (`matPageLimit`), so a reached target may still be off-page.  `--run`
  records the target's rank in the filtered list and first-page membership.
- **Stage A (not collected)** -- `--coverage-gaps` lists open questions that no
  fragment connects to any material.  No search tuning can reach a row that
  does not exist; only acquisition fills these.

The tool reproduces the viewer's haystack exactly (id, title, authors joined
by spaces, passage, literary_invitation; lowercased substring match) so the
numbers describe the deployed surface, not a better one.  It writes nothing:
every run is recomputable from the ledger at a fixed commit, which is what an
`evaluations` row with `evidence_type: "reproducible_script"` needs.

Usage:
  python3 tools/probe_search.py --run docs/search-probe-set.json
  python3 tools/probe_search.py --run docs/search-probe-set.json --json
  python3 tools/probe_search.py --coverage-gaps [--json]
  python3 tools/probe_search.py --self-test

Exit status: 0 unless a probe is invalid (a `ledger` wording that does not
reach its target, or a `paraphrase`/`hypernym` wording that occurs in its
target's own haystack -- both would make the probe measure nothing), or the
probe file is malformed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_io  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

#: The viewer paginates filtered results at this size (viewer/app.js matPageLimit),
#: so a hit beyond this rank is not on the first page the reader sees.
VIEWER_PAGE_LIMIT = 80

PROBE_KINDS = ("ledger", "paraphrase", "hypernym")


def load_materials(root: Path) -> list[dict[str, Any]]:
    """Material rows in collection order (frozen base, then shards by name)."""
    base = root / "state" / "materials.jsonl"
    errors: list[str] = []
    data = ledger_io.load_jsonl_union(base, "material_id", errors, root=root)
    if errors:
        raise SystemExit("materials ledger could not be read: " + "; ".join(errors[:3]))
    # dict preserves insertion order: frozen base first, then shards by name
    return list(data.values())


def viewer_haystack(row: dict[str, Any]) -> str:
    """The exact search haystack of viewer/app.js renderMaterials."""
    source = row.get("source") if isinstance(row.get("source"), dict) else {}
    authors = source.get("authors")
    authors_str = " ".join(authors) if isinstance(authors, list) else ""
    parts = [
        row.get("material_id") or "",
        row.get("title") or "",
        authors_str,
        row.get("passage") or "",
        row.get("literary_invitation") or "",
    ]
    return " ".join(str(p) for p in parts).lower()


def search(rows: list[dict[str, Any]], query: str) -> list[str]:
    """Substring filter in collection order -- what the viewer returns."""
    q = query.strip().lower()
    if not q:
        return []
    return [
        row["material_id"]
        for row in rows
        if q in viewer_haystack(row)
    ]


def load_probes(path: Path) -> list[dict[str, Any]]:
    """Read and shape-check the probe set; raise on structural problems."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"cannot read probe set {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"probe set {path} is not valid JSON: {exc}") from exc
    probes = doc.get("probes") if isinstance(doc, dict) else doc
    if not isinstance(probes, list) or not probes:
        raise SystemExit(f"probe set {path} must contain a non-empty 'probes' list")
    for i, probe in enumerate(probes):
        if not isinstance(probe, dict):
            raise SystemExit(f"probe #{i} is not an object")
        for key in ("target_id", "kind", "query"):
            if not isinstance(probe.get(key), str) or not probe[key].strip():
                raise SystemExit(f"probe #{i} is missing a non-empty '{key}'")
        if probe["kind"] not in PROBE_KINDS:
            raise SystemExit(
                f"probe #{i} kind {probe['kind']!r} is not one of {PROBE_KINDS}"
            )
    return probes


def run_probes(
    rows: list[dict[str, Any]], probes: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    """Replay every probe; return (per_probe, per_kind_summary, problems)."""
    problems: list[str] = []
    per_probe: list[dict[str, Any]] = []
    id_to_row = {row["material_id"]: row for row in rows}
    for probe in probes:
        target = probe["target_id"]
        kind = probe["kind"]
        query = probe["query"]
        if target not in id_to_row:
            problems.append(f"{target}: target material not in ledger ({kind}: {query!r})")
            continue
        hits = search(rows, query)
        rank = hits.index(target) + 1 if target in hits else None
        item: dict[str, Any] = {
            "target_id": target,
            "kind": kind,
            "query": query,
            "hits": len(hits),
            "reach": rank is not None,
            "rank": rank,
            "first_page": rank is not None and rank <= VIEWER_PAGE_LIMIT,
            "zero": len(hits) == 0,
        }
        target_hay = viewer_haystack(id_to_row[target])
        if kind == "ledger" and rank is None:
            problems.append(f"{target}: ledger wording {query!r} does not reach its own row")
        if kind in ("paraphrase", "hypernym") and query.strip().lower() in target_hay:
            problems.append(
                f"{target}: {kind} wording {query!r} occurs in the target's own haystack, "
                "so it measures nothing"
            )
        per_probe.append(item)
    summary: dict[str, Any] = {}
    for kind in PROBE_KINDS:
        items = [p for p in per_probe if p["kind"] == kind]
        if not items:
            continue
        n = len(items)
        reached = sum(1 for p in items if p["reach"])
        ranks = sorted(p["rank"] for p in items if p["rank"] is not None)
        summary[kind] = {
            "probes": n,
            "reach": reached,
            "reach_rate": round(reached / n, 4),
            "zero": sum(1 for p in items if p["zero"]),
            "first_page": sum(1 for p in items if p["first_page"]),
            "first_page_rate": round(sum(1 for p in items if p["first_page"]) / n, 4),
            "max_rank": max(ranks) if ranks else None,
            "median_rank": (
                ranks[len(ranks) // 2] if ranks and len(ranks) % 2 == 1
                else (ranks[len(ranks) // 2 - 1] + ranks[len(ranks) // 2]) / 2 if ranks
                else None
            ),
            "mean_hits": round(sum(p["hits"] for p in items) / n, 1),
        }
    return per_probe, summary, problems


def coverage_gaps(root: Path) -> dict[str, Any]:
    """Open questions no fragment connects to any material (failure stage A)."""
    def _union(collection: str, id_key: str) -> list[dict[str, Any]]:
        base = root / "state" / f"{collection}.jsonl"
        errors: list[str] = []
        data = ledger_io.load_jsonl_union(base, id_key, errors, root=root)
        if errors:
            raise SystemExit(f"{collection} ledger could not be read: " + "; ".join(errors[:3]))
        return list(data.values())

    questions = _union("questions", "question_id")
    fragments = _union("fragments", "fragment_id")
    connected: dict[str, set[str]] = {}
    for frag in fragments:
        for qid in frag.get("question_ids") or []:
            if isinstance(qid, str):
                connected.setdefault(qid, set()).update(
                    mid for mid in (frag.get("material_ids") or []) if isinstance(mid, str)
                )
    open_ids = [
        q["question_id"] for q in questions if q.get("status", "open") == "open"
    ]
    gaps = sorted(qid for qid in open_ids if not connected.get(qid))
    return {
        "open_questions": len(open_ids),
        "coverage_gaps": len(gaps),
        "gap_rate": round(len(gaps) / len(open_ids), 4) if open_ids else None,
        "question_ids": gaps,
    }


def _self_test() -> int:
    """Offline checks with fixture rows: no ledger is read."""
    rows = [
        {
            "material_id": "MAT-A",
            "title": "Keep の記憶と忘却",
            "source": {"authors": ["Alpha", "Beta"]},
            "passage": "保持とは痕跡の維持である。",
            "literary_invitation": "",
        },
        {
            "material_id": "MAT-B",
            "title": "Forgetting curves",
            "source": {"authors": ["Gamma"]},
            "passage": "忘却曲線は減衰を描く。",
            "literary_invitation": "なぜ薄れるのか。",
        },
        {
            "material_id": "MAT-C",
            "title": "保持の練習",
            "source": {},
            "passage": "検索練習は保持を高める。",
            "literary_invitation": "",
        },
    ]
    failures: list[str] = []

    def check(name: str, got: Any, want: Any) -> None:
        if got != want:
            failures.append(f"{name}: got {got!r}, want {want!r}")

    check("haystack joins authors", "alpha beta" in viewer_haystack(rows[0]), True)
    check("haystack lowercase", "forgetting curves" in viewer_haystack(rows[1]), True)
    check("hit order is collection order",
          search(rows, "保持"), ["MAT-A", "MAT-C"])
    check("empty query matches nothing", search(rows, "  "), [])
    check("no match returns empty", search(rows, "存在しない語"), [])

    probes = [
        {"target_id": "MAT-A", "kind": "ledger", "query": "記憶と忘却"},
        {"target_id": "MAT-B", "kind": "paraphrase", "query": "消える"},
        {"target_id": "MAT-C", "kind": "hypernym", "query": "学習方略"},
        {"target_id": "MAT-Z", "kind": "ledger", "query": "不存在"},
        {"target_id": "MAT-A", "kind": "paraphrase", "query": "保持"},
        {"target_id": "MAT-B", "kind": "ledger", "query": "Forgetting"},
    ]
    per_probe, summary, problems = run_probes(rows, probes)
    check("processed probe count (MAT-Z skipped)", len(per_probe), 5)
    check("ledger reach", summary["ledger"]["reach"], 2)
    check("ledger zero", summary["ledger"]["zero"], 0)
    check("paraphrase reach (only 保持 reaches MAT-A)", summary["paraphrase"]["reach"], 1)
    check("paraphrase zero (消える misses MAT-B)", summary["paraphrase"]["zero"], 1)
    check("hypernym zero-hit is counted as no-reach", summary["hypernym"]["reach"], 0)
    check("missing target flagged", any("MAT-Z" in p for p in problems), True)
    check("in-hay paraphrase flagged", any("MAT-A" in p for p in problems), True)
    check("first_page at rank<=80", per_probe[-1]["first_page"], True)

    # coverage_gaps on a synthetic tree
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        state = root / "state"
        state.mkdir()
        (state / "questions.jsonl").write_text(
            "\n".join([
                json.dumps({"question_id": "Q-1", "status": "open"}, ensure_ascii=False),
                json.dumps({"question_id": "Q-2"}, ensure_ascii=False),
                json.dumps({"question_id": "Q-3", "status": "closed"}, ensure_ascii=False),
            ]) + "\n",
            encoding="utf-8",
        )
        (state / "fragments.jsonl").write_text(
            json.dumps(
                {"fragment_id": "FRAG-1", "question_ids": ["Q-1"],
                 "material_ids": ["MAT-A"]},
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )
        gaps = coverage_gaps(root)
        check("open questions", gaps["open_questions"], 2)
        check("gaps", gaps["coverage_gaps"], 1)
        check("gap ids", gaps["question_ids"], ["Q-2"])
    if failures:
        for line in failures:
            print(f"FAIL: {line}")
        return 1
    print("PASS: probe_search self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", metavar="PROBES_JSON", help="replay a probe set")
    parser.add_argument("--coverage-gaps", action="store_true",
                        help="list open questions no fragment connects to a material")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--self-test", action="store_true",
                        help="run the offline checks and exit")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (for tests)")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()
    if args.run:
        rows = load_materials(args.root)
        probes = load_probes(Path(args.run))
        per_probe, summary, problems = run_probes(rows, probes)
        if args.json:
            print(json.dumps(
                {"probes": per_probe, "summary": summary, "problems": problems},
                ensure_ascii=False, indent=1,
            ))
        else:
            for kind, stats in summary.items():
                print(f"[{kind}] probes={stats['probes']} reach={stats['reach']} "
                      f"({stats['reach_rate']:.1%}) zero={stats['zero']} "
                      f"first_page={stats['first_page']} ({stats['first_page_rate']:.1%}) "
                      f"median_rank={stats['median_rank']} max_rank={stats['max_rank']} "
                      f"mean_hits={stats['mean_hits']}")
            for p in problems:
                print(f"INVALID: {p}")
        return 1 if problems else 0
    if args.coverage_gaps:
        gaps = coverage_gaps(args.root)
        if args.json:
            print(json.dumps(gaps, ensure_ascii=False, indent=1))
        else:
            print(f"open questions: {gaps['open_questions']}, "
                  f"coverage gaps: {gaps['coverage_gaps']} ({gaps['gap_rate']:.1%})")
            for qid in gaps["question_ids"]:
                print(f"  {qid}")
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
