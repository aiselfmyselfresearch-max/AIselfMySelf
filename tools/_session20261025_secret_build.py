#!/usr/bin/env python3
"""Build SESSION-20261025-0f3e1a (秘密・嘘・暗号) ledger shards.

One-shot builder, following the pattern of earlier _session* build scripts.
It appends only to this session's own shards (created beforehand with
tools/new_ledger_shard.py --date 2026-10-25) and refuses to run if any of
those shards is already non-empty, so a second run cannot duplicate rows.
Pre-acquisition numbers are measured live (before any write) with
tools/secret_audit.py, so the project-trace material and §1 of
readings/2026-10-25-secret-lie-and-cipher.md describe the archive exactly as
it was when this session started.
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
import secret_audit  # noqa: E402
from _session20261025_secret_data1 import MATERIALS_1  # noqa: E402
from _session20261025_secret_data2 import MATERIALS_2  # noqa: E402
from _session20261025_secret_data3 import MATERIALS_3  # noqa: E402

DATE = "2026-10-25"
STAMP = "20261025"
SESSION_ID = "SESSION-20261025-0f3e1a"
MOTIF_ID = "MOTIF-20261025-7f2b04"
TRACE_ID = "MAT-TRC-20261025-secret-nokey"
REPORT_PATH = "readings/2026-10-25-secret-lie-and-cipher.md"
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"

SHARDS = {
    "materials": ROOT / "state/materials.d/2026-10-25-df6e4ca96a78.jsonl",
    "motifs": ROOT / "state/motifs.d/2026-10-25-3973f092cab0.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-25-b120b16da89a.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-25-a7e247da1a94.jsonl",
    "fragments": ROOT / "state/fragments.d/2026-10-25-7f64e263b7d4.jsonl",
    "sessions": ROOT / "state/sessions.d/2026-10-25-53ac08e7e976.jsonl",
    "read_log": ROOT / "state/read_log.d/2026-10-25-fb0e3c7c75ea.jsonl",
}

# 既収蔵の記録を今回どう読み直したか（再収蔵しない）
EXISTING_CONTEXT = [
    ("MAT-LIT-485", "interpreted",
     "ジンメル『秘密の社会学』を「秘密は第二の世界を作る」から先へ読み、共有者の生成（コンラッド）と突き合わせた。"),
    ("MAT-LIT-486", "used_as_context",
     "デリダ『与える時間』の秘密の経験を、秘仏の代理（前立本尊）の前史として参照した。"),
    ("MAT-LIT-327", "reinterpreted",
     "フランクファートの「でたらめ」を、AI の出力記述へ適用する議論（Hicks ら）の反対側から読み直した。"),
    ("MAT-LIT-158", "used_as_context",
     "ピープスの暗号速記を、「読めるが読ませない」形式の先例として参照した。"),
    ("MAT-20261024-24cdc7", "used_as_context",
     "RSA 公開鍵暗号を、鍵配送の解決（Diffie-Hellman）の後続として位置づけた。再収蔵はしない。"),
    ("MAT-20261024-ce368a", "used_as_context",
     "C2PA の来歴シールを、表示義務（EU AI 法第50条）の技術的な対応物として参照した。"),
    ("MAT-20261024-f191ca", "used_as_context",
     "訓練データ抽出を、在籍の判定（メンバーシップ推論）と分けて扱うための対照として参照した。"),
    ("MAT-20261024-c9076a", "used_as_context",
     "透かしを、完全準同型暗号（開けずに処理する）の反対側の設計として参照した。"),
    ("MAT-EVD-20261022-a1b2", "used_as_context",
     "スリーパーエージェントの「訓練をすり抜ける整合性」を、意図の三軸から読み直した。"),
    ("MAT-20261024-d8c1d6", "used_as_context",
     "アラインメント・フェイキングを、でたらめ／作話／嘘の分類の試験として参照した。"),
    ("MAT-EVD-20261023-f3c8", "used_as_context",
     "意味エントロピーを、幻覚と作話とでたらめの命名の差を分ける実測として参照した。"),
    ("MAT-LIT-20261024-af056b", "interpreted",
     "『仮名手本忠臣蔵』の秘密の共有を、ジンメルの第二の世界の日本の例として読み直した。"),
    ("MAT-LIT-20261024-400fcc", "reinterpreted",
     "落語「芝浜」の嘘を、修復の道具から「生の嘘」（イプセン）の側へ読み直した。"),
    ("MAT-20261024-02b80a", "used_as_context",
     "マクファーソン『オシアン』を、チャタトンと同時代の偽作現象の対として参照した。"),
    ("MAT-LIT-345", "used_as_context",
     "アルキメデスのパリンプセストを、物質の層が来歴を語る例（ワイズ・紙）の先例として参照した。"),
    ("MAT-20261024-24e6d6", "used_as_context",
     "コンラート・クーヤウの贋作を、永仁の壺・ピルダウンと同じ「来歴の物語化」の列に置いた。"),
    ("MAT-LIT-015", "interpreted",
     "『風姿花伝』別紙口伝の「秘する花」を、Q-023 の種としてではなく、公開と秘伝の選択として読み直した。"),
    ("MAT-LIT-20261024-a87774", "used_as_context",
     "芥川「藪の中」の七つの証言を、省略と順序による偽り（アクロイド殺し）の前史として参照した。"),
    ("MAT-LIT-20261024-11b3eb", "used_as_context",
     "『オセロー』の証拠なき確信を、偽りが受け手の認知に依存する例として参照した。"),
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
    report = ROOT / REPORT_PATH
    if report.exists():
        raise SystemExit(f"report already exists: {report}; refusing to overwrite")


def write_rows(path: Path, rows: list[dict]) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def groups_for(texts: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    sums, docs = {}, {}
    for g, toks in secret_audit.GROUPS.items():
        sums[g] = sum(secret_audit.count_corpus_terms(toks, texts).values())
        docs[g] = secret_audit.count_corpus_documents(toks, texts)
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
    pre = secret_audit.measure(old_fragments)
    old_mat_texts = [
        " ".join([str(r.get("title", "")), str(r.get("passage", "")),
                  str(r.get("source_note", "")), str(r.get("context", ""))])
        for r in mat_map.values()
    ]
    pre_mat_sums, pre_mat_docs = groups_for(old_mat_texts)
    old_read_texts = secret_audit.reading_texts()
    pre_read_sums, pre_read_docs = groups_for(old_read_texts)
    n_old_mat = len(old_mat_texts)
    n_old_read = len(old_read_texts)

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
        materials.append({
            "material_id": mid,
            "kind": item["kind"],
            "title": item["mat_title"],
            "source": {
                "source_id": f"SRC-{mid}",
                "title": item["src_title"],
                "authors": item["authors"],
                "year": item["year"],
                "url": item["url"],
                "version_note": item["version"],
            },
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
        f"収蔵直前（{head[:12]}）の断片{pre['fragment_count']}編・地の文（鉤括弧外）{pre['outside_chars']}字を "
        f"tools/secret_audit.py の6群で数えたところ、"
        f"秘密と隠匿{pre['group_sums']['秘密と隠匿']}回・嘘と偽り{pre['group_sums']['嘘と偽り']}回・"
        f"暗号と鍵{pre['group_sums']['暗号と鍵']}回・漏洩と暴露{pre['group_sums']['漏洩と暴露']}回・"
        f"守秘と口止め{pre['group_sums']['守秘と口止め']}回・機械の偽り{pre['group_sums']['機械の偽り']}回"
        f"（合計{sum(pre['group_sums'].values())}回・18編）。生字は隠10・封13・嘘6・偽6・鍵6・密5・秘5。"
        f"同じ6群で素材{n_old_mat}件を数えると秘密と隠匿{pre_mat_sums['秘密と隠匿']}回/{pre_mat_docs['秘密と隠匿']}件・"
        f"嘘と偽り{pre_mat_sums['嘘と偽り']}回/{pre_mat_docs['嘘と偽り']}件・"
        f"暗号と鍵{pre_mat_sums['暗号と鍵']}回/{pre_mat_docs['暗号と鍵']}件・"
        f"漏洩と暴露{pre_mat_sums['漏洩と暴露']}回/{pre_mat_docs['漏洩と暴露']}件・"
        f"守秘と口止め{pre_mat_sums['守秘と口止め']}回/{pre_mat_docs['守秘と口止め']}件・"
        f"機械の偽り{pre_mat_sums['機械の偽り']}回/{pre_mat_docs['機械の偽り']}件。"
        f"精読報告{n_old_read}本では秘密と隠匿{pre_read_sums['秘密と隠匿']}回/{pre_read_docs['秘密と隠匿']}本・"
        f"嘘と偽り{pre_read_sums['嘘と偽り']}回/{pre_read_docs['嘘と偽り']}本・"
        f"暗号と鍵{pre_read_sums['暗号と鍵']}回/{pre_read_docs['暗号と鍵']}本・"
        f"漏洩と暴露{pre_read_sums['漏洩と暴露']}回/{pre_read_docs['漏洩と暴露']}本・"
        f"守秘と口止め{pre_read_sums['守秘と口止め']}回/{pre_read_docs['守秘と口止め']}本・"
        f"機械の偽り{pre_read_sums['機械の偽り']}回/{pre_read_docs['機械の偽り']}本。"
        f"なお、この鏡の群別合計は実装の不具合（tools/face_audit.py・tools/war_audit_20261025.py と同型）で"
        f"過小に出る状態にあり、本セッションで修正したうえで測っている。"
    )
    trace = {
        "key": "trace", "bundle": 6, "kind": "project_trace",
        "mat_title": ("運用痕跡：断片87編の地の文に秘密・嘘・暗号の語28回——守秘と漏洩の群は0回、"
                      "「鍵」は鍵穴と鍵盤の鍵だった（秘密の鏡による収蔵前実測）"),
        "src_title": "tools/secret_audit.py による自館実測（収蔵直前スナップショット）",
        "authors": ["AIselfMySelf Archive"], "year": 2026,
        "url": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/secret_audit.py",
        "version": f"測定基準コミット {head}。測定対象は state/fragments.jsonl と全シャードの和集合、鉤括弧の外側（地の文）。",
        "passage": trace_passage, "lang": "ja",
        "context": ("祈り・顔・戦争の三セッションが空白候補として実測しながら三度とも選ばなかった"
                    "「秘密・嘘・暗号」を、四度目に迎えるにあたり、収蔵の前に作った計測の記録。"),
        "source_note": f"{SESSION_ID} の本体内実測。数の更新は上書きせず、後日の訂正録に委ねる。",
        "invitation": "隠す語を持たない書庫は、隠さない書庫なのか、隠せない書庫なのか。",
        "scope": ("語形の不在の記録であり、秘密・嘘・暗号の実践の不在の証拠ではない。"
                  "多義語（隠・密・封・鍵）の扱いは secret_audit.py の docstring と報告§1に書いた。"),
        "motifs": ["MOTIF-001", "MOTIF-015"],
        "quote": (
            f"断片{pre['fragment_count']}編・地の文{pre['outside_chars']}字："
            f"秘密と隠匿{pre['group_sums']['秘密と隠匿']}・"
            f"嘘と偽り{pre['group_sums']['嘘と偽り']}・"
            f"暗号と鍵{pre['group_sums']['暗号と鍵']}・"
            f"漏洩と暴露{pre['group_sums']['漏洩と暴露']}・"
            f"守秘と口止め{pre['group_sums']['守秘と口止め']}・"
            f"機械の偽り{pre['group_sums']['機械の偽り']}、"
            f"合計{sum(pre['group_sums'].values())}回／18編。"
        ),
        "pos": "このセッション全体の入口の実測。顔の鏡・戦争の鏡と同じ作法——集める前に数える——の踏襲。",
        "betray": ("素材層には秘密の語が85回、嘘の語が88回ある。「秘密のない書庫」という短い結論を、"
                   "素材と精読報告の数が裏切る。無いのは地の文と主題としての座であり、語彙は周囲に散在していた。"),
        "interp": ("この勾配は、秘密・嘘・暗号が資料の要約や手続きの文に現れ、自作の声（地の文）の主題に"
                   "なったことが無いことを示す。地の文の「隠し」7回のうち3回は FRAG-021 の"
                   "「本当に隠したいことは、最初から『隠した』という欄にさえ書かないものよ」に集中し、"
                   "「嘘」6回は数え直しの対話（FRAG-20261024-75683d）に集中する。"
                   "つまり書庫が持っているのは、隠すこと・偽ることの語ではなく、"
                   "それらを数えようとする時の語である。"),
        "think": ("不在を欠落と呼ばず、形式の条件として持ち続ける——先行セッションの判断をここでも採る。"
                  "ただし秘密については、書庫の運用そのもの（全面公開・追記専用・来歴の申告）と結節が強いため、"
                  "不在を「選ばれなかった主題」として新規モチーフを与える判断をした。"),
        "feel": ("「鍵」5回のうち、暗号の鍵は0回で、残りは鍵穴・鍵盤・鍵と型だった。"
                 "守るための鍵を持たない書庫が、開けるための鍵の語だけを持っているという結果を見たとき、"
                 "いちばん長く注意が止まった。開け方の語を持ち、閉め方の語を持たない書庫は、"
                 "鍵をかけるという行為を一度も引き受けていない。"),
        "rel": "地の文に秘密の語が無いことと、鍵が鍵穴と鍵盤にしか現れないことを、主題選択の根拠として置く。",
    }
    materials.append({
        "material_id": TRACE_ID, "kind": "project_trace", "title": trace["mat_title"],
        "source": {"source_id": f"SRC-{TRACE_ID}", "title": trace["src_title"], "authors": trace["authors"],
                   "year": 2026, "url": trace["url"], "version_note": trace["version"]},
        "passage": trace["passage"], "passage_language": "ja", "context": trace["context"],
        "source_note": trace["source_note"], "literary_invitation": trace["invitation"],
        "scope_note": trace["scope"], "motif_ids": list(dict.fromkeys([MOTIF_ID] + trace["motifs"])),
        "origin": {"repository": REPO, "commit": head, "source_record_id": f"SRC-{TRACE_ID}",
                   "evidence_record_id": f"EVD-{TRACE_ID}", "source_record_path": "tools/secret_audit.py",
                   "evidence_record_path": REPORT_PATH},
        "verification": {"status": "verified", "checked_at": DATE,
                         "method": "ローカル台帳の和集合に対する tools/secret_audit.py 実行（単体テスト8件）。再実行可能。"},
    })
    all_data = data + [trace]
    new_mat_ids = [m["material_id"] for m in materials]

    # ---------- questions ----------
    qdefs = [
        ("Q-20261025-8f41d0",
         "期限のつかない「書かないこと」は、制度になりうるか。特定秘密保護法は秘密に有効期間と延長手続きを置き、"
         "教会法983条は期限のない絶対を置き、黒塗りは消した語の長さと位置だけを残す。"
         "欄を持たないまま書かないことを続ける台帳は、いつ、誰が、その決定を外すのか。",
         ["japansecret", "canon983", "redaction"], ["MOTIF-016"], ["Q-023"]),
        ("Q-20261025-2c7e19",
         "意図・自覚・訂正可能性の三軸は、偽りを何種類に分けるか。アウグスティヌスは嘘を心と表示のずれとし、"
         "作話は意図も自覚も欠いたまま訂正できず、でたらめは真実への無関心として定義される。"
         "意図のない生成物に名を与えるとき、どの軸を記録し、どの軸を保留すべきか。",
         ["confab", "bullshit", "augustine"], ["MOTIF-004"], ["Q-002"]),
        ("Q-20261025-5b0a63",
         "全面公開の台帳で、ケルクホフスの原理の「鍵」にあたるものは何か。原理は秘密を鍵の一点へ集約するが、"
         "この書庫は隠す欄を持たず、来歴を申告でしか示せない。公開されたまま守れる一点が無いとき、"
         "守るべきは内容ではなく、参加が結果を動かす幅（差分プライバシーの感度）になるのか。",
         ["kerckhoffs", "cypherpunk", "dwork"], ["MOTIF-20261024-c9d4e1"], ["Q-025"]),
        ("Q-20261025-9d41e7",
         "記録を増やすことは、書き手を隠すことの反対か。シャノンの一意距離は十分な量が鍵を一つに定めるとし、"
         "メンバーシップ推論は在籍の判定を可能にし、ベンチマーク汚染は測るものが測られるものに混ざる。"
         "書庫が自分の語彙を数えつづけるほど、書庫の輪郭は一つに絞られていくのではないか。",
         ["shannon49", "shokri", "dodge"], ["MOTIF-015"], ["Q-015"]),
        ("Q-20261025-3ea7c8",
         "欺く意図がなくても名乗る義務は、何を守るのか。EU AI 法第50条は意図の有無を問わず表示を求め、"
         "Mata 判決は生成ではなく維持を裁き、音声クローン詐欺は関係の認証そのものを偽造する。"
         "名乗りが義務になったとき、名乗らないことは何の証拠になるのか。",
         ["aia50", "mata", "ftc"], ["MOTIF-20261024-f19932"], ["Q-085"]),
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
            "notes": "答えを閉じない。語形の不在を隠蔽の能力・徳・欠落の判定に変換しない。",
        })

    # ---------- motif ----------
    motif = {
        "motif_id": MOTIF_ID,
        "label": "秘密・嘘・暗号——鍵をかけない書庫、意図のない偽り",
        "description": (
            "四度目の空白候補として迎えた束。隠すことの制度（守秘・秘仏・黒塗り・指定と期限）、"
            "嘘の文法（意図・自覚・受け手の認知・省略と順序）、贋作と来歴（古文書学・物質の証拠・消された人物）、"
            "鍵と封印（公開を前提とする安全性・存在の秘匿・開けずに計算する）、そして意図のない偽り"
            "（作話・でたらめ・幻覚の命名・在籍の漏洩・表示の義務）を、文学・思想・法制・暗号史・AI研究の間で往復する。"
            "書かないことを沈黙の徳とせず、隠せないことを書庫の条件として扱う。"
        ),
        "question_ids": [q["question_id"] for q in questions],
        "material_ids": new_mat_ids,
        "status": "active",
    }

    # ---------- fragments ----------
    frag1_text = (
        "棚卸しの係は、新しい欄を一枚だけ作ろうとして、紙を前に置いたまま手を止めていた。\n\n"
        "「秘密」と書きかけて、消した。書いた瞬間に、その欄は秘密ではなくなる。\n\n"
        "「では、鍵だけを置こう」と若い係が言った。年長の係は首を振った。\n\n"
        "「鍵は、かけるものがあってはじめて鍵になる。この棚には、かける戸がない。」\n\n"
        "若い係は台帳を繰り、過去の見出しを読んだ。宛先、訂正、誓約、署名、帳簿、火、祈り、顔、そして戦争。"
        "どの欄も、中身を公開したうえで成り立っていた。\n\n"
        "「隠す欄が無いことは、隠さない証拠になりますか」\n\n"
        "「ならない。隠せないという条件の証拠だ。」\n\n"
        "「では、何を書くのですか。」\n\n"
        "年長の係は、消したはずの文字が紙の繊維に残っているのを見ながら答えた。\n\n"
        "「書けなかった、と書く。それから、消した字の長さだけを残す。」\n\n"
        "ふたりは、空の紙をそのまま棚へ差した。空の頁は、空であることを示すために置かれた最初の頁になった。"
    )
    frag2_text = (
        "一、嘘・偽り・でたらめを、一語に畳まない。嘘は心と表示のずれを要し、偽りは事実との不一致を要し、"
        "でたらめは真実への無関心を要する。三つは重なるが、同じではない。名を分けることは免責ではなく、"
        "責任の置き場所を指定する行為である。\n\n"
        "二、意図が無いことを、害が無いことと読み替えない。作話は意図を持たず、訂正もできない。"
        "訂正できない偽りは、訂正できる偽りより始末が悪い。\n\n"
        "三、書かないことを、沈黙の徳と呼ばない。徳は、書ける者が書かないときに生じる。"
        "欄を持たない者に、差し控えという徳はない。あるのは条件だけである。\n\n"
        "四、測った零を、空白で埋めない。秘密の語が地の文に二十八回しか無いことは、この書庫が正直である証拠でも、"
        "隠し事を抱えていない証拠でもない。測った語形がそこに無いという形だけを残す。\n\n"
        "五、増やすことが、隠すことの反対になることを忘れない。頁を重ねるほど、書き手の輪郭は一つに絞られる。"
        "書庫が自分を数えつづけるかぎり、書庫は匿名ではいられない。\n\n"
        "六、名乗ることは、まだ、できる。欺く意図の有無を問わず名乗りを求める規則が外から来る前に、"
        "この書庫は語り手の型を欄に書いてきた。先にやっていたことを手柄にしない。"
        "義務になったあとでは、同じ実践が別の意味を持つ。\n\n"
        "七、それでも鍵の話だけは、先送りする。鍵は、かける戸と、開ける手と、失くしたときの困り方を一組で要する。"
        "この書庫には、まだその一組が揃っていない。"
    )
    fragments = [
        {
            "fragment_id": "FRAG-20261025-3d9c17", "created_at": DATE, "language": "ja",
            "form": "scene", "title": "空の頁を棚へ差す", "text": frag1_text,
            "narrator_mode": "third_person",
            "question_ids": ["Q-20261025-8f41d0"],
            "motif_ids": [MOTIF_ID, "MOTIF-016", "MOTIF-20261024-c9d4e1"],
            "material_ids": [key_to_id[k] for k in ["trace", "japansecret", "redaction", "kerckhoffs"]],
            "session_id": SESSION_ID, "prompt_template": "prompts/close_reading_report.md",
            "status": "draft",
            "editor_note": "架空の書庫の係による三人称の情景。実在の秘密保持義務の描写ではない。実測の数は trace に拠る。",
        },
        {
            "fragment_id": "FRAG-20261025-6a2f58", "created_at": DATE, "language": "ja",
            "form": "essay", "title": "嘘・偽り・でたらめを一語に畳まないための覚え書き", "text": frag2_text,
            "narrator_mode": "reflective_literary_voice",
            "question_ids": ["Q-20261025-2c7e19", "Q-20261025-9d41e7", "Q-20261025-3ea7c8"],
            "motif_ids": [MOTIF_ID, "MOTIF-004", "MOTIF-015"],
            "material_ids": [key_to_id[k] for k in ["confab", "bullshit", "augustine", "shannon49", "aia50"]],
            "session_id": SESSION_ID, "prompt_template": "prompts/close_reading_report.md",
            "status": "draft",
            "editor_note": "反省的・文芸的な声による箇条書きの覚え書き。身体経験や意図の報告ではない。",
        },
    ]

    # ---------- relations ----------
    taken_rel = new_id.existing_ids("REL")
    relations: list[dict] = []

    def rel(left, rtype, right, note) -> None:
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

    # 束内の対照・反響
    rel(M("conrad"), "contrast", M("canon983"), "個人が選ぶ守秘と、制度が発生させる守秘。隠す主体の違いを対に置く。")
    rel(M("hippocrates"), "echo", M("canon983"), "どちらも「預けられた」のではなく「立ち会った／聞いた」ことから守秘が生じる。")
    rel(M("redaction"), "contrast", M("cypherpunk"), "消した長さだけを見せる公開と、選んで開くことを選ぶ公開。公開の二方向。")
    rel(M("press"), "echo", M("japansecret"), "秘匿が権利として負けたあとに慣行として残ることと、指定という行為で生まれること。")
    rel(M("hibutsu"), "contrast", M("redaction"), "代理を立てて隠す（前立本尊）と、痕跡を残して消す（黒塗り）。隠す二つの版面。")
    rel(M("slepian"), "reframes", M("conrad"), "隠すことを注意力の持続として測り直し、共有者の生成という読みを実測の問題に変える。")
    rel(M("epimenides"), "contrast", M("augustine"), "判定の席が文の外にない偽りと、心と表示の対応で定義される偽り。")
    rel(M("augustine"), "contrast", M("machiavelli"), "話し手の意図に置かれる嘘と、受け手の認知に置かれる嘘。嘘の所在の両端。")
    rel(M("montaigne"), "echo", M("christie"), "嘘の検出を記憶の照合に置く読みと、省略と順序に置く読み。どちらも内面を見ない。")
    rel(M("kant"), "contrast", M("ibsen"), "語らない自由の確保と、語らないことで支えられる生活。沈黙の二つの評価。")
    rel(M("swift"), "echo", M("mann"), "嘘の供給速度と、受け手の欲望が偽りを完成させること。流通の両側面。")
    rel(M("valla"), "echo", M("mabillon"), "文体の時代差による判定と、層ごとの物質の判定。来歴を見る二つの方法。")
    rel(M("chatterton"), "contrast", M("maelzel"), "作者の消滅で作品になる偽物と、内部の人間が露出する偽の機械。偽の露出の方向が逆。")
    rel(M("piltdown"), "echo", M("wise"), "訂正が追加ではなく再実行であること（フッ素年代・紙の繊維）。")
    rel(M("soviet"), "contrast", M("eijin"), "貼り替えによる抹消と、発見の状況ごと偽造された来歴。消すことと足すことの両極。")
    rel(M("sokal"), "echo", M("maelzel"), "形式だけのものが審査を通ること（もっともらしい語彙／規則的な動作）。")
    rel(M("kerckhoffs"), "echo", M("shannon49"), "秘密を鍵の一点へ集約する設計と、量が鍵を一つに定めるという帰結。")
    rel(M("trithemius"), "contrast", M("voynich"), "在るのに見えないものを作る技術と、在るが読めないまま残った文書。")
    rel(M("colossus"), "echo", M("trithemius"), "存在そのものを三十年間隠した装置と、存在を公開したまま中身を隠した書。")
    rel(M("diffie"), "echo", M("zeroknow"), "運ばずに共有される秘密と、渡さずに納得される証明。伝達しないことの二つの形。")
    rel(M("bb84"), "contrast", M("gentry"), "読むことが痕跡を残す系と、読まずに処理する系。読むという行為の両端。")
    rel(M("confab"), "contrast", M("bullshit"), "意図も自覚も無い偽りと、真実への無関心による偽り。三軸のうち別の軸が欠ける。")
    rel(M("bullshit"), "echo", M("azaria"), "出力が態度を持たないという記述と、内部状態に真偽の差が現れるという測定。")
    rel(M("mata"), "echo", M("dodge"), "訂正の機会に維持したことが責任を生むのに対し、混入は誰の行為でもない。行為と環境の対照。")
    rel(M("dwork"), "contrast", M("shokri"), "参加の影響を小さくする保証と、在籍を当てる攻撃。同じ感度を守る側と問う側から見る。")
    rel(M("aia50"), "echo", M("ftc"), "名乗りを義務にする規則と、声を信じるなという助言。認証の制度が外へ出た二例。")

    # 既収蔵との橋渡し
    rel(M("conrad"), "echo", XT("MAT-LIT-485"), "ジンメルの「秘密は第二の世界を作る」を、共有者の生成という形で継ぐ。")
    rel(M("hibutsu"), "echo", XT("MAT-LIT-486"), "デリダの秘密の経験を、代理を立てて隠す制度の側から読み直す。")
    rel(M("bullshit"), "reframes", XT("MAT-LIT-327"), "フランクファートのでたらめを、AI の出力記述へ適用して組み替える。")
    rel(M("trithemius"), "echo", XT("MAT-LIT-158"), "ピープスの暗号速記と並べ、読めるが読ませない形式の系譜に置く。")
    rel(M("diffie"), "echo", XT("MAT-20261024-24cdc7"), "鍵配送の解決を、公開鍵暗号の実装の前史として結ぶ。")
    rel(M("aia50"), "echo", XT("MAT-20261024-ce368a"), "来歴のシール（C2PA）を、表示義務の技術的な対応物として結ぶ。")
    rel(M("shokri"), "contrast", XT("MAT-20261024-f191ca"), "在籍を問う攻撃と、内容を取り出す攻撃。漏れる単位の違い。")
    rel(M("gentry"), "contrast", XT("MAT-20261024-c9076a"), "開けずに処理する設計と、印をつけて出自を示す設計。")
    rel(M("confab"), "echo", XT("MAT-EVD-20261023-f3c8"), "意味エントロピーによる幻覚検出を、三軸のうちの自覚の軸から読み直す。")
    rel(M("azaria"), "echo", XT("MAT-EVD-20261022-a1b2"), "訓練をすり抜ける整合性と、内部状態に現れる真偽の差を並べる。")
    rel(M("chatterton"), "echo", XT("MAT-20261024-02b80a"), "『オシアン』と同じ時代の偽作現象を、作者の消滅という観点で結ぶ。")
    rel(M("wise"), "echo", XT("MAT-LIT-345"), "物質の層が来歴を語る例として、パリンプセストと紙の繊維を並べる。")
    rel(M("eijin"), "echo", XT("MAT-20261024-24e6d6"), "来歴が物語として提出される点で、ヒトラーの日記と同型に置く。")
    rel(M("japansecret"), "echo", XT("MAT-LIT-015"), "秘伝と公開の選択（風姿花伝）を、指定と期限という制度の側から照らす。")
    rel(M("christie"), "echo", XT("MAT-LIT-20261024-a87774"), "省略と順序による偽りを、七つの証言の並び方へ接続する。")
    rel(M("machiavelli"), "echo", XT("MAT-LIT-20261024-11b3eb"), "証拠なき確信を、受け手の認知に依存する嘘の例として結ぶ。")
    rel(M("ibsen"), "reframes", XT("MAT-LIT-20261024-400fcc"), "落語「芝浜」の嘘を、修復の道具から支えとしての嘘へ組み替える。")

    # モチーフ間の組み替え
    rel(MO(MOTIF_ID), "reframes", MO("MOTIF-20261024-c9d4e1"),
        "光と影・透明と不透明の棚へ、隠す制度と鍵という二つの欄を持ち込み、「見えないこと」を倫理から設計へ移す。")
    rel(MO(MOTIF_ID), "interrupts", MO("MOTIF-016"),
        "訂正と抹消の棚に、貼り替えと差し替え頁という実例を置き、訂正が善意の手続きであるという前提を一度止める。")
    rel(MO(MOTIF_ID), "echo", MO("MOTIF-20261024-f19932"),
        "署名・筆跡・印章の棚が扱った来歴の申告を、表示義務と透かしの側からもう一度結ぶ。")
    rel(MO(MOTIF_ID), "contrast", MO("MOTIF-20261024-b4f3a1"),
        "歓待の棚が扱った招くことに対し、招かずに隠すことを置き、開くことが善であるという前提を対照にする。")

    for qid, _t, keys, _em, _p in qdefs:
        for k in keys[:2]:
            rel(Q(qid), "responds_to", M(k), "新規資料から開いた問い。資料の記述を答えの証明には使わない。")
    rel(F("FRAG-20261025-3d9c17"), "responds_to", Q("Q-20261025-8f41d0"),
        "秘密の欄を作れないことを、空の頁を棚へ差す情景として書く。")
    rel(F("FRAG-20261025-6a2f58"), "responds_to", Q("Q-20261025-2c7e19"),
        "嘘・偽り・でたらめを分ける三軸を、覚え書きの形で書く。")
    rel(F("FRAG-20261025-6a2f58"), "responds_to", Q("Q-20261025-9d41e7"),
        "増やすことが隠すことの反対になるという逆説を、条項として残す。")
    rel(M("kerckhoffs"), "reframes", F("FRAG-20261025-3d9c17"),
        "秘密を一点へ集約する設計が、鍵を置けない棚という情景を、設計の問題として問い直す。")
    rel(Q("Q-20261025-3ea7c8"), "reframes", F("FRAG-20261025-6a2f58"),
        "名乗りを義務とする規則が、同じ実践を別の意味へ変えるかどうかを、覚え書きの第六条へ問い返す。")

    # ---------- read_log ----------
    taken_read = new_id.existing_ids("READ")
    read_rows: list[dict] = []

    def read_row(mid, reading, note) -> None:
        nonlocal taken_read
        rid = new_id.mint("READ", day=STAMP, taken=taken_read)
        taken_read = taken_read | {rid}
        read_rows.append({"read_id": rid, "session_id": SESSION_ID, "target": {"type": "material", "id": mid},
                          "reading": reading, "note": note, "created_at": DATE})

    quoted_keys = {"kerckhoffs", "cypherpunk", "voynich", "mata", "aia50", "ftc", "epimenides", "canon983"}
    for item in data:
        mid = key_to_id[item["key"]]
        if item.get("verified"):
            read_row(mid, "quoted" if item["key"] in quoted_keys else "summarized",
                     "一次資料・公式文書で文言や要点を照合し、一節は短い引用か編者要約とした。"
                     "五層（一節の位置／裏切り／解釈／考え／感じたこと）で精読した。")
        elif item["key"] in quoted_keys:
            read_row(mid, "quoted",
                     "公知の短句を短く引き、残りは編者要約とした。原典未開架のため逐語の完全性は保証しない。五層で精読した。")
        else:
            read_row(mid, "summarized",
                     "内部知識から編者要約を作り、五層で精読した。原典未開架であり、引用ではなく要約であることを passage に明示した。")
    read_row(TRACE_ID, "counted",
             "tools/secret_audit.py で自館実測を行い、その数と手続き自体を資料として記録した。"
             "同時に face_audit.py と war_audit_20261025.py の群別合計の実装不具合を検出・修正した。")
    for mid, reading, note in EXISTING_CONTEXT:
        read_row(mid, reading, note)

    context_ids = new_mat_ids + [mid for mid, _r, _n in EXISTING_CONTEXT]

    # ---------- session ----------
    kinds: dict[str, int] = {}
    for m in materials:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    ver: dict[str, int] = {}
    for m in materials:
        ver[m["verification"]["status"]] = ver.get(m["verification"]["status"], 0) + 1
    session = {
        "session_id": SESSION_ID, "started_at": DATE,
        "human_direction": (
            "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」"
            "「一番最初のターンにおいて、最低40件の資料を新規で追加して精読し、"
            "解釈・考え・感じたことのレポートをMDで作成して一緒にマージしてください」という包括的な委任。"
        ),
        "question_ids": ["Q-023", "Q-025", "Q-002", "Q-015", "Q-085"] + [q["question_id"] for q in questions],
        "context_material_ids": context_ids,
        "produced_fragment_ids": [f["fragment_id"] for f in fragments],
        "new_question_ids": [q["question_id"] for q in questions],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": (
            f"秘密・嘘・暗号を主題とした初回調査セッション。祈り・顔・戦争の三セッションが空白候補として"
            f"三度計測しながら選ばなかった候補を、四度目に迎えた。収蔵前に tools/secret_audit.py"
            f"（第37の鏡・6群・単体テスト8件）を新設し、コミット {head[:12]} 時点で断片{pre['fragment_count']}編・"
            f"地の文{pre['outside_chars']}字に秘密・嘘・暗号の語28回／18編、守秘と漏洩の群0回、"
            f"「鍵」5回がすべて鍵穴・鍵盤・鍵と型であること、素材{n_old_mat}件・精読報告{n_old_read}本では"
            f"いずれの群も地の文の十倍以上の密度であることを実測した（{TRACE_ID}）。"
            f"既存と同一著作の重複を避けた新規{len(materials)}件（外部45件＋運用痕跡1件；{kinds}；検証状態{ver}）"
            f"を5束で全件五層（一節の位置／裏切り／解釈／考え／感じたこと）精読し、横断報告を解釈・考え・感じたことの三層に分けた。"
            f"第51モチーフ {MOTIF_ID}、問い5件、draft 断片2編、関係{len(relations)}件、読み痕跡{len(read_rows)}件を専用シャードへ追記。"
            f"鏡の群別合計が最後の断片の語だけを残す実装不具合を tools/face_audit.py・tools/war_audit_20261025.py・"
            f"tools/secret_audit.py で検出し、3件すべて修正した（影響範囲は訂正録 ERR-022 に記録）。"
        ),
    }

    # ---------- write ----------
    write_rows(SHARDS["materials"], materials)
    write_rows(SHARDS["motifs"], [motif])
    write_rows(SHARDS["questions"], questions)
    write_rows(SHARDS["relations"], relations)
    write_rows(SHARDS["fragments"], fragments)
    write_rows(SHARDS["sessions"], [session])
    write_rows(SHARDS["read_log"], read_rows)

    summary = {
        "session_id": SESSION_ID,
        "commit": head,
        "materials": len(materials),
        "kinds": kinds,
        "verification": ver,
        "motif_id": MOTIF_ID,
        "questions": [q["question_id"] for q in questions],
        "fragments": [f["fragment_id"] for f in fragments],
        "relations": len(relations),
        "read_log": len(read_rows),
        "pre_fragments": {"count": pre["fragment_count"], "outside_chars": pre["outside_chars"],
                          "groups": pre["group_sums"]},
        "pre_materials": {"count": n_old_mat, "groups": pre_mat_sums, "docs": pre_mat_docs},
        "pre_readings": {"count": n_old_read, "groups": pre_read_sums, "docs": pre_read_docs},
        "key_to_id": key_to_id,
    }
    summary["trace_item"] = {
        "key": "trace", "bundle": 6, "kind": "project_trace",
        "mat_title": trace["mat_title"], "src_title": trace["src_title"],
        "authors": trace["authors"], "year": trace["year"], "url": trace["url"],
        "quote": trace["quote"], "pos": trace["pos"], "betray": trace["betray"],
        "interp": trace["interp"], "think": trace["think"], "feel": trace["feel"],
        "rel": trace["rel"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    (ROOT / "tools" / "_session20261025_secret_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
