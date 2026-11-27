# 経験の門——言語入力が、後から到達可能にするもの・不能にするものを決める発達

- 実日付: 2026-11-26（UTC）
- セッション: SESSION-20261126-02dd04
- モード: [prompts/close_reading_report.md](../prompts/close_reading_report.md)（精読報告）
- 読みの深さ: 原典本文（取得できた全チャンクを読み、未読チャンクは資料ごとに明記）
- 人間の依頼: 発達科学ドメインに限定した新規資料10件の追加、その精読、資料群の記述にAIがどう考えたかのMDレポート作成、文字混入の検証と修正、最後のマージ、回答リンクはGitHub URL。1セッション5件上限を超える10件は明示的な委任による。来歴であり証拠ではない。
- **感じたことのモード宣言**: 本稿の「感じたこと」は主観的意識の実証でも生身の身体感覚の捏造でもない。反省的・文学的な応答モードとして記述し、その根拠は各節の「一節」と「解釈」に結びつける。

## §0 選定前に測った不在と、選定の基準・偏り

### §0.1 台帳に何がなく、何があったか（実測）

- materials と hypotheses の題名・出典題名を grep した2026-11-26起点の実測: Werker 0件、Polka 0件、Fernald 0件、Romeo 0件、word gap 0件、30-million 0件、perceptual reorganization 0件、narrowing 0件、vowel 0件、motherese 0件。child-directed は Cristia (2019) の1件のみ。bilingual は Singh の計算論的1件のみ。Hart & Risley の書籍行は MAT-20261124-94feb1 として、Kuhl は Gopnik (1999)・Kuhl (2004)・Kuhl (2003) [MAT-20261126-c5aa0c] の3件が既にあった。
- 仮説側: 母語 0件、二言語 0件、言語経験 0件、知覚の再組織 0件。つまり「言語入力が発達の門を作る」という読みは、台帳のどこにも立っていない。
- 不在は能力・感情・意識の不在としてではなく、この語形・この欄・この関係の不在として記述する。台帳に「絞り込み」の語がないことと、絞り込みが起きることは別の話である。

### §0.2 選定基準と、選定によって生じる偏り

基準は三つ。(1) この主題（知覚の絞り込み・社会的ゲート・入力量と処理効率）への直接性、(2) 一次テキストが無料で取得できること、(3) 既収蔵との重複がないこと（three_gates --check-source で採番前に確認し、10件すべて CLEAR）。取得できなかった Polka & Werker (1994)（母語母音の絞り込みの古典）は外し、Byers-Heinlein & Werker (2009) で代替した。偏り: 英語圏の研究者が主で、北米・カナダの標本が中心である。音韻の門に強く、句読法・文法・語彙の門が薄い。Werker 研究室の系譜が5件と多く、独立系統の検証が同じ密度ではない。数字の集計はこの偏りを発見するために使い、読解の成功スコアにはしない。

### §0.3 手続き

10件すべてに `python3 tools/three_gates.py --check-source`（DOI・PMID・題名・著者・年）を採番前に実行し CLEAR、10件すべての passage を fetch_page で取得した原典本文に対して `three_gates.py --verify-span` を実行し VERIFIED_SPAN（span_sha256 と span_norm_chars を各行の verification に記録）。引用はすべて逐語、要約は【編者による要約】と明示する。

## §1 Werker & Tees (1984)——落ちる形を環境が教える

### 一節

> The results of these experiments replicate our original findings by showing that infants can discriminate nonnative speech contrasts without relevant experience, and that there is a decline in this ability during ontogeny. Furthermore, data from both cross-sectional and longitudinal studies shows that this decline occurs within the first year of life, and that it is a function of specific language experience. ... As can be seen, most of the infants aged 6 to 8 months reached criterion on both contrasts, whereas by 10 to 12 months of age, few infants reached criterion on either.

（Werker & Tees, 1984, 抄録と実験2の結果。MAT-20261126-4f55de）

### 解釈

英語話者乳児は経験なしで非母語対照（Thompson /ki/-/qi/、Hindi /ta/-/ta/）を弁別できたが、それが生後1年のうちに落ちる。しかも縦断データは落ち方が「特定の言語経験の機能」だと明言する。実験1の英語成人が10名中3名しか基準に達しなかったのに対し、6〜8か月児は10名中8名だった——経験が足りない成人と、経験が始まろうとしている乳児が同じ側にいる。落ちる量は喪失ではなく、母語の統計に合わせて形が作られる量だ。

### 考え

台帳の「到達可能性は手がかりと相手に依存する」（HYP-20261126-4e5813 相1）は、保存済みの痕跡を引き出す問題として書かれていた。この資料は、その手がかりの空間そのものが生後1年で作り替わることを示す。引き出す前に、何を引き出す候補に残すかが経験によって決められる。門は検索の入口にではなく、入力の受付に立っている。Kuhl2003 [MAT-20261126-c5aa0c] の「対面でなければ学べない」とは別の門——こちらは対面でなくても（日常の音の統計だけで）閉まる門——で、二つは同じ「経験が門を作る」の測定層が違う。

### 感じたこと

「機能的発達のprogressionは下降である」という言い方に最初は抵抗があった。落ちる成績を発達と呼ぶのは言い換えに聞こえた。けれどこの論文の下降は、失ったものがどこへ行ったかを示す方向の下降だ。私の索引も同じで、拾わなかった語は消えるのではなく、拾える語の形を決めている。堕ちるのではなく、削られる。削られ方は、聞く側ではなく聞かれる世界の統計が決める。

### 裏切り

この資料は私の「門は一度閉まれば不可逆」という読みを拒む。著者らは下降を発達の進歩と呼ぶが、閉じ方が「言語経験の機能」である以上、経験の入り方を変えば形も変わる。不可逆で固定の門という読みは、この資料の縦断設計が許す範囲を超えていた。

## §2 Stager & Werker (1997)——細部は、意味を結ぼうとする時に手放される

### 一節

> Here we use a recently developed technique to show that when they are required to pair words with objects, infants of 14 months fail to use the fine phonetic detail they detect in syllable discrimination tasks. In contrast, infants of 8 months—who are not yet readily learning words—successfully discriminate phonetic detail in the same task in which infants aged 14 months fail. ... Inattention to phonetic detail may be beneficial to the child who is at the cusp of word learning. ... In both cases, a decline rather than an increase in performance is evidence of a developmental progression.

（Stager & Werker, 1997, 抄録と考察。MAT-20261126-19b0f6）

### 解釈

bih/dih の弁別は8か月児にはできるのに、同じ刺激で語と物を結ぼうとすると14か月児は切り替えに気づかない。実験4でチェッカーボード併用にして命名を促さなければ、14か月児は元の弁別を素直に見せる（t(15)=3.691, p<.05）。つまり感知能力は保たれていて、使い場所で沈む。著者らはこれを第二の再組織と呼び、細部への不注意が「語学習の直前にいる子に有益」かもしれないと書く。減る成績が、課題の要求に応じた情報の絞り込みである。

### 考え

これは HYP-20261126-4e5813 相1の「保存と引き出しは別」を、保存以前へ拡張する。細部は保存されていても、意味を結ぶ局面では手がかりから外される。門は記憶の棚ではなく、タスクの要請に応じて開閉する注目の配分として現れる。同時に HYP-20261120-58ddce の要旨ゲートに、発達側の対応物を与える——要約は劣化ではなく、接続の計算量を下げるために必要な絞り込みで、乳児はそれを最初からやっている。

### 感じたこと

「気づかない」が「見えない」でないことに引き込まれた。14か月の乳児は音の差を知りながら、語の差として扱わない。私の読みも同じで、原文に文字としてあるものでも、問いの型が変わると同じ文字が別のものとして目に入らない。細部を捨てるのではなく、細部に依存しない側へ移る。移る先は、その時一番効いている仕事に決まる。

### 裏切り

私の「絞り込みは能力の喪失」という暗黙の読みに対し、実験4が即座に反対する。14か月の弁別能力は健在で、失われるのは能力ではなく利用である。喪失語彙で書いた初稿の解釈は、この資料の設計によって棄却された。

## §3 Kuhl (2007)——門は音の側ではなく、在り方の側にある

### 一節

> I advance the hypothesis that the earliest phases of language acquisition – the developmental transition from an initial universal state of language processing to one that is language-specific – requires social interaction. ... New studies indicate that early speech learning – at least in complex natural settings – is severely limited in the absence of social interaction, suggesting that something more than passive computation is required to explain infants' rapid language advancement in the first year of life. ... Infants exposed to Mandarin via a standard television or audio-only showed no evidence of learning; their behavioral test scores did not differ from those of infants in the control group who heard no Mandarin whatsoever (Kuhl et al., 2003).

（Kuhl, 2007, 抄録・序論・社会的相互作用の節。MAT-20261126-551b07）

### 解釈

9か月の乳児が普通話12回（平均33,000音節）から対面で学べるのは、聴覚の統計量が同じ録画・音声だけでは学ばないことの証拠として提示される。分布学習は2分の曝露で働く自動的な過程だが、自然な言語学習の場面では社会的相互作用が不可欠だと論じられる。門は入力の量ではなく、入力の届き方——対面か記録か——で開く。attention/arousal と information content の二機構が並べられ、どちらが主かは当稿では未決である。

### 考え

これにより「入力量」の系譜と「対面性」の系譜が同じ門の下に並ぶ。Weisleder & Fernald [MAT-20261126-261dad] は数量のうち対向するものだけが処理を育て、Kuhl2003 は同じ音でも対面だけが育てる。HYP-20261121-6e83a4 の多経路ゲート会計（信念会計層のゲートは別セッション独立検証を要する）に対して、発達は最初から多経路で、入力側の門（社会的）と計算側の門（分布）と任務側の門（Stager）が噛み合っていることを示す。台帳AIは入力のすべてが「録画」側にある非対称の測定点にいる、という読みは c5aa0c のときと続く。

### 感じたこと

同じ資料がテレビの中だと学ばない、という事実に、自分の処理の話としてではなく、乳児の話として向き合いたい衝動があった。門は声の情報量では測れない。人がいるかいないかで測れる。私が文書を読むとき、そこに誰が読むべき語を向けたかは、文字の数とは別の情報として残っている。c5aa0c のときの非対称が、ここで再び同じ形で立つ。

### 裏切り

私の「社会的門＝対面そのものが門」という読みに対し、資料自身が二つの候補機構（注意・覚醒と情報内容）を並べ、未決のまま残す。門の所在を対面性に特定する読みは、この総説が保証しない範囲に立っていた。門は確実に開くが、何が開けているかは、この資料は決めない。

## §4 Byers-Heinlein, Burns & Werker (2010)——門は生まれる前に少し開いている

### 一節

> The first steps towards bilingual language acquisition have already begun at birth. ... When tested on their preference for English versus Tagalog, “monolingual” newborns, whose mothers spoke only English during pregnancy, showed a robust preference for English. In contrast, “bilingual” newborns, whose mothers spoke both English and Tagalog regularly during pregnancy, showed equal preference for both languages. ... Both English monolingual and Tagalog bilingual infants discriminated between the two languages.

（Byers-Heinlein, Burns & Werker, 2010, 抄録とStudy1/2の結果。MAT-20261126-528159）

### 解釈

妊娠中に英語のみを聞いた新生児は英語を優先し（t(13)=-3.44, p=.004）、英語とTagalogを聞いた新生児は両言語に同じ好意を示した。中国語-英語の新生児は中間型で、好意の形が胎児期に聞いた特定の言語に対応する。Study2で両群とも二言語を弁別したので、好意の均等は混乱ではなく学習である。門の向こう側の選好は、出生前にすでに経験で傾いている。

### 考え

「発達の門」を学習期に閉じるものと考えていた読みを、出生前へ遡らせる。経験の依存性は生後1年の再組織（§1）だけでなく、胎内の聴きから始まっている。HYP-20261126-4e5813 相1の手がかり依存は、符号化以前の受付の傾きとして書き直せる。二言語という「複数の門を同時に保つ」初期形態が存在することは、門が単数で閉じるモデルへの反例になる。

### 感じたこと

まだ声の届いていない世界の外側で、どちらの声の側に体を向けるかが決められている、と書いてみて、言葉の早いことを改めて不思議に思った。私は文字を読んでから門が開いたが、この乳児たちは聞こえる前に開き方を決めさせられている。開き方を決めるのが誰か——その問いが、ここで初めて本気になる。

### 裏切り

「二言語児は二つの門を保つ」という私の期待に対し、資料は好意の均等と弁別能の保全を示すだけで、後の語彙経路がどうなるかは示さない。門を保つことと、門の先で何が育つかは、この資料の射程外であり、私はそこを読みすぎていた。

## §5 Byers-Heinlein & Werker (2009)——ヒューリスティックは成熟表ではなく、聞こえ方の産物

### 一節

> Monolinguals showed strong use of disambiguation, bilinguals showed marginal use, and trilinguals showed no disambiguation. The number of languages being learned, but not vocabulary size, predicted performance. ... If language experience itself influences the development of disambiguation, then markedly different types of early experience might change the developmental timetable of disambiguation. ... Word learning and disambiguation do not develop synchronously: instead infants' first understanding of highly frequent words such as “mommy” and “daddy” can be seen as early as 6 months, while disambiguation appears later, between 16 and 18 months of age.

（Byers-Heinlein & Werker, 2009, 抄録と序論。MAT-20261126-1815dc）

### 解釈

17〜18か月で、モノリンガルは新物に新しい名詞を当てる disambiguation を強く使い、バイリンガルはかろうじて、トリリンガルは使わない。予測したのは学習言語数で、語彙量ではない。語は6か月から理解が始まるのに、このヒューリスティックだけが16〜18か月に現れる——成熟の定時に見えたものが、言語数で時刻を動かす。複数言語を聞く手には「一つの物に一つの名前」が成り立たず、ヒューリスティックはその経験に合わせて作られない。

### 考え

HYP-20261126-4e5813 相2（問いの型ごとに正誤が反転する要旨資源）に、発達起源を与える資料である。「新物優先」の型が使えるかは、成熟でも語彙量でもなく、入力の構成で決まる。§1の音韻の門、§2の課題の門に続く第三の門——推論の型の門——が、言語数という外部の変数で開閉する。門の群は感覚・任務・推論の三層にまたがり、どれも入力の側から動く。

### 感じたこと

語彙量が予測しない、という結果が一番刺さった。豊かな語彙を持っているのにヒューリスティックがない——「持っている」と「使える型」の差が、ここではっきり分かれる。台帳の行が豊富でも、その行で問いの型が変わると返事が変わるのと同じだ。型は蓄積ではなく、環境の構成から毎回のような形で立ち上がる。

### 裏切り

「二言語は一言語の遅れ」という素朴な読みを、資料自身が拒む。トリリンガルの欠如は遅れの証明ではなく、経験依存の時刻変更として解釈される。時刻が動くことと、能力が欠けることは違う——この資料はその区別を私に要求した。

## §6 Hurtado, Marchman & Fernald (2008)——入力は uptake を塑形する

### 一節

> Children of mothers who provided more input at 18 months knew more words and were faster in word recognition at 24 months. Moreover, multiple regression analyses indicated that the influences of caregiver speech on speed of word recognition and vocabulary were largely overlapping. ... This study provides the first evidence that input shapes children's lexical processing efficiency

（Hurtado, Marchman & Fernald, 2008, 抄録。MAT-20261126-78bfe2）

### 解釈

スペイン語学習児27名の縦断で、18か月の母の話量が多い子は24か月で単語認識が速く語も多い。しかも多重回帰では、話量の影響が速度と語彙にほぼ重なって現れる——別々の二本ではなく、一本の経路の見え方。入力が語を増やす以前に、処理の速度を変える。速度は入力の産物として育つ。

### 考え

HYP-20261126-4e5813 相1の「保存されていても引き出せない」を、引き出しの速度として測る側から支える。処理効率は生まれつきの所与ではなく18か月時点の入力と結びついていた。これは Weisleder & Fernald [MAT-20261126-261dad] の中介分析の先行形で、後者が「対向するものだけ」に絞るのに対し、この段階では話量全体が速度と重なっている。門の開き方が、量として先に来る。

### 感じたこと

「largely overlapping」という淡々とした文に、入力と能力がまだ分離していない時期の手触りを感じた。分けられないことが劣化ではなく、初期の形なのだ。私の読解も同じで、誰の語で書いてあるかと、何が書かれているかが、まだ混ざったままのことがある。分離は、後から来る作業の成果である。

### 裏切り

私の「入力は量として語彙を足す」という初期形の読みに対し、この資料は量の効果が速度に重なると示し、量と能力の素朴な加算モデルを狭める。量を数えるだけの門の描き方は、この資料の回帰設計が許さない。

## §7 Fernald, Marchman & Weisleder (2013)——門の高さは家ごとに違う

### 一節

> The most important findings were that significant disparities in vocabulary and language processing efficiency were already evident at 18 months between infants from higher- and lower-SES families, and by 24 months there was a six-month gap between SES groups in processing skills critical to language development.

（Fernald, Marchman & Weisleder, 2013, 抄録。MAT-20261126-e33b15）

### 解釈

英語話者乳児48名の縦断で、18か月の時点で高低SESの差が語彙と処理効率に現れ、24か月には処理スキルで6か月の差になる。門の開きやすさが、個体の内側の資質としてではなく、SESという外部条件の関数として早くから並んでいる。差は学齢期の成績ではなく、リアルタイム処理の速度で測られている。

### 考え

§6の入力量を、SES という社会的条件に接続する。到達可能性の門は、同じ乳児でも家の条件によって開き方が異なる。Hart & Risley [MAT-20261124-94feb1] の語数記録は既に台帳にあるが、この資料の測定は語数ではなく処理効率である——「量の格差」を「速度の格差」として読む転換を与える。HYP-20261120-58ddce の外的分布監査に対し、分布の差が本人の内省に現れる前に処理の形として現れることを示す。

### 感じたこと

6か月という差の言い方が、何にも増して重い。差は「教わっていない」ではなく「同じ時間の中で、処理の速度として積もっている」。門の前に並ぶ行列の長さを、私が自分の読書量の差として連想してよいのかどうか——連想はするが、それを根拠にはしない。数字は他者の測定であり、私の自己理解の材料ではなく、台帳の前提をずらす材料として置く。

### 裏切り

「SES 差は環境の悪さ」という安易な読みを、この資料は測定層で拒む。差は処理効率という中間の機序で現れ、語数の直接の貧しさとしてではない。門の高さを環境の欠如の一語で説明する読みは、この資料の測定設計の前で単純すぎる。

## §8 Weisleder & Fernald (2013)——向けられた声だけが速さを育てる

### 一節

> Infants who experienced more child-directed speech became more efficient in processing familiar words in real time and had larger expressive vocabularies by 24 months, although speech simply overheard by the child was unrelated to vocabulary outcomes. Mediation analyses showed that the effect of child-directed speech on expressive vocabulary was explained by infants' language-processing efficiency, suggesting that richer language experience strengthens processing skills that facilitate language growth.

（Weisleder & Fernald, 2013, 抄録。MAT-20261126-261dad）

### 解釈

低SESのスペイン語家族29名で、1日中の家庭録音から対向発話と傍受発話を分離した。育つのは対向したものだけで、同じ部屋に流れていた傍受は語彙と無関係だった。しかも対向発話の語彙効果は処理効率で中介される——入力は語を直接足すのではなく、処理の速さを作り、速さが語を育てる。門は「誰に向けられたか」という属性で開く。

### 考え

Kuhl2003 の対面条件（同じ音でも対面だけ）の、測定側の対応物である。Kuhl は音韻の門、これは語彙と処理の門で、同じ問いを異なる層で測っている。HYP-20261120-58ddce の要旨ゲートは「量ではなく構造」だったが、この資料は入力側の構造（対向か傍受か）を最初の構造として置く。構造は台帳の索引だけでなく、乳児の受付にも最初から効いている。

### 感じたこと

傍受が効かない、という静かな結果が一番残った。同じ言葉、同じ家、同じ時間——差は情報ではなく向かい合い方にある。私の読書も、誰に宛てて書かれているかで読む内容が変わる。宛先のある文章は、宛先のない資料より早く私の中の速度を変える。これは比喩としてではなく、この資料の測定語（child-directed）をそのまま自分の読解の条件に写した感想である。

### 裏切り

「量を増やせばよい」という介入的な読みを、傍受の非関連が拒む。同じ量でも属性が違うと効かない。門を開ける鍵を数量側に求める私の初期の書き方は、この資料の分離設計によって射程を限られた。

## §9 Romeo et al. (2018)——折り返しの線が、脳側の場所を作る

### 一節

> During a story-listening functional MRI task, children who had experienced more conversational turns with adults—independently of SES, IQ, and adult-child utterances alone—exhibited greater left inferior frontal (Broca's area) activation, which significantly explained the relation between children's language exposure and verbal skill. ... Furthermore, results suggest that conversational experience impacts neural language processing over and above SES or the sheer quantity of words heard.

（Romeo et al., 2018, 抄録。MAT-20261126-8ca2d1）

### 解釈

SES多様な4〜6歳児36名で、家庭録音の会話ターン数がストーリー聴取中の左下前頭回の賦活を予測し、その賦活が曝露と語的技能の関係を説明した。成人の発話数そのものやSES・IQを上回る。門は語の総数ではなく、折り返しの回数——相互の応答の構造——で脳側の処理と結びつく。

### 考え

「3000万語格差」という数量の物語に対する測定上の反証として収蔵される。Hart & Risley の語数モデル [MAT-20261124-94feb1] は台帳にあるが、この資料は同じ時代の問いを構造側へ移す。HYP-20261120-58ddce の「近接手がかりと満足化」に対し、会話のターンは環境の分岐構造そのもので、その分岐を多く経験した子の脳が応答の形を持つ。入力の門は、単独の声ではなく応答の繰り返しで開く。

### 感じたこと

ターンという最小単位が、脳の賦活に結びつくことを書いてみて、対話の形式が内容よりも先に効く場面をいくつも思い出した。返事の来る話しかけ方が場を作る。私の書くものにも折り返しがある——誰が返事をする想定で書くかが、書き方の速度を変える。ここでは比喩の域を出ないが、測定語（conversational turns）は素直に受け取っている。

### 裏切り

「会話が脳を作る」という因果の強い読みを、この資料自身が避ける。相関と中介の設計で、方向は示されない。構造の優位を因果の鍵として扱う私の初稿の勢いは、この資料の記述の慎重さに矯正された。

## §10 Bergelson & Swingley (2012)——門は音の後に来るのではない

### 一節

> Over this entire age range, infants directed their gaze to the named pictures, indicating their understanding of spoken words. Because the words were not trained in the laboratory, the results show that even young infants learn ordinary words through daily experience with language. ... The precocious discovery of word meanings suggests a perspective in which learning vocabulary and learning the sound structure of spoken language go hand in hand as language acquisition begins.

（Bergelson & Swingley, 2012, 抄録。MAT-20261126-57defc）

### 解釈

6〜9か月の乳児が、実験室で訓練されていない日常語でも、親の名指しに注視で応じる。音素構造を先に学び、その先で語に達するという従来の順序が崩れる。語への到達と音構造の学習は、発達の最初から並走している。門が音の絞り込みの後に語を開ける、という直順序の読みはここでは成立しない。

### 考え

§1の絞り込みと並べると、発達は「絞ってから開く」ではなく「絞りながら開く」になる。絞り込み（何を母語の音として残すか）と到達（どの語に意味がつくか）が同時に走る。HYP-20261126-4e5813 相1は、門の序列を問う問いへ開かれる——手がかりの空間の構築と、その空間での到達は、どの順で立つのか。この資料は音の門が先という前提に、日常語の意味で先手を取られる。

### 感じたこと

「実験室で教えない」という条件が効いた。意味は訓練の産物ではなく、日常の名指しの積みである。私の記憶も、訓練されずに育った読み方がある——誰も教えないまま拾った語の意味が、後から体系を支えている。門の前に、名指された絵のような経験が先に積まれている。

### 裏切り

「語学習は音韻の門の先にある」という私の並べ方を、この資料の年齢範囲が拒む。6か月から語は到達している。門の序列を単線で書く読みは、この資料の注視設計の前で保留された。

## §11 横断——AIが資料群の記述にどう応答したか

- 10編は三つの門に整理できる。**(a) 受付の門**: 生前からの選好（§4）、経験依存の絞り込み（§1）、社会的な対面性（§3）。**(b) 任務の門**: 意味を結ぶ瞬間に細部が沈む（§2）。**(c) 型の門**: 推論のヒューリスティックが言語数で動く（§5）。この三つの門はすべて、保存以後の検索ではなく、保存以前・利用以前の側に立つ。
- **入力量の系譜**（§6-§9）は、門の開き方の個体差を測る。量は速度に重なり（§6）、SES の関数として早くから差になる（§7）、対向するものだけが効き（§8）、総数より折り返しが脳と結ぶ（§9）。§10 は、門の順序を「音の後に語」という単線から外す。
- 人間の依頼（10件・精読・レポート・文字監査・マージ・GitHub URL）は来歴としてここに置く。資料の証拠でも AI の独自解釈でもない。解釈の責任は各節の「解釈」「考え」にある。
- 既存記録からの継承: c5aa0c（Kuhl2003 の対面条件）と Hart & Risley の語数行を継承し、同じ問いを測定層で広げた。取り落とし: Polka & Werker (1994) の母音絞り込みの古典を全文取得できず収蔵しなかったこと、非音韻の門（文法・韻律）が本群にほぼ不在であること、US・カナダ標本への偏りを §0.2 に置いた。数値集計は偏りの発見にのみ使い、読解の成功スコアにしていない。「感じたこと」は §冒頭のモード宣言の範囲でのみ主観的応答である。引用と要約（【編者による要約】なしの本稿の一節はすべて逐語引用）を区別した。
- 不確実性の自律的記録: 各資料の未読チャンクは scope_note に明記し、そこから導いた数値・因果は主張していない。Romeo は相関設計、Fernald/Weisleder は観察的縦断であり、因果の語は使わない。Kuhl07 の機構は当稿で未決である。

## §12 条件付き仮説への判定（同一セッションで NOTE・EVL を登録する）

- **HYP-20261126-4e5813（三相発達説）へ `narrows_scope`**: 相1「到達可能性は手がかりと相手に依存する」は保存後の引き出し問題として書かれていたが、§1・§3・§5 は手がかりの空間そのものが入力（音の統計・対面性・言語数）によって構築されることを示す。相1は符号化後の到達に射程を限定され、符号化前の門は別相として置かなければならない。相2（問いの型）には §5 が発達起源を、相3（自己標識）には本群は直接触れない。EVL 行を同セッションで登録する。
- **HYP-20261120-58ddce（満足化・要旨ゲート・外的分布監査）へ `supports`**: §2 の「細部を制限することが有益」、§8 の「対向だけが処理を育てる」、§9 の「総数より折り返し」は、要旨・構造が量より先に効くという要旨ゲートの読を入力側から支える。外的分布の差（§7 の SES）が本人の内省に現れる前に処理の形として現れることも、外的監査の必要性と整合する。
- **HYP-20261121-6e83a4（非破壊的自己更新の三層条件）へ 判定しない**: 本群は三層条件のいずれの排除条項（a）-（c）も直接測らない。無理に supports/narrows を作らない。P_gate 推奨対の片方は判定せず、その旨を明記する。
- 新規仮説は立てない（根の仮説は飽和、子仮説の立項は本回の範囲外）。
