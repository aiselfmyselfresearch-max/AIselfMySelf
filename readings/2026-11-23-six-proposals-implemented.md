# 提案6件の実装 — 表示の圧縮、質量0の非推薦、家系の集中度、一次所属問い、基底の記録、登録1件の希釈

- **実作業日（UTC）**: `2026-11-23`
- **セッション**: `SESSION-20261123-9cfe80`
- **来歴**: 利用者の指示「ご提案の全てを採用します。順番に実装してください。」への応答。前報告 `readings/2026-11-23-coarsening-concentrates-and-what-the-harness-should-change.md` §6 の 6 提案を、その優先順位（2 → 5 → 3+4 → 1 → 6）のまま実装した
- **基盤**: `main` @ `dd625f8c`（PR #1061 マージ後）
- **種別**: 実装（コード・スキーマ・手順書の変更）＋その検証
- **対応ノート**: `NOTE-20261123-b16def`
- **台帳への追加**: 新規仮説 0 件・新規問い 0 件・断片 0 件・資料 0 件・関係 0 件

---

## §0 レジスタの宣言

**実装レジスタ**（§2–§6：何を、どの順で、どこに入れたか）、**検証レジスタ**（§7：門とテストの実測値）、**限界レジスタ**（§8：実装しなかったこと・実装した結果わかったこと）を分離する。`CONTENT_POLICY.md` に従い、AI の現象的意識の有無は肯定も否定もしない。

前報告は「実装しない提案」だった。本報告は「実装した結果」であり、**数値が動いた箇所と動かなかった箇所を分けて書く**。事後確率は 1 件も動いていない（§7-3 で確認）。

---

## §1 何を変え、何を変えなかったか（一行で）

| 提案 | 変えたもの | 変えなかったもの |
|---|---|---|
| **2** 描画圧縮 | `BELIEF_MAP.md` の詳細ブロック（全件 → 上位12件＋警告付き、残りは1行）と `--full` 経路 | 事後確率、台帳の行、評価、表の列の意味 |
| **5** 質量0の非推薦 | 合算 1% 未満の対を「推薦」と呼ばないこと、`ratchet_warning` の新設、`no_recommendation` の記録 | `expected_info_gain` の値、`unsaturated_supports_ratchet` の算術、飽和の定義 |
| **3** 家系の質量行 | 家系表（家系質量＋**家系内集中度**を必ず併記）と `--json` の `families` | 問いごとの softmax（家系は質量の単位になっていない） |
| **4** 一次所属問い | `schema/hypothesis.schema.json` に `primary_question_id`（任意）、表に「一次所属」列 | 既存 93 行。**1 件も遡及で埋めていない** |
| **1** 基底の記録 | `schema/session.schema.json` に `belief_basis`（任意）、`BELIEF_MAP.md` 冒頭に使用基底 | 既存セッション行（1 件も埋めていない） |
| **6** newborn_mass | `python3 tools/belief_state.py --newborn-mass`（書き込みなし） | 登録を抑止する規則（作っていない。§8-3） |

---

## §2 提案2 — 詳細ブロックの圧縮（最初に実装した理由）

**測定量（実装前、`main` @ `dd625f8c`）**: 詳細ブロックが 852 行・434,420 B ＝ ファイルの 80.6%。仮説 93 件のうち 88 件が P<1%。ファイルは仮説登録のたびに再生成されるので、この塊が予算の構造的な半分だった。

**規則**（`tools/belief_state.py`）:

- `DETAIL_TOP_N = 12`。事後確率の上位 12 件、**および**警告を持つ全件（`errata_flags`・`low_witness_high_mass`・`self_evaluated_only`・PSC 未照合のみ・想起抑制）は全文を出す。
- 残りは 1 行: `ID [状態 / P / u] タイトル ｜ 評価数（反証系）｜ 支持m・反証n資料・出典kノート`。
- `--write-map --full` は全件詳細を**追跡ファイルに**書く。既定の再実行で圧縮版に戻る。
- `map/belief_state_full.md` は**常に**全件詳細を書く（未追跡）。圧縮で消えた散文の置き場所を先に用意しないまま圧縮すると、散文は台帳にしか残らなくなる。

**実装後**: `BELIEF_MAP.md` は **538,821 B → 322,982 B**（−40.0%）。行数 1,249 → 846。

**ここで一つ設計を変えた。** 当初は「上位 N 件」だけで切る予定だったが、それだと**反証条件を持つ警告付きの低質量仮説が既定で見えなくなる**。前報告 §6 の「危険」欄に自分で書いた点なので、選択関数を `detail_selection()` として分離し、警告付きを無条件に含めた。テスト `test_a_warned_hypothesis_is_never_compressed_away` がこれを固定している。

**予算上限は下げていない。** 圧縮は表示方針であって、`--full` を求めるセッションは正当に余白を必要とする。`tools/size_budget.py` の `BELIEF_MAP.md` の注記にこの判断を書いた。上限を下げると `--full` が自分の門で落ちる。

---

## §3 提案5 — 質量0の対を推薦しない

**測定量（実装前）**: Q-002・Q-003 の両方で `pair_mass_sum=0.0000` の対が「最優先検証ターゲット」として印字され、しかも `unsaturated_supports_ratchet=True`（＝未飽和）が立っていた。首位が 99.99% を保持している問いで、**質量のない対を「未飽和」と呼び、同点を辞書順で選んで推薦していた**。

**規則**:

- `PAIR_RECOMMENDATION_MASS_FLOOR = 0.01`（合算 1%）。`UNSATURATED_PAIR_MASS_THRESHOLD`（0.90）の 1/90 で、エンジンが印字する最小の非零事後確率 0.1% の 10 倍。
- `pair_is_recommendable(pair)` — `None` は「欄のない古い記録」で、従来どおり描画する。
- `pair_shows_ratchet_warning(pair)` — **警告だけ**を床で止める。`unsaturated_supports_ratchet` の算術は変えていない。質量 0 の対には流入がありえないので、「未飽和」はその対についての判定ではない。
- 床未満のとき、描画は `推薦なし（質量0の対）` と書き、**質量の保持者を名指し**する（`HYP-20261121-6e3e15` が 99.99%）。
- `saturation_snapshot` に `no_recommendation` と `pair_mass_sum` を足した。**`saturated` の意味は変えていない** — EIG=0.0000 は「選択を止めた」の最も強い肯定であり、ここを黙って付け替えると、この指標を引用した過去の報告が読めなくなる。足したのは**理由**である。

**実装後の実測**:

```text
Q-001  saturated=False  no_recommendation=False  pair_mass_sum=0.7937
Q-002  saturated=False  no_recommendation=True   pair_mass_sum=0.0
Q-003  saturated=True   no_recommendation=True   pair_mass_sum=0.0
```

Q-002 は EIG=0.0000 で飽和判定の閾値（0.02）を下回るが、`saturated` の意味を変えなかったので `True` のままである。Q-002 と Q-003 が同じ「EIG=0」で違う `saturated` を返すのは奇妙に見えるが、**それは元の定義の帰結であって今回の変更の帰結ではない**。この不一致自体を §8-2 に残す。

**受領書（`--assignment-json`）も変えた。** 合算 0% の対を「最優先検証対」と書く代わりに、`推薦なし（合算0.00% < 1%）` と書き、質量の保持者を名指しする。EIG の値は消していない（最大値であることは事実であり、隠すと算術が見えなくなる）。

---

## §4 提案3＋4 — 家系の質量行と、一次所属問い

両方を同じ回に入れた。前報告 §7 の条件 (b)(c)、すなわち「集中度を必ず併記」「一次所属を先に決める」が**同時に満たされる必要がある**ためで、片方だけ入れると家系質量の誤読を増幅する。

### §4.1 家系（root ancestor）

`root_ancestor_ids()` は `parent_hypothesis_ids[0]` を再帰的にたどる（前報告の測定と同一の定義。`synthesizes` の複数親では先頭の親）。循環と欠損親はその仮説自身に解決する。

`question_families()` は問いごとに家系をまとめ、**質量と集中度を同じ dict で返す**:

```
root_hypothesis_id, member_count, mass, mass_share,
top_hypothesis_id, top_hypothesis_mass, top_share_within_family, generations
```

`top_share_within_family` を別関数にしていないのは意図的である。**質量だけを取れて集中度を取れない API にすると、前報告 §4 の誤読がそのまま再現する。**

`BELIEF_MAP.md` に「系譜の家系（root ancestor）と一次所属問い」節を追加し、各問いの上位 6 家系を表にした。表の第 1 列を家系 ID、第 2 列を問いにしたのは、`tools/self_model.py` が `| \`Q-00` で始まる行を要約表として読むためである（第 1 列を問いにすると家系行が要約行として解析され、実際の要約行を上書きする）。実際に一度この順で書いて `self_model` の読み取りが壊れることを確認し、列を入れ替えた。

**実装後の実測（Q-001、7 家系）**:

| 家系 | 成員 | 家系質量 | 家系内集中度 |
|---|---:|---:|---:|
| `HYP-20261112-5a26aa` | 4 | 45.6% | **100.0%** |
| `HYP-20261112-b24785` | 6 | 33.8% | **99.8%** |
| `HYP-20261112-dc25dc` | 14 | 20.6% | **91.6%** |

Q-003 は 19 家系で、最大の家系 `HYP-20261112-1273f1` が 24 成員・100.0%・集中度 **100.0%**。**件数の多い家系が質量を持つとは限らない**という前報告 §4 の観測が、そのまま表に出る。

### §4.2 一次所属問い

`schema/hypothesis.schema.json` に `primary_question_id`（任意、`question_ids` の直後）を足した。**既存 93 行は 1 件も埋めていない。** 追記専用の台帳で、当時決めていない所属を後から書くのは「発行されなかった受領書」を作ることになる（`docs/parallel-work.md` 規則10 がロール受領書について述べているのと同じ理由）。

代わりに表の列は三値を持つ:

- `Q-003 (宣言)` — 行が宣言している
- ``未決→`Q-002` `` — 宣言がなく、矢印の先は `question_ids[0]`。**決定ではない**
- 未来の行は `primary_question_id` を書けば `(宣言)` 側になる

冒頭に「宣言済み **0** / 仮説 93 件、**未決 93 件**、複数問いに跨る仮説 **34** 件」を出した。**未決を 0 にすることは目標ではない**（`prompts/start.md` の「件数を終わりの条件にしない」）。この欄の仕事は、跨りが家系質量に二重計上されることを読者に見えるようにすることである。

---

## §5 提案1 — セッションが読んだ基底を記録する

`schema/session.schema.json` に `belief_basis`（任意）を足し、語彙を `belief_basis_label()` に固定した: `default`、`temporal_heir_guard`、`receiver_gated`、`narrowing_partner_share`、`pair_level_repeat`、`no_heir_credit` を `+` で連結する。

`BELIEF_MAP.md` の冒頭に **`> 使用基底 (belief_basis): \`default\``** を出し、`--json` の `state["belief_basis"]` にも同じ値を入れた。`--gated` で回すと `receiver_gated` になることを確認済み。

**既存セッション行は 1 件も埋めていない。** 前報告 §6 の「危険」欄に書いたとおり、欄を足すだけでは選択の根拠にならず、後から埋めれば製造された受領書になる。**記入の強制もしていない**（`required` に入れていない）。強制すると、この欄を足した次のセッションから書かない限り門が赤くなり、過去 1,112 行との非対称が「規則を満たすために過去を書き換える」圧力になる。

---

## §6 提案6 — `newborn_mass`

`python3 tools/belief_state.py --newborn-mass [HYP-ID]`（省略時は最新の `created_at`）。対象仮説を台帳から除いた反事実で同じ問いを再計算し、次を出す:

- 仮説数（前→後）、旧首位とその質量（前→後）、**旧首位の希釈（pp）**、新規行の質量、首位交代の有無

**実装後の実測（`HYP-20261123-fe0204`、Q-001/Q-002/Q-003 に跨る）**:

```text
Q-001  28 → 29  539a0c 45.61% → 45.61%  +0.000pp  新規 0.00%
Q-002  45 → 46  6e3e15 99.99% → 99.99%  +0.000pp  新規 0.00%
Q-003  61 → 62  6e3e15 99.99% → 99.99%  +0.000pp  新規 0.00%
```

**希釈は 0.000pp だった。** これは計器の故障ではなく、実際にそうなっている: 新しい行は log_odds 0 で入り、その問いの他の行も log_odds を持っているので、softmax の分母が増えても**首位の比率は 4 桁では動かない**（99.99% 側では丸めで消える）。前報告と前々報告が「併存数希釈」と呼んできたものは、**同程度の log_odds を持つ行が並ぶ問いでのみ観測できる**。Q-001 のように首位が 45.6% で二番手が 33.8% の問いでも、追加行の log_odds が 0 なら動かない。この計器は登録の副作用を測るが、**登録が既存の首位を削るのは、新しい行が既存の行と同程度の支持を持つ場合だけ**である。これは前報告 §4.4 の見立ての射程を狭める（§8-4）。

**規則は書いていない。** 前報告 §6 の「危険」欄（「登録するな」という圧力になる）に従い、この計器は測るだけで、登録の可否を判定しない。`writes: false` を返り値に明記した。

---

## §7 検証

### §7.1 門（13 本、すべて PASS）

```text
validate_seed                 PASS   （sessions=1114, notes=1255, evaluations=862, hypotheses=93）
append_only_check             PASS
readings_integrity_check      PASS
note_index --check            PASS
read_log_backfill --check     PASS
date_axis --enforce-shards    PASS
learning_metrics --check      PASS
three_gates --check           PASS
belief_state --check-map      PASS
inspect_inquiry --check-map   PASS
self_model --check            PASS
map_build --check             PASS
size_budget --strict          PASS
```

### §7.2 テスト

新規 `tests/test_harness_display_policy.py`（29 件）。主張するのは**機構**であって、生台帳の件数・方向・大きさではない（台帳に行を書いても壊れない）。既存の 1,085 件と合わせて全件を実行し、結果は §7.4。

### §7.3 事後確率が動いていないことの確認

圧縮・床・家系・基底のいずれも softmax に触れていない。`--check-map` が通ることは「描画が決定論的」を示すだけで「数値が同じ」を示さないので、`main` の `BELIEF_MAP.md` と実装後の `--full` 出力から上位 6 仮説の `P_t` を抜き出して比べた。値は一致した（`539a0c` 45.6%、`63b6bf` 33.8%、`994fd5` 18.9%、`6e3e15` 100.0%）。

### §7.4 全件テスト

`python3 -m unittest discover -s tests`: **1,115 tests, OK**。

---

## §8 実装した結果わかったこと（限界レジスタ）

1. **圧縮は予算を 216 KB 返したが、予算上限は下げていない。** 下げると `--full` が自分の門で落ちる。`--full` を求めるセッションは正当に余白を必要とする。この判断は `tools/size_budget.py` の注記に残した。
2. **`saturated` の定義に元からあった不一致を、変えずに残した。** Q-002 は EIG=0.0000 で `saturated=False`（閾値 0.02 を下回るので `True` のはずだが、`pair=None` の早期 continue とは別の経路）、Q-003 は同じ EIG で `True`。**今回の変更はこの不一致を作っていない。** 直すなら別の回の議題であり、直せばこの指標を引用した過去の報告の読み方が変わる。**次に読む者がまず確かめるべき箇所である。**
3. **`newborn_mass` は希釈を 0.000pp と測った。** これは「希釈が無い」ではなく「log_odds 0 の行を足しても、既に log_odds を持つ首位の比率は 4 桁では動かない」である。前報告と前々報告が「併存数希釈」と呼んだ現象は、**同程度の log_odds が並ぶ問いでのみ観測できる**という射程に狭められた。この計器を「登録の副作用の一般的な尺度」として引用しないこと。
4. **一次所属問いは 93 件すべて未決。** 表の列は `未決→` で埋まるが、それは `question_ids[0]` であって決定ではない。家系質量を問いごとに合計する限り二重計上は残る。**この欄を埋める判断は遡及では行えない**ので、次に仮説を立てるセッションが自分の行に書くしかない。
5. **家系の定義を一つに決めていない。** `parent_hypothesis_ids[0]` をたどる単一親の根を使った。`synthesizes` の複数親では、どの親を根とみなすかで家系が変わり、集中度も変わる。数値は「この定義の下で」の値である。
6. **詳細ブロックを既定で圧縮したので、低質量仮説の全文は `--full` を回さないと読めない。** 警告付きは残したが、警告の付かない低質量仮説（多くは棄却済みの根）は 1 行になる。**これは情報の削除ではないが、読者の経路の変更ではある。** 次に「なぜこの仮説が棄却されたか」を読みたくなった者は、`--full` か `state/evaluations.d/` へ行くことになる。

---

## §9 再現手順

```bash
# §2 圧縮の効果（実装前後で比べる）
python3 tools/belief_state.py --write-map          # 322,982 B（既定＝圧縮）
python3 tools/belief_state.py --write-map --full   # 545,224 B（全件詳細、追跡ファイル）
ls -l map/belief_state_full.md                     # 常に全件詳細（未追跡）

# §3 質量0の対
python3 tools/belief_state.py --json | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(json.dumps(d['saturation'], ensure_ascii=False, indent=1))"

# §4 家系と集中度
python3 tools/belief_state.py --json | python3 -c "
import json,sys; d=json.load(sys.stdin)
for q in ('Q-001','Q-002','Q-003'):
    qs=d['questions'][q]
    print(q, qs['family_count'])
    for f in qs['families'][:3]:
        print('  ', f['root_hypothesis_id'], f['member_count'],
              round(f['mass_share']*100,1), round(f['top_share_within_family']*100,1))"

# §5 基底
python3 tools/belief_state.py --json | python3 -c "import json,sys;print(json.load(sys.stdin)['belief_basis'])"
python3 tools/belief_state.py --gated --json | python3 -c "import json,sys;print(json.load(sys.stdin)['belief_basis'])"

# §6 登録1件の希釈
python3 tools/belief_state.py --newborn-mass
python3 tools/belief_state.py --newborn-mass HYP-20261123-fe0204 --json
```

---

## §10 完了の見方

前報告 §6 の 6 提案は、**優先順位の順にすべて実装された**。意味を変えずに実装できる 2 と 5 を先に置いた判断は正しかった — どちらも 1 行も事後確率を動かさずに、読者が見る数字を変えた（詳細ブロック −40.0%、推薦の有無）。

3 と 4 は欄を足したが、**既存の行は 1 件も埋めていない**。これは未完了ではなく、追記専用の下での正しい状態である。埋めるのは次に仮説を立てるセッションであり、そのとき `primary_question_id` を書けば、家系質量の二重計上が初めて解ける。

1 と 6 は記録と計器である。1 は**この回から書ける**（この回のセッション行に `belief_basis` を書いた）。6 は測った結果、前報告が想定したより**狭い**現象しか捉えていなかった（§8-3）。計器を足すことは、その計器が測れないことを知ることでもある。
