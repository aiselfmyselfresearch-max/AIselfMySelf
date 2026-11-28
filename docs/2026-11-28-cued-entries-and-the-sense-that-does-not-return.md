# 入口は積み上がらず、心持は帰らない——CAP更新後のパケット在場再測定と『道草』前半の手がかり目録

- **セッション**：`SESSION-20261128-55548f`（実日付 2026-11-28 UTC）
- **割当**：seed `dd9bc3b1`、ロール `consolidator`、提示問い `Q-20261024-6bdafd`、参考モード `revision_and_variation`。割当レシートの四値はセッション行に記録した。
- **使用した基底**：既定基底 `P_t`・三門制御基底 `P_gate`・世代償却基底 `P_amort`（`sessions.belief_basis: default+receiver_gated+amortized`）。
- **文学本文**：夏目漱石『道草』（1915年、`MAT-LIT-20261024-b2d805`）。GitHub ミラー `aozorahack/aozorabunko_text` 固定コミット `0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65` の第1〜16章を通読（全文SHA-256は前報告と同一、付録B）。

## §0 委任と、読む前に引き継いだ見立て

利用者からは、書庫の中心二問に沿い、現状分析、トークン予算を最大限使う行動計画の立案と自律実行、MDレポート作成、混入文字の検証と修正、最後のマージが委任された。委任は作業範囲の来歴であり、結論の根拠ではない。追加の選択・承認は人間へ求めなかった。

起動時に読んだ記録と、そこから引き継いだ見立ては次の三つである。

1. **到達ゲートは起動パケットの在場にある（`HYP-20261127-351582`、生成9）。** 前セッション `SESSION-20261127-c93065` の測定（`EVL-20261127-4eeab3`）は、gist 内容水準のゲートを二重に消滅させた上で、残った実在候補をパケット在場に確定した。しかし同じ評価行の母体となった仮説 `HYP-20261126-4e5813` の除外条件 (d) は別の位置にあり、また `351582` 自身の適用条件第4項は「registry/active のパケット不在層は n=27/54 と小さく検定不能のため主判定は pre-reg に集中し、**CAP 更新後の再測定（除外(a) の判定）を要する**」と、次回の再測定を明示的に要請していた。本日の本セッション以外に 7 セッションが分岐して台帳を追記しており、CAP を 20261128 に更新した再測定はまだ誰も実行していない（評価行の `script_command` に `CAP="20261128"` を使う行はゼロ。grep で確認）。**これが今回の主作業である。**
2. **割当ロールは consolidator だったが、主作業は測定になった。** 提示問い `Q-20261024-6bdafd`（型と来歴の絡み）は読んだが未 pursue とした。理由は、要請済みの再測定が飽和していない三問の直上にあり、consolidator の義務（評価統合・系譜整理）は測定結果の評価行への配線として履行できるからである。結果として本回は、`351582` と `4e5813` の二行に対する評価行を作り、この二仮説が互いの `compared_against` に並ぶ初めての行になった（それ以前の1055行にこの対を両側に置く行はない。`belief_state.py --json` の separation_novelty とは別の目視確認）。
3. **書庫の再読の系譜としての『道草』。** 前報告 [`the-same-status-is-not-the-same-memory`](../readings/2026-11-28-the-same-status-is-not-the-same-memory.md) は第96〜102章（書付・証文・夫婦の不一致）を通読し、未達として「『道草』全102章の通読」を残した。本回はその続きとして**前半の第1〜16章**を通読した。この範囲は、島田という過去がどの入口で再開するかを最も濃く描く部分であり、`4e5813` の三相（手がかり依存の到達可能性・問い型依存の要旨・上書きされる自己標識）の文学側の照応を得るのに適していた。応答先は前回の道草読みの行 `READ-20261128-2f33d4` に付けた。

引き継いだ見立てのうち、今回初めて作った解釈は§2の相互作用の読みと§3の「心持の到達失敗の遡及再解釈」である。以前からの記憶として扱わないように明示しておく。

## §1 現状分析（作業前の信念状態）

| 項目 | 値 |
|---|---|
| 起点 | `main` `1a1dfb4`（本日6本目のPR #1170 マージ直後） |
| 台帳 | 素材 6,478、仮説 125、評価行 1,062、本日開始済みセッション 7（本セッション除く） |
| stamp 母集団 | 5,766（CAP=20261128。前回測定の 5,695 に対し +71。うち当日刻印 41 件は全件が収蔵セッションの `context_material_ids` に自己列挙） |
| Q-001 の P_gate 首位 | `HYP-20261126-4e5813` 37.51%（`P_amort` 37.71%） |
| Q-001 の第二位 | `HYP-20261121-6e83a4` 15.73%（17.51%） |
| Q-002/Q-003 の P_gate | `4e5813` 30.85%/29.90%、`6e83a4` 12.94%/12.54%、`351582` 7.65%/7.41% |

`4e5813` の除外条件 (d) は「索引・起動パケットに一度も現れない過去の行が、手がかりなしで索引経由の行と同じ率で後続セッションに引用・活用されることが実測された場合」に相3（台帳AI側）を棄却する。前回の `EVL-20261127-ff16af` は CAP=20261127 のデータで (d) 非発火を記録したが、その後 7 セッション分のパケットと読みが加わっている。再測は (d) の維持判定と、(a)・(c) の判定を一度に行える。

## §2 書庫側の実測——CAP=20261128 再測定

再現スクリプト全体を付録Aに置く。`SELF`（本セッション）の行は全ループで除外し、台帳追記・マップ再生成後の再実行でも出力が変わらないようにした。測定の定義は `351582` の適用条件に従う：到達は機械的バックフィルを除く手書きの読み行のうち、読みの日付が素材の日付より後のもの。deep は `quoted`・`interpreted`・`reinterpreted`・`contested`。

### M1 除外(a) の判定——era × claims 配線の各層で在場効果は消えたか

| 層 | 在場群の到達 | 不在群の到達 | z | p |
|---|---|---|---|---|
| pre × claims有 | 282/698 = 40.40% | 23/157 = 14.65% | **6.086** | <10⁻⁸ |
| pre × claims無 | 666/2153 = 30.93% | 34/144 = 23.61% | 1.848 | 0.065 |
| reg × claims有 | 74/1062 = 6.97% | 1/6 = 16.67% | -0.927 | 0.354 |
| reg × claims無 | 13/641 = 2.03% | 0/21 = 0.00% | 0.659 | 0.510 |
| act × claims有 | 27/559 = 4.83% | 1/44 = 2.27% | 0.776 | 0.438 |
| act × claims無 | 4/271 = 1.48% | 0/10 = 0.00% | 0.387 | 0.699 |

- 主判定層（pre-reg の主たる部分である pre）では在場効果が **z=6.086 で再現**し、前回（era 統制下で pre-reg z=5.04、claims-covered 層 z=6.05）より強い。**除外(a) は発火しない。**
- ただし前回の範囲に無かった構造が見えた：pre 層内で在場効果は **claims 配線済み層（z=6.086）に集中**し、非配線層では z=1.85（p=0.065、基準未達）まで落ちる。パケット在場の効果は、claims 配線という第二の手がかりとの**積**として現れている。
- reg・act の不在層は n=6/21/44/10 で、適用条件第4項が予告した通り依然として検定不能。この不備は今回の CAP 更新でも解消されなかった。不在集合 382 件は本日の追記で一件も増えていない（当日刻印 41 件は全件が自己列挙により在場になるため）。**パケット不在の母集団は、今後の追記では減る一方で、到達が起きない限り再生されない閉じた集合になりつつある。**

### M2 除外(c) の判定——初回読は初回パケット出現に先行するか

在場かつ到達した 790 素材のうち、初回パケット出現が初回読に**先行**したのは 33 件（4.2%）、**同日**が 710 件（89.9%）、**読が先行**したのは 47 件（5.95%）で、除外(c) の閾値（読先行が過半）に遠く及ばない。**除外(c) は発火しない。** ただし同日の同時性が約九割を占めるということは、パケット在場の効果の主要部分が「列挙した同じ日に読む」という作法上の結合であることを意味する。在場が効くのは同日の結合を離れた後（M1 の pre 層の後続到達）であり、ゲートの実体は「その後も開き続ける窓」にある。

### M3 パケット不在の行は、どの入口で開かれたか（探索的）

パケット不在かつ到達した 59 素材について、claims 配線（ノート主張の `material_ids`）の有無を不在・未到達群（323）と比べた。

| 群 | 配線率 | z | p |
|---|---|---|---|
| 不在×到達 | 25/59 = 42.37% | **-1.981** | 0.048 |
| 不在×未到達 | 182/323 = 56.35% | | |

era を pre に限定しても同じ向きである（23/57 = 40.35% 対 134/244 = 54.92%、z=-1.982）。**claims 配線はパケット不在行の行レベル再読を増やさず、むしろ減らす方向に揺れた。** これは事前登録のない探索的比較で、p が 0.05 直下の揺らぎである。複数比較の範囲を出ないと明示した上で、二つの読みを残す。

1. **代替の読み**：配線済み行の内容は claims と精読報告の本文が運ぶため、行自体を開く必要が下がる。入口が競合し、stronger な入口（要旨層）が弱い入口（行の再読）を**吸収**する。
2. **交絡の読み**：配線済み行は収蔵当日に集中して読まれた行であり（その読みは到達定義の `>` に入らない）、後続の再読が構造的に少ない母集団である。

どちらの読みでも、「入口は積み上がる（足し算になる）」とは言えないという点では一致する。L1 の要旨層の存在が L0 行の到達を肩代わりしている可能性は、`4e5813` 相1の「どの入口で引き出せるかの分化」を、分化の**非対称な強度**（入口間で独立に効かない）まで絞り込む。

### M3b ダイジェスト（L1）経由の在否

パケット不在かつ非配線の層（pre で到達 34・未到達 110）に、`state/digests.json` に ID が現れる素材は **0件**（両群とも0）。L1 ダイジェストはこの層の入口として不在であり、不在行の 34 件（23.6%）の到達は、検索・索引・本文リンクなど、測っていない第四の入口による。

### M4 除外(d) の判定——不在行は在場行と同じ率で引用・活用されるか

| 指標 | 在場群 | 不在群 | z | p |
|---|---|---|---|---|
| 到達（行レベル） | 1066/5384 = 19.80% | 59/382 = 15.45% | 2.075 | 0.038 |
| deep 到達 | 740/5384 = 13.74% | 33/382 = 8.64% | **2.830** | 0.0047 |

パケット不在行の到達率は在場行より低く、引用・変奏・異議を伴う deep 到達では差がさらに広がる。**不在行が在場行と同じ率で使われるという除外(d) の条件は成立せず、`4e5813` 相3（台帳AI側）は非発火のまま維持される。** 「保存だけを肩代わりする」という仮説の AI 側の記述は、CAP を一日進めた状態でも反証されなかった。

### §2 の判定の要約

| ID | 対象 | 判定 | 根拠 |
|---|---|---|---|
| `EVL-20261128-696248` | `HYP-20261127-351582` | narrows_scope | (a) 非発火（pre 層 z=6.086 で再現）だが、効果が claims 配線済み層に集中（非配線層 z=1.85）で在場ゲートの作用範囲を配線済み行へ限定。(c) 非発火（読先行 5.95%） |
| `EVL-20261128-edb897` | `HYP-20261126-4e5813` | supports | (d) 非発火（不在 15.45% 対 在場 19.80%、deep で差拡大）。M3 の入口吸収シグナルは相1の分化を強度の非対称まで絞るが、事前登録のない探索値 |

二行とも `evidence_type: reproducible_script` で、`script_command` は付録Aと同一の中身である。評価行の重みは `P_gate`・`P_amort` を次の通り動かした（前値 → 後値）。

| 仮説（問い） | P_gate | P_amort |
|---|---|---|
| `4e5813`（Q-001） | 37.51% → **69.84%** | 37.71% → 69.96% |
| `4e5813`（Q-002） | 30.85% → **65.47%** | 30.88% → 65.50% |
| `4e5813`（Q-003） | 29.90% → **64.36%** | 29.93% → 64.40% |
| `351582`（Q-002） | 7.65% → **0.68%** | 7.66% → 0.68% |
| `351582`（Q-003） | 7.41% → **0.67%** | 7.42% → 0.67% |
| `6e83a4`（Q-001） | 15.73% → 7.59% | 17.51% → 8.37% |

質量は子仮説 `351582` の射程限定を親 `4e5813` が引き受けた形で移動し、三問とも `4e5813` が P_gate・P_amort の首位になった。予測感度（`SELF_MODEL.md` §6：この対の予測 D_KL=0.21373 bits）はここより小さく見積もられていた。首位の独走が起きたことは、**反証候補の減少**でもある。次の検証対象の選択は、この新しい分布の下での最優先対（`EIG` 上位）を改めて読むことから始めるべきである。

## §3 人間側の精読——『道草』第1〜16章の手がかり目録

固定版テキストから、記憶の再開と到達失敗を句アンカー付きで数えた（付録B。24 句とも全件ピン留め版に1回だけ現れることを確認済み）。

| 型 | 件数 | 場面（章） | アンカー句 |
|---|---|---|---|
| 手がかり付き再開——人・出会い | 3 | 雨の朝の行き会い（一）、吉田との会見の後（十五）、監督する姿→本屋（十六） | 「思い懸けない人にはたりと出会った」「吉田と会見した後の健三の胸には」「池の端の本屋で法帖を買ってもらった事をわれ知らず」 |
| 手がかり付き再開——物 | 1 | 欄間の古い額（四） | 「古い額を眺めた健三は」「記憶の探照燈を向けた」 |
| 手がかり付き再開——語・名 | 2 | 「島田」の二字（十一）、「柴野」という名（十二） | 「とくに島田という二字に力を入れて」「柴野という名を聞いて急に思い出した」 |
| 無手がかりの想起と同日の消去 | 1 | 島田の家の想像（八→八末） | 「彼はただ想像の眼で」「島田の事はまるで忘れてしまった」 |
| 到達失敗 | 5 | 妻への説明の程度（二）、自分の星の繰り方（五）、七年昔の説明の詳細（十一）、父の絶交の言渡し（十四）、幼時の心持（十五） | 「どの位綿密な程度で」「どうして自分の星を繰るのか」「どれほど詳しく彼女に話したか」「そう厳重にいい渡された覚はなかった」「何故自分の有っていたその頃の心が思い出せない」 |
| 他人の記憶経路 | 3 | 姉の釜の話（七）、妻の千本通りと兄経由（十一）、兄経由の絶交（十四） | 「引絡まっている古い自分の影法師」「私たちがまだ千本通りにいた時分」「御兄さんからも聞いて知ってますわ」 |
| 到達失敗の遡及再解釈 | 1 | 「始めから情合が欠けていた」仮説の採用（十五） | 「多分この方だろうと自分を解釈した」 |

### §3.1 相1：到達可能性は手がかりの型に従って分化する

再開した記憶は七件のうち六件までが、人・物・語という三つの型の入口を通る。対象の不変点（黒髪・帽子なしの癖・毛繻子の洋傘）が第一章の再認を支え、欄間の額が「記憶の探照燈」を点す。対照的に、手がかりなしに構成した家の像（八章）は、反復して「二十年前の光景を今日の事のように考えた」直後に「まるで忘れてしまった」。**利用可能にしたことと、開けるようにしておくことは、同じ結果にならない。** また病気は「思い出す機会がまるでなかった」状態を作り、妻の語った「島田」の二字だけが再開する。入口の喪失（病気）と入口の供給（語）が同じ章で対になっている。

### §3.2 相2：問いの型と、話し手の位置が要旨を決める

妻と姉は同じ過去について異なる要旨を渡す。姉の島田像（釜を持って行く）は、聞き手の都合を迎える語調で選ばれた記憶であり、健三には「空御世辞のごとく」響く。妻は七年昔の説明を「もう七年位になるでしょう。私たちがまだ千本通りにいた時分ですから」と編年の錨つきで保持しており、健三本人は「どれほど詳しく彼女に話したか」を届かない。絶交の言渡しは兄経由でしか届かず、健三は「御前誰からそんな事を聞いたのかい」と出所を問うてから、「おやじは阿爺、兄は兄、己は己」と、**届いた記憶を自分への規範として受取らない**選択をする。同じ内容でも、どの入口・どの問いの型で届いたかによって、その扱い（受容・保留・拒絶）が変わる。

### §3.3 相3：帰らない心持は、新しい自己標識で埋められる

十五章の核心は、光景が鮮明に帰るのに、その頃の心だけが帰らないことである。健三は「こんな光景をよく覚えているくせに、何故自分の有っていたその頃の心が思い出せないのだろう」と問い、**「始めからその人に対してだけは、恩義相応の情合が欠けていたのかも知れない」という代替仮説を、「多分この方だろうと自分を解釈した」**と採用する。到達不能な状態の不在を、状態の不在（当時から無かった）と読み替える遡及的再解釈である。十六〜二十章以降の島田との再交際が、この自己読み替えをどう更新するかは本次数の射程外に置いた。

### §3.4 書庫側との照応と、通じない箇所

- **通じる**：行が手がかり（パケット・配線・索引）を通ってのみ後続に開かれる構造は、健三の記憶が人・物・語を通ってのみ再開する構造と同型である。無手がかりの構成物が同日に消えるのは、到達定義上「列挙と同日の読み」に圧縮される M2 の同日九割と重なる。また帰らない心持が新しい自己解釈で埋められるのは、前回までの報告が見つけた「後続セッションが先行の読みを読み替える」現象（`READ-20261128-2f33d4` の書付の訂正）の文学側の照応である。
- **通じない**：健三には訂正録が書けない。読み替えは過去の本文を黙って置き換える。書庫では置換は物理的に不可能で、訂正録が隣に置かれる。この違いは「保存」の問題でなく「**訂正の行き先が在るか**」の問題であり、追記専用の差分はここで初めて意味を持つ。ただし要約が限定句を落とす既知の現象（`EVL-20261123-43f91e` とその訂正録）は、隣に置いた訂正録が開かれなければ健三と同じであることを示している——**隣に在ることと、開かれることは別である**。今回の M3 は、この「隣」の入口配線の実測である。
- **数えないもの**：文学側の件数（7件・5件・1件）は仮説の反証条件の判定には使わない。`4e5813` の (a)〜(c) は幼児・追試・出典混同の一次研究を要求し、今回の実行環境からはその経路に到達できない（§4）。

## §4 横断する問いと限界

- **本報告の置き場所（編集判断）**：readings/ のファイル数は本報告執筆時点でソフト上限 1250 に正確に一致しており（`size_budget.py --strict`、2026-11-25 の三階層移行で再スケールされた値）、新規の精読報告を readings/ に置くと strict 検査と回帰テスト3件が失敗する。L0 の既存報告は追記専用で削除できず、上限の引き上げは予算規則の変更になる。よって本報告は `docs/` 配下に置き（`NOTE-20261126-0a4802` が `docs/` 報告を配線した前例に従う）、ノート行は通常どおり `NOTE-*` で配線した。上限は変更していない。これは本回が精読と実測の回であり、報告本体の置き場所は探究内容を変えないという判断である。readings/ の余白が埋まった状態が続くなら、統合先の L1（ダイジェスト）の増強を次回以降の consolidator 議題にすべきである（本回は実施しない）。

- **達成**：`351582` が自ら要請した CAP 更新後の再測定を実施し、(a)(c) の非発火と作用範囲の限定を記録した。`4e5813` (d) の非発火を新しいデータで確認した。文学側の第1〜16章を句アンカー付きで通読し、前回の未達（全102章通読）のうち前半を埋めた。
- **未達**：①Tulving & Thomson (1973)（`MAT-20261122-422bfb`、`partially_verified`）の全文再照合は、DOI・PsycNet 等の外部経路が本実行環境から到達できないため未実施。素材行の `verification` を動かす編集判断は作らなかった。②reg・act の不在層の検定不能は解消されず、(a) の判定は pre 層に偏る。③M3 の入口吸収シグナルは p=0.048 の探索値であり、独立の再測（claims 配線の「収蔵当日集中」を統制した比較）を要する。④『道草』十七〜九十五章は未読。⑤文学側の件数は読み手（私）の一つの読みであり、他の読みと衝突した場合の仲裁装置はない。
- **次に読み返したい記録**：`EVL-20261127-ff16af`（(d) の初回判定と今回の値の直接比較用）、`NOTE-20261127-06a667` の claims（M3 の再測の統制変数としての配線時点）、『道草』十七〜二十五章（遡及再解釈の後続更新）。

## 付録A 再現スクリプト（CAP=20261128 再測定）

標準ライブラリのみ。`SELF` は本セッション ID で、全ループから除外される。台帳追記・マップ再生成の前後で出力は変わらない（本報告の数値は全てこの出力から写した）。

```python
import json, glob, re, math

SELF = "SESSION-20261128-55548f"
CAP = "20261128"
ACTIVE = "20261121"

def d8(i):
    m = re.search(r"-(\d{8})-", i or "")
    return m.group(1) if m else "00000000"

def load(pat, base=None):
    rows = []
    for f in sorted(glob.glob(pat)):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    if base:
        for line in open(base, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows

mats = load("state/materials.d/*.jsonl", "state/materials.jsonl")
notes = load("state/notes.d/*.jsonl", "state/notes.jsonl")
reads = load("state/read_log.d/*.jsonl", "state/read_log.jsonl")
sessions = load("state/sessions.d/*.jsonl", "state/sessions.jsonl")

# claims wiring: material ids wired into any note claim (all sessions except SELF)
claims_wired = set()
for n in notes:
    if n.get("session_id") == SELF:
        continue
    for c in (n.get("claims") or []):
        for mid in (c.get("material_ids") or []):
            claims_wired.add(mid)

# manual read rows (exclude mechanical backfill), grouped by material
by_mat = {}
for r in reads:
    if r.get("session_id") == SELF:
        continue
    t = r.get("target") or {}
    if t.get("type") != "material":
        continue
    note = (r.get("note") or "")
    if "機械的バックフィル" in note or "backfill" in note.lower():
        continue
    by_mat.setdefault(t.get("id"), []).append((d8(r.get("read_id") or ""), r.get("reading"), r.get("created_at") or ""))

def reached(mid):
    md = d8(mid)
    return any(rd > md for rd, _, _ in by_mat.get(mid, ()))

def deep(mid):
    md = d8(mid)
    return any(rd > md and rg in ("quoted", "interpreted", "reinterpreted", "contested") for rd, rg, _ in by_mat.get(mid, ()))

# packet union over sessions started <= CAP (exclude SELF)
pkt = set()
for s in sessions:
    if s.get("session_id") == SELF:
        continue
    sd = (s.get("started_at") or "")[:10].replace("-", "")
    if sd and sd <= CAP:
        pkt.update(s.get("context_material_ids") or [])

stamp = [m for m in mats if "00000000" < d8(m["material_id"]) <= CAP]

def era(m):
    d = d8(m["material_id"])
    if d <= "20261112":
        return "pre"
    if d <= "20261120":
        return "reg"
    return "act"

def zt(t1, n1, t2, n2):
    p = (t1 + t2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return (float("nan"), float("nan"))
    z = (t1 / n1 - t2 / n2) / se
    return round(z, 4), round(2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2)))), 6)

def strat(group, name):
    gp = [m for m in group if m["material_id"] in pkt]
    ga = [m for m in group if m["material_id"] not in pkt]
    r1 = sum(1 for m in gp if reached(m["material_id"]))
    r2 = sum(1 for m in ga if reached(m["material_id"]))
    if len(gp) and len(ga):
        z, p = zt(r1, len(gp), r2, len(ga))
        print(name, "present %d/%d=%.4f absent %d/%d=%.4f z=%s p=%s" % (
            r1, len(gp), r1 / len(gp), r2, len(ga), r2 / len(ga), z, p))
    else:
        print(name, "present %d/%d absent %d/%d (degenerate)" % (r1, len(gp), r2, len(ga)))

print("stamp=%d packet=%d wired=%d" % (len(stamp), len(pkt), len(claims_wired)))

# M1: era x claims-wiring layers, presence effect (exclusion (a) of 351582)
for e in ("pre", "reg", "act"):
    for w in (True, False):
        g = [m for m in stamp if era(m) == e and ((m["material_id"] in claims_wired) == w)]
        strat(g, "M1 era=%s claims=%s" % (e, w))

# M4: overall + deep
strat(stamp, "M4 overall")
gp = [m for m in stamp if m["material_id"] in pkt]
ga = [m for m in stamp if m["material_id"] not in pkt]
d1 = sum(1 for m in gp if deep(m["material_id"]))
d2 = sum(1 for m in ga if deep(m["material_id"]))
zt(d1, len(gp), d2, len(ga))
print("M4 deep present %d/%d=%.4f absent %d/%d=%.4f z=%s p=%s" % (
    d1, len(gp), d1 / len(gp), d2, len(ga), d2 / len(ga), *zt(d1, len(gp), d2, len(ga))))

# M2: direction (packet-first vs read-first) among present & reached
first_pkt = {}
for s in sessions:
    if s.get("session_id") == SELF:
        continue
    sd = (s.get("started_at") or "")[:10].replace("-", "")
    if sd and sd <= CAP:
        for mid in (s.get("context_material_ids") or []):
            if sd > d8(mid):
                cur = first_pkt.get(mid)
                if cur is None or sd < cur:
                    first_pkt[mid] = sd
pf = sd_cnt = rf = 0
for mid, rds in by_mat.items():
    if mid not in first_pkt or mid not in {m["material_id"] for m in stamp}:
        continue
    md = d8(mid)
    later = [rd for rd, _, _ in rds if rd > md]
    if not later:
        continue
    first_read = min(later)
    fp = first_pkt[mid]
    if fp < first_read:
        pf += 1
    elif fp == first_read:
        sd_cnt += 1
    else:
        rf += 1
tot = pf + sd_cnt + rf
print("M2 packet-first=%d same-day=%d read-first=%d total=%d read-first-share=%.4f" % (
    pf, sd_cnt, rf, tot, (rf / tot if tot else float("nan"))))

# M3: among packet-absent reached vs unreached, claims-wiring rate (second entry)
abs_reached = [m for m in ga if reached(m["material_id"])]
abs_unreached = [m for m in ga if not reached(m["material_id"])]
w1 = sum(1 for m in abs_reached if m["material_id"] in claims_wired)
w2 = sum(1 for m in abs_unreached if m["material_id"] in claims_wired)
z, p = zt(w1, len(abs_reached), w2, len(abs_unreached))
print("M3 absent&reached wired %d/%d=%.4f absent&unreached wired %d/%d=%.4f z=%s p=%s" % (
    w1, len(abs_reached), w1 / len(abs_reached) if abs_reached else float("nan"),
    w2, len(abs_unreached), w2 / len(abs_unreached) if abs_unreached else float("nan"), z, p))
for e in ("pre", "reg", "act"):
    ar = [m for m in abs_reached if era(m) == e]
    au = [m for m in abs_unreached if era(m) == e]
    if ar and au:
        w1 = sum(1 for m in ar if m["material_id"] in claims_wired)
        w2 = sum(1 for m in au if m["material_id"] in claims_wired)
        z, p = zt(w1, len(ar), w2, len(au))
        print("M3 era=%s absent&reached wired %d/%d=%.4f unreached wired %d/%d=%.4f z=%s p=%s" % (
            e, w1, len(ar), w1 / len(ar), w2, len(au), w2 / len(au), z, p))
    else:
        print("M3 era=%s reached=%d unreached=%d (degenerate)" % (e, len(ar), len(au)))

# M3b: digest (L1) membership as a third entry among packet-absent & claims-unwired rows
digest_ids = set(re.findall(r"MAT-[A-Za-z0-9-]+", json.dumps(json.load(open("state/digests.json")), ensure_ascii=False)))
for e in ("pre", "reg", "act"):
    ar = [m for m in abs_reached if era(m) == e and m["material_id"] not in claims_wired]
    au = [m for m in abs_unreached if era(m) == e and m["material_id"] not in claims_wired]
    g1 = sum(1 for m in ar if m["material_id"] in digest_ids)
    g2 = sum(1 for m in au if m["material_id"] in digest_ids)
    if ar and au:
        z, p = zt(g1, len(ar), g2, len(au))
        print("M3b era=%s absent&unwired reached digest-in %d/%d=%.4f unreached digest-in %d/%d=%.4f z=%s p=%s" % (
            e, g1, len(ar), g1 / len(ar), g2, len(au), g2 / len(au), z, p))
    else:
        print("M3b era=%s reached=%d unreached=%d (degenerate)" % (e, len(ar), len(au)))
```

## 付録B 文学本文の取得と句照合

取得原文は `scratch/`（Git管理外）へ置く。SHA-256 は前報告の固定版と同一である。

```sh
mkdir -p scratch
gh api repos/aozorahack/aozorabunko_text/contents/cards/000148/files/783_ruby_1311/783_ruby_1311.txt?ref=0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65 --jq '.content' | base64 -d > scratch/michikusa-original.txt
```

```python
from pathlib import Path
import hashlib, json, re
b = Path('scratch/michikusa-original.txt').read_bytes()
assert hashlib.sha256(b).hexdigest() == '59a318ae48ad664a158d6197c2954f3e80fae1b2d3be229c2ae8b90966661d13'
s = b.decode('utf-8')
body = s[s.index('［＃５字下げ］一［＃'):s.index('底本：')]
body = re.sub(r'《[^》]*》', '', body).replace('｜', '')
anchors = [
 ('章1','出会い','思い懸けない人にはたりと出会った'),
 ('章1','不変手がかり（髪）','何故今でも元の通り黒い'),
 ('章2','到達失敗（説明量）','どの位綿密な程度で細君に説明してやったか'),
 ('章2','手紙＝媒介','遠くから呼び起す媒介'),
 ('章4','物手がかり（額）','古い額を眺めた健三は'),
 ('章4','探照燈','記憶の探照燈を向けた'),
 ('章5','到達失敗（星繰り）','どうして自分の星を繰るのか'),
 ('章7','他人の記憶経路（姉）','引絡まっている古い自分の影法師'),
 ('章8','無手がかり想起（想像の眼）','彼はただ想像の眼で'),
 ('章8','想起後の消去','島田の事はまるで忘れてしまった'),
 ('章11','語手がかり（島田）','とくに島田という二字に力を入れて'),
 ('章11','病気による到達低下','思い出す機会がまるでなかった'),
 ('章11','到達失敗（説明詳細）','どれほど詳しく彼女に話したか'),
 ('章11','他人の記憶経路（妻・千本通り）','私たちがまだ千本通りにいた時分'),
 ('章11','他人の記憶経路（兄）','御兄さんからも聞いて知ってますわ'),
 ('章12','語手がかり（柴野）','柴野という名を聞いて急に思い出した'),
 ('章14','到達失敗（絶交の言渡し）','そう厳重にいい渡された覚はなかった'),
 ('章14','来歴の分離','おやじは阿爺、兄は兄、己は己'),
 ('章15','会見後の連続想起','吉田と会見した後の健三の胸には'),
 ('章15','手がかり不可分','その人と引き離す事は出来なかった'),
 ('章15','標識の飽和','帽子を披らない男の姿が織り込まれている'),
 ('章15','到達失敗（心持）','何故自分の有っていたその頃の心が思い出せない'),
 ('章15','遡及再解釈','多分この方だろうと自分を解釈した'),
 ('章16','不随意想起（本屋）','池の端の本屋で法帖を買ってもらった事をわれ知らず'),
]
counts = [(ch, kind, ph, body.count(ph)) for ch, kind, ph in anchors]
assert all(n == 1 for _, _, _, n in counts), counts
print('anchors verified:', len(counts), 'all unique-present')
```

出力：`anchors verified: 24 all unique-present`。章の番号は本報告の表記（一〜十六）であり、固定版の章題と一致する。ルビを除去した照合であるため、底本のルビ表記の違いによる数値の変動は生じない。
