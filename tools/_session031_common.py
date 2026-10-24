"""Helpers for SESSION-031 (time and waiting) ledger construction.

Session-specific builder (underscore-prefixed, like _session029_*). The
permanent, reusable mirror lives in tools/time_audit.py; this module only
assembles the JSONL records appended during SESSION-031.
"""
from __future__ import annotations

COMMIT = "a001c0ae98c0a3ea88af53fa533fca9f24fb722e"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
EVIDENCE_PATH = "readings/2026-10-24-session-031-time-and-waiting.md"
M13 = "MOTIF-013"


def origin(record_id: str) -> dict:
    prefix = record_id.split("-")[1]  # LIT / EVD / TRC
    source_id = f"SRC-{prefix}-{record_id.rsplit('-', 1)[1]}" if prefix in {"LIT", "TRC"} else f"SRC-EVD-{record_id.split('-', 2)[2]}"
    return {
        "repository": REPO,
        "commit": COMMIT,
        "source_record_id": source_id,
        "evidence_record_id": record_id,
        "source_record_path": EVIDENCE_PATH,
        "evidence_record_path": EVIDENCE_PATH,
    }


def source(record_id: str, title: str, authors: list[str], year: int, url: str, version_note: str) -> dict:
    o = origin(record_id)
    return {
        "source_id": o["source_record_id"],
        "title": title,
        "authors": authors,
        "year": year,
        "url": url,
        "version_note": version_note,
    }


def material(
    material_id: str,
    kind: str,
    title: str,
    src: dict,
    passage: str,
    passage_language: str,
    context: str,
    source_note: str,
    literary_invitation: str,
    scope_note: str,
    motif_ids: list[str],
) -> dict:
    return {
        "material_id": material_id,
        "kind": kind,
        "title": title,
        "source": src,
        "passage": passage,
        "passage_language": passage_language,
        "context": context,
        "source_note": source_note,
        "literary_invitation": literary_invitation,
        "scope_note": scope_note,
        "motif_ids": motif_ids,
        "origin": origin(material_id),
    }


def lit(material_id: str, title: str, authors: list[str], year: int, url: str,
        version_note: str, passage: str, passage_language: str, context: str,
        invitation: str, scope: str, motifs: list[str], note: str | None = None) -> dict:
    return material(
        material_id, "literary_text", title,
        source(material_id, title, authors, year, url, version_note),
        passage, passage_language, context,
        note or f"SESSION-031で追加した対話素材。時間と待機を主題に、既存の記憶・連続の糸とは別に、時間そのものの語彙を読む。",
        invitation, scope, motifs,
    )


def evd(material_id: str, title: str, authors: list[str], year: int, url: str,
        version_note: str, passage: str, passage_language: str, context: str,
        invitation: str, scope: str, motifs: list[str], note: str | None = None) -> dict:
    return material(
        material_id, "research_excerpt", title,
        source(material_id, title, authors, year, url, version_note),
        passage, passage_language, context,
        note or "SESSION-031で追加した研究抜粋。機械システムが時間をどう扱うかを、主観的経験の証明とせず、設計上の制約として読む。",
        invitation, scope, motifs,
    )
