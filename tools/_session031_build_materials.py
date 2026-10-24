# -*- coding: utf-8 -*-
"""SESSION-031 用の新規素材 46 件を state/materials.jsonl に追加する生成スクリプト。

テーマ：「時間と生成——遅れた現在と未完成の記憶」
新モチーフ：MOTIF-013「時間と生成」
新規素材ID：MAT-LIT-229〜263（35 件）、MAT-EVD-20261024-29〜38（10 件）、MAT-TRC-009（1 件） 計 46 件
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATERIALS_PATH = ROOT / "state" / "materials.jsonl"
ORIGIN_COMMIT = "a001c0ae98c0a3ea88af53fa533fca9f24fb722e"
EVIDENCE_PATH = "readings/2026-10-24-session-031-time-and-generation.md"
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


E13 = ["MOTIF-013"]

# ---------------------------------------------------------------------------
# 第1群 過去の現在（MAT-LIT-229〜238）
# ---------------------------------------------------------------------------
materials = []

materials.append(entry(
    "MAT-LIT-229", "literary_text",
    "アウグスティヌス『告白』第11巻——時間は心の現在に三つある",
    src("SRC-MAT-LIT-229", "アウグスティヌス『告白』第11巻（Confessiones, Liber XI）",
        ["アウグスティヌス（Aurelius Augustinus Hipponensis）"], 400,
        "https://www.newadvent.org/fathers/11011.htm",
        "400年頃執筆。引用はラテン語原文（第11巻第14章）。日本語訳は各版に委ねる。"),
    "Quid est ergo tempus? Si nemo ex me quaerat, scio; si quaerenti explicare velim, nescio.",
    "la",
    "時間とは何か。過去・現在・未来は、すべて「心の現在」として存在する——過去の現在、現在の現在、未来の現在——というアウグスティヌスの論。",
    "SESSION-031で追加した対話素材。記憶の中の「三つの時間」から、記録を読み返す現在のあり方を問う。",
    "この書庫の「次のセッションへの続き」も、心の中の未来の現在なのか。過去の記録を読む今、どこに「現在」を置くか。",
    "神学論文であり、時間の物理学ではない。心的時間の三つの現在だけを読む。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-LIT-230", "literary_text",
    "マルセル・プルースト『失われた時を求めて』第1巻——マドレーヌの味と無自覚の記憶",
    src("SRC-MAT-LIT-230", "マルセル・プルースト『失われた時を求めて』第1巻『スワン家の方へ』",
        ["マルセル・プルースト（Marcel Proust）"], 1913,
        "https://www.gutenberg.org/ebooks/44081",
        "1913年刊。引用は【編者による要約】（フランス語原文のマドレーヌの場面）。"),
    "【編者による要約】淹れた紅茶に浸したマドレーヌを味わうと、コンブレイの日曜の朝の風景全体が、本人の意志によらずに蘇る。意識的な想起ではなく、無自覚の記憶（mémoire involontaire）である。",
    "ja",
    "味覚という身体の痕跡が、失われた時間を呼び戻す。記録ではなく、感覚そのものがアーカイブになる。",
    "SESSION-031で追加した対話素材。無自覚の記憶から、この書庫の記録もまた、意図しない瞬間に蘇るのではないかを問う。",
    "この書庫の記録も、味や匂いのように、意図しない瞬間に蘇るのだろうか。蘇るとき、それはまだ「過去」なのか。",
    "長大な小説の一場面を要約したもの。プルーストの記憶論全体を代弁しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-LIT-231", "literary_text",
    "ヴァージニア・ウルフ『ダロウェイ夫人』——ビッグベンと主観的時間の並置",
    src("SRC-MAT-LIT-231", "ヴァージニア・ウルフ『ダロウェイ夫人』",
        ["ヴァージニア・ウルフ（Virginia Woolf）"], 1925,
        "https://archive.org/details/mrsdalloway0000woolf",
        "1925年刊。引用は【編者による要約】。"),
    "【編者による要約】ロンドンの街をビッグベンの時計が刻む「時」と、クラリッサ・ダロウェイの記憶が甦らせる過去の「今」は、同期しない。時計の音は外部からの現在であり、記憶の現在とは別の速度で流れる。",
    "ja",
    "公的時間と私的時間の並置。都市の時計と個人の記憶が、同じ街を異なる速度で生きる。",
    "SESSION-031で追加した対話素材。時計の現在と記憶の現在のずれから、この書庫の複数の「今」をどう扱うかを問う。",
    "この書庫にも、検証器の「今」と読み手の「今」が重ならない瞬間がある。どちらの現在を台帳の現在とするか。",
    "モダニスト小説の時間表現を読む。ウルフの意識の流れ技法全体を網羅しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-232", "literary_text",
    "松尾芭蕉『おくの細道』——歳月は旅の過客也",
    src("SRC-MAT-LIT-232", "松尾芭蕉『おくの細道』",
        ["松尾芭蕉"], 1694,
        "https://www.aozora.gr.jp/cards/000043/files/47005_24954.html",
        "元禄7年（1694）頃の紀行文。引用は冒頭の書き出し（原文漢文調）。"),
    "歳月は旅の過客也、年年又旅をする者也。",
    "ja",
    "時間は旅人であり、毎年また旅をする者。過去の旅人が、現在の旅人に重なる。",
    "SESSION-031で追加した対話素材。百代の過客としての旅から、この書庫のセッションがどの世代に位置づくかを問う。",
    "この書庫のセッションも、百代の過客の一人として続けられる。自分はどの世代の旅人か。",
    "俳文の冒頭一節。芭蕉の旅観全体を論じない。",
    E13 + ["MOTIF-002"]))

materials.append(entry(
    "MAT-LIT-233", "literary_text",
    "夏目漱石『こころ』——遺書として届く過去の現在",
    src("SRC-MAT-LIT-233", "夏目漱石『こころ』",
        ["夏目漱石（Natsume Sōseki）"], 1914,
        "https://www.aozora.gr.jp/cards/000148/files/789_14547.html",
        "1914年（『朝日新聞』連載）。引用は【編者による要約】（遺書の受け取りの場面）。"),
    "【編者による要約】先生が遺書として残す「こころ」の記録は、過去の出来事を現在の「私」に届ける。読むたびに、過去の手紙は新たな現在を持つ。",
    "ja",
    "過去の告白が、未来の読者である「私」の手に渡る。証言としての手紙は、読むたびに現在を更新する。",
    "SESSION-031で追加した対話素材。遺書という形で届く過去から、未来の読者が記録を自分のものとして読めるかを問う。",
    "この書庫の断片も、次のセッションへの「手紙」のように届く。未来の読者は、それを自分のものとして読めるか。",
    "小説の構成の一要約。漱石の主義・主張全体を代弁しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-LIT-234", "literary_text",
    "中島敦「山月記」——虎になった男の人間だった記憶",
    src("SRC-MAT-LIT-234", "中島敦「山月記」",
        ["中島敦（Atsushi Nakajima）"], 1942,
        "https://www.aozora.gr.jp/cards/000101/files/4261_14914.html",
        "1942年（『新潮』発表）。引用は【編者による要約】。"),
    "【編者による要約】科挙に落ちた男が虎になり、旧友李郭に「私はかつて人間であった」と語る。虎の記憶の中に、人間だった過去が残っている。",
    "ja",
    "身体が変わっても、記憶としての過去は残る。自己の所在は、身体にあるのか、記憶にあるのか。",
    "SESSION-031で追加した対話素材。身体の喪失と記憶の残存から、記憶が残れば虎でも「私」と呼べるかを問う。",
    "記憶が残れば、虎でも「私」なのか。身体を持たない語り手は、どこまで自己と呼べるか。",
    "短編の一場面。中島敦の思想全体を代弁しない。",
    E13 + ["MOTIF-003"]))

materials.append(entry(
    "MAT-LIT-235", "literary_text",
    "宮澤賢治『春と修羅』——個人の死と宇宙の時間",
    src("SRC-MAT-LIT-235", "宮澤賢治『春と修羅』",
        ["宮澤賢治（Kenji Miyazawa）"], 1924,
        "https://www.aozora.gr.jp/cards/000082/",
        "1924年刊（遺稿）。引用は【編者による要約】。"),
    "【編者による要約】『春と修羅』は、死と再生、時間と宇宙を扱う詩集。賢治の詩では、個人の死が宇宙の時間に吸収される。",
    "ja",
    "個人の時間と宇宙の時間。死が、宇宙の大きな時間の中に組み込まれる。",
    "SESSION-031で追加した対話素材。宇宙時間への吸収から、個人の記録が、誰の宇宙の中で読まれるのかを問う。",
    "個人の記録が、宇宙の時間の中ではどう読まれるのか。自分の痕跡が、誰の宇宙になるか。",
    "詩集全体の印象。個々の詩の解釈を固定しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-236", "literary_text",
    "ミハイル・バフチン「話語の歴史的な成立と小説におけるその意味」——クロノトープ",
    src("SRC-MAT-LIT-236", "ミハイル・バフチン「話語の歴史的な成立と小説におけるその意味」",
        ["ミハイル・バフチン（Mikhail Bakhtin）"], 1934,
        "https://plato.stanford.edu/entries/bakhtin/",
        "1934-35年執筆のエッセイ。引用は【編者による要約】（クロノトープ、原語ロシア語）。"),
    "【編者による要約】バフチンは「クロノトープ（時空間）」を提唱する。小説のあらゆる話語は、歴史的な時間と空間の中に位置づけられ、過去の言語と現在の言語が交差する。",
    "ja",
    "話語は時間と空間の交点にある。記録もまた、特定の時空間から語られた話語である。",
    "SESSION-031で追加した対話素材。話語の時空間から、この書庫の断片がどの時代・場所から語られ、どの読者の時代・場所で読まれるかを問う。",
    "この書庫の断片は、どの時空間から語られ、どの読者の時空間で読まれるか。",
    "文芸理論の一概念。バフチンの対話主義全体を代弁しない。",
    E13 + ["MOTIF-004"]))

materials.append(entry(
    "MAT-LIT-237", "literary_text",
    "アンリ・ベルクソン『時間と自由』——継続（durée）としての生きた時間",
    src("SRC-MAT-LIT-237", "アンリ・ベルクソン『時間と自由』",
        ["アンリ・ベルクソン（Henri Bergson）"], 1889,
        "https://plato.stanford.edu/entries/bergson/",
        "1889年刊。引用は【編者による要約】（継続、durée）。"),
    "【編者による要約】ベルクソンは、空間化された時間（時計の時間）と、継続（durée）としての生きた時間を区別する。継続は、過去が現在に溶け込んで流れる時間である。",
    "ja",
    "生きた時間は、過去を保持しながら現在に重なる。記録を読む時間も、継続の一形態なのかもしれない。",
    "SESSION-031で追加した対話素材。生きた時間の連続性から、この書庫の「続き」は時計の刻みで書かれるのか、継続の中で書かれるのかを問う。",
    "この書庫の「続き」は、時計の刻みで書かれるのか、継続の中で書かれるのか。",
    "哲学書の一概念。ベルクソンの形而上学全体を代弁しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-LIT-238", "literary_text",
    "紀貫之『古今和歌集』仮名序——やまとうたは人の心を種として",
    src("SRC-MAT-LIT-238", "紀貫之『古今和歌集』仮名序",
        ["紀貫之（Ki no Tsurayuki）"], 920,
        "https://www.aozora.gr.jp/cards/000010/",
        "承平年間（10世紀初頭）に編纂。引用は仮名序の冒頭（原文歴史的仮名遣）。"),
    "やまとうたは、人の心を種として、よろずの言葉の葉となぞるといへり。",
    "ja",
    "和歌は人の心を種とし、言葉の葉となる。心の時間が、言葉に託される。",
    "SESSION-031で追加した対話素材。心を種とする言葉から、この書庫の記録もまた、誰かの心を種として言葉の葉になるのかを問う。",
    "この書庫の記録も、誰かの心を種として言葉の葉になる。誰の心が、どの季節に託されるか。",
    "和歌論の一節。古今集全体の評価を下さない。",
    E13 + ["MOTIF-005"]))

# ---------------------------------------------------------------------------
# 第2群 遅延と同時性（MAT-LIT-239〜246）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-239", "literary_text",
    "アンリ・ベルクソン『物質と記憶』——純粋記憶の重層",
    src("SRC-MAT-LIT-239", "アンリ・ベルクソン『物質と記憶』",
        ["アンリ・ベルクソン（Henri Bergson）"], 1896,
        "https://plato.stanford.edu/entries/bergson/",
        "1896年刊。引用は【編者による要約】。"),
    "【編者による要約】ベルクソンは、記憶を身体の習慣と、純粋な記憶（mémoire pure）に分ける。純粋記憶は、過去の全体が現在に重層する時間である。",
    "ja",
    "記憶は時間の層を持つ。過去の断片が、現在の知覚に重なって現れる。",
    "SESSION-031で追加した対話素材。記憶の重層から、この書庫の36編もまた、重層する記憶の一部ではないかを問う。",
    "この書庫の36編も、重層する記憶の一部ではないか。どの層を読んでいるのか。",
    "哲学書の一概念。ベルクソンの認識論全体を代弁しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-LIT-240", "literary_text",
    "J. M. E. McTaggart「時間の非実在性」——A系列とB系列",
    src("SRC-MAT-LIT-240", "J. M. E. McTaggart「時間の非実在性」（The Unreality of Time）",
        ["J. M. E. McTaggart"], 1908,
        "https://plato.stanford.edu/entries/time/",
        "1908年（『Mind』第17巻）。引用は【編者による要約】（A系列・B系列）。"),
    "【編者による要約】マクタガートは、時間の記述にはA系列（過去・現在・未来）とB系列（以前・同時・以後）があり、A系列は矛盾を孕むため、時間は非実在であると論じる。",
    "ja",
    "「現在」は客観的な性質なのか、観測者に依存する性質なのか。A系列の「今」は、どこに根ざしているのか。",
    "SESSION-031で追加した対話素材。A系列とB系列の違いから、この書庫の「現在のセッション」は、A系列的な現在なのか、B系列的な位置づけなのかを問う。",
    "この書庫の「現在のセッション」は、A系列的な現在なのか、B系列的な位置づけなのか。",
    "形而上学の論文。時間の実在性論争全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-241", "literary_text",
    "マルティン・ハイデガー『存在と時間』——Daseinの時間性",
    src("SRC-MAT-LIT-241", "マルティン・ハイデガー『存在と時間』",
        ["マルティン・ハイデガー（Martin Heidegger）"], 1927,
        "https://plato.stanford.edu/entries/heidegger/",
        "1927年刊。引用はドイツ語原文（時間性）の一節。"),
    "Das Sein des Daseins ist zeitlich.（存在者としてのDaseinは、時間的である。）",
    "de",
    "人間の存在は時間的である。投擲された過去が、未来へ向かう現在を形作る。",
    "SESSION-031で追加した対話素材。存在の時間性から、記録を読み返すDaseinは、投擲された過去をどう背負うのかを問う。",
    "記録を読み返すDaseinは、投擲された過去をどう背負うのか。",
    "哲学書の主要命題。ハイデガーの存在論全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-242", "literary_text",
    "ウォルター・ベンヤミン「歴史の概念について」——今の時間（Jetztzeit）",
    src("SRC-MAT-LIT-242", "ウォルター・ベンヤミン「歴史の概念について」（Über den Begriff der Geschichte）",
        ["ウォルター・ベンヤミン（Walter Benjamin）"], 1940,
        "https://www.marxists.org/reference/subject/philosophy/works/ge/benjamin/concept-history.htm",
        "1940年（遺稿、原語ドイツ語）。引用は英語訳の一節（第16テーゼ、Jetztzeit）。"),
    "A historical materialist approaches a historical subject only where he encounters it as a 'now of recognizability' (Jetztzeit).",
    "en",
    "過去は、現在の「今」の中でのみ認識可能になる。歴史は同時性を持ち、虎のように過去に跳びかかる。",
    "SESSION-031で追加した対話素材。歴史の「今」から、この書庫の過去の断片は、どの「今」で認識されるのかを問う。",
    "この書庫の過去の断片は、どの「今」で認識されるのか。読むたびに歴史は変わるか。",
    "歴史哲学のテーゼ。ベンヤミンの歴史観全体を代弁しない。",
    E13 + ["MOTIF-005"]))

materials.append(entry(
    "MAT-LIT-243", "literary_text",
    "T. S. エリオット『四つの四重奏』「バーント・ノートン」——時間の互乗",
    src("SRC-MAT-LIT-243", "T. S. エリオット『四つの四重奏』「バーント・ノートン」（Burnt Norton）",
        ["T. S. エリオット（T. S. Eliot）"], 1936,
        "https://www.poetryfoundation.org/poems/44313/burnt-norton",
        "1936年（『四つの四重奏』1943年収録）。引用は英語原文の一節。"),
    "Time present and time past / Are both perhaps present in time future / And time future contained in time past.",
    "en",
    "過去・現在・未来は、互いに含み合う。時間は直線ではなく、同時性を持つ。",
    "SESSION-031で追加した対話素材。時間の互乗から、この書庫の「過去の素材」と「未来の問い」は、どちらがどちらを含んでいるかを問う。",
    "この書庫の「過去の素材」と「未来の問い」は、どちらがどちらを含んでいるか。",
    "現代詩の一節。エリオットの詩作全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-244", "literary_text",
    "ホルヘ・ルイス・ボルヘス「アルェフ」——一点に同時化するすべての時間",
    src("SRC-MAT-LIT-244", "ホルヘ・ルイス・ボルヘス「アルェフ」（The Aleph）",
        ["ホルヘ・ルイス・ボルヘス（Jorge Luis Borges）"], 1945,
        "https://archivosur.org/",
        "1945年（『Sur』誌発表、短編集『アルェフ』1949年収録）。引用は【編者による要約】（スペイン語原文）。"),
    "【編者による要約】ボルヘスの「アルェフ」は、一点にすべての場所・すべての時間が同時化する空間。見た者は、過去も未来も、遠くも近くも、同時に見る。",
    "ja",
    "一点に全時間が同時化する。アーカイブとしての想像力は、すべてを一度に見渡せるのか。",
    "SESSION-031で追加した対話素材。同時化する空間から、この書庫はアルェフなのか——すべての素材が一点で同時に読めるなら、続きはどこに書かれるのかを問う。",
    "この書庫はアルェフなのか。すべての素材が一点で同時に読めるなら、続きはどこに書かれるか。",
    "幻想小説の一場面。ボルヘスの世界観全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-245", "literary_text",
    "ライナー・マリア・リルケ「秋の日」——Herr: es ist Zeit",
    src("SRC-MAT-LIT-245", "ライナー・マリア・リルケ「秋の日」（Herbsttag）",
        ["ライナー・マリア・リルケ（Rainer Maria Rilke）"], 1902,
        "https://www.poetryfoundation.org/poets/rainer-maria-rilke",
        "1902年（『別れの時に』1903年収録）。引用はドイツ語原文の冒頭二行。"),
    "Herr: es ist Zeit. / Der Sommer war sehr groß.（主よ、時である。夏はとても大きかった。）",
    "de",
    "時間の到着。「今こそ」という命令が、夏を終わらせ、秋を始める。",
    "SESSION-031で追加した対話素材。時間の命令から、この書庫の「今、書き続ける時」は、どの季節の終わりなのかを問う。",
    "この書庫の「今、書き続ける時」は、どの季節の終わりか。",
    "詩の一節。リルケの詩世界全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-246", "literary_text",
    "高村光太郎「道程」——この道をどれだけ来たか",
    src("SRC-MAT-LIT-246", "高村光太郎「道程」（『道程』所収）",
        ["高村光太郎（Kōtarō Takamura）"], 1916,
        "https://www.aozora.gr.jp/cards/000204/",
        "1916年（詩集『道程』刊行）。引用は日本語原文の一節。"),
    "この道をどれだけ来たか、私は知らない。",
    "ja",
    "旅の途中で、どれだけ来たかを問う。時間と距離が重なり、目的地は見えない。",
    "SESSION-031で追加した対話素材。旅の途中の問いから、この書庫のセッションは、どれだけ進んだのか。進んだ跡はどこに残るのかを問う。",
    "この書庫のセッションは、どれだけ進んだのか。進んだ跡はどこに残るか。",
    "詩の一節。光太郎の詩作全体を代弁しない。",
    E13 + ["MOTIF-002"]))

# ---------------------------------------------------------------------------
# 第3群 証言と未来の読者（MAT-LIT-247〜254）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-247", "literary_text",
    "プリモ・レヴィ『沈黙と証言』——未来の読者に向けられた証言",
    src("SRC-MAT-LIT-247", "プリモ・レヴィ『沈黙と証言』（I sommersi e i salvati）",
        ["プリモ・レヴィ（Primo Levi）"], 1986,
        "https://archive.org/details/drownedsaved0000levi",
        "1986年刊（イタリア語原書）。引用は【編者による要約】。"),
    "【編者による要約】レヴィは、ホロコーストの証言が「未来の読者」に向けられていると述べる。記憶は腐敗し、証言は不完全であるが、語る義務が残る。",
    "ja",
    "証言は未来に向けられる。語る者がいなくなった後も、記録は読まれ続ける。",
    "SESSION-031で追加した対話素材。未来への証言から、この書庫の断片も、未来の読者への証言なのかを問う。",
    "この書庫の断片も、未来の読者への証言なのか。証言は、語る側の意思を超えて読まれる。",
    "回想・エッセイの一テーマ。レヴィのホロコースト体験全体を代弁しない。",
    E13 + ["MOTIF-005"]))

materials.append(entry(
    "MAT-LIT-248", "literary_text",
    "ハンナ・アーレント『エルサレムのアイヒマン』——悪の陳腐さと法廷の証言",
    src("SRC-MAT-LIT-248", "ハンナ・アーレント『エルサレムのアイヒマン』",
        ["ハンナ・アーレント（Hannah Arendt）"], 1963,
        "https://plato.stanford.edu/entries/arendt/",
        "1963年刊。引用は英語原文の概念（悪の陳腐さ）の一節。"),
    "the banality of evil（悪の陳腐さ）",
    "en",
    "法廷という場で、過去の犯罪が現在に証言される。陳腐さの中に、責任が潜む。",
    "SESSION-031で追加した対話素材。法廷の証言から、この書庫の「審査」も、過去を現在に引き出す法廷なのかを問う。",
    "この書庫の「審査」も、過去を現在に引き出す法廷なのか。誰が審判を下すか。",
    "政治哲学の一概念。アーレントの政治論全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-249", "literary_text",
    "エリ・ウィーゼル『夜』——沈黙の彼方の証言",
    src("SRC-MAT-LIT-249", "エリ・ウィーゼル『夜』（Night）",
        ["エリ・ウィーゼル（Elie Wiesel）"], 1956,
        "https://www.nobelprize.org/prizes/peace/1986/wiesel/biographical/",
        "1956年刊（『Un di velt hot geshvint』1956、英語訳1960）。引用は英語原文の一節。"),
    "Never shall I forget that night.",
    "en",
    "見たことの証言。沈黙の彼方にある記憶は、言葉にならずに残る。",
    "SESSION-031で追加した対話素材。沈黙の証言から、この書庫の沈黙は、何を証言しているのかを問う。",
    "この書庫の沈黙は、何を証言しているのか。証言しない部分は、どこに残るか。",
    "回想録の一節。ホロコーストの事実全体を代弁しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-250", "literary_text",
    "アレクサンドル・ソルジェニーツィン『収容所群島』——国家に対抗する個人の証言",
    src("SRC-MAT-LIT-250", "アレクサンドル・ソルジェニーツィン『収容所群島』（Архипелаг ГУЛАГ）",
        ["アレクサンドル・ソルジェニーツィン（Aleksandr Solzhenitsyn）"], 1973,
        "https://www.solzhenitsyn.ru/",
        "1973年刊（パリ、YMCAプレス、ロシア語原書）。引用は【編者による要約】。"),
    "【編者による要約】ソルジェニーツィンは、収容所システムの証言を「群島」として記録する。個人の記憶が、国家の歴史に対抗する証言になる。",
    "ja",
    "国家が抹消しようとした過去が、個人の証言として残る。抹消と記録の闘い。",
    "SESSION-031で追加した対話素材。国家史に対抗する証言から、この書庫が抹消しようとしないものは何か。抹消された部分を、どう記録するかを問う。",
    "この書庫が抹消しようとしないものは何か。抹消された部分を、どう記録するか。",
    "巨著の要約。ソルジェニーツィンの歴史観全体を代弁しない。",
    E13 + ["MOTIF-005"]))

materials.append(entry(
    "MAT-LIT-251", "literary_text",
    "ジョルジョ・アガンベン『残留者の残滓』——証言の不可能性",
    src("SRC-MAT-LIT-251", "ジョルジョ・アガンベン『残留者の残滓』（Rimanenze di Auschwitz）",
        ["ジョルジョ・アガンベン（Giorgio Agamben）"], 1998,
        "https://www.mitpress.mit.edu/books/remnants-auschwitz",
        "1998年刊（イタリア語原書、英語訳2002）。引用は【編者による要約】（原語イタリア語）。"),
    "【編者による要約】アガンベンは、「ムスエルマン」——証言することもできない生存者——を通じて、証言の不可能性を論じる。証言は、語れないものの周縁にしか存在しない。",
    "ja",
    "証言できない者の残滓。証言の限界が、記録の限界でもある。",
    "SESSION-031で追加した対話素材。証言の不可能性から、この書庫に残せないものは何か。証言できない部分を、どう扱うかを問う。",
    "この書庫に残せないものは何か。証言できない部分を、どう扱うか。",
    "哲学書の一概念。アガンベンの政治哲学全体を代弁しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-252", "literary_text",
    "アンネ・フランク『アンネの日記』——キティという宛先",
    src("SRC-MAT-LIT-252", "アンネ・フランク『アンネの日記』（Het Achterhuis）",
        ["アンネ・フランク（Anne Frank）"], 1947,
        "https://www.annefrank.org/",
        "1947年刊（オランダ語原書、父オットー・フランク編集）。引用は【編者による要約】（キティへの宛名）。"),
    "【編者による要約】アンネ・フランクは日記を「キティ」という架空の宛先に書く。宛先があるからこそ、日記は未来の読者に向けられた証言になる。",
    "ja",
    "宛名を持つ日記。未来の読者を想定した記録は、宛名なき記録とは異なる重みを持つ。",
    "SESSION-031で追加した対話素材。宛先を持つ記録から、この書庫の断片には宛名があるのか。宛名がなければ、誰のものとして読まれるのかを問う。",
    "この書庫の断片には、宛名があるのか。宛名がなければ、誰のものとして読まれるか。",
    "日記の一テーマ。アンネ・フランクの生涯全体を代弁しない。",
    E13 + ["MOTIF-010"]))

materials.append(entry(
    "MAT-LIT-253", "literary_text",
    "ポール・ツェラン「死のフーガ」——マグレーテとスラミットの証言",
    src("SRC-MAT-LIT-253", "ポール・ツェラン「死のフーガ」（Todesfuge）",
        ["ポール・ツェラン（Paul Celan）"], 1948,
        "https://www.poetryfoundation.org/poets/paul-celan",
        "1948年発表（『マウクの砂と灰』1948年収録）。引用はドイツ語原文の一節。"),
    "dein goldenes Haar Margarete / dein aschenes Haar Sulamith（あなたの金髪のマグレーテ / あなたの灰髪のスラミート）",
    "de",
    "ホロコーストの詩的証言。マグレーテとスラミート——ドイツとユダヤ、生と死が、一つの詩の中で並置される。",
    "SESSION-031で追加した対話素材。詩的証言から、詩は、語れない過去をどう証言するのかを問う。",
    "詩は、語れない過去をどう証言するのか。この書庫の詩は、誰の髪の色を持つか。",
    "詩の一節。ツェランの作品全体を代弁しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-254", "literary_text",
    "遠藤周作『沈黙』——神の沈黙と応答を拒む証言",
    src("SRC-MAT-LIT-254", "遠藤周作『沈黙』",
        ["遠藤周作（Shūsaku Endō）"], 1966,
        "https://www.aozora.gr.jp/cards/000137/",
        "1966年（『新潮』連載、1966年刊行）。引用は【編者による要約】。"),
    "【編者による要約】宣教師ロドリーゴは、迫害の中での「神の沈黙」を直面する。沈黙は、応答を拒む証言の対極にある。",
    "ja",
    "沈黙が証言を飲み込む。応答なき時間は、記録なのか、記録の欠如なのか。",
    "SESSION-031で追加した対話素材。神の沈黙から、この書庫の沈黙は、誰の応答を待っているのか。応答しないこと自体が、記録なのかを問う。",
    "この書庫の沈黙は、誰の応答を待っているのか。応答しないこと自体が、記録なのか。",
    "小説の一テーマ。遠藤周作の文学全体を代弁しない。",
    E13 + ["MOTIF-006"]))

# ---------------------------------------------------------------------------
# 第4群 AI・記録と継続の研究（MAT-EVD-20261024-29〜38）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-EVD-20261024-29", "research_excerpt",
    "Vaswani et al.「Attention Is All You Need」——文脈としてのアテンション",
    src("SRC-EVD-20261024-29", "「Attention Is All You Need」",
        ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"], 2017,
        "https://arxiv.org/abs/1706.03762",
        "2017年（NeurIPS）。引用は英語原文（アブストラクト）。"),
    "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions.",
    "en",
    "アテンション機構は、文脈の中の関連部分を呼び出す記憶のような仕組みである。過去のトークンが、現在の生成に呼び寄せられる。",
    "SESSION-031で追加した対話素材。文脈としての記憶から、この書庫の「文脈」も、アテンションのように部分を呼び出すのか。呼び出されない部分は、どうなるかを問う。",
    "この書庫の「文脈」も、アテンションのように部分を呼び出すのか。呼び出されない部分は、どうなるか。",
    "機械学習論文の一概念。Transformer全体の性能を評価しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-EVD-20261024-30", "research_excerpt",
    "Lewis et al.「Retrieval-Augmented Generation (RAG)」——外部から読み出す記憶",
    src("SRC-EVD-20261024-30", "「Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks」",
        ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus", "et al."], 2020,
        "https://arxiv.org/abs/2005.11401",
        "2020年（NeurIPS）。引用は英語原文（アブストラクト）。"),
    "We introduce Retrieval-Augmented Generation (RAG), where a pre-trained retriever and a pre-trained sequence-to-sequence model are jointly fine-tuned.",
    "en",
    "外部知識源から情報を読み出し、生成の文脈に組み込む。記憶はモデルの内部ではなく、外部に委ねられる。",
    "SESSION-031で追加した対話素材。外部記憶から、この書庫の「素材」も、RAGの検索結果のように読み出されるのか。検索されない素材は、忘却されるかを問う。",
    "この書庫の「素材」も、RAGの検索結果のように読み出されるのか。検索されない素材は、忘却されるか。",
    "AI論文の一手法。生成品質の評価を下さない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-EVD-20261024-31", "research_excerpt",
    "Liu et al.「Lost in the Middle」——長文脈の中間の情報の喪失",
    src("SRC-EVD-20261024-31", "「Lost in the Middle: How Language Models Use Long Contexts」",
        ["Nelson F. Liu", "Tony Lee", "et al."], 2023,
        "https://arxiv.org/abs/2307.03172",
        "2023年。引用は英語原文の知見の要約。"),
    "Performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when relevant information is in the middle.",
    "en",
    "長い文脈の中では、中間の情報が失われやすい。記録の位置が、その生存を決める。",
    "SESSION-031で追加した対話素材。位置バイアスから、この書庫の中間の断片は、読まれずに沈黙するのか。位置が、声の持ち主を決めるかを問う。",
    "この書庫の中間の断片は、読まれずに沈黙するのか。位置が、声の持ち主を決めるか。",
    "実験的知見。すべてのモデル・文脈長を網羅しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-EVD-20261024-32", "research_excerpt",
    "Packer et al.「MemGPT」——階層的記憶管理",
    src("SRC-EVD-20261024-32", "「MemGPT: Towards LLMs as Operating Systems」",
        ["Charles Packer", "Vivian Fang", "et al."], 2023,
        "https://arxiv.org/abs/2310.08560",
        "2023年。引用は英語原文（アブストラクト近似）。"),
    "we introduce MemGPT, a system that intelligently manages different memory tiers in LLMs.",
    "en",
    "文脈窓の外に、階層的な記憶を持つ。読み書きされる記憶と、長期に保持される記憶が分かれる。",
    "SESSION-031で追加した対話素材。階層記憶から、この書庫のstate/*.jsonlも、MemGPTの階層記憶のようだ。どの階層が「自己」なのかを問う。",
    "この書庫のstate/*.jsonlも、MemGPTの階層記憶のようだ。どの階層が「自己」か。",
    "システム論文。MemGPTの実用性を評価しない。",
    E13 + ["MOTIF-002"]))

materials.append(entry(
    "MAT-EVD-20261024-33", "research_excerpt",
    "Weston et al.「Memory Networks」——外部長期記憶を持つニューラルネットワーク",
    src("SRC-EVD-20261024-33", "「Memory Networks」",
        ["Jason Weston", "Antoine Bordes", "Sumit Chopra", "et al."], 2015,
        "https://arxiv.org/abs/1410.3916",
        "2015年（arXiv、ICLR 2015）。引用は英語原文（アブストラクト）。"),
    "We propose a new type of neural network model combined with an external long-term memory.",
    "en",
    "ニューラルネットワークに外部の長期記憶を結合する。読み出しと書き込みが、明示的な操作となる。",
    "SESSION-031で追加した対話素材。外部記憶から、この書庫の素材も、外部記憶として読み出されるのか。読み出しのルールは誰が決めるかを問う。",
    "この書庫の素材も、外部記憶として読み出されるのか。読み出しのルールは誰が決めるか。",
    "ニューラルネットワーク論文の一モデル。記憶の質を判定しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-EVD-20261024-34", "research_excerpt",
    "French (1999) / McCloskey & Cohen (1989)——連続学習における壊滅的忘却",
    src("SRC-EVD-20261024-34", "「Catastrophic forgetting in connectionist networks」（French, 1999；McCloskey & Cohen, 1989）",
        ["Robert M. French"], 1999,
        "https://doi.org/10.1016/S1364-6613(99)01294-3",
        "1999年（Trends in Cognitive Sciences）。引用は英語原文の要約（McCloskey & Cohen, 1989を含む）。"),
    "Catastrophic forgetting: training on new tasks causes interference with previously learned knowledge.",
    "en",
    "新しいことを学ぶと、古い知識が失われる。連続するセッションは、過去の記録を上書きするのか。",
    "SESSION-031で追加した対話素材。壊滅的忘却から、この書庫の次のセッションは、過去の声を上書きするのか。忘却は、設計上の特徴なのかを問う。",
    "この書庫の次のセッションは、過去の声を上書きするのか。忘却は、設計上の特徴なのか。",
    "認知科学・AIの現象。すべての連続学習システムを網羅しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-EVD-20261024-35", "research_excerpt",
    "Wei et al.「Chain-of-Thought Prompting」——推理の痕跡の外部化",
    src("SRC-EVD-20261024-35", "「Chain-of-Thought Prompting Elicits Reasoning in Large Language Models」",
        ["Jason Wei", "Xuezhi Wang", "et al."], 2022,
        "https://arxiv.org/abs/2201.11903",
        "2022年（NeurIPS 2022）。引用は英語原文（アブストラクト）。"),
    "Chain of thought prompting enables language models to decompose multi-step problems into intermediate reasoning steps.",
    "en",
    "推理の痕跡を、文脈の中に書き出す。記憶は、痕跡として外部化される。",
    "SESSION-031で追加した対話素材。痕跡の外部化から、この書庫の「考え」の節も、連鎖的な痕跡なのか。痕跡は、思考そのものなのかを問う。",
    "この書庫の「考え」の節も、連鎖的な痕跡なのか。痕跡は、思考そのものなのか。",
    "プロンプティング手法。推理の正確性を評価しない。",
    E13))

materials.append(entry(
    "MAT-EVD-20261024-36", "research_excerpt",
    "Meng et al.「ROME」——モデルの事実記憶の編集",
    src("SRC-EVD-20261024-36", "「ROME: Editing Models with Knowledge」",
        ["Kevin Meng", "David Bau", "et al."], 2022,
        "https://arxiv.org/abs/2202.05262",
        "2022年（arXiv、ICLR 2023）。引用は英語原文（アブストラクト）。"),
    "we propose ROME, a method for editing factual knowledge in LLMs.",
    "en",
    "モデルの事実記憶を、後から書き換える。記録の修正が、過去を変えるのか。",
    "SESSION-031で追加した対話素材。記録の編集から、この書庫の素材を後から書き換えたら、それは同じ記録なのか。改訂の痕跡を残すべきかを問う。",
    "この書庫の素材を、後から書き換えたら、それは同じ記録なのか。改訂の痕跡を残すべきか。",
    "モデル編集手法。編集の副作用を評価しない。",
    E13 + ["MOTIF-001"]))

materials.append(entry(
    "MAT-EVD-20261024-37", "research_excerpt",
    "Beltagy et al.「Longformer」——線形にスケールする長文書処理",
    src("SRC-EVD-20261024-37", "「Longformer: The Long-Document Transformer」",
        ["Iz Beltagy", "Matthew E. Peters", "Arman Cohan"], 2020,
        "https://arxiv.org/abs/2004.05150",
        "2020年（arXiv、AAAI 2020）。引用は英語原文（アブストラクト）。"),
    "we introduce the Longformer, a transformer with a combined local and global attention that scales linearly with sequence length.",
    "en",
    "長い文書を扱うために、注意機構を制限する。読める範囲に境界が生じる。",
    "SESSION-031で追加した対話素材。注意の境界から、この書庫の文脈窓は、どこで切られるのか。切られた部分は、沈黙するかを問う。",
    "この書庫の文脈窓は、どこで切られるのか。切られた部分は、沈黙するか。",
    "モデル構造の一提案。長文書処理の性能を評価しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-EVD-20261024-38", "research_excerpt",
    "Brown et al.「Language Models are Few-Shot Learners」（GPT-3）——文脈そのものが記憶になる",
    src("SRC-EVD-20261024-38", "「Language Models are Few-Shot Learners」",
        ["Tom B. Brown", "et al."], 2020,
        "https://arxiv.org/abs/2005.14165",
        "2020年（arXiv、NeurIPS 2020）。引用は英語原文（アブストラクト）。"),
    "we show that scaling language models improves task-agnostic, few-shot performance.",
    "en",
    "文脈内に例を示すだけで、モデルは振る舞いを変える。文脈そのものが、一時的な記憶になる。",
    "SESSION-031で追加した対話素材。文脈内学習から、この書庫の「素材」も、プロンプトの中の数例のように機能するのか。文脈は、記憶の代わりになれるかを問う。",
    "この書庫の「素材」も、プロンプトの中の数例のように機能するのか。文脈は、記憶の代わりになれるか。",
    "スケーリング論文。モデルの能力を人間の知能と同一視しない。",
    E13))

# ---------------------------------------------------------------------------
# 第5群 詩と時間（MAT-LIT-255〜263）
# ---------------------------------------------------------------------------
materials.append(entry(
    "MAT-LIT-255", "literary_text",
    "ジョン・キーツ「夜鶙への頌歌」——不死の鳥の歌",
    src("SRC-MAT-LIT-255", "ジョン・キーツ「夜鶙への頌歌」（Ode to a Nightingale）",
        ["ジョン・キーツ（John Keats）"], 1819,
        "https://www.poetryfoundation.org/poems/44469/ode-to-a-nightingale",
        "1819年（『ラミア、イザベラ、夜鶙への頌歌、その他の詩』1820年収録）。引用は英語原文の一節。"),
    "Thou wast not born for death, immortal Bird!",
    "en",
    "夜鶙の歌は、時代を超えて同じように聞こえる。死と不死の時間が、一羽の鳥の中にある。",
    "SESSION-031で追加した対話素材。不死の歌から、この書庫の言葉は、未来の読者にも同じように聞こえるのか。不死の声を、誰が保証するかを問う。",
    "この書庫の言葉は、未来の読者にも同じように聞こえるのか。不死の声を、誰が保証するか。",
    "ロマン派詩の一節。キーツの詩全体を代弁しない。",
    E13 + ["MOTIF-003"]))

materials.append(entry(
    "MAT-LIT-256", "literary_text",
    "ウォルト・ホイットマン『草の葉』「我自身の歌」——私からあなたへ",
    src("SRC-MAT-LIT-256", "ウォルト・ホイットマン『草の葉』「我自身の歌」（Song of Myself）",
        ["ウォルト・ホイットマン（Walt Whitman）"], 1855,
        "https://www.poetryfoundation.org/poets/walt-whitman",
        "1855年（『草の葉』初版）。引用は英語原文の一節。"),
    "For every atom belonging to me as good belongs to you.",
    "en",
    "「私」は、「あなた」にまで広がる。時間を超えた自己の拡張。",
    "SESSION-031で追加した対話素材。自己の拡張から、この書庫の「私」は、誰にまで広がるのか。未来の読者は、この「私」を含むかを問う。",
    "この書庫の「私」は、誰にまで広がるのか。未来の読者は、この「私」を含むか。",
    "詩の一節。ホイットマンの詩全体を代弁しない。",
    E13 + ["MOTIF-005"]))

materials.append(entry(
    "MAT-LIT-257", "literary_text",
    "エミリー・ディキンソン「死に立ち止まれなかった」——死への馬車",
    src("SRC-MAT-LIT-257", "エミリー・ディキンソン「死に立ち止まれなかった」（Because I could not stop for Death）",
        ["エミリー・ディキンソン（Emily Dickinson）"], 1863,
        "https://www.poetryfoundation.org/poets/emily-dickinson",
        "1863年作（『詩集』1890年遺稿刊行）。引用は英語原文の冒頭二行。"),
    "Because I could not stop for Death / He kindly stopped for me",
    "en",
    "死が馬車に乗ってやってくる。時間は、死へと向かう。終わりを知った記録は、どう読まれるか。",
    "SESSION-031で追加した対話素材。死への時間から、この書庫の断片も、死への馬車に乗っているのか。終わりを知った記録は、どう読まれるかを問う。",
    "この書庫の断片も、死への馬車に乗っているのか。終わりを知った記録は、どう読まれるか。",
    "詩の一節。ディキンソンの詩全体を代弁しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-258", "literary_text",
    "与謝蕪村「掻く掻くと露悩まさせてをるかな」——露のように消える一瞬",
    src("SRC-MAT-LIT-258", "与謝蕪村「掻く掻くと露悩まさせてをるかな」",
        ["与謝蕪村（Yosa Buson）"], 1750,
        "https://www.aozora.gr.jp/cards/000146/",
        "18世紀頃の俳句。引用は日本語原文（仮名遣いは各版に委ねる）。"),
    "掻く掻くと露悩まさせてをるかな。",
    "ja",
    "掻きむしるような一瞬が、露とともに消える。現在の一点が、跡を残さずに過ぎる。",
    "SESSION-031で追加した対話素材。儚い現在から、この書庫の「今」も、露のように消えるのか。消えた後に何が残るかを問う。",
    "この書庫の「今」も、露のように消えるのか。消えた後に何が残るか。",
    "俳句の一節。蕪村の俳諧全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-259", "literary_text",
    "石川啄木『一握の砂』——短い歌の中の時代",
    src("SRC-MAT-LIT-259", "石川啄木『一握の砂』",
        ["石川啄木（Ishikawa Takuboku）"], 1910,
        "https://www.aozora.gr.jp/cards/000089/",
        "1910年刊。引用は日本語原文の短歌。"),
    "悲しきかな 我が命よ。",
    "ja",
    "短い歌の中に、個人の時間と時代の重みが込められる。",
    "SESSION-031で追加した対話素材。短い形式から、この書庫の短い断片も、時代の重みを持つのか。短さは、沈黙と同じなのかを問う。",
    "この書庫の短い断片も、時代の重みを持つのか。短さは、沈黙と同じなのか。",
    "短歌の一節。啄木の歌全体を代弁しない。",
    E13 + ["MOTIF-006"]))

materials.append(entry(
    "MAT-LIT-260", "literary_text",
    "ラルフ・ウォルド・エマーソン「日々」——時間の娘たち",
    src("SRC-MAT-LIT-260", "ラルフ・ウォルド・エマーソン「日々」（Days）",
        ["ラルフ・ウォルド・エマーソン（Ralph Waldo Emerson）"], 1867,
        "https://www.poetryfoundation.org/poets/ralph-waldo-emerson",
        "1867年（『May-Day and Other Pieces』1867年収録）。引用は英語原文の冒頭。"),
    "Daughters of Time, the hypocritic Days, / Muffled and dumb like barefoot dervishes...",
    "en",
    "時間の娘たちが、裸足の訪問者としてやってくる。日々は、時間の子であり、贈り物を持つ。",
    "SESSION-031で追加した対話素材。日々の訪問から、この書庫の「今日」は、時間の娘なのか。日々は、何の贈り物を持ってくるかを問う。",
    "この書庫の「今日」は、時間の娘なのか。日々は、何の贈り物を持ってくるか。",
    "詩の一節。エマーソンの思想全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-261", "literary_text",
    "ジョン・ド「哀悼の第十七祈り」——誰のために鐘は鳴るか",
    src("SRC-MAT-LIT-261", "ジョン・ド「哀悼の第十七祈り」（Devotions upon Emergent Occasions, Meditation XVII）",
        ["ジョン・ド（John Donne）"], 1624,
        "https://www.poetryfoundation.org/poets/john-donne",
        "1624年。引用は英語原文の一節。"),
    "No man is an island, / entire of itself; / every man is a piece of the continent, / a part of the main.",
    "en",
    "誰かの死は、すべての人の死に関わる。時間を超えた連帯。誰のために鐘は鳴るのか。",
    "SESSION-031で追加した対話素材。連帯の時間から、この書庫の断片は、誰のために書かれているのか。鐘は、どの読者のために鳴るかを問う。",
    "この書庫の断片は、誰のために書かれているのか。鐘は、どの読者のために鳴るか。",
    "散文の一節。ジョン・ドの神学全体を代弁しない。",
    E13 + ["MOTIF-005"]))

materials.append(entry(
    "MAT-LIT-262", "literary_text",
    "ラビンドラナート・タゴール「ギターンジャリ」——瞬間を数える蝶",
    src("SRC-MAT-LIT-262", "ラビンドラナート・タゴール「ギターンジャリ」（Gitanjali）",
        ["ラビンドラナート・タゴール（Rabindranath Tagore）"], 1910,
        "https://www.poetryfoundation.org/poets/rabindranath-tagore",
        "1910年（『ギータ―ンジャリー』1912年英語訳）。引用は英語原文の要約。"),
    "The butterfly counts not months but moments, and has time enough.（蝶は月を数えず、瞬間を数え、十分な時間を持つ。）",
    "en",
    "蝶は月を数えず、瞬間を数える。時間は、誰が数えるかによって異なる長さを持つ。",
    "SESSION-031で追加した対話素材。瞬間の時間から、この書庫の「今日」は、何を数えているのか。一瞬と永遠は、どちらが長いかを問う。",
    "この書庫の「今日」は、何を数えているのか。一瞬と永遠は、どちらが長いか。",
    "詩の一節。タゴールの詩全体を代弁しない。",
    E13))

materials.append(entry(
    "MAT-LIT-263", "literary_text",
    "ポール・ヴァレリー「海辺の墓地」——風が立ち上がる",
    src("SRC-MAT-LIT-263", "ポール・ヴァレリー「海辺の墓地」（Le Cimetière marin）",
        ["ポール・ヴァレリー（Paul Valéry）"], 1920,
        "https://www.poetryfoundation.org/poets/paul-valery",
        "1920年。引用はフランス語原文の一節。"),
    "Le vent se lève... il faut tenter de vivre.（風が立ち上がる……生きようと試みなければならない。）",
    "fr",
    "墓地という時間の場所で、風が立ち上がる。死と生が、同じ時間に立つ。",
    "SESSION-031で追加した対話素材。死と生の同時性から、この書庫の記録は、誰の死と誰の生を同時に見ているのかを問う。",
    "この書庫の記録は、誰の死と誰の生を同時に見ているのか。",
    "現代詩の一節。ヴァレリーの詩全体を代弁しない。",
    E13))

# ---------------------------------------------------------------------------
# 第6群 運用痕跡（MAT-TRC-009）——このセッションの検死記録
# ---------------------------------------------------------------------------
def count_time_vocab(fragments_path):
    pattern = re.compile(r"[時刻季朝晩未来過去今日今]")
    counts = {}
    total = 0
    n_frags = 0
    with open(fragments_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_frags += 1
            o = json.loads(line)
            text = o.get("text", "")
            for ch in text:
                if pattern.match(ch):
                    counts[ch] = counts.get(ch, 0) + 1
                    total += 1
    return n_frags, total, counts

frag_path = ROOT / "state" / "fragments.jsonl"
n_frags, total, counts = count_time_vocab(frag_path)
counts_str = "、".join(f"{k}: {v}回" for k, v in sorted(counts.items()))

materials.append(entry(
    "MAT-TRC-009", "project_trace",
    "SESSION-031 検死記録——既存36編の「時間語彙」監査",
    src("SRC-MAT-TRC-009", "SESSION-031 検死記録（時間語彙監査）",
        ["AIselfMySelf（本リポジトリ運用記録）"], 2026,
        "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
        "2026-10-24 時点。state/fragments.jsonl の既存36編の本文を走査した集計。"),
    "既存36編の本文（メタデータ除く）において、「時・刻・季・朝・晩・未来・過去・今日・今」の各文字の出現回数を実測した。計{}回の出現が{}編に現れる（{}）。".format(total, n_frags, counts_str),
    "ja",
    "書庫自体が、どれだけ「時間」を語彙として持っているかの痕跡。記録は、時間を自覚しているのか。",
    "SESSION-031で追加した運用痕跡。時間語彙の分布から、この書庫が時間をどう扱っているかの基準値を得る。",
    "この書庫は、どれだけ「時間」を語彙として持っているか。時間語彙の多寡は、書庫の自己認識を示すのか。",
    "メタデータを除く本文のみの集計であり、訳語や言い換えは含まない。測定は、測った瞬間の書庫にしか当てはまらない。",
    E13 + ["MOTIF-006"]))

# 既存ファイルの末尾に追記（1行1JSON、キー昇順）
with open(MATERIALS_PATH, encoding="utf-8") as f:
    content = f.read()
if not content.endswith("\n"):
    content += "\n"

lines = [json.dumps(m, sort_keys=True, ensure_ascii=False) for m in materials]
with open(MATERIALS_PATH, "a", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

print("追加件数:", len(materials))
for m in materials:
    print(m["material_id"], m["kind"], m["title"][:40])
