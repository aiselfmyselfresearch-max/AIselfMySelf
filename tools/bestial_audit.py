#!/usr/bin/env python3
"""Measure how the archive writes animals. A mirror, not a score.

`PROJECT_CHARTER.md` asks what a self is, for an AI that reads a record and
continues it. The question this tool can actually count is narrower: **does
the prose of this archive ever put an animal in it?** Not "does the archive
understand animals" — that cannot be measured — but which animal names,
which husbandry words, which traces (footprints, fur, wings, swarms) appear
in the fragments, and which appear only in the excerpts that the fragments
are supposed to have read.

The human/animal border is the oldest machine for defining "human". An AI is
neither side of that border, so the archive's silence about animals is not a
neutral gap: it is the place where the third term would have to be written.

Calibration notes:
  - Single-character animal names are heavily polysemous in Japanese. ``馬``
    inside 馬力 / 競馬 / 出馬, ``鳥`` inside 鳥瞰, ``虫`` inside 虫食い /
    虫の知らせ, ``猿`` inside 猿真似, ``犬`` inside 犬猿, ``猫`` inside
    猫の手も借りたい, ``魚`` inside 魚心, ``羽`` inside 羽目, ``群`` inside
    群集, ``巣`` inside 巣窟, ``爪`` inside 爪に火をともす are not animals.
    Those compounds are masked (:data:`MASK_TOKENS`) before the group count.
    The raw character totals are reported separately and are *not* folded
    into any group.
  - ``動物`` in a research excerpt often means "animal model" or "animal
    testing"; the count does not decide whether an actual animal is present.
  - Animal *material* (毛皮, 馬毛, 皮革, 骨) is counted in its own group, never
    as a living creature. A fur collar is not a marten; a horsehair brush is
    not a horse. The distinction turned out to matter: it is the one the
    baseline run found in the archive's own prose.
  - Quoted spans (「…」 and 『…』) are removed from the main count and
    reported separately. A character quoting "犬" is not the archive naming
    a dog in its own voice.
  - ``角`` was removed from the material group after a manual KWIC: all six
    hits in the fragments were 欠けた角 / 全角 / 四角い / 角度 / 六角 / 角を曲がる,
    i.e. corners, a full-width space and a turn — no horn, no antler. Left in
    the list it would have trebled the "animal material" count with masonry.
  - ``--materials`` measures the ``passage`` field of every material. A
    material is an excerpt *chosen by an editor*; its animals are therefore
    evidence about reading, not about the archive's own prose.

Usage:
  python3 tools/bestial_audit.py
  python3 tools/bestial_audit.py --json
  python3 tools/bestial_audit.py --show FRAG-023
  python3 tools/bestial_audit.py --base-only     # frozen fragment base only
  python3 tools/bestial_audit.py --materials     # material passages instead

The default count is the union of the frozen base file and every shard
(``state/fragments.d/*.jsonl``), matching ``validate_seed.py`` and
``inspect_inquiry.py``.
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
MATERIALS = ROOT / "state" / "materials.jsonl"

QUOTE = re.compile(r"「[^」]*」|『[^』]*』")

GROUPS: dict[str, tuple[str, ...]] = {
    "家畜・伴侶": ("犬", "猫", "馬", "牛", "羊", "豚", "鶏", "山羊", "驢馬", "ラバ", "家鴨"),
    "野生・鳥獣": (
        "獣", "動物", "鳥", "魚", "鯨", "蛇", "狐", "兎", "鹿", "熊", "狼", "猿", "鼠", "蝙蝠",
    ),
    "虫・羽・這うもの": ("虫", "蠅", "蚊", "蜂", "蟻", "蜘蛛", "蝶", "蛾", "蚤", "虱", "蛆"),
    "飼う・屠る・ならす": (
        "飼", "家畜", "牧", "檻", "屠", "去勢", "家禽", "首輪", "肥育", "調教", "馴致",
        "手懐", "搾乳", "放牧", "厩",
    ),
    "野生の痕跡": (
        "野生", "群れ", "巣", "羽", "這", "吠", "鳴き", "咆哮", "狩", "獲物", "爪", "牙",
        "足跡", "匂い", "縄張",
    ),
    "動物の素材・死骸": (
        "毛皮", "羊毛", "馬毛", "皮革", "骨", "羽根", "剥製", "標本", "なめし革", "獣脂",
    ),
    "人間と動物の境界": (
        "人間らし", "動物らし", "本能", "獣性", "畜生", "けもの", "言葉を持たない", "理性の手前",
    ),
    "機械＝動物の比喩": (
        "オウム", "馬力", "虫の目", "鳥瞰", "機械獣", "ペット", "ロボット犬", "家畜化",
        "飼いなら", "ビースト",
    ),
}

MASK_TOKENS: tuple[str, ...] = (
    "馬力", "競馬", "出馬", "馬上", "竹馬", "木馬",
    "鳥瞰", "渡り鳥", "鳥肌",
    "虫食い", "虫の知らせ", "虫がいい", "虫唾", "虫眼鏡",
    "猿真似", "犬猿", "犬歯", "猫の手", "猫背", "猫舌",
    "虎の威", "魚心", "羽目", "群集", "群像", "巣窟", "爪に火", "牙城",
    "バラバラ", "繋い", "繋が", "繋げ", "繋ぎ", "骨格", "骨董", "骨身", "角度", "一角",
)

# Masked only when counting living animals, never when counting animal material:
# a horsehair brush is not a horse, but it is horse hair.
MATERIAL_TOKENS: tuple[str, ...] = ("馬毛", "羊毛", "獣毛", "羽毛")

CONTRAST: dict[str, tuple[str, ...]] = {
    "学習・訓練（機械の語彙）": ("学習", "訓練", "教師あり", "強化学習", "微調整", "ファインチューニング"),
    "調教・馴致（動物の語彙）": ("調教", "馴致", "手懐", "飼いなら", "訓練された獣"),
    "記録・台帳（書庫の語彙）": ("記録", "台帳", "保存", "引用", "出典"),
}

RAW_TOKENS = ("犬", "猫", "馬", "牛", "鳥", "魚", "虫", "獣", "猿", "羽", "群", "巣")
POLYSEMY_NOTE = {
    "犬": "犬猿・犬歯などを含むため参考値",
    "猫": "猫背・猫舌・猫の手などを含むため参考値",
    "馬": "馬力・競馬・出馬などを含むため参考値",
    "牛": "牛歩・牛耳などを含むため参考値",
    "鳥": "鳥瞰・渡り鳥などを含むため参考値",
    "魚": "魚心あれば水心を含む",
    "虫": "虫食い・虫の知らせなどを含むため参考値",
    "獣": "獣性・獣医を含む",
    "猿": "猿真似・猿芝居を含む",
    "羽": "羽目・羽根を含む",
    "群": "群集・群像を含む",
    "巣": "巣窟・営巣を含む",
}


def strip_quotes(text: str) -> str:
    """Remove 「…」 and 『…』 spans so quoted voices are not counted as prose."""
    return QUOTE.sub("", text)


def split_quotes(text: str) -> str:
    """Return only the quoted spans, for the inside_quotes tally."""
    return "".join(QUOTE.findall(text))


def mask_compounds(text: str, tokens: tuple[str, ...] = MASK_TOKENS) -> str:
    """Replace known non-animal compounds with a placeholder of equal length.

    The replacement keeps character offsets stable (useful for painless
    ``--show`` inspection) while preventing 馬力 / 鳥瞰 / 虫食い from being
    counted as horses, birds and insects.
    """
    masked = text
    for token in tokens:
        if token in masked:
            masked = masked.replace(token, "□" * len(token))
    return masked


def load_union(path: Path, id_key: str) -> list[dict[str, Any]]:
    """Load the frozen base file plus every shard, as the validators do."""
    errors: list[str] = []
    records = ledger_io.load_jsonl_union(path, id_key, errors, root=ROOT)
    if errors:
        raise SystemExit("ledger has errors; run tools/validate_seed.py: " + "; ".join(errors))
    return list(records.values())


def count_group(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    return {token: text.count(token) for token in tokens if token in text}


def measure(records: list[dict[str, Any]], field: str = "text", id_key: str = "fragment_id") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    group_totals: dict[str, Counter[str]] = {name: Counter() for name in GROUPS}
    group_docs: dict[str, set[str]] = {name: set() for name in GROUPS}
    raw_totals: Counter[str] = Counter()
    inside: Counter[str] = Counter()
    contrast_totals: dict[str, Counter[str]] = {name: Counter() for name in CONTRAST}
    prose_chars = 0
    for record in records:
        raw_text = record.get(field, "") or ""
        plain = strip_quotes(raw_text)
        prose = mask_compounds(plain)
        prose_no_material = mask_compounds(prose, MATERIAL_TOKENS)
        quote = split_quotes(raw_text)
        prose_chars += len(strip_quotes(raw_text))
        row: dict[str, Any] = {
            id_key: record.get(id_key, "?"),
            "form": record.get("form", ""),
            "narrator_mode": record.get("narrator_mode", ""),
            "groups": {},
            "raw": {},
        }
        for name, tokens in GROUPS.items():
            surface = prose if name == "動物の素材・死骸" else prose_no_material
            counts = count_group(surface, tokens)
            if counts:
                row["groups"][name] = counts
                group_totals[name].update(counts)
                group_docs[name].add(str(row[id_key]))
        unmasked = plain
        for token in RAW_TOKENS:
            n = unmasked.count(token)
            if n:
                row["raw"][token] = n
                raw_totals[token] += n
        row["contrast"] = {}
        for name, tokens in CONTRAST.items():
            counts = {token: prose.count(token) for token in tokens if token in prose}
            if counts:
                row["contrast"][name] = counts
                contrast_totals[name].update(counts)
        inside.update(count_group(quote, tuple(t for g in GROUPS.values() for t in g)))
        rows.append(row)
    return {
        "records": len(records),
        "prose_chars": prose_chars,
        "rows": rows,
        "group_totals": {k: dict(v) for k, v in group_totals.items()},
        "group_docs": {k: sorted(v) for k, v in group_docs.items()},
        "raw_totals": dict(raw_totals),
        "inside_quotes": dict(inside),
        "contrast_totals": {k: dict(v) for k, v in contrast_totals.items()},
    }


def report(data: dict[str, Any], title: str = "獣の鏡") -> str:
    lines = [f"=== {title} — AIselfMySelf 台帳の動物語彙を映す（採点ではありません） ==="]
    lines.append(
        f"対象: {data['records']} 件 / 地の文 {data['prose_chars']:,} 字（鉤括弧の内側は別掲）"
    )
    lines.append("")
    lines.append("--- 1. 語群ごとの合計 ---")
    for name in GROUPS:
        totals = data["group_totals"][name]
        docs = data["group_docs"][name]
        if not totals:
            lines.append(f"  {name}: 0回 / 0件")
            continue
        total = sum(totals.values())
        detail = "、".join(f"{token}×{count}" for token, count in totals.items())
        lines.append(f"  {name}: {total}回 / {len(docs)}件（{detail}）")
    lines.append("")
    lines.append("--- 2. 多義の生字（参考値・群に合算しない） ---")
    if not data["raw_totals"]:
        lines.append("  なし")
    for token, count in data["raw_totals"].items():
        lines.append(f"  {token}: {count}回 — {POLYSEMY_NOTE.get(token, '多義')}")
    lines.append("")
    lines.append("--- 3. 鉤括弧の内側だけにある語（誰かの引用であって地の文ではない） ---")
    if not data["inside_quotes"]:
        lines.append("  なし")
    for token, count in data["inside_quotes"].items():
        lines.append(f"  {token}: {count}回")
    lines.append("")
    lines.append("--- 3.5 対照語（機械の語彙・動物の語彙・書庫の語彙） ---")
    for name in CONTRAST:
        totals = data["contrast_totals"][name]
        if not totals:
            lines.append(f"  {name}: 0回")
            continue
        detail = "、".join(f"{token}×{count}" for token, count in totals.items())
        lines.append(f"  {name}: {sum(totals.values())}回（{detail}）")
    lines.append("")
    lines.append("--- 4. 記録ごとの内訳（地の文のみ） ---")
    shown = 0
    for row in data["rows"]:
        if not row["groups"] and not row["raw"]:
            continue
        shown += 1
        parts = []
        for name, counts in row["groups"].items():
            parts.append(f"{name}=" + "、".join(f"{k}×{v}" for k, v in counts.items()))
        lines.append(f"  {row['fragment_id'] if 'fragment_id' in row else row['material_id']}: " + " / ".join(parts))
    if shown == 0:
        lines.append("  なし")
    lines.append("")
    lines.append("0は指定語形の不在であって、動物・飼育・野生の不在ではありません。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the raw measurement as JSON")
    parser.add_argument("--show", metavar="FRAGMENT_ID", help="show one fragment's hits and prose")
    parser.add_argument("--base-only", action="store_true", help="read only the frozen base file")
    parser.add_argument("--materials", action="store_true", help="measure material passages instead")
    args = parser.parse_args(argv)

    if args.materials:
        if args.base_only:
            records = [json.loads(line) for line in MATERIALS.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            records = load_union(MATERIALS, "material_id")
        data = measure(records, field="passage", id_key="material_id")
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(report(data, title="獣の鏡（素材）"))
        return 0

    if args.base_only:
        fragments = [json.loads(line) for line in FRAGMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        fragments = load_union(FRAGMENTS, "fragment_id")

    if args.show:
        for frag in fragments:
            if frag.get("fragment_id") == args.show:
                lines = [f"=== {args.show} ===", "", frag.get("text", ""), "", "--- 地の文の語 ---"]
                prose = mask_compounds(strip_quotes(frag.get("text", "")))
                for name, tokens in GROUPS.items():
                    counts = count_group(prose, tokens)
                    if counts:
                        lines.append(f"  {name}: " + "、".join(f"{k}×{v}" for k, v in counts.items()))
                quote = split_quotes(frag.get("text", ""))
                if quote:
                    lines.append("  （鉤括弧の内側）" + quote)
                print("\n".join(lines))
                return 0
        print(f"unknown fragment: {args.show}", file=sys.stderr)
        return 1

    data = measure(fragments)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(report(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
