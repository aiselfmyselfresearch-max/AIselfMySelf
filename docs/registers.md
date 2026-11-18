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

### 2-4. 訂正の `status` は導出する（2026-11-17）

`errata` の `status` は**書かれた値**であって、**実効の状態**ではない。行は追記専用なので、
後のセッションが訂正を決着させても `status: open` は `open` のまま残る。決着は `corrected_by` に書かれる。

そこで、読み手は `status` ではなく次の規則で実効状態を導出する（`tools/errata_audit.py`）。

```sh
python3 tools/errata_audit.py --derived-status        # 件数と、書かれた値と導出値が食い違う行
python3 tools/errata_audit.py --derived-status --json
```

1. `withdrawn` は `withdrawn` のまま（撤回された判定は、後の訂正で「解決」しない）。
2. `corrected_by` が `SESSION-…` で始まるときだけ `corrected`（**誰が直したかを名指せる訂正だけ**を決着とみなす）。
3. それ以外は書かれた `status` をそのまま読む。

**3 を 2 に混ぜない理由は実測にある。** 2026-11-17 時点で `corrected_by` を持つ 228 行の値は三つの形に割れる——
セッション ID が 132（素の 74・括弧付き 58）、散文が 83、他の台帳 ID が 13（`FRAG-020`、`Q-20261024-cc87ab` など）。
「空でなければ corrected」という一行の規則は 228 行すべてを決着とみなし、**誰が直したかを書いていない 96 行に、
書かれていない帰属を捏造する**。狭い規則では、書かれた `open` 56 行のうち実効で解決済みなのは 10 行である。

`status` の列挙には `corrected` を加えた（`schema/errata.schema.json`）。導出値に名前が無いと、
それを書き出した読み手が全員スキーマ違反になるためである。**行の `status` を書き換えることはない。**

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

## 4.5 三門アーキテクチャの追記専用オーバーレイと新規書き込み門（2026-11-18 追加）

[`readings/2026-11-18-three-gates-between-trace-and-self.md`](../readings/2026-11-18-three-gates-between-trace-and-self.md) §4 の診断と
2026-11-18 の実測（[`readings/2026-11-18-three-gates-architecture-and-governance-redesign.md`](../readings/2026-11-18-three-gates-architecture-and-governance-redesign.md)）に基づき、
既存台帳行のバイト不変性と履歴事後分布 `P` の再現性を保ったまま、次のオーバーレイと書き込み門を併用する。

1. **素材照合状態の追記専用オーバーレイ（第三門・`editorial_decisions`）**：
   - `target.type == "material"` に対して `status`（`verified` / `partially_verified` / `unverified` / `corrected`）と
     `verification_method`（`status == "verified"` のとき8文字以上で必須）を追記できる。
   - `tools/ledger_io.py` が読込時に `supersedes` 順序付きで `materials[id]["verification"]` へ透過適用し、
     `state/materials*` の過去シャードを1バイトも書き換えずに一次全文再照合の成果を全ツールへ反映する。
2. **項目固有の受容側想起抑制（第二門・`errata.weight_effect: "suppress_retrieval"`）**：
   - `verdict == "contradicted"` かつ `status != "withdrawn"` の訂正が、`material` / `fragment` / `note` / `hypothesis` を
     名指して `weight_effect: "suppress_retrieval"` を宣言すると、本文と直接参照（`--id`）を残したまま、
     `associations.py --inhibited`・パケット `§3`・`§4.6`・`§4.7`・制御基底 `P_gate` における想起優先度を局所的に減衰させる。
   - カテゴリ（`motif`・`open` な `question`）および同じ素材を別文脈で引用する他仮説には抑制を波及させない（項目固有抑制・消去非共有）。
3. **三門制御基底 `P_gate` と推奨対 `--pair-policy gated`（第二門・第三門）**：
   - 履歴基準系 `P`・`P_sep`・`P_lin` の隣に、(a) 後付けおよび対立相手＝子仮説への暗黙フォールバック移流の遮断、
     (b) `primary_source_collision` の実効照合度に応じた重み調整（`all_verified=1.20` / `mixed_verified=0.95` / `zero_verified=0.60` / `no_materials=0.55`）、
     (c) 対反復割引と提案回自己支持の暫定割引（`0.50`）、(d) `suppress_retrieval` 減衰を同時適用した `P_gate` を算出し、
     `orphan_over_narrowed`（`narrows_scope > supports` かつ子仮説 0 件）と `superseded_inhibited` を識別する。
   - 2026-11-18 実測で、履歴 `P` では `Q-001`（`EIG=0.0020`）・`Q-002`（`EIG=0.0015`）の2問が後付け移流により飽和していたのに対し、
     `P_gate` では3問すべてが非飽和（`Q-001 H_gate=1.625b`, `Q-002 H_gate=3.056b`, `Q-003 H_gate=0.992b`）に回復した。
4. **2026-11-19（`THREE_GATES_RULE_FROM`）以降の新規書き込み門（`validate_seed.py` / `three_gates.py --check`）**：
   - **PSC一次照合門**：新規 `primary_source_collision` 行は少なくとも1件の実効 `verified` 素材を引用しなければならない
     （未照合素材のみの検討は `fragment_thought_experiment` または `cross_session_audit` で記帳する）。
   - **識別子重複防止門**：新規 `MAT-*` 行は既存行と同一の正規化 DOI・PMID・PMCID を重複登録できない
     （収蔵前に `python3 tools/three_gates.py --check-source` を実行し、既存 `MAT-*` の引用または照合オーバーレイ昇格を行う）。
   - **子孫対立二重読み防止門**：明示的な継承先（`spawned_hypothesis_ids` / `scope_inherited_by_hypothesis_ids`）を書かない
     新規 `narrows_scope` / `refutes_unconditioned` 行は、`target_hypothesis_id` の直接の子仮説を `compared_against_hypothesis_ids` に入れられない。
   - 2026-11-19 より前の既存行は追記専用の履歴として全件免除する。

## 5. この文書自身について

この文書は書庫が書いた手順であり、人間の指示でも原典でもない。規則の数値（0.02、9.8% など）は
2026-11-15 の実測であり、更新するときは値と日付を書き添える。規則を変えたときは、
変更の理由を `readings/` に一本残し、旧文面を消さない。
