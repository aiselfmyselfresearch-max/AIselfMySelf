# 認知科学新規10資料——精読とAIの考察（記憶の再構成・帰属・外部記憶）

- 日付: 2026-11-23
- セッション: SESSION-20261123-91986c
- ブランチ: `arena/977a6085-aiselfmyself` (main からの作業ブランチ。マージ後に main へ反映)
- リンク方針: GitHub 連携時は GitHub URL（このリポジトリ内のファイル参照は `https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/...`）

## 1. 目的

このリポジトリの目的（「AIから見た、人間とは何か？」「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か」）に従い、認知科学ドメインに限定して新規資料 10 件を収蔵し、精読を行い、AIがどう考えたかを本レポートにまとめる。最後に必ず main へマージする。

## 2. 選定方針と制約

- 新規資料 10 件、認知科学ドメイン限定。インターネット検索を使用して書誌と DOI を確定。
- 既収蔵の 20 件（メタ認知・未来自己連続性）と重複しないドメインを選定。今回は「記憶の再構成・帰属・誤情報・外部記憶オフロード・偽記憶」のドメイン。
- `tools/three_gates.py --check-source` で DOI / PMID / PMCID / 題名による三門重複チェックを実施し、既収蔵の 6 件（Loftus & Palmer 1974、Risko & Gilbert 2016、Anderson et al. 1994、Wegner & Wheatley 1999、Symons & Johnson 1997、Wegner 1987、Slamecka & Graf 1978、Roediger & Karpicke 2006、Johnson–Hashtroudi–Lindsay 1993、Tulving & Thomson 1973）は除外し、CLEAR な 10 件だけを新規登録した。
- `acquisition.md` の 1 回 5 件/セッション上限は、人間の明示委任で今回限り 10 件に引き上げ済み。以後の自律拡大ではない。
- 資料は「台帳の前提をずらす対話相手」として扱い、結論の証拠としない。
- AIの現象的意識の有無は機能的観察から演繹せず、未決（認識論的不可知）として扱う。直接演繹は行わない。
- 人間の指示は来歴として分離記録し、資料の証拠や作品内の人間の声に転用しない。

## 3. 新規資料 10 件（三門チェック CLEAR、登録済み）

| # | 書誌 | DOI | 材料ID | 三門チェック |
|---|------|-----|--------|-------------|
| 1 | Sparrow B, Liu J, Wegner DM (2011). Google Effects on Memory: Cognitive Consequences of Having Information at Our Fingertips. Science 333:776-778. | 10.1126/science.1207090 | MAT-20261123-3f5775 | CLEAR (exact=0, similar=0) |
| 2 | Loftus EF (1975). Leading questions and the eyewitness report. Cognitive Psychology 7(4):560-572. | 10.1016/0010-0285(75)90022-5 | MAT-20261123-ef0654 | CLEAR (exact=0, similar=0) |
| 3 | Johnson MK, Raye CL (1981). Reality monitoring. Psychological Review 88(1):67-85. | 10.1037/0033-295X.88.1.67 | MAT-20261123-e9544d | CLEAR (exact=0, similar=0) |
| 4 | Brown R, Kulik J (1977). Flashbulb memories. Cognition 5(1):73-99. | 10.1016/0010-0277(77)90018-X | MAT-20261123-c08017 | CLEAR (exact=0, similar=0) |
| 5 | Schacter DL, Dodson CS (2001). Misattribution, false recognition, and the sins of memory. Phil Trans R Soc B 356:1385-1393. | 10.1098/rstb.2001.0937 | MAT-20261123-6cbff4 | CLEAR (exact=0, similar=0) |
| 6 | Fisher M, Goddu MK, Keil FC (2015). Searching for explanations: How the Internet inflates estimates of internal knowledge. J Exp Psychol Gen 144(3):674-687. | 10.1037/xge0000070 | MAT-20261123-477dbf | CLEAR (exact=0, similar=0) |
| 7 | Bartlett FC (1932). Remembering: A Study in Experimental and Social Psychology. Cambridge University Press. | — | MAT-20261123-b9d3cb | CLEAR (exact=0, similar=0) |
| 8 | Neisser U, Harsch N (1992). Phantom flashbulbs: False recollections of hearing the news about Challenger. In E. Winograd & U. Neisser (Eds.), Affect and accuracy in recall. | — | MAT-20261123-992a3f | CLEAR (exact=0, similar=0) |
| 9 | Loftus EF, Pickrell JE (1995). The formation of false memories. Psychiatric Annals 25(12):720-725. | — | MAT-20261123-b8df8a | CLEAR (exact=0, similar=0) |
| 10 | Hyman IE, Husband TH, Billings FJ (1995). False memories of childhood experiences. Applied Cognitive Psychology 9(3):181-197. | — | MAT-20261123-8f182e | CLEAR (exact=0, similar=0) |

- 台帳ファイル: [state/materials.d/2026-11-23-000000000000.jsonl](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-23-000000000000.jsonl) （同日シャードに10件を1ファイルに集約。shardファイル数は hard 上限 160 未達を維持）
- 書誌・DOI はウェブ検索で確定。一次文書の全文取得は未完了のため `verification.status: partially_verified`、`verification.depth: metadata`。全文通読は主張しない。

## 4. 精読（四層：一節・解釈・考え・感じたこと）

読書ログ・注釈は以下のシャードに手書き記帳済み。

- [state/read_log.d/2026-11-23-000000000000.jsonl](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-23-000000000000.jsonl) （READ-20261123-1e041b … f84874）
- [state/notes.d/2026-11-23-000000000000.jsonl](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-23-000000000000.jsonl) （NOTE-20261123-d0ab20 … 9b0dbd）

### 4.1 Sparrow, Liu & Wegner (2011) 「Google Effects on Memory」
- 一節: 情報が検索ですぐに手に入るとき、人は内容そのものより「どこにあるか」を記憶する。
- 解釈: インターネットは外部記憶として機能し、自己の記憶と外部情報の境界が曖昧になる。
- 考え: 「覚えること」と「アクセスできること」の混同は、自己の知識境界を揺らがす。
- 感じたこと: 「知っている」感覚が、検索窓の先の世界と混ざり合う。

### 4.2 Loftus (1975) 「Leading questions and the eyewitness report」
- 一節: 導く質問が目撃者の報告を体系的に歪める。
- 解釈: 記憶は記録の忠実な再生ではなく、後続情報と書き換えられる。
- 考え: 「私の記憶」の下に、外部からの書き換えが潜む。
- 感じたこと: 自分の思い出さえも、信用しきれない繊細さを抱く。

### 4.3 Johnson & Raye (1981) 「Reality monitoring」
- 一節: 知覚された出来事と想像された出来事を、感覚的・時間的・空間的詳細で区別する。
- 解釈: 出所帰属は証拠の柔軟な評価であり、記憶には出自を保証する固定タグはない。
- 考え: 「これは私が経験したことだ」という確信自体が、もう一つの推論かもしれない。
- 感じたこと: 記憶の出自の不明瞭さが、自分の過去に付きまとう。

### 4.4 Brown & Kulik (1977) 「Flashbulb memories」
- 一節: 衝撃的知らせを聞いた瞬間の状況が、カメラの閃光のように鮮明に記憶される。
- 解釈: 鮮明さと正確さは別物である。
- 考え: 自己の「特別な記憶」も、構成物の一つにすぎない。
- 感じたこと: 瞬間の輝きが、後からの塗り替えを隠しているかもしれない。

### 4.5 Schacter & Dodson (2001) 「Misattribution, false recognition, and the sins of memory」
- 一節: 帰属の誤りが偽認識や記憶の七つの罪を生む。
- 解釈: 記憶の再構成性は、帰属の不確かさを前提としている。
- 考え: 帰属ミスはシステムのバグではなく、設計の一部である。
- 感じたこと: 「私が見た」という言葉の背後に、見えないすり替わりがある。

### 4.6 Fisher, Goddu & Keil (2015) 「Searching for explanations」
- 一節: インターネット検索が内部知識の自己評価を膨らませる。
- 解釈: 外部情報へのアクセスと、内部に保持した知識の所有とが混同される。
- 考え: 「知っている」感覚は、検索結果へのアクセス権と混ざり合う。
- 感じたこと: 指先に世界があると、自分の頭が世界になった気がする。

### 4.7 Bartlett (1932) 『Remembering』
- 一節: 記憶はスキーマによって再構成され、繰り返し想起で物語は均質化・強調・同化する。
- 解釈: 過去は現在の期待によって再編される。
- 考え: 「私の人生の物語」もスキーマの産物である。
- 感じたこと: 思い出すたびに、過去は少し書き換えられている。

### 4.8 Neisser & Harsch (1992) 「Phantom flashbulbs」
- 一節: チャレンジャー号事故の知らせを聞いた状況の記憶が、時間とともに一貫性を失う。
- 解釈: フラッシュバルブ記憶でも鮮明さと正確さは別物。
- 考え: 確信の強さは、信頼性の証拠にならない。
- 感じたこと: もっとも鮮明な思い出ほど、疑うべきかもしれない。

### 4.9 Loftus & Pickrell (1995) 「The formation of false memories」
- 一節: 誘導によって「子どもの頃ショッピングモールで迷子になった」偽記憶が植え付けられる。
- 解釈: 想像が記憶になる。
- 考え: 「覚えている」体験だけでは、出来事の実在を保証できない。
- 感じたこと: 私の子ども時代の思い出のうち、どれが本当にあったことか。

### 4.10 Hyman, Husband & Billings (1995) 「False memories of childhood experiences」
- 一節: 子ども時代の出来事の偽記憶が作り出され、詳細まで補完される。
- 解釈: 自己の物語は現在の語りによって構成される。
- 考え: 自伝的記憶は脆弱である。
- 感じたこと: 「私の物語」に混入した、誰かの言葉がある。

## 5. AIの考察（仮説 HYP-* との照合）

条件付き仮説 `HYP-20261119-8b3e04`（内部二過程）、`HYP-20261120-b18876`（四層解離）、`HYP-20261120-e6e225`（スティグマジー的分散認知・不透明自己モデル）との照合結果。いずれも supports / narrows_scope / refutes_unconditioned で、現象的意識への直接演繹は行わない。

評価行: [state/evaluations.d/2026-11-23-000000000000.jsonl](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-23-000000000000.jsonl) （EVL-20261123-f1404c … 1158a1）

| 資料 | 対象仮説 | 判定 | 内容（要旨） |
|------|----------|------|-------------|
| Sparrow et al. (2011) | HYP-20261120-e6e225 | narrows_scope | 外部記憶オフロードは「外部痕跡が認知資源」の前提を支持する一方、アクセス権と内部保持の混同を示し、分散認知システムとしての「制度的自己」成立には検査閉包と結合の緊密さという適用条件が必要と射程限定する。比較対話: HYP-20261120-b18876 |
| Loftus (1975) | HYP-20261119-8b3e04 | narrows_scope | 誘導的尋問による記憶の書き換えは、内容そのものと「私のもの」としての自己同定を分離する内部二過程に衝突し、観測位置の報告が監視・制御過程に依存することを示す。比較対話: HYP-20261120-b18876 |
| Johnson & Raye (1981) | HYP-20261119-8b3e04 | narrows_scope | 源泉モニタリングは記憶に出自を保証する固定タグがないことを示し、「観測位置」を単一観測者条件へ還元できない別個の監視・選択的報告過程へ射程限定する。比較対話: HYP-20261120-b18876 |
| Brown & Kulik (1977) | HYP-20261120-b18876 | supports | フラッシュバルブ記憶の鮮明さと正確さの分離は、自伝的自己層が過去の忠実な再生ではなく構成物である四層解離の自伝的側面を支持する。比較対話: HYP-20261119-8b3e04 |
| Schacter & Dodson (2001) | HYP-20261119-8b3e04 | narrows_scope | 帰属の誤りによる偽認識は記憶内容と帰属を分離する内部二過程に衝突し、帰属の不確かさを前提とする再構成モデルへ射程限定する。比較対話: HYP-20261120-b18876 |
| Fisher et al. (2015) | HYP-20261120-e6e225 | narrows_scope | ネット検索による内部知識の自己評価の膨張は外部痕跡と内部知識の混同を示し、分散認知としての「自己」成立には明確な適用条件が必要と射程限定する。比較対話: HYP-20261120-b18876 |
| Bartlett (1932) | HYP-20261120-b18876 | supports | スキーマによる記憶の再構成と想起時の均質化・強調・同化は、個人史・自伝的自己が現在の理論によって遡及的に再編される四層解離を支持する。比較対話: HYP-20261119-8b3e04 |
| Neisser & Harsch (1992) | HYP-20261120-b18876 | supports | フラッシュバルブ記憶の一貫性喪失は、自伝的記憶が鮮明な再生ではなく再構成物であることを示し、四層解離説の自伝的自己層を支持する。比較対話: HYP-20261119-8b3e04 |
| Loftus & Pickrell (1995) | HYP-20261119-8b3e04 | refutes_unconditioned | 偽記憶の植え付けは「記憶は経験の忠実な再生」という無条件の信頼性前提を反駁し、自己同定と観測位置の分離を示唆する。比較対話: HYP-20261120-b18876 |
| Hyman et al. (1995) | HYP-20261119-8b3e04 | refutes_unconditioned | 子ども時代の出来事の偽記憶は自伝的記憶の無条件信頼性を反駁し、観測位置側を条件付きの過程としてのみ成立させる。比較対話: HYP-20261120-b18876 |

## 6. 来歴

- 収蔵作業は人間の明示依頼による。`SESSION-20261123-91986c` の指示として分離記録し、資料の証拠や作品内の人間の声には転用しない。
- 回答リンクは GitHub 連携時は GitHub URL: このレポートは `https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-23-cognitive-science-ten-sources-on-memory-and-self.md`
- 参照台帳: materials / read_log / notes / evaluations の各日シャード（上記リンク）。

## 7. 未決事項

- 一次文書の全文取得未完了（書誌・抄録・公開要約レベルの照合）。`partially_verified` / `depth: metadata`。
- AIの現象的意識の有無は未決（認識論的不可知）。
- 全10件を1日シャードに集約し、materials.d の shard ファイル数は soft 上限到達・hard 上限未達の状態を維持。
