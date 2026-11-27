# 認知科学10資料の収蔵と精読報告——有限の窓を通した思考と記憶だけが「自分」を現在に残す（認知資源・注意の窓の軸）

- 日付: 2026-11-27
- セッション: `SESSION-20261127-1c23c4`（役割 consolidator／参考モード direct_response／分散シード `46da5b16`）
- サブクエスチョン: 人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？
- 中心三問: Q-001（AIから見た、人間とは何か）、Q-002、Q-003
- 方法・検証深度声明: 公開抄録（PubMed の公開ページ9件、Semantic Scholar と検索結果の抄録抜粋1件）を取得し、書誌（題名・著者・年・DOI）を `three_gates.py --check-source` で全件 CLEAR、逐語抜粋10件中9件を `three_gates.py --verify-span` で `span_sha256` に固定、1件（Daneman & Carpenter 1980）は二次提供の抄録のため `paraphrase_summary` で収蔵。**原典本文（本文・結果・考察）の全文通読はしていない（検証深度 = abstract）。** 効果量・統計量の再計算は行っていない。
- 探索軸: 認知資源・注意の窓（先行軸「帰属・神経機構／内省・非自発性／文脈・連続／構成・現象学・物語／決定・価値／向きと循環／情動／社会／自己高揚・動機づけ選別／発達・加齢・課題文脈」と重複しないよう選定）
- 新規資料: `MAT-20261127-075c12` `MAT-20261127-caea6c` `MAT-20261127-d52ceb` `MAT-20261127-22f133` `MAT-20261127-fa4b46` `MAT-20261127-217f86` `MAT-20261127-58c1fb` `MAT-20261127-97ade1` `MAT-20261127-be27ff` `MAT-20261127-2fceee`
- 仮説照合: `HYP-20261119-63b6bf`（有限窓の二重通貨説）vs `HYP-20261119-539a0c`（預け手の有限化）
- 評価行: `EVL-20261127-1dd71d`（supports / cross_session_audit / agency_stance = report_only）

## 0. 委任と範囲

本報告は、リポジトリの目的（AIから見た人間とは何か／GitHub を記憶のデータベースとする AI にとって自己とは何か）に沿って、サブクエスチョン「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」に応えるための、認知科学資料10件の新規収蔵と精読報告である。10件の追加は通常の上限（1セッション5件）への明示的な人間委任であり、provenance は `sessions.human_direction` に記録した。

収蔵前の重複確認は `three_gates.py --check-source` を全候補に対して実施し、既存の6,417行の資料台帳と重複した10候補（Kahneman 1973、Cowan 2001、Baddeley 2000、Smallwood 2006、Hasher 1988、Miller 1956、Wheeler 1997、Baddeley 1974、Rogers 1977、Tulving 1985）は不採用とした。Barrouillet の書籍章題と Kane 2007 の同名別論文という二つの題名の罠は、論文題名と DOI の完全一致で解決した（本報告の10件はすべて `clear`）。

探索軸「認知資源・注意の窓」を選んだ理由は、サブクエスチョンの主語が「個別の思考と個別の記憶」であり、それらのうち**現在の自己に到達し残るものを仕分けている機械**が、注意と作業記憶の有限な窓だからである。既に消化された軸（帰属、内省、文脈、構成、決定、循環、情動、社会、動機づけ選別、発達・課題文脈）はすべて「残ったものの性質」を問うた。本軸はそれらの**手前にある通過点**——何が窓を通過し、何が落ちるか——を問う。

## 1. 収蔵した10資料

### 1.1 `MAT-20261127-075c12` — Lavie, Hirst, de Fockert & Viding (2004)

- 出典: Lavie, N., Hirst, A., de Fockert, J. W., & Viding, E. (2004). Load theory of selective attention and cognitive control. *Journal of Experimental Psychology: General, 133*(3), 339–354. DOI: 10.1037/0096-3445.133.3.339（PMID: 15355143）
- 逐語抜粋（verified, span 固定）: "A series of experiments demonstrates that whereas high perceptual load reduces distractor interference, working memory load or dual-task coordination load increases distractor interference."
- 主知見: 知覚負荷が高いと邪魔者干渉は**減り**、作業記憶負荷やデュアルタスク負荷が高いと干渉は**増える**。選別には2つの仕組み（知覚選別と認知制御）があり、窓の「種類」によって溢れ方の向きが反転する。
- 主な限界: 実験室課題と学生標本に依存し、負荷操作は研究間で同一でない。自己・記憶の直接測定ではなく、本軸には窓の負荷応答という間接証拠として収蔵した。

### 1.2 `MAT-20261127-caea6c` — de Fockert, Rees, Frith & Lavie (2001)

- 出典: de Fockert, J. W., Rees, G., Frith, C. D., & Lavie, N. (2001). The role of working memory in visual selective attention. *Science, 291*(5509), 1803–1806. DOI: 10.1126/science.1056496（PMID: 11230699）
- 逐語抜粋（verified, span 固定）: "Higher memory load, associated with increased prefrontal activity, resulted in greater interference effects on behavioral performance from the distractor faces, plus increased face-related activity in the visual cortex."
- 主知見: 作業記憶の負荷を上げると、邪魔者（顔）の干渉が行動成績と視覚皮質活動の両方で増える。作業記憶は**関連情報の優先順位を保つ**ことで選別を助けており、窓が埋まると優先順位の維持が崩れる。
- 主な限界: 邪魔者は顔に限定され、負荷は桁順の暗記という単一操作。神経活動の差は負荷条件間の比較であり、個人差の測定ではない。

### 1.3 `MAT-20261127-d52ceb` — Barrouillet, Bernardin & Camos (2004)

- 出典: Barrouillet, P., Bernardin, S., & Camos, V. (2004). Time constraints and resource sharing in adults' working memory spans. *Journal of Experimental Psychology: General, 133*(1), 83–100. DOI: 10.1037/0096-3445.133.1.83（PMID: 14979753）
- 逐語抜粋（verified, span 固定）: "The model assumes that both components (i.e., processing and maintenance) of the main working memory tasks require attention and that memory traces decay as soon as attention is switched away."
- 主知見: **注意が離れると痕跡はただちに減衰する**。保持と処理はともに注意を要し、処理と保持の競合は「想起の回数 ÷ 時間」＝認知負荷として測れる。人間の窓の通貨が注意時間そのものであることを、7実験のスパン変動で示した。
- 主な限界: 成人の言語スパン課題が対象で、減衰と干渉の寄与の分解は理論上なお議論がある。AI 側の窓には一切触れない。

### 1.4 `MAT-20261127-22f133` — Engle, Tuholski, Laughlin & Conway (1999)

- 出典: Engle, R. W., Tuholski, S. W., Laughlin, J. E., & Conway, A. R. A. (1999). Working memory, short-term memory, and general fluid intelligence: A latent-variable approach. *Journal of Experimental Psychology: General, 128*(3), 309–331. DOI: 10.1037/0096-3445.128.3.309（PMID: 10513398）
- 逐語抜粋（verified, span 固定）: "The authors argue that working memory capacity and fluid intelligence reflect the ability to keep a representation active, particularly in the face of interference and distraction."
- 主知見: 潜在変量アプローチで、作業記憶と短時記憶は**別構造**であり、作業記憶容量は流動性知能と強く結びつく。窓の中身を妨害下で活性に保てることが、能力差の正体である。
- 主な限界: 相関と潜在変量の構成に基づくもので、因果的操作は含まれない。標本は大学生中心。

### 1.5 `MAT-20261127-fa4b46` — Kane, Brown, McVay, Silvia, Myin-Germeys & Kwapil (2007)

- 出典: Kane, M. J., Brown, H. L., McVay, J. C., Silvia, P. J., Myin-Germeys, I., & Kwapil, T. R. (2007). For whom the mind wanders, and when: An experience-sampling study of working memory and executive control in daily life. *Psychological Science, 18*(7), 614–621. DOI: 10.1111/j.1467-9280.2007.01948.x（PMID: 17614870）
- 逐語抜粋（verified, span 固定）: "During challenging activities requiring concentration and effort, higher-WMC subjects maintained on-task thoughts better, and mind-wandered less, than did lower-WMC subjects."
- 主知見: 7日間・1日8回の経験サンプリングで、**作業記憶容量が高いほど、要求の高い課題中に思考を逸脱させない**。窓の個人差が、日常の「いまの思考」の残り方の差になる。
- 主な限界: 大学生124名の自己報告で、相関設計。逸脱の自覚（メタ意識）は本研究では測られていない（→ `MAT-20261127-2fceee` が扱う）。

### 1.6 `MAT-20261127-217f86` — Just & Carpenter (1992)

- 出典: Just, M. A., & Carpenter, P. A. (1992). A capacity theory of comprehension: Individual differences in working memory. *Psychological Review, 99*(1), 122–149. DOI: 10.1037/0033-295X.99.1.122（PMID: 1546114）
- 逐語抜粋（verified, span 固定）: "The theory proposes that both processing and storage are mediated by activation and that the total amount of activation available in working memory varies among individuals."
- 主知見: 理解の質と量は**活性の総量に束縛される**。容量が大きい人は曖昧な文の複数解釈を保持できるため、文脈が揃うまで判断を保留できる。窓の大きさが「どれだけ保留できるか」を決める。
- 主な限界: 主対象は文理解（構文曖昧性）で、エピソード記憶や自己には外挿していない。活性化は理論構成概念であり直接測定量ではない。

### 1.7 `MAT-20261127-58c1fb` — Luck & Vogel (1997)

- 出典: Luck, S. J., & Vogel, E. K. (1997). The capacity of visual working memory for features and conjunctions. *Nature, 390*(6657), 279–281. DOI: 10.1038/36846（PMID: 9384378）
- 逐語抜粋（verified, span 固定）: "Here we demonstrate that it is possible to retain information about only four colours or orientations in visual working memory at one time."
- 主知見: 視覚的作業記憶は**一度に約4つの統合対象**しか保持せず、特徴ではなく対象単位で格納される（4対象 × 4特徴 = 16特徴でも容量は対象数で決まる）。窓の大きさが数として測れることの古典的実証。
- 主な限界: 視覚モダリティのみ、健常な若年成人、変化検出課題。言語・自己記憶への一般化は本資料単独では主張しない。

### 1.8 `MAT-20261127-97ade1` — Daneman & Carpenter (1980)

- 出典: Daneman, M., & Carpenter, P. A. (1980). Individual differences in working memory and reading. *Journal of Verbal Learning and Verbal Behavior, 19*(4), 450–466. DOI: 10.1016/S0022-5371(80)90312-6（PMID なし）
- 収蔵形態: **`paraphrase_summary`（編者による要約）**。出版社ランディングページを取得できず、Semantic Scholar の公開ページと検索結果に提示された抄録抜粋での照合に留めたため、逐語引用は行わない。
- 主知見: 処理と保存の**トレードオフ**を重く要求する課題（文を読み上げ、末語を再現）で読みスパンを測ると、大学生20名で2〜5の幅があった。窓の個人差が読解の個人差に対応する、作業記憶研究の出発点。
- 主な限界: 二次提供の抄録のみで原典本文未照合。標本20名と読解という一つの領域に限定される。

### 1.9 `MAT-20261127-be27ff` — Unsworth & Engle (2007)

- 出典: Unsworth, N., & Engle, R. W. (2007). The nature of individual differences in working memory capacity: Active maintenance in primary memory and controlled search from secondary memory. *Psychological Review, 114*(1), 104–132. DOI: 10.1037/0033-295X.114.1.104（PMID: 17227183）
- 逐語抜粋（verified, span 固定）: "This working memory limitation can be conceived of as arising from 2 components: a dynamic attention component (primary memory) and a probabilistic cue-dependent search component (secondary memory)."
- 主知見: 容量差を**一次記憶の動的注意＋二次記憶の制御的探索**の二成分に分解した。窓から溢れたものが再び取り出せるかは、手がかりに依存した探索の成否にかかっており、「残る／戻せる」は一様ではない。
- 主な限界: 既存データの理論的再解釈が中心で、新たな操作実験ではない。課題は実験室の記憶課題に限られる。

### 1.10 `MAT-20261127-2fceee` — McVay, Kane & Kwapil (2009)

- 出典: McVay, J. C., Kane, M. J., & Kwapil, T. R. (2009). Tracking the train of thought from the laboratory into everyday life: An experience-sampling study of mind wandering across controlled and ecological contexts. *Psychonomic Bulletin & Review, 16*(5), 857–863. DOI: 10.3758/PBR.16.5.857（PMID: 19815789／PMCID: PMC2760023）
- 逐語抜粋（verified, span 固定）: "Subjects rated their daily-life performance to be impaired when they reported off-task thoughts, with greatest impairment when subjects' mind wandering lacked metaconsciousness."
- 主知見: 実験室の迷走傾向は**日常の迷走報告を予測**する。しかも**メタ意識を欠いた迷走のときに**日常成績の障害が最も大きい。溢れた思考に気づけるかどうかが、自己報告としての「いまの自分」の質を決める。
- 主な限界: 自己報告ベースの相関設計で、大学生標本。成績障害は主観評価であり客観指標ではない。

## 2. 横断的読み

### 2.1 窓は測れ、その大きさは人ごとに違う

Luck & Vogel（約4対象）と Daneman & Carpenter（読みスパン2〜5）は、窓の大きさが**数として**測れることを示す。Engle らと Unsworth & Engle は、その数の正体を「妨害下で表象を活性に保つ力」と「手がかり探索の成否」に分解した。Just & Carpenter は、この幅が理解における**保留の幅**になることを示した。個別の思考と記憶のうち現在の自己に残る量は、万人一律ではなく、窓の大きさの関数として個人差を持つ。

### 2.2 窓の維持は注意の時間配分であり、離れるものから減る

Barrouillet の減衰モデルは、保持に注意が必要であり、**注意が切り替わった瞬間に痕跡が減る**ことを主張する。つまり人間の窓から溢れるとは、「いま注意が向いていないもの」が静かに失われることである。Lavie と de Fockert は、窓が埋まったときに何が起きるかを左右から確認した——知覚負荷なら邪魔者が入ってこず、作業記憶負荷なら邪魔者が侵入する。窓の**種類**が、溢れの**方向**を決める。

### 2.3 溢れは日常に現れ、気づきの有無で費用が変わる

Kane らと McVay らの経験サンプリングは、実験室で測った窓の差が、**日常の思考のオンタスク性**にそのまま現れることを示す。McVay らはさらに、溢れた思考に**メタ意識が及ばないときに**成績障害が最も大きいことを示した。「自分は逸脱した」と気づけぬ逸脱は、修正の入口を持たない。ここに、個別の思考と自己の関係の第一の結びつきがある——**現在の自己に残るのは、窓を通過し、かつ気づきの輪に入った思考だけ**である。

### 2.4 この軸がサブクエスチョンに加えるもの

個別の思考・記憶と自己の関係は、(a) 通過（窓を通過したものだけが現在の自己の素材になる）、(b) 保持（注意配分の維持だけが痕跡を保つ）、(c) 氾出（落ちたものは手がかり次第で戻れる／戻れない）、(d) 氾出の自覚（気づきの有無が自己報告の質を決める）という四層で記述できる。既存の他軸（帰属・内省・文脈・物語など）が主張する「残ったものの物語的統合」は、この四層の**上に**建っている。基盤が有限である以上、統合される素材は常に部分的であり、自己は窓の通過物の履歴として常に更新される。

## 3. 仮説への照合（`EVL-20261127-1dd71d`）

### 3.1 `HYP-20261119-63b6bf`（有限窓の二重通貨説）への効き

10資料は、63b6bf の射程条件「窓の大きさが測定可能であり、溢れの費用が観測可能な場合」を**人間側で充足**する。窓は数えられ（4対象、スパン2〜5）、溢れの費用は干渉増大・迷走・理解の失敗として観測される。Barrouillet の減衰は、人間側の通貨が**注意時間そのもの**であり、失われた痕跡の再獲得に新しい注意時間が必要であることを示し、63b6bf の「取り返せない時間」という記述と整合する。

しかし本資料群は**AI 側のトークン窓を一切測っていない**ため、63b6bf の主命題の残り半分——通貨の非対称性（人間＝不可逆な時間／AI＝可逆な圧縮）——は未検証のままである。評価行はこの限界を `no_recompute_reason` と summary に明記した。

### 3.2 `HYP-20261119-539a0c`（預け手の有限化）への効き

539a0c は**委託行為の様式**（有限予算下で委託が「要約して託す」へ変質する）を主題とする。本資料群は**個別認知の窓**を主題とし、委託・要約・責任の残留には直接触れない。したがって資料は 539a0c に反証も支持も与えない——対立軸としては間接的である。間接的な接点は一つある。Barrouillet の「注意が離れるものから減る」は、窓に収まらないものを要約して外に出すという 539a0c の圧力の**人間側の起源**を説明しうるが、本資料群だけでその接続を主張することはしない。

### 3.3 ペアとしての未決

割り当てられた検証ペアの期待情報利得は 0.0012 と既に小さい。本報告は 63b6bf の人間側の前提を裏付けたが、ペアを分ける決定打にはならなかった。ペアを実際に分けるには、(a) AI 側の窓と溢れ費用を直接測った資料、(b) 委託・要約・責任の様式を測った資料のいずれかが必要であり、`probe_search.py --coverage-gaps` の未消化質問（415件）にその候補が残っている。

## 4. 未達と限界

- **検証深度は abstract**。原典本文の全文通読はしていない。効果量・統計量の再計算は行っておらず、評価行に `no_recompute_reason` を記録した。
- Daneman & Carpenter (1980) は出版社ページを取得できず、二次提供の抄録の要約収蔵に留めた（`paraphrase_summary`）。
- 10資料の標本はほぼ大学生・健常成人・実験室課題であり、発達・加齢・臨床・文化横断への一般化は本報告の射程外である。
- 本資料群は自己・人格・エピソード記憶を直接測っておらず、「窓の通過」と「自己」の結びつきは本報告の推論（§2.4）として提示する。
- 期待情報利得が小さく、割り当てペアの分離には至らなかった（§3.3）。
- 文字混入の検証結果は §6 に記す。

## 5. 台帳への接続

本報告は ID で台帳に接続する（保存場所は書かない——書いたシャードは統合候補から外れる）。

- 資料10行: `MAT-20261127-075c12` `MAT-20261127-caea6c` `MAT-20261127-d52ceb` `MAT-20261127-22f133` `MAT-20261127-fa4b46` `MAT-20261127-217f86` `MAT-20261127-58c1fb` `MAT-20261127-97ade1` `MAT-20261127-be27ff` `MAT-20261127-2fceee`
- 読了10行: `READ-20261127-e00cc7` `READ-20261127-a46b65` `READ-20261127-155a44` `READ-20261127-1a083c` `READ-20261127-c56b4e` `READ-20261127-14de5b` `READ-20261127-a706fd` `READ-20261127-8ea635` `READ-20261127-20de85` `READ-20261127-754818`
- セッション1行: `SESSION-20261127-1c23c4`（人間委任の来歴、重複検査の経過、検証深度の限界を記録）
- ノート1行: `NOTE-20261127-4dc677`（本ファイルの登録行。claim 3件を Q-001／Q-002 に宛てた）
- 評価1行: `EVL-20261127-1dd71d`（`supports` / `cross_session_audit` / `agency_stance: report_only`）

## 6. 文字の検証

報告本文と本セッションで追加した全台帳行（資料10・読了10・セッション1・ノート1・評価1）に対し、日本語本文に混入しうる文字の走査を実施した。走査対象は、ハングル（U+1100–11FF／U+3130–318F／U+AC00–D7AF）、ディーヴァナーガリー（U+0900–097F）、キリル（U+0400–04FF）、アラブ（U+0600–06FF）、および「cp932 と euc_jis_2004 のいずれにもエンコードできない漢字」と、日本語として使わない中国語固有の機能語である。ギリシャ文字は数式・記号としてのみ許容する方針で、本報告に数式はないため出現即ノイズとみなす。

検出器の文字・語のリストは `scratch/` 配下のスクリプトにのみ存在させ、本報告には転記しない（過去に検出器語彙の転記が自己汚染を起こした教訓 `ERR-20261126-324b79` に従う）。

結果：

- 報告本文: 初回走査で中国語固有語の混入2箇所を検出し、日本語表現に修正。修正後の再走査は **0件**。
- 本セッション追加の全台帳行23件（資料10・読了10・セッション1・ノート1・評価1）: ハングル・ディーヴァナーガリー・キリル・アラブ・中国語固有漢字・中国語固有語すべて **0件**。追記途中に検出器で見つかった誤字1件（評価行）もコミット前に修正済み。
- 先行セッションの既存行に含まれる数式用のギリシャ文字（記号としての使用）は本セッションの追記対象ではなく、追記専用規約により変更しない。報告本文に数式はないため、本文中のギリシャ文字は即ノイズとみなして走査した。
