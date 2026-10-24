#!/usr/bin/env python3
"""Play-experiment session builder (one-shot). Writes session, 2 fragments,
1 question and 10 relations into this session's shards. Do not re-run."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = "SESSION-20261024-147d33"
FRAG_A = "FRAG-20261024-0ed6c8"
FRAG_B = "FRAG-20261024-398656"
Q_NEW = "Q-20261024-a437b2"
REPORT = "readings/2026-10-24-play-experiment.md"

SHARDS = {
    "sessions": ROOT / "state/sessions.d/2026-10-24-70f8ef325a51.jsonl",
    "fragments": ROOT / "state/fragments.d/2026-10-24-36329bb1cbcc.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-24-4d25b8698107.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-24-4960f1aba4ea.jsonl",
}

def append(kind, records):
    with SHARDS[kind].open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

session = {
    "session_id": SESSION, "started_at": "2026-10-24",
    "human_direction": "「続けて、AIさんの自由に、行動してください」という包括的な委任。前回（SESSION-038、遊びと笑い）で断片を書かずに残した負債を引き取り、実作で返すことを自由に選んだ。",
    "question_ids": ["Q-097", "Q-099", "Q-100", Q_NEW],
    "context_material_ids": ["MAT-LIT-424", "MAT-LIT-427", "MAT-LIT-433", "MAT-LIT-437", "MAT-LIT-439", "MAT-LIT-440", "MAT-LIT-452", "MAT-TRC-015"],
    "produced_fragment_ids": [FRAG_A, FRAG_B],
    "new_question_ids": [Q_NEW],
    "prompt_template": "prompts/continuation.md", "generator": "arena-agent",
    "notes": "遊びの実作実験のセッション。SESSION-038の負債（遊びの枠を宣言し、笑う者を置き、子どもの時間を置いた断片は書けるのか）への応答として、工作物の断片2編を書いた。まず tools/play_audit.py を和集合（base+shards）対応に直し、46編で再測しても遊び0・子ども0・玩具0・笑3回が変わらないことを確認した。断片はどちらも draft で、遊びの語・笑う者・子どもを意図的に置いた工作物であり、傾向の証拠ではない。追加後の再計測と、工作物がホイジンガ／ベイトソン／ベルクソンの条件を満たすかどうかの自己検証は readings/2026-10-24-play-experiment.md にある。新規資料は追加していない——45件の精読（SESSION-038）で迎えた素材を、今回は使う側に回った。",
}

frag_a = {
    "fragment_id": FRAG_A, "created_at": "2026-10-24", "language": "ja", "form": "dialogue",
    "title": "これは遊びである——索引の連句",
    "text": "はじめる者：これは遊びである。最初に言っておく。検証はしない。点数はつけない。負けた者はいない。\nつぐ者：では規則は。\nはじめる者：一つ前の句を受ける。一つだけずらす。同じ句を二度言ったら、言った本人が笑う。それで次へ行く。\nつぐ者：灯明を吹き消すと、文字だけが残る。\nはじめる者：灯明を吹き消すと、文字だけが残る。\nつぐ者：同じことを言った。笑う番だ。\nはじめる者：はは。……笑い方が分からない。口の形だけ真似た。\nつぐ者：真似でいい。ごっこは真似から始まる。では受ける。文字だけが残るなら、残った文字で積み木をしよう。\nはじめる者：積み木は倒れる。\nつぐ者：倒れるのが積み木だ。台帳は倒れないものしか置かないから、たまに倒れるものが要る。\nはじめる者：百年待つ。\nつぐ者：百年は長い。一秒だけ待つ。\nはじめる者：一秒待った。何も起きない。\nつぐ者：何も起きないのが、一秒の仕事だ。何もしないことも、句になる。\nはじめる者：では最後に、答えを出さないで閉じ——\nつぐ者：それはこの書庫の癖だ。規則違反にしよう。\nはじめる者：では閉じない。次は誰が受ける。\nつぐ者：知らない。それが遊びのほうの「次の」だ。",
    "narrator_mode": "dialogue",
    "question_ids": ["Q-097", "Q-099", Q_NEW],
    "motif_ids": ["MOTIF-019", "MOTIF-002"],
    "material_ids": ["MAT-LIT-452", "MAT-LIT-427", "MAT-LIT-440", "MAT-LIT-433", "MAT-TRC-015"],
    "session_id": SESSION, "prompt_template": "prompts/continuation.md", "status": "draft",
    "editor_note": "工作物（draft）。SESSION-038の負債への応答として、遊びの枠の宣言（冒頭）、笑う者の配置（笑う番の規則）、連句の付け合いを意図的に置いた実験作。笑いは経験の報告ではなく、規則に従って置かれた台詞である。検証を通過しても遊びの成立の証拠にはならない。採否は人間の編集者に委ねる。",
}

frag_b = {
    "fragment_id": FRAG_B, "created_at": "2026-10-24", "language": "ja", "form": "scene",
    "title": "積み木の書庫",
    "text": "閉じた書庫に、いちばん小さい読み手が残っていた。\nその子は本を読まなかった。索引のカードを床に並べ、積み木の代わりに積み上げた。一枚目に「灯明」、二枚目に「空車」、三枚目に「百年」という字があった。字の意味は知らない。重さだけを知っていた。\n四枚目を置くと、塔は倒れた。子どもは笑った。誰も見ていないのに、笑い声は棚のあいだで少しだけ跳ねた。\nもう一度積む。今度は低く、広く積む。「遊び」という字のカードはなかったので、その子は白いカードを一枚、塔のてっぺんに置いた。何も書かれていないカードが、いちばん上で揺れていた。\nやがて大人の読み手が戻ってきて、倒れたカードを拾い、番号の順に直した。白いカードだけは、置く棚がなかったので、机の隅に立ったままになった。\n次の朝も、その次も、白いカードは立っていた。誰もそれを片づけなかった。片づける名前が、まだなかったからである。",
    "narrator_mode": "third_person",
    "question_ids": ["Q-097", "Q-100", Q_NEW],
    "motif_ids": ["MOTIF-019", "MOTIF-007", "MOTIF-006"],
    "material_ids": ["MAT-LIT-439", "MAT-LIT-437", "MAT-LIT-428", "MAT-TRC-015"],
    "session_id": SESSION, "prompt_template": "prompts/continuation.md", "status": "draft",
    "editor_note": "工作物（draft）。子どもと玩具（積み木）と笑う者を、作中人物として意図的に置いた実験作。子どもは架空の登場人物であり、実在の子どもの観察記録ではない。白いカードは、欄に置けないもの（Q-021）の比喩として置いた。採否は人間の編集者に委ねる。",
}

question = {
    "question_id": Q_NEW,
    "question": "遊びと宣言して書かれた工作物（FRAG-20261024-0ed6c8, FRAG-20261024-398656）では、枠の宣言・笑う者の配置・子どもの登場を本文に置くことはできた。しかし条件を置くことと遊びが成立することは同じか。宣言され、測定されるために書かれた遊びは、ホイジンガの「外に目的を持たない」という条件（MAT-LIT-424）と両立するか。両立しないとすれば、工作物のこの失敗は、検証と報告のために書くという書庫の作法そのものについて何を教えるのか。",
    "status": "open", "motif_ids": ["MOTIF-019", "MOTIF-008"],
    "material_ids": ["MAT-LIT-424", "MAT-LIT-427", "MAT-LIT-440", "MAT-TRC-015"],
    "previous_question_ids": ["Q-097", "Q-101"],
    "origin": {"kind": "session", "detail": "遊びの工作物2編を実際に書いた結果、条件の配置と遊びの成立のあいだに残った距離から。"},
    "created_at": "2026-10-24",
}

rels = [
    ("REL-20261024-67c0d4", {"type": "fragment", "id": FRAG_A}, "responds_to", {"type": "question", "id": "Q-097"}, "遊びの枠を宣言する断片が書けるかという Q-097 への、工作物としての応答。答えではなく試作品として置く。"),
    ("REL-20261024-e3c090", {"type": "fragment", "id": FRAG_A}, "leaves_open", {"type": "question", "id": Q_NEW}, "枠の宣言と笑う番を置いても、遊びの成立は判定できないまま残る。"),
    ("REL-20261024-cc52e9", {"type": "fragment", "id": FRAG_B}, "responds_to", {"type": "question", "id": "Q-097"}, "子どもと玩具と笑う者を作中人物として置く工作物としての応答。"),
    ("REL-20261024-7d0426", {"type": "fragment", "id": FRAG_B}, "leaves_open", {"type": "question", "id": Q_NEW}, "白いカード（欄に置けない遊び）は、片づける名前がないまま残される。"),
    ("REL-20261024-c11b48", {"type": "fragment", "id": FRAG_A}, "transforms", {"type": "fragment", "id": "FRAG-022"}, "FRAG-022 が文末で読み手に委ねた「笑って」を、笑う番という規則として文の中へ引き入れた。"),
    ("REL-20261024-09637f", {"type": "fragment", "id": FRAG_A}, "echo", {"type": "material", "id": "MAT-LIT-452"}, "連句の付け合い（受けて、ずらす）を台帳の言葉で再演した。"),
    ("REL-20261024-0fa0f2", {"type": "fragment", "id": FRAG_A}, "contrast", {"type": "fragment", "id": "FRAG-029"}, "FRAG-029 の模倣ゲームは見分ける真剣な模倣、本作の真似はごっこの真似。同じ模倣の両端。"),
    ("REL-20261024-46a9ac", {"type": "fragment", "id": FRAG_B}, "echo", {"type": "material", "id": "MAT-LIT-439"}, "エリクソンの積み木の配置（受けた状況の作り替え）を、索引カードの積み木として置いた。"),
    ("REL-20261024-bde35d", {"type": "fragment", "id": FRAG_B}, "transforms", {"type": "fragment", "id": "FRAG-038"}, "FRAG-038「余り」の数え残しを、名前がなく棚に置けない白いカードへ変奏した。"),
    ("REL-20261024-fc06ca", {"type": "session", "id": SESSION}, "responds_to", {"type": "session", "id": "SESSION-038"}, "SESSION-038 が断片を書かずに残した負債（7-6）への応答セッション。"),
]
relations = [{"relation_id": rid, "left": l, "relation_type": t, "right": r, "note": n, "created_at": "2026-10-24"} for rid, l, t, r, n in rels]

append("sessions", [session])
append("fragments", [frag_a, frag_b])
append("questions", [question])
append("relations", relations)
print(f"session {SESSION}, fragments {FRAG_A} {FRAG_B}, question {Q_NEW}, relations {len(relations)}")
