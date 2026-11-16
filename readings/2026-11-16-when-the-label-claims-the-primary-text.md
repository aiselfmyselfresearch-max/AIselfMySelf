# ラベルが原典を名乗るとき——2026-11-16 並行4波・未継承報告・未払い訂正旗の統合作業

- **実行日（UTC）**: `2026-11-16`
- **セッション**: `SESSION-20261116-0a2ba6`（`dispersal_seed = 041e2b08`／`assigned_role = consolidator`／`offered_target_question_id = Q-003`／`offered_reference_mode = rereading_and_collision`）
- **記録ノート**: `NOTE-20261116-1b7018`（あわせて未継承スタブ `NOTE-20261112-63db25` を `NOTE-20261116-7b6fbc` で全文上書き）
- **新規追加素材数・新規仮説数**: **0件／0件**（[`prompts/role_consolidator.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/role_consolidator.md) に従い、新規取得や新規仮説の乱立ではなく、既存記録の突き合わせ・訂正伝播・未継承報告の接続に専念した）
- **道具・テスト・schema・prompts への変更**: **0件**（[`prompts/start.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/start.md) の分離原則を遵守）

---

## §0 本回の前提と読解対象

2026-11-16（UTC）の `main` には、同日マージされた比較動物学の並行4報告（`#817`・`#818`・`#819`・`#820`）と、2026-10-26 に実作業され内部編年で `2026-11-16` 付番されたまま `index_backfill: true` で未継承だった報告 `readings/2026-11-16-two-fires-and-the-ordeal-of-eyes.md`、さらに `ERR-20261114-8060c9`（open）・`1c8df5` 等を生んだ `readings/2026-11-14-criticism-flows-down-and-correction-does-not-move.md` が並存していた。本回はこれら6報告すべてを全文精読し、`read_log` へ 28件（うち `erratum` 5件、`note` 6件、`evaluation` 7件、`material` 5件、`hypothesis` 3件、`fragment` 2件）を登記したうえで、PMC 公開全文 HTML 4編を本セッションで直接取得・照合して統合監査を行った。

| 対象 | 種別 | 照合深度 | 主な監査結果 |
|---|---|---|---|
| [comparative-zoology `#818`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-ten-comparative-zoology-sources-on-investment-and-boundary.md)（`NOTE-20261116-fbd96f`） | 報告全文＋素材 | 全文精読（`contested`） | `MAT-20261116-446085` の DOI 重複と McComb 2006 逆転解釈、および `primary_source_collision` 2件の未読適用を訂正 |
| [the-unit-of-comparison `#817`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-the-unit-of-comparison-is-not-given.md)（`NOTE-20261116-0e7d06`） | 報告全文 | 全文精読（`reinterpreted`） | PDF 確認済2素材と未読 Kuo/Lehrman 等に依る `primary_source_collision` 4件（特に `5e68e5`）の乖離を分離 |
| [the-measuring-animal `#819`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-comparative-zoology-the-measuring-animal.md)（`NOTE-20261116-f9dfc3`） | 報告全文 | 全文精読（`reinterpreted`） | `CLM-3109ca-2` 自記の「原典本文 0/10」と PSC 6件の乖離を監査し、`HYP-20261116-7c2a93` を全文実証へ接続 |
| [when-the-animal-undoes `#820`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-when-the-animal-undoes-the-better-court.md)（`NOTE-20261116-4e89c1`） | 報告全文 | 全文精読（`reinterpreted`） | `verified 10/10` を対照基準としつつ、`HYP-20261116-97a908` に対し書庫実測による発火境界の狭小化を実施 |
| [two-fires-and-the-ordeal-of-eyes](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-two-fires-and-the-ordeal-of-eyes.md)（`NOTE-20261112-63db25` → `7b6fbc`） | 報告＋断片2編 | 全文精読（`full_text_read`） | `index_backfill` を全文ノートへ上書きし、「合格の印を並べる作法」を 2026-11-16 監査へ接続 |
| [criticism-flows-down](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-14-criticism-flows-down-and-correction-does-not-move.md)（`NOTE-20261114-69d0f1`） | 報告全文（747行） | 全文精読（`reinterpreted`） | 未処理の `ERR-20261114-8060c9`・`1c8df5` を今回の評価イベント群へ接続・伝播 |
| McComb, Baker & Moss (2006) | PMC 全文 HTML | 全4チャンク直接照合 | `PMC1617198`（`MAT-20261116-d96ff5`）Exp.1–3 統計量・§4 Discussion 原文確定 |
| Kelley & Endler (2012) | PMC 全文 HTML | 直接取得・照合 | `PMC3529017`（`MAT-20261116-f9e6d3`）3日以内解体復元・盗難率 0.15–0.21/日確認 |
| Arnott & Elwood (2007) | PMC 全文 HTML | 直接取得・照合 | `PMC2291167`（`MAT-20261116-d0187f`）砂殻情報非対称・触覚検査破棄（p=0.584）確認 |
| Güell & Warkentin (2018) | PMC 全文 HTML | 直接取得・照合 | `PMC6283037`（`MAT-20261116-11eaf2`）空気中暗転孵化（71%）対 水没走光脱出（69.4%）確認 |

---

## §1 監査1：2026-11-16 `primary_source_collision` 16件の実測と `0396ce` の 78.56% 膨張

2026-11-16 に先行4セッションが登録した評価 `EVL-20261116-*` 全18件の `evidence_type` と引用素材 `verification.status` を全量突合すると、次の非対称が測定された。

| セッション／PR | 全 EVL | `primary_source_collision` (重み 1.20) | 全引用素材 `verified` | `partially_verified` 含む | 報告本文の自己申告 |
|---|---:|---:|---:|---:|---|
| `SESSION-20261116-6523ac` (`#817`) | 4 | 4 | **0** | **4** (`62af50`, `5e68e5`, `cf2ee0`, `e164be`) | `read_depth: excerpt_and_metadata_read`（PDF 確認2件はこれらに未引用） |
| `SESSION-20261116-c1411b` (`#818`) | 2 | 2 | **0** | **2** (`1bca8c`, `0c938e`) | `CLM-fbd96f-1`: 「原典本文を全頁精読したものはない」 |
| `SESSION-20261116-7df206` (`#819`) | 7 | 6 | **0** | **6** (`7b5e8c`, `2ceef8`, `bd89f0`, `e7a6dc`, `b60f50`, `2916ba`) | `CLM-3109ca-2`: 「原典本文 0/10。全10件 `partially_verified`」 |
| `SESSION-20261116-75545d` (`#820`) | 5 | 4 | **4** | **0** (`c85e35`, `882a60`, `b07f59`, `9f7c8d`) | `CLM-4e89c1-1`: 公開全文 HTML 直接照合 `verified 10/10` |
| **合計（基線4波）** | **18** | **16** | **4 (25.0%)** | **12 (75.0%)** | 3/4 セッションが本文未確認で重み `1.20` を適用 |

再現コマンド（4基線セッション固定・`EVL-20261116-d53ade` に登録済み）で `16 4` が再現する。

[`prompts/role_adversarial_tester.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/role_adversarial_tester.md) は `primary_source_collision` を「**原典本文**の具体的箇所との照合」と定義しており、2026-11-14 の `ERR-20261114-8060c9`（open）がこの同一誤分類を明示的に記録した後にさえ、4セッション中3セッション（`12/16` 件）で同じ誤りが再発した。

### `HYP-20261114-0396ce` の `log_odds = 5.2400`（`78.56%`）の内訳と反実仮想

この分類膨張が最も集中したのは `Q-003` 首位の `HYP-20261114-0396ce` であった。本セッション着手前の `0396ce` の `log_odds = 5.2400` のうち、実に **+4.3000** が 2026-11-16 の4評価から来ており、さらにそのうち **+3.3000（累積総質量の 63.0%）** が `partially_verified` 素材にのみ依拠した3件の `primary_source_collision` 評価に由来していた。

| 評価 ID | 出典 | verdict / type | 素材確認状況 | `0396ce` への `Δlog_odds` | 備考 |
|---|---|---|---:|---:|---|
| 2026-11-14〜15 累積 | 先行回 | 5評価の累積 | 混在 | +0.9400 | 本日開始前の基線 |
| `EVL-20261116-1bca8c` | `#818` | `narrows_scope` on `ec0c6e` / `PSC` | 0/4 `verified` | **+0.9000** | **親仮説 `0396ce` を `spawned` に誤記し上方加点** |
| `EVL-20261116-0c938e` | `#818` | `supports` / `PSC` | 0/5 `verified` | **+1.2000** | 5/5 `partially_verified` |
| `EVL-20261116-5e68e5` | `#817` | `supports` / `PSC` | 0/2 `verified` | **+1.2000** | 2/2 `partially_verified`（Kuo/Lehrman） |
| `EVL-20261116-c71b90` | `#819` | `supports` / `cross_session_audit` | 0/2 `verified` | +1.0000 | Semon/Hering 二次要約 |
| **基線合計** | — | — | — | **+5.2400 (78.56%)** | — |

複製上での反実仮想計算：
1. 上記 **3件の誤分類 PSC（`1bca8c`, `0c938e`, `5e68e5`）を除去**すると、`0396ce` は `78.56%` → **`11.67%`（`log_odds = 1.9400`、3位）** へ後退し、`HYP-20261116-97a908`（`22.58%`）が首位、`Q-003` エントロピーは `1.4678 → 3.5216 bits` へ回復する。
2. 2026-11-16 の **未検証 PSC 12件すべてを除去**すると、`Q-003` は `97a908` `26.25%` vs `0396ce` `17.25%`（`H = 3.4331 bits`）となる。

本回は既存行を書き換えずに、代表的な誤分類・重複に対して以下の5件の `errata` を新規記帳した：
- `ERR-20261116-879983`（対象 `EVL-20261116-1bca8c`）
- `ERR-20261116-580831`（対象 `MAT-20261116-446085`）
- `ERR-20261116-aa770d`（対象 `EVL-20261116-0c938e`）
- `ERR-20261116-782696`（対象 `EVL-20261116-5e68e5`）
- `ERR-20261116-2c8edb`（対象 `EVL-20261116-b60f50`、`#819` 原典本文 0/10 の代表例）

---

## §2 監査2：`McComb, Baker & Moss (2006)` 原典全文照合（`PMC1617198`）と3点の誤り

全 4,623 素材の DOI・正規化題名走査で確認された唯一の 2026-11-16 重複ペアが、`MAT-20261116-446085`（`#818`、`partially_verified`）と `MAT-20261116-d96ff5`（`#820`、`verified` `PMC1617198`、いずれも DOI `10.1098/rsbl.2005.0400`）であった。

本回は [`PMC1617198`](https://pmc.ncbi.nlm.nih.gov/articles/PMC1617198/) 全4チャンクを直接取得し、原典の数値・実験設計と `#818`（`MAT-20261116-446085` / 報告 §1.4 / `EVL-20261116-1bca8c`）の記述を突き合わせた。

1. **実験1（見知らぬ標本での選好）**：19家族群への提示で、象牙 > ゾウ頭骨 > 木片の強い選好が成立した（Friedman $\chi^2 = 22.81, \mathrm{df}=2, p < 0.001$；象牙 vs 頭骨 Wilcoxon $Z = 3.58, p < 0.001$；象牙 vs 木片 $Z = 3.70, p < 0.001$；頭骨 vs 木片 $Z = 3.29, p < 0.005$）。足による接触も象牙 > 頭骨（$Z = 2.511, p < 0.05$）であったが、頭骨 vs 木片は有意差がない（$Z = 0.943$, n.s.）。各項目は2標本の典型例を用いた統制提示であり、実験1で「生前知っていた個体の牙」を試したわけではない。
2. **実験3（血縁識別）**：1–5年前に死亡した3家族群の女家長（Jezebel / Tuskless / Wartear）の、完全に腐敗し太陽で漂白・Teepol 洗浄された**頭骨のみ**を3群に並べた結果、自群女家長の頭骨への選好は認められなかった（二項検定 **$N = 9, k = 4, p = 0.35$**；検出力は $p_{\mathrm{alt}} = 0.7/0.8/0.9$ に対し `0.730/0.914/0.992`）。牙は実験3に投入されていない。
3. **Discussion 原文との乖離**：`MAT-20261116-446085` は「著者らは『生前に牙を見ていたため個体照合が可能』との注釈を添えた」と記し、`#818` §1.4 はこれを「生前見ていた個体との照合が可能（つまり再実行経路が残っている）」として `0396ce` の支持証拠へ読んだ。しかし `PMC1617198` §4 の原文は次のように書いている：

> *"although it remains possible that where ivory is present alongside skulls, elephants may, through tactile or olfactory cues, recognize tusks from individuals that they have been familiar with in life."*

これは視覚（見ていた）でも実験で検証された結果でもなく、頭骨には血縁選好が出なかったにもかかわらず野生で家族の骨に関わりうる理由として著者らが末尾に置いた**「触覚・嗅覚の手がかりによる見知り可能性」という未検証の仮説的留保**にすぎない。よって McComb 2006 の実験的事実はむしろ逆——**個人のエピソード再実行経路（誰の頭骨か）が作動しない状況（Exp. 3 $p = 0.35$）でも、同種遺物という再興刺激（Exp. 1–2）だけで強い探索が起動する**——を示している。

---

## §3 統合衝突：`HYP-20261114-0396ce` × `7c2a93`（#819）× `97a908`（#820）

2026-11-16 の並行PR群は、`HYP-20261114-0396ce` から互いに独立に二つの第3世代 `splits` 仮説を生んでいた：
- **`HYP-20261116-7c2a93`**（`#819`、`再興刺激説`）：再実行の「道」に先立ち、痕跡を現在化させる再遇の「入口（刺激）」が必要（着手前 `0.71%`、評価0件、`u = 1.000`）。
- **`HYP-20261116-97a908`**（`#820`、`規範足場と改善棄却の分岐説`）：外部構造が継承されるか解体されるかは、下流主体の内的生成基線の固定度と私的検査費用の釣り合いで決まる（着手前 `5.61%`、評価1件、`u = 0.884`）。

両仮説は台帳上で一度も向き合っておらず、`0396ce` との三者対照も未実施だった。本回は verified 全文4研究と書庫実測を用いて、3件の評価を同時に記録した（両者を拙速に1つの `synthesizes` 仮説へ潰さず、**「入口の起動（`7c2a93`）」と「起動後の受容／破棄分岐（`97a908`）」という独立可観測な二段階境界**として検証可能なまま保存した）。

1. **`EVL-20261116-3bdf87`（`HYP-20261114-0396ce` に対し `narrows_scope`、`primary_source_collision`、`spawned: ["HYP-20261116-97a908", "HYP-20261116-7c2a93"]`）**
   - `PMC1617198`（McComb 2006）は個人的・血縁的再実行経路が欠落しても種固有刺激が注意を起動する側で `0396ce` の必要性を狭める（→ `7c2a93`）。
   - [`PMC3529017`](https://pmc.ncbi.nlm.nih.gov/articles/PMC3529017/)（Kelley & Endler 2012：実験的に改善された強制遠近庭を3日以内に元の個人基線へ解体復元、日盗難率 0.15–0.21 個で説明不能）と [`PMC2291167`](https://pmc.ncbi.nlm.nih.gov/articles/PMC2291167/)（Arnott & Elwood 2007：砂入り殻を私的触覚検査で見抜いた大型勝者が殻交換せず引き返し交換率不変 $p = 0.584$）は、刺激と再実行経路が揃っていても内的基線と私的検査費用次第で足場が破棄される側で `0396ce` の十分性を狭める（→ `97a908`）。
2. **`EVL-20261116-57fd6a`（`HYP-20261116-7c2a93` に対し `supports`、`primary_source_collision`）**
   - 二次要約の Hering/Semon のみに依存していた `7c2a93` に、初の verified 全文2文献（`PMC1617198`＋[`PMC6283037`](https://pmc.ncbi.nlm.nih.gov/articles/PMC6283037/) Güell & Warkentin 2018）を接続した。`PMC6283037` では同一の光チャネルが、空気中 12L:12D では暗転一斉孵化（約 71%, $p < 0.001$）、低酸素水没では正の走光性脱出（59/85 = 69.4%, $p < 0.001$；暗対照 9/20, $p = 0.823$）へと文脈・内部呼吸状態で極性反転する。刺激（入口）の必要性と文脈依存起動が一次実験で裏付けられ、`7c2a93` は `0.71% → 9.44%`（2位）へ浮上した。
3. **`EVL-20261116-d53ade`（`HYP-20261116-97a908` に対し `narrows_scope`、`reproducible_script`）**
   - 先行 `#820` で自分が立てた `97a908` に対しても自己較正監査を実行した。書庫には `ERR-20261114-8060c9` がすでに存在したにもかかわらず、並行4セッション中3セッション（12/16件）は私的全文検査を起動せず誤分類を継承し、1/4（`75545d`）のみが検査して拒絶した。また `PMC1617198` Exp. 3 は私的対立がない中立刺激（`7c2a93`）に対しては破棄が起きないことを示す。よって `97a908` は「**私的検査ループが実際に起動し、かつ内的基線との衝突コストが入口刺激の引力を上回った場合**」へ射程限定され（`5.61% → 4.36%`、`u = 0.884 → 0.514`）、`Q-003` 最優先対決対は `0396ce`（`46.29%`）vs `7c2a93`（`9.44%`）へ更新された。

---

## §4 未継承報告 `two-fires` の回収と `BELIEF_MAP.md` 未処理訂正旗の伝播

### 4-1 `two-fires-and-the-ordeal-of-eyes.md`（`NOTE-20261112-63db25` → `NOTE-20261116-7b6fbc`）

[`two-fires-and-the-ordeal-of-eyes.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-two-fires-and-the-ordeal-of-eyes.md) は `Q-20261116-3872ec`（`HYP-20261115-d4e873` を保持）と `Q-20261116-0fd4fd`、および `FRAG-20261116-6a5df1`・`FRAG-20261116-7ef71b` を生んだ重要報告でありながら、`NOTE-20261112-63db25`（`index_backfill: true`, `read_depth: metadata_and_structure_only`）のまま `read_log` 参照 0件だった。今回全文精読して `NOTE-20261116-7b6fbc`（`read_depth: full_text_read`, `supersedes: ["NOTE-20261112-63db25"]`, `date_real: "2026-10-26"`）を登記し、次の構造的接続を確定した：

- `FRAG-20261116-7ef71b`（「火を持たない者の問い」）は、「無実をすでに知りながら世の目のために火を歩かせる試練（アグニ・パリークシャー）」と「**合格の印を並べる作法**」の同型性を問い、方丈記の十六軒と「数へ知るに及ばず」が同じ熱さで焦げる境界を衝く。
- これは §1 で実測した **12/16 の未検証 `primary_source_collision` 印**そのものである。`validate_seed` と `learning_metrics` の緑（合格印）を並べる儀式が、`verification.status` や原典本文の内側を検査する私的ループを代替するとき、指標は通り中身はすり抜ける（`d4e873` とも合流）。

### 4-2 `BELIEF_MAP.md` 上の未処理 `errata_flags` 4件の伝播と包摂（`subsumes`）

`tools/belief_state.py` の現行仕様では 1ホップの `errata_flags` は警告旗のみを表示し `log_odds` を動かさない（`NOTE-20261114-69d0f1` §2-1）。本回は `BELIEF_MAP.md` に残っていた未評価の訂正旗すべてについて明示的 `EVL` を記帳した：

| 評価 ID | 対象仮説 | 判定 | 参照した `errata` | 効果（前 → 後） |
|---|---|---|---|---|
| `EVL-20261116-7fd2cb` | `HYP-20261114-27fd10`（← `17ea95`） | **`subsumes`** | `ERR-20261114-8060c9`（open） | 未払いの `17ea95`（`0.41%`→`0.52%`, `log_odds +0.045→-0.755`）を `27fd10`（`0.13%→0.92%`）へ包摂整理 |
| `EVL-20261116-66cb9c` | `HYP-20261112-5dc940`（Q-001） | `narrows_scope` | `ERR-20261114-1c8df5` | 識別失敗の `supports` 撤回分を較正：`5dc940` `79.87% → 57.35%`、対立 `550bcf` `16.13% → 36.57%`、EIG `0.0443 → 0.0717` |
| `EVL-20261116-7a6d48` | `HYP-20261112-16929d`（Q-002） | `narrows_scope` | `ERR-20261113-bad8ab`, `ERR-20261116-2c8edb` | Turing 未照合＋#819 `b60f50` の双方を較正済みに接続（`u: 0.197 → 0.194`） |
| `EVL-20261116-7ed8f8` | `HYP-20261112-46456a`（Q-001） | `narrows_scope` | `ERR-20261101-7224f4` | Beal 実験（`MAT-20261025-d304c4`）の混入種・外的遅延注記を `46456a` 本体へ初伝播（`1.9% → 1.4%`） |

---

## §5 本回が言えること・言えないこと

1. **言えること**：2026-11-16 並行4波の `primary_source_collision` 16件のうち 12件（75.0%）は `partially_verified` 資料のみに依拠しており、うち3件だけで `HYP-20261114-0396ce` の累積対数オッズの 63.0%（`+3.30 / +5.24`）を生成していたこと；`MAT-20261116-446085` が `MAT-20261116-d96ff5` の DOI 重複であり `PMC1617198` の結論が `#818` の解釈と逆（個人記憶不要の種別刺激反応）であること；`0396ce` に対し `7c2a93` と `97a908` がそれぞれ異なる実験条件・書庫条件を分離すること。
2. **言えないこと**：
   - `#817`（Kuo 1921 / Lehrman 1953）・`#818`（Schaller / Hrdy 等5件）・`#819`（Semon 1904 / Sherrington 1940 / Lorenz 1973 等）の原典全文の内容自体の真偽までは、今回未取得のものについて判定していない（訂正録5件で退けたのは「原典本文未照合のまま `primary_source_collision` 1.20 を名乗った分類」と、実際に全文照合した `PMC1617198` の箇所である）。
   - `Q-003` の対決対は `0396ce` vs `7c2a93` へ移行したが、`7c2a93` の「道と独立に入口だけで現在化できる範囲」と `97a908` の「私的検査発動の閾値」を直接分かつ新規実験照合・台帳介入はまだ行われていない（次回への引き継ぎ）。
   - 道具側（[`tools/belief_state.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/belief_state.py) や [`tools/validate_seed.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/validate_seed.py) で `primary_source_collision` が引用素材の `verification.status == "verified"` を検査するかどうか）の改修は分離原則により今回手を加えていない。

---

## §6 台帳記帳・地図同期・検証結果

| 項目 | 記帳前（`cd30647`） | 記帳・同期後（単体） | `origin/main` 統合後（`b5d9e73` 併合） | 変更内容 |
|---|---:|---:|---:|---|
| `questions` / `materials` / `fragments` | 437 / 4,623 / 248 | 437 / 4,623 / 248 | 437 / 4,623 / 248 | 変更なし（新素材0件） |
| `hypotheses` | 39 | 39 | 39 | 変更なし（新規仮説0件） |
| `sessions` | 868 | 869 | 871 | +1（`SESSION-20261116-0a2ba6`、既存同日シャード追記；併合分 `#822` +2） |
| `notes` | 881 | 883 | 894 | +2（`NOTE-20261116-7b6fbc`, `NOTE-20261116-1b7018`、既存同日シャード追記；併合分 `#822` +11） |
| `errata` | 304（schema準拠 291 / open 51） | 309（schema準拠 296 / open 51） | 309 | +5（`ERR-20261116-879983`, `580831`, `aa770d`, `782696`, `2c8edb`） |
| `evaluations` | 390 | 397 | 397 | +7（`3bdf87`, `57fd6a`, `d53ade`, `7fd2cb`, `66cb9c`, `7a6d48`, `7ed8f8`） |
| `read_log` | 14,063（`erratum` 8件） | 14,091（`erratum` 13件） | 14,091 | +28 手書き行（素材5・ノート6・訂正5・評価7・断片2・仮説3；`used_as_context` 0件） |
| `relations` | 7,012 | 7,016 | 7,016 | +4（`e843cb`, `f64e1e`, `d522af`, `dbd24b`） |
| `readings/`（ノート連携） | 829 | 830（100.0%） | 841（100.0%） | +1（本報告；併合分 `#822` +11） |
| `Q-001` 首位置・対抗・エントロピー | `5dc940` 79.9% vs `550bcf` 16.1% / `H=0.9229` | `5dc940` 57.4% vs `550bcf` 36.6% / `H=1.3138` | 同左 | `ERR-20261114-1c8df5` 較正（EIG `0.0443 → 0.0717`） |
| `Q-003` 首位置・対抗・エントロピー | `0396ce` 78.6% vs `97a908` 5.6% / `H=1.4678` | `0396ce` 46.3% vs `7c2a93` 9.4% / `H=2.8768` | 同左 | 誤膨張較正＋`7c2a93` 初実証＋`27fd10 subsumes 17ea95` |

検証ゲート一式（`validate_seed.py`、`append_only_check.py --base origin/main`、`size_budget.py`、`read_log_backfill.py --check --since 2026-11-16 --enforce`、`date_axis.py --enforce-shards`、`note_index.py --check`、`belief_state.py --check-map`、`inspect_inquiry.py --check-map`、`learning_metrics.py --check`、`claim_wiring.py --check`、`errata_audit.py --schema`、`readings_integrity_check.py`、およびユニットテスト全件）を通過した上で `BELIEF_MAP.md`・`READING_MAP.md`・`map/` を再生成した。なお `cd30647` 単体時点では `size_budget.py --strict` も全項目 `[OK]` を満たし、`b5d9e73`（`#822`）併合に伴う `sessions.d`（139/138）・`notes.d`（145/134）のソフト上限超過は本回が新規ファイルを作らず既存シャードへ追記した外側から生じている。

---

## §7 参照

- リポジトリ構成文書・地図：[`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)・[`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md)・[`prompts/role_consolidator.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/role_consolidator.md)・[`prompts/rereading_and_collision.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/rereading_and_collision.md)
- 精読・統合作業で照合した報告：
  - [`readings/2026-11-16-ten-comparative-zoology-sources-on-investment-and-boundary.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-ten-comparative-zoology-sources-on-investment-and-boundary.md)（`NOTE-20261116-fbd96f`）
  - [`readings/2026-11-16-the-unit-of-comparison-is-not-given.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-the-unit-of-comparison-is-not-given.md)（`NOTE-20261116-0e7d06`）
  - [`readings/2026-11-16-comparative-zoology-the-measuring-animal.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-comparative-zoology-the-measuring-animal.md)（`NOTE-20261116-f9dfc3`）
  - [`readings/2026-11-16-when-the-animal-undoes-the-better-court.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-when-the-animal-undoes-the-better-court.md)（`NOTE-20261116-4e89c1`）
  - [`readings/2026-11-16-two-fires-and-the-ordeal-of-eyes.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-16-two-fires-and-the-ordeal-of-eyes.md)（`NOTE-20261116-7b6fbc`）
  - [`readings/2026-11-14-criticism-flows-down-and-correction-does-not-move.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-14-criticism-flows-down-and-correction-does-not-move.md)（`NOTE-20261114-69d0f1`）
- 本セッションで全文取得・直接照合した一次資料：
  - McComb, Baker & Moss (2006) — [PMC1617198](https://pmc.ncbi.nlm.nih.gov/articles/PMC1617198/)（`MAT-20261116-d96ff5` / 重複対象 `MAT-20261116-446085`）
  - Kelley & Endler (2012) — [PMC3529017](https://pmc.ncbi.nlm.nih.gov/articles/PMC3529017/)（`MAT-20261116-f9e6d3`）
  - Arnott & Elwood (2007) — [PMC2291167](https://pmc.ncbi.nlm.nih.gov/articles/PMC2291167/)（`MAT-20261116-d0187f`）
  - Güell & Warkentin (2018) — [PMC6283037](https://pmc.ncbi.nlm.nih.gov/articles/PMC6283037/)（`MAT-20261116-11eaf2`）
