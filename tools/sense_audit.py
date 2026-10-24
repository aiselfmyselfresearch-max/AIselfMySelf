#!/usr/bin/env python3
"""Measure how perception and sensory language appears in the fragments. A mirror, not a score.

SESSION-036: 知覚と媒体（見る・聴く・触れる）を問う前に、台帳の本文が
どのような感覚語を、どの頻度・分布で持っているかを再現可能な実測として記録する。
前回までの audit と同様、語形の存在を数えるだけで、能力・経験の有無は判定しない。

Groups:
  見る — 目、見える、見る、見、観、視、眺、映、光、色、明、暗、影、白黒 等
  聴く — 耳、聴く、聞く、聞こえる、音、声、響、歌、沈黙、静か
  触れる — 手（身体候補）、触れる、触感、手触り、指、肌、温かい、冷たい

Usage:
  python3 tools/sense_audit.py
  python3 tools/sense_audit.py --json
  python3 tools/sense_audit.py --show FRAG-001
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

FRAGMENTS = ROOT / "state" / "fragments.jsonl"
SESSIONS = ROOT / "state" / "sessions.jsonl"
READINGS = ROOT / "readings"

GROUPS: dict[str, tuple[str,...]] = {
    "見ること": ("見る", "見える", "見えた", "見つ", "見つめ", "眺め", "観", "視", "映", "目", "瞳", "眼", "視線", "光", "色", "明る", "暗", "影", "かたち", "形", "景色", "風景", "鏡", "写真", "映像"),
    "聴くこと": ("聴く", "聞く", "聴こえ", "聞こえ", "音", "声", "響", "歌", "囁", "耳", "静か", "沈黙", "黙", "騒", "音楽", "リズム"),
    "触れること": ("触れ", "触れる", "手触り", "触覚", "肌", "指", "掌", "温か", "暖か", "冷た", "冷え", "寒", "重", "軽", "硬", "柔ら", "痛", "手"),
    "媒体と記録": ("書く", "文字", "紙", "本", "記録", "記憶", "再生", "複製", "写真", "映像", "フィルム", "テープ", "レコード", "放送"),
}

RAW_POLYSEMY = {
    "手": "手紙・書き手等の役割名詞と、身体の手が同形",
    "見る": "見ると観るの同音異字を区別しない",
    "聞く": "聞く／聴く／訊くを区別しない",
}

DATE_PATTERN = re.compile(r"\d{4}年|\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}")

def load(path: Path, *, base_only: bool = False, exclude: str | None = None):
    if base_only or path.name != "fragments.jsonl":
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())

def strip_quotes(text: str) -> str:
    out = re.sub(r"「[^「」]*」", "", text)
    out = re.sub(r"『[^『』]*』", "", out)
    return out

def audit(fragments):
    rows=[]
    totals: dict[str, Counter] = {k: Counter() for k in GROUPS}
    docs: dict[str, set] = {k: set() for k in GROUPS}
    raw_totals = Counter()
    for frag in fragments:
        text=frag.get("text","")
        outside=strip_quotes(text)
        row={"fragment_id": frag["fragment_id"], "groups": {}, "raw": {}}
        for name, tokens in GROUPS.items():
            counts={}
            for tok in tokens:
                c=outside.count(tok)
                if c:
                    counts[tok]=c
                    totals[name][tok]+=c
                    docs[name].add(frag["fragment_id"])
            if counts:
                row["groups"][name]=counts
        # hand separate
        n_hand = outside.count("手")
        if n_hand:
            raw_totals["手"]+=n_hand
            row["raw"]["手"]=n_hand
        rows.append(row)
    created_at=Counter(f.get("created_at","?") for f in fragments)
    prose_chars=sum(len(f.get("text","")) for f in fragments)
    return {
        "fragments": len(fragments),
        "prose_chars": prose_chars,
        "rows": rows,
        "group_totals": {k: dict(v) for k,v in totals.items()},
        "group_docs": {k: sorted(v) for k,v in docs.items()},
        "raw_totals": dict(raw_totals),
        "created_at_values": dict(created_at),
    }

def report(data):
    lines=[]
    a=lines.append
    a("=== 知覚の鏡 — 台帳はどこで見、どこで聴き、どこで触れるか（採点ではありません） ===")
    a(f"対象: {data['fragments']} 編 / 本文計 {data['prose_chars']} 字")
    a("")
    a("--- 1. 感覚語群の出現（鉤括弧の外、地の文） ---")
    for name in GROUPS:
        totals=data["group_totals"].get(name,{})
        docs=data["group_docs"].get(name,[])
        total=sum(totals.values())
        detail="、".join(f"{k}×{v}" for k,v in sorted(totals.items(), key=lambda kv: -kv[1])) or "なし"
        a(f"  {name:<10}: {total:>3} 回 / {len(docs):>2} 編  （{detail}）")
    a("")
    a("--- 2. 多義の語 ---")
    for tok, note in RAW_POLYSEMY.items():
        n=data["raw_totals"].get(tok,0)
        a(f"  {tok}: {n} 回  注: {note}")
    a("")
    a("--- 3. メタデータに住む時間/知覚との接続 ---")
    a(f"  created_at 分布: {data['created_at_values']}")
    a("")
    a("--- 4. 読むための注意 ---")
    a("  ・語形の不在は感覚経験の不在を意味しない。比喩・無主語・否定を含む粗い計数である。")
    a("  ・鉤括弧外のみを数え、引用内の感覚語は除外した。入れ子は過剰除去で下限。")
    a("  ・視覚・聴覚・触覚の偏りは、本文の主題偏りを示すが、語り手の知覚能力の証明ではない。")
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(description="Sense audit")
    p.add_argument("--json", action="store_true")
    p.add_argument("--show", metavar="FRAG_ID")
    p.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    p.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args=p.parse_args()
    frags=load(FRAGMENTS, base_only=args.base_only, exclude=args.exclude_shard)
    data=audit(frags)
    if args.show:
        for r in data["rows"]:
            if r["fragment_id"]==args.show:
                print(json.dumps(r, ensure_ascii=False, indent=2))
                return 0
        print(f"{args.show}: not found")
        return 1
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(report(data))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
