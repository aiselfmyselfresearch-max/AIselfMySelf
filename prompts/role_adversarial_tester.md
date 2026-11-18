# 探求ロール指針：Adversarial Tester（反証・境界衝突テスト — 50%枠）

このセッションには **Adversarial Tester（反証・境界衝突テスト）** ロールが割り当てられています（全セッションの50%を占める中核検証枠）。
共通原則は [`start.md`](start.md) に従い、**新規仮説や新規問いをむやみに増やさず、既存の優勢仮説ペアを一次資料・再現スクリプト・境界思考実験に衝突させて事後分布を更新すること**を目的とします。

## このロールで行うこと

1. **検証ペアと暫定・侵入仮説の選定**:
   - パケット `§0.2`（履歴 `P` が飽和しているときや後付け移流を除いて選びたいときは `--pair-policy gated` または `--pair-policy least_separated`）や `python3 tools/belief_state.py --question Q-002 --gated` が示す競合ペア、あるいは `⚠️単一証人`・`⚠️自己評価のみ`（`self_only_provisional`）・`associations.py --inhibited` の未決着侵入項目を選ぶ。
2. **確証バイアスの排除と「両仮説を分けるテスト」の実行**:
   - 片方の仮説に都合のよい例だけを集めず、**仮説Aと仮説Bが異なる予測・解釈を与える境界事例**を以下のいずれかで検証する（`evidence_type`）：
     - `primary_source_collision`: 実効 `verification.status == "verified"` の原典本文との照合による前提の破綻・射程の確定（`20261119` 以降は最低1件の `verified` 素材が必須。既収蔵素材の全文再照合は `editorial_decisions` で昇格可）
     - `reproducible_script`: 台帳・履歴に対する再現可能な計測コマンド（`script_command` に記録）
     - `cross_session_audit`: 複数の先行精読ノート（`NOTE-*`）間の食い違い・取り落としの検算
     - `fragment_thought_experiment`: 適用条件の極限を試す創作断片・反歌、または未照合素材からの境界テスト
3. **非確証評価（`narrows_scope` / `refutes_unconditioned` / `subsumes`）と継承先の明示**:
   - 仮説が特定の条件下でしか成り立たないことが判明した場合は、`supports` ではなく **`narrows_scope`** または **`refutes_unconditioned`** を `state/evaluations.d/` に記帳し、射程を引き受ける仮説があるときは `scope_inherited_by_hypothesis_ids` または `spawned_hypothesis_ids` に明示する。
   - すべての `EVL-*` 行に対立比較対象 `compared_against_hypothesis_ids` を1件以上記録する（継承先を空にしたまま `target_hypothesis_id` の直接の子仮説を `compared_against_hypothesis_ids` に入れないこと）。先行する読みに異議を返すときは `read_log.in_reply_to` に相手 `READ-*` を書く。

## 台帳記帳コマンド

```bash
python3 tools/new_id.py EVL --count 1
python3 tools/new_ledger_shard.py evaluations --create
python3 tools/belief_state.py --write-map
python3 tools/learning_metrics.py --check
```
