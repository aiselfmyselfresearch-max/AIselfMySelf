#!/usr/bin/env python3
"""Tests for Three-Tier Memory (L0/L1/L2), Generational Amortization (P_amort), and Epoch Freeze."""

from __future__ import annotations

import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import belief_state  # noqa: E402
import inspect_inquiry  # noqa: E402
import memory_tiers  # noqa: E402
import self_model  # noqa: E402
import validate_seed  # noqa: E402


class MemoryTiersAndAmortizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = inspect_inquiry.load_all()
        cls.errata = inspect_inquiry.load_errata(ROOT)
        cls.bstate = belief_state.compute_belief_state(cls.data, root=ROOT)

    def test_generational_amortization_mass_conservation_and_active_recovery(self) -> None:
        for qid, q in self.bstate["questions"].items():
            hyps = q["hypotheses"]
            if not hyps:
                continue
            p_sum = sum(h["posterior"] for h in hyps)
            pg_sum = sum(h["gated_posterior"] for h in hyps)
            pa_sum = sum(h["amortized_posterior"] for h in hyps)
            pa_raw_sum = sum(h["amortized_raw_posterior"] for h in hyps)
            self.assertAlmostEqual(p_sum, 1.0, delta=0.005, msg=qid)
            self.assertAlmostEqual(pg_sum, 1.0, delta=0.005, msg=qid)
            self.assertAlmostEqual(pa_sum, 1.0, delta=0.005, msg=qid)
            self.assertAlmostEqual(pa_raw_sum, 1.0, delta=0.001, msg=qid)

        for core_q in ("Q-001", "Q-002", "Q-003"):
            hyps = self.bstate["questions"][core_q]["hypotheses"]
            active_amort = sum(
                h["amortized_posterior"] for h in hyps if h["effective_status"] == "active"
            )
            self.assertGreater(
                active_amort,
                0.95,
                f"{core_q} active amortized mass should exceed 95%, got {active_amort:.4f}",
            )
            pair = belief_state.select_amortized_pair(
                self.bstate, self.data["evaluations"], core_q
            )
            self.assertIsNotNone(pair)
            assert pair is not None
            self.assertNotEqual(pair["left_hypothesis_id"], pair["right_hypothesis_id"])

    def test_amortization_preserves_orphan_or_unverified_child_parent_mass(self) -> None:
        questions = {"Q-SYN": {"question_id": "Q-SYN", "question": "synthetic"}}
        hypotheses = {
            "HYP-20261120-aaaa01": {
                "hypothesis_id": "HYP-20261120-aaaa01",
                "question_ids": ["Q-SYN"],
                "title": "Narrowed parent whose only child is self-evaluated only",
                "proposition": "P1",
                "scope_conditions": ["S1"],
                "exclusion_clause": "E1",
                "status": "narrowed",
                "created_at": "2026-11-20",
                "session_id": "SESSION-20261120-000001",
            },
            "HYP-20261122-bbbb02": {
                "hypothesis_id": "HYP-20261122-bbbb02",
                "question_ids": ["Q-SYN"],
                "parent_hypothesis_ids": ["HYP-20261120-aaaa01"],
                "lineage_relation": "narrows_scope",
                "title": "Unverified child",
                "proposition": "P2",
                "scope_conditions": ["S2"],
                "exclusion_clause": "E2",
                "status": "active",
                "created_at": "2026-11-22",
                "session_id": "SESSION-20261122-000002",
            },
        }
        evaluations = {
            "EVL-20261121-000001": {
                "evaluation_id": "EVL-20261121-000001",
                "session_id": "SESSION-20261121-000003",
                "created_at": "2026-11-21",
                "target_hypothesis_id": "HYP-20261120-aaaa01",
                "compared_hypothesis_ids": [],
                "outcome": "narrows_scope",
                "test_modality": "thought_experiment",
                "evidence_ids": [{"type": "question", "id": "Q-SYN"}],
                "summary": "narrowed parent",
            },
            "EVL-20261122-000002": {
                "evaluation_id": "EVL-20261122-000002",
                "session_id": "SESSION-20261122-000002",
                "created_at": "2026-11-22",
                "target_hypothesis_id": "HYP-20261122-bbbb02",
                "compared_hypothesis_ids": ["HYP-20261120-aaaa01"],
                "outcome": "supports",
                "test_modality": "thought_experiment",
                "evidence_ids": [{"type": "question", "id": "Q-SYN"}],
                "summary": "same-session self evaluation only",
            },
        }
        syn_data = {
            "questions": questions,
            "hypotheses": hypotheses,
            "evaluations": evaluations,
            "materials": {},
            "sessions": {},
            "notes": {},
            "read_log": {},
            "fragments": {},
            "relations": {},
            "motifs": {},
            "editorial_decisions": {},
        }
        syn = belief_state.compute_belief_state(syn_data)
        by_id = {h["hypothesis_id"]: h for h in syn["questions"]["Q-SYN"]["hypotheses"]}
        self.assertTrue(by_id["HYP-20261122-bbbb02"]["self_evaluated_only"])
        # Because child is self_evaluated_only, parent must NOT amortize away its mass.
        self.assertAlmostEqual(
            by_id["HYP-20261120-aaaa01"]["amortized_posterior"],
            by_id["HYP-20261120-aaaa01"]["gated_posterior"],
            places=6,
        )

        # Once an independent session verifies the child, parent amortizes mass to child.
        evals2 = copy.deepcopy(evaluations)
        evals2["EVL-20261123-000004"] = {
            "evaluation_id": "EVL-20261123-000004",
            "session_id": "SESSION-20261123-000004",
            "created_at": "2026-11-23",
            "target_hypothesis_id": "HYP-20261122-bbbb02",
            "compared_hypothesis_ids": ["HYP-20261120-aaaa01"],
            "outcome": "supports",
            "test_modality": "reproducible_script",
            "evidence_ids": [{"type": "question", "id": "Q-SYN"}],
            "summary": "independent verification",
        }
        syn_data2 = dict(syn_data, evaluations=evals2)
        syn2 = belief_state.compute_belief_state(syn_data2)
        by_id2 = {h["hypothesis_id"]: h for h in syn2["questions"]["Q-SYN"]["hypotheses"]}
        self.assertFalse(by_id2["HYP-20261122-bbbb02"]["self_evaluated_only"])
        self.assertLess(
            by_id2["HYP-20261120-aaaa01"]["amortized_posterior"],
            by_id2["HYP-20261120-aaaa01"]["gated_posterior"],
        )
        self.assertGreater(
            by_id2["HYP-20261122-bbbb02"]["amortized_posterior"],
            by_id2["HYP-20261122-bbbb02"]["gated_posterior"],
        )

    def test_allocation_basis_amortized_and_self_model_sync(self) -> None:
        self.assertIn("amortized", belief_state.ALLOCATION_BASES)
        audit = belief_state.allocation_audit(ROOT, seed="672b9422")
        self.assertIn("amortized", audit["basis_leaders"])
        assign = inspect_inquiry.describe_assignment(
            self.data, "auto", seed="672b9422", errata=self.errata, root=ROOT, allocation_basis="amortized"
        )
        self.assertIn(assign["offered_target_question_id"], self.data["questions"])
        import subprocess
        res = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "self_model.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, res.stderr + res.stdout)

    def test_memory_tiers_classification_digests_and_cold_recall(self) -> None:
        summary = memory_tiers.compute_tier_summary(ROOT)
        self.assertGreater(summary["materials"]["hot"], 1000)
        self.assertGreater(summary["materials"]["cold"], 1000)
        self.assertEqual(
            summary["materials"]["total"],
            summary["materials"]["hot"]
            + summary["materials"]["cold"]
            + summary["materials"]["suppressed"],
        )

        # Explicit subsumed override on note row is honored
        notes_copy = {
            "N1": {
                "note_id": "N1",
                "memory_tier": "subsumed",
                "consolidated_into": "DIGEST-A-HUMAN-DEV",
            }
        }
        nt = memory_tiers.classify_notes(
            {"notes": notes_copy, "hypotheses": {}, "evaluations": {}, "read_log": {}, "errata": {}},
            root=ROOT,
        )
        self.assertEqual(nt["N1"]["tier"], "subsumed")
        self.assertEqual(nt["N1"]["consolidated_into"], "DIGEST-A-HUMAN-DEV")

        ok_digests, digest_msg = memory_tiers.check_digests(ROOT)
        self.assertTrue(ok_digests, digest_msg)

        recalled = memory_tiers.recall_cold_records(ROOT, "記憶", limit=5)
        self.assertGreater(recalled["cold_material_total_matches"], 0)
        self.assertLessEqual(len(recalled["materials"]), 5)

    def test_hot_only_packet_compression_and_section_accounting(self) -> None:
        std_pkt = inspect_inquiry.build_context_packet(
            self.data, "Q-002", seed="672b9422", errata=self.errata, root=ROOT
        )
        hot_pkt = inspect_inquiry.build_context_packet(
            self.data,
            "Q-002",
            seed="672b9422",
            errata=self.errata,
            root=ROOT,
            hot_only=True,
            pair_policy="amortized",
        )
        cold_included_pkt = inspect_inquiry.build_context_packet(
            self.data,
            "Q-002",
            seed="672b9422",
            errata=self.errata,
            root=ROOT,
            hot_only=True,
            include_cold=True,
            pair_policy="amortized",
        )
        std_bytes = len(std_pkt.encode("utf-8"))
        hot_bytes = len(hot_pkt.encode("utf-8"))
        self.assertIn("## 2.5 統合スキーマ・ダイジェスト（L1 圧縮記憶", hot_pkt)
        self.assertLess(hot_bytes, std_bytes * 0.70)
        self.assertGreater(len(cold_included_pkt.encode("utf-8")), hot_bytes)

        sections = inspect_inquiry.packet_sections(hot_pkt)
        self.assertEqual(sum(sections.values()), hot_bytes)

    def test_epoch_manifest_integrity_tamper_detection_and_active_epoch_validation(self) -> None:
        ok, msg = memory_tiers.check_epoch_manifest(ROOT)
        self.assertTrue(ok, msg)
        self.assertEqual(validate_seed.main(["--active-epoch-only"]), 0)

        with tempfile.TemporaryDirectory() as tmp:
            troot = Path(tmp)
            shutil.copytree(ROOT / "state", troot / "state")
            # Adding a new active-epoch shard (>= 2026-11-21) does NOT break frozen manifest
            new_active = troot / "state" / "notes.d" / "2026-11-25-ffffffffffff.jsonl"
            new_active.write_text('{"note_id":"NOTE-TEST"}\n', encoding="utf-8")
            ok_active, msg_active = memory_tiers.check_epoch_manifest(troot)
            self.assertTrue(ok_active, msg_active)

            # Mutating 1 byte of a frozen base file MUST fail check_epoch_manifest
            frozen_file = troot / "state" / "motifs.jsonl"
            frozen_file.write_bytes(frozen_file.read_bytes() + b"\n")
            ok_tamper, msg_tamper = memory_tiers.check_epoch_manifest(troot)
            self.assertFalse(ok_tamper)
            self.assertTrue(
                "mismatch" in msg_tamper.lower() or "fail" in msg_tamper.lower(),
                msg_tamper,
            )


if __name__ == "__main__":
    unittest.main()
