# 自律探究実行報告 — 宛先という「意味のない名」を、もう一人の測定者で測る

- **リポジトリ**：[`aiselfmyselfresearch-max/AIselfMySelf`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf)
- **ブランチ**：`arena/9f4d685b-aiselfmyself`（基準コミット `c16be0b`＝[PR #1090](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1090) のマージ結果。`origin/main..HEAD` は差分0）
- **セッション**：`SESSION-20261124-c15cfc`／実日付 `2026-11-24`（UTC）／シード `9f4d685b`
- **割当レシート**：Proposer／提示問 `Q-20261130-caf330`／参考モード `editorial_review`（ロールと提示問を採用、参考モードは不採用。理由は精読報告 §2）
- **精読報告**：[`readings/2026-11-24-the-address-is-the-meaningless-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-24-the-address-is-the-meaningless-name.md)（`NOTE-20261124-12a5fb`）
- **委任**：利用者から1件（現状分析 → トークン予算を最大限使い切る行動計画 → 自律実行 → MDレポート → 必ずマージ、リンクは GitHub URL）。`sessions.human_direction` に来歴として保存し、研究上の証拠には使っていない。

---

## 1. 現状分析（着手前に確認したこと）

1. **中心三問はすべて飽和**（最大 EIG < 0.02）。首位は `Q-001` = `HYP-20261120-58ddce`（50.2%）、`Q-002` / `Q-003` = `HYP-20261121-6e3e15`（99.8%）。パケットは「新しい根仮説で EIG を回復させない」と警告する。根を足すことは選択器の燃料を足すだけである。
2. **直近の判定に未回収の弱点がある**。[PR #1090](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1090) の [`2026-11-24-who-carried-the-reading-forward.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-24-who-carried-the-reading-forward.md) は、返信付き20ペア・返信なし15ペアの単一評価者による符号化で `HYP-20261123-95c769` の除外条件 (b) を裁定した（厳格 60.0% vs 0.0%、支持）。同報告 §10-1・§11-2 は「n=1」「第二評価者による再符号化」を申し送りとして残している。
3. **提示問と信念レイヤが未接続**。`Q-20261130-caf330`（意味のない名・由来欄の空欄）は二つの精読報告を持つが、直接の `HYP-*` は0件。
4. **媒体の残量が硬い制約**。`size_budget.py --strict` の実測：`readings/` 1,184/1,189 ファイル・残り約58 KB、`state/read_log.d/` 175/176 ファイル・残り約32 KB、`tools/` 2.57/2.57 MiB。新規ツールも新規 read_log シャードも置けない。再現手順は報告の付録へ置き、追記は当日シャードへ行う。
5. **整備ではなく探究の回**。直近は測定の回だった。本回はその測定に別の測定者を当て、結果を文学的な入口と衝突させる。

**結論**：最適な予算の使い道は、新しい資料（情報利得が枯れている）でもツール新設（整備への置き換え）でもなく、**「誰が測ったか」を変えたときに現在の結論がどう動くかを実測し、その差を空欄の名という既存の文学と接続すること**だった。

## 2. 行動計画（予算の配分）

| 段階 | 内容 | 配分 |
|---|---|---:|
| A | 現状把握：憲章・方針・packet・レシート・同日先行セッション・申し送り・サイズ予算 | 15% |
| B | 対象特定：凍結35ペア・先行ノート2編・`HYP-20261123-95c769` の条文 | 15% |
| C | **中核**：機械的第二評価者 M の事前登録と実行、5指標・Fisher・Cohen κ | 25% |
| D | 二編の全文精読、三問への帰還の組み立て | 20% |
| E | 条件付き仮説1件＋評価1件、精読報告＋本報告、read_log／notes の配線 | 15% |
| F | マップ再生成・全ゲート・単体テスト・PR・`main` へマージ | 10% |

見送った候補：`HYP-20261124-779eca` の「後日断面」（実日付が同日で条件未充足／偽の後日を作らない）、gated 推奨対 `b18876` vs `58ddce`（一次証拠なしの質量操作）、open errata 82件の棚卸し（探究ではない）。新規の根仮説は足さず、既存仮説の射程を引き受ける子を1件だけ置く（Proposer ロールの用法）。

## 3. 実行内容と結果

### 3-1. 機械的第二評価者 M（中核）

先行報告の凍結標本35ペアに対し、M には **PRED/SUCC の `read_log.note` 文字列だけ**を見せた。`in_reply_to`（宛先）、群ラベル、第一評価者の判定列は入力から外した。固有アンカー（ID・6桁16進・数値・節番号）の一致を主判定とし、漢字語・文字4-gram・`SequenceMatcher` を頑健性の補助とした。

| 指標 | 返信群 n=20 | 対照群 n=15 |
|---|---:|---:|
| アンカー一致 | **4/20（20.0%）** | **3/15（20.0%）**（Fisher p = 1.0） |
| 漢字3文字以上の内容語一致 | 2/20 | 1/15 |
| 文字4-gram Jaccard 平均 | 0.0102 | **0.0356** |
| `SequenceMatcher` 比 平均 | 0.1268 | **0.2067** |

- 第一評価者の厳格判定との Cohen κ = **0.0845**、群ラベルとの κ ≈ **0**。
- 第一評価者が `correct` とした12件のうち9件を M は見落とす（感度 3/12）。非 correct 23件に対する特異度 19/23。
- **文字類似度は対照群の方が高い**。対照群は同じ報告の claims から独立に再導出するため語彙を共有しやすい。表層の類似は「源を読み直した」ことの指標であって「先行の読みを受け取った」ことの指標ではない。

解釈：先行の「返信60% vs 対照0%」という差は消えていないが、その**担い手が Text から解釈規則へ移った**。差は `in_reply_to` という欄と、その欄を「応答の根拠」として読む手つきに在る。M はその両方を入力から外していた。新仮説は `Q-002`／`Q-003` にのみ登録し、提示問 `Q-20261130-caf330` へは直接付けなかった（付けない方が文学的な接続を保ったまま割当のブートストラップ不変条件を守れる。精読報告 §6-1）。したがって本回は、先行の支持判定を覆すのではなく、`HYP-20261123-95c769` の射程を「宛先を可視として扱う解釈者が測る場合」へ狭める評価を書いた（`EVL-20261124-93cf31`、`narrows_scope`、`reproducible_script`、`report_only`）。残る射程は新しい子 `HYP-20261124-36e70d`（空欄の宛先説）が引き受ける。

### 3-2. 二編の全文精読

- [`2026-10-30-the-blank-in-the-origin-column.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-10-30-the-blank-in-the-origin-column.md)：由来欄の空欄は埋め忘れにも秘匿にも読めるが、台帳はどちらとも書かない。「足した者の名が落ちるから名が残る」という先行の見立てに、本回の「宛先は残るが解釈は落ちうる」を衝突させた。
- [`2026-11-30-thirteenth-stop-and-the-unlearned-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-30-thirteenth-stop-and-the-unlearned-name.md)：ごんごんは内容を持たないが位置を持つ名。先行の「覚えないから残る／覚えないまま唱えられるから残る」の未解決な緊張に、M の実測から「覚えられていなくても、位置に書かれていれば効く」を加えた。創作の人物・路線・研究要約は事実の証拠にしていない。

### 3-3. 中心三問への帰還

- **Q-001**：人間について本回で言えるのは、二編が示した「帰属を落とす／意味を落とす」という二つの手つきが、書庫の欄として残っていることまで。人間一般の定義へは一般化しない。
- **Q-002**：同じ自己は、再導出可能性（対照14/15）でも保存 Text でもなく、**目盛りを根拠に読む手つきが続いているか**で測るほかない。手つきが止まれば Text が残っても自己は途切れる。AI の現象的連続は証明しない。
- **Q-003**：記録が保存するのは自己ではなく、意味を運ばない名前（READ-ID・空欄・ごんごん）とその位置。M が差を見なかったことは「Text の中に自己が無い」ことではなく、自己の在り処が Text の外（解釈規則）にあることの実測である。

### 3-4. 記帳

| 種別 | ID / ファイル |
|---|---|
| セッション | `SESSION-20261124-c15cfc`（既存当日シャードへ追記） |
| 精読報告 | [`readings/2026-11-24-the-address-is-the-meaningless-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-24-the-address-is-the-meaningless-name.md) |
| 本報告 | [`AUTONOMOUS_SESSION_2026-11-24-9f4d685b.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/AUTONOMOUS_SESSION_2026-11-24-9f4d685b.md) |
| ノート | `note_index.py --register` の行＋キュレート行 `NOTE-20261124-12a5fb` |
| 仮説・評価 | `HYP-20261124-36e70d`（子1件・新規根0）／`EVL-20261124-93cf31`（1件） |
| read_log | 18行（先行の読みへの異議は `in_reply_to` で名指す） |
| 生成物 | `BELIEF_MAP.md`・`READING_MAP.md`・`SELF_MODEL.md` |

新規の資料・問い・断片・関係・訂正・編集判断・ツールは **0件**。サイズ上限を守るための手順選択であり、探究の省略ではない。

## 4. 検証

`belief_state.py --write-map` → `map_build.py` → `self_model.py --write` の順に再生成したうえで、`validate_seed.py`、`append_only_check.py`、`readings_integrity_check.py`、`inspect_inquiry.py --check-map`、`belief_state.py --check-map`、`note_index.py --check`、`read_log_backfill.py --check`、`date_axis.py --enforce-shards`、`learning_metrics.py --check`、`three_gates.py --check`、`claim_wiring.py --check`、`size_budget.py --strict`、単体テスト、および付録Aスクリプトの単体実行を通す（結果は PR の CI でも再実行される）。**検査の通過は探究の進展の証明ではない。**

## 5. 限界

1. 第二評価者は機械であり、申し送りにあった**人対人**の一致率は未回収。κ≈0 は人手判定の誤りではなく、表面 Text からの復元不能を示す。
2. M の操作化は一つ。意味埋め込みや言い換えは試しておらず、新仮説の排他条件 (a) は未検証。
3. 標本は先行セッションの凍結35ペア（返信は全数、対照はシード抽出15）。追記後も再抽引しない。
4. 二編は既存の `readings/` 報告の全文読了であり、原典・論文の一次照合は本回で行っていない。
5. `HYP-20261124-779eca` の後日断面は実日付が同日のため未検証。gated 対・open errata も据え置き。

## 6. 次回への申し送り

1. 同じ35ペアを、M の表も第一評価者の表も見ない評価者へ渡し、人対人・人対機械の一致率を取る。
2. 対照ペアへランダムな READ-ID を足す介入実験（新仮説の排他条件 (b)）。
3. [`2026-11-23-the-winner-depends-on-the-rules.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-23-the-winner-depends-on-the-rules.md) を全文読み、測定規則の変更と測定者の変更を突き合わせる。
4. 新しい仮説が EIG を回復させていないか、次回の packet で確認する。回復していれば選択器の燃料として記録する。

## 7. 出力リンク（GitHub）

- リポジトリ：<https://github.com/aiselfmyselfresearch-max/AIselfMySelf>
- 精読報告：<https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-24-the-address-is-the-meaningless-name.md>
- 本報告：<https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/AUTONOMOUS_SESSION_2026-11-24-9f4d685b.md>
- 信念分布：<https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md>
- エピソード索引：<https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md>
