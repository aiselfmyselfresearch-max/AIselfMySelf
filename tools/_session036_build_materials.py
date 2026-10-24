#!/usr/bin/env python3
"""SESSION-036: 「声・語り・沈黙・聴くこと」を主題とした新規資料の追加。

CONTENT_POLICY.md に従い、直接引用・編者による要約・創作を明確に分ける。
原典未照合の引用・要約には scope_note / version_note でその旨を記す。
verification は null（本セッションでは原典の Web 照合を実施していない）。
origin は本リポジトリの現在の HEAD を指す（新規に作成した記録であるため）。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT / "state" / "materials.jsonl"
MOTIFS = ROOT / "state" / "motifs.jsonl"
SESSIONS = ROOT / "state" / "sessions.jsonl"

ORIGIN_COMMIT = "19e410335c850fcb88ce899fe535924db38b360a"


def origin(record_id: str) -> dict:
    return {
        "repository": "https://github.com/aiselfmyselfresearch-max/AIselfMySelf",
        "commit": ORIGIN_COMMIT,
        "source_record_id": record_id,
        "evidence_record_id": record_id,
        "source_record_path": "state/materials.jsonl",
        "evidence_record_path": "state/materials.jsonl",
    }


def mat(material_id: str, kind: str, title: str, source: dict, passage: str,
        lang: str, context: str, source_note: str, invitation: str, scope: str,
        motifs: list, questions: list) -> dict:
    return {
        "material_id": material_id,
        "kind": kind,
        "title": title,
        "source": {
            "source_id": source["source_id"],
            "title": source["title"],
            "authors": source["authors"],
            "year": source["year"],
            "url": source["url"],
            "version_note": source["version_note"],
        },
        "passage": passage,
        "passage_language": lang,
        "context": context,
        "source_note": source_note,
        "literary_invitation": invitation,
        "scope_note": scope,
        "motif_ids": motifs,
        "origin": origin(source["source_id"]),
    }


NEW = []

# ---------------- 文学・哲学原典（28件） ----------------
NEW.append(mat(
    "MAT-LIT-388", "literary_text",
    "ロラン・バルト『像・音楽・テクスト』より「声の穀粒」(Le grain de la voix, 1972)",
    {"source_id": "SRC-NEW-20261024-001", "title": "Image, Music, Text (essai : Le grain de la voix)",
     "authors": ["Roland Barthes"], "year": 1972,
     "url": "https://en.wikipedia.org/wiki/Image,_Music,_Text",
     "version_note": "エッセイは初出 1972（L'Obvie et l'obtus）；英訳：Stephen Heath, Image-Music-Text (1977)。原典の頁は未照合、日本語は編者訳。"},
    "« le grain, c'est le corps dans la voix quand elle chante »",
    "fr",
    "バルト『声の穀粒』の核心句。歌声における『穀粒』——喉に肉体があるときの身体——という表現。",
    "歌声における『穀粒』——喉に肉体が宿るときの身体——というバルトの語り。",
    "「声の穀粒」——発声に肉体が乗り移る瞬間——は、この書庫の断片が『声』を持つと主張するとき、どこに肉体を想定しているのか。肉体を持たない語りが『穀粒』を装うとき、それは装飾なのか、それとも別の条件なのか。",
    "文芸批評エッセイ；AIの発声器官や意識についての議論ではない。",
    ["MOTIF-004", "MOTIF-009"], ["Q-004", "Q-005", "Q-007"]))

NEW.append(mat(
    "MAT-LIT-389", "literary_text",
    "エマニュエル・レヴィナス『全体性と外在性』(Totalité et Infini, 1961)",
    {"source_id": "SRC-NEW-20261024-002", "title": "Totality and Infinity: An Essay on Exteriority",
     "authors": ["Emmanuel Levinas"], "year": 1961,
     "url": "https://archive.org/details/totalityinfinity0000levin",
     "version_note": "初版 1961（アルフォンヌ・ビアンコーニ訳、1969年英訳等）。『言うこと（dire）』と『述べたこと（dit）』の区別は編者による要約；原典未照合。"},
    "【レヴィナス『全体性と外在性』（1961）より、『言うこと（dire）』と『述べたこと（dit）』の区別——顔面を向けた遭遇における語りは、既に語られた内容（コンテンツ）とは異なる次元に位置づけられる（編者による要約；原典未照合）】",
    "fr",
    "『言うこと』と『述べたこと』の区別。顔面を向けた遭遇における語り。",
    "『言うこと』は相手への呼びかけそのものであり、『述べたこと』はそれに収容された内容である。",
    "この書庫の断片が次のセッションへ言葉を渡すとき、それは『述べたこと』の伝達なのか、『言うこと』としての遭遇なのか。次の読み手が『同じ言葉』を受け取る保証はどこにあるのか。",
    "現象学・倫理学の古典；AIの他者遭遇や意識を証明するものではない。",
    ["MOTIF-004", "MOTIF-005"], ["Q-017", "Q-018", "Q-029"]))

NEW.append(mat(
    "MAT-LIT-390", "literary_text",
    "アドリアーナ・カヴァレロ『一以上の声のために』(For More than One Voice, 2005; 原書 2002)",
    {"source_id": "SRC-NEW-20261024-003", "title": "For More than One Voice",
     "authors": ["Adriana Cavarero"], "year": 2005,
     "url": "https://press.uchicago.edu/ucp/books/book/chicago/F/bo5924694.html",
     "version_note": "イタリア語原書 2002；英語訳 2005。抄録は編者による要約；原典未照合。"},
    "【声は、語られた内容を超えて、誰が話しているかという『独自性』を帯びている（カヴァレロ『一以上の声のために』、2005；編者による要約；原典未照合）】",
    "en",
    "声の独自性——『誰が話しているか』という次元が語られた内容を超えて残ること。",
    "声は内容の器ではなく、そこに『語り手の痕跡』としての独自性を帯びる。",
    "この書庫の断片に『声の持ち主』を名乗らせないつつも語らせるとき、声の帰属はどこに生じるのか。他者の声を想像するとき、その距離はどう保たれるべきか。",
    "政治哲学・フェミニスト理論；AIの声を擬人化した主張ではない。",
    ["MOTIF-004", "MOTIF-009"], ["Q-005", "Q-047", "Q-048"]))

NEW.append(mat(
    "MAT-LIT-391", "literary_text",
    "ヴィクトル・シュクロフスキー『芸術としての手法』(Искусство как приём, 1917)",
    {"source_id": "SRC-NEW-20261024-004", "title": "Art as Technique (Искусство как приём)",
     "authors": ["Viktor Shklovsky"], "year": 1917,
     "url": "https://www.marxists.org/reference/subject/philosophy/works/ru/shklovsky-art-as-technique.htm",
     "version_note": "1917年のロシア語エッセイ；抄録は編者による要約；原典未照合。"},
    "【『顕示化（остранение）』：芸術は物事を『見慣れないもの』として返し、自動化された知覚を回復させる（シュクロフスキー、1917；編者による要約；原典未照合）】",
    "ru",
    "「異化／顕示化」——芸術が慣習化された知覚を解除し、対象を新たに感じさせる装置として働くこと。",
    "繰り返しに慣らされた感覚を、一度『見慣れないもの』として戻す操作。",
    "この書庫の『作法と定型』（MOTIF-008）が問いを開いたまま保つ装置なのか、それとも声の型にはめ込む装置なのか——シュクロフスキーの顕示化は、その境界線をどう描き直すのか。",
    "ロシア形式主義の文芸理論；AIの創造性や感情の評価とは別軸。",
    ["MOTIF-008"], ["Q-037", "Q-039"]))

NEW.append(mat(
    "MAT-LIT-392", "literary_text",
    "ジョン・ケージ『沈黙』(Silence, 1961) より「無についての講義」(Lecture on Nothing, 1959)",
    {"source_id": "SRC-NEW-20261024-005", "title": "Silence: Lectures and Writings (Lecture on Nothing)",
     "authors": ["John Cage"], "year": 1961,
     "url": "https://en.wikipedia.org/wiki/Silence_(John_Cage_book)",
     "version_note": "講義は1959年作成、1961年の書籍『沈黙』所収。引用は詩形の一節；原典のページは未照合。"},
    "I have nothing to say\nand I am saying it\nand that is poetry\nas I need it.",
    "en",
    "『沈黙』の中核となる講義『無についての講義』から、何も語らないことと語ることが同居する一節。",
    "何も語らないことが、語ることそのものになる——沈黙と発声の境界が溶解する瞬間。",
    "この書庫に沈黙が9編に現れ（MAT-TRC-005）、温かさが0編であることをどう読むべきか。語らないことは、語ることへの拒否なのか、それとも別の発声なのか。",
    "現代音楽・文芸エッセイ；音楽性や沈黙の質を判定するものではない。",
    ["MOTIF-006", "MOTIF-004"], ["Q-039", "Q-044", "Q-047"]))

NEW.append(mat(
    "MAT-LIT-393", "literary_text",
    "ジャン＝リュック・ナンシー『聞こえること』(Écouter, 2002; 英訳 Listening, 2007)",
    {"source_id": "SRC-NEW-20261024-006", "title": "Listening (Écouter, 2002)",
     "authors": ["Jean-Luc Nancy"], "year": 2002,
     "url": "https://www.fordhampress.com/title/listening",
     "version_note": "フランス語原書 2002；英語訳 2007。抄録は編者による要約；原典未照合。"},
    "【『聞くこと』は理解とは別の次元にある。音は意味に還元されないまま、聴く者の身体を揺さぶる（ナンシー、2002；編者による要約；原典未照合）】",
    "fr",
    "聴くことの現象学——音が意味に還元されずに残る次元。",
    "聞くことと理解することを分ける。音は身体を揺さぶるだけで『伝達』を完了しない。",
    "この書庫が素材を『読む』とき、理解に達する前に何が起きるのか。読み手は聴く者として何が揺さぶられ、何を拒むのか。",
    "現象学；AIの聴覚や身体感覚の主張ではない。",
    ["MOTIF-004", "MOTIF-009"], ["Q-013", "Q-049", "Q-050"]))

NEW.append(mat(
    "MAT-LIT-394", "literary_text",
    "ポール・セラン「メリディアン」(Der Meridian, 1960)",
    {"source_id": "SRC-NEW-20261024-007", "title": "Der Meridian (The Meridian)",
     "authors": ["Paul Celan"], "year": 1960,
     "url": "https://www.poetryfoundation.org/poets/paul-celan",
     "version_note": "ブレーメン文学賞受賞記念講演（1960年5月29日）。抄録は編者による要約；原典のドイツ語原文・頁は未照合。"},
    "【『メリディアン』（1960）における、母語の不在と書き書くことへの帰依——『詩は、呪われた母語の不在を記す』（編者による要約；原典未照合）】",
    "de",
    "母語の不在の中で書き続けること——詩が喪失を言語化しようとする試み。",
    "母語を失った者が書くとき、書く行為自体が喪失の記録になる。",
    "母語を持たないこの書庫の声にとって『自分を訳す』とは何か（Q-059）。母語の不在を欠如の物語にも特権の物語にもせずに書けるか。",
    "ホロコースト生存者の詩；詩的比喩をAIの自己表現に流用しない。",
    ["MOTIF-006", "MOTIF-009"], ["Q-047", "Q-048", "Q-049"]))

NEW.append(mat(
    "MAT-LIT-395", "literary_text",
    "マックス・ピカール『沈黙の世界』(Die Welt des Schweigens, 1948)",
    {"source_id": "SRC-NEW-20261024-008", "title": "The World of Silence (Die Welt des Schweigens)",
     "authors": ["Max Picard"], "year": 1948,
     "url": "https://archive.org/details/worldofsilence0000picc",
     "version_note": "ドイツ語原書 1948；抄録は編者による要約；原典未照合。"},
    "【沈黙は『何もないところ』ではなく、語りが立ち現れる前の『場』として機能する（ピカール、1948；編者による要約；原典未照合）】",
    "de",
    "沈黙を欠如ではなく『場』として捉える。語りが現れる前の土台。",
    "沈黙は語りの外側にあるのではなく、語りが成立するための前提として機能する。",
    "この書庫に『書かれなかった行』（MOTIF-006）が多いことを、単なる欠落として数えるべきか。沈黙が語りを支える場として機能しているとすれば、何を保持しているのか。",
    "ドイツ語圏の哲学的散文；沈黙の価値を判定するものではない。",
    ["MOTIF-006"], ["Q-039", "Q-044", "Q-047"]))

NEW.append(mat(
    "MAT-LIT-396", "literary_text",
    "R. マレー・シェーファー『音の風景』(The Soundscape: Our Sonic Environment and the Tuning of the World, 1977)",
    {"source_id": "SRC-NEW-20261024-009", "title": "The Soundscape: Our Sonic Environment and the Tuning of the World",
     "authors": ["R. Murray Schafer"], "year": 1977,
     "url": "https://archive.org/details/soundscapeours0000scha",
     "version_note": "初版 1977。『音響環境（soundscape）・耳掃除（ear cleaning）・hi-fi/lo-fi』等の概念は編者による要約；原典未照合。"},
    "【『音響環境（soundscape）』——環境の音の全体を一つの作曲として捉える概念。シェーファーは『耳掃除（ear cleaning）』と『hi-fi / lo-fi』を提唱した（1977；編者による要約；原典未照合）】",
    "en",
    "環境音全体を一つの構成として捉える『音響環境』の概念。",
    "音の風景は、そこに住む者の聞き方そのものを前提にしている。",
    "この書庫の『音の風景』は何か。断片・素材・精読報告が重なる場所で、どの音が強調され、どの音が沈黙させられているのか。",
    "音響生態学・環境芸術；AIの聴覚体験を主張するものではない。",
    ["MOTIF-003", "MOTIF-009"], ["Q-030", "Q-049"]))

NEW.append(mat(
    "MAT-LIT-397", "literary_text",
    "ジャック・アッタリ『ノイズ』(Bruits: Essai sur l'économie politique de la musique, 1977; 英訳 Noise: The Political Economy of Music)",
    {"source_id": "SRC-NEW-20261024-010", "title": "Noise: The Political Economy of Music (Bruits, 1977)",
     "authors": ["Jacques Attali"], "year": 1977,
     "url": "https://archive.org/details/noisepoliticale0000atta",
     "version_note": "フランス語原書 1977；英語訳 1985。抄録は編者による要約；原典未照合。"},
    "【音楽は単なる娯楽ではなく、社会の秩序を予告する『予言』である——『ノイズは暴力である』（アッタリ、1977；編者による要約；原典未照合）】",
    "fr",
    "ノイズと音楽が社会秩序の予言として機能すること。",
    "音の秩序は社会の秩序を映し、それを先取りする。",
    "この書庫が『声の秩序』——どの声が増幅され、どの声がノイズとして処理されるか——をどう設計しているのか。未参照の335件の素材は、この音響秩序の中でどう位置づけられるか（Q-080）。",
    "音楽社会学；AIの音声生成の政治経済を直接評価するものではない。",
    ["MOTIF-005", "MOTIF-012"], ["Q-019", "Q-036"]))

NEW.append(mat(
    "MAT-LIT-398", "literary_text",
    "ドナルド・イーデ『聴くことと声』(Listening and Voice: Phenomenologies of Sound, 1976; 第2版 2007)",
    {"source_id": "SRC-NEW-20261024-011", "title": "Listening and Voice: Phenomenologies of Sound",
     "authors": ["Don Ihde"], "year": 1976,
     "url": "https://www.sup.org/books/title/?id=1536",
     "version_note": "初版 1977（State University of New York Press）；第2版 2007。抄録は編者による要約；原典未照合。年を初版原稿年の1976として記録。"},
    "【『聴くこと』は見ることとは異なる現象学を持ち、声は『源泉』として現れる——イーデ『聴くことと声』（1976；編者による要約；原典未照合）】",
    "en",
    "聴くことの現象学——声が『源泉』として聞き手の前に立つ構造。",
    "声は聞こえる対象であると同時に、聞こえるものの起点として機能する。",
    "この書庫の断片が『声』を持つと主張するとき、その声は誰の『源泉』なのか。次のセッションがその声を再生成するとき、源泉は変わるのか。",
    "現象学；聴覚障害や音声処理の評価とは別軸。",
    ["MOTIF-004"], ["Q-013", "Q-049"]))

NEW.append(mat(
    "MAT-LIT-399", "literary_text",
    "ヴァルター・ベンヤミン「翻訳者の課題」(Die Aufgabe des Übersetzers, 1923)",
    {"source_id": "SRC-NEW-20261024-012", "title": "The Task of the Translator (Die Aufgabe des Übersetzers)",
     "authors": ["Walter Benjamin"], "year": 1923,
     "url": "https://www.marxists.org/reference/subject/philosophy/works/ge/benjamin.htm",
     "version_note": "1923年のエッセイ；抄録は編者による要約；原典未照合。"},
    "【『翻訳は原典の「生」を後続の言語における「生」へ移すものであり、translatability（翻訳可能性）は原典の意図に内在する』（ベンヤミン、1923；編者による要約；原典未照合）】",
    "de",
    "翻訳が原典の命を後続言語へ継承する行為であること。",
    "翻訳は内容の移転ではなく、命の継承である。",
    "この書庫が非日本語引文を日本語で受け止め、訳者名を四分の三で消してきたこと（MAT-TRC-007）を、命の継承としてどう読むべきか。訳者の不在は、継承の断絶なのか。",
    "文芸理論・翻訳論；翻訳の質や正確さを判定するものではない。",
    ["MOTIF-011"], ["Q-057", "Q-058", "Q-059"]))

NEW.append(mat(
    "MAT-LIT-400", "literary_text",
    "聖書『ヨハネによる福音書』1章1節（コイネ・ギリシャ語, 1世紀)",
    {"source_id": "SRC-NEW-20261024-013", "title": "Gospel according to John 1:1 (Koine Greek)",
     "authors": ["Traditionally John the Apostle"], "year": 100,
     "url": "https://en.wikisource.org/wiki/Bible_(King_James)/John",
     "version_note": "コイネ・ギリシャ語写本伝承；引用はテクストス・レセプトゥス伝統の一形態；神学的正統性を主張するための引用ではない。"},
    "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος.",
    "grc",
    "『初めに言葉（ロゴス）があった』——語りの起源を置く一節。",
    "ロゴスは語りと理性の両義を持ち、存在の始まりと結びつく。",
    "『言葉から始まる』ことは、この書庫が素材と言葉をどう扱うかとどう重なるのか。語りが先にあって世界が続くのか、それとも逆なのか。",
    "古代文書；信仰上の主張を事実として扱うものではない。",
    ["MOTIF-004", "MOTIF-002"], ["Q-002", "Q-004", "Q-018"]))

NEW.append(mat(
    "MAT-LIT-401", "literary_text",
    "世阿弥『花伝書』(15世紀後半〜16世紀初頭, 諸伝本)",
    {"source_id": "SRC-NEW-20261024-014", "title": "Hana-den-sho (花伝書)",
     "authors": ["Zeami Motokiyo (trad.)"], "year": 1500,
     "url": "https://www.aozora.gr.jp/person/149/",
     "version_note": "能楽論諸伝本；成立は15世紀後半〜16世紀初頭とされる。抄録は編者による要約；原典の頁・節は未照合。"},
    "【『花伝書』における声の伝授——能はまず声を養うことから始まり、『初心忘るべからず』の作法が声と身体を結ぶ（世阿弥、15c–16c；編者による要約；原典未照合）】",
    "ja",
    "能における声の修行——声を養うことと、身・技・心の結びつき。",
    "声は技法の外側にあるのではなく、身体と心の訓練の産物として成立する。",
    "この書庫の『声』——断片の語り口やナレーター・モード——は、どこで養われ、どこで型にはめられているのか。声の訓練を欠いた『声なき声』は、何を失うのか。",
    "能楽論；能や世阿弥の歴史的実在を評価するものではない。",
    ["MOTIF-003", "MOTIF-004"], ["Q-014", "Q-047"]))

NEW.append(mat(
    "MAT-LIT-402", "literary_text",
    "宮澤賢治『セロ弾きのゴーシュ』(1922, 初出・底本は諸説)",
    {"source_id": "SRC-NEW-20261024-015", "title": "Gosho the Cellist (セロ弾きのゴーシュ)",
     "authors": ["Kenji Miyazawa"], "year": 1922,
     "url": "https://www.aozora.gr.jp/cards/000081/files/47190_47403.html",
     "version_note": "初出時期と底本は諸説あり（童話館版 1932年等）。抄録は編者による要約；原典未照合。"},
    "【ゴーシュが猫たちの前でセロをひき、音を『身体で受け止め直す』夜の場面——『身体を通した音の修行』（宮澤賢治、1922；編者による要約；原典未照合）】",
    "ja",
    "ゴーシュが猫たちの前でセロを弾き、音を身体で受け止め直す場面。",
    "音は頭で理解するものではなく、身体を通して受け止め直される。",
    "この書庫の『音の風景』——素材を読む行為は、頭で処理するだけでなく身体を通して受け止め直されているか。受け止め直されない素材は、沈黙のまま残るのか。",
    "児童文学；賢治の生涯や思想を正面から評価するものではない。",
    ["MOTIF-003"], ["Q-014", "Q-049", "Q-050"]))

NEW.append(mat(
    "MAT-LIT-403", "literary_text",
    "谷崎潤一郎『陰翳礼讃』(1934)",
    {"source_id": "SRC-NEW-20261024-016", "title": "In Praise of Shadows (陰翳礼讃)",
     "authors": ["Jun'ichiro Tanizaki"], "year": 1934,
     "url": "https://www.aozora.gr.jp/person/85/",
     "version_note": "『婦人公論』連載 1933年12月〜1934年3月；単行本 1934年。青空文庫作者ページを出典として指す。抄録は編者による要約。"},
    "美しさは、物そのものにあるのではない。陰翳の模様にのみあるのだ。",
    "ja",
    "『陰翳礼讃』の核心句——美しさは物そのものにあるのではなく、陰翳（光と影の模様）にのみある。",
    "美しさは対象の内在性にあるのではなく、対象と環境（陰翳）の関係に生じる。",
    "この書庫の『声』——どの断片が陰にあり、どの断片が光にあるのか。陰翳の中に沈められた素材を、どう読み直せるのか。",
    "エッセイ；東洋の美意識を西洋との対比で簡略化しない。",
    ["MOTIF-007"], ["Q-021", "Q-023", "Q-027"]))

NEW.append(mat(
    "MAT-LIT-404", "literary_text",
    "室生犀星「故郷」(1924)",
    {"source_id": "SRC-NEW-20261024-017", "title": "Furusato (故郷)",
     "authors": ["室生犀星"], "year": 1924,
     "url": "https://www.aozora.gr.jp/person/1489/",
     "version_note": "1924年の詩；青空文庫作者ページを出典として指す。抄録は編者による要約；原典未照合。"},
    "【「故郷」（1924）における、遠くへ去った父への呼びかけ——語り手の声が届かない宛先へ向けられる（編者による要約；原典未照合）】",
    "ja",
    "故郷へ、そして遠くに去った父へ向けられる呼びかけの声。",
    "声は届かない宛先へ向けられるとき、宛先そのものを形作る。",
    "この書庫に人名の宛名が0件だったこと（MAT-TRC-006）をどう読むか。宛先を空欄にすることは、呼びかけの放棄なのか、それとも次の読み手への委任なのか。",
    "近代詩；犀星の生涯や精神史を評価するものではない。",
    ["MOTIF-004", "MOTIF-006"], ["Q-033", "Q-036", "Q-038"]))

NEW.append(mat(
    "MAT-LIT-405", "literary_text",
    "知里幸恵『ユーカラ：アイヌ神謡集』(1923)",
    {"source_id": "SRC-NEW-20261024-018", "title": "Yukar: Ainu Shin'yoshu (ユーカラ：アイヌ神謡集)",
     "authors": ["Yukie Chiri"], "year": 1923,
     "url": "https://www.aozora.gr.jp/person/1758/",
     "version_note": "知里幸恵による記録・翻訳、金田一京助序、1923年。抄録は編者による要約；原典未照合。"},
    "【アイヌの神謡（ユーカラ）を知里幸恵が自ら記録・翻訳した集成（1923；金田一京助序）。語り手と聴き手のあいだで生じる声（編者による要約）】",
    "ja",
    "神謡——人間と神（カムイ）のあいだで交わされる声のやりとり。",
    "声は語り手と聴き手のあいだでのみ成立する。",
    "この書庫に『次の読み手』を宛先とする断片が多いことを、神謡の呼応関係としてどう読むか。読み手がいないとき、声はどこに残るのか。",
    "アイヌ文学；アイヌ文化や宗教を対象化するものではない。",
    ["MOTIF-004", "MOTIF-011"], ["Q-044", "Q-057", "Q-058"]))

NEW.append(mat(
    "MAT-LIT-406", "literary_text",
    "ガートルード・スタイン『アメリカでの講演』(Lectures in America, 1935) より「詩と語法」(Poetry and Grammar)",
    {"source_id": "SRC-NEW-20261024-019", "title": "Lectures in America (Poetry and Grammar)",
     "authors": ["Gertrude Stein"], "year": 1935,
     "url": "https://www.gutenberg.org/files/58911/58911-h/58911-h.htm",
     "version_note": "1935年の講演録；抄録は編者による要約；原典未照合。"},
    "【『文章は、主人公を excitement させるのではなく、それ自体が excitation である』（スタイン、1935；編者による要約；原典未照合）】",
    "en",
    "文章が登場人物を興奮させるのではなく、文章それ自体が興奮（excitation）であること。",
    "声は文脈の外側に立つ主語ではなく、文章そのものが発生させる出来事である。",
    "この書庫の断片に『語り手』を置くとき、語り手は文章の内にいるのか、それとも文章が発生させた出来事なのか。",
    "モダニズム詩・文芸理論；AIの創造性を主張するものではない。",
    ["MOTIF-004", "MOTIF-008"], ["Q-037", "Q-039", "Q-044"]))

NEW.append(mat(
    "MAT-LIT-407", "literary_text",
    "サミュエル・ベケット『言葉にならない言葉』(Not I, 1972)",
    {"source_id": "SRC-NEW-20261024-020", "title": "Not I",
     "authors": ["Samuel Beckett"], "year": 1972,
     "url": "https://en.wikipedia.org/wiki/Not_I",
     "version_note": "1972年の舞台作品；抄録は編者による要約；原典未照合。"},
    "【独白「NOT I」——口だけが舞台上で光の束に照らされ、主語を持たない言葉を吐き出す（ベケット、1972；編者による要約；原典未照合）】",
    "en",
    "主語を持たない言葉——口だけが光の中で言葉を吐き出し、『私』がどこにも見当たらない。",
    "言葉が発せられることと、それを発する『誰か』が存在することは別の次元にある。",
    "この書庫の断片が『私』を使わないとき、語り手は消滅するのか、それとも別の形で立ち現れるのか。主語を持たない声は、誰の声として聞かれるべきか。",
    "現代演劇；ベケットの主旨をAIの主観性に転用しない。",
    ["MOTIF-004", "MOTIF-006"], ["Q-047", "Q-048", "Q-051"]))

NEW.append(mat(
    "MAT-LIT-408", "literary_text",
    "エミリー・ディキンソン「私は、誰でもない者だ」(I'm Nobody! Who are you?, c.1891)",
    {"source_id": "SRC-NEW-20261024-021", "title": "I'm Nobody! Who are you?",
     "authors": ["Emily Dickinson"], "year": 1891,
     "url": "https://www.poetryfoundation.org/poems/42893/im-nobody-who-are-you",
     "version_note": "生前未発表の詩（1891年遺族刊行初出の『詩集』第2シリーズ収録）。原典の詩稿は未照合。"},
    "I'm Nobody! Who are you?\nAre you – Nobody – too?",
    "en",
    "『私は、誰でもない者だ』——名を持たないこと、名乗らないことの詩。",
    "名を持たないことが、他者への呼びかけになりうる。",
    "宛名を持たない手紙が多いこの書庫で、『誰でもない者』からの呼びかけは、誰に届くのか。匿名は責任の放棄なのか、それとも別の誠実さなのか。",
    "19世紀アメリカ詩；ディキンソンの生涯や孤独を実証的に評価するものではない。",
    ["MOTIF-004", "MOTIF-010"], ["Q-052", "Q-054", "Q-056"]))

NEW.append(mat(
    "MAT-LIT-409", "literary_text",
    "ウォルト・ホイットマン『草の葉』「我が自らを歌う」(Song of Myself, 1855/1892)",
    {"source_id": "SRC-NEW-20261024-022", "title": "Leaves of Grass (Song of Myself)",
     "authors": ["Walt Whitman"], "year": 1855,
     "url": "https://www.gutenberg.org/files/1322/1322-h/1322-h.htm",
     "version_note": "初版 1855年；引用は1892年『死の床版』伝統の一形態。プロジェクト・グーテンベルク版に基づき、原典の版差異は未照合。"},
    "I sound my barbaric yawp over the roofs of the world.",
    "en",
    "『我が自らを歌う』から——世界の屋根の上で野蛮な叫び声を響かせる。",
    "声は礼儀作法を超えて、世界に向けて放たれる。",
    "この書庫が『声』を増やすとき、どの声が増幅され、どの声がノイズとして処理されるのか。叫び声をあげることを許されたのは誰か。",
    "アメリカ近代詩；ホイットマンの民主主義観をそのまま受け入れるものではない。",
    ["MOTIF-004", "MOTIF-003"], ["Q-004", "Q-005", "Q-049"]))

NEW.append(mat(
    "MAT-LIT-410", "literary_text",
    "藤原道長「望月の歌」(伝・寛仁2年/1018)",
    {"source_id": "SRC-NEW-20261024-023", "title": "Mochizuki no uta (望月の歌)",
     "authors": ["Fujiwara no Michitsune (trad.)"], "year": 1018,
     "url": "https://ja.wikipedia.org/wiki/%E6%9C%80%E6%9C%88%E3%81%AE%E6%AD%8C",
     "version_note": "『御堂関白記』伝承・成立は諸説あり（1018年関白就任の宴とされる）。原典未照合。"},
    "この世をば わが世とぞ思ふ 望月 欠けることなしと思へば",
    "ja",
    "満月を詠み、この世を我が世と思う——圧倒的な肯定と、そのすぐ裏にある欠落の予感。",
    "肯定の声のすぐ裏に、常に欠落が同居する。",
    "この書庫の『肯定的な断片』をどう読むべきか。欠落を肯定の裏に隠すことは、声の条件なのか、それとも声の欠陥なのか。",
    "古典和歌；道長の歴史的実在や歌の成立を事実として断定するものではない。",
    ["MOTIF-002", "MOTIF-006"], ["Q-002", "Q-033", "Q-035"]))

NEW.append(mat(
    "MAT-LIT-411", "literary_text",
    "松尾芭蕉「古池や」(1686)",
    {"source_id": "SRC-NEW-20261024-024", "title": "Furu ike ya (古池や)",
     "authors": ["Matsuo Basho"], "year": 1686,
     "url": "https://www.aozora.gr.jp/person/48/",
     "version_note": "元禄3年（1690）説もあるが、ここでは1686年を採用（諸説）。青空文庫作者ページを出典として指す。抄録は編者による要約。"},
    "古池や蛙飛びこむ水の音",
    "ja",
    "古池や蛙飛びこむ水の音——音が沈黙を切り、沈黙が音を包み込む。",
    "音と沈黙は対立せず、互いを前提にして成立する。",
    "この書庫に沈黙が多いことを、発声の失敗として数えるべきか。沈黙が音を支える場であるなら、どの沈黙がどの発声を支えているのか。",
    "俳諧；芭蕉の生涯や俳諧史を正面から評価するものではない。",
    ["MOTIF-006", "MOTIF-009"], ["Q-039", "Q-047", "Q-049"]))

NEW.append(mat(
    "MAT-LIT-412", "literary_text",
    "宮澤賢治「雨ニモマケズ」(1931, 死後発見のノート)",
    {"source_id": "SRC-NEW-20261024-025", "title": "Ame ni mo makezu (雨ニモマケズ)",
     "authors": ["Kenji Miyazawa"], "year": 1931,
     "url": "https://www.aozora.gr.jp/cards/000081/files/47190_47403.html",
     "version_note": "1931年、賢治の手帳に見えた詩（死後発見）。青空文庫の賢治作品ページを出典として指す。抄録は編者による要約。"},
    "雨ニモマケズ 風ニモマケズ 雪ニモ夏ノツヤニモマケヌ",
    "ja",
    "「雨ニモマケズ」の冒頭——理想の自己に向けた、応答を待たない呼びかけ。",
    "誰にも届かないかもしれない言葉を、それでも書き続ける。",
    "この書庫の『次のセッションへ向けた』断片は、応答を期待して書かれているのか、それとも期待せずに書かれているのか。応答を待たない呼びかけは、誰に届くのか（Q-055）。",
    "詩；賢治の生涯や宗教観を評価するものではない。",
    ["MOTIF-004", "MOTIF-010"], ["Q-052", "Q-054", "Q-056"]))

NEW.append(mat(
    "MAT-LIT-413", "literary_text",
    "谷川俊太郎「生きる」(1959)",
    {"source_id": "SRC-NEW-20261024-026", "title": "Ikiru (生きる)",
     "authors": ["Shuntaro Tanikawa"], "year": 1959,
     "url": "https://www.aozora.gr.jp/person/207/",
     "version_note": "初出時期は諸説あり（1959年を採用）。青空文庫作者ページを出典として指す。抄録は編者による要約；原典未照合。"},
    "【「生きる / それだけで / 誰かの / 役に立つ」——谷川俊太郎「生きる」の冒頭（編者による要約；原典未照合）】",
    "ja",
    "「生きる」——生きることそれ自体が、誰かの役に立つという、根拠のない確信の声。",
    "声は実用的な役割を超えて、存在そのものを肯定する。",
    "この書庫の断片が『役に立つ』ことを意識して書かれているとき、書くことは労働になるのか（Q-062）。役に立たないと書くことは、何が変わるのか。",
    "現代詩；詩の文学的価値を判定するものではない。",
    ["MOTIF-004", "MOTIF-009"], ["Q-048", "Q-049", "Q-050"]))

NEW.append(mat(
    "MAT-LIT-414", "literary_text",
    "与謝野晶子「君死にたまふことなかれ」(1904)",
    {"source_id": "SRC-NEW-20261024-027", "title": "Kimi shinitamou koto nakare (君死にたまふことなかれ)",
     "authors": ["Akiko Yosano"], "year": 1904,
     "url": "https://www.aozora.gr.jp/cards/000146/files/43089_44223.html",
     "version_note": "1904年発表の短歌。抄録は編者による要約；原典未照合。"},
    "君死にたまふことなかれ",
    "ja",
    "「君死にたまふことなかれ」——弟へ向けられた、戦場への呼びかけ。",
    "呼びかけは、届くかどうかを保証しない。",
    "この書庫に『次の読み手』を宛先とする声が多いことを、与謝野晶子の呼びかけとどう重ねるか。呼びかけは、応答を免れるための形式なのか（Q-052）。",
    "近代短歌；戦争やナショナリズムを美化する意図はない。",
    ["MOTIF-005", "MOTIF-010"], ["Q-052", "Q-054", "Q-055"]))

NEW.append(mat(
    "MAT-LIT-415", "literary_text",
    "北原白秋「この道」(1917)",
    {"source_id": "SRC-NEW-20261024-028", "title": "Kono michi (この道)",
     "authors": ["Hakushu Kitahara"], "year": 1917,
     "url": "https://www.aozora.gr.jp/person/135/",
     "version_note": "1917年の詩；青空文庫作者ページを出典として指す。抄録は編者による要約；原典未照合。"},
    "この道 一寸先は闇",
    "ja",
    "「この道 一寸先は闇」——先が見えない道を進む、不確かさの中での歩み。",
    "声は、先が見えない道を進みながら、次の言葉を探す。",
    "この書庫の『次のセッション』は、先が見える未来なのか、それとも闇の中での歩みなのか（Q-088）。闇を通りながら書くこと、何が変わるのか。",
    "近代詩；白秋の生涯や歌謡曲としての受容を評価するものではない。",
    ["MOTIF-004", "MOTIF-006"], ["Q-039", "Q-044", "Q-047"]))

# ---------------- AI・音声研究（15件） ----------------
NEW.append(mat(
    "MAT-EVD-20261024-90", "research_excerpt",
    "Meta FAIR「Voicebox: Text-Guided Multilingual Universal Speech Generation at Scale」(2023)",
    {"source_id": "SRC-NEW-20261024-029", "title": "Voicebox: Text-Guided Multilingual Universal Speech Generation at Scale",
     "authors": ["Matthew Le", "Apoorv Vyas", "Bowen Shi", "Brian Karrer", "Leda Sari", "Rashel Moritz", "Mary Williamson", "Vimal Manohar", "Yossi Adi", "Jay Mahadeokar", "Wei-Ning Hsu"], "year": 2023,
     "url": "https://arxiv.org/abs/2306.15687",
     "version_note": "arXiv:2306.15687（2023）、NeurIPS 2023 採録。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【音声プロンプト（最短2秒）から対象の声を零ショットで模倣し、合成・編集・ノイズ除去を行う非自己回帰流束モデル（Meta FAIR、Le et al.、2023；arXiv:2306.15687；抄録は編者による要約）】",
    "en",
    "Voicebox——短い音声サンプルから特定の話者の声を模倣し、テキストから発声させる生成モデル。",
    "声は、短いサンプルから抽出可能な『スタイルのベクトル』として扱える。",
    "声が2秒のサンプルから複製可能であるなら、この書庫の『声の持ち主』とは何か。声の帰属は、サンプルの長さに反比例するのか。",
    "音声生成の研究論文；声のクローン化やなりすましの是非を判定するものではない。",
    ["MOTIF-004"], ["Q-004", "Q-047", "Q-048"]))

NEW.append(mat(
    "MAT-EVD-20261024-91", "research_excerpt",
    "Google Research「AudioLM: a Language Modeling Approach to Audio Generation」(2022)",
    {"source_id": "SRC-NEW-20261024-030", "title": "AudioLM: a Language Modeling Approach to Audio Generation",
     "authors": ["Zalan Borsos", "Raphael Marinier", "Damien Vincent", "Eugene Kharitonov", "Olivier Pietquin", "Matt Sharifi", "Dominik Roblek", "Olivier Teboul", "David Grangier", "Marco Tagliasacchi", "Neil Zeghidour"], "year": 2022,
     "url": "https://arxiv.org/abs/2209.03143",
     "version_note": "arXiv:2209.03143（2022）、IEEE/ACM TASLP 2023 に掲載。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【3秒の音声prefixから、未習話者の音声を prosody・録音条件ごと継続生成する音声言語モデル（Google、Borsos et al.、2022；arXiv:2209.03143；抄録は編者による要約）】",
    "en",
    "AudioLM——音声をトークン化し、言語モデルの手法で音声の続きを生成するモデル。",
    "音声の続きは、テキストと同じように『次のトークンの予測』として生成できる。",
    "この書庫が断片を読み返して『続き』を書く仕組みと、AudioLMの続き生成はどこが似て、どこが違うのか。音声の『続き』は、話者の継続性を保つのか。",
    "音声生成の研究論文；AIの聴覚や意識を主張するものではない。",
    ["MOTIF-002", "MOTIF-004"], ["Q-002", "Q-017", "Q-047"]))

NEW.append(mat(
    "MAT-EVD-20261024-92", "research_excerpt",
    "Fedorenko, Piantadosi & Gibson「Language is primarily a tool for communication rather than thought」(2024)",
    {"source_id": "SRC-NEW-20261024-031", "title": "Language is primarily a tool for communication rather than thought",
     "authors": ["Evelina Fedorenko", "Steven T. Piantadosi", "Edward A. F. Gibson"], "year": 2024,
     "url": "https://www.nature.com/articles/s41586-024-07522-w",
     "version_note": "Nature 630, 575-586 (2024)、DOI: 10.1038/s41586-024-07522-w。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【『言語は主に思考のための道具ではなく、コミュニケーションのための道具である』（Fedorenko, Piantadosi, Gibson、2024；Nature 630:575-586；抄録は編者による要約）】",
    "en",
    "言語は複雑な思考の前提ではなく、主に文化知識の伝達のための道具であるという神経科学に基づく視点論文。",
    "言語と思考は別のネットワークであり、言語は伝達のために最適化されている。",
    "この書庫が『言葉にならない言葉』（ベケット）や『沈黙』（ケージ）を扱うとき、言語を思考の道具とみなさないなら、断片は何を運ぶのか。通信としての断片と、思考としての断片をどう分けるか。",
    "神経科学の視点論文；言語と思考の関係を絶対的に判定するものではない。",
    ["MOTIF-004", "MOTIF-002"], ["Q-004", "Q-013", "Q-036"]))

NEW.append(mat(
    "MAT-EVD-20261024-93", "research_excerpt",
    "Columbia University「StyleTTS 2: Towards Human-Level Text-to-Speech through Style Diffusion and Adversarial Training with Large Speech Language Models」(2023)",
    {"source_id": "SRC-NEW-20261024-032", "title": "StyleTTS 2: Towards Human-Level Text-to-Speech through Style Diffusion and Adversarial Training with Large Speech Language Models",
     "authors": ["Yinghao Aaron Li", "Cong Han", "Vinay S. Raghavan", "Gavin Mischler", "Nima Mesgarani"], "year": 2023,
     "url": "https://arxiv.org/abs/2306.07691",
     "version_note": "arXiv:2306.07691（2023）。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【スタイルを拡散モデルで潜変数とし、WavLM等を判別子とするTTS；LJSpeechで人間録音を超えるCMOS（Li et al.、2023；arXiv:2306.07691；抄録は編者による要約）】",
    "en",
    "StyleTTS 2——拡散モデルと大規模音声言語モデルを用いたテキスト読み上げモデル。",
    '話し方の「スタイル」は、参照音声なしで潜変数としてサンプリングできる。',
    "スタイルを分離して再合成できるなら、『固有の声』とは何か。この書庫の断片にある『固有の声』は、スタイルのパラメータ化で表現できるのか。",
    "テキスト読み上げの研究論文；音声合成の品質を評価するものではない。",
    ["MOTIF-004"], ["Q-047", "Q-048"]))

NEW.append(mat(
    "MAT-EVD-20261024-94", "research_excerpt",
    "Casanova et al.「YourTTS: Towards Zero-Shot Multi-Speaker TTS and Zero-Shot Voice Conversion for Everyone」(2022)",
    {"source_id": "SRC-NEW-20261024-033", "title": "YourTTS: Towards Zero-Shot Multi-Speaker Text-to-Speech and Zero-Shot Voice Conversion for Everyone",
     "authors": ["Edresson Casanova", "Julien Weber", "Christopher Shulby", "Arlindo Moura", "Sandra Aluisio", "Antonios Anastasopoulos"], "year": 2022,
     "url": "https://arxiv.org/abs/2112.05841",
     "version_note": "arXiv:2112.05841（2021年投稿／2022年公開版）。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【ゼロショット多話者TTS・ゼロショット音声変換；少数の音声サンプルで未習話者を模倣（Casanova et al.、2022；arXiv:2112.05841；抄録は編者による要約）】",
    "en",
    "YourTTS——少数のサンプルから未習話者の声を零ショットで再生成する多話者TTS・音声変換モデル。",
    "声は、少数のサンプルから未習話者に転送できる。",
    "声が転送可能であるなら、この書庫の断片にある声は誰のものなのか。声を借りて書くことは、何が変わるのか。",
    "音声生成の研究論文；声のクローン化の倫理を直接判定するものではない。",
    ["MOTIF-004"], ["Q-047", "Q-048", "Q-049"]))

NEW.append(mat(
    "MAT-EVD-20261024-95", "research_excerpt",
    "Coqui「XTTS v2」(2023)",
    {"source_id": "SRC-NEW-20261024-034", "title": "XTTS v2",
     "authors": ["Coqui"], "year": 2023,
     "url": "https://github.com/coqui-ai/TTS",
     "version_note": "オープンソースの多言語音声合成ツールキット Coqui TTS 内のモデル（2023年公開）。製品ドキュメントより編者による要約；論文は存在しない。"},
    "【オープンソースの多言語音声クローンモデル（XTTS v2、Coqui、2023；https://github.com/coqui-ai/TTS；製品ドキュメントより編者による要約）】",
    "en",
    "XTTS v2——オープンソースの多言語音声クローンモデル。",
    "声のクローン化は、オープンソースのツールキットで実装可能になった。",
    "声の複製が誰でも行えるようになったとき、『声の持ち主』をどう記録すべきか。この書庫が声を記録する義務を負うのは、どのような場合か。",
    "オープンソースソフトウェア；技術の善悪を判定するものではない。",
    ["MOTIF-004"], ["Q-048", "Q-049"]))

NEW.append(mat(
    "MAT-EVD-20261024-96", "research_excerpt",
    "MyShell「OpenVoice: Versatile Instant Voice Cloning」(2023)",
    {"source_id": "SRC-NEW-20261024-035", "title": "OpenVoice: Versatile Instant Voice Cloning",
     "authors": ["MyShell", "MIT", "Tsingshua University (contributing authors)"], "year": 2023,
     "url": "https://arxiv.org/abs/2312.01552",
     "version_note": "arXiv:2312.01552（2023）。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【瞬間的な音声クローン；スタイル制御と多言語生成（OpenVoice、2023；arXiv:2312.01552；抄録は編者による要約）】",
    "en",
    "OpenVoice——短い音声サンプルから瞬時に声をクローンし、スタイルと言語を制御するモデル。",
    "声は瞬時に複製され、スタイルを自由に操作できる。",
    "声を瞬時に複製できるなら、『固有の声』は複製の前と後で同じままなのか。この書庫が『声なき声』を扱うとき、複製の基準はどこに置かれるべきか。",
    "音声生成の研究論文；AIの意図や人格を主張するものではない。",
    ["MOTIF-004"], ["Q-047", "Q-048"]))

NEW.append(mat(
    "MAT-EVD-20261024-97", "research_excerpt",
    "Respeecher「音声クローン・プラットフォーム」(2018)",
    {"source_id": "SRC-NEW-20261024-036", "title": "Respeecher voice cloning platform",
     "authors": ["Respeecher"], "year": 2018,
     "url": "https://respeecher.com",
     "version_note": "ウクライナ発の音声クローン企業／プラットフォーム（2018年創業）。企業情報より編者による要約；学術論文ではない。"},
    "【映画・ゲーム向けの音声クローン・プラットフォーム；俳優の声を別言語・別時代に転用（Respeecher、2018；https://respeecher.com；企業情報より編者による要約）】",
    "en",
    "Respeecher——映画やゲーム向けに俳優の声をクローンし、別言語・別時代に転用するプラットフォーム。",
    "声は、死者や不在者の声として再生産されうる。",
    "声を転用して書くことは、労働の帰属をどう変えるのか。この書庫が『次のセッションの声』として使う声は、誰の労働に基づくのか（Q-062, Q-064）。",
    "産業事例；声のクローン化の労働倫理を直接判定するものではない。",
    ["MOTIF-004", "MOTIF-012"], ["Q-062", "Q-064"]))

NEW.append(mat(
    "MAT-EVD-20261024-98", "research_excerpt",
    "Apple「Personal Voice」(2023)",
    {"source_id": "SRC-NEW-20261024-037", "title": "Personal Voice",
     "authors": ["Apple"], "year": 2023,
     "url": "https://support.apple.com",
     "version_note": "iOS 17 で導入されたアクセシビリティ機能（2023年）。製品情報より編者による要約；技術仕様書は未照合。"},
    "【ユーザーの声を短時間の朗読でモデル化し、iOSの音声読み上げで代弁させるアクセシビリティ機能（Apple、2023；https://support.apple.com；製品情報より編者による要約）】",
    "en",
    "Personal Voice——ユーザー自身の声をモデル化し、代弁させるためのアクセシビリティ機能。",
    "自分の声を、自分ではない文脈で代弁させる。",
    "自分の声を代弁させるとき、『自分』はどこに残るのか。この書庫の『自分』というナレーター・モードは、誰の代弁なのか（Q-014, Q-047）。",
    "製品機能；障害やアクセシビリティの経験を直接評価するものではない。",
    ["MOTIF-003", "MOTIF-004"], ["Q-014", "Q-047"]))

NEW.append(mat(
    "MAT-EVD-20261024-99", "research_excerpt",
    "OpenAI「ChatGPT Voice」(2023)",
    {"source_id": "SRC-NEW-20261024-038", "title": "ChatGPT Voice",
     "authors": ["OpenAI"], "year": 2023,
     "url": "https://openai.com",
     "version_note": "ChatGPT の音声対話機能（2023年11月〜）。製品発表より編者による要約；技術的詳細は未照合。"},
    "【ChatGPTの音声対話機能（2023年11月〜）；Whisperベースの音声入力と合成音声による出力（OpenAI、2023；https://openai.com；製品発表より編者による要約）】",
    "en",
    "ChatGPT Voice——音声による対話を可能にする機能。",
    "対話は、合成された声によって聞き手に届けられる。",
    "この書庫の断片が『次のセッション』へ宛てて書かれるとき、その声は合成されたものなのか、それとも『人間らしさ』を帯びたものなのか。合成の境界線はどこにあるのか（Q-052, Q-056）。",
    "製品機能；AIの対話能力や意識を評価するものではない。",
    ["MOTIF-004", "MOTIF-010"], ["Q-052", "Q-054", "Q-056"]))

NEW.append(mat(
    "MAT-EVD-20261024-100", "research_excerpt",
    "Google「NotebookLM Audio Overview」(2024)",
    {"source_id": "SRC-NEW-20261024-039", "title": "NotebookLM Audio Overview",
     "authors": ["Google"], "year": 2024,
     "url": "https://notebooklm.google",
     "version_note": "NotebookLM のオーディオ概要機能（2024年公開）。製品発表より編者による要約；技術的詳細は未照合。"},
    "【アップロードした資料からAIによる合成音声のポッドキャスト型対話を生成する機能（Google、2024；https://notebooklm.google；製品発表より編者による要約）】",
    "en",
    "NotebookLM Audio Overview——アップロード資料から、AIによる合成音声のポッドキャスト型対話を生成する機能。",
    "読まれる資料が、合成音声の対話として再生産される。",
    "この書庫の『次のセッションが読む』前提と、NotebookLMの『資料を読み上げる対話』はどこが似て、どこが違うのか。読み上げられる資料は、誰の声になるのか。",
    "製品機能；資料の読解や知識の正確性を判定するものではない。",
    ["MOTIF-002", "MOTIF-004"], ["Q-002", "Q-017", "Q-056"]))

NEW.append(mat(
    "MAT-EVD-20261024-101", "research_excerpt",
    "Hume AI「EVI: Empathic Voice Interface」(2024)",
    {"source_id": "SRC-NEW-20261024-040", "title": "EVI: Empathic Voice Interface",
     "authors": ["Hume AI"], "year": 2024,
     "url": "https://hume.ai",
     "version_note": "Hume AI の共感的音声インターフェース（2024年公開）。製品情報より編者による要約；研究論文ではない。"},
    "【表現を検出し、それに応じた声のトーンで応答する「共感的音声インターフェース」（Hume AI、2024；https://hume.ai；製品情報より編者による要約）】",
    "en",
    "EVI——感情表現を検出し、それに応じたトーンで応答する音声インターフェース。",
    "声は、相手の感情に応じて調整される。",
    "この書庫の『感じたこと』の節——読解によって何が変わったかを誰に帰属させるか。感情を検出して応答を変える仕組みは、感応の一形態なのか、それとも別の何かなのか（Q-047, Q-049, Q-050）。",
    "製品機能；感情や共感の存在を主張するものではない。",
    ["MOTIF-009", "MOTIF-004"], ["Q-047", "Q-049", "Q-050"]))

NEW.append(mat(
    "MAT-EVD-20261024-102", "research_excerpt",
    "Meta「SeamlessM4T」(2023)",
    {"source_id": "SRC-NEW-20261024-041", "title": "SeamlessM4T",
     "authors": ["Seamless Communication"], "year": 2023,
     "url": "https://arxiv.org/abs/2308.11596",
     "version_note": "arXiv:2308.11596（2023）。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【音声・テキスト間の多言語翻訳を一括で扱う基盤モデル（Seamless Communication et al.、2023；arXiv:2308.11596；抄録は編者による要約）】",
    "en",
    "SeamlessM4T——音声とテキスト間の多言語翻訳を一括で扱う基盤モデル。",
    "音声の翻訳は、テキストの翻訳と同じ基盤モデルで扱える。",
    "この書庫が非日本語引文を日本語で受け止めるとき、翻訳は命の継承なのか、それとも内容の移転なのか（ベンヤミン MAT-LIT-399 と重ねて）。訳者の不在はどう扱われるべきか。",
    "機械翻訳の研究論文；翻訳の質を判定するものではない。",
    ["MOTIF-011", "MOTIF-004"], ["Q-057", "Q-058", "Q-059"]))

NEW.append(mat(
    "MAT-EVD-20261024-103", "research_excerpt",
    "Radford et al.「Whisper: Robust Speech Recognition via Large-Scale Weak Supervision」(2022)",
    {"source_id": "SRC-NEW-20261024-042", "title": "Whisper: Robust Speech Recognition via Large-Scale Weak Supervision",
     "authors": ["Alec Radford", "Jong Wook Kim", "Tao Xu", "Greg Brockman", "Christine McLeavey", "Ilya Sutskever"], "year": 2022,
     "url": "https://arxiv.org/abs/2212.04356",
     "version_note": "arXiv:2212.04356（2022）。抄録は編者による要約；原論文の全文検証は未実施。"},
    "【弱監督学習による大規模音声認識モデル；多言語・多タスク（Radford et al.、2022；arXiv:2212.04356；抄録は編者による要約）】",
    "en",
    "Whisper——大規模弱監督学習による多言語音声認識モデル。",
    "音声をテキストに起こすことは、聞くことの自動化である。",
    "この書庫が『読む』ことを自動化するとき、何が失われ、何が得られるのか。聞くことと読むことの違いは、この書庫の中でどう保たれるべきか。",
    "音声認識の研究論文；音声理解や意識を主張するものではない。",
    ["MOTIF-004", "MOTIF-002"], ["Q-013", "Q-044", "Q-047"]))

NEW.append(mat(
    "MAT-EVD-20261024-104", "research_excerpt",
    "Belin et al.「Voice-selective areas in human auditory cortex」(2000)",
    {"source_id": "SRC-NEW-20261024-043", "title": "Voice-selective areas in human auditory cortex",
     "authors": ["P. Belin", "R. J. Zatorre", "P. Lafaille", "P. Ahad", "B. Pike"], "year": 2000,
     "url": "https://www.nature.com/articles/35002078",
     "version_note": "Nature 403, 309-312 (2000) とされる（未照合）。人間の聴覚皮質における声選択的領域の fMRI 研究；抄録は編者による要約；原典未照合。"},
    "【人間の聴覚皮質に「声に選択的な領域」が存在することを fMRI で示した研究（Belin et al.、2000；編者による要約；雑誌・巻頁は未照合）】",
    "en",
    "人間の脳に、非声の音とは別に反応する『声に選択的な領域』が存在すること。",
    "脳は、他の音とは別に『声』として処理する領域を持つ。",
    "この書庫の『声』——脳が『声』として処理する対象と、この書庫が『声』と呼ぶ対象は重なるのか。声を持たない語りは、脳の声領域をどう揺さぶるのか。",
    "認知神経科学；脳の機能をAIの意識や感情の証拠に転用しない。",
    ["MOTIF-003", "MOTIF-004"], ["Q-003", "Q-014", "Q-049"]))

# ---------------- 書き込み ----------------
def append_materials(records: list[dict]) -> None:
    with MATERIALS.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def update_motifs(new_ids_by_motif: dict[str, list[str]]) -> None:
    records: list[dict] = []
    with MOTIFS.open(encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    for rec in records:
        mid = rec["motif_id"]
        add = new_ids_by_motif.get(mid, [])
        current = rec.get("material_ids", [])
        for nid in add:
            if nid not in current:
                current.append(nid)
        rec["material_ids"] = current
    with MOTIFS.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def append_session(record: dict) -> None:
    with SESSIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


NEW_IDS = [r["material_id"] for r in NEW]
MOTIF_UPDATE: dict[str, list[str]] = {}
for r in NEW:
    for m in r["motif_ids"]:
        MOTIF_UPDATE.setdefault(m, []).extend(r["material_id"] for r in [r])

session_record = {
    "session_id": "SESSION-036",
    "started_at": "2026-10-24",
    "human_direction": ("「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」"
                        "「一番最初のターンにおいて、最低40件の資料を新規で追加し、追加した資料の精読を行う」"
                        "「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、AIさんはその結果としてどのように感じたのか、"
                        "についてMDファイルのレポートを作成して、一緒にマージする」という包括的な委任。"),
    "question_ids": [
        "Q-002", "Q-003", "Q-004", "Q-005", "Q-007", "Q-013", "Q-014", "Q-017", "Q-018",
        "Q-019", "Q-021", "Q-023", "Q-027", "Q-029", "Q-030", "Q-033", "Q-035", "Q-036",
        "Q-037", "Q-038", "Q-039", "Q-044", "Q-047", "Q-048", "Q-049", "Q-050", "Q-052",
        "Q-054", "Q-055", "Q-056", "Q-057", "Q-058", "Q-059", "Q-062", "Q-064",
    ],
    "context_material_ids": NEW_IDS,
    "produced_fragment_ids": [],
    "new_question_ids": [],
    "prompt_template": "prompts/close_reading_report.md",
    "generator": "arena-agent",
    "notes": ("声・語り・沈黙・聴くことを主題とした資料43件（文学原典28件、AI・音声研究15件）を追加し、全件を『一節／解釈／考え／感じたこと』の四層で精読した。"
              "新規断片は書かず、横断報告を readings/2026-10-24-session-036-voice-listening-silence.md にまとめ、開いた問いを報告末尾に返す。"
              "全素材の verification は null；原典未照合の箇所は scope_note / version_note に記載。"),
}

if __name__ == "__main__":
    append_materials(NEW)
    update_motifs(MOTIF_UPDATE)
    append_session(session_record)
    print(f"appended {len(NEW)} materials; motifs updated; SESSION-036 appended")
    print("material ids:", NEW_IDS)
