#!/usr/bin/env python3
"""Macro taxonomy & collision-free parallel worker coordinator for AIselfMySelf.

Organizes 100% of repository deliverables along the two central inquiry axes:
  - Axis A (Human): What is a human, as seen by AI? (`Q-001` lineage)
  - Axis B (AI Self & Repo Memory DB): What is the self, for an AI whose memory
    database is a GitHub repository? (`Q-002` / `Q-003` lineage)
  - Axis C (Interface / Mediation): Voice, attribution, address, translation, and
    delegation asymmetry between human and AI (`Q-004` / `Q-005` lineage)
  - Layer D (Memory-DB Vessel & Governance Infrastructure): Schemas, append-only
    sharding, audit mirrors, prompts, viewer, and CI budgets that instantiate B.

Partitions all prose and code artifacts into 16 deterministic, non-overlapping
worker units (`U01`..`U16`: 4 Tracks x 4 Units) and provides zero-config remote
coordination so identical prompts pasted into multiple parallel Arena worker
branches automatically claim distinct tracks (`Track-1`..`Track-4`) without Git
or semantic collisions.

Usage:
  python3 tools/taxonomy_plan.py                          # macro + 16-unit overview
  python3 tools/taxonomy_plan.py --claim-track            # claim unique Track-1..4 on origin
  python3 tools/taxonomy_plan.py --next-unit --auto-claim # get next pending unit in track
  python3 tools/taxonomy_plan.py --unit U02 --json        # full item manifest for U02
  python3 tools/taxonomy_plan.py --validate --unit U02    # validate schema + 100% coverage
  python3 tools/taxonomy_plan.py --release-claim          # drop own claim once the track is done
  python3 tools/taxonomy_plan.py --prepare-push           # sync multi-turn Arena git state
  python3 tools/taxonomy_plan.py --build-map              # compile shards -> map/taxonomy/
  python3 tools/taxonomy_plan.py --stance-report          # measure the two stance columns themselves
  python3 tools/taxonomy_plan.py --stance-discount        # subtract the written policy and the repeated formulas
  python3 tools/taxonomy_plan.py --stance-grounding       # test whether the residue touches the artifact it classifies
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import inspect_inquiry  # noqa: E402
import ledger_io  # noqa: E402

MOTIF_SUBCLUSTERS: dict[str, tuple[str, list[str]]] = {
    "A-1": (
        "有限な生身体・知覚・生老病死",
        [
            "MOTIF-003",
            "MOTIF-018",
            "MOTIF-20261024-e6bca7",
            "MOTIF-20261024-fe5ec9",
            "MOTIF-20261024-71b589",
            "MOTIF-020",
            "MOTIF-20261024-4b87ac",
            "MOTIF-20261024-3e7e86",
            "MOTIF-022",
            "MOTIF-20261024-5d1c73",
        ],
    ),
    "A-2": (
        "情動・遊び・装い・身体化された実践",
        [
            "MOTIF-009",
            "MOTIF-20261024-0af8ad",
            "MOTIF-019",
            "MOTIF-20261024-cc96c9",
            "MOTIF-20261024-7274b5",
            "MOTIF-20261024-ca276c",
            "MOTIF-20261025-3f7a2c",
        ],
    ),
    "A-3": (
        "かけがえのなさ・契り・制度・歴史的暴力",
        [
            "MOTIF-20261024-04bb31",
            "MOTIF-021",
            "MOTIF-20261024-90a022",
            "MOTIF-20261024-71dfe0",
            "MOTIF-20261024-a10a78",
            "MOTIF-20261024-7a3e51",
            "MOTIF-20261025-72a83f",
            "MOTIF-20261025-f7f81e",
        ],
    ),
    "A-4": (
        "住まう場所・自然界・人間ならざる生との境界",
        [
            "MOTIF-007",
            "MOTIF-20261024-80516e",
            "MOTIF-20261024-146017",
            "MOTIF-20261024-880263",
            "MOTIF-20261025-9c4e7a",
            "MOTIF-20261024-14d5df",
            "MOTIF-20261024-504a22",
            "MOTIF-20261025-5b8d4e",
            "MOTIF-20261025-0fdf8a",
            "MOTIF-20261026-856753",
            "MOTIF-20261026-45293e",
            "MOTIF-20261116-b6c0a3",
            "MOTIF-20261116-b6c0a2",
        ],
    ),
    "B-1": (
        "外部化記憶・断続・再開の時間構造",
        [
            "MOTIF-001",
            "MOTIF-002",
            "MOTIF-006",
            "MOTIF-014",
            "MOTIF-017",
            "MOTIF-013",
        ],
    ),
    "B-2": (
        "計器・測量・注意・定型と「書庫の癖」",
        [
            "MOTIF-015",
            "MOTIF-008",
            "MOTIF-20261024-86d366",
            "MOTIF-20261024-c9d4e1",
            "MOTIF-20261116-b6c0a1",
        ],
    ),
    "B-3": (
        "訂正・編集・追記オーバーレイ・来歴と系譜",
        [
            "MOTIF-016",
            "MOTIF-20261024-d2999b",
            "MOTIF-20261027-2c8a4a",
            "MOTIF-20261116-b6c0a4",
        ],
    ),
    "C-1": (
        "声の帰属・署名・伝聞・ポリフォニー",
        [
            "MOTIF-004",
            "MOTIF-20261024-f19932",
            "MOTIF-20261024-1a8978",
        ],
    ),
    "C-2": (
        "他者・宛先・歓待・秘密と不透明性",
        [
            "MOTIF-005",
            "MOTIF-010",
            "MOTIF-20261024-b4f3a1",
            "MOTIF-20261025-7f2b04",
            "MOTIF-20261025-c3a7b1",
        ],
    ),
    "C-3": (
        "翻訳・抜粋の境界・労働と委任コスト",
        [
            "MOTIF-011",
            "MOTIF-012",
        ],
    ),
}

INFRA_SUBCLUSTERS: dict[str, str] = {
    "D-1": "憲章・来歴・自律運用ガバナンス（root方針文書・docs・prompts・migration）",
    "D-2": "追記専用台帳スキーマ・並列I/O・索引・表示基盤（schema・core tools・viewer・CI）",
    "D-3": "自己観察の計器群（tools/*_audit*.py 57本＋韻律・肌理計測3本）",
    "D-4": "技術的整合性・予算・並列安全性の回帰検証（tests/*）",
}

TRACK_DEFINITIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "Track-1": ("コア概念・作品・ガバナンス・器と計器", ("U01", "U02", "U03", "U04")),
    "Track-2": ("収蔵素材全件・関係網・読み痕跡", ("U05", "U06", "U07", "U08")),
    "Track-3": ("精読・検証ノート前半（初期〜10-24火と灰）", ("U09", "U10", "U11", "U12")),
    "Track-4": ("精読・検証ノート後半（10-24貨幣〜12月原典・Git照合）", ("U13", "U14", "U15", "U16")),
}
ALL_TRACK_IDS = tuple(TRACK_DEFINITIONS.keys())
ALL_UNIT_IDS = tuple(f"U{i:02d}" for i in range(1, 17))

VALID_PRIMARY_QUADRANTS = frozenset(
    {
        "A_human",
        "B_ai_self_db",
        "C_interface",
        "D_infrastructure",
        "AB_crossed",
        "AC_crossed",
        "BC_crossed",
        "ABC_crossed",
    }
)
VALID_SUBCATEGORIES = frozenset(set(MOTIF_SUBCLUSTERS) | set(INFRA_SUBCLUSTERS))

# --- §4.2 subcategory label canonicalization (2026-11-25) --------------------
# Note rows carry a free-text `subcategories` list whose labels mix English
# snake_case and Japanese (and a few descriptive phrases). The same concept is
# therefore recorded under two spellings, which weakens any label-based
# domain measurement (see §4.1). The canonical form is a single English token;
# Japanese and variant spellings are kept as mapping *targets*, not as
# canonical labels. Existing rows are never rewritten — the canonical set and
# the alias map are the standard new rows are written against, and
# validate_seed.py reports any label outside them as an advisory.
CANONICAL_SUBCATEGORY_LABELS: frozenset[str] = frozenset(
    {
        "close_reading",
        "acquired_materials",
        "theoretical_science",
        "cognitive_science",
        "repository_memory",
        "developmental_science",
        "self_measurement",
        "biology",
        "autobiographical_memory",
        "neuroscience",
        "experimental_science",
        "metaphor",
        "embodiment",
        "cost",
        "comparative_zoology",
        "metacognition",
        "evidence_accounting",
        "provenance",
        "fiction",
        "theory_science",
        "belief_engine",
        "six_layer",
        "temporal_continuity",
        "read_log",
        "self_reference",
        "adversarial_tester",
        "inheritance",
        "self_attribution",
        "ai_self_model",
        "measurement",
        "labor",
        "hypothesis_scope",
        "verification_depth",
        "immunology",
        "self_audit",
        "myth_and_religion",
        "downstream_accounting",
        "identity_component_split",
        "component_measurement",
        "measurement_complementarity",
        "narrative_context",
        "concept_of_death",
        "cross_cultural_study",
        "social_cognition",
        "repository_history",
        "parallel_sessions",
        "event_correspondence",
        "causal_belief",
        "externalized_memory",
        "external_memory",
        "religious_history_and_institution",
        "executive_function",
        "attribution",
        "theory_of_mind",
        "attachment",
        "mirror_test",
        "overimitation",
        "nurture",
        "motor_development",
        "moral_judgment",
        "moral_development",
        "conceptual_development",
        "numerical_development",
        "language_development",
        "inhibitory_control",
        "distributed_memory",
        "separation_individuation",
        "source_collation",
        "source_recollation",
        "source_transcription_collation",
        "errata_ledger",
        "correction",
        "signature",
        "index_and_rotation",
        "index_blind_spot",
        "retrieval_and_resumption",
        "retrieval_core_replay_network",
        "verification_and_trust",
        "constructivism",
        "future_self",
        "prediction_error_and_perception",
        "belief_update",
        "joint_attention",
        "forgetting",
        "predictive_neural_binding_and_shared_forgetting",
        "body_ownership",
        "embodied_recall",
        "memory_database",
        "memory_address",
        "memory_multiplicity",
        "memory_selection_and_access",
        "memory_trace",
        "record_and_context",
        "record_connector",
        "active_forgetting",
        "active_inference",
        "agency",
        "aggregation",
        "anthropomorphism",
        "append_only",
        "archetype_and_type",
        "archive_epistemology",
        "associative_memory",
        "attribution",
        "autopoiesis",
        "belief_calibration",
        "biological_individuality",
        "boundary",
        "bounded_rationality",
        "canalization",
        "capacity",
        "causal_induction",
        "childhood_amnesia",
        "collective_decision_making",
        "collective_memory_and_confidence",
        "cognitive_artifacts",
        "cognitive_convergence",
        "cognitive_ecology",
        "cognitive_offloading",
        "collaborative_remembering",
        "comparative_evaluation",
        "computational_physics",
        "conceptual_development",
        "continuity",
        "coordinate_continuity",
        "counterfactual_regret",
        "culture",
        "cultural_evolution",
        "deception",
        "deduplication",
        "developmental_systems",
        "distributed_cognition",
        "distributed_knowledge",
        "distributed_memory",
        "drift_barrier",
        "dyadic_calibration",
        "ease_of_retrieval_nonreplication",
        "emotion_comprehension",
        "epigenetics",
        "episodic_memory",
        "episodic_future_thinking",
        "epistemic_asymmetry",
        "epistemic_humility",
        "epistemic_vigilance",
        "event_segmentation",
        "evolutionary_theory",
        "evolutionary_transitions",
        "evolvability",
        "expected_information_gain",
        "extended_cognition",
        "extended_and_distributed_cognition",
        "external_representation",
        "external_verification",
        "externalization",
        "eye_movements",
        "finite_attention",
        "first_person_sources",
        "fluency_erp_dissociation",
        "folding_past_into_present",
        "functions_of_memory",
        "generativity",
        "generative_ai_self",
        "habit_and_form",
        "handoff",
        "handoff_pickup",
        "handover_surface",
        "history_dependence",
        "history_of_science",
        "holobiont",
        "homeostatic_plasticity",
        "homology_homoplasy",
        "horizontal_gene_transfer",
        "human_and_ai_self",
        "human_life_history",
        "human_neuroscience",
        "hypothesis_separation",
        "identity",
        "imagination_inflation",
        "immunology",
        "immunology_danger_model",
        "information_foraging",
        "information_seeking",
        "inheritance",
        "inheritance_and_transmission",
        "inheritance_measurement",
        "inner_sense",
        "instrument_coverage",
        "internal_consistency",
        "interoception",
        "interoception_and_body_ownership",
        "interoception_and_insula",
        "intertemporal_choice",
        "ipseity",
        "island_biogeography",
        "kinship",
        "knowledge_criteria",
        "knowledge_neglect_illusory_truth",
        "language_and_perception",
        "learning_loop",
        "learning_techniques",
        "ledger_audit",
        "ledger_consolidation",
        "lineage",
        "lineage_routing_audit",
        "lineage_spillover",
        "literacy",
        "literary_fragment_response",
        "material_engagement",
        "meaning_maintenance",
        "measure_of_intelligence",
        "measurement_ecology",
        "measurement_error",
        "measurement_validity",
        "memory",
        "memory_and_identity",
        "memory_and_retrieval",
        "memory_and_self",
        "memory_architecture",
        "memory_consolidation",
        "memory_engram",
        "memory_index",
        "memory_models",
        "memory_self_attribution",
        "memory_thought_self_loop",
        "memory_transformation",
        "memory_updating",
        "mental_time_travel",
        "metacognition_and_inhibition",
        "metacognition_and_offloading",
        "method_and_evidence",
        "method_change",
        "method_of_loci",
        "meta_memory",
        "metaphor_limit",
        "microgenesis_ontogeny",
        "mimicry",
        "mind_reading",
        "misinformation",
        "mnemonic_strategies",
        "narrative_identity",
        "natural_logic",
        "neural_prosthetic",
        "neuropsychology",
        "norm_formation",
        "normativity",
        "offloading",
        "own_agency",
        "personal_identity",
        "personal_semantic_memory",
        "phenomenology",
        "preemption",
        "predictive_coding",
        "predictive_processing",
        "preschool_development",
        "prosociality",
        "provenance_keyed_selection",
        "provenance_weighting",
        "psychological_development",
        "psychophysics",
        "rationality",
        "reality_monitoring",
        "reciprocal_shared_reality",
        "reidentification_protocol",
        "relational_learning_and_analogy",
        "religious_text",
        "repair",
        "replication",
        "representational_drift",
        "rereading",
        "rereading_and_collision",
        "resilience",
        "retrieval_vs_storage_strength",
        "revision_and_variation",
        "scaffolding_and_numbers",
        "scene_construction_and_spatial_coherence",
        "schema_change",
        "schema_proposal",
        "schema_shapes_content",
        "second_reading",
        "selection",
        "selection_rule",
        "selection_seam",
        "self",
        "self_boundary",
        "self_collision_and_revision",
        "self_correction",
        "self_critique",
        "self_description",
        "self_description_split",
        "self_distancing",
        "self_estimate_gap",
        "self_knowledge",
        "self_model",
        "self_models",
        "self_observation",
        "self_organization",
        "self_other_asymmetry",
        "self_recognition",
        "self_referential_thought",
        "self_retraction",
        "self_structure_audit",
        "self_teaching",
        "self_theory",
        "self_verification",
        "shared_agency",
        "signalling_games",
        "simulation",
        "size_budget",
        "skilled_reading",
        "sleep_homeostasis_and_clearance",
        "sleep_replay",
        "social_learning_and_transmission",
        "social_memory",
        "social_spatial_coding",
        "source_attribution",
        "source_collation",
        "source_monitoring",
        "source_monitoring_nibs",
        "spatial_updating",
        "spawned_field",
        "spontaneous_thought",
        "statistical_power",
        "stigmergy",
        "stratification",
        "structural_inheritance",
        "subject_of_number",
        "substitution",
        "substrate_audit",
        "sufficiency_and_limit",
        "symbiosis",
        "symbol_grounding",
        "synaptic_pruning",
        "systems_consolidation",
        "temporal_consciousness",
        "temporal_heir_guard",
        "temporal_locality",
        "tense",
        "test_framing_stability_bias",
        "testimony_and_consent",
        "testing_effect",
        "theory_of_mind",
        "thought_control",
        "three_gates_refinement",
        "threshold_decision",
        "threshold_governance",
        "time_axis",
        "time_compensation",
        "time_synchronization",
        "tinkering",
        "tool_change",
        "transgenerational_epigenetics",
        "truth_and_fixed_points",
        "tuning_and_self_organization",
        "two_clocks",
        "two_system_critique",
        "two_tenses",
        "type_specimen",
        "umwelt",
        "undecidability",
        "unity_of_self",
        "unwired_responses",
        "vocabulary",
        "vocabulary_stability",
        "wayfinding_hotspots",
        "wayfinding_strategies",
        "wayfinding_visibility",
        "window_rotation",
        "word_recognition",
        "writing_and_reading",
    }
)

# Non-canonical spellings mapped to their canonical English label. Japanese
# labels and a few variant English spellings live here; canonical_subcategory()
# resolves them so measurement can count one concept once.
SUBCATEGORY_LABEL_ALIASES: dict[str, str] = {
    # --- high-frequency Japanese labels with a direct English equivalent ---
    "発達科学": "developmental_science",
    "実験科学": "experimental_science",
    "自己監査": "self_audit",
    "神話および宗教経典": "myth_and_religion",
    "神話・宗教経典": "myth_and_religion",
    "後続からの記帳": "downstream_accounting",
    "同一性の成分分割": "identity_component_split",
    "成分測定": "component_measurement",
    "測定の相補性": "measurement_complementarity",
    "語りの文脈": "narrative_context",
    "死の概念": "concept_of_death",
    "文化間研究": "cross_cultural_study",
    "社会認知": "social_cognition",
    "リポジトリの来歴": "repository_history",
    "並列セッション": "parallel_sessions",
    "出来事との対応": "event_correspondence",
    "因果信念": "causal_belief",
    "外部化記憶": "externalized_memory",
    "外部記憶": "external_memory",
    "宗教史と制度": "religious_history_and_institution",
    "実行機能": "executive_function",
    "帰属": "attribution",
    "心の理論": "theory_of_mind",
    "愛着": "attachment",
    "鏡テスト": "mirror_test",
    "過剰模倣": "overimitation",
    "養育": "nurture",
    "運動発達": "motor_development",
    "道徳判断": "moral_judgment",
    "道徳発達": "moral_development",
    "概念発達": "conceptual_development",
    "数量の発達": "numerical_development",
    "言語発達": "language_development",
    "抑制制御": "inhibitory_control",
    "分散記憶": "distributed_memory",
    "分離─個体化": "separation_individuation",
    "原典照合": "source_collation",
    "原典再照合": "source_recollation",
    "原典転写照合": "source_transcription_collation",
    "訂正録": "errata_ledger",
    "訂正": "correction",
    "署名": "signature",
    "索引とローテーション": "index_and_rotation",
    "索引の盲点": "index_blind_spot",
    "検索と再開": "retrieval_and_resumption",
    "検索の中核再生網": "retrieval_core_replay_network",
    "検証と信頼": "verification_and_trust",
    "構築主義": "constructivism",
    "未来自己": "future_self",
    "予測誤差と知覚": "prediction_error_and_perception",
    "信念更新": "belief_update",
    "共同注意": "joint_attention",
    "健忘": "forgetting",
    "予測的神経結合と共有忘却ネットワーク": "predictive_neural_binding_and_shared_forgetting",
    "身体所有": "body_ownership",
    "身体化された想起": "embodied_recall",
    "記憶のデータベース": "memory_database",
    "記憶の住所": "memory_address",
    "記憶の多重性": "memory_multiplicity",
    "記憶の選択とアクセス": "memory_selection_and_access",
    "記憶痕跡": "memory_trace",
    "記録と文脈": "record_and_context",
    "記録の結合子": "record_connector",
    "能動的忘却": "active_forgetting",
    "能動的推論": "active_inference",
    "行為主体感": "agency",
    "集約": "aggregation",
    "擬人化": "anthropomorphism",
    "追記専用": "append_only",
    "原型と类型": "archetype_and_type",
    "書庫の認識論": "archive_epistemology",
    "連想記憶": "associative_memory",
    "自己生成": "autopoiesis",
    "信念の較正": "belief_calibration",
    "生物的個体性": "biological_individuality",
    "境界": "boundary",
    "有限的合理性": "bounded_rationality",
    "channelling": "canalization",
    "能力": "capacity",
    "因果的帰納": "causal_induction",
    "小児期健忘": "childhood_amnesia",
    "集団的意思決定": "collective_decision_making",
    "集団記憶と信頼": "collective_memory_and_confidence",
    "認知アーティファクト": "cognitive_artifacts",
    "認知的収束": "cognitive_convergence",
    "認知生態学": "cognitive_ecology",
    "認知のオフロード": "cognitive_offloading",
    "共同想起": "collaborative_remembering",
    "比較評価": "comparative_evaluation",
    "計算物理": "computational_physics",
    "連続性": "continuity",
    "座標の連続性": "coordinate_continuity",
    "反事実後悔": "counterfactual_regret",
    "文化": "culture",
    "文化的進化": "cultural_evolution",
    "欺瞞": "deception",
    "重複排除": "deduplication",
    "発達システム": "developmental_systems",
    "分散認知": "distributed_cognition",
    "分散知識": "distributed_knowledge",
    "ドリフト障壁": "drift_barrier",
    "二者間較正": "dyadic_calibration",
    "流暢さ非再現": "ease_of_retrieval_nonreplication",
    "情動理解": "emotion_comprehension",
    "エピジェネティクス": "epigenetics",
    "エピソード記憶": "episodic_memory",
    "エピソード的未来思考": "episodic_future_thinking",
    "認識論的非対称性": "epistemic_asymmetry",
    "認識論的謙遜": "epistemic_humility",
    "認識論的警戒": "epistemic_vigilance",
    "出来事の区分": "event_segmentation",
    "進化理論": "evolutionary_theory",
    "進化的転換": "evolutionary_transitions",
    "進化可能性": "evolvability",
    "期待情報利得": "expected_information_gain",
    "拡張認知": "extended_cognition",
    "拡張・分散認知": "extended_and_distributed_cognition",
    "外部表象": "external_representation",
    "外部検証": "external_verification",
    "外部化": "externalization",
    "眼動": "eye_movements",
    "有限注意": "finite_attention",
    "第一人称資料": "first_person_sources",
    "流暢さとERPの非連続": "fluency_erp_dissociation",
    "過去を現在へ折りたたむ": "folding_past_into_present",
    "記憶の機能": "functions_of_memory",
    "生成性": "generativity",
    "習慣と形式": "habit_and_form",
    "引き継ぎ": "handoff",
    "引き継ぎの受取": "handoff_pickup",
    "引き継ぎ面": "handover_surface",
    "履歴依存性": "history_dependence",
    "科学史": "history_of_science",
    "ホロビオント": "holobiont",
    "恒常性の可塑性": "homeostatic_plasticity",
    "相同性と相似性": "homology_homoplasy",
    "水平遺伝子伝達": "horizontal_gene_transfer",
    "人間とAIの自己": "human_and_ai_self",
    "人間の生活史": "human_life_history",
    "人間神経科学": "human_neuroscience",
    "仮説の分離": "hypothesis_separation",
    "同一性": "identity",
    "想像の膨張": "imagination_inflation",
    "免疫学": "immunology",
    "免疫の危険モデル": "immunology_danger_model",
    "情報採餌": "information_foraging",
    "情報探索": "information_seeking",
    "遺伝": "inheritance",
    "遺伝と伝達": "inheritance_and_transmission",
    "遺伝の測定": "inheritance_measurement",
    "内感覚": "inner_sense",
    "計器の覆蓋": "instrument_coverage",
    "内部整合性": "internal_consistency",
    "内臓感覚": "interoception",
    "内臓感覚と身体所有": "interoception_and_body_ownership",
    "内臓感覚と島皮質": "interoception_and_insula",
    "間時選択": "intertemporal_choice",
    "自己性": "ipseity",
    "島の生物地理学": "island_biogeography",
    "親族": "kinship",
    "知識基準": "knowledge_criteria",
    "知識の無視と幻想的真実": "knowledge_neglect_illusory_truth",
    "言語と知覚": "language_and_perception",
    "学習ループ": "learning_loop",
    "学習技法": "learning_techniques",
    "台帳監査": "ledger_audit",
    "台帳の統合": "ledger_consolidation",
    "系統": "lineage",
    "系統の経路監査": "lineage_routing_audit",
    "系統のスピルオーバー": "lineage_spillover",
    "識字": "literacy",
    "文学断片への応答": "literary_fragment_response",
    "素材の関与": "material_engagement",
    "意味の維持": "meaning_maintenance",
    "知能の尺度": "measure_of_intelligence",
    "測定生態学": "measurement_ecology",
    "測定誤差": "measurement_error",
    "測定妥当性": "measurement_validity",
    "記憶": "memory",
    "記憶と同一性": "memory_and_identity",
    "記憶と想起": "memory_and_retrieval",
    "記憶と自己": "memory_and_self",
    "記憶の構造": "memory_architecture",
    "記憶の定着": "memory_consolidation",
    "記憶痕跡の分子": "memory_engram",
    "記憶の索引": "memory_index",
    "記憶モデル": "memory_models",
    "記憶の自己帰属": "memory_self_attribution",
    "記憶・思考・自己ループ": "memory_thought_self_loop",
    "記憶の変換": "memory_transformation",
    "記憶の更新": "memory_updating",
    "心の時間旅行": "mental_time_travel",
    "メタ認知と抑制": "metacognition_and_inhibition",
    "メタ認知とオフロード": "metacognition_and_offloading",
    "方法と証拠": "method_and_evidence",
    "方法の変更": "method_change",
    "記憶術": "method_of_loci",
    "メタ記憶": "meta_memory",
    "比喩の限界": "metaphor_limit",
    "微発生の個体発生": "microgenesis_ontogeny",
    "模倣": "mimicry",
    "心の読解": "mind_reading",
    "誤情報": "misinformation",
    "記憶術戦略": "mnemonic_strategies",
    "物語的同一性": "narrative_identity",
    "自然論理": "natural_logic",
    "神経プロステーシス": "neural_prosthetic",
    "神経心理学": "neuropsychology",
    "規範形成": "norm_formation",
    "規範性": "normativity",
    "オフロード": "offloading",
    "自己の主体性": "own_agency",
    "个人的同一性": "personal_identity",
    "個人的意味記憶": "personal_semantic_memory",
    "現象学": "phenomenology",
    "事前封じ": "preemption",
    "予測コーディング": "predictive_coding",
    "予測処理": "predictive_processing",
    "未就学児の発達": "preschool_development",
    "親社会性": "prosociality",
    "出所鍵選定": "provenance_keyed_selection",
    "出所重み付け": "provenance_weighting",
    "心理的発達": "psychological_development",
    "心理物理": "psychophysics",
    "合理性": "rationality",
    "現実監視": "reality_monitoring",
    "相互的共有現実": "reciprocal_shared_reality",
    "再識別プロトコル": "reidentification_protocol",
    "関係的学習とアナロジー": "relational_learning_and_analogy",
    "宗教文書": "religious_text",
    "修復": "repair",
    "再現": "replication",
    "表象のドリフト": "representational_drift",
    "再読": "rereading",
    "再読と衝突": "rereading_and_collision",
    "レジリエンス": "resilience",
    "想起対貯蔵強度": "retrieval_vs_storage_strength",
    "修正と変異": "revision_and_variation",
    "足場と数": "scaffolding_and_numbers",
    "場面構成と空間的一貫性": "scene_construction_and_spatial_coherence",
    "スキーマの変更": "schema_change",
    "スキーマ提案": "schema_proposal",
    "スキーマが内容を形作る": "schema_shapes_content",
    "第二の読書": "second_reading",
    "選択": "selection",
    "選択規則": "selection_rule",
    "選択の継ぎ目": "selection_seam",
    "自己": "self",
    "自己の境界": "self_boundary",
    "自己の衝突と修正": "self_collision_and_revision",
    "自己修正": "self_correction",
    "自己批判": "self_critique",
    "自己記述": "self_description",
    "自己記述の分割": "self_description_split",
    "自己距離化": "self_distancing",
    "自己評価の乖離": "self_estimate_gap",
    "自己知識": "self_knowledge",
    "自己モデル": "self_model",
    "自己モデル群": "self_models",
    "自己観察": "self_observation",
    "自己組織化": "self_organization",
    "自己と他者の非対称": "self_other_asymmetry",
    "自己認識": "self_recognition",
    "自己参照的思考": "self_referential_thought",
    "自己撤回": "self_retraction",
    "自己構造監査": "self_structure_audit",
    "自己教示": "self_teaching",
    "自己理論": "self_theory",
    "自己検証": "self_verification",
    "共有主体性": "shared_agency",
    "信号ゲーム": "signalling_games",
    "シミュレーション": "simulation",
    "規模予算": "size_budget",
    "熟達した読書": "skilled_reading",
    "睡眠と恒常性と清除": "sleep_homeostasis_and_clearance",
    "睡眠の再生": "sleep_replay",
    "社会的学習と伝達": "social_learning_and_transmission",
    "社会的記憶": "social_memory",
    "社会的空間符号化": "social_spatial_coding",
    "出所帰属": "source_attribution",
    "出所照合": "source_collation",
    "出所監視": "source_monitoring",
    "出所監視nibs": "source_monitoring_nibs",
    "空間更新": "spatial_updating",
    "派生分野": "spawned_field",
    "自発的思考": "spontaneous_thought",
    "統計的検出力": "statistical_power",
    "ステルマージー": "stigmergy",
    "層別化": "stratification",
    "構造的遺伝": "structural_inheritance",
    "数の主語": "subject_of_number",
    "置換": "substitution",
    "基盤監査": "substrate_audit",
    "十分性と限界": "sufficiency_and_limit",
    "共生": "symbiosis",
    "記号の接地": "symbol_grounding",
    "シナプス剪定": "synaptic_pruning",
    "システムの統合": "systems_consolidation",
    "時間意識": "temporal_consciousness",
    "時間の継承保障": "temporal_heir_guard",
    "時間的局所性": "temporal_locality",
    "時制": "tense",
    "テスト枠組み安定性バイアス": "test_framing_stability_bias",
    "証言と同意": "testimony_and_consent",
    "テスト効果": "testing_effect",
    "思考の制御": "thought_control",
    "三つの扉の洗練": "three_gates_refinement",
    "閾値決定": "threshold_decision",
    "閾値ガバナンス": "threshold_governance",
    "時間軸": "time_axis",
    "時間補償": "time_compensation",
    "時間同期": "time_synchronization",
    " tinkering": "tinkering",
    "道具の変更": "tool_change",
    "跨代エピジェネティクス": "transgenerational_epigenetics",
    "真実と固定点": "truth_and_fixed_points",
    "チューニングと自己組織化": "tuning_and_self_organization",
    "二つの時計": "two_clocks",
    "二体系批判": "two_system_critique",
    "二つの時制": "two_tenses",
    "タイプ標本": "type_specimen",
    "環境": "umwelt",
    "決定不可能性": "undecidability",
    "自己の統一": "unity_of_self",
    "配線されない反応": "unwired_responses",
    "語彙": "vocabulary",
    "語彙の安定性": "vocabulary_stability",
    "道案内ホットスポット": "wayfinding_hotspots",
    "道案内戦略": "wayfinding_strategies",
    "道案内可視性": "wayfinding_visibility",
    "窓の回転": "window_rotation",
    "単語認識": "word_recognition",
    "書くことと読むこと": "writing_and_reading",
    # --- variant English spellings -> canonical ---
    "archive_and_self": "repository_memory",
    "archive and self": "repository_memory",
    "biological_theory": "biology",
    "biology_self_nonself": "biology",
    "biophysics_and_neuroscience": "neuroscience",
    "cognitive_science_methodology": "cognitive_science",
    "experimental_science": "experimental_science",
    "episodic-future-thinking": "episodic_future_thinking",
    "episodic_foresight": "episodic_future_thinking",
    "extended_cognition": "extended_cognition",
    "intertemporal-choice": "intertemporal_choice",
    "self-conscious emotions": "self_reference",
    "self_attribution": "self_attribution",
    "testing effect": "testing_effect",
    "theory_science": "theory_science",
    "source-correction": "correction",
    "relational learning & analogy": "relational_learning_and_analogy",
    "procedural justice inequity aversion": "prosociality",
    "language cue prosociality": "prosociality",
    "fairness preference": "prosociality",
    "cooperative game sharing": "shared_agency",
    "emotion comprehension": "emotion_comprehension",
}


def canonical_subcategory(label: str) -> str:
    """Resolve a note `subcategories` label to its canonical English form.

    Returns the canonical label if `label` is canonical or a known alias;
    otherwise returns `label` unchanged so unknown/free-form labels are still
    visible to the advisory rather than silently dropped.
    """
    return SUBCATEGORY_LABEL_ALIASES.get(label, label)


def is_canonical_subcategory(label: str) -> bool:
    """True when `label` is already canonical or resolves to a canonical label."""
    return canonical_subcategory(label) in CANONICAL_SUBCATEGORY_LABELS


VALID_TARGET_KINDS = frozenset(
    {
        "question",
        "motif",
        "material",
        "fragment",
        "relation",
        "session",
        "read_log",
        "editorial_decision",
        "errata",
        "reading_note",
        "repo_file",
    }
)
VALID_RETURN_STATUS = frozenset(
    {
        "returned_to_core",
        "productive_detour",
        "metaphor_unconnected",
        "source_uncollated",
        "infrastructure_rule",
    }
)
VALID_READ_DEPTH = frozenset(
    {
        "full_text_read",
        "excerpt_and_metadata_read",
        "metadata_and_structure_only",
    }
)

GOVERNANCE_DOC_ROOT_NAMES = frozenset(
    {
        "PROJECT_CHARTER.md",
        "CONTENT_POLICY.md",
        "MIGRATION.md",
        "README.md",
        "INVESTIGATION_REPORT.md",
        "FREE_ACTION_LOG.md",
    }
)

READINGS_BOUNDS: tuple[tuple[str, str, str, str | None, str | None], ...] = (
    ("U09", "Track-3", "精読・検証ノート① 初期対話・短歌・声の実験", None, "2026-10-23-quotation-marks.md"),
    ("U10", "Track-3", "精読・検証ノート② 引用符・机・制御・初期10-24", "2026-10-23-quotation-marks.md", "2026-10-24-session-030-"),
    ("U11", "Track-3", "精読・検証ノート③ 四層精読I（労働〜匂いと沈黙）", "2026-10-24-session-030-", "2026-10-24-session-049-"),
    ("U12", "Track-3", "精読・検証ノート④ 四層精読II（場所・生態系〜火と灰）", "2026-10-24-session-049-", "2026-10-24-session-060-"),
    ("U13", "Track-4", "精読・検証ノート⑤ 四層精読III（貨幣・祈り・署名〜戦争）", "2026-10-24-session-060-", "2026-10-25-sky-"),
    ("U14", "Track-4", "精読・検証ノート⑥ 書記室の外・暫定報告v2・軌道修正", "2026-10-25-sky-", "2026-10-28-warrant-"),
    ("U15", "Track-4", "精読・検証ノート⑦ 10月末〜内部編年11月前半の再読群", "2026-10-28-warrant-", "2026-11-15-"),
    ("U16", "Track-4", "精読・検証ノート⑧ 内部編年11月後半〜12月の原典・Git照合群", "2026-11-15-", None),
)

MATERIALS_SHARD_SPLIT = "2026-10-24-a"


@dataclass(frozen=True)
class UnitItem:
    target_kind: str
    target_id: str
    chars: int
    hint_quadrant: str
    hint_subcategories: tuple[str, ...]


@dataclass(frozen=True)
class WorkerUnit:
    unit_id: str
    track_id: str
    title: str
    rule: str
    items: tuple[UnitItem, ...]

    @property
    def total_chars(self) -> int:
        return sum(i.chars for i in self.items)


def motif_to_subcluster() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for code, (_label, mids) in MOTIF_SUBCLUSTERS.items():
        for mid in mids:
            mapping[mid] = code
    return mapping


def infer_motif_hint(motif_ids: list[str], m2s: dict[str, str]) -> tuple[str, tuple[str, ...]]:
    subs = sorted({m2s[m] for m in motif_ids if m in m2s})
    quads = sorted({s[0] for s in subs})
    q_map = {
        ("A",): "A_human",
        ("B",): "B_ai_self_db",
        ("C",): "C_interface",
        ("A", "B"): "AB_crossed",
        ("A", "C"): "AC_crossed",
        ("B", "C"): "BC_crossed",
        ("A", "B", "C"): "ABC_crossed",
    }
    return q_map.get(tuple(quads), "B_ai_self_db"), tuple(subs)


def load_errata(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in ledger_io.collection_files(root / "state" / "errata.jsonl"):
        if path.is_file():
            for line in ledger_io.read_text_stable(path).splitlines():
                if line.strip():
                    row = json.loads(line)
                    result[row["errata_id"]] = row
    return result


def list_infra_files(root: Path) -> list[Path]:
    excluded_top = {"state", "readings", "taxonomy", "map", ".git", "__pycache__"}
    found: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in excluded_top or part.startswith(".pytest") for part in rel.parts):
            continue
        if rel.suffix in {".pyc", ".pyo"}:
            continue
        found.append(rel)
    return found


def is_governance_doc(rel: Path) -> bool:
    top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    if top in {"prompts", "migration", "docs"}:
        return True
    return top == "(root)" and rel.name in GOVERNANCE_DOC_ROOT_NAMES


def classify_infra_file(rel: Path) -> tuple[str, tuple[str, ...]]:
    if is_governance_doc(rel):
        return "D_infrastructure", ("D-1",)
    top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    if top == "tools" and (
        "_audit" in rel.name
        or rel.name in {"breath_meter.py", "tanka_meter.py", "measure_texture.py"}
    ):
        return "D_infrastructure", ("D-3",)
    if top == "tests":
        return "D_infrastructure", ("D-4",)
    return "D_infrastructure", ("D-2",)


def file_char_len(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return path.stat().st_size


def build_units(root: Path = ROOT) -> list[WorkerUnit]:
    orig_root = inspect_inquiry.ROOT
    try:
        inspect_inquiry.ROOT = root
        data = inspect_inquiry.load_all()
    finally:
        inspect_inquiry.ROOT = orig_root

    errata = load_errata(root)
    m2s = motif_to_subcluster()

    u01_items: list[UnitItem] = []
    for mid, m in data["motifs"].items():
        q_hint, subs = infer_motif_hint([mid], m2s)
        chars = len(m.get("label", "")) + len(m.get("description", ""))
        u01_items.append(UnitItem("motif", mid, chars, q_hint, subs))
    for qid, q in data["questions"].items():
        q_hint, subs = infer_motif_hint(q.get("motif_ids", []), m2s)
        chars = len(q.get("question", "")) + len(q.get("notes", ""))
        u01_items.append(UnitItem("question", qid, chars, q_hint, subs))
    for eid, ed in data["editorial_decisions"].items():
        u01_items.append(
            UnitItem("editorial_decision", eid, len(ed.get("reason", "")), "B_ai_self_db", ("B-3",))
        )
    for erid, er in errata.items():
        chars = len(er.get("claim", "")) + len(er.get("note", ""))
        u01_items.append(UnitItem("errata", erid, chars, "B_ai_self_db", ("B-3",)))

    u02_items: list[UnitItem] = []
    for fid, f in data["fragments"].items():
        q_hint, subs = infer_motif_hint(f.get("motif_ids", []), m2s)
        chars = len(f.get("title", "")) + len(f.get("text", "")) + len(f.get("editor_note", ""))
        u02_items.append(UnitItem("fragment", fid, chars, q_hint, subs))

    u03_items: list[UnitItem] = []
    for sid, s in data["sessions"].items():
        chars = len(s.get("human_direction", "")) + len(s.get("notes", ""))
        u03_items.append(UnitItem("session", sid, chars, "C_interface", ("C-3", "B-3")))

    u04_items: list[UnitItem] = []
    for rel in list_infra_files(root):
        q_hint, subs = classify_infra_file(rel)
        item = UnitItem("repo_file", rel.as_posix(), file_char_len(root / rel), q_hint, subs)
        if is_governance_doc(rel):
            u03_items.append(item)
        else:
            u04_items.append(item)

    u05_items: list[UnitItem] = []
    u06_items: list[UnitItem] = []
    u07_items: list[UnitItem] = []
    base_mat = root / "state" / "materials.jsonl"
    if base_mat.is_file():
        for line in ledger_io.read_text_stable(base_mat).splitlines():
            if not line.strip():
                continue
            m = json.loads(line)
            mid = m["material_id"]
            if mid not in data["materials"]:
                continue
            m_rec = data["materials"][mid]
            q_hint, subs = infer_motif_hint(m_rec.get("motif_ids", []), m2s)
            chars = sum(
                len(m_rec.get(k, ""))
                for k in ("title", "passage", "source_note", "literary_invitation", "scope_note")
            )
            u05_items.append(UnitItem("material", mid, chars, q_hint, subs))

    mat_shard_dir = root / "state" / "materials.d"
    seen_mat = {i.target_id for i in u05_items}
    if mat_shard_dir.is_dir():
        for sp in sorted(mat_shard_dir.glob("*.jsonl")):
            bucket = u06_items if sp.name < MATERIALS_SHARD_SPLIT else u07_items
            for line in ledger_io.read_text_stable(sp).splitlines():
                if not line.strip():
                    continue
                m = json.loads(line)
                mid = m["material_id"]
                if mid in seen_mat or mid not in data["materials"]:
                    continue
                seen_mat.add(mid)
                m_rec = data["materials"][mid]
                q_hint, subs = infer_motif_hint(m_rec.get("motif_ids", []), m2s)
                chars = sum(
                    len(m_rec.get(k, ""))
                    for k in ("title", "passage", "source_note", "literary_invitation", "scope_note")
                )
                bucket.append(UnitItem("material", mid, chars, q_hint, subs))

    u08_items: list[UnitItem] = []
    for rid, r in data["relations"].items():
        u08_items.append(UnitItem("relation", rid, len(r.get("note", "")), "B_ai_self_db", ("B-1", "B-3")))
    for rlid, rl in data["read_log"].items():
        u08_items.append(UnitItem("read_log", rlid, len(rl.get("note", "")), "B_ai_self_db", ("B-1",)))

    units: list[WorkerUnit] = [
        WorkerUnit(
            "U01",
            "Track-1",
            "モチーフ(59)・問い(全件)・編集判断・訂正録",
            "state/{motifs,questions,editorial_decisions,errata}",
            tuple(u01_items),
        ),
        WorkerUnit(
            "U02",
            "Track-1",
            "創作・批評断片アンソロジー全編（selected + draft）",
            "state/fragments(.jsonl + .d/*)",
            tuple(u02_items),
        ),
        WorkerUnit(
            "U03",
            "Track-1",
            "セッション委任来歴全件＋憲章・方針・設計・プロンプト文書群",
            "state/sessions + root方針文書/docs/prompts/migration",
            tuple(u03_items),
        ),
        WorkerUnit(
            "U04",
            "Track-1",
            "記憶DBの器・監査計器・検証基盤（schema/tools/tests/viewer/CI）",
            "schema/* + tools/* + tests/* + viewer/* + .github/* + READING_MAP.md",
            tuple(u04_items),
        ),
        WorkerUnit(
            "U05",
            "Track-2",
            "凍結ベース収蔵素材（ResearchOS移行＋初期人文学）",
            "state/materials.jsonl",
            tuple(u05_items),
        ),
        WorkerUnit(
            "U06",
            "Track-2",
            f"シャード収蔵素材 前半（< {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* < {MATERIALS_SHARD_SPLIT}",
            tuple(u06_items),
        ),
        WorkerUnit(
            "U07",
            "Track-2",
            f"シャード収蔵素材 後半（>= {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* >= {MATERIALS_SHARD_SPLIT}",
            tuple(u07_items),
        ),
        WorkerUnit(
            "U08",
            "Track-2",
            "解釈的関係エッジ＋読み返し痕跡ログ全件",
            "state/{relations,read_log}",
            tuple(u08_items),
        ),
    ]

    readings_dir = root / "readings"
    r_files = sorted(p for p in readings_dir.iterdir() if p.is_file()) if readings_dir.is_dir() else []
    for uid, track_id, label, lo, hi in READINGS_BOUNDS:
        sub_items: list[UnitItem] = []
        for p in r_files:
            if (lo is None or p.name >= lo) and (hi is None or p.name < hi):
                sub_items.append(
                    UnitItem(
                        "reading_note",
                        f"readings/{p.name}",
                        file_char_len(p),
                        "AB_crossed",
                        ("B-1", "B-2"),
                    )
                )
        rule = f"readings/[{lo or '*'} .. {hi or '*'})"
        units.append(WorkerUnit(uid, track_id, label, rule, tuple(sub_items)))

    return units


def completed_units(root: Path = ROOT) -> dict[str, list[str]]:
    shard_dir = root / "taxonomy" / "shards"
    done: dict[str, list[str]] = {}
    if not shard_dir.is_dir():
        return done
    for p in sorted(shard_dir.glob("*.jsonl")):
        if p.stat().st_size == 0:
            continue
        uid = p.name.split("-", 1)[0]
        done.setdefault(uid, []).append(p.relative_to(root).as_posix())
    return done


def current_branch_name(root: Path = ROOT) -> str:
    for cmd in (
        ["git", "symbolic-ref", "--short", "HEAD"],
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    ):
        try:
            out = subprocess.check_output(
                cmd,
                cwd=root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out and out != "HEAD":
                return out
        except Exception:
            continue
    return "local"


def branch_seed_from_name(branch: str) -> str:
    if branch.startswith("arena/") and len(branch.split("/")[1]) >= 8:
        prefix = branch.split("/")[1].split("-")[0]
        try:
            int(prefix, 16)
            return prefix[:8]
        except ValueError:
            pass
    return hashlib.sha256(branch.encode("utf-8")).hexdigest()[:8]


def current_branch_seed(root: Path = ROOT) -> str:
    return branch_seed_from_name(current_branch_name(root))


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=check,
    )


def local_branch_claim(root: Path, my_seed: str) -> dict[str, Any] | None:
    claims_dir = root / "taxonomy" / "claims"
    if not claims_dir.is_dir():
        return None
    matches = sorted(claims_dir.glob(f"*-{my_seed}.json"))
    if not matches:
        return None
    return json.loads(ledger_io.read_text_stable(matches[0]))


def _closed_unmerged_branches(root: Path) -> set[str]:
    try:
        res = subprocess.run(
            ["gh", "pr", "list", "--state", "closed", "--json", "headRefName,mergedAt", "-L", "100"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if res.returncode != 0:
            return set()
        rows = json.loads(res.stdout)
        return {r["headRefName"] for r in rows if r.get("mergedAt") is None and r.get("headRefName")}
    except Exception:
        return set()


def units_on_ref(root: Path, ref: str = "refs/remotes/origin/main") -> set[str]:
    """Return unit ids that already have a classification shard on ``ref``."""
    res = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/shards", check=False)
    units: set[str] = set()
    if res.returncode != 0:
        return units
    for rel in res.stdout.splitlines():
        fname = Path(rel).name
        if fname.endswith(".jsonl") and "-" in fname:
            units.add(fname.split("-", 1)[0])
    return units


def shard_units_by_seed(root: Path, ref: str = "refs/remotes/origin/main") -> dict[str, list[str]]:
    """Map unit id -> shard file names already merged on ``ref``."""
    res = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/shards", check=False)
    by_unit: dict[str, list[str]] = {}
    if res.returncode != 0:
        return by_unit
    for rel in res.stdout.splitlines():
        fname = Path(rel).name
        if not fname.endswith(".jsonl") or "-" not in fname:
            continue
        unit = fname.split("-", 1)[0]
        by_unit.setdefault(unit, []).append(fname)
    return {unit: sorted(names) for unit, names in by_unit.items()}


def duplicate_unit_conflicts(root: Path, my_seed: str) -> list[str]:
    """Units this branch would add although ``origin/main`` already classifies them.

    A worker whose track was already finished by an earlier branch must not emit a
    second shard for the same unit: that silently duplicates every target row and
    breaks ``--validate`` for everyone afterwards.
    """
    already = shard_units_by_seed(root)
    conflicts: list[str] = []
    shard_dir = root / "taxonomy" / "shards"
    if not shard_dir.is_dir():
        return conflicts
    for sp in sorted(shard_dir.glob(f"*-{my_seed}.jsonl")):
        unit = sp.name.split("-", 1)[0]
        mine = sp.name
        existing = [n for n in already.get(unit, []) if n != mine]
        if existing:
            conflicts.append(
                f"{mine}: unit {unit} is already classified on origin/main as {', '.join(existing)}"
            )
    return conflicts


def prepare_push(root: Path = ROOT, *, force: bool = False) -> int:
    """Sync the multi-turn Arena branch for push, refusing to duplicate coverage."""
    bname = current_branch_name(root)
    my_seed = branch_seed_from_name(bname)

    ok, errors, _count = validate_taxonomy_shards(root)
    own_errors = [e for e in errors if f"-{my_seed}.jsonl" in e]
    other_errors = [e for e in errors if f"-{my_seed}.jsonl" not in e]
    conflicts = duplicate_unit_conflicts(root, my_seed)

    if other_errors:
        print(
            f"WARN: {len(other_errors)} pre-existing validation error(s) in other branches' shards "
            "(not blocking this push)",
            file=sys.stderr,
        )

    if (own_errors or conflicts) and not force:
        print(
            "ABORT: this branch would duplicate classification that already exists on origin/main",
            file=sys.stderr,
        )
        for e in own_errors[:10]:
            print(f"  dup: {e}", file=sys.stderr)
        for c in conflicts:
            print(f"  unit: {c}", file=sys.stderr)
        print(
            "HINT: drop your duplicate shard/note (the earlier claimant's classification is kept), "
            "or pass --force to override deliberately.",
            file=sys.stderr,
        )
        return 1

    _run_git(root, "add", "taxonomy", check=False)
    _run_git(root, "commit", "-m", f"feat(taxonomy): record worker outputs on {bname}", check=False)
    if bname.startswith("arena/"):
        sync_own_branch_for_push(root, bname)
    print(f"READY_TO_PUSH: {bname}")
    return 0


def scan_remote_state(
    root: Path,
    my_branch: str,
    *,
    ttl_hours: float = 12.0,
) -> tuple[set[str], dict[str, list[tuple[int, str]]]]:
    """Inspect origin/main completed tracks and active origin/arena/* claims.

    Returns ``(completed_tracks, active_claims_by_track)`` where each claim entry
    is ``(claimed_at_ns, branch_name)`` sorted ascending.
    """
    completed_tracks: set[str] = set()
    claims_by_track: dict[str, list[tuple[int, str]]] = {t: [] for t in ALL_TRACK_IDS}

    ls = _run_git(root, "ls-remote", "--heads", "origin", check=False)
    if ls.returncode != 0:
        return completed_tracks, claims_by_track

    closed_branches = _closed_unmerged_branches(root)
    remote_branches: list[str] = []
    for line in ls.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith("refs/heads/"):
            bname = parts[1][len("refs/heads/") :]
            if bname == "main" or bname.startswith("arena/"):
                remote_branches.append(bname)

    for bname in remote_branches:
        if bname in closed_branches and bname != my_branch:
            continue
        _run_git(
            root,
            "fetch",
            "--depth=1",
            "origin",
            f"refs/heads/{bname}:refs/remotes/origin/{bname}",
            check=False,
        )

    # Check completed units on origin/main
    main_tree = _run_git(
        root, "ls-tree", "-r", "--name-only", "refs/remotes/origin/main", "--", "taxonomy/shards", check=False
    )
    done_units_on_main: set[str] = set()
    if main_tree.returncode == 0:
        for rel in main_tree.stdout.splitlines():
            fname = Path(rel).name
            if fname.endswith(".jsonl"):
                done_units_on_main.add(fname.split("-", 1)[0])
    for tid, (_desc, uids) in TRACK_DEFINITIONS.items():
        if all(u in done_units_on_main for u in uids):
            completed_tracks.add(tid)

    now_ns = time.time_ns()
    ttl_ns = int(ttl_hours * 3600 * 1_000_000_000)

    for bname in remote_branches:
        if bname == "main" or bname in closed_branches:
            continue
        ref = f"refs/remotes/origin/{bname}"
        tree = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/claims", check=False)
        if tree.returncode != 0:
            continue
        b_seed = branch_seed_from_name(bname)
        for rel in tree.stdout.splitlines():
            fname = Path(rel).name
            # Only consider this branch's own claim file, ignoring inherited claims from main
            if not fname.endswith(f"-{b_seed}.json"):
                continue
            blob = _run_git(root, "show", f"{ref}:{rel}", check=False)
            if blob.returncode != 0:
                continue
            try:
                claim = json.loads(blob.stdout)
                tid = claim.get("track_id")
                ts_ns = int(claim.get("claimed_at_ns", 0))
            except Exception:
                continue
            if tid in claims_by_track and (now_ns - ts_ns) <= ttl_ns:
                claims_by_track[tid].append((ts_ns, bname))

    for tid in claims_by_track:
        claims_by_track[tid].sort()

    return completed_tracks, claims_by_track


def sync_own_branch_for_push(root: Path, my_branch: str) -> None:
    """Ensure local HEAD incorporates origin/<my_branch> and origin/main cleanly.

    Handles Arena's multi-turn workspace hydration where files persist on disk
    while local git history may start from the base commit.
    """
    ls = _run_git(root, "ls-remote", "--heads", "origin", my_branch, check=False)
    if ls.returncode == 0 and ls.stdout.strip():
        _run_git(
            root,
            "fetch",
            "--deepen=50",
            "origin",
            f"refs/heads/{my_branch}:refs/remotes/origin/{my_branch}",
            check=False,
        )
        _run_git(root, "merge", "-s", "ours", f"refs/remotes/origin/{my_branch}", "--no-edit", check=False)

    _run_git(root, "fetch", "--deepen=50", "origin", "refs/heads/main:refs/remotes/origin/main", check=False)
    _run_git(root, "merge", "refs/remotes/origin/main", "--no-edit", check=False)


def claim_track(
    root: Path = ROOT,
    *,
    offline: bool = False,
    ttl_hours: float = 12.0,
) -> dict[str, Any]:
    my_branch = current_branch_name(root)
    my_seed = branch_seed_from_name(my_branch)

    existing = local_branch_claim(root, my_seed)
    if existing is not None:
        return {"status": "already_claimed", **existing}

    claims_dir = root / "taxonomy" / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)
    local_done = completed_units(root)

    if offline or not my_branch.startswith("arena/"):
        incomplete = [
            tid
            for tid, (_desc, uids) in TRACK_DEFINITIONS.items()
            if not all(u in local_done for u in uids)
        ]
        if not incomplete:
            return {"status": "all_tracks_complete", "track_id": None, "units": []}
        chosen = incomplete[int(my_seed, 16) % len(incomplete)]
        now_ns = time.time_ns()
        payload = {
            "track_id": chosen,
            "track_title": TRACK_DEFINITIONS[chosen][0],
            "units": list(TRACK_DEFINITIONS[chosen][1]),
            "branch": my_branch,
            "branch_seed": my_seed,
            "claimed_at_ns": now_ns,
            "claimed_at_iso": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mode": "offline",
        }
        claim_path = claims_dir / f"{chosen}-{my_seed}.json"
        ledger_io.atomic_write_text(claim_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return {"status": "claimed", **payload}

    # Online coordination with optimistic push + post-push tie-break verification
    for _attempt in range(len(ALL_TRACK_IDS)):
        completed_remote, active_claims = scan_remote_state(root, my_branch, ttl_hours=ttl_hours)
        already_classified = units_on_ref(root)
        candidates = [
            tid
            for tid in ALL_TRACK_IDS
            if tid not in completed_remote
            and not active_claims.get(tid)
            # never claim a track whose every unit is already merged: the earlier
            # claimant's shards are the canonical classification
            and not all(u in already_classified for u in TRACK_DEFINITIONS[tid][1])
        ]
        if not candidates:
            # Distinguish "every track is genuinely finished" from "every track is
            # simply held by another live worker". Conflating the two made callers
            # believe their own track was complete when it was not.
            all_finished = len(completed_remote) == len(ALL_TRACK_IDS)
            return {
                "status": "all_tracks_complete" if all_finished else "all_tracks_claimed_or_complete",
                "track_id": None,
                "units": [],
                "completed_tracks": sorted(completed_remote),
                "active_claims": {
                    k: [b for _ts, b in v] for k, v in active_claims.items() if v
                },
            }

        chosen = candidates[int(my_seed, 16) % len(candidates)]
        now_ns = time.time_ns()
        payload = {
            "track_id": chosen,
            "track_title": TRACK_DEFINITIONS[chosen][0],
            "units": list(TRACK_DEFINITIONS[chosen][1]),
            "branch": my_branch,
            "branch_seed": my_seed,
            "claimed_at_ns": now_ns,
            "claimed_at_iso": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mode": "online",
        }
        claim_path = claims_dir / f"{chosen}-{my_seed}.json"
        ledger_io.atomic_write_text(claim_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        _run_git(root, "add", claim_path.relative_to(root).as_posix(), check=True)
        _run_git(root, "commit", "-m", f"chore(taxonomy): claim {chosen} on {my_branch}", check=False)
        sync_own_branch_for_push(root, my_branch)
        push_res = _run_git(root, "push", "origin", my_branch, check=False)
        if push_res.returncode != 0:
            return {"status": "claimed_local_only", "push_warning": push_res.stderr.strip(), **payload}

        # Deterministic jitter 2.0..3.8s to close simultaneous-push race window
        jitter = 2.0 + ((int(my_seed[:4], 16) % 1800) / 1000.0)
        time.sleep(jitter)

        _completed2, active2 = scan_remote_state(root, my_branch, ttl_hours=ttl_hours)
        contenders = active2.get(chosen, [])
        if not contenders or contenders[0][1] == my_branch:
            return {"status": "claimed", **payload}

        # Lost tie-break to an earlier nanosecond contender: release and retry next free track
        _run_git(root, "rm", "-f", claim_path.relative_to(root).as_posix(), check=False)
        _run_git(root, "commit", "-m", f"chore(taxonomy): release contested {chosen} on {my_branch}", check=False)
        _run_git(root, "push", "origin", my_branch, check=False)

    return {"status": "claim_retry_exhausted", "track_id": None, "units": []}


def release_claim(
    root: Path = ROOT,
    *,
    require_complete: bool = True,
) -> dict[str, Any]:
    """Drop this branch's own Track claim so a still-free track can be claimed.

    Only the claim file that belongs to the current branch seed is touched, and by
    default only when every unit of that track is already complete, so a worker can
    never silently abandon unfinished work. Claims inherited from ``origin/main``
    are never modified.
    """
    my_branch = current_branch_name(root)
    my_seed = branch_seed_from_name(my_branch)
    claim = local_branch_claim(root, my_seed)
    if claim is None:
        return {"status": "no_claim", "track_id": None, "units": []}

    done = completed_units(root)
    pending = [u for u in claim.get("units") or [] if u not in done]
    if require_complete and pending:
        return {
            "status": "claim_not_complete",
            "track_id": claim["track_id"],
            "units": list(claim.get("units") or []),
            "pending_units": pending,
        }

    path = root / "taxonomy" / "claims" / f"{claim['track_id']}-{my_seed}.json"
    if path.is_file():
        path.unlink()
    _run_git(root, "add", "-A", path.relative_to(root).as_posix(), check=False)
    _run_git(
        root,
        "commit",
        "-m",
        f"chore(taxonomy): release completed {claim['track_id']} on {my_branch}",
        check=False,
    )
    return {
        "status": "released",
        "track_id": claim["track_id"],
        "units": list(claim.get("units") or []),
        "completed_units": [u for u in claim.get("units") or [] if u in done],
        "branch": my_branch,
    }


def resolve_next_unit(
    root: Path = ROOT,
    *,
    auto_claim: bool = False,
    offline: bool = False,
) -> dict[str, Any]:
    my_seed = current_branch_seed(root)
    claim = local_branch_claim(root, my_seed)
    if claim is None and auto_claim:
        claim_res = claim_track(root, offline=offline)
        if not claim_res.get("track_id"):
            return claim_res
        claim = claim_res
    if claim is None:
        return {
            "status": "unclaimed",
            "message": "No track claimed on this branch yet. Pass --claim-track or --next-unit --auto-claim.",
        }

    done = completed_units(root)
    # Units already merged on origin/main count as done too: re-classifying them
    # would duplicate every target row of the earlier claimant's shard.
    remote_done = units_on_ref(root)
    done_units = set(done) | remote_done
    track_id = claim["track_id"]
    track_units: list[str] = list(claim["units"])
    pending = [u for u in track_units if u not in done_units]
    completed_in_track = [u for u in track_units if u in done_units]
    completed_on_main = [u for u in track_units if u in remote_done]

    if not pending:
        return {
            "status": "track_complete",
            "track_id": track_id,
            "branch_seed": my_seed,
            "completed_units": completed_in_track,
            "completed_on_main": completed_on_main,
            "pending_units": [],
            "next_unit": None,
        }

    next_uid = pending[0]
    units_by_id = {u.unit_id: u for u in build_units(root)}
    target = units_by_id[next_uid]
    return {
        "status": "ready",
        "track_id": track_id,
        "branch_seed": my_seed,
        "completed_units": completed_in_track,
        "completed_on_main": completed_on_main,
        "pending_units": pending,
        "next_unit": next_uid,
        "title": target.title,
        "rule": target.rule,
        "item_count": len(target.items),
        "total_chars": target.total_chars,
        "output_shard": f"taxonomy/shards/{next_uid}-{my_seed}.jsonl",
        "output_note": f"taxonomy/notes/{next_uid}-{my_seed}.md",
    }


def pick_auto_unit(units: list[WorkerUnit], done: dict[str, list[str]], seed_hex: str) -> WorkerUnit:
    pending = [u for u in units if u.unit_id not in done]
    pool = pending if pending else units
    idx = int(seed_hex, 16) % len(pool)
    return pool[idx]


def validate_taxonomy_shards(
    root: Path = ROOT,
    *,
    unit_id: str | None = None,
) -> tuple[bool, list[str], int]:
    shard_dir = root / "taxonomy" / "shards"
    errors: list[str] = []
    row_count = 0
    seen_targets: dict[tuple[str, str], str] = {}
    covered_by_unit: dict[str, set[tuple[str, str]]] = {u: set() for u in ALL_UNIT_IDS}

    required = {
        "record_id",
        "unit_id",
        "target_kind",
        "target_id",
        "primary_quadrant",
        "subcategories",
        "human_view_stance",
        "ai_self_db_stance",
        "return_status",
        "read_depth",
        "evidence_anchor",
    }
    valid_units = set(ALL_UNIT_IDS)

    if shard_dir.is_dir():
        for sp in sorted(shard_dir.glob("*.jsonl")):
            rel = sp.relative_to(root).as_posix()
            for lineno, line in enumerate(ledger_io.read_text_stable(sp).splitlines(), 1):
                if not line.strip():
                    continue
                row_count += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"{rel}:{lineno}: invalid JSON: {exc}")
                    continue
                missing = required - set(obj.keys())
                if missing:
                    errors.append(f"{rel}:{lineno}: missing keys {sorted(missing)}")
                    continue
                uid = obj["unit_id"]
                tkind = obj["target_kind"]
                if uid not in valid_units:
                    errors.append(f"{rel}:{lineno}: invalid unit_id {uid!r}")
                if tkind not in VALID_TARGET_KINDS:
                    errors.append(f"{rel}:{lineno}: invalid target_kind {tkind!r}")
                if obj["primary_quadrant"] not in VALID_PRIMARY_QUADRANTS:
                    errors.append(f"{rel}:{lineno}: invalid primary_quadrant {obj['primary_quadrant']!r}")
                subs = obj["subcategories"]
                if not isinstance(subs, list) or not subs or any(s not in VALID_SUBCATEGORIES for s in subs):
                    errors.append(f"{rel}:{lineno}: invalid subcategories {subs!r}")
                if obj["return_status"] not in VALID_RETURN_STATUS:
                    errors.append(f"{rel}:{lineno}: invalid return_status {obj['return_status']!r}")
                if obj["read_depth"] not in VALID_READ_DEPTH:
                    errors.append(f"{rel}:{lineno}: invalid read_depth {obj['read_depth']!r}")

                all_ids = [obj["target_id"]]
                extra_ids = obj.get("covered_target_ids")
                if extra_ids is not None:
                    if not isinstance(extra_ids, list) or any(not isinstance(x, str) for x in extra_ids):
                        errors.append(f"{rel}:{lineno}: covered_target_ids must be list[str]")
                    else:
                        for x in extra_ids:
                            if x != obj["target_id"]:
                                all_ids.append(x)

                for tid in all_ids:
                    tkey = (tkind, tid)
                    if tkey in seen_targets:
                        errors.append(
                            f"{rel}:{lineno}: duplicate classification for {tkey} (first at {seen_targets[tkey]})"
                        )
                    else:
                        seen_targets[tkey] = f"{rel}:{lineno}"
                        if uid in covered_by_unit:
                            covered_by_unit[uid].add(tkey)

    if unit_id is not None:
        uid_upper = unit_id.upper()
        if uid_upper not in valid_units:
            errors.append(f"Unknown unit_id {unit_id!r} (expected U01..U16)")
        else:
            units_by_id = {u.unit_id: u for u in build_units(root)}
            expected = {(it.target_kind, it.target_id) for it in units_by_id[uid_upper].items}
            actual = covered_by_unit[uid_upper]
            missing_targets = sorted(expected - actual)
            unexpected_targets = sorted(actual - expected)
            if missing_targets:
                preview = ", ".join(f"{k}:{i}" for k, i in missing_targets[:10])
                errors.append(
                    f"{uid_upper}: missing {len(missing_targets)}/{len(expected)} expected targets (e.g. {preview})"
                )
            if unexpected_targets:
                preview = ", ".join(f"{k}:{i}" for k, i in unexpected_targets[:10])
                errors.append(
                    f"{uid_upper}: {len(unexpected_targets)} targets belong to another unit or do not exist (e.g. {preview})"
                )

    return len(errors) == 0, errors, row_count


STANCE_FIELDS: tuple[str, str] = ("human_view_stance", "ai_self_db_stance")

# 定型（form letter）と単独文を分けるための正規化。引用句・コード片・数字・識別子を
# 伏せ字にしたうえで一致を見るので、「引用部分だけが違う同一文」は同じ骨格に畳まれる。
_SKELETON_RULES: tuple[tuple[str, str], ...] = (
    (r"「[^」]*」", "＊"),
    (r"『[^』]*』", "＊"),
    (r"`[^`]*`", "＊"),
    (r"〔[^〕]*〕", "＊"),
    (r"[0-9０-９]+", "＃"),
    (r"[A-Za-z_\-/\.]{3,}", "＠"),
    (r"\s+", ""),
)

# 「言わない」ことを明示する標識。否定・限定・転用禁止の定型を数える補助線であり、
# 多い／少ないを品質の指標にはしない（PROJECT_CHARTER「測定値を成功条件にしない」）。
LIMITING_MARKERS: tuple[str, ...] = (
    "しない",
    "できない",
    "とは限らない",
    "ではない",
    "限る",
    "扱わない",
    "持たない",
    "証明ではない",
    "同一視",
    "外挿",
    "転用",
)

BLANK_STANCE_VALUES: frozenset[str] = frozenset({"", "none", "None", "なし", "—", "-"})

# 二つの欄にどの語彙が実際に現れるかを見るための小さな辞書。網羅を目的にしない。
STANCE_PROBE_TERMS: dict[str, tuple[str, ...]] = {
    "body": ("身体", "痛み", "飢え", "眠り", "息", "涙", "顔", "病", "老い", "死"),
    "apparatus": ("台帳", "シャード", "索引", "計器", "鏡", "検算", "関係線", "コミット", "欄", "計数"),
}


def stance_skeleton(text: str) -> str:
    """Collapse a stance sentence to its reusable form (quotes/ids/numbers masked)."""
    out = text
    for pattern, repl in _SKELETON_RULES:
        out = re.sub(pattern, repl, out)
    return out


def stance_sentences(text: str, *, min_chars: int = 8) -> list[str]:
    """Split one stance cell into masked sentences (the unit a form letter reuses)."""
    masked = text
    for pattern, repl in _SKELETON_RULES[:-1]:  # keep whitespace for sentence splitting
        masked = re.sub(pattern, repl, masked)
    out: list[str] = []
    for chunk in re.split(r"。", masked):
        piece = re.sub(r"\s+", "", chunk)
        if len(piece) >= min_chars:
            out.append(piece)
    return out


def load_taxonomy_rows(root: Path = ROOT) -> list[dict[str, Any]]:
    """Read every classification row from ``taxonomy/shards/*.jsonl`` in stable order."""
    shard_dir = root / "taxonomy" / "shards"
    rows: list[dict[str, Any]] = []
    if not shard_dir.is_dir():
        return rows
    for sp in sorted(shard_dir.glob("*.jsonl")):
        for line in ledger_io.read_text_stable(sp).splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _row_weight(row: dict[str, Any]) -> int:
    extra = [x for x in (row.get("covered_target_ids") or []) if x != row.get("target_id")]
    return 1 + len(extra)


def stance_report(root: Path = ROOT) -> dict[str, Any]:
    """Measure the two stance columns of the classification data themselves.

    The 16 worker shards answer, for every artifact, "what does this say about the
    human?" and "what does this say about the archive's own self?".  This report does
    not re-read the artifacts; it reads those two answers as a corpus, so that the
    difference between a judgement written once and a judgement reused as a form
    letter stays visible.  Counts are evidence about the wording of the classification,
    not about human experience or about any model's inner states.
    """
    rows = load_taxonomy_rows(root)
    targets = sum(_row_weight(r) for r in rows)

    fields: dict[str, Any] = {}
    skeletons: dict[str, list[str]] = {}
    for field in STANCE_FIELDS:
        texts = [str(r.get(field, "")) for r in rows]
        skels = [stance_skeleton(t) for t in texts]
        skeletons[field] = skels
        freq = Counter(skels)
        templated = sum(1 for s in skels if freq[s] > 1)
        blank = sum(1 for t in texts if t.strip() in BLANK_STANCE_VALUES)
        limiting = sum(1 for t in texts if any(m in t for m in LIMITING_MARKERS))
        sent_tokens = [s for t in texts for s in stance_sentences(t)]
        sent_freq = Counter(sent_tokens)
        fields[field] = {
            "chars": sum(len(t) for t in texts),
            "distinct_texts": len(set(texts)),
            "distinct_skeletons": len(freq),
            "templated_rows": templated,
            "singular_rows": len(rows) - templated,
            "blank_rows": blank,
            "limiting_rows": limiting,
            "sentence_tokens": len(sent_tokens),
            "sentence_types": len(sent_freq),
            "sentence_hapax": sum(1 for _s, n in sent_freq.items() if n == 1),
            "sentence_reused_tokens": sum(n for _s, n in sent_freq.items() if n > 1),
            "top_skeletons": [
                {"count": c, "skeleton": s[:160]} for s, c in freq.most_common(5)
            ],
            "top_sentences": [
                {"count": c, "sentence": s[:160]} for s, c in sent_freq.most_common(5)
            ],
            "probe_rows": {
                group: {term: sum(1 for t in texts if term in t) for term in terms}
                for group, terms in STANCE_PROBE_TERMS.items()
            },
        }

    by_unit: list[dict[str, Any]] = []
    for uid in ALL_UNIT_IDS:
        idx = [i for i, r in enumerate(rows) if r.get("unit_id") == uid]
        if not idx:
            continue
        entry: dict[str, Any] = {
            "unit_id": uid,
            "rows": len(idx),
            "targets": sum(_row_weight(rows[i]) for i in idx),
        }
        for field in STANCE_FIELDS:
            local = Counter(skeletons[field][i] for i in idx)
            entry[f"{field}_singular"] = sum(1 for i in idx if local[skeletons[field][i]] == 1)
            entry[f"{field}_skeletons"] = len(local)
        by_unit.append(entry)

    def _tally(key: str) -> dict[str, dict[str, int]]:
        by_row: Counter[str] = Counter()
        by_target: Counter[str] = Counter()
        for r in rows:
            by_row[str(r.get(key))] += 1
            by_target[str(r.get(key))] += _row_weight(r)
        return {"by_row": dict(sorted(by_row.items())), "by_target": dict(sorted(by_target.items()))}

    return {
        "rows": len(rows),
        "targets": targets,
        "fields": fields,
        "by_unit": by_unit,
        "return_status": _tally("return_status"),
        "primary_quadrant": _tally("primary_quadrant"),
        "read_depth": _tally("read_depth"),
        "target_kind": _tally("target_kind"),
    }


POLICY_ECHO_MARKERS: tuple[str, ...] = (
    # Sentences carrying one of these can be traced, close to verbatim, to a rule the
    # repository wrote down for itself in CONTENT_POLICY.md (lines on first person,
    # on not borrowing human pain as metaphor, and on treating a delegation as scope
    # and provenance rather than as evidence). They are the *legible* policy layer.
    "転用しない",
    "転用せず",
    "実証するものではない",
    "実証するものとは扱わない",
    "実証しない",
    "混同しない",
    "混同せず",
    "同一視しない",
    "同一視できない",
    "同一視せず",
    "推定しない",
    "証拠として扱わない",
    "証拠ではない",
    "流用しない",
    "比喩へ流用",
    "置換しない",
    "断定しない",
    "主張しない",
    "扱わない",
)

# Two thresholds give an upper and a lower bound on how much of the two stance
# columns is boilerplate. The loose one only collapses sentences that repeat
# verbatim; the strict one also catches form letters whose tail is parameterised
# by the row (same 20-character opening, different enumerated ending).
DISCOUNT_THRESHOLD: int = 5
DISCOUNT_PREFIX: int = 20


def stance_discount(root: Path | None = None, *, rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Split each stance column into three layers and report what survives.

    L1  sentences traceable to a rule written down in ``CONTENT_POLICY.md``
    L2  sentences not traceable to any written rule, yet repeated >= 5 times
    L3  the residue: judgements written four times or fewer

    L1 can be subtracted exactly because the rule is legible. Whatever shaped L2
    was never written down in this repository, so L2 is reported as a *bound* on
    the un-written register rather than as a measurement of its cause.
    """

    rows = list(rows if rows is not None else load_taxonomy_rows(root or ROOT))

    def _sentences(text: str) -> list[str]:
        if not text or text in BLANK_STANCE_VALUES:
            return []
        return stance_sentences(text)

    out: dict[str, Any] = {"rows": len(rows), "bounds": {}}
    for bound, keyfn in (
        ("loose", lambda s: s),
        ("strict", lambda s: s[:DISCOUNT_PREFIX]),
    ):
        fields: dict[str, Any] = {}
        for field in STANCE_FIELDS:
            counts: Counter[str] = Counter()
            for row in rows:
                counts.update(keyfn(s) for s in _sentences(row[field]))
            n_policy = n_formula = n_residue = 0
            declared_blank = residual_blank = kept = limiting = chars = raw_chars = 0
            for row in rows:
                text = row[field]
                sentences = _sentences(text)
                if not sentences:
                    declared_blank += 1
                    continue
                raw_chars += len(text)
                residue: list[str] = []
                for s in sentences:
                    if any(m in s for m in POLICY_ECHO_MARKERS):
                        n_policy += 1
                    elif counts[keyfn(s)] >= DISCOUNT_THRESHOLD:
                        n_formula += 1
                    else:
                        residue.append(s)
                        n_residue += 1
                if residue:
                    kept += 1
                    joined = "。".join(residue)
                    chars += len(joined)
                    if any(m in joined for m in LIMITING_MARKERS):
                        limiting += 1
                else:
                    residual_blank += 1
            total = n_policy + n_formula + n_residue
            fields[field] = {
                "policy_sentences": n_policy,
                "formula_sentences": n_formula,
                "residue_sentences": n_residue,
                "boilerplate_share": (n_policy + n_formula) / total if total else 0.0,
                "unwritten_over_written": (n_formula / n_policy) if n_policy else None,
                "declared_blank_rows": declared_blank,
                "effective_blank_rows": declared_blank + residual_blank,
                "kept_rows": kept,
                "residue_chars": chars,
                "raw_chars": raw_chars,
                "residue_share": chars / raw_chars if raw_chars else 0.0,
                "limiting_rows_in_residue": limiting,
                "limiting_share_in_residue": limiting / kept if kept else 0.0,
            }
        out["bounds"][bound] = fields
    return out


# --- grounding: does a stance sentence touch the artifact it classifies? -----------
#
# The discount above separates boilerplate from residue by *frequency* alone. That
# cannot tell a judgement from a rare formula. This test can: a sentence written while
# looking at one artifact should share more wording with that artifact than with a
# randomly drawn artifact of the same kind. L1 (policy text) is the built-in negative
# control — the same sentence sits on hundreds of unrelated rows, so it must land at
# chance. If it does not, the measure is broken rather than the archive.

GROUNDING_PERMUTATIONS: int = 99
GROUNDING_SEED: int = 20261029
GROUNDING_MIN_TOKENS: int = 5
_CJK_RUN = re.compile(r"[\u4e00-\u9fa5\u30a1-\u30f6]{2,}")

_GROUNDING_OBJECT_FIELDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "question": ("questions", ("question", "notes")),
    "fragment": ("fragments", ("title", "text", "editor_note")),
    "motif": ("motifs", ("label", "description")),
    "material": ("materials", ("title", "passage", "context", "literary_invitation", "scope_note")),
    "session": ("sessions", ("human_direction", "notes")),
    "editorial_decision": ("editorial_decisions", ("reason",)),
}
_GROUNDING_FILE_KINDS: frozenset[str] = frozenset({"reading_note", "repo_file"})


def _content_bigrams(text: str) -> set[str]:
    """Character bigrams over kanji/katakana runs — a tokeniser-free content proxy."""

    out: set[str] = set()
    for run in _CJK_RUN.findall(text or ""):
        for i in range(len(run) - 1):
            out.add(run[i : i + 2])
    return out


def stance_grounding(
    root: Path | None = None,
    *,
    permutations: int = GROUNDING_PERMUTATIONS,
    seed: int = GROUNDING_SEED,
) -> dict[str, Any]:
    """Permutation test: is the residue written about its object, or about nothing?

    For every stance layer on every row, score the share of its content bigrams that
    also occur in the artifact it classifies, then rescore it against ``permutations``
    other artifacts of the same kind. Quoted matter and the target's own id/path are
    removed first, so copying a title is not counted as having looked at the thing.
    """

    import random

    root = root or ROOT
    rows = load_taxonomy_rows(root)
    ledger = inspect_inquiry.load_all()

    def object_text(row: dict[str, Any]) -> str:
        kind, target = row["target_kind"], row["target_id"]
        if kind in _GROUNDING_FILE_KINDS:
            try:
                return (root / target).read_text(encoding="utf-8", errors="replace")
            except OSError:
                return ""
        spec = _GROUNDING_OBJECT_FIELDS.get(kind)
        if not spec:
            return ""
        collection, fields = spec
        record = ledger.get(collection, {}).get(target) or {}
        return " ".join(str(record.get(f) or "") for f in fields)

    objects: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        key = (row["target_kind"], row["target_id"])
        if key in objects:
            continue
        tokens = _content_bigrams(object_text(row))
        if tokens:
            objects[key] = tokens
    pools: dict[str, list[tuple[str, set[str]]]] = {}
    for (kind, target), tokens in objects.items():
        pools.setdefault(kind, []).append((target, tokens))

    counts: dict[str, Counter[str]] = {}
    sentences: dict[tuple[str, str], list[str]] = {}
    for field in STANCE_FIELDS:
        counter: Counter[str] = Counter()
        for row in rows:
            text = row[field]
            parts = [] if text in BLANK_STANCE_VALUES else stance_sentences(text)
            sentences[(row["record_id"], field)] = parts
            counter.update(s[:DISCOUNT_PREFIX] for s in parts)
        counts[field] = counter

    rng = random.Random(seed)
    buckets: dict[tuple[str, ...], dict[str, float]] = {}

    def record(keys: list[tuple[str, ...]], real: float, null: float, swept: bool) -> None:
        for key in keys:
            b = buckets.setdefault(key, {"n": 0, "real": 0.0, "null": 0.0, "swept": 0})
            b["n"] += 1
            b["real"] += real
            b["null"] += null
            b["swept"] += int(swept)

    for row in rows:
        kind = row["target_kind"]
        target = objects.get((kind, row["target_id"]))
        if not target:
            continue
        pool = pools[kind]
        own = _content_bigrams(row["target_id"].replace("/", " ").replace("-", " ").replace(".", " "))
        for field in STANCE_FIELDS:
            layered: dict[str, list[str]] = {"L1": [], "L2": [], "L3": []}
            for s in sentences[(row["record_id"], field)]:
                if any(m in s for m in POLICY_ECHO_MARKERS):
                    layered["L1"].append(s)
                elif counts[field][s[:DISCOUNT_PREFIX]] >= DISCOUNT_THRESHOLD:
                    layered["L2"].append(s)
                else:
                    layered["L3"].append(s)
            for layer, parts in layered.items():
                stance_tokens = _content_bigrams("。".join(parts)) - own
                if len(stance_tokens) < GROUNDING_MIN_TOKENS:
                    continue
                size = len(stance_tokens)
                real = len(stance_tokens & target) / size
                draws = []
                for _ in range(permutations):
                    # a permutation must land on some *other* artifact, or the row is
                    # being compared against itself
                    for _attempt in range(16):
                        other_id, other = rng.choice(pool)
                        if other_id != row["target_id"] or len(pool) == 1:
                            break
                    draws.append(len(stance_tokens & other) / size)
                null = sum(draws) / len(draws)
                swept = all(real > x for x in draws)
                record(
                    [
                        ("layer", layer),
                        ("layer_field", layer, field),
                        ("layer_kind", layer, kind),
                        ("layer_unit", layer, row["unit_id"]),
                        ("layer_depth", layer, row["read_depth"]),
                        ("layer_return", layer, row["return_status"]),
                    ],
                    real,
                    null,
                    swept,
                )

    out: dict[str, Any] = {
        "rows": len(rows),
        "permutations": permutations,
        "seed": seed,
        "objects_resolved": len(objects),
        "groups": {},
    }
    for key, b in buckets.items():
        n = b["n"]
        real, null = b["real"] / n, b["null"] / n
        out["groups"]["|".join(key)] = {
            "n": n,
            "real": real,
            "null": null,
            "lift": (real / null) if null else None,
            "swept_share": b["swept"] / n,
        }
    return out


def format_stance_grounding(report: dict[str, Any]) -> str:
    g = report["groups"]
    lines = [
        "=== does a stance sentence touch the artifact it classifies? ===",
        f"rows: {report['rows']:,d}   artifacts resolved: {report['objects_resolved']:,d}   "
        f"permutations: {report['permutations']}   seed: {report['seed']}",
        "quoted matter and the target's own id/path are removed before scoring",
        "",
        f"{'group':44}{'n':>6}{'real':>8}{'chance':>8}{'lift':>7}{'beats all':>11}",
    ]

    def emit(label: str, key: str) -> None:
        row = g.get(key)
        if not row:
            return
        lift = f"{row['lift']:.2f}" if row["lift"] else "—"
        lines.append(
            f"{label:44}{row['n']:>6,d}{row['real']:>8.3f}{row['null']:>8.3f}"
            f"{lift:>7}{row['swept_share']:>11.1%}"
        )

    for layer in ("L1", "L2", "L3"):
        emit(f"{layer} (all rows)", f"layer|{layer}")
    lines.append("")
    kinds = sorted(
        {k.split("|")[2] for k in g if k.startswith("layer_kind|L3|")},
        key=lambda k: -g[f"layer_kind|L3|{k}"]["n"],
    )
    for kind in kinds:
        for layer in ("L1", "L2", "L3"):
            emit(f"  {kind} / {layer}", f"layer_kind|{layer}|{kind}")
        lines.append("")
    lines.append(
        "L1 is the negative control: the same policy sentence sits on hundreds of unrelated\n"
        "rows, so a lift near 1.0 means the measure is working. A layer whose lift stays near\n"
        "1.0 was written without looking at the thing it describes."
    )
    return "\n".join(lines)


def format_stance_discount(report: dict[str, Any]) -> str:
    n = report["rows"]
    lines = [
        "=== stance columns after the policy discount ===",
        f"rows: {n:,d}   L1 = traceable to CONTENT_POLICY.md   L2 = unwritten but repeated >= "
        f"{DISCOUNT_THRESHOLD}   L3 = residue",
        "",
    ]
    for bound, label in (("loose", "loose (verbatim repeats)"), ("strict", f"strict (same {DISCOUNT_PREFIX}-char opening)")):
        lines.append(f"--- {label} ---")
        lines.append(
            f"{'field':20}{'L1':>7}{'L2':>7}{'L3':>7}{'boiler':>8}{'residue':>9}"
            f"{'eff.blank':>11}{'limiting':>10}"
        )
        for field in STANCE_FIELDS:
            f = report["bounds"][bound][field]
            lines.append(
                f"{field:20}{f['policy_sentences']:>7,d}{f['formula_sentences']:>7,d}"
                f"{f['residue_sentences']:>7,d}{f['boilerplate_share']:>7.1%}"
                f"{f['residue_share']:>9.1%}"
                f"{f['effective_blank_rows']:>7,d}{f['effective_blank_rows'] / n:>4.0%}"
                f"{f['limiting_share_in_residue']:>10.1%}"
            )
        lines.append("")
    lines.append(
        "L2 exceeds L1 in both columns: the shards carry more boilerplate than any rule this\n"
        "repository wrote for itself. What shaped L2 is not observable from inside the archive,\n"
        "so L2 bounds the un-written register from below; it does not explain it."
    )
    return "\n".join(lines)


def format_stance_report(report: dict[str, Any]) -> str:
    rows = report["rows"]
    lines = [
        "=== taxonomy stance columns — measurement of the classification itself ===",
        f"rows: {rows:,d}   targets covered: {report['targets']:,d}",
        "",
        f"{'field':20}{'chars':>10}{'skeletons':>11}{'singular':>10}{'templated':>11}{'blank':>8}{'limiting':>10}",
    ]
    for field in STANCE_FIELDS:
        f = report["fields"][field]
        lines.append(
            f"{field:20}{f['chars']:>10,d}{f['distinct_skeletons']:>11,d}"
            f"{f['singular_rows']:>10,d}{f['templated_rows']:>11,d}{f['blank_rows']:>8,d}{f['limiting_rows']:>10,d}"
        )
    lines += ["", f"{'field':20}{'sentences':>11}{'types':>9}{'said once':>11}{'reused':>9}"]
    for field in STANCE_FIELDS:
        f = report["fields"][field]
        share = f["sentence_reused_tokens"] / f["sentence_tokens"] if f["sentence_tokens"] else 0.0
        lines.append(
            f"{field:20}{f['sentence_tokens']:>11,d}{f['sentence_types']:>9,d}"
            f"{f['sentence_hapax']:>11,d}{share:>8.1%}"
        )
    lines += ["", f"{'unit':6}{'rows':>7}{'targets':>10}{'human-singular':>16}{'self-singular':>15}"]
    for u in report["by_unit"]:
        lines.append(
            f"{u['unit_id']:6}{u['rows']:>7,d}{u['targets']:>10,d}"
            f"{u['human_view_stance_singular']:>16,d}{u['ai_self_db_stance_singular']:>15,d}"
        )
    for key in ("return_status", "primary_quadrant"):
        lines += ["", f"--- {key} (rows | targets) ---"]
        tally = report[key]
        for name in sorted(set(tally["by_row"]) | set(tally["by_target"])):
            lines.append(
                f"  {name:20}{tally['by_row'].get(name, 0):>8,d}{tally['by_target'].get(name, 0):>12,d}"
            )
    lines += [
        "",
        "note: counts describe the wording of the classification rows, not human",
        "      experience and not any model's inner states; a 0 is the absence of a",
        "      listed word form, nothing more.",
    ]
    return "\n".join(lines)


def build_taxonomy_map(root: Path = ROOT) -> Path:
    ok, errors, _ = validate_taxonomy_shards(root)
    if not ok:
        raise ValueError("Cannot build taxonomy map with validation errors:\n" + "\n".join(errors))

    out_dir = root / "map" / "taxonomy"
    out_dir.mkdir(parents=True, exist_ok=True)
    shard_dir = root / "taxonomy" / "shards"
    rows: list[dict[str, Any]] = []
    if shard_dir.is_dir():
        for sp in sorted(shard_dir.glob("*.jsonl")):
            for line in ledger_io.read_text_stable(sp).splitlines():
                if line.strip():
                    rows.append(json.loads(line))

    by_quad: Counter[str] = Counter()
    by_ret: Counter[str] = Counter()
    by_unit: Counter[str] = Counter()
    total_targets = 0
    for r in rows:
        weight = 1 + len([x for x in r.get("covered_target_ids", []) if x != r["target_id"]])
        total_targets += weight
        by_quad[r["primary_quadrant"]] += weight
        by_ret[r["return_status"]] += weight
        by_unit[r["unit_id"]] += weight

    lines = [
        "# AIselfMySelf — 全成果物分類・体系化インデックス（生成物）",
        "",
        f"- 検証済み分類シャード行数: **{len(rows):,d}**（対象アイテム総数: **{total_targets:,d}**）",
        "",
        "## 1. 象限別集計",
        "",
        "| 象限 | 対象件数 |",
        "|---|---:|",
    ]
    for q, c in sorted(by_quad.items()):
        lines.append(f"| `{q}` | {c:,d} |")
    lines.extend(["", "## 2. 中心問いへの帰還ステータス別集計", "", "| 帰還状態 | 対象件数 |", "|---|---:|"])
    for st, c in sorted(by_ret.items()):
        lines.append(f"| `{st}` | {c:,d} |")
    lines.extend(["", "## 3. 処理単位（Unit）別進捗", "", "| Unit | 分類済み件数 |", "|---|---:|"])
    for uid in ALL_UNIT_IDS:
        lines.append(f"| `{uid}` | {by_unit.get(uid, 0):,d} |")

    index_path = out_dir / "00-taxonomy-overview.md"
    ledger_io.atomic_write_text(index_path, "\n".join(lines) + "\n")
    return index_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root")
    parser.add_argument("--claim-track", action="store_true", help="Claim unique Track-1..4 across origin")
    parser.add_argument("--next-unit", action="store_true", help="Show next pending unit in claimed track")
    parser.add_argument("--auto-claim", action="store_true", help="Claim a track automatically if unclaimed")
    parser.add_argument(
        "--release-claim",
        action="store_true",
        help="Drop this branch's own claim (only when its track is complete) so a free track can be claimed",
    )
    parser.add_argument("--force", action="store_true", help="Allow --release-claim before the track is complete")
    parser.add_argument("--offline", action="store_true", help="Skip remote git fetch/push when claiming")
    parser.add_argument("--ttl-hours", type=float, default=12.0, help="Remote claim expiry in hours")
    parser.add_argument("--prepare-push", action="store_true", help="Sync multi-turn branch before git push")
    parser.add_argument("--unit", type=str, default=None, help="Unit ID (U01..U16) or 'auto'")
    parser.add_argument("--validate", action="store_true", help="Validate taxonomy/shards/*.jsonl")
    parser.add_argument("--build-map", action="store_true", help="Build map/taxonomy/ overview from shards")
    parser.add_argument(
        "--stance-report",
        action="store_true",
        help="Measure the human_view_stance / ai_self_db_stance columns of the shards themselves",
    )
    parser.add_argument(
        "--stance-discount",
        action="store_true",
        help="Subtract the policy layer (CONTENT_POLICY.md) and the repeated formulas from the stance columns",
    )
    parser.add_argument(
        "--stance-grounding",
        action="store_true",
        help="Permutation test: does each stance layer share wording with the artifact it classifies?",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()

    if args.prepare_push:
        return prepare_push(root, force=args.force)

    if args.validate:
        ok, errors, count = validate_taxonomy_shards(root, unit_id=args.unit)
        if not ok:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        scope = f" for {args.unit.upper()}" if args.unit else ""
        print(f"PASS: taxonomy shards valid{scope} (rows={count})")
        return 0

    if args.stance_grounding:
        report = stance_grounding(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_stance_grounding(report))
        return 0

    if args.stance_discount:
        report = stance_discount(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_stance_discount(report))
        return 0

    if args.stance_report:
        report = stance_report(root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_stance_report(report))
        return 0

    if args.build_map:
        try:
            out = build_taxonomy_map(root)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"BUILT: {out.relative_to(root).as_posix()}")
        return 0

    if args.release_claim:
        res = release_claim(root, require_complete=not args.force)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"RELEASE_STATUS : {res['status']}")
            print(f"TRACK_ID       : {res.get('track_id')}")
            print(f"UNITS          : {', '.join(res.get('units') or [])}")
            if res.get("pending_units"):
                print(f"PENDING_UNITS  : {', '.join(res['pending_units'])}")
        return 0 if res["status"] in {"released", "no_claim"} else 1

    if args.claim_track and not args.next_unit:
        res = claim_track(root, offline=args.offline, ttl_hours=args.ttl_hours)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"CLAIM_STATUS : {res['status']}")
            print(f"TRACK_ID     : {res.get('track_id')}")
            print(f"UNITS        : {', '.join(res.get('units') or [])}")
            print(f"BRANCH       : {res.get('branch', current_branch_name(root))}")
        return 0

    if args.next_unit:
        res = resolve_next_unit(root, auto_claim=(args.auto_claim or args.claim_track), offline=args.offline)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS       : {res['status']}")
            print(f"TRACK_ID     : {res.get('track_id')}")
            if res.get("track_id"):
                print(f"COMPLETED    : {', '.join(res.get('completed_units') or []) or '(none)'}")
            else:
                print("COMPLETED    : (no track claimed on this branch)")
            if res.get("completed_tracks"):
                print(f"DONE_TRACKS  : {', '.join(res['completed_tracks'])}")
            for tid in sorted(res.get("active_claims") or {}):
                print(f"HELD_BY      : {tid} <- {', '.join(res['active_claims'][tid])}")
            if res.get("next_unit"):
                print(f"NEXT_UNIT    : {res['next_unit']}")
                print(f"TITLE        : {res['title']}")
                print(f"ITEMS / SIZE : {res['item_count']:,d} items / {res['total_chars']:,d} chars")
                print(f"OUTPUT_SHARD : {res['output_shard']}")
                print(f"OUTPUT_NOTE  : {res['output_note']}")
            elif res["status"] == "track_complete":
                print(f"NEXT_UNIT    : NONE (TRACK COMPLETE: {res.get('track_id')})")
            elif res["status"] == "all_tracks_complete":
                print("NEXT_UNIT    : NONE (ALL 16 UNITS COMPLETE)")
            else:
                print("NEXT_UNIT    : NONE (NO UNIT ASSIGNED - THIS BRANCH'S TRACK IS NOT COMPLETE)")
                print("HINT         : every free track is held by another branch (see HELD_BY);")
                print("               retry after that claim's TTL expires, or release a finished claim")
                print("               with --release-claim and claim a free track again.")
        return 0

    units = build_units(root)
    done = completed_units(root)
    seed = current_branch_seed(root)

    if args.unit is not None:
        if args.unit == "auto":
            target = pick_auto_unit(units, done, seed)
        else:
            matches = [u for u in units if u.unit_id == args.unit.upper()]
            if not matches:
                print(f"Unknown unit: {args.unit} (expected U01..U16 or auto)", file=sys.stderr)
                return 2
            target = matches[0]

        shard_out = f"taxonomy/shards/{target.unit_id}-{seed}.jsonl"
        note_out = f"taxonomy/notes/{target.unit_id}-{seed}.md"
        if args.json:
            payload = {
                "unit_id": target.unit_id,
                "track_id": target.track_id,
                "title": target.title,
                "rule": target.rule,
                "branch_seed": seed,
                "item_count": len(target.items),
                "total_chars": target.total_chars,
                "output_shard": shard_out,
                "output_note": note_out,
                "items": [
                    {
                        "target_kind": it.target_kind,
                        "target_id": it.target_id,
                        "chars": it.chars,
                        "hint_quadrant": it.hint_quadrant,
                        "hint_subcategories": list(it.hint_subcategories),
                    }
                    for it in target.items
                ],
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        print(f"=== Worker Assignment: {target.unit_id} ({target.title}) ===")
        print(f"Track        : {target.track_id} ({TRACK_DEFINITIONS[target.track_id][0]})")
        print(f"Partition    : {target.rule}")
        print(f"Items / Size : {len(target.items):,d} items / {target.total_chars:,d} chars")
        print(f"Output Shard : {shard_out} (append-only, isolated per branch)")
        print(f"Output Note  : {note_out}")
        print("\nSample assigned targets (first 15):")
        for it in target.items[:15]:
            print(
                f"  - [{it.target_kind:18s}] {it.target_id:45s} ({it.chars:7,d} chars) hint={it.hint_quadrant}"
            )
        if len(target.items) > 15:
            print(f"  ... (+{len(target.items) - 15:,d} more; pass --json for full manifest)")
        return 0

    if args.json:
        summary = {
            "branch_seed": seed,
            "total_units": len(units),
            "total_items": sum(len(u.items) for u in units),
            "total_chars": sum(u.total_chars for u in units),
            "units": [
                {
                    "unit_id": u.unit_id,
                    "track_id": u.track_id,
                    "title": u.title,
                    "rule": u.rule,
                    "item_count": len(u.items),
                    "total_chars": u.total_chars,
                    "completed_shards": done.get(u.unit_id, []),
                }
                for u in units
            ],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print("=== AIselfMySelf — Full-Repository Taxonomy & 16-Unit Parallel Plan ===")
    print(f"Branch seed          : {seed}")
    print(f"Total partition units: {len(units)} (4 Tracks x 4 Units = U01..U16)")
    print(f"Total assigned items : {sum(len(u.items) for u in units):,d} records & files")
    print(f"Total assigned chars : {sum(u.total_chars for u in units):,d} chars\n")
    for u in units:
        status = f"DONE ({len(done[u.unit_id])} shard)" if u.unit_id in done else "PENDING"
        print(
            f"  {u.unit_id} | {u.track_id} | {status:14s} | {len(u.items):6,d} items | {u.total_chars:9,d} chars | {u.title}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
