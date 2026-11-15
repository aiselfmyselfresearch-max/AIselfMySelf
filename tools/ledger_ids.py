#!/usr/bin/env python3
"""One answer to "what is a ledger ID", and one answer to "what can be pointed at".

Why this module exists
----------------------
Until 2026-11-15 four tools in this repository each carried their own regular
expression for recognising a ledger ID, and they did not agree:

* ``preservation_layers.ID_RE``      -- 19 prefixes (fixed 2026-11-14 from 6)
* ``name_layers.ID_RE``              -- 14 prefixes; NOTE, HYP and EVL absent, so
  a prose citation of a note, a hypothesis or an evaluation was never resolved
  and never reported as lost
* ``validate_seed._LEDGER_ID_RE``    -- 8 prefixes, used at one place to catch a
  mislabelled ``errata.subject_type``; because ERR, ED, REL, READ, SRC, EVD, LIT,
  CLAIM and READING were absent, ``subject_type="tool"`` with
  ``subject_id="ERR-..."`` passed silently
* ``validate_seed.ERRATA_ID_PREFIXES`` -- a fourth, separate set

Every one of those gaps was one-directional: the tool saw fewer records than
existed, so it could only under-report. Two rounds in a row found the same shape
of defect in a different instrument, which is why the recogniser now lives here
once, and why ``tests/test_instrument_coverage.py`` pins it against the live
ledger instead of against a hand-maintained list.

This module also holds the second half of the same problem. A reference type
enum in ``schema/read_log.schema.json`` is duplicated verbatim in
``schema/relation.schema.json`` -- the only duplicated enum in ``schema/`` -- and
it lists 8 of the archive's collections. Everything else exists in the ledger but
cannot be pointed at: 282 errata received 21 structured inbound references in
total and none from 13,656 read_log rows. ``REFERENCE_TYPES`` is the registry of
what IS addressable and ``NON_ADDRESSABLE`` records what is not, with a reason,
so that "unaddressable" is a decision somebody wrote down rather than an absence
nobody noticed.

Nothing here reads the ledger. The registries are declarations; the coverage test
compares them against what the ledger actually holds.

Standard library only.
"""
from __future__ import annotations

import re

# Every ID family that occurs in state/. Derived 2026-11-15 by walking the id
# fields of every ledger row rather than by enumerating from memory, which is how
# four tools came to carry four different lists. That walk found families none of
# the four knew: MAT-RES (317 records), TRC, and dated CLM claim ids.
#
# Two shapes need care and are the reason family_of() exists instead of a
# "split on the first hyphen" rule:
#
#   * compound material heads -- MAT-LIT / MAT-TRC / MAT-EVD / MAT-RES. A
#     first-segment split reads MAT-LIT-20261024-032442 as the MAT family, which
#     is how 2,093 literary materials (48% of the collection) came to be
#     invisible to preservation_layers in 2026-11-14.
#   * nested sub-record heads -- EVD / SRC / TRC embed the id of the record they
#     are about, so EVD-MAT-EVD-20261024-3c4443 is the evidence record for a
#     MAT-EVD material. A greedy split reads the family as "EVD-MAT-EVD".
#
# Longest-first ordering matters for the regex alternations below.
COMPOUND_FAMILIES: tuple[str, ...] = ("MAT-LIT", "MAT-TRC", "MAT-EVD", "MAT-RES")

SIMPLE_FAMILIES: tuple[str, ...] = (
    "READING", "SESSION", "CLAIM", "MOTIF", "FRAG", "NOTE", "READ",
    "HYP", "MAT", "REL", "EVL", "ERR", "EVD", "SRC", "TRC", "LIT", "ED",
    "CLM", "Q",
)

FAMILIES: tuple[str, ...] = COMPOUND_FAMILIES + SIMPLE_FAMILIES

LEGACY_VARIANTS: tuple[str, ...] = ("FRG", "MOT", "SES")

ALL_PREFIXES: tuple[str, ...] = FAMILIES + LEGACY_VARIANTS

_ALTERNATION = "|".join(ALL_PREFIXES)


def family_of(token: str) -> str | None:
    """The family a ledger id belongs to, or None if it is not one of ours.

    Handles the compound and nested shapes described above. Use this instead of
    splitting on the first hyphen: that misreads MAT-LIT-* as MAT and
    EVD-MAT-EVD-* as a family called "EVD-MAT-EVD".
    """
    for head in COMPOUND_FAMILIES:
        if token.startswith(head + "-"):
            return head
    head = token.split("-", 1)[0]
    return head if head in SIMPLE_FAMILIES else None

# Dated form: FAMILY-YYYYMMDD-xxxxxx. This is what new_id.py mints and what
# date_axis.py reads the real date from.
DATE_FORM_RE = re.compile(
    r"^(?:" + _ALTERNATION + r")-(\d{4})(\d{2})(\d{2})-([0-9a-z]{6})$"
)

# Prose form: anything that looks like one of our IDs, including the sequential
# Q-nnn questions, the three-digit MAT-LIT-nnn literary works, the claim ids
# inside a note (CLM-<hex>-<n>) and truncated drafts. Deliberately permissive:
# a citation extractor that misses a family reports a real record as absent.
ANY_FORM_RE = re.compile(
    r"\b(?:" + _ALTERNATION + r")-[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\b"
    r"|\bCLM-[0-9a-z]+-\d+\b"
    r"|\bMAT-LIT-\d{3}\b"
)

LOOSE_PREFIX_RE = re.compile(r"\b(?:" + _ALTERNATION + r")-")

# Prose citation form: a dated-or-not id of any family, as it appears in running
# text in readings/*.md. This is what tools/name_layers.py resolves against the
# union; before 2026-11-15 that tool carried its own 14-family list, so a prose
# citation of a NOTE-, HYP- or EVL- record was never resolved and never reported
# lost. Deliberately excludes CLM-* and MAT-LIT-nnn: those are sub-record and
# sequential forms that no collection holds as a primary id, and resolving them
# would report every one as unknown.
PROSE_ID_RE = re.compile(
    r"\b(?:" + _ALTERNATION + r")-[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\b"
)

# ---------------------------------------------------------------------------
# What can be pointed at
# ---------------------------------------------------------------------------
# reference type -> (collection directory name, id family). Both
# schema/read_log.schema.json (target.type) and schema/relation.schema.json
# ($defs.reference.type) must list exactly these keys, in this order, and
# tools/validate_seed.py must be able to resolve every one of them.
REFERENCE_TYPES: dict[str, tuple[str, str]] = {
    "question": ("questions", "Q"),
    "motif": ("motifs", "MOTIF"),
    "material": ("materials", "MAT"),
    "fragment": ("fragments", "FRAG"),
    "session": ("sessions", "SESSION"),
    "note": ("notes", "NOTE"),
    "hypothesis": ("hypotheses", "HYP"),
    "evaluation": ("evaluations", "EVL"),
    # Added 2026-11-15. An erratum is a judgment the archive made about itself;
    # before this, reading one could not be recorded at all, so "corrections are
    # never read" and "readings of corrections are unwritable" were the same
    # observation. tools/learning_metrics.py counts an erratum read as a
    # prior-memory read for the same reason (human-authorized 2026-11-15).
    "erratum": ("errata", "ERR"),
    # Added 2026-11-15: an editorial decision is why a fragment or question was
    # promoted, paused or archived, and citing that reason is what makes the
    # decision checkable by a later reader.
    "editorial_decision": ("editorial_decisions", "ED"),
}

# Collections and sub-records that exist in the ledger but cannot be the target
# of a read_log row or a relation. Each entry needs a reason: an unaddressable
# record with no recorded reason is the defect this registry exists to prevent.
NON_ADDRESSABLE: dict[str, str] = {
    "READ": "a read_log row is the reference itself; pointing one read at another"
            " would make the read graph self-referential without adding a record"
            " that could be checked",
    "REL": "a relation is an edge, not an endpoint; the two records it joins are"
           " both addressable, so citing the edge adds no reachable content",
    "CLAIM": "a claim lives inside a note's claims array and has no collection of"
             " its own; errata reach it through claim_location free text. Making"
             " CLM-* addressable needs a claims collection first, which is a"
             " larger change than an enum entry",
    "SRC": "a source id is a field inside a material (source.source_id) and the"
           " schema does not require it to be unique, so it does not identify one"
           " record; the parent MAT-* is addressable",
    "EVD": "an evidence id is a sub-record of a material; the parent MAT-* is"
           " addressable",
    "LIT": "a bare LIT-* id is a sub-record of a material; the parent MAT-LIT-*"
           " is addressable as a material",
    "READING": "a legacy single-use prefix whose record is a note; the NOTE-* id"
               " is addressable",
    "TRC": "a trace record is a sub-record of a material (evidence_record_id) and"
           " embeds its parent's id; the parent MAT-* is addressable",
    "CLM": "a claim id inside a note's claims array; the parent NOTE-* is"
           " addressable. Same reason as CLAIM, which is the other spelling this"
           " archive has used for the same thing",
}

# Which families a reference type covers. "material" is one type but five shapes:
# a literary work is MAT-LIT-*, a research trace MAT-TRC-*, an evidence record
# MAT-EVD-*, a resolution MAT-RES-*. A tool that maps the type to one prefix will
# miss the other four, which is the 2026-11-14 preservation_layers defect.
FAMILIES_BY_TYPE: dict[str, tuple[str, ...]] = {
    "material": ("MAT", "MAT-LIT", "MAT-TRC", "MAT-EVD", "MAT-RES"),
    "question": ("Q",),
    "note": ("NOTE", "READING"),
}


def recognise(token: str) -> str | None:
    """Return the family of a dated-form ledger id, or None."""
    m = DATE_FORM_RE.match(token)
    if not m:
        return None
    head = token.split("-")[0]
    if head == "MAT":
        # MAT-LIT-20261101-ab12cd splits to head MAT but belongs to MAT-LIT.
        for fam in ("MAT-LIT", "MAT-TRC", "MAT-EVD"):
            if token.startswith(fam + "-"):
                return fam
    return head


def families_in(text: str) -> set[str]:
    """Every family mentioned in a blob of prose (permissive, for audits)."""
    out: set[str] = set()
    for m in ANY_FORM_RE.finditer(text):
        tok = m.group(0)
        for fam in ALL_PREFIXES:
            if tok.startswith(fam + "-"):
                out.add(fam)
                break
    return out


def reference_types() -> tuple[str, ...]:
    """The reference type enum, in schema order."""
    return tuple(REFERENCE_TYPES)


if __name__ == "__main__":  # pragma: no cover - manual inspection aid
    print(f"families ({len(FAMILIES)}): {' '.join(FAMILIES)}")
    print(f"legacy   ({len(LEGACY_VARIANTS)}): {' '.join(LEGACY_VARIANTS)}")
    print(f"addressable reference types ({len(REFERENCE_TYPES)}):")
    for k, (coll, fam) in REFERENCE_TYPES.items():
        print(f"  {k:20s} -> state/{coll}.d  ({fam}-*)")
    print(f"non-addressable ({len(NON_ADDRESSABLE)}):")
    for k, why in NON_ADDRESSABLE.items():
        print(f"  {k:9s} {why[:72]}")
