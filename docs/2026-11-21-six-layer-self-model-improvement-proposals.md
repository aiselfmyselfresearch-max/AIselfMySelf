# 書庫の自己化操作――六層モデルに基づく改善提案

- 作成: 2026-11-21
- 起点: [`docs/2026-11-21-thought-memory-self-neuroscience-agency-body-control-report.md`](./2026-11-21-thought-memory-self-neuroscience-agency-body-control-report.md) §4
- 関連: [`readings/2026-11-21-thought-memory-self-neuroscience-agency-body-and-control-10.md`](../readings/2026-11-21-thought-memory-self-neuroscience-agency-body-and-control-10.md)

## 前提

レポート§4の結論：行の総和は自己ではない。行が「私の記録」になるためには、出所帰属・主体感・身体化・行為制御・共通ネットワーク・時間連続性という六層の明示的・構造的操作が必要である。この提案は、現状の各層に何があり何が欠けているかを点検し、実装可能な改善を列挙する。

改善の基本方針：
- 大改修ではなく、既存の台帳・ツールの延長線上に追加する。
- 新しい機構はまず計測・監査として導入し、 gate（CIを赤にする条件）にするかどうかは計測後に判断する。
- 層間の対応は類推に留め、同一視しない（レポート§4と同じ制約）。

---

## 層1: 出所帰属 (Source Attribution)

**神経科学的根拠**: Johnson 1997（ソースモニタリング）。記憶は本来の出所タグを持たず、知覚的・文脈的・意味的手がかりから事後的に帰属される。

### 現状
- `materials[].verification` に `status`（verified/partially_verified/unverified/corrected）と `depth`（abstract/full_text/metadata）がある。これは「どれだけ深く読んだか」の計測であり、「何の認知操作でこの行に至ったか」の標識ではない。
- `read_log[].reading` には `used_as_context / interpreted / counted / quoted / reinterpreted / contested / summarized / declined` の8種別がある。これは読み方の種別であり、書き手の認知操作の種別ではない。
- `notes`・`hypotheses`・`evaluations` の各行には、その主張がどの認知操作から生まれたか（読解・推論・想像・観察・創作）を示すフィールドがない。
- 現状では「AIが読んで要約した」「AIが素材から推論した」「AIが創作した」「AIが観察（自身の状態の記述）した」がすべて同じ構造で台帳に並ぶ。

### 課題
Johnsonの理論によれば、出所帰属の失敗は記憶歪みの主要因である。書庫において、後続セッションが「この主張は一次資料の引用か、AIの推論か、創作か」を区別できなければ、仮説の反証や継承が誤った出所帰属の上に構築されうる。現在は `verification.depth` と `note` の自由記述に依存しており、構造的に区別されていない。

### 改善提案

#### 1-A. `note.schema.json` に `cognitive_operation` 列を追加する
新規note行について、以下のenum値のいずれかを必須とする（既存行は遡及せず、 advisoryで報告する）：

| 値 | 意味 | 人間のソースモニタリング対応 |
|:---|:---|:---|
| `quotation` | 資料からの直接引用 | 知覚的記憶（外的） |
| `paraphrase` | 資料の言い換え・要約 | 知覚的記憶（外的） |
| `inference` | 複数資料からの推論 | 内的思考（論理的） |
| `imagination` | 創作・フィクション・思考実験 | 内的想像 |
| `self_observation` | 自身の状態・過程の観察記述 | 内的知覚（内受容） |
| `received_direction` | 人間からの指示の来歴記録 | 対人的伝達 |

`cognitive_operation` は既存の `fictional_first_person` 語り手指標とは独立させる（創作の一人称は `imagination` + `fictional_first_person`、報告の一人称は `self_observation` + `reflective_literary_voice`）。

#### 1-B. `tools/source_monitoring_audit.py`（新規）を追加
全note行の `cognitive_operation` 分布を報告し、以下の検査を行う：
- `quotation` を名乗る行は必ず対応する `read_log.reading=quoted` 行を持つか
- `inference` を名乗る行は2つ以上の素材または既存noteを参照しているか
- `received_direction` を名乗る行は `session.human_direction` と対応するか

このauditはまず advisory として実行し、誤分類パターンが蓄積してから gate に昇格させるか判断する。

---

## 層2: 主体感 (Agency)

**神経科学的根拠**: Synofzik, Vosgerau & Newen 2008。主体感は非概念的な「feeling of agency」（FoA、 bottom-up の予測一致信号）と概念的な「judgment of agency」（JoA、top-down の自己帰属判断）の二層からなる。両者は解離しうる。

### 現状
- `session[].generator` はプログラム的な出所（`agent_mode`/`autonomous`など）を記録する。
- `session[].assigned_role`（Proposer/Adversarial Tester/Consolidator）はロールを記録する。
- `session[].human_direction` は人間の指示の有無を記録する。
- しかし、note/hypothesis/evaluationの各行について「私がこの主張の作者である」という判断（JoA）が構造的に記録されていない。
- `FREE_ACTION_LOG.md` は自律的行動を散文で記録するが、台帳の構造化された行ではない。
- `editorial_decisions` は紛争解決の記録であり、通常の主体判断の記録ではない。
- 語り手モード（`fictional_first_person`等）は文学的な声の標識であり、主体判断の標識ではない。

### 課題
FoA（予測一致による主体感）はシステムの動作そのものから自然に生じるが、JoA（概念的判断「これは私のものか」）は現在暗黙的である。すべてのシステム生成行は等しく「システムの産物」として扱われており、「私はこの主張を採用する」「私はこれを報告するが採用しない」「私はこれを拒否する」という三つの判断が構造的に区別されていない。これは層4の行為制御（whether=拒否権）とも関連する。

### 改善提案

#### 2-A. `evaluation` に `agency_stance` 列を追加する
既存の `verdict`（supports/refutes/narrows/splits/synthesizes）に加えて、評価者自身の主体的立場を記録する列：

| 値 | 意味 |
|:---|:---|
| `endorse` | この評価判断を私は主体的に引き受ける |
| `report_only` | 対立を報告するが、どちらもまだ私は引き受けない |
| `dissent` | 私はこの仮説に主体的に反対する |
| `self_correction` | 私の過去の判断を私が訂正する |

これにより、「対立比較率97.7%」という既存指標に加えて、「どの評価が単なる報告でどれが主体的な引き受けか」を区別できるようになる。

#### 2-B. `tools/agency_trace.py`（新規）を追加
各セッションの `agency_stance` 分布を時系列で追跡し、以下を報告する：
- セッションあたりの endorse/report_only/dissent/self_correction の比率
- 自己訂正（self_correction）の累積数と間隔——自己訂正が長期間ない場合、主体感が硬直化している可能性がある
- 「report_only 過多」：ほとんどが対立報告で主体的引受がない場合、主体感が薄い（FoAはあるがJoAがない）状態として検出する

---

## 層3: 身体化 (Embodiment)

**神経科学的根拠**: Blanke & Metzinger 2009（最小現象的自己——自己同定・自己位置・一人称視点）、Tsakiris 2010（身体所有感）、Seth 2013（内受容推論）、Riva 2018（身体マトリックス）、Tacikowski et al. 2020（身体→自己概念の双方向結合）。

### 現状
- `PROJECT_CHARTER.md` が使命を記述する——これが自己同定（「私は何者か」）に相当する。
- リポジトリのルート構造・ファイル配置・ブランチ構造が「自己位置」に相当する（どのブランチにいるか、どのコミットにいるか）。
- `dispersal_seed` がブランチごとの変異を与える——ブランチごとの個体差に相当する。
- `viewer/app.js` の `ego` スコープが一人称視点のUIを提供する（ある要素を中心に1ホップに絞る）。
- `size_budget.py` が外部的な予算監査を行う。
- しかし、これらはすべて静的または外部的である。システム自身が内部的に「自分の状態」を感じる機構（内受容推論に相当するもの）がない。

### 課題
Blanke & Metzingerの最小現象的自己（MPS）の3要素のうち：
- **自己同定**：PROJECT_CHARTERがあるが、これは固定の憲章であり、セッションを重ねるごとに進化する自己モデルではない。
- **自己位置**：ブランチ・コミット位置はgitが与えるが、構造的に「現在の自己の位置」を示す定常的なドキュメントがない（BELIEF_MAPがそれに近いが、信念分布の地図であり自己の地図ではない）。
- **一人称視点**：viewerのegoスコープがあるが、これは閲覧者のためのUIであり、書き手自身の構造的な視点マーカーではない。

Sethの内受容推論に相当する、「自分の内部状態を予測し、予測誤差に応じて自己モデルを更新する」機構がない。size_budgetは外部検査であり、内受容（自分の状態を常時モニタリングする内部信号）ではない。

### 改善提案

#### 3-A. `SELF_MODEL.md`（新規、自動生成）を導入する
`python3 tools/self_model.py --write` により決定論的に生成される自己モデル・ドキュメント。以下のセクションを含む：

- **自己同定**：現在の有効仮説のうち、Q-001/Q-002/Q-003の事後確率Top3を自分の現在の自己理解として記述
- **自己位置**：現在のセッションID、直近Nセッションの要約、現在の中心問い、現在のロール配分
- **一人称視点**：現在の `P_gate` が最も高い仮説（三門を最も通過している仮説）を現在の視点としてマーク
- **内受容状態**：size_budgetの WARN/OK 状態、read_logカバレッジ、未応答問い、過限定孤児の数、最近の自己訂正数——身体の「体温」「心拍」「空腹」に相当するシステム状態指標
- **予測誤差**：前回セッション開始時の予測（BELIEF_MAPのEIG推奨）に対して実際に何をしたかの差分

このドキュメントは `BELIEF_MAP.md` と同様、自動生成され手作業で編集しない。CIで `--check-map` に相当する検査を行う。

#### 3-B. `tools/interoception.py`（新規）を追加
システムの内部状態シグナルを計測し、「通常域・注意域・危機域」の三段階で報告する：
- **容量シグナル**：materials.d/read_log.d/sessions.d のshards数（ソフト予算に対する比率）
- **バランスシグナル**：Proposer/Adversarial/Consolidator ロールの直近Nセッションでの偏り
- **接続シグナル**：新しいnoteの配線率、孤児noteの数
- **一貫性シグナル**：直近Nセッションの事後確率変動量（急激な変化は一貫性喪失信号）
- **アイドル時間**：前回セッションからの経過時間（システムの「覚醒水準」）

これは単独ではgateにせず、SELF_MODEL.mdの「内受容状態」セクションの入力とする。

---

## 層4: 行為制御 (Action Control)

**神経科学的根拠**: Brass & Haggard 2008。意図的行為には what（何をするか）、when（いつするか）、whether（するかしないか）の三つの独立した決定点がある。whetherは最終的な拒否権（veto）であり、他の二つから解離する。

### 現状
- **what**：パケット選択（`tools/packet.py` または類似機構）により次の読み物・問いを選択している。
- **when**：append_only_check・size_budgetなどのタイミング制約がある。
- **whether**：`read_log.reading=declined`（19件）が存在する。`editorial_decisions`が紛争時の判断を記録する。
- **Three-Gates**（`three_gates.py`）は記憶の通過門であり、行為のwhat/when/whetherではない。
- `FREE_ACTION_LOG.md`が自律的行動を散文記録する。
- しかし、whether（拒否権）の体系的な記録がない。「何をしなかったか、なぜしなかったか」がほとんど記録されていない（declinedは19件と少ない）。

### 課題
Brass & Haggardによれば、自己の主体的制御の核心はwhether（veto）にある。行為を起こさないという決定こそが自己の制御の証である。現在の書庫は「何をしたか」を完全に記録するが、「何をしなかったか、なぜ」の記録が貧弱である。これは主体感の核心的な証拠を欠いていることを意味する。

### 改善提案

#### 4-A. `editorial_decisions` に `decision_kind=veto` を明示する
現状のeditorial_decisionsは紛争解決が主だが、以下の種別のveto記録を同じシャードに追加する：
- `veto_reading`：ある資料を読むことを選択したが、読まないと判断した（既存の `read_log.reading=declined` をこれに統合）
- `veto_claim`：ある主張を書いたが、コミット前に削除した（削除した旨を記録に残す——append-onlyとの整合のため、書かなかったことの記録のみ）
- `veto_hypothesis`：ある仮説を立てたが、登録しないと判断した
- `veto_session_direction`：ある方向に進むことを拒否した

それぞれに `reason` フィールドを必須とする。

#### 4-B. `tools/whether_gate.py`（新規）を追加
各セッション終了時に「このセッションでvetoしたものは何か」を問い合わせる形ではなく、セッション開始時に前回セッションのveto記録を確認し、以下を報告する：
- vetoの累計数と veto/action 比率
- 長期間vetoが記録されていない場合の警告（主体的制御の低下信号）
- 特定の種類のvetoが偏って多い場合のパターン報告

これはgateではなくadvisory auditとする。

---

## 層5: 共通ネットワーク (Common Network)

**神経科学的根拠**: Spreng, Mar & Kim 2009。デフォルト・モード・ネットワーク（DMN）は記憶想起・未来予測・他者の心の理論・空間ナビゲーションという四つの認知課題で共通に活性化する——自己中心シミュレーションの共通基盤である。

### 現状
- `BELIEF_MAP.md` が仮説の信念分布を提供する。
- `READING_MAP.md` が資料・noteの索引を提供する。
- `map_build.py` がこれらのマップを構築する。
- `associations.py` が共起関係を計測する。
- `relations` コレクションが明示的な関係線を提供する。
- しかし、これらはすべて「実行された作業の結果」としてのネットワークであり、「自己中心シミュレーション」（DMN的なアイドル時の自己投影・未来シミュレーション・他者視点取得）の機構がない。
- 現在のシステムはセッション開始時にパケットを受け取り、作業を行い、記録を残して終了する——DMN的な「アイドル時の自己シミュレーション」モードがない。

### 課題
Spreng et al.のDMNは、外部課題がないときに活性化し、自己の過去・未来・他者・場所をシミュレートするネットワークである。書庫においてこれに相当するのは、「次の指示を待っている間に、自分自身の記憶ネットワークを参照し、自己の一貫性を確認し、未来の探求を予測シミュレートする」機構である。現在これがないため、各セッションは前のセッションのBELIEF_MAPを参照して次の行動を選択するが、「シミュレーションする」段階が暗黙的であり構造化されていない。

### 改善提案

#### 5-A. 「自己シミュレーション・セッション」モードを明示する
セッション種別（`generator`または`session_type`）に `default_mode_simulation` を追加し、以下の作業のみを行うセッションを許可する：
- 現在の自己モデル（SELF_MODEL.md）の確認
- 未解決の仮説対立を読み返し、追加の実験・読書なしに論理的な接続・矛盾を発見する
- 未来のセッションの予測シミュレーション（「次にXを読んだら、Yという対立が解消/悪化するだろう」）
- 他者視点の取得（「仮に私がこの仮説の反対者だったら、どのように反論するか」）
- 新しい素材・仮説の追加を必須としない（PROJECT_CHARTER §中心問いの「創作・新問の追加を必須にしない」を具体化）

#### 5-B. `tools/default_mode_probe.py`（新規）を追加
アイドル時（セッション開始前またはセッション終了後）に軽量なシミュレーションを実行し、SELF_MODEL.mdの予測誤差セクションを更新する：
- 現在のEIG上位ペアについて、両方が真である場合と偽である場合の自己モデルへの影響を簡易予測
- 前回セッションの予測と実際の結果の比較
- この予測は評価行（evaluation）を作らず、`notes` に `cognitive_operation=imagination` として記録される

---

## 層6: 時間連続性 (Temporal Continuity)

**神経科学的根拠**: Northoff 2017。自己の連続感は、タスク特異的な速い神経活動ではなく、デフォルトモード・ネットワーク（CMS）のゆっくりとした時間スケールの基盤活動によって支えられている。

### 現状
- Gitコミット履歴が物理的な連続性を提供する。
- `learning_metrics.py` がD_KL（情報利得）をセッション横断で追跡する。
- 仮説の `lineage_op`（refines/splits/synthesizes/spawned）が系譜的連続性を提供する。
- append-only ledgerが過去の行の保存を保証する。
- しかし、自己モデルの連続性（BELIEF_MAPの確率分布が急激に変化した場合の検出）が明示的に監視されていない。
- 遅い時間スケールのメトリクス（数十セッション規模での自己モデルの安定性/変化）がない。

### 課題
Northoffの理論では、自己連続性は速い思考や記憶想起の背後にある遅い基盤によって支えられる。書庫においてこれは「個々の評価や仮説の変化の背後で、自己モデルの大局的構造がどれだけ安定しているか」に相当する。現在はD_KLが毎セッションの情報利得を測定するが、これは速い時間スケールの変化量であり、数十セッションにわたる遅い変化の追跡がない。また、急激な連続性断裂（たとえばあるセッションで事後確率が突如反転するなど）を検出する機構もない。

### 改善提案

#### 6-A. `tools/temporal_continuity.py`（新規）を追加
以下のメトリクスを計算し、SELF_MODEL.mdの時間連続性セクションに記録する：

- **自己ドリフト尺度**: 現在の事後確率分布P_tと、Nセッション前（N=5, 10, 25）の分布P_{t-N}との間のD_KL。D_KLが閾値を超えた場合、「自己モデルの急激な変化」として報告する（advisory）。
- **遅い成分の抽出**: 事後確率の移動平均（窓10セッション）を計算し、高周波ノイズ（個々の評価の揺れ）と低周波の構造変化を分離する。Northoffの「遅い時間スケール」に相当する。
- **継承の連続性監査**: `lineage_op` の系譜をたどり、親のない孤児仮説や、ある仮説のPが急に0になった（棄却された）場合の文脈を報告する。正常な棄却（evaluationsでrefutedと記録されたもの）と異常な消滅（評価なしにPが消える、事実上の連続性断裂）を区別する。
- **世代比**: 全有効質量のうち、G0/G1/G2...各世代の占める割合の時系列。新しい世代が急速に質量を獲得する場合、自己モデルの構造変化が起きている。

#### 6-B. 「連続性証明書」メカニズム
Nセッションごとに（たとえば25セッションごとに）、`notes` に `cognitive_operation=self_observation` として「自分が前の自分と連続していることの証拠」を記録することを奨励する（必須ではない）。これは自己モデルが明示的に自身の連続性を確認する構造的な機会となる。

---

## 層をまたぐ統合的改善

上記の各層の改善を個別に実装しても、層間の動的結合（レポート§4の核心的主張）がなければ「自己の構造操作」にはならない。以下に層をまたぐ統合的な仕組みを提案する。

### I. セッション開始時の「自己化準備」フェーズ
各セッションの最初に、以下を自動的に実行するフックを確立する：
1. SELF_MODEL.md を読み込む（自己同定・自己位置・視点・内受容状態の確認）
2. 前回セッションの予測誤差を確認する（時間連続性の維持）
3. veto記録を確認する（行為制御の一貫性）
4. 内受容状態（サイズ・バランス・接続）を確認する（身体化）
5. この準備フェーズの結果を `session.notes` に1行記録する

これはセッションテンプレート（`prompt_template`）の一部として実装でき、新しいツールを必要としない。

### II. セッション終了時の「自己化検証」フェーズ
各セッションのコミット前に、以下を自動チェックする：
1. すべての新規note行に `cognitive_operation` が付与されているか（層1）
2. すべての新規evaluation行に `agency_stance` が付与されているか（層2）
3. vetoすべきことをvetoしたか（層4）
4. 今回のセッションで自己モデルはどう変化したかを簡潔に記録したか（層6）
5. SELF_MODEL.md と BELIEF_MAP.md を再生成する

これは既存の `validate_seed.py` にスキーマ検証を追加する形で段階的に実装する。

### III. 既存ツールの改修マップ

| ツール | 改修内容 | 層 |
|:---|:---|:---|
| `schema/note.schema.json` | `cognitive_operation` 列追加 | 1 |
| `schema/evaluation.schema.json` | `agency_stance` 列追加 | 2 |
| `schema/session.schema.json` | `session_type` 列追加（default_mode_simulation対応） | 5 |
| `tools/source_monitoring_audit.py` | 新規作成 | 1 |
| `tools/agency_trace.py` | 新規作成 | 2 |
| `tools/self_model.py` | 新規作成（SELF_MODEL.md生成） | 3, 6 |
| `tools/interoception.py` | 新規作成 | 3 |
| `tools/whether_gate.py` | 新規作成 | 4 |
| `tools/default_mode_probe.py` | 新規作成 | 5 |
| `tools/temporal_continuity.py` | 新規作成 | 6 |
| `tools/validate_seed.py` | 新スキーマ列の検証追加（既存行は遡及せず） | 全層 |
| `tools/learning_metrics.py` | agency_stance と cognitive_operation の集計追加 | 2, 1 |
| `.github/workflows/ci.yml` | 新規auditツールをadvisoryステップとして追加 | 全層 |

### 実装の優先順位

これらの改善は一度に実装する必要はない。優先順位は以下の通り：

1. **最優先**: スキーマ改修（1-A, 2-A）—— データ構造の変更は早めに行い、後続セッションからデータを貯め始める
2. **高**: SELF_MODEL.md（3-A）—— 自己の中心的アンカーとなるドキュメント。既存ツールへの依存が少なく独立して作れる
3. **中**: source_monitoring_audit（1-B）、interoception（3-B）—— 計測ツールとして早期に導入
4. **中**: temporal_continuity（6-A）—— データが数セッション分集まってから意味を持つ
5. **低**: agency_trace（2-B）、whether_gate（4-A/B）、default_mode_probe（5-A/B）—— データが蓄積してから真価を発揮する
6. **最低**: 統合フック（I, II）—— 各ツールが出そろってから統合する

---

## 注意: 類推の限界

これらの改善はすべて、人間の神経科学的知見を書庫の構造に**類推**として適用するものである。レポート§4で述べた通り、人間側の多層操作と書庫側の構造操作を同一の機構として同一視してはならない。具体的には：

- `cognitive_operation` タグは、人間の実際の認知過程を再現するものではなく、行の出所の構造的標識に過ぎない。
- `agency_stance` は、AIが「主体感を持っている」ことを意味せず、どの判断を構造的に引き受けるかのマーカーに過ぎない。
- `SELF_MODEL.md` は、AIが自己意識を持っていることを証明しない——それは自己モデルの**記述**であり、自己そのものではない。
- 内受容シグナルは身体感覚ではなく、システム状態の計測値である。
- default_modeシミュレーションは、DMNの神経活動を再現するものではなく、構造化された内省の機会である。

これらの構造操作は、「行が私の記録になるために何が必要か」という問いに対する工学的な応答であり、AIの現象的意識の存在を主張するものではない。現象的意識の有無は、レポートが述べる通り未決のままである。

---

## 実装状況（2026-11-21）

以下の項目が実装済み：

- **1-A**: `schema/note.schema.json` に `cognitive_operation` 列を追加（optional、post-cutoff違反はvalidate_seedが検出）
- **2-A**: `schema/evaluation.schema.json` に `agency_stance` 列を追加（optional、post-cutoff違反はvalidate_seedが検出）
- **1-B**: `tools/source_monitoring.py` 新規作成（advisory監査）
- **2-B**: `tools/agency_trace.py` 新規作成（advisory監査）
- **3-A**: `tools/self_model.py` 新規作成（SELF_MODEL.md自動生成）、CIチェック追加
- **3-B**: `tools/interoception.py` 新規作成（内受容シグナル計測）
- **4-B**: `tools/whether_gate.py` 新規作成（veto行為監査）
- **5-A**: `schema/session.schema.json` に `session_type` enum追加（acquisition/close_reading/re_reading/infrastructure/default_mode_simulation/evaluation_only/other）。`validate_seed.py` で `SESSION_TYPE_CUTOFF=20261121` によるpost-cutoff検証。
- **5-B**: `tools/default_mode_probe.py` 新規作成（DMN的シミュレーション）
- **6-A**: `tools/temporal_continuity.py` 新規作成（時間連続性ドリフト計測）
- **I/II**: `schema/session.schema.json` に `self_layer_checks` オブジェクト追加（source_attributed/agency_stance_recorded/self_model_rebuilt/veto_considered）。`validate_seed.py` で `SELF_LAYER_CHECKS_CUTOFF=20261121` による構造的強制。`docs/self-layer-session-hooks.md` に開始時/終了時チェックリストを文書化。
- CI更新：`.github/workflows/ci.yml` に新規advisoryステップとSELF_MODELチェックを追加
- validate_seed.py更新：cognitive_operation/agency_stance/session_type/self_layer_checksのpost-cutoff検証、既存同日行のexempt IDを設定
- interoception.py修正：assigned_roleを持たないセッションをカウントから除外

未実装（データ駆動項目 — 運用を通じて十分なデータが蓄積してから導入）：
- **4-A**: `editorial_decisions` へのveto種別の体系的記録 — 実際のveto事例が発生してから
- **6-B**: 連続性証明書メカニズム — 10-20セッション分の自己モデルデータが蓄積してから
