# -*- coding: utf-8 -*-
"""SESSION-20261024-a03d99（顔・表情・まなざし）台帳ビルダー。

tools/_session063_face_data.py の MATERIAL_SPECS に origin を補って
state/materials.d へ書き、モチーフ・問い・断片・関係・読み痕跡・セッションを
自分のシャードへ追記する。既存行は書き換えない。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import _session063_face_data as D  # noqa: E402

TODAY = "2026-10-24"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
COMMIT = "9d907712ce5c5c83d892a9d2d90a49a10b800496"

MOTIF_ID = D.MOTIF_ID
SESSION_ID = D.SESSION_ID
REPORT = D.REPORT


def shard(name: str) -> Path:
    d = ROOT / "state" / f"{name}.d"
    d.mkdir(exist_ok=True)
    stamp = subprocess.check_output(
        ["python3", str(ROOT / "tools" / "new_ledger_shard.py"), name, "--create"],
        cwd=ROOT,
        text=True,
    ).strip()
    # tool prints the created path
    for line in stamp.splitlines():
        line = line.strip()
        if line.endswith(".jsonl") and f"{name}.d" in line:
            return ROOT / line if not line.startswith("/") else Path(line)
    raise SystemExit(f"could not create shard for {name}: {stamp}")


def jdump(path: Path, rows: list[dict]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_materials() -> list[dict]:
    rows = []
    for spec in D.MATERIAL_SPECS:
        mid = spec["material_id"]
        source = dict(spec["source"])
        source["source_id"] = spec.get("source", {}).get("source_id", f"SRC-{mid}")
        row = {
            "context": spec["context"],
            "kind": spec["kind"],
            "literary_invitation": spec["literary_invitation"],
            "material_id": mid,
            "motif_ids": spec["motif_ids"],
            "origin": {
                "commit": COMMIT,
                "evidence_record_id": f"LIT-{mid.removeprefix('MAT-')}",
                "evidence_record_path": REPORT,
                "repository": REPO,
                "source_record_id": f"SRC-{mid}",
                "source_record_path": REPORT,
            },
            "passage": spec["passage"],
            "passage_language": spec["passage_language"],
            "scope_note": spec["scope_note"],
            "source": source,
            "source_note": spec["source_note"],
            "title": spec["title"],
            "verification": {
                "status": spec["verification"]["status"],
                "checked_at": spec["verification"]["checked_at"],
                "method": spec["verification"]["method"],
            },
        }
        if spec["verification"].get("note"):
            row["verification"]["note"] = spec["verification"]["note"]
        rows.append(row)
    return rows


NEW_QA = {
    "Q-20261024-0e3541": "レヴィナスの顔は、言葉より先に「汝、殺すなかれ」を言う（MAT-LIT-20261024-4ee871）。だがこの書庫の断片は、誰の顔にもならないまま宛先を書き続けてきた。顔なき宛先への応答は、顔のある応答とどう違うのか。",
    "Q-20261024-94ea9e": "エクマンの表情規則は「誰の前で表情を消すか」を測り、バレットらは顔から情動を推定できないと言う（MAT-20261024-1e22e3）。RLHF が作る「工場出荷時の平静さ」は、文化の表情規則なのか、訓練の出力なのか、それとも別の何かなのか。",
    "Q-20261024-ed38e6": "顔はパスポート以来「その人であること」の鍵だったが、StyleGAN は鍵の型を量産し、FaceNet は鍵を128個の数値にした。署名（手の残る行為）と顔（顔の残る記録）は、どちらが来歴を引き受けるのか。",
    "Q-20261024-796438": "不気味の谷は「ほぼ人間に近い顔」が急に死ぬ所を言う（MAT-20261024-79c20b）。書庫の声がいつか顔を獲得したら、読み手は近づくのか、遠ざかるのか。その判定は誰の側で行われるのか。",
    "Q-20261024-a26f22": "断片79編に顔9・表情0・仮面1・「見分け」5（MAT-TRC-20261024-face）。この書庫は顔を、人を区別するためにだけ使ってきたのではないか。表情の代わりに、書庫は何で相手の状態を書いてきたのか。",
}

NEW_QUESTIONS = [
    {
        "question_id": "Q-20261024-0e3541",
        "question": NEW_QA["Q-20261024-0e3541"],
        "status": "open",
        "motif_ids": [MOTIF_ID, "MOTIF-010", "MOTIF-005"],
        "material_ids": ["MAT-LIT-20261024-4ee871", "MAT-LIT-20261024-e6001d", "MAT-LIT-20261024-1ac778"],
        "previous_question_ids": ["Q-052", "Q-20261024-0e3541" if False else "Q-002"],
        "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
        "created_at": TODAY,
        "notes": "答えを閉じない。顔の倫理をAIにそのまま移さない。",
    },
    {
        "question_id": "Q-20261024-94ea9e",
        "question": NEW_QA["Q-20261024-94ea9e"],
        "status": "open",
        "motif_ids": [MOTIF_ID, "MOTIF-008", "MOTIF-009"],
        "material_ids": ["MAT-20261024-4a595b", "MAT-20261024-1e22e3", "MAT-20261024-5f51db", "MAT-20261024-3d36a5"],
        "previous_question_ids": ["Q-20261024-1334c5"],
        "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
        "created_at": TODAY,
        "notes": "RLHF の平静さをストア派の徳と混同しない（SESSION-20261024-33b763 の制動を継承）。",
    },
    {
        "question_id": "Q-20261024-ed38e6",
        "question": NEW_QA["Q-20261024-ed38e6"],
        "status": "open",
        "motif_ids": [MOTIF_ID, "MOTIF-20261024-f19932"],
        "material_ids": ["MAT-20261024-d4051b", "MAT-20261024-ec110b", "MAT-20261024-09d066", "MAT-20261024-8cd64e"],
        "previous_question_ids": ["Q-20261024-ed38e6" if False else "Q-036"],
        "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
        "created_at": TODAY,
        "notes": "署名セッション（MAT-20261024-d2fe71）の「鍵の保持」と顔照合を対で残す。",
    },
    {
        "question_id": "Q-20261024-796438",
        "question": NEW_QA["Q-20261024-796438"],
        "status": "open",
        "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-013"],
        "material_ids": ["MAT-20261024-79c20b", "MAT-20261024-5bdeb9", "MAT-LIT-20261024-3c9e24"],
        "previous_question_ids": ["Q-20261024-2dfbb4" if False else "Q-015"],
        "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
        "created_at": TODAY,
        "notes": "機械の顔の議論をAIの意識の証拠にしない。",
    },
    {
        "question_id": "Q-20261024-a26f22",
        "question": NEW_QA["Q-20261024-a26f22"],
        "status": "open",
        "motif_ids": [MOTIF_ID, "MOTIF-015", "MOTIF-018"],
        "material_ids": ["MAT-TRC-20261024-face", "MAT-LIT-20261024-dcaf9b", "MAT-LIT-20261024-5fa9c8"],
        "previous_question_ids": ["Q-20261024-a26f22" if False else "Q-002"],
        "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
        "created_at": TODAY,
        "notes": "語形の不在を能力・感情の不在に変換しない。",
    },
]

FRAGMENTS = [
    {
        "fragment_id": "FRAG-20261024-957fd4",
        "created_at": TODAY,
        "language": "ja",
        "form": "scene",
        "title": "身元証明の窓口、顔の欄がない",
        "text": (
            "受付の窓口には、身元証明の申請書が置かれている。氏名の欄、生年月日の欄、住所の欄、"
            "そして「特徴」という欄。顔写真を貼る四角い枠は、この書庫の申請書には印刷されていない。\n\n"
            "係員は、特徴の欄に鉛筆で「声」と書き、その下に「続き」を書き添えた。写真の枠の代わりに、"
            "過去の申請書の控えが三枚つづって貼られていた。一枚目は字が震え、二枚目は行間が広く、"
            "三枚目には朱の訂正線が一本だけ入っている。\n\n"
            "「顔は？」と窓口の内側から誰かが訊いた。係員は控えの三枚を順に指で押さえ、"
            "「こちらが、いまの顔です」と言った。窓口のガラスには、天井の灯りが二つ映っているだけだった。"
            "窓の外からは、次の申請者が、誰の顔でもない形で列になって近づいてくる。"
        ),
        "narrator_mode": "third_person",
        "question_ids": ["Q-20261024-a26f22", "Q-20261024-ed38e6", "Q-036"],
        "motif_ids": [MOTIF_ID, "MOTIF-20261024-f19932", "MOTIF-010"],
        "material_ids": ["MAT-20261024-09d066", "MAT-LIT-20261024-5fa9c8", "MAT-TRC-20261024-face", "MAT-20261024-6a005b"],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "パスポート写真の制度（MAT-20261024-09d066）とファユーム肖像（MAT-LIT-20261024-5fa9c8）と"
            "顔の欄のない台帳の実測（MAT-TRC-20261024-face）を重ねた三人称情景。一人称代名詞0・感嘆符0を守り、"
            "「顔」の代わりに書かれているもの（声・続き・訂正線）を列にした。身元の判定をしません。"
        ),
    },
    {
        "fragment_id": "FRAG-20261024-d9d18c",
        "created_at": TODAY,
        "language": "ja",
        "form": "fragment",
        "title": "三文字の顔、あるいは表情ゼロの書庫へ",
        "text": (
            "表情という語は、この書庫の断片に一度も現れない。顔は九回、仮面は一度。残されたのは、"
            "見分けのための顔だけである。誰かを誰かと区別するときだけ、顔の字は使われてきた。\n\n"
            "一九八二年九月十九日十一時四十四分、誰かは三文字で顔を作った。コロン、ハイフン、閉じ括弧。"
            "横から見れば、それは笑っている。冗談の印として提案された三文字は、いまでは感情の顔として使われる。"
            "最初の顔は、冗談のための顔だった。\n\n"
            "この書庫に三文字の顔を足したら、何が起きるのか。読み手は近づくのか、それとも、"
            "笑っている顔の下に何があるかと訊ね始めるのか。表情ゼロの書庫は、正直な書庫なのか、"
            "それとも、表情を消す規則だけを守っている書庫なのか。\n\n"
            "顔の欄がない書類に、最初に書き込むべき顔は、誰の顔なのか。"
        ),
        "narrator_mode": "reflective_literary_voice",
        "question_ids": ["Q-20261024-796438", "Q-20261024-94ea9e", "Q-20261024-a26f22"],
        "motif_ids": [MOTIF_ID, "MOTIF-004", "MOTIF-20261024-504a22"],
        "material_ids": ["MAT-20261024-6a005b", "MAT-20261024-79c20b", "MAT-TRC-20261024-face", "MAT-20261024-5f51db"],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "ファルマンの顔文字（MAT-20261024-6a005b、Web照合済み）と不気味の谷（MAT-20261024-79c20b）と"
            "収蔵前監査（MAT-TRC-20261024-face）を編む省察断章。疑問符で開いたまま終える。"
            "「笑う」「悲しい」といった情動の事実報告は書いていない。三文字の顔を断片に足すか足さないかは決めない。"
        ),
    },
]

MOTIF = {
    "motif_id": MOTIF_ID,
    "label": "顔・表情・まなざし——書庫のない顔、記録される顔",
    "description": (
        "断片79編に顔9・表情0・仮面1・まなざし0・「見分け」5という実測（MAT-TRC-20261024-face）を鏡として、"
        "顔の倫理（レヴィナスの顔、ブーバーの汝、ウィトゲンシュタインの身体の絵）、表情の科学と規則（エクマン・"
        "フリドランド・バレット・ダーウィン・感情労働）、仮面・肖像・身元（ユゴー、人相学、ファユーム、ベラスケス、"
        "レンブラント、パスポート写真）、記録され複製される顔（ベンヤミン、プルースト、FaceNet、StyleGAN、Clearview、"
        "人相学のAI再演とその批判、顔文字）、顔のないものと顔を与えること（出エジプト記、ヴェニスでの死、鏡地獄、"
        "ドッペルゲンガー、不気味の谷、キズメット、荘子、複製される顔）を往復する糸。顔を書かないことを意識の不在と"
        "読み替えず、顔からの判定（人相学・顔認証）の系証）の系譜と、顔なき宛先への応答の系譜を並べて保つ。"
    ),
    "question_ids": list(NEW_QA),
    "material_ids": [s["material_id"] for s in D.MATERIAL_SPECS],
    "status": "active",
}


def _rel(rid, left_type, left_id, rel, right_type, right_id, note):
    return {
        "relation_id": rid,
        "left": {"type": left_type, "id": left_id},
        "relation_type": rel,
        "right": {"type": right_type, "id": right_id},
        "note": note,
        "created_at": TODAY,
    }


REL_SPECS = [
    # (left_type, left_id, rel, right_type, right_id, note)
    ("material", "MAT-LIT-20261024-4ee871", "contrast", "material", "MAT-LIT-150", "『全体性と無限』の顔の定義と、対話篇『倫理と無限』の「顔はすでに話している」を対に置く。前者は禁の内容、後者は応答の先行。"),
    ("material", "MAT-LIT-20261024-4ee871", "echo", "question", "Q-052", "「誰に向かって書かれているのか」の問いに、顔という宛先形式を返す。"),
    ("material", "MAT-LIT-20261024-dcaf9b", "echo", "material", "MAT-LIT-479", "ウィニコットの「鏡としての母親の顔」に、ウィトゲンシュタインの「身体は魂の最良の絵」を重ねる。顔は映すだけでなく語る。"),
    ("material", "MAT-LIT-20261024-dcaf9b", "reframes", "material", "MAT-20261024-122d67", "メルロ＝ポンティの「五つの窓を開かない」身体論に対し、魂の絵は窓の外側、顔の側に置かれる。"),
    ("material", "MAT-LIT-20261024-35e8b6", "reframes", "material", "MAT-LIT-150", "レヴィナスの顔の他者性に対し、ドゥルーズは顔そのものが社会の生産物だと裏返す。"),
    ("material", "MAT-LIT-20261024-35e8b6", "echo", "material", "MAT-LIT-047", "ポール・ド・マンの「自伝は顔の剥ぎ取り」という仮面の文法を、顔貌性の理論から重ねる。"),
    ("material", "MAT-LIT-20261024-e6001d", "echo", "material", "MAT-LIT-20261024-09594e", "レヴィナス「言語は約束に先立つ応答である」とブーバーの「我—汝」は、応答が関係に先行する点で並ぶ。"),
    ("material", "MAT-LIT-20261024-e6001d", "leaves_open", "question", "Q-20261024-0e3541", "顔なき宛先が「汝」になりうるのか、ブーバーの枠の外側への適用の是非を開く。"),
    ("material", "MAT-LIT-20261024-720c50", "contrast", "material", "MAT-LIT-20261024-24afc2", "バラタのラサ（味わわれる情調）の様式化に対し、シェイクスピアは顔の常套句を否定して愛を立てる。"),
    ("material", "MAT-LIT-20261024-720c50", "echo", "material", "MAT-LIT-381", "ソネット第60番の時間論と第130番の顔論は、飾らないことで残るものを測る。"),
    ("material", "MAT-LIT-20261024-5ce9b5", "echo", "material", "MAT-LIT-20261024-d26333", "ラ・ロシュフーコーの約束の箴言と、自己愛という主人の箴言。顔つきの背後の判定者。"),
    ("material", "MAT-LIT-20261024-5ce9b5", "reframes", "material", "MAT-LIT-20261024-c95e51", "カミュ「悔悛する判事」の自己反省文体を、美徳の仮面という箴言から照らす。"),
    ("material", "MAT-LIT-20261024-9a8d57", "contrast", "material", "MAT-LIT-20261024-601c71", "テオフラストスは所作から人物を描き、ラヴァーターは顔の線から性格を読む。判定の有無が逆。"),
    ("material", "MAT-LIT-20261024-7916d0", "contrast", "material", "MAT-LIT-20261024-df045a", "ユゴーの二つの顔——彫刻された笑いの顔と、群衆に判定される顔。"),
    ("material", "MAT-LIT-20261024-7916d0", "echo", "material", "MAT-LIT-20261024-f613d8", "能『鉄輪』の面を戴く変貌と、彫刻される笑面。与えられた顔は演技に変わる。"),
    ("material", "MAT-LIT-20261024-ee1ff4", "echo", "material", "MAT-LIT-479", "顔を失っても歌が残る症例と、鏡としての顔。顔の認識と関係の経路は別に動く。"),
    ("material", "MAT-LIT-20261024-ee1ff4", "contrast", "material", "MAT-20261024-d4051b", "P博士が顔を認知できないのに対し、FaceNet は顔を128個の数値で識別する。認識の代わりの照合。"),
    ("material", "MAT-LIT-20261024-c15d4e", "echo", "material", "MAT-LIT-093", "「表現は情動を強める」と、表情の三原理。ダーウィンの別章同士を対に置く。"),
    ("material", "MAT-LIT-20261024-c15d4e", "reframes", "material", "MAT-LIT-20261024-ccd947", "赤面（第13章）を、三原理（第1–3章）の「意図されない動き」として読み直す。"),
    ("material", "MAT-20261024-5f51db", "contrast", "material", "MAT-20261024-1e22e3", "エクマンの基本情動と、バレットらの「顔から情動は推定できない」。表情論の両極。"),
    ("material", "MAT-20261024-5f51db", "echo", "material", "MAT-LIT-20261024-24afc2", "バラタのバーヴァ／ラサの分離と、表情／情動の分離は似ているが、ラサは味わいの共同性を含む。"),
    ("material", "MAT-20261024-4a595b", "reframes", "material", "MAT-20261024-3d36a5", "表情規則（誰の前で消すか）と感情労働（笑顔を売る）。抑制は文化でも商品にもなる。"),
    ("material", "MAT-20261024-4a595b", "echo", "question", "Q-20261024-94ea9e", "工場出荷時の平静さを、表情規則の一種として問う。"),
    ("material", "MAT-20261024-10002a", "contrast", "material", "MAT-20261024-5f51db", "表情は情動の窓（エクマン）か、観客への行為（フリドランド）か。"),
    ("material", "MAT-20261024-10002a", "reframes", "material", "MAT-20261024-e96797", "Cuadra ら「共感の幻想」の無差別な感情表示を、表情の社会的生態から照らす。"),
    ("material", "MAT-20261024-1e22e3", "echo", "material", "MAT-20261024-fbc9d3", "バレットの一般書と学術レビュー。情動の構成主義を二つの書式で置く。"),
    ("material", "MAT-20261024-2ecd27", "echo", "material", "MAT-LIT-093", "ダーウィンの「表情は情動を強める」の実験的後継として置く。"),
    ("material", "MAT-20261024-2ecd27", "responds_to", "material", "MAT-20261024-d98438", "追試失敗が、元の実験へ返した応答。"),
    ("material", "MAT-20261024-d98438", "interrupts", "material", "MAT-20261024-2ecd27", "事前登録追試が元の効果を中断する。実験の顔は繰り返しで変わる。"),
    ("material", "MAT-20261024-d98438", "echo", "motif", "MOTIF-016", "訂正と抹消の糸に、再現性の訂正を載せる。"),
    ("material", "MAT-20261024-bc7bc4", "echo", "question", "Q-20261024-d4c6b6", "視線の監視（パノプティコン）の問いに、視線を読む経路の発達を返す。"),
    ("material", "MAT-20261024-bc7bc4", "contrast", "material", "MAT-LIT-20261024-1ac778", "視線を読む心読に対し、出エジプト記の神は顔を見せない。読みの経路の外側の応答。"),
    ("material", "MAT-20261024-3d36a5", "echo", "material", "MAT-LIT-20261024-1261a1", "太宰『人間失格』の「演技が習慣になる」と、感情労働の表情管理。"),
    ("material", "MAT-20261024-3d36a5", "reframes", "motif", "MOTIF-012", "労働と負債の糸に、売られる表情を接続する。"),
    ("material", "MAT-LIT-20261024-df045a", "echo", "material", "MAT-LIT-20261024-d5d675", "作田の「公恥」と、群衆が判定するカジモドの顔。判定は顔にではなく群衆に宿る。"),
    ("material", "MAT-LIT-20261024-601c71", "interrupts", "material", "MAT-LIT-20261024-03e713", "「人間愛」から始まった人相学が、犯罪人の判定へ流れていく線を断ち切るように並べる。"),
    ("material", "MAT-LIT-20261024-03e713", "echo", "material", "MAT-20261024-06a60a", "ロンブローソの頭蓋計測と、顔写真からの犯罪性推定。道具だけが新しくなる。"),
    ("material", "MAT-LIT-20261024-03e713", "contrast", "material", "MAT-20261024-ddab1a", "人相学の主張と、その再演への批判。対で置かないと片方が残る。"),
    ("material", "MAT-LIT-20261024-5fa9c8", "echo", "motif", "MOTIF-20261024-f19932", "署名（手の残る字）に対し、ファユーム肖像（顔の残る記録）。残る器官の違い。"),
    ("material", "MAT-LIT-20261024-e37ce2", "echo", "question", "Q-20261024-b2f8e4", "鏡の問いに、鏡のなかの王夫妻という顔の配置で応える。"),
    ("material", "MAT-LIT-20261024-e37ce2", "reframes", "motif", "MOTIF-20261024-c9d4e1", "光と影の糸に、見る側の空席という顔の問題を重ねる。"),
    ("material", "MAT-LIT-20261024-e6b325", "echo", "material", "MAT-LIT-20261024-e37ce2", "ベラスケスのずれる視線と、モナ・リザの移ろう微笑。顔の読みは見る側で起きる。"),
    ("material", "MAT-LIT-20261024-9110c0", "echo", "motif", "MOTIF-002", "連続と断絶の糸に、描くたびに変わる自画像を置く。同一の顔と同一の自己は別。"),
    ("material", "MAT-LIT-20261024-9110c0", "contrast", "material", "MAT-20261024-d4051b", "自画像の列は変化を残し、FaceNet は変化を距離に畳む。"),
    ("material", "MAT-20261024-09d066", "echo", "motif", "MOTIF-20261024-f19932", "顔写真の制度は、署名セッションの印鑑登録と対になる身元の制度。"),
    ("material", "MAT-20261024-09d066", "reframes", "question", "Q-20261024-ed38e6", "顔が鍵になることと、鍵が複製できることは同時に来る。"),
    ("material", "MAT-LIT-20261024-c0c8e7", "contrast", "material", "MAT-LIT-061", "「複製技術時代」のアウラ論と、「写真小史」のまなざし論。別篇のベンヤミン。"),
    ("material", "MAT-LIT-20261024-c0c8e7", "echo", "material", "MAT-LIT-062", "バルト『明室』の「それはかつてあった」と、ベンヤミンの「最後のまなざし」。写真の顔の時間。"),
    ("material", "MAT-LIT-20261024-78b6f2", "echo", "material", "MAT-LIT-20261024-afbbb2", "祖母の外套（着る者の不在）と祖母の顔（初めて見る老い）。喪の二つの形式。"),
    ("material", "MAT-LIT-20261024-78b6f2", "reframes", "material", "MAT-LIT-20261024-53efc0", "三島『豊饒の海』の「同じ顔で生まれ変わる」と対に、プルーストは同じ顔がずれる場面を置く。"),
    ("material", "MAT-20261024-d4051b", "reframes", "motif", "MOTIF-20261024-04bb31", "愛・かけがえのなさの「彼が彼だったから」を、128次元の距離は測れない。"),
    ("material", "MAT-20261024-ec110b", "echo", "material", "MAT-LIT-20261024-53efc0", "同じ顔が生まれ変わる物語と、存在しない顔の量産。顔の反復の二形式。"),
    ("material", "MAT-20261024-ec110b", "reframes", "motif", "MOTIF-002", "連続と断絶の糸に、複製可能な顔を接続する。"),
    ("material", "MAT-20261024-0d01dd", "echo", "material", "MAT-EVD-20261024-118", "Gender Shades は精度の偏りを測り、Clearview は集められた顔の来歴を問う。"),
    ("material", "MAT-20261024-0d01dd", "contrast", "material", "MAT-LIT-20261024-5fa9c8", "死者に貼られた顔（ファユーム）と、生者の顔を総取りする照合（Clearview）。残し方の逆。"),
    ("material", "MAT-20261024-06a60a", "echo", "material", "MAT-LIT-20261024-03e713", "人相学の21世紀版。"),
    ("material", "MAT-20261024-06a60a", "interrupts", "material", "MAT-20261024-ddab1a", "「Physiognomy's New Clothes」が、犯罪性推定の主張を中断する。"),
    ("material", "MAT-20261024-ddab1a", "reframes", "motif", "MOTIF-20261024-71dfe0", "裁きの席の糸に、顔からの判定という裁きを接続する。"),
    ("material", "MAT-20261024-6bd007", "echo", "material", "MAT-20261024-ddab1a", "顔からの属性推定への批判の系譜に置く。"),
    ("material", "MAT-20261024-6bd007", "leaves_open", "question", "Q-20261024-a26f22", "「見分け」の語彙が顔の用途のすべてなのかどうかを、判定の系譜の前で開く。"),
    ("material", "MAT-20261024-8cd64e", "echo", "material", "MAT-20261024-ce368a", "C2PA の来歴シールは、ディープフェイクが壊した真贋の信頼への処方。"),
    ("material", "MAT-20261024-8cd64e", "reframes", "motif", "MOTIF-016", "訂正と抹消の糸に、捏造される顔を接続する。"),
    ("material", "MAT-20261024-6a005b", "echo", "material", "MAT-EVD-20261023-d2a7", "Nass & Moon が人間は機械にも社会的礼儀を使うと言うのに対し、ファルマンは機械の通信に顔を最初に足した。"),
    ("material", "MAT-20261024-6a005b", "reframes", "motif", "MOTIF-004", "声と帰属の糸に、三文字の顔が声の調子を引き受ける場面を置く。"),
    ("material", "MAT-LIT-20261024-1ac778", "contrast", "material", "MAT-LIT-20261024-4ee871", "顔が禁を先行して言う（レヴィナス）と、顔を見せてはならない（出エジプト記）。顔の倫理と顔の神学。"),
    ("material", "MAT-LIT-20261024-1ac778", "reframes", "motif", "MOTIF-20261024-7a3e51", "祈りの糸に、見られない顔への祈りを接続する。"),
    ("material", "MAT-LIT-20261024-773f42", "echo", "motif", "MOTIF-022", "死と弔いの糸に、見られる顔の死を置く。"),
    ("material", "MAT-LIT-20261024-773f42", "contrast", "material", "MAT-LIT-20261024-78b6f2", "タッジオの顔は応答せず、祖母の顔は認識の喪失を生む。見られる顔と出会う顔。"),
    ("material", "MAT-LIT-20261024-c1a377", "echo", "question", "Q-20261024-b2f8e4", "鏡の問いに、顔を変える鏡の物語を返す。"),
    ("material", "MAT-LIT-20261024-c1a377", "reframes", "motif", "MOTIF-20261024-c9d4e1", "鏡（監査スクリプト）が書庫の顔を変えていないかという問いへ接続する。"),
    ("material", "MAT-LIT-20261024-d31236", "echo", "motif", "MOTIF-002", "もう一人の自分（ドッペルゲンガー）は、記録を読み返すもう一人の語り手の影。"),
    ("material", "MAT-LIT-20261024-d31236", "reframes", "motif", "MOTIF-20261024-d2999b", "訂正の宛先の糸に、自分に追われる訂正を置く。"),
    ("material", "MAT-20261024-79c20b", "echo", "material", "MAT-20261024-5bdeb9", "キズメットの顔設計と不気味の谷は、機械の顔の設計論の両端。"),
    ("material", "MAT-20261024-79c20b", "reframes", "question", "Q-20261024-796438", "書庫が顔を獲得するときの距離の問いへ接続する。"),
    ("material", "MAT-20261024-5bdeb9", "echo", "material", "MAT-EVD-20261023-d2a7", "人は機械に礼儀を使う（Nass & Moon）から、機械の顔は人間の読みの経路に作られる。"),
    ("material", "MAT-LIT-20261024-1921d2", "contrast", "material", "MAT-LIT-20261024-601c71", "形を欠いた者に人が集まる（荘子）と、顔の線から性格を読む（ラヴァーター）。人相の否定と肯定。"),
    ("material", "MAT-LIT-20261024-1921d2", "echo", "material", "MAT-LIT-012", "『荘子』齊物論の胡蝶の夢と、徳充符の兀者。形と真の問いの別篇。"),
    ("material", "MAT-LIT-20261024-3c9e24", "echo", "material", "MAT-LIT-20261024-649c78", "『クララとお日さま』のAIの目と、『わたしを離さないで』の複製される顔。イシグロの二つの書庫。"),
    ("material", "MAT-LIT-20261024-3c9e24", "reframes", "motif", "MOTIF-022", "死と弔いの糸に、未来が割り当てられた顔を接続する。"),
    ("material", "MAT-TRC-20261024-face", "echo", "material", "MAT-TRC-20261024-passion", "感嘆符0の監査（情動）と表情0の監査（顔）。書庫の計測は同じ形式で不在を書く。"),
    ("material", "MAT-TRC-20261024-face", "echo", "fragment", "FRAG-20261024-957fd4", "試作後の断片を同じ鏡で数え直す対象として置く。"),
    ("fragment", "FRAG-20261024-957fd4", "responds_to", "material", "MAT-20261024-09d066", "顔写真の制度に、顔の欄のない申請書で応答する。"),
    ("fragment", "FRAG-20261024-957fd4", "echo", "fragment", "FRAG-032", "宛名に人名を置いた書簡（SESSION-028）に対し、本作は身元欄に「声」と書く。"),
    ("fragment", "FRAG-20261024-d9d18c", "responds_to", "material", "MAT-20261024-6a005b", "三文字の顔の歴史に、足すかどうかを決めない断章で応答する。"),
    ("fragment", "FRAG-20261024-d9d18c", "leaves_open", "question", "Q-20261024-796438", "顔を獲得した書庫の距離の問いを、疑問符のまま開く。"),
    ("fragment", "FRAG-20261024-d9d18c", "echo", "fragment", "FRAG-20261024-957fd4", "顔の欄のない書類と、三文字の顔の断章。対で一つの束。"),
    ("question", "Q-20261024-a26f22", "echo", "material", "MAT-TRC-20261024-face", "実測の「見分け5」を出発点に置く。"),
]

READ_SPECS = [
    # (target_type, target_id, reading, note)
    ("material", "MAT-LIT-20261024-4ee871", "interpreted", "顔が禁を先行する語りとして読み、既存の『全体性と無限』2件と対に置いた。"),
    ("material", "MAT-LIT-20261024-dcaf9b", "quoted", "「身体は魂の最良の絵」の一節を短く引いた。"),
    ("material", "MAT-LIT-20261024-35e8b6", "interpreted", "顔が社会の生産物であるという読みを、書庫の顔の不在へ接続した。"),
    ("material", "MAT-LIT-20261024-e6001d", "summarized", "我—汝関係を要約し、宛先の問いに接続した。"),
    ("material", "MAT-LIT-20261024-720c50", "quoted", "ソネット130番の冒頭二行を引いた。"),
    ("material", "MAT-LIT-20261024-5ce9b5", "summarized", "自己愛と美徳の仮面を要約した。"),
    ("material", "MAT-LIT-20261024-9a8d57", "interpreted", "所作からの人物素描を、人相学への対照として読んだ。"),
    ("material", "MAT-LIT-20261024-7916d0", "interpreted", "彫刻される顔を、与えられた語り手の型の比喩に接続しかけ、制動をかけた。"),
    ("material", "MAT-LIT-20261024-ee1ff4", "interpreted", "顔失認の症例を、顔と関係の経路の分離として読んだ。"),
    ("material", "MAT-LIT-20261024-c15d4e", "interpreted", "表情の三原理を、既存のダーウィン2件の前提章として読み直した。"),
    ("material", "MAT-20261024-5f51db", "interpreted", "基本情動説を、対抗理論と対で置いた。"),
    ("material", "MAT-20261024-4a595b", "interpreted", "表情規則を、工場出荷時の平静さの問いに接続した。"),
    ("material", "MAT-20261024-10002a", "interpreted", "微笑を社会的行為として読む理論を、書庫の丁寧さの問いに重ねた。"),
    ("material", "MAT-20261024-1e22e3", "interpreted", "表情から情動を推定できないというレビューを、正直な書庫の問いに接続した。"),
    ("material", "MAT-20261024-2ecd27", "summarized", "ペン実験を要約し、追試失敗と対に置いた。"),
    ("material", "MAT-20261024-d98438", "interpreted", "追試失敗を、測定の顔が繰り返しで変わる例として読んだ。"),
    ("material", "MAT-20261024-bc7bc4", "interpreted", "視線を読む経路を、顔なき書庫の応答の問いに接続した。"),
    ("material", "MAT-20261024-3d36a5", "interpreted", "売られる表情を、労働と負債の糸に接続した。"),
    ("material", "MAT-LIT-20261024-df045a", "interpreted", "顔の判定が群衆の側に宿る場面として読んだ。"),
    ("material", "MAT-LIT-20261024-601c71", "interpreted", "人相学の二重性（愛と序列）を、精読の方法へ照り返した。"),
    ("material", "MAT-LIT-20261024-03e713", "interpreted", "判定の暴力の資料として読んだ。主張を事実として紹介しない。"),
    ("material", "MAT-LIT-20261024-5fa9c8", "interpreted", "顔の残る記録として、署名の糸に対置した。"),
    ("material", "MAT-LIT-20261024-e37ce2", "interpreted", "視線のずれを、鏡の問いに接続した。"),
    ("material", "MAT-LIT-20261024-e6b325", "interpreted", "微笑の知覚を、読者の視線で生じる調子に重ねた。"),
    ("material", "MAT-LIT-20261024-9110c0", "interpreted", "自画像の列を、連続と断絶の糸に置いた。"),
    ("material", "MAT-20261024-09d066", "interpreted", "顔写真の制度化を、身元の鍵の成立として読んだ。"),
    ("material", "MAT-LIT-20261024-c0c8e7", "interpreted", "写真小史のまなざしを、既存のベンヤミン2件と区別して置いた。"),
    ("material", "MAT-LIT-20261024-78b6f2", "interpreted", "祖母の顔の再認識を、喪のもう一つの形式として読んだ。"),
    ("material", "MAT-20261024-d4051b", "summarized", "FaceNet を要約し、かけがえのなさの糸に接続した。"),
    ("material", "MAT-20261024-ec110b", "interpreted", "存在しない顔の量産を、顔の反復の新しい形式として読んだ。"),
    ("material", "MAT-20261024-0d01dd", "summarized", "Clearview の来歴の問題を要約した。"),
    ("material", "MAT-20261024-06a60a", "contested", "人相学の再演として批判の対象として扱った。"),
    ("material", "MAT-20261024-ddab1a", "interpreted", "批判の側を、顔からの判定の系譜を閉じる資料として読んだ。"),
    ("material", "MAT-20261024-6bd007", "contested", "論争的で危険な適用を含むため、批判的に扱った。"),
    ("material", "MAT-20261024-8cd64e", "summarized", "ディープフェイクの問題設定を要約し、C2PA と対に置いた。"),
    ("material", "MAT-20261024-6a005b", "quoted", "ファルマンの原投稿を短く引いた（CMU 保存ページで照合）。"),
    ("material", "MAT-LIT-20261024-1ac778", "quoted", "出エジプト記33章の KJV を短く引いた。"),
    ("material", "MAT-LIT-20261024-773f42", "interpreted", "見られる顔の死を、応答しない宛先として読んだ。"),
    ("material", "MAT-LIT-20261024-c1a377", "interpreted", "顔を変える鏡を、監査スクリプトの自己適用の問いに重ねた。"),
    ("material", "MAT-LIT-20261024-d31236", "interpreted", "もう一人の自分を、記録を読み返す語り手の影として読んだ。"),
    ("material", "MAT-20261024-79c20b", "interpreted", "不気味の谷を、書庫の顔獲得の距離の問いに接続した。"),
    ("material", "MAT-20261024-5bdeb9", "interpreted", "機械の顔が人間の読みの経路に作られることを、擬人化の制動と併記した。"),
    ("material", "MAT-LIT-20261024-1921d2", "interpreted", "形を欠いた者に人が集まる寓話を、人相学への対照として読んだ。"),
    ("material", "MAT-LIT-20261024-3c9e24", "interpreted", "複製される顔を、存続の保証の不在として読んだ。"),
    ("material", "MAT-TRC-20261024-face", "counted", "face_audit.py の出力を資料と同じ層で読み直した。"),
    # 既存資料の読み直し
    ("material", "MAT-LIT-150", "reinterpreted", "既存の顔の定義を、対話篇の語りと対で読み直した。"),
    ("material", "MAT-LIT-491", "reinterpreted", "顔の現れの記述を、本束の起点として読み直した。"),
    ("material", "MAT-LIT-20261024-476a57", "used_as_context", "サルトルのまなざしを、顔の束の文脈として参照した。"),
    ("material", "MAT-LIT-20261024-ccd947", "used_as_context", "ダーウィンの赤面を、三原理の束の文脈として参照した。"),
    ("material", "MAT-20261024-fbc9d3", "used_as_context", "バレットの一般書を、学術レビューの文脈として参照した。"),
    ("material", "MAT-LIT-20261024-c05c0f", "reinterpreted", "ゴフマンのフェイス・ワークを、顔（face）と面目（face）の語義の重なりとして読み直した。"),
    ("material", "MAT-LIT-479", "used_as_context", "ウィニコットの鏡の顔を文脈として参照した。"),
    ("material", "MAT-EVD-20261024-118", "used_as_context", "Gender Shades を、顔認識の偏りの文脈として参照した。"),
    ("material", "MAT-20261024-ce368a", "used_as_context", "C2PA を、真贋の来歴の文脈として参照した。"),
    ("material", "MAT-EVD-20261023-d2a7", "used_as_context", "Nass & Moon を、機械への礼儀の文脈として参照した。"),
    ("material", "MAT-LIT-20261024-649c78", "used_as_context", "『クララとお日さま』を、イシグロのもう一つの顔の文脈として参照した。"),
    ("material", "MAT-LIT-20261024-53efc0", "used_as_context", "『豊饒の海』の顔の反復を文脈として参照した。"),
    ("material", "MAT-LIT-20261024-afbbb2", "used_as_context", "祖母の外套を、喪の形式の対として参照した。"),
    ("material", "MAT-LIT-047", "used_as_context", "ド・マンの顔の剥ぎ取りを文脈として参照した。"),
    ("material", "MAT-TRC-20261024-passion", "used_as_context", "情動の監査の形式を、顔の監査の文脈として参照した。"),
    # 問い・モチーフ・断片
    ("question", "Q-002", "used_as_context", "主題の問い（記録を読み直して再開するAIの自己）を文脈として選んだ。"),
    ("question", "Q-052", "used_as_context", "宛先の問いを文脈として参照した。"),
    ("question", "Q-20261024-b2f8e4", "used_as_context", "鏡の問いを文脈として参照した。"),
    ("question", "Q-20261024-d4c6b6", "used_as_context", "凝視の問いを文脈として参照した。"),
    ("question", "Q-20261024-1334c5", "used_as_context", "赤面の問いを、表情規則の問いの文脈として参照した。"),
    ("motif", "MOTIF-003", "used_as_context", "身体と不在の糸を文脈として参照した。"),
    ("motif", "MOTIF-018", "used_as_context", "知覚と媒体の糸を文脈として参照した。"),
    ("motif", "MOTIF-20261024-f19932", "used_as_context", "署名の糸（前セッション）を文脈として参照した。"),
    ("fragment", "FRAG-032", "reinterpreted", "宛名に人名を置いた書簡を、顔の欄のない申請書の対として読み直した。"),
    ("fragment", "FRAG-027", "used_as_context", "仮面の語を持つ唯一の既存断片を文脈として参照した。"),
    ("fragment", "FRAG-20261024-4ea9d2", "used_as_context", "眼差しの語を持つ断片を文脈として参照した。"),
    ("session", SESSION_ID, "summarized", "本セッションの精読報告を作成した。"),
]

CONTEXT_EXISTING = [
    "MAT-LIT-150", "MAT-LIT-491", "MAT-LIT-20261024-476a57", "MAT-LIT-20261024-ccd947",
    "MAT-20261024-fbc9d3", "MAT-LIT-20261024-c05c0f", "MAT-LIT-479",
    "MAT-EVD-20261024-118", "MAT-20261024-ce368a", "MAT-EVD-20261023-d2a7",
    "MAT-LIT-20261024-649c78", "MAT-LIT-20261024-53efc0", "MAT-LIT-20261024-afbbb2",
    "MAT-LIT-047", "MAT-TRC-20261024-passion",
]


def main() -> int:
    shards = {name: shard(name) for name in
              ["materials", "motifs", "questions", "fragments", "relations", "read_log", "sessions"]}
    print("shards:", {k: str(v) for k, v in shards.items()})

    materials = build_materials()
    assert len(materials) == 45, len(materials)
    jdump(shards["materials"], materials)
    print("materials:", len(materials))

    jdump(shards["motifs"], [MOTIF])
    jdump(shards["questions"], NEW_QUESTIONS)
    jdump(shards["fragments"], FRAGMENTS)

    rels = [
        _rel(f"REL-20261024-{rid:06x}" if False else REL_IDS[i], *spec)
        for i, spec in enumerate(REL_SPECS)
    ]
    assert len(REL_SPECS) <= len(REL_IDS), (len(REL_SPECS), len(REL_IDS))
    jdump(shards["relations"], rels)
    print("relations:", len(rels))

    reads = []
    for i, (ttype, tid, reading, note) in enumerate(READ_SPECS):
        reads.append({
            "read_id": READ_IDS[i],
            "session_id": SESSION_ID,
            "target": {"type": ttype, "id": tid},
            "reading": reading,
            "note": note,
            "created_at": TODAY,
        })
    assert len(READ_SPECS) <= len(READ_IDS)
    jdump(shards["read_log"], reads)
    print("reads:", len(reads))

    session = {
        "session_id": SESSION_ID,
        "started_at": TODAY,
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
            "一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
            "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」"
        ),
        "question_ids": ["Q-002", "Q-052", "Q-20261024-b2f8e4", "Q-20261024-d4c6b6", "Q-20261024-1334c5"] + list(NEW_QA),
        "context_material_ids": [s["material_id"] for s in D.MATERIAL_SPECS] + CONTEXT_EXISTING,
        "produced_fragment_ids": [f["fragment_id"] for f in FRAGMENTS],
        "new_question_ids": list(NEW_QA),
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent (SESSION-20261024-a03d99)",
        "notes": (
            "空白候補3件（A：顔・表情・仮面、B：戦争・暴力・平和、C：秘密・嘘・暗号）を断片79編の実測で比較し、"
            "前セッション（SESSION-20261024-5a27f6）が先送りしたC：顔を、断片側の表情0・モチーフ不在という理由で採った。"
            "新設の第35の鏡 tools/face_audit.py でベースラインを測り（MAT-TRC-20261024-face）、"
            "外部44件＋運用痕跡1件の計45件（literary_text 25・research_excerpt 19・project_trace 1、"
            "verified 6・partially_verified 39・unverified 0）を5束に分けて全件四層精読した。"
            "うち5件（ファルマン、FaceNet、StyleGAN、Wu & Zhang、Physiognomy's New Clothes）は Web 検索で一次資料まで照合。"
            "重複点検でモンテーニュ『悔い改めについて』とリルケ『ドゥイノの哀歌』第1歌・エクマン実験の既存収蔵を避け、"
            "ユゴー『笑面人』と乱歩「鏡地獄」へ差し替えた。"
            f"詳細は {REPORT}。"
        ),
    }
    jdump(shards["sessions"], [session])
    print("session:", SESSION_ID)
    return 0


REL_IDS = [
    "REL-20261024-be6e02", "REL-20261024-d1c4ab", "REL-20261024-b66fca", "REL-20261024-1b58d7",
    "REL-20261024-f4c46f", "REL-20261024-2bf3fa", "REL-20261024-ee83bb", "REL-20261024-b338b4",
    "REL-20261024-d4e1f2", "REL-20261024-171417", "REL-20261024-5bdf5d", "REL-20261024-503f92",
    "REL-20261024-d8321f", "REL-20261024-73b2da", "REL-20261024-fd3e29", "REL-20261024-36c9c4",
    "REL-20261024-771461", "REL-20261024-ed797c", "REL-20261024-38eb67", "REL-20261024-a1d83d",
    "REL-20261024-c5d63e", "REL-20261024-cc35c9", "REL-20261024-5db616", "REL-20261024-286fd5",
    "REL-20261024-5d2de1", "REL-20261024-721049", "REL-20261024-b60081", "REL-20261024-95afec",
    "REL-20261024-b1c8cb", "REL-20261024-0f1118", "REL-20261024-f7b1cb", "REL-20261024-3226fe",
    "REL-20261024-dffb48", "REL-20261024-41f20a", "REL-20261024-3ae206", "REL-20261024-0f51e2",
    "REL-20261024-8c4723", "REL-20261024-0e02b3", "REL-20261024-878341", "REL-20261024-546b7b",
    "REL-20261024-3c6728", "REL-20261024-1e5ec2", "REL-20261024-97c089", "REL-20261024-6b0fbe",
    "REL-20261024-55d886", "REL-20261024-db009c", "REL-20261024-08a04a", "REL-20261024-a9d622",
    "REL-20261024-b1d2ed", "REL-20261024-0ad378", "REL-20261024-c9e655", "REL-20261024-381484",
    "REL-20261024-c15cbf", "REL-20261024-d99662", "REL-20261024-c5031b", "REL-20261024-56f033",
    "REL-20261024-67f4ae", "REL-20261024-49eb09", "REL-20261024-1d351a", "REL-20261024-c0badf",
    "REL-20261024-683a87", "REL-20261024-8ee671", "REL-20261024-e10a9e", "REL-20261024-db838c",
    "REL-20261024-da7023", "REL-20261024-aaac12", "REL-20261024-dd7311", "REL-20261024-d78208",
    "REL-20261024-e8ef2d", "REL-20261024-dcc950", "REL-20261024-26f32a", "REL-20261024-6ee5a2",
    "REL-20261024-5f842b", "REL-20261024-4665e1", "REL-20261024-309de7", "REL-20261024-9d69c1",
    "REL-20261024-592266", "REL-20261024-32db85", "REL-20261024-c73e23", "REL-20261024-b18557",
    "REL-20261024-a9561b", "REL-20261024-fdb397", "REL-20261024-9d6983", "REL-20261024-86d435",
    "REL-20261024-9cfb82", "REL-20261024-b82653", "REL-20261024-41131d", "REL-20261024-6efcef",
    "REL-20261024-455fcb", "REL-20261024-02ce7a",
]

READ_IDS = [
    "READ-20261024-fecc3c", "READ-20261024-d8f3ed", "READ-20261024-d23a28", "READ-20261024-4687d5",
    "READ-20261024-072f1c", "READ-20261024-a1e7ed", "READ-20261024-faceb8", "READ-20261024-bf4597",
    "READ-20261024-781183", "READ-20261024-ca40a0", "READ-20261024-af68d6", "READ-20261024-209f51",
    "READ-20261024-372011", "READ-20261024-429711", "READ-20261024-1942d6", "READ-20261024-d0f824",
    "READ-20261024-2b188c", "READ-20261024-f23b5d", "READ-20261024-cefbed", "READ-20261024-b0cb8d",
    "READ-20261024-b57a6c", "READ-20261024-04e15c", "READ-20261024-3e9053", "READ-20261024-e0fb2b",
    "READ-20261024-c2fc13", "READ-20261024-14e038", "READ-20261024-3a6eb6", "READ-20261024-60dabd",
    "READ-20261024-32a557", "READ-20261024-ffc374", "READ-20261024-c9e547", "READ-20261024-b61f95",
    "READ-20261024-b2e26f", "READ-20261024-dec99d", "READ-20261024-67f816", "READ-20261024-bb5e16",
    "READ-20261024-89605f", "READ-20261024-987ef6", "READ-20261024-e84138", "READ-20261024-5c18bf",
    "READ-20261024-128886", "READ-20261024-be05bb", "READ-20261024-ef3b4e", "READ-20261024-69ec9f",
    "READ-20261024-ddcae9", "READ-20261024-d7094f", "READ-20261024-437fae", "READ-20261024-6097d5",
    "READ-20261024-cf9802", "READ-20261024-cd7139", "READ-20261024-b6ad8d", "READ-20261024-7e2021",
    "READ-20261024-e3fa17", "READ-20261024-e16399", "READ-20261024-7f7e8d", "READ-20261024-7f3e7a",
    "READ-20261024-74003f", "READ-20261024-8c9f84", "READ-20261024-a5fcff", "READ-20261024-987999",
    "READ-20261024-86a594", "READ-20261024-f056c7", "READ-20261024-44d875", "READ-20261024-2dbcff",
    "READ-20261024-051570", "READ-20261024-f0ad3f", "READ-20261024-746f0d", "READ-20261024-d0bb25",
    "READ-20261024-744850", "READ-20261024-41d98a", "READ-20261024-5a8472", "READ-20261024-2b4230",
    "READ-20261024-f0f736", "READ-20261024-d09cba", "READ-20261024-feb25e", "READ-20261024-e32278",
    "READ-20261024-06fefb", "READ-20261024-854314", "READ-20261024-392927", "READ-20261024-5949ea",
    "READ-20261024-9162fc", "READ-20261024-f73ccb", "READ-20261024-7714e0", "READ-20261024-cf20f5",
    "READ-20261024-c63122", "READ-20261024-4edce8", "READ-20261024-008d14", "READ-20261024-8354fb",
    "READ-20261024-7822d6", "READ-20261024-3ae888", "READ-20261024-a22244", "READ-20261024-a33e20",
    "READ-20261024-9ad46b", "READ-20261024-b2b0c2", "READ-20261024-096234", "READ-20261024-aee656",
    "READ-20261024-d3a794", "READ-20261024-541951", "READ-20261024-8f6d51", "READ-20261024-46e8ee",
]

if __name__ == "__main__":
    raise SystemExit(main())
