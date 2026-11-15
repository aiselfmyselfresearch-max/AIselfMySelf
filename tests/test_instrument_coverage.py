"""Coverage tests: does each instrument see as much as the ledger holds?

Why this file exists
--------------------
Three rounds in a row found the same shape of defect in a different instrument,
and every time the error was one-directional -- the instrument saw less than
existed, so it could only under-report what would have falsified a hypothesis:

* 2026-11-14  ``preservation_layers.ID_RE`` recognised 6 of the ledger's id
  families, so the layer-3 ratio a hypothesis exclusion clause names was reported
  as 0.26% when it was 0.59%.
* 2026-11-15  ``execution_path_probe.CHECKS`` omitted ``append_only_check``, one
  of the three checks its own docstring and its subject hypothesis both name, so
  limb (b) had been scored against two thirds of the named set. The same file
  pinned the dispersal seed to a literal, which made the largest execution-path
  parameter structurally invisible.
* 2026-11-15  the fix for the first defect was itself a hand enumeration, and it
  still omitted ``MAT-TRC`` -- 417 live records.

A hand-maintained list of what exists will drift from what exists. These tests
compare each instrument against the live ledger instead, so a new family, a new
collection or a newly named check breaks the build rather than silently narrowing
a measurement.

They assert COVERAGE, never a live count, a posterior or a direction. Nothing here
pins how many rows the ledger has, so writing to the ledger cannot break these
tests -- which is the mistake that cost three earlier sessions their test suite.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import execution_path_probe as probe  # noqa: E402
import inspect_inquiry  # noqa: E402
import ledger_ids  # noqa: E402
import name_layers  # noqa: E402
import preservation_layers  # noqa: E402
import size_budget  # noqa: E402
import validate_seed  # noqa: E402

ID_KEY = re.compile(r"(?:^|_)ids?$")

# The four optional receipt fields added to schema/session.schema.json on
# 2026-11-15. Optional, so the 828 rows written before that stay valid.
RECEIPT_FIELDS = (
    "dispersal_seed",
    "assigned_role",
    "offered_target_question_id",
    "offered_reference_mode",
)


def _walk_ids(node: object, key: str = "") -> Iterator[str]:
    """Yield every value stored under an id-shaped key, at any nesting depth.

    Depth matters: claim ids live inside a note's claims array, and evidence and
    source ids inside a material's sub-records. A top-level scan misses them, and
    a naive regex over raw text invents families out of substrings -- the first
    version of this test reported 'TRC-MAT' and 'EVD-EVD-MAT-EVD' as families,
    which are what a nested id looks like when you split it in the wrong place.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk_ids(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_ids(v, key)
    elif isinstance(node, str) and ID_KEY.search(key):
        yield node


def live_families() -> set[str]:
    """Every id family that actually occurs in an id field under state/."""
    out: set[str] = set()
    for path in list((ROOT / "state").glob("*.jsonl")) + list((ROOT / "state").glob("*.d/*.jsonl")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            for value in _walk_ids(row):
                fam = ledger_ids.family_of(value)
                if fam:
                    out.add(fam)
    return out


def synthetic(family: str) -> str:
    return f"{family}-20261101-ab12cd"


class CanonicalRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = live_families()

    def test_the_ledger_holds_ids_at_all(self):
        """Guard the guard: an empty scan would make every test below pass."""
        self.assertGreater(len(self.live), 10, f"scan found only {self.live}")

    def test_every_live_family_is_declared(self):
        """A family the registry does not know is a family no tool can see."""
        unknown = self.live - set(ledger_ids.ALL_PREFIXES)
        self.assertEqual(unknown, set(),
                         "state/ holds id families tools/ledger_ids.py does not declare")

    def test_no_declared_family_is_fictional(self):
        """The reverse direction. A family declared but never used would mean the
        registry had drifted the other way, which is also worth knowing -- but the
        test is that the family occurs SOMEWHERE under state/, not that it occurs
        in an id field, because a few families (CLAIM, READING) survive only in
        prose and in old rows. Legacy spellings are exempt by declaration."""
        declared = set(ledger_ids.FAMILIES)
        legacy = set(ledger_ids.LEGACY_VARIANTS)
        self.assertEqual(declared & legacy, set(), "a family cannot be both current and legacy")
        blob = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in list((ROOT / "state").glob("*.jsonl"))
            + list((ROOT / "state").glob("*.d/*.jsonl"))
        )
        for fam in sorted(declared - self.live):
            with self.subTest(family=fam):
                self.assertIn(fam + "-", blob,
                              f"{fam} is declared but occurs nowhere under state/")

    def test_family_of_handles_the_compound_and_nested_shapes(self):
        """The two shapes that a first-segment split misreads."""
        cases = {
            "MAT-LIT-20261024-032442": "MAT-LIT",
            "MAT-RES-20261024-71138a": "MAT-RES",
            "MAT-LIT-001": "MAT-LIT",
            "EVD-MAT-EVD-20261024-3c4443": "EVD",
            "TRC-MAT-20261024-3c4443": "TRC",
            "SRC-TRC-20261024-prayer": "SRC",
            "CLM-20261105-49c323-01": "CLM",
            "Q-001": "Q",
            "SESSION-20261115-7212fa": "SESSION",
            "not-an-id": None,
        }
        for token, want in cases.items():
            with self.subTest(token=token):
                self.assertEqual(ledger_ids.family_of(token), want)


class RecogniserAgreementTests(unittest.TestCase):
    """Four tools used to carry four different answers to 'what is a ledger id'.

    They now derive from one module. These tests fail if any of them narrows
    again, which is how MAT-TRC came to be missed by a fix that was itself a
    hand-written list.
    """

    @classmethod
    def setUpClass(cls):
        cls.live = live_families()

    def test_preservation_layers_recognises_every_live_family(self):
        for fam in sorted(self.live):
            with self.subTest(family=fam):
                self.assertTrue(preservation_layers.ID_RE.search(synthetic(fam)),
                                f"preservation_layers.ID_RE cannot see {fam}-* records")

    def test_preservation_layers_does_not_count_a_target_as_a_second_record(self):
        """The reason LIT stays out of the plain alternation: without the
        (?<!MAT-) lookbehind, a row repeating its own MAT-LIT-* target looks as
        though it named a second record (measured: 49 read_log notes)."""
        note = "read MAT-LIT-20261024-032442 again"
        self.assertEqual(len(preservation_layers.ID_RE.findall(note)), 1)

    def test_name_layers_prose_recogniser_covers_every_live_family(self):
        """name_layers resolves the ids that readings/*.md cite in running prose.
        Its own list omitted NOTE, HYP and EVL, so a citation of a note, a
        hypothesis or an evaluation was never resolved and never reported lost."""
        for fam in sorted(self.live):
            with self.subTest(family=fam):
                self.assertTrue(name_layers.ID_RE.search(synthetic(fam)),
                                f"name_layers.ID_RE cannot resolve a prose citation of {fam}-*")

    def test_validate_seed_mislabel_guard_covers_every_live_family(self):
        """_LEDGER_ID_RE catches an errata row that calls a ledger id a tool path.
        It listed eight families, so subject_type='tool' with an ERR- subject_id
        passed silently."""
        for fam in sorted(self.live):
            with self.subTest(family=fam):
                self.assertTrue(validate_seed._LEDGER_ID_RE.match(synthetic(fam)),
                                f"the mislabel guard cannot see {fam}-* as a ledger id")

    def test_the_recognisers_now_agree(self):
        """One question, one answer: all three see the same set of families."""
        seen = {}
        for name, test in (("preservation_layers", preservation_layers.ID_RE.search),
                           ("name_layers", name_layers.ID_RE.search),
                           ("validate_seed", validate_seed._LEDGER_ID_RE.match)):
            seen[name] = {f for f in self.live if test(synthetic(f))}
        first = next(iter(seen.values()))
        for name, fams in seen.items():
            with self.subTest(tool=name):
                self.assertEqual(fams, first, f"{name} disagrees with the others")


class ReferenceClosureTests(unittest.TestCase):
    """What can be pointed at, and whether that was decided or merely forgotten."""

    def test_the_duplicated_enum_is_identical_in_both_schemas(self):
        """schema/ has exactly one duplicated enum. Drift between the two copies is
        how a reference would resolve in one collection and not the other."""
        rl = json.loads((ROOT / "schema" / "read_log.schema.json").read_text(encoding="utf-8"))
        rel = json.loads((ROOT / "schema" / "relation.schema.json").read_text(encoding="utf-8"))
        a = rl["properties"]["target"]["properties"]["type"]["enum"]
        b = rel["$defs"]["reference"]["properties"]["type"]["enum"]
        self.assertEqual(a, b)

    def test_both_schemas_match_the_canonical_registry(self):
        rl = json.loads((ROOT / "schema" / "read_log.schema.json").read_text(encoding="utf-8"))
        enum = rl["properties"]["target"]["properties"]["type"]["enum"]
        self.assertEqual(list(enum), list(ledger_ids.reference_types()))

    def test_erratum_and_editorial_decision_are_addressable(self):
        """282 errata received 21 structured inbound references in total and none
        from 13,656 read_log rows, because no reference type named them. 'Errata
        are never read' and 'reading an erratum cannot be written down' were the
        same observation."""
        types = ledger_ids.reference_types()
        self.assertIn("erratum", types)
        self.assertIn("editorial_decision", types)

    def test_every_reference_type_resolves_to_a_collection_that_exists(self):
        """A reference type with no collection behind it is a check that fails on
        the first use, which is what would have happened had the enum been widened
        without widening validate_seed's endpoint map."""
        for rtype, (coll, _fam) in ledger_ids.REFERENCE_TYPES.items():
            with self.subTest(reference_type=rtype):
                base = ROOT / "state" / f"{coll}.jsonl"
                shard = ROOT / "state" / f"{coll}.d"
                self.assertTrue(base.is_file() or shard.is_dir(),
                                f"{rtype} -> state/{coll} does not exist")

    def test_validate_seed_can_resolve_every_reference_type(self):
        """The endpoint map is the other half of widening the enum."""
        src = (ROOT / "tools" / "validate_seed.py").read_text(encoding="utf-8")
        block = src.split("endpoint_collections = {", 1)[1].split("\n    }", 1)[0]
        for rtype in ledger_ids.reference_types():
            with self.subTest(reference_type=rtype):
                self.assertIn(f'"{rtype}":', block,
                              "validate_seed's endpoint_collections cannot resolve this type")

    def test_every_live_collection_is_addressable_or_has_a_recorded_reason(self):
        """The point of NON_ADDRESSABLE: unreachability must be something a person
        wrote down, not an absence nobody noticed."""
        addressable = {coll for coll, _ in ledger_ids.REFERENCE_TYPES.values()}
        for path in sorted((ROOT / "state").glob("*.d")):
            coll = path.name[:-2]
            if coll in ("quarantine",):
                continue
            with self.subTest(collection=coll):
                self.assertTrue(
                    coll in addressable or coll in ledger_ids.NON_ADDRESSABLE
                    or coll in ("read_log", "relations", "quarantine"),
                    f"state/{coll}.d is neither addressable nor listed with a reason",
                )
        for fam, reason in ledger_ids.NON_ADDRESSABLE.items():
            with self.subTest(family=fam):
                self.assertTrue(reason.strip(), f"{fam} is unaddressable with no reason recorded")


class ProbeSubjectTests(unittest.TestCase):
    """The defect that started this: an instrument that omits a member of the very
    set its hypothesis names can only under-report a refutation."""

    @classmethod
    def setUpClass(cls):
        cls.hyp = None
        for path in list((ROOT / "state" / "hypotheses.d").glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                if row.get("hypothesis_id") == probe.SUBJECT_HYPOTHESIS:
                    cls.hyp = row
        cls.named = {n for n, _, kind in probe.CHECKS if kind == "named_in_scope"}

    def test_the_probe_names_its_subject(self):
        self.assertIsNotNone(self.hyp, f"{probe.SUBJECT_HYPOTHESIS} not found in the ledger")

    def test_scope_named_checks_are_a_subset_of_the_checks_run(self):
        """Read the hypothesis's own scope_conditions, extract every tool it names,
        and require the probe to run it. This is the test that was missing when
        append_only_check was listed in the docstring and absent from CHECKS."""
        self.assertIsNotNone(self.hyp)
        text = " ".join(self.hyp.get("scope_conditions") or [])
        mentioned = re.findall(r"([a-z_]+\.py)(\s+--check-map)?", text)
        self.assertTrue(mentioned, "no check named in scope_conditions; test would be vacuous")
        signatures = {}
        for name, cmd, _kind in probe.CHECKS:
            base = Path(cmd[0]).name
            signatures[base] = name
            if "--check-map" in cmd:
                signatures[base + " --check-map"] = name
        for tool, flag in mentioned:
            key = tool + (" --check-map" if flag.strip() else "")
            with self.subTest(check=key):
                self.assertIn(key, signatures, f"{key} is named by the hypothesis but not in CHECKS")
                self.assertIn(signatures[key], self.named,
                              f"{key} is named by the hypothesis but not labelled named_in_scope")

    def test_the_seed_is_a_parameter_of_every_intervention(self):
        for name, fam, _fn, seed in probe.INTERVENTIONS:
            with self.subTest(intervention=name):
                self.assertTrue(seed, f"{name} carries no seed")
        self.assertEqual({f for _, f, _, _ in probe.INTERVENTIONS}, {"storage", "packet", "seed"})


class ReceiptTests(unittest.TestCase):
    """The assignment receipt: recording the treatment next to the outcome."""

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schema" / "session.schema.json").read_text(encoding="utf-8"))
        cls.data = inspect_inquiry.load_all()
        cls.receipt = inspect_inquiry.describe_assignment(cls.data, "auto", seed="36c0e21c")

    def test_the_schema_carries_the_receipt_fields(self):
        props = self.schema["properties"]
        for field in RECEIPT_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, props)

    def test_the_receipt_fields_are_optional(self):
        """828 rows were written before these fields existed; making them required
        would invalidate every one."""
        for field in RECEIPT_FIELDS:
            with self.subTest(field=field):
                self.assertNotIn(field, self.schema.get("required", []))

    def test_session_row_fields_are_exactly_the_schema_fields(self):
        self.assertEqual(set(self.receipt["session_row_fields"]), set(RECEIPT_FIELDS))

    def test_the_receipt_agrees_with_the_packet_it_describes(self):
        """The receipt must not become a second source of truth that drifts. Same
        seed, same ledger: the values it reports are the ones the packet prints."""
        packet = inspect_inquiry.build_context_packet(self.data, "auto", seed="36c0e21c")
        head = packet.splitlines()[0]
        m = re.search(r"対象：(\S+)\s*／\s*参考モード：(\S+)\s*／\s*シード：([^）\s]+)", head)
        self.assertIsNotNone(m, f"packet header changed shape: {head}")
        self.assertEqual(m.group(1), self.receipt["offered_target_question_id"])
        self.assertEqual(m.group(2), self.receipt["offered_reference_mode"])
        self.assertEqual(m.group(3), self.receipt["dispersal_seed"])
        self.assertIn(self.receipt["assigned_role_label"], packet)

    def test_assigned_role_is_one_of_the_three_the_archive_assigns(self):
        import belief_state
        self.assertEqual(set(self.schema["properties"]["assigned_role"]["enum"]),
                         set(belief_state.ROLE_LABELS_JA))
        self.assertIn(self.receipt["assigned_role"], belief_state.ROLE_LABELS_JA)

    def test_the_receipt_is_available_from_the_cli(self):
        p = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "inspect_inquiry.py"),
             "--assignment-json", "--seed", "36c0e21c"],
            capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        got = json.loads(p.stdout)
        self.assertEqual(got["session_row_fields"], self.receipt["session_row_fields"])


class BudgetRatchetTests(unittest.TestCase):
    def test_every_shard_collection_has_a_budget(self):
        budgeted = {b.rel_dir.rstrip("/") for b in size_budget.SHARD_BUDGETS}
        for path in sorted((ROOT / "state").glob("*.d")):
            with self.subTest(collection=path.name):
                self.assertIn(f"state/{path.name}", budgeted)

    def test_reclaim_candidates_reports_only_real_slack(self):
        for cand in size_budget.reclaim_candidates(ROOT):
            with self.subTest(collection=cand["rel_dir"]):
                self.assertEqual(cand["free_slots"], cand["soft_shards"] - cand["shards"])
                self.assertEqual(cand["could_lower_to"], cand["shards"] + 1)
                self.assertGreaterEqual(cand["free_slots"], size_budget.RECLAIM_SLACK)

    def test_reclaim_is_informational_and_never_fails(self):
        """A ratchet needs a way back down, but reclaiming is a judgement about
        headroom, so it must not turn a green gate red."""
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "size_budget.py"), "--reclaim"],
                           capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p.returncode, 0, p.stderr)
        p2 = subprocess.run([sys.executable, str(ROOT / "tools" / "size_budget.py"),
                             "--reclaim", "--json"], capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(p2.returncode, 0, p2.stderr)
        self.assertIsInstance(json.loads(p2.stdout), list)


if __name__ == "__main__":
    unittest.main()
