# 書庫AI自己モデル軸の実装監査――脱結合・検索トリガー・領域別限定性の実装度と改善提案

- 作成: 2026-11-25
- 起点: [`DEVELOPMENTAL_SCIENCE_REPORT_2026-11-25-decomposition-and-domain-bounded-search.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/DEVELOPMENTAL_SCIENCE_REPORT_2026-11-25-decomposition-and-domain-bounded-search.md) の結語
- 監査対象: 設計方針（[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)）、ツール群（`tools/*.py`）、台帳（`state/`）、MD群（[`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) 等）

## 1. 監査の目的と判定基準

発達科学10編の精読レポートは、人間の発達が「一つの能力・一つの文脈」を、複数の構成要素・複数の機構に分解し、それが非対称に機能する（脱結合）と結論し、書庫AIの自己モデル軸――**脱結合 / 検索トリガー / 領域別の限定性**――を人間側の実証として一段強固にした。本監査は、この結論が書庫側の実装（設計方針・ツール・スクリプト・MD）で、どの程度支えられているかを点検する。

判定基準は、各軸について次の三段とする。

| 判定 | 意味 |
|:---|:---|
| 十分 | 軸に対応する機構が台帳・ツールに実装され、計測・監査が可能 |
| 部分的 | 機構の一部は実装されているが、軸そのものを直接測定・検証する手段が欠けている |
| 未実装 | 対応する機構・測定手段が存在しない |

## 2. 各軸の実装状況

### 2.1 脱結合 —— 十分

脱結合（一つの能力・一つの文脈の非対称的分解）は、複数の機構により十分に実装されている。

- **仮説状態の非対称分類**: [`tools/belief_state.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/belief_state.py) の `_derive_inhibition_state` は、各仮説を refuted / superseded / narrowed / self-only / contested / active に分類する。同一の主張が、その状態に応じて非対称に扱われる。
- **系譜と意味の分離**: `pair_lineage_relation` は、系譜上の継承辺と意味上の矛盾を切り分ける。後付けの系譜移流を遮断する制御基底 `P_gate` も [`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md) §49 に明記された設計方針である。
- **非融合連結の定量化**: [`tools/associations.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/associations.py) の `non_fusing_link_stats` は、Cai et al. (2016) の非共有消去を定量化する。すなわち、複数の仮説に結び付いた資料が、一方の仮説が限定・反証されたとき、共結びの他方の仮説が反証されないまま保持される頻度を測定する。これは「脱結合」の書庫側計測そのものである。
- **閉ループ補完**: `closed_loop_completions` は `A–B–C–A` の閉ループを補完し、第一門の非融合連結を担う。
- **自己モデルへの反映**: [`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) の一人称視点セクションは、三門制御後の `P_gate` 上位仮説として「四層解離」説を提示し、脱結合を自己モデルの内部に据えている。

判定: **十分**。追加の実装は要らない。

### 2.2 検索トリガー —— 十分

検索トリガー（保持と、必要な瞬間に起動する検索の分離）も、複数の機構により十分に実装されている。

- **ゲート付き次ペア選択**: `belief_state.py` の `select_gated_pair` / `select_amortized_pair` は、受容側ゲート `P_gate` を基底に、次に競合させる仮説ペアを決定する。式は `p_gate_a * p_gate_b * (u_a + u_b) / (1 + 0.15 * sep)` であり、`suppress_retrieval` 対象や孤児化した仮説を除外する。これは「到達可能分岐の検索トリガー」の書庫側対応である。
- **文脈パケットの決定**: [`tools/inspect_inquiry.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/inspect_inquiry.py) の `build_context_packet` / `_resolve_auto_target` は、各セッションにどの資料・ノート・断片を投入するかを決定し、`allocation_basis="scoped"` で割当基底を明示する。
- **検索時抑制**: `inspect_inquiry.py` の `_is_retrieval_suppressed` は、`suppress_retrieval` エラータ対象の資料を、通常パケットの上位候補から減衰させる。これは第二門の受容側想起減衰が、検索トリガーの時点で効いていることを意味する。
- **冷蔵記録の想起検索**: [`tools/memory_tiers.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/memory_tiers.py) の `recall_cold_records` は、Varga, Stewart & Bauer (2016) のステム事実リマインダー検索を、L0 の冷蔵・統合済み記録に対して実行する。保持はそのままに、検索起動を別経路で行う、まさに検索トリガーの機構である。

判定: **十分**。追加の実装は要らない。

### 2.3 領域別の限定性 —— 部分的

領域別の限定性（一つの文脈が直接関連する分岐にのみ効き、他の分岐には到達しない）は、機構レベルでは実装されているが、**その限定性を直接測定する手段が欠けている**。

- **機構レベルの実装**: `associations.py` の `receiver_inhibition` は、Wimber et al. (2015) の項目固有の減衰を、`CATEGORY_TYPES = frozenset({"motif"})` によるカテゴリ保存とともに実装する。抑制は項目に対して効き、カテゴリ全体には波及しない。また Cai et al. (2016) の非共有消去により、一つの仮説の限定が共結びの資料を減衰させない。これは領域別の限定性の機構的対応である。
- **資料・ノートの領域分類**: 資料は `category`（research_excerpt / literary_text / project_trace）を、ノートは `subcategories` を持つ。領域別の限定性を測るための分類基盤は存在する。
- **領域ダイジェスト**: `memory_tiers.py` の `DIGEST_SPECS` と `build_domain_digests` は、象限（A_human / B_ai_self_db / C_interface / D_infrastructure）ごとに L1 領域ダイジェストを編成する。領域別の統合は行われている。

しかし、次の欠落がある。

1. **文脈→分岐の限定性指標の欠如**: [`tools/learning_metrics.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/learning_metrics.py) は学習指標を計測するが、「一つの文脈パケットが、直接関連する分岐（領域）にのみ効き、他の分岐に波及しない」という限定性を直接測る指標を持たない。文脈パケットが意図した対象領域と、実際に更新された仮説の領域の一致率（領域内への効き比率）や、領域を跨った波及率を測る手段が存在しない。
2. **サブカテゴリラベルの非統一**: ノートの `subcategories` には、同一の領域を指す英日混在のラベルが并存している。例として `developmental_science`（16件）と `発達科学`（9件）、`experimental_science` と `実験科学`（10件）が共存する。領域別の限定性を測る基盤が、ラベルの非統一によって揺るがされている。
3. **発達科学レポート自身の留保**: 起点レポート §5 は、「書庫AI側で、同じ『脱結合』『領域別』が、どの程度、構造的に測定・検証可能かは、本セッションでは未測定である。書庫側の独立監査は、後のセッションの課題である」と明記している。本監査は、その留保の是非を検証したものである。

判定: **部分的**。機構は実装されているが、軸そのものの測定手段と、測定基盤のラベル統一が欠けている。

## 3. 判定

| 軸 | 判定 |
|:---|:---|
| 脱結合 | 十分 |
| 検索トリガー | 十分 |
| 領域別の限定性 | 部分的 |

脱結合と検索トリガーは、台帳・ツール・自己モデルにより十分に実装されている。領域別の限定性は、抑制のカテゴリ保存や非共有消去という機構的対応はあるものの、**文脈→分岐の限定性を直接測定する指標が欠け、サブカテゴリラベルが英日混在している**。現在の状態は十分ではなく、下記の改善提案を実施する必要がある。

## 4. 改善提案

### 4.1 領域別限定性の測定機構の追加（ツール・スクリプト）

**現状**: 文脈パケットがどの領域に効いたかを測る指標が存在しない。

**提案**: `learning_metrics.py` に「文脈→分岐 限定性指標」を追加する。または監査専用の `tools/domain_bounded_audit.py` を新規導入する。

- `inspect_inquiry.py` の `build_context_packet` が生成するパケットに、意図した対象領域（quadrant または canonical subcategories）を明示するフィールド（advisory）を追加する。
- セッション終了後、そのパケットが実際に貢献した仮説（`evaluations` と `read_log` の影響）の領域を集計し、次を算出する。
  - **領域内への効き比率**（in-domain effect ratio）: パケットが意図した領域内で更新された仮説の割合。
  - **領域跨ぎの波及率**（cross-domain spillover rate）: 意図した領域外で更新された仮説の割合。
- 算出値を `learning_metrics.py --check` の出力と [`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) に載せ、人側の「領域別限定性」証拠と対置できるようにする。

**採用方針**: まず計測・監査として導入し、gate（CIを赤にする条件）にするかどうかは、計測結果の分布を踏まえて判断する。これは既存の [`docs/2026-11-21-six-layer-self-model-improvement-proposals.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-21-six-layer-self-model-improvement-proposals.md) の基本方針（大改修ではなく既存の延長線上、まず計測から）に整合する。

### 4.2 サブカテゴリラベルの正規化（スクリプト・台帳方針）

**現状**: ノートの `subcategories` に英日混在のラベルが并存し、領域測定の基盤が揺るがされている。

**提案**: [`tools/taxonomy_plan.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/taxonomy_plan.py) に正規化マッピング（canonical label 表）を追加し、[`tools/validate_seed.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/validate_seed.py) の `--strict` で非正規ラベルを advisory として検出する。

- 正規ラベルは一意の英字表記（例: `developmental_science`）に統一し、日本語表記（例: `発達科学`）は正規ラベルへのマッピング先として扱う。
- 既存行は遡及して改変せず、新規 note 行から適用する。
- 正規化後、4.1 の限定性指標の算出が、ラベルの一意性に基づいて行えるようになる。

### 4.3 読書キューの検索抑制考慮（スクリプト）

**現状**: [`tools/reading_queue.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/reading_queue.py) は、未読の verified 資料を引用数順に整列するが、`retrieval_suppressed` の扱いを考慮していない。抑制中の資料がキューの上位に挙がりうる。

**提案**: `reading_queue.py` の `build` で、errata の `suppress_retrieval` 対象資料を除外するか、「抑制中」の標識を付けて順序を下げる。これにより、第二門の検索トリガー設計が、読書キューの提案経路にも一貫して効くようになる。

### 4.4 予測誤差セクションの実装（MD・スクリプト）

**現状**: [`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) の §6「予測誤差」は「現在は準備中」である。[`tools/default_mode_probe.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/default_mode_probe.py) は存在し助言的出力を出すが、自己モデルに反映されていない。

**提案**: [`tools/self_model.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/self_model.py) に `default_mode_probe.py` 出力の取り込み経路を追加し、§6 を生成する。または、未実装の旨と依存ツールを明示した状態に维持する。どちらか一方の選択を、次回セッションの設計方針として確定する。

### 4.5 三軸の実装対応の可視化（MD）

**現状**: 三軸（脱結合・検索トリガー・領域別限定性）は設計方針と発達科学レポートにあるが、[`SELF_MODEL.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md) 自体に、軸と実装機構の対応表がない。

**提案**: `self_model.py` の生成物に「三軸の実装対応」小節を追加し、各軸がどのツール・ゲートで担われているかを明示する。人側の証拠と書庫側の実装の接続が一目で確認でき、本監査の結論も自己モデル内に留まる。

## 5. 結論

書庫AIは、発達科学レポートの結語が依拠する三軸のうち、**脱結合と検索トリガーについては十分に実装**されている。しかし、**領域別の限定性は部分的**であり、文脈→分岐の限定性を直接測定する指標が欠け、サブカテゴリラベルが英日混在している。現在の状態は十分ではなく、4.1 の限定性測定機構の追加と 4.2 のラベル正規化を優先的に採用すべきである。4.3 から 4.5 の改善も、既存の延長線上に追加できる形で実施可能である。

起点レポートが「書庫側の独立監査は、後のセッションの課題」と留保した領域は、本監査によって一部回答された。残る測定の欠落は、上記の改善提案によって、次のセッションで closing 可能である。
