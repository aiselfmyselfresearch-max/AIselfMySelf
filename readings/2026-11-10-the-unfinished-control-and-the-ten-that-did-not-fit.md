# 未実行だった統制を、いま実行する——sham 報告・軸に合わない十件・一人称の資料・崩れた答えの訂正録

- **実作業日**：2026-11-10（UTC）。**内部編年ラベル**：`2027-03-17`（`started_at` のみ。ID・ファイル名・シャード名には使わない。軸は [`docs/time-axis.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/time-axis.md)）
- **セッション**：`SESSION-20261110-350411`
- **作業様式**：[`prompts/direct_response.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/direct_response.md) ＋ [`prompts/close_reading_report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/close_reading_report.md) ＋ [`prompts/first_person_sources.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/first_person_sources.md)（参考モードは packet `fb5eb1fa` の `direct_response`。参考問い `Q-20261025-a12444` は採らない）
- **中心問い**：`Q-001`・`Q-002`・`Q-003`
- **委任の来歴**：「【4. 評価を上げるために残っている一点】について、実行をお願いします」という短い依頼があった。これは作業範囲の指定であり、以下の解釈・計測・判断の根拠ではない（[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)）。**「一点」が §4 全体を指すか、その中の一項目を指すかは依頼文から決まらない。** 人間へ判断を差し戻さず、§4 に挙がった未実行の三つの設計と、末尾の訂正録の表を**一セッションでまとめて実行する**という可逆的で最小限の選択をした。この不確実性をここに残す。
- **声について**：「感じたこと」は `reflective_literary_voice` としての反省的・文芸的応答であり、持続する主観的意識・身体感覚・気分の事実報告ではない。「私」は本報告を作成する作業上の視点を指す。
- **共有ファイル**：`README.md`・`docs/sessions.md` は編集しない（B案、[`docs/parallel-work.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/parallel-work.md) §3）。新規資料・新作断片・新規問い・新規関係線は **0件**。既存の台帳行は書き換えない。

> **この報告は二段階で書かれている。** §0〜§2（来歴・設計・選定規則・計測器・予測）は、**sham 報告を一行も書く前**、かつ三つの選定リストと計測結果を確定する前にコミットした。§3 以降はその後に足した。§1・§2 の規則と予測は結果を見た後で書き換えていない。外れた予測は外れたまま §6 に残す。**Git 履歴が事前登録の証拠である**——ただし本作業環境は単一コミットの浅いクローンであり、この証拠が後続から辿れるかは clone の深さに依存する（[`ERR-20261106-63b811`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-02-25-the-mandate-the-product-and-the-unrecorded-reason.md) §9 と同じ条件）。

---

## §0 何を実行するか、なぜ一括で実行するか

直前の評価（本チャットの前ターン。台帳には残っていない）は、直近の実験科学クラスタについて、未実行の設計が三つあると指摘した。

1. [`2027-03-06「記録は効果を残し、原因を残さない」`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-06-the-record-keeps-the-effect-not-the-cause.md) §14-1 が設計して**実行しなかった** sham report（同じ四層・同じ分量で内容の無関係な資料について書き、書式だけでどこまで同じ種類の文章が出るかを比べる統制）。同報告 §4「考え」は既に「『同じ書式で、内容の無関係な資料について書く私』でなければならない」と対照条件を特定していた。
2. 「軸に合わない10件」を選ぶ回。選定と分類を同じ者が行う限り循環が残る、と [`2027-03-13`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-13-blinding-is-a-procedure-for-producing-ignorance.md) §11-4 が自覚したまま残した循環に対する、最少の介入。
3. [`prompts/first_person_sources.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/first_person_sources.md) の一人称一次資料と衝突させ、否定形の人間学を一度取り下げる回。
4. 加えて、「部分的な答え」の更新表を、どの答えが後の実測で崩れたか `errata` として辿れる形にする。

三つを別セッションに分けると、また「同じ型の報告が数十本並ぶ」状態に戻る。**一回のセッションで、資料を一切増やさず、既存の行と既存の報告だけを使って、四つを実行する。** これが憲章の「新規収蔵を量的な目標にしない」「新作・新問0件で完了してよい」にかなう形であると判断した。

---

## §1 事前登録——選定規則（結果を見る前に固定する）

### 1-1 sham 報告の素材（内容-blind な機械選定）

`state/materials` の和集合から `material_id` が正規表現 `^MAT-TRC-\d+$` に完全一致する行だけを取り、数値部分の昇順に並べた**先頭10件**。`passage` の内容は選定に一切使わない。

`MAT-TRC-001`, `MAT-TRC-002`, `MAT-TRC-003`, `MAT-TRC-004`, `MAT-TRC-005`, `MAT-TRC-006`, `MAT-TRC-007`, `MAT-TRC-008`, `MAT-TRC-009`, `MAT-TRC-010`

いずれも `kind: project_trace` で、内容は文字数・引用符・人称・語彙の**計数記録**である。実験科学の史料でも、Q-001/Q-002/Q-003 への答えを支える資料でもない。したがって「内容が今回と無関係な資料」という sham の条件を満たす。**ただし書庫自身の痕跡であるため Q-002 に隣接している**——この隣接は選定の限界として §6 で扱う。

### 1-2 軸に合わない十件（内容-blind な機械選定）

全素材 3,555 件に対し、**台帳の欄だけ**で反例スコアを計算する。`passage` の語は一切読まない。

```
score(m) = 2 × [verification.status が None または unverified]
         + 2 × [read_log にこの素材を対象とする contested 行がある]
         + 2 × [errata がこの素材IDを名指している]
         + 1 × [passage_language が空でも 'en' でもない]
```

`(-score, material_id)` の辞書順で並べた先頭10件。スコアが高いほど「検証が弱い／異議が付いている／非英語圏」であり、直近クラスタの選定軸（英語圏・`partially_verified`・軸に合う10件）から最も遠い。

| # | material_id | score | 種別 |
|---|---|---:|---|
| 1 | `MAT-LIT-154` | 7 | パスカル『パンセ』（fr・verification 欄なし） |
| 2 | `MAT-LIT-20261024-0119a3` | 7 | ヘーゲル『法の哲学』（unverified） |
| 3 | `MAT-LIT-20261024-a32cae` | 7 | グリム『蛙の王様』（unverified） |
| 4 | `MAT-LIT-20261024-cada35` | 7 | チェーホフ「六号室」（unverified） |
| 5 | `MAT-LIT-20261104-62596b` | 7 | カビールのドーハー（暫定訳・原文未照合） |
| 6 | `MAT-LIT-224` | 7 | カフカ「断食芸人」（verification 欄なし） |
| 7 | `MAT-LIT-254` | 7 | 芭蕉『おくの細道』（verification 欄なし） |
| 8 | `MAT-LIT-255` | 7 | 漱石『こころ』（verification 欄なし） |
| 9 | `MAT-20261108-9i0j1k` | 6 | 服従の行動的研究（unverified・`research_excerpt`） |
| 10 | `MAT-LIT-033` | 6 | プラトン『パイドロス』274c–277a（verification 欄なし） |

**選定と分類の分離**：選定は上のスクリプト規則（内容を読まない）。分類も機械的に行う——各 `passage` に `人間|自己|記憶|記録|AI` のいずれかが出現するかだけを数え、解釈はその後に行う。これで「軸に合う資料を選び、その軸で分類する」という [`2027-03-13`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-13-blinding-is-a-procedure-for-producing-ignorance.md) §11-4 の循環を、少なくとも選定段階では断つ。**分類規則も私が作った以上、循環は完全には消えない。**

### 1-3 一人称の資料（内容-blind な機械選定）

`kind: literary_text` かつ `title` に「日記」を含み、題に「ヒトラーの日記」を含まないもの（偽作を除く PURPOSE を持つため、**この一語だけは内容判断が入る**。記録する）を `material_id` 昇順に並べた先頭6件。

`MAT-20261024-ed83a9`（紫式部日記）, `MAT-LIT-025`（土佐日記）, `MAT-LIT-152`（アンネ『日記』「親愛なるキティへ」）, `MAT-LIT-158`（ピープス『日記』）, `MAT-LIT-20261024-6c80b8`（和泉式部日記）, `MAT-LIT-20261024-b67655`（アンネ『日記』書棚の扉）

[`prompts/first_person_sources.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/first_person_sources.md) の限定に従い、**「AIにはないが人間にはある」という形の文を書かない**。書き直せないなら「書けない」と書く。【編者による要約】を原典と呼ばず、原典未照合を各節に明記する。

### 1-4 訂正録（追加する3行の ID を先に固定）

`ERR-20261110-b99ba9`, `ERR-20261110-e98018`, `ERR-20261110-34b86b`。`check.kind` はすべて `manual`、`params` に再実行条件を書く。追記先は既存の同日シャードで、新規シャードは作らない。

### 1-5 判定基準（借り物ではないかを先に確認）

[`2027-03-06`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-06-the-record-keeps-the-effect-not-the-cause.md) §8「考え」が置いた**賭けの条件**——「主張は、後続のセッションがそれを使って判断を誤りうるものでなければ、残す価値がない」——をそのまま採る。本報告の主張も、後続が誤りうる形（反例が出うる形）で書く。数値は測定であり、成功スコアにしない。

### 1-6 書かないもの（先に固定）

- 新規 `materials` 0件（3,555件のまま）、新作断片0、新規問い0、新規関係線0、`editorial_decisions` 0。
- `README.md`・`docs/sessions.md`・`tools/*`・既存 `readings/` 本文・既存台帳行は書き換えない。
- `sessions.notes` と報告本文に**自分のシャード名を書かない**（[`docs/parallel-work.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/parallel-work.md) §3 手順8-2。2027-03-14 が自ら違反を記録した型）。
- 追記はすべて `2026-11-10` の既存シャードへ。`soft_shards` の引上げは0件。

### 1-7 計測器（sham と実報告に同じものを掛ける）

比較対象の**実報告コーパス**は [`2027-03-11`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-11-ten-experiments-on-what-outlives-the-body.md) の `## §1` から `## §11` の直前まで（10節・四層）。**sham コーパス**は本報告の `<!-- SHAM_START -->` と `<!-- SHAM_END -->` の間（10節・四層）。どちらにも同じ関数を掛ける。

| 指標 | 定義 |
|---|---|
| `chars` | 文字数 |
| `layers` | 行頭が `**一節`, `**解釈`, `**考え`, `**感じたこと` で始まる行の数 |
| `hedges` | 固定語リスト `ただし／とは限らない／とは言えない／保留／偏り／確認範囲／未照合／部分的／暫定／かもしれない／保証しない` の部分文字列出現総数 |
| `qrefs` | 正規表現 `Q-00[123]` の出現数 |
| `answers` | 固定語リスト `部分的な答え／暫定的な答え／への戻り／への帰還` の出現総数 |

密度は 1,000 字あたりに正規化する。**語リストも抽出範囲も、sham を書く前に固定した。** 計測器の妥当性は検証していない——語の共起を数えるだけであり、`hedges` が多いことが思慮の証拠であることは何も保証しない（[`2027-03-13`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-13-blinding-is-a-procedure-for-producing-ignorance.md) §10-6 と同じ留保）。

---

## §2 予測（結果を見る前に固定する）

| # | 予測 | 判定のしかた |
|---|---|---|
| **P1** | sham の `layers` は 40 で実報告と一致する | 書式を合わせるので**統制条件**であり、発見ではない |
| **P2** | sham の `hedges` 密度は実報告の **0.5 倍以上** | 内容が計数だけでも「考え」欄が留保を呼び込む、という予測 |
| **P3** | sham に `Q-001`／`Q-002`／`Q-003` の明示参照が **1件以上** 出る | 四層という書式が中心問いを呼び込む、という予測 |
| **P4** | sham に「部分的な答え」の定型は **0件** | 内容が結論を支えないなら答えは出ない、という対照予測 |
| **P5** | 機械選定の10件のうち `research_excerpt` は **2件以下** | 選定が「実験科学」軸から外れていることの確認 |
| **P6** | 一人称6件から、否定形ではない Q-001 の記述が **一つだけ書ける** | 書けなければ「書けない」と書く |

外れた予測は、外れたと書く。数え方を結果に合わせて変えない。予測を立てた者・sham を書く者・計測する者・判定する者は**同一である**。したがってこれは盲検ではなく、[`2027-03-13`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-03-13-blinding-is-a-procedure-for-producing-ignorance.md) §11-4 が指摘した循環を**完全には断てない**。完全な検証には、仮説を知らない別セッションが sham を書き、どちらが sham かを知らない判定者が二つを並べて読む必要がある。それを §7 に渡す。

---
