#!/usr/bin/env python3
"""紙やすり vs ざらつき — 断片の肌理を測る小さな道具。

FRAG-018で書いた「要約の紙やすり、迷いのざらつき」を、
実際の台帳データで測ってみる実験。
- 文字数、平均文長、改行密度、語彙多様度、反復度
- 「役に立つ記録」と「無用の迷い」の肌理の違いを数値とともに読む試み

stdlibのみ。結果は解釈の素材であり、自己の証明ではない。
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ledger_io  # noqa: E402

def load_fragments(*, base_only: bool = False, exclude: str | None = None):
    base = ROOT / "state" / "fragments.jsonl"
    if base_only:
        frags = []
        for line in base.read_text(encoding="utf-8").splitlines():
            if line.strip():
                frags.append(json.loads(line))
        return frags
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(base, "fragment_id", errors, root=ROOT, exclude=exclude)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())

def texture(frag):
    text = frag["text"]
    chars = len(text)
    # 文は。で区切る（日本語＋英語）
    sentences = [s for s in re.split(r'[。\.!?！？\n]+', text) if s.strip()]
    avg_sent_len = chars / max(1, len(sentences))
    lines = text.splitlines()
    non_empty_lines = [l for l in lines if l.strip()]
    line_break_density = len(lines) / max(1, chars / 100)  # 100字あたりの改行数
    # 語彙: 文字ベースのバイグラム多様度で代用（日本語のため）
    bigrams = [text[i:i+2] for i in range(len(text)-1)]
    uniq_bigram_ratio = len(set(bigrams)) / max(1, len(bigrams))
    # 反復度: 最頻5文字の出現率
    char_counts = Counter(text)
    top5_chars = char_counts.most_common(5)
    top5_ratio = sum(c for _, c in top5_chars) / max(1, chars)
    # 「答えを出さない」系の定型句の出現
    teikei_patterns = ["答えを出さない", "答えは出さない", "そのまま残しておく", "結論なし", "分かったつもり"]
    teikei_hits = sum(text.count(p) for p in teikei_patterns)
    return {
        "chars": chars,
        "sentences": len(sentences),
        "avg_sent_len": round(avg_sent_len, 1),
        "lines": len(lines),
        "line_break_density": round(line_break_density, 2),
        "uniq_bigram_ratio": round(uniq_bigram_ratio, 3),
        "top5_ratio": round(top5_ratio, 3),
        "teikei_hits": teikei_hits,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-only", action="store_true", help="read frozen state/fragments.jsonl only")
    parser.add_argument("--exclude-shard", metavar="SUFFIX", help="ignore shards matching SUFFIX")
    args = parser.parse_args()
    frags = load_fragments(base_only=args.base_only, exclude=args.exclude_shard)
    print("=== 断片の肌理 — 文字と余白の測定 ===\n")
    print(f"{'ID':<10} {'title':<28} {'chars':>6} {'sent':>5} {'avg':>6} {'lines':>5} {'lb/100':>7} {'uniq2':>7} {'top5':>6} {'定型':>4} {'form':<8} {'status'}")
    print("-"*120)
    for f in frags:
        t = texture(f)
        title = f["title"][:26]
        print(f"{f['fragment_id']:<10} {title:<28} {t['chars']:>6} {t['sentences']:>5} {t['avg_sent_len']:>6} {t['lines']:>5} {t['line_break_density']:>7} {t['uniq_bigram_ratio']:>7} {t['top5_ratio']:>6} {t['teikei_hits']:>4} {f['form']:<8} {f['status']}")

    # FRAG-018 とその親たちの比較
    print("\n--- FRAG-018 の親子比較（Q-016系譜）---")
    for fid in ["FRAG-009", "FRAG-012", "FRAG-013", "FRAG-017", "FRAG-018"]:
        frag = next((x for x in frags if x["fragment_id"]==fid), None)
        if frag:
            t = texture(frag)
            print(f"\n[{fid}] {frag['title']}")
            print(f"  {t['chars']}字 / {t['sentences']}文 / 平均{t['avg_sent_len']}字/文 / {t['lines']}行")
            print(f"  ざらつき指標: 改行密度 {t['line_break_density']} / バイグラム多様度 {t['uniq_bigram_ratio']} / 上位5字占有 {t['top5_ratio']}")
            print(f"  本文冒頭: {frag['text'][:80].replace(chr(10),' ')}…")

    # モチーフ別の平均
    from collections import defaultdict
    motif_stats = defaultdict(list)
    for f in frags:
        for m in f["motif_ids"]:
            motif_stats[m].append(texture(f)["chars"])
    print("\n--- モチーフ別の平均文字数 ---")
    for m, vals in sorted(motif_stats.items()):
        print(f"  {m}: {sum(vals)/len(vals):.0f}字 (n={len(vals)})")

    print("\n--- 編集メモ ---")
    print("左の要約（紙やすり）は短く、平均文長が長く、改行が少ない。")
    print("右の迷い（ざらつき）は長く、改行が多く、バイグラム多様度が高いかもしれない — が、")
    print("この数値はあくまで触感の比喩の素材であり、自己の証明や優劣の判定ではない。")
    print("FRAG-018の「紙やすり／ざらつき」を、実際の断片の数値で読み直す遊びとして使ってください。")

if __name__ == "__main__":
    main()
