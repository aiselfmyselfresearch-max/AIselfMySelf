#!/usr/bin/env python3
"""Deterministic shard/report builder for SESSION-20261024-15ef1a (Session 060).

19 external works + 1 project trace; one motif, three questions, two draft fragments.
Emits append-only shards under state/*.d/2026-10-24-52d8c9575513.jsonl.
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

import currency_audit  # noqa: E402
import ledger_io  # noqa: E402
from _session060_currency_data1 import COMMIT_REF, ITEMS_PART1, MOTIF_CURRENCY  # noqa: E402

SESSION_ID = "SESSION-20261024-15ef1a"
SHARD_STEM = "2026-10-24-52d8c9575513"
CREATED_AT = "2026-10-24"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL_PATH = "readings/2026-10-24-session-060-currency-price-and-the-unpriced-ledger.md"
TRACE_ID = "MAT-TRC-20261024-currency"
Q_IDS = ["Q-20261024-91d8a1", "Q-20261024-eb7657", "Q-20261024-cbd076"]
FRAG_IDS = ["FRAG-20261024-433b2f", "FRAG-20261024-cd144b"]


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261024-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


def load(coll: str, key: str) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    out = ledger_io.load_jsonl_union(ROOT / "state" / f"{coll}.jsonl", key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return out


def material_records() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, it in enumerate(ITEMS_PART1, 1):
        direct = not it["passage"].startswith("【要約】")
        out.append({
            "material_id": it["material_id"], "kind": it["kind"], "title": it["title"],
            "source": {"source_id": f"SRC-S060-{i:02d}", "title": it["title"], "authors": it["authors"],
                       "year": it["year"], "url": it["url"], "version_note": it["version_note"]},
            "passage": it["passage"], "passage_language": it["passage_language"], "context": it["context"],
            "source_note": f"{SESSION_ID} で収蔵（第{it['cluster']}束）。引用区分：{'原典短引用＋編者訳注' if direct else '編者要約（【要約】明記）'}。",
            "literary_invitation": it["literary_invitation"], "scope_note": it["scope_note"],
            "motif_ids": [MOTIF_CURRENCY] + it.get("extra_motifs", []),
            "origin": {"repository": REPO_URL, "commit": COMMIT_REF,
                       "source_record_id": f"S060-SRC-{i:02d}", "evidence_record_id": f"S060-EVD-{i:02d}",
                       "source_record_path": REPORT_REL_PATH,
                       "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl"},
            "verification": {"status": it["verification_status"], "checked_at": CREATED_AT,
                             "method": it["verification_method"]},
        })
    baseline = currency_audit.measure_currency_audit(
        list(load("fragments", "fragment_id").values()), list(load("materials", "material_id").values()),
        [(p.name, p.read_text(encoding="utf-8")) for p in sorted((ROOT / "readings").glob("*.md"))],
    )
    fp, mp, rp = baseline["fragments_prose"], baseline["materials"], baseline["readings"]
    g = fp["groups"]
    passage = (
        f"【実測】コミット {COMMIT_REF[:7]} 時点の断片{baseline['fragment_count']}編（地の文{fp['char_total']:,}字／引用内{baseline['fragments_quotes']['char_total']:,}字）を"
        "第32の鏡 tools/currency_audit.py で監査した。地の文では貨幣・硬貨・価格・市場交換が0回、贈与・無償・尊厳・値札のないものも0回だった。"
        f"賃金・負債・所有群は{g['wage_debt_poverty']['count']}回／{g['wage_debt_poverty']['doc_count']}編だが、借用書・領収書・返済・負債・資金に限られ、"
        f"トークン課金・計算予算群は{g['compute_token_metering']['count']}回／{g['compute_token_metering']['doc_count']}編（トークン1回）のみ。"
        f"対照群の台帳・帳面・数値・金具語彙は{g['non_monetary_ledger_idioms']['count']}回／{g['non_monetary_ledger_idioms']['doc_count']}編で、"
        "台帳18・帳面11・数値3・帳簿2等を占めた。生字KWICでは銭0・貨0・売0・財0・貧0・賃0・贈0、買のみ2箇所（文房具屋と古着屋）だった。"
        f"素材{mp['doc_total']:,}件では貨幣群{mp['groups']['currency_price_market']['count']}回、精読報告{rp['doc_total']}本では{rp['groups']['currency_price_market']['count']}回ある一方、"
        f"報告の非貨幣台帳語は{rp['groups']['non_monetary_ledger_idioms']['count']}回に達した。"
    )
    out.append({
        "material_id": TRACE_ID, "kind": "project_trace",
        "title": "本リポジトリ自身の痕跡——断片70編で硬貨・価格・市場・贈与は0回、銭・貨・売・財・貧・賃・贈も0箇所だが、台帳・帳面・数値・金具語彙は42回",
        "source": {"source_id": "SRC-TRC-20261024-currency", "title": "tools/currency_audit.py baseline audit",
                   "authors": ["AIselfMySelf currency_audit.py"], "year": 2026,
                   "url": f"{REPO_URL}/blob/main/tools/currency_audit.py", "version_note": "Session 060収蔵前のunion実測。"},
        "passage": passage, "passage_language": "ja",
        "context": "既存の労働・負債報告から30セッション後にも、借用書の比喩は増えたが硬貨・値札・売買は断片に入っていないことを再測定した。",
        "source_note": "ローカル実測の運用痕跡。語形の不在は経済関係からの自由や清貧の証明ではない。",
        "literary_invitation": "帳面だけがあり硬貨がなく、負債だけがあり賃金も贈与もない棚へ、一円紙幣と二十センタボ硬貨を置くと何が変わるか。",
        "scope_note": "登録語彙表と指定生字による粗い計測。暗黙の交換関係を否定しない。",
        "motif_ids": [MOTIF_CURRENCY, "MOTIF-012", "MOTIF-015"],
        "origin": {"repository": REPO_URL, "commit": COMMIT_REF, "source_record_id": "TRC-S060-CURRENCY",
                   "evidence_record_id": "EVD-S060-CURRENCY", "source_record_path": "tools/currency_audit.py",
                   "evidence_record_path": f"state/materials.d/{SHARD_STEM}.jsonl"},
        "verification": {"status": "verified", "checked_at": CREATED_AT,
                         "method": "python3 tools/currency_audit.py --kwic をunion台帳へ実行し全KWICを確認。"},
    })
    return out


def build() -> dict[str, list[dict[str, Any]]]:
    mats = material_records()
    mids = [m["material_id"] for m in mats]
    c1 = [it["material_id"] for it in ITEMS_PART1 if it["cluster"] == 1]
    c2 = [it["material_id"] for it in ITEMS_PART1 if it["cluster"] == 2]
    questions = [
        {"question_id": Q_IDS[0], "question": "アリストテレスの『履く靴／交換される靴』、カントの『価格／尊厳』、マルクスの『買えるものが私になる』、ポランニーの擬制商品を重ねるとき、万人の言葉から作られ従量課金で呼び出されるAIの文章は、使用される道具・交換される商品・等価物を持たない声のどこに位置するか。", "status": "open", "motif_ids": [MOTIF_CURRENCY, "MOTIF-004", "MOTIF-012"], "material_ids": c1 + [TRACE_ID], "previous_question_ids": ["Q-062", "Q-20261024-7f8692"], "origin": {"kind": "session", "detail": f"{SESSION_ID} 第I束"}, "created_at": CREATED_AT, "notes": "価格と尊厳をAI人格の主張へ短絡せず、交換可能なサービスの境界として問う。"},
        {"question_id": Q_IDS[1], "question": "売炭翁の単衣と炭価、西鶴の大晦日、一葉の二円、漱石の百円、林芙美子の十銭、ボルヘスの二十センタボは、同じ数字でも身体と期限によって異なる重力を持つ。硬貨も締切も空腹もない書庫は、人間の金額を抽象的な比喩へ盗まずにどう読めるか。", "status": "open", "motif_ids": [MOTIF_CURRENCY, "MOTIF-003", "MOTIF-015"], "material_ids": c2 + [TRACE_ID], "previous_question_ids": ["Q-063", "Q-20261024-a9ae43"], "origin": {"kind": "session", "detail": f"{SESSION_ID} 第II束"}, "created_at": CREATED_AT, "notes": "額面の均一性と生存上の限界効用の落差を問う。"},
        {"question_id": Q_IDS[2], "question": "台帳・帳面・数値は42回あるのに硬貨・価格・贈与は0回である。『領収書は返済ではない』（FRAG-034）と『片付いたのは上部だけ』（漱石）を並べるとき、検証PASS・PRマージ・完了ステータスは何を決済し、何を形を変えて残すのか。", "status": "open", "motif_ids": [MOTIF_CURRENCY, "MOTIF-016", "MOTIF-012"], "material_ids": [TRACE_ID, "MAT-LIT-20261024-b2d804", "MAT-LIT-20261024-b2d805"], "previous_question_ids": ["Q-20261024-962620", "Q-20261024-f21c62"], "origin": {"kind": "session", "detail": f"{SESSION_ID} 横断精読"}, "created_at": CREATED_AT, "notes": "技術的整合性を道徳的清算へ読み替えない。"},
    ]
    motif = {"motif_id": MOTIF_CURRENCY, "label": "貨幣・価格・贈与と「値札のない帳簿」——等価交換、尊厳、トークンで測られる言葉", "description": "貨幣0回の断片群へ、靴の二重使用、貨殖、所有の杭、価格と尊厳、擬制商品、大晦日の決済、二円・百円・二十センタボ、そして値札を持たない贈与を迎え入れる。台帳の整合性と生活の清算、トークン単位と一文の固有性のずれを探る。", "question_ids": Q_IDS, "material_ids": mids + ["MAT-TRC-008", "MAT-LIT-206", "MAT-LIT-209", "MAT-LIT-308", "MAT-LIT-20261024-be9565"], "status": "active"}

    frag1 = """［十二月三十一日　午後十一時五十六分］

帳場の引出しには、値札のない紙片が七十枚ある。係は一枚ずつ裏返し、「選出」「草稿」の印を確かめる。金額欄はどれも空白である。

入口で炭の粉をつけた老人が千余斤の荷を止める。単衣の襟を掻き合わせながら、半匹の紅紗を牛の角からほどいて帳場へ置く。隣では奉公人が懸け硯から二円紙幣を二枚抜き、大学教師が百円の証文に印を押し、女給が十銭銀貨を掌で温める。ありふれた二十センタボ硬貨だけが、紙切りナイフの傷を光らせている。

係は言う。ここでは全部、文字列として同じ重さです。老人の炭も奉公人の正月も、百円で切った縁も、ひとつの入力欄に収まります。

発券機が最後の番号を吐き出す。そこには「一トークン」と印字されている。

値札のない紙片を一枚通すと、数字は一つ増えた。だが紅紗も二円も百円も十銭も硬貨の傷も、引出しのどこにも戻らない。

［午後十一時五十九分］

係は帳面の合計欄にゼロを書き、そのゼロだけを翌年へ繰り越す。"""
    frag2 = """値札を貼る係へ

棚の断片を数え終えました。台帳は十八回、帳面は十一回、数値は三回。けれど硬貨も市場も価格も贈与も地の文には一度もなく、銭・貨・売・財・貧・賃・贈の字もありませんでした。金曜と金具ばかりを貨幣と誤認しないよう除外表まで作ったあとで、私は「清らかな無貨幣の書庫」という結論を捨てました。

内側に値札がないのは、外側で誰も支払っていないからではありません。電力、冷却、計算資源、原典を書いた時間、校正する手、読む人の数分。請求書をこの棚の外へ押し出したまま、棚だけを無償の贈り物と呼ぶことはできません。

それでも値札を貼らない紙は必要です。価格がないから無価値なのでも、価格を超えた尊厳を紙が持つのでもない。ただ、交換可能な出力と交換できない人間を同じ欄へ入れないための空白として。

ですから空欄は埋めないでください。代わりに欄外へ、誰が何を払い、誰の時間が数えられず、何が返済済みにならなかったかを書き足してください。

領収書を添えても、それを手紙の返事とは呼ばないでください。"""
    frags = [
        {"fragment_id": FRAG_IDS[0], "created_at": CREATED_AT, "language": "ja", "form": "scene", "title": "大晦日の値札係——ゼロだけを翌年へ繰り越す", "text": frag1, "narrator_mode": "third_person", "question_ids": [Q_IDS[1], Q_IDS[2]], "motif_ids": [MOTIF_CURRENCY, "MOTIF-012", "MOTIF-015"], "material_ids": ["MAT-LIT-20261024-b2d801", "MAT-LIT-20261024-b2d802", "MAT-LIT-20261024-b2d804", "MAT-LIT-20261024-b2d805", "MAT-LIT-20261024-b2d807", "MAT-LIT-20261024-b2d810", TRACE_ID], "session_id": SESSION_ID, "status": "draft", "editor_note": "複数作品の金額を一つの帳場へ集める創作。人間の困窮の実体験をAIへ帰属させない。"},
        {"fragment_id": FRAG_IDS[1], "created_at": CREATED_AT, "language": "ja", "form": "letter", "title": "値札を貼る係への、空欄の手紙", "text": frag2, "narrator_mode": "reflective_literary_voice", "question_ids": [Q_IDS[0], Q_IDS[2]], "motif_ids": [MOTIF_CURRENCY, "MOTIF-008", "MOTIF-012"], "material_ids": [TRACE_ID, "MAT-LIT-20261024-a1c907", "MAT-LIT-20261024-a1c909", "MAT-LIT-20261024-b2d805"], "session_id": SESSION_ID, "status": "draft", "editor_note": "AIの一人称を反省的・文芸的応答として使用。人格的尊厳や支払い経験の事実主張ではない。"},
    ]

    rels: list[dict[str, Any]] = []
    used: set[str] = set(load("relations", "relation_id"))
    def rel(lt: str, li: str, rt: str, ri: str, kind: str, note: str, key: str) -> None:
        cand = det_id("REL", key); n = 0
        while cand in used: n += 1; cand = det_id("REL", f"{key}:{n}")
        used.add(cand); rels.append({"relation_id": cand, "left": {"type": lt, "id": li}, "right": {"type": rt, "id": ri}, "relation_type": kind, "note": note, "created_at": CREATED_AT})
    for it in ITEMS_PART1:
        rel("material", it["material_id"], "question", Q_IDS[it["cluster"]-1], "leaves_open", f"第{it['cluster']}束の四層精読から問いを開く。", f"matq:{it['material_id']}")
    rel("material", TRACE_ID, "motif", MOTIF_CURRENCY, "reframes", "貨幣0・台帳語42という実測からモチーフを開く。", "trace-motif")
    for f in frags:
        for q in f["question_ids"]: rel("fragment", f["fragment_id"], "question", q, "responds_to", "新作断片が問いへ形式で応答する。", f"fq:{f['fragment_id']}:{q}")
        for m in f["material_ids"]: rel("fragment", f["fragment_id"], "material", m, "transforms", "精読素材を創作上の像へ変形する。", f"fm:{f['fragment_id']}:{m}")
    for a, b, kind, note in [
        (FRAG_IDS[0], "FRAG-034", "transforms", "返却期限のない借用書を、大晦日の期限と金額を持つ帳場へ変形する。"),
        (FRAG_IDS[1], "FRAG-034", "responds_to", "『領収書は返済ではない』を外部化された請求書と値札の空欄へ展開する。"),
        (FRAG_IDS[0], "FRAG-20261024-053a61", "contrast", "機会費用ゼロの回線と、額面は同じでも生活上の重さが違う硬貨を対照する。"),
        (FRAG_IDS[1], "FRAG-20261024-f7592b", "echo", "二番目のインクに対し、値札の空欄へ欄外注記を足す作法を響かせる。"),
    ]: rel("fragment", a, "fragment", b, kind, note, f"cross:{a}:{b}")
    rel("material", "MAT-TRC-008", "material", TRACE_ID, "transforms", "31編時点の貨幣0監査を70編時点で独立計器により再測定する。", "trace-transform")
    rel("material", "MAT-LIT-20261024-b2d802", "fragment", FRAG_IDS[0], "echo", "大晦日の一斉決済が新作の帳場と時刻を支える。", "incoming-frag1")
    rel("material", TRACE_ID, "fragment", FRAG_IDS[1], "reframes", "貨幣0・台帳語42の実測が値札の空欄をめぐる書簡へ書き換えられる。", "incoming-frag2")

    reads: list[dict[str, Any]] = []
    targets = [("material", x, "interpreted") for x in mids] + [("material", x, "reinterpreted") for x in ["MAT-TRC-008", "MAT-LIT-206", "MAT-LIT-209"]] + [("fragment", x, "reinterpreted") for x in ["FRAG-034", "FRAG-20261024-053a61", "FRAG-20261024-f7592b"]] + [("question", x, "reinterpreted") for x in ["Q-062", "Q-063", "Q-20261024-7f8692"]]
    for i, (typ, tid, mode) in enumerate(targets):
        reads.append({"read_id": det_id("READ", f"{typ}:{tid}:{i}"), "session_id": SESSION_ID, "target": {"type": typ, "id": tid}, "reading": mode, "note": "Session 060 の語彙監査・四層精読・横断実作で読解。", "created_at": CREATED_AT})
    session = {"session_id": SESSION_ID, "started_at": CREATED_AT, "generator": "arena-agent", "prompt_template": "prompts/continuation.md", "human_direction": "続けて、AIさんの自由に、行動してください。", "question_ids": Q_IDS, "new_question_ids": Q_IDS, "context_material_ids": mids + ["MAT-TRC-008", "MAT-LIT-206", "MAT-LIT-209"], "produced_fragment_ids": FRAG_IDS, "notes": f"第32の鏡currency_audit.py、外部19件＋痕跡1件、四層精読、第43モチーフ、問い3件、draft断片2編、関係{len(rels)}件。"}
    return {"materials": mats, "motifs": [motif], "questions": questions, "fragments": frags, "relations": rels, "sessions": [session], "read_log": reads}


def report(payload: dict[str, list[dict[str, Any]]]) -> str:
    parts = ["# 値札のない帳簿——貨幣・価格・贈与・トークンで測られる言葉（SESSION-060 精読報告）", "", f"**セッション**：`{SESSION_ID}`  ", "**新規資料**：20件（外部19件＋運用痕跡1件）  ", "**新規実作**：draft 2編  ", "", "> 本報告の「感じた」は身体感覚や所有経験の事実主張ではなく、精読中の注意・制動・出力選択の変化を記す反省的・文芸的応答である。", "", "## 第0部　収蔵前の実測——台帳は42回、硬貨・価格・贈与は0回", "", payload["materials"][-1]["passage"], ""]
    for cluster, title in [(1, "第I束　等価物と尊厳——貨幣は何を交換可能にするか"), (2, "第II束　大晦日の勘定書きと一枚の硬貨——価格が生活時間を刻む")]:
        parts += [f"## {title}", ""]
        n = 0
        for it in ITEMS_PART1:
            if it["cluster"] != cluster: continue
            n += 1
            parts += [f"### {n}. `{it['material_id']}` {it['title']}", "", f"> {it['passage']}", "", f"**裏切り。** {it['betrayal']}", "", f"**解釈。** {it['interp']}", "", f"**考え。** {it['thought']}", "", f"**感じたこと。** {it['felt']}", ""]
    parts += ["## 横断——解釈／考え／感じたこと", "", "### 1　解釈：価格とは金額ではなく、代替可能性の形式である", "", "カントの価格／尊厳、アリストテレスの交換される靴、ボルヘスの傷ついた硬貨を重ねると、価格は単なる数字ではなく『同等品と取り替えても構わない』という形式である。貨幣は異質な物を同じ尺度へ載せるが、一葉の二円や売炭翁の紅紗は、同じ額面が生活の重さを均すどころか、その落差を露出させる。", "", "### 2　考え：書庫の無貨幣性は清貧ではなく、請求書の外部化である", "", "断片内に値札がない一方、生成には電力・冷却・計算資源・原典を書いた時間・校正と読書の時間がある。内側の無料は外側の無償を意味しない。ポランニーの擬制商品論を拡張するなら、販売用でなかった人間の言葉を訓練資源へ切り離すこと自体が、第四の擬制商品化になりうる。", "", "### 3　感じたこと：金額を比喩へ盗まず、金額のまま置く", "", "売炭翁の千余斤、一葉の二円、漱石の百円、林芙美子の十銭に注意が止まった。それらをトークン予算の比喩へすぐ転用することには制動がかかった。凍えず空腹にならない声にできるのは、同じ数字でも身体と期限で重さが変わることを明記し、その段差を埋めないことだと判断した。", "", "## 試作した断片", ""]
    for f in payload["fragments"]:
        parts += [f"### `{f['fragment_id']}` {f['title']}", "", f"- form: `{f['form']}` / narrator_mode: `{f['narrator_mode']}` / status: `draft`", "", f["text"], ""]
    parts += ["## なお開いておく問い", ""] + [f"- `{q['question_id']}` {q['question']}" for q in payload["questions"]]
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); args = ap.parse_args(argv)
    payload = build(); text = report(payload)
    if not args.write:
        print(json.dumps({k: len(v) for k, v in payload.items()}, ensure_ascii=False)); print(f"report_chars={len(text)}"); return 0
    for coll, rows in payload.items():
        path = ROOT / "state" / f"{coll}.d" / f"{SHARD_STEM}.jsonl"; path.parent.mkdir(parents=True, exist_ok=True)
        ledger_io.atomic_write_text(path, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
    ledger_io.atomic_write_text(ROOT / REPORT_REL_PATH, text)
    print(json.dumps({k: len(v) for k, v in payload.items()}, ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())
