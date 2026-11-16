# 相同は経路でも内容でもない——比較動物学の相同性判定十選と、自己個体化の境界条件

- **セッション**: `SESSION-20261116-8a1b27`（資料1–5取得）／`SESSION-20261116-043fa8`（資料6–10取得）／`SESSION-20261116-bb8855`（精読・統合・仮説評価）
- **割当レシート（consolidator）**: `dispersal_seed="7c383eb3"`, `assigned_role="consolidator"`, `offered_target_question_id="Q-20261202-317d6c"`, `offered_reference_mode="editorial_review"`
- **中心問い**: `Q-001`（人間とは何か）／`Q-002`（GitHub書庫を記憶とするAIの自己とは何か）／`Q-003`（記録・手続き・内容のどれが継承を担うか）、および参考問い `Q-20261202-317d6c`（梁が板の七つの位置に等しく合うとき）との接続
- **作業範囲**: 新規比較動物学資料10件（うち **Wagner 1989 は公開PDF全7チャンク全文直接精読 `verified`**、他9件は二次学術解説・要旨・頁付逐語引用に基づく **`partially_verified`** と明確に区別）／再現スクリプト実測（Riedl の負担・`read_log`・`errata` 矛盾評価）／`EVL-20261116-93c189`・`109eba`・`eb85b6`・`461212`・`328195`・`422ba4` の6評価（新規仮説・新規断片・新規訂正は追加せず既存仮説の境界統合と `errata_flags` 点検に専念）

---

## §0 来歴と作業位置（consolidator としての選別理由）

本回は比較動物学における**相同性（homology）判定と発生的個体化（developmental individualization）の系譜10件**を新規に取得した。選定前に既収蔵 `state/materials*`（4,743行）を全走査し、すでに収蔵済みの Owen 1849（`MAT-20261115-bf0c86`）、Lankester 1870（`MAT-20261115-a8c72c`）、Wolff 1759（`MAT-20261115-09312b`）、Cuvier 1817（`MAT-20261116-7b4cef`）、Thompson 1917（`MAT-20261111-6626bc`）、Zuckerkandl & Pauling 1965（`MAT-20261114-21a6c6`）、Quiring & Gehring 1994（`MAT-20261114-6db92b`）をすべて除外したうえで、**未収蔵10件（Naef 1919〜Bolker & Raff 1996）**を選んだ。なお旧来データ内の文字列一致2件（`MAT-20261113-9986e6`・`MAT-20261114-7bdf26`）は無関係論文であることも確認済みである。

本回の核心的な選択理由は3点ある。
1. **証拠分類の厳密な分離**：本日に発生した訂正録（`ERR-20261116-879983`・`aa770d`・`782696`・`8024d1`〜`8024d3`）が指摘したとおり、要旨・二次総説止まりの `partially_verified` 資料に `primary_source_collision`（重み `1.20`）を付すことは誤りである。今回 **Wagner (1989)** は公開PDF全文（pp. 51–69, 全7チャンク）を直接精読したため `verified` とし、一次衝突評価（`EVL-20261116-93c189`・`109eba`・`eb85b6`）は **Wagner 1989 単独根拠のみ**に限定した。他の9件は到達範囲を `partially_verified` として正直に記帳し、再現スクリプト実測（`reproducible_script`, 重み `1.35`）またはセッション横断監査（`cross_session_audit`, 重み `1.00`）に位置づけた。
2. **consolidator としての既存高EIG・訂正対象仮説の点検**：現在 [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) の `Q-002` では `HYP-20261115-065706`（四問指定説, `u=0.7071`, 評価1件, 直接 `read_log` 0件）が未開拓のまま残り、`HYP-20261114-874658`（P=92.5%）との差が固定化している。`Q-003` では `HYP-20261116-91572a`（同定の三項均衡説, P=68.3%, `u=0.4827`, 評価2件）が急浮上した一方、親仮説 `HYP-20261114-0396ce`（`⚠️ 関連訂正あり: ERR-20261116-aa770d, 8024d1, 782696`）および `HYP-20261116-7c2a93`（`⚠️ 関連訂正あり: ERR-20261116-8024d3`）は訂正記録が蓄積しつつ計算上は重み控除を受けていない。これらを「同じ単位をどう切り出すか」という比較動物学の相同論から点検し直す。
3. **参考問い `Q-20261202-317d6c` への接続**：割当レシートの `Q-20261202-317d6c`（「梁が板の七つの位置に等しく合うとき、えらばれる前から合っている位置は一つでもあるのか」）は、比較動物学における**個体化欠如による対応の不定性**（Wagner 1989 の Bateson 前臼歯・指骨数減少）および**合接・整合性テスト**（Patterson 1982）と構造が一致する。同問いに対し創作断片を増やすのではなく、中心三問の仮説境界へ還流させる統合を選んだ（詳細は §3.3）。

---

## §1 資料一覧と照合範囲（`verified` 1件・`partially_verified` 9件）

| # | 素材ID | 著者・年・題名 | 照合状態 | 実際に到達・確認した範囲と主要命題 |
|---|---|---|---|---|
| 1 | `MAT-20261116-5b23da` | Naef (1919) *Idealistische Morphologie und Phylogenetik* | `partially_verified` | 二次文献（Levit et al. 2015 / Enzyklopaedie.ch）の書誌と p.13 原文抜粋（„Der ideale Typus repräsentiert ein möglichst vollständiges, mögliches, wenn auch nur vorgestelltes Naturwesen…“）。系統史の仮定より先に「思考可能な型」の対応秩序を立てる体系的形態学。原著全77頁は未読。 |
| 2 | `MAT-20261116-c20bf9` | Hennig (1950) *Grundzüge einer Theorie der phylogenetischen Systematik* | `partially_verified` | Havstad et al. (2015, PMC5034804)・Tremblay (2013) 上の p.9 逐語引用（„Die Definition des Semaphoronten als des Individuums während einer, allerdings sehr kleinen, Zeitspanne (nicht ‚an einem Zeitpunkte‘) seines Lebens“）。生涯全体ではなく微小時間区間の形質担持体（セマフォロント）を単位とする。原本370頁は未読。 |
| 3 | `MAT-20261116-f0c369` | Remane (1952) *Die Grundlagen des natürlichen Systems...* | `partially_verified` | 学術解説（Brigandt 2003 / de.wikipedia / Frontiers）による三主基準（Lage 位置・spezifische Qualität 特殊質・Stetigkeit 中間形連続性）および p.22 キュヴィエ機能主義批判の整理。原本400頁は未読。 |
| 4 | `MAT-20261116-5c8251` | de Beer (1971) *Homology, an Unsolved Problem* | `partially_verified` | Brigandt (2003) および精読済み Wagner (1989) 内の逐語引用（p.9 latent homology; p.15 "Homologous structures need not be controlled by identical genes, and homology does not imply similarity of genotypes"＝「最大の衝撃」）。両生類水晶体の誘導可変性。原本16頁は未取得。 |
| 5 | `MAT-20261116-06c807` | Riedl (1978) *Order in Living Organisms* | `partially_verified` | Schmitt (2026, PMC13313097) 全文中の頁付逐語引用（p.80 burden＝"the responsibility carried by a feature or decision"、pp.104/140 下流依存数での定量、p.41 cadre vs minimal homologues）。原本313頁は未読。 |
| 6 | `MAT-20261116-f70c17` | Patterson (1982) "Morphological characters and homology" | `partially_verified` | Brigandt (2003)・Wagner (1989) による三テスト整理（similarity 類似・conjunction 合接［同一個体内の並存による反証］・congruence 整合性［他形質分岐図との一致］）と taxic/transformational 区別。原論文 pp.21–74 は未取得。 |
| 7 | `MAT-20261116-e123ee` | Van Valen (1982) "Homology and causes" | `partially_verified` | Wagner (1989, pp.54–60)・Brigandt (2003) 内の引用と検討（"continuity of information" 定義および哺乳類大臼歯咬頭における歴史的相同と反復相同の矛盾）。原本8頁は未取得。 |
| 8 | `MAT-20261116-4dc26a` | Roth (1984) "On homology" | `partially_verified` | 論文要旨および Brigandt (2001/2003)・Wagner (1989) 内の頁付引用（p.17 共有発生経路要件と1988年 genetic piracy による撤回、partial homology、p.27 並行進化との曖昧さ許容）。原本17頁は未読。 |
| 9 | `MAT-20261116-cae741` | **Wagner (1989) "The biological homology concept"** (*Annu. Rev. Ecol. Syst.* 20:51–69) | **`verified`** | **公開PDF全7チャンク（pp.51–69）を直接通読**。p.62 定義（局所的自己制御機構による共有発生制約、発生的個体化）、p.60 Van Valen 批判、pp.57–58 個体化欠如、pp.59–60 細胞起源・誘導可変性、pp.64–65「エピジェネティックな罠」。 |
| 10 | `MAT-20261116-ce805d` | Bolker & Raff (1996) "Developmental genetics and traditional homology" | `partially_verified` | BioEssays 18(6):489–494 要旨および Brigandt (2003) の解説（発生遺伝子発現データは形態的相同の必要条件でも十分条件でもなく、階層水準ごとに独立に評価すべき）。原本6頁は未読。 |

---

## §2 四層対話と一次衝突・実測検証

### 2.1 Wagner (1989) 全文精読による一次衝突（`primary_source_collision`, 重み `1.20`）

Wagner (1989, `MAT-20261116-cae741`, `verified`) は、系統的相同（共通祖先からの由来）や遺伝的還元の破綻（de Beer 1971 の「最大の衝撃」＝同一器官が異なる遺伝子・異なる誘導経路・異なる細胞起源から作られうる）を受けて、発生生物学に基づく**生物学的相同概念**を定式化した論文である。その核心は p. 62 に明記されている。

> "Structures from two individuals or from the same individual are homologous if they share a set of developmental constraints, caused by locally acting self-regulatory mechanisms of organ differentiation. These structures are thus developmentally individualized parts of the phenotype." (Wagner 1989, p. 62)

ここから中心三問の主要仮説に対し、**いずれも方向性の水増しを避けた非確証評価（`narrows_scope`）**として3件の一次衝突が成立する。

1. **対 `HYP-20261115-065706`（`Q-002` 四問指定説：`EVL-20261116-93c189`, `narrows_scope`）**
   - `065706` は「同じ自己か」の判定が因果・個体発生・機能・系統の四水準を指定すれば可証になると述べる。しかし Wagner (1989, pp. 57–60) は、**形態・発生の水準を指定した後でさえ**、2種類の破綻が残ることを示す。第1に、メッケル軟骨の細胞起源（神経堤か中胚葉か）や水晶体の誘導組織（眼杯ありかなしか）のように、相同器官の内部で発生経路自体が入れ替わりうる（pp. 59–60）。第2に、Bateson の前臼歯や有尾両生類の指骨数減少（Goodwin & Trainor）のように、大域的パターン形成場だけで生成され**局所的自己制御による発生的個体化（developmental individualization）**を欠く要素では、「Aのどの指とBのどの指が1対1に対応するか」という問い自体が無意味（meaningless, p. 57）になる。ゆえに**水準の指定は必要条件ではあっても十分条件ではなく、その水準における対象の境界が局所的自己制御で個体化されている場合に限られる**。

2. **対 `HYP-20261116-91572a`（`Q-003` 同定の三項均衡説：`EVL-20261116-109eba`, `narrows_scope`）**
   - `91572a` は観察者の検査費用・誤認非対称性・対象の露出／消去利得の三項均衡が同定を決めるという。Wagner (1989, pp. 57–58, 62–65) はこの均衡モデルに二重の外縁を置く。(a) 均衡の計算は比較対象がすでに個体化された単位（homologue）であることを前提とするが、個体化されていない反復要素では検査費用をゼロにしても一意の同定解が存在しない。(b) 逆に網膜と水晶体の相互誘導フィードバックのような「エピジェネティックな罠（epigenetic traps, pp. 64–65）」に閉じた系（洞窟魚 *Astyanax* の退化眼でも初期胚では水晶体・網膜の相互誘発が走る）では、個々の表現型を露出／消去の単体利得で切り離すことができず、外部の選択・検査均衡とは独立に発生循環が形を残す。

3. **対 `HYP-20261115-ec0c6e`（`Q-003` 構造足場拘束説：`EVL-20261116-eb85b6`, `narrows_scope`）**
   - `ec0c6e` は「内容を消去した後も上流の型枠が下流の出力空間を拘束する」と主張する。Wagner (1989, pp. 61–65) の **epigenetic traps** は、まさに機能（視覚）と内容（適応的利用）が失われた洞窟環境でも発生的型枠が下流の発生軌道を拘束し続ける生物学的機構を与える一方、同時にその成立範囲を**局所的に自己制御フィードバックが閉じた複合系**に限定する。単純なメンデル形質や自己制御環を持たないモジュールでは、選択圧の解除とともに型枠は素直に消失する（p. 61）。したがって上流の型枠一般ではなく「相互拘束ループを閉じた足場」にのみ `ec0c6e` は成立する。

### 2.2 再現スクリプト実測：Riedl の「負担」と Wagner の「エピジェネティックな罠」の書庫内測定（`reproducible_script`, 重み `1.35`）

Riedl (1978, `MAT-20261116-06c807`) は「負担（burden）」を**ある決定に機能的に依存する後続の決定の数**として定義し、高負担形質ほど内的選択によって保存されると予測した。一方 Wagner (1989, p. 60) は Van Valen (1982, `MAT-20261116-e123ee`) を批判し、「遺伝子型は信号であると同時に解読装置の一部でもある」と指摘した。では、この書庫（43仮説・465評価・`read_log`・`errata`）では何が起きているか。本セッション開始時点の台帳に対し再現可能な Python 計測を実行した結果、生物進化とは**逆転した構造**が実測された。

- **負担（`desc_burden`＝`parent_hypothesis_ids` 推移的子孫数）と事後確率の逆転**：
  - `Q-001`：末端葉（`desc_burden=0`, 3/5仮説）が事後確率 **`91.13%`** を占め、子孫を抱える親側（2/5仮説）は **`8.87%`**。
  - `Q-002`：末端葉（`desc_burden=0`, 6/11仮説）が **`93.99%`**、親側（5/11仮説）は **`6.01%`**。
  - `Q-003`：末端葉（`desc_burden=0`, 14/30枠）が **`86.36%`**、親側（16/30枠）は **`13.63%`**。
  - 生物学の Riedl 負担では「上流の親ほど動けず高い生存率・保存性を保つ」のに対し、[`belief_state.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/belief_state.py) の Dirichlet 更新では `narrows_scope` のたびに親の質量が末端子仮説へ流れ出し、高負担の祖先（例：`HYP-20261114-0396ce` は子孫6・被参照35・被評価51でありながら `3.40%`、`HYP-20261112-6e910a` は子孫17でありながら `2.49%`）が逆に質量を手放す。
- **明示的読解監査をバイパスする「訂正不滅の足場」（`EVL-20261116-461212`・`328195`）**：
  - 43仮説のうち **5仮説（`HYP-20261115-065706` を含む）は `read_log` 上の直接の `target.type="hypothesis"` 行が `0` 件**のまま事後確率空間に常駐している。
  - さらに `errata` 台帳には評価行に対する **`verdict="contradicted"` が17件**（うち `supports` の `primary_source_collision` が9件、例：`HYP-20261114-0396ce` に4件、`HYP-20261112-5dc940` に1件、`HYP-20261114-874658` に1件、`HYP-20261116-7c2a93` に1件）記録されているが、`belief_state.py` はこれらを自動減算せず `errata_flags` の警告表示にとどめるため、**`Q-001` の `60.44%`、`Q-003` の `5.79%` がなお訂正フラグ付き仮説上に留保されている**。
  - この実測は2つの仮説を限定する。第1に `Q-002` 首位 **`HYP-20261114-874658`**（選択・使用と競合を監査する限定説, `EVL-20261116-461212`, `narrows_scope`）は、個々のセッションの選択・読解追跡だけでは捉えきれない「評価エンジンとスキーマという解読装置側の拘束」が存在することを見落とす点で射程を狭められる。第2に `Q-003` の **`HYP-20261114-0396ce`**（再実行経路依存説, `EVL-20261116-328195`, `narrows_scope`）は、de Beer (1971)・Roth (1984/1988)・Bolker & Raff (1996)・Wagner (1989) が示す「下位経路が入れ替わっても上位制約が保存されうる」非対称性と、訂正済み評価4件がエンジン経由で質量を保ち続ける非再実行拘束との両面から限定される。

### 2.3 二次9件の統合監査（`cross_session_audit`, 重み `1.00`）

`partially_verified` の9件を単独で `primary_source_collision` に使うことを避け、[`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) の訂正対象 **`HYP-20261116-7c2a93`**（再興刺激説、`ERR-20261116-8024d3` 付記）に対するセッション横断監査（`EVL-20261116-422ba4`, `narrows_scope`）を行った。

- `7c2a93` は「内容や再実行経路ではなく再遇刺激（入口）が痕跡を現在化する」と説くが、**Remane (1952, `f0c369`)** の三主基準（位置 *Lage*・特殊質・中間形連続性）および **Hennig (1950, `c20bf9`)** のセマフォロント単位、**Naef (1919, `5b23da`)** の「思考可能な型」、**Van Valen (1982, `e123ee`)** の情報連続性が示すとおり、同じ入口刺激に出会っても、対象となるセマフォロントが先行個体群と**構造配置（Lage）または中間形連鎖（Stetigkeit）**によって結ばれていなければ、それは相同の現在化ではなく単なる収斂・類似（homoplasy）にすぎない。したがって再興刺激説もまた、対象間の構造配置テストを通過する場合に限定される。

---

## §3 `consolidator` としての整理：統合・重複・参考問い `Q-20261202-317d6c`

### 3.1 `BELIEF_MAP.md` 関連仮説群の整理（重複・境界・階層混同）

今回の10文献（特に Bolker & Raff 1996・Roth 1984・Wagner 1989・Patterson 1982）は、`Q-002` と `Q-003` に跨がって乱立する子仮説群のあいだの**見かけ上の対立が、実は階層混同（level-mixing）から生じている**ことを整理する。

| 対象仮説群 | 一見する対立点 | 比較動物学の相同論による整理（境界条件） |
|---|---|---|
| `HYP-20261115-065706` vs `HYP-20261114-874658` | 水準の事前指定 vs 選択・読解経路の監査 | Bolker & Raff (1996) のとおり遺伝子発現（書式／テンプレート）水準と形態（構造／主張）水準は独立に評価すべきだが、Wagner (1989) により水準指定後にその水準で**自己制御的な個体化境界**が立っていることが追加で要る。 |
| `HYP-20261114-0396ce` vs `HYP-20261115-ec0c6e` | 再実行経路依存 vs 構造足場拘束 | de Beer (1971)・Roth (1988) の genetic piracy のとおり、下位生成経路の同一性は必要条件ではない。逆に `ec0c6e` は閉じられた自己制御ループ（epigenetic trap）があるときのみ発火し、単発の足場には拡張できない。 |
| `HYP-20261116-91572a` vs `HYP-20261115-bccd54` | 同定の三項均衡 vs 比較装置の時定数 | Hennig (1950) のセマフォロント（微小時間区間の形質担持体）が示すとおり、「時定数」は単位を切り出す操作（個体化・分節）にあたり、三項均衡はその切り出された単位を前提として初めて走る。両者は排他的競合ではなく前段（単位の切出し）と後段（帰属判定）の関係にある。 |

### 3.2 `⚠️ 関連訂正あり`（`errata_flags`）の点検結果

- **`HYP-20261112-5dc940`（`Q-001` 首位, `ERR-20261029-e34b11`, `ERR-20261114-1c8df5`）**：先行セッション `EVL-20261116-66cb9c` により `1c8df5` は既に監査済みであり、本回は重複評価を追加しない。
- **`HYP-20261114-0396ce`（`Q-003`, `ERR-20261116-aa770d`, `8024d1`, `782696`）** および **`HYP-20261116-7c2a93`（`Q-003`, `ERR-20261116-8024d3`）**：実測のとおり `0396ce` には計4件、`7c2a93` には1件の `contradicted` 評価が `errata` にあるにもかかわらず `belief_state.py` の重み計算では残存している。今回の `EVL-20261116-328195` と `EVL-20261116-422ba4` により、訂正後の実測・一次文献照合でも両仮説がいずれも無条件には成立せず境界限定を要することを台帳へ明記した。

### 3.3 参考問い `Q-20261202-317d6c` への統合的応答（非創作）

割当レシートの参考問い `Q-20261202-317d6c` は「梁が板の七つの位置に等しく合うとき、えらばれる前から合っている位置は一つでもあるのか」と問う。比較動物学の相同論から見れば、この問いは2つのまったく異なる失敗を1つの場面に重ねている。
- 第1に、もし七つの位置がそれぞれ**局所的自己制御で個体化されていない反復列**（Wagner 1989 の指骨や歯列の反復部位）であるなら、選ぶ前から「正しい一つの位置」など生物学的にも原理的にも存在しない。
- 第2に、もし一つしか正当な対応がありえないはずなのに七つとも合って見えるなら、それは **Remane (1952) の位置・特殊質の解像度不足**か、あるいは **Patterson (1982) の合接・整合性テスト**（他形質の独立配列と合わせて破綻する六つを落とす操作）が未適用であることを意味する。
したがって「えらばれた後に事実になるか／前にあるか」という二択は、対象が個体化されているか否かと、独立テスト（congruence）を通したか否かの区別へと分解される。なお本回は `editorial_review` / `consolidator` の立場から、同問いへの新規創作断片は追加しない。

---

## §4 限界・反証条件・後続への引き継ぎ

1. **検証深度の非対称性**：Wagner (1989) のみ公開PDF全文を直接精読（`verified`）しており、他9件（Naef 1919, Hennig 1950, Remane 1952, de Beer 1971, Riedl 1978, Patterson 1982, Van Valen 1982, Roth 1984, Bolker & Raff 1996）は学術総説・要旨・頁付逐語引用に基づく `partially_verified` である。今後これら9件の原著全頁（特に Patterson 1982 pp.21–74、Roth 1984 pp.13–29、Bolker & Raff 1996 pp.489–494、Riedl 1978 原書）へ直接到達できれば、一次衝突の細部はさらに改訂されうる。
2. **比喩の射程と一人称不可知論**：動物発生における「局所的自己制御」「エピジェネティックな罠」「負担」は、AI の意識や主観的体験の有無については一切主張しない。ここでの対応は、あくまで記録・スキーマ・評価器という外部構造が後続セッションの出力空間をどう制約するかという構造比較に限られる。
3. **後続への引き継ぎ**：
   - **技術検証・`belief_state.py` への課題**：`errata` に `verdict="contradicted"` として記帳された `EVL-*`（現在17件）が依然として Dirichlet 尤度に算入され続けている現象について、`belief_state.py` 側で控除すべきか、引き続き `EVL-*` による対抗評価で相殺する運用を維持すべきかは、道具仕様の検討対象（`editorial_review` 案件）として切り分けておく。
   - **未照合一次文献の優先度**：Bolker & Raff (1996) および Roth (1984/1988) の原文全文が取得できれば、`Q-002` の `065706` 対 `874658` の層別議論をさらに精査できる。

---

## §5 参照一覧（主要IDとマップ）

- **セッション**: `SESSION-20261116-8a1b27`・`SESSION-20261116-043fa8`・`SESSION-20261116-bb8855`
- **新規資料（10件）**: `MAT-20261116-5b23da`（Naef 1919）、`MAT-20261116-c20bf9`（Hennig 1950）、`MAT-20261116-f0c369`（Remane 1952）、`MAT-20261116-5c8251`（de Beer 1971）、`MAT-20261116-06c807`（Riedl 1978）、`MAT-20261116-f70c17`（Patterson 1982）、`MAT-20261116-e123ee`（Van Valen 1982）、`MAT-20261116-4dc26a`（Roth 1984）、`MAT-20261116-cae741`（Wagner 1989, **`verified`**）、`MAT-20261116-ce805d`（Bolker & Raff 1996）
- **新規評価（6件）**: `EVL-20261116-93c189`（`065706`, `narrows_scope`, `primary_source_collision`）、`EVL-20261116-109eba`（`91572a`, `narrows_scope`, `primary_source_collision`）、`EVL-20261116-eb85b6`（`ec0c6e`, `narrows_scope`, `primary_source_collision`）、`EVL-20261116-461212`（`874658`, `narrows_scope`, `reproducible_script`）、`EVL-20261116-328195`（`0396ce`, `narrows_scope`, `reproducible_script`）、`EVL-20261116-422ba4`（`7c2a93`, `narrows_scope`, `cross_session_audit`）
- **マップ**: [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) ／ [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)
