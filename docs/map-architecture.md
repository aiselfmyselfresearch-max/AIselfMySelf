# 読書案内データのアーキテクチャ — 増加に耐える4層の設計

`READING_MAP.md` が 37MB・71,909行に達し、チャット・PR・clone を重くしていた問題（2026-10-24 診定）に対する設計変更の記録。調査した外部の事例と、このリポジトリへの適用をまとめる。

## 1. 何が問題だったか

| 観測 | 計測値（変更前） |
|---|---|
| `READING_MAP.md` | 36,916,878 bytes / 71,909 行 |
| うち「開かれた問いの系譜」セクション | 66,342 行（**全体の 92%**） |
| 原因 | 問いの DAG（`previous_question_ids` は多対多）を全文付きツリーとして展開しており、問い 1 件の本文が**パスの数だけ繰り返し**出力されていた |
| 台帳そのもの（`state/`） | 3.2MB — 本体は軽い |

## 2. 調査した事例と結論

### 2.1 GitHub での巨大ファイル・生成物の扱い

- GitHub 公式は「リポジトリは 1GB 以下が望ましい（5GB 以下を強く推奨）」とし、**プログラムで生成されるファイルは Git の外（object storage 等）に置く**よう明示している
  （[Repository limits - GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits)、[About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)）。
- 単一オブジェクトの推奨上限は 1MB（強制は 100MB、50MB 超で警告）。
- **Git LFS は不向き**。LFS は「コミットと対応するバイナリ」のための仕組みであり、「毎回生成されるレポート」「毎日全文書き換えされるファイル」は Git の外に置くべきケースとして挙げられている
  （[Git LFS Guide](https://www.fast.io/resources/github-lfs-guide/)）。
- **GitHub Releases / Actions artifacts** が生成物の配布に使われる（Release asset は最大 2GB、Actions artifact は最大 5GB・保存 90 日）
  （[community discussion #171247](https://github.com/orgs/community/discussions/171247)）。

### 2.2 大規模データの分割（パーティショニング／シャーディング）

- **レンジ分割**は順序付きキーに有効で、末尾への追記（append-only）と相性がよい。新規レコードは末尾シャードにだけ落ち、既存シャードは不変になる
  （[Azure Sharding Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)、[Data partitioning strategies](https://learn.microsoft.com/en-us/azure/architecture/best-practices/data-partitioning-strategies)）。
- シャードキーは**安定**した値を選ぶこと（変わりうる値をキーにするとデータ移動が発生する）。台帳の挿入順は不変なのでキーに適する。
- シャードを引くための**セカンダリ索引**（Index Table / shard map）を別に持つ。
- 不変・append-only なパーティションは分析・再生成に向く。

## 3. 採用した4層構造

```
Tier 1  state/            台帳の正本（append-only JSONL シャード・git 管理・約3MB）
Tier 2  READING_MAP.md    小型索引（決定的生成・git 管理・約250KB・警告閾値2MB）
Tier 3  map/              全文生成文書（レンジ分割シャード・git 管理外・約2.4MB）
Tier 4  CI artifact       .github/workflows/map.yml が map/ を毎回 build して配布
```

### Tier 1 — 台帳（正本）

`state/*.jsonl` ＋ `state/*.d/*.jsonl` の追記専用シャード。既存のままで、これが唯一の source of truth。

### Tier 2 — 追跡される小型索引（`READING_MAP.md`）

サマリー・モチーフ表・**問いの DAG 索引（各行1問・本文抜粋100字・親子ID）**・断片一覧・素材一覧・セッション一覧・関係の種類別件数・シャード目録。
本文は持たない。サイズは 2MB を超えたら警告（`map_build.py`）。

### Tier 3 — 全文シャード（`map/`・git 管理外）

| ファイル | 内容 | 分割単位 |
|---|---|---|
| `00-overview.md` | 総覧・モチーフ全文 | — |
| `10-question-index.md` | 問いの DAG（ID・親子・抜粋） | — |
| `11-question-bodies-NN.md` | 問い本文（**各1回だけ**） | 50 件 |
| `20-fragments-NN.md` | 断片アンソロジー全文 | 20 編 |
| `30/31/32-materials-*.md` | 素材カタログ全文 | 100 件 |
| `40-relations-NN.md` | 解釈的関係の全表 | 500 件 |
| `50-sessions-NN.md` | セッション年譜 | 50 件 |
| `manifest.json` | ID→シャード対応表・sha256・件数・バイト | — |

- **シャードキー**：台帳の挿入順（安定・不変）。追加されたレコードは末尾シャードに入るため、再生成の差分は末尾だけ。
- **セカンダリ索引**：`manifest.json`（sha256 付き）と Tier 2 索引の ID 列。
- 写しは `tools/map_build.py` が `state/.ledger.lock` の排他ロックと `ledger_io.atomic_write_text`（一時ファイル＋`os.replace`）で行う。

### Tier 4 — git の外での配布

`.github/workflows/map.yml` が `main` への push と手動実行で `map/` を build し、Actions artifact `reading-map`（90日保持）としてアップロードする。Git 履歴は一切増えない。

## 4. 効果

| 指標 | 変更前 | 変更後 |
|---|---:|---:|
| git 追跡の生成物 | 36.9 MB | **0.24 MB**（99.3% 減） |
| 問い本文の重複 | パス数だけ重複（最大数百回） | **各1回** |
| 再生成の差分 | 全体書き換え気味 | 末尾シャードのみ |
| 10万件規模への拡張 | 1ファイルが肥大化し続ける | 分割単位ごとに追加、索引は O(n) の1行/件 |

## 5. 運用コマンド

```sh
python3 tools/map_build.py                 # map/ と READING_MAP.md を再生成
python3 tools/map_build.py --check         # 索引が台帳と一致するか（CI も同じ）
python3 tools/map_build.py --report        # シャードのサイズ報告
python3 tools/map_build.py --sync-readme   # README.md §1/§2/§4 の件数表を台帳と同期（editorial_review 回用）
python3 tools/inspect_inquiry.py --write-map   # map_build.py への委譲（互換）
python3 tools/inspect_inquiry.py --check-map   # 同上
```

## 6. 留保

- `map/` は git 管理外のため、clone だけでは全文がない。`--write-map` か CI artifact で取得する。
- `--check` は追跡している索引のみを検査する（`map/` は untracked のため対象外）。
- 過去のコミットに残った 37MB 級の `READING_MAP.md` blob がサーバ側履歴に残っている。clone は shallow で軽いが、完全履歴を軽くしたい場合は `git filter-repo` による履歴書き換えが要る（破壊的なので既定では行わない）。

## 7. 成長予算とローテーション（A1・A2・B3）

READING_MAP.md の事故は「単一ファイルが全成長を吸収する」ことの結果だった。同じ病が README と台帳モノリスに再発しないよう、予算と移行手順を置く。

### 7.1 サイズ予算（`tools/size_budget.py`）

以下の表は初期設計時の値です。現在の上限と保守条件の正本は `tools/size_budget.py` とその実行結果です。2026-10-28の探究方針改訂は、これらの技術予算を緩和していません。作業モードの選択・語彙・辺数は別であり、数値による探究上の発動義務は廃止しました（[`mode-rotation-triggers.md`](mode-rotation-triggers.md)）。

| 対象 | soft（WARN） | hard（CI 停止） | soft 超過時の移行 |
|---|---:|---:|---|
| `README.md` | 150 KB | 300 KB | 詳細窓を維持し、超過分を `docs/sessions.md` へ verbatim ローテーション |
| `READING_MAP.md` | 2 MB | 5 MB | map_build の 2MB 警告と同じ。超えたら索引の表を分割（§3 Tier 2 の拡張） |
| `state/<collection>.jsonl`（各モノリス） | 5 MB | 10 MB | モノリスを生成物化し、`state/*.d/` シャードを正本に切り替える（§3 Tier 1 の移行） |
| git pack（参考値） | 500 MB | 1GB（指針） | §6 の留保（filter-repo）の実行を AI の判断で行う |

`python3 tools/size_budget.py` が各ファイルを点検する（`--strict` は WARN も失敗）。CI（`ci.yml`）は hard 超過で停止する。リポジトリ全体は GitHub の指針（<1GB 推奨）を超えるまでは現状維持。

### 7.2 README ローテーション規約（B案：編集レビュー回への集約）

記憶の削除ではなく**移動**である。README は入口であり全量ではない。また、並行セッションが毎回 `README.md` と `docs/sessions.md` を編集して Git コンフリクトや二重移管を起こすのを防ぐため、ローテーションと件数同期は **B案（`editorial_review` 回への集約）** で運用する。

1. **通常回では編集しない**：通常の創作・再読・改稿回（`rereading_and_collision` / `revision_and_variation` / `acquisition`）では `README.md` と `docs/sessions.md` を変更せず、`state/*.d/`・`readings/`・`READING_MAP.md`（`python3 tools/map_build.py`）のみを更新する。
2. **詳細窓のサイズと移管手順**：到達点 bullet の詳細窓は **3件**、注釈付き報告エントリの詳細窓は **5件**。`editorial_review` 回で窓を入れ替えるときは、押し出される古い項目を `docs/sessions.md` の該当節へ **一字一句変えずに**移す。
3. **件数表の自動同期**：`editorial_review` 回では `python3 tools/map_build.py --sync-readme` を実行し、`README.md` §1・§2 の総数表記および §4 の件数表を台帳と `readings/` の実測値に同期する。
4. `docs/sessions.md` も追記専用。既存行の書き換え・要約・圧縮をしない（訂正は新しい注記）。
5. WARN はこの操作の合図。hard 超過は移行が済むまでマージしない。

### 7.3 読み痕跡 `read_log`（B3）

台帳は「何を集めたか」（素材）と「どう解釈したか」（関係）を持つが、「どの記録を・どのセッションが・どう読み返したか」の網羅的痕跡を持たなかった。`state/read_log.jsonl` はそれを記録する追記専用コレクションで、「記録を読み返して続きを語る AI」の**読み返し**そのものを測定可能にする。

- 各行は (session, target, reading, note)。`reading` は quoted／summarized／interpreted／reinterpreted／contested／used_as_context／counted。
- 精選された解釈は関係へ、本文は断片・報告へ置く（read_log は痕跡の索引であり、解釈の置き場ではない）。
- `tools/read_log_backfill.py` が確定できる部分（各セッションの `context_material_ids`）を機械的に転記し、`--check` で網羅を CI が検査する。
- 書案内（`READING_MAP.md`／`map/`）への収録はまだ行わない。読み返しの索引が必要になった時点で `map_build.py` に表を追加する。
