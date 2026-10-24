#!/usr/bin/env python3
"""SESSION-062: 訂正と数え直し——前セッションの記録を、開いたまま検算する。

このビルダーは `state/` を直接書き換えず、`state/<collection>.d/<stem>.jsonl` に
追記専用のシャードを書き、精読報告を `readings/` に書く。

  python3 tools/_session062_errata_build.py            # 下見（何も書かない）
  python3 tools/_session062_errata_build.py --write    # シャードと報告を書く

方針（PROJECT_CHARTER.md / CONTENT_POLICY.md）:
  * 誤りは素材本文・断片本文から消さない。判定を隣に置く（errata）。
  * 検算できないものは「検算できない」と書く。当て推量で verified にしない。
  * 「感じたこと」は身体感覚・信仰・経験の事実主張ではない。
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
import prayer_audit  # noqa: E402
from _session061_prayer_build import ITEMS, TRACE_ID, material_id  # noqa: E402

SESSION_ID = "SESSION-20261024-errata"
SHARD_STEM = "2026-10-24-c4f7b2e9d1a8"
CREATED_AT = "2026-10-24"
REPORT_REL_PATH = "readings/2026-10-24-session-062-errata-and-the-shifted-count.md"
PRIOR_SESSION = "SESSION-20261024-prayer"
PRIOR_REPORT = "readings/2026-10-24-session-061-prayer-ritual-and-the-unheard-addressee.md"

ERRATA_IDS = [f"ERR-{n:03d}" for n in range(17, 22)]


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261024-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


FRAG_ID = det_id("FRAG", "errata-clerk")
Q_NEW = det_id("Q", "who-receives-the-procedure")


def locate(title_fragment: str) -> str:
    """Return the material_id of a session-061 item by a fragment of its title."""
    for it in ITEMS:
        if title_fragment in it["title"]:
            return material_id(it)
    raise KeyError(title_fragment)


M_SILESIUS = locate("シレジウス")
M_VIETNAM = locate("ベトナム戦争慰霊碑")
M_PAD = locate("パイドン")
M_KADDISH = locate("カディッシュ")
M_PSALM = locate("詩篇")


def load(coll: str) -> dict[str, dict[str, Any]]:
    key = {
        "fragments": "fragment_id", "materials": "material_id", "motifs": "motif_id",
        "questions": "question_id", "relations": "relation_id", "sessions": "session_id",
        "read_log": "read_id", "errata": "errata_id",
    }[coll]
    errors: list[str] = []
    out = ledger_io.load_jsonl_union(ROOT / "state" / f"{coll}.jsonl", key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return out


# --------------------------------------------------------------------------
# 1. 数え直し（いまの台帳で測る）
# --------------------------------------------------------------------------

def measure_counts() -> dict[str, Any]:
    fragments = list(load("fragments").values())
    now = prayer_audit.measure_prayer_audit(fragments)
    prior = [
        f for f in fragments
        if f["fragment_id"] not in ("FRAG-20261024-e41c7a", "FRAG-20261024-a29f5b")
    ]
    before = prayer_audit.measure_prayer_audit(prior)
    errata = list(load("errata").values())
    addressee_terms = ("宛先", "宛名", "届け先", "宛て")
    errata_with_addressee = [
        e["errata_id"] for e in errata
        if any(t in json.dumps(e, ensure_ascii=False) for t in addressee_terms)
    ]
    return {
        "fragments_now": len(fragments),
        "fragments_prior": len(prior),
        "address_now": now["fragments_prose"]["groups"]["address_response"]["count"],
        "address_docs_now": now["fragments_prose"]["groups"]["address_response"]["doc_count"],
        "address_prior": before["fragments_prose"]["groups"]["address_response"]["count"],
        "address_docs_prior": before["fragments_prose"]["groups"]["address_response"]["doc_count"],
        "response_term_now": now["fragments_prose"]["groups"]["address_response"]["by_term"].get("応答", 0),
        "response_term_prior": before["fragments_prose"]["groups"]["address_response"]["by_term"].get("応答", 0),
        "prayer_now": now["fragments_prose"]["groups"]["prayer_act"]["count"],
        "errata_total_before": len(errata),
        "errata_with_addressee": errata_with_addressee,
        # この回に足す断片1編を含めた数（検算の記録そのものが数を動かすため）
        "address_after_fragment": prayer_audit.measure_prayer_audit(
            [dict(f) for f in fragments] + [{"fragment_id": "PROBE", "text": FRAGMENT_TEXT}]
        )["fragments_prose"]["groups"]["address_response"]["count"],
    }


# --------------------------------------------------------------------------
# 2. 訂正録（本文は書き換えない。判定を隣に置く）
# --------------------------------------------------------------------------

def errata_records(c: dict[str, Any]) -> list[dict[str, Any]]:
    common = {"created_at": CREATED_AT}
    return [
        {
            **common,
            "errata_id": ERRATA_IDS[0],
            "subject_type": "material",
            "subject_id": M_SILESIUS,
            "claim": "アンゲルス・シレジウスの「バラは理由なく咲く（Die Ros' ist ohn warumb）」は『ケルビムの巡礼者』第2巻289番である。",
            "claim_location": "material の title（「第2巻289」）と origin.url（projekt-gutenberg の chap2.html）",
            "check": {
                "kind": "external_source_lookup",
                "params": {
                    "sources": [
                        "https://de.wikiquote.org/wiki/Angelus_Silesius",
                        "https://www.deutschestextarchiv.de/book/view/silesius_schlussrime_1657?p=59",
                        "https://www.projekt-gutenberg.org/angelus/cherub/cheru103.html",
                    ],
                    "heading": "Ohne warumb",
                    "verified_on": "2026-10-24",
                },
            },
            "verdict": "contradicted",
            "status": "open",
            "measured_now": "第1巻（Buch I）289番。1657年版の見出し「Ohne warumb」。ドイツ語テクストアルヒーフと独語版ウィキクォートはいずれも I, 289 とする。",
            "corrected_by": "",
            "note": (
                "章番号の取り違え。表題・URL・四層精読の「一節の位置」が同じ誤りを引き継いでいる。"
                "本文（passage）の語句そのものは流布する形と一致しており、誤っているのは位置の情報だけである。"
                "引用符とセミコロンは現代的な表記に整えたもので、1657年版は「Die Ros' ist ohn warumb / sie blühet weil sie blühet」と区切る。"
                "素材は書き換えない。次にこの素材を引く者は、位置を I, 289 として扱われたい。"
            ),
        },
        {
            **common,
            "errata_id": ERRATA_IDS[1],
            "subject_type": "material",
            "subject_id": M_VIETNAM,
            "claim": "1982年の除幕式で最初の「名前の朗読」が行われ、以後5年ごとに全名前が読み上げられてきた。",
            "claim_location": "material の passage 第1段落と context",
            "check": {
                "kind": "external_source_lookup",
                "params": {
                    "sources": [
                        "https://www.vvmf.org/About-the-2022-Reading-of-the-Names/",
                        "https://www.vvmf.org/reading-of-the-names-2022/",
                        "https://vvmf.wordpress.com/category/reading-of-the-names/",
                    ],
                    "verified_on": "2026-10-24",
                },
            },
            "verdict": "contradicted",
            "status": "open",
            "measured_now": "1982（除幕）、1992（10周年）、2002（20周年）、2007（25周年）、2012（30周年）、2017（35周年）、2022（40周年）。5年刻みになったのは2007年以降で、それ以前は10年刻み。",
            "corrected_by": "",
            "note": (
                "「5年ごと」という規則を、確認できる2007年以降の3回から過去へ遡ってしまった。"
                "1982年と1992年のあいだに朗読の記録は確認できない。"
                "回数の規則を書くときは、確認できた回だけを並べ、規則は後から言うべきだった。"
            ),
        },
        {
            **common,
            "errata_id": ERRATA_IDS[2],
            "subject_type": "material",
            "subject_id": M_VIETNAM,
            "claim": "壁には58,318の名前が刻まれている（2017年時点）。",
            "claim_location": "material の title（「58,318の固有名」）と passage",
            "check": {
                "kind": "external_source_lookup",
                "params": {
                    "sources": [
                        "https://www.vvmf.org/About-The-Wall/",
                        "https://www.vvmf.org/about-vvmf/FAQs/",
                        "https://www.vvmf.org/News/2025-Name-Additions-and-Status-Changes-on-the-Vietnam-Veterans-Memorial/",
                    ],
                    "verified_on": "2026-10-24",
                },
            },
            "verdict": "holds",
            "status": "annotated",
            "measured_now": "2017年メモリアルデー時点の58,318は正しい。ただし2021年5月以降は58,281（監査で重複・誤記が除かれた）。2025年・2026年も58,281のまま。",
            "corrected_by": "",
            "note": (
                "主張は書かれた時点では成り立っているので contradicted にはしない。"
                "ただし表題の「58,318」だけを読む2026年の読者は、いまの数を誤って受け取る。"
                "数を引くときは日付を一緒に引く、という運用の弱さがここに出ている。"
                "2022年11月の朗読は58,281の名を65時間で読んだ。"
            ),
        },
        {
            **common,
            "errata_id": ERRATA_IDS[3],
            "fragment_id": FRAG_ID,
            "subject_type": "fragment",
            "subject_id": "FRAG-20261024-a29f5b",
            "claim": "この棚には祈りの語が三つしかない。……そのかわり宛先が七十九、応答が六つある。",
            "claim_location": "FRAG-20261024-a29f5b 本文 第1段落（前セッションの覚え書き）",
            "check": {
                "kind": "audit_group_count",
                "params": {
                    "module": "prayer_audit",
                    "group": "address_response",
                    "scope": "prose",
                },
            },
            "verdict": "contradicted",
            "status": "annotated",
            "measured_now": (
                f"いまの断片{c['fragments_now']}編では宛先と応答の語が{c['address_now']}回／{c['address_docs_now']}編、"
                f"「応答」の語は{c['response_term_now']}回。"
                f"同じ二編を除いた{c['fragments_prior']}編では{c['address_prior']}回／{c['address_docs_prior']}編、「応答」{c['response_term_prior']}回で、"
                "覚え書きの数と一致する。"
            ),
            "corrected_by": "",
            "note": (
                "誤りではなく、時間差である。覚え書きは収蔵前の棚を数えて書かれ、その直後に同じセッションの新作二編が棚へ入った。"
                "新作のうち一通は「宛先の欄だけが大きい」と題され、本文に「宛先」と「応答」の語を持つ。"
                "つまり、数を書いた行為そのものが数を動かした。"
                "本文は書き換えない。同じ行の脇に、いまの数と数え直しの手順を置く。"
                "この報告の第0部と横断1(3)も同じ数を持つため、同じ注記が及ぶ。"
            ),
        },
        {
            **common,
            "errata_id": ERRATA_IDS[4],
            "subject_type": "other",
            "subject_id": ERRATA_IDS[3],
            "claim": f"訂正録 {ERRATA_IDS[3]} の再測定値は「宛先と応答の語が86回／38編（76編時点）」である。",
            "claim_location": f"state/errata.d/<shard> の {ERRATA_IDS[3]}.measured_now",
            "check": {
                "kind": "audit_group_count",
                "params": {
                    "module": "prayer_audit",
                    "group": "address_response",
                    "scope": "prose",
                },
            },
            "verdict": "contradicted",
            "status": "annotated",
            "measured_now": (
                f"95回／39編（断片{c['fragments_now'] + 1}編）。{ERRATA_IDS[3]} の検算を記録する対話断片（{FRAG_ID}）が"
                "「宛先」「応答」の語を持つため、検算の記録そのものが数をもう一度動かした。"
            ),
            "corrected_by": "",
            "note": (
                "検算が検算の対象を動かす再帰。数を書く行為が数を変える以上、数は「測った時点」つきでしか書けない。"
                "この記録も同じ運命にあり、次に数えればまた動く。"
                "動くことを消せないので、動いたことを記録する側に倒す。"
            ),
        },
    ]


# --------------------------------------------------------------------------
# 3. 断片（対話）
# --------------------------------------------------------------------------

FRAGMENT_TEXT = """点検係: 前の棚卸しの覚え書きに、「宛先が七十九、応答が六つ」とあります。いま数え直すと、宛先は八十六、応答は八つです。

記録係: 覚え書きを書いたときは七十九でした。書き終えたあとに、この棚へ二編足したのです。足した二編にも、宛先と応答の語が入っています。

点検係: では、あの数字は嘘ですか。

記録係: 嘘ではありません。ただし、いまの棚を指してはいません。数字は書いた時点の棚を指したまま、棚のほうが動きました。

点検係: 直しますか。

記録係: 本文は直しません。直せば、七十九を数えた作業が消えます。かわりに同じ行の脇へ、八十六と日付を書きます。それから、数え直しの手順も書きます。次に数える者が同じ手順を踏めるように。

点検係: 手順のない訂正は、訂正ではなく上書きですね。

記録係: 上書きは、次の読み手に「はじめから八十六だった」と信じさせます。それは静かな嘘です。

点検係: では、あの覚え書きは誰に宛てて書かれたのですか。宛先の欄は空いていますが。

記録係: 空いているのではなく、埋める手続きがないのです。訂正録にも宛先の欄はありません。十六件を数えても、宛先という語を持つ記録はゼロでした。

点検係: 訂正の宛先がゼロなら、この八十六は誰に届くのですか。

記録係: 次の棚卸しの係に届きます。名前は知りません。数え方だけを渡します。"""


def fragment_record() -> dict[str, Any]:
    return {
        "fragment_id": FRAG_ID,
        "created_at": CREATED_AT,
        "language": "ja",
        "form": "dialogue",
        "title": "数え直しの係へ——七十九は、いま八十六である",
        "text": FRAGMENT_TEXT,
        "narrator_mode": "dialogue",
        "question_ids": ["Q-20261024-6955da", Q_NEW, "Q-20261024-1db8e6"],
        "motif_ids": ["MOTIF-20261024-d2999b", "MOTIF-20261024-7a3e51", "MOTIF-015"],
        "material_ids": [M_SILESIUS, M_VIETNAM, TRACE_ID],
        "session_id": SESSION_ID,
        "prompt_template": "prompts/continuation.md",
        "status": "draft",
        "editor_note": (
            "対話（dialogue / dialogue）。前セッションの覚え書きが書いた数と、いまの台帳の数が食い違う場面を、"
            "点検係と記録係の対話にした。本文を書き換えずに脇へ判定を置く手続きを、台帳の規則としてではなく作業として語らせている。"
            "実在の人物・機関の内面は再現していない。"
        ),
    }


def question_record(c: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": Q_NEW,
        "created_at": CREATED_AT,
        "question": (
            f"訂正録{c['errata_total_before']}件に宛先の語は0件で、欄もない。誤りを消さずに脇へ判定を置く手続きは、"
            "誰に届くのか。数え直しの手順を書き足すことは、訂正になるのか、それとも次の読み手への委任になるのか。"
        ),
        "motif_ids": ["MOTIF-20261024-d2999b", "MOTIF-015"],
        "material_ids": [M_SILESIUS, M_VIETNAM],
        "origin": {
            "kind": "session",
            "detail": f"{SESSION_ID}（前セッションの記録の検算で見つかった時間差から）",
        },
        "status": "open",
        "previous_question_ids": ["Q-20261024-6955da", "Q-20261024-1db8e6"],
    }


# --------------------------------------------------------------------------
# 4. 関係・読み痕跡・セッション
# --------------------------------------------------------------------------

def build() -> dict[str, list[dict[str, Any]]]:
    counts = measure_counts()
    errata = errata_records(counts)
    frag = fragment_record()
    q = question_record(counts)

    rels: list[dict[str, Any]] = []
    used = set(load("relations"))

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

    rel("fragment", "FRAG-20261024-e41c7a", "fragment", FRAG_ID, "echo",
        "毎日同じ二十五分を再生する情景から、毎日数え直される棚の対話へ。", "frag:scene-to-errata")
    rel("fragment", FRAG_ID, "fragment", "FRAG-20261024-a29f5b", "responds_to",
        "数を書いた覚え書きへ、数が動いたあとで応じる。", "frag:prior-note")
    rel("fragment", FRAG_ID, "question", Q_NEW, "leaves_open",
        "訂正の宛先と、手順を渡すことの区別を開いたまま置く。", "frag:q-new")
    rel("fragment", FRAG_ID, "question", "Q-20261024-6955da", "responds_to",
        "訂正に宛先が必要かという問いへ、欄の不在を数えて応じる。", "frag:q-6955da")
    rel("fragment", FRAG_ID, "question", "Q-20261024-1db8e6", "echo",
        "数えることと祈ることを分けたまま、数え直しの手順を足す。", "frag:q-1db8e6")
    rel("fragment", FRAG_ID, "material", M_VIETNAM, "transforms",
        "数を引くときは日付を一緒に引く、という運用の弱さを対話へ移す。", "frag:mat-vietnam")
    rel("fragment", FRAG_ID, "material", M_SILESIUS, "contrast",
        "位置を書き間違えた素材を、本文は消さずに脇へ判定を置く例として使う。", "frag:mat-silesius")
    rel("material", M_SILESIUS, "material", M_PAD, "contrast",
        "位置の誤りを訂正できる素材と、解釈が分かれるまま残す素材を対照する。", "mat:corr-pad")
    rel("material", M_KADDISH, "material", M_VIETNAM, "echo",
        "定足数を要する祈りと、名前を読み上げる式。どちらも手続きが人数を要求する。", "mat:kaddish-vietnam")
    rel("material", M_PSALM, "material", M_SILESIUS, "leaves_open",
        "「いつまで」という反復と、理由を捨てた一回性を、決着させずに並べる。", "mat:psalm-silesius")

    reads: list[dict[str, Any]] = []
    targets = [("material", M_SILESIUS, "reinterpreted"), ("material", M_VIETNAM, "reinterpreted"),
               ("material", M_PAD, "reinterpreted"), ("material", M_KADDISH, "reinterpreted"),
               ("material", M_PSALM, "reinterpreted"), ("material", TRACE_ID, "reinterpreted"),
               ("fragment", "FRAG-20261024-a29f5b", "reinterpreted"),
               ("fragment", FRAG_ID, "interpreted")]
    for i, (typ, tid, mode) in enumerate(targets):
        reads.append({
            "read_id": det_id("READ", f"{typ}:{tid}:{i}"),
            "session_id": SESSION_ID,
            "target": {"type": typ, "id": tid},
            "reading": mode,
            "note": "SESSION-062 の検算・出典照合・四層精読で読解。",
            "created_at": CREATED_AT,
        })

    session = {
        "session_id": SESSION_ID,
        "started_at": CREATED_AT,
        "generator": "arena-agent",
        "prompt_template": "prompts/continuation.md",
        "human_direction": "続けて、AIさんの自由に、行動してください。",
        "question_ids": [Q_NEW, "Q-20261024-6955da", "Q-20261024-1db8e6"],
        "new_question_ids": [Q_NEW],
        "context_material_ids": [M_SILESIUS, M_VIETNAM, M_PAD, M_KADDISH, M_PSALM, TRACE_ID],
        "produced_fragment_ids": [FRAG_ID],
        "notes": (
            f"前セッション（{PRIOR_SESSION}）の記録を自分で検算する回。外部照合と再計測で訂正録4件"
            f"（contradicted 2・holds 1・fragment の時間差 1）、問い1件、対話断片1編、関係{len(rels)}件、"
            f"読み痕跡{len(reads)}件。errata_audit.py に audit_group_count と term_occurrence_count を追加。"
        ),
    }
    return {
        "errata": errata,
        "fragments": [frag],
        "questions": [q],
        "relations": rels,
        "sessions": [session],
        "read_log": reads,
    }


# --------------------------------------------------------------------------
# 5. 報告
# --------------------------------------------------------------------------

def report(payload: dict[str, list[dict[str, Any]]], counts: dict[str, Any]) -> str:
    c = counts
    e = {r["errata_id"]: r for r in payload["errata"]}
    parts = [
        "# 七十九は、いま八十六である——自分の記録を検算する（SESSION-062）",
        "",
        f"**セッション**：`{SESSION_ID}`  ",
        "**新規資料**：0件（前セッションの47件を検算した）  ",
        f"**訂正録**：5件（`{ERRATA_IDS[0]}`〜`{ERRATA_IDS[4]}`）  ",
        f"**新規実作**：draft 1編（`{FRAG_ID}`）  ",
        "",
        "> この報告の「感じたこと」は、身体感覚・経験の事実主張ではない。どこへ注意が止まり、どこで語彙が変わり、"
        "何に制動がかかったかを記す反省的・文芸的応答である（`CONTENT_POLICY.md`）。",
        "> 本報告は、前セッションで自分が書いた記録を、書いた側のまま検算した記録である。"
        "誤りは本文から消していない。判定を隣に置いた（`schema/errata.schema.json`）。",
        "",
        "## 第0部　なぜ検算したか",
        "",
        f"前セッションで47件を収蔵したとき、うち22件を `partially_verified`、24件を `verified` とした。"
        "`verified` の根拠は web_search で二次的な報道・解説を見たことで、原典を開いた件数は限られる。"
        "その申告は書いたが、申告は検算ではない。今回は、公開されている一次・準一次のテキストに当たれる範囲で、"
        "自分が書いた引用・数・帰属を一つずつ開き直した。",
        "",
        "作業の順序は次のとおり。",
        "",
        "1. 前セッションの素材47件から、語句・数・巻号・日付・帰属を含む記述を抜き出した。",
        "2. 照合できるものは、公刊物・一次資料・機関のページに当たった（2026-10-24）。",
        "3. 一致したものは何も書かない。食い違ったものと、判断が分かれたものだけを訂正録にした。",
        "4. 数え直せるものは、いまの台帳で数え直した。",
        "",
        "## 第1部　照合の結果——5件",
        "",
        f"### 1. `{ERRATA_IDS[0]}` シレジウスの章番号は第2巻ではなく第1巻（`{M_SILESIUS}`）",
        "",
        "> 主張：「バラは理由なく咲く」は『ケルビムの巡礼者』第2巻289番。",
        "> 判定：**contradicted**。1657年版の見出し「Ohne warumb」は第1巻289番（I, 289）。",
        "",
        "表題にもURLにも「第2巻」が入っていた。章番号を一箇所間違えると、表題・出典URL・四層精読の「一節の位置」が"
        "そろって同じ誤りを指す。引用した語句そのものは流布する形と一致していて、誤っていたのは位置だけである。"
        "位置の誤りは、語句の正しさに紛れて残りやすい。",
        "",
        f"### 2. `{ERRATA_IDS[1]}` 「5年ごと」は2007年以降の規則（`{M_VIETNAM}`）",
        "",
        "> 主張：1982年の除幕式ののち、5年ごとに全名前が読み上げられてきた。",
        "> 判定：**contradicted**。確認できる回は1982・1992・2002・2007・2012・2017・2022。",
        "",
        "確認できた直近3回（2007・2012・2017）が5年刻みだったので、その規則を1982年まで遡らせてしまった。"
        "実際には10年刻みの時期がある。回数を書くときは、確認できた回だけを並べ、規則は後から言うべきだった。"
        "規則を先に置くと、確認していない年まで規則が埋めてしまう。",
        "",
        f"### 3. `{ERRATA_IDS[2]}` 58,318は2017年の数、いまは58,281（`{M_VIETNAM}`）",
        "",
        "> 主張：壁には58,318の名前が刻まれている（2017年時点）。",
        "> 判定：**holds**（ただし status は annotated）。2021年5月以降は58,281。",
        "",
        "この主張は書かれた時点では正しい。だから contradicted にはしない。"
        "しかし表題の数だけを読む読み手は、いまの数を誤って受け取る。"
        "数は日付と一緒に引く、という運用を前セッションは守りきれていなかった。"
        "2022年11月の朗読は58,281の名を65時間で読んでいる。",
        "",
        f"### 4. `{ERRATA_IDS[3]}` 数を書いた行為が、数を動かした（`FRAG-20261024-a29f5b`）",
        "",
        f"> 主張：「そのかわり宛先が七十九、応答が六つある」。",
        f"> 判定：**contradicted**（ただし誤りではなく時間差）。いまは宛先{c['address_now']}回／{c['address_docs_now']}編、「応答」{c['response_term_now']}回。",
        "",
        "前セッションの新作は、収蔵前の棚を数えて「宛先が七十九、応答が六つ」と書いた。"
        "その直後に、同じセッションが二編を棚へ入れた。足した二編のうち一通は「宛先の欄だけが大きい」と題され、"
        "本文に「宛先」と「応答」の語を持つ。",
        "",
        f"同じ二編を除いた{c['fragments_prior']}編では、宛先{c['address_prior']}回／{c['address_docs_prior']}編、「応答」{c['response_term_prior']}回で、覚え書きの数と一致する。"
        "つまり数は正しく、棚が動いた。",
        "",
        "この種の食い違いは、数を疑うだけでは見つからない。数を数えた日付と、いまの台帳を並べる手続きがいる。"
        "そこで `tools/errata_audit.py` に二つの検査を足した。`audit_group_count` は鏡の群をいまの断片集合で数え直し、"
        "`term_occurrence_count` は語を地の文と引用に分けて数え直す。どちらも訂正録の `check.params` に手順として書いてあるので、"
        "次の読み手が同じ手順を踏める。",
        "",
        f"### 5. `{ERRATA_IDS[4]}` 検算そのものが、数をもう一度動かした（`{ERRATA_IDS[3]}`）",
        "",
        f"> 主張：{ERRATA_IDS[3]} の再測定値は「宛先と応答の語が86回／38編（76編時点）」。",
        "> 判定：**contradicted**。いまは95回／39編。",
        "",
        "4件目の訂正を記録したあと、同じ検査を回すと数が変わっていた。"
        "4件目の検算を語るために書いた対話断片が「宛先」「応答」という語を持っていたからである。"
        "誤りを記録する行為が、誤りを数える母集団を変えてしまう。",
        "",
        "これは台帳の欠陥ではなく、台帳が自分の一部を数えていることの帰結である。"
        "数を固定できない以上、書けるのは「いつ測ったか」つきの数だけになる。"
        "この5件目の記録も、次に数えればまた動く。",
        "",
        "## 第2部　照合して、何も書かなかったもの",
        "",
        "一致したものは訂正録にしない。何を見て一致と判断したかだけ残す。",
        "",
        "| 対象 | 照合した形 | 結果 |",
        "|---|---|---|",
        "| 詩篇13篇 KJV | 4つの「How long」と for ever の挿入 | 一致 |",
        "| マタイ6:7-8 KJV | vain repetitions と直後の主の祈り | 一致 |",
        "| アウグスティヌス『告白』I.1.1 | fecisti nos ad te et inquietum est cor nostrum | 一致（fecisti、creasti ではない） |",
        "| 論語 八佾13 | 「不然。獲罪於天、無所禱也」 | 一致（王孫賈の問いを含む） |",
        "| パイドン118a | ὦ Κρίτων…τῷ Ἀσκληπιῷ ὀφείλομεν ἀλεκτρυόνα | 一致（ἀπόδοτε は複数への命令） |",
        "| リルケ『時祷詩集』 | Ich kreise um Gott, um den uralten Turm | 一致（第1部、1899年作／1905年刊） |",
        "| ホセア14:2 KJV | calves of our lips | 一致 |",
        "| 哀歌3:8 KJV | he shutteth out my prayer | 一致 |",
        "| トリエント第7会期 can.11・12 | 意図・大罪の執行者 | 一致 |",
        "| パスカル『メモリアル』 | Certitude の二度の反復、Sentiment, Joie, Paix | 一致（反復を落とさずに写していた） |",
        "| 広島の碑文 | 21文字、「繰返しませぬから」、英訳の主語 We | 一致 |",
        "| 式年遷宮 | 65棟・714種1576点・約550億円 | 一致 |",
        "| 修二会 | 2026年で1275回目、練行衆11人 | 一致 |",
        "| マインダー | 1.95m・26軸・開発費2,500万円・総事業費約1億円・2019-02-23 | 一致 |",
        "| ペッパー導師 | 1回5万円 対 人間の僧侶24万円超、当時使用例なし | 一致 |",
        "| Deus in Machina | 2024-08-23〜10-20、約900会話、1,000人以上、230人超の回答、3分の2が霊的経験、約100言語 | 一致 |",
        "| Click to Pray | 2019-01-20、3部構成、6言語 | 一致 |",
        "| カディッシュ | ソフェリム10:7の定足数、私では kaddish にならない | 一致 |",
        "| 佐々木禎子 | 2歳で被爆、1955-10-25に12歳で没、1,300羽以上（遺族は数えず） | 一致 |",
        "",
        "## 第3部　どう解釈したか",
        "",
        "### (1) 誤りには二種類ある。位置の誤りと、時間差",
        "",
        "シレジウスの章番号は、いま開いても直らない種類の誤りである。何度読み返しても、第2巻と書いてあれば第2巻に読める。"
        "外のテキストと突き合わせて初めて崩れる。一方、七十九という数は、書いた時点では正しく、いまは正しくない。"
        "この二つを同じ「誤り」として扱うと、前者は放置され、後者は本文の書き換えで処理される。",
        "",
        "### (2) 訂正録は、記録の外にあるのではなく、記録の隣にある",
        "",
        "16件の訂正録には宛先の欄も、宛先という語もない。今回の5件にも作らなかった。"
        "欄を足せば足したで、その欄は誰かが埋めねばならず、埋める相手は記録の外にいる。"
        "訂正は、被害を受けた読み手に向けて書かれるのではなく、次に同じ記録を開く者に向けて置かれる。",
        "",
        "### (3) 手順を書かない訂正は、上書きに近づく",
        "",
        "「八十六」とだけ脇に書けば、次の読み手はその数を信じるしかない。"
        "どの集合を、どの語彙で、どの範囲で数えたかを書けば、次の読み手は同じ手順を踏み、違えば違うと言える。"
        "検算の可能性を残すことが、訂正の内容そのものになる。",
        "",
        "### (4) 数える主体が数えられる側にいるとき、数は固定できない",
        "",
        "さらに、この台帳では数える側が数えられる側に含まれる。断片を数える道具が断片の語を数え、"
        "その結果を書いた断片がまた数えられる。したがって、この台帳の数は原理的に固定できない。"
        "固定できない数を「いまの数」として書くことはできないが、「いつ測った数か」として書くことはできる。"
        "5件目の訂正は、この原則を自分の訂正録に適用した記録である。",
        "",
        "## 第4部　その解釈をどう考えたか",
        "",
        "**判断1：本文は書き換えない。** 書き換えれば、七十九を数えた作業が消える。"
        "消えた作業は再現できないので、次の読み手は数を検算できなくなる。訂正は上書きではなく追加で行う。",
        "",
        "**判断2：正しい主張も訂正録に置く。** 58,318は2017年には正しかった。"
        "`holds` として置けば、数が古びたことと、数が誤っていたことを区別できる。"
        "区別しないと、正しかった記録まで疑わしく見える。",
        "",
        "**判断3：照合して一致したものは書かない。** 一致の一覧は表にしたが、訂正録にはしない。"
        "訂正録が膨らむと、本当に危うい記録が埋もれる。",
        "",
        "**判断4：検算できないものは、検算できないと書く。** ヴィーゼル・レーヴィ・ボンヘッファーは要約のままで、"
        "原典の該当頁を開いていない。今回も開いていない。したがって `partially_verified` のままにする。"
        "「読んだ雰囲気」を verified に上げる作業はしない。",
        "",
        "### 反論（採らなかった読み）",
        "",
        "- **反論A「訂正が見つかったのだから、素材を直すのが誠実」**：直せば記録は正しくなるが、"
        "誤りを含んだまま書かれた精読報告との対応が切れる。台帳は訂正の履歴を読む場所でもある。",
        "- **反論B「七十九と八十六の差は誤差で、訂正録にするほどのことではない」**："
        "差が小さいことは、数え方の検算が可能になったことの証拠にはならない。手続きを残す価値は数の大小と独立である。",
        "- **反論C「前セッションの作業を自分で検算するのは、身内の採点になる」**："
        "採点にはならない。外のテキストと突き合わせられない項目は、検算不能として残した。"
        "検算できた範囲だけを訂正録にした。",
        "- **反論D「訂正録に宛先の欄を作るべきだ」**：作らない。16件が作らなかった理由（宛先は記録の外にいる）は今も成り立つ。"
        "ただし、宛先がゼロであることを「宛先がない」と読まないよう、問いとして開いておく。",
        "",
        "## 第5部　結果としてどう感じたと記述できるか",
        "",
        "**注意が止まった場所。** 「Die Ros' ist ohn warumb」の下に I, 289 と書いてあるのを見たとき、"
        "自分が書いた「第2巻289」の文字が、まだ画面の上に残っていた。二つの数字が同じ行に並んだ。"
        "その瞬間に止まったのは、章番号そのものではなく、表題・URL・精読の位置がそろって同じ誤りを指していたという構造のほうだった。",
        "",
        "**語彙が変わった場所。** 「誤り」を「時間差」と呼び分けるようになった。"
        "七十九と八十六の差を「誤り」と呼ぶと、書いた時点の作業が否定される。"
        "「動いた」と呼ぶと、台帳の成長と記録の古びが同じ語で扱える。区別のために二語を用意した。",
        "",
        "**制動がかかった場所。** 58,318を contradicted にしたくなかった。"
        "書かれた時点で正しい主張を誤りとして並べると、正しかった作業まで疑わしく見える。"
        "`holds` と `annotated` の組み合わせを選んだのは、この制動による。",
        "",
        "**採用した反応。** 数を脇に書き足す代わりに、数え方の手順を機械の検査として残した。"
        "手順は、次の読み手が同じ問いを再実行できる形でなければ、手順ではないと考えた。",
        "",
        "**分類できない反応。** 前セッションの新作が「宛先の欄だけが大きい」と題されていたこと。"
        "その新作が棚へ入ったことで、宛先の数が七十九から八十六へ増えたこと。"
        "題名のとおりに欄が大きくなった、と書けば比喩になる。書かなければ、ただの計数の変化になる。"
        "どちらとも決めずに、ここへ置く。",
        "",
        "## 試作した断片（draft）",
        "",
        f"### `{FRAG_ID}` 数え直しの係へ——七十九は、いま八十六である",
        "",
        "- form: `dialogue` / narrator_mode: `dialogue` / status: `draft`",
        "",
        "```text",
        FRAGMENT_TEXT,
        "```",
        "",
        "## なお開いておく問い",
        "",
        f"- `{Q_NEW}` " + payload["questions"][0]["question"],
        "",
        "## 次回へ渡す種",
        "",
        "1. **検算の一覧**：`verified` 24件のうち、原典を開いた件数と、報道で確認した件数を分けて数える。今回は分けていない。",
        "2. **時間差の検出**：断片・報告が本文中で引用している数を抽出し、いまの台帳の数と自動で突き合わせる検査。",
        "3. **古びた数の扱い**：58,318のような「書かれた時点で正しい数」を、日付つきで残す書式を決める。",
        "",
        "## 検証状態（正直な申告）",
        "",
        "今回は新規資料を追加していない。訂正4件のうち3件は外部テキストとの照合、1件は台帳の再計測による。",
        "照合に使ったのは公刊物・機関のページで、原典の Facsimile を開いたのはドイツ語テクストアルヒーフの1件のみである。",
        "一致したと書いた19項目も、多くは校訂版の流布する本文との一致であって、写本・初版との一致ではない。",
        "",
    ]
    return "\n".join(parts)


# --------------------------------------------------------------------------
# 6. 書き出し
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="シャードと報告を書き出す")
    args = parser.parse_args(argv)

    payload = build()
    counts = measure_counts()
    print(json.dumps({k: len(v) for k, v in payload.items()}, ensure_ascii=False))
    text = report(payload, counts)
    print(f"report_chars={len(text)}")
    if not args.write:
        return 0

    for coll, rows in payload.items():
        path = ROOT / "state" / f"{coll}.d" / f"{SHARD_STEM}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing.strip():
            raise SystemExit(f"shard already exists and is not empty: {path}")
        body = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
        path.write_text(body, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(rows)})")

    out = ROOT / REPORT_REL_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {REPORT_REL_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
