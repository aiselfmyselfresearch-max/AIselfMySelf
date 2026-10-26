# `state/read_log.d/` シャード統合記録（SESSION-20261118-291f45）

- **セッションID**：`SESSION-20261118-291f45`（124 → 125件目）
- **日付**：台帳内部編年 `2026-11-18`（実行環境の実日付は `2026-10-26`。開始時に台帳の直近内部日付を確認し `2026-11-18` で確定）
- **作業ブランチ**：`arena/482439d8-aiselfmyself`（起点 `origin/main` = `dbb2e23c79eaee27fbe0e66892c5b3179574c9fc`）
- **種別**：保守専用セッション（`docs/mode-rotation-triggers.md` §3 に基づく `state/read_log.d/` シャード統合。新規探究・創作なし）
- **追加・変更なしの確認**：新規素材0・新規断片0・新規問い0・新規モチーフ0・新規関係0・新規編集判断0・新規訂正0・新規 `read_log` 行0・凍結ベース `state/read_log.jsonl` 変更0・`README.md` / `docs/sessions.md` 未編集（`--sync-readme` 不実行）

---

## 1. 開始時のブランチ・リモート状態と前提整理

1. **ローカル・リモート・PR 状態**：
   - 作業ツリーは clean、作業ブランチは `arena/482439d8-aiselfmyself`（Arena セッション固定ブランチ、起点 `dbb2e23c79eaee27fbe0e66892c5b3179574c9fc`）。
   - `git fetch` 後の `origin/main` は `dbb2e23c79eaee27fbe0e66892c5b3179574c9fc`、`gh pr list --state open` は 0 件。
   - リモート上の全ブランチを確認したところ、未マージの `origin/arena/99feeea6-aiselfmyself`（`d37306842fa2333b0021c8ded17960d175d07312`、`read_log` 4,122行・79/80シャード）が存在し、他の並走セッションによるシャード統合は行われていなかった。
   - 開始時に人間へ状況を整理・確認のうえ、`d37306842f` は取り込まず現在の `origin/main`（`dbb2e23`、`read_log` 4,082行・`state/read_log.d/` 78/80シャード）のまま統合を実施し、内部日付を `2026-11-18` とする方針で確定した。
2. **発動基準と手順の根拠**：
   - [`docs/mode-rotation-triggers.md`](../docs/mode-rotation-triggers.md) §3：`state/read_log.d/` シャード数の soft 上限 80 ファイル接近・到達時は他の創作より統合を優先する。
   - [`docs/parallel-work.md`](../docs/parallel-work.md)：凍結ベース `state/*.jsonl` は変更せず、`README.md` と `docs/sessions.md` は通常・保守回では編集しない（B案）。
   - [`readings/2026-11-14-two-spoons-of-salt-and-the-frozen-sea.md`](2026-11-14-two-spoons-of-salt-and-the-frozen-sea.md) §9.3・§9.3b：最古21シャードを先頭シャード名のまま無改変で1本へ連結し、連結前後で `base + 全シャード`（ファイル名順・行順）の SHA-256 と ID 集合を検算するとともに、統合対象シャード名を記録に残す。

---

## 2. 統合対象シャード（ファイル名順・最古21本 → 1本）

ファイル名辞書順で先頭21シャードの元バイト列を、正規化・並べ替え・書き換えを行わずそのまま `state/read_log.d/2026-10-24-1608281fffef.jsonl` へ連結し、2番目〜21番目の20ファイルを整理した。

| 順 | ファイル名 | 統合前の行数 | 統合前のバイト数 | 統合後の扱い |
|---:|---|---:|---:|---|
| 1 | `2026-10-24-1608281fffef.jsonl` | 49 | 10,782 | **統合先として維持（2,314行 / 771,605 B）** |
| 2 | `2026-10-24-1ac8a5977f75.jsonl` | 57 | 20,502 | 1番へ連結・削除 |
| 3 | `2026-10-24-2481bfd5a159.jsonl` | 1,242 | 434,669 | 1番へ連結・削除 |
| 4 | `2026-10-24-31ab111918e2.jsonl` | 70 | 26,132 | 1番へ連結・削除 |
| 5 | `2026-10-24-52d8c9575513.jsonl` | 29 | 7,954 | 1番へ連結・削除 |
| 6 | `2026-10-24-5a3ffba1db46.jsonl` | 17 | 5,102 | 1番へ連結・削除 |
| 7 | `2026-10-24-5c637288acca.jsonl` | 18 | 5,303 | 1番へ連結・削除 |
| 8 | `2026-10-24-64ce1669060c.jsonl` | 102 | 31,478 | 1番へ連結・削除 |
| 9 | `2026-10-24-6900d8b2c4f1.jsonl` | 68 | 18,926 | 1番へ連結・削除 |
| 10 | `2026-10-24-6dd3a546071a.jsonl` | 46 | 16,319 | 1番へ連結・削除 |
| 11 | `2026-10-24-7727cb78a407.jsonl` | 46 | 16,752 | 1番へ連結・削除 |
| 12 | `2026-10-24-7c1e0d9a4b62.jsonl` | 56 | 15,453 | 1番へ連結・削除 |
| 13 | `2026-10-24-83c3fa31ed9a.jsonl` | 34 | 12,410 | 1番へ連結・削除 |
| 14 | `2026-10-24-a0f49f2a166f.jsonl` | 75 | 21,434 | 1番へ連結・削除 |
| 15 | `2026-10-24-a5e0751ac7d9.jsonl` | 82 | 25,812 | 1番へ連結・削除 |
| 16 | `2026-10-24-b7e21c9d4f03.jsonl` | 52 | 14,347 | 1番へ連結・削除 |
| 17 | `2026-10-24-bb121a7b509c.jsonl` | 92 | 33,033 | 1番へ連結・削除 |
| 18 | `2026-10-24-bf83d7ae3a24.jsonl` | 72 | 20,027 | 1番へ連結・削除 |
| 19 | `2026-10-24-c4f7b2e9d1a8.jsonl` | 8 | 2,176 | 1番へ連結・削除 |
| 20 | `2026-10-24-ccff816447d5.jsonl` | 62 | 19,637 | 1番へ連結・削除 |
| 21 | `2026-10-24-d5095811b8dd.jsonl` | 37 | 13,357 | 1番へ連結・削除 |
| **計** | **最古21シャード合計** | **2,314** | **771,605** | **1ファイルへ集約** |

- 無変更で残したシャード（旧22番目〜78番目、計57本）：先頭 `2026-10-24-d6a0dd8adaba.jsonl` 〜 末尾 `2026-11-17-31e4afb103c7.jsonl`（計 1,768行 / 687,872 B）
- 凍結ベース `state/read_log.jsonl`：0行 / 0 B（変更なし）

---

## 3. 検算値（統合前・一時ファイル検算・統合確定後）

一時ファイル上で統合候補を作成し、行数・`read_id` 集合・出現順・SHA-256 の完全一致を確認したうえで、`ledger_io.exclusive_lock` 下の `fsync` + `os.replace` により先頭シャードを置換し、統合元20ファイルを削除した。確定後に実ディレクトリを再走査し、すべての検算値が統合前と一致することを確認した。

| 検算項目 | 統合前 | 一時ファイル検算 | 統合確定後 | 判定 |
|---|---:|---:|---:|---|
| `state/read_log.jsonl`（base） | 0行 / 0 B | 0行 / 0 B | 0行 / 0 B | 無変更 |
| `state/read_log.d/` シャード数 | 78（soft 80） | 58（soft 80） | **58（soft 80）** | −20（上限内） |
| `read_log` 総行数 | 4,082 | 4,082 | **4,082** | 完全一致 |
| ユニーク `read_id` 数（重複件数） | 4,082（重複0） | 4,082（重複0） | **4,082（重複0）** | 集合・順序とも一致 |
| `base + 全シャード` 連結バイト数 | 1,459,477 B | 1,459,477 B | **1,459,477 B** | 完全一致 |
| `base + 全シャード` 連結 SHA-256 | `b0c192341cb25e1e12e04fc1a0f718fd657799fc81e4087091ed562f1ad059b6` | `b0c192341cb25e1e12e04fc1a0f718fd657799fc81e4087091ed562f1ad059b6` | **`b0c192341cb25e1e12e04fc1a0f718fd657799fc81e4087091ed562f1ad059b6`** | 完全一致 |
| `read_id` 順列（`\n` 区切り）SHA-256 | `8c399674df443cd655879f13eb2f29e42c9837904a0ff8cb18f567d355d8e26b` | `8c399674df443cd655879f13eb2f29e42c9837904a0ff8cb18f567d355d8e26b` | **`8c399674df443cd655879f13eb2f29e42c9837904a0ff8cb18f567d355d8e26b`** | 完全一致 |

---

## 4. 検証コマンド結果

- `python3 tools/validate_seed.py`：PASS（`questions=328, motifs=59, materials=2433, fragments=169, relations=5009, sessions=125, read_log=4082, editorial_decisions=47`）
- `python3 tools/read_log_backfill.py --check`：PASS（`3063/3063 (session, context material) pairs`）
- `python3 tools/map_build.py` / `python3 tools/map_build.py --check`：PASS（本保守セッション1件を反映して `READING_MAP.md` を再生成、`--sync-readme` は不実行）
- `python3 tools/size_budget.py --strict`：PASS（`state/read_log.d/` は `58 / soft 80 / hard 160`、`state/sessions.d/` は `66 / soft 80 / hard 160`、`tools/_*` は `0`）
- `python3 -m unittest discover -s tests`：OK（全284テスト通過）
- `node --check viewer/app.js`：成功（exit 0）

本セッションで追記したファイルは `state/sessions.d/2026-11-18-aeb2eb88bbf3.jsonl`（1行）と本ノート `readings/2026-11-18-read-log-shard-compaction.md`、および `map_build.py` による `READING_MAP.md` 再生成分のみである。将来、別ブランチと併合する際は両親の `read_id` 集合の和集合と行数を検算し、`READING_MAP.md` を union から再生成する。
