#!/usr/bin/env python3
"""Audit vegetal / botanical / seed / tree vocabulary across fragments, materials, and readings.

Counts surface word forms for living plants alongside dead-wood/manuscript relics
and computer-science / archive arborescent metaphors:

Living-plant groups (5):
- seed_sprout       : 種（植物の種子）・発芽・播種・芽・双葉・球根・胞子
- root_stem_leaf    : 根・幹・茎・枝・葉・樹皮・年輪・維管束・光合成
- flower_fruit      : 花・蕾・開花・満開・花弁・花粉・実・果実・桜・菊・蓮
- tree_forest_herb  : 樹木・大樹・倒木・森・林・草・雑草・薬草・苔・羊歯・菌根
- soil_cultivation  : 土・土壌・腐葉土・凍土・庭・畑・農耕・接ぎ木・植林・種子庫

Control groups (2):
- timber_paper_relic: 木材・丸太・木片・木箱・版木・拍子木・薪・炭・草稿・草子・台紙
- arborescent_meta  : 実行状態の木・構文木・決定木・分岐・枝分かれ・枝刈り・乱数シード・言葉・根拠

Compound words where a botanical kanji is part of a non-vegetal word (e.g.
種類, 人種, 屋根, 根拠, 言葉, 葉書, 火花, 花押, 草稿, 煙草, 粘土, 国土) are masked out
before counting single-kanji botanical tokens, or routed explicitly to the
appropriate control group.

All numbers are counts of surface strings. Nothing here measures whether an
archive grows, whether a text has life, or whether a machine perceives a plant.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_io  # noqa: E402


QUOTE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"「[^」]*」"),
    re.compile(r"『[^』]*』"),
    re.compile(r"“[^”]*”"),
    re.compile(r'"[^"\n]*"'),
)


VEGETAL_GROUPS: dict[str, dict[str, Any]] = {
    "seed_sprout": {
        "label": "種・芽・発芽・胞子",
        "kind": "living",
        "note": "種子・発芽・播種・双葉・新芽・球根・胞子（種類・人種・種明かし・次回の種は除外）",
        "terms": [
            "種子貯蔵庫",
            "種子バンク",
            "種子庫",
            "発芽",
            "播種",
            "種まき",
            "種蒔き",
            "種袋",
            "種子",
            "実生",
            "幼根",
            "双葉",
            "子葉",
            "本葉",
            "新芽",
            "若芽",
            "木の芽",
            "芽吹き",
            "芽吹く",
            "芽吹い",
            "芽生え",
            "芽生える",
            "球根",
            "塊茎",
            "地下茎",
            "胞子",
            "休眠打破",
            "蒔く",
            "蒔い",
            "蒔か",
            "蒔け",
            "種",
            "芽",
        ],
    },
    "root_stem_leaf": {
        "label": "根・幹・枝・葉・年輪",
        "kind": "living",
        "note": "植物の根・幹・茎・枝・葉・樹皮・年輪・維管束・光合成（言葉・屋根・根拠・幹線は除外／対照へ）",
        "terms": [
            "光合成",
            "葉緑体",
            "葉緑素",
            "クロロフィル",
            "維管束",
            "道管",
            "師管",
            "形成層",
            "気孔",
            "蒸散",
            "ひげ根",
            "毛根",
            "細根",
            "主根",
            "側根",
            "気根",
            "根っこ",
            "根張り",
            "根上がり",
            "年輪",
            "樹皮",
            "木肌",
            "樹液",
            "葉脈",
            "落葉",
            "紅葉",
            "黄葉",
            "新緑",
            "青葉",
            "若葉",
            "枯れ葉",
            "枯葉",
            "落ち葉",
            "落葉樹",
            "常緑樹",
            "針葉樹",
            "広葉樹",
            "押し葉",
            "芭蕉葉",
            "梛の葉",
            "草の根",
            "木の根",
            "桜の根",
            "小枝",
            "枯れ枝",
            "枯枝",
            "枝ぶり",
            "梢",
            "樹幹",
            "茎",
            "幹",
            "根",
            "枝",
            "葉",
        ],
    },
    "flower_fruit": {
        "label": "花・開花・果実・花名",
        "kind": "living",
        "note": "花・蕾・満開・花粉・果実・桜・菊・蓮・薔薇（火花・花崗岩・花押・花街は除外）",
        "terms": [
            "花びら",
            "花弁",
            "花冠",
            "花托",
            "花粉",
            "雄しべ",
            "雌しべ",
            "雄蕊",
            "雌蕊",
            "花束",
            "切り花",
            "切花",
            "生け花",
            "いけばな",
            "華道",
            "立花",
            "投入花",
            "押し花",
            "草花",
            "野花",
            "顕花植物",
            "隠花植物",
            "満開",
            "開花",
            "落花",
            "花ざかり",
            "花盛り",
            "つぼみ",
            "蕾",
            "咲く",
            "咲き",
            "咲い",
            "咲か",
            "咲け",
            "結実",
            "果実",
            "木の実",
            "ドングリ",
            "団栗",
            "ナツメヤシ",
            "無花果",
            "いちじく",
            "林檎",
            "りんご",
            "葡萄",
            "ぶどう",
            "蜜柑",
            "柘榴",
            "胡桃",
            "桜の花",
            "桜の森",
            "桜の樹",
            "桜の木",
            "夜桜",
            "山桜",
            "吉野桜",
            "梅の花",
            "白梅",
            "紅梅",
            "朝顔",
            "撫子",
            "なでしこ",
            "女郎花",
            "おみなえし",
            "をみなへし",
            "藤袴",
            "ふじばかま",
            "桔梗",
            "アイリス",
            "向日葵",
            "ひまわり",
            "紫陽花",
            "あじさい",
            "蒲公英",
            "たんぽぽ",
            "蓮の花",
            "睡蓮",
            "百合",
            "野薔薇",
            "薔薇",
            "桜",
            "櫻",
            "椿",
            "菊",
            "蕊",
            "萼",
            "花",
        ],
    },
    "tree_forest_herb": {
        "label": "樹木・森・草・苔・菌根",
        "kind": "living",
        "note": "樹木・倒木更新・森・草木・薬草・苔・粘菌・菌根（木材・草稿・人名は除外／対照へ）",
        "terms": [
            "倒木更新",
            "原生林",
            "自然林",
            "雑木林",
            "鎮守の森",
            "神林",
            "樹林",
            "山林",
            "森林",
            "密林",
            "竹林",
            "竹藪",
            "樹冠",
            "林冠",
            "老樹",
            "巨樹",
            "大樹",
            "古木",
            "老木",
            "親木",
            "稚樹",
            "苗木",
            "若木",
            "倒木",
            "風倒木",
            "街路樹",
            "並木",
            "植木",
            "盆栽",
            "樹木",
            "木々",
            "樹々",
            "草木",
            "植物相",
            "植物界",
            "植物盲",
            "植物学",
            "植物誌",
            "本草綱目",
            "本草",
            "薬草",
            "雑草",
            "野草",
            "下草",
            "秋草",
            "七草",
            "牧草",
            "水草",
            "海藻",
            "藻類",
            "蘚苔類",
            "蘚苔",
            "羊歯",
            "シダ",
            "粘菌",
            "菌根ネットワーク",
            "菌根菌",
            "菌根",
            "菌糸",
            "マザーツリー",
            "破れ芭蕉",
            "破芭蕉",
            "芭蕉の葉",
            "芭蕉の株",
            "芭蕉の精",
            "エゾマツ",
            "えぞ松",
            "屋久杉",
            "縄文杉",
            "大楠",
            "大樟",
            "樟",
            "楠",
            "梛",
            "桧",
            "檜",
            "欅",
            "樫",
            "柏",
            "柳",
            "尾花",
            "ススキ",
            "すすき",
            "葛",
            "萩",
            "植物",
            "苔",
            "森",
            "林",
            "樹",
            "木",
            "草",
        ],
    },
    "soil_cultivation": {
        "label": "土・庭・農耕・接ぎ木・植林",
        "kind": "living",
        "note": "土壌・腐葉土・永久凍土・庭・畑・接ぎ木・植林・植物標本（粘土・国土・土台・土佐は除外）",
        "terms": [
            "ジーンバンク",
            "植物標本帳",
            "標本帳",
            "植物標本",
            "ハーバリウム",
            "植物園",
            "演習林",
            "腐葉土",
            "培養土",
            "永久凍土",
            "凍土",
            "土壌",
            "黒土",
            "赤土",
            "庭土",
            "畑土",
            "肥沃",
            "堆肥",
            "肥料",
            "接ぎ木",
            "接木",
            "台木",
            "穂木",
            "挿し木",
            "挿木",
            "植え替え",
            "植林",
            "造林",
            "伐採",
            "伐木",
            "濫伐",
            "農耕",
            "園芸",
            "庭園",
            "庭師",
            "花壇",
            "温室",
            "苗床",
            "田畑",
            "水田",
            "耕す",
            "耕し",
            "植える",
            "植え",
            "培う",
            "培い",
            "枯れる",
            "枯れ",
            "立ち枯れ",
            "朽ちる",
            "朽ち",
            "畑",
            "庭",
            "土",
        ],
    },
    "timber_paper_relic": {
        "label": "木材・木器・草稿（切断遺骸・対照）",
        "kind": "control",
        "note": "木材・丸太・木片・木箱・積み木・草稿・草子・煙草・洋紙（切断・加工後の植物由来物）",
        "terms": [
            "おがくず",
            "割り箸",
            "積み木",
            "拍子木",
            "パピルス",
            "木の塊",
            "添え木",
            "添木",
            "横木",
            "木枠",
            "木材",
            "材木",
            "丸太",
            "角材",
            "板材",
            "木片",
            "木屑",
            "木箱",
            "木札",
            "木簡",
            "竹簡",
            "版木",
            "木版",
            "木彫",
            "木造",
            "木製",
            "木槌",
            "木靴",
            "木馬",
            "木琴",
            "木炭",
            "切り株",
            "切株",
            "流木",
            "枯れ木",
            "枯木",
            "朽木",
            "枕木",
            "垂木",
            "棟木",
            "和紙",
            "洋紙",
            "台紙",
            "草稿",
            "草案",
            "草子",
            "草紙",
            "枕草子",
            "徒然草",
            "煙草",
            "たばこ",
            "タバコ",
            "薪",
        ],
    },
    "arborescent_meta": {
        "label": "構文木・分岐・シード・言葉（比喩・対照）",
        "kind": "control",
        "note": "実行状態の木・構文木・決定木・分岐・枝刈り・乱数シード・次回の種・言葉・根拠",
        "terms": [
            "Tree of Thoughts",
            "random forest",
            "Random Forests",
            "manual_seed",
            "random_seed",
            "random seed",
            "validate_seed",
            "human_seed",
            "L-system",
            "実行状態の木",
            "状態の木",
            "問いの枝",
            "ランダムフォレスト",
            "ツリー構造",
            "木構造",
            "構文木",
            "句構造木",
            "決定木",
            "探索木",
            "系統樹",
            "樹形図",
            "家系図",
            "思考の木",
            "乱数シード",
            "初期シード",
            "枝刈り",
            "pruning",
            "次回の種",
            "次の種",
            "問いの種",
            "探求の種",
            "物語の種",
            "対話の種",
            "不安の種",
            "悩みの種",
            "議論の種",
            "どの枝を伸ばすか",
            "枝を伸ばす",
            "枝葉末節",
            "枝葉",
            "枝分かれ",
            "分岐",
            "合い言葉",
            "合言葉",
            "言の葉",
            "言葉",
            "根源",
            "根拠",
            "根本",
            "根底",
            "根幹",
        ],
    },
}


EXCLUDED_COMPOUNDS: tuple[str, ...] = (
    # 種 — classification / sort / ethnicity / inoculation / spark
    "第一種",
    "第二種",
    "第三種",
    "異種",
    "同種",
    "変種",
    "亜種",
    "新種",
    "原種",
    "雑種",
    "純種",
    "人種",
    "民族種",
    "業種",
    "職種",
    "機種",
    "車種",
    "兵種",
    "語種",
    "火種",
    "血種",
    "接種",
    "予防接種",
    "種類",
    "種別",
    "種目",
    "種族",
    "種々",
    "種種",
    "各種",
    "多種",
    "数種",
    "何種",
    "全種",
    "両種",
    "一種",
    "二種",
    "三種",
    "四種",
    "五種",
    "六種",
    "七種",
    "八種",
    "九種",
    "十種",
    "百種",
    "千種",
    "万種",
    "手持ちの種",
    "手品の種",
    "種明かし",
    "種明し",
    "噂の種",
    "頭痛の種",
    # 芽 — proper nouns / idioms not literal plant buds
    "麦芽糖",
    # 根 — architectural / abstract / proper nouns
    "屋根裏",
    "屋根",
    "垣根",
    "羽根",
    "矢羽根",
    "付け根",
    "付根",
    "根元",
    "根気",
    "根性",
    "根絶",
    "根治",
    "根強い",
    "根強く",
    "根ざす",
    "根ざし",
    "根付く",
    "根付き",
    "根付い",
    "根掘り葉掘り",
    "島根",
    "箱根",
    "彦根",
    "利根",
    "白根",
    "赤根",
    "蓮根",
    # 幹 — human hierarchy / transport
    "新幹線",
    "幹線",
    "幹部",
    "幹事",
    "主幹",
    "基幹",
    "体幹",
    "脳幹",
    "才幹",
    # 枝 — proper nouns / tools
    "楊枝",
    "爪楊枝",
    "枝豆",
    # 葉 — postal / era / anatomy / proper nouns
    "絵葉書",
    "葉書",
    "万葉集",
    "万葉",
    "千葉",
    "双葉山",
    "前頭葉",
    "側頭葉",
    "頭頂葉",
    "後頭葉",
    "肺葉",
    "中葉",
    "末葉",
    "初葉",
    "前葉",
    "後葉",
    "一葉",
    "樋口一葉",
    "尾崎紅葉",
    # 花 — sparks / granite / signature / entertainment / proper nouns
    "火花",
    "花火",
    "花崗岩",
    "花押",
    "花街",
    "花柳",
    "花形",
    "花道",
    "花嫁",
    "花婿",
    "花見酒",
    "花生け",
    "花瓶",
    "花器",
    "風花",
    "雪花",
    "浪花",
    "難波",
    "徒花",
    "落花生",
    "天花",
    "花田",
    "花園",
    # 桜 / 梅 / 菊 / 椿 / 松 / 杉 / 竹 / 柳 / 林 / 森 / 木 / 樹 — proper nouns / non-living
    "桜田",
    "桜島",
    "梅雨",
    "梅毒",
    "梅干",
    "梅干し",
    "白梅学園",
    "菊池",
    "菊五郎",
    "松尾芭蕉",
    "松尾",
    "松岡",
    "松下",
    "松本",
    "松平",
    "松竹",
    "松明",
    "たいまつ",
    "杉並",
    "杉田",
    "杉本",
    "上杉",
    "高杉",
    "竹中",
    "竹内",
    "竹下",
    "竹田",
    "竹取",
    "爆竹",
    "柳田",
    "柳宗元",
    "川柳",
    "花柳界",
    "小林",
    "大林",
    "若林",
    "林立",
    "林業",
    "農林",
    "伯林",
    "ベルリン",
    "少林",
    "森鴎外",
    "森鷗外",
    "青森",
    "森羅万象",
    "森厳",
    "森閑",
    "木曜",
    "木星",
    "木村",
    "木下",
    "木戸",
    "鈴木",
    "佐々木",
    "青木",
    "高木",
    "黒木",
    "白木",
    "赤木",
    "栃木",
    "厚木",
    "六本木",
    "麻木",
    "石川啄木",
    "啄木",
    "土木",
    "木綿",
    "木魚",
    "木鐸",
    "樹木希林",
    "樹立",
    "樹氷",
    "果樹園",
    # 草 — manuscript / posture / footwear / proper nouns
    "草創",
    "草書",
    "仕草",
    "しぐさ",
    "道草",
    "草履",
    "草鞋",
    "わらじ",
    "浅草",
    "天草",
    "本草学",
    "起草",
    "除草剤",
    # 土 — clay / territory / weekday / planet / proper nouns
    "粘土板",
    "粘土",
    "国土",
    "領土",
    "本土",
    "郷土",
    "風土",
    "浄土",
    "冥土",
    "黄土",
    "焦土",
    "赤土器",
    "土器",
    "土産",
    "土曜",
    "土星",
    "土台",
    "土間",
    "土俵",
    "土塀",
    "土蔵",
    "土方",
    "土佐",
    "土岐",
    "安土",
    "土耳其",
    # 庭 / 畑 — non-garden compounds
    "家庭",
    "法廷",
    "校庭",
    "中庭",
    "箱庭",
    "庭訓",
    "田畑",  # handled in soil_cultivation before exclusion if matched first, keep out of exclusion!
)

# Remove any accidental overlap where a term in VEGETAL_GROUPS also appears in EXCLUDED_COMPOUNDS
_GROUP_TERM_SET = {
    t for g in VEGETAL_GROUPS.values() for t in g["terms"]
}
EFFECTIVE_EXCLUSIONS: tuple[str, ...] = tuple(
    w for w in EXCLUDED_COMPOUNDS if w not in _GROUP_TERM_SET
)


RAW_KANJI: dict[str, str] = {
    "種": "種子 / 種類・人種・次回の種",
    "芽": "新芽・発芽",
    "根": "植物の根 / 屋根・根拠・根元",
    "幹": "樹幹 / 幹線・根幹",
    "枝": "樹枝 / 分岐の枝・枝葉",
    "葉": "植物の葉 / 言葉・合言葉・葉書",
    "花": "植物の花 / 火花・花押・芸の花",
    "木": "生木 / 木材・木箱・実行状態の木",
    "樹": "樹木 / 樹立・系統樹",
    "森": "森林 / 森鷗外・青森",
    "草": "生草 / 草稿・草子・煙草",
    "土": "土壌 / 粘土・国土・土台・土佐",
}


SEED_NON_BOTANICAL_RE = re.compile(
    r"(?:"
    r"[一二三四五六七八九十百千万何各多全両数異同変亜新原雑純人業職機車兵語火血接]種"
    r"|種(?:明かし|明し|[類別目族々種])"
    r"|(?:次回|次|問い|探求|物語|対話|不安|悩み|議論|頭痛|噂|手品|手持ち)の種"
    r")"
)


def _build_scanner() -> tuple[re.Pattern[str], dict[str, tuple[str, ...]], dict[str, str]]:
    term_to_group: dict[str, str] = {}
    for group_key, spec in VEGETAL_GROUPS.items():
        for term in spec["terms"]:
            term_to_group.setdefault(term, group_key)
    all_tokens = sorted(
        set(term_to_group.keys()) | set(EFFECTIVE_EXCLUSIONS),
        key=lambda item: (-len(item), item),
    )
    by_first: dict[str, list[str]] = {}
    for tok in all_tokens:
        by_first.setdefault(tok[0], []).append(tok)
    anchor_re = re.compile("[" + "".join(re.escape(ch) for ch in sorted(by_first)) + "]")
    by_first_tuples = {ch: tuple(toks) for ch, toks in by_first.items()}
    return anchor_re, by_first_tuples, term_to_group


ANCHOR_RE, TOKENS_BY_FIRST, TERM_TO_GROUP = _build_scanner()


def split_prose_and_quotes(text: str) -> tuple[str, str]:
    """Return `(prose_without_quotes, quoted_segments_joined)`."""
    spans: list[tuple[int, int]] = []
    for pat in QUOTE_PATTERNS:
        for match in pat.finditer(text):
            spans.append(match.span())
    if not spans:
        return text, ""
    spans.sort()
    merged: list[tuple[int, int]] = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    prose_parts: list[str] = []
    quote_parts: list[str] = []
    cursor = 0
    for start, end in merged:
        prose_parts.append(text[cursor:start])
        quote_parts.append(" ")
        quote_parts.append(text[start:end])
        prose_parts.append(" ")
        cursor = end
    prose_parts.append(text[cursor:])
    return "".join(prose_parts), "".join(quote_parts)


def count_seed_literal(text: str) -> int:
    """Count '種' occurrences that survive non-botanical compound stripping."""
    cleaned = SEED_NON_BOTANICAL_RE.sub("  ", text)
    return cleaned.count("種")


def scan_text(text: str) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {key: {} for key in VEGETAL_GROUPS}
    pos = 0
    search = ANCHOR_RE.search
    startswith = text.startswith
    by_first = TOKENS_BY_FIRST
    term_to_group = TERM_TO_GROUP
    n = len(text)
    while pos < n:
        match = search(text, pos)
        if match is None:
            break
        idx = match.start()
        candidates = by_first[text[idx]]
        matched_tok: str | None = None
        for tok in candidates:
            if startswith(tok, idx):
                matched_tok = tok
                break
        if matched_tok is None:
            pos = idx + 1
            continue
        group = term_to_group.get(matched_tok)
        if group is not None:
            bucket = counts[group]
            bucket[matched_tok] = bucket.get(matched_tok, 0) + 1
        pos = idx + len(matched_tok)
    return counts


def _aggregate_docs(docs: list[tuple[str, str]]) -> dict[str, Any]:
    group_totals: dict[str, int] = {key: 0 for key in VEGETAL_GROUPS}
    group_docs: dict[str, list[str]] = {key: [] for key in VEGETAL_GROUPS}
    term_totals: dict[str, dict[str, int]] = {key: {} for key in VEGETAL_GROUPS}
    living_docs_set: set[str] = set()
    control_docs_set: set[str] = set()
    char_total = 0

    for doc_id, text in docs:
        char_total += len(text)
        scanned = scan_text(text)
        has_living = False
        has_control = False
        for key, bucket in scanned.items():
            total = sum(bucket.values())
            if total > 0:
                group_totals[key] += total
                group_docs[key].append(doc_id)
                if VEGETAL_GROUPS[key]["kind"] == "living":
                    has_living = True
                else:
                    has_control = True
                agg = term_totals[key]
                for tok, num in bucket.items():
                    agg[tok] = agg.get(tok, 0) + num
        if has_living:
            living_docs_set.add(doc_id)
        if has_control:
            control_docs_set.add(doc_id)

    groups_out: dict[str, Any] = {}
    living_total = 0
    control_total = 0
    for key, spec in VEGETAL_GROUPS.items():
        top_terms = sorted(
            term_totals[key].items(), key=lambda item: (-item[1], item[0])
        )
        cnt = group_totals[key]
        if spec["kind"] == "living":
            living_total += cnt
        else:
            control_total += cnt
        groups_out[key] = {
            "label": spec["label"],
            "kind": spec["kind"],
            "note": spec.get("note", ""),
            "count": cnt,
            "doc_count": len(group_docs[key]),
            "docs": group_docs[key][:30],
            "top_terms": dict(top_terms[:20]),
        }

    return {
        "doc_total": len(docs),
        "char_total": char_total,
        "living_total": living_total,
        "living_doc_count": len(living_docs_set),
        "control_total": control_total,
        "control_doc_count": len(control_docs_set),
        "groups": groups_out,
    }


def _snippet(text: str, start: int, width: int = 22) -> str:
    left = max(0, start - width)
    right = min(len(text), start + width + 1)
    return text[left:right].replace("\n", "⏎")


def inspect_raw_kanji_in_fragments(
    fragments: list[dict[str, Any]], width: int = 22
) -> dict[str, list[dict[str, str]]]:
    """Return KWIC rows for each raw kanji, from fragment prose only."""
    rows: dict[str, list[dict[str, str]]] = {ch: [] for ch in RAW_KANJI}
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, _quoted = split_prose_and_quotes(str(frag.get("text", "")))
        for ch in RAW_KANJI:
            start = 0
            while True:
                index = prose.find(ch, start)
                if index < 0:
                    break
                rows[ch].append(
                    {"fragment_id": fid, "snippet": _snippet(prose, index, width)}
                )
                start = index + len(ch)
    return rows


def measure_vegetal_audit(
    fragments: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    readings: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Measure vegetal / tree / seed vocabulary across fragments, materials, and readings.

    Everything is a count of surface word forms. Nothing here measures whether an
    archive grows, whether a text is alive, or whether a machine perceives a plant.
    """
    prose_docs: list[tuple[str, str]] = []
    quote_docs: list[tuple[str, str]] = []
    seed_rows: list[dict[str, Any]] = []
    for frag in fragments:
        fid = str(frag.get("fragment_id", ""))
        prose, quoted = split_prose_and_quotes(str(frag.get("text", "")))
        prose_docs.append((fid, prose))
        quote_docs.append((fid, quoted))
        total_seed = prose.count("種")
        literal_seed = count_seed_literal(prose)
        if total_seed:
            seed_rows.append(
                {
                    "fragment_id": fid,
                    "seed_total": total_seed,
                    "seed_literal": literal_seed,
                }
            )

    material_docs: list[tuple[str, str]] = []
    for mat in materials or []:
        mid = str(mat.get("material_id", ""))
        blob = " ".join(
            [
                str(mat.get("title", "")),
                str(mat.get("passage", "")),
                str(mat.get("source_note", "")),
            ]
        )
        material_docs.append((mid, blob))

    if readings is None:
        readings = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "readings").glob("*.md"))
        ]

    kwic = inspect_raw_kanji_in_fragments(fragments)
    living_keys = [k for k, v in VEGETAL_GROUPS.items() if v["kind"] == "living"]
    control_keys = [k for k, v in VEGETAL_GROUPS.items() if v["kind"] == "control"]

    return {
        "fragment_count": len(fragments),
        "fragments_prose": _aggregate_docs(prose_docs),
        "fragments_quotes": _aggregate_docs(quote_docs),
        "materials": _aggregate_docs(material_docs),
        "readings": _aggregate_docs(readings),
        "raw_kanji_kwic": kwic,
        "raw_kanji_counts": {ch: len(rows) for ch, rows in kwic.items()},
        "seed_rows": seed_rows,
        "seed_total": sum(row["seed_total"] for row in seed_rows),
        "seed_literal": sum(row["seed_literal"] for row in seed_rows),
        "group_order": list(VEGETAL_GROUPS.keys()),
        "living_group_order": living_keys,
        "control_group_order": control_keys,
    }


def _load_union(collection: str, key: str, base_only: bool) -> list[dict[str, Any]]:
    errors: list[str] = []
    path = ROOT / "state" / f"{collection}.jsonl"
    if base_only:
        text = ledger_io.read_text_stable(path)
        out: list[dict[str, Any]] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line:
                out.append(json.loads(line))
        return out
    records = ledger_io.load_jsonl_union(path, key, errors, root=ROOT)
    if errors:
        raise RuntimeError("; ".join(errors))
    return list(records.values())


def _print_human(report: dict[str, Any], kwic: bool) -> None:
    fp = report["fragments_prose"]
    print("=== vegetal_audit — 植物・樹木・種子・根・花の語彙 ===")
    print()
    print(
        f"断片           : {report['fragment_count']} 編 / 地の文 {fp['char_total']:,} 字 "
        f"（生きた植物5群 計 {fp['living_total']} 回・{fp['living_doc_count']} 編 / "
        f"遺骸・比喩対照2群 計 {fp['control_total']} 回・{fp['control_doc_count']} 編）"
    )
    for key in report["group_order"]:
        info = fp["groups"][key]
        tag = "植物" if info["kind"] == "living" else "対照"
        print(f"                 [{tag}] {info['label']}: {info['count']} 回 / {info['doc_count']} 編  {info['top_terms']}")
    print(
        "生字KWIC（地の文）: "
        + " / ".join(f"{ch}={report['raw_kanji_counts'][ch]}" for ch in RAW_KANJI)
    )
    print(
        f"「種」の内訳      : 全 {report['seed_total']} 回 / 非植物複合語を除く "
        f"{report['seed_literal']} 回"
    )
    qp = report["fragments_quotes"]
    print(
        f"引用内         : {qp['char_total']:,} 字 "
        f"（生きた植物5群 {qp['living_total']} 回 / 対照2群 {qp['control_total']} 回）"
    )
    for key in report["group_order"]:
        info = qp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 編")
    mp = report["materials"]
    print(
        f"素材           : {mp['doc_total']:,} 件 / {mp['char_total']:,} 字 "
        f"（生きた植物5群 {mp['living_total']:,} 回 / 対照2群 {mp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = mp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 件")
    rp = report["readings"]
    print(
        f"精読報告       : {rp['doc_total']} 本 / {rp['char_total']:,} 字 "
        f"（生きた植物5群 {rp['living_total']:,} 回 / 対照2群 {rp['control_total']:,} 回）"
    )
    for key in report["group_order"]:
        info = rp["groups"][key]
        print(f"                 {info['label']}: {info['count']} 回 / {info['doc_count']} 本")
    print()
    print("註: 語形の数であり、植物の成長・生命の実在・機械の知覚の判定ではない。")
    if kwic:
        print()
        for ch, rows in report["raw_kanji_kwic"].items():
            print(f"--- 生字「{ch}」{len(rows)} 箇所（{RAW_KANJI[ch]}）---")
            for row in rows[:40]:
                print(f"  {row['fragment_id']}: …{row['snippet']}…")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--kwic", action="store_true")
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args(argv)
    fragments = _load_union("fragments", "fragment_id", args.base_only)
    materials = _load_union("materials", "material_id", args.base_only)
    report = measure_vegetal_audit(fragments, materials)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report, args.kwic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
