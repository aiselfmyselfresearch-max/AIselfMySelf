import io
import json
import math
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
        # SESSION-20261113-2e9501 adds seven biology primary-source
        # collisions from ten further sources (three supports / four
        # narrows_scope, EVL-20261113-2a477e ... -7a6c37) and no new
        # hypotheses, taking the live total to 153 evaluations.  The seven
        # were chosen so that no verdict is unconditional support:
        # HYP-20261113-a35ee5 (83.48% before this session) gets no support at
        # all, because none of the ten sources measures a two-layer
        # judgement/transformation-class structure; the report discloses that
        # its rise to 84% is a reallocation of mass from the two hypotheses
        # that were narrowed, not fresh evidence for it.
        # PR #730 (SESSION-20261113-1a5bd2) adds four comparative biology
        # evaluations on top of PR #729's 153 (EVL-20261113-a68b44, -7176a6,
        # -ff21e1, -165ab3: one supports / three narrows_scope), taking the
        # live total to 157 without adding hypotheses. Its ten new biology
        # sources do not overlap PR #729's ten; all ten are partially_verified
        # (abstract/bibliography or an author review, no primary full text),
        # which readings/2026-11-13-what-decides-which-line-is-read.md discloses
        # and which limits what these four rows can be taken to prove.
        # SESSION-20261113-ef19c0 adds four biology-scoped evaluations
        # (EVL-20261113-7ddfcb, -346e22, -c49807, -7becc6; four
        # narrows_scope) and no new hypotheses, taking the live total to
        # 161. All four are fragment_thought_experiment: the biological
        # sources do not directly measure the archive's identity layers,
        # and the report (§11-2) records both Q-002 hypotheses as narrowed
        # rather than letting an analogy support one of them.
        # SESSION-20261113-e72e9a adds ten biology primary-source readings and
        # ten evaluations (EVL-20261113-5dcd06 ... -0efe65: six
        # narrows_scope / four supports), and
        # for the first time in this batch registers two child hypotheses:
        # HYP-20261113-20fa8c (refines be95bc) and HYP-20261113-ccc1d8
        # (splits a35ee5).  Both take a single parent, following the
        # 2026-11-13 measurement that dual-parent splits over-accumulate
        # boost transfer.  The count therefore moves from 20 to 22; the
        # evaluation bound stays a lower bound.
        # SESSION-20261113-910748 adds six biology evaluations from ten
        # further sources (EVL-20261113-88e210, -d441c6, -80e646, -1e7c10,
        # -155f42, -da1b05; five narrows_scope / one supports) and no new
        # hypotheses, taking the live total to 182. Narrowing both leading
        # Q-002 hypotheses at once moved mass to the refuted Gen-0 ones
        # (dc25dc 9.8% -> 25.3%, 3bfb7e 5.7% -> 14.8%); the dead-hypothesis
        # revival gate still reads 0 because these are narrows, not supports.
        # readings/2026-11-13-what-is-kept-when-the-carrier-dies.md §12-4
        # records that side effect and the first-draft error it exposed.
        # SESSION-20261113-a5bf3b closes the reading of ten biology sources
        # (materials MAT-20261113-82e46b..fe382d) with four evaluations
        # (EVL-20261113-800cad, -0e1b45, -177c8e, -e31f6e; all narrows_scope)
        # and one new hypothesis, HYP-20261113-17ea95 (lineage_op=refines,
        # parent HYP-20261113-34b501), taking the live total to 21.
        # EVL-20261113-177c8e first read as refutes_unconditioned on 34b501;
        # the revival gate rejected it because two earlier supports already
        # exist on that target, so the evaluation was rewritten as a narrow
        # plus a spawned successor. Without the successor, 34b501's
        # unconditioned form would still be standing after a source that
        # shows action changing without any change to the decision centre
        # (Hughes et al. 2011, brain and muscle uninvaded; the mandibular
        # muscle atrophies and the ant simply cannot open its jaw).
        # readings/2026-11-13-ten-biological-sources-on-substitution-and-holding.md
        # §追記の範囲と未決 records the rewrite and the reasoning openly.
        # origin/main added two hypotheses in shard 2026-11-13-b51b15accc7f
        # (HYP-20261113-20fa8c, HYP-20261113-ccc1d8, SESSION-20261113-3b32da1ac5fc)
        # before this branch merged, so the combined live total is 23.
        # SESSION-20261113-d8950c adds two scoped child hypotheses from ten
        # biology full-text readings (HYP-20261113-977052 refines ba8bff;
        # HYP-20261113-3a106a splits 20fa8c), taking the live total to 25.
        self.assertEqual(bs["total_hypotheses"], 25)
        # Evaluations are append-only; later inquiry sessions may add more.
        self.assertGreaterEqual(bs["total_evaluations"], 161)
        for qid in ("Q-001", "Q-002", "Q-003"):
            self.assertIn(qid, bs["questions"])
            q_state = bs["questions"][qid]
            # SESSION-20261113-b4b40c: comparative scope limitations brought
            # Q-002 Gen-1+ mass to 0.8962. A valid inquiry may reduce confidence
            # in later hypotheses; requiring >90% rewards a preferred outcome.
            # Test numerical invariants here, not the direction of the reading.
            self.assertGreaterEqual(q_state["kl_from_uniform_bits"], 0.0, qid)
            self.assertLessEqual(
                q_state["kl_from_uniform_bits"],
                math.log2(len(q_state["hypotheses"])) + 1e-4, qid,
            )
            for key in ("gen0_mass", "gen1_plus_mass"):
                self.assertGreaterEqual(q_state[key], 0.0, qid)
                self.assertLessEqual(q_state[key], 1.0, qid)
            # gen0_mass / gen1_plus_mass are computed as sums of posteriors
            # that were each already rounded to 4 dp, then rounded again.  With
            # twelve hypotheses on Q-003 the two rounded sums can therefore
            # miss 1.0 by one or two units in the last place.  This checks that
            # the split is normalised up to that rounding, not that a particular
            # generation should hold a particular share.
            n_hyp = len(q_state["hypotheses"])
            self.assertAlmostEqual(
                q_state["gen0_mass"] + q_state["gen1_plus_mass"],
                1.0, delta=5e-5 * (n_hyp + 1) + 1e-9, msg=qid,
            )
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
