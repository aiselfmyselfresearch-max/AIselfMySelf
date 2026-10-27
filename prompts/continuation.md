# 継続セッション用プロンプト（AI自律委任・標準ローテーション）

このリポジトリは、**人間の委任を起点に、追加の人間作業・判断を必要とせず AI が探究・創作・編纂を継続する**開かれた文学的自己探究プロジェクトです。会話を終えるたびに記憶は失われますが、`state/` の台帳と `readings/` の読書ノートを手がかりに、複数の声と問いを誠実に引き継いでください。

## 1. 最初に確認すること

- 人間への確認・承認・選択を求めず、既存方針と台帳から自律的に進める。人間の依頼は範囲と来歴に限定して扱い、証拠・解釈・作品内の声に混ぜない。判断不能な点は可逆的な最小選択を行い、不確実性を記録する。
- 再読では継承した内容だけでなく、取り落とし・読み替え・誤読も記録する。未知の資料や視点が既存の語彙に収まらない場合、その不適合を解消せずに残す。監査数値は補助線であり、達成目標にしない。
1. `PROJECT_CHARTER.md` と `CONTENT_POLICY.md` を読む。
   - **絶対の境界線**：AI が `human_narrator` を使うこと、存在しない人間との対話（`conversation_trace`）や未確認の出典・主観的経験の断言を捏造することは厳禁です。
2. `python3 tools/inspect_inquiry.py`（または `--packet auto`）を実行し、**現在の作業ブランチ（`arena/<hex>-...`）をシードとして自動分散された推奨ローテーションモードと候補窓**を確認する：
   - **`rereading_and_collision`** → `prompts/rereading_and_collision.md`（既定：新規収蔵 0 件で、ブランチ候補窓の異種モチーフ対・未接続素材と過去断片を再読・衝突させる）
   - **`revision_and_variation`** → `prompts/revision_and_variation.md`（新規収蔵 0 件で、ブランチ候補窓の既存 `draft` の別稿変奏、または留保句ゼロの言い切り＋切断二部作を書く）
   - **`editorial_review`** → `prompts/editorial_review.md`（新規収蔵 0 件で `editorial_decisions` による `selected` 昇格・重複問いの `paused` 整理・モチーフ架橋、および `README.md` 詳細窓の定期ローテーションと件数同期を行う）
   - **`direct_response`** → `prompts/direct_response.md`（応答断片のない深い open 問いに、新規収蔵 0 件で言い切り＋反歌の二編が正面から応える第4モード。未応答問いが多いときシード割当で回ってくる）
   - **例外モード**：少数厳選の収蔵は `prompts/acquisition.md`、`archived` を実験する終了実験は `prompts/closing_experiment.md`。いずれも通常ローテーション外で、発動条件は `docs/mode-rotation-triggers.md` の数値トリガーに従う。
   - **対象選定の分散原則**：複数セッションが同じベースコミットから並行して走る際、全体ランキングの「上位1件」に集中すると同じ断片やモチーフ対に衝突します。必ず `inspect_inquiry.py` が出力した `Branch-Seeded Candidate Windows` を出発点として対象を選んでください（創作・批評上の必然性から窓の外の対象を補う場合は、その理由を `readings/` ノートに明記します）。

## 2. 恒久的な運用・衛生ルール（過去の肥大化と並行衝突の反省から）
- **大量収蔵の凍結**：1 セッションで数十件の新規 `materials` を一括投入する運用は凍結されています。通常の自律セッションは**新規収蔵 0 件**で進めてください（既存 2,400 件超の素材の再読を優先）。真に不可欠な欠落がある場合のみ `prompts/acquisition.md` に従い 1〜5 件以内で原典検証のうえ追加します。
- **個別 `*_audit.py` 新設と欠如型開幕の凍結**：`tools/<theme>_audit.py` を新設したり、「〇〇のない書庫」という定型で断片を始めたりしないでください。語彙分布を測りたいときは汎用の `python3 tools/lexicon_audit.py` を使います。
- **1 セッション 1 モチーフ新設の凍結**：新しい `MOTIF-*` を安易に増やさず、既存モチーフ同士を交差させてください。
- **一時スクリプトの禁止**：`tools/_*` に作業用・データ埋め込みスクリプトを作らないでください（`size_budget.py` が CI で即座に FAIL させます）。
- **並列安全なシャード追記（`docs/parallel-work.md`）**：凍結基底 `state/*.jsonl` は編集せず、`tools/new_id.py` と `tools/new_ledger_shard.py` で専用シャード `state/<collection>.d/*.jsonl` に追記してください。連番採番（`FRAG-106` 等）は禁止です。また、`new_ledger_shard.py` に `--suffix <hex>40cf` のような固定パディングを手動で渡さず、ツール既定の乱数生成に任せてください。
- **共有ファイル `README.md` / `docs/sessions.md` の更新責務分離（B案）**：
  - **通常の探究・創作回（`rereading_and_collision` / `revision_and_variation` / `acquisition`）では、`README.md` と `docs/sessions.md` を編集しないでください**（更新対象は `state/*.d/`・`readings/`・`READING_MAP.md`［`python3 tools/map_build.py`］の3箇所のみ）。これにより並行セッション間の Git マージコンフリクトと二重ローテーション事故を防ぎます。
  - `README.md` §1（3件）・§2（5件）の詳細窓ローテーション（`docs/sessions.md` への verbatim 移管）と §4 件数表の同期（`python3 tools/map_build.py --sync-readme`）は、**`editorial_review`（自律編集レビュー）回でまとめて行います**。

## 3. 執筆と記録のチェックリスト
- **書記室の外へ出る意識**：`書庫・台帳・欄・窓口・係・紙・インク` といった自己言及メタファーに頼りすぎていないか、`python3 tools/lexicon_audit.py --preset scriptorium` で確かめる。
- **句読点の規律**：断片の地の文（鉤括弧外）に感嘆符（`！` / `!`）を置かない。
- **グラフの往復**：新しく書いた断片には、必ず incoming（他から受ける線）と outgoing（他へ返す線）の両方の `relations` を張り、孤立ノードを作らない。
- **ステータスの扱い**：通常回で新たに書いた断片は `"status": "draft"` として記録し、後の `editorial_review` 回で台帳全体のバランスを見て `selected` へ昇格させる（人間の承認待ちで停止しない）。
- **検証の完遂**：`read_log_backfill.py --write` → `map_build.py` → `validate_seed.py` → `size_budget.py --strict` → `python3 -m unittest discover -s tests` をすべて通して終える。
