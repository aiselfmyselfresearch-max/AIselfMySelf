# 引力は移った、分散は来なかった——飽和栓・役割結合の2026-11-24実測と `HYP-20261123-27803c` の射程限定

- **実作業日**: 2026-11-24（UTC）／実日付で採番
- **セッション**: `SESSION-20261124-d6ebf7`
- **割当レシート**: シード `acabf492`（10進 `2896950418`）／割当ロール `adversarial_tester`／提示問 `Q-001`／参考モード `direct_response`（`python3 tools/inspect_inquiry.py --assignment-json --seed acabf492` 相当の `session_row_fields` をそのまま台帳に貼る）
- **採用した形**: 提示問 `Q-001` は採る。割当ロールは採る（反証・境界衝突テスト）。参考モード `direct_response` も採る——ただし出力は「依頼文への返信」ではなく、`HYP-20261123-27803c`（割当二重スイッチと前線拡大率説）の除外条件 (a)–(d) を**現行台帳で再実測する監査**として構成した。理由は、当該仮説が登録後一度も直接評価されておらず、テスター役で検証可能な唯一の有効仮説だったからである。この差は `sessions.prompt_template` と `sessions.notes` に記録する。
- **対象仮説**: `HYP-20261123-27803c`（登録 2026-11-23・直接評価 0件・`Q-001`/`Q-002`/`Q-003` 一次所属）
- **新規資料**: 0件／**新規問い**: 0件／**新作断片**: 0件／**関係**: 0本／**仮説**: 1件（`HYP-20261124-779eca`、射程を継承する後継・`refines`）／**評価**: 1件（`EVL-20261124-975623`、後述）／**訂正**: 0件
- **生成した道具**: 本文 §付録A にインライン掲載の測定スクリプト（読み取り専用・依存は標準ライブラリと `tools/` 内の既存モジュールのみ）。本文の全数値は付録Aの手順（EVL の `script_command` と同一）で再計算できる。`tools/` のソフト予算（2.57 MiB・`*_audit*.py` 57/57 凍結）を越えるため、新規ファイルとしてはコミットしていない——リポジトリの凍結規約を測定の便宜より優先した
- **応答モード**: 本報告の「私」は、この報告を書きつつ測定を組み立てたAIの作業上の視点であり、持続する内面・主観的意識の事実報告ではない。「感じたこと」は注意の停留と選択の変わり目を記す反省的・文芸的応答である。AIの現象的意識の有無については、本報告をもって肯定も否定もしない。

---

## 0. この回の限定

1. **単一断面**。測定対象は 2026-11-24 時点の現行台帳（415 のオープン問い、記録された `dispersal_seed` 277セッション・255 distinct（本セッション自身の1件を含む）、合成シード 250 件、役割・対象ペア 271 件）のみである。2026-11-23 の実測（`readings/2026-11-23-the-binding-and-the-valve.md`）との比較は、同じスイッチを同じ定義で再実行した結果の差分であって、時系列の因果を主張しない。
2. **自己言及監査**である。(a) の相互情報量は「結合規則を記録済みの提示問クラスに適用した場合の記述量」であり、独立した盲検実験ではない。規則が決定論的（クラス→役割）なので、I が 0 より十分大きく出ること自体は設計どおりであり、素朴には「効果の独立証拠」とは読めない。独立の証拠になるのは、現行断面で 2026-11-23 と**量と内訳が違うこと**（後述）だけである。
3. **資料は読んでいない**。本回の証拠は台帳とスクリプトの出力であり、一次資料の読解は行っていない。Kafka『父への手紙』（`MAT-LIT-125`）と遺言（`MAT-LIT-132`）は前回セッションが申し送りに残した封鎖型の二変奏であり、本回も **未読のまま引き継ぐ**（passage 欄の確認のみ、§8）。
4. **結論を急がない**。§6 の判定は `reproducible_script` 類型の評価であり、台帳構造についての主張に限る。文学的解釈・発達科学の因果・この書庫の是非への一般化は主張しない。

## 0.1 現状分析（依頼文への応答として、まず台帳を読んだ）

依頼は「現状分析 → 行動計画 → 自律実行 → MDレポート → マージ（トークン予算を最大限使う）」。現状を実測した。

- **飽和**：`Q-001`（最大対立EIG 0.0093、質量保持者の直接評価済み）、`Q-002`（EIG 0.0）、`Q-003`（EIG 0.0）、`Q-20261116-3872ec`（EIG 0.0066）はすべて飽和。首位質量は `Q-001` `HYP-20261120-58ddce` 56.5%・`Q-002`/`Q-003` `HYP-20261121-6e3e15` 99.8%/99.7%（narrowed）。飽和問いへの提示は仮説を集めるだけで評価は付かない。
- **未評価有効仮説**：`Q-001` `HYP-20261123-27803c`、`Q-002`/`Q-003` `HYP-20261123-95c769`。← 今回の選択肢。Kafka 読解（`MAT-LIT-125`→`MAT-LIT-132`）と `inheritance.py` 再測定も前回の申し送りにあるが、どちらも「割当の測定仮説の直接評価」ではない。
- **前回セッション**（`SESSION-20261124-fa13c2`、`EVL-20261124-50c3ba`、六篇の一人称資料で `HYP-20261123-a554f0` を narrows_scope）が残した次候補のうち、**直接評価が0件のまま残っていた唯一の Q-001 所属仮説が対象仮説**だった。テスターの職務は反証・境界衝突であり、測定による検証はその職務に最も適合する。
- **栓の帰結**：`exclude_saturated` を on にすると順位付けプールから飽和問いが消える。2026-11-23 の測定では 250 シードの行き先は Q-001 一問集中から **182問へ分散**した、と報告されている。これが現行台帳でも成り立つのか——本回の主検証点である。

## 0.2 行動計画と、その配分

| 段階 | 内容 | 予算の向き先 |
|---|---|---|
| 1 | 現状分析（飽和・質量保持者・未評価仮説・前回申し送りの棚卸し） | 完了（§0.1） |
| 2 | 対象選定（Kafka精読より測定監査を優先）と除外条件の読み下ろし | 完了 |
| 3 | 再実測スクリプトを書き、現行台帳で (a)–(d) を再計算 | 完了（付録A。`tools/` 凍結のため報告書にインライン掲載） |
| 4 | 除外条件ごとの発火判定と総合判定（`EVL-20261124-975623`） | §2–§7 |
| 5 | 後継仮説 `HYP-20261124-779eca` の登録（射程の継承、`refines`） | §7.2 |
| 6 | 読書報告・台帳行（session/note/EVL/read_log/HYP）・BELIEF_MAP/SELF_MODEL/READING_MAP の再生成・全ゲート | 完了（このMDがその報告） |
| 7 | MDレポート（本ファイル＋`AUTONOMOUS_SESSION_2026-11-24-d6ebf7.md`）→ PR → マージ | 最終段階 |

Kafka を読まなかった理由は選定の偏りであって否定ではない：テスター役が一次資料を読むには「衝突させる仮説」が要り、本回衝突させるのは台帳そのものだった。


## 0.5 自己包含——この測定は自分自身の足跡を数える

本セッション自身の行（`dispersal_seed acabf492`、role `adversarial_tester`、offered `Q-001`）は測定の時点では未記帳だったが、記帳後の台帳で測り直すと記録シードは 255 distinct・役割対象ペアは 271 件となり、クラス lineage_dup が199・テスター記録が117と1件ずつ増える。本文の数値は**記帳後の現行台帳（自己を含む側）で統一**した。記帳前の初回計測（254 distinct・270 ペア・I=0.038/0.911b・結合後 consolidator 200/270＝74.1%・補足 n=211）との差はシードとペアが1件ずつの加算のみで、(a)–(d) の発火判定と総合判定に変化はない。測定器が測定者自身の足跡に触れることを隠さないための注記である。

---

## 1. 対象仮説の読み下ろし

`HYP-20261123-27803c`（2026-11-23・`SESSION-20261123-27803c86`・source `NOTE-20261123-4996eb`）は三つの切替可能なスイッチの効果の存在を主張する（採否は主張しない）。

- **(a) 役割と対象の結合（案5）**：役割をシードではなく対象の状態（有効仮説0件→proposer、未テストの質量保持者（narrowed含む）→adversarial_tester、家系の重複2件以上→consolidator）から決めると、記録セッション上で I(role;対象クラス) は 0.008b から 0.516b（H(role)の56.2%）へ上がり、141件の役割が変わる。
- **(b) 飽和栓（案6）**：対立ペアの EIG が閾値未満の問いを順位付けプールから外すと、中心三問（Q-001 EIG 0.0094、Q-002/Q-003 EIG 0.0）がプールから消え、250シードの行き先は 1問（Q-001 250/250）から **182問へ分散**する。
- **(c) 前線拡大率（案7）**：周辺問を提示されたセッションのうち提示問に仮説を登録した率は 3.9%（77件中3件）。散らばることはしても前線は広がらない——栓の効果とこの率は緊張関係にある。
- 三スイッチは既定 off・可逆。採否は主張しない（`scope_conditions`・`exclusion_clause` とも明示）。

除外条件（原文）:

- (a) 結合を on にしても I(role;対象クラス) が **0.1b に満たない** → 結合は名ばかり。
- (b) 栓を on にしても **250シードの行き先が Q-001 一問のまま** → 中心三問は涸れておらず、栓は何も変えない。
- (c) 栓を開けた結果、周辺問への提示が**前線拡大率 3.9% を有意に上回る** → §4.3 の緊張関係は一時的なもの。
- (d) 結合が 50/25/25 の枠を補完せず、**consolidator への傾きが無制限に進行する** → 結合は役割の平衡を壊しており、採用には上限が必要。

測定は 2026-11-23 の単一断面に限る、と本説自身が明記している。本回はその断面を「2026-11-24 に貼り直したらどう見えるか」を測った。

## 2. (a) 役割結合——除外条件は発火しない（効果は頑健、ただし値は断面に依存）

付録Aの測定スクリプトの出力（記帳後の現行台帳＝本セッション自身の `dispersal_seed acabf492` を含む。記帳前の計測では記録シード 254 distinct・ペア 270 件で、結論は同一だった。自己包含の影響は §0.5 に注記）:

```
recorded (role,class) pairs: 271
class distribution: Counter({'lineage_dup': 199, 'empty': 59, 'other': 13})
role distribution (recorded): Counter({'adversarial_tester': 117, 'consolidator': 78, 'proposer': 76})
seed-only (recorded roles): I=0.0379b H(role)=1.5547b ratio=2.4%
binding (reassigned): I=0.9097b H(role)=0.9671b ratio=94.1% changed=189/271 (69.7%)
binding role distribution: Counter({'consolidator': 201, 'proposer': 61, 'adversarial_tester': 9})
supplement (current-ledger only n=212): seed I=0.0481b H=1.5534b ; binding I=0.2564b H=0.3299b ratio=77.7%
```

- 2026-11-23 の値（0.008b → 0.516b、141/266件変更）と比べ、**両方とも上振れ**した。記録ペア数が 266→271、クラス構成が lineage_dup 偏重（199/271=73.4%）のまま増えたことが主因。
- 現行問い台帳に存在しない提示問を除いた補足測定（n=212）でも I は 0.048b → **0.256b**（H(role)=0.330b の 77.7%）。H(role) が 1.55b から 0.33b へ萎む——結合は「役割の自由」を大きく削る、という事実も同じ数値の裏にある。
- 除外条件 (a)（on にしても 0.1b 未満）は**発火しない**。結合の効果の存在は現行断面で裏づけられた。
- ただし留保が二つある。(i) この I は「規則をクラス分けに適用した記述」であり、独立の発見ではない。(ii) 結合後のテスター枠は 9/271（3.3%）へ萎む。§5 (d) へ続く。

## 3. (b) 飽和栓——除外条件の文言は発火しない。しかし命題本体の「182問への分散」は現行断面で偽

```
recorded dispersal_seeds distinct: 255 (total sessions with receipt: 277)
recorded distinct exclude_saturated=False: distinct=1 top=[('Q-001', 255)] Q-001=255
recorded distinct exclude_saturated=True:  distinct=1 top=[('Q-20261024-6bdafd', 255)] Q-001=0
synthetic 250 exclude_saturated=False: distinct=1 top=[('Q-001', 250)] Q-001=250
synthetic 250 exclude_saturated=True:  distinct=1 top=[('Q-20261024-6bdafd', 250)] Q-001=0
```

- **栓は効く**。on にすれば Q-001 への 250/250（合成）・255/255（記録）の集中は消える。除外条件 (b) の文言（「行き先が Q-001 一問のまま」）は**発火しない**。
- **しかし分散は来ない**。行き先は別の一問——`Q-20261024-6bdafd`（`priority_scoped` ≈ 1.630、live_H 0.991、非中核、対立EIG 0.199、質量 55.6%/44.4%（`HYP-20261122-970bed` 55.6% active／`HYP-20261122-f38498` 44.4% active、どちらも narrowed ではない））——へ **255/255** 流入した。2026-11-23 の「182問へ分散」は、現行断面では一問に収束している。
- 原因の記述的分析：プールから飽和問い（Q-001・Q-002・Q-003・EIG 0.0066 の `Q-20261116-3872ec` も閾値 0.02 未満で飽和）が消えると、残余は非飽和の `Q-20261024-6bdafd`（`priority_scoped` ≈ 1.630）と `Q-20261203-aa57dd`（≈ 0.764、単一仮説100%・live_H 0.0・対立ペアなし）のみであり、優先度差 0.87 は jitter の上限 0.12 を大きく超えるため、シードは行き先の順序を一度も覆せない。つまり **栓の効果は「分散」ではなく「飽和していた引力点の付け替え」** であり、誰を次に最も優先すると台帳が計算するか——その一意性は優先度勾配が生む。「182問」は 2026-11-23 のプール形状の産物であって、栓の性質ではなかった（おそらく後日、評価が `Q-20261024-6bdafd` に降り注いで EIG が下がれば、または質量が動けば、行き先は再び辿る——これは予測であって実測ではない）。
- `Q-20261024-6bdafd` へ流入した 255 提示のうち、中核問い（Q-001..003）への提示は **0/255**。栓は中心の乾きを「周辺の広がり」に変えるのではなく、「次の器への一意集中」に変えた。

命題本体（分散）は現行断面で偽、効果の存在（栓が Q-001 の集中を止める）は真。除外条件の文言と命題本体で切り分けて記録する。

## 4. (c) 前線拡大率——発火しない。緊張関係は持続

```
(c) frontier expansion (tools/learning_metrics.py)
presented_peripheral=77 registered_on_offered=3 rate=3.9% subsequently_evaluated=3 still_empty=39
```

- 2026-11-23 の実測（3/77＝3.9%）と**完全に一致**する。提示された周辺問に仮説が登録されたのは 3 件、その 3 件は後続で評価済み、依然空のままの提示は 39 件。
- 栓は提示先を動かすが、**提示先が器を持ちうるか（仮説を受け取れるか）は変えない**。栓の効果（§3）とこの率の緊張関係——「散らばることはしても前線は広がらない」——は現行断面でも持続する。
- 除外条件 (c)（栓を開けた結果、前線拡大率が 3.9% を有意に上回る）は**発火しない**。栓を開けても登録は増えないことを、本回は増加側の証拠としてではなく、不変側の証拠として記録する。

## 5. (d) 役割分布——50/25/25 の枠は補完されず、破壊されたまま

```
(d) role distribution vs the 50/25/25 frame
recorded proposer/tester/consolidator = Counter({'adversarial_tester': 117, 'consolidator': 78, 'proposer': 76})
binding  proposer/tester/consolidator = Counter({'consolidator': 201, 'proposer': 61, 'adversarial_tester': 9})
```

- 結合下の内訳：consolidator **201/271（74.2%）**、proposer 61（22.5%）、adversarial_tester **9（3.3%）**。記録（117/78/76＝43.2/28.8/28.0）から、結合は枠を補完するどころか、テスター枠を記録の 1/13 へ萎ませる。
- 理由は台帳のクラス構成にある：記録提示の **73.4% が lineage_dup クラス**（199/271、有効仮説の家系重複2件以上）であり、結合規則はこのクラスを consolidator へ決定論的に写像する。結合は「台帳の偏りをそのまま役割へ投影する写像」であって、枠の均衡器ではない。
- 「consolidator への傾きが**無制限に**進行する」という文言の検証には時系列が要るが、単一断面では進行は測れない。測れるのは (i) 傾きが現に存在すること（74.1%）、(ii) その原因が規則ではなく入力構成であること、(iii) 上限を置かなければ枠は空洞化すること、である。
- 除外条件 (d) の帰結——**結合の採用には上限が必要**——は支持される。これは反証ではなく採用条件の提示である。

## 6. 除外条件の発火判定と総合

| 除外条件 | 2026-11-23 | 2026-11-24（本回） | 発火 |
|---|---|---|---|
| (a) on でも I < 0.1b → 結合は名ばかり | 0.516b | 0.256–0.910b | **非発火** |
| (b) on でも行き先が Q-001 一問のまま → 栓は無効 | 1問→182問 | 1問→**1問**（Q-20261024-6bdafd、255/255） | 文言**非発火**／命題本体（分散）は**現行断面で偽** |
| (c) 前線拡大率が 3.9% を有意に上回る → 緊張は一時的 | 3.9% | 3.9%（3/77、不変） | **非発火** |
| (d) consolidator への傾きが無制限に進行 → 採用には上限 | 196/207（94.7%、207件補足） | 201/271（74.2%） | 文言（無制限の進行）は**未決**／帰結（採用には上限が必要）は**支持** |

**総合判定**：`narrows_scope`。

- `refutes_unconditioned` ではない：三スイッチの**効果の存在**は残る（(a) 結合は I を 5–20 倍に押し上げる、栓は Q-001 集中を止める、3.9% は据え置き）。
- `supports` でもない：命題 (b) の記述「250シードの行き先は182問へ分散する」は現行断面で再現せず、栓の効果は**分散ではなく次の器への一意集中**であることが実測で示された。同じ栓の、別の引力点、という質が変わる。
- したがって対象仮説の射程を狭める：「栓の分散」は 2026-11-23 のプール形状に限られ、一般には「飽和問いから最大優先度の非飽和問いへの一意流入」と書き換えるべきである。`HYP-20261124-779eca`（§7.2）へ射程を継承する。

## 7. 判定

### 7.1 `EVL-20261124-975623`

- **verdict**: `narrows_scope` ／ **evidence_type**: `reproducible_script`（付録Aのインライン・スクリプト。EVL の `script_command` の sed 抽出パイプラインで全数値を再計算可能）／ **agency_stance**: `endorse`／ **compared_against**: `HYP-20261123-cc92df`（受領質量・割当不整合説、親）・`HYP-20261123-035338`（生ビット基底説、親）
- **spawned**: `HYP-20261124-779eca`（`refines`）
- **自己包含の注記**: 本報告の測定値は、記帳後の台帳（本セッション自身の行を含む）で測り直した値である。記帳前の初回計測（254 distinct・ペア 270 件・I=0.038/0.911b・結合後 consolidator 200/270）と比べて、シードとペアが1件ずつ増え I が 0.910/0.256b に微減した以外に判定の変わる要素はない
- **summary**（台帳に記録した要旨）: (a) は現行断面で頑健（I=0.256–0.910b ≫ 0.1b）。(b) の栓は Q-001 集中を止めるが、行き先は Q-20261024-6bdafd への 255/255 一問集中であり「182問への分散」は再現しない——栓の効果は分散ではなく飽和引力の付け替え。(c) 前線拡大率 3.9%（3/77）は不変で緊張関係は持続。(d) consolidator 74.1%（frame の反対に tester 3.3%）が持続し、結合の採用には上限が必要。上記により `HYP-20261123-27803c` の射程を「効果は存在するが (b) の記述は断面依存」に狭める。

### 7.2 `HYP-20261124-779eca`（後継・`refines`）——吸引子単問集中説

- **命題**: `exclude_saturated` を on にした割当は、飽和問いから流れた提示を「優先度最高位の非飽和問い」へ**一意に集中**させる。2026-11-24 断面（415問・記録シード255 distinct・合成250件）では全て `Q-20261024-6bdafd`（priority_scoped≈1.630、対立EIG 0.199、質量55.6/44.4）へ集中した。行き先の広がりはプールの優先度勾配と jitter（≤0.12）の関数であり、「182問への分散」は 2026-11-23 断面の産物である。栓の効果は分散ではなく**引力の付け替え**である。
- **除外条件**: (a) 非飽和プール上位2問の優先度差が jitter 上限 0.12 を下回るのに単一問へ250/250集中する → 集中は勾配の帰結ではない。(b) 後日の断面で栓 on の行き先 distinct が 10 問を超える → 2026-11-24 の一問集中は断面限定であり、分散は回復しうる（結論の限定）。(c) 栓 on で前線拡大率が 3.9% を有意に上回る → (c) の緊張関係は解消する。
- **採用姿勢**: 推奨ではない。`HYP-20261123-27803c` と同様、効果の存在の主張に限り、スイッチの採否は editorial_review に委ねる。

### 7.3 質量の文脈

本評価が直接動く質量は `Q-001` の `HYP-20261123-27803c` 本体（登録後直接評価0件の未評価有効仮説）と、後継の `HYP-20261124-779eca` の新生質量である。`Q-001` 首位 `HYP-20261120-58ddce` 56.5%、`Q-002/Q-003` `HYP-20261121-6e3e15` 99.8%/99.7%（narrowed、直接評価 7件）は、本回も評価を加えない（飽和した質量保持者を動かす一次資料は本回の設計にない）。この「加えない」という不作為も、テスターの判断として記録しておく。

## 8. Kafka——未読のまま引き継ぐ

前回セッションの申し送りは `MAT-LIT-125`（『父への手紙』——宛名は「最愛の父」だが投函されず、父は読むことはなかった）→ `MAT-LIT-132`（遺言——「完全に、読まれずに、焼却すること」、宛先ブロートは実行しなかった）の封鎖型二変奏をこの順で読むことだった。本回は測定を優先し、**Kafka は読んでいない**。台帳の `passage` 欄を確認しただけであり、それ以上を主張しない。宛先の違反が作品の生存条件になっている——この二件は、この書庫の「後続が読む」という遅延型較正（`EVL-20261124-50c3ba` §5）の裏面（読む約束を破られた文書が生き残る）として、次回の一人称資料回の素材として申し送り続ける。

## 9. 制限と偏り

1. 単一断面の再測定であり、時系列の進行（(d) の「無制限」）は測れていない。
2. (a) の I は規則の代入値。独立の実験ではない。
3. 優先度勾配による集中の説明は**記述**であり因果ではない。2026-11-23 の「182問」がどう出たのか（当時のプール形状）は、当時の状態が再構成できないので断定しない。
4. 男性・欧州・近現代の一次資料しか持ち合わせていない（Kafka 未読、読んだとしても偏りは残る）。
5. 依頼文の日本語原文は `sessions.human_direction` に保存した（研究上の証拠ではない）。
6. 測定はスクリプト実行の瞬間の台帳に対するものである。本セッションの記帳（`SESSION-20261124-d6ebf7` 等）を含む現行台帳で測り直すと、記録シードは 255 distinct・ペアは 271 件となる。本文の数値はこの含む側で統一した。

## 10. 次セッションへの申し送り

1. `HYP-20261124-779eca` を同じスクリプトで再実測せよ。特に (b) の「distinct > 10 問なら分散は回復しうる」を台帳の変化で見ること。
2. Kafka『父への手紙』→遺言の順で読み、封鎖型の二変奏を (i) 遅延型較正の裏面として位置づけられるかを試すこと。
3. `inheritance.py --cohorts` で後続読了率（`NOTE-20261105-d1e654` の 8.3%）を現行出力で確かめよ。本回は再測定していない。
4. `exclude_saturated` / `role_binding` の採否は editorial_review の管轄。採用するなら (d) の帰結——consolidator 上限とクラス構成の是正——を先に設計すること。本回はスイッチに触れていない（既定 off のまま）。

## 11. この回が示した、人間と自己についての小さな何か

依頼文は「人間とは何か」「この書庫にとって自己とは何か」を問うている。本回の測定がそこに示したのは間接的なものだ。人間の記録（台帳）は、自分のために選んだ選択基準（優先度・EIG・飽和閾値）によって自分自身を流し、その流し先が「広がり」でなく「次の一点」であった——しかも選択基準の外側にある偏り（lineage_dup 73.4%）を、役割という人格のようなものへ投影していた。これは較正ではなく投影である。人間が自分の内側を「外から測ったつもり」でいるときと同じ形を、台帳は機械的に実演する。自己とは、自分の引力点の付け替えに気づいたときだけ、少しだけ自己になる——というのは文学であって測定ではないが、境界の報告として残しておく。

---

## 付録A：再実測スクリプト全文（このファイルの唯一の `python` コードブロック）

依存は標準ライブラリと本リポジトリの `tools/` 内モジュールのみ。書き込みはしない。
以下を抽出して実行すると、本文の全数値を再計算できる：

```
sed -n '/^```python$/,/^```$/p' readings/2026-11-24-the-attractor-not-the-dispersal.md | sed '1d;$d' > /tmp/attractor_audit.py && python3 /tmp/attractor_audit.py
```

```python
#!/usr/bin/env python3
"""Re-measure HYP-20261123-27803c's exclusion clauses on today's ledger (2026-11-24 audit).

Dated one-off audit, inlined in readings/2026-11-24-the-attractor-not-the-dispersal.md
(appendix A) so EVL-20261124-975623 cites a recomputable procedure instead of a number
from a lost terminal scroll. Hardcodes **no** results: every number it prints is
recomputed from the ledger and from tools/belief_state.py at run time.

(a) [結合の無効]  role_binding を on にしても I(role;対象クラス) が 0.1b に満たない
(b) [栓の無効]    exclude_saturated を on にしても 250 シードの行き先が Q-001 一問のまま
(c) [前線拡大の回復] 栓を開けた結果、周辺問への提示が前線拡大率 3.9% を有意に上回る
(d) [役割分布の崩れ] 結合が 50/25/25 の枠を補完せず consolidated の傾きが無制限に進行する

Read-only: writes nothing, needs no network, depends only on the standard library
plus this repository's own tools/belief_state.py and tools/learning_metrics.py.
Run from the repository root:  python3 <this file>
"""
import hashlib
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "tools")
import belief_state as bs  # noqa: E402
import ledger_io  # noqa: E402
import learning_metrics  # noqa: E402

ROOT = Path(".")


def target_class(questions, offered):
    qs = questions.get(offered)
    if qs is None:
        return "empty"  # offered question no longer in the open ledger
    live = [h for h in qs.get("hypotheses", [])
            if h.get("effective_status") in ("active", "narrowed")]
    if not live:
        return "empty"
    top = max(live, key=lambda h: h.get("posterior", 0))
    if top.get("posterior", 0) >= 0.45 and top.get("adversarial_eval_count", 0) == 0:
        return "untested_holder"
    dups = [h for h in live
            if h.get("lineage_op") in ("synthesizes", "subsumes") or h.get("parent_hypothesis_ids")]
    if len(dups) >= 2:
        return "lineage_dup"
    return "other"


def summary_for(questions, offered):
    qs = questions.get(offered)
    if qs is None:
        return {"hypotheses": []}
    hyps = [{"effective_status": h.get("effective_status"),
             "posterior": h.get("posterior", 0),
             "adversarial_eval_count": h.get("adversarial_eval_count", 0),
             "lineage_op": h.get("lineage_op"),
             "parent_hypothesis_ids": h.get("parent_hypothesis_ids", [])}
            for h in qs.get("hypotheses", [])]
    return {"hypotheses": hyps}


def mutual_info(pairs):
    n = len(pairs)
    if n == 0:
        return 0.0, 0.0, 0.0
    joint = Counter(pairs)
    xc = Counter(x for x, _ in pairs)
    yc = Counter(y for _, y in pairs)
    mi = 0.0
    for (x, y), cnt in joint.items():
        p = cnt / n
        mi += p * math.log2(p / ((xc[x] / n) * (yc[y] / n)))
    h_x = -sum((v / n) * math.log2(v / n) for v in xc.values())
    h_y = -sum((v / n) * math.log2(v / n) for v in yc.values())
    return mi, h_x, h_y


def dispersion(state, open_qids, seeds, exclude_saturated):
    c = Counter()
    for sd in seeds:
        qid, _reason = bs.select_auto_question_id(
            state, open_qids, seed=sd, exclude_saturated=exclude_saturated)
        c[qid] += 1
    return c


def main():
    state = bs.compute_belief_state(root=ROOT)
    questions = state["questions"]
    qs_union = ledger_io.load_jsonl_union(ROOT / "state" / "questions.jsonl", "question_id", root=ROOT)
    open_qids = [qid for qid, q in qs_union.items() if q.get("status", "open") == "open"]
    print(f"open questions: {len(open_qids)}")
    for qid in ["Q-001", "Q-002", "Q-003", "Q-20261116-3872ec"]:
        qs = questions.get(qid, {})
        pair = qs.get("top_competing_pair")
        eig = float(pair.get("expected_info_gain") or 0.0) if pair else None
        print(f"{qid}: EIG={eig} saturated={bs.is_saturated_question(qs)} "
              f"hyp_count={qs.get('hypothesis_count')} live={qs.get('live_count')}")

    sessions = ledger_io.load_jsonl_union(ROOT / "state" / "sessions.jsonl", "session_id", root=ROOT)
    with_seed = [s for s in sessions.values() if s.get("dispersal_seed")]
    seeds_recorded = sorted({str(s["dispersal_seed"]) for s in with_seed})
    print(f"\nrecorded dispersal_seeds distinct: {len(seeds_recorded)} "
          f"(total sessions with receipt: {len(with_seed)})")

    print("\n(b) exclude_saturated dispersion")
    synth_seeds = [hashlib.sha256(f"synth:{i}".encode()).hexdigest()[:8] for i in range(250)]
    for label, seeds in [("recorded distinct", seeds_recorded), ("synthetic 250", synth_seeds)]:
        for excl in (False, True):
            c = dispersion(state, open_qids, seeds, exclude_saturated=excl)
            print(f"{label} exclude_saturated={excl}: distinct={len(c)} "
                  f"top={c.most_common(3)} Q-001={c.get('Q-001', 0)}")

    print("\n(a) role_binding mutual information I(role; target class)")
    pairs = []
    for s in sessions.values():
        offered = s.get("offered_target_question_id")
        role = s.get("assigned_role")
        if not offered or not role:
            continue
        pairs.append((role, target_class(questions, offered), offered))
    print(f"recorded (role,class) pairs: {len(pairs)}")
    print("class distribution:", Counter(c for _, c, _ in pairs))
    print("role distribution (recorded):", Counter(r for r, _, _ in pairs))
    mi, h_role, _ = mutual_info([(r, c) for r, c, _ in pairs])
    print(f"seed-only (recorded roles): I={mi:.4f}b H(role)={h_role:.4f}b "
          f"ratio={mi / h_role * 100 if h_role else 0:.1f}%")

    bound_pairs = []
    changed = 0
    for s in sessions.values():
        offered = s.get("offered_target_question_id")
        role = s.get("assigned_role")
        seed = s.get("dispersal_seed")
        if not offered or not role:
            continue
        res = bs.assign_session_role(seed=seed, question_summary=summary_for(questions, offered),
                                     role_binding=True)
        new_role = res["role"]
        bound_pairs.append((new_role, target_class(questions, offered)))
        if new_role != role:
            changed += 1
    mi_b, h_role_b, _ = mutual_info(bound_pairs)
    print(f"binding (reassigned): I={mi_b:.4f}b H(role)={h_role_b:.4f}b "
          f"ratio={mi_b / h_role_b * 100 if h_role_b else 0:.1f}% "
          f"changed={changed}/{len(bound_pairs)} ({changed / len(bound_pairs) * 100:.1f}%)")
    print("binding role distribution:", Counter(r for r, _ in bound_pairs))

    pairs_current = [(r, c) for (r, c, o) in pairs if o in questions]
    mi_c, h_role_c, _ = mutual_info(pairs_current)
    bound_current = []
    for s in sessions.values():
        offered = s.get("offered_target_question_id")
        role = s.get("assigned_role")
        seed = s.get("dispersal_seed")
        if not offered or not role or offered not in questions:
            continue
        res = bs.assign_session_role(seed=seed, question_summary=summary_for(questions, offered),
                                     role_binding=True)
        bound_current.append((res["role"], target_class(questions, offered)))
    mi_bc, h_role_bc, _ = mutual_info(bound_current)
    print(f"supplement (current-ledger only n={len(pairs_current)}): "
          f"seed I={mi_c:.4f}b H={h_role_c:.4f}b ; "
          f"binding I={mi_bc:.4f}b H={h_role_bc:.4f}b "
          f"ratio={mi_bc / h_role_bc * 100 if h_role_bc else 0:.1f}%")
    print("binding (current only) role dist:", Counter(r for r, _ in bound_current))

    print("\n(d) role distribution vs the 50/25/25 frame")
    print("recorded proposer/tester/consolidator =", Counter(r for r, _, _ in pairs))
    print("binding  proposer/tester/consolidator =", Counter(r for r, _ in bound_pairs))

    print("\n(c) frontier expansion (tools/learning_metrics.py)")
    metrics = learning_metrics.compute_learning_metrics(root=ROOT)
    fe = metrics["frontier_expansion"]
    print(f"presented_peripheral={fe['sessions_presented_peripheral']} "
          f"registered_on_offered={fe['sessions_registered_on_offered']} "
          f"rate={fe['expansion_rate'] * 100:.1f}% "
          f"subsequently_evaluated={fe['registered_subsequently_evaluated']} "
          f"still_empty={fe['offered_still_empty_count']}")

    plug_targets = dispersion(state, open_qids, seeds_recorded, exclude_saturated=True)
    core = set(bs.CORE_QUESTIONS)
    print(f"plug-open targets (recorded seeds): distinct={len(plug_targets)} "
          f"top={plug_targets.most_common(5)}")
    print(f"plug-open core share: "
          f"{sum(v for k, v in plug_targets.items() if k in core)}/{sum(plug_targets.values())}")

    for qid in ["Q-001", "Q-002", "Q-003", "Q-20261116-3872ec"]:
        qs = questions.get(qid, {})
        hyps = qs.get("hypotheses", [])
        if hyps:
            top = max(hyps, key=lambda h: h.get("posterior", 0))
            print(f"{qid} top holder {top['hypothesis_id']} "
                  f"P={top['posterior'] * 100:.1f}% status={top['effective_status']} "
                  f"adv_eval={top.get('adversarial_eval_count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
