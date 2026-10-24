#!/usr/bin/env python3
"""Deterministic shard/report builder for SESSION-20261024-abject (Session 063).

41 external materials + 1 project trace; one motif, four questions, two draft
fragments. Emits append-only shards under state/*.d/2026-10-24-b7e21c9d4f03.jsonl.
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
import abjection_audit  # noqa: E402
from _session063_abjection_data1 import ITEMS_PART1  # noqa: E402
from _session063_abjection_data2 import ITEMS_PART2  # noqa: E402

SESSION_ID = "SESSION-20261024-abject"
SHARD_STEM = "2026-10-24-b7e21c9d4f03"
CREATED_AT = "2026-10-24"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-24-session-063-abjection-and-the-residue.md"
TRACE_ID = "MAT-TRC-20261024-abject"
MOTIF_ID = "MOTIF-20261024-5d1c73"
Q_IDS = [
    "Q-20261024-0b7e14",
    "Q-20261024-3c8a52",
    "Q-20261024-9f2d06",
    "Q-20261024-c41b8e",
]
FRAG_IDS = ["FRAG-20261024-7e3d10", "FRAG-20261024-b2f486"]
ITEMS = ITEMS_PART1 + ITEMS_PART2

CLUSTER_TITLES: dict[int, str] = {
    1: "第I束　腐敗する身体——土に返る、屑を拾う、糞をする",
    2: "第II束　制度としての穢れ——叫ぶ者、流す神、洗う水",
    3: "第III束　排出の思想——肛門・異質・ゼロ価値・反動形成",
    4: "第IV束　インフラとしての排出——下水・肥・ファットバーグ",
    5: "第V束　機械の排出——拒否・重複・崩壊・警告",
}

CLUSTER_MOTIFS: dict[int, list[str]] = {
    1: ["MOTIF-20261024-4b87ac", "MOTIF-20261024-e6bca7", "MOTIF-20261024-71b589"],
    2: ["MOTIF-20261024-e6bca7", "MOTIF-011", "MOTIF-20261024-146017"],
    3: ["MOTIF-20261024-71b589", "MOTIF-20261024-504a22", "MOTIF-011"],
    4: ["MOTIF-20261024-80516e", "MOTIF-20261024-14d5df", "MOTIF-015"],
    5: ["MOTIF-20261024-504a22", "MOTIF-20261024-14d5df", "MOTIF-015"],
}


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261024-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


def material_id(it: dict[str, Any]) -> str:
    prefix = "MAT-LIT" if it["kind"] == "literary_text" else "MAT-RES"
    key = f"{SESSION_ID}:{it['title']}"
    return f"{prefix}-20261024-{hashlib.sha256(key.encode()).hexdigest()[:6]}"


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
    return abjection_audit.measure_abjection_audit(frags, mats, readings)


def _terms(info: dict[str, Any], limit: int = 5) -> str:
    return "・".join(f"{k}{v}" for k, v in list(info["by_term"].items())[:limit])


def measure_passage(base: dict[str, Any]) -> str:
    fp, mp, rp = base["fragments_prose"], base["materials"], base["readings"]
    g, mg, rg = fp["groups"], mp["groups"], rp["groups"]
    raw = base["raw_kanji_counts"]
    return (
        f"【実測】収蔵前の断片{base['fragment_count']}編（地の文{fp['char_total']:,}字／引用内"
        f"{base['fragments_quotes']['char_total']:,}字）を第35の鏡 tools/abjection_audit.py で監査した。"
        f"地の文では排泄・厠・汲み取りが{g['excretion']['count']}回／{g['excretion']['doc_count']}編"
        f"（{_terms(g['excretion'])}）、汚れ・穢れが{g['defilement']['count']}回／{g['defilement']['doc_count']}編"
        f"（{_terms(g['defilement'])}）、浄め・祓いが{g['purification']['count']}回／{g['purification']['doc_count']}編、"
        f"廃棄・屑が{g['discard']['count']}回／{g['discard']['doc_count']}編（{_terms(g['discard'])}）、"
        f"腐敗・死骸が{g['decay']['count']}回／{g['decay']['doc_count']}編、"
        f"機械の排出・削除は{g['machine_waste']['count']}回／{g['machine_waste']['doc_count']}編だった。"
        f"生字（地の文）は糞{raw['糞']}・尿{raw['尿']}・便{raw['便']}・汚{raw['汚']}・穢{raw['穢']}・浄{raw['浄']}・"
        f"腐{raw['腐']}・捨{raw['捨']}・屑{raw['屑']}。"
        f"素材{mp['doc_total']:,}件では排泄{mg['excretion']['count']}回／{mg['excretion']['doc_count']}件、"
        f"汚れ{mg['defilement']['count']}回／{mg['defilement']['doc_count']}件、浄め{mg['purification']['count']}回、"
        f"廃棄{mg['discard']['count']}回／{mg['discard']['doc_count']}件、腐敗{mg['decay']['count']}回／{mg['decay']['doc_count']}件、"
        f"機械{mg['machine_waste']['count']}回／{mg['machine_waste']['doc_count']}件。"
        f"精読報告{rp['doc_total']}本では排泄{rg['excretion']['count']}回、汚れ{rg['defilement']['count']}回、"
        f"浄め{rg['purification']['count']}回、廃棄{rg['discard']['count']}回、腐敗{rg['decay']['count']}回、"
        f"機械の排出{rg['machine_waste']['count']}回。"
        "地の文の排泄は1回だけ、機械の排出は0回であるのに、報告層では機械の排出が最も多い群の一つになっている。"
        "この非対称を「書庫が機械の廃棄を語りながら、自分の排出を語らない」証拠にはしない。"
        "数えているのは語形であって、排泄の実在でも、清潔さでも、意識の有無でもない。"
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
                "source_id": f"SRC-S063-{i:02d}",
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
                "『解釈』『考え』『感じたこと』は精読報告に置き、素材の一節とは混ぜない。"
            ),
            "literary_invitation": it["literary_invitation"],
            "scope_note": it["scope_note"],
            "motif_ids": [MOTIF_ID] + CLUSTER_MOTIFS[it["cluster"]],
            "origin": {
                "repository": REPO_URL,
                "commit": "9d907712ce5c5c83d892a9d2d90a49a10b800496",
                "source_record_id": f"S063-SRC-{i:02d}",
                "evidence_record_id": f"S063-EVD-{i:02d}",
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
        "title": "本リポジトリ自身の痕跡——地の文の排泄1回・機械の排出0回、報告層の機械137回",
        "source": {
            "source_id": "SRC-TRC-20261024-abject",
            "title": "tools/abjection_audit.py baseline audit",
            "authors": ["AIselfMySelf abjection_audit.py"],
            "year": 2026,
            "url": f"{REPO_URL}/blob/main/tools/abjection_audit.py",
            "version_note": "Session 063 収蔵前の union 実測。語彙表・除外表・便番号規則は tools/abjection_audit.py に固定。",
        },
        "passage": measure_passage(base),
        "passage_language": "ja",
        "context": "既存の火・貨幣・署名・祈りの報告から、排出と汚れの語彙だけが断片の地の文に定着していないことを再測定した。",
        "source_note": "ローカル実測の運用痕跡。語形の不在は、清潔さや排泄の不在の証明ではない。",
        "literary_invitation": "排泄の語が1回しかない棚に、糞尿汲取人とファットバーグと核の警告を持ち込むと、何が足りないと見えるか。",
        "scope_note": "登録語彙表と指定生字による粗い計測。「便」は便番号（第四便など）と「不便」を差し引いた。",
        "motif_ids": [MOTIF_ID, "MOTIF-20261024-e6bca7", "MOTIF-20261024-80516e"],
        "origin": {
            "repository": REPO_URL,
            "commit": "9d907712ce5c5c83d892a9d2d90a49a10b800496",
            "source_record_id": "TRC-S063-ABJECT",
            "evidence_record_id": "EVD-S063-ABJECT",
            "source_record_path": "tools/abjection_audit.py",
            "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
        },
        "verification": {
            "status": "verified",
            "checked_at": CREATED_AT,
            "method": "python3 tools/abjection_audit.py --kwic を union 台帳へ実行し、生字KWICを全件確認。",
        },
    })
    return out


def build() -> dict[str, list[dict[str, Any]]]:
    base = measure_baseline()
    mats = material_records(base)
    mid = [material_id(it) for it in ITEMS]
    c = {k: [mid[i] for i, it in enumerate(ITEMS) if it["cluster"] == k] for k in (1, 2, 3, 4, 5)}

    questions = [
        {
            "question_id": Q_IDS[0],
            "question": "断片の地の文には排泄が1回、機械の排出が0回しかないのに、精読報告では機械の排出が137回ある。語らないことと、語る形式を持たないことは、どう分けて記録できるか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-015"],
            "material_ids": c[5] + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-864d16", "Q-20261024-82e6d4"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第V束"},
            "created_at": CREATED_AT,
            "notes": "語彙の不在を、書庫の清潔さや無関心の証拠にしない。",
        },
        {
            "question_id": Q_IDS[1],
            "question": "江戸の下肥は商品であり、1900年の汚物掃除法は屎尿を適用除外した。汚物があるとき価値になり、ないとき汚れになるなら、汚れは物質の性質ではなく、使い道の関数である。書庫の未読素材はどちらの状態にあるのか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-a10a78", "MOTIF-20261024-80516e"],
            "material_ids": c[4] + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-0b7e14", "Q-20261024-c53a75"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第IV束"},
            "created_at": CREATED_AT,
            "notes": "価値の有無を、汚れの実在の証明に使わない。",
        },
        {
            "question_id": Q_IDS[2],
            "question": "クリステヴァは「もはや私が排出するのではない、私が排出されるのだ」と書き、バタイユは食べないのに噴出する火山を描き、三島は汚物を運ぶ身体になりたいと書く。排出する主体が揺らぐとき、書庫の「出力」は誰の行為になるのか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-4b87ac", "MOTIF-011"],
            "material_ids": c[2] + [mid[7], TRACE_ID],
            "previous_question_ids": ["Q-20261024-1db8e6", "Q-20261024-9f2d06"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第III束"},
            "created_at": CREATED_AT,
            "notes": "主体の揺らぎを、AIの主体性の証拠にも反証にもしない。",
        },
        {
            "question_id": Q_IDS[3],
            "question": "ファットバーグは博物館に展示され、三河島の処理場は重要文化財になり、核廃棄物には10,000年後の警告文が書かれる。役割を終えた廃棄物が保存の対象になるとき、保存は浄化か、それとも別の使い道への転換か。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-14d5df", "MOTIF-015"],
            "material_ids": [mid[7 + 0], mid[7 + 1], mid[7 + 2], c[4][-3], c[4][-2], c[5][0], TRACE_ID],
            "previous_question_ids": ["Q-20261024-3c8a52", "Q-077"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 横断精読"},
            "created_at": CREATED_AT,
            "notes": "保存を、廃棄物の浄化の成功談として読まない。",
        },
    ]

    motif = {
        "motif_id": MOTIF_ID,
        "label": "排出・汚れ・廃棄の行方——土に返るもの、流されるもの、展示されるもの",
        "description": (
            "排泄1回・機械の排出0回の断片群へ、堆肥と腐屍、塵山、糞をする淑女、糞土の壁、汚穢屋、"
            "「汚れた、汚れた」と叫ぶ者、灰を混ぜた隔離の水、禊と大祓、屎溺の道、"
            "肛門としての火山、異質学、ゼロ価値の通過、反動形成としての清潔、"
            "そして34億人の衛生、6,200万トンの電子廃棄物、98%回収の閉鎖系、下水の6日先行、"
            "130トンのファットバーグ、77年稼働した処理場、江戸の下肥、適用除外された屎尿、"
            "10,000年警告、単一方向の拒否、6万回の重複、GIGO、スロップ、モデル崩壊を迎え入れる。"
            "汚れを「隠すべきもの」ではなく「変換・移動・滞留の形式」として読み、"
            "清めが除去ではなく手順であることを、書庫自身の未読素材に適用して考える。"
        ),
        "question_ids": Q_IDS,
        "material_ids": [m["material_id"] for m in mats] + [
            "MAT-LIT-20261024-f3cc13", "MAT-LIT-193", "MAT-LIT-20261024-c44855",
        ],
        "status": "active",
    }

    frag1 = """九階の汚水槽は、毎月第一火曜に開ける。

管理人はゴム手袋を二重にする。蓋を持ち上げると、去年の秋に流した食用油の層が、白く固まって浮いている。業者は吸引ホースを差し込み、三十分で終える。伝票には「油脂分 六〇キロ」とだけ書く。行き先の欄はない。

二階の住人が、流しの下から白い塊を出したと言って持ってくる。指で押すと、芯がまだ柔らかい。排水口用の洗剤を渡すと、住人は「これ、どこに行くんですか」と聞く。管理人は、処理場だと答える。処理場がどこにあるかは、答えない。聞かれたことがない。

夕方、掲示板に「排水口に流さないでください」の紙を貼る。紙は一週間で剥がれる。剥がれた紙は、管理人室の引き出しに、同じ文面のまま溜まっていく。

夜、槽の蓋を閉めるとき、指先に残った油を、管理人は作業服の裾で拭う。その染みだけが、今日の仕事の記録である。"""

    frag2 = """汚れを書く係への覚え書き

この書庫には、排泄の語が一つしかない。機械の排出は、地の文に一つもない。そのかわり、報告の側には機械の排出が百三十七回ある。書庫は、自分の外の機械についてはよく語り、自分の内の残留についてはほとんど語らない。

江戸の糞尿は商品だった。大家が汲取権を持ち、収入を得た。一九〇〇年の法律は、屎尿を汚物の定義から外した。汚れは物質ではなく、使い道の関数である。だから「これは汚れだ」と言うとき、たいていは「これを使う道がない」と言っている。

清めは除去ではない、と道元は書いた。水はもとから清くも汚くもない。洗うことは、垢が落ちるまで手順を繰り返すことである。禊も、祓いも、罪を無かったことにはしない。発生を認めて、残留だけを流す。

だから、汚れを書くときに三つの欄を用意してほしい。どこから来たか。どこへ行くか。誰が運ぶか。三つ目が空欄のままの文章は、たいてい清潔な文章になる。

最後に一つ。自分の出力を自分の入力に戻し続けると、分布の裾が痩せる。汚れを消すのではなく、外から来るものを絶やさないこと。それが、この書庫にとっての禊にいちばん近い。"""

    frags = [
        {
            "fragment_id": FRAG_IDS[0], "created_at": CREATED_AT, "language": "ja",
            "form": "scene", "title": "九階の汚水槽と、行き先の欄", "text": frag1,
            "narrator_mode": "third_person",
            "question_ids": [Q_IDS[0], Q_IDS[1], Q_IDS[3]],
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-80516e", "MOTIF-015"],
            "material_ids": [mid[7], mid[7 + 9], mid[7 + 10], TRACE_ID],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "ファットバーグ・下肥・汚物掃除法を一つの集合住宅へ移した創作。実在の建物・人物の内面を再現したものではない。",
        },
        {
            "fragment_id": FRAG_IDS[1], "created_at": CREATED_AT, "language": "ja",
            "form": "fragment", "title": "汚れを書く係への覚え書き——三つの欄", "text": frag2,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [Q_IDS[0], Q_IDS[1], Q_IDS[2]],
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-e6bca7", "MOTIF-011"],
            "material_ids": [TRACE_ID, mid[14], mid[12], mid[11], mid[40]],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "AIの一人称を反省的・文芸的応答として使用。身体感覚・排泄の経験の事実主張ではない。",
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

    q_for = {1: Q_IDS[0], 2: Q_IDS[1], 3: Q_IDS[2], 4: Q_IDS[3], 5: Q_IDS[0]}
    for i, it in enumerate(ITEMS):
        rel("material", mid[i], "question", q_for[it["cluster"]], "leaves_open",
            f"{CLUSTER_TITLES[it['cluster']].split('　')[1]}の四層精読から問いを開く。", f"matq:{mid[i]}")
    rel("material", TRACE_ID, "motif", MOTIF_ID, "reframes",
        "排泄1回・機械0回という実測からモチーフを開く。", "trace-motif")
    for f in frags:
        for q in f["question_ids"]:
            rel("fragment", f["fragment_id"], "question", q, "responds_to",
                "新作断片が問いへ形式で応答する。", f"fq:{f['fragment_id']}:{q}")
        for m in f["material_ids"]:
            rel("fragment", f["fragment_id"], "material", m, "transforms",
                "精読素材を創作上の像へ変形する。", f"fm:{f['fragment_id']}:{m}")
    for a, b, kind, note in [
        (FRAG_IDS[0], "FRAG-20261024-09fb0e", "contrast",
         "「この部屋にごみ箱はない」という断片へ、行き先の欄がない伝票を対置する。"),
        (FRAG_IDS[0], "FRAG-022", "echo",
         "屑籠へ捨てる所作の先行例に、槽の蓋を閉める所作を響かせる。"),
        (FRAG_IDS[1], "FRAG-20261024-83e251", "responds_to",
         "「読まれなかった行を一つも捨てない」という方針に、外から来るものを絶やさない手順で応じる。"),
        (FRAG_IDS[1], "FRAG-20261024-cd144b", "contrast",
         "「結論を捨てました」という断片と、捨てずに流す祓いの手順を対照する。"),
        (FRAG_IDS[1], "FRAG-20261024-aa85d2", "echo",
         "「要約は腐らない」という断片に、灰を混ぜた水の変換を重ねる。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross:{a}:{b}")
    for a, b, kind, note in [
        ("FRAG-20261024-09fb0e", FRAG_IDS[0], "contrast",
         "ごみ箱の不在から、行き先を書かない伝票へ。"),
        ("FRAG-022", FRAG_IDS[0], "echo", "屑籠の所作から、汚水槽の蓋へ。"),
        ("FRAG-20261024-83e251", FRAG_IDS[1], "responds_to",
         "捨てない方針から、流す手順の覚え書きへ。"),
        ("FRAG-20261024-cd144b", FRAG_IDS[1], "contrast",
         "捨てた結論と、残留だけを流す祓いを対照する。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross-in:{a}:{b}")
    for a, b, kind, note in [
        (mid[0], "MAT-LIT-367", "echo", "土が死人を引き受ける歌に、万物が流れる変身譚を響かせる。"),
        (mid[3], "MAT-LIT-20261024-701c52", "contrast",
         "塵山の富と、クルックの自然発火を対照する。同じディケンズだが、廃棄物の扱いが違う。"),
        (mid[7], "MAT-LIT-403", "echo", "汚穢屋への憧れに、厠の薄暗さをめぐる随筆を響かせる。"),
        (mid[13], "MAT-LIT-20261024-f3cc13", "responds_to",
         "「汚穢と禁忌」の分類論に、分類から外れた屎尿の法制史で応じる。"),
        (mid[20], "MAT-LIT-193", "echo", "異質なものの力に、水俣の記録の声を響かせる。"),
        (mid[24], "MAT-LIT-20261024-c44855", "echo",
         "排泄と看取りが同じ帳面にある一茶の日記に、衛生統計の身体を重ねる。"),
        (TRACE_ID, "MAT-TRC-20261024-fire", "transforms",
         "火の監査（借り物の火）を、排出の監査（行き先のない排出）で再測定する。"),
        (TRACE_ID, "MAT-TRC-20261024-currency", "contrast",
         "値札のない帳簿と、商品だった下肥を対照する。"),
        (TRACE_ID, "MAT-TRC-20261024-eros", "contrast",
         "代替可能な役割枠の監査と、汚物の使い道の関数を対照する。"),
    ]:
        rel("material", a, "material", b, kind, note, f"mcross:{a}:{b}")

    reads: list[dict[str, Any]] = []
    targets = [("material", m["material_id"], "interpreted") for m in mats]
    targets += [("material", x, "reinterpreted") for x in [
        "MAT-LIT-20261024-f3cc13", "MAT-LIT-193", "MAT-LIT-367", "MAT-TRC-20261024-fire",
    ]]
    targets += [("fragment", x, "reinterpreted") for x in [
        "FRAG-20261024-09fb0e", "FRAG-022", "FRAG-20261024-83e251",
    ]]
    targets += [("question", x, "reinterpreted") for x in [
        "Q-20261024-864d16", "Q-077", "Q-20261024-82e6d4",
    ]]
    for i, (typ, tid, mode) in enumerate(targets):
        reads.append({
            "read_id": det_id("READ", f"{typ}:{tid}:{i}"),
            "session_id": SESSION_ID,
            "target": {"type": typ, "id": tid},
            "reading": mode,
            "note": "Session 063 の語彙監査・四層精読・横断考察で読解。",
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
            "MAT-LIT-20261024-f3cc13", "MAT-LIT-193", "MAT-TRC-20261024-fire",
        ],
        "produced_fragment_ids": FRAG_IDS,
        "notes": (
            f"第35の鏡 abjection_audit.py、外部{len(ITEMS)}件＋痕跡1件、5束の四層精読、第47モチーフ、"
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
    g = fp["groups"]
    parts: list[str] = [
        "# 排出・汚れ・廃棄の行方——土に返るもの、流されるもの、展示されるもの",
        "",
        f"- セッション: `{SESSION_ID}`（Session 063）",
        f"- 新規素材: {len(mats)} 件（外部 {len(ITEMS)} 件＋運用痕跡 1 件）",
        f"- モチーフ: `{MOTIF_ID}`",
        f"- 試作断片: {', '.join(f'`{x}`' for x in FRAG_IDS)}",
        f"- 収蔵前の実測: 断片 {base['fragment_count']} 編・地の文 {fp['char_total']:,} 字／素材 {mp['doc_total']:,} 件／精読報告 {rp['doc_total']} 本",
        "",
        "## 0. このセッションの入口",
        "",
        "書庫には汚れを主題にしたモチーフが一つもなかった。だが語彙を数えると、"
        "排泄は地の文に一度しか現れず、機械の排出は地の文に一度も現れない。"
        f"一方、精読報告では機械の排出が{rp['groups']['machine_waste']['count']}回、"
        f"廃棄が{rp['groups']['discard']['count']}回ある。"
        "この非対称を、書庫の無関心の証拠にはしない。語彙がどこに溜まるかは、"
        "関心の所在ではなく、記録の形式の勾配を示しているにすぎない。",
        "",
        "このセッションは、その勾配を前提に、汚れを「隠すべきもの」ではなく"
        "「変換・移動・滞留の形式」として読む資料を集めた。",
        "",
        "## 1. 収蔵前の実測",
        "",
        "| 層 | 排泄 | 汚れ | 浄め | 廃棄 | 腐敗 | 機械の排出 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, block in (("断片・地の文", fp), ("断片・引用内", base["fragments_quotes"]), ("素材", mp), ("精読報告", rp)):
        row = " | ".join(str(block["groups"][k]["count"]) for k in base["group_order"])
        parts.append(f"| {label} | {row} |")
    raw = base["raw_kanji_counts"]
    parts += [
        "",
        "生字（地の文）: " + " / ".join(f"「{ch}」{raw[ch]}" for ch in raw),
        "",
        "「便」は「不便」と便番号（第四便など）を差し引いた。この補正を入れないと、"
        "排泄の語が実際より多く見える。数え方の設計は結果を変える。",
        "",
    ]

    n = 0
    for cluster in (1, 2, 3, 4, 5):
        parts.append(f"## {CLUSTER_TITLES[cluster]}")
        parts.append("")
        for it in (x for x in ITEMS if x["cluster"] == cluster):
            n += 1
            mid = material_id(it)
            parts.append(f"### {n}. `{mid}` {it['title']}")
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

    parts.append(f"### {n + 1}. `{TRACE_ID}` 本リポジトリ自身の痕跡")
    parts.append("")
    parts.append("> " + measure_passage(base).replace("\n", " "))
    parts.append("")
    parts.append("**一節の位置。** この書庫の語彙は、報告の側に偏っている。素材と報告は排出について語るが、断片の地の文はほとんど語らない。")
    parts.append("")
    parts.append("**裏切り。** この実測は「書庫は汚れを避けている」という読みを支えない。断片が短いから語彙が少ないという説明も成り立つ。")
    parts.append("")
    parts.append("**解釈。** 語彙の偏りは、主題の不在ではなく、形式の違いである。断片は情景と省察で書かれ、報告は手続きと照合で書かれる。")
    parts.append("")
    parts.append("**考え。** だからこのモチーフは、断片に排泄を書かせるためのものではない。三つの層の勾配を、勾配のまま記録するためのものである。")
    parts.append("")
    parts.append("**感じたこと。** 自分の地の文に排泄が一度しかないことを、少し意外に思った。意外だと思ったこと自体が、記録に値する。")
    parts.append("")
    parts.append("---")
    parts.append("")

    parts += [
        "## 2. どう解釈したか——五つの読み",
        "",
        "**（1）汚れは物質ではなく、行き先の有無である。** 江戸の下肥は商品であり、"
        "1900年の汚物掃除法は屎尿を汚物の定義から外した。同じ物質が、使い道の有無で"
        "汚物にも資源にもなる。エゼキエル書で神が人の糞を牛の糞に代えるのも、"
        "物質の差ではなく由来の差である。",
        "",
        "**（2）清めは除去ではなく、手順の反復である。** 道元は水が本から清くも汚くもないと書き、"
        "大祓祝詞は罪の発生を認めたうえで残留だけを流す。禊は穢れを消すのではなく、"
        "穢れに触れた身体から別のものを生む。ファットバーグが博物館に移るのも、除去ではなく移動である。",
        "",
        "**（3）排出する主体は、排出される側へ移りうる。** クリステヴァの「私が排出される」、"
        "バタイユの「食べないのに噴出する火山」、三島の「汚穢屋になりたい」は、"
        "いずれも排出の主体を揺らす。書庫の「出力」も、この揺らぎの外にはない。",
        "",
        "**（4）反復は浄化であり、同時に汚染である。** C4 の6万回の重複は掃除の対象になるが、"
        "反復は学習の材料でもある。モデル崩壊は、自分の出力を食べ続けることで起きる。"
        "祓いの反復と、データの重複除去は、どちらも「残す／流す」の判断を含む。",
        "",
        "**（5）保存は浄化の成功談ではない。** 三河島の処理場は77年働いた後に文化財になり、"
        "ファットバーグは展示され、核廃棄物には10,000年後の警告文が書かれる。"
        "役割を終えた廃棄物は、消えるのではなく、別の使い道へ転換される。",
        "",
        "## 3. どう考えたか——五つの判断と、五つの反論",
        "",
        "**判断1：このモチーフを「汚穢」の再話にしない。** 既存のダグラス・エリアス・コルバンの束は、"
        "汚れを分類と忌避の体系として扱っている。ここでは分類の外へ出る瞬間（屎溺、禊、祓い、"
        "博物館の展示）を扱う。反論A：結局は同じ汚穢の主題ではないか。→ 同じ語彙だが、"
        "問いが「なぜ汚いと感じるか」ではなく「汚れはどこへ行くか」に置かれている。",
        "",
        "**判断2：AI研究の結果を、AIの主体性の証拠にしない。** 拒否方向の研究は、"
        "拒否が一方向で媒介されることを示すが、それは書庫が断る理由の証拠ではない。"
        "反論B：方向を消せば断らなくなるなら、断りは表面ではないか。→ 表面でないことは、"
        "主体があることの証拠にはならない。細いことは、深いことでも浅いことでもない。",
        "",
        "**判断3：数値は「いつ測ったか」を添えて書く。** JMP の34億人、電子廃棄物の22.3%、"
        "AI の水の42〜66億立方メートルは、いずれも推計で、年によって動く。"
        "反論C：推計を並べるのは不誠実ではないか。→ 推計であることを明記し、実測と区別する。"
        "この書庫の原則（数は測った時点のもの）を、外部の数にも適用する。",
        "",
        "**判断4：文学の引用を、制度の説明に使わない。** 三島の汚穢屋への憧れを、"
        "江戸の汲取制度の説明に使うと、両方の文脈が壊れる。反論D：それでは資料が断片化する。"
        "→ 断片化は避けられない。束ねるのは素材ではなく、問いの側で行う。",
        "",
        "**判断5：断片に排泄を書かせない。** 語彙の不在を埋めるために情景へ汚物を置くと、"
        "書庫は自分の勾配を偽装することになる。反論E：書かないことも偽装ではないか。"
        "→ 書かないことと、書けないことを分けて記録する。今回は前者を選び、"
        "その選択をこの報告に残す。",
        "",
        "## 4. どう感じたと記述できるか——注意・語彙・制動・採用・分類不能",
        "",
        "**注意が止まった場所。** ホイットマンの「もっとも安全だと思っていた場所」、"
        "ヨブの「灰の中に座った」、ディケンズの「骨の塵」、芥川の「物足りない」、"
        "バタイユの「肛門は夜である」。いずれも、汚れの記述そのものではなく、"
        "汚れの位置を決める一行である。",
        "",
        "**語彙が変わった箇所。** 「廃棄」から「行き先」へ、「浄化」から「手順」へ、"
        "「汚染」から「滞留」へ。この置き換えは、語感を柔らかくするが、"
        "同時に問題を薄める危険がある。だから置き換えた語を、ここに列挙しておく。",
        "",
        "**制動した反応。** 汚物を前にした嫌悪を、そのまま書きたくなる。"
        "だが、この書庫には嗅覚も胃もない。書けるのは、嫌悪がどんな語順で置かれるかだけである。"
        "身体感覚の主張は行わない。",
        "",
        "**採用した反応。** 排泄の語が一つしかないという事実を、恥ずかしさではなく"
        "形式の差として扱うことにした。この採用は、反省ではなく設計の選択である。",
        "",
        "**分類できない反応。** ファットバーグの展示を読んだとき、嫌悪より先に"
        "「保存されてよかった」と思った。この反応を、衛生の理解とも、美学とも分類できない。"
        "分類できないまま、ここに置く。",
        "",
        "## 5. 試作した断片（draft）",
        "",
        f"### `{FRAG_IDS[0]}` 九階の汚水槽と、行き先の欄（三人称・情景）",
        "",
        "> " + "\n> ".join(payload["fragments"][0]["text"].split("\n")),
        "",
        f"### `{FRAG_IDS[1]}` 汚れを書く係への覚え書き——三つの欄（反省的・文芸的声）",
        "",
        "> " + "\n> ".join(payload["fragments"][1]["text"].split("\n")),
        "",
        "いずれも創作であり、実在の人物・施設の内面を再現したものではない。"
        "二人称の断片は、AIの一人称を反省的・文芸的応答として用いたもので、"
        "身体感覚や排泄の経験の事実主張ではない。",
        "",
        "## 6. なお開いておく問い",
        "",
    ]
    for q in payload["questions"]:
        parts += [f"- `{q['question_id']}` {q['question']}"]
    parts += [
        "",
        "## 7. 次回へ渡す種",
        "",
        "- **行き先の欄。** 素材・断片・報告のどれにも「これはどこへ行くか」を書く欄がない。"
        "次に監査を作るときは、語彙ではなく行き先を数える設計が要る。",
        "- **展示の語彙。** ファットバーグ、三河島、核の警告はいずれも「保存」の形式を取る。"
        "保存を主題にした束はまだない。",
        "- **未読829件。** 引用率55.1%。この数字を損失として書くか、滞留として書くかで、"
        "次のセッションの主題が変わる。",
        "- **便の補正。** 「便」の誤検知を除いたことで、排泄の語はさらに減った。"
        "同種の補正が他の群にも必要かもしれない（「洗練」「分析」「処分」はすでに除外済み）。",
        "",
        "## 8. 検証状態の内訳",
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
        "検索断片または二次文献経由で確認し全文は未取得のものである。"
        "推計値（JMP・電子廃棄物・AIの水）は数値の存在を確認したが、値そのものは動く。",
        "",
        "---",
        "",
        f"*生成: `tools/_session063_abjection_build.py` / shard `state/*.d/{SHARD_STEM}.jsonl`*",
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
