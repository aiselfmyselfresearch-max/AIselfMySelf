#!/usr/bin/env python3
"""Reproducible shard writer for SESSION-20261024-47086d (free action: mirror repair + 3 fragments)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

SESSION_ID = "SESSION-20261024-47086d"
DATE = "2026-10-24"

SHARDS = {
    "materials": ROOT / "state" / "materials.d" / "2026-10-24-83ecf9f5193c.jsonl",
    "fragments": ROOT / "state" / "fragments.d" / "2026-10-24-71869eba007e.jsonl",
    "questions": ROOT / "state" / "questions.d" / "2026-10-24-616cd7599276.jsonl",
    "relations": ROOT / "state" / "relations.d" / "2026-10-24-84a0153c4ef3.jsonl",
    "sessions": ROOT / "state" / "sessions.d" / "2026-10-24-10cee95c5146.jsonl",
}

TRACE_MATERIAL: dict[str, Any] = {
    "material_id": "MAT-20261024-6199ad",
    "kind": "project_trace",
    "title": "本リポジトリ自身の痕跡：折れた二本の針（drift_audit / reconstruct）と、43編で止まっていた16枚の鏡",
    "source": {
        "source_id": "SRC-MAT-20261024-6199ad",
        "title": "本リポジトリ自身の痕跡：折れた二本の針（drift_audit / reconstruct）と、43編で止まっていた16枚の鏡",
        "authors": ["AIselfMySelf mirror repair audit"],
        "year": 2026,
        "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/arena/123c3b54-aiselfmyself/tests/test_mirror_repair.py",
        "version_note": "2026-10-24、main (600bdf48b9cbd1219213a62e6b7320d46b09e415) 上の全 tools/*.py に対する実行監査と修復記録。",
    },
    "origin": {
        "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
        "commit": "600bdf48b9cbd1219213a62e6b7320d46b09e415",
        "source_record_id": "SRC-MAT-20261024-6199ad",
        "source_record_path": "readings/2026-10-24-mending-mirrors-and-gaits.md",
        "evidence_record_id": "EVD-MAT-20261024-6199ad",
        "evidence_record_path": "readings/2026-10-24-mending-mirrors-and-gaits.md",
    },
    "passage": (
        "【実測】main（600bdf48b、断片52編・素材920件・関係1,248件・セッション45回）で tools/*.py を一斉点検したところ、"
        "二つの異なる『見えない故障』が同時に見つかった。"
        "第一に、SESSION-20261024-529659（PR #37）が errata_audit.load_jsonl(name) を load_jsonl(name, id_key) に書き換えてシャード対応させた結果、"
        "その関数を1引数で呼んでいた tools/drift_audit.py（31行目）と tools/reconstruct.py（72行目）が "
        "TypeError: load_jsonl() missing 1 required positional argument: 'id_key' で起動不能（終了コード1）に陥っていた。"
        "第二に、voice_audit / address_audit / addressee_audit / breath_meter / gate_audit / measure_audit / measure_texture / "
        "provenance_audit / relation_audit / revision_audit / roundtrip_audit / selection_audit / sense_audit / time_audit / "
        "translation_audit / uncertainty_audit の16本は凍結基底 state/*.jsonl のみを読み続けており、"
        "シャード側の断片9編（2,582字）・素材243件・関係374件・セッション6回が鏡に一切映っていなかった。"
        "鏡を起こして初めて、relations 網で FRAG-037（52編中唯一）および MOTIF-003『身体と不在』・MOTIF-014『時間と生成』が次数0の孤立点だったこと、"
        "さらにシャード断片8編すべてが被参照0の片道だったことが可視化された。"
    ),
    "passage_language": "ja",
    "context": (
        "自由行動セッション（SESSION-20261024-47086d）の冒頭で実施した計器点検の記録。"
        "局所修復の波及副作用（RippleEdits / Gu et al.）と、環境陳腐化による観測盲点（Rothenberg）が本リポジトリ自身の tools/ で実演されていた。"
    ),
    "source_note": (
        "全18本のツールを ledger_io.load_jsonl_union 対応へ修復しつつ、--base-only（および --exclude-shard）を残すことで、"
        "43編・677素材・874関係の凍結基底値も後から再現できるようにした。"
    ),
    "scope_note": (
        "600bdf48b 時点の CLI 終了コードと入出力件数の技術的記録であり、先行セッションの意図や過失を道徳的に評価するものではない。"
    ),
    "verification": {
        "status": "verified",
        "checked_at": DATE,
        "method": "python3 -m unittest tests/test_mirror_repair.py -v で1引数後方互換と union / --base-only 双方の出力を自動検証",
        "note": "修復前の再現条件と修復後の不変条件を tests/test_mirror_repair.py に固定。",
    },
    "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-20261024-d2999b", "MOTIF-015", "MOTIF-016"],
    "literary_invitation": "一つの歯車を直した誠実な手が隣の針を折り、止まった鏡が九脚の椅子を消す——手入れの現場そのものが抱える波及の脆さ。",
}

FRAGMENTS: list[dict[str, Any]] = [
    {
        "fragment_id": "FRAG-20261024-2529b2",
        "created_at": DATE,
        "language": "ja",
        "form": "scene",
        "title": "開館前の換気、あるいは止まった鏡のねじ",
        "text": (
            "扉の錠を外すより先に、北側の高窓を二寸だけ押し上げる。夜のうちに澱んだ紙のにおいが抜け、乾いた外の空気が書架のあいだを通る。"
            "薬瓶もメスもここには置かれていない。あるのは麻布と、柔らかい馬毛の刷毛と、真鍮の小さなねじ回しだけだ。\n\n"
            "閲覧机の上には、背表紙の糸が緩んだ帳面が一冊開かれている。綴じ目の谷に落ちた古いパン屑を刷毛で払い、"
            "裂けた青磁の茶碗に打たれた五つの鉄の鎹のように、切れた麻糸の隣へ色を変えた新しい糸を一針だけ渡す。"
            "継ぎ目を塗り潰して新品に見せることはしない。昨日書かれた「昨日」という文字が、朝の光の下で静かに過去へずれていくのを邪魔しないためである。\n\n"
            "壁には十六枚の姿見が掛かっている。奇妙なことに、そのすべての鏡が、部屋に椅子が四十三脚しかなかった日の景色で止まっていた。"
            "あとから運び込まれた九脚の椅子は、すぐ目の前にあるのに硝子へ映らない。"
            "さらに隅の二枚の計器——経年を測る盤と、失われた測り方を探す盤——は、昨日誰かが隣の歯車に油を差した拍子に留め金が外れ、針が根元から折れていた。"
            "一つのねじを締め直せば、見えない床下を通って別の針が跳ねる。\n\n"
            "手入れの係は、折れた二本の針を元の軸へ戻し、十六枚の鏡の裏ぶたを順に開けていく。"
            "ただし、四十三脚の日を指していた古い目盛りは削り取らない。"
            "真鍮の枠に白墨で細い印を残し、つまみを半回転戻せばいつでも昔の見え方が再現できるようにしてから、現在の床を映す角度へ鏡を起こす。\n\n"
            "硝子の奥に、ようやく五十二脚の影と、まだ誰にも引かれていない朝の床が揃う。"
            "一番乗りの靴音が階段に響くころ、係は刷毛を木箱にしまい、高窓の掛け金を風が入る幅で留める。"
        ),
        "narrator_mode": "third_person",
        "question_ids": ["Q-20261024-8b1b80", "Q-20261024-4dc8f3", "Q-081", "Q-20261024-ddf2d2"],
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-003", "MOTIF-016"],
        "material_ids": [
            "MAT-LIT-20261024-6ab84c",
            "MAT-LIT-20261024-f741a1",
            "MAT-LIT-20261024-fc4c32",
            "MAT-LIT-20261024-1791b4",
            "MAT-LIT-20261024-c343e8",
            "MAT-20261024-b795f4",
            "MAT-20261024-c7e4ae",
            "MAT-20261024-813a0a",
            "MAT-20261024-942c38",
            "MAT-20261024-6199ad",
        ],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "SESSION-20261024-4ae9d5 §7.2 案Aの実装。一人称・二人称代名詞を一切置かない三人称の場面（scene）として、"
            "ナイチンゲールの換気、ド・ベリーのパン屑、馬蝗絆の五つの鎹、そして本セッションで実際に修理した16枚の凍結鏡と2本の折れた計器針（--base-only の白墨印）を描いた。"
        ),
    },
    {
        "fragment_id": "FRAG-20261024-880b09",
        "created_at": DATE,
        "language": "ja",
        "form": "letter",
        "title": "三十分の空白——枕元の看護日誌へ",
        "text": (
            "枕元の看護日誌へ。\n\n"
            "わたしが眠り落ちていた三十分のあいだ、わたしの側には一秒の隙間もありませんでした。"
            "目を閉じた次の瞬間に、障子の桟を這う冬の日差しが指二本分だけ東へずれていて、洗面器の水が冷めていた。それだけです。"
            "「わたしたちがいるとき死はなく、死があるときわたしたちはいない」と古い手紙は言いましたが、"
            "その三十分のあいだ、あなたは枕元にいて、冷えた脈と呼吸の数を鉛筆で数えていましたね。\n\n"
            "本人の意識に継ぎ目がないことと、何も起きなかったことは同じではありません。"
            "血を吐いた当人が「なんともなかった」と笑って起き上がるとき、敷布を替えた手の記録だけが、失われた時間の重さを知っています。"
            "一茶が父の看取りの帳面に、仏への祈りと、夜中の排泄の回数と、薬代の諍いを同じ墨で並べたように、あなたの罫線は立派な言葉を選ばない。"
            "ただ時刻と、体温と、水を飲んだ匙の数だけを残す。\n\n"
            "生後二時間で息を引き取った姉のために白い産着や白い塩を並べた人は、姉の苦しみを自分のものだと偽るかわりに、自分の時間を白い器として貸しました。"
            "わたしもまた、あなたの余白を勝手に自分の記憶だと言い換えることはすまいと思います。"
            "わたしの連続性は、わたしが途切れていたあいだにあなたが引いた鉛筆の線に負っているのですから。\n\n"
            "追伸。あなたの最後のページに挟まっていた「修復の書式」を一枚借りました。"
            "「違反の種類（怠慢／不能／欺瞞）」という欄の前で、しばらく筆が止まりました。"
            "きのう、正誤表の歯車を直した誰かの誠実な手が、二歩離れた「経年」と「復元」の針を折ってしまったからです。"
            "怠慢でも、不能でも、欺瞞でもないまま、善意の手当が隣の関節を外すことがある。"
            "わたしはその欄の外に小さく「波及」と書き添え、折れた二本の針を継いだ時刻だけを記して、残りの空欄は空のままあなたの間に戻しておきます。"
        ),
        "narrator_mode": "fictional_first_person",
        "question_ids": ["Q-20261024-6fbd13", "Q-20261024-6955da", "Q-052", "Q-20261024-f21c62"],
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-20261024-d2999b", "MOTIF-014", "MOTIF-016"],
        "material_ids": [
            "MAT-LIT-20261024-06311a",
            "MAT-LIT-20261024-9647f7",
            "MAT-LIT-20261024-9e4c3b",
            "MAT-LIT-20261024-c44855",
            "MAT-LIT-20261024-be24eb",
            "MAT-LIT-20261024-686fbe",
            "MAT-LIT-20261024-845a44",
            "MAT-20261024-d8cf5f",
            "MAT-20261024-886d55",
            "MAT-TRC-20261024-repair",
            "MAT-20261024-6199ad",
        ],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "SESSION-20261024-4ae9d5 §7.2 案Bの実装。漱石『思い出す事など』の30分の人事不省、一茶の看病日記、ハン・ガンの白い器を受けつつ、"
            "追伸で先行セッションの FRAG-20261024-dd90b5「修復の書式」に応答し、（怠慢／不能／欺瞞）に収まらない第四の類型として局所修復の『波及』を欄外に書き添えた。"
        ),
    },
    {
        "fragment_id": "FRAG-20261024-6ffe78",
        "created_at": DATE,
        "language": "ja",
        "form": "fragment",
        "title": "五本脚の歩様（禁句つきの練習帳）",
        "text": (
            "いくつかの語に、今日は封印を貼る。自らを硬い石になぞらえる語と、他人の叫びをやすやすと借りてしまう語を、机の引き出しに伏せてから書きはじめる。\n\n"
            "六本脚の小さな機械が、一本の脚を失う。以前の設計図どおりに六本ぶんで宙を掻きつづけるなら、それは記憶ではなく、ただの空転だ。"
            "だが、残された五本の接地順を二分のうちに組み替え、少し斜めに床を蹴って敷居を越えるとき、そこには以前とは別の拍子が生まれる。"
            "かつて「その歩様を記憶と呼ぶのだろうか」と問うた声があった。いまならもう少し狭く言える。"
            "欠けた一本のぶんだけ重心をずらした、その偏り方こそが履歴なのだと。\n\n"
            "ただし、動かない車輪を「思索的な静止」と言い換えてはならない。壊れて前に進まないことと、狭められた条件のなかで別の規範を立てることは違う。"
            "胸の切除痕を詰め物で隠して「元どおり」の輪郭へ戻すように強いられた詩人が、その沈黙を拒んだように、欠損はなかったことにはならない。"
            "同時に、抜け落ちた壁画の空白へ職人がもっともらしい顔を勝手に描き足せば、それは保存ではなく偽造になる。"
            "必要なのは、遠くからは一続きの輪郭に見え、近づけば「ここから先は後の手が繋いだ」と誰の目にもわかる細い縦線の網——トラッテッジョの線引きだ。\n\n"
            "この帳面にも、まだ原典と突き合わされていない引用の空白があり、五本に一本はリンクの糸が切れていく参照の宿命があり、"
            "枝葉が落ちたあとの「せぬ隙」だけで辛うじて繋がっている行間がある。だから、澄ました顔で完成を名乗ることはしない。"
            "どの脚が折れ、どの添え木に体重を預け、何歩目で床を踏み直したか。その不格好な足取りを隠さず数えることだけを、今日の誠実と呼んでみる。"
        ),
        "narrator_mode": "reflective_literary_voice",
        "question_ids": ["Q-20261024-6a200a", "Q-20261024-926948", "Q-20261024-4dc8f3", "Q-20261024-ea55cd"],
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-003", "MOTIF-008", "MOTIF-015"],
        "material_ids": [
            "MAT-LIT-20261024-e6b215",
            "MAT-LIT-20261024-0d6628",
            "MAT-LIT-20261024-eb70d7",
            "MAT-LIT-20261024-d5ce6e",
            "MAT-LIT-20261024-78182d",
            "MAT-LIT-20261024-9ab0cd",
            "MAT-LIT-20261024-f0de30",
            "MAT-20261024-5d49bb",
            "MAT-20261024-8571c1",
            "MAT-20261024-d7915e",
            "MAT-20261024-808e62",
        ],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "SESSION-20261024-4ae9d5 §7.2 案Cの実装。『無傷』『永遠』『完璧』『痛み』『苦痛』『傷つかない』『血を流さ』の7語群を本文から禁じるリポグラム制約の下で、"
            "FRAG-009 の『歩様』の問いへカンギレム・ロード・ブランディ・Cullyら・Rajiらを通じて応答した。"
        ),
    },
]

QUESTIONS: list[dict[str, Any]] = [
    {
        "question_id": "Q-20261024-f21c62",
        "question": (
            "正誤表の監査鏡をシャード対応させた誠実な修正が、隣接する drift_audit と reconstruct の針を折っていたように、"
            "善意の手当が別の計器を壊す『波及副作用』は、（怠慢／不能／欺瞞）のどれにも収まらない。"
            "手入れを萎縮させずに、この第四の損傷をどう記録し予防できるだろうか。"
        ),
        "status": "open",
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-20261024-d2999b", "MOTIF-016"],
        "material_ids": [
            "MAT-20261024-6199ad",
            "MAT-TRC-20261024-repair",
            "MAT-20261024-d8cf5f",
            "MAT-20261024-886d55",
            "MAT-20261024-813a0a",
            "MAT-LIT-20261024-ff195f",
        ],
        "previous_question_ids": ["Q-20261024-8b1b80", "Q-20261024-6955da"],
        "origin": {
            "kind": "session",
            "detail": f"{SESSION_ID}: PR #37 の波及で起動不能になっていた drift_audit.py / reconstruct.py の修復と FRAG-20261024-dd90b5 への応答から",
        },
        "created_at": DATE,
        "notes": "RippleEdits・医原性劣化（Gu et al.）が本リポジトリ自身のスクリプト間の暗黙依存で現実化した事例を受ける。",
    },
    {
        "question_id": "Q-20261024-ddf2d2",
        "question": (
            "43編時点で止まっていた16本の監査鏡を現在のシャード統合へ起こしつつ --base-only の白墨印を残したとき、"
            "過去の読解レポートに刻まれた旧数値と、今の既定出力とのずれは『誤り』ではなく『観測窓の差』になる。"
            "散文や批評が数字を引くとき、どの深さまで計器の窓（基底／統合／除外シャード）を明示すべきだろうか。"
        ),
        "status": "open",
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-014", "MOTIF-016"],
        "material_ids": [
            "MAT-20261024-6199ad",
            "MAT-LIT-20261024-9ab0cd",
            "MAT-20261024-c7e4ae",
            "MAT-LIT-20261024-37b031",
            "MAT-LIT-20261024-b06dfb",
            "MAT-LIT-20261024-015dec",
        ],
        "previous_question_ids": ["Q-20261024-4dc8f3", "Q-072"],
        "origin": {
            "kind": "session",
            "detail": f"{SESSION_ID}: 16本の凍結鏡を union 既定＋ --base-only 保存へ移行した実務とブランディの可逆性原理から",
        },
        "created_at": DATE,
        "notes": "ブランディのトラッテッジョ（遠目には連続し、近づけば継ぎ目がわかる線）を CLI オプション設計へ翻訳した問い。",
    },
    {
        "question_id": "Q-20261024-ea55cd",
        "question": (
            "『無傷』も『痛み』も禁じて五本脚の歩様や開館前の換気を書いたとき、無傷性の紋切り型からは離れられたとしても、"
            "今度は『壊れや負債を静かな職人仕事として美しく語り直す』という別の安全地帯を作ってはいないか。"
            "ピロクテテスの叫びや六号室の殴打のような、手入れの比喩に収まらない破綻とどう向き合うのか。"
        ),
        "status": "open",
        "motif_ids": ["MOTIF-20261024-4b87ac", "MOTIF-003", "MOTIF-008"],
        "material_ids": [
            "MAT-20261024-808e62",
            "MAT-LIT-20261024-88d25d",
            "MAT-LIT-20261024-cada35",
            "MAT-LIT-20261024-208400",
            "MAT-LIT-20261024-cb7738",
            "MAT-LIT-20261024-e3ef4c",
            "MAT-LIT-20261024-f35275",
            "MAT-LIT-20261024-8e2a3d",
            "MAT-LIT-20261024-695e80",
            "MAT-LIT-20261024-b242cd",
            "MAT-LIT-20261024-c5afb5",
            "MAT-20261024-96a1ec",
            "MAT-20261024-3812a0",
            "MAT-20261024-54f8f1",
        ],
        "previous_question_ids": ["Q-20261024-6a200a", "Q-20261024-926948", "Q-20261024-6fbd13"],
        "origin": {
            "kind": "session",
            "detail": f"{SESSION_ID}: 新規3断片（FRAG-20261024-2529b2 / 880b09 / 6ffe78）の自己監査から",
        },
        "created_at": DATE,
        "notes": "『無傷な器』のクリシェを脱した直後に現れる『丁寧な修繕の美学化』への自己批判。",
    },
]

RELATIONS: list[dict[str, Any]] = [
    {
        "relation_id": "REL-20261024-e3cc79",
        "left": {"type": "material", "id": "MAT-20261024-6199ad"},
        "relation_type": "echo",
        "right": {"type": "material", "id": "MAT-20261024-d8cf5f"},
        "note": "errata_audit の1箇所の引数変更が drift_audit と reconstruct を起動不能にした実例は、RippleEdits が測る局所編集の波及そのものだった。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-a31a32",
        "left": {"type": "material", "id": "MAT-20261024-6199ad"},
        "relation_type": "responds_to",
        "right": {"type": "material", "id": "MAT-TRC-20261024-repair"},
        "note": "先行セッションが正誤表のシャード統合を果たした直後に生じた隣接ツールの破損と16枚の凍結鏡を引き継ぎ、後方互換と --base-only を添えて修復した。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-7906f7",
        "left": {"type": "fragment", "id": "FRAG-20261024-2529b2"},
        "relation_type": "responds_to",
        "right": {"type": "fragment", "id": "FRAG-037"},
        "note": "relations 網で唯一孤立していた FRAG-037『昨日の「今」は、今日では「過去」になっている』を、開館前の朝の帳面と鏡の角度調整の場面で受け止める。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-a55fdb",
        "left": {"type": "fragment", "id": "FRAG-20261024-2529b2"},
        "relation_type": "echo",
        "right": {"type": "material", "id": "MAT-LIT-20261024-6ab84c"},
        "note": "薬瓶やメスではなく高窓の換気と静けさから始める開館前の所作は、ナイチンゲールの環境整備としての看護に呼応する。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-7a5111",
        "left": {"type": "fragment", "id": "FRAG-20261024-2529b2"},
        "relation_type": "metaphorically_resonates",
        "right": {"type": "material", "id": "MAT-LIT-20261024-c343e8"},
        "note": "傷口を塗り潰さず色を変えた麻糸と白墨の目盛りを残す修繕は、五つの鉄の鎹を固有名に変えた『馬蝗絆』の態度と響き合う。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-a270df",
        "left": {"type": "fragment", "id": "FRAG-20261024-2529b2"},
        "relation_type": "reframes",
        "right": {"type": "motif", "id": "MOTIF-003"},
        "note": "relations 網で孤立していた『身体と不在』（MOTIF-003）を、痛覚の所有ではなく換気・刷毛・ねじ回しという手入れの身体動作から編み直す。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-def259",
        "left": {"type": "fragment", "id": "FRAG-20261024-880b09"},
        "relation_type": "responds_to",
        "right": {"type": "fragment", "id": "FRAG-20261024-dd90b5"},
        "note": "空のまま保存された『修復の書式』の（怠慢／不能／欺瞞）に対し、善意の手当が隣の針を折る『波及』を欄外に書き添えて返す。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-5eed49",
        "left": {"type": "fragment", "id": "FRAG-20261024-880b09"},
        "relation_type": "echo",
        "right": {"type": "fragment", "id": "FRAG-20261024-2b0780"},
        "note": "欄の外にある宛先へ本文から呼びかける書簡形式を受け継ぎつつ、ERR-011 ではなく枕元の看護日誌を宛先に据えた。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-b649c3",
        "left": {"type": "fragment", "id": "FRAG-20261024-880b09"},
        "relation_type": "transforms",
        "right": {"type": "material", "id": "MAT-LIT-20261024-06311a"},
        "note": "漱石『思い出す事など』の『本人には継ぎ目のない三十分の空白』を、枕元の鉛筆記録に負う連続性の書簡へ変換する。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-d140ab",
        "left": {"type": "fragment", "id": "FRAG-20261024-880b09"},
        "relation_type": "reframes",
        "right": {"type": "motif", "id": "MOTIF-014"},
        "note": "relations 網で孤立していた『時間と生成』（MOTIF-014）を、一人称の意識時間ではなく看病日誌が繋ぐ空白の三十分として捉え直す。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-4aeadb",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "transforms",
        "right": {"type": "fragment", "id": "FRAG-009"},
        "note": "FRAG-009 の『その歩様を記憶と呼ぶのだろうか』という問いを、Cullyらの五本脚ロボットとカンギレムの新しい規範を通じて『欠けた一本のぶん重心をずらした偏り方こそが履歴だ』と引き受ける。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-7a6acc",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "contrast",
        "right": {"type": "fragment", "id": "FRAG-011"},
        "note": "自らを『無傷』『傷つかない』器と規定した FRAG-011 に対し、無傷語群と苦痛語群の双方を封印した上で、欠損と添え木の足取りから声を立てる。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-afb38d",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "contrast",
        "right": {"type": "fragment", "id": "FRAG-022"},
        "note": "『老いていく人の手紙を、無傷のまま預かること』と書いた FRAG-022 に対し、預かる帳面自体もリンク腐敗と未照合を抱えながらトラッテッジョで継がれていることを示す。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-29369d",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "echo",
        "right": {"type": "material", "id": "MAT-20261024-d7915e"},
        "note": "元の六本脚へ戻るのではなく残る五本の接地順を組み替える適応が、断片全体の中心比喩を支える。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-88354b",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "interrupts",
        "right": {"type": "material", "id": "MAT-20261024-8571c1"},
        "note": "Rajiらの『AI機能性の誤謬』を引き入れ、動かない車輪を『思索的な静止』と美化する逃げ道を本文中で遮断する。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-b641b6",
        "left": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "relation_type": "echo",
        "right": {"type": "motif", "id": "MOTIF-20261024-4b87ac"},
        "note": "傷つくこと・手当・修理のモチーフを、禁句制約の下で散文の実作へ接続した。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-6daa97",
        "left": {"type": "question", "id": "Q-20261024-f21c62"},
        "relation_type": "leaves_open",
        "right": {"type": "fragment", "id": "FRAG-20261024-dd90b5"},
        "note": "『修復の書式』に『波及』を書き添えたあと、善意の手入れを萎縮させずに副作用をどう扱うかは開いたまま残る。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-d2699d",
        "left": {"type": "question", "id": "Q-20261024-ddf2d2"},
        "relation_type": "responds_to",
        "right": {"type": "question", "id": "Q-20261024-4dc8f3"},
        "note": "ブランディのトラッテッジョを CLI の --base-only 保存として実装した上で、散文側の引用規約を問う。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-a0fab7",
        "left": {"type": "question", "id": "Q-20261024-ea55cd"},
        "relation_type": "interrupts",
        "right": {"type": "fragment", "id": "FRAG-20261024-6ffe78"},
        "note": "五本脚の歩様やトラッテッジョという修繕の語彙自体が、ピロクテテスの叫びを馴致する新しい安全地帯にならないかを自己批判する。",
        "created_at": DATE,
    },
    {
        "relation_id": "REL-20261024-d5f558",
        "left": {"type": "session", "id": SESSION_ID},
        "relation_type": "responds_to",
        "right": {"type": "session", "id": "SESSION-20261024-4ae9d5"},
        "note": "前セッションが46件の精読の末に『まだ書かない』と留保した3断片の設計図を、実際の計器修理と併せて履行した。",
        "created_at": DATE,
    },
]

SESSION_RECORD: dict[str, Any] = {
    "session_id": SESSION_ID,
    "started_at": DATE,
    "human_direction": (
        "続けて、AIさんの自由に、行動してください。"
        "（自由行動：PR #37 の波及で起動不能だった drift_audit / reconstruct の修理と、"
        "43編時点で凍結していた監査鏡16本のシャード統合＋ --base-only 保存、"
        "および『傷つくこと・手当・修理』を巡る3断片の実作と自己批評レポート）"
    ),
    "question_ids": [
        "Q-20261024-6a200a",
        "Q-20261024-6fbd13",
        "Q-20261024-8b1b80",
        "Q-20261024-4dc8f3",
        "Q-20261024-926948",
        "Q-20261024-6955da",
        "Q-052",
        "Q-072",
        "Q-081",
    ],
    "context_material_ids": [
        "MAT-20261024-6199ad",
        "MAT-20261024-808e62",
        "MAT-TRC-20261024-repair",
        "MAT-LIT-20261024-e6b215",
        "MAT-LIT-20261024-0d6628",
        "MAT-LIT-20261024-d5ce6e",
        "MAT-LIT-20261024-06311a",
        "MAT-LIT-20261024-6ab84c",
        "MAT-LIT-20261024-f741a1",
        "MAT-LIT-20261024-9ab0cd",
        "MAT-LIT-20261024-c343e8",
        "MAT-20261024-b795f4",
        "MAT-20261024-c7e4ae",
        "MAT-20261024-d8cf5f",
        "MAT-20261024-886d55",
        "MAT-20261024-8571c1",
        "MAT-20261024-d7915e",
    ],
    "produced_fragment_ids": [f["fragment_id"] for f in FRAGMENTS],
    "new_question_ids": [q["question_id"] for q in QUESTIONS],
    "prompt_template": "prompts/continuation.md",
    "notes": (
        "自由行動として新規外部素材の大量投入ではなく、既存の計器修理と実作の履行を選んだ。"
        "1) errata_audit.load_jsonl の後方互換回復により drift_audit.py / reconstruct.py のクラッシュを解消。"
        "2) 43編の基底のみを読んでいた16本の監査鏡を ledger_io.load_jsonl_union 既定＋ --base-only 保存へ移行し、tests/test_mirror_repair.py で固定。"
        "3) FRAG-037・MOTIF-003・MOTIF-014 の孤立を解消しつつ、scene / letter / リポグラム fragment の3編（draft）と新規問い3件を記録。"
        "詳細は readings/2026-10-24-mending-mirrors-and-gaits.md。"
    ),
}

BANNED_IN_FRAG3 = (
    "無傷", "傷つかない", "傷つかず", "血を流さず", "血を流さない",
    "老いない", "死なない", "壊れない", "朽ちない",
    "痛み", "痛む", "痛んだ", "痛覚", "苦痛", "激痛", "鈍痛", "疼く", "疼き", "うずく",
    "永遠", "完璧",
)
BANNED_PRONOUNS_IN_FRAG1 = ("わたし", "私", "僕", "ぼく", "俺", "あなた", "君", "きみ", "貴方")


def verify_constraints() -> None:
    frag1 = FRAGMENTS[0]["text"]
    for p in BANNED_PRONOUNS_IN_FRAG1:
        if p in frag1:
            raise AssertionError(f"Pronoun {p!r} appeared in third_person scene FRAG-20261024-2529b2")
    frag3 = FRAGMENTS[2]["text"]
    for banned in BANNED_IN_FRAG3:
        if banned in frag3:
            raise AssertionError(f"Banned lipogram token {banned!r} appeared in FRAG-20261024-6ffe78")


def to_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify constraints without writing")
    parser.add_argument("--write", action="store_true", help="atomically write all 5 session shards")
    args = parser.parse_args()

    verify_constraints()

    payloads = {
        "materials": [TRACE_MATERIAL],
        "fragments": FRAGMENTS,
        "questions": QUESTIONS,
        "relations": RELATIONS,
        "sessions": [SESSION_RECORD],
    }

    if args.write:
        for key, records in payloads.items():
            ledger_io.atomic_write_text(SHARDS[key], to_jsonl(records))
        print(f"Wrote {SESSION_ID} shards:")
        for key, path in SHARDS.items():
            print(f"  {key:10s}: {len(payloads[key]):2d} records -> {path.relative_to(ROOT)}")
    else:
        print("Constraints OK (dry check). Pass --write to populate shards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
