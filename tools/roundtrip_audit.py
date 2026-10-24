#!/usr/bin/env python3
"""Round-trip drift audit for the archive's own fragments (stdlib only).

Reads readings/2026-10-24-roundtrip-sample.json, compares each fragment with the
Japanese text that came back from an English round trip, and reports surface
drift. It does not score quality: a low similarity is not a bad translation, and
a high similarity is not a faithful one. Both numbers are counts of change.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "readings" / "2026-10-24-roundtrip-sample.json"

FIRST_PERSON = ("私", "僕", "自分", "われ", "わたし", "俺")


def normalize(text: str) -> str:
    """Drop whitespace and the punctuation marks that the round trip can freely add."""
    return re.sub(r"[\s、。，．・「」『』（）\(\)\-—…？！?!]", "", text)


def counts(text: str) -> dict[str, int]:
    return {
        "chars": len(text),
        "first_person": sum(text.count(w) for w in FIRST_PERSON),
        "question_marks": text.count("？") + text.count("?"),
        "quoted": text.count("「"),
        "commas": text.count("、"),
        "sentence_ends": text.count("。"),
    }


def main() -> int:
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    fragments = {
        f["fragment_id"]: f
        for f in (json.loads(l) for l in (ROOT / "state" / "fragments.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())
    }
    print("往復翻訳の漂流——同一モデル・同一セッション内の最小値\n")
    header = f"{'fragment':10} {'chars':>12} {'ratio(正規化)':>12} {'一人称':>10} {'「':>6} {'？':>4}"
    print(header)
    print("-" * len(header))
    for sample in data["samples"]:
        fid = sample["fragment_id"]
        original = fragments[fid]["text"]
        back = sample["back_ja"]
        ratio = difflib.SequenceMatcher(None, normalize(original), normalize(back)).ratio()
        a, b = counts(original), counts(back)
        print(
            f"{fid:10} {a['chars']:5d}->{b['chars']:<6d} {ratio:12.3f} "
            f"{a['first_person']:4d}->{b['first_person']:<5d} "
            f"{a['quoted']:2d}->{b['quoted']:<3d} {a['question_marks']:1d}->{b['question_marks']:<2d}"
        )
    print("\n註：類似度は文字の並びの一致であり、意味の一致ではない。")
    print("同一モデルが原文を見ながら往復したため、この値は系をまたぐ漂流の下限にあたる。")
    print("値が高いことは翻訳が正しいことを、低いことは誤りであることを意味しない。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
