# 状態台帳

`*.jsonl` は一行一レコード（UTF-8、キー昇順ソート推奨）です。

- `questions.jsonl` / `motifs.jsonl`：開かれた問いの系譜と、問いを横断する6つのモチーフ。
- `materials.jsonl`：`ResearchOS` から選定した AI 研究抜粋（`research_excerpt`）と、本リポジトリで追加した哲学・文学原典（`literary_text`）。`tools/import_researchos.py --write` を実行しても、本リポジトリ側で追加したローカル素材は保持されます。
- `fragments.jsonl` / `relations.jsonl` / `sessions.jsonl`：各セッションで生成・選出された文芸断片、解釈的関係、セッション履歴。

台帳を更新した後は、必ず以下の2つを実行して整合性と読書案内を同期してください。

```sh
python3 tools/validate_seed.py
python3 tools/inspect_inquiry.py --write-map
```
