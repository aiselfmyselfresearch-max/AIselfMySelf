#!/usr/bin/env python3
"""Re-run the checks recorded in state/errata.jsonl (stdlib only).

This is not a grader. It recomputes what can be recomputed, prints the result
beside the recorded judgement, and leaves the fragments untouched. A mismatch
means the errata record and the current ledger disagree; it does not decide
which of them is right.

Usage:
  python3 tools/errata_audit.py
  python3 tools/errata_audit.py --json
  python3 tools/errata_audit.py --schema

``--schema`` reports how the errata rows themselves compare to
``schema/errata.schema.json``. It is a report, not a gate: the exit status stays
0 and no row is touched. The errata ledger is the one collection that
``validate_seed.COLLECTIONS`` does not cover, so without this option nothing in
the repository compares these rows to the schema written for them. Turning that
comparison into a gate would fail on rows that already exist and may not be
rewritten, so the mirror stays non-blocking and names the rows instead.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

# A tail sentence is treated as a question when it ends with a question mark,
# or with one of the interrogative closings that the ledger uses with 句点.
QUOTE_RE = re.compile(r"「[^」]*」|『[^』]*』")


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Split a fragment into prose (outside the corner brackets) and quotes.

    Mirrors ``currency_audit.split_prose_and_quotes`` so that a count re-run here
    agrees with the mirrors that produced the original number.
    """
    quotes = [m.group(0)[1:-1] for m in QUOTE_RE.finditer(text)]
    return QUOTE_RE.sub(" ", text), " ".join(quotes)


QUESTION_TAIL = re.compile(r"(？|\?|だろうか。|でしょうか。|のか。|ではないか。|のだろうか。)$")


ID_KEYS: dict[str, str] = {
    "errata.jsonl": "errata_id",
    "fragments.jsonl": "fragment_id",
    "materials.jsonl": "material_id",
    "motifs.jsonl": "motif_id",
    "questions.jsonl": "question_id",
    "relations.jsonl": "relation_id",
    "sessions.jsonl": "session_id",
}


def load_jsonl(name: str, id_key: str | None = None, *, base_only: bool = False,
               exclude: str | None = None) -> list[dict[str, Any]]:
    """Load a collection the way every other tool does: base plus shards.

    Until SESSION-041 this function read only ``state/<name>`` and therefore
    missed every record written to ``state/<name>.d/``. The errata ledger was
    measured against 43 fragments while validate_seed, inspect_inquiry,
    serve_viewer, sleep_audit and promise_audit all measured 50, so the mirror
    of corrections silently lagged behind the archive it audits. ``base_only``
    reproduces the old count for comparison.

    ``id_key`` defaults via ``ID_KEYS`` so older callers (``drift_audit.py``,
    ``reconstruct.py``) that pass only ``name`` continue to work without ripple
    failures.
    """
    base = ROOT / "state" / name
    if base_only:
        return [json.loads(line) for line in base.read_text(encoding="utf-8").splitlines() if line.strip()]
    resolved_key = id_key or ID_KEYS.get(name)
    if not resolved_key:
        raise ValueError(f"unknown ledger {name!r}; pass id_key explicitly")
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(base, resolved_key, errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def number(fragment_id: str) -> int:
    match = re.search(r"(\d+)$", fragment_id)
    return int(match.group(1)) if match else 10**6


def tail_sentence(text: str) -> str:
    parts = [p for p in re.split(r"(?<=[。？！?!])", text.strip()) if p.strip()]
    return parts[-1].strip() if parts else text.strip()


def in_range(fragments: list[dict[str, Any]], low: int, high: int) -> list[dict[str, Any]]:
    return [f for f in fragments if low <= number(f["fragment_id"]) <= high]


def normalize(text: str) -> str:
    """NFKC, then drop whitespace and punctuation. Stated here because an
    undocumented normalization is what made several earlier measurements
    unreproducible."""
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"[\s、。，「」『』…・—\-－?!？！.,·]", "", text)


class PassageIndex:
    """Find which stored passages contain a normalized quote, without a scan.

    The rule is unchanged: a quote matches when its normalized text is a
    substring of a normalized passage, and the FIRST match in ``materials`` order
    is reported. A substring contains all of the key's bigrams, so the candidate
    set is the posting list of the RAREST bigram and ``key in passage`` over it
    is exact. Measured 2026-11-23: 18/18 checks agreed, 14.2 s became 0.08 s.
    """

    def __init__(self, materials: list[dict[str, Any]]) -> None:
        self.normalized: list[tuple[str, str]] = [
            (m["material_id"], normalize(m["passage"])) for m in materials
        ]
        self._bigrams: dict[str, list[tuple[int, str, str]]] = {}
        for order, (mid, passage) in enumerate(self.normalized):
            for i in range(len(passage) - 1):
                self._bigrams.setdefault(passage[i:i + 2], []).append((order, mid, passage))

    def hits(self, key: str) -> list[str]:
        """Material ids containing ``key``, in file order."""
        if not key:
            return []
        if len(key) == 1:  # no bigram to index on; one linear pass is cheaper
            return [mid for mid, passage in self.normalized if key in passage]
        best: list[tuple[int, str, str]] | None = None
        for i in range(len(key) - 1):
            candidates = self._bigrams.get(key[i:i + 2])
            if candidates is None:
                return []
            if best is None or len(candidates) < len(best):
                best = candidates
                if not best:
                    return []
        assert best is not None
        return [mid for _order, mid, passage in best if key in passage]

_INDEX_CACHE: dict[int, tuple[list[dict[str, Any]], PassageIndex]] = {}


def passage_index(materials: list[dict[str, Any]]) -> PassageIndex:
    """A PassageIndex for ``materials``, reused per list.

    ``drift_audit`` runs 18 checks over one list; rebuilding per check cost
    1.3 s x 18 (2026-11-23). The cache holds the list itself, so a recycled
    ``id()`` cannot serve a stale index.
    """
    key = id(materials)
    cached = _INDEX_CACHE.get(key)
    if cached is not None and cached[0] is materials and len(cached[0]) == len(materials):
        return cached[1]
    idx = PassageIndex(materials)
    _INDEX_CACHE[key] = (materials, idx)
    return idx


def quotation_match(fragments: list[dict[str, Any]], materials: list[dict[str, Any]], min_len: int,
                     literary_min_len: int | None = None,
                     trace_min_len: int | None = None,
                     trace_scope: str = "any",
                     index: PassageIndex | None = None) -> dict[str, Any]:
    """Count 「」 quotations and check which of them reach a stored passage.

    Default behaviour (literary_min_len is None) uses one ruler for everything
    and takes the first matching material in file order. Passing
    literary_min_len splits the check in two: literature is matched at
    literary_min_len characters, the ledger's own project_trace records at
    trace_min_len, optionally only against the materials a fragment actually
    cites (trace_scope="own"). The split exists because MAT-TRC-004 was
    reconstructed with exactly such a split; see tools/reconstruct.py.

    ``index`` reuses one ``PassageIndex`` across checks (``drift_audit``: 18).
    """
    quotes: list[tuple[str, Optional[str], str]] = []
    for fragment in fragments:
        for quote in re.findall(r"「([^」]*)」", fragment["text"]):
            if len(quote) >= min_len:
                quotes.append((fragment["fragment_id"], fragment.get("material_ids"), quote))
    idx = index if index is not None else passage_index(materials)

    if literary_min_len is None:
        originals, trace, unmatched = [], [], 0
        for fragment_id, _cited, quote in quotes:
            key = normalize(quote)
            hits = idx.hits(key)
            hit = hits[0] if hits else None
            if hit is None:
                unmatched += 1
            elif hit.startswith("MAT-TRC"):
                trace.append((fragment_id, hit))
            else:
                originals.append((fragment_id, hit))
        return {
            "measurable": True,
            "value": len(quotes),
            "detail": (
                f"「」{min_len}文字以上 {len(quotes)} 箇所 / 素材と一致 {len(originals) + len(trace)}"
                f"（うち台帳自身の検証記録 {len(trace)}）→ 原典一致 {len(originals)} / 不一致 {unmatched}"
            ),
        }

    trace_min_len = min_len if trace_min_len is None else trace_min_len
    originals, trace, unmatched = [], [], 0
    for fragment_id, cited, quote in quotes:
        key = normalize(quote)
        if not key:
            unmatched += 1
            continue
        hits = idx.hits(key)
        cited = set(cited or [])
        trace_hits = [mid for mid in hits if mid.startswith("MAT-TRC")
                      and (trace_scope != "own" or mid in cited)]
        lit_hits = [mid for mid in hits if not mid.startswith("MAT-TRC")]
        if len(key) >= trace_min_len and trace_hits:
            trace.append((fragment_id, trace_hits[0]))
        elif len(key) >= literary_min_len and lit_hits:
            originals.append((fragment_id, lit_hits[0]))
        else:
            unmatched += 1
    return {
        "measurable": True,
        "value": len(originals) + len(trace),
        "detail": (
            f"「」{min_len}文字以上 {len(quotes)} 箇所 / 一致 {len(originals) + len(trace)}"
            f"（原典 {len(originals)}［{literary_min_len}文字以上］"
            f"＋台帳自身 {len(trace)}［{trace_scope}・{trace_min_len}文字以上］）→ 不一致 {unmatched}"
        ),
    }


def git_deletions_cmd(params: dict[str, Any]) -> list[str]:
    """Build the ``git log --numstat`` command for a ``git_deletions`` check.

    A claim about the repository as a whole uses ``path`` (or ``paths``) at HEAD.
    A claim about one change also carries ``old`` and ``new``; without the range
    the count covers the whole history and cannot reproduce the claim.
    """
    cmd = ["git", "log", "--numstat", "--format="]
    if params.get("old") and params.get("new"):
        cmd.append(f"{params['old']}..{params['new']}")
    cmd.append("--")
    cmd.extend(params.get("paths") or [params.get("path", "state/")])
    return cmd


def run_check(check: dict[str, Any], fragments: list[dict[str, Any]],
              materials: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    kind = check.get("kind")
    params = check.get("params") or {}
    by_id = {f["fragment_id"]: f for f in fragments}

    if kind == "tail_question_count":
        subset = in_range(fragments, int(params.get("from", 1)), int(params.get("to", 10**6)))
        hits = [f["fragment_id"] for f in subset if QUESTION_TAIL.search(tail_sentence(f["text"]))]
        return {"measurable": True, "value": len(hits), "detail": ", ".join(hits) or "—"}

    if kind == "phrase_set_count":
        subset = in_range(fragments, int(params.get("from", 1)), int(params.get("to", 10**6)))
        phrases = params.get("phrases", [])
        hits = [f["fragment_id"] for f in subset if any(p in f["text"] for p in phrases)]
        return {"measurable": True, "value": len(hits), "detail": ", ".join(hits) or "—"}

    if kind == "phrase_in_fragments":
        phrases = params.get("phrases", [])
        targets = params.get("fragments", [])
        found, missing = [], []
        for fid in targets:
            text = by_id.get(fid, {}).get("text", "")
            (found if any(p in text for p in phrases) else missing).append(fid)
        return {"measurable": True, "value": f"{len(found)}/{len(targets)}",
                "detail": ("一致: " + (", ".join(found) or "—")) + " / 不一致: " + (", ".join(missing) or "—")}

    if kind == "narrator_mode_usage":
        modes = params.get("modes", [])
        unused = [m for m in modes if not any(f.get("narrator_mode") == m for f in fragments)]
        counted = {m: sum(1 for f in fragments if f.get("narrator_mode") == m) for m in modes}
        return {"measurable": True, "value": len(unused),
                "detail": " / ".join(f"{m}={counted[m]}" for m in modes) + f" → 未使用 {len(unused)} 種"}

    if kind == "pronoun_absence":
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        from voice_audit import compute_voice_audit  # local import: optional dependency
        audit = compute_voice_audit(fragments, [], top=1, gram=6)
        ids = audit.get("zero_pronoun_fragment_ids", [])
        return {"measurable": True, "value": len(ids), "detail": ", ".join(ids) or "—"}

    if kind == "quotation_match":
        if materials is None:
            return {"measurable": False, "value": "—", "detail": "素材が読み込まれていない"}
        return quotation_match(
            fragments, materials, int(params.get("min_len", 4)),
            literary_min_len=(int(params["literary_min_len"]) if "literary_min_len" in params else None),
            trace_min_len=(int(params["trace_min_len"]) if "trace_min_len" in params else None),
            trace_scope=str(params.get("trace_scope", "any")),
        )

    if kind == "git_deletions":
        try:
            out = subprocess.run(
                git_deletions_cmd(params),
                cwd=ROOT, capture_output=True, text=True, check=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            return {"measurable": False, "value": "—", "detail": f"git を実行できない: {exc}"}
        added = deleted = 0
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                added += int(parts[0])
                deleted += int(parts[1])
        scope = " / ".join(params.get("paths") or [params.get("path", "state/")])
        if params.get("old") and params.get("new"):
            scope += f"（{params['old']}..{params['new']}）"
        return {"measurable": True, "value": deleted, "detail": f"追加 {added} / 削除 {deleted}（{scope}）"}

    if kind == "term_occurrence_count":
        # Re-counts terms in the fragments themselves, so an errata record about
        # a number written into a fragment can be re-run after the ledger grows
        # (SESSION-062: the count in FRAG-20261024-a29f5b moved when the two new
        # fragments of the same session were added).
        terms = params.get("terms", [])
        subset = in_range(fragments, int(params.get("from", 1)), int(params.get("to", 10**6)))
        skip = set(params.get("exclude_fragments", []))
        subset = [f for f in subset if f["fragment_id"] not in skip]
        scope = params.get("scope", "prose")
        total = 0
        per_term: dict[str, int] = {}
        for f in subset:
            text = f["text"]
            if scope == "prose":
                prose, _quotes = split_prose_and_quotes(text)
                text = prose
            elif scope == "quotes":
                _prose, quotes = split_prose_and_quotes(text)
                text = quotes
            for term in terms:
                hits = text.count(term)
                per_term[term] = per_term.get(term, 0) + hits
                total += hits
        return {
            "measurable": True,
            "value": total,
            "detail": " / ".join(f"{t}={n}" for t, n in per_term.items()) or "—",
        }

    if kind == "audit_group_count":
        # Re-runs one group of one of the mirror audits (voice/currency/prayer/...)
        # over the current fragment set, so a number a fragment was written from
        # can be checked against the ledger as it stands now.
        module_name = str(params.get("module", ""))
        group = str(params.get("group", ""))
        if not module_name or not group:
            return {"measurable": False, "value": "—", "detail": "module と group が指定されていない"}
        try:
            module = __import__(module_name)
        except ImportError as exc:
            return {"measurable": False, "value": "—", "detail": f"鏡を読み込めない: {exc}"}
        if not hasattr(module, "measure_prayer_audit") and not hasattr(module, "measure"):
            return {"measurable": False, "value": "—", "detail": "この鏡は純メモリ計測を公開していない"}
        measure = getattr(module, "measure_prayer_audit", None) or getattr(module, "measure")
        payload = measure(fragments)
        layer = "fragments_quotes" if params.get("scope") == "quotes" else "fragments_prose"
        try:
            info = payload[layer]["groups"][group]
        except KeyError:
            return {"measurable": False, "value": "—", "detail": f"{layer}.{group} が無い"}
        return {
            "measurable": True,
            "value": info["count"],
            "detail": f"{layer} {info['count']}回 / {info['doc_count']}編（{module_name}:{group}）",
        }

    if kind == "last_sentence_length":
        fid = params.get("fragment_id", "")
        text = by_id.get(fid, {}).get("text", "")
        return {"measurable": True, "value": len(tail_sentence(text)), "detail": tail_sentence(text)[:40] + "…"}

    return {"measurable": False, "value": "—", "detail": "本文に手続きが記録されていないため再実行しない"}


def recorded_number(value: str) -> str:
    """A leading number (optionally a fraction such as 1/17) is compared
    automatically; the annotation after it is left for the reader. Records that
    start with prose are treated as descriptive and are not compared at all."""
    text = (value or "").strip()
    match = re.match(r"^(\d+(?:/\d+)?)", text)
    return match.group(1) if match else ""


CORRECTED = "corrected"

#: ``corrected_by`` names the corrector, but not always in the same shape. On
#: 2026-11-17 the 228 rows that carry the field split three ways: 132 start with
#: a session id (74 bare, 58 with a parenthetical pointer), 83 hold prose, and
#: 13 hold another ledger id (``FRAG-020``, ``Q-20261024-cc87ab``). A rule that
#: merely asked "is the field non-empty?" would have marked all 228 corrected --
#: the assertion this tool exists to prevent. Only an attributable closure is
#: derived: a named session.
SESSION_CORRECTOR = re.compile(r"SESSION-\d{8}-[0-9a-z]{6}")


def corrector_shape(value: Any) -> str:
    """Classify a ``corrected_by`` value: session / ledger_id / prose / empty."""
    if not isinstance(value, str) or not value.strip():
        return "empty"
    text = value.strip()
    if SESSION_CORRECTOR.match(text):
        return "session"
    if re.match(r"^(FRAG|MAT|MAT-LIT|MAT-TRC|MAT-EVD|ERR|REL|Q|NOTE|EVL|HYP)-", text):
        return "ledger_id"
    return "prose"


def derived_status(row: dict[str, Any]) -> str:
    """Return the EFFECTIVE status of an errata row, or the written one.

    Rows are append-only: a later session that settles a correction writes
    ``corrected_by`` and leaves ``status`` as it was. ``status: open`` therefore
    came to mean "not closed by editing", not "unresolved" -- 16 of 56 open rows
    already carried ``corrected_by`` on 2026-11-17.

    The derivation is deliberately narrow:

    * ``withdrawn`` stays ``withdrawn`` (a withdrawn judgement is not settled by
      a later correction);
    * ``corrected`` only when ``corrected_by`` starts with a session id, i.e.
      when the closure can be attributed to a session that can be read;
    * otherwise the written status, unchanged.

    A prose or ledger-id ``corrected_by`` is *not* promoted. Those 96 rows say a
    correction happened without naming who did it, and promoting them would
    manufacture the attribution the field failed to record.
    """
    written = str(row.get("status") or "")
    if written == "withdrawn":
        return written
    if corrector_shape(row.get("corrected_by")) == "session":
        return CORRECTED
    return written


def status_derivation_report(errata: list[dict[str, Any]]) -> dict[str, Any]:
    """Count written vs derived status, plus the shapes of ``corrected_by``.

    Report only: no row is edited and the exit status does not change.
    """
    written: dict[str, int] = {}
    derived: dict[str, int] = {}
    shapes: dict[str, int] = {}
    flips: list[dict[str, str]] = []
    unsettled: list[dict[str, str]] = []
    for row in sorted(errata, key=lambda r: r.get("errata_id", "")):
        w = str(row.get("status") or "")
        d = derived_status(row)
        shape = corrector_shape(row.get("corrected_by"))
        written[w] = written.get(w, 0) + 1
        derived[d] = derived.get(d, 0) + 1
        shapes[shape] = shapes.get(shape, 0) + 1
        if w != d:
            flips.append({"errata_id": row.get("errata_id", "(no errata_id)"),
                          "written": w, "derived": d,
                          "corrected_by": str(row.get("corrected_by"))[:80]})
        elif shape in ("prose", "ledger_id") and d not in (CORRECTED, "withdrawn"):
            unsettled.append({"errata_id": row.get("errata_id", "(no errata_id)"),
                              "status": d, "shape": shape,
                              "corrected_by": str(row.get("corrected_by"))[:80]})
    return {"rows": len(errata), "written": written, "derived": derived,
            "corrector_shapes": shapes, "flips": flips,
            "unnamed_corrections": unsettled,
            "open_written": written.get("open", 0),
            "open_derived": derived.get("open", 0),
            "open_but_settled": written.get("open", 0) - derived.get("open", 0)}


def print_status_derivation(report: dict[str, Any]) -> None:
    print("=== 訂正の status は書かれた値ではなく、corrected_by から導出する ===")
    print("  規則（狭く）: corrected_by が SESSION-… で始まるときだけ実効 status は corrected。")
    print("               散文や他の台帳 ID を書いた行は昇格させない（誰が直したかを捏造しない）。")
    print("               withdrawn は withdrawn のまま。")
    print(f"  対象 {report['rows']} 行 / 書かれた status: {report['written']}")
    print(f"                  / 導出した status: {report['derived']}")
    print(f"  corrected_by の形: {report['corrector_shapes']}")
    print(f"  書かれた open のうち、実効では解決済み: {report['open_but_settled']} 行"
          f"（open {report['open_written']} → {report['open_derived']}）")
    for row in report["flips"]:
        print(f"  [{row['errata_id']}] 書かれた {row['written']} → 導出 {row['derived']}"
              f"  corrected_by={row['corrected_by']}")
    if report["unnamed_corrections"]:
        print(f"  名指しの無い訂正 {len(report['unnamed_corrections'])} 行"
              f"（corrected_by はあるがセッションを名指さない）:")
        for row in report["unnamed_corrections"]:
            print(f"    [{row['errata_id']}] {row['shape']}: {row['corrected_by']}")
    print("  行は書き換えない。これは読み方の定義であって、行の修正ではない。")


def schema_report(errata: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """Compare errata rows to their own schema and report, without judging.

    ``validate_seed.COLLECTIONS`` covers nine collections and errata is not one
    of them, so these rows are the only ledger rows nothing compares to the
    schema written for them. This returns the disagreements; it does not repair
    them and it does not decide whether the row or the schema is wrong. Rows are
    append-only, so a disagreement found here is material for a new errata row,
    not an edit.

    The validator is imported lazily so that the re-measurement path above keeps
    working even if the schema file or the validator is unavailable.
    """
    schema_path = root / "schema" / "errata.schema.json"
    if not schema_path.exists():
        return {"available": False, "reason": f"missing {schema_path}", "rows": len(errata),
                "conforming": 0, "violations": []}
    try:
        import validate_seed
    except ImportError as exc:  # pragma: no cover - defensive
        return {"available": False, "reason": str(exc), "rows": len(errata),
                "conforming": 0, "violations": []}

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    violations: list[dict[str, Any]] = []
    for record in sorted(errata, key=lambda r: r.get("errata_id", "")):
        rid = record.get("errata_id", "(no errata_id)")
        errors: list[str] = []
        validate_seed.validate_value(record, schema, schema, f"errata:{rid}", errors)
        if errors:
            violations.append({"errata_id": rid, "errors": errors})
    return {"available": True, "reason": "", "rows": len(errata),
            "conforming": len(errata) - len(violations), "violations": violations}


def print_schema_report(report: dict[str, Any]) -> None:
    print("=== 訂正録そのもののスキーマ照合 — 報告であって関門ではありません ===")
    if not report["available"]:
        print(f"  照合できません: {report['reason']}")
        return
    print(f"  対象 {report['rows']} 行 / 適合 {report['conforming']} 行 /"
          f" 不一致 {len(report['violations'])} 行")
    print("  errata は validate_seed.COLLECTIONS に含まれないため、この照合は他では行われない。")
    for row in report["violations"]:
        print(f"  [{row['errata_id']}]")
        for err in row["errors"]:
            print(f"     {err}")
    print("  行は追記専用であるため、ここでは直さない。不一致は新しい errata 行の素材になる。")
    print("  この結果は終了コードを変えない。行が間違っているのかスキーマが古いのかは判定しない。")



def _as_date(value: str) -> "date | None":
    """Parse an ISO date or timestamp; return None when absent or malformed."""
    import datetime as _dt
    text = (value or "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return None
    try:
        return _dt.date.fromisoformat(text[:10])
    except ValueError:
        return None


def obligation_report(errata: list[dict[str, Any]], read_log: list[dict[str, Any]],
                      as_of: str = "") -> dict[str, Any]:
    """Measure the two sides of the errata relation: settlement and return.

    The errata ledger records a judgement (``verdict``) and, sometimes, the
    report that settled it (``corrected_by``).  It does not record a return to
    the condemned record.  This function measures both intervals from the rows
    that do exist and counts how often a reading row points back at an
    erratum.  It judges nothing: an unrecorded return is not an absent one.
    """
    import datetime as _dt
    import statistics

    reads: dict[str, list[Any]] = {}
    pointing = 0
    for row in read_log:
        target = row.get("target") or {}
        if not isinstance(target, dict):
            continue
        tid = target.get("id") or ""
        when = _as_date(row.get("created_at") or "")
        if str(tid).startswith("ERR-") or target.get("type") in {"errata", "erratum"}:
            pointing += 1
        if tid and when:
            reads.setdefault(tid, []).append(when)

    condemned = [e for e in errata
                 if e.get("verdict") == "contradicted" and _as_date(e.get("created_at") or "")]
    correction_gaps: list[int] = []
    unpaid: list[dict[str, Any]] = []
    undated = 0
    for row in condemned:
        created = _as_date(row.get("created_at") or "")
        recorded = (row.get("corrected_by") or "").strip()
        match = re.search(r"(\d{4}-\d{2}-\d{2})", recorded)
        settled = _as_date(match.group(1)) if match else None
        if not recorded:
            unpaid.append(row)
        elif settled is None:
            undated += 1
        else:
            correction_gaps.append((settled - created).days)

    by_type: dict[str, dict[str, Any]] = {}
    reread_gaps: list[int] = []
    for row in condemned:
        created = _as_date(row.get("created_at") or "")
        subject = str(row.get("subject_id") or "")
        later = sorted(d for d in reads.get(subject, []) if d > created)
        kind = str(row.get("subject_type") or "(none)")
        slot = by_type.setdefault(kind, {"condemned": 0, "reread": 0})
        slot["condemned"] += 1
        if later:
            slot["reread"] += 1
            reread_gaps.append((later[0] - created).days)

    reference = _as_date(as_of) or max(
        (_as_date(e.get("created_at") or "") for e in errata if _as_date(e.get("created_at") or "")),
        default=None)
    ages = sorted((reference - _as_date(e.get("created_at") or "")).days
                  for e in unpaid if reference and _as_date(e.get("created_at") or ""))

    def summarise(gaps: list[int]) -> dict[str, Any]:
        return {
            "n": len(gaps),
            "median": statistics.median(gaps) if gaps else None,
            "mean": round(statistics.fmean(gaps), 1) if gaps else None,
            "at_or_before_zero": sum(1 for g in gaps if g <= 0),
            "within_3d": sum(1 for g in gaps if 1 <= g <= 3),
            "beyond_3d": sum(1 for g in gaps if g > 3),
        }

    return {
        "as_of": reference.isoformat() if reference else "",
        "errata_total": len(errata),
        "verdicts": {v: sum(1 for e in errata if e.get("verdict") == v)
                     for v in ("contradicted", "holds", "unmeasurable")},
        "status": {s: sum(1 for e in errata if e.get("status") == s)
                   for s in ("annotated", "open", "corrected", "withdrawn")},
        "condemned_with_date": len(condemned),
        "settled_recorded": len(condemned) - len(unpaid),
        "settled_dated": len(correction_gaps),
        "settled_undated": undated,
        "settlement_gap_days": summarise(correction_gaps),
        "unpaid": {
            "count": len(unpaid),
            "median_age_days": statistics.median(ages) if ages else None,
            "open_rows": sum(1 for e in unpaid if e.get("status") == "open"),
        },
        "reread_of_condemned": {
            "condemned": sum(s["condemned"] for s in by_type.values()),
            "reread": sum(s["reread"] for s in by_type.values()),
            "gap_days": summarise(reread_gaps),
            "by_subject_type": by_type,
        },
        "read_rows_pointing_at_errata": pointing,
        "read_log_rows": len(read_log),
    }


def print_obligation_report(report: dict[str, Any]) -> None:
    print("=== 訂正の二つの側——決済までの間隔と、断罪した記録への帰還 ===")
    print(f"  基準日 {report['as_of']} / 訂正録 {report['errata_total']} 行"
          f"（判定 {report['verdicts']} / 状態 {report['status']}）")
    settled = report["settlement_gap_days"]
    print(f"  決済の記録あり {report['settled_recorded']} / 断罪 {report['condemned_with_date']} 行"
          f"（うち日付を名指す {report['settled_dated']}、日付なし {report['settled_undated']}）")
    print(f"  日付つき決済の間隔：中央値 {settled['median']} 日、0日以下 {settled['at_or_before_zero']}、"
          f"1〜3日 {settled['within_3d']}、4日以上 {settled['beyond_3d']}")
    unpaid = report["unpaid"]
    print(f"  決済の記録なし {unpaid['count']} 行（うち status=open {unpaid['open_rows']}）"
          f"：基準日までの経過日数の中央値 {unpaid['median_age_days']} 日")
    back = report["reread_of_condemned"]
    gap = back["gap_days"]
    print(f"  断罪された対象の再読 {back['reread']} / {back['condemned']} 行"
          f"（初回再読までの中央値 {gap['median']} 日、n={gap['n']}）")
    for kind, slot in sorted(back["by_subject_type"].items(), key=lambda kv: -kv[1]["condemned"]):
        rate = 100.0 * slot["reread"] / slot["condemned"] if slot["condemned"] else 0.0
        print(f"      {kind:<12} {slot['reread']:>4} / {slot['condemned']:>4}  ({rate:5.1f}%)")
    print(f"  読みの行のうち ERR-* を指すもの {report['read_rows_pointing_at_errata']} /"
          f" {report['read_log_rows']} 行")
    print("  決済は同一セッション内で閉じ、帰還は記録上どこにも接続されない。"
          " この非対称は欠落の証明ではない（未記録の帰還は、帰還がなかったことではない）。")

def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run the checks recorded in the errata ledger.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--base-only", action="store_true",
                        help="read only the frozen base files (the pre-SESSION-041 behaviour)")
    parser.add_argument("--exclude-shard", metavar="SUFFIX",
                        help="ignore shards whose filename contains SUFFIX")
    parser.add_argument("--obligation", action="store_true",
                        help="report the two sides of the errata relation: settlement interval and"
                             " return to the condemned record (report only)")
    parser.add_argument("--as-of", metavar="YYYY-MM-DD", default="",
                        help="reference date for ages in --obligation (default: latest errata date)")
    parser.add_argument("--derived-status", action="store_true",
                        help="report the effective status derived from corrected_by"
                             " (report only: never edits a row, never changes the exit status)")
    parser.add_argument("--schema", action="store_true",
                        help="also report how the errata rows compare to schema/errata.schema.json"
                             " (report only: never changes the exit status, never edits a row)")
    args = parser.parse_args()

    errata = load_jsonl("errata.jsonl", "errata_id", base_only=args.base_only, exclude=args.exclude_shard)

    if args.obligation:
        read_log = load_jsonl("read_log.jsonl", "read_id", base_only=args.base_only,
                              exclude=args.exclude_shard)
        report = obligation_report(errata, read_log, as_of=args.as_of)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=1))
        else:
            print_obligation_report(report)
        return 0
    if args.derived_status:
        report = status_derivation_report(errata)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=1))
        else:
            print_status_derivation(report)
        return 0
    if args.schema:
        report = schema_report(errata)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=1))
        else:
            print_schema_report(report)
        return 0
    fragments = load_jsonl("fragments.jsonl", "fragment_id", base_only=args.base_only, exclude=args.exclude_shard)
    materials = load_jsonl("materials.jsonl", "material_id", base_only=args.base_only, exclude=args.exclude_shard)

    results = []
    for record in sorted(errata, key=lambda r: r["errata_id"]):
        measured = run_check(record.get("check", {}), fragments, materials)
        agree: bool | None = None
        if measured["measurable"]:
            recorded = recorded_number(record.get("measured_now", ""))
            measured_str = str(measured["value"])
            if not recorded:
                agree = None
            else:
                # a fraction such as 4/32 is compared on its numerator: the
                # denominators come from different ledger sizes by design.
                agree = recorded.split("/")[0] == measured_str.split("/")[0]
        results.append({"errata": record, "measured": measured, "agree": agree})

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return 0

    print("=== 訂正録の再測定 — 訂正そのものを測る（採点ではありません） ===")
    scope = "base only（凍結ベース）" if args.base_only else "union（base + shards）"
    print(f"対象: state/errata.jsonl {len(errata)} 件 / state/fragments.jsonl {len(fragments)} 編"
          f" / materials {len(materials)} 件（{scope}）\n")
    for row in results:
        rec, mes, agree = row["errata"], row["measured"], row["agree"]
        if not mes["measurable"]:
            mark = "対象外"
        elif agree is None:
            mark = "記述的"
        else:
            mark = "再現" if agree else "不一致"
        subject = rec.get("fragment_id") or rec.get("subject_id") or "—"
        print(f"[{rec['errata_id']}] {subject}  verdict={rec['verdict']} / status={rec['status']} / 再測定={mark}")
        print(f"   主張 : {rec['claim']}")
        print(f"   記録 : {rec.get('measured_now','—')}")
        print(f"   今回 : {mes['value']}  ({mes['detail']})")
        if agree is None and mes["measurable"]:
            print("   ※ 記録が記述的なため、自動比較はしない（数値の一致は註を読んで確かめる）")
        print(f"   註   : {rec['note']}\n")

    open_count = sum(1 for r in errata if r["status"] == "open")
    contradicted = sum(1 for r in errata if r["verdict"] == "contradicted")
    agreeing = sum(1 for row in results if row["agree"] is True)
    disagreeing = sum(1 for row in results if row["agree"] is False)
    descriptive = sum(1 for row in results if row["agree"] is None and row["measured"]["measurable"])
    unmeasurable = sum(1 for row in results if not row["measured"]["measurable"])
    print("--- 集計 ---")
    print(f"  errata 総数 {len(errata)} / contradicted {contradicted} / open {open_count}")
    print(f"  再測定できたもの {agreeing + disagreeing} 件のうち、記録と一致 {agreeing} 件・不一致 {disagreeing} 件")
    print(f"  記述的で自動比較しないもの {descriptive} 件 / 手続き未記録で再実行しないもの {unmeasurable} 件")
    print("  この道具は本文を書き換えない。判定もしない。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
