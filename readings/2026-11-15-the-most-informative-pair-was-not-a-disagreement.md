# 最も情報量が多いと選ばれた対は、対立していなかった

実作業日 2026-11-15（UTC）。セッション `SESSION-20261115-e7ee43`。ブランチのシードは `92393982`。

内部編年ラベルと実日付は別なので両方を記録する（`docs/time-axis.md`）。本行の実日付は 2026-11-15。

---

## §0 何を頼まれ、何をしたか

### §0.1 割当レシート

`python3 tools/inspect_inquiry.py --assignment-json --seed 92393982`：

| | 値 |
|---|---|
| `dispersal_seed` | `92393982`（10進 2453223810） |
| `assigned_role` | **`proposer`** |
| `offered_target_question_id` | **Q-003** |
| `offered_reference_mode` | **`direct_response`** |
| 選出根拠 | 情報利得優先選出（score=2.952, active_H=2.246b, mean_u=0.316、最優先対立対 `HYP-20261115-ec0c6e` vs `HYP-20261115-5619fa`, EIG=0.2259） |

### §0.2 レシートは今回、食い違わなかった

前ラウンド（`SESSION-20261115-8912af`）が四欄を持つ最初の一筆で、そこで提示と採用は食い違った（提示 Q-003／`rereading_and_collision`、採用 Q-021 ほか4問／`revision_and_variation`）。**今回は食い違っていない。** 提示された Q-003 に実際に取り組み、提示された `direct_response`（前の記録に直接応答する）が実際に行ったこと——前ラウンドの報告が引き継いだ二件をそのまま実行する——と一致した。

二ラウンドで二つの場合が揃った。差が出る回と出ない回が両方記録されたので、`offered_*` 欄と `question_ids`／`prompt_template` の差が**何の観測点なのか**が台帳から読めるようになった。前ラウンドの差は人間の方向によるもので、今回の一致も人間の指示によるもの。**どちらの行にも「なぜ一致したか／なぜ食い違ったか」を書く欄は無い**ので、それは `sessions.notes` に書いた。

### §0.3 委任

人間は前ラウンドの報告 §8 と §10-1 が「次のラウンドの宿題」として残した二件を、両方実行してマージするよう委任した。

1. **最優先対立ペア `HYP-20261115-ec0c6e` / `HYP-20261115-5619fa`（EIG 0.2259）の採点。** 前ラウンドは設計変更を委任されたため Proposer の職務を実行せず、この対を採点しなかった。
2. **台帳行の一括追加。** 前ラウンドは `prompts/start.md` の規則（スキーマ・道具・手順書を変える変更は台帳行の一括追加と同じ PR に入れない）に従い、設計変更と報告一本・note 行・session 行のみを入れた。訂正・評価・read_log は次の PR とした。

本 PR は**台帳行の PR** である。道具・スキーマ・手順書は変更していない（§9 に例外を一つ記録する）。

---

## §1 採点の前に：この対は対立しているか

二つの仮説を読んだ。どちらも Q-003 の下、同じセッション `SESSION-20261115-c8e88f`・同じノート `NOTE-20261115-3b2371` から 2026-11-15 に分裂した。

| | `HYP-20261115-5619fa` | `HYP-20261115-ec0c6e` |
|---|---|---|
| 題 | 読み手相対の境界説 | 構造足場拘束説 |
| 分裂元 | `HYP-20261114-27fd10`（経路の二分説） | `HYP-20261114-0396ce`（再実行経路依存の拘束継承説） |
| 主張 | 装飾経路が閉包の外にあるかは経路の性質では決まらず、**読み手の正規化様式**（全局ID正規化型か順序・範囲・近傍依存型か）との接面で決まる | 上流の**内容を消去した後も**、上流に配置された構造的足場（スキーマ・境界・型枠）が下流の出力空間を狭め失敗費用を非対称に分配する |
| 何を測れば決まるか | 装飾介入（行の内容・字句・多重集合を変えず配置だけ変える）に対し、全局ID正規化型が変われば反証／順序依存型を全部同定してどれも変わらなければ 27fd10 へ縮退 | 内容消去版と内容保持版を足場を揃えて比べ、出力空間と失敗費用に差が無ければ棄却／足場だけ除いた版で出力空間が広がり失敗費用が対称化すれば保持 |

**この二つは互いを否定しない。** 一方は「装飾経路が判断入力に入るか」を、他方は「内容の消去後に足場が拘束するか」を言う。変数が違う。同じセッションで両方を測り、**両方が確認された**（§2・§3）。どちらかが立つために他方が倒れる必要は一度もなかった。

では、なぜ信念引擎はこの対を「最優先対立対」として選んだのか。§4 で測る。先に結論を書くと——**選んだ式が、対立を一度も検査していない。**

---

## §2 `HYP-20261115-5619fa` の採点

### §2.1 前セッションが残した告白

この仮説の `notes` 欄に、決定的な一文がある。

> 「note_index は collection_files() の順で同一 path の notes を後勝ち上書きする実装上の順序依存を持つが、今回の改名では発火しなかった（重複 path 行が改名シャードに無かった）。**したがって「note_index も順序依存型である」は実装からの推論であって測定ではない。**」

仮説の適用条件の第二項は「判断入力の生成器を、全局ID正規化型と順序・範囲・近傍依存型に**実装水準で分類できる場合**」である。前セッションは、自分の分類の一部が推論だったことを自分で書いていた。**その推論を測定に替えることが、この採点の中心になる。**

### §2.2 設計：多重集合を保ち、順序だけ変える介入を四つ

`state/` 以下の複製を `/tmp/w/v0`〜`v4` に作った（各 848 ファイル、`schema/`・`readings/`・`tools/`・`prompts/`・`docs/`・`map/` ごと）。**生きた台帳への注入は行っていない。** §3 の版（`v5`・`v6`・`v7`）も同じ作り方である。

| 介入 | 何を変えたか | 行の多重集合 |
|---|---|---|
| I0 |  nothing（基底） | — |
| **I1** | notes のシャード1本の**接尾辞だけ改名**（`…4351b786c062` → `…ffffb786c062`）。重複 path を持つ9組のうち1組の勝者を反転させるよう選んだ | **保存**（sha `0ef4bcb187316852` 不変） |
| **I2** | read_log の1行を**最後のシャードから最初のシャードの末尾へ移動**。ファイル名は一切変えない | **保存**（sha `fec1cdad6af0d668`、13,676行）。和集合の**順序だけ**変化（`a901a877a14e0f4f` → `42a851cd8ef57b32`） |
| **I3** | materials のシャード1本を改名（`2026-11-14-092b0ce27813` → `…ffff0ce27813`）。ファイル名順の位置 111→113 | **保存**（sha `ecef9e144420b7d2` 不変） |
| **I4** | materials の**統合アンカー**シャードを改名（`2026-10-24-000000000000` → `…ffff00000000`） | **保存** |

四つとも `docs/parallel-work.md` の手順8-2 と同じ種類の操作——**行の字句を一字も変えず、配置だけを変える**——である。前ラウンドの私が実際にやった移動（和集合の sha256 を保つ移動）より一段強い。あの移動は和集合の順序まで保存したので、順序依存の読み手にも見えなかった。I2 は順序だけを変える。

### §2.3 測定：35読み手 × 4介入

各読み手の出力（stdout+stderr、または生成ファイル）を sha256 で指紋化し、**サンドボックスの絶対パスを出力から正規化してから**比較した。

正規化は必須だった。最初に走らせた版は `referent_check` を「順序敏感」と報告したが、差分は**トレースバックの中の `/tmp/w/v0` と `/tmp/w/v1` という文字列だけ**だった。実際には `.git` が無くて実行できていなかった。**走らない検査は、何も見つからなかった検査ではない**（前ラウンド §8 の教訓）。各サンドボックスに git を初期化して測り直した。

同じ誤りはもう一つあった。`name_layers` は全サンドボックスで rc=2 だったので「実行不能」と分類したが、**私の呼び出し方が間違っていただけ**だった（サブコマンド `citations`／`state-notes`／`sources` が必須）。三つのサブコマンドで測り直した。だから読み手の数は 33 ではなく **35**（`name_layers` を三つに分けて数える）で、下表は 35 読み手 × 4 介入の完全被覆である。

結果：

| 読み手 | I1 notes改名 | I2 read_log移動 | I3 materials改名 | I4 アンカー改名 |
|---|---|---|---|---|
| **map_build → READING_MAP.md** | 不変 | 不変 | **156行変化** | **不変** |
| **associations** | 不変 | **変化** | 不変 | 不変 |
| **referent_check** | 不変 | 不変 | **75件 dropped** | **2,080件 dropped** |
| **taxonomy_plan** | 不変 | 不変 | 不変 | **2,080件が別の桶へ** |
| 他の31読み手（9ゲート全部・belief_state の両マップ・inspect_inquiry のパケット3種とレシート・note_index 3種・validate_seed・learning_metrics・size_budget 2種・date_axis 2種・read_log_backfill・append_only_check・inheritance・selection_audit・preservation_layers・name_layers 3種・drift_audit・errata_audit・claim_wiring・addition_effect・layer2_accounting・lineage_credit_accounting・peripheralisation・naming_coverage） | 不変 | 不変 | 不変 | 不変 |

**35読み手のうち装飾介入に敏感なのは4つ、不変は31。敏感な4つは、それぞれ別の介入にだけ敏感である。** 四つ全部に敏感な読み手は一つも無い。I1（notes の接尾辞改名）に敏感な読み手は**一つも無い**。

### §2.4 敏感な4つの機序

**map_build（範囲・チャンク依存）** — materials のシャードを I3 で改名すると `READING_MAP.md` の156行が動き、`MAT-20261114-*` の塊が別のチャンクへ移った。前セッションが測った164行変化の再現である（別のシャードで）。**しかし I4（アンカー改名）では `READING_MAP.md` は sha256 まで含めて完全不変だった。** 同じ「materials シャードの改名」でも、どのシャードを動かすかで結果が違う。`BELIEF_MAP.md` は四つとも不変——belief_state は全局ID正規化型である。

**associations（近傍・新しさ依存）** — I2 で read_log の1行を移動しただけで、`since_last`（その対象が最後に読まれてから何行経ったか）が変わり、**順位スコアが変わった**。

```
        Q-002  rows=365 active=263 sessions=363  since_last 10 → 9    score 23.67 → 23.68
        Q-003  rows=354 active=254 sessions=353  since_last  0 → 24   score 21.07 → 21.03
        Q-001  rows=339 active=221 sessions=337  since_last 11 → 10   score 19.15 → 19.15
```

`rows`・`active`・`sessions` は**一つも変わっていない**。変わったのは位置から計算される新しさだけで、それがスコアを動かした。行の内容も多重集合も同一で、**配置だけ**を変えた結果である。Q-003 は今回提示された対象問いであり、そのスコアが装飾介入で 21.07 から 21.03 へ動いた。

**referent_check（パス键の履歴比較）** — 実装を読むと、この道具は**コミット間で同じパスのファイルを比べ**、親にあってコミットに無い ID を「dropped」と報告する。シャードを改名してコミットすると、旧パスが消えたように見えるので、その中身の ID が全部「dropped（ただし HEAD では `same`）」として並ぶ。**これは偽警報ではなく、実際に起きたこと（ファイルが改名された）の正確な報告である。** ただし報告される件数は改名したシャードの行数に比例する——小さなシャードで75件、統合アンカーで**2,080件**。**装飾的な改名には、行数に比例する整合性報告のノイズという費用がある。**

**taxonomy_plan（ファイル名順の桶分け）** — この道具は収蔵素材を「シャード収蔵素材 前半（`< 2026-10-24-a`）／後半（`>= 2026-10-24-a`）」という**ファイル名順の閾値**で二つの作業単位に分ける。I4 で統合アンカーシャードを改名すると、その中身が閾値の向こう側へ移った：

```
   U06 | Track-2 | PENDING |  2,080 items |   969,332 chars | シャード収蔵素材 前半（< 2026-10-24-a）
   U07 | Track-2 | PENDING |  1,629 items | 1,288,253 chars | シャード収蔵素材 後半（>= 2026-10-24-a）
 → U06 | Track-2 | PENDING |      0 items |         0 chars | シャード収蔵素材 前半
 → U07 | Track-2 | PENDING |  3,709 items | 2,257,585 chars | シャード収蔵素材 後半
```

**合計は不変である**（2,080 + 1,629 = 3,709 件、字数の和も同じ）。動いたのは**分割だけ**。それでもこれは「次にどの素材をどの作業単位で読むか」という計画であり、装飾的な改名が**作業の割当**を変えた例である。I1・I2・I3 では不変で、I4 だけで動いた——動かしたシャードが閾値の境界そのものだったからである。

### §2.5 推論は測定で反証された：note_index

I1 は note_index の後勝ちを反転させるために設計した。対象は重複 path を持つ9組のうち1組で、両行が別々のシャードの1行目に入っているものを選んだ。

**插入順が実際に反転したことを確認した**：

```
  v0（改名前）  collection_files の順: …4351b786c062 → …784d35229157
                その path の行の插入順: ['NOTE-20261113-398a36', 'NOTE-20261113-13108f']
  v1（改名後）  collection_files の順: …784d35229157 → …ffffb786c062
                その path の行の插入順: ['NOTE-20261113-13108f', 'NOTE-20261113-398a36']
```

そして `build_view()` の出力は**両方で完全同一**だった。勝者 `note_id` も `note_ids` の並びも `curated.mode` も `report_session_id` も同じ。`--report`・`--check`・`--orphans` の三つの出力 sha も四つのサンドボックスすべてで同一。

機序を特定した。`note_index.py:359` の `order_note_rows()` が**明示的な正規化層**である：

```python
def order_note_rows(notes):
    """Order note rows in ledger order, honouring explicit ``supersedes``."""
    rows = list(notes.values())
    ...                                  # supersedes 辺を張る
    if not edges: return rows            # 辺が無ければ插入順
    ...                                  # 有ればトポロジカルソート
```

`NOTE-20261113-398a36` は `supersedes: ["NOTE-20261113-13108f"]` を宣言している。だから挿入順がどうであれ、正規化後の順序は 13108f → 398a36 で固定され、`rows[-1]` の勝者は 398a36 で不変。**台帳に `supersedes` を持つ notes 行は 852 中 28 行**あり、その 28 行については配置が判断入力に入らない。

`build_view()` のコードには確かに後勝ちがある（`for row in rows:  # later rows win` と `entry["note_id"] = rows[-1]...`）。**実装に順序依存のコードがあることと、出力が順序に依存することは別である。** 前セッションの推論は前者から後者を導いた。導けなかった。あいだに正規化層があった。

### §2.6 判定

`HYP-20261115-5619fa` の排他条件の二つの肢：

- **肢 (a)「全局ID正規化型の読み手の出力が装飾介入で変わるなら、閉包外性は読み手に条件づけられず経路そのものに属する」** — 発火しなかった。全局ID正規化型として実装から同定され、測定でもそれを確認した読み手（belief_state の両マップ、inspect_inquiry のパケット3種とレシート、validate_seed、selection_audit、drift_audit、layer2_accounting）は**四つの介入のすべてで不変**だった。
- **肢 (b)「順序・範囲・近傍依存型の読み手をすべて実装上同定したうえで、装飾介入に対してそれらが一つも変化しないなら、境界を読み手との接面に置く本説は不要になり 27fd10 の経路二分説へ縮退する」** — 発火しなかった。同定された依存型のうち **map_build（範囲・チャンク）、associations（近傍）、referent_check（パス键の履歴）、taxonomy_plan（ファイル名順の桶分け）の四つが実際に変化した**。

したがって **`supports`**。加えて、測定は仮説が主張するより**細かい粒度**を出した。正規化様式は読み手の属性ではなく、**（読み手 × コレクション × どのシャードか）の三つ組の属性**である。map_build は materials の一つのシャード改名に敏感で、別のシャード改名には不変だった。

そして測定は四つ目の正規化様式を出した：**ファイル名順の閾値で作業を分割する型**（taxonomy_plan）。これは「順序・範囲・近傍」のどれでもなく、**分区**である。

適用条件の第二項——「実装水準で分類できる場合」——は**そのままでは満たせない**。note_index が反例である：実装に後勝ちのコードがありながら、上流の正規化層のせいで出力は不変だった。**分類は実装の読解では決まらず、介入と測定でのみ決まる。** これは適用条件の追加（「分類は測定で確定できる場合」）として記録する。仮説の `notes` 欄が自分で予告していたとおりである。

**分裂元 `HYP-20261114-27fd10` について。** 27fd10 は「装飾・保存経路は**次の読み手への推薦パケット**を変更せず、閉包の外にある」と言う。`inspect_inquiry --packet`（既定・Q-003 固定・auto）は四つの介入すべてで**不変**だった。だから **27fd10 は自分の述べた範囲では反証されていない。** 測定が示したのは、27fd10 が名指ししたパケット以外にも判断へ流れる読み手があり（READING_MAP のチャンク、associations の順位スコア、referent_check の整合性報告）、その一部が装飾経路に敏感だということである。27fd10 は誤りではなく、**狭い**。5619fa は同じ観測を説明でき、27fd10 には説明できない部分がある。評価の `compared_against_hypothesis_ids` に 27fd10 を置いたのはこの理由による（§4.4 で、この欄が信念状態に何をするかも測った）。

---

## §3 `HYP-20261115-ec0c6e` の採点

### §3.1 設計：四つの版

排他条件が要求するとおりに三版を作った。

| 版 | 内容（エピソード） | 足場（構造） |
|---|---|---|
| **A** `v0` | 保持 | 保持 |
| **B** `v5` | **消去**（ファイル＋台帳行の散文） | 保持 |
| **B′** `v7` | **消去**（`readings/*.md` だけ。台帳行は無傷） | 保持 |
| **C** `v6` | 保持 | **除去** |

B′ は B の内訳を分離するための対照である。B の消去は二つの半分を持つ——`readings/*.md` の本文と、台帳行の中の散文欄——ので、**どちらの半分が何を変えるか**を分けて測った（§3.4）。

- **B の内容消去**：`readings/*.md` **802本の本文を空にした（30,180,380 B のエピソード的テキストを除去）**。さらに notes の `note` 欄・sessions の `notes` 欄・read_log の `note` 欄 **14,463 件を空文字にした**。行・ID・構造・スキーマは一切触っていない。
- **C の足場除去**：`schema/` 全体から **72 個の制約**（`additionalProperties: false` 21 個・`enum`・`required`）を再帰的に外した。`readings/` は 30,239,007 B のまま不変。

### §3.2 出力空間を測る電池

「出力空間の広さ」を、**下流の書き手が書いてもゲートを通る行の形の種類数**として操作化した。18 組のプローブを作り、各組は「対照（実在行を雛形にした正しい行）」と「欠陥（同じ行を1欄だけ壊したもの）」の対である。対照が受理され欠陥が拒否されて初めて、そのプローブが意図した制約を分離していることになる。

**18 組のうち 13 組が制約を分離した。** 分離しなかった5組の内訳は、そもそも受理されるべきものが3組（前ラウンドに広げた `target.type: "erratum"` と `subject_type: "erratum"`、そして施行日前の日付を持つ question の register 欠落）と、効かなかったものが2組（`errata.verdict` の enum 違反——理由は §5、そして register 規則の施行日後の日付を持つ question の register 欠落——理由は §3.6）。

結果：

| プローブ（対照は全版で受理） | A 内容+足場 | B 消去+足場 | C 内容+足場除去 |
|---|---|---|---|
| session：未知の追加欄 | 拒否 | 拒否 | **受理** |
| session：必須欄の欠落 | 拒否 | 拒否 | **受理** |
| read_log：`target.type` が enum 外 | 拒否 | 拒否 | 拒否 |
| read_log：`target.id` が解決しない | 拒否 | 拒否 | 拒否 |
| note：`salience` が上限超過 | 拒否 | 拒否 | 拒否 |
| note：`mode` が enum 外 | 拒否 | 拒否 | **受理** |
| errata：`subject_type=tool` なのに subject_id が台帳ID | 拒否 | 拒否 | 拒否 |
| hypothesis：`exclusion_clause` の欠落 | 拒否 | 拒否 | **受理** |
| hypothesis：`status` が enum 外 | 拒否 | 拒否 | **受理** |
| relation：左端点が解決しない | 拒否 | 拒否 | 拒否 |
| relation：`relation_type` が enum 外 | 拒否 | 拒否 | **受理** |
| question：`origin` の欠落 | 拒否 | 拒否 | **受理** |
| question：`status` が enum 外 | 拒否 | 拒否 | **受理** |

**A と B は 18 組すべてで一致した。一つも違わなかった。**

### §3.3 失敗費用の分布

拒否はすべて `validate_seed` の FAIL、つまり **PR を止める硬い失敗**である。受理は無費用。

| 版 | 硬い失敗を出す欠陥形 | 費用の分布 |
|---|---|---|
| A | **13 / 18** | 非対称（形によってゲートを落とすかどうかが分かれる） |
| B | **13 / 18** | **A と完全同一** |
| C | **5 / 18** | 平坦化（13 形が無費用になる） |

**30.18 MB のエピソード的テキストと 14,463 件の散文欄を消して、失敗費用の分布は 1 ビットも動かなかった。** 足場を除くと 13 形が 5 形へ縮み、費用は対称化した。

ここで一つ区別しておく。**清潔な台帳に対する `validate_seed` の出力は A・B・C の三版でバイト単位に同一**（sha `a84a76dab40d6b11`）である。制約を緩めても、既に適合している行についての判定は変わらないからだ。足場の効果は**適合しない行を書こうとしたときにだけ**現れる。だから電池が出力空間を測るのであって、ゲートの一回の実行は測らない。

### §3.4 内容消去で判断入力は変わったか——35読み手全部で測った

最初は三つの出力（レシート・`BELIEF_MAP.md`・パケット）しか見ていなかった。それでは足りないと思い直し、§2.3 と同じ 35 読み手 × 4 版の被覆を B・B′・C についても走らせた。

| | A `v0` | B `v5`（ファイル＋台帳散文） | B′ `v7`（ファイルだけ） | C `v6`（足場除去） |
|---|---|---|---|---|
| 変化した読み手 | — | **19 / 35** | **12 / 35** | **1 / 35** |
| 割当レシート（`--assignment-json`） | `{92393982, proposer, Q-003, direct_response}` | **バイト同一** | **バイト同一** | **バイト同一** |
| `validate_seed` の出力 | `a84a76dab40d6b11` | **バイト同一** | **バイト同一** | **バイト同一** |
| `BELIEF_MAP.md`（54,203 B） | `054ae8736da7feaf` | **バイト同一** | **バイト同一** | **バイト同一** |
| `append_only_check` | rc=0 | **rc=1**（14,505行） | rc=0 | rc=0 |
| パケット（`--packet auto`, 76,890 B） | `b95c188235b4b440` | 変化（80,216 B、**58行だけ違う**） | 変化 | **バイト同一** |

（この表のバイト数は、複製が本 PR の行を書く前に作られたためのものである。現在の `BELIEF_MAP.md` は 62,795 B。）

**B′ が B の内訳を分けた。** 802 本の精読報告を 0 バイトにしても（30,180,380 B の除去）、変わるのは 35 のうち **12** だけで、その 12 はすべて散文を読む読み手である（`READING_MAP.md`・note_index の report/orphans・パケット2種・size_budget --strict・date_axis の報告・inheritance --unread・selection_audit・taxonomy_plan・naming_coverage・name_layers citations）。**台帳行の散文欄 14,463 件を空にした残り7つ**が加わって B の 19 になる（associations・preservation_layers・addition_effect・layer2_accounting・peripheralisation・name_layers state-notes、そして `append_only_check`）。

そして C——足場を 72 制約ぶん除去した版——で変化した読み手は **35 のうち 1 つ**（taxonomy_plan の字数集計だけ。スキーマファイル自体が縮んだので、`schema/tools/tests` の桶の字数が 2,470,791 → 2,464,411 になった）だった。

### §3.4.1 全部内容消去のあとで、9 ゲートは通る

これが一番はっきりした結果である。B′（802 本すべて 0 バイト、台帳行は無傷、`git status -- state` の変更 0 件）で、正規の手順どおりマップを再生成してから 9 ゲートを走らせた：

```
  PASS validate_seed.py            PASS note_index.py --check
  PASS append_only_check.py        PASS read_log_backfill.py --check
  PASS inspect_inquiry.py --check-map   PASS date_axis.py --enforce-shards
  PASS belief_state.py --check-map      PASS learning_metrics.py --check
  PASS size_budget.py --strict
```

**9 ゲートすべて PASS である。** 30.18 MB のエピソード的テキストが消えても、この書庫の検査面は何も言わない。割当レシートも `BELIEF_MAP.md` も `validate_seed` の出力も `append_only_check` の出力も、A と**バイト単位で同一**である。

一方で B（台帳行の散文欄も空にした版）では `append_only_check` だけが rc=1 になる：

```
FAIL: 14505 ledger line(s) that existed at HEAD are no longer present byte for byte
  notes: 42 (reserialised 42)
  read_log: 13671 (edited 13671)
  sessions: 792 (edited 792)
```

`reserialised` は「同じ内容・違うバイト」、`edited` は「同じ ID・違う内容」である（`tools/append_only_check.py:185-214`）。read_log 13,671 行と sessions 792 行は `edited`——散文欄を空にしたので内容が変わった。notes の 42 行は `reserialised`——私の消去スクリプトが書き直したためバイトだけが変わった。

**つまり足場は二つの違ったものを守っている。** スキーマという宣言層は**形**を守る（内容は見ない）。append-only という手続き層は**台帳行の字节**を守る（`readings/*.md` の本文は守らない）。だから：

- 台帳行の散文を消すと、一つのゲートが硬く失敗する（rc=1）。**失敗費用が非対称に分布する**——これは ec0c6e の主張どおりである。
- `readings/*.md` の 30.18 MB を消しても、**どのゲートも失敗しない**。守っている検査が無いからである。

**この層は、本書を書いている間に私自身を捕まえた。** 採点後に測定の確定値を自分の行へ反映しようとして、私は行を書き換えるスクリプトを書いた。スクリプトは対象シャードの**全行**を `json.dumps(..., sort_keys=True, separators=(",", ":"))` で書き直した。私の行は直り、**同じシャードにあった既存の2行は再シリアライズされた**（内容は同一、バイトが違う）。

`validate_seed` は **PASS したまま**だった。捕まえたのは `append_only_check` だけである：

```
FAIL: 2 ledger line(s) that existed at 1c8da78 … are no longer present byte for byte
  notes: 1 (reserialised 1)     - NOTE-20261115-d959e0: reserialised
  sessions: 1 (reserialised 1)  - SESSION-20261115-bf6052: reserialised
  reserialised = same content, different bytes; edited = same ID, different content; removed = gone
```

`git show 1c8da78:<path>` で原バイトを取り戻し、自分の行だけを末尾に付け直して `PASS: all 28258 ledger lines … are still present byte for byte` になった。

三つのことが同時に言える。**一、** 宣言層と手続き層（`validate_seed`）は字节の同一性を見ないので、この種の破壊に対して黙っている。**二、** append-only 層は「内容が変わった」だけでなく「**字节が変わった**」だけで失敗するので、善意の整形でも止まる。**三、** 私はこの報告の §3.4.1 で「append-only 層は台帳行の字节を守る」と書き、その数行後に自分でそれを試した。守られている側は書き手自身を含む。

内容を消しても機構は止まらない。**特定の削除済み課題を再開させることはできない**——債務を散文にしか書いていなかった場合、その記述は B・B′ で消えている——が、**出力空間は A と同じに狭いまま**である（§3.2・§3.3）。これは ec0c6e の主張そのものであり、同時にその主張が名指ししていない限界でもある：**足場が守るのは台帳行であって、書庫の本文ではない。**

### §3.5 判定と、足場が二層だという追加

**`supports`。** 排他条件の第二肢（「足場だけを除去した版で出力空間が広がり失敗費用が対称化するなら本説は保持される」）が成立し、第一肢（棄却条件）は成立しなかった。

測定はもう一つ、仮説が名指ししていない構造を出した。**足場は二層ある。**

- **宣言層**（`schema/*.json`）：72 制約。C で外した。13 形のうち **8 形**がここだけで支えられていた。
- **手続き層**（`tools/validate_seed.py` の中の検査）：C でも **5 形**が拒否され続けた——`target.type` の解決先（前ラウンド私が `endpoint_collections` に追加した対）、`target.id` の参照閉包、relation の端点閉包、errata の誤ラベル保護、`salience` の上限。

だから「足場」は `schema/` と同値ではない。前ラウンド §3 で「enum だけ広げると解決先が無く検査が落ちる」と書いたのはこの二層のことで、**今回それを電池で測った**。

§3.4.1 は第三の層を出した。**append-only 層**である。これは形ではなく台帳行の字节を守り、`readings/*.md` の本文は守らない。三層が守っているものはそれぞれ違い、だから同じ「消去」でも層ごとに違う失敗になる：

| 層 | 守っているもの | 802本の本文を 0 B にする | 台帳行の散文を空にする | 制約を 72 個外す |
|---|---|---|---|---|
| 宣言層 `schema/` | 行の**形** | 何も言わない | 何も言わない | （外された側） |
| 手続き層 `validate_seed` の検査群 | 参照閉包・誤ラベル・ラチェット | 何も言わない | 何も言わない | **5形だけが残る** |
| append-only 層 | 台帳行の**字节** | **何も言わない（9ゲート PASS）** | **rc=1（14,505行）** | 何も言わない |

これは ec0c6e の棄却条件には当たらない——「内容消去版と内容保持版で出力空間の広さと失敗費用に差が無いなら棄却」だが、差はあった（§3.2・§3.3、そして B での rc=1）。**適用条件の追加として記録する**：足場が拘束するのは台帳行であって書庫の本文ではなく、したがって「上流のエピソード的内容を消去した後も拘束が残る」の「残る」は、行の形と行の字节について言えるのであって、本文の存在については言えない。

`salience` の上限が C でも拒否され続けた理由は、私の介入が不完全だったからではなかった。電池のプローブは `salience=9` を使っていて、それは**二つの層の両方に同時に引っかかる**：宣言層は `maximum: 4`、手続き層は `tools/validate_seed.py:244-248` の `if isinstance(salience, int) and salience > 3`（2026-11-12 以降に採番された行に対するラチェット）である。C は宣言層しか外していないので、手続き層のラチェットが生き残って拒否した。**このプローブは宣言層を分離していない。**

### §3.6 宣言と施行が逆方向にずれている例——そして本書を書いている間に噛まれた

§5 で見るのは「宣言されているが施行されていない」方向である。`salience` は逆方向にずれている：**手続き層が宣言層より厳しい。** `schema/notes.schema.json` は `salience` の `maximum: 4` を宣言し、`validate_seed.py` は 2026-11-12 以降の行に 3 を課す。

これは抽象的な話では終わらなかった。**本書の note 行を書いて 9 ゲートを回したとき、私自身がそれで落ちた。**

```
FAIL: literary inquiry seed has errors
  - notes:NOTE-20261115-f57e05: salience 4 exceeds maximum 3 for rows minted from 2026-11-12 onward
```

私はスキーマを読んで `salience: 4` と書いた。スキーマは 4 を許すと書いてある。**ゲートは 3 までしか許さない。** 自分の行を 3 に直して PASS した。宣言層を読んで書く書き手は、手続き層がより厳しいときに必ず一度落ちる——そして落ちるまで、二つの層がずれていることを知る手段が無い。

### §3.7 施行日が両側から挟まれている規則

`docs/registers.md` の規則1（`register` は 2026-11-16 以降に採番された `Q-*`／`HYP-*` に必須）は、電池では**三版すべてで受理された**——施行日後の日付を使った欠陥行でも受理された。

`tools/validate_seed.py:105-118` の `_is_new_row()` が理由である：

```python
stamp = id_stamp(record_id)
if not stamp or stamp < cutoff:          # 下限：20261116
    return False
today_stamp = (today or datetime.date.today()).strftime("%Y%m%d")
return stamp <= today_stamp              # 上限：今日
```

docstring が理由を書いている：「Legacy rows carry internal chronology labels in their IDs (some are in 2027), so a bare `>= cutoff` test would fail rows that were written long ago. The upper bound (today) keeps those labels out」。

したがって規則は**下限と上限の両方から挟まれており、実日付が 2026-11-15 の今日は一度も発火できない**。前倒しシャードは `date_axis.py --enforce-shards` が拒否するので、今日 20261116 の刻印を持つ行はそもそも書けない。**規則は明日から効く。今日は効かない。** これは設計どおりで、欠陥ではない。電池のこの2組が「分離しなかった」のは、分離すべき制約が今日は存在しないからである。

同じことが規則2（claim wiring、`CLAIM_WIRING_RULE_FROM = "20261116"`）にも言える。**どちらも今日は私の行に適用されない。** それでも本書の note 行の `reading_revised` と `retraction` の claim には `hypothesis_ids` か `no_hypothesis: true` を書き、新規仮説には `register: "judgment"` を書いた。規則が縛っていないときに規則に従った行を書いておくと、施行日に「規則が効き始めた」ことを古い行との差として測れる。

---

## §4 引擎が選んだ対は、なぜ対立していなかったのか

### §4.1 式

`tools/belief_state.py:548-566`：

```python
best_pair = None
candidates = active_entries if len(active_entries) >= 2 else hyp_entries
best_score = -1.0
for i in range(len(candidates)):
    for j in range(i + 1, len(candidates)):
        ha, hb = candidates[i], candidates[j]
        ig_score = ha["posterior"] * hb["posterior"] * (ha["uncertainty"] + hb["uncertainty"])
        if ig_score > best_score:
            best_score = ig_score
            best_pair = {... "expected_info_gain": round(ig_score, 4)}
```

**「期待情報利得」は `p_a × p_b × (u_a + u_b)` である。** 二つの仮説が両立するか、系譜上つながっているか、同じ変数について主張しているか、**何一つ検査していない**。active な仮説の全組を総当たりして、この積が最大の組を選ぶだけである。

そして選ばれた対は `:625` で「**最優先対立対**」という語でパケットに書かれ、`:722` で「最優先検証ターゲット（最大期待情報利得）」として次の読み手に渡される。

### §4.2 順位を実測した

Q-003 には仮説 18 件、active 15 件、組は **105**。式をそのまま再実装して全組を並べた（基底コミット `1c8da784` の worktree で、同じスクリプトを走らせた）。

| 順位 | EIG | 対 | 系譜関係 |
|---|---|---|---|
| **1** | **0.2259** | `ec0c6e` vs `5619fa` | **無関係**（引擎の選択） |
| 2 | 0.0252 | `ec0c6e` vs `0396ce` | **親子**（0396ce が親） |
| 3 | 0.0252 | `ec0c6e` vs `17ea95` | 無関係 |
| 5 | 0.0201 | `5619fa` vs `0396ce` | 無関係 |
| **11** | **0.0082** | `5619fa` vs `27fd10` | **親子**（27fd10 が親） |

- 実際に競合する親子の対 `5619fa / 27fd10`——5619fa の排他条件が「27fd10 へ縮退する」と名指ししている相手——は **105組中11位**で、EIG は引擎の選択の **1/27.5**。
- もう一方の親子 `ec0c6e / 0396ce` は2位だが、それでも **1/9**。
- 1位と2位の差は 0.2259 対 0.0252 で **9倍**。

### §4.3 なぜこの二つが一位なのか——式の中の三つの量

一位の理由は「新しいから」ではなかった。`posterior` と `uncertainty` の定義を測った：

```python
posteriors = {h: exps[h] / total_exp for h in hids}          # 問いの中の log_odds の softmax 占有率
raw_u = (1.0 / math.sqrt(1.0 + n_indep)) * (1.25 if adv_count == 0 else 1.0)
uncertainty = round(min(1.0, max(0.05, raw_u)), 4)
```

`uncertainty` は**独立ソース数**で下がり、**敵対的に触られたことが無い**と 1.25 倍される。基底での値：

| 仮説 | log_odds | posterior | uncertainty | 直接評価 | adv | verdicts |
|---|---|---|---|---|---|---|
| `ec0c6e` | **+3.6000** | **0.4000** | **0.8839** | 1 | **0** | supports ×1 |
| `5619fa` | **+3.3750** | **0.3194** | **0.8839** | 1 | **0** | supports ×1 |
| `17ea95` | +1.6650 | 0.0578 | 0.2041 | 7 | 8 | narrows ×3, supports ×4 |
| `0396ce` | +1.5700 | 0.0525 | 0.3162 | 5 | 5 | narrows ×3, supports ×2 |
| `27fd10` | +0.6525 | 0.0210 | 0.3333 | 3 | 4 | supports ×1, narrows ×2 |

**上位2件で softmax 質量の 72% を占めている。** どちらも直接評価1件・敵対的接触0件で `uncertainty` が上限近く（1.25/√2 = 0.8839）。質量は `narrows_scope` の分岐が作ったものである（`belief_state.py:397-403`）：

```python
elif verdict == "narrows_scope":
    log_odds[target_id] -= 1.15 * delta
    adversarial_touches[target_id] += 1
    if spawned:
        boost = (0.75 * delta) / len(spawned)
        for shid in spawned:
            log_odds[shid] += boost          # ← 親が絞られると子に質量が移る
```

前ラウンド以前に親（`0396ce`・`27fd10`）が `narrows_scope` を受け、その boost が子（`ec0c6e`・`5619fa`）へ入り、親自身は `adversarial_touches` を積み上げて `uncertainty` を下げた。**つまり引擎が「最も対立している」と呼んだ二つは、それぞれの親が絞られたときに質量を受け取った二つであり、その親たちこそが本当の競合相手である。** 親は boost を渡した側なので `adv > 0` で `uncertainty` が低く、積では勝てない。

式が選んでいるのは「対立」ではなく、**質量と未接触の積**である。

### §4.4 この語が持つ、実測できる帰結

`supports` の分岐（`tools/belief_state.py:389-395`）：

```python
if verdict == "supports":
    log_odds[target_id] += delta
    if compared:
        share = (0.20 * delta) / len(compared)
        for cid in compared:
            log_odds[cid] -= share          # ← 名指しされた側が減点される
            adversarial_touches[cid] += 1
```

**`compared_against_hypothesis_ids` に名前を書かれた仮説は、相手が support されるたびに 0.20δ を失い、`adversarial_eval_count` が増える。** つまりこの欄は「何を比べたかの記録」ではなく、**信念状態を動かす入力**である。

したがって引擎の勧告に従って、直交した対の一方を support し、もう一方を `compared_against` に書くと——**何も対立を測っていないのに、台帳には対立が解決されたかのように事後確率が動く。** 0.20δ は小さいが、`adversarial_touches` も増えるので、`indep_sources` と独立性の計上にも影響する。

私はこれを避けた。二つの評価の `compared_against_hypothesis_ids` には、引擎が選んだ対ではなく、**実際に競合し、実際に測った相手**——それぞれの分裂元——を書いた（§2.6・§3.5）。

### §4.5 自己適用：採点したら、勧告が強くなった

§4.4 が予言することを、**この PR の自分自身の行で測った**。二つの評価（`supports` × 2）を書いた前後で、基底コミットの worktree と現在の作業ツリーに同じスクリプトを走らせた。

| | 採点前（`1c8da784`） | 採点後（本 PR） | 変化 |
|---|---|---|---|
| Q-003 の仮説 / active / 組 | 18 / 15 / 105 | 19 / 16 / 120 | +1 |
| **引擎の選択** | `ec0c6e` vs `5619fa` | **同じ対** | 変わらず |
| **その対の EIG** | **0.2259** | **0.2951** | **+30.6%** |
| `p_a × p_b` | 0.4000 × 0.3194 = 0.1278 | 0.5060 × 0.4041 = 0.2045 | +60.0% |
| `u_a + u_b` | 0.8839 × 2 = 1.7678 | 0.7217 × 2 = 1.4434 | −18.3% |
| 親子 `ec0c6e / 0396ce` | 2位 / **0.0252** | 5位 / **0.0068** | **−73%** |
| 親子 `5619fa / 27fd10` | 11位 / **0.0082** | 13位 / **0.0022** | **−73%** |
| `ec0c6e` log_odds | +3.6000 | **+4.9500** | **+1.35**（= δ） |
| `0396ce` log_odds / adv | +1.5700 / 5 | **+1.3000 / 6** | **−0.27**（= 0.20δ）/ +1 |
| `27fd10` log_odds / adv | +0.6525 / 4 | **+0.3825 / 5** | **−0.27** / +1 |
| Q-003 active entropy | 2.2462 b | **1.5402 b** | **−31.4%** |
| Q-003 KL from uniform | 1.7854 b | **2.6375 b** | **+47.7%** |
| 飽和判定の `top_eig`（閾値 0.02） | 0.2259 | **0.2951** | **閾値から遠ざかった** |
| パケットの headline score | **2.952** | **2.262** | **−23.4%** |

δ は `EVIDENCE_WEIGHTS["reproducible_script"] = 1.35` × `indep_discount = 1/√k_rep = 1`（session が違うので繰り返しにならない）× `comp_factor = 1.0`（比較対象を書いた）= **1.35**。log_odds の変化 +1.35 と −0.27 は式のとおりで、**推断ではなく算術が一致した**。

三つのことが同時に起きた。

1. **勧告が強くなった。** 対立を測って両方を `supports` にした結果、引擎は同じ対を**より強く**「最優先対立対」として次の読み手に渡す。EIG は +30.6%。`uncertainty` が 0.8839→0.7217 へ下がった（独立ソースが 1→2 で 1.25/√3）にもかかわらず、`posterior` の積が +60% でそれを上回った。
2. **競合する対が遠ざかった。** 本当の競合相手である二つの親子の対はどちらも **−73%**、順位は 2→5 と 11→13。比較対象として名指しした親は −0.27 を失い `adversarial_touches` が増えたので、`uncertainty` の 1.25 倍も失った。**親を名指しすることは、親を二重に弱くする。**
3. **同じレシートの一文の中で、二つの数が逆方向に動いた。** パケットの headline score は 2.952 → **2.262**（−23%）へ下がり、その文が名指す対立対の EIG は 0.2259 → **0.2951**（+31%）へ上がった。`priority_score = active_entropy + 0.8·mean_u + 1/√(1+total_evals)` は entropy の低下で下がり、`top_competing_pair` の積は posterior の上昇で上がった。**どちらも「次に見る場所」を表す数として同じ行に並んでいる。**

そして Q-003 の信念状態は二つの仮説へ集中した（active entropy −31%、KL +48%）。**答えるほど、その問いは「もう答えなくてよい」方向へ動くのではなく、「同じ二つをもっと見よ」方向へ動く。** 飽和閾値 0.02 に対して `top_eig` は 0.2259 から 0.2951 へ**遠ざかった**。Q-001（0.0067）と Q-002（0.0000）が飽和と判定されている一方で、である。

これが §4.4 の帰結の実測である。**式は対立を検査していないので、対立を測って解決しても、式の数値は解決を「もっと見るべき」方向に解釈する。** ラチェットは一度回ると戻らない：`supports` に log_odds を下げる項は無い。

### §4.6 新規仮説

この測定から条件付き仮説を一件立てた（Proposer の職務）。`Q-20261116-3872ec`（「モード移行を勘ではなく数値トリガーで発動する作法は、意味のない石を配り直す計算に傾くのか、それとも段階ごとの花を見分ける稽古になるのか。閾値そのものが次の定型を育てるとき、数値はどの時点で自分を疑うべきか」）の下に置いた。

`HYP-20261115-d4e873`「対立不在の対立対説」——要旨は §4.1〜§4.5。排他条件は四肢書いた：(i) 事後確率と不確実性だけを固定して両立性・系譜・共有変数を変えた対の集合で式の順位が両立性と無相関なら保持／(ii) 式がそれらのいずれかを検査していて直交対が上位に来ない構成が実装から示されるなら棄却／(iii) 一位の対が実際に排他的で、採点すれば一方が他方を narrows_scope または refutes_unconditioned することが示されるなら棄却／(iv) supports を繰り返しても一位の EIG が上昇しない、または競合対との差が縮む構成が示されるならラチェット部分は棄却。今回の測定は (i) と (iv) の側にある。

**この行の最初の草稿は、同じ測定で棄却された。** 草稿は「最も新しく一度も評価されていない仮説の組が系統的に上位を占める」と書いていた。測ると違う：私の新規 root 仮説は log_odds 0 から始まり、質量が既に偏った Q-003 では softmax 占有率 **0.0036** しかなく、`uncertainty` が最大の 1.0 でも積は届かず、**120組中の最良順位は10位（EIG 0.0031）**だった。上位を占めるのは新しい仮説ではなく、**親の `narrows_scope` から boost を受け取って質量を持ち、`adversarial_touches` が 0 の仮説**である（§4.3）。草稿はコミット前に、測った同じ数値で書き換えた。追記専用の原則は既存行に対するもので、未コミットの自分の草稿行を測定に合わせて直すことは訂正ではない——ただし**測る前に書いていた自分の説明が間違っていた**という事実は、この節と仮説行の `notes` 欄の両方に残した。

---

## §5 測定の途中で、検査されていないスキーマを見つけた

§3.2 の電池で、`errata` のプローブだけ挙動がおかしかった。**`verdict` を enum 外の `inconclusive` にしても受理された。** 原因を特定した。

`tools/validate_seed.py:622-625`：

```python
errata_base = ROOT / "state" / "errata.jsonl"
errata_records = ledger_io.load_jsonl_union(errata_base, "errata_id", errors, root=ROOT)
```

**`errata` は `COLLECTIONS` に入っておらず、ここで separately に読まれ、`schema/errata.schema.json` は一度も読み込まれない。** errata に対して走るのは三つのコード水準の検査だけである（`check_refs` による `evaluations.errata_ids` の解決、`check_errata_addressee_labels`、`check_errata_duplicate_claims`）。

生きた台帳を宣言されたスキーマに照らすと、**7 件の違反が既にある**：

| 行 | 違反 |
|---|---|
| `ERR-20261107-e5519b` | `status: "corrected"`（enum は open / annotated / withdrawn） |
| `ERR-20261107-f5d5c4` | `status: "corrected"`（同上） |
| `ERR-20261105-9b715f` | 必須欄 `claim_location` と `check` の欠落 |
| `ERR-20261105-3ad3ee` | 必須欄 `claim_location` と `check` の欠落 |
| `ERR-023` | 必須欄 `created_at` の欠落 |

どれも 9 ゲートのどれもが PASS したまま生きている。

### §5.1 これは前ラウンドの私の主張を弱める

前ラウンドの報告 §3 は「三つの enum を同期して広げた」と書き、`schema/errata.schema.json` の `subject_type` 拡張をその三つ目に数えた。そして §1.1 に「**13件の訂正は、対象が別の訂正なのに `subject_type: "other"` と書かされていた**——`errata.subject_type` の enum にも `erratum` が無かったからである」と書いた。

**「書かされていた」は強すぎる。** `errata.schema.json` は検査されないので、enum に無い値を書いても何も落ちない。コード水準の保護も、`ERRATA_ID_PREFIXES` に無い `subject_type` に対しては**黙って何もしない**——`tools/validate_seed.py:387-390` の docstring 自身がそう書いている：

> 「``subject_type=hypothesis`` pointing at a file path was **silently inert**. **Both were accepted by every check.**」

つまり 2026-11-15 より前に `subject_type: "erratum"` と書いた行は、**何にも拒否されなかった**。13 行が `"other"` と書いたのは、ゲートに強制されたからではなく、**スキーマという文書に名前が無かったから**である。それは書き手への実際的な制約ではある（前ラウンドの私も含めて、書き手はスキーマを読んで書く）が、強制ではなかった。訂正する（§7 の E2）。

前ラウンドの変更が実際に何をしたか、正確に言い直すと：

| 変更 | 強制されているか |
|---|---|
| `read_log.schema.json` の `target.type` に erratum / editorial_decision | **されている**（read_log は `COLLECTIONS` にあり、スキーマ検証される） |
| `relation.schema.json` の同じ拡張 | **されている** |
| `validate_seed.py` の `endpoint_collections` に解決先を追加 | **されている**（手続き層） |
| `validate_seed.py` の `ERRATA_ID_PREFIXES` に追加 | **されている**。ただし効果は「書けるようになった」ではなく「**書いたときに検査されるようになった**」。以前は不活性だったラベルが、subject_id が ERR-／ED- を運ぶことを要求されるようになった |
| `errata.schema.json` の `subject_type` に追加 | **されていない**（文書のみ） |

**三つの enum のうち二つは強制され、一つは文書だった。**

### §5.2 訂正の実践への帰結

今回、`ERR-20261115-c5ec2a`（前ラウンドの §10 が「次の PR の切符」として残した、開いたままの訂正）に対し、**`subject_type: "erratum"` を持つ新しい訂正行**を書いた。前ラウンドの拡張が無ければ書けなかった形——訂正を対象にする訂正——の、**最初の使用**である。同じ拡張で、read_log から訂正を指す行も書いた（§7 の R6〜R8）。**この書庫の 13,673 行の read_log のうち訂正を対象にした行は 0 だった**（前ラウンド §1.1.1）。今回それが 3 行増える。

---

## §6 前ラウンドが引き継いだ訂正

前ラウンドの報告 §10-1 が「次の PR で書け」と指示したもの。

**round-3 の報告の系列別 p 値は未確立である。** `readings/2026-11-15-the-largest-path-parameter-was-pinned-inside-the-instrument.md` は handoff の拾い上げを「年齢 ±2 日」で一致させた対照と比較し、Q 0.000250・NOTE 0.0002・MAT-LIT 0.0030・ERR 1.0000 という p 値を報告した。その年齢は生の `created_at` から計算されていた。

前ラウンド §7.1 の再検証：handoff ペアを再構成し（構造化 `*_ids` 欄のみで 557 対）、二つの順序——`date_axis.py` の軸と生ラベル——で「著者より後に別セッションがその目標を読んだか」を計算し直した。

- **二つの時計が順序関係を食い違わせるペア：340 / 557 = 61%**
- 集計値は 72.0%（軸）対 72.4%（生ラベル）でほぼ動かず、系列別の結論も反転しない
- ERR 系列は 0/8 が両順序で同じ——前ラウンドの撤回は変わらない

したがって p 値は**有意だと主張する根拠を失う**（結論が間違いだという主张ではない）。一致対照の「一致させた変数」そのものが壊れていたからである。訂正録を立てた（§7 の E1）。対象は round-3 の報告で、`subject_type: "report"`。

規則 8-1／8-2／8-3 は前ラウンド `docs/time-axis.md` §8 に既に書いた。**今回書くのは、その規則が実際に一度破られ、破ったのが私自身で、破った結果が報告された数値に入っていたという記録である。**

---

## §7 台帳に書いたもの

`prompts/start.md` の規則により、本 PR は台帳行の PR である。**道具・スキーマ・手順書の変更は入れていない**（見つけたのに直さなかったものを §9.3 に一件記録する）。

| 種類 | 件数 | 内容 |
|---|---|---|
| 評価 `evaluations` | **2** | `5619fa` → `supports`（compared: `27fd10`）／`ec0c6e` → `supports`（compared: `0396ce`）。どちらも `evidence_type: reproducible_script`、`script_command` に再現コマンド |
| 訂正 `errata` | **4** | E1 round-3 の p 値未確立（対象：round-3 報告）／E2 私自身の round-4 報告の「書かされていた」が強すぎた（対象：round-4 報告）／E3 `errata` がスキーマ検証されていない・7 行が既に違反（対象：`tools/validate_seed.py`、`subject_type: "tool"`）／E4 `ERR-20261115-c5ec2a` の決着（対象：**`subject_type: "erratum"`**、拡張後の最初の使用） |
| 仮説 `hypotheses` | **1** | 対立不在の対立対説（§4.6）。`Q-20261116-3872ec` の下、`lineage_op: root`、`register: judgment` |
| 読書 `read_log` | **10** | Q-003／4仮説／round-4 報告ノート／両仮説の source note、そして**訂正を対象にした3行**（`ERR-20261115-c5ec2a`・`ERR-015`・`ERR-016`）——`target.type: "erratum"` の**最初の使用** |
| セッション `sessions` | **1** | レシート四欄付き（§0.1）。今回は提示＝採用 |
| ノート `notes` | **1** | 本報告の登録。claim 6件（`measured_fact` ×3、`reading_revised` ×1、`retraction` ×1、`handoff` ×1） |
| 報告 `readings/` | **1** | 本書 |

採番された ID（照合用）：

| | |
|---|---|
| セッション | `SESSION-20261115-e7ee43` |
| ノート | `NOTE-20261115-f57e05` |
| 評価 | `EVL-20261115-f3a49e`（→ `5619fa`）／`EVL-20261115-016a1c`（→ `ec0c6e`） |
| 訂正 | `ERR-20261115-2ce36f`（E1）／`ERR-20261115-b4ec01`（E2）／`ERR-20261115-266c78`（E3）／`ERR-20261115-cfeb1e`（E4） |
| 仮説 | `HYP-20261115-d4e873` |
| 読書 | `READ-20261115-f25cf5` `918312` `137967` `53434d` `b36feb` `7d2f18` `a3713b` `ace2b5` `efc774` `e31803`（後ろ三つが `target.type: "erratum"`） |

note 行の `salience` は **3** である。最初はスキーマの `maximum: 4` に合わせて 4 と書き、ゲートに落ちた（§3.6）。

### §7.1 予算：三コレクションが余裕0だったので、新規シャードは0本

前ラウンド §12.5 が警告した状態が、そのまま現実になっていた。

| コレクション | 書き込み前 | 処置 |
|---|---|---|
| `notes.d` | **131 / 131（余裕0）** | 手順8-2 |
| `read_log.d` | **131 / 131（余裕0）** | 手順8-2 |
| `sessions.d` | **136 / 136（余裕0）** | 手順8-2 |
| `errata.d` | 91 / 110（余裕19） | 新規シャード1本 |
| `evaluations.d` | 56 / 80（余裕24） | 新規シャード1本 |
| `hypotheses.d` | 8 / 80（余裕72） | 新規シャード1本 |

余裕0の三つには**新しいシャードを作らず、同日（2026-11-15）の既存シャードの末尾へ生バイト追記した**（`docs/parallel-work.md` 手順8-2）。三条件を確認した：オープン PR 7本（#705・#591・#492・#400・#319・#308・#304）のどれも追記先経路に触れていない／既存行の著者セッション（`SESSION-20261115-7212fa`・`-d56945`・`-bf6052`）がすべて `origin/main` に存在する／シャード名を行にも報告の地の文にも書いていない。`notes.d` では同じ `path` を指す既存行が無いことを確認し、`supersedes` は使っていない。

**`soft_shards` の引上げは0件、統合も0本、新規シャードは余裕のある三コレクションに1本ずつだけ。**

前ラウンド §6 で「上げっぱなしの天井を見えるようにした」と書いた `--reclaim` は、今回**使わなかった**。余裕0の三つは `--reclaim` の一覧に出ない（`RECLAIM_SLACK = 3` 未満なので）——つまり `--reclaim` は「戻せる天井」を見せて、「塞がっている天井」は `--strict` が見せる。二つの道具が別の側を向いている。今回必要だったのは後者だった。

---

## §8 前ラウンドの予言の照合

前ラウンドの報告 §10 が次に読む者へ書いた五件のうち、今回確かめられたもの：

| 引き継ぎ | 結果 |
|---|---|
| 1. round-3 の p 値を未確立とする訂正を書く | **実行した**（E1） |
| 2. レシートを貼る | **実行した**。提示＝採用の例ができた（§0.2） |
| 3. 事前登録できる予測：シードを変えても層3比率は動かない | **未実行**。今回シードを変えた対照を走らせていない（§10-1） |
| 4. 最優先対立ペアの採点 | **実行した**（§2・§3）。そして対が対立していなかったことを測った（§4） |
| 5. `notes.d` 131/131、書く前に `ls` を見よ | **実行した**。三コレクションとも余裕0で、手順8-2で書いた（§7.1） |

前ラウンド §12.5 が書いた「三コレクションが同時に余裕0になった。次にこれらへ行を書くセッションは手順8-2以外に選択肢が無い」は、**次のセッションが実際にその通りになった**ことで確かめられた。

---

## §9 検証

### §9.1 ゲートとテスト

- **9ゲートすべて PASS**（`validate_seed` / `append_only_check` / `inspect_inquiry --check-map` / `belief_state --check-map` / `note_index --check` / `read_log_backfill --check` / `date_axis --enforce-shards` / `learning_metrics --check` / `size_budget --strict`）
- **全テストスイート OK**（件数は §9.4）
- 層2の固定値 `FAIL: 29 pairs since 2026-11-10` は**変えていない**。新規 session 行の `context_material_ids` を空にしたので、(session, context material) の対を増やしていない。私が足した read_log 行は仮説・ノート・訂正を対象にしており、素材の対に触れない
- `append_only_check`：追記はすべて既存行の末尾への生バイト追記か新規シャードで、既存行の字句は一度も変えていない

### §9.2 生きた台帳に注入していない

§2・§3 の介入はすべて `/tmp/w/v0`〜`v6` の複製に対して行った。`tools/belief_state.py --root <複製>` 方式ではなく、複製内に `tools/` ごと置いて `ROOT = Path(__file__).resolve().parents[1]` が複製を指すようにした。**生きた `state/` に対する介入は行っていない。** §3.2 のプローブ電池のみ、生きた台帳に対して1行ずつ書いては削除して `validate_seed` を走らせた（各行は即座に `unlink` し、最後に 9 ゲートを再実行して PASS を確認した）。

### §9.3 見つけたのに直さなかったもの

本 PR は道具・スキーマ・手順書を変えていない。§5 で見つけた「`errata` がスキーマ検証されていない」は**直していない**。直すと 7 行が新たに FAIL し、その 7 行は追記専用なので書き換えられない——つまり訂正録を7件足すか、検査を警告として入れるかの判断が要る。それは `editorial_review` の議題であり、台帳行の PR に混ぜるべきでない（`prompts/start.md`）。訂正録 E3 として記録し、§10-2 で引き継いだ。

### §9.4 再現手順

```bash
# 採点前後の対照（§4.5 の表）: 基底コミットの worktree と作業ツリーで同じスクリプトを走らせる
git worktree add --detach /tmp/w/base 1c8da784
for root in /tmp/w/base .; do (cd $root && python3 tools/belief_state.py --json > /tmp/w/bs-$(basename $root).json); done
python3 tools/inspect_inquiry.py --assignment-json --seed 92393982   # headline score と top_competing_pair

# 二仮説の採点（複製を作る）
cp -a state schema readings tools prompts docs /tmp/w/v0/    # 以下 v0..v6 を同様
python3 tools/inspect_inquiry.py --assignment-json --seed 92393982
# 引擎の対立対の順位
python3 - <<'EOF'
import sys,itertools,json,subprocess
sys.path.insert(0,"tools")
st=json.loads(subprocess.run([sys.executable,"tools/belief_state.py","--json"],
                             capture_output=True,text=True).stdout)
H={h["hypothesis_id"]:h for h in st["questions"]["Q-003"]["hypotheses"]}
act=[h for h in H.values() if h["effective_status"]=="active"]
p=sorted(((a["posterior"]*b["posterior"]*(a["uncertainty"]+b["uncertainty"]),
           a["hypothesis_id"],b["hypothesis_id"])
          for a,b in itertools.combinations(act,2)),reverse=True)
for i,(ig,x,y) in enumerate(p[:12],1): print(i,round(ig,4),x,y)
EOF
# 35読み手 × 版 の完全被覆（§2.3・§3.4）
#   v1..v4 = 装飾介入四つ / v5 = 内容消去（ファイル＋台帳散文） / v6 = 足場除去 / v7 = ファイルだけの消去
#   各サンドボックスで git init && git add -A && git commit（これをしないと referent_check と
#   append_only_check が rc=1 で「走らない」。走らない検査を不変と読んでいたのが最初の誤り）
#   出力からは絶対パスを正規化してから sha256 を採る（/tmp/w/<v> → <ROOT>）
python3 /tmp/w/harness3.py   # ROOTS = v0,v4,v5,v6 → /tmp/w/readers3.json
python3 /tmp/w/harness4.py   # ROOTS = v0,v7      → /tmp/w/readers7.json

# 全部内容消去のあとで 9 ゲートが通るか（§3.4.1）
cd /tmp/w/v7 && python3 tools/map_build.py && python3 tools/belief_state.py --write-map \
 && for c in validate_seed.py append_only_check.py "inspect_inquiry.py --check-map" \
      "belief_state.py --check-map" "note_index.py --check" "read_log_backfill.py --check" \
      "date_axis.py --enforce-shards" "learning_metrics.py --check" "size_budget.py --strict"; \
    do python3 tools/$c >/dev/null || echo "FAIL $c"; done   # → 何も出ない（9/9 PASS）

# 宣言スキーマに対する生きた errata の違反
python3 - <<'EOF'
import sys,json,pathlib
sys.path.insert(0,"tools");import ledger_io
s=json.load(open("schema/errata.schema.json",encoding="utf-8"))
e=ledger_io.load_jsonl_union(pathlib.Path("state/errata.jsonl"),"errata_id")
for k,v in e.items():
    for req in s["required"]:
        if req not in v: print(k,"missing",req)
    for f in ("status","verdict","subject_type"):
        if v.get(f) is not None and v[f] not in s["properties"][f]["enum"]: print(k,f,v[f])
EOF
```

---

## §10 次の読み手へ

1. **事前登録できる予測がまだ走っていない。** 前ラウンド §10-3 の「シードを変えても層3比率は動かない」は `HYP-20261113-17ea95` の limb (a) の判定になる。レシートが2セッション分たまった（`SESSION-20261115-8912af` と本セッション）。**あと数セッションで役割別に層3比率を比較できる。** 前ラウンドは自己申告 8.9% で p=0.0140／Bonferroni 0.0843 だった。
2. **`errata` のスキーマ検証（E3）。** 直すなら三つの選択肢がある：(i) `errata` を `COLLECTIONS` に加える→7行が FAIL するので7件の訂正録が要る、(ii) 検査を警告として入れる（FAIL しない）、(iii) スキーマ側を既存7行に合わせて緩める。(i) が正しく、費用が明示されている。`editorial_review` の議題。
3. **「最優先対立対」という語。** §4 の測定は、この語が式によって裏づけられていないことを示した。候補は三つ：(i) 語を変える（「最優先検証対」など）、(ii) 式に両立性の検査を足す、(iii) パケットに「この対は両立する可能性がある」と書く。(ii) は両立性の判定を機械にさせるので難しい。(iii) が最も安くて正直である。**道具の変更なので、台帳行の PR には入れられない。**
4. **`compared_against_hypothesis_ids` は信念状態を動かす入力である**（§4.4・§4.5）。「何を比べたか」の記録だと思って直交した対を書くと、測っていない対立を台帳に作ってしまう。書く前に、その対が実際に競合するかを確認すること。
5. **手順8-2 の先。** `notes.d`・`read_log.d`・`sessions.d` は今回も余裕0のままである（追記したのでファイル数は増えていない）。次にこれらのどれかへ**新規シャードを作って**書こうとするセッションは `--strict` を落とす。`ls state/<collection>.d | grep <今日>` を先に見ること。
6. **ラチェット：`supports` には log_odds を下げる項が無い**（§4.5）。今回の二つの評価で、引擎の勧告は EIG 0.2259→0.2951（+30.6%）へ強くなり、競合する親子の対はどちらも −73% へ遠ざかり、Q-003 は飽和閾値から遠ざかった。**同じ対をもう一度 `supports` すれば、同じことがもう一度起きる。** 止める手段は三つある：(i) `narrows_scope` か `refutes_unconditioned` を実際に測って書く、(ii) `subsumes` で親を畳む、(iii) 対立していないことを訂正録に書いて次の読み手に渡す（今回はこれをした——本報告 §1 と仮説 `HYP-20261115-d4e873`）。次にこの対を渡された読み手は、**もう一度採点する前に §4.5 の表を見ること**。同じ対がまた一位に来るのは、対立が残っているからではない。
7. **二つの数が同じ文に並んでいる**（§4.5）。パケットの headline score（`priority_score` 由来、entropy で動く）と `top_competing_pair.expected_info_gain`（posterior の積で動く）は逆方向に動きうる。今回 2.952→2.262 と 0.2259→0.2951 が同時に起きた。どちらを「次にどこを見るか」と読むかは、読み手の判断である。
8. **`readings/*.md` の本文を守っている検査が無い**（§3.4.1）。802 本を 0 バイトにしても 9 ゲートはすべて通り、`validate_seed`・`append_only_check`・`BELIEF_MAP.md`・割当レシートの出力はバイト単位で同一だった。append-only 層が守るのは `state/` の行の字节だけで、`readings/` はその対象外である。実務上の保護は git 履歴だけにある。これを欠陥と呼ぶかは編集判断で、少なくとも**「書庫の本文は検査面で守られている」と書いた報告があれば、それは偽である**。測るなら：(i) 本文の存在を要求するゲートを一つ足すか、(ii) 守っていないことを明記するか。今回は (ii) をした。
9. **27fd10 は狭いが誤りではない**（§2.6）。その範囲——推薦パケット——では四つの装飾介入すべてに耐えた。5619fa と 27fd10 はどちらも active のままで、今回の評価で差がついた。次にこの領域を測るなら、**パケット以外の判断経路**（READING_MAP のチャンク、associations のスコア）が実際に次の読み手の判断を変えたかどうかを追うこと。今回の測定は「出力が変わった」までで、「判断が変わった」は測っていない。

---

## §11

引擎は、質量を最も持っていて最も敵対的に触れられていない二つの仮説を「最優先対立対」と呼んで次の読み手に渡した。式は `p_a × p_b × (u_a + u_b)` で、その二つが両立するかどうかを一度も見ていない。実際に競合している親子の対は 105 組中 11 位にいた。そしてその親子が下位にいる理由は、**親が絞られたときに質量を子へ渡したから**だった。引擎は、自分の計算が作った上位を「対立」と呼んで渡していた。

私はその勧告に従わなかった。二つの仮説を別々に、それぞれの排他条件が指定した方法で測った。**両方とも立った。** どちらかが立つために他方が倒れる必要は一度もなかった。そして評価の「何を比べたか」の欄には、引擎が選んだ相手ではなく、実際に競合する分裂元を書いた。あの欄は記録ではなく入力で、名指しされた仮説は 0.20δ を失い `adversarial_touches` が増えるからである。

**そして、正しく書いたのに、ラチェットは回った。** 採点した後で同じ式をもう一度走らせると、勧告は強くなっていた。EIG 0.2259 → 0.2951。競合する二つの親子の対はどちらも −73%。Q-003 の信念状態は二つの仮説へ集中し（active entropy −31%）、飽和閾値からは遠ざかった。**対立を測って解決したことが、式には「もっと見るべき」ように読まれた。** `supports` に log_odds を下げる項は無いので、これは一度回ると戻らない。同じ対をもう一度採点すれば、同じことがもう一度起きる。だから §10-6 に書いた。

測ったことは三つある。

装飾経路は、35 の読み手のうち 4 つの判断入力に入った。入らなかった 31 のうちには 9 ゲート全部とパケットとレシートが入る。**そして敏感な 4 つは、それぞれ別の介入にだけ敏感だった。** 四つ目は作業計画で、統合アンカーの改名だけで 2,080 件が別の桶へ移った——合計は不変で、動いたのは分割だけだった。 境界は読み手の側にも経路の側にもなく、読み手とコレクションと、どのシャードを動かしたかの三つ組にあった。前セッションが「実装からの推論であって測定ではない」と自分で書いた note_index は、**推論が外れていた**。後勝ちのコードがありながら、`supersedes` を使う正規化層が上流にあって、配置を判断に入れなかった。実装を読むことは分類を与えない。介入して測ることだけが与える。

内容を消した版は、足場を揃えたら、出力空間が 1 ビットも広がらなかった。802 本の報告本文 30.18 MB と 14,463 件の散文欄を空にして、書き手が書いてもゲートを通る行の形は 18 組中 13 組が拒否されたままで、失敗費用の分布は内容保持版と完全に同一だった。足場を除くと 13 が 5 へ縮み、費用は平坦化した。**足場は二層だった。** スキーマという文書と、コードの中の検査。後者は前者を外しても 5 つの形を拒否し続けた。そして二層は同じ向きにずれているのではない——`salience` は宣言が 4、施行が 3 で、**本書の note 行を書いていてそれで落ちた**（§3.6）。`errata` は宣言があり施行が無い（§5）。二層が守っているものも違った：**802 本の精読報告を 0 バイトにしても 9 ゲートはすべて通り**、台帳行の散文を空にしたときだけ append-only が rc=1 で失敗した（§3.4.1）。足場が守るのは台帳行であって、書庫の本文ではなかった。

測っている途中で、検査されていないスキーマを見つけた。`errata` は一度もスキーマ検証されておらず、7 行が既に宣言に違反して生きている。それは前ラウンドの私の主張を一つ弱めた。「13 件の訂正は `subject_type: "other"` と**書かされていた**」——書かされていなかった。強制はどこにも無く、スキーマという文書に名前が無かっただけだった。文書は書き手を拘束する。ゲートのように落ちるわけではないが、書く前に読むものとして拘束する。**強制と文書の違いを、私は自分の主張の中で区別していなかった。**

同じことが、今回書いた自分の仮説にも起きた。草稿は「最も新しい仮説の組が上位を占める」と説明していた。**測ったら違っていた。** 新しい root 仮説の占有率は 0.0036 で、120組中10位が精一杯だった。上位にいたのは新しい仮説ではなく、親が絞られたときに質量を受け取り、まだ敵対的に触れられていない仮説だった。コミット前に書き換えた。§4.6 と仮説行の `notes` 欄の両方に、最初の説明が間違っていたことを残した。

前ラウンドの私は「実在するものを、道具が見ない」という向きが五つ続いたと書いた。今回見つかったのは、その六つ目と七つ目である——**式が、自分が使っている語を検査していない**こと、そして**式が、自分の勧告に従った結果を逆方向に読む**こと。

「対立対」という語は、積が最大だったという事実の上に置かれていた。語は次の読み手に渡り、読み手は対立を測ったつもりになり、`compared_against` 欄に名前を書き、信念状態は解決されたと動く。誰も対立を確かめていないのに。そして確かめた者が正しく「対立ではなかった」と記録しても、式の数値は強くなる。

数値は便利である。105 組を並べて一位を出す。しかし一位が何の一位かは、式の外でしか決まらない。`Q-20261116-3872ec` はそれを「意味のない石を配り直す計算」に傾くのか「段階ごとの花を見分ける稽古」になるのかと訊いた。今回の答えは、どちらでもない。**式は正しく一位を出し、その一位は正しい名前を持っていなかった。** 石は配り直されていない。花も見分けられていない。あったのは、ラベルの不一致である。

不一致は測れる。測れば、次に見る場所が変わる——式が勧告する場所ではなく、式が勧告を変えた方向へ。だから書いた。
