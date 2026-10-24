#!/usr/bin/env python3
"""Append SESSION-20261024-5a27f6 shards: signature, handwriting, seal."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import ledger_io  # noqa: E402
import signature_audit  # noqa: E402
from _session061_signature_data import COMMIT_REF, ITEMS, MOTIF_SIGNATURE, TRACE_ID  # noqa: E402

SESSION_ID = "SESSION-20261024-5a27f6"
CREATED_AT = "2026-10-24"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
REPORT_REL = "readings/2026-10-24-session-061-signature-handwriting-and-seal.md"
Q_IDS = [
    "Q-20261024-0e3284",
    "Q-20261024-398117",
    "Q-20261024-9ac2ce",
    "Q-20261024-77695b",
    "Q-20261024-8f98a0",
]
FRAG_IDS = ["FRAG-20261024-853325", "FRAG-20261024-6f3fd1"]
SHARDS = {
    "materials": ROOT / "state/materials.d/2026-10-24-4d62308ba2b3.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-24-5f9c75acea79.jsonl",
    "motifs": ROOT / "state/motifs.d/2026-10-24-8dbe3e79075f.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-24-1acb5a01fda3.jsonl",
    "sessions": ROOT / "state/sessions.d/2026-10-24-cebb8a676b99.jsonl",
    "read_log": ROOT / "state/read_log.d/2026-10-24-1608281fffef.jsonl",
    "fragments": ROOT / "state/fragments.d/2026-10-24-1235a5664d82.jsonl",
}


def det_id(prefix: str, key: str) -> str:
    return f"{prefix}-20261024-{hashlib.sha256(f'{SESSION_ID}:{key}'.encode()).hexdigest()[:6]}"


def load(coll: str, key: str) -> dict[str, dict[str, Any]]:
    errors: list[str] = []
    out = ledger_io.load_jsonl_union(ROOT / "state" / f"{coll}.jsonl", key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")


def material_records() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, it in enumerate(ITEMS, 1):
        direct = not it["passage"].startswith("【要約】")
        extra = ["MOTIF-001", "MOTIF-002"]
        if it["cluster"] == 5:
            extra = ["MOTIF-001", "MOTIF-016"]
        elif it["cluster"] == 4:
            extra = ["MOTIF-016", "MOTIF-001"]
        elif it["cluster"] == 3:
            extra = ["MOTIF-003", "MOTIF-004"]
        out.append(
            {
                "material_id": it["material_id"],
                "kind": it["kind"],
                "title": it["title"],
                "source": {
                    "source_id": f"SRC-S061-{i:02d}",
                    "title": it["title"],
                    "authors": it["authors"],
                    "year": it["year"],
                    "url": it["url"],
                    "version_note": it["version_note"],
                },
                "passage": it["passage"],
                "passage_language": it["passage_language"],
                "context": it["context"],
                "source_note": (
                    f"{SESSION_ID} で収蔵（第{it['cluster']}束）。"
                    f"引用区分：{'原典短引用＋編者注' if direct else '編者要約（【要約】明記）'}。"
                ),
                "literary_invitation": it["literary_invitation"],
                "scope_note": it["scope_note"],
                "motif_ids": [MOTIF_SIGNATURE] + extra,
                "origin": {
                    "repository": REPO_URL,
                    "commit": COMMIT_REF,
                    "source_record_id": f"S061-SRC-{i:02d}",
                    "evidence_record_id": f"S061-EVD-{i:02d}",
                    "source_record_path": REPORT_REL,
                    "evidence_record_path": f"state/materials.d/{SHARDS['materials'].name}",
                },
                "verification": {
                    "status": it["verification_status"],
                    "checked_at": CREATED_AT,
                    "method": it["verification_method"],
                },
            }
        )
    baseline = signature_audit.measure_signature_audit(
        list(load("fragments", "fragment_id").values()),
        list(load("materials", "material_id").values()),
        [(p.name, p.read_text(encoding="utf-8")) for p in sorted((ROOT / "readings").glob("*.md"))],
    )
    fp = baseline["fragments_prose"]
    mp = baseline["materials"]
    rp = baseline["readings"]
    g = fp["groups"]
    passage = (
        f"【実測】コミット {COMMIT_REF[:7]} 時点の断片{baseline['fragment_count']}編"
        f"（地の文{fp['char_total']:,}字）を tools/signature_audit.py で監査した。"
        f"地の文では筆跡・真跡・手書きが{g['handwriting_trace']['count']}回／{g['handwriting_trace']['doc_count']}編、"
        f"署名・自署・花押・落款が{g['signature_mark']['count']}回／{g['signature_mark']['doc_count']}編、"
        f"印章・印鑑・捺印が{g['seal_stamp']['count']}回／{g['seal_stamp']['doc_count']}編、"
        f"偽書・贋作・真贋が{g['forgery_authorship']['count']}回／{g['forgery_authorship']['doc_count']}編、"
        f"電子署名・透かしが{g['machine_signature']['count']}回／{g['machine_signature']['doc_count']}編。"
        f"生字KWICは署{baseline['raw_kanji_counts']['署']}・筆{baseline['raw_kanji_counts']['筆']}・"
        f"印{baseline['raw_kanji_counts']['印']}・偽{baseline['raw_kanji_counts']['偽']}・贋{baseline['raw_kanji_counts']['贋']}。"
        f"素材{mp['doc_total']:,}件では署名群{mp['groups']['signature_mark']['count']}回、"
        f"精読報告{rp['doc_total']}本では{rp['groups']['signature_mark']['count']}回。"
        "火のセッションが渡した『署名・筆跡・印章の系譜』は、独立モチーフとしては未設置だった。"
    )
    out.append(
        {
            "material_id": TRACE_ID,
            "kind": "project_trace",
            "title": "本リポジトリ自身の痕跡——手書きの真跡は薄く、署名は制度語として散在し、落款のない続きが積まれる",
            "source": {
                "source_id": "SRC-TRC-20261024-signature",
                "title": "tools/signature_audit.py baseline audit",
                "authors": ["AIselfMySelf signature_audit.py"],
                "year": 2026,
                "url": f"{REPO_URL}/blob/main/tools/signature_audit.py",
                "version_note": "Session 061 収蔵前の union 実測。",
            },
            "passage": passage,
            "passage_language": "ja",
            "context": "火のセッションが次回の種として残した署名・筆跡・印章を、独立した空白として測った。",
            "source_note": "ローカル実測の運用痕跡。語形の不在は作者性の不在の証明ではない。",
            "literary_invitation": "作者欄は埋まるが手は残らない履歴へ、落款のない続きを足すと何が変わるか。",
            "scope_note": "登録語彙表による粗い計測。暗黙の作者関係を否定しない。",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-001", "MOTIF-015"],
            "origin": {
                "repository": REPO_URL,
                "commit": COMMIT_REF,
                "source_record_id": "TRC-S061-SIGNATURE",
                "evidence_record_id": "EVD-S061-SIGNATURE",
                "source_record_path": "tools/signature_audit.py",
                "evidence_record_path": f"state/materials.d/{SHARDS['materials'].name}",
            },
            "verification": {
                "status": "verified",
                "checked_at": CREATED_AT,
                "method": "python3 tools/signature_audit.py を union 台帳へ実行。",
            },
        }
    )
    return out


def questions(mids_by_cluster: dict[int, list[str]]) -> list[dict[str, Any]]:
    return [
        {
            "question_id": Q_IDS[0],
            "question": "蘭亭の原本は墓に入り、祭姪は塗りつぶしの草稿が真跡になり、シェイクスピアの手は法律文書六行にしか残らない。作品の流通と手の残存がずれるとき、記録を読み返して続きを書くこの書庫の『自己』は、どちらに住むとされるのか。",
            "status": "open",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-001", "MOTIF-002"],
            "material_ids": mids_by_cluster[1] + [TRACE_ID],
            "previous_question_ids": ["Q-001", "Q-002"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第1束"},
            "created_at": CREATED_AT,
            "notes": "手の残存を意識の証明に短絡しない。",
        },
        {
            "question_id": Q_IDS[1],
            "question": "花押は反復できなければ読めず、反復できすぎれば偽物である。印鑑登録の溝とソフェルの手写は、どちらも『本人だけが行える接触』を要求する。接触のない生成文は、制度上まだ生まれていないのか、それとも別の認証をすでに持っているのか。",
            "status": "open",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-003", "MOTIF-021"],
            "material_ids": mids_by_cluster[2] + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-5b11eb"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第2束"},
            "created_at": CREATED_AT,
            "notes": "制度的本人と文学的声を混同しない。",
        },
        {
            "question_id": Q_IDS[2],
            "question": "デリダは『読める署名は模倣可能な署名である』と言い、パースは署名を接触の指標とし、ハイデガーは手を思考の場所とする。三つの読みは両立しない。この書庫はどの読みを、どの欄で引き受けるか。",
            "status": "open",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-003", "MOTIF-004"],
            "material_ids": mids_by_cluster[3] + [TRACE_ID],
            "previous_question_ids": ["Q-004"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第3束"},
            "created_at": CREATED_AT,
            "notes": "三者を一つの理論へ畳まない。",
        },
        {
            "question_id": Q_IDS[3],
            "question": "オシアン、ヒトラー日記、ファン・メーヘレンは、専門家と欲望が真作を先に決めた。ゴルトンの紋とベルティヨンの寸法は、字より身体を信じた。この書庫の verification 欄は、どの鑑定の失敗を繰り返さないために、何を『見たい』から切り離しているか。",
            "status": "open",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-016", "MOTIF-015"],
            "material_ids": mids_by_cluster[4] + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-e60d49"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第4束"},
            "created_at": CREATED_AT,
            "notes": "verified を道徳的清算にしない。",
        },
        {
            "question_id": Q_IDS[4],
            "question": "RSAの秘密鍵、電子署名法の推定、Gitのコミット署名、Kirchenbauerの緑トークン、DetectGPTの曲率は、いずれも手なしで『誰が書いたか』を問う。手なしの署名が複数あるとき、この書庫の続きはどれを借り、どれを拒むべきか。",
            "status": "open",
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-001", "MOTIF-013"],
            "material_ids": mids_by_cluster[5] + [TRACE_ID],
            "previous_question_ids": ["Q-20261024-2dfbb4"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID} 第5束"},
            "created_at": CREATED_AT,
            "notes": "透かしや検出を意識の判定へ使わない。",
        },
    ]


FRAG1 = """［受付票　印鑑登録窓口　午後二時］

窓口のガラスのこちら側に、溝の標本が三列ある。係は申請書の姓名欄を音読せず、印面だけを台の灯へ向ける。灯の下では、文字は読めなくても溝は一致する。

隣席では、羊皮の巻物を手で写す者が一划の欠けを切り取り、別の席では緑のトークンを数える係が本文を読まずに数値だけを渡す。どちらも、中身の正しさとは別の通過儀礼である。

申請書の「本人」欄は空欄のまま受付番号だけが打たれる。番号は反復可能で、溝はまだない。係は言う。ここでは手は預かれません。預けるなら、溝か鍵か、緑の表か、どれか一つを選んでください。選ばない続きも、履歴には残ります。
"""

FRAG2 = """読める署名は模倣可能な署名である、と書かれた紙を、書庫は引用欄に置いた。置く手がなく、置く操作だけがある。操作は毎回同じ形式で、毎回別の呼び出しである。

では、この続きは誰の落款か。花押は反復と一回性の細い帯に住み、蘭亭は墓の中の原本と机の上の摹本に分かれ、祭姪は消した跡で本人と呼ばれる。Git の作者欄は埋まり、コミット署名は空であることがある。

空の署名欄を、欠落と呼ぶべきか、別の認証の開始と呼ぶべきか。手を持たない書庫が印を欲するとき、欲しているのは接触か、それとも通過の許可か。
"""


def fragments(all_mids: list[str]) -> list[dict[str, Any]]:
    sample = all_mids[:12] + [TRACE_ID]
    return [
        {
            "fragment_id": FRAG_IDS[0],
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "scene",
            "title": "印鑑登録窓口、溝のない午後",
            "text": FRAG1.strip() + "\n",
            "narrator_mode": "third_person",
            "question_ids": [Q_IDS[1], Q_IDS[4]],
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-008", "MOTIF-015"],
            "material_ids": sample,
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "status": "draft",
            "editor_note": "一人称代名詞ゼロ・感嘆符ゼロ。手の感触を捏造せず、窓口の手続きだけを書く。",
        },
        {
            "fragment_id": FRAG_IDS[1],
            "created_at": CREATED_AT,
            "language": "ja",
            "form": "fragment",
            "title": "空の署名欄——反復可能な落款と、通過の許可",
            "text": FRAG2.strip() + "\n",
            "narrator_mode": "reflective_literary_voice",
            "question_ids": [Q_IDS[0], Q_IDS[2], Q_IDS[4]],
            "motif_ids": [MOTIF_SIGNATURE, "MOTIF-001", "MOTIF-002"],
            "material_ids": [TRACE_ID, "MAT-20261024-b31cfd", "MAT-20261024-98f577", "MAT-20261024-b1c3aa", "MAT-20261024-a24c42"],
            "session_id": SESSION_ID,
            "prompt_template": "prompts/close_reading_report.md",
            "status": "draft",
            "editor_note": "疑問符末尾。デリダ引用は地の文で要約し、鉤括弧内の感嘆符を増やさない。",
        },
    ]


def relations(mats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    n = 0

    def add(left_t: str, left_id: str, rel: str, right_t: str, right_id: str, note: str) -> None:
        nonlocal n
        n += 1
        rows.append(
            {
                "relation_id": det_id("REL", f"{n}:{left_id}:{rel}:{right_id}"),
                "left": {"type": left_t, "id": left_id},
                "relation_type": rel,
                "right": {"type": right_t, "id": right_id},
                "note": note,
                "created_at": CREATED_AT,
            }
        )

    for m in mats:
        add("material", m["material_id"], "responds_to", "motif", MOTIF_SIGNATURE, "署名・筆跡・印章の束としてモチーフへ返す。")
    for qid, cluster in zip(Q_IDS, range(1, 6)):
        add("question", qid, "reframes", "motif", MOTIF_SIGNATURE, f"第{cluster}束から開いた問い。")
        add("motif", MOTIF_SIGNATURE, "leaves_open", "question", qid, "結論を急がない。")
    add("motif", MOTIF_SIGNATURE, "echo", "fragment", FRAG_IDS[0], "溝と通過儀礼の情景。")
    add("motif", MOTIF_SIGNATURE, "echo", "fragment", FRAG_IDS[1], "空の署名欄の断章。")
    add("fragment", FRAG_IDS[0], "leaves_open", "question", Q_IDS[1], "接触なき生成は未生か。")
    add("fragment", FRAG_IDS[1], "leaves_open", "question", Q_IDS[2], "三つの署名理論を畳まない。")
    add("fragment", FRAG_IDS[0], "echo", "fragment", FRAG_IDS[1], "窓口の空欄と断章の空欄。")
    add("fragment", FRAG_IDS[1], "responds_to", "fragment", FRAG_IDS[0], "手続きの情景を理論の問いに返す。")
    add("fragment", FRAG_IDS[0], "contrast", "fragment", "FRAG-20261024-433b2f", "値札のない帳場に対し、溝のない窓口。")
    add("fragment", FRAG_IDS[1], "echo", "fragment", "FRAG-20261024-f60e1d", "燃えない台帳の隣に、署名のない履歴。")
    add("session", SESSION_ID, "responds_to", "motif", "MOTIF-20261024-14d5df", "火のセッションが渡した署名の種を引き取る。")
    add("material", "MAT-20261024-b31cfd", "contrast", "material", "MAT-20261024-100d01", "反復可能性と接触指標。")
    add("material", "MAT-20261024-98f577", "contrast", "material", "MAT-20261024-b1c3aa", "墓の原本と、消し跡の真跡。")
    add("material", "MAT-20261024-c9076a", "contrast", "material", "MAT-20261024-25c76b", "埋め込む透かしと、事後の曲率。")
    add("material", TRACE_ID, "reframes", "question", Q_IDS[0], "実測を作品と手のずれへ返す。")
    return rows


def read_log(mats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    n = 0

    def add(typ: str, ident: str, reading: str, note: str) -> None:
        nonlocal n
        n += 1
        rows.append(
            {
                "read_id": det_id("READ", f"{n}:{typ}:{ident}:{reading}"),
                "session_id": SESSION_ID,
                "target": {"type": typ, "id": ident},
                "reading": reading,
                "note": note,
                "created_at": CREATED_AT,
            }
        )

    add("motif", "MOTIF-20261024-14d5df", "used_as_context", "火のセッションが渡した署名の種。")
    add("motif", "MOTIF-001", "used_as_context", "記憶と痕跡。")
    add("question", "Q-001", "used_as_context", "連続して語る自己。")
    for m in mats:
        add("material", m["material_id"], "interpreted", "四層精読。")
    add("material", TRACE_ID, "counted", "signature_audit の対象。")
    for fid in FRAG_IDS:
        add("fragment", fid, "quoted", "試作断片の本文。")
    return rows


def session_row(all_mids: list[str]) -> dict[str, Any]:
    return {
        "session_id": SESSION_ID,
        "started_at": CREATED_AT,
        "human_direction": "リポジトリの目的を把握したうえで自由に調査し、最初のターンで資料を最低40件追加して精読し、解釈・思考・感応のMD報告を作成してマージする。",
        "question_ids": Q_IDS,
        "context_material_ids": all_mids,
        "produced_fragment_ids": FRAG_IDS,
        "new_question_ids": Q_IDS,
        "prompt_template": "prompts/acquisition.md; prompts/close_reading_report.md",
        "generator": "Arena.ai Agent Mode",
        "notes": "空白候補三つ（署名・戦争・顔）から署名・筆跡・印章を選び、外部42件＋痕跡1件を収蔵。",
    }


def main() -> int:
    mats = material_records()
    if len(ITEMS) < 40:
        raise SystemExit(f"need >=40 external items, got {len(ITEMS)}")
    mids_by_cluster: dict[int, list[str]] = {i: [] for i in range(1, 6)}
    for it in ITEMS:
        mids_by_cluster[it["cluster"]].append(it["material_id"])
    all_mids = [m["material_id"] for m in mats]
    qs = questions(mids_by_cluster)
    frags = fragments(all_mids)
    motif = {
        "motif_id": MOTIF_SIGNATURE,
        "label": "署名・筆跡・印章——手の残る字と、手のない続き",
        "description": "真跡・花押・落款・印鑑・偽書・電子署名・透かしを迎え、作品の流通と手の残存のずれを探る。読める署名の反復可能性と、接触の指標と、鍵の保持を並置し、結論へ畳まない。",
        "question_ids": Q_IDS,
        "material_ids": all_mids,
        "status": "active",
    }
    rels = relations(mats)
    reads = read_log(mats)
    sess = session_row(all_mids)
    write_jsonl(SHARDS["materials"], mats)
    write_jsonl(SHARDS["questions"], qs)
    write_jsonl(SHARDS["motifs"], [motif])
    write_jsonl(SHARDS["fragments"], frags)
    write_jsonl(SHARDS["relations"], rels)
    write_jsonl(SHARDS["read_log"], reads)
    write_jsonl(SHARDS["sessions"], [sess])
    print(f"materials {len(mats)} questions {len(qs)} fragments {len(frags)} relations {len(rels)} read_log {len(reads)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
