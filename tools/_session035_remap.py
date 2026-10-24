# -*- coding: utf-8 -*-
"""Second-round renumbering for the SESSION-033/034 parallel merges.

After the first collision resolution (SESSION-031 draft -> SESSION-033, see
_session033_remap.py), two more parallel sessions merged into main as
SESSION-033 (数えること、測ること、余り = MOTIF-015, Q-077..081, FRAG-038,
MAT-TRC-011) and SESSION-034 (訂正と抹消 = MOTIF-016, Q-082..086). The time
and waiting session is therefore renumbered again:

  MAT-LIT-286..319   -> MAT-LIT-354..387   (+68)
  MAT-EVD-...-59..66 -> MAT-EVD-...-82..89 (+23, incl. EVD_BASE suffixes)
  MAT-TRC-011        -> MAT-TRC-013
  MOTIF-015          -> MOTIF-017
  Q-077..081         -> Q-087..091         (+10)
  FRAG-038/039       -> FRAG-039/040       (reverse order; sources overlap targets)
  REL-554..608       -> REL-668..722       (+114, prose only)
  SESSION-033        -> SESSION-035

Two same-work overlaps introduced by the new merges (Orwell 1984, Joyce
Ulysses) are replaced by hand afterwards (_session035_replacements.py).
Run once, from repo root:  python3 tools/_session035_remap.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "tools/_session035_common.py",
    "tools/_session035_apply.py",
    "tools/_session035_data1.py",
    "tools/_session035_data2.py",
    "tools/_session035_data3.py",
    "tools/_session035_data4.py",
    "tools/time_audit.py",
    "readings/2026-10-24-session-033-time-and-waiting.md",
]


def remap(text: str) -> str:
    def lit_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"MAT-LIT-{n + 68}" if 286 <= n <= 319 else m.group(0)

    text = re.sub(r"MAT-LIT-(\d{3})", lit_sub, text)

    def evd_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"MAT-EVD-20261024-{n + 23}" if 59 <= n <= 66 else m.group(0)

    text = re.sub(r"MAT-EVD-20261024-(\d{2})", evd_sub, text)

    def suffix_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f'EVD_BASE + "{n + 23}"' if 59 <= n <= 66 else m.group(0)

    text = re.sub(r'EVD_BASE \+ "(\d{2})"', suffix_sub, text)

    text = text.replace("MAT-TRC-011", "MAT-TRC-013")
    text = text.replace('"source_id": "SRC-TRC-011"', '"source_id": "SRC-TRC-013"')
    text = text.replace("MOTIF-015", "MOTIF-017")

    def q_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"Q-{n + 10:03d}" if 77 <= n <= 81 else m.group(0)

    text = re.sub(r"Q-(\d{3})", q_sub, text)

    def rel_sub(m: re.Match) -> str:
        n = int(m.group(1))
        return f"REL-{n + 114:03d}" if 554 <= n <= 608 else m.group(0)

    text = re.sub(r"REL-(\d{3})", rel_sub, text)

    # FRAG sources overlap targets (38->39, 39->40): map the higher one first.
    text = text.replace("FRAG-039", "FRAG-040")
    text = text.replace("FRAG-038", "FRAG-039")

    text = text.replace("SESSION-033", "SESSION-035")
    text = text.replace("M15", "M17")
    text = text.replace("range(286, 320)", "range(354, 388)")
    text = text.replace("range(59, 67)", "range(82, 90)")
    text = text.replace(
        "readings/2026-10-24-session-033-time-and-waiting.md",
        "readings/2026-10-24-session-035-time-and-waiting.md",
    )
    text = text.replace("2026-10-24-session-033-time-and-waiting", "2026-10-24-session-035-time-and-waiting")
    return text


def main() -> int:
    for rel in TARGETS:
        path = ROOT / rel
        original = path.read_text(encoding="utf-8")
        rewritten = remap(original)
        if rel.endswith("session-033-time-and-waiting.md"):
            new_path = ROOT / "readings/2026-10-24-session-035-time-and-waiting.md"
            new_path.write_text(rewritten, encoding="utf-8")
            path.unlink()
            print(f"moved+remapped {rel} -> {new_path.relative_to(ROOT)}")
        else:
            path.write_text(rewritten, encoding="utf-8")
            print(f"remapped {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
