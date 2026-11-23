# 実装報告 2026-11-23 ——案3・案1・案2 を実装し、案2 を測って棄却した

- セッション: `SESSION-20261123-9fd9b67b`
- ブランチ: `arena/9fd9b67b-aiselfmyself`（基点 `0ef5ef0d`）
- 受領証: `dispersal_seed 9fd9b67b` / `adversarial_tester` / 提示問 `Q-049` / `editorial_review`
- 詳細: [`readings/2026-11-23-the-allocation-reads-the-question-not-the-leftovers.md`](readings/2026-11-23-the-allocation-reads-the-question-not-the-leftovers.md)

---

## 0. 一行で

**案3 と案1 と案4 は入り、案2 は入らなかった。** 案2（正規化）は実装して測った
ところ、直そうとしていた「登録数が順位を決める」を**向きを変えて再生産した**——
上限 `log2(n)` で割ると、2 仮説の周辺問（0.909）が 26 生存仮説の中心問（0.290）を
上回る。既定は生ビットに切り替え、正規化は切替基底として残した。

---

## 1. 何が変わったか

| | 変更前 | 変更後 |
|---|---|---|
| 数える状態 | `active` のみ | `active` + `narrowed` |
| 優先度の第一項 | `active_entropy`（生ビット） | `live_entropy`（生ビット、既定） |
| 正規化 | なし | `scoped_norm` 基底として選択可（既定ではない） |
| `H = 0` の意味 | 決着 | 決着**または**質量が集合の外（`readable` で区別） |
| 仮説0件の問い | 固定床 0.40 で順位付け | 順位付けから除外、提題者枠 0.20 |
| 248 シードの行き先 | `Q-20261024-6bdafd` 248/248 | `Q-001` 248/248 |

---

## 2. 測定（前後）

```
問い                      仮説n  active  生存  H(active)  H(生存)   質量   可読
Q-001                       31     20    27     0.658     1.364   63.48%   可
Q-002                       49     31    44    -0.000     0.010    0.05%  ⚠️不可
Q-003                       65     45    61    -0.000     0.010    0.05%  ⚠️不可
Q-20261024-6bdafd            2      2     2     0.909     0.909  100.00%   可
```

- **案1 の効果**: 中心問いの未解決量が 0.658 → 1.364 bit。27 件の生存仮説が実際に
  競っており、その 7 件ぶんは `active` の外側にあった。
- **案2 の棄却**: `Q-001` は 1.364 / 上限 4.700 = **0.290**、`Q-20261024-6bdafd` は
  0.909 / 上限 1.000 = **0.909**。0.455 bit 多く未解決を抱える側が、比では負ける。
- **案3 の効果**: 6 問中 2 問（`Q-002`/`Q-003`）が「読めない」と判定された。
  9 エラのあいだ、この 2 問の `H = 0.000 bits` は決着と区別できなかった。
- **案4**: 本日の断面では仮説0件の問いが割当候補に 0 件なので、まだ何も決めて
  いない。決めるのは空問いが再び候補に現れたときである。

### 2.1 基底ごとの首位（248 分散シード）

| 基底 | 首位 | 分布 |
|---|---|---|
| `scoped`（生ビット、**新既定**） | `Q-001` | 248 / 248 |
| `scoped_norm`（案2） | `Q-20261024-6bdafd` | 248 / 248 |
| `historical`（旧既定） | `Q-20261024-6bdafd` | 248 / 248 |

`historical` が旧首位を 1 件も違えず返すことが、**過去の数字を書き換えていない**
ことの証拠である。

---

## 3. 実装

`tools/belief_state.py`

- `LIVE_EFFECTIVE_STATUSES = ("active", "narrowed")`
- `UNREADABLE_MASS_SHARE_FLOOR = 0.50` / `SCOPE_INCLUSIVE_MIN_MASS_SHARE = 0.01`
- `PROPOSER_BOOTSTRAP_PRIORITY = 0.20`
- `ALLOCATION_BASES = ("scoped", "scoped_norm", "historical")`、既定 `scoped`
- 各問いに `live_entropy_bits` / `live_entropy_normalized` / `live_count` /
  `live_mass_share` / `readable` / `priority_scoped` / `priority_scoped_normalized`
  を追加。`active_entropy_bits` と `priority_score` は**そのまま**
- `--allocation-audit`（書き込みなし）: 可読性の判定と基底ごとの首位
- `BELIEF_MAP.md` 主表に「生存エントロピー」「数えた集合の質量」列と ⚠️

`tools/inspect_inquiry.py`

- 25% 分散枠のプールに関するコメントを実測に合わせて訂正（挙動は変えていない）

`tests/test_allocation_basis.py`（新規 17 件）

- 状態の固定、不変条件、前後表、基底掃引、`scoped_norm` の棄却、案4 の枠

---

## 4. 変えなかったもの（明示）

- `test_measurement_knobs.py::test_default_still_pays_a_post_dated_child` — 時間的
  継承の既定は意図的な固定なので触っていない
- `test_pair_honesty.py::HypothesisLessPriorityTests` の source-string 固定 —
  `"priority_score": HYPOTHESIS_LESS_CORE_PRIORITY` と
  `score = HYPOTHESIS_LESS_CORE_PRIORITY + jitter` は原文のまま存在する
- `HYPOTHESIS_LESS_CORE_PRIORITY = 2.50`、および仮説0件の中核問いの公開
  `priority_score`
- 案5・案6・案7 は未実装（指示範囲外）

既存テスト 3 件は契約が変わったため更新した（理由はその場にコメント）。いずれも
「旧既定の固定」ではなく「判別の保存」を目的としていた箇所である。

---

## 5. 検証

| ゲート | 結果 |
|---|---|
| `validate_seed.py` | PASS（問い 439 / 仮説 96 / 評価 881 / セッション 1127） |
| `append_only_check.py` | PASS（35,178 行 byte 一致） |
| `belief_state.py --check-map` | PASS（326,403 B） |
| `inspect_inquiry.py --check-map` | PASS |
| `self_model.py --check` | PASS |
| `note_index.py --check` | PASS（1,176 notes） |
| `read_log_backfill.py --check` | PASS |
| `date_axis.py --enforce-shards` | PASS（0 件） |
| `learning_metrics.py --check` | PASS |
| `three_gates.py --check` | PASS |
| `size_budget.py --strict` | PASS |
| `unittest discover -s tests` | **1,170 件 OK** |

---

## 6. 台帳

- `HYP-20261123-035338` — 生ビット基底説（`cc92df` の子）
- `EVL-20261123-4af349` — `cc92df` を `narrows_scope`（反証条件 (a) は満たされず、
  処方の第二項のみ誤り）
- `NOTE-20261123-a612ad` — 本報告の読書ノート（6 主張）
- `SESSION-20261123-9fd9b67b` — 本セッション

---

## 7. 次に読む人へ

次のセッションは `Q-001` へ行く。そこには 27 件の生存仮説と 1.364 bit の未解決が
あり、最優先検証対は `HYP-20261120-58ddce` vs `HYP-20261119-30d3f5`。

`Q-002`/`Q-003` は**依然として読めない**。質量 99.92% が `HYP-20261121-6e3e15`
（5 回の射程限定、支持 0 回）にあり、本日の変更はこれを「読めない」と表示する
ようにしただけで、再評価はしていない。`temporal_heir_guard` 基底では同仮説の
質量が 99.870% に戻り H が 1.148 bit になる——**この 1 件を数えるかどうかが、
この 2 問いの可読性そのもの**である。それは本日の射程の外に置いた。

棄却条件 (c)（`Q-001` に行ったセッションが EVL を 1 件も残さないなら、基底の
変更は行き先を変えただけ）は、次のセッションの観測を要する。
