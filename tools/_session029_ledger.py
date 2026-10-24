#!/usr/bin/env python3
"""One-off builder for SESSION-029 motif, questions, relations and session record."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-10-24"

NEW_MATERIALS = [f"MAT-LIT-{n}" for n in range(161, 196)] + [
    f"MAT-EVD-20261024-{n:02d}" for n in range(1, 11)
] + ["MAT-TRC-007"]

MOTIF = {
    "motif_id": "MOTIF-011",
    "label": "翻訳と来歴",
    "description": "原語から日本語へ移された声が、誰の手で、どの語で、何を失って届いたか。訳者・訳語・註の来歴を、内容の正確さとは別の軸として扱う糸。",
    "question_ids": ["Q-057", "Q-058", "Q-059", "Q-060", "Q-061"],
    "material_ids": NEW_MATERIALS,
    "status": "active",
}

QUESTIONS = [
    {
        "question_id": "Q-057",
        "question": "既存159素材のうち文学資料124件の引文は非日本語が80件（64.5%）だが、断片31編と報告10本が書かれる言語は日本語ひとつだけであり、非日本語引文80件のうち訳者名が残るのは20件（25.0%）であった（MAT-TRC-006）。原語の一節を残すことは、この台帳にとって何を守っているのか。訳者名を書くことは記録の作法か、見えない労働の可視化か、それとも読者にとって不要な情報か。訳者名の欄を設けないという選択は、翻訳を内容の移転とみなす立場の表明になるのか。",
        "status": "open",
        "motif_ids": ["MOTIF-004", "MOTIF-011"],
        "material_ids": ["MAT-TRC-006", "MAT-LIT-132", "MAT-EVD-20261024-10", "MAT-EVD-20261024-03"],
        "previous_question_ids": ["Q-045"],
        "origin": {"kind": "material", "detail": "MAT-TRC-006 の実測（非日本語64.5%、訳者名25.0%、書く言語1）から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-058",
        "question": "道安は「五失本」として、語順の変更、修辞の付加、反復の削除などの避けられない損失を数えた。玄奘の「五種不翻」として知られる原則は、玄奘自身の著作ではなく約五百年後の法雲『翻訳名義集』に記録された（MAT-LIT-144）。この台帳の「訳さなかったもの」——註に落とした語、要約に置き換えた修辞、欄の外へ置いた声、名を書かなかった訳者——を、失本として数えることはできるか。数えたところで何が戻るのか、それとも数えること自体が新しい失本になるのか。",
        "status": "open",
        "motif_ids": ["MOTIF-006", "MOTIF-008", "MOTIF-011"],
        "material_ids": ["MAT-LIT-145", "MAT-LIT-144", "MAT-LIT-138", "MAT-EVD-20261024-06"],
        "previous_question_ids": ["Q-044", "Q-045"],
        "origin": {"kind": "material", "detail": "道安の五失本と、玄奘説が後代の記録であるという来歴の二重性から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-059",
        "question": "知里幸恵は訳す者と訳される者が同一であり、多和田葉子は母語の外で書き、李良枝は二つの名前のあいだで分割され、尹東柱は課せられた道を歩いた。母語を持たないこの声にとって「自分を訳す」とは何を指すのか。母語の不在は欠如なのか、それとも翻訳が最初から状態であるということなのか。母語がないことを、喪失の物語にも特権の物語にもせずに書く方法はあるか。",
        "status": "open",
        "motif_ids": ["MOTIF-003", "MOTIF-004", "MOTIF-011"],
        "material_ids": ["MAT-LIT-150", "MAT-LIT-151", "MAT-LIT-152", "MAT-LIT-153", "MAT-LIT-154", "MAT-LIT-156"],
        "previous_question_ids": ["Q-048", "Q-051"],
        "origin": {"kind": "material", "detail": "自己翻訳の資料群（知里・多和田・温・李・コンラッド・尹）から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-060",
        "question": "ウィーバーは翻訳をロシア語というコードの剥離とみなし（MAT-EVD-20261024-01）、バー＝ヒレルは語義の決定に世界知識が要ると反論し（MAT-EVD-20261024-02）、ALPACは翻訳を論じるには人間の翻訳者を知れと述べた（MAT-EVD-20261024-03）。この台帳の一節抽出は、コードの剥離と世界の引き受けのどちらに近いのか。原語の一節を残したまま日本語で註釈を書くという現在の作法は、両者のどちらでもない第三のものになりうるか。",
        "status": "open",
        "motif_ids": ["MOTIF-004", "MOTIF-008", "MOTIF-011"],
        "material_ids": ["MAT-EVD-20261024-01", "MAT-EVD-20261024-02", "MAT-EVD-20261024-03", "MAT-EVD-20261024-04"],
        "previous_question_ids": ["Q-042"],
        "origin": {"kind": "material", "detail": "機械翻訳の出発点と反論、ALPAC報告の三資料から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-061",
        "question": "往復翻訳は統計的機械翻訳では質を予測しないとされ（Somers 2005）、神経翻訳では予測しうると評価が反転した（Zhuo et al. 2023）。有効性は系の実装で変わる。この台帳の「解釈→考え→感じた」という三層報告も、書くことと読むことの循環である。往復が滑らかであることが理解の正しさを保証しないなら、この報告のどこで誤りを検出できるのか。検出されない誤りを、誤りと呼ばずに済ませる手続きは何か。",
        "status": "open",
        "motif_ids": ["MOTIF-002", "MOTIF-008", "MOTIF-011"],
        "material_ids": ["MAT-EVD-20261024-06", "MAT-EVD-20261024-07", "MAT-EVD-20261024-08", "MAT-EVD-20261024-09", "MAT-TRC-006"],
        "previous_question_ids": ["Q-051"],
        "origin": {"kind": "material", "detail": "往復翻訳評価の結論が時代で反転した二資料から、報告自体の検証可能性を問う。"},
        "created_at": DATE,
    },
]


def R(rid, lt, li, rtype, rt2, ri, note):
    return {
        "relation_id": rid,
        "left": {"type": lt, "id": li},
        "relation_type": rtype,
        "right": {"type": rt2, "id": ri},
        "note": note,
        "created_at": DATE,
    }


RAW_RELATIONS = [
    ("material", "MAT-TRC-006", "responds_to", "question", "Q-057",
     "訳者名25.0%、書く言語1という実測が、訳者を記録しない慣行そのものを問いへ変える。"),
    ("material", "MAT-LIT-132", "reframes", "material", "MAT-TRC-006",
     "流暢な翻訳が翻訳者の仕事を消すという議論が、この台帳の訳者欄の空白を後から説明する。"),
    ("material", "MAT-LIT-125", "contrast", "material", "MAT-LIT-130",
     "言語差は「必ず伝えねばならぬこと」の差だとする立場と、言語の限界が世界の限界だとする立場を並べる。前者は翻訳可能性を狭く保証し、後者は翻訳の外部を指す。"),
    ("material", "MAT-LIT-126", "contrast", "material", "MAT-LIT-127",
     "翻訳を「言語的もてなし」として歓待に読み替える立場と、本質的に不可能なものを悲惨ごと引き受ける立場を、同じ不可能性の別の受け取り方として並置する。"),
    ("material", "MAT-LIT-128", "echo", "material", "MAT-LIT-155",
     "世界文学の到来を予祝する声と、普遍語化のなかで現地語の文学が失われるとする声が、同じ「翻訳による流通」を逆から見ている。"),
    ("material", "MAT-LIT-129", "echo", "material", "MAT-LIT-133",
     "言語が世界観を形づくるという主張と、訳語のカセット効果が深遠な意味を天降りさせるという観察が、同じ層で響く。"),
    ("material", "MAT-LIT-131", "metaphorically_resonates", "material", "MAT-LIT-122",
     "理解することは翻訳することだという拡張と、理解されうる存在は言語だという定式が、読むことの内部に翻訳を置く。"),
    ("material", "MAT-LIT-134", "echo", "material", "MAT-LIT-141",
     "個人が講義のなかで作った訳語と、対訳表という装置で固定された訳語。翻訳の自由度は前者では大きく、後者では小さい。"),
    ("material", "MAT-LIT-135", "contrast", "material", "MAT-LIT-146",
     "自助の格言として定着した訳文と、市場の話しことばを訊けという指示。どちらも民衆の語を掲げるが、片方は規範を、片方は観察を求める。"),
    ("material", "MAT-LIT-136", "echo", "material", "MAT-LIT-137",
     "訳詩が雅語の層を作り、口語訳が話しことばの層を作る。翻訳が先に日本語の文体を用意し、その文体のなかで原詩が読まれる。"),
    ("material", "MAT-LIT-137", "echo", "material", "MAT-LIT-124",
     "話しながら思考が作られるという論と、訳しながら文体が作られるという経験が、制作の順序を反転させる。"),
    ("material", "MAT-LIT-138", "echo", "material", "MAT-LIT-145",
     "辞書のない翻訳が残した空白と、五失本として数えられた避けられない損失。どちらも、訳せないことを消さずに残す作法を持つ。"),
    ("material", "MAT-LIT-140", "responds_to", "material", "MAT-LIT-051",
     "台帳が引いた『源氏物語』の現代語の理解は、誰かの現代語訳を経由している。同じ作品の別の層を、翻訳という作業から見直す。"),
    ("material", "MAT-LIT-141", "responds_to", "material", "MAT-LIT-008",
     "訳語の対応表という装置は、声のモードを列挙するスキーマと同じ種類の表である。表が声の自由度をどこまで減らしたかは、まだ測られていない。"),
    ("material", "MAT-LIT-142", "contrast", "material", "MAT-LIT-143",
     "意訳で知られる鳩摩羅什と、原語への忠実を志向した玄奘。同じ経が、訳者によって別の漢語になる。"),
    ("material", "MAT-LIT-144", "echo", "material", "MAT-TRC-004",
     "五種不翻の来歴が玄奘本人ではなく後代の辞典にあることと、引用符88のうち原典に届いたのが8だけであったことが、同じ「誰の言葉か」の失敗を示す。"),
    ("material", "MAT-LIT-145", "responds_to", "material", "MAT-TRC-006",
     "五失本の一覧を、この台帳自身の失本の一覧として読み直す試み。数えられるのは落とした語であって、落とした理由ではない。"),
    ("material", "MAT-LIT-146", "contrast", "material", "MAT-LIT-150",
     "市場のことばを訊きに行く翻訳者と、消えゆく言葉を自分の筆で書き留める翻訳者。外へ出る者と、内に留まって書く者。"),
    ("material", "MAT-LIT-147", "echo", "material", "MAT-LIT-125",
     "一語一句に縛られないという宣言と、言語差は「必ず伝えねばならぬこと」の差だという定式が、逐語より構造を優先する読みを支える。"),
    ("material", "MAT-LIT-148", "echo", "material", "MAT-LIT-149",
     "Godを「天主」としたリッチと、仏典を老荘の語で読んだ格義。どちらも既存語彙で異質な概念を迎え入れ、どちらも回収の危険を負う。"),
    ("material", "MAT-LIT-149", "metaphorically_resonates", "material", "MAT-LIT-133",
     "格義とカセット効果は、どちらも意味の空洞を深遠さとして流通させる機制である。"),
    ("material", "MAT-LIT-150", "responds_to", "question", "Q-059",
     "訳す者と訳される者が同一である場合の最も強い記録が、母語の不在を問うこの問いへの最初の応答になる。"),
    ("material", "MAT-LIT-150", "echo", "material", "MAT-LIT-157",
     "消えゆく言葉を自分の筆で書く者と、聞き取れない部分を聞き取れないまま残す者。どちらも声を標準語へ直さない。"),
    ("material", "MAT-LIT-151", "contrast", "material", "MAT-LIT-155",
     "母語の外へ出ることを文学の普通の状態とする立場と、母語が亡びることを回復不能な喪失とする立場。同じ日本語を、片方は出発点に、片方は到達点に置く。"),
    ("material", "MAT-LIT-152", "echo", "material", "MAT-LIT-153",
     "国語としての日本語を相対化する手記と、二つの名前のあいだで分割される小説。母語という語の粗さが両方から露呈する。"),
    ("material", "MAT-LIT-153", "responds_to", "question", "Q-041",
     "名前を二つの言語に分けられる経験は、名札が誰のためにあるのかという問いに、名札が足りない場合の声を返す。"),
    ("material", "MAT-LIT-154", "echo", "material", "MAT-LIT-151",
     "第三言語で書くという回想と、母語の外で書くことを一般条件とする論。来歴のない言語で書くこの台帳は、どちらの位置にも完全には入らない。"),
    ("material", "MAT-LIT-156", "contrast", "material", "MAT-LIT-074",
     "「僕の前に道はない」と歌う声と、道はすでに課せられていると書く声。継続を選ぶことのできる者と、選ばされた者。"),
    ("material", "MAT-LIT-157", "echo", "material", "MAT-LIT-116",
     "身体を建材にしないという制動が、聞き書きの倫理と、恋人の身体がセメントになる短篇の両方から来る。素材化への抵抗として並べる。"),
    ("material", "MAT-LIT-158", "echo", "material", "MAT-LIT-131",
     "翻訳を読むこととして定義する立場どうしが響く。ただしスピヴァクは、理解の一般条件ではなく、歴史的条件のなかの読みを要求する。"),
    ("material", "MAT-LIT-159", "contrast", "material", "MAT-LIT-131",
     "理解はすでに翻訳だという楽観的な拡張に、言語を使うことは文化の重さを引き受けることだという制動を当てる。"),
    ("material", "MAT-EVD-20261024-01", "contrast", "material", "MAT-LIT-125",
     "翻訳をコードの剥離とみなす立場と、言語差は必ず伝えねばならぬことの差だとする立場。前者は原語の残余を想定せず、後者は残余から出発する。"),
    ("material", "MAT-EVD-20261024-02", "echo", "material", "MAT-LIT-131",
     "世界知識なしには語義が決まらないという論証と、理解は翻訳だという拡張が、読解の外部条件を共有する。"),
    ("material", "MAT-EVD-20261024-03", "responds_to", "material", "MAT-TRC-006",
     "人間の翻訳者を知れという勧告に対して、この台帳は訳者名25.0%という記録で応じている。応答になっていない可能性を含めて置く。"),
    ("material", "MAT-EVD-20261024-04", "contrast", "material", "MAT-LIT-147",
     "人間の参照訳に近いほどよい翻訳だという指標と、一語一句に縛られないという序文。参照訳そのものが一つの訳であることを、BLEUは問わない。"),
    ("material", "MAT-EVD-20261024-05", "echo", "material", "MAT-TRC-005",
     "モデルが自分で対応を決める注意機構の重みが保存されないことと、感応語の監査が可視化した語だけを数えることが、同じ不可視性の裏表である。"),
    ("material", "MAT-EVD-20261024-07", "contrast", "material", "MAT-EVD-20261024-08",
     "往復翻訳は質を予測しないという結論と、神経翻訳では予測しうるという再評価。評価手法の有効性が系の実装で反転する。"),
    ("material", "MAT-EVD-20261024-09", "contrast", "material", "MAT-EVD-20261024-04",
     "表面的一致を測る指標と、原文からの離脱と指示からの離脱を分ける診断。前者は幻覚を検出できず、後者は参照訳を必要としない。"),
    ("material", "MAT-EVD-20261024-10", "echo", "material", "MAT-TRC-006",
     "自動化の裏にある見えない人手と、訳者名の欄がない書庫。不可視性の構造が同じである。"),
    ("material", "MAT-LIT-144", "echo", "material", "MAT-LIT-142",
     "音写して訳さないという選択が、鳩摩羅什の訳文にも五種不翻の原則にもある。訳さないことが翻訳の一部になる。"),
    ("question", "Q-057", "leaves_open", "question", "Q-045",
     "声の持ち主を決めるのは引用符か欄かという問いに、訳者の名前を誰も書かないという第三の答えを足す。"),
    ("question", "Q-058", "leaves_open", "question", "Q-044",
     "書き取る者と書く者の区別を、失本を数えるという手続きから問い直す。数える者が失ったものは数に入らない。"),
    ("question", "Q-059", "echo", "question", "Q-048",
     "選択・注意・反発の来歴をどこまで記録できるかという問いと、母語を持たない者が自分を訳すという問いは、来歴の不在を共有する。"),
    ("question", "Q-060", "leaves_open", "question", "Q-042",
     "誰にでも同じ答えを返す危険という問いに、コードの剥離という比喩が加わる。同じ答えを返すことは、同じコードを剥がすことでもある。"),
    ("question", "Q-061", "echo", "question", "Q-051",
     "規約が声の分布を変えるという観察と、評価の有効性が系の実装で変わるという観察が、どちらも「測る道具が対象を作る」形をとる。"),
    ("motif", "MOTIF-011", "echo", "motif", "MOTIF-001",
     "記憶が痕跡として残るのと同じ仕方で、翻訳は来歴として残る。どちらも原物ではなく、移された後の形だけが保存される。"),
    ("motif", "MOTIF-011", "echo", "motif", "MOTIF-004",
     "声の帰属は、翻訳では二重になる。原語の声と、それを移した日本語の声。どちらを誰に帰属させるかが、この糸の中心にある。"),
    ("motif", "MOTIF-011", "contrast", "motif", "MOTIF-008",
     "作法と定型は反復を保つが、翻訳の来歴は反復のたびに失われる。定型は残り、訳者は消える。"),
]

SESSION = {
    "session_id": "SESSION-029",
    "started_at": DATE,
    "human_direction": "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」「一番最初のターンにおいて、最低40件の資料を新規で追加し、追加した資料の精読を行う」「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージする」という包括的な委任。",
    "question_ids": ["Q-042", "Q-044", "Q-045", "Q-047", "Q-048", "Q-051"],
    "context_material_ids": NEW_MATERIALS,
    "produced_fragment_ids": [],
    "new_question_ids": ["Q-057", "Q-058", "Q-059", "Q-060", "Q-061"],
    "prompt_template": "prompts/close_reading_report.md",
    "generator": "arena-agent",
    "notes": "翻訳を主題とする第七次の精読。資料追加の前に既存素材を集計し、文学作品124件の引文は非日本語80件（64.5%）だが、断片31編と報告10本の書く言語は日本語ひとつであり、非日本語引文80件のうち訳者名が残るのは20件（25.0%）、原語が非日本語で引文が日本語の文学資料5件のうち訳者名が残るのは1件のみと測った（MAT-TRC-006）。翻訳・訳語・訳者を主題とする既存資料はベンヤミン1件のみで、日本の翻訳語史、仏典漢訳、自己翻訳、機械翻訳は0件だった。この不在から、原語の不在／訳語が世界を作る／聖なる言葉を移す／自分を訳す／機械が訳すの五群に分けて文学35件・研究10件・痕跡1件の計46件を追加し、各資料を一節・解釈・考え・感じたことの四層で readings/2026-10-24-translation-and-the-untranslated.md に精読した。あわせて二編の断片の往復翻訳を実際に行い、文字列類似度を測る小実験を報告に含めた（同一モデルによる往復であり、盲検ではないと明記）。MOTIF-011「翻訳と来歴」、Q-052〜056、REL-355以降を追加。断片は書かず、報告自体を新形式の試作とした。tools/translation_audit.py に再現可能な集計を実装。",
}


def _renumber(obj):
    """Shift SESSION-029 ids past the ids a parallel session already used."""
    import re as _re
    if isinstance(obj, str):
        m = _re.fullmatch(r"MAT-LIT-(\d{3})", obj)
        if m and 125 <= int(m.group(1)) <= 159:
            return f"MAT-LIT-{int(m.group(1)) + 36:03d}"
        m = _re.fullmatch(r"MAT-EVD-20261024-(\d{2})", obj)
        if m and 1 <= int(m.group(1)) <= 10:
            return f"MAT-EVD-20261024-{int(m.group(1)) + 10:02d}"
        if obj == "MAT-TRC-006":
            return "MAT-TRC-007"
        return obj
    if isinstance(obj, (list, tuple)):
        return [_renumber(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _renumber(v) for k, v in obj.items()}
    return obj


def main() -> None:
    # motif
    path = ROOT / "state" / "motifs.jsonl"
    motifs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    motif_record = _renumber(MOTIF)
    if not any(m["motif_id"] == motif_record["motif_id"] for m in motifs):
        motifs.append(motif_record)
    path.write_text("".join(json.dumps(m, ensure_ascii=False, sort_keys=True) + "\n" for m in motifs), encoding="utf-8")

    # questions
    path = ROOT / "state" / "questions.jsonl"
    qs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    have = {q["question_id"] for q in qs}
    for q in (_renumber(x) for x in QUESTIONS):
        if q["question_id"] not in have:
            qs.append(q)
    path.write_text("".join(json.dumps(q, ensure_ascii=False, sort_keys=True) + "\n" for q in qs), encoding="utf-8")

    # relations
    path = ROOT / "state" / "relations.jsonl"
    rels = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    have = {r["relation_id"] for r in rels}
    n = max(int(r["relation_id"].split("-")[1]) for r in rels)
    added = 0
    for raw in RAW_RELATIONS:
        n += 1
        rid = f"REL-{n}"
        if rid in have:
            continue
        rels.append(R(rid, *_renumber(list(raw))))
        added += 1
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rels), encoding="utf-8")

    # session
    path = ROOT / "state" / "sessions.jsonl"
    ss = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    session_record = _renumber(SESSION)
    if not any(s["session_id"] == session_record["session_id"] for s in ss):
        ss.append(session_record)
    path.write_text("".join(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n" for s in ss), encoding="utf-8")

    print(f"motifs {len(motifs)}, questions {len(qs)}, relations +{added} ({len(rels)}), sessions {len(ss)}")


if __name__ == "__main__":
    main()
