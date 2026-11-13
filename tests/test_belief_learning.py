import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state
import date_axis
import inspect_inquiry
import learning_metrics
import ledger_io


class BeliefStateAndLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live_data = inspect_inquiry.load_all()

    def test_live_belief_posteriors_and_map_sync(self):
        bs = belief_state.compute_belief_state(self.live_data)
        # Live-ledger counts are pinned so ledger changes cannot pass unnoticed.
        # PR #719 (SESSION-20261113-aa926d) raised evaluations from 75 to 85.
        # SESSION-20261113-f556b8 adds six primary-source-collision evaluations
        # across Q-001..Q-003 (EVL-20261113-606754, -5acbff, -f50572,
        # -2c6d36, -17a2fd, -9e41a6), taking the live total to 91.
        # SESSION-20261113-6c8a47 adds nine evaluations from ten further
        # biology sources: three primary-source collisions and six fragment
        # thought experiments (EVL-20261113-f6a99f ... -06b38d), taking the
        # live total to 100.
        # SESSION-20261113-48efa5 adds six biology evaluations here
        # (one support / five narrows), taking the live total to 116.
        # The first draft of EVL-20261113-e7d58d read HYP-20261112-afd1a5
        # as an inheritance claim it is not, and its refutes_unconditioned
        # verdict tripped the dead-hypothesis revival gate; ERR-20261113-764a04
        # records the misreading and the verdict was changed to narrows_scope.
        # SESSION-20261113-1650a1 adds two scoped conditional child hypotheses
        # (HYP-20261113-ebd567, HYP-20261113-be95bc) and ten comparative
        # evaluations, taking the live totals to 20 hypotheses and 126
        # evaluations. PR #725 adds three biology-scoped evaluations
        # (EVL-20261113-9dfeb9, -584c93, -3675e0), bringing the live total to
        # 129 without adding hypotheses. SESSION-20261113-c801a5 and
        # SESSION-20261113-070329 add two scoped biology evaluations,
        # taking the total to 131 without adding hypotheses.
        # SESSION-20261113-0598a2 adds six primary-source collisions from ten
        # further biology sources (two supports / four narrows_scope,
        # EVL-20261113-c127ce ... -82fe40) and no new hypotheses, taking the
        # live total to 137 evaluations.
        # SESSION-20261113-2f7b6e adds nine biology evaluations here.
        # The first draft held seven (one support / one refutation / five
        # narrows; EVL-20261113-7d74b5, -60b755, -05b67c, -addf7c, -e35311,
        # -6becc2, -5b2bcb), all pointing the same way; two of the ten
        # materials (McGrath & Solter 1984, Balaban et al. 2004) had no
        # evaluation at all, and both readings argue the opposite direction.
        # That asymmetry pushed Q-002 below the kl_from_uniform and
        # gen1_plus_mass gates (0.255 / 0.844), which this test caught.
        # EVL-20261113-10b28f and -eb86cf record the two missing readings,
        # taking the live total to 146 without adding hypotheses.  Six of the
        # nine cite sources read only to abstract/secondary-quotation depth,
        # which is the classification problem recorded in ERR-20261113-2a392a;
        # ERR-20261113-5ac381 names this session's rows, and the report
        # discloses the weight rather than treating it as settled.
        self.assertEqual(bs["total_hypotheses"], 20)
        self.assertEqual(bs["total_evaluations"], 146)
        for qid in ("Q-001", "Q-002", "Q-003"):
            self.assertIn(qid, bs["questions"])
            q_state = bs["questions"][qid]
            self.assertGreater(q_state["kl_from_uniform_bits"], 0.4, qid)
            self.assertGreater(q_state["gen1_plus_mass"], 0.90, qid)
            self.assertIsNotNone(q_state["top_competing_pair"], qid)
            total_p = sum(row["posterior"] for row in q_state["hypotheses"])
            # Each posterior is rounded to 4 decimal places before it reaches
            # this list, so the sum of n hypotheses can drift by up to
            # n * 5e-5.  This checks that the distribution is normalised to the
            # rounding, not to an impossible exact 1.0.
            self.assertAlmostEqual(
                total_p, 1.0, delta=5e-5 * len(q_state["hypotheses"]) + 1e-9, msg=qid
            )

        # Errata flags propagate automatically onto Q-001 hypotheses citing corrected materials
        q1_by_id = {row["hypothesis_id"]: row for row in bs["questions"]["Q-001"]["hypotheses"]}
        self.assertTrue(q1_by_id["HYP-20261112-46456a"]["errata_flags"])
        self.assertTrue(q1_by_id["HYP-20261112-5dc940"]["errata_flags"])

        ok, msg = belief_state.check_belief_map(ROOT)
        self.assertTrue(ok, msg)

    def test_unverified_evaluations_keep_errata_flags_and_refutation(self):
        belief_data = belief_state.load_belief_ledgers(ROOT)
        bs = belief_state.compute_belief_state(belief_data)
        q2 = {h["hypothesis_id"]: h for h in bs["questions"]["Q-002"]["hypotheses"]}
        cases = (
            ("MAT-20261113-c03554", "EVL-20261113-cec5a8", "ERR-20261113-fc0a12", "HYP-20261112-afd1a5"),
            ("MAT-20261113-1695e0", "EVL-20261113-439690", "ERR-20261113-bad8ab", "HYP-20261112-16929d"),
        )
        for material_id, evaluation_id, errata_id, hypothesis_id in cases:
            with self.subTest(evaluation_id=evaluation_id):
                self.assertEqual(self.live_data["materials"][material_id]["verification"]["status"], "unverified")
                self.assertEqual(self.live_data["evaluations"][evaluation_id]["evidence_type"], "primary_source_collision")
                self.assertEqual(belief_data["errata"][errata_id]["subject_id"], evaluation_id)
                self.assertIn(errata_id, q2[hypothesis_id]["errata_flags"])
        q3 = {h["hypothesis_id"]: h for h in bs["questions"]["Q-003"]["hypotheses"]}
        self.assertEqual(q3["HYP-20261112-1273f1"]["effective_status"], "refuted")

    def test_role_allocation_ratios_are_balanced(self):
        counts = {"proposer": 0, "adversarial_tester": 0, "consolidator": 0}
        for i in range(400):
            role = belief_state.assign_session_role(seed=f"seed-{i}", question_summary=None)
            counts[role["role"]] += 1
        self.assertGreater(counts["adversarial_tester"], 160)
        self.assertLess(counts["adversarial_tester"], 240)
        self.assertGreater(counts["proposer"], 70)
        self.assertGreater(counts["consolidator"], 70)

    def test_live_learning_metrics_pass_all_gates(self):
        metrics = learning_metrics.compute_learning_metrics(root=ROOT)
        failures = learning_metrics.check_invariants(metrics)
        self.assertEqual(failures, [], f"Failed gates: {failures}")
        self.assertEqual(metrics["wiring_and_chronology"]["unregistered_report_paths"], [])
        self.assertEqual(metrics["wiring_and_chronology"]["forward_dated_shards"], [])
        self.assertEqual(metrics["dead_hypothesis_revivals"]["count"], 0)
        self.assertGreater(metrics["evaluation_discipline"]["non_confirming_ratio"], 0.25)

    def test_unconditioned_revival_detection(self):
        metrics = learning_metrics.compute_learning_metrics(root=ROOT)
        tampered = json.loads(json.dumps(metrics))
        tampered["dead_hypothesis_revivals"]["count"] = 1
        tampered["dead_hypothesis_revivals"]["events"] = [
            {"evaluation_id": "EVL-20261112-ffffff", "target_hypothesis_id": "HYP-20261112-406d11"}
        ]
        failures = learning_metrics.check_invariants(tampered)
        self.assertTrue(failures)

    def test_shard_aliases_and_forward_shard_gate(self):
        aliases_doc = json.loads((ROOT / "state" / "shard_aliases.json").read_text(encoding="utf-8"))
        aliases = aliases_doc["aliases"]
        self.assertEqual(len(aliases), 171)
        sample_old = next(iter(aliases.keys()))
        resolved = ledger_io.resolve_shard_alias(sample_old, root=ROOT)
        self.assertIsNotNone(resolved)
        self.assertTrue((ROOT / resolved["new_shard"]).is_file())
        self.assertEqual(date_axis.forward_dated_shards(ROOT), [])

    def test_packet_auto_core_focus_and_id_resolution(self):
        bs = belief_state.compute_belief_state(self.live_data)
        open_qids = sorted(
            qid for qid, q in self.live_data["questions"].items() if q.get("status", "open") == "open"
        )
        core_hits = 0
        for i in range(80):
            qid, _ = belief_state.select_auto_question_id(
                bs, open_qids, seed=f"pkt-seed-{i}"
            )
            if qid in ("Q-001", "Q-002", "Q-003"):
                core_hits += 1
        # Expect ~75% routing to Q-001..Q-003
        self.assertGreaterEqual(core_hits, 45)

        pkt_q2 = inspect_inquiry.build_context_packet(self.live_data, "Q-002", seed="fixed-a")
        pkt_q2_b = inspect_inquiry.build_context_packet(self.live_data, "Q-002", seed="fixed-b")
        self.assertIn("## 0.2 条件付き仮説分布ブリーフィング", pkt_q2)
        self.assertIn("HYP-20261112-16929d", pkt_q2)
        # §3 material ranking is deterministic and seed-invariant
        sec3_a = pkt_q2.split("## 3. 対話素材")[1].split("## 4. 先行する関連断片")[0]
        sec3_b = pkt_q2_b.split("## 3. 対話素材")[1].split("## 4. 先行する関連断片")[0]
        self.assertEqual(sec3_a, sec3_b)

        # --id supports HYP-*, EVL-*, ERR-*, readings/ path, and aliased shard path
        aliases_doc = json.loads((ROOT / "state" / "shard_aliases.json").read_text(encoding="utf-8"))
        sample_old = next(iter(aliases_doc["aliases"].keys()))
        sample_evl = next(iter(self.live_data["evaluations"].keys()))
        for query in (
            "HYP-20261112-16929d",
            sample_evl,
            "ERR-20261101-7224f4",
            "readings/2026-11-12-conditional-belief-learning-and-memory-rewiring.md",
            sample_old,
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = inspect_inquiry.print_record_detail(self.live_data, query)
            self.assertEqual(rc, 0, query)
            self.assertTrue(buf.getvalue().strip(), query)

    def test_validate_seed_rejects_malformed_hypothesis_and_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            shutil.copytree(ROOT / "schema", repo / "schema")
            shutil.copytree(
                ROOT / "tools",
                repo / "tools",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            state = repo / "state"
            state.mkdir(parents=True)
            (repo / "readings").mkdir()
            for _, (filename, _, _) in inspect_inquiry.COLLECTIONS.items():
                (state / filename).write_text("", encoding="utf-8")

            (state / "questions.jsonl").write_text(
                json.dumps({
                    "question_id": "Q-001",
                    "question": "人間とは何か？",
                    "status": "open",
                    "created_at": "2026-10-24",
                    "origin": {"kind": "human_seed", "detail": "d"},
                    "motif_ids": [],
                    "material_ids": [],
                    "previous_question_ids": [],
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (state / "sessions.jsonl").write_text(
                json.dumps({
                    "session_id": "SESSION-20261112-aaaaaa",
                    "started_at": "2026-11-12",
                    "human_direction": "test",
                    "question_ids": ["Q-001"],
                    "context_material_ids": [],
                    "produced_fragment_ids": [],
                    "new_question_ids": [],
                    "prompt_template": "prompts/start.md",
                    "notes": "test session notes",
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (state / "hypotheses.jsonl").write_text(
                json.dumps({
                    "hypothesis_id": "HYP-20261112-111111",
                    "question_ids": ["Q-001"],
                    "session_id": "SESSION-20261112-aaaaaa",
                    "created_at": "2026-11-12",
                    "title": "不正な系譜テスト仮説",
                    "proposition": "条件付きテスト命題であり十分な長さを持つ記述テキスト。",
                    "scope_conditions": ["変換クラスAの下でのみ成立する条件"],
                    "exclusion_clause": "一次資料Xにおいて反例Yが確認された場合には直ちに棄却される。",
                    "parent_hypothesis_ids": [],
                    "lineage_op": "refines",
                    "status": "active",
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            (state / "evaluations.jsonl").write_text(
                json.dumps({
                    "evaluation_id": "EVL-20261112-222222",
                    "session_id": "SESSION-20261112-aaaaaa",
                    "created_at": "2026-11-12",
                    "target_hypothesis_id": "HYP-20261112-111111",
                    "compared_against_hypothesis_ids": ["HYP-20261112-111111"],
                    "verdict": "supports",
                    "evidence_type": "reproducible_script",
                    "summary": "再現可能スクリプトなのにコマンドが欠落し自己比較している不正評価行。",
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(repo / "tools" / "validate_seed.py")],
                cwd=repo,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            combined = proc.stdout + proc.stderr
            self.assertIn("refines", combined)
            self.assertIn("compared_against_hypothesis_ids", combined)
            self.assertIn("reproducible_script", combined)


if __name__ == "__main__":
    unittest.main()
