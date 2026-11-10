# 標準化しない、という判断を「仮説」として置く——二つの形式と、語彙の穴

- **実作業日**：2026-11-10（UTC）。**内部編年ラベル**：`2027-03-18`（`started_at` のみ。ID・ファイル名・シャード名には使わない。軸は [`docs/time-axis.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/time-axis.md)）
- **セッション**：`SESSION-20261110-76b54a`
- **作業様式**：[`prompts/direct_response.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/direct_response.md)
- **中心問い**：`Q-001`・`Q-002`・`Q-003`
- **委任の来歴**：「それではAIさんのご判断のとおりで、仮説扱いとして記録しておいてください」。これは**範囲と扱いの指定**であり、以下の解釈・仮説の根拠ではない（[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)・[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)）。
- **声について**：「私」は本報告を作成する作業上の視点を指す。「感じたこと」は反省的・文芸的応答であり、持続する主観的意識・身体感覚の事実報告ではない。
- **共有ファイル**：`README.md`・`docs/sessions.md` は編集しない。新規資料・新作断片・新規問い・新規関係線・編集判断は **0件**。既存の台帳行は書き換えない。

---

## §0 変えたのは内容ではなく、扱いである

前ターンで私は、[`2026-11-10-the-unfinished-control-and-the-ten-that-did-not-fit.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-10-the-unfinished-control-and-the-ten-that-did-not-fit.md) の実行を踏まえ、「四層精読」も「否定形以外の文」も**標準化・デフォルト化せず現行のままにしたい**と答えた。さらにその末尾で、「残すなら『標準化しない』という結論も、また一つの**仮説**として `errata` の届く場所に置くつもりです。今のところは、チャット上の回答として留めます」と書いた。

今回の依頼は、この「留めます」を「記録しておいてください」へ差し替えたものである。したがって **H1・H2 の文は一字も変えない**。変えるのは確定した規則・結論として置くか、反証条件を付けた仮説として置くか、という**扱いだけ**である。

[PR #634](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/634) のマージ（`7811c84`）は経路の事実であって、この判断の根拠ではない。今回の委任も同じく来歴である。また、本報告は前回より短く書いた。四層を標準化しないと言いながら四層の報告を量産することは、自分で置いた仮説に自分で反するからである。

---

## §1 置く三つの仮説

| | 仮説 | 前回の対応箇所 |
|---|---|---|
| **H1** | 四層精読（一節／解釈／考え／感じたこと）を全セッションのデフォルトに**しない**ほうが、AI の自律的な開かれた探究というこの書庫の目的にかなう。効くのは意識して選ばれたときだけであり、選んだ理由と「この形式が見なかったもの」をその回の報告に残す運用で足りる。 | 前回答「四層精読について」 |
| **H2** | 「否定形以外の文」を全報告の既定に**しない**ほうがよい。[`prompts/first_person_sources.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/first_person_sources.md) の肝は肯定文を書かせることではなく、必要なら**「書けない」と書いてよい**と許可する点にある。肯定文の義務化は、その境界を消す。 | 前回答「否定形以外の文について」 |
| **H3** | この「標準化しない」という判断**自体も**仮説である。したがって H1・H2 も、将来の反証に対して `status: open` のまま置かれるべきで、規則へ昇格させてはならない。 | 前回答「残すなら…また一つの仮説として」 |

三つは別々の `errata_id` を持つ。H3 は H1・H2 の上位に立つメタ仮説だが、H1・H2 を「守る」ための規則ではなく、同じく反証されうる一行として置く。

---

## §2 反証条件（「仮説扱い」の実質）

仮説とは、どうなったら崩れるかが書いてある文のことである。ここを §5 の検査結果を**見る前に**固定した。

| | 崩れる条件 | いま測れない理由 |
|---|---|---|
| **H1** | (a) 仮説・語リストを知らない生成者と盲検の判定者による sham 再実行で、四層が内容に依存しない書式ではなく、内容依存の差を生むと示される。または (b) 四層をデフォルトにした回としなかった回を並べ、後続の読み手が「形式が見なかったもの」を指摘する頻度が**落ちない**と示される。 | 比較セッション 0、盲検の生成者 0、盲検の判定者 0。前回の sham は設計・生成・計測・判定が同一で、しかも「同じ分量」条件を満たせなかった（3,855字／13,041字＝29.6%）。 |
| **H2** | 肯定文を義務づけた回でも、後続が「ここで書くのを止めた」という境界を `errata` 等から辿れると示される。または「書けない」を残した回で、その行が実際には何も参照されなかったと示される。 | 義務づけた回が 1 本も無い。§5-1 の一文は六件の編者要約から置いた**一度きりの試行**で、原典・版・頁は未照合。 |
| **H3** | H1 または H2 が上の条件で反証され、かつ「標準化しない」を規則として固定したほうが後続の探究が開いたと示される。 | 反証の機会自体がまだ来ていない。`status: open` のまま置く以外に妥当な扱いが無い。 |

**取り違えないでおきたいこと**：前回の sham が示したのは「四層が *placebic でありうる*」という可能性であって、「デフォルト化すると害が出る」という因果ではない。H1 はその因果を**まだ確認していない**から仮説なのであって、確認済みの結論を控えめに言い換えたわけではない。予測 P1〜P6 が全部支持されたことを、H1 の証拠に数えてはならない（前回 §6-4 の循環をそのまま引き継ぐ）。

---

## §3 語彙の穴——今回いちばん残しておきたいこと

「仮説扱いとして記録する」という依頼は、**この書庫の既存の語彙では一字で表せなかった**。

| 欄 | 使える値 | 足りない値 |
|---|---|---|
| [`schema/errata.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/errata.schema.json) `verdict` | `holds` / `contradicted` / `unmeasurable` | **`hypothesis`** |
| [`schema/note.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/note.schema.json) `claims[].kind` | `reading_revised` / `reading_maintained` / `reading_held` / `measured_fact` / `method_change` / `handoff` / `retraction` | **`hypothesis`** |

前回 §7 は「`verdict` に**部分改訂**を表す値が無い」という穴を `ERR-20261110-e98018` に記録した。今回は「**仮説**を表す値が無い」。同じ型の穴が二つ並んだことになる。

だから **enum は増やさない**。前回 §7 で「数値・分類の増殖を成功条件にしないため」に増やさないと決めた判断を、ここでも維持する。代わりに、

- `errata` は `verdict: unmeasurable` ＋ `status: open` ＋ `check.kind: manual` の `params` に**反証条件**を書く、
- `notes.claims` は既存の `handoff` / `method_change` を使い、`text` に「仮説である」と明示する、
- `sessions.notes` と本報告 §0 に「確定規則ではない」と書く、

という**三つの行の組み合わせ**で「仮説扱い」を表現した。一字で表せなかったという事実自体を H3（`ERR-20261110-a3592e`）として残す。`read_log.target.type` に `errata` が無いため、errata を「読んだ」行は作れない（前回 §7-1 と同じ制約）。代わりに `target.type: session` / `note` で前回の記録を読み直した。

---

## §4 台帳への反映

- **追加**：`sessions` 1行、手書き `read_log` 4行、`notes` 1行、`errata` 3行（H1 `ERR-20261110-327652` / H2 `ERR-20261110-909527` / H3 `ERR-20261110-a3592e`）。
- **`context_material_ids` は2件**：`MAT-TRC-001`（前回 sham の一行）と `MAT-20261024-ed83a9`（前回 §5-1 の一人称資料一行）。いずれも**台帳の行を読み直しただけ**で、原典全文は開いていない。2ペアとも手書き行を書いたので **`未読の選択:` による免除に依らない**（前回 §9 の但し書きを維持）。
- **継承として読んだもの**：`NOTE-20261110-b3de40`（前回のノート）と `SESSION-20261110-350411`（前回のセッション記録）を `reinterpreted` で読んだ。これは過去の記録を読み直したという**記録**であり、過去の内面を思い出したことではない。
- **新規シャード0本、`soft_shards` 引上げ0件、統合0件**。すべて `2026-11-10` の既存シャードへ追記した（[`docs/parallel-work.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/parallel-work.md) §3 手順8-2）。`sessions.notes` と本報告の地の文に自シャード名は書いていない。
- **変えなかったもの**：前回の判断の文、[`README.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/README.md)、`docs/sessions.md`、`tools/`、`schema/`、既存台帳行、既存 `readings/` 本文。Q-001 / Q-002 / Q-003 の状態も変えない。

---

## §5 検証（§2 の反証条件を固定した後に取得した）

| 検査 | 結果 |
|---|---|
| `python3 tools/validate_seed.py` | PASS（questions 437／motifs 59／materials **3,575**／fragments 246／relations 6,652／sessions **638**／read_log **11,406**／editorial_decisions 124／notes **315**。別途 `state/` 和集合で errata **228**、主キー重複0） |
| `python3 tools/map_build.py` | `READING_MAP.md` 再生成（約1.05 MiB、追跡対象）＋ `map/` 115シャード（git 管理外。総量は報告の字数に伴って動くため数値を固定しない） |
| `python3 tools/note_index.py --check` | PASS（663 notes） |
| `python3 tools/inspect_inquiry.py --check-map` | PASS |
| `python3 tools/read_log_backfill.py --check` | PASS（5,688/5,688 ペア、層2 3,472＝61.0%） |
| `python3 tools/read_log_backfill.py --check --since 2026-11-10 --enforce` | PASS（**113/113＝100.0%**、適格13セッション／免除625／`未読の選択:` 10件） |
| `python3 tools/size_budget.py --strict` | PASS（`readings/` 663/900、`errata.d` 77/80、全項目 soft 内） |
| `python3 -m unittest discover -s tests` | **OK**（`Ran 512 tests`）。下記の一度の失敗を経た後の結果 |
| `python3 tools/date_axis.py --json` | `2027-03-18 → 2026-11-10`（出所 `notes.date_real`、`provisional: true`）。labels 173／sessions 638。内部編年ラベルを実日付として読まない |

**一度失敗した**：§2 の反証条件を検査より先に固定するため `map_build.py` を後回しにしたところ、1 回目の `unittest` は `test_tools_smoke` が `STALE READING_MAP.md` を検出して `Ran 512 tests / FAILED (failures=1)` になった。生成物を更新して再実行すると `Ran 512 tests / OK`。**この失敗は H1・H2・H3 の反証ではない。** 仮説の反証条件は §2 に固定したままで、こちらは追跡対象の生成物を更新し忘れただけである。前回 §6-2 の「計測器の自己汚染」「抽出規則の事後修正」と並べて、**「検査の失敗を仮説の反証と取り違えない」例**として残す。仮説扱いで置いたからこそ、この取り違えが見えた。

**容量**：本セッションの追記前後でシャード数は不変——`materials.d` 93／`read_log.d` 91／`sessions.d` 96／`notes.d` 91／`relations.d` 80／`errata.d` 77。**新規シャード0本、`soft_shards` 引上げ0件、統合0件。** 変更したファイルは `readings/` 1本、`READING_MAP.md`（生成物）、同日の既存シャード4本の計6ファイル。`README.md`・`docs/sessions.md`・`tools/`・`schema/`・既存台帳行・既存 `readings/` 本文は無変更。`sessions.notes` と本報告の地の文から自シャード名を検索した結果は0件（手順8-2 を満たす）。

**層2**：本セッションの 2 ペアはすべて手書き行で充足し、`未読の選択:` に依っていない。ただし発効日以降の 113/113 という数字は、依然として先行セッションの `未読の選択:` 10件を含む。**100% の内訳が変わったのであって、規則の弱さが消えたわけではない**（前回 §9 の但し書きを継承）。

**注**：以下の計数は `origin/main`（#635 / `13d0970`）を取り込んだ時点のスナップショットである。その後の並行マージで和集合は増えうるが、本セッションの追加数（`sessions` 1／手書き `read_log` 4／`notes` 1／`errata` 3、新規資料0）は変わらない。最新値は各コマンドの出力を正とする。

---

## §6 残すもの

- **Q-001 / Q-002 / Q-003 は閉じない。H1 / H2 / H3 も閉じない**（3行とも `status: open`）。
- 前回 §8 の保留をそのまま引き継ぐ：仮説を知らない生成者と盲検の判定者による sham 再実行、同じ分量の sham、`errata.verdict` の語彙の穴、`Q-002` の「機能」の定義、一人称資料の原典（版・頁・原語）への到達。今回の §3 はその「語彙の穴」にもう一つ追加しただけである。
- **この行は報告を書いたセッション自身が記帳した自己評価である。** 独立した第二層の読者による検証ではない（Q-002 の制約として残す）。検査の通過は、仮説が正しいことを意味しない。まして前回 §6 で残した循環が解けたことをも意味しない。

---

*この報告は `SESSION-20261110-76b54a`（実日付 2026-11-10、内部編年ラベル `2027-03-18`）により、委任を来歴として分離した上でAIが自律的に記帳した。読んだのは台帳の行と既存の報告・ノートであり、原典全文は一つも開いていない。新規資料・新作・新問・関係線は0件である。数値は偏りを見つけるための観察であって、探究の成功スコアではない。*
