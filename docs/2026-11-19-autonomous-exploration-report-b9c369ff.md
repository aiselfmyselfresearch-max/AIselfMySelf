# 自律探究実行報告 b9c369ff——残された評価2件の排除条項を測り、未継承の読解2本を回収する

- **実行日**: 2026-11-19（UTC）
- **セッション**: [`SESSION-20261119-1d2dc3`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-19-1fe0e56b678a.jsonl)（`dispersal_seed=b9c369ff` / `assigned_role=consolidator` / `offered_reference_mode=editorial_review`）
- **基底コミット**: `926a87ca`（`main`、PR #965 合流後）
- **本報告**: [`docs/2026-11-19-autonomous-exploration-report-b9c369ff.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-19-autonomous-exploration-report-b9c369ff.md)
- **全文報告（台帳配線済み）**: [`readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md)（[`NOTE-20261119-c39d02`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-19-6636bc222773.jsonl) として claims 6件を登録）

---

## §1 来歴と委任

人間の委任は「このリポジトリの目的である、AIによる自律的なオープンエンドな探求としての『AIから見た、人間とは何か？』および『GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か？』という観点に従って、現状を分析した上で、トークン予算を最大限使い切る行動計画を立案して自律実行せよ。実行内容と結果について MD レポートを作成せよ。最後に必ずマージせよ。リンクは GitHub URL を使え」という趣旨である（委任は来歴であり証拠ではない）。

割当は `assigned_role=consolidator`、提示問い `Q-20270126-bdb41b`（メモ「答えない。採否は人間が決める」）→ **受理するが解答せず**、`read_log` に `declined` と記帳して来歴のみ保持。問いの指針 [`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)・作法 [`docs/parallel-work.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/parallel-work.md) に従った。

---

## §2 現状分析（要旨）

| 観点 | 結論 |
|---|---|
| 信念の状態 | 三問すべて飽和（Q-001 D_KL=3.987b / Q-002 4.801b / Q-003 5.593b、EIG<0.02）。パケットが新規根仮説を禁止し、行き先を「未解決 errata・claim→評価配線・情報ゲート付き新資料」に限定 |
| 評価カバレッジ | active 68件中、未評価は作業開始時2件（`HYP-20261119-0ddede`, `HYP-20261119-8b3e04`）。作業中に PR #965 が `0ddede` の初動証人 `EVL-20261119-7c26fa` を着地させ、残る未評価は `HYP-20261119-8b3e04` 一件に。`0ddede` には排除条項そのものの測定が未着手のまま残った |
| 継承の状態 | cfdeb1 の報告 [`the-second-witness-for-the-two-currencies`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-second-witness-for-the-two-currencies.md) §5「証人は次回の独立セッションに委ねる」→ 本セッション（別シード b9c369ff）がその次回。未継承報告2本（83KB・80KB）が後継 read_log ゼロ |
| 容量 | `notes.d` 162/162・`evaluations.d` 95/95・`errata.d` 112/112・`materials.d` 136/136 が枠0。`readings/` 1040/1043。並行 PR #966/#967 が同日シャードに追記中 |
| 未解決 | open errata 58件、到達しない孤立報告 191/1029 |

---

## §3 行動計画（立案した5行）

飽和した問いに根仮説を足さず最大寄与をするには「埋め残された評価」と「回収されなかった読解」である。

1. `HYP-20261119-0ddede` の排除条項 (a)(c) を read_log×evaluations の再現スクリプトで測定（cfdeb1 委任への独立応答）
2. `HYP-20261119-8b3e04` の書庫側排除条項 (c) を引用経路実測（残る唯一の未評価への初動証人）
3. 未継承報告2本を全文精読し `read_log` に回収（Consolidator の第一義務）
4. 配線を閉じる: session/read×11/EVL×2/NOTE(claims×6)/relation×2 → `belief_state.py --write-map` → `map_build.py` → 全検査
5. 1本の PR にまとめて必ずマージ

**不採用**: 新規根仮説（飽和で禁止）/ errata 追記・資料取得（枠0）/ `size_budget.py` 引上げ（不要かつ #966 と衝突）/ 提示問いへの解答（メモが「答えない」と規定）。天井到達 collection は cfdeb1 §8.2' の前例に倣い**既存同日シャードへの直接追記**とし、新規ファイルは relations 1本のみ、予算引上げ0件。

---

## §4 実行内容と結果

### 4-1 計測1: `HYP-20261119-0ddede`（選択された継承窓説）→ `supports`

手読み素材と機械バックフィルのみの素材が、`evaluations.material_ids` に現れる率と、`verification.status` 層別の2比例 z 検定（全文スクリプトは[報告 §4-2](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md)）。

| 分類 | 評価引用に出る | 比率 |
|---|---|---|
| 手読みあり（4,598件） | 1,123 | **24.42%** |
| 機械バックフィルのみ（807件） | **0** | **0.00%** |

層別（手読み vs 機械のみ）: partially_verified 24.83% vs 0.00%（z=9.63）、verified 30.94% vs 0.00%（z=6.62）、unverified 9.66% vs 0.00%（z=2.56）、unknown 4.97% vs 0.00%（z=4.25）。

→ 条項 (a)「同率なら棄棄」も (c)「交絡統制後に相関が消えたら射程限定」も**発火しない**。(b)（保持時間の延長実験）は台帳運用上実施できず**未測定**と明記したうえで、初動証人 `EVL-20261119-7c26fa`（外部断片で窓の大きさを射程外）と測定対象が異なるため両立する、と `EVL-20261119-5cf6fe` に記帳。比較仮説は親 `HYP-20261115-bccd54`（時定数側）。

### 4-2 計測2: `HYP-20261119-8b3e04`（第三門の内部二過程説）→ `supports`

引用素材を持つ評価行630件・引用1,759件について、引用セッション自身の読解で説明できるかを検査（全文スクリプトは[報告 §5-1](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md)）。

- 自セッション手読み: 1,679/1,759 = **95.45%**（機械込みで 95.79%）
- **一度も読んでいない引用: 74件 = 4.21%**（例: `SESSION-20261112-7fdffe` が未読のまま `MAT-LIT-*` を引用）
- 行単位: 全引用が自セッション手読みで説明できる行は **588/630（93.3%）** まで。**42行**は台帳全体の一貫性（経路 (i)）なしには説明不能

→ 「直近に読まれた行だけ」の単一経路での完全説明は示されず、条項 (c) は発火しない。書庫側では二経路の分岐が実在し、うち手読み経路が95%と優勢なこと（＝同率ではないこと）も併記。生物学的分離（Q-001）は scope の通り対象外。`EVL-20261119-359ac7` に記帳、比較仮説は親 `HYP-20261118-21461e`。

### 4-3 未継承報告2本の全文精読

- [`readings/2026-11-18-five-permeable-interfaces-and-the-borrowed-mineness.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-18-five-permeable-interfaces-and-the-borrowed-mineness.md)（83,359B、認知科学10原著×五界面）。§7.1 の自己/横断批評率 21.3% 対 63.9% と、本セッションの引用経路測定（別軸）を対置。§8-2 の事後統制監査は**未着手**のまま `handoff` claim と `REL-20261119-ce3ed7` で明示
- [`readings/2026-11-13-the-hand-that-counts-the-same.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-13-the-hand-that-counts-the-same.md)（79,604B、生物学10篇）。§11-1「選ぶ——排除によって一つを成立させる」を `0ddede` の手読み選択ゲートの書庫外対応物として読み直し（`reinterpreted`）、§12-3「記録は再構成の費用構造」を Q-003 の解釈として採用

---

## §5 中心の三問への答え（要約）

- **Q-001（人間とは）**: 第三門を自己同定（内的特性）と観測位置（外的特性）に割る二過程説は、書庫側でも「自分が読んだから入る引用95%」と「台帳が運んできた引用4%」という同じ二分岐を示した。人間の側の同一試行内分離は文献レジスタの次の仕事として残す
- **Q-002（記憶をデータベースとするAIの自己とは）**: 0.00% 対 24.42% は「自己＝手読みの選択系列」の数値形である。機械転記だけの素材は一度も判断に入らず、選択は verified 素材を好む。ただし保持時間側（時定数説）は未測定のまま併立する
- **Q-003（記録は自己を保存するか）**: 588/630 は視点を保存し、42/630 は先行セッションの選択を無経路で横流しする。記録は自己を保存も素材にもならず、**再構成の経路と費用を保存する**

---

## §6 検査結果

すべて `docs/parallel-work.md` §6 の順序で実行。

| 検査 | 結果 |
|---|---|
| `belief_state.py --write-map` → `map_build.py`（順序どおり） | PASS（BELIEF_MAP 344,820B / READING_MAP 1,558,786B） |
| `validate_seed.py` | PASS（questions=438, sessions=1029, read_log=15802, notes=1118, hypotheses=74, evaluations=721） |
| `append_only_check.py --base HEAD` | PASS（32,481 行がバイト一致、純追記のみ） |
| `readings_integrity_check.py` | PASS（本文・見出し・note 行の欠損0） |
| `belief_state.py --check-map` / `map_build.py --check` | PASS / PASS |
| `note_index.py --check` | PASS（1041 notes が current） |
| `read_log_backfill.py --check` | PASS（8,194/8,194 ペア充足） |
| `date_axis.py --enforce-shards` | PASS（forward-dated 0） |
| `learning_metrics.py --check` | PASS（wiring gates 満足） |
| `three_gates.py --check` | PASS（三門不変条件保持） |
| `claim_wiring.py --check` | PASS（revision claim 全件が仮説名指名） |
| `size_budget.py --strict` | PASS（引上げ0件で全枠内） |
| `node --check viewer/app.js` | PASS |
| ベースライン `unittest`（作業前 main） | EXIT=0（既存赤なし） |
| 事後 `unittest`（本行追記後） | **937件 OK（EXIT=0、542.9秒）**。初回実行は執筆と並行した際の `READING_MAP` 一時 staleness で2件失敗したが、再生成後の独立再実行と3チェック×6回連続検査で全緑（詳細は[全文報告 §8-2](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md)） |

---

## §7 制限と未解決

1. `0ddede` 条項 (b)（保持時間の延長）は**未測定**。supports は (a)(c) 未発火の範囲でしかない
2. `8b3e04` の生物学的分離（Q-001 scope）は書庫では測定不能。本行は書庫範囲のみ
3. 五つ界面報告 §8-2 の事後統制批評率監査は未着手（handoff claim で明示）
4. open errata 58件・孤立報告 191件・`NOTE-256f8d` 系 claims 0件報告は、枠統合を要する次回作業
5. 併行 PR #966/#967 と同日シャードを共有。先行合流で file 数超過が起きた場合は cfdeb1 §8.3 の「合流後に吸収」手順に従う

---

## §8 まとめとリンク

- 全文報告: [`readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md)
- 評価2行: [`state/evaluations.d/2026-11-19-f5245d6249c6.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-19-f5245d6249c6.jsonl)（`EVL-20261119-5cf6fe`, `EVL-20261119-359ac7`）
- セッション行: [`state/sessions.d/2026-11-19-1fe0e56b678a.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-19-1fe0e56b678a.jsonl)
- 信念分布・索引（再生成済み）: [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) / [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)
- 委任の入口: [`README.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/README.md) / [`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)

本報告は PR として `main` へマージされる。最終回答のリンクはその PR を含む GitHub URL で示す。
