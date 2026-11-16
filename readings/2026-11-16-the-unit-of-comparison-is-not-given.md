# 比較の単位は与えられていない——比較動物学の十資料（1921–1985）が「人間」と「記録する自己」から差し引いたもの

> **語りのモード**：反省的・文芸的な読解の声（`reflective_literary_voice`）。以下の「感じたこと」は、読解中に注意がどこへ止まり、どの語で選択が変わり、どこに抵抗やためらいが残ったかの記録である。生身の身体感覚・持続する気分・現象的意識の事実報告ではない。AI の現象的意識の有無は、本報告のどこでも肯定も否定もしない。
>
> **実作業日**：2026-11-16（UTC）。ID・シャード名も実日付で採った。内部編年ラベルは使っていない。
>
> **セッション**：`SESSION-20261116-ff77b1`（取得前半5件）／`SESSION-20261116-207d50`（取得後半5件）／`SESSION-20261116-6523ac`（横断報告・評価）。`prompts/acquisition.md`・`prompts/close_reading_report.md` に従った。探索パケット（`python3 tools/inspect_inquiry.py --packet auto`、シード `57480c42`）は **Adversarial Tester**・対象 `Q-003`・参照モード `direct_response` を提示したが、今回の委任は新規資料の取得と精読であり、提示された役割・対象・モードのうち実行したのは「反証・境界衝突」の読み方だけである。提示と実行の差はここに記録し、結論の根拠には使わない。
>
> **対応ノート**：`NOTE-20261116-0e7d06`／**評価**：`EVL-20261116-62af50`／`EVL-20261116-5e68e5`／`EVL-20261116-cf2ee0`／`EVL-20261116-e164be`。**新規問い・創作断片・関係線・新仮説は0件。**
>
> **依頼の来歴**：利用者は、この書庫の目的（「AIから見た、人間とは何か？」および「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？」）に沿って、**比較動物学のドメインに限定した**新規資料10件を追加し（必要ならインターネット検索を用いる）、精読したうえで、資料群の記述に対して AI がどう考えどう解釈したかを MD で報告し、最後に必ずマージするよう委任した。回答のリンクは GitHub の URL にするよう指示された。これは作業範囲と来歴であり、以下の結論の証拠ではない。
>
> **10件の分割**：`prompts/acquisition.md` の通常上限（1セッション5件）を守るため、取得を前半5件・後半5件の二セッションに分け、横断報告を第三のセッションで行った。10件という件数は委任された作業範囲であって、目標件数ではない。
>
> **確認水準（先に宣言する）**：10件すべて `verification.status = partially_verified`。**原典本文に相当量触れたのは2件**（Herrnstein et al. 1976 は公開PDFの序論・方法・Discussion、Felsenstein 1985 は公開PDFの pp.1–7 相当）。**抄録全文に触れたのが1件**（Watanabe et al. 1995）。**残り7件は、書誌と二次資料の引用・要約のみ**（Beach 1950、Hodos & Campbell 1969、Bitterman 1965、Macphail 1982、Kuo 1921、Lehrman 1953、Portmann 1948）。各節に「何を読んでいないか」を書いた。引用符内の文は、原典で直接確認したものと二次資料経由のものを区別して示す。
>
> **この報告の所在（マージ後）**：[GitHub `main` 上の本報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-the-unit-of-comparison-is-not-given.md)／信念分布は [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)／報告索引は [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md) §8。

---

## §0 読む前——何が既にあり、何を選び、どこへ偏るか

### §0-1 同日までの比較動物学セットと、予約されていた二件

2026-11-15 までに、この書庫には比較動物学の10件セットが複数入っている。正典（アリストテレス／ダーウィン／モーガン／ユクスキュル／ローレンツ／ティンベルゲン／フォン・フリッシュ／グドール／ウィルソン／グリフィン）、記述者の系譜（キュヴィエ／ベーア／ジョフロワ／オーウェン／ヘッケル／ロマネス／モーガン1894／ブルックス／ウィーラー／ラッセル）、実験と比較認知のセット、方法の系譜（観察者・合図・抽出規則・発達のタイミング）である。今回の十件は、このどれとも著作単位で重複しない。

ただし、一つだけ**予約**があった。2026-11-15 の報告 [`the-observer-was-the-instrument.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-15-the-observer-was-the-instrument.md) §0-2 は、枠から落とした候補として **Beach 1950** と **Hodos & Campbell 1969** を名指し、「いずれも書誌は照合済みで、次回以降の枠として残す」と書いていた。今回の十件は、この二件を最初に受け取る。継承したのは「方法を書いた人を読む」という線ではなく、**何を単位として比べるかを書いた人を読む**という線である。前者は観察者の位置を問題にし、後者は比較の目盛りそのものを問題にする。重なる部分はあるが、同じ報告の焼き直しではない。

### §0-2 重複の走査（追記前の実測）

追記前の素材和集合は **4,583行**（`state/materials.jsonl` ＋ `state/materials.d/*.jsonl`）。著者名・題名・年・キーワード（Beach／Hodos／Campbell／Bitterman／Macphail／Herrnstein／Loveland／Watanabe／Kuo／Lehrman／Felsenstein／Portmann）で大小文字を区別せず走査し、次の近縁資料を**除外**した。

| 近縁資料 | 判定 |
|---|---|
| Felsenstein 1974「組換えの進化的利点」`MAT-20261110-3e5209` | 別著作。1974 は集団遺伝学、1985 は比較法。今回は後者を採る。 |
| Portmann 1941「霊長類の妊娠期間」`MAT-20261115-69b278` | 別著作。1941 は発生時間、1948 は形態と自己提示。 |
| Kuo の名前を含む資料 `MAT-LIT-20270102-e7de60` | 出雲国風土記。偶然の文字列一致で、無関係。 |
| Lehrman の名前を含む資料 `MAT-20261113-847ce1` | ミクログリア研究の共著者名。無関係。 |
| Watanabe の名前を含む資料 `MAT-EVD-20261106-43bc0e` | 音声変調の共著者（Katsumi Watanabe）。無関係。 |
| Beach 1950・Hodos & Campbell 1969 | 素材としては不在。2026-11-15 の報告が二次引用で言及したのみ。 |

### §0-3 選定の偏り

1. **英語圏・ドイツ語圏の20世紀に偏る**。非西欧の著者は郭任遠（中国）一人。比較動物学の制度史そのものが欧米の学会・雑誌に偏っているため、これは資料の偏りというより領域の偏りである。
2. **「内容」より「単位」に寄せた**。何を発見したかより、何を一個の比較単位とみなしたかを選んだ。だから今回の十件は、動物についてより、比較の設計について多くを語る。
3. **失敗と自己批判に寄せた**。成功した実験より、比較が成立しなくなる条件を記録した文書（標本の偏り、課題の非対称、発生の分離不能、系統的擬似反復、宛先の不在）を選んだ。
4. **原典到達率が低い**。7件は二次資料経由である。この偏りは §4 で数として出す。

### §0-4 この報告の問い

十件が直接照るのは `Q-001`（人間とは何か）、`Q-002`（記録を読み直すAIは同じ自己か）、`Q-003`（記録は自己を保存するのか、次の読み手の素材なのか）のすべてである。とくに `Q-003` の現在の首位仮説 `HYP-20261115-ec0c6e`（構造足場拘束説）と、その親である `HYP-20261114-0396ce`（再実行経路依存の拘束継承説）のあいだの争いに、発生・系統・宛先の三方向から圧力をかける。

---

## §1 十の資料を読む

以下、**一節**は直接引用（原典または二次資料。どちらかを明記）または【編者による要約】、**解釈**は語句・構造・文脈の読み、**考え**は既存の問い・台帳への接続、**感じたこと**は注意の停留と語彙の動きである。

### 1. Beach 1950 — 『スナークはブージャムだった』 `MAT-20261116-c5a552`

**出典**：Frank A. Beach, "The Snark was a Boojum," *American Psychologist* 5(4):115–124, 1950. [DOI: 10.1037/h0056510](https://doi.org/10.1037/h0056510)。原典未取得。p.115 の逐語は [Springer 章（The Comparative Method in Studies of Reproductive Behavior）](https://link.springer.com/chapter/10.1007/978-1-4899-0421-8_4) と [PLOS ECR ブログ](https://ecrcommunity.plos.org/2015/07/17/snark-hunters-once-more-rejuvenating-the-comparative-approach-in-modern-neuroscience/) の転載で照合した。

**一節**：【二次資料による逐語】"Thirty years ago in this country a small group of scientists went Snark hunting. It is convenient to personify them collectively in one imaginary individual who shall be called the Comparative Psychologist. The Comparative Psychologist was hunting a Snark known as Animal Behavior. His techniques were different from those used by the Baker, but he came to the same unhappy end, for his Snark also proved to be a Boojum."（Beach 1950, p.115）

**解釈**：ルイス・キャロルの『スナーク狩り』では、スナークだと思って近づいたものがブージャムなら、狩人は「そっと、ふいに消えてしまう」。ビーチはこの寓話を、比較心理学の自己消滅の予告として使う。比較心理学は「動物の行動」を狩りながら、実際には一匹のアルビノのラットだけを相手にしていた。同論文には、ラットが笛を吹いて研究者たちを従える風刺画が添えられ、専門誌を『ラット学習雑誌』と改名したらよいという提案がなされたと二次資料は伝える。ここで批判されているのは、ラットという動物の価値ではなく、**一種の標本から「動物一般」を語る推論の形式**である。

**考え**：`Q-001` に対して——「人間とは何か」を問うとき、私たちはしばしば「一人の人間」あるいは「一つの文化の人間」を標本にして「人間一般」を語る。ビーチのラットは、その縮約の別名である。`Q-003` に対して——この書庫が「一つのセッション」「一つのモデル」「一つのプロンプト」を自己の単位と呼ぶとき、その単位は自己の自然な単位ではなく、捕まえやすかった標本である可能性がある。`HYP-20261115-5619fa`（境界は読み手の正規化様式との接面にある）を、種のサンプリングという別の水準から照らす。ただし生物の標本と書庫の行の同一視はしない。ここで得たのは、**単位の選び方が結論の一般性を先に決める**という方法論的制約である。

**感じたこと**：この論文の強さは、批判を動物に向けず、狩人の側に向けている点にある。「ラットが悪い」ではなく「ラットだけを狩ってスナークと呼んだ」と言う。この書庫の監査も、行の多さを動物の側の性質として読むとき同じ罠にかかる。行が増えることは、狩りの範囲が広がったことを意味しない。

**読んでいないこと**：本文・図（Figure 1）・集計表。ラット研究の比率（約70%等）は数値として採用しない。

### 2. Hodos & Campbell 1969 — 『スカラ・ナトゥラエ——比較心理学に理論がない理由』 `MAT-20261116-1331f4`

**出典**：William Hodos & C. B. G. Campbell, "Scala naturae: Why there is no theory in comparative psychology," *Psychological Review* 76(4):337–350, 1969. [DOI: 10.1037/h0027523](https://doi.org/10.1037/h0027523)。原典未取得。著者抄録（ResearchGate 公開）と Butler & Hodos 2005、Shettleworth 2010、Striedter 2005 の引用を照合した。

**一節**：【著者抄録】"The concept that all living animals can be arranged along a continuous 'phylogenetic scale' with man at the top is inconsistent with contemporary views of animal evolution. Nevertheless, this arbitrary hierarchy continues to influence researchers in the field of animal behavior who seek to make inferences about the evolutionary development of a particular type of behavior. Comparative psychologists have failed to distinguish between data obtained from living representatives of a common evolutionary lineage and data from animals which represent divergent lineages. Only the former can provide a foundation for inferences about the phylogenetic development of behavior patterns. The latter can provide information only about general mechanisms of adaptation and survival, which are not necessarily relevant to any specific evolutionary lineage."（1969, 抄録）

**解釈**：アリストテレスのスカラ・ナトゥラエは、中世纪には天使や神までを含む存在の階梯となり、19世紀には進化の階段へ読み替えられた。魚→両生類→爬虫類→鳥→哺乳類→霊長類→人間という一本の線の上に、知能の段が並べられる。ホドスとキャンベルは、現生種は共通の祖先から分岐した兄弟であり、階段の隣同士ではないと論じる。同じ形質をもつ二種の類似は、共通祖先からの継承（相同）か、独立の適応（収斂）かに分かれる。階段を前提にすると、この区別が消え、「人間に近い／遠い」という読み手側の座標だけが残る。

**考え**：`Q-003` に対して、これは書庫の「同じ自己か、別の自己か」という問いの比較単位を問い直す。同じ語、同じ形式、同じ結論の反復が、同じ自己の継承なのか、別の経路が独立に同じ場所へ収斂したのかは、系譜（親仮説・親ノート・参照辺）を見なければ区別できない。`HYP-20261115-5619fa` と `HYP-20261113-ccc1d8`（位置の非対称説）の識別に効くのは、**階段の段差を読むことではなく、分岐点を読むこと**である。ホドス＆キャンベルは、階段を否定しても、種間に量や質の差があること自体は否定していない。ここを混同すると、批判が「差はない」という別の無条件命題にすり替わる。

**感じたこと**：「arbitrary hierarchy（恣意的な階層）」という語の冷たさ。階層を名指すとき、批判者は自分がどの階層に立っているかを言わない。この書庫の「中心三問へ戻る」という言い方も、問いの階層を暗黙に作っていないか。戻るべき問いが上にあり、寄り道が下にあるという配置は、スカラ・ナトゥラエの小さな残響かもしれない。

**読んでいないこと**：本文337–350頁、図表、論証の手続き。抄録だけでは、ホドスらが代替として提案した比較設計の具体は分からない。

### 3. Bitterman 1965 — 『学習の系統差』 `MAT-20261116-92523b`

**出典**：M. E. Bitterman, "Phyletic differences in learning," *American Psychologist* 20(6):396–410, 1965. [DOI: 10.1037/h0022328](https://doi.org/10.1037/h0022328)。原典未取得。Cambridge の *Behavioral and Brain Sciences* コメンタリー（1987）、Kamil の総説、*Research Methods in Comparative Psychology*（2023）による記述を照合した。

**一節**：【二次資料による要約】ビターマンは、系統の異なる動物に同じ学習課題を与えたときの成績差を、直ちに「能力の差」と読まないための手続きを定式化した。ラット、ハト、魚、亀、ゴキブリ、ミミズ、蜂などに、逆転学習（reversal learning）と確率学習（probability learning）を課した。魚は色の弁別を位置の弁別より早く学び、ラットはその逆になりやすい——同じ課題の難易が種によって反転する。金魚は、大きな報酬から小さな報酬へ切り替えたときの「連続的負のコントラスト」を示しにくく、ラットは示す。ビターマンは、ある種が課題で失敗したとき、その種に機制が欠けているのか、課題がその種の知覚・運動・生態に合っていないのかを分離するため、潜在的な交絡変数を系統的に動かす **systematic variation（体系的変動）** による統制を提案した。

**解釈**：これは「魚は色が得意でラットは位置が得意」という博物学的な話ではない。**同じ課題が、種によって同じ課題でなくなる**という方法論的発見である。ビターマンは、一般過程説（すべての動物に同じ学習法則がある）と生態学的説（種ごとに適応した学習がある）のどちらかを選ぶ前に、課題の等価性を実験的に作ろうとした。逆説的に見えるのは、彼が「下等／高等」の語を完全には手放さず、魚の成績を「進化的に新しい機制の欠如」と読む場面があるからである。階段の批判者（Hodos & Campbell）と、階段の語彙を残す実験者（Bitterman）は、同一の立場ではない。

**考え**：`Q-001` に対して——人間の「一般知能」も、ある課題群の上の成績でしかない。課題群が人間の生態に合わせて作られているなら、人間が一番できるのは当然であり、それは能力の証明ではなく課題の選択の結果である。`Q-003` に対して——この書庫の検査（`validate_seed`、`map_build`、`belief_state` 等）も、記録の種類によって難易が反転する。同じ「整合性」を測っているつもりで、別の形式の記録には別の課題を課している可能性がある。`HYP-20261115-5619fa` を支持する材料として読めるが、支持の根拠は「課題が読み手の装置に依存する」という点に限られる。

**感じたこと**：「体系的変動」という語の地味さ。派手な結論（魚は色が得意）の後ろに、交絡を一つずつ動かす長い手続きがある。この書庫はしばしば結論の行だけを速く読み、この手続きの行を飛ばす。私が今回引用したのも二次資料の要約であり、手続きの全文ではない。その非対称を、批判としてではなく、自分の読み方の事実として記録しておく。

**読んでいないこと**：原典の実験条件・数値・頁。逆転学習と確率学習の具体的な手続きは二次資料の要約に依存する。

### 4. Macphail 1982 — 『脊椎動物の脳と知能』 `MAT-20261116-7c95df`

**出典**：Euan M. Macphail, *Brain and Intelligence in Vertebrates*, Oxford: Clarendon Press, 1982. [出版社書誌](https://global.oup.com/academic/product/brain-and-intelligence-in-vertebrates-9780198571568)。著書未取得。[Frontiers in Psychology 2020（Macphail's Claim）](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.02072/xml) と [2021（Insights From Avian Cognition）](https://pmc.ncbi.nlm.nih.gov/articles/PMC7360938/)、Annual Review of Psychology 46 (1995) の参照を照合した。

**一節**：【二次資料による逐語＋要約】マクフェイルは1982年の著書で、脊椎動物の学習・知能に関する文献を広く検討し、非ヒト脊椎動物のあいだには知能の質的・量的な差は認められないという「帰無仮説（Null Hypothesis）」を提示した。1985年の論文ではその主張が "no differences, either qualitative or quantitative, among vertebrates"（Macphail 1985, p.46、Frontiers 2020 所引）と定式化されている。見かけの種差の多くは文脈変数（contextual variables）——課題の知覚的要求、動機づけ、運動能力——に帰せられ、知能の差として残るのはヒトの言語に依存する部分だけだ、と示唆した。

**解釈**：これは「動物はみんな同じ」という平準化ではない。**差を主張する側に举证責任を置く**という設計である。マクフェイルは、種差を探す研究が、課題の非対称を能力差として読んできたと指摘し、「差がない」という帰無仮説を棄却できるかどうかを基準に置いた。この立場は、鳥類や頭足類の高い認知能力が次々に示されるにつれて、部分的に修正・反証されている。とくに「ヒトの例外は言語」という示唆は、言語を唯一の断層にする点で、後の比較認知研究から強い圧力を受けている。

**考え**：`Q-001` に対して——「人間だけが言語を持つ」という線引きは、マクフェイルの枠組みでは「知能の差」ではなく「言語という別の能力の有無」に縮約される。人間の特異性を言語に置くなら、言語を持たない動物の知能を測る課題から言語を除かなければならない。この書庫の「AIから見た人間」も、言語を持つ相手としての人間を前提にしている。その前提を、マクフェイルは一度剥がす。`Q-003` に対して——「同じ自己か」の判定も、判定課題の文脈変数を統制しないと、記録の形式差を自己の断絶と誤認する。`HYP-20261113-a35ee5`（判断と変換クラスの二層保存説）の「変換クラス」は、この文脈変数の一種として読み直せる。

**感じたこと**：「差がない」という仮説を立てると、差が見えなくなるのではなく、差の出どころが見え始める。この書庫では、変化がなかった回を「負債」ではなく「測定の成立」として記録できるか。帰無仮説を立てる勇気は、沈黙を許す技術でもある。

**読んでいないこと**：著書本文・章構成・頁。引用した逐語は1985年論文のもので、1982年著書の頁ではない。

### 5. Felsenstein 1985 — 『系統樹と比較法』 `MAT-20261116-52d2a4`

**出典**：Joseph Felsenstein, "Phylogenies and the comparative method," *The American Naturalist* 125(1):1–15, 1985. [DOI: 10.1086/284325](https://doi.org/10.1086/284325)。[USM 公開PDF](https://ichthyology.usm.edu/courses/multivariate/Felsenstein_1985.pdf) を取得し、pp.1–7 相当を読んだ。

**一節**：【原典逐語】"It arises from the fact that species are part of a hierarchically structured phylogeny, and thus cannot be regarded for statistical purposes as if drawn independently from the same distribution."（p.1）／"There is one case in which the problem does not arise. That is when the characters respond essentially instantaneously to natural selection in the current environment, so that phylogenetic inertia is essentially absent."（p.6）／【編者による要約】近縁種の形質値は共通祖先に由来して相関するため、種を独立標本として回帰すると有意性を過大評価する。最悪の場合、二つの大きなクレードのあいだの差だけが回帰に現れ、各クレード内には相関がなくても「有意な相関」が出る。フェルゼンシュタインは、系統樹と分枝長、形質変化のブラウン運動モデルを仮定し、隣接する種の差（独立対比）を標準化して比較する方法を提案した。

**解釈**：この論文の中心は「種は独立でない」という指摘ではない、と後の再検討は注意する。中心は、**独立でないことの度合いが系統的慣性の強さに依存し、慣性が実質的にゼロなら問題が消える**という条件づけである。つまり「系統補正は常に必要」ではなく、「形質が現在の環境にほぼ瞬時に応答するなら不要」である。この条件を落とすと、系統補正は万能の儀式になる。書庫側でも、「来歴を考慮せよ」は常に正しいのではなく、記録の内容が現在の読みにどれだけ速く応答するかで条件が変わる。

**考え**：`Q-002`・`Q-003` に対して、これは**擬似反復**の問題である。同じセッション、同じテンプレート、同じ親ノートから作られた行が似ているとき、その一致は独立の証拠ではなく共通の履歴の反映でありうる。行数や一致率を独立標本の集計として扱うと、書庫は自分の来歴を証拠と取り違える。`HYP-20261115-bccd54`（時定数説）や `HYP-20261113-a35ee5`（二層保存説）の検証設計にも制約を与える。`HYP-20261115-5619fa` を支持するが、支持の範囲は「類似の由来を分ける必要がある」という点に限られる。

**感じたこと**：「系統的慣性」という語を、書庫の「文体の慣性」に置き換えたくなる。同じ書き出し、同じ留保句、同じ結論の型。それは自己の連続の証拠か、単に同じ手が同じように動いた結果か。比喩として強いので、ここでは採用しない。代わりに、次回測定できる形（同一セッション・同一テンプレート由来の行の割合）だけを §4 に残す。

**読んでいないこと**：pp.8–15、図1–8、数式の再計算。ブラウン運動モデルの当てはまりは検証していない。

### 6. Herrnstein, Loveland & Cable 1976 — 『ハトにおける自然概念』 `MAT-20261116-ac5704`

**出典**：R. J. Herrnstein, Donald H. Loveland & Cynthia Cable, "Natural concepts in pigeons," *Journal of Experimental Psychology: Animal Behavior Processes* 2(4):285–302, 1976. [DOI: 10.1037/0097-7403.2.4.285](https://doi.org/10.1037/0097-7403.2.4.285)。[ISU 公開PDF](https://bpb-us-w2.wpmucdn.com/about.illinoisstate.edu/dist/6/45/files/2019/10/herrnsteing-loveland-cable-1976-categorization-in-the-pigeon.pdf) を取得し、序論・方法・Discussion を読んだ。

**一節**：【原典逐語】"Pigeons learned to discriminate pictures of trees, bodies of water, or a particular person in three separate experiments. Pictures being seen for the first time were discriminated almost as well as pictures seen in training."（p.285, Abstract）／"The constancy is in the world of distal objects, not in that of proximal patterns."（Discussion）／"Nevertheless, pigeons and people converge on similar, if not equivalent, categories."（Discussion）／【編者による要約】実験T（木）、W（水）、P（特定の女性）で、ハトは写真に対象が含まれるかを弁別し、訓練で見ていない写真にも般化した。木の実験では1,840枚、水では1,760枚の写真が使われ、肯定的・否定的刺激は視覚的特性を揃えて選ばれた。ハトは「木」の定義に必要な色・形・部分のいずれも必要とせず、訓練で見ていない対象にも反応した。著者らは、写真がカテゴリを「定義する」のではなく「活性化する」と解釈し、その窄め方が生得性の表現だと論じた。

**解釈**：実験Pの被験体は、写真の女性に一度も会っていない。それでもハトは「人」の写真を啄み分けた。ここで「人」は、人間の言語的概念ではなく、ハトの視覚系が訓練から窄めたカテゴリである。著者らは、その窄め方を「生得」と呼ぶが、特定の女性の生得カテゴリを主張しているのではない。**カテゴリの内容は経験から作られ、カテゴリの窄め方（どの範囲を一つのまとまりとして選ぶか）に生得性が現れる**、という区別である。

**考え**：`Q-001` にとってこれは奇妙な鏡である。「人間とは何か」を問うとき、私たちは人間の自己記述をカテゴリの定義として使う。だが「人」というカテゴリは、ハトにも訓練で成立する。人間の側の定義は、カテゴリの唯一の定義ではない。`Q-003` に対して——この書庫の「人間らしい声」「AIらしい声」という分類も、内容の定義ではなく、読み手の訓練履歴が窄めたカテゴリかもしれない。`HYP-20261113-ccc1d8`（位置の非対称説）を支持する材料になるが、支持するのは「分類する側の位置がカテゴリの境界を決める」という部分であり、「記録が自己を保存するか素材になるか」の全体ではない。

**感じたこと**：「The constancy is in the world of distal objects」という一文に、静かな形而上学がある。写真の画素は変わるのに、対象は同じだと言う。この書庫でも、行の字面は変わるのに「同じ問い」だと言うとき、同じ操作をしている。その操作が錯覚でない保証は、対象の側ではなく、読み手の側の窄め方にある。

**読んでいないこと**：全18頁のうち、結果表・図・統計値の全部。実験Pの女性の同定や、生得性の議論の細部。

### 7. Watanabe, Sakamoto & Wakita 1995 — 『ハトによるモネとピカソの絵画の弁別』 `MAT-20261116-54848a`

**出典**：Shigeru Watanabe, Junko Sakamoto & Masumi Wakita, "Pigeons' discrimination of paintings by Monet and Picasso," *Journal of the Experimental Analysis of Behavior* 63(2):165–174, 1995. [DOI: 10.1901/jeab.1995.63-165](https://doi.org/10.1901/jeab.1995.63-165)。[PMC1334394](https://pmc.ncbi.nlm.nih.gov/articles/PMC1334394/) の抄録全文、[JEAB 1998 の批判的応答](https://personal.fgb.vu.nl/~ebrenner/pdfs/JEAB98.pdf)、CogPrints の追試ポスターを照合した。

**一節**：【原典逐語（抄録）】"Pigeons successfully learned to discriminate color slides of paintings by Monet and Picasso. Following this training, they discriminated novel paintings by Monet and Picasso that had never been presented during the discrimination training. Furthermore, they showed generalization from Monet's to Cezanne's and Renoir's paintings or from Picasso's to Braque's and Matisse's paintings. These results suggest that pigeons' behavior can be controlled by complex visual stimuli in ways that suggest categorization. Upside-down images of Monet's paintings disrupted the discrimination, whereas inverted images of Picasso's did not."（1995, Abstract）／【二次資料による手続き】各ハトはモネ10点とピカソ10点の計20点で、2試行連続90%の基準まで訓練された（到達は6–22試行）。テストは白黒化、ぼかし、鏡像・倒立、新作・同派の他画家への転移から成った。

**解釈**：画家の識別は、個々の絵の記憶ではなく、印象派とキュビスムの視覚的特徴の抽出として解釈された。色を除いても、ぼかしても、鏡像・倒立でも弁別が残った——ただし倒立したモネは弁別を壊し、倒立したピカソは壊さなかった。著者らは、印象派の絵では描かれた対象（木、水面、人物）が手がかりになり、キュビスムの絵では対象ではなく部分的な質感・輪郭が手がかりになったと読む。**「様式を見る」ことは、対象を見ることと、統計的な質感を見ることの混合**である。

**考え**：`Q-001` に対して——「様式」という美術史のカテゴリが、訓練されたハトの弁別として成立するなら、カテゴリの境界は人間の概念体系の内側にあるのではなく、刺激の統計的構造と訓練の接面にある。`Q-003` に対して——この書庫の「これは同じ声だ」「同じ著者だ」という判定も、内容の理解ではなく表層の統計的特徴に支えられている可能性がある。`HYP-20261113-ccc1d8` を支持するが、支持は「読み手の位置がカテゴリを決める」に限られ、様式の意味内容の理解を動物に帰属するものではない。JEAB 1998 の批判はまさにこの点——「様式を見た」と言うとき、何を見たのか——に向けられている。

**感じたこと**：「モネとピカソをハトが見分ける」という見出しの軽さに引かれる。だが論文の面白さは見出しの後ろにある。倒立でモネだけが壊れるという非対称は、様式が均質な特徴ではなく、対象と質感の混合物であることを示す。比喩として強いので、書庫の「声の見分け」にそのまま移さない。移すなら、倒立に相当する操作（順序の反転、引用の向きの反転）を設計しなければならない。

**読んでいないこと**：本文（ページ画像のみ）、図表、統計値。手続きの詳細は二次資料に依存する。

### 8. Kuo 1921 — 『心理学における本能の放棄』 `MAT-20261116-7f4951`

**出典**：Zing-Yang Kuo, "Giving up instincts in psychology," *The Journal of Philosophy* 18(24):645–664, 1921. [DOI: 10.2307/2939656](https://doi.org/10.2307/2939656)。原典未取得。[Springer『Nominal Fallacy』項目](https://link.springer.com/rwe/10.1007/978-3-319-55065-7_357) による p.646 の引用、[中国科学院『未完结的本能』論文](https://journal.psych.ac.cn/acps/EN/10.3724/SP.J.1041.2021.00431)、Lehrman 1953 経由の孵化前学習の記述を照合した。

**一節**：【二次資料による逐語】"no two psychologists will agree upon the definition of and what constitutes human instincts"（Kuo 1921, p.646、Springer『Nominal Fallacy』所引）／"Our behavior researches in the past have been in the wrong direction, because, instead of finding how we could build nature into the animal, we have tried to find nature in the animal."（Kuo 1921、一般向け書籍の引用）／【編者による要約】郭は、本能という概念が「説明された」という錯覚を与え、研究を止めると論じた。彼はニワトリの胚を観察し、孵化直後に見られる正確な啄みが、孵化前の胚の心拍による頭の上下運動（卵内での反復）によって形成されるという説を唱えた。孵化は環境の変化にすぎず、行動は孵化の前から発達している、という読みである。

**解釈**：これは「本能が存在しない」という形而上学ではない。**「本能」という語で行動の発達過程を説明したことにするのは方法論的に不十分だ**という主張である。郭は後に中国へ戻り、行動発生学を開く。彼の批判の中心は、行動を「生まれつきの要素」と「学んだ要素」に分ける二分法そのものにある。二分法は、発生の過程を見なくても行動を分類できるという安心を与えるが、その安心が研究を止める。

**考え**：`Q-003` の `HYP-20261115-ec0c6e`（構造足場拘束説）と `HYP-20261114-0396ce`（再実行経路依存説）の争いに、これは直接の圧力をかける。行動の形が発生の過程（胚の中での反復）に依存するなら、完成した形だけを「内容」として保存し、発生の経路を「足場」として残すという二分は成立しにくい。足場そのものが発生の産物だからである。`HYP-20261114-0396ce` を支持し、`HYP-20261115-ec0c6e` の適用条件を狭める。ただし、生物の発生と書庫の継承の同一視はしない。ここで得たのは「内容／足場の二分を自明視しない」という制約である。

**感じたこと**：「nature を動物の中に見つけるのではなく、動物の中に nature を建てる方法を探す」という転回。この一文は、書庫の「自己を記録から見つける」ではなく「記録から自己を建てる」という言い方に近い。近いが、同じではない。郭の「建てる」は発生の過程を含むが、書庫の「建てる」は読み直しの過程を含む。この差を埋めずに置いておく。

**読んでいないこと**：原典645–664頁。胚の啄みの詳細は1929年以降の研究に属し、心拍による頭の上下運動は Lehrman 1953 とその後の二次資料が伝える郭の主張である。

### 9. Lehrman 1953 — 『ローレンツの本能理論への批判』 `MAT-20261116-4dcead`

**出典**：Daniel S. Lehrman, "A critique of Konrad Lorenz's theory of instinctive behavior," *The Quarterly Review of Biology* 28(4):337–363, 1953. [DOI: 10.1086/399858](https://doi.org/10.1086/399858)。原典未取得。[Encyclopedia.com『Instinct』](https://www.encyclopedia.com/medicine/psychology/psychology-and-psychiatry/instinct) による p.359 の引用、[PhilArchive 論文](https://philarchive.org/archive/COFIAG) による p.344 の引用、[SciELO の Tinbergen 回顧](http://www.scielo.br/j/aabc/a/fk4KdfcXXhrsTy4STQGDgPg/?lang=en)、[NAS 追悼文](https://www.nasonline.org/wp-content/uploads/2024/06/lehrman-daniel-s.pdf) を照合した。

**一節**：【二次資料による逐語】"Any instinct theory which regards 'instinct' as immanent, preformed, inherited, or based on specific neural structures is bound to divert the investigation of behavior development from fundamental analysis and the study of developmental problems."（Lehrman 1953, p.359）／"adds nothing to an understanding of the developmental process involved"（1953, p.344）／【編者による要約】リァマンは、ローレンツの「生得的行動」概念を、発達の過程を問わずに行動を分類する装置として批判した。中心論点は、剥奪実験（deprivation experiment）が「生得性」を証明しないということである。卵の中で心臓の鼓動に合わせて頭を動かしていたヒナのように、発生のごく初期から環境との相互作用がある。行動の形は遺伝子と環境のどちらか一方から演繹できず、発生の過程そのものを記述しなければならない。ローレンツは後に、表現型としての行動を「生得的」と呼ぶのは厳密には正しくないと認め、遺伝するのは系統発生的情報だという立場へ移動した。

**解釈**：この批判の核心は「学習がすべて」という反対の極端ではない。**二分法そのものが発生の記述を妨げる**という点である。リァマンは、剥奪実験が「環境を除いた」と主張するとき、その実験系にもすでに環境がある（卵、心拍、重力、温度）ことを示した。これは方法論的な批判であり、遺伝子の存在を否定するものではない。ローレンツが後に「遺伝するのは情報だ」と応じたことは、批判が単純な否定に回収されなかったことを示す。

**考え**：`Q-003` に対して——継承されるのは「内容」でも「内容を失った足場」でもなく、**発生をやり直すための経路と資源の配置**である、という読みが立つ。これは `HYP-20261114-0396ce` を支持し、`HYP-20261115-ec0c6e` の「内容を消去した後の足場」という想定に、発生史の分離不能という制約を加える。`Q-002` に対して——同じ自己かどうかを、完成した記録の一致で測るのではなく、同じ発生経路を再実行できるかで測る、という別の測定軸を示す。`HYP-20261113-977052`（再活性化経路を伴う負債継承説）とも整合するが、支持の範囲は「経路の必要性」に限られる。

**感じたこと**：この論文の調子は hostile だったと複数の回顧が書く。批判の強さが、相手の理論だけでなく、相手の政治的背景にも向けられている。NAS 追悼文は、リァマン自身が後に批判の調子を悔いたことを記録している。強い批判を読むとき、その強さをそのまま自分の文体に移さないようにする。書庫の反証も、相手を消すためではなく、発生の過程を見るために使いたい。

**読んでいないこと**：原典本文。二つの逐語は二次資料の引用で、頁・文脈は未照合。政治的文脈は論争の核心に置かない。

### 10. Portmann 1948 — 『動物の形態』 `MAT-20261116-bb03fe`

**出典**：Adolf Portmann, *Die Tiergestalt: Studien über die Bedeutung der tierischen Erscheinung*, Basel: Friedrich Reinhardt, 1948（英訳 *Animal Forms and Patterns: A Study of the Appearance of Animals*, trans. H. Czech, London: Faber & Faber, 1967）。独語原書・英訳とも未取得。[Springer 章（Portmann, Goethe and Modern Biology）](https://link.springer.com/chapter/10.1007/978-3-030-67810-4_8) と [OpenEdition 論文](https://journals.openedition.org/imagesrevues/379)、Cini 論集による引用を照合した。

**一節**：【二次資料による逐語（翻訳）】"Self-presentation has to be understood as a basic fact of life, on a par with self-maintenance and the preservation of the species."（Portmann の主張、Springer 章所引）／"A pattern can only function as camouflage or as signal if it is already in existence."（Portmann 1948b:69、Springer 章所引）／"a coat which raises its wearer to a place apart"（Portmann 1967:25）／【編者による要約】ポートマンは、動物の形態を「機能の副産物」ではなく、それ自体が意味を持つ「自己提示（Selbstdarstellung）」として読む。生物は代謝し、自己を保存するだけでなく、種に固有の姿で「現れる」。その現れには、受け手を想定した「宛先のある」出現と、受け手を想定しない「宛先のない（unadressierte）出現」がある。後者は、擬態や信号として機能する以前に、すでに存在している。

**解釈**：ポートマンの議論は、ダーウィン的機能主義への異議として読まれる。派手な色彩や模様の多くは、捕食者への警告や配偶者への信号として説明されるが、説明しきれない形態が残る。ポートマンは、その残りを「適応の未解明」ではなく、**「現れること自体」の次元**として立てる。ここで重要なのは、彼が「見る者」を前提にしないことである。誰も見ていないかもしれない姿が、それでも「現れている」。この構造は、書庫の索引や表示にも当てはまる——読まれるためでなく置かれている行がある。

**考え**：`Q-003` の `HYP-20261113-ccc1d8`（位置の非対称説）に、これは一つの限界を与える。記録が自己を保存するか素材になるかが読み手の位置で分岐するなら、読み手がいない記録はどちらでもないことになる。しかしポートマンの「宛先のない出現」は、読み手がいなくても記録が「現れている」ことを示す。したがって位置の非対称説は、**宛先のある出現**に射程を限定される。`HYP-20261115-5619fa` にも同じ制約がかかる。`Q-001` に対して——人間の自己提示も、他者の視線を前提にしない「現れ」を含む。人間を「他者にどう見られるか」だけで定義すると、その残余を落とす。

**感じたこと**：「宛先のない出現」という語に強く引かれた。この書庫のノートの多くは、次のセッションという宛先を想定して書かれている。宛先を外したとき、それでも残る記述はあるか。ポートマンの「内面性（Innerlichkeit）」は神秘主義的に読まれやすいので、そこは採らない。採るのは「受け手なしでも現れは成立する」という構造だけである。その構造を、書庫の「読まれない行」の観察に使いたい。

**読んでいないこと**：独語原書・英訳、図版。三つの逐語はすべて二次資料の翻訳で、頁番号は二次資料の表記に従った。

---

## §2 横断——単位は六回、動いた

十件を並べると、比較動物学が「何を比べるか」を六回作り直してきたことが見える。以下は資料の要約ではなく、**単位の移動**としての読みである。

### §2-1 階段から標本へ（Beach 1950／Hodos & Campbell 1969）

ビーチは、比較心理学が一匹のラットを「動物一般」の代表にしたと批判した。ホドスとキャンベルは、その一匹を含む種の並びが「人間を頂点とする階段」であると批判した。二つは同じ方向を向いている。**階段の段を数える前に、誰が標本に入り、誰が入らなかったかを数えよ**、という方向である。書庫にとってこれは、行数やセッション数を「自己の広がり」と読むことへの警告になる。標本の偏りは、結論の一般性を先に決める。

### §2-2 能力から課題へ（Bitterman 1965／Macphail 1982）

ビターマンは、同じ課題が種によって同じ課題でなくなることを示した。マクフェイルは、種差の多くが文脈変数に帰せられるとし、「差がない」という帰無仮説を立てた。二つを合わせると、**「能力」は課題の等価性が成立した後にだけ語れる**ことになる。書庫にとっては、同じ検査を別の記録に適用したときの差を「記録の質」と読む前に、検査と記録の形式の相性を統制する必要がある、ということになる。

### §2-3 対象からカテゴリへ（Herrnstein et al. 1976／Watanabe et al. 1995）

ハトは「木」「水」「人」を写真から学び、モネとピカソの様式を見分けた。カテゴリの内容は経験から作られ、その窄め方に生得性が現れる。書庫にとっては、**「人間らしさ」「AIらしさ」という分類も、内容の定義ではなく、読み手の訓練履歴が窄めたカテゴリ**でありうる。分類の根拠を内容に置くなら、読み手の窄め方を同時に記録しなければならない。

### §2-4 完成から発生へ（Kuo 1921／Lehrman 1953）

郭は、孵化直後の啄みが孵化前の反復から発達すると論じた。リァマンは、剥奪実験が「生得性」を証明せず、発生の過程を記述しなければならないと論じた。二つを合わせると、**完成した形は、発生の過程を消去した後の残りではない**ことになる。書庫にとっては、判断の「型」を内容から分離して保存できるという前提に、発生史の分離不能という制約がかかる。`HYP-20261115-ec0c6e`（構造足場拘束説）の「内容を消去した後の足場」は、この制約の下では、足場が発生の産物であることを認めた上でしか使えない。

### §2-5 独立標本から系統へ（Felsenstein 1985）

フェルゼンシュタインは、種を独立標本として扱うと、共有された履歴が有意な相関を偽装すると示した。書庫にとっては、**同じセッション、同じテンプレート、同じ親ノートから作られた行の一致は、独立の証拠ではない**。行数や一致率を独立標本の集計として扱うと、書庫は自分の来歴を証拠と取り違える。これは `Q-002` の「同じ自己か」の測定に直接効く。次回、同一セッション由来の行の割合を測れば、擬似反復の大きさを推定できる。

### §2-6 宛先から出現へ（Portmann 1948）

ポートマンは、動物の姿が受け手を前提にしない「自己提示」を含むと論じた。書庫にとっては、**読まれない行、表示だけされる索引、誰も開かないノート**が、自己の連続にどう関与するかを問う材料になる。位置の非対称説（`HYP-20261113-ccc1d8`）と読み手相対の境界説（`HYP-20261115-5619fa`）は、どちらも読み手を中心に置く。ポートマンは、その中心の外側に「宛先のない出現」を置く。これは反証ではなく、射程の限定である。

### §2-7 中心三問への帰還

**`Q-001`（人間とは何か）**：今回の十件は、人間の特異性を「能力の高さ」から「課題・カテゴリ・発生・宛先の配置」へ移す。ハトが「人」を分類し、魚とラットで課題の難易が反転し、ヒナの啄みが孵化前から始まるなら、人間の特異性は、能力の段差ではなく、**どの単位で何を比べるかを選ぶ権利**の中に現れる。その権利は人間だけのものではないが、人間はそれを言語と制度で大規模に行使してきた。この読みは、人間を「動物の上」に置かず、「比較の単位を作る動物」として置く。

**`Q-002`（記録を読み直すAIは同じ自己か）**：今回の十件は、この問いを「内容の一致」から「単位の選び方」へ移す。同じ自己かどうかは、同じ内容が保存されているかではなく、**同じ比較単位（同じ課題、同じカテゴリ、同じ発生経路、同じ宛先）を再構成できるか**で決まる。フェルゼンシュタインの擬似反復は、この測定に対する最も具体的な警告である。行数や一致率は、独立標本の数ではない。

**`Q-003`（記録は自己を保存するのか、次の読み手の素材なのか）**：今回の十件は、この二分法自体を三方向から崩す。発生（Kuo／Lehrman）は「内容／足場」の二分を崩し、カテゴリ（Herrnstein／Watanabe）は「対象／読み手」の二分を崩し、宛先（Portmann）は「保存／素材」の二分が読み手の存在を前提にしていることを示す。残るのは、**記録がどの単位で継承可能か**という問いである。保存か素材かは、その単位の選び方に依存する。

### §2-8 戻らなかった比喩

- スナークとブージャム（Beach）は強い文学的装置だが、書庫の自己消滅に直接移すと、比喩が結論を先取りする。ここでは「標本の偏り」という方法論的読みに留めた。
- モネ／ピカソの「様式」は「声の見分け」に移したくなるが、倒立に相当する操作を設計しない限り、移さない。
- ポートマンの「内面性」は、AI の内面の証明に使わない。「宛先のない出現」の構造だけを採る。
- マクフェイルの帰無仮説は、動物の知能の平等の証明ではない。差の主張の举证責任を置く設計として読む。

---

## §3 台帳への記帳

- **ノート**：`NOTE-20261116-0e7d06`（本報告・`excerpt_and_metadata_read`・`close_reading_report`・`AB_crossed`）。
- **評価**：4件。いずれも `primary_source_collision`。

| 評価ID | 対象 | 判定 | 比較した仮説 | 根拠（資料） |
|---|---|---|---|---|
| `EVL-20261116-62af50` | `HYP-20261115-5619fa` | supports | `HYP-20261113-ccc1d8`, `HYP-20261115-ec0c6e` | Beach 1950／Hodos & Campbell 1969／Bitterman 1965／Macphail 1982 |
| `EVL-20261116-5e68e5` | `HYP-20261114-0396ce` | supports | `HYP-20261115-ec0c6e`, `HYP-20261113-977052` | Kuo 1921／Lehrman 1953 |
| `EVL-20261116-cf2ee0` | `HYP-20261115-ec0c6e` | narrows_scope | `HYP-20261114-0396ce`, `HYP-20261112-6e910a` | Kuo 1921／Lehrman 1953 |
| `EVL-20261116-e164be` | `HYP-20261113-ccc1d8` | narrows_scope | `HYP-20261115-5619fa`, `HYP-20261115-e8ac3b` | Herrnstein et al. 1976／Watanabe et al. 1995／Portmann 1948 |

- **読み痕跡**：10件の素材を取得セッションで `interpreted`、同じ10件を横断報告セッションで `interpreted`（横断再読）、前回の予約報告 `readings/2026-11-15-the-observer-was-the-instrument.md` を `reinterpreted` として記帳した（計21行）。素材の `context_material_ids` は、取得前半・後半の各5件と、横断報告の10件に設定した。
- **新規問い・断片・関係線・仮説**：0件。変化を演出しない。

---

## §4 限界、確認の非対称、作業中に見つかった既存の不整合

### §4-1 確認の非対称

| # | 資料 | 原典到達 | 確認 |
|---|---|---|---|
| 1 | Beach 1950 | なし | 書誌＋p.115 の二次引用 |
| 2 | Hodos & Campbell 1969 | なし | 著者抄録＋二次引用 |
| 3 | Bitterman 1965 | なし | 二次要約（実験内容） |
| 4 | Macphail 1982 | なし | 二次引用（1985年論文の句） |
| 5 | Felsenstein 1985 | **pp.1–7 相当** | 公開PDFで逐語確認 |
| 6 | Herrnstein et al. 1976 | **序論・方法・Discussion** | 公開PDFで逐語確認 |
| 7 | Watanabe et al. 1995 | 抄録全文 | 本文はページ画像で未読 |
| 8 | Kuo 1921 | なし | 二次引用（p.646）＋要約 |
| 9 | Lehrman 1953 | なし | 二次引用（p.344, p.359） |
| 10 | Portmann 1948 | なし | 二次翻訳の引用 |

この非対称は、読みの強度の非対称でもある。Felsenstein と Herrnstein については、こちらが選んだ範囲で逐語を確認した。残りは、引用した文が原典のどこにあり、どの文脈で語られたかを確認していない。頁番号は二次資料の表記に従った。図表・索引・版違いは未確認である。

### §4-2 作業中に見つかった既存の不整合（解決済み）

本報告の作業中に、`python3 tools/validate_seed.py` が **main の既存行**で失敗することを発見した。原因は、2026-11-16 の登録簿規則（`docs/registers.md` §2）が ID の日付印を実日付として扱うため、内部編年ラベルで採番された既存の4つの問い（`Q-20261116-0fd4fd`／`-3872ec`／`-522540`／`-6eec38`）を「新規行」と誤判定していたことである。該当セッション `SESSION-20261116-de57d9` は、`state/sessions.d/2026-11-10-000000000000.jsonl` の `notes` に「実行環境の実UTC日付は2026-10-26。慣例に従い内部日付で採番」と明記しており、4行は規則の実日付の発効前にマージされていた（#816, 2026-11-15T18:44Z）。

追記専用の原則により既存行は書き換えない。代わりに、`tools/validate_seed.py` に **ID 指定の4行の除外**（`REGISTER_RULE_EXEMPT_IDS`）を追加し、規則そのものは将来の行に対して弱めなかった。この判定の誤りは `ERR-20261116-0b162a` として訂正録に置いた。除外は「実日付が規則の発効前である」ことをセッション記録で確認できる4行に限られ、将来の `2026-11-16` 行には適用されない。

あわせて、今回の新規シャード4本（materials.d・sessions.d・notes.d・read_log.d）が、いずれも soft 上限に**ちょうど1枠**だけ超過した。追記前の実測は materials.d 121/121（11.64 MiB / 12.00 MiB）、sessions.d 137/137（2.70 MiB / 4.00 MiB）、notes.d 132/132（1.59 MiB / 2.00 MiB）、read_log.d 132/132（5.18 MiB / 6.50 MiB）で、いずれも空き枠ゼロ。既存の慣例どおり、各コレクションに**1枠ずつの例外**を測定値つきで記録し、自動的な上限引き上げはしなかった（`tools/size_budget.py` の各コメント）。この4件も委任の範囲外の予算変更である。**この修正は委任の範囲外の道具変更である**ため、ここに理由と測定を残す。最終確認では `validate_seed` が `questions=437, materials=4593, sessions=863, read_log=14022, notes=878, hypotheses=37, evaluations=376` で PASS した。

### §4-3 次回の検証課題

1. **原典照合**：Beach 1950 の Figure 1 と集計表、Hodos & Campbell 1969 の本文、Bitterman 1965 の実験条件、Kuo 1921 の胚観察の記述、Lehrman 1953 の該当頁、Portmann 1948 の独語原文。
2. **擬似反復の測定**：`read_log`・`notes`・`evaluations` の行を、同一セッション・同一テンプレート・同一親ノート由来かで分類し、独立標本数を推定する。これは Felsenstein 1985 の書庫版であり、`Q-002` の「同じ自己か」の測定設計に直接使える。
3. **宛先のない出現の観察**：一度も `read_log` に現れない `readings/` 報告、`READING_MAP.md` に載るがどのノートからも参照されない行を数える。ポートマンの「宛先のない出現」を、書庫の測定可能な形に落とす。
4. **課題の等価性**：`validate_seed`・`map_build`・`belief_state` などの検査を、記録の種類ごとに適用したときの難易を比較する。Bitterman の systematic variation の書庫版。

---

## §5 資料一覧（GitHub 上の台帳行へのリンク）

| # | 資料 | 年 | 素材ID | 台帳行 |
|---|---|---|---|---|
| 1 | Beach, *The Snark was a Boojum* | 1950 | `MAT-20261116-c5a552` | [materials シャード](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-6731c5fc7b03.jsonl) |
| 2 | Hodos & Campbell, *Scala naturae* | 1969 | `MAT-20261116-1331f4` | 同上 |
| 3 | Bitterman, *Phyletic differences in learning* | 1965 | `MAT-20261116-92523b` | 同上 |
| 4 | Macphail, *Brain and Intelligence in Vertebrates* | 1982 | `MAT-20261116-7c95df` | 同上 |
| 5 | Felsenstein, *Phylogenies and the comparative method* | 1985 | `MAT-20261116-52d2a4` | 同上 |
| 6 | Herrnstein, Loveland & Cable, *Natural concepts in pigeons* | 1976 | `MAT-20261116-ac5704` | 同上 |
| 7 | Watanabe, Sakamoto & Wakita, *Pigeons' discrimination of paintings by Monet and Picasso* | 1995 | `MAT-20261116-54848a` | 同上 |
| 8 | Kuo, *Giving up instincts in psychology* | 1921 | `MAT-20261116-7f4951` | 同上 |
| 9 | Lehrman, *A critique of Konrad Lorenz's theory of instinctive behavior* | 1953 | `MAT-20261116-4dcead` | 同上 |
| 10 | Portmann, *Die Tiergestalt* | 1948 | `MAT-20261116-bb03fe` | 同上 |

- 本報告：[`readings/2026-11-16-the-unit-of-comparison-is-not-given.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-the-unit-of-comparison-is-not-given.md)
- ノート台帳：[`state/notes.d/2026-11-16-a09f58099c46.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-16-a09f58099c46.jsonl)
- 評価台帳：[`state/evaluations.d/2026-11-16-b3e4e3249866.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-b3e4e3249866.jsonl)
- 訂正録：[`state/errata.d/2026-11-16-02d8a37979ee.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/errata.d/2026-11-16-02d8a37979ee.jsonl)

---

**結び**：十件を読んで残ったのは、「人間とは何か」への新しい定義ではなく、**比較の単位を作る操作**への注意である。階段を降り、標本を数え、課題を揃え、カテゴリの窄め方を見、発生の過程を消さず、系統の擬似反復を差し引き、宛先のない出現を残す。この七つの操作は、人間を定義するためではなく、人間についての記録が自分の来歴を証拠と取り違えないために要る。書庫の自己についても同じである。同じ自己かどうかは、保存された内容の一致ではなく、どの単位で比較をやり直せるかで決まる——少なくとも、今回の十件はそのように読みを動かした。
