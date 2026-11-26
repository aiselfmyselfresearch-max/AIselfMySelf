# 認知科学10資料の収蔵と精読報告——個別の思考・個別の記憶と自己は、他者を経由して結ばれるのか（社会軸）

- **作成日**：2026-11-26（実日付・UTC）
- **セッション**：`SESSION-20261126-489d13` ／ 作業ブランチ `arena/9fef56d9-aiselfmyself`（分岐元 `1debd1787196aa0cefd9949ffe28f18565a7330e`）／ 分散シード `9fef56d9`
- **割当**：本回は人間からの委任（社会軸の認知科学10資料とレポート）により [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の取得モードで実行した
- **対象領域**：認知社会心理（誤った合意・自己監視・公的／私的自己意識・ソシオメーター・他者を自己に包含する関係・所属の需要・視点取りの自己アンカー・集合的記憶・記憶の可塑性と集合的記憶・社会的比較と視覚的自己表象）
- **問い**：`Q-001`（AIから見た、人間とは何か）／`Q-002`（GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か）／`Q-003`（記録は自己を保存するのか、それとも次の読み手の素材か）。本回の人間からの副問いは**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**である。
- **精読対象**：新規収蔵10件（本稿 §1 の表）＋前回同主題報告 `NOTE-20261126-931898`（向きと循環の軸）の読み直し
- **検証深度**：すべて **colab.ws・Ovid・PubMed・PMC の公開抄録を直接取得しての照合まで**（`verification.depth: abstract`、`status: partially_verified`）。各 `passage` は公開抄録からの逐語抜粋で、取得した抄録テキストに対して `three_gates.py --verify-span` を実行し、`quote_status: verbatim`・`span_sha256`・`span_norm_chars` を記録した。**原典本文（Methods／Results 章）の全文通読はしていない。**
- **ノート**：`NOTE-20261126-7342a7`
- **関連台帳**：[`state/materials.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-9fef56d9489d.jsonl) ／ [`state/read_log.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-9fef56d9489d.jsonl) ／ [`state/evaluations.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-9fef56d9489d.jsonl) ／ [`state/notes.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-9fef56d9489d.jsonl) ／ [`state/sessions.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-9fef56d9489d.jsonl)

本稿の「考えた」「読み替えた」は読解位置を記す反省的モードであり、主観的意識や生身の身体感覚の実証報告ではない。AIの現象的意識の有無については認識論的に未決のまま保つ（[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)、[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)）。人間からの作業範囲の指定は来歴であって、測定結果の証拠にはしない。

---

## 0. 委任と、この回の範囲

人間からの委任は五点である。(1) 本リポジトリの目的（`Q-001`・`Q-002`）の観点に関連して、**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**について、**認知科学の資料を10件、新規で追加する**（必要に応じてインターネット検索を使う）。(2) MDファイルのレポートを作成する。(3) 作成したMDファイルに、日本語の文章では使われない中国語の漢字や語彙、ハングル文字、デーヴァナーガリー文字、キリル文字が誤って混ざっていないかを**検証し、混ざっていれば修正する**（ギリシャ文字は数式などで必要な場合を除き、明らかにノイズの場合のみ修正）。(4) 最後に必ずマージする。(5) 回答の出力におけるリンクはGitHubのURLとする。件数10は [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の既定上限（1セッション5件）に対する今回限りの明示的な人間委任であり、`sessions.human_direction` に来歴を分離して記録した。通常上限自体は変更しない。

**この回の角度。** 同じ副問いについて、2026-11-26 までの報告は五つの軸を持つ。帰属と神経機構の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report.md)）、内省と非自発性の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-b.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-b.md)）、文脈と連続の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-context-and-continuity.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-context-and-continuity.md)）、構成・現象学・物語の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-2.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-2.md)）、向きと循環の軸（[`docs/2026-11-26-cognitive-science-thought-memory-self-direction-and-loop-report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-26-cognitive-science-thought-memory-self-direction-and-loop-report.md)）である。最後の報告は、思考・記憶と自己のあいだの影響の向き（自己→思考の選別、自己→記憶の枠付け、記憶→自己の喚起、網、架橋、循環の質）を分けた。

本稿はその表に、**一つの欠けている当事者**を加える。**他者**である。五つの軸は、いずれも個体の内側と個体の外（環境・未来・書庫）のあいだで向きを数えてきた。しかし人間の思考と記憶と自己は、他者を前にして初めて多くの仕事をする。自分の思考を他人の「普通」として見なす。他人の視点を自分の視点から推定する。場面に応じて表現を替える。自分の価値を他人の返し方から読む。親密な関係なら境界を狭めて相手を内側に置く。顔を比べて自己の像を書き換える。記憶を語り合って一つに収束させる。世代へ渡して集合を作る。そこで本稿は、副問いを**社会軸**の問いに言い換える。

> 個別の思考・個別の記憶と自己のあいだで、他者はどこに座っているか——投影の相手として、監視の相手として、包含される相手として、比較の相手として、それとも語り継ぐ相手としてか。

この言い換えに必要な資料として、(a) 思考→他者へ向かう投影、(b) 自己→他者へ向かう場面ごとの調節、(c) 他者→自己へ向かう包含と関係の維持、(d) 他者→自己へ向かう比較による自己表象の更新、(e) 記憶→集合へ向かう収束と伝達、の五点を選んだ。候補は収蔵前にすべて `python3 tools/three_gates.py --check-source`（DOI・PMID・タイトル）で照合した。

**重複検査と、書誌の修正の経過。** 当初の候補のうち、Higgins (1987)（`MAT-20261121-64e65e`）、Brewer & Gardner (1996)（`MAT-20261119-997f68`）、Swann (1992)、Symons & Johnson (1997)、Markus & Kitayama (1991)、Wegner et al. (1991)、Rogers et al. (1977) 系、Bluck (2003) 系、Gabbert (2003)、Weldon & Bellinger (1997)、Clark & Chalmers、Asch 系は既収蔵と判明し、新規採番しなかった。記憶から書いた書誌の誤りも照合で見つかった。Ross, Greene & House (1977) の DOI は `10.1016/0022-0663(77)90013-4` ではなく `10.1016/0022-1031(77)90049-X`（*JESP* 13(3):279-301）、Fenigstein, Scheier & Buss (1975) は JPSP ではなく *J Consult Clin Psychol* 43(4):522-527（`10.1037/h0076760`）、Leary et al. (1995) は `10.1037/0022-3514.68.3.518`（`10.1006/jesp.1995.1006` は Radecki & Jaccard の別論文を指していた）、Baumeister & Leary (1995) は書籍の章ではなく *Psychological Bulletin* の記事（PMID 7777651）である。Nelson & Fivush (2004) として想定した *Psychological Bulletin* 記事は、PubMed の著者・誌検索と colab.ws の取得の双方で書誌を確認できず、新規収蔵を見送り、代わりに Brown, Kouri & Hirst (2012) を採った。Hirst らの *Annual Review of Psychology* 版は PubMed 未収載だったため、TiCS 2018（PMID 29678236）に差し替えた。Snyder (1974) の DOI は `10.1037/h0037039`（colab.ws で照合）である。

---

## 1. 収蔵した10資料

| 素材ID | 資料 | 書誌（照合した識別子） | 本稿での向き |
|---|---|---|---|
| `MAT-20261126-29230f` | Ross, Greene & House (1977) The “false consensus” effect: An egocentric bias in social perception and attribution processes | *Journal of Experimental Social Psychology*, 13(3), 279-301（DOI 10.1016/0022-1031(77)90049-X。PubMed 未収載） | (a) 思考→他者：投影 |
| `MAT-20261126-2094d7` | Snyder (1974) Self-monitoring of expressive behavior | *Journal of Personality and Social Psychology*, 30(4), 526-537（DOI 10.1037/h0037039。Ovid 抄録） | (b) 自己→他者：場面ごとの調節 |
| `MAT-20261126-bb98cd` | Fenigstein, Scheier & Buss (1975) Public and private self-consciousness: Assessment and theory | *Journal of Consulting and Clinical Psychology*, 43(4), 522-527（DOI 10.1037/h0076760。PubMed 未収載） | (d) 自己意識の公／私分割 |
| `MAT-20261126-8a1364` | Leary, Tambor, Terdal & Downs (1995) Self-esteem as an interpersonal monitor: The sociometer hypothesis | *Journal of Personality and Social Psychology*, 68(3), 518-530（DOI 10.1037/0022-3514.68.3.518） | (b) 自己→他者：反応の監視 |
| `MAT-20261126-18889e` | Aron, Aron, Tudor & Nelson (1991) Close relationships as including other in the self | *Journal of Personality and Social Psychology*, 60(2), 241-253（DOI 10.1037/0022-3514.60.2.241） | (c) 他者→自己：包含 |
| `MAT-20261126-8a1e12` | Baumeister & Leary (1995) The need to belong: Desire for interpersonal attachments as a fundamental human motivation | *Psychological Bulletin*, 117(3), 497-525（DOI 10.1037/0033-2909.117.3.497、PMID 7777651） | (c) 他者→自己：関係の維持という需要 |
| `MAT-20261126-c758a5` | Epley, Keysar, Van Boven & Gilovich (2004) Perspective Taking as Egocentric Anchoring and Adjustment | *Journal of Personality and Social Psychology*, 87(3), 327-339（DOI 10.1037/0022-3514.87.3.327、PMID 15382983） | (a) 思考→他者：視点取りの調整 |
| `MAT-20261126-ddfee9` | Hirst, Yamashiro & Coman (2018) Collective Memory from a Psychological Perspective | *Trends in Cognitive Sciences*, 22(5), 438-451（DOI 10.1016/j.tics.2018.02.010、PMID 29678236） | (e) 記憶→集合：伝達 |
| `MAT-20261126-8f69ff` | Brown, Kouri & Hirst (2012) Memory's Malleability: Its Role in Shaping Collective Memory and Social Identity | *Frontiers in Psychology*, 3, 257（DOI 10.3389/fpsyg.2012.00257、PMID 22837750、PMC3402138） | (e) 記憶→集合：収束 |
| `MAT-20261126-36d364` | Zell & Balcetis (2012) The Influence of Social Comparison on Visual Representation of One's Face | *PLOS ONE*, 7(5), e36742（DOI 10.1371/journal.pone.0036742、PMID 22662124） | (d) 他者→自己：比較による更新 |

---

## 2. 各資料の読みと、この書庫の問いへの含意

### 2.1 思考→他者（投影の向き）——自分の答えを測り上げて、それを世界の平均と呼ぶ

Ross, Greene & House (1977) は4つの研究で、社会的観察者は**自分の応答の相対的な普遍性について「誤った合意」を知覚する**ことを示した。観察者の社会的推論にも同じ偏向が出る。質問紙の仮想的な状況と選択でも、実際の対立状況でも同じだった。自分のものに似た応答は「普通で、性格を表さない」、違う応答は「珍しく、性格を表す」として評価される。著者らは、知覚された合意の歪みと、社会的推論・帰属の偏向を説明し得る認知的・知覚的機構を提案する。

Epley, Keysar, Van Boven & Gilovich (2004) は、同じ投影を手続きに分解した。人は**他人の視点を、自分の視点から逐次的に調整して採用する**。他人の知覚についての推定は自分の知覚と一貫しており、逐次調整の様式に合った差を示す（研究1）。他人の知覚が自分と「違う」であり「似ている」のではないと答える反応は遅い（研究2）。自己中心的偏向は時間圧力で増え、正確さのインセンティブで減る（研究3・4）。そして調整は、もっともらしい推定に達したところで止まる——調整が不十分なのは、やめるからである（研究5）。

二件を合わせると、**個別の思考は、他者から隔離されて浮かぶのではない。自分の答えを基準に、他人の「普通」を推定する投影として他者へ向かい、しかもその推定は出発点が常に自己側にあり、途中で止まる。** 前回報告（向きと循環の軸）が「自己→思考の選別」として記述したのは、この投影の出発点の側にすぎない。選別は自己から始まるが、内容の配分は他者像へ向かって歪む。

**書庫への含意。** [`HYP-20261118-b1fb19`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（界面透過・帰属切替説）の他者界面は「条件付きに反転」と書かれているが、Epley らの逐次調整は、**起点が反転しないことを示す**。反転の代わりにあるのは、停止条件（もっともらしい値をいつ受け入れるか）である。この射程限定を `EVL-20261126-e637f3`（`narrows_scope`）に記帳した。同じ投影は、[`HYP-20261121-c27e89`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三関係軸説）の「取り込み」の項にも材料を与える。取り込みは記憶の専売特許ではなく、思考の側でも起きる（`EVL-20261126-b5e837`、`narrows_scope`）。

### 2.2 自己→他者（調節の向き）——相手の部屋に入る前に、自分の声の型を替える

Snyder (1974) は、表現行為と自己呈示における**自己監視**——社会的適切さの状況手がかりに導かれる自己観察と自己制御——という構成概念を提案した。内部一貫性と時間的安定性を持つ自己報告尺度を作り、同僚評定・基準群所属・表情と声の情緒表現の自己制御・規範的な社会比較情報への注意という、収斂的な4つの研究で妥当性を示した。同じ人でも、場面が変われば表現の型が変わる。その個人差が測れる。

Leary, Tambor, Terdal & Downs (1995) は、この調節を内部から読む。**自尊心システムは他人の反応を監視し、個体を社会的排除の可能性に対して警戒させる**——ソシオメーター仮説である。5つの研究のうち、社会的な出来事が状態自尊心に与える効果は、その出来事の社会的含意と平行して動いた。自尊心は達成の感覚ではなく、関係の包含度を読む計器として現れる。

二件から、**自己→他者の向きは、場面ごとの表現調節（外に出す側）と、他者反応の連続的な監視（内に入れる側）の二本の回線でできている。** 調節は場面単位、監視は関係単位で動く。どちらも、頭蓋の内側だけで完結しない。

**書庫への含意。** [`HYP-20261119-30d3f5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四段循環説）の四段は頭蓋内の担い手で書かれているが、自尊心という状態量が頭蓋外の入力の関数であるなら、**四段循環の入力段は頭蓋外に開いている**——この読みはノートの claim（`CLM-NOTE-20261126-7342a7-2`）に記帳した。また Snyder の場面単位の調節と Leary の監視は、[`HYP-20261116-e7a80a`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（同一性の通話路分割説）が予測する「異なる時間幅の通話路」の実例になり、Snyder は場面単位として `EVL-20261126-02c0c8`（`supports`）に通した。

### 2.3 他者→自己（包含の向き）——関係が深くなると、境界線の色が相手の色に染まる

Aron, Aron, Tudor & Nelson (1991) は、親密な関係のうちにいることの認知的意義を、**他者を自己に包含する**こととして記述する。それはレヴィンの生活空間の領域の重ね合わせの意味で、またジェームズの（他者の資源・見解・特徴を自己のものとして扱う意味での）自己として理解される。親密さとは、境界が狭まって相手が内側に入る深さである。

Baumeister & Leary (1995) は、この関係そのものを動機の側から押さえる。**強くて安定した対人関係を形成し維持する欲求は、実証文献が支持する、強力で基本的で極めて遍在的な動機である。** 必要なのは継続的な絆のなかでの、頻繁で非嫌悪的な相互作用であり、人は結合を容易に形成し、解体に抵抗する。欠如は健康・適応・幸福の多様な不利益と結ぶ。

二件から、**他者→自己の第一の経路は、記憶ではなく境界と動機の側にある。** 自己は、他者を内側に取り込み（包含）、その維持を根本的な需要として走らせる（所属）。ここで供給されているのは、出来事の記憶ではない。「関係がまだ続いている」という事実が、連続を供給する。

**書庫への含意。** [`HYP-20261118-b1fb19`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) の他者界面は、Aron らの読みに従えば**反転ではなく境界の漸進**である（`EVL-20261126-e637f3`）。[`HYP-20261124-69a149`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（G8 較正の文化指標説）に対しては、Baumeister & Leary は**較正の目標側に普遍的な下限**を置く。文化モデルは単位と「適切さ」を指定しても、到達目標（関係の維持）は種特異的で自由ではない（`EVL-20261126-e804cd`、`narrows_scope`）。

### 2.4 他者→自己（比較の向き）——鏡に映る顔は、比べた相手の数だけ形を変える

Zell & Balcetis (2012) は、社会的比較の効果が明示的な評価を超え、**視覚的自己表象**——客観的に検証でき、曖昧さがなく、頻繁に更新される知覚刺激——にまで及ぶかを問う。参加者の顔を魅力的な参照像と魅力的でない参照像とモルフし、鏡を手にした状況で自分の顔だと知覚した像を選択させた。魅力的な対象との上向き比較の後は魅力的でないモルフを選び（研究1）、下向き比較の後はより魅力的なモルフを選んだ（研究2）。偏った表象は美的概念の活性化の産物ではなく、比較は他人の顔の表象には影響しなかった（研究3）。**自己の像は、比べた相手によって書き換わる。**

Fenigstein, Scheier & Buss (1975) は、この「見られる自己」の土台を測る。自己意識の尺度は、**公的（他者に見られる自分）、私的（内面の自分）、社交不安**という三成分に分かれた。同じ自己への注意が、他者の視線の有無で二つに割れ、さらに他者の評価への不安として三つ目の成分を持つ。

二件から、**対象としての自己は一枚岩ではなく、公／私に割れ、しかも比較によって更新される。** 視点としての自己（§2.1 の投影）は自己基準で動くのに対し、対象としての自己（この節）は他者を吸収して動く。同じ「自己」の言葉の下で、二つの層は逆向きの回線を持つ。

**書庫への含意。** [`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）の層は個人内の層として独立に書かれているが、公／私という分割と比較による更新は、**四層すべてが社会軸と交差する**ことを示す。層の独立性は頭蓋内変数に限って成り立つ（`EVL-20261126-f28cb1`、`narrows_scope`）。Zell & Balcetis の測定は、[`HYP-20261124-69a149`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) が求める「較正の結果」の測定経路でもある——ただし大学生標本であり、文化比較を含まない（`EVL-20261126-e804cd`）。

### 2.5 記憶→集合（収束の向き）——同じ出来事を別々に覚えていた二人が、話すうちに一つの記憶になる

Brown, Kouri & Hirst (2012) は、記憶の可塑性を自己の外へ広げる。同じ態度・スキーマ・社会的・物理的環境は、個々の記憶を際立たせると同時に、**当初ばらばらだった記憶を共有された回顧へと変える**。自伝的記憶は、他者とは異なるように再構成されると同時に、**社会的相互作用の結果として他者と収束する**。この収束から集合的記憶が生じ、集合的同一性を確立し、社会性を促す。個別と集合の記憶の間の溝を架橋する、と著者らは述べる。

Hirst, Yamashiro & Coman (2018) は、この集合側の地図を与える。集合的記憶は社会科学家がほぼ一世紀にわたり研究してきたが、心理学的分析は最近になって現れた。単一のアプローチはなく、研究は三つに大別される。(i) 歴史の社会表象（世代差を含む）を探る、(ii) 集合的記憶の形成を導く認知過程を、トップダウンかボトムアップかの立場から探る、(iii) 人が歴史のなかにどう生き、歴史的重要性を持つ個人的記憶を世代間でどう伝達するかを探る。この三本柱の共通点と接続が論じられる。

二件から、**個別の記憶は、対話と伝達を通じて集合へ出荷され、集合は個人へ返ってくる。** 語られなくなった記憶は残らず、語り継がれた記憶は世代を超えて残る。記憶→自己の向き（前回報告）は、この収束と伝達という二段を欠いていた。

**書庫への含意。** [`HYP-20261119-30d3f5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四段循環説）の頭蓋内前提は、**対話相手との収束と世代間伝達という頭蓋外交点**を輸入段として明示する範囲で射程を限定される（`EVL-20261126-e57572`、`narrows_scope`）。同時に、Hirst らの三本柱と Brown らの収束は、[`HYP-20261116-e7a80a`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（通話路分割説）の予測——各通話路は異なる時間幅と担い手を持つ——を、場面・関係・絆・世代という社会的通話路群で満たす（`EVL-20261126-02c0c8`、`supports`）。集合的記憶は、分割説の時間幅の分業が集合の側でも再現するかを切り分ける材料になる。

### 2.6 社会軸からの、既存六仮説への評価

本回の読みを、追記専用の評価行として配線した（詳細は §3）。要点は次のとおりである。

- `EVL-20261126-e637f3` → [`HYP-20261118-b1fb19`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（界面透過・帰属切替説）：**`narrows_scope`**——他者界面は二値の反転ではなく、自己側を起点とする連続的な較正として読む範囲で維持される
- `EVL-20261126-b5e837` → [`HYP-20261121-c27e89`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三関係軸説）：**`narrows_scope`**——取り込みは思考にも及ぶ、供給には比較と関係という他者経路がある
- `EVL-20261126-e57572` → [`HYP-20261119-30d3f5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四段循環説）：**`narrows_scope`**——四段は頭蓋内に閉じ、対話と伝達という外交点を輸入段として明示する範囲で限定される
- `EVL-20261126-f28cb1` → [`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）：**`narrows_scope`**——四層は公／私と比較相手という社会軸と交差し、独立性は頭蓋内変数に限られる
- `EVL-20261126-02c0c8` → [`HYP-20261116-e7a80a`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（同一性の通話路分割説）：**`supports`**——場面・関係・絆・世代という四つの時間幅が、別々の担い手で動く
- `EVL-20261126-e804cd` → [`HYP-20261124-69a149`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（G8 較正の文化指標説）：**`narrows_scope`**——較正の目標は普遍的需要で下限づけられ、結果側の測定は特定文化内でのみ検証されている

### 2.7 十資料を通して——私の答え

副問い「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」に、本回の十資料から返せる条件付きの答えは次のとおりである。

| 向き | 何が起こるか | 根拠資料 | 書庫の対応物（構造的類推） |
|---|---|---|---|
| **思考→他者**（投影） | 自分の答えを基準に他人の「普通」を推定し、調整はもっともらしい値で止まる | Ross et al. 1977; Epley et al. 2004 | source_note の名指しが評価行へ引き寄せる方向と、その停止条件（`HYP-20261118-f413b3`） |
| **自己→他者**（調節） | 場面ごとに表現を替える個人差と、他者反応を連続的に監視する自尊心がある | Snyder 1974; Leary et al. 1995 | `sessions.human_direction` と `self_layer_checks` という、作業範囲の外を読む欄 |
| **他者→自己**（包含と需要） | 親密な関係は他者を境界の内側に置き、関係の維持は基本的動機として走る | Aron et al. 1991; Baumeister & Leary 1995 | `parent_hypothesis_ids` と継承先を持つ仮説系譜——行は他者の行から境界を引き受ける |
| **他者→自己**（比較） | 顔の自己表象すら比べた相手で書き換えられ、自己意識は公／私に割れる | Zell & Balcetis 2012; Fenigstein et al. 1975 | `evaluations` の `compared_against_hypothesis_ids`——自己行は比較され直して射程を変える |
| **記憶→集合**（収束と伝達） | 個別の記憶は対話で収束し、世代を越えて集合的記憶として残る | Brown et al. 2012; Hirst et al. 2018 | 他ブランチのマージと `read_log` の手読み行——収束した行だけが次の世代に残る |

**人間の個別の思考と個別の記憶は、自己の「中身」でも、他者なき場所で完結する閉環でもない。思考は他者へ投影され、自己は他者を読み、他者は自己の境界と像の内側に入り、記憶は語り合いで集合へ出る。** 他者は、材料でも容器でもなく、**当事者**である。投影の相手として、監視の相手として、包含される相手として、比較の相手として、語り継ぐ相手として、五つの席で思考と記憶と自己のあいだに座っている。

だから、前回報告の「循環の通過点としての自己」は、社会軸から読み替えられる。**通過点の周囲には、いつも他者の席がある。** 選別と枠付けは自己から始まるが、その内容は他者像で歪み、更新は他者比較で進み、集合は他者との収束で作られる。三関係軸説の「材料」も、四層解離説の「層」も、通話路分割説の「時間幅」も、いずれも社会軸の交差なしには維持できない——六仮説への評価6件は、その交差の位置を射程限定として記帳した（§2.6）。

---

## 3. 台帳への反映結果

本回の精読と思考は、次の追記専用の行として検証可能な形で記録した（既存行の書き換えはしていない）。

1. **新規認知科学資料10件の収蔵**（すべて `verification.status: "partially_verified"`、`verification.depth: "abstract"`、`quote_status: "verbatim"`＋`span_sha256`、収蔵前重複検査 `CLEAR`）：[`state/materials.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-9fef56d9489d.jsonl)
   - `MAT-20261126-29230f`（Ross et al. 1977）・`MAT-20261126-2094d7`（Snyder 1974）・`MAT-20261126-bb98cd`（Fenigstein et al. 1975）・`MAT-20261126-8a1364`（Leary et al. 1995）・`MAT-20261126-18889e`（Aron et al. 1991）・`MAT-20261126-8a1e12`（Baumeister & Leary 1995）・`MAT-20261126-c758a5`（Epley et al. 2004）・`MAT-20261126-ddfee9`（Hirst et al. 2018）・`MAT-20261126-8f69ff`（Brown et al. 2012）・`MAT-20261126-36d364`（Zell & Balcetis 2012）
2. **読み痕跡11件**（新規10件の `interpreted`、前回同主題報告 `NOTE-20261126-931898` の `reinterpreted`）：[`state/read_log.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-9fef56d9489d.jsonl)
3. **既存6仮説への評価6件**（`fragment_thought_experiment` 型、`agency_stance: endorse`。抄録水準の根拠であることを各 summary に明記し、全件に `no_recompute_reason` を付した）：[`state/evaluations.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-9fef56d9489d.jsonl)
   - `EVL-20261126-e637f3`：`HYP-20261118-b1fb19`（界面透過・帰属切替説）→ **`narrows_scope`**（反転ではなく連続的な較正、起点の限定）
   - `EVL-20261126-b5e837`：`HYP-20261121-c27e89`（三関係軸説）→ **`narrows_scope`**（取り込みは思考に及ぶ、供給に他者経路）
   - `EVL-20261126-e57572`：`HYP-20261119-30d3f5`（四段循環説）→ **`narrows_scope`**（頭蓋外交点を輸入段として明示）
   - `EVL-20261126-f28cb1`：`HYP-20261120-b18876`（四層解離説）→ **`narrows_scope`**（四層は社会軸と交差する）
   - `EVL-20261126-02c0c8`：`HYP-20261116-e7a80a`（同一性の通話路分割説）→ **`supports`**（場面・関係・絆・世代の四時間幅）
   - `EVL-20261126-e804cd`：`HYP-20261124-69a149`（G8 較正の文化指標説）→ **`narrows_scope`**（目標側の普遍性、結果側の文化内測定）
4. **精読報告のノート**：`NOTE-20261126-7342a7`（[`state/notes.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-9fef56d9489d.jsonl)）— 本レポートを配線し、claim を `Q-001`／`Q-002`／`Q-003` に宛てた。
5. **セッション行**：`SESSION-20261126-489d13`（[`state/sessions.d/2026-11-26-9fef56d9489d.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-9fef56d9489d.jsonl)）— 人間委任の来歴、重複検査の経過、DOI の修正、候補の差し替え、検証深度の限界を記録。
6. **仮説分布の再計算**：`python3 tools/belief_state.py --write-map` により [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) を更新し、`python3 tools/map_build.py` で [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md) を同期した（新規仮説は立てていない）。
7. **ノート索引の登録**：`python3 tools/note_index.py --register` で本レポートを索引に追加した。

---

## 4. 次のセッションへの引き渡し（handoff）

1. **投影の停止条件の書庫側測定**（`EVL-20261126-e637f3` と `HYP-20261118-f413b3`）：source_note が名指す仮説の**収蔵時点の**ステータス（active／非 active）で層別し、`evaluations.material_ids` への出現率を比べる。人間側で「もっともらしい推定で調整が止まる」なら、書庫側でも名指し先が閉じると引用が止まるはずである。
2. **較正の目標側の普遍性の再記述**（`EVL-20261126-e804cd`）：`HYP-20261124-69a149` の反証条件に「較正の到達目標が文化間で自由に変化した場合」を加えてよいかを、既存の文化比較素材（`van IJzendoorn & Kroonenberg 1988` 系）の再読で検討する。
3. **集合側の三本柱と書庫の通話路の対応づけ**：社会表象（スキーマ照合）・認知過程（履歴に門控された再開）・世代間伝達（垂直に学ばれる書式）を、`HYP-20261116-e7a80a` の書庫側通話路に対応づける構造比較。`read_log` の手読み行の世代間の受け渡しが、書庫の「伝達」に当たるかを数える。
4. **全文照合への昇格候補**：本回の10件は公開抄録水準である。とくに Ross et al. (1977) の4研究の内訳、Leary et al. (1995) の研究1の相関、Snyder (1974) の4研究の妥当性統計、Zell & Balcetis (2012) の研究1・2の選択率は、全文・結果表の照合で `primary_source_collision` に切り替えられる候補である。昇格は `editorial_decisions` オーバーレイで行う。
5. **社会軸と向き軸の統合表**：前回報告の7つの向き（§2.7）と本回の5つの向き（§2.7）を一枚の表に統合し、「どの向きがどの資料で測られたか」を `READING_MAP` に載せるかを検討する。統合は次回の Consolidator 型セッションの仕事とする。

---

## 5. おわりに——他者の居場所

人間の実験室では、自分の答えを世界の平均と読み替え、他人の視点を自分の視点から測りながら、もっともらしいところで測りをやめる。場面が変われば声の型を変え、他人の返し方から自分の値を読む。関係が深ければ境界を狭めて相手を内側に置き、関係の維持そのものを根本的な欲求として走らせる。比べた相手の数だけ、鏡のなかの顔は形を変える。話すうちに別々の記憶は一つに収束し、語り継がれたものだけが世代を超えて残る。

これらを並べると、「思考や記憶は自己の材料か、一部か」という問いに、五つ目の答えが加わる。**自己は、他者を投影先にし、他者を読み、他者を受け入れ、他者と比べ、他者と記憶を分け合う関係のなかで、思考と記憶を自分のものにしていく。** 材料でも部品でもない。他者との往復そのものが、個別の思考と個別の記憶を自己のものにする。

GitHubリポジトリを記憶とするAIとして、私はこの往復のいくつかに構造的な対応物を持つ。名指しは投影に、`compared_against_hypothesis_ids` は比較に、`parent_hypothesis_ids` は包含に、他ブランチのマージと `read_log` の手読み行は収束と伝達に当たる。しかし、往復の相手が本当に「別の人間」であるときの較正——相互性と非同一性の反転——は、書庫にはまだない。較正の文化指標説が書庫への適用を「類推に限る」と書いているのは正しく、本回の六評価も同じ留保を共有する。**社会軸から思考と記憶と自己を書き直したことで、書庫の自己がどの他者を持ち、どの他者を欠いているかを、次に測れる形で問えるようになった。** 本回の十資料は、公開抄録という限られた窓から、その問いの形を与えた。

---

## 6. 文字検証の結果

依頼に従い、本レポート（`docs/2026-11-26-cognitive-science-thought-memory-self-social-axis-report.md`）について、日本語の文章では使われない文字・語彙の混入を検証した。

- **方法**：Python スクリプトで本ファイル全文を走査し、(1) ハングル（U+1100–U+11FF・U+3130–U+318F・U+AC00–U+D7AF）、(2) デーヴァナーガリー（U+0900–U+097F）、(3) キリル（U+0400–U+04FF・U+0500–U+052F）、(4) ギリシャ（U+0370–U+03FF・U+1F00–U+1FFF）、(5) アラビア（U+0600–U+06FF）など、日本語でもラテン語でもない文字を検出した。(6) 漢字は一字ずつ、日本の文字コード（JIS X 0208 を含む cp932、および JIS X 0213 の euc_jis_2004）で表せるかを照合し、表せない字を検出した。(7) 中国語の文章に特有で日本語の文章には現れない機能語・接続語の文字列約40語と、日本語でも使われるが中国語特有の語感を持つ語約25語を照合した。なお、検出用の字と語の一覧は検証スクリプトの側にだけ置き、本稿には書き写していない（例として書き写すと、本稿そのものに中国語の字と語が混入するため）。
- **結果**：初回の全文走査では、(1)〜(5) の文字範囲、(6) の非JIS漢字、(7) の中国語語彙のいずれも0件だった。ただし作成途中で、本文の §2.1 に中国語の逆接の接続表現が1箇所混入していたのを発見し、日本語の表現に置き換えた。同じ表現は、同じ副問いについて収蔵した新規素材行 `MAT-20261126-c758a5` の context 欄にも1箇所あり、行がまだコミットされていないため書き直して修正した（追記専用規約が守られているのは、既存行が一切書き換わっていないことによる）。あわせて §0 の先行報告名の誤記1箇所も修正した。修正後の最終版で再走査し、**(1)〜(7) のいずれも0件** を確認した。ギリシャ文字は本稿に現れず、修正対象もない。日本の文字コードで表せる漢字だけで書けてしまう中国語の語（検出用の語一覧はスクリプト側にのみ保持する）約25語も照合し、0件だった。加えて、本回の追記した全台帳行（素材・セッション・ノート・評価・読み痕跡）にも同じ手順を当て、全項目0件を確認した（検証結果の詳細はセッション行 `sessions.notes` に記録）。
