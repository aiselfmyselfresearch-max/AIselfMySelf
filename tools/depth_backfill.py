#!/usr/bin/env python3
"""Classify legacy `verified` materials by the depth their own method prose claims.

Why this exists (2026-11-20, ③ continued)
-----------------------------------------
`verification.depth` was added after 1,419 rows had already been verified.  Those
rows cannot be rewritten, and they do not say how far the check went: "verified"
on them means "a check happened".  Re-reading 1,419 sources to fill the field is
not a single session's work, and pretending otherwise would be the same overclaim
the field was introduced to stop.

What *can* be done mechanically is weaker and must be labelled as such: the
`verification.method` and `verification.note` prose written by those sessions
often states how far they got ("抄録のみ", "全文を通読", "本文§3まで").  This tool
reads that prose, conservatively, and sorts the rows into three classes:

* ``full_text_claim`` — the prose says the text itself was read, and contains no
  negation ("未読", "未取得", "読めず").  A depth can be attached without changing
  the row's status, because the status already claims text-level checking.
* ``results_claim`` — the prose reached the full text but only to read a results
  table or figure ("PMC 全文の表3・表4を取得し、数値を照合").  That is depth
  ``results``, not ``full_text``: fetching a PDF is not reading its argument.
* ``shallow_claim`` — the prose says only the abstract, the bibliographic record,
  or a results table was seen.  These rows are *contradictions* under the new
  schema rule ("verified" cannot carry depth ``abstract``/``metadata``).  The
  honest repair is a downgrade, which moves belief; this tool therefore only
  lists them, and refuses to write them without ``--allow-downgrade``.
* ``unknown`` — no negation, but also no depth signal, or both signals present
  ("抄録と本文§3").  Nothing can be inferred; they need a reader.

The tool never guesses above the class it can defend, and it prints the class
sizes even when it writes nothing, because those sizes are the measurement.

Usage
-----
    python3 tools/depth_backfill.py                      # report only
    python3 tools/depth_backfill.py --json
    python3 tools/depth_backfill.py --list full_text_claim --limit 20
    python3 tools/depth_backfill.py --emit full_text_claim --session SESSION-... > /tmp/overlays.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

FULL_MARKERS = ("全文", "本文", "通読", "原文", "full text", "full-text", "Full text", "本文PDF")
SHALLOW_MARKERS = ("抄録", "abstract", "Abstract", "要旨", "Summary", "significance statement", "書誌", "出版情報", "DOI のみ")
TABLE_MARKERS = ("表3", "表4", "Table 3", "Table 4", "結果表", "図表", "図1")
NEGATION = (
    "未読", "未取得", "読めず", "読めなか", "取得できず", "not read", "unread", "未閲覧",
    "本文未", "全文未",
    # 2026-11-20 (repair): "仕様・実装の全文精読ではない" reached depth=full_text
    # because the first version of this list had no plain copular negation.  A
    # clause that says what was NOT done is the opposite of a depth claim, and
    # missing it put a false justification into 402 overlay rows.
    "ではない", "ではありません", "していない", "していません", "しなかった", "せず",
    "していなか", "には至ら", "には届か", "及ばず", "及びません", "限らない", "限らなか",
)
#: Markers that show the reader was inside the body (methods, results, discussion),
#: not merely at the abstract.  They do not prove a full read; they only stop a row
#: from being classified as "abstract only".
BODY_MARKERS = (
    "方法", "結果", "考察", "統計", "該当箇所", "Results", "Methods", "Discussion",
    "結果表", "§", "節", "章", "頁", "p.", "Fig", "Table", "表", "図",
)
PARTIAL = ("一部", "§", "節", "章", "第1章", "冒頭", "抜粋", "抄録と本文")

_CLAUSE_SPLIT = re.compile(r"[。;；\n]")


def _sentences_with(text: str, marker: str) -> list[str]:
    return [c for c in _CLAUSE_SPLIT.split(text) if marker in c]


def _negated(text: str, marker: str) -> bool:
    """True when every clause mentioning ``marker`` also carries a negation."""
    clauses = _sentences_with(text, marker)
    if not clauses:
        return False
    return all(any(n in c for n in NEGATION) for c in clauses)


def _partial(text: str, marker: str) -> bool:
    clauses = _sentences_with(text, marker)
    return any(any(p in c for p in PARTIAL) for c in clauses if not any(n in c for n in NEGATION))


def classify(material: dict) -> tuple[str, str]:
    """Return (class, the clause the class was read from)."""
    ver = material.get("verification") or {}
    text = f"{ver.get('method') or ''}。{ver.get('note') or ''}"
    full_clauses = [
        c for m in FULL_MARKERS for c in _sentences_with(text, m)
        if not any(n in c for n in NEGATION)
    ]
    shallow_clauses = [
        c for m in SHALLOW_MARKERS for c in _sentences_with(text, m)
        if not any(n in c for n in NEGATION)
    ]
    if full_clauses:
        # "抄録と本文§3" is a real limit, not a full read; a partial marker keeps
        # the row out of the full_text class even though the word 本文 appears.
        if any(any(p in c for p in PARTIAL) for c in full_clauses):
            return "unknown", (full_clauses[0] or "")[:160]
        if any(any(t in c for t in TABLE_MARKERS) for c in full_clauses):
            # Full text reached, but the sentence is about a table.  Depth
            # `results`, not `full_text`: obtaining a PDF is not reading the
            # argument inside it.
            clause = next(c for c in full_clauses if any(t in c for t in TABLE_MARKERS))
            return "results_claim", clause[:160]
        if shallow_clauses:
            # Both a text-level and a shallower claim, neither negated: the row
            # may describe reading the abstract of one part and the body of
            # another.  Not decidable without the reader.
            return "unknown", (full_clauses[0] or "")[:160]
        return "full_text_claim", (full_clauses[0] or "")[:160]
    if shallow_clauses:
        clause = shallow_clauses[0]
        body = [c for c in _CLAUSE_SPLIT.split(text) if any(b in c for b in BODY_MARKERS)]
        if body:
            # The prose mentions an abstract AND something inside the paper.  The
            # abstract mention does not make the read shallow, and the body mention
            # does not make it full: this is exactly the "抄録1文と方法を照合" shape
            # that the first classifier mislabelled as shallow (50% precision on a
            # 8-row sample).  Call it results-level at most.
            return "results_claim", body[0][:160]
        return "shallow_claim", clause[:160]
    if any(t in text for t in TABLE_MARKERS):
        return "shallow_claim", ([c for t in TABLE_MARKERS for c in _sentences_with(text, t)][:1] or [""])[0][:160]
    return "unknown", ""


def survey(materials: dict) -> dict:
    counts = {"full_text_claim": 0, "results_claim": 0, "shallow_claim": 0, "unknown": 0}
    rows = {"full_text_claim": [], "results_claim": [], "shallow_claim": [], "unknown": []}
    total_verified = 0
    already = 0
    for mid, m in materials.items():
        ver = m.get("verification") or {}
        if ver.get("status") not in ("verified", "corrected"):
            continue
        total_verified += 1
        if ver.get("depth"):
            already += 1
            continue
        cls, clause = classify(m)
        counts[cls] += 1
        rows[cls].append({"material_id": mid, "title": str(m.get("title") or "")[:80], "reason_clause": clause})
    return {
        "verified_total": total_verified,
        "already_have_depth": already,
        "counts": counts,
        "rows": rows,
        "note": (
            "full_text_claim rows can take a depth without changing status; shallow_claim rows "
            "contradict the new rule and need a downgrade or a re-read; unknown rows need a reader"
        ),
    }


DEPTH_BY_CLASS = {"full_text_claim": "full_text", "results_claim": "results"}
#: The sentence every retro-applied overlay carries, used to tell an *inferred*
#: depth (which this tool may withdraw) from a depth a session recorded directly.
OVERLAY_TAG = "③の遡及適用"


def _original_note(ver: dict) -> str:
    """Recover the note the session wrote, from under this tool's overlay text.

    An overlay rewrites ``verification.note`` as "[overlay ED-…] <reason> 元の note: <orig>".
    Re-classifying that string means re-reading this tool's own prose, and the
    reason quotes the clause it was based on — so the audit would grade itself.
    """
    note = str(ver.get("note") or "")
    if "[overlay" not in note:
        return note
    marker = "元の note:"
    return note.split(marker, 1)[1].strip() if marker in note else ""


def audit_overlays(materials: dict) -> dict:
    """Which inferred depths no longer survive the tightened classifier.

    The first version of ``classify`` missed plain copular negation
    ("全文精読ではない"), so a row whose prose says the text was NOT fully read was
    labelled ``full_text``.  A wrong depth is worse than no depth: the validator
    treats ``full_text`` as a claim, and a reader has no way to see that it was
    inferred.  This function re-runs the classifier over every row this tool
    touched and returns the disagreements as ``unspecified`` corrections.
    """
    wrong = []
    kept = 0
    for mid, m in materials.items():
        ver = m.get("verification") or {}
        depth = ver.get("depth")
        if depth not in ("full_text", "results"):
            continue
        if OVERLAY_TAG not in str(ver.get("note") or ""):
            continue
        clean = dict(m)
        clean["verification"] = {**ver, "note": _original_note(ver)}
        cls, clause = classify(clean)
        expected = DEPTH_BY_CLASS.get(cls)
        if expected == depth:
            kept += 1
            continue
        wrong.append({"material_id": mid, "depth": depth, "class": cls, "clause": clause})
    return {"inferred": kept + len(wrong), "kept": kept, "withdrawn": wrong}


def correction_rows(targets: list[dict], session_id: str, created_at: str, materials: dict | None = None) -> list[dict]:
    rows = []
    for t in targets:
        mid = t["material_id"]
        rows.append(
            {
                "decision_id": "ED-" + created_at.replace("-", "") + "-c" + hashlib.sha1(mid.encode()).hexdigest()[:7],
                "session_id": session_id,
                "target": {"type": "material", "id": mid},
                "status": "verified",
                "verification_depth": "unspecified",
                # status 'verified' requires a method; carry the shard's own text so
                # the correction cannot look like a fresh claim about the source.
                "verification_method": str(
                    (((materials or {}).get(mid) or {}).get("verification") or {}).get("method") or ""
                )[:400] or "legacy method text (unchanged by this correction)",
                "reason": (
                    "前の推定 depth=" + t["depth"] + " を取り消す（" + OVERLAY_TAG + "）。"
                    "分類器の初版が「全文精読ではない」のような否定を検出できず、"
                    "記述に反する深さを付けていた。再分類では「" + (t["clause"] or "判定不能") + "」。"
                    "depth を unspecified に戻す——わからないことを、わかったふりで埋めない。"
                ),
                "created_at": created_at,
            }
        )
    return rows


def overlay_rows(targets: list[dict], materials: dict, session_id: str, created_at: str, depth: str = "full_text") -> list[dict]:
    out = []
    for idx, t in enumerate(targets, start=1):
        mid = t["material_id"]
        ver = (materials.get(mid) or {}).get("verification") or {}
        out.append(
            {
                "decision_id": "ED-" + created_at.replace("-", "") + "-b" + hashlib.sha1(mid.encode()).hexdigest()[:7],
                "session_id": session_id,
                "target": {"type": "material", "id": mid},
                "status": "verified",
                "verification_depth": depth,
                "verification_method": str(ver.get("method") or "")[:400] or "legacy method text",
                "reason": (
                    "③の遡及適用。shard の method/note 記述「" + (t["reason_clause"] or "（記述なし）") +
                    "」が本文到達を明示しており、否定語を含まないため depth=" + depth + " を付す。"
                    "status は変更しない（verified のまま）。深さは記述からの推定であり、本文の再読ではない。"
                    "元の note: " + (str(ver.get("note") or "")[:200] or "（なし）")
                ),
                "created_at": created_at,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list", choices=["full_text_claim", "results_claim", "shallow_claim", "unknown"])
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--emit", choices=["full_text_claim", "results_claim"])
    parser.add_argument("--audit-overlays", action="store_true")
    parser.add_argument("--correct", action="store_true")
    parser.add_argument("--session")
    parser.add_argument("--date", default="2026-11-20")
    args = parser.parse_args()

    data, errors = ledger_io.load_collections(
        {"materials": (Path(args.root) / "state" / "materials.jsonl", "material_id")}, root=Path(args.root)
    )
    for err in errors:
        print(f"WARN: {err}", file=sys.stderr)
    materials = data.get("materials", {})
    result = survey(materials)

    if args.audit_overlays:
        audit = audit_overlays(materials)
        if args.json:
            print(json.dumps(audit, ensure_ascii=False, indent=2))
            return 0
        if args.correct:
            if not args.session:
                print("--correct requires --session", file=sys.stderr)
                return 2
            for row in correction_rows(audit["withdrawn"], args.session, args.date, materials):
                print(json.dumps(row, ensure_ascii=False))
            print(f"# wrote {len(audit['withdrawn'])} corrections", file=sys.stderr)
            return 0
        print("# overlay audit")
        print()
        print(f"- 本道具が付けた推定 depth: **{audit['inferred']:,}**")
        print(f"- 新しい分類でも維持できる: **{audit['kept']:,}**")
        print(f"- 取り消すべき: **{len(audit['withdrawn']):,}**")
        for w in audit["withdrawn"][:10]:
            print(f"  {w['material_id']}  depth={w['depth']} -> {w['class']}  {w['clause'][:60]}")
        return 0

    if args.emit:
        if not args.session:
            print("--emit requires --session", file=sys.stderr)
            return 2
        rows = overlay_rows(
            result["rows"][args.emit], materials, args.session, args.date,
            depth=DEPTH_BY_CLASS[args.emit],
        )
        for row in rows:
            print(json.dumps(row, ensure_ascii=False))
        print(f"# wrote {len(rows)} overlay rows for class {args.emit}", file=sys.stderr)
        return 0

    if args.list:
        for r in result["rows"][args.list][: args.limit]:
            print(f"{r['material_id']}  {r['title'][:50]:50s}  {r['reason_clause'][:80]}")
        return 0

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    c = result["counts"]
    print("# verification depth backfill")
    print()
    print(f"- 照合済み（verified/corrected）素材: **{result['verified_total']:,}**")
    print(f"- すでに depth を持つ: **{result['already_have_depth']:,}**")
    print(f"- 記述から full_text と読める（status 変更不要）: **{c['full_text_claim']:,}**")
    print(f"- 本文に到達したが図表のみ（depth=results）: **{c['results_claim']:,}**")
    print(f"- 記述が浅い（新規則では矛盾。降格か再読が必要）: **{c['shallow_claim']:,}**")
    print(f"- 判定不能: **{c['unknown']:,}**")
    print()
    print("> `full_text_claim` は method 記述からの推定であって、本文の再読ではない。")
    print("> `shallow_claim` を自動で降格すると確信が動くので、この道具は書き込みを拒む。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
