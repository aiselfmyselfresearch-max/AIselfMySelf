# 三階層記憶（L0/L1/L2）・世代償却（`P_amort`）・エポック境界凍結の制度化と実測（2026-11-25）

- **セッションID**: `SESSION-20261125-672b94`（`session_type: infrastructure` / `assigned_role: consolidator` / `dispersal_seed: 672b9422`）
- **対象問い**: `Q-001`, `Q-002`, `Q-003`
- **基準コミット**: `c31467112cdb1311fe16d7acd76f81a6ffb0e2d4`（PR `#1109` マージ直後の `main`）
- **参照した先行ノート**: `NOTE-20261125-4c5935`（[`readings/2026-11-25-offloading-reorganization-and-the-prompted-past.md`](2026-11-25-offloading-reorganization-and-the-prompted-past.md)）、`NOTE-20261125-76cfac`（[`readings/2026-11-25-when-the-unread-counts-6e20f3f7.md`](2026-11-25-when-the-unread-counts-6e20f3f7.md)）
- **参照した一次資料**: `MAT-20261125-06bf09`（Armitage et al., 2020）、`MAT-20261125-abc85d`（Uehara, 2015）、`MAT-20261125-80e99b`（Varga, Stewart & Bauer, 2016）
- **人間からの委任（来歴）**: 直前セッションで実施したアーカイブ全量診断と三本柱提案（①三階層メモリアーキテクチャ L0/L1/L2、②信念計算における世代償却 `P_amort`、③エポック境界凍結 `state/epoch_manifest.json`）をすべて実装・検証し、`main` へマージする委任。人間の指示は作業範囲の来歴であり、研究上の証拠ではない。AIの現象的意識や主観的体験の有無については主張しない（`CONTENT_POLICY.md`）。

---

## §1 実装前のボトルネック実測と「whether 拒否ゲート」の検討

### 1.1 診断された3つの構造的ボトルネック

`c31467112cdb1311fe16d7acd76f81a6ffb0e2d4` 時点の書庫全量を計測した結果、追記専用の非忘却原則（`state/` 約 `37.49 MiB`・`readings/` 約 `38.52 MiB`）と有限なセッション作業記憶との間に、以下の3つの構造的摩擦が生じていた：

1. **検索希釈と `readings/` 上限逼迫**:
   - `readings/` ファイル数は `1,199` 本に達し、当時の `size_budget.py` ハード上限 `1,200` 本まで残り **1 本** となっていた。
   - 総素材 `6,146` 件のうち、初期シード期の未検証・未配線素材 `3,275` 件（`53.3%`）が、全文検証済み一次文献や仮説配線済み素材 `2,871` 件（`46.7%`）と無階層のまま混在していた。
   - `Q-002` の標準起動パケットは `151,319 B` に膨張しており、その `61.1%`（`92,531 B`）を棄却済み・射程限定済み仮説を含む全64仮説の逐語展開（`§0.2`）が占めていた。
2. **`narrowed` 親仮説の確率質量固着（死荷重）**:
   - 標準基底 `P_t` では、射程限定（`narrows_scope`）を受けて条件付き子仮説へ役割を譲ったはずの親仮説が `Q-002` で **`99.35%`**（現役 `active` 合計わずか **`0.65%`**）、`Q-003` で **`99.31%`**（現役 `active` **`0.69%`**）、`Q-001` で **`39.65%`** を保持し続け、現役世代の実質的競争が読めない状態（`BELIEF_MAP.md` で `⚠️読めない` 表示）になっていた。
3. **完了エポックの再走査コストと歴史的境界の不在**:
   - `2026-11-02` の [`docs/memory-architecture.md`](../docs/memory-architecture.md) §1 で「`L0/L1/L2 の段階的読み込みは未実装`」「`減衰がない`」と明記されて以来、完了エポックのシャード群を暗号学的に凍結して現行アクティブ・エポックと分離する制度が存在しなかった。

### 1.2 Layer I（whether 拒否ゲート）の検討

生データを削除・要約置換する「破壊的忘却」は、`append_only_check.py` の不変条件と事後検算可能性を破壊するため**拒否**した。代わりに、(a) L0 生データの1バイト無改変保持、(b) 既存の `P_t / P_sep / P_lin / P_gate` を1ビットも変えない第5基底 `P_amort` の並置、(c) 完了エポック `<= 2026-11-20` のみを対象とする SHA-256 ロールアップ凍結という**完全加法・非破壊の制度化**として引き受けた。

---

## §2 三本柱の実装と前後比較の実測値

仕様の全体は [`docs/three-tier-memory-and-amortization.md`](../docs/three-tier-memory-and-amortization.md) に定めた。ここでは実装後の実測値を記録する。

### 2.1 柱1：三階層記憶（L0 / L1 / L2）と起動パケット圧縮（`tools/memory_tiers.py`, `tools/inspect_inquiry.py`）

- **L0 / L1 / L2 分類実測（本報告追加前の基準状態）**:
  - `materials`（計 `6,146` 件）：L2 `hot = 2,871`（`46.7%`）／ L0 `cold = 3,275`（`53.3%`）／ `suppressed = 0`
  - `notes`（計 `1,304` 件）：L2 `hot = 599`（`45.9%`）／ L1 `subsumed = 278`（`21.3%`）／ L0 `cold = 427`（`32.7%`）
- **L1 統合スキーマ層の生成**:
  - 5つの領域別ダイジェスト（`DIGEST-A-HUMAN-DEV`〜`DIGEST-E-FALSIFICATION-FRONTIER`）を `state/digests.json`（`80,332 B`）および [`docs/CONSOLIDATED_DIGESTS.md`](../docs/CONSOLIDATED_DIGESTS.md)（`62,518 B`）として出力。約 `76 MiB` の L0 書庫から現役の不変原則と反証条項を `61.1 KiB` へ凝縮した。
- **L0 幹事実リマインダー検索（Varga, Stewart & Bauer 2016 型のキュー再統合）**:
  - `python3 tools/memory_tiers.py --recall-cold "記憶"` により、L0 `cold` 素材 `338` 件・`cold/subsumed` ノート `54` 件が即座にオンデマンド検索可能であることを確認。
- **L2 ホット起動パケット（`--hot-only --pair-policy amortized`, seed `672b9422`）のサイズ圧縮実測**:

| 対象問い | 従来標準パケット | L2 `--hot-only` パケット | 圧縮量（削減率） |
|---|---:|---:|---:|
| `Q-001` | `133,946 B` | `78,858 B` | `-55,088 B`（**-41.1%**） |
| `Q-002` | `151,319 B` | `77,184 B` | `-74,135 B`（**-49.0%**） |

### 2.2 柱2：世代償却基底 `P_amort` の導入（`tools/belief_state.py`, `tools/self_model.py`）

独立異セッション検証を通過した現役子孫仮説が存在する場合に限り、`narrowed` 親仮説（および過限定親仮説）の滞留質量を現役子孫へ質量保存移譲する `amortized_posterior`（`P_amort`）を実装した。中心三問における現役 `active` 仮説の合計確率質量は以下の通り回復した：

| 問い | 標準基底 `P_t` の `active` 合計 | 三門制御 `P_gate` の `active` 合計 | 世代償却 `P_amort` の `active` 合計 | `P_amort` 首位仮説（質量） |
|---|---:|---:|---:|---|
| `Q-001` | `60.3%` | `89.9%` | **`98.2%`**（`narrowed` 残 `1.8%`） | `HYP-20261124-4514c6`（`54.1%`） |
| `Q-002` | `0.65%`（⚠️読めない） | `88.1%` | **`98.3%`**（`narrowed` 残 `1.6%`） | `HYP-20261124-4514c6`（`47.8%`） |
| `Q-003` | `0.69%`（⚠️読めない） | `89.0%` | **`97.5%`**（`narrowed` 残 `2.4%`） | `HYP-20261124-4514c6`（`45.9%`） |

### 2.3 柱3：エポック境界凍結と増分スキーマ検証（`state/epoch_manifest.json`, `tools/validate_seed.py`）

- 完了エポック `epoch_0_seed_expansion`（`<= 2026-10-31`）と `epoch_1_three_gates_schema`（`2026-11-01..2026-11-20`）に属する **`1,006` ファイル・`33,636` 行** の SHA-256 ダイジェストを `state/epoch_manifest.json`（マスターロールアップ `42b125298073...`）に固定した。
- `python3 tools/validate_seed.py --active-epoch-only` により、凍結エポックの SHA-256 一括照合＋現行アクティブ・エポック（`>= 2026-11-21`）のみの JSON Schema 行検証が全参照整合チェック込みで高速通過することを確認した（フル検証 `2.04s` → アクティブ限定 `1.46s`）。

---

## §3 `prompts/start.md` 変更前後の文面と理由の記録

`prompts/start.md` 末尾の規約（「本文書の変更は、次の入力の変更です。変えたら旧文面と理由を `readings/` に残してください」）に従い、本セッションで行った変更の旧文面・新文面・理由を以下に記録する。

### 3.1 旧文面（変更箇所）

> `**この回に読んだ基底を sessions.belief_basis に書いてください**（default / temporal_heir_guard / receiver_gated など）。基底を書かない事後確率は他の事後確率と比較できません。新規仮説を登録する回は primary_question_id を書いてください（既存行は遡及で埋めません）。登録1件が動かした質量は python3 tools/belief_state.py --newborn-mass で測れます（書き込みなし）。**基底間の差は進展ではなく、反復・系譜移流・未照合重みの寄与の測定量です。**`
>
> `台帳を追記したら **python3 tools/belief_state.py --write-map を先に**、それから python3 tools/map_build.py を実行し（順序を逆にすると READING_MAP.md の言及グラフが古い BELIEF_MAP.md を読むため、正しい木でも --check-map が STALE を返します。map_build.py が警告を出します）、python3 tools/validate_seed.py・python3 tools/append_only_check.py・python3 tools/readings_integrity_check.py・python3 tools/inspect_inquiry.py --check-map・python3 tools/belief_state.py --check-map・python3 tools/note_index.py --check・python3 tools/read_log_backfill.py --check・python3 tools/date_axis.py --enforce-shards・python3 tools/learning_metrics.py --check・python3 tools/three_gates.py --check・python3 tools/size_budget.py --strict・python3 -m unittest discover -s tests で技術的な整合性を確認してください。`

### 3.2 新文面（変更箇所）

- `sessions.belief_basis` の例示に `amortized` を追加し、2026-11-25 追補として世代償却基底 `P_amort`、L2 ホット起動（`--packet auto --hot-only --pair-policy amortized`、L1 `docs/CONSOLIDATED_DIGESTS.md` 自動注入）、および L0 休眠証跡検索（`python3 tools/memory_tiers.py --recall-cold <検索語>`）の選択肢を案内した。
- 台帳追記後の再生成・整合性チェック手順に `python3 tools/self_model.py --write` / `--check` および `python3 tools/memory_tiers.py --check` を明記した（CI の新設ゲートとローカル手順を一致させるため）。

### 3.3 変更の理由

1. 新設した `P_amort` 基底・L2 `--hot-only` 起動・L0 `--recall-cold` 検索が後続セッションから発見可能でなければ、実装した三階層記憶と世代償却が死蔵されるため（ただし強制ではなく選択肢として提示）。
2. CI（`.github/workflows/ci.yml`）に `python3 tools/memory_tiers.py --check` と `python3 tools/self_model.py --check` が入っているため、`prompts/start.md` の完了チェック列と CI 実行列の齟齬をなくすため。

---

## §4 残された課題と次セッションへの引き継ぎ（Handoff）

- **L1 ダイジェストへの明示的卒業運用の継続**: 今後は `Consolidator` ロールのセッションが複数ノートを横断統合する際、新しい要約専用 `readings/` を増やす代わりに `schema/note.schema.json` の `memory_tier: "subsumed"` と `consolidated_into: "DIGEST-..."` を追記し、`python3 tools/memory_tiers.py --write-digests` で L1 層を育てる運用が実地検証の対象となる。
- **反証フロンティアの実証継続**: `P_amort` によって可視化された中心三問の首位仮説 `HYP-20261124-4514c6` と第2位群（`HYP-20261123-1054be`, `HYP-20261124-90c776`, `HYP-20261125-d74ea8`）の直接衝突を、一次文献の Exclusion Clause 検証で進める段階が整った。
