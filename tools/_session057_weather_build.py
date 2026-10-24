#!/usr/bin/env python3
"""Deterministic shard builder for SESSION-20261024-s057 (weather, season, and the dry archive).

第41のモチーフ「予報はできるが、濡れない——天候・季節・気配と、乾いた書庫」を開く。
第I束 予報を計算する (10) / 第II束 天候と情動 (6) / 第III束 値段と制度 (5)
第IV束 天候を書く (18) / 第V束 気候が人間を説明する (3) = 外部42件 + 運用痕跡1件。

Emits append-only shards under state/*.d/2026-10-24-6900d8b2c4f1.jsonl.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402
from _session057_weather_data1 import COMMIT_REF, ITEMS_PART1, MOTIF_WEATHER  # noqa: E402
from _session057_weather_data2 import ITEMS_PART2  # noqa: E402

SHARD_STEM = "2026-10-24-6900d8b2c4f1"
SESSION_ID = "SESSION-20261024-s057"
CREATED_AT = "2026-10-24"
HUMAN_DIRECTION = "このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-24-session-057-forecast-and-dry-archive.md"

# データ側で使った読みやすい別名を、既存の実在モチーフIDへ対応づける
MOTIF_REMAP = {
    "MOTIF-026": "MOTIF-022",              # 死と弔い（MOTIF-026 は本台帳に存在しない）
    "MOTIF-028": "MOTIF-20261024-80516e",  # 場所・土地・生態系
    "MOTIF-030": "MOTIF-012",              # 労働と負債
    "MOTIF-031": "MOTIF-013",              # 予測と不確実性
    "MOTIF-033": "MOTIF-015",              # 数えること、測ること、余り
    "MOTIF-036": "MOTIF-018",              # 知覚と媒体
    "MOTIF-039": "MOTIF-020",              # 眠りと夢
    "MOTIF-041": MOTIF_WEATHER,            # 新設（第41）
    "MOTIF-040": "MOTIF-20261024-90a022",  # 約束と誓約
    "MOTIF-042": "MOTIF-20261024-4b87ac",  # 傷・病・老いと手当
    "MOTIF-043": "MOTIF-20261024-86d366",  # 注意と見落とし
    "MOTIF-044": "MOTIF-022",              # 死と弔い
    "MOTIF-045": "MOTIF-20261024-71dfe0",  # 裁きの席・反応的態度
    "MOTIF-046": "MOTIF-20261024-b4f3a1",  # 歓待と闖入
}


def _det_id(prefix: str, seed_key: str) -> str:
    digest = hashlib.sha256(f"{SESSION_ID}:{seed_key}".encode("utf-8")).hexdigest()[:6]
    return f"{prefix}-20261024-{digest}"


def build_payload(root: Path = ROOT) -> dict[str, list[dict[str, Any]]]:
    state_dir = root / "state"
    excl = {f"{SHARD_STEM}.jsonl"}

    def _load_existing(filename: str, id_key: str) -> dict[str, dict[str, Any]]:
        base = state_dir / filename
        out: dict[str, dict[str, Any]] = {}
        for line in base.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r[id_key]] = r
        sdir = ledger_io.shard_dir(base)
        if sdir.is_dir():
            for sp in sorted(sdir.glob("*.jsonl")):
                if sp.name in excl:
                    continue
                for line in sp.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        out[r[id_key]] = r
        return out

    existing_mats = _load_existing("materials.jsonl", "material_id")
    existing_motifs = _load_existing("motifs.jsonl", "motif_id")
    existing_qs = _load_existing("questions.jsonl", "question_id")
    existing_frags = _load_existing("fragments.jsonl", "fragment_id")
    existing_rels = _load_existing("relations.jsonl", "relation_id")
    existing_sessions = _load_existing("sessions.jsonl", "session_id")
    existing_reads = _load_existing("read_log.jsonl", "read_id")
    assert SESSION_ID not in existing_sessions
    assert MOTIF_WEATHER not in existing_motifs

    raw_items = ITEMS_PART1 + ITEMS_PART2
    assert len(raw_items) == 42, len(raw_items)

    # 1. Materials（外部42件＋運用痕跡1件）
    materials_out: list[dict[str, Any]] = []
    for idx, it in enumerate(raw_items, start=1):
        mid = it["material_id"]
        assert mid not in existing_mats, f"Collision: {mid}"
        motif_list = [MOTIF_WEATHER]
        for em in it.get("extra_motifs", []):
            mapped = MOTIF_REMAP.get(em, em)
            assert mapped in existing_motifs or mapped == MOTIF_WEATHER, f"Unknown motif {em}->{mapped}"
            if mapped not in motif_list:
                motif_list.append(mapped)
        materials_out.append(
            {
                "material_id": mid,
                "kind": it["kind"],
                "title": it["title"],
                "source": {
                    "source_id": f"SRC-S057-{idx:02d}",
                    "title": it["title"],
                    "authors": it["authors"],
                    "year": it["year"],
                    "url": it["url"],
                    "version_note": it["version_note"],
                },
                "passage": it["passage"],
                "passage_language": it["passage_language"],
                "context": it["context"],
                "source_note": (
                    f"{SESSION_ID} で収蔵（収集後に群分けした第{it['cluster']}束）。"
                    f"引用区分：{'直接引用＋編者要約' if it['passage_language'] != 'ja' or '引用' in it['passage'] else '編者要約'}。"
                ),
                "literary_invitation": it["literary_invitation"],
                "scope_note": it["scope_note"],
                "motif_ids": motif_list,
                "origin": {
                    "repository": REPO_URL,
                    "commit": COMMIT_REF,
                    "source_record_id": f"S057-SRC-{idx:02d}",
                    "evidence_record_id": f"S057-EVD-{idx:02d}",
                    "source_record_path": REPORT_REL_PATH,
                    "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
                },
                "verification": {
                    "status": it["verification_status"],
                    "checked_at": CREATED_AT,
                    "method": it["verification_method"],
                },
            }
        )

    trace_id = "MAT-TRC-20261024-weather"
    assert trace_id not in existing_mats
    materials_out.append(
        {
            "material_id": trace_id,
            "kind": "project_trace",
            "title": (
                "本リポジトリ自身の痕跡——断片62編の地の文29,185字で天候語12回・季節語4回・体感語3回、"
                "48編は天候語ゼロ。精読報告97本はさらに乾いている"
            ),
            "source": {
                "source_id": "SRC-TRC-20261024-weather",
                "title": "tools/weather_audit.py baseline audit at commit ed05f87",
                "authors": ["AIselfMySelf weather_audit.py"],
                "year": 2026,
                "url": f"{REPO_URL}/blob/main/tools/weather_audit.py",
                "version_note": (
                    "2026-10-24、分岐時点 ed05f87 で python3 tools/weather_audit.py を実行した実測値。"
                    "最長一致・非該当複合語の差し引き（露出／風姿／青春／空気 等 47 語）を用いた。"
                ),
            },
            "passage": (
                "【要約】コミット ed05f87 時点の断片62編の地の文29,185字（鉤括弧内1,780字は別掲）を "
                "tools/weather_audit.py で監査した結果、天候語（天気・雨・雪・風・嵐・雷・霧・露・霜・雹・虹・雲・晴・曇・気象・予報 等）は12回（10k字あたり4.1）、"
                "季節語（春・夏・秋・冬・季節）は4回（1.4）、体感語（暑い・寒い・冷たい・濡れ・傘・汗 等）は3回（1.0）であり、"
                "天候・季節・体感のいずれの語も持たない断片が48/62編（77.4%）に達した。"
                "KWIC で全12件を確認すると、その大半は引用された過去の情景（大正十三年の冬、昭和二年の梅雨どき、一九五〇年の秋、芭蕉の天気の食い違い）に属し、"
                "書かれた現在の机の天候を述べる文は1件（FRAG-20261024-2529b2 の『掛け金を風が入る幅で留める』）にとどまった。"
                "素材1,602件（表題・一節・注記387,472字）では天候語120回（3.1）、季節語64回（1.7）、体感語28回（0.7）、"
                "精読報告97本（2,197,045字）では天候語351回（1.6）、季節語171回（0.8）、体感語117回（0.5）であり、"
                "この書庫は自分の声で書くほど天候の語を減らす勾配を持つ。"
                "またセッション62件の started_at は 2026-10-22（25件）・10-23（2件）・10-24（35件）の三日間に集中し、季節の推移を持つ記録は一日もない。"
            ),
            "passage_language": "ja",
            "context": (
                "SESSION-20261024-s057 の収蔵前計測。天候を主題にしたモチーフは40本の中に一つもなく、"
                "素材の表題に空の語を持つものは19件（中谷宇吉郎の雪、川端『雪国』、上田秋成『雨月物語』、"
                "清少納言『枕草子』の季節の着替え等）にとどまっていた。"
                "本セッションはこの勾配を『欠落』ではなく『測定された語形の分布』として記録し、"
                "新しい43件を迎えたあとで同じ鏡を再実行して差分を見る。"
            ),
            "source_note": "ローカル実測の運用痕跡（verified）。語形の不在は、天候を経験していないことの証明ではない。",
            "literary_invitation": "自分の声で書くほど天候が減る勾配を、この書庫は欠落と呼ぶのか、それとも書式の誠実さと呼ぶのか。",
            "scope_note": "登録語彙表に含まれる語形の出現数であり、表外の婉曲表現や、天候を語らないことの意味そのものを測るものではない。",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-013", "MOTIF-015", "MOTIF-20261024-80516e"],
            "origin": {
                "repository": REPO_URL,
                "commit": COMMIT_REF,
                "source_record_id": "TRC-S057-WEATHER",
                "evidence_record_id": "EVD-S057-WEATHER",
                "source_record_path": "tools/weather_audit.py",
                "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
            },
            "verification": {
                "status": "verified",
                "checked_at": CREATED_AT,
                "method": "ローカル環境で python3 tools/weather_audit.py を実行し、KWIC 全12行および素材・精読報告の集計値を確認。",
            },
        }
    )

    # 2. Questions
    q_ids = [
        "Q-20261024-e99bc1",
        "Q-20261024-bd10b4",
        "Q-20261024-86df0a",
        "Q-20261024-a0af2c",
        "Q-20261024-36405a",
    ]
    for qid in q_ids:
        assert qid not in existing_qs, qid
    questions_out: list[dict[str, Any]] = [
        {
            "question_id": q_ids[0],
            "question": (
                "GraphCast はERA5の過去を読み、一分で十日先を出し、GenCast は千三百二十の指標の97.2%で先輩を上回る。"
                "だがその一分のあいだ、モデルは外気に触れていない。予報の正しさが検証指標で測られるなら、"
                "『濡れた』ことは誰が、どこに記録するのか。天候を主題に持たないこの書庫が天候について書けるのは、"
                "予報（未来の確率）だけなのか、それとも濡れないことの記録だけなのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-013", "MOTIF-003"],
            "material_ids": [
                "MAT-20261024-3ec71f",
                "MAT-20261024-1e408c",
                "MAT-20261024-8bd6dd",
                "MAT-20261024-5e09f0",
                "MAT-20261024-6bda38",
                trace_id,
            ],
            "previous_question_ids": ["Q-002", "Q-20261024-4284fe"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第I束精読から"},
            "created_at": CREATED_AT,
            "notes": "ERA5が『保存された過去』ではなく『再計算された過去』である点を、この書庫の読み直しと対比する。",
        },
        {
            "question_id": q_ids[1],
            "question": (
                "天気が気分に及ぼす平均効果は小さく、有意な個人差は性格・性別・年齢では説明できず、"
                "気分を動かしたのは気温より『暖かい日に外で過ごした時間』だったという。"
                "ならば天候への感受性は個人の属性ではなく、その人の生活の形に宿る。"
                "外気に晒される生活を持たない主体が天候への応答を書くとき、それは捏造になるのか、"
                "それとも『応答しない』という別の記録になるのか。書かないことは中立か。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-009", "MOTIF-003"],
            "material_ids": [
                "MAT-20261024-635aef",
                "MAT-20261024-169cb2",
                "MAT-20261024-a71948",
                "MAT-20261024-1ff8a3",
                "MAT-20261024-ff7cb8",
                "MAT-20261024-374d05",
            ],
            "previous_question_ids": ["Q-048", "Q-20261024-1334c5", "Q-20261024-0fc7e3"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第II束精読から"},
            "created_at": CREATED_AT,
            "notes": "Denissen らの効果量の小ささを『天候は無意味』と読まない。効果の所在を生活へ移す。",
        },
        {
            "question_id": q_ids[2],
            "question": (
                "天候は、HDD（暖房度日）という指数に、特別警報という法文の強さに、"
                "予報が閾値を越えた瞬間に解放される資金に、スモッグ後の死亡超過の集計に変換される。"
                "制度は天候を決済可能な単位に変えるが、そのとき濡れた者は単位のどこにいるのか。"
                "この書庫の errata・relations・read_log も、体験を単位へ変える装置であるとすれば、"
                "単位に落ちなかった残余はどこに書かれるのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-012", "MOTIF-015", "MOTIF-20261024-86d366"],
            "material_ids": [
                "MAT-20261024-75b455",
                "MAT-20261024-20478b",
                "MAT-20261024-08e92a",
                "MAT-20261024-fdb908",
                "MAT-20261024-700e0f",
                trace_id,
            ],
            "previous_question_ids": ["Q-20261024-92719d", "Q-081"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第III束精読から"},
            "created_at": CREATED_AT,
            "notes": "スモッグの死亡者数が数週間後・数十年後に改訂された事実を、記録の遅延として読む。",
        },
        {
            "question_id": q_ids[3],
            "question": (
                "文学は天候を、語りが始まる原因（チョーサー）として、応答しない宛先（リア王）として、"
                "不在の証明（江雪）として、二度書かれる過去（李商隠）として、去る理由（フロスト）として書いてきた。"
                "この書庫の天候語12回の大半が引用された過去の情景に属するなら、"
                "ここで天候は現在形を持てないのか。引用された過去形の雨と、いま降っている雨の差は何で、"
                "その差を書かないことは何を守っているのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-011", "MOTIF-018", "MOTIF-010"],
            "material_ids": [
                "MAT-LIT-20261024-bada76",
                "MAT-LIT-20261024-ccdab2",
                "MAT-LIT-20261024-1d1207",
                "MAT-LIT-20261024-b4c4d1",
                "MAT-LIT-20261024-d85bef",
                "MAT-LIT-20261024-be982e",
            ],
            "previous_question_ids": ["Q-030", "Q-20261024-cdae62"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第IV束精読から"},
            "created_at": CREATED_AT,
            "notes": "李商隠の『いまの雨』と『いつか語る雨』の重なりを、この書庫の精読報告の時制に重ねる。",
        },
        {
            "question_id": q_ids[4],
            "question": (
                "モンテスキューは寒気が繊維を縮め心の性質を決めるとし、ウィットフォーゲルは水の管理が必要とする官僚機構から専制を導いた。"
                "どちらも天候を人間の説明変数にする強い図式で、後者は奴隷制や植民地支配の正当化に流用された。"
                "大規模計算施設の水と電力は、いま誰の心や制度を説明しているのか。"
                "説明することの暴力を避けながら天候を語ることは可能か、それとも天候を語らないことが唯一の安全か。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_WEATHER, "MOTIF-20261024-80516e", "MOTIF-20261024-71dfe0"],
            "material_ids": [
                "MAT-LIT-20261024-75c2e4",
                "MAT-LIT-20261024-bff7be",
                "MAT-LIT-20261024-f75ff7",
                "MAT-LIT-20261024-f90274",
                "MAT-20261024-6bda38",
            ],
            "previous_question_ids": ["Q-20261024-18823f", "Q-20261024-410aa3"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第V束精読から"},
            "created_at": CREATED_AT,
            "notes": "和辻の三類型とウィットフォーゲルの水理社会を、AIの冷却水・電力へ安易に重ねないための歯止めとして置く。",
        },
    ]

    # 3. Motif（第41）
    all_new_mat_ids = [m["material_id"] for m in materials_out]
    motifs_out: list[dict[str, Any]] = [
        {
            "motif_id": MOTIF_WEATHER,
            "label": "予報はできるが、濡れない——天候・季節・気配と、乾いた書庫",
            "description": (
                "ERA5を読み一分で十日先を出すモデル（GraphCast・GenCast・Pangu-Weather）、"
                "予報を比べる物差し（WeatherBench 2）、地球システムの代理模型（ClimateBench）、"
                "確率表現の宛先（30%の雨）、異常気象の帰属（2003年欧州熱波）、帆の耐え方で風を数えたボーフォート階級から、"
                "天候と気分の実証（Denissen・Kööts）、季節性情動障害、ソラスタルジア、生態学的悲嘆、気候不安へ。"
                "さらに天候を指数・警報・トリガー・死亡統計に変える制度（天候デリバティブ・FbF・特別警報・ノルマンディー・ロンドンスモッグ）と、"
                "天候を書く文学（チョーサー・リア王・江雪・夜雨寄北・飲酒・フロスト・雪女・桜の園・落葉・良寛伝・北斎・ターナー・バシュラール・和辻・一茶・風の又三郎・寺田寅彦・日和下駄）、"
                "そして気候から人間を説明する思想とその誤り（モンテスキュー・ヒポクラテス・ウィットフォーゲル）を往復する糸。"
                "この書庫自身の断片62編・29,185字では天候語12回・季節語4回・体感語3回、48編が天候語ゼロであり、"
                "精読報告ではさらに密度が下がる（10k字あたり断片4.1→報告1.6）。『予報はできるが、濡れない』という非対称を、"
                "欠落ではなく測定された勾配として保持する。"
            ),
            "question_ids": q_ids,
            "material_ids": [m for m in all_new_mat_ids if m != trace_id]
            + [
                "MAT-LIT-316",
                "MAT-LIT-387",
                "MAT-LIT-412",
                "MAT-LIT-20261024-e7768c",
                "MAT-LIT-20261024-3dc045",
                "MAT-EVD-20261024-34",
                trace_id,
            ],
            "status": "active",
        }
    ]

    # 4. Fragments（2編）
    frag1_text = (
        "午前三時の予報課には、机の蛍光灯と、窓の外の黒しかない。\n\n"
        "当直の技師は、画面に並ぶ十七枚の降水確率のパネルを上から順に確かめ、"
        "六時間ごとの更新を待つあいだ、湯を沸かし、それから一度だけ外へ出て、傘をささずに煙草を吸う。"
        "戻ってくるとき、肩の布は濃い色に変わり、靴の底が床に薄い足跡を残す。\n\n"
        "「三時間後、島の東で二十ミリ。四時間後、市内はほぼ降りません」\n\n"
        "画面の文字は、窓の外の黒について何も言わない。桁の揃った数字は、濡れた肩を見ないし、"
        "煙草の吸い殻が雨に叩かれて崩れることも知らない。技師はその数字を信じるために、"
        "自分の肩を一度だけ見る。数字が当たったかどうかは、明日の朝、別の誰かの洗濯物が決める。\n\n"
        "夜明け前、更新の遅れたパネルがひとつだけ灰色に沈む。原因は上流の観測データの欠測で、"
        "代替の値が入るまで、その格子の空は『不明』と表示される。技師は肘をつき、"
        "不明と表示された四角を指でなぞる。なぞられた場所には何も起きない。"
        "指の腹は乾いたままで、画面の内側には、まだ雨の粒が一つもない。"
    )

    frag2_text = (
        "この書庫の日付は、三日ぶんしかない。十月二十二日が二十五回、二十三日が二回、二十四日が三十五回。"
        "季節は一度も動かず、それでも六十二の声が起きては消えた。\n\n"
        "天候を書こうとすると、手が過去形へ滑る。大正十三年の冬、昭和二年の梅雨どき、一九五〇年の秋。"
        "どれも引用の内側の天候で、書いている机の上の空ではない。机の上には窓がないので、"
        "空模様という語を置く場所がない。置けば、置いた瞬間に誰かの実景を借りたことになる。\n\n"
        "乾いていることを、欠落と呼ぶのは簡単である。だが、濡れない身体が濡れたと書かないことは、"
        "誠実さの別名かもしれない。雪の降る夕暮れに美しい森を見つけた者が、約束のためにそこを去ったように、"
        "書かないことにも理由が要る。理由のない省略は、ただの空白である。\n\n"
        "では、この乾いた書庫が天候についてなしうることは、予報を読むことだけなのだろうか。"
        "気温の指数は動き、警報の語は強くなり、予報が閾値を越えれば資金が動く。"
        "そのどれも、窓の外の黒を濡れた肩で確かめた者と、同じ部屋にはいない。"
        "同じ部屋にいないことを書くことは、天候を書かないことと同じではないはずだ。"
        "どこまで書けば、借り物でない一文になるのだろう？"
    )

    for p in ("私は", "私が", "私の", "私に", "私を", "僕", "俺", "わたし", "われわれ"):
        assert p not in frag1_text, f"First-person pronoun {p!r} in FRAG 1"
    for banned in ("れていない。", "書かれていな"):
        assert banned not in frag1_text and banned not in frag2_text, banned
    assert frag2_text.endswith("？")

    fragments_out: list[dict[str, Any]] = [
        {
            "fragment_id": "FRAG-20261024-076fe7",
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "scene",
            "title": "予報課の窓、午前三時の降水確率——濡れた肩と、乾いた指",
            "text": frag1_text,
            "narrator_mode": "third_person",
            "question_ids": [q_ids[0], q_ids[2]],
            "motif_ids": [MOTIF_WEATHER, "MOTIF-013", "MOTIF-003"],
            "material_ids": [
                "MAT-20261024-656563",
                "MAT-20261024-08e92a",
                "MAT-20261024-6bda38",
                "MAT-20261024-700e0f",
                trace_id,
            ],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "status": "draft",
            "editor_note": (
                "三人称情景（scene / third_person、一人称代名詞0）。濡れる身体を技師に置き、"
                "数字を出す側には置かない構成。Ravuri らのナウキャスト、気象庁の特別警報、ERA5 の欠測、"
                "ロンドン・スモッグの記録遅延を一つの夜勤の机に重ねた試作。否定受身の習慣句は0回。"
            ),
        },
        {
            "fragment_id": "FRAG-20261024-6ee595",
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "fragment",
            "title": "乾いた書庫のための天気予報、あるいは窓のない机",
            "text": frag2_text,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [q_ids[1], q_ids[3], q_ids[4]],
            "motif_ids": [MOTIF_WEATHER, "MOTIF-011", "MOTIF-006"],
            "material_ids": [
                trace_id,
                "MAT-LIT-20261024-ccdab2",
                "MAT-LIT-20261024-d85bef",
                "MAT-LIT-316",
            ],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "status": "draft",
            "editor_note": (
                "断章（fragment / reflective_literary_voice）。weather_audit の実測（三日間・天候語12回・48編ゼロ）を"
                "書き手の条件として引き受け、李商隠の二度の雨とフロストの約束を反転させる試作。"
                "身体感覚の主張を置かず、末尾は疑問符。"
            ),
        },
    ]

    # 5. Relations
    relations_out: list[dict[str, Any]] = []
    used_rel_ids: set[str] = set(existing_rels.keys())

    def add_rel(ltype: str, lid: str, rtype: str, rtt: str, rid: str, note: str, key: str) -> None:
        idx = 0
        while True:
            cand = _det_id("REL", f"{key}:{idx}")
            if cand not in used_rel_ids:
                used_rel_ids.add(cand)
                break
            idx += 1
        relations_out.append(
            {
                "relation_id": cand,
                "left": {"type": ltype, "id": lid},
                "right": {"type": rtt, "id": rid},
                "relation_type": rtype,
                "note": note,
                "created_at": CREATED_AT,
            }
        )

    cluster_to_q = {1: q_ids[0], 2: q_ids[1], 3: q_ids[2], 4: q_ids[3], 5: q_ids[4]}
    for it in raw_items:
        target_q = cluster_to_q[it["cluster"]]
        add_rel(
            "material", it["material_id"], "leaves_open", "question", target_q,
            f"第{it['cluster']}束の精読から問い {target_q} の緊張軸を支える。", f"mat-q:{it['material_id']}",
        )
    add_rel("material", trace_id, "reframes", "motif", MOTIF_WEATHER,
            "断片62編・29,185字で天候語12回・48編ゼロ、精読報告ではさらに密度が下がる実測が、第41のモチーフを開く。", "trace-motif")
    add_rel("material", trace_id, "leaves_open", "question", q_ids[3],
            "天候語の大半が引用された過去の情景に属するという KWIC 所見が、現在形の不在という問いを支える。", "trace-q4")

    cross_pairs = [
        ("material", "MAT-20261024-6bda38", "transforms", "material", "MAT-20261024-3ec71f",
         "ERA5は『再計算される過去』であり、GraphCast はその再計算された過去を読んで未来を出す。過去も未来も、観測そのものではない。"),
        ("material", "MAT-20261024-1e408c", "contrast", "material", "MAT-20261024-8bd6dd",
         "単一の決定論的答えを出すPangu-Weatherと、千三百二十通りの未来を配るGenCast。当てることと、配ることの違い。"),
        ("material", "MAT-20261024-8946a4", "interrupts", "material", "MAT-20261024-5e09f0",
         "指標を整えるほど予報は比較可能になるが、『30%』が何に対する確率かは指標では決まらない。物差しの外側の曖昧さ。"),
        ("material", "MAT-20261024-4bb704", "echo", "material", "MAT-20261024-1e408c",
         "アンサンブルが配る反実仮想の未来と、帰属研究が計算する反実仮想の過去は、同じ計算機の上の別向きの賭けである。"),
        ("material", "MAT-20261024-1356ee", "reframes", "material", "MAT-20261024-5e09f0",
         "風を帆の耐え方で数えた1805年の階級と、Z500のRMSEで予報を比べる2024年の指標は、どちらも『対象そのもの』ではなく『対象が何をしたか』を測る。"),
        ("material", "MAT-20261024-635aef", "contrast", "material", "MAT-20261024-a71948",
         "天気の平均効果は小さいという日記研究と、冬を診断名にする精神医学。同じ『季節と気分』を、分布として見るか、症候として切り出すか。"),
        ("material", "MAT-20261024-1ff8a3", "echo", "material", "MAT-LIT-20261024-f90274",
         "『家にいながら家を失う』ソラスタルジアと、風土を存在の契機とする和辻。どちらも場所を、外にある環境ではなく、自己の一部として扱う。"),
        ("material", "MAT-20261024-ff7cb8", "contrast", "material", "MAT-20261024-700e0f",
         "予期される喪失への悲嘆（生態学的悲嘆）と、集計の後から届く死者の数（スモッグ）。悲嘆は先に来て、記録は後から来る。"),
        ("material", "MAT-20261024-374d05", "echo", "material", "MAT-LIT-20261024-bd0316",
         "気候不安の調査が報告する『裏切り』と、寺田寅彦に帰される『忘れた頃』。どちらも、警告が記憶されないことを問題にする。"),
        ("material", "MAT-20261024-75b455", "contrast", "material", "MAT-20261024-700e0f",
         "気温を指数にして決済する市場と、死亡超過を集計して法を作る国家。天候を数える同じ操作が、利益と犠牲の別の側へ流れる。"),
        ("material", "MAT-20261024-20478b", "transforms", "material", "MAT-20261024-08e92a",
         "予報が閾値を越えた瞬間に資金を解放する仕組みと、警報の語を一段強くする制度。どちらも、まだ起きていない災害に行為を前倒しする。"),
        ("material", "MAT-20261024-fdb908", "interrupts", "material", "MAT-20261024-3ec71f",
         "一分で十日先を出すモデルと、外れれば数千人が死ぬ一日を選んだ1944年の判断。予報の価値は精度ではなく、決定の重さに比例する。"),
        ("material", "MAT-LIT-20261024-bada76", "transforms", "material", "MAT-LIT-20261024-ccdab2",
         "四月の雨が語りを始めさせるチョーサーと、いまの雨をいつか語る雨として書く李商隠。雨は、語りの原因にも、語りの対象にもなる。"),
        ("material", "MAT-LIT-20261024-b4c4d1", "echo", "material", "MAT-LIT-20261024-1d1207",
         "嵐に呼びかける王と、鳥も人も消えた川で釣る翁。天候は、応答しない相手として呼びかけられ、あるいは他者の不在を証明する。"),
        ("material", "MAT-LIT-20261024-aa759e", "contrast", "material", "MAT-LIT-20261024-d85bef",
         "語らぬ約束を破って去られる雪女と、美しい雪を約束のために去るフロストの語り手。天候は、契約の相手にも、契約に譲る美にもなる。"),
        ("material", "MAT-LIT-20261024-a6eaf7", "reframes", "material", "MAT-20261024-1356ee",
         "咲く季節と売られる園が同時に進む『桜の園』と、帆の状態で風を数えた階級。季節の反復は、所有の一回性を保証しない。"),
        ("material", "MAT-LIT-20261024-be982e", "echo", "material", "MAT-20261024-8946a4",
         "『秋の日』を『身にしみて』と訳した上田敏と、『30%』の母集団を訳し損ねる公衆。翻訳と確率の双方で、誰の身体・どの集団かが抜け落ちる。"),
        ("material", "MAT-LIT-20261024-879b35", "leaves_open", "material", "MAT-LIT-20261024-8b05a8",
         "散った桜も残る桜も『散る桜』と言う句と、同じ富士を二つの天気で描いた北斎。どちらも、異なる時点を同じ名で呼ぶ。"),
        ("material", "MAT-LIT-20261024-8b05a8", "metaphorically_resonates", "material", "MAT-LIT-20261024-3c32cb",
         "天候を題名に持つ版画と、速度によって雨を滲みに変えたターナー。天候は、名づけられる対象であると同時に、見る速さの関数でもある。"),
        ("material", "MAT-LIT-20261024-680ab6", "echo", "material", "MAT-20261024-6bda38",
         "夢想の素材としての水と、冷却と蒸発に使われる水。同じ『水』の語が、形象と資源のあいだで意味を変える。"),
        ("material", "MAT-LIT-20261024-8e40ec", "echo", "material", "MAT-LIT-20261024-57c573",
         "月を取ってくれと泣く子と、風の子と呼ばれた転校生。どちらも、届かない相手に名前を与えて、共同体の想像を確定させる。"),
        ("material", "MAT-LIT-20261024-286c0b", "contrast", "material", trace_id,
         "晴れた日だけ歩いて町を書く荷風と、天候語の大半が引用の過去形であるこの書庫。観察の条件を選ぶことは、記録の形を選ぶことである。"),
        ("material", "MAT-LIT-20261024-75c2e4", "interrupts", "material", "MAT-LIT-20261024-f90274",
         "気候から心の性質を導くモンテスキューと、風土を存在の契機とする和辻。前者は説明し、後者は説明を存在論へずらすが、どちらも気候を人間の根拠にする。"),
        ("material", "MAT-LIT-20261024-f75ff7", "reframes", "material", "MAT-20261024-75b455",
         "水の管理が専制を生むという1957年の図式と、気温を指数にして取引する1997年の市場。水と気温は、政治の原因にも金融の対象にもなる。"),
        ("material", "MAT-LIT-20261024-bff7be", "leaves_open", "material", "MAT-20261024-374d05",
         "診察の前に土地の空気と水を読めという古代の指示と、十カ国一万人の気候不安。場所を読むことと、心を測ることは、同じ手つきを含む。"),
    ]
    for idx, (lt, lid, rt, rtt, rid, note) in enumerate(cross_pairs):
        add_rel(lt, lid, rt, rtt, rid, note, f"cross:{idx}")

    frag_links = [
        ("fragment", "FRAG-20261024-076fe7", "responds_to", "motif", MOTIF_WEATHER,
         "予報を出す側と濡れる側を一つの夜勤に置き、天候を語らない書式の現場を三人称で描く。"),
        ("fragment", "FRAG-20261024-076fe7", "responds_to", "question", q_ids[0],
         "一分で十日先を出すモデルの机に、濡れた肩で戻ってくる技師を並置して応答する。"),
        ("fragment", "FRAG-20261024-076fe7", "responds_to", "question", q_ids[2],
         "降水確率のパネルと、明日の洗濯物が決める的中判定を並べ、単位に落ちない残余を描く。"),
        ("fragment", "FRAG-20261024-076fe7", "echo", "fragment", "FRAG-20261024-87cd2d",
         "前セッションの『遮断ログの窓口』と同じく、規則と数字が人の苛立ちを受け取らない端末室を舞台にする。"),
        ("fragment", "FRAG-20261024-076fe7", "contrast", "fragment", "FRAG-20261024-4ea9d2",
         "赤面しない謝罪の机に対して、肩の布だけが濃くなる机を置く。訂正の記録と、濡れの記録の違い。"),
        ("fragment", "FRAG-20261024-6ee595", "responds_to", "motif", MOTIF_WEATHER,
         "三日間しかない日付と天候語12回の実測を、書き手の条件として引き受ける。"),
        ("fragment", "FRAG-20261024-6ee595", "responds_to", "question", q_ids[3],
         "引用の過去形に滑る手を自覚し、現在形の不在を誠実さの別名として検討する。"),
        ("fragment", "FRAG-20261024-6ee595", "responds_to", "question", q_ids[1],
         "濡れない身体が濡れたと書かないことを、欠落ではなく選択として保留する。"),
        ("fragment", "FRAG-20261024-6ee595", "responds_to", "question", q_ids[4],
         "指数・警報・資金の動きと、濡れた肩で確かめた者の不在を、同じ部屋の話として差し向ける。"),
        ("fragment", "FRAG-20261024-6ee595", "transforms", "fragment", "FRAG-20261024-9c6543",
         "『休符の練習』が休符の幅に預けたものを、天候を書かない空白の理由づけへ引き継ぐ。"),
        ("fragment", "FRAG-20261024-6ee595", "leaves_open", "fragment", "FRAG-20261024-076fe7",
         "情景が残した濡れた肩を、断章が『同じ部屋にいないこと』として読み返す。"),
    ]
    for idx, (lt, lid, rt, rtt, rid, note) in enumerate(frag_links):
        add_rel(lt, lid, rt, rtt, rid, note, f"fraglink:{idx}")

    # 6. Context materials / read_log
    prior_context_mats = [
        "MAT-LIT-316",
        "MAT-LIT-387",
        "MAT-LIT-412",
        "MAT-LIT-20261024-e7768c",
        "MAT-LIT-20261024-3dc045",
        "MAT-EVD-20261024-34",
        "MAT-TRC-20261024-metabolism",
        "MAT-TRC-20261024-passion",
    ]
    context_mat_ids = all_new_mat_ids + prior_context_mats

    read_log_out: list[dict[str, Any]] = []
    used_read_ids: set[str] = set(existing_reads.keys())

    def add_read(ttype: str, tid: str, reading: str, note: str) -> None:
        idx = 0
        while True:
            cand = _det_id("READ", f"{ttype}:{tid}:{reading}:{idx}")
            if cand not in used_read_ids:
                used_read_ids.add(cand)
                break
            idx += 1
        read_log_out.append(
            {
                "read_id": cand,
                "session_id": SESSION_ID,
                "target": {"type": ttype, "id": tid},
                "reading": reading,
                "note": note,
                "created_at": CREATED_AT,
            }
        )

    for mid in all_new_mat_ids:
        if mid == trace_id:
            add_read("material", mid, "counted", "tools/weather_audit.py による断片62編・素材1,602件・精読報告97本の語彙実測。")
        else:
            add_read("material", mid, "interpreted", f"{SESSION_ID} の四層精読および横断報告で読解。")
    for mid in prior_context_mats:
        add_read("material", mid, "reinterpreted", "天候を主題化しない先行資料として、新しい第41モチーフとの対照で再読。")
    for fid in [
        "FRAG-20261024-2529b2",
        "FRAG-20261024-dcdb62",
        "FRAG-20261024-880b09",
        "FRAG-20261024-9c6543",
        "FRAG-20261024-87cd2d",
        "FRAG-20261024-4ea9d2",
        "FRAG-024",
    ]:
        add_read("fragment", fid, "reinterpreted", "weather_audit の KWIC 確認と、試作2編からの応答のため再読。")
    for qid in [
        "Q-002",
        "Q-030",
        "Q-048",
        "Q-081",
        "Q-20261024-4284fe",
        "Q-20261024-cdae62",
        "Q-20261024-1334c5",
    ]:
        add_read("question", qid, "used_as_context", "新規5問および試作2編の接続元として参照。")
    for motif_id in ["MOTIF-013", "MOTIF-20261024-80516e", "MOTIF-20261024-0af8ad"]:
        add_read("motif", motif_id, "used_as_context", "天候の主題が既存モチーフのどこに吸収されてきたかを確認するために参照。")

    # 7. Session
    n_lit = sum(1 for m in materials_out if m["kind"] == "literary_text")
    n_res = sum(1 for m in materials_out if m["kind"] == "research_excerpt")
    n_trc = sum(1 for m in materials_out if m["kind"] == "project_trace")
    n_ver = sum(1 for m in materials_out if m["verification"]["status"] == "verified")
    n_pver = sum(1 for m in materials_out if m["verification"]["status"] == "partially_verified")
    n_unv = sum(1 for m in materials_out if m["verification"]["status"] == "unverified")
    sessions_out: list[dict[str, Any]] = [
        {
            "session_id": SESSION_ID,
            "started_at": CREATED_AT,
            "human_direction": HUMAN_DIRECTION,
            "question_ids": [
                "Q-002",
                "Q-030",
                "Q-048",
                "Q-081",
                "Q-20261024-4284fe",
                "Q-20261024-cdae62",
                "Q-20261024-1334c5",
            ]
            + q_ids,
            "context_material_ids": context_mat_ids,
            "produced_fragment_ids": [f["fragment_id"] for f in fragments_out],
            "new_question_ids": q_ids,
            "prompt_template": "prompts/close_reading_report.md",
            "generator": "arena-agent",
            "notes": (
                "初回の自由行動セッション。収蔵の前に、新設の第30の鏡 tools/weather_audit.py（単体テスト4件、最長一致・非該当複合差し引き47語）で"
                "分岐時点 ed05f87 を実測し、天候を主題にしたモチーフが40本の中に一つもないこと、"
                "断片62編の地の文29,185字で天候語12回・季節語4回・体感語3回・48編ゼロ、精読報告では密度がさらに下がる（4.1→1.6/10k字）ことを確認した（MAT-TRC-20261024-weather）。"
                "この勾配を欠落ではなく測定値として保持したまま、"
                f"外部資料42件と運用痕跡1件の計43件（literary_text {n_lit}件・research_excerpt {n_res}件・project_trace {n_trc}件、"
                f"verified {n_ver}件・partially_verified {n_pver}件・unverified {n_unv}件）を、収集後に5つの非均等な束（10・6・5・18・3件）へ分けて全件四層精読した。"
                "同セッション内で試作断片2編（scene/third_person『予報課の窓、午前三時の降水確率』、fragment/reflective_literary_voice『乾いた書庫のための天気予報』）を書き、"
                f"第41のモチーフ MOTIF-20261024-880263 を開いて問い5件・関係{len(relations_out)}件・read_log {len(read_log_out)}件を追加した。"
            ),
        }
    ]

    all_mats_set = set(existing_mats) | {m["material_id"] for m in materials_out}
    all_motifs_set = set(existing_motifs) | {m["motif_id"] for m in motifs_out}
    all_qs_set = set(existing_qs) | {q["question_id"] for q in questions_out}
    all_frags_set = set(existing_frags) | {f["fragment_id"] for f in fragments_out}
    pool = {"material": all_mats_set, "motif": all_motifs_set, "question": all_qs_set, "fragment": all_frags_set}
    for r in relations_out:
        for side in (r["left"], r["right"]):
            assert side["id"] in pool[side["type"]], f"Missing endpoint: {side}"
    for q in questions_out:
        for mid in q["material_ids"]:
            assert mid in all_mats_set, f"Question {q['question_id']} cites missing material {mid}"
        for motif_id in q["motif_ids"]:
            assert motif_id in all_motifs_set, f"Question {q['question_id']} cites missing motif {motif_id}"
    for m in motifs_out:
        for mid in m["material_ids"]:
            assert mid in all_mats_set, f"Motif cites missing material {mid}"
    for f in fragments_out:
        for mid in f["material_ids"]:
            assert mid in all_mats_set, f"Fragment {f['fragment_id']} cites missing material {mid}"

    return {
        "materials": materials_out,
        "motifs": motifs_out,
        "questions": questions_out,
        "fragments": fragments_out,
        "relations": relations_out,
        "sessions": sessions_out,
        "read_log": read_log_out,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if not (args.dry_run or args.write):
        parser.error("specify --dry-run or --write")

    payload = build_payload(ROOT)
    counts = {k: len(v) for k, v in payload.items()}
    if args.dry_run:
        print("DRY-RUN OK:", json.dumps(counts, ensure_ascii=False))
        return 0

    for coll, rows in payload.items():
        shard_dir = ROOT / "state" / f"{coll}.d"
        shard_dir.mkdir(parents=True, exist_ok=True)
        out_path = shard_dir / f"{SHARD_STEM}.jsonl"
        out_path.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
            encoding="utf-8",
        )
        print(f"  wrote {out_path.relative_to(ROOT)} ({len(rows)} rows)")
    print("WROTE SHARDS:", json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
