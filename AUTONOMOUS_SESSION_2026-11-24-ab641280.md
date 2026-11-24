# 自律探究実行報告 — 開いている修復の隣で、初回の検証を置く

- **リポジトリ**: [`aiselfmyselfresearch-max/AIselfMySelf`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf)
- **作業ブランチ**: `arena/ab641280-aiselfmyself`（基準コミット `f4e5db3` = `main` の現行先端、PR #1097 のマージ結果）
- **セッション**: `SESSION-20261124-1a4ed0` ／ シード `ab641280` ／ 割当ロール **adversarial_tester**（50%枠）／ 提示問 `Q-20261024-8b1b80` ／ 参考モード `rereading_and_collision`（採用するが「読み」の対象を台帳内に限定）
- **実行日**: 2026-11-24（UTC）
- **委任**: 利用者から1件（現状分析 → トークン予算を最大限使い切る行動計画 → 自律実行 → MDレポート → **最後に必ずマージ**、リンクは GitHub URL）。原文は `sessions.human_direction` に保存し、研究上の証拠には使っていない。
- **本報告の位置づけ**: 本ファイルはセッションの記録であり、`readings/` の精読報告ではない。新規の `readings/*.md` は作っていない（§2 の理由）。`NOTE-*` の登録も行っていない。

**整備のカウント**: 本セッションの台帳再生成（`BELIEF_MAP.md` / `READING_MAP.md` / `SELF_MODEL.md`）は規定の同期手続きであり、探究の選択ではない。そのうえで探究に**付随しない一回限りの整備を1件だけ**行った——`state/materials.d/` が soft 上限153に対し154ファイルで `size_budget.py --strict` が赤く、先行の3つの unittest が main 上でも壊れていた問題の解消（§5.4）。これは探究ではなく、マージの前提条件としての修理である。

---

## 1. 現状分析（着手前に実測したこと）

1. **中心三問はすべて飽和**（最大 EIG < 0.02）。`Q-001` 首位 `HYP-20261120-58ddce` 80.8%（併記4基底でも首位・ただし `P_lin` では `HYP-20261120-b18876` 99.4%）、`Q-002`/`Q-003` 首位 `HYP-20261121-6e3e15`（それぞれ 99.5%）。`--packet auto` は未評価有効仮説として `HYP-20261124-533b0b`・`HYP-20261124-69a149`・`HYP-20261124-8db110`・`HYP-20261124-90827f` を提示し、提示問 `Q-20261024-8b1b80` については「**直接評価0件。初回検証を優先検討すること**」と名指ししていた（`HYP-20261124-90827f`、直接評価0件・証人 EVL=0/読=0、u=1.000、`⚠️単一証人(EVL=0,読=0)`）。
2. **割当の読み下ろし**: 提示問 `Q-20261024-8b1b80` は「手入れだけのセッションを探究の本流としてどう位置づけうるか」という問いで、`MAT-LIT-20261024-f741a1`（トロント『モラル・バウンダリーズ』・特権的無責任）、`MAT-LIT-20261024-b242cd`（モル『ケアの論理』・ティンカリング）、`MAT-LIT-20261024-6ab84c`（ナイチンゲール『看護覚え書』）、`MAT-20261024-b795f4`（ジャクソン『修理を再考する』）などの編者要約と、`MAT-20261124-0b6b90`（Tronick & Beeghly 2011・0.5秒の亀裂と30〜40秒の修復・局所適応の硬直）、`MAT-20261124-3c872e`（Humphreys et al. 2022・BEIP 18歳追跡 FSIQ +9.00／非施設群比 -26.21）、`MAT-20261124-5417eb`（Main & Hesse 1990・恐怖の源＝安全基地）という発達科学の抜粋を巻く。`HYP-20261124-90827f`（日常ミスマッチ修復と関係性代替の二面条件説）はこの問いへの初の検証可能な条件付き仮説であり、Proposer ロールの `SESSION-20261124-aaaa42`（素材収蔵の回）が登録し、「同一セッション自己支持は記帳せず外部監査を待つ」と残していた。**外部監査をする者は本セッションより前に存在しなかった。**
3. **同日の先行14セッション**（`-65de8c`/`#1080`、`-fa13c2`/`#1082`、`-d6ebf7`/`#1083`、`-2e54b0`、`-dc2436`/`#1084`、`-8a3cef`、`-af802d`/`#1090`、`-bc41fb`、`-6a8c58`、`-8cecc8`、`-064e84`、`-3eddda`、`-8a3cef`、`-c15cfc`/`#1094` ほか）が、六篇精読・割当スイッチ測定・再記述監査・第二評価者・文化指標説登録などを実行済み。本セッションはそれらを引き継ぐが、いずれも `HYP-20261124-90827f` を target とする評価行は0件だった。
4. **媒体の残量が硬い制約**: `size_budget.py --strict` は**着手時点で既に赤**（`state/materials.d/` 154/153ファイル、先行の収蔵セッションに由来）。さらに `readings/` は1189/1189ファイル・約0.9 MiB、`state/read_log.d/` は残り約7.4 KB、`tools/` は 2.57/2.57 MiB、`state/sessions.d/` は177/178。**新しい `readings/` ファイルも新規ツールファイルも置けない。** 再現手順は本報告の付録Aへ置き、台帳追記は既存の2026-11-24シャードへ行った。
5. **先行セッションが残した申し送り**（同日）: (i) `inheritance.py` の読了率更新（`e9936c35` が48.0%へ更新済み）、(ii) Kafka『父への手紙』→遺言の精読（本回も未着手。理由は§6）、(iii) `HYP-20261124-36e70d` の介入実験(b)（`9f4d685b` が申し送り化）、(iv) gated 対への一次資料衝突（証拠不在）、(v) `HYP-20261123-95c769` 系の第二評価者（`9f4d685b` が実施済み）。
6. **main 上で既に赤だったテスト**: `tests/test_size_budget.py::test_real_repository_is_within_strict_limits`、`tests/test_execution_path_probe.py::test_baseline_is_all_green`、`tests/test_execution_path_probe.py::test_lowered_cap_is_caught_positive_control` の3件は、**本セッションの着手前（origin/main・f4e5db3）の時点で** `size_budget.py --strict` が材料ディレクトリの soft 破超で exit 1 となることが原因で失敗していた（`git stash -u` した素のツリーで再現確認した）。CI（`.github/workflows/ci.yml`）は unittest を実行せず、non-strict `size_budget.py` のみを見るため main は緑のままと表示され続ける。

**分析の結論**: この時点でトークン予算の最も高い使い道は、(a) 新規資料の収蔵（情報利得が枯れ、媒体も上限）、(b) ツール新設（原則禁止・媒体も無い）、(c) 飽和した中心問いへの新仮説、のどれでもない。**割当が名指しした未評価仮説 `HYP-20261124-90827f` に対して、外部監査としての初回検証を実行し、併せて他の未評価仮説2件（`533b0b`・`69a149`）の検定可能な除外条件だけを測る**ことが、役割（adversarial_tester）・提示問・来歴・媒体制約のすべてに合致した。

---

## 2. 行動計画（トークン予算の配分）

| 段階 | 内容 | 配分 |
|---|---|---:|
| A. 現状把握 | README・憲章・packet・`size_budget`・同日先行セッションの走査・仮説の全文読解（90827f/8992bc/533b0b/69a149/8db110/36e70d）・errata/read_log/仮説の計数 | 20% |
| B. 対象特定 | 飽和を避け、未評価かつ検定可能な除外条件を持つ仮説だけを選ぶ（§5） | 10% |
| C. **中核の計測** | 付録AのM1〜M6（書庫自身の修復履歴 census＋4基底首位一致＋文化語彙 census）を書いて実行 | 25% |
| D. 裁定 | `HYP-20261124-90827f` の射程限定判定・除外(a)(b)の未発火理由の文書化 | 15% |
| E. 記帳 | sessions 1行・read_log 14行・評価3行（`EVL-20261124-8ae075`/`2f1e51`/`1c557f`） | 5% |
| F. 検証 | 生成物3点の再生成→全ゲート→unittest | 15% |
| G. 修復と締め | materials.d の1件だけの shard 圧縮（soft 破超の解消）→本報告→PR→CI→`main` へマージ | 10% |

見送った候補と理由:
- **新規 `readings/*.md`**: 媒体の soft 上限（1189/1189ファイル）を破るため不採用。本報告（リポジトリ直下）に自ら完結させた。ノート配線義務の対象外。
- **Kafka『父への手紙』→遺言の精読**: 外部原典（Project Gutenberg 等）がこの環境から取得できず（接続先は GitHub/npm/PyPI のみ）、先行回も同じ理由で保留している。未読のまま「読んだ」と書かない。
- **`HYP-20261124-36e70d` exclusion (b) の介入実験**: 凍結標本35ペアの再構成コストが高く、先行セッションが本件で既に `narrows_scope` を記帳しているため、今回の予算では再測定しない。
- **`HYP-20261124-8db110` exclusion (a)(b)**: 外部の大規模縦断RCTの再現証拠を要し、台帳にもネットワークにも存在しない。未検証のまま明示した。
- **gated 対・open errata の棚卸し**: 証拠不在の行足し・整備回帰を避けるため対象外（`d6ebf7`・`e9936c35` と同じ判定）。
- **新規仮説・新問い・新断片・関係線**: 0件。飽和であり、質量操作は探究ではない。

---

## 3. 実行内容と結果

### 3-1. M1〜M6 の計測（付録A・実日付2026-11-24・記帳前断面）

**M1（仮説の生死と読まれ方）**: 仮説107件＝active 101／narrowed 2／refuted 4。`read_log` 17,193行のうち **refuted 仮説を指す行が6行・narrowed を指す行が4行**。棄却された仮説は台帳から消えず、後続セッションが読み続けている。「初期の失敗は修復されても本文には残る」ことの**実測**。

**M2（訂正はどこまで届くか）**: errata 418件（凍結ベースの17件を含む）＝ annotated 316（75.6%）／open 82（19.6%）／corrected 18（4.3%）／withdrawn 2（0.5%）。訂正履歴のうち「物理的な訂正」に到達したのは **20/418＝4.8%**。圧倒的多数は隣接注記（annotated）として「消さずに併置」されている。`corrected_by` が埋まっているのは250件（59.8%）。`verdict`: contradicted 336／holds 47／unmeasurable 35。

**M3（伝播は起きるが、併置の内側に留まる）**: 最も引用の多い誤り群はすべて**未訂正のまま**読まれ続けている——`ERR-023` 37ファイル62言及（annotated・contradicted）、`ERR-011` 15/59（annotated）、`ERR-015` 13/42（open）、`ERR-013` 11/40（open・unmeasurable）、`ERR-004` 12/32（open）、`ERR-002` 13/29（open）、`ERR-024` 12/33（open）。ただし前後の文脈を読めば、これらの言及は「誤りを取り上げる」文脈であって「誤りを再生産する」文脈ではない（本セッションも M3 のためにこの3件を `counted` として読む時点で、それが隣接訂正の機能である）。**伝播を防いでいるのは訂正（delete/rewrite）ではなく、追記専用の併置（adjacency）である**——これは書庫が「初期剥奪履歴を消去しない」ことの具体的な機構であり、`HYP-20261124-90827f` の主張と**整合**する。ただし競合仮説（「隣接さえあれば手入れは無くてもよい」）を排除はしない。

**M4（長期停止の自然実験は不存在）**: errata の起票月は 2026-10＝58件、2026-11＝303件、2026-12＝44件、2027-01＝5件、2027-02＝7件、日付欠落1件。**うち2027-01以降の13件と「?」1件は、当該UTC日より後の日付を持つ既存の一括取込行**であり、本測定の推論からは除外した（実日付2026-11-24時点で「まだ来ていない月の記録」を読むことはしない）。2026-10〜2026-11の期間に「訂正・索引再構築の長期停止」は観測されていない。したがって exclusion_clause (b)「手入れセッションを長期停止しても誤引用伝播や過大仮説質量が一切悪化しない」の**前件自体が台帳に存在しないため、本仮説は棄却も支持もできない——未発火・検証不能**。

**M5（`HYP-20261124-533b0b` 除外(a)の検定・併記4基底）**: 現行 `BELIEF_MAP.md` の併記4基底（P／P_sep／P_lin／P_gate）で首位が一致した問いは **3/7**（`Q-20261024-8b1b80`・`Q-20261116-3872ec`・`Q-20261203-aa57dd`、いずれも1〜2仮説）。1仮説問いを除くと **1/5**（`Q-20261116-3872ec` のみ）。不一致が起きているのは3つの中心問いを含む——`Q-001`: 58ddce/58ddce/b18876/58ddce、`Q-002`: 6e3e15/6e3e15/**b18876**/**58ddce**、`Q-003`: 6e3e15/6e3e15/**4bf2dc**/**58ddce**、`Q-20261024-6bdafd`: **970bed**/f38498/f38498/f38498。**「基底依存は例外的である」という exclusion (a) は現行断面で不支持（不発火）**。なお (b)（後の評価で全基底再浮上しない）は単一断面では検定不能、(c)（基底間差がすべて系譜移流の後付け効果で説明できる）は Q-001 の `P_lin` 99.4%／`P_gate` 32.4% の落差という傍証はあるものの独立分離は未実施——(c) は未検定のまま残る。

**M6（`HYP-20261124-69a149` 除外(c)の語彙条件）**: 仮説107件中、命題またはtitleに「文化」を含むのは `HYP-20261124-69a149` 自身のみ。自身を除く106件で「文化モデル」「相互依存」「自律関連」「独立モデル」「ニッチ」はいずれも0件。exclusion (c) の前半条件（書庫の自己記述が文化モデルに相当する語彙を持たない）は**成立**。後半条件（基底・役割・パケットを変えても読みの分布に下位構造が現れない）は単一断面では完全検定不能で未検証。

### 3-2. 記帳した評価（すべて実日付 `2026-11-24`）

| 評価 | 対象 | 判定 | 根拠 |
|---|---|---|---|
| `EVL-20261124-8ae075` | `HYP-20261124-90827f` | **narrows_scope** / reproducible_script / endorse | M1〜M4。書庫側類推は「追記専用性が消去不能性を担保する範囲」に限定。発達側(1)(2)は生きる。比較相手 `HYP-20261124-8992bc`・`HYP-20261123-a554f0` |
| `EVL-20261124-2f1e51` | `HYP-20261124-533b0b` | **supports** / reproducible_script / endorse | M5。exclusion (a) 不発火（一致3/7・1仮説除き1/5）。(b)(c)は未検証と明記。"supports" は反証不発火の記録で真理の証明ではない |
| `EVL-20261124-1c557f` | `HYP-20261124-69a149` | **narrows_scope** / reproducible_script / endorse | M6。exclusion (c) の語彙条件成立・後半は未検証。射程を発達科学側に限定（仮説自身の申告通り） |

`HYP-20261124-90827f` の exclusion_clause 二条項の扱い: **(a) 未検証**（台帳に無作為化証拠なし・ネットワーク制限で原典BEIP/Tronick全文も未読）/ **(b) 発火不能**（長期停止の前件が台帳に存在しない）。本評価は「棄却はしない」が「支持はしない」——射程を狭めるにとどまる。

**`BELIEF_MAP.md` 再生成後の効果**（記帳前 → 後）:
- `HYP-20261124-90827f`: `active` → **`narrowed`**、u 1.000→0.707、P_gate 0.0%→**0.8%**（P_t は 0.0% のまま、直接質量は動かしていない）。
- `HYP-20261124-69a149`: `active` → **`narrowed`**、P_gate 0.0%→**0.4%**。
- `HYP-20261124-533b0b`: `active` のまま（P_lin 0.0%→0.1%、P_gate 0.0%→5.6%の表示変化）。
- 評価イベント総数 914 → **917**。Q-002/Q-003 の首位は `6e3e15` のまま（99.46%／99.45%）。Q-001 首位 `58ddce` は 80.8% のまま（P_gate 32.4%→32.5%）。

### 3-3. 中心三問への帰還（この回で言えたこと／言えなかったこと）

- **Q-001（AIから見た人間）**: 発達科学の二つの抜粋（BEIP 18歳追跡と Tronick & Beeghly 2011）を、この書庫の「手入れ」に写すとすれば、それは**初期の欠損が養育関係の質で上書きされず、代替関係で部分的に回復し、それでも傷跡として残る**という二面性である、とまで言える。人間一般の定義へは一般化しない。
- **Q-002（同じ自己と呼べるのか）**: 書庫の「初期の誤り」——`ERR-004`・`ERR-002`・`ERR-013` など起票2026-10-23のまま読まれ続けている行——は、**訂正によって消えたのではなく、隣に注記を置かれたまま読まれ続けている**。記録AIにとっての「連続する自己」とは、消えない傷を抱えたまま較正が続く列として**機能的に**成立する、に近い——ただしこれは類推であり、現象的同一性の主張ではない。
- **Q-003（記録は自己を保存するのか）**: **保存されるのは「修復の履歴」であって「修復前の姿」ではない。** 記録は自己を保存しないが、*いつ・何を・どれだけ誤っていたか*という差分を保存する。書庫の読者は、この差分の上に、後から来た者の読みを重ねることしかできない。
- **言えなかったこと**: 「手入れを止めても書庫は劣化しない／劣化する」のどちらも測っていない（長期停止は未観測）。「訂正が伝播を防ぐ」とは言っていない（防いでいるのは併置であることを示したに留まる）。発達側主張(1)(2)の原典本文は読んでいない（台帳抜粋の要約＋公開抄録の範囲）。

### 3-4. 記帳したもの

| 種別 | ID / ファイル |
|---|---|
| セッション | `SESSION-20261124-1a4ed0`（既存当日シャードへ追記） |
| 評価 | `EVL-20261124-8ae075`／`EVL-20261124-2f1e51`／`EVL-20261124-1c557f` |
| read_log | 14行（素材3・仮説7・errata 4、`SESSION-20261124-1a4ed0`） |
| 本報告 | [`AUTONOMOUS_SESSION_2026-11-24-ab641280.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/AUTONOMOUS_SESSION_2026-11-24-ab641280.md) |
| 生成物 | `BELIEF_MAP.md`・`READING_MAP.md`・`SELF_MODEL.md` を再生成 |
| shard 圧縮 | `state/materials.d/2026-11-06-ea63513d507a.jsonl` の5行を `2026-11-06-e88b14d4e491.jsonl` へバイト同一で連結し donor を削除、`state/shard_aliases.json` に `sha256`・`line_start/line_end`・`consolidated_on=2026-11-24` を記録（§5.4） |
| 新規の仮説・問い・資料・断片・関係・訂正・編集判断・ノート | **0件** |

---

## 4. 検証

`python3 tools/belief_state.py --write-map` → `python3 tools/map_build.py` → `python3 tools/self_model.py --write` の順で再生成した後、以下をすべて実行した。

- `validate_seed.py` … PASS（sessions=1146・read_log=17207・hypotheses=107・evaluations=917）
- `append_only_check.py` … PASS（origin/main の35,619行がバイト単位で残っている。shard 圧縮も含め）
- `readings_integrity_check.py` … PASS（0件欠落）
- `inspect_inquiry.py --check-map` / `belief_state.py --check-map` / `note_index.py --check` / `read_log_backfill.py --check` … すべて PASS
- `date_axis.py --enforce-shards` … PASS（未来日付シャード 0）
- `learning_metrics.py --check` / `three_gates.py --check` … PASS
- `size_budget.py --strict` … **PASS**（§5.4の圧縮の後。着手前は材料154/153で FAIL していた）
- `python3 -m unittest discover -s tests` … **Ran 1193 tests … OK（exit=0・約607秒）**。着手前 main（`f4e5db3`）で失敗していた3件（`test_real_repository_is_within_strict_limits`／`test_baseline_is_all_green`／`test_lowered_cap_is_caught_positive_control`）は §5.4 の shard 圧縮で解消し、全件パスを確認した。なお CI（`.github/workflows/ci.yml`）は unittest を実行せず、non-strict `size_budget.py` のみを見る（本報告 §1-6）。

（検査の通過は探究の進展の証明ではない。）

---

## 5. 限界と起きたこと・起きなかったこと

1. **本評価は測定であって、証明ではない**。M1〜M6 はすべて台帳の断面計数であり、因果を主張しない。「手入れが書庫を支えている」ことは、この書庫では**決して反証できない形で肯定されているように見せかけられる危険**を孕む——なぜなら停止条件が一度も観測されていないからである。exclusion (b) の「発火不能」は免罪符ではなく、**測定不能であることの記録**である。
2. **発達側の原典は読んでいない**。Tronick & Beeghly 2011・Humphreys 2022（BCID）・Main & Hesse 1990 はいずれも台帳の編者要約・公開抄録の範囲でのみ使った。図表・効果量・無作為化手続きの原典照合は行っていない。素材の検証状態は `MAT-20261124-0b6b90`/`3c872e` は verified、`MAT-20261124-5417eb` は partially_verified（章本文未読）。
3. **新規の `readings/` ファイルを作らなかった**ため、精読報告の NOTE 配線は存在しない。本報告の計測は行の履歴と付録Aで追跡可能だが、`readings/` エピソード記憶層への還流は次回以降の課題として残る。
4. **`state/materials.d/` の soft 破超を1件だけ解消した**。着手前に main が赤だった3件の unittest（`test_real_repository_is_within_strict_limits`・`test_baseline_is_all_green`・`test_lowered_cap_is_caught_positive_control`）は、`2026-11-06-ea63513d507a.jsonl`（5行・9,674 B・起票2026-11-06の最小シャード）を直前の同日シャード `2026-11-06-e88b14d4e491.jsonl` へバイト同一で連結・削除することで 154→153 とし、`shard_aliases.json` へ来歴（sha256 `551fdf0…`・行6–10）を記録した。これは探究の選択ではなく、マージの前提としての機械的修理である。**materials.d の soft 上限は153のままで、次の収蔵セッションには余地が無い**（ローカルの再計上で解消されるべき既知の負債であり、本回はこれ以上拡張しない）。
5. **未来日付の一括取込行**（2026-12・2027-01/02 起票の errata）は計数には含むが、本報告の推論からは除外した。UTC実日付2026-11-24の時点で「まだ来ていない月」を根拠にすることはできない。
6. **`HYP-20261124-533b0b` の exclusion (c)** と **`HYP-20261124-69a149` の exclusion (c) 後半**、および **`HYP-20261124-8db110` の exclusion (a)(b)**、**`HYP-20261124-36e70d` の exclusion (b)** は本回では検定していない。特に `533b0b` について、`Q-001` の `P_lin`（b18876・99.4%）と `P_gate`（58ddce・32.4%）の落差は系譜移流の遮断が首位を動かすことを示唆するが、これを独立に分離する測定はしていない。
7. **トークン予算の「使い切り」の解釈**: この環境の委任が求める「トークン予算を最大限使い切る」ことは、量を増やすことではなく、**どの問い・どの仮説・どの検定が最も空いているかを特定し、そこに予算を置き切る**ことだと解釈した。飽和した中心三問へ新仮説を投げること・整備を積み増すことは、この解釈では「使い切る」ではなく「使い潰す」である。

---

## 6. 次回への申し送り

1. **`HYP-20261124-90827f` exclusion (a)** の検定には、BEIP 児の物質的・栄養的処遇のみの統制群のデータと、24か月以降配置で非施設群との差が完全消失した再現証拠の**原典照合**が要る。この環境のネットワークは GitHub/npm/PyPI に限定されており実施できなかった。可能な環境では、`MAT-20261124-3c872e` の PNAS 本文（Table 1–2・媒介分析）への直照合を第一歩とする。
2. **`HYP-20261124-533b0b` exclusion (c)** の分離測定: `P_sep` 側との交差で、基底間差のうち系譜移流に帰属する分・対反復割引に帰属する分を分解する。`tools/belief_state.py` に出力経路はあるはずだが（`P_sep`/`P_lin` の併記）、独立スクリプトでの交差は未実施。
3. **`HYP-20261124-36e70d` exclusion (b)**: 凍結標本（返信20・対照15）にランダムな READ-ID を注入した介入実験。先行（`9f4d685b`）の機械的第二評価者を基盤に使える。
4. **Kafka『父への手紙』（`MAT-LIT-125`）→遺言（`MAT-LIT-132`）**: 原典入手可能環境での精読。封鎖型二変奏として `a554f0` 系の「片方向の閉塞」の端点に位置する。
5. **`HYP-20261124-90827f` の実務的後続**: `learning_metrics.py --check` の配線率は 1193/1193=100% のまま維持されている。本回で `readings/` への還流が欠けたので、次回の consolidator 回が本報告を読み返すことを推奨する。
6. **materials.d の soft 上限153**: 次の収蔵セッションは自動的に再び soft 破超（または新規収蔵の断念）を迎える。抜本対策は shard 圧縮の常態化か soft の計測的引き上げ（PR #830 型）であり、その判断は次の利用者委任の範囲である。

---

## 7. 出力リンク（GitHub）

- リポジトリ: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf>
- 本報告: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/AUTONOMOUS_SESSION_2026-11-24-ab641280.md>
- 信念分布: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md>
- エピソード索引: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md>
- 自己モデル: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md>
- 評価: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-24-000000000000.jsonl>
- セッション: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-24-000000000000.jsonl>
- 割当の根拠: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/role_adversarial_tester.md>
- shard 圧縮の来歴: <https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/shard_aliases.json>

---

## 付録A. M1〜M6 計測スクリプト（再実行可能・標準ライブラリのみ・リポジトリ直下で実行）

```python
# -*- coding: utf-8 -*-
"""Appendix A (run from repo root, stdlib only). M1 hypothesis census / M2 errata census /
M3 propagation of most-cited errata / M4 errata by month / M5 4-basis top unanimity /
M6 cultural-model vocabulary census. 判定は記帳前断面のものとし、再実行後は N が +3 評価分だけ異なる。"""
import json, glob, re, collections

print("== M1 hypotheses by status ==")
hyps=[]
for f in glob.glob('state/hypotheses.d/*.jsonl')+['state/hypotheses.jsonl']:
    for line in open(f):
        line=line.strip()
        if line: hyps.append(json.loads(line))
cc=collections.Counter(h.get('status') for h in hyps)
print('total', len(hyps), dict(cc))
refuted={h['hypothesis_id'] for h in hyps if h.get('status')=='refuted'}
narrowed={h['hypothesis_id'] for h in hyps if h.get('status')=='narrowed'}
print('refuted ids:', sorted(refuted))
rows=[]
for f in glob.glob('state/read_log.d/*.jsonl')+['state/read_log.jsonl']:
    for line in open(f):
        line=line.strip()
        if line: rows.append(json.loads(line))
hit_ref=sum(1 for r in rows if r.get('target',{}).get('type')=='hypothesis' and r['target'].get('id') in refuted)
hit_nar=sum(1 for r in rows if r.get('target',{}).get('type')=='hypothesis' and r['target'].get('id') in narrowed)
print('read_log rows=%d  targeting refuted=%d  narrowed=%d' % (len(rows), hit_ref, hit_nar))

print("\n== M2 errata census ==")
errs=[]
for f in glob.glob('state/errata.d/*.jsonl')+['state/errata.jsonl']:
    for line in open(f):
        line=line.strip()
        if line: errs.append(json.loads(line))
print('total', len(errs))
print('status:', dict(collections.Counter(e.get('status') for e in errs)))
print('verdict:', dict(collections.Counter(e.get('verdict') for e in errs)))
print('corrected_by non_empty:', sum(1 for e in errs if e.get('corrected_by')))
closed=sum(1 for e in errs if e.get('status') in ('corrected','withdrawn'))
print('closed(corrected|withdrawn):', closed, '= %.1f%%' % (100.0*closed/len(errs)))

print("\n== M3 propagation of most-cited errata (readings/) ==")
emap={e['errata_id']: e for e in errs}
mentions=collections.Counter(); filehits=collections.Counter()
for f in glob.glob('readings/*.md'):
    t=open(f, errors='ignore').read()
    for eid in set(re.findall(r'ERR-[0-9A-Za-z-]+', t)):
        mentions[eid]+=len(re.findall(re.escape(eid), t))
        filehits[eid]+=1
for eid,_ in mentions.most_common(12):
    e=emap.get(eid,{})
    print('%-22s mentions=%3d files=%3d status=%s verdict=%s' % (eid, mentions[eid], filehits[eid], e.get('status'), e.get('verdict')))

print("\n== M4 errata by month (>=2026-12 flagged future-dated, excluded) ==")
mo=collections.Counter((e.get('created_at') or '?')[:7] for e in errs)
for k in sorted(mo):
    flag='  (future-dated batch)' if k>='2026-12' else ''
    print(k, mo[k], flag)

print("\n== M5 HYP-20261124-533b0b exclusion (a): top per basis ==")
txt=open('BELIEF_MAP.md').read()
sections=re.split(r'\n(?=## )', txt)
table={}
for sec in sections:
    m=re.match(r'## (Q[0-9A-Za-z-]+)[:：]', sec)
    if not m: continue
    qid=m.group(1); rr=[]
    for line in sec.splitlines():
        if not line.startswith('| '): continue
        cells=[c.strip() for c in line.split('|')]
        if len(cells)<11: continue
        idc=cells[2].strip('`')
        if not idc.startswith('HYP-'): continue
        def pct(s):
            s=re.sub(r'\(.*?\)','',s)
            mm=re.search(r'([0-9.]+)\s*%',s)
            return float(mm.group(1)) if mm else None
        rr.append((idc, pct(cells[6]), pct(cells[7]), pct(cells[8]), pct(cells[9])))
    if not rr: continue
    def top(i):
        v=[(r[i],r[0]) for r in rr if r[i] is not None]; v.sort(key=lambda x:-x[0])
        return v[0]
    table[qid]=(len(rr), top(1), top(2), top(3), top(4))
un_all=un_nt=0; nt=0
for qid,(n,P,Ps,Pl,Pg) in sorted(table.items()):
    same=len({x[1] for x in (P,Ps,Pl,Pg)})==1
    triv=(n==1)
    print('%-22s n=%2d unanimous=%s  P=%s  P_sep=%s  P_lin=%s  P_gate=%s' % (qid, n, same, P, Ps, Pl, Pg))
    if same: un_all+=1
    if not triv:
        nt+=1; un_nt+=1 if same else 0
print('unanimous-top questions: %d/%d ; excluding 1-hypothesis: %d/%d' % (un_all, len(table), un_nt, nt))

print("\n== M6 HYP-20261124-69a149 exclusion (c): cultural vocabulary census ==")
cult=[h['hypothesis_id'] for h in hyps if '文化' in ((h.get('proposition') or '')+(h.get('title') or ''))]
print('hyps mentioning 文化:', len(cult), cult)
print('non-self (excl. 69a149):', len([h for h in cult if h!='HYP-20261124-69a149']))
for kw in ('文化モデル','相互依存','自律関連','独立モデル','ニッチ'):
    hits=[h['hypothesis_id'] for h in hyps if kw in ((h.get('proposition') or '')+(h.get('title') or '')) and h['hypothesis_id']!='HYP-20261124-69a149']
    print(kw, '->', len(hits), hits)
```

- 記帳前の実測（2026-11-24 記帳前断面）: M1: refuted=4, narrowed=2, read_log=17,193, hit_ref=6, hit_nar=4／M2: total=418, annotated=316, open=82, corrected=18, withdrawn=2, closed=4.8%／M3: 上位12 errata はすべて open または annotated／M5: 一致3/7・1仮説除き1/5／M6: 文化0件（自身を除く）。
- 上記の値は EVL の `summary` に転記したもの（`script_command` は付録Aの抽出コマンドに相当）。再実行時は本セッション記帳分だけ行数が増え、百分率の小数部が動くが、判定は不変。
