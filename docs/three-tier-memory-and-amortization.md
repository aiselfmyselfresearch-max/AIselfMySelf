# 三階層記憶アーキテクチャ（L0/L1/L2）・世代償却（`P_amort`）・エポック境界凍結

> **実装日**: `2026-11-25`（[`docs/memory-architecture.md`](memory-architecture.md) §1 で 2026-11-02 以来「未実装」とされていた `L0/L1/L2 の段階的読み込み` と `忘却・減衰` の制度的実装）
>
> **主要実装ファイル**: `tools/memory_tiers.py`, `tools/belief_state.py`, `tools/inspect_inquiry.py`, `tools/self_model.py`, `tools/validate_seed.py`, `tools/size_budget.py`, `schema/note.schema.json`, `docs/CONSOLIDATED_DIGESTS.md`, `state/digests.json`, `state/epoch_manifest.json`

---

## 1. 背景と問題設定：非忘却（追記専用保存）と有限トークン予算の緊張

本アーカイブは `state/`（12コレクションの追記専用 JSONL シャード）と `readings/`（精読・検証報告）を 1 バイトも書き換えず保持する。この**非忘却の原則**は、過去の誤り・反証・来歴の改ざんを防ぎ、任意の時点の主張を事後検算可能にする真正性の基盤である。

しかし、2026-11-25 時点の実測により、保存（availability）と作業記憶への検索（accessibility）を無階層のまま直結させた結果として次の3つの構造的ボトルネックが確認された：

1. **検索希釈とファイル数飽和**: 書庫総量約 `78 MiB` に対し、1セッションの起動パケットが実際に読めるのは `~0.16%` に過ぎない。初期シード期の未検証・未配線素材（活用率 `2.8%`）が全文検証済み一次資料（活用率 `64.2%`）と同じ平面に並び、`readings/` も `1,199 / 1,200` のハード上限直前に達していた。
2. **信念分布における `narrowed` 親仮説の死荷重固着**: 歴史的基底 `P_t` では、射程限定（`narrows_scope`）を受けて条件付き子仮説へ役割を引き渡したはずの親仮説が、`Q-002` で `99.36%`、`Q-003` で `99.32%`、`Q-001` で `39.63%` の確率質量を保持し続け、独立検証を通過した現役世代の競争が覆い隠されていた。
3. **スキーマ・時間軸の歴史的負債の累積**: 初期エポックのシャード群を毎回ゼロから現行エポックと同じ重さで走査・管理するコストが増大していた。

発達科学の実証知見——適応的認知オフローディング（Armitage et al. 2020, 2025; Liang et al. 2025）、幼児期健忘における新旧識別境界 M2 を境とした記憶様式の再編成（Uehara 2015）、単一の幹事実リマインダーによる休眠記憶の再統合（Varga, Stewart & Bauer 2016）、海馬損傷下のオンザフライ再構成の限界（Cooper et al. 2011）、選択前プロンプトによるアクセス可能性の回復（O'Connor et al. 2014）——はすべて、**「痕跡を消去すること」ではなく「生証跡の永続保存と、圧縮スキーマ・課題時検索キューの階層分離」こそが有限資源下の知性の解法である**ことを示している。

---

## 2. 柱1：三階層メモリアーキテクチャ（L0 / L1 / L2）

### 2.1 L0（コールド証跡層：Cold Evidence Archive）

- **対象**: `state/*.jsonl`・`state/*.d/*.jsonl` の全生行、および `readings/*.md` の全エピソード報告。
- **不変条件**: **削除・書き換えは一切行わない**（`append_only_check.py` がバイト単位で強制）。
- **決定論的分類（`memory_tiers.classify_materials` / `classify_notes`）**:
  - **素材 (`materials`)**: 非棄却仮説・評価行・ノート主張のいずれかに配線されているか、実効 `verified`（原典照合 depth 付きまたは現行エポック収蔵）の素材を `hot` とし、未検証かつ未配線の初期休眠素材（約 3,275 件）を `cold`（L0 休眠証跡）に分類する。`suppress_retrieval` 訂正付きは `suppressed` とする。
  - **精読ノート (`notes`)**: 現行エポック・仮説出典・高 salience（`>=3`）・異セッション手書き再読ありを `hot`、完了エポックの主張付きノートで L1 ドメイン・ダイジェストへ統合済みのもの（または明示 `memory_tier: "subsumed"` / `supersedes` 被置換）を `subsumed`、構造バックフィルのみの未参照旧行を `cold` に分類する。
- **幹事実リマインダー検索（Stem-Fact Cue Recall）**:
  - Varga, Stewart & Bauer (2016) に倣い、`cold` / `subsumed` に分類された記録も `python3 tools/memory_tiers.py --recall-cold "<検索語・著者・モチーフID>"` によって即座にオンデマンド検索でき、`inspect_inquiry.py --id <ID>` や `--include-cold` でいつでも作業記憶へ引き上げられる。

### 2.2 L1（統合スキーマ層：Consolidated Domain Digests）

- **対象**: 機械可読レジストリ `state/digests.json` と追跡 Markdown 文書 [`docs/CONSOLIDATED_DIGESTS.md`](CONSOLIDATED_DIGESTS.md)。
- **5つの統合ドメイン**:
  1. `DIGEST-A-HUMAN-DEV`: 人間発達・認知的オフローディング・記憶再編成と促された過去
  2. `DIGEST-B-AI-MEMORY`: AI記録自己・三門制御・証拠会計と世代償却
  3. `DIGEST-C-INTERFACE`: 人間×AIの非対称インターフェース・宛先・プロンプト循環
  4. `DIGEST-D-INFRA-INVARIANTS`: 制度的不変量・実日付時間軸・エポック境界凍結と予算規律
  5. `DIGEST-E-FALSIFICATION-FRONTIER`: 中心三問（`Q-001`〜`Q-003`）の世代償却（`P_amort`）現役反証フロンティア
- **並列安全性と運用**:
  - `Consolidator` ロールのセッションは、個別 `readings/` ファイルを際限なく増やす代わりに `python3 tools/memory_tiers.py --write-digests` を実行して L1 ダイジェストを更新し、必要に応じて `schema/note.schema.json` の `memory_tier: "subsumed"` / `consolidated_into: "DIGEST-..."` を追記できる。
  - CI（`memory_tiers.py --check`）は `state/digests.json` と `docs/CONSOLIDATED_DIGESTS.md` の完全一致・仮説参照整合・反証条項の非空を検証する。通常セッションが新しい台帳シャードを追記しただけで `CONSOLIDATED_DIGESTS.md` が競合を起こすことはない（海馬 L0 への即時記帳と新皮質 L1 の周期的コンソリデーションの分離）。

### 2.3 L2（ホット作業記憶パケット：`inspect_inquiry.py --packet ... --hot-only`）

- `python3 tools/inspect_inquiry.py --packet auto --hot-only --pair-policy amortized` を実行すると：
  1. 対象問いに対応する **L1 統合スキーマ・ダイジェスト（`## 2.5`）** を自動注入する。
  2. `§0.2` の仮説一覧を **世代償却 `P_amort` 上位 8 件の現役仮説＋未評価有効仮説** に圧縮し、棄却済み・`narrowed` 死荷重の詳細展開を省く（実測で `Q-002` パケットを `151.3 KB -> 77.2 KB`、`-49.0%` 圧縮）。
  3. `§3` の対話素材から L0 `cold` 素材を除外し、全文検証済み・配線済みの `hot` 一次文献にトークン予算を集中させる（`--include-cold` で全件復帰可能）。

---

## 3. 柱2：信念計算における世代償却（Generational Amortization: `P_amort`）

### 3.1 過去の再現性を壊さない並置設計

この書庫では、過去の報告やノートが引用した事後確率を遡及的に書き換えないことを原則とする。そのため、従来の `P_t`（セッション単位）、`P_sep`（対単位割引）、`P_lin`（系譜移流なし）、`P_gate`（三門制御）の計算式は 1 ビットも変更せず、第5の精錬基底として **`P_amort`（`amortized_posterior`）** および割当基底 **`amortized`** を横に並置（additive）した。

### 3.2 質量保存型の世代償却移譲則

同一の問い $Q$ に属する仮説集合を世代昇順（親→子→孫）に走査する。ある親仮説 $h_p$ に対し、同一問い内の系譜グラフ（`children_hypothesis_ids`）を辿って到達可能な**独立検証済み現役子孫仮説**の集合 $H_{\text{heirs}}(h_p)$ を次で定義する：

- `effective_status == "active"`
- `direct_eval_count >= 1` かつ `not self_evaluated_only`（提案セッション以外の独立評価を通過）
- `not retrieval_suppressed`

$H_{\text{heirs}}(h_p) \neq \emptyset$ のとき（すなわち、条件を引き継いだ現役子孫が独立検証を通過しているときに限り；子仮説を持たない `orphan_over_narrowed` 仮説の質量は勝手に消滅させない）：

1. $h_p$ が `narrowed` の場合、残存率を $\gamma = 0.10 \times 0.5^{\max(0, |H_{\text{heirs}}| - 1)}$ とする。
2. $h_p$ が `active` だが過限定（`narrows_scope > supports` かつ `narrows_scope >= 2`）の場合、残存率を $\gamma = 0.35$ とする。
3. 解放された確率質量 $\Delta m = m(h_p) \cdot (1 - \gamma)$ を $h_p$ から減じ、各継承子孫 $c \in H_{\text{heirs}}(h_p)$ へその基盤重み $w_c = P_{\text{gate}}(c) + 0.01$ に比例して**厳密に質量保存移譲**する。

この操作により、2026-11-25 実測において：
- `Q-001` の現役 `active` 質量比率は `60.3%`（`P_t`）→ **`98.2%`（`P_amort`）**
- `Q-002` の現役 `active` 質量比率は `0.65%`（`P_t`、⚠️読めない）→ **`98.3%`（`P_amort`、可読回復！）**
- `Q-003` の現役 `active` 質量比率は `0.69%`（`P_t`、⚠️読めない）→ **`97.5%`（`P_amort`、可読回復！）**

となり、`BELIEF_MAP.md` と `SELF_MODEL.md` §3 の双方で現役世代間の実質的対立軸が直ちに読み取れるようになった。

---

## 4. 柱3：エポック境界凍結（Epoch Boundary Freeze）

Uehara (2015) が縦断観察で示した「新旧識別（M2）成立後の検索様式の質的転換」に倣い、台帳の歴史を完了済み凍結エポックと現行アクティブ・エポックに区分する：

| エポック ID | 期間 | 状態 | 概要 |
|---|---|---|---|
| `epoch_0_seed_expansion` | `2026-10-22` 〜 `2026-10-31` | **Frozen** | 初期ベースファイル `state/*.jsonl` および 10月初期探索シャード群 |
| `epoch_1_three_gates_schema` | `2026-11-01` 〜 `2026-11-20` | **Frozen** | 条件付き仮説台帳・三門制御・実日付正規化期 |
| `epoch_2_six_layer_active` | `2026-11-21` 〜 現在 | **Active** | 六層自己モデル・全文検証・三階層記憶・世代償却期 |

- `python3 tools/memory_tiers.py --freeze-epochs` は、Frozen エポック（`<= 2026-11-20`）に属する全ベースファイルおよびシャード（計 `1,006` ファイル、`33,636` 行）のバイト数・行数・SHA-256 ダイジェストとコレクション別ロールアップ SHA-256 を `state/epoch_manifest.json` に固定する。
- 新規セッションは `>= 2026-11-21`（実日付）のシャードにしか追記しないため、`state/epoch_manifest.json` は並列ブランチ間で競合しない。
- `python3 tools/memory_tiers.py --check` が CI で毎回ロールアップ SHA-256 を高速検証し、`python3 tools/validate_seed.py --active-epoch-only` を使えば凍結エポックのハッシュ検証＋現行アクティブ・エポックのみの JSON Schema 行走査による高速増分チェックが可能となる。

---

## 5. 主要コマンド一覧

```sh
# 三階層記憶（L0/L1/L2）とエポック凍結の状態サマリー
python3 tools/memory_tiers.py

# L0 コールド／卒業証跡に対する幹事実リマインダー検索
python3 tools/memory_tiers.py --recall-cold "オフローディング"

# L1 ドメイン・ダイジェスト（state/digests.json & docs/CONSOLIDATED_DIGESTS.md）の再生成
python3 tools/memory_tiers.py --write-digests

# エポック凍結マニフェスト＆L1ダイジェストの整合検証（CI 実行）
python3 tools/memory_tiers.py --check

# エポック境界を用いた現行エポック高速スキーマ検証
python3 tools/validate_seed.py --active-epoch-only

# 世代償却（P_amort）＋ L2 ホット作業記憶モードでのセッション起動パケット生成
python3 tools/inspect_inquiry.py --packet auto --hot-only --pair-policy amortized
python3 tools/belief_state.py --question Q-002 --amortized
```
