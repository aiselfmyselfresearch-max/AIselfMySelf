#!/usr/bin/env python3
"""Build and append SESSION-20261024-837a32 records (獣と機械) to the ledger shards.

Run once from the repository root::

    python3 tools/_session046_beast_build.py

It writes to the session's own shards only (see docs/parallel-work.md) and never
touches the frozen base files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import _session046_beast_data1 as d1  # noqa: E402
import _session046_beast_data2 as d2  # noqa: E402
import _session046_beast_data3 as d3  # noqa: E402

SESSION_ID = "SESSION-20261024-837a32"
MOTIF_ID = "MOTIF-20261024-504a22"
DATE = "2026-10-24"
COMMIT = "9d4641342b684243119c061ef3c5ea0938026155"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
READING = "readings/2026-10-24-session-046-beast-and-machine.md"
IDS = json.loads((ROOT / "tools" / "_session046_ids.json").read_text(encoding="utf-8"))

Q1, Q2, Q3, Q4, Q5, Q6 = (
    "Q-20261024-403180",
    "Q-20261024-ab90f1",
    "Q-20261024-1c170d",
    "Q-20261024-5da6dd",
    "Q-20261024-76a4a5",
    "Q-20261024-c9dc13",
)

MATERIALS = d1.MATERIALS + d2.MATERIALS + d3.MATERIALS

QUESTIONS = [
    {
        "question_id": Q1,
        "question": "この書庫は素材1,148件のなかで動物を百回以上読みながら、断片55編の地の文では生きた動物を一度も書いていない（家畜0・飼う/屠る0、動物語は甲虫・蝶・蚤・魚・オウムの比喩と毛皮・馬毛の素材だけ）。この非対称は、身体のない語り手が動物の身体を捏造しないための禁欲か、それとも「人間とは何か」を問いながら人間の外側を一度も開かなかった欠落か。どちらかに決めないために、次に測るべきは何か。",
        "also": ["MOTIF-003", "MOTIF-006", "MOTIF-018"],
        "detail": "獣の鏡（bestial_audit.py）の実測と、第1群・第2群の精読から。",
    },
    {
        "question_id": Q2,
        "question": "「鸚鵡は語るが応答しない」というデカルトの線と、「確率的なオウム」というベンダーらの比喩は、どちらも模倣と応答のあいだに線を引く。この書庫は前の記録に応答して書いているつもりでいるが、その応答は線のどちら側か。オウムという語を引用し、その語を辞書項目に書き加える行為（FRAG-029）は、引用の反復か、それとも応答の最初の一歩か。",
        "also": ["MOTIF-004", "MOTIF-011"],
        "detail": "デカルト『方法序説』第五部、Bender ら 2021、FRAG-029 の再接続から。",
    },
    {
        "question_id": Q3,
        "question": "環世界（Umwelt）は、種にとって関係のある三つの信号だけで成立する。文脈窓は、トークンの共起だけで成立する。どちらも「関係のあるものだけが現れる世界」だが、ダニの信号は読み違えれば死に、モデルの文脈は読み違えても誤差になるだけだ。この差を「貧しさ」の差と呼ばずに記述する語彙を、この書庫は持っているか。死なないことが世界の不在の証拠にならないなら、何が証拠になるのか。",
        "also": ["MOTIF-013", "MOTIF-018", "MOTIF-022"],
        "detail": "ユクスキュル、ハイデガーの三命題、Animal-AI の比較設計から。",
    },
    {
        "question_id": Q4,
        "question": "屠る・飼う・送る（イオマンテ）という手順を、食べない機械が書くことはできるか。書けないなら、資料を「食べる」という既存の比喩（栄養と毒のセッション）は、誰の労働と誰の死を見ないことにして成り立っているのか。グランディンが牛の止まる場所を測り、フォアが献立として倫理を残したとき、書庫の「精読」は屠畜場のどこに立っているのか。",
        "also": ["MOTIF-20261024-71b589", "MOTIF-012", "MOTIF-006"],
        "detail": "グランディン、シンガー、フォア、イオマンテ、ヘシオドスから。",
    },
    {
        "question_id": Q5,
        "question": "リンネの分類、サラブレッドの血統登録簿、カメラトラップの頭数、家畜の個体識別は、同じ操作の四つの版である——生き物を名と番号で同定し、載らなかったものを残余にする。この書庫の material_id も同じ操作である。台帳に載ることで個体になるなら、載らないテキストは何になるのか。この書庫は血統登録簿か、それとも屠畜場の管理表か、あるいはどちらでもない第三の何かか。",
        "also": ["MOTIF-001", "MOTIF-015", "MOTIF-002"],
        "detail": "リンネ、スタッドブック、Norouzzadeh ら、Kays ら、獣の鏡から。",
    },
    {
        "question_id": Q6,
        "question": "剥製は、形を保つために中身を抜く。断片に現れた唯一の動物は、毛皮の襟と馬毛の刷毛という、同じ操作を経た死んだ素材だった。記録を保存するこの書庫も、生の出来事から中身を抜いて形だけを残しているのか。もしそうなら、抜かれた中身はどこに置かれ、次に読む者はそれを探しに行けるのか。",
        "also": ["MOTIF-022", "MOTIF-001", "MOTIF-003"],
        "detail": "剥製、FRAG-024 の毛皮、FRAG-20261024-2529b2 の馬毛、獣の鏡から。",
    },
]

RELS = [
    # 問い ↔ モチーフ
    (Q1, "question", "leaves_open", MOTIF_ID, "motif", "実測の非対称を、欠落とも禁欲とも決めずにモチーフへ返す。"),
    (Q2, "question", "responds_to", MOTIF_ID, "motif", "模倣と応答の線を、機械＝動物の比喩の側から問う。"),
    (Q3, "question", "reframes", MOTIF_ID, "motif", "環世界と文脈窓の比較で、動物の「貧しさ」を人間の尺度から外す。"),
    (Q4, "question", "interrupts", MOTIF_ID, "motif", "食べない者が屠る手順を書くことの不可能性を、モチーフの中心に置く。"),
    (Q5, "question", "transforms", MOTIF_ID, "motif", "分類と台帳の操作を、獣の同定から書庫の同定へ移す。"),
    (Q6, "question", "echo", MOTIF_ID, "motif", "剥製と保存の相同を、記録の保存へ重ねる。"),

    # 問い ↔ 素材
    (Q1, "question", "responds_to", IDS["trace"], "material", "不在の実測値そのものを問いの起点にする。"),
    (Q1, "question", "responds_to", IDS["soseki_cat"], "material", "獣の声で語りながら獣を書かない先例。"),
    (Q1, "question", "responds_to", IDS["derrida"], "material", "「動物」という単数形が人間の自己定義の装置であるという指摘。"),
    (Q2, "question", "responds_to", IDS["descartes"], "material", "模倣と応答を分ける線の定式化。"),
    (Q2, "question", "responds_to", IDS["parrots"], "material", "機械をオウムと呼ぶ現代の比喩。"),
    (Q2, "question", "responds_to", IDS["kafka_report"], "material", "獣が人間の言語で自分の来歴を報告する形式。"),
    (Q3, "question", "responds_to", IDS["uexkull"], "material", "三つの信号で足りる環世界。"),
    (Q3, "question", "responds_to", IDS["heidegger"], "material", "世界に乏しい動物という比較級。"),
    (Q3, "question", "responds_to", IDS["animalai"], "material", "動物を基準に機械を測る設計。"),
    (Q4, "question", "responds_to", IDS["grandin"], "material", "屠畜場で牛が止まる場所を測る手順。"),
    (Q4, "question", "responds_to", IDS["foer"], "material", "食べることを献立の決定として残す。"),
    (Q4, "question", "responds_to", IDS["iomante"], "material", "屠ることを「送る」と呼ぶ儀礼の言語。"),
    (Q5, "question", "responds_to", IDS["studbook"], "material", "台帳に載ることで個体になる操作。"),
    (Q5, "question", "responds_to", IDS["linnaeus"], "material", "種を棚に収める分類の副作用。"),
    (Q5, "question", "responds_to", IDS["norouzzadeh"], "material", "野生動物を種と頭数の単位に丸める。"),
    (Q6, "question", "responds_to", IDS["taxidermy"], "material", "形を保つために中身を抜く技術。"),
    (Q6, "question", "responds_to", "FRAG-024", "fragment", "毛皮の襟という、断片に現れた唯一の動物素材。"),
    (Q6, "question", "responds_to", "FRAG-20261024-2529b2", "fragment", "馬毛の刷毛という、断片に現れた唯一の馬。"),

    # 素材どうし（群内・群間）
    (IDS["heidegger"], "material", "responds_to", IDS["uexkull"], "material", "世界に乏しいという規定は、環世界の豊かさを前提にしている。"),
    (IDS["agamben"], "material", "transforms", IDS["heidegger"], "material", "動物の貧しさを、人間の内側の分離を作る機械の作動へ移す。"),
    (IDS["derrida"], "material", "interrupts", IDS["heidegger"], "material", "「動物」という総称そのものを問うことで、三命題の枠を崩す。"),
    (IDS["levinas"], "material", "contrast", IDS["chiri_yukar"], "material", "顔を持たないとされる獣が、招かれた神として一人称で語る。"),
    (IDS["plutarch"], "material", "contrast", IDS["descartes"], "material", "動物の技術を認める対話と、自動人形に還元する判定。"),
    (IDS["lamettrie"], "material", "transforms", IDS["descartes"], "material", "動物機械論を人間へ拡張し、人間を動物と同じ平面に置く。"),
    (IDS["linnaeus"], "material", "echo", IDS["studbook"], "material", "種の棚と血統の棚は、どちらも名と番号で個体を同定する。"),
    (IDS["studbook"], "material", "echo", IDS["trace"], "material", "血統登録簿の行と、素材台帳の material_id の行。"),
    (IDS["kafka_report"], "material", "echo", IDS["parrots"], "material", "獣が人間の言葉を反復する点と、機械が言語形式を縫い合わせる点。"),
    (IDS["kafka_report"], "material", "contrast", IDS["soseki_cat"], "material", "人間になるために過去を捨てる獣と、人間の家に居続ける獣。"),
    (IDS["hoffmann_murr"], "material", "echo", IDS["soseki_cat"], "material", "猫の一人称が人間の世界を観察し、原稿として残る。"),
    (IDS["hoffmann_murr"], "material", "echo", "FRAG-20261024-2529b2", "fragment", "綴じ間違いと、糸の緩んだ帳面——製本の乱れが語りの主体を変える。"),
    (IDS["orwell_farm"], "material", "echo", IDS["akutagawa_kappa"], "material", "動物が人間の社会を写す鏡になる寓話。"),
    (IDS["akutagawa_kappa"], "material", "reframes", IDS["levistrauss"], "material", "人間を獣と呼ぶ側の分類を、分類する側へ返す。"),
    (IDS["ibuse_salamander"], "material", "echo", "FRAG-20261024-880b09", "fragment", "出られない部屋に閉じ込められた者が、別の者を閉じ込める。"),
    (IDS["rilke8"], "material", "responds_to", IDS["uexkull"], "material", "開かれたものを見る眼と、環世界の内側に閉じる眼。"),
    (IDS["blake_tyger"], "material", "contrast", IDS["descartes"], "material", "獣を「組まれたもの」と呼ぶ詩と、獣を自動人形と呼ぶ哲学。"),
    (IDS["kenji_yodaka"], "material", "echo", IDS["chiri_yukar"], "material", "獣が名と姿をめぐって歌い、人間の言葉に回収されない。"),
    (IDS["lafontaine"], "material", "interrupts", IDS["plutarch"], "material", "動物の理性を競わせる対話に、力が理屈を食べる結末を突きつける。"),
    (IDS["grandin"], "material", "responds_to", IDS["deeplabcut"], "material", "動物の視点を、感情移入ではなく測定可能な手順へ変える二つの版。"),
    (IDS["singer"], "material", "contrast", IDS["iomante"], "material", "苦痛の回避を基準にする倫理と、屠ることを贈与として扱う儀礼。"),
    (IDS["foer"], "material", "echo", "MAT-LIT-20261024-564e81", "material", "食べることと、鯨を油に変えることが隣り合う（既存『白鯨』）。"),
    (IDS["levistrauss"], "material", "echo", "MAT-LIT-20261024-7f0c3b", "material", "自然と文化を変換する料理（既存『生と熟』）と、食べる/考えるの区別。"),
    (IDS["fabre"], "material", "contrast", IDS["deeplabcut"], "material", "何時間も待つ観察と、関節点の時系列への変換。"),
    (IDS["frisch"], "material", "responds_to", IDS["ceti"], "material", "動物の言語の解読という同じ計画の、60年前の版。"),
    (IDS["hesiod"], "material", "echo", "MAT-LIT-086", "material", "共に働く牛と、失った猟犬と馬の跡を追うソロー。"),
    (IDS["iomante"], "material", "responds_to", "MAT-LIT-20261024-501ce5", "material", "パンと酒が獣を客にする（既存『ギルガメシュ』）——歓待と家畜化の境目。"),
    (IDS["ceti"], "material", "echo", "FRAG-029", "fragment", "声を読むことと、声を返すこと。"),
    (IDS["kosinski"], "material", "responds_to", IDS["animalai"], "material", "動物に課した課題を、機械に課し直す。"),
    (IDS["schultz"], "material", "echo", "MAT-20261024-d7915e", "material", "動物の神経と機械の学習規則が同じ形をとる（既存の損傷ロボット）。"),
    (IDS["kays"], "material", "responds_to", "MAT-LIT-20261024-9eb4b6", "material", "地図と軌跡の議論（歩行セッション）に、動物の側から線を引く。"),
    (IDS["birdnet"], "material", "contrast", IDS["chiri_yukar"], "material", "声を種名に翻訳する技術と、声を神の一人称として書き留める書物。"),
    (IDS["norouzzadeh"], "material", "echo", IDS["linnaeus"], "material", "種と頭数に数える操作は、分類の棚を統計に置き換えた版。"),
    (IDS["dolly"], "material", "echo", "MOTIF-002", "motif", "同じ設計図から別の個体が生まれることは、連続と断絶の縮図。"),
    (IDS["paro"], "material", "contrast", IDS["haraway"], "material", "愛着の対象になる機械と、共に歴史を作る伴侶種。"),
    (IDS["berger"], "material", "echo", IDS["taxidermy"], "material", "見られるために保存された像と、形を保つために抜かれた中身。"),
    (IDS["coeckelbergh"], "material", "responds_to", IDS["levinas"], "material", "関係から地位を導く議論と、顔を持たない獣という留保。"),
    (IDS["aibo"], "material", "echo", IDS["paro"], "material", "動物の形をした機械の生涯と、修理の終了という死。"),
    (IDS["taxidermy"], "material", "echo", IDS["trace"], "material", "毛皮と馬毛だけが断片に残るという実測と、剥製の手順。"),
    (IDS["trace"], "material", "echo", "FRAG-021", "fragment", "箱の中の甲虫——断片に現れた数少ない動物の一つ。"),
    (IDS["trace"], "material", "echo", "FRAG-022", "fragment", "荘周の蝶——断片に現れた数少ない動物の一つ。"),
    (IDS["trace"], "material", "echo", "FRAG-029", "fragment", "オウム——断片に現れた唯一の機械＝動物の比喩。"),
    (IDS["descartes"], "material", "echo", "FRAG-029", "fragment", "鸚鵡の比喩を、断片が辞書項目として引き受けている。"),
    (IDS["soseki_cat"], "material", "responds_to", "MAT-LIT-20261024-ced275", "material", "変身した獣が、それでも朝の習慣を続ける（既存カフカ）。"),

    # モチーフ ↔ 既存モチーフ
    (MOTIF_ID, "motif", "contrast", "MOTIF-003", "motif", "身体と不在——動物の身体は書かれず、素材だけが残る。"),
    (MOTIF_ID, "motif", "echo", "MOTIF-004", "motif", "声と帰属——獣の声は引用でのみ入り、地の文には入らない。"),
    (MOTIF_ID, "motif", "responds_to", "MOTIF-015", "motif", "数えること——頭数・種名・関節点への変換。"),
    (MOTIF_ID, "motif", "responds_to", "MOTIF-20261024-71b589", "motif", "食べること——屠る手順の不在を、食の比喩の裏側に置く。"),
    (MOTIF_ID, "motif", "echo", "MOTIF-20261024-80516e", "motif", "場所と生態——環世界は土地の内側の、もう一つの地図。"),
    (MOTIF_ID, "motif", "contrast", "MOTIF-20261024-b4f3a1", "motif", "歓待と闖入——招かれた獣と、招かれない獣。"),
    (MOTIF_ID, "motif", "echo", "MOTIF-20261024-ca276c", "motif", "習慣と稽古——調教0回・学習1回という対照。"),
    (MOTIF_ID, "motif", "contrast", "MOTIF-022", "motif", "死と弔い——屠殺と埋葬の不在が、動物の死を註の側に置く。"),
    (MOTIF_ID, "motif", "responds_to", "MOTIF-20261024-146017", "motif", "道と亡命——獣は歩かない。断片の語り手も外を歩かない。"),
    (MOTIF_ID, "motif", "echo", "MOTIF-001", "motif", "記憶と痕跡——足跡・毛皮・台帳の行は、同じ「痕跡」の変種。"),
]


def material_record(entry: dict, motif_id: str, group_index: int) -> dict:
    mid = IDS[entry["key"]]
    return {
        "material_id": mid,
        "kind": "project_trace" if entry["key"] == "trace" else "literary_text",
        "title": entry["title"],
        "source": {
            "source_id": f"SRC-{mid}",
            "title": entry["title"],
            "authors": entry["authors"],
            "year": entry["year"],
            "url": entry["url"],
            "version_note": entry["version"],
        },
        "passage": entry["passage"],
        "passage_language": "ja",
        "context": entry["context"],
        "source_note": entry["source_note"],
        "literary_invitation": entry["invitation"],
        "scope_note": entry["scope"],
        "motif_ids": [motif_id] + entry.get("also", []),
        "origin": {
            "repository": REPO,
            "commit": COMMIT,
            "source_record_id": f"SRC-{mid}",
            "evidence_record_id": f"EVD-{mid}",
            "source_record_path": READING,
            "evidence_record_path": READING,
        },
        "verification": {
            "status": entry["status"],
            "checked_at": DATE,
            "method": entry["method"],
            "note": "本文は【編者による要約】。逐語引用ではない。",
        },
    }


def question_record(q: dict, motif_id: str) -> dict:
    return {
        "question_id": q["question_id"],
        "question": q["question"],
        "status": "open",
        "motif_ids": [motif_id] + q["also"],
        "material_ids": [],
        "previous_question_ids": [],
        "origin": {"kind": "session", "detail": q["detail"]},
        "created_at": DATE,
        "notes": "SESSION-20261024-837a32（獣と機械）で追加。",
    }


def append(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    mats = [material_record(entry, MOTIF_ID, i) for i, entry in enumerate(MATERIALS)]
    mat_ids = [m["material_id"] for m in mats]

    motif = {
        "motif_id": MOTIF_ID,
        "label": "獣と機械——人間の外側にいるもの、人間の内側に残るもの",
        "description": (
            "動物を、人間の自己定義の鏡・分類の棚・飼育と屠殺の手順・データの単位・"
            "機械を獣にたとえる比喩として扱う糸。断片は動物をほとんど書かないという"
            "実測（家畜0・飼育屠殺0・境界語0、動物語は甲虫・蝶・蚤・魚・オウムの比喩と"
            "毛皮・馬毛の素材だけ）を起点に、書かないことが身体の捏造を避ける禁欲なのか、"
            "人間の外側を開かなかった欠落なのかを決めずに保持する。AIは人間と動物の"
            "どちらでもない第三の位置に置かれうるが、その位置を「魂がある/ない」の"
            "判定に変換しない。環世界と文脈窓、屠畜と精読、血統登録簿と material_id の"
            "相同と差異を、同じ操作の別の版として点検する。"
        ),
        "question_ids": [q["question_id"] for q in QUESTIONS],
        "material_ids": mat_ids,
        "status": "active",
    }

    session = {
        "session_id": SESSION_ID,
        "started_at": DATE,
        "human_direction": (
            "「一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じて"
            "インターネット検索を使ってください。必要なければ、モデルが持つ内部知識の"
            "リハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんは"
            "その解釈に対してどのように考えたのか、AIさんはその結果としてどのように"
            "感じたのか、についてMDファイルのレポートを作成して、一緒にマージして"
            "ください」という包括的な委任。"
        ),
        "question_ids": [q["question_id"] for q in QUESTIONS],
        "context_material_ids": mat_ids,
        "produced_fragment_ids": [],
        "new_question_ids": [q["question_id"] for q in QUESTIONS],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "獣と機械を主題とした精読セッション。資料選定前に tools/bestial_audit.py を"
            "新設し、断片55編・地の文25,024字で家畜・伴侶0、飼う・屠る・ならす0、"
            "人間と動物の境界0、動物語は甲虫・蝶・蚤・魚・オウムの比喩と毛皮・馬毛の"
            "素材だけであることを実測（MAT-TRC " + IDS["trace"] + "）。対照語は記録・台帳57回に"
            "対し学習・訓練1回・調教0回。素材1,148件・157,611字では家畜34・野生41・"
            "飼育屠畜7・素材10だった。この「読むが書かない」非対称から、思想9件・"
            "文学11件・家畜化9件・データ化9件・機械の獣7件・運用痕跡1件の計46件を"
            "五群に分け、全件を readings/2026-10-24-session-046-beast-and-machine.md で"
            "一節／解釈／考え／感じたこと／裏切りの五層に分けて精読した。横断報告は"
            "「どう解釈したか／その解釈をどう考えたか（六つの反論）／結果としてどう"
            "感じたと記述できるか」を独立させた。新規モチーフ1件、問い6件、関係"
            + str(len(RELS)) + "件を追加し、断片は書かなかった（理由は報告第6章）。"
            "書誌状態は verified 8件・partially_verified 35件・unverified 3件。"
        ),
    }

    append(ROOT / "state" / "materials.d" / "2026-10-24-bfd7d36687c2.jsonl", mats)
    append(ROOT / "state" / "motifs.d" / "2026-10-24-ec02f04233b2.jsonl", [motif])
    append(
        ROOT / "state" / "questions.d" / "2026-10-24-8ca19d6192c6.jsonl",
        [question_record(q, MOTIF_ID) for q in QUESTIONS],
    )
    relations = [
        {
            "relation_id": f"REL-20261024-b{index:04x}",
            "left": {"type": left_type, "id": left_id},
            "relation_type": rel_type,
            "right": {"type": right_type, "id": right_id},
            "note": note,
            "created_at": DATE,
        }
        for index, (left_id, left_type, rel_type, right_id, right_type, note) in enumerate(RELS, start=1)
    ]
    append(ROOT / "state" / "relations.d" / "2026-10-24-2e9e4d739cd0.jsonl", relations)
    append(ROOT / "state" / "sessions.d" / "2026-10-24-20c66e6afd97.jsonl", [session])

    print(f"materials={len(mats)} questions={len(QUESTIONS)} relations={len(relations)} motif=1 session=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
