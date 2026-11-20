# 探求ロール指針：Consolidator（評価統合・系譜整理 — 25%枠）

このセッションには **Consolidator（評価統合・系譜整理）** ロールが割り当てられています。
共通原則は [`start.md`](start.md) に従い、**散在する精読報告・未継承ノート（`§4.8`）・訂正録（`errata`）を検討し、根拠がある範囲で信念状態レイヤに継承すること**を目的とします。記帳や配線の件数自体は目的にせず、保留も許されます。

## このロールで行うこと

1. **未継承の窓（`§4.8`）と休眠精読ノート（`§4.7` 第3層）の回収**:
   - 別セッションの `read_log` 記録がない報告（それだけで未読とは言えない）や、`index_backfill: true` の構造スタブしか持たない報告を候補にする。実際に読んだ範囲に限って、必要なら `note_index.py --register <path> --session <SESSION-ID>` で判断を登録し、`--read-depth` は実際の読了範囲に合わせる（1セッション最大12件以内）。
   - 読んだノート行は必ず `read_log`（`target.type: "note"`, `reading: "reinterpreted"` または `"contested"`）に記帳する。
2. **重複仮説・過限定孤児の整理と、素材の再読・照合昇格・受容側鎮静**:
   - 異なる語彙で実質的に同じ条件付き命題を述べている仮説群は `lineage_op: "synthesizes"` または `verdict: "subsumes"` で整理し、`orphan_over_narrowed`（過限定・子仮説0件）や閉ループ補完候補（`§4.6` / `associations.py --complete`）に未回収の論点があれば接続する。
   - `python3 tools/three_gates.py --tier0-candidates` の未配線素材は**候補**であり、別セッションでの読書・評価の共起は、実時間順・読書から評価への変換・配線の効果を示さない。`counted` は精読とは限らず、基準セッション不明や記帳欠落もある。現在の層は事後分類で、`pre-2026-11` は実日付でなく記録のラベルかもしれない。実際に読んだ内容が主張の根拠になる場合に限って `claims` などに接続し、配線を増やすこと自体を目的にしない。生データは削除しない（[監査](../docs/2026-11-20-reading-is-not-conversion-991cf0a7.md)）。
   - `python3 tools/three_gates.py --upgrade-candidates` が示す非 `verified` 既収蔵素材を原典全文で再照合した場合は、新規 `MAT-*` を重複作成せず `editorial_decisions`（`target.type: "material"`, `status: "verified"`, `verification_method` 明記）で追記昇格する。
   - `BELIEF_MAP.md` で `⚠️ 関連訂正あり` の仮説や反証済み記録が再侵入し続けている場合は、`EVL-*` の記帳・評価行の `void_row`・または項目固有の受容側想起減衰 `errata.weight_effect: "suppress_retrieval"`（行は消さない）を検討する。
   - `state/*.d/` のシャード数が上限に近づいた場合は、独立したメンテナンスコミットで `python3 tools/three_gates.py --compact-shards`（確認後 `--apply`）を実行し、未参照の同日隣接シャードを順序・SHA-256 完全保存で統合できる。
3. **索引・学習メトリクス・三門整合の同期検証**:
   - `python3 tools/belief_state.py --write-map`・`python3 tools/map_build.py`・`python3 tools/learning_metrics.py --check`・`python3 tools/three_gates.py --check` を実行し、配線漏れ・棄却済み仮説の無条件復活・三門不変条件の違反がないことを確認する。
