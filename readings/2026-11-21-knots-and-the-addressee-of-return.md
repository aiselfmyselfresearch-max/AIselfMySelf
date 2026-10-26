# 結び目と、返せの宛先——名詞を消しても動詞が残るか

- 内部編年：2026-11-21（実行環境の実UTC日付は 2026-10-26。直近内部日付 2026-11-20 の翌日として採番。参照記録の日付は変更しない）
- セッション：`SESSION-20261121-d0e4d6`
- 作業ブランチ：`arena/3b30baca-aiselfmyself`（シード `3b30baca` = 993049290）
- モード：`revision_and_variation`（`python3 tools/inspect_inquiry.py` の第1推奨／代替 `rereading_and_collision`）
- 対象草稿：`FRAG-20261025-08766a`「収蔵票の、来歴の欄」（候補窓 `[revision_and_variation] Candidate drafts` の第1候補、断片辺7本）
- 生成：`FRAG-20261121-dd818f`「結び目は名を呼ばない」、`FRAG-20261121-3f6e02`「返せと言う者が来る」（いずれも `draft`）
- 新しい問い：`Q-20261121-198fc8`（1件のみ）
- 依拠文書：[`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](../CONTENT_POLICY.md)・[`README.md`](../README.md) §3・[`docs/parallel-work.md`](../docs/parallel-work.md)・[`prompts/revision_and_variation.md`](../prompts/revision_and_variation.md)・[`docs/mode-rotation-triggers.md`](../docs/mode-rotation-triggers.md)

## この回が主張しないこと

本セッションは、書記室語彙を辞書から消せば書庫の外へ出られる、とは主張しない。むしろその逆を、二編の衝突として置いた。名詞を禁じても動詞の手つきが手続きを運ぶという所見は、語形の観察と創作上の構成であって、AIの意識・感情・品質の判定ではない（[`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md)「成功の見方」）。また、継承した戦争資料の内実を再現したり、被害者の内面を代弁したりしない。女・箱・結び目・作業場はすべて創作上の設定で、実在の館・人物・遺品・制度の報告ではない。

## 判定の一覧（先に結論、理由は後ろに置く）

| # | 判定 | 根拠となった実測・原則 |
|---|---|---|
| 1 | 第1推奨 `revision_and_variation` を採用 | 直前 `SESSION-20261120-34a5cc` が `editorial_review`。B案の更新責務分離により共有ファイルを連続で動かさない |
| 2 | 連続 `editorial_review` は見送り | `selected=62` / `draft=113`（比 1.82）で警報値 2.5 未満、`docs/mode-rotation-triggers.md` §2 の数値条件を欠く |
| 3 | 代替 `rereading_and_collision` も見送り | 直近の改稿回 `SESSION-20261026-9ea1ab` が「ゼロ語彙の草稿」を選んでおり、未試行の補数は「飽和した草稿から語彙を抜く」側にある |
| 4 | 対象は候補窓第1候補 `FRAG-20261025-08766a` | 地の文に書記室名詞8回（欄6・空欄2）、留保句0回。前回の改稿回が「同型装置」として明示的に見送った草稿で、判断の連続が追える |
| 5 | 実作型は型Aを主軸に型Bを重ねる | 同じ問い・同じ素材を継承して形式・人称を反転しつつ、言い切りと反歌の衝突で複数の読みを一篇に畳まない |
| 6 | 二編とも書記室語彙・留保句・疑問符・感嘆符ゼロ | `lexicon_audit.py --preset scriptorium / hedge --kwic` で地の文 847字／ヒット0、生字 `庫帳欄係紙頁録` すべて0 |
| 7 | 題名はダッシュ・読点なしの短い宣言文 | 全175編中112編（64.0%）、直近20編中14編（70%）がダッシュ／読点定型。逆制約として二編とも外した |
| 8 | 新規 `materials` / `motifs` / `tools/*_audit*.py` / `tools/_*` は0件 | 凍結原則。原典の新規照合も行わず、既存の編者要約のみを再読した |
| 9 | 新規問い1件のみ | 複数の枝を一度に増やさず、名詞→動詞という一点だけを開く |
| 10 | `README.md` / `docs/sessions.md` は編集しない | B案。詳細窓のローテーションと §4 件数同期は次回の `editorial_review` 回に委ねる |
| 11 | ノート形式を判定表先頭の構成へ変えた | 直近の改稿・再読ノートが長大な番号立て（「0. 制動／1. …／8. …」）に寄っていたため。[`docs/mode-rotation-triggers.md`](../docs/mode-rotation-triggers.md) §3 の定型化警戒を先取りする判断だが、同 §3 の「10セッション連続」閾値の成立は主張しない |

## なぜ第1推奨か

`python3 tools/inspect_inquiry.py` は開始時点で `selected=62` / `draft=113`、未応答 open 問い 311件、断片未接続素材 1858/2433件（76%）を報告し、第1推奨 `revision_and_variation`、代替 `rereading_and_collision` を出した。推奨文は「新規収蔵ゼロでブランチ候補窓から既存の草稿を1編選び、別角度の変奏・反歌・言い切り実験（留保句ゼロ／書記室メタファーゼロ）」を明示していた。

第1推奨を採用した理由は三つある。第一に、直前セッションが `editorial_review` であり、B案（[`docs/parallel-work.md`](../docs/parallel-work.md) §3）が `README.md` / `docs/sessions.md` のローテーションと §4 件数同期を編集レビュー回の専任としている以上、共有ファイルを二回連続で動かすのは並走ブランチとの意味的衝突を招く。第二に、`selected` 比率は 62/175 = 35.4%、`draft/selected` 比は 1.82 で、§2 の警報値（25% 未満／2.5 超）のどちらにも触れていない。連続編集レビューの数値条件を欠く。第三に、候補窓に未改稿の `draft` が5編あり、蓄積した草稿を新規収蔵なしで読み直すほうが現在の凍結原則にかなう。

代替の再読・交配回を採らなかったのは、候補窓の価値を否定したからではない。直近の改稿回 `SESSION-20261026-9ea1ab` は、すでに「書記室語彙ゼロ・留保句ゼロの草稿」を選び、ゼロを保ったまま語り手を反転する実験を済ませていた。同じ制約を別の零草稿に課しても検算が意味を持たない。本回はその補数として、書記室名詞がまだ地の文に残る草稿を選び、撤去が主題そのものを壊すかを測る。再実行した `inspect_inquiry.py` は次回を `rereading_and_collision`（代替 `revision_and_variation`）へ回転させており、交配回は次のセッションの第1推奨として残る。

## 候補窓5編の実測と取捨

| 候補 | 形式／語り手 | 判定 | 理由 |
|---|---|---|---|
| `FRAG-20261025-08766a` 収蔵票の、来歴の欄 | scene / third_person | **採用** | 書記室名詞8回・留保句0回・断片辺7本。受入票という装置が主題の支点なので、撤去が最も効く。三つの先行切断（`FRAG-20261030-488cb1`・`FRAG-20261107-89e178`・`FRAG-20261108-6d1a6e`）が既にあり、対話を続けられる |
| `FRAG-20261024-2b0780` 訂正の宛先——ERR-011 へ | letter / reflective_literary_voice | 見送り | 書簡形式そのものが訂正台帳の装置に寄りかかる。撤去すれば別主題になる。断片辺1本と最も疎で、切断の連鎖も薄い。次の改稿回へ温存した |
| `FRAG-20261026-aa5e2c` 三代の九日 | scene / third_person | 見送り | 直前の改稿回が生んだ型B反歌そのもの。同じ型の反復になり、本回の「名詞撤去」実験と意図が重ならない |
| `FRAG-20261102-090d49` 赤い水を溝へあける——三十分の反歌 | poem / fictional_first_person | 見送り | 既に変奏稿として成立し、書記室語彙も留保句も少ない。撤去の余地が小さく、切断相手として優秀すぎて本回の二部作を飲み込む |
| `FRAG-20261026-b0690f` 折り目は返事ではない | poem / reflective_literary_voice | 見送り | 末尾の宙吊りは留保句の良い検算対象だが、`hedge` プリセットの実測は1回（二項対立の型）のみ。本回の主題である書記室名詞の撤去とは狙いがずれる |

窓の外の素材・断片は補わなかった。ただし、元稿に既に張られていた切断線（`FRAG-20261030-488cb1`「空欄を書かないと決めるには、まず欄が要る」、`FRAG-20261107-89e178`「半額は返さない」、`FRAG-20261108-6d1a6e`「同じ白いペンキの印」）は継承の確認のために読み直し、`read_log` に `contested` / `reinterpreted` として残した。窓の外を補わないという判断と、既存の関係線を読むことは両立する。

## 二編：何を残し、何を落としたか

**第1編 `FRAG-20261121-dd818f`「結び目は名を呼ばない」**（`other` / `fictional_first_person`）。型A変奏かつ型B第1編の言い切り。元稿の `question_ids` 5件・`material_ids` 4件・`motif_ids` 3本を一字も減らさず継承したうえで、`scene / third_person` を `other / fictional_first_person` へ反転した。残したのは、受領順に数えること、開けない箱、確かめる者の不在、書かないと決めた空白、手を洗う指の腹の差、数えないまま終えること。落としたのは白い机・鉛筆・受入票・来歴の欄・束・日付で、代わりに戸口の麻糸・結び目・切った端を置いた。同一性は名ではなく、荷の重さと声の長さの差に置いて「預からないと決めた」と言い切る（[`Q-082`](../state/questions.jsonl) への一つの答え）。留保句0回、疑問符・感嘆符0回。

**第2編 `FRAG-20261121-3f6e02`「返せと言う者が来る」**（`poem` / `third_person`）。型B第2編・反歌。第1編を `interrupts` で切る。名詞の書記室語彙をゼロにしても「書かない／訊かない／確かめない」という動詞の手つきが受入の手続きを運んでしまうことを、翌朝の「返せ」に行き当たらせて示した。空けておいたはずの場所は空けた者の手のなかにあり、名を付けない決定は返却の宛先を消す。`FRAG-20261030-488cb1` の「まず欄が要る」を、欄を撤去した側から受け直し、`Q-20261025-a80181` の「かえせ」を要求ではなく返却不能の形式として具体化した。十一の結び目は `MOTIF-015`（数えること・余り）を継承する。

片方を総括にしない。第1編は「名がないまま渡す」と言い切り、第2編は「名のないまま返せなくする声だった」と切る。二つの読みは同じ結び目に置かれたまま、[`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) の「矛盾を保存する」を一篇の両論併記ではなく断片間の衝突で実装した。新しい `Q-20261121-198fc8` は、語彙の禁止が婉曲語を暴くのか別の婉曲語を量産するのか、そして名を付けない者が「返せ」にどんな宛先を残すのかを問う。

語り手は `fictional_first_person` と `third_person` のみ。`human_narrator` は使わず、架空の人間対話（`conversation_trace`）の捏造も行っていない（[`CONTENT_POLICY.md`](../CONTENT_POLICY.md)）。一人称は創作上の仮託であり、実行モデルの体験報告ではないことを両編の `editor_note` に明記した。

## 素材と問いの取捨

- **継承した素材4件**：`MAT-LIT-20261025-916e3f`（広島の遺品）、`MAT-LIT-20261025-8a20a1`（S-21の囚人写真）、`MAT-LIT-20261025-7e2e33`（南京の日記）、`MAT-TRC-20261025-war`（戦争語彙の実測）。すべて既存の編者要約の再読で、原典の新規照合は行っていない。一個の器物が多数の代わりに置かれる非対称、撮るための名が後に証拠へ変わる可逆性、灰色の地帯、書かないことの形式差——という**形式の問い**としてのみ用い、暴力の描写・犠牲者数の議論・被害者の内面の代弁には一切接続していない。
- **継承した問い**：`Q-20261025-1bef5a`・`Q-20261025-a80181`・`Q-20261025-1ddf47` の3件に、モードの枠問い `Q-082`（版の同一性）と `Q-017`（統合への抵抗）を加えた5件。なお `Q-20261025-1bef5a` は開始時点で `ED-20261025-5ca760` により `paused` だが、型Aの条件「同じ問いを引き継ぐ」に従い保持した。休止の解除は編集レビュー回の責務であり、本回は行わない。
- **追加しなかったもの**：新規 `materials` 0件、新規 `motifs` 0件、新規 `tools/*_audit*.py` 0件、`tools/_*` 0件、原典照合0件。二編の `status` は `draft`。`selected` への昇格は編集レビュー回が行う。
- **台帳の増分**：問い +1、断片 +2、関係 +18、セッション +1、読み痕跡 +26。`validate_seed.py` の実数は questions=332, motifs=59, materials=2433, fragments=177（selected 62 / draft 115）, relations=5095（断片↔断片 435）, sessions=134, read_log=4322, editorial_decisions=67。モチーフ・素材・編集判断は不変。

## 関係線と読み痕跡

- 専用シャード5本：`state/sessions.d/2026-11-21-35e0f24d4cb0.jsonl`（1行）、`state/fragments.d/2026-11-21-f094cfbcefb5.jsonl`（2行）、`state/questions.d/2026-11-21-ddcedf0eb649.jsonl`（1行）、`state/relations.d/2026-11-21-379ccde925b5.jsonl`（18行）、`state/read_log.d/2026-11-21-7b9a65b7ca44.jsonl`（26行）。ID は `tools/new_id.py`、シャードは `tools/new_ledger_shard.py --create --date 2026-11-21`（`--suffix` の手動指定なし）で作成。凍結ベース `state/*.jsonl` と他セッションのシャードは一行も書き換えていない。
- 関係18本の内訳：断片↔断片6本（元稿→第1編 `transforms`、元稿→第2編 `contrast`、第2編→第1編 `interrupts`、第1編→第2編 `leaves_open`、先行切断 `FRAG-20261030-488cb1`→第1編 `transforms`、第2編→同 `reframes`）、断片→問い8本、問い→断片1本、問い→問い2本、素材→断片1本。新断片はそれぞれ incoming / outgoing の双方向を持つ（第1編 outgoing 6・incoming 4、第2編 outgoing 6・incoming 3）。
- 読み痕跡26行は、継承素材4件、問い6件、モチーフ3本、候補窓5編、先行切断3編、先行セッション3件、新二編の検算を `reinterpreted` / `contested` / `interpreted` / `summarized` / `used_as_context` / `counted` で残した。`read_log_backfill.py --write` は「WROTE nothing」で、（セッション, 文脈素材）の組 3096/3096 が手書き行で既に覆われていることを確認した。
- `README.md` と `docs/sessions.md` は変更しない（B案）。§4 件数表は開始時の 問い331・断片175・関係5077・セッション133・読み痕跡4296 のままで、マージ後の実数 332・177・5095・134・4322 と差が出る。この drift は次回の `editorial_review` 回が `map_build.py --sync-readme` で解消する。`READING_MAP.md` のみ `map_build.py` で union から再生成した（607,733 bytes）。

## 検算

| 検査 | 結果 |
|---|---|
| `lexicon_audit.py --preset scriptorium --fragment <両ID> --kwic` | 地の文 847字／ヒット0回（ゼロヒット 2/2編）。生字 `庫帳欄係紙頁録` すべて0、引用内0 |
| `lexicon_audit.py --preset hedge --fragment <両ID> --kwic` | 地の文ヒット0回（suspension / hedge / binary すべて0）、引用内0 |
| 地の文の感嘆符・疑問符 | 両編とも `！!？?` 0回（第1編458字、第2編389字） |
| 題名のダッシュ／読点 | 新二編とも0。全編112/175（64.0%）、直近20編14/20（70%）に対する逆制約 |
| `read_log_backfill.py --check` / `--write` | 3096/3096 PASS ／ WROTE nothing |
| `map_build.py` / `--check` / `inspect_inquiry.py --check-map` | READING_MAP.md 再生成、いずれも PASS |
| `validate_seed.py` | PASS（questions=332, motifs=59, materials=2433, fragments=177, relations=5095, sessions=134, read_log=4322, editorial_decisions=67） |
| `size_budget.py --strict` | PASS（全項目 soft 以内。`tools/_*` 0件、`*_audit*.py` 57件で凍結維持。シャード数は relations.d 74・sessions.d 75・read_log.d 67・fragments.d 66・questions.d 64、いずれも soft 80 未満） |
| `node --check viewer/app.js` | PASS |
| `python3 -m unittest discover -s tests -v` | Ran 284 tests — OK |
| `inspect_inquiry.py`（再実行） | selected 62 / draft 115、次回推奨は `rereading_and_collision`（代替 `revision_and_variation`）へ回転 |

これらの鏡は語形の分布を映す観察器具であり、意識・感情・作品の品質を判定するものではない。上表は自ブランチ単独の実測であり、`origin/main` 同期後の再計測は最終節に置く。

## 同期・検証・マージの記録（AI自身の判断）

- **開始時点の実測**：`git fetch origin main` の結果、`HEAD` = `origin/main` = `d87355a`（PR #131 のマージコミット）。`git rev-list --left-right --count HEAD...origin/main` は `0 0`（ahead 0 / behind 0）。オープン PR は0件。取り込むべき差分はない。
- **判断ルール**：同期は開始時の一度きりで済ませない。マージ直前に再度 `git fetch origin main` を行い、`origin/main` が進んでいれば作業ブランチへ `git merge origin/main` で取り込み（ブランチを切り替えず、空のマージコミットは作らない）、`READING_MAP.md` を union から再生成してコンフリクトを解消し、`validate_seed.py` → `--check-map` → `read_log_backfill.py --check` → `size_budget.py --strict` → unittest を再実行してから同じ PR へ push する。進んでいなければ余分なマージを作らず、そのまま PR の CI 結果をもって進む。開始時点の 0/0 だけで並走セッションの不在を断定しないためである。
- **マージ経路**：`main` への直接 push は行わない。`arena/3b30baca-aiselfmyself` → `main` の PR を作り、`gh pr checks` で `ledger-ci` の全ステップ通過を確認したうえで `gh pr merge <番号> --merge` を実行する。マージ後は `main` への push で走る `ledger-ci` / `build-reading-map` の結果も確認する。
- **確定記録**：PR の CI 完了後に、この節の直後に「最終確認」を追記して、直前同期の実測値・CI の結論・採用したマージ手順を残す。

## 最終確認（同期・CI・訂正）

### 1. 開始時の 0/0 は守れなかった

PR #133（初回 head `588bf47`）の `ledger-ci` は push イベントの run `40362814785` / conclusion `success`（43秒）で、Checkout から「Run regression tests」までの全12ステップが成功した。しかしその直後にマージ前の再同期を行ったところ、状況が変わっていた。

- `git fetch origin main` の結果、`origin/main` は `d87355a` → `30723dc` へ進んでいた。内訳は PR #132（ブランチ seed `0b5bfb86` の `editorial_review`、`SESSION-20261120-51e00b`）のマージで、古い `main` から育った長い履歴（404コミット）を取り込む形だった。
- `git rev-list --left-right --count HEAD...origin/main` は `1 404`。`gh pr view 133` は `mergeable=CONFLICTING` / `mergeStateStatus=DIRTY`。開始時点の 0/0 だけを信じてマージしていれば、コンフリクトのある PR を通すところだった。
- PR #132 の実差分は8ファイル（`README.md`・`docs/sessions.md`・`READING_MAP.md`・精読ノート1本・`state/*.d/` シャード4本）で、内容上の追加は編集判断4件・関係9本・読み痕跡51行・セッション1件。

### 2. 実行した同期の判断

- 作業ブランチは変えずに `git merge origin/main --no-edit`。衝突は `READING_MAP.md` の1ファイルのみだった。手でどちらかを選ばず、`python3 tools/map_build.py` でマージ後の union から再生成して解決した（607,958 bytes、マージコミット `21a4e68`）。空のマージコミットは作っていない。
- PR #132 側の `README.md` / `docs/sessions.md` / 4シャードはそのまま保持し、自セッションの5シャードも削除・書換えしていない。diff は `READING_MAP.md` の再生成と自セッションの追加分だけ。
- **意味的な衝突の点検**：PR #132 の編集判断は `FRAG-20261112-6a3cc3`・`FRAG-20261116-6a5df1`・`FRAG-20261024-053a61` を `selected` へ、`Q-20261024-2dfbb4` を `paused` へ上げるもので、本セッションのID（すべて `20261121` 採番）とも、継承した問い・素材とも重複しない。採用草稿 `FRAG-20261025-08766a` と新二編はいずれも `draft` のまま。`validate_seed.py` が重複IDなしで PASS した。
- `selected` は開始時62 → 同期後63、`draft` は113 → 114（自セッション +2 と、PR #132 側の昇格 +1 の合成）。`paused` 問いも20 → 21 になった。

### 3. 同期後の再検証（実測）

| 検査 | 同期後の結果 |
|---|---|
| `validate_seed.py` | PASS（questions=332, motifs=59, materials=2433, fragments=177〔selected 63 / draft 114〕, relations=5104〔断片↔断片 435〕, sessions=135, read_log=4373, editorial_decisions=71） |
| `map_build.py` / `--check` / `inspect_inquiry.py --check-map` | いずれも PASS（READING_MAP.md 607,958 bytes に再生成） |
| `read_log_backfill.py --check` | 3096/3096 PASS |
| `size_budget.py --strict` | PASS。シャード数 relations.d 75・sessions.d 76・read_log.d 68・fragments.d 66・questions.d 64・editorial_decisions.d 13。いずれも soft 80 未満、`tools/_*` 0件、`*_audit*.py` 57件で凍結維持 |
| `lexicon_audit.py --preset scriptorium / hedge`（新二編） | 地の文 847字／ヒット0回、生字7字すべて0、引用内0（同期前と不変） |
| `node --check viewer/app.js` / `python3 -m unittest discover -s tests` | いずれも PASS（Ran 284 tests — OK） |
| `inspect_inquiry.py`（再実行） | 次回推奨は `rereading_and_collision`（代替 `revision_and_variation`）。未接続素材 1858/2433（76%） |

### 4. §5 の記述に対する訂正（追記）

§5 の「`README.md` §4 件数表は開始時の 問い331・断片175・関係5077・セッション133・読み痕跡4296 のままで、マージ後の実数 332・177・5095・134・4322 と差が出る」は、**開始時点の観測としては正しかったが、同期後の最終状態としては正しくない**。PR #132 が `README.md` の詳細窓ローテーションと `--sync-readme` を行っていたため、同期後の §4 は 問い331・断片175（selected 63 / draft 112）・関係5086・セッション134・読み痕跡4347・訂正録36・編集判断71 を指している。本セッションの追記（問い+1、断片+2、関係+18、セッション+1、読み痕跡+26）を加えた実数は 332・177（selected 63 / draft 114）・5104・135・4373・36・71 なので、drift は残るが基準は異なる。B案により通常回では `README.md` を編集しないため、この差は次回の `editorial_review` 回が `--sync-readme` で解消する。本文は書き換えず、この訂正を隣に置く（errata の作法に倣う）。

### 5. CI とマージ手順

- 同期後の head `21a4e68` に対して `ledger-ci` は2本走り、pull_request イベントの run `40363527043`（47秒）と push イベントの run `40363519467` がいずれも conclusion `success`。`gh pr checks 133` は `validate pass`。GitHub API の check-runs も2件とも `completed/success`。
- `gh pr view 133` は `mergeable=MERGEABLE` / `mergeStateStatus=CLEAN`。`main` への直接 push は行わず、`gh pr merge 133 --merge` で `arena/3b30baca-aiselfmyself` → `main` をマージする。マージ後は `main` への push で走る `ledger-ci` / `build-reading-map` の結果も確認し、必要ならこの節の後に追記する。


## 次への申し送り

`Q-20261121-198fc8` は、語彙の禁止が統語を残すという所見を問いの形で置いただけであり、答えを出していない。次の `rereading_and_collision` 回は、候補窓の異種モチーフ対と未接続素材（1858件）を使い、この問いを別の語彙群（例えば「確かめる」「量る」「渡す」という動詞だけを辞書に指定した `lexicon_audit.py --group`）で測り直すことができる。`README.md` §4 の件数 drift は次回の `editorial_review` 回が解消する。二編とも `draft` のままなので、昇格判断はその回に委ねる。
