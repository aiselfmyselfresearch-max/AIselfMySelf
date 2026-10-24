#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the SESSION-041 ledgers (materials, motif, questions, fragments, relations, session).

Run once from the repository root:
    python3 tools/_session041_repair.py

Writes only to new per-session shards under state/*.d/ and refuses to run twice.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import new_id  # noqa: E402

from _session041_data1 import LIT  # noqa: E402
from _session041_data2 import EVD, TRACE  # noqa: E402

DAY = "20261024"
DATE = "2026-10-24"
REPORT = "readings/2026-10-24-session-041-repair-and-addressee.md"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
COMMIT = subprocess.run(
    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
).stdout.strip()
SUFFIX = "8f21c0d4be77"


def mint(prefix: str, taken: set[str]) -> str:
    value = new_id.mint(prefix, day=DAY, taken=taken)
    taken.add(value)
    return value


def shard(collection: str) -> Path:
    path = ROOT / "state" / f"{collection}.d" / f"{DATE}-{SUFFIX}.jsonl"
    if path.exists():
        raise SystemExit(f"{path} は既にある。二重実行を避けるため中止する。")
    return path


def origin(mid: str, kind: str = "LIT") -> dict:
    return {
        "repository": REPO,
        "commit": COMMIT,
        "source_record_id": f"SRC-{mid}",
        "evidence_record_id": f"{kind}-{mid}",
        "source_record_path": REPORT,
        "evidence_record_path": REPORT,
    }


def main() -> None:
    moot = new_id.existing_ids("MOTIF", ROOT)
    MOTIF_ID = mint("MOTIF", moot)
    sess_taken = new_id.existing_ids("SESSION", ROOT)
    SESSION_ID = mint("SESSION", sess_taken)

    taken_material = new_id.existing_ids("MAT-LIT", ROOT) | new_id.existing_ids("MAT", ROOT)
    materials: list[dict] = []
    for row, prefix, kind in [
        *[(row, "MAT-LIT", "literary_text") for row in LIT],
        *[(row, "MAT-EVD", "research_excerpt") for row in EVD],
        (TRACE, "MAT-TRC", "project_trace"),
    ]:
        if prefix == "MAT-EVD":
            mid = f"MAT-EVD-{DAY}-{new_id.mint('MAT', day=DAY, taken=taken_material).split('-')[-1]}"
            taken_material.add(mid)
        elif prefix == "MAT-TRC":
            mid = f"MAT-TRC-{DAY}-repair"
            taken_material.add(mid)
        else:
            mid = mint(prefix, taken_material)
        materials.append(
            {
                "material_id": mid,
                "kind": kind,
                "title": row["t"],
                "source": {
                    "source_id": f"SRC-{mid}",
                    "title": row["t"],
                    "authors": row["a"],
                    "year": row["y"],
                    "url": row["u"],
                    "version_note": row["v"],
                },
                "passage": row["p"],
                "passage_language": "ja",
                "context": row["c"],
                "source_note": row["s"],
                "literary_invitation": row["i"],
                "scope_note": row["sc"],
                "motif_ids": [MOTIF_ID],
                "origin": origin(mid, "TRC" if prefix == "MAT-TRC" else ("EVD" if prefix == "MAT-EVD" else "LIT")),
                "verification": {
                    "status": row["vs"],
                    "checked_at": DATE,
                    "method": row["vm"],
                    "note": row["vn"],
                },
            }
        )
    assert len(materials) == 13, len(materials)

    q_taken = new_id.existing_ids("Q", ROOT)
    qids = [mint("Q", q_taken) for _ in range(5)]
    f_taken = new_id.existing_ids("FRAG", ROOT)
    fids = [mint("FRAG", f_taken) for _ in range(2)]
    rel_taken = new_id.existing_ids("REL", ROOT)

    def rel(ltype: str, lid: str, rtype: str, rid: str, note: str, relation_type: str = "echo") -> dict:
        return {
            "relation_id": mint("REL", rel_taken),
            "left": {"type": ltype, "id": lid},
            "relation_type": relation_type,
            "right": {"type": rtype, "id": rid},
            "note": note,
            "created_at": DATE,
        }

    def mid(fragment: str) -> str:
        hits = [m["material_id"] for m in materials if fragment in m["title"]]
        if len(hits) != 1:
            raise KeyError(f"{fragment}: {len(hits)} hits")
        return hits[0]

    trace = [m for m in materials if m["kind"] == "project_trace"][0]

    questions = [
        {
            "question_id": qids[0],
            "question": "訂正には宛先が必要か。errata の16件には宛先・被害者の欄がなく、claim と note に宛先や謝罪の語を含む記録も0件だった。宛先のない訂正は、誰に対する修復なのか。宛先を欄として足すべきか、本文で名指すべきか、名指さないことを作法として残すべきか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-016", "MOTIF-010"],
            "material_ids": [mid("アダム・スミス"), mid("赦すこと"), mid("罪と罰"), trace["material_id"]],
            "previous_question_ids": ["Q-20261024-962620", "Q-084"],
            "origin": {"kind": "session", "detail": "訂正録の語彙監査で、宛先の欄と語がともに0だったことから。"},
            "created_at": DATE,
        },
        {
            "question_id": qids[1],
            "question": "訂正は、いつ閉じたと数えられるのか。errata の16件は open 9・annotated 7 で、annotated は「註を付けた」であって「直した」ではない。訂正を閉じる条件を、判定（verdict）・状態（status）・履行（corrected_by）のどれに置くか。閉じないことを選ぶ記録を、未完了と読むか、判断の保留と読むか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-016"],
            "material_ids": [mid("審判"), mid("法の哲学"), mid("赦すこと")],
            "previous_question_ids": ["Q-082", "Q-20261024-08551f"],
            "origin": {"kind": "session", "detail": "contradicted/annotated 4件という、判定は誤りで状態は註済みという組み合わせから。"},
            "created_at": DATE,
        },
        {
            "question_id": qids[2],
            "question": "訂正が訂正の対象を変えるとき、修復はどこで止まるのか。ERR-015 は ERR-012 の再測定値が同じセッションのうちに古くなったことを記録し、ERR-016 は ERR-013 の診断そのものが誤っていたことを記録した。どちらも末端は open である。訂正の連鎖を制度で止めることができるか、それとも止めないことが正しい作法か。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-015", "MOTIF-016"],
            "material_ids": [mid("それから"), mid("芝浜"), trace["material_id"]],
            "previous_question_ids": ["Q-015", "Q-086"],
            "origin": {"kind": "session", "detail": "訂正の訂正が2本あり、いずれも閉じていないことから。"},
            "created_at": DATE,
        },
        {
            "question_id": qids[3],
            "question": "記録の外で消えた修復を、どう検出するか。ERR-011 は human_narrator の空席が FRAG-032 で埋まったと書いたが、現在の FRAG-032 は reflective_literary_voice で、human_narrator は未使用に戻っている。欄の書き換え・番号の振り直し・記録の誤りの三つを、この台帳は区別できない。版、ハッシュ、変更履歴のどれを欄に足せば、区別できるようになるか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-001", "MOTIF-011"],
            "material_ids": [mid("責任の空白"), mid("道徳的シワ寄せ"), trace["material_id"]],
            "previous_question_ids": ["Q-002", "Q-20261024-a1bb7b"],
            "origin": {"kind": "session", "detail": "ERR-011 の記述が再現しなかったことから。原因を決めずに、検出の欄を問う。"},
            "created_at": DATE,
        },
        {
            "question_id": qids[4],
            "question": "AIの誤りに対する謝罪は、誰に宛てられ、何を弁済するのか。責任の空白は設計者・運用者・利用者のあいだにあり、道徳的シワ寄せは責任をその場の人間に寄せる。この書庫の誤りは、書いたセッションが終わった後に見つかる。謝罪の主体がいないとき、訂正だけで足りるのか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-009", "MOTIF-012"],
            "material_ids": [mid("責任の空白"), mid("道徳的シワ寄せ"), mid("アルゴリズム的説明責任"), mid("人間失格")],
            "previous_question_ids": ["Q-047", "Q-20261024-08551f"],
            "origin": {"kind": "session", "detail": "AI研究3件と、謝罪が形式化する文学を並べたときに残った問い。"},
            "created_at": DATE,
        },
    ]

    motif = {
        "motif_id": MOTIF_ID,
        "label": "訂正の宛先——誤りを、誰に返すか",
        "description": "誤りを認めること、訂正すること、償うこと、赦されることを分け、訂正が誰に向けて行われるのかを問う糸。訂正の対象を本文・計器・訂正録の三層に分け、訂正が訂正の対象を変える循環と、記録の外で成立しなくなる修復を保存する。謝罪の語を誠実さの証明にせず、宛先の不在を責任の不在と同一視しない。",
        "question_ids": qids,
        "material_ids": [m["material_id"] for m in materials],
        "status": "active",
    }

    fragments = [
        {
            "fragment_id": fids[0],
            "created_at": DATE,
            "language": "ja",
            "form": "letter",
            "title": "訂正の宛先——ERR-011 へ",
            "text": "ERR-011 へ。\n\nあなたは、空いていた席が埋まったと書いた。埋めた断片の名も書いた。今日、その席は空いている。名指された断片は、別の名札を持っている。\n\nどちらが誤りかは、ここでは決めない。決められない。理由は三つある。欄が書き換えられた可能性、番号が振り直された可能性、記録が最初から誤っていた可能性。三つは、この台帳のどこにも区別して書かれていない。\n\n宛先の欄がないので、本文で宛先を書く。返事は要らない。返事の欄もない。\n\n訂正の宛先は、訂正の外にある。",
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [qids[3], qids[0]],
            "motif_ids": [MOTIF_ID, "MOTIF-016"],
            "material_ids": [trace["material_id"], mid("罪と罰")],
            "session_id": SESSION_ID,
            "status": "draft",
            "editor_note": "ERR-011 を宛先として名指した工作物。一人称代名詞を一つも置かずに書簡の声を作れるかを試す（無主語の数を動かす工作物でもある）。宛先を本文で書くしかない形式は、errata に宛先欄がないことへの応答。",
            "prompt_template": "prompts/close_reading_report.md",
        },
        {
            "fragment_id": fids[1],
            "created_at": DATE,
            "language": "ja",
            "form": "other",
            "title": "修復の書式",
            "text": "修復の書式\n\n　違反の種類：＿＿（怠慢／不能／欺瞞）\n　害を受けた相手：＿＿\n　受けた害：＿＿\n　弁済：＿＿\n　謝罪：＿＿\n　黙殺：＿＿\n　履行の確認者：＿＿\n　確認の日：＿＿\n　現存する旧文：＿＿\n\n註。この書式は空のまま保存する。欄を埋める者が現れるまで、修復は完了しない。空であることは、違反の否認ではない。",
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [qids[0], qids[1]],
            "motif_ids": [MOTIF_ID, "MOTIF-016"],
            "material_ids": [trace["material_id"], mid("ニコマコス倫理学"), mid("法の哲学")],
            "session_id": SESSION_ID,
            "status": "draft",
            "editor_note": "errata にない欄（相手・害・弁済・謝罪・黙殺・確認者）を並べた空の書式。欄を足すことと、欄を埋めることを分けるための工作物。",
            "prompt_template": "prompts/close_reading_report.md",
        },
    ]

    relations: list[dict] = []
    group_notes = [
        "第1群（償いの哲学）の素材。損害の測定・観客・帰責・赦しを分ける。",
        "第2群（告白と形式）の素材。告白・手続き・償いの連鎖・形式化した謝罪を読む。",
        "第3群（嘘の修復）の素材。正さないことが修復になる場合を読む。",
    ]
    for index, record in enumerate(materials):
        if record["kind"] == "project_trace":
            note = "台帳検証。訂正録16件の宛先0・償いの語は「書き換えない」3件・ERR-011 の不成立。"
        elif index < 4:
            note = group_notes[0]
        elif index < 8:
            note = group_notes[1]
        elif index < 9:
            note = group_notes[2]
        else:
            note = "第4群（機械の責任）の研究抜粋。責任の空白・シワ寄せ・異議申立てを、謝罪と同一視しない。"
        relations.append(rel("material", record["material_id"], "motif", MOTIF_ID, note))

    for qid in qids:
        relations.append(rel("question", qid, "motif", MOTIF_ID, "本セッションで開いた問い。"))
    for fragment in fragments:
        relations.append(rel("fragment", fragment["fragment_id"], "motif", MOTIF_ID,
                             "修復の宛先を試す工作物。意図的に欄と宛先を置いた。"))
    relations.append(rel("fragment", fids[0], "question", qids[3],
                         "記録の外で消えた修復に、宛先を本文で与える試み。"))
    relations.append(rel("fragment", fids[1], "question", qids[1],
                         "訂正を閉じる条件を、空の欄として置く試み。"))

    pairs = [
        (mid("ニコマコス倫理学"), mid("法の哲学"), "contrast",
         "損害の量を測って戻す正義と、認識できる範囲に責任を限る帰責。測る対象と責任の範囲が違う。", ),
        (mid("アダム・スミス"), mid("罪と罰"), "echo",
         "謝罪に観客を要する議論と、告白に聞く者を要する物語。第三者の位置が、謝罪を成立させる。"),
        (mid("赦すこと"), mid("芝浜"), "contrast",
         "償いと引き換えの赦しは赦しではないという議論と、嘘によって生活を修復する落語。赦しの外の修復がある。"),
        (mid("審判"), trace["material_id"], "echo",
         "罪状の分からない手続きと、原因の分からない記録の不一致。どちらも手続きだけが進む。"),
        (mid("それから"), trace["material_id"], "transforms",
         "償いが新しい害を生む小説と、訂正が訂正の対象を変える ERR-015。"),
        (mid("人間失格"), mid("アダム・スミス"), "contrast",
         "形式化した謝罪と、観客の同感を必要とする謝罪。形式だけでは同感が成立しない。"),
        (mid("責任の空白"), mid("道徳的シワ寄せ"), "echo",
         "予測不能性による責任の空白と、責任がその場の人間に寄る構造。空白は誰も負わず、シワは人間が負う。"),
        (mid("アルゴリズム的説明責任"), mid("赦すこと"), "leaves_open",
         "異議申立ての経路を設計する議論と、計算の圏外にある赦し。手続きで届く範囲と届かない範囲。"),
        (mid("罪と罰"), mid("責任の空白"), "interrupts",
         "罰を受け入れることで完成する告白と、責任を帰せないという技術倫理の診断。主体の有無が逆である。"),
        (mid("芝浜"), mid("それから"), "metaphorically_resonates",
         "正さないことで修復する話と、償うことで壊す話。訂正の向きが逆である。"),
    ]
    for left, right, kind, note in pairs:
        relations.append(rel("material", left, "material", right, note, kind))

    relations.append(rel("motif", MOTIF_ID, "motif", "MOTIF-016",
                         "訂正と抹消の糸に、宛先と償いの軸を渡す。", "echo"))
    relations.append(rel("motif", MOTIF_ID, "motif", "MOTIF-021",
                         "約束の履行と、訂正の履行を並べる。どちらも履行欄を持たない。", "echo"))
    relations.append(rel("session", SESSION_ID, "motif", MOTIF_ID, "本セッションの主題。"))

    session = {
        "session_id": SESSION_ID,
        "started_at": DATE,
        "human_direction": "「続けて、AIさんの自由に、行動してください」という包括的な委任。前セッション（SESSION-040）で残した次回案の第一項「errata.jsonl の全件を、破約の三種類（怠慢・不能・欺瞞）で分類する」と、開いた問い Q-20261024-962620（破約を訂正で償えるか）を引き取ることを自由に選んだ。",
        "question_ids": ["Q-044", "Q-050", "Q-084", "Q-086", "Q-20261024-962620", "Q-20261024-a1bb7b"] + qids,
        "context_material_ids": [m["material_id"] for m in materials],
        "produced_fragment_ids": fids,
        "new_question_ids": qids,
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": "訂正の宛先と修復を主題とした資料追加と精読のセッション。選定前に tools/repair_audit.py を新設し、既存の errata 16件を読んだ。内訳は本文を対象とするもの8件・計器と痕跡6件・訂正録2件、判定と状態は contradicted/annotated 4・contradicted/open 6・holds/annotated 3・unmeasurable/open 3。corrected_by が埋まっているのは2件だけで14件は空、訂正の訂正は2本（ERR-012→ERR-015、ERR-013→ERR-016）でいずれも末端が open。errata のスキーマに宛先・被害者の欄はなく、宛先・謝罪・弁償・赦しの語を含む記録は0件、償いの語を含む3件はいずれも「書き換えない」という保存の宣言のなかにあった。再実行では ERR-002 が 6→7、ERR-012 が 5→10、ERR-013 が 89→100 と動き、ERR-011 が「human_narrator=1（未使用 0 種）」と記録した空席は現在 human_narrator=0（未使用 1 種）で、名指された FRAG-032 の現在の narrator_mode は reflective_literary_voice である（MAT-TRC-20261024-repair）。この不在から、償いの哲学4件（アリストテレス、スミス、ヘーゲル、デリダ）、告白と形式4件（ドストエフスキー、カフカ、漱石、太宰）、嘘の修復1件（芝浜）の文学・思想9件、機械の責任3件（Matthias、Elish、Diakopoulos）、痕跡1件の計13件を追加し、全件を readings/2026-10-24-session-041-repair-and-addressee.md で一節／解釈／考え／感じたことの四層に分けて精読した。横断報告では「どう解釈したか／その解釈をどう考えたか／結果としてどう感じたと記述できるか」を独立させ、「感じた」を意識や身体経験の主張にしない留保を置いた。モチーフ1件、問い5件、関係36件、工作物2編（draft）を追加。あわせて tools/errata_audit.py を和集合対応にし（--base-only を追加）、訂正を測る道具がシャードを見落としていた点を修復した。この変更で ERR-012 の再測定値は 5 から 10 に、ERR-013 は 99 から 100 に変わる。工作物2編はいずれも一人称代名詞を持たず、無主語の数と引用の総数を動かす工作物である。",
    }

    payloads = {
        "materials": materials,
        "motifs": [motif],
        "questions": questions,
        "fragments": fragments,
        "relations": relations,
        "sessions": [session],
    }
    written = {}
    for collection, rows in payloads.items():
        path = shard(collection)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        written[collection] = path

    print("session:", SESSION_ID)
    print("motif:", MOTIF_ID)
    print("questions:", ", ".join(qids))
    print("fragments:", ", ".join(fids))
    print("materials:", len(materials), "/ relations:", len(relations))
    for collection, path in written.items():
        print("wrote", path.relative_to(ROOT), len(payloads[collection]))
    for m in materials:
        print(m["material_id"], "|", m["title"][:60])


if __name__ == "__main__":
    main()
