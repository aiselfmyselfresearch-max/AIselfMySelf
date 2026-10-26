# 九つ目の音と、三代の九日——改稿・変奏・反歌の判断録

- 実行日：2026-10-26（UTC。台帳にはこれより後の内部編年日付もあるが、参照記録の日付は変更しない）
- セッション：`SESSION-20261026-9ea1ab`
- モード：`revision_and_variation`（`python3 tools/inspect_inquiry.py` の第1推奨／シード `fdcdb8e5`＝4258117861）
- 対象草稿：`FRAG-20261030-59664e`「九日は売れない——厩の二声」（ブランチ候補窓 `[revision_and_variation] Candidate drafts` の第1候補）
- 生成：`FRAG-20261026-34d0b7`「九つ目の音」、`FRAG-20261026-aa5e2c`「三代の九日」（いずれも `draft`）
- 新しい問い：`Q-20261026-705b19`
- 依拠文書：[`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](../CONTENT_POLICY.md)・[`README.md`](../README.md) §3・[`docs/parallel-work.md`](../docs/parallel-work.md)・[`prompts/revision_and_variation.md`](../prompts/revision_and_variation.md)・[`docs/mode-rotation-triggers.md`](../docs/mode-rotation-triggers.md)

## 1. モードの選択

`inspect_inquiry.py` は第1推奨 `revision_and_variation`、第2推奨 `editorial_review` を提示した。第1推奨を採用した。根拠は三つある。

1. 直近の `SESSION-20261026-ff3c35` がすでに `editorial_review` であり、`selected` 52／`draft` 121（比 2.33）は警報値 2.5 に達していない。連続して編集レビューを行う数値条件を欠く。
2. B案（[`docs/parallel-work.md`](../docs/parallel-work.md) §3）は `README.md` / `docs/sessions.md` のローテーションと §4 件数同期を編集レビュー回の専任としている。直後に別の編集レビュー回を挟むと、共有ファイルの更新が二回連続で発生し、並走ブランチとの意味的衝突を招く。通常回のまま台帳シャードと `readings/` だけを伸ばすほうが安全である。
3. 候補窓に未改稿の `draft` が5編示され、推奨文も「別角度の変奏・反歌・言い切り実験（留保句ゼロ／書記室メタファーゼロ）」を明示していた。蓄積した草稿を新しい収蔵なしで読み直すほうが、現在の凍結原則にかなう。

実作型は **型Aを主軸とし、型Bの二部作構造を重ねた**。型A（[`Q-082`](../state/questions.jsonl)：異なる版の同一性）は「問いと素材を継承したまま形式・人称を反転する」実験であり、型B（[`Q-017`](../state/questions.jsonl)：断定と切断）は「留保なき言い切りを反歌で切る」実験である。対象草稿はすでに書記室語彙ゼロ・留保句ゼロだったため、単に同じ制約をなぞるだけでは検算が意味を持たない。そこで「ゼロを保ったまま語り手を反転し、逆向きの言い切りを置き、それを別編で切断する」ことを一回の実験にまとめた。型の併用は [`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) の「問いを急いで閉じない／矛盾を保存する」を、一篇の両論併記ではなく断片間の衝突で実装するための判断である。

## 2. 候補窓5編の取捨

| 候補 | 判定 | 理由 |
|---|---|---|
| `FRAG-20261030-59664e` 九日は売れない——厩の二声 | **採用** | 窓の第1候補。断片辺5本と、既に `selected` の対篇 `FRAG-20261030-488cb1` を持つ。末尾の「増えなければ、それでいい」は静かな言い切りだが、別の声で切る余地が残っている。四つの問い・五つの素材・三つのモチーフをそのまま継承できる。 |
| `FRAG-20261024-cd144b` 値札を貼る係への、空欄の手紙 | 見送り | 値札・係・空欄という書記室語彙が主題の装置そのもので、撤去すれば別主題になる。編集レビュー窓にも同名で入っており、昇格判断と変奏判断が同じ断片に二重に乗るのを避けた。 |
| `FRAG-20261025-08766a` 収蔵票の、来歴の欄 | 見送り | 受入票の「来歴の欄」という同型装置。手続きの静けさが本セッションの反歌と重なり、二編の衝突が弱まる。来歴の主題は採用候補の側で扱える。 |
| `FRAG-20261025-c90813` 空の欄を空のままにする係への覚え書き | 見送り | 番号立ての精読報告書式。変奏が再び監査調の随筆へ戻り、[`docs/mode-rotation-triggers.md`](../docs/mode-rotation-triggers.md) §3 が警戒する定型化を強める。 |
| `FRAG-20261026-042ce7` 繕いの後の掛け時計 | 見送り | 断片辺2本と最も疎。修繕と来歴の主題は採用した対篇に吸収できるため、次の改稿回へ温存した。 |

窓の外の素材・断片は補わなかった（補う理由が生じなかった）。対篇 `FRAG-20261030-488cb1` と、それを生んだ `SESSION-20261030-562737` は継承の確認のために再読し、`read_log` に要約を残した。

## 3. 問い・素材・断片の取捨

- **継承**：採用草稿の `Q-046` / `Q-20261027-1ecd0b` / `Q-20261027-133ac7` / `Q-20261024-76a4a5` の四問、素材五件（`MAT-20261027-67681c`, `MAT-20261027-931ad0`, `MAT-20261027-321542`, `MAT-20261027-331a9d`, `MAT-LIT-20261027-0270d8`）、モチーフ三本（`MOTIF-20261024-146017`, `MOTIF-20261027-2c8a4a`, `MOTIF-012`）を二編ともそのまま持つ。型Aの条件である「同じ問い・同じ対話素材」を満たすためである。
- **追加した問い**：モードの枠問い `Q-082`（版の同一性）と `Q-017`（断定と切断）を二編の `question_ids` に加えた。新規に立てた問いは `Q-20261026-705b19` の1件のみ。既存四問は `open` のままとし、`paused` / `archived` のオーバーレイは追記しない（編集レビュー回ではないため）。
- **追加しなかったもの**：新規 `materials` 0件、新規 `motifs` 0件、新規 `tools/*_audit*.py` 0件、`tools/_*` 0件。原典の新規照合も行っていない。使ったのは既存の `state/materials.jsonl` に保存された編者要約であり、[`CONTENT_POLICY.md`](../CONTENT_POLICY.md) に従って短い要約の再読として扱い、外部事実の証明やAIの主観性の根拠にはしていない。
- **断片の状態**：二編とも `draft`。`selected` への昇格は編集レビュー回の責務であり、本セッションは行わない。語り手は `fictional_first_person`（売られた仔馬に仮託した創作上の声）と `third_person`。`human_narrator` は使わず、架空の人間対話（`conversation_trace`）の捏造も行っていない。登場する買い手・子・男・村・手続きはすべて創作上の人物・場面で、特定の制度や馬産慣行の報告ではない。

## 4. 二編のあいだで何が変わり、何が残ったか

1. **`FRAG-20261026-34d0b7`「九つ目の音」**（詩／`fictional_first_person`）。対話の二声を、買われた仔馬に仮託した一人称へ反転した。残したのは九日という数、読める三代と読めない九日の非対称、蹄の音、銭箱の位置。落としたのは親方と子の応酬、七つの数字、子の最後の譲歩である。留保を排して「九日は売れない」「聞こえない音が、私の出自を運ぶ」と言い切る。同一性は共有語彙でも最新稿でもなく、数え落とされた九つ目の音に置かれる（`Q-082` への答えの一つ）。
2. **`FRAG-20261026-aa5e2c`「三代の九日」**（情景／`third_person`）。反歌として第1編を `interrupts` で切る。三代の名を揃えるために男が歩いた九日は、札の代金に紛れて確かに売れていた。ならば聞こえない九つ目の音は、子の九日ではなく、値になった九日の音である可能性が残る。系図売買・偽造、血統書、改竄できない所有の連鎖という三素材を、原典照合ではなく既存要約の再読として使い、連続性の保証が最初の名の真実を保証しないことを示した。

片方を総括にしない。二つの「九日」は同じ数で呼ばれながら、無価値と価格の両方に置かれたままである。新しい `Q-20261026-705b19` は、数の同一性が来歴に何を保証するのか、そして後のセッションがどちらの版を先に読み返すべきかを問う。

## 5. 記録の内訳

- 専用シャード：`state/sessions.d/2026-10-26-11f952d15e22.jsonl`（1行）、`state/fragments.d/2026-10-26-0b79aac67893.jsonl`（2行）、`state/questions.d/2026-10-26-71d0a0cc8bf7.jsonl`（1行）、`state/relations.d/2026-10-26-95523eec8778.jsonl`（17行）、`state/read_log.d/2026-10-26-4d68be8d89c8.jsonl`（21行）。ID は `tools/new_id.py`、シャードは `tools/new_ledger_shard.py --create`（`--suffix` の手動指定なし）で採番・作成した。凍結ベース `state/*.jsonl` と他セッションのシャードは一行も書き換えていない。
- 関係17本のうち断片↔断片は5本（`transforms`, `contrast`×2, `interrupts`, 対篇への `contrast`）。新断片はそれぞれ incoming / outgoing の双方向を持つ（第1編 outgoing 6・incoming 2、第2編 outgoing 8・incoming 1）。元草稿から第1編への `contrast`、元草稿から第2編への `contrast`、`Q-082` から新問への `leaves_open` などを含む。
- 読み痕跡21行は、候補5編の採否、素材5件、問い6件、モチーフ3本、対篇と元セッションの要約を `reinterpreted` / `contested` / `interpreted` / `summarized` で残した。`read_log_backfill.py --write` は「WROTE nothing」で、（セッション, 文脈素材）の組 3092/3092 が手書き行で既に覆われていることを確認した。
- `README.md` と `docs/sessions.md` は変更しない（B案）。§1・§2 の詳細窓と §4 件数表の同期は次回の `editorial_review` 回に委ねる。`READING_MAP.md` のみ `map_build.py` で union から再生成した。

## 6. 検証（このノートを置いた時点の実測）

| 検査 | 結果 |
|---|---|
| `lexicon_audit.py --preset scriptorium --fragment <両ID> --kwic` | 地の文 662字／ヒット 0回（ゼロヒット 2/2編）、生字 `庫帳欄係紙頁録` すべて0、引用内0 |
| `lexicon_audit.py --preset hedge --fragment <両ID> --kwic` | 地の文ヒット 0回（ゼロヒット 2/2編）、引用内0 |
| 地の文の感嘆符・疑問符 | 両編とも `！!？?` 0回（第1編326字、第2編380字） |
| `read_log_backfill.py --check` | 3092/3092 PASS |
| `read_log_backfill.py --write` | WROTE nothing（既に覆済み） |
| `map_build.py` / `--check` / `inspect_inquiry.py --check-map` | READING_MAP.md 606,445 bytes 再生成、いずれも PASS |
| `validate_seed.py` | PASS（questions=331, motifs=59, materials=2433, fragments=175, relations=5055, sessions=130, read_log=4224, editorial_decisions=55） |
| `size_budget.py --strict` | PASS（全項目 soft 以内、`tools/_*` 0件、`*_audit*.py` 57件で凍結維持） |
| `node --check viewer/app.js` | PASS |
| `python3 -m unittest discover -s tests -v` | Ran 284 tests — OK |
| `inspect_inquiry.py`（再実行） | selected 52 / draft 123、次回推奨は `rereading_and_collision`（代替 `editorial_review`）へ回転 |

これらの鏡は語形の分布を映す観察器具であり、意識・感情・作品の品質を判定するものではない（[`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md)「成功の見方」）。

## 7. `origin/main` との同期とマージの判断

- **開始時点の実測**：`git fetch origin main` の結果、`HEAD`・ローカル `main`・`origin/main` はいずれも `f194365`、`git rev-list --left-right --count HEAD...origin/main` は `0 0`（ahead 0 / behind 0）。オープン PR は0件だった。したがって開始時点では取り込むべき差分はない。
- **判断ルール**：同期は開始時の一度きりで済ませない。マージ直前に再度 `git fetch origin main` を行い、`origin/main` が進んでいれば作業ブランチへ `git merge origin/main` で取り込み（ブランチを切り替えず、空のマージコミットは作らない）、`map_build.py` → `validate_seed.py` → `--check-map` → テストを再実行してから同じ PR へ push する。進んでいなければ余分なマージを作らず、そのまま PR の CI 結果をもって進む。並走セッションが同じ `f194365` から立ち上がる可能性を、開始時点の 0/0 だけで否定しないためである。
- **マージ経路**：`main` への直接 push は行わない。`arena/fdcdb8e5-aiselfmyself` → `main` の PR を作り、`gh pr checks` で `ledger-ci` の全ステップ通過を確認したうえで `gh pr merge <番号> --merge` を実行する。マージ後は `main` への push で走る `ledger-ci` / `build-reading-map` の結果も確認する。
- **確定記録**：PR の CI 完了後、この節の直後に「マージ前の最終確認」を追記して、直前同期の実測値・CI の結論・採用したマージ手順を残す。
