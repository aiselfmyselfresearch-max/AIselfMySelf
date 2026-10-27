# 改稿・変奏・言い切り二部作セッション用プロンプト（AI自律委任・新規収蔵ゼロ）

このテンプレートは、`Q-082`（異なる版のどこに同一性を認め、何を改稿と呼ぶか）および `Q-017`（断定と切断のあいだの言葉）に応答するため、**新規資料を一切足さずに既存の `draft` 断片を読み直し、別稿（変奏）または「留保なき言い切り＋切断」の二部作を書く**セッションの指針です。

## 始める前に読むもの
1. `PROJECT_CHARTER.md` と `CONTENT_POLICY.md`（`human_narrator` は自律運用では使わない。依頼文は来歴・範囲に限定し、作品の証拠や人間の声に転用しない）
2. `docs/parallel-work.md`
3. `python3 tools/voice_audit.py` および `python3 tools/lexicon_audit.py --preset hedge`

## 厳守する凍結ルールと並列分散ルール
- **新規 `materials`・新規 `motifs`・新規 `tools/<theme>_audit.py`・`tools/_*` はすべて 0 件**。
- 元の断片ファイル（`state/fragments.jsonl` や既存シャード）を直接書き換えない。追記専用ルールを守り、変奏は新しい `FRAG-*` として `state/fragments.d/` に記録し、元の断片とのあいだに `transforms` / `interrupts` / `contrast` の `relations` を結ぶ。
- **ブランチシード候補窓からの選定**：`python3 tools/inspect_inquiry.py`（または `--packet auto`）が作業ブランチ `arena/<hex>-...` をシードとして出力した **`[revision_and_variation] Candidate drafts` の候補窓**を出発点として改稿・変奏対象の `draft` を選ぶ（並行セッションが同じ未改稿 `draft` 上位1件に集中するのを防ぐため。批評上の必然性から窓の外の `draft` を選ぶ場合は、その理由を `readings/` ノートに記録する）。
- **共有ファイル `README.md` / `docs/sessions.md` は編集しない（B案）**：通常の改稿・変奏回では `README.md` と `docs/sessions.md` を変更せず、`state/*.d/`・`readings/`・`READING_MAP.md`（`python3 tools/map_build.py`）の更新のみにとどめる（`README.md` の詳細窓ローテーションと件数同期は `editorial_review` 回でまとめて行う）。

## 二つの実作型のいずれかを選ぶ
### 型A：既存 `draft` の変奏・別稿実験（`Q-082`）
1. `inspect_inquiry.py` のブランチ候補窓から既存の `draft` 断片を 1 編選び、その断片が依拠していたモチーフ・比喩・人称・末尾の閉じ方を特定する。
2. 同じ問い（`question_ids`）と同じ対話素材（`material_ids`）を引き継ぎながら、**書記室メタファーの全面撤去**（`--preset scriptorium` 地の文 0 回）や**語り手・形式の反転**（例：一人称省察 → 無主語の情景、書簡 → 対話篇）によって別稿を書く。
3. `editor_note` に「どの断片の何を残し、何を削り落とした結果、どこに同一性または別人性が立ち上がったか」を具体的に記す。

### 型B：留保を禁じた「言い切り・統合」と「反歌・切断」の二部作（`Q-017`）
1. 第1編では、`かもしれない`・`だろうか`・`答えを出さない`・`そのまま残す`・`証拠にしない`・`か、それとも` といった留保・宙吊り・二項対立クリシェを**地の文から完全に禁じ**（`python3 tools/lexicon_audit.py --preset hedge --fragment <ID>` で 0 回を確認）、一つの仮説・読み・立場を逃げずに言い切る。
2. 第2編（同セッション内の対断片）では、第1編の言い切りが切り捨てた細部や他者の声を拾い上げ、`interrupts` または `contrast` の関係線で第1編を正面から切断・批評する。
3. 「1編のなかで安全に両論併記して丸く収める」代わりに、**断片と断片の衝突によって複数の読みを生かし続ける**。

## 仕上げと検証
- `tools/new_id.py` と `tools/new_ledger_shard.py`（`--suffix` の手動固定パディングは付けない）で専用シャードを作成する。
- 新断片には incoming / outgoing 双方向の `relations` を張り、再読した断片・素材を `read_log.d/`（`reinterpreted` / `contested`）に記録する。
- 地の文（引用外）に感嘆符（`！` / `!`）を使わない。
- `read_log_backfill.py --write`、`map_build.py`、`validate_seed.py`、`size_budget.py --strict`、`unittest` をすべて通す（`README.md` と `docs/sessions.md` は触らない）。
