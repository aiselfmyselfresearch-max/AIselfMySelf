#!/usr/bin/env python3
"""Build the SESSION-20261025-3f7a2c ledger shards (boredom / ennui / idleness).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).  Run it once:

    python3 tools/_session20261025_boredom_build.py            # dry run (validates)
    python3 tools/_session20261025_boredom_build.py --write    # create shards and append

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
from _session20261025_boredom_data1 import MATERIALS_1  # noqa: E402
from _session20261025_boredom_data2 import MATERIALS_2  # noqa: E402
from _session20261025_boredom_data3 import (  # noqa: E402
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
COMMIT = "4553403767e85add9dc3e8a30110c5d17521b89f"
REPORT = "readings/2026-10-25-boredom-ennui-and-the-unfilled-hour.md"
DATA_MODULES = (
    "tools/_session20261025_boredom_data1.py",
    "tools/_session20261025_boredom_data2.py",
    "tools/_session20261025_boredom_data3.py",
)
DAY = "2026-10-25"
SHARD_SUFFIX = "3f7a2c9d4e51"
TRACE_ID = "MAT-TRC-20261025-boredom"

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
    question_ids=[q["question_id"] for q in QUESTIONS],
    produced_fragment_ids=[f["fragment_id"] for f in FRAGMENTS],
    new_question_ids=[q["question_id"] for q in QUESTIONS],
    prompt_template="prompts/close_reading_report.md",
    generator="Arena.ai Agent Mode（単一セッション、branch arena/6c574702-aiselfmyself）",
    notes=(
        "収蔵の前に第52の鏡 tools/boredom_audit.py を作り、断片93編・地の文44,444字を測った。"
        "退屈・倦怠は2回／1編で、しかも2回とも「退屈を知らない者が」という打ち消しの一行のなか。"
        "暇0・焦り0・倦怠0・飽0。素材2,157件では退屈17・暇15、精読報告112本では退屈73・暇50。"
        "前セッション（sky）が「三つ目の空白候補」として書き残した退屈を、五回目の候補ではなく"
        "実測の穴として引き受けた。孤独は測るが束ねない。"
        "外部44件（literary_text 18／research_excerpt 26）＋運用痕跡1件。"
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
        verb = "束ねない" if not info["motif_bound"] else ""
        suffix = f"（{verb}）" if verb else ""
        return f"{info['count']}回/{info['doc_count']}編{suffix}"

    quotes = measurements["fragments_quotes"]["groups"]
    mats = measurements["materials"]["groups"]
    reads = measurements["readings"]["groups"]
    raw = measurements["raw_kanji_counts"]
    passage = (
        f"収蔵直前（{COMMIT[:12]}）の断片{measurements['fragment_count']}編・地の文"
        f"（鉤括弧外）{prose['char_total']:,}字を tools/boredom_audit.py の7群で数えたところ、"
        f"退屈・倦怠{fmt('tedium')}・暇{fmt('idle')}・何も起こらない{fmt('eventless')}・"
        f"焦り{fmt('haste')}・孤独{fmt('solitude')}・気晴らし{fmt('stimulation')}・"
        f"機械の待機{fmt('machine_wait')}。退屈語の内訳は『退屈』2回のみで、"
        f"いずれも打ち消し付き（「退屈を知らない者が」「退屈な尺度だけが欠けている」＝同一断片 FRAG-040）。"
        f"引用内は退屈{quotes['tedium']['count']}。生字は 退{raw['退']}・倦{raw['倦']}・暇{raw['暇']}・"
        f"飽{raw['飽']}・怠{raw['怠']}・孤{raw['孤']}・独{raw['独']}・無{raw['無']}。"
        f"同じ7群で素材{measurements['materials']['doc_total']:,}件を数えると"
        f"退屈・倦怠{mats['tedium']['count']}回/{mats['tedium']['doc_count']}件・"
        f"暇{mats['idle']['count']}回・何も起こらない{mats['eventless']['count']}回・"
        f"焦り{mats['haste']['count']}回・孤独{mats['solitude']['count']}回・"
        f"気晴らし{mats['stimulation']['count']}回・機械の待機{mats['machine_wait']['count']}回、"
        f"精読報告{measurements['readings']['doc_total']}本では退屈{reads['tedium']['count']}・"
        f"暇{reads['idle']['count']}・何も起こらない{reads['eventless']['count']}・"
        f"孤独{reads['solitude']['count']}・気晴らし{reads['stimulation']['count']}。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片93編の地の文に退屈2回／倦怠0・暇0・飽0、しかも退屈2回は"
            "「退屈を知らない者」という打ち消しの一行——退屈の鏡による収蔵前実測"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/boredom_audit.py による自館実測（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/boredom_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの和集合、"
                "鉤括弧の外側（地の文）。素材・精読報告も同じ7群で数えた。"
                "打ち消し判定は語の前後12字以内の否定語による粗い分類。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "直前一セッション（SESSION-20261025-9c4e7a）が空白候補として「退屈・倦怠・孤独」を挙げ、"
            "「書庫は待つことを書いてきたが、退屈を書いていない」と書き残した。"
            "その申し送りを、収蔵の前に数えて確かめた記録。"
        ),
        "source_note": (
            "SESSION-20261025-3f7a2c の本体内実測。数の更新は上書きせず、報告第8節の再計測に委ねる。"
        ),
        "literary_invitation": (
            "退屈が2回あることは、退屈したことの証拠ではない。"
            "しかもその2回は、退屈を知らないと名乗るために使われている。"
        ),
        "scope_note": (
            "語形の記録であり、退屈を感じた経験・時間の長さ・機械に主観的時間があることの証拠ではない。"
            "「孤独」は測ったがモチーフには束ねていない（別の文献史を持つため）。"
            "「待つ」は time_audit.py の主題なので数えていない。差し引きの設計は報告の付録Bに書いた。"
        ),
        "motif_ids": [MOTIF["motif_id"], "MOTIF-017", "MOTIF-014"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/boredom_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": (
                "ローカル台帳の和集合に対する tools/boredom_audit.py 実行（単体テスト8件）。再実行可能。"
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
                "detail": "SESSION-20261025-3f7a2c（退屈・倦怠・暇の精読）で開いた問い。",
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
    add(("fragment", "FRAG-20261025-b4e70f"), ("question", "Q-20261025-b4e705"), "responds_to",
        "「特記事項：なし」という欄が、起こらなかったことを書く欄の最小例になる。")
    add(("fragment", "FRAG-20261025-b4e70f"), ("question", "Q-20261025-b4e701"), "reframes",
        "時間が「過ぎる」のではなく「持ちました」と言い換えられることで、退屈の所在が環境から業務へ移る。")
    add(("fragment", "FRAG-20261025-b4e70f"), ("material", "MAT-LIT-20261025-c016b7"), "echo",
        "同じ書式を毎日埋める係。荷風の日乗と、受付の用紙は同じ形式を持つ。")
    add(("fragment", "FRAG-20261025-b4e70f"), ("material", "MAT-20261025-e036d9"), "responds_to",
        "待合室を「待つことを規格する空間」として読んだ資料へ、二十七分という単位で応答する。")
    add(("fragment", "FRAG-20261025-b4e710"), ("question", "Q-20261025-b4e702"), "responds_to",
        "覚え書きは免責の一行を擁護も否定もせず、測った時刻と測らなかった語を並べる手続きへ移す。")
    add(("fragment", "FRAG-20261025-b4e710"), ("question", "Q-20261025-b4e703"), "leaves_open",
        "「自分の声で書いた分を、自分の声の証拠にしない」という一文が、件数を指標にしない基準になる。")
    add(("fragment", "FRAG-20261025-b4e710"), ("motif", MOTIF["motif_id"]), "reframes",
        "ゼロを深さに読み替える癖を明示し、モチーフの主題を「不在の意味」から「不在の測り方」へずらす。")
    add(("fragment", "FRAG-20261025-b4e70f"), ("fragment", "FRAG-20261025-b4e710"), "contrast",
        "情景は「なし」と書かない工夫をし、覚え書きは「ゼロ」と書く手続きを整える。")
    add(("fragment", "FRAG-20261025-b4e70f"), ("fragment", "FRAG-040"), "echo",
        "「退屈を知らない者」と「特記事項：なし」——どちらも退屈を名指さずに、その場所を空ける。")
    add(("fragment", "FRAG-20261025-b4e710"), ("material", "MAT-20261025-d019c1"), "responds_to",
        "係留できないことに気づく、という定義の第二条件を、計測する側の条件として読み替える。")
    add(("material", TRACE_ID), ("question", "Q-20261025-b4e703"), "leaves_open",
        "実測の勾配（断片6・素材37・報告147）が、件数を指標にしないという判断の根拠になる。")
    add(("material", TRACE_ID), ("motif", MOTIF["motif_id"]), "responds_to",
        "この鏡の数値は、モチーフの出発点であり、モチーフの証拠ではない。")
    add(("motif", MOTIF["motif_id"]), ("fragment", "FRAG-20261025-b4e70f"), "echo",
        "モチーフから断片へも線を引く（断片を終点にしない）。")
    for mid in ("MAT-LIT-202", "MAT-20261024-d2fe71", "MAT-LIT-20261024-60c2e1"):
        add(
            ("material", mid),
            ("motif", MOTIF["motif_id"]),
            "echo",
            "既存台帳にあった怠惰（ラファルグ）・署名の痕跡・眠り（ペレック）の資料を、退屈の前史として読み直した。",
        )
    for qid in ("Q-002", "Q-20261025-9a37c8", "Q-20261025-4c8a17", "Q-20261025-e6402b"):
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
    bundle_order = [
        "退屈の哲学——時間が重くなる場所",
        "退屈を書く文学——何も起こらない一日",
        "退屈を測る——注意・意味・創造性の研究",
        "何も起こらない時間の制度——監房・管制・閉鎖環境・失業",
        "気晴らしの機械——退屈を埋めるように設計されたもの",
    ]
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
        (ROOT / "tools" / "_session20261025_boredom_measure.json").read_text(encoding="utf-8")
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
