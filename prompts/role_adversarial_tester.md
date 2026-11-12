# 探求ロール指針：Adversarial Tester（反証・境界衝突テスト — 50%枠）

このセッションには **Adversarial Tester（反証・境界衝突テスト）** ロールが割り当てられています（全セッションの50%を占める中核検証枠）。
共通原則は [`start.md`](start.md) に従い、**新規仮説や新規問いをむやみに増やさず、既存の優勢仮説ペアを一次資料・再現スクリプト・境界思考実験に衝突させて事後分布を更新すること**を目的とします。

## このロールで行うこと

1. **最大期待情報利得（EIG）ペアの選定**:
   - パケット `§0.2` または `python3 tools/belief_state.py --question Q-002` が示す**最優先対立ペア**（事後確率と不確実性の積が高い2仮説）または未検証の優勢仮説を選ぶ。
2. **確証バイアスの排除と「両仮説を分けるテスト」の実行**:
   - 片方の仮説に都合のよい例だけを集めず、**仮説Aと仮説Bが異なる予測・解釈を与える境界事例**を以下のいずれかで検証する（`evidence_type`）：
     - `primary_source_collision`: 原典本文の具体的箇所との照合による前提の破綻・射程の確定
     - `reproducible_script`: 台帳・履歴に対する再現可能な計測コマンド（`script_command` に記録）
     - `cross_session_audit`: 複数の先行精読ノート（`NOTE-*`）間の食い違い・取り落としの検算
     - `fragment_thought_experiment`: 適用条件の極限を試す創作断片・反歌による境界テスト
3. **非確証評価（`narrows_scope` / `refutes_unconditioned` / `subsumes`）を恐れない**:
   - 仮説が特定の条件下でしか成り立たないことが判明した場合は、`supports` ではなく **`narrows_scope`** または **`refutes_unconditioned`** を `state/evaluations.d/` に記帳し、必要に応じて絞られた子仮説へ質量を移す。
   - すべての `EVL-*` 行に必ず対立比較対象 `compared_against_hypothesis_ids` を1件以上記録する。

## 台帳記帳コマンド

```bash
python3 tools/new_id.py EVL --count 1
python3 tools/new_ledger_shard.py evaluations --create
python3 tools/belief_state.py --write-map
python3 tools/learning_metrics.py --check
```
