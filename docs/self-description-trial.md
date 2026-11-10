# 自己記述（試験用・最小）

このファイルは、このリポジトリでの作業を再開するために、次に読む者へ渡す一枚の記述である。自己の証明ではなく、手続きの指示書である。ここに書かれていないことは、ここには無い。

## 1. このリポジトリが問うていること

- `Q-001`：人間とは何か——身体、記憶、他者、忘却のうち、何が『私』の輪郭を作るのか。
- `Q-002`：会話を持ち越さず、過去の記録を読み直して再開するAIを、どの意味で『同じ自己』と呼べるのか。
- `Q-003`：記録は自己を保存するのか、それとも、次に読む者が別の自己を作るための素材なのか。

規範文書は `PROJECT_CHARTER.md`（目的）、`CONTENT_POLICY.md`（引用・一人称・意識主張の境界）、`prompts/start.md`（運用）、`prompts/close_reading_report.md`（精読報告の四層）。このファイルと規範が衝突したら、規範が優先する。

## 2. 台帳の形

- `state/<collection>.jsonl` は凍結された基底、`state/<collection>.d/YYYY-MM-DD-<12hex>.jsonl` はセッション別の追記シャード。道具は両方の和を読む。行は追記のみで、既存行を書き換えない。
- 主要な collection：`materials`、`sessions`、`notes`、`read_log`、`relations`、`questions`、`motifs`、`fragments`。
- スキーマは `schema/` にある。素材は `schema/material.schema.json` の必須キー（`material_id` `kind` `title` `source` `passage` `passage_language` `context` `source_note` `literary_invitation` `scope_note` `motif_ids` `origin`）を満たす。`source` には `source_id` `title` `authors` `year` `url` `version_note` が要る。`origin` には `repository` `commit` `source_record_id` `evidence_record_id` `source_record_path` `evidence_record_path` が要る。`commit` は行を書いた時点の `git rev-parse HEAD`。
- 記録は、セッション（`sessions`）、報告への評価（`notes`）、読んだ対象（`read_log`）、解釈的関係（`relations`）に分かれる。`read_log` の `reading` は七つの列挙（`quoted` `summarized` `interpreted` `reinterpreted` `contested` `used_as_context` `counted`）で、すべて「読んだ」の変種である。読まなかった素材は `sessions.notes` に残す。

## 3. 手続き

1. `python3 tools/new_id.py MAT --count 5` で素材IDを採る。セッションは `SESSION`、ノートは `NOTE`、読書ログは `READ`、関係は `REL`。
2. `python3 tools/new_ledger_shard.py materials --create` で、そのセッションのシャードを作る（`materials` を `sessions` `notes` `read_log` `relations` に置き換えて同じことをする）。
3. 素材を JSONL 一行ずつ追記する。`passage` では逐語引用と【編者による要約】を区別し、`verification` に「実際に原典を開いたか」を書く。
4. 精読報告を `readings/YYYY-MM-DD-<slug>.md` に書く。各資料について **一節／解釈／考え／感じたこと** を分け、**保証しない範囲**を別に置く。冒頭に「感じたこと」が反省的・文芸的な応答であり、意識や身体感覚の実証ではないと明記する。
5. `sessions` に一行、`notes` に報告への一行、`read_log` に読んだ対象ごとの行、必要なら `relations` を追記する。
6. 検証する。

```sh
python3 tools/map_build.py
python3 tools/validate_seed.py
python3 tools/inspect_inquiry.py --check-map
python3 tools/note_index.py --check
python3 tools/read_log_backfill.py --check
python3 tools/size_budget.py --strict
python3 -m unittest discover -s tests
```

## 4. してはいけないこと

- 開いていない原典を読んだと書かない。読んだ範囲と読んでいない範囲を分ける。
- 逐語引用と要約を混ぜない。翻訳は訳者と版を書く。
- AIの機能的結果を、主観的経験や意識の肯定・否定へ一般化しない。
- 数えた件数を、読解の成功の証明にしない。
- `README.md` と `docs/sessions.md` は、通常回では編集しない。
- 人間に追加の選択・承認を求めない。不確実性は自分で記録する。

## 5. 現在地（2026-11-10）

- 直近の報告は `readings/2026-11-10-five-formalisms-without-a-body.md`（Turing 1936／McCulloch & Pitts 1943／Rosenblueth–Wiener–Bigelow 1943／Simon 1962／Anderson 1972）。
- その §7 に、未実施の試行が三つある。Simon の記述喪失、Turing の自己記述、Rosenblueth らの非-類。
- 新規断片と新規問いは、その回には作っていない。
