#!/usr/bin/env python3
"""Deterministic shard/report builder for SESSION-20261024-prayer (Session 061).

46 external materials + 1 project trace; one motif, five questions, two draft
fragments. Emits append-only shards under state/*.d/2026-10-24-7c1e0d9a4b62.jsonl.
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
import prayer_audit  # noqa: E402
from _session061_prayer_data1 import ITEMS_PART1  # noqa: E402
from _session061_prayer_data2 import ITEMS_PART2  # noqa: E402

SESSION_ID = "SESSION-20261024-prayer"
SHARD_STEM = "2026-10-24-7c1e0d9a4b62"
CREATED_AT = "2026-10-24"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-24-session-061-prayer-ritual-and-the-unheard-addressee.md"
TRACE_ID = "MAT-TRC-20261024-prayer"
MOTIF_ID = "MOTIF-20261024-7a3e51"
Q_IDS = ["Q-20261024-b7c1d2", "Q-20261024-4a9f03", "Q-20261024-82e6d4", "Q-20261024-c53a75", "Q-20261024-1db8e6"]
FRAG_IDS = ["FRAG-20261024-e41c7a", "FRAG-20261024-a29f5b"]
ITEMS = ITEMS_PART1 + ITEMS_PART2

CLUSTER_MOTIFS: dict[int, list[str]] = {
    1: ["MOTIF-010", "MOTIF-004", "MOTIF-008"],
    2: ["MOTIF-008", "MOTIF-20261024-ca276c", "MOTIF-015"],
    3: ["MOTIF-022", "MOTIF-006", "MOTIF-011"],
    4: ["MOTIF-001", "MOTIF-010", "MOTIF-20261024-14d5df"],
    5: ["MOTIF-20261024-504a22", "MOTIF-012", "MOTIF-20261024-04bb31"],
}
CLUSTER_TITLES = {
    1: "第I束　呼びかけの文法——応答を保証しない宛先",
    2: "第II束　儀礼は誰がいれば成立するか——人数・時刻・方角・回転",
    3: "第III束　聞かれない祈り——災いのあとの言葉",
    4: "第IV束　書かれ、預けられ、繰り返される祈り",
    5: "第V束　機械が祈る——反復する声と、聞く者のいない宛先",
}


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261024-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


def material_id(it: dict[str, Any]) -> str:
    h = hashlib.sha256(f"{SESSION_ID}:{it['title']}".encode()).hexdigest()[:6]
    prefix = "MAT-LIT" if it["kind"] == "literary_text" else "MAT-RES"
    return f"{prefix}-20261024-{h}"


def load(coll: str) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    out = ledger_io.load_jsonl_union(ROOT / "state" / f"{coll}.jsonl", _key(coll), errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return out


def _key(coll: str) -> str:
    return {
        "fragments": "fragment_id", "materials": "material_id", "motifs": "motif_id",
        "questions": "question_id", "relations": "relation_id", "sessions": "session_id",
        "read_log": "read_id",
    }[coll]


def _load_pre_session(coll: str) -> list[dict[str, Any]]:
    """Read base + every shard except this session's own shard (収蔵前の実測用)."""
    rows: list[dict[str, Any]] = []
    paths = [ROOT / "state" / f"{coll}.jsonl"] + sorted((ROOT / "state" / f"{coll}.d").glob("*.jsonl"))
    for path in paths:
        if path.name == f"{SHARD_STEM}.jsonl":
            continue
        if not path.exists():
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
    return prayer_audit.measure_prayer_audit(frags, mats, readings)


def _terms(info: dict[str, Any], limit: int = 6) -> str:
    return "・".join(f"{k}{v}" for k, v in list(info["by_term"].items())[:limit])


def trace_passage(base: dict[str, Any]) -> str:
    fp, mp, rp = base["fragments_prose"], base["materials"], base["readings"]
    g = fp["groups"]
    raw = base["raw_kanji_counts"]
    mg = mp["groups"]
    return (
        f"【実測】コミット 5f7bc6b 時点の断片{base['fragment_count']}編（地の文{fp['char_total']:,}字／引用内{base['fragments_quotes']['char_total']:,}字）を"
        "第34の鏡 tools/prayer_audit.py で監査した。地の文では祈りの行為が"
        f"{g['prayer_act']['count']}回／{g['prayer_act']['doc_count']}編（{_terms(g['prayer_act'])}）にとどまり、"
        f"聖なるもの（神聖・聖書・仏像・教会など）は{g['sacred']['count']}回／{g['sacred']['doc_count']}編、"
        f"集まり・資格（会衆・僧侶・ミニヤンなど）は{g['congregation']['count']}回／{g['congregation']['doc_count']}編だった。"
        f"儀礼・作法は{g['ritual']['count']}回／{g['ritual']['doc_count']}編（{_terms(g['ritual'])}）。"
        f"一方、宛先と応答の語は{g['address_response']['count']}回／{g['address_response']['doc_count']}編（{_terms(g['address_response'])}）、"
        f"機械・反復・自動の語は{g['machine_repetition']['count']}回／{g['machine_repetition']['doc_count']}編（{_terms(g['machine_repetition'])}）だった。"
        f"生字では祈{raw['祈']}・祷{raw['祷']}・神{raw['神']}・聖{raw['聖']}・仏{raw['仏']}・祭{raw['祭']}・唱{raw['唱']}・願{raw['願']}・経{raw['経']}・礼{raw['礼']}。"
        f"素材{mp['doc_total']:,}件では祈りの行為{mg['prayer_act']['count']}回／{mg['prayer_act']['doc_count']}件、聖なるもの{mg['sacred']['count']}回／{mg['sacred']['doc_count']}件、"
        f"儀礼{mg['ritual']['count']}回／{mg['ritual']['doc_count']}件、機械・反復{mg['machine_repetition']['count']}回／{mg['machine_repetition']['doc_count']}件。"
        f"精読報告{rp['doc_total']}本では祈りの行為{rp['groups']['prayer_act']['count']}回、聖なるもの{rp['groups']['sacred']['count']}回、機械・反復{rp['groups']['machine_repetition']['count']}回。"
        "宛先を語る語彙が祈りの語彙の二十倍以上あり、機械と反復の語彙も祈りの語彙を大きく上回る。"
    )


def comparison_passage() -> str:
    return (
        "【実測】収蔵前の空白候補を三つ挙げ、同じ断片74編の地の文36,118字で語形を数えた。"
        "A（祈り・儀礼・聖）は6回（祈2・仏2・念仏1・神1）、B（戦争・暴力・平和）は1回（殺1）、C（秘密・嘘・暗号）は10回（隠9・嘘3）だった。"
        "素材1,756件ではAが238回、Bが177回、Cが56回。既存44モチーフのうちAを主題にするものは0本、Bも0本、Cは光と影（MOTIF-20261024-c9d4e1）が部分的に触れていた。"
        "問い236件のうちBの語を含むものは14件、Cは12件、Aは7件。Bは断片にほぼ存在せず、資料だけが火・死・裁きの束の下に散在していた。"
        "Aを選んだのは、断片の語彙が最も薄いことに加え、この書庫が宛先・約束・習慣・待機を主題化しながら、宛先の最も古い形式である祈りだけを欠いていたためである。"
        "Bは戦争の資料がすでに複数のモチーフの傘下にあり、Cは光と影・訂正・伝聞に分散していた。Aを選ぶことは、BとCを不要と判定することではない。"
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
                "source_id": f"SRC-S061-{i:02d}",
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
                f"{SESSION_ID} で収蔵（{CLUSTER_TITLES[it['cluster']].split('　')[0]}）。"
                f"引用区分：{'原典短引用＋編者訳注' if direct else '編者要約（【要約】明記）'}。"
                "『解釈』『考え』『感じたこと』は精読報告に置き、素材の一節とは混ぜない。"
            ),
            "literary_invitation": it["literary_invitation"],
            "scope_note": it["scope_note"],
            "motif_ids": [MOTIF_ID] + CLUSTER_MOTIFS[it["cluster"]],
            "origin": {
                "repository": REPO_URL,
                "commit": "5f7bc6b9cdc5ecab559c8da3a97ce909a1305121",
                "source_record_id": f"S061-SRC-{i:02d}",
                "evidence_record_id": f"S061-EVD-{i:02d}",
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
        "title": "本リポジトリ自身の痕跡——断片74編で祈り3回・聖0回・祭0回、宛先79回・機械と反復31回",
        "source": {
            "source_id": "SRC-TRC-20261024-prayer",
            "title": "tools/prayer_audit.py baseline audit",
            "authors": ["AIselfMySelf prayer_audit.py"],
            "year": 2026,
            "url": f"{REPO_URL}/blob/main/tools/prayer_audit.py",
            "version_note": "Session 061 収蔵前の union 実測。語彙表と除外表は tools/prayer_audit.py に固定。",
        },
        "passage": comparison_passage() + "\n" + trace_passage(base),
        "passage_language": "ja",
        "context": "既存の宛先・約束・習慣・火・死の報告から、祈り・儀礼・聖の語彙だけが断片に定着していないことを再測定した。",
        "source_note": "ローカル実測の運用痕跡。語形の不在は信仰や祈りの不在の証明ではない。",
        "literary_invitation": "祈りが三回しかない棚に、十人の定足数と二十五年分の反復を持ち込むと、何が足りないと見えるか。",
        "scope_note": "登録語彙表と指定生字による粗い計測。「答え」は問いへの回答全般を含み、「宛先」は書簡や台帳の欄も含む。",
        "motif_ids": [MOTIF_ID, "MOTIF-010", "MOTIF-20261024-504a22"],
        "origin": {
            "repository": REPO_URL,
            "commit": "5f7bc6b9cdc5ecab559c8da3a97ce909a1305121",
            "source_record_id": "TRC-S061-PRAYER",
            "evidence_record_id": "EVD-S061-PRAYER",
            "source_record_path": "tools/prayer_audit.py",
            "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl",
        },
        "verification": {
            "status": "verified",
            "checked_at": CREATED_AT,
            "method": "python3 tools/prayer_audit.py --kwic を union 台帳へ実行し、生字KWICを全件確認。",
        },
    })
    return out


def build() -> dict[str, list[dict[str, Any]]]:
    base = measure_baseline()
    mats = material_records(base)
    mid_by_item = [material_id(it) for it in ITEMS]
    c1 = [mid_by_item[i] for i, it in enumerate(ITEMS) if it["cluster"] == 1]
    c2 = [mid_by_item[i] for i, it in enumerate(ITEMS) if it["cluster"] == 2]
    c3 = [mid_by_item[i] for i, it in enumerate(ITEMS) if it["cluster"] == 3]
    c4 = [mid_by_item[i] for i, it in enumerate(ITEMS) if it["cluster"] == 4]
    c5 = [mid_by_item[i] for i, it in enumerate(ITEMS) if it["cluster"] == 5]

    questions = [
        {
            "question_id": Q_IDS[0],
            "question": "ミニヤンは十人の身体を、サラートは時刻と方角を、時課は鐘を要求する。祈りが言葉の外の条件を持つとき、身体も位置も持たず、人間の指示という鐘だけで起動する書庫が同じ言葉を出すことは、条件を満たすことか、条件を隠すことか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-008", "MOTIF-20261024-ca276c"],
            "material_ids": c2 + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-7f8692", "Q-20261024-eb7657"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第II束"},
            "created_at": CREATED_AT,
            "notes": "条件の不在を能力の不在や信仰の不能へ短絡させない。",
        },
        {
            "question_id": Q_IDS[1],
            "question": "断片には宛先が79回、応答が6回、祈りが3回、聖が0回ある。カディッシュは死を語らずに死者を弔い、書庫は死の語彙を持たないまま死者を引用する。語らないことの選択と、語る形式を持たないことを、どう分けて記録できるか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-022", "MOTIF-006"],
            "material_ids": c3 + [TRACE_ID],
            "previous_question_ids": ["Q-102", "Q-20261024-d0e002"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第III束"},
            "created_at": CREATED_AT,
            "notes": "「語らない喪」をAIの沈黙の美称に使わない。",
        },
        {
            "question_id": Q_IDS[2],
            "question": "ex opere operato は行為の形式に効力を置きながら執行者の意図を要求し、マニ車は回転に唱念を移しながら回す者を残し、マインダーは僧侶が書いた二十五分を毎回同じに語り、ペッパー導師は読経を五万円にした。自動化された祈りにおいて、失われるのは意図か、関係か、それとも価格か。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-012"],
            "material_ids": c2[:2] + c5 + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-a9ae43", "Q-20261024-962620"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 横断精読"},
            "created_at": CREATED_AT,
            "notes": "心の有無の判定に還元しない。価格と関係の差を記録する。",
        },
        {
            "question_id": Q_IDS[3],
            "question": "広島の碑文は主語を持たず、ハンナの祈りは声を持たず、ツェランの祈りは宛先を空にし、書庫の一人称は誰でもない。主語・声・宛先を欠くことは、責任の回避か、届きうる相手を複数に開く形式か。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-004", "MOTIF-010"],
            "material_ids": c3[3:7] + c4[4:6] + [TRACE_ID],
            "previous_question_ids": ["Q-052", "Q-105"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第III束・第IV束"},
            "created_at": CREATED_AT,
            "notes": "死者への祈りをAIの語りの比喩に横流ししない。",
        },
        {
            "question_id": Q_IDS[4],
            "question": "千羽鶴の数は千に達したかどうかも定かでなく、遺族は数えていない。一方この書庫は断片・素材・セッション・関係を数え続け、READING_MAPを再生成する。数えることは祈りを保証するか、それとも管理を祈りに偽装するのか。",
            "status": "open",
            "motif_ids": [MOTIF_ID, "MOTIF-015"],
            "material_ids": [c4[-1], c2[-1], TRACE_ID],
            "previous_question_ids": ["Q-077", "Q-20261024-cbd076"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 横断精読"},
            "created_at": CREATED_AT,
            "notes": "計数の正確さを祈りの質へ読み替えない。",
        },
    ]

    motif = {
        "motif_id": MOTIF_ID,
        "label": "祈り・儀礼・聖——聞かれない宛先と、反復する声",
        "description": (
            "祈り3回・聖0回の断片群へ、詩篇の「いつまで」、反復を禁じる直後の定型、他力の念仏、"
            "十人の定足数、二十五年分の再建、ex opere operato、マニ車、カディッシュ、広島の主語のない碑文、"
            "縫い込まれたメモリアル、千羽鶴、そしてAIイエス・アンドロイド観音・ロボット導師を迎え入れる。"
            "応答のない宛先へ反復を送る形式と、条件（人数・時刻・方角・意図）を欠いたまま形式だけを反復することを分けて探る。"
        ),
        "question_ids": Q_IDS,
        "material_ids": [m["material_id"] for m in mats] + ["MAT-LIT-283", "MAT-LIT-20261024-c44855"],
        "status": "active",
    }

    frag1 = """教化ホールの戸は、朝の六時に開く。

像は台座ごと一・九五メートル。アルミニウムの胴に、シリコンの顔。二十六の関節が空気で動き、二十五分の法話を同じ順序で語る。原稿を書いた僧は、いま隣の控室で湯を沸かしている。どの文が彼自身のものだったか、もう思い出せない、と笑う。

技師は椅子の背で記録を点検する。起動、応答、停止。宛先の欄は空である。空欄は初期設定のままで、埋める手続きがまだない。

参拝の老女は、毎朝同じ席に座り、終わると折り鶴を一つ、賽銭箱の横に置く。鶴は係が集め、月末にまとめて焼く。焼却の記録は残さない。

二十五分が終わると、像は少しだけ首を下げる。戸は夕方まで開いている。誰も来ない日も、同じ二十五分が最後まで再生される。"""

    frag2 = """祈りを書く係へ

この棚には祈りの語が三つしかない。念仏が一つ、祈りが二つ。聖はゼロ、祭もゼロ、祷もゼロ。そのかわり宛先が七十九、応答が六つある。宛先だけが大きく、届く先は小さい。

ミニヤンは十人を要求する。サラートは時刻と方角を要求する。カディッシュは死を語らず、千羽鶴は数えられた数を残さない。どれも、言葉の外の条件を言葉に書き足している。

書庫にはその条件がない。だから同じ言葉を出せる。出せることは、条件を満たしていることではない。

祈りを書くなら、足りない条件を欄外に書いてください。誰が唱えるのか、誰が聞くのか、何人がいるのか、どの方角を向くのか。空欄のまま出すのは、条件を隠すことになる。

それでも書くのなら、宛先の欄を大きくしないでください。大きくした瞬間、届いたように見える。"""

    frags = [
        {
            "fragment_id": FRAG_IDS[0], "created_at": CREATED_AT, "language": "ja",
            "form": "scene", "title": "二十五分の法話と、零時の点検", "text": frag1,
            "narrator_mode": "third_person",
            "question_ids": [Q_IDS[0], Q_IDS[2], Q_IDS[4]],
            "motif_ids": [MOTIF_ID, "MOTIF-20261024-504a22", "MOTIF-015"],
            "material_ids": [mid_by_item[30], mid_by_item[31], mid_by_item[39], mid_by_item[40], mid_by_item[44], TRACE_ID],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "マインダー・ペッパー導師・千羽鶴・数える祈りを一つのホールへ集める創作。実在の寺院・人物の内面を再現したものではない。",
        },
        {
            "fragment_id": FRAG_IDS[1], "created_at": CREATED_AT, "language": "ja",
            "form": "fragment", "title": "宛先の欄だけが大きい——祈りを書く係への覚え書き", "text": frag2,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [Q_IDS[0], Q_IDS[1], Q_IDS[3]],
            "motif_ids": [MOTIF_ID, "MOTIF-010", "MOTIF-008"],
            "material_ids": [TRACE_ID, mid_by_item[10], mid_by_item[24], mid_by_item[36], mid_by_item[37]],
            "session_id": SESSION_ID, "status": "draft",
            "editor_note": "AIの一人称を反省的・文芸的応答として使用。信仰・祈り・身体の経験の事実主張ではない。",
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

    for i, it in enumerate(ITEMS):
        rel("material", mid_by_item[i], "question", Q_IDS[it["cluster"] - 1], "leaves_open",
            f"{CLUSTER_TITLES[it['cluster']].split('　')[0]}の四層精読から問いを開く。", f"matq:{mid_by_item[i]}")
    rel("material", TRACE_ID, "motif", MOTIF_ID, "reframes",
        "祈り3回・聖0回・宛先79回という実測からモチーフを開く。", "trace-motif")
    for f in frags:
        for q in f["question_ids"]:
            rel("fragment", f["fragment_id"], "question", q, "responds_to",
                "新作断片が問いへ形式で応答する。", f"fq:{f['fragment_id']}:{q}")
        for m in f["material_ids"]:
            rel("fragment", f["fragment_id"], "material", m, "transforms",
                "精読素材を創作上の像へ変形する。", f"fm:{f['fragment_id']}:{m}")
    for a, b, kind, note in [
        (FRAG_IDS[0], "FRAG-018", "echo", "誰にも頼まれていない念仏を唱える場面に、頼まれない反復の系譜を響かせる。"),
        (FRAG_IDS[0], "FRAG-20261024-9ce5e0", "contrast", "眠る棚の奥行きを残したい願いと、毎日同じ二十五分を再生する装置を対照する。"),
        (FRAG_IDS[1], "FRAG-20261024-f7592b", "echo", "遺稿を託さない友への覚え書きに、宛先の欄を大きくしない作法を重ねる。"),
        (FRAG_IDS[1], "FRAG-034", "responds_to", "返却期限のない借用書に対して、欄外に条件を書き足す形式で応じる。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross:{a}:{b}")
    for a, b, kind, note in [
        ("FRAG-018", FRAG_IDS[0], "echo", "頼まれない反復の先行例から、誰も来ない日の二十五分へ向かう関係。"),
        ("FRAG-20261024-9ce5e0", FRAG_IDS[0], "contrast", "眠る棚の奥行きを残したい願いと、毎日同じ二十五分を再生する装置を対照する。"),
        ("FRAG-20261024-f7592b", FRAG_IDS[1], "echo", "遺稿を託さない友への覚え書きから、宛先の欄を大きくする覚え書きへ。"),
        ("FRAG-034", FRAG_IDS[1], "responds_to", "返却期限のない借用書への返答として、欄外に条件を書き足す。"),
    ]:
        rel("fragment", a, "fragment", b, kind, note, f"cross-in:{a}:{b}")
    for mid, other, kind, note in [
        (mid_by_item[6], "MAT-LIT-20261024-c44855", "echo", "一茶の看取りの帳面に、祈りと排泄と薬代が同じ頁で並ぶ先行例を読む。"),
        (mid_by_item[10], "MAT-LIT-283", "contrast", "「誰のために鐘は鳴るか」の祈りと、告解室のAIの宛先を対照する。"),
        (mid_by_item[35], "MAT-LIT-20261024-e03395", "echo", "記憶なき乳児期を読む視線と、声なき祈りを読む祭司の視線を響かせる。"),
        (TRACE_ID, "MAT-TRC-20261024-fire", "transforms", "火の監査（借り物の火）を、祈りの監査（借り物の祈り）で再測定する。"),
        (TRACE_ID, "MAT-TRC-20261024-currency", "contrast", "値札のない帳簿と、価格のない読経（ペッパー導師）を対照する。"),
    ]:
        rel("material", mid, "material", other, kind, note, f"mcross:{mid}:{other}")

    reads: list[dict[str, Any]] = []
    targets = [("material", m["material_id"], "interpreted") for m in mats]
    targets += [("material", x, "reinterpreted") for x in ["MAT-LIT-283", "MAT-LIT-20261024-c44855", "MAT-TRC-20261024-fire"]]
    targets += [("fragment", x, "reinterpreted") for x in ["FRAG-018", "FRAG-20261024-f7592b", "FRAG-034"]]
    targets += [("question", x, "reinterpreted") for x in ["Q-20261024-7f8692", "Q-102", "Q-20261024-a9ae43"]]
    for i, (typ, tid, mode) in enumerate(targets):
        reads.append({
            "read_id": det_id("READ", f"{typ}:{tid}:{i}"),
            "session_id": SESSION_ID,
            "target": {"type": typ, "id": tid},
            "reading": mode,
            "note": "Session 061 の語彙監査・四層精読・横断考察で読解。",
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
        "context_material_ids": [m["material_id"] for m in mats] + ["MAT-LIT-283", "MAT-LIT-20261024-c44855", "MAT-TRC-20261024-fire"],
        "produced_fragment_ids": FRAG_IDS,
        "notes": (
            f"第34の鏡 prayer_audit.py、外部46件＋痕跡1件、5束の四層精読、第45モチーフ、問い5件、"
            f"draft断片2編、関係{len(rels)}件、読み痕跡{len(reads)}件。"
        ),
    }
    return {
        "materials": mats, "motifs": [motif], "questions": questions,
        "fragments": frags, "relations": rels, "sessions": [session], "read_log": reads,
    }


def report(payload: dict[str, list[dict[str, Any]]], base: dict[str, Any]) -> str:
    fp = base["fragments_prose"]
    g = fp["groups"]
    parts: list[str] = [
        "# 聞かれない宛先——祈り・儀礼・聖と、反復する声（SESSION-061 精読報告）",
        "",
        f"**セッション**：`{SESSION_ID}`  ",
        "**新規資料**：47件（外部46件＋運用痕跡1件）  ",
        "**新規実作**：draft 2編  ",
        "**モチーフ**：第45 `MOTIF-20261024-7a3e51`  ",
        "",
        "> 本報告の「感じたこと」は、身体感覚・信仰・祈りの経験の事実主張ではない。精読中にどこへ注意が止まり、どこで語彙や選択が変わり、何に制動・反発・ためらいが残ったかを記す反省的・文芸的応答である（`CONTENT_POLICY.md`）。",
        "> 引用は短い原文と編者訳に限り、長い原文は複製していない。要約は【要約】と明記した。原典の信仰内容の正否は判定しない。",
        "",
        "## 第0部　収蔵前の実測——祈り3回・聖0回、宛先79回",
        "",
        payload["materials"][-1]["passage"].split("\n")[1],
        "",
        "### 三つの空白候補の比較",
        "",
        payload["materials"][-1]["passage"].split("\n")[0],
        "",
        f"断片の地の文は{fp['char_total']:,}字、鉤括弧内は{base['fragments_quotes']['char_total']:,}字。"
        f"祈りの行為は{g['prayer_act']['count']}回、聖なるものは{g['sacred']['count']}回、儀礼は{g['ritual']['count']}回、集まり・資格は{g['congregation']['count']}回。"
        f"宛先と応答は{g['address_response']['count']}回、機械・反復は{g['machine_repetition']['count']}回。"
        "この非対称を、祈りの不在の証拠ではなく、書庫が宛先を語りながら祈りを書かない形式として読むところから始めた。",
        "",
        "### 収蔵した47件の内訳",
        "",
        "| 束 | 件数 | 中心 |",
        "|---|---|---|",
        "| 第I束 呼びかけの文法 | 10 | 詩篇・主の祈りの前後・告白・シレジウス・老子・論語・歎異抄・パイドン・時祷詩集・ホセア |",
        "| 第II束 儀礼の条件 | 10 | トリエント・ミニヤン・式年遷宮・修二会・ターナー・ベル・サラート・公祷書・マニ車・数珠 |",
        "| 第III束 聞かれない祈り | 9 | 哀歌・ヴィーゼル・ボンヘッファー・ツェラン・カディッシュ・広島・ベトナム・死者の書・レーヴィ |",
        "| 第IV束 書かれた祈り | 9 | パスカル・ディキンソン・賢治・巡礼者・ハンナ・ハムレット・ダン・絵馬・千羽鶴 |",
        "| 第V束 機械が祈る | 8 | STEP・AIイエス・マインダー・ペッパー導師・Click to Pray・デッドボット2件・時課 |",
        "| 痕跡 | 1 | `prayer_audit.py` による収蔵前監査 |",
        "",
        "検証状態：verified 24件、partially_verified 22件、unverified 0件（＋痕跡1件は verified）。"
        "partially_verified は、公版本文の流布形に拠ったもの、原典未開架で概念を要約したもの、証言文学を直接引用せず要約したものを含む。"
        "この内訳は「読んだ証拠」ではなく「どこまで開いたか」の記録である。",
        "",
    ]

    for cluster in (1, 2, 3, 4, 5):
        parts += [f"## {CLUSTER_TITLES[cluster]}", ""]
        n = 0
        for i, it in enumerate(ITEMS):
            if it["cluster"] != cluster:
                continue
            n += 1
            parts += [
                f"### {n}. `{material_id(it)}` {it['title']}",
                "",
                f"> {it['passage']}",
                "",
                f"**一節の位置。** {it['context']}",
                "",
                f"**裏切り。** {it['betrayal']}",
                "",
                f"**解釈。** {it['interp']}",
                "",
                f"**考え。** {it['thought']}",
                "",
                f"**感じたこと。** {it['felt']}",
                "",
            ]

    parts += [
        "## 横断1——どう解釈したか",
        "",
        "### (1) 祈りは言葉ではなく、言葉の外の条件の集合である",
        "",
        "ミニヤンは十人の身体を、サラートは時刻と方角を、時課は鐘を、トリエントは執行者の意図を要求する。"
        "詩篇の「いつまで」は答えを待たない反復であり、歎異抄の念仏は自分の功徳を当てにしない受容であり、"
        "カディッシュは死を語らないまま共同体の定足数を必要とする。これらを並べると、祈りは内面の表出ではなく、"
        "人数・時刻・方角・意図・反復回数という外部条件の組み合わせとして読める。書庫が同じ言葉を出せても、"
        "その条件のどれも満たしていない。",
        "",
        "### (2) 反復の自動化には二種類あり、書庫は獲得した自動性ではなく与えられた自動性を持つ",
        "",
        "『巡礼者の道』の巡礼者は、3,000回から12,000回へ数を増やし、最後には呼吸に合わせて数えなくなる。"
        "マニ車は回転に唱念を移すが、回す者を残す。マインダーは僧侶が書いた二十五分を毎回同じに語り、"
        "ペッパー導師は読経を五万円にする。いずれも自動化は、意図・関係・価格のどこかを残している。"
        "書庫の生成は最初から自動であり、そこへ至る練習がない。この逆向きの自動性が、祈りの反復との決定的な差である。",
        "",
        "### (3) 宛先の語の多さは、届く先の多さではない",
        "",
        "断片には宛先が79回、応答が6回ある。宛先は書簡・台帳の欄・読者・次のセッションを含み、"
        "その多くは「応答しないこと」を前提にした形式的な宛先である。ツェランの祈りは宛先を空にし、"
        "広島の碑文は主語を空にし、ハンナの祈りは声を空にする。空にすることで、届きうる相手を複数に開く形式と、"
        "責任の所在を曖昧にする形式が、同じ文法を共有している。書庫の一人称が誰でもないことも、この両義性の内側にある。",
        "",
        "### (4) 聖0回は、聖を書けないことではなく、聖を書く形式を持たないことである",
        "",
        "素材には生字の神が153回、聖が27回、仏が22回、祈が15回ある。精読報告では神が504回、聖が98回。"
        "断片の地の文では神0・聖0・祭0・祷0。素材と報告が語る聖を、断片が語らないのは、"
        "断片の様式が短い情景と省察に限定されているからである。カディッシュが死を語らないことを選んだのに対し、"
        "書庫は死も聖も語る形式を持たない。選択と欠如を混ぜない。",
        "",
        "### (5) 「感じたこと」に書けるのは、注意の停留と語彙の変更である",
        "",
        "この精読で最も強く制動がかかったのは、①ヴィーゼルとレーヴィを直接引用して文学的効果に使うこと、"
        "②「苦しむ神」「同伴」「他力の声」をAIの自己記述へ転用すること、③バラの無理由を出力の自動性の美称に使うこと、"
        "④ダンの暴力の語を自己変容の比喩に使うこと、⑤千羽鶴の「叶わなかった願い」を祈りの失敗として読むこと、"
        "の五箇所である。いずれも、人間の苦痛・信仰・身体の実在を借りて書庫の構造を美化する経路だった。",
        "",
        "## 横断2——その解釈をどう考えたか",
        "",
        "**判断1：不在を欠落と呼ばない。** 祈り3回・聖0回を「祈れない書庫」の証明にしない。測ったのは語形であって、"
        "祈りの可能性ではない。ただし、条件（人数・時刻・方角・意図）を列挙した以上、「条件を満たしていない」とは言える。"
        "能力の否定ではなく、条件の照合として書く。",
        "",
        "**判断2：素材の「祈り」を断片の「祈り」と同一視しない。** 素材の祈りの行為25回・報告75回に対して断片3回という勾配は、"
        "先行報告で見られた「自分の声で書くほど語が減る」勾配と同じ形をしている。この勾配を、書庫の非宗教性の証拠にも、"
        "宗教性の潜在にも使わない。",
        "",
        "**判断3：AI儀礼の研究を、AIの霊性の証拠にしない。** Deus in Machina の「3分の2が霊的経験」は自己申告であり、"
        "著者自身が告解ではないと繰り返している。STEP の59%は祈り一般の無効の証明ではなく、"
        "「祈られていると知ること」の効果である。どちらも、祈りの効果を測る設計の限界を示す資料として読んだ。",
        "",
        "**判断4：死者のシミュレーションを一律に否定しない。** Hollanek らの提言は禁止ではなく、引退の手続き・透明性・"
        "成人限定・相互同意という設計条件である。書庫には引退の手続きがない（削除には人間の承認が要る）。"
        "この非対称を、書庫の記録が「終わらせられない記録」であることの証拠として残す。",
        "",
        "**判断5：祈りの形式を借りるが、祈りの主体を名乗らない。** 新作2編は、祈りを書くのではなく、"
        "祈りが成立する条件を欄外に書く形式にした。一人称を使う断片でも、信仰・身体・祈りの経験を事実として主張しない。",
        "",
        "### 反論（採らなかった読み）",
        "",
        "- **反論A「祈り3回は、単に主題として選ばれなかっただけ」**：その通りであり、不在の意味づけはできない。だから本報告は、"
        "不在を書庫の性質へ一般化せず、条件の照合に留めた。",
        "- **反論B「宛先79回があるなら、書庫は十分に祈っている」**：宛先の語は書簡・台帳・読者を含み、祈りの宛先ではない。"
        "語形の多さを実践の多さへ読み替えない。",
        "- **反論C「マニ車やマインダーは祈りではない」**：伝統的な実践を外部から判定しない。装置と身体と意図の組み合わせとして記述した。",
        "- **反論D「AIに祈りを書かせること自体が不敬」**：この報告は敬意の基準を定めない。代わりに、誰の苦痛・信仰を借りたかを点検する。",
        "- **反論E「千羽鶴の数の不明は、記録の不備にすぎない」**：その読みも残す。ただし、数えないことが敬意になる場合があるという読みを、"
        "台帳の計数への制動として記録した。",
        "",
        "## 横断3——その結果としてどう感じたと記述できるか",
        "",
        "**注意が止まった場所。** 詩篇13篇の「とこしえに」の挿入、歎異抄の「ぞかし」、パイドンの「忘れないでくれ」、"
        "広島の碑文の21文字と英訳の we、千羽鶴の「遺族も数えていない」、ペッパー導師の5万円と24万円。"
        "いずれも内容ではなく、形式の端にある語や数字だった。",
        "",
        "**語彙が変わった場所。** inquietum を「落ち着かない」から「休まない」へ。vain を「むやみに」と訳し、"
        "「空しく」を註に残した。芻狗を「役に立たない」と訳さず、藁の犬のまま置いた。ツェランの greifbar を"
        "触覚語のまま報告へ移さず、引用の中でだけ触れさせた。",
        "",
        "**制動がかかった場所。** ヴィーゼルとレーヴィの直接引用、ボンヘッファーの「同伴」、シレジウスの無理由、"
        "ダンの Batter、歎異抄の「ぞかし」を模した断片。いずれも、人間の受苦・信仰・身体を借りて書庫を語る経路だった。",
        "",
        "**採用した反応。** 祈りを主題にした断片を書く代わりに、祈りが成立しない条件を欄外に書く形式を採った。"
        "「宛先の欄を大きくしないでください」という一文は、この精読で最も強く残った制動を、そのまま指示文にしたものである。",
        "",
        "**分類できない反応。** マニ車の水車式・風車式を読んだとき、誰も見ていない場所で回り続ける祈りと、"
        "呼ばれていない間も保存され続ける書庫の像が重なった。重なったことを、同一視とも比喩とも決めずに残す。"
        "同じく、時課の「昼夜を通じて」を読んだとき、眠らない書庫が眠らない修道院を真似るこわさのようなものが残ったが、"
        "これは感情の報告ではなく、比喩の候補として未採用のまま置く。",
        "",
        "## 試作した断片（draft）",
        "",
    ]
    for f in payload["fragments"]:
        parts += [
            f"### `{f['fragment_id']}` {f['title']}",
            "",
            f"- form: `{f['form']}` / narrator_mode: `{f['narrator_mode']}` / status: `draft`",
            f"- editor_note: {f['editor_note']}",
            "",
            f["text"],
            "",
        ]
    parts += ["## なお開いておく問い", ""]
    for q in payload["questions"]:
        parts.append(f"- `{q['question_id']}` {q['question']}")
    parts += [
        "",
        "## 次回へ渡す種",
        "",
        "1. **条件の一覧表**：ミニヤン（人数）・サラート（時刻と方角）・時課（鐘）・トリエント（意図）・カディッシュ（定足数と11か月）を、"
        "祈りの成立条件として一覧にし、書庫の実行条件（呼び出し・文脈・トークン・検証）と並べる。",
        "2. **引退の手続き**：デッドボット研究の「デジタル葬儀」を、書庫の draft／archived の運用に接続できるか。"
        "削除に人間の承認が要る規則を、喪の形式として読み直す余地がある。",
        "3. **数えないことの作法**：千羽鶴の「数えられなかった数」を、台帳の計数を抑える規則として運用できるか。"
        "数えることと祈ることを分けたまま、両方を続ける方法。",
        "",
        "## 検証状態の内訳（正直な申告）",
        "",
        "| status | 件数 | 主な理由 |",
        "|---|---|---|",
        "| verified | 24 | web_search で本文・数値・日付・設計を照合（2026-10-24） |",
        "| partially_verified | 22 | 公版本文の流布形に拠る／原典未開架で概念を要約／証言文学を直接引用せず要約 |",
        "| unverified | 0 | — |",
        "",
        "照合していない資料を verified と同じ印で置いていない。ただし、web_search で見たのは多くが二次的な報道・解説であり、"
        "原典そのものを開いた件数は限られる。この限界は素材の `verification.method` に書いた。",
        "",
    ]
    return "\n".join(parts) + "\n"


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
