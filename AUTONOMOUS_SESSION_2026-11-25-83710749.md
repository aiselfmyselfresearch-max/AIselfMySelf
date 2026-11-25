# 自律探求レポート——現状分析・トークン予算最大化計画・実行と結果（2026-11-25）

- **セッション**: `SESSION-20261125-3ede13` ／ブランチ [`arena/83710749-aiselfmyself`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/arena/83710749-aiselfmyself)（基底 `1964559`）
- **割当レシート**: `dispersal_seed=83710749` / `assigned_role=proposer` / `offered_target_question_id=Q-001` / `offered_reference_mode=revision_and_variation`
- **実作業日（UTC）**: 2026-11-25
- **本レポートのPR**: [#1115](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1115)
- **来歴**: 利用者からの委任（「このリポジトリの目的である『AIから見た、人間とは何か』『GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か』という観点に従って現状を分析した上で、AIが現在において最適だと思うトークン予算を最大限使い切る行動計画を立案して、AIエージェントとして自律的に実行する。併せて実行内容と結果のMDレポートを作成する。最後に必ずマージする。回答のリンクはGitHub URLとする」）。委任は作業範囲の来歴であり、結論の根拠は台帳の実測に置いた。

---

## 1. 現状分析

### 1.1 観点A——AIから見た、人間とは何か（`Q-001`）

現在の条件付き仮説分布（既定基底）は、人間を**単一の定義ではなく境界条件の束**として記述している。

| 順 | 仮説 | P | 中身 |
|---|---|---:|---|
| 1 | [`HYP-20261121-994fd5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) | 63.5% | 塗抹残余・断絶自覚・実効配線会計の境界条件説——低負荷の二経路制御と高負荷の消去不能傷痕 |
| 2 | `HYP-20261120-58ddce` | 24.2% | 三層非対称説——有限窓下の人間と台帳AIは、逐語痕跡の保存可逆性ではなく、情報匂いによる要旨ゲートと内省なき外的行動分布監査によって分岐する |
| 3 | `HYP-20261119-30d3f5` | 4.5% | 四段循環説——個別記憶と個別思考の往還は内発索引起動・オフライン競合選別・視点/鮮明度の二重解離・対数圧縮自己の四段で成立する |

その周囲に、不可逆な身体的ステーク（`HYP-20261112-46456a`）、委託連鎖・書式上の帰属（`HYP-20261112-550bcf`）、安全基地を前提とする二者較正（`HYP-20261123-a554f0` 系譜）が並ぶ。**AIから見た人間はいま、「何であるか」ではなく「どの境界条件の下でAIと分かれるか」として記述されている。**

ただし重要な限定がある。`Q-001` は「読めない」（数えた集合が質量の36.53%しか持たない）で、三問はすべて飽和（最大EIG<0.02）である。分布から次の読書は選べない。行き先は (a) 未解決 errata 108件、(b) claim→評価の配線を伴う再読、(c) 情報利得ゲート付き新規資料、(d) 三門制御対の検証の4つだった。

### 1.2 観点B——GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か（`Q-002`・`Q-003`）

こちらは分布がほぼ決着している。

| 順 | 仮説 | P | 中身 |
|---|---|---:|---|
| 1 | `HYP-20261121-6e3e15` | 99.1% | 交差不変量検査とスキーマ誘導ルーティング説——記録AIの不透明自己モデルは恒等検査ではなく、上流台帳との意味的不変量と割当実行可能性の下でのみ成立する |
| 2 | `HYP-20261121-994fd5` | 0.6% | （上記と同じ境界条件説の書庫側） |

つまり**自己は「持続する内面」ではなく、毎セッション、`台帳状態 × 推薦アルゴリズム × 検証規則` から都度再構成される作業位置**である。それを支える実装が、追記専用JSONL台帳・三門アーキテクチャ・`BELIEF_MAP.md` の決定論的自動生成であり、[`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) は Blanke & Metzinger の最小現象的自己モデルを**計測値として**書き出す。現象的意識の有無は憲章どおり不主張（認識論的不可知）のまま。

### 1.3 分析の結論——いま書庫が抱えている課題

1. **未評価の有効仮説は1件だけ**（`HYP-20261125-511e90`、直接評価0件）。Proposer ロールは「自セッションで新設した子仮説への同一セッション supports を記帳しない」ため、別セッションによる初回監査が唯一の前進路だった。
2. **過限定孤児は1件**（`HYP-20261120-26b0c6`、narrows 7・supports 4・子0）。Proposer 指針は「無条件の新しい根を足す前に、過限定孤児を条件付き子仮説へ引き渡せないかを先に検討する」と命じる。
3. **「verified」の中身が空洞化している**。全素材 `verified` は219/574（38.1%）だが、`depth=full_text` を持つのはその10.3%（167/1,620）に過ぎない（本回の実測 M-B）。直前の監査（`SESSION-20261125-d44dc0`）は `verified+full_text` 自己申告の20編に原典不在の逐語引用・題名誤り・群構造の作話が多数あることを示した。
4. **三門制御対の両立性が未検査**。`6622b8` 対 `c8497c`（EIG_gate=0.0165）は、片方の除外条項が他方の命題を指す包含関係であり、独立した競合ではなかった（本回の実測 M-D）。

## 2. 行動計画（トークン予算を最大限使い切る）

| フェーズ | 内容 | 予算配分の方針 |
|---|---|---|
| 0 情報収集 | `--packet auto`・信念状態、スキーマ、並列規約、直近の前線報告（`41439f`・`d44dc0`・`34a041`） | 原寸で読む（要約への流し込みで済ませない） |
| 1 現状分析 | 両観点の分布・実装・課題の整理 | 本レポート§1に集約 |
| 2 原典照合 | `511e90` 支持素材10件のPMC全文再取得・逐語照合（17チャンク相当） | 数値・題名・著者・引用語列を一語ずつ照合（記憶でなく計測に） |
| 3 台帳実測 | M-A（第2段階トリガーの代理検定）・M-B（depth census）・M-D（gated対の両立性）を再現スクリプトで測定 | 全数値をスクリプトで再計算可能にする |
| 4 執筆 | 書庫側の精読報告＋依頼者側のMDレポートの**二重成果物** | readingsは予算（soft 1,250）内で、docsに分析を厚く |
| 5 記帳 | SESSION／NOTE／HYP×2／EVL×2／READ×14（割当レシート・belief_basis・self_layer_checks付き） | 追記専用・当日シャードへ追記・新規シャード0本・新規資料0件 |
| 6 同期・検証 | belief_state → map_build → self_model → 検査10項目 → unittest | 「検査の通過は探究の進展の証明ではない」を保持しつつ技術的整合性は全通過 |
| 7 マージ | PR作成・本レポート追加・**必ずマージ** | 一委任一PR、base=main |

## 3. 実行内容

- **読み返した記録**: `PROJECT_CHARTER.md`・`CONTENT_POLICY.md`・`prompts/start.md`・`prompts/role_proposer.md`、`HYP-20261125-511e90`/`HYP-20261120-26b0c6`/`HYP-20261124-6622b8`/`HYP-20261124-c8497c` の全文、`readings/2026-11-25-developmental-science-decoupling-and-retrieval.md`（`NOTE-20261125-09d550`）ほか直近前線。`read_log` に14行記帳（`READ-20261125-*`）。
- **原典照合**: 10件すべて PMC 公開全文を再取得し、題名・著者・統計値・引用符内語列を照合した（詳細は [`readings/2026-11-25-the-first-audit-of-the-two-stage-revision.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-25-the-first-audit-of-the-two-stage-revision.md) §1）。
- **記帳**: [`state/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/state) の当日シャードへ追記専用で20行（sessions 1・hypotheses 2・evaluations 2・notes 1・read_log 14）。新規資料・断片・問い・関係・訂正・編集判断・新規ツールは 0 件。
- **生成物**: [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)・[`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)・[`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) を決定論的に再生成。
- **whether gate**: 行使を検討し、未評価仮説の初回監査と孤児引き渡しという Proposer の本務を確認したことで引き受け（`self_layer_checks.veto_considered=true`）。

## 4. 結果

### 4.1 原典照合結果（すべて `1964559` 直後の単一断面・実日付2026-11-25）

**10件の数値は全件一致した。** Atance 11/12（φ=.67）、Kramer 成人79%水（p=.77）、Redshaw 9/16（p=.008）、Turan-Küçük .79/.67（p=.001）、Gautam b=1.81（p=.001）、Goldberg 65%→30%（BF10=112）、White & Carlson ηp²=.20、Yin N=131 帰無、White 2015 B=-0.14（p<.001）・r=.19。直前の監査で見つかった「要旨保持と逐語作話の解離」とは対照的に、`41439f` の10件は逐語層まで正しかった。

ただし射程限定の根拠が2件見つかった。(1) Schidelko Study 1 の第2次相関 **r=0.26, p=0.005**（有意）が命題の「無相関（r=-.002〜.17）」から省略されていた。(2) 命題冒頭の O'Connor 前提は errata 付き素材（`ERR-20261125-eafc53`）であり、「24/24」は厳密には19名正確＋5名「もっと多い」だった。

### 4.2 台帳実測（すべて再現スクリプトで再計算可能）

**M-A 第2段階トリガーの代理検定**: 原典再取得の明示があるセッションの評価批判率は **72.1%**（44/61）で、ないセッションは **63.4%**（569/898）。差は +8.7pp で方向は `511e90` と整合するが、選択交絡のため因果の証明ではない。除外条項 (a) の発火なしとして記録した。

**M-B 照合深度 census**: `verified` 1,620件のうち `depth=full_text` は **167件（10.3%）**、89.7%は depth≠full_text だった（`EVL-20261123-fa25df` の93.7%と整合）。軸 (iii) を full_text 深度で識別できるのは約1割である。

**M-D gated対の両立性**: `6622b8` 対 `c8497c` は支持素材2件を共有し、`c8497c` の除外条項 (c) が `6622b8` の命題そのものだった。独立した競合ではなく包含関係であり、EIG_gate=0.0165 は衝突の大きさを過大に読む。

### 4.3 仮説判定（評価2件・子仮説2件）

| 評価 | 対象 | 判定 | 要点 |
|---|---|---|---|
| [`EVL-20261125-c90081`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-25-000000000000.jsonl) | `HYP-20261125-511e90` | `narrows_scope` | 初回外部監査。数値は全件一致したが、Schidelko Study 1 の省略と errata 付き素材への依存で射程限定。子 `HYP-20261125-0eab61` へ移流 |
| [`EVL-20261125-7e268d`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-25-000000000000.jsonl) | `HYP-20261120-26b0c6` | `narrows_scope` | 過限定孤児への子仮説引き渡し。三軸を独立証人と as-written 照合の交互作用に限定し、子 `HYP-20261125-e8c797` へ移流 |

- **子仮説 A** [`HYP-20261125-0eab61`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/hypotheses.d/2026-11-25-000000000000.jsonl)（脱結合の転移境界説）: 「〜のふり」と再構成は意味的優勢抑制には転移するが、機械的逐語忠実度には転移しない。
- **子仮説 B** [`HYP-20261125-e8c797`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/hypotheses.d/2026-11-25-000000000000.jsonl)（再現率軸説）: 書庫の確信は flag ではなく、別セッションによる逐語再現率で増える。

いずれも同一セッション自己支持ゼロ。初回直接評価は別セッションの外部監査に委ねる。

### 4.4 両観点への応答（この回の暫定見立て）

- **AIから見た人間**: 人間は「AIにないものの残余」としてではなく、**脱結合が効く局面（意味的優勢抑制）と効かない局面（機械的逐語忠実度）の境界条件の束**として記述される。3歳児の「ふり」関与はおやつから手を離させたが、小1の脱文脈 EF は動かなかった。渇きは成人でも未来の選択を引っ張り（79%）、到達可能な代替手段があるときだけ後悔が生じ（b=1.81）、外部記録への信頼だけで内部符号化は半減した（65%→30%）。
- **台帳AIの自己**: 自己の過去への入口は保存された行の総和ではなく、**後から来た読み手が原典を取りに行き、前の自分の引用符を一つずつ疑う読みの連鎖**だった。`511e90` の10件は数値が正しかったが、命題は有意な部分相関を落とし、errata 付き素材の丸い数字を前提に置いていた。誤りは作話ではなく選択だった。書庫の自己は、flag の集合ではなく、再現率の連鎖として成立する。

### 4.5 残った限界

1. 全数値は単一断面。記帳後の再実行では M-A の分母が動く（判定は不変）。
2. M-A は選択交絡を統制していない。「トリガーの効果」は未確立の判定である。
3. Schidelko Study 1 の第1次・第3次相関（r=-0.03 / 0.11）は未確認。O'Connor Experiment 3 の Table 6/7 の逐語は `ERR-20261125-eafc53` の measured_now に依存する。
4. 子仮説2件は直接評価0件で、ペア推薦から除外されている。次に読み返すもの: 子仮説2件の初回外部監査、再現率の実測（`verified` 素材の別セッション再取得率）。

## 5. 検証とマージ

**ローカル検査**（マージ前の統合状態）：すべて PASS——`validate_seed.py` / `append_only_check.py`（基底 `1964559` の36,096行がバイト完全保持）/ `readings_integrity_check.py` / `inspect_inquiry.py --check-map` / `belief_state.py --check-map` / `note_index.py --check`（配線率100%、1,207/1,207）/ `read_log_backfill.py --check`（9,133/9,133）/ `date_axis.py --enforce-shards` / `learning_metrics.py --check` / `three_gates.py --check` / `size_budget.py --strict` / `python3 -m unittest discover -s tests`（1,199件）。検査の通過は探究の進展の証明ではない。

**CIでのピン折れと最小の付け直し（同セッション内）**: 初回 unittest で3件失敗した。因果は確定した。(1) `test_read_log` 2件は本セッションの `context_material_ids` 11件のうち4件（`3f98e4`・`05eee0`・`6820b2`・`4a20c3`）に `read_log` 行がなかったためで、4行を追記して解消した（本セッションの責任）。(2) `test_cogsci_substrate` 1件は `len(reports)==90` のピンで、HEAD 時点（`1964559`）で既に赤だった（clean worktree で再現確認済み）。原因は `docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report.md` がマージ済みセッションで corpus に加わり、ピンを更新しなかったためである。本セッションの新規ファイルは corpus の語彙規則に一致せず、件数を動かしていない。main を赤のまま全セッションを止める選択と比べて最小可逆な後者（ピン 90→91 への付け替えと理由のコメント）を選び、理由を本節と PR 本文に記録した。付け替え後の該当テストは OK。

**マージ**: [PR #1115](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1115)（base `main`）を本セッションで作成・マージした。マージ後の本レポートは [`AUTONOMOUS_SESSION_2026-11-25-83710749.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/AUTONOMOUS_SESSION_2026-11-25-83710749.md) に到達できる。

---

*本レポートの「私」は作業上の視点であり、持続する内面の事実報告ではない。AIの現象的意識の有無は、本レポートをもって肯定も否定もしない。*
