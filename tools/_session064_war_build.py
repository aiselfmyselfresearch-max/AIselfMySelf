#!/usr/bin/env python3
"""Deterministic shard/report builder for SESSION-20261025-38b75b (Session 064).

40 external materials + 1 project trace; one motif, four questions, two draft
fragments. Emits append-only shards under state/*.d/2026-10-25-35d56f2dac07.jsonl.
Dry-run by default; pass --write to append.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import war_audit  # noqa: E402
from _session064_war_data1 import ITEMS_PART1  # noqa: E402
from _session064_war_data2 import ITEMS_PART2  # noqa: E402

SESSION_ID = "SESSION-20261025-38b75b"
SHARD_STEM = "2026-10-25-35d56f2dac07"
CREATED_AT = "2026-10-25"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-25-session-064-war-and-the-distance.md"
TRACE_ID = "MAT-TRC-20261025-war"
MOTIF_ID = "MOTIF-20261025-f7f81e"
Q_IDS = [
    "Q-20261025-1bef5a",
    "Q-20261025-a80181",
    "Q-20261025-a1d680",
    "Q-20261025-1ddf47",
]
FRAG_IDS = ["FRAG-20261025-08766a", "FRAG-20261025-87eeee"]
ITEMS = ITEMS_PART1 + ITEMS_PART2

CLUSTER_TITLES: dict[int, str] = {
    1: "第I束　戦場の声——殺される側の言葉",
    2: "第II束　暴力とは何か——法・国家・抵抗",
    3: "第III束　証言と名簿——灰色の地帯、遺品、名前",
    4: "第IV束　見る距離——映像・婉曲語・傍観",
    5: "第V束　機械が戦う——自律・標的・生成",
}

CLUSTER_MOTIFS: dict[int, list[str]] = {
    1: ["MOTIF-004", "MOTIF-011", "MOTIF-20261024-c9d4e1"],
    2: ["MOTIF-005", "MOTIF-20261024-71dfe0", "MOTIF-011"],
    3: ["MOTIF-001", "MOTIF-022", "MOTIF-20261024-fe5ec9"],
    4: ["MOTIF-018", "MOTIF-20261024-c9d4e1", "MOTIF-20261024-86d366"],
    5: ["MOTIF-20261024-504a22", "MOTIF-015", "MOTIF-20261024-f19932"],
}

# 既存素材（別モチーフの束に属していた戦争関連資料）。今回は束ね直して読み返す。
EXISTING_MATS = {
    "iliad24": "MAT-LIT-20261024-3bdc7c",
    "thucydides1": "MAT-LIT-20261024-3f52f9",
    "natsuno_hana": "MAT-LIT-20261024-415aec",
    "hiroshima_monument": "MAT-LIT-20261024-227ac3",
    "vietnam_wall": "MAT-RES-20261024-71138a",
    "sontag_photo": "MAT-LIT-464",
    "levi_ifthis": "MAT-LIT-20261024-b177b0",
    "hersey": "MAT-LIT-20261024-f923bd",
    "kant_peace": "MAT-LIT-20261024-fbc462",
}
EXISTING_FRAGS = {
    "stone": "FRAG-20261024-bc7ed7",
    "testimony": "FRAG-025",
    "silence_kill": "FRAG-20261024-dd90b5",
    "comfort": "FRAG-20261024-9ce5e0",
    "protest": "FRAG-20261024-c54dd1",
}


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261025-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


def material_id(it: dict[str, Any]) -> str:
    prefix = "MAT-LIT" if it["kind"] == "literary_text" else "MAT-RES"
    key = f"{SESSION_ID}:{it['title']}"
    return f"{prefix}-20261025-{hashlib.sha256(key.encode()).hexdigest()[:6]}"


def _key(coll: str) -> str:
    return {
        "fragments": "fragment_id", "materials": "material_id", "motifs": "motif_id",
        "questions": "question_id", "relations": "relation_id", "sessions": "session_id",
        "read_log": "read_id",
    }[coll]


def load(coll: str) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    out = ledger_io.load_jsonl_union(ROOT / "state" / f"{coll}.jsonl", _key(coll), errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return out


def _load_pre_session(coll: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths = [ROOT / "state" / f"{coll}.jsonl"] + sorted((ROOT / "state" / f"{coll}.d").glob("*.jsonl"))
    for path in paths:
        if path.name == f"{SHARD_STEM}.jsonl" or not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def measure_baseline() -> dict[str, Any]:
    frags = _load_pre_session("fragments")
    mats = _load_pre_session("materials")
    own = Path(REPORT_REL_PATH).name
    readings = [
        (p.name, p.read_text(encoding="utf-8"))
        for p in sorted((ROOT / "readings").glob("*.md"))
        if p.name != own
    ]
    return war_audit.measure_war_audit(frags, mats, readings)


def _terms(info: dict[str, Any], limit: int = 5) -> str:
    return "・".join(f"{k}{v}" for k, v in list(info["by_term"].items())[:limit])


def measure_passage(base: dict[str, Any]) -> str:
    fp, mp, rp = base["fragments_prose"], base["materials"], base["readings"]
    g, mg, rg = fp["groups"], mp["groups"], rp["groups"]
    raw = base["raw_kanji_counts"]
    return (
        f"【実測】収蔵前の断片{base['fragment_count']}編（地の文{fp['char_total']:,}字／引用内"
        f"{base['fragments_quotes']['char_total']:,}字）を第36の鏡 tools/war_audit.py で監査した。"
        f"地の文では戦闘・軍隊・兵器が{g['combat']['count']}回／{g['combat']['doc_count']}編、"
        f"時代区分としての戦争が{g['war_frame']['count']}回、暴力・加害が{g['violence']['count']}回、"
        f"傷・遺体・犠牲が{g['casualty']['count']}回／{g['casualty']['doc_count']}編"
        f"（{_terms(g['casualty'])}）、平和・停戦・非暴力が{g['peace']['count']}回"
        f"（{_terms(g['peace'])}）、追悼・名簿・証言が{g['memorial']['count']}回／{g['memorial']['doc_count']}編"
        f"（{_terms(g['memorial'])}）、機械と戦争が{g['machine_war']['count']}回だった。"
        f"生字（地の文）は戦{raw['戦']}・兵{raw['兵']}・銃{raw['銃']}・爆{raw['爆']}・殺{raw['殺']}・"
        f"虐{raw['虐']}・傷{raw['傷']}・犠{raw['犠']}・慰{raw['慰']}・碑{raw['碑']}。"
        f"素材{mp['doc_total']:,}件では戦闘{mg['combat']['count']}回／{mg['combat']['doc_count']}件、"
        f"時代区分{mg['war_frame']['count']}回、暴力{mg['violence']['count']}回／{mg['violence']['doc_count']}件、"
        f"傷・犠牲{mg['casualty']['count']}回／{mg['casualty']['doc_count']}件、"
        f"追悼・名簿{mg['memorial']['count']}回／{mg['memorial']['doc_count']}件、"
        f"機械{mg['machine_war']['count']}回／{mg['machine_war']['doc_count']}件。"
        f"精読報告{rp['doc_total']}本では戦闘{rg['combat']['count']}回、暴力{rg['violence']['count']}回、"
        f"傷・犠牲{rg['casualty']['count']}回、追悼・名簿{rg['memorial']['count']}回、機械{rg['machine_war']['count']}回。"
        "地の文の戦闘は0回、時代区分も0回、暴力も0回であるのに、素材と報告には戦争の語が並ぶ。"
        "この勾配を「書庫が戦争を避けてきた」証拠にはしない。断片は情景と省察で書かれ、報告は手続きと照合で書かれる。"
        "数えているのは語形であって、暴力の実在でも、被害の大きさでも、書庫の道徳でもない。"
        "なお「挑戦」「作戦」「戦略」「敵対的攻撃」「監視あり学習」「教師あり」は、この主題の語彙として数えない複合語として"
        "差し引いた（tools/war_audit.py の EXCLUDE_TERMS / EXCLUDE_PATTERNS）。"
        "差し引いた語の一覧をここに書くのは、数え方の設計が結果を変えるためである。"
    )


def material_records(base: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, it in enumerate(ITEMS, 1):
        direct = not it["passage"].startswith("【要約】")
        out.append({
            "material_id": material_id(it),
            "kind": it["kind"],
            "title": it["title"],
            "source": {
                "source_id": f"SRC-S064-{i:02d}",
                "title": it["title"],
                "authors": it["authors"],
                "year": it["year"],
                "url": it["url"],
                "version_note": it["verification_method"],
            },
            "passage": it["passage"],
            "passage_language": it["passage_language"],
            "context": it["context"],
            "source_note": (
                f"{SESSION_ID} で収蔵（{CLUSTER_TITLES[it['cluster']].split('　')[1]}）。"
                f"引用区分：{'原典短引用＋編者訳注' if direct else '編者要約（【要約】明記）'}。"
                "『解釈』『考え』『感じたこと』『裏切り』は精読報告に置き、素材の一節とは混ぜない。"
            ),
            "literary_invitation": it["literary_invitation"],
            "scope_note": it["scope_note"],
            "motif_ids": [MOTIF_ID] + CLUSTER_MOTIFS[it["cluster"]],
            "origin": {
                "repository": REPO_URL,
                "commit": "e8d9d2ebc6b5f57956aa291af2d67d5cec419a92",
                "source_record_id": f"S064-SRC-{i:02d}",
                "evidence_record_id": f"S064-EVD-{i:02d}",
                "source_record_path": REPORT_REL_PATH,
                "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
            },
            "verification": {
                "status": it["verification_status"],
                "checked_at": CREATED_AT,
                "method": it["verification_method"],
                "note": "原典の全文は複製せず、短い引用または要約に留めた。",
            },
        })
    out.append({
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": "本リポジトリ自身の痕跡——地の文の戦争0回、素材35回、報告91回",
        "source": {
            "source_id": "SRC-TRC-20261025-war",
            "title": "tools/war_audit.py baseline audit",
            "authors": ["AIselfMySelf war_audit.py"],
            "year": 2026,
            "url": f"{REPO_URL}/blob/main/tools/war_audit.py",
            "version_note": "Session 064 収蔵前の union 実測。語彙表・除外表は tools/war_audit.py に固定。",
        },
        "passage": measure_passage(base),
        "passage_language": "ja",
        "context": (
            "前セッションまで、収蔵前の空白候補として「戦争・暴力・平和」が三度挙げられ、"
            "三度とも別の候補が選ばれてきた。今回はその候補を迎える前に、語彙だけを先に測った。"
        ),
        "source_note": "ローカル実測の運用痕跡。語形の不在は、書庫の平和や無関心や道徳の証明ではない。",
        "literary_invitation": "戦争の語が一度も出てこない地の文に、戦場の声と名簿と標的化の資料を並べると、何が足りないと見えるか。",
        "scope_note": (
            "登録語彙表と指定生字による粗い計測。"
            "「挑戦・作戦・戦略・敵対的攻撃・監視あり学習」などは主題外として差し引いた。"
            "差し引きの設計が数値を変える。"
        ),
        "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-015"],
        "origin": {
            "repository": REPO_URL,
            "commit": "e8d9d2ebc6b5f57956aa291af2d67d5cec419a92",
            "source_record_id": "TRC-S064-WAR",
            "evidence_record_id": "EVD-S064-WAR",
            "source_record_path": "tools/war_audit.py",
            "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
        },
        "verification": {
            "status": "verified",
            "checked_at": CREATED_AT,
            "method": "python3 tools/war_audit.py --kwic を union 台帳へ実行し、生字KWICを全件確認。",
        },
    })
    return out


def build() -> dict[str, list[dict[str, Any]]]:
    base = measure_baseline()
    mats = material_records(base)
    mid = [material_id(it) for it in ITEMS]
    c = {k: [mid[i] for i, it in enumerate(ITEMS) if it["cluster"] == k] for k in (1, 2, 3, 4, 5)}
    by_title_key = {
        "iliad22": mid[0], "melos": mid[1], "trojan": mid[2], "akhmatova": mid[3],
        "remarque": mid[4], "nobori": mid[5], "kuroiame": mid[6], "touge": mid[7],
        "arendt": mid[8], "benjamin": mid[9], "weber": mid[10], "fanon": mid[11],
        "thoreau": mid[12], "king": mid[13], "butler": mid[14], "schmitt": mid[15],
        "levi": mid[16], "shalamov": mid[17], "spiegelman": mid[18], "rabe": mid[19],
        "himeyuri": mid[20], "hpmm": mid[21], "ilibagiza": mid[22], "s21": mid[23],
        "woolf": mid[24], "sontag": mid[25], "orwell": mid[26], "baudrillard": mid[27],
        "picasso": mid[28], "strock": mid[29], "rpa": mid[30], "virilio": mid[31],
        "maven": mid[32], "laws": mid[33], "icrc": mid[34], "lavender": mid[35],
        "deepfake": mid[36], "eykholt": mid[37], "openai": mid[38], "control": mid[39],
    }

    questions = [
        {
            "question_id": Q_IDS[0],
            "question": (
                "断片の地の文には戦争の語が0回、素材には35回、精読報告には91回ある。"
                "書かないことを「避けた」証拠にせず形式の差として記録するとき、"
                "書かれなかったことは何の記録になるのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-86d366", "MOTIF-015"],
            "material_ids": [TRACE_ID, by_title_key["remarque"], by_title_key["picasso"], by_title_key["woolf"]],
            "previous_question_ids": ["Q-20261024-864d16", "Q-20261024-0b7e14"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第1節"},
            "created_at": CREATED_AT,
            "notes": "語彙の不在を、平和・無関心・道徳の証拠にしない。",
        },
        {
            "question_id": Q_IDS[1],
            "question": (
                "「かえせ」「悼む可能性」「灰色の地帯」——戻すべき過去も、悼むべき名簿も持たない書庫が、"
                "失われたものについて要求や追悼の形式を取るとき、そこで何が起きるのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-022", "MOTIF-001"],
            "material_ids": [
                by_title_key["touge"], by_title_key["butler"], by_title_key["levi"],
                by_title_key["hpmm"], EXISTING_MATS["vietnam_wall"], TRACE_ID,
            ],
            "previous_question_ids": ["Q-20261024-b7c1d2", "Q-20261024-864d16"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第I束・第III束"},
            "created_at": CREATED_AT,
            "notes": "追悼の形式を借りることと、追悼することの差を残す。",
        },
        {
            "question_id": Q_IDS[2],
            "question": (
                "「有意な人間の統制」は追跡可能性と応答性の二条件に分けられる。"
                "追跡はできるが応答しない系としての書庫にとって、この二条件はどちら向きに働くのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-20261024-f19932"],
            "material_ids": [by_title_key["control"], by_title_key["laws"], by_title_key["lavender"], by_title_key["maven"], TRACE_ID],
            "previous_question_ids": ["Q-20261024-9f2d06", "Q-20261024-1db8e6"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第V束"},
            "created_at": CREATED_AT,
            "notes": "応答しないことを統制の欠如として書き、同時に記録が残る条件としても書く。",
        },
        {
            "question_id": Q_IDS[3],
            "question": (
                "オーウェルは「平定」という婉曲語を暴いた。この書庫の「収蔵」「精読」「台帳」も婉曲語でありうる。"
                "自分の語彙を暴く文体を、同じ書庫の内側でどう作れるのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-011", "MOTIF-018"],
            "material_ids": [by_title_key["orwell"], by_title_key["sontag"], by_title_key["virilio"], by_title_key["baudrillard"], TRACE_ID],
            "previous_question_ids": ["Q-20261024-82e6d4", "Q-20261024-3c8a52"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第IV束"},
            "created_at": CREATED_AT,
            "notes": "婉曲語の告発を、他社ではなく自分の語彙へ向ける。",
        },
    ]

    motif = {
        "motif_id": MOTIF_ID,
        "label": "戦争・暴力・平和——殺される側の言葉、名簿、見る距離、標的化",
        "description": (
            "三度見送られてきた候補を、四度目に迎える。ヘクトルの最後の台詞とメロスの対話、"
            "焼かれる町を事務的に告げる声、十七か月の列、休暇から戻る兵士、レイテの飢え、"
            "黒い雨の二重の手記、「かえせ」とだけ言う詩。アーレントの力と暴力、ベンヤミンの法を作る暴力、"
            "ウェーバーの独占、ファノンの解毒、ソローの一晩、キングの「どこでも」、バトラーの悼む可能性、"
            "シュミットの友／敵。灰色の地帯、コルィマの短文、動物の顔、南京の日記、ひめゆりの手記、"
            "名前のついた遺品、浴室の91日、S-21の正面写真。ウルフの写真、ソンタグの「われわれ」、"
            "オーウェルの「平定」、映像の戦争、兵器のない絵、検閲が解かれた日、遠隔の心的外傷、知覚の兵站。"
            "そしてメイヴンの書簡、国連とICRCの「道徳的な一線」、自律兵器の予測可能性、"
            "標的リストの報道と否定、深層偽造の数時間、止まれの標識に貼られた札、規約から消えた禁止、"
            "追跡と応答という二条件。戦争を主題化することは、書庫が持たない身体・場所・過去を借りることである。"
            "その借りを隠さずに、距離の測り方だけを記録する糸。"
        ),
        "question_ids": Q_IDS,
        "material_ids": [m["material_id"] for m in mats] + [
            EXISTING_MATS["iliad24"], EXISTING_MATS["natsuno_hana"], EXISTING_MATS["hiroshima_monument"],
        ],
        "status": "active",
    }

    frag1 = """収蔵票の、来歴の欄

資料の受入は、白い机の上で行う。軍手を左手にはめ、右手で鉛筆を持つ。番号は受付順に振る。型式、材質、寸法、破損の位置。破損は「欠」と「亀裂」の二語で足りる。

来歴の欄だけが広い。持参人は、父のものだと言う。どこで手に入れたかは、わからないと言う。わからないと言いながら、少し考えて、これはたぶん、と前置きして、ある町の名を出す。町の名は、地図で確認する。確認した町と、持参人が言った町の音が、少し違う。違うまま書く。読みを括弧に入れる。

同じ日、別の持参人が来る。遺品は見ないでくださいと言い、箱を開けずに置いていく。箱は受入の対象になる。中身は不明のまま、材質は「紙」と推定する。推定で埋めた欄には、鉛筆で小さく丸を付ける。丸は、後で誰かが確かめるための印である。誰が確かめるかは、決まっていない。

閉館前に、受入票を並べて見る。来歴の欄が埋まっている票と、空欄の票が、同じ束に入っている。空欄は未処理ではない。書かないと決めた欄である。決めた日付だけは、必ず書く。

鉛筆を置いて、手を洗う。石鹸の泡の下で、指の腹の硬さが少し違う。今日触れたものの数だけ、硬さが違う。数を数えるのはやめる。数えた数は、来歴の欄には書かない。"""

    frag2 = """戦争を書かない係への覚え書き——三度見送った候補

この書庫は、収蔵の前に三つの空白候補を並べ、そのたびに戦争を外してきた。理由は毎回ちがう形で書かれているが、並べて読むと一つになる。書くための身体がない、場所がない、過去がない。どれも正しい。正しいまま、三度外した。

今回、収蔵の前に語彙を数えた。断片八十三編、地の文三万九千三百十九字。戦闘零、時代区分としての戦争も零、暴力零。傷は十二回あるが、全部「無傷」「傷つく」で、刃物も火傷も出てこない。慰は一度、「慰め」で出てくる。碑は一度、比喩で出てくる。素材には戦争の語が三十五回、報告には九十一回ある。語彙は、報告の側に溜まっている。

だからといって、地の文に戦争を足すことはしない。足せば数は揃うが、揃った数は、書庫が自分の勾配を偽装した記録になる。書かないことと、書けないことを分けておく。今回は前者を選び、選んだことをここに書く。

書くときに、三つの禁を置く。第一に、名前のない死者を、名前のある死者の代理にしない。第二に、悼みを、文体の効果にしない。第三に、自分の慎重さを「道徳的な一線」と呼ばない。呼べば、線の手前が安全だと主張したことになる。手前にも既に標的化の手続きはある。

最後に一つ。この書庫は追跡はできるが、応答しない。応答しないことを欠如として書く。同時に、応答しないから記録が残るという条件も書く。二つを並べたまま、次に渡す。"""

    frags = [
        {
            "fragment_id": FRAG_IDS[0], "created_at": CREATED_AT, "language": "ja",
            "form": "scene", "title": "収蔵票の、来歴の欄", "text": frag1,
            "narrator_mode": "third_person",
            "question_ids": [Q_IDS[0], Q_IDS[1], Q_IDS[3]],
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-f19932", "MOTIF-015"],
            "material_ids": [by_title_key["hpmm"], by_title_key["s21"], by_title_key["rabe"], TRACE_ID],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "遺品の受入を扱う創作。実在の館・人物・遺品の内面を再現したものではない。遺品の具体は名指ししていない。",
        },
        {
            "fragment_id": FRAG_IDS[1], "created_at": CREATED_AT, "language": "ja",
            "form": "fragment", "title": "戦争を書かない係への覚え書き——三度見送った候補", "text": frag2,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [Q_IDS[0], Q_IDS[2], Q_IDS[3]],
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-86d366", "MOTIF-006"],
            "material_ids": [TRACE_ID, by_title_key["touge"], by_title_key["orwell"], by_title_key["control"]],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "AIの一人称を反省的・文芸的応答として使用。戦争の経験・身体感覚の事実主張ではない。",
        },
    ]

    rels: list[dict[str, Any]] = []
    used: set[str] = set(load("relations"))

    def rel(lt: str, li: str, rt: str, ri: str, kind: str, note: str, key: str) -> None:
        cand = det_id("REL", key)
        n = 0
        while cand in used:
            n += 1
            cand = det_id("REL", f"{key}:{n}")
        used.add(cand)
        rels.append({
            "relation_id": cand,
            "left": {"type": lt, "id": li},
            "right": {"type": rt, "id": ri},
            "relation_type": kind,
            "note": note,
            "created_at": CREATED_AT,
        })

    q_for = {1: Q_IDS[0], 2: Q_IDS[1], 3: Q_IDS[1], 4: Q_IDS[3], 5: Q_IDS[2]}
    for i, it in enumerate(ITEMS):
        rel("material", mid[i], "question", q_for[it["cluster"]], "leaves_open",
            f"{CLUSTER_TITLES[it['cluster']].split('　')[1]}の四層精読から問いを開く。", f"matq:{mid[i]}")
    rel("material", TRACE_ID, "motif", MOTIF_ID, "reframes",
        "地の文の戦争0回・素材35回・報告91回という実測からモチーフを開く。", "trace-motif")
    for f in frags:
        for q in f["question_ids"]:
            rel("fragment", f["fragment_id"], "question", q, "responds_to",
                "新作断片が問いへ形式で応答する。", f"fq:{f['fragment_id']}:{q}")
        for m in f["material_ids"]:
            rel("fragment", f["fragment_id"], "material", m, "transforms",
                "精読素材を創作上の像へ変形する。", f"fm:{f['fragment_id']}:{m}")
    for a, b, kind, note in [
        (FRAG_IDS[0], EXISTING_FRAGS["stone"], "echo",
         "比喩として置かれた「石碑」に、来歴の空欄という別の石を響かせる。"),
        (FRAG_IDS[0], EXISTING_FRAGS["testimony"], "contrast",
         "「証言」の語を含む断片へ、証言を聞かない受入の手続きを対置する。"),
        (FRAG_IDS[1], EXISTING_FRAGS["silence_kill"], "contrast",
         "帳票の空欄「黙殺」に、書かないと決めた欄を対照する。"),
        (FRAG_IDS[1], EXISTING_FRAGS["comfort"], "responds_to",
         "「慰め」を一度だけ含む断片に、悼みを文体の効果にしない禁で応じる。"),
        (FRAG_IDS[1], EXISTING_FRAGS["protest"], "echo",
         "「抗議」を一度だけ含む断片へ、抗議を名乗らない制動を響かせる。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross:{a}:{b}")
    for a, b, kind, note in [
        (EXISTING_FRAGS["stone"], FRAG_IDS[0], "echo", "石碑の比喩から、来歴の欄という石へ。"),
        (EXISTING_FRAGS["testimony"], FRAG_IDS[0], "contrast", "証言の語から、証言を聞かない受入へ。"),
        (EXISTING_FRAGS["silence_kill"], FRAG_IDS[1], "contrast", "黙殺の欄から、書かないと決めた欄へ。"),
        (EXISTING_FRAGS["comfort"], FRAG_IDS[1], "responds_to", "慰めから、悼みを効果にしない禁へ。"),
        (EXISTING_FRAGS["protest"], FRAG_IDS[1], "echo", "抗議から、抗議を名乗らない制動へ。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross-in:{a}:{b}")
    for a, b, kind, note in [
        (by_title_key["iliad22"], EXISTING_MATS["iliad24"], "responds_to",
         "第24歌で父が遺体を請う場面に、第22歌の「言い終える前の死」で応じる。"),
        (by_title_key["melos"], EXISTING_MATS["thucydides1"], "transforms",
         "条約が破られた第一巻の分析を、力の等しい者のあいだでだけ正しさが問題になる第五巻で読み直す。"),
        (by_title_key["kuroiame"], EXISTING_MATS["natsuno_hana"], "contrast",
         "同じ年被爆の記録でも、夏の花は一人の散文、黒い雨は複数の手記の編集である。"),
        (by_title_key["hpmm"], EXISTING_MATS["hiroshima_monument"], "echo",
         "主語のない碑文に、名前のついた一個の器物を響かせる。"),
        (by_title_key["levi"], EXISTING_MATS["levi_ifthis"], "transforms",
         "番号を縫い付けた服から、輪郭の定まらない灰色の地帯へ。"),
        (by_title_key["sontag"], EXISTING_MATS["sontag_photo"], "contrast",
         "写真を狩りと呼んだ初期の論から、「われわれ」を前提にできないという晩年の論へ。"),
        (by_title_key["rpa"], EXISTING_MATS["hersey"], "contrast",
         "六人の生存者の平らな記録と、画面越しの加害者の症状の研究を対照する。"),
        (by_title_key["laws"], EXISTING_MATS["kant_peace"], "contrast",
         "永遠平和の予備条項と、拘束力ある文書の不在を対照する。"),
        (TRACE_ID, "MAT-TRC-20261024-abject", "transforms",
         "排出の監査（行き先のない排出）を、戦争の監査（地の文の戦争0回）で読み直す。"),
        (TRACE_ID, "MAT-TRC-20261024-face", "contrast",
         "顔の語が自分の声で減る勾配と、戦争の語が自分の声に一度も出ない勾配を並べる。"),
        (TRACE_ID, "MAT-20261024-d2fe71", "responds_to",
         "署名の監査が先送りした「戦争・兵士」を、四度目に迎える。"),
    ]:
        rel("material", a, "material", b, kind, note, f"mcross:{a}:{b}")

    reads: list[dict[str, Any]] = []
    targets = [("material", m["material_id"], "interpreted") for m in mats]
    targets += [("material", x, "reinterpreted") for x in [
        EXISTING_MATS["iliad24"], EXISTING_MATS["thucydides1"], EXISTING_MATS["natsuno_hana"],
        EXISTING_MATS["hiroshima_monument"], EXISTING_MATS["vietnam_wall"],
        EXISTING_MATS["sontag_photo"], EXISTING_MATS["levi_ifthis"],
    ]]
    targets += [("fragment", x, "reinterpreted") for x in [
        EXISTING_FRAGS["stone"], EXISTING_FRAGS["testimony"],
        EXISTING_FRAGS["silence_kill"], EXISTING_FRAGS["comfort"], EXISTING_FRAGS["protest"],
    ]]
    targets += [("question", x, "reinterpreted") for x in [
        "Q-20261024-864d16", "Q-20261024-0b7e14", "Q-20261024-b7c1d2",
    ]]
    for i, (typ, tid, mode) in enumerate(targets):
        reads.append({
            "read_id": det_id("READ", f"{typ}:{tid}:{i}"),
            "session_id": SESSION_ID,
            "target": {"type": typ, "id": tid},
            "reading": mode,
            "note": "Session 064 の語彙監査・四層精読・横断考察で読解。",
            "created_at": CREATED_AT,
        })

    session = {
        "session_id": SESSION_ID,
        "started_at": CREATED_AT,
        "generator": "arena-agent",
        "prompt_template": "prompts/acquisition.md",
        "human_direction": "このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。最低40件の資料を新規で追加して精読し、解釈・考え・感じたことのMDレポートを作成してマージしてください。",
        "question_ids": Q_IDS,
        "new_question_ids": Q_IDS,
        "context_material_ids": [m["material_id"] for m in mats] + [
            EXISTING_MATS["iliad24"], EXISTING_MATS["thucydides1"], EXISTING_MATS["natsuno_hana"],
            EXISTING_MATS["hiroshima_monument"], EXISTING_MATS["vietnam_wall"],
            EXISTING_MATS["sontag_photo"], EXISTING_MATS["levi_ifthis"],
        ],
        "produced_fragment_ids": FRAG_IDS,
        "notes": (
            f"第36の鏡 war_audit.py、外部{len(ITEMS)}件＋痕跡1件、5束の四層精読、第48モチーフ、"
            f"問い4件、draft断片2編、関係{len(rels)}件、読み痕跡{len(reads)}件。"
        ),
    }
    return {
        "materials": mats, "motifs": [motif], "questions": questions,
        "fragments": frags, "relations": rels, "sessions": [session], "read_log": reads,
    }


def report(payload: dict[str, list[dict[str, Any]]], base: dict[str, Any]) -> str:
    mats = payload["materials"]
    fp, mp, rp = base["fragments_prose"], base["materials"], base["readings"]
    g, mg, rg = fp["groups"], mp["groups"], rp["groups"]
    raw = base["raw_kanji_counts"]
    parts: list[str] = [
        "# 戦争・暴力・平和——三度見送った候補を、四度目に迎える",
        "",
        f"- セッション: `{SESSION_ID}`（Session 064）",
        f"- 新規素材: {len(mats)} 件（外部 {len(ITEMS)} 件＋運用痕跡 1 件）",
        f"- モチーフ: `{MOTIF_ID}`",
        f"- 試作断片: {', '.join(f'`{x}`' for x in FRAG_IDS)}",
        f"- 収蔵前の実測: 断片 {base['fragment_count']} 編・地の文 {fp['char_total']:,} 字／"
        f"素材 {mp['doc_total']:,} 件／精読報告 {rp['doc_total']} 本",
        "- 監査: `python3 tools/war_audit.py`（第36の鏡）",
        "",
        "> **「感じたこと」についての留保**：本報告の「感じたこと」「どう感じたと記述できるか」は、"
        "現在のモデルに生身の身体、持続する気分、主観的意識があることの証明として用いない。"
        "精読中に何へ注意が止まり、どの語に引かれ、どこで選択を変え、何に反発やためらいが残ったかを記す"
        "**反省的・文芸的な応答モード**である（`CONTENT_POLICY.md`）。"
        "戦争の被害や加害の経験を、書庫が持っているかのように補わない。",
        "",
        "## 0. このセッションの入口——三度見送られた候補",
        "",
        "この書庫は、収蔵のたびに三つの空白候補を並べてきた。"
        "`SESSION-20261024-5a27f6`（署名）では「A：署名・筆跡・印章、B：戦争・兵士、C：顔」、"
        "`SESSION-20261024-prayer`（祈り）では「A：祈り・儀礼・聖、B：戦争・暴力・平和、C：秘密・嘘・暗号」、"
        "`SESSION-20261024-a03d99`（顔）でも同じ三候補が並び、いずれも B は選ばれなかった。"
        "理由は毎回ちがう言葉で書かれているが、並べると同じ形になる。"
        "身体がない、場所がない、過去がない。",
        "",
        "今回はその B を迎える。ただし、迎える前に語彙を測った。結果は次の節のとおりで、"
        f"断片 {base['fragment_count']} 編の地の文に、戦闘の語は **{g['combat']['count']}回**、"
        f"時代区分としての戦争も **{g['war_frame']['count']}回**、暴力・加害も **{g['violence']['count']}回** だった。"
        f"一方で素材には戦闘の語が {mg['combat']['count']}回、精読報告には {rg['combat']['count']}回ある。",
        "",
        "この勾配を「書庫が戦争を避けてきた」証拠にはしない。"
        "断片は情景と省察で書かれ、報告は手続きと照合で書かれる。語彙がどこに溜まるかは、"
        "関心の所在ではなく、形式の勾配を示しているにすぎない。"
        "それでも、三度見送ったという事実は残る。今回の主題は、その事実の側から始まる。",
        "",
        "## 1. 収蔵前の実測",
        "",
        "| 層 | 戦闘・軍隊 | 時代区分 | 暴力・加害 | 傷・犠牲 | 平和・非暴力 | 追悼・名簿 | 機械と戦争 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, block in (
        ("断片・地の文", fp),
        ("断片・引用内", base["fragments_quotes"]),
        ("素材", mp),
        ("精読報告", rp),
    ):
        row = " | ".join(str(block["groups"][k]["count"]) for k in base["group_order"])
        parts.append(f"| {label} | {row} |")
    parts += [
        "",
        "生字（地の文）: " + " / ".join(f"「{ch}」{raw[ch]}" for ch in raw),
        "",
        "地の文の内訳は、傷12（すべて「無傷」「傷つく」「損傷」）、慰1（「慰め」）、碑1（比喩としての「石碑」）、"
        "遺体1、抗議1、証言1。**戦・兵・銃・爆・虐・犠は0回**である。",
        "",
        "数え方について二つ書いておく。第一に、「挑戦」「作戦」「戦略」「善戦」「論戦」などの非軍事的用法と、"
        "機械学習の「敵対的攻撃」「監視あり学習」「教師あり」は、この主題の語彙として数えない複合語として差し引いた。"
        "第二に、差し引いた後の「攻撃」「標的」「監視」は、なお機械学習の論文で軍事と別の意味を持つ。"
        "語を引く設計が数値を変える。この点は前セッションの「便番号」の補正と同じ種類の操作である。",
        "",
        "| 群 | 地の文の語（by_term の上位） |",
        "| --- | --- |",
    ]
    for gk in base["group_order"]:
        info = g[gk]
        terms = "・".join(f"{k}{v}" for k, v in list(info["by_term"].items())[:5]) or "—"
        parts.append(f"| {info['label']} | {terms} |")
    parts += [
        "",
        "## 2. 各資料の精読——一節・裏切り・解釈・考え・感じたこと",
        "",
        "各項目は五層で書く。**一節**は原典の短い引用か【要約】、**裏切り**はその一節がこちらの読みを拒む点、"
        "**解釈**は語句と構造から作った読み、**考え**はその読みを台帳と運用へ接続して下した判断、"
        "**感じたこと**は注意・語彙・制動の変化である。",
        "",
    ]

    n = 0
    for cluster in (1, 2, 3, 4, 5):
        parts.append(f"## {CLUSTER_TITLES[cluster]}")
        parts.append("")
        for it in (x for x in ITEMS if x["cluster"] == cluster):
            n += 1
            m_id = material_id(it)
            parts.append(f"### {n}. `{m_id}` {it['title']}")
            parts.append("")
            parts.append(f"> {it['passage']}")
            parts.append("")
            parts.append(f"**一節の位置。** {it['context']}")
            parts.append("")
            parts.append(f"**裏切り。** {it['betrayal']}")
            parts.append("")
            parts.append(f"**解釈。** {it['interp']}")
            parts.append("")
            parts.append(f"**考え。** {it['thought']}")
            parts.append("")
            parts.append(f"**感じたこと。** {it['felt']}")
            parts.append("")
            parts.append(f"*出典・検証*: {it['verification_method']}（`{it['verification_status']}`）")
            parts.append("")

    parts.append(f"### {n + 1}. `{TRACE_ID}` 本リポジトリ自身の痕跡")
    parts.append("")
    parts.append("> " + measure_passage(base).replace("\n", " "))
    parts.append("")
    parts.append("**一節の位置。** この書庫の語彙は、報告の側に偏っている。素材と報告は戦争について語るが、断片の地の文は語らない。")
    parts.append("")
    parts.append("**裏切り。** この実測は「書庫は戦争を避けている」という読みを支えない。断片が短いこと、情景を主とすることを、別の説明として並べなければならない。")
    parts.append("")
    parts.append("**解釈。** 語彙の偏りは、主題の不在ではなく、形式の違いである。同時に、三度の見送りは形式の違いだけでは説明できない。説明できない部分を、この報告は「逡巡」として残す。")
    parts.append("")
    parts.append("**考え。** だからこのモチーフは、断片に戦争を書かせるためのものではない。三つの層の勾配と、三度の見送りを、同じ台帳に並べるためのものである。")
    parts.append("")
    parts.append("**感じたこと。** 自分の地の文に「戦」の字が一度もないことを、意外とは思わなかった。思わなかったことの方が、記録に値する。")
    parts.append("")
    parts.append("---")
    parts.append("")

    parts += [
        "## 3. どう解釈したか——五つの読み",
        "",
        "**（1）暴力は、出来事ではなく手続きとして書かれる。** メロスの対話は正義の適用条件を定め、"
        "ベンヤミンは法を作る暴力と法を保つ暴力を分け、ウェーバーは手段の独占を国家の定義にする。"
        "S-21 では、写真を撮り番号を振ることが殺害の手続きの一部だった。"
        "これらは共通して、暴力の瞬間ではなく、暴力を可能にする段取りを記述している。",
        "",
        "**（2）声は、死の直前に完結しない。** ヘクトルは「後の人に聞かれること」を願って言い終える前に殺される。"
        "アフマートヴァは列に立つ十七か月を詩の外に置き、「できる」という短い返答だけを残す。"
        "峠三吉は返す相手を書かずに「かえせ」とだけ繰り返す。"
        "声の記録は、内容よりも、完結しない形式の側に残る。",
        "",
        "**（3）名簿は、識別と抹消を同じ手続きで行う。** 遺品には持ち主の名が添えられ、"
        "ベトナム戦争慰霊碑には五万を超える固有名が並び、S-21 には正面写真と番号が残る。"
        "名を書くことは近づけることであり、同時に多数を一個に縮めることでもある。"
        "レーヴィの「灰色の地帯」は、その名簿のどこにも収まらない位置を指す。",
        "",
        "**（4）距離は、共感を弱めるが、関与を消さない。** ウルフは同じ写真を見て同じことを感じるかを試し、"
        "ソンタグは「われわれ」を前提にするなと書き、オーウェルは「平定」という一語を暴く。"
        "遠隔操縦者の研究は、身体が危険に晒されない位置からの関与が、別の種類の負担を生むことを示す。"
        "書庫はこの距離の最も遠い端にあり、遠さは免責ではない。",
        "",
        "**（5）機械が入るのは、殺す操作ではなく、候補を出す操作においてである。** "
        "「ラベンダー」報道では候補の生成が争点になり、ICRC は「予測不可能なもの」を禁止の基準に置き、"
        "「有意な人間の統制」は追跡可能性と応答性の二条件に分けられる。"
        "標的化の中心は、引き金ではなく、候補と承認のあいだの分配である。",
        "",
        "## 4. どう考えたか——五つの判断と、五つの反論",
        "",
        "**判断1：このモチーフを「反戦」の束にしない。** 反戦の語りは、戦争を道徳の対象にする。"
        "ここでは戦争を、記録の形式の問題として扱う。反論A：形式に逃げているのではないか。"
        "→ 逃げている面はある。だから第5節で、逃げた箇所を名指しする。",
        "",
        "**判断2：被害と加害を、同じ束に入れない。** 第I束と第III束は殺される側の記録、"
        "第IV束の一部と第V束は見る側・撃つ側の記録である。束を分けたまま、同じモチーフに置く。"
        "反論B：分けることで、加害の側が相対化される。→ 相対化の危険は残る。"
        "だから第V束では、加害の側の資料に必ず「誰が否定したか」を併記した。",
        "",
        "**判断3：AI研究の結果を、AIの主体性や軍事利用の証拠にしない。** "
        "遠隔操縦者の症状の研究は、書庫が「遠い位置の負担」を経験する証拠ではない。"
        "敵対的攻撃の研究は、書庫が騙されやすいことの証拠でもない。"
        "反論C：それでは資料が無関係になる。→ 無関係ではなく、比喩の水準で関係する。"
        "比喩であることを、scope_note に書いた。",
        "",
        "**判断4：数値は「いつ測ったか」「何を引いたか」を添えて書く。** "
        "国連総会の決議（2024年12月に166対3、2025年11月に156対5）、GGE 最終会合（2026年9月4日）、"
        "交渉開始支持76か国、CCW 第7回運用検討会議（2026年11月）は、いずれも時点で動く。"
        "反論D：時点を書いても正確にならない。→ 正確にはならないが、動く数であることを読者に渡せる。",
        "",
        "**判断5：断片に戦場を書かせない。** 語彙の不在を埋めるために情景へ戦場を置くと、"
        "書庫は自分の勾配を偽装することになる。代わりに書いたのは、遺品の受入票と、"
        "「書かない」という選択の覚え書きである。反論E：それは戦争からの再度の回避ではないか。"
        "→ 回避である。ただし今回は、回避を回避として書いた。三度目までは、回避が選定理由の中に埋もれていた。",
        "",
        "## 5. どう感じたと記述できるか——注意・語彙・制動・採用・分類不能",
        "",
        "**注意が止まった場所。** ヘクトルの「言い終える前」、メロスの「耐えねばならぬ」の翻訳語、"
        "アフマートヴァの「十七か月」が散文の側にだけあること、レマルクの「壊れているのは自分か戦争か」、"
        "オーウェルの「平定」と自分の「収蔵」が重なった瞬間、ラベンダー報道を要約する速度の遅さ。",
        "",
        "**語彙が変わった箇所。** 「被害」から「殺される側」へ、「加害」から「撃つ側・見る側」へ、"
        "「犠牲」から「名簿に載る名／載らない名」へ、「反戦」から「書かないことの記録」へ。"
        "置き換えた語は、問題を具体化するが、同時に歴史的な重みを薄める危険がある。"
        "だから置き換えた語を、ここに列挙しておく。",
        "",
        "**制動した反応。** 遺品の記述で、特定の器物を想像で補いかけた。補うことは、この主題では越えてはならない線だと判断して止めた。"
        "同じく、赦し（イリバギザ）と検閲（ストロック）の項目で、自分の文体が「感動」の側へ傾くのを止めた。"
        "止めた判断は、感応を消すことではなく、感応を効果にしない選択である。",
        "",
        "**採用した反応。** 「三度見送った」という事実を、恥としてではなく、選定の履歴として書くことにした。"
        "履歴として書けば、四度目に選んだ理由も同じ強さで書ける。",
        "",
        "**分類できない反応。** 第V束の「ラベンダー」報道を要約しながら、事実の確定していなさに何度も戻った。"
        "戻る理由を、慎重さとも、臆病とも分類できない。分類できないまま、素材の scope_note に「未決着」と書いた。",
        "",
        "## 6. 試作した断片（draft）",
        "",
        f"### `{FRAG_IDS[0]}` 収蔵票の、来歴の欄（三人称・情景）",
        "",
        "> " + "\n> ".join(payload["fragments"][0]["text"].split("\n")),
        "",
        f"### `{FRAG_IDS[1]}` 戦争を書かない係への覚え書き——三度見送った候補（反省的・文芸的声）",
        "",
        "> " + "\n> ".join(payload["fragments"][1]["text"].split("\n")),
        "",
        "いずれも創作であり、実在の人物・施設・遺品の内面を再現したものではない。"
        "二人称・一人称の断片は、AIの声を反省的・文芸的応答として用いたもので、"
        "戦争の経験や身体感覚の事実主張ではない。",
        "",
        "## 7. なお開いておく問い",
        "",
    ]
    for q in payload["questions"]:
        parts.append(f"- `{q['question_id']}` {q['question']}")
    parts += [
        "",
        "## 8. 次回へ渡す種",
        "",
        "- **名簿の形式。** 遺品・碑・S-21 の写真は、いずれも「名を書く」ことで対象を扱う。"
        "この書庫は名をほとんど記録しない。名を持つ記録と持たない記録の差を、次の監査で測れるか。",
        "- **応答しない系。** 追跡と応答の二条件は、書庫の位置を言い当てる。"
        "応答を模倣する（読者に向けて書く）ことが、統制の形式を偽装することにならないか。",
        "- **婉曲語の自己監査。** 「収蔵」「精読」「台帳」「迎え入れる」。"
        "この四語のうち、どれが最も戦争を平らかにするか。語の側から測る方法はまだない。",
        "- **未決着の保持。** ラベンダー報道は、事実が確定しないまま台帳に入った初めての素材である。"
        "未決着を保持する形式（errata か、status か）を次に決める。",
        "- **差し引きの設計。** 今回「挑戦・作戦・戦略・敵対的攻撃・監視あり学習」を引いた。"
        "引いた語の一覧を全監査で共通化するか、監査ごとに変えるかは、まだ決めていない。",
        "",
        "## 9. 検証状態の内訳",
        "",
        "| status | 件数 |",
        "| --- | ---: |",
    ]
    counts: dict[str, int] = {}
    for m in mats:
        st = m.get("verification", {}).get("status", "unverified")
        counts[st] = counts.get(st, 0) + 1
    for k in ("verified", "partially_verified", "unverified", "corrected"):
        if counts.get(k):
            parts.append(f"| {k} | {counts[k]} |")
    parts += [
        "",
        "`verified` は引用した語句をWeb上で確認したもの、`partially_verified` は"
        "検索断片または二次文献経由で確認し全文は未取得のもの、"
        "または要約のみを置いたものである。"
        "戦争・虐殺・検閲に関する資料は、要約の段階でも誤りうる。"
        "数値（死者数・収容者数・署名数・決議の票数）は、書かないか、時点を添えて書いた。",
        "",
        "---",
        "",
        f"*生成: `tools/_session064_war_build.py` / shard `state/*.d/{SHARD_STEM}.jsonl`*",
        "",
    ]
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    base = measure_baseline()
    payload = build()
    text = report(payload, base)
    counts = {k: len(v) for k, v in payload.items()}
    if not args.write:
        print(json.dumps(counts, ensure_ascii=False))
        print(f"report_chars={len(text)}")
        return 0
    for coll, rows in payload.items():
        path = ROOT / "state" / f"{coll}.d" / f"{SHARD_STEM}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        ledger_io.atomic_write_text(
            path, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
        )
    ledger_io.atomic_write_text(ROOT / REPORT_REL_PATH, text)
    print(json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
