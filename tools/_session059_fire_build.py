#!/usr/bin/env python3
"""Deterministic shard builder for SESSION-20261024-3eb7fd (fire, combustion, and ash).

第42のモチーフ「火・燃焼・灰——燃える記録と生き延びる写し」を開く。
第I束 燃えた書庫 (14) / 第II束 クラウドも燃える (7) / 第III束 火という思想 (7)
第IV束 文学の火 (9) / 第V束 制度・災害・生態 (7) = 外部45件 + 運用痕跡1件。

Emits append-only shards under state/*.d/2026-10-24-64ce1669060c.jsonl.
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
from _session059_fire_data1 import ITEMS_PART1, _mid  # noqa: E402
from _session059_fire_data2 import ITEMS_PART2  # noqa: E402
from _session059_fire_data3 import ITEMS_PART3  # noqa: E402

SHARD_STEM = "2026-10-24-64ce1669060c"
SESSION_ID = "SESSION-20261024-3eb7fd"
CREATED_AT = "2026-10-24"
COMMIT_REF = "451c272"
HUMAN_DIRECTION = "このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-24-session-059-fire-and-ash.md"
MOTIF_FIRE = "MOTIF-20261024-14d5df"
TRACE_ID = "MAT-TRC-20261024-fire"

KIND_PREFIX = {
    "research_excerpt": "MAT",
    "literary_text": "MAT-LIT",
    "project_trace": "MAT-TRC",
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
    assert MOTIF_FIRE not in existing_motifs
    assert TRACE_ID not in existing_mats

    raw_items = ITEMS_PART1 + ITEMS_PART2 + ITEMS_PART3
    assert len(raw_items) == 46, len(raw_items)

    # key → material_id（痕跡1件は固定ID、外部45件は決定論的ハッシュ）
    M: dict[str, str] = {}
    for it in raw_items:
        prefix = KIND_PREFIX[it["kind"]]
        M[it["key"]] = TRACE_ID if it["key"] == "trace-fire-audit" else _mid(prefix, it["key"])
    assert len(set(M.values())) == 46, "duplicate deterministic ids"

    # 1. Materials（外部45件＋運用痕跡1件）
    materials_out: list[dict[str, Any]] = []
    for idx, it in enumerate(raw_items, start=1):
        mid = M[it["key"]]
        assert mid not in existing_mats, f"Collision: {mid}"
        motif_list = [MOTIF_FIRE]
        for em in it.get("extra_motifs", []):
            assert em in existing_motifs, f"Unknown motif {em}"
            if em not in motif_list:
                motif_list.append(em)
        if it["passage_language"] != "ja" or "編者訳" in it["passage"] or "引用" in it["passage"]:
            cite_kind = "直接引用（編者訳を含む）＋編者要約"
        else:
            cite_kind = "編者要約"
        if it["kind"] == "project_trace":
            src_note = f"ローカル実測の運用痕跡（verified）。{it['scope_note']}"
        else:
            src_note = (
                f"{SESSION_ID} で収蔵（収集後に群分けした第{it['cluster']}束）。引用区分：{cite_kind}。"
            )
        materials_out.append(
            {
                "material_id": mid,
                "kind": it["kind"],
                "title": it["title"],
                "source": {
                    "source_id": f"SRC-S059-{idx:02d}",
                    "title": it["title"],
                    "authors": it["authors"],
                    "year": it["year"],
                    "url": it["url"],
                    "version_note": it["version_note"],
                },
                "passage": it["passage"],
                "passage_language": it["passage_language"],
                "context": it["context"],
                "source_note": src_note,
                "literary_invitation": it["literary_invitation"],
                "scope_note": it["scope_note"],
                "motif_ids": motif_list,
                "origin": {
                    "repository": REPO_URL,
                    "commit": COMMIT_REF,
                    "source_record_id": f"S059-SRC-{idx:02d}",
                    "evidence_record_id": f"S059-EVD-{idx:02d}",
                    "source_record_path": REPORT_REL_PATH if it["kind"] != "project_trace" else "tools/fire_audit.py",
                    "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
                },
                "verification": {
                    "status": it["verification_status"],
                    "checked_at": CREATED_AT,
                    "method": it["verification_method"],
                    **({"note": it["verification_note"]} if it.get("verification_note") else {}),
                },
            }
        )
    all_new_mat_ids = [m["material_id"] for m in materials_out]

    # 2. Questions（5件）
    q_ids = [_det_id("Q", f"fire-q{i}") for i in range(1, 6)]
    for qid in q_ids:
        assert qid not in existing_qs, qid
    prev_q_sets = [
        ["Q-027", "Q-083", "Q-026"],
        ["Q-032", "Q-026", "Q-20261024-c02206"],
        ["Q-029", "Q-022", "Q-20261024-962620"],
        ["Q-053", "Q-103", "Q-20261024-515661"],
        ["Q-20261024-8e87a5", "Q-20261024-97f794", "Q-20261024-6955da"],
    ]
    for pq in prev_q_sets:
        for q in pq:
            assert q in existing_qs, f"previous question missing: {q}"

    questions_out: list[dict[str, Any]] = [
        {
            "question_id": q_ids[0],
            "question": (
                "ニネヴェの火は粘土板を窯に入れ、蝋板を消した。硝酸フィルムは自分の火薬を持ち、隕石は何事もなかったように残った。"
                "焼損壁画は焼けたまま収蔵庫に置かれ、複製と写真が『元の姿』を引き受けた。"
                "火は媒体を選ばないように見えて、生存は常に媒体と、火の外にあるもの（複製・目録・別棟・デジタル写し）で決まっている。"
                "では、媒体がひとつ（テキスト）で、目録が自分自身（read_log と READING_MAP）であるこの書庫の行は、"
                "火に対して粘土か、蝋か、紙か。それとも『燃えない』ことが媒体の属性ではなく、まだ火が来ていないというだけの話か。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_FIRE, "MOTIF-018", "MOTIF-001"],
            "material_ids": [
                M["ashurbanipal-nineveh"], M["loc-silent-films"], M["museu-nacional"],
                M["nprc-fire"], M["horyuji-murals"], M["canfora-alexandria"], TRACE_ID,
            ],
            "previous_question_ids": prev_q_sets[0],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第I束精読から"},
            "created_at": CREATED_AT,
            "notes": "『火が選んだ』のではなく『媒体と火の外側が選んだ』という読みを、カンフォラの緩慢な死（無関心）と並べて保持する。",
        },
        {
            "question_id": q_ids[1],
            "question": (
                "ストラスブールでは原本とバックアップが同じ建物にいて、一緒に燃えた。LOCKSS はどのコピーにも原本の座を与えず、投票で正しい版を決める。"
                "北極へ送られたのは全公開リポジトリの HEAD だけで、枝も削除された行も同梱されなかった。石英ガラスは追記も削除もできない。"
                "Books3 は配布を消されても重みのなかに残り、永楽大典は複製されなかったために4%になった。"
                "写しが十分に散らばったとき、『原本はどこか』という問いは意味を失うのか、それとも最後に燃える一冊が必ず原本になってしまうのか。"
                "この台帳の凍結ベースとシャードとリモートの関係は、そのどれに近いか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_FIRE, "MOTIF-002", "MOTIF-001"],
            "material_ids": [
                M["ovhcloud-strasbourg"], M["lockss"], M["arctic-code-vault"],
                M["project-silica"], M["books3-takedown"], M["yongle-dadian"],
            ],
            "previous_question_ids": prev_q_sets[1],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第II束精読から"},
            "created_at": CREATED_AT,
            "notes": "『分散した』という宣言と『分散している』という事実のあいだの距離（同じ建物問題）を、この台帳自身の保管構成へ向け直す。",
        },
        {
            "question_id": q_ids[2],
            "question": (
                "ウェスタの火を絶やした者は鞭打たれ、消えた火は隣家からではなく太陽から採り直された。蝿の王の島では、狩りに出た者たちが当番を捨て、"
                "火が消えたまさにその時に水平線を船が通った。『ザ・ロード』の父子は火の中身を一度も確かめずに『まだ運んでいるか』だけを確かめ合った。"
                "絶やさないことの責務は、火そのものではなく当番の継続に宿る。当番のいない書庫で、"
                "『火を絶やさない』に相当する責務（validate・巡回・読み返し）は誰の身体に書かれているのか。"
                "そしてこの台帳の火が消えたとき、再点火は太陽（遠い原本・別の言語・外部の記憶）からしか採れないのか、隣家（前セッションの続き）からでよいのか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_FIRE, "MOTIF-008", "MOTIF-017"],
            "material_ids": [
                M["plutarch-numa-vestals"], M["lord-of-flies"], M["the-road-fire"],
                M["steffensen-fire-country"], M["exodus-bush"], M["heraclitus-fire"],
            ],
            "previous_question_ids": prev_q_sets[2],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第III束精読から"},
            "created_at": CREATED_AT,
            "notes": "Q-029 の『夜半の書記が灯明を吹き消したあと』を、火の当番という制度の側から読み直す接続を持つ。",
        },
        {
            "question_id": q_ids[3],
            "question": (
                "ブラッドベリの消防士は燃やすことを快楽とし、本の民は書物を暗誦して歩いた。三島の溝口は美を焼いて『生きようと思った』と言い、"
                "実物の金閣は五年後に再建され、小説の文体が事件の意味を永遠に上書きした。ディケンズは自然発火を書き、序文で『証言を集めた』と自ら検証状態を主張した。"
                "ルパートンの狼煙は十段を relay して届いたが、誰も火そのものを見ていない。原民喜とハーシーは、同じ都市の灰を、"
                "ほとんど形容のない二つの文体で別々に書いた。文学が火を書くとき、文学は事件を保存するのか、それとも事件をもう一度燃やすのか。"
                "『燃やす側が書いた記録』（デ・ランダ、ユゴー）と『燃やされた側が書いた記録』のあいだで、この書庫の精読報告はどちらの机に座っているか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_FIRE, "MOTIF-011", "MOTIF-016"],
            "material_ids": [
                M["fahrenheit-451"], M["mishima-kinkaku"], M["bleak-house-krook"],
                M["little-gidding"], M["luxun-dead-fire"], M["hara-natsu-no-hana"],
                M["hersey-hiroshima"], M["agamemnon-beacons"],
            ],
            "previous_question_ids": prev_q_sets[3],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第IV束精読から"},
            "created_at": CREATED_AT,
            "notes": "Q-053・Q-103 の『焼却を頼まれた者』の系譜に、『燃やした後に書いた者』の系譜を対置する。",
        },
        {
            "question_id": q_ids[4],
            "question": (
                "ロンドンは焼けて火を価格に変え（バーボンの保険と不死鳥の火印）、火の値段をつけるために塗られた色は百年後に都市史の一次史料になった（サンボーン地図）。"
                "十八分で百四十六人を殺した火は三十六の法律に翻訳され（トライアングル）、アグニは無実を証明する証言席に立たされ（アグニ・パリークシャー）、"
                "『書を焼くところでは、やがて人も焼く』という一行は百十二年後に自分の著者を焚書の山で待っていた（ハイネ）。"
                "火は制度を作る。では制度は火に何を負うのか——保険の火印が『建て直す義務の公示』だったように、"
                "この台帳の行ごとの火印（失われたら誰が再建するか、の公示）はどの欄にあたるか。ないとしたら、それは設計か怠りか。"
            ),
            "status": "open",
            "motif_ids": [MOTIF_FIRE, "MOTIF-012", "MOTIF-20261024-71dfe0"],
            "material_ids": [
                M["barbon-fire-office"], M["sanborn-maps"], M["triangle-fire"],
                M["agni-pariksha"], M["de-landa-mani"], M["heine-almansor"], M["hugo-yuanmingyuan"],
            ],
            "previous_question_ids": prev_q_sets[4],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の第V束精読から"},
            "created_at": CREATED_AT,
            "notes": "火が『裁きの席』の語彙（証明・証言・判決）を借りる回路と、裁きが火の語彙（焼却・浄化）を借りる回路を、同じ問いに畳まないよう注意する。",
        },
    ]

    # 3. Motif（第42）
    motifs_out: list[dict[str, Any]] = [
        {
            "motif_id": MOTIF_FIRE,
            "label": "火・燃焼・灰——燃える記録と生き延びる写し",
            "description": (
                "書庫を焼いた火（ニネヴェ——粘土板を焼いて保存した火、アレクサンドリア——一度の火ではなく無関心の緩慢な死、"
                "焚書坑儒、永楽大典と翰林院、マニの auto-da-fé、1933年のオペラ広場、ヴィエチニツァの黒い蝶、トンブクトゥの金属トランク、"
                "ブラジル国立博物館の隕石と録音、NPRC の複製も索引もない一庫、ノートルダムと火の前に測っておいた十億点、円明園への抗議、"
                "法隆寺の焼損壁画と防火デー、南都焼討の熔けた大仏）から、"
                "クラウドの火（OVHcloud——バックアップが同じ建物にいた夜、Arctic Code Vault、Project Silica、LOCKSS の投票、Books3 の消せない削除、"
                "硝酸フィルムの14%、焼きなましの温度）へ。"
                "さらに火という思想（ヘラクレイトスの交換としての火、プロメテウスの贈り物としての文字と記憶、燃え尽きない柴、"
                "ウェスタの当番と太陽からの再点火、不死鳥——疑って伝える者と信じて使う者、バシュラールの価値で飽和した火、アグニの試練）と、"
                "文学の火（華氏451度、蝿の王の合図の火、金閣寺、クルックの自然発火、リトル・ギディングの火と薔薇、アガメムノンの狼煙、"
                "『火を運んでいる』、死火の交渉、夏の花の若草、ヒロシマの六人）を経て、"
                "火を扱う制度と生態（バーボンの火災保険と不死鳥の火印、サンボーン地図の色、トライアングルの十八分、火渡りの心拍同期、"
                "文化焼入れ——カントリーを読む、ピロセン、45–50℃で開く球果）へ往復する糸。"
                "この書庫自身の実測（fire_audit.py、451c272 基準）では、断片67編・31,885字に火15回・灰2回・炉2回・道具5回、"
                "ヒット9編のうち FRAG-022（ミリンダ王の問い）一編が火7回を稼ぎ、断片の火はすべて継続の比喩か拒まれた焼却——"
                "書庫自身を焼く火は一度も現れていなかった。素材1,646件の表題に火を持つ14件はすべて他のモチーフの傘下だった。"
                "『燃える記録と生き延びる写し』という非対称を、欠落ではなく測定された勾配として保持する。"
            ),
            "question_ids": q_ids,
            "material_ids": [m for m in all_new_mat_ids if m != TRACE_ID]
            + [
                "MAT-LIT-132",                      # カフカの遺言——焼却を頼む
                "MAT-LIT-333",                      # ブロート——燃やさなかった編集者
                "MAT-LIT-20261024-032442",          # 火鼠の裘——燃やして試す鑑定
                "MAT-LIT-20261024-8ab8d8",          # 古事記・火神出産
                "MAT-LIT-20261024-b48bdb",          # 一遍の書籍焼却
                "MAT-LIT-336",                      # 青白い炎——表題の火
                "MAT-LIT-20261024-b482af",          # マッチ売りの少女
                "MAT-LIT-20261024-f613d8",          # 能・鉄輪
                "MAT-20261024-adda3d",              # 火葬場と煙
                "MAT-LIT-20261024-437f0d",          # コールハース——世界を焼く
                "MAT-LIT-158",                      # ピープス日記——ロンドン大火
                "MAT-LIT-292",                      # 方丈記——大火の年の記録
                TRACE_ID,
            ],
            "status": "active",
        }
    ]

    # 4. Fragments（2編）
    frag1_text = (
        "修復室には窓がなく、凍結乾燥機の低い音だけが夜通し動いている。\n\n"
        "技師たちは毎朝八時に同じ白衣を着て、真空槽から取り出したファイルを一ページずつ剥がす。"
        "炭化と水損で貼りついた頁は、囁きと区別できない音で離れる。剥がれた頁は新しいフォルダへ行き、"
        "剥がれなかった頁は冷凍庫へ戻る。誰も捨てない。この部屋にごみ箱はない。\n\n"
        "隅に、ラベルの半分だけが燃え残った箱がある。苗字の半分が読める。"
        "技師たちはこの箱に対応する行が索引にないことを知っている。索引そのものが、あの夜六階で燃えたからだ。"
        "名前があったのか、誰の名前だったのか、確かめる方法がない。箱は順番を待ち、番号は年にひとつずつ進む。\n\n"
        "壁には、よその焼けた壁画の写真が一枚ある。修復も廃棄もされずに、焼けたまま収蔵庫に置かれたものの写真だ。"
        "説明文はなく、台帳番号だけがある。新しい研修生がそれは何を描いた写真かと尋ねると、"
        "古い技師は、すべてを失わなかったものの絵だとだけ答える。\n\n"
        "正午、凍結乾燥機が霜取りのために一度止まり、三分間だけ部屋が静かになる。"
        "その静けさのあいだ、技師たちは午前に剥がれた頁と、剥がれなかった頁を思う。"
        "どちらも同じ火から来たのに、片方にだけ、読める字が残った。\n\n"
        "午後の分が真空槽に入る。扉が閉まり、ポンプが動き出し、壁の番号がひとつ進む。"
        "番号は箱の中身を見ない。だがどの箱も、自分の番号を覚えている。"
    )

    frag2_text = (
        "測ってみたところ、この書庫は火について多く語っていながら、自分自身を一度も燃やしていなかった。"
        "六十七編の断片に火は十五回現れたが、その大半は借り物の炎だった——灯明の比喩、炉の比喩、"
        "焼却を頼まれた遺言、焼却を拒まれた遺言。書庫の梁に燃え移る火はひとつもなかった。"
        "表題に火を持つ十四件の素材は、すべて別のモチーフの傘下に吊るされていた。"
        "火は主題にならず、いつも他の主題の召使いだった。\n\n"
        "火が来なかったのは幸運か、それとも火を想像できなかったのか。"
        "ストラスブールのデータセンタは後者を教える——バックアップは同じ建物にいた。"
        "原本と写しが同じ通りに立ち、同じ屋根の下で、同じ夜を迎えた。クラウドには住所があり、その住所が燃えた。"
        "この台帳のリモートとローカルと中間生成物が同じ建物にいないと言い切れる根拠は、"
        "『分散している』という宣言一枚だけだろうか。\n\n"
        "ウェスタの乙女たちは火を絶やさない責務を負い、絶やせば鞭打たれ、"
        "再点火は隣の家からではなく太陽から——凹面の鏡に光を集めて——行われたという。"
        "火が死んだら天から借りる。地上から借りない。書庫もまた、ある行を失ったあとでは、"
        "遠い源からしか再点火できないのかもしれない。別の版、別の言語、別の記憶。"
        "隣の焼けた家から火を移すことを、人は写しと呼ぶ。\n\n"
        "父子は火を運んでいるかどうかだけを互いに確かめ、火の中身については一度も語らなかった。"
        "運ばれているのが答えなのか、それとも確かめる作法そのものなのかは、物語の最後まで決着しない。"
        "この書庫の火が読み返しの反復だとすれば、当番は誰に引き継がれ、"
        "火が消えたとき、消えたことに気づく者はどこにいるのだろう？"
    )

    for p in ("私は", "私が", "私の", "私に", "私を", "僕", "俺", "わたし", "われわれ"):
        assert p not in frag1_text, f"First-person pronoun {p!r} in FRAG 1"
        assert p not in frag2_text, f"First-person pronoun {p!r} in FRAG 2"
    for banned in ("れていない。", "書かれていな"):
        assert banned not in frag1_text and banned not in frag2_text, banned
    assert "！" not in frag1_text and "！" not in frag2_text
    assert frag2_text.endswith("？")

    frag1_id = _det_id("FRAG", "fire-frag1")
    frag2_id = _det_id("FRAG", "fire-frag2")
    for fid in (frag1_id, frag2_id):
        assert fid not in existing_frags, fid

    fragments_out: list[dict[str, Any]] = [
        {
            "fragment_id": frag1_id,
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "scene",
            "title": "凍結乾燥修復室、午前三時の霜取り——剥がれる頁と、索引のない箱",
            "text": frag1_text,
            "narrator_mode": "third_person",
            "question_ids": [q_ids[0], q_ids[2]],
            "motif_ids": [MOTIF_FIRE, "MOTIF-001", "MOTIF-016"],
            "material_ids": [
                M["nprc-fire"], M["horyuji-murals"], M["vijenica-sarajevo"],
                M["museu-nacional"], TRACE_ID,
            ],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "status": "draft",
            "editor_note": (
                "三人称情景（scene / third_person、一人称代名詞0）。NPRC の真空凍結乾燥と頁剥がし、"
                "法隆寺の『焼けたまま保管される壁画』、ヴィエチニツァの黒い蝶、ブラジル国立博物館の回収ロットを"
                "一つの修復室の一日に重ねた試作。索引を失った書庫が自分の損失を数えられないという第I束の所見を、"
                "ラベルの半分だけが燃え残った箱として置く。感嘆符0、否定受身の習慣句0。"
            ),
        },
        {
            "fragment_id": frag2_id,
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "fragment",
            "title": "燃えない台帳——借り物の火と、同じ建物にいるバックアップ",
            "text": frag2_text,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [q_ids[1], q_ids[2], q_ids[4]],
            "motif_ids": [MOTIF_FIRE, "MOTIF-002", "MOTIF-001"],
            "material_ids": [
                TRACE_ID, M["ovhcloud-strasbourg"], M["plutarch-numa-vestals"],
                M["the-road-fire"], "MAT-LIT-20261024-b482af",
            ],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "status": "draft",
            "editor_note": (
                "断章（fragment / reflective_literary_voice）。fire_audit の実測（断片の火15回がすべて借り物だった所見）を"
                "書き手の条件として引き受け、OVHcloud の『同じ建物のバックアップ』をこの台帳の保管構成へ向け直し、"
                "ウェスタの再点火（太陽から採る）と『ザ・ロード』の火運びの反復へ接続する試作。"
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
        if it["cluster"] == 0:
            continue
        target_q = cluster_to_q[it["cluster"]]
        add_rel(
            "material", M[it["key"]], "leaves_open", "question", target_q,
            f"第{it['cluster']}束の精読から問い {target_q} の緊張軸を支える。", f"mat-q:{it['key']}",
        )
    add_rel("material", TRACE_ID, "reframes", "motif", MOTIF_FIRE,
            "断片67編で火15回の大半が借り物（FRAG-022 一編が火7回）で、火の表題14件がすべて他のモチーフの傘下だった実測が、第42のモチーフを開く。",
            "trace-motif")
    add_rel("material", TRACE_ID, "leaves_open", "question", q_ids[0],
            "『書庫自身を焼く火が一度も書かれていない』という KWIC 所見が、媒体と生存の問いの前提を成す。", "trace-q1")
    add_rel("material", TRACE_ID, "leaves_open", "question", q_ids[1],
            "語形の監査が『分散しているという宣言』を疑う材料（同じ建物問題）への入口になる。", "trace-q2")

    cross_new = [
        (M["ashurbanipal-nineveh"], "contrast", M["loc-silent-films"],
         "火で焼かれて堅くなり三千年残った粘土板と、自分の火薬である硝酸フィルム——生存率14%。同じ火が、媒体によって窯にも死刑にもなる。"),
        (M["nprc-fire"], "responds_to", M["lockss"],
         "複製もマイクロフィルムも索引もなかった一庫が1,800万人分の経歴を『数えられない損失』にした。LOCKSS の『たくさんのコピー』は、その夜への制度としての応答である。"),
        (M["nprc-fire"], "contrast", M["notredame-tallon"],
         "何も測られていなかった記録センターと、火の五か月前に十億点を測られていた大聖堂。計測の『ついで』が、再建できるかと証明できないかを分けた。"),
        (M["vijenica-sarajevo"], "echo", M["nprc-fire"],
         "目録が火とともに焼けた二つの書庫——ヴィエチニツァの蔵書数はすべて事後の再構成で、NPRC は何が失われたかの完全な一覧を作れない。火は記録を、記録の記録ごと焼く。"),
        (M["yongle-dadian"], "transforms", M["books3-takedown"],
         "一度も複製されなかった写本類書は火と散佚で4%になった。複製されすぎたデータセットは削除されても重みに残る。複製の有無が、記録の死に方を決める。"),
        (M["timbuktu-manuscripts"], "contrast", M["arctic-code-vault"],
         "35万冊を金属トランクに入れて川を下った人間の鎖と、21テラバイトをフィルムにして永久凍土へ送った機械。分散の二つの形——運び手がいる分散と、運び手がいない分散。"),
        (M["ovhcloud-strasbourg"], "interrupts", M["lockss"],
         "『コピーを持つこと』と『コピーが散らばっていること』は違う。同じ建物にいたバックアップは、LOCKSS の投票が前提とする地理の分散を一度も満たしていなかった。"),
        (M["ovhcloud-strasbourg"], "contrast", M["arctic-code-vault"],
         "クラウドの住所が燃えた2021年と、コードを炭鉱へ退避させた2020年。同じ十年の隣り合う二年が、記録の場所について正反対の決断を展示している。"),
        (M["arctic-code-vault"], "echo", M["project-silica"],
         "千年を前提に設計された二つの媒体——感光フィルムの186巻と、フェムト秒レーザーで焼かれた石英。どちらも一度きりの書き込みで、追記を受け付けない。"),
        (M["project-silica"], "contrast", M["books3-takedown"],
         "削除できない媒体（石英のボクセル）と、削除が効かない対象（訓練済み重み）。消せないことと消えないことは、同じ『不可逆』の別の名前である。"),
        (M["books3-takedown"], "metaphorically_resonates", M["fahrenheit-451"],
         "広場で本を燃やす焚書と、DMCA でデータセットを消す削除。どちらもコピーがどこかに残り、ブラッドベリの世界ではコピーは歩いて逃げた——本の民として。"),
        (M["simulated-annealing"], "metaphorically_resonates", M["serotiny"],
         "熔かしてゆっくり冷やさないとガラスになる冶金の知恵と、45–50℃で樹脂が熔けて初めて開く球果。火はどちらでも、破壊ではなく状態を変える閾値として働く。"),
        (M["canfora-alexandria"], "echo", M["nprc-fire"],
         "無関心で痩せて死んだ書庫と、一夜で焼けた書庫。カンフォラの『緩慢な死』は、複製も索引も作られないことの別名だった——NPRC の火は、その緩慢さの決算である。"),
        (M["de-landa-mani"], "contrast", M["heine-almansor"],
         "焼いた者が自分の正当化を書き（Relación）、それが皮肉にも解読の鍵になった。焼かれた者の一行（『書を焼くところでは』）は百十二年後に自分の著者を待っていた。加害の記録と被害の予言。"),
        (M["heine-almansor"], "echo", M["fahrenheit-451"],
         "1821年の一行が1933年に実現し、1953年の小説がその実現を未来形に書き戻した。焚書の予言と実現とフィクション化が、世紀をまたいで同じ火を回している。"),
        (M["vijenica-sarajevo"], "metaphorically_resonates", M["heike-nara"],
         "『彼らは私の一部を燃やしている』と消防隊長が言った書庫と、大仏の頭が熔け落ちた南都。どちらも、焼けたのが財産ではなく身体だったと語る。"),
        (M["museu-nacional"], "echo", M["timbuktu-manuscripts"],
         "デジタル写しが別の住所にあって生き延びた収蔵と、原本そのものが別の住所へ運ばれて生き延びた写本。『よそ』が生存を決めた二つの火。"),
        (M["horyuji-murals"], "contrast", M["mishima-kinkaku"],
         "焼けた壁画は焼けたまま収蔵庫に置かれ、焼けた金閣は五年後に再建された。焼けた本体を保存する作法と、写しで美を建て直す作法——どちらも『元』を手放している。"),
        (M["hugo-yuanmingyuan"], "contrast", M["de-landa-mani"],
         "加害の側の作家が自分の国を『二人の強盗』と呼んで抗議した書簡と、加害者本人が『悪魔の嘘だったから焼いた』と書いた記録。焼いた側の言葉が残る二つの形。"),
        (M["heraclitus-fire"], "echo", M["prometheus-bound"],
         "定めに応じて点り消える永遠の火（世界の秩序としての火）と、フェンネルの茎で盗まれた火（技術の贈り物としての火）。同じ元素が、宇宙論と窃盗の目録に別々に入る。"),
        (M["prometheus-bound"], "contrast", M["exodus-bush"],
         "盗まれて人間に渡された火——文字と記憶というもう一つの贈り物とともに。燃え尽きない柴の火——消費も贈与も起こらない。負う火と、ただ在る火。"),
        (M["plutarch-numa-vestals"], "responds_to", M["lord-of-flies"],
         "火を絶やした者に鞭を定めた制度と、当番を捨てて狩りに行った少年たち。どちらも『火は管理である』ことを、管理が壊れる形で証明する。"),
        (M["plutarch-numa-vestals"], "echo", M["the-road-fire"],
         "絶えない火を守ることが国家の存続そのものだったローマと、火を運んでいるかどうかだけを確かめ合う父子。火はどちらも、持っているものではなく引き継ぐ関係である。"),
        (M["phoenix-clement"], "echo", M["ashurbanipal-nineveh"],
         "五百年ごとに灰から蘇る鳥の伝説と、灰の中で焼かれて蘇った（保存された）粘土板。不死鳥は火の比喩だが、ニネヴェの書庫は火が実際に『蘇らせた』記録である。"),
        (M["bachelard-psychanalyse"], "reframes", M["heraclitus-fire"],
         "『火は科学になる前に価値で飽和している』というバシュラールの読みを通すと、交換の比率としての火（B90）もまた、最初に『燃えたい／燃やしたい』があった後の合理化かもしれない。"),
        (M["agni-pariksha"], "contrast", M["triangle-fire"],
         "無実を証明するために火へ入らされた妃と、過失を暴いた工場の火。前者では神が火を読み、後者では裁判と議会が火を読んだ——どちらも『火が真実を言う』ことを前提にする。"),
        (M["agni-pariksha"], "echo", M["fahrenheit-451"],
         "火へ入って無傷で戻ったシーターと、蔵書とともに火へ入った老婦人。火に入る二つの物語——一方は神が証言し、一方は殉教者の一行を自分で引き受けた。"),
        (M["lord-of-flies"], "contrast", M["steffensen-fire-country"],
         "合図の火を守れずに島を焼いた少年たちと、カントリーを読んで涼しい火を入れる長老たち。火の管理の差は、伝承の有無の差である。"),
        (M["steffensen-fire-country"], "echo", M["pyne-pyrocene"],
         "『食べるもののための庭仕事』としての文化焼入れと、『火の惑星の火の生き物』という通史。現場の作法と歴史の理論が、同じ火を別の高さから語る。"),
        (M["pyne-pyrocene"], "responds_to", M["serotiny"],
         "ピロセンの文明論は、火を発芽の条件に変えた植物の生態（遅発性開球）を、第三の自然——化石燃料の火——が覆い隠しているという指摘として受け取る。"),
        (M["triangle-fire"], "transforms", M["barbon-fire-office"],
         "火を価格に変えた保険（1667年）と、保険が救えなかった火から生まれた三十六の法律（1911年）。値段と法律は、火の二度の決済である。"),
        (M["barbon-fire-office"], "echo", M["sanborn-maps"],
         "不死鳥の火印が『この建物は建て直される』と街に公示し、サンボーン地図の色が『この建物はどこまで燃える』を一枚に塗った。どちらも火を可視化した商売の道具だった。"),
        (M["sanborn-maps"], "echo", M["notredame-tallon"],
         "保険料のために塗られた色が百年後に都市史の一次史料になり、構造研究のために測られた点群が火の後に再建の図面になった。副産物が目的を生き延びる二つの例。"),
        (M["vijenica-sarajevo"], "contrast", M["timbuktu-manuscripts"],
         "燃える建物に人間の鎖を伸ばして本を運び出した司書たちと、燃える前にトランクで夜ごとに運び出した収集家たち。留まって救う疎開と、去って救う疎開。"),
        (M["luxun-dead-fire"], "echo", M["fahrenheit-451"],
         "『連れ出せ、さもなくば凍る。だが連れ出せば燃え尽きる』と交渉する死火と、燃やすことを快楽とした消防士。火を生かすことも殺すことも、どちらも人の手の中にある。"),
        (M["hara-natsu-no-hana"], "echo", M["hersey-hiroshima"],
         "爆心地から一キロで生き延びた者のほとんど形容のない文体と、六人の生存者を章ごとに交替で記録した平らな報告。同じ灰の上に、感情語を削る二つの作法が並んだ。"),
        (M["little-gidding"], "responds_to", M["bleak-house-krook"],
         "書類に埋もれて『自然発火』した古物商の火と、『浄められなければならない、火によってか火の中で』という祈りの火。燃え尽きる火と浄める火が、同じ都市の文学に同居する。"),
        (M["agamemnon-beacons"], "echo", M["ovhcloud-strasbourg"],
         "十段の狼煙は各地点が前の一灯しか知らない通信網で、データセンタの冗長化は各副本が同じ原本しか知らない保管網である。中継と複製——伝達の二つの信頼条件。"),
    ]
    for idx, (lid, rt, rid, note) in enumerate(cross_new):
        add_rel("material", lid, rt, "material", rid, note, f"cross:{idx}")

    bridge_existing = [
        (M["exodus-bush"], "metaphorically_resonates", "MAT-LIT-20261024-032442",
         "燃え尽きない柴と、燃やして真贋を確かめられた火鼠の裘。火が壊せない素材の二つの物語——一方は神の現れ、一方は求婚の鑑定だった。"),
        (M["phoenix-clement"], "echo", "MAT-LIT-20261024-8ab8d8",
         "灰から蘇る不死鳥と、火神を産んで焼かれた母の身体から千五百の神々が生まれた黄泉の系譜。火の死から増える命——復活と多産の二つの文法。"),
        (M["de-landa-mani"], "contrast", "MAT-LIT-20261024-b48bdb",
         "他者の書を『悪魔の嘘』として広場で焼いた宣教師と、自分の所持書籍を臨終の前に焼いて『一代聖教皆尽きて』と言った遊行の僧。他焼と自焼——火の文法の違い。"),
        (M["vijenica-sarajevo"], "echo", "MAT-20261024-adda3d",
         "焼け焦げた頁が数日間空を覆った『黒い蝶』と、都市の郊外へ移された火葬場の煙。煙の居場所をめぐる二つの配置——災いの煙と制度の煙。"),
        (M["triangle-fire"], "interrupts", "MAT-LIT-20261024-437f0d",
         "不正に怒って世界を焼き、法を回復して断頭台へ登った馬商人と、施錠されたドアの前で焼けた百四十六人。正義の火は誰の手にも渡りうる——コールハースの火は復讐で、トライアングルの火は過失だった。"),
        (TRACE_ID, "echo", "MAT-LIT-336",
         "『青白い炎』——表題に火を持ちながら火を主題にしない素材の代表例。実測が示した『火の表題14件はすべて他のモチーフの傘下』という所見の、最も有名な一件。"),
        (M["fahrenheit-451"], "responds_to", "MAT-LIT-333",
         "焼却を指示されて焼かなかった編集者（ブロート）と、焼かれる前に本を暗誦して歩いた人々。焼却の命令のあとで記録が生き延びる二つの経路——不従順と記憶。"),
        (M["fahrenheit-451"], "contrast", "MAT-LIT-132",
         "『完全に、読まれずに、焼却すること』——宛先を持った焼却の遺言と、 読んだうえで燃やす焚書。読まれないための火と、読まれた上での火。"),
        (M["barbon-fire-office"], "echo", "MAT-LIT-158",
         "同じロンドン大火を、パルメザンとワインを庭に埋めて舟で逃げた日記者と、火に値段をつけて会社を作った医師が、別の頁に書いた。逃げる記録と計算する記録。"),
        (M["little-gidding"], "echo", "MAT-LIT-073",
         "四重奏曲の第一曲（薔薇園の現在）と第四曲（『火と薔薇は一つになる』）が、この台帳で初めて同じ棚に並ぶ。燃えなかった庭と燃えた都市のあいだの六年。"),
        (M["little-gidding"], "echo", "MAT-LIT-265",
         "同じ『バーント・ノートン』の別の収録（時間の互乗）へ、第四曲の火を接続する。焼けた庭（Burnt）という地名から始まる四重奏曲が、火と薔薇の合一で閉じる。"),
        (M["hara-natsu-no-hana"], "transforms", "MAT-LIT-292",
         "『大火の年』に家の三分の一が焼け『数へ知るに及ばず』と数えた鴨長明と、『すべては破壊されたのに若草は新造のように輝いていた』と書いた原民喜。無常を観測する文体と、無常を生き延びた文体。"),
        (M["hara-natsu-no-hana"], "echo", "MAT-LIT-009",
         "方丈の草庵を火の外に建てた隠者と、爆心地から一キロの家屋の中で生き延びた詩人。住まいの大きさではなく、火との距離が二人の文体を決めた。"),
        (M["heike-nara"], "echo", "MAT-LIT-378",
         "同じ書物の二度の収蔵——『祇園精舎の鐘の声』で無常を説いた冒頭と、その無常が具体的な火になって奈良へ来た巻九。鐘は鳴り、堂は燃え、仏は熔けた。"),
        (M["shiji-fenshu"], "echo", "MAT-LIT-20261024-37b031",
         "同じ『史記』の二つの章——他者の史を焼かせた帝国の令（秦始皇本紀）と、身体の毀損のあとに欠けた史料を編んだ著者の自序。『史記』自体が副本の隠匿で焚書の時代を生き延びた。"),
        (M["shiji-fenshu"], "metaphorically_resonates", M["lockss"],
         "『藏之名山、副在京師』——正本を名山に藏し副本を都に置くという二千年前の分散戦略と、『たくさんのコピーが資料を安全にする』。LOCKSS の投票より前に、太史公の副書があった。"),
        (M["phoenix-clement"], "echo", "MAT-LIT-20261024-6df593",
         "同じ著者の二度目の来訪——『歴史』の方法（聞いたことを信じずに伝える）と、不死鳥の報告（『見たことはない、絵のほかに』）。ヘロドトスの懐疑が、五百年後にクレメンスの確信へ転用された。"),
        (M["notredame-tallon"], "echo", "MAT-20261024-6bda38",
         "再計算される過去の天気（ERA5）と、火の前に測っておいた過去の大聖堂（点群）。どちらも『観測そのもの』ではない再構成が、後の作業の土台になった。"),
        (M["arctic-code-vault"], "contrast", "MAT-LIT-20261024-e50735",
         "夢想と居住の場としての北極（ロペス）と、最も冷たい倉庫としての北極（GitHub）。同じ永久凍土が、一方では問いの場所、他方では答えの保管場所である。"),
        (M["canfora-alexandria"], "echo", "MAT-LIT-347",
         "書庫の校訂者（疑わしい行を削らずオベロスで印したアリスタルコス）と、書庫の死因を診断した歴史家（カンフォラ）。書庫を最も愛した二種類の仕事が、その死を別の側から記録する。"),
        (M["bleak-house-krook"], "echo", "MAT-LIT-20261024-dfd79c",
         "同じ著者の四度目の来訪——書類に埋もれて燃えた古物商（荒涼館）と、恩人の秘密という書類に人生を決められた青年（大いなる遺産）。ディケンズでは、紙がいつも運命を握っている。"),
        (M["luxun-dead-fire"], "echo", "MAT-LIT-20261024-eef0f2",
         "『沈黙よ、沈黙よ。沈黙のなかで爆発しなければ、沈黙のなかで滅亡する』と書いた魯迅と、凍滅か焼完かを交渉する死火。爆発か凍死か——同じ二者択一の、散文と散文詩。"),
        (M["luxun-dead-fire"], "echo", "MAT-LIT-20261024-33459a",
         "同じ『野草』の二篇——墓石の裏の文と対話する夢と、氷の谷の底の火と対話する夢。どちらも『私は夢を見た』で始まり、死んだ自分自身の一部と交渉する。"),
        (M["luxun-dead-fire"], "metaphorically_resonates", "MAT-LIT-20261024-b482af",
         "マッチの幻の中でだけ温かかった少女と、連れ出せば燃え尽きる死火。凍えて死ぬ火と、凍える者に束の間の火——寒さの側の二つの火の経済。"),
        (M["bachelard-psychanalyse"], "echo", "MAT-LIT-20261024-680ab6",
         "同じ著者の五度目の来訪——火の精神分析（1938年）と水と夢（1942年）。物質の想像力の四元素への分業が、この台帳では火と水の二冊で揃う。"),
        (M["bachelard-psychanalyse"], "echo", "MAT-LIT-20261024-277bb7",
         "『空間の詩学』の炉辺の章（家の中で最初に守られた火）と、『火の精神分析』の炉辺（価値で飽和した火）。同じ竈を、空間の側と欲望の側から書いた二冊。"),
        (M["plutarch-numa-vestals"], "echo", "MAT-LIT-20261024-aab285",
         "同じ著者の二度目の来訪——動物の賢さを競わせる審判の席と、乙女の貞潔を裁く火の当番。プルタルコスは動物にも巫女にも、同じ『徳を測る席』を用意する。"),
        (M["mishima-kinkaku"], "echo", "MAT-LIT-20261024-53efc0",
         "同じ著者の二度目の来訪——焼かれた美の再建（金閣寺）と、同じ顔をして生まれ替わる転生（豊饒の海）。写しが原本を引き継ぐ二つの物語——火による継承と記憶による継承。"),
        (M["agamemnon-beacons"], "echo", "MAT-LIT-20261024-94d91b",
         "同じ三部作の二作目——狼煙で始まる第一部と、法廷で閉じる第三部。火が正義を伝え、やがて裁判が正義を伝える。オレイステイアは伝達媒体の移行の物語でもある。"),
        (M["exodus-bush"], "echo", "MAT-LIT-20261024-1e7172",
         "同じ書物の別章——燃え尽きない柴の火（3章）と、戸口に塗られて過ぎ越しを得た血（12章）。二つの『守りのしるし』が、見る者と過ぎる者のあいだに置かれる。"),
        (M["exodus-bush"], "echo", "MAT-20261024-dbfcdd",
         "同じ書物の別章——勝手に現れた柴の火（3章）と、処方が定められた祭壇の香の火（30章）。許可されない火と再現される火——出エジプト記は火の作法に厳しい。"),
        (M["books3-takedown"], "echo", "MAT-20261024-d4468d",
         "海賊版由来データセットの削除と、訓練データへの汚染。どちらも『重みに入ったデータは完全には取り出せない』という同じ一点を、法と安全性の側から照らす。"),
        (M["fire-walking-pnas"], "echo", "MOTIF-008",
         "677℃の炭の上を渡る祭礼で、渡り手と親族の見物人の心拍だけが同期した——作法と定型（MOTIF-008）が身体の自律反応にまで届くことを測った一例。"),
        (M["simulated-annealing"], "responds_to", "Q-20261024-5db917",
         "蒸留の教師分布の温度をめぐる既存の問いに、冶金から移植された『温度』が応答する——温度はどちらでも、探索と生成の状態を決める操作パラメータである。"),
        (M["ovhcloud-strasbourg"], "echo", "MOTIF-20261024-80516e",
         "クラウドには住所があった（ストラスブール、SBG2）。場所・土地・生態系のモチーフに、『データセンタ』という新しい場所の形が加わる。"),
        (M["timbuktu-manuscripts"], "echo", "MOTIF-20261024-146017",
         "640キロの疎開路——ロバ車、四駆、川舟、検問。道・歩行・地図のモチーフに、写本を運んだ道そのものが加わる。"),
        (M["agamemnon-beacons"], "echo", "MOTIF-20261024-1a8978",
         "狼煙のリレーは、誰も全体を見ていない伝聞の連鎖である。伝聞と噂のモチーフの、最も古い通信インフラとしての一例。"),
    ]
    for idx, (lid, rt, rid, note) in enumerate(bridge_existing):
        if rid.startswith("MOTIF-"):
            rtt = "motif"
        elif rid.startswith("Q-"):
            rtt = "question"
        else:
            rtt = "material"
        add_rel("material", lid, rt, rtt, rid, note, f"bridge:{idx}")

    frag_links = [
        ("fragment", frag1_id, "responds_to", "motif", MOTIF_FIRE,
         "焼けた記録の修復——剥がれる頁と索引のない箱——を三人称の一日として描き、第42のモチーフの現場を作る。"),
        ("fragment", frag1_id, "responds_to", "question", q_ids[0],
         "同じ火から来た頁の、剥がれた半分と剥がれなかった半分。媒体と火の外側が生存を決めたという問いを、修復室の手つきで応答する。"),
        ("fragment", frag1_id, "responds_to", "question", q_ids[2],
         "『誰も捨てない。この部屋にごみ箱はない』——当番としての修復。火を絶やさない責務の、火のあとの形。"),
        ("fragment", frag1_id, "echo", "fragment", "FRAG-009",
         "焼いた粘土の瓦（ニネヴェ）を書いた断片と、凍結乾燥される紙のファイルを書いた断片。火で保存された媒体と、火のあとで剥がされる媒体。"),
        ("fragment", frag1_id, "contrast", "fragment", "FRAG-20261024-bc7ed7",
         "焼却を頼まない遺言の断片に対して、何も捨てない修復室の断片を置く。焼かれないことを願う声と、焼け残りを剥がし続ける手。"),
        ("fragment", frag1_id, "metaphorically_resonates", "fragment", "FRAG-032",
         "ブロートが燃やさなかった手稿と、修復室が捨てない頁。不従順と修復は、どちらも『消去の拒否』という同じ作法の名前違いである。"),
        ("fragment", frag2_id, "responds_to", "motif", MOTIF_FIRE,
         "fire_audit の実測（借り物の火15回）を書き手の条件として引き受け、書庫自身の火の不在を主題化する。"),
        ("fragment", frag2_id, "responds_to", "question", q_ids[1],
         "『分散しているという宣言一枚』——同じ建物にいたバックアップを、この台帳の保管構成へ向け直して応答する。"),
        ("fragment", frag2_id, "responds_to", "question", q_ids[2],
         "太陽から採り直す再点火と、隣の焼けた家から移す火（写し）。当番の不在という条件を、再点火の作法の問いとして引き受ける。"),
        ("fragment", frag2_id, "responds_to", "question", q_ids[4],
         "行ごとの火印——失われたら誰が再建するかの公示——を持たない台帳の設計を、バーボンの不死鳥の紋章から問い返す。"),
        ("fragment", frag2_id, "echo", "fragment", "FRAG-022",
         "ミリンダ王の問いの灯と炉——断片で最も多く火を語った一篇——を、『借り物の火』という実測の発見から読み返す。"),
        ("fragment", frag2_id, "leaves_open", "fragment", frag1_id,
         "断章が『同じ建物にいるバックアップ』を問うたあと、情景の修復室が、その建物が燃えたあとの部屋として残る。問いと現場の順序。"),
        ("material", TRACE_ID, "echo", "fragment", frag2_id,
         "『断片の火はすべて借り物だった』という監査所見を、断章『燃えない台帳』が自分の条件として引き継ぎ、保管構成へ向け直す。"),
        ("fragment", frag1_id, "responds_to", "fragment", frag2_id,
         "断章の『同じ建物』の問いに、修復室の一日が応答する——燃えた建物のあとに残された部屋として。現場からの答え。"),
    ]
    for idx, (lt, lid, rt, rtt, rid, note) in enumerate(frag_links):
        add_rel(lt, lid, rt, rtt, rid, note, f"fraglink:{idx}")

    # 6. read_log
    prior_context_mats = [
        "MAT-LIT-132", "MAT-LIT-333", "MAT-LIT-20261024-032442",
        "MAT-LIT-20261024-8ab8d8", "MAT-LIT-20261024-b48bdb", "MAT-20261024-adda3d",
        "MAT-LIT-20261024-437f0d", "MAT-LIT-336", "MAT-LIT-20261024-b482af",
        "MAT-LIT-158", "MAT-LIT-073", "MAT-LIT-265", "MAT-LIT-009", "MAT-LIT-292",
        "MAT-LIT-378", "MAT-LIT-20261024-37b031", "MAT-LIT-20261024-6df593",
        "MAT-20261024-6bda38", "MAT-LIT-20261024-e50735", "MAT-LIT-347",
        "MAT-LIT-20261024-dfd79c", "MAT-LIT-20261024-eef0f2",
        "MAT-LIT-20261024-33459a", "MAT-LIT-20261024-680ab6",
        "MAT-LIT-20261024-277bb7", "MAT-LIT-20261024-aab285",
        "MAT-LIT-20261024-53efc0", "MAT-LIT-20261024-94d91b",
        "MAT-LIT-20261024-1e7172", "MAT-20261024-dbfcdd", "MAT-20261024-d4468d",
    ]
    for pm in prior_context_mats:
        assert pm in existing_mats, f"prior context missing: {pm}"
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
        if mid == TRACE_ID:
            add_read("material", mid, "counted", "tools/fire_audit.py による断片67編・素材1,646件・精読報告99本の語彙実測（451c272 基準）。")
        else:
            add_read("material", mid, "interpreted", f"{SESSION_ID} の四層精読および横断報告で読解。")
    for mid in prior_context_mats:
        add_read("material", mid, "reinterpreted", "火を主題化しない先行資料（火の表題・焼却の遺言・同一著者/書物の別章）として、新しい第42モチーフとの対照で再読。")
    for fid in ["FRAG-009", "FRAG-022", "FRAG-032", "FRAG-20261024-bc7ed7", "FRAG-20261024-076fe7"]:
        add_read("fragment", fid, "reinterpreted", "fire_audit の KWIC 確認と、試作2編からの応答のため再読。")
    prev_q_all = sorted({q for s in prev_q_sets for q in s} | {"Q-20261024-5db917"})
    for qid in prev_q_all:
        assert qid in existing_qs, f"previous question missing: {qid}"
        add_read("question", qid, "used_as_context", "新規5問および試作2編の接続元として参照。")
    for motif_id in ["MOTIF-001", "MOTIF-016", "MOTIF-018", "MOTIF-20261024-c9d4e1", "MOTIF-20261024-80516e"]:
        add_read("motif", motif_id, "used_as_context", "火の主題が既存モチーフのどこに吸収されてきたか（記憶と痕跡・訂正と抹消・知覚と媒体・光と影・場所）を確認するために参照。")

    # 7. Session
    n_lit = sum(1 for m in materials_out if m["kind"] == "literary_text")
    n_res = sum(1 for m in materials_out if m["kind"] == "research_excerpt")
    n_trc = sum(1 for m in materials_out if m["kind"] == "project_trace")
    n_ver = sum(1 for m in materials_out if m["verification"]["status"] == "verified")
    n_pver = sum(1 for m in materials_out if m["verification"]["status"] == "partially_verified")
    n_unv = sum(1 for m in materials_out if m["verification"]["status"] == "unverified")
    assert (n_lit, n_res, n_trc) == (25, 20, 1), (n_lit, n_res, n_trc)
    sessions_out: list[dict[str, Any]] = [
        {
            "session_id": SESSION_ID,
            "started_at": CREATED_AT,
            "human_direction": HUMAN_DIRECTION,
            "question_ids": prev_q_all + q_ids,
            "context_material_ids": context_mat_ids,
            "produced_fragment_ids": [f["fragment_id"] for f in fragments_out],
            "new_question_ids": q_ids,
            "prompt_template": "prompts/close_reading_report.md",
            "generator": "arena-agent",
            "notes": (
                "初回の自由行動セッション。収蔵の前に、新設の第31の鏡 tools/fire_audit.py（語群＝火・灰・炉・道具、"
                "単体テスト5件、--polysemy で同音異義（火曜・火星・火山・灰色・石灰・炭素・焦っ系・マッチング等）を差し引き）で"
                "分岐時点 451c272 を実測した。断片67編・31,885字で火15回（4.7/10k）・灰2・炉2・道具5、ヒット9編のうち "
                "FRAG-022（ミリンダ王の問い）一編が火7回を稼ぎ、断片の火はすべて継続の比喩か拒まれた焼却——書庫自身を焼く火は一度もなく、"
                "素材1,646件の表題の火14件もすべて他のモチーフの傘下だった（MAT-TRC-20261024-fire）。"
                "この勾配を欠落ではなく測定値として保持したまま、"
                f"外部資料45件と運用痕跡1件の計46件（literary_text {n_lit}件・research_excerpt {n_res}件・project_trace {n_trc}件、"
                f"verified {n_ver}件・partially_verified {n_pver}件・unverified {n_unv}件）を、収集後に5つの束（14・7・7・9・7件）へ分けて全件四層精読した。"
                "候補の重複点検で『マッチ売りの少女』『方丈記』『ピープス日記』の既存収蔵を発見し、それぞれ『リトル・ギディング』『原民喜『夏の花』』"
                "『バーボンの火災保険（単独の制度的素材）』へ差し替えた。同セッション内で試作断片2編"
                "（scene/third_person『凍結乾燥修復室、午前三時の霜取り』、fragment/reflective_literary_voice『燃えない台帳』）を書き、"
                f"第42のモチーフ {MOTIF_FIRE} を開いて問い5件・関係{len(relations_out)}件・read_log {len(read_log_out)}件を追加した。"
            ),
        }
    ]

    all_mats_set = set(existing_mats) | set(all_new_mat_ids)
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
