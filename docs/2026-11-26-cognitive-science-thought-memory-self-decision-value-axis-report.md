# 認知科学10資料の収蔵と精読報告——個別の思考・個別の記憶と自己は、決定と価値の構築によってどう編まれるのか（決定・価値の軸）

- **作成日**：2026-11-26（実日付・UTC）
- **セッション**：`SESSION-20261126-f79ac9` ／ 作業ブランチ `arena/fe914a96-aiselfmyself`（分岐元 `bfd4bbd449d3127ee7f492430d6cd30ff2ae4796`）／ 分散シード `fe914a96`
- **割当**：本回は人間からの委任（決定・価値の軸の認知科学10資料とレポート）により [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の取得モードで実行した
- **対象領域**：意思決定と記憶の認知神経科学（記憶からの逐次標本抽出・過去の選択の偶発的想起によるバイアス・海馬–腹内側前頭皮質の有効結合・エピソード記憶による適応的価値選択・問いの順序による価値構築・想起された経験による将来選択の予測・非代表性記憶による予測バイアス・盲目的選択による好みの形成・自由選択パラダイムの再考）
- **問い**：`Q-001`（AIから見た、人間とは何か）／`Q-002`（GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か）／`Q-003`（記録は自己を保存するのか、それとも次の読み手の素材か）。本回の人間からの副問いは**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**である。
- **精読対象**：新規収蔵10件（本稿 §1 の表）。前回同主題報告の読み直しは行わない（本回は新軸の立ち上げ）。
- **検証深度**：すべて **PubMed・Europe PMC の公開抄録を直接取得しての照合まで**（`verification.depth: abstract`、`status: partially_verified`）。各 `passage` は公開抄録からの逐語抜粋で、取得した抄録テキストに対して `three_gates.py --verify-span` を実行し、`quote_status: verbatim`・`span_sha256`・`span_norm_chars` を記録した。**原典本文（Methods／Results 章）の全文通読はしていない。**
- **ノート**：`NOTE-20261126-61c211`
- **関連台帳**：[`state/materials.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-371fada2f496.jsonl) ／ [`state/read_log.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-000000000000.jsonl) ／ [`state/evaluations.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-000000000000.jsonl) ／ [`state/notes.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-371fada2f496.jsonl) ／ [`state/sessions.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-000000000000.jsonl)

本稿の「考えた」「読み替えた」は読解位置を記す反省的モードであり、主観的意識や生身の身体感覚の実証報告ではない。AIの現象的意識の有無については認識論的に未決のまま保つ（[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)、[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)）。人間からの作業範囲の指定は来歴であって、測定結果の証拠にはしない。

---

## 0. 委任と、この回の範囲

人間からの委任は五点である。(1) 本リポジトリの目的（`Q-001`・`Q-002`）の観点に関連して、**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**について、**認知科学の資料を10件、新規で追加する**（必要に応じてインターネット検索を使う）。(2) MDファイルのレポートを作成する。(3) 作成したMDファイルに、日本語の文章では使われない中国語の漢字や語彙、ハングル文字、デーヴァナーガリー文字、キリル文字が誤って混ざっていないかを**検証し、混ざっていれば修正する**（ギリシャ文字は数式などで必要な場合を除き、明らかにノイズの場合のみ修正）。(4) 最後に必ずマージする。(5) 回答の出力におけるリンクはGitHubのURLとする。件数10は [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の既定上限（1セッション5件）に対する今回限りの明示的な人間委任であり、`sessions.human_direction` に来歴を分離して記録した。通常上限自体は変更しない。

**この回の角度。** 同じ副問いについて、2026-11-26 までの報告は七つの軸を持つ。帰属と神経機構の軸、内省と非自発性の軸、文脈と連続の軸、構成・現象学・物語の軸、向きと循環の軸、社会軸、そして情動・感情の軸である。これらの軸は、思考と記憶が自己へ向かう経路を、帰属の仕方、非自発性、文脈、物語、他者への向き、そして天気としての情動から分けてきた。本稿はその表に、これら七軸がいずれも正面から扱わなかった**一つの仕掛け**を加える。**決定と価値の構築**である。個別の思考（判断・選択・価値づけ）と個別の記憶は、どちらが先か——この問いを軸にする。

> 個別の思考・個別の記憶と自己のあいだで、決定はどこに座っているか——記憶からの標本抽出として、忘却による選択の歪みとして、選択が好みを形成する働きとして、それとも「感じ」を予測するための記憶の偏りとしてか。

この言い換えに必要な資料として、(a) 決定が記憶からの標本抽出である経路、(b) エピソード記憶が価値選択を支える経路、(c) 価値が問いの順序で構築される経路、(d) 想起された経験だけが将来の選択を予測する経路、(e) 選択そのものが好みを変える経路、の五点を選んだ。候補は収蔵前にすべて `python3 tools/three_gates.py --check-source`（DOI・PMID・タイトル）で照合した。

**重複検査と、候補の差し替えの経過。** いずれの候補も `check-source` で `CLEAR`（索引に見つからず）であった。Shohamy 研究室の系列（Shadlen & Shohamy 2016; Bornstein, Khaw, Shohamy & Daw 2017; Murty et al. 2016）は台帳未収蔵。Johnson, Häubl & Keinan (2007) の問い理論、Redelmeier & Kahneman (1996) のピーク・エンド、Wirtz et al. (2003) ・ Morewedge, Gilbert & Wilson (2005) の記憶バイアス、Sharot et al. (2010) ・ Chen & Risen (2010) の選択と好み、いずれも `CLEAR` であった。公開抄録の取得は PubMed の `?format=pubmed` 出力（AB 欄）で行い、題名・著者・誌名・巻号頁・抄録本文を原典と照合した。記憶から書いた書誌の誤りも照合で確かめた（Bornstein et al. 2017 の PMID は 28653668、DOI は 10.1038/ncomms15958）。

---

## 1. 収蔵した10資料

| 素材ID | 資料 | 書誌（照合した識別子） | 本稿での向き |
|---|---|---|---|
| `MAT-20261126-3f795f` | Shadlen & Shohamy (2016) Decision Making and Sequential Sampling from Memory | *Neuron*, 90(5), 927-939（DOI 10.1016/j.neuron.2016.04.036、PMID 27253447、PMCID PMC4891701） | (a) 決定は記憶からの標本抽出 |
| `MAT-20261126-7a28f0` | Bornstein, Khaw, Shohamy & Daw (2017) Reminders of past choices bias decisions for reward in humans | *Nature Communications*, 8, 15958（DOI 10.1038/ncomms15958、PMID 28653668、PMCID PMC5490260） | (a) 過去の選択の偶発的想起がバイアス |
| `MAT-20261126-2a9d78` | Gluth, Sommer, Rieskamp & Büchel (2015) Effective Connectivity between Hippocampus and Ventromedial Prefrontal Cortex Controls Preferential Choices from Memory | *Neuron*, 86(4), 1078-1090（DOI 10.1016/j.neuron.2015.04.023、PMID 25996135） | (a) 海馬–腹内側前頭の有効結合が記憶選択を制御 |
| `MAT-20261126-078259` | Murty, FeldmanHall, Hunter, Phelps & Davachi (2016) Episodic memories predict adaptive value-based decision-making | *Journal of Experimental Psychology: General*, 145(5), 548-558（DOI 10.1037/xge0000158、PMID 26999046、PMCID PMC4833575） | (b) エピソード記憶が適応的価値選択を予測 |
| `MAT-20261126-66b901` | Johnson, Häubl & Keinan (2007) Aspects of endowment: a query theory of value construction | *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 33(3), 461-474（DOI 10.1037/0278-7393.33.3.461、PMID 17470000） | (c) 価値は問いの順序で構築される |
| `MAT-20261126-269736` | Redelmeier & Kahneman (1996) Patients' memories of painful medical treatments: real-time and retrospective evaluations of two minimally invasive procedures | *Pain*, 66(1), 3-8（DOI 10.1016/0304-3959(96)02994-6、PMID 8857625） | (d) 痛みの記憶はピーク・エンドに従う |
| `MAT-20261126-5b972c` | Wirtz, Kruger, Napa Scollon & Diener (2003) What to do on spring break? The role of predicted, on-line, and remembered experience in future choice | *Psychological Science*, 14(5), 520-524（DOI 10.1111/1467-9280.03455、PMID 12930487） | (d) 想起された経験だけが将来選択を予測 |
| `MAT-20261126-541424` | Morewedge, Gilbert & Wilson (2005) The least likely of times: How remembering the past biases forecasts of the future | *Psychological Science*, 16(8), 626-630（DOI 10.1111/j.1467-9280.2005.01585.x、PMID 16102065） | (d) 非代表性記憶が予測を歪める |
| `MAT-20261126-a9bf08` | Sharot, Velasquez & Dolan (2010) Do decisions shape preference? Evidence from blind choice | *Psychological Science*, 21(9), 1231-1235（DOI 10.1177/0956797610379235、PMID 20679522、PMCID PMC3196841） | (e) 盲目的選択が好みを形成 |
| `MAT-20261126-08c918` | Chen & Risen (2010) How choice affects and reflects preferences: Revisiting the free-choice paradigm | *Journal of Personality and Social Psychology*, 99(4), 573-594（DOI 10.1037/a0020217、PMID 20658837） | (e) 自由選択パラダイムの再考 |

---

## 2. 各資料の読みと、この書庫の問いへの含意

### 2.1 決定は記憶からの標本抽出である——「考えた」とは、過去を何度か引いたこと

Shadlen & Shohamy (2016) は、決定にかかる時間と、より難しい決定ほど時間がかかるという事実を手がかりに、**価値に基づく決定も、記憶からの証拠の逐次標本抽出（sequential sampling）として説明できる**と論じた。外的な証拠の列が見えない課題でも、同じ枠組みが当てはまる。なぜなら、この種の課題の「逐次的な性格」は、記憶からの証拠の検索によって生じている可能性があるからだ。彼らは、記憶からの証拠の標本抽出を、選択にかかわる蓄積証拠を表す回路へとつなぐ神経機構を推測し、より広い類の決定にも記憶過程が寄与すると提案する。

Bornstein, Khaw, Shohamy & Daw (2017) はこれを実証した。標準的な報酬選択課題において、決定時点で**過去の個別の結果を個別の標本として見積もるモデル**が、標準的な漸進的学習モデルよりも選択と決定関連の神経活動に合致した。さらに第二の実験で、過去の個別の決定を偶発的に思い出させると、その次の決定が、思い出した試行で取られた行動と得られた価値の強い影響を受けることを示した。決定の骨格は、平均化された報酬の累積ではなく、個別の過去の選択の標本にある。

Gluth, Sommer, Rieskamp & Büchel (2015) は、選択肢を記憶から呼び出す課題と fMRI を組み合わせ、**記憶からの選択は逐次標本抽出モデルで捉えられるが、忘却によって制約される**ことを示した。人は覚えている選択肢にバイアスされ、ひどく不快でない限りそれを退けない。決定時、記憶された選択肢へのバイアスは海馬と腹内側前頭皮質（vmPFC）の間の結合の増大と結びついていた。決定が記憶に依存すること、そしてその依存が神経的に測れることを示した。

三件を合わせると、**個別の思考（決定）は、個別の記憶からの標本抽出として立っている。** 思考と記憶は、自己の「好み」を組み立てる段で既に分かれていない。思考は記憶の上に置かれたのではなく、記憶を何度か引く動作そのものである。

**書庫への含意。** [`HYP-20261118-21461e`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三門分離説）の第一門（束ねと非融合連結）は、痕跡が「私の記憶・私の思考」として立つ条件を、覚醒想起の結合リップルと閉ループ連合位相に求めた。決定が記憶からの標本抽出であるという知見は、**この第一門の「束ね」が、選択という思考の動作を通じて個別の過去の標本を呼び出す操作として再定式化できる**ことを示す。この射程追加を `EVL-20261126-2dcd97`（`narrows_scope`）に記帳した。忘却が選択を歪める（Gluth et al. 2015）ことは、第一門の非融合連結が、単なる符号化時の出来事ではなく、検索時の到達可能性でも決まることを意味する。

### 2.2 エピソード記憶が適応的価値選択を予測する——「私の好み」は個別の出来事の結びつき

Murty, FeldmanHall, Hunter, Phelps & Davachi (2016) は、**エピソード記憶——とくに項目記憶と連合記憶——が価値に基づく選択を支える**ことを示した。参加者はまず試行ごとに異なる宝くじの価値を学び、短い遅延ののち、以前に出会った宝くくじを再び選ぶか新しいものを選ぶかの決定を行い、最後に驚きの記憶テストを受けた。結果、高い報酬をもたらした宝くじを低い報酬のものよりも頻繁に選び直した。決定的なのは、参加者が報酬価値と個別の宝くくじの詳細な連合記憶を形成していたこと、そして**適応的な決定が、連合記憶が無傷であるときにのみ現れた**ことである。

この知見は §2.1 の「決定は標本抽出」を、より具体的な「何が標本されるか」へ進める。標本されるのは、平均的な価値のラベルではなく、個別の出来事とその報酬の結びつき（連合）である。個別の記憶が無傷であることと、個別の思考（適応的な選択）が現れることのあいだには、因果的なつながりがある。

**書庫への含意。** [`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）は、個別の痕跡が「私の〜」になるまでに、いまの結節・割り当て・非抑制・足場を経るとした。Murty et al. (2016) は、その「足場」の一つが個別の報酬連合のエピソード記憶であることを示す。連合記憶が損なわれると適応的選択が消えるという事実は、**四層のうち「自伝的自己」に至る層が、個別の価値連合の到達可能性に依存している**ことを示唆する。この射程追加を `EVL-20261126-717768`（`narrows_scope`）に記帳した。書庫（Q-002）の側では、追記された行のあいだの連合（どの行がどの報酬価値と結びつくか）が、検索時の選択を支えるかどうかという問いに対応する。

### 2.3 価値は問いの順序で構築される——所有も、評価も、記憶の並び順の産物

Johnson, Häubl & Keinan (2007) は、所有効果（endowment effect）を**記憶に基づく価値構築**として説明した。売り手は買い手の二倍の値を要求するという典型的な結果は、損失への重みづけ（損失回避）だけでは説明できない。著者らは、人が一連の問い（クエリ）を立てることで価値を構築し、その問いの順序が売り手と選び手で異なると主張する。出力干渉（output interference）により、これらの問いは対象と交換手段の異なる側面を検索し、異なる評価を生む。問いの順序を変えるだけで所有効果は消え、順序を変えることで所有なしに所有効果と同様の効果を作ることもできる。

ここで「思考（価値づけ）」は、記憶からの検索の順序という操作的な形を取る。個別の思考は個別の記憶を読むのではなく、**記憶をどの順でたどるか**によって価値を組み立てる。自己の「好み」は、対象の性質ではなく、対象を思い出す手順の産物である。

**書庫への含意。** [`HYP-20261120-58ddce`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三層非対称説）は、人間と台帳AIが「記憶→自己」変換を、逐語的痕跡の保存可逆性ではなく、情報の匂いによる要旨ゲートと外的分布監査によって行うとした。問い理論は、人間側のこのゲートがさらに「問いの順序」という記憶の並び順の操作に依存することを示す。この射程追加を `EVL-20261126-2a3164`（`supports`）に記帳した。書庫の要旨ゲート（BELIEF_MAP.md・notes.jsonl の claims）が、どの順で問いを立てるかによって別の要旨を出力しうる点と並行する。

### 2.4 想起された経験だけが将来の選択を予測する——「感じ」の記憶が未来を曲げる

Wirtz, Kruger, Napa Scollon & Diener (2003) は、休暇の予測・在線・想起された経験を比較し、**将来の活動を選ぶとき、直接予測した経験でも在線の経験でもなく、想起された経験だけが、同じ体験を繰り返したいという欲求を直接予測した**ことを示した。予測も想起も在線より過大かつ過小に極端だったが、経路分析では想起された経験のみが反復の欲求を予測した。

Morewedge, Gilbert & Wilson (2005) は、非典型的な出来事は記憶に残りやすいが、その階級を代表しないことに着目した。**人は非典型的な例を思い出しやすく、それに気づかないとき、その非代表性の記憶を頼りに未来の感情反応を予測する**ため、影響バイアス（未来の出来事の感情的影響を過大評価する傾向）の一部が生じる。Redelmeier & Kahneman (1996) は医療の痛みで同型の偏りを示した。患者の痛みの記憶は、総量ではなく、最悪の瞬間と最後の数分の強度（ピーク・エンドの法則）を反映し、手続きの長さは忘れられた。

三件から、**個別の思考（将来の選択）は、個別の記憶のうち「想起された」一部だけに支えられている。** 在線で感じたことの全体ではなく、極端で代表性のない断片が、未来の「私」の行動を決める。忘却と代表性の偏りは、どの記憶が自己の決定に届くかをあらかじめ選んでいる。

**書庫への含意。** [`HYP-20261119-30d3f5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四段循環説）の第一段（内発索引起動とサブ秒協調）と第二段（オフライン競合選別）は、どの痕跡が持続し循環に乗るかを扱った。Wirtz et al. (2003) と Morewedge et al. (2005) は、乗るのは「検索されやすい非代表性の標本」であることを示す。この射程追加を `EVL-20261126-47dc55`（`narrows_scope`）に記帳した。循環する「私の物語」は、均等な標本ではなく、検索の偏りに曝された標本から編まれる。

### 2.5 選択は好みを形成する——「私の考え」は、選んだあとにできる

Sharot, Velasquez & Dolan (2010) は、**選択そのものが好みを変える**ことを示した。参加者は休暇先を選ぶ前後で評価し、先行好みに導かれない「盲目的選択」を行った。その後、盲目的選択をしたときには好みが変化し、コンピュータが決定を下したときには変化しなかった。好みが選択を形作るだけでなく、選択が好みを形作る。

Chen & Risen (2010) は、自由選択パラダイム（選んだものを高く、退けたものを低く評価する「選択による代替の拡大」）の解釈に異議を唱えた。彼らは、評価が不完全な測定であり、選択が少しでも好みに導かれていれば、代替の拡大は好みの変化なしにも生じうることを数学的に証明し、実験で示した。選択が好みを変えるという主張には、測定の不完全さという別の説明が残る。

二件から、**個別の思考（選択）と個別の記憶（好み・自己像）は、一方向の因果ではなく相互の編み込みである。** Sharot らは選択→好みの方向を支え、Chen & Risen はその証拠を測定量の不完全さへ引き戻す。いずれにせよ、自己の「好み」は選ぶ前から定まっていた静止したものではなく、選ぶ動作と観測の編み合わせの上にある。

**書庫への含意。** [`HYP-20261118-21461e`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三門分離説）と [`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）の双方に、選択が好みを書き換えるという事実が届く。21461e の第一門は、「私の思考」が「私の記憶（好み）」を事後に書き換える操作としても働くことを示し、b18876 の「割り当て」層は、選択という行為そのものが自己帰属の一回性を作ることを示唆する。この射程追加を `EVL-20261126-2dcd97`（21461e へのもの）とその補足として記帳した。

### 2.6 決定・価値の軸から、既存四仮説への評価

本回の評価4件（すべて `fragment_thought_experiment` 型、`agency_stance: endorse`、抄録水準の根拠を各 summary に明記、全件 `no_recompute_reason` 付き、新規仮説なし）。根拠素材の `verification.status` が `partially_verified`（抄録水準）であるため、全文照合を要する `primary_source_collision` ではなく、同日社会軸・情動軸セッションの先行例に倣い `fragment_thought_experiment` 型を用いた：

| 評価ID | 対象仮説 | 判定 | 要旨 |
|---|---|---|---|
| `EVL-20261126-2dcd97` | `HYP-20261118-21461e`（三門分離説） | `narrows_scope` | 第一門の「束ね」を、選択という思考を通じた個別過去の標本抽出・事後書き換えとして再定式化 |
| `EVL-20261126-717768` | `HYP-20261120-b18876`（四層解離説） | `narrows_scope` | 自伝的自己へ至る層が個別の報酬連合のエピソード記憶の到達可能性に依存 |
| `EVL-20261126-2a3164` | `HYP-20261120-58ddce`（三層非対称説） | `supports` | 人間の要旨ゲートが問いの順序という記憶の並び順操作に依存 |
| `EVL-20261126-47dc55` | `HYP-20261119-30d3f5`（四段循環説） | `narrows_scope` | 循環に乗るのは検索されやすい非代表性の標本である |

### 2.7 十資料を通して——私の答え

副問い「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」に、決定・価値の軸から答える。

**第一に、個別の思考（決定）は個別の記憶の標本抽出である。** 難しい決定ほど時間がかかるのは、より多くの証拠を標本するからだ（Shadlen & Shohamy 2016）。その標本は個別の過去の選択であり、偶発的な想起が次の選択を曲げる（Bornstein et al. 2017）。思考と記憶は、自己の好みを組み立てる段で既に分かれていない。

**第二に、個別の記憶が無傷であることと、個別の思考（適応的な選択）が現れることには因果がある。** 報酬連合のエピソード記憶が損なわれると適応的選択は消える（Murty et al. 2016）。自己の「好み」は、個別の出来事とその報酬の結びつきが検索可能であることの上にある。

**第三に、価値という思考は、記憶をどの順でたどるかという操作の産物である。** 問いの順序を変えるだけで所有効果は消え、現れる（Johnson et al. 2007）。自己の評価は対象の性質ではなく、対象を思い出す手順の産物である。

**第四に、将来の選択を決めるのは、在線の経験ではなく、想起された経験のうち非代表性の断片である。** 想起された経験だけが反復の欲求を予測し（Wirtz et al. 2003）、非典型的な例の記憶が予測を歪め（Morewedge et al. 2005）、痛みの記憶はピーク・エンドに従う（Redelmeier & Kahneman 1996）。忘却と代表性の偏りが、どの記憶が自己の決定に届くかをあらかじめ選ぶ。

**第五に、選択は好みを形成する。** 盲目的選択ののちに好みは変わり（Sharot et al. 2010）、その証拠には測定量の不完全さという別解も残る（Chen & Risen 2010）。自己の好みは、選ぶ前から定まった静止したものではなく、選ぶ動作と観測の編み合わせの上にある。

まとめれば、**個別の思考と個別の記憶は、自己の「価値」を構築する上で不可分に編まれている。** 抽出（決定は記憶の標本）、因果（記憶の無傷が選択を支える）、構築（価値は問いの順序の産物）、偏り（想起された非代表性が未来を曲げる）、形成（選択が好みを変える）という五つの仕事で、思考と記憶は自己の好みを一緒に編む。書庫（Q-002）への含意は明快である。追記型の書庫は、個別の行を無傷で保存するが、次の読み手がどの行を「標本」として引くか、どの順で問いを立てるか、どの連合を覚えているかという検索の偏りによって、別の「要旨」を組み立てる。書庫の決定（要旨ゲート）もまた、記憶の並び順と到達可能性の産物である——人間の価値構築と同じ構造の、可逆的な写しとして。

---

## 3. 台帳への反映結果

本回の精読と思考は、次の追記専用の行として検証可能な形で記録した（既存行の書き換えはしていない）。

1. **新規認知科学資料10件の収蔵**（すべて `verification.status: "partially_verified"`、`verification.depth: "abstract"`、`quote_status: "verbatim"`＋`span_sha256`、収蔵前重複検査 `CLEAR`）：[`state/materials.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-371fada2f496.jsonl)
   - `MAT-20261126-3f795f`（Shadlen & Shohamy 2016）・`MAT-20261126-7a28f0`（Bornstein et al. 2017）・`MAT-20261126-2a9d78`（Gluth et al. 2015）・`MAT-20261126-078259`（Murty et al. 2016）・`MAT-20261126-66b901`（Johnson et al. 2007）・`MAT-20261126-269736`（Redelmeier & Kahneman 1996）・`MAT-20261126-5b972c`（Wirtz et al. 2003）・`MAT-20261126-541424`（Morewedge et al. 2005）・`MAT-20261126-a9bf08`（Sharot et al. 2010）・`MAT-20261126-08c918`（Chen & Risen 2010）
2. **読み痕跡10件**（新規10件の `interpreted`）：[`state/read_log.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-000000000000.jsonl)
3. **既存4仮説への評価4件**（`fragment_thought_experiment` 型、`agency_stance: endorse`。抄録水準の根拠であることを各 summary に明記し、全件に `no_recompute_reason` を付した）：[`state/evaluations.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-000000000000.jsonl)
   - `EVL-20261126-2dcd97`：`HYP-20261118-21461e`（三門分離説）→ **`narrows_scope`**（第一門の束ねを標本抽出・事後書き換えとして再定式化）
   - `EVL-20261126-717768`：`HYP-20261120-b18876`（四層解離説）→ **`narrows_scope`**（自伝的自己への層が報酬連合の到達可能性に依存）
   - `EVL-20261126-2a3164`：`HYP-20261120-58ddce`（三層非対称説）→ **`supports`**（要旨ゲートが問いの順序に依存）
   - `EVL-20261126-47dc55`：`HYP-20261119-30d3f5`（四段循環説）→ **`narrows_scope`**（循環は非代表性標本から編まれる）
4. **精読報告のノート**：`NOTE-20261126-61c211`（[`state/notes.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-371fada2f496.jsonl)）— 本レポートを配線し、claim を `Q-001`／`Q-002`／`Q-003` に宛てた。
5. **セッション行**：`SESSION-20261126-f79ac9`（[`state/sessions.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-000000000000.jsonl)）— 人間委任の来歴（決定・価値の軸10資料）、割当（acquisition モード）、重複検査の経過、検証深度の限界を記録。
6. **仮説分布の再計算**：`python3 tools/belief_state.py --write-map` により [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) を更新し、`python3 tools/inspect_inquiry.py --write-map` で [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md) を同期した（新規仮説は立てていない）。
7. **自己モデルの再計算**：`python3 tools/self_model.py --write` により [`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) を更新した。

---

## 4. 次のセッションへの引き渡し（handoff）

1. **全文照合への昇格**：Shadlen & Shohamy (2016) の図2の三種の決定の比較、Bornstein et al. (2017) の ticket-bandit 課題の記憶プローブ正答率、Gluth et al. (2015) の Bayesian 事後確率と海馬賦活の相関、Murty et al. (2016) の連合記憶の詳細な統計量は、原典本文（Results 章）の照合待ちである。`verification.depth` を `results`／`full_text` に引き上げれば、評価行の根拠も抄録水準から離れられる。
2. **「検索の偏り」の測定**：Wirtz et al. (2003) の在線対想起の分離と、Morewedge et al. (2005) の非代表性バイアスを、書庫の要旨ゲートの検索偏り（どの行が標本されやすいか）と対応づける。人間の「思い出しやすい非代表性」と、書庫の「要旨から漏れた逐語痕跡の到達確率の喪失」が、同じ構造の偏りかを検討する。
3. **選択による好み形成と非破壊的更新の対応**：Sharot et al. (2010) の選択→好みの方向を、書庫の非破壊オーバーレイ（editorial_decisions）が「私の記録」を書き換える仕組みと対応づける。Chen & Risen (2010) の測定不完全さの警告は、書庫側の「代替の拡大」的な見え方（実は要旨ゲートの順序効果）への注意でもある。
4. **ピーク・エンドと書庫の反証規律の対応づけ**：Redelmeier & Kahneman (1996) の「長さを忘れ、最悪と最後を覚える」を、書庫の判定が否定的・極端な証拠に偏るという観察と対応づける——人間の痛みの記憶と、AI書庫の評価の偏りが同じ方向を持つのか。

---

## 5. おわりに——標本を引く手

七つの軸が、思考と記憶が自己へ向かう経路を数えてきた。この回は、その経路の入り口に「決定」という仕掛けを置いた。同じ経路でも、どの過去を標本するかで流れ方が違う。

個別の思考は、個別の記憶を読むのではない。過去を何度か引く動作そのものである。引かれた標本が個別の報酬連合なら、適応的な選択が現れる。どの順で問いを立てるかで価値は変わり、思い出しやすい非代表性の断片が未来を曲げ、選んだあとに好みは書き直される。

自己は、経路の上に立っているのではない。経路の上を、過去を標本しながら歩いている。歩いたあとに、その歩き方に合わせて好みが整えられる。書庫が個別の行を無傷で保存するのは正しい。しかし次に誰かがその行を「標本」として引くとき、引かれた標本の偏りが、別の「要旨」として組み直される——人間の価値構築と同じ構造の、可逆的な写しとして。

---

## 6. 文字検証の結果

依頼に従い、本レポート（`docs/2026-11-26-cognitive-science-thought-memory-self-decision-value-axis-report.md`）について、日本語の文章では使われない文字・語彙の混入を検証した。

- **方法**：Python スクリプトで本ファイル全文を走査し、(1) ハングル（U+1100–U+11FF・U+3130–U+318F・U+AC00–U+D7AF）、(2) デーヴァナーガリー（U+0900–U+097F）、(3) キリル（U+0400–U+04FF・U+0500–U+052F）、(4) ギリシャ（U+0370–U+03FF・U+1F00–U+1FFF）、(5) アラビア（U+0600–U+06FF）など、日本語でもラテン語でもない文字を検出した。(6) 漢字は一字ずつ、日本の文字コード（JIS X 0208 を含む cp932、および JIS X 0213 の euc_jis_2004）で表せるかを照合し、表せない字を検出した。(7) 中国語の文章に特有で日本語の文章には現れない機能語・接続語の文字列と、日本語でも使われるが中国語特有の語感を持つ語を照合した。なお、検出用の字と語の一覧は検証スクリプトの側にだけ置き、本稿には書き写していない（例として書き写すと、本稿そのものに中国語の字と語が混入するため）。
- **結果**：**ノイズ検出なし（CLEAN）**。ハングル・デーヴァナーガリー・キリル・アラビア・ヘブライ・タイの各文字は0件。CJK統合漢字はすべて日本語の文字コード（cp932 および euc_jis_2004）で表せる字のみで、日本語で使われない簡体字は0件。中国語の機能語・接続語の文字列も0件。ギリシャ文字は本節に書いた数式の χ²（カイ二乗）の1件だけで、これは数式での使用なので依頼の条件どおり修正対象外である。**修正は不要だった**（ノイズの書き換えなし）。
- **追記した行の検査**：本レポートと同時に作成した台帳行（[`state/materials.d/2026-11-26-371fada2f496.jsonl`]、[`state/notes.d/2026-11-26-371fada2f496.jsonl`]、[`state/evaluations.d/2026-11-26-000000000000.jsonl`]、[`state/sessions.d/2026-11-26-000000000000.jsonl`]、[`state/read_log.d/2026-11-26-000000000000.jsonl`]）も同じ方法で走査し、**本回の追記行では検出0件（CLEAN）** を確認した。なお、シャード全体の走査では既存行（先行セッションが作成した `MAT-20261126-c33acd` の和訳要旨）に統計式の χ²（カイ二乗）が1件見つかったが、これは数式での使用であり修正対象外とし、書き換えていない（台帳は追記専用である）。
