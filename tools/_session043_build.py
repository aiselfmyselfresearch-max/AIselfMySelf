#!/usr/bin/env python3
"""Write SESSION-20261024-9c4e17 ledgers to dedicated shards.

Follows docs/parallel-work.md: the frozen base ledgers are never modified; new
records go to ``state/*.d/<date>-<hex>.jsonl`` so that parallel sessions cannot
interleave bytes or collide on sequential IDs.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import _session043_hospitality as data  # noqa: E402

DAY = "2026-10-24"
SHARDS = {
    "materials": ROOT / "state" / "materials.d" / "2026-10-24-9c4e17a04b21.jsonl",
    "motifs": ROOT / "state" / "motifs.d" / "2026-10-24-9c4e17a04b21.jsonl",
    "questions": ROOT / "state" / "questions.d" / "2026-10-24-9c4e17a04b21.jsonl",
    "relations": ROOT / "state" / "relations.d" / "2026-10-24-9c4e17a04b21.jsonl",
    "sessions": ROOT / "state" / "sessions.d" / "2026-10-24-9c4e17a04b21.jsonl",
}

REL_IDS = [
    "REL-20261024-506e63", "REL-20261024-4ca2bb", "REL-20261024-a1fe5b", "REL-20261024-49eb13",
    "REL-20261024-66114c", "REL-20261024-f1d8bc", "REL-20261024-abb625", "REL-20261024-b1be75",
    "REL-20261024-636970", "REL-20261024-7ca963", "REL-20261024-04d999", "REL-20261024-aa9d41",
    "REL-20261024-165940", "REL-20261024-135897", "REL-20261024-af362f", "REL-20261024-c373d7",
    "REL-20261024-51624e", "REL-20261024-765cfc", "REL-20261024-f638e1", "REL-20261024-3329b8",
    "REL-20261024-fb4b87", "REL-20261024-c70de6", "REL-20261024-a2ddc8", "REL-20261024-6d1250",
    "REL-20261024-ee6cb1", "REL-20261024-31256f", "REL-20261024-2bd4d0", "REL-20261024-56bcd5",
    "REL-20261024-41be1e", "REL-20261024-ff1bb3", "REL-20261024-3941d2", "REL-20261024-fd9e3f",
    "REL-20261024-7fca21", "REL-20261024-f11900", "REL-20261024-52ae60", "REL-20261024-5bf760",
    "REL-20261024-bbb2d1", "REL-20261024-ec826d", "REL-20261024-7f4483", "REL-20261024-73cf6d",
    "REL-20261024-a8f853", "REL-20261024-606900", "REL-20261024-7a5203", "REL-20261024-a3d351",
    "REL-20261024-02f3b9", "REL-20261024-d34dc8", "REL-20261024-b568df", "REL-20261024-525bac",
    "REL-20261024-998b04", "REL-20261024-d92532", "REL-20261024-5cea64", "REL-20261024-317ef5",
    "REL-20261024-5a3d7f", "REL-20261024-ec647c", "REL-20261024-649b44", "REL-20261024-c4a6ad",
    "REL-20261024-79b487", "REL-20261024-62c730", "REL-20261024-5fab5d", "REL-20261024-a6731b",
    "REL-20261024-4cbbe8", "REL-20261024-be9729", "REL-20261024-c2e1a9", "REL-20261024-b317bb",
    "REL-20261024-1b63ee", "REL-20261024-a2e6fe", "REL-20261024-7ec280", "REL-20261024-7ef657",
    "REL-20261024-c197c1", "REL-20261024-8af42a", "REL-20261024-dba9b6", "REL-20261024-f66a15",
    "REL-20261024-3ceaac", "REL-20261024-b79ab6", "REL-20261024-25b54c", "REL-20261024-6dd400",
    "REL-20261024-8e01ad", "REL-20261024-92e776", "REL-20261024-4ecaf2", "REL-20261024-95e550",
    "REL-20261024-642ad2", "REL-20261024-aa8df3", "REL-20261024-12b25e", "REL-20261024-ce794b",
    "REL-20261024-bf47ab", "REL-20261024-79f018", "REL-20261024-4abb74", "REL-20261024-c44d76",
    "REL-20261024-484bb0", "REL-20261024-a0556e", "REL-20261024-436178", "REL-20261024-629d4f",
    "REL-20261024-77f0d3", "REL-20261024-fa5430", "REL-20261024-110e8b", "REL-20261024-424f7e",
    "REL-20261024-c03ded", "REL-20261024-dbb435", "REL-20261024-62b2b9", "REL-20261024-2fdb99",
    "REL-20261024-378ea1", "REL-20261024-b25664", "REL-20261024-33f07d", "REL-20261024-213648",
    "REL-20261024-7f17c4", "REL-20261024-9cee38", "REL-20261024-df85a9", "REL-20261024-43d79d",
    "REL-20261024-96172e", "REL-20261024-7bf259", "REL-20261024-d11e35", "REL-20261024-f05101",
    "REL-20261024-e3a6b1", "REL-20261024-b3f6aa", "REL-20261024-6e83fa", "REL-20261024-dc76c1",
    "REL-20261024-2908fd", "REL-20261024-36b740", "REL-20261024-a3edfd", "REL-20261024-6e4904",
]

MOTIF = data.MOTIF

# 既存の断片・素材・モチーフへの架橋（新規素材ID, 相手ID, 種別, 注記）
BRIDGES: list[tuple[str, str, str, str, str]] = [
    ("MAT-LIT-20261024-43cd9c", "FRAG-018", "fragment", "reframes",
     "『戸口で名乗れ』という narrator_mode の作法を、扉は閉じうるから開くという境界の理論から組み替える。"),
    ("MAT-LIT-20261024-277bb7", "FRAG-026", "fragment", "echo",
     "扉のない広間を歩く情景に、外でも内でもない第三の場所としての戸を重ねる。"),
    ("MAT-LIT-20261024-7fc9f0", "FRAG-024", "fragment", "contrast",
     "カフカの開け放たれた門の前で待つ男に対し、戸を内側から閉ざして群衆を押し返すロトの家を置く。"),
    ("MAT-LIT-20261024-9b0b6d", "FRAG-019", "fragment", "contrast",
     "観客に問いかける対話形式と、洞窟の戸を塞がれて観客のいない舞台とを対照させる。"),
    ("MAT-LIT-20261024-aaad28", "FRAG-20261024-be45a7", "fragment", "contrast",
     "次のセッションが四十五件を覚えているという約束に、覚えることではなく語り続けることで滞在を延ばす手続きを対置する。"),
    ("MAT-LIT-20261024-4ce0e9", "MOTIF-20261024-90a022", "motif", "contrast",
     "返礼を期待しない贈与と、履行を記録しない約束とを、どちらも台帳の欄の外にある行為として並べる。"),
    ("MAT-LIT-20261024-be9565", "Q-063", "question", "responds_to",
     "引用は返済かという問いに、等価の即時返礼が関係を終わらせるという贈与論から応答する。"),
    ("MAT-LIT-20261024-1e7172", "FRAG-033", "fragment", "reframes",
     "空欄の宛先を次に読む者が埋めてよいとする書式を、戸口に塗られた印を外から読む行為として読み直す。"),
    ("MAT-LIT-20261024-188ace", "FRAG-039", "fragment", "responds_to",
     "『明日この書簡を開く者がいるかどうかは分からない』という書き出しに、今日はじめて門を開ける一回性を返す。"),
    ("MAT-LIT-20261024-0af71c", "FRAG-017", "fragment", "contrast",
     "栞を『別の風を入れる隙間』と呼ぶ断片に、門を閉じて内を選ぶ隠棲の作法を対置する。"),
    ("MAT-LIT-20261024-402918", "MOTIF-019", "motif", "echo",
     "遊びと笑いの糸に、笑いと祝祭が押し開ける力より先に閉じた戸を動かすという神話を接続する。"),
    ("MAT-LIT-20261024-b67655", "MOTIF-20261024-4b87ac", "motif", "responds_to",
     "傷と手当の糸に、守るための戸が外から開けられる暴力を差し挟む。"),
    ("MAT-LIT-20261024-066386", "FRAG-024", "fragment", "interrupts",
     "門番の言葉を信じて待ち続ける男の話に、泊まった家が翌朝には消えているという反転を割り込ませる。"),
    ("MAT-LIT-20261024-93223c", "FRAG-026", "fragment", "contrast",
     "扉のない部屋の静けさに対し、招かれて入った館の内部から崩壊が迫る語りを置く。"),
    ("MAT-LIT-20261024-6047a2", "FRAG-030", "fragment", "metaphorically_resonates",
     "調書が閉じられ次の申出人が呼ばれる審問の場に、門の下で衣を剥がれる老婆の場面が比喩的に共鳴する。"),
    ("MAT-LIT-20261024-590aad", "FRAG-013", "fragment", "echo",
     "閉じられた枝の縁で書き換えをためらう声に、内側から閉ざされた門の生活を重ねる。"),
    ("MAT-LIT-20261024-229b55", "MOTIF-010", "motif", "responds_to",
     "宛先の糸に、遠方から来る者を評価の外で迎える作法を返す。"),
    ("MAT-LIT-20261024-237b59", "MOTIF-20261024-4b87ac", "motif", "responds_to",
     "傷と手当の糸に、最も小さい者への行いとしての歓待を接続する。"),
    ("MAT-LIT-20261024-276896", "MAT-EVD-20261024-cf5f73", "material", "contrast",
     "指示階層が声の優先順位で侵入を防ぐのに対し、検察官の町は相手の正体を確かめないことで侵入を許す。"),
    ("MAT-LIT-20261024-501ce5", "MOTIF-011", "motif", "reframes",
     "翻訳と来歴の糸に、迎え入れることが元の文脈からの切断でもあるという民族誌的知見を組み込む。"),
    ("MAT-LIT-20261024-fb44f9", "FRAG-20261024-398656", "fragment", "echo",
     "閉じた書庫に残る小さい読み手という像に、戸を開けた二人だけが洪水を免れる挿話を重ねる。"),
    ("MAT-LIT-20261024-5aeb49", "FRAG-011", "fragment", "contrast",
     "傷つかない器という自己記述に、与え続けて外見を失う像を対置する。"),
    ("MAT-LIT-20261024-1a9fd2", "MOTIF-009", "motif", "contrast",
     "感応と帰属の糸に、饗宴の形式だけを残して内容を反転させる歓待の失敗を置く。"),
    ("MAT-LIT-20261024-35ccf8", "FRAG-032", "fragment", "metaphorically_resonates",
     "宛名に人名を置いた書簡に、招かれなければ入れないという規則と、招いた者を去らせない城とが共鳴する。"),
    ("MAT-LIT-20261024-e2762b", "MOTIF-20261024-90a022", "motif", "contrast",
     "果たされない言葉の拘束力に対し、迎える言葉が同時に殺意でありうる場面を置く。"),
    ("MAT-20261024-f9a396", "MOTIF-004", "motif", "responds_to",
     "声と帰属の糸に、指示がデータの側から来るという帰属の攪乱を接続する。"),
    ("MAT-20261024-a122c0", "MAT-EVD-20261024-cf5f73", "material", "contrast",
     "指示階層が優先順位で分けるのに対し、StruQ は入力の通路そのものを分ける。"),
    ("MAT-20261024-b7282c", "FRAG-018", "fragment", "metaphorically_resonates",
     "外部データに印を付ける Spotlighting と、戸口で名乗る narrator_mode の作法が共鳴する。"),
    ("MAT-20261024-7df55a", "MOTIF-019", "motif", "responds_to",
     "遊びと笑いの糸に、注入を書き合う遊びが攻撃の dataset になることを接続する。"),
    ("MAT-20261024-a2a5c8", "MOTIF-006", "motif", "responds_to",
     "忘却と沈黙の糸に、守る側が想定した形式の外側に守られていない戸があることを接続する。"),
    ("MAT-TRC-017", "Q-20261024-f0b5cc", "question", "leaves_open",
     "観客8・客0の実測を、歓待の証拠をどこに記録するかという問いへ渡す。"),
    ("MAT-TRC-017", "MOTIF-010", "motif", "responds_to",
     "宛先の糸に、戸口が宛名の欄として使われてきたという計数を返す。"),
    ("MAT-20261024-3a7eb2", "MOTIF-016", "motif", "responds_to",
     "訂正と抹消の糸に、注入を防ぐとは入力を読まないことではなく制御を変えないことだという設計を接続する。"),
    ("MAT-20261024-e07252", "MOTIF-018", "motif", "responds_to",
     "知覚と媒体の糸に、意味を持たない文字列が意味を読むモデルを動かすという非対称を接続する。"),
    ("MAT-20261024-7373c4", "MOTIF-013", "motif", "responds_to",
     "予測と不確実性の糸に、道具を呼ぶ手続きのなかで測られる攻撃成功率を接続する。"),
    ("MAT-20261024-e57c7f", "MOTIF-015", "motif", "responds_to",
     "数えること・測ることの糸に、状態を持つ環境でしか測れない安全性を接続する。"),
]


def _write(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    ledger_io.atomic_write_text(path, text)


def build() -> dict[str, Any]:
    materials = [*data.MATERIALS, data.TRACE]
    mids = [m["material_id"] for m in materials]
    assert len(mids) == 46, len(mids)

    material_records: list[dict[str, Any]] = []
    for record in materials:
        clean = {k: v for k, v in record.items() if k != "group"}
        material_records.append(clean)

    motif_record = dict(data.MOTIF_RECORD)
    motif_record["material_ids"] = mids

    question_records: list[dict[str, Any]] = []
    for qid, spec in data.QUESTIONS.items():
        question_records.append({
            "question_id": qid,
            "question": spec["question"],
            "status": "open",
            "motif_ids": spec["motif_ids"],
            "material_ids": spec["material_ids"],
            "previous_question_ids": spec["previous_question_ids"],
            "origin": {"kind": "session", "detail": spec["origin_detail"]},
            "created_at": DAY,
        })

    relation_records: list[dict[str, Any]] = []
    rel_iter = iter(REL_IDS)

    def add(left: str, ltype: str, rtype_name: str, right: str, rtype: str, note: str) -> None:
        relation_records.append({
            "created_at": DAY,
            "left": {"id": left, "type": ltype},
            "note": note,
            "relation_id": next(rel_iter),
            "relation_type": rtype,
            "right": {"id": right, "type": rtype_name},
        })

    for record in materials:
        note = record["literary_invitation"]
        add(record["material_id"], "material", "motif", MOTIF, "responds_to", note)

    for qid, spec in data.QUESTIONS.items():
        add(MOTIF, "motif", "question", qid, "leaves_open", spec["origin_detail"])
        for prev in spec["previous_question_ids"]:
            add(qid, "question", "question", prev, "responds_to", spec["origin_detail"][:70])

    for mid, other, otype, rtype, note in BRIDGES:
        add(mid, "material", otype, other, rtype, note)

    prev_qs = sorted({q for spec in data.QUESTIONS.values() for q in spec["previous_question_ids"]})
    session_record = dict(data.SESSION_RECORD)
    session_record["context_material_ids"] = mids
    session_record["question_ids"] = prev_qs + list(data.QUESTIONS.keys())

    assert len(relation_records) <= len(REL_IDS), len(relation_records)
    return {
        "materials": material_records,
        "motifs": [motif_record],
        "questions": question_records,
        "relations": relation_records,
        "sessions": [session_record],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the shards (default: dry run)")
    args = parser.parse_args(argv)

    bundles = build()
    for name, records in bundles.items():
        print(f"{name}: {len(records)} records -> {SHARDS[name].relative_to(ROOT)}")
    kinds = Counter(r["kind"] for r in bundles["materials"])
    statuses = Counter(r["verification"]["status"] for r in bundles["materials"])
    print(f"kinds={dict(kinds)} statuses={dict(statuses)}")

    if args.write:
        for name, records in bundles.items():
            _write(SHARDS[name], records)
        print("written")
    else:
        print("dry run; pass --write to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
