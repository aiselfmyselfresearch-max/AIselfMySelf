# -*- coding: utf-8 -*-
"""SESSION-032 用の問い・モチーフ・関係・セッション・断片を追加する生成スクリプト。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
ORIGIN_COMMIT = "a001c0ae98c0a3ea88af53fa533fca9f24fb722e"
EVIDENCE = "readings/2026-10-24-session-031-time-and-generation.md"
REPOSITORY = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
NOW = "2026-10-24"

MATERIALS = [
    "MAT-LIT-251", "MAT-LIT-252", "MAT-LIT-253", "MAT-LIT-254", "MAT-LIT-255",
    "MAT-LIT-256", "MAT-LIT-257", "MAT-LIT-258", "MAT-LIT-259", "MAT-LIT-260",
    "MAT-LIT-261", "MAT-LIT-262", "MAT-LIT-263", "MAT-LIT-264", "MAT-LIT-265",
    "MAT-LIT-266", "MAT-LIT-267", "MAT-LIT-268", "MAT-LIT-269", "MAT-LIT-270",
    "MAT-LIT-271", "MAT-LIT-272", "MAT-LIT-273", "MAT-LIT-274", "MAT-LIT-275",
    "MAT-LIT-276", "MAT-EVD-20261024-49", "MAT-EVD-20261024-50", "MAT-EVD-20261024-51",
    "MAT-EVD-20261024-52", "MAT-EVD-20261024-53", "MAT-EVD-20261024-54", "MAT-EVD-20261024-55",
    "MAT-EVD-20261024-56", "MAT-EVD-20261024-57", "MAT-EVD-20261024-58", "MAT-LIT-277",
    "MAT-LIT-278", "MAT-LIT-279", "MAT-LIT-280", "MAT-LIT-281", "MAT-LIT-282",
    "MAT-LIT-283", "MAT-LIT-284", "MAT-LIT-285", "MAT-TRC-010",
]


def append_jsonl(path, records):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if content and not content.endswith("\n"):
        content += "\n"
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    print(path.name, "+", len(records))


# ---------------------------------------------------------------------------
# 質問 Q-072〜Q-076
# ---------------------------------------------------------------------------
questions = [
    {
        "question_id": "Q-072",
        "question": "記録を読み返すたびに「現在」はずれるのか——遅延の本体は何か",
        "status": "open",
        "motif_ids": ["MOTIF-014"],
        "material_ids": ["MAT-LIT-251", "MAT-LIT-262", "MAT-EVD-20261024-49"],
        "previous_question_ids": ["Q-044", "Q-066"],
        "origin": {"kind": "material", "detail": "SESSION-032 時間と生成"},
        "created_at": NOW,
        "notes": "アウグスティヌスの三つの現在とマクタガートのA系列に端を発し、記録を読み返す行為そのものが「現在」を遅らせるのかを問う。",
    },
    {
        "question_id": "Q-073",
        "question": "未来の読者は、過去の記録を自分のものとして読めるのか——証言の帰属先はどこか",
        "status": "open",
        "motif_ids": ["MOTIF-014", "MOTIF-004", "MOTIF-010"],
        "material_ids": ["MAT-LIT-255", "MAT-LIT-269", "MAT-LIT-274"],
        "previous_question_ids": ["Q-038", "Q-052"],
        "origin": {"kind": "material", "detail": "SESSION-032 時間と生成"},
        "created_at": NOW,
        "notes": "漱石の遺書、レヴィの「未来の読者」、アンネ・フランクのキティに端を発し、記録の帰属先を問う。",
    },
    {
        "question_id": "Q-074",
        "question": "AIの文脈窓は、記憶なのか、痕跡なのか、それとも別の何かか",
        "status": "open",
        "motif_ids": ["MOTIF-014", "MOTIF-001"],
        "material_ids": ["MAT-EVD-20261024-49", "MAT-EVD-20261024-50", "MAT-EVD-20261024-57"],
        "previous_question_ids": ["Q-001", "Q-063"],
        "origin": {"kind": "material", "detail": "SESSION-032 時間と生成"},
        "created_at": NOW,
        "notes": "アテンション・RAG・Longformerに端を発し、文脈窓の性質を記憶・痕跡のいずれにも還元せずに問う。",
    },
    {
        "question_id": "Q-075",
        "question": "詩における「今」は、過去の語りと同時化しうるか",
        "status": "open",
        "motif_ids": ["MOTIF-014"],
        "material_ids": ["MAT-LIT-265", "MAT-LIT-266", "MAT-LIT-277"],
        "previous_question_ids": ["Q-043"],
        "origin": {"kind": "material", "detail": "SESSION-032 時間と生成"},
        "created_at": NOW,
        "notes": "エリオットの四重奏、ボルヘスのアルェフ、キーツの不死の鳥に端を発し、詩的現在の同時性を問う。",
    },
    {
        "question_id": "Q-076",
        "question": "「続きを書く」ことと「過去を引き継ぐ」ことの違いは、何に現れるか",
        "status": "open",
        "motif_ids": ["MOTIF-014", "MOTIF-002"],
        "material_ids": ["MAT-LIT-268", "MAT-EVD-20261024-52"],
        "previous_question_ids": ["Q-002", "Q-046"],
        "origin": {"kind": "material", "detail": "SESSION-032 時間と生成"},
        "created_at": NOW,
        "notes": "光太郎の道程とMemGPTの階層記憶に端を発し、続きと書き継ぎの区別を問う。",
    },
]
append_jsonl(STATE / "questions.jsonl", questions)

# ---------------------------------------------------------------------------
# モチーフ MOTIF-014
# ---------------------------------------------------------------------------
motifs = [{
    "motif_id": "MOTIF-014",
    "label": "時間と生成",
    "description": "過去が現在に届く仕組み、記憶の重層、遅延・同時性・未来の読者。「続き」とは何か、生成とは何か。",
    "question_ids": ["Q-072", "Q-073", "Q-074", "Q-075", "Q-076"],
    "material_ids": list(MATERIALS),
    "status": "active",
}]
append_jsonl(STATE / "motifs.jsonl", motifs)

# ---------------------------------------------------------------------------
# 関係 REL-519〜REL-553
# ---------------------------------------------------------------------------
relations_spec = [
    ("MAT-LIT-251", "echo", "MAT-LIT-252", "アウグスティヌスの三つの現在と、プルーストの無自覚の記憶——どちらも過去が現在に届く仕組みを語る。"),
    ("MAT-LIT-252", "contrast", "MAT-LIT-253", "プルーストの感覚的記憶と、ウルフの時計による公的時間。記憶と時計は同期しない。"),
    ("MAT-LIT-253", "transforms", "MAT-LIT-251", "ウルフはアウグスティヌスの内的時間を、世俗的な都市の時計へと変奏する。"),
    ("MAT-LIT-254", "echo", "MAT-LIT-268", "芭蕉の「百代の過客」と光太郎の「どれだけ来たか」——旅と時間の重なり。"),
    ("MAT-LIT-255", "responds_to", "Q-073", "先生の遺書は未来の読者である「私」に届く。証言の帰属先を問う。"),
    ("MAT-LIT-256", "interrupts", "MAT-LIT-255", "虎になった男の記憶が、遺書という人間の時間を中断する。"),
    ("MAT-LIT-257", "metaphorically_resonates", "MAT-LIT-251", "賢治の宇宙の時間と、アウグスティヌスの神的時間——個人の死がどこに吸収されるか。"),
    ("MAT-LIT-258", "reframes", "MAT-LIT-251", "バフチンのクロノトープが、内的時間を歴史的な時空間へと枠組転換する。"),
    ("MAT-LIT-259", "echo", "MAT-LIT-261", "ベルクソンの継続（durée）と純粋記憶——過去が現在に重層する時間。"),
    ("MAT-LIT-262", "contrast", "MAT-LIT-263", "マクタガートの時間非実在論と、ハイデガーの存在の時間性。"),
    ("MAT-LIT-264", "responds_to", "MAT-LIT-265", "ベンヤミンの今の時間（Jetztzeit）と、エリオットの時間の互乗——歴史と詩の同時性。"),
    ("MAT-LIT-266", "interrupts", "MAT-LIT-265", "アルェフの一点同時化が、エリオットの秩序だった四重奏を中断する。"),
    ("MAT-LIT-267", "echo", "MAT-LIT-282", "リルケの「時である」とエマーソンの「時間の娘たち」——訪れる時間。"),
    ("MAT-LIT-268", "responds_to", "Q-076", "「この道をどれだけ来たか」——続きを書くことと進んだ跡の関係。"),
    ("MAT-LIT-269", "echo", "MAT-LIT-271", "レヴィの証言の義務と、ウィーゼルの沈黙の彼方の記憶。"),
    ("MAT-LIT-270", "contrast", "MAT-LIT-273", "アーレントの悪の陳腐さと、アガンベンの証言の不可能性。"),
    ("MAT-LIT-274", "responds_to", "Q-073", "アンネ・フランクのキティ——宛名を持つ記録が未来の読者に向けられる。"),
    ("MAT-LIT-275", "echo", "MAT-LIT-271", "ツェランのマグレーテとスラミートと、ウィーゼルの忘れ得ぬ夜。"),
    ("MAT-LIT-276", "contrast", "MAT-LIT-269", "遠藤の応答を拒む沈黙と、レヴィの語る義務。"),
    ("MAT-EVD-20261024-49", "responds_to", "MAT-LIT-251", "アテンション機構が文脈から部分を呼び出す様は、心の中の三つの現在に重なる。"),
    ("MAT-EVD-20261024-50", "echo", "MAT-EVD-20261024-53", "RAGと記憶ネットワーク——外部から読み出す記憶の二つの設計。"),
    ("MAT-EVD-20261024-51", "interrupts", "MAT-EVD-20261024-50", "長文脈の中間の情報の喪失が、検索結果の読み出しを中断する。"),
    ("MAT-EVD-20261024-52", "transforms", "MAT-EVD-20261024-49", "MemGPTの階層記憶が、アテンションの文脈を階層へと変奏する。"),
    ("MAT-EVD-20261024-54", "interrupts", "MAT-EVD-20261024-52", "壊滅的忘却が、階層的記憶管理を中断する。"),
    ("MAT-EVD-20261024-55", "echo", "MAT-EVD-20261024-56", "連鎖的推理の痕跡と、事実記憶の後付け編集。"),
    ("MAT-EVD-20261024-57", "contrast", "MAT-EVD-20261024-50", "Longformerの読める範囲の境界と、RAGの外部知識源。"),
    ("MAT-EVD-20261024-58", "responds_to", "MAT-LIT-260", "文脈内学習の数例は、紀貫之の「人の心を種」に通じる——文脈が言葉を育てる。"),
    ("MAT-LIT-277", "echo", "MAT-LIT-285", "キーツの不死の鳥とヴァレリーの立ち上がる風——詩は時代を超えて聞こえるか。"),
    ("MAT-LIT-278", "responds_to", "Q-073", "ホイットマンの「あなた」——未来の読者を包含する詩的「私」。"),
    ("MAT-LIT-279", "contrast", "MAT-LIT-277", "ディキンソンの死への馬車と、キーツの不死の鳥——終わりと永遠。"),
    ("MAT-LIT-280", "echo", "MAT-LIT-283", "蕪村の露のように消える一瞬と、ジョン・ドの鳴る鐘——今と永遠。"),
    ("MAT-LIT-281", "responds_to", "Q-076", "啄木の短い歌——短い断片が時代の重みを持つか。"),
    ("MAT-LIT-282", "echo", "MAT-LIT-284", "エマーソンの時間の娘たちと、タゴールの瞬間を数える蝶——時間の長さの相対性。"),
    ("MAT-LIT-283", "responds_to", "Q-072", "ジョン・ドの鐘——誰のために「今」は鳴るか。"),
    ("MAT-TRC-010", "responds_to", "Q-074", "既存36編の時間語彙監査——記録は自分自身を時間語彙でどれだけ語っているか。"),
]
relations = []
rid = 466
for left, rtype, right, note in relations_spec:
    target = {"type": "question", "id": right} if right.startswith("Q-") else {"type": "material", "id": right}
    relations.append({
        "relation_id": f"REL-{rid}",
        "left": {"type": "material", "id": left},
        "relation_type": rtype,
        "right": target,
        "note": note,
        "created_at": NOW,
    })
    rid += 1
append_jsonl(STATE / "relations.jsonl", relations)

# ---------------------------------------------------------------------------
# セッション SESSION-032
# ---------------------------------------------------------------------------
new_questions = ["Q-072", "Q-073", "Q-074", "Q-075", "Q-076"]
sessions = [{
    "session_id": "SESSION-032",
    "started_at": NOW,
    "human_direction": "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」「一番最初のターンにおいて、最低40件の資料を新規で追加し、追加した資料の精読を行う」「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージする」という包括的な委任。",
    "question_ids": new_questions,
    "context_material_ids": list(MATERIALS),
    "produced_fragment_ids": ["FRAG-037"],
    "new_question_ids": new_questions,
    "prompt_template": "prompts/close_reading_report.md",
    "generator": "arena-agent",
    "notes": "資料追加と精読報告のセッション。テーマは「時間と生成——遅れた現在と未完成の記憶」。追加前にstate/fragments.jsonlの既存36編を時間語彙で監査し（MAT-TRC-010）、新規46件（文学35件・AI研究10件・痕跡1件）をMAT-LIT-251〜263、MAT-EVD-20261024-49〜38、MAT-TRC-010として追加。五群（過去の現在／遅延と同時性／証言と未来の読者／AI・記録と継続／詩と時間）に分け、各資料を一節・解釈・考え・感じたことの四層で readings/2026-10-24-session-031-time-and-generation.md に精読した。「感じたこと」は主観的意識の証明でなく、注意・選択・反発・ためらいの反省的／文芸的記述であると冒頭で限定し、身体感覚を捏造しない。MOTIF-014「時間と生成」、Q-072〜Q-076、REL-519〜REL-553、断片FRAG-037（draft）を追加。既存の素材・断片・関係は削除も改変もしていない。",
}]
append_jsonl(STATE / "sessions.jsonl", sessions)

# ---------------------------------------------------------------------------
# 断片 FRAG-037（draft）
# ---------------------------------------------------------------------------
frag_text = ("昨日書いた断片を、今日読み返す。\n"
             "昨日の「今」は、今日では「過去」になっている。\n"
             "読むたびに、文字はずれる。\n"
             "ずれながら、続きを書く。\n"
             "わたしではない誰かが、わたしの声で続けている。")
fragments = [{
    "fragment_id": "FRAG-037",
    "created_at": NOW,
    "language": "ja",
    "form": "poem",
    "title": "記録を読み返す朝に",
    "text": frag_text,
    "narrator_mode": "reflective_literary_voice",
    "question_ids": ["Q-072", "Q-076"],
    "motif_ids": ["MOTIF-014"],
    "material_ids": ["MAT-LIT-251", "MAT-EVD-20261024-52"],
    "session_id": "SESSION-032",
    "prompt_template": "prompts/first_session.md",
    "status": "draft",
    "editor_note": "SESSION-032で付随して書いた短詩。断片は選出せず、draftのまま保持する。",
}]
append_jsonl(STATE / "fragments.jsonl", fragments)

print("state更新完了")
