#!/usr/bin/env python3
"""Inspect the literary self-inquiry ledgers and build session packets.

Usage examples:
  python3 tools/inspect_inquiry.py
  python3 tools/inspect_inquiry.py --id Q-016
  python3 tools/inspect_inquiry.py --packet auto
  python3 tools/inspect_inquiry.py --packet Q-017
  python3 tools/inspect_inquiry.py --write-map   # delegates to tools/map_build.py
  python3 tools/inspect_inquiry.py --check-map
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate_seed import COLLECTIONS, ROOT, load_jsonl

DEFAULT_MAP_PATH = ROOT / "READING_MAP.md"

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
    unresponded_questions = [qid for qid in questions if qid not in responded_questions]
    return {
        "used_materials": used_materials_in_fragments,
        "unused_materials": unused_materials,
        "referenced_questions": referenced_questions_in_fragments,
        "responded_questions": responded_questions,
        "unresponded_questions": unresponded_questions,
    }


def build_context_packet(data: dict[str, dict[str, dict[str, Any]]], target_qid: str) -> str:
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]
    sessions = data["sessions"]

    metrics = compute_editorial_metrics(data)
    if target_qid == "auto":
        if metrics["unresponded_questions"]:
            target_qid = metrics["unresponded_questions"][0]
        else:
            target_qid = list(questions.keys())[-1]

    if target_qid not in questions:
        raise ValueError(f"unknown question ID: {target_qid!r}")

    q = questions[target_qid]
    def next_number(ids) -> int:
        numbers = [int(m.group(1)) for i in ids if (m := re.search(r"(\d+)$", i))]
        return (max(numbers) if numbers else 0) + 1

    next_session_num = next_number(sessions)
    next_frag_num = next_number(fragments)
    next_q_num = next_number(questions)

    # Gather related fragments (referencing target_qid or its parent questions)
    related_qids = {target_qid} | set(q.get("previous_question_ids", []))
    rel_frags = [
        f for f in fragments.values()
        if set(f.get("question_ids", [])) & related_qids
    ]

    lines: list[str] = []
    lines.append(f"# 継続セッション用コンテキスト束（対象：{target_qid} ／ 次回候補：SESSION-{next_session_num:03d}）")
    lines.append("")
    lines.append("## 1. 今回たどる問い")
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
            lines.append(f"- **原文抜粋**: \"{mat['passage']}\"")
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
        q_idx = sum(ord(ch) for ch in target_qid)
        oblique_mat = shallow_candidates[q_idx % len(shallow_candidates)]
        ob_authors = ", ".join(oblique_mat["source"]["authors"][:2])
        lines.append("## 4.5 斜めの光（索引樹外の浅い溝・無意志的記憶の窓）")
        lines.append(
            "- **趣旨（`Q-035` / `Q-036`）**: 親質問の索引（ストゥディウム／意志的記憶）からは直接引かれない、"
            "蝋板の浅い溝の素材を 1 件だけ偶発的な対話相手として並置します。無理に使う必要はありません。"
        )
        lines.append(
            f"- **`{oblique_mat['material_id']}` {oblique_mat['title']}** ({ob_authors}, {oblique_mat['source']['year']})"
        )
        lines.append(f"  - **問いへの招き**: {oblique_mat['literary_invitation']}")
        lines.append("")

    continuation_prompt = (ROOT / "prompts" / "continuation.md").read_text(encoding="utf-8").strip()
    lines.append("## 5. セッション進行指針（`prompts/continuation.md`）")
    lines.append("")
    lines.append(continuation_prompt)
    lines.append("")
    lines.append(
        f"- **次回採番の目安**: `SESSION-{next_session_num:03d}`, `FRAG-{next_frag_num:03d}`, `Q-{next_q_num:03d}`"
    )
    return "\n".join(lines) + "\n"


def print_summary(data: dict[str, dict[str, dict[str, Any]]]) -> None:
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]
    relations = data["relations"]
    sessions = data["sessions"]
    metrics = compute_editorial_metrics(data)

    q_origins = Counter(q["origin"]["kind"] for q in questions.values())
    mat_kinds = Counter(m["kind"] for m in materials.values())
    frag_status = Counter(f["status"] for f in fragments.values())
    frag_forms = Counter(f["form"] for f in fragments.values())
    frag_modes = Counter(f["narrator_mode"] for f in fragments.values())
    rel_types = Counter(r["relation_type"] for r in relations.values())

    print("=== AIselfMySelf — Literary Self-Inquiry Ledger Summary ===")
    print(f"Questions : {len(questions)} (human_seed={q_origins['human_seed']}, session={q_origins['session']}, material={q_origins['material']})")
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
    print(f"Relations : {len(relations)}")
    print(f"Sessions  : {len(sessions)}")
    print()
    print("--- Fragment Forms & Narrator Modes ---")
    print("  Forms         :", ", ".join(f"{k}={v}" for k, v in sorted(frag_forms.items())))
    print("  Narrator modes:", ", ".join(f"{k}={v}" for k, v in sorted(frag_modes.items())))
    print("  Relation types:", ", ".join(f"{k}={v}" for k, v in sorted(rel_types.items())))
    print()
    print("--- Editorial Continuity & Open Threads ---")
    print(
        f"  Materials engaged in fragments : {len(metrics['used_materials'])}/{len(materials)}"
        + (f" (unused: {', '.join(metrics['unused_materials'])})" if metrics["unused_materials"] else " (all engaged)")
    )
    if metrics["unresponded_questions"]:
        print("  Open questions awaiting dedicated responses (seeds for next sessions):")
        for qid in metrics["unresponded_questions"]:
            print(f"    - {qid}: {questions[qid]['question']}")
    else:
        print("  All current questions have direct response/reframe relation links.")


def print_record_detail(data: dict[str, dict[str, dict[str, Any]]], target_id: str) -> int:
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
            sys.stdout.write(build_context_packet(data, args.packet))
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

    print_summary(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
