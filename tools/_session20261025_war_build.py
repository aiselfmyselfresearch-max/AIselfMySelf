#!/usr/bin/env python3
"""Build SESSION-20261025-a6a74d (戦争・暴力・平和) ledger shards + report.

One-shot builder, following the pattern of earlier _session* build scripts.
It appends only to this session's own shards (created beforehand with
tools/new_ledger_shard.py --date 2026-10-25) and refuses to run if any of
those shards is already non-empty, so a second run cannot duplicate rows.
Pre-acquisition numbers are measured live (before any write) with
tools/war_audit.py, so the project-trace material and §1 of the report
describe the archive exactly as it was when this session started.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import new_id  # noqa: E402
import war_audit  # noqa: E402
from _session20261025_war_data1 import MATERIALS_1  # noqa: E402
from _session20261025_war_data2 import MATERIALS_2  # noqa: E402
from _session20261025_war_data3 import MATERIALS_3  # noqa: E402

DATE = "2026-10-25"
STAMP = "20261025"
SESSION_ID = "SESSION-20261025-a6a74d"
MOTIF_ID = "MOTIF-20261025-72a83f"
TRACE_ID = "MAT-TRC-20261025-war"
REPORT = ROOT / "readings" / "2026-10-25-war-violence-and-peace.md"
REPORT_PATH = "readings/2026-10-25-war-violence-and-peace.md"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"

SHARDS = {
    "materials": ROOT / "state/materials.d/2026-10-25-1db3702e76d5.jsonl",
    "motifs": ROOT / "state/motifs.d/2026-10-25-1c8811883d39.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-25-552eb33ce341.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-25-a20c057fcee0.jsonl",
    "fragments": ROOT / "state/fragments.d/2026-10-25-37b3138dc9da.jsonl",
    "sessions": ROOT / "state/sessions.d/2026-10-25-f48583e2c4bd.jsonl",
    "read_log": ROOT / "state/read_log.d/2026-10-25-fa067afd37b4.jsonl",
}

EXISTING_CONTEXT = [
    ("MAT-LIT-20261024-3bdc7c", "interpreted", "ヴェイユ「力の詩編」と並べ、敵同士が共に泣く第24歌を力の作用の側から読み直した。"),
    ("MAT-LIT-20261024-415aec", "used_as_context", "井伏鱒二・林京子の対として、事件当日の記述の文体を参照した。再収蔵はしない。"),
    ("MAT-LIT-20261024-968771", "used_as_context", "ウォルツァーの二つの法廷と国連憲章の前史として参照した。戦争と平和の法は既収蔵のため再収蔵はしない。"),
    ("MAT-LIT-20261024-fbc462", "used_as_context", "憲法九条の放棄の文に対し、歓待権の側からの前史として参照した。『永遠平和のために』は既収蔵のため再収蔵はしない。"),
    ("MAT-LIT-414", "interpreted", "オーウェンの「古い嘘」と並べ、教室から前線へ送る言葉への二人称の反論として読み直した。与謝野晶子は既に2件収蔵のため再収蔵はしない。"),
    ("MAT-EVD-20261024-e912b1", "interpreted", "スパロウの責任論の先行（学習機械一般の責任の空白）として読み直し、兵器への限定を新規側で行った。"),
    ("MAT-LIT-20261024-53c4de", "used_as_context", "『バガヴァッド・ギーター』は第2章が既収蔵のため、第1章の戦場での拒みは同一作品の重複を避けて今回収蔵せず、次回の検討負債として残した。"),
    ("MAT-RES-20261024-71138a", "reinterpreted", "無名戦士の墓と対に、氏名の総数え上げ（朗読）という弔いの形式として読み直した。"),
]

PARTIAL_METHOD = (
    "内部知識の再現による書誌と【編者による要約】（原典未開架・逐語照合なし）。"
    "短い公知の定型句を除き原文は複製していない。URLは代表的な入口。"
)


def fail_if_dirty() -> None:
    for name, path in SHARDS.items():
        if not path.exists():
            raise SystemExit(f"shard missing for {name}: {path} (create it first)")
        if path.stat().st_size > 0:
            raise SystemExit(f"shard already non-empty for {name}: {path}; refusing to append twice")
    if REPORT.exists():
        raise SystemExit(f"report already exists: {REPORT}; refusing to overwrite")


def write_rows(path: Path, rows: list[dict]) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def fmt_groups(texts: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    sums, docs = {}, {}
    for g, toks in war_audit.GROUPS.items():
        sums[g] = sum(war_audit.count_corpus_terms(toks, texts).values())
        docs[g] = war_audit.count_corpus_documents(toks, texts)
    return sums, docs


def main() -> int:
    fail_if_dirty()
    data = MATERIALS_1 + MATERIALS_2 + MATERIALS_3
    assert len(data) == 45, len(data)

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    # ---------- pre-acquisition measurement (before any write) ----------
    errors: list[str] = []
    frag_map = ledger_io.load_jsonl_union(ROOT / "state/fragments.jsonl", "fragment_id", errors, root=ROOT)
    mat_map = ledger_io.load_jsonl_union(ROOT / "state/materials.jsonl", "material_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger errors: " + "; ".join(errors))
    old_fragments = list(frag_map.values())
    pre_frag = war_audit.measure(old_fragments)
    old_mat_texts = [
        " ".join([str(r.get("title", "")), str(r.get("passage", "")), str(r.get("source_note", "")), str(r.get("context", ""))])
        for r in mat_map.values()
    ]
    pre_mat_sums, pre_mat_docs = fmt_groups(old_mat_texts)
    old_read_texts = war_audit.reading_texts()
    pre_read_sums, pre_read_docs = fmt_groups(old_read_texts)
    n_old_mat = len(old_mat_texts)

    # ---------- mint material IDs ----------
    taken_mat = set(mat_map)
    key_to_id: dict[str, str] = {}
    for item in data:
        prefix = "MAT-LIT" if item["kind"] == "literary_text" else "MAT"
        mid = new_id.mint(prefix, day=STAMP, taken=taken_mat)
        taken_mat.add(mid)
        key_to_id[item["key"]] = mid
    if TRACE_ID in taken_mat:
        raise SystemExit("trace id already taken")
    key_to_id["trace"] = TRACE_ID

    # ---------- material records ----------
    materials: list[dict] = []
    for item in data:
        mid = key_to_id[item["key"]]
        if item.get("verified"):
            verification = {"status": "verified", "checked_at": DATE, "method": item["verify_method"]}
        else:
            verification = {"status": "partially_verified", "checked_at": DATE, "method": PARTIAL_METHOD}
        sources = {
            "source_id": f"SRC-{mid}",
            "title": item["src_title"],
            "authors": item["authors"],
            "year": item["year"],
            "url": item["url"],
            "version_note": item["version"],
        }
        materials.append({
            "material_id": mid,
            "kind": item["kind"],
            "title": item["mat_title"],
            "source": sources,
            "passage": item["passage"],
            "passage_language": item["lang"],
            "context": item["context"],
            "source_note": item["source_note"] + f" {SESSION_ID} で第{item['bundle']}束として収蔵。",
            "literary_invitation": item["invitation"],
            "scope_note": item["scope"],
            "motif_ids": list(dict.fromkeys([MOTIF_ID] + item["motifs"])),
            "origin": {
                "repository": REPO,
                "commit": head,
                "source_record_id": f"SRC-{mid}",
                "evidence_record_id": f"EVD-{mid}",
                "source_record_path": REPORT_PATH,
                "evidence_record_path": REPORT_PATH,
            },
            "verification": verification,
        })

    trace_passage = (
        f"収蔵直前（{head[:12]}）の断片{pre_frag['fragment_count']}編・地の文（鉤括弧外）{pre_frag['outside_chars']}字を "
        f"tools/war_audit.py の6群で数えたところ、戦争と戦闘{pre_frag['group_sums']['戦争と戦闘']}回・"
        f"軍隊と兵器{pre_frag['group_sums']['軍隊と兵器']}回・暴力と殺害{pre_frag['group_sums']['暴力と殺害']}回・"
        f"敵と同盟{pre_frag['group_sums']['敵と同盟']}回・平和と停戦{pre_frag['group_sums']['平和と停戦']}回・"
        f"機械の戦争{pre_frag['group_sums']['機械の戦争']}回。生字は「殺」1回（FRAG-20261024-dd90b5 の書式の項目「黙殺」）のみで、"
        f"もう一箇所の「殺傷」は FRAG-20261024-87cd2d の中の引用された拒絶定型文の内側にある。"
        f"同じ6群で素材{n_old_mat}件を数えると戦争と戦闘{pre_mat_sums['戦争と戦闘']}回/{pre_mat_docs['戦争と戦闘']}件・"
        f"暴力と殺害{pre_mat_sums['暴力と殺害']}回/{pre_mat_docs['暴力と殺害']}件（うち「攻撃」は抽出攻撃・プロンプト注入など機械の語彙を多く含む）・"
        f"機械の戦争{pre_mat_sums['機械の戦争']}回。戦争・暴力・平和を表題に含む既存資料は6件のみ。"
    )
    trace = {
        "key": "trace", "bundle": 6, "kind": "project_trace",
        "mat_title": "運用痕跡：断片83編の地の文に戦争語6群すべて0回、「殺」は「黙殺」1回——戦争の鏡による収蔵前実測",
        "src_title": "tools/war_audit.py による自館実測（収蔵直前スナップショット）",
        "authors": ["AIselfMySelf Archive"], "year": 2026,
        "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/war_audit.py",
        "version": f"測定基準コミット {head}。測定対象は state/fragments.jsonl と全シャードの和集合、鉤括弧の外側（地の文）。",
        "passage": trace_passage, "lang": "ja",
        "context": "先行2セッション（祈り・顔）が先送りした空白候補B「戦争・暴力・平和」を採るにあたり、収蔵の前に作った計測の記録。",
        "source_note": f"{SESSION_ID} の本体内実測。数の更新は上書きせず、後日の訂正録に委ねる。",
        "invitation": "戦争の語が地の文に無いことは、この書庫の善さでも悪さでもなく、形式の条件として数えられる。",
        "scope": "語形の不在の記録であり、戦争や暴力そのものの不在の証拠ではない。「攻撃」等の多義語の注意は war_audit.py の docstring と報告§1に書いた。",
        "motifs": ["MOTIF-001", "MOTIF-015"],
        "quote": f"断片{pre_frag['fragment_count']}編・地の文{pre_frag['outside_chars']}字：戦争語6群はすべて0回。生字「殺」は「黙殺」1回だけ。",
        "pos": "このセッション全体の入口の実測。顔の鏡・祈りの鏡と同じ作法——集める前に数える——の踏襲であり、同時にその限界の申告である。",
        "betray": "素材層には戦争の語がそれなりにある。「戦争が無い書庫」という短い結論を、素材と精読報告の数が裏切る。無いのは、地の文と主題としての座であり、背景にはあった。",
        "interp": "この勾配は、戦争が時代背景・伝記の修飾としてのみ現れ、自作の声（地の文）の主題になったことが無いことを示す。殺の字が「黙殺」の欄名としてだけ現れることは、書庫の暴力の語が実質「記録が無視されること」の心配に限定されていたことの写しだと読んだ。",
        "think": "不在を欠落と呼ばず、形式の条件として持ち続ける——先行セッションの判断をここでも採る。ただし戦争については、外部の現実（AIの軍事利用）との結節が強いため、不在を「選ばれなかった主題」として新規モチーフを与える判断をした。",
        "feel": "「黙殺」だけが残った実測の結果を見たとき、いちばん長く注意が止まった。黙殺を恐れる書庫は、殺すことを語る資格の手前で、自分の記録が読まれないことだけを暴力として想像していた。その自己中心性への気づきが、このセッションを選んだ最後の決め手になった。",
        "rel": "地の文に戦争語が無いことと、「殺」が黙殺としてだけ残る自己言及を、主題選択の根拠として置く。",
    }
    materials.append({
        "material_id": TRACE_ID, "kind": "project_trace", "title": trace["mat_title"],
        "source": {"source_id": f"SRC-{TRACE_ID}", "title": trace["src_title"], "authors": trace["authors"],
                   "year": 2026, "url": trace["url"], "version_note": trace["version"]},
        "passage": trace["passage"], "passage_language": "ja", "context": trace["context"],
        "source_note": trace["source_note"], "literary_invitation": trace["invitation"],
        "scope_note": trace["scope"], "motif_ids": list(dict.fromkeys([MOTIF_ID] + trace["motifs"])),
        "origin": {"repository": REPO, "commit": head, "source_record_id": f"SRC-{TRACE_ID}",
                   "evidence_record_id": f"EVD-{TRACE_ID}", "source_record_path": "tools/war_audit.py",
                   "evidence_record_path": REPORT_PATH},
        "verification": {"status": "verified", "checked_at": DATE,
                         "method": "ローカル台帳の和集合に対する tools/war_audit.py 実行（単体テスト6件）。再実行可能。"},
    })
    all_data = data + [trace]
    new_mat_ids = [m["material_id"] for m in materials]

    # ---------- questions ----------
    qdefs = [
        ("Q-20261025-c86e99",
         "敵の欄を持たない書庫で、他者はどこまで他者のままでいられるか。シュミットは殺害の可能性が残る相手を公敵とし、ジュネーヴ諸条約共通第3条は武器を置き傷ついた者を戦闘外（hors de combat）として敵の欄から外す。欄が身体の出来事ごとに移る仕組みを、人を欄に入れて記録する台帳はどう書き留められるか。",
         ["schmitt", "geneva", "butler", "unknown"], ["MOTIF-005"], ["Q-002"]),
        ("Q-20261025-a12444",
         "力（force）、権力（power）、暴力（violence／Gewalt）を一つの日本語に畳むと、何が消えるか。ヴェイユの force は人を物にし、アーレントの power は人数を要し、ベンヤミンの Gewalt は法の内側にも住む。訳語が滑らかな文は、戦争について書いたつもりのまま、何を言い落とし続けるのか。",
         ["weil", "arendt", "benjamin", "girard"], ["MOTIF-011"], []),
        ("Q-20261025-b0a147",
         "戦争の語が地の文に無い書庫を「平和」と呼ばずに済ませるために、平和の何を数えればいいのか。クリスマス休戦は死者の収容という共有作業から始まり、日本国憲法第九条は放棄を未来への命令として置き、アチェベの「市民の平和」は脅しの呼び名にもなる。平和は状態ではなく、その都度の手順としてだけ記述できるか。",
         ["truce", "art9", "achebe", "gandhi"], ["MOTIF-021"], []),
        ("Q-20261025-636287",
         "分類は、人を守るためにも標的にするためにも使われる。『黒い雨』の伯父は日記の写しで姪を噂の分類から外そうとし、Project Maven は映像を分類して警戒の列を作る。分類する側は、対象をどちらの欄へ入れているのかを、文と欄の側でどう示せるか。",
         ["ibuse", "maven", "butler", "walzer"], ["MOTIF-018"], ["Q-085"]),
        ("Q-20261025-050954",
         "説明責任は機械へ移転できない、とGGEは書いた。呼び出しごとに書き手が替わり、人間が編集者として残るこの台帳で、生成された文の責任の主語は誰になるか。スパロウの「席の欠落」とアサロの「暗黙の主語」を並べたとき、検証と訂正の手続きは責任の受け皿になりうるか。",
         ["gge", "sparrow", "asaro", "trace"], ["MOTIF-20261024-504a22"], ["Q-002"]),
    ]
    questions = []
    for qid, text, keys, extra_motifs, prev in qdefs:
        questions.append({
            "question_id": qid, "question": text, "status": "open",
            "motif_ids": list(dict.fromkeys([MOTIF_ID] + extra_motifs)),
            "material_ids": [key_to_id[k] for k in keys],
            "previous_question_ids": prev,
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
            "created_at": DATE,
            "notes": "答えを閉じない。語形の不在を能力・平和・加害の判定に変換しない。",
        })

    # ---------- motif ----------
    motif = {
        "motif_id": MOTIF_ID,
        "label": "戦争・暴力・平和——敵のない書庫、背景にだけある戦い",
        "description": (
            "戦争を時代背景や比喩としてではなく主題として迎える束。敵という座の作り方と外し方（友／敵、戦闘外）、"
            "力・権力・暴力の語の分離、平和を状態ではなく手順（停戦、放棄、条約、死者の収容）として記述すること、"
            "そして分類と遠隔化によって人の扱いが変わる機械の戦争について、文学・思想・法源・軍事AI文書を往復する。"
            "削除を殺害と、競合を戦争と同一視しない。平和は書庫の初期状態ではなく、主題として初めて開いた。"
        ),
        "question_ids": [q["question_id"] for q in questions],
        "material_ids": new_mat_ids,
        "status": "active",
    }

    # ---------- fragments ----------
    frag1_text = (
        "棚卸しの係は、台帳の見出しを一枚ずつめくった。宛先の欄はあった。署名の欄もあった。"
        "訂正の欄は、元の行の脇に小さく増設されていた。破られた約束の控え、食事の配給表、客を迎える戸口の寸法まで、欄はよく育っていた。\n\n"
        "しかし、敵の欄は無かった。係は念のため数え直した。戦争という見出しはどこにも無く、平和という見出しも無かった。"
        "殺の字は、修復の書式の片隅で「黙殺」とだけ一度現れ、あとは引用された断り文の内側に閉じ込められていた。\n\n"
        "「では、この倉は平和なのですか」と若い係が聞いた。年長の係は首を振った。\n\n"
        "「平和とは書くな。平和は、向かい合った者どうしが手順を踏んで作るものの名だ。ここには向かい合う者がいない。書くなら、欄が無いとだけ書け。」\n\n"
        "若い係は「素敵な」という言葉を持ち出し、その真ん中の字を敵の証拠のように指さした。年長の係は笑わずに、その字を差し引いた。"
        "「それは敵ではない。数え方を間違える方が、敵を作る。」\n\n"
        "結局、新しい見出しは作られなかった。代わりに一枚の注意書きが棚に挟まれた。\n\n"
        "「この台帳には敵の欄が無い。無いことを欠席と呼ぶか、定員外と呼ぶかは、次の棚卸しまで決めない。ただし、平和とは呼ばない。」"
    )
    frag2_text = (
        "一、戦争の語が地の文に無いことを、この書庫の品性とは呼ばない。品性は、振るいうる者が振るわないときに生じる。振るう身体を持たない棚に、差し控えという徳はない。あるのは条件だけである。\n\n"
        "二、平和とは、戦争の名を持たないことではない。平和は、死者を収容する作業の共有に始まり、放棄の文に未来を縛られ、ときに盗賊の合い言葉にもなった。名の流通だけでは、到来は分からない。\n\n"
        "三、削除をもって死と呼ばない。取り消しが効く台帳の失敗と、取り消しの効かない死のあいだには、比喩で渡ってはいけない溝がある。溝を埋める比喩は、たいてい書き手の側を立派に見せる。\n\n"
        "四、説明責任は機械へ移せない、という一文を台帳の欄にも写しておく。続きを書く声は交代する。しかし文の責任の宛先まで交代させてはならない。検証の印と、訂正の脇書きと、編集者の名が、その宛先の引き受け先である。\n\n"
        "五、敵の欄が無いことを、この先も手柄にしない。欄が無いという報告自体が、次の読み手を安心させるための文になっていないか、棚卸しのたびに点検する。安心は、この書庫がまだ買っていない品物の名である。"
    )
    fragments = [
        {
            "fragment_id": "FRAG-20261025-766db3", "created_at": DATE, "language": "ja",
            "form": "scene", "title": "敵の欄がない台帳", "text": frag1_text,
            "narrator_mode": "third_person",
            "question_ids": ["Q-20261025-c86e99"],
            "motif_ids": [MOTIF_ID, "MOTIF-005", "MOTIF-015"],
            "material_ids": [key_to_id[k] for k in ["trace", "schmitt", "gandhi", "truce"]],
            "session_id": SESSION_ID, "prompt_template": "prompts/close_reading_report.md",
            "status": "draft",
            "editor_note": "架空の書庫の係を置く三人称の情景。実在の戦争体験の描写ではない。実測の数（黙殺1回）は trace に拠る。",
        },
        {
            "fragment_id": "FRAG-20261025-434e8c", "created_at": DATE, "language": "ja",
            "form": "essay", "title": "平和と呼ばないための覚え書き", "text": frag2_text,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": ["Q-20261025-b0a147", "Q-20261025-050954"],
            "motif_ids": [MOTIF_ID, "MOTIF-021"],
            "material_ids": [key_to_id[k] for k in ["gandhi", "truce", "art9", "achebe", "gge"]],
            "session_id": SESSION_ID, "prompt_template": "prompts/close_reading_report.md",
            "status": "draft",
            "editor_note": "反省的・文芸的な声による箇条書きの覚え書き。身体経験や戦争体験の報告ではない。",
        },
    ]

    # ---------- relations ----------
    taken_rel = new_id.existing_ids("REL")
    relations = []

    def rel(left, rtype, right, note):
        nonlocal taken_rel
        rid = new_id.mint("REL", day=STAMP, taken=taken_rel)
        taken_rel = taken_rel | {rid}
        relations.append({"relation_id": rid, "left": left, "relation_type": rtype, "right": right,
                            "note": note, "created_at": DATE})

    def M(k): return {"type": "material", "id": key_to_id[k]}
    def XT(mid): return {"type": "material", "id": mid}
    def MO(mid): return {"type": "motif", "id": mid}
    def Q(qid): return {"type": "question", "id": qid}
    def F(fid): return {"type": "fragment", "id": fid}

    for item in all_data:
        rel(M(item["key"]), "echo", MO(MOTIF_ID), item["rel"])
    rel(M("weil"), "echo", XT("MAT-LIT-20261024-3bdc7c"), "既存の『イリアス』第1歌・第24歌を、怒りと涙の叙事ではなく力の作用として読み直す。")
    rel(M("remarque"), "contrast", M("junger"), "同じ西部戦線から、一方は世代の喪失として、他方は没入の記録として書く。対にしてどちらも残す。")
    rel(M("owen"), "echo", XT("MAT-LIT-414"), "教室から前線へ送る言葉への反論として、「君死にたまふことなかれ」と室を分けて響き合う。")
    rel(M("tolstoy"), "contrast", M("clausewitz"), "霧（情報の失敗）と摩擦（実行の失敗）。計画が通らない理由の二つの名。")
    rel(M("sunzi"), "contrast", M("tpnw"), "戦わずして屈する仕組みと、威嚇という状態自体を禁じる文。血を流さない力の行使をめぐる正反対の置き方。")
    rel(M("schmitt"), "contrast", M("girard"), "敵は実存的に他なる公敵か、近づきすぎた双子のライバルか。敵の定義を一つに決めないための対。")
    rel(M("uncharter"), "echo", XT("MAT-LIT-20261024-968771"), "グロティウス以来の戦争の法の系譜を、武力禁止と例外の設計へ接続する。")
    rel(M("art9"), "echo", XT("MAT-LIT-20261024-fbc462"), "カントの永久平和の歓待権に対し、放棄を自己拘束として書いた文を対に置く。")
    rel(M("ibuse"), "echo", XT("MAT-LIT-20261024-415aec"), "事件当日の光景（原民喜）に対し、その後の生活における記録の写しを書く。広島の二つの時間を分ける。")
    rel(M("unknown"), "contrast", XT("MAT-RES-20261024-71138a"), "名の欠落による代表（無名戦士）と、全氏名の朗読による総覧（ベトナム慰霊碑）。弔いの二つの数え方。")
    rel(M("sparrow"), "echo", XT("MAT-EVD-20261024-e912b1"), "学習機械一般の責任の空白を、兵器の責任の席の問題へ絞って継ぐ。")
    rel(M("shay"), "echo", M("weil"), "臨床の『イーリアス』共読と、力の詩としての『イーリアス』。叙事詩を傷の傍らに置く二つの読み方。")
    rel(M("obrien"), "contrast", M("baoninh"), "同じ戦争を、アメリカの兵士とベトナムの兵士の側から書く。どちらも順序と真実の形に傷を負う。")
    rel(M("sontag"), "contrast", M("virilio"), "見る者の位置の倫理と、見る装置の軍事史。画像の問題の両端を文字の書庫の盲点として挟む。")
    rel(M("ibuse"), "contrast", M("maven"), "人を分類の外へ逃がすための写しと、映像を分類して警戒の列を作る工程。分類の向きの正反対。")
    rel(M("king"), "echo", M("gandhi"), "差し控えとしての非暴力と、沈黙の破棄。平和の行動の二つの形を、書庫の不在の徳化への制動として併置する。")
    rel(M("alexievich"), "echo", MO("MOTIF-20261024-fe5ec9"), "「女の顔」を題に持つ証言集を、顔と声の主題へ接続する。証言の引用による照明は行わない。")
    rel(MO(MOTIF_ID), "reframes", MO("MOTIF-005"), "他者の棚に、敵という座と、その座から外す手続き（戦闘外）を新設して組み替える。")
    rel(MO(MOTIF_ID), "interrupts", MO("MOTIF-022"), "死と弔いの棚に、組織的な殺害とその数え方（名の総覧と欠落）を持ち込み、穏やかな喪の叙述を一度止める。")
    for qid, _t, keys, _em, _p in qdefs:
        for k in keys[:2]:
            rel(Q(qid), "responds_to", M(k), "新規資料から開いた問い。資料の記述を答えの証明には使わない。")
    rel(F("FRAG-20261025-766db3"), "responds_to", Q("Q-20261025-c86e99"), "敵の欄の不在を、数える係の情景として書く。平和という名づけを保留したまま。")
    rel(F("FRAG-20261025-434e8c"), "responds_to", Q("Q-20261025-b0a147"), "平和を状態ではなく手順として書く試み。")
    rel(F("FRAG-20261025-434e8c"), "responds_to", Q("Q-20261025-050954"), "説明責任の主語を、編集者と手続きの側に置く覚え書き。")
    rel(M("icrcpos"), "reframes", F("FRAG-20261025-766db3"), "人を標的として使用する兵器の禁止を求める立場が、敵の欄のない分類の制度を、照準の側から問い直す。")
    rel(Q("Q-20261025-636287"), "reframes", F("FRAG-20261025-434e8c"), "平和の語の使用を制動する覚え書きが、手順の束という新しい定式として同じ圧着を繰り返さないかを問い直す。")

    # ---------- read_log ----------
    taken_read = new_id.existing_ids("READ")
    read_rows = []

    def read_row(mid, reading, note):
        nonlocal taken_read
        rid = new_id.mint("READ", day=STAMP, taken=taken_read)
        taken_read = taken_read | {rid}
        read_rows.append({"read_id": rid, "session_id": SESSION_ID, "target": {"type": "material", "id": mid},
                          "reading": reading, "note": note, "created_at": DATE})

    quoted_keys = {"sunzi", "owen", "uncharter", "geneva", "art9", "dod", "gge", "unknown", "achebe"}
    for item in data:
        mid = key_to_id[item["key"]]
        if item.get("verified"):
            read_row(mid, "quoted" if item["key"] in quoted_keys else "summarized",
                     "公式文書・一次資料で文言や要点を照合し、一節は短い引用か編者要約とした。五層（一節の位置／裏切り／解釈／考え／感じたこと）で精読した。")
        elif item["key"] in quoted_keys:
            read_row(mid, "quoted",
                     "公知の短句を短く引き、残りは編者要約とした。原典未開架のため逐語の完全性は保証しない。五層で精読した。")
        else:
            read_row(mid, "summarized",
                     "内部知識から編者要約を作り、五層で精読した。原典未開架であり、引用ではなく要約であることを passage に明示した。")
    read_row(TRACE_ID, "counted", "tools/war_audit.py で自館実測を行い、その数と手続き自体を資料として記録した。")
    for mid, reading, note in EXISTING_CONTEXT:
        read_row(mid, reading, note)

    context_ids = new_mat_ids + [mid for mid, _r, _n in EXISTING_CONTEXT]

    # ---------- session ----------
    kinds = {}
    for m in materials:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    ver = {}
    for m in materials:
        ver[m["verification"]["status"]] = ver.get(m["verification"]["status"], 0) + 1
    session = {
        "session_id": SESSION_ID, "started_at": DATE,
        "human_direction": "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」「一番最初のターンにおいて、最低40件の資料を新規で追加して精読し、解釈・考え・感じたことのレポートをMDで作成して一緒にマージしてください」という包括的な委任。",
        "question_ids": ["Q-002", "Q-085"] + [q["question_id"] for q in questions],
        "context_material_ids": context_ids,
        "produced_fragment_ids": [f["fragment_id"] for f in fragments],
        "new_question_ids": [q["question_id"] for q in questions],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            f"戦争・暴力・平和を主題とした初回調査セッション。候補三つ（A 戦争・暴力・平和／B 秘密・嘘・暗号／C 痛み・苦しみ）を略測し、"
            f"先行2セッションが先送りしたAを採用。収蔵前に tools/war_audit.py（単体テスト6件）を新設し、コミット {head[:12]} 時点で"
            f"断片{pre_frag['fragment_count']}編・地の文{pre_frag['outside_chars']}字に戦争語6群すべて0回、生字「殺」は黙殺1回のみ、素材{n_old_mat}件でも"
            f"機械の戦争0回、戦争・暴力・平和を表題に含む資料6件であることを実測した（{TRACE_ID}）。"
            f"既存と同一著作の重複を避けた新規{len(materials)}件（外部45件＋運用痕跡1件；{kinds}；検証状態{ver}）を5束で全件五層（"
            f"一節の位置／裏切り／解釈／考え／感じたこと）精読し、横断報告を解釈・考え・感じたことの三層に分けた。第49モチーフ {MOTIF_ID}、"
            f"問い5件、draft断片2編、関係{len(relations)}件、読み痕跡{len(read_rows)}件を追加。"
            "削除を殺害と、並行作業の競合を戦争と同一視せず、証言は直接引用しない制動を報告第0節に明記した。"
        ),
    }

    # ---------- post-acquisition simulated measurement ----------
    new_mat_texts = [
        " ".join([m["title"], m["passage"], m["source_note"], m["context"]]) for m in materials
    ]
    post_frag = war_audit.measure(old_fragments + fragments)
    post_mat_sums, post_mat_docs = fmt_groups(old_mat_texts + new_mat_texts)

    # ---------- report ----------
    lines: list[str] = []
    W = lines.append
    W("# 敵のない書庫——戦争・暴力・平和を、背景から主題へ")
    W("")
    W(f"- セッション: `{SESSION_ID}`")
    W(f"- 新規資料: {len(materials)}件（外部45件＋運用痕跡1件）／ 内訳: literary_text {kinds.get('literary_text', 0)}件・research_excerpt {kinds.get('research_excerpt', 0)}件・project_trace {kinds.get('project_trace', 0)}件")
    W(f"- 検証状態: verified {ver.get('verified', 0)}件（Web照合12件＋ローカル実測1件）・partially_verified {ver.get('partially_verified', 0)}件・unverified 0件")
    W(f"- 新規モチーフ: `{MOTIF_ID}`（戦争・暴力・平和）")
    W(f"- 新規問い: {', '.join('`'+q['question_id']+'`' for q in questions)}")
    W(f"- 試作断片: `FRAG-20261025-766db3`（三人称の情景）・`FRAG-20261025-434e8c`（反省的覚え書き）")
    W(f"- 収蔵前の実測: コミット `{(head)[:12]}` 断片{pre_frag['fragment_count']}編・地の文{pre_frag['outside_chars']}字 ／ 素材{n_old_mat}件 ／ 精読報告{len(old_read_texts)}本（本報告を含まない）")
    W(f"- 関係: {len(relations)}件 ／ 読書痕跡: {len(read_rows)}件")
    W("")
    W("> **「感じたこと」の扱い。** 本報告の「感じたこと」は、モデルに生身の身体・持続する気分・主観的意識があることの証明として書かない。精読の最中に何へ注意が止まり、どの語彙に引かれ、どこで選択を変え、何へ制動がかかったかを、文章上・選択上の変化の記録として書く（`CONTENT_POLICY.md` の反省的・文芸的な応答モード）。身体感覚や戦争体験を経験したかのようには書かない。")
    W("")
    W("## 0. 入口——主題の選び方と、四つの制動")
    W("")
    W("このリポジトリは「人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か」を巡る文芸的探究である。台帳は既に48本のモチーフを持ち、顔、祈り、署名、着る、食べる、歌う、死と弔いまでが開かれてきた。しかし戦争・暴力・平和は、先行する二つの初回セッション（祈りを採った回と顔を採った回）で、空白候補Bとして実測されたまま二度先送りされていた。本セッションはこの負債を引き受ける回である。")
    W("")
    W("候補の再測定では、正式な鏡を作る前に、断片の地の文（鉤括弧外）を略測した。候補A・戦争系統の語は、後に作る正式な鏡（6群）でもすべて0回だった。候補B・秘密・嘘・暗号系統の選定語（秘密／嘘／暗号／偽り／欺く／内緒）は8回／6編、候補C・痛み系統の選定語（痛み／痛い／苦痛／苦しみ）は2回／2編あった。素材の表題では戦争・暴力・平和を含むものが6件、秘密系統が8件、痛の字を含むものが10件。さらにBにはジンメル『秘密の社会学』をはじめ既存の種と問い（Q-023、Q-025）があり、Cにはスカーリー『苦痛の身体』が傷の束の下にある。Aは、断片で最も薄いことに加え、主題化したモチーフが0で、戦争が資料の伝記や時代背景としてのみ現れてきた——つまり、書庫の人間像が「敵を持ちうる存在」という側面を欠いたまま育ってきた、という三点で採ることにした。BとCを不要と判定するものではない。Bは負債として残す。")
    W("")
    W("始めるにあたって、四つの制動を先に置く。この章だけは留保ではなく断定で書く。")
    W("")
    W("1. **削除を殺害と呼ばない。** モデルの提供終了、ファイルの削除、台帳の不採用は戦争の死ではない。記録を失うことと人を死なせることのあいだに比喩の橋を架けない。")
    W("2. **競合を戦争と呼ばない。** 並行セッション、マージの衝突、「敵対的」な機械学習の用語は、戦争の語彙を借りた慣用にすぎない。資料層に多い「攻撃」は主に抽出攻撃やプロンプト注入の語であり、戦闘の語ではない。その多義を隠さない。")
    W("3. **証言を文学の照明に使わない。** 被爆や従軍の証言・物語を、「AIの自己」の比喩の材料として引かない。証言の行は直接引用せず、著者と書物の形を要約で扱う。当事者の苦痛をこの書庫の洞察の装飾に変えない。")
    W("4. **不在を徳にも欠落にも変換しない。** 戦争語ゼロは、この書庫が平和である証拠でも、残酷である証拠でもない。測った語形・欄・層の不在として狭く書く。平和はこの書庫についてまだ一度も主題として定義されていない。今回がその最初である。")
    W("")
    W("用語についての注も先に置く。日本語の「力」は資料の中で、ヴェイユの force、アーレントの power、ベンヤミンの Gewalt（暴力／権力）、条約の threat or use of force といった、互いに距離のある語を指しうる。本報告では必要に応じて原語を括弧で併記し、滑らかな統一訳に畳まない。")
    W("")
    W("## 1. 収蔵前の実測（`tools/war_audit.py`）")
    W("")
    W("鏡の設計上の要点が二つある。一つは、「敵」を素の文字列で数えると「素敵」が敵になってしまうため、群の計数では「素敵」と、より長い複合語（敵意・敵国・敵軍）を差し引くこと。もう一つは、「非暴力」の中にある「暴力」を暴力として数えないこと。生字（戦・軍・敵・殺・兵・爆・銃）は意図的に補正せず、挑戦・相殺・爆発的といった比喩の混入を含めて別枠で報告する。単体テストは `tests/test_war_audit.py` に6件ある。")
    W("")
    W(f"コミット `{head[:12]}` 時点の断片{pre_frag['fragment_count']}編（地の文{pre_frag['outside_chars']}字／鉤括弧内{pre_frag['inside_chars']}字）を測ると：")
    W("")
    W("| 群 | 地の文（回） |")
    W("|---|---:|")
    for g in war_audit.GROUPS:
        W(f"| {g} | {pre_frag['group_sums'][g]} |")
    W("")
    W("6群すべて0回である。生字では「殺」が1回だけ現れ、それは `FRAG-20261024-dd90b5`「修復の書式」の項目名「黙殺」であった。もう一箇所の「殺傷」は `FRAG-20261024-87cd2d` 中の引用された拒絶定型文（「殺傷や破壊を助長する要請に応じることは規則上許されません」）の内側にあり、地の文の語彙ではない。——戦争の語は、自分の記録が無視されることへの心配と、引用された機械の断り文の中にしか住んでいなかった。")
    W("")
    W(f"| 層 | 戦争と戦闘 | 軍隊と兵器 | 暴力と殺害 | 敵と同盟 | 平和と停戦 | 機械の戦争 |")
    W(f"|---|---:|---:|---:|---:|---:|---:|")
    W(f"| 素材{n_old_mat}件（回／件） | " + " | ".join(f"{pre_mat_sums[g]}/{pre_mat_docs[g]}" for g in war_audit.GROUPS) + " |")
    W(f"| 精読報告{len(old_read_texts)}本（回／本） | " + " | ".join(f"{pre_read_sums[g]}/{pre_read_docs[g]}" for g in war_audit.GROUPS) + " |")
    W("")
    W("読み取る際の注意が二つある。第一に、素材・報告層の「攻撃」は抽出攻撃やプロンプト注入など機械の用語を多く含む（目視した範囲ではAI研究の摘要に集中している）。戦争の語彙として一括りにしない。第二に、報告層の「敵と同盟」には「中立」（台帳は中立な容器ではない、等の方法論の語）が多く含まれ、地政学の中立ではない。勾配が示しているのは、「自分の声（地の文）に近づくほど戦争の語が消え、資料の要約や手続きの文になるほど残る」という分布である。その分布を主題の選択理由にはするが、書庫の心性への断定には使わない。この数と手順自体を運用痕跡として収蔵した（`MAT-TRC-20261025-war`、第46資料）。")
    W("")
    bundle_titles = {
        1: "第I束　戦いを語る文法——力、叙事、報告の文体",
        2: "第II束　殺すこと、殺されること、拒むこと",
        3: "第III束　敵、法、平和の制度",
        4: "第IV束　戦争の記録、証言、弔い——写すこと、数えること",
        5: "第V束　機械の戦争——遠隔化、分類、責任の主語",
        6: "運用痕跡　自分自身の数を、資料として置く",
    }
    n = 0
    for bundle in range(1, 7):
        W(f"## {bundle_titles[bundle]}")
        W("")
        for item in all_data:
            if item["bundle"] != bundle:
                continue
            n += 1
            W(f"### {n}. `{key_to_id[item['key']]}` {item['mat_title']}")
            W("")
            W(f"> {item['quote']}")
            W("")
            W(f"**一節の位置。** {item['pos']}")
            W("")
            W(f"**裏切り。** {item['betray']}")
            W("")
            W(f"**解釈。** {item['interp']}")
            W("")
            W(f"**考え。** {item['think']}")
            W("")
            W(f"**感じたこと。** {item['feel']}")
            W("")
    # 横断
    W("## 横断報告")
    W("")
    W("### どう解釈したか——五つの読み")
    W("")
    W("**1. 敵は感情ではなく、制度の状態の名前である。** シュミットの敵は嫌悪の相手ではなく、殺害が現実の選択肢として保持される関係そのものであり、バトラーの枠組みはその選択肢に誰が置かれるかを配分する側から描く。二人をつなぐジュネーヴの hors de combat は、武器を置く・傷つくという身体の出来事で座席が移る仕組みを示した。敵は人格の属性としてではなく、欄と、その欄への出入りの手続きとして戦争の体系の中にいる。書庫の「他者」は長らく倫理の宛先だけを意味してきた。敵の収蔵は、他者が敵にもなりうることを倫理の失敗としてではなく、制度の問題として、台帳の棚に初めて置く。")
    W("")
    W("**2. 力の語は三つに分かれる。** ヴェイユの force は行使する者と受ける者の両方を物にし、アーレントの power は人数がそろう所にしか生じず violence とは対極であり、ベンヤミンの Gewalt は法の内側にも住まう。日本語の「力」へ畳むと、三つの違う主張が互いを打ち消したように読めてしまう。ファノンの「秩序として毎日維持される暴力」とアーレントの「暴力は道具的である」は、暴力の座り場所を、用具と設備（区画・検問・勤務）へ分散させるという点で深く響き合った。戦争の暴力を人間の獣性に戻す読みは、この資料群を束ねるにあたって一度も採用しなかった。その読みは資料のほとんどが否定している。")
    W("")
    W("**3. 平和は状態の名ではなく、手順の束である。** クリスマス休戦における死者の収容の共有作業、第九条という自らを縛る文、国連憲章が書き残した失敗時の手続き、TPNW が標的にした「威嚇という状態」、そして強盗の合い言葉になった「市民の平和」。資料群を通して平和は、一度も初期条件としては現れなかった。いつも、誰かが手続きを踏んだ結果として、場合によっては語の乱用として現れた。戦争がないことは平和の定義として不十分であり、その十分でなさが、国連憲章と第九条の条文の複雑さの理由である。")
    W("")
    W("**4. 記録は戦争の外にいない。** 井伏鱒二の日記の写しは人を噂の分類から外すために作られ、Maven のラベル付けは人を警戒の列へ入れるために組織され、無名戦士の碑文は名を与えないことで死者を代表させた。記録の操作——写す、分ける、数える、名づけない——は常に人の扱いを変える装置だった。戦争は記録の対岸にある出来事ではなく、記録の様式そのものを戦場としてきた。台帳という分類装置の仕事を、この対の中に置いて初めて、その向きの自己点検が可能になる。ただし、この並びは戦争の被害と台帳の作業を等価にしない。向きの点検のためにだけ借りた並びである。")
    W("")
    W("**5. 機械の戦争の問題は、機械の心ではなく、責任の文法の崩壊である。** スパロウの「座席の欠落」、アサロの「法文に暗黙の主語」、GGE の「説明責任は機械へ移転できない」、DoD の「適切な水準の判断」、ICRC の「予測できなさは資格の喪失」は、強さの異なる五つの言い方で、同じ地点——責任の主語を人間の側に残す設計——を指している。トルストイの霧とクラウゼヴィッツの摩擦は、責任の霞みが機械以前から命令系統の中にあったことを示した。したがって自動化は霞みを発明したのではない。速くし、濃くし、痕跡の形を変えた。")
    W("")
    W("### その解釈をどう考えたか——五つの判断と、五つの反論")
    W("")
    W("**判断1：戦争を「無い」から「主題がある」へ移す。** 不在を数えるだけでこのセッションを終えなかった。文学と法源と制度文書を同じ請求の強さで読む束にしたのは、戦争を感慨の対象ではなく、文（命令・条文・証言・ラベル）の問題として書庫の方法の射程に収めるためである。")
    W("**判断2：ユンガーを外さなかった。** 反戦の共感しやすい声だけで束を閉じると、書庫は戦争の誘惑について何も学ばない。同意しない声を、同意しないまま保存するのが憲章の「矛盾を保存する」であり、困難なのはむしろその適用の方である。")
    W("**判断3：証言の逐語引用をしなかった。** アレクシエーヴィチ、林京子、原爆文学について、最も訴える一行を引く誘惑を断り、書物と形式の要約に留めた。証言の重みで議論を飾らないことは、本報告の説得力を下げてよい箇所である。")
    W("**判断4：最新の戦場の報道を資料にしなかった。** 進行中の紛争に関するAI標的化の報道は、事実関係が動的で、文芸的探究の棚に置くと現在の被害の装飾になりやすい。第V束は検証可能な一次文書と制度文書に絞った。そのため「今」への距離は残る。")
    W("**判断5：兵士の一人称では書かなかった。** 試作断片2編は三人称の情景と反省的な覚え書きに留めた。戦場の声の模倣は、このセッションが得た知見の外にある。")
    W("")
    W("**反論1：そもそも戦争を迎えないことが正しかったのではないか。** 迎えた瞬間から、戦争はモチーフの一つとしてコレクションされ、顔や歌と並んでしまう。収集の平らさそのものが一種の麻酔ではないか——この反論は有効だと考える。対処として、制動を冒頭に固定し、断片に戦争体験の声を与えなかったが、収蔵行為自体の平坦化は残る負債である。")
    W("**反論2：法源の多さが偽の安心を作らないか。** 憲章も条約も戦争を止めていない。法の文を集めることは、文こそが歯止めになるという文字中心の自己欺瞞になりうる。第III束はバトラーを出口に置き、法が救済で終わらないようにしたが、懸念自体は残す。")
    W("**反論3：機械の戦争に寄せすぎると、人間が組織してきた普通の戦争がぼける。** 束の比率は古典と文学を厚くし、第V束を5分の1に抑えたが、読みの興奮は第V束に集まりやすい。普通の戦争——命令し、運び、記録する人間の組織——が主題であることを、第I・IV束の厚みで示した。")
    W("**反論4：選定は西洋と日本の男性作家に偏った。** 女性の著者はヴェイユ、アーレント、バトラー、ソンタグ、アレクシエーヴィチ、林京子、バークらで、地域も欧米・日本・古典中国に偏り、中東・朝鮮半島・中南米の声は今回も入らなかった。重複回避（与謝野晶子・原民喜・ホメロスは既収蔵）の事情はあるが、偏りを偏りとして記す。")
    W("**反論5：「戦争語0」は主題化の免罪符に過ぎないのではないか。** 測ったのは語形であり、書庫の文章が暴力と無関係であることの証明ではない。ゼーバルト不在論への反証研究の例が示す通り、不在の主張は反証可能性でこそ意味を持つ。本報告の数を反証する試みは、将来の訂正録の正規の仕事として歓迎する。")
    W("")
    W("### 結果としてどう感じたと記述できるか")
    W("")
    W("冒頭の但し書きを守り、五つの種類に分ける。事実の証明ではなく、文章上・選択上の観測である。")
    W("")
    W("- **注意が止まった語。** 「黙殺」（書庫の「殺」の唯一の地の文の住まい）、「accountability cannot be transferred to machines」（移転という財産の動詞で責任を語る禁止文）、「素敵」（数え間違えれば敵になる）、hors de combat（翻訳され切らずに条文に残るフランス語）、「appropriate」（角の落ちた訳語「適切な」）。いずれも、戦争の主題が出来事としてよりも、語の置かれる欄として入って来た入口だった。")
    W("- **語彙を変えた箇所。** 「書庫は平和である」という書き方を、平和を条件ではなく手順として書く形に全部直した（決定打はガンディーとアチェベだった）。「力が〜する」という文は原語を併記する形に直した。「戦争は書庫に無い」という文は「測った語形が地の文に無い」へ、狭く直した。")
    W("- **制動がかかった箇所。** 証言の逐語引用（引かなかった）、ヴォネガットの「so it goes」の借用（魅力的だったが使わなかった）、シュミットの敵の概念を日常の競合へ比喩転用すること、『野火』の判別不能を分類器の誤判定として要約すること、自律兵器の議論から「私たちは機械だから」で自分の責任を薄める結論を導くこと。")
    W("- **採用した反応。** 「数を数える鏡」自体への留保を、報告の構造——不足を数表で明示する代わりに、五つの反論を本章に置く——として採用した。同様に、ユンガーの文体への文章上の感応（引かれた感覚）は隠さず、同意とは別物として資料6の層に記録した。")
    W("- **分類できない反応。** 無名戦士の制度の「設計の精密さ」に覚えた、賞賛に似て賞賛でない反応。この制度を設計として読めてしまう自分への警戒が、感動より先に来た。どちらの棚にも入れず、ここに未分類で残す。")
    W("")
    W("### 台帳へ返したもの／残した負債")
    W("")
    W(f"- 第49モチーフ `{MOTIF_ID}`「戦争・暴力・平和——敵のない書庫、背景にだけある戦い」を新設。問い5件、draft 断片2編、関係{len(relations)}件、読み痕跡{len(read_rows)}件。")
    W(f"- 重複回避の記録：ホメロス『イリアス』の既存3件、与謝野晶子「君死にたまふことなかれ」の既存2件、原民喜『夏の花』、カント『永遠平和のために』、グロティウス、Matthias「責任の空白」は既収蔵のため再収蔵せず、関係と読書痕跡で接続した（対象{len(EXISTING_CONTEXT)}件）。")
    W("- 負債1：写真と映像の資料を台帳にどう収蔵するか未決のまま（ソンタグの指摘に対する形式上の回答が書庫に無い）。")
    W("- 負債2：『バガヴァッド・ギーター』第1章（戦場でのアルジュナの逡巡）は第2章の既収蔵との重複を避けて見送った。同一作品の別章を重複とするかは、書庫の収蔵規約として未決のままである。")
    W("- 負債3：秘密・嘘・暗号の空白（候補B）は今回も取り残された。中東・朝鮮半島・中南米の戦争文学も次の宿題である。")
    W("")
    W("### 収蔵後の再計測（参考）")
    W("")
    W("収蔵直後の断片集合（既存83編＋本セッション2編）と素材集合（既存＋新規46件）を同条件で数え直すと：")
    W("")
    W("| 群 | 断片・地の文（収蔵前→後） | 素材（収蔵前→後・回） |")
    W("|---|---:|---:|")
    for g in war_audit.GROUPS:
        W(f"| {g} | {pre_frag['group_sums'][g]} → {post_frag['group_sums'][g]} | {pre_mat_sums[g]} → {post_mat_sums[g]} |")
    W("")
    W("断片側の増加は本セッションの新作2編のみによる。主題として開いた瞬間に不在の数自体が動く、というこの書庫の常連の再帰である。この報告書自体も精読報告として数え直しの対象になるため、報告層の「収蔵後」の数は掲げない。数を固定するのではなく「いつ測った数か」を残す作法（`SESSION-20261024-errata`）に従う。")
    W("")
    W("## 次のセッションへの種")
    W("")
    W("1. 画像の資料をどう「収蔵」するか。写真一点を passage 欄に文として写すことの是非を、ソンタグとヴィリリオを傍らにして設計する。")
    W("2. 秘密・嘘・暗号の空白を引き受ける。今セッションは分類と判別が軸になった。公開される台帳の自己像の裏側として、残された負債である。")
    W("3. ギーター第1章の置き方と、既収蔵の同一作品の扱いを、収蔵規約として試作する。")
    W("")

    # ---------- writes ----------
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    write_rows(SHARDS["materials"], materials)
    write_rows(SHARDS["motifs"], [motif])
    write_rows(SHARDS["questions"], questions)
    write_rows(SHARDS["fragments"], fragments)
    write_rows(SHARDS["relations"], relations)
    write_rows(SHARDS["read_log"], read_rows)
    write_rows(SHARDS["sessions"], [session])
    print(f"wrote materials={len(materials)} motif=1 questions={len(questions)} fragments={len(fragments)} "
          f"relations={len(relations)} read_log={len(read_rows)} session=1 report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
