#!/usr/bin/env python3
"""Build the SESSION-20261026-6f7122 ledger shards (fungi / fermentation / decay).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).

    python3 tools/_session20261026_fungi_build.py            # dry run (validates)
    python3 tools/_session20261026_fungi_build.py --write    # create shards and append
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
from _session20261026_fungi_data1 import BUNDLE_1, BUNDLE_2, MATERIALS_1  # noqa: E402
from _session20261026_fungi_data2 import BUNDLE_3, BUNDLE_4, MATERIALS_2  # noqa: E402
from _session20261026_fungi_data3 import (  # noqa: E402
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
COMMIT = "d857f74fb68d5f4a2d77517f3cc81085cf4c31d9"
REPORT = "readings/2026-10-26-fungi-fermentation-and-decay.md"
DATA_MODULES = (
    "tools/_session20261026_fungi_data1.py",
    "tools/_session20261026_fungi_data2.py",
    "tools/_session20261026_fungi_data3.py",
)
DAY = "2026-10-26"
SHARD_SUFFIX = "3f8a1c9d2e47"
TRACE_ID = "MAT-TRC-20261026-fungi"

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
        "収蔵の前に第54の鏡 tools/fungi_audit.py を作り、断片97編・素材2,248件・精読報告114本の語彙を測った。"
        "断片の地の文46,771字に菌類・発酵・腐敗5群は計12回（うち発酵・醸造0回、菌根・共生0回、菌類の体5回）、"
        "衛生・培養対照2群は計1回（さび）だった——"
        "この書庫は変化を「生成」と呼びながら、微生物に任せて熟す変化（発酵）を一度も書いてこなかった。"
        "45件の外部資料（literary_text 22／research_excerpt 23）＋運用痕跡1件＝計46件を収蔵し、"
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
        f"（鉤括弧外）{prose['char_total']:,}字を tools/fungi_audit.py の7群（菌類・発酵・腐敗5群＋衛生・培養対照2群）で数えたところ、"
        f"菌類・発酵・腐敗5群は合計{prose['living_total']}回/{prose['living_doc_count']}編"
        f"（菌類の体{fmt('fungi_body')}、胞子と繁殖{fmt('spore_cycle')}、"
        f"発酵と醸造{fmt('fermentation_craft')}、腐敗・分解{fmt('decay_return')}、"
        f"共生と菌根{fmt('symbiosis_web')}）だったのに対し、"
        f"衛生・培養対照2群は合計{prose['control_total']}回/{prose['control_doc_count']}編"
        f"（細菌・衛生・薬{fmt('microbe_medicine')}、培養と比喩・機械{fmt('culture_metaphor')}）であった。"
        f"生字は 菌{raw['菌']}・酵{raw['酵']}・腐{raw['腐']}・朽{raw['朽']}・麹{raw['麹']}・醸{raw['醸']}・"
        f"胞{raw['胞']}・糸{raw['糸']}・毒{raw['毒']}・黴{raw['黴']}。"
        f"「菌」全{measurements['kin_total']}回のうち細菌・殺菌・滅菌などの複合語を除いた残りは"
        f"{measurements['kin_literal']}回。引用内（{quotes['char_total']:,}字）は菌類5群{quotes['living_total']}回・"
        f"対照2群{quotes['control_total']}回。同じ7群で素材{mats['doc_total']:,}件を数えると菌類5群{mats['living_total']}回・"
        f"対照2群{mats['control_total']}回、精読報告{reads['doc_total']}本では菌類5群{reads['living_total']:,}回・"
        f"対照2群{reads['control_total']:,}回であった。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片97編の地の文に発酵0回・菌根0回、菌類・発酵・腐敗5群12回に対し衛生・培養対照群1回——"
            "菌類の鏡による収蔵前実測"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/fungi_audit.py による自館実測（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/fungi_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの和集合、"
                "鉤括弧の外側（地の文）および引用内、ならびに素材2,248件・精読報告114本。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "この書庫は変化を「生成」と呼び、熟すこと・育つことを書きながら、断片の地の文には"
            "微生物に任せて時間をかけて変わる営み（発酵）を一度も書いてこなかった事実を、"
            "今回の収蔵前に測った記録。"
        ),
        "source_note": (
            f"{SESSION_ID} の本体内実測。収蔵後の数値変化で上書きせず、収蔵直前スナップショットとして凍結保持する。"
        ),
        "literary_invitation": (
            "「生成する」と言いながら発酵を一度も書かなかった帳面は、変化のどの型を持ち、どの型を持たないのか。"
        ),
        "scope_note": (
            "語形の出現数であり、菌類の生命や機械の知覚の証拠ではない。"
            "「分解」（地の文1回）は有機物の分解とは限らず、「増殖」（1回）も比喩の可能性がある。"
            "差し引きと群の設計は tools/fungi_audit.py に明記した。"
        ),
        "motif_ids": [MOTIF["motif_id"], "MOTIF-20261024-86d366", "MOTIF-015"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/fungi_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": "ローカル台帳の和集合に対する tools/fungi_audit.py 実行（単体テスト7件）。再実行可能。",
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
            candidate = f"REL-20261026-{secrets.token_hex(3)}"
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
        "第54の鏡による収蔵前実測はモチーフの出発点であり、生命や成長の証拠ではない。")

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
    f1 = "FRAG-20261026-b73a9a"
    f2 = "FRAG-20261026-7b2ac0"
    add(("fragment", f1), ("question", "Q-20261026-79cd5b"), "responds_to",
        "咲かせる菌と眠らせる菌という同じ菌への二つの作法が、発酵と腐敗・保存の境界は評価と場所で引かれるという問いを具体化する。")
    add(("fragment", f1), ("question", "Q-20261026-1bacfc"), "responds_to",
        "殺さず眠らせる書物の黴の管理が、追記型台帳の「消さずに開いたままにする」作法と保存の形として響き合う。")
    add(("fragment", f2), ("question", "Q-20261026-85b4a2"), "responds_to",
        "糸も腸も持たない書き手が発酵0回の不在を引き受け、比喩を使うときは捨てる部分を一行添えるという決めを残す。")
    add(("fragment", f2), ("question", "Q-20261026-29dd83"), "leaves_open",
        "粘菌の管の仕組みの側に言葉を置き、「考える」という語を人と菌の両方へ安易に渡さない制動を残す。")
    add(("fragment", f2), ("question", "Q-20261026-1bacfc"), "reframes",
        "堆肥の切り返しと台帳の蓄積を並べ、「減らないまま積み続けること」を保存の未熟さとして問い直す。")
    add(("fragment", f1), ("fragment", f2), "contrast",
        "情景は蔵と図書室の作業を外から描き、エッセイは糸を持たない記述の側から発酵の比喩の借り方を点検する。")
    add(("question", "Q-20261026-85b4a2"), ("fragment", f1), "leaves_open",
        "咲かせた菌も眠らせた菌も消さずに別の列へ並べる帳面の作法を、次の探求者への問いとして残す。")
    add(("motif", MOTIF["motif_id"]), ("fragment", f2), "echo",
        "モチーフ自身から内省エッセイへも関係線を引き、断片を行き止まりの終端にしない。")
    add(("fragment", "FRAG-20261025-3768c8"), ("fragment", f2), "transforms",
        "植物セッションの「根を持たない記述のための覚え書き」を、菌糸も持たない記述の覚え書きとして編み直す。")

    return records


def read_log_records(taken: set[str], context_ids: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def mint() -> str:
        while True:
            candidate = f"READ-20261026-{secrets.token_hex(3)}"
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
        (ROOT / "tools" / "_session20261026_fungi_measure.json").read_text(encoding="utf-8")
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
