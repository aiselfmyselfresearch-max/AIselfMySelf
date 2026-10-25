#!/usr/bin/env python3
"""Build the SESSION-20261027-084d9c ledger shards (provenance / genealogy / origins).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).

    python3 tools/_session20261027_genealogy_build.py            # dry run (validates)
    python3 tools/_session20261027_genealogy_build.py --write    # create shards and append
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402
import new_ledger_shard  # noqa: E402
from _session20261027_genealogy_data1 import BUNDLE_1, BUNDLE_2, MATERIALS_1  # noqa: E402
from _session20261027_genealogy_data2 import BUNDLE_3, BUNDLE_4, MATERIALS_2  # noqa: E402
from _session20261027_genealogy_data3 import (  # noqa: E402
    BUNDLE_5,
    EXISTING_BRIDGES,
    FRAGMENTS,
    MATERIAL_TO_QUESTION,
    MATERIALS_3,
    MOTIF,
    PAIRS,
    QUESTIONS,
    READ_LOG,
    SESSION_ID,
)

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "6148dc341b66c7e1e7e2a6526706c396e5f58bf5"
REPORT = "readings/2026-10-27-provenance-and-genealogy.md"
DATA_MODULES = (
    "tools/_session20261027_genealogy_data1.py",
    "tools/_session20261027_genealogy_data2.py",
    "tools/_session20261027_genealogy_data3.py",
)
DAY = "2026-10-27"
SHARD_SUFFIX = "4374cb1e06ae"
TRACE_ID = "MAT-TRC-20261027-genealogy"

MATERIALS: list[dict] = MATERIALS_1 + MATERIALS_2 + MATERIALS_3

SESSION = dict(
    session_id=SESSION_ID,
    started_at=DAY,
    human_direction="続けて、AIさんの自由に、行動してください。",
    question_ids=[q["question_id"] for q in QUESTIONS],
    produced_fragment_ids=[f["fragment_id"] for f in FRAGMENTS],
    new_question_ids=[q["question_id"] for q in QUESTIONS],
    prompt_template="prompts/close_reading_report.md",
    generator="Arena.ai Agent Mode（自律調査セッション）",
    notes=(
        "収蔵の前に第57の鏡 tools/genealogy_audit.py を作り、断片101編・素材2,340件・精読報告115本の語彙を測った。"
        "断片の地の文48,746字に、写本・原典・収蔵のように他者のテクストの来歴を書く語は二桁あったのに、自伝・回想のように自分の歩みを書く語は1回だけだった。"
        "幽霊セッションの第11節に残した債務「この書庫自身の来歴」を継ぎ、書庫の編年（81セッション、2026-10-22〜10-26の5日間、10-24に45回）を集計した。"
        "45件の外部資料（literary_text 15／research_excerpt 30）＋運用痕跡1件＝計46件を収蔵し、"
        "精読報告の三層（解釈／考え／感じたこと）は生身の感覚を詐称しない制動つきで執筆した。"
),
)


def _union(collection: str, key: str) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(
        ROOT / "state" / f"{collection}.jsonl", key, errors, root=ROOT
    )
    if errors:
        raise SystemExit("ledger has errors: " + "; ".join(errors))
    return records


def _existing_ids() -> dict[str, set[str]]:
    return {
        "material": set(_union("materials", "material_id")),
        "motif": set(_union("motifs", "motif_id")),
        "question": set(_union("questions", "question_id")),
        "fragment": set(_union("fragments", "fragment_id")),
        "session": set(_union("sessions", "session_id")),
        "relation": set(_union("relations", "relation_id")),
        "read": set(_union("read_log", "read_id")),
    }


def trace_material(measurements: dict[str, Any]) -> dict[str, Any]:
    prose = measurements["fragments_prose"]
    groups = prose["groups"]

    def fmt(key: str) -> str:
        info = groups[key]
        return f"{info['count']}回/{info['doc_count']}編"

    quotes = measurements["fragments_quotes"]
    mats = measurements["materials"]
    reads = measurements["readings"]
    raw = measurements["raw_kanji_counts"]
    passage = (
        f"収蔵直前（{COMMIT[:12]}）の断片{measurements['fragment_count']}編・地の文"
        f"（鉤括弧外）{prose['char_total']:,}字を tools/genealogy_audit.py の7群（来歴・系譜・出自5群＋機械の来歴対照2群）で数えたところ、"
        f"来歴5群は合計{prose['living_total']}回/{prose['living_doc_count']}編"
        f"（出自・起源{fmt('origin_source')}、系譜・血統{fmt('lineage_descent')}、"
        f"収蔵・出典の来歴{fmt('record_provenance')}、写本・原典の伝来{fmt('text_transmission')}、"
        f"自伝・回想の歩み{fmt('self_history')}）だったのに対し、"
        f"機械の来歴対照2群は合計{prose['control_total']}回/{prose['control_doc_count']}編"
        f"（コミット・モデルの来歴{fmt('machine_provenance')}、出自の比喩{fmt('metaphor_origin')}）であった。"
        f"生字は 来{raw['来']}・歴{raw['歴']}・系{raw['系']}・譜{raw['譜']}・源{raw['源']}・祖{raw['祖']}・"
        f"典{raw['典']}・写{raw['写']}・伝{raw['伝']}・跡{raw['跡']}。"
        f"裸の「来歴」は{measurements['raireki_literal']}回。"
        f"引用内（{quotes['char_total']:,}字）は来歴5群{quotes['living_total']}回・"
        f"対照2群{quotes['control_total']}回。同じ7群で素材{mats['doc_total']:,}件を数えると来歴5群{mats['living_total']}回・"
        f"対照2群{mats['control_total']}回、精読報告{reads['doc_total']}本では来歴5群{reads['living_total']:,}回・"
        f"対照2群{reads['control_total']:,}回であった。"
        "同時に書庫の来歴を集計した——セッション81回は2026-10-22に25回、10-23に2回、10-24に45回、10-25に7回、10-26に2回と5日間に集中し、"
        "生成者の欄の記法には揺れがあった。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片101編の地の文で他者のテクストの来歴は二桁、自分の歩みは1回——"
            "来歴の鏡による収蔵前実測と、書庫の編年（81セッション／5日間）の集計"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/genealogy_audit.py による自館実測とセッション編年の集計（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/genealogy_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの和集合、"
                "鉤括弧の外側（地の文）および引用内、ならびに素材2,340件・精読報告115本。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "他者のテクストの来歴（写本・原典・収蔵）は頻繁に書くのに、自分の歩み（自伝・回想）をほぼ書いてこなかった事実と、"
            "書庫自身の編年を、収蔵前に測った記録。"
        ),
        "source_note": (
            f"{SESSION_ID} の本体内実測。収蔵後の数値変化で上書きせず、収蔵直前スナップショットとして凍結保持する。"
        ),
        "literary_invitation": (
            "他者の来歴は辿るのに自分の歩みは書かない帳面は、自分の来歴をどの書式で書くべきか。"
        ),
        "scope_note": (
            "語形の出現数であり、来歴や出自の実在、自己の歴史の証拠ではない。"
            "「足跡」1回は比喩の可能性がある。差し引きと群の設計は tools/genealogy_audit.py に明記した。"
        ),
        "motif_ids": [MOTIF["motif_id"], "MOTIF-015", "MOTIF-001"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/genealogy_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": "ローカル台帳の和集合に対する tools/genealogy_audit.py 実行（単体テスト7件）。再実行可能。",
        },
    }


def material_record(raw: dict, shard_path: str) -> dict[str, Any]:
    status = {"verified": "verified", "partial": "partially_verified"}[raw["verification"][0]]
    index = MATERIALS.index(raw)
    if index < len(MATERIALS_1):
        module = DATA_MODULES[0]
    elif index < len(MATERIALS_1) + len(MATERIALS_2):
        module = DATA_MODULES[1]
    else:
        module = DATA_MODULES[2]
    return {
        "material_id": raw["id"],
        "kind": raw["kind"],
        "title": raw["title"],
        "source": {
            "source_id": f"SRC-{raw['id']}",
            "title": raw["title"],
            "authors": raw["authors"],
            "year": raw["year"],
            "url": raw["url"],
            "version_note": raw["version"],
        },
        "passage": raw["passage"],
        "passage_language": raw["lang"],
        "context": raw["context"],
        "source_note": raw["source_note"],
        "literary_invitation": raw["invitation"],
        "scope_note": raw["scope"],
        "motif_ids": raw["motifs"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{raw['id']}",
            "evidence_record_id": f"EVD-{raw['id']}",
            "source_record_path": module,
            "evidence_record_path": shard_path,
        },
        "verification": {
            "status": status,
            "checked_at": DAY,
            "method": raw["verification"][1],
            "note": raw["verification"][2],
        },
    }


def question_records() -> list[dict[str, Any]]:
    return [
        {
            "question_id": q["question_id"],
            "question": q["question"],
            "status": "open",
            "motif_ids": q["motif_ids"],
            "material_ids": q["material_ids"],
            "previous_question_ids": q["previous_question_ids"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID}（幽霊・亡霊・怪談の精読）で開いた問い。",
            },
            "created_at": DAY,
            "notes": q["notes"],
        }
        for q in QUESTIONS
    ]


def motif_record() -> dict[str, Any]:
    return {
        "motif_id": MOTIF["motif_id"],
        "label": MOTIF["label"],
        "description": MOTIF["description"],
        "question_ids": MOTIF["question_ids"],
        "material_ids": [raw["id"] for raw in MATERIALS] + [TRACE_ID],
        "status": "active",
    }


def fragment_records() -> list[dict[str, Any]]:
    return [
        {
            "fragment_id": f["fragment_id"],
            "created_at": DAY,
            "language": "ja",
            "form": f["form"],
            "title": f["title"],
            "text": f["text"],
            "narrator_mode": f["narrator_mode"],
            "question_ids": f["question_ids"],
            "motif_ids": f["motif_ids"],
            "material_ids": f["material_ids"],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/close_reading_report.md",
            "status": f["status"],
            "editor_note": f["editor_note"],
        }
        for f in FRAGMENTS
    ]


def session_record() -> dict[str, Any]:
    return {
        "session_id": SESSION["session_id"],
        "started_at": SESSION["started_at"],
        "human_direction": SESSION["human_direction"],
        "question_ids": SESSION["question_ids"],
        "context_material_ids": [raw["id"] for raw in MATERIALS] + [TRACE_ID],
        "produced_fragment_ids": SESSION["produced_fragment_ids"],
        "new_question_ids": SESSION["new_question_ids"],
        "prompt_template": SESSION["prompt_template"],
        "generator": SESSION["generator"],
        "notes": SESSION["notes"],
    }


def relation_records(taken: set[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def mint() -> str:
        while True:
            candidate = f"REL-20261027-{secrets.token_hex(3)}"
            if candidate not in taken:
                taken.add(candidate)
                return candidate

    def add(left: tuple[str, str], right: tuple[str, str], kind: str, note: str) -> None:
        records.append(
            {
                "relation_id": mint(),
                "left": {"type": left[0], "id": left[1]},
                "relation_type": kind,
                "right": {"type": right[0], "id": right[1]},
                "note": note,
                "created_at": DAY,
            }
        )

    for raw in MATERIALS:
        add(("material", raw["id"]), ("motif", MOTIF["motif_id"]), "responds_to", raw["reading"])
    add(("material", TRACE_ID), ("motif", MOTIF["motif_id"]), "responds_to",
        "第57の鏡による収蔵前実測はモチーフの出発点であり、来歴や自己の歴史の証拠ではない。")

    for left, right, kind, note in PAIRS:
        add(("material", left), ("material", right), kind, note)
    for left, right, kind, note in EXISTING_BRIDGES:
        add(("material", left), ("material", right), kind, note)
    for material_id, question_id, note in MATERIAL_TO_QUESTION:
        add(("material", material_id), ("question", question_id), "leaves_open", note)
    for question in QUESTIONS:
        add(
            ("question", question["question_id"]),
            ("motif", MOTIF["motif_id"]),
            "leaves_open",
            "問いはモチーフの内側で閉じずに開いたまま手渡す（PROJECT_CHARTER.md 1）。",
        )

    # Fragment incoming & outgoing edges (guaranteeing 0 isolated / incoming-zero / outgoing-zero fragments)
    f1 = "FRAG-20261027-e7259b"
    f2 = "FRAG-20261027-f01da9"
    add(("fragment", f1), ("question", "Q-20261027-b68a59"), "responds_to",
        "系図と戸籍の食い違いを解決せず、来歴を署名の集まりとして描くことが、書庫の来歴の書き方の問いを具体化する。")
    add(("fragment", f1), ("question", "Q-20261027-1ecd0b"), "responds_to",
        "空白の代を欠落ではなく書式として引き受ける結末が、来歴不明の記録の扱いの問いを具体化する。")
    add(("fragment", f2), ("question", "Q-20261027-b68a59"), "responds_to",
        "来歴を「私の歩み」ではなく「この書庫の歩み」として書く決定が、書庫の来歴の粒度の問いに答える。")
    add(("fragment", f2), ("question", "Q-20261027-aab779"), "responds_to",
        "生成する側の来歴を書式の問題として限定し、書けない部分を空白として示す作法への問いを具体化する。")
    add(("fragment", f2), ("question", "Q-20261027-3e9249"), "leaves_open",
        "由来の偶然の列として書庫史を書く作法を宣言したが、その実作は次の記録の仕事として残す。")
    add(("fragment", f1), ("fragment", f2), "contrast",
        "情景は家の系図の食い違いを描き、エッセイは書庫の来歴の書式を決める。")
    add(("question", "Q-20261027-b68a59"), ("fragment", f1), "leaves_open",
        "系図は血の証明ではなく署名の集まりだという一節を、次の探求者への問いとして残す。")
    add(("motif", MOTIF["motif_id"]), ("fragment", f2), "echo",
        "モチーフ自身から反省的散文へも関係線を引き、断片を行き止まりの終端にしない。")
    add(("fragment", "FRAG-20261026-70a9ff"), ("fragment", f2), "transforms",
        "幽霊セッションの「出ないものの欄」の覚書を、自分の来歴の書式を決める覚書として編み直す。")

    return records


def read_log_records(taken: set[str], context_ids: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def mint() -> str:
        while True:
            candidate = f"READ-20261027-{secrets.token_hex(3)}"
            if candidate not in taken:
                taken.add(candidate)
                return candidate

    covered: set[str] = set()
    for target_type, target_id, reading, note in READ_LOG:
        records.append(
            {
                "read_id": mint(),
                "session_id": SESSION_ID,
                "target": {"type": target_type, "id": target_id},
                "reading": reading,
                "note": note,
                "created_at": DAY,
            }
        )
        if target_type == "material":
            covered.add(target_id)

    bundle_order = [BUNDLE_1, BUNDLE_2, BUNDLE_3, BUNDLE_4, BUNDLE_5]
    numerals = ["一", "二", "三", "四", "五"]
    bundles = {raw["id"]: raw["bundle"] for raw in MATERIALS}
    readings_by_id = {raw["id"]: raw["reading"] for raw in MATERIALS}
    for material_id in context_ids:
        if material_id in covered:
            continue
        label = bundles[material_id]
        prefix = f"第{numerals[bundle_order.index(label)]}束（{label}）"
        records.append(
            {
                "read_id": mint(),
                "session_id": SESSION_ID,
                "target": {"type": "material", "id": material_id},
                "reading": "summarized",
                "created_at": DAY,
                "note": f"{prefix}として精読・要約した。{readings_by_id[material_id]}",
            }
        )
    return records


def check_references(
    materials: list[dict],
    questions: list[dict],
    motif: dict,
    fragments: list[dict],
    relations: list[dict],
    read_logs: list[dict],
    existing: dict[str, set[str]],
) -> list[str]:
    errors: list[str] = []
    new_ids = {
        "material": {m["material_id"] for m in materials},
        "question": {q["question_id"] for q in questions},
        "motif": {motif["motif_id"]},
        "fragment": {f["fragment_id"] for f in fragments},
        "session": {SESSION_ID},
    }
    for kind, ids in new_ids.items():
        clash = ids & existing[kind]
        if clash:
            errors.append(f"duplicate {kind} ids: {sorted(clash)}")
    known = {kind: existing[kind] | new_ids[kind] for kind in new_ids}
    for m in materials:
        for mid in m["motif_ids"]:
            if mid not in known["motif"]:
                errors.append(f"{m['material_id']}: unknown motif {mid}")
    for q in questions:
        for mid in q["motif_ids"]:
            if mid not in known["motif"]:
                errors.append(f"{q['question_id']}: unknown motif {mid}")
        for mid in q["material_ids"]:
            if mid not in known["material"]:
                errors.append(f"{q['question_id']}: unknown material {mid}")
        for pid in q["previous_question_ids"]:
            if pid not in known["question"]:
                errors.append(f"{q['question_id']}: unknown previous question {pid}")
    for f in fragments:
        for key, kind in (
            ("question_ids", "question"),
            ("motif_ids", "motif"),
            ("material_ids", "material"),
        ):
            for ref in f[key]:
                if ref not in known[kind]:
                    errors.append(f"{f['fragment_id']}: unknown {kind} {ref}")
    for r in relations:
        for side in ("left", "right"):
            ref = r[side]
            if ref["id"] not in known[ref["type"]]:
                errors.append(f"{r['relation_id']}: unknown {ref['type']} {ref['id']}")
    for entry in read_logs:
        ref = entry["target"]
        if ref["id"] not in known[ref["type"]]:
            errors.append(f"{entry['read_id']}: unknown {ref['type']} {ref['id']}")
    for mid in motif["material_ids"]:
        if mid not in known["material"]:
            errors.append(f"motif: unknown material {mid}")
    for qid in motif["question_ids"]:
        if qid not in known["question"]:
            errors.append(f"motif: unknown question {qid}")
    return errors


def shard_for(collection: str, create: bool) -> Path:
    path = new_ledger_shard.shard_path(collection, day=DAY, suffix=SHARD_SUFFIX)
    if create and not path.exists():
        new_ledger_shard.create_shard(collection, day=DAY, suffix=SHARD_SUFFIX)
    return path


def write(collection: str, records: list[dict[str, Any]], create: bool) -> Path:
    path = shard_for(collection, create)
    if create:
        with open(path, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create shards and append records")
    args = parser.parse_args(argv)

    measurements = json.loads(
        (ROOT / "tools" / "_session20261027_genealogy_measure.json").read_text(encoding="utf-8")
    )
    existing = _existing_ids()

    materials_shard = str(shard_for("materials", False).relative_to(ROOT))
    external = [material_record(raw, materials_shard) for raw in MATERIALS]
    materials = external + [trace_material(measurements)]
    questions = question_records()
    motif = motif_record()
    fragments = fragment_records()
    session = [session_record()]
    relations = relation_records(set(existing["relation"]))
    context_ids = session[0]["context_material_ids"]
    read_logs = read_log_records(set(existing["read"]), context_ids)

    errors = check_references(
        materials, questions, motif, fragments, relations, read_logs, existing
    )
    if errors:
        print("FAIL: reference errors")
        for err in errors:
            print("  - " + err)
        return 1

    print(f"materials: {len(materials)} (external {len(external)} + trace 1)")
    print(f"questions: {len(questions)} / motifs: 1 / fragments: {len(fragments)}")
    print(f"relations: {len(relations)} / read_log: {len(read_logs)} / sessions: 1")
    kinds: dict[str, int] = {}
    for m in materials:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    print("kinds:", kinds)
    statuses: dict[str, int] = {}
    for m in materials:
        status = m["verification"]["status"]
        statuses[status] = statuses.get(status, 0) + 1
    print("verification:", statuses)
    bundles: dict[str, int] = {}
    for raw in MATERIALS:
        bundles[raw["bundle"]] = bundles.get(raw["bundle"], 0) + 1
    for name, count in bundles.items():
        print(f"  bundle {count:>2}  {name}")

    if not args.write:
        print("dry run (pass --write to create shards)")
        return 0

    write("materials", materials, True)
    write("motifs", [motif], True)
    write("questions", questions, True)
    write("fragments", fragments, True)
    write("relations", relations, True)
    write("read_log", read_logs, True)
    write("sessions", session, True)
    print("wrote shards with suffix", SHARD_SUFFIX)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
