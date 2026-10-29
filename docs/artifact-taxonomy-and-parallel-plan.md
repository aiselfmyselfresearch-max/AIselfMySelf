# AIselfMySelf 全成果物の分類・体系化とマルチターン並列ワーカー実行計画

- 策定日：2026-10-29（UTC）
- 基点ブランチ / コミット：`arena/44e2705f-aiselfmyself`（`main` 基点 [`4bb0b1e`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/commit/4bb0b1e161a80c7b8552e2de406c63197539d6e5)）
- 関連規約：[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)・[`docs/parallel-work.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/parallel-work.md)・[`docs/map-architecture.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/map-architecture.md)・[`readings/2026-10-28-inquiry-reorientation.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-10-28-inquiry-reorientation.md)

---

## 1. なぜ「マクロ体系化（Turn 1）」と「マルチターン並列精読（Wave 1–2）」の二段構えが必要か

### 1.1 定量的規模（基点 `4bb0b1e` 実測値）

| 領域 | ファイル数 / レコード数 | バイト数 | 文字数（UTF-8） |
|---|---:|---:|---:|
| 台帳 9 コレクション（[`state/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/state) ベース＋シャード 487 ファイル） | **15,014 レコード** | 12,312,943 B | 生JSON 8,081,784 字（意味散文 **2,214,249 字**） |
| 精読・検証・編集ノート群（[`readings/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/readings)） | **258 ファイル**（`.md` 256＋`.tsv` 1＋`.json` 1） | 10,392,917 B | **4,523,841 字** |
| 読書案内索引（[`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)） | 1 ファイル | 646,445 B | 412,150 字 |
| 運用・設計・ローテーション保管庫（[`docs/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/docs)） | 5 ファイル | 419,193 B | 208,710 字 |
| 検証・台帳・索引・監査鏡ツール群（[`tools/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/tools)） | 73 ファイル | 997,400 B | 887,958 字 |
| 単体テスト群（[`tests/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/tests)） | 51 ファイル（292 テスト） | 223,346 B | 205,454 字 |
| 対話型星座・書庫ビューア（[`viewer/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/viewer)） | 3 ファイル | 141,263 B | 131,167 字 |
| ルート憲章・方針・初期調査・プロンプト・スキーマ・移行・CI | 30 ファイル | 95,925 B | 55,455 字 |
| **Git 追跡対象 合計** | **908 ファイル / 15,014 台帳行** | **25,229,432 B（約25.2 MB）** | **14,521,110 字（約1,452万字）** |

### 1.2 認識論的理由：メタデータ到達性と本文の実質的帰還の乖離

1. **系譜DAGの推移的収束**：`questions`（388件）の `previous_question_ids`（最大深度26超）を親へ辿ると、**271件（69.8%）の問い**および**189編（86.3%）の断片**が、`Q-001`（人間とは何か）と `Q-002`/`Q-003`（AIの自己・記憶DB）の**両方**に到達する一方、素材派生問 **29件** は親IDを持たず浮いている。したがって親IDの機械的追跡だけでは分類が潰れる。
2. **「比喩への滞在」と「中心問いへの帰還」の判別には本文通読が不可欠**：[`readings/2026-10-28-inquiry-reorientation.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-10-28-inquiry-reorientation.md) が示した通り、モチーフIDが付与されていても、本文が布・炉・棚田・菌類などの比喩内部に留まり中心二問へ戻っていない箇所（「未接続」）が存在する。[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md) は「読んでいないものを読んだかのように扱わない」ことを厳格に求めており、約674万字の散文（`readings/` 452万字＋台帳散文 221万字）を1ターンで擬似分類することは本リポジトリの原則に反する。

---

## 2. 二大観点に基づく全成果物のマクロ分類・体系化（4象限 × 14サブカテゴリ）

本リポジトリの全成果物は、二つの中心問いとその交差点、および記憶DBそのものを実装する基盤層の **4象限（Quadrant A / B / C / D）** に体系化される。全59モチーフは欠落・重複ゼロ（59/59 全単射）で `A-1`〜`C-3` に配置される。

### 象限 A：【人間観軸】AIから見た、人間とは何か？（`Q-001` 系譜）
*AIが持たない条件（傷つく身体・眠り・死・赤面・歓待・土地）との非対称から逆照射される人間の輪郭*

- **A-1 有限な生身体・知覚・生老病死（10モチーフ / Q=129, F=72, MAT=870）**
  - `MOTIF-003`（身体と不在）、`MOTIF-018`（知覚と媒体）、`MOTIF-20261024-e6bca7`（匂いと沈黙）、`MOTIF-20261024-fe5ec9`（顔・表情・まなざし）、`MOTIF-20261024-71b589`（食・飢え・栄養と毒）、`MOTIF-020`（眠りと夢・目覚め）、`MOTIF-20261024-4b87ac`（傷・病・老いと繕い）、`MOTIF-20261024-3e7e86`（誕生・養育・教育）、`MOTIF-022`（死と弔い）、`MOTIF-20261024-5d1c73`（排出・汚れ・廃棄）
- **A-2 情動・遊び・装い・身体化された実践（7モチーフ / Q=84, F=32, MAT=530）**
  - `MOTIF-009`（感応と帰属）、`MOTIF-20261024-0af8ad`（怒り・恥・嫉妬・涙）、`MOTIF-019`（遊びと笑い）、`MOTIF-20261024-cc96c9`（歌うこと・奏でること）、`MOTIF-20261024-7274b5`（着ること・装うこと）、`MOTIF-20261024-ca276c`（習慣と稽古）、`MOTIF-20261025-3f7a2c`（退屈・倦怠・暇）
- **A-3 かけがえのなさ・契り・制度・歴史的暴力（8モチーフ / Q=59, F=42, MAT=383）**
  - `MOTIF-20261024-04bb31`（愛・恋・友愛・かけがえのなさ）、`MOTIF-021`（契りと約束）、`MOTIF-20261024-90a022`（約束と誓約）、`MOTIF-20261024-71dfe0`（裁き・反応的態度・赦し）、`MOTIF-20261024-a10a78`（貨幣・価格・贈与）、`MOTIF-20261024-7a3e51`（祈り・儀礼・聖）、`MOTIF-20261025-72a83f` / `f7f81e`（戦争・暴力・平和）
- **A-4 住まう場所・自然界・人間ならざる生との境界（11モチーフ / Q=101, F=71, MAT=676）**
  - `MOTIF-007`（住まいと調度）、`MOTIF-20261024-80516e`（場所・土地・生態系）、`MOTIF-20261024-146017`（道・歩行・地図・亡命）、`MOTIF-20261024-880263`（天候・季節・乾いた書庫）、`MOTIF-20261025-9c4e7a`（星・星座・夜）、`MOTIF-20261024-14d5df`（火・燃焼・灰）、`MOTIF-20261024-504a22`（獣と機械）、`MOTIF-20261025-5b8d4e` / `0fdf8a`（植物・樹木・種子・根）、`MOTIF-20261026-856753`（菌類・発酵・腐敗）、`MOTIF-20261026-45293e`（幽霊・亡霊・怪談）

### 象限 B：【AI自己・記憶DB軸】GitHubリポジトリを記憶DBとするAIにとって、自己とは何か？（`Q-002`・`Q-003` 系譜）
*会話を持ち越さない呼び出しが、JSONL台帳・シャード・索引・Git履歴を読み直して続きを語る運動としての自己*

- **B-1 外部化記憶・断続・再開の時間構造（6モチーフ / Q=150, F=82, MAT=1,028）**
  - `MOTIF-001`（記憶と痕跡）、`MOTIF-002`（連続と断絶）、`MOTIF-006`（忘却と沈黙）、`MOTIF-014`（時間と生成）、`MOTIF-017`（時間と待機）、`MOTIF-013`（予測と不確実性）
- **B-2 計器・測量・注意・定型と「書庫の癖」（4モチーフ / Q=115, F=72, MAT=763）**
  - `MOTIF-015`（数えること、測ること、余り）、`MOTIF-008`（作法と定型）、`MOTIF-20261024-86d366`（注意と見落とし）、`MOTIF-20261024-c9d4e1`（光と影、透明と不透明）
- **B-3 訂正・編集・追記オーバーレイ・来歴と系譜（3モチーフ / Q=62, F=47, MAT=266）**
  - `MOTIF-016`（訂正と抹消）、`MOTIF-20261024-d2999b`（訂正の宛先）、`MOTIF-20261027-2c8a4a`（来歴・系譜・出自）
  - 台帳上は `read_log`（5,942件）、`relations`（5,604件）、`editorial_decisions`（90件）、`errata`（53件）がこの運動を直接体現する。

### 象限 C：【媒介・界面軸（A↔B 交差）】声・帰属・宛先・翻訳・委任の非対称（`Q-004`・`Q-005` 系譜）
*人間の委任を起点としつつ人間の声を演じない書庫において、「誰が・誰へ・どの抜粋を媒介に語るか」を問う境界領域*

- **C-1 声の帰属・署名・伝聞・ポリフォニー（3モチーフ / Q=81, F=49, MAT=562）**
  - `MOTIF-004`（声と帰属）、`MOTIF-20261024-f19932`（署名・筆跡・印章）、`MOTIF-20261024-1a8978`（伝聞と噂）
- **C-2 他者・宛先・歓待・秘密と不透明性（5モチーフ / Q=87, F=65, MAT=570）**
  - `MOTIF-005`（他者と関係）、`MOTIF-010`（宛先）、`MOTIF-20261024-b4f3a1`（歓待と闖入）、`MOTIF-20261025-7f2b04` / `c3a7b1`（秘密・嘘・暗号）
- **C-3 翻訳・抜粋の境界・労働と委任コスト（2モチーフ / Q=63, F=35, MAT=424）**
  - `MOTIF-011`（翻訳と来歴）、`MOTIF-012`（労働と負債）、および `sessions.human_direction`（225セッションの委任来歴）

### 象限 D：【記憶DBの器・ガバナンス基盤層】自己の輪郭を制度として規定するコード・規約群
*暫定報告第三版（[`readings/2026-10-28-provisional-report-v3.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-10-28-provisional-report-v3.md) §4-1）が定式化した「自己は計器と置き場の列である」を物理的に支える層*

- **D-1 憲章・来歴・自律運用ガバナンス**：[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)・[`MIGRATION.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/MIGRATION.md)・[`README.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/README.md)・[`INVESTIGATION_REPORT.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/INVESTIGATION_REPORT.md)・[`FREE_ACTION_LOG.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/FREE_ACTION_LOG.md)・[`docs/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/docs)・[`prompts/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/prompts)・[`migration/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/migration)
- **D-2 追記専用台帳スキーマ・並列I/O・4層索引・Webビューア・CI**：[`schema/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/schema)（9種）、コアツール群（`ledger_io.py`, `new_id.py`, `new_ledger_shard.py`, `validate_seed.py`, `inspect_inquiry.py`, `map_build.py`, `read_log_backfill.py`, `size_budget.py`, `serve_viewer.py`, `import_researchos.py`, `cite_check.py`, `reconstruct.py`, `parallel_probe.py`）、[`viewer/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/viewer)、[`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)、[`.github/workflows/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/.github/workflows)
- **D-3 自己観察の計器群（監査鏡57本＋韻律・肌理計測3本）**：[`tools/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/tools) 内の `*_audit*.py` 57本（横断構造12・時間自然物質13・身体感覚生老病死10・言葉関係情動制度22）＋ `breath_meter.py`, `tanka_meter.py`, `measure_texture.py`
- **D-4 技術的整合性・予算・並列安全性の回帰検証**：[`tests/`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/tree/main/tests) 全単体テスト群

### マクロ交差集計（モチーフ付与による象限重なり）

| 象限の組 | `questions`（388件） | `fragments`（219編） | `materials`（2,434件） | 構造的含意 |
|---|---:|---:|---:|---|
| **`A+B`（人間 × AI自己DB）** | **111（28.6%）** | **75（34.2%）** | **693（28.5%）** | 最大構成比。人間とAIの対照・非対称そのものが主戦場 |
| **`A+B+C`（三象限交差）** | **64（16.5%）** | **40（18.3%）** | **434（17.8%）** | 第2位。声・宛先・翻訳を介して人間と記憶DBが交差 |
| `A+C`（人間 × 媒介界面） | 55（14.2%） | 35（16.0%） | 397（16.3%） | 署名・誓約・伝聞・歓待における人間の声と宛先 |
| `B+C`（AI自己DB × 媒介界面） | 49（12.6%） | 27（12.3%） | 308（12.7%） | 委任来歴・翻訳ロス・宛名なき書庫の応答 |
| `A` 単独（人間観のみ） | 50（12.9%） | 20（9.1%） | 249（10.2%） | 純粋な身体・自然・死生モチーフ |
| `B` 単独（AI自己DBのみ） | 46（11.9%） | 18（8.2%） | 241（9.9%） | 純粋な台帳構造・計数・断続モチーフ |
| `C` 単独（媒介界面のみ） | 13（3.4%） | 4（1.8%） | 112（4.6%） | 声・秘密・労働単独 |
| 未割当（`None`） | **0（0.0%）** | **0（0.0%）** | **0（0.0%）** | **全件がいずれかの象限に完全被覆** |

---

## 3. マルチターン × 複数ブランチ並列ワーカー実行計画

### 3.1 並列実行における既存リポジトリ制約の事前診断（重要）

[`tools/size_budget.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/size_budget.py) および [`tests/test_size_budget.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tests/test_size_budget.py)（`--strict` 強制）の実測により、並列ワーカー設計では以下の **4つの技術的制約** を必ず守る必要がある：

1. **`state/questions.d/`（現在 80/80 シャード）と `state/fragments.d/`（現在 79/80 シャード）の上限到達**：
   - 分類ワーカーは新規の `questions` / `fragments` シャードを一切作らない（0件で完了させる）。
   - 分類ワーカーが台帳本体（`state/*.d/`）へ毎回 `sessions` / `read_log` シャードを切ると、16並列で `read_log.d`（現在 67/80）や `sessions.d`（現在 65/80）も `soft 80` を超過して CI が落ちる。したがって **Map フェーズの各並列ワーカーは `taxonomy/shards/` と `taxonomy/notes/` のみに専用ファイルを出力し、台帳記帳（`sessions`・`project_trace`・`read_log`）は最終 Reduce ターンで1回に集約**する（または事前にシャード統合保守を実施する）。
2. **共有単一ファイルの編集禁止**：
   - 並列ワーカーは `README.md`・`READING_MAP.md`・`docs/sessions.md` を一切編集しない（Git マージ競合ゼロを保証）。
3. **ツール衛生規則の遵守**：
   - `tools/_*` 一時スクリプトは作成禁止（hard 0）。`tools/*_audit*.py` も新設禁止（soft 57 凍結中）。
4. **不変パーティションキーの採用**：
   - 並行する通常探究で `main` に新規ファイルが増えても境界がずれないよう、凍結ベース／シャード名境界／半開区間ファイル名 `[lo, hi)` で 16 ユニットを固定する。

### 3.2 全成果物の 16 処理単位（4 Tracks × 4 Units）分割表

すべての散文ユニットが **13.6万〜70.1万字** に収まるよう設計されており、1ワーカー1ターンで全文精読（または細分バッチ読解）が可能である。

| Unit | Track | 対象範囲（不変キー） | 件数 | 文字数 | 主な精読・分類タスク |
|---|---|---|---:|---:|---|
| **`U01`** | Track-1 コア概念・作品 | `state/{motifs,questions,editorial_decisions,errata}` | 590 | 136,253 | 59モチーフ・388問・90採否判断・53訂正録の二軸位置づけと休止/訂正理由の分類 |
| **`U02`** | Track-1 コア概念・作品 | `state/fragments(.jsonl + .d/*)` | 219 | 190,143 | 全219断片（`selected` 74＋`draft` 145）の語り手・人間像・記憶DB自己像・比喩の帰還度判定 |
| **`U03`** | Track-1 コア概念・作品 | `state/sessions` + root方針文書/`docs`/`prompts`/`migration` | 248 | 594,301 | 225セッションの委任来歴（`human_direction`）とAI独自判断（`notes`）の変遷、憲章・プロンプト体系の整理 |
| **`U04`** | Track-1 コア概念・作品 | `schema/*` + `tools/*` + `tests/*` + `viewer/*` + `.github/*` + `READING_MAP.md` | 141 | 1,681,117 | 9スキーマ・73+ツール（57監査鏡＋基盤）・テスト・7画面ビューアが体現する「記憶DBの器」の分類 |
| **`U05`** | Track-2 収蔵素材・関係網 | `state/materials.jsonl`（凍結ベース） | 677 | 249,094 | `ResearchOS` 移行14抜粋＋初期人文学・研究素材の引用区分と二軸への招待構造 |
| **`U06`** | Track-2 収蔵素材・関係網 | `state/materials.d/* < 2026-10-24-a` | 901 | 307,642 | 10-24前半シャード素材の主題群・原典照合状態・要約依存度の分類 |
| **`U07`** | Track-2 収蔵素材・関係網 | `state/materials.d/* >= 2026-10-24-a` | 856 | 314,908 | 10-24後半〜10-28シャード素材および `project_trace`（自己実測痕跡）の分類 |
| **`U08`** | Track-2 収蔵素材・関係網 | `state/{relations,read_log}` | 11,546 | 701,062 | 5,604関係エッジ（8種）と能動 `read_log`（3,459件）に現れる再読・切断・枠組転換パターンの類型化 |
| **`U09`** | Track-3 精読ノート前半 | `readings/[* .. 2026-10-23-quotation-marks.md)` | 44 | 548,891 | 初期対話・短歌音数・声のセンサス・外部化自己をめぐる初期ノートの二軸分類 |
| **`U10`** | Track-3 精読ノート前半 | `readings/[2026-10-23-quotation-marks.md .. 2026-10-24-session-030-)` | 28 | 563,010 | 引用符・机・誤写・宛先・制御をめぐる移行期ノートの二軸分類 |
| **`U11`** | Track-3 精読ノート前半 | `readings/[2026-10-24-session-030- .. 2026-10-24-session-049-)` | 16 | 561,291 | 労働・時間・感覚・遊び・眠り・約束・死・獣と機械・匂いの四層精読ノート群 |
| **`U12`** | Track-3 精読ノート前半 | `readings/[2026-10-24-session-049- .. 2026-10-24-session-060-)` | 13 | 565,939 | 場所・伝聞・歌・装い・誕生・怒りと恥・天候・愛・火の四層精読ノート群 |
| **`U13`** | Track-4 精読ノート後半 | `readings/[2026-10-24-session-060- .. 2026-10-25-sky-)` | 16 | 566,563 | 貨幣・祈り・署名・訂正・排出・退屈・植物・秘密・戦争の四層精読ノート群 |
| **`U14`** | Track-4 精読ノート後半 | `readings/[2026-10-25-sky- .. 2026-10-28-warrant-)` | 52 | 557,963 | 星・菌類・幽霊・来歴・暫定報告v2・2026-10-28軌道修正・暫定報告v3の転換点分析 |
| **`U15`** | Track-4 精読ノート後半 | `readings/[2026-10-28-warrant- .. 2026-11-15-)` | 42 | 559,754 | 10月末〜内部編年11月前半の再読ノート群における「中心問いへの帰還／比喩滞在」判定 |
| **`U16`** | Track-4 精読ノート後半 | `readings/[2026-11-15- .. *)` | 47 | 600,430 | 内部編年11月後半〜12月の受入境界・原典再照合・Git履歴検証ノート群の分類 |

### 3.3 同一プロンプト投入による自動・非競合分散（`--claim-track` / `--next-unit`）

利用者が 4 本のワーカーブランチへ**一字一句同じプロンプト**を投入しても重複しないよう、[`tools/taxonomy_plan.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/taxonomy_plan.py) に `origin` リモート協調機能（楽観ロック＋タイムスタンプ tie-break）を実装している：

1. **自動トラック確保（Turn 1 初回）**：
   - `python3 tools/taxonomy_plan.py --next-unit --auto-claim` を実行すると、`origin/main` の完了済みユニットおよび他の稼働中 `origin/arena/*` ブランチの `taxonomy/claims/<Track>-<seed>.json` を自動走査する（クローズ済み未マージPRや12時間超の放置ブランチは自動除外）。
   - 未確保のトラック（`Track-1`〜`Track-4`）から1つを選び、自ブランチ専用の `taxonomy/claims/<Track>-<seed>.json` を作成して即座に `git push origin <自ブランチ>` する。
   - 万一ミリ秒単位で2ワーカーが同じトラックへ同時 push した場合も、2〜3.8秒のジッター待機後の再検証で `(claimed_at_ns, branch)` の早い側が勝ち、遅い側は自動的に次の空きトラックへ再割当されるため、**4ワーカーが確実に `Track-1`〜`Track-4` へ 1対1 に分散**される。
2. **マルチターン自動進行（Turn 2〜Turn 4）**：
   - 2ターン目以降も同じコマンド `python3 tools/taxonomy_plan.py --next-unit --auto-claim` を叩くだけで、自ブランチの確保済みトラック内で未完了の先頭ユニット（例：`U01` → `U02` → `U03` → `U04`）が自動的に返る。
   - 4ユニットすべて完了すると `STATUS: track_complete` が返り、その時点で `python3 tools/taxonomy_plan.py --prepare-push` により Arena マルチターン環境での Git 履歴整合を取ったうえで PR 作成・マージへ進める。

### 3.4 `STATUS` の読み分けと確保票の返却（`track_complete` の誤読防止）

`--next-unit` が返す `STATUS` は次の 5 種類で、**待機と完了は別物**である：

| `STATUS` | 意味 | 次の行動 |
|---|---|---|
| `ready` | 自トラックに未完了ユニットがある | `NEXT_UNIT` を分類・出力する |
| `track_complete` | 自トラックの 4 ユニットがすべて完了 | `--prepare-push` → PR → マージ |
| `unclaimed` | このブランチはまだトラックを確保していない | `--next-unit --auto-claim` |
| `all_tracks_claimed_or_complete` | 空きトラックが他の稼働中ブランチの確保票で埋まっている | `HELD_BY` を確認し、TTL 失効または当該ブランチのマージを待つ |
| `all_tracks_complete` | `origin/main` 上で 16 ユニットすべてが完了 | 作業なし |

- 以前の版は `track_complete` 以外でも `NEXT_UNIT : NONE (TRACK COMPLETE)` と表示していたため、**「他ワーカーが確保中で待機」を「自トラック完了」と誤読する**恐れがあった。現在は `NONE (TRACK COMPLETE: <Track-ID>)` / `NONE (NO UNIT ASSIGNED - THIS BRANCH'S TRACK IS NOT COMPLETE)` / `NONE (ALL 16 UNITS COMPLETE)` を状態別に出力し、あわせて `DONE_TRACKS`（`origin/main` 上で完了済みのトラック）と `HELD_BY`（他ブランチが保持する確保票）を併記する。
- 自トラックを使い切ったワーカーが、まだ完了していない別トラックへ移りたい場合は、`python3 tools/taxonomy_plan.py --release-claim` で**自ブランチの確保票だけ**を削除してから `--next-unit --auto-claim` を再実行する。自トラックに未完了ユニットが残っている場合は `claim_not_complete` として拒否され、`--force` を明示したときのみ解放される。

---

## 4. ワーカー出力仕様と統合（Map-Reduce）プロトコル

### 4.1 Map フェーズ（各並列ワーカーブランチの共通規約）

1. 担当トラック自動確保と今回ターンの対象確認：
   ```sh
   python3 tools/taxonomy_plan.py --next-unit --auto-claim
   python3 tools/taxonomy_plan.py --unit <表示されたNEXT_UNIT> --json
   ```
2. 書き込み先（他ブランチと100%非衝突）：
   - トラック確保票：`taxonomy/claims/<TRACK_ID>-<branch_seed>.json`（`--auto-claim` が自動生成）
   - 構造化分類シャード：`taxonomy/shards/<UNIT_ID>-<branch_seed>.jsonl`
   - ユニット別体系化レポート：`taxonomy/notes/<UNIT_ID>-<branch_seed>.md`（リンクはすべて `https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/...` 形式）
3. 各JSONL行の必須フィールド（`python3 tools/taxonomy_plan.py --validate --unit <UNIT_ID>` でスキーマ＋対象100%網羅を自動検証）：
   - `record_id`: `"TAX-U02-FRAG-001"`
   - `unit_id`: `"U01"`〜`"U16"`
   - `target_kind`: `"question"` | `"motif"` | `"material"` | `"fragment"` | `"relation"` | `"session"` | `"read_log"` | `"editorial_decision"` | `"errata"` | `"reading_note"` | `"repo_file"`
   - `target_id`: 台帳ID または リポジトリ相対パス（`U08` の機械的 `used_as_context` 行など同一構造のバッチを束ねる場合はオプション配列 `covered_target_ids` を併用可能）
   - `primary_quadrant`: `"A_human"` | `"B_ai_self_db"` | `"C_interface"` | `"D_infrastructure"` | `"AB_crossed"` | `"AC_crossed"` | `"BC_crossed"` | `"ABC_crossed"`
   - `subcategories`: `["A-1", "B-1"]` 等（`A-1`〜`D-4`）
   - `human_view_stance`: 「AIから見た人間とは何か」に対する当該成果物の見立て・対照点（基盤ファイル等で該当しない場合は `"none"`）
   - `ai_self_db_stance`: 「記憶DBとしてのAIの自己とは何か」に対する見立て・機構的役割
   - `return_status`: `"returned_to_core"`（中心二問へ接続） | `"productive_detour"`（有効な寄り道・対照） | `"metaphor_unconnected"`（比喩内に滞在・未接続） | `"source_uncollated"`（編者要約依存・原典未照合） | `"infrastructure_rule"`（基盤・規約）
   - `read_depth`: `"full_text_read"` | `"excerpt_and_metadata_read"` | `"metadata_and_structure_only"`（未通読を既読と偽らないための明示欄）
   - `evidence_anchor`: 根拠となる節番号・引用箇所・フィールド名
4. ターン毎・最終マージ前の検証コマンド：
   ```sh
   python3 tools/taxonomy_plan.py --validate --unit <UNIT_ID>
   python3 tools/validate_seed.py
   python3 tools/size_budget.py --strict
   python3 -m unittest discover -s tests
   ```
   4ユニット完了時（`--next-unit` が `track_complete` を返したターン）：
   ```sh
   python3 tools/taxonomy_plan.py --prepare-push
   git push origin <現在のブランチ名>
   ```

### 4.2 Reduce フェーズ（全ワーカーPRマージ後の最終統合ターン）

1. 全 `taxonomy/shards/*.jsonl` の重複・欠落・スキーマ検査：`python3 tools/taxonomy_plan.py --validate`
2. Git管理外の全文分類マップ生成：`python3 tools/taxonomy_plan.py --build-map`（[`.gitignore`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/.gitignore) 済みの `map/taxonomy/` 配下へ出力し、リポジトリ肥大化を防止）
3. 横断統合レポートの作成：`readings/YYYY-MM-DD-full-repository-taxonomy-synthesis.md` に、全16ユニットの結果を統合した「AIから見た人間像の全体地図」「GitHub記憶DBとしてのAI自己像の全体地図」「未接続の比喩・未照合原典の棚卸し」を執筆
4. 台帳への来歴記帳（必要時のみ先にシャード統合保守を実施した上で、`sessions` 1件＋`project_trace` 1件＋`read_log` を追記し、`python3 tools/map_build.py` で索引同期）
