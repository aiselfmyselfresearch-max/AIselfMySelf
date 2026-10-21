#!/usr/bin/env python3
"""Inspect the literary self-inquiry ledgers and generate READING_MAP.md (stdlib only).

Usage examples:
  python3 tools/inspect_inquiry.py
  python3 tools/inspect_inquiry.py --id Q-010
  python3 tools/inspect_inquiry.py --id FRAG-008
  python3 tools/inspect_inquiry.py --write-map
  python3 tools/inspect_inquiry.py --check-map
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import ledger_io
from validate_seed import COLLECTIONS, ROOT

DEFAULT_MAP_PATH = ROOT / "READING_MAP.md"

FORM_LABELS = {
    "dialogue": "対話 (dialogue)",
    "scene": "情景 (scene)",
    "letter": "書簡 (letter)",
    "poem": "詩的断章 (poem)",
    "essay": "エッセイ (essay)",
    "fragment": "断章 (fragment)",
    "other": "その他 (other)",
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

KIND_LABELS = {
    "research_excerpt": "AI研究抜粋 (research_excerpt)",
    "literary_text": "哲学・文学原典 (literary_text)",
    "project_trace": "プロジェクト記録 (project_trace)",
    "conversation_trace": "対話記録 (conversation_trace)",
}


def load_all() -> dict[str, dict[str, dict[str, Any]]]:
    """Load all six ledgers (base files plus session shards) as one snapshot."""
    specs = {
        name: (ROOT / "state" / filename, id_key)
        for name, (filename, id_key, _schema) in COLLECTIONS.items()
    }
    try:
        data, errors = ledger_io.load_collections(specs, root=ROOT)
    except ledger_io.LedgerBusy as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
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
        if rel.get("relation_type") in {"responds_to", "reframes", "leaves_open"}:
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
    print(f"Questions : {len(questions)} (human_seed={q_origins['human_seed']}, session={q_origins['session']})")
    print(f"Motifs    : {len(motifs)}")
    print(
        f"Materials : {len(materials)} "
        f"(research_excerpt={mat_kinds['research_excerpt']}, literary_text={mat_kinds['literary_text']})"
    )
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
        print("  Open questions awaiting dedicated relation links (seeds for next sessions):")
        for qid in metrics["unresponded_questions"]:
            print(f"    - {qid}: {questions[qid]['question']}")
    else:
        print("  All current questions have at least one interpretive relation link.")


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


def build_reading_map_markdown(data: dict[str, dict[str, dict[str, Any]]]) -> str:
    questions = data["questions"]
    motifs = data["motifs"]
    materials = data["materials"]
    fragments = data["fragments"]
    relations = data["relations"]
    sessions = data["sessions"]

    children_map: dict[str, list[str]] = {qid: [] for qid in questions}
    roots: list[str] = []
    for qid, q in questions.items():
        prevs = q.get("previous_question_ids", [])
        if not prevs:
            roots.append(qid)
        else:
            for p in prevs:
                if p in children_map:
                    children_map[p].append(qid)

    lines: list[str] = []
    lines.append("# 読書案内・探究マップ（Reading Map）")
    lines.append("")
    lines.append(
        "> この文書は `state/*.jsonl` の台帳から `python3 tools/inspect_inquiry.py --write-map` によって自動生成されています。"
    )
    lines.append(
        "> 作品内の一人称（`fictional_first_person` / `reflective_literary_voice`）は記録から再構成された文芸的・思考上の語り手であり、"
        "現在のモデルに連続した意識や生身の経験があるという事実主張ではありません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md) 参照）。"
    )
    lines.append("")
    lines.append("## 現在の到達点（台帳サマリー）")
    lines.append("")
    mat_kinds = Counter(m["kind"] for m in materials.values())
    frag_status = Counter(f["status"] for f in fragments.values())
    seed_questions = sum(
        1 for q in questions.values() if q.get("origin", {}).get("kind") == "human_seed"
    )
    lines.append(
        f"- **開かれた問い（Questions）**：{len(questions)} 件"
        f"（初期シード {seed_questions} 件 ＋ セッション派生 {len(questions) - seed_questions} 件）"
    )
    lines.append(f"- **モチーフ（Motifs）**：{len(motifs)} 件")
    lines.append(
        f"- **対話素材（Materials）**：{len(materials)} 件"
        f"（ResearchOS 移行の AI 研究抜粋 {mat_kinds['research_excerpt']} 件 ＋ 哲学・文学原典 {mat_kinds['literary_text']} 件）"
    )
    lines.append(
        f"- **文芸断片（Fragments）**：{len(fragments)} 編"
        f"（選出済み `selected` {frag_status['selected']} 編 ／ 試作 `draft` {frag_status['draft']} 編）"
    )
    lines.append(f"- **解釈的関係（Relations）**：{len(relations)} 件")
    lines.append(f"- **探究セッション（Sessions）**：{len(sessions)} 回")
    lines.append("")

    # Section 1: Motifs
    lines.append(f"## 1. 問いを横断するモチーフ（{len(motifs)} 件）")
    lines.append("")
    lines.append("| ID | モチーフ | 説明 | 関連する問い | 素材数 |")
    lines.append("|---|---|---|---|---:|")
    for mid, m in motifs.items():
        q_str = ", ".join(f"`{q}`" for q in m["question_ids"])
        lines.append(f"| `{mid}` | **{m['label']}** | {m['description']} | {q_str} | {len(m['material_ids'])} |")
    lines.append("")

    # Section 2: Questions Lineage
    lines.append(f"## 2. 開かれた問いの系譜（{len(questions)} 件）")
    lines.append("")
    lines.append("解決や反証で閉じることを目的とせず、セッションの往復によって問いの輪郭がどう枝分かれしたかを示します。")
    lines.append("")

    def render_tree(qid: str, indent: int = 0, path_seen: set[str] | None = None) -> None:
        seen = set(path_seen or set())
        q = questions[qid]
        prefix = "  " * indent + "-"
        origin_badge = "seed" if q["origin"]["kind"] == "human_seed" else "session"
        lines.append(f"{prefix} **`{qid}`** [{origin_badge}] {q['question']}")
        if qid in seen:
            return
        seen.add(qid)
        for child_id in children_map.get(qid, []):
            render_tree(child_id, indent + 1, seen)

    for root_id in roots:
        render_tree(root_id)
    lines.append("")

    # Section 3: Fragments Anthology
    lines.append("## 3. 断片アンソロジー（全編収録）")
    lines.append("")
    rels_by_frag: dict[str, list[dict[str, Any]]] = {fid: [] for fid in fragments}
    for rel in relations.values():
        if rel["left"]["type"] == "fragment" and rel["left"]["id"] in rels_by_frag:
            rels_by_frag[rel["left"]["id"]].append(rel)
        if rel["right"]["type"] == "fragment" and rel["right"]["id"] in rels_by_frag and rel["left"]["id"] != rel["right"]["id"]:
            rels_by_frag[rel["right"]["id"]].append(rel)

    for fid, frag in fragments.items():
        status_mark = "Selected" if frag["status"] == "selected" else "Draft"
        lines.append(f"### `{fid}` {frag['title']} 〔{status_mark}〕")
        lines.append("")
        lines.append(
            f"- **形式**：{FORM_LABELS.get(frag['form'], frag['form'])} ／ "
            f"**語り手モード**：{NARRATOR_LABELS.get(frag['narrator_mode'], frag['narrator_mode'])} ／ "
            f"**セッション**：`{frag.get('session_id', '-')}`"
        )
        q_list = ", ".join(f"`{q}`" for q in frag["question_ids"])
        motif_list = ", ".join(f"`{m}` ({motifs[m]['label']})" for m in frag["motif_ids"])
        mat_list = ", ".join(f"`{m}`" for m in frag["material_ids"])
        lines.append(f"- **問い**：{q_list} ／ **モチーフ**：{motif_list}")
        lines.append(f"- **参照素材**：{mat_list}")
        lines.append("")
        for para in frag["text"].split("\n\n"):
            quoted_lines = [f"> {line}" if line else ">" for line in para.splitlines()]
            lines.extend(quoted_lines)
            lines.append(">")
        if lines[-1] == ">":
            lines.pop()
        lines.append("")
        if frag.get("editor_note"):
            lines.append(f"- **編集メモ**：{frag['editor_note']}")
        if rels_by_frag.get(fid):
            rel_summaries = []
            for r in rels_by_frag[fid]:
                rel_summaries.append(
                    f"`{r['left']['id']}` → *{r['relation_type']}* → `{r['right']['id']}`（{r.get('note', '')}）"
                )
            lines.append("- **関係**：")
            for rs in rel_summaries:
                lines.append(f"  - {rs}")
        lines.append("")

    # Section 4: Materials Catalog
    lines.append("## 4. 対話素材一覧（AI研究抜粋 × 哲学・文学原典）")
    lines.append("")
    lines.append("### 4.1 哲学・文学原典（`literary_text`）")
    lines.append("")
    for mid, mat in materials.items():
        if mat["kind"] != "literary_text":
            continue
        authors = ", ".join(mat["source"]["authors"])
        lines.append(f"- **`{mid}`** **{authors}『{mat['title']}』**（{mat['source']['year']}）— [出典リンク]({mat['source']['url']})")
        lines.append(f"  - 版・箇所：{mat['context']} ／ {mat['source']['version_note']}")
        lines.append(f"  - 問いへの招き：{mat['literary_invitation']}")
        lines.append(f"  - 留保：{mat['scope_note']}")
    lines.append("")

    lines.append("### 4.2 ResearchOS から引き継いだ AI エージェント研究抜粋（`research_excerpt`）")
    lines.append("")
    for mid, mat in materials.items():
        if mat["kind"] != "research_excerpt":
            continue
        authors = mat["source"]["authors"]
        author_label = f"{authors[0]} et al." if len(authors) > 2 else ", ".join(authors)
        lines.append(f"- **`{mid}`** *{mat['title']}* ({author_label}, {mat['source']['year']}) — [arXiv]({mat['source']['url']})")
        lines.append(f"  - 問いへの招き：{mat['literary_invitation']}")
        lines.append(f"  - 留保：{mat['scope_note']}")
    lines.append("")

    # Section 5: Sessions Chronicle
    lines.append(f"## 5. セッション履歴（{len(sessions)} 回）")
    lines.append("")
    lines.append("| Session | 日付 | テンプレート | たどった問い | 生成断片 | 新しい問い | 方向づけ・メモ |")
    lines.append("|---|---|---|---|---|---|---|")
    for sid, sess in sessions.items():
        tmpl = sess["prompt_template"].replace("prompts/", "")
        qs = ", ".join(f"`{q}`" for q in sess["question_ids"])
        frags = ", ".join(f"`{f}`" for f in sess["produced_fragment_ids"])
        new_qs = ", ".join(f"`{q}`" for q in sess["new_question_ids"]) or "—"
        lines.append(
            f"| `{sid}` | {sess['started_at']} | `{tmpl}` | {qs} | {frags} | {new_qs} | {sess['human_direction']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Show detailed record and relations for a specific ID")
    parser.add_argument("--map-path", type=Path, default=DEFAULT_MAP_PATH, help="Path for READING_MAP.md")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write-map", action="store_true", help="Write READING_MAP.md from current state ledgers")
    action.add_argument("--check-map", action="store_true", help="Verify READING_MAP.md matches current state ledgers")
    args = parser.parse_args()

    if args.write_map:
        # Regenerate from a fresh union snapshot while holding the writer lock, and
        # replace the file atomically so a reader never sees a half-written map.
        try:
            with ledger_io.exclusive_lock(ROOT / "state" / "questions.jsonl"):
                data = load_all()
                expected_md = build_reading_map_markdown(data)
                ledger_io.atomic_write_text(args.map_path, expected_md)
        except ledger_io.LedgerLockTimeout as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(
            f"WROTE {ledger_io.display_path(args.map_path, ROOT)} "
            f"({len(expected_md.encode('utf-8'))} bytes)"
        )
        return 0

    data = load_all()

    if args.id:
        return print_record_detail(data, args.id)

    if args.check_map:
        try:
            actual_md = (
                ledger_io.read_text_stable(args.map_path) if args.map_path.is_file() else None
            )
        except ledger_io.LedgerBusy as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if actual_md != build_reading_map_markdown(data):
            print(
                f"STALE {ledger_io.display_path(args.map_path, ROOT)}: "
                "run `python3 tools/inspect_inquiry.py --write-map`",
                file=sys.stderr,
            )
            return 1
        print(
            f"PASS: {ledger_io.display_path(args.map_path, ROOT)} is up to date with state/*.jsonl"
        )
        return 0

    print_summary(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
