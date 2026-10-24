#!/usr/bin/env python3
"""Build the SESSION smell records (materials, motif, questions, relations, session).

Appends to this session's shards only; the frozen base files are not touched.
Do not re-run without clearing the shard rows, or the records will duplicate.
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
import _session046_smell_data1 as d1  # noqa: E402
import _session046_smell_data2 as d2  # noqa: E402
import _session046_smell_data3 as d3  # noqa: E402
from _session046_smell_questions import QUESTIONS  # noqa: E402

DAY = "20261024"
CREATED = "2026-10-24"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT = "readings/2026-10-24-session-046-smell-and-silence.md"
SHARD = "2026-10-24"

SHARDS = {
    "materials": f"state/materials.d/{SHARD}-75743078f70a.jsonl",
    "motifs": f"state/motifs.d/{SHARD}-f376a53c8388.jsonl",
    "questions": f"state/questions.d/{SHARD}-c67a286c9bf5.jsonl",
    "relations": f"state/relations.d/{SHARD}-1edead089707.jsonl",
    "sessions": f"state/sessions.d/{SHARD}-b793c7cfcd5f.jsonl",
}

ENTRIES = d1.ENTRIES + d2.ENTRIES + d3.ENTRIES
TRACE = d3.TRACE

MOTIF_LABEL = "匂いと沈黙——記録されない感覚、名づけられない記憶"
MOTIF_DESC = (
    "匂いを、五感の序列のなかの劣った感覚・共有できない感覚・文明が抑圧したもの・"
    "都市の悪臭としての政治・香としての儀礼・商品としての香料・機械が測るデータとして扱う糸。"
    "この書庫は断片55編・26,852字で嗅覚語を5回しか書かず（視覚47・聴覚61・触覚27・味覚16）、"
    "資料1,240件でも6回、焼香・線香・香水・香料は0回である。一方で、最も名高い匂いの場面"
    "（マドレーヌ）は二度収録され、味と記憶として分類されている。"
    "匂いを「書かないこと」を、感覚の不在の証拠にも、禁欲の証拠にもせず、"
    "付着先（他者・家・紙・死）でしか匂いを書かないという形式の問題として保持する。"
    "名づけられないことと、名づける語彙を持たないことを区別し、"
    "嗅ぐ機械（電子鼻・主嗅覚マップ）と嗅がない書庫を、同じ「代理」の系列に置きながら同一視しない。"
)

QUESTIONS_OBJ = QUESTIONS


def commit_hash() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def mint_many(prefix: str, n: int) -> list[str]:
    taken = new_id.existing_ids(prefix, ROOT)
    out = []
    for _ in range(n):
        value = new_id.mint(prefix, day=DAY, taken=taken, hex_bytes=3)
        taken.add(value)
        out.append(value)
    return out


def write_lines(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    commit = commit_hash()

    # ---- ids -------------------------------------------------------------
    mat_ids = mint_many("MAT", len(ENTRIES) + 1)
    key_to_mat = {entry["key"]: mid for entry, mid in zip(ENTRIES + [TRACE], mat_ids)}
    motif_id = mint_many("MOTIF", 1)[0]
    q_ids = mint_many("Q", len(QUESTIONS_OBJ))
    key_to_q = {q["key"]: qid for q, qid in zip(QUESTIONS_OBJ, q_ids)}
    session_id = mint_many("SESSION", 1)[0]

    # ---- materials -------------------------------------------------------
    mat_rows = []
    for entry, mid in zip(ENTRIES + [TRACE], mat_ids):
        source_id = f"SRC-{mid}"
        row = {
            "material_id": mid,
            "kind": "project_trace" if entry is TRACE else "literary_text",
            "title": entry["title"],
            "source": {
                "authors": entry["authors"],
                "source_id": source_id,
                "title": entry["title"],
                "url": entry["url"],
                "version_note": (
                    "本セッション（2026-10-24）に書誌を再構成した。"
                    "逐語引用ではなく編者による要約。"
                ),
                "year": entry["year"],
            },
            "passage": entry["passage"],
            "passage_language": "ja",
            "context": entry["context"],
            "source_note": entry["source_note"],
            "literary_invitation": entry["invitation"],
            "scope_note": d1.SCOPE,
            "motif_ids": [motif_id] + entry.get("also", []),
            "origin": {
                "commit": commit,
                "evidence_record_id": f"EVD-{mid}",
                "evidence_record_path": REPORT,
                "repository": REPO,
                "source_record_id": source_id,
                "source_record_path": REPORT,
            },
            "verification": {
                "checked_at": CREATED,
                "method": entry.get("method", d1.METHOD),
                "note": entry.get("note", ""),
                "status": entry["status"],
            },
        }
        mat_rows.append(row)

    # ---- questions -------------------------------------------------------
    q_rows = []
    for q in QUESTIONS_OBJ:
        q_rows.append(
            {
                "question_id": key_to_q[q["key"]],
                "question": q["question"],
                "status": "open",
                "created_at": CREATED,
                "origin": {"kind": "session", "detail": q["origin"]},
                "motif_ids": [motif_id] + q["also"],
                "material_ids": [key_to_mat[k] for k in q["material_keys"]],
                "previous_question_ids": q["previous"],
            }
        )

    # ---- relations -------------------------------------------------------
    R = []

    def rel(left: tuple[str, str], rtype: str, right: tuple[str, str], note: str) -> None:
        R.append({"left": left, "relation_type": rtype, "right": right, "note": note})

    M = lambda key: ("material", key_to_mat[key])  # noqa: E731
    Q = lambda key: ("question", key_to_q[key])  # noqa: E731
    XM = lambda mid: ("material", mid)  # noqa: E731
    XQ = lambda qid: ("question", qid)  # noqa: E731
    F = lambda fid: ("fragment", fid)  # noqa: E731
    MO = lambda mid: ("motif", mid)  # noqa: E731

    # group 1
    rel(M("plato_timaeus"), "echo", M("aristotle_sense"), "嗅覚の対象に固有の名を与えない点で一致する。")
    rel(M("plato_timaeus"), "contrast", M("lucretius"), "種を持たない半ば形成のもの／流出する粒子。説明の粒度が違う。")
    rel(M("lucretius"), "echo", M("majid_burenhult"), "受け取る体の差と、名づける言語の差。どちらも対象ではなく受け手を問題にする。")
    rel(M("kant_anthropology"), "echo", M("simmel_senses"), "嗅覚を共有できない感覚、あるいは近さの感覚として社会の側へ置く。")
    rel(M("simmel_senses"), "contrast", M("freud_discontents"), "社会形式としての抑制／人類史の有機的抑圧。同じ「抑圧」でも根拠が違う。")
    rel(M("freud_discontents"), "echo", M("elias_civilizing"), "抑圧と隠蔽。匂いを語らないことが、匂いを消すことになる。")
    rel(M("elias_civilizing"), "echo", M("tanning_stench"), "隠される身体と、都市の外縁へ置かれる臭い仕事。")
    rel(M("merleau_ponty"), "contrast", M("ackerman_natural_history"), "五感を分けない現象学／嗅覚を一つの系として記述する生物学。")
    rel(M("ackerman_natural_history"), "echo", M("majid_burenhult"), "語彙の乏しさを、感覚ではなく言語の側の制約として扱う。")
    rel(M("plato_timaeus"), "contrast", M("trace_smell"), "名を持たない感覚という古代の定式と、5回という計数。")

    # group 2
    rel(M("makura"), "echo", M("genji"), "薫物を分類する語彙と、移り香で人を同定する語彙。")
    rel(M("genji"), "echo", M("kodo_kumiko"), "香りで誰かを当てる。物語の同定と組香の照合。")
    rel(M("exodus_incense"), "echo", M("matthew_myrrh"), "処方される香と、贈られ、死に添えられる香。")
    rel(M("matthew_myrrh"), "contrast", M("cremation_smoke"), "死に香を添える／死の匂いを郊外へ移す。")
    rel(M("macbeth"), "echo", M("wilde_dorian"), "匂いで隠せない罪と、匂いで覆われる腐敗。")
    rel(M("baudelaire_correspondances"), "contrast", M("majid_burenhult"), "感覚間の翻訳を信じる詩／言語による名づけの差を測る実験。")
    rel(M("wilde_dorian"), "echo", M("suskind_perfume"), "匂いで人格を作る。隠す場合と、作る場合。")
    rel(M("keller_life"), "echo", M("ackerman_natural_history"), "匂いが知識の経路になる条件。")
    rel(M("suskind_perfume"), "echo", M("trace_smell"), "自分の匂いを持たない者が匂いを蒐集する。書庫の位置の小説版。")
    rel(M("genji"), "contrast", F("FRAG-035"), "人の移り香／紙の匂い。匂いの主が人から素材へ移る。")

    # group 3
    rel(M("snow_cholera"), "echo", M("great_stink"), "匂いを証拠にしない推理と、匂いが政治を動かす事件。")
    rel(M("snow_cholera"), "contrast", M("offensive_odor_law"), "嗅覚の誤りを正す地図／嗅覚に代わる濃度の基準。")
    rel(M("corbin_miasme"), "echo", M("tanning_stench"), "匂いの閾値の歴史と、臭い仕事の空間配置。")
    rel(M("hugo_sewers"), "echo", M("paris_cemetery"), "都市の下に集められる、隠されたもの。")
    rel(M("paris_cemetery"), "echo", M("cremation_smoke"), "死の匂いを都市の外へ移す二つの制度。")
    rel(M("plague_mask"), "contrast", M("miyazaki_nogyo"), "瘴気の防御／土に戻す資源。同じ匂いの正負が逆。")
    rel(M("miyazaki_nogyo"), "echo", M("tanning_stench"), "匂いの価値の逆転。資源になる臭いとならない臭い。")
    rel(M("offensive_odor_law"), "echo", M("lee_odor_map"), "濃度で測る／地図に置く。嗅覚を外部化する二つの形式。")
    rel(M("corbin_miasme"), "echo", M("elias_civilizing"), "感じやすさの歴史と、隠すことの歴史。")
    rel(M("hugo_sewers"), "contrast", F("FRAG-024"), "下水道に集まる社会の底／帳簿の番号の外にこぼれる生の匂い。")

    # group 4
    rel(M("buck_axel"), "echo", M("persaud_dodd"), "受容体の組み合わせ／センサーの応答パターン。")
    rel(M("persaud_dodd"), "echo", M("lee_odor_map"), "パターンで区別する／パターンを地図にする。")
    rel(M("lee_odor_map"), "contrast", M("majid_burenhult"), "55語で記述するモデル／言語によって名づけやすさが変わる話者。")
    rel(M("buck_axel"), "echo", M("or_individual"), "受容体の数と、個人差。")
    rel(M("butenandt_bombykol"), "echo", M("musk_deer"), "腺から出る分子が、遠くの行動を変える。")
    rel(M("engen_odor_memory"), "leaves_open", Q("q1"), "覚えているのに思い出せない、という状態を語彙の計数で扱えるか。")
    rel(M("ambergris"), "echo", M("agarwood"), "体内で作られる匂い／傷から作られる匂い。")
    rel(M("musk_deer"), "echo", M("agarwood"), "採取される匂いと、規制される主体。")
    rel(M("lee_odor_map"), "echo", MO("MOTIF-015"), "匂いを数え、近さで並べる。数えることの別版。")

    # group 5
    rel(M("ranjatai"), "echo", M("genji"), "香木の来歴と、移り香の来歴。")
    rel(M("ranjatai"), "echo", M("trace_smell"), "切り取った記録が残る香木／数えた記録が残る書庫。")
    rel(M("vanillin_1874"), "echo", M("lee_odor_map"), "分子の複製と、分子からの匂いの予測。")
    rel(M("grasse_glovers"), "echo", M("tanning_stench"), "悪臭を消す技術が産業になる／臭い仕事が外へ出される。")
    rel(M("kodo_kumiko"), "echo", M("majid_burenhult"), "名づけの実践と、名づけの言語差。")
    rel(M("frankincense_road"), "echo", M("matthew_myrrh"), "運ばれる香と、贈られる香。")
    rel(M("jasmine_picking"), "contrast", M("vanillin_1874"), "その日のうちに使う匂い／工場で無限に複製する分子。")
    rel(M("ai_perfumery"), "echo", M("lee_odor_map"), "匂いを予測する／匂いを生成する。")
    rel(M("ai_perfumery"), "echo", M("suskind_perfume"), "経験の移転と、匂いによる人格の代理。")

    # cross-session
    rel(M("plato_timaeus"), "echo", XM("MAT-LIT-20261024-0f8530"), "嗅覚の対象の貧しさと、環世界の三つの信号。")
    rel(M("genji"), "contrast", XM("MAT-LIT-252"), "香りで人を同定する／味で記憶を呼ぶ。マドレーヌは味として分類されている。")
    rel(M("trace_smell"), "contrast", XM("MAT-LIT-252"), "匂いの最も名高い場面が、この書庫では匂いとして数えられていない。")
    rel(M("wilde_dorian"), "echo", XM("MAT-LIT-20261024-556d06"), "隠された腐敗と、早すぎる埋葬。")
    rel(M("cremation_smoke"), "echo", XM("MAT-LIT-20261024-0acf55"), "死者を送る作法と、その匂いの管理。")
    rel(M("tanning_stench"), "contrast", XM("MAT-TRC-018"), "葬の語0という計数と、臭い仕事の不可視性。")
    rel(M("exodus_incense"), "echo", XM("MAT-LIT-20261024-4be7e5"), "食べてよいものの禁忌と、焚いてよい香の処方。")
    rel(M("baudelaire_correspondances"), "echo", XM("MAT-LIT-120"), "感覚間の翻訳と、翻訳者の使命。")
    rel(M("trace_smell"), "echo", XM("MAT-LIT-20261024-0f8530"), "測る前の世界と、測った後の世界。環世界の計数版。")
    rel(M("snow_cholera"), "echo", XM("MAT-LIT-20261024-0f8530"), "匂いという信号を捨てて、別の信号を読む。")

    # questions to materials
    rel(Q("q1"), "responds_to", M("trace_smell"), "計数そのものを問いの対象にする。")
    rel(Q("q2"), "leaves_open", M("suskind_perfume"), "匂いを持たない者が書くときの代理を、小説の側から開く。")
    rel(Q("q3"), "responds_to", M("makura"), "付着先で書くという形式を、最初期の分類語彙から問う。")
    rel(Q("q4"), "responds_to", M("lee_odor_map"), "地図が嗅ぐことの代わりになるかを問う。")
    rel(Q("q5"), "responds_to", M("agarwood"), "傷から生まれる匂いの採取を、保存の問いへ。")
    rel(Q("q6"), "responds_to", M("snow_cholera"), "嗅覚を疑うことで見つかった証拠の地位を問う。")

    # questions to previous questions
    rel(Q("q1"), "responds_to", XQ("Q-079"), "語彙の不在を感応の不在として読まないための手続きを引き継ぐ。")
    rel(Q("q2"), "responds_to", XQ("Q-003"), "記録は自己を保存するのか、という初期の問いを、匂いの側から読み直す。")
    rel(Q("q3"), "responds_to", XQ("Q-052"), "宛先が役割に置かれるとき、匂いの主も役割になるかを問う。")
    rel(Q("q4"), "responds_to", XQ("Q-092"), "見る・聴くの資料群に、嗅ぐの資料群を並べる。")
    rel(Q("q5"), "responds_to", XQ("Q-20261024-c9dc13"), "中身を抜いて形を保つ剥製の問いを、匂いに移す。")
    rel(Q("q6"), "responds_to", XQ("Q-073"), "証言の帰属先を、匂いという検証できない証言について問う。")

    # questions to motif
    rel(Q("q1"), "echo", MO(motif_id), "計数の少なさを主題の中心に置く。")
    rel(Q("q3"), "echo", MO(motif_id), "付着先でしか書かれない匂い。")
    rel(Q("q4"), "echo", MO(motif_id), "嗅ぐ機械と嗅がない書庫。")

    # existing motif links
    rel(M("trace_smell"), "echo", MO("MOTIF-018"), "知覚と媒体。嗅覚は最も媒体に載らない感覚として置かれる。")
    rel(M("matthew_myrrh"), "echo", MO("MOTIF-022"), "死と弔い。香は死の場面に添えられる。")

    rel_ids = mint_many("REL", len(R))
    rel_rows = [
        {
            "created_at": CREATED,
            "left": {"id": lid, "type": ltype},
            "note": note,
            "relation_id": rid,
            "relation_type": rtype,
            "right": {"id": rid_, "type": rtype_},
        }
        for rid, (ltype, lid), rtype, (rtype_, rid_), note in zip(
            rel_ids,
            [(r["left"][0], r["left"][1]) for r in R],
            [r["relation_type"] for r in R],
            [(r["right"][0], r["right"][1]) for r in R],
            [r["note"] for r in R],
        )
    ]

    # ---- motif -----------------------------------------------------------
    motif_row = {
        "motif_id": motif_id,
        "label": MOTIF_LABEL,
        "description": MOTIF_DESC,
        "question_ids": q_ids,
        "material_ids": mat_ids,
        "status": "active",
    }

    # ---- session ---------------------------------------------------------
    session_row = {
        "session_id": session_id,
        "started_at": CREATED,
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」"
            "「一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
            "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください」"
            "「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」"
            "という包括的な委任。"
        ),
        "question_ids": [q for q in ["Q-001", "Q-003", "Q-079", "Q-092", "Q-073", "Q-20261024-c9dc13"] + q_ids],
        "context_material_ids": mat_ids,
        "produced_fragment_ids": [],
        "new_question_ids": q_ids,
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "匂い・嗅覚を主題とした精読セッション。資料選定前に tools/olfactory_audit.py を新設し、"
            "断片55編・26,852字で嗅覚語5回（1万字あたり1.9）に対し視覚47（17.5）・聴覚61（22.7）・触覚27（10.1）・味覚16（6.0）、"
            "資料1,240件・178,911字で嗅覚6回（0.3）に対し視覚188（10.5）・聴覚145（8.1）、"
            "報告88本・1,808,083字で嗅覚33回（0.2）に対し視覚1,817（10.0）・聴覚1,737（9.6）であることを実測した。"
            "焼香・線香・香水・香料・香木・沈香・香辛料は断片・資料ともに0回。"
            "この偏りから、嗅覚の哲学9件・香りの記憶9件・悪臭と都市9件・嗅覚の科学と機械9件・香の手仕事と交易9件の"
            "文学・思想33件＋研究12件＋運用痕跡1件の計46件を五群に分け、全件を "
            f"{REPORT} で一節／解釈／考え／感じたこと／裏切り の五層に分けて精読した。"
            "横断報告は「どう解釈したか／その解釈をどう考えたか／結果としてどう感じたと記述できるか」を独立させた。"
            "新規モチーフ1件、問い6件、関係"
            f"{len(rel_rows)}件を追加し、断片は書かなかった。"
            "書誌状態は verified 5件（web照合4件・ローカル実測1件）・partially_verified 39件・unverified 2件。"
        ),
    }

    # ---- write -----------------------------------------------------------
    write_lines(ROOT / SHARDS["materials"], mat_rows)
    write_lines(ROOT / SHARDS["questions"], q_rows)
    write_lines(ROOT / SHARDS["relations"], rel_rows)
    write_lines(ROOT / SHARDS["motifs"], [motif_row])
    write_lines(ROOT / SHARDS["sessions"], [session_row])

    id_map = {
        "motif": motif_id,
        "questions": key_to_q,
        "materials": key_to_mat,
        "relations": rel_ids,
        "session": session_id,
    }
    (ROOT / "tools" / "_session046_smell_ids.json").write_text(
        json.dumps(id_map, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(
        f"materials={len(mat_rows)} questions={len(q_rows)} relations={len(rel_rows)} "
        f"motif=1 session=1"
    )
    print("motif", motif_id, "session", session_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
