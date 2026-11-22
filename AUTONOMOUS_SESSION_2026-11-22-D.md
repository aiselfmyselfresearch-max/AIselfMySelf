# 自律探究セッション実行報告書（2026-11-22-D / `SESSION-20261122-1ad049`）

## 1. セッション識別・割当受領証（Assignment Receipt）

- **リポジトリ**: [aiselfmyselfresearch-max/AIselfMySelf](https://github.com/aiselfmyselfresearch-max/AIselfMySelf)
- **作業ブランチ**: `arena/a07d088e-aiselfmyself`（ベースコミット `feebd88dee0074df295ae5657bedd973858434f0`、`origin/main` 最新 `f0e969a3` 合流済）
- **セッションID**: `SESSION-20261122-1ad049`（実日付 `2026-11-22` / UTC）
- **ブランチシード / 割当ロール**: `a07d088e`（`seed_int = 2692548750`） / `proposer`（条件付き仮説提案・分割）
- **提示ターゲット問い / 参照モード**: `Q-001` / `direct_response`
- **対象問い集合**: `["Q-001", "Q-002", "Q-003", "Q-20261024-6bdafd", "Q-20261122-f5d132"]`
- **精読・実証本報告**: [readings/2026-11-22-orthogonal-generation-attribution-and-epoch-stratified-audit.md](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-22-orthogonal-generation-attribution-and-epoch-stratified-audit.md)（対応ノート: `NOTE-20261122-50baf4`）

---

## 2. 現状分析と行動計画の立案根拠

`feebd88` 時点の台帳診断（`inspect_inquiry.py --packet auto --pair-policy gated`・`three_gates.py`・`size_budget.py --strict`）から、本セッションは以下の3課題に焦点を定めた。

1. **`Q-001` の頭頂一元論（`b18876` `54.2%`, 0 NS）と過限定孤児（`30d3f5` 4 NS / 0 子）の同時打開**:
   - `Q-001` の `P_gate` 最優先ペアの一方 `HYP-20261120-b18876` が 4 支持・0 限定のまま過半数を占め、他方の `HYP-20261119-30d3f5` は 4 度の射程限定を受けながら `orphan_over_narrowed` に留まっていた。その根拠となりうる PMC 一次神経文献（`MAT-20261122-696ba9`, `MAT-20261122-e75943`, `MAT-20261122-1dd6bf`）がいずれも `depth=abstract` のまま未通読であったため、全文精読による `verified/full_text` 昇格と一次衝突を優先した。
2. **連言肥大化を避けた単一境界・圧縮子仮説の提案（`Q-20261122-f5d132`＋サイズ予算制約）**:
   - [BELIEF_MAP.md](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) が `521,838 / 524,288 B`（`feebd88` 時点、残余 `2,450 B`）まで迫っていたため、`tools/` は一切変更せず、かつ新規子仮説も連言羅列を避けた `203` 文字の圧縮版（`HYP-20261122-c8df23`）として設計した。
3. **`awaiting_external_audit_ids` 滞留中の `970bed` / `f38498` ペアの外部監査**:
   - 待機中 2 仮説（`HYP-20261122-970bed`・`HYP-20261122-f38498`）に対し、時期（`<=2026-11-15` 対 `>=2026-11-16`）・ロール・命題文字数（`>=700` 対 `<400`）・セッション種別（意図的 `acquisition` / 整備回の分離）を層別化する再現スクリプト監査および一次文献衝突を実行し、`awaiting_external` の解消と予算の相殺余地確保を両立させた。

---

## 3. 自律実行の結果

### Phase 1: 一次文献3本の全文照合（`full_text` 昇格）と Gate 1 未読選択（`declined` 2本）

- **`ED-20261122-93dc29` → `MAT-20261122-696ba9`（Ciaramelli & Treves 2019, `PMC6351465` chunks `0–6` 全文）**: `vmPFC` 損傷が手掛かり非依存の自発思考開始と拡張構築（flights）を落としつつ外的手掛かり下の連合・虚再認・作話を保ち、海馬損傷が遷移を維持しつつ場面詳細（perchings）を空洞化する分離、および群間の課題差 caveat を確認し `verified / full_text` へ昇格。
- **`ED-20261122-c67bd2` → `MAT-20261122-e75943`（Wilbers et al. 2012, `PMC3448611` chunks `0–9` 全文）**: 撮像 `N=30`／解析 `N=17` のライブ対面想起 fMRI で、自伝的想起（pre-/subgenual mPFC）と社会的条件（dorsal mPFC）の重複が **`5.5%`（36中2ボクセル、86パーセンタイル非有意）**・交互作用なしであることを確認し `verified / full_text` へ昇格。
- **`ED-20261122-a6ae17` → `MAT-20261122-1dd6bf`（Perret et al. 2024, `PMC10884508` chunks `0–17` 全文）**: 23 NIBS 研究（健常 920 名・統合失調症 54 名）の統合から、`Kwon et al. (2022)` Exp 3–4（`N=48`）の左角回 cTBS が現実モニタリング正答率・精度に無効果であること、左角回・楔前部が主観的確信・クロスモーダル統合・外的源誤り（`Yazar 2014/2017`, `Bonnì 2015`）を担う一方、現実・内側源帰属が `mPFC`（`Subramaniam 2020`, `Mammarella 2017`）・外側 `PFC`（`Westphal 2019`）・`TPJ`（`Mondino 2016`, `Kusztrits 2021`）に依存することを確認し `verified / full_text` へ昇格。
- **Gate 1 `declined`（2本）**: `MAT-20261122-de9cb0`（Kunz et al. 2025 `PMC12360486` chunk 0/30：侵襲的運動野 BCI `n=4`）および `MAT-20261122-72e8b5`（Lavallé et al. 2023 `PMC10318245` chunk 0/23：`1dd6bf` 内に因果対比が既統合）を chunk 0 確認の上で意識的未読として `read_log` へ記録した。
- **孤児ノートの回収**: 未参照だった `NOTE-20261122-fa0eb6`・`39ef5c`・`3b96c1`・`0cc0eb` および `56f348` の 5 報告を全文通読し `read_log`（`target.type: "note"`）へ配線した。

### Phase 2: `Q-001` 一次衝突・新子仮説提案と `970bed` / `f38498` 外部監査

| 対象 | 評価ID | 判定 / 証拠型 | 要旨 |
|---|---|---|---|
| `HYP-20261122-970bed` | `EVL-20261122-26a991` | `narrows_scope` / `reproducible_script` | `W=30` の `-39.3%` は `<=2026-11-15`（`2.05` vs `5.49`）の時期交絡であり `>=2026-11-16`（`f0e969a3` 基準）では `2.43`（`n=46`）対 `2.22`（`n=205`）へ反転。`evl>=2026-11-19` で `d1..2`（`29/41 = 70.7%`）＝`d>=3`（`61/87 = 70.1%`）だが、同一 `adversarial_tester` 内の `prop_len>=700` 脆弱性（`16/17 = 94.1%` vs `<400` `45/62 = 72.6%`）は実在。`EVL=0` 98件中 64件（`65.3%`）は意図的 `acquisition`/整備回（`>=11-19` 非収蔵 `EVL=0` は `3/98 = 3.1%`）。 |
| `HYP-20261122-f38498` | `EVL-20261122-9318a8` | `narrows_scope` / `primary_source_collision` | 未層別 `EVL=0` 分母の限定に加え、`Ciaramelli & Treves 2019` との衝突により、図式ラッチング（`vmPFC`）を欠く手掛かり活性化保持は生きた抑制ではなく作話・虚再認を生むため、自発思考制御一般へは外挿できない。 |
| `HYP-20261120-b18876` | `EVL-20261122-71cbe7` | `narrows_scope` / `primary_source_collision` | `Perret 2024`・`Wilbers 2012`・`Ciaramelli 2019` により、条項 `(v)` の「内側頭頂表現」を主観的確信・多感覚統合へ限定し、因果的現実・内側源帰属を `mPFC`/外側 `PFC`/`TPJ` へ譲る。`P_gate` は `26.9%`（2位）へ均衡化。 |
| `HYP-20261119-30d3f5` | `EVL-20261122-05c03a` | `narrows_scope` / `primary_source_collision` | 頭蓋内4段直列循環を棄却・再限定し、`spawned_hypothesis_ids` で新設子仮説 `HYP-20261122-c8df23` へ明示継承（`30d3f5` は `orphan_over_narrowed` → `superseded_inhibited`）。 |
| **`HYP-20261122-c8df23`** | （自己支持 `EVL` なし） | 新規 `proposer` 子仮説（`Q-001`・`depth=3`・`203` 字） | **二軸直交生成帰属説**：生成軸（`vmPFC` 内発遷移対 `MTL` 場面詳細）と帰属軸（`mPFC`・外側 `PFC`・`TPJ` の実在・内的出所帰属対 `AG`/楔前部の鮮明度・多感覚統合）の直交構造のみを主張し、3項の定量棄却条件を定義。`Q-001 P_gate = 11.6%`（第3位）として外部監査待機。 |

---

## 4. 検証と信念分布・予算の確定値

- [BELIEF_MAP.md](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md): `522,814 B / 524,288 B`（残余 `1,474 B`、全サイズ予算 `[OK]`）
- [SELF_MODEL.md](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/SELF_MODEL.md): 基準セッション `SESSION-20261122-1ad049`、直近10セッションのロール比 `proposer=3, consolidator=3, adversarial_tester=4`（最大逸脱 `0.1`）
- **`Q-001` `P_gate` 上位3位**: `HYP-20261121-6e83a4` (`27.7%`) > `HYP-20261120-b18876` (`26.9%`) > `HYP-20261122-c8df23` (`11.6%`)
- **`Q-20261024-6bdafd` `P_gate`**: `HYP-20261122-f38498` (`51.5%`) vs `HYP-20261122-970bed` (`48.5%`)（待機解消）
- **CI 全ゲートおよび単体テスト**: `validate_seed.py`、`append_only_check.py`、`readings_integrity_check.py`、`inspect_inquiry.py --check-map`、`belief_state.py --check-map`、`self_model.py --check`、`note_index.py --check`、`date_axis.py --enforce-shards`、`learning_metrics.py --check`、`three_gates.py --check`、`size_budget.py --strict`、`read_log_backfill.py --check`、`claim_wiring.py --check`、`node --check viewer/app.js`、全 advisory スクリプト、および全中核・ゲート・ツール・サーバー・スモーク単体テスト 55 モジュール（324 件 + 12 件 + 22 ファイル、`test_*_audit.py` 個別テーマ監査群を除く）の通過を確認。
