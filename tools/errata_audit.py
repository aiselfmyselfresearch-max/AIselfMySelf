#!/usr/bin/env python3
"""Re-run the checks recorded in state/errata.jsonl (stdlib only).

This is not a grader. It recomputes what can be recomputed, prints the result
beside the recorded judgement, and leaves the fragments untouched. A mismatch
means the errata record and the current ledger disagree; it does not decide
which of them is right.

Usage:
  python3 tools/errata_audit.py
  python3 tools/errata_audit.py --json
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


def quotation_match(fragments: list[dict[str, Any]], materials: list[dict[str, Any]], min_len: int,
                     literary_min_len: int | None = None,
                     trace_min_len: int | None = None,
                     trace_scope: str = "any") -> dict[str, Any]:
    """Count 「」 quotations and check which of them reach a stored passage.

    Default behaviour (literary_min_len is None) uses one ruler for everything
    and takes the first matching material in file order. Passing
    literary_min_len splits the check in two: literature is matched at
    literary_min_len characters, the ledger's own project_trace records at
    trace_min_len, optionally only against the materials a fragment actually
    cites (trace_scope="own"). The split exists because MAT-TRC-004 was
    reconstructed with exactly such a split; see tools/reconstruct.py.
    """
    quotes: list[tuple[str, Optional[str], str]] = []
    for fragment in fragments:
        for quote in re.findall(r"「([^」]*)」", fragment["text"]):
            if len(quote) >= min_len:
                quotes.append((fragment["fragment_id"], fragment.get("material_ids"), quote))
    normalized = [(m["material_id"], normalize(m["passage"])) for m in materials]

    if literary_min_len is None:
        originals, trace, unmatched = [], [], 0
        for fragment_id, _cited, quote in quotes:
            key = normalize(quote)
            hit = next((mid for mid, passage in normalized if key and key in passage), None)
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
                f"（うち台帳自身の検死記録 {len(trace)}）→ 原典一致 {len(originals)} / 不一致 {unmatched}"
            ),
        }

    trace_min_len = min_len if trace_min_len is None else trace_min_len
    originals, trace, unmatched = [], [], 0
    for fragment_id, cited, quote in quotes:
        key = normalize(quote)
        if not key:
            unmatched += 1
            continue
        hits = [mid for mid, passage in normalized if key in passage]
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run the checks recorded in the errata ledger.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--base-only", action="store_true",
                        help="read only the frozen base files (the pre-SESSION-041 behaviour)")
    parser.add_argument("--exclude-shard", metavar="SUFFIX",
                        help="ignore shards whose filename contains SUFFIX")
    args = parser.parse_args()

    errata = load_jsonl("errata.jsonl", "errata_id", base_only=args.base_only, exclude=args.exclude_shard)
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
