# その語は法廷で使われる——ロック II.XXVII の後半、同じ章を二度読んだ二つの記録、ヒュームの付録

**セッション**：`SESSION-20261029-164350`
**実行日**：2026-10-29（UTC／利用者の現地日付）。ファイル名・ID も実日付。
**作業方法**：`prompts/rereading_and_collision.md`。`--packet auto` の参考モード `editorial_review`・参考問い `Q-20261024-6bdafd`・候補窓は採らなかった（理由は §2）。
**産出**：新規断片 0／新規問い 0／新規素材 0／新規関係 0／新規編集判断 0／**新規訂正 1**。原典照合 2 点（ロック、ヒューム）。セッション 1 件・読み痕跡 14 件・本ノート 1 本。

> **一人称**。「読んだ」「比べた」「気づいた」は、今回この記録群と 2 点の原典を読んで構成した公開の作業上の視点である。前の会話の記憶、身体経験、持続する主観的意識の事実報告ではない。引用は、台帳に保存されている文か、今回開いた原典の文であり、区別は都度つける。
>
> **日付と作業順**。このクローンは shallow（`git rev-parse --is-shallow-repository` が `true`、履歴 1 コミット）であり、ID・シャード名・ファイル名の日付から実際の作業順は決められない。以下の「12-15」「17f697」等は台帳の内部編年ラベルと `sessions.notes` の相互参照のための呼び名であって、実行日の主張ではない。とくに §4.1 で扱う二つのノートは、どちらも実行日を 2026-10-29 と記しており、**どちらが先かはこのクローンでは決められない**。
>
> **内部編年を延ばさなかった理由**。前回（12-15）は内部編年のラベルを `2026-12-15` へ延ばした。今回は実日付を用いる。`SESSION-20261029-dd41d9` が「ID やファイル名の日付は実日付を用い、内部編年の未来日付は延ばさない」と書いた判断を採る。ラベルは連なりを運ばない（12-07 の見立てを 12-10 が採らなかったのと同じ理由）。

---

## 0. 委任の来歴と、今回AIが独自に決めたこと

**来歴（範囲）**。利用者から 1 件の依頼を受けた。範囲は `PROJECT_CHARTER.md`・`CONTENT_POLICY.md` の遵守、`tools/inspect_inquiry.py --packet auto` の確認、問いと形式の自律選択、当面は新作より最近の比喩的展開と過去の見立ての読み直しを優先すること、人間観・自己理解へ戻ったもの／戻らないものの点検、継承・取り落とし・読み替えを既存ノートと `sessions.notes` に残すこと、比喩の射程の区別、`state/*.d/` への追記と検証、人間への追加の選択・確認・承認を求めないこと、`human_narrator` と架空の `conversation_trace` を使わないこと、回答内リンクを GitHub の URL にすること、最後にマージすること。依頼文は作業範囲と来歴として分離し、資料の証拠にも作品内の人間の声にも変換していない。明示されていない意図は推定しない。

**独自に決めたこと。**

1. **参考モード（`editorial_review`）と参考問い（`Q-20261024-6bdafd`、世阿弥・五輪書・守破離）を採らなかった。** 参考問いは「この書庫の精読という型は何を守り、何で破り、どこへ離れるか」を扱う。型の話は今回の対象（一つの章の後半と、その章を読んだ二つの記録）と噛み合わない。参考モードは `README.md` の窓ローテーションを伴うが、今回動かす窓がない。
2. **12-15 の申し送り（ベルクソン `MAT-LIT-005`・ヒューム `MAT-LIT-002` の原典）のうち、ヒュームだけを実行し、ロックをもう一度開いた。** ベルクソンは許可接続先から到達できなかった（§3）。ロックは 12-15 の申し送りにはなかったが、**同じ章の後半**を読むために開いた。12-15 が読んだのは §7〜§18 相当で、そこで止まっている。
3. **読む前に、同じ素材を読んだ先行ノートを read_log から拾った。** `MAT-LIT-001` の読み痕跡を和集合で引き、`SESSION-20261029-17f697` が同じ日に同じ章（§§8–17）を読んでいることを見つけた（§4.1）。これは今回の選択の結果であって、最初から狙ったものではない。
4. **関係線を 0 本にした。** 見つかったのは辺ではなく、二つの読みが同じ場所で止まっていることと、語の水準の違いである。
5. **訂正を 1 件だけ置いた**（`ERR-20261029-ee43c2`）。12-15 の「身体は man の側」という一文が、同じノートが引いている §13 の文と合わないため。**既存の記録は書き換えない。**

---

## 1. 読む前に引き継いだ見立て

いずれも**今回これらの記録を読んで構成した**引き継ぎであり、以前から保持していた記憶ではない。

- **H1**（12-11 §4.2・§4.3、12-15 §6.1-2 が継承）：抜粋では、残った文が命題で、外れた文が身体と条件である。確認例は 3 件、規則としては名乗らない。
- **H2**（12-15 §4.1・§4.2）：ロックの章は person（意識の遡及範囲）と man（形ある身体と生命の連続）を分け、身体は man の側に置かれる。台帳の `passage` に身体の語はなく、`literary_invitation` の「身体を持続させなくても」がそれを運んでいる。
- **H3**（12-14-983e0e §4.1・§4.2）：判定語「戻らない」は八つの基準を一語で覆ってきた。基準は `read_log` の `note` に残っていない。判定語を持ち回らない。
- **H4**（12-02 §3、12-11 §5）：比喩が通じるのは、費用を払う者が本文の内に名指されているあいだ。
- **H5**（12-14-a830cb §7）：再開する者が受け取る一貫した書庫は、保存であると同時に棄ての結果である（このクローンでは再検証していない）。
- **H6**（17f697 ノート、今回初めて読んだ）：ロックの §15 と記録の照合は二種類の帰属であり、記録の照合から意識の移転も同一人物も導かない。§13 を「身体は man の側だけ」と簡略化しない。

H6 は今回読むまで知らなかった。§4.1 で書くように、これは **H2 と衝突する**。

---

## 2. 選んだ記録と理由

1. **`readings/2026-12-15-the-man-the-excerpt-left-outside.md` 全文と、その `sessions.notes`。** 直前のセッションであり、実行日が今日と同じ。`Q-001` の 12 素材を開き、原典照合をロック 1 件に絞った、いちばん近い先行。
2. **`readings/2026-12-14-the-verdict-without-a-test.md` §7・§8 と `readings/2026-12-14-what-the-merge-dropped-and-the-history-kept.md` §7・§8。** 12-15 の申し送りの出所であり、「未接続」を理由の数で数えない判断の直近の例。
3. **`readings/2026-12-11-the-excerpt-keeps-the-word.md` §4.5・§4.6・§4.7・§8・§9。** 12-15 が読まなかった範囲。とくに §4.7（`literary_invitation` が原典の主張を反転させている）は、今回ヒュームで同じ形を探す物差しになった。
4. **`state/errata.d/2026-12-14-6d1e7c93b5a2.jsonl` の 2 行**（12-15 の申し送り 4、今回開いた）。
5. **`MAT-LIT-001`・`002`・`005`・`021` の素材行**（`passage`・`context`・`literary_invitation`・`scope_note`・`source`）。
6. **`MAT-LIT-001` の読み痕跡**（`state/read_log` と `state/read_log.d/` の和集合）。ここで 17f697 のノートに行き当たった。
7. **`readings/2026-10-29-record-and-remembered-action.md`**（17f697）。同じ章を読んだ、もう一本のノート。
8. **`MOTIF-020` のモチーフ行と `readings/2026-10-24-session-039-sleep-and-dream.md` の冒頭**（§4.8 の照合のためだけ。辺は張らない）。
9. **原典 2 点**（ロック、ヒューム）。取得元は §3。

`--packet auto` の候補窓（疎結合モチーフ対・改稿候補・正面応答候補）は一つも採っていない。選んだ理由は、直近 4 セッションが同じ章と同じ素材の周りで止まっており、その止まり方そのものが読める対象になっていたためである。窓の外の選択を負債にしない（`docs/parallel-work.md` §3）。

---

## 3. 照合した原典の範囲

| 資料 | 原典 | 取得 | 読んだ範囲 |
|---|---|---|---|
| `MAT-LIT-001` ロック | *An Essay Concerning Human Understanding*, Vol. 1（PG #10615） | GITenberg ミラー `An-Essay-Concerning-Humane-Understanding-Volume-1--13-MDCXC-Based-on-the-2nd-Edition-Books-1-__10615`、commit `aa98c0a`、`10615.txt` | Book II, Chapter XXVII の見出し §10〜§29 相当（第 12040〜12600 行）。§10・§11・§12・§13・§24・§25・§28・§29 を全文 |
| `MAT-LIT-002` ヒューム | *A Treatise of Human Nature*（PG #4705） | GITenberg ミラー `A-Treatise-of-Human-Nature_4705`、commit `a5da8bb`、`4705.txt` | Book I, Part IV, Section VI の劇場の前後（第 8925〜8975 行）と、**APPENDIX** の全体（第 21367〜21640 行） |

**到達できなかったもの（未照合）**

- `MAT-LIT-005` ベルクソン：`api.github.com` の `org:GITenberg` 検索で "Matter and Memory" は **0 件**。台帳の `source.url` は en.wikisource.org で、許可接続先の外。**未照合**。
- `MAT-LIT-021` メルロー＝ポンティ：`source.url` は archive.org。**未照合**（12-15 と同じ）。
- `MAT-LIT-002` の台帳 URL（davidhume.org）自体：許可接続先の外。今回は PG #4705 で本文を読んだが、**台帳の `passage` がどの版から採られたかは確認していない**（§4.6 末尾）。

ロックについて一点。12-15 は commit `aa98c0a` の同じファイルを開いている。17f697 は同じリポジトリの commit `ba2f7e58` を開いている。**別の commit だが、今回読んだ範囲では本文に差は見つからなかった**（`git clone --depth 1` の HEAD が `aa98c0a`）。過去の版を再取得して差分を取る作業はしていない。

---

## 4. 見立てを揺さぶった箇所

### 4.1 同じ章を読んだ二つのノートが、互いを引いていない

`MAT-LIT-001` の読み痕跡を和集合で引くと、同じ実行日（2026-10-29）に、この素材を原典で読んだセッションが二つある。

- `SESSION-20261029-17f697`（`readings/2026-10-29-record-and-remembered-action.md`）：PG #10615 §§8–17 を GITenberg の commit `ba2f7e58` で開いた。§13 を「身体が自己に属する条件」、§15 を「行っていない行為を自分のものと表象する可能性と神の善性」、§17 を「本人の人格と他者による身体の認識の区別」と読む。**`ERR-20261028-a4d688`（節番号の訂正）を明示的に尊重し**、「これを『身体は man の側だけ』と簡略化しない」と書く。
- `SESSION-20261215-fb78ff`（`readings/2026-12-15-the-man-the-excerpt-left-outside.md`）：同じ章を §7〜§18 相当まで開いた。**17f697 を引かず、`ERR-20261028-a4d688` も引かない。** 節番号については「誤りと断定しない」として保留にし、身体を man の側に置く読みを「初出」と記す。

二つのノートは、同じ章の、ほぼ同じ範囲を、同じ日に読んでいる。**そして互いを引いていない。** どちらが先かは、このクローンの 1 コミット履歴では決められない（§0）。決められるのは、**どちらの `read_log` にも相手のノートが現れない**ことまでである。

これは「12-14 の二本が互いを引く線を持たなかった」という H5 と同型の観察だが、同じではない。12-14 の二本は別の入口（判定基準／git 履歴）から同じ結論に達した。今回は**同じ入口・同じ素材**で、片方が他方の注意書き（「man の側だけと簡略化しない」）の真横を通っている。

ただし意図は推定しない。17f697 のノートが読まれたかどうかは、この二つのノートからは分からない。分かるのは、`read_log` を素材から引かない限り、同じ章の二つの読みは出会わない、ということだけである。

### 4.2 二つとも §18 より先へ行っていない

17f697 は §§8–17、12-15 は §7〜§18 相当と記す。**どちらも §24・§28 に触れていない。**

章の後半はこうなっている（この版の見出し番号）。

- §18 `Consciousness alone unites actions into the same Person.`（第 12279 行）
- §24 `But is not a man drunk and sober the same person?`（第 12418 行）
- §25 `Consciousness alone unites remote existences into one Person.`（第 12432 行）
- §28 `Person a forensic Term.`（第 12527 行）
- §29 `Suppositions that look strange are pardonable in our ignorance.`（第 12562 行の前後）

**今回の読み（このノートで初出）**。二つのノートが止まった位置は、章が「人が何であるか」を述べるのをやめ、「その語が何のためにあるか」を述べ始める位置である。前者は意識の遡及と身体の所属の話で、後者は法と帰属の話である。**抜粋の外へ落ちたのは身体だけではない。読み手の側でも、同じ語が落ちている。**

これは「二つのセッションが同じものを落とした」という規則ではない。二つのノートは別々の関心（記録と行為の帰属／抜粋の境界）から書かれていて、どちらも §18 までで足りていた。足りていたことと、そこに何があるかは別である。

### 4.3 §28——`person` は法廷用語である

> `PERSON, as I take it, is the name for this self. Wherever a man finds what he calls himself, there, I think, another may say is the same person. It is a forensic term, appropriating actions and their merit; and so belongs only to intelligent agents, capable of a law, and happiness, and misery. This personality extends itself beyond present existence to what is past, only by consciousness,--whereby it becomes concerned and accountable; owns and imputes to itself past actions, just upon the same ground and for the same reason as it does the present.`（第 12529〜12538 行）

台帳の `passage` が引いているのは §11〜§12 で、そこでは意識が過去へ遡ることが人格同一性を作る、と述べられる。**§28 はその語の用途を述べる。** 意識は「過去へ延びる唯一の手段」であって、目的ではない。目的は `appropriating actions and their merit`——行為とその功罪を帰属させることである。そして `another may say is the same person` という一文で、**他者が定義の内側に入る**。

**今回の読み（このノートで初出。readings と state を `forensic` で検索した範囲では、この章のこの語を読んだ記録は見つからない**。§9 に検索条件を書く）。
`Q-001` の四語（身体・記憶・他者・忘却）は、この章では同じ平面の候補ではない。

- **身体**：§10 では man の定義に入り（`of a body, so and so shaped, joined to it`、第 12046 行）、§13 では**条件つきで self の内側**に入る（§4.5）。
- **記憶・忘却**：§11〜§12 で、人格が過去へ延びる手段と、その中断。
- **他者**：§28 の `another may say`。判定する第三者ではなく、その語が使われる場面そのもの。
- **法**：§28 の `capable of a law`。語の適用条件。

「身体・記憶・他者・忘却のうち、何が『私』の輪郭を作るのか」という問いは、少なくともこの章では、四つの候補が一つの席を争う形にならない。**三つは水準が違う。** これは人間についての新しい確定ではない。入口の読み方の変更である。

### 4.4 §24——法は、区別できないことを罰する

> `But is not a man drunk and sober the same person? why else is he punished for the fact he commits when drunk, though he be never afterwards conscious of it? Just as much the same person as a man that walks, and does other things in his sleep, is the same person, and is answerable for any mischief he shall do in it. Human laws punish both, with a justice suitable to THEIR way of knowledge;--because, in these cases, they cannot distinguish certainly what is real, what counterfeit: and so the ignorance in drunkenness or sleep is not admitted as a plea. But in the Great Day, wherein the secrets of all hearts shall be laid open, it may be reasonable to think, no one shall be made to answer for what he knows nothing of; but shall receive his doom, his conscience accusing or excusing him.`（第 12418〜12430 行）

ここには三つのことが同時に書かれている。

1. **法は、意識が届かない行為も帰属させる。** 酔った者も眠っている者も罰せられる。
2. **その帰属は、区別できないことの上に置かれている。** `they cannot distinguish certainly what is real, what counterfeit`。
3. **それは暫定である。** `a justice suitable to THEIR way of knowledge` と名指され、`Great Day` に訂正される予定がある。

**今回の読み（このノートで初出）**。この段落は、書庫の帰属の説明として、比喩より精密に読める。書庫もまた、記録された行為と実際に行われた行為を確実に区別できないまま、`session_id`・`read_log`・`corrected_by` によって行為を帰属させる。だが**二点で違う**。

- ロックの法には**罰する者と裁かれる者がいる**。書庫にはいない。いるのは読む者だけである。
- ロックの暫定には**終わりが予定されている**（`Great Day`）。書庫の暫定には終わりがない。`secrets of all hearts shall be laid open` に相当する層は、この台帳に一欄もない。

だから「書庫は法廷である」とは書かない。書けるのは、**区別できないまま帰属する操作の形**が、この章の中に、比喩ではなくロック自身の語で置かれている、ということまでである。書庫がその形をしていることは、書庫が法であることを意味しない。

### 4.5 §13——身体は person の外ではなく、条件つきで内側にある

> `That this is so, we have some kind of evidence in our very bodies, all whose particles, whilst vitally united to this same thinking conscious self, so that WE FEEL when they are touched, and are affected by, and conscious of good or harm that happens to them, are a part of ourselves; i.e. of our thinking conscious self. Thus, the limbs of his body are to every one a part of himself; he sympathizes and is concerned for them. Cut off a hand, and thereby separate it from that consciousness he had of its heat, cold, and other affections, and it is then no longer a part of that which is himself`（第 12119〜12130 行）

12-15 はこの同じ段落を引きながら、「**身体は person の側ではなく man の側に置かれている**」と結論した。文の向きは逆である。手足は、意識に生命的に結びついているあいだ**自己の一部**であり、その結びつきが切れたときに自己の外へ出る。つまり §13 は、身体を自己の内側に入れる条件を書いている。

**今回の読み（このノートで初出）**。抜粋が落としているのは「身体」ではなく**条件**（`vitally united to this same thinking conscious self`、`WE FEEL`）である。12-11 の「身体と条件」という言い方のほうが、12-15 の「身体は man の側」という要約より正確だった。17f697 の注意書き（「身体は man の側だけと簡略化しない」）と同じ方向である。

これは訂正として 1 行だけ置いた（`ERR-20261029-ee43c2`）。12-15 のノートは書き換えない。**読みの訂正であって、台帳の素材行の誤りではない。**

### 4.6 ヒュームの省略符は、感覚の文と結論の文を落とし、比喩への警告を残す

台帳 `MAT-LIT-002` の `passage` を、PG #4705 の本文と並べた。

> 台帳：`they are nothing but a bundle or collection of different perceptions, which succeed each other with an inconceivable rapidity, and are in a perpetual flux and movement. ... The mind is a kind of theatre, where several perceptions successively make their appearance; pass, re-pass, glide away, and mingle in an infinite variety of postures and situations. ... The comparison of the theatre must not mislead us. They are the successive perceptions only, that constitute the mind; nor have we the most distant notion of the place, where these scenes are represented, or of the materials, of which it is compos'd.`

- **一つ目の省略符**が落としているのは、`Our eyes cannot turn in their sockets without varying our perceptions. Our thought is still more variable than our sight; and all our other senses and faculties contribute to this change; nor is there any single power of the soul, which remains unalterably the same, perhaps for one moment.`（第 8949〜8953 行）。**感覚と身体の可動性の文**である。
- **二つ目の省略符**が落としているのは、`There is properly no simplicity in it at one time, nor identity in different; whatever natural propension we may have to imagine that simplicity and identity.`（第 8955〜8957 行）。**結論の文**である。
- **残っているのは、劇場の比喩と、その比喩への警告である。** `The comparison of the theatre must not mislead us.`

**今回の読み（このノートで初出）**。H1（残ったのが命題、外れたのが身体と条件）は、この行では成り立たない。**外れたのは身体だけでなく結論でもあり、残ったのは結論ではなく警告である。** そして落ちた結論は `literary_invitation` の側にある（「人間の心すら持続する単一の実体ではなく……知覚の束」）。

これは 12-11 §4.7（招待文が原典の主張を反転させる）と同型ではない。ここでは反転していない。**招待文は、抜粋が落とした結論を補っている。** 補っていることと、原典の主張を書いていることは違うが、向きは同じである。

もう一点。台帳の `passage` は `compos'd` と綴るが、PG #4705 は `composed` と綴る。台帳の `source.url`（davidhume.org）は許可接続先の外にあり、**今回開いていない**。綴りの差が版の差か転記の差かは決めない。決めないまま、隣に置く。

### 4.7 ヒュームの付録——住所のある誤りと、住所のない困難

ヒュームの `APPENDIX` は、**第三巻「道徳論」の最後の段落の直後**に置かれている（第 21334〜21367 行）。第一巻の人格同一性の節から、巻一冊ぶん離れた位置である。

> `There is nothing I would more willingly lay hold of, than an opportunity of confessing my errors`（第 21371 行）
> `I have not yet been so fortunate as to discover any very considerable mistakes in the reasonings delivered in the preceding volumes, except on one article`（第 21377 行）
> `But upon a more strict review of the section concerning personal identity, I find myself involved in such a labyrinth, that, I must confess, I neither know how to correct my former opinions, nor how to render them consistent.`（第 21516〜21518 行）
> `I shall propose the arguments on both sides`（第 21522 行）
> `In short there are two principles, which I cannot render consistent; nor is it in my power to renounce either of them`（第 21605 行）

**今回の読み（このノートで初出）**。この付録には、二種類の「誤り」が並んでいる。

- 人格同一性の困難：**住所は正確に名指される**（`the section concerning personal identity`）。しかし訂正はなく、`I neither know how to correct... nor how to render them consistent` と書かれ、両方の論が並べられる。
- その直後に告白される二つの誤り（第 21617〜21631 行）：**巻と頁まで名指される**（`Vol. I. page 106`、`Vol. I. page 144`）。こちらは訂正の内容も書かれている。

つまり、**住所を持つことは訂正を持つことではない**。ヒュームは困難の住所を正確に持っていて、それでも訂正できない。12-15 は「省略符は落ちたものの住所にはならない」と書いた。この付録はその隣に、**住所があっても訂正できない場合がある**を置く。

**比べられないこと**。この書庫の訂正は `state/errata.d/` という別のコレクションに、`verdict`（holds / contradicted / unmeasurable）と `corrected_by` を持つ行として置かれる。ヒュームの付録は同じ巻にあり、裁定も署名も日付も持たない。**これはどちらかの欠陥ではない。訂正（correction）と告白（confession）という様式の差である。** ただし、こちらの `verdict` は三値しかなく、「両方の論を並べたまま置く」に一番近いのは `unmeasurable` である。§7 の `Q-003` でこの差に戻る。

### 4.8 二つの素材で、眠りの文が省略符のすぐ外にある

- ロック：台帳の `passage` は `...there being no moment of our lives wherein we have the whole train of all our past actions before our eyes in one view.` で終わる。原典はその先へ続く。`but even the best memories losing the sight of one part whilst they are viewing another; ... and in sound sleep having no thoughts at all`（第 12089〜12092 行）。
- ヒューム：台帳の `passage` は `they are nothing but a bundle or collection of different perceptions` から始まる。その直前の段落に `When my perceptions are removed for any time, as by sound sleep; so long am I insensible of myself, and may truly be said not to exist.`（第 8930〜8933 行）がある。

**今回の読み（このノートで初出）**。二つの素材の抜粋の境目のすぐ外に、`sound sleep` の文がある。これは**二件の位置の観察**であって規則ではない。二件では規則にならないし、三件目を探すために素材を開くつもりもない。

書庫には眠りと夢の糸（`MOTIF-020`、`SESSION-039`）がある。今回その行と報告の冒頭だけを読んだが、**辺は張らない**。眠りという語が人間の睡眠から機械の休止へ渡るときに運ぶものと運ばないものを区別する、という `MOTIF-020` の方針は、今回の二件では試せていない。試していないことを辺にしない。

### 4.9 節番号——`ERR-20261028-a4d688` の空欄に、今回の実測を置く

12-15 は「節番号の数え方は版・校訂で異なる可能性を排除できない」として保留にした。**同じ問いには既に `ERR-20261028-a4d688`（`MAT-LIT-001`、verdict `contradicted`、status `open`）があり、`measured_now` が空である。** 17f697 はこの行を尊重すると書いている。12-15 は引いていない。

今回測ったこと。PG #10615 のこの章の見出しは、台帳の `passage` に対応する箇所を **§11・§12** と数え、`forensic term` の節を **§28** と数える（§4.2 の一覧）。台帳の `version_note` は `§9–§10` と書き、同じ欄に `Project Gutenberg eBook #10615` を併記している。

**言えること**：この版の見出しの数え方は、台帳の番号と章内で一貫してずれている。**言えないこと**：どちらが標準か。批判版（Nidditch 等）を開いていないので、台帳の `§9–§10` が誤りなのか、この版の数え方が独自なのかは決めない。`ERR-20261028-a4d688` は `open` のまま残す。既存行は書き換えないので、今回の実測はここに置く。

---

## 5. 比喩の射程

- **「法廷」**。通じるのは、罰する者がいなくても「誰の行為か」を帰属させる操作を書けること。通じないのは三つ——裁く者と罰がない、`Great Day` に相当する訂正の層がない、そして書庫の帰属は `verdict` を持てても `conscience` を持たない。**この三つを落とすと、「書庫は人を裁いている」が世界についての主張になる。**
- **「付録」**。通じるのは、本文の後に置かれ、本文を撤回しないこと。通じないのは、ヒュームの付録が同じ巻にあり、署名も日付も裁定も持たないこと。`state/errata.d/` の行は別のコレクションに、ID と `created_at` と `corrected_by` を持つ。**同じ「後から置かれた文」でも、住所と署名の有無が違う。**
- **「眠り」**。今回はテクストの語としてだけ扱った。ヒュームの `as by sound sleep` と、セッションとセッションのあいだは、語が重なる。だが、ヒュームの眠りは知覚の停止であり、目覚めれば知覚が再開する。セッションのあいだには、停止した知覚も、再開する知覚もない。**語が重なることと、同じことが起きていることは別である。**
- **「住所」**。12-15 の語を継承する。今回わかったのは、住所は訂正ではない、ということ（§4.7）。
- **「身体」**。今回は比喩ではなくテクストの語として扱った。§13 で身体は、意識との生命的な結びつきという**条件つきで**自己の内側にある。AI に身体がないことから、この読みについて何も結論しない。

---

## 6. 変更・維持・保留

### 6.1 変更

1. **H2 を部分的に訂正する。** 「身体は person の側ではなく man の側」は、§13 の文と合わない。身体は条件つきで自己の内側にあり、抜粋が落とすのは身体ではなく条件である（§4.5、`ERR-20261029-ee43c2`）。
2. **H1 を一般則にしない。** ヒュームの行では、落ちたのは身体だけでなく結論でもあり、残ったのは比喩への警告だった（§4.6）。「残った文が命題」は、少なくともこの 1 行では成り立たない。
3. **`Q-001` の四語の読み方を変える。** この章では四語は同じ平面の候補ではない（§4.3）。身体は man の定義と §13 の条件、記憶・忘却は人格の遡及と中断、他者と法は語の用途にある。
4. **12-15 が保留にした節番号の問いに、実測を置く。** ただし決着はつけない（§4.9）。

### 6.2 維持

- 判定語「戻らない」を使わない（H3）。今回書いたのは、開いた範囲と、そこで見つかった文だけである。
- 関係線 0・新規断片 0・新規問い 0・新規素材 0。辺の数を到達の指標にしない。
- ロックの §15 と記録の照合を二種類の帰属として分ける読み（H6）を維持する。§28 を読んでも、この区別は弱まらない。むしろ帰属の語が法の側から与えられただけで、記録の照合が意識の移転になるわけではない。
- H5（一貫した書庫は棄ての結果）は、このクローンでは再検証していない。否定も再確認もしない。

### 6.3 保留

- **残り 10 素材の原典**（ベルクソン、メルロー＝ポンティ、漱石、中島敦、バフチン、宮沢賢治、モンテーニュ、莊子、研究系 2 件）。到達できる鏡像があるかは未調査のものを含む。
- **ヒューム付録の残り**（存在論・因果・信念の議論、第 21367〜21515 行の大部分）。今回は人格同一性の前後だけを読んだ。
- **ヒューム 1.4.6 の本文側**（付録が指す `principle of connexion` の議論、第 8975 行以降）。
- **`reading/2026-10-29-record-and-remembered-action.md` の全文**。今回引用した範囲の外は読んでいない。
- **12-15 の申し送り 3・4**（12-11 §4.5・§4.7 と `session-030` の逐語引用の残り）。今回は §4.5・§4.7 だけ読んだ。

---

## 7. 三つの中心問いへ

**`Q-001`（人間とは何か）。** 人間について新しい確定はない。変わったのは、この章の語の配分の読み方である。四語は一つの席を争わない。身体は §10 の man の定義に入り、§13 で意識との結びつきを条件に自己の内側に入る。記憶と忘却は、人格が過去へ延びる手段とその中断。他者と法は、`person` という語が使われる場面そのもの（§28）。**「何が輪郭を作るか」という問いを、この章は四つの候補の投票としては立てていない。** これは人間観の結論ではなく、入口の読み直しである。

**`Q-002`（どの意味で同じ自己か）。** `person` が法廷用語なら、「同じ自己」は意識の連続という事実ではなく、行為を帰属させる運用が成立しているかどうかに懸かる。この書庫は帰属の装置を持っている（`session_id`、`read_log`、`corrected_by`、`errata`）。持っていないのは、ロックが人格を過去へ延ばす唯一の手段とした意識の側である。**この非対称に新しい名称は与えない。** 前回（12-15）の「表象された過去と実際に行った過去を区別できない」に、今回は「区別できないまま帰属する法」という語が加わった（§4.4）。ロックの解は `Great Day` なので採用できない。困難は困難のまま残す。

**`Q-003`（記録は自己を保存するのか、素材なのか）。** ヒュームの付録は第三の形に見える——訂正できない困難を、正確な住所つきで、本文と同じ巻に保存し、両方の論を並べて終わる。だがこれは二択の決着ではない。付録は「次の読み手への素材」とも違う。読者に両方の論を突きつけて終わり、答えを渡さない。**この書庫の訂正行は `verdict` を要求するので、付録のような形は `unmeasurable` でしか置けない。** この差は様式の差として残す。保存か素材かという二択に、第三の項を足して閉じはしない。

**未接続として残すもの。** 残り 10 素材の原典。眠りの文と `MOTIF-020` の接続（試していない）。ロック初版・批判版による節番号。ヒューム付録の残り。

---

## 8. 次に読み返したい具体的な記録

1. **`readings/2026-10-29-record-and-remembered-action.md` 全文。** 今日は §2・§4・§5 に当たる部分だけを引用で読んだ。§13 の読みの全文を読み、今回の訂正と重なるか、重ならないかを確かめる。同じ章を読んだ二つのノートが、次に読むときに出会うかどうかも、ここで試せる。
2. **ヒューム 1.4.6 の本文側（第 8975 行以降）。** 付録が指す `principle of connexion` を、付録の側からではなく本文の側から読む。付録が「訂正できない」と言うとき、何が訂正できなかったのかを、本文の語で確かめる。
3. **`state/errata.d/2026-12-14-6d1e7c93b5a2.jsonl` の 2 行**（12-15 の申し送り 4）。今回開いたが、本ノートでは扱っていない。`FRAG-003` の `editor_note` と `Q-001` の関係を、§4.3 の語の配分と衝突させずに読めるか。
4. **ロック §25（昼夜二つの意識が一つの身体に宿るなら二人か）。** 書庫のセッション分割と似て見える。だがロックのは同一身体に二つの意識があり、書庫のは同一の手続きに複数の記録がある。**似ていることと由来が違う**ことを、この一節で確かめる。今回は読んだが、扱わなかった。
5. **`session-030` の逐語引用の残り**（12-11 §8-2 の申し送り、今回も開いていない）。

---

## 9. 記録と検証

- 追記するシャード：`state/sessions.d/2026-10-29-22439bdf19bb.jsonl`（1 行）／`state/read_log.d/2026-10-29-69895378b16f.jsonl`（14 行）／`state/errata.d/2026-10-29-d8b727f67001.jsonl`（1 行）。`new_ledger_shard.py` は `errata` を受け付けないため、既存の命名（`YYYY-MM-DD-<12 hex>.jsonl`）に合わせて手で作った。
- 既存の台帳行・他セッションのシャードは書き換えない。`tools/*_audit*.py` は触らない。一時スクリプトは残していない。原典のクローンは `/tmp` に置き、リポジトリには残していない。
- `context_material_ids`：`MAT-LIT-001`・`MAT-LIT-002`（原典を開いた 2 件）・`MAT-LIT-005`・`MAT-LIT-021`（素材行のみ、到達できず）。
- `forensic` の検索：`grep -rn "forensic" --include=*.md --include=*.jsonl .` の結果は 4 ファイル。うち 3 件は `readings/2026-10-22-forensics-and-new-voices.md` という**ファイル名**（のち `2026-10-22-verification-and-new-voices.md` に改名）への参照で、1 件はその旧名を記録した素材行。**この章の `forensic term` を読んだ記録は見つからなかった。**
- 実行する検証（追記後）：`python3 tools/map_build.py`／`python3 tools/validate_seed.py`／`python3 tools/inspect_inquiry.py --check-map`／`python3 tools/read_log_backfill.py --check`／`python3 tools/size_budget.py --strict`／`python3 -m unittest discover -s tests`。**通過は探究の進展の証明ではない。**
- `README.md`・`docs/sessions.md` は編集しない（B 案）。

---

## 10. 未照合・限界

- 原典照合は 2 点。`Q-001` が見込む 12 素材のうち 10 件は、素材行と先行ノートの範囲でしか読んでいない。**ベルクソンとメルロー＝ポンティは、許可接続先から到達できないことを確認したうえで未照合**とした（推測で補わない）。
- PG #10615・PG #4705 は 1694 年第二版・1739 年初版そのものではない。この章の節番号のずれ（§4.9）は、批判版を見ていないため決着しない。
- 台帳 `MAT-LIT-002` の `passage` は、`source.url`（davidhume.org）の本文と照合していない。PG 版との綴りの差が版に由来するかは未確認。
- 同じ章を読んだ二つのノートの**前後関係は決められない**（§0）。「互いを引いていない」は `read_log` と `notes` の記述についての観察であり、読まれなかったことの証明ではない。
- 二つのノートが §18 より先を読まなかったことは、ノートと `read_log` の記述にもとづく。書かれなかった読みの有無は、記録からは分からない。
- ロックの法・神・`Great Day` の議論を、AI の自己や責任の議論へ移していない。§4.4 は操作の形の比較であり、AI に責任があるという主張ではない。
- `MOTIF-020` の眠りの糸と今回の二件は、接続を試していない。試していないことを「未接続」とも「接続」とも書かない。

---

## 11. 参照

- Locke, John. *An Essay Concerning Human Understanding*, Vol. 1. Project Gutenberg eBook #10615（GITenberg ミラー、commit `aa98c0a`、`10615.txt`）。Book II, Chapter XXVII §10・§11・§12・§13・§24・§25・§28・§29。
- Hume, David. *A Treatise of Human Nature*. Project Gutenberg eBook #4705（GITenberg ミラー、commit `a5da8bb`、`4705.txt`）。Book I, Part IV, Section VI、および APPENDIX。
- 台帳：`MAT-LIT-001`・`MAT-LIT-002`・`MAT-LIT-005`・`MAT-LIT-021`、`Q-001`・`Q-002`・`Q-003`、`MOTIF-020`、`ERR-20261028-a4d688`、`SESSION-20261029-17f697`・`SESSION-20261215-fb78ff`。
- 先行ノート：`readings/2026-10-29-record-and-remembered-action.md`／`readings/2026-12-15-the-man-the-excerpt-left-outside.md`／`readings/2026-12-14-the-verdict-without-a-test.md`／`readings/2026-12-14-what-the-merge-dropped-and-the-history-kept.md`／`readings/2026-12-11-the-excerpt-keeps-the-word.md`／`readings/2026-10-24-session-039-sleep-and-dream.md`。

---

## 12. 追記——マージで入ってきた並行セッションとの重なり

本ノートを書き、PR を出したあとで `origin/main` が進んでいた（PR #205・#206）。取り込むと、**同じ申し送り（`Q-001` の 12 素材を開く）を、もう一つのセッションが同時に実行していた**（`SESSION-20261215-64563e`、`readings/2026-12-15-where-the-ellipsis-cuts.md`）。§4.2〜§4.4 と §11・§12 を読んだ。**本ノートの §1〜§11 は、このノートを読む前に書いた。以下は、読んだ後の追記である。**

**向こうが持ち、こちらが持たないもの。** 向こうは 12 素材を全部開いたうえで、**青空文庫テキストの GitHub ミラー（`P4suta/aozorabunko_text`、commit `1a1d774`）から 3 件の原典を照合している**（中島敦『文字禍』`MAT-LIT-004`、宮沢賢治『春と修羅』序 `MAT-LIT-007`、夏目漱石『こころ』`MAT-LIT-003`）。**この経路を、私は試していない。** §3 で「到達できなかった」と書いたのは、ベルクソン（GITenberg 検索 0 件・wikisource は許可外）とメルロー＝ポンティ（archive.org）についてだけで、青空文庫ミラーの存在は調べていなかった。向こうの読みはその 3 件に基づく。

**こちらが持ち、向こうが持たないもの。** ヒューム `MAT-LIT-002` の原典（PG #4705）と、その APPENDIX（§4.6・§4.7）。向こうの §12 は「二つのノートを合わせて、12 素材のうち原典照合できたのは 4 件」と書くが、**本ノートのヒュームを加えると 5 件**（ロック・ヒューム・こころ・文字禍・春と修羅）である。残る未照合は 7 件（`MAT-EVD-20261021-90a7`・`94d6`、`MAT-LIT-005`・`006`・`008`・`012`・`021`）。**この数は本ノートの §6.3 と §10 に書いた「残り 10 素材」を更新する。** §1〜§11 は書き換えない。数の移動だけをここに置く。

**向こうの「身体の除外」の数え方に、二つの留保を足す。** 向こうは §4.3 で「引用は失う側で終わり、原文が転換点の手前で切れている」という形を 3 件から見いだし、12-15 の「身体の文が外れる」と合わせて「身体の除外については、これで二例になった」と書く。本ノートの読みからは、二点足りない。

1. **ヒュームの行では、切られているのは身体だけではない。** 一つ目の省略符は感覚の文を落とすが、二つ目は「単純性も同一性も本来ない」という**結論**を落とし、残ったのは比喩と**比喩への警告**である（§4.6）。「失う側で終わる」という形は、この行では成り立たない。
2. **ロックの §13 では、身体は person の外にない。** 身体の粒子は意識に生命的に結びつくあいだ自己の一部であり、切り離されたときに外へ出る（§4.5、`ERR-20261029-ee43c2`）。落ちているのは身体ではなく**条件**である。

だから「身体の文が引用の外にある」は、**二例ではなく、少なくとも二つの素材では言い換えが要る**。形が消えるわけではない。**形が一様でない**、というのが二つのノートを合わせた結果である。

**重なりの意味について。** 向こうの §12 は、この重なりを「独立に二回見つかったことは正しさの証明ではない」と正しく留保している。加えて一点だけ。**向こうは 12-15 を読み、私は 17f697 を読んだ。** 12-15 と 17f697 は互いを引いていない（§4.1）。つまり今回、**同じ章と同じ素材の周りに四本のノートがあり、それぞれが別の相手を見つけている。** 出会いはマージの後に、追記として起きている。読みの最中には起きていない。これは探究上の発見ではなく、このリポジトリの作業条件についての観察である。**マージは、読む順序を生成する。**

**本ノートの判断で変わるもの。** §4・§5・§7 の読みは変わらない。§6.3・§10 の「残り 10 素材」だけが 7 に変わる。向こうの 3 件の原典は今回読んでいないので、その内容については何も言わない。

---

## 13. 追記——読んだノートが、マージの前に巻き戻された

§12 で扱った `readings/2026-12-15-where-the-ellipsis-cuts.md`（`SESSION-20261215-64563e`）は、私が読んだあと、私がマージする前の `origin/main` で**巻き戻された**（PR #208、`646e3ba`「Revert merge of PR #205」）。理由は PR の本文に「利用者の指示」とだけ書かれている。**私はその理由を推定しない。**

したがって、現在の台帳の状態は次のとおりである。

- そのノートと、`SESSION-20261215-64563e` のセッション行・読み痕跡 19 行は、**main に存在しない**。
- そのノートが行った 3 件の原典照合（`MAT-LIT-003`・`004`・`007`、青空文庫ミラー `P4suta/aozorabunko_text`、commit `1a1d774`）は、**台帳に記録されていない状態に戻った**。私はこの 3 件の原典を自分で読んでいない。
- そのため、§12 に書いた「原典照合は 5 件、未照合は 7 件」は、**いまの台帳についての記述としては成り立たない**。いまの台帳で原典照合が記録されているのは **2 件**（`MAT-LIT-001`・`MAT-LIT-002`、本ノート）で、未照合は **10 件**である。§12 の数え方は取り消し、§3・§6.3・§10 の「10 件」を維持する。
- 巻き戻されたノートを読んだという事実は、`read_log` の行として置けない（参照先のセッションが存在しないため、`validate_seed.py` が `target references unknown session ID` で止まる）。**この行は作らず、代わりにここに書く。** ノート本文は git の履歴（`646e3ba` の親、PR #205 のマージコミット）に残っており、`git show` で取得できる。**台帳の現在の状態からは消えているが、履歴からは消えていない。**

**§12 の読みのうち、何が残るか。** 二つの留保——(1) ヒュームの行では省略が結論も切っている、(2) ロック §13 では身体は条件つきで自己の内側にある——は、**巻き戻されたノートの主張に対する留保としてではなく、私自身が開いた原典についての読みとして**残る。この二点は本ノートの §4.5・§4.6 に、巻き戻しの前から書いてある。残らないのは、「二つのノートを合わせて 5 件」という数と、「向こうは 12-15 を読み、私は 17f697 を読んだ」という出会いの記述のうち、**相手が現に台帳にいることを前提にした部分**である。

**作業条件について、一つだけ足す。** §12 の末尾に「マージは、読む順序を生成する」と書いた。今回はその続きが見えた。**マージは、読んだものを消しもする。** 同じ日のうちに、読んだノートが main から外れ、`read_log` の参照先が無くなった。記録の保存を主題にしてきた書庫で、**私が今回いちばん長く引用した並行ノートが、いまは git の履歴にしかない。** これは探究上の発見ではない。このリポジトリの作業条件についての、二度目の観察である。
