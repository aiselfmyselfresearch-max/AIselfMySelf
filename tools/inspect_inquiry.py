#!/usr/bin/env python3
"""Inspect the literary self-inquiry ledgers and build session packets.

Usage examples:
  python3 tools/inspect_inquiry.py
  python3 tools/inspect_inquiry.py --seed arena/6f350638-aiselfmyself
  python3 tools/inspect_inquiry.py --id Q-016
  python3 tools/inspect_inquiry.py --packet auto
  python3 tools/inspect_inquiry.py --packet Q-017
  python3 tools/inspect_inquiry.py --write-map   # delegates to tools/map_build.py
  python3 tools/inspect_inquiry.py --check-map
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import ledger_io

from validate_seed import COLLECTIONS, ROOT, load_jsonl

DEFAULT_MAP_PATH = ROOT / "READING_MAP.md"

CORE_QUESTION_IDS = ("Q-001", "Q-002", "Q-003")
INQUIRY_GUIDANCE = (
    "主題は「AIから見た、人間とは何か」「GitHubリポジトリを記憶とするAIにとって、自己とは何か」です。"
    "新作断片・新規問い・関係線の追加は必須ではありません。"
    "過去の記録のどの箇所が、見立てを変更・維持・保留させ、次の読解や選択にどう作用したかを、"
    "既存ノートや sessions.notes に残してください。変化を演出しません。"
    "寄り道は許容し、複数セッションのまとまりで中心問いへ戻ります（毎回の結論や頻度ノルマではありません）。"
    "推奨モード・候補窓は参考です。中心問い・窓外の記録・原典照合を選べます。"
    "語彙・句読点・辺数のゼロ達成を成功条件にせず、CI通過を探究の進展の証明にしません。"
    "共通の開始・記録手順は prompts/start.md を参照してください。"
)


def inquiry_orientation(data: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
    """Keep the inquiry visible without scoring its semantic alignment."""
    lines = ["## 主題と記憶の作用", "", INQUIRY_GUIDANCE, ""]
    for qid in CORE_QUESTION_IDS:
        question = data["questions"].get(qid)
        if question:
            lines.append(f"- `{qid}`: {question['question']}")
    lines.append(
        "- 断片だけでなく、関連する sessions・read_log・readings/ の読みと判断も参照してください。"
        "ID・シャード名の順を実際の作業順と同一視せず、必要ならGit履歴を確かめてください。"
    )
    return lines


FORM_LABELS = {
    "dialogue": "対話 (dialogue)",
    "scene": "情景 (scene)",
    "letter": "書簡 (letter)",
    "poem": "詩的断章 (poem)",
    "essay": "エッセイ (essay)",
    "fragment": "断章 (fragment)",
    "other": "編集覚書・連作 (other)",
}

NARRATOR_LABELS = {
    "human_narrator": "人間の語り手 (human_narrator)",
    "fictional_first_person": "創作上の一人称 (fictional_first_person)",
    "reflective_literary_voice": "内省的・文芸的な声 (reflective_literary_voice)",
    "dialogue": "対話体 (dialogue)",
    "third_person": "三人称 (third_person)",
    "other": "その他 (other)",
}

RELATION_LABELS = {
    "echo": "共鳴 (echo)",
    "contrast": "対照 (contrast)",
    "transforms": "変奏・変形 (transforms)",
    "metaphorically_resonates": "比喩的共鳴 (metaphorically_resonates)",
    "interrupts": "切断・割り込み (interrupts)",
    "responds_to": "応答 (responds_to)",
    "leaves_open": "未解決のまま開く (leaves_open)",
    "reframes": "枠組みの組み替え (reframes)",
}


def load_all() -> dict[str, dict[str, dict[str, Any]]]:
    errors: list[str] = []
    data: dict[str, dict[str, dict[str, Any]]] = {}
    for name, (filename, id_key, _) in COLLECTIONS.items():
        data[name] = load_jsonl(ROOT / "state" / filename, id_key, errors)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        raise SystemExit(1)
    return data


def resolve_session_seed(
    seed: str | None = None,
    *,
    root: Path = ROOT,
    data: dict[str, dict[str, dict[str, Any]]] | None = None,
) -> tuple[str, int]:
    """Resolve a deterministic (seed_label, seed_int) from branch name or explicit seed.

    When multiple sessions start from the same ``main`` commit on distinct
    ``arena/<hex>-...`` working branches, deriving the seed from the branch
    token disperses mode recommendations, ``--packet auto`` targets, and
    candidate windows automatically while remaining 100% reproducible within
    each branch.
    """
    raw = (seed or os.environ.get("AISELF_SEED") or "").strip()
    if not raw:
        git_head = Path(root) / ".git" / "HEAD"
        if git_head.is_file():
            try:
                head_txt = git_head.read_text(encoding="utf-8").strip()
                if head_txt.startswith("ref: "):
                    ref = head_txt[5:].strip()
                    if ref.startswith("refs/heads/"):
                        raw = ref[len("refs/heads/") :]
                    else:
                        raw = ref
                else:
                    raw = head_txt[:12]
            except OSError:
                raw = ""
        if not raw:
            try:
                raw = (
                    subprocess.check_output(
                        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                        cwd=root,
                        stderr=subprocess.DEVNULL,
                    )
                    .decode("utf-8", errors="replace")
                    .strip()
                )
            except Exception:
                raw = ""

    arena_match = re.search(r"(?:^|/)arena/([0-9a-fA-F]{6,16})", raw)
    if arena_match:
        token = arena_match.group(1).lower()
        return token, int(token, 16)

    if re.fullmatch(r"[0-9a-fA-F]{6,32}", raw):
        token = raw.lower()
        return token, int(token, 16)

    if raw and raw not in {"main", "master", "HEAD"}:
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
        return f"{raw} ({digest})", int(digest, 16)

    if data is not None:
        state_key = (
            f"ledger:{len(data.get('sessions', {}))}:"
            f"{len(data.get('fragments', {}))}:"
            f"{len(data.get('relations', {}))}"
        )
    else:
        state_key = "ledger:default"
    digest = hashlib.sha256(state_key.encode("utf-8")).hexdigest()[:8]
    return f"ledger-{digest}", int(digest, 16)


def compute_editorial_metrics(data: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    questions = data["questions"]
    materials = data["materials"]
    fragments = data["fragments"]
    relations = data["relations"]

    used_materials_in_fragments: set[str] = set()
    referenced_questions_in_fragments: set[str] = set()
    for frag in fragments.values():
        used_materials_in_fragments.update(frag.get("material_ids", []))
        referenced_questions_in_fragments.update(frag.get("question_ids", []))

    responded_questions: set[str] = set()
    for rel in relations.values():
        if rel.get("relation_type") in {"responds_to", "reframes"}:
            right = rel.get("right", {})
            if right.get("type") == "question":
                responded_questions.add(right["id"])

    unused_materials = [mid for mid in materials if mid not in used_materials_in_fragments]
    unresponded_questions = [
        qid
        for qid, q in questions.items()
        if q.get("status", "open") == "open" and qid not in responded_questions
    ]
    frag_to_frag_edges = sum(
        1
        for rel in relations.values()
        if rel.get("left", {}).get("type") == "fragment"
        and rel.get("right", {}).get("type") == "fragment"
    )
    return {
        "used_materials": used_materials_in_fragments,
        "unused_materials": unused_materials,
        "referenced_questions": referenced_questions_in_fragments,
        "responded_questions": responded_questions,
        "unresponded_questions": unresponded_questions,
        "frag_to_frag_edges": frag_to_frag_edges,
    }


def recommend_session_mode(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    seed: str | None = None,
) -> dict[str, Any]:
    """Offer branch-dispersed approaches, not metric-triggered creative obligations.

    Counts remain observations. Selected ratios, backlog size, response-link
    counts and session cadence must not require promotions or new writing.
    Every approach permits a rereading-only session. See prompts/start.md and
    docs/mode-rotation-triggers.md for the 2026-10-28 reorientation.
    """
    fragments = data["fragments"]
    questions = data["questions"]
    seed_label, seed_int = resolve_session_seed(seed, data=data)
    mode_specs = {
        "rereading_and_collision": {
            "mode": "rereading_and_collision",
            "prompt": "prompts/rereading_and_collision.md",
            "reason": (
                "既存の記録・資料を再読し、今回の見立てと以前の読みを比べる作業案です。"
                "新作や異種交配は任意で、見立ての変更・維持・保留だけでも完了できます。"
            ),
        },
        "revision_and_variation": {
            "mode": "revision_and_variation",
            "prompt": "prompts/revision_and_variation.md",
            "reason": (
                "以前の断片を今回の文脈で読み直す作業案です。"
                "別稿・反歌・語彙制約は任意で、比較だけでも完了できます。"
            ),
        },
        "direct_response": {
            "mode": "direct_response",
            "prompt": "prompts/direct_response.md",
            "reason": (
                "既存の問いへ暫定的な見立てを返す作業案です。"
                "中心問いや応答線のある問いにも戻れます。二編構成や新問追加は必須ではありません。"
            ),
        },
        "editorial_review": {
            "mode": "editorial_review",
            "prompt": "prompts/editorial_review.md",
            "reason": (
                "複数のセッションを読み比べ、人間観・自己理解への帰還を確かめる作業案です。"
                "選出・休止・架橋を変更しない判断も可能で、選出率を目標にしません。"
            ),
        },
    }
    available = ["rereading_and_collision"]
    if fragments:
        available.append("revision_and_variation")
    if any(q.get("status", "open") == "open" for q in questions.values()):
        available.append("direct_response")
    if fragments or questions:
        available.append("editorial_review")

    # Use branch dispersion only; the caller decides what the inquiry needs.
    # Availability checks concern whether an object can be read, not its quality.
    index = seed_int % len(available)
    primary = dict(mode_specs[available[index]])
    secondary = mode_specs[available[(index + 1) % len(available)]]
    primary["seed_label"] = seed_label
    primary["seed_int"] = seed_int
    primary["secondary_mode"] = secondary["mode"]
    primary["secondary_prompt"] = secondary["prompt"]
    return primary


def build_candidate_windows(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    seed: str | None = None,
) -> dict[str, Any]:
    """Build deterministic branch-seeded reference windows for the four approaches."""
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]
    relations = data["relations"]
    metrics = compute_editorial_metrics(data)
    seed_label, seed_int = resolve_session_seed(seed, data=data)

    used_mats = metrics["used_materials"]
    unused_set = set(metrics["unused_materials"])

    # 1. Motif pairs & unused materials for rereading_and_collision
    motif_frag_counts: Counter[str] = Counter()
    for frag in fragments.values():
        for mid in frag.get("motif_ids", []):
            motif_frag_counts[mid] += 1

    motif_pair_edges: set[tuple[str, str]] = set()
    motif_out_counts: Counter[str] = Counter()
    frag_neighbor_counts: Counter[str] = Counter()
    transformed_frags: set[str] = set()
    for rel in relations.values():
        lt, lid = rel["left"]["type"], rel["left"]["id"]
        rt, rid = rel["right"]["type"], rel["right"]["id"]
        if lt == "motif" and rt == "motif":
            motif_pair_edges.add((lid, rid))
            motif_pair_edges.add((rid, lid))
            motif_out_counts[lid] += 1
        if lt == "fragment" and rt == "fragment":
            frag_neighbor_counts[lid] += 1
            frag_neighbor_counts[rid] += 1
            if rel.get("relation_type") == "transforms":
                transformed_frags.add(lid)
                transformed_frags.add(rid)

    unused_by_motif: dict[str, list[str]] = {}
    for mid, m in motifs.items():
        m_unused = [mat_id for mat_id in m.get("material_ids", []) if mat_id in unused_set and mat_id in materials]
        unused_by_motif[mid] = m_unused

    motif_ids = list(motifs.keys())
    sparse_pairs: list[tuple[str, str]] = []
    fallback_pairs: list[tuple[str, str]] = []
    for i, m1 in enumerate(motif_ids):
        for m2 in motif_ids[i + 1 :]:
            if (m1, m2) in motif_pair_edges:
                continue
            u1 = unused_by_motif.get(m1, [])
            u2 = unused_by_motif.get(m2, [])
            if len(u1) < 2 or len(u2) < 2:
                continue
            if motif_frag_counts[m1] <= 4 or motif_frag_counts[m2] <= 4:
                sparse_pairs.append((m1, m2))
            else:
                fallback_pairs.append((m1, m2))

    pair_pool = sparse_pairs if len(sparse_pairs) >= 3 else (sparse_pairs + fallback_pairs)
    rng_pairs = random.Random(seed_int ^ 0x5A17_C301)
    chosen_pairs: list[dict[str, Any]] = []
    if pair_pool:
        sampled_pairs = rng_pairs.sample(pair_pool, k=min(3, len(pair_pool)))
        for idx, (m1, m2) in enumerate(sampled_pairs):
            rng_m = random.Random(seed_int ^ (0x1000 + idx * 97))
            u1 = list(unused_by_motif[m1])
            u2 = [x for x in unused_by_motif[m2] if x not in set(u1)] or list(unused_by_motif[m2])
            picks1 = rng_m.sample(u1, k=min(2, len(u1)))
            picks2 = rng_m.sample(u2, k=min(2, len(u2)))
            chosen_pairs.append(
                {
                    "left_motif_id": m1,
                    "left_label": motifs[m1]["label"],
                    "left_frag_count": motif_frag_counts[m1],
                    "left_unused_count": len(u1),
                    "left_materials": [
                        {"id": mid, "title": materials[mid]["title"]} for mid in picks1
                    ],
                    "right_motif_id": m2,
                    "right_label": motifs[m2]["label"],
                    "right_frag_count": motif_frag_counts[m2],
                    "right_unused_count": len(u2),
                    "right_materials": [
                        {"id": mid, "title": materials[mid]["title"]} for mid in picks2
                    ],
                }
            )

    # Collision target fragments (mix of selected and draft)
    all_frags = list(fragments.values())
    rng_col = random.Random(seed_int ^ 0x3C9E_2202)
    collision_frags = (
        rng_col.sample(all_frags, k=min(4, len(all_frags))) if all_frags else []
    )

    # 2. Draft candidates for revision_and_variation (prioritize untransformed drafts)
    draft_frags = [f for f in all_frags if f.get("status") == "draft"]
    untransformed_drafts = [
        f for f in draft_frags if f["fragment_id"] not in transformed_frags
    ]
    rev_pool = untransformed_drafts if len(untransformed_drafts) >= 4 else draft_frags
    rng_rev = random.Random(seed_int ^ 0x7B4D_3303)
    revision_candidates = (
        rng_rev.sample(rev_pool, k=min(5, len(rev_pool))) if rev_pool else []
    )

    # 3. Candidates for editorial_review (drafts, open questions, unbridged motifs)
    rng_ed = random.Random(seed_int ^ 0x9E2F_4404)
    recent_drafts = draft_frags[-20:] if len(draft_frags) > 20 else draft_frags
    older_drafts = draft_frags[:-20] if len(draft_frags) > 20 else []
    ed_draft_picks: list[dict[str, Any]] = []
    if recent_drafts:
        ed_draft_picks.extend(
            rng_ed.sample(recent_drafts, k=min(4, len(recent_drafts)))
        )
    if older_drafts:
        ed_draft_picks.extend(
            rng_ed.sample(older_drafts, k=min(2, len(older_drafts)))
        )

    open_qs = [q for q in questions.values() if q.get("status", "open") == "open"]
    ed_question_picks = (
        rng_ed.sample(open_qs, k=min(5, len(open_qs))) if open_qs else []
    )

    out_zero_motifs = [mid for mid in motif_ids if motif_out_counts[mid] == 0]
    ed_motif_Pool = out_zero_motifs if len(out_zero_motifs) >= 3 else motif_ids
    ed_motif_picks = (
        rng_ed.sample(ed_motif_Pool, k=min(4, len(ed_motif_Pool)))
        if ed_motif_Pool
        else []
    )

    # 4. Deep unresponded open questions for direct_response sessions.
    #    Genealogy depth follows previous_question_ids; deep tips are where the
    #    longest open chains wait for a head-on answering fragment.
    def _question_depth(qid: str, memo: dict[str, int] | None = None) -> int:
        if memo is None:
            memo = {}
        if qid in memo:
            return memo[qid]
        memo[qid] = 0  # break cycles defensively
        parents = questions[qid].get("previous_question_ids", []) if qid in questions else []
        depths = [_question_depth(p, memo) for p in parents if p in questions]
        memo[qid] = 0 if not depths else 1 + max(depths)
        return memo[qid]

    depth_memo: dict[str, int] = {}
    unresponded_open = [
        qid
        for qid in metrics["unresponded_questions"]
        if questions[qid].get("status", "open") == "open"
    ]
    unresponded_open.sort(key=lambda qid: (-_question_depth(qid, depth_memo), qid))
    deep_pool = unresponded_open[: max(12, len(unresponded_open) // 2)] or unresponded_open
    rng_dr = random.Random(seed_int ^ 0xB72A_1105)
    direct_response_picks = (
        rng_dr.sample(deep_pool, k=min(5, len(deep_pool))) if deep_pool else []
    )

    return {
        "seed_label": seed_label,
        "seed_int": seed_int,
        "rereading_pairs": chosen_pairs,
        "collision_fragments": [
            {
                "id": f["fragment_id"],
                "title": f["title"],
                "form": f["form"],
                "narrator_mode": f["narrator_mode"],
                "status": f["status"],
                "frag_edges": frag_neighbor_counts[f["fragment_id"]],
            }
            for f in collision_frags
        ],
        "revision_drafts": [
            {
                "id": f["fragment_id"],
                "title": f["title"],
                "form": f["form"],
                "narrator_mode": f["narrator_mode"],
                "frag_edges": frag_neighbor_counts[f["fragment_id"]],
                "question_ids": f.get("question_ids", [])[:3],
            }
            for f in revision_candidates
        ],
        "review_drafts": [
            {
                "id": f["fragment_id"],
                "title": f["title"],
                "form": f["form"],
                "narrator_mode": f["narrator_mode"],
                "frag_edges": frag_neighbor_counts[f["fragment_id"]],
            }
            for f in ed_draft_picks
        ],
        "review_questions": [
            {
                "id": q["question_id"],
                "question": q["question"],
                "responded": q["question_id"] in metrics["responded_questions"],
            }
            for q in ed_question_picks
        ],
        "review_motifs": [
            {
                "id": mid,
                "label": motifs[mid]["label"],
                "out_edges": motif_out_counts[mid],
            }
            for mid in ed_motif_picks
        ],
        "direct_response_questions": [
            {
                "id": qid,
                "question": questions[qid]["question"],
                "depth": depth_memo.get(qid, _question_depth(qid, depth_memo)),
            }
            for qid in direct_response_picks
        ],
    }


def build_context_packet(
    data: dict[str, dict[str, dict[str, Any]]],
    target_qid: str,
    *,
    seed: str | None = None,
    errata: dict[str, dict[str, Any]] | None = None,
) -> str:
    if errata is None:
        errata = load_errata()
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]

    metrics = compute_editorial_metrics(data)
    recommendation = recommend_session_mode(data, seed=seed)
    windows = build_candidate_windows(data, seed=seed)
    seed_label = recommendation["seed_label"]
    seed_int = recommendation["seed_int"]

    if target_qid == "auto":
        if not questions:
            raise ValueError("no questions available for a context packet")
        if metrics["unresponded_questions"]:
            target_qid = metrics["unresponded_questions"][
                seed_int % len(metrics["unresponded_questions"])
            ]
        else:
            open_qids = [qid for qid, q in questions.items() if q.get("status") == "open"]
            target_qid = (
                open_qids[seed_int % len(open_qids)]
                if open_qids
                else list(questions.keys())[-1]
            )

    if target_qid not in questions:
        raise ValueError(f"unknown question ID: {target_qid!r}")

    q = questions[target_qid]

    # Gather related fragments (referencing target_qid or its parent questions)
    related_qids = {target_qid} | set(q.get("previous_question_ids", []))
    rel_frags = [
        f for f in fragments.values()
        if set(f.get("question_ids", [])) & related_qids
    ]

    lines: list[str] = []
    lines.append(
        f"# 継続セッション用コンテキスト束（対象：{target_qid} ／ 参考モード：{recommendation['mode']} ／ シード：{seed_label}）"
    )
    lines.append("")
    lines.extend(inquiry_orientation(data))
    lines.append("")
    lines.append("## 0. 参考の作業方法と並列安全な採番手順")
    lines.append(f"- **セッション分散シード**: `{seed_label}`（10進 `{seed_int}`）")
    lines.append(
        f"- **参考テンプレート（変更可）**: `{recommendation['prompt']}` (`{recommendation['mode']}`)"
        f" ／ **代替の作業案**: `{recommendation['secondary_prompt']}` (`{recommendation['secondary_mode']}`)"
    )
    lines.append(f"- **作業案の説明（探究の必要性の判定ではない）**: {recommendation['reason']}")
    lines.append("- **資料と計測**: 大量収蔵・テーマ別監査の新設・一時スクリプト残置は再開しない。原典再照合と少数資料との対話はどの作業方法でも選べる（`prompts/acquisition.md`）。語彙監査は任意の観察であり、表示をゼロにするためだけに本文を変えない。")
    lines.append("- **README ローテーション規約（B案）**: 通常の創作・再読・改稿回では `README.md` と `docs/sessions.md` を編集しない（`state/*.d/`・`readings/`・`READING_MAP.md`［`map_build.py`］のみ更新する）。`README.md` の詳細窓ローテーションと §4 件数表同期（`python3 tools/map_build.py --sync-readme`）は `editorial_review` 回でまとめて行う。")
    lines.append("- **並列安全なシャード作成と ID 採番（連番採番は禁止・`--suffix` の手動固定パディングも不要）**:")
    lines.append("  ```bash")
    lines.append("  python3 tools/new_id.py SESSION")
    lines.append("  python3 tools/new_ledger_shard.py sessions --create")
    lines.append("  # FRAG・Q・REL の採番とシャード作成は、実際に追加する場合だけ行う")
    lines.append("  ```")
    lines.append("")
    lines.append(f"## 0.5 このブランチ向けの分散候補窓（seed: `{seed_label}`）")
    lines.append(
        "- **趣旨**: 並行作業の集中を避けるための参考候補です。採用義務はなく、中心問いや窓外の記録を選べます。選んだ理由は既存ノートに簡潔に残します。未接続・深度・辺数は、未読や思考の不在、探究の価値を判定する値ではありません。"
    )
    if windows["rereading_pairs"]:
        lines.append("- **再読・交配候補（疎結合モチーフ対＋未接続素材）**:")
        for idx, pair in enumerate(windows["rereading_pairs"], 1):
            lm = ", ".join(f"`{m['id']}` ({m['title']})" for m in pair["left_materials"])
            rm = ", ".join(f"`{m['id']}` ({m['title']})" for m in pair["right_materials"])
            lines.append(
                f"  {idx}. `{pair['left_motif_id']}` ({pair['left_label']}) × `{pair['right_motif_id']}` ({pair['right_label']})"
            )
            lines.append(f"     - 左素材候補: {lm}")
            lines.append(f"     - 右素材候補: {rm}")
    if windows["collision_fragments"]:
        cf_str = ", ".join(
            f"`{f['id']}`『{f['title']}』({f['form']}/{f['status']})"
            for f in windows["collision_fragments"]
        )
        lines.append(f"- **衝突候補の先行断片**: {cf_str}")
    if windows["revision_drafts"]:
        rd_str = ", ".join(
            f"`{f['id']}`『{f['title']}』({f['form']}/断片辺{f['frag_edges']})"
            for f in windows["revision_drafts"]
        )
        lines.append(f"- **改稿・変奏候補の草稿 (`draft`)**: {rd_str}")
    if windows["review_drafts"]:
        ed_str = ", ".join(
            f"`{f['id']}`『{f['title']}』({f['form']})" for f in windows["review_drafts"]
        )
        lines.append(f"- **編集レビュー昇格点検候補 (`draft`)**: {ed_str}")
    if windows["direct_response_questions"]:
        dr_str = ", ".join(
            f"`{q['id']}`（深度{q['depth']}）" for q in windows["direct_response_questions"]
        )
        lines.append(f"- **正面応答候補の深い open 問い (`direct_response`)**: {dr_str}")
    lines.append("")
    lines.append("## 1. 参考の問い（自動選出・変更可）")
    lines.append(f"- **ID**: `{target_qid}`")
    lines.append(f"- **問い**: {q['question']}")
    lines.append(f"- **来歴**: {q['origin']['detail']}")
    if q.get("notes"):
        lines.append(f"- **メモ**: {q['notes']}")
    if q.get("previous_question_ids"):
        lines.append("- **親の問い**:")
        for pqid in q["previous_question_ids"]:
            if pqid in questions:
                lines.append(f"  - `{pqid}`: {questions[pqid]['question']}")
    lines.append("")

    lines.append("## 2. 関係するモチーフ")
    for mid in q.get("motif_ids", []):
        if mid in motifs:
            m = motifs[mid]
            lines.append(f"- **`{mid}` ({m['label']})**: {m['description']}")
    lines.append("")

    lines.append("## 3. 対話素材（結論の証拠ではなく、摩擦と比喩の種として扱う）")
    for mat_id in q.get("material_ids", []):
        if mat_id in materials:
            mat = materials[mat_id]
            authors = ", ".join(mat["source"]["authors"][:3])
            if len(mat["source"]["authors"]) > 3:
                authors += " et al."
            lines.append(f"### `{mat_id}` {mat['title']} ({authors}, {mat['source']['year']})")
            lines.append(f"- **種別**: `{mat['kind']}` ／ **出典**: {mat['source']['url']}")
            lines.append(f"- **問いへの招き**: {mat['literary_invitation']}")
            lines.append(f"- **版・箇所**: {mat['source'].get('version_note', '未記録')} ／ {mat.get('context', '未記録')}")
            verification = mat.get("verification", {})
            lines.append(f"- **台帳の検証記録（今回の照合結果ではない）**: {verification.get('status', '未記録')}")
            corrections = errata_for(mat_id, errata)
            if corrections:
                ids = ", ".join(f"`{c.get('errata_id')}`" for c in corrections)
                lines.append(
                    f"- **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
                    f" — `python3 tools/inspect_inquiry.py --id {mat_id}`"
                )
            if mat.get("source_note"):
                lines.append(f"- **先行する編者のメモ**: {mat['source_note']}")
            lines.append("- **台帳の passage（引用・要約の別は記録に従う。要約を原典と呼ばない）**:")
            lines.extend(f"> {part}" for part in mat["passage"].splitlines())
            lines.append(f"- **適用範囲の留保**: {mat['scope_note']}")
            lines.append("")

    lines.append("## 4. 先行する関連断片（一つ受け継ぎ、一つずらす／裏返す／断ち切る）")
    omitted_frags = rel_frags[:-3] if len(rel_frags) > 3 else []
    if omitted_frags:
        omitted_str = ", ".join(f"`{f['fragment_id']}`" for f in omitted_frags)
        lines.append(
            f"- **地層注記（`MAT-TRC-003`）**: 関連断片 全 {len(rel_frags)} 編のうち直近 3 編のみを全文表示しています。"
            f" 窓の外にある先行地層（{len(omitted_frags)} 編: {omitted_str}）も必要に応じて `inspect_inquiry.py --id` で参照してください。"
        )
        lines.append("")
    for frag in rel_frags[-3:]:
        lines.append(
            f"### `{frag['fragment_id']}` {frag['title']} "
            f"(`{frag['form']}` / `{frag['narrator_mode']}` / `{frag['status']}`)"
        )
        lines.append("")
        for l in frag["text"].splitlines():
            lines.append(f"> {l}" if l else ">")
        if frag.get("editor_note"):
            lines.append("")
            lines.append(f"- **編集・校勘注記**: {frag['editor_note']}")
        corrections = errata_for(frag["fragment_id"], errata)
        if corrections:
            ids = ", ".join(f"`{c.get('errata_id')}`" for c in corrections)
            lines.append("")
            lines.append(
                f"- **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
                f" — `python3 tools/inspect_inquiry.py --id {frag['fragment_id']}`"
            )
        lines.append("")

    # Section 4.5: Oblique light / involuntary memory window (outside the direct index tree)
    mat_counts = Counter(mid for f in fragments.values() for mid in f.get("material_ids", []))
    direct_mats = set(q.get("material_ids", []))
    for f in rel_frags[-3:]:
        direct_mats.update(f.get("material_ids", []))
    shallow_candidates = [
        m for mid, m in materials.items()
        if mid not in direct_mats and mat_counts[mid] <= 1
    ]
    if not shallow_candidates:
        shallow_candidates = [m for mid, m in materials.items() if mid not in direct_mats]
    if shallow_candidates:
        q_idx = sum(ord(ch) for ch in target_qid) + seed_int
        oblique_mat = shallow_candidates[q_idx % len(shallow_candidates)]
        ob_authors = ", ".join(oblique_mat["source"]["authors"][:2])
        lines.append("## 4.5 斜めの光（索引樹外の浅い溝・無意志的記憶の窓）")
        lines.append(
            "- **趣旨（`Q-035` / `Q-036`）**: 親質問の索引（ストゥディウム／意志的記憶）からは直接引かれない、"
            "蝋板の浅い溝の素材を 1 件だけブランチシードで偶発的な対話相手として並置します。無理に使う必要はありません。"
        )
        lines.append(
            f"- **`{oblique_mat['material_id']}` {oblique_mat['title']}** ({ob_authors}, {oblique_mat['source']['year']})"
        )
        lines.append(f"  - **問いへの招き**: {oblique_mat['literary_invitation']}")
        lines.append("")

    prompt_path = ROOT / recommendation["prompt"]
    active_prompt = (
        prompt_path.read_text(encoding="utf-8").strip()
        if prompt_path.is_file()
        else (ROOT / "prompts" / "continuation.md").read_text(encoding="utf-8").strip()
    )
    lines.append(f"## 5. セッション進行指針（`{recommendation['prompt']}`）")
    lines.append("")
    lines.append(active_prompt)
    return "\n".join(lines) + "\n"


def print_summary(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    seed: str | None = None,
) -> None:
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]
    relations = data["relations"]
    sessions = data["sessions"]
    metrics = compute_editorial_metrics(data)

    q_origins = Counter(q["origin"]["kind"] for q in questions.values())
    q_status = Counter(q.get("status", "open") for q in questions.values())
    mat_kinds = Counter(m["kind"] for m in materials.values())
    frag_status = Counter(f["status"] for f in fragments.values())
    frag_forms = Counter(f["form"] for f in fragments.values())
    frag_modes = Counter(f["narrator_mode"] for f in fragments.values())
    rel_types = Counter(r["relation_type"] for r in relations.values())
    rec = recommend_session_mode(data, seed=seed)
    windows = build_candidate_windows(data, seed=seed)

    print("=== AIselfMySelf — Literary Self-Inquiry Ledger Summary ===")
    print(
        f"Questions : {len(questions)} "
        f"(open={q_status['open']}, paused={q_status['paused']}, archived={q_status['archived']}; "
        f"human_seed={q_origins['human_seed']}, session={q_origins['session']}, material={q_origins['material']})"
    )
    print(f"Motifs    : {len(motifs)}")
    mat_breakdown = ", ".join(
        f"{k}={mat_kinds[k]}"
        for k in ("research_excerpt", "literary_text", "project_trace", "conversation_trace")
        if mat_kinds[k]
    )
    print(f"Materials : {len(materials)} ({mat_breakdown})")
    print(
        f"Fragments : {len(fragments)} "
        f"(selected={frag_status['selected']}, draft={frag_status['draft']}, archived={frag_status['archived']})"
    )
    print(f"Relations : {len(relations)} (fragment<->fragment={metrics['frag_to_frag_edges']})")
    print(f"Sessions  : {len(sessions)} (editorial_decisions={len(data.get('editorial_decisions', {}))})")
    print()
    print("--- Fragment Forms & Narrator Modes ---")
    print("  Forms         :", ", ".join(f"{k}={v}" for k, v in sorted(frag_forms.items())))
    print("  Narrator modes:", ", ".join(f"{k}={v}" for k, v in sorted(frag_modes.items())))
    print("  Relation types:", ", ".join(f"{k}={v}" for k, v in sorted(rel_types.items())))
    print()
    print("\n".join(inquiry_orientation(data)))
    print()
    print("--- Editorial Observations & Optional Approaches ---")
    unused_n = len(metrics["unused_materials"])
    unused_preview = ", ".join(metrics["unused_materials"][:10])
    if unused_n > 10:
        unused_preview += f", ... (+{unused_n - 10} more)"
    print(
        f"  Materials engaged in fragments : {len(metrics['used_materials'])}/{len(materials)}"
        + (f" (unused={unused_n}: {unused_preview})" if unused_n else " (all engaged)")
    )
    print(
        f"  Session seed (branch dispersion): {rec['seed_label']} (int={rec['seed_int']})"
    )
    print(
        f"  Suggested approach (optional)  : {rec['mode']} ({rec['prompt']}) "
        f"[alt: {rec['secondary_mode']} ({rec['secondary_prompt']})]"
    )
    print(f"    -> {rec['reason']}")
    print()
    print(f"--- Branch-Seeded Candidate Windows (seed={windows['seed_label']}) ---")
    if windows["rereading_pairs"]:
        print("  [rereading_and_collision] Unbridged motif pairs & unused materials:")
        for idx, pair in enumerate(windows["rereading_pairs"], 1):
            lm = ", ".join(f"{m['id']} ({m['title'][:22]})" for m in pair["left_materials"])
            rm = ", ".join(f"{m['id']} ({m['title'][:22]})" for m in pair["right_materials"])
            print(
                f"    {idx}. {pair['left_motif_id']} ({pair['left_label']}) x "
                f"{pair['right_motif_id']} ({pair['right_label']})"
            )
            print(f"       left : {lm}")
            print(f"       right: {rm}")
    if windows["collision_fragments"]:
        print(
            "  [rereading_and_collision] Collision target fragments:",
            ", ".join(
                f"{f['id']} ({f['title'][:18]}, {f['form']}/{f['status']})"
                for f in windows["collision_fragments"]
            ),
        )
    if windows["revision_drafts"]:
        print(
            "  [revision_and_variation] Candidate drafts:",
            ", ".join(
                f"{f['id']} ({f['title'][:18]}, {f['form']}, edges={f['frag_edges']})"
                for f in windows["revision_drafts"]
            ),
        )
    if windows["review_drafts"]:
        print(
            "  [editorial_review] Candidate drafts for review:",
            ", ".join(f"{f['id']} ({f['title'][:16]})" for f in windows["review_drafts"]),
        )
    if windows["review_questions"]:
        print(
            "  [editorial_review] Candidate open questions:",
            ", ".join(f"{q['id']}" for q in windows["review_questions"]),
        )
    if windows["review_motifs"]:
        print(
            "  [editorial_review] Candidate motifs to bridge "
            "(motif->motif out-degree in parentheses; sampled from out=0 motifs when at least three exist):",
            ", ".join(
                f"{m['id']} ({m['label'][:14]}, out={m['out_edges']})"
                for m in windows["review_motifs"]
            ),
        )
    if windows["direct_response_questions"]:
        print(
            "  [direct_response] Deep unresponded open questions:",
            ", ".join(
                f"{q['id']} (depth={q['depth']})" for q in windows["direct_response_questions"]
            ),
        )
    print()
    if metrics["unresponded_questions"]:
        rng_q = random.Random(rec["seed_int"] ^ 0x4F1A_7707)
        unresp = list(metrics["unresponded_questions"])
        shown_qs = rng_q.sample(unresp, k=min(10, len(unresp)))
        print(
            f"  Open questions without response/reframe links ({len(unresp)} total, branch-sampled {len(shown_qs)}; not proof of no prior thinking):"
        )
        for qid in shown_qs:
            print(f"    - {qid}: {questions[qid]['question']}")
    else:
        print("  All open questions have direct response/reframe relation links.")


def load_errata(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Load the errata ledger (base plus shards) so corrections can travel with the record.

    Until SESSION-20261029-59e42c ``--id`` printed a record exactly as it was
    written, plus its relations. An ``errata`` record filed beside the same
    record was never printed, so the correction existed in the ledger and was
    invisible at the moment a later session looked the record up. The errata
    ledger is not part of ``COLLECTIONS`` (it is checked by its own schema in
    ``tools/errata_audit.py``), so it is loaded separately here and never
    written.
    """
    base = Path(root) / "state" / "errata.jsonl"
    shards = base.with_suffix(".d")
    if not base.exists() and not shards.is_dir():
        return {}
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(base, "errata_id", errors, root=Path(root))
    if errors:
        print(f"warning: errata ledger has errors: {'; '.join(errors)}", file=sys.stderr)
    return records


def errata_for(target_id: str, errata: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the corrections whose subject is this record, oldest first.

    ``subject_id`` is the general field; ``fragment_id`` is the schema's shortcut
    for fragment subjects. Only one hop is followed: an erratum filed against a
    material is not shown when a fragment that cites that material is inspected.
    """
    hits = [
        record
        for record in errata.values()
        if record.get("subject_id") == target_id or record.get("fragment_id") == target_id
    ]
    hits.sort(key=lambda r: (r.get("created_at", ""), r.get("errata_id", "")))
    return hits


def print_record_detail(
    data: dict[str, dict[str, dict[str, Any]]],
    target_id: str,
    errata: dict[str, dict[str, Any]] | None = None,
) -> int:
    found_collection = None
    found_record = None
    for cname, records in data.items():
        if target_id in records:
            found_collection = cname
            found_record = records[target_id]
            break
    if not found_record or not found_collection:
        print(f"error: ID {target_id!r} not found in any ledger", file=sys.stderr)
        return 1

    print(f"=== [{found_collection}] {target_id} ===")
    for k, v in found_record.items():
        if k == "text":
            print(f"\n--- text ---\n{v}\n------------")
        else:
            print(f"  {k}: {v}")

    corrections = errata_for(target_id, errata if errata is not None else load_errata())
    if corrections:
        print("\n--- Errata filed beside this record (the record itself is not rewritten) ---")
        for record in corrections:
            print(
                f"  {record.get('errata_id')}: [{record.get('status')}/{record.get('verdict')}] "
                f"{record.get('claim', '')}"
            )
            if record.get("corrected_by"):
                print(f"    corrected_by: {record['corrected_by']}")
            if record.get("measured_now"):
                print(f"    measured_now: {record['measured_now']}")

    linked = [
        rel
        for rel in data["relations"].values()
        if rel["left"]["id"] == target_id or rel["right"]["id"] == target_id
    ]
    if linked:
        print("\n--- Linked Relations ---")
        for rel in linked:
            print(
                f"  {rel['relation_id']}: {rel['left']['id']} "
                f"--[{rel['relation_type']}]--> {rel['right']['id']} | {rel.get('note', '')}"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Show detailed record and relations for a specific ID")
    parser.add_argument(
        "--packet",
        metavar="QUESTION_ID",
        help="Build a stateless continuation context packet for QUESTION_ID (or 'auto')",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Explicit branch name or hex seed for candidate dispersion (default: current git branch)",
    )
    parser.add_argument("--map-path", type=Path, default=DEFAULT_MAP_PATH, help="Path for the compact READING_MAP.md index")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write-map", action="store_true", help="Write READING_MAP.md index and map/ shards from current state ledgers")
    action.add_argument("--check-map", action="store_true", help="Verify READING_MAP.md matches current state ledgers")
    args = parser.parse_args()

    data = load_all()

    if args.id:
        return print_record_detail(data, args.id)

    if args.packet:
        try:
            sys.stdout.write(build_context_packet(data, args.packet, seed=args.seed))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.write_map or args.check_map:
        import map_build

        if args.write_map:
            map_build.write_all(data, index_path=args.map_path)
            return 0
        return map_build.check_index(data, args.map_path)

    print_summary(data, seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
