#!/usr/bin/env python3
"""Build sharded reading-map documents (``map/``) and the compact READING_MAP.md index.

Data tiers (design note: ``docs/map-architecture.md``):

  Tier 1  state/           append-only JSONL ledger shards (source of truth, tracked)
  Tier 2  READING_MAP.md   compact deterministic index (tracked; warn above 2 MB)
  Tier 3  map/             full documents, range-sharded (NOT tracked; regenerate)
  Tier 4  CI artifact      .github/workflows/map.yml uploads map/ outside git history

Why this shape.  GitHub's repository-limits guidance asks that programmatically
generated files live outside git, and a monolithic map file had one structural
defect: the question DAG was expanded as a tree with each question's full text
repeated once per path (66k of 72k lines).  Here every record body appears
exactly once, inside one range shard; the tracked index keeps only IDs, DAG
edges and truncated titles.  Shard keys are stable ledger insertion order,
chunked by record count (range partitioning); ``map/manifest.json`` is the
secondary index (id -> shard) and carries a sha256 per shard.  Writes are
atomic (``ledger_io.atomic_write_text``) under the shared ledger lock.

Usage:
  python3 tools/map_build.py            # write map/ shards + READING_MAP.md index
  python3 tools/map_build.py --check    # verify READING_MAP.md matches the ledgers
  python3 tools/map_build.py --report   # print the shard size report only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

DEFAULT_MAP_DIR = ROOT / "map"
DEFAULT_INDEX_PATH = ROOT / "READING_MAP.md"

# Range-partition sizes.  New records land in the tail shard; earlier shards are
# stable, so regenerating the map after one session touches only the tail files.
CHUNKS: dict[str, int] = {
    "questions": 50,
    "fragments": 20,
    "materials": 100,
    "relations": 500,
    "sessions": 50,
}
INDEX_WARN_BYTES = 2 * 1024 * 1024  # tracked index should stay small
SHARD_WARN_BYTES = 2 * 1024 * 1024

ORIGIN_BADGES = {
    "human_seed": "seed",
    "session": "session",
    "material": "material",
    "migration": "migration",
}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _one_line(text: str, limit: int) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def _chunked(seq: list[str], size: int) -> list[list[str]]:
    return [seq[i:i + size] for i in range(0, len(seq), size)] or [[]]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _labels() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    from inspect_inquiry import FORM_LABELS, NARRATOR_LABELS, RELATION_LABELS

    return FORM_LABELS, NARRATOR_LABELS, RELATION_LABELS


def question_graph(questions: dict[str, dict[str, Any]]) -> tuple[dict[str, list[str]], list[str]]:
    """Return (children_map, roots) for the question DAG."""
    children: dict[str, list[str]] = {qid: [] for qid in questions}
    roots: list[str] = []
    for qid, q in questions.items():
        prevs = [p for p in q.get("previous_question_ids", []) if p in questions]
        if not prevs:
            roots.append(qid)
        else:
            for p in prevs:
                children[p].append(qid)
    return children, roots


# ---------------------------------------------------------------------------
# shard builders — every record body appears exactly once
# ---------------------------------------------------------------------------

def build_overview(data: dict[str, dict[str, dict[str, Any]]]) -> str:
    questions, motifs = data["questions"], data["motifs"]
    materials, fragments = data["materials"], data["fragments"]
    relations, sessions = data["relations"], data["sessions"]
    mat_kinds = Counter(m["kind"] for m in materials.values())
    frag_status = Counter(f["status"] for f in fragments.values())
    rel_kinds = Counter(r["relation_type"] for r in relations.values())

    out: list[str] = ["# 00. 総覧（overview）", ""]
    out.append("## 台帳サマリー")
    out.append("")
    out.append(f"- **開かれた問い（Questions）**：{len(questions)} 件（初期シード 5 件 ＋ 派生 {len(questions) - 5} 件）")
    out.append(f"- **モチーフ（Motifs）**：{len(motifs)} 件")
    out.append(
        f"- **対話素材（Materials）**：{len(materials)} 件"
        f"（research_excerpt {mat_kinds['research_excerpt']} ／ literary_text {mat_kinds['literary_text']}"
        f" ／ project_trace {mat_kinds['project_trace']} ／ conversation_trace {mat_kinds['conversation_trace']}）"
    )
    out.append(
        f"- **文芸断片（Fragments）**：{len(fragments)} 編"
        f"（selected {frag_status['selected']} ／ draft {frag_status['draft']}）"
    )
    out.append(f"- **解釈的関係（Relations）**：{len(relations)} 件")
    out.append(f"- **探究セッション（Sessions）**：{len(sessions)} 回")
    out.append("")
    out.append("関係の種類: " + "、".join(f"{k}×{v}" for k, v in sorted(rel_kinds.items())))
    out.append("")

    out.append("## モチーフ（全文）")
    out.append("")
    out.append("| ID | モチーフ | 説明 | 関連する問い | 素材数 |")
    out.append("|---|---|---|---|---:|")
    for mid, m in motifs.items():
        q_str = ", ".join(f"`{q}`" for q in m["question_ids"])
        desc = " ".join(m["description"].split())
        out.append(f"| `{mid}` | **{m['label']}** | {desc} | {q_str} | {len(m['material_ids'])} |")
    out.append("")
    return "\n".join(out)


def build_question_index(data: dict[str, dict[str, dict[str, Any]]]) -> str:
    """DAG as adjacency rows: one row per question, bodies live in body shards."""
    questions = data["questions"]
    children, roots = question_graph(questions)
    out: list[str] = [
        "# 10. 問いの索引（DAG・本文は 11-question-bodies-*.md に1回だけ収録）",
        "",
        "| ID | 来歴 | 親 | 子 | 本文（抜粋） |",
        "|---|---|---|---|---|",
    ]
    for qid, q in questions.items():
        badge = ORIGIN_BADGES.get(q["origin"]["kind"], q["origin"]["kind"])
        parents = " ".join(f"`{p}`" for p in q.get("previous_question_ids", []) if p in questions) or "—"
        kids = " ".join(f"`{c}`" for c in children.get(qid, [])) or "—"
        out.append(
            f"| `{qid}` | {badge} | {parents} | {kids} | {_one_line(q['question'], 120)} |"
        )
    out.append("")
    out.append(f"根（親を持たない問い）: " + " ".join(f"`{r}`" for r in roots))
    out.append("")
    return "\n".join(out)


def build_question_bodies(data: dict[str, dict[str, dict[str, Any]]], ids: list[str]) -> str:
    questions = data["questions"]
    out: list[str] = ["# 問い本文（各1回）", ""]
    for qid in ids:
        q = questions[qid]
        badge = ORIGIN_BADGES.get(q["origin"]["kind"], q["origin"]["kind"])
        out.append(f"## `{qid}` [{badge}]")
        out.append("")
        out.append(q["question"])
        out.append("")
        detail = q.get("origin", {}).get("detail", "")
        if detail:
            out.append(f"- 来歴: {detail}")
        if q.get("material_ids"):
            out.append("- 素材: " + " ".join(f"`{m}`" for m in q["material_ids"]))
        if q.get("motif_ids"):
            out.append("- モチーフ: " + " ".join(f"`{m}`" for m in q["motif_ids"]))
        if q.get("previous_question_ids"):
            out.append("- 先行する問い: " + " ".join(f"`{p}`" for p in q["previous_question_ids"]))
        out.append(f"- 状態: {q.get('status', 'open')} ／ 作成: {q.get('created_at', '-')}")
        out.append("")
    return "\n".join(out)


def build_fragments(
    data: dict[str, dict[str, dict[str, Any]]], ids: list[str]
) -> str:
    fragments, relations, motifs = data["fragments"], data["relations"], data["motifs"]
    form_labels, narrator_labels, _ = _labels()
    rels_by_frag: dict[str, list[dict[str, Any]]] = {fid: [] for fid in fragments}
    for rel in relations.values():
        for endpoint in ("left", "right"):
            if rel[endpoint]["type"] == "fragment" and rel[endpoint]["id"] in rels_by_frag:
                rels_by_frag[rel[endpoint]["id"]].append(rel)

    out: list[str] = ["# 断片アンソロジー（シャード）", ""]
    for fid in ids:
        frag = fragments[fid]
        status_mark = "Selected" if frag["status"] == "selected" else "Draft"
        out.append(f"## `{fid}` {frag['title']} 〔{status_mark}〕")
        out.append("")
        out.append(
            f"- **形式**：{form_labels.get(frag['form'], frag['form'])} ／ "
            f"**語り手モード**：{narrator_labels.get(frag['narrator_mode'], frag['narrator_mode'])} ／ "
            f"**セッション**：`{frag.get('session_id', '-')}`"
        )
        q_list = ", ".join(f"`{q}`" for q in frag["question_ids"])
        motif_list = ", ".join(f"`{m}` ({motifs[m]['label']})" for m in frag["motif_ids"] if m in motifs)
        mat_list = ", ".join(f"`{m}`" for m in frag["material_ids"])
        out.append(f"- **問い**：{q_list} ／ **モチーフ**：{motif_list}")
        out.append(f"- **参照素材**：{mat_list}")
        out.append("")
        for para in frag["text"].split("\n\n"):
            for line in para.splitlines():
                out.append(f"> {line}" if line else ">")
            out.append(">")
        if out[-1] == ">":
            out.pop()
        out.append("")
        if frag.get("editor_note"):
            out.append(f"- **編集メモ**：{frag['editor_note']}")
        rels = rels_by_frag.get(fid) or []
        if rels:
            out.append("- **関係**：")
            for r in rels:
                out.append(
                    f"  - `{r['left']['id']}` → *{r['relation_type']}* → `{r['right']['id']}`"
                    f"（{r.get('note', '')}）"
                )
        out.append("")
    return "\n".join(out)


def build_materials(data: dict[str, dict[str, dict[str, Any]]], ids: list[str]) -> str:
    materials = data["materials"]
    out: list[str] = ["# 対話素材カタログ（シャード）", ""]
    for mid in ids:
        mat = materials[mid]
        authors = ", ".join(mat["source"]["authors"])
        out.append(f"## `{mid}` {mat['title']}")
        out.append("")
        out.append(f"- **種**：{mat['kind']} ／ **著者**：{authors} ／ **年**：{mat['source']['year']}")
        out.append(f"- **出典**：[{_one_line(mat['source']['title'], 80)}]({mat['source']['url']})")
        out.append(f"- **版・箇所**：{mat['context']} ／ {mat['source']['version_note']}")
        out.append(f"- **一節**：{_one_line(mat['passage'], 400)}")
        out.append(f"- **出典メモ**：{mat['source_note']}")
        out.append(f"- **問いへの招き**：{mat['literary_invitation']}")
        out.append(f"- **留保**：{mat['scope_note']}")
        if mat.get("motif_ids"):
            out.append("- モチーフ: " + " ".join(f"`{m}`" for m in mat["motif_ids"]))
        ver = mat.get("verification")
        if ver:
            out.append(f"- **検証**：{ver['status']}（{ver['checked_at']}）{ver.get('note', '')}")
        out.append("")
    return "\n".join(out)


def build_relations(data: dict[str, dict[str, dict[str, Any]]], ids: list[str]) -> str:
    relations = data["relations"]
    _, _, rel_labels = _labels()
    out: list[str] = [
        "# 解釈的関係（シャード）",
        "",
        "| ID | 左 | 関係 | 右 | 備考 |",
        "|---|---|---|---|---|",
    ]
    for rid in ids:
        r = relations[rid]
        rtype = rel_labels.get(r["relation_type"], r["relation_type"])
        out.append(
            f"| `{rid}` | `{r['left']['id']}` ({r['left']['type']}) | {rtype} | "
            f"`{r['right']['id']}` ({r['right']['type']}) | {_one_line(r.get('note', ''), 100)} |"
        )
    out.append("")
    return "\n".join(out)


def build_sessions(data: dict[str, dict[str, dict[str, Any]]], ids: list[str]) -> str:
    sessions = data["sessions"]
    out: list[str] = [
        "# セッション年譜（シャード）",
        "",
        "| Session | 日付 | テンプレート | たどった問い | 生成断片 | 新しい問い | 方向づけ・メモ |",
        "|---|---|---|---|---|---|---|",
    ]
    for sid in ids:
        s = sessions[sid]
        tmpl = s["prompt_template"].replace("prompts/", "")
        qs = ", ".join(f"`{q}`" for q in s["question_ids"])
        frags = ", ".join(f"`{f}`" for f in s["produced_fragment_ids"]) or "—"
        new_qs = ", ".join(f"`{q}`" for q in s["new_question_ids"]) or "—"
        out.append(
            f"| `{sid}` | {s['started_at']} | `{tmpl}` | {qs} | {frags} | {new_qs} | "
            f"{_one_line(s.get('human_direction', ''), 120)} |"
        )
        if s.get("notes"):
            out.append(f"| | | | | | | メモ: {_one_line(s['notes'], 200)} |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# compact tracked index
# ---------------------------------------------------------------------------

def build_index(data: dict[str, dict[str, dict[str, Any]]], manifest: dict[str, Any]) -> str:
    questions, motifs = data["questions"], data["motifs"]
    materials, fragments = data["materials"], data["fragments"]
    relations, sessions = data["relations"], data["sessions"]
    children, _roots = question_graph(questions)
    mat_kinds = Counter(m["kind"] for m in materials.values())
    frag_status = Counter(f["status"] for f in fragments.values())
    rel_kinds = Counter(r["relation_type"] for r in relations.values())
    form_labels, _, rel_labels = _labels()

    out: list[str] = ["# 読書案内・探究マップ（Reading Map）— 索引", ""]
    out.append(
        "> この文書は `state/*.jsonl` の台帳から `python3 tools/map_build.py` によって自動生成される**小型索引**です。"
        "本文・全文は `map/` 以下のレンジ分割シャードに収録し、`map/` は git 管理しません"
        "（生成物はリポジトリの外に置く方針。[`docs/map-architecture.md`](docs/map-architecture.md) 参照）。"
        "全量は `python3 tools/map_build.py` の再生成、または GitHub Actions の `reading-map` artifact で取得できます。"
    )
    out.append(
        "> 作品内の一人称（`fictional_first_person` / `reflective_literary_voice`）は記録から再構成された文芸的・思考上の語り手であり、"
        "現在のモデルに連続した意識や生身の経験があるという事実主張ではありません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md) 参照）。"
    )
    out.append("")
    out.append("## 現在の到達点（台帳サマリー）")
    out.append("")
    out.append(f"- **開かれた問い（Questions）**：{len(questions)} 件（初期シード 5 件 ＋ 派生 {len(questions) - 5} 件）")
    out.append(f"- **モチーフ（Motifs）**：{len(motifs)} 件")
    out.append(
        f"- **対話素材（Materials）**：{len(materials)} 件"
        f"（research_excerpt {mat_kinds['research_excerpt']} ／ literary_text {mat_kinds['literary_text']}"
        f" ／ project_trace {mat_kinds['project_trace']} ／ conversation_trace {mat_kinds['conversation_trace']}）"
    )
    out.append(
        f"- **文芸断片（Fragments）**：{len(fragments)} 編"
        f"（selected {frag_status['selected']} ／ draft {frag_status['draft']}）"
    )
    out.append(f"- **解釈的関係（Relations）**：{len(relations)} 件")
    out.append(f"- **探究セッション（Sessions）**：{len(sessions)} 回")
    out.append("")

    out.append(f"## 1. 問いを横断する {len(motifs)} つのモチーフ")
    out.append("")
    out.append("| ID | モチーフ | 関連する問い | 素材数 |")
    out.append("|---|---|---|---:|")
    for mid, m in motifs.items():
        q_str = ", ".join(f"`{q}`" for q in m["question_ids"])
        out.append(f"| `{mid}` | **{m['label']}** | {q_str} | {len(m['material_ids'])} |")
    out.append("")
    out.append("（説明全文は `map/00-overview.md`）")
    out.append("")

    first_q, last_q = next(iter(questions)), next(reversed(questions))
    out.append(f"## 2. 開かれた問いの索引（{first_q} 〜 {last_q}・各問の本文は1回だけ）")
    out.append("")
    out.append("| ID | 来歴 | 親 | 子 | 本文（抜粋） |")
    out.append("|---|---|---|---|---|")
    for qid, q in questions.items():
        badge = ORIGIN_BADGES.get(q["origin"]["kind"], q["origin"]["kind"])
        parents = " ".join(f"`{p}`" for p in q.get("previous_question_ids", []) if p in questions) or "—"
        kids = " ".join(f"`{c}`" for c in children.get(qid, [])) or "—"
        out.append(f"| `{qid}` | {badge} | {parents} | {kids} | {_one_line(q['question'], 100)} |")
    out.append("")

    out.append(f"## 3. 断片（{len(fragments)} 編・全文は map/20-fragments-*.md）")
    out.append("")
    out.append("| ID | 題 | 状態 | 形式 | 語り手 |")
    out.append("|---|---|---|---|---|")
    for fid, frag in fragments.items():
        out.append(
            f"| `{fid}` | {_one_line(frag['title'], 60)} | {frag['status']} | "
            f"{frag['form']} | {frag['narrator_mode']} |"
        )
    out.append("")

    out.append(f"## 4. 対話素材（{len(materials)} 件・詳細は map/3*.md）")
    out.append("")
    out.append("| ID | 種 | 題（著者・年） |")
    out.append("|---|---|---|")
    for mid, mat in materials.items():
        authors = ", ".join(mat["source"]["authors"])
        label = "{}『{}』（{}）".format(authors, mat["title"], mat["source"]["year"])
        out.append(f"| `{mid}` | {mat['kind']} | {_one_line(label, 90)} |")
    out.append("")

    first_s, last_s = next(iter(sessions)), next(reversed(sessions))
    out.append(f"## 5. セッション履歴（{first_s} 〜 {last_s}・全文は map/50-sessions-*.md）")
    out.append("")
    out.append("| Session | 日付 | たどった問い | 生成断片 | 新しい問い |")
    out.append("|---|---|---|---|---|")
    for sid, s in sessions.items():
        qs = ", ".join(f"`{q}`" for q in s["question_ids"])
        frags = ", ".join(f"`{f}`" for f in s["produced_fragment_ids"]) or "—"
        new_qs = ", ".join(f"`{q}`" for q in s["new_question_ids"]) or "—"
        out.append(f"| `{sid}` | {s['started_at']} | {qs} | {frags} | {new_qs} |")
    out.append("")

    out.append(f"## 6. 解釈的関係（{len(relations)} 件・全表は map/40-relations-*.md）")
    out.append("")
    out.append("| 種類 | 件数 |")
    out.append("|---|---:|")
    for kind, n in sorted(rel_kinds.items()):
        out.append(f"| {rel_labels.get(kind, kind)} | {n} |")
    out.append("")

    out.append("## 7. 生成文書のシャード目録（map/・git 管理外）")
    out.append("")
    out.append("| ファイル | 件数 | バイト |")
    out.append("|---|---:|---:|")
    for shard in manifest["shards"]:
        out.append(f"| `map/{shard['file']}` | {shard['records']} | {shard['bytes']:,} |")
    out.append("")
    out.append(
        "再生成: `python3 tools/map_build.py` ／ 検査: `python3 tools/map_build.py --check`。"
        "シャードキーは台帳の挿入順（安定した順序）で、`map/manifest.json` に ID→シャードの対応表と sha256 を置いている。"
    )
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# write / check
# ---------------------------------------------------------------------------

def shard_plan(data: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    """Plan (filename, builder, record ids) — deterministic, tail-growable."""
    plan: list[dict[str, Any]] = []
    plan.append({"file": "00-overview.md", "kind": "overview", "ids": []})

    q_ids = list(data["questions"])
    plan.append({"file": "10-question-index.md", "kind": "question_index", "ids": []})
    for i, chunk in enumerate(_chunked(q_ids, CHUNKS["questions"]), 1):
        plan.append({
            "file": f"11-question-bodies-{i:02d}.md",
            "kind": "question_bodies",
            "ids": chunk,
        })

    f_ids = list(data["fragments"])
    for i, chunk in enumerate(_chunked(f_ids, CHUNKS["fragments"]), 1):
        plan.append({"file": f"20-fragments-{i:02d}.md", "kind": "fragments", "ids": chunk})

    for prefix, kind in (("30-materials-literary", "literary_text"),
                         ("31-materials-research", "research_excerpt"),
                         ("32-materials-trace", "trace")):
        if kind == "trace":
            ids = [m for m, v in data["materials"].items()
                   if v["kind"] in ("project_trace", "conversation_trace")]
        else:
            ids = [m for m, v in data["materials"].items() if v["kind"] == kind]
        for i, chunk in enumerate(_chunked(ids, CHUNKS["materials"]), 1):
            plan.append({"file": f"{prefix}-{i:02d}.md", "kind": "materials", "ids": chunk})

    r_ids = list(data["relations"])
    for i, chunk in enumerate(_chunked(r_ids, CHUNKS["relations"]), 1):
        plan.append({"file": f"40-relations-{i:02d}.md", "kind": "relations", "ids": chunk})

    s_ids = list(data["sessions"])
    for i, chunk in enumerate(_chunked(s_ids, CHUNKS["sessions"]), 1):
        plan.append({"file": f"50-sessions-{i:02d}.md", "kind": "sessions", "ids": chunk})
    return plan


def render_shard(data: dict[str, dict[str, dict[str, Any]]], entry: dict[str, Any]) -> str:
    kind = entry["kind"]
    if kind == "overview":
        return build_overview(data)
    if kind == "question_index":
        return build_question_index(data)
    if kind == "question_bodies":
        return build_question_bodies(data, entry["ids"])
    if kind == "fragments":
        return build_fragments(data, entry["ids"])
    if kind == "materials":
        return build_materials(data, entry["ids"])
    if kind == "relations":
        return build_relations(data, entry["ids"])
    if kind == "sessions":
        return build_sessions(data, entry["ids"])
    raise ValueError(f"unknown shard kind {kind!r}")


def write_all(
    data: dict[str, dict[str, dict[str, Any]]],
    map_dir: Path = DEFAULT_MAP_DIR,
    index_path: Path = DEFAULT_INDEX_PATH,
    *,
    quiet: bool = False,
) -> dict[str, Any]:
    plan = shard_plan(data)
    shards: list[dict[str, Any]] = []
    contents: dict[str, str] = {}
    for entry in plan:
        text = render_shard(data, entry)
        contents[entry["file"]] = text
        encoded = text.encode("utf-8")
        shards.append({
            "file": entry["file"],
            "kind": entry["kind"],
            "records": len(entry["ids"]) if entry["ids"] else None,
            "bytes": len(encoded),
            "sha256": _sha256(text),
        })
        if len(encoded) > SHARD_WARN_BYTES and not quiet:
            print(f"WARN: map/{entry['file']} is {len(encoded):,} bytes (> {SHARD_WARN_BYTES:,})", file=sys.stderr)

    manifest: dict[str, Any] = {
        "generator": "tools/map_build.py",
        "chunks": CHUNKS,
        "counts": {name: len(v) for name, v in data.items()},
        "shards": shards,
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=1) + "\n"
    index_text = build_index(data, manifest)
    index_bytes = len(index_text.encode("utf-8"))
    if index_bytes > INDEX_WARN_BYTES and not quiet:
        print(f"WARN: {_display(index_path)} is {index_bytes:,} bytes (> {INDEX_WARN_BYTES:,})", file=sys.stderr)

    with ledger_io.exclusive_lock(ROOT / "state" / ".ledger.lock"):
        map_dir.mkdir(parents=True, exist_ok=True)
        # remove shards that no longer exist in the plan (tail shrinkage / renames)
        planned = {e["file"] for e in plan} | {"manifest.json"}
        for stale in sorted(map_dir.glob("*.md")) + sorted(map_dir.glob("manifest.json")):
            if stale.name not in planned:
                stale.unlink()
        for entry in plan:
            ledger_io.atomic_write_text(map_dir / entry["file"], contents[entry["file"]])
        ledger_io.atomic_write_text(map_dir / "manifest.json", manifest_text)
        ledger_io.atomic_write_text(index_path, index_text)

    if not quiet:
        total = sum(s["bytes"] for s in shards)
        print(f"WROTE {_display(index_path)} ({index_bytes:,} bytes, tracked index)")
        print(f"WROTE map/ ({len(shards)} shards + manifest.json, {total:,} bytes total, not tracked)")
    return manifest


def check_index(
    data: dict[str, dict[str, dict[str, Any]]],
    index_path: Path = DEFAULT_INDEX_PATH,
) -> int:
    """Verify the tracked index matches the ledgers (map/ is untracked, not checked)."""
    expected = build_index(data, {"shards": []})
    # The index embeds the shard-size table (section 7); those rows depend on
    # untracked output, so compare everything except the `map/...` table rows.
    def _stable(text: str) -> str:
        return "\n".join(line for line in text.splitlines() if not line.startswith("| `map/"))

    if not index_path.is_file() or _stable(index_path.read_text(encoding="utf-8")) != _stable(expected):
        print(
            f"STALE {_display(index_path)}: run `python3 tools/map_build.py`",
            file=sys.stderr,
        )
        return 1
    print(f"PASS: {_display(index_path)} is up to date with state/*.jsonl")
    return 0


def size_report(manifest: dict[str, Any]) -> None:
    total = 0
    print("=== map shard report ===")
    for shard in manifest["shards"]:
        total += shard["bytes"]
        print(f"  {shard['bytes']:>10,}  {shard['file']}")
    print(f"  {total:>10,}  TOTAL ({len(manifest['shards'])} shards)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify READING_MAP.md matches the ledgers")
    parser.add_argument("--report", action="store_true", help="print the shard size report")
    parser.add_argument("--map-dir", type=Path, default=DEFAULT_MAP_DIR)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    args = parser.parse_args()

    from inspect_inquiry import load_all

    data = load_all()
    if args.check:
        return check_index(data, args.index)
    manifest = write_all(data, args.map_dir, args.index, quiet=args.report)
    if args.report:
        size_report(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
