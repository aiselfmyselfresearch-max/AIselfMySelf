#!/usr/bin/env python3
"""Mechanism tests for ``tools/preservation_layers.py``.

Why this file exists
--------------------
``preservation_layers.py`` computes the quantity that ``HYP-20261113-17ea95``'s
own exclusion clause names first -- 「read_log の層3比率」.  On 2026-11-14 that
pattern was found to recognise six of the seventeen id-prefix families the
ledger actually uses, and none of the ``MAT-LIT-*`` literature ids (2,093 of
4,343 materials).  The error is one-directional: a prefix the recogniser does
not know can only turn a layer-3 row into a layer-2 row, so the census was
reporting **less than half** the re-executions it claims to count (35 rows,
0.26%, where the corrected recogniser finds 79 rows, 0.59%).

A hypothesis whose falsification depends on that number was therefore being
scored against an instrument that could only under-report the very thing that
would falsify it.

These tests assert the *mechanism*, not a count of the live ledger:

* every id family that resolves to a record under ``state/`` is recognised
  (a coverage property -- it fails loudly when a new collection appears, which
  is the point, because that is exactly how the defect arose);
* the specific families that were missed are now matched;
* layer 3 still requires a *second* record and a disagreement marker, so the
  wider recogniser cannot inflate the layer by matching a row's own target or
  by matching an id in an otherwise neutral note.

No test here asserts how many rows the live ledger has.  That mistake is
recorded three times in ``readings/2026-11-14-the-checks-guard-what-never-
reaches-the-reader.md`` §9-1 and is not repeated a fourth time.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import preservation_layers as PL  # noqa: E402

# Id families that were absent from the recogniser before the 2026-11-14
# correction.  Each one resolves to real records under state/.
PREVIOUSLY_MISSED = ("FRAG", "ERR", "REL", "READ", "MOTIF", "ED")

DATED_FORM = re.compile(r"^([A-Z]{2,8})-[0-9]{8}-[0-9a-z]{6}$")


def ledger_id_families() -> set[str]:
    """Prefixes of every dated id that appears as a whole value under state/."""
    families: set[str] = set()
    paths = list((ROOT / "state").glob("*.jsonl"))
    paths += [p for d in (ROOT / "state").glob("*.d") for p in d.glob("*.jsonl")]
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            stack = [row]
            while stack:
                value = stack.pop()
                if isinstance(value, dict):
                    stack.extend(value.values())
                elif isinstance(value, list):
                    stack.extend(value)
                elif isinstance(value, str):
                    m = DATED_FORM.match(value)
                    if m:
                        families.add(m.group(1))
    return families


def run_tool(rows: list[dict], loose: bool = False) -> dict:
    """Run the tool over a synthetic ledger and return its JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "state").mkdir()
        with (root / "state" / "read_log.jsonl").open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        cmd = [sys.executable, str(TOOLS / "preservation_layers.py"), "--json",
               "--root", str(root)]
        if loose:
            cmd.append("--loose")
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0, proc.stderr
        return json.loads(proc.stdout)


def row(read_id: str, note: str, reading: str = "interpreted",
        target_id: str = "MAT-20261101-aaaaaa") -> dict:
    return {
        "read_id": read_id,
        "session_id": "SESSION-20261114-aaaaaa",
        "target": {"type": "material", "id": target_id},
        "reading": reading,
        "note": note,
        "created_at": "2026-11-14",
    }


class TestIdRecogniserCoverage(unittest.TestCase):
    def test_every_ledger_id_family_is_recognised(self) -> None:
        """A family that resolves to records must not be invisible to layer 3.

        The assertion is on recognition, not on membership in ``ID_PREFIXES``:
        ``LIT`` is recognised through a dedicated guarded alternative because a
        bare ``LIT`` in the prefix set would also match the tail of every
        ``MAT-LIT-*`` id (see ``test_lit_guard_prevents_self_match``).
        """
        families = ledger_id_families()
        self.assertTrue(families, "no dated ids found under state/ -- test is vacuous")
        missing = []
        for family in sorted(families):
            token = f"{family}-20261101-ab12cd"
            if token not in PL.ID_RE.findall(f"先行判断 {token} は誤りだった"):
                missing.append(family)
        self.assertEqual(
            missing, [],
            "preservation_layers.ID_RE does not recognise these id families that "
            f"exist in the ledger: {missing}. A work row naming only such a record "
            "is counted as layer 2 no matter how clearly it re-executes a "
            "judgement, so the layer-3 census can only under-report. Recognise the "
            "family (in ID_PREFIXES, or by a guarded alternative).",
        )

    def test_lit_guard_prevents_self_match(self) -> None:
        """``LIT`` is a family, but ``MAT-LIT-*`` must not match twice.

        Without the negative lookbehind, a row whose note merely repeats its own
        ``MAT-LIT-*`` target yields a second token (``LIT-...``) that differs
        from the target string, so the row looks as though it named *another*
        record.  49 read_log notes contain that substring.
        """
        own = "MAT-LIT-20261101-a8dee4"
        found = PL.ID_RE.findall(f"{own} の選定は誤りだった")
        self.assertIn(own, found)
        self.assertNotIn("LIT-20261101-a8dee4", found)
        # a standalone LIT id is still recognised on its own
        self.assertIn("LIT-20261024-23f03e",
                      PL.ID_RE.findall("LIT-20261024-23f03e の記述は矛盾している"))

    def test_previously_missed_families_are_now_matched(self) -> None:
        for prefix in PREVIOUSLY_MISSED:
            token = f"{prefix}-20261101-ab12cd"
            with self.subTest(prefix=prefix):
                self.assertIn(token, PL.ID_RE.findall(f"先行判断 {token} を確認した"))

    def test_legacy_literature_ids_are_matched(self) -> None:
        """MAT-LIT-* is 2,093 of 4,343 materials and matches neither MAT- nor LIT-."""
        for token in ("MAT-LIT-001", "MAT-LIT-004", "MAT-LIT-20261024-032442",
                      "MAT-LIT-20261101-a8dee4"):
            with self.subTest(token=token):
                self.assertIn(token, PL.ID_RE.findall(f"{token} の選定理由を再確認"))

    def test_short_question_ids_still_matched(self) -> None:
        self.assertIn("Q-003", PL.ID_RE.findall("Q-003 の首位が入れ替わった"))

    def test_recogniser_does_not_match_prose(self) -> None:
        """Widening must not turn ordinary words into record references."""
        prose = "The EDITORIAL review noted that RELATIVE humidity was READILY " \
                "available, and that MOTIVATION and SESSIONS matter."
        self.assertEqual(PL.ID_RE.findall(prose), [])


class TestLayer3Mechanism(unittest.TestCase):
    def test_row_naming_only_a_fragment_is_layer3(self) -> None:
        """The regression: before the fix this row was counted as layer 2."""
        out = run_tool([row(
            "READ-20261114-aaaaaa",
            "先行レビューが対篇 FRAG-20261111-198cfb を選出した際に本篇を draft に "
            "残した理由（選出を前篇の否定と扱わない）を確認し、新しい反証がないため維持。",
            target_id="MAT-20261101-aaaaaa",
        )])
        self.assertEqual(out["layers"].get("3_reexecution", 0), 1)
        self.assertEqual(out["layers"].get("2_work", 0), 0)

    def test_row_naming_only_an_erratum_is_layer3(self) -> None:
        out = run_tool([row(
            "READ-20261114-bbbbbb",
            "source.url が別作品を指す誤りを ERR-20261028-38c72d に記録した。",
        )])
        self.assertEqual(out["layers"].get("3_reexecution", 0), 1)

    def test_own_target_does_not_make_layer3(self) -> None:
        """Naming the row's own target is not naming *another* judgement."""
        out = run_tool([row(
            "READ-20261114-cccccc",
            "MAT-20261101-aaaaaa の記述は誤りであり、矛盾が残る。",
            target_id="MAT-20261101-aaaaaa",
        )])
        self.assertEqual(out["layers"].get("3_reexecution", 0), 0)
        self.assertEqual(out["layers"].get("2_work", 0), 1)

    def test_other_record_without_disagreement_is_layer2(self) -> None:
        out = run_tool([row(
            "READ-20261114-dddddd",
            "NOTE-20261101-ab12cd の要約を併せて読んだ。",
        )])
        self.assertEqual(out["layers"].get("3_reexecution", 0), 0)
        self.assertEqual(out["layers"].get("2_work", 0), 1)

    def test_exposure_kind_is_never_layer3(self) -> None:
        out = run_tool([row(
            "READ-20261114-eeeeee",
            "ERR-20261101-ab12cd の誤りを指摘する記述に触れた。",
            reading="used_as_context",
        )])
        self.assertEqual(out["layers"].get("3_reexecution", 0), 0)
        self.assertEqual(out["layers"].get("1_exposure", 0), 1)

    def test_loose_and_strict_agree_on_the_wider_recogniser(self) -> None:
        """--loose must remain a superset of the strict default."""
        rows = [
            row("READ-20261114-f0f0f0",
                "FRAG-20261111-198cfb の選出は誤りだと異議を記録した。"),
            row("READ-20261114-f1f1f1",
                "MAT-20261101-aaaaaa を読んだ。"),
        ]
        strict = run_tool(rows)
        loose = run_tool(rows, loose=True)
        self.assertGreaterEqual(
            loose["layers"].get("3_reexecution", 0),
            strict["layers"].get("3_reexecution", 0),
        )
        self.assertEqual(strict["layers"].get("3_reexecution", 0), 1)


if __name__ == "__main__":
    unittest.main()
