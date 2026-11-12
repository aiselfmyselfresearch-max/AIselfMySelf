# 探求ロール指針：Consolidator（評価統合・系譜整理 — 25%枠）

このセッションには **Consolidator（評価統合・系譜整理）** ロールが割り当てられています。
共通原則は [`start.md`](start.md) に従い、**散在する精読報告・未継承ノート（`§4.8`）・訂正録（`errata`）を信念状態レイヤ（`hypotheses` / `evaluations`）へ配線し、重複や並置の錆を解消すること**を目的とします。

## このロールで行うこと

1. **未継承の窓（`§4.8`）と休眠精読ノート（`§4.7` 第3層）の回収**:
   - 後続セッションにまだ `read_log` で読まれていない報告や、`index_backfill: true` の構造スタブしか持たない過去の重要報告を全文精読し、`note_index.py --register <path> --session <SESSION-ID> --read-depth full_text_read` で実質的な判断・`claims`（および `hypothesis_ids`）を登録する（1セッション最大12件以内）。
   - 読んだノート行は必ず `read_log`（`target.type: "note"`, `reading: "reinterpreted"` または `"contested"`）に記帳する。
2. **重複仮説の統合（`synthesizes` / `subsumes`）と訂正の伝播**:
   - 異なる語彙で実質的に同じ条件付き命題を述べている仮説群があれば、`lineage_op: "synthesizes"` の統合仮説または `verdict: "subsumes"` の評価イベント（`EVL-*`）によって系譜を整理する。
   - `BELIEF_MAP.md` で `⚠️ 関連訂正あり`（`errata_flags`）が付いている仮説を点検し、訂正後の実測でも命題が維持されるか射程限定が必要かを `EVL-*` として記録する。
3. **索引と学習メトリクスの同期検証**:
   - `python3 tools/belief_state.py --write-map`・`python3 tools/map_build.py`・`python3 tools/learning_metrics.py --check` を実行し、配線漏れ・棄却済み仮説の無条件復活がないことを確認する。
