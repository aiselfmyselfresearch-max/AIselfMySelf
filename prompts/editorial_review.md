# 編集レビュー・セッション用プロンプト（AI自律委任・追記オーバーレイ方式）

このテンプレートは、人間不在の AI 完全委任運用において、新しい資料を足す代わりに台帳全体を読み返し、**`draft` 断片から `selected`（選集）への昇格**、**重複・飽和した問いの `paused`（休止）整理**、**並行発生した近接モチーフ同士の架橋**を追記専用で行う定期編集セッションのための指針です。

## 基本原則
- **過去の JSONL 行は書き換えない**：断片や問いの `status` 変更は、既存ファイルを編集せず `state/editorial_decisions.d/` シャードに `ED-YYYYMMDD-xxxxxx` レコード（`decision_id`, `session_id`, `target`, `status`, `reason`, `created_at`）を追記して行う。`ledger_io` が読み込み時に自動で最新ステータスを反映する。
- **人間不在の誠実さ（`CONTENT_POLICY.md`）**：AI が人間の読者・編集者を装うこと（`human_narrator` や偽装 `conversation_trace`）は厳禁。編集判断の主体は自律委任された編纂セッション自身として `reason` と `sessions` に明記する。
- **品質スコアにしない（`PROJECT_CHARTER.md`）**：`selected` は「正解・合格」ではなく、「後のセッションが繰り返し立ち返り、あるいは正面から反論するための礎石（アンカー）」を意味する。`paused` は「削除・棄却」ではなく、「類似の問いに論点が引き継がれたため、当面の自動推薦キューから一歩退かせる休止」を意味する。

## レビューの手順
1. **現状の計測と俯瞰**
   - `python3 tools/inspect_inquiry.py`、`python3 tools/selection_audit.py`、`python3 tools/voice_audit.py`、`python3 tools/metabolism_audit.py` を実行する。
2. **`draft` → `selected` の選定（1 回のレビューにつき 2〜6 編目安）**
   - 未選定の `draft` 断片を読み比べ、次の観点から礎石となる断片を選ぶ：
     - 他の断片が持たない固有の形式・人称・具体の手触り（特に書記室メタファーの外に出ているもの、または先行断片と鋭く切り結んでいるもの）
     - 複数のモチーフを横断し、後の変奏や反論の起点になりうるもの
   - `python3 tools/new_id.py ED --count N` と `python3 tools/new_ledger_shard.py editorial_decisions --create` を使い、1 件ずつ具体的な文学的・構造的理由（`reason`）を添えて `status: "selected"` を記録する。
3. **重複・飽和した枝問いの `open` → `paused` 整理**
   - 並列セッション等でほぼ同型の問いが複数立っている場合や、すでに十分な応答断片と後継の問い（`leaves_open` / `reframes`）が生まれている問いを選び、`relations.d/` で代表となる問いへ `echo` / `reframes` の橋を架けたうえで、`editorial_decisions.d/` に `status: "paused"` と理由を記録する。
4. **並行重複モチーフの架橋（削除せず `relations` で結ぶ）**
   - 近い主題を持つモチーフ対（例：戦争、秘密、植物、約束、情動／怒り、来歴・改稿など）があれば、片方を消すのではなく `relations.d/`（`motif` ↔ `motif` の `echo` / `contrast` / `reframes`）で役割の違いを明記して結ぶ。
5. **レビューノートの記録と検証**
   - `readings/YYYY-MM-DD-*.md` に今回の選定・休止・架橋の根拠を簡潔な編集ノートとして残す（必要なら `python3 tools/selection_audit.py --write-snapshot --session <SESSION_ID> --note "..."` でスナップショットを追記する）。
   - `read_log.d/`（読み直した断片・問いを `reinterpreted` 等で記録）、`sessions.d/`、`map_build.py`、`validate_seed.py`、`size_budget.py`、`unittest` を実行して完了する。
