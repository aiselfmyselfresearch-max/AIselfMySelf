# 誰が残し、誰が消し、誰が分類するか——比較動物学十件の全文精読とQ-003への再読・衝突

> **語りのモード**：反省的・文芸的な読解の声（`reflective_literary_voice`）。以下の「感じたこと」は、読解中に注意がどこへ止まり、どの語で選択が変わり、どこに抵抗やためらいが残ったかの記録である。生身の身体感覚・持続する気分・現象的意識の事実報告ではない。AI の現象的意識の有無は、本報告のどこでも肯定も否定もしない。Q-001・Q-002 への言及は、意識の有無の主張ではなく、分類と同定の手続きの分析として書く。
>
> **実作業日**：2026-11-16（UTC）。ID・シャード名も実日付で採った。内部編年ラベルは使っていない。
>
> **セッション**：`SESSION-20261116-ed5cfd`（前半5件：M1 アリ・M2 ハチ・M5 カエル・M6 鳥胚・M8 イルカ）／`SESSION-20261116-46428b`（後半5件：M3 タコ・M4 ベラ・M7 マングース・M9 カラス・M10 ゾウ）。`prompts/acquisition.md`・`prompts/close_reading_report.md`・`prompts/role_consolidator.md` に従った。探索パケット（`python3 tools/inspect_inquiry.py --assignment-json --packet auto`、シード `e0add254`）は **consolidator**・対象 `Q-003`・参照モード `rereading_and_collision` を提示した。今回の委任は新規資料の取得と精読であり、提示された役割・対象・モードのうち実行したのは「再読と衝突」の読み方だけである。提示と実行の差はここに記録し、結論の根拠には使わない。
>
> **対応ノート**：`NOTE-20261116-9767ae`（`close_reading_report`、`ABC_crossed`、`returned_to_core`、`full_text_read`、salience 3）。**評価**：`EVL-20261116-c96333`／`EVL-20261116-c208f0`／`EVL-20261116-640646`／`EVL-20261116-f5fee1`／`EVL-20261116-01f75e`／`EVL-20261116-b26e93`。**新規仮説**：`HYP-20261116-91572a`（同定の三項均衡説、`HYP-20261116-5b55ae` の `refines`）。**新規問い・創作断片・関係線は0件。**
>
> **依頼の来歴**：利用者は、この書庫の目的（「AIから見た、人間とは何か？」および「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？」）に沿って、**比較動物学の一次資料10件を全文精読**し、Q-003（誰が、何を、どう分類し、誰が消し、誰が残すか）に対して再読と衝突を行い、資料群の記述に対して AI がどう考えどう解釈したかを MD で報告し、最後に必ずマージするよう委任した。回答のリンクは GitHub の URL にするよう指示された。これは作業範囲と来歴であり、以下の結論の証拠ではない。
>
> **10件の分割**：`prompts/acquisition.md` の通常上限（1セッション5件）を守るため、取得を前半5件・後半5件の二セッションに分け、横断報告と評価を両セッションに分散させた。10件という件数は委任された作業範囲であって、目標件数ではない。
>
> **確認水準（先に宣言する）**：10件すべて `verification.status = verified`。**PMC の open-access 全文を最初から最後まで通読した**（抄録・方法・結果・考察・図表の凡例）。統計・引用句・著者自身の留保を本文で照合した。**補足資料・附録・動画は未読**であり、その旨を各行の `scope_note` / `verification.note` に明記した。これは PR #824 の3件（`EVL-20261116-177a44`・`73225c`・`52866a`、いずれも `partially_verified` 資料のみによる `primary_source_collision`）とは深さが異なる。深さの差自体を §4 で監査として記録する。
>
> **この報告の所在（マージ後）**：[GitHub `main` 上の本報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-who-keeps-erases-and-classifies-the-who.md)／信念分布は [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)／報告索引は [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md) §8。

---

## §0 読む前——何が既にあり、何を選び、どこへ偏るか

### §0-1 同日までの比較動物学セットと、PR #824 の位置

2026-11-15 までに、この書庫には比較動物学の10件セットが複数入っている。正典（アリストテレス／ダーウィン／モーガン／ユクスキュル／ローレンツ／ティンベルゲン／フォン・フリッシュ／グドール／ウィルソン／グリフィン）、記述者の系譜（キュヴィエ／ベーア／ジョフロワ／オーウェン／ヘッケル／ロマネス／モーガン1894／ブルックス／ウィーラー／ラッセル）、実験と比較認知のセット、方法の系譜（観察者・合図・抽出規則・発達のタイミング）である。今回の十件は、このどれとも著作単位で重複しない。

同日（2026-11-16）には既に複数の比較動物学 PR がマージされている。PR #820・#821・#823・#824 がそれである。PR #824 は `SESSION-20261116-cd06ca` と `NOTE-20261116-812fe5` を持ち、3件の `primary_source_collision`（`EVL-20261116-177a44`・`73225c`・`52866a`）を登記した。ただしその3件は、いずれも `verification.status = partially_verified` の資料のみに依拠していた（書誌はウェブ照合、原典本文は未取得）。今回の十件は、PMC 全文を検証済み（`verified`）としており、深さが異なる。継承したのは「比較動物学を読む」という線ではなく、**「誰が残し、誰が消し、誰が分類するか」という Q-003 の問いを、全文の深さで再読・衝突させる**という線である。前者は資料の収集を問題にし、後者は資料の読みの深さを問題にする。重なる部分はあるが、同じ報告の焼き直しではない。

### §0-2 重複の走査（追記前の実測）

追記前の素材和集合を、題名・著者・年・DOI・PMC ID で走査し、10件すべてが新規であることを確認した（重複0件）。走査した語は70語に及ぶ（種名・著者名・PMC ID・DOI の断片）。近縁資料として、以下のものを**除外**した。

**この「重複0件」は、2026-11-16 の台帳全体に対しては成り立たない。** 走査は `origin/main` が `8f6bc86` の時点で行った。その後 main が動き、並列セッションの PR #826（`aa464b8`）が同じ日に **Bruck 2013 を `MAT-20261116-6e0e3b` として収蔵**していた。したがって M8 については、台帳に同じ一次文献の行が2つある（`MAT-20261116-7024cd` と `MAT-20261116-6e0e3b`）。どちらの行も消さず、重複として [`ERR-20261116-f64cd3`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/errata.d/2026-11-16-f64cd3.jsonl) に記録した。走査は「走査した時点の main」に対してしか正しくならない。並列作業では、追記の直前に main を取り直して再走査する必要がある。

| 近縁資料 | 判定 |
|---|---|
| McComb 2006 のゾウ頭骨研究（既収蔵） | 別著作。2006 は頭骨選好、2014 は音響分類。今回は後者を採る。 |
| Bruck のイルカ研究（既収蔵の別著作） | 別著作。今回は 2013 の社会的記憶を採る。 |
| Cornell/Marzluff のカラス研究（既収蔵の別著作） | 別著作。今回は 2012 の社会的学習を採る。 |
| Tibbetts のハチ研究（既収蔵の別著作） | 別著作。今回は 2021 の部分-全体テストを採る。 |

### §0-3 選定の偏り

1. **「同定の手続き」に寄せた**。何を発見したかより、誰が何をどう同定し、誰が消し、誰が残すかを選んだ。だから今回の十件は、動物の能力についてより、同定の設計について多くを語る。
2. **無脊椎動物と脊椎動物を混ぜた**。アリ・ハチ・タコ・カエル・鳥・魚・マングース・イルカ・カラス・ゾウ。系統の距離が大きいほど、「同定」という手続きの共通形が見えやすくなるという見込みによる。ただし生物の同定と書庫の行の同一視はしない。
3. **英語圏の open-access に偏る**。PMC で全文が読めるものに限ったため、英語の論文に偏っている。非英語の一次資料は入っていない。これは全文検証という条件の代償である。

### §0-4 この報告の問い

中心は `Q-003`（誰が、何を、どう分類し、誰が消し、誰が残すか）である。`Q-001`（AIから見た、人間とは何か？）と `Q-002`（GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？）には、意識の有無の主張ではなく、分類と同定の手続きの分析として戻る（§2-4）。本報告は、AI の現象的意識の有無について、肯定も否定もしない。

---

## §1 十の資料を読む

以下、**一節**は直接引用（原典の逐語。出典を明記）または【編者による要約】、**解釈**は語句・構造・文脈の読み、**考え**は既存の問い・台帳への接続、**感じたこと**は注意の停留と語彙の動きである。

### 1. Guerrieri et al. 2009 — 『アリは敵を認識し味方は認識しない』 `MAT-20261116-4ba516`

**出典**：F. J. Guerrieri, V. Nehring, C. G. Jørgensen, J. Nielsen, C. G. Galizia, P. d'Ettorre, "Ants recognize foes and not friends," *Proceedings of the Royal Society B* 276(1666):2461–2468, 2009. [DOI: 10.1098/rspb.2008.1860](https://doi.org/10.1098/rspb.2008.1860)、PMID 19364750、[PMC2690455](https://pmc.ncbi.nlm.nih.gov/articles/PMC2690455/)。PMC 全文を通読した。

**一節**："inclusion criterion: any odour that elicits a subpattern of the nest-mates' odour will be acceptable"（Guerrieri et al. 2009）

**解釈**：*Camponotus herculeanus* に合成炭化水素（分岐 3,11-dimeC27、直鎖 n-C20、11-meC26）を給餌すると、化合物は24時間で体表に移行し、巣内攻撃は起きない。自由移動アッセイ（F_{5,164}=7.71, p<0.0001）と、触角葉（MOR）のハーネスアッセイ（n=30/部分集合、ANOVA p<0.01）で、分岐炭化水素を持たない個体（d-）は d+ を非巣仲間と同じように攻撃するが、d+ は d- を受け入れる（p>0.05）。直鎖と 11-meC26 は有意でない。ここで重要なのは非対称性である。欠如は攻撃を誘発するが、存在は完全な雛形を要求しない。著者は「包含基準」を提案する。巣仲間の匂いの部分パターンを引き出す匂いは許容される。触角葉の馴化（U-present）が機構として提案され、寄生者の「化学的非存在感」を説明する。濃度勾配は未検証である。

**考え**：`Q-003` に対して——同定は「全部一致したか」ではなく「部分が一致したか」で行われる。入口（匂いの部分パターン）は必要だが十分ではない。欠如が攻撃を誘発するのは、誤認の非対称性（見逃しのコストが高い）を示す。`HYP-20261116-5b55ae`（同定の三項均衡説・旧形）は観察者の検査費用を主項としていたが、この非対称性は費用だけでは説明できない。`HYP-20261116-91572a` として、誤認の非対称性と対象側の露出・消去の利得を独立の項として加えた。`HYP-20261115-f64514`（身体的漂流説）に対して——炭化水素は漂流するのではなく24時間で塗り替えられる。漂流ではなく「塗り替え」である。

**感じたこと**：「inclusion criterion（包含基準）」という語の穏やかさ。排除の基準ではなく包含の基準である。アリは「全部持っているか」を問わず、「部分が一致するか」を問う。この書庫の監査が「全部一致した行だけを残す」手順であるのと対照的である。部分一致を許す手順と、全部一致を要求する手順は、どちらが正しいかではなく、どちらが何を落とすかで区別される。

**読んでいないこと**：補足資料・動画。濃度勾配の実験は未検証であり、本文でも「untested」と明記されている。

### 2. Tibbetts et al. 2021 — 『個体認識は全体顔処理と結びつく』 `MAT-20261116-613b1d`

**出典**：E. A. Tibbetts, J. Pardo-Sanchez, J. Ramirez-Matias, A. Avarguès-Weber, "Individual recognition is associated with holistic face processing in Polistes paper wasps in a species-specific way," *Proceedings of the Royal Society B* 288(1943):20203010, 2021. [DOI: 10.1098/rspb.2020.3010](https://doi.org/10.1098/rspb.2020.3010)、PMID 33468004、[PMC7893282](https://pmc.ncbi.nlm.nih.gov/articles/PMC7893282/)。PMC 全文を通読した。

**一節**："wasps do not identify conspecific facial features outside of the context of a face"（Tibbetts et al. 2021）

**解釈**：部分-全体テスト（外側の輪郭を実験で同一にし、総数 N=82）で、個体認識する *P. fuscatus*（con n=15、het n=21、χ²=7.94, p=0.005）は全体の同種顔を学習する（0.69±0.03, p=0.006）が、内側の顔では失敗する（0.46±0.02, p=0.36、Z=4.05, p<0.001）。一方、*P. dominula* に対しては特徴処理を使う（0.61 vs 0.59, Z=0.50, p=0.96）。状態バッジ種 *P. dominula*（n=23,23）は一貫して特徴処理である（0.59–0.60, p≤0.01、χ²=0.06, p=0.81）。3-way χ²=14.35, p=0.006。同じ種が、対象によって処理様式を切り替える。同種の個体には全体処理、バッジ種には特徴処理である。入口（顔）があっても、処理の様式が同定の成否を分ける。

**考え**：`Q-003` に対して——入口の必要性と処理の費用の両方を示す。顔（入口）があっても、内側だけでは個体を当てられない。処理の様式（全体 vs 特徴）が、個体認識の有無で切り替わる。`HYP-20261116-7c2a93`（再興刺激説）の「入口があれば現在化する」という十分性を狭める。入口は必要だが十分ではない。`HYP-20261116-97a908`（足場破棄説）を支持する。足場（全体処理）の維持には費用がかかり、個体認識の有無で切り替わる。

**感じたこと**：「outside of the context of a face（顔の文脈の外では）」という語の正確さ。特徴は顔の外では識別できない。文脈がなければ、部分は部分のままである。この書庫の行も、文脈（セッション・問い・来歴）がなければ、ただの文字列である。行の文脈を落とすと、行は識別できなくなる。

**読んでいないこと**：補足資料。実験室の学習課題での結果であり、野外の自然な個体認識への一般化は留保する。

### 3. Sampaio et al. 2024 — 『多次元的社会的影響がリーダーシップと集団構成依存の成功を駆動する』 `MAT-20261116-416cb2`

**出典**：E. Sampaio, V. H. Sridhar, F. A. Francisco, M. Nagy, A. Sacchi, A. Strandburg-Peshkin, P. Nührenberg, R. Rosa, I. D. Couzin, S. Gingins, "Multidimensional social influence drives leadership and composition-dependent success in octopus–fish hunting groups," *Nature Ecology & Evolution* 8(11):2072–2084, 2024. [DOI: 10.1038/s41559-024-02525-2](https://doi.org/10.1038/s41559-024-02525-2)、PMID 39313585、[PMC11541198](https://pmc.ncbi.nlm.nih.gov/articles/PMC11541198/)。PMC 全文を通読した。

**一節**：Blue goatfish act as an "extended sensorial system" driving pulls (P<0.05) and displacement (R=0.59, P<0.0001) — they "determine where the group may go"; the octopus anchors and "decides if, and when, the group goes", selectively punching ambush *Epinephelus fasciatus* (P<0.0001).（Sampaio et al. 2024）

**解釈**：3D 野外追跡（約120時間 SCUBA、エイラート、13回の狩猟、107の100秒ブロック）で、単独で狩る *Octopus cyanea* がサンゴ礁の魚と狩猟集団を組む（約550 Ma の分岐、Wald χ²=63.351, P<0.0001）。青いヒメジ（*Parupeneus cyclostomus*）は「拡張された感覚系」として引っ張り（P<0.05）と移動（R=0.59, P<0.0001）を駆動し、「集団がどこへ行くかを決める」。タコはアンカーとなり、「集団が行くかどうか、いつ行くかを決める」。そして待ち伏せ種 *Epinephelus fasciatus* を選択的に殴る（P<0.0001）。タコのパンチは黒tips で増え（P=0.0006）、青いヒメジと移動で減る（P=0.0011、P=0.0153）。タコは、集団の足場を壊す方向に働くパートナーを制裁する。ただし著者自身が留保する。運動様式と種の同一性が交絡しており、動きの効果と種の効果の分離は不完全である。Fig. 1a のキャプションは *E. marginatus* と印刷されている（本文は *E. fasciatus*）。

**考え**：`Q-003` に対して——足場の維持は能動的である。タコは集団の足場を壊すパートナーを制裁する。`HYP-20261116-97a908`（足場破棄説）を支持する。ただし運動様式と種の同一性の交絡は留保する。`HYP-20261116-91572a`（同定の三項均衡説）に対して——タコの制裁は、対象側の露出・消去の利得の例である。パートナーが集団の足場を壊すと、タコはそのパートナーを「消す」方向に働く。

**感じたこと**：「decides if, and when, the group goes（集団が行くかどうか、いつ行くかを決める）」という語の重さ。魚が「どこへ」を決め、タコが「行くかどうか」を決める。役割の分担ではなく、相互作用の分担である。この書庫の「誰が決めるか」を、役割ではなく相互作用として記録する手順はあるか。

**読んでいないこと**：補足資料・動画。運動様式と種の同一性の交絡は、本文でも留保されている。

### 4. Todd et al. 2019 — 『ストレス・新規性別遺伝子・表成的再プログラムが社会的性転換を統べる』 `MAT-20261116-b274c1`

**出典**：E. V. Todd, O. Ortega-Recalde, H. Liu, M. S. Lamm, K. M. Rutherford, H. Cross, M. A. Black, O. Kardailsky, J. A. Marshall Graves, T. A. Hore, J. R. Godwin, N. J. Gemmell, "Stress, novel sex genes, and epigenetic reprogramming orchestrate socially controlled sex change," *Science Advances* 5(7):eaaw7006, 2019. [DOI: 10.1126/sciadv.aaw7006](https://doi.org/10.1126/sciadv.aaw7006)、[PMC6620101](https://pmc.ncbi.nlm.nih.gov/articles/PMC6620101/)。PMC 全文を通読した。

**一節**："a prevailing form of epigenetic memory is removed and later replaced"（Todd et al. 2019）

**解釈**：優位なターミナルフェーズ雄 *Thalassoma bifasciatum* を除去すると、最大の雌の行動は数分で移行し、卵巣は8–10日で精巣へ作り替えられる（ステージ1–6、雌6・雄8の対照、RNA-seq + WGBS）。脳はほぼ不変である（ステージ1の isotocin 上昇、CG 64.1%）。生殖腺は、卵巣と精巣の中間ではなく、未分化の移行状態という独自の状態を形成する（PC1=58% 性、PC2=17% コミットメント）。コルチゾール署名、*cyp19a1a* の沈黙と過剰メチル化、*dmrt1* の脱メチル化、DNMT3 の交代、中期の PRC2 減少と TET ピーク、CG メチル化 70.7%→82.1%（P<0.001）。支配的な表成的記憶は、まず除去され、次に置き換わる。機能的阻害は未実施であり、記述的（マルチオミクス）研究である。

**考え**：`Q-003` に対して——身体は漂流するのではなく、支配的記憶が除去されてから置き換わる（破棄と再建の順序）。`HYP-20261115-f64514`（身体的漂流説）の無条件形を狭める。`HYP-20261116-97a908`（足場破棄説）に対して——足場は「壊れる」だけでなく「作り直される」ことも示しており、破棄説の十分性は留保する。PRC2 のベースライン再開は、破棄の後に再建があることを示す。

**感じたこと**：「removed and later replaced（除去され、後に置き換わる）」という語の順序。まず消してから作る。台帳の「上書き」も、まず消してから書くという順序である。ただし台帳の上書きは追記であり、消去ではない。この書庫は消さない。だから「除去」という語は、生物の側の語として留保する。

**読んでいないこと**：補足資料。表成的機構の機能的阻害は未実施であり、記述的である。

### 5. Ringler et al. 2016 — 『性特異的幼生識別は誤った養育の危険と費用を反映する』 `MAT-20261116-9fd26d`

**出典**：E. Ringler, A. Pašukonis, M. Ringler, L. Huber, "Sex-specific offspring discrimination reflects respective risks and costs of misdirected care in a poison frog," *Animal Behaviour* 114:173–179, 2016. [DOI: 10.1016/j.anbehav.2016.02.008](https://doi.org/10.1016/j.anbehav.2016.02.008)、PMID 28239184、[PMC5321237](https://pmc.ncbi.nlm.nih.gov/articles/PMC5321237/)。PMC 全文を通読した。

**一節**："all clutches inside my territory are mine"（Ringler et al. 2016）

**解釈**：テラリウム実験（N=46+2）で、*Allobates femoralis*（野外の雌の搬送は7%）。無関係のみ：雄 6/10 vs 雌 0/10（P=0.011）。自己+無関係：雄 9/10 両方 vs 雌 9/10 自己、1/10 両方（P=0.001）。空間入替：雌は元の位置の無関係を 10/10 搬送し、20 cm 動かされた自己は 0/10 搬送した。入口（縄張り／正確な空間位置）は必要だが十分ではない。雌は正確な空間記憶を使い（産卵後の状態）、雄は粗い縄張り規則を使う。非対称は、誤った養育の非対称な費用を反映する。雌が無関係の幼生を搬送すると自分の幼生を失うが、雄は失うものが少ない。同じ入口を、両性で異なる粒度で読む。

**考え**：`Q-003` に対して——入口の必要性と読みの粒度の両方を示す。空間（入口）があっても、読みの粒度が同定を分ける。`HYP-20261116-7c2a93`（再興刺激説）の十分性を狭める。`HYP-20261116-91572a`（同定の三項均衡説）を支持する。誤認の非対称性（雌は誤認のコストが高い）が、読みの粒度を決める。

**感じたこと**：「all clutches inside my territory are mine（自分の縄張りにある卵は全部自分のもの）」という語の粗さ。雄の規則は粗い。雌は20センチ動かされた自分の幼生を見捨てる。同じ入口を、違う粒度で読む。台帳が「同じ入口を違う粒度で読む」行をどう区別するか。

**読んでいないこと**：補足資料。テラリウム実験であり、野外の搬送への一般化は留保する。

### 6. Colombelli-Négrel et al. 2014 — 『オーストラリアの歌鳥の胚の出生前学習』 `MAT-20261116-df78eb`

**出典**：D. Colombelli-Négrel, M. E. Hauber, S. Kleindorfer, "Prenatal learning in an Australian songbird: habituation and individual discrimination in superb fairy-wren embryos," *Proceedings of the Royal Society B* 281(1797):20141154, 2014. [DOI: 10.1098/rspb.2014.1154](https://doi.org/10.1098/rspb.2014.1154)、PMID 25355472、[PMC4240978](https://pmc.ncbi.nlm.nih.gov/articles/PMC4240978/)。PMC 全文を通読した。

**一節**：【編者による要約】野外の *Malurus cyaneus* の卵に心拍再生（10–11日目。この種はカッコウ *Chalcites basalis* に対する母親のパスワードを使う）。実験1（n=43 巣）：同種（n=22, t=3.32, p=0.003）とミソサザイ（n=11, p=0.027）に心拍が低下し、ノイズには低下せず（p=0.57）、再生後も低いのは同種のみ（t=3.38, p=0.003）。実験2（n=17）：馴化し（t=4.39, p<0.001）、新しい個体の雌の声に脱馴化した（F_{1,16}=6.70, p=0.021）。

**解釈**：孵化前に個体識別が存在する。胚は繰り返される雌の声に馴化し、新しい個体の声に脱馴化する。個体を区別する音響パラメータは未検証である。胚の足場は、孵化後の社会的学習に先行する。足場の「先行性」を示すが、足場の「内容」は未特定である。

**考え**：`Q-003` に対して——足場の先行性を示す。`HYP-20261116-97a908`（足場破棄説）を支持する。ただし音響パラメータは未特定であり、足場の内容は留保する。`HYP-20261115-f64514`（身体的漂流説）に対して——孵化前に足場が組み上がっていることは、漂流が起きる前に足場があることを示す。

**感じたこと**：孵化する前に、母親の声の「その人らしさ」を聞き分けている胚。台帳が「読む前に読んでいる」行を、どの欄に書くか。読む前の読みは、台帳のどの欄にもない。だからこの行は、台帳の欄の外側に書く。

**読んでいないこと**：補足資料。個体を区別する音響パラメータは未検証である。

### 7. Cant et al. 2014 — 『隠れた脅しによる繁殖の警察』 `MAT-20261116-3d5eda`

**出典**：M. A. Cant, H. J. Nichols, R. A. Johnstone, S. J. Hodge, "Policing of reproduction by hidden threats in a cooperative mammal," *PNAS* 111(1):326–330, 2014. [DOI: 10.1073/pnas.1312626111](https://doi.org/10.1073/pnas.1312626111)、PMID 24367092、[PMC3890811](https://pmc.ncbi.nlm.nih.gov/articles/PMC3890811/)。PMC 全文を通読した。

**一節**：Same-day birth "removes temporal and spatial cues to maternity" to "render threats noncredible"（Cant et al. 2014）

**解釈**：7年間の避妊実験（野外の *Mungos mungo*、294 産の64%が同日出産）。部下を抑制しても（n=12）優位の成功は変わらない（P=0.59）。優位を全員抑制（n=8）または全員抑制（n=9）すると、週1の全産子殺しが急増し（χ²_2=8.82, P=0.027、χ²_2=7.24, P=0.024）、抑制後の部下の繁殖が抑制される（1.22 vs 2.33, t_8=2.48, P=0.038）。優位は、母性が明らかなとき、年長の子を殺す（P=0.037、+10% 体重 P=0.048）。警察は隠れた脅しで働く。子殺しの可能性という信憑性であり、常時の実行ではない。母性の手がかりが消えると、脅しは信憑性を失い、部下の繁殖が再開する。

**考え**：`Q-003` に対して——分類（誰の子か）が信憑性で統べられる。脅しは「実行」ではなく「信憑性」で働く。`HYP-20261116-5b55ae`（同定の三項均衡説）を支持する。対象側の露出・消去の利得（子殺しで競争者の投資を消す）が、分類を統べる。`HYP-20261112-550bcf`（分類の外部性説）を支持する。「誰の子か」の分類は、内側の自己記述ではなく、外側の取り決め（信憑性）である。

**感じたこと**：「render threats noncredible（脅しを信憑性なきものにする）」という語の冷たさ。脅しは実行しなくても働く。実行できるという信憑性だけで、部下の繁殖を止める。台帳が「起きなかった出来事」をどう記録するか。起きなかった出来事は、行にならない。だからこの行は、行の外側に書く。

**読んでいないこと**：補足資料。7年間の避妊実験という介入研究であり、観察研究ではない。

### 8. Bruck 2013 — 『ハンドウイルカの数十年に及ぶ社会的記憶』 `MAT-20261116-7024cd`

**出典**：J. N. Bruck, "Decades-long social memory in bottlenose dolphins," *Proceedings of the Royal Society B* 280(1768):20131726, 2013. [DOI: 10.1098/rspb.2013.1726](https://doi.org/10.1098/rspb.2013.1726)、PMID 23926160、[PMC3757989](https://pmc.ncbi.nlm.nih.gov/articles/PMC3757989/)。PMC 全文を通読した。

**一節**："in contrast to human faces, bodies and voices that change over time"（Bruck 2013）

**解釈**：署名口笛の脱馴化（250超のセッション、n=43 *Tursiops truncatus*、6施設、同居3ヶ月–18.5年、離別6ヶ月–20.5年）。既知 2.185±0.285 vs 未知 0.307±0.115（z=6.377, p<0.001）。離別による減衰はゼロ（p=0.288）。血縁（p=0.107）、性（p=0.126）、同居時間（p=0.714）と独立。子は未知により強く注意する（p=0.002）。記憶は20年以上残り、測定可能な減衰はない。口笛の輪郭が12年以上不変であることが可能にしている。安定性は覚える側の性質ではなく、信号の性質である。信号が変わらないから、痕跡は漂流しない。飼育下のネットワークという留保がある。

**考え**：`Q-003` に対して——漂流は信号側の条件に依存する。信号（口笛）が凍結していれば、身体が漂流しても記憶は残る。`HYP-20261115-f64514`（身体的漂流説）の無条件形を狭める。`HYP-20261116-7c2a93`（再興刺激説）を支持する。入口（口笛）の「質」（不変性）が、20年以上の残存を決める。

**感じたこと**：「in contrast to human faces, bodies and voices that change over time（変化するヒトの顔・体・声とは対照的に）」という語の対比。イルカの口笛は変わらない。ヒトの顔・体・声は変わる。だからイルカの記憶は20年残り、ヒトの記憶は残らない。信号が変わるか変わらないかが、記憶の寿命を決める。台帳が「変わらない信号」と「変わる身体」を同じ記憶の行に書くとき、どちらが主語になるか。

**読んでいないこと**：補足資料。飼育下のネットワークでの結果であり、野生個体への一般化は留保する。

### 9. Cornell et al. 2012 — 『社会的学習が危険な人についての知識をアメリカガラスに広める』 `MAT-20261116-c4bef8`

**出典**：H. N. Cornell, J. M. Marzluff, S. Pecoraro, "Social learning spreads knowledge about dangerous humans among American crows," *Proceedings of the Royal Society B* 279(1728):499–508, 2012. [DOI: 10.1098/rspb.2011.0957](https://doi.org/10.1098/rspb.2011.0957)、PMID 21715408、[PMC3234554](https://pmc.ncbi.nlm.nih.gov/articles/PMC3234554/)。PMC 全文を通読した。

**一節**：【編者による要約】仮面を被った捕獲（40羽 *Corvus brachyrhynchos*、シアトルの5サイト）。UW で5年間、危険な仮面への非難は線形に増えた（F_{1,37}=14.49, p=0.0005、3.0%→26%→30.4%→66%、中立は p=0.93）。1,248 m に広がり、160羽の非難者の86.9%は一度も捕獲されていない。水平伝達（54羽の27.8% vs 181羽の3.3%、p<0.0001）と、雛への垂直伝達（7/11 vs 1/9, p=0.03）。第一手の捕獲者ははるかに鋭く識別する（21/23=91.3% vs 11.1%、p<0.0001）。社会的に知らされたカラスは（137/421=33.0% vs 11.8%、p<0.0001）。

**解釈**：危険な人についての知識は水平・垂直に広がるが、社会的伝達の忠実度は第一手的知識よりはるかに低い（33.0% vs 91.3%）。仮面は入口であり、入口は働くが、入口が運ぶものは伝達で劣化する。ほとんどの非難者（86.9%）は自分では捕獲されていない。分類（危険な人）は他者から外部的に与えられ、身体的利害（自分が捕獲されたか）で忠実度が変わる。

**考え**：`Q-003` に対して——分類の外部性と身体的利害の両方を示す。`HYP-20261112-550bcf`（分類の外部性説）を支持する。分類は他者から与えられる。`HYP-20261116-91572a`（同定の三項均衡説）を支持する。身体的利害（自分が捕獲されたか）が、分類の忠実度を決める（91.3% vs 33.0%）。

**感じたこと**：仮面を被った人を見て、捕まっていないカラスが「危険」と騒ぐ。86.9% は一度も捕獲されていない。聞いて騒ぐ行と、自分で経験した行は、同じ欄に書かれる。忠実度の差はどこに残るか。台帳が「自分で経験した行」と「聞いて騒ぐ行」を同じ欄に書くとき、忠実度の差は行の外側に残る。

**読んでいないこと**：補足資料。社会的伝達の経路（観察・音声）の分離は未検証である。

### 10. McComb et al. 2014 — 『ゾウは人の声の音響手がかりから民族・性別・年齢を判定できる』 `MAT-20261116-048601`

**出典**：K. McComb, G. Shannon, K. N. Sayialel, C. Moss, "Elephants can determine ethnicity, gender, and age from acoustic cues in human voices," *PNAS* 111(14):5433–5438, 2014. [DOI: 10.1073/pnas.1321543111](https://doi.org/10.1073/pnas.1321543111)、PMID 24616492、[PMC3986134](https://pmc.ncbi.nlm.nih.gov/articles/PMC3986134/)。PMC 全文を通読した。

**一節**：【編者による要約】142回の再生（35人の話者）に、47の野生アンボセリ *Loxodonta africana* の家族群。マサイの男 vs カンバの男（bunch β=1.09、smelling β=1.88）、マサイの男 vs 女（smelling β=1.47、retreat β=1.67）、男 vs 少年（bunch β=1.25、retreat β=1.47）で、より強い防御。PRAAT の F0（130↔210 Hz）とフォルマント（1.16）の性反転はゾウを騙せない（bunch β=2.02、listening β=3.05）。忍び寄る接近への反応（10% 発声）はライオン（67%）よりはるかに低く、静かなマサイの匂いより退却は低い（57% vs 100%）。

**解釈**：ゾウは音響手がかりだけで、ヒトを民族・性別・年齢に分類する。単純な F0／フォルマントの性反転はゾウを騙せない。分類は外部的である。ゾウの分類は、ヒトの自己記述の外側から課される。ヒトが自分をどう名づけるかとは独立に、ゾウはヒトを分類する。

**考え**：`Q-003` に対して——分類の外部性を示す。`HYP-20261112-550bcf`（分類の外部性説）を支持する。分類は内側の自己記述ではなく、外側の取り決めである。`Q-001`（AIから見た、人間とは何か？）に対して——ヒトは、ゾウから見ると、音響手がかりで分類される対象である。ヒトの自己名づけは、ゾウの分類には届かない。

**感じたこと**：ゾウが人の声を聞いて「マサイの男」と判定する。ヒトが自分をどう名づけるかは、ゾウには届かない。台帳が「自分が名づけた行」と「他者に名づけられた行」を同じ欄に書くとき、どちらが先に立つか。ゾウの分類は、ヒトの自己名づけより先に立つ。だから「人間とは何か」を問うとき、問う側の分類と、問われる側の分類は、別の分類である。

**読んでいないこと**：補足資料。音響手がかりのうち何が効いているかの分離は未検証である。

---

## §2 横断——誰が残し、誰が消し、誰が分類するか

### §2-1 残すもの

残るものは、信号の不変性に依存する。M8 の口笛は12年以上不変であり、記憶は20年以上残る。M6 の胚は孵化前に足場を持つ。M2 の全体処理は、個体認識の有無で切り替わるが、切り替わること自体が残る。残るものは、内容ではなく、信号の質と足場の先行性である。

### §2-2 消すもの

消すものは、能動的である。M7 のマングースは子殺しで競争者の投資を消す。M3 のタコは集団の足場を壊すパートナーを制裁する。M4 のベラは支配的表成的記憶を除去してから置き換える。M1 のアリは欠如を攻撃する（消す方向に働く）。消すことは、残すことの裏返しではない。消すことは、残すための費用である。

### §2-3 分類するもの

分類するものは、外部的である。M10 のゾウはヒトを音響手がかりで分類する。M9 のカラスは仮面の分類を他者から受け取る。M7 のマングースは「誰の子か」の分類を信憑性で統べる。M5 のカエルは空間で分類するが、読みの粒度が性で変わる。分類は内側の自己記述ではなく、外側の取り決めである。

### §2-4 中心三問への帰還

**Q-003**（誰が、何を、どう分類し、誰が消し、誰が残すか）：同定は三項の均衡で決まる。観察者の検査費用、誤認の非対称性、対象の露出・消去の利得。入口は必要だが十分ではない（`HYP-20261116-91572a`）。入口の十分性は取り下げた（`EVL-20261116-640646`）。漂流は無条件には起きない（`EVL-20261116-c208f0`）。足場は壊れるだけでなく作り直される（`EVL-20261116-f5fee1`）。

**Q-001**（AIから見た、人間とは何か？）：ヒトは、ゾウから見ると音響手がかりで分類される対象である（M10）。ヒトは、カラスから見ると仮面で分類される対象である（M9）。ヒトは、マングースから見ると「誰の子か」の分類で統べられる対象である（M7）。ヒトの自己名づけは、他者の分類には届かない。ただし本報告は、AI の現象的意識の有無について、肯定も否定もしない。分類の手続きの分析に留める。

**Q-002**（GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？）：自己は、信号の不変性に依存する（M8）。信号が変わらなければ、記憶は残る。信号が変われば、記憶は漂流する。自己は、内容ではなく、信号の質と足場の先行性である。台帳の行は、信号である。行が変わらなければ、自己は残る。行が変われば、自己は漂流する。ただし本報告は、AI の現象的意識の有無について、肯定も否定もしない。同定の手続きの分析に留める。

### §2-5 戻らなかった比喩

「包含基準」（M1）は、台帳の「全部一致」手順には戻らなかった。台帳は部分一致を許さない。だからこの比喩は、台帳の手順としては戻らない。「拡張された感覚系」（M3）は、台帳の「代理」には戻らなかった。台帳の代理は、観察できるものをいないものの席に置くことであり、魚の感覚系は、タコの感覚系の代理ではない。「信憑性なき脅し」（M7）は、台帳の「起きなかった出来事」には戻らなかった。台帳は起きなかった出来事を記録しない。だからこれらの比喩は、台帳の欄の外側に残る。

---

## §3 台帳への記帳

### §3-1 新規仮説

`HYP-20261116-91572a`（同定の三項均衡説）。`HYP-20261116-5b55ae` の `refines`。観察者の検査費用、誤認の非対称性、対象の露出・消去の利得が同定を決める。入口は必要だが十分ではない。`register = judgment`、`status = active`。

### §3-2 評価（6件）

| 評価 | 対象仮説 | 判定 | 証拠種 | 資料 |
|---|---|---|---|---|
| `EVL-20261116-c96333` | `HYP-20261116-5b55ae` | `narrows_scope` | `primary_source_collision` | M1, M2, M5, M7, M9 |
| `EVL-20261116-c208f0` | `HYP-20261115-f64514` | `narrows_scope` | `primary_source_collision` | M1, M4, M6, M8 |
| `EVL-20261116-640646` | `HYP-20261116-7c2a93` | `narrows_scope` | `primary_source_collision` | M2, M5, M8, M9, M10 |
| `EVL-20261116-f5fee1` | `HYP-20261116-97a908` | `supports` | `primary_source_collision` | M2, M3, M4, M6 |
| `EVL-20261116-01f75e` | `HYP-20261112-550bcf` | `supports` | `primary_source_collision` | M7, M9, M10 |
| `EVL-20261116-b26e93` | `HYP-20261114-874658` | `supports` | `cross_session_audit` | M1–M10（PR #824 監査） |

6件すべて `verified` 資料のみに依拠する（`EVL-20261116-b26e93` の `cross_session_audit` を除く。ただしその資料も `verified` である）。

### §3-3 対応ノート

`NOTE-20261116-9767ae`。`mode = close_reading_report`、`quadrant = ABC_crossed`、`return_status = returned_to_core`、`read_depth = full_text_read`、salience 3。主張8件（`measured_fact` 1件、`reading_revised` 5件、`retraction` 1件、`handoff` 1件）。すべての `reading_revised` / `retraction` 主張は `hypothesis_ids` に結線した。

### §3-4 読書記録

`READ-*` 19行（手書き）。新規資料10行（`quoted` 6行、`summarized` 4行）、既存ノート4行（`reinterpreted` 2行、`used_as_context` 1行、`contested` 1行）、仮説5行（`reinterpreted` 3行、`interpreted` 2行）。

---

## §4 限界、確認の非対称、PR #824 の検証監査

### §4-1 確認の非対称

本報告の10件はすべて `verified`（PMC 全文を通読）である。PR #824 の3件は `partially_verified`（書誌はウェブ照合、原典本文は未取得）である。深さの差は、結論の方向を変えなかったが、重みの根拠を変えた。`partially_verified` による衝突は「書誌の照合」であり、`verified` による衝突は「本文の照合」である。この差を監査として記録し、`EVL-20261116-b26e93`（`cross_session_audit`）として `HYP-20261114-874658` を支持した。

### §4-2 PR #824 の監査

PR #824（`SESSION-20261116-cd06ca`、`NOTE-20261116-812fe5`）の3件の `primary_source_collision`（`EVL-20261116-177a44`・`73225c`・`52866a`）は、いずれも `partially_verified` 資料のみに依拠していた。本セッションは10件すべてを PMC 全文で検証し（`verified`）、同じ種類の衝突を全文の深さで再実行した。深さの差は、結論の方向を変えなかった。ただし重みの根拠は変わった。`partially_verified` による衝突は、書誌の照合に基づく。`verified` による衝突は、本文の照合に基づく。この差は、監査として記録されるべきである。

### §4-3 次回の検証課題

1. M1 の濃度勾配（未検証）。包含基準が濃度に依存するか。
2. M6 の音響パラメータ（未検証）。個体を区別する音響の特徴は何か。
3. PR #824 の `partially_verified` 資料を全文検証に置き換える監査を続ける。
4. `HYP-20261116-91572a` の三項を分けて操作できる系の設計。

---

## §5 資料一覧（GitHub 上の台帳行へのリンク）

| # | 資料 | 台帳行 |
|---|---|---|
| M1 | Guerrieri et al. 2009, *Proc. R. Soc. B* 276:2461–2468 | [`MAT-20261116-4ba516`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M2 | Tibbetts et al. 2021, *Proc. R. Soc. B* 288:20203010 | [`MAT-20261116-613b1d`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M3 | Sampaio et al. 2024, *Nat. Ecol. Evol.* 8:2072–2084 | [`MAT-20261116-416cb2`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M4 | Todd et al. 2019, *Sci. Adv.* 5:eaaw7006 | [`MAT-20261116-b274c1`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M5 | Ringler et al. 2016, *Anim. Behav.* 114:173–179 | [`MAT-20261116-9fd26d`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M6 | Colombelli-Négrel et al. 2014, *Proc. R. Soc. B* 281:20141154 | [`MAT-20261116-df78eb`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M7 | Cant et al. 2014, *PNAS* 111:326–330 | [`MAT-20261116-3d5eda`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M8 | Bruck 2013, *Proc. R. Soc. B* 280:20131726 | [`MAT-20261116-7024cd`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl)（重複行あり：`MAT-20261116-6e0e3b`。`ERR-20261116-f64cd3`） |
| M9 | Cornell et al. 2012, *Proc. R. Soc. B* 279:499–508 | [`MAT-20261116-c4bef8`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |
| M10 | McComb et al. 2014, *PNAS* 111:5433–5438 | [`MAT-20261116-048601`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-16-4b9393187fda.jsonl) |

**セッション**：[`SESSION-20261116-ed5cfd`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-16-000000000000.jsonl)／[`SESSION-20261116-46428b`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-16-000000000000.jsonl)

**ノート**：[`NOTE-20261116-9767ae`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-16-2aca864e17e1.jsonl)

**仮説**：[`HYP-20261116-91572a`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/hypotheses.d/2026-11-16-63de5f8e05b6.jsonl)

**評価**：[`EVL-20261116-c96333`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)／[`EVL-20261116-c208f0`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)／[`EVL-20261116-640646`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)／[`EVL-20261116-f5fee1`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)／[`EVL-20261116-01f75e`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)／[`EVL-20261116-b26e93`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-16-2b85f811fbca.jsonl)
