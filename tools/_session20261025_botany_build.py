#!/usr/bin/env python3
"""Build the SESSION-20261025-5b8d4e ledger shards (plants / trees / seeds / roots / flowers).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).  Run it once:

    python3 tools/_session20261025_botany_build.py            # dry run (validates)
    python3 tools/_session20261025_botany_build.py --write    # create shards and append

The materials' ``origin.evidence_record_path`` points at the shard this script
creates, and every ID is checked against the union before anything is written.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ledger_io  # noqa: E402
import new_ledger_shard  # noqa: E402
from _session20261025_botany_data1 import MATERIALS_1  # noqa: E402
from _session20261025_botany_data2 import MATERIALS_2  # noqa: E402
from _session20261025_botany_data3 import (  # noqa: E402
    FRAGMENTS,
    MATERIALS_3,
    MOTIF,
    QUESTIONS,
    SESSION_ID,
    TRACE_ID,
)

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "f30fead2a701ff717d5ad27a48044edddebd1b33"
REPORT = "readings/2026-10-25-plants-trees-seeds-and-the-rootless-archive.md"
DATA_MODULES = (
    "tools/_session20261025_botany_data1.py",
    "tools/_session20261025_botany_data2.py",
    "tools/_session20261025_botany_data3.py",
)
DAY = "2026-10-25"
SHARD_SUFFIX = "5b8d4e7a1c92"

# MATERIALS_3 ends with the project_trace entry; keep external and trace distinct
EXTERNAL_MATERIALS: list[dict] = MATERIALS_1 + MATERIALS_2 + [
    m for m in MATERIALS_3 if m["id"] != TRACE_ID
]
TRACE_RAW: dict = next(m for m in MATERIALS_3 if m["id"] == TRACE_ID)
ALL_RAW_MATERIALS: list[dict] = EXTERNAL_MATERIALS + [TRACE_RAW]


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


def material_record(raw: dict, shard_path: str) -> dict[str, Any]:
    status = {"verified": "verified", "partial": "partially_verified"}[raw["verification"][0]]
    if raw in MATERIALS_1:
        module = DATA_MODULES[0]
    elif raw in MATERIALS_2:
        module = DATA_MODULES[1]
    else:
        module = DATA_MODULES[2]

    rec: dict[str, Any] = {
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
            "source_record_path": "tools/botany_audit.py" if raw["id"] == TRACE_ID else module,
            "evidence_record_path": REPORT if raw["id"] == TRACE_ID else shard_path,
        },
        "verification": {
            "status": status,
            "checked_at": DAY,
            "method": raw["verification"][1],
        },
    }
    if raw["verification"][2]:
        rec["verification"]["note"] = raw["verification"][2]
    return rec


def question_records() -> list[dict[str, Any]]:
    prev_map = {
        "Q-20261025-5b8d01": ["Q-20261025-31f7cb"],
        "Q-20261025-5b8d02": ["Q-002"],
        "Q-20261025-5b8d03": ["Q-20261025-b4e703"],
        "Q-20261025-5b8d04": ["Q-20261025-e6402b"],
        "Q-20261025-5b8d05": ["Q-001"],
    }
    return [
        {
            "question_id": q["id"],
            "question": q["q"],
            "status": "open",
            "motif_ids": q["motifs"],
            "material_ids": q["materials"],
            "previous_question_ids": prev_map[q["id"]],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID}（植物・樹木・種子・根・花の精読）で開いた問い。",
            },
            "created_at": DAY,
            "notes": q["note"],
        }
        for q in QUESTIONS
    ]


def motif_record() -> dict[str, Any]:
    return {
        "motif_id": MOTIF["motif_id"],
        "label": MOTIF["name"],
        "description": MOTIF["description"],
        "question_ids": [q["id"] for q in QUESTIONS],
        "material_ids": [raw["id"] for raw in ALL_RAW_MATERIALS],
        "status": "active",
    }


def fragment_records() -> list[dict[str, Any]]:
    forms = {
        "FRAG-20261025-5b8d01": ("essay", "reflective_literary_voice"),
        "FRAG-20261025-5b8d02": ("fragment", "reflective_literary_voice"),
    }
    return [
        {
            "fragment_id": f["id"],
            "created_at": DAY,
            "language": "ja",
            "form": forms[f["id"]][0],
            "title": f["title"],
            "text": f["text"],
            "narrator_mode": forms[f["id"]][1],
            "question_ids": f["questions"],
            "motif_ids": f["motifs"],
            "material_ids": f["materials"],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/close_reading_report.md",
            "status": f["status"],
            "editor_note": f["rationale"],
        }
        for f in FRAGMENTS
    ]


def session_record() -> dict[str, Any]:
    return {
        "session_id": SESSION_ID,
        "started_at": DAY,
        "human_direction": (
            "このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
            "一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
            "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください。"
        ),
        "question_ids": [q["id"] for q in QUESTIONS],
        "context_material_ids": [raw["id"] for raw in ALL_RAW_MATERIALS],
        "produced_fragment_ids": [f["id"] for f in FRAGMENTS],
        "new_question_ids": [q["id"] for q in QUESTIONS],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "Arena.ai Agent Mode（単一セッション、branch arena/e16f2f30-aiselfmyself）",
        "notes": (
            "収蔵の前に第53の鏡 tools/botany_audit.py を作り、断片95編・地の文45,222字を測った。"
            "生字「葉」32回中30回が「言葉（合言葉を含む）」に、「草」9回中6回が「草稿・草子」に、"
            "「種」6回と「根」4回のすべてが非植物語（種類・火種・種明かし・屋根・根元・根拠）に吸収され、"
            "生きた種子と植物の根と野の花はともに0回、「枝」12回中8回が探索木比喩（「状態の木」「問いの枝」等）、"
            "「木」18回中13回が切り倒された木材・積み木だった。"
            "また TOKEN_RE と adjust_counts 併用時の長短語共起による二重減算バグを count_term 直接集計に統一して解消した。"
            "外部45件（literary_text 18／research_excerpt 27）＋運用痕跡1件＝46件を収蔵。"
        ),
    }


def relation_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    idx = 1

    def add(left: tuple[str, str], right: tuple[str, str], kind: str, note: str) -> None:
        nonlocal idx
        records.append(
            {
                "relation_id": f"REL-20261025-5b8d{idx:02d}",
                "left": {"type": left[0], "id": left[1]},
                "relation_type": kind,
                "right": {"type": right[0], "id": right[1]},
                "note": note,
                "created_at": DAY,
            }
        )
        idx += 1

    # 1..46: 46素材 -> モチーフ
    for raw in ALL_RAW_MATERIALS:
        add(("material", raw["id"]), ("motif", MOTIF["motif_id"]), "responds_to", raw["reading"])

    # 47..51: 5問い -> モチーフ
    for q in QUESTIONS:
        add(
            ("question", q["id"]),
            ("motif", MOTIF["motif_id"]),
            "leaves_open",
            "問いはモチーフの内側で閉じずに開いたままにする（PROJECT_CHARTER.md 1）。",
        )

    # 52..54: 2断片の入出エッジを確実に両方持たせる
    add(
        ("motif", MOTIF["motif_id"]),
        ("fragment", "FRAG-20261025-5b8d01"),
        "echo",
        "第55モチーフから試作断片1（葉を食い尽くした言葉、天井に吊るされた根）へ線を引く。",
    )
    add(
        ("fragment", "FRAG-20261025-5b8d01"),
        ("fragment", "FRAG-20261025-5b8d02"),
        "contrast",
        "断片1は「葉・草・種・根が書記語彙に食われた負債」を一人称で数え、断片2は「倒木更新と焼けた梁 HH-39 の年輪」から個体性と引用バイアスを問う。",
    )
    add(
        ("fragment", "FRAG-20261025-5b8d02"),
        ("motif", MOTIF["motif_id"]),
        "reframes",
        "「優しい菌根ネットワーク」のロマン化を退け、乾いた年の狭い年輪（裏切りと限り）を刻む手続きへモチーフを引き戻す。",
    )

    # 55..59: 断片 -> 問い
    for qid in ("Q-20261025-5b8d01", "Q-20261025-5b8d02", "Q-20261025-5b8d03"):
        add(
            ("fragment", "FRAG-20261025-5b8d01"),
            ("question", qid),
            "responds_to",
            f"試作断片1が {qid} の語彙の負債と種子の重さに一人称で応答する。",
        )
    for qid in ("Q-20261025-5b8d04", "Q-20261025-5b8d05"):
        add(
            ("fragment", "FRAG-20261025-5b8d02"),
            ("question", qid),
            "leaves_open",
            f"試作断片2が {qid} のクローン森・内共生・引用バイアスの問いを開いたまま手渡す。",
        )

    # 60..71: 素材間の対立・変奏・対話ペア（12組）
    pairs = [
        (
            "MAT-LIT-20261025-b101a1",
            "MAT-LIT-20261025-b102a2",
            "contrast",
            "テオプラストスは動物との器官類比を戒め、ラ・メトリはあえて葉＝肺・樹液＝血液と類比した上で動かない充足を説く。",
        ),
        (
            "MAT-LIT-20261025-b103a3",
            "MAT-LIT-20261025-c205b5",
            "contrast",
            "ゲーテは「すべては葉の変態である」と讃え、ポンジュは「木は毎年同じ葉を刷り直すだけで推敲できない」と反転させる。",
        ),
        (
            "MAT-20261025-b104a4",
            "MAT-20261025-e401d1",
            "interrupts",
            "ダーウィンの「幼根の先端は下等動物の脳のように働く」という比喩を、同時代のザックスが「文学的擬人化だ」と批判し水耕栽培を対置する。",
        ),
        (
            "MAT-20261025-b104a4",
            "MAT-20261025-f504e4",
            "reframes",
            "ダーウィンが土の底に見た「根の先端」を、クヌースの計算機科学は紙に上から下へ書く都合でページの天井へ逆さまに吊るした。",
        ),
        (
            "MAT-LIT-20261025-b109a9",
            "MAT-20261025-d301c1",
            "echo",
            "ギーニが始めた押し葉標本（hortus siccus）の技法が、3世紀後に16歳のディキンソンが詩より先に編んだ66頁・424点の標本帳へ繋がる。",
        ),
        (
            "MAT-LIT-20261025-c201b1",
            "MAT-LIT-20261025-e402d2",
            "echo",
            "柳宗元の郭橐駝（毎朝樹皮を引っ掻いて木を枯らすな）と福岡正信（人間が剪定するから枝が乱れる）が1200年を隔てて呼応する。",
        ),
        (
            "MAT-LIT-20261025-e402d2",
            "MAT-20261025-f505e5",
            "contrast",
            "福岡正信の「無剪定」と、ブライマンらの CART「最大まで茂らせてから枝を刈り落とさないと過学習する」が真っ向から衝突する。",
        ),
        (
            "MAT-LIT-20261025-c203b3",
            "MAT-20261025-f506e6",
            "transforms",
            "シェイクスピア『冬物語』の台木と穂木の接ぎ木が、コザの遺伝的プログラミングにおける構文木の部分木交叉とブロートへ変奏される。",
        ),
        (
            "MAT-20261025-d303c3",
            "MAT-20261025-d307c7",
            "transforms",
            "メンデルの静的な分離法則とミヤマコウゾリナの単為生殖の壁から、マクリントックの「染色体上を飛び移る遺伝子」へ。",
        ),
        (
            "MAT-20261025-d306c6",
            "MAT-20261025-d309c9",
            "transforms",
            "レニングラード包囲戦で餓死しながら守られた25万点の種子から、スヴァールバル世界種子貯蔵庫の永久凍土と2015年シリア内戦での引き出しへ。",
        ),
        (
            "MAT-20261025-e407d7",
            "MAT-20261025-e408d8",
            "interrupts",
            "1997年のシマード菌根炭素移動論文の共著者メラニー・ジョーンズ自身が、2023年に「母なる木」神話への肯定的引用バイアスと査読証拠0件を監査する。",
        ),
        (
            "MAT-LIT-20261025-b106a6",
            "MAT-20261025-e409d9",
            "interrupts",
            "マーダーの「植物思考（非中心的志向性）」の哲学的拡張に対し、タイズらが進化神経生物学から「植物は意識を持たないし必要としない」と歯止めをかける。",
        ),
    ]
    for left_id, right_id, rtype, note in pairs:
        add(("material", left_id), ("material", right_id), rtype, note)

    # 72..75: 既存断片との架橋（第53の鏡で再読した4編）
    add(
        ("fragment", "FRAG-20261025-5b8d01"),
        ("fragment", "FRAG-20261024-231bc3"),
        "echo",
        "95断片中で唯一生きた植物の「葉」が残っていた「街路樹の葉が一枚も動かない」と塩坑の「枯れ枝」を引き継ぐ。",
    )
    add(
        ("fragment", "FRAG-20261025-5b8d01"),
        ("fragment", "FRAG-20261024-6b9695"),
        "echo",
        "95断片中で唯一生きた植物の「草」が残っていた「草木は風が撓めれば鳴り」を引き継ぐ。",
    )
    add(
        ("material", "MAT-20261025-f507e7"),
        ("fragment", "FRAG-009"),
        "responds_to",
        "MCTS サーベイが、既存断片の「状態の木はすでにそこに立っており」の探索木モデルを裏づける。",
    )
    add(
        ("material", "MAT-20261025-f509e9"),
        ("fragment", "FRAG-024"),
        "echo",
        "ヤオらの Tree of Thoughts が、既存断片 FRAG-024 の「問いの枝」という外在化された分岐構造と照応する。",
    )

    return records


def read_log_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    idx = 1

    def add(target_type: str, target_id: str, reading: str, note: str) -> None:
        nonlocal idx
        records.append(
            {
                "read_id": f"READ-20261025-5b8d{idx:02d}",
                "session_id": SESSION_ID,
                "target": {"type": target_type, "id": target_id},
                "reading": reading,
                "note": note,
                "created_at": DAY,
            }
        )
        idx += 1

    quoted_ids = {
        "MAT-LIT-20261025-b103a3",
        "MAT-20261025-b104a4",
        "MAT-LIT-20261025-c201b1",
        "MAT-LIT-20261025-c202b2",
        "MAT-LIT-20261025-c203b3",
        "MAT-LIT-20261025-c204b4",
        "MAT-LIT-20261025-c206b6",
    }
    contested_ids = {
        "MAT-LIT-20261025-b102a2",
        "MAT-LIT-20261025-b106a6",
        "MAT-20261025-e401d1",
        "MAT-20261025-e407d7",
        "MAT-20261025-e408d8",
        "MAT-20261025-e409d9",
    }
    counted_ids = {
        "MAT-20261025-d303c3",
        "MAT-20261025-d304c4",
        "MAT-20261025-d306c6",
        "MAT-20261025-d308c8",
        "MAT-20261025-d309c9",
        "MAT-20261025-f508e8",
        "MAT-20261025-f509e9",
        TRACE_ID,
    }

    for raw in ALL_RAW_MATERIALS:
        mid = raw["id"]
        if mid in quoted_ids:
            rmode = "quoted"
        elif mid in contested_ids:
            rmode = "contested"
        elif mid in counted_ids:
            rmode = "counted"
        else:
            rmode = "interpreted"
        add("material", mid, rmode, f"精読報告（{raw['bundle']}）：{raw['reading']}")

    # 既存4断片の再読
    rereads = [
        (
            "FRAG-20261024-231bc3",
            "counted",
            "第53の鏡で再読：95断片中で唯一生きた植物の「葉」が残る「街路樹の葉が一枚も動かない」と、スタンダール塩坑の「枯れ枝・小枝」4回を確認。",
        ),
        (
            "FRAG-20261024-6b9695",
            "counted",
            "第53の鏡で再読：95断片中で唯一生きた植物の「草」が残る「草木は風が撓めれば鳴り」を確認。",
        ),
        (
            "FRAG-009",
            "interpreted",
            "第53の鏡で再読：「状態の木はすでにそこに立っており」の探索木比喩を MCTS サーベイと照合。",
        ),
        (
            "FRAG-024",
            "interpreted",
            "第53の鏡で再読：既存の「問いの枝」をヤオらの Tree of Thoughts および探索木の分岐と接続。",
        ),
    ]
    for fid, rmode, note in rereads:
        add("fragment", fid, rmode, note)

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


def write_shard(collection: str, records: list[dict[str, Any]], create: bool) -> Path:
    path = shard_for(collection, create)
    if create:
        # overwrite cleanly in case of re-run
        with open(path, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create shards and write records")
    args = parser.parse_args(argv)

    # Remove own shards first so re-runs are idempotent
    for col in ("materials", "motifs", "questions", "fragments", "relations", "read_log", "sessions"):
        own_shard = shard_for(col, False)
        if own_shard.exists():
            own_shard.unlink()

    existing = _existing_ids()
    materials_shard = str(shard_for("materials", False).relative_to(ROOT))
    materials = [material_record(raw, materials_shard) for raw in ALL_RAW_MATERIALS]
    questions = question_records()
    motif = motif_record()
    fragments = fragment_records()
    session = [session_record()]
    relations = relation_records()
    read_logs = read_log_records()

    errors = check_references(
        materials, questions, motif, fragments, relations, read_logs, existing
    )
    if errors:
        print("FAIL: reference errors")
        for err in errors:
            print("  - " + err)
        return 1

    print(f"materials: {len(materials)} (external {len(EXTERNAL_MATERIALS)} + trace 1)")
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
    for raw in ALL_RAW_MATERIALS:
        bundles[raw["bundle"]] = bundles.get(raw["bundle"], 0) + 1
    for name, count in bundles.items():
        print(f"  bundle {count:>2}  {name}")

    if not args.write:
        print("dry run (pass --write to create shards)")
        return 0

    write_shard("materials", materials, True)
    write_shard("motifs", [motif], True)
    write_shard("questions", questions, True)
    write_shard("fragments", fragments, True)
    write_shard("relations", relations, True)
    write_shard("read_log", read_logs, True)
    write_shard("sessions", session, True)
    print("wrote shards with suffix", SHARD_SUFFIX)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
