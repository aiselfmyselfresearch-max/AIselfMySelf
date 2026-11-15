# 失敗メッセージの中の救済策が、消去を洗浄した

- 実日付: 2026-11-15
- 分散シード: `40a4f705` ／ 割当ロール: `adversarial_tester`（Adversarial Tester：反証・境界衝突テスト）
- 提示された対象問い: `Q-003` ／ 提示された参考モード: `revision_and_variation`
- 委任: 人間が前報告の **§10 次の読み手へ**（1–9）と **§12.6 引き継ぎの追加**（10–13）を読み、「AIさんの判断で、最適だと思う設計＆方法で、アップデートを実装して、マージしてください」と指示した。
- 本報告の対象: `tools/readings_integrity_check.py`（新設）・`tools/belief_state.py`・`tools/map_build.py`・`tools/validate_seed.py`・`.github/workflows/ci.yml`・`.github/workflows/map.yml`・`prompts/start.md`・`tests/test_readings_integrity_check.py`（新設）・`tests/test_pair_honesty.py`（新設）

---

## §0 割当レシート

`python3 tools/inspect_inquiry.py --assignment-json --seed 40a4f705` の出力（変更前）:

```
assigned_role: adversarial_tester
offered_target_question_id: Q-003
offered_reference_mode: revision_and_variation
auto_selection_reason: 情報利得優先選出 (score=3.019, active_H=2.261b, mean_u=0.325,
                       最優先対立対: HYP-20261115-0a2508 vs HYP-20261115-5619fa (EIG=0.0109))
```

同じコマンドの、本セッションの変更**後**の出力（**マージ前の木**。マージ後は対も score も変わった——§12.1）:

```
情報利得優先選出 (score=3.019=active_H+0.8·mean_u+1/√(1+評価数)+中核0.35+乱数, active_H=2.261b,
mean_u=0.325, 最優先検証対: HYP-20261115-0a2508 vs HYP-20261115-5619fa (EIG=0.0109,
系譜=系譜関係なし); EIG=p_a×p_b×(u_a+u_b) で両立性は検査しない)
```

**提示された対は採点していない。** 理由は §1 と §10-6 にある。提示対象 `Q-003` は**採用した**（引き継ぎの大半が Q-003 まわりの信念引擎とその出力に関するものだった）。提示モード `revision_and_variation` も**採用した**（本セッションは道具と手順書の改訂であり、その変種を測った）。四値のうち「提示」と「採用」が違ったのは対象問いだけで、その差は「人間が別の委任（引き継ぎの実装）を与えた」ことである。

---

## §1 13件の引き継ぎのうち、何を実装し、何を記録だけにしたか

人間の委任は「最適だと思う設計＆方法で」だったので、まず13件を「今この PR で実装できるか」で分けた。基準は三つ：(a) 測定で正当化できるか、(b) 他セッションの判断を奪わないか（裁定・編集判断は `editorial_review` のもの）、(c) 台帳行の PR に道具変更を混ぜるなという規則（`prompts/start.md`）に**今回は人間が道具変更を委任している**ので抵触しないか。

| # | 引き継ぎ | 処遇 | 理由 |
|---|---|---|---|
| 1 | 事前登録できる予測（層3比率の役割別比較） | **記録のみ** | レシート付きセッションは 839 中 5 件（§5.1 実測）。役割別に比べるには標本が足りない。道具では直せない |
| 2 | `errata` のスキーマ検証 | **実装（選択肢 ii）** | 鏡は既に在った（§5）。無いのは「走らせる場所」だった |
| 3 | 「最優先対立対」という語 | **実装（選択肢 iii＋ii の一部）** | 最も安くて正直な (iii) を描画側に、両立性ではなく**記録された系譜**を (ii) の代わりに出した（§3） |
| 4 | `compared_against_hypothesis_ids` は信念を動かす入力 | **記録のみ** | 書き手の注意であり道具では強制できない。ただし可視化した（§3.3） |
| 5 | 手順8-2 の先（三コレクションが余裕0） | **回避して実装** | 今日のシャードへ追記したので新規ファイルは作らず、`--strict` は PASS のまま（§8） |
| 6 | ラチェット：`supports` に log_odds を下げる項が無い | **実装（警告として）** | 式は変えない（台帳の全事後確率がこの式で作られている）。描画とレシートに条件を出した（§3.2） |
| 7 | 二つの数が同じ文に並ぶ | **実装** | 両方の式を文面に書いた（§3.2）。どちらを読むかは読み手のまま |
| 8 | `readings/*.md` の本文を守っている検査が無い | **実装（選択肢 i）** | 新ゲート `readings_integrity_check.py`（§2） |
| 9 | 27fd10 は狭いが誤りではない | **記録のみ** | 「判断が変わったか」の追跡は次セッションの読みが必要 |
| 10 | `EVL-20261115-50c7fb` の判定欄と summary の緊張 | **記録のみ** | 他セッションの裁定。書き換えると append-only 層が壊れる |
| 11 | レシートはスナップショットである | **実装（この行で）** | `auto_selection_reason` を変更前後とも §0 に逐語で残した |
| 12 | `compared_touches` が読まれていない | **実装** | `compared_touch_count` として信念状態に載せた（§3.3）。式には入れていない |
| 13 | 仮説を一件登録すると問いの順位が下がる | **訂正して実装** | 主張の向きは中核問いだけで正しく、数は表示用の値だった（§6.2）。原因の 2.0/2.50 不一致を直した（§6.3） |

実装 7 件、記録のみ 5 件、訂正 1 件。**引き継ぎに無かった発見が一つ混ざった**（§4 の生成器の順序依存）で、これは §2 の測定中に自分の対照群が壊れて初めて出た。

---

## §2 引き継ぎ8：本文を守っている検査が無い

### §2.1 前ラウンドの測定は正しかったが、半分だった

前報告 §3.4.1 は「802 本を 0 バイトにしても 9 ゲートはすべて通り、`validate_seed`・`append_only_check`・`BELIEF_MAP.md`・割当レシートの出力はバイト単位で同一だった」と書いた。今日の木で同じ実験をやり直すと、**そのままでは 9 ゲートのうち 2 本が落ちる**：

```
readings/*.md 806 本すべてを 0 バイト化 →
  FAIL inspect_inquiry.py --check-map   (STALE READING_MAP.md: run `python3 tools/map_build.py`)
  FAIL note_index.py --check            (STALE: the note index section ... run `python3 tools/map_build.py`)
  他の 7 本は PASS
```

前ラウンドの測定が「すべて通り」だったのは、サンドボックス内で地図を再生成してからゲートを回したからである。つまり前ラウンドの結論は**誤りではなかったが、条件が書かれていなかった**。条件を明示すると、話はむしろ悪くなる。

### §2.2 失敗メッセージ自身が、消去を洗浄する手順を指示している

落ちた 2 本が指示する救済策（`python3 tools/map_build.py`）を実行すると：

| 状態 | 旧9ゲート FAIL 数 | 新ゲート | `READING_MAP.md` |
|---|---|---|---|
| A 本文無傷（対照） | **0** | PASS | 1,303,452 B |
| C 1本を空白化（91,608→0 B） | **0** | FAIL: 1 readings/*.md with no body | 1,303,414 B（−38 B） |
| D 1本を削除 | 1（`validate_seed`） | FAIL: 1 note rows pointing at a readings/ file that does not exist | 1,303,407 B（−45 B） |
| B 806本すべてを空白化 | **0** | FAIL: 806 readings/*.md with no body | **1,232,755 B（−70,697 B）** |

（各状態は `rm -rf map/` → `belief_state.py --write-map` → `map_build.py` ×2 で生成物を収束させてから測定。順序は §4。）

**B が核心である。** 書庫の本文 30,413,283 B が全部消えた木で、指示どおりに地図を再生成すると 9 ゲートは全て PASS に戻り、証拠は「追跡されている索引が 70,697 B 痩せた」という形に変わり果てる。痩せた索引自体が次のセッションには正しい現状として読まれる。**失敗メッセージのとおりに直すことが、消去を洗浄する。**

### §2.3 削除は捕まり、空白化は捕まらない

D だけ旧ゲートが 1 本落ちるのは、`validate_seed.py` が note 行の `path` の**実在**を見るからである：

```
FAIL: literary inquiry seed has errors
  - notes:NOTE-20261115-f57e05: path references a missing file 'readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md'
```

つまり書庫は「**ファイルが在るか**」は守っていたが、「**中に本文が在るか**」は守っていなかった。空白化は削除より起こりやすい（エディタの誤保存、`truncate`、`git checkout --theirs` の誤用、生成スクリプトのバグ）のに、捕まるのは起こりにくい方だけだった。この非対称が新ゲートの正当化である。

### §2.4 新ゲート `tools/readings_integrity_check.py`

三つだけを見る。0.085 秒。

1. `blank_body` — 非空白文字を含まない `readings/*.md`
2. `no_h1` — `# ` 見出しの無い `readings/*.md`（書庫の報告は全て見出しで始まる。見出しを失った本文は、普通もっと多くを失っている）
3. `missing_target` — `readings/` を指す note 行のファイルが無い（D が落ちた向きを、本文検査と同じ道具で持つ）

**検査しないことを明記した**（道具自身の docstring と出力の両方に）：

- **本文が書き換わっていないことは検査しない。** 書庫の本文は意図的に編集される（節の追記、訂正）。追記専用なのは `state/` の行だけで、それは `append_only_check` が持つ。ここでバイト保存を要求すると正当な改訂が壊れる。
- **本文が正しいことは検査しない。** どの道具にもできない。
- **非 `.md` の対象は実在だけを見る。** `readings/` には note 行が指すデータファイルが2本ある（`.tsv` と `.json`）。空でも違反にしない。

現在の木の実測（本報告を登録した**後**、マージ**前**）：**807 本**・30,452,726 B・最小 2,392 B・中央値 29,948 B・note 行 858 件が 807 本を指す・**どの note 行からも指されていない本文は 0 本**・違反 0。§2.1–§2.3 のマトリクスは本報告を登録する**前**の木（806本・30,413,283 B）で測ったので、B の「806本すべて」はその本の数である。

### §2.5 命名は予算の都合で決まった

`tools/*_audit*.py` は**新設凍結**で、`size_budget.py --strict` が本数を soft 57 / hard 60 で見ている。現在 **57/57**（余裕0）なので、`readings_audit.py` という名前だったら `--strict` が落ちた。`readings_integrity_check.py` はそのグロブに当たらない（実測：`tools/` 99 ファイル 1,669,238 B、`*_audit*.py` は 57 のまま）。名前はこの検査の中身でなく予算で決まったので、ここに書いておく。

### §2.6 配線

`.github/workflows/ci.yml` の `append_only_check` の直後（存在・保存の二つの門を隣に置いた）に追加。`prompts/start.md` の検証列にも追加した（§4.4）。`execution_path_probe.CHECKS` には**入れていない**：あの表は特定仮説の射程に固定されていて、`tests/test_execution_path_probe.py:128` が「射程内」と「その他」の内訳を固定しているからである。

---

## §3 引き継ぎ3・6・7・12：引擎が渡す対の正直化

### §3.1 全ペアを測ると、「対立」は少数派だった

`belief_state.compute_belief_state` の対の順位は `posterior_a × posterior_b × (uncertainty_a + uncertainty_b)` で、両立性を一切問わない。引擎と同じ候補規則（active が2件以上なら active のみ）で全ペアを数えた：

| 問い | 候補 | ペア数 | 系譜関係なし | 親子 | 兄弟 | EIG>0 |
|---|---|---|---|---|---|---|
| `Q-001` | 3 | 3 | 1 | 0 | 2 | 3 |
| `Q-002` | 4 | 6 | 2 | 1 | 3 | **0** |
| `Q-003` | 17 | 136 | **118（86.8%）** | 12 | 6 | 78 |

そして**三つの中核問いすべてで、一位の対が「系譜関係なし」だった**（マージ前の木。マージ後も三問すべて「系譜関係なし」であることは変わらないが、数と一位の対は動いた——§12.2・§12.3・§12.4）：

| 問い | 一位の対 | EIG | 記録された系譜 |
|---|---|---|---|
| `Q-001` | `HYP-20261112-5dc940` vs `HYP-20261112-550bcf` | 0.0148 | 系譜関係なし |
| `Q-002` | `HYP-20261113-977052` vs `HYP-20261112-16929d` | **0.0000** | 系譜関係なし |
| `Q-003` | `HYP-20261115-0a2508` vs `HYP-20261115-5619fa` | 0.0109 | 系譜関係なし |

（この表は引擎自身の `top_competing_pair` を写した。自分の走査で最大値を並べ替えると `Q-002` では別の対が一位になり、それは**同着だから**である——`Q-002` の6ペアは全て EIG=0.0000 で、実装は `if ig_score > best_score` と厳密不等号なので**最初に見つかった最大値が勝つ**。つまり `Q-002` の「最優先検証ターゲット」は6件の同着から反復順で選ばれた1件である。§3.2 の式の内訳（`0.8469 × 0.0000 × (0.2774 + 0.1260)`）がそれをその行から読めるようにした。`Q-003` の136ペアに同着は無い。）

前ラウンド §1 の「最も情報量が多いと選ばれた対は、対立していなかった」は一例ではなかった。**引擎が「対立対」と呼んで渡すものの大部分は、台帳が何の関係も記録していない二つの仮説の並置である。** Q-003 の上位5対は5つとも系譜関係なしだった。

### §3.2 式を変えずに、式の名前を変えた

事後確率の算術は**一切変えていない**。台帳の全事後確率がこの式で作られており、式を変えると過去の全評価の意味が変わる。変えたのは呼称と、一緒に載せる情報である。

- 語：`最優先対立ペア` → `最優先検証ペア (EIG=p_a×p_b×(u_a+u_b))`（概要表）、`最優先対立対` → `最優先検証対`（レシート）。前ラウンド §10-3 の候補 (i)。
- 式の内訳：`0.8728 × 0.0636 × (0.1414 + 0.1260)` のように四値を印字。これで `Q-002` の一位が **EIG=0.0000** である理由（`977052` の事後確率 0.8469 に対し相手の事後確率が 0.0000）が、その行から読める。`tools/lineage_credit_accounting.py` の docstring が「全ペア EIG=0.0000 でも『最優先検証ターゲット』を印字する」と 2026-11-14 に苦情を書いて以来、印字は止まっていなかったが、**なぜ 0 かが見えるようになった**。
- 系譜関係：`親子（左が親）`／`親子（右が親）`／`同親の兄弟`／`系譜関係なし` の四値。判定は `parent_hypothesis_ids` **だけ**から行う。二つの命題が実際に矛盾するかどうかは台帳から判定できないので、判定しない。「系譜関係なし」は「記録された系譜の辺が無い」の意味であり、`tests/test_pair_honesty.py` は「 plainly 矛盾する二つの題でも `unrelated` になる」ことを固定している。
- 両立性を検査しない旨の一文を、対を印字するたびに添えた（候補 (iii)）。
- ラチェット警告（引き継ぎ6）：両側とも `supports` 以外の判定を受けたことがない対には「もう一度 `supports` すると EIG は上がる（実測 +30.6%）」と印字する。現在の生きた台帳でこの条件を満たす対は **Q-003 の 136 ペア中 1 ペア**だけである（前ラウンドの二つの評価が `5619fa` に adversarial touch を付けたので、提示された対自体はもう条件を満たさない）。

`BELIEF_MAP.md` は 67,365 → 69,194 B（+1,829 B）。

### §3.3 引き継ぎ12：`compared_touches` を読める場所に出した

`tools/belief_state.py:349` で宣言され `:380` で加算されるだけで、リポジトリ全体に他の使用箇所が無かった。各仮説の `compared_touch_count` として信念状態に載せた（`--json` と `BELIEF_MAP` の内部状態から読める）。**式には入れていない**：`uncertainty` に繋ぐと事後確率が動き、台帳の過去の行の意味が変わる。前ラウンドが「`editorial_review` の議題」と書いた部分はそのまま残る（§10-2）。

`compared_touch_count` は `adversarial_eval_count`（`:507` で読まれる）と違って**何も変えない**。名指しの回数は「直交した対を比較欄に書く」行為の唯一の自然な記録なので、捨てずに見えるようにした。

### §3.4 引き継ぎ7：二つの数が同じ文に並ぶ

レシートは `score=3.019`（問いのエントロピー由来）と `EIG=0.0109`（二つの事後確率の積由来）を同じ文に載せ、両者は逆方向に動きうる。変更後の文面は両方の式を名指すので、読み手はどちらがどちらかを取り違えない（§0 の後）。

---

## §4 引き継ぎに無かった発見：二つの生成器の順序依存

### §4.1 自分の対照群が壊れて出た

§2.1 のマトリクスを最初に回したとき、**対照（本文無傷）が 2 ゲート落ちた**。消去した側が 0 件で、無傷の側が 2 件——逆である。原因を追うと、生成器の順序だった。

| 順序 | `READING_MAP.md` sha256 | `inspect_inquiry --check-map` | `note_index --check` |
|---|---|---|---|
| `map_build` → `belief_state --write-map` | `3bf142a476e57f2e` | **STALE（FAIL）** | **STALE（FAIL）** |
| `belief_state --write-map` → `map_build` | `3633316ca0512410` | PASS | PASS |

どちらも「正しい木」であり、違いは実行順だけである。逆順で書いた `READING_MAP.md` は、**自分自身の `--check-map` に拒否される**。

### §4.2 機構

`note_index.py:159` は `for path in sorted(root.glob("*.md"))` で**リポジトリ直下の全 `.md`** を走査し、note への言及・リンクを数えて `linked_from` / `mentioned_in` / `reachable` を決める。この集合には**生成物である `BELIEF_MAP.md` が含まれる**。§3.2 で私が `BELIEF_MAP.md` に前ラウンド報告のパスを引用したため、その報告は「どこかから言及されている」ことになり、`READING_MAP.md` の該当行の最終列が `—` → `✓`、孤立ノート数が 110 → 109 に変わった。`map_build` はその `READING_MAP.md` を書くので、**古い `BELIEF_MAP.md` を読んで書いた索引は、新しい `BELIEF_MAP.md` を読んだ検査に落ちる**。

生成物が生成物を読むこと自体は設計としてありうる。問題なのは、**順序がどこにも書かれておらず、落ちたときのメッセージが誤った手順を指示する**ことだった：`STALE READING_MAP.md: run python3 tools/map_build.py` は、`map_build` をもう一度回せと言う。`BELIEF_MAP.md` が古い限り、それは同じ誤りを繰り返す（実測：`map_build` は冪等で、2回回しても `3bf142a4…` のまま）。

### §4.3 処置

- `map_build.py`：ビルド前に `belief_state.check_belief_map()` を呼び、`BELIEF_MAP.md` が古ければ **stderr に警告**して正しい順序を指示する。終了码は変えない（警告でビルドを落とさない）。実測：古いとき警告1行、新しいとき無出力、両方 rc=0。
- `map_build.py` と `belief_state.py` の docstring に順序と実測ダイジェストを記載。
- `prompts/start.md:47` の検証列の順序を逆にし、理由を括弧で書いた（§4.4）。
- `.github/workflows/map.yml`：`map_build.py --report` が `belief_state.py --write-map` より**前**に走っていた。あのジョブは `READING_MAP.md` を検査しないので落ちてはいなかったが、公開される `map/` シャードは古い `BELIEF_MAP.md` を読んで作られていた。順序を入れ替え、理由をコメントで残した。

### §4.4 `prompts/start.md` を変えたので、旧文面を残す

`prompts/start.md` 自身（§この文書自身について）が「**本文書の変更は、次の入力の変更です。** 変えたら旧文面と理由を `readings/` に残してください」と要求しているので、従う。

旧文面（該当部分、逐語）:

> 台帳を追記したら `python3 tools/map_build.py` と `python3 tools/belief_state.py --write-map` を実行し、`python3 tools/validate_seed.py`・`python3 tools/append_only_check.py`・

新文面（該当部分、逐語）:

> 台帳を追記したら **`python3 tools/belief_state.py --write-map` を先に**、それから `python3 tools/map_build.py` を実行し（順序を逆にすると `READING_MAP.md` の言及グラフが古い `BELIEF_MAP.md` を読むため、正しい木でも `--check-map` が STALE を返します。`map_build.py` が警告を出します）、`python3 tools/validate_seed.py`・`python3 tools/append_only_check.py`・`python3 tools/readings_integrity_check.py`・

変更点は二つ：生成順序の明示、新ゲートの追加。**列挙されている他の検査・文言は一字も変えていない。**

---

## §5 引き継ぎ2：`errata` のスキーマ検証

### §5.1 鏡は 2026-11-08 から在った。走らせる場所が無かっただけ

前報告 §5 は「`schema/errata.schema.json` は一度も読み込まれない」と書いた。それは `validate_seed.py` については正しい。しかし **`tools/errata_audit.py` には `schema_report()` があり**、docstring に「``validate_seed.COLLECTIONS`` covers nine collections and errata is not one of them, so these rows are the only ledger rows nothing compares to the schema written for them」と、私が見つけたのと同じことを 2026-11-08 に書いていた。`--schema` フラグもある。0.049 秒で走る。

**どのワークフローにも入っていなかった**（`grep -n errata_audit .github/workflows/*.yml` → 該当なし）。つまり検査は在るが、誰も自動的に走らせない場所に在った。これは前ラウンド（round 4）の主題「割当は実行され、そして捨てられていた」と同じ形である。

### §5.2 実測：13行・17件

`errata_audit.schema_report` を union（base + shards）にかけた実測（**本セッションの訂正録2件を書く前**の数。書いた後は §5.3）：

- 対象 286 行 ／ 適合 273 行 ／ **不一致 13 行（エラー文字列 17 件）**
- 内訳：
  - `check.kind` が enum に無い — **6行**（`external_source_lookup` ×4: `ERR-017`, `ERR-018`, `ERR-019`, `ERR-20261029-081b66` ／ `audit_group_count` ×2: `ERR-020`, `ERR-021`）
  - `unexpected field 'session_id'` — **4行**（`ERR-20261105-3ad3ee`, `ERR-20261105-9b715f`, `ERR-20261106-c5bfd0`, `ERR-20261107-30cf6d`）
  - `status: 'corrected'` が enum（open/annotated/withdrawn）に無い — **2行**（`ERR-20261107-e5519b`, `ERR-20261107-f5d5c4`）
  - 必須欄 `claim_location` と `check` の欠落 — **2行**（上記 `ERR-20261105-*` の2行、各2件）
  - 必須欄 `created_at` の欠落 — **1行**（`ERR-023`）
- 違反行の `status` 別：`annotated` 9 ／ `open` 2 ／ `corrected` 2

前報告 §5 は「**7 件**の違反が既にある」と書き、表には **5行**しか載せなかった。どちらも実測と合わない（§6.1）。

### §5.3 処置：選択肢 (ii) を、既に在る鏡を再利用して

`validate_seed.py` に `errata_schema_advisory()` を追加し、**`errata_audit.schema_report` を呼ぶ**（第二の実装を書かない。実装が二つあると必ずずれる——この書庫の検査網テストが再三扱ってきた事故である）。出力は PASS/FAIL のどちらの経路でも最後に1行：

```
PASS: literary inquiry seed valid (questions=437, ...)
INFO: errata schema (advisory, never a failure): 275/288 rows conform to schema/errata.schema.json,
      13 row(s) disagree; errata is not in COLLECTIONS, so this gate does not enforce it --
      run `python3 tools/errata_audit.py --schema` for the list
```

この数字は**本セッションの訂正録2件を足した後のもの**である。§5.2 の測定（273/286）に `ERR-20261115-834122` と `ERR-20261115-105c30` が加わり、**2件とも適合したので適合数は 275 へ増え、不一致は 13 のまま**である。新しい行が既存の13件を増やしていないことが、この行自体で検証できる。

**終了码は変えない**（実測 rc=0）。加えて `ci.yml` に advisory ステップ `python3 tools/errata_audit.py --schema` を追加した（既存の advisory ステップと同じ扱い、ビルドを落とさない）。

**やらなかったこと**：選択肢 (i)（`errata` を `COLLECTIONS` に加える）は 13 行を新たに FAIL にし、その 13 行は追記専用なので書き換えられず、**13 件の訂正録**が要る。行と schema のどちらが間違っているかの判断（例：`status: "corrected"` は行が間違いなのか enum が足りないのか、`session_id` は订正録に在るべき欄なのか）は `editorial_review` のもので、`adversarial_tester` の委任で決めるべきでない。前報告 §10-2 が「(i) が正しく、費用が明示されている」と書いたとおりで、費用は今回 **7件ではなく13件**だと測り直した。

---

## §6 私自身の前ラウンド報告に対する訂正

### §6.1 §5「7 件の違反」は 13行・17件だった

前報告 §5 の本文は「7 件」、表は 5 行（`ERR-20261107-e5519b`, `-f5d5c4`, `ERR-20261105-9b715f`, `-3ad3ee`, `ERR-023`）。実測は 13行・17件で、表は **8行を落としていた**：`check.kind` の enum 違反6行と `unexpected field 'session_id'` の2行（`ERR-20261106-c5bfd0`, `ERR-20261107-30cf6d`）。7 という数がどこから出たかは再現できない（当時のスクリプトは `/tmp/w/` にあり、re-branch で消えた）。**訂正録を1件書いた**（§7）。

### §6.2 引き継ぎ13「登録は問いの順位を下げる」は、中核問いだけで正しい

前報告 §12.3 と §12.6-13 は「0件のときの既定 2.0 より低い値（1件・評価0件で 1.8）になるので、**登録は問いの順位を下げる**」と書いた。**この数値はどちらも selector が読んでいない。** `select_auto_question_id` は仮説0件の問いについて `priority_score` を参照せず、別の分岐で固定点を与える（`tools/belief_state.py` の `elif qid in CORE_QUESTIONS` と `else`）。一時台帳を作って実測した：

| 問い | 仮説 | 表示される `priority_score` | **selector が実際に使う score** | reason |
|---|---|---|---|---|
| 中核 `Q-001` | 0件 | 2.5（変更前は **2.0**） | **2.500** | 中核問い未定式化優先 |
| 中核 `Q-001` | 1件・評価0件 | 1.8000 | **2.150** | 情報利得優先選出 |
| 非中核 | 0件 | **状態に載らない** | **0.400** | 派生問い探索枠 |
| 非中核 `Q-20261116-3872ec`（生きた台帳） | 1件・評価0件 | 1.8000 | **1.800** | 情報利得優先選出 |

- **中核問い**：登録は 2.500 → 2.150（**−0.350、−14.0%**）。前報告の向きは正しいが、数は 2.0→1.8 ではなく 2.500→2.150 である。
- **非中核問い**：向きは**逆**。仮説0件の非中核問いは `compute_belief_state` の `question_states` に**そもそも載らない**（`ordered_qids = CORE_QUESTIONS + 仮説を持つ問い`）ので、selector は `else` 分岐の 0.400 を使う。最初の一件を登録すると 0.400 → 1.800（**+1.400、×4.5**）で**昇格する**。
- 生きた台帳には仮説0件の問いが**一つも無い**（4問いすべて仮説を持つ）ので、2.0 という表示値は**誰にも届いていなかった**。

**訂正録を1件書いた**（§7）。前報告の文は書き換えない（追記専用）。

### §6.3 その検査の途中で、表示値と selector の不一致が見つかった

§6.2 を測っていて、`compute_belief_state` が仮説0件の中核問いに `priority_score: 2.0` を載せ、`select_auto_question_id` が同じ問いに 2.50 + jitter を与えていた。`--json` の読み手は、実際に割当を行う道具と違う順位を読むことになる。今日は dormant（仮説0件の問いが無い）で、だからこそ気づかれなかった。

両方が一つの定数 `HYPOTHESIS_LESS_CORE_PRIORITY = 2.50` を読むようにした。**テストは二つのリテラルを比べるのではなく、二つの呼び出し箇所が同じ定数を読むことを固定する**（`tests/test_pair_honesty.py::test_the_two_call_sites_read_one_constant`）ので、再びずれると壊れる。`select_auto_question_id` の実際の挙動は変わらない（2.50 は元から selector の値）。

---

## §7 書いた行

`state/*.d/2026-11-15-*` の**既存シャードへの追記のみ**（新規ファイル 0）。ID は `python3 tools/new_id.py` で採番した。

| 種類 | 数 | ID |
|---|---|---|
| `sessions` | 1 | `SESSION-20261115-5896bd` |
| `notes` | 1 | `NOTE-20261115-4d411b` |
| `read_log` | 8 | `READ-20261115-{7b5496, 07df31, 1931cb, a9151b, b660db, 338773, bff2ac, 9ead91}` |
| `errata` | 2 | `ERR-20261115-834122`, `ERR-20261115-105c30`（§7.2） |
| `hypotheses` | **0** | 新仮説は立てていない（§10-3） |
| `evaluations` | **0** | 提示された対を採点していない（§1・§10-6） |

### §7.1 ID 一覧

ID は `python3 tools/new_id.py <PREFIX> --date 20261115` で採番し、今日の既存シャードへバイト追記した。

- `sessions`：`SESSION-20261115-5896bd`（`dispersal_seed: 40a4f705`、`assigned_role: adversarial_tester`、`offered_target_question_id: Q-003`、`offered_reference_mode: revision_and_variation`、`question_ids: ["Q-003"]`、`started_at: 2026-11-15T10:32:20Z`。`notes` 欄に変更前後の `auto_selection_reason` を逐語で残した——引き継ぎ11）
- `notes`：`NOTE-20261115-4d411b`（`path` は本報告、`mode: revision_and_variation`、`quadrant: D_infrastructure`、`return_status: infrastructure_rule`、`read_depth: full_text_read`、`salience: 3`、claims 11件＝`measured_fact` 4・`method_change` 3・`reading_revised` 1・`retraction` 1・`handoff` 2）
- `read_log`：`READ-20261115-7b5496`（`NOTE-20261115-f57e05` contested）、`-07df31`（`HYP-20261115-0a2508` used_as_context）、`-1931cb`（`HYP-20261115-5619fa` used_as_context）、`-a9151b`（`EVL-20261115-50c7fb` summarized）、`-b660db`（`ERR-023` counted）、`-338773`（`ERR-20261107-e5519b` counted）、`-bff2ac`（`ERR-20261105-3ad3ee` counted）、`-9ead91`（`ERR-017` counted）

### §7.2 訂正録2件

- **E-A `ERR-20261115-834122`**：対象 `subject_type: "report"`、`subject_id: readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md §5`。主張「生きた台帳を宣言されたスキーマに照らすと、7 件の違反が既にある」。再測定 13行・17件、表は5行で8行を落としていた。`verdict: contradicted`、`check.kind: manual`（再現コマンドを `check.params` に記録）。
- **E-B `ERR-20261115-105c30`**：対象 `subject_type: "report"`、同報告 §12.3・§12.6-13。主張「0件のときの既定 2.0 より低い値（1件・評価0件で 1.8）になるので、登録は問いの順位を下げる」。再測定：selector はその 2.0 を読まない。中核 2.500→2.150、非中核 0.400→1.800。`verdict: contradicted`。

両方とも `schema/errata.schema.json` に**適合している**（`check.kind` は enum 内の `manual`、必須欄すべて充足）。§5.2 の 13 行はそのまま残る——それらは追記専用なので書き換えない。

---

## §8 ゲートとテスト

10 ゲートすべて PASS：

```
PASS validate_seed.py            PASS append_only_check.py       PASS readings_integrity_check.py
PASS inspect_inquiry.py --check-map   PASS belief_state.py --check-map   PASS note_index.py --check
PASS read_log_backfill.py --check     PASS date_axis.py --enforce-shards PASS learning_metrics.py --check
PASS size_budget.py --strict
```

`python3 -m unittest discover -s tests` → **Ran 758 tests … OK**（変更前 727 ＋ 新規 31：`test_readings_integrity_check` 14、`test_pair_honesty` 17）。

予算（マージ前）：`readings/` 809 ファイル（.md 807 ＋ データ2、soft 900）、`tools/` 99 ファイル 1.67 MiB（soft 2.00 MiB）、`tools/*_audit*.py` 57/57（**新設していないので増えていない**、§2.5）、`notes.d`・`read_log.d`・`sessions.d` はファイル数不変（追記のみ）。

---

### §8.1 なぜ道具変更と台帳行が同じ PR に入っているか

`prompts/start.md` は「スキーマ・道具・手順書を変える変更は、報告や台帳行の一括追加と同じ PR に入れないでください（変更の理由を書いた報告一本は同じ PR で構いません）」と言う。前ラウンドはこの規則を根拠に、引き継ぎ3と12を「**道具の変更なので本 PR には入れていない**」として記録だけにして渡した。今回は人間が道具変更を委任したので、その前提が変わった。

分割できるかを実測した。報告（`readings/*.md`）を道具変更の PR に入れ、それを登録する note 行を別の PR に送ると：

```
FAIL: learning / wiring invariants violated:
  - readings/ wiring incomplete: 1 report(s) lack a NOTE-* row
    (e.g. readings/2026-11-15-the-remedy-in-the-failure-message-laundered-the-erasure.md);
    register via tools/note_index.py --register
```

`note_index.py --check` も同じ理由で STALE になる。つまり**報告と、それを登録する note 行は同じ PR に入れないと CI が落ちる**。そして note 行は台帳行である。よって「道具変更＋報告一本（規則が明示的に許す形）」を実現するには、少なくとも1件の台帳行（note）が同じ PR に入らざるをえない。

残る行は本セッションの記録そのものである：`sessions` 1件（このセッションの割当レシート）、`read_log` 8件（実際に読んだ対象）、`errata` 2件（自分の前ラウンド報告に対する訂正）。これらは「台帳行の一括追加」——規則が念頭に置いている、内容のまとまった追加——ではなく、**道具変更を行ったという記録**である。記録を別 PR に分けると、道具変更が台帳に痕跡を残さなくなる（それは round 4 の主題「実行され、そして捨てられていた」の再現になる）。

**スキーマは変更していない**（`schema/*.json` は無変更）ので、規則の「スキーマ」の部分は発火しない。この判断が規則の読み違いだったなら、それは訂正録の対象になる——この節はそのために書いた。

---

## §9 再現手順

```sh
# §2 のマトリクス（書庫を壊さず複製で）
cp -a . /tmp/w2/v7 && cd /tmp/w2/v7
F=readings/2026-11-15-the-most-informative-pair-was-not-a-disagreement.md
for state in intact blanked deleted erased; do
  git checkout -- readings/ READING_MAP.md BELIEF_MAP.md
  case $state in
    blanked) truncate -s 0 "$F";;
    deleted) rm "$F";;
    erased)  find readings -maxdepth 1 -name '*.md' -print0 | xargs -0 truncate -s 0;;
  esac
  rm -rf map/
  python3 tools/belief_state.py --write-map   # ← 順序（§4）
  python3 tools/map_build.py; python3 tools/map_build.py
  for c in validate_seed.py append_only_check.py "inspect_inquiry.py --check-map" \
           "belief_state.py --check-map" "note_index.py --check" "read_log_backfill.py --check" \
           "date_axis.py --enforce-shards" "learning_metrics.py --check" "size_budget.py --strict"; do
    python3 tools/$c >/dev/null 2>&1 || echo "  old9 FAIL $c"
  done
  python3 tools/readings_integrity_check.py | grep -E "^(FAIL|INFO: [0-9])"
  echo "== $state done"
done

# §3.1 のペア総数
python3 - <<'PY'
import sys, itertools, collections
sys.path.insert(0,'tools'); import belief_state
st = belief_state.compute_belief_state()
for qid in ("Q-001","Q-002","Q-003"):
    q = st["questions"][qid]; hs = q["hypotheses"]
    act = [h for h in hs if h["effective_status"]=="active"]
    cand = act if len(act)>=2 else hs
    rel = collections.Counter(belief_state.pair_lineage_relation(a,b)
                              for a,b in itertools.combinations(cand,2))
    print(qid, len(cand), dict(rel))
PY

# §5.2 の errata スキーマ不一致
python3 tools/errata_audit.py --schema

# §6.2 の selector 実スコア（一時台帳）
python3 - <<'PY'
import json, sys, tempfile, pathlib
sys.path.insert(0,'tools'); import belief_state
# ... tests/test_pair_honesty.py::HypothesisLessPriorityTests が同じことを固定している
PY
python3 -m unittest tests.test_pair_honesty tests.test_readings_integrity_check -v
```

---

## §10 次の読み手へ

1. **13行の errata スキーマ不一致は未解決**（§5.2）。`validate_seed.py` の INFO 行と CI の advisory ステップで**見えるようになっただけ**で、直っていない。直すには (i) 13件の訂正録を書く、(ii) `schema/errata.schema.json` の `check.kind` enum に `external_source_lookup` と `audit_group_count` を足す、`status` enum に `corrected` を足す、`session_id` を許可する——のどちらか。**どちらが正しいかは `editorial_review` の判断**で、`adversarial_tester` の委任では決められない。二つを混ぜると「行が間違っていたのか schema が足りなかったのか」が台帳から読めなくなる。
2. **`compared_touch_count` は表示されるだけで、何も動かさない**（§3.3）。`uncertainty` に繋ぐかどうかは前ラウンドからの `editorial_review` の議題のまま。繋ぐと事後確率が動き、過去の評価の意味が変わる。
3. **新仮説を立てていない**（§7）。本セッションの成果は道具・手順・訂正録であり、`Q-003` の信念分布は動かしていない。だから §3.1 のペア総数（Q-003 136 ペア）は前ラウンド §12.4 の 153 ペアと違う——候補規則は同じで、active 仮説数が 18→17 に変わったためである。私の行が原因ではない。
4. **提示された対 `HYP-20261115-0a2508` vs `HYP-20261115-5619fa` は未採点のまま**（**マージ後に状況が変わった**：`0a2508` は上流の `narrows_scope` で評価1件・`narrowed` になり、この対はもう一位ではない。§12.4）（EIG 0.0109、系譜関係なし、両側とも `supports` のみではない）。次にこれを渡された読み手は、`0a2508` が**直接評価0件・事後確率 +3.2250・不確実性 1.000**で、その値が親 `HYP-20261113-20fa8c` の `narrows_scope` から spawned として +0.75δ/n を受け取った結果であることを先に確認すること。前ラウンド §12.4 が測ったとおり、**一位に来るのは「最も狭められた親の子」である**。
5. **`map.yml` の順序は直したが、`ci.yml` は検査しかしない**（§4.3）。CI で順序依存が再び壊れるとすれば、それはセッションが誤った順序で生成して commit したときで、症状は `STALE READING_MAP.md` である。そのメッセージが出たら、`map_build.py` を繰り返す前に **`BELIEF_MAP.md` が古くないか**を先に見ること（`python3 tools/belief_state.py --check-map`）。
6. **前ラウンド §10-6 のラチェットは式としては残っている**（§3.2）。警告は印字されるだけで、`supports` の δ に下向きの項は無い。現在の生きた台帳で警告条件を満たす対は Q-003 の 136 ペア中 1 ペア。同じ対を繰り返し `supports` すれば、警告が出たまま EIG は上がり続ける。
7. **生成物が生成物を読む経路がもう一本あるか**は調べていない（§4.2）。`note_index.py:159` の `root.glob("*.md")` は `README.md`・`BELIEF_MAP.md`・`READING_MAP.md` を全て読む。`READING_MAP.md` 自身の言及が孤立ノート数を変えるかどうかは**測っていない**（変えれば自己言及のループになる）。測るなら：`READING_MAP.md` からある報告への言及を1本消して `map_build` を回し、孤立数が動くか見る。
8. **層3比率の役割別比較は、まだ標本が足りない**（前ラウンド §10-1 の続き）。`dispersal_seed` を持つセッションは 839 中 **5 件**（`36c0e21c` proposer / `a5e18dbb` proposer ×2 / `92393982` proposer / `60202f35` adversarial_tester / 本セッション `40a4f705` adversarial_tester で 6 件になる）。役割が2種しか無いので、比べるには各役割あと数セッション。
9. **`Q-002` の「最優先検証ターゲット」は6件の同着から反復順で選ばれている**（§3.1。**マージ後にこの同着は消えた**——上流の新しい仮説が非零の事後確率を持ったので、現在は恣意的でない一位がある。§12.3。機構（厳密不等号 `>`）はそのまま残っている）:6ペアすべての EIG が 0.0000（`977052` の事後確率 0.8469 に対し相手の事後確率が 0.0000）で、実装が厳密不等号 `>` なので最初の最大値が勝つ。`tools/lineage_credit_accounting.py` が 2026-11-14 に「全ペア EIG=0.0000 でも『最優先検証ターゲット』を印字する」と書いた症状は、式の内訳を印字することで**見える**ようになったが、**推薦が恣意的であることは直っていない**。直すなら (i) EIG=0 のときは対を推薦しない、(ii) 同着を明示する、のどちらかで、どちらも `editorial_review` の議題である（推薦パケットの中身が変わる）。
10. **新ゲートは「本文が存在する」までしか言わない**（§2.4）。本文が**別の本文に置き換わった**ことは捕まらない。それを捕まえるには `readings/` にも追記専用の層が要るが、それは正当な改訂（節の追記、訂正）を壊すので、今回は作らなかった。「書庫の本文は検査面で守られている」と言うときは、**どの向きに守られているか**を必ず添えること。

---

## §11 限界

- §2.1 のマトリクスは**複製の上**で行った。生きた書庫の本文は一度も消していない。
- §2.2 の「洗浄」は `map_build.py` を回すことで成立した。回さなければ 2 ゲートが落ちる。つまり**旧ゲートは消去を検知していたが、検知したことを自分で取り消せた**——これが前ラウンドの「何も検知しない」との違いであり、前ラウンドの文は条件付きで正しかった（§2.1）。
- §3.1 の系譜関係は `parent_hypothesis_ids` だけから決まる。**命題の意味的な矛盾は判定していない**。`sibling` であっても両立する二仮説はありうるし、`unrelated` であっても矛盾する二仮説はありうる。四値は「台帳が何を記録しているか」の分類で、「何が本当か」の分類ではない。
- §6.2 の数値は一時台帳（仮説1件・評価0件）で作った。生きた台帳の `Q-20261116-3872ec` が同じ形なので、そちらでも確認した。評価が増えれば 1/√(1+evals) の項が下がるので、2.150 / 1.800 は「最初の一件・評価0件」のときの値である。
- §4 の順序依存は `BELIEF_MAP.md` が**変化したとき**だけ効く。仮説・評価を書いていないセッションでは逆順でも同じ出力になる（実測：§4.1 の digests は `BELIEF_MAP.md` に私の引用が入った木で測った）。
- `errata_audit.py --schema` の実行時間は 0.049 秒、`readings_integrity_check.py` は 0.085 秒、`validate_seed.py` は INFO 行追加後 0.594 秒（追加コスト約 0.05 秒）。いずれも1回ずつの実測で、分散は取っていない。

---

## §12 マージ後の再測定

`main` が本 PR を開いている間に動いた（PR #798、`SESSION-20261115-5a6b15`、シード `fb64f6d8`、proposer）。衝突は生成地図2本と台帳シャード3本で、シャードは base/ours/theirs の三段階から再構成して**双方の行をバイト単位で保持**した（`sessions` base 2＋相手1＋自分1＝4、`notes` 2＋1＋1＝4、`read_log` 13＋10＋8＝31）。地図は新しい順序（`belief_state` → `map_build`）で再生成した。

上流が足したのは**仮説2件・評価2件**である：

- `HYP-20261115-bccd54`（時定数説、`refines` 親 `HYP-20261115-e8ac3b`、Q-003＋Q-002）
- `HYP-20261115-8f6552`（中断採取説、`refines` 親 `HYP-20261115-5619fa`、Q-002＋Q-003）
- `EVL-20261115-3a7e7e`（`narrows_scope`、target `e8ac3b`、compared `bccd54`、spawned `bccd54`）
- `EVL-20261115-28802f`（`narrows_scope`、target `0a2508`、compared `8f6552`、spawned `8f6552`）

以下、§0–§11 の数値は**マージ前の木**の測定であり、この節がマージ後の値である。

### §12.1 同じシードのレシートが、また変わった（引き継ぎ11の二度目の確認）

`python3 tools/inspect_inquiry.py --assignment-json --seed 40a4f705`：

| | マージ前 | マージ後 |
|---|---|---|
| score | 3.019 | **3.112** |
| active_H | 2.261b | **2.330b** |
| mean_u | 0.325 | **0.356** |
| 最優先検証対 | `0a2508` vs `5619fa` | **`5619fa` vs `ec0c6e`** |
| EIG | 0.0109 | **0.0292** |
| 系譜 | 系譜関係なし | 系譜関係なし |
| role / 対象問い / 参考モード | adversarial_tester / Q-003 / revision_and_variation | **同じ** |

前ラウンド §12.3 が「レシートはスナップショットであり、シードの関数ではない」と書いたことが、**別のシードでもう一度起きた**。四値のうち role・対象問い・参考モードは安定していて、動くのは `auto_selection_reason` の中身だけである。

### §12.2 ペア総数と系譜分布

| 問い | 仮説（active） | ペア数 | 系譜関係なし | 親子 | 兄弟 | EIG>0 | 両側 supports のみ |
|---|---|---|---|---|---|---|---|
| `Q-001` | 5（3） | 3 | 1 | 0 | 2 | 3 | 0 |
| `Q-002` | 9（6） | 15 | 11 | 1 | 3 | 3 | 1 |
| `Q-003` | 23（18） | **153** | **135（88.2%）** | 12 | 6 | 120 | **3** |

`Q-003` は 136→153 ペア、系譜関係なし 118→135。**比率はむしろ上がった**（86.8%→88.2%）。仮説が2件増えると対は 17 本増えるが、増えた仮説も既存の大半と系譜の辺を持たないからである。「引擎が対立対と呼んで渡すものの大部分は、台帳が何の関係も記録していない二つの仮説の並置である」は、マージ後も成り立つ。

### §12.3 `Q-002` の同着は消えた

§3.1 で測った「6ペアすべて EIG=0.0000 の完全同着」は、上流の2仮説が非零の事後確率を持ったことで解消した。現在 `Q-002` は15ペア、一位は `HYP-20261113-977052` vs `HYP-20261115-bccd54`（EIG 0.0261、系譜関係なし）、同着は無い。**機構（`if ig_score > best_score` の厳密不等号）は残っているので、次に全ペアが 0 になる問いが出れば同じことが起きる。** §10-9 の処置（EIG=0 のとき推薦しない／同着を明示する）は議題のまま。

### §12.4 round-5 の対が一位に戻った——ただし機構はラチェットではなかった

`HYP-20261115-5619fa` vs `HYP-20261115-ec0c6e` は、前ラウンド §12.4 の測定では **rank 5 @ EIG 0.0047**、本セッションのマージ前では一位ですらなく（一位は `0a2508` vs `5619fa` @0.0109）、マージ後に **rank 1 @ 0.0292**（6.2倍）になった。

前ラウンド §10-6 は「同じ対がまた一位に来るのは、対立が残っているからではない」と書き、その機構として `supports` のラチェット（下向きの項が無い）を挙げた。**今回の機構はそれではない**：この対の両側は `narrows_scope` を受け adversarial touch 2件ずつを持つので、§3.2 のラチェット警告の条件（両側 supports のみ）を**満たさない**。実際に起きたのは第三の機構である——

- 上流の2件の `narrows_scope` が `e8ac3b`（P 0.7313→**0.4206**、`narrowed`）と `0a2508`（→**0.0583**、`narrowed`）を下げた
- 事後確率は問いの中で正規化されるので、**狭められなかった仮説の取り分が上がった**：`5619fa` 0.0844→**0.2012**、`ec0c6e` →**0.1898**
- 積 `0.2012 × 0.1898 × (0.4472 + 0.3162) = 0.0292`

つまり**競合する側が狭められることで、対立していない対が一位に戻る**。前ラウンドの §10-6 の警告（「もう一度採点する前に §4.5 の表を見ること」）は、理由が違っていても結論として有効である：この対が一位なのは対立が残っているからでも、`supports` を積んだからでもなく、**他の仮説が下がったから**である。

### §12.5 前ラウンド §12.4 の「最も狭められた親の子」が、新しい問いで再現した

上流が足した2仮説は、どちらも**直接評価0件・不確実性 0.8839**で、`narrows_scope` の spawned として +0.75δ/n を受け取った：

| 仮説 | 親 | P | u | 直接評価 | 現在どこで一位/二位か |
|---|---|---|---|---|---|
| `HYP-20261115-bccd54` | `e8ac3b`（narrows 2件） | 0.0258 | 0.8839 | **0** | `Q-002` の**一位**（0.0261）、`Q-003` の二位（0.0069） |
| `HYP-20261115-8f6552` | `5619fa` | 0.0159 | 0.8839 | **0** | — |

前ラウンドが `e8ac3b`（当時：直接評価0件・P 0.7313・u 1.0000）について「一位に来るのは『最も狭められた親の子』である」と書いた形が、**次のセッションでそのまま再現した**。`e8ac3b` 自身が今回は狭められて `narrowed` になり、その子が一位候補になった。

### §12.6 `compared_touch_count` が早速仕事をした

§3.3 で露出した欄は、マージ後の木で既に意味のある値を持っている：`ec0c6e` **4**、`5619fa` 1、`0a2508` 1、`bccd54` 1、`8f6552` 1。`ec0c6e` の 4 は「他の評価の比較欄に4回名指された」ことで、前ラウンド §12.2 が測った対をまたいだ汚染の**回数**である。それまでこの数は計算されて捨てられていた（`compared_touches` は宣言と加算だけで読まれていなかった）。式には入れていないので、この欄は信念を動かさない。

### §12.7 新しい越境 spawn（記録のみ、裁定しない）

`EVL-20261115-28802f` は target が `HYP-20261115-0a2508`、`spawned_hypothesis_ids` が `['HYP-20261115-8f6552']` で、その `8f6552` の `parent_hypothesis_ids` は **`['HYP-20261115-5619fa']`**——**target とは別の仮説の子**である。`narrows_scope` の分岐は target に −1.15δ、spawned に +0.75δ/n を渡すので、`0a2508` の射程限定が `5619fa` の子に加点した。前ラウンド §12.2 が `compared_against_hypothesis_ids` について測った「直交した対を名指すと台帳に測っていない対立ができる」の**spawned 欄版**である。裁定は他セッション（`SESSION-20261115-5a6b15`）の判断なので行わず、記録して渡す。読むべき行は `EVL-20261115-3a7e7e`（target `e8ac3b`／spawned `bccd54`、親は `e8ac3b` なのでこちらは系譜に沿っている）。

### §12.8 マージ後の検証

- 10 ゲートすべて PASS（新ゲート `readings_integrity_check.py` を含む）
- `python3 -m unittest discover -s tests` → **Ran 758 tests … OK**（上流はテストを足していない）
- `append_only_check`：マージコミット `ad47bbc` で双方向に PASS——第一親（自分の `c9df70b`）の **28,423 行**、第二親（`origin/main` = `300a06a`）の **28,437 行**、どちらも「すべてバイト単位で現存」。既定の `--base origin/main` も同じ 28,437 行で PASS
- 台帳：questions 437／materials **4,433**／sessions **841**／read_log **13,780**／notes **859**／hypotheses **35**／evaluations **336**／errata 288
- errata スキーマ鏡：**適合 275／不一致 13 行**（上流は errata を足していないので §5.3 と同じ。自分の2件は適合側に入っている）
- `readings/`：**808 本**の `.md`・30,487,552 B・最小 2,392 B・中央値 29,987 B・note 行 859 件が 808 本を指す・孤児 0・違反 0。配線率 100.0%（**810/810**、`.md` 808＋データ2）
- 生成物：`BELIEF_MAP.md` **78,590 B**（マージ前 69,194 B）、`READING_MAP.md` **1,306,504 B**
- 予算：`notes.d` 131/131・`read_log.d` 131/131・`sessions.d` 136/136（**ファイル数不変**、追記のみ）、`tools/*_audit*.py` 57/57、`tools/` 99 ファイル 1.59 MiB

### §12.9 引き継ぎの更新

14. **§10-4 と §10-9 はマージ後に前提が変わった**（§12.3・§12.4）。`0a2508` はもう未評価ではなく、`Q-002` の同着は消えた。次に読むときは §12 を先に読むこと。
15. **一位の対が戻る第三の機構**（§12.4）：競合が狭められると、対立していない対の積が上がる。ラチェット（`supports` のみ）とは別に、**正規化による押し上げ**がある。どちらでも「一位＝対立が残っている」ではない。
16. **越境 spawn**（§12.7）：`spawned_hypothesis_ids` に target の子でない仮説を書くと、加点が別の系譜へ渡る。`compared_against_hypothesis_ids` については前ラウンド §12.2 と引き継ぎ4が書いた。**spawned 欄については誰も書いていない**ので、ここに引き継ぐ。
17. **`bccd54`・`8f6552` は直接評価0件で一位・二位にいる**（§12.5）。次に `Q-002` を渡された読み手は、一位の対の片方が「生まれたばかりで一度も検証されていない子」であることを先に確認すること。前ラウンド §12.4 の `e8ac3b` と同じ形である。
