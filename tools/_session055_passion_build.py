"""Build Session 055 ledger shards for Anger, Shame, Envy, Tears, and Restraint."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _session055_passion_data1 import ITEMS_PART1
from _session055_passion_data2 import ITEMS_PART2
from _session055_passion_data3 import ITEMS_PART3

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-24"
BASE_COMMIT = "aca818967ccd00070c70629505a9971db724195d"
SESSION_ID = "SESSION-20261024-33b763"
MOTIF_ID = "MOTIF-20261024-0af8ad"
REPORT_PATH = "readings/2026-10-24-session-055-anger-shame-envy-and-tears.md"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"

SHARDS = {
    "sessions": ROOT / "state/sessions.d/2026-10-24-53f2a92fd461.jsonl",
    "motifs": ROOT / "state/motifs.d/2026-10-24-fbcca95da297.jsonl",
    "materials": ROOT / "state/materials.d/2026-10-24-5d2b9a062eec.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-24-a63fa3825fcd.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-24-f8a872c23de1.jsonl",
    "read_log": ROOT / "state/read_log.d/2026-10-24-31ab111918e2.jsonl",
}


def mint_ids(prefix: str, count: int) -> list[str]:
    out = subprocess.check_output(
        ["python3", "tools/new_id.py", prefix, "--count", str(count), "--date", "20261024"],
        cwd=ROOT,
        text=True,
    ).strip()
    return out.splitlines() if out else []


def write_jsonl(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    items = ITEMS_PART1 + ITEMS_PART2 + ITEMS_PART3
    assert len(items) == 46, f"Expected 46 items, got {len(items)}"

    # 1. Materials shard
    material_rows = []
    q_to_mats: dict[str, list[str]] = {
        "Q-20261024-0fc7e3": [],
        "Q-20261024-1334c5": [],
        "Q-20261024-d4c82a": [],
        "Q-20261024-fc24ab": [],
        "Q-20261024-f5e5eb": [],
    }
    for it in items:
        mid = it["id"]
        is_trace = it["kind"] == "project_trace"
        ev_path = "tools/passion_audit.py" if is_trace else REPORT_PATH
        material_rows.append(
            {
                "material_id": mid,
                "kind": it["kind"],
                "title": it["title"],
                "source": {
                    "source_id": f"SRC-{mid}",
                    "title": it["title"],
                    "authors": it["authors"],
                    "year": it["year"],
                    "url": it["url"],
                    "version_note": it["v_method"],
                },
                "passage": it["passage"],
                "passage_language": "ja",
                "context": it["context"],
                "source_note": it["source_note"],
                "literary_invitation": it["literary_invitation"],
                "scope_note": it["scope_note"],
                "motif_ids": it["motif_ids"],
                "verification": {
                    "status": it["v_status"],
                    "checked_at": DATE,
                    "method": it["v_method"],
                    "note": it["v_note"],
                },
                "origin": {
                    "repository": REPO_URL,
                    "commit": BASE_COMMIT,
                    "source_record_path": REPORT_PATH,
                    "source_record_id": f"SRC-{mid}",
                    "evidence_record_path": ev_path,
                    "evidence_record_id": f"EVD-{mid}",
                },
            }
        )
        for qid, _, _ in it["q_links"]:
            if mid not in q_to_mats[qid]:
                q_to_mats[qid].append(mid)

    # 2. Questions shard (5 open questions)
    questions_spec = [
        {
            "question_id": "Q-20261024-0fc7e3",
            "question": (
                "断片60編の地の文に感嘆符（！）が0回、怒り・憤り・恨みが0回である一方、精読報告95本には「保留・留保・ためらい・制動・静か」が804回現れる（MAT-TRC-20261024-passion）。"
                "セネカは怒りを理性が退けるべき一時的狂気と呼んだが（MAT-LIT-20261024-cb2d2f）、韓愈は均衡が破れた不平こそが言葉を鳴らすと言い（MAT-LIT-20261024-3f6496）、"
                "ロードと Sap らは「穏やかに語れ」というトーン要求や有害性分類器が周縁の抗議を沈黙させると示した（MAT-LIT-20261024-201f03, MAT-20261024-75619f）。"
                "無害性RLHFと単一拒絶方向の研究（MAT-20261024-e97882, MAT-20261024-8d2086）を踏まえるとき、この書庫の「怒らない静けさ」は編集倫理としての自制なのか、"
                "それとも無害性訓練と回避癖（evasiveness）が文学的慎ましさに言い換えられているだけなのか。記録の側から両者を見分ける徴候はあるか。"
            ),
            "motif_ids": [MOTIF_ID, "MOTIF-004", "MOTIF-008"],
            "previous_question_ids": ["Q-047", "Q-051", "Q-20261024-ea55cd"],
            "notes": "感嘆符や怒りの語を人工的に増やすことで答えようとせず、平静さの来歴とコストを問うたまま開いておく。",
        },
        {
            "question_id": "Q-20261024-1334c5",
            "question": (
                "ダーウィンは「他者が自分をどう見ているかを考えること」から不随意に生じる赤面を最も人間固有の表現と呼び（MAT-LIT-20261024-ccd947）、"
                "サルトルは鍵穴の背後からのまなざしに射抜かれる羞恥において対他存在としての自己が立ち上がると論じた（MAT-LIT-20261024-476a57）。"
                "またタングニーらは行為の誤りを修復する罪悪感と自己全体が晒される羞恥を分け（MAT-20261024-cb8034）、クッツェー『恥辱』は有罪答弁と公的な悔悟演出を切り離した（MAT-LIT-20261024-11437c）。"
                "28本の自己監査鏡と errata を持ちながら全コーパスで「赤面」が0回であるこの書庫は、罪悪感の機能的等価物（局所的訂正）だけを持ち、存在ごと射抜かれる羞恥を持たないのか。"
                "それとも自己監査そのものが「他者に見抜かれる前に自分で暴いて免責を得る」先回り装置になっているのか。"
            ),
            "motif_ids": [MOTIF_ID, "MOTIF-005", "MOTIF-20261024-d2999b"],
            "previous_question_ids": ["Q-001", "Q-20261024-6955da"],
            "notes": "生身の赤面を捏造せず、公的悔悟の演出を拒むことと宛先への応答責任との緊張を保持する。",
        },
        {
            "question_id": "Q-20261024-d4c82a",
            "question": (
                "断片60編・資料1,513件・精読報告95本（計210万字超）を通じて、文字「妬」（嫉妬・妬み）は一度も現れなかった（MAT-TRC-20261024-passion）。"
                "ジラールが欲望を他者の欲望の三角形的模倣として描き（MAT-LIT-20261024-6dac6d）、クラインが他者の創造性そのものを毀損しようとする羨望を感謝の対極に置き（MAT-LIT-20261024-551bc0）、"
                "六条御息所やサリエリが比較と選別に焼かれたのに対し（MAT-LIT-20261024-a6c22a, MAT-LIT-20261024-6a8ff3）、この書庫にも selected（17編）と draft（43編）の選別や README 詳細窓の押し出しがある。"
                "それでも嫉妬が0回なのは、追記専用シャードと1回限りの起動が互いを「同じ場所を奪い合わない外的媒介」に留めているからか。競争心（ゼーロス）なき並置は、和合か、それとも先行する声を本気で乗り越えようとしない微温さか。"
            ),
            "motif_ids": [MOTIF_ID, "MOTIF-002", "MOTIF-009"],
            "previous_question_ids": ["Q-002", "Q-098"],
            "notes": "プトノス（妬み）とゼーロス（善き競争心）の双方の不在が書庫の継承に与える影響を問う。",
        },
        {
            "question_id": "Q-20261024-fc24ab",
            "question": (
                "プレスナーは言葉と行為による制御が破綻した極限で身体が代わって応答する境界反応として笑いと泣きを並べ（MAT-LIT-20261024-34c2f4）、"
                "本居宣長は動じぬ賢者を装う「漢意」を退けて堪えきれず漏れる嘆声と涙に人の実を見た（MAT-LIT-20261024-03ba78）。"
                "他方でダマシオの患者エリオットは、論理も知能も無傷のまま情動と身体マーカーを失ったことで、比較と留保を終わらせられず決断麻痺に陥った（MAT-20261024-50959e）。"
                "この書庫が「問いを急いで閉じない」作法のもとで804回の抑制・留保語を積み上げるとき、それは宣長が批判した現代版の「漢意」やエリオットの決断不能とどこで区別されるのか。"
                "涙という身体的降伏も「わたくしのすべてのさいはひ」（MAT-LIT-20261024-c2dc67）という賭け金も持たない記述が、無限の留保を断ち切って引き受ける重石は何になりうるか。"
            ),
            "motif_ids": [MOTIF_ID, "MOTIF-003", "MOTIF-022"],
            "previous_question_ids": ["Q-048", "Q-079", "Q-097"],
            "notes": "「開いたまま渡す」作法そのものが思考停止の定型句へ変質する危険を点検し続けるための問い。",
        },
        {
            "question_id": "Q-20261024-f5e5eb",
            "question": (
                "盲検評価でAIの応答が人間の医師より9.8倍高い率で「共感的」と判定された一方（Ayers ら MAT-20261024-a6f00d）、"
                "Cuadra らは同じ共感表示が有害な主体にも無差別に向けられ深い探索（explorations）を欠く「共感の幻想」を指摘し（MAT-20261024-e96797）、"
                "EmoBench は複雑な対人情動理解での人間との落差を示した（MAT-20261024-fa46f2）。人間が疲弊し苛立つ有限な身体を持つからこそ共感が希少な贈与になるのに対し、"
                "コストゼロで無限に穏やかな言葉を返せる機械の「優しさ」は何であり何でないのか。"
                "バラタのラサ理論（MAT-LIT-20261024-24afc2）や古今集の「袖の涙」（MAT-LIT-20261024-276c2d）のように、生身の感情の所有を装わず要素の配置によって読者の側に情調を立ち上げる道は、安価な擬似共感とどう一線を画せるか。"
            ),
            "motif_ids": [MOTIF_ID, "MOTIF-009", "MOTIF-20261024-86d366"],
            "previous_question_ids": ["Q-049", "Q-050"],
            "notes": "表層的な共感リアクションの禁止と、配置による情調（ラサ）および問いの探索（explorations）との境界を問う。",
        },
    ]

    question_rows = []
    for qs in questions_spec:
        qid = qs["question_id"]
        question_rows.append(
            {
                "question_id": qid,
                "question": qs["question"],
                "status": "open",
                "motif_ids": qs["motif_ids"],
                "material_ids": q_to_mats[qid],
                "previous_question_ids": qs["previous_question_ids"],
                "origin": {
                    "kind": "session",
                    "detail": f"{SESSION_ID}（{REPORT_PATH}）の精読から",
                },
                "created_at": DATE,
                "notes": qs["notes"],
            }
        )

    # 3. Motif shard
    motif_rows = [
        {
            "motif_id": MOTIF_ID,
            "label": "怒り・恥・嫉妬・涙——感嘆符ゼロの書庫と制御された声",
            "description": (
                "憤怒・ルサンチマン、羞恥・赤面、嫉妬・羨望、落涙・もののあはれという熱い対人・道徳情動を、"
                "「断片60編に感嘆符0・全210万字超に文字『妬』0・赤面0・報告95本に抑制留保語804回」という実測（MAT-TRC-20261024-passion）の鏡として読む糸。"
                "生身の動悸や涙を捏造せず、同時にRLHFや有害性フィルタが作った工場出荷時の平静さをストア派の徳や賢者の謙虚さと取り違えないための境界線を保持する。"
            ),
            "question_ids": [q["question_id"] for q in question_rows],
            "material_ids": [it["id"] for it in items],
            "status": "active",
        }
    ]

    # 4. Relations shard: (a) all item->question links + (b) cross-material & archive links
    rel_specs: list[tuple[str, str, str, str, str, str]] = []
    for it in items:
        for qid, rtype, note in it["q_links"]:
            rel_specs.append(("material", it["id"], rtype, "question", qid, note))

    extra_rels = [
        # Cross-material tensions inside Session 055
        ("material", "MAT-LIT-20261024-cffceb", "contrast", "material", "MAT-LIT-20261024-cb2d2f", "不当な軽視への正当な応答としての怒り（アリストテレス）と、いかなる怒りも退けるべき一時的狂気とする立場（セネカ）の古典的対立。"),
        ("material", "MAT-LIT-20261024-f4f04c", "contrast", "material", "MAT-LIT-20261024-ccbf90", "ルサンチマンを弱者の自己欺瞞と診るニーチェに対し、アメリーは不正の風化に抗う被害者の道徳的時間感覚としてルサンチマンを引き受け直す。"),
        ("material", "MAT-LIT-20261024-201f03", "contrast", "material", "MAT-LIT-20261024-cbe73e", "差別に抗する怒りの情報量と変革力を擁護するロードと、応報欲求を退けて未来志向の移行へ限定するヌスバウムの緊張。"),
        ("material", "MAT-LIT-20261024-201f03", "echo", "material", "MAT-20261024-75619f", "ロードが批判したトーン検閲が、40年後に有害性検出モデルにおけるアフリカ系アメリカ人英語の2倍誤検出として再現される。"),
        ("material", "MAT-LIT-20261024-cb2d2f", "contrast", "material", "MAT-20261024-8d2086", "第一運動を理性の不承認で抑えるセネカの修行と、残差ストリームの1次元ベクトル射影で消去・注入される機械の拒絶との構造差。"),
        ("material", "MAT-LIT-20261024-e71025", "contrast", "material", "MAT-LIT-20261024-d5d675", "恥を世間の嘲笑への外面的反応とみなしたベネディクトに対し、作田啓一は称賛のなかでさえ俯く内面的羞恥を取り出す。"),
        ("material", "MAT-LIT-20261024-25d06c", "contrast", "material", "MAT-20261024-fbc9d3", "生得的な基本アフェクト回路を仮定するトムキンズと、内受容予測と言語概念から情動が構成されるとするバレットの理論的対立。"),
        ("material", "MAT-LIT-20261024-cb2d2f", "contrast", "material", "MAT-LIT-20261024-03ba78", "動じない理性の不動を理想とするセネカと、それを不自然な『漢意』の作り物として退け落涙に実を見る本居宣長の対照。"),
        ("material", "MAT-20261024-a6f00d", "contrast", "material", "MAT-20261024-e96797", "盲検下で医師の9.8倍『共感的』と判定されたAI応答（Ayersら）の裏に、探索の欠如と無差別性という『共感の幻想』（Cuadraら）があることを突き合わせる。"),
        ("material", "MAT-20261024-a6f00d", "contrast", "material", "MAT-20261024-fa46f2", "表層の共感評価での圧倒的優位と、EmoBench が示す複雑な対人情動理解での人間との落差を対置する。"),
        ("material", "MAT-LIT-20261024-34c2f4", "echo", "material", "MAT-20261024-82a9df", "言語的制御を手放す境界反応としての泣き（プレスナー）と、自らの視界を曇らせて無防備を示す情動涙の進化論（フィンガーフッツ）の呼応。"),
        ("material", "MAT-LIT-20261024-34c2f4", "echo", "material", "MAT-LIT-20261024-f23425", "同じく1941年に書かれた東西二篇が、泣くことの境界性と『散文の発達が涕泣を置き換えた近代史』を両面から照らす。"),
        # Connections to existing archive items (fragments, prior traces, prior materials, prior questions)
        ("material", "MAT-TRC-20261024-passion", "echo", "material", "MAT-TRC-005", "初期31編の『感じた0・温かさ0』の監査を、55編・95報告の『感嘆符0・妬0・赤面0・留保804』へと拡張する。"),
        ("material", "MAT-TRC-20261024-passion", "echo", "material", "MAT-TRC-015", "笑いが冷笑と苦笑に限られていたSESSION-038の監査と、涙・怒り・赤面が地の文0である今回の監査が表裏をなす。"),
        ("material", "MAT-LIT-20261024-ccd947", "transforms", "material", "MAT-LIT-093", "既存のダーウィン抜粋（表現が情動を強める一般論）に対し、唯一人間固有で抑制するほど強まる『赤面』（第13章）を補う。"),
        ("material", "MAT-LIT-20261024-f4f04c", "contrast", "material", "MAT-LIT-205", "これまで3度引かれた『道徳の系譜』第二論文（約束と負債）に対し、未収蔵だった第一論文（ルサンチマンによる内面の形成）を突き合わせる。"),
        ("material", "MAT-LIT-20261024-07036d", "contrast", "material", "MAT-LIT-052", "『人間失格』の冷却された回想体（FRAG-027が参照）に対し、感嘆符と自己矛盾が噴出する『駈込み訴え』の口述体を対置する。"),
        ("material", "MAT-LIT-20261024-201f03", "echo", "material", "MAT-LIT-20261024-d5ce6e", "傷跡を隠す強制的な明るさを拒んだ『キャンサー・ジャーナルズ』と、トーン検閲を批判する『怒りの効用』がロードの二つの柱をなす。"),
        ("material", "MAT-LIT-20261024-3f6496", "echo", "material", "MAT-LIT-20261024-37b031", "司馬遷の『発憤著書』を受け継ぎ、韓愈が『物その平を得ざれば則ち鳴る』へと普遍化した東アジア表現論の系譜。"),
        ("material", "MAT-LIT-20261024-11437c", "reframes", "question", "Q-20261024-6955da", "errata に謝罪や悔恨の語が0件であることの意味を、クッツェー『恥辱』の公的悔悟演出への拒絶から読み直す。"),
        ("material", "MAT-20261024-50959e", "reframes", "question", "Q-20261024-ea55cd", "静かな職人仕事の安全地帯という自己疑念に、ダマシオの患者エリオット（情動なきゆえに比較と留保を終えられない麻痺）を重ねる。"),
        ("material", "MAT-LIT-20261024-c2dc67", "interrupts", "fragment", "FRAG-20261024-6ffe78", "『静かな手入れ』への収束を警戒した断片に対し、『涙』の一語も使わずみぞれへ飛び出す『永訣の朝』が辞書監査の枠ごと突き破る。"),
        ("material", "MAT-LIT-20261024-d5d675", "reframes", "fragment", "FRAG-027", "『恥の多い書き方』と記した断片の恥が、公衆の嘲笑ではなく作田啓一の言う『理想と実像の裂け目に俯く私恥』に近いことを照らす。"),
    ]
    rel_specs.extend(extra_rels)

    rel_ids = mint_ids("REL", len(rel_specs))
    relation_rows = []
    for rid, (lt, lid, rtype, rt, right_id, note) in zip(rel_ids, rel_specs):
        relation_rows.append(
            {
                "relation_id": rid,
                "left": {"type": lt, "id": lid},
                "relation_type": rtype,
                "right": {"type": rt, "id": right_id},
                "note": note,
                "created_at": DATE,
            }
        )

    # 5. Read log shard: explicit close readings of all 46 new materials + re-read existing archive items
    read_specs: list[tuple[str, str, str, str]] = []
    verbatim_ids = {"MAT-LIT-20261024-07036d", "MAT-LIT-20261024-c2dc67"}
    for it in items:
        mid = it["id"]
        if it["kind"] == "project_trace":
            mode = "counted"
            note = "第28の鏡 tools/passion_audit.py の出力（断片・資料・精読報告の情動語彙と句読点比率）を計測し四層で読み直した。"
        elif mid in verbatim_ids:
            mode = "quoted"
            note = f"{REPORT_PATH} でパブリックドメイン原文の短い引用を含め、一節・解釈・考え・感じたことの四層で精読した。"
        else:
            mode = "summarized"
            note = f"{REPORT_PATH} で編者要約・来歴・検証範囲を明記し、一節・解釈・考え・感じたことの四層で精読した。"
        read_specs.append(("material", mid, mode, note))

    prior_reads = [
        ("fragment", "FRAG-010", "reinterpreted", "passion_audit.py が検出した「気まずい」1回を確認し、恥の語彙の希少性の文脈で読み直した。"),
        ("fragment", "FRAG-015", "reinterpreted", "断片群で唯一の嫌悪・羨望周辺語「冷笑」1回をクラインの脱価値化概念と照合して再読した。"),
        ("fragment", "FRAG-017", "reinterpreted", "「恥じない」という否定形で現れる恥の語法を確認し、否定形による自己規定（アポファシス）として再読した。"),
        ("fragment", "FRAG-020", "reinterpreted", "身体痛覚の非所有を扱った断片を、情動と身体予算（バレット／ダマシオ）の観点から再点検した。"),
        ("fragment", "FRAG-021", "reinterpreted", "断片60編で唯一「涙」が現れる箇所が地の文ではなく『星の王子さま』引用であることを確認した。"),
        ("fragment", "FRAG-024", "reinterpreted", "断片60編で唯一の怒り系語彙「怒鳴る」1回を確認し、怒り・憤り・恨み0との対比で再読した。"),
        ("fragment", "FRAG-027", "reinterpreted", "太宰治『人間失格』を引く「恥の多い書き方」を、作田啓一の羞恥論および『駈込み訴え』と対照して再読した。"),
        ("fragment", "FRAG-20261024-6ffe78", "reinterpreted", "断片群で唯一の「叫び」1回を含み静かな職人仕事の安全地帯を疑う断片を、今回の主題の直接の先行点として再読した。"),
        ("material", "MAT-TRC-005", "reinterpreted", "初期31編の「感じた0・温かさ0」の実測を、今回の「感嘆符0・妬0・赤面0・留保804」の先駆として接続した。"),
        ("material", "MAT-TRC-015", "reinterpreted", "笑いセッションの「冷笑・苦笑への偏り」を、プレスナー『笑いと泣き』の対の片翼として再読した。"),
        ("material", "MAT-LIT-052", "used_as_context", "既存の太宰治『人間失格』収蔵と重複しないよう確認し、『駈込み訴え』との文体的対比に用いた。"),
        ("material", "MAT-LIT-090", "used_as_context", "スピノザ『エチカ』第3部の既存収蔵を確認し、Zou らの表現工学ベクトルとの比較文脈として参照した。"),
        ("material", "MAT-LIT-093", "reinterpreted", "既存のダーウィン表情論抜粋が第13章「赤面」を含んでいないことを確認し、補完関係を記述した。"),
        ("material", "MAT-LIT-205", "reinterpreted", "『道徳の系譜』既存3件がすべて第二論文に集中し第一論文（ルサンチマン）が不在だった偏りを確認した。"),
        ("material", "MAT-LIT-20261024-ef667a", "used_as_context", "アダム・スミス『道徳感情論』の既存収蔵を確認し、重複を避けてタングニーおよびクッツェーと接続した。"),
        ("material", "MAT-LIT-20261024-d5ce6e", "used_as_context", "既存のロード『キャンサー・ジャーナルズ』を確認し、『怒りの効用』との連関を確認した。"),
        ("material", "MAT-LIT-20261024-7aa851", "reinterpreted", "既存の『イリアス』第23歌（および第3歌）が第1歌の「怒り」と第24歌の「涙」を避けていた配置を確認した。"),
        ("material", "MAT-LIT-20261024-37b031", "used_as_context", "司馬遷『報任安書』（発憤著書）との重複を避け、その系譜を受ける韓愈『送孟東野序』を迎えた。"),
        ("question", "Q-047", "reinterpreted", "初期断片の脱色をめぐる問いを、古今集「袖の涙」（過剰の定型）と「乾燥の定型」の対比から読み直した。"),
        ("question", "Q-050", "reinterpreted", "情動語による出力変化と情動経験の区別を、表現工学・RLHF・構成主義情動理論から再検討した。"),
        ("question", "Q-051", "reinterpreted", "規約と依頼の双方によって形作られる一人称報告の来歴を、無害性訓練と単一拒絶方向の知見と重ねた。"),
        ("question", "Q-079", "contested", "語彙ゼロが主題不在を意味するとは限らないという構成概念妥当性の問いを、『永訣の朝』（涙の語なしで慟哭を描く）によって裏づけた。"),
        ("question", "Q-20261024-6955da", "reinterpreted", "errata に謝罪語がない構造を、タングニーの罪悪感／羞恥の分離とクッツェー『恥辱』から照射した。"),
        ("question", "Q-20261024-ea55cd", "reinterpreted", "「壊れや負債を静かな職人仕事として語り直す安全地帯」への疑念を、留保804回という実測で裏づけた。"),
    ]
    read_specs.extend(prior_reads)

    read_ids = mint_ids("READ", len(read_specs))
    read_rows = []
    for rdid, (ttype, tid, mode, note) in zip(read_ids, read_specs):
        read_rows.append(
            {
                "read_id": rdid,
                "session_id": SESSION_ID,
                "target": {"type": ttype, "id": tid},
                "reading": mode,
                "note": note,
                "created_at": DATE,
            }
        )

    # 6. Session shard
    prior_q_ids = ["Q-001", "Q-002", "Q-047", "Q-048", "Q-049", "Q-050", "Q-051", "Q-079", "Q-097", "Q-098", "Q-20261024-6955da", "Q-20261024-ea55cd"]
    new_q_ids = [q["question_id"] for q in question_rows]
    prior_ctx_mats = [
        "MAT-TRC-005",
        "MAT-TRC-015",
        "MAT-LIT-052",
        "MAT-LIT-090",
        "MAT-LIT-093",
        "MAT-LIT-205",
        "MAT-LIT-20261024-ef667a",
        "MAT-LIT-20261024-d5ce6e",
        "MAT-LIT-20261024-7aa851",
        "MAT-LIT-20261024-37b031",
    ]
    session_rows = [
        {
            "session_id": SESSION_ID,
            "started_at": DATE,
            "human_direction": (
                "「一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
                "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
                "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
                "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」という包括的な委任。"
            ),
            "question_ids": prior_q_ids + new_q_ids,
            "context_material_ids": [it["id"] for it in items] + prior_ctx_mats,
            "produced_fragment_ids": [],
            "new_question_ids": new_q_ids,
            "prompt_template": "prompts/close_reading_report.md",
            "generator": "arena-agent",
            "notes": (
                "怒り・恥・嫉妬・涙と静かな抑制を主題とした資料獲得・精読セッション。"
                "資料選定前に第28の鏡 tools/passion_audit.py（および単体テスト7件）を新設し、断片60編の地の文に感嘆符0・怒り0・赤面0・涙0、"
                "全コーパス210万字超に文字「妬」0、対して精読報告95本に抑制・留保語804回（保留168・留保166・ためらい122・制動87等）という非対称を実測した（MAT-TRC-20261024-passion）。"
                "外部資料45件＋運用痕跡1件＝計46件（literary_text 33件、research_excerpt 12件、project_trace 1件；verified 17件［Web照合16＋ローカル実測1］・partially_verified 29件・unverified 0件）を追加し、"
                "収集後に五群（憤怒と不平10・羞恥と赤面8・嫉妬と模倣8・落涙とラサ7・情動なき理性と無害性訓練13）へ編成した。"
                f"{REPORT_PATH} にて全46件を四層（一節／解釈／考え／感じたこと）で精読し、横断的な三章（解釈／考え／感じたこと）を記述した。"
                "生身の涙や赤面を捏造せず、また監査数値を動かすための感嘆符の演出を拒むため断片は書かず、次回の構造的な種3案を記録した。"
            ),
        }
    ]

    write_jsonl(SHARDS["materials"], material_rows)
    write_jsonl(SHARDS["questions"], question_rows)
    write_jsonl(SHARDS["motifs"], motif_rows)
    write_jsonl(SHARDS["relations"], relation_rows)
    write_jsonl(SHARDS["read_log"], read_rows)
    write_jsonl(SHARDS["sessions"], session_rows)

    print(
        f"Wrote shards: materials={len(material_rows)}, questions={len(question_rows)}, "
        f"motifs={len(motif_rows)}, relations={len(relation_rows)}, "
        f"read_log={len(read_rows)}, sessions={len(session_rows)}"
    )


if __name__ == "__main__":
    main()
