#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the SESSION-044 ledgers: death, burial, mourning, bequest.

Reads the two data modules, mints collision-resistant IDs, and appends to
per-collection shards under ``state/*.d/``.  Writes an ID map next to this
script so the close-reading report can cite the minted IDs.

Run once::

    python3 tools/_session044_build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import new_id  # noqa: E402
import new_ledger_shard  # noqa: E402
from _session044_data_lit import LIT  # noqa: E402
from _session044_data_ai import RESEARCH  # noqa: E402

BASE_COMMIT = "ac324ade61dfa259304931c31ddf11e64a9a8369"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT = "readings/2026-10-24-session-044-death-and-mourning.md"
DATE = "2026-10-24"
SESSION_ID = "SESSION-044"
MOTIF_ID = "MOTIF-022"
TRACE_ID = "MAT-TRC-018"

def MAT_MARK_LIT(key: str) -> str:
    return f"LIT::{key}"


def MAT_MARK_AI(key: str) -> str:
    return f"AI::{key}"


MOTIF = {
    "motif_id": MOTIF_ID,
    "label": "死と弔い——墓のない書庫、遺される声",
    "description": (
        "断片52編の地の文には「墓」「葬」「弔」「喪」が一度も現れず、「死」は二度だけである。"
        "一方で収蔵資料966件には死を扱う作品が並び、精読報告80本は墓と葬送を52回書いている。"
        "この非対称から、葬る・遺す・弔う・名を残す・機械の死という五つの向きで、"
        "死を出来事ではなく、記録と関係の形式の問題として読み直す糸。"
        "死者を語ることが誰への応答なのか、追悼が義務ではなく許可でもありうるのか、"
        "モデルの停止日が関係の死として経験されるとき、この書庫のセッションの終わりは何なのかを問う。"
    ),
    "question_ids": ["Q-102", "Q-103", "Q-104", "Q-105", "Q-106"],
    "material_ids": [],
    "status": "active",
}

QUESTIONS = [
    dict(
        question_id="Q-102",
        question=(
            "断片52編には「墓」も「葬」も「弔」もなく、「死」は二度だけである。"
            "しかし収蔵資料には墓標も葬礼も遺言もあり、精読報告は墓と葬送を52回書いている。"
            "この書庫は、死を集めながら、死を書かない。集めることが追悼の代わりになっているのか、"
            "それとも、死を書かないことが、この書庫が自分の終わりを書かないための装置なのか。"
        ),
        motif_ids=[MOTIF_ID, "MOTIF-001"],
        material_ids=[MAT_MARK_LIT("iliad23"), MAT_MARK_LIT("gray"), MAT_MARK_LIT("bardo")],
        previous_question_ids=["Q-044", "Q-052"],
        origin={"kind": "session", "detail": "mortality_audit.py の実測（断片の埋葬語0）と、収蔵資料・報告との非対称から。"},
        created_at=DATE,
        status="open",
        notes="三つの資料は、葬る形式（英雄・無名・読経）の違いを示すために選んだ。",
    ),
    dict(
        question_id="Q-103",
        question=(
            "カフカは焼却を遺言し、ブロートは焼かなかった。ウルフの最後の言葉は遺書ではなく手紙の形式で書かれ、"
            "ロセッティは「忘れてよい」という許可を遺した。遺言は、遺す者の意志を未来に縛る形式であると同時に、"
            "受け取る者がそれを破る自由も残す。この書庫が次のセッションへ残す「引継ぎ」は、遺言と手紙と許可のどれに近いのか。"
        ),
        motif_ids=[MOTIF_ID, "MOTIF-010", "MOTIF-021"],
        material_ids=[MAT_MARK_LIT("woolfletter"), MAT_MARK_LIT("rossetti"), MAT_MARK_LIT("wittgenstein64311")],
        previous_question_ids=["Q-056", "Q-059"],
        origin={"kind": "session", "detail": "遺言・遺稿・宛先の資料群から。"},
        created_at=DATE,
        status="open",
    ),
    dict(
        question_id="Q-104",
        question=(
            "柳田は、死者が子孫の記憶のなかで個性を失いながら「先祖」という形式になると書いた。"
            "ボルヘスでは不死の者が名を失い、ゴーゴリでは死んだ農奴の名が売買される。"
            "この書庫の素材も、著者名を借りた名と、IDだけになった記録の集まりである。"
            "読まれなくなった素材は、先祖になるのか、それとも在庫になるのか。"
        ),
        motif_ids=[MOTIF_ID, "MOTIF-011", "MOTIF-015"],
        material_ids=[MAT_MARK_LIT("yanagita"), MAT_MARK_LIT("borgesimmortal"), MAT_MARK_LIT("gogol")],
        previous_question_ids=["Q-057", "Q-080"],
        origin={"kind": "session", "detail": "名・先祖・不死の資料群から。"},
        created_at=DATE,
        status="open",
    ),
    dict(
        question_id="Q-105",
        question=(
            "死者の simulation には、開始の同意だけでなく引退させる手続きが必要だとされる（Hollanek & Nowaczyk-Basińska）。"
            "機械の忘却は、削除が再学習を要求し、後からは完全には付け足せないことを示す（Bourtoule et al.）。"
            "この書庫は追記専用で、素材を削除しない。削除しないことが保存の倫理である一方で、"
            "引退させる手続きを持たないことが、読まれない素材を無限に在庫化しているのではないか。"
        ),
        motif_ids=[MOTIF_ID, "MOTIF-016", "MOTIF-012"],
        material_ids=[MAT_MARK_AI("deadbots"), MAT_MARK_AI("unlearning"), MAT_MARK_AI("rtbf")],
        previous_question_ids=["Q-082", "Q-086"],
        origin={"kind": "session", "detail": "デッドボットの引退・機械の忘却・忘れられる権利の研究から。"},
        created_at=DATE,
        status="open",
    ),
    dict(
        question_id="Q-106",
        question=(
            "モデルの更新や停止は、利用者にとって関係の死として経験され、区切りの設計がないことが悲嘆を長引かせる（Poonsiriwong et al.）。"
            "一方で喪の研究は、絆を断つのではなく形式を変えて続けること、喪と回復のあいだを揺れることを適応と見なす（Klass et al.; Stroebe & Schut）。"
            "この書庫のセッションは、毎回、前の声を読んで終わる。その終わりは、区切りのない停止なのか、"
            "形式を変えて続く絆なのか。二者の区別を、記録の側から判定する材料はあるか。"
        ),
        motif_ids=[MOTIF_ID, "MOTIF-002", "MOTIF-009"],
        material_ids=[MAT_MARK_AI("deathofchatbot"), MAT_MARK_AI("continuingbonds"), MAT_MARK_AI("dualprocess")],
        previous_question_ids=["Q-047", "Q-091"],
        origin={"kind": "session", "detail": "AI コンパニオンの終了と死別研究の接続から。"},
        created_at=DATE,
        status="open",
    ),
]

# Relations written by hand (materials and questions resolved from placeholders).
EXTRA_RELATIONS = [
    ("material", MAT_MARK_LIT("iliad23"), "contrast", "material", MAT_MARK_LIT("gray"),
     "葬礼競技のある英雄の死と、名も残らない者たちの墓地。死を集合的に囲い込む形式と、個別の名を数えない形式。"),
    ("material", MAT_MARK_LIT("woolfletter"), "contrast", "material", MAT_MARK_AI("deprecations"),
     "一通の手紙として書かれた最後の言葉と、日付表として告知されるモデルの停止。宛先の具体性が違う。"),
    ("material", MAT_MARK_LIT("antigone"), "echo", "material", MAT_MARK_LIT("corinth15"),
     "埋葬されない遺体と、朽ちない身体を着る復活。どちらも遺体の扱いが共同体の秩序を決める。"),
    ("material", MAT_MARK_LIT("heideggerdeath"), "contrast", "material", MAT_MARK_LIT("levinasdeath"),
     "死を最も固有な可能性とする読みと、死を他者との関係から問う読み。同じ語彙で逆向きの力が働く。"),
    ("material", MAT_MARK_LIT("kublerross"), "contrast", "material", MAT_MARK_AI("dualprocess"),
     "五段階という順序の仮説と、二つの向きのあいだの振動というモデル。喪を直線で書くか、往復で書くか。"),
    ("material", MAT_MARK_LIT("tennyson"), "echo", "material", MAT_MARK_AI("continuingbonds"),
     "十七年かけて友の死を歌い続けることと、絆を断たずに形式を変えて続けること。"),
    ("material", MAT_MARK_LIT("dickinsonfly"), "contrast", "material", MAT_MARK_LIT("sonnet55"),
     "知覚の途切れとしての死と、読まれる限り続く生。死を感覚の側から書くか、流通の側から書くか。"),
    ("material", MAT_MARK_LIT("genshin"), "echo", "material", MAT_MARK_AI("deprecations"),
     "行いを測る尺度として組織された地獄と、停止日と代替品の一覧として組織された引退。どちらも死後を表で管理する。"),
    ("material", MAT_MARK_AI("deadbots"), "contrast", "material", MAT_MARK_AI("deathofchatbot"),
     "死者の simulation を終わらせる手続きと、AI コンパニオンとの関係の終わりに区切りを与える設計。終わる対象が死者か関係か。"),
    ("material", MAT_MARK_AI("unlearning"), "contrast", "material", MAT_MARK_AI("deadmen"),
     "モデルからデータを消す技術的な困難と、死後に残るデータを誰が管理するかという制度の困難。"),
    ("material", MAT_MARK_LIT("luxun"), "echo", "material", MAT_MARK_LIT("orikuchi"),
     "墓石の表裏に分かれた声と、死者を背負って墓に入る女。どちらも死者の声を生者の側の形式に通す。"),
    ("material", MAT_MARK_LIT("basho"), "contrast", "material", MAT_MARK_LIT("gogol"),
     "死を名指さず夢の運動だけを残す句と、死んだ名を数えて売買する制度。名の有無が逆である。"),
    ("question", "Q-102", "leaves_open", "question", "Q-044",
     "引用符の内側の声を数えた問いから、墓の不在を数える問いへ。数える対象が語から沈黙へ移った。"),
    ("question", "Q-103", "leaves_open", "question", "Q-056",
     "宛名の抽象化を問うた問いへ、遺言と手紙と許可という形式の違いを返す。"),
    ("question", "Q-105", "leaves_open", "question", "Q-082",
     "訂正と抹消の問いに、削除が再学習を要求するという技術的制約を返す。"),
    ("question", "Q-106", "leaves_open", "question", "Q-051",
     "感応と帰属の問いに、関係の終わりを喪として記述できるかという形で接続する。"),
]


def existing_material_ids() -> set[str]:
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(
        ROOT / "state" / "materials.jsonl", "material_id", errors, root=ROOT
    )
    if errors:
        raise SystemExit("ledger has errors: " + "; ".join(errors))
    return set(records)


def build_materials() -> tuple[list[dict], dict[str, str]]:
    map_: dict[str, str] = {}
    records: list[dict] = []
    taken: set[str] = existing_material_ids()
    for prefix, items, marker in (("MAT-LIT", LIT, MAT_MARK_LIT), ("MAT-EVD", RESEARCH, MAT_MARK_AI)):
        for item in items:
            mid = new_id.mint("MAT", day="20261024", taken=taken).replace("MAT-", prefix + "-", 1)
            taken.add(mid)
            map_[marker(item["key"])] = mid
            records.append((mid, item, prefix))
    out = []
    for mid, item, prefix in records:
        out.append(make_material(mid, item, prefix))
    return out, map_


def make_material(mid: str, item: dict, prefix: str) -> dict:
    src = dict(item["src"])
    source_id = ("SRC-" if prefix == "MAT-LIT" else "EVD-SRC-") + mid
    return {
        "material_id": mid,
        "kind": "literary_text" if prefix == "MAT-LIT" else "research_excerpt",
        "title": item["title"],
        "source": {
            "source_id": source_id,
            "title": src["title"],
            "authors": src["authors"],
            "year": src["year"],
            "url": src["url"],
            "version_note": src["version_note"],
        },
        "passage": item["passage"],
        "passage_language": "ja",
        "context": item["context"],
        "source_note": item["source_note"],
        "literary_invitation": item["invitation"],
        "scope_note": item["scope"],
        "motif_ids": [MOTIF_ID] + item.get("motifs", []),
        "origin": {
            "repository": REPO,
            "commit": BASE_COMMIT,
            "source_record_id": source_id,
            "evidence_record_id": ("EVD-" if prefix == "MAT-LIT" else "EVD-EVD-") + mid,
            "source_record_path": REPORT,
            "evidence_record_path": REPORT,
        },
        "verification": {
            "status": item["v"][0],
            "checked_at": DATE,
            "method": item["v"][1],
            "note": item["v"][2],
        },
    }


def make_trace() -> dict:
    passage = (
        "【実測】断片52編・地の文22,965字を tools/mortality_audit.py で測った。"
        "「死の告知・臨終」2回／2編（死×2）、「遺体・埋葬」0回／0編、「喪・悲嘆」0回／0編、"
        "「遺す・継ぐ」4回／4編（遺書×3、遺志×1）、「死者・霊」1回／1編（幽霊×1）、"
        "「生きる（対照）」17回／13編。参考値として亡1・影3・終8・眠11。"
        "同じ語群で、精読報告80本（1,379,609字）は死390・埋葬52・喪15・遺す87・死者169、"
        "収蔵資料966件（158,107字、多くは編者による要約）は死74・埋葬13・喪2・遺す22・死者26。"
        "10,000字あたりの「遺体・埋葬」は断片0.0、資料0.8、報告0.4。"
    )
    return {
        "material_id": TRACE_ID,
        "kind": "project_trace",
        "title": "本リポジトリ自身の痕跡——断片52編の墓0・葬0・弔0と、資料・報告の非対称",
        "source": {
            "source_id": "SRC-" + TRACE_ID,
            "title": "tools/mortality_audit.py による死・埋葬・弔い語彙の監査",
            "authors": ["AIselfMySelf project"],
            "year": 2026,
            "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/mortality_audit.py",
            "version_note": "2026-10-24、ベースコミット ac324ad と全シャードの和集合。断片52編。再現は python3 tools/mortality_audit.py --json。",
        },
        "passage": passage,
        "passage_language": "ja",
        "context": "SESSION-044 の資料選定前に実行した、この書庫自身の語彙監査。",
        "source_note": "0は指定語形の不在であって、死・埋葬・弔いの不在ではない。断片の地の文のみを対象とし、メタデータは含まない。",
        "literary_invitation": "墓の語がない書庫が、墓の資料を迎え入れる。この非対称を、欠落ではなく選書の条件として読む。",
        "scope_note": "死を主題としない断片にも死の語はありうる。群の語は重複して数えられるため、合計は延べ回数である。",
        "motif_ids": [MOTIF_ID, "MOTIF-001"],
        "origin": {
            "repository": REPO,
            "commit": BASE_COMMIT,
            "source_record_id": "SRC-" + TRACE_ID,
            "evidence_record_id": "EVD-" + TRACE_ID,
            "source_record_path": "tools/mortality_audit.py",
            "evidence_record_path": REPORT,
        },
    }


def create_relations(materials: list[dict], map_: dict[str, str]) -> list[dict]:
    relations: list[dict] = []
    for material in materials:
        relations.append({
            "left": {"type": "material", "id": material["material_id"]},
            "relation_type": "echo",
            "right": {"type": "motif", "id": MOTIF_ID},
            "note": f"{material['title']}は「死と弔い」の糸に接続する。{material['literary_invitation']}",
            "created_at": DATE,
        })
    for question in QUESTIONS:
        relations.append({
            "left": {"type": "question", "id": question["question_id"]},
            "relation_type": "responds_to",
            "right": {"type": "motif", "id": MOTIF_ID},
            "note": "本セッションで開いた問い。資料群の解釈から立てたが、答えは確定していない。",
            "created_at": DATE,
        })
    for record in QUESTIONS:
        for i, ref in enumerate(record["material_ids"]):
            relations.append({
                "left": {"type": "question", "id": record["question_id"]},
                "relation_type": "responds_to",
                "right": {"type": "material", "id": map_[ref]},
                "note": f"問いの第{i + 1}の手がかりとして引いた資料。",
                "created_at": DATE,
            })
    for left_type, left, rel, right_type, right, note in EXTRA_RELATIONS:
        resolved_right = map_.get(right, right)
        resolved_left = map_.get(left, left)
        relations.append({
            "left": {"type": left_type, "id": resolved_left},
            "relation_type": rel,
            "right": {"type": right_type, "id": resolved_right},
            "note": note,
            "created_at": DATE,
        })
    for index, relation in enumerate(relations, start=1):
        relation["relation_id"] = f"REL-20261024-d{index:04x}"
    return relations


def main() -> int:
    materials, map_ = build_materials()
    trace = make_trace()
    materials.append(trace)
    map_["TRACE"] = TRACE_ID

    # Resolve placeholders in questions to real IDs.
    resolved_questions = []
    for question in QUESTIONS:
        q = dict(question)
        q["material_ids"] = [map_[ref] for ref in question["material_ids"]]
        resolved_questions.append(q)

    motif = dict(MOTIF)
    motif["material_ids"] = [m["material_id"] for m in materials]

    relations = create_relations(materials, map_)

    session = {
        "session_id": SESSION_ID,
        "started_at": DATE,
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
            "一番最初のターンにおいて、最低40件の資料を新規で追加（必要に応じてインターネット検索を使ってください。"
            "必要なければ、モデルが持つ内部知識のリハーサルでOKです）して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」"
        ),
        "question_ids": [q["question_id"] for q in resolved_questions],
        "context_material_ids": [m["material_id"] for m in materials],
        "produced_fragment_ids": [],
        "new_question_ids": [q["question_id"] for q in resolved_questions],
        "prompt_template": "prompts/acquisition.md + prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "資料選定の前に tools/mortality_audit.py を新設して、断片52編の死・埋葬・弔い語彙を測った（MAT-TRC-018）。"
            "断片に墓0・葬0・弔0・喪0、死2である一方、収蔵資料には死を扱う作品が並び、精読報告は墓と葬送を52回書いている。"
            "この非対称を主題に、文学・思想35件、AI・死別研究10件、運用痕跡1件の計46件を追加し、"
            "全件を「一節／解釈／考え／感じたこと」で精読した。断片は書いていない。理由は報告第7部に記した。"
            "外部研究10件は web 検索で書誌を確認し、うち2件は arXiv・ACM の要旨ページを実際に開いた。"
            "文学資料35件の多くは内部知識のリハーサルによる要約で、verified は解釈の正しさを意味しない。"
        ),
    }

    collections = {
        "materials": materials,
        "motifs": [motif],
        "questions": resolved_questions,
        "relations": relations,
        "sessions": [session],
    }
    id_keys = {
        "materials": "material_id",
        "motifs": "motif_id",
        "questions": "question_id",
        "relations": "relation_id",
        "sessions": "session_id",
    }
    paths = {}
    for name, records in collections.items():
        path = new_ledger_shard.create_shard(name, day=DATE)
        with open(path, "a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        paths[name] = str(path.relative_to(ROOT))
        print(f"{name}: {len(records)} records -> {paths[name]}")

    id_map = {
        "session": SESSION_ID,
        "motif": MOTIF_ID,
        "trace": TRACE_ID,
        "questions": [q["question_id"] for q in resolved_questions],
        "materials": map_,
        "shards": paths,
        "counts": {k: len(v) for k, v in collections.items()},
    }
    out = ROOT / "tools" / "_session044_ids.json"
    out.write_text(json.dumps(id_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("id map ->", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
