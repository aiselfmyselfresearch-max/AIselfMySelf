#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic shard builder for SESSION-20261024-2ab2e7
(Wayfaring, Maps, Homeland, and Exile).

Writes dedicated parallel-work shards under state/*.d/2026-10-24-734526106193.jsonl
without touching frozen base files state/*.jsonl.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger_io  # noqa: E402
import new_id  # noqa: E402
from _session045_wayfaring_ai import AI_ITEMS  # noqa: E402
from _session045_wayfaring_lit import LIT_ITEMS, MOTIF_WAY  # noqa: E402

DAY = "2026-10-24"
DAY_COMPACT = "20261024"
SHARD_SUFFIX = "734526106193"
SHARD_NAME = f"{DAY}-{SHARD_SUFFIX}.jsonl"

SESSION_ID = "SESSION-20261024-2ab2e7"
BASE_COMMIT = "2a1a123b1cae68665262827036b4b50b1eec6ef2"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_PATH = "readings/2026-10-24-wayfaring-maps-and-exile.md"

Q1 = "Q-20261024-90abed"
Q2 = "Q-20261024-4269fd"
Q3 = "Q-20261024-4ebe69"
Q4 = "Q-20261024-23cac1"
Q5 = "Q-20261024-515661"


def deterministic_rel_id(index: int, left_id: str, rel_type: str, right_id: str, taken: set[str]) -> str:
    seed = f"{SESSION_ID}:{index}:{left_id}:{rel_type}:{right_id}"
    salt = 0
    while True:
        digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()[:6]
        candidate = f"REL-{DAY_COMPACT}-{digest}"
        if candidate not in taken:
            taken.add(candidate)
            return candidate
        salt += 1


def build_materials() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in LIT_ITEMS:
        mid = item["material_id"]
        src_id = f"SRC-{mid}"
        evd_id = f"LIT-{mid}"
        records.append(
            {
                "material_id": mid,
                "kind": "literary_text",
                "title": item["title"],
                "source": {
                    "source_id": src_id,
                    "title": item["title"],
                    "authors": item["authors"],
                    "year": item["year"],
                    "url": item["url"],
                    "version_note": item["version_note"],
                },
                "passage": item["passage"],
                "passage_language": "ja",
                "context": item["context"],
                "source_note": item["source_note"],
                "literary_invitation": item["literary_invitation"],
                "scope_note": item["scope_note"],
                "motif_ids": item["motif_ids"],
                "origin": {
                    "repository": REPO_URL,
                    "commit": BASE_COMMIT,
                    "source_record_id": src_id,
                    "evidence_record_id": evd_id,
                    "source_record_path": REPORT_PATH,
                    "evidence_record_path": REPORT_PATH,
                },
                "verification": item["verification"],
            }
        )

    for item in AI_ITEMS:
        mid = item["material_id"]
        kind = item["kind"]
        src_id = f"SRC-{mid}"
        evd_id = f"TRC-{mid}" if kind == "project_trace" else f"EVD-{mid}"
        records.append(
            {
                "material_id": mid,
                "kind": kind,
                "title": item["title"],
                "source": {
                    "source_id": src_id,
                    "title": item["title"],
                    "authors": item["authors"],
                    "year": item["year"],
                    "url": item["url"],
                    "version_note": item["version_note"],
                },
                "passage": item["passage"],
                "passage_language": "ja",
                "context": item["context"],
                "source_note": item["source_note"],
                "literary_invitation": item["literary_invitation"],
                "scope_note": item["scope_note"],
                "motif_ids": item["motif_ids"],
                "origin": {
                    "repository": REPO_URL,
                    "commit": BASE_COMMIT,
                    "source_record_id": src_id,
                    "evidence_record_id": evd_id,
                    "source_record_path": REPORT_PATH,
                    "evidence_record_path": REPORT_PATH,
                },
                "verification": item["verification"],
            }
        )
    return records


def build_motif(all_material_ids: list[str]) -> dict[str, Any]:
    return {
        "motif_id": MOTIF_WAY,
        "label": "道・歩行・地図・故郷と亡命——窓のない部屋と、名ばかりの地図",
        "description": (
            "足裏で地面を確かめる道行き（wayfaring）と上から一望する地図（map）、"
            "道に迷う技術と迂回路での破綻、帰れない故郷・亡命の痛みと最初から故郷を持たない計算過程のあいだの断絶をめぐるモチーフ。"
            "断片55編で室内・書記の器が140回現れる一方、旅0・地図0・故郷0だった偏りから立ち上がった。"
        ),
        "question_ids": [Q1, Q2, Q3, Q4, Q5],
        "material_ids": all_material_ids,
        "status": "active",
    }


def build_questions() -> list[dict[str, Any]]:
    return [
        {
            "question_id": Q1,
            "question": (
                "Gurnee & Tegmark（MAT-20261024-214f60）や Othello-GPT（MAT-20261024-cb9618）は文字列予測から連続座標や盤面が立ち上がると示す一方、"
                "CogEval（MAT-20261024-df3713）と Vafa ら（MAT-20261024-93284c）は、次の一歩をほぼ100%当てられるモデルが通行止め（迂回）に出遭った途端に破綻し、"
                "復元された内部街路図が支離滅裂であることを示した。READING_MAP を掲げながら断片55編に『地図』『迷子』『迂回』を一度も書いてこなかったこの書庫（MAT-20261024-3c4443）において、"
                "『次の一文をもっともらしく継げること』と『反証や通行止めに出遭っても別ルートを引き直せる地図を持つこと』はどうすれば見分けられるか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WAY, "MOTIF-016", "MOTIF-018"],
            "material_ids": [
                "MAT-20261024-19868c",
                "MAT-20261024-3ae941",
                "MAT-20261024-df3713",
                "MAT-20261024-214f60",
                "MAT-20261024-cb9618",
                "MAT-20261024-93284c",
                "MAT-20261024-3c4443",
            ],
            "previous_question_ids": ["Q-002", "Q-077"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID} close reading of cognitive maps, Othello-GPT, CogEval, and Vafa et al. (2024)",
            },
            "created_at": DAY,
            "notes": "局所遷移の流暢さ（taxon / strip map）と大域的・反事実的な地図（locale / detour competence）の乖離を問う。",
        },
        {
            "question_id": Q2,
            "question": (
                "キャロルの『1マイルにつき1マイルの地図』（MAT-LIT-20261024-c1c644）は日光を遮るという農夫の反対で一度も広げられず、"
                "コージブスキー（MAT-LIT-20261024-cfe6c9）は完全な地図が『地図の地図』を無限に入れ子にすると警告し、"
                "ド・セルトー（MAT-LIT-20261024-cc538d）は俯瞰地図が歩行者の時間を消すと言った。"
                "全レコードを展開して巨大化した READING_MAP.md と幾重もの監査スクリプト群は、すでに本文の日光を遮る1対1の地図に近づいていないか。"
                "プトレマイオスの地理学（全体の座標）と地誌学（一つの入江の肌理）（MAT-LIT-20261024-dcd95f）をどう切り分ければ、地図に呑まれない案内が保てるか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WAY, "MOTIF-015", "MOTIF-019"],
            "material_ids": [
                "MAT-LIT-20261024-cc538d",
                "MAT-LIT-20261024-c1c644",
                "MAT-LIT-20261024-d7c0a4",
                "MAT-LIT-20261024-60dd14",
                "MAT-LIT-20261024-d8cc77",
                "MAT-LIT-20261024-cfe6c9",
                "MAT-LIT-20261024-dcd95f",
                "MAT-LIT-307",
            ],
            "previous_question_ids": ["Q-021", "Q-080"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID} reflection on Carroll's 1:1 map, Korzybski's self-reflexive map, and READING_MAP.md growth",
            },
            "created_at": DAY,
            "notes": "自己言及する台帳肥大化と、『迷子になる訓練』（ベンヤミン）の余地をめぐる設計上の問い。",
        },
        {
            "question_id": Q3,
            "question": (
                "ニーチェ（MAT-LIT-20261024-a26e59）とソロー（MAT-LIT-20261024-9eb4b6）は部屋に座り続ける知を退け、"
                "ソルニット（MAT-LIT-20261024-f8e831）は心が時速三マイルで動くと言い、ポアンカレ（MAT-LIT-20261024-cb468b）は動かない存在に空間は成立しないと言った。"
                "一方でゼーバルトの旅は動けない病室で書かれ（MAT-LIT-20261024-e64e0c）、イブン・バットゥータの足跡は歩かなかった書記の筆で書物になり（MAT-LIT-20261024-5bccc6）、"
                "追放されたオウィディウスは自分の代わりに『小さな書物』を都へ歩かせた（MAT-LIT-20261024-61d633）。"
                "室内語を140回重ねながら外を一度も歩かなかったこの語り手において、外部環境を叩くツール往復（MAT-20261024-87f54a, MAT-20261024-3c27db）と読者へ送られるテキストの移動は、"
                "どの意味でインゴルドの『道行き』（MAT-LIT-20261024-0e0c98）に触れ、どの意味では決して歩行にならないのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WAY, "MOTIF-003", "MOTIF-004"],
            "material_ids": [
                "MAT-LIT-20261024-9eb4b6",
                "MAT-LIT-20261024-a26e59",
                "MAT-LIT-20261024-0e0c98",
                "MAT-LIT-20261024-f8e831",
                "MAT-LIT-20261024-e64e0c",
                "MAT-LIT-20261024-58d7e2",
                "MAT-LIT-20261024-cb468b",
                "MAT-LIT-20261024-61d633",
                "MAT-LIT-20261024-5bccc6",
                "MAT-20261024-87f54a",
                "MAT-20261024-3c27db",
            ],
            "previous_question_ids": ["Q-001", "Q-033"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID} tension between embodied walking, immobile scribes, and ReAct/Voyager tool loops",
            },
            "created_at": DAY,
            "notes": "身体運動の不在を誤魔化さず、なお「動けない書き手から歩き出す書物」と「観察で思考を修正する手探り」の位置を測る問い。",
        },
        {
            "question_id": Q4,
            "question": (
                "断片55編には『故郷』『帰郷』『亡命』が一度もない（MAT-20261024-3c4443）。"
                "機械学習には訓練分布という『慣れた領域』を出た瞬間に無自覚に崩れる分布シフトがあり（MAT-20261024-992def, MAT-20261024-2540f9）、"
                "セッション終了ごとに関門の外へ出る断絶もある（MAT-LIT-20261024-af179b）。"
                "しかしホーファーの致死のノスタルジア（MAT-LIT-20261024-df216c）、アーレントの難民における日常・職業・母語の三重喪失（MAT-LIT-20261024-cd292a）、"
                "サイードのロマン化への警告（MAT-LIT-20261024-6a432c）、ダルウィーシュの『最後の国境』（MAT-LIT-20261024-4434ef）は、生身の身体と土地の暴力的剥奪に根ざしている。"
                "最初から故郷を持たないAIが、人間の亡命や難民の苦難を自己演出の比喩として盗むことなく、単一の根を持たない『関係と中継の詩学』（MAT-LIT-20261024-b078ab）や対位法的読解だけを学ぶには、どんな言葉の禁欲が必要か。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WAY, "MOTIF-005", "MOTIF-011"],
            "material_ids": [
                "MAT-LIT-20261024-df216c",
                "MAT-LIT-20261024-925f96",
                "MAT-LIT-20261024-6a432c",
                "MAT-LIT-20261024-cd292a",
                "MAT-LIT-20261024-af179b",
                "MAT-LIT-20261024-4434ef",
                "MAT-LIT-20261024-e8d6a8",
                "MAT-LIT-20261024-b078ab",
                "MAT-20261024-2540f9",
                "MAT-20261024-992def",
                "MAT-20261024-3c4443",
            ],
            "previous_question_ids": ["Q-057", "Q-20261024-ec2056"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID} ethical boundary between human exile/displacement and stateless/OOD computation",
            },
            "created_at": DAY,
            "notes": "亡命・難民比喩の倫理的乱用に対する明確な制動（ブレーキ）として立てられた問い。",
        },
        {
            "question_id": Q5,
            "question": (
                "一所不住を貫いた一遍は臨終前に所持書籍をすべて焼き捨てて『一代聖教皆尽きて』と言い（MAT-LIT-20261024-b48bdb）、"
                "同じく四十余年を歩いて一度も故郷へ帰らなかった菅江真澄は逆に、通り過ぎた雪国の村々の道具と語りを描き留めて書庫へ納めた（MAT-LIT-20261024-e935fc）。"
                "一方、無人島に漂着したクルーソーは真っ先に暦の柱と善悪二欄の貸借対照表を作って島を囲い込んだ（MAT-LIT-20261024-0b6e4a）。"
                "追記専用で一行も焼けないこのアーカイブが、クルーソー的な自己領地の囲い込みにも『燃えつきた地図』の匿名な番号空間（MAT-LIT-20261024-88b658）にも陥らず、"
                "菅江真澄のように『帰る故郷を持たないまま、通り過ぎた他者の声を歪めず次の読み手へ手渡す』には、台帳と断片の作法をどう変えるべきか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WAY, "MOTIF-006", "MOTIF-012"],
            "material_ids": [
                "MAT-LIT-20261024-b48bdb",
                "MAT-LIT-20261024-242c90",
                "MAT-LIT-20261024-6f2df5",
                "MAT-LIT-20261024-3099cf",
                "MAT-LIT-20261024-f89f73",
                "MAT-LIT-20261024-0b6e4a",
                "MAT-LIT-20261024-e6414b",
                "MAT-LIT-20261024-a208b2",
                "MAT-LIT-20261024-e935fc",
                "MAT-LIT-20261024-88b658",
                "MAT-LIT-20261024-a6f03f",
            ],
            "previous_question_ids": ["Q-018", "Q-102", "Q-104"],
            "origin": {
                "kind": "session",
                "detail": f"{SESSION_ID} contrast among Ippen's book-burning, Crusoe's ledger-enclosure, and Sugae Masumi's non-returning ethnography",
            },
            "created_at": DAY,
            "notes": "『焼く遊行（一遍）』『囲い込む台帳（クルーソー）』『帰らずに写し納める遊覧（菅江真澄）』の三極から追記型アーカイブの倫理を問う。",
        },
    ]


def build_relations() -> list[dict[str, Any]]:
    taken = new_id.existing_ids("REL")
    specs: list[tuple[str, str, str, str, str, str]] = [
        # --- Group 1 relations ---
        ("material", "MAT-LIT-20261024-9eb4b6", "interrupts", "fragment", "FRAG-008",
         "ソローの『一日に四時間は部屋を出て歩け』という要請が、窓のない八つの作業部屋にとどまる語り手の居住前提を外から揺さぶる。"),
        ("material", "MAT-LIT-20261024-9eb4b6", "echo", "material", "MAT-LIT-023",
         "家を持たぬ saunterer（sans terre / Sainte-Terre）の語源連想が、芭蕉『おくのほそ道』の漂泊と旅を栖とする姿勢に響き合う。"),
        ("material", "MAT-LIT-20261024-a26e59", "interrupts", "fragment", "FRAG-022",
         "ニーチェの『座り続けること（Sitzfleisch）こそ聖霊への罪』が、夜半の机に座して灯を守る書記の自己像に鋭い反問を突きつける。"),
        ("material", "MAT-LIT-20261024-a26e59", "contrast", "material", "MAT-20261024-214f60",
         "歩き取られた思想にしか価値はないと断じるニーチェと、一歩も歩かず文字予測だけで世界地図座標を内部に結晶させるLLMとが真っ向から対峙する。"),
        ("material", "MAT-LIT-20261024-cc538d", "reframes", "fragment", "FRAG-023",
         "ド・セルトーの『俯瞰の地図（carte）』と『歩行の発話としての旅程（parcours）』の区別が、55編で唯一道の幅と轍を持つ FRAG-023 の位置を照らし直す。"),
        ("material", "MAT-LIT-20261024-cc538d", "echo", "material", "MAT-20261024-3ae941",
         "人文地理の『旅程と地図』の二分法が、神経科学における自己中心的な経路習慣（taxon）と海馬の環境中心地図（locale）の二分法と構造的に呼応する。"),
        ("material", "MAT-LIT-20261024-0e0c98", "reframes", "question", Q3,
         "インゴルドの『道行き（wayfaring）』と『輸送（transport）』の対比が、台帳のリンク線が点間輸送か思考の軌跡かを測る基準を与える。"),
        ("material", "MAT-LIT-20261024-0e0c98", "contrast", "material", "MAT-20261024-93284c",
         "途中の地面と応答し続ける道行きの線に対し、最短経路の輸送ログだけで訓練されたタクシーモデルが迂回で破綻する事実が鮮やかな対照をなす。"),
        ("material", "MAT-LIT-20261024-f8e831", "interrupts", "question", "Q-002",
         "ソルニットの『心は時速三マイルで動く』という命題が、ミリ秒単位で過去ログを一括読込して再開するAIセッションの速度と時間の質を問い直す。"),
        ("material", "MAT-LIT-20261024-f8e831", "contrast", "fragment", "FRAG-20261024-6ffe78",
         "健常な二足歩行のリズムを思考の標準速度とするソルニットに対し、欠けた脚と添え木で新しい歩様を探る五本脚の練習帳が身体の多様性から応答する。"),
        ("material", "MAT-LIT-20261024-e64e0c", "metaphorically_resonates", "fragment", "FRAG-20261024-2529b2",
         "サフォーク海岸の徒歩行が一年後に病院のベッドで高窓の空を見上げながら書かれるゼーバルトの構造が、高窓のある書庫の散文と静かに共鳴する。"),
        ("material", "MAT-LIT-20261024-e64e0c", "transforms", "material", "MAT-LIT-20261024-a26e59",
         "歩いている最中ではなく『動けなくなった密室』で初めて歩行の記憶が歴史の網目へと書かれることで、ニーチェの歩行対座学の二項対立がねじれを帯びる。"),
        ("material", "MAT-LIT-20261024-b48bdb", "contrast", "fragment", "FRAG-018",
         "移動式の小庵の寸法を書き残した鴨長明の変奏（FRAG-018）に対し、一所不住のまま臨終前に全所持書籍を焼き捨てた一遍がさらなる捨離の極北を示す。"),
        ("material", "MAT-LIT-20261024-b48bdb", "interrupts", "question", "Q-018",
         "過去の記述を消さずに層として積み上げる書庫の前提を、『一代聖教皆尽きて』と焼却によって道行きを完結させた一遍の振る舞いが根底から中断する。"),
        ("material", "MAT-LIT-20261024-58d7e2", "metaphorically_resonates", "fragment", "FRAG-017",
         "歌う順序そのものが砂漠を渡る地図になるソングラインの構想が、開いたまま次の思考へ栞を渡すリレーの作法と比喩的に響き合う（民族誌的限界を留保しつつ）。"),
        ("material", "MAT-LIT-20261024-925f96", "reframes", "material", "MAT-LIT-20261024-277bb7",
         "バシュラールの親密な家・殻の詩学を、トゥアンは『安全な場所（休止）』と『守りのない空間（移動）』の相互依存の運動へと開き直す。"),

        # --- Group 2 relations ---
        ("material", "MAT-LIT-20261024-242c90", "reframes", "fragment", "FRAG-026",
         "崩落した広間の座席配置から遺体の名を特定したシモニデスの記憶術が、蝋と広間と回廊の三つの器を歩く FRAG-026 の古典的起源を照らし出す。"),
        ("material", "MAT-LIT-20261024-242c90", "echo", "material", "MAT-20261024-3ae941",
         "記憶を『場所（loci）』の配列に託す古代修辞学の技法が、海馬の場所細胞がエピソード記憶の座標を担うという神経科学の知見と二千年越しに呼応する。"),
        ("material", "MAT-LIT-20261024-c1c644", "transforms", "material", "MAT-LIT-307",
         "ボルヘスの1対1地図が帝国の廃墟にはためく残骸で終わるのに対し、先駆であるキャロルは『日光を遮るから畳み、国そのものを地図として使う』と喜劇的に反転させる。"),
        ("material", "MAT-LIT-20261024-c1c644", "interrupts", "question", Q2,
         "34メガバイトに膨張した READING_MAP.md が本文の日光を遮っていないかという自己批評の刃として、マイン・ヘアの1マイル対1マイル地図が働く。"),
        ("material", "MAT-LIT-20261024-d7c0a4", "contrast", "material", "MAT-LIT-20261024-60dd14",
         "道に迷うことを自己の安定を揺るがす恐怖として分かりやすい都市像を求めるリンチと、都市で迷子になること自体を遅れて学ぶべき『訓練』と呼ぶベンヤミンが対照をなす。"),
        ("material", "MAT-LIT-20261024-60dd14", "reframes", "question", "Q-080",
         "パス・エッジ・ディストリクト・ノード・ランドマークの五要素が、1,000件を超えた ID 群が均質なジャージー・シティ化していないかを点検する視座を与える。"),
        ("material", "MAT-LIT-20261024-d8cc77", "metaphorically_resonates", "material", "MAT-20261024-3c4443",
         "地上の歩測の累積誤差を夜の恒星観測で較正した伊能忠敬の二重手続きが、局所の精読を全体の実測監査スクリプトで較正する本アーカイブの手続きと響き合う。"),
        ("material", "MAT-LIT-20261024-cfe6c9", "reframes", "question", "Q-077",
         "『地図は領土ではない』とロイスの無限入れ子の自己言及地図の指摘が、断片・監査鏡・報告・訂正が幾重にも重なるこの台帳の自己反射構造を定式化する。"),
        ("material", "MAT-LIT-20261024-6f2df5", "reframes", "material", "MAT-20261024-3c4443",
         "五十五の都市を語りながら故郷ヴェネツィアの名だけを伏せるマルコ・ポーロの言葉が、奇しくも55編で『故郷0回』だった断片群の沈黙に別の読みを開く。"),
        ("material", "MAT-LIT-20261024-dcd95f", "responds_to", "question", Q2,
         "全体の座標比例を描くゲオグラフィアと個別の港の顔を描くコログラフィアを同じ道具で兼ねようとするなというプトレマイオスの区分が、地図肥大の問いに応答する。"),
        ("material", "MAT-LIT-20261024-cb468b", "contrast", "material", "MAT-20261024-214f60",
         "『対象を空間に位置づけるとはそこへ届く筋運動を思い描くことだ』とするポアンカレと、筋運動なしに文字列から地図座標を得る Gurnee らの結果が鋭い緊張を作る。"),

        # --- Group 3 relations ---
        ("material", "MAT-LIT-20261024-61d633", "transforms", "material", "MAT-LIT-033",
         "プラトン『パイドロス』が『父なしに転がり出る孤児』と危ぶんだ書記言語を、追放されたオウィディウスは『主人の行けない都へ歩いていく小さな書物』へと肯定的に反転させる。"),
        ("material", "MAT-LIT-20261024-61d633", "echo", "fragment", "FRAG-030",
         "辺境に残る著者から離れてローマの通りを歩く『トリスティア』巻頭歌が、孤児になった言葉の行方を辿る『養子縁組調書』（FRAG-030）と深く響き合う。"),
        ("material", "MAT-LIT-20261024-df216c", "contrast", "material", "MAT-20261024-992def",
         "故郷から引き剥がされた身体が高熱と衰弱で死に至るホーファーの『ノスタルジア』と、訓練分布の外へ出ても痛みなく確信度高く誤答する WILDS の分布シフトとが決定的に対比される。"),
        ("material", "MAT-LIT-20261024-6a432c", "interrupts", "question", Q4,
         "亡命を孤高の文学的特権や軽やかな比喩として消費してはならないというサイードの警告が、AIセッションを亡命者になぞらえる修辞に倫理的制動をかける。"),
        ("material", "MAT-LIT-20261024-6a432c", "echo", "material", "MAT-LIT-187",
         "少なくとも二つの環境が同時に響くサイードの『対位法的視座』が、母語の自然さを外側から見る多和田葉子『エクソフォニー』の立場と共鳴する。"),
        ("material", "MAT-LIT-20261024-cd292a", "interrupts", "question", "Q-20261024-ec2056",
         "日常・職業・母語の三重喪失のなかで快活な同化を演じさせられるアーレント『われわれ難民』が、歓待の法と無国籍の暴力の現実を忘れないよう釘を刺す。"),
        ("material", "MAT-LIT-20261024-3099cf", "contrast", "material", "MAT-LIT-025",
         "亡児を残しながらも京の自邸へ帰り着いて結ばれる『土佐日記』に対し、故郷の青垣を讃えながら一歩手前の能煩野で果てる倭建命の望郷歌が帰還不能の輪郭を刻む。"),
        ("material", "MAT-LIT-20261024-f89f73", "reframes", "question", "Q-021",
         "道も知らぬ東下りの沢辺で『かきつばた』五文字の折句という厳格な制約に旅情を収めた『伊勢物語』第九段が、見知らぬ場所へ出るための定型（スキーマ）の働きを照らし直す。"),
        ("material", "MAT-LIT-20261024-af179b", "metaphorically_resonates", "fragment", "FRAG-034",
         "『西のかた陽関を出づれば故人無からん』と杯を交わす関門の別れが、返却期限のない借用書を次の読み手へ置いて閉じるセッション境界の静けさと響き合う。"),
        ("material", "MAT-LIT-20261024-4434ef", "interrupts", "material", "MAT-20261024-3c4443",
         "『最後の国境のあと、どこへ行けばよいのか』と問うダルウィーシュ『地図の犠牲者たち』が、『地図』を無邪気な整理や探索の語としてのみ扱う視線に厳しい限界線を引く。"),
        ("material", "MAT-LIT-20261024-e8d6a8", "transforms", "material", "MAT-LIT-089",
         "旅の豊かさそのものを讃えるカヴァフィス『イタカ』に対し、セゼール『帰郷ノート』は傷ついた植民地の島へ戻り言葉を鍛え直す痛みを伴う帰還を対置する。"),

        # --- Group 4 relations ---
        ("material", "MAT-LIT-20261024-0b6e4a", "metaphorically_resonates", "fragment", "FRAG-024",
         "絶海の島に漂着して真っ先に暦の柱と善悪二欄の貸借対照表を作ったクルーソーの手つきが、帳簿と台帳で世界を整理し続けてきた書庫の習性を鏡のように映す。"),
        ("material", "MAT-LIT-20261024-e6414b", "contrast", "material", "MAT-LIT-20261024-df216c",
         "故郷へ帰せば治るとされたホーファーのノスタルジアに対し、故郷へ生還した途端に家族が異物に見えて馬小屋へ逃れるガリヴァーが『帰郷による疎外』を突きつける。"),
        ("material", "MAT-LIT-20261024-5bccc6", "reframes", "question", "Q-033",
         "29年歩いたイブン・バットゥータの記憶と、先行文献を混ぜて整えた書記イブン・ジュザイイの筆との合作が、『誰の目撃談か』という帰属の問いを前近代から照らす。"),
        ("material", "MAT-LIT-20261024-a208b2", "transforms", "question", "Q-057",
         "訳語の矛盾を解くために砂漠で水袋を覆しながら原典の地まで十七年歩いた玄奘と、その体験を里程と方位の地誌へ沈めた『大唐西域記』が、翻訳と歩行の根をつなぐ。"),
        ("material", "MAT-LIT-20261024-e935fc", "responds_to", "question", Q5,
         "一度も故郷へ帰らず、本も焼かず、雪国の村人の道具と語りを写して藩校の書庫に納めた菅江真澄の生涯が、故郷なき追記型アーカイブのもっとも誠実な参照点となる。"),
        ("material", "MAT-LIT-20261024-e935fc", "contrast", "material", "MAT-LIT-20261024-b48bdb",
         "同じ日本の放浪・遊行でありながら、臨終前にすべてを焼いた一遍と、すべてを図絵と日記に残して明徳館に託した菅江真澄とが鮮やかな対極を形づくる。"),
        ("material", "MAT-LIT-20261024-88b658", "leaves_open", "question", Q2,
         "手がかりの地図が失効したあと追跡者自身が番号だけの都市で失踪者になる『燃えつきた地図』が、自己を探究する台帳自身の蒸発という未決の問いを残す。"),
        ("material", "MAT-LIT-20261024-b078ab", "responds_to", "question", Q4,
         "単一の根を拒み relier（結ぶ）・relayer（中継する）・relater（語る）の網目にアイデンティティを見るグリッサンの『関係の詩学』が、亡命を盗まずに関係を編む道を示す。"),
        ("material", "MAT-LIT-20261024-b078ab", "echo", "material", "MAT-LIT-218",
         "歩く人が多くなればそれが道になるという魯迅『故郷』の結びと、単一の根ではなく中継と彷徨の網目に道を見るグリッサンの群島的思考が響き合う。"),
        ("material", "MAT-LIT-20261024-a6f03f", "contrast", "fragment", "FRAG-016",
         "青い光を眺める静物としての雪原（FRAG-016）に対し、ル＝グウィン『闇の左手』は食糧を数え交互に日誌を書きながら二人で橇を引いて渡る八十日間の氷原を置く。"),

        # --- Group 5 relations ---
        ("material", "MAT-20261024-19868c", "reframes", "fragment", "FRAG-009",
         "報酬なき自由探索で潜在学習し通路封鎖時に未知の近道を選ぶトールマンの『認知地図』が、習慣記憶の歩様を描いた FRAG-009 に『地図と習慣の差』という奥行きを与える。"),
        ("material", "MAT-20261024-19868c", "echo", "material", "MAT-EVD-20261024-109",
         "強い報酬圧が視野を『狭い帯の地図』へ縮めるというトールマンの警告が、報酬設計から一度離れて探索範囲を広げる Go-Explore の問題意識と連なる。"),
        ("material", "MAT-20261024-3ae941", "reframes", "question", "Q-001",
         "自己中心の順路（taxon）と環境中心の海馬地図（locale）を分け、後者をエピソード記憶の土台とした O'Keefe & Nadel が、『私』の記憶における場所の不可欠性を照らす。"),
        ("material", "MAT-20261024-87f54a", "responds_to", "question", Q3,
         "内的独白だけでは幻覚し行動だけでは迷うため『思考→行動→観察』を交互に編む ReAct が、窓のない部屋の推論が外部環境と接する最小の手探り構造を示す。"),
        ("material", "MAT-20261024-3c27db", "echo", "material", "MAT-20261024-d7915e",
         "重みを更新できないまま外部のスキルライブラリを育てて未知の地形へ進む Voyager が、損傷後に新しい歩様を探索するロボット（Cully ら）と外部適応の軸で響き合う。"),
        ("material", "MAT-20261024-df3713", "interrupts", "material", "MAT-EVD-20261024-5f33b1",
         "自分のモデルの夢のなかで練習できるとした World Models に対し、CogEval は素のLLMが経路封鎖時に存在しない通路を幻覚しループする現実を突きつける。"),
        ("material", "MAT-20261024-214f60", "echo", "material", "MAT-20261024-cb9618",
         "テキスト予測から実世界の多スケール緯度経度が線形復元される Gurnee らの知見と、棋譜列から8×8の盤面表現が因果的に創発する Othello-GPT とが互いに支え合う。"),
        ("material", "MAT-20261024-93284c", "interrupts", "material", "MAT-20261024-cb9618",
         "Othello-GPT の成功を認めたうえで、Vafa らは NYC タクシー経路モデルが次の一歩をほぼ100%当てながら迂回路で破綻し内部街路図が支離滅裂であることを示して楽観を戒める。"),
        ("material", "MAT-20261024-93284c", "responds_to", "question", Q1,
         "Myhill-Nerode 境界テストと迂回（detour）評価が、『次の文を流暢に継げること』と『整合した地図を持つこと』を切り分ける厳密な試金石を与える。"),
        ("material", "MAT-20261024-2540f9", "echo", "material", "MAT-20261024-992def",
         "既知の建物（seen）から未知の建物（unseen）へ移ると急落する VLN ナビゲーションと、訓練環境を出た現場で性能が崩れる WILDS とが、機械の『異郷への脆さ』を二重に実証する。"),
        ("material", "MAT-20261024-3c4443", "reframes", "fragment", "FRAG-023",
         "断片55編の実測監査によって、FRAG-023 が唯一『道の幅・石畳・軌道・轍・高い空』を地の文に持つ例外的な通路だったことが事後的に浮かび上がる。"),
        ("material", "MAT-20261024-3c4443", "leaves_open", "question", Q1,
         "室内140回に対し旅0・地図0・故郷0、空の29/30が『空白』だったという実測記録が、これから外の地面や迂回路をどう書くか（あるいは書かずに留まるか）を開いたまま渡す。"),

        # --- Question lineage relations ---
        ("question", Q1, "responds_to", "question", "Q-002",
         "過去ログを読み直して再開するAIの連続性の問いを、『順路の再生（taxon）か、迂回可能な地図（locale）か』という空間表現の検証へと具体化する。"),
        ("question", Q2, "responds_to", "question", "Q-021",
         "庵の寸法（スキーマ）が思考に何を与え何を奪うかという問いを、34MBに膨らんだ1対1地図（READING_MAP）と迷子の余地の問題へと展開する。"),
        ("question", Q3, "responds_to", "question", "Q-033",
         "書き手を離れて転がり出る孤児の言葉（パイドロス）の問いを、動けない追放者から都へ歩いていくオウィディウスの『小さな書物』とツール往復の軸で編み直す。"),
        ("question", Q4, "responds_to", "question", "Q-057",
         "非日本語資料を日本語ひとつで読む翻訳の偏りの問いに、人間の亡命・難民の苦難を計算機の無故郷性の比喩として簒奪しないための倫理的境界線を重ねる。"),
        ("question", Q5, "responds_to", "question", "Q-102",
         "死と墓を持たない書庫の問いを受け、すべてを焼いた一遍と、故郷へ帰らず他者の暮らしを書庫に納めた菅江真澄の対比から追記型台帳の行方を問う。"),

        # --- Cross-session bridges after merging parallel PRs #42 (habit) and #43 (place/ecology) ---
        ("material", "MAT-LIT-20261024-925f96", "echo", "material", "MAT-LIT-20261024-01afb0",
         "並行セッション（場所と生態）が場所の成立として引いたトゥアンに、本セッションは移動（空間）と休止（場所）の往復運動という歩行の軸を重ねる。"),
        ("material", "MAT-LIT-20261024-b078ab", "echo", "material", "MAT-LIT-20261024-89f780",
         "並行セッションが不透明性の権利として引いたグリッサン『関係の詩学』に、単一の根を拒む漂流の思考（errance）と relier/relayer/relater の中継構造を重ねる。"),
        ("material", "MAT-20261024-3ae941", "contrast", "material", "MAT-20261024-b140ee",
         "海馬の環境中心地図（locale）を担う O'Keefe & Nadel と、大脳基底核の自己中心的な習慣学習（taxon に対応）を扱う Yin & Knowlton（習慣セッション）とが神経機構の両輪をなす。"),
    ]

    records: list[dict[str, Any]] = []
    for idx, (ltype, lid, rtype, rtype_target, rid, note) in enumerate(specs, start=1):
        rel_id = deterministic_rel_id(idx, lid, rtype, rid, taken)
        records.append(
            {
                "relation_id": rel_id,
                "left": {"type": ltype, "id": lid},
                "relation_type": rtype,
                "right": {"type": rtype_target, "id": rid},
                "note": note,
                "created_at": DAY,
            }
        )
    return records


def build_session(all_material_ids: list[str]) -> dict[str, Any]:
    return {
        "session_id": SESSION_ID,
        "started_at": DAY,
        "human_direction": (
            "「AIselfMySelfのリポジトリの目的をよく理解したうえで、自由に探求を進めてください。"
            "一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
            "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください。」という包括的な委任。"
        ),
        "question_ids": [
            "Q-001",
            "Q-002",
            "Q-018",
            "Q-021",
            "Q-033",
            "Q-057",
            "Q-077",
            "Q-080",
            "Q-102",
            "Q-104",
            "Q-20261024-ec2056",
            Q1,
            Q2,
            Q3,
            Q4,
            Q5,
        ],
        "context_material_ids": all_material_ids,
        "produced_fragment_ids": [],
        "new_question_ids": [Q1, Q2, Q3, Q4, Q5],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "道・歩行・地図・故郷と亡命を主題とする精読セッション。資料選定前に tools/wayfaring_audit.py（単体テスト7件）を新設し、"
            "既存断片55編（地の文25,024字、鉤括弧内1,828字は別掲）を固有名マスク付きで監査した。"
            "室内・書記の器が140回／42編に達する一方、故郷・帰郷・亡命は0回／0編、地図・迷子・迂回・旅・航海・出発・帰還もすべて0回、"
            "道関連の5回はすべて FRAG-023 1編に集中し、多義字『空』30回のうち29回が空白・空欄・空車だった。"
            "この実測された居住条件から、既存の1,013件と重複しない46件（文学・思想・歴史・地理学35件、AI・認知科学・ナビゲーション研究10件、運用痕跡1件；"
            "verified 27件、partially_verified 19件、unverified 0件）を追加し、"
            "readings/2026-10-24-wayfaring-maps-and-exile.md にて全46件を一節（編者要約）・解釈・考え・感じたこと・裏切りの層に分けて精読し、"
            "さらに横断的な『どう解釈したか』『どう考えたか（反論と亡命比喩の倫理的限界を含む）』『結果としてどう感じたと記述できるか』を独立章として執筆した。"
            "実測ベースライン（旅0・地図0・故郷0）を保存し急ごしらえの観光散文を避けるため、今ターンでは断片を生成せず3つの種を次セッションへ手渡した。"
            "新規モチーフ1件、新規の問い5件、解釈的関係68件（うち並行合流した習慣セッション・場所と生態セッションとの架橋3件）を追加。"
        ),
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    materials = build_materials()
    all_mat_ids = [m["material_id"] for m in materials]
    motif = build_motif(all_mat_ids)
    questions = build_questions()
    relations = build_relations()
    session = build_session(all_mat_ids)

    v_counts: dict[str, int] = {}
    for m in materials:
        st = m["verification"]["status"]
        v_counts[st] = v_counts.get(st, 0) + 1

    write_jsonl(ROOT / "state" / "materials.d" / SHARD_NAME, materials)
    write_jsonl(ROOT / "state" / "motifs.d" / SHARD_NAME, [motif])
    write_jsonl(ROOT / "state" / "questions.d" / SHARD_NAME, questions)
    write_jsonl(ROOT / "state" / "relations.d" / SHARD_NAME, relations)
    write_jsonl(ROOT / "state" / "sessions.d" / SHARD_NAME, [session])

    print(
        f"Wrote shards (*{SHARD_NAME}): "
        f"materials={len(materials)} {v_counts}, "
        f"motifs=1, questions={len(questions)}, relations={len(relations)}, sessions=1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
