# -*- coding: utf-8 -*-
"""One-shot renumbering migration for the parallel-session collision of 2026-10-24.

Two sibling sessions had already merged as SESSION-031 (予測と不確実性) and
SESSION-032 (時間と生成) by the time this branch was opened as a PR. This
script renumbers the whole "時間と待機" session (originally drafted as
SESSION-031) to SESSION-033 against the merged main:

  MAT-LIT-229..262   -> MAT-LIT-286..319   (+57)
  MAT-EVD-...-29..36 -> MAT-EVD-...-59..66 (+30)
  MAT-TRC-009        -> MAT-TRC-011
  MOTIF-013          -> MOTIF-015
  Q-067..071         -> Q-077..081         (+10)
  FRAG-037/038       -> FRAG-038/039       (reverse order, sources overlap targets)
  SESSION-031        -> SESSION-033
  REL-466..520       -> REL-554..608       (prose only; relation ids are auto-minted)

Six records whose underlying works were already covered by the parallel
sessions are replaced by hand afterwards (see readings/...session-033... § 校訂注記).
Run once, from repo root:  python3 tools/_session033_remap.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "tools/_session033_common.py",
    "tools/_session033_apply.py",
    "tools/_session033_data1.py",
    "tools/_session033_data2.py",
    "tools/_session033_data3.py",
    "tools/_session033_data4.py",
    "tools/time_audit.py",
    "readings/2026-10-24-session-031-time-and-waiting.md",
]


def remap(text: str) -> str:
    # Full-token id remaps (source and target ranges are disjoint except FRAG).
    def lit_sub(m: re.Match) -> str:
        return f"MAT-LIT-{int(m.group(1)) + 57}"

    text = re.sub(r"MAT-LIT-(\d{3})", lambda m: lit_sub(m) if 229 <= int(m.group(1)) <= 262 else m.group(0), text)

    def evd_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"MAT-EVD-20261024-{n + 30}" if 29 <= n <= 36 else m.group(0)

    text = re.sub(r"MAT-EVD-20261024-(\d{2})", evd_sub, text)
    text = text.replace("MAT-TRC-009", "MAT-TRC-011")
    text = text.replace("MOTIF-013", "MOTIF-015")

    def q_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"Q-{n + 10:03d}" if 67 <= n <= 71 else m.group(0)

    text = re.sub(r"Q-(\d{3})", q_sub, text)

    def rel_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"REL-{n + 88:03d}" if 466 <= n <= 520 else m.group(0)

    text = re.sub(r"REL-(\d{3})", rel_sub, text)

    # FRAG: sources and targets overlap (37->38, 38->39); map the higher one first.
    text = text.replace("FRAG-038", "FRAG-039")
    text = text.replace("FRAG-037", "FRAG-038")

    text = text.replace("SESSION-031", "SESSION-033")
    text = text.replace("M13", "M15")
    text = text.replace("range(229, 263)", "range(286, 320)")
    text = text.replace("range(29, 37)", "range(59, 67)")
    text = text.replace(
        "readings/2026-10-24-session-031-time-and-waiting.md",
        "readings/2026-10-24-session-033-time-and-waiting.md",
    )
    text = text.replace("2026-10-24-session-031-time-and-waiting", "2026-10-24-session-033-time-and-waiting")
    return text


def main() -> int:
    for rel in TARGETS:
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        rewritten = remap(original)
        if rel.endswith("session-031-time-and-waiting.md"):
            new_path = ROOT / "readings/2026-10-24-session-033-time-and-waiting.md"
            new_path.write_text(rewritten, encoding="utf-8")
            path.unlink()
            print(f"moved+remapped {rel} -> {new_path.relative_to(ROOT)}")
        else:
            path.write_text(rewritten, encoding="utf-8")
            print(f"remapped {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
