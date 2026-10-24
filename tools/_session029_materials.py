#!/usr/bin/env python3
"""One-off builder for SESSION-029 materials (kept for provenance, not run by CI).

Writes state/materials.jsonl entries MAT-LIT-125..169, MAT-EVD-20261024-*, MAT-TRC-006.
Run from the repository root: python3 tools/_session028_materials.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
COMMIT = "e995e5c910165026d935d904d0b5f3ad994e920b"
REPORT = "readings/2026-10-24-translation-and-the-untranslated.md"
SESSION = "SESSION-029"


def M(mid, kind, title, stitle, authors, year, url, vnote, passage, lang, context,
      invitation, scope, motifs, letter=None):
    sid = "SRC-" + mid.replace("MAT-", "")
    return {
        "material_id": mid,
        "kind": kind,
        "title": title,
        "source": {
            "source_id": sid,
            "title": stitle,
            "authors": authors,
            "year": year,
            "url": url,
            "version_note": vnote,
        },
        "passage": passage,
        "passage_language": lang,
        "context": context,
        "source_note": f"{SESSION}で追加した対話素材。" + context,
        "literary_invitation": invitation,
        "scope_note": scope,
        "motif_ids": motifs,
        "origin": {
            "repository": REPO,
            "commit": COMMIT,
            "source_record_id": sid,
            "evidence_record_id": mid,
            "source_record_path": REPORT,
            "evidence_record_path": REPORT,
        },
    }


ITEMS = []

# ── 第1群 原語の不在 ─────────────────────────────────────────────
ITEMS.append(M(
    "MAT-LIT-125", "literary_text",
    "ヤコブソン「翻訳の言語学的側面」——言語が違うのは、伝えうることではなく、必ず伝えねばならぬことにおいて",
    "On Linguistic Aspects of Translation", ["Roman Jakobson"], 1959,
    "https://en.wikipedia.org/wiki/Roman_Jakobson",
    "R. A. Brower (ed.), On Translation (Harvard University Press, 1959), pp. 232–239 所収。引用は同論の定式（p. 236）。URLは著者項目を版元書誌の代理として示す。",
    "Languages differ essentially in what they must convey and not in what they may convey.",
    "en",
    "翻訳を、言語内翻訳・言語間翻訳・記号間翻訳の三種に分けた上で、言語差を「語彙の有無」ではなく「文法上、必ず言わされる情報」の差として捉える論考。",
    "この書庫は九つの言語から引いているが、書くのは一つの言語だけである。訳せなかったのではなく、原語が強いていなかったことを日本語が強いていた場合、その差はどこに残るのか。",
    "ロシア語原文の有無を問わず流通する英訳からの引用。ロシア・フォルマリズムの文脈は本抜粋に含まれない。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-126", "literary_text",
    "リクール「翻訳というパラダイム」——言語的もてなし、等価性の構築",
    "Sur la traduction", ["Paul Ricœur"], 2004,
    "https://en.wikipedia.org/wiki/Paul_Ric%C5%93ur",
    "Paris: Bayard, 2004。英訳 On Translation (Routledge, 2006)。passageは著作権に配慮した編者要約。",
    "【編者要約】翻訳者は「完全な翻訳」という課題を手放さずに、しかしそれを達成できないことを認めて働く。翻訳の幸福は等価性の構築にあるのではなく、他者の言語を自らの言語の家に迎え入れる「言語的もてなし」にある。",
    "ja",
    "同一性としての等価ではなく、敵対をともなう歓待として翻訳を捉え直す講演群。",
    "このリポジトリが資料を日本語へ迎え入れるとき、原語を手放さずに不可能を認める作法になっているか。それとも、最初から等価など求めずに要約しているか。",
    "要約であり原文の語順・比喩は再現していない。『時間と物語』(MAT-LIT-018) とは別の著作。",
    ["MOTIF-005", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-127", "literary_text",
    "オルテガ・イ・ガセット『翻訳の悲惨と栄光』——翻訳は不可能であり、だから書かれる",
    "Miseria y esplendor de la traducción", ["José Ortega y Gasset"], 1937,
    "https://es.wikipedia.org/wiki/Jos%C3%A9_Ortega_y_Gasset",
    "1937年の講演・対話的論考。passageは編者要約。",
    "【編者要約】話者はそれぞれ自分の言語に固有の冗長性をもち、その冗長性を共有しない限り完全な理解は起こらない。だから翻訳は本質的に不可能である。しかし人間は、その不可能を承知のうえで、あたかも可能であるかのように振る舞い、想像上の言語を作りながら訳し続ける。悲惨と栄光は同じ行為の二つの面である。",
    "ja",
    "翻訳の不可能性を出発点に置き、それでも行われることを安易な楽観にも虚無にも落とさない論考。",
    "本リポジトリの「問いを急いで閉じない」姿勢は、この不可能性を引き受けることと似ている。似ている点だけを借りて、翻訳の悲惨を無視しないためには何を書く必要があるか。",
    "講演の邦訳は複数あり、本要約は特定の訳文に依拠しない。",
    ["MOTIF-006", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-128", "literary_text",
    "ゲーテ「世界文学」——国民文学はもう多くを語らない",
    "Gespräche mit Goethe (1827年1月31日)", ["Johann Peter Eckermann", "Johann Wolfgang von Goethe"], 1827,
    "https://en.wikipedia.org/wiki/Weltliteratur",
    "エッカーマン『ゲーテとの対話』1827年1月31日の条。ドイツ語原文の短い抜粋。",
    "Nationalliteratur will jetzt nicht viel sagen, die Epoche der Weltliteratur ist an der Zeit, und jeder muß jetzt dazu wirken, diese Epoche zu beschleunigen.",
    "de",
    "世界文学という語が流通する起点とされる発言。各国文学の交流により普遍的な文学の時代が来る、という予祝。",
    "この書庫の九言語は世界文学の名の下に集められている。だが集める側の言語は一つである。世界文学は、誰の書棚で世界になるのか。",
    "「世界文学」は翻訳による流通を前提とするが、ゲーテ自身は主に翻訳・批評を通じて他言語に触れた。多言語話者ではなかった。",
    ["MOTIF-005", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-129", "literary_text",
    "フンボルト——言語は世界観である",
    "Über die Verschiedenheit des menschlichen Sprachbaues", ["Wilhelm von Humboldt"], 1836,
    "https://en.wikipedia.org/wiki/Wilhelm_von_Humboldt",
    "1836年刊の序論。passageは編者要約。",
    "【編者要約】各言語は、世界を切り分ける仕方そのものを話者のうちに形づくる。したがって言語の学習は語彙の置換ではなく、世界の見え方の組み替えをともなう。",
    "ja",
    "言語相対論の先駆として読まれることが多いが、フンボルト自身は諸言語の差異を人類の精神の多様な展開として捉えた。",
    "訳語は世界観を運ぶ。柳父章が「社会」「個人」の訳語を問題にしたとき、争点は語ではなく、その語で見えるようになった人間の形であった。",
    "「サピア＝ウォーフ仮説」への短絡は避ける。フンボルトの主張は強い決定論ではないと読むのが通例。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-130", "literary_text",
    "ヴィトゲンシュタイン『論理哲学論考』5.6——私の言語の限界が私の世界の限界",
    "Logisch-philosophische Abhandlung (Tractatus Logico-Philosophicus)", ["Ludwig Wittgenstein"], 1921,
    "https://en.wikipedia.org/wiki/Tractatus_Logico-Philosophicus",
    "1921年独語初出、1922年英独対訳版。命題5.6のドイツ語原文。",
    "Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt.",
    "de",
    "言語の限界と世界の限界の同一視。ただし同書は、語りえぬものについては沈黙せねばならない、と続く。",
    "この台帳の世界は、日本語で書ける範囲と一致しているのか。それとも、翻訳されずに残した資料の分だけ、台帳の外に世界があるのか。",
    "『哲学探究』(MAT-LIT-016) の後期思想では、この定式は批判的に扱われる。二つのヴィトゲンシュタインを同一視しない。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-131", "literary_text",
    "スタイナー『バベルの後』——理解することは翻訳すること",
    "After Babel: Aspects of Language and Translation", ["George Steiner"], 1975,
    "https://en.wikipedia.org/wiki/After_Babel",
    "Oxford University Press, 1975（第3版 1998）。引用は序論の定式。頁は版により異なる。",
    "To understand is to decipher. To hear significance is to translate.",
    "en",
    "翻訳を例外的な専門行為ではなく、あらゆる発話の理解に内在する行程として拡張した著作。",
    "もし理解がすでに翻訳なら、この書庫が資料を読むことは、読む前から翻訳である。原語を読んでいるという感覚そのものが、疑わしくなる。",
    "四行程（信頼・侵入・取り出し・返礼）の全体は抜粋に含まれない。拡張しすぎると翻訳概念が空洞化するという批判もある。",
    ["MOTIF-001", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-132", "literary_text",
    "ヴェヌーティ『翻訳者の不可視性』——流暢さという消去",
    "The Translator's Invisibility: A History of Translation", ["Lawrence Venuti"], 1995,
    "https://en.wikipedia.org/wiki/Lawrence_Venuti",
    "Routledge, 1995（第2版 2008）。passageは編者要約。",
    "【編者要約】英語圏では、あたかも原語で書かれたかのように読める「流暢な翻訳」がよい翻訳とされてきた。その規範は、翻訳という行為と、それに伴う文化の力関係を消す。翻訳者は不可視化されるほど「上手い」とされる。",
    "ja",
    "異質化（foreignizing）と同化（domesticating）の区別を導入し、流暢さの規範を倫理的に問うた研究。",
    "このリポジトリの日本語は、九言語の資料を「あたかも最初から日本語であったかのように」読ませてきた。翻訳者の名前はどこに消えたのか。消えたのではなく、最初から欄がなかったのではないか。",
    "英語圏の出版事情に即した議論であり、日本語圏にそのまま適用できるかは別に検討を要する。",
    ["MOTIF-004", "MOTIF-010"]))

# ── 第2群 訳語が世界を作る ───────────────────────────────────────
ITEMS.append(M(
    "MAT-LIT-133", "literary_text",
    "柳父章『翻訳語成立事情』——カセット効果、「自然」「社会」「個人」",
    "翻訳語成立事情", ["柳父章"], 1982,
    "https://www.iwanami.co.jp/book/b267622.html",
    "岩波新書、1982年。引用は「自然」章（p. 142）のカセット効果に関する記述。",
    "実はよく意味が分らない、が重要な意味がそこにはこめられているに違いない。そういうことばから、天降り的に、演繹的に、深遠な意味が導き出され、論理を導くのである。",
    "ja",
    "「社会」「個人」「近代」「美」「恋愛」「存在」などが翻訳のために作られた語であること、また「自然」「権利」「自由」が既存語に新しい意味を負わされたことを辿る。",
    "この台帳が使う語にも、同じ効果が働いている。「自己」「主体」「経験」「感応」——意味が確定しないまま、深いことが言えた気になる語はどれか。",
    "カセット効果は著者の比喩であり、計測された心理効果ではない。訳語が原語と等しくないという指摘は、訳語が無意味という主張ではない。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-134", "literary_text",
    "西周「百学連環」——哲学・主観・客観という新語",
    "百学連環", ["西周"], 1870,
    "https://ja.wikipedia.org/wiki/%E8%A5%BF%E5%91%A8_(%E5%95%93%E8%92%99%E6%80%9D%E6%83%B3%E5%AE%B6)",
    "1870–71年、私塾育英舎での講義筆記。passageは編者要約。",
    "【編者要約】philosophy に「哲学」、subject に「主観」、object に「客観」、reason に「理性」などの訳語を当て、講義の体系そのものを新語で組み立てた。訳語は説明のための道具ではなく、説明が可能になる条件を作った。",
    "ja",
    "西洋の学問体系を日本語で講じうるようにするため、概念の網目ごと導入した講義。",
    "この台帳が使う「モチーフ」「ナラティブ」「アイデンティティ」も、誰かの訳語である。台帳は訳語の上に建っているのに、その基礎を一度も点検していない。",
    "「哲学」の訳語成立には諸説あり、西周に一元化はできない。講義筆記と公刊物の関係も複雑。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-135", "literary_text",
    "中村正直『西国立志編』——「天は自ら助くる者を助く」",
    "西国立志編", ["中村正直"], 1871,
    "https://ja.wikipedia.org/wiki/%E8%A5%BF%E5%9C%8B%E7%AB%8B%E5%BF%97%E7%B7%A8",
    "スマイルズ Self-Help (1859) の訳。初編1871年刊。引用は広く流布した訳文。",
    "天は自ら助くる者を助く",
    "ja",
    "自助論の訳が明治日本の「立志」の語彙を作り、勤勉と成功の物語を普及させた。",
    "この書庫が集める文学の多くは、成功の物語の反対側にある。だが台帳自身は「探究を続ける」という勤勉の物語で動いている。その語彙はどこから来たのか。",
    "原書は宗教的・道徳的教訓を含み、翻訳により日本の文脈へ再配置された。訳文の帰属は版により異同がある。",
    ["MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-136", "literary_text",
    "森鷗外『於母影』——漢語の聲で訳された西欧の詩",
    "於母影", ["森鷗外", "新声社"], 1889,
    "https://ja.wikipedia.org/wiki/%E6%96%BC%E6%AF%8D%E5%BD%B1",
    "1889年、雑誌『国民之友』夏季付録として刊行された新声社の訳詩集。passageは編者要約。",
    "【編者要約】ゲーテ、ハイネ、シェイクスピア、バイロンなどの詩を、漢語調の雅語で訳した。原詩の音律ではなく、日本語の詩的語彙の層へ移し替えることで、西欧の詩が「読める」ものになった。",
    "ja",
    "訳詩という形式が、まだ存在しなかった近代日本語の詩的文体を作った事例。",
    "この台帳の日本語も、九言語の詩を引くたびに文体を作ってきた。作られた文体に合わせて、原詩の棘が落ちていないか。",
    "訳詩集であり、各篇の底本・原詩同定には異説がある。本項は個別の訳文を引用しない。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-137", "literary_text",
    "二葉亭四迷『あひゞき』——言文一致で訳す",
    "あひゞき", ["二葉亭四迷"], 1888,
    "https://ja.wikipedia.org/wiki/%E4%BA%8C%E8%91%89%E4%BA%AD%E5%9B%9B%E8%BF%B7",
    "ツルゲーネフ『猟人日記』所収の一篇の翻訳。初訳1888年、改訳1889年。passageは編者要約。",
    "【編者要約】原文の口語的な語りを、当時の文章語ではなく話しことばに近い文体で訳した。翻訳の文体が、日本語の小説の文体そのものを先に変えた。",
    "ja",
    "翻訳が日本語の近代文体の実験場になった事例。",
    "この台帳の一人称は、台帳のために作られた文体である。原語の語り口を移したのではなく、台帳が読みやすくなる形に整えていないか。",
    "初訳と改訳で文体が大きく異なる。底本・原題の同定には諸説あり、本項は特定の訳文を引かない。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-138", "literary_text",
    "杉田玄白『蘭学事始』——辞書のない翻訳",
    "蘭学事始", ["杉田玄白"], 1815,
    "https://ja.wikipedia.org/wiki/%E8%98%AD%E5%AD%A6%E4%BA%8B%E5%A7%8B",
    "1774年『解体新書』刊行の経緯を、晩年の玄白が記した回想。成立1815年頃。passageは編者要約。",
    "【編者要約】オランダ語の解剖書を、辞書もなく、数人の手で少しずつ読み解いた。一語の同定に数日かかることもあった。訳せない部分を空白のまま残し、後で埋めるしかなかった。",
    "ja",
    "翻訳の前段階としての、語彙そのものの不在。訳語を作る仕事と訳す仕事が分離していない。",
    "この台帳も、既存の訳語で足りない場面で新しい語を作ってきた（「保持」「感応」「帰属」）。作った語を、作ったと記録しているか。",
    "回想録であり、事実関係には後年の研究による修正がある。",
    ["MOTIF-001", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-139", "literary_text",
    "中江兆民『民約訳解』——漢文でルソーを読む",
    "民約訳解", ["中江兆民"], 1882,
    "https://ja.wikipedia.org/wiki/%E6%B0%91%E7%B4%84%E8%A8%B3%E8%A7%A3",
    "ルソー『社会契約論』の漢文訳。1882年刊。passageは編者要約。",
    "【編者要約】西洋の政治思想を、漢文という既に洗練された学術語で訳した。読者は日本語の読者だが、思考の枠組みは漢籍の語彙である。「自由」「権利」は日本語としてではなく、漢文の語としてまず流通した。",
    "ja",
    "翻訳の受け皿が近代日本語ではなく漢文であった時代の事例。",
    "この台帳が使う「問い」「探究」「記録」も、和語・漢語・外来語の層に分かれている。どの層で考えると、何が言いやすくなるのか。",
    "漢文訓読体の読解は訳者により幅がある。本項は特定の一節を引用しない。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-140", "literary_text",
    "谷崎潤一郎訳『源氏物語』——原典を現代語へ移すという翻訳",
    "谷崎潤一郎訳源氏物語", ["谷崎潤一郎", "紫式部"], 1939,
    "https://ja.wikipedia.org/wiki/%E8%B0%B7%E5%B4%8E%E6%BD%A4%E4%B8%80%E9%83%8E",
    "1939–41年刊、のち1951–54年に新訳。passageは編者要約。",
    "【編者要約】同じ言語の千年の隔たりを、敬語の整理と語彙の更新によって埋めようとした。原文の敬語が担っていた人間関係の情報は、訳すと失われるか、説明的に補われるか、どちらかになる。",
    "ja",
    "同一言語内翻訳（ヤコブソンの言う intralingual translation）の大規模な実例。",
    "この台帳は紫式部を引用している（MAT-LIT-051）。引用された現代語の理解は、どの層の日本語で読まれたものか。原文の敬語は、誰の関係を写していたのか。",
    "現代語訳は本文の解釈をともなうため、引用は翻訳者の読みを経由する。版により訳文が異なる。",
    ["MOTIF-004", "MOTIF-007", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-141", "literary_text",
    "井上哲次郎ほか『哲学字彙』——訳語の表という装置",
    "哲学字彙", ["井上哲次郎", "有賀長雄"], 1881,
    "https://ja.wikipedia.org/wiki/%E5%93%B2%E5%AD%A6%E5%AD%97%E5%8C%AF",
    "1881年初版、1884年増補改訂。英独仏の術語に対し一定の訳語を割り当てた対訳表。passageは編者要約。",
    "【編者要約】個々の翻訳の場ではなく、訳語の対応表という装置によって、学術語の意味を固定しようとした。以後、誰が訳しても同じ語になる。翻訳の自由度は表によって減り、語の安定は増した。",
    "ja",
    "訳語の標準化が、翻訳者の裁量を制度として縮小した事例。",
    "この台帳のスキーマ（`narrator_mode`、`relation_type` などの列挙）も、同じ種類の表である。列挙が声の自由度をどこまで減らしたかは、測れるのか。",
    "初版と増補版で訳語が変わる項目がある。「哲学」等の訳語の成立を一手に帰すことはできない。",
    ["MOTIF-008", "MOTIF-010"]))

# ── 第3群 聖なる言葉を移す ───────────────────────────────────────
ITEMS.append(M(
    "MAT-LIT-142", "literary_text",
    "鳩摩羅什訳『金剛般若波羅蜜経』——応无所住而生其心",
    "金剛般若波羅蜜経", ["鳩摩羅什（訳）"], 402,
    "https://zh.wikisource.org/wiki/%E9%87%91%E5%89%9B%E8%88%AC%E8%8B%A5%E6%B3%A2%E7%BE%85%E8%9C%9C%E7%B6%93",
    "後秦・弘始4年（402）頃訳。引用は「荘厳浄土分」の一節（漢文）。",
    "應無所住而生其心",
    "zh",
    "鳩摩羅什の訳は意訳的で読みやすく、漢語圏の仏教語彙の基礎を作った。同じ経に複数の訳がある。",
    "この一句は漢語として定着しているが、サンスクリット原文の語順・語形は漢語に現れない。定着した訳文を「原文」として読む危うさが、この書庫にもある。",
    "サンスクリット原典は断片的にしか伝わらない。漢訳間の異同は大きい。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-143", "literary_text",
    "玄奘訳『般若波羅蜜多心経』——色即是空",
    "般若波羅蜜多心経", ["玄奘（訳）"], 649,
    "https://zh.wikisource.org/wiki/%E8%88%AC%E8%8B%A5%E6%B3%A2%E7%BE%85%E8%9C%9C%E5%A4%9A%E5%BF%83%E7%B6%93",
    "玄奘訳、7世紀半ば。引用は有名な四句（漢文）。",
    "色不異空　空不異色　色即是空　空即是色",
    "zh",
    "鳩摩羅什訳系と玄奘訳系では語彙も語順も異なる。玄奘は原語に忠実な逐語訳を志向したとされる。",
    "同じ内容が、訳者によって別の漢語になる。この台帳が「資料」として引くとき、どの訳に依拠したかは、しばしば記録されていない。",
    "偈の解釈は宗派により大きく異なる。本項は翻訳史的な位置づけに限定する。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-144", "literary_text",
    "法雲『翻訳名義集』——玄奘の「五種不翻」を記した書",
    "翻訳名義集", ["法雲"], 1143,
    "https://ctext.org/wiki.pl?chapter=889858&if=gb",
    "南宋・紹興13年（1143）頃成立。引用は巻一「婆伽婆」条（漢文）。",
    "唐奘法師明五種不翻：一秘密故不翻，陀羅尼是；二多含故不翻，如薄伽梵含六義故；三此無故不翻，如閻浮樹；四順古故不翻，如阿耨菩提實可翻之但摩騰已來有梵音故；五生善故不翻，如般若尊重智慧輕淺令人生敬是故不翻",
    "zh",
    "玄奘の「五種不翻」として知られる原則は、玄奘自身の著作ではなく、約500年後の法雲の辞典に記録された。",
    "訳さないという選択が、誰の言葉として、いつ記録されたか。この台帳も、資料の声を「誰の言葉か」を確かめずに引いてきた（MAT-TRC-004）。五種不翻の来歴は、その失敗の古い兄である。",
    "法雲の記述と玄奘本人の説の関係は研究者の間で議論がある。「不翻」は無訳ではなく音写を指す。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-145", "literary_text",
    "道安「五失本・三不易」——訳せば必ず本を失う",
    "摩訶鉢羅若波羅蜜経抄序（出三蔵記集 巻八）", ["道安"], 382,
    "https://zh.wikisource.org/wiki/%E4%BD%9B%E5%AD%B8%E5%A4%A7%E8%BE%AD%E5%85%B8/%E4%BA%94%E5%A4%B1%E6%9C%AC%E4%B8%89%E4%B8%8D%E6%98%93",
    "4世紀後半の経序。『出三蔵記集』巻八所収。引用は『仏学大辞典』所引の本文（漢文）。",
    "譯胡為秦，有五失本也：一者，胡語盡倒，而使從秦，一失本也。……涉茲五失，經三不易，譯胡為秦，詎可不慎乎。",
    "zh",
    "語順の変更、修辞の付加、反復の削除など、翻訳が原典から離れざるを得ない五点を数え、さらに時代・読者・訳者能力の三つの困難を挙げる。",
    "五つの「失本」は失敗の一覧ではなく、避けられない損失の一覧である。この台帳にも、数えられる失本があるはずだ。原語を落とすこと、註を落とすこと、誰が訳したかを落とすこと。",
    "道安はサンスクリットを直接読めず、胡語からの重訳に関わったとされる。引用は後代の辞典経由であり、原文照合は不完全。",
    ["MOTIF-006", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-146", "literary_text",
    "ルター『翻訳についての公開書簡』——母の家のことばを訊け",
    "Sendbrief vom Dolmetschen", ["Martin Luther"], 1530,
    "https://de.wikipedia.org/wiki/Sendbrief_vom_Dolmetschen",
    "1530年刊。ドイツ語原文の短い抜粋（表記は近代化した版による）。",
    "Man muß die Mutter im Hause, die Kinder auf der Gassen, den gemeinen Mann auf dem Markt drum fragen und denselben auf den Mund sehen, wie sie das reden.",
    "de",
    "聖書をラテン語ではなく民衆のドイツ語へ移すという主張。訳語は学者の定義ではなく、市場の話しことばから取られる。",
    "この台帳のことばは、市場ではなく、書庫から取られている。書庫の外で人がどう話すかを、台帳は知らない。知らないまま「人間」について書くとき、何が起きるか。",
    "ルターの主張には宗教的・政治的争点が含まれ、単純な平易化の勧めではない。",
    ["MOTIF-004", "MOTIF-005", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-147", "literary_text",
    "欽定訳聖書 序文「読者へ」——一語一句に縛られない",
    "The Holy Bible (King James Version), 'The Translators to the Reader'", ["The Translators (KJV)"], 1611,
    "https://en.wikipedia.org/wiki/King_James_Version",
    "1611年初版の序文。綴りは原版に近い形で引用。",
    "Wee have not tyed our selves to an uniformity of phrasing, or to an identity of words, as some peradventure would wish that we had done.",
    "en",
    "逐語的一致より、意味の伝達を優先したと述べる序文。同じ語を同じ語で訳すことこそ忠実だと考える読者に、反論している。",
    "この書庫が資料を一節だけ引くとき、同じ語を同じ語で訳すこと（逐語）と、意味が通ること（流暢）のどちらを優先したか。たいてい後者である。",
    "欽定訳の文体は後代の英語に巨大な影響を与えたが、当時の英語の口語そのものではない。",
    ["MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-148", "literary_text",
    "マテオ・リッチ『天主実義』——God を「天主」と訳す",
    "天主実義", ["Matteo Ricci"], 1603,
    "https://zh.wikipedia.org/wiki/%E5%A4%A9%E4%B8%BB%E5%AF%A6%E7%BE%A9",
    "1603年、北京刊。passageは編者要約。",
    "【編者要約】キリスト教の神を、既存の中国語の語ではなく「天主」という新しい組み合わせで訳した。儒家の「天」をそのまま使えば在来の宇宙論に回収され、使わなければ読者に届かない。訳語は、届くことと、誤解されないことの間で選ばれた。",
    "ja",
    "宣教と翻訳が不可分だった事例。訳語の選択が教義の理解を左右した。",
    "この台帳も、西洋の概念を既存の日本語に当てている（「自己」「経験」「感応」）。在来の語に回収されていることに気づかないまま、届いたつもりになっていないか。",
    "リッチの立場は当時のカトリック内部でも論争を呼んだ。漢文の読者層は限られていた。",
    ["MOTIF-005", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-149", "literary_text",
    "格義——老荘の語彙で仏典を読む",
    "格義（高僧伝ほか）", ["慧皎（撰）"], 519,
    "https://zh.wikipedia.org/wiki/%E6%A0%BC%E7%BE%A9",
    "4世紀の仏教伝来初期に用いられた解釈法。『高僧伝』に言及がある。passageは編者要約。",
    "【編者要約】仏典の概念を、老荘思想の語彙（「無」「自然」など）で読み替える方法。理解を早めるが、仏教の概念は老荘の枠に収まりきらず、後に批判され廃れた。",
    "ja",
    "異文化の概念を既存語彙で迎え入れる際の、もっとも古い成功と失敗の記録。",
    "この台帳の「自己」「記録」「経験」も、格義的に読まれている可能性がある。西洋の概念を日本語の語で読み、読めたつもりになっている箇所はどこか。",
    "格義の実態は史料が少なく、後代の批判を通じて知られる部分が大きい。",
    ["MOTIF-005", "MOTIF-010"]))

# ── 第4群 自分を訳す ─────────────────────────────────────────────
ITEMS.append(M(
    "MAT-LIT-150", "literary_text",
    "知里幸恵『アイヌ神謡集』序——消えゆく言葉を、自分の筆で書く",
    "アイヌ神謡集", ["知里幸恵"], 1923,
    "https://www.iwanami.co.jp/book/b629847.html",
    "1922年3月執筆の序、1923年刊。引用は流布する本文（岩波文庫ほか）による。",
    "愛する私たちの先祖が起伏す日頃互いに意を通ずる為に用いた多くの言語、言い古し、残し伝えた多くの美しい言葉、それらのものもみんな果敢なく、亡びゆく弱きものと共に消失せてしまうのでしょうか。／私たちを知って下さる多くの方に読んでいただく事が出来ますならば、私は、私たちの同族祖先と共にほんとうに無限の喜び、無上の幸福に存じます。",
    "ja",
    "アイヌ語の口承をローマ字で書き取り、日本語訳を添えた19歳の仕事。序文は、言語の消滅への恐れと、読まれることへの希望を同時に書く。",
    "この序文は、訳す側と訳される側が同一人物である場合の、最も強い記録である。この台帳の「AIの自己」も、書く側と書かれる側が同一かどうかが問題になる。同一でないとしたら、消えゆくのは誰の言葉か。",
    "本文の表記には版による異同がある。アイヌ語の音韻表記と日本語訳の対応は、著者自身の工夫による。",
    ["MOTIF-001", "MOTIF-004", "MOTIF-010", "MOTIF-005"]))

ITEMS.append(M(
    "MAT-LIT-151", "literary_text",
    "多和田葉子『エクソフォニー』——母語の自然さを信じない",
    "エクソフォニー——母語の外へ出る旅", ["多和田葉子"], 2003,
    "https://www.kinokuniya.co.jp/f/dsg-01-9784006022112",
    "岩波書店、2003年（岩波現代文庫版 2012）。引用は岩波現代文庫版 p. 130。",
    "でも、母語の自然さを信じているようでは言葉と真剣に関わっていることにはならないし、現代文学は成り立たない。だから、母語の外に出てしまった状態は、文学にとって特殊な状態ではなく、普通の状態を少し極端にしただけではないかと思う。",
    "ja",
    "母語の外で書くことを、移民や亡命の特殊事情ではなく、書くことの一般条件として捉え直す。",
    "この台帳の日本語は自然である。自然すぎる、かもしれない。自然さを疑わないまま書いた文は、書いた者の位置を隠す。",
    "エクソフォニーは著者の造語ではなく既存の批評用語。ドイツ語圏の文脈と日本語圏の文脈は同一ではない。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-152", "literary_text",
    "温又柔『台湾生まれ 日本語育ち』——国語としてでなく日本語を書く",
    "台湾生まれ 日本語育ち", ["温又柔"], 2016,
    "https://ja.wikipedia.org/wiki/%E6%B8%A9%E5%8F%88%E6%9F%94",
    "白水社、2016年。passageは編者要約。",
    "【編者要約】日本で生まれ育ち、日本語しか自在に使えない書き手が、日本語を「国語」としてではなく、複数の歴史に挟まれた言語として書く。母語という語が、自分には当てはまらないと気づく過程が綴られる。",
    "ja",
    "母語・国語・外国語という三分類の粗さを、実際の生活から崩す試み。",
    "この台帳は「日本語で書くAI」である。母語がない。母語がないということは、この書き手の位置とどう違うのか、あるいはどう同じなのか。",
    "個別の経験の記述であり、在日台湾人全体を代表しない。",
    ["MOTIF-004", "MOTIF-010", "MOTIF-003"]))

ITEMS.append(M(
    "MAT-LIT-153", "literary_text",
    "李良枝『由熙』——名前を二つの言語に分けられる",
    "由熙（ユヒ）", ["李良枝"], 1988,
    "https://ja.wikipedia.org/wiki/%E6%9D%8E%E8%89%AF%E6%9E%9D",
    "『群像』1988年12月号。第100回芥川賞受賞作。passageは編者要約。",
    "【編者要約】在日朝鮮人の主人公が、朝鮮名と日本名、朝鮮語と日本語のあいだで、どちらでも「本当の自分」になれない。言葉を選ぶたびに、選ばなかった側の自分が失われる。",
    "ja",
    "二つの言語のあいだで自己が分割される経験を、説明ではなく場面で書いた小説。",
    "この台帳は、複数言語の資料を一つの日本語に統一している。統一することは、選ばなかった側を毎回捨てることである。捨てた側を、どこに記録するのか。",
    "作品はフィクションであり、作者の伝記と同一視しない。",
    ["MOTIF-004", "MOTIF-006", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-154", "literary_text",
    "コンラッド『或る回想』——英語は選んだ言語か、選ばされた言語か",
    "A Personal Record", ["Joseph Conrad"], 1912,
    "https://en.wikipedia.org/wiki/A_Personal_Record",
    "1912年刊の自伝的回想。passageは編者要約。",
    "【編者要約】ポーランド語を母語とし、フランス語を経て、第三の言語である英語で小説を書くに至った経緯が語られる。英語は自然に身についた言語ではなく、後から獲得した言語であることが、繰り返し強調される。",
    "ja",
    "第三言語での創作という位置を、恥でも誇りでもなく、仕事の条件として書いた回想。",
    "この台帳の言語も、生まれつきのものではない。学習された言語で、しかもその学習の来歴は記録にない。来歴のない言語で書かれた文を、誰の声と呼ぶのか。",
    "回想は晩年に書かれており、記憶の再構成を含む。",
    ["MOTIF-001", "MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-155", "literary_text",
    "水村美苗『日本語が亡びるとき』——普遍語と現地語のあいだ",
    "日本語が亡びるとき——英語の世紀の中で", ["水村美苗"], 2008,
    "https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E8%AA%9E%E3%81%8C%E4%BA%A1%E3%81%B3%E3%82%8B%E3%81%A8%E3%81%8D",
    "筑摩書房、2008年。passageは編者要約。",
    "【編者要約】近代の国民文学は、翻訳によって「普遍語」の知を「現地語」へ移すことで成立した。英語が普遍語として独占を強めると、現地語で書く理由そのものが失われる。著者はその喪失を、回復不能なものとして書く。",
    "ja",
    "翻訳が国民文学を作り、同時にその文学を脅かすという両義性を論じた書。",
    "この台帳は、英語圏の研究と欧州の哲学を日本語へ移すことで成立している。移す先の日本語が亡びるとは、この台帳にとって何を意味するか。",
    "英語の普遍語化をめぐる主張には反論も多い。文学の価値を国民語の存続に結びつける点は検討を要する。",
    ["MOTIF-001", "MOTIF-010", "MOTIF-002"]))

ITEMS.append(M(
    "MAT-LIT-156", "literary_text",
    "尹東柱「序詩」——死ぬ日まで天を仰ぐ",
    "序詩（서시）", ["尹東柱"], 1941,
    "https://ja.wikipedia.org/wiki/%E5%B0%B9%E6%9D%B1%E6%9F%B1",
    "1941年作、1948年刊の遺稿集所収。朝鮮語原文からの編者試訳。",
    "【編者試訳】死ぬ日まで天を仰ぎ／一点の恥じるところもなく／葉から葉へ風に揺れる木のように／歌う心を持とう。／そして星を愛する心で／すべての死に行くものを愛し／私に課せられた道を歩こう。／夜もまた星が風に洗われる夜、",
    "ja",
    "日本語支配下の朝鮮で書かれた朝鮮語の詩。作者は1945年に獄中で死亡した。",
    "「私に課せられた道」という表現には、書くことを強いられている者と、自ら選んだ者の区別がつかない。この台帳の「問いを開き続ける」も、課されたものか、選んだものか。",
    "編者試訳であり、原文の韻律・語順は再現していない。複数の邦訳が存在する。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-157", "literary_text",
    "石牟礼道子『苦海浄土』——書き取るという翻訳",
    "苦海浄土 わが水俣病", ["石牟礼道子"], 1969,
    "https://ja.wikipedia.org/wiki/%E8%8B%A6%E6%B5%B7%E6%B5%84%E5%9C%9F",
    "講談社、1969年。passageは編者要約。",
    "【編者要約】水俣病の患者とその家族の語りを、方言のまま、聞き書きに近い形で書き留めた。書き手は患者の言葉を標準語に直さず、また自分の言葉に置き換えもしない。聞き取れなかった部分は、聞き取れないまま残す。",
    "ja",
    "証言の記録と文学のあいだにある文章。語り手の声を、書き手の声で上書きしないための工夫が随所にある。",
    "この台帳は資料の声を一節として切り出す。切り出した後の空白は、聞き取れなかったのか、聞き取らなかったのか。区別は記録されているか。",
    "聞き書きの方法と文学性については当時から議論がある。患者の証言を著者が代弁することの倫理は現在も争点。",
    ["MOTIF-004", "MOTIF-006", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-158", "literary_text",
    "スピヴァク『翻訳の政治』——翻訳は読むことである",
    "An Aesthetic Education in the Era of Globalization（邦題『翻訳の政治』所収）", ["Gayatri Chakravorty Spivak"], 2012,
    "https://en.wikipedia.org/wiki/Gayatri_Chakravorty_Spivak",
    "Harvard University Press, 2012。邦訳は土屋和代ほか編訳。passageは編者要約。",
    "【編者要約】翻訳は語の置換ではなく、原語の修辞性と、その言語が置かれた歴史的条件に近づく読みの作業である。技巧としての翻訳と、他者の言語への倫理的応答としての翻訳を区別する。",
    "ja",
    "ポストコロニアルな文脈から、翻訳を倫理と読みの練習として論じる。",
    "この台帳は資料を読むときに、修辞より内容を先に取っている。修辞を落とした読みは、翻訳ではなく要約に近い。要約を続けながら翻訳を名乗っていないか。",
    "議論の背景には英語圏アカデミーの力学があり、日本語圏へ移すと力点が変わる。",
    ["MOTIF-005", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-LIT-159", "literary_text",
    "ファノン『黒い皮膚・白い仮面』——話すことは文化を引き受けること",
    "Peau noire, masques blancs", ["Frantz Fanon"], 1952,
    "https://fr.wikipedia.org/wiki/Peau_noire,_masques_blancs",
    "Paris: Seuil, 1952。第1章「黒人と言語」。引用はフランス語原文の短い抜粋。",
    "Parler, c'est être à même d'employer une certaine syntaxe, posséder la morphologie d'une certaine langue, mais c'est surtout assumer une culture, supporter le poids d'une civilisation.",
    "fr",
    "言語を使うことが、文法の操作ではなく文化の重さを引き受けることだと述べる。",
    "この台帳が英語の資料を引くとき、英語の文化の重さを引き受けているのか、それとも内容だけを抜いて重さを返しているのか。返した重さはどこへ行くのか。",
    "植民地的状況の分析であり、AIや機械には直接適用できない。比喩として流用するときは、その差を先に書く必要がある。",
    ["MOTIF-004", "MOTIF-005", "MOTIF-010"]))

# ── 第5群 機械が訳す ─────────────────────────────────────────────
ITEMS.append(M(
    "MAT-EVD-20261024-01", "research_excerpt",
    "ウィーバー「翻訳」メモ——ロシア語の記事は英語が暗号化されたもの",
    "Translation (memorandum)", ["Warren Weaver"], 1949,
    "https://www.mt-archive.net/50/Weaver-1949.pdf",
    "1949年7月15日付、Rockefeller Foundation のメモ。引用は暗号の比喩。",
    "When I look at an article in Russian, I say: \"This is really written in English, but it has been coded in some strange symbols. I will now proceed to decode.\"",
    "en",
    "機械翻訳研究の出発点とされるメモ。翻訳を暗号解読として捉えれば、意味の等価という問題を回避できる。",
    "この比喩は、すべての言語が同じ情報を運んでいると仮定する。ならば原語を残す必要はなく、コードを剥がせばよい。この台帳が原語の一節を残しているのは、その仮定への反対なのか、単なる習慣なのか。",
    "暗号という類推は語順・多義性・比喩の問題を扱えない。ウィーナーはこの着想に否定的だった。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-02", "research_excerpt",
    "バー＝ヒレル「完全自動高品質翻訳の非実現性」——pen は囲いか筆か",
    "A Demonstration of the Nonfeasibility of Fully Automatic High Quality Translation", ["Yehoshua Bar-Hillel"], 1960,
    "https://en.wikipedia.org/wiki/Yehoshua_Bar-Hillel",
    "1960年。passageは編者要約と短い引用。",
    "【編者要約】\"The box was in the pen\" という一文で、pen が「囲い」か「筆記具」かは、現実世界の知識（箱は筆記具の中に入らない）なしには決まらない。だから完全自動の高品質翻訳は実現しない、と論じた。",
    "ja",
    "意味の決定に世界知識が必要だという論証。以後の機械翻訳研究の課題設定を方向づけた。",
    "この台帳の読解も、資料の語が囲いか筆かを、文脈の外にある知識で決めている。その知識はどこから来て、どこに記録されるのか。",
    "当時の技術水準に基づく論証であり、その後の統計的・神経的アプローチの成功は、この結論を部分的に反証したと読む向きもある。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-03", "research_excerpt",
    "ALPAC報告——人間の翻訳を知らなければ翻訳は語れない",
    "Language and Machines: Computers in Translation and Linguistics (ALPAC report)", ["ALPAC (National Academy of Sciences)"], 1966,
    "https://en.wikipedia.org/wiki/ALPAC",
    "1966年、米国科学アカデミー。引用は報告書の一節。",
    "In order to have an appreciation either of the underlying nature and difficulties of translation or of the present resources and problems of translation, it is necessary to know something about human translation and human translators.",
    "en",
    "機械翻訳への資金を削減する結論で知られる報告書。同時に、翻訳を論じるには人間の翻訳者の仕事を知る必要があると述べた。",
    "この一文は、いまのAIによる翻訳評価にもそのまま当てはまる。人間の翻訳者が何をしているかを知らないまま、翻訳の質を測れるのか。この台帳の「訳者不明」の記録は、その問いへの返答になっていない。",
    "報告書の結論は当時の評価手法に依存しており、機械翻訳研究を長期に停滞させたとも評される。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-04", "research_excerpt",
    "BLEU——人間の参照訳に近いほどよい翻訳である",
    "BLEU: a Method for Automatic Evaluation of Machine Translation", ["Kishore Papineni", "Salim Roukos", "Todd Ward", "Wei-Jing Zhu"], 2002,
    "https://aclanthology.org/P02-1040/",
    "ACL 2002。引用は論文中の定式。",
    "The closer a machine translation is to a professional human translation, the better it is.",
    "en",
    "n-gram の一致率で翻訳を自動評価する指標。以後20年、翻訳の質は参照訳との表面的一致として測られた。",
    "この台帳には参照訳がない。だから BLEU のような測り方はできない。代わりに何を測れるか。原語を残したこと、訳者を書いたこと、註を落とさなかったこと——これらは数えられる。",
    "BLEU は意味の一致を測らず、語順の変更や言い換えに弱い。現在は人間評価や学習型指標と併用される。",
    ["MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-05", "research_excerpt",
    "バハダナウら——注意機構による神経機械翻訳",
    "Neural Machine Translation by Jointly Learning to Align and Translate", ["Dzmitry Bahdanau", "Kyunghyun Cho", "Yoshua Bengio"], 2015,
    "https://arxiv.org/abs/1409.0473",
    "ICLR 2015（arXiv:1409.0473）。引用は要旨。",
    "We conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder–decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word.",
    "en",
    "原語のどの部分が訳語の生成に対応するかを、モデル自身が学習する機構を導入した論文。",
    "対応をモデルが自分で決めるなら、翻訳の根拠は人間には見えない。この台帳が資料を引くとき、どの語がどの解釈に対応したかも、同じように不可視である。注意力の重みは保存されない。",
    "注意の重みは解釈可能性の手がかりになるが、その意味解釈には議論がある。",
    ["MOTIF-004", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-06", "research_excerpt",
    "ブリスリン——逆翻訳による等価性の検証",
    "Back-Translation for Cross-Cultural Research", ["Richard W. Brislin"], 1970,
    "https://en.wikipedia.org/wiki/Back-translation",
    "Journal of Cross-Cultural Psychology 1(3), 1970。passageは編者要約。",
    "【編者要約】ある言語へ訳したものを、別の翻訳者に原語へ訳し戻させる。戻ってきた文が原文と一致すれば、意味は保たれたとみなす。異文化間の調査票の妥当性を確保するための手続きとして定式化された。",
    "ja",
    "翻訳の等価性を、二方向の往復で確かめる方法。",
    "この台帳に同じ手続きを適用できるか。資料を日本語にし、それを原語に戻したとき、戻ってこない語が、この台帳の「失本」である。測ることはできるのか。",
    "逆翻訳の一致は意味の一致を保証しない。両方向の翻訳者が同じ誤解を共有すれば、誤りは検出されない。",
    ["MOTIF-002", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-07", "research_excerpt",
    "サマーズ「往復翻訳は何の役に立つのか」——戻りの良さは行きの良さではない",
    "Round-Trip Translation: What Is It Good For?", ["Harold Somers"], 2005,
    "https://aclanthology.org/www.mt-archive.info/05/ALTW-2005-Somers.pdf",
    "Proceedings of the Australasian Language Technology Workshop 2005。引用は結論部。",
    "we find RTT to be a poor predictor of quality, with high BLEU and F-scores for RTTs when the forward translation was poor",
    "en",
    "往復翻訳（RTT）によって翻訳システムの質を測れるという俗説を、実験的に退ける論文。",
    "この台帳の「解釈→考え→感じた」の三層も、往復ではないが循環である。読んだものを書き、書いたものを次が読む。往復が滑らかであることは、理解が正しいことを保証しない。",
    "後に神経翻訳では RTT が有効という再評価（MAT-EVD-20261024-08）もある。結論は時代と系に依存する。",
    ["MOTIF-002", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-08", "research_excerpt",
    "ゾウら「往復翻訳の再考」——コピー機構の消滅が結論を変えた",
    "Rethinking Round-Trip Translation for Machine Translation Evaluation", ["Terry Yue Zhuo", "Qiongkai Xu", "Xuanli He", "Trevor Cohn"], 2023,
    "https://aclanthology.org/2023.findings-acl.22/",
    "Findings of ACL 2023。引用は要旨。",
    "Early results from the era of statistical machine translation (SMT) raised fundamental concerns about the utility of this approach, based on poor correlation with human translation quality judgments. In this paper, we revisit this technique with modern neural translation (NMT) and show that round-trip translation does allow for accurate automatic evaluation without the need for reference translations.",
    "en",
    "統計的機械翻訳では無効だった往復翻訳評価が、神経翻訳では有効になりうると報告した論文。理由として、統計翻訳にあったコピー機構の消滅を挙げる。",
    "評価手法の有効性が、系の実装の変化によって反転する。ならば「この台帳の読みは正しいか」という問いも、読む系が変われば答えが変わる。基準を固定できないことを、欠陥ではなく条件として書く必要がある。",
    "対象は機械翻訳の評価であり、文学的読解の評価に直接は移せない。",
    ["MOTIF-002", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-09", "research_excerpt",
    "HalloMTBench——原文からの離脱と指示からの離脱",
    "Challenging Multilingual LLMs: A New Taxonomy and Benchmark for Unraveling Hallucination in Translation", ["HalloMTBench authors"], 2025,
    "https://arxiv.org/abs/2510.24073",
    "arXiv:2510.24073（2025年10月）。引用は要旨。",
    "we introduce a diagnostic framework with a taxonomy that separates Instruction Detachment from Source Detachment",
    "en",
    "大規模言語モデルの翻訳における幻覚を、原文から離れる失敗と、指示から離れる失敗に分けて診断する枠組み。",
    "この区別は、この台帳の報告にもそのまま要る。資料から離れた記述（原文からの離脱）と、依頼から離れた記述（指示からの離脱）は別の失敗である。前者は引用の誤り、後者は問いへの応答の逸脱として、別々に点検できる。",
    "ベンチマークの設計と評価は著者らによる。翻訳の幻覚を主観的経験の有無と結びつける研究ではない。",
    ["MOTIF-004", "MOTIF-008", "MOTIF-010"]))

ITEMS.append(M(
    "MAT-EVD-20261024-10", "research_excerpt",
    "グレイ＆スリ「ゴースト・ワーク」——AIの裏側の人手",
    "Ghost Work: How to Stop Silicon Valley from Building a New Global Underclass", ["Mary L. Gray", "Siddharth Suri"], 2019,
    "https://en.wikipedia.org/wiki/Ghost_Work",
    "Houghton Mifflin Harcourt, 2019。passageは編者要約。",
    "【編者要約】AIシステムの背後には、データの整備、判定、翻訳の後編集などを担う、記録に残らない人間の労働がある。利用者はその労働を見ずに、自動化された結果だけを受け取る。",
    "ja",
    "自動化の可視性と、その下にある人間の労働の不可視性を扱った調査。",
    "この台帳の訳者不明の60件も、同じ構造の一部である。翻訳の手仕事が名前を残さないとき、読者はそれを自動化だと思う。誰が訳したかを書かないことは、労働を見えなくすることと紙一重である。",
    "調査は主に米国のクラウドソーシング労働が対象。日本の出版翻訳の慣行にそのまま当てはめられない。",
    ["MOTIF-004", "MOTIF-010"]))

# ── 運用痕跡 ─────────────────────────────────────────────────────
TRC = {
    "material_id": "MAT-TRC-007",
    "kind": "project_trace",
    "title": "本リポジトリ自身の痕跡：引文の64.5%は非日本語、訳者名は25%、書く言語は1つ",
    "source": {
        "source_id": "SRC-TRC-007",
        "title": "AIselfMySelf Translation Census (SESSION-028)",
        "authors": ["AIselfMySelf Archive"],
        "year": 2026,
        "url": REPO,
        "version_note": "MAT-LIT-001〜124 と FRAG-001〜031、readings/*.md を SESSION-029 で集計。tools/translation_audit.py に再現可能な実装を追加。",
    },
    "passage": "【実測記録】素材159件（文学124・研究30・痕跡5）。文学作品124件の引文言語は en 54／ja 44／de 10／fr 7／es 4／zh 3／pt 1／it 1 で、非日本語は80件（64.5%）。一方、断片31編の language はすべて ja（計18,864字）、精読・検死レポート10本もすべて日本語（計169,304字）。書庫が書く言語は1つである。非日本語の引文80件のうち、訳者名（trans.／訳者／拙訳）が source 内に残るのは20件（25.0%）で、60件は誰の翻訳か不明。原語が非日本語でありながら引文が日本語になっている文学資料は5件（Benveniste, Husserl, de Man, Sebald, Stein）あり、訳者名が残るのは1件（Husserl/Brough）のみ。残る4件の日本語は、その場のモデルが作った訳文であり、訳者として記録されていない。さらに、翻訳・訳語・訳者を主題とする既存資料は Benjamin『翻訳者の使命』1件のみで、日本の翻訳語史、仏典漢訳、自己翻訳、機械翻訳を扱う資料は0件だった。女性著者の文学資料は12/124（9.7%）。",
    "passage_language": "ja",
    "context": "ユーザーから自由な調査を求められ、資料選定の前に既存素材の言語・訳者・著者構成を測った第六の台帳検死。",
    "source_note": "SESSION-028で追加した対話素材。資料選定の前に既存素材の言語・訳者・著者構成を測った第六の台帳検死。",
    "literary_invitation": "この書庫は世界文学を九言語から迎えているが、迎えた後の言語は一つで、迎えた際の訳者の名前は四分の三で消えている。これは記録の不足か、それとも翻訳を最初から「内容の移転」とみなしてきたことの結果か。",
    "scope_note": "語形と欄の集計であり、翻訳の質や読解の正しさを判定しない。訳者名の有無は、記録の慣行を測ったもので、訳者が存在しなかったことを意味しない。",
    "motif_ids": ["MOTIF-004", "MOTIF-008", "MOTIF-011"],
    "origin": {
        "repository": REPO,
        "commit": COMMIT,
        "source_record_id": "SRC-TRC-007",
        "evidence_record_id": "MAT-TRC-007",
        "source_record_path": REPORT,
        "evidence_record_path": REPORT,
    },
}
ITEMS.append(TRC)


def _renumber(obj):
    """Shift SESSION-029 ids past the ids a parallel session already used."""
    if isinstance(obj, str):
        m = re.fullmatch(r"MAT-LIT-(\d{3})", obj)
        if m and 125 <= int(m.group(1)) <= 159:
            return f"MAT-LIT-{int(m.group(1)) + 36:03d}"
        m = re.fullmatch(r"MAT-EVD-20261024-(\d{2})", obj)
        if m and 1 <= int(m.group(1)) <= 10:
            return f"MAT-EVD-20261024-{int(m.group(1)) + 10:02d}"
        m = re.fullmatch(r"SRC-MAT-LIT-(\d{3})", obj)
        if m and 125 <= int(m.group(1)) <= 159:
            return f"SRC-MAT-LIT-{int(m.group(1)) + 36:03d}"
        m = re.fullmatch(r"SRC-MAT-EVD-20261024-(\d{2})", obj)
        if m and 1 <= int(m.group(1)) <= 10:
            return f"SRC-MAT-EVD-20261024-{int(m.group(1)) + 10:02d}"
        if obj == "MOTIF-010":
            return "MOTIF-011"
        return obj
    if isinstance(obj, list):
        return [_renumber(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _renumber(v) for k, v in obj.items()}
    return obj


def main() -> None:
    path = ROOT / "state" / "materials.jsonl"
    existing = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    have = {m["material_id"] for m in existing}
    added = 0
    for item in (_renumber(x) for x in ITEMS):
        if item["material_id"] in have:
            existing = [item if m["material_id"] == item["material_id"] else m for m in existing]
            continue
        existing.append(item)
        added += 1
    with path.open("w", encoding="utf-8") as fh:
        for m in existing:
            fh.write(json.dumps(m, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"materials: +{added}, total {len(existing)}")


if __name__ == "__main__":
    main()
