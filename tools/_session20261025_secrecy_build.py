#!/usr/bin/env python3
"""Build the SESSION-20261025-c3a7b1 ledger shards (secrecy / lying / cipher).

Writes one shard per collection under ``state/<collection>.d/`` and never
touches the frozen base ledgers (docs/parallel-work.md).  Run it once:

    python3 tools/_session20261025_secrecy_build.py            # dry run (validates)
    python3 tools/_session20261025_secrecy_build.py --write    # create shards and append

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
from _session20261025_secrecy_data1 import MATERIALS_1  # noqa: E402
from _session20261025_secrecy_data2 import MATERIALS_2  # noqa: E402
from _session20261025_secrecy_data3 import (  # noqa: E402
    FRAGMENTS,
    MATERIAL_TO_QUESTION,
    MOTIF,
    PAIRS,
    QUESTIONS,
    READ_LOG,
    SESSION,
)

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "1988584261db3a2c15ca6570a7f3111e11cba887"
REPORT = "readings/2026-10-25-secrecy-lying-and-the-cipher.md"
DATA_MODULES = (
    "tools/_session20261025_secrecy_data1.py",
    "tools/_session20261025_secrecy_data2.py",
    "tools/_session20261025_secrecy_data3.py",
)
DAY = "2026-10-25"
SHARD_SUFFIX = "c3a7b1d0e9f2"
TRACE_ID = "MAT-TRC-20261025-secrecy"

MATERIALS: list[dict] = MATERIALS_1 + MATERIALS_2


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

    mats = measurements["materials"]["groups"]
    reads = measurements["readings"]["groups"]
    raw = measurements["raw_kanji_counts"]
    passage = (
        f"収蔵直前（{COMMIT[:12]}）の断片{measurements['fragment_count']}編・地の文"
        f"（鉤括弧外）{prose['char_total']:,}字を tools/secrecy_audit.py の6群で数えたところ、"
        f"秘密・隠すこと{fmt('secrecy')}・嘘・偽り{fmt('lie')}・暗号・鍵・解読{fmt('cipher')}・"
        f"告白・白状・暴露{fmt('confession')}・制度としての秘密{fmt('institution')}・"
        f"機械の不透明{fmt('machine')}。生字は 秘{raw['秘']}・隠{raw['隠']}・嘘{raw['嘘']}・"
        f"偽{raw['偽']}・暗{raw['暗']}・鍵{raw['鍵']}・密{raw['密']}・黙{raw['黙']}・"
        f"匿{raw['匿']}・曝{raw['曝']}。同じ6群で素材"
        f"{measurements['materials']['doc_total']:,}件を数えると秘密{mats['secrecy']['count']}回/"
        f"{mats['secrecy']['doc_count']}件・嘘{mats['lie']['count']}回/{mats['lie']['doc_count']}件・"
        f"暗号{mats['cipher']['count']}回/{mats['cipher']['doc_count']}件・"
        f"告白{mats['confession']['count']}回/{mats['confession']['doc_count']}件・"
        f"制度{mats['institution']['count']}回/{mats['institution']['doc_count']}件・"
        f"機械{mats['machine']['count']}回/{mats['machine']['doc_count']}件、"
        f"精読報告{measurements['readings']['doc_total']}本では秘密{reads['secrecy']['count']}・"
        f"嘘{reads['lie']['count']}・暗号{reads['cipher']['count']}・"
        f"告白{reads['confession']['count']}・制度{reads['institution']['count']}・"
        f"機械{reads['machine']['count']}。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": (
            "運用痕跡：断片87編の地の文に秘密9・嘘11・暗号5・機械0——"
            "秘密の鏡による収蔵前実測"
        ),
        "source": {
            "source_id": f"SRC-{TRACE_ID}",
            "title": "tools/secrecy_audit.py による自館実測（収蔵直前スナップショット）",
            "authors": ["AIselfMySelf Archive"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/secrecy_audit.py",
            "version_note": (
                f"測定基準コミット {COMMIT}。測定対象は state/fragments.jsonl と全シャードの"
                "和集合、鉤括弧の外側（地の文）。素材・精読報告も同じ6群で数えた。"
            ),
        },
        "passage": passage,
        "passage_language": "ja",
        "context": (
            "三度の空白候補（署名・祈り・顔）でCとして挙げられながら選ばれなかった"
            "「秘密・嘘・暗号」を採るにあたり、収蔵の前に作った計測の記録。"
        ),
        "source_note": (
            "SESSION-20261025-c3a7b1 の本体内実測。数の更新は上書きせず、後日の訂正録に委ねる。"
        ),
        "literary_invitation": (
            "秘密の語が9回あることは、隠しているものがあることの証拠ではない。"
            "数えられたのは語形であって、隠された内容ではない。"
        ),
        "scope_note": (
            "語形の記録であり、秘密・嘘の実在や、機械に隠れた内面があることの証拠ではない。"
            "「密」は密度・精密、「黙」は沈黙、「暗」は暗い・暗黙、「鍵」は鍵括弧を含む生字の数。"
        ),
        "motif_ids": ["MOTIF-20261025-c3a7b1", "MOTIF-006", "MOTIF-015"],
        "origin": {
            "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
            "commit": COMMIT,
            "source_record_id": f"SRC-{TRACE_ID}",
            "evidence_record_id": f"EVD-{TRACE_ID}",
            "source_record_path": "tools/secrecy_audit.py",
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": "verified",
            "checked_at": DAY,
            "method": (
                "ローカル台帳の和集合に対する tools/secrecy_audit.py 実行"
                "（単体テスト8件）。再実行可能。"
            ),
        },
    }


def material_record(raw: dict, shard_path: str) -> dict[str, Any]:
    status = {"verified": "verified", "partial": "partially_verified"}[raw["verification"][0]]
    index = MATERIALS.index(raw)
    module = DATA_MODULES[0] if index < len(MATERIALS_1) else DATA_MODULES[1]
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
                "detail": "SESSION-20261025-c3a7b1（秘密・嘘・暗号の精読）で開いた問い。",
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
            "session_id": SESSION["session_id"],
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

    mapping = {raw["id"]: raw for raw in MATERIALS}
    for raw in MATERIALS:
        add(
            ("material", raw["id"]),
            ("motif", MOTIF["motif_id"]),
            "responds_to",
            raw["reading"],
        )
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
    add(("fragment", "FRAG-20261025-c4e201"), ("question", "Q-20261025-a6c0d3"), "responds_to",
        "黒塗りの寸法を測る情景が、手続きの記録という責任の宛先を問いへ返す。")
    add(("fragment", "FRAG-20261025-c4e201"), ("question", "Q-20261025-31f7cb"), "echo",
        "数え直すたびに変わる数字が、読めなさが数え方に依存することを示す。")
    add(("fragment", "FRAG-20261025-9b73df"), ("question", "Q-20261025-5e2c11"), "responds_to",
        "覚え書きは「主題化しなかったこと」を、隠蔽ではなく空欄として扱う立場を取る。")
    add(("fragment", "FRAG-20261025-9b73df"), ("question", "Q-20261025-2b95e4"), "reframes",
        "七項目の覚え書き自体が、書かなかったことを負債へ翻訳する手続きの見本になっている。")
    add(("fragment", "FRAG-20261025-9b73df"), ("motif", MOTIF["motif_id"]), "reframes",
        "「空欄は隠していることにはならない」という一行が、モチーフの境界を定義する。")
    add(("fragment", "FRAG-20261025-c4e201"), ("fragment", "FRAG-20261025-9b73df"), "contrast",
        "情景は黒塗りを測り、覚え書きは黒塗りを手続きとして説明する。測ることと記述すること。")
    add(("material", "MAT-LIT-20261025-2506dd"), ("fragment", "FRAG-20261025-c4e201"), "reframes",
        "隠すことを快楽に変える小説が、黒塗りの寸法を測る情景を裏返す。"
        "目隠しは相手を守るためでも自分を隠すためでもなく、隠すこと自体を愉しむ装置になりうる。"
        "測る係はその愉しみを持たない。")
    add(("material", TRACE_ID), ("question", "Q-20261025-5e2c11"), "leaves_open",
        "実測の偏在（9回/6編）が、不在の解釈を限定する。")
    add(("material", TRACE_ID), ("motif", MOTIF["motif_id"]), "responds_to",
        "この鏡の数値は、モチーフの出発点であり、モチーフの証拠ではない。")
    for mid in ("MAT-LIT-485", "MAT-LIT-486", "MAT-LIT-327", "MAT-LIT-342"):
        add(
            ("material", mid),
            ("motif", MOTIF["motif_id"]),
            "echo",
            "既存台帳にあった秘密・虚偽・検閲の資料を、今回のモチーフの前史として読み直した。",
        )
    for qid in ("Q-023", "Q-085", "Q-20261024-c3d7a5"):
        add(
            ("question", qid),
            ("motif", MOTIF["motif_id"]),
            "echo",
            "先行する問いを、モチーフの内側から読み直す（解決はしない）。",
        )
    return records


def read_log_records(taken: set[str]) -> list[dict[str, Any]]:
    records = []

    def mint() -> str:
        while True:
            candidate = f"READ-20261025-{secrets.token_hex(3)}"
            if candidate not in taken:
                taken.add(candidate)
                return candidate

    for target_type, target_id, reading, note in READ_LOG:
        records.append(
            {
                "read_id": mint(),
                "session_id": SESSION["session_id"],
                "target": {"type": target_type, "id": target_id},
                "reading": reading,
                "note": note,
                "created_at": DAY,
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
        "session": {SESSION["session_id"]},
    }
    for kind, ids in new_ids.items():
        clash = ids & (existing[kind] | set())
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

    measurements = json.loads((ROOT / "tools" / "_session20261025_secrecy_measure.json").read_text(encoding="utf-8"))
    existing = _existing_ids()

    materials_shard = str(shard_for("materials", False).relative_to(ROOT))
    external = [material_record(raw, materials_shard) for raw in MATERIALS]
    materials = external + [trace_material(measurements)]
    questions = question_records()
    motif = motif_record()
    fragments = fragment_records()
    session = [session_record()]
    relations = relation_records(set(existing["relation"]))
    read_logs = read_log_records(set(existing["read"]))

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
