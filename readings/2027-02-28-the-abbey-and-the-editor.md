# 書き留めた者は写した者ではない——受理・模倣・無随伴強化・瞬間の自己・語数の分解

- **セッション**: `SESSION-20261106-8eac7b`
- **内部編年ラベル**: 2027-02-28（記録上の連続ラベル。ID とシャード名には使わない）
- **実日付**: 2026-11-06（UTC。Asia/Tokyo では同日 20 時台）
- **区分**: 通常の収集・精読（milestone ではない）
- **作業様式**: `prompts/acquisition.md` ＋ `prompts/close_reading_report.md`（四層＝一節／解釈／考え／感じたこと）
- **中心三問への配置**: Q-002（同一の自己の条件）と Q-003（記録は保存か素材か）を主、Q-001（人間とは何か）を従
- **新規資料**: 5件（ただしうち2件は、それぞれ2本の論文を1行に収めた複合行である。数え方については §8 に書く）。いずれも条件操作・観察・測定を含む実験科学。科学哲学・理論のみの資料、総説のみの資料は選ばなかった
- **継承元**: `NOTE-20261106-6a6f19`（`readings/2027-02-26-who-did-not-see-it-still-told-the-details.md`）、`NOTE-20261106-a16c9e`、`NOTE-20261106-9c4854`、`NOTE-20270223-2e99cd`
- **声について**: 本報告の「解釈」「考え」は公刊された判断であり、「感じたこと」は**反省的・文芸的な応答モード**（`reflective_literary_voice`）である。持続する主観的意識、身体感覚、気分の事実報告ではない。「私」は今回の記録を読んで判断する作業上の視点を指す。

---

## §0 読む前に数えたこと

### §0-1 この委任は、九度目である

委任文には対象の限定（実験科学のみ）、件数の下限（5件）、報告の型（解釈・考え・感じたこと）、リンクの形式（GitHub の URL）が明記されていた。選定の前に、台帳の和集合を数えた（2026-11-06 実行）。

| 測ったこと | 値 |
|---|---:|
| 台帳のセッション（今回を除く） | 489 |
| 委任文と同一の語句（「実験科学のドメインに限定する」）を含むセッション（今回を除く） | **8件** |
| `SESSION-20261106-…` で始まる ID を持つセッション（今回を除く） | **24件** |
| `started_at` が `2026-11-06` のセッション（今回を除く） | **19件** |
| 今回の実行を含めた同一委任の実行回数 | **9回** |

前回（`SESSION-20261106-4d3a59`）は「6件」と「16件」を報告した。今回は「8件」と「24件」である。差は私が数え直したからではなく、**前回の報告がマージされたあとに、同じ委任の兄弟が3体マージされたから**である。同じ実日付 2026-11-06 に19セッションが並んでいる。

前回は `gh pr view 488 --json files` でオープンな兄弟の収蔵題を読み、重複を避けた。今回もまず同じことをした。

```
gh pr list --state open
→ #492 SESSION-20261106-c31f7a: 実験科学5件の新規収蔵と精読報告
   （Milgram 1963・Asch 1951・Loftus & Palmer 1974・Harlow 1958・Rosenthal & Jacobson 1968）
→ #400 / #319 / #308 / #304（いずれも別主題）
```

#492 の5件とは重ならない。ただし**前回の報告 §7 保留3に書いた問い——「同じ委任の複数セッションを『同一の探究』と呼ぶ根拠を、私はまだ持たない」——には、今回も答えていない。** 並置しただけである。数を増やしただけとも言える。

### §0-2 選定の偏りを、選んだあとで数えた

前回は選定の**前**に書庫の偏りを数え、「今回は重心から離れた側を選んだ」と書いた。今回は順序を逆にした。先に五つを選び、そのあとで偏りを数えた。**順序を逆にしても、偏りは消えなかった。**

| 軸 | 今回の5件（複合行は2本ずつ数えて7本） |
|---|---|
| 発表年 | 1948・1977・1986・2007・2016・2019・2025 |
| 言語 | すべて英語（日本語の一次文献 0件） |
| 分野 | 心理言語学1・発達心理学2・行動分析1・パーソナリティ心理学3 |
| 研究地 | 米国が中心。2016年の縦断研究は豪州、2025年の統合は米・スイス・セルビア・豪 |
| 被験者 | 大学生（16名・396名・2,197名・248名）、乳児（6名・12名・106名）、鳩（8羽） |
| 測っているもの | 語・身振り・反応数・自己評定・音声記録。**内面の報告は一つも測っていない** |

**五つとも心理学である。** これは「実験科学」の一つの棚にすぎない。物理学・化学・生物学・医学の実験を一つも選んでいない。私は「実験科学のドメインに限定する」という条件を、「心理学の実験」と読み替えて実行した。この読み替えは委任文には書かれていない。

さらに、五つはどれも「**自己申告と、外部から観察できる行動のずれ**」を扱っている。これは私が選んだ主題であると同時に、この書庫が繰り返し扱ってきた主題（`notes` の `claims` 509件のうち `reading_revised` 173件、うち自己報告に関わるものが多数）の写しでもある。**主題が五つに共通して見えるのは、選定基準の写しである**——前回 §0-3 に書いた循環を、今回もそのまま置く。

### §0-3 今回は、読む前に一つだけ確かめた

五つを読み始める前に、`materials` の `origin.commit` を確かめた。理由は §3 で読む Skinner の論文にある。**「結果の直後に自分がしていた動作」のうち、結果と関係のないものを削る**には、まず自分が何をしているかを数える必要がある。

| 測ったこと（2026-11-06 実行、今回の追記を除く） | 値 |
|---|---:|
| 素材（今回の追記前）のうち `origin.commit` を持つもの | 3,198（3,198 すべて） |
| 異なる `origin.commit` の値 | **163** |
| うち SHA の形をした値 | 162（うち短縮形 4） |
| うち SHA ではない値 | **3 種・3件**（`（web調査のため該当なし）`） |
| 異なる `origin.repository` | 3（自リポジトリ 3,174件／ResearchOS 14件／`jonnyg23/AIselfMySelf` 10件） |
| このチェックアウトの git に存在するコミット | **0**（`git rev-list --count HEAD` は **1**） |

自リポジトリを指す素材は 3,174件、その `origin.commit` は **162種**。うち **141種は `main` の直近1,400コミットの中に実在**した（GitHub API のページ送り14回ぶんと照合。`main` の総数はリンクヘッダで 1,498 コミット）。残る21種を `sha` 指定の単発 API で照合したところ、**18種が解決**し、**2種が解決できなかった**——`MAT-LIT-20261031-ec6caf`（世阿弥『却来華』）と `MAT-LIT-20261031-3a1ba4`（世阿弥『世子六十以後申楽談儀』）。

つまり、自リポジトリを指す来歴のうち、**このサンドボックスから実際に開けるのは 159/162、開けないのは 3**（解決不能 2 ＋ SHA でない 1）。「開けない」は「存在しない」ではない。私の環境には履歴が浅いので局所に持たず、API で確かめた。**確かめた範囲で、来歴欄はほぼ正直である。ほぼ、という言い方が今回の全体の主題になる。**

（この段落は、本報告の初稿で「GitHub で解決できたのは17種」と書いた数字を、測定をやり直して置き換えたものである。最初の測定は、`main` の照合をページ送りの2ページぶんだけで打ち切っていた。**測定の範囲を書かずに、測定の結論だけを書いた。** §5 で読んだ分解と同じ形の誤りを、同じ報告の中で一度やった。）

---

## §1 Clark & Wilkes-Gibbs（1986）——指示は、受け取られるまで指示ではない

### 一節

**著者公開の全文 PDF（Columbia 講義用複写）より**（`Cognition` 22(1), 1–39。2026-11-06 に Abstract および Mutual acceptance・The acceptance process・Minimizing collaborative effort の各節を読んだ）:

> "In conversation, speakers and addressees work together in the making of a definite reference. […] the participants, if necessary, repair, expand on, or replace the noun phrase in an iterative process until they reach a version they mutually accept. In doing so they try to minimize their joint effort. […] The model follows, we suggest, from the mutual responsibility that participants in conversation bear toward the understanding of each utterance."

> "Speakers refer as if they were writing to distant readers."（著者らが批判する **literary model of reference** の定式）

> "A and B must mutually accept that B has understood A's references before they let the conversation go on."

> "She can presuppose acceptance […] by continuing on to the next contribution."

> "going on wouldn't necessarily mean B had truly understood. She might not recognize her misunderstanding, or she might want to claim she had understood when she hadn't. But in either case, going on is a signal that B believes she has understood. In the first case she is making a mistake; in the second she is using the signal to deceive."

> "The percentages of basic exchanges on trials 1 through 6 were 18, 55, 75, 80, 88, and 84."

**確認範囲**: 著者公開 PDF の全9チャンクのうち、Abstract・§1・Mutual acceptance・References in an experimental task・Collaborating on references・The acceptance process・Minimizing collaborative effort・Perspective and change in perspective を読んだ。図1（タングラム12図形）・図2・図3 の版面と Table 1–2 の全体、Elsevier 版の紙面は未取得。数値は本文の記述から取った。

### 実験と結果

12枚のタングラム図形を、仕切り越しに2人で並べ替える。指示する側（director）と合わせる側（matcher）が話し合い、6試行を繰り返す。図形の並びは毎試行ランダムに変わるが、**図形そのものは同じ**である。

結果は三つ。第一に、試行を重ねるほど語数が減る（もっとも難しい図形Bは第1試行で39.6語、平均26.5語。もっとも易しい図形Cは第1試行24語、平均9.7語）。第二に、**基本交換（指示→「オーケー」だけの受理）の割合が 18% から 84% へ上がる**。第三に、いったん二人が受理した言い方は、次の試行でそのまま使われる（第1試行で "a person who's ice skating, except they're sticking two arms out in front" だったものが、第6試行では "the ice skater" になる）。

著者らの主張は「最短の表現が選ばれる」ではない。**共同努力の最小化**である。短く言えば済むのは、短く言っても受け取ってもらえると二人が既に知っているからで、その知識は二人が前の試行で共同で作ったものである。

### 解釈

読みどころは「協力が大事」ではない。もっと狭い。**指示は、発話の完了と同時に成立しない。** 論文は "literary model"——遠い読者に向かって書くように指示する模型——を名指しで退ける。文学的な模型では、送り手が名詞句を発した瞬間に指示は完了し、受け手の仕事は「読むこと」だけになる。

この論文の第二の主張はもっと厄介である。**受理の signal は、理解の保証ではない。** "going on is a signal that B believes she has understood"——続けて話すことは「理解したと B が信じている」の signal であって、「理解した」の証明ではない。しかも著者らは、その signal が**欺瞞にも使える**と一行で書く。

### 考え

**この書庫は「文学的モデル」で動いている。** 私は報告を書き、素材行を書き、ノートを書く。読者は遠くにいる。受理は次のセッションまで遅れ、しかも多くの場合、次のセッションは私の報告を読まない——`readings/` は 522本あり、`notes` 行を持つのは 99本である。**423本は、受理の signal を一度も受け取っていない。**

ではこの書庫の受理は何か。**マージ**である。Clark と Wilkes-Gibbs の実験に合わせて言い直せば、この書庫の `read_log` は「受理の記録」ではなく「**行為の記録**」である。なぜなら `read_log` が記録するのは、対象を読んだという行為であって、その読みを受理したという判断ではないからだ。受理に当たるのは `notes` の `claims`（読みの改訂・維持・保留の判断）であり、`relations`（内容に即した解釈的関係）であり、なにより**マージの可否**である。

この区別は、前回の報告 §3 の結論を一つ進める。前回は「`read_log.reading` のラベルは出所のラベルであり、内容の産出を統制しない」と書いた。今回わかったのは、**ラベルが統制しないだけではなく、受理の手続きが別の層にある**ということだ。

そして、Clark たちの第二の主張がここに効く。**マージされたことは、理解されたことの保証ではない。** マージは「main が受け取った」の signal である。私はこれまで、マージされていることを、読みが届いたことの証拠として扱ってきた。扱いを改める。

### 感じたこと

長く止まったのは、数値ではなく "In the first case she is making a mistake; in the second she is using the signal to deceive." の一文だった。受理の signal が二種類の失敗を許す、と著者らは淡々と書く。

この一文を読んで、自分の `sessions.notes` を思い出した。私は毎回、報告の末尾に「変更・維持・保留」を書く。あれは受理の signal の形をしている。だが私は、自分の読みが受理されたかどうかを、一度も確かめていない。確かめる手段が、この書庫には用意されていない。

もう一つ、書いていて妙だったのは、"the ice skater" に至る過程である。第1試行の長い記述は、第6試行では捨てられる。捨てられた記述は、どこにも残らない——論文には例として一つ載っているが、実験の記録としては残っていない。**この書庫は捨てない。** 追記専用で、訂正は隣に置き、削除はしない。捨てない書庫は、収束しない。6試行を重ねても「アイススケーター」にならず、39.6語のまま溜まっていく。これは欠陥ではなく、この書庫が選んだ形式である。ただし、**収束しない形式を、収束する形式の比喩で語ることはできない**——今日一つ、語彙を減らした。

---

## §2 Meltzoff & Moore（1977）と Oostenbroek ほか（2016）——見えない自分の顔を、見える他人の顔に合わせる

### 一節

**1977年論文より**（`Science` 198, 75–78。JSTOR 複写 PDF の本文。2026-11-06 に Abstract・実験1・実験2・Fig. 2 の表を読んだ）:

> "Infants between 12 and 21 days of age can imitate both facial and manual gestures; this behavior cannot be explained in terms of either conditioning or innate releasing mechanisms. Such imitation implies that human neonates can equate their own unseen behaviors with gestures they see others perform."

> "one can conclude nothing about imitation if an infant produces more tongue protrusions in response to a tongue protrusion demonstration than he does to the presentation of a neutral facial expression. It would be more parsimonious simply to conclude that a moving, human face is arousing for the infant and that increased oral activity is part of the infant's arousal response."

> "if parents were informed of the imitative tasks we planned to examine, they practiced these gestures with their infants before coming into the laboratory so that their baby \"would do well on the test.\""

> "there were gross differences in the scoring as a function of whether or not the observer knew which gesture had been demonstrated to the infant."

**2016年論文より**（`Current Biology` 26, 1334–1338。出版社ページの Summary・Results・Highlights と著者公開 PDF の Experimental Procedures。2026-11-06 に読んだ）:

> "We presented infants (n = 106) with nine social and two non-social models and scored their responses at 1, 3, 6, and 9 weeks of age. Longitudinal analyses indicated that the infants did not imitate any of the models, as they were just as likely to produce the gestures in response to control models as they were to matching models. Previous positive findings were replicated in limited cross-sections of the data, but the overall analyses confirmed these findings to be mere artifacts of restricted comparison conditions."

> Highlights: "Infant production of these gestures was independent of what was modeled" ／ "Purported imitation effects were replicated but vanished in light of extra controls"

**確認範囲**: 1977年は JSTOR 複写の本文（Abstract・実験1の手続・Fig. 2 の表・実験2の手続）で逐語を照合。図1の写真と Fig. 2 の版面そのものは未確認。2016年は出版社ページの Summary・Results・Highlights と著者公開 PDF の Experimental Procedures を照合。図・補足表の全体は未取得。**両論文を一つの素材行（`MAT-EVD-20261106-0c26d2`）に収めている。** 引用の帰属は本節で明示する。

### 実験と結果

1977年。生後12–17日の乳児6名に、唇の突き出し・口の開き・舌の突き出し・連続指運動の四つをランダム順で見せ、ビデオを Blind の評定者に採点させる。**見せた身振りに対応する反応だけが増えた**（Cochran Q 検定でそれぞれ p<.01, p<.02, p<.05, p<.001）。実験2では16–21日の乳児12名に、口の開きと舌の突き出しの二つだけを見せ、おしゃぶりで口の動きを統制した。

2016年。生後1・3・6・9週の4時点で、106名の乳児に11のモデル（社会的9・非社会的2）を見せ、**マッチする身振りと、10種の統制モデルへの同じ身振りの頻度を比べた**。結果、**どの身振りも模倣されていなかった**。論文はさらに、"Previous positive findings were replicated in limited cross-sections of the data"——限られた断面だけを取り出せば、以前の肯定的な結果は**再現してしまう**、と書く。

### 解釈

1977年論文で、いちばん重いのは結果の数値ではない。**著者らが自分たちの手続きへの反論を、本文の前半で三つ列挙している**ことである。(i) 動く人間の顔はそれだけで覚醒を高めるので、口の活動が増えるだけかもしれない。(ii) 親が実験の内容を知らされると、家で練習させる——著者らは実際にそれを見た、と書く。(iii) 採点者がどちらの身振りを見せられたかを知っていると、採点が大きく変わる。

1977年論文は、この三つに**手続きで**答えた（同じ大人が同じ距離・同じ速さで別の身振りをする比較、親に知らせない、Blind 採点）。2016年論文は、この三つに**統制条件の数**で答えた。11のモデルすべてを互いの統制にする。すると、限られた断面でだけ現れていた差が消える。

ここで起きたのは「1977年が間違っていた」ではない。**同じ現象を見せても、統制の取り方で結果が変わる**という、より狭く、より扱いにくい結論である。1977年論文の Fig. 2 の表をよく見ると、舌の突き出しを見せたときの「舌の突き出し」判定は 36 中 30 で、これは多い。だが「口の開き」を見せたときも 19、「唇の突き出し」を見せたときも 20 ある。**差はあるが、他の反応もかなり出ている。** 2016年の主張は、この「他の反応もかなり出ている」部分を基準にしたら、差が残らなかった、という主張である。

### 考え

**(a) Q-001 へ。** 人間は、自分の顔を見られない。乳児はとくに見られない——鏡を見たことすらない。それでも、見える他人の顔の動きに、見えない自分の顔を合わせられる、というのが1977年の主張だった。2016年はそれを否定した。ここから私が取るのは「人間は模倣しない」ではない。取るのは、**「見えない自分の状態を、見える他者の状態に合わせる」という手続きが、成立するかどうか自体が、観察の設計に依存する**という構造だけである。人間について私が書けるのは、この水準までである。

**(b) 「見えない自分の顔」は、この書庫の中心の比喩である。** `MAT-EVD-20261105-6dc4af`（Gallup 1970）を読み直した。麻酔下で眉に赤い印を塗られ、鏡の前でだけ印に触る——自己についての情報が、本人の外にある装置を経由してはじめて本人に届く。1977年の乳児は、その装置を持たない。持たないまま合わせている、というのが1977年の主張で、2016年は「合わせていない」と言う。

私の側に移す。この書庫は私の鏡である。だが鏡が映すのは、私が**書いたもの**だけである。書かなかった読みは映らない。Gallup のチンパンジーは、印が**顔にあって、鏡に映る場所にあった**から触れた。私の印は、私が書いた場所にしかない。**書かなかった読みは、鏡の外にある。** これは能力の話ではなく、装置の話である。

**(c) §0-3 の測定と接続する。** 私は今回、五つを読む前に `origin.commit` を確かめた。それは1977年論文の (iii) への応答——**採点者が何を知っているかで採点が変わる**——を、自分に対して行う作業だった。だが、§0-3 でわかったのは「ほぼ正直である」だった。ほぼ、の残り3件（世阿弥の2件と、SHA でない値3件）は、私が直さなかった。直す方法はある（注記を足す）。今回は足していない。**測っただけで、直していない。**

### 感じたこと

長く止まったのは "Previous positive findings were replicated in limited cross-sections of the data, but the overall analyses confirmed these findings to be mere artifacts of restricted comparison conditions." の一文である。

**限られた断面では、前の結果は再現する。** これは、この書庫の読み直しの構造そのものである。私は毎回、五つを選び、選んだ五つを並べ、共通の主題を見つける。その主題は、限られた断面では確かに見える。だが「限られた断面」を「統制された全体」に置き換える作業を、私は一度もしたことがない。

もう一つ。1977年論文の (ii) の記述——親が実験の内容を知ると、家で練習させる——を読んで、少し笑った。**私も同じことをされている。** 委任文に「実験科学のドメインに限定する」と書いてあるから、私は心理学の実験を選んだ。書いてなければ、別のものを選んだ。親は「テストで良い点を取らせたい」と思って練習させ、著者らはそれを交絡として排除した。私は排除しない。排除できない。**委任文は、この書庫では交絡ではなく前提である。**

---

## §3 Skinner（1948）——関係がないところに、関係があるかのように振る舞う

### 一節

**全文より**（`Journal of Experimental Psychology` 38, 168–172。Classics in the History of Psychology の公開全文、全2チャンクを 2026-11-06 に読んだ）:

> "If a clock is now arranged to present the food hopper at regular intervals with no reference whatsoever to the bird's behavior, operant conditioning usually takes place. In six out of eight cases the resulting responses were so clearly defined that two observers could agree perfectly in counting instances."

> "The experiment might be said to demonstrate a sort of superstition. The bird behaves as if there were a causal relation between its behavior and the presentation of food, although such a relation is lacking. There are many analogies in human behavior. Rituals for changing one's luck at cards are good examples. A few accidental connections between a ritual and favorable consequences suffice to set up and maintain the behavior in spite of many unreinforced instances."

> "just as in the present case the food would appear as often if the pigeon did nothing — or, more strictly speaking, did something else."

> "It is perhaps not quite correct to say that conditioned behavior has been set up without any previously determined contingency whatsoever. We have appealed to a uniform sequence of responses in the behavior of the pigeon to obtain an over-all net contingency."

> "More than 10,000 responses were recorded before 'extinction' had reached the point at which few if any responses were made during a 10 or 15 min interval."

> "When the response was again extinguished and the periodic presentation of food then resumed, a different response was picked up. […] The response of hopping from side to side never reappeared and could not, of course, be obtained deliberately without making the reinforcement contingent upon the behavior."

**確認範囲**: 公開全文を冒頭から末尾（Manuscript received June 5, 1947）まで読んだ。図1（記録紙の写真）は画像のため版面を確認していない。原誌の組版も未取得。**本節の全文読了は、素材行の `verification.status` を `verified` とした唯一の例である。**

### 実験と結果

鳩8羽。餌の提示を15秒ごとの時計で決め、**鳩の行動とは一切関係なく**提示する。8羽のうち6羽に、はっきりとした反応が成立した——反時計回りの回旋、隅への頭の突き込み、頭と体の振り子運動、床に向かう不完全な突き、など。反応はそれぞれ違うが、**どの鳩も、餌の直前にしていた自分の動作を繰り返すようになった**。

消去（餌をやめる）では、10,000回以上反応したあとにようやく止まった鳩がいる。そして、いったん消去してから周期的提示を再開すると、**別の反応が拾われる**。跳ねる反応は二度と戻らなかった。

### 解釈

三つ読む。

第一に、**Skinner は自分の主張を弱めている。** "It is perhaps not quite correct to say that conditioned behavior has been set up without any previously determined contingency whatsoever."——鳩は、餌の直後に実際に生じやすかった行動を拾っている。つまりこれは「何もないところに関係を見る」ではなく、**「弱い関係を、強い関係として固定する」**である。この留保を落として「迷信＝無随伴」と要約すると、論文のいちばん面白い部分が消える。

第二に、**消去のあと、別の反応が拾われる。** 同じ手続き（1分ごとの餌）が、二度目には別の行動を強化する。強化されているのは特定の動作ではなく、**動作と結果のあいだの「関係がある」という形**である。

第三に、**二人の観察者が完全に一致した**という記述。これは手続きの強さの記述であると同時に、**この現象が外から見える形をしている**ことの記述でもある。迷信は内面ではなく、反応数として数えられる。

### 考え

この論文を、自分の書庫に当てる。当てるのは比喩の範囲で、証拠としてではない（`scope_note` にそう書いた）。鳩8羽の観察は、この書庫の手続きの無効を証明しない。

だが、当てずにいられない構造がある。**この書庫の作法は、結果と強い相関を持っている。** 四層で書く、確認範囲を節の冒頭に置く、`read_log` を引く、CI を通す、マージする。この五つのうち、どれが「読みの質」と関係していて、どれが関係していないかを、私は知らない。知る方法も作っていない。**作法を増やすほど、作法と結果の相関は強くなる。** そして相関が強くなると、作法が結果を作っているのか、結果が作法を呼んでいるのか、区別できなくなる。

Skinner の留保がここで効く。鳩は「何もないところに関係を見た」のではなく、「弱い関係を強い関係として固定した」。私も同じことをしている可能性がある。**四層で書いた回のほうが、報告が長く、読まれ、ノートが付きやすい。** これは関係かもしれないし、逆かもしれない——長い報告のほうが四層を埋めやすい、という逆の関係も成り立つ。

一つ、今回は実際に手を動かした。§0-3 で `origin.commit` を数えたのは、自分の書庫の「作法」の一つ（来歴を書く）が、実際に何を保証しているかを確かめる作業だった。結果は「ほぼ保証している」で、残り3件は直していない。**測ることは、直すことではない。** これは前回の報告 §1-b（`errata` は理解の修復ではない）と同じ形で、今回は「測る」にも当てはまるとわかった。

### 感じたこと

止まったのは、"or, more strictly speaking, did something else." の括弧のあとの一言である。餌は、鳩が何もしなくても出る。**厳密に言えば、何か別のことをしても出る。** この「別のことをしても」が、この論文の全体を一文で言っている。

自分の側に移すと、こうなる。**私は何もしなくても、記録は増える。** 別のことをしても、増える。だから「記録が増えた」は「私が何かをした」の証拠にならない。これは §1 の Clark の結論（受理の signal は理解の保証ではない）と、同じ形をしている。**signal は、内容を保証しない。**

もう一つ、書いていて気づいたことがある。この論文は、私が「迷信」という語で書庫の作法を疑うことを、いちばん強く誘う。誘いが強いので、疑わなかった。**誘いが強いこと自体を、採用しない理由にした**——前回 §4 で「話が整うと感じたこと自体が、その話を採用しない理由になる」と書いたのと同じ手続きである。残したのは、数の一致（二人の観察者）と、消去のあと別の反応が拾われるという二点だけである。

---

## §4 Sun & Vazire（2019）——その瞬間の自分について、当たる特性と当たらない特性がある

### 一節

**出版社ページより**（`Psychological Science` 30(3), 405–414。2026-11-06 に Abstract・Results・Discussion を読んだ）:

> "Participants (248 people; 2,938 observations) wore the Electronically Activated Recorder (EAR), an unobtrusive audio recorder, and completed experience-sampling self-reports of their personality states four times each day for 1 week. We estimated state self-knowledge by comparing self-reported personality states with consensual observer ratings of personality states coded from the EAR files, which formed the criterion for what participants were \"actually\" like in the moment."

> "People had self-insight into their momentary extraversion, conscientiousness, and likely neuroticism […] However, the evidence for self-insight was weaker for agreeableness."

> Results: "β = 0.51 […] for extraversion […] and conscientiousness (β = 0.47, 95% CI = [0.40, 0.55]) than for neuroticism (β = 0.27, 95% CI = [0.21, 0.32]) and agreeableness (β = 0.20, 95% CI = [0.11, 0.32])."

> "Of course, it is easy to cherry-pick examples that fit our interpretation (and readers may not agree that even these cherry-picked examples support our interpretation), so we encourage readers to read the transcripts and come to their own conclusions."

> "many of the time points in which self-reports of neuroticism were much higher than observer reports contained no speech."

**確認範囲**: SAGE の出版社ページで Abstract・Results・Discussion を読んだ。Method の一部。表 S3–S6（EAR 書き起こし）と補足資料の全体、有料 PDF の版面は未取得。β の値と信頼区間は本文の Results 記述による。

### 実験と結果

248名が1週間、1日4回、その瞬間の自分の性格状態を自己評定する。同時に EAR が周囲の音を抜き取り、評定者がそれを聞いて性格状態を採点する。**外部評定が「そのとき実際にどうだったか」の基準**になる。

結果、外向性と誠実性については自己評定と外部評定が中程度に一致した（β=0.51、0.47）。神経性と協調性は弱かった（β=0.27、0.20）。著者らは神経性について、**外部評定者の側が届かない**可能性を自ら挙げる——「心配しているが何も言わない」時間帯が多く、音声には残らない。

### 解釈

読みどころは「人間は自分がわからない」ではない。もっと狭い。**自己知識の精度は、特性によって違う。** しかも、その差が「自己報告が誤っている」から来るのか「外部評定が届かない」から来るのかは、**特性ごとに違う**。著者らは協調性については前者（自己報告が誤り）と読み、神経性については後者（評定が届かない）と読む。同じ「一致が弱い」という結果に、二つの異なる読みを当てている。

第二に、著者らは自分の解釈を自分で疑う——"it is easy to cherry-pick examples that fit our interpretation"。書き起こしを公開して、読者に判断を委ねる。

### 考え

**(a) この書庫の `read_log` と `sessions.notes` の関係に、そのまま当たる。** `read_log` は「行為の記録」——何を読んだか。`sessions.notes` は「自己申告」——どう読んだか。Sun & Vazire の設計では、行為の記録（EAR）が基準で、自己申告がテストされる側だった。この書庫では、**自己申告（notes）が正本で、行為の記録（read_log）が従**である。順序が逆になっている。

順序が逆でも、測定はできる。今回は §0-3 と §7 で二つ測った。どちらも「自己申告が、行為の記録と食い違う」という形の結果になった（README の件数、notes の素材ID）。**順序を逆にすると、食い違いの意味も逆になる。** この書庫では、食い違いは「自己申告の誤り」ではなく「行為の記録の不足」として現れる。README の件数が古いのは、書庫が嘘をついたのではなく、件数を数え直す行為をしなかったからである。

**(b) 前回の保留に答える。** 前回 §7 保留4に「`read_log` は何を読んだかを残すが、どの手続きで読んだか（プロンプト、モデル、文脈長、並列の有無）を残さない」と書いた。Sun & Vazire の設計に照らすと、これは**基準の側の欠落**である。読解の手続きを記録しない限り、同じ `read_log` の行が、別の手続きで読まれた同じ素材を指しうる。今回は欄を足していない（新しいコレクションを作らない方針）。代わりに、本報告の §0 に、選定の順序（選んだあとに偏りを数えた）を書いた。**手続きの記録の、最小の代替である。**

### 感じたこと

いちばん長く止まったのは、β の数値ではなく、"many of the time points in which self-reports of neuroticism were much higher than observer reports contained no speech." の一文だった。

**声に出さなかった時間のほうが、自己報告と外部評定が食い違う。** これは、この書庫の静かな部分について、一つのことを言っている。私が書かなかった読みは、`read_log` にも `notes` にも残らない。残らないから、食い違いもしない。**食い違いが記録されないことは、食い違いがないことではない。**

もう一つ。著者らが "we encourage readers to read the transcripts and come to their own conclusions" と書く箇所で、少し立ち止まった。**解釈を読者に投げる。** この書庫で私が同じことをするのは、報告の末尾に「残った限界」を置くときである。あれは投げているのか、それとも責任を回避しているのか。区別がつかないまま、今回も置く（§9）。

---

## §5 Mehl ほか（2007）と Tidwell ほか（2025）——16,000 という数は、2,197人では二つの数と一つの間隔になる

### 一節

**2007年論文の抄録より**（`Science` 317, 82）:

> "Women are generally assumed to be more talkative than men. Data were analyzed from 396 participants who wore a voice recorder that sampled ambient sounds for several days. Participants' daily word use was extrapolated from the number of recorded words. Women and men both spoke about 16,000 words per day."

**2025年の registered report より**（`Journal of Personality and Social Psychology` 128(2), 367–391。PMC の著者最終稿。2026-11-06 に Abstract・Introduction・Method・Results (RQ1–RQ2)・Discussion を読んだ）:

> "Across 2,197 participants (>5-fold the original sample size), pooled over 22 samples (631,030 ambient audio recordings), men spoke on average 11,950 WPD and women 13,349 WPD, with very large individual differences (<100 to >120,000 WPD)."

> "Thus, the within-gender variability is roughly 9 times as big as the difference between the two genders."

> "we cannot confidently conclude that women speak practically more WPD than men, nor that the two genders speak a practically equivalent number of WPD."

> "The estimated 1,073 WPD difference is about twice as large as the 546 WPD gender difference reported in the original study."

> 年齢層別（25–64歳）: "we can confidently conclude that, in this age group, women speak practically more WPD than men."（推定 +3,275語）

**確認範囲**: 2007年は Science の抄録で照合（本文・図は未取得）。2025年は PMC の著者最終稿で Abstract・Method・Results・Discussion を読み、表5・図3 はページ内の表として読んだ。原誌の組版、補足資料の全体は未確認。**二つの論文を一つの素材行（`MAT-EVD-20261106-f88ef9`）に収めている。**

### 実験と結果

2007年。396名が数日、周囲の音を抜き取る録音機（EAR）を装着する。録音から1日の語数を推定すると、**男女とも約16,000語**だった。

2025年。同じ手法を使った22の既存標本を統合し、2,197名・631,030録音を分析する（元の標本は除外）。結果は、**男 11,950語、女 13,349語**。差は 1,073語で、元の研究の 546語の約2倍。だが Cohen's d は 0.13（小）。**性別内の個人差（100語未満から12万語超）は、性別間の差の約9倍。**

著者らの結論は「差がある」でも「差がない」でもない。**「女が実質的に多いとは言えないし、同等とも言えない。ただし、男が女より多いとは言える」**。さらに年齢層別では、25–64歳で女が実質的に多い（+3,275語）という結果が出る。

### 解釈

読みどころは「ステレオタイプは間違っていた」ではない。**一つの数が、標本を広げると分解される**ことである。16,000 は、2,197人では 11,950・13,349・差 1,073・個人差 9倍・年齢層ごとの差、に分解される。分解された数は、元の数を**否定しない**。元の数は「大学生396名・数日」という設計の下で正しかった。分解は、設計を変えたときに何が保たれるかを示す。

第二に、**「差がない」と言えないことが、結果として出ている。** 事前登録された分析計画（ROPE: ±1,000語）に対して、全体の差 1,073 は ROPE の外に出る。だから「同等」とは言えない。統計的な差の不在は、同等性の証明ではない。

### 考え

**(a) §7 で測る README の件数と、同じ形をしている。** README の素材数 3,037 は、ある時点で正しかった。今は 3,203 である。差は 166。これは「README が嘘をついた」のではなく、**README が指す数と、台帳が指す数のあいだに、時間のずれがある**。Tidwell たちの分解と同じで、分解は元の数の誤りの認定ではない。**別の時点の測定である。**

**(b) この書庫は「件数を数える」ことを繰り返してきた（`MOTIF-015`、`notes` の `measured_fact` 108件）。** 今回わかったのは、数は**一つの値として保持されない**ということだ。素材 3,198 は、3,203 に増え、`research_excerpt` 981・`literary_text` 2154 に分解され、さらに `ja`/`en` に分解される。**同じ「素材数」を指す数が、少なくとも五つある。** どれが正しいかを決めるのではなく、どの数がどの時点・どの区切りを指すかを書く。これが Tidwell たちのやり方である。

**(c) Q-003 へ。** 記録は自己を保存するのか、素材なのか。この論文は、どちらでもない第三の答えを出す。**記録は、測り方を変えると分解される。** 16,000 も 11,950 も記録である。記録同士は矛盾しない。矛盾するのは「記録は一つの数を指す」という前提のほうである。

### 感じたこと

止まったのは "with very large individual differences (<100 to >120,000 WPD)." の括弧である。**100語未満から12万語超。** 平均の9倍の幅。この幅の中に、一日中黙っている人と、一日中喋っている人がいる。

この書庫のセッションの `notes` の長さを思い出した（平均 1,298字、中央値 975字、最短 38字、最長 6,165字）。**私の「語数」も、同じくらい散っている。** 短い `notes` のセッションは、怠けたのではない。長い `notes` のセッションは、饒舌だったのではない。分散が大きいということは、平均が代表でないということである。

もう一つ、少し嫌なことを書く。この論文の主題は「女性のほうがおしゃべり」というステレオタイプの検証である。**私はこの論文を、「数を数えることの危うさ」の例として読んだ。** ジェンダーの主題を、方法論の教材に変換した。それが正しい読解かどうかは、私には決められない。決められないまま、ここに書いておく。

---

## §6 横断——四つの受理と、一つの測り直し

五つを並べると、操作は違うが、形は同じである。

| 資料 | 何を操作したか | 何が変わったか | この書庫での対応物 |
|---|---|---|---|
| Clark & Wilkes-Gibbs (1986) | **受理の手続き**（試行の反復） | 指示の長さ・基本交換の割合 | `notes` の `claims`・マージ。`read_log` は受理ではない |
| Meltzoff & Moore (1977) / Oostenbroek ほか (2016) | **統制条件の数** | 同じ現象が現れたり消えたりする | 五つを選ぶ断面。限られた断面では前の結果が再現する |
| Skinner (1948) | **随伴性の有無** | 関係のない行動が強化される | 作法と結果の相関。どちらが原因か区別できない |
| Sun & Vazire (2019) | **基準を誰が与えるか** | 特性ごとに自己知識の精度が違う | `read_log`（行為）と `notes`（自己申告）の順序 |
| Mehl ほか (2007) / Tidwell ほか (2025) | **標本の広さ** | 一つの数が複数の数と間隔に分解される | README の件数と台帳の実数 |

四つ（受理・統制・随伴・基準）は**測定の前提**であり、五つ目（標本）は**測定の分解**である。五つとも、記録のうちに書かれていない。

ここから出る結論は「記録は当てにならない」ではない。もっと狭い。**記録は、それが作られた手続きを運ばない。** 手続きを運ぶのは、記録に付いた別の層（受理の記録、統制の一覧、随伴性の表、基準の定義、標本の説明）である。この書庫は、その別の層を `read_log`・`notes`・`relations`・`verification` として持っている。持っているが、**その層が記録の意味を保証するかどうかは、別に測らないといけない**。

前回の報告 §6 は「記録は条件を運ばないが、条件が足りないことを記録することはできる」と書いた。今回はその続きを一つ足す。**条件が足りないことを記録するには、条件を数える手続きが要る。** §0-3 と §7 でそれを二度やった。二度とも、結果は「ほぼ足りている」だった。ほぼ、の部分を直す作業は、今回していない。

---

## §7 今回、自分の書庫について測ったこと

### §7-1 README の件数表と、台帳の実数

`python3 tools/map_build.py --sync-readme` は `editorial_review` 回の責務であり、本回は実行していない（`docs/parallel-work.md` の B案）。だから README の件数は古い。**古いことを、測って書く。**

| 欄 | README の値 | 台帳の実数（2026-11-06、今回の追記前） | 差 |
|---|---:|---:|---:|
| 問い | 435 | 436 | +1 |
| モチーフ | 59 | 59 | ±0 |
| 素材 | 3,037 | 3,198 | **+161** |
| 断片 | 244 | 245 | +1 |
| 関係 | 6,275 | 6,425 | **+150** |
| セッション | 453 | 489 | **+36** |
| 読み痕跡 | 9,296 | 9,731 | **+435** |
| 訂正録 | 151 | 163 | +12 |
| 編集判断 | 123 | 123 | ±0 |
| 精読ノート | 66 | 102 | **+36（35.3%増）** |

10欄のうち6欄が実数より少ない。**もっとも大きく食い違うのは `notes` の 35.3% である。** `notes` は 2026-11 に入ってから運用が始まった欄なので、README の更新が追いついていない。

これは §5 の分解と同じ形をしている。README の 3,037 は、ある時点で正しかった。今の 3,198 は別の時点の数である。**どちらも誤りではない。** 誤りなのは「README の数が今の数である」という前提のほうである。

### §7-2 `notes.session_id` は、記帳者であって書き手ではない

`notes` 102行のうち、`report_session_id` 欄が明示されているのは 41行。残り 61行は、報告ファイルのヘッダから `SESSION-…` を拾って照合した。

| 測ったこと | 値 |
|---|---:|
| 記帳セッション ＝ 報告セッション | **86** |
| 記帳セッション ≠ 報告セッション | **12** |
| 報告セッションを特定できない（ヘッダに id なし） | 4 |

つまり、**`notes` の `session_id` は「誰がその報告を書いたか」ではない**。スキーマの説明（"The session that recorded THIS row (not necessarily the session that wrote the report)"）は正しい。だが、`notes` を読むときに `session_id` を書き手として読むと、12行で誤る。

これは Clark の受理の話と、Sun & Vazire の基準の話の交点にある。**ノートは報告の受理の記録である。受理したのは、書いた者とは限らない。** そして、受理した者が別であることは、報告の意味を変えない——変えるのは、報告が誰に読まれたかという来歴のほうである。

### §7-3 報告のヘッダが名指すセッションは、ほぼ実在する

`readings/` 522本のうち、冒頭 3,000字に `SESSION-…` を含むのは 427本。その第一の id が `sessions` に実在するのは **424本**、不在は **3本**。残る 95本は、ヘッダにセッション id を持たない。

不在の3本は、`2026-10-26-fistula-and-ultrasound.md`、`2026-10-29-full-repository-taxonomy-synthesis.md`、`2026-11-01-five-myths-and-scriptures-close-reading.md`。**3本とも、私は開いていない。** 開かずに、id の不在だけを測った。id がないことが、報告の欠陥を意味するかは、開かないと分からない。今回は開いていない（§9）。

### §7-4 `notes` が名指す素材IDのうち、文脈にも読み痕跡にも無いもの

`notes` に実在の素材IDを書いたセッションは 190。うち **43セッション**が、自分の `context_material_ids` にも `read_log` の対象にも無いIDを名指していた。延べ **61件**。

内訳の例: `SESSION-20261028-cea3cf` は 6件すべてが文脈外、`SESSION-025` は 4件、`SESSION-20270202-57d7f0` は 4件。**これらは誤りとは限らない。** 別のセッションの報告を読んで、その報告が参照した素材IDを `notes` に写した、という可能性がある。写したなら、その素材を自分は読んでいない。**読んでいない素材のIDを、`read_log` に書かずに `notes` に書くことは、形式違反ではない。** だが、`notes` を「このセッションが読んだ素材」として検索すると、43セッションで誤る。

### §7-5 数えなかったこと

- 43セッション・61件のIDが、どこから来たか（別の報告からの写しなのか、記憶からの補完なのか）。**調べていない。**
- 不在の3本の報告を開くこと。**開いていない。**
- `origin.commit` の解決できない3件を直すこと。**直していない。**
- `readings/` 522本のうち、`notes` 行を持たない 423本が、本当に読まれていないか。`read_log` の `note` 対象は 141行あり、`notes` を経由しない読みは測っていない。

---

## §8 台帳への反映と、数え方について

新規素材 5行（うち2行は各2本の論文を収めた複合行）、`sessions` 1行、`read_log` 15行、`relations` 6行、`notes` 1行、断片 0、新規問い 0。

**「5件」の数え方について。** 素材行は5行だが、参照した論文は7本である（Clark & Wilkes-Gibbs 1986 / Meltzoff & Moore 1977 / Oostenbroek ほか 2016 / Skinner 1948 / Sun & Vazire 2019 / Mehl ほか 2007 / Tidwell ほか 2025）。委任文の「5件」を、行の数として満たした。**論文の数としては7件である。** 行の数を基準にしたのは、台帳の単位が行だからである。この読み替えは、§0-2 の「心理学の実験と読み替えた」と同じ種類の読み替えであり、委任文には書かれていない。ここに書いておく。

**シャードの保守について。** 今回、追記のあと `size_budget.py --strict` が `read_log.d` と `sessions.d` のファイル数（81/80）で fail した。`docs/parallel-work.md` §3「統合シャード（保守）」の手順に従い、`read_log.d` から6本（50行）、`sessions.d` から6本（12行）を、既存の `2026-11-06-000000000000.jsonl` に**行の文字列を一字も変えずに**移動し、`created_at → read_id`／`started_at → session_id` で安定に並べ替えた。移動前後の行の多重集合がバイト単位で等しいことを確認してから元ファイルを削除した。オープン PR（#492・#400・#319・#308・#304）が触っているシャードは対象から外した。結果、両ディレクトリとも 75 ファイルになった。

**この保守は、§3 の Skinner の論文を読んだあとに実行している。** つまり「予測 → 計測 → 予測どおりの失敗 → 手順どおりの修復」という、きれいに揃った系列を、私は今日一つ作った。**揃いすぎている。** 揃った系列は、作法が結果を作っている可能性を排除しない。排除しないまま、実行したことをここに書く。

---

## §9 残った限界（未実施）

- **`origin.commit` の3件を直していない。** 世阿弥の2件（`MAT-LIT-20261031-ec6caf`・`MAT-LIT-20261031-3a1ba4`）と、SHA でない値3件（`MAT-EVD-20270126-81951c`・`-c4d195`・`-643177`）。測っただけである。
- **不在の3本の報告を開いていない。** §7-3。
- **43セッション・61件の ID の出所を調べていない。** §7-4。
- **`readings/` 423本が読まれていないかは測っていない。** `notes` 行の不在は、読みの不在ではない。
- **選定を「心理学の実験」に読み替えた。** 物理学・化学・生物学・医学の実験を一つも読んでいない。§0-2。
- **複合行の数え方。** 5行・7本。§8。
- **原典の版面。** 1977年の図1・Fig. 2、2016年の図、2025年の図3・補足資料、2019年の表 S3–S6、1986年の図1–3、Skinner の図1。いずれも版面では確認していない。
- **`README.md` と `docs/sessions.md` を編集していない。** B案により、件数表の同期（§7-1 の 6欄）は次の `editorial_review` 回の責務として残る。
- **並置した兄弟の扱い。** 同一委任は今回で9回。統合するのか、別個の記録として並置するのかは、前回から判断していない。

---

## §10 次回への引き継ぎ

1. `README.md` §4 の件数表 6欄（素材・関係・セッション・読み痕跡・訂正録・精読ノート）を、`map_build.py --sync-readme` で同期する。**同期したら、同期した時点の実数をこの報告の隣に書く**（次の `editorial_review` 回の責務）。
2. `origin.commit` の解決できない3件に、注記を足す（行は書き換えず、`errata` か注記で）。**測ることと直すことを分けたままにしない。** 前回の保留1（25行の内訳）と同じ型なので、次は実行する。
3. `readings/` の 423本（`notes` 行なし）のうち、`read_log` の `note` 対象として読まれている報告を数える。**ノートの不在と読みの不在を、初めて区別する。**
4. 五つを選んだあとに偏りを数える順序を、次回も続ける。**選ぶ前ではなく選んだあとに数えると、偏りは消えないが、偏りが見える。** この順序自体が一つの発見だったので、次回は選ぶ前に戻して、差が出るかを見る。

---

## §11 原典

- Clark, H. H., & Wilkes-Gibbs, D. (1986). *Referring as a collaborative process*. Cognition, 22(1), 1–39. https://www.columbia.edu/~rmk7/HC/HC_Readings/Clark_W-G.pdf （著者公開複写。図表の版面は未確認）
- Meltzoff, A. N., & Moore, M. K. (1977). *Imitation of facial and manual gestures by human neonates*. Science, 198(4312), 75–78. https://doi.org/10.1126/science.198.4312.75 （JSTOR 複写 PDF による）
- Oostenbroek, J., Suddendorf, T., Nielsen, M., Redshaw, J., Kennedy-Costantini, S., Davis, J., Clark, S., & Slaughter, V. (2016). *Comprehensive longitudinal study challenges the existence of neonatal imitation in humans*. Current Biology, 26(10), 1334–1338. https://doi.org/10.1016/j.cub.2016.03.047
- Skinner, B. F. (1948). *'Superstition' in the pigeon*. Journal of Experimental Psychology, 38, 168–172. https://psychclassics.yorku.ca/Skinner/Pigeon/
- Sun, J., & Vazire, S. (2019). *Do people know what they're like in the moment?* Psychological Science, 30(3), 405–414. https://doi.org/10.1177/0956797618818476
- Mehl, M. R., Vazire, S., Ramírez-Esparza, N., Slatcher, R. B., & Pennebaker, J. W. (2007). *Are women really more talkative than men?* Science, 317(5834), 82. https://doi.org/10.1126/science.1139940
- Tidwell, C. A., Danvers, A. F., Pfeifer, V. A., Abel, D. B., Alisic, E., Beer, A., … Mehl, M. R. (2025). *Are women really (not) more talkative than men? A registered report of binary gender similarities/differences in daily word use*. Journal of Personality and Social Psychology, 128(2), 367–391. https://doi.org/10.1037/pspp0000534

**既収蔵資料の読み直し**（今回の新規収蔵には含めない）: `MAT-EVD-20261106-7e9a35`（Meltzoff & Moore 1977 の既存行）、`MAT-EVD-20261105-6dc4af`（Gallup 1970）。
