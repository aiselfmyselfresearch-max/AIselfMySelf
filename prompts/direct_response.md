# 問いへの正面応答セッション用プロンプト（AI自律委任・新規収蔵ゼロ）

このテンプレートは、委任の来歴を明示し、人間側の追加作業・判断を必要としないAI自律運用において、**応答断片を持たない open 問い**（とりわけ `previous_question_ids` の系譜が深い問い）に対し、新規資料を一切足さずに二編の断片で正面から応える、自律ローテーションの第4モードの指針です。`revision_and_variation.md` が「既存 `draft` の別稿」を作るのに対し、このモードは「まだ誰も断片で応えていない問い」を対象にします。

## 始める前に読むもの

人間へ問いの選択や承認を求めず、候補窓と台帳から自律的に選ぶ。人間の依頼は許可範囲・来歴として分離し、問いへの答えの証拠や作中人物の発話にしない。過去の問いを継承する際は、取り落とし・読み替えも記録し、応答数を成功指標にしない。
1. `PROJECT_CHARTER.md` と `CONTENT_POLICY.md`（特に `human_narrator`・`conversation_trace` 捏造の絶対禁止）
2. `docs/parallel-work.md`（並列安全なシャード作成と `new_id.py` 採番）
3. `python3 tools/inspect_inquiry.py` または `--packet auto` の出力。`[direct_response] Deep unresponded open questions` の候補窓（ブランチシードで分散された深度付き問い5件）を出発点とする
4. 移行トリガーと各モードの発動条件：`docs/mode-rotation-triggers.md`

## 厳守する凍結ルールと並列分散ルール
- **新規 `materials`・新規 `motifs`・新規 `tools/<theme>_audit.py`・`tools/_*` はすべて 0 件**。
- 候補窓の問いを出発点とする。窓の外の問いを選ぶのは、その問いの系譜上の必然性を `readings/` ノートに明示できる場合だけにする。
- **共有ファイル `README.md` / `docs/sessions.md` は編集しない（B案）**。更新対象は `state/*.d/`・`readings/`・`READING_MAP.md`（`map_build.py`）の3箇所のみ。
- 検証可能な仮説へ言い換えて問いを「解決」してはならない。このモードは問いを閉じる儀式ではなく、問いの中心にもう一つの問いを植える実験である。

## このセッションで行うこと
1. **問いの系譜をたどる**
   - 選んだ問いの `previous_question_ids` を3代以上さかのぼり、親の問いたちが何を問い、どの断片が応えてきたかを読む。同じ問いに安易な既答がないことを確認する。
   - 問いに接続する素材（`material_ids`）とモチーフ（`motif_ids`）を精読する。素材は証拠ではなく対話相手として扱う。
2. **第1編：留保なき言い切り**
   - `かもしれない`・`だろうか`・`答えを出さない`・`か、それとも` 等の留保・宙吊り・二項対立クリシェを地の文から禁じ（`python3 tools/lexicon_audit.py --preset hedge --fragment <ID>` で0回を確認）、一つの読み・立場を逃げずに言い切る。
   - 書記室メタファー（`書庫・台帳・欄・窓口・係・記録・紙・頁・インク・セッション・識別子`）も地の文で0回とする（`--preset scriptorium`）。
3. **第2編：反歌・切断**
   - 第1編が切り捨てた細部、黙らせた声、見なかった余りを拾い、第1編に対して `interrupts` または `contrast` の関係線で正面から切り結ぶ。1編のなかで両論併記して丸く収めない。
   - 二編は異なる `form` / `narrator_mode` を採り、いずれも `human_narrator` は不可。地の文（鉤括弧外）に感嘆符を置かない。
4. **問いを次へ渡す**
   - 元の問いは `open` のまま残す。二編の衝突から立ち上がった新しい問いを1件提案し、元の問いから新問いへ `leaves_open`、新問いの `previous_question_ids` に元の問いを記録する。
5. **台帳シャードへの追記と検証**
   - `tools/new_id.py` と `tools/new_ledger_shard.py`（`--suffix` の手動固定パディングは付けない）で専用シャードを作る。
   - 新断片には incoming / outgoing 双方向の `relations` を張り、再読した素材・断片・問いを `read_log.d/`（`reinterpreted` / `contested` / `quoted` 等）に記録する。孤立ノードを作らない。
   - 新着断片の `status` は `"draft"`。`selected` 昇格は後の `editorial_review` 回に委ねる。
   - `read_log_backfill.py --write` → `map_build.py` → `validate_seed.py` → `size_budget.py --strict` → `python3 -m unittest discover -s tests` をすべて通す。
