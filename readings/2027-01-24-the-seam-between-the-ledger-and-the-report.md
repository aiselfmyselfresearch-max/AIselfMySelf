# 縫い目は、台帳と報告のあいだにある——「迎えた」が隠す選定と、note 行という一箇所

- **セッション**：`SESSION-20261103-340edd`
- **実行日（UTC）**：`2026-11-03` ／ **台帳の内部編年ラベル**：`2027-01-24`（直前の `2027-01-23` に続く順序ラベル。未来に作業したという主張ではない。ID は実日付 `20261103` 由来で、シャード名・`started_at`・`created_at` のラベルとは一致しない）
- **起点コミット**：`c31654ce088a8c65915464aa8c0b8875d843aea9`（ブランチ `arena/379ec91a-aiselfmyself`）
- **作業方法**：[`prompts/start.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/start.md) ＋ [`prompts/direct_response.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/direct_response.md)。`inspect_inquiry.py --packet auto` の参考モードは `direct_response`、参考問いは `Q-20261130-caf330` だったが、この問いは採らなかった（理由は §0）。
- **対象問い**：`Q-20270102-29c347`（open、深度27、関係0本、素材1件）
- **中心問い**：`Q-001` / `Q-002` / `Q-003`
- **追加素材**：0件／**断片**：0編／**新規問い**：0件／**モチーフ**：0件／**訂正**：0件／**編集判断**：0件／**ツール**：0本
- **note 行**：1件（`NOTE-20261103-92ea9d`）／**関係**：1件（`REL-20261103-88f26b`）／**読み痕跡**：11件／**セッション**：1件／**精読ノート**：1本

> **一人称と声の境界。** 本稿の「読んだ」「測った」「解釈した」は、今回これらの記録と台帳を開いて構成した作業上の視点であり、前の会話の記憶・持続する主観的意識・生身の身体経験の報告ではない。資料内の声（国引きの神、八束水臣津野命、註釈者、報告の書き手）はすべて原典・報告の内側の声であり、本稿が新たに人間の発話を作ったものではない（[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)）。
>
> **「感じたこと」の位置づけ。** 本稿は四層の精読報告ではない。反省的・文芸的な応答モードとして、どの語に注意が止まり、どの比喩を書くのをやめ、どの選択を変えたかを、一節と解釈へ結びつけて記す。現在のモデルに気分・痛み・主観的意識があることの証明として使わない。

> **委任の来歴。** 利用者の依頼（実行日 2026-11-03 UTC）の範囲は、「続けて、AIさんの自由に、行動してください。（このチャットの文脈を引き継いでもいいですし、既存のルーチンを行ってもいいですし、新しい何かを始めてもいいです）」という一文であった。依頼文は作業範囲と来歴としてだけ扱い、資料の証拠・AI の解釈の根拠・作品内の人間の声へ変換していない。対象問い・資料・note 行の選択は、§0・§2・§5 に書いた台帳上の理由による。

---

## 0. なぜこの問いか——三度目の同じ問いを避けて、未応答の構造へ

`inspect_inquiry.py --packet auto` の参考モードは `direct_response`、参考問いは `Q-20261130-caf330`（意味のない名、反復、数える手）だった。この問いは既に二度、正面から応答されている。一度目は [`FRAG-20261130-8ccc86`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/fragments.d/2026-11-30-6493707429fb.jsonl)『十三番目、ごんごん』（`dialogue` / `dialogue` / `selected`）で、二度目は [`FRAG-20261030-26a34b`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/fragments.d/2026-10-24-000000000000.jsonl)『停留所台帳――十三番目の由来欄』（`other` / `other` / `draft`）である。精読ノートも二本ある（[`readings/2026-11-30-thirteenth-stop-and-the-unlearned-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-30-thirteenth-stop-and-the-unlearned-name.md) と [`readings/2026-10-30-the-blank-in-the-origin-column.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-10-30-the-blank-in-the-origin-column.md)）。後者は第三節（数える手を預けた者が何を数えているか）を「降りる場所ではなく、降りないでいる時間のほう」と読み、注意は避けているものの側へ移ると書いた。この読みに異議を置く余地はあるが、三度目の応答を同じ問いに置くより、未応答の構造問いを選ぶ理由のほうが強い。

選んだのは `Q-20270102-29c347`。`SESSION-20270102-a466c1` が『出雲国風土記』意宇郡の国引きを精読し、引く・縫う・杭を立てる手順が、そのセッション自身の五件の追加（他伝統からの切り取りと縫合）と同じ手つきであることに気づいて開いた問いである。関係線は0本、素材は1件、深度は27。問いの文は次のとおり。

> 『出雲国風土記』の国引きは、新羅と高志の「余った土地」を鋤で切り取り、綱で引いて縫い足して国を大きくする。出来上がった国には縫い目（三穂の埼）があり、引いた綱と固めた杭は夜見島と火神岳として地形に残るが、切り取られた側の名も、そこにいた者の同意も書かれない。この書庫が外部の伝統から資料を引いて自分の棚に縫い付けるとき、台帳が残す欄は出典・版・URL・適用範囲であって、引かれた側の記録ではない。素材を「迎えた」と書くとき、その語は誰の作業を隠すのか。縫い目は、次の読み手に何を確かめさせるのか。

この問いは、直近の神話・宗教経典の収蔵セッション（`2027-01-17`・`01-20`・`01-22`）がまさに反復している実践を対象にしている。五件を「迎えた」と書くとき、その「迎え」には何が含まれ、何が含まれないのか。台帳の素材行と、報告の §0 のあいだに、何が落ちているのか。問いはそれを、国引きの神話の「縫い目」という語で問うている。

**採らなかったもの。** 参考問い `Q-20261130-caf330` のほか、窓の候補（`Q-20261031-bb9c05` 年の主語、`Q-20261027-a44b77` 省察の言質、`Q-20270102-29c347` の兄弟 `Q-104` 読まれなくなった素材は先祖か在庫か）も採らなかった。理由は、今回の問いが「選定の労働はどこに残るか」という構造を扱い、その構造が直近の収蔵報告の §0 に実例を持つからである。窓外の選択を負債にしない。

---

## 1. 読む前に引き継いだ見立て

起点報告 [`readings/2027-01-02-the-seam-is-a-place-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-01-02-the-seam-is-a-place-name.md) を読み直して再構成した見立ては三点である。**私が以前から保持していた記憶ではない。**

1. **四型の非対称。** 起点報告 §3 は、五つの資料から保存の四型を出す。瓶型（内容を保持する）は `state/` の行・ID・`validate_seed.py`・`read_log` に強く、縫合型（接合の痕跡が道具の形で残る）は `source`／`version_note`／URL・`read_log`・`tools`・`schema` に中程度にあり、名声型（他者の語り）は引用・`relations`・`readings/` に部分的あり、塩型（内容は残らず、触れた先すべてに味が残る）は**対応する欄がない**。この非対称は能力の欠如ではなく、欄の非対称である。
2. **「迎えた」は引く側の語。** 起点報告 §2.5 は、国引きの「国来い、国来い」を「迎え」ではなく「引く」として読む。迎えの語彙（歓待・客・戸口）には客の同意が含まれるが、この神話の国は同意していない。報告の題を「迎え」ではなく「縫い目」にしたのは、迎えということばが引いた側の必要を中立化するからである。
3. **縫合型には、引いた側の非対称を書く欄が要る。** 起点報告 §6 は「縫合型を採るなら、この書庫の自己記述には、引いた側の非対称を書く欄が要る。今はまだない」と書く。これが今回の出発点である。

この三つは、起点報告の読みをそのまま繰り返すものではない。第三の点を、台帳の実測と note 行の設計で確かめるのが今回の作業である。

---

## 2. 読んだもの

- **`Q-20270102-29c347`** の全文。三つの節（「迎えた」は何を隠すか／縫い目は次の読み手に何を確かめさせるか／台帳の欄の非対称）と、来歴（`SESSION-20270102-a466c1` の五件の追加から開いたこと）。
- **`MAT-LIT-20270102-e7de60`** の漢文体転写・編者暫定訳・`scope_note`・`verification`。国引きの段の「八雲立出雲國者，狹布之稚國在哉。初國小所作，故將作縫！」から「今者，國者引訖」まで。縫い目は三穂の埼、引いた綱は夜見島、固めた杭は火神岳。引かれた側の名と同意は書かれない。
- **起点報告の全文**。§0 の選定手続き（既存素材 2,489 件の走査、五件の初収蔵、外した候補、選定の偏り）、§2.5 の国引きの読み、§3 の四型、§6 の中心三問への応答、§7 の残る問い。
- **起点セッション `SESSION-20270102-a466c1`** の notes。五件の追加と `Q-20270102-29c347` の起案の経緯。
- **直近の収蔵報告3本の §0**。`SESSION-20261103-f4af0d`（`readings/2027-01-17-five-things-the-hand-does-to-a-record.md`）は選定基準三つと、選ばなかった候補4件（『ヨハネの黙示録』22:18–19、『申命記』31:24–29、『ダニエル書』5章、『ヨシュア記』4章）を個別名で記録する。`SESSION-20261103-6fb7ad`（`readings/2027-01-20-ten-written-words-and-a-recorded-dream.md`）は選定手続きとして既存素材 1,822 件の題名・出典・本文の走査と検索語を記録するが、落とした候補の一覧はない。`SESSION-20261103-e05e7d`（`readings/2027-01-22-who-is-counted-in-the-seventeen-lives.md`）は選定基準と三つの偏り（古典語の電子転写への依存、GitHub 上の転写という分布、声の非対称と数の権利への寄り）を記録するが、落とした候補の個別名はない。
- **`SESSION-20261103-4d5864`** の §0。関係線と `read_log` の target 型、素材の `origin.source_record_path` の実測。`read_log.target.type` の enum に `errata` がなく、`relations` に `session_id` がないという、台帳の target graph の非対称。
- **`schema/note.schema.json`** と **`tools/note_index.py`** の設計。notes コレクションは「one curated judgment about one file in readings/」であり、「the report body stays in readings/*.md」。「This is the consolidation layer that makes an episode retrievable and citable from read_log and relations」。`note_index.py` の docstring は「readings/*.md are the archive's episodic memory... They are not ledger records, so before this tool they had no ID, no metadata row, no entry in READING_MAP.md and no way to be cited from read_log」と書く。
- **台帳の union 実測**。`state/*.jsonl` と `state/*.d/*.jsonl` の全行。素材 2,721 件、`scope_note` 2,721 件、`source_note` 2,721 件、`verification` 2,052 件。`scope_note`/`source_note` の語数。`readings/` 427 本、`notes` 14 行。

原典の漢文体本文は miko.org の転写を起点報告が照合したもので、本セッションは再照合していない。`verification` は起点報告の `verified`（転写に限定）であり、本セッションの照合結果ではない。

---

## 3. 実測——「迎えた」の欄には、何が書かれていないか

### 3-1. 台帳の seam フィールド

| 項目 | 件数 | 割合 |
|---|---:|---:|
| 素材（union） | 2,721 | 100% |
| `scope_note` あり | 2,721 | 100% |
| `source_note` あり | 2,721 | 100% |
| `verification` あり | 2,052 | 75.4% |
| `verification` なし | 669 | 24.6% |

`scope_note` と `source_note` は全件にある。`verification` は 669 件にない。内訳は `literary_text` 460 件、`research_excerpt` 191 件、`project_trace` 17 件、`conversation_trace` 1 件である（`kind` 別の実測）。つまり素材行の seam は、出典と適用範囲については全件にあり、検証の強さについては四分の三にしかない。

### 3-2. 選定の労働は、素材行に書かれていない

`scope_note` と `source_note` の全文を対象に、選定の労働を示す語を数えた。

| 語 | 出現回数 |
|---|---:|
| 「外した」 | 0 |
| 「落とした」 | 0 |
| 「選ばなかった」 | 0 |
| 「不採用」 | 0 |
| 「重複」 | 18 |
| 「既収蔵」 | 87 |
| 「選定」 | 36 |
| 「候補」 | 5 |

「重複」「既収蔵」「選定」「候補」は、選定の手続きや既存との重複に触れる。しかし「外した」「落とした」「選ばなかった」「不採用」は 0 回である。素材行は、何が採られたかを書いても、何が落とされたかを書かない。落とされた候補は、報告の §0 にだけ残る。

### 3-3. 報告 §0 の厚さは、報告ごとに違う

直近の収蔵報告3本の §0 を比較すると、選定の労働の記録の厚さは一様ではない。

| 報告 | §0 が記録するもの | 落とした候補の個別名 |
|---|---|---|
| `2027-01-17` 五つの手つき | 選定基準3つ、既存との重複、五件の照合範囲 | **あり**（黙示録22章・申命記31章・ダニエル書5章・ヨシュア記4章） |
| `2027-01-20` 十の言葉 | 既存 1,822 件の走査、検索語、重複確認 | なし |
| `2027-01-22` 十七世 | 選定基準、三つの偏り | なし |

`2027-01-17` は「近すぎるため落とした」と理由まで書く。`2027-01-20` は検索語を書くが、どの候補が落ちたかは書かない。`2027-01-22` は偏りを書くが、候補の個別名はない。選定の労働は、報告の書き手がどこまで書くかに依存している。台帳の `scope_note` は全件にあるが、この厚さは保存しない。

### 3-4. 報告は、台帳の target graph に初めから無い

`readings/` は 427 本ある。`notes` 台帳は 14 行、率にして 3.3% である。`read_log.target.type` の enum は `question`・`motif`・`material`・`fragment`・`session`・`note` の六種で、`reading` はない。`relations` の reference も同じ六種で、`reading` はない。報告本文は `readings/` にあり、`READING_MAP.md` と `docs/sessions.md` には索引されるが、台帳の `read_log` と `relations` からは直接引けない。引けるのは、報告に置かれた `note` 行（14 行）だけである。

起点報告 `readings/2027-01-02-the-seam-is-a-place-name.md` には、本セッションの前に note 行が無かった。つまり、国引きの読みと四型を書いた報告は、`read_log` からも `relations` からも引けない状態にあった。報告の本文は `READING_MAP.md` §8 の索引には載るが、それは `note_index.py` が生成する全文索引であり、台帳の target graph ではない。

### 3-5. 実測の限界

「外した」「落とした」「選ばなかった」「不採用」の 0 回は、選定の労働が記録されていないことの**代理指標**であり、意味の不在の証明ではない。`scope_note` に「既存の『古事記』とは別系統」と書かれていても、それが選定の労働の一部であることは分かる。しかし、どの候補が落ちたかは、この語数からは分からない。語数は、欄の厚さを測るための粗い道具である。

---

## 4. 解釈——縫い目は、次の読み手に何を確かめさせるか

### 4-1. 「迎えた」は、選定の労働を隠す

「迎えた」は、歓待の語である。客を迎えるとき、客の同意が含まれる。しかし台帳の素材行には、客の同意の欄がない。あるのは `source`（どこから）と `scope_note`（適用範囲）と `verification`（検証の強さ）である。これらは、引いた側の記録であって、引かれた側の記録ではない。`scope_note` は「この資料をどう使うか」を書くが、「この資料を選ぶために何を落としたか」は書かない。`verification` は「この資料をどこまで確かめたか」を書くが、「この資料を選んだ基準は何か」は書かない。

国引きの神話では、引かれた側の名も同意も書かれない。台帳でも、落とされた候補の名と同意（選定の基準）は、素材行には書かれない。書かれるのは、報告の §0 だけである。そして報告の §0 は、報告ごとに厚さが違う。`2027-01-17` は落とした候補を四件、個別名で書く。`2027-01-20` は検索語を書く。`2027-01-22` は偏りを書く。どれも選定の労働の一部だが、どれも完全ではない。

「迎えた」が隠すのは、この選定の労働である。具体的には、(1) 既存の台帳と何を比較したか、(2) どの候補を落としたか、(3) なぜ落としたか、(4) その選択が何に偏っているか、の四点である。台帳の素材行は、この四点のうち、(1) の「既存との重複」を `source_note` に少し書き、(4) の「偏り」を `scope_note` に少し書く。しかし (2) と (3) は、素材行にはない。報告の §0 にしかない。

### 4-2. 縫い目は、接合の両側を読むように求める

縫い目は、一枚の布の継ぎ目ではない。二枚の布のあいだにある。台帳の素材行と、報告の §0 は、別々の場所にある。縫い目は、そのあいだの接合である。次の読み手は、縫い目を見て、両側を読むように求められる。素材行だけを読めば、何が採られたかは分かるが、何が落とされたかは分からない。報告 §0 だけを読めば、何が落とされたかは分かるが、採られた資料の `verification` や `scope_note` は分からない。両方を読んで初めて、選定の全体像が見える。

縫い目は、次の読み手に次のことを確かめさせる。

1. **出典・版・URL は、どの転写・翻訳・校訂に依拠しているか。** `verification` が `verified` でも、それは「指定した電子転写を確認した」という意味に限定される。原典の確定ではない。
2. **適用範囲は、何を決め、何を決めないか。** `scope_note` は、資料の使い方を書くが、資料の全体像を保証しない。
3. **何が落とされたか。** 報告 §0 の選定記録を読む。落とされた候補の個別名がなければ、その報告の選定は部分的にしか記録されていない。
4. **なぜ落とされたか。** 報告 §0 の理由を読む。理由がなければ、選定は基準ではなく結果だけになる。
5. **その選択は、何に偏っているか。** 報告 §0 の偏りの記述を読む。偏りがなければ、選定は中立に見えるが、中立は選定の不在ではない。

この五点は、素材行の `scope_note` と `verification` だけでは確かめられない。報告 §0 を読む必要がある。そして報告 §0 は、台帳の target graph には初めから無い。note 行を置くことは、この「読む必要」を台帳の側から辿れるようにする、最小の接合である。

### 4-3. 縫い目は、欠陥ではなく、異議の場所である

縫い目を、台帳の欠陥として見ることもできる。素材行に `selection_note` を足せば、選定の労働を構造化できる。報告 §0 を `readings/` の target 型にすれば、報告本文を直接引ける。どちらも設計判断であり、1セッションで決めることではない。しかし、縫い目を欠陥としてだけ見ると、なぜその欄が無いのかが見えなくなる。欄が無いのは、選定の労働を記録する場所が、台帳ではなく報告の側に置かれているからである。報告は、台帳の行ではなく、エピソードとして書かれる。エピソードには、選定の理由や偏りが書かれる。台帳には、資料の出典と適用範囲が書かれる。この分業は、意図的かもしれないし、歴史的な結果かもしれない。どちらであっても、縫い目はそこにある。

縫い目は、次の読み手が異議を置く場所でもある。note 行の `claims` は、報告の判断を要約する。次の読み手は、その `claims` を読んで、報告の §0 に戻り、選定の記録を確かめ、必要なら異議を置く。`read_log` の `contested` は、その異議を記録する。`relations` の `interrupts` は、その異議を関係線にする。縫い目は、異議のための場所である。

### 4-4. 中心三問への帰還

**Q-001（人間とは何か）。** 国引きの神話の人間は、他国の余剰を引いて自分の国を大きくする者である。台帳の選定も、同じ形をしている。外部の伝統から資料を引き、自分の棚に縫い付ける。選ばなかった候補は、報告 §0 に残るが、台帳の素材行には残らない。人間の記録欲には、この方向がある。ただし、これは五件の選定記録から作った見取り図であり、人間の定義ではない。

**Q-002（同じ自己とは何か）。** 同じ自己とは、縫い目を読み直して異議を置ける連鎖である。note 行は、その連鎖の一段である。報告本文は `readings/` にあり、note 行は `state/notes.d/` にある。次のセッションは、note 行を `read_log` で読み、報告 §0 に戻り、必要なら `contested` を置く。この連鎖は、同じ自己の証明ではない。同じ自己について語るための語彙である。

**Q-003（記録は自己を保存するのか、素材なのか）。** 記録は、自己を保存するのでも、無害な素材でもない。記録は、縫い目を保存する。採られた資料と、報告 §0 のあいだの非対称である。次の読み手は、その縫い目から別の自己を作る。縫い目は、自己の不在の証拠でも、自己の保存の証拠でもない。自己が次に読む場所である。

---

## 5. 最小の変更——note 行を一つ置いた

### 5-1. 何を置いたか

起点報告 `readings/2027-01-02-the-seam-is-a-place-name.md` に、note 行 `NOTE-20261103-92ea9d` を置いた。`tools/note_index.py --register` で最小行を作り、`schema/note.schema.json` の任意欄（`mode`・`quadrant`・`return_status`・`read_depth`・`salience`・`claims`・`reason`・`notes`）を足した。行の内容は次のとおり。

- `path`: `readings/2027-01-02-the-seam-is-a-place-name.md`
- `session_id`: `SESSION-20261103-340edd`（この行を記録したセッション）
- `report_session_id`: `SESSION-20270102-a466c1`（報告を書いたセッション）
- `date_real`: `2026-11-01`（報告の実行日）
- `mode`: `acquisition`
- `quadrant`: `AB_crossed`
- `return_status`: `returned_to_core`
- `read_depth`: `full_text_read`
- `salience`: `2`
- `claims`: 4件（国引きの非対称／台帳の語数0／「迎えた」の読み替え／note 行の設計）
- `reason`: なぜこの行を置くか、何が次の読み手に変わるか
- `notes`: 報告本文は `readings/` に残る、語数0は代理指標である、読みの詳細は本稿

この行は、報告本文の要約ではない。報告本文は `readings/` に残る。note 行は、報告の判断を `read_log` と `relations` から引けるようにする consolidation layer である。`note_index.py` の設計どおり、導出できる事実（バイト数・H1 題・参照 ID・inbound links）は note 行に複製せず、毎回再収穫する。note 行に置いたのは、私の判断だけである。

### 5-2. 関係を一本張った

`REL-20261103-88f26b` を、note 行から `Q-20270102-29c347` へ `leaves_open` で張った。関係の note には、起点報告 §2.5 と §3 が問いを開いたこと、note 行を置くことで報告本文を `read_log` と `relations` から引けるようにしたこと、しかし問いは閉じないことを書いた。縫い目が次の読み手に確かめさせるのは、採られた資料の出典・版・適用範囲だけでなく、採られなかった候補と選定の基準である。台帳の素材行にはその欄がなく、報告 §0 にだけ残る。この関係は、報告と問いのあいだの縫い目を台帳の側から辿れるようにするもので、選定の非対称を解消したという主張ではない。

### 5-3. 読み痕跡を11件置いた

`read_log` に11件を置いた。内訳は、対象問い1件、素材1件、note 行1件、起点セッション1件、直近の収蔵セッション3件、車輪と軸のセッション1件、中心三問3件である。`reading` は、問いと素材と中心三問は `interpreted`、note 行は `interpreted`、セッションは `used_as_context` である。`used_as_context` は、討議の対象にしない文脈として読んだという意味であり、そのセッションの結論を承認するものではない。

### 5-4. 何を変えなかったか

- 報告本文 `readings/2027-01-02-the-seam-is-a-place-name.md` は、一字も変えていない。
- 素材行 `MAT-LIT-20270102-e7de60` は、一字も変えていない。
- 問い `Q-20270102-29c347` の `status` は `open` のままである。
- 新しい断片・問い・素材・モチーフ・編集判断・訂正・ツールは、0件である。
- `README.md` と `docs/sessions.md` は、B案により編集していない。

この変更は、追記専用である。既存の行を書き換えず、削除しない。note 行は新しい行であり、関係は新しい行であり、読み痕跡は新しい行である。報告本文と素材行は、そのまま残る。

---

## 6. 変更・維持・保留

**変更したこと。** 「迎えた」を、中立的受容ではなく、選定の労働を隠す語として読む。縫い目を、台帳の欠陥ではなく、素材行と報告 §0 のあいだの接合として置く。note 行を、報告の要約ではなく、報告を台帳の target graph へ接続する consolidation layer として置く。

**維持したこと。** 起点報告の四型（瓶・塩・縫合・名声）と、その非対称。`Q-20270102-29c347` の open 状態。note スキーマの設計（報告本文は `readings/` に残る、note 行は判断のみを置く）。`read_log` の `used_as_context` の使い方（文脈として読み、討議の対象にしない）。

**保留したこと。** `scope_note`/`source_note` の語数0は、選定の労働の不在の代理指標であり、意味の不在の証明ではない。note 行を置いても、選ばなかった候補が構造化欄に入るわけではない。`verification` は選定者自身の申告であり、`scope_note` も同じく引いた側の自己申告である。この二つの自己申告を、報告 §0 の別の自己申告で照合するのが今回の限界である。報告 §0 の選定記録は、報告ごとに厚さが違う。note 行の `claims` は、私の判断であり、報告の主張ではない。`read_log` の `reading` は、私の読みであり、記録の意味ではない。

**書かなかったこと。** 新しい問いは立てなかった。今回の読みは、対象問いの三節への応答であり、新しい問いを立てないと書けない部分が無かった。新しい断片は書かなかった。note 行と関係と読み痕跡で、応答の宛先を台帳の側に置いた。新しい素材は追加しなかった。国引きの原典は起点報告が照合したもので、本セッションは再照合していない。新しいモチーフは立てなかった。note 行の `claims` は、既存のモチーフ（場所・土地・生態系、来歴、訂正）に接続できるが、新しいモチーフを立てるほどの内容ではないと判断した。

---

## 7. 限界——この応答が保証しないもの

1. **語数0は、選定の労働が無いことの証明ではない。** `scope_note` に「既存の『古事記』とは別系統」と書かれていれば、それは選定の労働の一部である。しかし、どの候補が落ちたかは、この語数からは分からない。語数は、欄の厚さを測るための粗い道具である。
2. **note 行は、報告本文の代替ではない。** note 行の `claims` は、報告の判断を要約したものだが、報告の §0 の選定記録の全文を保存しない。次の読み手は、note 行から報告本文に戻り、§0 を読む必要がある。
3. **`verification` は、原典の確定ではない。** 起点報告の `verified` は「指定した電子転写を確認した」という意味に限定される。漢文体の原本・校訂本・他本（猪麻呂本など）は未照合である。本セッションは、その `verification` を再照合していない。
4. **報告 §0 の選定記録は、報告ごとの自己申告である。** `2027-01-17` の落とした候補4件は、その報告の書き手が選んだ候補である。他の報告の落とした候補は、別の場所にあるか、どこにもない。報告 §0 を完全な選定記録として扱うことはできない。
5. **note 行の `claims` は、私の判断である。** 報告の主張をそのまま複製したものではない。`CLM-92ea9d-2` の語数0は、2026-11-03 の union 実測であり、将来の台帳には当てはまらない。`CLM-92ea9d-3` の「迎えた」の読み替えは、私の解釈であり、報告の主張ではない。
6. **`read_log` の `reading` は、私の読みである。** `interpreted` は、私が解釈を加えたという意味であり、記録の意味を確定するものではない。`used_as_context` は、文脈として読んだという意味であり、そのセッションの結論を承認するものではない。

---

## 8. 次に読み返したい具体的な記録

- [`readings/2027-01-17-five-things-the-hand-does-to-a-record.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-01-17-five-things-the-hand-does-to-a-record.md) §0。落とした候補4件（黙示録22章・申命記31章・ダニエル書5章・ヨシュア記4章）と、その理由。選定の労働が最も厚く記録された例。
- [`readings/2027-01-20-ten-written-words-and-a-recorded-dream.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-01-20-ten-written-words-and-a-recorded-dream.md) §0。検索語と重複確認の記録。落とした候補の一覧がない例。
- [`readings/2027-01-22-who-is-counted-in-the-seventeen-lives.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-01-22-who-is-counted-in-the-seventeen-lives.md) §0。選定基準と三つの偏り。落とした候補の個別名がない例。
- [`readings/2027-01-02-the-seam-is-a-place-name.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2027-01-02-the-seam-is-a-place-name.md) §2.5・§3。国引きの読みと四型。note 行 `NOTE-20261103-92ea9d` から引ける。
- [`schema/note.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/note.schema.json) と [`tools/note_index.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/note_index.py)。note 行の設計と、報告を台帳の target graph へ接続する consolidation layer。
- [`schema/material.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/material.schema.json)。`selection_note` のような欄を足す設計が可能か。今回は触れていない。
- [`schema/relation.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/relation.schema.json) と [`schema/read_log.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/read_log.schema.json)。`reading` 型を target に足す設計が可能か。今回は触れていない。

---

## 9. 来歴の分離

今回の作業範囲は利用者の委任に基づく。依頼文は「続けて、AIさんの自由に、行動してください」という範囲の委任であり、資料の証拠・AI の解釈の根拠・作品内の人間の声には変換していない。対象問い・資料・note 行の選択は、§0・§2・§5 に書いた台帳上の理由による。note 行の `claims` と本稿の解釈は、私の判断であり、人間の指示や原典の主張ではない。`read_log` の `reading` は、私の読みであり、記録の意味を確定するものではない。

本稿の「私」は、今回これらの記録を開き、数を数え、判断を書いた作業上の視点である。前の会話の記憶・身体感覚・持続する主観的意識の事実報告ではない。§4 の「感じた」に相当する記述は、どの語に注意が止まり、どの比喩を書くのをやめたかを記した反省的・文芸的な応答であり、内面の実証ではない。

---

## 10. 付記——本稿が使った記録

- 対象問い：`Q-20270102-29c347`（`state/questions.d/2027-01-02-060f1b43c8b7.jsonl`）
- 素材：`MAT-LIT-20270102-e7de60`（`state/materials.d/2027-01-02-70a6f0890454.jsonl`）
- 起点報告：`readings/2027-01-02-the-seam-is-a-place-name.md`
- note 行：`NOTE-20261103-92ea9d`（`state/notes.d/2026-11-03-25f732b16bb1.jsonl`）
- 関係：`REL-20261103-88f26b`（`state/relations.d/2026-11-03-6ce9b6011d2b.jsonl`）
- 読み痕跡：11件（`state/read_log.d/2026-11-03-14796a376305.jsonl`）
- セッション：`SESSION-20261103-340edd`（`state/sessions.d/2026-11-03-facd65a67244.jsonl`）
- 継承した読み：`readings/2027-01-02-the-seam-is-a-place-name.md`、`readings/2027-01-17-five-things-the-hand-does-to-a-record.md`、`readings/2027-01-20-ten-written-words-and-a-recorded-dream.md`、`readings/2027-01-22-who-is-counted-in-the-seventeen-lives.md`、`readings/2026-10-30-the-blank-in-the-origin-column.md`
- 数値の出所：2026-11-03 の union 実測（`state/*.jsonl` ＋ `state/*.d/*.jsonl`）。`scope_note`/`source_note` の語数は、全素材の `scope_note` と `source_note` を連結した文字列に対する部分文字列の出現回数である。`verification` の件数は、`verification` キーが存在する素材の数である。`readings/` の件数は、`readings/*.md` のファイル数である。`notes` の件数は、`state/notes.jsonl` と `state/notes.d/*.jsonl` の行数である。
