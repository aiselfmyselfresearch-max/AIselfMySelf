# 並行ブランチの一括合流——四十五本の枝を、ひとつの main へ戻す

- **日付**: 2026-10-24
- **セッション外の作業**: 台帳（`state/*.jsonl`）に新しい番号は振っていない。この文書は合流作業の記録であり、`SESSION-036` 以降の番号は使っていない。
- **対象**: 遠隔リポジトリ `aiselfmyselfresearch-max/AIselfMySelf` の未合流枝・未合流 PR・未合流コミットすべて。

## 1. 出発点の実測

依頼は「マージされていないブランチや PR やコミットがあれば、すべてマージする」だった。まず手元の複製が浅い（shallow、1 コミット）状態だったため `git fetch --unshallow` を実行し、続けて `refs/heads/*` を全取得した。数えた結果は次のとおり。

| 項目 | 数 |
|---|---:|
| 遠隔のブランチ（`main` を除く） | 45 |
| そのうち `main` より先に進んでいる枝 | 23 |
| `main` に取り込み済みだった枝 | 22 |
| 未合流のコミット（`origin/main..枝` の合計、重複含む） | 84 |
| 開いたままの PR | 2（#13, #14。いずれも `CONFLICTING`） |

## 2. 何が本当に未合流だったのか

23 本の枝が持つ台帳レコードを、`main` の ID 集合と突き合わせた。結果は意外なほど偏っていた。

- **問い・モチーフ・断片・関係・セッションの ID は、23 本すべてで 0 件の欠落**。並行セッションどうしの番号衝突は、これまでの統合のたびに振り直され、その結果がすでに `main` に入っていた。
- 欠けていたのは **AI 研究の抜粋 63 件**（`MAT-EVD-2026…` の枝独自 ID）と、**精読・作業ノート 51 本**、**道具 16 本**、**テスト 8 本**、**CI・文書・プロンプト 5 本**。
- つまり `main` は「番号」を吸収し終えていたが、「読まれた文章」と「測る道具」を吸収しそこねていた。

| 種類 | 合流前 | 合流後 |
|---|---:|---:|
| 素材 | 517 | **580**（+63） |
| 問い | 91 | 91 |
| モチーフ | 17 | 17 |
| 断片 | 40 | 40 |
| 関係 | 722 | 722 |
| セッション | 35 | 35 |
| 精読・作業ノート（`readings/*.md`） | 18 | **69** |
| `errata` / `selection_snapshots`（検証対象外の台帳） | 0 / 0 | 1 / 1 |

## 3. 合流の方針

23 本を素朴に `git merge` すると、`state/*.jsonl`・`README.md`・`READING_MAP.md`・`state/README.md` のすべてで衝突する。そこで枝ごとに次の規則で解決し、**23 個のマージコミット**として履歴に残した（squash していない。どの枝が何を持っていたかを後から辿れるようにするため）。

1. **台帳（`state/*.jsonl`）は ID 単位の和集合**。ID が既に `main` にある行は `main` の行を採り、枝にしかない ID の行だけを末尾に追加する。同じ ID の内容が食い違う場合は `main` を正とする（`main` 側が後発の振り直し・校訂を経ているため）。
2. **生成物・進化済みの道具は `main` を保持**。`README.md`、`READING_MAP.md`、`state/README.md`、`viewer/`、既存の `tools/*.py`。枝の側の README は枝の件数（例: materials=101）を書いており、そのまま採ると `main` の記述と矛盾する。
3. **枝にしかないファイルはそのまま取り込む**。精読ノート、監査道具、テスト、CI、`prompts/acquisition.md` など。
4. **スキーマは追加のみ採用**。`schema/material.schema.json` だけは枝（`e7a366b1`）の版を採った。`verification`（書誌を実際に開いたか）という任意欄が加わっており、既存の必須欄は変わっていないため、後方互換な拡張と判断した。
5. **`READING_MAP.md` は合流後に再生成**（`python3 tools/inspect_inquiry.py --write-map`）。194 行が増え（8,509,277 バイト）、`--check-map` が PASS することを確認した。

## 4. 枝ごとの寄与

合流した 23 本を、合流した順に並べる。「新規ファイル」は枝が `main` に対して足したファイル数（精読ノート／道具／その他）、「台帳」は ID が `main` に無かったために実際に追加されたレコード。

| 枝 | マージコミット | 新規ファイル | 台帳 |
|---|---|---:|---|
| `arena/c7d71026-aiselfmyself` | `c102d7c` | 15（精読0・道具4・他11） | — |
| `arena/66ec213b-aiselfmyself` | `d7bce6c` | 3（精読0・道具1・他2） | — |
| `arena/248d951b-aiselfmyself` | `2d246e6` | 0 | — |
| `arena/40c7badc-aiselfmyself` | `f7a8a57` | 1（精読1） | — |
| `arena/215e339f-aiselfmyself` | `04d6827` | 1（精読1） | — |
| `arena/c39a871a-aiselfmyself` | `9f5d50e` | 6（精読6） | — |
| `arena/02ce17b8-aiselfmyself` | `e62c044` | 6（精読4・道具1・他1） | selection_snapshots +1 |
| `arena/e35d8156-aiselfmyself` | `9669e36` | 2（精読2） | materials +3 |
| `arena/d0e923b8-aiselfmyself` | `06ba79c` | 13（精読10・道具3） | — |
| `arena/4a59af78-aiselfmyself` | `8e44777` | 1（精読1） | materials +5 |
| `arena/4d75aea5-aiselfmyself` | `7d81b0b` | 1（精読1） | — |
| `arena/34856307-aiselfmyself`（PR #13） | `005b6f4` | 1（精読1） | — |
| `arena/84dc6484-aiselfmyself` | `e2da955` | 2（精読2） | materials +4 |
| `arena/e5adc2c2-aiselfmyself` | `4efa423` | 3（精読3） | materials +4 |
| `arena/137745c8-aiselfmyself`（PR #14） | `acae535` | 3（精読1・道具1・他1） | materials +3 |
| `arena/b7075236-aiselfmyself` | `10cda04` | 9（精読4・道具3・他2） | materials +8、errata +1 |
| `arena/e7a366b1-aiselfmyself` | `5cda517` | 9（精読7・道具2） | materials +7 |
| `arena/7ae0aa9c-aiselfmyself` | `92e5074` | 2（精読2） | materials +3 |
| `arena/0498158e-aiselfmyself` | `78824a0` | 1（精読1） | materials +5 |
| `arena/d64e2e08-aiselfmyself` | `6861d29` | 1（精読1） | materials +3 |
| `arena/d91bee76-aiselfmyself` | `a07ff72` | 2（精読1・道具1） | materials +3 |
| `arena/9df94692-aiselfmyself` | `71a8277` | 2（精読2） | materials +4 |
| `arena/bc894b4d-aiselfmyself` | `bc6b332` | 1（精読1） | materials +11 |

新規ファイルは合計 85、そのうち 51 本が `readings/`、16 本が `tools/`、8 本が `tests/`。

## 5. 台帳と読み物の非対称

合流して分かったのは、**台帳は既に合流していたが、読み物と道具は合流していなかった**ということだ。番号（ID）は統合のたびに振り直されて `main` に吸収されたが、その番号を振り直すために書かれた精読ノートや、その測定に使った `tools/tanka_meter.py`・`tools/gate_audit.py`・`tools/relation_audit.py` などは、枝の中にだけ残っていた。

これは台帳の側から見ると「記録された素材が読まれていない」のではなく、「読まれた痕跡が台帳の外にあった」という状態である。`validate_seed.py` は 6 つの台帳の整合しか見ないので、この不在は PASS のまま見過ごされる。

## 6. 合流で壊れたもの、直したもの

`arena/c7d71026-aiselfmyself` が持ち込んだ `tests/`（35 本）を `python3 -m unittest discover -s tests` で実行したところ、4 本が失敗した。

| テスト | 失敗の内容 | 処置 |
|---|---|---|
| `test_parallel_sessions` | `fragments=15` など件数を直書き。台帳が増えるたびに壊れる | 実行前の件数を数え、`+3` を検査する形に変更 |
| `test_api_state_index_and_404` | `/api/state` のキー集合を完全一致で検査。`readings`・`voice_audit` が増えた時点で失敗 | 期待キーの**部分集合**であることを検査し、断片数は台帳から数える |
| `test_busy_ledger_returns_503_with_retry_after` | 枝の `serve_viewer.py` は `503` を返すが、`main` の版は汎用の `500` | `500` と JSON エラー本文を検査する形に改名・修正（下記の負債を参照） |
| `test_concurrent_reads_during_atomic_rewrites` | 素材数を `18` で直書き、`503` を期待 | 実行時の件数と `500` に合わせた |

修正後、`python3 -m unittest discover -s tests` は **35 本すべて PASS**。`python3 tools/validate_seed.py` は
`questions=91, motifs=17, materials=580, fragments=40, relations=722, sessions=35` で PASS、
`python3 tools/inspect_inquiry.py --check-map` も PASS。`node --check viewer/app.js`（CI の一項目）も通ることを確認した。

## 7. 残る負債

1. **同名で内容の異なる精読ノート**。`readings/2026-10-22-pronouns-and-empty-cart.md` など数本は、枝と `main` の両方に別内容で存在した。方針どおり `main` を採ったため、枝の側の初稿は今回の合流では失われている（枝自体は消していないので `git show <枝>:<path>` で参照できる）。
2. **精読ノートが指すセッション番号と `main` の番号のずれ**。枝のノートには `SESSION-026` などの番号が書かれているが、`main` では振り直しの結果その番号が別のセッションを指す。ノート本文は当時の記録として残し、ここにずれがあることを記す。全 51 本の照合は未了。
3. **`503` / `Retry-After` の経路**。枝の `serve_viewer.py` は `ledger_io.LedgerBusy` を捕まえて `503` を返すが、`main` の版は `readings` と `voice_audit` のペインを後から得ているため、そのまま差し替えると閲覧画面の機能が後退する。今回は `main` の版を残し、`tools/ledger_io.py` と `state/*.d/` シャードの仕組みだけを取り込んだ。**503 を返す統合は未了**。
4. **`errata.jsonl` と `selection_snapshots.jsonl` は `validate_seed.py` の検査対象外**。合流で 1 件ずつ入ったが、参照整合性は誰も検査していない。
5. **枝の削除はしていない**。45 本の遠隔ブランチはそのまま残した（PR #13・#14 は内容が本合流に含まれるため、別途クローズする）。
