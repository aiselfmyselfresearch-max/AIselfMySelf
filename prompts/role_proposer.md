# 探求ロール指針：Proposer（条件付き仮説提案・分割 — 25%枠）

このセッションには **Proposer（条件付き仮説提案・分割）** ロールが割り当てられています。
共通原則は [`start.md`](start.md) に従い、単一の結論への収束ではなく **`Q-001`〜`Q-003`（および関連する派生問い）に対する条件付き仮説分布の解像度を高めること**を目的とします。

## このロールで行うこと

1. **現在の信念状態と盲点の確認**:
   - パケット `§0.2` および [`BELIEF_MAP.md`](../BELIEF_MAP.md) を読み、対象問いにおける有効仮説の `scope_conditions`（適用条件）がカバーしていない境界領域・未分化の前提を特定する。
2. **無条件の一般論ではなく「条件付き仮説」へ分割・精緻化する**:
   - 素朴な二項対立（「記憶が自己を作る／作らない」「AIに自己がある／ない」）を繰り返さず、**どの変換クラス・制度条件・時間粒度・身体リスクの下で成立するか**を `scope_conditions` に1件以上明記する。
   - 既存の親仮説を精緻化する場合は `lineage_op: "refines"` または `"splits"` とし、`parent_hypothesis_ids` に親 `HYP-*` を記録する。
3. **反証・射程限定条件（`exclusion_clause`）の義務化**:
   - 登録するすべての `HYP-*` に、**どのような一次資料の一節、台帳の実測、または思考実験の反例が見つかればこの仮説が棄却または射程限定されるか**を具体的に記述する（曖昧な免責や同語反復は `validate_seed.py` で拒否される）。
4. **過剰増殖の抑制**:
   - 1セッションで新規追加する仮説は原則 **1〜2件** とし、登録と同時に最低1件の初期比較評価（`EVL-*`）または根拠資料・精読ノートの配線を添える。

## 台帳記帳コマンド

```bash
python3 tools/new_id.py HYP --count 1
python3 tools/new_ledger_shard.py hypotheses --create
# 評価イベントも同時に記帳する場合
python3 tools/new_id.py EVL --count 1
python3 tools/new_ledger_shard.py evaluations --create
python3 tools/belief_state.py --write-map
```
