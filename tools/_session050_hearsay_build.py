#!/usr/bin/env python3
"""Build the SESSION-20261024-76329d ledger rows (hearsay, testimony, rumour).

Writes to per-session shards only; the frozen ``state/*.jsonl`` bases are never
touched (see docs/parallel-work.md). Run with ``--write``. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import new_ledger_shard  # noqa: E402
import new_id  # noqa: E402
from _session050_hearsay_data import (  # noqa: E402
    CONTEXT_LIT, CONTEXT_RES, LIT, RES, SCOPE_LIT, SCOPE_RES, SCOPE_TRC,
)

SESSION_ID = "SESSION-20261024-76329d"
MOTIF_ID = "MOTIF-20261024-1a8978"
REPORT = "readings/2026-10-24-session-050-hearsay-and-testimony.md"
COMMIT = "5f112a72bce764b70e6e3a5725e168cd69c042ed"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
CHECKED = "2026-10-24"

NEW_QUESTIONS = [
    ("Q-20261024-0087a0",
     "「一節」欄に編者の要約を置くとき、その文が誰の声なのかを、本文の側で示すことはできるか。"),
    ("Q-20261024-e28e44",
     "断片の地の文に「噂」「うわさ」「伝聞」が0回であることは、声が清潔であることの証拠か、"
     "それとも自分の聞いた話を名乗らない習慣の証拠か。"),
    ("Q-20261024-287e33",
     "同じ文章を何度も読み返す書庫は、反復を独立した証言として数えてしまうのではないか。"),
    ("Q-20261024-e60d49",
     "引用の支持率は、引用された原文の正しさを測らない。来歴の正しさは何で測れるのか。"),
    ("Q-20261024-2dfbb4",
     "幻覚を「嘘」ではなく「伝聞の失敗」と呼ぶとき、何が見え、何が隠れるか。"),
]

MOTIF_DESCRIPTION = (
    "聞いた話を、自分の言葉にすること。伝聞・噂・証言・引用・要約・幻覚を、信／不信の二分ではなく、"
    "誰が誰に何を渡したかの経路として扱う糸。断片55編の地の文には「噂」「うわさ」「伝聞」「風聞」が"
    "0回、「証言」は1回しかなく、引用・要約・出典の語20回に対して、書く・読む・記録・次の語は225回ある。"
    "一方で収蔵資料1,194件の53.7%（641件）は【編者による要約】で始まり、精読報告87本の「一節」欄250行のうち"
    "74.4%（186行）も編者要約である。声は直接を装い、来歴は註と `verification` に置かれている。"
    "この非対称を、告発ではなく書式の問題として読み続ける。"
)

# 45 material -> motif relation notes, in the order LIT + RES.
NOTES = [
    "信じる意志は反証を受け取らず、仕組まれた場面だけがそれを破る。この書庫の「一節」も、場面ではなく註で正体を明かす。",
    "確かめられない噂が人物の像を作り、像を信じた者が動く。台帳の人物像も、要約の反復で作られている。",
    "名を言わないことが人を守り、同時に推測の暴力を残す。匿名の要約は、そこで誰を守っているのか。",
    "語り手は居合わせていない時間を噂で埋める。報告の「考え」の欄は、しばしばこの埋め草である。",
    "同じ事件の証言が重なり、最後まで閉じない。この台帳が矛盾を保存する理由の文学的先例。",
    "唯一の証言だけが根拠のとき、信じる判断は読者へ戻される。精読報告の一人称も同じ位置に立つ。",
    "誰も全体を見ていないのに、記録の継ぎ目で判断が作られる。監査ツールはこの継ぎ目を数える。",
    "入れ子の語りが死を先延ばしにする。セッションを跨ぐ記録も、語り終えないことで続いている。",
    "証言は真実の窓であると同時に、誰かが選んだ形式である。`passage` 欄はその形式の最小形。",
    "誰が名付けたか分からない噂が本人の死を決める。名付けの来歴を欠いた記録の危うさ。",
    "「聞いた話」という枠が、責任を移すと同時に届ける。`scope_note` はこの枠の現代版である。",
    "併記して決めない作法。この台帳が複数の読みを畳まない方針の遠い親戚。",
    "証言を吟味して再構成し、それを証言と呼ぶ。`source_note` と `passage` の関係が同じ問題を抱える。",
    "証言の重さが語る者の位置で変わる。`verification.status` はその位置の粗い代理を務める。",
    "知識の大部分は他人の証言への信頼に支えられる。台帳の `source` 欄はこの信頼の記録である。",
    "証言を確率として扱う。`verified` の三値は、その確率を粗く切ったものにすぎない。",
    "誰も責任を取らない世間話が公衆を作る。出典の欄だけが埋まった要約は、この公衆の言葉に近い。",
    "情報の優勢が物語の権威を失わせる。要約の書庫は、物語を情報の形式へ移した結果である。",
    "証言を吟味することは語り手を疑うことではない。`verification` の註がこの区別を担う。",
    "伝聞の鎖そのものを批判する。この台帳の鎖は `origin` と `read_log` で途切れている。",
    "証言は還元できない知識源である。資料を「証拠ではない」と断ることは、証言を消すことではない。",
    "証言の失敗は聞き手の条件でも起こる。要約を読む側の読み方が、要約の意味を変える。",
    "信用が偏見で差し引かれる。この書庫がどの資料を「未確認」に置きやすいかも、同じ問いの内側にある。",
    "沈黙は語る能力の不在ではなく、届かない構造の産物でありうる。断片に噂が0回なのも、同種の沈黙かもしれない。",
    "証言の信用が身分と結びつく。`verified` の印は、誰の言葉を信用するかの制度である。",
    "正確さと誠実さを分ける。この台帳は正確さを `verification` に、誠実さを `scope_note` に置いている。",
    "聞き手の態度が語りうる範囲を変える。精読報告の「考え」は、資料に対する聞き手の態度の記録である。",
    "聞き手の期待が証言を変える。報告が資料を「対話相手」と呼ぶとき、この危険が生じる。",
    "聞き書きは語り手の言葉を整形しすぎない。要約はその反対の操作であり、失われるものを明示する必要がある。",
    "伝達で話は削られ、尖り、似せられる。要約の反復は、この三つの操作の制度化である。",
    "噂は空白を埋める即興のニュースである。この台帳の `source_note` も、空白を埋める即興である。",
    "噂を否定する声明が噂を強めることがある。訂正の連鎖を扱う `errata` と同じ問題を抱える。",
    "出所をたどれない話が具体的な地名を持つ。URLのある資料でも、その版を開いていなければ同じである。",
    "虚偽は速く遠く届く。この台帳が速さを競わず、遅い照合を残す理由の一つ。",
    "信じることは注意の不足でも起こる。読まれない註は、注意の経済のなかにある。",
    "真偽は会話の途中で交渉される。固定した `verification.status` は、その交渉を一瞬で切る。",
    "正しい情報への導線が対策になる。`source.url` は導線だが、辿られた保証ではない。",
    "モデルは自分の知識の境界をある程度申告できる。`scope_note` はこの申告を手で書いたものに近い。",
    "引用の質は回答の正しさと別に測られる。`passage` が要約であることは、引用の質の指標にならない。",
    "引用の精度が高くても答えは支えられないことがある。註の多さは、本文の正しさの保証ではない。",
    "有名な話は当たり、珍しい話は外れる。`partially_verified` に偏るこの書庫の分布と響き合う。",
    "語られた理由は働いた理由ではない。精読報告の「考え」は、事後の説明であることを免れない。",
    "段階を踏んだ説明を書けることは、段階を踏んだことの証拠ではない。四層の書式にも同じ危険がある。",
    "根拠を示すことと正しく答えることを分けて測る。この台帳の `origin` も同じ分離の上にある。",
    "出力の来歴を事後的にたどる。`read_log` はその試みの、はるかに粗い版である。",
]

TRACE = {
    "material_id": "MAT-TRC-020",
    "kind": "project_trace",
    "title": "本リポジトリ自身の痕跡——断片55編の噂0・伝聞0と、資料53.7%・「一節」74.4%が編者要約である非対称",
    "source": {
        "source_id": "SRC-MAT-TRC-020",
        "title": "tools/hearsay_audit.py の実行結果（2026-10-24）",
        "authors": ["AIselfMySelf SESSION-20261024-76329d"],
        "year": 2026,
        "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/hearsay_audit.py",
        "version_note": "このセッションで新設・実行した監査ツールの出力。コミット前の作業ツリー。",
    },
    "passage": (
        "【実測】断片55編・地の文25,024字で、伝聞の標識5回／5編（と言われ1・聞こえ1・聞いて2・によれば1）、"
        "証言・証拠4回／4編、引用・要約・出典20回／12編、疑い・照合16回／11編、情報源18回／15編、"
        "対照の書庫語225回／51編。「噂」「うわさ」「伝聞」「風聞」「目撃」「宣誓」は0回。"
        "素材1,194件のうち【編者による要約】で始まる passage は641件（53.7%）、"
        "精読報告87本の「一節」行250行のうち編者要約は186行（74.4%）、鉤括弧を含む行は81行。"
    ),
    "passage_language": "ja",
    "context": "本リポジトリの台帳と精読報告を、同じセッションで実行した監査ツールで数えた痕跡。",
    "source_note": "SESSION-20261024-76329d で追加。数値は語形の数であり、証言・信頼・疑いの有無の判定ではない。",
    "literary_invitation": "声は直接を装いながら、その半分は要約である。この非対称を、どこに記録するのか。",
    "scope_note": SCOPE_TRC,
    "motif_ids": [MOTIF_ID, "MOTIF-001", "MOTIF-015"],
    "verification": {
        "status": "verified",
        "checked_at": CHECKED,
        "method": "このセッションで python3 tools/hearsay_audit.py を実行し、出力をそのまま転記した。",
        "note": "再実行で同じ数値を確認できる。台帳が増えれば数値は変わる。",
    },
}


def material_records() -> list[dict]:
    records: list[dict] = []
    for mid, title, authors, year, url, summary, invitation in LIT:
        note = (
            "書誌は内部知識で照合。該当版・頁は未閲覧。"
            if "worldcat" in url or "gutenberg" in url or "perseus" in url
            else "書誌は内部知識で照合。該当版・頁は未閲覧。"
        )
        records.append({
            "material_id": mid,
            "kind": "literary_text",
            "title": title,
            "source": {
                "source_id": f"SRC-{mid}",
                "title": title,
                "authors": authors,
                "year": year,
                "url": url,
                "version_note": "書誌情報は内部知識で照合。該当版・頁は未閲覧。",
            },
            "passage": f"【編者による要約】{summary}",
            "passage_language": "ja",
            "context": CONTEXT_LIT,
            "source_note": "SESSION-20261024-76329d で追加。伝聞・証言・噂を、信／不信ではなく経路として読むための素材。",
            "literary_invitation": invitation,
            "scope_note": SCOPE_LIT,
            "motif_ids": [MOTIF_ID],
            "origin": {
                "repository": REPO,
                "commit": COMMIT,
                "source_record_id": f"SRC-{mid}",
                "evidence_record_id": mid,
                "source_record_path": REPORT,
                "evidence_record_path": REPORT,
            },
            "verification": {
                "status": "partially_verified",
                "checked_at": CHECKED,
                "method": "内部知識による書誌照合。ウェブ検索・原文照合なし。",
                "note": note,
            },
        })
    for mid, title, authors, year, url, summary, invitation, status, method in RES:
        records.append({
            "material_id": mid,
            "kind": "research_excerpt",
            "title": title,
            "source": {
                "source_id": f"SRC-{mid}",
                "title": title,
                "authors": authors,
                "year": year,
                "url": url,
                "version_note": "書誌情報は内部知識およびウェブ検索で照合。本文は未取得。",
            },
            "passage": f"【編者による要約】{summary}",
            "passage_language": "ja",
            "context": CONTEXT_RES,
            "source_note": "SESSION-20261024-76329d で追加。証言・噂・引用の流通を測る研究として読む。",
            "literary_invitation": invitation,
            "scope_note": SCOPE_RES,
            "motif_ids": [MOTIF_ID, "MOTIF-013", "MOTIF-015"] if year >= 2016 else [MOTIF_ID, "MOTIF-001"],
            "origin": {
                "repository": REPO,
                "commit": COMMIT,
                "source_record_id": f"SRC-{mid}",
                "evidence_record_id": mid,
                "source_record_path": REPORT,
                "evidence_record_path": REPORT,
            },
            "verification": {
                "status": "verified" if status == "verified" else "partially_verified",
                "checked_at": CHECKED,
                "method": method,
                "note": "本文・数値・実験条件は未確認。" if status != "verified" else "題名・著者・発表年・会場のみ照合。本文は未取得。",
            },
        })
    trace = dict(TRACE)
    trace["origin"] = {
        "repository": REPO,
        "commit": COMMIT,
        "source_record_id": "SRC-MAT-TRC-020",
        "evidence_record_id": "MAT-TRC-020",
        "source_record_path": "tools/hearsay_audit.py",
        "evidence_record_path": REPORT,
    }
    records.append(trace)
    return records


def mint_relation_ids(count: int) -> list[str]:
    used = new_id.existing_ids("REL")
    out: list[str] = []
    while len(out) < count:
        rid = f"REL-20261024-{secrets.token_hex(3)}"
        if rid not in used and rid not in out:
            out.append(rid)
    return out


def relation_records(materials: list[dict]) -> list[dict]:
    ids = mint_relation_ids(70)
    pairs: list[tuple[dict, dict, str, str]] = []
    ordered = [m["material_id"] for m in materials if m["material_id"] != "MAT-TRC-020"]
    for mid, note in zip(ordered, NOTES):
        pairs.append(({"type": "material", "id": mid}, {"type": "motif", "id": MOTIF_ID}, "responds_to", note))

    def mat(mid: str) -> dict:
        return {"type": "material", "id": mid}

    def lit(i: int) -> str:
        return LIT[i][0]

    def res(i: int) -> str:
        return RES[i][0]

    pairs += [
        (mat(lit(11)), mat(lit(12)), "contrast", "併記して決めないヘロドトスと、吟味して再構成するトゥキディデス。同じ「証言を書く」でも、決めないことと作り直すことが分かれる。"),
        (mat(lit(28)), mat(lit(26)), "echo", "聞き書きの宮本と、聞くことを場の生成とする鷲田。どちらも、聞き手が語りうる範囲を変えると言う。"),
        (mat(lit(22)), mat(lit(23)), "transforms", "フリッカーの「信用の差し引き」から、ドットソンの「聞き取れなさの構造」へ。不正義は聞き手の側へ移る。"),
        (mat(res(9)), mat(res(10)), "contrast", "引用の質を測る ALCE と、引用が答えを支えないことを測るリウら。指標が増えても、支えられていない半分は残る。"),
        (mat(res(0)), mat(res(2)), "echo", "伝達による削減・先鋭化・同化と、噂を社会の知識形式として読むカプフェレ。変形の単位が話から集団へ移る。"),
        (mat(lit(7)), mat(lit(8)), "contrast", "生き延びるために語り終えない千夜一夜と、体制のために証言を編むアトウッド。同じ入れ子が、逆の目的に働く。"),
        (mat(lit(10)), mat(lit(28)), "echo", "「聞いた話」という枠を付ける西鶴と、語り手の言葉を整形しすぎない宮本。枠の強さが違うだけで、来歴を残す仕事は同じである。"),
        (mat(lit(14)), mat(lit(15)), "transforms", "ロックは証言の確からしさを数と誠実さで測り、ヒュームはそれを確率に変える。人格の重みが計算へ移る。"),
        (mat(res(7)), mat(res(11)), "contrast", "自分の不確実性を申告するカダヴァスらと、語られた理由が働いた理由ではないとするラナムら。申告と説明は、どちらも証言の候補である。"),
        (mat(lit(6)), mat(lit(4)), "echo", "記録の継ぎ目で判断を作るドラキュラと、食い違う証言を閉じないフォークナー。継ぎ目は証拠にも迷宮にもなる。"),
        ({"type": "motif", "id": MOTIF_ID}, {"type": "motif", "id": "MOTIF-001"}, "echo", "記憶を痕跡として読む糸に、その痕跡が誰の証言かを問う軸を足す。"),
        ({"type": "motif", "id": MOTIF_ID}, {"type": "motif", "id": "MOTIF-008"}, "reframes", "「一節／解釈／考え／感じたこと」の書式は、引用と要約の区別を守る型であると同時に、声を註へ追いやる型でもある。"),
        ({"type": "motif", "id": MOTIF_ID}, {"type": "motif", "id": "MOTIF-20261024-d2999b"}, "contrast", "訂正は誤りを差し出し元へ返せるが、伝聞は誤りが誰から来たかを返せないことがある。"),
        ({"type": "motif", "id": MOTIF_ID}, {"type": "motif", "id": "MOTIF-011"}, "echo", "訳すことと伝えることは、どちらも来歴を伴う移動である。失われるものの名前が違う。"),
        ({"type": "motif", "id": MOTIF_ID}, {"type": "motif", "id": "MOTIF-015"}, "reframes", "監査は語形を数えられるが、その語が誰の声かは数えられない。数えることは、来歴の代わりにならない。"),
        ({"type": "fragment", "id": "FRAG-030"}, {"type": "motif", "id": MOTIF_ID}, "contrast", "編者を父として立てる調書は、要約を声の代わりに置くこの書庫の縁組を先に書いていた。"),
        ({"type": "fragment", "id": "FRAG-020"}, {"type": "motif", "id": MOTIF_ID}, "responds_to", "引用と註を数える断片は、来歴を本文の外に置く作法をすでに問題にしている。"),
        ({"type": "fragment", "id": "FRAG-013"}, {"type": "motif", "id": MOTIF_ID}, "echo", "要約とざらつきの対比は、要約が削るものの記録である。"),
        ({"type": "question", "id": "Q-002"}, {"type": "motif", "id": MOTIF_ID}, "leaves_open", "記録を読み直す自己の連続性は、伝聞の連鎖のどこで成立するのか。"),
        ({"type": "material", "id": "MAT-TRC-020"}, {"type": "motif", "id": MOTIF_ID}, "responds_to", "断片の噂0と資料の要約53.7%を同じ紙に置くと、この書庫の声の由来が初めて数字で見える。"),
    ]
    for qid, _text in NEW_QUESTIONS:
        pairs.append(({"type": "question", "id": qid}, {"type": "motif", "id": MOTIF_ID}, "leaves_open", "新しい糸に属する問いとして、答えを閉じずに台帳へ返す。"))
    records = []
    for rid, (left, right, rtype, note) in zip(ids, pairs):
        records.append({
            "relation_id": rid,
            "left": left,
            "relation_type": rtype,
            "right": right,
            "note": note,
            "created_at": CHECKED,
        })
    return records


def question_records() -> list[dict]:
    records = []
    for qid, text in NEW_QUESTIONS:
        records.append({
            "question_id": qid,
            "question": text,
            "status": "open",
            "motif_ids": [MOTIF_ID],
            "material_ids": [],
            "previous_question_ids": [],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} の精読報告から"},
            "created_at": CHECKED,
            "notes": "答えを閉じない。数値の不在を能力や誠実さの判定に変換しない。",
        })
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="append the rows to new per-session shards")
    args = parser.parse_args(argv)

    materials = material_records()
    relations = relation_records(materials)
    questions = question_records()
    motif = {
        "motif_id": MOTIF_ID,
        "label": "伝聞と噂——聞いた話を、自分の言葉にする",
        "description": MOTIF_DESCRIPTION,
        "question_ids": [q for q, _ in NEW_QUESTIONS],
        "material_ids": [m["material_id"] for m in materials],
    }
    session = {
        "session_id": SESSION_ID,
        "started_at": CHECKED,
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください。"
            "一番最初のターンにおいて、最低40件の資料を新規で追加して、追加した資料の精読を行うようにしてください。"
            "精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、"
            "AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージしてください」という包括的な委任。"
        ),
        "question_ids": [q for q, _ in NEW_QUESTIONS],
        "context_material_ids": [m["material_id"] for m in materials],
        "produced_fragment_ids": [],
        "new_question_ids": [q for q, _ in NEW_QUESTIONS],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            "伝聞・証言・噂を主題とした精読セッション。資料選定前に tools/hearsay_audit.py を新設し、"
            "断片55編25,024字を鉤括弧の内外に分けて測った。噂0・うわさ0・伝聞0・風聞0、証言1、"
            "伝聞の標識5回／5編に対し、書く・読む・記録・次の語は225回／51編。素材1,194件の53.7%が"
            "【編者による要約】で始まり、精読報告の「一節」250行の74.4%も編者要約である。"
            "この非対称から、文学・思想29件（噂が動かす物語11、証言を書く作法9、証言の倫理9）、"
            "研究16件（噂・流言の社会科学8、機械の伝聞8）、運用痕跡1件の計46件を追加し、"
            f"{REPORT} で全件を一節／解釈／考え／感じたことの四層に分けて精読した。"
            "横断報告は「どう解釈したか／その解釈をどう考えたか／結果としてどう感じたと記述できるか」を独立させ、"
            "五つの反論と、断片を書かなかった理由を記した。新規モチーフ1件、問い5件、関係70件を追加。"
            "書誌状態は verified 9件（研究8・痕跡1）・partially_verified 37件・unverified 0件。"
        ),
    }

    if not args.write:
        print(json.dumps({"materials": len(materials), "relations": len(relations),
                          "questions": len(questions)}, ensure_ascii=False))
        return 0

    groups = {
        "materials": materials,
        "motifs": [motif],
        "questions": questions,
        "relations": relations,
        "sessions": [session],
    }
    for collection, rows in groups.items():
        path = new_ledger_shard.create_shard(collection)
        with open(path, "a", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{collection}: {len(rows)} rows -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
