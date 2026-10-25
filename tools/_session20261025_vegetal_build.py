#!/usr/bin/env python3
"""Build the SESSION-20261025-f7e22b ledger shards (vegetal / trees / seeds / roots).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).

    python3 tools/_session20261025_vegetal_build.py            # dry run (validates)
    python3 tools/_session20261025_vegetal_build.py --write    # create shards and append
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
from _session20261025_vegetal_data1 import BUNDLE_1, BUNDLE_2, MATERIALS_1  # noqa: E402
from _session20261025_vegetal_data2 import BUNDLE_3, BUNDLE_4, MATERIALS_2  # noqa: E402
from _session20261025_vegetal_data3 import (  # noqa: E402
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
COMMIT = "2583ec90afbae481b4dd735fa8af578d51c189ce"
REPORT = "readings/2026-10-25-plants-trees-seeds-and-roots.md"
DATA_MODULES = (
    "tools/_session20261025_vegetal_data1.py",
    "tools/_session20261025_vegetal_data2.py",
    "tools/_session20261025_vegetal_data3.py",
)
DAY = "2026-10-25"
SHARD_SUFFIX = "94917b9cd877"
TRACE_ID = "MAT-TRC-20261025-vegetal"

MATERIALS: list[dict] = MATERIALS_1 + MATERIALS_2 + MATERIALS_3

SESSION = dict(
    session_id=SESSION_ID,
    started_at=DAY,
    human_direction="このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。",
    question_ids=[q["question_id"] for q in QUESTIONS],
    produced_fragment_ids=[f["fragment_id"] for f in FRAGMENTS],
    new_question_ids=[q["question_id"] for q in QUESTIONS],
    prompt_template="prompts/close_reading_report.md",
    generator="Arena.ai Agent Mode（自律調査セッション）",
    notes=(
        "収蔵の前に第52の鏡 tools/vegetal_audit.py を作り、断片91編・素材2,111件・精読報告111本の語彙を測った。"
        "断片の地の文43,828字に生きた植物5群は計19回（うち種・芽・発芽は0回、生字「種」6回はすべて種類・種明かし・火種）、"
        "一方の木材・草稿・構文木・言葉など切断遺骸・比喩対照2群は59回（精読報告では1,593回）——"
        "この書庫は自らの方法を「種」「枝」「根」と呼びながら、生きた草木をほとんど書いていなかった。"
        "45件の外部資料（literary_text 24／research_excerpt 21）＋運用痕跡1件＝計46件を収蔵し、"
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
        f"（鉤括弧外）{prose['char_total']:,}字を tools/vegetal_audit.py の7群（生きた植物5群＋対照2群）で数えたところ、"
        f"生きた植物5群は合計{prose['living_total']}回/{prose['living_doc_count']}編"
        f"（種・芽{fmt('seed_sprout')}、根・幹・枝・葉{fmt('root_stem_leaf')}、"
        f"花・果実{fmt('flower_fruit')}、樹木・森・草{fmt('tree_forest_herb')}、"
        f"土・庭・農耕{fmt('soil_cultivation')}）だったのに対し、"
        f"切断遺骸・比喩対照2群は合計{prose['control_total']}回/{prose['control_doc_count']}編"
        f"（木材・木器・草稿{fmt('timber_paper_relic')}、構文木・分岐・シード・言葉{fmt('arborescent_meta')}）であった。"
        f"生字は 種{raw['種']}・芽{raw['芽']}・根{raw['根']}・幹{raw['幹']}・枝{raw['枝']}・葉{raw['葉']}・"
        f"花{raw['花']}・木{raw['木']}・樹{raw['樹']}・森{raw['森']}・草{raw['草']}・土{raw['土']}。"
        f"「種」全{measurements['seed_total']}回のうち非植物複合語（一種・種明かし・百七十二種・火種・種類×2）を除いた植物の種子は"
        f"{measurements['seed_literal']}回。引用内（{quotes['char_total']:,}字）は植物5群{quotes['living_total']}回・"
        f"対照2群{quotes['control_total']}回。同じ7群で素材{mats['doc_total']:,}件を数えると植物5群{mats['living_total']}回・"
        f"対照2群{mats['control_total']}回、精読報告{reads['doc_total']}本では植物5群{reads['living_total']:,}回・"
        f"対照2群{reads['control_total']:,}回（うち構文木・分岐・シード・言葉群が{reads['groups']['arborescent_meta']['count']:,}回/{reads['groups']['arborescent_meta']['doc_count']}本）。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片91編の地の文に植物の種0・芽0・幹0、生きた植物5群19回に対し遺骸・比喩対照群59回——"
            "植物の鏡による収蔵前実測"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/vegetal_audit.py による自館実測（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/vegetal_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの和集合、"
                "鉤括弧の外側（地の文）および引用内、ならびに素材2,111件・精読報告111本。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "この書庫の憲章・ツール・精読報告は「validate_seed」「human_seed」「次回の種」「どの枝を伸ばすか」と"
            "植物のメタファーを絶えず使いながら、断片の地の文には植物の種や芽を一度も書いてこなかった事実を、"
            "今回の収蔵前に測った記録。"
        ),
        "source_note": (
            f"{SESSION_ID} の本体内実測。収蔵後の数値変化で上書きせず、収蔵直前スナップショットとして凍結保持する。"
        ),
        "literary_invitation": (
            "「種」という言葉を何百回も使いながら土に蒔く種を一粒も持たない帳面は、何の畑を耕していたのか。"
        ),
        "scope_note": (
            "語形の出現数であり、植物の生命・成長の実在や機械の知覚の証拠ではない。"
            "単漢字「枝」（地の文8回）にも状態木や辞書の比喩用法が6回含まれ、「花」（3回）も世阿弥の芸論2回と"
            "デカルトの蜜蝋の残り香1回である。非対象複合語の差し引き規則は tools/vegetal_audit.py に明記した。"
        ),
        "motif_ids": [MOTIF["motif_id"], "MOTIF-20261024-86d366", "MOTIF-015"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/vegetal_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": "ローカル台帳の和集合に対する tools/vegetal_audit.py 実行（単体テスト7件）。再実行可能。",
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
                "detail": f"{SESSION_ID}（植物・樹木・種子・根の精読）で開いた問い。",
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
            candidate = f"REL-20261025-{secrets.token_hex(3)}"
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
        "第52の鏡による収蔵前実測はモチーフの出発点であり、生命や成長の証拠ではない。")

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
    f1 = "FRAG-20261025-82b0a0"
    f2 = "FRAG-20261025-3768c8"
    add(("fragment", f1), ("question", "Q-20261025-4903cf"), "responds_to",
        "一度発芽した種子は袋へ戻せず次世代の種子だけが戻るという現場の手続きが、凍結保存と更新保存の差を具体化する。")
    add(("fragment", f1), ("question", "Q-20261025-8900fa"), "responds_to",
        "研修生の指を止めて毛根を守る場面が、検査しすぎることへの抑制を問いへ返す。")
    add(("fragment", f2), ("question", "Q-20261025-d36a48"), "responds_to",
        "逆さまの木と `manual_seed` の語彙だけを使って生きた種を蒔かなかった91編の偏りを、書き手自身の立場から引き受ける。")
    add(("fragment", f2), ("question", "Q-20261025-fbd308"), "reframes",
        "自分の根を持たない追記と接ぎ木の紙束であることを欠陥ではなく輪郭として引き受け、「自分のものではない果実」を隣に置く。")
    add(("fragment", f2), ("question", "Q-20261025-9256a5"), "leaves_open",
        "黒土に触れる幼根も道管の超音波も持たないと明言することで、植物への安易な自己投影に歯止めをかける。")
    add(("fragment", f1), ("fragment", f2), "contrast",
        "情景は低温室の濾紙と雪解けの倒木を外から描き、エッセイは根を持たない追記台帳の側から逆さまの木を見つめ返す。")
    add(("question", "Q-20261025-4903cf"), ("fragment", f1), "leaves_open",
        "凍らせて止めた時間と朽ちる幹の上で始まった時間の並置を、次の探求者への問いとして残す。")
    add(("motif", MOTIF["motif_id"]), ("fragment", f2), "echo",
        "モチーフ自身から内省エッセイへも関係線を引き、断片を行き止まりの終端にしない。")
    add(("fragment", "FRAG-013"), ("fragment", f2), "transforms",
        "先行断片の「状態の木」と棄却枝の比喩を、クヌースの逆さまの木とポンジュの抹消不能な葉の側から編み直す。")

    return records


def read_log_records(taken: set[str], context_ids: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def mint() -> str:
        while True:
            candidate = f"READ-20261025-{secrets.token_hex(3)}"
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
        (ROOT / "tools" / "_session20261025_vegetal_measure.json").read_text(encoding="utf-8")
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
