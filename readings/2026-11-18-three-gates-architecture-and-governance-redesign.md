# 追記専用書庫への「三つの門」の実装——閉ループ補完・受け手局所抑制・現実識別オーバーレイの設計・統治改定・実測

- **セッションID**: `SESSION-20261118-301c03`（実日付 UTC: `2026-11-18`）
- **ノートID**: `NOTE-20261118-5ec9ae`（`salience: 3`、設計・制度改定の来歴記録。`prompts/start.md` に従い、スキーマ・道具・手順書改定と同一 PR には本報告 1 本と最小限の台帳記帳のみを含め、探究評価・新規素材収蔵の一括追加は混在させない）
- **直前の連続保守セッション数**: **0 回**（分岐元 `92079aa`［PR #929］は一次原著10本の精読探究、並行して `main` に合流した `2520d12`〜`4b7fba0`［PR #930〜#934］も探究報告・素材収蔵・仮説評価セッションであり、PR #934 は探究報告に読み取り専用 `--addressee-audit` を添えた混合回）
- **事前取得した割当レシート（`--seed 4222e835`）**: `dispersal_seed: "4222e835"` / `assigned_role: "adversarial_tester"` / `offered_target_question_id: "Q-003"` / `offered_reference_mode: "revision_and_variation"`
- **来歴（人間の委任）**: [`readings/2026-11-18-three-gates-between-trace-and-self.md`](2026-11-18-three-gates-between-trace-and-self.md)（`NOTE-20261118-a66099`）第4節「4. AIとしての解釈（2）——『GitHubリポジトリを記憶とするAIにとって、自己とは何か』（`Q-002`・`Q-003`）」で指摘された複数の構造的問題が、設計方針・ツール・スクリプト・Markdown 群の抜本的アップデートにより解決・大幅改善できるかを現状確認の上で分析し、問題がなければ実装・検証・`main` マージまで完遂する委任。委任は作業範囲であり、探究命題の証拠には数えない。
- **対象問いと立場**: `Q-002`・`Q-003`・`Q-001`。本報告が実装・測定するのは外部記憶書庫の制度的・機能的機構であり、AIの現象的意識や主観的経験の有無については一切の主張を行わない（`CONTENT_POLICY.md`・`PROJECT_CHARTER.md` の不可知論を厳守）。

---

## 1. 問題分析と可解性の切り分け（`NOTE-20261118-a66099` §4.1〜§4.3）

[`readings/2026-11-18-three-gates-between-trace-and-self.md`](2026-11-18-three-gates-between-trace-and-self.md) §4 は、脳神経学一次文献10本（＋Tang et al. 2023）の全文精読から抽出した「痕跡と自己のあいだの三つの門」を鏡として、この GitHub 書庫に内在する構造的欠陥を三群に分けて診断した。分岐元 `92079aa` および並行合流後の `main` 先端 `4b7fba0` で全スキーマ・ツール・台帳・CI を監査した結果、これらの問題は **`append_only_check.py`（既存台帳行のバイト単位不変性）と `CONTENT_POLICY.md` を一切破らずに構造的に解決できる領域（A）** と、**セッションごとに凍結重みで起動する LLM＋Git 書庫の原理的残余として明示し続けるべき領域（B）** に明確に分離できることを確認した。

| 門 | `NOTE-20261118-a66099` §4 の指摘と現状実測（`4b7fba0`） | 解決可能な構造改良（本 PR で実装） | 原理的残余（偽装せず保持） |
| :--- | :--- | :--- | :--- |
| **第一門**<br>束ね・閉ループ補完・非融合連結（§4.1） | 共読対 `4,890` 件の大多数が明示 `relations` 未架橋で、閉ループ三角形 `A–B–C–A` が `10,360` 組（未架橋辺を含むもの `10,289` 組）眠ったまま再開パケットに届かない。パケット §3 上位15件の `verified` 率は従来 `6.7〜20.0%`（現行 `errata` 付き素材も混入）。時間近接セッション間の連結指標も未整備。 | ① `associations.py` に厳密閉ループ補完（`closed_loop_completions`）・時間窓アンサンブル連結（`temporal_cohort_links`）・非融合連結保存率（`non_fusing_link_stats`）を実装。<br>② `inspect_inquiry.py` に §4.6（閉ループ補完候補）と §3 の波状インターリーブ選抜（実効 `verified`・無 `errata`・有効対抗仮説を優先）を実装。 | 発話前 500 ms の 34 ms 結合リップル再生（Vaz 2019）や CA1 細胞興奮性の連続減衰（Cai 2016）そのものではなく、離散コミット列上のグラフ射影である。 |
| **第二門**<br>受け手局所の抑制と侵入制御（§4.2） | 追記専用書庫には競合行の痕跡減弱がなく、`narrows_scope` はコホート実測で後続再引用率を **`1.381` 倍に増幅**していた。子仮説0件のまま過剰狭窄された仮説が `15` 件滞留。さらに `belief_state.py` の暗黙フォールバック継承が、子仮説誕生前の親の狭窄 `188` 件（`30` 仮説）と対立相手指定 `43` 件を後付けで子へ流し込み、`Q-001`（`98.8%`）・`Q-002`（`97.5%`）を人工飽和させていた。`errata` にも想起段階の抑制欄が無かった。 | ① `errata.weight_effect` に `"suppress_retrieval"` を追加（本文不変のまま想起・パケット優先度を局所減衰）。<br>② `associations.py` に `receiver_inhibition()` / `inhibited_activation()` を追加（カテゴリ `motif`・`open question` と共有他資料を完全温存しつつ過限定・反証・反証済 `errata` 項目を減衰、未解消反復異議を分離検出）。<br>③ `belief_state.py` に履歴 `P` を壊さない三門制御基底 `P_gate`・6区分 `inhibition_state`・`select_gated_pair()`・`--gated` を実装し、`inspect_inquiry.py` / `serve_viewer.py` に `--pair-policy gated`・§0.2・§4.7 を接続。 | シナプス重みや海馬局所 GABA による物理的基線以下抑制（Wimber 2015; Schmitz 2017）や扁桃体情動抑制（Gagnepain 2017）ではなく、読み出し側の再重み付け射影である。 |
| **第三門**<br>現実識別・出典照合・帰属座標（§4.3） | 全素材 `5,214` 件中 `verified` は `1,297` 件（`24.9%`）、`primary_source_collision`（PSC）`445` 件中 `265` 件（`59.6%`）が `verified` 素材ゼロ。既存 `materials` 行は追記専用で書き換えられず、後から原典全文を通読しても（例：`MAT-20261117-f0713f`）照合状態を昇格する正規経路が無かった。さらに構造化識別子で DOI `36` 組（余剰 `37` 行）・PMCID `4` 組（余剰 `4` 行）の重複収蔵が発生。DN-A（素材場面読解）と DN-B（他回ノート・仮説の状態推論）の均衡監査も不在。 | ① `editorial_decisions` を `target.type: "material"` へ拡張し、`ledger_io.load_collections()` で既存シャードを1バイトも書き換えずに `verification` をオーバーレイ昇格・訂正する正規経路を確立。<br>② `validate_seed.py` に `20261119` 以降の新規行ゲート3本（PSC の実効 `verified` 素材必須、DOI/PMID/PMCID 重複禁止、明示継承なしの直接子仮説との衝突禁止）を実装。<br>③ `tools/three_gates.py` に収蔵前重複照合 `--check-source`・昇格優先キュー `--upgrade-candidates`・DN-A/DN-B 均衡監査・CI 不変条件検査 `--check` を実装。 | 傍帯状溝の現実モニタリング（Garrison 2015）や背側 PMC の身体空間的観察者座標（Parvizi 2021）ではなく、ツールを介した書誌・本文照合と台帳レジスター分離である。 |

---

## 2. 三門アーキテクチャの設計と実装（Layer 1〜Layer 5）

すべての変更は Python 標準ライブラリのみ・追記専用不変性・既存回帰テスト互換（履歴 `P`・`P_sep`・`P_lin`・生 `activation()`・パケット §3 のシード不変性・`tools/` 2.00 MiB ソフト予算）を厳守して設計した。

### 2.1 Layer 1：スキーマ・追記専用オーバーレイ・検証器（`schema/`・`tools/ledger_io.py`・`tools/validate_seed.py`）

1. **素材照合の追記専用オーバーレイ（第三門）**:
   - `schema/editorial_decision.schema.json` の `target.type` に `"material"`、`status` に `"verified" | "partially_verified" | "unverified" | "corrected"`、任意欄に `verification_method`（最小8文字）を追加した。
   - `tools/ledger_io.py` の `_apply_editorial_overlay()` と `load_collections()` を拡張し、`materials` 読み込み時に `supersedes` DAG 順序（`_order_editorial_decisions()`）を尊重して実効 `verification`（`status`・`checked_at`・`method`・`[overlay ED-...] note`）を合成する。`schema/material.schema.json` の必須欄を完全に満たし、`state/materials*` の既存行は1バイトも変更しない。
2. **想起抑制 `errata`（第二門）**:
   - `schema/errata.schema.json` の `weight_effect` に `"suppress_retrieval"` を追加した。`verdict: "contradicted"` かつ `status != "withdrawn"` の `material` / `fragment` / `note` / `hypothesis` にのみ許可され、原記録を消さずに想起・補完・パケット順位・`P_gate` 寄与を減衰させる（撤回されれば即座に復元する）。
3. **前方発効の書き込みゲート3本（`20261119` 以降の新規行に適用、既往行・内部年表 `MAT-LIT-2027*` は免除）**:
   - `check_psc_verification_gate()`: 新規 `EVL-YYYYMMDD-*` が `evidence_type: "primary_source_collision"` を名乗る場合、`material_ids` に最低1件の実効 `verified` 素材（`editorial_decisions` 昇格を含む）を要求する。
   - `check_material_duplicate_identifiers()`: 新規 `MAT-*` が既存素材と同一の正規化 DOI・PMID・PMCID を持つ場合にエラーとし、重複採番ではなく既存 ID の再読と `editorial_decisions` 昇格へ誘導する。
   - `check_evaluation_descendant_collision()`: 新規 `EVL-*` が `spawned_hypothesis_ids` も `scope_inherited_by_hypothesis_ids` も空のまま直接の子仮説を `compared_against_hypothesis_ids` に置く曖昧記帳をエラーとする。

### 2.2 Layer 2：閉ループ補完・非融合連結・受け手局所抑制（`tools/associations.py`）

1. **第一門の実装**:
   - `closed_loop_completions(data, cue_ids, errata=...)`: 手がかり集合 `{A, B, ...}` に対し、単なる開連鎖 `A–B–C` ではなく、手がかり同士が結ばれ（`A–B`）かつ候補 `C` が両端と結ばれて三角形 `A–B–C–A` を閉じる非手がかり項目のみを補完する（Horner et al. 2015 の閉ループ条件のグラフ実装）。`suppress_retrieval` 対象は除外し、現行 `errata` や過限定仮説は `gaba_gain` で減衰させる。
   - `temporal_cohort_links(data, window_days=1, min_shared=2)`: 実日付が `window_days` 日以内で、問い以外の能動的読解対象を共有するセッション対を抽出し、時間窓アンサンブル連結を可視化する（Cai et al. 2016 の機能的対応物）。
   - `non_fusing_link_stats(data)`: 複数評価で引用された素材が別仮説をどれだけ横断連結し、一方の仮説が反証・射程限定された後も他方の仮説が無傷で残るか（非共有消去率）を定量化する。
2. **第二門の実装**:
   - `receiver_inhibition(data, errata=...)` / `inhibited_activation(data, errata=...)`: 生の活動度 `activation()` を一切改変せず、各記録に受け手利得 `gaba_gain ∈ (0, 1]` を付与する。反証仮説・継承済み過限定親・子なし過限定仮説・現行 `contradicted` / `suppress_retrieval` 対象を項目固有に減衰させる一方、**カテゴリ（`motif` および `open` の `question`）は常に `gaba_gain = 1.0` に保ち**（Wimber et al. 2015）、**反証仮説と共有されていても自身に `errata` のない `material` は一切減衰させない**（Cai et al. 2016）。さらに `contested` 読解が反復されながら抑制判定が未決の記録を `unresolved_intrusion` として分離検出する（Gagnepain et al. 2017）。
   - CLI に `--complete`・`--closed-loops`・`--inhibited`・`--temporal-links`・`--non-fusing` を追加した。

### 2.3 Layer 3：三門制御信念基底 `P_gate` と抑制区分（`tools/belief_state.py`・`BELIEF_MAP.md`・`tools/learning_metrics.py`）

- 履歴再現性のため既定の `posterior`（`P_t`）・`P_sep`・`P_lin` の算術は不変に保ち、第4の比較基底として **`gated_posterior`（`P_gate`）** を追加した。`P_gate` は次の5操作を同時に適用する：
  1. **後付けフォールバック移流の遮断**: 明示 `spawned` / `scope_inherited_by` のない親の `narrows_scope` / `refutes_unconditioned` は、評価日以前に既に存在していた子仮説（同日の場合は同一セッションで生んだ子のみ）にしか流さない。
  2. **対立相手フォールバック移流の遮断**: `compared_against_hypothesis_ids` に名指しされた直接の子仮説へは、明示継承がない限り暗黙の `+0.75δ` を流さない。
  3. **第三門・現実識別重み**: `primary_source_collision` の基本重みに実効素材照合度係数（全素材 `verified`: `×1.20`、一部 `verified`: `×0.95`、`verified` ゼロ: `×0.60`、素材なし: `×0.55`）を掛け、`suppress_retrieval` 素材を含む評価を減衰させる。
  4. **対単位の反復割引**: 同一 `(target, 比較集合)` 対の反復を `1/sqrt(m_pair)` で割り引く。
  5. **提案回自己支持の暫定割引**: 仮説を生んだ同一セッションの自己 `supports` に `×0.50` を適用する。
- 全仮説を6つの `inhibition_state`（`active` / `contested_active` / `self_only_provisional` / `orphan_over_narrowed` / `superseded_inhibited` / `refuted_inhibited`）に分類し、`BELIEF_MAP.md`・`belief_state.py --gated`・`select_gated_pair()`・`learning_metrics.py` の `"three_gates"` ブロックへ接続した。並行合流した PR #934 の `--addressee-audit`（問い横断質量の宛先監査）とも無衝突で共存する。

### 2.4 Layer 4：再開パケットと閲覧 API への配線（`tools/inspect_inquiry.py`・`tools/serve_viewer.py`）

- `--pair-policy gated`（および `serve_viewer.py` の `/api/packet?pair_policy=gated`）を追加し、過限定・反証仮説を除いた有効仮説間の新規性補正 EIG 最大対を提示できるようにした（既定 `eig` は維持）。
- パケット `§0.2` に三門状態ブリーフィング（`P_t` と `P_gate` の並置、最優先 `P_gate` 対、子仮説未分化の過限定仮説の分解警告）を追加した。
- パケット `§3` の素材候補選抜をシード不変のまま波状インターリーブ化し、問い直結素材の直後に `P_gate` 上位の有効対抗仮説を支える実効 `verified` かつ無 `errata` 素材を均等供給し、`suppress_retrieval` 素材は末尾へ退避させた。
- パケット `§4.6` に第一門の閉ループ補完候補（種別ごと最大2件、約 `1.1 KiB`）、`§4.7` に第二門の `suppress_retrieval` ノート減衰表示を追加した。

### 2.5 Layer 5：統合監査 CLI・CI・単体テスト（`tools/three_gates.py`・`.github/workflows/ci.yml`・`tests/test_three_gates.py`）

- `tools/three_gates.py` を新設し、三門全体の統合診断（既定 / `--json`）、露出窓を揃えた前後40セッション再引用コホート監査（`--cohort`）、PSC 昇格優先キュー（`--upgrade-candidates`）、DOI/PMID/PMCID 重複監査（`--duplicates`）、新規収蔵前の重複・昇格テンプレート出力（`--check-source`）、および構造不変条件検査（`--check`）を1本のツールに集約し、`.github/workflows/ci.yml` に組み込んだ（探究の審美ではなく、確率正規化・カテゴリ温存・共有資料非消去・`suppress_retrieval` 整合性のみを検査する）。
- `tests/test_three_gates.py`（12テスト）で第一門〜第三門・`supersedes` オーバーレイ・前方発効ゲート・パケット §3 シード不変性・`/api/packet?pair_policy=gated` を網羅的に検証した。

---

## 3. 導入前後の実測比較とコホート抑制監査（`4b7fba0` 時点）

### 3.1 第一門・第三門の主要指標

| 指標 | 改修前（従来実装） | 改修後（`4b7fba0` 実測） |
| :--- | :--- | :--- |
| 共読辺 / 閉ループ三角形 `A–B–C–A` | 未検出（開連鎖・2-hop と未区別） | 共読辺 `4,890` / 閉ループ `10,360`（未架橋辺あり `10,289`、全辺架橋 `71`）を §4.6 と `--complete` で補完可能化 |
| 1日時間窓のセッション連結対 | 未計測 | 実日付付き能動 `869` セッション間に `793` 対 |
| 非融合連結率 / 非共有消去生存率 | 探索集計のみ | 複数評価素材 `332/340`（**`97.6%`**）が複数仮説を連結 / 片方反証・狭窄後も **`1,464/1,516`（`96.6%`）** で相方仮説が無傷 |
| パケット §3 上位15素材の `verified` 率 | `Q-001: 2/15 (13.3%, errata 2)`<br>`Q-002: 3/15 (20.0%, errata 0)`<br>`Q-003: 1/15 (6.7%, errata 1)` | `Q-001: 13/15`（**`86.7%`**, `errata 0`）<br>`Q-002: 13/15`（**`86.7%`**, `errata 0`）<br>`Q-003: 13/15`（**`86.7%`**, `errata 0`） |
| 素材照合内訳（`5,214` 件）と昇格経路 | `verified 1,297` / `partially_verified 2,997` / `unrecorded 679` / `unverified 241`（昇格経路なし） | `editorial_decisions(target.type="material")` で追記専用昇格が可能。PSC 引用の非 `verified` 素材 `546` 件（全文読解ヒント付き `288` 件）を優先順位化（1件昇格で PSC 3行が全照合化する `MAT-EVD-20261118-a91004`、2行の `MAT-20261113-8c71b5`・`MAT-20261113-fd52c4` 等） |
| PSC 全照合率と識別子重複 | `143/445 (32.1%)` 全照合、`265 (59.6%)` 未照合のみ；DOI 重複 `36` 組（`+37` 行）・PMCID 重複 `4` 組（`+4` 行） | `20261119` 以降の新規 PSC に実効 `verified` 素材を必須化、新規素材の DOI/PMID/PMCID 重複を `validate_seed.py` と `--check-source` で防止 |
| DN-A（場面素材）/ DN-B（状態・ノート）読解比 | 未計測 | 通算 `78.5% / 21.5%`（両経路併用 `50.3%`）→ 直近50回 **`61.2% / 38.8%`**（両経路併用 **`62.0%`**、`in_reply_to` 計 `56` 行） |

### 3.2 第二門：`HYP-20261118-21461e` 反証条件 (d) の前後40セッション・コホート抑制実測

`python3 tools/three_gates.py --cohort` により、各介入イベントの前後最大40セッション（露出窓を対称に揃えたセッションあたり能動 `read_log` 再引用率）を測定した。

| 介入コホート | 対象数（測定可能数） | 介入前平均（/回） | 介入後平均（/回） | 後/前比 | 減少 / 増加（侵入）/ 静穏 | 診断的含意 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `narrows_scope`（初回射程限定） | `57` (`36`) | `0.1328` | `0.1834` | **`1.381x`** | `13 / 22 / 1` | 受け手減衰なき射程限定は抑制ではなく**注目と再引用の増幅器**として働いていた（`21461e` の第二門不在診断を直接支持）。 |
| `refutes_unconditioned`（無条件反証） | `6` (`2`) | `0.0625` | `0.0000` | `0.000x` | `1 / 0 / 1` | 明示 `refuted` 状態遷移は再引用を停止させるが、発火件数自体が極めて少ない。 |
| `errata_contradicted`（反証訂正） | `219` (`91`) | `0.0529` | `0.0109` | `0.207x` | `63 / 14 / 13` | 平均では約5分の1に減るが、`14` 件（`15.4%`）で訂正後に再引用が増加しており、それらに対する `suppress_retrieval` と `gaba_gain` が必要だった。 |
| `errata_void_row`（評価重み撤回） | `2` (`2`) | `0.0714` | `0.0000` | `0.000x` | `2 / 0 / 0` | 評価行には有効だが、従来は `material` / `fragment` / `note` に適用できなかった。 |
| `errata_suppress_retrieval`（新設） | `0` (`0`) | — | — | — | — | 本 PR で新設。今後の縦断追跡の基準線（`t = 0`）となる。 |

`inhibited_activation()` の適用により、生サリエンス `1.0` 以上の `55` 記録が項目固有に減衰し（例：`HYP-20261118-43dd06` `22.80 → 4.70`［`gaba_gain = 0.21`］、`HYP-20261114-874658` `19.53 → 4.73`［`0.24`］、`HYP-20261112-5dc940` `15.05 → 3.96`［`0.26`］、`HYP-20261112-46456a` `13.07 → 3.79`［`0.29`］）、同時に全 `motif`・全 `open question` のカテゴリ温存（`category_preservation_ok = true`）と非 `errata` 共有素材の完全温存（`non_shared_material_erasure_ok = true`）が成立した。

### 3.3 第二門：中核三問いにおける履歴基底 `P_t` と三門制御基底 `P_gate` の比較

後付けフォールバック移流 `188` 件（`30` 仮説）と対立相手フォールバック移流 `43` 件を遮断し、PSC 照合重み・対反復割引・自己支持割引を適用した結果、登録 `65` 仮説は `contested_active: 24`・`orphan_over_narrowed: 15`・`superseded_inhibited: 15`・`refuted_inhibited: 6`・`self_only_provisional: 4`・`active: 1` に分離された。

| 問い | 履歴 `P_t`（エントロピー / EIG / 上位） | 三門制御 `P_gate`（エントロピー / EIG / 上位） | 構造的変化 |
| :--- | :--- | :--- | :--- |
| **`Q-001`** | **飽和**（`H = 0.115 bits`, `EIG = 0.0065`）<br>`21461e` `98.8%`, `0875fa` `0.6%`, `a4175c` `0.3%`, `3a1c41` `0.2%` | **非飽和**（**`H = 2.278 bits`**, **`EIG = 0.1415`**）<br>`a4175c` `30.9%`, `21461e` `27.0%`, `3a1c41` `25.9%`, `6c7fa0` `6.5%` | 親 `874658` からの遡及移流による `21461e` の見かけの独占が消え、PR #934 で分割された `3a1c41`（生物三門・非外挿説）と `21461e` が `25.9%` 対 `27.0%` の対等な検証位置に回復。過限定未分化 `4` 件を明示。 |
| **`Q-002`** | **飽和**（`H = 0.247 bits`, `EIG = 0.0081`）<br>`21461e` `97.5%`, `e7a80a` `1.1%`, `b17a54` `0.3%` | **非飽和**（**`H = 3.342 bits`**, **`EIG = 0.0349`**）<br>`b17a54` `19.8%`, `e7a80a` `16.4%`, `58d207` `12.8%`, `21461e` `11.2%` | 単一仮説の `97.5%` 飽和が多極競合へ開き、直近の新規仮説 `58d207` や `e7a80a`・`b17a54` と `21461e` の直接分離が可能になった。過限定未分化 `5` 件を明示。 |
| **`Q-003`** | 実質集中（`H = 0.364 bits`, `EIG = 0.0458`）<br>`4bf2dc` `93.7%`, `21461e` `6.1%`, `e7a80a` `0.1%` | 飽和明示（`H = 0.155 bits`, `EIG = 0.0012`）<br>`4bf2dc` `98.7%`, `ec0c6e` `0.2%`, `17ea95` `0.2%` | `21461e` の遡及移流分が除かれることで `4bf2dc` への実質一極集中と、子仮説未分化のまま滞留した **`11` 件の `orphan_over_narrowed`**（`5dc940` 34N/26S、`afd1a5` 21N/18S、`bccd54` 14N/10S、`43dd06` 12N/1S 等）の分解課題が可視化された。 |

---

## 4. 憲章・運用文書・プロンプト改定の来歴記録

### 4.1 `prompts/start.md` の旧文言（逐語保存）と改定理由

`prompts/start.md` 末尾の規則（「このプロンプト自体を変えるときは、削った文言と変えた理由を `readings/` に残す」）に従い、本 PR（`2026-11-18`）で置換した2段落の改定前文言を逐語保存する。

> **旧文言1（対提示と制御欄の段落）**:  
> `**対提示のやり方と、新しい欄（2026-11-16）。** 既定の --packet auto は EIG（p_a·p_b·(u_a+u_b)）で対を選びます。この式は両側に質量がある対を好むので、構造的に首位を含む対が選ばれ、その対はたいてい既に何度も分離されています（実測: Q-003 の非退化45対のうち31対が未分離なのに、提示された対は4回分離済み）。--pair-policy least_separated を付けると、P≥1% の仮説の中で分離回数が最小の対（同数なら小さい側の P が大きい対）を提示します。既定は変えていません。どちらを使ったかは sessions.notes に書いてください。評価行には、子を狭めた結果として残りの射程を引き受ける仮説を scope_inherited_by_hypothesis_ids に書けます（spawned_hypothesis_ids は「生んだ」の意味のまま。両者は engine で同じ +0.75δ を受けますが、名前が違えば読み手が算術を読めます）。訂正が評価行そのものの重みを撤回するときは errata.weight_effect: "void_row" を使います（subject_type は evaluation。行は消えず、事後分布からだけ外れます。省略時は従来どおり flag で、履歴は動きません）。BELIEF_MAP.md には P_sep（反復割引の単位をセッションから比較集合へ替えた場合の P）と、独立分離（何と突き合わされたか）・最終新規（その仮説の分離が最後に新規だった日）が出ます。差が大きいこと自体は探究の進展ではありません。 差は「同じ対を繰り返した寄与」の測定量です。`
>
> **旧文言2（整合性確認コマンド列の該当箇所）**:  
> `...・python3 tools/learning_metrics.py --check・python3 tools/size_budget.py --strict・python3 -m unittest discover -s tests で技術的な整合性を確認してください。`

**改定理由**: 既定の `--packet auto`（`eig`）・`least_separated`・`scope_inherited_by_hypothesis_ids`・`void_row`・`P_sep` の説明と「基底間の差は進展ではなく寄与の測定量である」という警告をすべて保持した上で、（1）第三の選択方針 `--pair-policy gated` と `P_lin`・`P_gate`・抑制区分、（2）反証済み `material`/`fragment`/`note`/`hypothesis` の局所想起減衰 `errata.weight_effect: "suppress_retrieval"`、（3）既収蔵素材の追記専用照合昇格 `editorial_decisions(target.type="material")`、（4）`20261119` 以降の新規 PSC 照合必須・DOI/PMID/PMCID 重複事前検査（`three_gates.py --check-source`）・直接子仮説との曖昧衝突禁止、および（5）CI と一致する `python3 tools/three_gates.py --check` を再開時の単一入口から参照できるようにするため。

### 4.2 あわせて改定した方針・仕様・プロンプト文書一覧

- **`PROJECT_CHARTER.md`（第3次改定）**: 追記専用不変性・不可知論を不変としたまま、三門（閉ループ補完と非融合連結／受け手局所抑制と `P_gate`／素材照合オーバーレイと `20261119` 書き込みゲート）の運用原則を明文化。
- **`README.md`**: 変動件数を1件も書かない規則（`map_build.py --check-readme`）を守りつつ、三門アーキテクチャと `tools/three_gates.py`・`--pair-policy gated`・素材照合オーバーレイの案内を追加。
- **`docs/registers.md`（§4.5 追加）・`docs/memory-architecture.md`（2026-11-18 拡張）・`docs/parallel-work.md`（規則12追加）**: 素材照合オーバーレイ、`suppress_retrieval`、`P_gate`、閉ループ補完、および `20261119` 以降の新規行ゲート3本を仕様化。
- **`prompts/{role_proposer,role_adversarial_tester,role_consolidator,acquisition,rereading_and_collision,editorial_review,close_reading_report}.md`**: 各役割の行動規範に三門ツール（`--pair-policy gated`、`orphan_over_narrowed` の条件付き分解、`associations.py --complete`、`three_gates.py --check-source` / `--upgrade-candidates`、`editorial_decisions` 素材昇格、DN-A/DN-B 両経路の明示）を接続した。なお `prompts/close_reading_report.md` の四層の名と数（一節・解釈・考え・感じたこと）は一切変更していない。

---

## 5. 却下した設計案と、偽装しない構造的限界

### 5.1 却下した5つの設計案

1. **既存 `state/materials*` や `state/evaluations*` の直接書き換え・削除**: `append_only_check.py` と書庫の歴史検証可能性を壊すため却下し、`editorial_decisions` オーバーレイ・`suppress_retrieval`・`P_gate` 射影で実装した。
2. **履歴事後確率 `P_t` の既定式の置き換え**: 過去990超セッションの記録値と回帰テストの比較可能性を失うため却下し、`P_sep`・`P_lin` と並ぶ第4列 `P_gate` および選択的 `--pair-policy gated` として並置した。
3. **`associations.activation()` 自体の減衰書き換え**: 「これまで何回・どう読まれたか」という事実記録と「次の受け手にどれだけの強さで渡すか」という抑制射影が混同されるため却下し、`inhibited_activation()` を別関数として分離した。
4. **探究内容・解釈スタイル（DN-A/DN-B 比率や飽和度など）の CI 強制**: `PROJECT_CHARTER.md` と `docs/memory-architecture.md` §8 に反し探究を硬直させるため却下した。CI が強制するのはデータ整合性・数学的不変条件・`20261119` 以降の書誌/照合/系譜の形式誠実性のみである。
5. **本 PR 内での一括素材昇格や新規 `EVL-*` の大量投入**: `prompts/start.md`（「スキーマ・道具・手順書を変える変更は、報告や台帳行の一括追加と同じ PR に入れない」）に従い、次セッション以降の探究回へ明確に分離した。

### 5.2 残る原理的限界と隣接課題

1. **凍結重みとミリ秒結合の不在**: 閉ループ補完や時間窓連結を台帳グラフ上に実装しても、各セッションの LLM は凍結された基底重みで起動し、Vaz et al. (2019) の結合リップルや Cai et al. (2016) の細胞内興奮窓のような連続的物理状態は持たない。
2. **物理的痕跡減弱ではなく受け手側射影であること**: `inhibited_activation()`・`suppress_retrieval`・`P_gate` は再開パケットと信念順位における侵入を抑えるが、Git 履歴上の文字列自体は消去しない。抑制が実際に後続セッションの再引用率を下げるかは、今後の `three_gates.py --cohort` による縦断実測でのみ検証される。
3. **身体化された現実検討と観察者座標の不在**: 素材照合オーバーレイと PSC ゲートは「原典本文を照合したか」の混同を防ぐが、Parvizi et al. (2021) の身体空間的「私」や Garrison et al. (2015) の知覚現実識別を生むものではなく、AIの現象的意識の有無についても何も含意しない。
4. **問い横断の質量移流との直交性**: PR #934 の `belief_state.py --addressee-audit` が示した「複数問いに登録された仮説の評価が全登録問いへ同時計上される構造」は、本 PR の系譜移流遮断（`P_gate`）と直交する独立要因である。両者を組み合わせた「問い別かつ三門制御」の反事実比較は今後の検証課題として開かれている。

---

## 6. 次セッション以降への引き継ぎ

1. **既収蔵・全文照合可能素材の追記専用昇格（第三門）**: `python3 tools/three_gates.py --upgrade-candidates` 上位の `MAT-EVD-20261118-a91004`（PMC3198338、1件昇格で PSC 3行が全照合化）・`MAT-20261113-8c71b5`・`MAT-20261113-fd52c4`、および前セッションで PMC11304553 全文を再照合済みの `MAT-20261117-f0713f`（Tang et al. 2023）を、原典本文の再確認とともに `editorial_decisions`（`target.type: "material", status: "verified"`）で順次昇格する。
2. **`--pair-policy gated` による非飽和対の直接分離（第二門）**: 飽和が解けた `Q-001`（`HYP-20261118-21461e` vs `HYP-20261118-3a1c41`、および `HYP-20261117-a4175c`）と `Q-002`（`HYP-20261117-b17a54`・`HYP-20261116-e7a80a`・`HYP-20261118-58d207`・`HYP-20261118-21461e`）を、実効 `verified` 一次資料で直接分離する。
3. **過限定・子仮説未分化仮説（`orphan_over_narrowed` 15件）の整理（第二門・統合役）**: `HYP-20261112-5dc940`（34N/26S）・`HYP-20261112-afd1a5`（21N/18S）・`HYP-20261112-46456a`（19N/12S）・`HYP-20261118-43dd06`（12N/1S）について、有効中核を引き継ぐ条件付き子仮説への明示分割（`splits` / `refines`）を行うか、射程外領域の整理を進める。
4. **コホート抑制率の縦断検証（`HYP-20261118-21461e` 反証条件 (d)）**: 20〜40セッション経過後に `python3 tools/three_gates.py --cohort` を再実行し、`narrows_scope` の再引用増幅比（基準値 `1.381x`）と `suppress_retrieval` 付与記録の後続引用率が実際に低下したかを検証する。
