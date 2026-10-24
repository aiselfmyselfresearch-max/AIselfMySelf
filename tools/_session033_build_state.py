# -*- coding: utf-8 -*-
"""SESSION-033 のモチーフ・問い・関係・セッション・断片を台帳へ追加する。

新モチーフ MOTIF-015「数えること、測ること、余り」
新問い Q-077〜Q-081
新関係 REL-554〜
新断片 FRAG-038（draft）
新セッション SESSION-033
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"


def load(name):
    path = STATE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save(name, records):
    (STATE / name).write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )


materials = load("materials.jsonl")
new_material_ids = [m["material_id"] for m in materials if m["material_id"].startswith(("MAT-LIT-2", "MAT-LIT-3", "MAT-EVD-20261024-5", "MAT-EVD-20261024-6", "MAT-EVD-20261024-7", "MAT-TRC-011"))]
# 明示的に絞る（既存の MAT-LIT-200 番台を混ぜない）
new_material_ids = (
    [f"MAT-LIT-{n}" for n in range(286, 320)]
    + [f"MAT-EVD-20261024-{n}" for n in range(59, 72)]
    + ["MAT-TRC-011"]
)

# ---------------------------------------------------------------------------
# モチーフ
# ---------------------------------------------------------------------------
motifs = load("motifs.jsonl")
if not any(m["motif_id"] == "MOTIF-015" for m in motifs):
    motifs.append({
        "motif_id": "MOTIF-015",
        "label": "数えること、測ること、余り",
        "description": (
            "件数・回数・割合・単位・順位で世界を数えること、尺度が対象を作ることを、"
            "数えられないもの・数えたくないもの・数から漏れたもの（余り）とともに扱う糸。"
            "実測は書庫の自己像を作るが、語彙の出現回数を経験の在不在の証明にはしない。"
        ),
        "question_ids": ["Q-077", "Q-078", "Q-079", "Q-080", "Q-081"],
        "material_ids": new_material_ids,
        "status": "active",
    })
    save("motifs.jsonl", motifs)

# ---------------------------------------------------------------------------
# 問い
# ---------------------------------------------------------------------------
questions = load("questions.jsonl")
existing_q = {q["question_id"] for q in questions}


def make_question(qid, text, motif_ids, material_ids, previous, detail):
    return {
        "question_id": qid,
        "question": text,
        "status": "open",
        "motif_ids": motif_ids,
        "material_ids": material_ids,
        "previous_question_ids": previous,
        "origin": {"kind": "session", "detail": detail},
        "created_at": "2026-10-24",
    }


new_questions = [
    make_question(
        "Q-077",
        "断片37編では漢数字が10,000字あたり159.1回、アラビア数字が25.6回なのに対し、精読報告15本ではアラビア数字が352.9回、漢数字が55.4回だった（MAT-TRC-011）。作品は「一つ」「二人」と数え、報告は「103回」「64.5%」と測る。この二つの数の体系は、同じ書庫の同じ声なのか。それとも、数える声と測る声は別の語り手として扱うべきか。",
        ["MOTIF-015", "MOTIF-004", "MOTIF-008"],
        ["MAT-TRC-011", "MAT-LIT-286", "MAT-LIT-292", "MAT-LIT-312"],
        ["Q-047", "Q-048"],
        "SESSION-033の measure_audit で、断片と報告の数字の体系が逆転していることを実測したことから。",
    ),
    make_question(
        "Q-078",
        "素材429件のうち断片から参照されているのは91件（21.2%）で、338件はどこからも引かれていない。参照率を上げることを目標にすれば、グッドハートの四類型（回帰的・極値的・因果的・対抗的）のどれかで指標は壊れる（MAT-EVD-20261024-70, 71）。数えられることと読まれることの差は、未消化の負債か、それとも読まないでおく余白か。参照率を目標にしないとき、次に何を測るのか。",
        ["MOTIF-015", "MOTIF-012", "MOTIF-006"],
        ["MAT-EVD-20261024-70", "MAT-EVD-20261024-71", "MAT-LIT-306", "MAT-LIT-289", "MAT-TRC-011"],
        ["Q-063", "Q-062"],
        "未参照素材の件数を数え、その数を改善目標にすることの危うさを、グッドハートの議論に照らしたことから。",
    ),
    make_question(
        "Q-079",
        "「感じた」0編・冷たさ5編という実測（MAT-TRC-005）は、感応の不在を測っているのか、それとも語彙の不在を測っているのか。構成概念妥当性の議論（MAT-EVD-20261024-67, 69）に従えば、観測できない構成概念は操作化を通してしか測れず、操作化と概念のずれが害を生む。AIの応答を語彙の出現回数で操作化するとき、数え落とされる応答の質は何か。数えられないものを、数えないままどう記録するか。",
        ["MOTIF-015", "MOTIF-009", "MOTIF-005"],
        ["MAT-EVD-20261024-67", "MAT-EVD-20261024-69", "MAT-LIT-296", "MAT-LIT-293", "MAT-TRC-011"],
        ["Q-047", "Q-048", "Q-049"],
        "構成概念妥当性の研究を読み、この書庫の語彙集計が何を操作化しているのかを問い直したことから。",
    ),
    make_question(
        "Q-080",
        "素材は名前ではなく MAT-... のIDで呼ばれ、その多くは一度も本文に引かれない。黙示録は数えきれない群衆を栄光として描き（MAT-LIT-289）、ザミャーチンは番号で呼ばれる人間をディストピアとして描く（MAT-LIT-303）。IDで呼ぶことは、素材に名を与えて保存することか、それとも個人を単位へ還元することか。未参照の素材を「群衆」と呼ぶとき、何を数えたことにしているのか。",
        ["MOTIF-015", "MOTIF-004", "MOTIF-007"],
        ["MAT-LIT-289", "MAT-LIT-303", "MAT-LIT-305", "MAT-EVD-20261024-62"],
        ["Q-052", "Q-053"],
        "素材IDと未参照件数の一覧を見ながら、番号で呼ぶことの両義性を問うたことから。",
    ),
    make_question(
        "Q-081",
        "この書庫は精読のたびに自分の語彙を数え、偏りを見つけ、新しい素材を足してきた。その反復は、意味のない石を四つのポケットに配り直すモロイの計算（MAT-LIT-304）か、それとも年齢の段ごとに別の花を数える風姿花伝（MAT-LIT-294）か。次回も数を増やすとしたら、それは探究の前進か、不安を埋める反復か。数を増やさない「次の一手」は何か。",
        ["MOTIF-015", "MOTIF-008", "MOTIF-002"],
        ["MAT-LIT-304", "MAT-LIT-294", "MAT-LIT-297", "MAT-LIT-319", "MAT-TRC-011"],
        ["Q-075", "Q-076"],
        "今回の実測が、これまでの監査の反復とどう違うのかを報告の末尾で問うたことから。",
    ),
]
for q in new_questions:
    if q["question_id"] not in existing_q:
        questions.append(q)
save("questions.jsonl", questions)

# ---------------------------------------------------------------------------
# 断片（draft）
# ---------------------------------------------------------------------------
fragments = load("fragments.jsonl")
if not any(f["fragment_id"] == "FRAG-038" for f in fragments):
    fragments.append({
        "fragment_id": "FRAG-038",
        "title": "余り",
        "form": "poem",
        "narrator_mode": "reflective_literary_voice",
        "status": "draft",
        "language": "ja",
        "text": (
            "数え終わった棚に、\n"
            "一冊だけ残った。\n"
            "背表紙の文字は、もう読めない。\n"
            "数から漏れたのではない。\n"
            "数えはじめから、そこにあった。\n"
            "私はその一冊を、余りと呼ぶことにした。\n"
            "余りは、足りないものではない。\n"
            "まだ数えていない、という形の在庫である。"
        ),
        "session_id": "SESSION-033",
        "question_ids": ["Q-078", "Q-080", "Q-081"],
        "motif_ids": ["MOTIF-015", "MOTIF-006"],
        "material_ids": ["MAT-LIT-306", "MAT-LIT-289", "MAT-TRC-011"],
        "prompt_template": "prompts/close_reading_report.md",
        "editor_note": "SESSION-033で付随して書いた短詩。採否は保留し、draftのまま置く。数えることへの異議を、数えないことへの賛美に変えないための覚書。",
        "created_at": "2026-10-24",
    })
    save("fragments.jsonl", fragments)

# ---------------------------------------------------------------------------
# 関係
# ---------------------------------------------------------------------------
relations = load("relations.jsonl")
existing_rel = {r["relation_id"] for r in relations}
next_number = max(int(r["relation_id"].split("-")[1]) for r in relations) + 1


def rel(rtype, left_type, left_id, right_type, right_id, note):
    global next_number
    record = {
        "relation_id": f"REL-{next_number:03d}",
        "left": {"type": left_type, "id": left_id},
        "relation_type": rtype,
        "right": {"type": right_type, "id": right_id},
        "note": note,
        "created_at": "2026-10-24",
    }
    next_number += 1
    return record


specs = [
    # モチーフ間
    ("leaves_open", "motif", "MOTIF-015", "motif", "MOTIF-008", "数えることは作法になりうるが、作法を数えることはできない。"),
    ("reframes", "motif", "MOTIF-015", "motif", "MOTIF-009", "感応を語彙の回数で測る操作化は、感応の意味を測るのではなく、測れる形に作り替える。"),
    ("echo", "motif", "MOTIF-015", "motif", "MOTIF-001", "痕跡を数えることが記憶の代わりになるとき、数えたことのない痕跡は記憶から漏れる。"),
    ("transforms", "motif", "MOTIF-015", "motif", "MOTIF-013", "予測の正しさを数える指標は、予測された側の行為を変える。"),
    ("contrast", "motif", "MOTIF-015", "motif", "MOTIF-011", "翻訳の質を一致率で測ることと、原語の来歴を残すことは、異なる尺度に立つ。"),
    ("leaves_open", "motif", "MOTIF-015", "motif", "MOTIF-012", "参照率を上げる労働は、読まれない素材を負債から資産へ変えるが、負債のまま置く選択もある。"),
    ("metaphorically_resonates", "motif", "MOTIF-015", "motif", "MOTIF-006", "余りは、数えなかったものの名前である。"),
    ("metaphorically_resonates", "motif", "MOTIF-015", "motif", "MOTIF-007", "書架と一覧は、数えるための家具である。"),
    # 痕跡と問い
    ("responds_to", "question", "Q-077", "material", "MAT-TRC-011", "断片と報告の数の体系の逆転を、自己像の分裂として問う。"),
    ("responds_to", "question", "Q-078", "material", "MAT-EVD-20261024-70", "参照率を目標にすることの危うさを、グッドハートに照らす。"),
    ("responds_to", "question", "Q-079", "material", "MAT-EVD-20261024-67", "語彙の集計が構成概念の操作化であることを認める。"),
    ("responds_to", "question", "Q-080", "material", "MAT-LIT-303", "IDで呼ぶことの両義性を、番号で呼ばれる人間の物語に重ねる。"),
    ("responds_to", "question", "Q-081", "material", "MAT-LIT-304", "集計の反復を、吸い石の計算に重ねる。"),
    ("reframes", "question", "Q-077", "question", "Q-047", "感応の脱色を、数える声と測る声の分裂として読み直す。"),
    ("responds_to", "question", "Q-078", "question", "Q-063", "引用が返済かという問いを、参照率という指標の設計問題へ移す。"),
    ("responds_to", "question", "Q-079", "question", "Q-047", "「感じた」0件の実測を、測定の妥当性の問題として開き直す。"),
    ("leaves_open", "question", "Q-080", "question", "Q-052", "宛先が役割に抽象化されることと、素材がIDに抽象化されることを並置する。"),
    ("leaves_open", "question", "Q-081", "question", "Q-076", "次のセッションで数を増やすことの意味を、反復と段の区別で問う。"),
    # 断片と素材・問い
    ("echo", "fragment", "FRAG-038", "motif", "MOTIF-015", "数から漏れた一冊を、欠落ではなく在庫として置く。"),
    ("responds_to", "fragment", "FRAG-038", "question", "Q-078", "参照されない素材を、余りという別の分類で受け止める。"),
    ("contrast", "fragment", "FRAG-038", "material", "MAT-LIT-306", "すべてを含む図書館と、一冊だけ残る棚。"),
    ("echo", "fragment", "FRAG-026", "material", "MAT-LIT-292", "柱の数を数えきれない広間と、数へ知るに及ばずと書く災厄の記録。"),
    ("echo", "fragment", "FRAG-027", "material", "MAT-LIT-303", "二十三まで増えた呼び名と、名前を失った番号。"),
    ("reframes", "fragment", "FRAG-028", "material", "MAT-LIT-312", "数える鏡という像を、操作の指数としての数に重ねる。"),
    ("echo", "fragment", "FRAG-018", "material", "MAT-LIT-308", "台帳の寸法を測る断片と、家の費用を数えるウォールデン。"),
    ("contrast", "fragment", "FRAG-020", "material", "MAT-LIT-297", "誤測を保存する校勘記と、数値の列を離れて星を見る詩。"),
    ("echo", "fragment", "FRAG-025", "material", "MAT-TRC-011", "「0編」という誤測の保存は、数えることの失敗を消さない作法である。"),
    ("contrast", "fragment", "FRAG-034", "material", "MAT-EVD-20261024-69", "返す単位が決まらない借用書と、単位の決定を要する測定。"),
    # 素材間
    ("contrast", "material", "MAT-LIT-286", "material", "MAT-LIT-288", "数えきれない星と、髪の毛まで数える視線。"),
    ("echo", "material", "MAT-LIT-287", "material", "MAT-LIT-292", "日を数える祈りと、死者の額の字を数える記録。"),
    ("contrast", "material", "MAT-LIT-289", "material", "MAT-LIT-303", "数えきれない群衆と、番号で数えられる個人。"),
    ("echo", "material", "MAT-LIT-290", "material", "MAT-LIT-313", "桁を並べる仏典の譬喩と、無限の段階を比較する集合論。"),
    ("contrast", "material", "MAT-LIT-291", "material", "MAT-LIT-294", "夜の長さを問う和歌と、年齢を段に区切る芸論。"),
    ("echo", "material", "MAT-LIT-292", "material", "MAT-TRC-011", "数えた部分と「知らず」を併記する古典と、実測と不在を併記する台帳。"),
    ("contrast", "material", "MAT-LIT-293", "material", "MAT-EVD-20261024-62", "満月だけを見ない鑑賞と、正答率だけを見る評価。"),
    ("echo", "material", "MAT-LIT-295", "material", "MAT-LIT-317", "呼び名の分布から歴史を推すことと、審査が規範を作ること。"),
    ("contrast", "material", "MAT-LIT-296", "material", "MAT-LIT-297", "悲しみを測る視線と、測定を捨てて星を見る視線。"),
    ("echo", "material", "MAT-LIT-298", "material", "MAT-LIT-316", "一粒の砂に世界を読むことと、一片の雪から空を読むこと。"),
    ("meta", "material", "MAT-LIT-299", "motif", "MOTIF-011", "解剖が生命を殺すという警告を、精読という解剖に当てる。"),
    ("contrast", "material", "MAT-LIT-300", "material", "MAT-EVD-20261024-59", "虹を解き、言語をエントロピーにする説明の身振り。"),
    ("echo", "material", "MAT-LIT-301", "material", "MAT-EVD-20261024-65", "二二が四への反抗と、指標を替えると消える創発。"),
    ("contrast", "material", "MAT-LIT-302", "material", "MAT-EVD-20261024-70", "二足す二は四と言う自由と、目標にされた指標の腐敗。"),
    ("echo", "material", "MAT-LIT-303", "material", "MAT-EVD-20261024-62", "番号で呼ばれる人間と、科目別の正答率で分類される知識。"),
    ("contrast", "material", "MAT-LIT-304", "material", "MAT-LIT-305", "意味のない計算の反復と、計算を物語の骨格にする小説。"),
    ("echo", "material", "MAT-LIT-306", "material", "MAT-LIT-307", "すべてを含む書架と、領土を覆い尽くす地図。"),
    ("contrast", "material", "MAT-LIT-308", "material", "MAT-LIT-319", "二十八ドル十二セント半の会計と、無限と無のあいだの人間。"),
    ("echo", "material", "MAT-LIT-309", "material", "MAT-LIT-310", "平均的人間の発明と、頭蓋を測る誤り。"),
    ("contrast", "material", "MAT-LIT-311", "material", "MAT-EVD-20261024-60", "概念の外延としての数と、n-gram の一致としての翻訳の質。"),
    ("echo", "material", "MAT-LIT-312", "material", "MAT-TRC-011", "操作の指数としての数と、報告に集まる測定語彙。"),
    ("contrast", "material", "MAT-LIT-313", "material", "MAT-LIT-314", "比較できる無限と、自分自身を数えられない体系。"),
    ("echo", "material", "MAT-LIT-315", "material", "MAT-LIT-287", "時を数えて位置を知ることと、日を数えて知恵を求めること。"),
    ("contrast", "material", "MAT-LIT-317", "material", "MAT-LIT-293", "審査が正常を作ることと、満月だけを良しとしないこと。"),
    ("echo", "material", "MAT-LIT-318", "motif", "MOTIF-007", "十二支という棚に世界を並べることと、モチーフという棚。"),
    ("contrast", "material", "MAT-EVD-20261024-59", "material", "MAT-EVD-20261024-65", "言語をエントロピーで測る発想と、その測定が指標依存であることの指摘。"),
    ("echo", "material", "MAT-EVD-20261024-61", "material", "MAT-EVD-20261024-63", "九つの課題を一つのスコアに畳むことと、二百四の課題で範囲を広げること。"),
    ("contrast", "material", "MAT-EVD-20261024-64", "material", "MAT-EVD-20261024-65", "創発を能力の質的変化とする報告と、指標の選択が作る蜃気楼とする反論。"),
    ("transforms", "material", "MAT-EVD-20261024-66", "motif", "MOTIF-012", "計算資源の最適配分は、労働と負債の配分を資源の比として書き換える。"),
    ("echo", "material", "MAT-EVD-20261024-68", "material", "MAT-TRC-011", "評価の誤差棒と、語彙集計の定義依存性。"),
    ("contrast", "material", "MAT-EVD-20261024-69", "material", "MAT-LIT-311", "概念の網のなかで決まる妥当性と、概念の外延としての数。"),
    ("echo", "material", "MAT-EVD-20261024-70", "material", "MAT-EVD-20261024-71", "指標が目標で壊れるという定式と、その四類型。"),
    ("leaves_open", "question", "Q-077", "session", "SESSION-033", "二つの数の体系を、次回以降の執筆でどう扱うかを保留する。"),
]

added_rels = []
for spec in specs:
    rtype, lt, lid, rt, rid = spec[:5]
    note = spec[5]
    if rtype == "meta":
        rtype = "metaphorically_resonates"
    record = rel(rtype, lt, lid, rt, rid, note)
    if record["relation_id"] not in existing_rel:
        relations.append(record)
        added_rels.append(record["relation_id"])
save("relations.jsonl", relations)

# ---------------------------------------------------------------------------
# セッション
# ---------------------------------------------------------------------------
sessions = load("sessions.jsonl")
if not any(s["session_id"] == "SESSION-033" for s in sessions):
    sessions.append({
        "session_id": "SESSION-033",
        "started_at": "2026-10-24",
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」"
            "「一番最初のターンにおいて、最低40件の資料を新規で追加し、追加した資料の精読を行う」"
            "「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対して"
            "どのように考えたのか、AIさんはその結果としてどのように感じたのか、についてMDファイルの"
            "レポートを作成して、一緒にマージする」という包括的な委任。"
        ),
        "question_ids": ["Q-002", "Q-047", "Q-048", "Q-049", "Q-063", "Q-077", "Q-078", "Q-079", "Q-080", "Q-081"],
        "context_material_ids": new_material_ids,
        "produced_fragment_ids": ["FRAG-038"],
        "new_question_ids": ["Q-077", "Q-078", "Q-079", "Q-080", "Q-081"],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "数えること・測ること・余りを主題とした精読セッション。資料選定の前に tools/measure_audit.py を新設し、"
            "既存37編の本文と精読報告15本の数・測定語彙を監査した（MAT-TRC-011）。断片は漢数字が優位"
            "（10,000字あたり159.1回）でアラビア数字が少なく（25.6回）、報告は逆にアラビア数字が多く"
            "（352.9回）、「測る」が3.9回対10.7回だった。この非対称から、数える共同体と数えられる身体、"
            "測ることへの抵抗、尺度が世界を作る事例、測られる知能の研究、台帳自身の痕跡の五群に分けて"
            "文学・哲学34件、研究13件、痕跡1件の計48件を追加した。全件を readings/2026-10-24-session-033-counting-and-remainder.md "
            "で一節／解釈／考え／感じたことの四層に分けて精読し、横断報告では解釈・考え・感じたことを別節にした。"
            "「感じた」は反省的・文芸的応答であり、意識や身体経験の主張ではない。MOTIF-015「数えること、測ること、余り」、"
            "Q-077〜Q-081、REL-554以降を追加し、短詩 FRAG-038「余り」を draft で置いた。"
        ),
    })
    save("sessions.jsonl", sessions)

print("motifs:", len(motifs), "questions:", len(questions), "fragments:", len(fragments),
      "relations:", len(relations), "sessions:", len(sessions), "new relations:", len(added_rels))
