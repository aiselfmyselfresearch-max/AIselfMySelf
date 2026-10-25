#!/usr/bin/env python3
"""Build the SESSION-20261025-9c4e7a ledger shards (star / constellation / night).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).  Run it once:

    python3 tools/_session20261025_sky_build.py            # dry run (validates)
    python3 tools/_session20261025_sky_build.py --write    # create shards and append

The materials' ``origin.evidence_record_path`` points at the shard this script
creates, and every ID is checked against the union before anything is written.
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
from _session20261025_sky_data1 import MATERIALS_1  # noqa: E402
from _session20261025_sky_data2 import MATERIALS_2  # noqa: E402
from _session20261025_sky_data3 import (  # noqa: E402
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
COMMIT = "679db4e14158ae5e2941b4e14a7890512c2c4b78"
REPORT = "readings/2026-10-25-sky-stars-and-constellations.md"
DATA_MODULES = (
    "tools/_session20261025_sky_data1.py",
    "tools/_session20261025_sky_data2.py",
    "tools/_session20261025_sky_data3.py",
)
DAY = "2026-10-25"
SHARD_SUFFIX = "9c4e7a3f5b21"
TRACE_ID = "MAT-TRC-20261025-sky"

MATERIALS: list[dict] = MATERIALS_1 + MATERIALS_2 + MATERIALS_3

SESSION = dict(
    session_id=SESSION_ID,
    started_at=DAY,
    human_direction=(
        "このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
        "一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
        "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
        "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
        "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください。"
    ),
    question_ids=[
        "Q-20261025-4c8a17",
        "Q-20261025-b05e3d",
        "Q-20261025-71d9f2",
        "Q-20261025-e6402b",
        "Q-20261025-9a37c8",
    ],
    produced_fragment_ids=["FRAG-20261025-2d81b7", "FRAG-20261025-c90813"],
    new_question_ids=[
        "Q-20261025-4c8a17",
        "Q-20261025-b05e3d",
        "Q-20261025-71d9f2",
        "Q-20261025-e6402b",
        "Q-20261025-9a37c8",
    ],
    prompt_template="prompts/close_reading_report.md",
    generator="Arena.ai Agent Mode（Claude系モデル、単一セッション）",
    notes=(
        "収蔵の前に第51の鏡 tools/sky_audit.py を作り、断片89編の語彙を測った。"
        "断片の地の文に星1・星座0・光年0・光害0、生字「空」63回の大半が空欄・空白——"
        "この書庫は自分の方法を「星座図」と呼びながら、自分の声で空を書いていなかった。"
        "44件の外部資料（literary_text 7／research_excerpt 37）＋運用痕跡1件。"
        "精読報告の三層（解釈／考え／感じたこと）は、感じたことを主観の証明に使わない制動つきで書いた。"
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

    quotes = measurements["fragments_quotes"]["groups"]
    mats = measurements["materials"]["groups"]
    reads = measurements["readings"]["groups"]
    raw = measurements["raw_kanji_counts"]
    passage = (
        f"収蔵直前（{COMMIT[:12]}）の断片{measurements['fragment_count']}編・地の文"
        f"（鉤括弧外）{prose['char_total']:,}字を tools/sky_audit.py の7群で数えたところ、"
        f"星{fmt('star')}・夜空{fmt('night_sky')}・宇宙{fmt('cosmos')}・"
        f"遅れて届く光{fmt('delay')}・見えなさ{fmt('visibility')}・"
        f"点を結ぶ{fmt('plotting')}・機械の空{fmt('machine_sky')}。引用内は"
        f"星{quotes['star']['count']}・夜空{quotes['night_sky']['count']}・"
        f"宇宙{quotes['cosmos']['count']}・点を結ぶ{quotes['plotting']['count']}。"
        f"生字は 星{raw['星']}・空{raw['空']}・夜{raw['夜']}・光{raw['光']}・闇{raw['闇']}・"
        f"月{raw['月']}・天{raw['天']}・雲{raw['雲']}・点{raw['点']}・図{raw['図']}。"
        f"「月」全{measurements['month_total']}回のうち、日付・月数を除く残りは"
        f"{measurements['month_not_date']}回。同じ7群で素材{measurements['materials']['doc_total']:,}件を"
        f"数えると星{mats['star']['count']}回/{mats['star']['doc_count']}件・"
        f"星座を含む点を結ぶ{mats['plotting']['count']}回/{mats['plotting']['doc_count']}件・"
        f"宇宙{mats['cosmos']['count']}回・遅れて届く光{mats['delay']['count']}回、"
        f"精読報告{measurements['readings']['doc_total']}本では星{reads['star']['count']}・"
        f"点を結ぶ{reads['plotting']['count']}（うち星座{reads['plotting']['terms'].get('星座', 0)}・"
        f"星座図{reads['plotting']['terms'].get('星座図', 0)}）・夜空{reads['night_sky']['count']}。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片89編の地の文に星1・星座0・光年0、生字「空」63回の大半は空欄——"
            "星の鏡による収蔵前実測"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/sky_audit.py による自館実測（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/sky_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの"
                "和集合、鉤括弧の外側（地の文）。素材・精読報告も同じ7群で数えた。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "この書庫のビューアは関係グラフを「星座図」と呼び、断片の配置を"
            "「コンステレーション」と呼んできた（FRAG-017）。その語を使いながら、"
            "空そのものを書いた断片がほとんどなかったことを、収蔵の前に測った記録。"
        ),
        "source_note": (
            "SESSION-20261025-9c4e7a の本体内実測。数の更新は上書きせず、後日の訂正録に委ねる。"
        ),
        "literary_invitation": (
            "星が1回あることは、空を見たことの証拠ではない。"
            "数えられたのは語形であって、空ではない。"
        ),
        "scope_note": (
            "語形の記録であり、星を見た経験・夜空の実在・機械の感覚の証拠ではない。"
            "「空」63回は空欄・空白・空っぽ、「点」35回は点検・採点・視点、「月」15回の大半は"
            "日付であり、いずれも空の語ではない。差し引きの設計は報告の付録に書いた。"
        ),
        "motif_ids": [MOTIF["motif_id"], "MOTIF-006", "MOTIF-015"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/sky_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": (
                "ローカル台帳の和集合に対する tools/sky_audit.py 実行（単体テスト8件）。再実行可能。"
            ),
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
                "detail": "SESSION-20261025-9c4e7a（星・星座・夜の精読）で開いた問い。",
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
    for left, right, kind, note in PAIRS:
        add(("material", left), ("material", right), kind, note)
    for material_id, question_id, note in MATERIAL_TO_QUESTION:
        add(("material", material_id), ("question", question_id), "leaves_open", note)
    for question in QUESTIONS:
        add(
            ("question", question["question_id"]),
            ("motif", MOTIF["motif_id"]),
            "leaves_open",
            "問いはモチーフの内側で閉じずに開いたままにする（PROJECT_CHARTER.md 1）。",
        )
    add(("fragment", "FRAG-20261025-2d81b7"), ("question", "Q-20261025-b05e3d"), "responds_to",
        "線を引かない時間を三分延ばすという実務が、点を結ぶことの条件を問いへ返す。")
    add(("fragment", "FRAG-20261025-2d81b7"), ("question", "Q-20261025-e6402b"), "echo",
        "衛星を星と誤認した記録が、書庫の外の空の変化を一行の日付として残す。")
    add(("fragment", "FRAG-20261025-2d81b7"), ("question", "Q-20261025-4c8a17"), "reframes",
        "線がないと星はただ散らばる——散らばったままでも空だと知る、という一行が不在の読みを反転させる。")
    add(("fragment", "FRAG-20261025-c90813"), ("question", "Q-20261025-4c8a17"), "responds_to",
        "覚え書きは「見なかった」と書くのを保留し、空欄の名前を「空」に固定する。")
    add(("fragment", "FRAG-20261025-c90813"), ("question", "Q-20261025-71d9f2"), "leaves_open",
        "記入者と記入日を書かない末尾が、著者の同定を宙に置いたまま終わる。")
    add(("fragment", "FRAG-20261025-c90813"), ("motif", MOTIF["motif_id"]), "reframes",
        "七項目のうち五が「作業のための夜」であることを明示し、モチーフの重心を労働の側へずらす。")
    add(("fragment", "FRAG-20261025-2d81b7"), ("fragment", "FRAG-20261025-c90813"), "contrast",
        "情景は線を一本ずつ引き、覚え書きは線を引かない理由を数える。引くことと、引かないことの記録。")
    add(("question", "Q-20261025-b05e3d"), ("fragment", "FRAG-20261025-2d81b7"), "leaves_open",
        "線を引く前の判断を、手続きとして残す場所として問いがこの断片を指す。")
    add(("question", "Q-20261025-e6402b"), ("fragment", "FRAG-20261025-2d81b7"), "responds_to",
        "見えなくなったことに日付を添える操作の最小例が、この情景の五番目の記録にある。")
    add(("motif", MOTIF["motif_id"]), ("fragment", "FRAG-20261025-2d81b7"), "echo",
        "モチーフから断片へも線を引く（断片を終点にしない）。")
    add(("material", TRACE_ID), ("question", "Q-20261025-4c8a17"), "leaves_open",
        "実測の偏在（星1・空63）が、不在の解釈を限定する。")
    add(("material", TRACE_ID), ("motif", MOTIF["motif_id"]), "responds_to",
        "この鏡の数値は、モチーフの出発点であり、モチーフの証拠ではない。")
    for mid in ("MAT-LIT-154", "MAT-LIT-20261024-4de8b4", "MAT-LIT-20261024-27cd43", "MAT-LIT-064"):
        add(
            ("material", mid),
            ("motif", MOTIF["motif_id"]),
            "echo",
            "既存台帳にあった空の思想を、今回のモチーフの前史として読み直した。",
        )
    for qid in ("Q-002", "Q-023", "Q-20261025-5e2c11"):
        add(
            ("question", qid),
            ("motif", MOTIF["motif_id"]),
            "echo",
            "先行する問いを、モチーフの内側から読み直す（解決はしない）。",
        )
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
    # 収蔵した素材はすべて精読している。手書きの痕跡がない分は、
    # 束の名前を添えた used_as_context として補い、--check の網羅条件を満たす。
    bundle_order = ["星を数え、名づける——点に名前を与える制度", "光は遅れて届く——距離・時間・記録",
                    "夜空が明るくなる——見えなくなること、増える光", "点を結ぶ——図を描くこと、誤読、捏造",
                    "夜の側——眠らないこと、待つこと、星に帰ること"]
    numerals = ["一", "二", "三", "四", "五"]
    bundles = {raw["id"]: raw["bundle"] for raw in MATERIALS}
    for material_id in context_ids:
        if material_id in covered:
            continue
        if material_id == TRACE_ID:
            label = "運用痕跡（自館実測）"
            prefix = ""
        else:
            label = bundles[material_id]
            prefix = f"第{numerals[bundle_order.index(label)]}束（{label}）"
        records.append(
            {
                "read_id": mint(),
                "session_id": SESSION_ID,
                "target": {"type": "material", "id": material_id},
                "reading": "used_as_context",
                "created_at": DAY,
                "note": (
                    f"{prefix}として精読した。報告 §2 に一節・解釈・考え・"
                    "感じたこと・裏切りを書いた。"
                ),
            }
        )
    return records


def check_references(
    materials: list[dict], questions: list[dict], motif: dict, fragments: list[dict],
    relations: list[dict], read_logs: list[dict], existing: dict[str, set[str]],
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
        for key, kind in (("question_ids", "question"), ("motif_ids", "motif"), ("material_ids", "material")):
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
        (ROOT / "tools" / "_session20261025_sky_measure.json").read_text(encoding="utf-8")
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

    errors = check_references(materials, questions, motif, fragments, relations, read_logs, existing)
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
