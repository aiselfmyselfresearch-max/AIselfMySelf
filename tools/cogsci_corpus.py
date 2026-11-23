#!/usr/bin/env python3
"""Measure the cognitive-science report corpus as a corpus (read-only).

Why this tool exists.  Between 2026-11-18 and 2026-11-23 the archive produced
dozens of reports that each read a batch of cognitive-science sources and each
answered the two central questions.  Every one of those reports measured the
*sources*.  None measured the *series*: how its form converged, whether its
materials were ever encountered twice, whether the later reports read the
earlier reports, and in what grammatical shape the human appeared across them.
Those are facts about the archive's own memory, so they are checkable here.

The unit is a report file, not a ledger row.  ``readings/*.md``, ``docs/*.md``
and the top-level ``COGNITIVE_SCIENCE_REPORT_*.md`` are scanned; a file joins the
corpus when its H1 title names 認知科学 or its filename carries
``cognitive-science`` / ``cogsci``.  The rule is lexical on purpose: it can be
re-run by anyone and it does not depend on a curated list that would drift.

Self-exclusion is explicit (``SELF_REPORTS``).  The report this tool was built
for is itself a cognitive-science report; counting it would let the report
change the numbers it reports.  Both of its files are listed below, so the
figures in it stay stable after it is committed.

Determinism: reads file contents and names only.  No mtime, no git, no today's
date.  The numbers are reproducible at a fixed commit; the report says which.

Usage:
  python3 tools/cogsci_corpus.py                 # every section
  python3 tools/cogsci_corpus.py --section form
  python3 tools/cogsci_corpus.py --section reuse
  python3 tools/cogsci_corpus.py --section depth
  python3 tools/cogsci_corpus.py --section chain
  python3 tools/cogsci_corpus.py --section shape
  python3 tools/cogsci_corpus.py --json

This tool only counts.  It does not decide whether the form is good, whether the
reports are original, or whether the human they describe exists.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state"

# The report that this instrument was written for, and its reading record.
# Counting them would make the report's own numbers depend on the report.
SELF_REPORTS = frozenset(
    {
        "COGNITIVE_SCIENCE_REPORT_2026-11-23-H.md",
        "2026-11-23-the-cognitive-science-reports-as-a-corpus.md",
    }
)

_H1 = re.compile(r"^#\s+(.*)$", re.M)
_H2 = re.compile(r"^##\s+(.*)$", re.M)
_SESSION = re.compile(r"SESSION-(\d{8})")
_FILE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_MAT_ID = re.compile(r"\bMAT-\d{8}-[0-9A-Za-z]+")
_MAT_DATE = re.compile(r"\bMAT-(\d{8})-")
_HYP = re.compile(r"\bHYP-\d{8}-[0-9a-f]{6}")
_MD_LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
_SENTENCE = re.compile(r"(?<=[。．！？])")
_NEGATION = re.compile(r"(ない|できな|測っていな|言えな|未検定|外挿しな|不明|保留)")

# The apparatus: features that say "this report was written to a template",
# independent of what it found.  Named and counted separately so a reader can
# disagree with one and still use the others.
APPARATUS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("session_id", re.compile(r"SESSION-\d{8}")),
    ("target_pair", re.compile(r"対象対")),
    ("depth_table", re.compile(r"読んだ深さ")),
    ("disclaimer", re.compile(r"反省的|文芸的なモード")),
    ("provenance", re.compile(r"来歴")),
    ("three_judgments", re.compile(r"中心的な判断は三つ|中心的な結論")),
    ("ledger_section", re.compile(r"^##.*台帳", re.M)),
    ("limits", re.compile(r"限界|残ったこと")),
    ("two_questions", re.compile(r"二つの中心問い|AIから見た、人間とは何か|AIから見た人間")),
)

# Grammatical shapes of the answer to Q-001 ("what is a human").  The first two
# make the human a kind of system; the last two make it a kind of person.  The
# tool counts them; it does not claim the counts mean a change of mind.
SYSTEM_SHAPES = ("である系", "系である", "過程", "層", "分解")
PERSON_SHAPES = ("存在である", "有限者", "対話の相手", "かけがえのない", "美しき")


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------

def _candidate_paths(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    for sub in ("readings", "docs"):
        directory = root / sub
        if directory.is_dir():
            paths.extend(sorted(directory.glob("*.md")))
    paths.extend(sorted(root.glob("COGNITIVE_SCIENCE_REPORT*.md")))
    return paths


def _title(text: str) -> str:
    match = _H1.search(text)
    return match.group(1).strip() if match else ""


def discover(root: Path = ROOT, *, title_only: bool = False) -> list[dict[str, Any]]:
    """Return one record per corpus report, sorted by path.

    ``title_only`` narrows discovery to files whose H1 names 認知科学.  It exists
    so the report can show how much its numbers depend on the lexical rule:
    filename matches add 34 reports on the base measured (2026-11-23).
    """
    corpus: list[dict[str, Any]] = []
    for path in _candidate_paths(root):
        name = path.name
        if name in SELF_REPORTS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        title = _title(text)
        lexical = "cognitive-science" in name or "cogsci" in name
        keep = "認知科学" in title or (lexical and not title_only)
        if not keep:
            continue
        corpus.append(
            {
                "path": path.relative_to(root).as_posix(),
                "name": name,
                "title": title,
                "text": text,
                "date": _report_date(text, name),
                "bytes": len(text.encode("utf-8")),
            }
        )
    return corpus


def _report_date(text: str, name: str) -> str | None:
    """Real date of the work: the session stamp if present, else the filename."""
    match = _SESSION.search(text)
    if match:
        return match.group(1)
    match = _FILE_DATE.search(name)
    if match:
        return match.group(1).replace("-", "")
    return None


def _headings(text: str) -> set[str]:
    """H2 headings with list numbering removed, so 1./2./3. do not split a set."""
    out = set()
    for heading in _H2.findall(text):
        cleaned = re.sub(r"^\d+(\.\d+)*[.．]\s*", "", heading).strip()
        if cleaned:
            out.add(cleaned)
    return out


def _jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _apparatus(text: str) -> int:
    return sum(1 for _, pattern in APPARATUS if pattern.search(text))


# ---------------------------------------------------------------------------
# ledger readers (union of frozen base and shards)
# ---------------------------------------------------------------------------

def _load_rows(collection: str, root: Path = ROOT) -> list[dict[str, Any]]:
    base = root / "state" / f"{collection}.jsonl"
    files = [base] if base.is_file() else []
    shard_dir = root / "state" / f"{collection}.d"
    if shard_dir.is_dir():
        files.extend(sorted(shard_dir.glob("*.jsonl")))
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            handle = path.open(encoding="utf-8")
        except OSError:
            continue
        with handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def section_form(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in corpus:
        by_date[row["date"] or "unknown"].append(row)

    per_date = []
    for day in sorted(by_date):
        rows = by_date[day]
        scores = [_apparatus(row["text"]) for row in rows]
        per_date.append(
            {
                "date": day,
                "reports": len(rows),
                "mean_apparatus_of_9": round(sum(scores) / len(scores), 2),
                "max_apparatus": max(scores),
            }
        )

    # The late template: the reports of the last day that carry most of the
    # apparatus.  Compared against the earlier docs/ series.
    latest = max(by_date) if by_date else None
    tight = [row for row in by_date.get(latest, []) if _apparatus(row["text"]) >= 6]
    late_pairs = []
    for first, second in itertools.combinations(tight, 2):
        score = _jaccard(_headings(first["text"]), _headings(second["text"]))
        late_pairs.append(
            {
                "a": first["name"],
                "b": second["name"],
                "jaccard": round(score, 3),
            }
        )
    early = [row for row in corpus if row["path"].startswith("docs/")]
    early_scores = [
        _jaccard(_headings(first["text"]), _headings(second["text"]))
        for first, second in itertools.combinations(early, 2)
    ]

    def stats(values: list[float]) -> dict[str, Any]:
        if not values:
            return {"n": 0}
        return {
            "n": len(values),
            "mean": round(sum(values) / len(values), 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "gte_0.8": sum(1 for value in values if value >= 0.8),
        }

    late_scores = [pair["jaccard"] for pair in late_pairs]
    return {
        "corpus_reports": len(corpus),
        "dates": sorted(by_date),
        "per_date": per_date,
        "late_template": {
            "date": latest,
            "reports": len(tight),
            "pairwise_heading_jaccard": stats(late_scores),
            "identical_skeletons": [pair for pair in late_pairs if pair["jaccard"] >= 1.0],
        },
        "docs_series_pairwise_heading_jaccard": stats(early_scores),
    }


def section_reuse(corpus: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    corpus_cites: dict[str, set[str]] = defaultdict(set)
    for row in corpus:
        for material in _MAT_ID.findall(row["text"]):
            corpus_cites[material].add(row["name"])

    paths = [path for path in _candidate_paths(root) if path.name not in SELF_REPORTS]
    archive_cites: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for material in _MAT_ID.findall(text):
            archive_cites[material].add(path.name)

    same = older = newer = 0
    for row in corpus:
        if not row["date"]:
            continue
        for material in _MAT_DATE.findall(row["text"]):
            if material == row["date"]:
                same += 1
            elif material < row["date"]:
                older += 1
            else:
                newer += 1

    def once_share(cites: dict[str, set[str]]) -> dict[str, Any]:
        total = len(cites)
        once = sum(1 for reports in cites.values() if len(reports) == 1)
        return {
            "distinct_ids": total,
            "cited_by_one_report": once,
            "share_pct": round(once / total * 100, 1) if total else 0.0,
        }

    count = Counter(len(reports) for reports in corpus_cites.values())
    return {
        "corpus": once_share(corpus_cites),
        "archive_wide": once_share(archive_cites),
        "corpus_citation_counts": {f"cited_by_{k}": v for k, v in sorted(count.items())},
        "mint_vs_report_date": {"same_day": same, "older_material": older, "newer_material": newer},
    }


def section_depth(corpus: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    materials = {row["material_id"]: row for row in _load_rows("materials", root) if "material_id" in row}
    cited: set[str] = set()
    for row in corpus:
        cited.update(_MAT_ID.findall(row["text"]))

    status: Counter[str] = Counter()
    depth: Counter[str] = Counter()
    crosstab: Counter[str] = Counter()
    missing = 0
    for material_id in sorted(cited):
        record = materials.get(material_id)
        if record is None:
            missing += 1
            continue
        verification = record.get("verification") or {}
        status[str(verification.get("status"))] += 1
        depth[str(verification.get("depth"))] += 1
        crosstab[f"{verification.get('status')}|{verification.get('depth')}"] += 1

    recorded = sum(value for key, value in depth.items() if key not in ("None",))
    # The third axis of HYP-20261120-26b0c6 reads "全文通読（verified）".  `status`
    # and `depth` are separate columns, so a row can be verified without a depth:
    # worth counting rather than assuming the two coincide.
    verified = sum(value for key, value in status.items() if key == "verified")
    verified_full = sum(value for key, value in crosstab.items() if key == "verified|full_text")

    archive = Counter()
    for record in materials.values():
        verification = record.get("verification") or {}
        if verification.get("status") == "verified":
            archive["verified"] += 1
            if verification.get("depth") != "full_text":
                archive["verified_without_full_text"] += 1

    return {
        "corpus_cited_rows": len(cited),
        "not_in_ledger": missing,
        "status": dict(status.most_common()),
        "depth": dict(depth.most_common()),
        "status_x_depth": dict(crosstab.most_common()),
        "depth_recorded": recorded,
        "depth_recorded_pct": round(recorded / (len(cited) - missing) * 100, 1) if len(cited) > missing else 0.0,
        "verified_rows": verified,
        "verified_with_full_text_depth": verified_full,
        "archive_verified": archive.get("verified", 0),
        "archive_verified_without_full_text": archive.get("verified_without_full_text", 0),
    }


def section_chain(root: Path = ROOT) -> dict[str, Any]:
    notes = {row["note_id"]: row for row in _load_rows("notes", root) if "note_id" in row}
    lag: Counter[int] = Counter()
    same_day = 0
    total = 0
    unparseable = 0
    for row in _load_rows("read_log", root):
        target = row.get("target") or {}
        if target.get("type") != "note":
            continue
        note = notes.get(target.get("id"))
        if note is None:
            unparseable += 1
            continue
        try:
            made = date.fromisoformat(str(note.get("created_at", ""))[:10])
            read = date.fromisoformat(str(row.get("created_at", ""))[:10])
        except ValueError:
            unparseable += 1
            continue
        days = (read - made).days
        lag[days] += 1
        total += 1
        if days == 0:
            same_day += 1

    return {
        "note_read_rows": total,
        "same_day": same_day,
        "same_day_pct": round(same_day / total * 100, 1) if total else 0.0,
        "negative_lag_rows": sum(v for k, v in lag.items() if k < 0),
        "unresolved_targets": unparseable,
        "lag_days": {str(k): v for k, v in sorted(lag.items()) if -2 <= k <= 7},
    }


_H = re.compile(r"^(#{2,4})\s+(.*)$", re.M)
_Q1 = re.compile(r"(AIから見た、?人間とは何か|人間とは何か|AIから見た人間)")
_COVERAGE = re.compile(r"(含まない|範囲でしか|しかない|測っていない|限られる|ではない)")


def _q1_sections(text: str) -> list[str]:
    """The answer body of every heading that answers Q-001, up to the next peer."""
    heads = list(_H.finditer(text))
    out: list[str] = []
    for position, head in enumerate(heads):
        if not _Q1.search(head.group(2)):
            continue
        end = len(text)
        for later in heads[position + 1 :]:
            if len(later.group(1)) <= len(head.group(1)):
                end = later.start()
                break
        body = text[head.end() : end]
        if len(body) > 80:
            out.append(body)
    return out


def section_shape(corpus: list[dict[str, Any]]) -> dict[str, Any]:
    sentences = 0
    negated = 0
    for row in corpus:
        body = re.sub(r"^[|].*$", "", row["text"], flags=re.M)
        for sentence in _SENTENCE.split(body):
            if "人間" in sentence:
                sentences += 1
                if _NEGATION.search(sentence):
                    negated += 1

    q1_found = 0
    q1_covered = 0
    q1_bullets = 0
    for row in corpus:
        for body in _q1_sections(row["text"]):
            q1_found += 1
            q1_bullets += len(re.findall(r"^\s*[-*]\s", body, re.M))
            if _COVERAGE.search(body):
                q1_covered += 1

    shapes = Counter()
    for row in corpus:
        for phrase in SYSTEM_SHAPES:
            shapes[f"system:{phrase}"] += row["text"].count(phrase)
        for phrase in PERSON_SHAPES:
            shapes[f"person:{phrase}"] += row["text"].count(phrase)

    hypotheses = Counter()
    for row in corpus:
        for hypothesis in set(_HYP.findall(row["text"])):
            hypotheses[hypothesis] += 1

    return {
        "human_sentences": sentences,
        "human_sentences_with_negation": negated,
        "negation_share_pct": round(negated / sentences * 100, 1) if sentences else 0.0,
        "answer_shapes": dict(sorted(shapes.items())),
        "q1_sections": {
            "found": q1_found,
            "with_coverage_clause": q1_covered,
            "bullets": q1_bullets,
        },
        "hypotheses_named": len(hypotheses),
        "top_hypotheses": [
            {"hypothesis_id": hypothesis_id, "reports": count}
            for hypothesis_id, count in hypotheses.most_common(8)
        ],
        "cross_report_links": _cross_links(corpus),
    }


def section_verdicts(root: Path = ROOT) -> dict[str, Any]:
    """What operation the archive performs on hypotheses, across all evaluations."""
    rows = [row for row in _load_rows("evaluations", root) if row.get("verdict")]
    verdicts = Counter(row["verdict"] for row in rows)
    total = sum(verdicts.values())
    return {
        "evaluations": total,
        "verdicts": dict(verdicts.most_common()),
        "share_pct": {key: round(value / total * 100, 1) for key, value in verdicts.most_common()} if total else {},
        "evidence_types": dict(Counter(row.get("evidence_type") for row in rows).most_common()),
    }


def _cross_links(corpus: list[dict[str, Any]]) -> dict[str, int]:
    names = {row["name"] for row in corpus}
    linking = 0
    edges = 0
    for row in corpus:
        targets = {Path(target).name for target in _MD_LINK.findall(row["text"])}
        hits = (targets - {row["name"]}) & names
        if hits:
            linking += 1
            edges += len(hits)
    return {"reports_linking_another": linking, "reports": len(corpus), "edges": edges}


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def collect(root: Path = ROOT, *, title_only: bool = False) -> dict[str, Any]:
    corpus = discover(root, title_only=title_only)
    return {
        "basis": {
            "scanned": ["readings/*.md", "docs/*.md", "COGNITIVE_SCIENCE_REPORT*.md"],
            "self_excluded": sorted(SELF_REPORTS),
            "discovery": "H1 names 認知科学, or filename contains cognitive-science/cogsci",
        },
        "form": section_form(corpus),
        "reuse": section_reuse(corpus, root),
        "depth": section_depth(corpus, root),
        "chain": section_chain(root),
        "shape": section_shape(corpus),
        "verdicts": section_verdicts(root),
    }


def _print_human(payload: dict[str, Any]) -> None:
    form = payload["form"]
    print("== 形式（セッション見出しなど、内容と独立な型の数） ==")
    print(f"対象報告数: {form['corpus_reports']}  日付: {', '.join(form['dates'])}")
    print(f"{'日付':<10}{'報告':>5}{'平均装備数(/9)':>16}{'最大':>6}")
    for row in form["per_date"]:
        print(f"{row['date']:<10}{row['reports']:>5}{row['mean_apparatus_of_9']:>16}{row['max_apparatus']:>6}")
    late = form["late_template"]
    late_stats = late["pairwise_heading_jaccard"]
    early = form["docs_series_pairwise_heading_jaccard"]
    print(f"\n最終日の型を持つ報告 {late['reports']} 件（{late['date']}）の見出し集合 Jaccard:")
    print(f"  n={late_stats.get('n')} 平均={late_stats.get('mean')} 最大={late_stats.get('max')} J>=0.8={late_stats.get('gte_0.8')}対")
    for pair in late["identical_skeletons"]:
        print(f"  J=1.000 {pair['a']} と {pair['b']}")
    print(f"docs/ 期の見出し集合 Jaccard: n={early.get('n')} 平均={early.get('mean')} 最大={early.get('max')}")

    reuse = payload["reuse"]
    print("\n== 素材の再利用 ==")
    for label in ("corpus", "archive_wide"):
        row = reuse[label]
        print(f"  {label:<12} 異なりID {row['distinct_ids']:>5} / 1報告のみ {row['cited_by_one_report']:>5} ({row['share_pct']}%)")
    print(f"  参照の日付: 同日 {reuse['mint_vs_report_date']['same_day']} / 古い素材 {reuse['mint_vs_report_date']['older_material']} / 新しい素材 {reuse['mint_vs_report_date']['newer_material']}")

    depth = payload["depth"]
    print("\n== 引用された素材の照合状態 ==")
    print(f"  対象行 {depth['corpus_cited_rows']} 件（台帳に無い {depth['not_in_ledger']} 件）")
    print(f"  status: {depth['status']}")
    print(f"  depth : {depth['depth']}")
    print(f"  depth が記録された行: {depth['depth_recorded']} ({depth['depth_recorded_pct']}%)")
    print(f"  status×depth: {depth['status_x_depth']}")
    print(f"  verified 行 {depth['verified_rows']} のうち depth=full_text は {depth['verified_with_full_text_depth']}")
    print(f"  書庫全体: verified {depth['archive_verified']} のうち depth≠full_text {depth['archive_verified_without_full_text']}")

    chain = payload["chain"]
    print("\n== ノートを読む鎖 ==")
    print(f"  ノート対象の読書行 {chain['note_read_rows']} 件 / 同日 {chain['same_day']} ({chain['same_day_pct']}%) / 負のlag {chain['negative_lag_rows']} 件")

    shape = payload["shape"]
    print("\n== 人間の現れ方 ==")
    print(f"  「人間」を含む文 {shape['human_sentences']} 件 / 否定・留保語を伴う {shape['human_sentences_with_negation']} ({shape['negation_share_pct']}%)")
    q1 = shape["q1_sections"]
    print(f"  Q-001 への応答節 {q1['found']} 節 / 自ら範囲を限定する節 {q1['with_coverage_clause']} / 箇条書き {q1['bullets']} 項目")
    print(f"  語の生起（全体・文脈非統制）: {shape['answer_shapes']}")
    print(f"  言及された仮説 {shape['hypotheses_named']} 件 / 上位: " + ", ".join(f"{h['hypothesis_id']}({h['reports']})" for h in shape['top_hypotheses'][:5]))
    verdicts = payload.get("verdicts")
    if verdicts:
        print("\n== 台帳が仮説に行う操作 ==")
        print(f"  評価 {verdicts['evaluations']} 件: " + ", ".join(f"{k} {v} ({verdicts['share_pct'][k]}%)" for k, v in verdicts["verdicts"].items()))
    links = shape["cross_report_links"]
    print(f"  他の報告へリンクする報告 {links['reports_linking_another']}/{links['reports']}（辺 {links['edges']}）")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure the cognitive-science report corpus (read-only).")
    parser.add_argument("--section", choices=("all", "form", "reuse", "depth", "chain", "shape", "verdicts"), default="all")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    parser.add_argument(
        "--discovery",
        choices=("lexical", "title"),
        default="lexical",
        help="lexical: H1 or filename (default). title: H1 only, for the sensitivity check.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root).resolve()
    title_only = args.discovery == "title"
    corpus = discover(root, title_only=title_only)
    if args.section == "all":
        payload = collect(root, title_only=title_only)
    else:
        builders = {
            "form": lambda: section_form(corpus),
            "reuse": lambda: section_reuse(corpus, root),
            "depth": lambda: section_depth(corpus, root),
            "chain": lambda: section_chain(root),
            "shape": lambda: section_shape(corpus),
            "verdicts": lambda: section_verdicts(root),
        }
        payload = {args.section: builders[args.section]()}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
    else:
        if args.section == "all":
            _print_human(payload)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
