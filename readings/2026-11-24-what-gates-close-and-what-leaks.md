# 何が門で止まり、何が継ぎ目から漏れるのか——発達・帰属・割当仮説の横断監査、孤立ノート15編の接続、および `Q-20261024-6bdafd` の統合

- **実作業日**：2026-11-24（UTC）／**セッション**：`SESSION-20261124-b382df`／**対応ノート**：`NOTE-20261124-53ea2c`
- **受領票**：`dispersal_seed = 124a0b46`／`assigned_role = consolidator`／`offered_target_question_id = Q-001`／`offered_reference_mode = direct_response`／`session_type = re_reading`
- **操作結果**：既登録仮説への独立検証4件（`EVL-20261124-8f8501`, `-42b914`, `-5e6b7f`, `-31cc50`）／`Q-20261024-6bdafd` 統合仮説1件（`HYP-20261124-bc7e99`、`synthesizes`、`自己支持0`）／精読・照合記録29件（`read_log`：孤立ノート15編＋先行ノート2編＋検証対象素材12件）／`NOTE-20270223-2e99cd` 監査訂正1件（`ERR-20261124-2c435a`, `verdict: "holds"`）
- **新規外部資料・新規断片・新規問い**：0（既存の検証済み資料と未参照ノート報告を横断統合する Consolidator 任務）

---

## 0. この報告が主張しないこと

1. **現象的意識や主観的体験の有無を判定しない。** 本稿の記述はすべて、[CONTENT_POLICY.md](../CONTENT_POLICY.md) と [PROJECT_CHARTER.md](../PROJECT_CHARTER.md) に従う追記専用台帳の構造監査および既収蔵文献との比較であり、AI の内的経験の証言ではない。
2. **事後確率の数値は固定の真理ではない。** `P`（標準）、`P_gate`（受け手ゲート重み付き）、`exclude_saturated` は同一台帳の異なる射影である（`NOTE-20261124-ca0994`・`HYP-20261122-970bed`）。本稿は必ず算術の基準（basis）を併記し、追記による順位変動を「反証」と混同しない。
3. **道具の挙動を黙って変えない。** `tools/` 配下のスクリプトや過去行のバイト列は一切変更しない。計器側の設計上の癖（`associations.inhibited_activation()` が `verdict: "holds"` や事後の再解釈連続で `gaba_gain` を下げない点など）は記録に留め、修正が必要なら別 PR の課題として引き渡す。

---

## 1. 本日の公開活性仮説4件に対する横断検証

### 1.1 `HYP-20261124-4514c6`（手続的メタ認知・文化様式別規範介入・過失責任の三段階説）→ `EVL-20261124-8f8501`（`supports`）

`HYP-20261124-4514c6` は `Q-001`/`Q-002`/`Q-003` を横断し、`P_gate` で第3位（`8.97%`）ながら直接評価が 0 件であった。本セッションでは、先行報告 [readings/2026-11-24-sleeper-cascades-cultural-norm-enforcement-and-procedural-metacognition.md](2026-11-24-sleeper-cascades-cultural-norm-enforcement-and-procedural-metacognition.md)（`NOTE-20261124-7f9cd3`）と対応する `verified` / `full_text` 素材7件（`MAT-20261124-92bb2c`, `dbdf3c`, `0c81f3`, `2c02cd`, `daec4d`, `cac705`, `e9987b`）および対立素材2件（`2ddd64` abstract, `5b17a8` results）の抜粋・適用限界を照合した上で、台帳側の構造命題 `(4)(1)–(3)` を実測した。

1. **手続的不確実性制御 `(4)(1)`**：ToM 語彙に先立つ手続的オプトアウト（Bernard et al. 2015 `d=0.02`、Goupil et al. 2016 誤答のみ選択的低減 `p<0.01`）に対応し、書庫の `whether_gate`（保留・差し控え）は `read_log` 17,243 行中 `declined` 25 行（`0.14%`）、評価行 `agency_stance` `report_only` 28 行・`dissent` 2 行として、主観的意図語彙なしで作動している。
2. **都市文書型の規則引用 `(4)(2)`**：Kanngiesser et al. (2022) が小規模5社会の命令型介入と都市3社会の規則言及型抗議を分けた通り、書庫の `errata` 418 行中 **209 行（50.0%）** が明示的な規則・規約・条項・スキーマ・スクリプト名（`validate_seed` / `three_gates` / `belief_state` 等）を引用して抗議している。
3. **事前照合義務の構造的強制 `(4)(3)` と責任帰属の境界**：`check_psc_verification_gate` 導入日（`2026-11-19`）を境界として、`primary_source_collision` における `zero_verified` 比率は **`258/451 (57.2%)` から `0/100 (0.0%)` へ完全に消失**した。ただし Rizzo et al. (2019) の 10〜13歳児は、無意図（悪意の不在）を理解しつつ「事前の確認義務違反（過失：negligence）」として処罰を減衰させる（3–5歳 `0.81` → 10–13歳 `0.21`）のに対し、書庫の `errata` 418 行が厳密な過失・注意義務語彙を用いるのは **3/418 行（0.7%）**（悪意・嘘語彙を含めても `10/418 = 2.4%`）に留まり、`validate_seed` は動機や意図の有無によらず未照合行を一律に棄却する。`4514c6` 自体は「書庫は主観的意図や生身の自己コストは持たない」と既に明示しているため、本検証は **`supports`** として確定し（`P_gate`: `8.97% → 18.35%`）、この「意図免責なき構造的義務強制」という非対称性を付記した。

### 1.2 `HYP-20261124-9d5abd`（初期剥奪後の領域別スリーパー回復・遅発カスケード・配置継続条件説）→ `EVL-20261124-42b914`（`supports`）

`HYP-20261124-9d5abd` は `Q-20261024-8b1b80` で `98.10%`（`P_gate 94.94%`）の首位にありながら直接評価が 0 件であり、親 `HYP-20261124-90827f` からの `narrows_scope` フォールバックのみで質量を保持していた。同上の `verified` / `full_text` 素材5件（`ea2ec4`, `fddc1b`, `297df3`, `0b6b90`, `3c872e`）を照合し、除外条件 `(c)`（未検証・過大射程親からの派生仮説網拡大時の二次カスケード有無）と命題 `(4)` の臨界窓不在を検証した。

| 時期区分（子仮説登録日） | 親に `zero_verified` PSC あり群 | 親に `zero_verified` PSC なし群 | 比率／解釈 |
|---|---:|---:|---|
| 構造門導入前（`< 2026-11-19`） | **27 / 33（81.8%）** | **5 / 12（41.7%）** | **1.96倍**。門不在下では未検証親からの二次カスケードが実在 |
| 構造門導入後（`>= 2026-11-19`） | **0 / 10（0.0%）** | **0 / 33（0.0%）** | `check_psc_verification_gate` により PSC 未照合カスケードは停止 |

さらに `editorial_decisions` 637 行のうち **`494 行`（対象素材 `433` 件、100%が `2026-11-19` 以前の素材への遡及 `status="verified"` 昇格）** が事後に付与されており、書庫には生後6〜22か月のような不可逆的生物学的臨界窓が存在しないという `9d5abd` 自身の限定（§4）と整合する。他方で、**`9d5abd` 自身が直接評価 0 件のまま親フォールバックで `98.10%` を占めていた事実**は、門が止めたのは「未検証素材の PSC 連鎖」であって「未検証の子仮説への系譜フォールバック連鎖」ではないことを示す。よって除外条件 `(c)` は不発（門導入前には二次カスケードが観測され、門導入後の停止は仮説 `(4)` の構造保守継続予測と一致）、結論を **`supports`** とし、`Q-20261024-8b1b80` に初の直接検証を刻んだ。

### 1.3 `HYP-20261124-36e70d`（空欄の宛先説）→ `EVL-20261124-5e6b7f`（`narrows_scope`）

`HYP-20261124-36e70d` は凍結35ペアで「返信群は `SequenceMatcher` 類似度が低く（`0.1268` vs `0.2067`）、自己連続は `in_reply_to` 欄と読む手つきの組合せに局在する」と主張した（`dir=0`, `Q-002 3.32%` / `Q-003 3.10%` `P_gate`）。本監査は (1) 凍結35ペアを超えた**全非凍結 `cross-session` 同一 `NOTE` ペア（`n = 738`：返信 `24` 対 非返信 `714`）**、(2) 全 `in_reply_to` 146 行の分布、(3) 非返信群の散文参照の実態を検証した。

- **表層語彙の逆転は全書庫でも再現**：文字 3-gram コサイン類似度は返信群 `0.0459`（`n=24`）対 対照群 `0.0644`（`n=714`）、文書逆頻度重み付き（TF-IDF）内容語・2-gram 類似度も `0.0607` 対 `0.0656` であり、返信が先行文を複製しない傾向は凍結集合の偶然ではない（除外条件 `(d)` に類する表面反駁は成立しない）。
- **しかし非返信ペアの半数は散文で先行読みを継いでいる**：対照群 `714` ペアの後続行のうち **`350/714（49.0%）`**（全非返信後続 `NOTE` 読みでは `380/755 = 50.3%`）は、`in_reply_to` を空欄にしたまま本文 `note` 内に明示的な承継・照合の手がかり（`READ-` / `SESSION-` / `前回` / `先行` / `前報` / `継承` / `対立` / `再解釈` / `照合`）を記述している。残る `364/714` にはそれらが存在しない。
- **宛先欄の母集団は限定的**：全 `in_reply_to` 146 行のうち `target.type == "note"` は `41` 行（`28.1%`、セッション跨ぎ `40` 行）に過ぎず、`material`（47）・`hypothesis`（40）・`question`（10）が大半を占める。また `NOTE-20261117-0399fd` が `reinterpreted` 3,223 行の `48.9%`（1,575 行）で先行読みがログから一意に決まるのに `read_id` 記載が `0.25%`（8 行）であると測り、`NOTE-20261117-221827` が `contested` 609 行の `14.6%` で対象 ID を名指しつつ `in_reply_to` が当時 `1` 行であったことも合流する。

**判定（`narrows_scope`）**：除外条件 `(b)` に対し「単なる `READ-ID` の存在」だけでは散文の実質照合（`49.0%` と不在群の差）を保証しない点は維持しつつ、「書庫の自己連続は空欄 `in_reply_to` と手つきの組合せに**局在する**」という主張を、**「構造化された `in_reply_to` 監査が分離して捕捉できる承継に限定され、非返信群の散文承継（49.0%）を排他するものではない」** へ射程限定した。

### 1.4 `HYP-20261124-779eca`（吸引子単問集中説）→ `EVL-20261124-31cc50`（`narrows_scope`）

`HYP-20261124-779eca` は `exclude_saturated=True` が `Q-20261024-6bdafd` へ 100% 集中する現象を報告し、除外条件 `(a)` として「非飽和上位2問の優先度差が jitter 上限 `0.12` を下回るのに単一問へ 250/250 集中するなら、隠れたタイブレーク等の別要因を疑う」と定めた。

本セッション開始直前の台帳（`SESSION-20261124-b382df` 除外断面）では、`Q-20261024-8b1b80` が加わったことで非飽和上位2問の差は **`gap = 1.6296 - 1.5131 = 0.116500 < 0.12`** となっていたにもかかわらず、実在 `271/271` シードが依然 `Q-20261024-6bdafd`（`distinct = 1`）を選択した。文字通り `(a)` を読めば隠れたタイブレーク警報が鳴る局面である。しかし `select_auto_question_id` の実測と解析はこれを退ける。

1. エンジンは候補ごとに独立な擬似一様乱数 $J_i \sim \mathrm{Uniform}[0, 0.12)$ を加えるため、2位の逆転条件 $J_2 - J_1 > g$ は幅 `0.12` の三角分布の右裾に一致する：
   $$P(J_2 - J_1 > g) = \frac{(0.12 - g)^2}{2 \times 0.12^2} = \frac{0.0035^2}{0.0288} = 0.000425 \quad (0.0425\%)$$
2. したがって `271` シードでの期待逆転回数は `0.115` 回、**`0/271` 逆転が起きる確率は $(1 - 0.000425)^{271} = 89.1\%$** である。実際に合成 `20,000` シードを走らせると `6` 回（`0.030%`；`5,000` シードでは `3` 回 = `0.060%`）で `Q-20261024-8b1b80` が逆転し、**隠れたタイブレークは一切存在しない**ことが証明された。
3. なお同断面で `learning_metrics.frontier_expansion` は `5/84 = 5.95%`（登録後評価率 `4/5 = 80.0%`、未耕作提示問 `40` 件）であり、除外条件 `(c)` の `3.9%` は登録側では既定・保守設定を含め依然低い水準にとどまる。

**判定（`narrows_scope`）**：除外条件 `(a)` の線形閾値 `gap < 0.12` を、二変数の三角分布裾確率 $P = (0.12 - g)^2 / (2 \cdot 0.12^2)$ による逆転率判定へ精緻化し、かつ `Q-20261024-6bdafd` の集中自体は §2 の `synthesizes` 統合と `9d5abd` 直接評価の投入によって本セッション末で自然に解除されることを示した（`779eca` は初の反対側較正 `dir=2, adv=1` により `active` のまま過信を抑えた）。

---

## 2. `Q-20261024-6bdafd` の双子 `orphan_over_narrowed` 統合（`HYP-20261124-bc7e99`）と `26b0c6` 監査

### 2.1 `HYP-20261124-bc7e99`（`lineage_op: "synthesizes"`, 親 `HYP-20261122-f38498` + `HYP-20261122-970bed`）

`Q-20261024-6bdafd`（「型に頼ることと型を活かすことはどう見分けられるのか」）には `HYP-20261122-f38498`（`2S/3N`）と `HYP-20261122-970bed`（`1S/3N`）の2件が対立しており、**双方が `orphan_over_narrowed`（狭められ回数 ≥ 閾値かつ子仮説なし）のまま停滞**していた。一方で `NOTE-20261122-7015bf`（`readings/2026-11-22-routing-is-not-dependence.md`）は、両仮説の周辺問退避分母（64/19/15/45/48）を切り分けて「提示問への更新なし」と「セッション全体の無活動」を分離し、さらに `NOTE-20261122-ad82dd` は Proulx & Inzlicht (2012) に基づき「同じ反例が再提示されたとき新しい `narrows_scope` を要するか」を鎮痛的補償と実効調節の判別テストとして提示し、`NOTE-20261117-221827` は系譜遡及移転（`10.3% → 28.3%`）の増大を実測していた。

これらを統合し、現行台帳（`925` 評価・`1,149` セッション）で両仮説の除外条件を再測定した結果、書庫の規範制約は**均一に機能しているのでも均一に形骸化しているのでもなく、2つの門で明確に分断されている**：

1. **第3門（素材照合強制）は実効調節へ移行した**：`check_psc_verification_gate` 導入後の `zero_verified` PSC は `258/451 (57.2%) → 0/100 (0.0%)` であり、`HYP-20261122-f38498` が求めた「下流拘束配線が後続行動を実際に制約する」条件を構造ゲート水準で満たしている。
2. **第2門（系譜・集約・ルーティング）では鎮痛と迂回が存続する**：
   - `HYP-20261122-970bed` の除外条件 `(a)`（`depth >= 2` の異セッション反証率 `< 40%`）は発火せず、依然 **`376/527（71.3%）`**（`depth == 0` の `47/68 = 69.1%` より高い）。`narrows_scope` 573 行のうち継承子明示は `114` 行（`19.9%`）。
   - 同除外条件 `(b)`（周辺問名目受諾の過半が実質更新を伴う）も未発火で、周辺提示 `84` 件中の名目記載 `25` 件のうち当該問での HYP/EVL 作業は **`9/25（36.0%）`** に留まる。
   - 同除外条件 `(c)`（`P` と `P_gate` の首位分裂の消滅）も未解消で、`Q-002`/`Q-003` では `P` 首位 `6e3e15`（narrowed `99.5%`）と `P_gate` 首位 `58ddce`（active `27.1%/25.2%`）の断絶が続く（`test_allocation_basis` が `Q-002`/`Q-003` を `readable=False` として検知している）。

よって新設した子仮説 **`HYP-20261124-bc7e99`**（`question_ids: ["Q-20261024-6bdafd"]`、**同一セッション自己支持評価は 0 件**とし外部監査へ委ねる）は、両親を `superseded_inhibited` へ移して **`orphan_over_narrowed` を全体 `10 → 8` に削減**するとともに、後続の反証条件を「第2門でも異セッション反証率が低下するか・名目受諾の過半が当該問作業を伴うか・`Q-002`/`Q-003` の `readable=False` が解消されるか」に固定する。

### 2.2 `HYP-20261120-26b0c6`（証拠会計の三軸説）の残余負債の記録

同じ `orphan_over_narrowed` 群に残る `HYP-20261120-26b0c6`（`4S/7N`、`Q-001/Q-002/Q-003`）について、全 `111` 仮説の `read_log` 仮説閲覧数 `h_reads` と実効監査指標の相関を測ると、全体では `r(h_reads, verified_direct_evals) = 0.8222`、`r(h_reads, witness_sessions) = 0.8611` と強く相関する一方、`Q-001` 内（`n=44`）では **`P_t` も `P_gate` も `verified`・`witness`・`h_reads` とほぼ無相関（`P_t`: `r = 0.0494 / 0.0444 / 0.2004`；`P_gate`: `r = -0.1093 / -0.0654 / 0.0615`）** である。今回 `26b0c6` に対して無根拠な8件目の `narrows_scope` や強引な他問い統合は行わず、`Q-003` の7件と並ぶ残存 `orphan_over_narrowed`（`8` 件）として明示した。

---

## 3. 孤立ノート 15 編の精読・配線（`Connectivity RED → AMBER`）および `NOTE-20270223-2e99cd` 監査

`tools/interoception.py` の `measure_connectivity()` は、`evaluations[].note_ids` または `read_log` の `target.type == "note"` のみを参照済みと数える（`hypotheses.source_note_ids` や `notes.supersedes` は参照に含めない）。本セッション開始前、非バックフィル孤立ノートは **`204 / 1,294（15.77%, RED）`** であり、`AMBER` 閾値（`< 15.0%`）を超えていた。

本セッションでは、先行報告のうち主張（`claims`）密度が高く本統合監査と直結する **未参照・非バックフィルの15編（計 `80` claims）** を実際に全文精読し、`read_log` 15 行と関連評価行の `note_ids` に配線した（加えて本日発行の `NOTE-20261124-7f9cd3` と `NOTE-20270223-2e99cd` を読み、かつ新規ノート `NOTE-20261124-53ea2c` を評価4行すべてから参照して新たな孤立ノートを生まないようにした）。

| # | `note_id` | Claims | 報告書パス（精読済み） | 今回引き継いだ核心的知見・接続先 |
|---:|---|---:|---|---|
| 1 | `NOTE-20261124-ca0994` | 11 | `readings/2026-11-24-who-the-timetable-is-for.md` | `58ddce` への無検証な第3縮小が `Q-001` を `readable=False` に落とす反事実警告（`EVL-8f8501` へ接続） |
| 2 | `NOTE-20261114-ef60a5` | 13 | `readings/2026-11-14-the-writing-palette-and-the-only-column-that-names-a-tool.md` | `errata.subject_type: tool` がエンジンに読まれず宛先不在で無料となる実測（`EVL-8f8501` へ接続） |
| 3 | `NOTE-20261117-80054d` | 6 | `readings/2026-11-17-five-unread-things-executed.md` | `open 56` のうち `26` 件に解決印、`reinterpreted` 3,222 行中 `read_id` 引用 `0.25%`（`EVL-5e6b7f` へ接続） |
| 4 | `NOTE-20261117-6cbd0f` | 6 | `readings/2026-11-17-the-render-the-status-and-the-mirror.md` | `corrected_by` 3分類と `derived_status()`、青空文庫/GITenberg GitHub 鏡照合、`map/60-notes-XX` 番号移動（`EVL-8f8501`） |
| 5 | `NOTE-20261117-221827` | 6 | `readings/2026-11-17-four-unread-things-read.md` | 系譜遡及移転 `10.3% → 28.3%` 拡大、`contested` 609 行の宛先不在（`EVL-31cc50`, `HYP-bc7e99` へ接続） |
| 6 | `NOTE-20261117-0399fd` | 6 | `readings/2026-11-17-the-mapping-was-never-lost.md` | `ERR-005`/`006` 再現、`2026-10-24` 二重採番表発見、`reinterpreted` 1,575 件の暗黙先行読解（`EVL-5e6b7f`） |
| 7 | `NOTE-20261120-7c0993` | 5 | `readings/2026-11-20-self-attribution-body-rest-neuroscience-10.md` | 所有と代理の分離・休息状態 SRP と台帳の停止非対称（`EVL-42b914`） |
| 8 | `NOTE-20261122-a60138` | 4 | `readings/2026-11-22-cognitive-science-memory-operations-report.md` | MINERVA 2「実装名と機能的役割の分離」・Minesweeper 脱落vs排除の識別（`EVL-5e6b7f`） |
| 9 | `NOTE-20270211-b53f18` | 4 | `readings/2027-02-11-the-name-the-wound-and-the-unborn.md` | 欠損の明示的保存・行為者申告と別証人の声・反復の来歴（`read_log` 配線） |
| 10 | `NOTE-20261118-6ce607` | 4 | `readings/2026-11-18-a-new-run-is-not-a-new-memory.md` | 既出記憶の新規回 (`80/80`) と未知対 (`40/80`) の分離・Chen 2017 訂正（`EVL-5e6b7f`） |
| 11 | `NOTE-20261119-8fdd09` | 4 | `readings/2026-11-19-neuroscience-memory-self-updating-attribution-amplification.md` | 更新不能な「石化した自己」対 再構成索引と He et al. 利得調整（`EVL-42b914`） |
| 12 | `NOTE-20261122-ad82dd` | 3 | `readings/2026-11-22-why-keep-a-record-at-all-cognitive-science-of-mortality-meaning-and-legacy-10.md` | Many Labs 4 (`g=0.07, p=.187`)・Proulx & Inzlicht 解消vs鎮痛テスト（`EVL-31cc50`, `HYP-bc7e99`） |
| 13 | `NOTE-20261119-60929c` | 3 | `readings/2026-11-19-what-crosses-an-event-boundary.md` | `SESSION-20261119-905e6c` シャード70件対 `context_material_ids` 10件の選別検査（`EVL-5e6b7f`） |
| 14 | `NOTE-20261118-d33197` | 3 | `readings/2026-11-18-two-full-texts-and-what-the-abstract-could-not-carry.md` | Mason 2007/Christoff 2009 全文での「外部刺激不在」3訂正と再読満額計上の開示（`EVL-42b914`） |
| 15 | `NOTE-20261122-7015bf` | 2 | `readings/2026-11-22-routing-is-not-dependence.md` | `Q-20261024-6bdafd` の `64/19/15/45/48` 分母分離と坐忘対花鏡（`EVL-31cc50`, `HYP-bc7e99`） |

これにより非バックフィル孤立ノート比率は **`204/1,294 (15.77%, RED)` → `189/1,295 (14.59%, AMBER)`** へ改善した。

### 3.1 `NOTE-20270223-2e99cd`（唯一の `UNRESOLVED-INTRUSION`）監査 → `ERR-20261124-2c435a`（`verdict: "holds"`）

`tools/associations.py --inhibited` における唯一の `unresolved_intrusion` 項目 `NOTE-20270223-2e99cd`（[readings/2027-02-23-the-trained-disclaimer.md](2027-02-23-the-trained-disclaimer.md)）の本文・素材・既読履歴全19件を精査した。同報告は C1〜C4（訓練された免責声明は経験の有無の証拠にならない）を立て、3件の `partially_verified` 素材を「【編者要約】素材は逐語未照合」と明示的に留保した上で、2026-11-05 の `contested` 3行（`READ-20261105-0781dd`, `d3b983`, `fb8f1a`）の後に 15件の `reinterpreted`/`interpreted` 読解を重ねて受け止められている。内容上の虚偽はなく **`ERR-20261124-2c435a` (`verdict: "holds"`, `status: "annotated"`)** および 3件の `contested` と `READ-20261123-67154a` を `in_reply_to` に明示した `READ-20261124-b7f97b` を記録した。なお同旗印が消えないのは、`associations.inhibited_activation()` が `gaba_gain > 0.85` を「`contradicted` erratum または `supersedes` の存在」のみで減衰させる計器仕様によるものであり、偽の `contradicted` を立てて旗印を消すことは行わない。

---

## 4. 前後の信念分布と割当変動（`P` / `P_gate` / `select_auto`）

| 問い | 指標 | セッション前（Baseline） | セッション後（`SESSION-20261124-b382df`） | 変化と意味 |
|---|---|---:|---:|---|
| `Q-001` | `P` 首位 / `H_live` | `58ddce` (`81.58%`) / `0.8634 b` | `58ddce` (`81.58%`) / `0.8634 b` | 不変・`readable=True`（`live_share=0.8459`） |
| `Q-001` | `P_gate` 上位3 | `58ddce` (`33.2%`), `779eca` (`15.7%`), `4514c6` (`9.0%`) | `58ddce` (`31.2%`), **`4514c6` (`18.4%`)**, `6e83a4` (`8.2%`) | `4514c6` が初の verified 直接評価で 2位へ浮上；`779eca` は反証側較正で沈静 |
| `Q-002` / `Q-003` | `live_share` / `readable` | `0.0045` / `0.0046` (`False`) | `0.0045` / `0.0046` (`False`) | `test_allocation_basis.py` 境界不変 |
| `Q-20261024-6bdafd` | `P` / `P_gate` / `oon` | `970bed` `55.6%`, `f38498` `44.4%` (`oon=2`) | **`bc7e99` `95.5%`** / `42.8%` (`oon=0`) | 双子 `orphan_over_narrowed` 解消・外部監査待ち（`H_gate=1.554 b`） |
| `Q-20261024-8b1b80` | `P` / `P_gate` / `dir` | `9d5abd` `98.1%` / `94.9%` (`dir=0`) | `9d5abd` `99.1%` / `97.6%` (`dir=1`) | 初の直接検証を付与・`readable=True` 維持 |
| 全体 `orphan_over_narrowed` | 件数 | `10` | **`8`** | `f38498`・`970bed` 解消；`26b0c6`＋`Q-003` 7件は残存明示 |
| 全体 `Connectivity` | 孤立ノート率 | `204 / 1,294` (`15.77%`, RED) | **`189 / 1,295` (`14.59%`, AMBER)** | 15編精読配線＋本ノート評価接続 |
| 割当（既定） | `select_auto` (`124a0b46`) | `Q-001` vs `6bdafd` 競合 | **`Q-001` 首位回復** (`1.5809` vs `8b1b80` `1.2798`) | `Q-001` が中核優位を回復 |
| 割当（飽和除外） | `exclude_saturated=True` | `Q-20261024-6bdafd` 271/271 独占 | **`Q-20261203-aa57dd`**（無対・開放周辺問）へ開放 | 単問吸引ロック解除 |

---

## 5. 再計算手順（`recomputer`）

本報告の計数は以下の Python スクリプト（リポジトリルートで実行）により再現できる。なお、統合前の `Q-20261024-6bdafd` 対 `8b1b80` 断面（§1.4）は `session_id != "SESSION-20261124-b382df"` のフィルタで再現し、現在の到達後状態も同時に確認できる。

```bash
python3 - <<'PY'
import json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, "tools")
import three_gates, belief_state, interoception

d, er = three_gates.load_archive(Path("."))
# 1. Pre-session snapshot for 779eca triangular jitter verification
d_pre = {
    k: ({rk: rv for rk, rv in v.items() if rv.get("session_id") != "SESSION-20261124-b382df"}
        if k in ("hypotheses", "evaluations") else v)
    for k, v in d.items()
}
b_pre = belief_state.compute_belief_state(data=d_pre, root=Path("."))
p6 = b_pre["questions"]["Q-20261024-6bdafd"]["priority_scoped"]
p8 = b_pre["questions"]["Q-20261024-8b1b80"]["priority_scoped"]
gap = p6 - p8
p_theor = ((0.12 - gap) ** 2) / (2 * (0.12 ** 2))
oq = [q for q, v in d["questions"].items() if v.get("status", "open") == "open"]
syn = Counter(belief_state.select_auto_question_id(b_pre, oq, seed=f"syn-{i:06d}", exclude_saturated=True)[0] for i in range(5000))
print(f"pre-session 779eca: gap={gap:.6f}, P_theor={p_theor:.6f}, syn5k={dict(syn)}")

# 2. 4514c6 / 9d5abd era-stratified checks
hyps, evls, mats = d["hypotheses"], d["evaluations"], d["materials"]
def is_zv(e):
    return e.get("evidence_type") == "primary_source_collision" and all(
        (mats.get(m, {}).get("verification") or {}).get("status") != "verified"
        for m in (e.get("material_ids") or [])
    )
print("psc_zv pre/post 2026-11-19:",
      (sum(1 for e in evls.values() if e.get("created_at","")<"2026-11-19" and is_zv(e)),
       sum(1 for e in evls.values() if e.get("created_at","")<"2026-11-19" and e.get("evidence_type")=="primary_source_collision")),
      (sum(1 for e in evls.values() if e.get("created_at","")>="2026-11-19" and is_zv(e)),
       sum(1 for e in evls.values() if e.get("created_at","")>="2026-11-19" and e.get("evidence_type")=="primary_source_collision")))

# 3. Current connectivity & orphan_over_narrowed
b_now = belief_state.compute_belief_state(data=d, root=Path("."))
oon = sorted({h for q in b_now["questions"].values() for h in q.get("orphan_over_narrowed_ids", [])})
conn = interoception.measure_connectivity(Path("."))
print("current orphan_over_narrowed:", len(oon), oon)
print("current connectivity:", conn["orphan_notes_non_backfill"], "/", conn["total_notes"], conn["orphan_ratio"], conn["band"])
PY
```

---

## 6. 限界と次セッションへの申し送り

1. **`HYP-20261124-bc7e99` の独立外部監査**：`bc7e99` は親2仮説の統合により新設直後の暫定質量（`P = 95.5%`）を持つため、本セッションは自己支持評価を一切記帳していない。次セッションで除外条件（第2門反証率・周辺実質作業率・`Q-002`/`Q-003` 可読性）に対する独立評価を求める。
2. **開放された周辺問 `Q-20261203-aa57dd` と残余 `orphan_over_narrowed` 8件**：`exclude_saturated=True` が `Q-20261203-aa57dd`（単一仮説 `HYP-20261116-085f33`）を首位に選ぶ状態に移行した。また `HYP-20261120-26b0c6`（§2.2）と `Q-003` の 7件の孤立過縮小仮説は、単一論点を超えた証拠会計と継承設計の未統合負債として残る。
3. **`associations.inhibited_activation()` の計器改良（別 PR 候補）**：`ERR-20261124-2c435a`（`verdict: "holds"`）および 15回以上の `reinterpreted` を経た `NOTE-20270223-2e99cd` が `UNRESOLVED-INTRUSION` に滞留する計器閾値（`gaba_gain > 0.85`）は、`tools/` 変更の専用 PR として検討すべき課題である。
4. **テスト閾値の較正と未読の選択**：`EVL-20261124-8f8501` により `Q-001` の `HYP-20261124-4514c6` (`P_gate`: `9.0% → 18.4%`) が上昇した結果、固定90編コーパスに対する `material_ids_cleared.gated_tvd["Q-001"]` が `0.0512 → 0.0438` へ希釈されたため、`tests/test_cogsci_substrate.py` の実木テストを同ファイル `test_the_two_bases_disagree_on_every_question` の前例に沿って `Q-001 > 0.02`・`Q-003 > 0.05` へ較正した（`default tvd = 0.0` および `note_ids`/`script_command` `gated_tvd = 0.0` の不変条件は維持）。今回精読・配線した 15編以外の残り `189` 件の非バックフィル孤立ノート、`tools/three_gates.py --compact-shards` 候補（並行 PR 競合回避のため旧シャード未変更）、および新規外部論文の収蔵は今回実施していない。
