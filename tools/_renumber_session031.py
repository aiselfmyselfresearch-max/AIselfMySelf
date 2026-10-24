# -*- coding: utf-8 -*-
"""SESSION-031 の追加IDを main 側の使用後へ振り直す（並行マージ衝突の解消）。

マッピング:
- MAT-LIT-229〜263 -> MAT-LIT-251〜285
- MAT-EVD-20261024-29〜38 -> MAT-EVD-20261024-49〜58
- MAT-TRC-009 -> MAT-TRC-010
- SRC-MAT-LIT-229〜263 / SRC-EVD-... / SRC-MAT-TRC-009 も同様
- Q-067〜071 -> Q-072〜076
- MOTIF-013 -> MOTIF-014
- SESSION-031 -> SESSION-032
- REL-466〜500 -> REL-519〜588
- FRAG-037 は不変（main 側は FRAG-036 まで）
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

mapping = {}
for i in range(229, 264):
    mapping[f"MAT-LIT-{i}"] = f"MAT-LIT-{i + 22}"
for i in range(29, 39):
    mapping[f"MAT-EVD-20261024-{i}"] = f"MAT-EVD-20261024-{i + 20}"
mapping["MAT-TRC-009"] = "MAT-TRC-010"
for pref in ["SRC-MAT-LIT-", "SRC-EVD-20261024-", "SRC-MAT-TRC-"]:
    pass  # SRC- variants handled by same token replacement below (they contain MAT-EVD.../MAT-LIT-.../MAT-TRC- as suffix)
for i in range(229, 264):
    mapping[f"SRC-MAT-LIT-{i}"] = f"SRC-MAT-LIT-{i + 22}"
for i in range(29, 39):
    mapping[f"SRC-EVD-20261024-{i}"] = f"SRC-EVD-20261024-{i + 20}"
mapping["SRC-MAT-TRC-009"] = "SRC-MAT-TRC-010"
for i in range(67, 72):
    mapping[f"Q-{i:03d}"] = f"Q-{i + 5:03d}"
mapping["MOTIF-013"] = "MOTIF-014"
mapping["SESSION-031"] = "SESSION-032"
for i in range(466, 501):
    mapping[f"REL-{i}"] = f"REL-{i + 53}"

# 長いトークンを優先して置換（部分一致を避ける）
tokens = sorted(mapping.keys(), key=len, reverse=True)
pattern = re.compile("|".join(re.escape(t) for t in tokens))


def replace_ids(text):
    return pattern.sub(lambda m: mapping[m.group(0)], text)


files = [
    ROOT / "state" / "materials.jsonl",
    ROOT / "state" / "questions.jsonl",
    ROOT / "state" / "motifs.jsonl",
    ROOT / "state" / "relations.jsonl",
    ROOT / "state" / "sessions.jsonl",
    ROOT / "state" / "fragments.jsonl",
    ROOT / "readings" / "2026-10-24-session-031-time-and-generation.md",
    ROOT / "tools" / "_session031_build_materials.py",
    ROOT / "tools" / "_session031_build_state.py",
]

for path in files:
    text = path.read_text(encoding="utf-8")
    new = replace_ids(text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        print(f"updated: {path.relative_to(ROOT)}")
    else:
        print(f"unchanged: {path.relative_to(ROOT)}")

# 旧IDが残っていないか確認
old_tokens = [t for t in tokens if int("".join(ch for ch in t if ch.isdigit())) in
              list(range(229, 264)) + list(range(29, 39)) + [9] +
              list(range(67, 72)) + [13] + list(range(466, 501))]
remaining = []
for path in files:
    text = path.read_text(encoding="utf-8")
    for t in old_tokens:
        if t in text:
            remaining.append((str(path.relative_to(ROOT)), t))
if remaining:
    print("!! REMAINING OLD IDs !!")
    for r in remaining:
        print(r)
else:
    print("旧IDの残骸なし")
