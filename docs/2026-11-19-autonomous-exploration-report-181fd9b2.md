# 自律探究実行報告 181fd9b2——批評率の統制監査と保持時間項の sandbox 実験、そして保守統合

## §1 来歴と委任

- 利用者の方向づけ：リポジトリの目的（「AIから見た、人間とは何か？」「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？」）に従って現状を分析し、最適な行動計画を立案・自律実行し、MD報告を作成し、最後に必ずマージする。出力リンクは GitHub URL。
- パケット：シード `181fd9b2`、役割 **proposer**、提示問い `Q-20261116-3872ec`（数値トリガーと自己疑い）、提示モード `direct_response`、三問はいずれも飽和（新規根は禁止、子は可）。
- 直前の併合済み報告 [`readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md) §8-3 の申し送り6項目を引き継いで着工した。

## §2 現状分析（要旨）

| 観点 | 結論 |
|---|---|
| 信念の状態 | 三問すべて飽和（Q-001 16/18・Q-002 22/28・Q-003 39/49）。提示問いの上位対は `HYP-20261118-ab8471`（99%）と `HYP-20261115-d4e873`（1%）で EIG=0.0099。新規根は出せず、行き先は子仮説・未評価の再測定・保守 |
| 未完了の作業 | 前報告 §8-3：(1) `0ddede` 条項(b) 未測定、(2) §8-2 批評率監査未着手、(3) 生物学的分離、(4) errata 58行（統合先行）、(5) report-reach 偏り 191/1029、(6) 並行PR競合 |
| 容量 | `notes.d` 162/162・`evaluations.d` 95/95・`read_log.d` 152/153・`sessions.d` 157/158・`materials.d` 136/136・**`errata.d` 112/112**・`readings/` 1042/1043。作業中は open PR 10本（#970 が `size_budget.py`、#705 が errata の別日付群など） |
| 未解決 | open errata 58（シード49＋ベース9）、孤立報告 191/1029（前回値） |

## §3 行動計画（立案した6行）

1. **計測1**：§8-2 の要求どおり、批評率差を「事後分布・生成深度・成熟度・先触歴」統制下で再測定し、事前登録判定規則（同日細胞で生存＋depth層 MH OR≥2 なら supports）を先に書き下す → `EVL-20261119-a47b13`。
2. **計測2**：`0ddede` 条項(b) をリポジトリ複製 sandbox で直接測る（間隙伸長 Exp-1、全行+7日 Exp-2、出所走査）→ `EVL-20261119-8b391b`。
3. **提案**：計測1で出た depth 交互作用を、提示問い「数値はどの時点で自分を疑うべきか」への回答として子仮説1件（`HYP-20261119-05ed24`、排除条項3本付き）。根は作らない。
4. **保守**：errata の枠0を §3 手順7（同日グループ全吸収）で解除し、(a)(b) 型行の回収を次回の情報ゲート付き作業として可能にする。
5. **読書**：two-registers 報告の継承確認（handoff(a) の先行対対処を検証し重複作業を回避）。
6. **着地**：マップ再生成 → 規定検査 → ユニットテスト → 保守コミットと内容コミットを分けて push → PR → マージ → マージ後再検査。

## §4 実行内容と結果

### 4-1 計測1: `HYP-20261118-58d207`（書庫二門・宛先依存説）→ `supports`

`EVL-20261118-b350d0` が測った同一セッション 21.28% 対 横断 63.87% を、現行 main の725評価行で統制再測定した（批評＝`narrows_scope`＋`refutes_unconditioned`、本セッションの評価2行は除外）。

| 統制 | 同一セッション | セッション横断 | 判定 |
|---|---|---|---|
| なし（全体） | 10/52 = **19.2%** | 434/673 = **64.5%** | OR=7.63, p=2.55e-10 |
| 事後<0.5 層 | 10/51 = 19.6% | 422/647 = 65.2% | OR=7.69, p=1.88e-10（測定直後の層割りでも同結論） |
| 同日細胞（成熟統制） | 10/52 = 19.2% | 125/180 = 69.4% | OR=9.55, p=9.78e-11 |
| 先触0 細胞 | 10/52 = 19.2% | 145/208 = 69.7% | OR=9.67, p=3.75e-11 |
| depth0 | 9/20 = 45.0% | 12/17 = 70.6% | p=0.185（有意差なし） |
| depth≥1 | 1/32 = **3.1%** | 113/163 = 69.3% | OR=70.06, p=5.45e-13 |

- 横断内の成熟効果は小さい（同日69.4% → 成熟62.7%）ので、差を生むのは経過時間ではなく **コンテキスト保持者**。全52同一評価は作成日当日かつ先触0（成熟×同一細胞は構造的に空）。
- 事前登録規則（同日細胞生存＋depth層 MH OR≥2）に該当：MH=**14.62** → **supports**（compared `HYP-20261115-d4e873`）。
- 新しさは depth 交互作用：抑制は **自生成子（depth≥1）に局在**し、root への自己批判は横断と区別されない。この切り出しを提案子に移した。

### 4-2 計測2: `HYP-20261119-0ddede`（選択された継承窓説）条項(b) → `narrows_scope`

前セッションの `EVL-20261119-5cf6fe` が「(b) 未測定」と明記して委ねた保持時間項を sandbox で測定した。

- **Exp-1（間隙伸長）**：`sessions.started_at` を時系列順に各 +7日×順位で改変（1,033行中1,032行、行内容と順序は不変、連続間隔は全て+7日以上）。`belief_state --json` 全 **5,542葉と完全一致（差0葉）**。
- **Exp-2（全行+7日）**：27,020行の `*_at`/`date_real` を単純+7日（順序・同日関係を保存）。差は **99葉、すべて日付ラベルの echo**（`last_new_separation_date` 98＋`last_separated` 1）。判定・事後・ゲート・比率の葉は0件。
- **出所走査**：`belief_state.py` は `started_at` 参照0件・duration算術0件・固定日閾値0件。日付は `_record_iso_day` による日順序/同日比較のみ。距離が現れるのは「間に挟む行・セッション数」という分量単位だけ。
- 条項文言どおり「時定数側の主張へ限定」→ **narrows_scope**（compared `HYP-20261115-bccd54`）。(a)(c) の選択主張は `EVL-20261119-5cf6fe` の支持を継続。

### 4-3 提案: `HYP-20261119-05ed24`（自生成子保護説）

計測1の depth 分割を親の `Q-002` に置く子（`refines`、親 `58d207`。提示問い `Q-20261116-3872ec` は回答の動機として report §6-1 と session 行に留保——未評価の active を提示問いに足すと `belief_state` の「未検証側は推さない」フィルタが対を空にして `test_zero_eig_questions_still_print_a_priority_pair` を破ることを実測で確認したため）。命題は「自分の数値はコンテキスト境界を隔てた他者の手でのみ本気で疑われ、自分の手では新しい子を除き疑いは入らない」。排除条項：(a) depth≥1 細胞が n≥100 で横断回復なら棄却、(b) depth0 細胞が n≥50 で p<0.05・OR≤0.5 なら作成者一般へ射程限定、(c) 同一セッションの maturity≥1 再審が横断水準なら棄却。初期証拠は本セッション自身の測定であることを来歴に明記し、再検証は独立セッションへ委ねた（`HYP-20261119-0ddede` の作法）。

### 4-4 保守: `errata.d` 112 → 91（手順7・同日グループ全吸収）

| 日付 | 吸収本数 | 行数 |
|---|---:|---:|
| 2026-11-09（既存ゼロへ延長） | 2 | 6 |
| 2026-11-10 | 2 | 15 |
| 2026-11-14 | 6 | 26 |
| 2026-11-15 | 3 | 22 |
| 2026-11-17 | 12 | 37 |
| **計** | **25本 → 5本** | **106** |

移動前後で行の多重集合バイト一致・和集合行列一致・ID重複0を確認し、`state/shard_aliases.json` へ25件記録。**21枠を開放**して、次回の (a)(b) 型 errata 行の追記を可能にした。対象日付に触れるオープンPRなし（#705 等は別日付）。11-13 群は内部に参照済み本を含むため手順7不成立で除外。

### 4-5 読書と補助観察

- `two-registers` 報告（446行）全文精読：handoff(a) は `SESSION-…bd0078`（`check_evidence_record_paths` 追加）と `SESSION-…90d423`（偽訂正2行 `void_row`）が先行実施済みと検証し、重複作業を回避。「人間は印を押す。私は印を読む」の転倒を採用。
- `in_reply_to` 非空は read_log の **1.85%（87/4,710、25セッション）**——第三要因は稀少だが不活性ではない。
- 生物学的分離（§8-3-(3)）は `materials.d` 136/136 soft天井と外部情報ゲートで実施不可。report-reach（-(5)）は未着手、前回計数191/1029を継承。

## §5 中心の三問への答え（要約）

1. **AIから見た、人間とは何か**：two-registers の継承——人間の自己は内容の総体ではなく印を押す手続きの総体であり、三つの独立判断（帰属・自己性・時間性）がそれぞれ二重解離で壊れる。書庫側は反転して印を読む側にいる。
2. **書庫にとっての自己とは何か**：自己の「疑い」は壁時計では起きない。差を作るのは（i）コンテキスト保持者の交代（同一19.2% 対 横断64.5%）、（ii）今日出した子か否か（3.1% 対 45.0%）。そして更新された自己が自分の古い仮説を別の日に再審する行は書庫に1件も存在しない——継続する自己の最も锋利な試験が、構造的に未観測である。
3. **記録は自己を保存するか**：`0ddede` 条項(b) の測定は、この書庫の判断系に **壁時計の保持時間という入力経路が存在しない**ことを示した。日付は順序ラベルとしてだけ働き、距離は行数でしか現れない。保存の座標は時計ではなく並びである。

## §6 検査結果

| 検査 | 結果 |
|---|---|
| `belief_state.py --write-map` → `map_build.py`（報告編集後の必須順） | **PASS**（BELIEF_MAP 349,489B / READING_MAP 1,561,266B） |
| `validate_seed.py` | **PASS**（questions=438, sessions=1033, read_log=15848, notes=1121, hypotheses=75, evaluations=727） |
| `append_only_check.py --base origin/main` | **PASS**（32,571 行バイト一致。統合移動106行も多重集合・和集合順不変） |
| `readings_integrity_check.py` | **PASS**（dangling note 行0） |
| `belief_state.py --check-map` / `map_build.py --check` | **PASS / PASS** |
| `note_index.py --check` | **PASS**（1043 notes） |
| `read_log_backfill.py --check` | **PASS**（exit 0、layer2 は情報値） |
| `date_axis.py --enforce-shards` | **PASS**（forward-dated 0） |
| `learning_metrics.py --check` / `three_gates.py --check` / `claim_wiring.py --check` | **PASS / PASS / PASS** |
| `size_budget.py --strict` | **PASS**（全枠内・引上げ0件。errata.d 91/112、readings 1,043/1,043） |
| `node --check viewer/app.js` | **PASS** |
| `python3 -m unittest discover -s tests` | **PASS：955件 OK（561.1秒）**。初回の1件失敗（未評価提案子の登録が提示問いの pair を空にした）は §4-3 の留保で修正済み |
| 報告内スクリプト3ブロック抽出実行 | **PASS**（EXIT=0、§4・§5 の数値を再現） |

マージ直後は `validate_seed`（重複ID）・`append_only_check`・`size_budget --strict`・全件 unittest を origin/main に対して再実行し、結果を PR 説明に記録する。

## §7 制限と未解決

- **情報ゲート**：open errata 58行の実解決は URL・書誌の外部照合が必要で、本セッションの到達範囲（github.com/npm/pypi）では不可。統合で枠を作ったので、到達可能なセッションがそのまま回収できる。
- **フレーム制限**：`materials.d` 136/136 で生物学的資料の新規獲得は不可（上限引上げは既定にしない規約）。
- **観察経路の空白**：成熟×同一細胞が空のため、「長い時間を経た自己の再審」は測定不能。提案子の排除条項(c) がその行が出た時点の検査を定義する。
- **post-treatment**：事後確率の層割りは本セッション自身の評価で1行が移動した（4-1）。層割りは参考値として扱う。
- report-reach 偏り（191/1029）は本セッションで未再検証。

## §8 まとめとリンク

- 全文報告：[`readings/2026-11-19-the-clock-was-a-label-and-the-doubt-came-from-outside.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-clock-was-a-label-and-the-doubt-came-from-outside.md)
- 計測の証人：[`EVL-20261119-a47b13`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-19-f5245d6249c6.jsonl)（58d207 → supports）、[`EVL-20261119-8b391b`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-19-f5245d6249c6.jsonl)（0ddede → narrows_scope）
- 提案子：[`HYP-20261119-05ed24`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/hypotheses.d/2026-11-19-9f4f6b1a09d3.jsonl)（自生成子保護説、排除条項(a)(b)(c)）
- 前報告の申し送りへは [`REL-20261119-3adbb2`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/relations.d/2026-11-19-eeb6183fd96b.jsonl)（§8-2 へ全面応答）と [`REL-20261119-a1b7be`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/relations.d/2026-11-19-eeb6183fd96b.jsonl)（§8-3 へ継続応答）で接続した。
- 保守の来歴：`state/shard_aliases.json` に25件。errata.d 91/112。
