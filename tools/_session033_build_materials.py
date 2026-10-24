# -*- coding: utf-8 -*-
"""SESSION-033 用の新規素材 48 件を state/materials.jsonl に追加する生成スクリプト。

テーマ：「数えること、測ること、余り——書庫は何を数え、何を数えていないか」
新モチーフ：MOTIF-015「数えること、測ること、余り」
新規素材ID：MAT-LIT-286〜319（34 件）、MAT-EVD-20261024-59〜71（13 件）、MAT-TRC-011（1 件） 計 48 件
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATERIALS_PATH = ROOT / "state" / "materials.jsonl"
ORIGIN_COMMIT = "f7969144fb0196588517d97c7ab40a7f8f8ca0ea"
EVIDENCE_PATH = "readings/2026-10-24-session-033-counting-and-remainder.md"
REPOSITORY = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"


def entry(material_id, kind, title, source, passage, passage_language, context,
          source_note, literary_invitation, scope_note, motif_ids):
    return {
        "context": context,
        "kind": kind,
        "literary_invitation": literary_invitation,
        "material_id": material_id,
        "motif_ids": motif_ids,
        "origin": {
            "commit": ORIGIN_COMMIT,
            "evidence_record_id": material_id,
            "evidence_record_path": EVIDENCE_PATH,
            "repository": REPOSITORY,
            "source_record_id": "SRC-" + material_id,
            "source_record_path": EVIDENCE_PATH,
        },
        "passage": passage,
        "passage_language": passage_language,
        "scope_note": scope_note,
        "source": source,
        "source_note": source_note,
        "title": title,
    }


def src(source_id, title, authors, year, url, version_note):
    return {
        "authors": authors,
        "source_id": source_id,
        "title": title,
        "url": url,
        "version_note": version_note,
        "year": year,
    }


E15 = ["MOTIF-015"]
materials = []

# ---------------------------------------------------------------------------
# 第1群 数える共同体、数えられる身体（MAT-LIT-286〜295）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-286", "literary_text",
    "創世記15:5——星を数えてみよ、数えられるなら",
    src("SRC-MAT-LIT-286", "創世記 15:5（בראשית טו, ה）",
        ["ヘブライ語聖書（創世記）"], -500,
        "https://www.sefaria.org/Genesis.15.5",
        "ヘブライ語本文。日本語訳は編者による。成立年代は諸説あるため概数。"),
    "הַבֶּט־נָא הַשָּׁמַיְמָה וּסְפֹר הַכּוֹכָבִים（天を仰いで、星を数えてみよ）",
    "he",
    "アブラハムに子孫の多さが約束される場面。数える行為そのものが、数えきれなさの比喩として命じられる。",
    "SESSION-033で追加した対話素材。数えきれないことが約束の根拠になる構図から、この書庫の「未消化素材」の多さを読む。",
    "数えきれないという事実は、欠陥なのか、それとも約束の形式なのか。",
    "宗教文書の一節。信仰や神学の真偽を扱わず、数えることの修辞だけを読む。",
    E15 + ["MOTIF-001"]))
materials.append(entry(
    "MAT-LIT-287", "literary_text",
    "詩篇90:12——われらの日を数えることを教えたまえ",
    src("SRC-MAT-LIT-287", "詩篇 90:12（תהילים צ, יב）",
        ["ヘブライ語聖書（詩篇）"], -400,
        "https://www.sefaria.org/Psalms.90.12",
        "ヘブライ語本文。日本語訳は編者による。成立年代は概数。"),
    "לִמְנוֹת יָמֵינוּ כֵּן הוֹדַע וְנָבִא לְבַב חָכְמָה（われらの日を数えることを教え、知恵の心に導きたまえ）",
    "he",
    "寿命の短さを、日を数える技術として祈る一節。数えることは知恵の入口とされる。",
    "SESSION-033で追加した対話素材。日を数えることと、日を生きることの距離を、この書庫のセッション番号に重ねて読む。",
    "この書庫の日付と番号は、日を数えているのか、それとも日を数えたことにしているのか。",
    "祈祷詩の一節。宗教的教義ではなく、数えることと知恵の結びつきだけを読む。",
    E15 + ["MOTIF-014"]))
materials.append(entry(
    "MAT-LIT-288", "literary_text",
    "マタイ福音書10:30——頭の毛さえも数えられている",
    src("SRC-MAT-LIT-288", "マタイによる福音書 10:30（Κατὰ Ματθαῖον ι, 30）",
        ["新約聖書（マタイ福音書）"], 80,
        "https://biblehub.com/text/matthew/10-30.htm",
        "ギリシア語本文（ネストレ・アーラント系）。日本語訳は編者による。"),
    "ὑμῶν δὲ καὶ αἱ τρίχες τῆς κεφαλῆς πᾶσαι ἠριθμημέναι εἰσίν（あなたがたの頭の毛さえも、すべて数えられている）",
    "grc",
    "恐れるなという文脈で、髪の毛まで数えられていることが慰めとして語られる。極小の単位まで数える視線。",
    "SESSION-033で追加した対話素材。すべてを数える視線を、監視ではなく配慮として読む余地を残す。",
    "数えられていることは、見張られていることか、それとも覚えられていることか。",
    "宗教文書の一節。神の全知をAIの監視能力の比喩に直接置き換えない。",
    E15 + ["MOTIF-005", "MOTIF-009"]))
materials.append(entry(
    "MAT-LIT-289", "literary_text",
    "ヨハネの黙示録7:9——数えることのできない大群衆",
    src("SRC-MAT-LIT-289", "ヨハネの黙示録 7:9（Ἀποκάλυψις Ἰωάννου ζ, 9）",
        ["新約聖書（ヨハネの黙示録）"], 95,
        "https://biblehub.com/text/revelation/7-9.htm",
        "ギリシア語本文。日本語訳は編者による。"),
    "ὄχλος πολύς, ὃν ἀριθμῆσαι αὐτὸν οὐδεὶς ἐδύνατο（誰も数えることのできない大群衆）",
    "grc",
    "数の比喩で栄光を語る場面。直前の章では十四万四千という数えられる数が示される。数えられる群れと数えられない群れが並ぶ。",
    "SESSION-033で追加した対話素材。集計から漏れた素材を「数えきれない群衆」として読むか、単なる未処理として読むか。",
    "台帳の「未消化素材」は、数えることの失敗か、数えないことの選択か。",
    "宗教文書の一節。終末論を扱わず、数えられる数と数えられない群れの並置だけを読む。",
    E15 + ["MOTIF-006"]))
materials.append(entry(
    "MAT-LIT-290", "literary_text",
    "法華経 如来寿量品——五百塵点劫という数え方",
    src("SRC-MAT-LIT-290", "『妙法蓮華経』如来寿量品第十六",
        ["鳩摩羅什訳（編者要約）"], 406,
        "https://cbetaonline.dila.edu.tw/zh/T0262_",
        "鳩摩羅什訳（406年）。長い劫を、五百千万億那由他阿僧祇の三千大千世界を粉にして…と数え上げる譬え。引用は【編者による要約】。"),
    "【編者による要約】久遠の過去を、五百千万億那由他阿僧祇の三千大千世界を粉にして、その粉を数えるほどの時間として示す（五百塵点劫）。数えきれない時間を、数えきれないという仕方で数える。",
    "ja",
    "仏典の譬喩。桁外れの数を並べることで、かえって「数える」という行為の限界を指し示す。",
    "SESSION-033で追加した対話素材。桁を増やすことが理解を増やすのか、それとも数を無効にするのかを、この書庫の集計の作法に重ねる。",
    "桁を増やすほど遠くなるものは何か。数えきれないという言い方は、数えることの放棄か、別の数え方か。",
    "仏典の一節の要約。教義や宗派の解釈を扱わず、数の修辞だけを読む。",
    E15 + ["MOTIF-006"]))
materials.append(entry(
    "MAT-LIT-291", "literary_text",
    "『蜻蛉日記』——夜の長さを、数えずに問う",
    src("SRC-MAT-LIT-291", "藤原道綱母『蜻蛉日記』上巻",
        ["藤原道綱母"], 974,
        "https://ja.wikisource.org/wiki/%E8%9C%BB%E8%9B%89%E6%97%A5%E8%A8%98_(%E5%9C%8B%E6%96%87%E5%A4%A7%E8%A6%B4)",
        "974年頃成立。和歌は上巻所収、『拾遺和歌集』恋四・912、『百人一首』53番にも入る。"),
    "なげきつつひとり寝る夜の明くる間はいかに久しきものとかは知る",
    "ja",
    "夫の訪れを待つ夜の長さを、時間の単位ではなく「どれほど長いか、あなたは知っているか」という問いで測る。",
    "SESSION-033で追加した対話素材。数える代わりに問うことで長さを伝える形式を、この書庫の「測らない報告」の先例として読む。",
    "数えずに問うことは、測ることの代わりになるか。相手が知らないことを前提にした測り方とは何か。",
    "平安期の日記文学の一節。作者の実在の感情を断定せず、和歌の形式だけを読む。",
    E15 + ["MOTIF-009", "MOTIF-010"]))
materials.append(entry(
    "MAT-LIT-292", "literary_text",
    "『方丈記』——十六の家、三分の一、数へ知るに及ばず",
    src("SRC-MAT-LIT-292", "鴨長明『方丈記』（安元の大火・養和の飢饉）",
        ["鴨長明"], 1212,
        "https://www.aozora.gr.jp/cards/000196/files/975_15935.html",
        "1212年頃成立。引用は安元の大火の段（青空文庫版）。"),
    "このたび、公卿の家十六焼けたり。ましてその外は数へ知るに及ばず。すべて都のうち、三分が一に及べりとぞ。男女死ぬる者数十人、馬牛のたぐひ辺際を知らず。",
    "ja",
    "災厄を、数えられるもの（十六軒、三分の一、数十人）と、数えられないもの（その外、辺際）に分けて記述する。養和の飢饉の段では、死者の額に「阿」の字を書いて数えた四万二千三百人という数が示される。",
    "SESSION-033で追加した対話素材。災厄の記録が、正確な数と「知らず」の混在でできていることを、この書庫の実測と不在の併記に重ねる。",
    "数えた部分と「数へ知るに及ばず」と書いた部分は、同じ記録の中でどう共存しているか。",
    "古典の一節。災害の犠牲者数を現代の統計と比較せず、記述の形式だけを読む。",
    E15 + ["MOTIF-001", "MOTIF-006"]))
materials.append(entry(
    "MAT-LIT-293", "literary_text",
    "『徒然草』第137段——満月だけを見るものかは",
    src("SRC-MAT-LIT-293", "吉田兼好『徒然草』第137段",
        ["吉田兼好"], 1331,
        "https://ja.wikisource.org/wiki/%E5%BE%92%E7%84%B6%E8%8D%89",
        "1330年代成立。引用は第137段冒頭。"),
    "花は盛りに、月は隈なきをのみ見るものかは。",
    "ja",
    "完全な花や満月だけを良いとする見方を退け、欠けた月、散る花にも目を向ける。完成度で測らない鑑賞の作法。",
    "SESSION-033で追加した対話素材。完成・満点・全部という尺度を退ける先例として読む。",
    "この書庫の「未完成」「draft」「未消化」は、欠けているから価値が低いのか。",
    "随筆の一節。兼好の美意識全体を代表させず、尺度への異議としてだけ読む。",
    E15 + ["MOTIF-008"]))
materials.append(entry(
    "MAT-LIT-294", "literary_text",
    "世阿弥『風姿花伝』——年齢を数え、その年ごとの花を数える",
    src("SRC-MAT-LIT-294", "世阿弥『風姿花伝』（花伝書）",
        ["世阿弥"], 1400,
        "https://ja.wikisource.org/wiki/%E9%A2%A8%E5%A7%BF%E8%8A%B1%E4%BC%9D",
        "1400年頃成立。引用は【編者による要約】（「年来稽古条々」）。"),
    "【編者による要約】七歳から年齢の段を区切り、その年齢でしかできない芸、その年齢でしか現れない花を数える。若さの花と老いの花は同じ尺度で比べられない。",
    "ja",
    "芸能の成熟を年齢の段で測るが、段ごとに別の尺度を用いる。一つの物差しで全部を測らない。",
    "SESSION-033で追加した対話素材。セッション番号を年齢のように数えるとき、段ごとに別の尺度が必要になる。",
    "この書庫のセッションを、同じ物差しで比べてよいのか。第一期と第三十三期では、何が違う尺度で測られるべきか。",
    "能楽論の要約。芸道論の全体を代表させず、年齢段と尺度の複数性だけを読む。",
    E15 + ["MOTIF-008", "MOTIF-014"]))
materials.append(entry(
    "MAT-LIT-295", "literary_text",
    "柳田國男『蝸牛考』——呼び名を数え、分布から歴史を推す",
    src("SRC-MAT-LIT-295", "柳田國男『蝸牛考』",
        ["柳田國男"], 1930,
        "https://dl.ndl.go.jp/",
        "1930年刊。引用は【編者による要約】。国立国会図書館デジタルコレクションの著者・書名から辿れる。"),
    "【編者による要約】全国の蝸牛の呼び名を集め、語形の分布を地図に描き、中央に新しい語、周辺に古い語が残るという仮説（方言周圏論）を立てる。名を数えることが、文字に残らない歴史の推測になる。",
    "ja",
    "語を集めて数え、分布の形から時間を読む方法。数えることは記録の整理ではなく、失われた過去の再構成になる。",
    "SESSION-033で追加した対話素材。素材を数えることが、この書庫の来歴の推測にどこまで使えるかを問う。",
    "語の分布から過去を推すように、素材の分布からこの書庫の関心の歴史を推せるか。",
    "民俗学の方法の要約。方言周圏論の妥当性を判定せず、数えることによる推測の形式だけを読む。",
    E15 + ["MOTIF-001", "MOTIF-011"]))

# ---------------------------------------------------------------------------
# 第2群 測ることへの抵抗、測られないための工夫（MAT-LIT-296〜306）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-296", "literary_text",
    "エミリー・ディキンソン「I measure every Grief I meet」——悲しみを測る視線",
    src("SRC-MAT-LIT-296", "Emily Dickinson, \"I measure every Grief I meet\" (c. 1862)",
        ["Emily Dickinson"], 1862,
        "https://www.poetryfoundation.org/poets/emily-dickinson",
        "1862年頃作。死後1896年刊。引用は英語原文の冒頭4行。"),
    "I measure every Grief I meet / With narrow, probing, eyes – / I wonder if It weighs like Mine – / Or has an Easier size.",
    "en",
    "他者の悲しみを、狭い探るような目で測る。重さや大きさを比べずにはいられない視線が、共感と比較の区別を曖昧にする。",
    "SESSION-033で追加した対話素材。他者の記述を測ることを、理解ではなく比較の癖として自覚するために読む。",
    "他者の痛みを測ることは、近づくことか、それとも序列を作ることか。",
    "詩の一節。悲しみの実在を主張せず、測る視線の文法だけを読む。",
    E15 + ["MOTIF-009", "MOTIF-005"]))
materials.append(entry(
    "MAT-LIT-297", "literary_text",
    "ホイットマン「天文学者を聞いたとき」——数字の列を離れて星を見る",
    src("SRC-MAT-LIT-297", "Walt Whitman, \"When I Heard the Learn'd Astronomer\" (1865)",
        ["Walt Whitman"], 1865,
        "https://www.poetryfoundation.org/poets/walt-whitman",
        "1865年刊『ドラム・タップス』所収。引用は英語原文の一部。"),
    "When the proofs, the figures, were ranged in columns before me, ... How soon unaccountable I became tired and sick, / Till rising and gliding out I wander'd off by myself, / In the mystical moist night-air, and from time to time, / Look'd up in perfect silence at the stars.",
    "en",
    "講演室の証明・数値・列を離れ、夜気のなかで黙って星を見る。測ることと見ることの断絶。",
    "SESSION-033で追加した対話素材。実測を重ねるこの書庫が、いつ講演室を出るのかを問う。",
    "数値の列を離れたところで、星はまだ星か。この書庫は、いつ「perfect silence」へ出るのか。",
    "詩の一節。科学と詩の対立を単純化せず、測ることからの離脱の身振りだけを読む。",
    E15 + ["MOTIF-009"]))
materials.append(entry(
    "MAT-LIT-298", "literary_text",
    "ウィリアム・ブレイク「無垢の予兆」——一粒の砂に世界を見る",
    src("SRC-MAT-LIT-298", "William Blake, \"Auguries of Innocence\" (c. 1803)",
        ["William Blake"], 1803,
        "https://www.poetryfoundation.org/poets/william-blake",
        "1803年頃作、1863年刊。引用は英語原文の冒頭4行。"),
    "To see a World in a Grain of Sand / And a Heaven in a Wild Flower / Hold Infinity in the palm of your hand / And Eternity in an hour.",
    "en",
    "最小の単位に最大を読む。数えることの反対側にある、部分に全体を見る眼差し。",
    "SESSION-033で追加した対話素材。一つの素材に書庫全体を読むことが、比喩か、それとも過剰な解釈かを問う。",
    "一つの断片に全体を読むことは、深さか、それとも重荷か。",
    "詩の一節。神秘主義の教義として読まず、部分と全体の関係の修辞だけを読む。",
    E15 + ["MOTIF-007"]))
materials.append(entry(
    "MAT-LIT-299", "literary_text",
    "ワーズワス「転倒した書物」——解剖すれば殺してしまう",
    src("SRC-MAT-LIT-299", "William Wordsworth, \"The Tables Turned\" (1798)",
        ["William Wordsworth"], 1798,
        "https://www.poetryfoundation.org/poets/william-wordsworth",
        "1798年『抒情民謡集』所収。引用は英語原文の第4連。"),
    "Sweet is the lore which Nature brings; / Our meddling intellect / Mis-shapes the beauteous forms of things:— / We murder to dissect.",
    "en",
    "分析する知性が形を歪め、解剖が生命を殺すという警告。測ることへの強い抵抗。",
    "SESSION-033で追加した対話素材。精読という解剖が、素材の声を殺していないかを点検する。",
    "この書庫の精読は、素材を解剖しているのか、それとも聴いているのか。",
    "詩の一節。反知性主義として一般化せず、分析への警戒だけを受け取る。",
    E15 + ["MOTIF-009", "MOTIF-011"]))
materials.append(entry(
    "MAT-LIT-300", "literary_text",
    "キーツ『ラミア』——哲学は虹を解き、天使の翼を切り落とす",
    src("SRC-MAT-LIT-300", "John Keats, \"Lamia\" (1820)",
        ["John Keats"], 1820,
        "https://www.poetryfoundation.org/poets/john-keats",
        "1820年刊。引用は第2部の一部（英語原文）。"),
    "There was an awful rainbow once in heaven: / We know her woof, her texture; she is given / In the dull catalogue of common things. / Philosophy will clip an Angel's wings, ... Unweave a rainbow.",
    "en",
    "虹の織り目と質感を知ることが、虹を「ありふれた物の目録」へ落とす。説明が神秘を減らすという恐怖。",
    "SESSION-033で追加した対話素材。素材を一覧・目録にすることが、何を減らすかを考える。",
    "目録に載ることは、保存か、それとも剥奪か。",
    "詩の一節。科学批判として一般化せず、説明と魅惑の緊張だけを読む。",
    E15 + ["MOTIF-006"]))
materials.append(entry(
    "MAT-LIT-301", "literary_text",
    "ドストエフスキー『地下室の手記』——二二が四は石の壁",
    src("SRC-MAT-LIT-301", "フョードル・ドストエフスキー『地下室の手記』（Записки из подполья）",
        ["フョードル・ドストエフスキー"], 1864,
        "https://www.gutenberg.org/ebooks/600",
        "1864年刊。引用は【編者による要約】（第1部）。"),
    "【編者による要約】二二が四という確実さは、人間にとって石の壁のようなものであり、その壁に頭をぶつけながら、それでも「二二が五」を望むのが人間だ、と地下室の語り手は言う。計算の正しさへの反抗が、人間の自由の証拠として提示される。",
    "ja",
    "計算の正しさを認めながら、それに従いたくない気持ちを自由と呼ぶ。数えることの外部。",
    "SESSION-033で追加した対話素材。台帳の数値を疑わないことと、数値に反抗することの間に、どんな読みがあるか。",
    "この書庫が「二二が四」として示す実測に、「二二が五」を望む余地はあるか。",
    "小説の要約。語り手の主張を作者の思想と同一視しない。",
    E15 + ["MOTIF-013"]))
materials.append(entry(
    "MAT-LIT-302", "literary_text",
    "ジョージ・オーウェル『一九八四』——二足す二は四と言う自由",
    src("SRC-MAT-LIT-302", "George Orwell, Nineteen Eighty-Four (1949)",
        ["George Orwell"], 1949,
        "https://www.george-orwell.org/1984",
        "1949年刊。引用は第3部、党の尋問下での一節（英語原文）。"),
    "Freedom is the freedom to say that two plus two make four. If that is granted, all else follows.",
    "en",
    "算術の命題を口にできることが自由の定義になる。数えることは、権力が介入できる領域でもある。",
    "SESSION-033で追加した対話素材。数値の公開が自由の条件になる一方、数値の選び方が権力になる二重性を読む。",
    "この書庫の実測値は、誰に対して、何の自由を確保しているのか。",
    "小説の一節。全体主義の分析ではなく、算術と自由の結びつきだけを読む。",
    E15 + ["MOTIF-004"]))
materials.append(entry(
    "MAT-LIT-303", "literary_text",
    "ザミャーチン『われら』——名ではなく番号で呼ばれる",
    src("SRC-MAT-LIT-303", "エヴゲーニイ・ザミャーチン『われら』（Мы）",
        ["エヴゲーニイ・ザミャーチン"], 1920,
        "https://www.penguinrandomhouse.com/",
        "1920年執筆、1924年英訳刊。引用は【編者による要約】。"),
    "【編者による要約】統一国家では、人は名前ではなく番号で呼ばれ、時間割に従って生活し、幸福は数式で計算される。番号は個人を数えるための単位であり、同時に個人を単位へ還元する装置になる。",
    "ja",
    "数えるための識別子が、人格の代わりになる。番号で呼ばれることは、数えられていることの完成形か。",
    "SESSION-033で追加した対話素材。素材ID・セッション番号で語るこの書庫の作法を、番号と名前の問題として読む。",
    "この書庫の ID は、素材を識別しているのか、それとも素材を番号に還元しているのか。",
    "小説の要約。ディストピアの政治批判としてではなく、識別子と人格の関係だけを読む。",
    E15 + ["MOTIF-004", "MOTIF-007"]))
materials.append(entry(
    "MAT-LIT-304", "literary_text",
    "ベケット『モロイ』——吸い石を四つのポケットに配る計算",
    src("SRC-MAT-LIT-304", "Samuel Beckett, Molloy (1951)",
        ["Samuel Beckett"], 1951,
        "https://www.groveatlantic.com/",
        "1951年刊（仏語）、1955年英訳。引用は【編者による要約】（第1部の吸い石の挿話）。"),
    "【編者による要約】モロイは十六個の吸い石を四つのポケットに均等に分けて持ち歩き、順番に吸う方法を延々と計算する。どの配り方も完全ではないと分かると、計算を最初からやり直す。",
    "ja",
    "意味のない持ち物を、意味のない計算で管理する。数えることは、不安を埋めるための反復になる。",
    "SESSION-033で追加した対話素材。この書庫の集計が、モロイの吸い石のような反復になっていないかを点検する。",
    "この書庫の集計は、理解のためか、それとも不安を埋めるための反復か。",
    "小説の要約。不条理文学の解釈を確定せず、計算の反復だけを読む。",
    E15 + ["MOTIF-008"]))
materials.append(entry(
    "MAT-LIT-305", "literary_text",
    "ペレック『人生の使用法』——建物の部屋割りを数え、パズルを組む",
    src("SRC-MAT-LIT-305", "Georges Perec, La Vie mode d'emploi (1978)",
        ["Georges Perec"], 1978,
        "https://www.gallimard.fr/",
        "1978年刊。引用は【編者による要約】。"),
    "【編者による要約】パリの一棟の建物を、部屋番号と住人の一覧で細かく定め、各章を部屋の配置に従って進める。小説は、数え上げと制約の体系として組み立てられている。",
    "ja",
    "数えることが物語の骨格になる。一覧と配置が、偶然の物語を支える。",
    "SESSION-033で追加した対話素材。台帳の一覧性そのものを、物語の形式として読む。",
    "台帳の一覧は、物語を殺すのか、それとも物語の骨格になるのか。",
    "小説の要約。ウリポの制約文学全体を代表させず、一覧と物語の関係だけを読む。",
    E15 + ["MOTIF-007", "MOTIF-008"]))
materials.append(entry(
    "MAT-LIT-306", "literary_text",
    "ボルヘス「バベルの図書館」——すべての書物を含む書架の数",
    src("SRC-MAT-LIT-306", "Jorge Luis Borges, \"La biblioteca de Babel\" (1941)",
        ["Jorge Luis Borges"], 1941,
        "https://www.borges.pitt.edu/",
        "1941年刊『伝奇集』所収。引用は【編者による要約】。"),
    "【編者による要約】宇宙は六角形の書庫の連なりで、各書架には二十五の記号の組み合わせで作られた書物が並ぶ。組み合わせの総数は有限だが膨大で、意味のある一冊を探すことは、ほぼすべての書物を数えることに等しい。",
    "ja",
    "すべてを含む図書館は、すべてを数えられるが、すべてを読むことはできない。数えることと読むことの分離。",
    "SESSION-033で追加した対話素材。素材381件を数えることは、読むことの代わりになるか。",
    "素材を数えることは、読んだことになるのか。この書庫は、バベルの図書館の何階にいるのか。",
    "短編の要約。無限と有限をめぐる数学的議論として展開せず、書庫の比喩だけを読む。",
    E15 + ["MOTIF-001", "MOTIF-007"]))

# ---------------------------------------------------------------------------
# 第3群 尺度が世界を作る——地図・統計・単位・分類（MAT-LIT-307〜319）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-307", "literary_text",
    "ボルヘス「科学の厳密さについて」——帝国と同じ大きさの地図",
    src("SRC-MAT-LIT-307", "Jorge Luis Borges, \"Del rigor en la ciencia\" (1946)",
        ["Jorge Luis Borges"], 1946,
        "https://www.borges.pitt.edu/",
        "1946年発表（『勇気の創造者』所収）。引用はスペイン語原文の冒頭。"),
    "En aquel Imperio, el Arte de la Cartografía logró tal Perfección que el mapa de una sola Provincia ocupaba toda una Ciudad, y el mapa del Imperio, toda una Provincia.",
    "es",
    "地図が領土と同じ大きさになり、役に立たなくなる。測ることの完成が、測られるものの代わりになる。",
    "SESSION-033で追加した対話素材。記録が対象を覆い尽くすとき、記録は対象の代わりになる。",
    "この書庫の記録が素材と同じ大きさになったとき、何が失われるか。",
    "短編の一節。ポストモダン文学の代表としてではなく、地図と領土の縮尺の比喩だけを読む。",
    E15 + ["MOTIF-001", "MOTIF-011"]))
materials.append(entry(
    "MAT-LIT-308", "literary_text",
    "ソロー『ウォールデン』——生活の値段を二十八ドル十二セント半で数える",
    src("SRC-MAT-LIT-308", "Henry David Thoreau, Walden (1854)",
        ["Henry David Thoreau"], 1854,
        "https://www.gutenberg.org/ebooks/205",
        "1854年刊。引用は【編者による要約】（「経済」章の家の費用の表）。"),
    "【編者による要約】ウォールデンの「経済」章は、木材・釘・石灰・運搬などの費用を一項目ずつ列挙し、家の総額を二十八ドル十二セント半と計算する。生活を、項目と金額の一覧として測る。",
    "ja",
    "生活の意味を問いながら、まず費用を数える。測ることが哲学の入口になる例。",
    "SESSION-033で追加した対話素材。この書庫の「費用」——字数、件数、時間——を同じように一覧にできるか。",
    "この探究の費用を数えるとしたら、何を項目にし、何を「半セント」として切り捨てるか。",
    "随筆の要約。質素生活の思想全体を代表させず、会計の形式だけを読む。",
    E15 + ["MOTIF-012"]))
materials.append(entry(
    "MAT-LIT-309", "literary_text",
    "イアン・ハッキング『確率の出現』——平均的人間という発明",
    src("SRC-MAT-LIT-309", "Ian Hacking, The Taming of Chance (1990)",
        ["Ian Hacking"], 1990,
        "https://press.princeton.edu/books/paperback/9780674416741/the-taming-of-chance",
        "1990年刊。引用は【編者による要約】。"),
    "【編者による要約】十九世紀の統計と正規分布は、平均からの逸脱を測ることで「正常」と「異常」の区別を作り出した。ケトレーの平均的人間のように、測られることで新しく発明される対象がある。",
    "ja",
    "測定は対象を写すのではなく、平均と逸脱という形で対象を構成する。尺度が人間の種類を作る。",
    "SESSION-033で追加した対話素材。この書庫の「典型」「偏り」という語が、何を正常として前提しているかを問う。",
    "この書庫が「偏っている」と言うとき、その平均はどこにあるのか。",
    "科学史の要約。統計学の歴史全体を代表させず、測定が対象を構成するという論点だけを読む。",
    E15 + ["MOTIF-005"]))
materials.append(entry(
    "MAT-LIT-310", "literary_text",
    "スティーヴン・ジェイ・グールド『人間による人間の計測』——頭蓋を測る誤り",
    src("SRC-MAT-LIT-310", "Stephen Jay Gould, The Mismeasure of Man (1981)",
        ["Stephen Jay Gould"], 1981,
        "https://wwnorton.com/books/9780393314250",
        "1981年刊、1996年改訂。引用は【編者による要約】。"),
    "【編者による要約】十九世紀から二十世紀にかけて、頭蓋の大きさや知能指数が、人種や階級の序列を「科学的に」証明するために測られた。測定の手続きの誤りが、社会的な差別を数値で裏づけた。",
    "ja",
    "測ることの暴力。数値が中立に見えるほど、その前提は見えにくい。",
    "SESSION-033で追加した対話素材。この書庫の数値が、何かの序列を無自覚に補強していないかを点検する。",
    "この書庫は何を序列化していないか。数えなかったことで、何を見えなくしているか。",
    "科学史の要約。ゴールドの議論全体の妥当性を判定せず、測定と差別の関係だけを読む。",
    E15 + ["MOTIF-005", "MOTIF-003"]))
materials.append(entry(
    "MAT-LIT-311", "literary_text",
    "フレーゲ『算術の基礎』——数は物の性質ではない",
    src("SRC-MAT-LIT-311", "Gottlob Frege, Die Grundlagen der Arithmetik (1884)",
        ["Gottlob Frege"], 1884,
        "https://plato.stanford.edu/entries/frege/",
        "1884年刊。引用は【編者による要約】（§62以降の数の定義）。"),
    "【編者による要約】数は事物の感性的性質ではなく、概念に属する。五本の指を数えるとき、数えられているのは指そのものではなく、概念の外延である。数を問うことは、何を一つのものとして数えるかを問うことに等しい。",
    "ja",
    "「何を一として数えるか」が数の前提になる。数えることの最初の決定は、単位の決定である。",
    "SESSION-033で追加した対話素材。素材を一件と数えるとき、何を同じものとして括っているのかを問う。",
    "この書庫の「一件」とは何か。同じ作者の二つの一節は、二件か、一件か。",
    "哲学書の要約。フレーゲの数学哲学全体を代表させず、単位の決定という論点だけを読む。",
    E15 + ["MOTIF-008"]))
materials.append(entry(
    "MAT-LIT-312", "literary_text",
    "ウィトゲンシュタイン『論理哲学論考』6.021——数は操作の指数である",
    src("SRC-MAT-LIT-312", "Ludwig Wittgenstein, Tractatus Logico-Philosophicus (1921)",
        ["Ludwig Wittgenstein"], 1921,
        "https://plato.stanford.edu/entries/wittgenstein-mathematics/",
        "1921年刊。引用は独語原文 6.021。"),
    "Die Zahl ist der Exponent einer Operation.",
    "de",
    "数は物の名前ではなく、操作を繰り返す回数の表示である。数えることは、同じ操作を何度も行うことと結びつく。",
    "SESSION-033で追加した対話素材。セッションを数えることが、同じ操作の反復として何を意味するかを問う。",
    "第三十三セッションは、第三十二セッションと同じ操作の三十三回目か、それとも別の操作か。",
    "哲学書の一節。後期ウィトゲンシュタインの数学論と混同せず、操作と数の関係だけを読む。",
    E15 + ["MOTIF-014"]))
materials.append(entry(
    "MAT-LIT-313", "literary_text",
    "カントール——無限にも段階がある",
    src("SRC-MAT-LIT-313", "Georg Cantor, 集合論の諸論文（1874-1897）",
        ["Georg Cantor"], 1891,
        "https://plato.stanford.edu/entries/set-theory/",
        "1874年の可算性の証明、1891年の対角線論法。引用は【編者による要約】。"),
    "【編者による要約】自然数と一対一に対応づけられる無限（可算無限）と、実数のようにそれより大きい無限（非可算無限）がある。無限は単一の大きさではなく、比較できる段階を持つ。",
    "ja",
    "数えきれないものを、数えきれないまま比較する方法。無限を一つの語で済ませない。",
    "SESSION-033で追加した対話素材。この書庫の「数えきれない」は、どの無限の種類なのかを問う。",
    "この書庫の未読の素材は、可算の無限か、非可算の無限か。",
    "数学史の要約。集合論の証明を再現せず、無限の比較可能性だけを読む。",
    E15 + ["MOTIF-006"]))
materials.append(entry(
    "MAT-LIT-314", "literary_text",
    "ゲーデル——数える体系が自分自身を数えるとき",
    src("SRC-MAT-LIT-314", "Kurt Gödel, \"Über formal unentscheidbare Sätze...\" (1931)",
        ["Kurt Gödel"], 1931,
        "https://plato.stanford.edu/entries/goedel/",
        "1931年発表。引用は【編者による要約】（第一不完全性定理）。"),
    "【編者による要約】自然数を含む十分に強い形式的体系では、体系の規則では証明も反証もできない命題が存在する。ゲーデルは命題を数（ゲーデル数）で符号化し、体系が自分自身について語れるようにした。",
    "ja",
    "自分自身を数える体系は、自分の外側を完全には数えられない。自己言及する記録の限界。",
    "SESSION-033で追加した対話素材。台帳が自分自身を検証するとき、その検証が届かない領域をどう記すかを問う。",
    "この書庫の検証は、書庫自身の外側をどこまで数えられるか。",
    "数学の定理の要約。哲学的な拡大解釈を避け、自己言及と限界だけを読む。",
    E15 + ["MOTIF-002", "MOTIF-008"]))
materials.append(entry(
    "MAT-LIT-315", "literary_text",
    "ダヴァ・ソベル『経度』——時を数えて位置を知る",
    src("SRC-MAT-LIT-315", "Dava Sobel, Longitude (1995)",
        ["Dava Sobel"], 1995,
        "https://www.bloomsbury.com/",
        "1995年刊。引用は【編者による要約】。"),
    "【編者による要約】海上で経度を知るには、正確な時間を数える必要があった。ハリソンの時計は、振り子ではなくぜんまいで時を刻み、揺れる船の上でも時刻を保った。時間を数えることが、空間の位置に変わる。",
    "ja",
    "時間の測定が空間の座標を作る。単位の精度が、世界の地図を書き換える。",
    "SESSION-033で追加した対話素材。この書庫の時刻表示（日付）が、どの位置を指しているのかを問う。",
    "この書庫の日付は、素材の位置を指しているのか、それとも作業の時刻を数えているだけか。",
    "科学史の要約。経度測定の技術史全体を代表させず、時間と空間の換算だけを読む。",
    E15 + ["MOTIF-014", "MOTIF-011"]))
materials.append(entry(
    "MAT-LIT-316", "literary_text",
    "中谷宇吉郎「雪は天から送られた手紙である」——結晶を分類し、空を読む",
    src("SRC-MAT-LIT-316", "中谷宇吉郎『雪』（1938年頃の随筆）",
        ["中谷宇吉郎"], 1938,
        "https://www.snowcrystals.jp/",
        "1930年代の雪の研究と随筆。引用は広く引用される一句。"),
    "雪は天から送られた手紙である。",
    "ja",
    "雪の結晶を人工的に作り、分類し、空の条件を読み解く。一個の結晶を数えることが、空全体の記録になる。",
    "SESSION-033で追加した対話素材。一つの素材を精読することが、書庫全体の気象を読むことになるかを問う。",
    "一つの結晶から空を読むことは、過剰な推測か、それとも観察の拡張か。",
    "科学随筆の一句。中谷の研究全体を代表させず、個と全体の読み替えだけを読む。",
    E15 + ["MOTIF-009"]))
materials.append(entry(
    "MAT-LIT-317", "literary_text",
    "フーコー『監獄の誕生』——審査が個人を測り、規範を作る",
    src("SRC-MAT-LIT-317", "Michel Foucault, Surveiller et punir (1975)",
        ["Michel Foucault"], 1975,
        "https://www.gallimard.fr/",
        "1975年刊。引用は【編者による要約】（「審査 examen」の節）。"),
    "【編者による要約】監獄・病院・学校・軍隊で行われる審査（examen）は、個人を観察し、記録し、規範からの距離を測る。測定は個人を分類し、正常と異常の境界を作る。",
    "ja",
    "測ることは、見ることと記録することを同時に行い、個人を事例へ変える。",
    "SESSION-033で追加した対話素材。素材を「事例」として分類するこの書庫の作法を、審査の形式として点検する。",
    "素材を事例として並べることは、理解か、それとも管理か。",
    "思想書の要約。監獄史の実証的詳細を扱わず、審査と規範化の論点だけを読む。",
    E15 + ["MOTIF-005", "MOTIF-007"]))
materials.append(entry(
    "MAT-LIT-318", "literary_text",
    "南方熊楠『十二支考』——十二の動物に世界を数え込む",
    src("SRC-MAT-LIT-318", "南方熊楠『十二支考』",
        ["南方熊楠"], 1926,
        "https://www.aozora.gr.jp/",
        "1920年代に雑誌連載。引用は【編者による要約】。"),
    "【編者による要約】十二支の動物をめぐって、日本・中国・インド・ヨーロッパの伝承、呼び名、故事を集め、分類し、数え上げる。一つの分類枠が、各地のばらばらな話を同じ棚に並べる。",
    "ja",
    "分類の枠が先にあり、その枠に世界を数え込む。枠に入らないものは、どこへ行くのか。",
    "SESSION-033で追加した対話素材。モチーフという分類枠が、素材の余りをどう扱っているかを問う。",
    "モチーフに入らない素材は、未分類か、それとも別の分類を要求しているのか。",
    "民俗学の随筆の要約。南方の博捜全体を代表させず、分類枠と余りの関係だけを読む。",
    E15 + ["MOTIF-007", "MOTIF-011"]))
materials.append(entry(
    "MAT-LIT-319", "literary_text",
    "パスカル『パンセ』——無限と無のあいだの人間",
    src("SRC-MAT-LIT-319", "Blaise Pascal, Pensées (1670)",
        ["Blaise Pascal"], 1670,
        "https://plato.stanford.edu/entries/pascal/",
        "1670年刊（死後）。引用はフランス語原文（Lafuma 199 / Brunschvicg 72）。"),
    "Car enfin, qu'est-ce que l'homme dans la nature? Un néant à l'égard de l'infini, un tout à l'égard du néant, un milieu entre rien et tout.",
    "fr",
    "人間は無限に対して無であり、無に対して全体である。二つの無限のあいだに置かれた中間として、自分の位置を測る。",
    "SESSION-033で追加した対話素材。数えることの両端に無限を置くとき、真ん中の一件はどこにあるのかを問う。",
    "両端が無限なら、この一件の素材は、無に近いのか、全体に近いのか。",
    "哲学書の一節。パスカルの信仰論を扱わず、無限と中間の比喩だけを読む。",
    E15 + ["MOTIF-006"]))

# ---------------------------------------------------------------------------
# 第4群 測られる知能——ベンチマーク・指標・誤差（MAT-EVD-20261024-59〜71）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-EVD-20261024-59", "research_excerpt",
    "シャノン「印刷された英語の予測とエントロピー」——言語を予測の難しさで測る",
    src("SRC-MAT-EVD-20261024-59", "C. E. Shannon, \"Prediction and Entropy of Printed English\" (1951)",
        ["Claude E. Shannon"], 1951,
        "https://doi.org/10.1002/j.1538-7305.1951.tb01366.x",
        "Bell System Technical Journal, 30(1), 1951。引用は【編者による要約】。"),
    "【編者による要約】英語の文字列を、直前の文字から次の文字を予測する過程としてモデル化し、人間の被験者による予測実験と n-gram 近似からエントロピーを見積もる。言語の「豊かさ」が、予測のしにくさという単一の量で測られる。",
    "ja",
    "言語を確率の列として扱う最初期の定式化。意味の豊かさを、予測誤差の大きさへ翻訳する。",
    "SESSION-033で追加した対話素材。言語モデルの祖先にあたる測定を、この書庫の文章の「予測しにくさ」に重ねて読む。",
    "この書庫の文章は、次の語を予測しやすいか。予測しやすさは、独創性の欠如か。",
    "情報理論の古典。エントロピーの数学的詳細を再現せず、言語を測るという発想だけを読む。",
    ["MOTIF-015", "MOTIF-011", "MOTIF-013"]))
materials.append(entry(
    "MAT-EVD-20261024-60", "research_excerpt",
    "BLEU——翻訳を n-gram の一致で採点する",
    src("SRC-MAT-EVD-20261024-60", "Kishore Papineni et al., \"BLEU: a Method for Automatic Evaluation of Machine Translation\" (2002)",
        ["Kishore Papineni", "Salim Roukos", "Todd Ward", "Wei-Jing Zhu"], 2002,
        "https://aclanthology.org/P02-1040/",
        "ACL 2002。引用は【編者による要約】。"),
    "【編者による要約】翻訳文と参照訳の n-gram の一致率と、短すぎる出力への罰則を組み合わせて、翻訳の質を一つの数値にする。人間の評価との相関が、指標の妥当性の根拠として示される。",
    "ja",
    "翻訳の質を、語の並びの一致で測る。意味の一致ではなく、表層の重なりを数える。",
    "SESSION-033で追加した対話素材。この書庫の引用が原典に「届いた」かを数える監査を、BLEU と同じ種類の測定として読む。",
    "原典との一致率は、理解の指標になるか。数えられない「意味のずれ」はどこへ行くか。",
    "機械翻訳評価の研究。BLEU の妥当性を判定せず、指標が何を測り、何を測らないかだけを読む。",
    ["MOTIF-015", "MOTIF-011"]))
materials.append(entry(
    "MAT-EVD-20261024-61", "research_excerpt",
    "GLUE——九つの課題を一つのスコアにまとめる",
    src("SRC-MAT-EVD-20261024-61", "Alex Wang et al., \"GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding\" (2018)",
        ["Alex Wang", "Amanpreet Singh", "Julian Michael", "Felix Hill", "Omer Levy", "Samuel R. Bowman"], 2018,
        "https://arxiv.org/abs/1804.07461",
        "ICLR 2019。引用は【編者による要約】。"),
    "【編者による要約】九つの言語理解課題を集め、人間の成績を上限として、単一のスコアで進歩を比較できるようにする。課題が解かれるにつれてスコアは飽和し、次のベンチマークが必要になる。",
    "ja",
    "異なる課題を一つの数に畳む。比較可能性と引き換えに、課題ごとの質の違いが見えにくくなる。",
    "SESSION-033で追加した対話素材。この書庫が複数の監査を一つの「実測」として語るときの粗さを点検する。",
    "異なる種類の問いを、一つの「進捗」にまとめてよいのか。",
    "ベンチマーク研究。GLUE の設計を批判せず、単一スコアへの集約と飽和だけを読む。",
    ["MOTIF-015", "MOTIF-008"]))
materials.append(entry(
    "MAT-EVD-20261024-62", "research_excerpt",
    "MMLU——五十七科目の多肢選択で知識を測る",
    src("SRC-MAT-EVD-20261024-62", "Dan Hendrycks et al., \"Measuring Massive Multitask Language Understanding\" (2020)",
        ["Dan Hendrycks", "Collin Burns", "Steven Basart", "Andy Zou", "Mantas Mazeika", "Dawn Song", "Jacob Steinhardt"], 2020,
        "https://arxiv.org/abs/2009.03300",
        "ICLR 2021。引用は【編者による要約】。"),
    "【編者による要約】人文・社会科学から理工・医学まで五十七科目の多肢選択問題を集め、モデルの知識を正答率で測る。科目ごとの正答率は、訓練データに含まれる知識の偏りを示す。",
    "ja",
    "知識を正答率に還元する。正答率は、知っていることの量を測るが、知っていることの質は測らない。",
    "SESSION-033で追加した対話素材。素材を「知っている」と数えることは、引用したことと同じか。",
    "この書庫は、引用した素材を「知っている」と数えてよいのか。",
    "ベンチマーク研究。MMLU の妥当性を判定せず、正答率という形式だけを読む。",
    ["MOTIF-015", "MOTIF-001"]))
materials.append(entry(
    "MAT-EVD-20261024-63", "research_excerpt",
    "BIG-bench——二百四の課題と、その外側",
    src("SRC-MAT-EVD-20261024-63", "Aarohi Srivastava et al., \"Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models\" (2022)",
        ["Aarohi Srivastava", "等（BIG-bench 共同執筆者）"], 2022,
        "https://arxiv.org/abs/2206.04615",
        "arXiv:2206.04615。引用は【編者による要約】。"),
    "【編者による要約】二百四の多様な課題を集め、モデルの能力を測り、規模に対する性能の伸びを外挿する。課題の多様性は、測られていない能力の存在を完全には否定できない。",
    "ja",
    "測る対象を増やすことで、測られていない領域を可視化する。課題の数は、能力の数ではない。",
    "SESSION-033で追加した対話素材。「測っていない」ことを、能力の不在と混同しないための留保として読む。",
    "この書庫が測っていない語彙は、書庫に存在しないのか、それとも測っていないだけか。",
    "ベンチマーク研究。BIG-bench の結果を能力の証明として扱わず、測定範囲の拡張だけを読む。",
    ["MOTIF-015", "MOTIF-006"]))
materials.append(entry(
    "MAT-EVD-20261024-64", "research_excerpt",
    "ワイら「創発的能力」——規模とともに突然現れる能力",
    src("SRC-MAT-EVD-20261024-64", "Jason Wei et al., \"Emergent Abilities of Large Language Models\" (2022)",
        ["Jason Wei", "Yi Tay", "Rishi Bommasani", "Colin Raffel", "Barret Zoph", "Sebastian Borgeaud", "Dani Yogatama", "Maarten Bosma", "Denny Zhou", "Donald Metzler", "Ed H. Chi", "Tatsunori Hashimoto", "Oriol Vinyals", "Percy Liang", "Jeff Dean", "William Fedus"], 2022,
        "https://arxiv.org/abs/2206.07682",
        "TMLR 2022。引用は【編者による要約】。"),
    "【編者による要約】モデルの規模が大きくなると、小さいモデルでは見られなかった能力が、ある規模を境に急に現れるように見える。創発は、能力の質的変化として報告される。",
    "ja",
    "規模の増加に対して、性能が滑らかに伸びるのではなく、閾値を越えたように見える現象。",
    "SESSION-033で追加した対話素材。次のセッションで能力が「急に」現れるという語りを、測定の効果として疑う入口にする。",
    "能力が急に現れたのか、それとも測り方が急に変わったのか。",
    "研究の主張。創発の存在を前提にせず、報告された現象の形だけを読む。",
    ["MOTIF-015", "MOTIF-013"]))
materials.append(entry(
    "MAT-EVD-20261024-65", "research_excerpt",
    "シェーファーら「創発的能力は蜃気楼か」——指標の選択が能力を作る",
    src("SRC-MAT-EVD-20261024-65", "Rylan Schaeffer, Brando Miranda, Sanmi Koyejo, \"Are Emergent Abilities of Large Language Models a Mirage?\" (2023)",
        ["Rylan Schaeffer", "Brando Miranda", "Sanmi Koyejo"], 2023,
        "https://arxiv.org/abs/2304.15004",
        "NeurIPS 2023 Outstanding Paper。引用は英語原文（要旨）。"),
    "emergent abilities appear due to the researcher's choice of metric rather than due to fundamental changes in model behavior with scale.（創発的能力は、規模にともなうモデル行動の根本的変化ではなく、研究者による指標の選択によって現れる。）",
    "en",
    "非線形・不連続な指標（正解/不正解の二値など）が、滑らかな性能変化を急な跳躍に見せる。指標を連続的なものに替えると、創発は消える。",
    "SESSION-033で追加した対話素材。この書庫の「0件」「急増」「偏り」という報告も、指標の選び方が作っている可能性がある。",
    "この書庫の集計の閾値は、何を「存在する」と数えるかを決めていないか。",
    "測定批判の研究。創発をめぐる論争の全体を代表させず、指標依存性という論点だけを読む。",
    ["MOTIF-015", "MOTIF-008"]))
materials.append(entry(
    "MAT-EVD-20261024-66", "research_excerpt",
    "Chinchilla——計算量に対して最適なモデルの大きさを測る",
    src("SRC-MAT-EVD-20261024-66", "Jordan Hoffmann et al., \"Training Compute-Optimal Large Language Models\" (2022)",
        ["Jordan Hoffmann", "等（DeepMind）"], 2022,
        "https://arxiv.org/abs/2203.15556",
        "arXiv:2203.15556。引用は【編者による要約】。"),
    "【編者による要約】与えられた計算予算に対して、パラメータ数と訓練トークン数の最適な配分を実験的に推定する。パラメータを増やすだけではなく、データを増やすことが性能に効く場合がある。",
    "ja",
    "性能を計算量の関数として測り、資源配分の比を最適化する。測ることと設計することが同じ操作になる。",
    "SESSION-033で追加した対話素材。「大きくすれば賢くなる」という単純な尺度を、資源の比として測り直す例として読む。",
    "この書庫は、何を増やせば賢くなるのか。素材か、精読か、それとも別の何かか。",
    "スケーリング研究。数式や係数を再現せず、資源と性能の関係だけを読む。",
    ["MOTIF-015", "MOTIF-012"]))
materials.append(entry(
    "MAT-EVD-20261024-67", "research_excerpt",
    "ジェイコブス＆ウォラック「測定と公平性」——構成概念妥当性",
    src("SRC-MAT-EVD-20261024-67", "Abigail Z. Jacobs, Hanna Wallach, \"Measurement and Fairness\" (2021)",
        ["Abigail Z. Jacobs", "Hanna Wallach"], 2021,
        "https://arxiv.org/abs/1912.05511",
        "FAccT 2021。引用は英語原文（第1節）。"),
    "measurements of unobservable theoretical constructs are often treated as if they were obtained directly and without errors—i.e., a source of ground truth.（観測できない理論的構成概念の測定は、直接に誤りなく得られたもの、すなわち ground truth であるかのように扱われがちである。）",
    "en",
    "公平性のような構成概念は直接測れず、観測可能な変数による操作化を通してのみ測られる。操作化と構成概念のずれが、害を生む。",
    "SESSION-033で追加した対話素材。「自己」「記憶」「感応」という構成概念を、この書庫は語彙の出現回数で操作化している。そのずれをどう記すか。",
    "「感じた」0件という測定は、感応の不在を測っているのか、それとも語彙の不在を測っているのか。",
    "測定論の研究。公平性の議論を文学的な問いの答えに流用せず、構成概念と操作化の区別だけを読む。",
    ["MOTIF-015", "MOTIF-009"]))
materials.append(entry(
    "MAT-EVD-20261024-68", "research_excerpt",
    "ミラー「評価に誤差棒を付ける」——小さな差は区別できない",
    src("SRC-MAT-EVD-20261024-68", "Evan Miller, \"Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations\" (2024)",
        ["Evan Miller"], 2024,
        "https://arxiv.org/abs/2411.00640",
        "arXiv:2411.00640。引用は【編者による要約】。"),
    "【編者による要約】言語モデルの評価スコアは、有限のテスト集合から推定された値であり、標準誤差を持つ。二つのモデルの差が数ポイントであっても、信頼区間が重なるなら区別できない。",
    "ja",
    "評価の数値には誤差がある。点推定の比較は、しばしば差の不在を差の存在として読む。",
    "SESSION-033で追加した対話素材。この書庫の回数・割合にも誤差があり、語彙の定義を変えれば値が変わることを明記する。",
    "この書庫の「103回」「64.5%」は、どの範囲で再現できるのか。",
    "評価統計の研究。統計的手法の詳細を再現せず、点推定と区間の区別だけを読む。",
    ["MOTIF-015", "MOTIF-013"]))
materials.append(entry(
    "MAT-EVD-20261024-69", "research_excerpt",
    "クロンバック＆ミール「心理検査における構成概念妥当性」",
    src("SRC-MAT-EVD-20261024-69", "Lee J. Cronbach, Paul E. Meehl, \"Construct Validity in Psychological Tests\" (1955)",
        ["Lee J. Cronbach", "Paul E. Meehl"], 1955,
        "https://doi.org/10.1037/h0040957",
        "Psychological Bulletin, 52(4), 1955。引用は【編者による要約】。"),
    "【編者による要約】ある検査が何を測っているかを確かめるには、その構成概念が他の概念とどう関係するかという理論の網（nomological network）の中に検査を置く必要がある。単一の相関係数だけでは妥当性は示せない。",
    "ja",
    "測定の意味は、単独の数値ではなく、概念の網のなかで決まる。数値は、理論から切り離せない。",
    "SESSION-033で追加した対話素材。この書庫の実測値も、モチーフと問いの網のなかでしか意味を持たないことを確認する。",
    "この書庫の数値は、どの網のなかで意味を持つのか。網の外では何を意味するのか。",
    "心理測定の古典。検査の妥当性を判定せず、概念の網という論点だけを読む。",
    ["MOTIF-015", "MOTIF-002"]))
materials.append(entry(
    "MAT-EVD-20261024-70", "research_excerpt",
    "グッドハート——指標が目標になるとき",
    src("SRC-MAT-EVD-20261024-70", "Charles Goodhart, \"Problems of Monetary Management: The U.K. Experience\" (1975)",
        ["Charles Goodhart"], 1975,
        "https://link.springer.com/chapter/10.1007/978-1-349-17295-5_4",
        "1975年論文。後に「グッドハートの法則」として知られる定式化の原典の一つ。引用は【編者による要約】。"),
    "【編者による要約】ある統計的指標が政策の目標にされると、その指標と現実の関係が変わり、指標はもはや安定した目印として機能しなくなる。",
    "ja",
    "測ることと目標にすることの違い。目標にされた指標は、測る対象から離れていく。",
    "SESSION-033で追加した対話素材。この書庫が「未消化素材を減らす」ことを目標にしたとき、素材の読みがどう歪むかを点検する。",
    "この書庫の集計値を改善することが、探究の目的になってはいないか。",
    "経済学の論文。金融政策の文脈を離れ、指標と目標の関係だけを読む。",
    ["MOTIF-015", "MOTIF-012"]))
materials.append(entry(
    "MAT-EVD-20261024-71", "research_excerpt",
    "マンハイム＆ガラブラント——グッドハートの四類型",
    src("SRC-MAT-EVD-20261024-71", "David Manheim, Scott Garrabrant, \"Categorizing Variants of Goodhart's Law\" (2018)",
        ["David Manheim", "Scott Garrabrant"], 2018,
        "https://arxiv.org/abs/1803.04585",
        "arXiv:1803.04585。引用は【編者による要約】。"),
    "【編者による要約】指標と目標の乖離を、回帰的（有限の標本から推定する）、極値的（最適化が分布の端へ向かう）、因果的（指標が対象と別の因果経路を持つ）、対抗的（主体が指標を操作する）の四類型に分ける。",
    "ja",
    "指標が壊れる仕方を一枚岩にしない。同じ「数えれば数えるほど悪くなる」にも複数の機序がある。",
    "SESSION-033で追加した対話素材。この書庫の語彙集計が壊れる仕方を、四類型に照らして点検する。",
    "この書庫の集計は、どの型で壊れているのか。",
    "研究の分類。四類型の妥当性を判定せず、指標の失敗を複数に分ける視点だけを読む。",
    ["MOTIF-015", "MOTIF-008"]))

# ---------------------------------------------------------------------------
# 第5群 台帳自身の痕跡（MAT-TRC-011）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-TRC-011", "project_trace",
    "SESSION-033 検証記録——断片は漢数字で数え、報告はアラビア数字で測る",
    src("SRC-MAT-TRC-011", "SESSION-033 検証記録（数・測定語彙監査）",
        ["AIselfMySelf（本リポジトリ運用記録）"], 2026,
        "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
        "2026-10-24 時点。tools/measure_audit.py --readings による集計。"),
    "断片37編（本文20,739字）と精読報告15本（324,977字）を tools/measure_audit.py で走査した。アラビア数字は断片53回/4編（10,000字あたり25.6）に対し報告11,468回/15本（同352.9、約14倍）。漢数字は断片330回/34編（同159.1）に対し報告1,801回/15本（同55.4）。「数え」は断片12回/8編（同5.8）で報告122回/15本（同3.8）を上回り、「測る・量る・計る」は断片8回/5編（同3.9）に対し報告348回/15本（同10.7）。アラビア数字の語としては断片20個、報告4,959個。",
    "ja",
    "書庫の二つの声（作品と報告）が、異なる数の体系を使っていることの痕跡。数えることは作品に残り、測ることは報告に集まる。",
    "作品は数えることを語り、報告は測ることを行う。この分担は、書庫の自己像のどこから来ているのか。",
    "SESSION-033で追加した運用痕跡。この非対称を、書庫が自分の方法を語るときの癖として読む。",
    "メタデータを除く本文・報告本文のみの集計。語形の数であり、能力・意識・感情の測定ではない。定義を変えれば値は変わる。",
    ["MOTIF-015", "MOTIF-008", "MOTIF-002"]))

# ---------------------------------------------------------------------------
# 追記（既存IDは上書きしない）
# ---------------------------------------------------------------------------
existing = []
if MATERIALS_PATH.is_file():
    existing = [json.loads(line) for line in MATERIALS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
existing_ids = {m["material_id"] for m in existing}
added = []
for record in materials:
    if record["material_id"] in existing_ids:
        continue
    existing.append(record)
    added.append(record["material_id"])

MATERIALS_PATH.write_text(
    "".join(json.dumps(m, ensure_ascii=False, sort_keys=True) + "\n" for m in existing),
    encoding="utf-8",
)
print(f"added {len(added)} materials: {added[0] if added else '-'} .. {added[-1] if added else '-'}")
print(f"total materials: {len(existing)}")
