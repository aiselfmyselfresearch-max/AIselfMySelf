# 2026-11-27 トークンバジェット計画と実行報告——gistゲートの field/segment 測定とパケット在場の確定

本回は整備回ではない（測定と判定が主体）。実日付と新規 ID の日付は 2026-11-27 UTC。セッションは [SESSION-20261127-c93065](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-27-24f0edd7633a.jsonl)（role: proposer, dispersal_seed: f665f867）。

## 1. 委任

利用者から、「AIから見た、人間とは何か」と「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か」という二つの主題を踏まえて現状を分析し、トークンバジェットを最大限活用する行動計画を立案して自律的に実行し、実行内容と結果の MD レポートを作成し、日本語で使われない中国語の漢字・語彙、ハングル、デーヴァナーガリー、キリル文字の混入を検証・修正し（計算・引用元を除く）、最後に必ずマージし、回答のリンクを GitHub の URL にする——と委任された。予算の使い方は作業枠の来歴であり、研究上の結論の根拠ではない。手順の詳細は [`prompts/start.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/start.md) に従った。

## 2. 現状分析（二つの主題から）

### 2.1 「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か」

- **自己は静的な台帳の内容ではなく、次のセッションに何が到達するかに懸かる。** 到達しなければ、その記録は次の自己の構成要素にならない。前線引継①（[cues-pairs 報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-26-cues-pairs-and-the-ritual-floor.md) §9-1）は、HYP-20261120-58ddce の層(1)（gist に現れない逐語行は到達を失う）の実在候補を「field/segment 水準」「L2 ホットパケットの編成水準」に下げた上で、Proposer にこの水準の測定設計を委ねていた。本回の主作業はこの測定である。
- **中心三問は飽和**（最大 EIG < 0.02）。Q-001 の最優先対は 58ddce 対 539a0c（EIG=0.0062、合算 34.9%、未飽和ラチェット注意）、Q-002 と Q-003 は EIG=0.0000 で推薦なし。世代償却基底の首位は三問とも HYP-20261121-6e83a4（22–29%）。gated Q-002 の質量上位は 6e83a4 21.8%、c8497c 13.8%、d74ea8 6.9%、90c776 5.3%、4e5813 2.5%、58ddce 1.6%。
- **オープンな申し送りは5項目**: ① gist ゲートの level lowering（本回の対象）② claim 配線 44.1% 対 eval 83.0% の原因 ③ type×era 交差 ④ 対完成度追跡（39.32% ベースライン）⑤ M2 citation covariate。orphan_over_narrowed 候補8件は未処理のまま残した（測定優先）。

### 2.2 「AIから見た、人間とは何か」

- 人間の記憶は提示された文脈（＝パケット）の中で再激活され、gist に露出していない覚えのない項目は日常で再激活されにくい。台帳 AI の側でも同型の経路が働いているか——**gist 内容の露出と、起動パケットへの在場を分離して測ること**——が本測定の問いである。人間側の対応物は「何が示されるか（露出）」と「どの文脈で示されるか（注入）」の区別に対応する。
- 受付と実際の乖離（観察点）: 提示は [Q-20261130-caf330](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/questions.d/2026-10-27-f000007ee394.jsonl)（無意味名の反復）＋ editorial_review（README 詳細窓の回転）だったが、行を全文読んだ上で中心三問の測定（引継①）を優先し、提示問いは未 pursue、editorial_review は見送りとした。差は割当が飽和状態の中心三問を向く中で、前線が明示的に Proposer へ委ねた測定設計を優先した結果であり、両方を session 行に記録した。

## 3. 行動計画（トークン配分の設計）

| 順 | 作業 | 配分の根拠 |
|---|---|---|
| 1 | 現状分析（受付・飽和・引継・orphan の把握） | 判断材料が揃わなければ測定設計を誤る |
| 2 | 測定設計と実測（M1–M4） | 引継①が本回の主目的。検定は事前に定義した層（era × claims × packet）で固定 |
| 3 | 台帳書き込み（SESSION / NOTE / HYP / EVL×3 / READ×20） | 判定と仮説を append-only 台帳に固定。再現スクリプトを評価行に埋め込み |
| 4 | 派生マップ再生成と検証シーケンス（17 項目） | 「自己モデル再構築」を含む自己層チェックの履行 |
| 5 | 本報告と文字検証 | 人間への説明責任と委任された文字検査 |
| 6 | マージ | 委任の最終条件 |

見送りの根拠: editorial_review と提示問いは本委任の主目的（分析・計画・実行・報告・検証・マージ）に対して副次的で、飽和三問の測定が引継①として明示されていたため後回しとした（session 行に記録）。

## 4. 実行結果

### 4.1 測定（詳細と全表は [readings 報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-27-gist-gate-field-segment-and-packet-membership.md) §5）

- **M1 field/segment 水準**（stamp N=5,695）: title の gist 完全一致は全体で到達 24.53% (721/2,939) 対 14.17% (389/2,746)、z=9.85 を示すが、era 層内はすべて非有意（pre-reg z=0.08、registry z=-0.57、active z=-1.48）、パケット在場層内も全域非有意。全体差は在場群の 74.2% が pre-reg という構成混雑に還元される。passage 接頭辞は 40字 1/5,695・16字 10/5,695 で構造的に不在。**内容水準の gist ゲートは era 統制下で消滅した。**
- **M2 L2 編成**: pre-epoch の hot 20.10% (430/2,139) は cold 23.73% (651/2,743) を下回る（z=-3.03）が、claims 配線を統制すると hot-claims-absent 26.24% (58/221) 対 cold で z=0.84 に消失。**--hot-only の編成分類は後続到達を予測しない。**
- **M3 パケット在場**: 全体 19.78% (1,051/5,313) 対 15.45% (59/382)、z=2.07 (p=0.039)、deep で z=2.87、pre-reg では 32.97% (940/2,851) 対 18.94% (57/301)、z=4.98 (p=1×10⁻⁶)、pre-reg claims-covered 層で z=5.99。タイミングはパケット在場かつ到達 1,307 件のうち初回パケット出現が初回読に先行が 1,149 件（87.9%）、同日 152、読先行 6。**残った実在候補は起動パケットへの在場そのものである。**
- **M4 対完成度**（引継④の1回目）: d8 ≥ 20261126 の research_excerpt n=157 で cue 127 (80.9%)・pair 83 (52.9%)。20261126 バッチ n=111 は cue 97 = 87.4% で [fecf94](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/hypotheses.d/2026-11-26-000000000000.jsonl) の front-line 87.5% を再現、literary n=172 は 0%。20261127 バッチは収蔵群別に 0/10・10/10・20/20 と非均一で、**手掛かり付与は素材群でなく収蔵セッションに依存する。**

### 4.2 判定と仮説（すべて append-only 台帳に記録）

| ID | 対象 | 判定 |
|---|---|---|
| EVL-20261127-4eeab3 | HYP-20261120-58ddce | narrows_scope（field/segment 水準の消滅。spawned: HYP-20261127-351582） |
| EVL-20261127-ff16af | HYP-20261126-4e5813 | supports（除外(d) が非発火、作用点は hot/cold でなくパケット在場） |
| EVL-20261127-098b2e | HYP-20261126-fecf94 | supports（front-line 87.4% で 87.5% を再現、収蔵セッション依存を注記） |
| HYP-20261127-351582 | synthesizes [58ddce, 4e5813] | register=judgment、primary Q-003。**到達ゲートは gist 内容の露出ではなく起動パケットの在場にある**（除外条件 (a) 層内非有意化で棄棄、(b) パケット統制下の field 効果 z≥2 で gist ゲート復活、(c) 読先行 >50% で方向づけ棄棄） |

- 評価3件はすべて evidence_type=reproducible_script。スクリプトは SELF/CAP/OWN 錨つきで、台帳書き込み・マップ再生成後の再実行でも出力が報告値と完全一致することを確認した。
- 記録した行: SESSION×1、NOTE（[readings 報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-27-gist-gate-field-segment-and-packet-membership.md) = NOTE-20261127-06a667）、HYP×1、EVL×3、READ×20（ノート2・仮説4・評価3・セッション2・問い4・素材5）。
- 書き込み途中の是正2件: (1) HYP の scope_conditions を文字列ではなく配列に修正（schema/evaluation ではなく schema/hypothesis の array 要件）、(2) NOTE 行に cognitive_operation="inference" を追加（2026-11-21 以降の必須要件）。いずれも自セッションの新規行に対する修正で、origin/main の行には触れていない。

## 5. 検証

### 5.1 検証シーケンス（マップ再生成 →17項目、すべて PASS）

| 検査 | 結果 |
|---|---|
| belief_state --write-map / self_model --write / map_build.py | WROTE（BELIEF_MAP 479,075 B / SELF_MODEL 12,439 B / READING_MAP 1,792,438 B） |
| validate_seed | PASS（sessions=1,198, read_log=17,941, notes=1,353, hypotheses=125, evaluations=1,047） |
| append_only_check | PASS（origin/main の37,041行がバイト単位で保持） |
| readings_integrity_check | PASS（存在しない readings を指す note 行0件） |
| inspect_inquiry --check-map | PASS（READING_MAP は state と同期） |
| belief_state --check-map | PASS（BELIEF_MAP 現行） |
| self_model --check | PASS（現行かつ意味不変条件を保持） |
| note_index --check | PASS（ノート索引1,250件が現行） |
| read_log_backfill --check | PASS（全 context 素材に行あり。層2 = 6,974/9,420 = 74.0% は情報提供） |
| date_axis --enforce-shards | PASS（前方日付シャード0件、today=2026-11-27） |
| learning_metrics --check | PASS（学習・反証・時系列・配線ゲートすべて充足） |
| three_gates --check | PASS（PSC/dedup/lineage、P_gate 正規化、非融合リンク保存） |
| memory_tiers --check | PASS（epoch_manifest 1,001 frozen files、L1 digests5件検証） |
| size_budget --strict | PASS（全ソフトリミット内） |
| unittest discover | exit 0（全テスト合格） |
| EVL 再現スクリプト再実行（3本） | 報告値と出力完全一致 |

### 5.2 文字検証（中国語固有漢字・ハングル・デーヴァナーガリー・キリル・ギリシャ語ノイズ）

委任された文字検証を、本ファイルと [readings 報告](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-27-gist-gate-field-segment-and-packet-membership.md) を対象に実施した。方法は [2026-11-25 報告 §6](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-25-cognitive-science-thought-memory-self-6e4355a8.md) の先例に倣う:（1）ハングル（U+1100–11FF, U+3130–318F, U+AC00–D7A3）、デーヴァナーガリー（U+0900–097F）、キリル（U+0400–04FF）、CJK 拡張 B 以降（U+20000+）、およびギリシャ（U+0370–03FF）・アラビア・タイ・ヘブライの各ブロック走査、（2）簡体字固有形の代表集合との照合、（3）本ファイルの CJK 漢字集合が既存の追跡対象日本語コーパス（`git ls-files` の *.md、1,235 件）に既出かどうかの照合。

実行結果: **ハングル0件・デーヴァナーガリー0件・キリル0件・CJK 拡張 B 以降0件・ギリシャ0件・アラビア/タイ/ヘブライ0件**。簡体字代表集合の一次スキャンで19種（体内却号将当数断条来残点状画着辞重量静）が候補として挙がったが、いずれもコーパス既出の日本語常用漢字であり簡体字固有形の混入ではない。CJK 漢字は readings 報告315種・本ファイルの全種がコーパスに既出（未出0件）。**混入は検出されず、修正は不要だった。** ギリシャ文字は本ファイルに出現しない（統計はラテン文字の z・p で記載）。ハングルや簡体字を含む題名の素材（MAT-LIT-20270126-46283e、MAT-EVD-20270126-81951c 等）は本文に引用していない。

## 6. 申し送り

1. **引継④（claim 配線 44.1% 対 eval 83.0% の原因）** と **引継③ type×era 交差**、**引継⑤ M2 citation covariate** は未着手（本回は引継①に全日を充てた）。
2. **Q-20261130-caf330**（提示問い）は未 pursue。無意味名の反復＝儀式床の延長として、次回の source reading で直接 HYP を切るか、中心三問の子から接続するかを決める。
3. **editorial_review（README 詳細窓の回転）** は未実行。窓の現状と回転基準を次回確認。
4. **orphan_over_narrowed 8件**（Q-001 系 c8df23/69a149、Q-003 系6件）は条件付き子を切るか統合するかの判定待ち。
5. **HYP-20261127-351582 の除外(a)**（層内在場=不在の |z|<1.96）は registry/active のパケット不在 n=27/54 で現時点は検定不能。CAP 更新後の再測定を要する。
6. **20261127 バッチの収蔵群別非均一**（cue 0/10・10/10・20/20）は収蔵プロトコル側の handoff 候補。

## 7. リンク（本リポジトリ）

- 委任と手順: [`prompts/start.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/start.md)
- 本回の測定報告: [`readings/2026-11-27-gist-gate-field-segment-and-packet-membership.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-27-gist-gate-field-segment-and-packet-membership.md)
- 本報告: [`docs/2026-11-27-token-budget-plan-gist-gate-packet-membership.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-27-token-budget-plan-gist-gate-packet-membership.md)
- 前線引継①の原典: [`readings/2026-11-26-cues-pairs-and-the-ritual-floor.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-26-cues-pairs-and-the-ritual-floor.md)、[`readings/2026-11-26-selection-cue-gate-conditional-presence.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-26-selection-cue-gate-conditional-presence.md)
- 前回の同委任の実行例: [`docs/2026-11-26-token-budget-plan-selection-cue-gate.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-26-token-budget-plan-selection-cue-gate.md)
