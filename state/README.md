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

## 並列セッション（シャード）

複数のセッションが同時に探究を進める場合、`state/*.jsonl` は凍結ベースとして触らず、セッションごとのシャードへ追記します。

```sh
python3 tools/new_ledger_shard.py fragments --create
# state/fragments.d/2026-10-21-3f9a2c81b4d7.jsonl
python3 tools/new_id.py FRAG
```

- シャードの名前は `YYYY-MM-DD-<12桁hex>.jsonl`。`tools/new_ledger_shard.py` が `O_EXCL` で作り、既存ファイルを上書きしません。
- ID は `tools/new_id.py` で採番します（`PREFIX-YYYYMMDD-xxxxxx`）。連番を自分で計算すると並列で衝突します。
- 追記のみ。既存レコードの削除・書き換えはしません。
- `validate_seed.py`、`inspect_inquiry.py`、`serve_viewer.py` は、ベースと全シャードの**和集合**を読みます。
- `state/materials.d/` に空でないシャードファイルがある間は `tools/import_researchos.py --write` を実行できません（素材ベースを再生成するため）。先に統合してください。

運用の詳細は [`docs/parallel-work.md`](../docs/parallel-work.md)、点検結果は [`docs/parallel-safety-audit.md`](../docs/parallel-safety-audit.md) を参照してください。
