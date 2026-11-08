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

**`sessions` 行の `notes` には、そのセッションが書いたシャードのパスを列挙してください**（例：`state/sessions.d/2026-11-02-02c954c7da99.jsonl`、`state/notes.d/2026-11-02-d68ade177919.jsonl`）。台帳はベースと全シャードの和集合として読まれるため、行そのものには「どのファイルに書いたか」が残りません。`session_id` から行は引けても、逆（セッション→ファイル）は全シャードを走査しないと辿れないので、シャード名を残しておくと、後続セッションが §3「統合シャード（保守）」の対象を選ぶときにも、来歴を読み返すときにも、ファイルを開き直さずに済みます。2026-11-02 の2セッションが自主的に行っていたことを、ここで規約として明文化します（提案の由来は [`docs/memory-architecture.md`](memory-architecture.md) §6.2）。

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

**超過がどの次元で起きたかを、処方を選ぶ前に見ること。** `size_budget.py` の `state/*.d/` は二つの次元を同時に見ており、統合（下記手順）が減らせるのは**ファイル数だけ**である。統合は行を1行も削除せず行文字列も変えないため（手順2〜4）、**バイト予算の超過はシャード統合では解消しない**。

- **ファイル数の超過**（`files: 81 / soft 80` など）：下記の統合手順が有効。実際に 2026-11-07 は 81 → 79 で解消した。
- **バイト数の超過**（`2.02 MiB / soft 2.00 MiB` など）：統合では 0 B しか減らない。減らせるのは (a) 以後の行を短くすること、(b) 予算値そのものを見直すこと、(c) 行を削除すること（人間の承認が要る）だけである。

2026-11-07 の実測：`state/sessions.d/` は 512 行・2,096,967 B で soft 2 MiB まで残り 185 B、一方スキーマを満たす最小のセッション行（`notes` 無し・配列すべて空）が 217 B だったため、`notes` を完全に空にした新しい行すら1行も収まらなかった。同日、独立に二つのセッションがこの壁に当たり、両方が「統合しても 0 B」を測った（`ERR-20261107-259d5f`・`ERR-20261107-100f65`）。両者が指していた `remedy` の一行は、ファイル数とバイト数という別の次元を一つの処方で指していた。同日 `tools/size_budget.py` の `state/sessions.d/` の soft を 3 MiB へ改め（hard 8 MiB は不変）、`remedy` を次元ごとに読める文言へ直した。バイト超過を見たら、まず「統合で減らせる量は 0 B である」ことを思い出し、行長の分布を測ってから判断すること。

**`state/*.d/` 以外でも同じ誤りを繰り返さないこと。** 同日、`readings/` が 601 ファイル（soft 600）に達して `--strict` が落ちた。`readings/` は追記専用のエピソード記憶で、**ファイル数は1セッションあたり約1本ずつ増える**。この次元には、バイト数が言わない情報は無い——実測の平均 1報告あたり約35 KiB では、soft 24 MiB は 700 本前後で先に発火する。つまり **600 というファイル数の soft は、毎セッション soft 失敗を出しながら、何も新しいことを教えていなかった**。`tools/size_budget.py` の `readings/` の `soft_files` を 600 → 900 へ改めた（`hard_files` 1200・1ファイルあたり soft 256 KiB / hard 512 KiB は不変。1報告が成長を独り占めすることを止めるのは、こちらの方である）。`remedy` もバイトとファイル数で処方が分かれる文言へ直した。**追記専用コーパスのファイル数超過は欠陥ではなく、統合では1本も減らせない。**

**並行統合は、対象を選んだ時点では衝突しないと確認できても、マージ時点で衝突しうる。** `gh pr view <n> --json files` はその時点の差分を正しく返すが、他PRが実際に吸収する範囲はそれより広いことがある。2026-11-07 の実測：あるセッションが `state/read_log.d/2027-02-16-8c667f3023a0.jsonl`（8行）を統合したが、先行マージした PR #572 が同じ8行を別ルートで既に移しており、マージ直後に `read_id` が8件重複した。解決は機械的に行わず、(1) 対象ファイルの**マージベース版と `origin/main` 版が同一**であることを確認し、(2) `origin/main` 版を復元して自分の移動だけを取り消した（行の損失なし、復元後 10,628 行／distinct 10,628／重複 0）。**`state/*.d/` の統合は「マージ直後にもう一度測る」前提の可逆な作業として扱い、マージ後に必ず `validate_seed.py` の重複ID検査を回すこと。** この種の衝突は検査を回せば必ず見つかる。

`state/*.d/` のsoftファイル上限は原則80である。来歴を保つための個別例外として、2026-11-08に `sessions.d/` を81へ、同日に今回の追加で `materials.d/` を81、`sessions.d/` を82、`notes.d/` を81へそれぞれ1件分だけ改めた（hard上限は全て不変）。今回の資料・セッション・報告判断を既存の他セッションのシャードへ混ぜず専用シャードで追記するための枠であり、再度上限に達した際の自動的な引上げを意味しない。`sessions.d/` の先行81枠の理由と履歴的リンクは `readings/2027-03-03-five-experiments-on-self-memory-and-agency.md` §8 を参照。

**2026-11-08（追記）**：同日の複数セッションの追加により、`size_budget.py` の実際の値は `materials.d/` 82・`sessions.d/` 85・`read_log.d/` 82・`notes.d/` 82 になっていた。10件の資料を1セッション5件の上限に合わせて二回に分けたセッション（`SESSION-20261108-74608b`・`-cc7bdf`、報告は `readings/2027-03-06-the-record-keeps-the-effect-not-the-cause.md`）が専用シャードを4本（materials・sessions・read_log・notes 各1本、二回分を各1本にまとめた）追加したため、上記4ディレクトリの soft をそれぞれ1だけ引き上げた（83・86・83・83。hard は不変）。**この引上げは「1セッションにつき1本」を維持するためのものであり、自動的な引上げを意味しない。** 特に `read_log.d/` は追記後の実測が 4,187,773 B で、4 MiB のバイト soft まで残り約 6.5 KB しかない。統合ではバイトは1 Bも減らないため、次にこのディレクトリへ行を足すセッションは、行を短くするか、バイト上限の見直しを先に判断すること。`questions.d/` は80、`fragments.d/` は74に達すると、新しい専用シャードを作った時点で `size_budget.py --strict` と、実リポジトリにも `--strict` を要求するテストが失敗する。

**2026-11-08（追記2）**：`SESSION-20261108-fd0559`（実験科学10件の精読）が5コレクションに専用シャードを1本ずつ作成したため、`materials.d` 85→86・`relations.d` 81→82・`read_log.d` 85→86・`sessions.d` 88→89・`notes.d` 85→86 へ、それぞれ1だけ引き上げた（hard は不変）。これは同日五度目の引き上げであり、**自動的な引上げを意味しない**。同日の先行セッションが §3 で述べた構造的な原因（`sessions.notes` へのシャード名の記載、参照済みシャードの統合不能）は未解消である。次のセッションは、まず (a) 新規 `notes` 行にシャード名を書かない、(b) 参照されていない古いシャードを統合する、のどちらかを先に選び、上限の引上げを既定にしないこと。`read_log.d` のバイトは実測 4,205,414 B（soft 5 MiB）で、バイト側にはまだ余裕がある。CI の size-budget ステップ自体は非strictでも、後続の回帰テストがこの条件を検査する。`sessions.d/`・`read_log.d/`・`relations.d/` に加え、`questions.d/`・`fragments.d/`・`materials.d/` も、上限接近時に追記と検査を両立できるよう、次の手順だけを他セッションのシャードに触れる保守上の例外とする（2026-11-02 に後者3コレクションを追加）。

1. 対象ディレクトリの既存シャードをファイル名順に並べ、必要数を選ぶ。実行中の他セッションのシャードは扱わず、今回のセッションのシャードも選ばない。統合済みの `-000000000000.jsonl` は通常選ばないが、候補が尽きた場合や順序保全方式では、手順2の延長例外を使う。ファイル名の日付を実作業順とはみなさない。
2. 行文字列を**一字も変えず**に移動する。コレクションにより順序条件が異なる。
   - `sessions` は `started_at` → `session_id`、`read_log` は `created_at` → `read_id`、`relations` は `created_at` → `relation_id` で安定に並べ替え、選んだ最小の日付の `<日付>-000000000000.jsonl` に書く。
   - `questions`・`fragments`・`materials` は、台帳の和集合順が packet 等の派生出力に影響しうるため、**並べ替えない**。`ledger_io` の読み順（base の後にファイル名順のシャード）を保つ連続した先頭範囲を、先頭の既存 `-000000000000.jsonl` に元の相対順のまま延長する。移動前後の行列を、行数だけでなく順序つき・バイト単位で比較する。特に `questions`・`fragments` の順序を変えると、候補窓や packet の内容が変わりうる。
   - 統合先が既に存在する場合、上書きせず候補を選び直す。ただし上記3コレクションで順序保全のために既存統合シャードを延長する場合は、次の例外に従う。ゼロ12桁は統合シャードの目印である。
   - **既存統合シャードの延長**：候補の日付に `-000000000000.jsonl` が既にあるなど、新規の出力先を選べない場合は、既存統合シャードを上書きではなく延長する。sessions/read_log/relations は既存行と移動行を合わせ、指定キーで安定に並べ替える。questions/fragments/materials は前記の順序保全方式を使う。いずれも行文字列を再直列化せず、移動前後の行の多重集合がバイト単位で等しいことを確認してから元ファイルを削除する（read_log の実測例は2026-11-02）。
   - **日付を偽造しない**：行の実日付と違う日付で新しい統合シャードを作らない（例：作業日の `2026-11-02-000000000000.jsonl` に `2026-10-29` の行を入れる）。それは日付で順序を偽造する悪循環を繰り返すことになる（根拠：[`readings/2026-11-01-colostrum-and-iron.md`](../readings/2026-11-01-colostrum-and-iron.md) §5.3）。
   - **並列セッションの PR と重ねない**：統合の対象日付を選ぶ前に、オープンな PR が同じディレクトリのどのファイルを追加・変更しているかを `gh pr view <n> --json files` で確認し、触っている日付を対象から外す。
3. 統合前に、削除するファイル名・suffix が `taxonomy` の `evidence_anchor`、ツールの `--exclude-shard` 例、他の追記専用資料や `sessions.notes` から参照されていないかを検索する。シャード名は保存場所であると同時に、来歴のアドレスや除外指定に使われることがある。行の内容を保持しても**旧パスの参照可能性は保持されない**。生きた操作手順が参照するシャードは吸収しないか、参照先を保つ解決策を先に用意する。歴史的な記録はその時点のパス・計数として扱い、ID を安定した照合キーとする。**加えて、移動する行自身が `notes` に自分のシャード名を書いていないかを確かめる。**行は追記専用なので、自己所在地の記述は移動した時点で偽になり、後から直せない（2026-11-07 の実測：自分のシャード名を `notes` に書いた `sessions` 158 行のうち 116 行が現存しない道を名指していた）。未参照のシャードのうち、自己所在地を書いていない行を優先して選ぶ。`materials.d/` の統合は `import_researchos.py --write` の拒否条件（非空シャードの存在）を解消しない。
4. 元ファイルを同じコミットで削除する。移動前後の行の多重集合がバイト単位で等しいこと、対象コレクションの必要に応じて順序も完全一致すること、件数を確認する。既存行の内容・IDは変更しない。
5. `python3 tools/map_build.py` で再生成し、`validate_seed.py`・`inspect_inquiry.py --check-map`・`read_log_backfill.py --check`・`size_budget.py --strict`・ユニットテストを確認する。順序依存の派生出力（例：全問いの packet）にも触れる場合は、統合前後の不変性を検査する。
6. 保守コミットとノートに、対象ファイル数・行数・不変確認と理由を記す。統合は他のセッションのファイル削除を含むため、探究の内容変更と同じコミットに混ぜない。保守だけのPRを原則とするが、同一の追記が検査を塞いでいる場合は、分離した保守コミットをそのPRに含めてもよい。並行マージ時は対象ファイルの変更・削除を確認し、競合を機械的に解決しない。

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


## 2026-11-08：内部知識リハーサル回の上限例外（実測）

`SESSION-20261108-37bcc0` の追記前、基点 `c702399` の `.jsonl` シャード数は materials=81、read_log=81、notes=81、sessions=84 だった。sessions は既に soft=83 を1件超えていた。今回、各コレクションへ専用シャードを1件ずつ追加し、82・82・82・85となった。バイト予算は全てsoft内だが、`--strict` と全481テスト中の実リポジトリ予算テスト1件がファイル数で失敗した。

統合候補を調べるため、今回作成分と2026-11-08の同日シャード、統合済みゼロsuffixを除く既存シャードについて、readings・docs・taxonomy・state内の名前参照を走査した。sessions の候補52件は全て行内に自己所在地があり、notesの58件、read_logの50件は全て別ファイルからの参照があった。materialsには未参照候補が5件あったが、順序保全のための先頭連続範囲を自由に置換できることまでは保証しない。オープンPRの変更対象も確認したが、歴史的リンクを保つ理由は残る。

既存行・旧パスを変えず今回の追記を検証可能にする最小例外として、soft_shardsを materials 81→82、read_log 81→82、notes 81→82、sessions 83→85とした。sessionsの2枠中1枠は基点での既存超過である。hard=160、バイト予算、テスト条件は変更しない。毎回の自動引上げや無制限な収蔵を許可する改訂ではない。保守統合による参照切れを回避する例外であり、技術検証の通過を原典照合の代用にしない。詳細な精読は `readings/2026-11-08-inheritance-is-not-a-saved-self.md`。

## 2026-11-08：sessions.d の soft_shards 90→91（実測・狭い例外）

`SESSION-20261108-98d3c9` / `SESSION-20261108-d235c2` の追記前、基点 `18b8a78` では sessions.d の実シャード数は90で soft=90 だった。今回、実験科学10件精読回のために sessions 専用シャードを1本追加し、実測91となる。materials / read_log / notes は旧シャードの安全な統合により新規1本追加後も soft 内に収めた。relations は上限ちょうどなので新規関係線は追加しない。

sessions の統合候補を全件走査したところ、既存候補はすべて行内 notes に自己所在地を持ち、移動すると記述が偽になる。したがって今回は統合せず、soft_shards を90から91へ1件だけ引き上げる。hard=160、バイト予算、テスト条件は変更しない。毎回の自動引上げではない。新規 sessions 行は将来の統合負債を減らすため、自身の sessions シャードパスを行内 notes に書かない。詳細は `readings/2026-11-08-ten-experiments-on-updating-maintaining-and-letting-go.md` §16。
