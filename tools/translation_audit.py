#!/usr/bin/env python3
"""Translation census of the archive (stdlib only).

Counts, from state/*.jsonl: which languages the materials quote, how often a
translator is named, how many materials are quoted in Japanese although the
original is not Japanese, and how many languages the archive itself writes in.

This is a count of recorded fields. A missing translator name is a missing
record, not proof that no translator existed. Nothing here scores translation
quality.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSLATOR = re.compile(r"trans\.|translated|訳者|拙訳|\(trans\.\)")
WOMEN = {
    "Virginia Woolf", "Simone Weil", "Edith Stein", "George Eliot",
    "Mary Wollstonecraft Shelley", "Susan Sontag", "Hannah Arendt",
    "Emily Dickinson", "清少納言", "紫式部", "金子みすゞ", "多和田葉子",
    "温又柔", "李良枝", "水村美苗", "石牟礼道子", "知里幸恵",
    "Gayatri Chakravorty Spivak",
}


def load(name: str) -> list[dict]:
    path = ROOT / "state" / name
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


THIS_REPORT = "readings/2026-10-24-translation-and-the-untranslated.md"


def baseline(mats: list[dict]) -> list[dict]:
    """Materials that existed before the two sessions dated 2026-10-24 added theirs.

    MAT-TRC-007 records a census taken when the ledger held 159 materials, before
    the parallel SESSION-028 merged. Excluding every 2026-10-24 addition is what
    reproduces that measurement.
    """
    return [m for m in mats if "2026-10-24" not in m["origin"].get("evidence_record_path", "")]


def main() -> int:
    all_mats = load("materials.jsonl")
    mats = baseline(all_mats)
    frags = [f for f in load("fragments.jsonl") if f.get("session_id") not in ("SESSION-028", "SESSION-029")]
    reports = [p for p in sorted((ROOT / "readings").glob("*.md")) if "2026-10-24" not in p.name]

    print(f"基準状態：2026-10-24 の各セッションの追加分（{len(all_mats) - len(mats)}件）を除いた集計")
    print("（MAT-TRC-007 の集計はこの状態で測った。現在の台帳の値ではない）\n")
    print("== 素材 ==")
    print(f"総数 {len(mats)}  種別 {dict(Counter(m['kind'] for m in mats))}")
    lit = [m for m in mats if m["kind"] == "literary_text"]
    langs = Counter(m["passage_language"] for m in lit)
    non_ja = [m for m in lit if m["passage_language"] != "ja"]
    print(f"文学資料 {len(lit)}  引文言語 {dict(langs.most_common())}")
    print(f"非日本語の引文 {len(non_ja)} ({len(non_ja) / len(lit):.1%})")

    named = [m for m in non_ja if TRANSLATOR.search(json.dumps(m["source"], ensure_ascii=False))]
    print(f"うち source に訳者名が残るもの {len(named)} ({len(named) / len(non_ja):.1%})")
    print(f"訳者名が残らないもの {len(non_ja) - len(named)}")

    def latin_only(authors: list[str]) -> bool:
        return any(not re.search(r"[ぁ-んァ-ヶ一-龥]", a) and "Archive" not in a for a in authors)

    ja_from_foreign = [
        m for m in lit if m["passage_language"] == "ja" and latin_only(m["source"]["authors"])
    ]
    print(f"\n原語が非日本語なのに引文が日本語の文学資料 {len(ja_from_foreign)}")
    for m in ja_from_foreign:
        flag = "訳者名あり" if TRANSLATOR.search(json.dumps(m["source"], ensure_ascii=False)) else "訳者名なし"
        print(f"  {m['material_id']} {m['source']['authors']} [{flag}]")

    print("\n== 書く側 ==")
    print(f"断片 {len(frags)}  言語 {dict(Counter(f.get('language') for f in frags))}  "
          f"総字数 {sum(len(f['text']) for f in frags)}")
    print(f"精読・検証レポート {len(reports)} 本  総字数 {sum(len(p.read_text(encoding='utf-8')) for p in reports)}")
    written = Counter(f.get("language") for f in frags)
    print(f"書庫が書く言語の種類 {len(written)}")

    print("\n== 翻訳を主題とする既存資料 ==")
    hits = [m for m in mats if re.search(r"翻訳|訳語|訳者|translat|Übersetz|Dolmetsch|back-translation|Round-Trip",
                                         m["title"] + m["source"]["title"])]
    print(f"{len(hits)} 件")
    for m in hits:
        print(f"  {m['material_id']} {m['title'][:70]}")

    print("\n== 著者構成（文学資料） ==")
    jp = [m for m in lit if any(re.search(r"[ぁ-んァ-ヶ一-龥]", a) for a in m["source"]["authors"])]
    women = [m for m in lit if any(a in WOMEN for a in m["source"]["authors"])]
    print(f"日本語著者 {len(jp)} / 非日本語著者 {len(lit) - len(jp)}")
    print(f"女性著者 {len(women)} ({len(women) / len(lit):.1%})")
    print(f"\n== 現在（追加後） ==")
    lit_all = [m for m in all_mats if m["kind"] == "literary_text"]
    print(f"素材 {len(all_mats)}  文学 {len(lit_all)}  "
          f"非日本語引文 {sum(1 for m in lit_all if m['passage_language'] != 'ja')}")
    print("\n註：欄に記録された値の集計であり、翻訳の質・読解の正しさ・訳者の存在を判定しない。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
