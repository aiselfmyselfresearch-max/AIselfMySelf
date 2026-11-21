#!/usr/bin/env python3
"""List the materials whose check was recorded as deeper than it was, in reading order.

The queue this prints
---------------------
``tools/depth_backfill.py`` classifies every ``verified`` row by the prose in its
own ``verification.method``/``note``.  Two classes come out of it:

* ``shallow_claim`` -- the row says ``verified`` while the prose says a
  bibliography, an abstract, or a table row was checked.  112 rows as of
  2026-11-21.
* ``unknown`` -- the prose does not say how far the check went.  769 rows.

Neither can be repaired by a script: the only honest repair is to read the
source, and the only honest *label* after reading is whatever the reading
actually reached.  So this tool does not repair anything.  It orders the work.

Ordering
--------
By **how many evaluations cite the material** (descending), then by how old the
check is.  A row that backs six ``supports`` rows costs more to leave unread
than a row nothing cites; the sample of 8 shallow rows taken on 2026-11-21
found half of them were *accurately* recorded as abstract-level, so the queue is
a list of rows to read, not a list of rows known to be wrong.

Each line carries the URL to fetch and a ``fetch`` hint: ``arxiv``/``pmc``/
``journal`` pages came back through the page-fetch tool on 2026-11-21, while a
bare ``doi.org`` link usually redirects to a paywall and needs an OA copy first.

Usage
-----
    python3 tools/reading_queue.py                  # both classes, top 40
    python3 tools/reading_queue.py --class shallow  # only the self-contradicting rows
    python3 tools/reading_queue.py --host arxiv --limit 20
    python3 tools/reading_queue.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import depth_backfill  # noqa: E402
import inspect_inquiry  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def fetch_hint(url: str) -> str:
    lowered = (url or "").lower()
    if "arxiv.org" in lowered:
        return "arxiv"
    if "pmc.ncbi" in lowered or "ncbi.nlm.nih.gov/pmc" in lowered:
        return "pmc"
    if any(host in lowered for host in ("jneurosci.org", "nature.com", "science.org", "cell.com", "pnas.org")):
        return "journal"
    if "doi.org" in lowered:
        return "doi"
    if not lowered:
        return "no-url"
    return "other"


def build(data: dict) -> list[dict]:
    citations: dict[str, int] = {}
    for evaluation in data.get("evaluations", {}).values():
        for mid in evaluation.get("material_ids") or []:
            if isinstance(mid, str):
                citations[mid] = citations.get(mid, 0) + 1

    queue: list[dict] = []
    for mid, material in data.get("materials", {}).items():
        verification = material.get("verification") or {}
        if verification.get("status") != "verified" or verification.get("depth"):
            continue
        cls, clause = depth_backfill.classify(material)
        if cls not in ("shallow_claim", "unknown"):
            continue
        source = material.get("source") or {}
        origin = material.get("origin") or {}
        url = source.get("url") or ""
        queue.append(
            {
                "material_id": mid,
                "kind": "shallow" if cls == "shallow_claim" else "unknown",
                "title": str(material.get("title") or "")[:70],
                "url": url,
                "fetch": fetch_hint(url),
                "citations": citations.get(mid, 0),
                "checked_at": str(verification.get("checked_at") or ""),
                "clause": clause[:110],
                "evidence_record_path": str(origin.get("evidence_record_path") or ""),
            }
        )
    queue.sort(key=lambda row: (-row["citations"], row["checked_at"], row["material_id"]))
    return queue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--class", dest="klass", choices=("shallow", "unknown", "both"), default="both")
    parser.add_argument("--host", default=None, help="arxiv / pmc / journal / doi")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    data = inspect_inquiry.load_all()
    queue = build(data)
    if args.klass != "both":
        queue = [row for row in queue if row["kind"] == args.klass]
    if args.host:
        queue = [row for row in queue if row["fetch"] == args.host]

    if args.json:
        print(json.dumps(queue[: args.limit], ensure_ascii=False, indent=2))
        return 0

    shallow = sum(1 for row in queue if row["kind"] == "shallow")
    print("# reading queue (read-only)")
    print()
    print(f"- 行数: **{len(queue):,}**（自己矛盾 {shallow:,} / 記述なし {len(queue) - shallow:,}）")
    print("- 並び: 引用されている evaluation の数 → 照合日の古い順")
    print("- この道具は何も直さない。読む順番を決めるだけである。")
    print()
    print("| # | 素材 | 種別 | 引用 | fetch | 照合日 | URL |")
    print("| ---: | :--- | :--- | ---: | :--- | :--- | :--- |")
    for index, row in enumerate(queue[: args.limit], 1):
        url = row["url"] or "（URL なし）"
        print(
            f"| {index} | `{row['material_id']}` | {row['kind']} | {row['citations']} | "
            f"{row['fetch']} | {row['checked_at']} | {url} |"
        )
    print()
    print("> 読んだ後は `editorial_decisions` の overlay で depth を記録する。")
    print("> depth=abstract / metadata は status=partially_verified と組でしか通らない（2026-11-20 §3）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
