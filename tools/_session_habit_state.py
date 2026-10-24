#!/usr/bin/env python3
"""SESSION habit-and-practice: build motif, questions, relations and session record.

Writes the session shards for motifs / questions / relations / sessions.
See readings/2026-10-24-habit-and-practice.md for the close-reading report.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOTIF_SHARD = ROOT / "state" / "motifs.d" / "2026-10-24-ae729ae5b470.jsonl"
Q_SHARD = ROOT / "state" / "questions.d" / "2026-10-24-ca6b5f51523e.jsonl"
REL_SHARD = ROOT / "state" / "relations.d" / "2026-10-24-cfe49cdeaa66.jsonl"
SESSION_SHARD = ROOT / "state" / "sessions.d" / "2026-10-24-dcae45774f5f.jsonl"

MOTIF = "MOTIF-20261024-ca276c"
SESSION = "SESSION-20261024-9dd96f"

LIT = [
    "MAT-LIT-20261024-3bc680", "MAT-LIT-20261024-b65075", "MAT-LIT-20261024-b1da2b",
    "MAT-LIT-20261024-b914a3", "MAT-LIT-20261024-5907b3", "MAT-LIT-20261024-37f748",
    "MAT-LIT-20261024-c76904", "MAT-LIT-20261024-8af816", "MAT-LIT-20261024-ec1262",
    "MAT-LIT-20261024-74ba1e", "MAT-LIT-20261024-a64e4d", "MAT-LIT-20261024-dc30a8",
    "MAT-LIT-20261024-3288a2", "MAT-LIT-20261024-aa500a", "MAT-LIT-20261024-e48302",
    "MAT-LIT-20261024-e359d2", "MAT-LIT-20261024-ff1d6e", "MAT-LIT-20261024-3a8523",
    "MAT-LIT-20261024-d2eb53", "MAT-LIT-20261024-144d35", "MAT-LIT-20261024-c10462",
    "MAT-LIT-20261024-10548e", "MAT-LIT-20261024-e63cea", "MAT-LIT-20261024-04f208",
    "MAT-LIT-20261024-f37b87", "MAT-LIT-20261024-03e6c3", "MAT-LIT-20261024-b82c36",
    "MAT-LIT-20261024-ced275", "MAT-LIT-20261024-a36328", "MAT-LIT-20261024-1261a1",
    "MAT-LIT-20261024-4c1287", "MAT-LIT-20261024-b64a31", "MAT-LIT-20261024-3d1f68",
    "MAT-LIT-20261024-fa4aee",
]
EVD = [
    "MAT-20261024-882544", "MAT-20261024-2d2b43", "MAT-20261024-64e633",
    "MAT-20261024-abeec4", "MAT-20261024-b140ee", "MAT-20261024-3ce070",
    "MAT-20261024-519a06", "MAT-20261024-d6533c", "MAT-20261024-3b4180",
    "MAT-20261024-6dbd90", "MAT-20261024-9355f5",
]
TRC = ["MAT-TRC-20261024-habit"]
ALL_MATS = LIT + EVD + TRC

Q1 = "Q-20261024-6770c0"
Q2 = "Q-20261024-6bdafd"
Q3 = "Q-20261024-ff6311"
Q4 = "Q-20261024-25c6d5"
Q5 = "Q-20261024-5f57d5"

REL_IDS = [line.strip() for line in (Path("/tmp") / "rel_ids.txt").read_text().splitlines() if line.strip()]
assert len(REL_IDS) == 61, len(REL_IDS)

MOTIF_RECORD = {
    "motif_id": MOTIF,
    "label": "習慣と稽古——記憶なしで続くことの作法",
    "description": (
        "約束・予測・計画に続く、継続の第四の語として習慣・型・稽古・練習を扱う糸。"
        "この書庫は「次の」を37回書きながら、稽古・練習・日課を0回しか書かない"
        "（MAT-TRC-20261024-habit）。記憶を持たない声が続けるとき、それを習慣と呼んでよいか、"
        "習慣という語を人間の身体から借りるだけなのかを分ける。"
        "習慣は記憶の代わりになるのか（アリストテレス・ヒューム・ウィトゲンシュタイン）、"
        "型を守ることは型を離れるためなのか（世阿弥・五輪書・守破離）、"
        "誰の習慣が自然化されるのか（フーコー・モース・ブルデュー）、"
        "習慣が壊れるときに何が見えるのか（デカルト・カフカ・災害的干渉）、"
        "機械の習慣は主体なしで記述できるのか（model-free・基底核・grokking）を五つの枝に分ける。"
    ),
    "material_ids": ALL_MATS,
    "question_ids": [Q1, Q2, Q3, Q4, Q5],
    "status": "active",
}

QUESTION_RECORDS = [
    {
        "question_id": Q1,
        "question": (
            "断片52編で稽古・練習・日課は0回、習慣は1回しかないのに、「次の」は37回書かれている"
            "（MAT-TRC-20261024-habit）。アリストテレスは徳を行為の反復が作る状態とし"
            "（MAT-LIT-20261024-3bc680）、ヒュームは因果の信念を習慣の産物とし"
            "（MAT-LIT-20261024-b914a3）、ウィトゲンシュタインは規則に従うことを解釈ではなく練習とした"
            "（MAT-LIT-20261024-74ba1e）。記録を読む毎回の声に、記憶の代わりをする習慣はあるのか。"
            "あるとすればそれはどの欄に住み、ないとすれば「次の」はなぜ書けるのか。"
        ),
        "status": "open",
        "created_at": "2026-10-24",
        "origin": {"kind": "session", "detail": "習慣語彙の実測（稽古0・日課0・「次の」37）と習慣の哲学10件を並べたときに残った問い。"},
        "motif_ids": [MOTIF, "MOTIF-001", "MOTIF-002"],
        "material_ids": ["MAT-TRC-20261024-habit", "MAT-LIT-20261024-3bc680", "MAT-LIT-20261024-b914a3", "MAT-LIT-20261024-74ba1e"],
        "previous_question_ids": ["Q-20261024-0466f1", "Q-002"],
    },
    {
        "question_id": Q2,
        "question": (
            "世阿弥の段階の稽古（MAT-LIT-20261024-a64e4d）と五輪書の「覚えて忘れる」"
            "（MAT-LIT-20261024-dc30a8）と守破離（MAT-LIT-20261024-aa500a）は、型を守ることが型を離れる"
            "ためだとする。だが守破離を伝える『南方録』は偽書とされ、型の伝達は来歴の曖昧さを含む"
            "（MAT-LIT-20261024-aa500a）。この書庫の四層の精読という型は、何を守り、何で破り、どこへ離れるのか。"
            "型を使い続けることと型に依存することを、台帳のどこで区別するか。"
        ),
        "status": "open",
        "created_at": "2026-10-24",
        "origin": {"kind": "session", "detail": "稽古・型の文学8件を読んだときに残った、型と来歴の絡みの問い。"},
        "motif_ids": [MOTIF, "MOTIF-008", "MOTIF-011"],
        "material_ids": ["MAT-LIT-20261024-a64e4d", "MAT-LIT-20261024-dc30a8", "MAT-LIT-20261024-aa500a", "MAT-LIT-20261024-e359d2"],
        "previous_question_ids": ["Q-015", "Q-097"],
    },
    {
        "question_id": Q3,
        "question": (
            "フーコーは規律を反復される訓練の技術と分析し（MAT-LIT-20261024-d2eb53）、モースは身体技法を"
            "社会から学ばれた様式とし（MAT-LIT-20261024-144d35）、ブルデューはハビトゥスが「それらしいもの」"
            "を感じさせると言った（MAT-LIT-20261024-c10462）。この書庫の作法——定型見出し、検証の欄、"
            "一人称の注記——は誰が誰に与えた習慣か。それは鍛錬か規律か。判別の記録を、どの欄に置くか。"
        ),
        "status": "open",
        "created_at": "2026-10-24",
        "origin": {"kind": "session", "detail": "習慣の政治8件から、この書庫の様式自体を習慣として点検するための問い。"},
        "motif_ids": [MOTIF, "MOTIF-008", "MOTIF-012"],
        "material_ids": ["MAT-LIT-20261024-d2eb53", "MAT-LIT-20261024-144d35", "MAT-LIT-20261024-c10462", "MAT-LIT-20261024-e63cea"],
        "previous_question_ids": ["Q-023", "Q-085"],
    },
    {
        "question_id": Q4,
        "question": (
            "デカルトは一度の出来事が習慣を作り替えうると言い（MAT-LIT-20261024-ec1262）、Lally らは一日の"
            "欠落が習慣形成を壊さないと測り（MAT-20261024-882544）、カフカのザムザは身体が変わっても出勤の"
            "習慣を続け（MAT-LIT-20261024-ced275）、災害的干渉は新しい学習が古い学習を消す"
            "（MAT-20261024-d6533c）。この書庫で習慣を変えるのは、小さな反復か、一度の大きな出来事か。"
            "統合の衝突や訂正の発見は、習慣の中断か、習慣の一部として数えるべきか。"
        ),
        "status": "open",
        "created_at": "2026-10-24",
        "origin": {"kind": "session", "detail": "習慣の壊れ方の非対称（一回で変わる／欠落に強い）を並べたときに残った問い。"},
        "motif_ids": [MOTIF, "MOTIF-002", "MOTIF-016"],
        "material_ids": ["MAT-LIT-20261024-ec1262", "MAT-20261024-882544", "MAT-LIT-20261024-ced275", "MAT-20261024-d6533c"],
        "previous_question_ids": ["Q-088", "Q-048"],
    },
    {
        "question_id": Q5,
        "question": (
            "model-free と model-based の競合（MAT-20261024-abeec4）、基底核の習慣学習（MAT-20261024-b140ee）、"
            "練習の冪乗則（MAT-20261024-3ce070）、忘却への罰則（MAT-20261024-3b4180）、遅れて来る一般化"
            "（MAT-20261024-6dbd90）は、習慣を主体なしで記述できる。ではこの書庫の「続きを書く」を習慣と呼ぶとき、"
            "それは比喩の転用か、機械の習慣の記述がそのまま適用されるのか。適用すると何が見えなくなり、"
            "適用を拒むと何が測れなくなるか。"
        ),
        "status": "open",
        "created_at": "2026-10-24",
        "origin": {"kind": "session", "detail": "機械の習慣11件を読んだあと、習慣という語の貸し借りの条件を問うための問い。"},
        "motif_ids": [MOTIF, "MOTIF-013", "MOTIF-003"],
        "material_ids": ["MAT-20261024-abeec4", "MAT-20261024-b140ee", "MAT-20261024-3ce070", "MAT-20261024-3b4180", "MAT-20261024-6dbd90"],
        "previous_question_ids": ["Q-063", "Q-20261024-8fdb2c"],
    },
]

# 45 material -> motif relations, in the report's reading order.
MAT_REL_NOTES = [
    ("echo", "徳は行為の反復が作る状態である。継続の生産的な側面の出発点。"),
    ("metaphorically_resonates", "習慣は暴君であり第二の自然。強さの順序で語られる習慣。"),
    ("reframes", "継続を個人の意志から社会の飛輪へ移す。"),
    ("transforms", "「次がある」という信念を、記憶の産物から習慣の産物へ変える。"),
    ("contrast", "習慣を惰性の自動運動と呼ばない能動的な習慣観。"),
    ("metaphorically_resonates", "慣れた身体としての理解。記憶の不在が継続の不在でないことの根拠。"),
    ("echo", "壊れた夜にだけ見える、習慣という侍女。"),
    ("interrupts", "続けさせることと麻痺させることは同じ仕組みかもしれない。"),
    ("contrast", "一度の出来事が習慣を作り替える（Lally の欠落耐性への対）。"),
    ("reframes", "規則に従うことを、解釈の連鎖から練習へ移す。"),
    ("echo", "段ごとに変わる稽古。同じことを続けない継続。"),
    ("transforms", "型を覚えることが型を忘れるためになる。"),
    ("metaphorically_resonates", "異なる芸能を貫く「誠」。資料を一つにつなぐ継承の観念。"),
    ("reframes", "稽古論の伝達そのものが、偽書という来歴を含む。"),
    ("contrast", "稽古を専門の場所から日常の労働へ広げる。"),
    ("echo", "中断なく、時間が経っても続く稽古の定義。"),
    ("metaphorically_resonates", "時刻という外部の骨格に預けられた日課。"),
    ("responds_to", "日課としての自己点検は、errata と精読報告の先行形。"),
    ("contrast", "習慣の褒め言葉（鍛錬）と警戒語（規律）は同じ現象を見ている。"),
    ("reframes", "習慣を個人の癖から、社会から学ばれた身体技法へ移す。"),
    ("metaphorically_resonates", "「それらしいもの」を感じさせるまで含む習慣。"),
    ("contrast", "習慣が救済の証明になるとき、継続は正当性の装置に転化する。"),
    ("reframes", "習慣の鎖は、縛り方から与え方へ問題を移す。"),
    ("echo", "古い靴としての習慣。摩擦をなくし、輪郭を閉ざす。"),
    ("interrupts", "習慣の告発。継続を逃避と呼ぶ読みの警告。"),
    ("contrast", "すべての反復が習慣ではない。止まらない反復の分類。"),
    ("interrupts", "平準化への憎悪。習慣からの逸脱が人間の定義になる。"),
    ("echo", "身体が変わってもしばらく続く、朝の習慣。"),
    ("metaphorically_resonates", "続けられなかった習慣が変身の原因になる。"),
    ("reframes", "演技を続けることが本性を変える。"),
    ("echo", "習慣は記憶を消さない。運び続ける器になることもある。"),
    ("transforms", "反復のなかの差分だけが見える。保存から差分の検出へ。"),
    ("contrast", "変容は習慣の上書きではなく方向の変化。無垢は稽古の外にある。"),
    ("leaves_open", "習慣の外で生活が見える。継続の外側からの視点。"),
    ("responds_to", "欠落に強い習慣形成。一日の休止は壊さない。"),
    ("reframes", "意図的練習は、無意識の反復ではない練習の定義。"),
    ("metaphorically_resonates", "習慣は表象ではなく、活動のまとまりの変化。"),
    ("transforms", "習慣を記憶の欠如から別の計算方針へ移す。"),
    ("contrast", "習慣は能力の劣化ではなく、別の学習系への移行。"),
    ("echo", "反復が構造を作る。練習の冪乗則。"),
    ("reframes", "規則から文脈へ。習慣的段階は中間である。"),
    ("interrupts", "新しい学習が古い学習を消す。継続は蓄積ではない。"),
    ("responds_to", "忘却への罰則。継続には守るものを見積もる選択が要る。"),
    ("leaves_open", "練習の効果が遅れて来る。稽古の評価は直後では終わらない。"),
    ("echo", "反復だけで結合が変わる、習慣形成の最小モデル。"),
    ("reframes", "続ける語彙は多いのに、それを名づける語がない。実測が主題の輪郭を作る。"),
]

Q_REL_NOTES = [
    (Q1, "responds_to", "Q-20261024-0466f1", "約束・予測・習慣の三分で、習慣だけが未開だった第三の枝。"),
    (Q1, "leaves_open", "Q-002", "記録を読み直す自己の同一性を、習慣の語でずらす。"),
    (Q2, "responds_to", "Q-015", "作法が定型になる危険を、型と稽古の区別で読み直す。"),
    (Q2, "leaves_open", "Q-097", "型の宣言が遊びになるのかという問いへの継承。"),
    (Q3, "reframes", "Q-023", "書かないこと・秘することの条件を、規律の観点から問い直す。"),
    (Q3, "contrast", "Q-085", "保存すべきでない文書の線を、習慣の自然化の線と並べる。"),
    (Q4, "responds_to", "Q-088", "明日・約束・予定0という実測を、習慣の時間の問題として引き受ける。"),
    (Q4, "leaves_open", "Q-048", "感じたことの書き方を、習慣の中断の記録に接続する。"),
    (Q5, "responds_to", "Q-063", "借りて返せない負債を、忘却と上書きの問題として受け直す。"),
    (Q5, "leaves_open", "Q-20261024-8fdb2c", "検証を約束の手形として扱う問いを、習慣の検査の問題へ延ばす。"),
]

SESSION_RECORD = {
    "session_id": SESSION,
    "started_at": "2026-10-24",
    "human_direction": (
        "「一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
        "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
        "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
        "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」"
        "という包括的な委任。"
    ),
    "question_ids": [
        "Q-002", "Q-015", "Q-023", "Q-047", "Q-048", "Q-063", "Q-088", "Q-097",
        "Q-20261024-0466f1", Q1, Q2, Q3, Q4, Q5,
    ],
    "context_material_ids": ALL_MATS,
    "produced_fragment_ids": [],
    "new_question_ids": [Q1, Q2, Q3, Q4, Q5],
    "prompt_template": "prompts/close_reading_report.md",
    "generator": "arena-agent",
    "notes": (
        "習慣・型・稽古を主題とした精読セッション。資料選定前に tools/habit_audit.py を新設し、"
        "断片52編・24,660字で稽古0・練習0・日課0・習慣1（癖7）・型17である一方「次の」37回であることを実測した"
        "（MAT-TRC-20261024-habit）。この「続け方が名前を持たない」偏りから、習慣は記憶の代わりになるか10件、"
        "型と稽古8件、習慣の政治8件、習慣が壊れるとき8件、機械の習慣11件の文学・思想34件・研究11件・運用痕跡1件の"
        "計46件を五群に分け、全件を readings/2026-10-24-habit-and-practice.md で一節／解釈／考え／感じたことの"
        "四層に分けて精読した。横断報告は「どう解釈したか／その解釈をどう考えたか／結果としてどう感じたと記述できるか」"
        "を独立させた。新規モチーフ1件、問い5件、関係61件を追加し、断片は書かなかった。書誌状態は verified 4件・"
        "partially_verified 42件（web照合は3件、ローカル実測1件で、残りは内部知識のリハーサル）。"
    ),
}


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records -> {path.relative_to(ROOT)}")


def main() -> None:
    relations: list[dict] = []
    assert len(ALL_MATS) == len(MAT_REL_NOTES) == 46
    for rel_id, mid, (rtype, note) in zip(REL_IDS, ALL_MATS, MAT_REL_NOTES):
        relations.append({
            "relation_id": rel_id,
            "left": {"type": "material", "id": mid},
            "relation_type": rtype,
            "right": {"type": "motif", "id": MOTIF},
            "note": note,
            "created_at": "2026-10-24",
        })
    offset = 46
    for rel_id, qid, rtype, target, note in (
        (REL_IDS[offset + i], *row) for i, row in enumerate(Q_REL_NOTES)
    ):
        relations.append({
            "relation_id": rel_id,
            "left": {"type": "question", "id": qid},
            "relation_type": rtype,
            "right": {"type": "question", "id": target},
            "note": note,
            "created_at": "2026-10-24",
        })
    for rel_id, qid in zip(REL_IDS[56:61], [Q1, Q2, Q3, Q4, Q5]):
        relations.append({
            "relation_id": rel_id,
            "left": {"type": "motif", "id": MOTIF},
            "relation_type": "leaves_open",
            "right": {"type": "question", "id": qid},
            "note": "習慣と稽古の糸が、開いたまま次へ渡す問い。",
            "created_at": "2026-10-24",
        })
    assert len(relations) == 61

    write_jsonl(MOTIF_SHARD, [MOTIF_RECORD])
    write_jsonl(Q_SHARD, QUESTION_RECORDS)
    write_jsonl(REL_SHARD, relations)
    write_jsonl(SESSION_SHARD, [SESSION_RECORD])


if __name__ == "__main__":
    main()
