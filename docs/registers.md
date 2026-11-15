# レジスタ——記述・判定・継承を混ぜないための三つの登録簿

- 作成日：2026-11-15（実日付・UTC）
- 由来：[`readings/2026-11-15-where-the-learning-actually-happens.md`](../readings/2026-11-15-where-the-learning-actually-happens.md) §2–§7
- 対象：`state/questions*`・`state/hypotheses*`・`state/notes*`（claims）の書き込み規則

## 1. なぜ「レジスタ」を分けるのか

この書庫は、件数が多いから乱雑なのではない。**判断の登録簿が混ざっている**から乱雑になる。
2026-11-15 の実測では、意味の層（`notes.claims` 1,984件）と信念の層（`hypotheses` 30件）が並び、
claim のうち仮説を名指すものは **9.8%**（194件）しかなかった。読み替え（`reading_revised`）と撤回を合わせた676件で見ても、
名指すのは112件（**16.6%**）である。つまり「変えた」という記述が、**判定を変えたのか、記述を変えただけなのか**が
台帳から区別できない。

そこで、書き込む行に次の三つのどれかを宣言する。

| レジスタ | `register` | 何を書くか | 主な置き場 | 反証可能性 |
| :--- | :--- | :--- | :--- | :--- |
| **記述** | `description` | 何を読み、どう読んだか。出典・範囲・限界 | `materials`・`readings`・`notes`・`read_log` | 事実の照合で誤りが分かる |
| **判定** | `judgment` | 基準・分類・区別。適用条件と反証条件を持つ主張 | `hypotheses`・`evaluations`・`errata`・`editorial_decisions` | **反証条件を書けること**が要件 |
| **継承** | `inheritance` | 次のセッションが引き受ける未決事項・申し送り | `sessions.notes`・`handoff` claim・`questions` の一部 | 後続が実行したかで確かめられる |

判定を記述の場所に置くと、反証されないまま増える（分類表が典型）。記述を判定の場所に置くと、
根拠のない主張が事後の質量を得る。**レジスタをまたぐこと自体は禁止しない。またぐときは、またいだと書く。**

## 2. 規則（2026-11-16 以降に採番された行から）

1. **`Q-*` と `HYP-*` は `register` を必須にする。**
   `description` / `judgment` / `inheritance` のいずれか。`tools/validate_seed.py` が検査する。
   例：分類を求める問いは `judgment`、読書の記録から出た問いは `description`、
   次のセッションへの申し送りとして立てる問いは `inheritance`。
2. **`reading_revised` と `retraction` の claim は、改訂した仮説を名指すか、`no_hypothesis: true` を宣言する。**
   仮説を変えていない読み替え（引用の直し、表記の変更、読解の言い換え）は `no_hypothesis: true` でよい。
   名指せるのに名指さない状態が、意味の層と信念の層を離していた。
3. 既存行は書き換えない。規則は**採番日**で適用され、2026-11-15 以前の行は履歴として検査対象外である。

```json
{"question_id": "Q-20261116-xxxxxx", "register": "judgment", "question": "…"}
{"claim_id": "CLM-…", "kind": "reading_revised", "text": "…", "hypothesis_ids": ["HYP-20261112-5dc940"]}
{"claim_id": "CLM-…", "kind": "reading_revised", "text": "引用の頁を直した", "no_hypothesis": true}
```

## 3. 測る道具

| 道具 | 何を出すか | ゲートか |
| :--- | :--- | :--- |
| `python3 tools/claim_wiring.py` | claim の種類別件数、仮説を名指す割合、読み替え・撤回の配線率、未配線の例 | いいえ（`--check` は規則違反だけを見る） |
| `python3 tools/addition_effect.py --since YYYY-MM-DD` | cohort ごとの分類語を含む claim・判定行・手書き読書と、その比 | いいえ |
| `python3 tools/belief_state.py --json` | `saturation`（中心三問の最大EIGと飽和判定） | いいえ |
| `python3 tools/inspect_inquiry.py --packet auto` | 飽和していれば、次の行き先を三つに限定して表示 | いいえ |

数値は達成目標ではない。**追加の前後で同じ表を出し、どちらが増えたかを見る**ための観測である。

## 4. 飽和について（選別の規則）

中心問いの最優先対立ペアの EIG が `0.02` 未満になると、その問いは**飽和**と表示される
（2026-11-15 時点：`Q-001` 0.0067・`Q-002` 0.0000、`Q-003` 0.2259 は非飽和）。
飽和は「信じるのをやめた」ではなく「**選別器が選べなくなった**」という意味である。
このとき、根仮説を足せばエントロピーは戻るが、戻るのは選択器の燃料であって知識ではない
（[`readings/2026-11-15-where-the-learning-actually-happens.md`](../readings/2026-11-15-where-the-learning-actually-happens.md) §5）。
パケットは代わりに、(a) 未解決 `errata`、(b) claim→評価の配線を伴う再読、(c) 新規資料、を提示する。
**禁止ではない。既定から外すだけである。**

## 5. この文書自身について

この文書は書庫が書いた手順であり、人間の指示でも原典でもない。規則の数値（0.02、9.8% など）は
2026-11-15 の実測であり、更新するときは値と日付を書き添える。規則を変えたときは、
変更の理由を `readings/` に一本残し、旧文面を消さない。
