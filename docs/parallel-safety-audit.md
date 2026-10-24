# 並列セッション安全性の点検

- 日付：2026-10-21
- 対象ブランチ：`arena/c7d71026-aiselfmyself`
- 対象：`state/*.jsonl` の同時読み書き、`tools/` の更新系、`viewer/` の並列リクエスト
- 方法：コード読解、リポジトリの複製での再現実験、回帰テストの追加
- 実験は `/tmp` の複製で行い、このリポジトリの台帳は変更していません（`READING_MAP.md` の見出しのみ再生成）。

## 0. 要約

このリポジトリには、複数セッションが同じ台帳を同時に更新するための仕組みがありませんでした。連番ID（`FRAG-013`）、単一の `state/*.jsonl`、ロックなしの `Path.write_text()`、シャードを無視する検証・表示という構成で、**並列化すると実際に壊れる**ことを主要な4種類で再現しました。

| # | 見つけた問題 | 重大度 | 状態 |
|---|---|---|---|
| P1 | 書換中の読み取りが空ファイル／途中の行を返す | 高 | 修正 |
| P2 | 台帳の書換が非原子（truncate → write） | 高 | 修正（同梱ツール） |
| P3 | 並列セッションの連番IDが衝突する | 高 | 修正（採番ツール） |
| P4 | `state/*.d/` のシャードが検証・読書案内・ビューアから見えない | 高 | 修正 |
| P5 | `--write-map` が last-writer-wins・非原子 | 中 | 修正 |
| P6 | `import_researchos.py --write` の2ファイル更新が非原子 | 中 | 修正（完全なトランザクションではない） |
| P7 | 並列リクエスト中の例外が HTTP 500 になる | 高 | 修正（503＋再試行） |
| P8 | 6ファイルの読み取りに一貫したスナップショットがない | 中 | ベストエフォートで改善 |
| P9 | 固定見出し（`Q-001 〜 Q-015` 等）が件数とずれる | 低 | 修正 |
| P10 | パス判定の prefix 比較、スレッドの無制限生成 | 低 | 一部修正 |

**未解決**：意味的な正しさ、共有文書の Git 衝突、協力しない書換、複数ファイル間の完全な一貫性。これらは「解決した」とは書きません（§6）。

## 1. 対象と方法

### 1.1 何を「並列化」と呼んでいるか

ここでいう並列化は、CPU の並列計算ではなく、**複数の AI セッション／プロセスが同じリポジトリの台帳を同時に読み書きする状況**です。ビューアの `ThreadingHTTPServer` が複数リクエストを並列に処理する状況も含みます。

上流の ResearchOS は、凍結ベース＋セッション別シャード、非連番ID（`PREFIX-YYYYMMDD-xxxx`）、`new_id.py`、`new_ledger_shard.py`、`ledger_store.py` でこの問題に対処しています。本リポジトリは移行時にその仕組みを引き継いでおらず、`import_researchos.py` だけが上流のシャードを読む状態でした。

### 1.2 再現実験

- 240KB の台帳を40回 `Path.write_text()` で書き換え、別スレッドで `load_jsonl` 相当の読み取りを688回。
- 4.5MB の台帳（レコード2160件）を60回書き換え、8スレッドで `serve_viewer.read_archive_payload()` を246回。
- 2プロセスが同時に「現在の最大ID＋1」を採番し、`fragments.jsonl` に追記。
- 同じ `FRAG-013` を `state/fragments.d/` に置き、検証・読書案内・ビューアがどう扱うかを確認。

測定用のスクリプトは監査時は `/tmp` に置きました。同種の測定を再実行できるように、`tools/parallel_probe.py` を追加しています（§7）。

## 2. 見つけた問題と証拠

### P1. 書換中の読み取りが空ファイル／途中の行を返す（高）

`Path.read_text()` は1回の open と複数回の read で構成され、`Path.write_text()` は**最初にファイルを切り詰めてから**書きます。読み取りがその間に来ると、空ファイルや途中で切れた JSON 行を読んでしまいます。

- 240KB・688回の読み取り：`json` エラー39回、レコード数が足りない読み取り197回。**236/688（34.3%）が不完全**。
- 4.5MB・246回の読み取り：`RuntimeError` 38回（15.4%）。例：`state/materials.jsonl:89: invalid JSON: Unterminated string`。
- 影響：`validate_seed.py` の一時的な false red、`inspect_inquiry.py --check-map` の false stale、ビューアの HTTP 500。
- 参照：旧 `tools/validate_seed.py` の `load_jsonl()`、旧 `tools/serve_viewer.py` の `read_archive_payload()`。

### P2. 台帳の書換が非原子（高）

`Path.write_text()` は `O_TRUNC` で開いてから書くため、クラッシュや同時実行で空・途中のファイルが残ります。240KB の実験では、書き換え中に**レコード数が足りない読み取り（空を含む）が197回**観測されました。`--write-map` と `import_researchos.py --write` がこの経路でした。

### P3. 並列セッションの連番IDが衝突する（高）

2つのセッションが同じ台帳を読み、どちらも最大値12から `FRAG-013` を採番しました。両方を追記すると、`validate_seed.py` は次で失敗します。

```text
state/fragments.jsonl:14: duplicate fragment_id FRAG-013
```

連番は「読んでから書くまでに他の誰も書かない」ことを前提にしており、並列化では成立しません。既存の素材（`MAT-EVD-20261021-90a7` など）は上流由来の非連番IDで、スキーマも連番を要求していません。

### P4. シャードが検証・読書案内・ビューアから見えない（高）

`state/fragments.d/` に `FRAG-013` を置いた場合：

| 読み手 | 結果 |
|---|---|
| `validate_seed.py` | **PASS**、`fragments=12`（シャードを読まない） |
| `inspect_inquiry.py --write-map` | `FRAG-013` が `READING_MAP.md` に現れない |
| `serve_viewer.py` | `FRAG-013` が0件 |
| `import_researchos.py` | 上流の `state/*.d/*.jsonl` を読む実装になっている |

**同じリポジトリの中で、シャードを見るツールと見ないツールが混在**していました。パラレルセッションがシャードに書いても、検証は緑のまま、読者には存在しない——もっとも危険な失敗の仕方です。

### P5. `--write-map` が last-writer-wins・非原子（中）

旧実装は `args.map_path.write_text(expected_md)` の1行で、ロックも原子的置換もありませんでした。2セッションが同時に実行すると、後勝ちで片方の状態を反映した地図だけが残る可能性があります。読者が書き込み途中の `READING_MAP.md` を見ることもあります。

### P6. `import_researchos.py --write` の2ファイル更新が非原子（中）

`state/materials.jsonl` と `migration/manifest.json` を順に `write_text()` していました。クラッシュすると materials だけ新しく manifest が古い、またはその逆の状態が残ります。同時実行の直列化もありません。

### P7. 並列リクエスト中の例外が HTTP 500 になる（高）

旧 `do_GET` は `read_archive_payload()` の例外をすべて 500 にしていました。P1 の失敗は一時的な競合であるにもかかわらず、クライアントには恒久的なサーバエラーとして見えます。ビューア側にも再試行はありませんでした。

### P8. 6ファイルの読み取りに一貫したスナップショットがない（中）

`validate_seed.py`、`inspect_inquiry.py`、`serve_viewer.py` は6つの台帳を別々に読んでいました。セッションが fragment と relation を別ファイルに追記している途中に読むと、「fragment はあるが relation はない」という、どの時点とも一致しない状態を観測し得ます。

### P9. 固定見出しが件数とずれる（低）

`READING_MAP.md` の生成側に `## 2. 開かれた問いの系譜（Q-001 〜 Q-015）`、`## 5. セッション履歴（SESSION-001 〜 SESSION-012）`、`## 1. 問いを横断する 6 つのモチーフ` が固定文字列で埋め込まれていました。シャードや非連番IDを追加すると、見出しだけが古くなります。

### P10. パス判定とスレッド（低）

- 静的ファイルの判定が `str(candidate).startswith(str(VIEWER_DIR))` で、`viewer_evil/` のような前方一致を許し得ました。
- `ThreadingHTTPServer` はリクエストごとにスレッドを作ります。`timeout` がなく、遅いクライアントがスレッドを保持し続けられます（上限は今もありません。§6）。

## 3. 実測：修正前と修正後

`tools/parallel_probe.py` は、同じ台帳に対して「素朴な書換／原子的書換」×「素朴な読み／安定読み」の4通りを測ります。300レコード・約0.6MB・40回書換・6読者スレッドの結果です。

| 書き手 | 読み手 | parsed | json エラー | short（不完全） | busy | ok |
|---|---|---:|---:|---:|---:|---:|
| 素朴（`write_text`） | 素朴（`read_text`） | 408 | 62 | 196 | 0 | 212 |
| 素朴（`write_text`） | 安定（`ledger_io`） | 58 | 0 | 3 | 0 | 55 |
| 原子的（`ledger_io`） | 素朴（`read_text`） | 699 | 0 | 0 | 0 | 699 |
| 原子的（`ledger_io`） | 安定（`ledger_io`） | 200 | 0 | 0 | 0 | 200 |

同じ条件を3回繰り返すと、素朴な書き手＋安定読みの `short` は **3/58、31/54、5/47** と変動しました（実行ごとのスケジューリング依存）。原子的な書き手では3回とも0です。

読み方：

- **書き手を原子的にするだけで、素朴な読み手でも壊れない**（3行目）。同梱ツールの書込みを `os.replace()` に変えた効果です。
- 安定読みは、素朴な書き手に対しても json エラーを0にします（2行目）。ただし**truncate の一瞬を捉えた short が残ります**（3〜31回、実行による）。これは協力しない書換に対する限界で、§6 に残します。
- 安定読みは再試行するため読み取り回数は減ります（47〜66回）。ビューアの通常負荷では問題になりませんが、高頻度の書換中は 503 を返す設計です。

## 4. 修正内容

| ファイル | 変更 |
|---|---|
| `tools/ledger_io.py`（新規） | 安定読み（サイズ・mtime・ctime・inode の前後比較＋再試行）、複数ファイルのスナップショット、base＋シャードの union 読取、重複検出、原子的書換、排他ロック |
| `tools/validate_seed.py` | `load_jsonl()` を union 対応に。6台帳を1スナップショットで読む。書換中は終了コード2で「再試行」を促す |
| `tools/inspect_inquiry.py` | union 読取。`--write-map` はロック＋最新スナップショット＋原子的置換。`--check-map` は安定読み。見出しを件数ベースに |
| `tools/serve_viewer.py` | union＋安定読み。競合時は **503＋`Retry-After: 1`**。パス包含判定を `relative_to` に。`timeout=30`、キュー64、`mimetypes.init()` |
| `tools/import_researchos.py` | ローカル素材の安定読み。`--write` はロック＋原子的置換。`state/materials.d/` に空でないシャードがある間は `--write` を拒否 |
| `tools/new_id.py`（新規） | `PREFIX-YYYYMMDD-xxxxxx` の採番。base＋全シャードを確認 |
| `tools/new_ledger_shard.py`（新規） | `state/<collection>.d/YYYY-MM-DD-<12hex>.jsonl` を `O_EXCL` で作成 |
| `viewer/app.js` | 503 のとき短く再試行してから fallback |
| `tests/`（新規） | 並列セッションの End-to-End、実サーバの並列リクエスト、原子的書換、ロック、採番、シャードを含む35テスト |
| `READING_MAP.md` | 見出し3箇所のみ再生成（内容は不変） |

## 5. 検証結果

```sh
$ python3 tools/validate_seed.py
PASS: literary inquiry seed valid (questions=15, motifs=6, materials=18, fragments=12, relations=31, sessions=12)

$ python3 tools/inspect_inquiry.py --check-map
PASS: READING_MAP.md is up to date with state/*.jsonl

$ python3 tools/import_researchos.py --source-root /tmp/ResearchOS --check
PASS: selected source/evidence snapshot and manifest match the upstream checkout

$ python3 -m unittest discover -s tests -v
... 35 tests ... OK
```

End-to-End テストでは、3セッションが同時に4種類のシャード（fragments / questions / relations / sessions）を作成し、IDを採番して追記します。その後、`validate_seed.py` が `fragments=15, questions=18, relations=34, sessions=15` で PASS し、`READING_MAP.md` とビューアの payload に3件の新しい断片が現れることを確認しています。

## 6. 残る危険（未解決）

| 問題 | 状態・理由 |
|---|---|
| **協力しない truncate 書換** | `Path.write_text()` で台帳を書き換える外部スクリプト・エディタは、依然として空や途中の状態を見せ得る。probe の「素朴な書き手＋安定読み」で short 3〜31/47〜66（実行による）。防御はプロトコル（シャードへ追記、書換は `ledger_io.atomic_write_text()`）のみ |
| **複数ファイル間の一貫性** | 全ファイルの署名を前後で比較するベストエフォート。書き手がファイル間で長く止まると混ざった時点を読む可能性が残る。各ツールは1操作1ファイルを守ることで窓を小さくしている |
| **意味的な正しさ** | スキーマ・ID一意性・参照整合性だけを検査する。引用が原典と一致するか、解釈が妥当かは見ない（上流と同じ立場） |
| **共有文書の Git 衝突** | `README.md`、`docs/`、`READING_MAP.md` は同時編集でテキスト衝突し得る。CI はマージ後の `--check-map` で stale を検出するが、衝突自体は防がない |
| **ロックは助言的** | `state/.ledger.lock` を取るのは同梱ツールだけ。シェルリダイレクトや外部エディタは無視できる |
| **ランダムIDの衝突** | 6 hex（16,777,216通り）。同じ日に100個で約0.03%、1000個で約3.0%。衝突したら `validate_seed.py` が重複として拒否する。必要なら `--hex-bytes` を増やす |
| **IDに時系列がない** | 非連番IDのため、ID順は生成順ではない。順序はファイル内の追記順と `created_at` で示す |
| **書き手の識別** | 全セッションが同じ Git author。誰が書いたかは残らない（上流と同じ未解決） |
| **サーバのスレッド上限** | `timeout=30` とキュー64で緩和したが、同時接続数にハードリミットはない |
| **materials のシャード** | `import_researchos.py --write` は `state/materials.d/` に空でないシャードがある間、意図的に拒否する。素材だけは統合してから再生成する |
| **ベースへの直接追記** | 運用で禁止しているが、強制はしない。重複IDは検証で捕まるが、同一ファイルへの同時追記による Git 衝突は防げない |

「未解決」を「解決」と書かないために、この表を残します。とくに1行目は、同梱ツールの外側で台帳を書き換えた場合に残ります。

## 7. 再現手順

```sh
# 4通りの並列読み書きを測定（一時ディレクトリのみ。state/ は触らない）
python3 tools/parallel_probe.py

# 大きめの台帳で測る場合
python3 tools/parallel_probe.py --records 800 --record-bytes 2000 --iterations 60 --readers 8

# 回帰テスト
python3 -m unittest discover -s tests -v
```

`tests/test_parallel_sessions.py` は、3セッション同時実行・ID衝突の拒否・union 表示を確認します。`tests/test_server.py` は、原子的書換中の並列 `/api/state` が 500 を返さないこと、busy 時に 503 と `Retry-After` を返すことを確認します。

## 8. 参照

- 運用ルール：[`parallel-work.md`](parallel-work.md)
- 上流 ResearchOS：`docs/parallel-work-ownership.md`、`docs/record-id-scheme.md`、`scripts/new_id.py`、`scripts/new_ledger_shard.py`、`scripts/ledger_store.py`
- 台帳スキーマ：[`schema/`](../schema/)、 [`state/README.md`](../state/README.md)
- 移行方針：[`MIGRATION.md`](../MIGRATION.md)
