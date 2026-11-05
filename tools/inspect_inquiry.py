#!/usr/bin/env python3
"""Inspect the literary self-inquiry ledgers and build session packets.

Usage examples:
  python3 tools/inspect_inquiry.py
  python3 tools/inspect_inquiry.py --seed arena/6f350638-aiselfmyself
  python3 tools/inspect_inquiry.py --id Q-016
  python3 tools/inspect_inquiry.py --packet auto
  python3 tools/inspect_inquiry.py --packet Q-017
  python3 tools/inspect_inquiry.py --packet-stats            # §3 と packet 全体の分布
  python3 tools/inspect_inquiry.py --packet-stats --stats-limit 40   # 標本で素早く
  python3 tools/inspect_inquiry.py --packet auto --inheritance-window 30  # 未継承の窓を変える
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
from typing import Any, Iterable, Sequence

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


def _one_line(text: Any, limit: int) -> str:
    """Collapse whitespace and truncate for one index line."""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def related_notes(
    data: dict[str, dict[str, dict[str, Any]]],
    target_qid: str,
    related_fragment_ids: Iterable[str] = (),
    *,
    root: Path = ROOT,
    limit: int = 6,
    note_view: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Rank the episodic reports in ``readings/`` that touch this question.

    Retrieval by harvested reference, not by recency: a report is a candidate
    because it actually cites the target question, one of its parents, or one of
    the related fragments.  Ranking is a recommendation only — an unranked report
    is not a debt (see prompts/start.md).
    """
    import note_index

    questions = data.get("questions", {})
    parents = set(questions.get(target_qid, {}).get("previous_question_ids", []) or [])
    wanted = {target_qid} | parents
    wanted_frags = set(related_fragment_ids)

    # The harvest reads all of readings/ (~411 files, 15 MB).  Callers that
    # build many packets in one process pass a shared view; building it per
    # packet is the difference between seconds and minutes.
    view = note_view if note_view is not None else note_index.build_view(Path(root), data)
    scored: list[tuple[tuple[int, int, int, int, str], dict[str, Any]]] = []
    for entry in view.values():
        refs = entry.get("refs", {})
        hit_questions = wanted & set(refs.get("questions", []))
        hit_fragments = wanted_frags & set(refs.get("fragments", []))
        if not hit_questions and not hit_fragments:
            continue
        direct = 1 if target_qid in refs.get("questions", []) else 0
        claims = entry.get("curated", {}).get("claims") or []
        claim_hits = sum(
            1
            for claim in claims
            if wanted & set(claim.get("question_ids", []) or [])
            or wanted_frags & set(claim.get("fragment_ids", []) or [])
        )
        salience = entry.get("curated", {}).get("salience")
        salience = salience if isinstance(salience, int) else 0
        key = (
            -direct,
            -(len(hit_questions) + len(hit_fragments) + claim_hits),
            -salience,
            -entry.get("ref_count", 0),
            entry.get("chars", 0),
            entry["path"],
        )
        scored.append((key, entry))
    scored.sort(key=lambda pair: pair[0])
    return [entry for _key, entry in scored[:limit]]


def related_notes_lines(
    data: dict[str, dict[str, dict[str, Any]]],
    target_qid: str,
    related_fragment_ids: Iterable[str] = (),
    *,
    root: Path = ROOT,
    note_view: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    entries = related_notes(
        data, target_qid, related_fragment_ids, root=root, note_view=note_view
    )
    lines = ["## 4.7 関連する精読ノート（`readings/`・エピソード記憶への入口）"]
    lines.append(
        "- **趣旨**: 台帳（意味記憶）に対し、`readings/` は各セッションの語り＝エピソード記憶です。"
        "以下は**この問い・その親・関連断片を実際に参照しているノート**を、"
        "`tools/note_index.py` が本文から読み直した参照IDで引いたものです（新しい順でも短い順でもありません）。"
    )
    if not entries:
        lines.append(
            f"- この問いを参照するノートは見つかりませんでした。全候補は "
            f"`python3 tools/note_index.py --for-id {target_qid}`、索引は `READING_MAP.md` §8。"
        )
        lines.append("")
        return lines
    for entry in entries:
        when = entry.get("date_real") or "実日付の記載なし"
        label = entry.get("date_label") or "?"
        reach = "リンクあり" if entry.get("reachable") else "孤立（grep/ファイル名のみ）"
        lines.append(
            f"- `{entry['path']}` — {_one_line(entry.get('title') or entry['name'], 70)}"
        )
        lines.append(
            f"  - 実日付 {when}／内部編年ラベル `{label}`・{entry.get('chars', 0):,} 字・"
            f"参照ID {entry.get('ref_count', 0)} 件・{reach}"
            + (f"・モード `{entry['mode']}`（導出）" if entry.get("mode") else "")
        )
        curated = entry.get("curated") or {}
        for field in ("quadrant", "return_status", "read_depth"):
            if curated.get(field):
                lines.append(f"  - **{field}（台帳判断）**: `{curated[field]}`")
        for claim in (curated.get("claims") or [])[:3]:
            anchor = f"（{claim['anchor']}）" if claim.get("anchor") else ""
            lines.append(f"  - **固定された主張** `{claim.get('claim_id')}` [{claim.get('kind')}]{anchor} {_one_line(claim.get('text', ''), 160)}")
        if entry.get("note_id"):
            lines.append(
                "  - 台帳行 `" + str(entry["note_id"]) + "`（`read_log` の `target.type` を `note` にしてこのノートを引用できます）"
            )
    lines.append(
        "- **読み方の注意**: 上は索引であって本文ではありません。開いて読んだノートだけ "
        "`read_log` に記帳し、読んでいないノートを既読として扱わないでください"
        "（`CONTENT_POLICY.md`）。判断を台帳に残す場合は "
        "`python3 tools/note_index.py --register <path> --session <SESSION-ID> --read-depth full_text_read`。"
    )
    lines.append("")
    return lines


# Working-memory budget for the one unbounded evidence section of a packet.
#
# Measured over all 408 questions (commit d133bbe, before this budget existed):
#   §3 対話素材   p50  7,023 B ／ p90 15,602 B ／ p99 55,631 B ／ max 55,631 B
#   packet 全体   p50 34,217 B ／ p90 44,009 B ／ p99 82,657 B ／ max 82,727 B
# The tail is driven by material *count*, not by passage length: the five worst
# questions each link 43 materials whose passages total only 6,233 B, so ~1,290 B
# of fixed scaffold per material is what multiplies.  §4 (3-fragment window), §4.7
# (6 notes x 3 claims) and §1/§2 (the question's own motif_ids) are already
# bounded, which leaves §3 as the only section that grows without limit.
#
# 16 KiB sits just under p90, so a typical session is unaffected -- the budget
# trims the tail instead of forcing a change on everyone (a number here is an
# observation, not a command: docs/mode-rotation-triggers.md §2).  Omitted
# materials are named by ID with the command to fetch them, so reachability into
# the 2,656-material archive is preserved even when the bytes are not carried.
MATERIAL_SECTION_BUDGET = 16_384


# ---------------------------------------------------------------------------
# §4.8 未継承の窓 — reports a later session could have read and did not
# ---------------------------------------------------------------------------
#
# docs/memory-architecture.md §2 diagnosed the gap (411 reports, no index, no
# retrieval path back into the episodes); tools/inheritance.py measures it.  The
# packet is where a session chooses what to read, so the gap belongs here too.
#
# Two rules keep this section from becoming a scoreboard:
#
#   * **Read, not ranked.**  A report appears because no ``read_log`` row from a
#     *different* session names its ``notes`` row.  Prose citations are shown but
#     never counted as inheritance, and a report without a ``notes`` row is
#     listed as *unmeasurable* rather than as unread.
#   * **Cheap.**  The section reads no report bodies (only the note ledger and
#     ``read_log``), is capped at six rows of one line each, and is placed after
#     §4.7 so §3, §4, §4.5 and §4.7 keep their measured byte sizes exactly.
INHERITANCE_WINDOW_DEFAULT = 30
INHERITANCE_LIMIT = 6


def inherited_report_paths(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    root: Path = ROOT,
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Return ``(per-report facts, totals)`` from the ledger alone.

    Deliberately not re-using :mod:`note_index`'s harvest: this runs inside every
    packet, and §8 must stay byte-identical to what ``map_build.py`` renders.
    Only ``notes`` (which report a row describes) and ``read_log`` (who logged a
    reading of that row) are needed.
    """
    notes = data.get("notes", {})
    read_log = data.get("read_log", {})
    path_by_note = {
        note_id: row["path"]
        for note_id, row in notes.items()
        if isinstance(row.get("path"), str)
    }
    author_by_path: dict[str, set[str]] = {}
    label_by_path: dict[str, str] = {}
    for note_id, row in notes.items():  # ledger order: later rows win
        path = row.get("path")
        if not isinstance(path, str):
            continue
        author = row.get("report_session_id") or row.get("session_id")
        if isinstance(author, str) and author:
            author_by_path.setdefault(path, set()).add(author)
        if isinstance(row.get("date_real"), str):
            label_by_path[path] = row["date_real"]

    read_by_path: dict[str, set[str]] = {}
    totals = {
        "note_rows": len(notes),
        "note_read_rows": 0,
        "self_read_rows": 0,
        "inherited_rows": 0,
        "reports_with_notes": len({row.get("path") for row in notes.values() if isinstance(row.get("path"), str)}),
    }
    for record in read_log.values():
        target = record.get("target")
        if not isinstance(target, dict) or target.get("type") != "note":
            continue
        totals["note_read_rows"] += 1
        path = path_by_note.get(target.get("id"))
        if path is None:
            continue
        reader = record.get("session_id")
        if isinstance(reader, str) and reader and reader in author_by_path.get(path, set()):
            totals["self_read_rows"] += 1
            continue
        totals["inherited_rows"] += 1
        read_by_path.setdefault(path, set()).add(reader or "?")

    return (
        {"read_by": read_by_path, "authors": author_by_path, "date_real": label_by_path},
        totals,
    )


def unread_report_lines(
    data: dict[str, dict[str, dict[str, Any]]],
    target_qid: str,
    *,
    root: Path = ROOT,
    window: int = INHERITANCE_WINDOW_DEFAULT,
) -> list[str]:
    """§4.8: recent reports with no ledger-visible successor, plus the totals."""
    facts, totals = inherited_report_paths(data, root=root)
    lines = ["## 4.8 未継承の窓（この報告を、後続のセッションはまだ一度も `read_log` で読んでいない）"]
    lines.append(
        "- **趣旨**: `readings/` はエピソード記憶ですが、後続がそのノート行を "
        "`read_log`（`target.type: \"note\"`）で読んだ記録は、報告本文のリンクや README の窓より"
        "はるかに少ない状態です（実測は `python3 tools/inheritance.py`）。"
        "ここに並ぶのは**未測定**の報告で、未読・無価値の判定ではありません。"
    )
    lines.append(
        f"- **台帳の実測**: notes 行 {totals['note_rows']} ／ note を指す読み {totals['note_read_rows']} 行"
        f"（自セッション {totals['self_read_rows']} ／ 後続 {totals['inherited_rows']}）"
        f"。notes 行を持たない報告はそもそも継承を測れません。"
    )
    candidates = sorted(
        (
            (path, when)
            for path, when in facts["date_real"].items()
            if not facts["read_by"].get(path)
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )[:window]
    if not candidates:
        lines.append("- 窓内に未継承の報告はありません（すべて後続の `read_log` に現れています）。")
    else:
        lines.append(
            f"- **直近 {len(candidates)} 本の候補**（新しい順・上から {INHERITANCE_LIMIT} 件だけ名指しします）:"
        )
        for path, when in candidates[:INHERITANCE_LIMIT]:
            readers = facts["read_by"].get(path) or set()
            state = "後続あり" if readers else "後続なし"
            lines.append(f"  - `{path}`（実日付 {when}・{state}）")
    lines.append(
        "  - 読んだら `python3 tools/note_index.py --register <path> --session <SESSION-ID> "
        "--read-depth full_text_read` でノート行を記帳し、`read_log` の `target.type` に `note` を"
        "使ってください。記帳しないと、次のセッションには継承が見えません。"
    )
    lines.append(
        "- **注意**: この節は候補であって義務ではありません。読まない選択も記録できます。"
        "継承の実測は `python3 tools/inheritance.py --cohorts`。"
    )
    lines.append("")
    return lines


def material_block(mat_id: str, mat: dict[str, Any], errata: dict[str, dict[str, Any]]) -> list[str]:
    """Render one §3 material entry, whole.  Never split: a half-quoted passage
    is worse than an omitted one, because it can be mistaken for the full quote
    ("要約を原典と呼ばない")."""
    out: list[str] = []
    authors = ", ".join(mat["source"]["authors"][:3])
    if len(mat["source"]["authors"]) > 3:
        authors += " et al."
    out.append(f"### `{mat_id}` {mat['title']} ({authors}, {mat['source']['year']})")
    out.append(f"- **種別**: `{mat['kind']}` ／ **出典**: {mat['source']['url']}")
    out.append(f"- **問いへの招き**: {mat['literary_invitation']}")
    out.append(f"- **版・箇所**: {mat['source'].get('version_note', '未記録')} ／ {mat.get('context', '未記録')}")
    verification = mat.get("verification", {})
    out.append(f"- **台帳の検証記録（今回の照合結果ではない）**: {verification.get('status', '未記録')}")
    corrections = errata_for(mat_id, errata)
    if corrections:
        ids = ", ".join(f"`{c.get('errata_id')}`" for c in corrections)
        out.append(
            f"- **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
            f" — `python3 tools/inspect_inquiry.py --id {mat_id}`"
        )
    if mat.get("source_note"):
        out.append(f"- **先行する編者のメモ**: {mat['source_note']}")
    out.append("- **台帳の passage（引用・要約の別は記録に従う。要約を原典と呼ばない）**:")
    out.extend(f"> {part}" for part in mat["passage"].splitlines())
    out.append(f"- **適用範囲の留保**: {mat['scope_note']}")
    out.append("")
    return out


def build_context_packet(
    data: dict[str, dict[str, dict[str, Any]]],
    target_qid: str,
    *,
    seed: str | None = None,
    errata: dict[str, dict[str, Any]] | None = None,
    root: Path = ROOT,
    material_budget: int = MATERIAL_SECTION_BUDGET,
    note_view: dict[str, dict[str, Any]] | None = None,
    inheritance_window: int = INHERITANCE_WINDOW_DEFAULT,
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
    q_corrections = errata_for(target_qid, errata)
    if q_corrections:
        ids = ", ".join(f"`{c.get('errata_id')}`" for c in q_corrections)
        lines.append(
            f"- **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
            f" — `python3 tools/inspect_inquiry.py --id {target_qid}`"
        )
    if q.get("previous_question_ids"):
        lines.append("- **親の問い**:")
        for pqid in q["previous_question_ids"]:
            if pqid in questions:
                lines.append(f"  - `{pqid}`: {questions[pqid]['question']}")
                pq_corrections = errata_for(pqid, errata)
                if pq_corrections:
                    ids = ", ".join(f"`{c.get('errata_id')}`" for c in pq_corrections)
                    lines.append(
                        f"    - **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
                        f" — `python3 tools/inspect_inquiry.py --id {pqid}`"
                    )
    lines.append("")

    lines.append("## 2. 関係するモチーフ")
    for mid in q.get("motif_ids", []):
        if mid in motifs:
            m = motifs[mid]
            lines.append(f"- **`{mid}` ({m['label']})**: {m['description']}")
            m_corrections = errata_for(mid, errata)
            if m_corrections:
                ids = ", ".join(f"`{c.get('errata_id')}`" for c in m_corrections)
                lines.append(
                    f"  - **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
                    f" — `python3 tools/inspect_inquiry.py --id {mid}`"
                )
    lines.append("")

    lines.append("## 3. 対話素材（結論の証拠ではなく、摩擦と比喩の種として扱う）")
    # Byte budget, ledger-order prefix.  Every material of the question is a
    # candidate in the order the ledger records it; blocks are added whole until
    # the next one would cross the budget, and everything from there on is named
    # as omitted rather than silently dropped.  Strict prefix (not best-fit) so
    # the selection stays deterministic and stays in ledger order -- a greedy
    # fill would reorder by size and make "which materials did I see" depend on
    # passage lengths instead of on the question's own record.
    packet_materials = [mid for mid in q.get("material_ids", []) if mid in materials]
    shown_mats: list[str] = []
    omitted_mats: list[str] = []
    used_bytes = 0
    for idx, mat_id in enumerate(packet_materials):
        block = material_block(mat_id, materials[mat_id], errata)
        cost = len(("\n".join(block) + "\n").encode("utf-8"))
        # The first material is always carried whole, even if it alone exceeds
        # the budget: an empty §3 would hide the question's own materials.
        if material_budget > 0 and shown_mats and used_bytes + cost > material_budget:
            omitted_mats = packet_materials[idx:]
            break
        shown_mats.append(mat_id)
        used_bytes += cost
        lines.extend(block)
    if omitted_mats:
        omitted_str = ", ".join(f"`{m}`" for m in omitted_mats)
        lines.append(
            f"- **予算注記（§3 の上限 {material_budget:,} B）**: この問いの対話素材 "
            f"{len(packet_materials)} 件のうち台帳順の先頭 {len(shown_mats)} 件（{used_bytes:,} B）を載せ、"
            f"窓外の {len(omitted_mats)} 件は**載せていません**: {omitted_str}。"
        )
        lines.append(
            # 字节 は簡体字の混入（正しくは バイト／字節）だが、この行は packet の §3 に
            # 描画されるため、直すと予算注記が出る40問の §3 が +3 B 動き、§3 p99
            # 16,652→16,655・max 16,956→16,959 になる。max の 16,956 B は追記専用台帳の
            # CLM-599b4c-4 に入っていて訂正できない。よって表記は据え置き、
            # 訂正は errata（記録の隣に置き記録自体は書き換えない）で行う。
            "  省略は素材の価値や関連度の判断ではなく、packet の字节予算だけです。"
            " 窓外の素材も `python3 tools/inspect_inquiry.py --id <MAT-ID>` で全文を引けます"
            "（予算は `--material-budget` で変更可、0 で無制限）。"
        )
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
        ob_corrections = errata_for(oblique_mat["material_id"], errata)
        if ob_corrections:
            ids = ", ".join(f"`{c.get('errata_id')}`" for c in ob_corrections)
            lines.append(
                f"  - **訂正録（この記録の隣に置かれ、記録自体は書き換えていない）**: {ids}"
                f" — `python3 tools/inspect_inquiry.py --id {oblique_mat['material_id']}`"
            )
        lines.append("")

    lines.extend(
        related_notes_lines(
            data,
            target_qid,
            [f["fragment_id"] for f in rel_frags],
            root=root,
            note_view=note_view,
        )
    )
    lines.extend(
        unread_report_lines(
            data,
            target_qid,
            root=root,
            window=inheritance_window,
        )
    )

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


# --- Packet byte distribution (an observation, not a gate) -----------------
#
# MATERIAL_SECTION_BUDGET was chosen from a measurement of §3 across all
# questions, but nothing in the repository could reproduce that measurement:
# the script that produced it was scratch, so the figures in the constant's
# comment were the only surviving trace and could not be checked again as the
# corpus grew.  These functions make the derivation re-runnable.
#
# Two measured facts the readout has to carry:
#
#   * The percentile form is pinned, not chosen.  ``ordered[int(q * n)]``
#     clamped to the last index reproduces all sixteen figures already written
#     into docs/memory-architecture.md and into append-only ``notes`` claims
#     (§3 and packet total, p50/p90/p99/max, budgeted and unbudgeted) at seed
#     9a7bda3c.  A neighbouring definition shifts §3 p50 by 91 B and packet p99
#     by 1,436 B, which would make this tool contradict records that cannot be
#     corrected.
#   * §3 does not move with the branch seed; the packet total does, because
#     §0.5 (the dispersion window) is seeded.  Measured over all 408 questions
#     under two seeds: every §3 percentile matched to the byte, while every
#     packet percentile shifted (p50 34,223 -> 32,707 B, max 84,379 -> 83,104 B
#     unbudgeted).  So §3 is the column that is comparable across branches and
#     across time, and a packet total is only comparable within one seed --
#     which is why the readout prints the seed it measured under.  Reading a
#     packet total from another branch as growth or shrinkage would be reading
#     the seed.


def percentile(ordered: Sequence[int], q: float) -> int:
    """The pinned percentile of an ascending sequence: ``ordered[int(q * n)]``.

    Clamped to the last index, so p99 of a short list is its maximum rather
    than an IndexError.  See the block above for why this exact form: it is the
    one that reproduces the figures already recorded in append-only ledgers.
    """
    if not ordered:
        return 0
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def packet_sections(packet: str) -> dict[str, int]:
    """Byte size of each ``## `` section of a packet, keyed by heading token.

    The key is the heading's first token with one trailing dot stripped, so
    ``## 3. 対話素材…`` keys as ``3`` and ``## 4.5 斜めの光…`` keys as ``4.5``.
    Matching by prefix instead (``startswith("## 4.")``) silently merges §4
    with §4.5 and §4.7 -- that mistake once produced an inflated §4 here.

    Lines before the first ``## `` key as ``"(前文)"``.  Every line is charged
    its own bytes plus the newline ``splitlines`` removed, so the values sum to
    ``len(packet.encode("utf-8"))`` for a packet ending in one newline.
    """
    sizes: dict[str, int] = {}
    key = "(前文)"
    for line in packet.splitlines():
        if line.startswith("## "):
            token = line[3:].split(" ", 1)[0]
            key = token[:-1] if token.endswith(".") else token
        sizes[key] = sizes.get(key, 0) + len(line.encode("utf-8")) + 1
    return sizes


# The tail threshold docs quote as "48 KB 超" is decimal 48,000 B, not 48 KiB.
# Pinned by reproduction: at seed 9a7bda3c the recorded "27 問 -> 1 問" comes
# out exactly with >48_000 (unbudgeted max 84,379 B, budgeted max 49,042 B),
# while >49_152 yields 25 and 0 and would contradict a table already merged.
# The budgeted maximum sits between the two thresholds, which is the only
# reason the difference is visible at all.
TAIL_THRESHOLD_BYTES = 48_000


def _distribution(values: list[int]) -> dict[str, int]:
    ordered = sorted(values)
    return {
        "p50": percentile(ordered, 0.5),
        "p90": percentile(ordered, 0.9),
        "p99": percentile(ordered, 0.99),
        "max": ordered[-1] if ordered else 0,
        "over_tail": sum(1 for v in ordered if v > TAIL_THRESHOLD_BYTES),
    }


def packet_stats(
    data: dict[str, dict[str, dict[str, Any]]],
    *,
    seed: str | None = None,
    material_budget: int = MATERIAL_SECTION_BUDGET,
    errata: dict[str, dict[str, Any]] | None = None,
    root: Path = ROOT,
    limit: int = 0,
) -> dict[str, Any]:
    """Measure every question's packet, budgeted and unbudgeted.

    Returns the §3 and packet-total distributions plus how many questions the
    budget actually touched.  ``limit`` measures only the first N questions in
    ledger order -- a sample for a quick check, not the corpus, and the readout
    says so when it is in effect.

    The note view is harvested once and shared by every packet.  It reads all
    of readings/ (~411 files, 15 MB); rebuilding it per question turned an
    eleven-second pass into an eleven-minute one, with byte-identical output.
    """
    import note_index

    if errata is None:
        errata = load_errata(root)
    view = note_index.build_view(Path(root), data)
    seed_label, _seed_int = resolve_session_seed(seed, root=Path(root), data=data)
    qids = list(data.get("questions", {}))
    sampled = limit > 0 and limit < len(qids)
    if limit > 0:
        qids = qids[:limit]

    passes: list[tuple[str, int]] = [("budgeted", material_budget)]
    if material_budget != 0:
        passes.append(("unbudgeted", 0))

    stats: dict[str, Any] = {
        "seed_label": seed_label,
        "material_budget": material_budget,
        "questions": len(qids),
        "sampled": sampled,
    }
    for name, budget in passes:
        section_three: list[int] = []
        totals: list[int] = []
        noted = 0
        omitted_total = 0
        omitted_max = 0
        for qid in qids:
            packet = build_context_packet(
                data,
                qid,
                seed=seed,
                errata=errata,
                root=root,
                material_budget=budget,
                note_view=view,
            )
            sections = packet_sections(packet)
            section_three.append(sections.get("3", 0))
            totals.append(len(packet.encode("utf-8")))
            if "予算注記" in packet:
                noted += 1
                candidates = [
                    m
                    for m in data["questions"][qid].get("material_ids", [])
                    if m in data.get("materials", {})
                ]
                omitted = len(candidates) - packet.count("\n### `MAT-")
                omitted_total += omitted
                omitted_max = max(omitted_max, omitted)
        stats[name] = {
            "section_three": _distribution(section_three),
            "packet": _distribution(totals),
            "noted_questions": noted,
            "omitted_materials": omitted_total,
            "omitted_max_per_question": omitted_max,
        }
    return stats


def print_packet_stats(stats: dict[str, Any]) -> None:
    """Print the distribution as an observation, with its comparison rules."""
    budget = stats["material_budget"]
    print("=== packet バイト分布（観察値。合否でも命令でもない）===")
    scope = f"先頭 {stats['questions']} 問（標本。母集団全体ではない）"
    if stats["sampled"]:
        print(f"対象: {scope} ／ シード: `{stats['seed_label']}`")
    else:
        print(f"対象: 全 {stats['questions']} 問 ／ シード: `{stats['seed_label']}`")
    print()
    for name, label in (("budgeted", f"予算 {budget:,} B"), ("unbudgeted", "予算なし (0)")):
        if name not in stats:
            continue
        row = stats[name]
        s3 = row["section_three"]
        pk = row["packet"]
        print(f"[{label}]")
        print(
            f"  §3 対話素材  p50 {s3['p50']:>7,} ／ p90 {s3['p90']:>7,} ／ "
            f"p99 {s3['p99']:>7,} ／ max {s3['max']:>7,} B"
        )
        print(
            f"  packet 全体  p50 {pk['p50']:>7,} ／ p90 {pk['p90']:>7,} ／ "
            f"p99 {pk['p99']:>7,} ／ max {pk['max']:>7,} B"
        )
        print(
            f"  {TAIL_THRESHOLD_BYTES:,} B 超  §3 {s3['over_tail']} 問 ／ "
            f"packet {pk['over_tail']} 問"
        )
        if name == "budgeted" and budget:
            print(
                f"  予算注記     {row['noted_questions']} 問 ／ 窓外の素材 "
                f"{row['omitted_materials']} 件（1問あたり最大 "
                f"{row['omitted_max_per_question']} 件）"
            )
        print()
    print("読み比べるときの注意（どちらも実測に基づく）:")
    print("  * §3 はブランチシードで動かない。時系列とブランチをまたいで比べられるのは §3 だけ。")
    print("  * packet 全体は §0.5（分散候補窓）がシード依存なので、同じシード内でしか比べられない。")
    print("    別ブランチの packet 全体を肥大化や縮小として読むと、読んでいるのはシードである。")
    print()
    if "unbudgeted" in stats and budget:
        p90 = stats["unbudgeted"]["section_three"]["p90"]
        print(f"再測定の目安: 既定値 {budget:,} B は「§3 の予算なし p90」に寄せてある。")
        print(f"  現在の予算なし p90 は {p90:,} B。")
        if p90 > budget:
            print("  p90 が既定値を超えているので、この値はもう §3 の p90 ではない。")
        else:
            print("  p90 は既定値以下なので、この値はまだ §3 の p90 相当である。")
        print("  どちらの行も観察であって、値を変える作業を強制しない")
        print("  （docs/mode-rotation-triggers.md §2「廃止した探究上の数値条件」）。")


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
    parser.add_argument(
        "--material-budget",
        type=int,
        default=MATERIAL_SECTION_BUDGET,
        metavar="BYTES",
        help=(
            "Byte budget for packet §3 (対話素材).  Materials are carried whole, in "
            "ledger order, until the next block would cross this limit; the rest are "
            "named as omitted with the command to fetch them.  0 means unlimited "
            f"(default: {MATERIAL_SECTION_BUDGET}, measured at p90 of all questions)"
        ),
    )
    parser.add_argument(
        "--inheritance-window",
        type=int,
        default=INHERITANCE_WINDOW_DEFAULT,
        metavar="N",
        help=(
            "How many recent reports §4.8 draws its un-inherited window from "
            f"(default: {INHERITANCE_WINDOW_DEFAULT}). The section names at most "
            f"{INHERITANCE_LIMIT} paths and never changes §3/§4/§4.5/§4.7 bytes."
        ),
    )
    parser.add_argument(
        "--packet-stats",
        action="store_true",
        help=(
            "Measure the packet byte distribution over every question and print "
            "it as an observation (§3 and packet total, budgeted and unbudgeted). "
            "This is how MATERIAL_SECTION_BUDGET's derivation is re-checked; it is "
            "not a gate and asserts nothing. Reads all of readings/ once, so it "
            "takes seconds rather than the minutes a per-question harvest would."
        ),
    )
    parser.add_argument(
        "--stats-limit",
        type=int,
        default=0,
        metavar="N",
        help="With --packet-stats, measure only the first N questions in ledger order (a sample, labelled as one; 0 = all, the default)",
    )
    parser.add_argument("--map-path", type=Path, default=DEFAULT_MAP_PATH, help="Path for the compact READING_MAP.md index")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write-map", action="store_true", help="Write READING_MAP.md index and map/ shards from current state ledgers")
    action.add_argument("--check-map", action="store_true", help="Verify READING_MAP.md matches current state ledgers")
    args = parser.parse_args()

    data = load_all()

    if args.id:
        return print_record_detail(data, args.id)

    if args.packet_stats:
        print_packet_stats(
            packet_stats(
                data,
                seed=args.seed,
                material_budget=args.material_budget,
                limit=args.stats_limit,
            )
        )
        return 0

    if args.packet:
        try:
            sys.stdout.write(
                build_context_packet(
                    data,
                    args.packet,
                    seed=args.seed,
                    material_budget=args.material_budget,
                    inheritance_window=args.inheritance_window,
                )
            )
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
