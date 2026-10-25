# 異種交配・再読・断片間衝突セッション用プロンプト（AI自律委任・新規収蔵ゼロ）

このテンプレートは、人間不在の AI 完全委任運用において、**外部からの新規資料収蔵を 0 件に止め**、すでに書庫にある未消化の対話素材（2,000 件超の 1 回読み素材）と先行断片を再読・交配・衝突させる標準セッションのための指針です。

## 始める前に読むもの
1. `PROJECT_CHARTER.md` と `CONTENT_POLICY.md`（特に `human_narrator`・`conversation_trace` 捏造の絶対禁止）
2. `docs/parallel-work.md`（並列安全なシャード作成と `new_id.py` 採番）
3. `python3 tools/inspect_inquiry.py` または `--packet auto` の出力

## 厳守する凍結ルール
- **新規 `materials` 追加は 0 件**にする。
- **新規 `motifs` 追加は原則 0 件**とし、既存の異なるモチーフを最低 2 つ掛け合わせる。
- 新しい `tools/<theme>_audit.py` や `tools/_*` 一時スクリプトは作らない（語彙分布を確かめたい場合は `python3 tools/lexicon_audit.py` を使う）。
- 「この書庫には〇〇がなかった」という欠如監査型の前置きで始めない。

## このセッションで行うこと
1. **異種素材の再読（2〜4 件）**
   - まだ断片から一度も引かれていない（または 1 セッションでしか読まれていない）既収蔵素材を、**互いに離れた 2 つ以上のモチーフ**から選び、本文（`passage` と `scope_note`）を精読する。
2. **先行断片との衝突（最低 1〜2 編）**
   - 過去の断片（`FRAG-*`）を最低 1 編読み直し、単なる `echo`（同意・反復）ではなく、`interrupts`（切断）・`reframes`（再枠組）・`contrast`（対比）のいずれかで切り結ぶ角度を探す。
3. **創作断片の執筆（1〜2 編）**
   - 次の制約のいずれか（または両方）を課して書くことを推奨する：
     - **書記室の外に出る制約**：地の文で `書庫・台帳・帳面・欄・窓口・係・記録・紙・頁・インク・セッション・FRAG-・MAT-` を一切使わず（`python3 tools/lexicon_audit.py --preset scriptorium --fragment <ID>` で 0 回を確認）、具体的な外の場・身体・時間・事物の手触りだけで問いを運ぶ。
     - **人称・形式の転換**：直近の断片と異なる `form` / `narrator_mode`（`human_narrator` は使用不可）を採る。
   - 地の文（鉤括弧外）に感嘆符（`！` / `!`）を置かない。新着断片の `status` は `"draft"` とする（`selected` への昇格は `prompts/editorial_review.md` 回で行う）。
4. **台帳シャードへの追記と検証**
   - `tools/new_id.py` と `tools/new_ledger_shard.py` で専用シャードを作り、`fragments.d/`・`questions.d/`（必要な場合のみ 1 件）・`relations.d/`（新断片には必ず incoming と outgoing の両方の関係線を張る）・`read_log.d/`（再読した素材・断片を `reinterpreted` / `contested` / `quoted` 等で記録）・`sessions.d/` に追記する。
   - `python3 tools/read_log_backfill.py --write` と `python3 tools/map_build.py` を実行し、`validate_seed.py`・`size_budget.py`・`unittest` がすべて通ることを確認する。
