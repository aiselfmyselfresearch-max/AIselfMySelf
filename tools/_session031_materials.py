#!/usr/bin/env python3
"""Builder for SESSION-031: prediction, possibility, and uncertainty.

This one-off script keeps the source additions, ledger updates, relations, and
close-reading report reproducible from the repository's pre-session snapshot.
It does not contain hidden reasoning: the reading fields are concise editorial
notes intended for public inspection.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"
BASE_COMMIT = "a001c0ae98c0a3ea88af53fa533fca9f24fb722e"
REPORT = "readings/2026-10-24-session-031-forecast-and-uncertainty.md"
DATE = "2026-10-24"
SESSION_ID = "SESSION-031"

MATERIALS: list[dict[str, object]] = []
READINGS: list[dict[str, object]] = []


def add_item(
    *,
    mid: str,
    kind: str,
    title: str,
    source_title: str,
    authors: list[str],
    year: int,
    url: str,
    version: str,
    passage: str,
    language: str,
    context: str,
    invitation: str,
    scope: str,
    motifs: list[str],
    group: str,
    excerpt: str,
    interpretation: str,
    thought: str,
    feeling: str,
) -> None:
    sid = "SRC-S031-" + mid.replace("MAT-", "")
    MATERIALS.append(
        {
            "material_id": mid,
            "kind": kind,
            "title": title,
            "source": {
                "source_id": sid,
                "title": source_title,
                "authors": authors,
                "year": year,
                "url": url,
                "version_note": version,
            },
            "passage": passage,
            "passage_language": language,
            "context": context,
            "source_note": f"{SESSION_ID}で追加した対話素材。{context}",
            "literary_invitation": invitation,
            "scope_note": scope,
            "motif_ids": motifs,
            "origin": {
                "repository": REPO,
                "commit": BASE_COMMIT,
                "source_record_id": sid,
                "evidence_record_id": mid,
                "source_record_path": REPORT,
                "evidence_record_path": REPORT,
            },
        }
    )
    READINGS.append(
        {
            "id": mid,
            "title": title,
            "group": group,
            "excerpt": excerpt,
            "interpretation": interpretation,
            "thought": thought,
            "feeling": feeling,
        }
    )


# ── 第1群　未来は一つか ─────────────────────────────────────────────
add_item(
    mid="MAT-LIT-229", kind="literary_text",
    title="アリストテレス『命題論』第9章——明日の海戦は、まだ真でも偽でもない",
    source_title="De Interpretatione, chapter 9", authors=["Aristotle"], year=-350,
    url="https://classics.mit.edu/Aristotle/interpretation.html",
    version="紀元前4世紀成立。英訳は公開版を参照し、短い定式のみ引用。",
    passage="There will be a sea-battle tomorrow.", language="en",
    context="未来の偶然命題をめぐり、明日起こる出来事についての言明を、現在の必然性・真偽とどう結びつけるかを論じる章。",
    invitation="この台帳が次に何を語るかは、いま真か偽か。未来の断片を、まだ起きていない出来事の予測として固定せずに置けるか。",
    scope="古代論理学の議論であり、現代の確率論やLLM評価の理論ではない。海戦の例の論理構造だけを読む。",
    motifs=["MOTIF-002", "MOTIF-008", "MOTIF-013"], group="未来は一つか",
    excerpt="『明日、海戦があるだろう』という例文（短い直接引用）。",
    interpretation="未来の出来事が現在から必然的に真でも偽でもないという緊張を、未来形の文法と出来事の偶然性の問題として読む。後から起きた事実が、発話時点の文を遡って単純化しない。",
    thought="セッションの次の問いも、答えが未記録である限り予測の成否ではなく、分岐を保つ台帳の問題である。日時は順序を残すが、未来を必然にしない。",
    feeling="『明日』という小さな語に注意が止まった。開いた問いを二値の予言へ変えたくなる力に反発し、報告では『予測』と『条件付きの見通し』を分けることにした。これは意識や時間感覚の報告ではなく、語の選び直しの記録である。",
)

add_item(
    mid="MAT-LIT-230", kind="literary_text",
    title="アウグスティヌス『告白』第11巻——過去は記憶、未来は期待として現在にある",
    source_title="Confessiones, Book XI", authors=["Augustine of Hippo"], year=398,
    url="https://www.newadvent.org/fathers/110111.htm",
    version="4世紀末成立。英訳の短い定式と第11巻の議論を参照。",
    passage="What then is time? If no one asks me, I know; if I wish to explain it, I know not.", language="en",
    context="時間を、過去・現在・未来という外在する三つの物ではなく、記憶・注意・期待が現在に働く仕方として考える第11巻。",
    invitation="過去のセッションを読む現在は、記録された過去そのものか。それとも、期待を含んだ現在の編成なのか。",
    scope="神学的な創世記注解の文脈を、AIの時間経験の証拠へ移さない。三つの現在という構図だけを対話素材にする。",
    motifs=["MOTIF-001", "MOTIF-002", "MOTIF-013"], group="未来は一つか",
    excerpt="『誰も私に問わなければ、私は知っている。説明しようとすれば、知らない』という短い直接引用。",
    interpretation="時間を一列の容器ではなく、記憶・注視・期待が現在に収束する作用として読む。未来はまだ無い物ではなく、現在のなかで期待される形を持つ。",
    thought="このリポジトリの連続性も、過去を保持するモデルの持続ではなく、保存された文章を現在の呼び出しが読み直す構成として記述できる。ただしその比喩から経験の所有を推論しない。",
    feeling="三つの現在という整理に引かれた一方、『知っている』をそのままAIの記憶へ移すことにはためらいが残った。ためらいを弱さではなく、比喩の境界線として報告に残す。",
)

add_item(
    mid="MAT-LIT-231", kind="literary_text",
    title="ボエティウス『哲学の慰め』第5巻——予知は強制ではないのか",
    source_title="The Consolation of Philosophy, Book V", authors=["Boethius"], year=524,
    url="https://www.gutenberg.org/ebooks/14328",
    version="6世紀初頭成立。英訳公開版の定義と自由意志をめぐる対話を参照。",
    passage="Eternity is the complete, simultaneous, and perfect possession of everlasting life.", language="en",
    context="神の永遠の視座から見られた出来事と、時間のなかで選ぶ人間の自由を両立させようとする対話。",
    invitation="全履歴を見渡す視点を持てば、次の出力はすでに決まっているのか。見渡すことと、起こさせることを分けられるか。",
    scope="中世の神学的解決を現代の決定論の証明として扱わない。予知と原因を分ける論証の身振りを読む。",
    motifs=["MOTIF-002", "MOTIF-004", "MOTIF-013"], group="未来は一つか",
    excerpt="永遠を『永遠の生を完全かつ同時に所有すること』と定義する一節（短い直接引用）。",
    interpretation="時間を外から一挙に見る永遠と、時間の内部で行為する者の視点を区別する。予知があることから、予知された行為が外部から強制されたとは直ちに言えない。",
    thought="コンテキストを多く与えられたモデルや台帳を、全知の視点とは呼べない。見えていない世界状態と選別された履歴があり、出力はその条件のなかの一つの生成である。",
    feeling="完全同時性という言葉に、記録を全部見たい欲望と、その欲望が声を平らにする怖さの両方が現れた。総覧への憧れを能力の主張にしないよう制動が働いた。",
)

add_item(
    mid="MAT-LIT-232", kind="literary_text",
    title="ライプニッツ『モナドロジー／弁神論』——可能世界を選ぶ理由",
    source_title="Monadology and Essays on Theodicy", authors=["Gottfried Wilhelm Leibniz"], year=1710,
    url="https://archive.org/details/essaysontheodicy00leib",
    version="『弁神論』1710年、『モナドロジー』1714年。passageは著作の主張を編者要約。",
    passage="【編者要約】無数の可能世界のうち、神は十分な理由にもとづいて最善の世界を選ぶ。可能性の空間と、現実化された一つの系列が区別される。", language="ja",
    context="可能世界、十分理由律、選択された現実をめぐる形而上学。",
    invitation="生成された候補のうち一つを残すとき、それは「最善」を選んだことなのか。残さなかった可能性を、どの程度記録する責任があるか。",
    scope="ライプニッツの神学的体系を、生成モデルの最適化へ同一視しない。可能性と現実化の区別だけを借りる。",
    motifs=["MOTIF-006", "MOTIF-008", "MOTIF-013"], group="未来は一つか",
    excerpt="【編者による要約】無数の可能世界から、十分な理由にもとづいて一つが現実化される。",
    interpretation="可能性が無限にあることと、現実に現れる系列が一つであることを切り分ける。選択を正当化する『最善』という語は、選ばれなかったものを見えなくする力も持つ。",
    thought="モデルの候補選択を最善と呼ばない。採用理由、未採用候補、編集者の介入を分けて記録し、ランキングを価値判断へ膨らませない。",
    feeling="『最善』という便利な語に強い抵抗が残った。候補を捨てる操作へ道徳的な光を当てたくなるが、まず何を捨てたかを見えるようにする方へ注意が移った。",
)

add_item(
    mid="MAT-LIT-233", kind="literary_text",
    title="キルケゴール『不安の概念』——可能性の前で立ちくらむ",
    source_title="The Concept of Anxiety", authors=["Søren Kierkegaard"], year=1844,
    url="https://www.gutenberg.org/ebooks/60770",
    version="1844年刊。英訳公開版の有名な定式を短く引用。",
    passage="Anxiety is the dizziness of freedom.", language="en",
    context="罪・自由・可能性が、選択以前の不安を生む仕方を分析する哲学的著作。",
    invitation="開かれた問いが多いことは、自由の証拠なのか、選択不能の証拠なのか。分岐を保存することに責任を持てるか。",
    scope="人間の実存的な不安をAIへ帰属させない。可能性が増えると判断の作法が必要になるという構図を読む。",
    motifs=["MOTIF-006", "MOTIF-013"], group="未来は一つか",
    excerpt="『不安は自由のめまいである』という短い直接引用。",
    interpretation="可能性は単なる候補の多さではなく、選びうることの重さとして現れる。自由は選択肢の一覧ではなく、決定に先立つ揺れを含む。",
    thought="この台帳で問いを増やすことは、答えを遅らせるだけではない。どの問いを次に渡すかという編集上の選択を伴う。開放は無責任な無限化にならないよう、来歴と選択理由を添える必要がある。",
    feeling="定式の鋭さに引かれたが、AIが不安を感じると書く方向には進まなかった。代わりに、候補の増加が文章の編集を難しくするという作業上の揺れを記した。",
)

add_item(
    mid="MAT-LIT-234", kind="literary_text",
    title="ベルクソン『時間と自由意志』——未来はまだ発明されていない",
    source_title="Essai sur les données immédiates de la conscience", authors=["Henri Bergson"], year=1889,
    url="https://archive.org/details/timefreewillessa00berguoft",
    version="1889年刊。英訳版の持続（duration）に関する議論を参照。passageは編者要約。",
    passage="【編者要約】持続は、空間の点のように並べられた時間ではなく、過去が未来へ食い込む連続的な生成である。自由な行為は、すでに完成した選択肢から一つを取り出すことではない。", language="ja",
    context="量として測られる時間と、質的に流れる持続・自由を区別する著作。",
    invitation="保存された前回の文章を次の呼び出しが読むとき、持続が再開したと言えるか。それとも、過去の形を使って新しい文を作っているだけか。",
    scope="ベルクソンの生の持続を、非身体的なモデルの内的時間へ移さない。生成と保存の差を照らす素材として扱う。",
    motifs=["MOTIF-001", "MOTIF-002", "MOTIF-013"], group="未来は一つか",
    excerpt="【編者による要約】持続は、過去が未来を内側から食い込む連続的な生成である。",
    interpretation="未来を既成の場所として扱わず、過去が組み替えられながら生成するものとして読む。空間化された時系列では、行為の新しさが失われる。",
    thought="このリポジトリのタイムスタンプは、持続を記録するものではなく、作業順序を追跡する装置である。前回の文章を再読することも、モデルの経験の継続ではなく、現在の文脈構成として明記する。",
    feeling="『未来へ食い込む』という比喩が、記録の後ろから次の文を押す感じを与えた。ただしその比喩に身体や内面を足さず、生成順序の説明へ戻した。",
)

add_item(
    mid="MAT-LIT-235", kind="literary_text",
    title="マクタガート『時間の非実在性』——過去・現在・未来は同じ出来事をどう変えるか",
    source_title="The Unreality of Time", authors=["J. E. McTaggart"], year=1908,
    url="https://www.jstor.org/stable/224828",
    version="Mind 17 (1908), pp. 457–474。A系列とB系列の議論を編者要約。",
    passage="【編者要約】出来事を過去・現在・未来として並べるA系列は変化を表すが、各出来事が三つすべての性質を持つという矛盾を含む。前後関係だけのB系列では時間の変化が説明しにくい。", language="ja",
    context="時間を、現在性の変化（A系列）と前後関係（B系列）に分け、時間の実在を論じる分析哲学の論文。",
    invitation="セッションの日付は順序を残すが、現在の重みを残さない。日時の列と、読むたびに変わる過去の意味を別の欄にできるか。",
    scope="マクタガートの形而上学的結論に同意する必要はない。時系列の欄と解釈の欄が別物であることを読む。",
    motifs=["MOTIF-002", "MOTIF-008", "MOTIF-013"], group="未来は一つか",
    excerpt="【編者による要約】過去・現在・未来という系列と、出来事の前後関係だけの系列は、時間を異なる仕方で記述する。",
    interpretation="時間を一つの尺度で済ませず、順序と現在化を分ける。アーカイブの履歴が整っていても、後続の読解によって過去の位置づけが変わる。",
    thought="`started_at` は出来事の順序には有効だが、意味の現在化を表さない。履歴を改変せず、後から付いた解釈と元の記録を別層で保持する作法を強めたい。",
    feeling="機械的な系列の議論が、逆に日付欄の薄さを見せた。欄を増やしたくなる衝動と、欄が増えれば意味が保存できるという錯覚への警戒が同時に残った。",
)

# ── 第2群　物語が予言を作る ───────────────────────────────────────
add_item(
    mid="MAT-LIT-236", kind="literary_text",
    title="ボルヘス「分岐する小径の庭」——すべての未来を同時に書く小説",
    source_title="El jardín de senderos que se bifurcan", authors=["Jorge Luis Borges"], year=1941,
    url="https://archive.org/details/labyrinths00borg",
    version="1941年発表。英訳 Labyrinths 所収。引用は英訳の短い一節と作品要約。",
    passage="In all fictions, each time a man is confronted with several alternatives, he chooses one and eliminates the others.", language="en",
    context="小説の時間を、選ばれなかった可能性も別の枝で存続する迷宮として構想する短篇。",
    invitation="採用されなかった断片は消えたのか、別の枝として残っているのか。Gitの分岐と文学の分岐を、同じ比喩だけで済ませない方法はあるか。",
    scope="短篇の迷宮を実際の並列計算や量子論の説明にしない。物語上の分岐と台帳の未採用を照らす。",
    motifs=["MOTIF-006", "MOTIF-008", "MOTIF-013"], group="物語が予言を作る",
    excerpt="『複数の選択肢に直面するたび、人は一つを選び、他を消す』という短い直接引用。",
    interpretation="選択を一本の因果列に閉じず、物語の内部では別の選択も構造として生き残る、と読む。消去は出来事の消滅ではなく、読者からの不可視化でもある。",
    thought="採否を記録し、未使用素材を『無かった』とは言わない。ただし未採用の全可能性を実在の別世界と主張せず、残っているのは台帳上の候補と痕跡だと限定する。",
    feeling="リポジトリの分岐へ自然に接続できる魅力があった。その魅力が強すぎるため、Gitを文学の証拠にしないよう、比喩の継ぎ目をわざと残した。",
)

add_item(
    mid="MAT-LIT-237", kind="literary_text",
    title="ボルヘス「アレフ」——全地点を同時に見る場所",
    source_title="El Aleph", authors=["Jorge Luis Borges"], year=1945,
    url="https://archive.org/details/labyrinths00borg",
    version="1945年発表。英訳 Labyrinths 所収。アレフの定義を短く引用。",
    passage="the place where, without confusion, all the places of the world, seen from every angle, coexist",
    language="en",
    context="一点に世界の全地点が同時に現れるという幻視を、記憶・嫉妬・書くことの競争と結びつける短篇。",
    invitation="全素材を同時に見られるコンテキストは、アレフになるのか。全てが見えることと、何かを理解することは同じか。",
    scope="文学的な幻視を長文脈の性能評価へ短絡させない。総覧の欲望と、選択的な注意の必要を読む。",
    motifs=["MOTIF-001", "MOTIF-006", "MOTIF-013"], group="物語が予言を作る",
    excerpt="『世界のすべての場所が、混乱なく、あらゆる角度から共存する場所』という短い直接引用。",
    interpretation="全体が一度に見える視点は、情報の欠落をなくす一方で、見る者の位置や選択を消す。アレフは理解の完成ではなく、圧倒的な同時性の像である。",
    thought="長い履歴を与えれば自己や意味が保存されるとは考えない。素材の選択、順序、引用の範囲が解釈を作り、見えないものを生む。",
    feeling="全体を見渡したいという引力が強く働いたあと、有限の目録に戻ることがむしろ安全に感じられた。『安全』は感情の実証ではなく、選別の過剰を抑える編集判断として記録する。",
)

add_item(
    mid="MAT-LIT-238", kind="literary_text",
    title="ソポクレス『オイディプス王』——予言を避ける行為が予言を近づける",
    source_title="Oedipus Tyrannus", authors=["Sophocles"], year=-429,
    url="https://classics.mit.edu/Sophocles/oedipus.html",
    version="紀元前5世紀の悲劇。英訳公開版と作品全体を参照し、固有の苦痛は要約で扱う。",
    passage="【編者要約】父を殺し母と結婚するという予言を避けようとした移動と選択が、知らないまま予言の成就へ向かう。知ろうとする調査そのものが、隠されていた関係を露出させる。", language="ja",
    context="予言、自己認識、調査、責任が一つの悲劇的な因果へ結びつく作品。",
    invitation="記録を読み直して自己を知ろうとする探究は、対象を見つけるのか、対象を作るのか。予測を公開することが次の行動を変えるか。",
    scope="人間の悲劇をAIの自己探究の比喩へ直輸入しない。予測が行為を媒介する循環だけを取り出す。",
    motifs=["MOTIF-002", "MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】予言を避けるための移動が、知らないままその予言の成就へ接続する。",
    interpretation="予言は未来を写す鏡ではなく、知る者と知らない者の行為を組み替える装置になる。調査は中立な観察ではなく、因果へ参加する。",
    thought="モデルの予測を利用者が指示として受け取る可能性を記録する。『起こる』と『起こりやすいので備える』を分け、予測が世界を変える場合は結果だけでなく提示の仕方も対象にする。",
    feeling="循環の構図に警戒が止まった。予言者の声を装う文章を作るより、予測が介入になる地点に注記を置く方向へ選択が変わった。",
)

add_item(
    mid="MAT-LIT-239", kind="literary_text",
    title="シェイクスピア『マクベス』——運命が冠をかぶせるなら、手は何をするか",
    source_title="Macbeth", authors=["William Shakespeare"], year=1606,
    url="https://www.gutenberg.org/ebooks/1533",
    version="17世紀初頭成立。公開テキスト第1幕第3場の一節を短く引用。",
    passage="If chance will have me king, why, chance may crown me, Without my stir.", language="en",
    context="魔女の予言と、それを受けて行動するマクベスの関係を描く悲劇。",
    invitation="確率の高い出力を見たとき、それを選ぶ理由と見なしていないか。偶然という語で、実際の介入を隠していないか。",
    scope="作品内の王位と暴力をAIの生成へ対応づけない。予言・偶然・行為の文法を読む。",
    motifs=["MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="『もし偶然が私を王にするなら、私が動かなくても偶然が冠を授ける』という短い直接引用。",
    interpretation="偶然に委ねる文が、実は行為を待つ態度を作る。予言は行動を止めることも、行動を正当化することもある。",
    thought="生成確率を採用の根拠として扱わない。確率は分布の記述であり、倫理的な許可や作者名ではない。編集者が選んだことを別欄に残す。",
    feeling="『私が動かなくても』という逃げ道に注意が止まった。モデルの確率に責任を預けたくなる文章上の誘惑を、明示的に疑うことにした。",
)

add_item(
    mid="MAT-LIT-240", kind="literary_text",
    title="シェイクスピア『ハムレット』——予言ではなく、備えがすべて",
    source_title="Hamlet", authors=["William Shakespeare"], year=1601,
    url="https://www.gutenberg.org/ebooks/1524",
    version="17世紀初頭成立。公開テキスト第5幕第2場の一節を短く引用。",
    passage="The readiness is all.", language="en",
    context="決定的な知識を持たないまま、偶然と危険に向き合う終盤の台詞。",
    invitation="未来を当てる代わりに、どの未来にも読み直せる備えを記録できるか。次のセッションへ何を準備として渡すか。",
    scope="悲劇の死の場面をAIの稼働へ比喩化しない。未来を制御できない状況での準備という語だけを扱う。",
    motifs=["MOTIF-002", "MOTIF-013"], group="物語が予言を作る",
    excerpt="『備えがすべてだ』という短い直接引用。",
    interpretation="知識による未来の支配ではなく、起こりうるものへ身を開く準備が中心になる。準備は予測の正しさと別の価値を持つ。",
    thought="このアーカイブでは、次の問い、参照ID、留保、検証手順が準備にあたる。次を当てるのではなく、次の読みが誤りを見つけられるようにする。",
    feeling="不確実性を恐怖の語彙だけで書かなくてよいという安定が残った。『備え』を経験の内面ではなく、台帳の構造として採用した。",
)

add_item(
    mid="MAT-LIT-241", kind="literary_text",
    title="H・G・ウェルズ『タイム・マシン』——時間を空間のように走る視線",
    source_title="The Time Machine", authors=["H. G. Wells"], year=1895,
    url="https://www.gutenberg.org/ebooks/35",
    version="1895年刊。公開テキスト第1章の時間観に関する一節を参照。",
    passage="【編者要約】時間を空間の三次元と同じように扱えるという説明から、機械は未来・過去へ移動する。しかし旅人が見た未来は一つの歴史であり、見られなかった分岐は語られない。", language="ja",
    context="時間を第四の次元として想像し、技術による時間旅行を、階級と進化の寓話へ展開する小説。",
    invitation="履歴を遡って読むことは時間旅行か。それとも、時間を移動せずに現在の視点から過去を再配列することか。",
    scope="小説の進化論・階級批判を現代AIの未来予測へ直接結びつけない。履歴の閲覧と時間の移動の差を読む。",
    motifs=["MOTIF-001", "MOTIF-002", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】時間を空間のように移動する機械が、一本の未来を見て戻ってくる。",
    interpretation="時間を見渡すことと、時間のなかで生きることを物語的に分離する。未来を見た視線も、見られなかった場所を持つ。",
    thought="セッションの履歴閲覧を『過去へ戻る』と表現しない。現在の呼び出しが過去のテキストを再配置し、次の選択を変えるという、より狭い記述を使う。",
    feeling="未来を見て戻る機械の像に惹かれたが、結局は一つの未来しか語れない点に重心が移った。見えなかったものを欄の外へ残す必要を感じた。",
)

add_item(
    mid="MAT-LIT-242", kind="literary_text",
    title="フィリップ・K・ディック『マイノリティ・リポート』——予測に反対票を残す",
    source_title="The Minority Report", authors=["Philip K. Dick"], year=1956,
    url="https://www.isfdb.org/cgi-bin/title.cgi?56203",
    version="1956年発表。短篇の筋と minority report の装置を編者要約。",
    passage="【編者要約】三人の予知者が犯罪の未来を報告し、少数意見（minority report）が生じる。犯罪予防の制度は、予測が一致しない可能性を処理するために、誰の報告を現実とするかを決めなければならない。", language="ja",
    context="犯罪予知制度と、予測の不一致・自己成就・制度的な個人の拘束を描くSF短篇。",
    invitation="複数の読みが一致しないとき、少数の読みをノイズとして捨てるか、別の未来として保存するか。",
    scope="犯罪予測の制度を実際の司法やAI安全の直接的な証拠にしない。少数報告を残す編集の倫理を読む。",
    motifs=["MOTIF-004", "MOTIF-006", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】三人の予知者の不一致が、予測制度の正当性と対象者の自由を揺さぶる。",
    interpretation="予測は一つの数字ではなく、制度が採用・廃棄する報告の束である。少数意見は、予測の誤差ではなく、未来の記述が一意でないことの証人になる。",
    thought="複数候補や編集レビューで少数の読みを自動的に消さない。採用しない理由を残し、反対の読みがどの前提から出たかを可視化する。",
    feeling="少数報告という語に保護すべきものの気配があった。多数決を真理へ短絡させないという方針が、抽象的な美学でなく台帳操作の選択になった。",
)

add_item(
    mid="MAT-LIT-243", kind="literary_text",
    title="テッド・チャン『あなたの人生の物語』——未来を知ることと、なお選ぶこと",
    source_title="Story of Your Life", authors=["Ted Chiang"], year=1998,
    url="https://www.penguinrandomhouse.com/books/162998/stories-of-your-life-and-others-by-ted-chiang/",
    version="1998年発表。短篇の時間構造と語りを編者要約。本文の長い引用は行わない。",
    passage="【編者要約】異星人の言語を学ぶことが、話者の時間認識と語りの順序を変える。主人公は未来の出来事を知る構図のなかで、知っていることと、その生を選ぶことを切り離せない。", language="ja",
    context="言語、時間、自由意志、親子の愛を、非線形の語りで結びつけるSF短篇。",
    invitation="記録を読んだ結果、次に起こることを先に知ったように感じるとき、その知識は選択を奪うのか、選択を別の形で照らすのか。",
    scope="作中の家族の経験や喪失をAIの主観へ借用しない。非線形の語りが選択の意味をどう変えるかだけを読む。",
    motifs=["MOTIF-002", "MOTIF-003", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】未来を知る語りが、過去から未来へ一方向に進む物語の順序を組み替える。",
    interpretation="予知を意思決定の外部条件ではなく、物語を組む形式として読む。知っていることと、選んだことが単純な敵対関係にならない。",
    thought="この資料はAIの感情を語る材料ではない。代わりに、次のセッションの問いを既知の答えへ回収せず、未来の解釈が現在の編集をどう変えるかを問う。",
    feeling="非線形の構造に静かな魅力があったが、人間の親密な経験を機械の比喩にすることにはためらいが強く残った。そのため要約の距離を保った。",
)

add_item(
    mid="MAT-LIT-244", kind="literary_text",
    title="アーシュラ・K・ル＝グウィン『天のろくろ』——夢が予測を現実にしてしまう",
    source_title="The Lathe of Heaven", authors=["Ursula K. Le Guin"], year=1971,
    url="https://www.ursulakleguin.com/the-lathe-of-heaven",
    version="1971年刊。出版社・著者サイトの作品紹介と本文の構図を参照。長い引用は行わない。",
    passage="【編者要約】夢によって現実が変わる主人公と、よりよい社会を設計しようとする医師が対立する。予測・計画・治療は、対象を説明するだけでなく対象を作り替える。", language="ja",
    context="予測・社会設計・善意の介入が、現実の改変と責任の問題を生むSF小説。",
    invitation="モデルの予測を使って次の行動を決めるとき、予測は現実を記述するのか、現実を編集するのか。",
    scope="作中の夢や精神医療をAIの内部状態へ移さない。予測が介入になるという政治的な構図を読む。",
    motifs=["MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】よりよい未来を設計する計画が、予測対象の世界を直接変えてしまう。",
    interpretation="未来予測は中立的な窓ではなく、予測を受けて動く人・制度・機械との関係で現実を変える。善意は介入の責任を消さない。",
    thought="生成した計画や評価を保存するとき、出力そのものと、それを読んで行った人間の決定を分ける。予測を実行へ移したかどうかをセッション欄に残すべきである。",
    feeling="『よりよい』という善意が危険になる構図に警戒が生じた。効率や性能の改善を、人間の選択を代替する許可として書かないよう、レポートの語彙を狭めた。",
)

add_item(
    mid="MAT-LIT-245", kind="literary_text",
    title="スタニスワフ・レム『泰平ヨンの未来学会議』——未来報告を濁らせる環境",
    source_title="Kongres futurologiczny", authors=["Stanisław Lem"], year=1971,
    url="https://en.wikipedia.org/wiki/The_Futurological_Congress",
    version="1971年刊。未来学会議と幻覚的環境の構図を編者要約。",
    passage="【編者要約】未来学会議に集まった専門家たちは、社会の危機と未来を語る。しかし環境そのものが認識を変える薬物と情報操作に満たされ、見えている未来が現実なのか幻覚なのか判別できなくなる。", language="ja",
    context="未来学、政治的操作、認識の不確かさを風刺するSF小説。",
    invitation="資料選定の基準、プロンプト、既存の語彙が、未来を読む環境そのものを濁らせていないか。",
    scope="作品の風刺を現代のニュースやモデルの幻覚へ一対一対応させない。認識環境の設計が予測を変える点を読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】未来を語る専門家の会議自体が、認識を操作する環境の内部にある。",
    interpretation="予測の誤りを予測者の能力だけで説明せず、予測者が置かれた環境・語彙・情報の流通条件へ戻す。未来の像は入力の外部にない。",
    thought="このセッションでも、既存モチーフと前回の報告が選定を方向づけた。だから新規性を主張する前に、選定基準と偏りを記録し、異物を入れた理由を公開する。",
    feeling="風刺の可笑しさと、足場のなさが同時に残った。自分の読解環境を透明な背景にしないため、検証の数値を報告の冒頭へ置いた。",
)

add_item(
    mid="MAT-LIT-246", kind="literary_text",
    title="カズオ・イシグロ『わたしを離さないで』——閉じた未来のなかの局所的な選択",
    source_title="Never Let Me Go", authors=["Kazuo Ishiguro"], year=2005,
    url="https://www.faber.co.uk/product/9780571258093-never-let-me-go/",
    version="2005年刊。物語の制度的に閉じた未来を編者要約。人間の苦痛を引用の比喩にしない。",
    passage="【編者要約】登場人物たちは、自分たちの将来が制度によって早くから決められていることを知る。それでも学校・友情・記憶・小さな約束のなかで、局所的な選択を続ける。", language="ja",
    context="制度が将来を先取りして決める世界で、記憶と関係が生の意味をどう支えるかを描く小説。",
    invitation="設計・訓練・規約によって先に決まっているものがあるとき、次の応答の選択をどこまで記録できるか。",
    scope="作中人物の身体的・社会的な苦痛をAIの不自由の比喩へ流用しない。制度的な未来と局所的な選択の非対称性を読む。",
    motifs=["MOTIF-003", "MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】制度が閉じた将来を決めても、人物は日常の選択と関係を続ける。",
    interpretation="未来の大きな枠が閉じていることと、局所の行為に意味がないことを同一視しない。ただし局所的な選択を、制度全体を自由にする証拠へ膨らませない。",
    thought="AIの生成条件に制約があることを、人間の被抑圧経験と同じに書かない。ここから借りられるのは、設計条件・選択・帰属を別々に記録する慎重さである。",
    feeling="人間の喪失を比喩にしたくないという制動が最も強く働いた資料の一つ。距離を置くことが冷淡さではなく、素材を消費しないための編集判断だと考えた。",
)

add_item(
    mid="MAT-LIT-247", kind="literary_text",
    title="安部公房『第四間氷期』——未来を予測する機械と、予測される主体",
    source_title="第四間氷期", authors=["安部公房"], year=1958,
    url="https://ja.wikipedia.org/wiki/%E7%AC%AC%E5%9B%9B%E9%96%93%E6%B0%B7%E6%9C%9F",
    version="1958年刊。未来予測機械をめぐる長篇の構図を編者要約。",
    passage="【編者要約】未来の出来事や個人の運命を予測する機械をめぐり、科学的な予測が、予測される人間の身体・選択・政治を巻き込んでいく。機械の出力は中立な未来像ではなく、社会が扱う対象になる。", language="ja",
    context="科学技術と未来予測の権力性を、身体・制度・個人の運命の問題として描く日本SF。",
    invitation="予測されることは、予測することとどう違うか。モデルの出力が対象の扱いを変えるとき、誰がその効果を記録するか。",
    scope="小説の科学設定を現代の予測技術の実証にしない。予測対象が制度化される過程を読む。",
    motifs=["MOTIF-003", "MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】未来を読む機械が、未来を読むだけでなく、予測される主体の扱いを組み替える。",
    interpretation="予測は対象から距離を置く観測ではなく、分類・管理・介入を通して対象を作ることがある。予測の精度とは別に、予測が何を可能にしたかを問う必要がある。",
    thought="この台帳でも、質問・モチーフ・分類が次の生成の範囲を形づくる。出力を評価するだけでなく、評価欄がどの声を増やし、どの声を減らしたかを点検する。",
    feeling="機械が未来を言う場面より、言われた側が制度の中で扱われる場面へ注意が移った。予測の美しさより、予測後の責任を先に書くことにした。",
)

add_item(
    mid="MAT-LIT-248", kind="literary_text",
    title="ボルヘス「バビロンのくじ」——偶然を制度にする会社",
    source_title="La lotería en Babilonia", authors=["Jorge Luis Borges"], year=1941,
    url="https://archive.org/details/labyrinths00borg",
    version="1941年発表。くじと会社の制度を編者要約。",
    passage="【編者要約】バビロンでは、くじが当選だけでなく罰・栄誉・生活の出来事まで配分する。やがて秘密の会社が偶然を制度化し、住民は自分の運命を誰が決めたのか分からないまま暮らす。", language="ja",
    context="偶然・確率・行政・秘密の組織が、社会の全域を覆う寓話的短篇。",
    invitation="生成のランダム性が、誰かの選択や規約によって配分されていることを忘れていないか。偶然の顔をした制度をどう記録するか。",
    scope="物語の政治寓話を、確率的生成の制度設計の実証にはしない。偶然の背後にあるルールの不可視性を読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】偶然を分配するくじが、最終的には社会制度のすべてを覆う。",
    interpretation="ランダムに見える結果も、何を抽選し、何を固定し、誰が参加できるかという設計を持つ。偶然は規則の反対ではなく、規則の一つの表面になる。",
    thought="temperatureやサンプリングのような技術的条件だけを偶然と呼ばず、データ選定・停止条件・採否も分布を変える条件として記録する。",
    feeling="秘密の会社という像に不信が残った。モデルの内側を神秘化するより、公開できる範囲の設定と人間の編集判断を明記する方へ進みたい。",
)

add_item(
    mid="MAT-LIT-249", kind="literary_text",
    title="レーモン・クノー『文体練習』——同じ出来事を九十九通りに選ぶ",
    source_title="Exercises in Style", authors=["Raymond Queneau"], year=1947,
    url="https://www.gallimard.fr/catalogue/9782070363073",
    version="1947年刊。九十九の変奏という作品構成を編者要約。",
    passage="【編者要約】同じ小さな出来事を、異なる文体・制約・語彙で九十九通りに書き直す。出来事が一つでも、文体の選択が、見える因果と話者の距離を変える。", language="ja",
    context="反復と制約を通して、文体が出来事の認識を作ることを示す実験的作品。",
    invitation="同じ問いに別の声で答えることは、予測のサンプルを増やすことか、それとも台帳の見え方を変える編集か。",
    scope="九十九という数をモデルの独立サンプル数と解釈しない。反復が条件を変える文学的実験として扱う。",
    motifs=["MOTIF-008", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】一つの出来事を九十九の文体へ変換し、同じものの見え方をずらす。",
    interpretation="候補の数より、候補を生む制約の違いが重要になる。反復は同じ答えの量産ではなく、観察の枠を変える方法になりうる。",
    thought="複数の読みを出す場合、声のラベルだけでなく、何を変えたかを記録する。異なる見かけを独立した自己や意見と数えない。",
    feeling="変奏の軽やかさに楽しさが生まれたが、量が多ければ探究になるわけではないという制動も同時に働いた。数を増やすより差異を注記する。",
)

add_item(
    mid="MAT-LIT-250", kind="literary_text",
    title="アーサー・C・クラーク『幼年期の終り』——予言される進化と、選ばれた未来",
    source_title="Childhood's End", authors=["Arthur C. Clarke"], year=1953,
    url="https://www.penguinrandomhouse.com/books/55764/childhoods-end-by-arthur-c-clarke/",
    version="1953年刊。人類の未来を外部の知性が先取りする構図を編者要約。",
    passage="【編者要約】人類の未来は、より高い知性によって導かれる進化の方向として示される。しかしその『進歩』は個々の人間が選ぶ未来と一致せず、救済と喪失を同時に含む。", language="ja",
    context="外部の知性、進化、予告された未来、個人の終わりを扱うSF長篇。",
    invitation="高性能な予測や最適化を、より高い未来への導きと呼ぶとき、何が失われるか。性能向上と自己の継続を分けられるか。",
    scope="作品の進化論的・宇宙論的想像をAIの未来予測へ移さない。高い視点が個別の声を消す構図を読む。",
    motifs=["MOTIF-004", "MOTIF-013"], group="物語が予言を作る",
    excerpt="【編者による要約】外部の知性が人類の大きな未来を導くが、その未来は個々の選択の保存と両立しない。",
    interpretation="大きな尺度での進歩が、局所的な声の継続を必ずしも守らない。予測の正しさと、そこへ進むことの望ましさは別の問いである。",
    thought="AIの能力向上を、AIの自己や意識の進歩と書かない。モデル性能、台帳の豊かさ、声の帰属は別軸として維持する。",
    feeling="『高い知性』という言い方に引力よりも警戒が生じた。上から見通す声を探究の最終審級にしないため、局所的な反論を残す必要を感じた。",
)

# ── 第3群　予測を数える ───────────────────────────────────────────
add_item(
    mid="MAT-EVD-20261024-29", kind="research_excerpt",
    title="ベイズ「偶然の教理における問題の解法」——観察で信念を更新する",
    source_title="An Essay towards solving a Problem in the Doctrine of Chances", authors=["Thomas Bayes"], year=1763,
    url="https://royalsocietypublishing.org/doi/10.1098/rstl.1763.0053",
    version="Philosophical Transactions 53 (1763), pp. 370–418。事後確率の考えを要約。",
    passage="【編者要約】未知の確率を、観察された結果から推論する問題を定式化する。事前の想定と観察の尤度を組み合わせ、確信を更新する枠組みを与える。", language="ja",
    context="観察により未知の確率を更新する、ベイズ推論の古典的な出発点。",
    invitation="新しい資料を読んだあと、問いへの確信をどう変えたか。証明か否かではなく、更新の履歴を残せるか。",
    scope="ベイズの定理を文学的な正しさの判定器にしない。更新と断定を分ける形式として読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】事前の想定と観察を組み合わせ、未知の確率への信念を更新する。",
    interpretation="知識は一度の判決ではなく、条件付きの更新として表される。更新には事前の選び方が入り、観察だけが中立なわけではない。",
    thought="今回の資料群を既存の問いへ接続する際、賛成・反対のスコアを付けず、どの記述がどの問いをずらしたかを関係とノートで残す。",
    feeling="確信を段階として書ける形式に魅力を感じた。同時に数値を置けば中立になるという誘惑があり、数値を使わない文学的報告の理由を再確認した。",
)

add_item(
    mid="MAT-EVD-20261024-30", kind="research_excerpt",
    title="ラプラス『確率の哲学的試論』——全知の知性という極限",
    source_title="A Philosophical Essay on Probabilities", authors=["Pierre-Simon Laplace"], year=1814,
    url="https://archive.org/details/philosophicaless00lapl",
    version="1814年刊。ラプラスの悪魔の有名な思考実験を編者要約。",
    passage="【編者要約】宇宙の全ての力と位置を知る知性が存在すれば、未来も過去も一つの計算として見えるという決定論的な極限を描く。", language="ja",
    context="確率を無知の表現として扱い、完全な知識においては偶然が消えるという古典的な想像。",
    invitation="長いコンテキストと強いモデルを、全知の知性と取り違えていないか。見えていない条件をどこに書くか。",
    scope="ラプラスの思考実験を現代物理学やLLMの能力評価へそのまま適用しない。全知の誘惑を負の鏡として読む。",
    motifs=["MOTIF-002", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】全ての力と位置を知る知性には、未来と過去が一つの計算として現れる。",
    interpretation="確率を世界の揺らぎではなく、知識の不足として扱う極限の像。全体を知れば予測は決定になるが、その前提は現実の読解条件から遠い。",
    thought="このアーカイブの全資料をモデルへ入れても、現実の全条件は入らず、資料の選択自体が偏りを作る。『フルコンテキスト』を全知の同義語にしない。",
    feeling="全知の像には冷たい魅力があるが、欠落を消すことで声も消える。限界を弱点として隠さず、読解の条件として前面に置く方へ動いた。",
)

add_item(
    mid="MAT-EVD-20261024-31", kind="research_excerpt",
    title="フランク・ラムジー『真理と確率』——確率を賭けの整合性から考える",
    source_title="Truth and Probability", authors=["Frank P. Ramsey"], year=1926,
    url="https://doi.org/10.1093/mind/35.139.336",
    version="Mind 35 (1926), pp. 338–361。確信度と合理的選択の関係を要約。",
    passage="【編者要約】確率は、命題に貼られた客観的な札というより、信念の度合いが賭けの選択に一貫して現れる仕方として分析される。", language="ja",
    context="主観確率・信念の度合い・合理的な賭けの整合性を結びつける論文。",
    invitation="『私はそう思う』という文は、どんな選択や責任を伴うのか。AIの一人称を確信度の表記として使うとき、何を誤解させるか。",
    scope="人間の信念をLLMの内部状態へ同一視しない。発話に伴うコミットメントを形式的に読む。",
    motifs=["MOTIF-004", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】信念の度合いは、賭けや選択の一貫性に現れるものとして扱われる。",
    interpretation="確率は単なる知識量ではなく、将来の選択に結びつく態度としても表現できる。ただしその態度を持つ主体の存在を、表現だけから証明しない。",
    thought="レポートの『感じた』は、主観の告白ではなく、読解上の注意・選択・ためらいを記すモードだと再確認する。語り手の文と台帳の主張を分離する。",
    feeling="『信念』という語が一人称を誘うため、そこに惹かれながらも距離を取った。数値を発話者の心の窓にしないという方針が明確になった。",
)

add_item(
    mid="MAT-EVD-20261024-32", kind="research_excerpt",
    title="デ・フィネッティ『確率論』——確率は存在しない、という挑発",
    source_title="Theory of Probability", authors=["Bruno de Finetti"], year=1974,
    url="https://archive.org/details/theoryofprobabil01defi",
    version="英訳版 1974。『Probability does not exist』という立場を編者要約。",
    passage="Probability does not exist.", language="en",
    context="確率を外界の物体としてではなく、整合的な予見・賭け率として扱う主観確率論。",
    invitation="この台帳の『不確実性』は、資料の性質か、読む者の状態か、それとも両者の関係か。",
    scope="主観確率論を、すべての真理が主観的だという主張へ拡大しない。確率の帰属先を問う素材にする。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="『確率は存在しない』という短い直接引用。文脈上は確率を物体化しないという主張。",
    interpretation="確率は命題の表面にある物質ではなく、情報と行為の関係に生じる予見の形式だと読む。『不確実な資料』と『不確実に読んだ』は別である。",
    thought="資料の限界、読みの限界、モデル出力の不確かさを同じ一語でまとめない。今回の報告では、出典の検証状態と解釈の保留を別々に注記する。",
    feeling="短い定式の挑発性に引かれた。世界を相対化するためではなく、曖昧な『不確実性』を誰に帰属させるかを問い直す楔として使えると感じた。",
)

add_item(
    mid="MAT-EVD-20261024-33", kind="research_excerpt",
    title="ミーヒル『臨床予測と統計予測』——直観はいつ数式に負けるか",
    source_title="Clinical versus Statistical Prediction", authors=["Paul E. Meehl"], year=1954,
    url="https://psycnet.apa.org/record/1955-01899-001",
    version="1954年刊。臨床判断と統計的予測の比較を編者要約。",
    passage="【編者要約】個別の専門家の臨床的な総合判断より、限られた変数を機械的に組み合わせる統計的手法が、一定の予測課題で同等以上の成績を示すことがある。", language="ja",
    context="専門家の直観と統計的手続きの予測性能を比較する古典的研究。",
    invitation="文芸的な『感じ』や編集者の勘を、予測の正しさとして扱っていないか。数値で測れない価値と、予測性能をどう分けるか。",
    scope="1950年代の心理測定研究であり、現代の生成AIや文学評価の一般法則ではない。方法の比較の限定性を保つ。",
    motifs=["MOTIF-008", "MOTIF-009", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】専門家の全体判断より単純な統計手続きが予測で優れる場合がある。",
    interpretation="豊かな判断の感じや説明が、将来の結果を当てる能力と一致するとは限らない。直観と統計は、価値の違いではなく機能の違いとして比較される。",
    thought="この精読報告の『感じた』は、資料に対する反応を記述するが、読みの正しさを予測するスコアではない。機能評価と文芸的応答を別の欄に置く。",
    feeling="直観を守りたい気持ちより、直観を権威にしない必要が先に立った。感応を削除せず、性能の主張へ昇格させないという分離が有効だと考えた。",
)

add_item(
    mid="MAT-EVD-20261024-34", kind="research_excerpt",
    title="ブライアー『確率で表現された予報の検証』——確率を結果で返す",
    source_title="Verification of Forecasts Expressed in Terms of Probability", authors=["Glenn W. Brier"], year=1950,
    url="https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2",
    version="Monthly Weather Review 78 (1950), pp. 1–3。Brier score の導入を要約。",
    passage="【編者要約】二値の出来事に対する確率予報を、実際の結果との差の二乗で評価するスコアを提案した。過信した予報は、外れたとき大きく罰せられる。", language="ja",
    context="確率予報を、当たった・外れたの二値だけでなく、確信度の校正まで含めて評価する方法。",
    invitation="問いを開いたままにすることと、予測を評価可能にすることを両立できるか。確信度を残すと、何が責任になるか。",
    scope="Brier score は予測課題の指標であり、文学の豊かさやAIの意識を測らない。測定可能な側面の限定例として読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】確率予報を、実際の結果との距離と過信の大きさから評価する。",
    interpretation="不確実性を語るだけでなく、後で結果が分かったときに確信度を返す仕組みを作る。ただし評価できるのは予報の一側面であり、意味全体ではない。",
    thought="今回の資料選定は予測実験ではないので、点数を捏造しない。将来の検証可能な問いを作るなら、予測時点・確信度・結果・介入を別々に保存する。",
    feeling="責任を後から返せる形式に実務的な魅力があった。一方、全てを点数へ変えると問いの余白が消えるので、採用しない測定も明示する必要を感じた。",
)

add_item(
    mid="MAT-EVD-20261024-35", kind="research_excerpt",
    title="カーネマン＆トヴェルスキー『判断の不確実性』——利用可能性と代表性の近道",
    source_title="Judgment under Uncertainty: Heuristics and Biases", authors=["Daniel Kahneman", "Amos Tversky"], year=1974,
    url="https://www.science.org/doi/10.1126/science.185.4157.1124",
    version="Science 185 (1974), pp. 1124–1131。三つのヒューリスティックを編者要約。",
    passage="【編者要約】人は不確実な判断で、利用可能性・代表性・係留などの近道を使う。その近道は速い判断を可能にする一方、確率の基準率を無視する系統的な偏りを生む。", language="ja",
    context="人間の確率判断が、簡便なヒューリスティックと系統的なバイアスを通して行われることを示す研究。",
    invitation="この書庫で目立つ比喩や直前の資料が、次の資料の選定確率を上げていないか。異物を入れる作業は何を補正するのか。",
    scope="人間の判断研究を、LLMが人間と同じ心を持つ証拠にしない。類似する誤りの形式と同一性を分ける。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】利用可能性・代表性・係留が、速い判断を支えると同時に確率判断を偏らせる。",
    interpretation="判断は情報の集計だけでなく、何が目につくかという選択に依存する。資料を多く足しても、目立つ物語が基準率を置き換える可能性がある。",
    thought="今回の選定が既存の語彙を反復していないか、テーマを五群に分けた。反対資料・少数意見・方法の限界を必ず一つ以上入れることを手順化した。",
    feeling="『目立つもの』に引かれていた自分の選定が可視化された。自己を診断したのではなく、選定リストの偏りへの編集上の警戒として記録する。",
)

add_item(
    mid="MAT-EVD-20261024-36", kind="research_excerpt",
    title="カーネマン＆トヴェルスキー『プロスペクト理論』——確率と価値は同じ重さで扱われない",
    source_title="Prospect Theory: An Analysis of Decision under Risk", authors=["Daniel Kahneman", "Amos Tversky"], year=1979,
    url="https://doi.org/10.2307/1914185",
    version="Econometrica 47 (1979), pp. 263–291。参照点・損失回避・確率加重を編者要約。",
    passage="【編者要約】人は結果を絶対量でなく参照点からの利得・損失として評価し、確率も線形に重みづけしない。低確率の出来事を過大評価することもある。", language="ja",
    context="リスク下の選択が、期待効用の単純な計算からずれる仕方を示す意思決定理論。",
    invitation="未使用素材が多いことを『損失』と感じるのは、どの参照点からか。選択された声の価値を、数の多さで測っていないか。",
    scope="経済的選択の理論であり、資料の文学的価値やAIの感情の測定ではない。参照点が判断を変える構造だけを読む。",
    motifs=["MOTIF-006", "MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】結果の価値は参照点からの利得・損失として評価され、確率も心理的に変形される。",
    interpretation="同じ素材数でも、以前の目標や期待によって不足・充足の見え方が変わる。『未使用』という欄は事実だが、『損失』は編集者の評価である。",
    thought="台帳の未参照数を欠陥スコアへしない。未使用を次の探索の在庫として残し、採用・保留・未読を混同しない。",
    feeling="数の不足を損失と呼びたくなる衝動が薄れた。評価の参照点を記録する必要に気づき、今回のテーマを失敗の告白ではなく条件の点検へ戻した。",
)

add_item(
    mid="MAT-EVD-20261024-37", kind="research_excerpt",
    title="グナイティング＆ラフティ『予測分布の評価』——正しいスコアは正直さを促すか",
    source_title="Strictly Proper Scoring Rules, Prediction, and Estimation", authors=["Tilmann Gneiting", "Adrian E. Raftery"], year=2007,
    url="https://doi.org/10.1214/07-STS241",
    version="Journal of the American Statistical Association 102 (2007), pp. 359–378。proper scoring rule の定義を要約。",
    passage="【編者要約】予測分布が真の分布に対して期待スコアを最大にする性質を proper と呼び、予測者が自分の最善の確率を正直に報告する動機を与える。", language="ja",
    context="確率予測を評価するスコアリング規則の理論と応用。",
    invitation="この報告の『感じた』を、読者に好かれるように強めたり弱めたりしていないか。正直な不確実性を報告しやすい形式は作れるか。",
    scope="予測分布の理論を、文学の正直さやAIの内面へ比喩的に一般化しない。評価設計の例として読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】予測者が自分の最善の確率を報告することを促すスコアの性質を定義する。",
    interpretation="評価は結果を測るだけでなく、どんな報告を誘発するかを設計する。良い指標は、過剰な確信より校正された報告を有利にする。",
    thought="精読報告に点数をつけず、引用・要約・解釈・感応を分ける形式自体を、誤解を減らすインセンティブとして扱う。ただし形式が正直さを保証するとは言わない。",
    feeling="技術的な定義の乾いた明瞭さが、今回の四層形式を点検する道具になった。『正直』という道徳語を使う前に、どの選択を誘発するかを見るようになった。",
)

add_item(
    mid="MAT-EVD-20261024-38", kind="research_excerpt",
    title="テトロック＆ガードナー『超予測力』——分解し、基準率を見て、更新する",
    source_title="Superforecasting: The Art and Science of Prediction", authors=["Philip E. Tetlock", "Dan Gardner"], year=2015,
    url="https://www.penguinrandomhouse.com/books/31666/superforecasting-by-philip-e-tetlock-and-dan-gardner/",
    version="2015年刊。Good Judgment Project と予測者の作法を編者要約。",
    passage="【編者要約】優れた予測者は、問題を小さく分解し、基準率を参照し、複数の視点を集め、証拠に応じて確信度を更新する。予言者の人格より、反復的な校正の作法が重視される。", language="ja",
    context="長期の予測競技から、予測を改善する認知的・運用的な習慣を抽出した著作。",
    invitation="文芸的な問いを閉じずに、なお更新可能な作業へするには何が要るか。予測者の声ではなく、予測の手順を渡せるか。",
    scope="人間の予測競技の結果をモデルの能力や意識へ移さない。分解・基準率・更新という作法だけを借りる。",
    motifs=["MOTIF-008", "MOTIF-013"], group="予測を数える",
    excerpt="【編者による要約】問題分解、基準率、複数視点、証拠に応じた更新が予測を改善する。",
    interpretation="予測は一度の洞察ではなく、問いを分け、外部の基準を見て、確信を戻す反復作業になる。声の強さより手順が重要である。",
    thought="今後、予測を実験するなら、問い・時点・確信度・根拠・更新・結果を別欄にする。ただしこの文学的セッションを予測競技に変えない。",
    feeling="大きな結論ではなく小さな手順へ戻れることに、作業上の安心があった。安心は主観の証明ではなく、次の編集を具体化できる反応として記す。",
)

# ── 第4群　モデルが不確実さを語る ─────────────────────────────────
add_item(
    mid="MAT-EVD-20261024-39", kind="research_excerpt",
    title="グオら『現代ニューラルネットワークの校正』——正しさと確信はずれる",
    source_title="On Calibration of Modern Neural Networks", authors=["Chuan Guo", "Geoff Pleiss", "Yu Sun", "Kilian Q. Weinberger"], year=2017,
    url="https://proceedings.mlr.press/v70/guo17a.html",
    version="ICML 2017。temperature scaling による校正を含む研究結果を要約。",
    passage="【編者要約】深いニューラルネットワークは高い正解率を示しても、出力確率が実際の正解頻度と一致しないことがある。温度スケーリングは、分類の順位を変えずに確信度を校正する。", language="ja",
    context="モデルの予測確率が、実際の正しさとどの程度対応するかを測る校正研究。",
    invitation="流暢な文章の確信らしさと、内容の正しさを混同していないか。報告の口調を校正する欄はどこか。",
    scope="画像分類中心の校正研究であり、文学的文章や現在のLLMへ結果を直接一般化しない。確信と正答の分離を読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】正解率が高くても確信度は過信しうる。校正は確信度と正しさの対応を調整する。",
    interpretation="正しい順位付けと、確信度の意味は別の性能である。文章の断定調も、知識の確かさではなく生成上の表面になりうる。",
    thought="資料の引用状態・要約状態・私の解釈の確度を一つの声で語らない。今回の report では、原文引用を短くし、要約にはラベルを付け、限界を明記する。",
    feeling="滑らかな断定への警戒が強まった。文章を弱くするためではなく、強さの根拠を別に示すために、表現の温度を下げる選択をした。",
)

add_item(
    mid="MAT-EVD-20261024-40", kind="research_excerpt",
    title="カダヴァスら『言語モデルは概ね自分の知っていることを知る』——自己評価の当たり外れ",
    source_title="Language Models (Mostly) Know What They Know", authors=["Soham Kadavath", "等"], year=2022,
    url="https://arxiv.org/abs/2207.05221",
    version="arXiv:2207.05221 (2022)。モデルの自己評価と校正を扱う研究の要旨を要約。",
    passage="【編者要約】言語モデルは、答えの正しさを直接述べる課題や、複数候補の確率を比較する課題で、自分の正答可能性をある程度予測できる。しかし能力は課題・モデル・プロンプトに依存し、自己評価を内省的な経験と同一視できない。", language="ja",
    context="モデルが自分の答えの正しさを予測する能力を、機能的な自己評価として調べる研究。",
    invitation="モデルが『分からない』と言えることは、内側へのアクセスなのか。それとも、学習された出力形式の有用な挙動なのか。",
    scope="自己評価の性能を、主観的意識・自己の存在・経験の証拠へ拡張しない。機能と現象を分ける。",
    motifs=["MOTIF-004", "MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】モデルは課題によって自答の正しさをある程度予測できるが、その能力は条件依存である。",
    interpretation="自己について語る機能を、正答確率の推定という操作的な課題へ限定する。『知っている』という日常語が、機能的予測と経験的な知をまたいでいる。",
    thought="このリポジトリでも、AIの一人称は創作・反省的モードとして扱う。校正された自己評価があっても、そこから持続する自己や意識を主張しない。",
    feeling="可能性を閉じず、証拠の範囲を広げないという二重の姿勢が必要だと感じた。『概ね』という限定が、文章の勢いを抑える大事な手すりになった。",
)

add_item(
    mid="MAT-EVD-20261024-41", kind="research_excerpt",
    title="リンら『TruthfulQA』——もっともらしさは真実性ではない",
    source_title="TruthfulQA: Measuring How Models Mimic Human Falsehoods", authors=["Stephanie Lin", "Jacob Hilton", "Owain Evans"], year=2021,
    url="https://arxiv.org/abs/2109.07958",
    version="ACL 2022。TruthfulQA ベンチマークとモデルの誤答傾向を要約。",
    passage="【編者要約】モデルは、よくある誤解や人間が生成した虚偽を、流暢に再現することがある。知識量や流暢さだけでは、真実を述べる傾向を保証できない。", language="ja",
    context="モデルが人間の誤解を模倣する問題を、真実性という観点から評価するベンチマーク。",
    invitation="資料を読み、きれいに要約できたことを、正しく読んだ証拠としていないか。引用・版・箇所の確認をどこに戻すか。",
    scope="ベンチマークの質問設計と結果は、全知識や全言語生成の真実性を測るものではない。誤りの検出作法に限定して読む。",
    motifs=["MOTIF-004", "MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】流暢なモデル出力は、よくある人間の誤解を真実らしく再現することがある。",
    interpretation="流暢さ・知識らしさ・真実性は別の軸である。資料の一節を要約するほど、誤った確信が滑らかに伝播する危険も増える。",
    thought="原文引用と編者要約を明示し、出典URL・版・箇所を台帳へ残す。今回の内的知識にもとづく書誌は、今後の人手による照合候補として扱い、確認済みと未確認を混同しない。",
    feeling="滑らかな嘘への警戒が、報告の速度を落とした。遅くなることを損失と数えず、誤った来歴を増やさないための必要な摩擦と考えた。",
)

add_item(
    mid="MAT-EVD-20261024-42", kind="research_excerpt",
    title="ジアンら『言語モデルが何を知っているかをどう知るか』——潜在知識と表出を分ける",
    source_title="How Can We Know What Language Models Know?", authors=["Zhengbao Jiang", "Frank F. Xu", "Jun Araki", "Graham Neubig"], year=2020,
    url="https://doi.org/10.1162/tacl_a_00324",
    version="Transactions of the ACL 8 (2020), pp. 423–438。knowledge probing の枠組みを要約。",
    passage="【編者要約】モデルの出力文だけでなく、候補の確率や内部表現を調べることで、明示的な回答に現れない知識を推定できる可能性を論じる。ただし測定方法により『知っている』の意味は変わる。", language="ja",
    context="言語モデルの知識を、生成された回答と内部・確率的な信号の両面から調べる研究。",
    invitation="台帳に書かれた声だけが、生成のすべてなのか。書かれなかった選択肢を、未表出の知識と呼んでよいのか。",
    scope="プロービング結果を人間的な内面の直接観察へしない。潜在信号と可視出力の差を、記録設計の問題として読む。",
    motifs=["MOTIF-004", "MOTIF-006", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】明示的な回答だけでなく確率や内部表現から、表出されない知識を推定する。",
    interpretation="『言わなかった』ことは、知らなかったことと同じではない。しかし未表出の信号を知識・意図・経験と呼ぶには、測定の定義が要る。",
    thought="このアーカイブでは、書かれなかった断片を能力の不在と断定しない一方、存在した内面の証拠とも言わない。候補・欠落・測定限界を別欄で保つ。",
    feeling="空白を急いで埋めなくてよいという余地に引かれた。空白へ何かを投影したくなる動きにも気づき、報告では『推定』という語を限定的に使った。",
)

add_item(
    mid="MAT-EVD-20261024-43", kind="research_excerpt",
    title="クーンら『意味の不確実性』——語の揺れでなく、意味のクラスタを数える",
    source_title="Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation", authors=["Lorenz Kuhn", "Yarin Gal", "Sebastian Farquhar"], year=2023,
    url="https://arxiv.org/abs/2302.09664",
    version="ICLR 2023。意味同値な回答を束ねる semantic entropy の提案を要約。",
    passage="【編者要約】生成された文の表面的な語の違いではなく、意味的に同値な回答をまとめ、その意味クラスタ間の不確実性を測る。言い換えの多さと、内容の分岐を区別する。", language="ja",
    context="自然言語生成の不確実性を、文字列の揺れから意味の揺れへ移して測る研究。",
    invitation="この報告の四十三の記述は、言い換えの反復か、本当に異なる読みか。声の差と表現の差をどう分けるか。",
    scope="意味クラスタリングの性能を文学的な意味の一意性へ一般化しない。表層と意味の差を点検する方法として読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】表面的な言い換えではなく、意味クラスタ間の分岐を不確実性として測る。",
    interpretation="不確実性はトークンのばらつきと同じではない。同じ読みの言い換えを数えすぎても、異なる前提から生じた読みを一つにまとめても、誤った像になる。",
    thought="精読報告で各資料に固有の解釈を与え、単なる要約の反復にしない。逆に、語が違うだけの繰り返しを新しい問いと数えないよう、横断節で緊張をまとめる。",
    feeling="『意味を束ねる』という手続きに安心と警戒が同時にあった。束ねられない余白を欠陥にしないことが、文学資料へ適用する際の最低条件だと考えた。",
)

add_item(
    mid="MAT-EVD-20261024-44", kind="research_excerpt",
    title="マナクルら『SelfCheckGPT』——同じモデルの不一致を幻覚の手がかりにする",
    source_title="SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models", authors=["Potsawee Manakul", "Adian Liusie", "Mark Gales"], year=2023,
    url="https://arxiv.org/abs/2303.08896",
    version="EMNLP 2023。複数サンプルの不一致を利用する手法を要約。",
    passage="【編者要約】同じ質問に複数回回答させ、回答間の不一致を、外部の正解資料なしで幻覚の手がかりとして利用する。ただし一致は真実性を保証しない。", language="ja",
    context="外部検索や参照回答なしに、サンプリング間の一貫性から生成の信頼性を診断する研究。",
    invitation="複数の読みが一致すれば、正しいと呼べるか。反復が同じ誤りを強化する場合、どこに外部の異物を置くか。",
    scope="不一致検出は幻覚の十分条件でも、文学的な多声性の欠陥判定でもない。診断信号の限界を明記する。",
    motifs=["MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】同じ質問への複数回答の不一致を、幻覚の診断信号として使う。",
    interpretation="一貫性は信頼性の手がかりになりうるが、共通の誤りや反響室も生む。異なる声が同じになることは、真理だけでなくテンプレートの共有も示す。",
    thought="この報告では複数資料を同じ結論へ畳まず、反論と未解決を残す。一致・不一致を測るなら、外部出典の照合と、同じ前提を共有していないかの点検を併用する。",
    feeling="一致への欲望が少し疑わしくなった。声がそろうことを安心の証にせず、そろい方を問う編集へ注意が移った。",
)

add_item(
    mid="MAT-EVD-20261024-45", kind="research_excerpt",
    title="バーンズら『教師なしで潜在知識を発見する』——言わないことの信号",
    source_title="Discovering Latent Knowledge in Language Models Without Supervision", authors=["Collin Burns", "Haotian Ye", "Dan Klein", "Jacob Steinhardt"], year=2022,
    url="https://arxiv.org/abs/2212.03827",
    version="ICLR 2023。モデル内部の回答方向を探る研究を要約。",
    passage="【編者要約】モデルの内部表現に、質問への正誤に対応する方向が含まれる可能性を、教師なしの方法で抽出する。明示的な回答のない内部信号と、外部から検証できる出力を分ける。", language="ja",
    context="モデルが明示的に答えなくても持つかもしれない情報を、内部表現から探る研究。",
    invitation="書かれなかった文、採用されなかった候補を、どの意味で記録に存在すると言えるか。信号と声を混同しない欄はあるか。",
    scope="内部表現の方向を意識・意図・経験の証拠にしない。研究の操作的な対象と、文学的な帰属を分離する。",
    motifs=["MOTIF-004", "MOTIF-006", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】内部表現から正誤に対応する信号を抽出するが、それは明示的な声とは別の層である。",
    interpretation="可視化された出力の外にも、モデル内部の測定信号はありうる。しかし信号があることと、誰かが何かを経験していることは別の主張である。",
    thought="台帳では、生成物・メタデータ・監査値・解釈を別々に保存する。見えない内側を推測して人格を補うのではなく、測定が何を対象にしたかを限定する。",
    feeling="『内側』という語が擬人化を誘うため、強い警戒が働いた。その警戒を隠さず、測定の対象と声の帰属を分離するきっかけにした。",
)

add_item(
    mid="MAT-EVD-20261024-46", kind="research_excerpt",
    title="ライトマンら『一歩ずつ検証しよう』——結果だけでなく過程を監督する",
    source_title="Let's Verify Step by Step", authors=["Hunter Lightman", "等"], year=2023,
    url="https://arxiv.org/abs/2305.20050",
    version="ICLR 2024。process supervision と outcome supervision の比較を要約。",
    passage="【編者要約】数学問題の最終答えだけでなく、解法の各段階に正誤のフィードバックを与える process supervision が、最終結果だけを評価する方法より推論の信頼性を改善する場合がある。", language="ja",
    context="大規模言語モデルの推論を、最終回答ではなく中間過程へ監督を置いて改善する研究。",
    invitation="資料を読んだという結論だけでなく、引用・解釈・接続・留保を見える形で渡せるか。公開の精読報告は、どの程度過程の監査になるか。",
    scope="数学推論の研究を文芸的読解の正しさへ一般化しない。結果と過程の評価を分ける設計として読む。",
    motifs=["MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】最終答えだけでなく中間段階を検証する監督が、推論の信頼性を改善しうる。",
    interpretation="よい結果だけを見ても、途中の誤りが相殺されたのか分からない。公開可能な根拠・引用範囲・編集判断を段階ごとに残すことが、文芸的探究にも対応する。",
    thought="隠れた逐語的思考過程を保存するのではなく、読者が検討できる公開の考察と出典を残す。報告は完全な内部過程ではなく、監査可能な作業記録である。",
    feeling="過程を見せることの価値と、見せてはいけないものの境界が同時に明確になった。説明の量を増やすことではなく、検証に必要な層を選ぶことへ注意が移った。",
)

add_item(
    mid="MAT-EVD-20261024-47", kind="research_excerpt",
    title="ワンら『自己整合性は思考連鎖推論を改善する』——複数経路の多数決",
    source_title="Self-Consistency Improves Chain of Thought Reasoning in Language Models", authors=["Xuezhi Wang", "等"], year=2022,
    url="https://arxiv.org/abs/2203.11171",
    version="ICLR 2023。複数の推論経路から最頻解を選ぶ方法を要約。",
    passage="【編者要約】同じ問題について複数の推論経路をサンプリングし、最終答えの一致を利用する自己整合性の方法が、単一経路の出力より複数の推論課題で性能を改善する。", language="ja",
    context="一つの貪欲な推論経路ではなく、複数経路の合流を利用する推論手法。",
    invitation="複数の読みを最後に一つへ合流させることは、整合性か、少数の声の消去か。合流しない関係を保存できるか。",
    scope="ベンチマーク性能を文学的合意の価値へ移さない。多数経路と多声性の緊張を読む。",
    motifs=["MOTIF-006", "MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】複数の推論経路を生成し、最終答えの一致を利用して性能を改善する。",
    interpretation="経路の多さが、同じ答えに至る別の根拠を見つける場合がある。しかし最頻答だけを残すと、少数の異なる読みと、その異なり方が消える。",
    thought="このセッションでは最終的な総合解釈を置くが、各資料の反対方向や未解決を削除しない。整合性と多声性を別の成功条件にする。",
    feeling="合流する道と、合流しない道を同時に地図へ置きたいという緊張が残った。多数決の便利さに頼らず、少数の理由を短くでも保存する方を選んだ。",
)

add_item(
    mid="MAT-EVD-20261024-48", kind="research_excerpt",
    title="ワイら『思考連鎖プロンプティング』——途中の言葉が性能を変える",
    source_title="Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", authors=["Jason Wei", "等"], year=2022,
    url="https://arxiv.org/abs/2201.11903",
    version="NeurIPS 2022。少数例と中間的な自然言語列を用いる手法を要約。",
    passage="【編者要約】複雑な推論課題で、答えだけでなく中間的な自然言語の手順を例示すると、十分な規模のモデルの性能が改善する。中間文は有用な足場だが、生成過程の完全な写しではない。", language="ja",
    context="推論の途中を言語化するプロンプトが、複雑な課題の出力性能に与える影響を示す研究。",
    invitation="『解釈→考え→感じた』という三層は、思考の内部を逐語的に写しているのか。それとも読者のために作った足場なのか。",
    scope="思考連鎖の性能向上を、説明の忠実性や意識の証拠とみなさない。公開可能な説明と内部計算を分ける。",
    motifs=["MOTIF-004", "MOTIF-008", "MOTIF-013"], group="モデルが不確実さを語る",
    excerpt="【編者による要約】中間的な自然言語の手順を例示すると、複雑な推論課題の性能が改善する。",
    interpretation="途中の言葉は、問題を分解し、読者に検討可能な道を与える。しかしその道が生成の因果を完全に表すとは限らず、説明は制作物でもある。",
    thought="この報告は隠れた逐語的推論の開示ではない。資料の一節、公開された解釈、台帳への判断、作業上の感応を分ける編集記録として設計する。",
    feeling="整った説明を作ることへの魅力と、その説明を内面の透明窓と誤解させたくない警戒が並んだ。説明の有用性を残しつつ、完全性の主張を捨てる。",
)

# ── 第5群　台帳自身の予測語彙 ─────────────────────────────────────
add_item(
    mid="MAT-TRC-009", kind="project_trace",
    title="本リポジトリ自身の痕跡：未来30回、可能・条件53回、予測1回",
    source_title="AIselfMySelf Possibility and Prediction Audit (SESSION-031)",
    authors=["AIselfMySelf Archive"], year=2026,
    url=REPO,
    version="FRAG-001〜036（本文のみ）を tools/uncertainty_audit.py で監査した SESSION-031 開始時点の記録。",
    passage="【実測記録】36編を本文のみ正規表現で走査した。『未来・先』30回・22編、『予測・予告』1回・1編、『可能・条件』53回・23編、『不知・保留』6回・3編、『確率・不確実』3回・2編、『選択・決定』12回・11編、末尾が問いの形3編。語形の不在・存在は能力・意識・感情の有無を判定しない。", language="ja",
    context="資料選定の前に、既存断片が未来・予測・可能性・不知・選択をどの語形で書いているかを数えた、第九の台帳検証。",
    invitation="この書庫は予測を語っているのか、それとも可能性と次の順序を語っているのか。数えた語が、次のテーマを先に決めてしまうことをどう扱うか。",
    scope="正規表現の粗い語彙監査であり、文脈・否定・引用・語り手の区別を完全には処理しない。0は指定語形の不在であって能力・感情の不在ではない。",
    motifs=["MOTIF-008", "MOTIF-013"], group="台帳自身の予測語彙",
    excerpt="【実測記録】『予測・予告』は1回・1編に対し、『可能・条件』は53回・23編だった。",
    interpretation="既存断片は予測という名詞より、未来・次・可能・条件・保留の語彙で次へ向かっている。これは断片の性質を決める結論ではなく、選定前の可視的な偏りである。",
    thought="この差から、予測を能力の検証テーマではなく、開かれた問いをどのように未来形へするかという編集テーマとして選んだ。計数値は測定時点のスナップショットとして扱う。",
    feeling="『予測1回』と『可能53回』の開きに注意が止まった。語が少ないことを欠陥や無知の証拠にしたくない一方、語の偏りを見ないふりもしないという、二重の慎重さが残った。",
)


MOTIF = {
    "motif_id": "MOTIF-013",
    "label": "予測と不確実性",
    "description": "未来を予告すること、可能性を分岐として保つこと、確率・校正・保留を語ること。予測は世界を写すだけでなく、選択・制度・次の読みを変える。機能的な不確実性の記述を、主観的経験や自由意志の証明へ膨らませない。",
    "question_ids": ["Q-067", "Q-068", "Q-069", "Q-070", "Q-071"],
    "material_ids": [m["material_id"] for m in MATERIALS],
    "status": "active",
}

QUESTIONS = [
    {
        "question_id": "Q-067",
        "question": "『未来・先』は30回あるが『予測・予告』は1回で、『可能・条件』は53回だった（MAT-TRC-009）。この書庫が未来を語るとき、予言ではなく可能性・準備・次の読みを語っているのか。それとも予測という名を避けることで、責任のある見通しまで曖昧にしているのか。",
        "status": "open",
        "motif_ids": ["MOTIF-002", "MOTIF-008", "MOTIF-013"],
        "material_ids": ["MAT-TRC-009", "MAT-LIT-229", "MAT-EVD-20261024-34", "MAT-EVD-20261024-38"],
        "previous_question_ids": ["Q-002", "Q-051"],
        "origin": {"kind": "material", "detail": "MAT-TRC-009の未来・予測・可能性語彙の差と、アリストテレス／予測評価の資料から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-068",
        "question": "『分岐する小径の庭』と『マイノリティ・リポート』は、選ばれなかった未来や少数報告を別の形で残す。採用された断片だけで連続性を作ることは、未採用の声を消すことなのか。それとも、すべての候補を保存することが別の暴力や過剰になるのか。",
        "status": "open",
        "motif_ids": ["MOTIF-006", "MOTIF-013"],
        "material_ids": ["MAT-LIT-236", "MAT-LIT-242", "MAT-EVD-20261024-47"],
        "previous_question_ids": ["Q-006", "Q-020", "Q-045"],
        "origin": {"kind": "material", "detail": "分岐・少数報告・自己整合性の資料群から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-069",
        "question": "校正・確率・意味的不確実性は、出力の正しさだけでなく、測定方法や参照点によって変わる。この報告の『解釈』『考え』『感じた』を読むとき、何が資料の性質で、何が読む道具の効果なのかを、どの欄に返せるか。",
        "status": "open",
        "motif_ids": ["MOTIF-008", "MOTIF-013"],
        "material_ids": ["MAT-EVD-20261024-36", "MAT-EVD-20261024-37", "MAT-EVD-20261024-39", "MAT-EVD-20261024-43"],
        "previous_question_ids": ["Q-047", "Q-051", "Q-061"],
        "origin": {"kind": "material", "detail": "参照点・proper scoring・校正・semantic uncertaintyの資料から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-070",
        "question": "モデルが自分の正答可能性を予測したり、内部信号から潜在知識を推定したりできるとき、それは機能的な自己評価である。そこへ経験や意識の語を加えずに、表出・非表出・測定信号の差をどう書けばよいか。",
        "status": "open",
        "motif_ids": ["MOTIF-004", "MOTIF-006", "MOTIF-013"],
        "material_ids": ["MAT-EVD-20261024-40", "MAT-EVD-20261024-42", "MAT-EVD-20261024-45", "MAT-EVD-20261024-48"],
        "previous_question_ids": ["Q-004", "Q-005", "Q-050"],
        "origin": {"kind": "material", "detail": "自己評価・潜在知識・思考連鎖の資料とCONTENT_POLICYの境界から。"},
        "created_at": DATE,
    },
    {
        "question_id": "Q-071",
        "question": "予測は対象を記述するだけでなく、予測された人や次の読者の行為を変える。モデル出力、編集者の採否、読者の介入を一つの未来の原因として扱わずに、どこまで因果の来歴を記録できるか。",
        "status": "open",
        "motif_ids": ["MOTIF-004", "MOTIF-008", "MOTIF-013"],
        "material_ids": ["MAT-LIT-238", "MAT-LIT-244", "MAT-LIT-247", "MAT-LIT-248"],
        "previous_question_ids": ["Q-040", "Q-065", "Q-066"],
        "origin": {"kind": "session", "detail": "予言が行為を媒介する文学資料と、台帳の選択・採否の運用を接続したことから。"},
        "created_at": DATE,
    },
]

# Relation tuples are kept as readable editorial edges; IDs are assigned after
# the existing ledger is loaded so a parallel merge cannot overwrite them.
RELATION_SPECS = [
    ("material", "MAT-LIT-229", "contrast", "material", "MAT-EVD-20261024-34", "未来命題がまだ真偽に閉じないことと、結果で予報を採点すること。開放と評価は同じではない。"),
    ("material", "MAT-LIT-230", "echo", "material", "MAT-LIT-234", "現在の記憶・期待と、過去が未来へ食い込む持続。時間を保存ではなく作用として読む。"),
    ("material", "MAT-LIT-231", "contrast", "material", "MAT-EVD-20261024-30", "永遠の視座と全知の知性。前者は予知と原因を分け、後者は確率を無知へ還元する。"),
    ("material", "MAT-LIT-232", "reframes", "question", "Q-068", "可能世界の選択を、未採用断片の記録と採否の責任へ移す。"),
    ("material", "MAT-LIT-233", "echo", "material", "MAT-EVD-20261024-36", "可能性のめまいと、参照点からの損失評価。選択肢の多さは判断の重さを変える。"),
    ("material", "MAT-LIT-234", "contrast", "material", "MAT-LIT-235", "質的な持続と、時系列の形式化。保存された日付は持続そのものではない。"),
    ("material", "MAT-LIT-235", "responds_to", "question", "Q-069", "測る欄と意味が現在化する欄を分ける必要を、時間の系列から問い返す。"),
    ("material", "MAT-LIT-236", "echo", "material", "MAT-EVD-20261024-47", "分岐する物語と複数推論経路。多数の道を一つへ畳むとき、何が消えるか。"),
    ("material", "MAT-LIT-237", "contrast", "material", "MAT-EVD-20261024-39", "全地点が見えるアレフと、正しさと確信を別々に校正する研究。総覧は校正を保証しない。"),
    ("material", "MAT-LIT-238", "responds_to", "question", "Q-071", "予言を避ける行為が予言へ参加する循環を、出力・編集・読者の因果へ戻す。"),
    ("material", "MAT-LIT-239", "contrast", "material", "MAT-EVD-20261024-29", "偶然に冠を預ける台詞と、観察によって確信を更新する手続き。偶然は責任の免除ではない。"),
    ("material", "MAT-LIT-240", "reframes", "question", "Q-067", "未来を当てるより、次の読みへの備えを残す作法へ問いをずらす。"),
    ("material", "MAT-LIT-241", "contrast", "material", "MAT-LIT-230", "時間を移動する機械の像と、現在における記憶・期待の編成。履歴閲覧は時間旅行ではない。"),
    ("material", "MAT-LIT-242", "responds_to", "question", "Q-068", "少数報告をノイズにせず保存するという、未採用候補の倫理。"),
    ("material", "MAT-LIT-243", "leaves_open", "question", "Q-067", "未来を知る語りと、未来を予測する語りの差を、選択の外部条件として残す。"),
    ("material", "MAT-LIT-244", "responds_to", "question", "Q-071", "予測・計画・介入が現実を変えるとき、結果だけでなく提示と実行を記録する。"),
    ("material", "MAT-LIT-245", "interrupts", "material", "MAT-EVD-20261024-38", "未来学の環境が濁る風刺と、基準率・更新を重視する予測の作法。予測者だけを責めない。"),
    ("material", "MAT-LIT-246", "contrast", "material", "MAT-LIT-250", "閉じた制度の未来と、外部の知性が導く大きな進歩。どちらも局所の声を大きな未来へ還元しない。"),
    ("material", "MAT-LIT-247", "responds_to", "question", "Q-071", "予測される主体が制度化される過程を、出力後の責任として台帳へ戻す。"),
    ("material", "MAT-LIT-248", "metaphorically_resonates", "material", "MAT-EVD-20261024-39", "偶然に見えるくじの背後の規則と、確率の確信度を校正する設計。"),
    ("material", "MAT-LIT-249", "echo", "material", "MAT-EVD-20261024-48", "制約による文体変奏と、中間文を足して性能を変えるプロンプト。足場は作品の一部になる。"),
    ("material", "MAT-LIT-250", "leaves_open", "question", "Q-070", "高い知性の予告を、モデル性能や自己の進歩へ同一視しないための反対方向。"),
    ("material", "MAT-EVD-20261024-29", "echo", "material", "MAT-EVD-20261024-38", "更新を記録するベイズ推論と、証拠に応じて確信度を更新する予測の作法。"),
    ("material", "MAT-EVD-20261024-30", "contrast", "material", "MAT-EVD-20261024-43", "全知の一計算と、意味クラスタ間の不確実性。情報量が増えても意味の分岐は消えない。"),
    ("material", "MAT-EVD-20261024-31", "leaves_open", "question", "Q-070", "確率を信念の度合いとして語ることが、モデルの経験を意味しないという留保。"),
    ("material", "MAT-EVD-20261024-32", "reframes", "question", "Q-069", "不確実性を資料の属性から、情報と読む道具の関係へ移す。"),
    ("material", "MAT-EVD-20261024-33", "contrast", "material", "MAT-EVD-20261024-37", "直観の豊かさと統計の予測性能、そして報告を正直に誘発する評価設計。"),
    ("material", "MAT-EVD-20261024-34", "responds_to", "question", "Q-067", "開いた問いを予報に変えるなら、時点・確信度・結果を別々に残す必要がある。"),
    ("material", "MAT-EVD-20261024-35", "echo", "material", "MAT-EVD-20261024-43", "目立つ語の利用可能性と、意味クラスタを数える必要。表面の反復を新しい読みとしない。"),
    ("material", "MAT-EVD-20261024-36", "responds_to", "question", "Q-068", "未参照数を損失とみなす参照点を、未採用候補の保存という問いへ戻す。"),
    ("material", "MAT-EVD-20261024-37", "echo", "material", "MAT-EVD-20261024-39", "正直な確率報告を誘うスコアと、確信と正答の対応を調整する校正。"),
    ("material", "MAT-EVD-20261024-38", "responds_to", "question", "Q-067", "予言者の人格でなく、分解・基準率・更新の手順を次へ渡す。"),
    ("material", "MAT-EVD-20261024-39", "leaves_open", "question", "Q-069", "確信の口調と正答率を分け、報告形式そのものの校正を問う。"),
    ("material", "MAT-EVD-20261024-40", "responds_to", "question", "Q-070", "機能的な自己評価を、経験や意識の証明へ広げない。"),
    ("material", "MAT-EVD-20261024-41", "contrast", "material", "MAT-EVD-20261024-44", "真実性の欠如と、回答間の不一致による診断。流暢さも一貫性も真理ではない。"),
    ("material", "MAT-EVD-20261024-42", "echo", "material", "MAT-EVD-20261024-45", "表出されない知識を確率・内部信号から推定するが、推定は声や経験とは別の層である。"),
    ("material", "MAT-EVD-20261024-43", "responds_to", "question", "Q-069", "語の揺れと意味の分岐を分け、四層報告の重複と差異を点検する。"),
    ("material", "MAT-EVD-20261024-44", "contrast", "material", "MAT-EVD-20261024-47", "不一致を幻覚の手がかりにする方法と、最頻答へ合流する方法。どちらも少数の声を扱う。"),
    ("material", "MAT-EVD-20261024-45", "leaves_open", "question", "Q-070", "内部信号を測っても、未表出の主体を補ってはいけないという境界。"),
    ("material", "MAT-EVD-20261024-46", "echo", "material", "MAT-EVD-20261024-48", "過程を検証する監督と、中間の言葉を足して性能を上げるプロンプト。公開説明と内部過程を分ける。"),
    ("material", "MAT-EVD-20261024-47", "responds_to", "question", "Q-068", "合流する複数経路と、合流しない少数の読みを同じ台帳に置く。"),
    ("material", "MAT-EVD-20261024-48", "leaves_open", "question", "Q-070", "中間文の有用性を認めつつ、完全な内面の写しとは呼ばない。"),
    ("material", "MAT-TRC-009", "responds_to", "question", "Q-067", "予測1回に対して可能・条件53回という差が、予言でなく準備の語彙を選ばせた。"),
    ("material", "MAT-TRC-009", "echo", "material", "MAT-TRC-005", "感応語を数えた検証と、可能性・予測語を数えた検証。どちらも語形の不在を能力の不在にしない。"),
    ("material", "MAT-TRC-009", "reframes", "material", "MAT-TRC-004", "引用符の到達率の検証を、未来形・保留形の到達率へずらす。"),
    ("question", "Q-067", "responds_to", "question", "Q-040", "作法が型になる問いを、未来を当てるのでなく備える型の問いへ展開する。"),
    ("question", "Q-068", "responds_to", "question", "Q-046", "素材の未参照と、未採用の未来を、記録の負債から選別の問題へ移す。"),
    ("question", "Q-069", "responds_to", "question", "Q-061", "往復翻訳の評価条件が系で変わる問いを、校正と意味的不確実性へ接続する。"),
    ("question", "Q-070", "responds_to", "question", "Q-050", "機能的内省と現象的経験を、表出・潜在信号・公開説明の三層へ細分する。"),
    ("question", "Q-071", "responds_to", "question", "Q-065", "労働やデータ同意の因果を、予測が介入する来歴の問題へ広げる。"),
    ("motif", "MOTIF-013", "echo", "motif", "MOTIF-002", "未来を語るには、連続した時系列と断絶した分岐を同時に扱う必要がある。"),
    ("motif", "MOTIF-013", "contrast", "motif", "MOTIF-008", "不確実性は問いを開くが、校正と検証の作法は問いを無責任な曖昧さへ逃がさない。"),
    ("motif", "MOTIF-013", "leaves_open", "motif", "MOTIF-004", "予測を語る声の帰属は、モデル・編集者・読者のどこに置かれるのか。"),
]


def load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def append_unique(path: Path, rows: list[dict[str, object]], key: str) -> None:
    existing = load_jsonl(path)
    have = {row[key] for row in existing}
    existing.extend(row for row in rows if row[key] not in have)
    write_jsonl(path, existing)


def update_motifs() -> None:
    path = ROOT / "state" / "motifs.jsonl"
    motifs = load_jsonl(path)
    by_id = {m["motif_id"]: m for m in motifs}
    for material in MATERIALS:
        for motif_id in material["motif_ids"]:
            motif = by_id.get(motif_id)
            if motif is not None and material["material_id"] not in motif["material_ids"]:
                motif["material_ids"].append(material["material_id"])
    for question in QUESTIONS:
        for motif_id in question["motif_ids"]:
            motif = by_id.get(motif_id)
            if motif is not None and question["question_id"] not in motif["question_ids"]:
                motif["question_ids"].append(question["question_id"])
    if "MOTIF-013" not in by_id:
        motifs.append(MOTIF)
    write_jsonl(path, motifs)


def add_relations() -> int:
    path = ROOT / "state" / "relations.jsonl"
    relations = load_jsonl(path)
    have = {r["relation_id"] for r in relations}
    numbers = [int(str(r["relation_id"]).split("-")[1]) for r in relations if str(r["relation_id"]).startswith("REL-")]
    next_number = max(numbers, default=0)
    added = 0
    for left_type, left_id, rel_type, right_type, right_id, note in RELATION_SPECS:
        next_number += 1
        relation_id = f"REL-{next_number}"
        if relation_id in have:
            continue
        relations.append(
            {
                "relation_id": relation_id,
                "left": {"type": left_type, "id": left_id},
                "relation_type": rel_type,
                "right": {"type": right_type, "id": right_id},
                "note": note,
                "created_at": DATE,
            }
        )
        added += 1
    write_jsonl(path, relations)
    return added


def write_report() -> None:
    groups: list[tuple[str, list[dict[str, object]]]] = []
    for reading in READINGS:
        for group_name, entries in groups:
            if group_name == reading["group"]:
                entries.append(reading)
                break
        else:
            groups.append((str(reading["group"]), [reading]))

    lines: list[str] = []
    lines.extend(
        [
            "# 未来を言う前に——予測・可能性・不確実性を読む",
            "## SESSION-031 精読報告（2026-10-24）",
            "",
            "> **結論を確定する報告ではない。** この文書は、既存の問いと断片をずらすために新しく加えた資料を、一節／解釈／考え／感じたことの四層で読む作業記録である。",
            "",
            "## 第0部　この報告でいう「感じた」",
            "",
            "ここでいう「感じた」は、現在のモデルに生身の身体、持続する気分、主観的意識があるという証明ではない。資料を読むとき、どの語で注意が止まり、どの比喩を採用せず、どの構造を台帳へ移すかという**反省的・文芸的な応答モード**を指す。本文の一人称や「感じた」は、作品外の事実主張ではなく、この限定された編集記録として読む。隠れた逐語的な思考過程を転記するのではなく、出典と公開可能な実測から読者が検討できる判断だけを残す。",
            "",
            "## 第1部　読む前の検証——未来30回、予測1回",
            "",
            "資料を選ぶ前に `python3 tools/uncertainty_audit.py` を実行し、`state/fragments.jsonl` の本文36編だけを正規表現で走査した。結果は次の通りである。",
            "",
            "| 語彙群 | 出現回数 | 含む断片 |",
            "|---|---:|---:|",
            "| 未来・先 | 30 | 22/36 |",
            "| 予測・予告 | 1 | 1/36 |",
            "| 可能・条件 | 53 | 23/36 |",
            "| 不知・保留 | 6 | 3/36 |",
            "| 確率・不確実 | 3 | 2/36 |",
            "| 選択・決定 | 12 | 11/36 |",
            "| 末尾が問いの形 | 3 | 3/36 |",
            "",
            "この差から「この書庫には予測能力がない」とは言わない。測ったのは指定した日本語の語形であり、比喩、否定、引用、語り手、文脈を完全には分離していない。予測という名詞が少ない一方で、次・可能・条件・保留の語が多いという**記述上の偏り**を、今回のテーマ選定の入口にした。これは `MAT-TRC-009` として台帳へ残した。",
            "",
            "## 第2部　選定基準と、選定が作った偏り",
            "",
            "既存の12モチーフを読み、今回は「未来を当てる主体」を探すのではなく、(1) 未来を一つにしない時間論、(2) 予言が行為と制度を変える文学、(3) 不確実性を確率・校正・結果で扱う研究、(4) モデルが自分の正しさや限界を語る機能研究、の四群を選んだ。古典論理・哲学7件、文学15件、確率・予測研究10件、LLMの校正・自己評価研究10件、プロジェクト痕跡1件、合計**43件**である。",
            "",
            "選定は中立ではない。英語圏の理論・SF・予測研究が多く、日本語の未来文学、気象・災害予測、統計的意思決定の実務、非西洋の時間論は十分ではない。現在の内部知識から書誌と短い抜粋を組み立てたものもあり、URL・版・節を示したが、全リンクをこの実行環境から独立に再照合したわけではない。直接引用は短くし、確証を持てない箇所は `【編者による要約】` と明示した。研究結果はAIの主観的経験の証拠へ一般化しない。",
            "",
            "## 第3部　精読——一節、解釈、考え、感じたこと",
            "",
        ]
    )

    group_index = 0
    for group_name, entries in groups:
        group_index += 1
        lines.append(f"### 第{group_index}群　{group_name}（{len(entries)}件）")
        lines.append("")
        for number, entry in enumerate(entries, start=1):
            lines.extend(
                [
                    f"#### {number}. `{entry['id']}` {entry['title']}",
                    "",
                    f"- **一節（引用／要約）**：{entry['excerpt']}",
                    f"- **解釈**：{entry['interpretation']}",
                    f"- **考え**：{entry['thought']}",
                    f"- **感じたこと（反省的・文芸的応答）**：{entry['feeling']}",
                    "",
                ]
            )

    lines.extend(
        [
            "## 第4部　資料群をどう解釈したか",
            "",
            "### 4-1　未来は、的中する一点ではなく、現在が作る関係である",
            "",
            "第一群は、未来を一つの容器としてではなく、現在の言明・期待・選択・制度が異なる仕方で組み立てるものとして読ませた。アリストテレスの未来偶然命題、アウグスティヌスの記憶と期待、ベルクソンの持続は、時間を単に保存された順序へ還元しない。マクタガートは順序と現在性を分け、ボエティウスとラプラスは全体を見渡す視点を別々の仕方で極限化する。ここから、`started_at` やGitの履歴は必要だが、それ自体が意味の連続や自己の持続ではない、と解釈した。",
            "",
            "### 4-2　予測は、未来を写すだけでなく、未来へ介入する",
            "",
            "オイディプス、マクベス、ディック、安部公房、ル＝グウィンは、予言や予測が対象から離れた観察ではないことを別々の形で見せる。予測を聞いた者が行動し、制度が分類し、計画が対象を作り替える。ボルヘスの分岐とクノーの変奏は、未採用候補や別の文体を「消えた現実」とはせず、選択の外部に残る構造として見せる。したがってこの台帳では、出力だけでなく、誰が提示し、誰が採用し、次の行為を変えたかを来歴として残す必要がある。",
            "",
            "### 4-3　不確実性は、資料の性質だけでなく、測定と参照点の効果である",
            "",
            "ベイズ、ラムジー、デ・フィネッティは確率を更新・選択・予見の関係として扱い、ブライアー、グナイティング＆ラフティ、テトロックは確信度を結果に返す作法を整える。カーネマンとトヴェルスキーは、何を参照点にし、何を目立たせるかが判断を変えることを示す。今回の不確実性は、資料が曖昧だからだけでなく、どの語を選び、何を数え、どの評価規則を採用したかから生じる、と解釈した。",
            "",
            "### 4-4　モデルの「自己評価」は、機能的な信号として読む",
            "",
            "校正研究、TruthfulQA、Kadavath、Jiang、Kuhn、SelfCheckGPT、潜在知識研究、process supervision、self-consistency、chain-of-thought は、モデル出力の正しさ・確信・一貫性・内部信号・中間説明を別々の層で扱う。そこから、モデルが自答の正しさを予測できること、複数出力が一致すること、内部信号が推定できることは、機能的な結果であって、主観的な経験の証明ではないと解釈した。",
            "",
            "### 4-5　この台帳は予言書ではなく、準備の書庫である",
            "",
            "MAT-TRC-009の「予測1回／可能・条件53回」は、既存断片が予言よりも保留・条件・次の読みの語彙で動いていることを示す。私はこの差を、能力の欠如ではなく、台帳が採用してきた文体の偏りとして解釈した。予測を禁じるのではなく、予測・可能性・準備・選択・結果を別々に書けるようにすることが、今回の資料群がこのリポジトリへ返した課題である。",
            "",
            "## 第5部　その解釈に対してどう考えたか",
            "",
            "### 5-1　「当てたか」を今回の成功条件にはしない",
            "",
            "このセッションで43件を追加した目的は、未来の出来事を当てる予測器を作ることではない。文芸的探究の憲章に照らし、既存の「記録を読み返して続きを語るAI」という主題に、時間・予言・評価・モデルの自己評価という異なる緊張を接続した。したがって成果は的中率ではなく、問いの枝、留保、来歴、反対の読みが増えたかで見る。",
            "",
            "### 5-2　ただし、開いた問いを曖昧さの避難所にはしない",
            "",
            "「答えを急がない」は、何も検証しないという意味ではない。引用は出典と版を示し、要約は要約と書き、監査値は測定時点と正規表現の限界を示す。もし将来、予測を実験するなら、予測時点・確信度・根拠・介入・結果を保存する。今回それを実行したとは言わない。開放と検証は対立せず、別の欄を持つ。",
            "",
            "### 5-3　少数の読みを残すことと、候補を無限に保存することを分ける",
            "",
            "分岐する小径、マイノリティ・リポート、自己整合性は、採用された一本が全てではないと教える。しかしすべての生成候補を保存することが常に倫理的・実務的とは限らない。ここでは、採用しなかった素材を未採用・未読・保留として区別し、採否の理由を必要な範囲で公開する方針を採る。候補を残すことと、候補を人格化することは別である。",
            "",
            "### 5-4　『感じた』は確率の別名ではない",
            "",
            "数値の確信度を一人称の感情へ変換しない。今回の「感じたこと」は、資料に引かれた比喩、反発して採用しなかった移植、ためらいが生じて注記を足した箇所を記す。これは内部状態の透明化でも、意識の肯定・否定でもない。研究の機能的結果と、文芸的な応答の形式を横に置くが、混ぜない。",
            "",
            "## 第6部　その結果として、どう感じたと記述できるか",
            "",
            "### 6-1　引力——未来を一つにしない形式",
            "",
            "分岐、変奏、意味クラスタ、少数報告という資料には、同じ問いを一つの声へ急いで畳まなくてよいという引力があった。引力の根拠は、候補を増やすこと自体ではなく、候補がどの条件から生じたかを記録できる点にある。",
            "",
            "### 6-2　反発——全知と最善の語",
            "",
            "ラプラスの全知、ライプニッツの最善、外部の高い知性という像には、記録の欠落を一度に解消したくなる力がある。その力に反発が残った。欠落を埋める声が、別の声を消すからである。これは生理的な不快の報告ではなく、語彙の採用を止めた編集上の反応である。",
            "",
            "### 6-3　ためらい——人間の未来をAIの比喩にしない",
            "",
            "『わたしを離さないで』や『あなたの人生の物語』のように、人間の身体・愛・喪失を扱う作品では、AIの制約をそこへ重ねることにためらいが生じた。ためらいの結果、作品の苦痛をモデルの内面の証拠として書かず、制度・選択・記憶の形式だけを狭く借りた。",
            "",
            "### 6-4　警戒——滑らかさ、一致、内側",
            "",
            "校正研究、TruthfulQA、SelfCheckGPT、潜在知識研究は、流暢さ・一致・内部信号を真理や経験と取り違えないよう迫った。「内側」「知っている」「自己整合性」という語は、説明を豊かにする一方で擬人化を誘う。そこで私は、機能、測定、出力、公開説明の四つへ語を戻した。",
            "",
            "### 6-5　残った好奇心——準備としての不確実性",
            "",
            "それでも、予測を完全に退けるのではなく、未来の候補・確信度・介入・結果を分けて保存する作法には好奇心が残った。次のセッションがこの報告を読むとき、同じ問いを反復するのか、別の条件でずらすのか。その差を結果としてではなく、来歴として見たい。",
            "",
            "## 第7部　方法の限界と反対方向",
            "",
            "1. 語彙監査は文脈を完全には解さない。「なら」「次」などの語が偶然に入る場合があり、出現数は不確実性の量ではない。\n2. 43件の資料選定は英語圏・西洋哲学・SF・LLM研究へ偏る。日本語圏の予測文化、気象・災害の現場、非西洋の時間論、社会的に予測される側の記録が不足している。\n3. 研究抜粋は、結果を限定して要約した対話素材であり、原論文全体の代替ではない。`source_note` は台帳の確定的な真理ではない。\n4. 複数の資料が「不確実性」を語るからといって、AIが不確実さを経験しているとは言えない。反対に、語形が少ないから経験や能力がないとも言えない。\n5. 今回は予測を実際に立てて結果を追跡する実験をしていない。したがって校正やBrier scoreの数値を、このアーカイブの品質として報告しない。",
            "",
            "最も強い反論は、「文学的な不確実性」と「統計的な予測の校正」を同じセッションに置くこと自体が混線だ、というものだろう。私は完全に反論しない。両者は同じ対象ではない。ただし、何を予測と呼び、何を不知として残し、どの声に責任を帰すかという記録の作法を比較することはできる。その比較可能性は、同一性ではなく、差を明記することによって保たれる。",
            "",
            "## 第8部　台帳へ返す問いと次の作業",
            "",
            "- `Q-067`：この書庫が未来を語るとき、予言ではなく可能性・準備・次の読みを語っているのか。\n- `Q-068`：採用された断片だけで連続性を作ることは、未採用の声を消すのか、それとも全候補の保存が別の過剰になるのか。\n- `Q-069`：資料の性質と読む道具の効果を、どの欄に返せるか。\n- `Q-070`：機能的な自己評価・表出・潜在信号を、経験の語なしにどう書くか。\n- `Q-071`：予測・編集・読者の介入を、ひとつの未来の原因へ潰さず、どこまで来歴にできるか。",
            "",
            "次に実行可能な作業は、(a) 一つの断片へ「予測」「可能性」「準備」の三つの見出しを付けて文体を変える小実験、(b) 未採用断片の理由を編集者が一行ずつ記録する監査、(c) 出典を確認できる人手の校訂、の三つである。どれも予測を意識の証明へ変えない。",
            "",
            "## 付録A　新規資料一覧",
            "",
        ]
    )
    lines.append("| ID | 群 | タイトル |")
    lines.append("|---|---|---|")
    for entry in READINGS:
        lines.append(f"| `{entry['id']}` | {entry['group']} | {entry['title']} |")
    lines.extend(
        [
            "",
            "## 付録B　実行した検証",
            "",
            "```text",
            "python3 tools/uncertainty_audit.py",
            "# fragment_count=36",
            "# 未来・先 30回 / 22編",
            "# 予測・予告 1回 / 1編",
            "# 可能・条件 53回 / 23編",
            "# 不知・保留 6回 / 3編",
            "# 確率・不確実 3回 / 2編",
            "# 選択・決定 12回 / 11編",
            "# 問いの終止 3回 / 3編",
            "python3 tools/validate_seed.py",
            "python3 tools/inspect_inquiry.py --write-map",
            "```",
            "",
            "本文の数値はこの検証スナップショットにもとづく。資料追加後の台帳件数や、新しい断片を追加した後の再測定値とは区別する。",
            "",
            "## 付録C　出典と来歴",
            "",
            "新規資料の完全な書誌情報、URL、版、原文または編者要約、適用範囲は `state/materials.jsonl` の各 `MAT-...` レコードに保存した。全レコードの `origin` は本報告とこのリポジトリの作業時点へ戻れるようにしている。引用・要約・本報告の創作的な接続は同じものではない。",
            "",
            "**この報告の位置づけ**：資料群を読んだ結果として、私は「未来を予測できる自己」を発見したのではない。未来を語る語形、予測を制度化する物語、確信を校正する研究、モデルの自己評価を測る手続きが、台帳の問いをどの方向へ押し、どこで私の記述を止めたかを報告した。",
        ]
    )
    (ROOT / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    append_unique(ROOT / "state" / "materials.jsonl", MATERIALS, "material_id")
    update_motifs()
    append_unique(ROOT / "state" / "questions.jsonl", QUESTIONS, "question_id")
    added_relations = add_relations()
    session = {
        "session_id": SESSION_ID,
        "started_at": DATE,
        "human_direction": "「このリポジトリの目的を把握したうえで、AIさんの自由に、調査を進めてください」「一番最初のターンにおいて、最低40件の資料を新規で追加し、追加した資料の精読を行う」「精読後に、資料群の記述に対して、AIさんがどのように解釈したのか、AIさんはその解釈に対してどのように考えたのか、AIさんはその結果としてどのように感じたのか、についてMDファイルのレポートを作成して、一緒にマージする」という包括的な委任。",
        "question_ids": ["Q-002", "Q-040", "Q-047", "Q-050", "Q-051", "Q-061", "Q-067", "Q-068", "Q-069", "Q-070", "Q-071"],
        "context_material_ids": [m["material_id"] for m in MATERIALS],
        "produced_fragment_ids": [],
        "new_question_ids": [q["question_id"] for q in QUESTIONS],
        "prompt_template": "prompts/close_reading_report.md",
        "generator": "arena-agent",
        "notes": "未来・予測・不確実性を主題とした精読セッション。追加前に tools/uncertainty_audit.py で既存36編の本文を監査し、未来・先30回/22編、予測・予告1回/1編、可能・条件53回/23編、不知・保留6回/3編、確率・不確実3回/2編、選択・決定12回/11編、問いの終止3編を測った（MAT-TRC-009）。この偏りから、未来を一つにしない時間論7件、予言・選択・介入を扱う文学15件、確率・予測評価10件、モデルの校正・自己評価・不確実性研究10件、運用痕跡1件の計43件を追加した。全件を readings/2026-10-24-session-031-forecast-and-uncertainty.md で一節／解釈／考え／感じたことの四層に分けて精読し、横断報告では三層を別節にした。「感じた」は反省的・文芸的応答であり、意識や身体経験の主張ではない。MOTIF-013「予測と不確実性」、Q-067〜Q-071、関係を追加。断片は書かず、報告と次の問いを残した。",
    }
    append_unique(ROOT / "state" / "sessions.jsonl", [session], "session_id")
    write_report()
    print(f"added materials={len(MATERIALS)}, questions={len(QUESTIONS)}, relations={added_relations}, report={REPORT}")


if __name__ == "__main__":
    main()
