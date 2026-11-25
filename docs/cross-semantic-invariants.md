# 交差意味的不変量と予測誤差アラーム（Cross-Semantic Invariants & Prediction-Error Alarms）

本仕様書は、単一ファイルの JSON スキーマ検査（構文妥当性）だけでは検出できない**台帳間の意味的矛盾・暗黙の無更新停滞・記憶再構成による疑似逐語引用（作話）**を機械的に検知・遮断する、リポジトリ横断の**交差意味的不変量（予測誤差アラーム）**の設計を定義する。

---

## 1. 導入動機：構文妥当性と意味的整合性の乖離

追記専用（append-only）JSONL 台帳と派生 Markdown 群からなる外部記憶システムでは、すべての行が `schema/*.schema.json` に適合していても、次の3種類の「静かな意味的破綻」が生じうる。

1. **派生自己モデルの空疎化・凍結**: `BELIEF_MAP.md` 側に有効仮説が存在するのに、`SELF_MODEL.md` の抽出器が空リストや 100% 超の確率和を出力したまま「ファイル再生成結果と一致」として `--check` を通過する（2026-11-23 `ERR-20261123-7a1c02` で実測・修正）。
2. **評価記帳と信念更新の乖離（ルーチン消化停滞）**: `EVL-*` 行や `sessions.question_ids` が形式的に追記されていながら、事後分布 `P_amort` / `P_gate` のカルバック・ライブラー情報量 `D_KL(P_after || P_before)` が実質ゼロのまま推移する「無更新消化」や、問いを受諾しつつ台帳成果物が 0 件に終わる「名目的受諾」。
3. **送出時記憶再構成による疑似逐語引用（Reality-Monitoring 破綻）**: 原典全文を閲覧した直後であっても、JSONL 生成時に LLM がコンテキスト記憶から英文を再構成して引用符を付す作話（`SESSION-20261125-5310bf` の監査で `10/10` 件の疑似逐語引用を実測）。

これらを防ぐため、本リポジトリでは**複数の独立した台帳・派生ビュー・暗号学的証跡を突き合わせる交差意味的不変量**を実装し、GitHub Actions（`.github/workflows/ci.yml`）のハードゲートとして強制する。

---

## 2. 派生 Markdown 群の依存 DAG と鮮度・意味検査

手編集禁止の 4 つの派生 Markdown は、以下の順序で単方向の依存 DAG をなす。

1. [`BELIEF_MAP.md`](../BELIEF_MAP.md)（`python3 tools/belief_state.py --write-map`）
   - `hypotheses`・`evaluations`・`errata`・`editorial_decisions`・`read_log` から 4 基底（`P_t`, `P_sep`, `P_gate`, `P_amort`）・家系集中度・推奨対を決定論的に算出する。
2. [`docs/CONSOLIDATED_DIGESTS.md`](CONSOLIDATED_DIGESTS.md)（`python3 tools/memory_tiers.py --write-digests`）
   - L2（現役）・L1（統合スキーマ）・L0（休眠・エポック凍結 SHA-256）の三階層索引を生成する。
3. [`SELF_MODEL.md`](../SELF_MODEL.md)（`python3 tools/self_model.py --write`）
   - `BELIEF_MAP.md`・`sessions`・`interoception.py`・`temporal_continuity.py`・`default_mode_probe.py` を統合し、§1（自己同定）〜§6（予測誤差）を生成・検証する。
4. [`READING_MAP.md`](../READING_MAP.md)（`python3 tools/map_build.py`）
   - 上記を含む書庫全体の言及グラフとエピソード索引を構築する。

---

## 3. 第6層：予測誤差プローブと反事実感度（`tools/default_mode_probe.py` / `SELF_MODEL.md` §6）

`tools/default_mode_probe.py` は台帳を一切書き換えず（読み取り専用）、以下の 2 系統の予測誤差指標を算出し、`SELF_MODEL.md` §6 および `python3 tools/default_mode_probe.py --check` に配線する。

### 3.1 遡及的予測誤差（Retrospective Prediction-Error Audit）

- **直近評価セッションの前後分割**: 非撤回の評価行（`errata.weight_effect == "void_row"` を除外）を持つ直近セッション `s_last` の前後で `evaluations` を分割し、`P_amort`（世代償却基底）および `P_gate`（三門制御基底）について中心三問 `Q-001`〜`Q-003` ごとに情報利得（KL ダイバージェンス）と L1 距離を算出する。
  - `D_KL(P_after || P_before) = Σ_h P_after(h) log2(P_after(h) / P_before(h))`（単位: bits）
- **フロンティア照準整合（`frontier_alignment`）**: `s_last` 実行前の `P_amort` / `P_gate` 首位対立ペアに対し、実際の評価行が直接その対を分離したか（`exact_frontier_pair`）、片方の仮説を検証したか（`frontier_member`）、フロンティア外を探索したか（`off_frontier_exploration`）を分類する。
- **停滞・名目的受諾アラーム（`band`: `green` / `amber` / `red`）**:
  - `red`: 直近 `W`（既定 5）評価セッションすべてで `max_Q D_KL < 1e-4` bits（評価行を書きながら信念分布が全く動かないルーチン消化）。
  - `amber`: 直近 `W` 評価セッションの半数以上が `D_KL < 1e-4` bits、累積最大ドリフト `< 5e-4` bits、または直近探求 5 セッション中 3 回以上が名目的受諾（`question_ids` 非空かつ `EVL`/`HYP`/`NOTE`/`ERR` すべて 0 件）。
  - `green`: 上記いずれにも該当せず、実質的な事後更新が継続している状態。

### 3.2 事前の反事実感度予測（Prospective Counterfactual Sensitivity）

- 現在の `Q-001`〜`Q-003` それぞれの最高 `EIG_amort` 対立ペア（`left` vs `right`）に対し、インメモリで「独立セッションによる `verified` 原典衝突（`primary_source_collision` / `narrows_scope`）1 件」を仮想注入し、次回セッションで観測されるべき予測シフト `pred_D_KL`（bits）と `ΔP_amort`（percentage points）を `SELF_MODEL.md` §6 に明記する。

### 3.3 `self_model.py` における交差不変量検査

`self_model.validate_invariants()` は既存の §1〜§3・日付整合に加え、以下を強制する。
- `D_KL >= 0`（非負有限値）、`L1 ∈ [0, 2]`、`band ∈ {"green", "amber", "red"}`。
- `BELIEF_MAP.md` の §3 で `P_amort` 上位仮説が 2 件以上ある中心問いについて、`SELF_MODEL.md` §6 の `prospective.core_pairs` が欠落していないこと。

---

## 4. 第三門拡張：原典スパン証跡の交差意味的不変量（`three_gates.py --verify-span` / `validate_seed.py`）

### 4.1 計算非対称性を利用した作話遮断の原理

自己回帰型 LLM はトークン生成中に記憶から流暢な疑似引用文を合成できる一方、**正規化文字列の SHA-256 ハッシュ値を重み内部で暗算することはできない**。この計算非対称性を利用し、`schema/material.schema.json` の `verification` に以下の任意欄を追加した。

- `quote_status`: `"verbatim"` | `"paraphrase_summary"` | `"mixed"` | `"none"`
- `span_sha256`: 正規化済み逐語スパン列の SHA-256（64 文字 16 進）
- `span_norm_chars`: 正規化済み逐語スパン列の文字数

### 4.2 収蔵時の原典照合手順（`--verify-span`）

新規に逐語引用を含む素材を記録する際は、取得した原典テキストファイルに対して以下を実行する。

```bash
python3 tools/three_gates.py --verify-span \
  --source-file /tmp/fetched_paper.txt \
  --passage "Organisms adapt well enough to 'satisfice' ... do not, in general, 'optimize.'" \
  --quote-status verbatim
```

1. `normalize_source_span()` が HTML タグ除去・NFKC 正規化・小文字化・トークン列化を行う（改行・イタリック装飾・引用符の揺れには頑健でありながら、単語の置換・創作・条件反転には即座に不一致となる）。
2. 学術的省略記号（`...` / `…`）で区切られたすべての節が、原典テキスト内に**順序通り連続トークン列として実在するか**を検証する。1 節でも不在なら `STATUS: CONFABULATION_MISMATCH`（終了コード 1）を返し、ハッシュを発行しない。
3. 全節一致時のみ `STATUS: VERIFIED_SPAN` として `quote_status`・`span_sha256`・`span_norm_chars` の JSON スニペットを出力する。

### 4.3 オフライン CI における交差意味的不変量（`validate_seed.py` & `three_gates.py --check`）

著作権保護された原典全文をリポジトリに同梱しなくとも、CI はオフラインで以下の交差不変量を `< 5 ms` で検証できる。

1. **前方日付ゲート（`SPAN_WITNESS_RULE_FROM = "20261126"`、シャード実日付境界つき）**: `2026-11-26` 以降に新規追加される `status: "verified"` かつ `depth ∈ {"full_text", "results"}` の `research_excerpt`・`literary_text` 行は、`verification.quote_status` の明示を必須とする（既存の全歴史行は無変更のまま通過し、追記専用不変量を保つ）。
2. **ハッシュ再計算一致**: `quote_status ∈ {"verbatim", "mixed"}` の行では、`passage` から抽出した正規化逐語スパンの SHA-256 と文字数を再計算し、`span_sha256`・`span_norm_chars` と完全一致しない限りエラーとする（LLM がダミーの 64 文字 16 進数を手書きしたり、検証後に `passage` を改変したりすると即座に検出される）。
3. **照合深度・要約標識との意味的無矛盾**:
   - `quote_status ∈ {"verbatim", "mixed"}` でありながら `depth ∈ {"metadata", "unspecified"}` または `status == "unverified"` とする矛盾を拒否する。
   - `quote_status == "verbatim"` でありながら `passage` が `【編者による要約】` 等で始まる矛盾を拒否する。
   - `quote_status == "paraphrase_summary"` では、`passage` または `context` に明示的な要約標識（`【編者による要約】` 等）を要求し、要約文が無標識のまま原典逐語引用として流通することを防ぐ。
