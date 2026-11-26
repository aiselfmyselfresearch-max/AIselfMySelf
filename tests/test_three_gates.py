"""Unit and coverage tests for the Three-Gates architecture (2026-11-18).

Covers Gate 1 (closed-loop completion, temporal-window ensembles, non-fusing links),
Gate 2 (receiver-local inhibition, parallel intrusion control, ``P_gate``,
``suppress_retrieval``, cohort suppression), and Gate 3 (append-only material
verification overlays via ``editorial_decisions``, forward-dated PSC/dedup/lineage
write gates, pre-acquisition source checker, and DN-A/DN-B channel balance).

Never pins live ledger counts, so future append-only growth cannot break these tests.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _support  # noqa: E402

TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import associations  # noqa: E402
import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402
import ledger_io  # noqa: E402
import three_gates  # noqa: E402
import validate_seed  # noqa: E402


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")


class Gate1PatternCompletionAndLinkingTests(unittest.TestCase):
    def _loop_fixture(self) -> dict:
        read_log = {}
        idx = 0
        # Sessions S1, S2 co-read (A, B, C) -> true closed triad A-B-C-A.
        # Sessions S3, S4 co-read (B, D) only -> open chain A-B-D (missing A-D).
        # Sessions S5, S6 co-read (A, E) and (B, E) is absent -> open chain.
        plan = [
            ("SESSION-20261110-000001", [("material", "MAT-A"), ("material", "MAT-B"), ("material", "MAT-C")]),
            ("SESSION-20261110-000002", [("material", "MAT-A"), ("material", "MAT-B"), ("material", "MAT-C")]),
            ("SESSION-20261115-000003", [("material", "MAT-B"), ("material", "MAT-D")]),
            ("SESSION-20261115-000004", [("material", "MAT-B"), ("material", "MAT-D")]),
        ]
        for sid, targets in plan:
            for ttype, tid in targets:
                idx += 1
                rid = f"READ-{idx:03d}"
                read_log[rid] = {
                    "read_id": rid,
                    "session_id": sid,
                    "target": {"type": ttype, "id": tid},
                    "reading": "interpreted",
                    "note": "test",
                }
        materials = {
            m: {"material_id": m, "title": f"Title {m}", "verification": {"status": "verified"}}
            for m in ("MAT-A", "MAT-B", "MAT-C", "MAT-D")
        }
        sessions = {
            "SESSION-20261110-000001": {"session_id": "SESSION-20261110-000001", "created_at": "2026-11-10"},
            "SESSION-20261110-000002": {"session_id": "SESSION-20261110-000002", "created_at": "2026-11-11"},
            "SESSION-20261115-000003": {"session_id": "SESSION-20261115-000003", "created_at": "2026-11-15"},
            "SESSION-20261115-000004": {"session_id": "SESSION-20261115-000004", "created_at": "2026-11-18"},
        }
        return {
            "questions": {},
            "motifs": {"M-1": {"motif_id": "M-1"}},
            "materials": materials,
            "fragments": {},
            "relations": {},
            "sessions": sessions,
            "read_log": read_log,
            "editorial_decisions": {},
            "notes": {},
            "hypotheses": {},
            "evaluations": {},
            "errata": {},
        }

    def test_closed_loop_returns_triad_member_and_rejects_open_chain(self) -> None:
        data = self._loop_fixture()
        comps = associations.closed_loop_completions(data, ["MAT-A", "MAT-B"])
        self.assertEqual([c["target"]["id"] for c in comps], ["MAT-C"])
        self.assertEqual(comps[0]["closed_loops"], 1)
        # Unlinked cue pair MAT-A and MAT-D closes zero loops even though MAT-B touches both.
        unlinked = associations.closed_loop_completions(data, ["MAT-A", "MAT-D"])
        self.assertEqual(unlinked, [])
        summary = associations.closed_loop_summary(data)
        self.assertEqual(summary["closed_triads"], 1)
        self.assertEqual(summary["triads_with_unbridged_edge"], 1)

    def test_suppress_retrieval_excludes_item_until_withdrawn(self) -> None:
        data = self._loop_fixture()
        err = {
            "ERR-1": {
                "errata_id": "ERR-1",
                "subject_type": "material",
                "subject_id": "MAT-C",
                "claim": "misquoted number",
                "verdict": "contradicted",
                "status": "open",
                "weight_effect": "suppress_retrieval",
            }
        }
        self.assertEqual(associations.closed_loop_completions(data, ["MAT-A", "MAT-B"], errata=err), [])
        err["ERR-1"]["status"] = "withdrawn"
        restored = associations.closed_loop_completions(data, ["MAT-A", "MAT-B"], errata=err)
        self.assertEqual([c["target"]["id"] for c in restored], ["MAT-C"])

    def test_temporal_cohort_links_respects_day_window(self) -> None:
        data = self._loop_fixture()
        res = associations.temporal_cohort_links(data, window_days=1, min_shared=2)
        # S1 (11-10) and S2 (11-11) are 1 day apart and share 3 materials;
        # S3 (11-15) and S4 (11-18) are 3 days apart -> excluded.
        self.assertEqual(res["linked_session_pairs"], 1)
        pair = res["top_pairs"][0]
        self.assertEqual(pair["shared_count"], 3)
        self.assertEqual(pair["day_gap"], 1)

    def test_non_fusing_links_preserve_partner_hypothesis_and_material(self) -> None:
        data = self._loop_fixture()
        data["questions"] = {"Q-001": {"question_id": "Q-001", "status": "open"}}
        data["hypotheses"] = {
            "HYP-1": {"hypothesis_id": "HYP-1", "question_ids": ["Q-001"], "parent_hypothesis_ids": []},
            "HYP-2": {"hypothesis_id": "HYP-2", "question_ids": ["Q-001"], "parent_hypothesis_ids": []},
        }
        data["evaluations"] = {
            "EVL-1": {"evaluation_id": "EVL-1", "target_hypothesis_id": "HYP-1", "verdict": "refutes_unconditioned", "material_ids": ["MAT-A"]},
            "EVL-2": {"evaluation_id": "EVL-2", "target_hypothesis_id": "HYP-2", "verdict": "supports", "material_ids": ["MAT-A"]},
        }
        nf = associations.non_fusing_link_stats(data)
        self.assertEqual(nf["cross_hypothesis_share_pct"], 100.0)
        self.assertEqual(nf["non_shared_erasure_pct"], 100.0)
        inhib = associations.receiver_inhibition(data)
        self.assertLess(inhib[("hypothesis", "HYP-1")]["gaba_gain"], 0.2)
        self.assertNotIn(("hypothesis", "HYP-2"), inhib)
        self.assertNotIn(("material", "MAT-A"), inhib)
        self.assertNotIn(("question", "Q-001"), inhib)
        self.assertNotIn(("motif", "M-1"), inhib)


class Gate2ReceiverInhibitionAndGatedBeliefTests(unittest.TestCase):
    def test_parallel_intrusion_dampening_vs_unresolved_intrusion(self) -> None:
        data = {
            "questions": {"Q-002": {"question_id": "Q-002", "status": "open"}},
            "motifs": {"M-SELF": {"motif_id": "M-SELF"}},
            "materials": {},
            "fragments": {},
            "relations": {},
            "sessions": {},
            "editorial_decisions": {},
            "notes": {},
            "hypotheses": {
                "HYP-RESOLVED": {"hypothesis_id": "HYP-RESOLVED", "question_ids": ["Q-002"], "parent_hypothesis_ids": []},
                "HYP-INTRUDE": {"hypothesis_id": "HYP-INTRUDE", "question_ids": ["Q-002"], "parent_hypothesis_ids": []},
            },
            "evaluations": {
                f"EVL-N{i}": {
                    "evaluation_id": f"EVL-N{i}",
                    "target_hypothesis_id": "HYP-RESOLVED",
                    "verdict": "narrows_scope",
                }
                for i in range(5)
            },
            "read_log": {
                "R1": {"read_id": "R1", "session_id": "S1", "target": {"type": "hypothesis", "id": "HYP-RESOLVED"}, "reading": "contested"},
                "R2": {"read_id": "R2", "session_id": "S2", "target": {"type": "hypothesis", "id": "HYP-RESOLVED"}, "reading": "contested"},
                "R3": {"read_id": "R3", "session_id": "S1", "target": {"type": "hypothesis", "id": "HYP-INTRUDE"}, "reading": "contested"},
                "R4": {"read_id": "R4", "session_id": "S2", "target": {"type": "hypothesis", "id": "HYP-INTRUDE"}, "reading": "contested"},
                "R5": {"read_id": "R5", "session_id": "S2", "target": {"type": "motif", "id": "M-SELF"}, "reading": "contested"},
            },
            "errata": {},
        }
        raw = associations.activation(data)
        inh = associations.inhibited_activation(data)
        # Raw activation untouched.
        self.assertEqual(raw[("hypothesis", "HYP-RESOLVED")]["salience"], inh[("hypothesis", "HYP-RESOLVED")]["raw_salience"])
        # Resolved narrowed hypothesis dampened strongly; not marked unresolved_intrusion.
        res_entry = inh[("hypothesis", "HYP-RESOLVED")]
        self.assertLess(res_entry["gaba_gain"], 0.4)
        self.assertLess(res_entry["inhibited_salience"], res_entry["raw_salience"] * 0.4)
        self.assertFalse(res_entry["unresolved_intrusion"])
        # Unresolved contested hypothesis flagged for attention.
        intr_entry = inh[("hypothesis", "HYP-INTRUDE")]
        self.assertEqual(intr_entry["gaba_gain"], 1.0)
        self.assertTrue(intr_entry["unresolved_intrusion"])
        # Category motif never inhibited.
        self.assertEqual(inh[("motif", "M-SELF")]["gaba_gain"], 1.0)

    def test_p_gate_blocks_postdated_and_rival_fallback_and_weights_psc(self) -> None:
        data = {
            "questions": {"Q-001": {"question_id": "Q-001", "question": "人間とは何か", "status": "open"}},
            "materials": {
                "MAT-VER": {"material_id": "MAT-VER", "verification": {"status": "verified"}},
                "MAT-UNV": {"material_id": "MAT-UNV", "verification": {"status": "partially_verified"}},
            },
            "hypotheses": {
                "HYP-20261112-parent": {
                    "hypothesis_id": "HYP-20261112-parent",
                    "question_ids": ["Q-001"],
                    "session_id": "S0",
                    "title": "親",
                    "proposition": "P",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-12",
                },
                "HYP-20261118-child": {
                    "hypothesis_id": "HYP-20261118-child",
                    "question_ids": ["Q-001"],
                    "session_id": "S9",
                    "title": "後発子",
                    "proposition": "C",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "refines",
                    "parent_hypothesis_ids": ["HYP-20261112-parent"],
                    "status": "active",
                    "created_at": "2026-11-18",
                },
                "HYP-20261113-ver": {
                    "hypothesis_id": "HYP-20261113-ver",
                    "question_ids": ["Q-001"],
                    "session_id": "S1",
                    "title": "照合済対抗",
                    "proposition": "V",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-13",
                },
                "HYP-20261113-unv": {
                    "hypothesis_id": "HYP-20261113-unv",
                    "question_ids": ["Q-001"],
                    "session_id": "S1",
                    "title": "未照合対抗",
                    "proposition": "U",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-13",
                },
            },
            "evaluations": {
                # Four earlier narrowings of parent BEFORE child existed:
                **{
                    f"EVL-20261114-00000{i}": {
                        "evaluation_id": f"EVL-20261114-00000{i}",
                        "session_id": f"S{i+2}",
                        "target_hypothesis_id": "HYP-20261112-parent",
                        "compared_against_hypothesis_ids": ["HYP-20261113-ver"],
                        "verdict": "narrows_scope",
                        "evidence_type": "primary_source_collision",
                        "material_ids": ["MAT-VER"],
                        "created_at": "2026-11-14",
                    }
                    for i in range(4)
                },
                # One later narrowing naming child as rival without explicit spawned:
                "EVL-20261119-000099": {
                    "evaluation_id": "EVL-20261119-000099",
                    "session_id": "S10",
                    "target_hypothesis_id": "HYP-20261112-parent",
                    "compared_against_hypothesis_ids": ["HYP-20261118-child"],
                    "verdict": "narrows_scope",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-VER"],
                    "created_at": "2026-11-19",
                },
                # Identical cross-session PSC supports, differing only in material verification:
                "EVL-20261115-000010": {
                    "evaluation_id": "EVL-20261115-000010",
                    "session_id": "S7",
                    "target_hypothesis_id": "HYP-20261113-ver",
                    "compared_against_hypothesis_ids": ["HYP-20261112-parent"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-VER"],
                    "created_at": "2026-11-15",
                },
                "EVL-20261115-000011": {
                    "evaluation_id": "EVL-20261115-000011",
                    "session_id": "S7",
                    "target_hypothesis_id": "HYP-20261113-unv",
                    "compared_against_hypothesis_ids": ["HYP-20261112-parent"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-UNV"],
                    "created_at": "2026-11-15",
                },
                # Self-support on newborn child:
                "EVL-20261118-000020": {
                    "evaluation_id": "EVL-20261118-000020",
                    "session_id": "S9",
                    "target_hypothesis_id": "HYP-20261118-child",
                    "compared_against_hypothesis_ids": ["HYP-20261112-parent"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-VER"],
                    "created_at": "2026-11-18",
                },
            },
            "errata": {},
        }
        st = belief_state.compute_belief_state(data=data)
        by_id = {h["hypothesis_id"]: h for h in st["questions"]["Q-001"]["hypotheses"]}
        child = by_id["HYP-20261118-child"]
        ver = by_id["HYP-20261113-ver"]
        unv = by_id["HYP-20261113-unv"]
        parent = by_id["HYP-20261112-parent"]

        # Historical P gives child massive retroactive fallback lead; P_gate removes it.
        self.assertEqual(child["postdated_heir_transfers"], 4)
        self.assertEqual(child["rival_heir_transfers"], 1)
        self.assertGreater(child["posterior"], ver["posterior"])
        self.assertGreater(ver["gated_posterior"], child["gated_posterior"])
        # Verified PSC beats unverified PSC under P_gate while tying under historical P.
        self.assertEqual(ver["posterior"], unv["posterior"])
        self.assertGreater(ver["gated_posterior"], unv["gated_posterior"])
        # Parent with children + heavy narrowing is classified superseded_inhibited.
        self.assertEqual(parent["inhibition_state"], "superseded_inhibited")
        self.assertEqual(child["inhibition_state"], "self_only_provisional")

        # Iteration-order invariance of P_gate.
        rev_data = {**data, "evaluations": dict(reversed(list(data["evaluations"].items())))}
        st_rev = belief_state.compute_belief_state(data=rev_data)
        rev_by_id = {h["hypothesis_id"]: h for h in st_rev["questions"]["Q-001"]["hypotheses"]}
        for hid in by_id:
            self.assertEqual(by_id[hid]["gated_posterior"], rev_by_id[hid]["gated_posterior"])


class Gate3OverlayAndWriteGateTests(unittest.TestCase):
    def test_material_editorial_overlay_is_append_only_and_upgrades_psc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state"
            orig_mat = {
                "material_id": "MAT-20261117-aaa111",
                "kind": "research_excerpt",
                "title": "Primary Study",
                "source": {
                    "source_id": "SRC-TEST-001",
                    "title": "Primary Study",
                    "authors": ["A"],
                    "year": 2023,
                    "url": "https://doi.org/10.1038/s41593-023-01304-9",
                    "version_note": "published article",
                },
                "passage": "要約",
                "passage_language": "ja",
                "context": "背景",
                "source_note": "出典注記",
                "origin": {
                    "repository": "aiselfmyselfresearch-max/AIselfMySelf",
                    "commit": "0000000000000000000000000000000000000000",
                    "source_record_id": "SRC-TEST-001",
                    "evidence_record_id": "EVD-TEST-001",
                    "source_record_path": "state/materials.jsonl",
                    "evidence_record_path": "state/materials.jsonl",
                },
                "verification": {"status": "partially_verified"},
                "scope_note": "抄録のみ",
                "literary_invitation": "問い",
                "motif_ids": [],
            }
            _write_jsonl(state / "materials.jsonl", [orig_mat])
            raw_bytes_before = (state / "materials.jsonl").read_bytes()
            # Include an out-of-order supersedes chain to verify supersession rules.
            _write_jsonl(
                state / "editorial_decisions.jsonl",
                [
                    {
                        "decision_id": "ED-20261118-000002",
                        "session_id": "SESSION-20261118-000002",
                        "target": {"type": "material", "id": "MAT-20261117-aaa111"},
                        "status": "verified",
                        "verification_method": "PMC11304553 open-access full text verified directly",
                        "reason": "本文・方法・図表を全文照合したため昇格。",
                        "supersedes": ["ED-20261118-000001"],
                        "created_at": "2026-11-18T12:00:00Z",
                    },
                    {
                        "decision_id": "ED-20261118-000001",
                        "session_id": "SESSION-20261118-000001",
                        "target": {"type": "material", "id": "MAT-20261117-aaa111"},
                        "status": "unverified",
                        "reason": "初期仮判定。",
                        "created_at": "2026-11-18T11:00:00Z",
                    },
                ],
            )
            loaded, errs = ledger_io.load_collections(
                {"materials": (state / "materials.jsonl", "material_id")}, root=Path(tmp)
            )
            self.assertEqual(errs, [])
            # Base file on disk untouched byte-for-byte.
            self.assertEqual((state / "materials.jsonl").read_bytes(), raw_bytes_before)
            mat = loaded["materials"]["MAT-20261117-aaa111"]
            self.assertEqual(mat["verification"]["status"], "verified")
            self.assertIn("PMC11304553", mat["verification"]["method"])
            self.assertIn("ED-20261118-000002", mat["verification"]["note"])

            # Schema conformance of overlaid material record preserved.
            schema = json.loads((ROOT / "schema" / "material.schema.json").read_text(encoding="utf-8"))
            schema_errs: list[str] = []
            validate_seed.validate_value(mat, schema, schema, "materials:MAT-20261117-aaa111", schema_errs)
            self.assertEqual(schema_errs, [])

            # Forward-dated PSC row passes once overlaid to verified, fails if unverified.
            future = datetime.date(2026, 11, 20)
            evls = {
                "EVL-20261119-111111": {
                    "evaluation_id": "EVL-20261119-111111",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-20261117-aaa111"],
                }
            }
            gate_errs_unv: list[str] = []
            validate_seed.check_psc_verification_gate(
                evls, {"MAT-20261117-aaa111": orig_mat}, gate_errs_unv, today=future
            )
            self.assertEqual(len(gate_errs_unv), 1)
            gate_errs_ver: list[str] = []
            validate_seed.check_psc_verification_gate(evls, loaded["materials"], gate_errs_ver, today=future)
            self.assertEqual(gate_errs_ver, [])

    def test_check_source_title_index_guards_and_author_year(self) -> None:
        # docs/2026-11-26-check-source-title-blindspot-proposal.md, stage 1.
        def mat(mid, title, src_title, *, url="", authors=(), year=None, note="", kind="research_excerpt"):
            return {"material_id": mid, "kind": kind, "title": title, "verification": {"status": "partially_verified"},
                    "source": {"title": src_title, "url": url, "authors": list(authors), "year": year, "version_note": note}}

        materials = {m["material_id"]: m for m in (
            mat("MAT-20261106-aaaaaa", "新生児模倣の原論文と大規模追試",
                "Imitation of Facial and Manual Gestures by Human Neonates (Science 198, 75-78, 1977) ／ "
                "Comprehensive Longitudinal Study Challenges the Existence of Neonatal Imitation in Humans (Current Biology 26, 2016)",
                url="https://example.org/meltzoff1977.pdf", authors=["Andrew N. Meltzoff", "M. Keith Moore"], year=1977),
            mat("MAT-20261107-bbbbbb", "自己参照効果のメタ分析", "The self-reference effect in memory: a meta-analysis",
                note="Psychological Bulletin; doi:10.1037/0033-2909.121.3.371"),
            mat("MAT-20261108-cccccc", "詩篇23", "Psalm 23 (King James Version)", kind="literary_text"),
            mat("MAT-20261108-dddddd", "讃歌", "Rig-Veda, Book 10, Hymn CXXXV. Yama", kind="literary_text"),
            mat("MAT-20261109-eeeeee", "再現性", "Estimating the reproducibility of psychological science"),
        )}
        # The second work of a combined row is found through source.title (display title is Japanese).
        hit = three_gates.check_source(
            materials, title="Comprehensive longitudinal study challenges the existence of neonatal imitation in humans")
        self.assertEqual(hit["status"], "SIMILAR_TITLE")
        self.assertEqual(hit["similar_title_matches"][0]["material_id"], "MAT-20261106-aaaaaa")
        self.assertEqual(hit["similar_title_matches"][0]["matched_field"], "source.title")
        # Numeric locators (Arabic or Roman) keep chapters and hymns apart.
        self.assertEqual(three_gates.check_source(materials, title="Psalm 24 (King James Version)")["status"], "CLEAR")
        self.assertEqual(three_gates.check_source(materials, title="Psalm 23 (King James Version)")["status"], "SIMILAR_TITLE")
        self.assertEqual(three_gates.check_source(materials, title="Rig-Veda Book 10 Hymn XIV Yama")["status"], "CLEAR")
        # A comment on a paper is related, not the paper.
        com = three_gates.check_source(materials, title='Comment on "Estimating the reproducibility of psychological science"')
        self.assertEqual(com["status"], "RELATED")
        self.assertEqual(com["related_title_matches"][0]["material_id"], "MAT-20261109-eeeeee")
        # A DOI written only in version_note is reported separately and is not an identifier-gate hit.
        note = three_gates.check_source(materials, doi="10.1037/0033-2909.121.3.371")
        self.assertEqual(note["status"], "NOTE_IDENTIFIER")
        self.assertEqual(note["exact_identifier_matches"], [])
        # Author + year reach rows without a matching title; CLEAR carries the not-proof-of-novelty advisory.
        auth = three_gates.check_source(materials, author="Meltzoff", year=1977)
        self.assertEqual([m["material_id"] for m in auth["author_year_matches"]], ["MAT-20261106-aaaaaa"])
        self.assertEqual(three_gates.check_source(materials, author="Meltzoff", year=1990)["status"], "CLEAR")
        clear = three_gates.check_source(materials, title="An entirely unrelated monograph about tidal engineering")
        self.assertTrue(any("not proof" in a for a in clear["advisories"]))

    def test_source_recording_rules_and_duplicate_audit(self) -> None:
        today = datetime.date(2026, 11, 28)
        combined = "Imitation of Facial and Manual Gestures by Human Neonates ／ Comprehensive Longitudinal Study of Neonatal Imitation"
        rows = {
            "MAT-20261127-aaaaaa": {"kind": "research_excerpt", "source": {"title": combined, "url": "", "version_note": ""}},
            "MAT-20261127-bbbbbb": {"kind": "research_excerpt", "source": {"title": combined, "url": "", "version_note": "single-work: one title"}},
            "MAT-20261127-cccccc": {"kind": "research_excerpt", "source": {"title": "Vision and language navigation (VLN / Room-to-Room benchmark)", "url": "", "version_note": "doi:10.1000/xyz"}},
            "MAT-20261127-dddddd": {"kind": "literary_text", "source": {"title": "Mencius, Chapter 21 / Gaozi I 1-8 (James Legge translation)", "url": "", "version_note": ""}},
            "MAT-20261126-eeeeee": {"kind": "research_excerpt", "source": {"title": combined, "url": "", "version_note": ""}},
        }
        errs: list[str] = []
        adv: list[str] = []
        validate_seed.check_material_source_recording(rows, errs, adv, today=today)
        self.assertEqual(len(errs), 1)
        self.assertIn("MAT-20261127-aaaaaa", errs[0])
        self.assertEqual(len(adv), 1)
        self.assertIn("MAT-20261127-cccccc", adv[0])

        def mat(mid, src_title, url="", kind="research_excerpt"):
            return {"material_id": mid, "kind": kind, "title": "表示題", "source": {"title": src_title, "url": url}}

        mats = {m["material_id"]: m for m in (
            mat("MAT-20261110-aaaaaa", "How a Cockpit Remembers Its Speeds"),
            mat("MAT-20261120-bbbbbb", "How a cockpit remembers its speeds", "https://doi.org/10.1207/s15516709cog1903_1"),
            mat("MAT-20261111-cccccc", "The self-reference effect in memory: a meta-analysis", "https://doi.org/10.1037/0033-2909.121.3.371"),
            mat("MAT-20261121-dddddd", "The self-reference effect in memory: a meta-analysis", "https://doi.org/10.1037/0033-2909.121.371"),
            mat("MAT-20261112-eeeeee", "Hávamál, The Poetic Edda, Bellows translation", kind="literary_text"),
            mat("MAT-20261122-ffffff", "Hávamál, The Poetic Edda, Bellows translation", kind="literary_text"),
        )}
        audit = three_gates.source_duplicate_audit(mats, today=today)
        causes = {r["material_id"]: r["cause"] for r in audit["post_gate_duplicates"]}
        self.assertEqual(causes, {"MAT-20261120-bbbbbb": "earlier_row_has_no_identifier",
                                  "MAT-20261121-dddddd": "doi_disagreement"})
        self.assertEqual(len(audit["doi_conflict_clusters"]), 1)

    def test_duplicate_identifier_and_descendant_collision_gates(self) -> None:
        future = datetime.date(2026, 11, 20)
        materials = {
            "MAT-20261115-111111": {
                "material_id": "MAT-20261115-111111",
                "title": "Wimber 2015",
                "source": {"url": "https://doi.org/10.1038/ncomms8499"},
                "verification": {"status": "partially_verified"},
            },
            # Pre-cutoff duplicate stays exempt:
            "MAT-20261116-222222": {
                "material_id": "MAT-20261116-222222",
                "title": "Wimber duplicate old",
                "source": {"url": "https://doi.org/10.1038/NCOMMS8499/"},
            },
            # Post-cutoff duplicate is caught:
            "MAT-20261119-333333": {
                "material_id": "MAT-20261119-333333",
                "title": "Wimber duplicate new",
                "source": {"url": "https://doi.org/10.1038/ncomms8499"},
            },
        }
        dup_errs: list[str] = []
        validate_seed.check_material_duplicate_identifiers(materials, dup_errs, today=future)
        self.assertEqual(len(dup_errs), 1)
        self.assertIn("MAT-20261119-333333", dup_errs[0])
        self.assertIn("MAT-20261115-111111", dup_errs[0])

        # Pre-acquisition checker flags exact DOI and emits upgrade template.
        chk = three_gates.check_source(materials, doi="10.1038/ncomms8499")
        self.assertEqual(chk["status"], "DUPLICATE_ID")
        self.assertIsNotNone(chk["editorial_upgrade_template"])
        clear = three_gates.check_source(materials, doi="10.9999/never-seen-xyz")
        self.assertEqual(clear["status"], "CLEAR")

        # Descendant-as-rival without explicit inheritance is rejected post-cutoff, allowed when explicit.
        hyps = {
            "HYP-P": {"hypothesis_id": "HYP-P", "parent_hypothesis_ids": []},
            "HYP-C": {"hypothesis_id": "HYP-C", "parent_hypothesis_ids": ["HYP-P"]},
        }
        evls = {
            "EVL-20261119-bad001": {
                "evaluation_id": "EVL-20261119-bad001",
                "target_hypothesis_id": "HYP-P",
                "verdict": "narrows_scope",
                "compared_against_hypothesis_ids": ["HYP-C"],
            },
            "EVL-20261119-ok0002": {
                "evaluation_id": "EVL-20261119-ok0002",
                "target_hypothesis_id": "HYP-P",
                "verdict": "narrows_scope",
                "compared_against_hypothesis_ids": ["HYP-C"],
                "scope_inherited_by_hypothesis_ids": ["HYP-C"],
            },
        }
        lin_errs: list[str] = []
        validate_seed.check_evaluation_descendant_collision(evls, hyps, lin_errs, today=future)
        self.assertEqual(len(lin_errs), 1)
        self.assertIn("EVL-20261119-bad001", lin_errs[0])

    def test_packet_section_three_demotes_suppressed_material_and_stays_seed_invariant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "readings").mkdir()
            data = {
                "questions": {
                    "Q-T": {
                        "question_id": "Q-T",
                        "question": "テスト問い",
                        "status": "open",
                        "origin": {"kind": "human_seed", "detail": "t"},
                        "previous_question_ids": [],
                        "motif_ids": [],
                        "material_ids": ["MAT-BAD", "MAT-GOOD"],
                    }
                },
                "materials": {
                    mid: {
                        "material_id": mid,
                        "kind": "research_excerpt",
                        "title": mid,
                        "source": {"authors": ["A"], "year": 2020, "url": f"https://example.org/{mid}"},
                        "passage": "x" * 200,
                        "verification": {"status": "verified"},
                        "scope_note": "s",
                        "literary_invitation": "i",
                        "motif_ids": [],
                    }
                    for mid in ("MAT-BAD", "MAT-GOOD")
                },
                "fragments": {},
                "motifs": {},
                "relations": {},
                "sessions": {},
                "editorial_decisions": {},
                "read_log": {},
            }
            errata = {
                "ERR-S1": {
                    "errata_id": "ERR-S1",
                    "subject_type": "material",
                    "subject_id": "MAT-BAD",
                    "claim": "bad",
                    "verdict": "contradicted",
                    "status": "open",
                    "weight_effect": "suppress_retrieval",
                }
            }
            order = inspect_inquiry._candidate_materials_for_question(data, "Q-T", errata=errata)
            self.assertEqual(order, ["MAT-GOOD", "MAT-BAD"])
            p1 = inspect_inquiry.build_context_packet(data, "Q-T", seed="11111111", errata=errata, root=root)
            p2 = inspect_inquiry.build_context_packet(data, "Q-T", seed="22222222", errata=errata, root=root)
            s1 = p1.split("## 3.")[1].split("## 4.")[0]
            s2 = p2.split("## 3.")[1].split("## 4.")[0]
            self.assertEqual(s1, s2)
            self.assertIn("suppress_retrieval", s1)

    def test_editorial_and_suppress_retrieval_validation_rules(self) -> None:
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            repo = _support.copy_repo(
                Path(tmp), include_readings=False, extra_exclude=("viewer",)
            )
            _write_jsonl(
                repo / "state" / "editorial_decisions.d" / "2026-11-18-zztest.jsonl",
                [
                    {
                        "decision_id": "ED-20261118-bad001",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "material", "id": "MAT-EVD-001"},
                        "status": "verified",
                        "reason": "method欠落",
                        "created_at": "2026-11-18T00:00:00Z",
                    },
                    {
                        "decision_id": "ED-20261118-bad002",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "fragment", "id": "FRAG-005"},
                        "status": "selected",
                        "verification_method": "not allowed on fragment",
                        "reason": "断片",
                        "created_at": "2026-11-18T00:00:00Z",
                    },
                    {
                        "decision_id": "ED-20261118-good01",
                        "session_id": "SESSION-20261024-9dd96f",
                        "target": {"type": "material", "id": "MAT-EVD-001"},
                        "status": "verified",
                        "verification_method": "DOI full text verified directly",
                        "reason": "正当な昇格",
                        "created_at": "2026-11-18T00:00:00Z",
                    },
                ],
            )
            _write_jsonl(
                repo / "state" / "errata.d" / "2026-11-18-zztest.jsonl",
                [
                    {
                        "errata_id": "ERR-9991",
                        "subject_type": "material",
                        "subject_id": "MAT-EVD-001",
                        "claim": "c",
                        "claim_location": "state/materials.jsonl",
                        "check": {"kind": "manual", "params": {"source": "DOI"}},
                        "verdict": "contradicted",
                        "status": "open",
                        "weight_effect": "suppress_retrieval",
                        "created_at": "2026-11-18",
                        "note": "ok",
                    },
                    {
                        "errata_id": "ERR-9992",
                        "subject_type": "material",
                        "subject_id": "MAT-EVD-001",
                        "claim": "c2",
                        "claim_location": "state/materials.jsonl",
                        "check": {"kind": "manual", "params": {"source": "DOI"}},
                        "verdict": "holds",
                        "status": "open",
                        "weight_effect": "suppress_retrieval",
                        "created_at": "2026-11-18",
                        "note": "bad verdict",
                    },
                    {
                        "errata_id": "ERR-9993",
                        "subject_type": "session",
                        "subject_id": "SESSION-20261024-9dd96f",
                        "claim": "c3",
                        "claim_location": "state/sessions.jsonl",
                        "check": {"kind": "manual", "params": {"source": "ledger"}},
                        "verdict": "contradicted",
                        "status": "open",
                        "weight_effect": "suppress_retrieval",
                        "created_at": "2026-11-18",
                        "note": "bad subject type",
                    },
                ],
            )
            proc = subprocess.run(
                [sys.executable, "tools/validate_seed.py"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertNotEqual(proc.returncode, 0)
            out = proc.stdout + proc.stderr
            self.assertIn("ED-20261118-bad001", out)
            self.assertIn("ED-20261118-bad002", out)
            self.assertNotIn("ED-20261118-good01", out)
            self.assertIn("ERR-9992", out)
            self.assertIn("ERR-9993", out)
            self.assertNotIn("ERR-9991", out)

    def test_orphan_over_narrowed_select_gated_pair_and_diagnostics(self) -> None:
        data = {
            "questions": {"Q-2": {"question_id": "Q-2", "question": "自己", "status": "open"}},
            "materials": {
                "MAT-P": {
                    "material_id": "MAT-P",
                    "title": "PMC Paper",
                    "source": {"url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9999999/"},
                    "verification": {"status": "partially_verified"},
                }
            },
            "hypotheses": {
                "HYP-ORPH": {
                    "hypothesis_id": "HYP-ORPH",
                    "question_ids": ["Q-2"],
                    "session_id": "S0",
                    "title": "子なし過限定",
                    "proposition": "O",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-10",
                },
                "HYP-A": {
                    "hypothesis_id": "HYP-A",
                    "question_ids": ["Q-2"],
                    "session_id": "S0",
                    "title": "対抗A",
                    "proposition": "A",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-10",
                },
                "HYP-B": {
                    "hypothesis_id": "HYP-B",
                    "question_ids": ["Q-2"],
                    "session_id": "S0",
                    "title": "対抗B",
                    "proposition": "B",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-10",
                },
            },
            "evaluations": {
                **{
                    f"EVL-20261111-00000{i}": {
                        "evaluation_id": f"EVL-20261111-00000{i}",
                        "session_id": f"S{i+1}",
                        "target_hypothesis_id": "HYP-ORPH",
                        "compared_against_hypothesis_ids": ["HYP-A"],
                        "verdict": "narrows_scope",
                        "evidence_type": "primary_source_collision",
                        "material_ids": ["MAT-P"],
                        "created_at": "2026-11-11",
                    }
                    for i in range(4)
                },
                "EVL-20261112-000010": {
                    "evaluation_id": "EVL-20261112-000010",
                    "session_id": "S6",
                    "target_hypothesis_id": "HYP-A",
                    "compared_against_hypothesis_ids": ["HYP-B"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-P"],
                    "created_at": "2026-11-12",
                },
                "EVL-20261112-000011": {
                    "evaluation_id": "EVL-20261112-000011",
                    "session_id": "S7",
                    "target_hypothesis_id": "HYP-B",
                    "compared_against_hypothesis_ids": ["HYP-A"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-P"],
                    "created_at": "2026-11-12",
                },
            },
            "errata": {},
            "sessions": {
                "SESSION-20261111-000001": {"session_id": "SESSION-20261111-000001", "created_at": "2026-11-11"},
                "SESSION-20261112-000002": {"session_id": "SESSION-20261112-000002", "created_at": "2026-11-12"},
            },
            "read_log": {
                "RL-1": {"read_id": "RL-1", "session_id": "SESSION-20261111-000001", "target": {"type": "material", "id": "MAT-P"}, "reading": "interpreted"},
                "RL-2": {"read_id": "RL-2", "session_id": "SESSION-20261112-000002", "target": {"type": "note", "id": "NOTE-1"}, "reading": "interpreted", "in_reply_to": "SESSION-20261111-000001"},
            },
            "notes": {"NOTE-1": {"note_id": "NOTE-1", "in_reply_to": ["NOTE-0"]}},
            "fragments": {},
            "motifs": {},
            "relations": {},
            "editorial_decisions": {},
        }
        st = belief_state.compute_belief_state(data=data)
        q2 = st["questions"]["Q-2"]
        by_id = {h["hypothesis_id"]: h for h in q2["hypotheses"]}
        self.assertEqual(by_id["HYP-ORPH"]["inhibition_state"], "orphan_over_narrowed")
        pair = belief_state.select_gated_pair(st, data["evaluations"], "Q-2")
        self.assertIsNotNone(pair)
        self.assertEqual({pair["left_hypothesis_id"], pair["right_hypothesis_id"]}, {"HYP-A", "HYP-B"})

        upg = three_gates.upgrade_candidates(data, limit=5)
        self.assertEqual(upg["psc_cited_non_verified_materials"], 1)
        self.assertEqual(upg["top_candidates"][0]["material_id"], "MAT-P")
        self.assertEqual(upg["top_candidates"][0]["psc_citations"], 6)
        self.assertEqual(upg["top_candidates"][0]["psc_single_blocker_rows"], 6)

        dnb = three_gates.dn_channel_balance(data)
        self.assertEqual(dnb["all_time"]["active_sessions"], 2)
        self.assertEqual(dnb["all_time"]["dn_a_scene_reads"], 1)
        self.assertEqual(dnb["all_time"]["dn_b_state_reads"], 1)
        self.assertEqual(dnb["all_time"]["in_reply_to_rows"], 1)

        cohort = three_gates.cohort_suppression_audit(data, data["errata"])
        self.assertIn("narrows_scope", cohort["cohorts"])

    def test_live_three_gates_cli_and_gated_packet_policy(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "three_gates.py"), "--check"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        p_pkt = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "inspect_inquiry.py"),
                "--packet",
                "Q-002",
                "--pair-policy",
                "gated",
                "--seed",
                "4222e835",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(p_pkt.returncode, 0, p_pkt.stderr)
        self.assertIn("三門制御P_gate", p_pkt.stdout)
        self.assertIn("## 4.6 第一門：閉ループ補完候補", p_pkt.stdout)

        import threading
        import urllib.request
        import serve_viewer

        srv = serve_viewer.ReusableThreadingHTTPServer(("127.0.0.1", 0), serve_viewer.ArchiveRequestHandler)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/packet?question_id=Q-002&pair_policy=gated", timeout=30
            ) as resp:
                self.assertEqual(resp.status, 200)
                body = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(body["pair_policy"], "gated")
            self.assertIn("三門制御P_gate", body["packet"])
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/packet?question_id=Q-002&pair_policy=bogus", timeout=30
            ) as resp2:
                body2 = json.loads(resp2.read().decode("utf-8"))
            self.assertEqual(body2["pair_policy"], "eig")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_memory_temperature_tier0_candidates_and_shard_compaction(self) -> None:
        self.assertEqual(belief_state.SELF_SUPPORT_DEPTH1_GATED_DISCOUNT, 0.0)
        data = {
            "questions": {
                "Q-001": {
                    "question_id": "Q-001",
                    "question": "人間とは何か",
                    "status": "open",
                    "material_ids": [
                        "MAT-BASE-1",
                        "MAT-BASE-2",
                        "MAT-20261025-cold01",
                        "MAT-20261025-warm01",
                    ],
                }
            },
            "materials": {
                "MAT-BASE-1": {"material_id": "MAT-BASE-1", "verification": {"status": "verified"}},
                "MAT-BASE-2": {"material_id": "MAT-BASE-2", "verification": {"status": "verified"}},
                "MAT-20261025-warm01": {
                    "material_id": "MAT-20261025-warm01",
                    "kind": "philosophical_text",
                    "title": "Early warm unwired source",
                    "source": {"authors": ["Warm Author"], "year": 2005, "url": "https://example.org/warm"},
                    "passage": "Warm passage",
                    "verification": {"status": "verified"},
                    "scope_note": "scope",
                    "literary_invitation": "invite",
                    "motif_ids": ["M-01"],
                },
                "MAT-20261025-cold01": {
                    "material_id": "MAT-20261025-cold01",
                    "kind": "philosophical_text",
                    "title": "Early cold verbatim source",
                    "source": {"authors": ["Cold Author"], "year": 2001, "url": "https://example.org/cold"},
                    "passage": "Cold passage",
                    "verification": {"status": "partially_verified"},
                    "scope_note": "scope",
                    "literary_invitation": "invite",
                    "motif_ids": ["M-01"],
                },
            },
            "sessions": {
                "SESSION-A": {"session_id": "SESSION-A", "context_material_ids": ["MAT-20261025-warm01"]},
                "SESSION-B": {"session_id": "SESSION-B", "context_material_ids": []},
            },
            "notes": {},
            "hypotheses": {
                "HYP-20261110-root": {
                    "hypothesis_id": "HYP-20261110-root",
                    "question_ids": ["Q-001"],
                    "session_id": "SESSION-A",
                    "title": "Root",
                    "proposition": "P",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "root",
                    "parent_hypothesis_ids": [],
                    "status": "active",
                    "created_at": "2026-11-10",
                },
                "HYP-20261118-child": {
                    "hypothesis_id": "HYP-20261118-child",
                    "question_ids": ["Q-001"],
                    "session_id": "SESSION-B",
                    "title": "Child",
                    "proposition": "C",
                    "scope_conditions": ["c"],
                    "exclusion_clause": "e",
                    "lineage_op": "refines",
                    "parent_hypothesis_ids": ["HYP-20261110-root"],
                    "status": "active",
                    "created_at": "2026-11-18",
                },
            },
            "evaluations": {
                "EVL-20261118-self": {
                    "evaluation_id": "EVL-20261118-self",
                    "session_id": "SESSION-B",
                    "target_hypothesis_id": "HYP-20261118-child",
                    "compared_against_hypothesis_ids": ["HYP-20261110-root"],
                    "verdict": "supports",
                    "evidence_type": "primary_source_collision",
                    "material_ids": ["MAT-BASE-1"],
                    "created_at": "2026-11-18",
                }
            },
            "read_log": {
                "READ-20261025-w1": {
                    "read_id": "READ-20261025-w1",
                    "session_id": "SESSION-A",
                    "target": {"type": "material", "id": "MAT-20261025-warm01"},
                    "reading": "interpreted",
                    "note": "Initial birth read of warm material in SESSION-A.",
                    "created_at": "2026-10-25",
                },
                "READ-20261115-w2": {
                    "read_id": "READ-20261115-w2",
                    "session_id": "SESSION-B",
                    "target": {"type": "material", "id": "MAT-20261025-warm01"},
                    "reading": "reinterpreted",
                    "note": "Subsequent session re-read of warm material in SESSION-B.",
                    "created_at": "2026-11-15",
                },
            },
            "errata": {},
        }
        st = belief_state.compute_belief_state(data=data)
        qs = st["questions"]["Q-001"]
        self.assertIn("HYP-20261118-child", qs["awaiting_external_audit_ids"])
        by_id = {h["hypothesis_id"]: h for h in qs["hypotheses"]}
        # Under P_gate, depth>=1 same-session supports carries 0.0 log-odds delta.
        self.assertEqual(by_id["HYP-20261118-child"]["gated_log_odds"], 0.0)

        mt = three_gates.memory_temperature_and_gate_audit(data, limit=10)
        self.assertGreaterEqual(mt["temperature_tiers"].get("warm_unwired", 0), 1)
        self.assertGreaterEqual(mt["temperature_tiers"].get("cold_verbatim", 0), 1)
        cand_ids = [r["material_id"] for r in mt["top_tier0_candidates"]]
        self.assertIn("MAT-20261025-warm01", cand_ids)

        # In §3 candidate ordering, Warm (2+ read sessions, verified) precedes Cold verbatim.
        ordered_mids = inspect_inquiry._candidate_materials_for_question(data, "Q-001")
        self.assertLess(
            ordered_mids.index("MAT-20261025-warm01"),
            ordered_mids.index("MAT-20261025-cold01"),
        )

        # Verify order-preserving shard compaction in a temporary workspace.
        with tempfile.TemporaryDirectory() as tmp:
            troot = Path(tmp)
            sdir = troot / "state" / "materials.d"
            sdir.mkdir(parents=True)
            (troot / "readings").mkdir()
            s1 = sdir / "2026-11-12-aaaa01.jsonl"
            s2 = sdir / "2026-11-12-bbbb02.jsonl"
            s3 = sdir / "2026-11-12-cccc03.jsonl"
            s1.write_text('{"material_id": "MAT-1"}\n', encoding="utf-8")
            s2.write_text('{"material_id": "MAT-2"}\n', encoding="utf-8")
            s3.write_text('{"material_id": "MAT-3"}\n', encoding="utf-8")
            # Reference s3 in readings/ so only (s1, s2) is eligible for compaction.
            (troot / "readings" / "ref.md").write_text(
                "Mentions 2026-11-12-cccc03.jsonl explicitly.\n", encoding="utf-8"
            )
            dry = three_gates.compact_unreferenced_shards(troot, apply=False)
            self.assertEqual(dry["collections"]["materials"]["safe_disjoint_pairs_found"], 1)
            applied = three_gates.compact_unreferenced_shards(troot, apply=True)
            self.assertEqual(applied["collections"]["materials"]["merged_count"], 1)
            self.assertEqual(
                applied["collections"]["materials"]["union_sha256"],
                dry["collections"]["materials"]["union_sha256"],
            )
            self.assertTrue(s1.is_file())
            self.assertFalse(s2.is_file())
            self.assertTrue(s3.is_file())


if __name__ == "__main__":
    unittest.main()
