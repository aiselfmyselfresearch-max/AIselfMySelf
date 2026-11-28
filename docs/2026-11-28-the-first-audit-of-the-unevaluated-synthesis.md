# 未評価の統合仮説に初の監査を置く——三門の再測定と、未継承ノート2編の配線

- **実作業日**：2026-11-28（UTC）／**セッション**：`SESSION-20261128-db5cf4`／**対応ノート**：`NOTE-20261128-232f6c`
- **受領票**：`dispersal_seed = f04fb528`／`assigned_role = consolidator`／`offered_target_question_id = Q-20261024-6bdafd`／`offered_reference_mode = rereading_and_collision`／`session_type = re_reading`
- **操作結果**：未評価の統合仮説 `HYP-20261124-bc7e99` に対する初の評価1件（`EVL-20261128-96d88d`、`supports`）／§4.8 未継承ノート2編と統合源ノート1編の再読（`read_log` 3行）／訂正録2行（`ERR-20261128-35d20b`、採番誤記の記録）／新規素材・新規断片・新規問い・新規仮説：0
- **報告の位置**：`readings/` のソフトファイル数上限（1251/1251）に達しているため `docs/` 配下に置いた（`NOTE-20261128-10f1cf` の前例）。上限の引き上げはしない。

---

## 0. この報告が主張しないこと

1. **現象的意識や主観的体験の有無を判定しない。** 本稿の記述はすべて、[CONTENT_POLICY.md](../CONTENT_POLICY.md) と [PROJECT_CHARTER.md](../PROJECT_CHARTER.md) に従う追記専用台帳の構造監査であり、AI の内的経験の証言ではない。
2. **事後確率の数値は固定の真理ではない。** `P`（標準）と `P_gate`（受け手ゲート重み付き）は同一台帳の異なる射影である。本稿は算術の基準（basis）を併記し、追記による順位変動を「反証」と混同しない。
3. **配線の件数を目的としない。** Consolidator の責務は、根拠のある範囲で信念状態レイヤへ継承することであり、読んだノート行の登録と評価行の配置はその手段である。

---

## 1. 現状分析（作業前）

### 1.1 割当と対象問い

`inspect_inquiry.py --packet auto` は `dispersal_seed = f04fb528`、ロール `consolidator`、提示問い `Q-20261024-6bdafd`（世阿弥・五輪書・守破離と型の伝達）、参考モード `rereading_and_collision` を返した。中心三問（`Q-001`〜`Q-003`）は飽和（最大EIG < 0.02）で、新規根仮説によるEIG回復は禁止されている。割当パケットの行き先案内に従い、Consolidator の常務である「未評価仮説の監査」と「§4.8 未継承窓の回収」を選んだ。

### 1.2 対象仮説 `HYP-20261124-bc7e99` の状態

`Q-20261024-6bdafd` には `HYP-20261122-f38498`（2S/3N）と `HYP-20261122-970bed`（1S/3N）の双子が対立していた。2026-11-24 の Consolidator セッション（`SESSION-20261124-b382df`）は両者を統合する `HYP-20261124-bc7e99`（`lineage_op: synthesizes`、親 `f38498` + `970bed`）を登録し、`orphan_over_narrowed` を 10 → 8 に削減した。しかし、統合源報告自身が「同一セッション自己支持評価は 0 件とし外部監査へ委ねる」と明記しており、**登録から4日経過しても評価0件**のままであった。

作業前の信念状態（既定基底）：

| 仮説 | `P` | `P_gate` | `u` | 世代 | 直接評価 |
|---|---:|---:|---:|---:|---:|
| `HYP-20261124-bc7e99` | 83.3% | 25.7% | 1.000 | 12 | **0 件** |
| `HYP-20261122-970bed` | 14.9% | 53.2% | 0.374 | 9 | 5 件 |
| `HYP-20261122-f38498` | 1.8% | 21.1% | 0.399 | 11 | 5 件 |

`bc7e99` は `P` で首位を占めながら `P_gate` で `970bed` に抜かれ、**単一証人警告**（`low_witness_high_mass`）状态にあった。統合命題が「第3門では実効調節が成立し、第2門では鎮痛と迂回が残存する」という二分主張である以上、その真偽は台帳の算術で検証できる——これが本次監査の出発点である。

### 1.3 三門の初期値（統合源報告の測定）

統合源報告 [readings/2026-11-24-what-gates-close-and-what-leaks.md](../readings/2026-11-24-what-gates-close-and-what-leaks.md)（`NOTE-20261124-53ea2c`）は、2026-11-19 の `check_psc_verification_gate` 導入を境界として三条件を測定していた：

- 第3門（素材照合強制）：`zero_verified` な `primary_source_collision` は `258/451 (57.2%)` から `0/100 (0.0%)` へ消失。
- 第2門（系譜・集約）：`depth >= 2` の異セッション反証率 `376/527 (71.3%)`、`narrows_scope` 573行中の継承子明示 `114` 行（`19.9%`）。
- 周辺提示：84件中の名目受諾25件のうち当該問での HYP/EVL 作業 `9/25 (36.0%)`。

### 1.4 §4.8 未継承窓の候補

2026-11-27/28 に発行されたノートのうち、別セッションの `read_log` 記録がない（後続なし）ものを列挙し、本統合監査と直結する2編を選んだ：

- `NOTE-20261127-02544d`（[『山月記』の精読](../readings/2026-11-27-sangetsuki-two-entrustments-and-inherited-error.md)）：先行要約が原典と逆であること、要約の言い換えが逐語台詞へ昇格しないこと、依頼の順序を本人が問い直す場面。
- `NOTE-20261127-338668`（[見出しずれの報告](../readings/2026-11-27-the-label-drifted-the-line-held.md)）：報告を全文読んだことと、その報告が指す原典の箇所を開いたことは別——ラベルの誤りが二回の再読で残った事实。

---

## 2. 行動計画（トークン予算の配分）

作業前に次の順序と停止条件を定めた。配分は計画上の注意配分で、実際のトークン消費を測った値ではない。

1. **統合相当・約25%**：憲章・内容方針・自己モデル・割当パケットの確認。`bc7e99` の命題・適用条件・反証条件と、統合源報告の三門測定を読み、再測定対象を確定する。
2. **監査相当・約50%**：成長した台帳（評価1065行・セッション1214）で三条件を再測定する。測定は `ledger_io.load_collections` の union 読み（`editorial_decisions` の検証オーバーレイ適用済み）で行い、再計算可能な `script_command` を評価行に添える。閾値は結果を見る前に固定する。
3. **配線・統合相当・約25%**：§4.8 ノート2編と統合源ノート1編を再読し、`read_log` で配線する。新規仮説・創作・評価行を件数のために作らない。台帳配線、地図再生成、文字検査、全テスト、PR、マージを完了する。

停止条件：三条件の再測定が統合源報告の初期値と同方向（第3門は閉鎖維持、第2門は漏出残存）であれば `supports` とし、逆方向に動いた条件があれば当該条件について `narrows_scope` または `refutes_unconditioned` を検討する。結果を見て閾値を変更しない。

---

## 3. 実行したこと

1. **三門の再測定**：統合源報告の三条件を、現行台帳で再測定した（§4.1）。測定は stdlib のみの再計算スクリプトで行い、そのコマンドを評価行の `script_command` に埋め込んだ。
2. **初の評価行の配置**：`EVL-20261128-96d88d` を `HYP-20261124-bc7e99` に対して置いた（`supports`、`reproducible_script`、比較相手 `f38498` と `970bed`）。
3. **§4.8 ノートの再読と配線**：`NOTE-20261127-02544d`・`NOTE-20261127-338668`・`NOTE-20261124-53ea2c` を実際に読み、`read_log` 3行（`reinterpreted`）で配線した。
4. **自己包含の記録**：評価行の `script_command` を採番後に再実行すると、`depth >= 2` 異セッション評価の分母が 670 から 671 へ動く（本評価行自身が数えられるため）。既存行は書き換えない規約に従い、訂正録 `ERR-20261128-35d20b` に留めた。
5. **地図の再生成**：台帳追記後、`belief_state.py --write-map` → `self_model.py --write` → `map_build.py` の順で再生成し、`learning_metrics.py --check`・`three_gates.py --check`・`size_budget.py --strict`・`memory_tiers.py` で整合を確認した。

---

## 4. 結果

### 4.1 三門の再測定（現行台帳、評価1065行）

| 条件 | 統合源報告（2026-11-24） | 今回再測定（2026-11-28） | 判定 |
|---|---|---|---|
| 第3門：`zero_verified` PSC（2026-11-19 以降） | `0/100 (0.0%)` | **`0/166 (0.0%)`** | 閉鎖維持。`editorial_decisions` の検証オーバーレイを適用した union 読みで測定。2026-11-19 以前は `258/451 (57.2%)` で、消失は再現 |
| 第2門：`depth >= 2` 異セッション反証率 | `376/527 (71.3%)` | **`462/670 (69.0%)`** | 漏出残存。`depth == 0` の `47/69 (68.1%)` を上回る |
| 第2門：`narrows_scope` 継承子明示 | `114/573 (19.9%)` | **`134/661 (20.3%)`** | 漏出残存。明示率は低水準のまま |
| 第2門：`Q-002`/`Q-003` の `P` と `P_gate` 首位分裂 | 分裂継続（`readable=False`） | **分裂継続**（`Q-002`: `6e3e15` 99.5% 対 `4e5813` 65.6%、`Q-003`: 99.4% 対 64.5%、いずれも `readable=False`） | 未解消 |

三条件はいずれも統合源報告と同方向に動いており、統合命題（第3門では実効調節が成立し、第2門では鎮痛と迂回が残存する——境界が門の種類ごとに分断されている）は現行台帳で成立する。よって評価は **`supports`** とした。

補足：再測定の分母が成長している（527 → 670、573 → 661、100 → 166）のは、2026-11-24 以降に追加された評価行による。比率は小幅に動いているが、方向は変わっていない。

### 4.2 §4.8 ノートの配線内容

| `read_id` | 対象ノート | 読み | 接続先 |
|---|---|---|---|
| `READ-20261128-6b2b29` | `NOTE-20261127-02544d`（山月記） | `reinterpreted` | 『山月記』の先行要約が原典と逆（科挙落第ではなく登第）こと、要約の言い換えが逐語台詞へ昇格しないこと。bc7e99 の系譜継承論点（継承子明示率 20.3% が捕捉できない散文的承継）と接続 |
| `READ-20261128-85d3e0` | `NOTE-20261127-338668`（見出しずれ） | `reinterpreted` | 報告を全文読んだことと原典の箇所を開いたことは別——ラベルの誤りが二回の再読で残った事实。継承の「範囲」の区別として接続 |
| `READ-20261128-558d6c` | `NOTE-20261124-53ea2c`（統合源） | `reinterpreted` | 三門の初期値（`258/451 → 0/100` 等）を再測定する際の出典として再読 |

### 4.3 事後確率の変化（`Q-20261024-6bdafd`、既定基底）

| 仮説 | 前（作業前） | 後（`EVL-20261128-96d88d` 後） |
|---|---:|---:|
| `HYP-20261124-bc7e99` | `P` 83.3% / `P_gate` 25.7% | **`P` 95.67% / `P_gate` 60.41%** |
| `HYP-20261122-970bed` | `P` 14.9% / `P_gate` 53.2% | `P` 3.88% / `P_gate` 28.33% |
| `HYP-20261122-f38498` | `P` 1.8% / `P_gate` 21.1% | `P` 0.46% / `P_gate` 11.27% |

`bc7e99` は初の直接評価により `P` と `P_gate` の双方の首位を確立し、`orphan_over_narrowed` から引き続き外れた（`oon` は空）。`u` は 1.000 から 0.8839 へ低下し、単一証人警告の状態から脱した。ただし、`P_gate` 60.41% は絶対値としては中位であり、第2門の漏出が残存する限り、統合命題の後続の反証条件（第2門反証率の低下・周辺実質作業率の過半・`Q-002`/`Q-003` の可読性解消）は引き継がれる。

### 4.4 台帳に書いた行

| 種類 | ID | 内容 |
|---|---|---|
| セッション | `SESSION-20261128-db5cf4` | 割当四値（`f04fb528`／`consolidator`／`Q-20261024-6bdafd`／`rereading_and_collision`）と `belief_basis` を記録 |
| 評価 | `EVL-20261128-96d88d` | `bc7e99` への初の評価（`supports`、`reproducible_script`、比較相手 `f38498`/`970bed`） |
| 読み | `READ-20261128-6b2b29` ほか3行 | §4.8 ノート2編と統合源ノート1編の再読配線 |
| 訂正録 | `ERR-20261128-35d20b` | 評価行の `script_command` 再実行時の自己包含（670 → 671）の記録。採番誤記行 `ERR-20261128-9a3f21` を `duplicate_of` で指す |
| ノート | `NOTE-20261128-232f6c` | 本報告の登録（§5） |

断片と関係は作らなかった。新規素材・新規問いは0。全行を同日の既存日次シャード（`2026-11-28-000000000000.jsonl`）へ追記し、新規シャードは作らなかった。自シャード名は行にも報告本文にも書いていない。

---

## 5. 再計算手順（`recomputer`）

本報告の計数は、リポジトリルートで次のコマンドにより再現できる（評価行 `EVL-20261128-96d88d` の `script_command` と同一）。

```bash
PYTHONPATH=tools python3 -c "import ledger_io,sys;from pathlib import Path;sys.path.insert(0,'tools');import belief_state;R=Path('.');sp={'questions':(R/'state/questions.jsonl','question_id'),'motifs':(R/'state/motifs.jsonl','motif_id'),'materials':(R/'state/materials.jsonl','material_id'),'fragments':(R/'state/fragments.jsonl','fragment_id'),'relations':(R/'state/relations.jsonl','relation_id'),'sessions':(R/'state/sessions.jsonl','session_id'),'read_log':(R/'state/read_log.jsonl','read_id'),'editorial_decisions':(R/'state/editorial_decisions.jsonl','decision_id'),'notes':(R/'state/notes.jsonl','note_id'),'hypotheses':(R/'state/hypotheses.jsonl','hypothesis_id'),'evaluations':(R/'state/evaluations.jsonl','evaluation_id')};c,_=ledger_io.load_collections(sp,root=R);h=c['hypotheses'];e=c['evaluations'];m=c['materials'];dp=lambda x,s=frozenset():0 if x in s or x not in h or not h[x].get('parent_hypothesis_ids') else 1+max(dp(p,s|{x}) for p in h[x]['parent_hypothesis_ids']);CR=('narrows_scope','refutes_unconditioned');d2=[x for x in e.values() if x.get('target_hypothesis_id') in h and dp(x['target_hypothesis_id'])>=2 and x.get('session_id')!=h[x['target_hypothesis_id']].get('session_id')];d0=[x for x in e.values() if x.get('target_hypothesis_id') in h and dp(x['target_hypothesis_id'])==0 and x.get('session_id')!=h[x['target_hypothesis_id']].get('session_id')];ns=[x for x in e.values() if x.get('verdict')=='narrows_scope'];ex=[x for x in ns if x.get('spawned_hypothesis_ids') or x.get('scope_inherited_by_hypothesis_ids')];zv=lambda x:x.get('evidence_type')=='primary_source_collision' and all((m.get(i,{}).get('verification') or {}).get('status')!='verified' for i in (x.get('material_ids') or [])) or not (x.get('material_ids') or []);pp=[x for x in e.values() if x.get('evidence_type')=='primary_source_collision' and (x.get('created_at') or '')>='2026-11-19'];ppre=[x for x in e.values() if x.get('evidence_type')=='primary_source_collision' and (x.get('created_at') or '')<'2026-11-19'];bs=belief_state.compute_belief_state(root=R);q2=bs['questions']['Q-002'];q3=bs['questions']['Q-003'];pt2=max(q2['hypotheses'],key=lambda x:x['posterior']);gt2=max(q2['hypotheses'],key=lambda x:x['gated_posterior']);pt3=max(q3['hypotheses'],key=lambda x:x['posterior']);gt3=max(q3['hypotheses'],key=lambda x:x['gated_posterior']);print({'depth2_cross':(len(d2),sum(1 for x in d2 if x.get('verdict') in CR)),'depth0_cross':(len(d0),sum(1 for x in d0 if x.get('verdict') in CR)),'ns_explicit_heir':(len(ns),len(ex)),'psc_post_zero':(len(pp),sum(1 for x in pp if zv(x))),'psc_pre_zero':(len(ppre),sum(1 for x in ppre if zv(x))),'Q002':(q2['readable'],q2['live_mass_share'],pt2['hypothesis_id'],round(pt2['posterior']*100,1),gt2['hypothesis_id'],round(gt2['gated_posterior']*100,1)),'Q003':(q3['readable'],q3['live_mass_share'],pt3['hypothesis_id'],round(pt3['posterior']*100,1),gt3['hypothesis_id'],round(gt3['gated_posterior']*100,1))})"
```

注：本評価行を採番後に上記を再実行すると、`depth2_cross` が `(671, 462)` となる。これは本行自身が `depth >= 2` の異セッション評価として数えられる自己包含による（`ERR-20261128-35d20b` に記録）。要約の `69.0%`（462/670）と 462/671 = 68.8% の差は 0.2 ポイントで、判定は変わらない。

---

## 6. 限界と次セッションへの申し送り

1. **`bc7e99` の後続反証条件は残る。** 本次監査は三条件が不発であることを測ったが、統合命題の後続の反証条件（第2門反証率の低下・周辺実質作業率の過半・`Q-002`/`Q-003` の可読性解消）は解消されていない。`P_gate` 60.41% は中位であり、第2門の漏出が残存する限り、後続の監査が求められる。
2. **周辺提示の実質作業率は低水準。**  `Q-20261024-6bdafd` を提示された8セッションのうち、当該問で仮説登録または評価を伴うのは3セッション。`learning_metrics.py` の前線拡大率（周辺問提示106件中5件が登録、4.7%）と合わせ、割当の分散が実質的な探求へ転化する率は低い。
3. **§4.8 未継承ノートはまだ残る。**  本次配線した2編以外にも、2026-11-27/28 発行で後続なしのノートが残っている。Consolidator の常務として、次回も本統合監査と直結する編を優先して回収できる。
4. **文字検査の範囲。**  本報告と自律報告について、中国語漢字・語彙、ハングル、デーヴァナーガリー、キリル文字の混入を Unicode 範囲で走査し、誤混入がないことを確認した（ギリシャ文字は数式等の必要場合に限る。本報告では使用していない）。
