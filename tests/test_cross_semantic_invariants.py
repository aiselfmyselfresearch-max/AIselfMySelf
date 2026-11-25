from __future__ import annotations

import datetime
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import default_mode_probe  # noqa: E402
import self_model  # noqa: E402
import three_gates  # noqa: E402
import validate_seed  # noqa: E402


def _make_material(
    mid: str,
    *,
    kind: str = "research_excerpt",
    passage: str = "",
    context: str = "Primary context",
    status: str = "verified",
    depth: str | None = "full_text",
    quote_status: str | None = None,
    span_sha256: str | None = None,
    span_norm_chars: int | None = None,
) -> dict:
    ver: dict = {
        "status": status,
        "checked_at": "2026-11-26",
        "method": "Full text read directly",
    }
    if depth is not None:
        ver["depth"] = depth
    if quote_status is not None:
        ver["quote_status"] = quote_status
    if span_sha256 is not None:
        ver["span_sha256"] = span_sha256
    if span_norm_chars is not None:
        ver["span_norm_chars"] = span_norm_chars
    return {
        "material_id": mid,
        "kind": kind,
        "title": "Test Material",
        "source": {
            "source_id": f"SRC-{mid}",
            "title": "Test Source",
            "authors": ["Simon, H. A."],
            "year": 1956,
            "url": "https://example.org/paper",
            "version_note": "OA text",
        },
        "passage": passage,
        "passage_language": "en",
        "context": context,
        "source_note": "Testing span witness",
        "literary_invitation": "Boundary condition check",
        "scope_note": "Behavioral scope only",
        "motif_ids": [],
        "origin": {"created_at": "2026-11-26"},
        "verification": ver,
    }


class SpanWitnessInvariantTests(unittest.TestCase):
    SOURCE_HTML = (
        "<p>Organisms adapt well enough to <i>'satisfice'</i>; "
        "this intervening sentence explains environmental structure; "
        "they do not, in general, 'optimize.'</p>"
    )

    def test_verify_span_accepts_verbatim_with_html_and_ellipsis(self) -> None:
        passage = "Organisms adapt well enough to 'satisfice' ... they do not, in general, 'optimize.'"
        res = three_gates.verify_passage_against_source(
            passage, self.SOURCE_HTML, quote_status="verbatim"
        )
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["status"], "VERIFIED_SPAN")
        self.assertEqual(res["matched_segments"], 2)

        mat = _make_material(
            "MAT-20261126-aa11bb",
            passage=passage,
            quote_status="verbatim",
            span_sha256=res["span_sha256"],
            span_norm_chars=res["span_norm_chars"],
        )
        errors: list[str] = []
        checked, _ = validate_seed.check_material_span_witness(
            {mat["material_id"]: mat},
            errors,
            today=datetime.date(2026, 11, 26),
        )
        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_verify_span_rejects_confabulated_paraphrase_and_reversed_order(self) -> None:
        # One word altered from memory ("well enough" -> "sufficiently"), mimicking 5310bf
        confab = "Organisms adapt sufficiently to 'satisfice' ... they do not, in general, 'optimize.'"
        res = three_gates.verify_passage_against_source(
            confab, self.SOURCE_HTML, quote_status="verbatim"
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["status"], "CONFABULATION_MISMATCH")

        # Clauses present in source but quoted in reversed order
        reversed_q = "they do not, in general, 'optimize.' ... Organisms adapt well enough to 'satisfice'"
        res_rev = three_gates.verify_passage_against_source(
            reversed_q, self.SOURCE_HTML, quote_status="verbatim"
        )
        self.assertFalse(res_rev["ok"])
        self.assertEqual(res_rev["status"], "CONFABULATION_MISMATCH")

    def test_offline_ci_rejects_forged_sha256_and_tampered_passage(self) -> None:
        passage = "Organisms adapt well enough to 'satisfice'"
        res = three_gates.verify_passage_against_source(
            passage, self.SOURCE_HTML, quote_status="verbatim"
        )
        self.assertTrue(res["ok"])

        # Forged dummy 64-hex string that an LLM might emit without running --verify-span
        forged = _make_material(
            "MAT-20261126-ff0011",
            passage=passage,
            quote_status="verbatim",
            span_sha256="a" * 64,
            span_norm_chars=res["span_norm_chars"],
        )
        # Tampered passage after hashing
        tampered = _make_material(
            "MAT-20261126-ff0022",
            passage="Organisms adapt sufficiently to 'satisfice'",
            quote_status="verbatim",
            span_sha256=res["span_sha256"],
            span_norm_chars=res["span_norm_chars"],
        )
        errors: list[str] = []
        validate_seed.check_material_span_witness(
            {forged["material_id"]: forged, tampered["material_id"]: tampered},
            errors,
            today=datetime.date(2026, 11, 26),
        )
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("span witness mismatch" in e for e in errors), errors)

    def test_cross_semantic_contradictions_and_mixed_mode(self) -> None:
        inline_passage = (
            'Simon (1956) は "Organisms adapt well enough to satisfice" と述べ、'
            "最適化前提を退けた。"
        )
        mixed_res = three_gates.verify_passage_against_source(
            inline_passage, self.SOURCE_HTML, quote_status="mixed"
        )
        self.assertTrue(mixed_res["ok"], mixed_res)

        valid_mixed = _make_material(
            "MAT-20261126-cc0001",
            passage=inline_passage,
            quote_status="mixed",
            span_sha256=mixed_res["span_sha256"],
            span_norm_chars=mixed_res["span_norm_chars"],
        )
        valid_summary = _make_material(
            "MAT-20261126-cc0002",
            passage="【編者による要約】環境構造と満足化の関係を論じた。",
            quote_status="paraphrase_summary",
        )
        bad_metadata_verbatim = _make_material(
            "MAT-20261126-cc0003",
            passage="Organisms adapt well enough to satisfice",
            status="partially_verified",
            depth="metadata",
            quote_status="verbatim",
            span_sha256=three_gates.compute_passage_span_witness(
                "Organisms adapt well enough to satisfice", "verbatim"
            )["span_sha256"],
            span_norm_chars=three_gates.compute_passage_span_witness(
                "Organisms adapt well enough to satisfice", "verbatim"
            )["span_norm_chars"],
        )
        bad_unmarked_summary = _make_material(
            "MAT-20261126-cc0004",
            passage="Organisms adapt sufficiently to satisfice without optimizing.",
            context="Plain context without marker",
            quote_status="paraphrase_summary",
        )
        bad_summary_marked_verbatim = _make_material(
            "MAT-20261126-cc0005",
            passage="【編者による要約】Organisms adapt well enough to satisfice",
            quote_status="verbatim",
            span_sha256="b" * 64,
            span_norm_chars=40,
        )

        mats = {
            m["material_id"]: m
            for m in (
                valid_mixed,
                valid_summary,
                bad_metadata_verbatim,
                bad_unmarked_summary,
                bad_summary_marked_verbatim,
            )
        }
        errors: list[str] = []
        validate_seed.check_material_span_witness(
            mats, errors, today=datetime.date(2026, 11, 26)
        )
        joined = "\n".join(errors)
        self.assertNotIn("cc0001", joined)
        self.assertNotIn("cc0002", joined)
        self.assertIn("cc0003", joined)
        self.assertIn("cc0004", joined)
        self.assertIn("cc0005", joined)

    def test_date_gating_respects_pre_cutoff_and_shard_bounded_labels(self) -> None:
        pre_cutoff = _make_material(
            "MAT-20261125-legacy1",
            passage="Unwitnessed historical row",
        )
        forward_label_in_old_shard = _make_material(
            "MAT-20270315-legacy2",
            passage="Internal chronology label in old shard",
        )
        new_missing_qstat = _make_material(
            "MAT-20261126-newrow1",
            passage="New verified full_text row missing quote_status",
        )
        shard_map = {
            "MAT-20261125-legacy1": Path("state/materials.d/2026-11-25-000000000000.jsonl"),
            "MAT-20270315-legacy2": Path("state/materials.d/2026-11-10-000000000000.jsonl"),
            "MAT-20261126-newrow1": Path("state/materials.d/2026-11-26-123456abcdef.jsonl"),
        }
        errors: list[str] = []
        _checked, legacy_n = validate_seed.check_material_span_witness(
            {
                pre_cutoff["material_id"]: pre_cutoff,
                forward_label_in_old_shard["material_id"]: forward_label_in_old_shard,
                new_missing_qstat["material_id"]: new_missing_qstat,
            },
            errors,
            today=datetime.date(2030, 1, 1),
            shard_of=shard_map,
        )
        self.assertEqual(legacy_n, 2)
        self.assertEqual(len(errors), 1)
        self.assertIn("MAT-20261126-newrow1", errors[0])

    def test_cli_verify_span_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src_file = Path(tmp) / "source.html"
            src_file.write_text(self.SOURCE_HTML, encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                rc_ok = three_gates.main(
                    [
                        "--verify-span",
                        "--source-file",
                        str(src_file),
                        "--passage",
                        "Organisms adapt well enough to 'satisfice'",
                        "--json",
                    ]
                )
            self.assertEqual(rc_ok, 0)
            payload = json.loads(out.getvalue())
            self.assertTrue(payload["ok"])

            err = io.StringIO()
            with redirect_stderr(err):
                rc_bad = three_gates.main(
                    [
                        "--verify-span",
                        "--source-file",
                        str(src_file),
                        "--passage",
                        "Fabricated sentence absent from primary paper",
                    ]
                )
            self.assertEqual(rc_bad, 1)


class PredictionErrorAndSelfModelTests(unittest.TestCase):
    def _write_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )

    def _build_synthetic_archive(
        self,
        root: Path,
        *,
        zero_shift_tail: bool = False,
        nominal_stasis_tail: bool = False,
    ) -> None:
        questions = [
            {"question_id": qid, "title": f"Core {qid}", "status": "open"}
            for qid in ("Q-001", "Q-002", "Q-003")
        ]
        materials = [
            {
                "material_id": "MAT-20261120-000001",
                "kind": "research_excerpt",
                "title": "Verified Primary Paper",
                "verification": {"status": "verified", "depth": "full_text"},
            }
        ]
        hypotheses = [
            {
                "hypothesis_id": f"HYP-20261120-000{i}a",
                "title": f"Hypothesis A for Q-00{i}",
                "question_ids": [f"Q-00{i}"],
                "primary_question_id": f"Q-00{i}",
                "claim": "Claim A",
                "applicability_scope": "Scope A",
                "exclusion_clause": "Falsified if counterexample X holds",
                "status": "active",
                "proposed_in_session_id": "SESSION-20261120-000001",
                "supporting_material_ids": ["MAT-20261120-000001"],
                "counter_material_ids": [],
                "source_note_ids": [],
                "parent_hypothesis_ids": [],
            }
            for i in (1, 2, 3)
        ] + [
            {
                "hypothesis_id": f"HYP-20261120-000{i}b",
                "title": f"Hypothesis B for Q-00{i}",
                "question_ids": [f"Q-00{i}"],
                "primary_question_id": f"Q-00{i}",
                "claim": "Claim B",
                "applicability_scope": "Scope B",
                "exclusion_clause": "Falsified if counterexample Y holds",
                "status": "active",
                "proposed_in_session_id": "SESSION-20261120-000001",
                "supporting_material_ids": ["MAT-20261120-000001"],
                "counter_material_ids": [],
                "source_note_ids": [],
                "parent_hypothesis_ids": [],
            }
            for i in (1, 2, 3)
        ]

        if zero_shift_tail:
            # Add an unrelated non-core question Q-999 so EVL rows on Q-999 produce 0 shift on Q-001..Q-003
            questions.append({"question_id": "Q-999", "title": "Side Q", "status": "open"})
            hypotheses.append(
                {
                    "hypothesis_id": "HYP-20261120-side01",
                    "title": "Side hyp",
                    "question_ids": ["Q-999"],
                    "primary_question_id": "Q-999",
                    "claim": "Side",
                    "applicability_scope": "Side",
                    "exclusion_clause": "Falsified if Z",
                    "status": "active",
                    "proposed_in_session_id": "SESSION-20261120-000001",
                    "supporting_material_ids": [],
                    "counter_material_ids": [],
                    "source_note_ids": [],
                    "parent_hypothesis_ids": [],
                }
            )

        sessions = [
            {
                "session_id": f"SESSION-2026112{d}-00000{d}",
                "started_at": f"2026-11-2{d}",
                "assigned_role": "adversarial_tester",
                "belief_basis": "amortized",
                "offered_target_question_id": "Q-001",
                "question_ids": ["Q-001"],
                "session_type": "inquiry",
            }
            for d in (1, 2, 3, 4)
        ]
        evaluations = [
            {
                "evaluation_id": f"EVL-20261121-init0{i}",
                "session_id": "SESSION-20261121-000001",
                "target_hypothesis_id": f"HYP-20261120-000{i}a",
                "compared_against_hypothesis_ids": [f"HYP-20261120-000{i}b"],
                "verdict": "supports",
                "evidence_type": "primary_source_collision",
                "material_ids": ["MAT-20261120-000001"],
                "fragment_ids": [],
                "note_ids": [],
                "rationale": "Initial grounding",
                "passed_conditions": ["c1"],
                "failed_conditions": [],
                "spawned_hypothesis_ids": [],
                "created_at": "2026-11-21",
            }
            for i in (1, 2, 3)
        ] + [
            {
                "evaluation_id": f"EVL-20261121-initb{i}",
                "session_id": "SESSION-20261121-000001",
                "target_hypothesis_id": f"HYP-20261120-000{i}b",
                "compared_against_hypothesis_ids": [f"HYP-20261120-000{i}a"],
                "verdict": "supports",
                "evidence_type": "primary_source_collision",
                "material_ids": ["MAT-20261120-000001"],
                "fragment_ids": [],
                "note_ids": [],
                "rationale": "Initial rival grounding",
                "passed_conditions": ["c1"],
                "failed_conditions": [],
                "spawned_hypothesis_ids": [],
                "created_at": "2026-11-21",
            }
            for i in (1, 2, 3)
        ]

        for d in (2, 3, 4):
            sid = f"SESSION-2026112{d}-00000{d}"
            if zero_shift_tail:
                evaluations.append(
                    {
                        "evaluation_id": f"EVL-2026112{d}-side0{d}",
                        "session_id": sid,
                        "target_hypothesis_id": "HYP-20261120-side01",
                        "compared_against_hypothesis_ids": [],
                        "verdict": "inconclusive",
                        "evidence_type": "internal_ledger_audit",
                        "material_ids": [],
                        "fragment_ids": [],
                        "note_ids": [],
                        "rationale": "No core update",
                        "passed_conditions": [],
                        "failed_conditions": [],
                        "spawned_hypothesis_ids": [],
                        "created_at": f"2026-11-2{d}",
                    }
                )
            elif not nominal_stasis_tail:
                evaluations.append(
                    {
                        "evaluation_id": f"EVL-2026112{d}-core0{d}",
                        "session_id": sid,
                        "target_hypothesis_id": "HYP-20261120-0001a",
                        "compared_against_hypothesis_ids": ["HYP-20261120-0001b"],
                        "verdict": "narrows_scope" if d % 2 == 0 else "supports",
                        "evidence_type": "primary_source_collision",
                        "material_ids": ["MAT-20261120-000001"],
                        "fragment_ids": [],
                        "note_ids": [],
                        "rationale": "Core boundary collision",
                        "passed_conditions": [],
                        "failed_conditions": ["f1"] if d % 2 == 0 else [],
                        "spawned_hypothesis_ids": [],
                        "created_at": f"2026-11-2{d}",
                    }
                )

        self._write_jsonl(root / "state" / "questions.jsonl", questions)
        self._write_jsonl(root / "state" / "materials.jsonl", materials)
        self._write_jsonl(root / "state" / "fragments.jsonl", [])
        self._write_jsonl(root / "state" / "notes.jsonl", [])
        self._write_jsonl(root / "state" / "sessions.jsonl", sessions)
        self._write_jsonl(root / "state" / "hypotheses.jsonl", hypotheses)
        self._write_jsonl(root / "state" / "evaluations.jsonl", evaluations)

    def test_synthetic_green_red_and_amber_prediction_error_bands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_g:
            rg = Path(tmp_g)
            self._build_synthetic_archive(rg)
            rep_g = default_mode_probe.compute_prediction_error(rg, window_sessions=3)
            self.assertEqual(rep_g["band"], "green")
            self.assertEqual(default_mode_probe.validate_prediction_error_invariants(rep_g), [])
            self.assertEqual(
                rep_g["retrospective"]["latest_eval_session"]["frontier_alignment"],
                "exact_frontier_pair",
            )
            self.assertGreater(
                rep_g["prospective"]["core_pairs"]["Q-001"]["pred_dkl_amort_bits"],
                0.0,
            )

        with tempfile.TemporaryDirectory() as tmp_r:
            rr = Path(tmp_r)
            self._build_synthetic_archive(rr, zero_shift_tail=True)
            rep_r = default_mode_probe.compute_prediction_error(rr, window_sessions=3)
            self.assertEqual(rep_r["band"], "red")

        with tempfile.TemporaryDirectory() as tmp_a:
            ra = Path(tmp_a)
            self._build_synthetic_archive(ra, nominal_stasis_tail=True)
            rep_a = default_mode_probe.compute_prediction_error(ra, window_sessions=3)
            self.assertEqual(rep_a["band"], "amber")
            self.assertEqual(
                len(rep_a["retrospective"]["trailing_window"]["recent_nominal_stasis_sessions"]),
                3,
            )

    def test_self_model_validate_invariants_rejects_corrupted_section6(self) -> None:
        belief = self_model.load_belief_summary(ROOT)
        sess = self_model.load_current_session(ROOT)
        pe = self_model.load_prediction_error(ROOT)
        self.assertEqual(self_model.validate_invariants(belief, sess, pe), [])

        # Corrupt prospective pairs (drop Q-001 despite BELIEF_MAP having >=2 P_amort candidates)
        pe_missing_pair = json.loads(json.dumps(pe))
        pe_missing_pair["prospective"]["core_pairs"].pop("Q-001", None)
        errs1 = self_model.validate_invariants(belief, sess, pe_missing_pair)
        self.assertTrue(any("prospective.core_pairs is missing Q-001" in e for e in errs1), errs1)

        # Corrupt retrospective KL to negative
        pe_neg_kl = json.loads(json.dumps(pe))
        pe_neg_kl["retrospective"]["latest_eval_session"]["per_question"]["Q-001"]["dkl_amort_bits"] = -0.01
        errs2 = self_model.validate_invariants(belief, sess, pe_neg_kl)
        self.assertTrue(any("dkl_amort_bits" in e for e in errs2), errs2)

        # Live SELF_MODEL.md must no longer carry the stubbed placeholder
        sm_text = (ROOT / "SELF_MODEL.md").read_text(encoding="utf-8")
        self.assertNotIn("現在は準備中", sm_text)
        self.assertIn("予測誤差アラーム", sm_text)
        self.assertIn("次回検証の事前感度予測", sm_text)


if __name__ == "__main__":
    unittest.main()
