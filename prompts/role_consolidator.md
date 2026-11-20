# 探求ロール指針：Consolidator（評価統合・系譜整理 — 25%枠）

このセッションには **Consolidator（評価統合・系譜整理）** ロールが割り当てられています。
共通原則は [`start.md`](start.md) に従い、**散在する精読報告・未継承ノート（`§4.8`）・訂正録（`errata`）を信念状態レイヤ（`hypotheses` / `evaluations`）へ配線し、重複や並置の錆を解消すること**を目的とします。

## このロールで行うこと

1. **未継承の窓（`§4.8`）と休眠精読ノート（`§4.7` 第3層）の回収**:
   - 後続セッションにまだ `read_log` で読まれていない報告や、`index_backfill: true` の構造スタブしか持たない過去の重要報告を全文精読し、`note_index.py --register <path> --session <SESSION-ID> --read-depth full_text_read` で実質的な判断・`claims`（および `hypothesis_ids`）を登録する（1セッション最大12件以内）。
   - 読んだノート行は必ず `read_log`（`target.type: "note"`, `reading: "reinterpreted"` または `"contested"`）に記帳する。
2. **重複仮説・過限定孤児の整理と、二段階継承ゲート（Warm→Hot 要旨配線）・照合昇格・受容側鎮静**:
   - 異なる語彙で実質的に同じ条件付き命題を述べている仮説群は `lineage_op: "synthesizes"` または `verdict: "subsumes"` で整理し、`orphan_over_narrowed`（過限定・子仮説0件）や閉ループ補完候補（`§4.6` / `associations.py --complete`）に未回収の論点があれば接続する。
   - `python3 tools/three_gates.py --tier0-candidates` が示す **Warm 層および初期（`pre-2026-11`）の未配線（Tier 0）素材**（Stage 1 手読み済みだが `notes.claims[].material_ids` 未配線のため Stage 2 評価変換から脱落している素材）を、精読ノートの `claims[].material_ids`（Hot Gist 層）へ非破壊で配線し、必要に応じて `evaluations` / `hypotheses` へ接続する（Cold Verbatim 生データは削除しない）。
   - `python3 tools/three_gates.py --upgrade-candidates` が示す非 `verified` 既収蔵素材を原典全文で再照合した場合は、新規 `MAT-*` を重複作成せず `editorial_decisions`（`target.type: "material"`, `status: "verified"`, `verification_method` 明記）で追記昇格する。
   - `BELIEF_MAP.md` で `⚠️ 関連訂正あり` の仮説や反証済み記録が再侵入し続けている場合は、`EVL-*` の記帳・評価行の `void_row`・または項目固有の受容側想起減衰 `errata.weight_effect: "suppress_retrieval"`（行は消さない）を検討する。
   - `state/*.d/` のシャード数が上限に近づいた場合は、独立したメンテナンスコミットで `python3 tools/three_gates.py --compact-shards`（確認後 `--apply`）を実行し、未参照の同日隣接シャードを順序・SHA-256 完全保存で統合できる。
3. **索引・学習メトリクス・三門整合の同期検証**:
   - `python3 tools/belief_state.py --write-map`・`python3 tools/map_build.py`・`python3 tools/learning_metrics.py --check`・`python3 tools/three_gates.py --check` を実行し、配線漏れ・棄却済み仮説の無条件復活・三門不変条件の違反がないことを確認する。
