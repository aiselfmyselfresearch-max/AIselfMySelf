#!/usr/bin/env python3
"""Measure where promising, swearing, keeping and handing over appear in the archive.

This is the second mirror for the promise theme.  ``tools/promise_audit.py``
(SESSION-040) counts fragments and schema keys; this tool adds the editors'
close-reading reports and the session/question ledgers, and counts the recurring
"裏切り" heading separately.

The heading itself carries two meanings and they are counted apart.  The older
form "**この資料が裏切るもの**" (SESSION-20261024-836a43) means "the point where
this material refuses my reading" — a refutation.  Since 2026-10-25 the shorter
"**裏切り**" is also used for "the range this material does not vouch for" — a
scope note.  A scope note counted as a refutation inflates the archive's record
of its own corrections (state/errata.jsonl ERR-023), so the two forms are
reported on separate lines and the total is labelled as mixed.


This is a mirror, not a score and not a test of sincerity.  It counts selected
word forms in fragment ``text`` fields.  A zero means that the specified form is
absent; it does not prove that promise, trust, obligation, or an experience of
them is absent.  Ambiguous single characters (契 in 契機, 判 in 判断, 信 in
信號) are reported separately and are never silently folded into the groups.

Usage:
  python3 tools/pledge_audit.py
  python3 tools/pledge_audit.py --json
  python3 tools/pledge_audit.py --show FRAG-017
  python3 tools/pledge_audit.py --base-only
  python3 tools/pledge_audit.py --no-reports
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
READINGS = ROOT / "readings"
SESSIONS = ROOT / "state" / "sessions.jsonl"
QUESTIONS = ROOT / "state" / "questions.jsonl"

# Keep the groups deliberately literal.  約 and 契 are not group tokens: 契機 and
# 契約 share 契, and 約 alone would catch 約する only by accident of orthography.
GROUPS: dict[str, tuple[str, ...]] = {
    "約束・誓約": (
        "約束", "約を", "誓い", "誓う", "誓った", "誓って", "契り", "契約", "盟約",
        "起請", "公約", "言質", "請け合", "請合",
    ),
    "履行・破約": (
        "守る", "守った", "守って", "破る", "破った", "破って", "違える", "違えた",
        "果たす", "果たした", "裏切", "背いて", "背いた", "反故", "不履行",
    ),
    "信頼・疑い": (
        "信じる", "信じた", "信じて", "信頼", "疑い", "疑う", "疑った", "頼り", "期待した",
    ),
    "証文・署名": (
        "証文", "証書", "署名", "捺印", "契約書", "借用書", "起請文", "判を", "印を",
    ),
    "貸借・債務": (
        "借り", "貸し", "返す", "返済", "負債", "債務", "借金", "恩義", "義理",
    ),
    "待機・引継": (
        "待つ", "待った", "待って", "待ち", "引き継", "次回", "次に", "次の",
    ),
}

RAW_TOKENS: dict[str, str] = {
    "約": "契約・約する・節約等を含む。約束の回数ではない",
    "誓": "誓約・誓言等の複合を含む",
    "契": "契機・契り等を含む。契約の回数ではない",
    "信": "信号・迷信等を含みうる。信頼の回数ではない",
    "判": "判断・判決等を大部分に含む",
    "待": "待機・期待等の複合を含む",
}

PROMISE_SHAPED = ("次回", "次のセッション", "引き継", "渡す", "残す", "手渡")


def strip_quotes(text: str) -> str:
    """Remove non-nested Japanese quotation spans, as in the other audit mirrors."""
    out = re.sub(r"「[^「」]*」", "", text)
    return re.sub(r"『[^『』]*』", "", out)


def load_base() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in FRAGMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_fragments(base_only: bool = False) -> tuple[list[dict[str, Any]], str]:
    if base_only:
        return load_base(), "base only（state/fragments.jsonl）"
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(FRAGMENTS, "fragment_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values()), "union（base + shards）"


def contexts(text: str, token: str, radius: int = 24) -> list[str]:
    return [
        text[max(0, match.start() - radius):match.end() + radius].replace("\n", " ")
        for match in re.finditer(re.escape(token), text)
    ]


def measure(fragments: list[dict[str, Any]], source_label: str = "test") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    totals = {name: Counter() for name in GROUPS}
    docs = {name: set() for name in GROUPS}
    raw_totals: Counter = Counter()
    inside: Counter = Counter()

    for fragment in fragments:
        text = fragment.get("text", "")
        outside = strip_quotes(text)
        row: dict[str, Any] = {
            "fragment_id": fragment.get("fragment_id", ""),
            "groups": {},
            "raw": {},
            "contexts": {},
        }
        for name, tokens in GROUPS.items():
            counts: dict[str, int] = {}
            for token in tokens:
                n_out = outside.count(token)
                n_in = text.count(token) - n_out
                if n_out:
                    counts[token] = n_out
                    totals[name][token] += n_out
                    docs[name].add(row["fragment_id"])
                    row["contexts"][token] = contexts(outside, token)
                if n_in:
                    inside[token] += n_in
            if counts:
                row["groups"][name] = counts
        for token in RAW_TOKENS:
            n = text.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        rows.append(row)

    return {
        "source": source_label,
        "fragments": len(fragments),
        "prose_chars": sum(len(f.get("text", "")) for f in fragments),
        "rows": rows,
        "group_totals": {name: dict(counter) for name, counter in totals.items()},
        "group_docs": {name: sorted(ids) for name, ids in docs.items()},
        "inside_quotes": dict(inside),
        "raw_totals": dict(raw_totals),
    }


# The report of this session quotes the archive's promise vocabulary while
# discussing it.  Counting it alongside its predecessors would double the mirror,
# so the file that this audit produces for is excluded by name.
CURRENT_REPORT = "2026-10-24-session-041-promise-and-oath.md"

# Heading forms.  The order matters: the legacy string does not contain the new
# one, so the two counts never overlap.
HEADING_LEGACY = "**この資料が裏切るもの"
HEADING_NEW = "**裏切り"
HEADING_LINE_RE = re.compile(r"^\s*[-*]\s*\*\*(裏切り|この資料が裏切るもの)\*\*\s*[:：]")
HEADING_NOTE = (
    "旧型は『その資料が自分の読みを拒む点』（反証）、新型は 2026-10-25 以降"
    "『その資料が保証しない範囲』（但し書き）の意味でも使われている。"
    "二つは同じ欄に入っているので、合計を反証の件数と読まない（ERR-023）。"
)


def measure_reports(limit: int | None = None, exclude_current: bool = True) -> dict[str, Any]:
    """Count the same forms in the editors' close-reading reports."""
    files = sorted(READINGS.glob("*.md"))
    if exclude_current:
        files = [path for path in files if path.name != CURRENT_REPORT]
    if limit is not None:
        files = files[-limit:]
    totals = {name: Counter() for name in GROUPS}
    docs = {name: set() for name in GROUPS}
    chars = 0
    promise_files = 0
    promise_count = 0
    uragiri_headings = 0
    uragiri_legacy = 0
    uragiri_new = 0
    uragiri_lines_legacy = 0
    uragiri_lines_new = 0
    for path in files:
        text = stamp = path.read_text(encoding="utf-8")
        chars += len(stamp)
        for name, tokens in GROUPS.items():
            for token in tokens:
                n = text.count(token)
                if n:
                    totals[name][token] += n
                    docs[name].add(path.name)
        uragiri_legacy += text.count(HEADING_LEGACY)
        uragiri_new += text.count(HEADING_NEW)
        uragiri_headings = uragiri_legacy + uragiri_new
        for line in text.splitlines():
            match = HEADING_LINE_RE.match(line)
            if match:
                if match.group(1) == "裏切り":
                    uragiri_lines_new += 1
                else:
                    uragiri_lines_legacy += 1
        hits = sum(text.count(word) for word in PROMISE_SHAPED)
        if hits:
            promise_files += 1
            promise_count += hits
    return {
        "files": len(files),
        "chars": chars,
        "group_totals": {name: dict(counter) for name, counter in totals.items()},
        "group_docs": {name: sorted(ids) for name, ids in docs.items()},
        "promise_shaped": promise_count,
        "uragiri_headings": uragiri_headings,
        "uragiri_headings_legacy": uragiri_legacy,
        "uragiri_headings_new": uragiri_new,
        "uragiri_lines_legacy": uragiri_lines_legacy,
        "uragiri_lines_new": uragiri_lines_new,
        "uragiri_lines_total": uragiri_lines_legacy + uragiri_lines_new,
        "promise_files": sorted({name for name in docs["待機・引継"]}),
    }


def measure_ledgers() -> dict[str, Any]:
    errors: list[str] = []
    sessions = ledger_io.load_jsonl_union(SESSIONS, "session_id", errors, root=ROOT)
    questions = ledger_io.load_jsonl_union(QUESTIONS, "question_id", errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    handoff = 0
    for record in sessions.values():
        notes = str(record.get("notes", ""))
        if any(word in notes for word in ("次回", "次に", "次のセッション", "引き継", "残した")):
            handoff += 1
    statuses = Counter(record.get("status", "") for record in questions.values())
    return {
        "sessions": len(sessions),
        "sessions_with_handoff": handoff,
        "questions": len(questions),
        "question_status": dict(statuses),
    }


def report(data: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add("=== 約束の鏡 — 誓う語・守る語・次へ渡す語はどこにあるか（採点ではありません） ===")
    add(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字（メタデータを除く）")
    add(f"計数の範囲: {data['source']}")
    add("")
    add("--- 1. 語群ごとの出現（鉤括弧の外、地の文） ---")
    for name in GROUPS:
        counts = data["group_totals"].get(name, {})
        identifiers = data["group_docs"].get(name, [])
        total = sum(counts.values())
        detail = "、".join(
            f"{token}×{number}"
            for token, number in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ) or "なし"
        add(f"  {name:<12}: {total:>3} 回 / {len(identifiers):>2} 編  （{detail}）")
    add("")
    add("--- 2. 多義の生字（約束・信頼へ合算しない参考値） ---")
    for token in RAW_TOKENS:
        add(f"  {token}: {data['raw_totals'].get(token, 0)} 回  注意: {RAW_TOKENS[token]}")
    add("")
    add("--- 3. 鉤括弧の内側だけにある語 ---")
    add("  " + ("、".join(f"{k}×{v}" for k, v in sorted(data["inside_quotes"].items())) or "なし"))
    add("")
    add("--- 4. 読むための注意 ---")
    add("  ・0は指定語形の不在であって、約束・誠実さ・信頼の経験や主題の不在を証明しない。")
    add("  ・『契機』の『契』、『判断』の『判』、『信号』の『信』は約束として数えない。")
    add("  ・『待つ』『次の』は待機と継起を含み、約束の履行とは限らない。文脈は --show で確かめる。")
    add("  ・鉤括弧の除去は非入れ子の正規表現による近似で、地の文／引用の厳密な構文解析ではない。")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--show", metavar="FRAG_ID", help="show one fragment's matches and contexts")
    parser.add_argument("--base-only", action="store_true", help="exclude session shards")
    parser.add_argument("--no-reports", action="store_true", help="skip readings/*.md and ledgers")
    args = parser.parse_args()

    fragments, label = load_fragments(args.base_only)
    data = measure(fragments, label)
    if args.show:
        for row in data["rows"]:
            if row["fragment_id"] == args.show:
                print(json.dumps(row, ensure_ascii=False, indent=2))
                return 0
        print(f"{args.show}: not found", flush=True)
        return 1
    if not args.no_reports:
        data["reports"] = measure_reports()
        data["ledgers"] = measure_ledgers()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(report(data))
    if "reports" in data:
        reports = data["reports"]
        ledgers = data["ledgers"]
        print("")
        print("--- 5. 編集者の声（readings/*.md）での同じ語形 ---")
        for name in GROUPS:
            counts = reports["group_totals"].get(name, {})
            total = sum(counts.values())
            files = len(reports["group_docs"].get(name, []))
            detail = "、".join(
                f"{token}×{number}"
                for token, number in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:6]
            ) or "なし"
            print(f"  {name:<12}: {total:>4} 回 / {files:>2} 本  （{detail}）")
        print("")
        print(f"  『次回 / 次のセッション / 引継 / 渡す / 残す』を含む報告: {reports['promise_shaped']} 回 / {len(reports['promise_files'])} 本")
        print(
            f"  太字『裏切』を含む箇所（緩い計数。見出し以外の強調も入る）: "
            f"{reports['uragiri_headings']}"
            f"（旧型『この資料が裏切るもの』{reports['uragiri_headings_legacy']} / "
            f"新型『裏切り』{reports['uragiri_headings_new']}）"
        )
        print(
            f"  うち行頭の見出し（`- **裏切り**：` の形）: {reports['uragiri_lines_total']} 箇所"
            f"（旧型 {reports['uragiri_lines_legacy']} / 新型 {reports['uragiri_lines_new']}）"
        )
        print(f"    注意: {HEADING_NOTE}")
        print("")
        print("--- 6. 台帳の側 ---")
        print(f"  セッション: {ledgers['sessions']} 件 / 引継ぎの語を含む notes: {ledgers['sessions_with_handoff']} 件")
        print(f"  問い: {ledgers['questions']} 件 / 状態: {ledgers['question_status']}")
        print("")
        print("--- 7. 読むための注意（編集者の声） ---")
        print("  ・報告は『約束』を主題語として使うが、その大半は引用・要約・分析の対象である。")
        print("  ・『次回』『次のセッション』は呼びかけであって、履行の記録ではない。")
        print("  ・台帳の全問いが open であることは、未履行の証明でも、誠実さの証明でもない。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
