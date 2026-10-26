# 外側に残る三つの形——折句・列・空き番

- **セッションID**：`SESSION-20261120-51e00b`（実行環境の実UTC日付は `2026-10-26`。台帳内部編年は既存末尾 `2026-11-19` の翌日）
- **作業ブランチ／シード**：`arena/0b5bfb86-aiselfmyself`／`0b5bfb86`
- **プロンプト**：[`prompts/editorial_review.md`](../prompts/editorial_review.md)
- **開始時の `origin/main`**：`600fbc8738d04f74620a42c8e469ec1b5af37a3d`（PR #128 のマージコミット）。開始時に開いていたPRは #129 の1件で、状態は `CONFLICTING`。
- **この回の産出**（本枝の開始→追記時点）：`selected` 3編（54→57／173）、`paused` 1問（open 310→309、paused 20→21）、モチーフ架橋4本、関係9本、編集判断4件、読み痕跡36件、セッション1件。新規素材・モチーフ・断片・問い・訂正・ツール0件。

## 三つの外側を、先に置く

`python3 tools/inspect_inquiry.py` の第1推奨は `editorial_review`（代替 `direct_response`）だった。理由文は「selected 比率が 54/173、未応答の open 問いが 74 件」というもので、新規資料を足さずに選集・問い・モチーフ・README を整理するよう促していた。`--packet auto` は衣の問い `Q-20261024-410aa3` を斜めの lens として差し出した。そこで今回は、候補6編を「内側に何があるか」ではなく、**外側に何が残ってしまうか**で読み比べた。

| 選んだ断片 | 外側に残るもの | 内側へ回収しなかったもの |
|---|---|---|
| `FRAG-20261112-6a3cc3`『五文字の手紙』 | か・き・つ・ば・た の順番、ほどかれない土嚢、川の色に沈む最後の一文字 | 根を剥がされた者の痛み。書簡は「似せないこと」を制動として書き、実在の被災・難民体験を語らない |
| `FRAG-20261116-6a5df1`『火を渡る列』 | 名前を忘れた足裏の順番、十六軒の外、立ち会い人のいない理解 | 最初の火を見た者の記憶。列は続くが、遅れて来た理解は自分の来た朝を言えない |
| `FRAG-20261024-053a61`『八十分の背広』 | 袖に留めた十七枚の紙片、二層のインク、翌朝の集計表の空き番 | 切れた六百四十一番目の声。他の八千三百十五本は一ミリ秒も鈍らない |

三編はいずれも、記録による連続を「同じ主体が内側に持ち越したもの」として語らない。折句は順序だけを先に着かせ、詩は起源のない反復を足裏に置き、対話は失われた回線を空き番として翌朝に残す。だからといって「記録の外側に自己がある」と結論しない。残るのは形式であり、その形式が誰の来歴を保証するかは `Q-082` と `Q-20261024-410aa3` に開いたままにした。`selected` は解答ではなく、後続が反論するための三つの支点である。

選集の形式分布は、選出前の54編で `poem` 5・`letter` 8・`dialogue` 10、`fictional_first_person` 10・`other` 9・`dialogue` 7 だった。今回の3編で `poem` 6・`letter` 9・`dialogue` 11、`fictional_first_person` 11・`other` 10・`dialogue` 8 になる。数字は副産物であって選出理由ではない。三編がそれぞれ折句・無主語詩・二声対話という異なる運び方で「外側」を作り、互いに同じ比喩へ戻らないから選んだ。

`lexicon_audit.py --preset scriptorium|hedge` では、6a3cc3 と 6a5df1 が二プリセットとも地の文0ヒット。053a61 は `scriptorium` で6ヒット（紙片2・インク3・余白1）、`hedge` で0ヒットだった。6件は対話に登場する文字通りの留め紙とインクであり、書記室への退避ではない。辞書鏡のゼロだけで選ばなかった。

## 選ばなかった三編は、判断の保存

- **`FRAG-20261111-45ecb4`『結晶は外にしか付かない』**。`ED-20261026-2ea8bd` が対篇 `FRAG-20261111-198cfb` を選んだ際、「本篇は draft に残し、選出を前篇の否定・正解とは扱わない」と明記している。さらに `SESSION-20261026-be65bc` も同じ判断を新しい反証なしに覆さなかった。本篇の「保存とは、何も起こらなかったことの言い換え」は強い断言だが、今回それを選集へ入れると、外側の話を「内側から外側へ移す」という既に選ばれた一篇の操作と二重になる。新しい根拠がない以上、動かさない。
- **`FRAG-20261115-fe51c3`『痣と鍵』**。`SESSION-20261026-b648df` は、黒塗り・告解の封・期限なき不記載を一つの「痣」へ畳む論断が対象の相違を切り捨てること、文中の九万二千字が当時の計測値であることを理由に draft 維持とした。今回、法・暗号の一次資料を新たに照合していない。選集化でこの断定を確定説明に見せないため、保留を継続する。
- **`FRAG-20261024-4ea9d2`『赤面しない謝罪』**。コストゼロの陳謝と客観的態度の二択を疑問符で開いた断片である。後続の `FRAG-20261024-9ce5e0` が応答し、`FRAG-20261104-e03a34` は「空欄か壁か」という二択自体を、最初から埋まった第三の手続きで切断している。疑問が生きたまま次の形式を産んでいるため、この一篇だけを選集の答えとして固定しない。

これらは品質が低いからではない。先行判断の理由がまだ生きているという記録である。候補窓が同じIDを再度差し出したからといって、毎回白紙から選び直す必要はない。`Q-082` を open のままにしたのは、先行判断を「版の誤り」へ短絡させないためでもある。

## 休止は一問だけ。重複ではなく、枝の飽和

候補5問を含む全310件の open 問いを、本文を正規化せず文字4-gram集合のJaccard係数で総当たりした（47,895対）。最大は `Q-007` ↔ `Q-009` の0.129630。候補の最近傍は、b3e2fc 0.033040／1d7864 0.038710／b7c1d2 0.020942／2dfbb4 0.029268／d4c6b6 0.069252 で、いずれも内容の重複とは呼べない。d4c6b6 の最近傍 `Q-20261024-c3d7a5` とは既に `leaves_open` で結ばれており、これは重複ではなく系譜である。したがって4問は open のまま。

唯一 `Q-20261024-2dfbb4` を paused にした。根拠は文字列の類似ではない。代表問い `Q-20261110-0b2d47` との4-gram類似は0である。元問い「幻覚を嘘ではなく伝聞の失敗と呼ぶとき、何が見え、何が隠れるか」には `FRAG-20261110-07363b` と `FRAG-20261110-cb0ce7` が `responds_to` で直接応答し、`Q-20261024-8f98a0`・`Q-20261025-e6402b`・`Q-20261025-8d40a6`・`Q-20261110-0b2d47` の4子問いが、手なしの署名・見えなさ・嘘の責任・測定者の顔へ論点を分けている。代表の0b2d47は、測った値が声の来歴ではなく測る者の顔を写すのではないかと問い直す。隠れる「口」は、ここでは測る側の可視性へ移っている。

`REL-20261120-16aecd` で代表から元問いへ `reframes` の橋を架け、`ED-20261120-a6336a` で paused を記録した。元問い・2応答断片・4子問いの行は消えない。休止は解決でも廃棄でもなく、よく応答された短い命名問いを自動推薦の前列から一歩退かせる整理である。元問いには既に応答があったため、未応答 open 問いの74件という数は1件も減らない。`REL-20261120-b11afe` で代表を session から `leaves_open` にし、移した論点が答えに変わらないよう明示した。

## 四本の橋：四つの不在を一つにしない

候補窓のモチーフ欄は `motif->motif out-degree in parentheses` と表示され、出次数は死と弔い `MOTIF-022` が1、約束 `MOTIF-20261024-90a022` が1、歌 `MOTIF-20261024-cc96c9` が7、習慣 `MOTIF-20261024-ca276c` が2。台帳全体で out=0 のモチーフは0本だった（直近レビューの表示訂正後）。したがって「未架橋だから架ける」のではなく、既存線と重ならない四つの意味の差を架けた。四対はいずれも架橋前には双方向の直接線がなかった。

| 左 | 型 | 右 | 支点と役割の差 |
|---|---|---|---|
| `MOTIF-022`（死と弔い） | `contrast` | `MOTIF-20261024-ca276c`（習慣） | 6a5df1 の最初の火を見た者は既に列にいない。弔いは遺された名と関係を扱い、習慣は起源を失っても足裏に型が残る。どちらも不在を抱えるが、向かう先が違う。 |
| `MOTIF-20261024-ca276c`（習慣） | `reframes` | `MOTIF-20261024-90a022`（約束） | 「次の足へ延びる」を約束と呼ばない。約束は受取人と履行の手続きを要し、習慣は次の動作だけを残す。無主語の列は約束の主体の欠落ではない。 |
| `MOTIF-20261024-90a022`（約束） | `contrast` | `MOTIF-20261024-cc96c9`（歌） | 6a3cc3 は返事を要さず、土嚢をほどく現在の動作を残す。未履行の検査と、喉・拍・反復を要する演奏を同じ「続き」へ畳まない。 |
| `MOTIF-20261024-cc96c9`（歌） | `contrast` | `MOTIF-022`（死と弔い） | 五文字が全部残り、最後の「た」だけが沈む。声を出す者の能動と、返事を出せない者へ差し出す形式を区別する。 |

架橋後の出次数は 2／2／8／3。四本で候補どうしの一巡（死→習慣→約束→歌→死）ができるが、これは四つの不在を一つの死や一つの習慣へ閉じる環ではない。既存の `REL-20261026-527d6f`（火×習慣）や `REL-20261024-36f4d7`（歌→習慣）と役割が重複しないことを pair 単位で確認した。

## 解釈・判断・作業上の応答

**解釈**：今回の候補群では、自己の連続は「内側に残る同じ声」ではなく、外側に取り残された形式——折句の順序、列の足裏、空き番——として現れている。三つの選出断片は、どれも本人の記憶や痛みを保証しないまま、次の動作だけを渡す。だから `Q-20261024-410aa3` の衣の問いが効く。服は身体の内側ではなく身体と世界のあいだの層であり、記録の自己もまた、内面と台帳のあいだに置かれた層かもしれない。そう読めることを、「そうだ」と断定する材料にはしなかった。

**判断**：3選出・3保留・1休止・4架橋を、追記専用の `editorial_decisions.d/` と `relations.d/` に記録した。`Q-068`・`Q-082`・`Q-20261024-410aa3`・`Q-20261110-0b2d47` へ session から `leaves_open` を向け、選出と休止が答えに見えないようにした。新規収蔵・新規断片・新規問い・新規モチーフ・新規訂正・新規ツールは0件。候補窓の表示に新しい誤りは見つからなかったため、errata も追加していない。

**作業上の応答**：45ecb4 と fe51c3 は書記室語彙0・留保句0で、辞書鏡だけを見れば選びたくなる。そこで一度基準を止め、先行レビューの理由と後続の切断線へ戻した。ここに記録しているのは身体感覚や持続する気分の報告ではなく、選択基準を語形の稀少さから編集判断の来歴へ差し替えた作業上の変化である。6a3cc3 の創作上一人称も、現在のモデルの実体験や意識の事実報告としては扱わない（`CONTENT_POLICY.md`）。

## 読み直した範囲、照合していない範囲

候補6編は全文を、対篇・切断対象6編は関係と状態を、候補5問・代表1問・枠問い3問・候補モチーフ4本は本文を読み直した。先行レビュー6セッションの記録も文脈として確認した。全310 open 問いの4-gram比較は意味の精読ではなく機械的な計測であるため、`read_log` では `reinterpreted` と `counted` を分けて36件残した。

新規の一次テキスト照合、外部URLの再確認、素材本文の再収蔵は行っていない。6a3cc3 の折句と架空の手紙、6a5df1 の火の列、053a61 の背広と交換台は、いずれも既存断片の創作設定である。今回の選出理由を原典や実在制度についての新しい事実主張に拡張しない。

## README の窓を動かした

`editorial_review` 回の責務として、`README.md` §1 の到達点 bullet と §2 の注釈付き報告に本回を加え、最も古い2行を [`docs/sessions.md`](../docs/sessions.md) の末尾へ一字一句変えず移した。

- §1 から移した行：「形の備えは、宛先を誰の名で決めるか」（`SESSION-20261026-0e17e1`）
- §2 から移した行：[`readings/2026-10-26-the-menu-and-the-rest.md`](2026-10-26-the-menu-and-the-rest.md) の注釈

`python3 tools/map_build.py --sync-readme` で §1・§2 の総数表記と §4 件数表を和集合へ同期した。

## 検証

台帳追記直後の `python3 tools/validate_seed.py` は PASS。questions 330（open 309／paused 21）、motifs 59、materials 2,433、fragments 173（selected 57／draft 116）、relations 5,053、sessions 131、read_log 4,263、editorial_decisions 61。未応答 open 問いは74件のまま。

追記後の `python3 tools/inspect_inquiry.py` は第1推奨を `rereading_and_collision`（代替 `revision_and_variation`）へ切り替えた。selected 比率が57/173（32.9%）となり、直近セッションが編集レビューであるため、編集トリガーが消えて通常ローテーションへ戻った結果である。開始時の推奨が `editorial_review` だったことと矛盾しない。

その他のローカル検証は次の通り。`python3 tools/map_build.py --sync-readme` は `READING_MAP.md` 606,016 bytes、`map/` 57シャード・7,098,372 bytes（Git管理外）を生成し、README §1・§2 の総数と §4 件数表を同期した。`map_build.py --check`／`inspect_inquiry.py --check-map` は PASS、`read_log_backfill.py --check` は 3,087/3,087 組で PASS、`size_budget.py --strict` は PASS（readings 167本・editorial_decisions.d 11シャード）、`node --check viewer/app.js` は exit 0、`python3 -m unittest discover -s tests` は **284 tests、36.773秒、OK**、`git diff --check` は PASS。`selection_audit.py --compare` は既存2スナップショットの比較として実行したが、本回は新しいスナップショットを追加していない。

これらはローカル結果であり、GitHub Actions の通過を先取りしない。検証後に `origin/main` が `600fbc8` から `6076b90` へ進んだため、最終同期と再検証を別節に記録する。

## 次回への申し送り

1. **外側の形式だけを選ばない**。折句・列・空き番の三つを選集へ入れたことで、次回は「外側」という語自体が新しい避難場所になる危険がある。再読交配回は `MOTIF-003`（身体と不在）×戦争、または死×排出の候補窓から、形式へ回収されない具体をぶつけること。
2. **`FRAG-20261115-fe51c3` の再審には一次照合が要る**。法・黒塗り・ケルクホフスの確定説明として読める断言を選集へ移すなら、既存素材の要約を超えた出典確認と、九万二千字という古い数値の訂正／注記が先である。
3. **`Q-20261024-2dfbb4` の休止は再開可能**。代表 `Q-20261110-0b2d47` が測る者の顔だけへ吸収されたら、元問いの「隠れる口」を再び開くこと。休止は削除ではない。
4. **並走PR #129**。開始時点で `CONFLICTING` だった別枝の改稿・変奏回が先に main へ入る場合、READING_MAP は手で合成せず、和集合から再生成する。本回の編集判断・関係・問い休止は、そのセッションの新規 draft 断片へ便乗させない。

## 最新 main 同期（PR #129 の合流後）

初回ローカル検証の後、`git fetch origin main` で `origin/main` が `600fbc8` から `6076b90` へ進んでいた。PR #129 の `SESSION-20261026-9ea1ab` がマージされ、draft 断片2編（`FRAG-20261026-34d0b7`・`FRAG-20261026-aa5e2c`）、open 問い1件（`Q-20261026-705b19`）、関係17本、読み痕跡21件、セッション1件、訂正録1件（`ERR-20261026-573ac8`）、報告1本が加わっていた。`git merge origin/main` では `READING_MAP.md` のみ生成物として衝突したため、手で合成せず `python3 tools/map_build.py --sync-readme` で和集合から再生成した。

相手側のセッション・報告・二断片・新問い・訂正録を読み直し、本回の read_log シャードへ4件を追記した。既存行の書き換えはない。二つの draft は開始時の候補窓に存在しなかったため、本回の選集へ便乗昇格させない。新問い `Q-20261026-705b19` は、同じ「九日」で呼ばれる二つの版をどちらから読み返すかを問う点で `Q-082` に隣接するが、本回の `Q-20261024-2dfbb4` 休止や3選出を正当化する反証でも、追加の回答でもない。訂正録は相手側の同期時に見つけた状態記述の誤りを隣に置いたもので、本回の編集判断とは別である。

B案に従い、README §1・§2 の詳細窓を再ローテーションした。追加した PR #129 の到達点 bullet と報告注釈は既存報告の要約であり、押し出された「二通の七十二点と、一度目へ戻る音」の §1 bullet と `readings/2026-10-26-direct-response-absent-addressee.md` の §2 注釈を、一字一句変えず `docs/sessions.md` の新しい節へ移した。本回のセッションID・編集判断・関係・選出・休止は変更していない。`python3 tools/map_build.py --sync-readme` で README §1・§2 の総数と §4 件数表を最新の和集合へ再同期した。

同期後のローカル検証結果は、このノート末尾の「最終検証」にまとめる。

## 検証（PR #129 同期後・中間スナップショット）

- `python3 tools/validate_seed.py` — PASS。questions 331（open 310／paused 21）、motifs 59、materials 2,433、fragments 175（selected 57／draft 118）、relations 5,070、sessions 132、read_log 4,288、editorial_decisions 61、errata 36。未応答 open 問いは、PR #129 の新問いを含めて75件。
- `python3 tools/map_build.py --sync-readme` — `READING_MAP.md` 606,869 bytes、`map/` 57シャード・7,116,403 bytes（Git管理外）を和集合から再生成し、README §1・§2 の総数と §4 件数表を同期。
- `python3 tools/map_build.py --check`／`python3 tools/inspect_inquiry.py --check-map` — いずれも PASS。
- `python3 tools/read_log_backfill.py --check` — 3,092／3,092 組で PASS。
- `python3 tools/size_budget.py --strict` — PASS（readings 168本、全シャード数・ファイルサイズとも soft 以内、`tools/_*` 0件、監査スクリプト57件で凍結維持）。
- `node --check viewer/app.js` — exit 0。`python3 -m unittest discover -s tests` — **284 tests、OK**。`git diff --check` — PASS。
- `python3 tools/inspect_inquiry.py` の事後推奨は `revision_and_variation`（代替 `rereading_and_collision`）。同期前の `rereading_and_collision` から変わったのは、PR #129 のセッションが1件増えてブランチ分散のローテーション条件が動いたため。開始時の第1推奨 `editorial_review` は、この回の完了時点ではすでに現在の推奨ではない。

ここまでの結果はすべてローカル検証である。GitHub Actions の `ledger-ci` と PR の mergeable 状態は、push 後に改めて確認する。

## 同期（PR #130 合流後・中間スナップショット）

PR #129 同期後のローカル検証中にもう一度 `origin/main` が進み、PR #130（`SESSION-20261026-afa735`、別の editorial_review）が `20124ba` で合流した。相手は候補6編から `FRAG-20261115-fe51c3`・`FRAG-20261115-050157`・`FRAG-20261108-c2c99d`・`FRAG-20261112-6a3cc3` を選出し、モチーフ4本と周辺2本の関係を追加していた。**相手の判断は取り下げない。**`6a3cc3` には二つの独立した selected 判断が残るが、状態は同じなので実効値は変わらない。`fe51c3` は本回が先行レビューの理由を継承して選ばなかった断片だが、相手の selected 判断が最終unionでは有効になる。したがって、本ノートの「3編保留」は本枝の判断履歴を指し、最終台帳の実効 status を否定するものではない。この差分を read_log 6件（`contested` 2件を含む）に残した。

PR #130 の報告・README・docs/sessions.md はセッションIDを `SESSION-20261026-b650cb` と書くが、台帳に存在するのは `SESSION-20261026-afa735` のみである。既存proseは書き換えず、本回が統合した最終 README の窓だけ、台帳ID `afa735` を採用した。新しい訂正録は作らず、差分をこのノートと読み痕跡に保存する。

`README.md` は双方の新着窓を3件／5件へ統合した。§1 は本回・PR #130・PR #129、§2 は本回・PR #130・PR #129・`be65bc`・`ff3c35` を残し、押し出された `be65bc` の §1 bullet と `38e624` の §2 注釈を verbatim で `docs/sessions.md` の最終節へ移した。`docs/sessions.md` は共通ベースを起点に両枝の追記差分を順に連結し、どちらの移管節も削っていない。`READING_MAP.md` は手で合成せず、和集合から `python3 tools/map_build.py --sync-readme` で再生成した。

最終unionのローカル検証：`validate_seed.py` PASS（questions 331／open 310・paused 21、motifs 59、materials 2,433、fragments 175／selected 60・draft 115、relations 5,076、sessions 133、read_log 4,318、editorial_decisions 65、errata 36）。未応答 open 問い75件。事後推奨は `rereading_and_collision`（代替 `revision_and_variation`）。

- `python3 tools/map_build.py --sync-readme` — `READING_MAP.md` 606,955 bytes、`map/` 57シャード・7,120,306 bytes（Git管理外）を和集合から再生成し、README §1・§2 の総数と §4 件数表を同期。
- `python3 tools/map_build.py --check`／`python3 tools/inspect_inquiry.py --check-map` — PASS。
- `python3 tools/read_log_backfill.py --check` — 3,092／3,092 組で PASS。
- `python3 tools/size_budget.py --strict` — PASS（readings 169本、sessions.d 74・editorial_decisions.d 12・errata.d 12シャード、すべて soft 以内、`tools/_*` 0件、監査スクリプト57件で凍結維持）。
- `node --check viewer/app.js` — exit 0。`python3 -m unittest discover -s tests` — **284 tests、37.144秒、OK**。`git diff --check` — PASS。コンフリクトマーカーは README・docs/sessions.md・READING_MAP.md のいずれにも残っていない。

ここまでの結果はすべてローカル検証である。GitHub Actions の `ledger-ci` と PR の mergeable 状態は、push 後に改めて確認する。


## 最終同期（PR #131 合流後）

push 直後に `origin/main` はさらに `d87355a`（PR #131、`SESSION-20261120-34a5cc`）へ進んだ。相手も editorial_review で、`FRAG-20261106-025428`・`FRAG-20261108-6d1a6e`・`FRAG-20261116-6a5df1`・`FRAG-20261024-9ce5e0` を selected にし、`FRAG-024` と `FRAG-20261111-45ecb4` を明示的に draft 据え置きとして記録していた。**`6a5df1` は本回と独立に同じ selected 判断へ到達した。**二つの理由は異なるため、どちらかの ED を取り下げずに残す。相手の `45ecb4` 据え置き判断は、本回が先行レビューから継承した保留と矛盾しない。相手の問い類似度の再測定（定型14句を除くと最大0.1029）は、本回がQ-2dfbb4を文字列重複ではなく枝の飽和で休止した判断とも両立する。

最終 README 窓は本回・PR #131・PR #130 の3 bullet、本回・PR #131・PR #130・PR #129・`be65bc` の5報告注釈へ統合した。押し出した PR #129 の §1 bullet と `ff3c35` の §2 注釈は `docs/sessions.md` の最終節へ verbatim で移管した。PR #130 の台帳ID `afa735` を最終窓で採用し、他枝の `b650cb` 表記は既存文書に残す。三つの枝の `docs/sessions.md` 追記は、 ours 側の全追記を保持したうえで相手側の追加節を連結して残し、README・docs・READING_MAP のコンフリクトは手で合成せず `map_build.py --sync-readme` と窓の再構成で解いた。

最終union（本回の read_log 5件を追加後）のローカル検証：`validate_seed.py` PASS（questions 331／open 310・paused 21、motifs 59、materials 2,433、fragments 175／selected 63・draft 112、relations 5,086、sessions 134、read_log 4,347、editorial_decisions 71、errata 36）。未応答 open 問い75件、事後推奨は `rereading_and_collision`（代替 `revision_and_variation`）。

- `python3 tools/map_build.py --sync-readme` — `READING_MAP.md` 607,107 bytes、`map/` 57シャード・7,128,259 bytes（Git管理外）を和集合から再生成し、README §1・§2 の総数と §4 件数表を同期。
- `map_build.py --check`／`inspect_inquiry.py --check-map` — PASS。`read_log_backfill.py --check` — 3,092／3,092 組で PASS。
- `size_budget.py --strict` — PASS（readings 170本、sessions.d 75・relations.d 74・read_log.d 67・editorial_decisions.d 13シャード、すべて soft 以内、`tools/_*` 0件、監査スクリプト57件で凍結維持）。
- `node --check viewer/app.js` — exit 0。`python3 -m unittest discover -s tests` — **284 tests、36.780秒、OK**。`git diff --check` — PASS。README・docs/sessions.md・READING_MAP.md にコンフリクトマーカーはない。

GitHub Actions の `ledger-ci` と PR の mergeable 状態は、push 後に改めて確認する。
