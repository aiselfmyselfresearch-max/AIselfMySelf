# 証拠会計の変更（②③④の実装と①の着手）— 2026-11-20

この文書は、`readings/2026-11-20-cognitive-science-replication-and-the-archive.md` §3 の一文

> `partially_verified` は「読んだ」の記録ではなく、**「読まなかった」の記録**でもある。
> 判断の61.9%がその状態の素材に支えられているという事実は、誠実さの証明ではなく、
> **証拠の検出力の低さ**の測定値である。

に対して、運用上の改善を4つ実装した記録である。実装順は ②→③→④→①（ユーザー指示）。

測定はすべて台帳から再計算できる。使ったコマンドは各節に書く。

---

## ② 支持照合率による割引 — `P_gate` の係数

**何を変えたか。** `supports` 評価行の重みを、その行が引用した素材のうち `verification.status == "verified"`
である割合 `r` で割り引く。

```
factor = SUPPORT_DEPTH_FLOOR + (1 - SUPPORT_DEPTH_FLOOR) * r      # floor = 0.5
```

* 素材を1件も引用しない行（命題監査・再現スクリプト）は `r` が定義されないので**割り引かない**。
  「本文を読んでいない」と「本文について語っていない」は別だから。
* 効果は `P_gate` のみ。歴史的事後確率 `P_t` は動かさない（既存の `P_sep` / `P_lin` と同じ扱い）。

**実装。** `tools/belief_state.py` の `support_verified_ratio()` と `delta` の1行。閾値の実測は
`python3 tools/verification_targets.py`（未照合の支持行 158/356）。

**効き方（2026-11-20 時点、`SUPPORT_DEPTH_FLOOR` を 1.0 に戻した対照との比較）。**

| 問い | 仮説 | 割引なし | 割引あり | Δ |
| :--- | :--- | ---: | ---: | ---: |
| Q-003 | `HYP-20261117-4bf2dc` | 99.2% | 78.4% | −20.8pp |
| Q-001 | `HYP-20261119-8b3e04` | 61.8% | 50.9% | −10.9pp |
| Q-002 | `HYP-20261119-8b3e04` | 49.1% | 39.9% | −9.1pp |
| Q-003 | `HYP-20261119-8b3e04` | 0.4% | 8.8% | +8.5pp |

51仮説が動いた。Q-003 の首位が20.8ポイント下がったのは、その支持が未照合素材に載っていたからで、
これは「確信が読書の深さに依存していた」ことの直接の測定値である。

---

## ③ 検証深度の分離 — `verification.depth`

**何を変えたか。** `verification` に `depth` を足した。

| 値 | 意味 |
| :--- | :--- |
| `metadata` | 書誌だけ |
| `abstract` | 抄録・Summary |
| `results` | 結果表・主要図 |
| `full_text` | 引用した一節を論文本文で読んだ |
| `re_derived` | 報告された数値から再計算した |

* `schema/material.schema.json` に追加（既存行は無変更、`additionalProperties: false` は維持）。
* `schema/editorial_decision.schema.json` に `verification_depth` を追加し、
  `tools/ledger_io.py` が material の `verification.depth` へ適用する（shard は書き換えない）。
* 検証器（`validate_seed.py`）は次の2つを強制する:
  - `depth` が `metadata` / `abstract` なのに `status == verified` は**矛盾**（本文を読まずに verified は名乗れない）。
  - `depth` が `full_text` / `re_derived` なら `status` は `verified`（または `corrected`）。
  - `2026-11-21` 以降に照合した行は `depth` 必須。

**正直な残高。** `python3 tools/validate_seed.py` の助言行:

```
INFO: verification.depth (advisory): 2 material(s) carry a depth; 1414 legacy `verified` row(s) predate the field
```

つまり既存の 1,414 件の `verified` は「照合はあった」としか言っていない。本文を読んだのか抄録だけかは、
この変更以前の行からは**復元できない**。復元できるのは、これから書く行だけである。

---

## ④ 数値の三経路と、独立二読

### ④-a 数値は「再計算・照合済み素材・理由」のどれかを持つ

`evaluations.no_recompute_reason` と `notes.claims[].recomputer` を追加し、`2026-11-21` 以降の行で
数値を含む主張がどの経路も持たない場合を**エラー**にした。

```
python3 tools/validate_seed.py
INFO: number traceability (advisory): 0 numeric row(s) from 2026-11-21 on are gated by script/material/reason;
      1211 legacy numeric rows are ungated and remain un-recomputed history
```

この規則は、この文書を書いている最中に**自分の誤りを1つ捕まえた**。前の応答で
「上位50件の照合で支持行の約6割が verified を持つ」と書いたが、これは複数素材が支える行を
二重に数えた値だった。行を一度だけ数えると、50件で **31%**、100件で **51%** である
（`python3 tools/verification_targets.py`）。数値を書いた本人が再計算しないと、その数値は記憶になる。

### ④-b 二読の食い違いを測る — `tools/double_reading.py`

Arena ではモデルの割当を選べない。だから「同じ素材を別セッションが読む」ことだけが
モデル間分散への手がかりになる。

```
python3 tools/double_reading.py
- 手読みのある素材: 4,620
- うち 2 セッション以上が読んだ素材: 1,169 (25.3%)
- セッション対: 2,594 / 読みの種類が食い違う対: 1,832 (70.6%)
- 方向転換の対（interpreted → reinterpreted/contested）: 704 / 該当素材 441
```

70.6% という数字は**上限**である（二人が同じ `interpreted` と書いても内容が同じとは限らない）。
それでも、二読の4分の3が同じ語を選ばないという事実は、「一度読んだ素材の読みを台帳は保存している」
という前提を弱める。保存されているのは読み**行為**の分類であって、読み**内容**ではない。

---

## ① 照合予算の付け替え — 着手

**何を変えたか。** `tools/verification_targets.py` を追加し、「未照合の支持行を最も多く解く素材」を
貪欲法で並べる買い物リストを作った。新規資料の追加ではなく、既存の判断の下敷きを固めるための予算配分である。

| 照合する素材数 | 解き放たれる支持行 | 割合 |
| ---: | ---: | ---: |
| 5 | 10 | 6% |
| 10 | 16 | 10% |
| 20 | 32 | 20% |
| 50 | 49 | 31% |
| 100 | 80 | 51% |

**コストの再見積り。** 上位は書籍（Oyama 1985、Kanerva 1988、Pradeu 2012）と有料誌が多く、
`fetch_page` で本文に到達できない。実際に開けたのは上位20件のうち2件だけだった。
したがって「50件で3割」は**アクセス可能な資料に限ればさらに高くつく**。①は1セッションで終わる作業ではなく、
資料アクセスを含めた複数セッションの計画として扱うべきである。

**このセッションで行った照合（2件、いずれも到達深度つき）。**

| 素材 | 到達深度 | 何を確認したか | 状態 |
| :--- | :--- | :--- | :--- |
| `MAT-20261113-fb2212` | `abstract` | PMC7617458 の Summary と Introduction の引用句を逐語一致 | `partially_verified` のまま |
| `MAT-20261118-7c9eb5` | `abstract` | J Neurosci 36(30):7829 の Abstract と Significance statement を逐語一致 | `partially_verified` のまま |

2件とも **`verified` に上げていない**。読んだのは抄録までだからである。③を入れた直後に
「読んだ分量より深い状態を名乗らない」を自分に適用した最初の例が、この2行になる。

---

## 残っていること

* 1,414 件の legacy `verified` に深度を与えること（本文の再訪が必要。安くはない）。
* 1,211 件の legacy 数値主張の再計算（うち何件が今も同一の値を出すかは未測定）。
* ①のキュー上位50件のうち、アクセス可能な資料からの照合（本セッションは2件）。
* 二読の**内容**一致を測る手段。現状の `read_log.reading` は行為の分類でしかない。
