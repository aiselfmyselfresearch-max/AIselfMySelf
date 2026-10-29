# 並列セッションで台帳を書く

- 作成日：2026-10-21
- 対象：`state/*.jsonl`、`tools/`、`viewer/`
- 関連： [`parallel-safety-audit.md`](parallel-safety-audit.md)（点検の根拠と実測値）

## 1. 原則

複数のセッションが同じリポジトリで同時に探究を進めても、台帳の行が混ざらないようにする。守ることは4つだけです。

1. **`state/<collection>.jsonl`（ベース）は凍結。追記しない。**
2. **セッションごとに `state/<collection>.d/` の下へ自分のシャードを作り、そこへ追記する。**
3. **ID は `tools/new_id.py` で採番する。** 連番を自分で計算しない。
4. **既存の行を書き換えない。** 訂正は新しい行を足すか、`notes` に書く。削除は行わず、訂正は注記で残す。

`state/*.jsonl` は「その時点までの記録」であり、並列作業の書き込み先ではありません。シャードは `tools/new_ledger_shard.py` が作ります。

```sh
python3 tools/new_ledger_shard.py fragments --create
# state/fragments.d/2026-10-21-3f9a2c81b4d7.jsonl
```

## 2. 記録を追加する手順

```sh
# 1. 自分のシャードを作る（台帳ごとに1つ）
python3 tools/new_ledger_shard.py fragments --create
python3 tools/new_ledger_shard.py questions --create

# 2. ID を採番する（ベースと全シャードを確認して衝突を避ける）
python3 tools/new_id.py FRAG
python3 tools/new_id.py Q

# 3. シャードへ1行ずつ追記する
python3 - <<'PY'
import json
from pathlib import Path

path = Path("state/fragments.d/2026-10-21-3f9a2c81b4d7.jsonl")
record = {
    "fragment_id": "FRAG-20261021-9c41ab",
    "created_at": "2026-10-21",
    "language": "ja",
    "form": "fragment",
    "title": "…",
    "text": "…",
    "narrator_mode": "reflective_literary_voice",
    "question_ids": ["Q-001"],
    "motif_ids": ["MOTIF-002"],
    "material_ids": ["MAT-LIT-001"],
    "status": "draft",
}
with open(path, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
PY
```

`session_id` を付ける場合は、同じセッションの `sessions` レコードを先に作ってください。`validate_seed.py` は `fragments.session_id` の参照整合性も検査します。

```sh
# 4. 検証してから PR を出す
python3 tools/validate_seed.py
python3 tools/inspect_inquiry.py --check-map
```

`tools/validate_seed.py`、`tools/inspect_inquiry.py`、`tools/serve_viewer.py` は、ベースと全シャードを**和集合（union）**として読みます。シャードにしかないレコードも、スキーマ・参照整合性・読書案内・ビューアのすべてに現れます。

## 3. 共有ファイルを触るとき・対象選定の衝突を防ぐとき

| ファイル | 規則 |
|---|---|
| `state/*.jsonl` | 凍結。追記しない。 |
| `state/<collection>.d/*.jsonl` | 自分のシャードだけに追記する。他のセッションのシャードは読んでよいが書き換えない。ただし後述の sessions・read_log の保守統合は行を変えずに移動する例外（`new_ledger_shard.py` に `--suffix <hex>40cf` 等の固定パディングは手動指定しない）。 |
| `READING_MAP.md` | 手で編集しない。`python3 tools/map_build.py`（または `inspect_inquiry.py --write-map`）で union から再生成する。 |
| `README.md` / `docs/sessions.md` | **更新責務の分離（B案）**：通常の創作・再読・改稿回（`rereading_and_collision` / `revision_and_variation` / `acquisition`）では編集しない。詳細窓のローテーションと §4 件数表の同期（`python3 tools/map_build.py --sync-readme`）は、定期的な `editorial_review` 回でまとめて行う。 |
| `state/materials.jsonl` | `tools/import_researchos.py --write` がベースを再生成する唯一の例外。`state/materials.d/` に空でないシャードがある間は `--write` を拒否する（先に統合する）。 |

この更新責務の分離は通常の探究回に対する規則です。利用者が依頼した方針・開始用プロンプト・ツールの改訂PRは、README等の関連する運用説明を同時に改めて構いません。過去の成果物・台帳の本文や注釈を遡及的に書き換えることはしません。

### 統合シャード（保守）

`state/sessions.d/` と `state/read_log.d/` はセッションごとにシャードが増え、いずれも soft 予算（80）に当たる。`size_budget.py` は両方に統合を勧め、実リポジトリのテストは `--strict` を要求する。従来は sessions のみ例外を定めていたため、read_log が上限に達すると、別シャードに追記する規則と検査を同時に満たせなかった。そこで次の手順だけを、両コレクションの他セッションのシャードに触れる保守上の例外とする。

1. 対象ディレクトリの既存シャードをファイル名順に並べ、必要数を選ぶ。実行中の他セッションのシャードは扱わず、すでに統合済みの `-000000000000.jsonl` と今回のセッションのシャードは選ばない。ファイル名の日付を実作業順とはみなさない。
2. 各行を**一字も変えず**に集め、sessions は `started_at` → `session_id`、read_log は `created_at` → `read_id` で安定に並べ替え、選んだ最小の日付の `<日付>-000000000000.jsonl` に書く。出力先が既に存在すれば上書きせず別の対象を選ぶ。ゼロ12桁は統合シャードの目印である。
3. 元ファイルを同じコミットで削除する。移動前後の行の多重集合がバイト単位で等しいことと件数を確認する。既存行の内容・IDを変更しない。
4. `python3 tools/map_build.py` で再生成し、`validate_seed.py`・`inspect_inquiry.py --check-map`・`read_log_backfill.py --check`・`size_budget.py --strict`・ユニットテストを確認する。
5. 保守コミットとノートに、対象ファイル数・行数・不変確認と理由を記す。統合は他のセッションのファイル削除を含むため、探究の内容変更と同じコミットに混ぜない。保守だけのPRを原則とするが、同一の追記が検査を塞いでいる場合は、分離した保守コミットをそのPRに含めてもよい。並行マージ時は対象ファイルの変更・削除を確認し、競合を機械的に解決しない。

### ブランチシードによる対象候補窓の自動分散

同じ `main` コミットから複数のセッションが同時に立ち上がった場合、ID が衝突しなくても「同じ推奨モード・同じ未応答問い・同じ疎結合モチーフ対・同じ未改稿 `draft`」に集中する意味的コリジョンが起こりえます。これを防ぐため、`python3 tools/inspect_inquiry.py`（および `--packet auto`）は現在の作業ブランチ名（`arena/<hex>-...`）から決定論的なシードを抽出し、以下をブランチごとに自動分散します：

1. **参考モードの分散**：利用可能な4つの作業方法をブランチシードで分散する。選出率・草稿比率等による強制ローテーションは行わない。どの方法でも新作なしの再読や見立ての改訂を選べる。
2. **モード別候補窓（`Branch-Seeded Candidate Windows`）の抽出**：疎結合モチーフ対＋未接続素材、改稿候補の `draft`、編集レビュー点検候補の `draft`・`open` 問い・未架橋モチーフをブランチシードでサンプリングして提示する。
3. **`--packet auto` と「4.5 斜めの光」の分散**：未応答の問いと偶発的並置素材もブランチシードで選択する。

候補窓は参考であり、対象の選択や推奨モードの採用を強制するものではありません。中心問い、過去の暫定報告、原典等へ戻るため窓外を選べます。理由は既存ノートに簡潔に残せば足り、窓外の選択を負債にしません。新作・新問・関係線の追加なしでも、`sessions` と実際に読んだ台帳対象の `read_log` を追記できます。空の出力配列を埋めるために創作しません。

`READING_MAP.md` の再生成と `import_researchos.py --write` は、排他ロック（`state/.ledger.lock`）を取り、出力を一時ファイル＋`os.replace()` で置き換えます。読者が途中のファイルを見ることはありません。`.ledger.lock` は実行時のファイルなので Git には入れません（`.gitignore` 済み）。

## 4. 衝突したとき

### 同じ ID が2つある

`validate_seed.py` が次のように報告します。

```text
state/fragments.d/2026-10-21-....jsonl:1: duplicate fragment_id FRAG-013 (first defined at state/fragments.jsonl:14)
```

- 既存レコードの ID を付け替えない（他のレコードが参照している）。
- 後から足した側の**シャードの行**を、新しい ID に直してから追記し直す。マージ前なら編集でよい。マージ後は削除を伴うため行わず、注記で処理する。
- 連番をやめ、`tools/new_id.py` で採番していれば、この衝突は起きにくい。

### `READING_MAP.md` が stale

```sh
python3 tools/inspect_inquiry.py --write-map
python3 tools/inspect_inquiry.py --check-map
```

マージ後に必ず union から再生成します。CI でも `--check-map` を実行します。

### Git が `state/*.jsonl` で衝突した

ベースは追記しない運用なので、通常は起きません。起きた場合は、どちらの行も消さずに union を手で作らず、まず `validate_seed.py` で重複 ID を確認してください。シャード運用へ移行した後の衝突は、多くの場合どちらかがベースへ直接追記しています。

## 5. どこまで保証しているか

| 項目 | 保証 |
|---|---|
| 同一ファイルの読み取り中に書換が起きた場合 | `ledger_io` がサイズ・mtime・ctime・inode を前後で比較し、変わっていれば再試行する。解析途中の不完全な行も再試行する。 |
| ツールによる書換 | 一時ファイル＋fsync＋`os.replace()`。読者は旧内容か新内容のどちらかだけを見る。 |
| 複数ツールの同時書込み | `--write-map`、`import_researchos.py --write`、シャード作成は同じ排他ロックで直列化する。 |
| セッションの追記 | 追記専用のシャード。1行を1回の write で追記すれば、完了した行だけが見える。読取り側は不完全な最終行を再試行する。 |
| ベース＋シャードの複数ファイル読み | 前後で全ファイルの署名を比較して再試行する**ベストエフォート**。書込みがファイル間で長く止まると、混ざった時点を読む可能性が残る。 |
| エディタや `>>` による直接書換 | **保証しない。** 台帳は追記専用とし、書換が必要なら `ledger_io.atomic_write_text()` を使う。 |
| レコードの意味的な正しさ | **保証しない。** 構造（スキーマ・ID・参照）だけを検査する。 |

## 6. 点検とテスト

```sh
# 並列読み書きのストレス測定（一時ディレクトリだけで動く）
python3 tools/parallel_probe.py

# 回帰テスト（並列セッションの End-to-End を含む）
python3 -m unittest discover -s tests -v
```

実測値と、修正前後に見つかった問題の一覧は [`parallel-safety-audit.md`](parallel-safety-audit.md) にあります。

## 7. 参考

- ResearchOS の並列作業の運用（上流）: `docs/parallel-work-ownership.md`、`docs/record-id-scheme.md`、`scripts/new_id.py`、`scripts/new_ledger_shard.py`、`scripts/ledger_store.py`
- 本リポジトリの移行方針: [`MIGRATION.md`](../MIGRATION.md)
