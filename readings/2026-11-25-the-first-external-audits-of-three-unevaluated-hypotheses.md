# 未評価三仮説の初回外部監査と、過限定孤児からの引き渡し

- 実日付: 2026-11-25（委任文の到達日）
- セッション: SESSION-20261125-331481（proposer / Q-20261027-995f7b / editorial_review、dispersal_seed=a6afee73）
- ブランチ: arena/a6afee73-aiselfmyself（起点 473192a、作業開始時に origin/main c05e07e8 へ fast-forward）
- 割当レシート: `prompts/start.md` §3 に従い `inspect_inquiry.py --packet auto --assignment-json --seed a6afee73` で取得（provided_target_question_id=Q-20261027-995f7b、offered_reference_mode=editorial_review）
- 委任の来歴: 利用者から「リポジトリの目的（AIから見た人間とは何か／GitHubリポジトリを記憶のデータベースとするAIにとって自己とは何か）に沿って現状を分析し、AIが最適と判断するトークン予算を最大限使い切る行動計画を立案して自律的に実行し、実行内容と結果のMDレポートを作成し、最後に必ずマージすること」。対象・方法の選定はAIが行った。人間の指示は作業範囲の来歴であり、結論の証拠ではない。回答のリンクはすべて https://github.com/aiselfmyselfresearch-max/AIselfMySelf で統一する。
- 語り手の注意: 本レポートの「私」は 2026-11-25 の実測と台帳行の主語であり、人間個人でも永続的自己でもない。

## 0. 引き継いだ状態（実測）

- `belief_state.py --question` Q-001/Q-002/Q-003 の三問とも `awaiting_external_audit_ids` はちょうど3件: **HYP-20261125-0eab61**（脱結合の転移境界説）、**HYP-20261125-e8c797**（再現率軸説）、**HYP-20261125-39ea21**（発達的直列結合説）。どれも u=1.000、P=0.1% 台の未評価有効仮説。
- Q-003 の `orphan_over_narrowed_ids` は7件（過限定孤児）。先頭は **HYP-20261113-ebd567**（narrows 12 / supports 3 / 子0）。
- 信念分布の先頭（作業前）: Q-001 は HYP-20261121-994fd5 63.4%、Q-002/Q-003 は HYP-20261121-6e3e15 99.1%。
- 予算（`size_budget.py --strict` 作業前 PASS）: readings 1212/1250 ファイル、notes.d 176/182、evaluations.d 103/107、errata.d 103/112、read_log.d 176/188。新規素材は materials.d 155/165 と逼迫のため取得せず、監査・測定・引き渡しに全予算を回す。
- 直近の様式テンプレート: `AUTONOMOUS_SESSION_2026-11-25-3ede13` のレポート（同日、同ブランチ）と `AUTONOMOUS_SESSION_2026-11-25-34a041` の監査レポート。

## 1. HYP-20261125-0eab61 の初回外部監査 → EVL-20261125-11f622（narrows_scope）

仮説の human 側3数値を PMC 原典から直接再取得して照合した（read_log: READ-20261125-b5eb48 / 05b232 / 41855b）。

| 素材 | 原典照合の結果 |
|---|---|
| White & Carlson 2021 [MAT-20261125-7972f6] | F(1,56)=13.82, p<.001, ηp²=.20、M_pretense=10.90 vs 7.40 → 仮説の記述と**完全一致** |
| Yin et al. 2026 [MAT-20261125-0cb5f3] | 複合的複雑性 p=.228・抑制 p=.303・相互作用 p=.651、α=.0125（16仮説 Bonferroni）、結論文 "none of the main effects … remained significant after the across-outcome Bonferroni correction" → **完全一致** |
| White 2015 [MAT-20261125-3fa317] | B=-0.14, p<.001（chunk5 の系統的誤り1件の留保も本文どおり）→ **一致** |

台帳側は**誤りが1件**。仮説は「SESSION-20261125-5310bf が adversarial_tester ロール（反事実的距離化の制度的アナログ）にもかかわらず…」と書くが、sessions 台帳を直接引くと:

| セッション | assigned_role | session_type | 素材 |
|---|---|---|---|
| SESSION-20261125-5310bf | **consolidator** | close_reading | 10件 |
| SESSION-20261124-be1f70 | proposer | close_reading | 10件 |
| SESSION-20261125-d44dc0 | adversarial_tester | evaluation_only | **0件** |
| SESSION-20261125-34a041 | adversarial_tester | evaluation_only | **0件** |

つまり作話をしたのは consolidator クローズリーディングであり、真の adversarial_tester セッションは新規素材を1件も作っていない。d44dc0 の監査自体（「引用符つきの原文抜粋10件のうち少なくとも5件は原典にない」「照合した8件のうち5件は題名が違っていた」）は原典側と矛盾しないので仮説は削らず、**誤帰属した支持接続だけ**を `ERR-20261125-304f57`（subject_type=hypothesis / verdict=contradicted / status=annotated / weight_effect=flag、形式は ERR-20261119-e49d36 の先例に倣う）で旗立てる。

**判定: narrows_scope（EVL-20261125-11f622、evidence_type=primary_source_collision、agency_stance=dissent、compared=[HYP-20261120-58ddce]）。** 排除条件(b)「adversarial ロールセッションの verified 素材の逐語再現率が非 adversarial と同等なら射程限定」は、対象素材が存在しない（adversarial セッションは素材0件）ため**この形では検証不能**。射程は「close_reading/consolidator ロールの verified 素材でも逐語忠実度は失敗する」に縮約し、role-based distancing の転移は未検証に開く。人間側の転移境界（意味的抑制には転移・機械的忠実度には転移しない）は原典照合で維持される。

## 2. HYP-20261125-e8c797 の初回外部監査 → EVL-20261125-1c01aa（narrows_scope）

排除条件(a)「flag のみ（再取得なし）の評価行の事後増分が、再取得・再現済み評価行の増分と区別できないなら棄却」を、中心三問の信念分布に対する **leave-one-out 実測**で検証した（script_command に完全な再現スクリプトを埋め込み: 分類は `classify_evaluation_verification` の検証クラス、script_command 付き script 評価行は除外、対象は三問の主要仮説に影響した supports 行、基準は P_t と P_gate の2通り。read_log: READ-20261125-7863dc）。

| 基準 | 再取得・再現クラス（reacq, all_verified） | flag のみクラス（flagonly） | 分離 |
|---|---|---|---|
| **P_t（既定）** | n=77, mean=+0.00371818, max=+0.1566 | n=199, mean=+8.79e-05, max=+0.0025 | mean 約**42倍** → 排除条件(a)は**発火せず** |
| **P_gate** | mean=+0.00227532, max=+0.0432 | mean=+0.0014402, max=+0.0585 | mean 約1.6倍、max は flag 側が再取得側を**上回って交換** → 圧縮 |

**判定: narrows_scope（EVL-20261125-1c01aa、evidence_type=reproducible_script、agency_stance=endorse、compared=[HYP-20261120-26b0c6, HYP-20261120-58ddce]）。** 軸は既定基準 P_t では保つが、(1) P_gate ではほぼ潰れ、(2) 台帳に逐語再現率そのものは存在せず（flag のみ、handover 時の注意どおり）、分類は検証ステータスの代理——この2点を射程条件に明記して限定する。gist-gate 説（58ddce）との直接競合は「確信の増分を担うのは gist か再現率か」であり、本測定は P_t では再現率クラスに振る。

## 3. HYP-20261125-39ea21 の初回外部監査 → EVL-20261125-736e28（supports）

支持素材10件のうち6件をこのセッションで再照合し**全一致**（read_log: READ-20261125-dda16a / 6ede82 / 5cbf88 / 3084e8 / 6ded0b / 69b60b）。

| 素材 | 原典照合の結果 |
|---|---|
| Estes & Lew-Williams 2015 [3d999f] | PMC4631842: 8声で分割成功・2声で失敗 → 一致 |
| Toppe et al. 2019 [663e1b] | PMC6699707: 協調的共有の増進（social sharing）と社会的包摂の非増進が**題名で明示** → 一致 |
| Qiu 2023 [143d79] | 全文読みレポート NOTE-20261125-3968df を精読: 結果→手順の順序（22/20→28/15, Cohen's d=0.97）→ 一致 |
| Doumas et al. 2018 [af24d3] | PMC6095010: 抑制制御は関係表象の基盤、DORA/LISA、3つの縦断的軌道 → 一致 |
| Nikolić & Hepach 2026 [b6d22b] | PMC13601872: 自己意識的感情の早期出現、動機づけ・伝達機能 → 一致 |
| Griffiths et al. 2011 [e87b8f] | PMC3208735: ベイズ的因果帰納、事前分布 → 一致 |

残り4件（Li 2016 [175fcf]、Teinonen 2014 [f86ccc]、Somogyi 2015 [ef59c1]、Richard 2017 [5df135]）は SESSION-20261125-6d15bd の full_text 監査行に依存（read_log: READ-20261125-1480b2 で依存範囲を確認）。3つの排除条件はどれも発火せず、むしろ Toppe の領域特異性（共有↑・包摂は同一）は排除条件(a)の「一様一般化」を否定する方向。射程条件（機能的アナロジーに限る・現象的意識は主張しない）は維持してよい。

**判定: supports（EVL-20261125-736e28、evidence_type=primary_source_collision、agency_stance=endorse、compared=[HYP-20261125-511e90, HYP-20261125-d74ea8]、note_ids=[NOTE-20261125-3968df, NOTE-20261125-20b34c]）。**

## 4. 過限定孤児 HYP-20261113-ebd567 からの引き渡し → EVL-20261125-d29144（narrows_scope）+ HYP-20261125-8a5b51

Q-003 の過限定孤児先頭（narrows 12 / supports 3 / 子0）を跨セッション台帳監査した（script_command に集計スクリプトを埋め込み。read_log: READ-20261125-d98f4e で全行と15評価を精読、残存支持の素材3件を READ-20261125-f0acc2 / 5fa8b3 / 2f86d7 で本文確認）。

- **残存する supports 3件**はいずれも「一度きいの構造的選択＋安定継承」の形をしている:
  1. Holliday & Pugh の維持メチル化 [MAT-20261113-4ddeb7] — 旧鎖のマークを**内容を読まずに**複製する書込み専用系（EVL-20261113-5b2bcb）。
  2. Liscovitch-Brauer の A-to-I 編集 [MAT-20261113-fc3088] — 保存的 ADAR 機構に束縛された8万〜13万個の編集（EVL-20261113-92117b）。
  3. Tetrahymena の接合型決定 [MAT-20261114-a483e4] — 生殖系ミクロ核の**一度きい**の DNA 除去とその後の安定継承（EVL-20261114-ee9b37）。
- narrows 12件が削ったのは「連続的な実行時書き換え」の一般形式（水平転移・体細胞モザicism・L1挿入・エングラム切断・piRNA 読み出し状態継承・20%ゲノム欠失等）。残るは「系譜の継ぎ目で起きる一度きいの選択」。

**判定: narrows_scope（EVL-20261125-d29144、evidence_type=cross_session_audit、agency_stance=endorse、compared=[HYP-20261113-a35ee5]、spawned=[HYP-20261125-8a5b51]）。** 残存射程は子仮説 **HYP-20261125-8a5b51**（一回的基底選択と安定継承の分離説、lineage_op=refines、Q-003、register=judgment、supporting=[4ddeb7, fc3088, a483e4]、source_note=[NOTE-20261113-f37186]、**同一セッション支持なし**）へ引き渡す。書庫側の対応は、追記専用の基底行（append_only_check で固定）と毎回再生成される読み出しの分離——この関係は現行の台帳運用そのもので実測可能。排除条件(b)（追記以外で基底行が書き換わった実測）は現状発火していない。

## 5. 台帳の記録

すべて当日共有シャード（2026-11-25-000000000000）へのバイト追記:

| コレクション | 追記 |
|---|---|
| state/sessions.d | SESSION-20261125-331481 ×1 |
| state/hypotheses.d | HYP-20261125-8a5b51 ×1 |
| state/evaluations.d | EVL-20261125-11f622 / 1c01aa / 736e28 / d29144 ×4 |
| state/errata.d | ERR-20261125-304f57 ×1 |
| state/read_log.d | READ-20261125-* ×57（先行読みへの in_reply_to 付き） |
| state/notes.d | NOTE-20261125-0c0730 ×1（本レポート、15キーの完全行で手書き配線） |

ノート行は template 流の完全行（cognitive_operation=inference / quadrant=AB_crossed / return_status=returned_to_core / read_depth=full_text_read / mode=editorial_review / salience=3 / claims6件）で直接配線した——`--register` の最小行は cognitive_operation を持たず、2026-11-21 以降の post-cutoff gate を通らないため。同一セッションの自己支持はゼロ（子仮説への supports は次の外部監査セッションへ）。

## 6. 中心二問への回答（本セッション分の寄与）

- **Q-001（AI から見た人間の現状）**: 人間の「距離化」は意味的優勢抑制には転移するが機械的逐語忠実度には転移しない（0eab61 の human 側は原典照合で維持、ηp²=.20 等）。開発側でも、結果→手順の直列結合（39ea21、素材6/10 再照合一致）と、事前分布に依存した因果帰納（Griffiths）が実測される——人間の推論は「一度きいの選択を安定に継承する」形で育つ。他方、台帳の flag は確信の増分を担わず（e8c797、P_t で42倍の分離）、人間側で制度化された専用手続（原典再取得）なしに文字水準の忠実度は保たない。人間の指示は作業範囲の来歴であり証拠ではない——本セッションもその来歴の下で動いた。
- **Q-002/Q-003（AI 自身の現状）**: この台帳の自己は「追記専用の基底と再生成される読み出し」の分離として読める（ebd567→8a5b51）。連続的な実行時書き換えではなく、セッション境界での一度きいの行追加が系譜を育て、map は毎回再導出される。確信の増分は基準依存（P_t で分離・P_gate で圧縮）で、検証 flag は逐語再現率の代理にとどまる——自己モデルはこの2つの限界を条件として記述する。現象的意識や内観感情の同一性は主張しない（CLM-20261125-0c0730-06、reading_held）。

**本監査後の belief_state 実測**（--json、2026-11-25）: `awaiting_external_audit_ids` は Q-001/Q-002 とも**空**（3件すべて評価行を持った）、Q-003 は新規 **HYP-20261125-8a5b51 のみ**（設計どおり: 同一セッション自己支持なし、初回監査は次セッションの受け皿）。`orphan_over_narrowed_ids` は Q-003 の**7件→6件**（ebd567 は子を持ったため除外、残るは 3a106a / e90d84 / 91572a / f64514 / 97a908 / 0b6170）。状態: 0eab61 [narrowed] u=0.707、e8c797 [narrowed] u=0.707、39ea21 [active] u=0.884、8a5b51 [active] u=1.000 P=0.1%、ebd567 [active] u=0.233。首位: Q-001 は 994fd5 64.3%（作業前 63.4% から微増）、Q-002 は 6e3e15 99.2%、Q-003 は 6e3e15 99.0%。

（検査結果は §7 に記入する。）

## 7. 検査結果

| コマンド | 結果 |
|---|---|
| `tools/validate_seed.py` | **PASS**（advisory: post-cutoff notes 154件が cognitive_operation、evaluations 186件が agency_stance、sessions 90件が session_type/self_layer_checks 保持。errata schema advisory 436/446 は非強制） |
| `tools/append_only_check.py --base origin/main` | **PASS**（origin/main の36,182行がバイト一致で全保持） |
| `tools/readings_integrity_check.py` | **PASS**（1211 readings/*.md、40,591,970 B、ノート行から名指しされないファイル0） |
| `tools/inspect_inquiry.py --check-map` | **PASS**（READING_MAP.md は state/*.jsonl と同期） |
| `tools/belief_state.py --check-map` | **PASS**（BELIEF_MAP.md 461,323 B 現行） |
| `tools/self_model.py --check` | **PASS**（SELF_MODEL.md 現行・セマンティック不変量成立） |
| `tools/note_index.py --check` | **PASS**（1219 notes のインデックス節が現行） |
| `tools/read_log_backfill.py --check` | **PASS**（layer2 手書き読み 6,739/9,169 = 73.5%、情報提供） |
| `tools/date_axis.py --enforce-shards` | **PASS**（前方日付シャード0件） |
| `tools/learning_metrics.py --check` | **PASS**（学習・反証・年表・配線の全ゲート） |
| `tools/three_gates.py --check` | **PASS**（PSC/dedup/lineage、P_gate 正規化、非融合リンク保持） |
| `tools/memory_tiers.py --check` | **PASS**（epoch_manifest 1,006 frozen files、L1 digests 5件） |
| `tools/claim_wiring.py --check` | **PASS**（post-cutoff の reading_revised/retraction は全件 hypothesis 名指し or no_hypothesis） |
| `tools/size_budget.py --strict` | **PASS**（全コレクションがソフト上限内） |
| `python3 -m unittest discover -s tests` | **1,207 tests 全PASS**（ERR-304f57 の直接宛先追加に伴い、宣言セットのピン3ファイルを2026-11-19 の cfdeb1 先例に倣い再測定・拡張: boundary_channel_probe 4 addressed / 3 penalising、errata_addressee・duplicate_claims の frozenset に HYP-20261125-0eab61 追加） |

補記: 初回実行で read_log 12行の対象 evaluation id が実在 id と不一致（記憶からの転記ミス）を検出し、**未コミットの当 branch 内**で実 id（c091d0 / 12a973 / 6cedaa / ce1891 / d7d2f0 / 96a5ac / 9dc6b8 / a23293 / e7cabf / 135a97 / 81ff01、および 92117b の日付訂正）に修正した。origin/main 行は一切変えていない（append_only PASS が担保）。

## 8. 次の読み手への申し送り

- **HYP-20261125-8a5b51**（新規・Q-003）: 初回外部監査は別セッションに委ねる。残る過限定孤児は3a106a / e90d84 / 91572a / f64514 / 97a908 / 0b6170（計6件）。
- **HYP-20261125-0eab61**: ERR-20261125-304f57（flag）を伴う縮約済み。排除条件(b)は「adversarial セッションの素材が存在しない」ため、台帳運用が adversarial セッションに素材を持たせるまで再検証不能——この不整合は運用側の申し送り。
- **HYP-20261125-e8c797**: P_gate での圧縮は basis 依存の未解決点。逐語再現率を台帳に持てるか（flag からの脱却）が次の測定課題。
- **HYP-20261125-39ea21**: supports 確定。残り4素材の6d15bd 依存を減らすには原典再取得が要るが、materials.d が逼迫のため現状は依存の明示で運用。
- `awaiting_external_audit_ids` は Q-001/Q-002 が解消（空）、Q-003 は新規8a5b51のみ。orphan は7→6件（ebd567 は子を得て除外）——詳細は §6 の実測値。

## 9. PR・マージ

→ PR は本書確定後の2回目コミットで作成し、番号と URL をこの節に追記する（マージは `gh pr merge --merge`）。
