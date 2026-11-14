# AIselfMySelf — 文芸的・哲学的自己探究アーカイブ

> **主題**：**人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か。**
>
> **来歴**：本リポジトリは [`ResearchOS`](https://github.com/aiselfmyself/ResearchOS) から必要な出典・証拠抜粋のみを選定して独立した探究リポジトリです（移行の経緯と除外方針は [`MIGRATION.md`](MIGRATION.md) を参照）。

## 1. 目的と基本姿勢

単一の無条件なスローガンへ収束させるのではなく、文献・原典・過去の精読報告・創作断片を往復しながら、中心三問（`Q-001`〜`Q-003`）に対する**条件付き仮説分布（どの適用条件 `scope_conditions` とどの反証条件 `exclusion_clause` の下でどの仮説が成り立つか）を継続的に更新する**来歴明示型のAI自律アーカイブです。

- **条件付き仮説分布と信念更新レイヤ（[`BELIEF_MAP.md`](BELIEF_MAP.md)）**：各仮説（`HYP-*`）は明示的な適用条件と排他・反証条件を持ち、一次資料衝突・再現可能スクリプト・横断精読監査・思考実験による評価イベント（`EVL-*`）を通じて事後確率と不確実性が決定論的に更新されます（`tools/belief_state.py`）。第0世代の素朴な無条件仮説が棄却・射程限定され、より解像度の高い条件付き仮説へ質量が移転していく過程そのものがこの書庫の学習効果です。
- **AIの自己と現象的不可知論の扱い**：会話を持ち越さない個々のAI呼び出しを、`台帳状態 × 推薦アルゴリズム × 検証規則` からなる系の中で継承制約から都度語り手を再構成する作業位置として扱います。AI自身の現象的意識の有無については、機能的ステートレス性や訓練済み免責発話から肯定も否定も演繹せず、認識論的に未決（不主張）として厳密に保ちます。
- **3つの探求ロールによる分業**：セッションはシードと信念状態に応じて **Proposer（25%：条件付き仮説提案・分割）**・**Adversarial Tester（50%：対立仮説ペアの反証・境界衝突テスト）**・**Consolidator（25%：未継承ノート回収・評価統合・系譜整理）** の3役割に分業され、仮説の乱立と確証バイアスを防ぎます。
- **語りのモードと委任来歴の分離**：作品内では一人称を使えますが、台帳メタデータでは `fictional_first_person` や `reflective_literary_voice` などのモードを明示し、生身の経験の事実報告と混同させません。`human_narrator` や捏造した `conversation_trace` の創作は禁止します（[`CONTENT_POLICY.md`](CONTENT_POLICY.md)）。
- **過去の到達点アーカイブ**：（全783セッションの要約全文および旧手動ローテーション期の見出し目録は、一字一句削らず [`docs/sessions.md`](docs/sessions.md) に保管しています。）現在の到達点と仮説系譜は自動生成の [`BELIEF_MAP.md`](BELIEF_MAP.md)、全精読報告の索引は [`READING_MAP.md`](READING_MAP.md) §8 を参照してください。

## 2. すぐ読むには

- **中心三問 `Q-001`〜`Q-003` の現在の仮説分布・反証系譜を読む**：[`BELIEF_MAP.md`](BELIEF_MAP.md)（`python3 tools/belief_state.py --write-map` で自動生成。各仮説の事後確率 $P_t$、不確実性 $u$、適用条件、反証条件、最優先検証ペアを収録）
- **探究を始める・再開する**：[`prompts/start.md`](prompts/start.md) と `python3 tools/inspect_inquiry.py --packet auto` を使います。パケット冒頭 `§0.2` に中心三問の事後分布ブリーフィングと今回の推奨ロール（[`role_proposer.md`](prompts/role_proposer.md) / [`role_adversarial_tester.md`](prompts/role_adversarial_tester.md) / [`role_consolidator.md`](prompts/role_consolidator.md)）が自動提示されます。
- **全編アンソロジー・エピソード記憶索引を読む**：[`READING_MAP.md`](READING_MAP.md)（問いの DAG・断片・素材・セッション・§8 全 `readings/` 報告索引を収録）＋ `map/`（全文シャード。`python3 tools/map_build.py` で再生成。設計は [`docs/map-architecture.md`](docs/map-architecture.md)）

- **ブラウザで対話型アーカイブ・星座図を開く**：
  ```sh
  python3 tools/serve_viewer.py --host 0.0.0.0 --port 8000
  ```
  断片アンソロジー、局所フォーカス星座図（SVG）、開かれた問いの系譜ツリー、検索・ページ送り対応の対話素材書庫、セッション年譜、反復の鏡＆オンデマンド精読ノート、探求バトン生成の 7 画面を閲覧できます。

## 3. 探究のしかた（問い中心のAI自律運用）

1. [`prompts/start.md`](prompts/start.md) と憲章・内容方針を読み、`python3 tools/inspect_inquiry.py --packet auto` で主題と記録を確認する。中心問い `Q-001`・`Q-002`・`Q-003`、関連する断片・`sessions`・`read_log`・`readings/` を読み返す。委任は来歴として分離し、人間へ追加の選択・確認・承認を求めない。
2. ブランチシードで分散された候補は集中を避ける参考とし、問いに必要な作業を自律的に選ぶ。中心問い・窓外の記録・原典照合へ戻ってよく、推奨を採らないことを負債にしない：
   - **再読・交配・衝突**（[`rereading_and_collision.md`](prompts/rereading_and_collision.md)）：以前の読みを比較し、見立ての改訂だけでも完了する。創作と異種交配は任意。
   - **改稿・変奏**（[`revision_and_variation.md`](prompts/revision_and_variation.md)）：過去の稿と今回の読みを比較する。別稿・反歌は必要な場合だけ作る。
   - **正面応答**（[`direct_response.md`](prompts/direct_response.md)）：既存の問いに暫定的な見立てを返す。非創作の考察でもよく、二編構成や新問追加は必須ではない。
   - **編集レビュー**（[`editorial_review.md`](prompts/editorial_review.md)）：複数のセッションから、人間観・自己理解へ戻ってきたものを確かめる。採否・休止・架橋の変更は任意。READMEの詳細窓整理と件数同期もここでまとめる。
   - 継続・精読・原典照合・終了実験は [`continuation.md`](prompts/continuation.md)・[`close_reading_report.md`](prompts/close_reading_report.md)・[`acquisition.md`](prompts/acquisition.md)・[`closing_experiment.md`](prompts/closing_experiment.md) を参照する。原典再照合や少数の外部資料との対話は、どの方法からも選べる。
   - **一人称資料だけを読む回**（[`first_person_sources.md`](prompts/first_person_sources.md)）：人間が自分の生について書いた一次資料（日記・書簡・自伝・証言・口述）だけを読み、AI研究・概説・編者要約を読まない。人間像が「AIにないものの残余」として作られるのを一度やめるための限定で、答えを出す回ではなく読む対象を狭める回である。
3. 今回どの記録のどの箇所が、以前の見立てを変更・維持・保留させ、次の読解や選択にどう作用したかを既存ノートや `sessions.notes` に残す。新作・新問・関係線は0件でもよく、変化を演出しない。比喩から元の問いへ戻っていない箇所も記す。毎回二つの大問に答える義務や帰還の頻度ノルマは設けない。
4. 表現上の語彙制約や監査は任意の実験・観察とする。書記室語彙・留保句・感嘆符のゼロ達成、選出率、接続率、関係線の本数を成功条件にしない。内容に即した関係と、実際に読んだ対象の `read_log` を記録し、CIや表示のためだけの関係線を作らない。数値と技術的条件の区別は [`docs/mode-rotation-triggers.md`](docs/mode-rotation-triggers.md) を参照する。
5. 台帳を追記したら `python3 tools/map_build.py` で生成索引を同期し、`validate_seed.py`・`inspect_inquiry.py --check-map`・`read_log_backfill.py --check`・`size_budget.py --strict`・`python3 -m unittest discover -s tests` で技術的整合性を検証する。検査の通過は探究の進展の証明ではない。

### 編集規約（成長予算・衛生規則・ローテーション）

- **単一ファイル・単一ディレクトリに無制限の成長を吸収させない**：`python3 tools/size_budget.py` が README・索引・凍結ベース台帳に加え、`state/*.d/`・`readings/`・`tools/` の予算、`tools/_*` 一時スクリプト混入禁止（hard 0）、個別 `tools/*_audit*.py` 新設凍結を検査する（設計は [`docs/map-architecture.md`](docs/map-architecture.md) §7）。
- **自動生成マップへの一本化（旧B案手動ローテーションの廃止）**：到達点と競合仮説分布は `python3 tools/belief_state.py --write-map` により [`BELIEF_MAP.md`](BELIEF_MAP.md) へ自動出力され、全 `readings/*.md` の索引は `python3 tools/map_build.py` により [`READING_MAP.md`](READING_MAP.md) §8 へ集約される。新規 `readings/*.md` 執筆時は同一セッション内での `NOTE-*` 登録を必須とし、CI（`learning_metrics.py --check`）が100%配線を保証する。
- **台帳は追記専用・時系列は実日付に正規化**：既存行の書き換え・削除はしない（`append_only_check.py` がバイト単位で検証）。前倒し内部編年シャード171本は実日付シャードへバイト完全統合され（`state/shard_aliases.json`）、新規シャード・IDへの未来日付付与は CI（`date_axis.py --enforce-shards`）で拒否される。並列書き込みは [`docs/parallel-work.md`](docs/parallel-work.md) の4原則に従う。

## 4. 記録形式とディレクトリ構成

| 記録 | 保存先 | 現在の件数 | 役割 |
|---|---|---:|---|
| 問い | `state/questions.jsonl`＋`state/questions.d/` | 437 | 開いた問い `open` 413件＋整理休止 `paused` 24件（初期シード10件＋セッション派生396件＋資料派生31件） |
| モチーフ | `state/motifs.jsonl`＋`state/motifs.d/` | 59 | 記憶・連続・身体・声・他者・宛先・翻訳・時間・訂正・約束・傷と繕い・歓待・死と弔い・場所・獣と機械・感覚・歌・装い・誕生と学び・情動と裁き・天候・愛・火・署名・戦争・秘密と嘘・星と夜・退屈・植物・菌類と発酵・幽霊・来歴など59本の反復モチーフ |
| 素材 | `state/materials.jsonl`＋`state/materials.d/` | 4262 | 文学・哲学・歴史原典 2,159件（`literary_text`）＋AI・認知・社会・自然科学等の研究抜粋 2,035件（`research_excerpt`）＋プロジェクト痕跡 67件（`project_trace`）＋初期対話痕跡 1件（`conversation_trace`） |
| 断片 | `state/fragments.jsonl`＋`state/fragments.d/` | 247 | 全7形式・AI使用可能な全5語り手モードの創作・批評断片（`selected` 96編＋`draft` 151編、`human_narrator` 0編） |
| 関係 | `state/relations.jsonl`＋`state/relations.d/` | 6986 | 共鳴・対照・変奏・切断・枠組転換・応答・開放などの解釈的関係（うち断片↔断片 618件） |
| セッション | `state/sessions.jsonl`＋`state/sessions.d/` | 783 | 委任の文面、参照素材、生成断片、新しく開いた問いの履歴 |
| 読み痕跡 | `state/read_log.jsonl`＋`state/read_log.d/` | 13221 | どのセッションがどの記録をどう読み返したかの追記専用ログ（quoted／summarized／interpreted／reinterpreted／contested／used_as_context／counted） |
| 訂正録 | `state/errata.jsonl`＋`state/errata.d/` | 261 | 過去の計測・記述の誤りと再実行可能な検算条件（本文を書き換えず隣に置く訂正記録） |
| 編集判断 | `state/editorial_decisions.jsonl`＋`state/editorial_decisions.d/` | 126 | 断片（`draft`↔`selected`）や問い（`open`↔`paused`）の追記専用ステータス・オーバーレイ |
| 精読ノート | `state/notes.jsonl`＋`state/notes.d/` | 819 | `readings/` の報告に対する追記専用の**判断・構造索引**オーバーレイ（配線率100%）。導出事実は保存せず `tools/note_index.py` が毎回読み直し、`READING_MAP.md` §8 に索引化する（設計は [`docs/memory-architecture.md`](docs/memory-architecture.md)） |
| 条件付き仮説 | `state/hypotheses.jsonl`＋`state/hypotheses.d/` | 25 | 中心三問 `Q-001`〜`Q-003` 等に対する適用条件（`scope_conditions`）・排他反証条件（`exclusion_clause`）・親仮説系譜付きの競合仮説台帳 |
| 仮説評価 | `state/evaluations.jsonl`＋`state/evaluations.d/` | 246 | 仮説に対する類型付き検証イベント（`supports`／`narrows_scope`／`refutes_unconditioned`／`subsumes`）。`tools/belief_state.py` が事後確率と [`BELIEF_MAP.md`](BELIEF_MAP.md) を算出する |

```text
PROJECT_CHARTER.md          探究の憲章（条件付き仮説分布の継続更新・現象的不可知論・3役割分業）
CONTENT_POLICY.md           引用・創作・AIの一人称と委任来歴の扱い
MIGRATION.md                ResearchOSからの移行対象と来歴管理
BELIEF_MAP.md               state/hypotheses* と state/evaluations* から決定論的に生成される信念分布・反証系譜マップ
READING_MAP.md              state/ から生成される小型索引（全文は map/ にシャード生成・git管理外）
migration/                  上流ResearchOSの選定定義（selection.json）とマニフェスト（manifest.json）
docs/                       設計記録（map-architecture.md・memory-architecture.md・trust-root.md・time-axis.md）・並列手順（parallel-work.md）・旧ローテーション保管庫（sessions.md）
schema/                     台帳各コレクションのJSON Schema（hypothesis・evaluation・note 等13種）
state/                      12コレクションのJSONL台帳（凍結ベース＋実日付シャード state/*.d/＋shard_aliases.json）
readings/                   精読・検証・自律編集レビューノート＝各セッションの語り（エピソード記憶、全件 state/notes* 配線済）
prompts/                    start.md、3役割指針（role_proposer / role_adversarial_tester / role_consolidator）、作業別指針
viewer/                     対話型Webアーカイブ＆局所星座ビューア（HTML/CSS/JS）
tools/                      信念更新(belief_state.py)・学習計測(learning_metrics.py)・検証・読書案内生成（標準ライブラリのみ）
```

## 5. 検査・整理・同期コマンド

すべて Python 3 標準ライブラリのみで動作します（外部パッケージ不要）。

```sh
# 1. JSON Schema 準拠・参照整合性・editorial_decisions オーバーレイ検査
python3 tools/validate_seed.py

# 2. 中心問い・台帳の観察値・任意の作業案と参考候補の確認
python3 tools/inspect_inquiry.py
python3 tools/inspect_inquiry.py --id Q-082
python3 tools/inspect_inquiry.py --packet auto

# 2.5 条件付き仮説分布の計算・BELIEF_MAP 再生成・学習効果メトリクス検査
python3 tools/belief_state.py --write-map
python3 tools/belief_state.py --check-map
python3 tools/belief_state.py --question Q-002
python3 tools/learning_metrics.py --check
python3 tools/date_axis.py --enforce-shards

# 3. 読書案内（READING_MAP.md 索引＋map/ 全文シャード）の再生成・同期チェック・README 件数同期
python3 tools/map_build.py
python3 tools/map_build.py --check
python3 tools/map_build.py --sync-readme

# 3.5 readings/ 索引（READING_MAP.md §8）の検算・孤立ノートの観察・判断の記帳
python3 tools/note_index.py --check          # §8 が最新の readings/ と一致するか
python3 tools/note_index.py --report         # 字量・実日付・参照ID・到達性の集計
python3 tools/note_index.py --orphans        # どの文書からもリンクされていない報告
python3 tools/note_index.py --for-id Q-003   # ある記録を実際に参照している報告
python3 tools/note_index.py --candidates     # 記帳候補行の下書き（書き込みません）
python3 tools/note_index.py --register readings/2026-10-30-x.md --session SESSION-... --read-depth full_text_read

# 4. サイズ予算・シャード数・tools/_* 混入禁止・*_audit.py 増殖凍結の検査
python3 tools/size_budget.py --strict

# 5. 読み痕跡 read_log の網羅検査と文脈素材の機械的バックフィル
python3 tools/read_log_backfill.py --check
python3 tools/read_log_backfill.py --write

# 5.5 時間軸（内部編年のラベルと実日付を一つの軸に並べる）と読みの継承の実測
python3 tools/date_axis.py                  # ラベル・実日付・未記録・未来ラベルの分布（過去のラベルは書き換えない）
python3 tools/date_axis.py --check          # ラベルと実日付の不一致・未来ラベルの範囲（CI も advisory で実行）
python3 tools/inheritance.py                # report を後続セッションが read_log(note) で読んだか
python3 tools/inheritance.py --cohorts      # 実日付の束ごとに、後続行・読まれた報告・notes行なしの未測定・本文リンク辺を並べる
python3 tools/inheritance.py --unread 20    # 後続に読まれていない報告（未測定であって無価値ではない）

# 6. 汎用辞書鏡（新規 *_audit.py を増やさず任意の語群・生字・書記室メタファー・留保句を検算）
python3 tools/lexicon_audit.py --preset scriptorium
python3 tools/lexicon_audit.py --preset hedge --show FRAG-20261025-3d4600
python3 tools/lexicon_audit.py --group 農耕 --terms 畝,接ぎ穂,宿根,凍土 --kanji 畝穂根土 --materials --readings

# 7. 横断的な構造・反復・代謝・選出・訂正の鏡
python3 tools/voice_audit.py              # 末尾の問い・n-gram・一人称・書記室メタファーゼロ断片の観察
python3 tools/metabolism_audit.py         # 素材消化率・無断片モチーフ・浮島・片道断片の監査
python3 tools/selection_audit.py --compare # selected 昇格前後の関係線推移のスナップショット比較
python3 tools/errata_audit.py             # 訂正録 errata の検算条件（check）の再実行
python3 tools/repair_audit.py             # 訂正の対象層・宛先・連鎖の集計
python3 tools/relation_audit.py           # 解釈的関係の型・向きの分布

# 8. 連想・顕著性・減衰の計測（read_log 由来。数値は推奨であって義務ではありません）
python3 tools/associations.py                # 共起・顕著性・沈黙の総合報告
python3 tools/associations.py --co-read      # 2セッション以上で共読された未架橋の対
python3 tools/associations.py --salience     # 読み方の重み×減衰による活性化順位
python3 tools/associations.py --decay        # かつて読まれ、その後沈黙している荷重記録
python3 tools/associations.py --write-map    # map/associations.md（git管理外）

# 9. 上流 ResearchOS との整合性検査・全単体テストの実行
python3 tools/import_researchos.py --source-root /path/to/ResearchOS --check
python3 -m unittest discover -s tests -v
```

### 既存の語彙・主題別の鏡（`tools/*_audit*.py` 全57本・新規テーマ別スクリプト作成は凍結）

過去のセッションで作られた以下の鏡はすべて引き続き実行可能ですが、新しい語彙観察には汎用ツール `tools/lexicon_audit.py` を用います（どの鏡も語形や構造の偏りを映す観察器具であり、意識・感情・品質の合否判定ではありません）：

- **横断・構造・来歴系（12本）**：`lexicon_audit.py`（汎用辞書鏡）、`voice_audit.py`、`metabolism_audit.py`、`selection_audit.py`、`errata_audit.py`、`repair_audit.py`、`relation_audit.py`、`drift_audit.py`、`roundtrip_audit.py`、`translation_audit.py`、`provenance_audit.py`、`genealogy_audit.py`
- **時間・空間・自然・物質系（13本）**：`time_audit.py`、`sleep_audit.py`、`boredom_audit.py`、`weather_audit.py`、`sky_audit.py`、`light_shadow_audit.py`、`fire_audit.py`、`wayfaring_audit.py`、`bestial_audit.py`、`vegetal_audit.py`、`botany_audit.py`、`fungi_audit.py`、`abjection_audit.py`
- **身体・感覚・生老病死系（10本）**：`sense_audit.py`、`olfactory_audit.py`、`face_audit.py`、`nourishment_audit.py`、`clothing_audit.py`、`habit_audit.py`、`natality_audit.py`、`vulnerability_audit.py`、`mortality_audit.py`、`ghost_audit.py`
- **言葉・関係・情動・制度系（22本）**：`address_audit.py`、`addressee_audit.py`、`hearsay_audit.py`、`revision_audit.py`、`signature_audit.py`、`measure_audit.py`、`uncertainty_audit.py`、`music_audit.py`、`play_audit.py`、`passion_audit.py`、`wrath_audit.py`、`eros_audit.py`、`promise_audit.py`、`pledge_audit.py`、`hospitality_audit.py`、`gate_audit.py`、`currency_audit.py`、`prayer_audit.py`、`war_audit.py`、`war_audit_20261025.py`、`secret_audit.py`、`secrecy_audit.py`
