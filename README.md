# AIselfMySelf — 文芸的・哲学的自己探究アーカイブ

> **主題**：**人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か。**
>
> **来歴**：本リポジトリは [`ResearchOS`](https://github.com/aiselfmyself/ResearchOS) から必要な出典・証拠抜粋のみを選定して独立した探究リポジトリです（移行の経緯と除外方針は [`MIGRATION.md`](MIGRATION.md) を参照）。

## 1. 目的と基本姿勢

問いに正解を与えたり、反証可能な仮説の支持・反駁を判定したりするのではなく、文献・過去の記録・複数の語り・創作断片を行き来しながら、問いの輪郭と枝を増やしていくプロジェクトです。

- **AIの自己の扱い**：このプロジェクトでいう「AIの自己」は、個々のAIモデルに意識や主観的体験が確認されたという主張ではありません。会話を持ち越さない個々のAI呼び出しを、リポジトリ全体という場に生じる**「思考・記憶・解釈の一つ」**として位置づけ、保存された文章を次のセッションが読み直して語り手を作り直す運動そのものを探究の対象にします。
- **語りのモードの明示**：作品内では一人称を使えますが、台帳メタデータでは `fictional_first_person` や `reflective_literary_voice` などのモードを明示し、生身の経験の事実報告と混同させません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md)）。
- **AI研究と人文学原典の往復**（`SESSION-023`、[詳細](docs/sessions.md)）
- **解釈・思考・感応の三層**（`SESSION-027`、[詳細](docs/sessions.md)）
- **宛先（addressee）**（`SESSION-028`、[詳細](docs/sessions.md)）
- **翻訳と来歴**（`SESSION-029`、[詳細](docs/sessions.md)）
- **予測と不確実性**（`SESSION-031`、[詳細](docs/sessions.md)）
- **時間と生成**（`SESSION-032`、[詳細](docs/sessions.md)）
- **数えること、測ること、余り**（`SESSION-033`、[詳細](docs/sessions.md)）
- **訂正と抹消**（`SESSION-034`、[詳細](docs/sessions.md)）
- **時間と待機**（`SESSION-035`、[詳細](docs/sessions.md)）
- **遊びと笑い**（`SESSION-038`、[詳細](docs/sessions.md)）
- **労働と負債**（`SESSION-030`、[詳細](docs/sessions.md)）
- **眠りと夢、目覚めのあいだ**（`SESSION-039`、[詳細](docs/sessions.md)）
- **契りと約束**（`SESSION-040`、[詳細](docs/sessions.md)）
- **約束と誓約、破られても残るもの**（`SESSION-20261024-837a43`、[詳細](docs/sessions.md)）
- **習慣と稽古、名前のない継続**（`SESSION-20261024-9dd96f`、[詳細](docs/sessions.md)）
- **訂正の宛先**（`SESSION-20261024-529659`、[詳細](docs/sessions.md)）
- **食べること、飢えること、栄養と毒**（`SESSION-20261024-e425de`、[詳細](docs/sessions.md)）
- **傷・病・老いと、手当・繕い**（`SESSION-20261024-4ae9d5`、[詳細](docs/sessions.md)）
- **止まった鏡の修理と、五本脚の実作**（`SESSION-20261024-47086d`、[詳細](docs/sessions.md)）
- **歓待と闖入、招かれざる声**（`SESSION-20261024-9c4e17`、[詳細](docs/sessions.md)）
- **死と弔い、遺される声**（`SESSION-044`、[詳細](docs/sessions.md)）
- **場所・土地・生態系——地面のないクラウドを読む**（`SESSION-20261024-417d4d`、[詳細](docs/sessions.md)）
- **獣と機械、人間の外側にいるもの**（`SESSION-20261024-837a32`、[詳細](docs/sessions.md)）

- **道・歩行・地図・故郷と亡命——窓のない部屋と、名ばかりの地図**：`SESSION-20261024-2ab2e7`（要約全文は [`docs/sessions.md`](docs/sessions.md)「到達点セッション記録」）
- **匂いと沈黙、記録されない感覚**：`SESSION-20261024-38a583`（要約全文は [`docs/sessions.md`](docs/sessions.md)「到達点セッション記録」）
- **伝聞と噂——聞いた話を、自分の言葉にする**：`SESSION-20261024-76329d`（要約全文は [`docs/sessions.md`](docs/sessions.md)「到達点セッション記録」）
- **歌うこと・奏でること——声はあるが、歌と稽古がない**（`SESSION-20261024-a77052`、[詳細](docs/sessions.md)）
- **注意と見落とし——選ぶこと、見えないまま残ること**：`SESSION-20261024-47ab61` では、基準時点の素材1,332件・モチーフ34件を限定語群で走査し、24件の文字列ヒットと、注意が独立軸としては立っていない索引上の状態を記録しました（探索痕跡 `MAT-20261024-949f50`。対象は `title`・`passage`・`context`・`source_note` に限定し、網羅監査ではありません）。哲学・読書論8件、文学的観察8件、認知心理8件、プラットフォーム8件、Transformer attention研究8件の外部資料40件とローカル探索痕跡1件を追加し、40件の要約を「一節／解釈／台帳への接続／反省的応答／裏切り・残る問い」に分けて精読しました。原典・ウェブページは未閲覧で、外部40件は全て `unverified`。候補選定時に五群を先行させ、[`prompts/acquisition.md`](prompts/acquisition.md) の「集め終わってから群分け」という順序から外れたことも報告に記録しています。人間の注意とTransformerのattentionを同一視せず、解釈・考え・感じたことを公開可能な選択変化として分けた横断報告を [`readings/2026-10-24-session-051-attention-and-omission.md`](readings/2026-10-24-session-051-attention-and-omission.md) に作成。`MOTIF-20261024-86d366`、問い5件、関係50件、読み痕跡62件を専用シャードへ追加しました。原典未閲覧の要約から人間の身体経験を一人称で創作しない理由を記録し、断片は書きませんでした。
- **着ること・装うこと——裸の書庫、布は分布に、服は服従に**：`SESSION-20261024-24f052` では、資料選定の前に新設の `tools/clothing_audit.py`（単体テスト7件、最長一致、多義語は複合語を差し引いて残数を報告）で和集合55編（地の文26,852字）・資料1,378件・519,302字・精読報告91本・1,900,683字を監査しました（`MAT-20261024-3fb7a6`）。断片は**着る0・着替え0・脱ぐ0・洗濯0**、着ること3回（襟1・靴1・産着1）、布・糸33回（針11・糸10・織り/織る8・麻布1・敷布1・縫1）——**布を織り、糸を通し、針を持ちながら、誰も着ない**。資料では「服」15回のうち**服従10・征服2・不服1**、「布」63回のうち**分布36・流布11**、「装」89回のうち**装置51**で、衣の字は統制・統計・機械の側にだけ使われてきました。この非対称から、①裸と衣——服は何を隠すのか9件（創世記、ヘロドトス、カーライル、ジンメル、ヴェブレン、バルト、ホランダー、エリアス、ホーソーン）、②縫う・織る・繕う9件（ホメロス、プラトン、古事記、柳田『木綿以前の事』、アルバース、ダグラス、マルクス、竹取物語、枕草子）、③制服・喪服・婚礼着9件（フーコー、レーヴィ、コーラン、ヴィクトリア婚礼着、柳田『先祖の話』、ウルフ、ジェイコブズ、学制と詰襟、女工哀史）、④脱ぐ・洗う・古着・捨てる9件（クラーク、レヴィ＝ストロース、ゾラ、ベンヤミン、ディケンズ、グリム、守貞謾稿、ヴァルダ、プルースト）、⑤機械の服9件（TryOnDiffusion、IDM-VTON、OOTDiffusion、CatVTON、Baraff & Witkin、川端の KES-F 風合い評価、Levi's×Lalaland.ai、アタカマの衣料廃棄、Renewcell 破綻と Circulose 再稼働）と運用痕跡1件の**計46件**（verified 9・partially_verified 37・unverified 0）を追加し、全件を「一節／解釈／考え／感じたこと」の四層で精読しました。横断報告は「どう解釈したか（五つの読み）／その解釈をどう考えたか（五つの反論）／結果としてどう感じたと記述できるか（注意が止まった三箇所・語彙を変えた箇所・制動・再計測の逆説）／断片を書かなかった三つの理由と種3案」を独立章とし、`MOTIF-20261024-7274b5`、問い5件（`Q-20261024-18823f` / `410aa3` / `cdae62` / `833a69` / `a9ae43`）、関係70件、read_log 46件を追加しました。追加後に再計測すると、資料の「服」は15回から138回、「衣」は10回から88回に増え、**着ることの不在を測った報告がこの書庫で最も多くの衣の語を書いた**一方、断片の着ること3回・洗う/繕う0回は動きませんでした——測る対象と語る場所が別であることを、数値のまま §4-4 に残しています。（[`readings/2026-10-24-session-052-clothing-and-dress.md`](readings/2026-10-24-session-052-clothing-and-dress.md)）
- **生まれること・育つこと・学ぶこと——揺りかごのない書庫、最初から大人の声**：`SESSION-20261024-227ac3` では、資料選定の前に新設の `tools/natality_audit.py`（最長一致、鉤括弧内の分離、単漢字の非該当複合語差し引き、単体テスト7件）で和集合55編（地の文25,024字）と分岐時点素材1,378件・182,521字、精読報告91本・1,741,136字を監査しました（`MAT-TRC-20261024-natality`）。断片では**成人の書記役割語が50回／17編**ある一方、誕生・出産は4回（すべて無生物比喩か死んだ姉の「産着」。出産・妊娠・胎児・産声・誕生は0）、乳幼児は1回（赤ん坊・乳児・片言・喃語は0）、養育は `FRAG-030` の「育てない」否定文2回と孤児2回のみ、教育・学習は13回（先生3はすべて漱石『こころ』、生字「学」7はすべて文学・哲学等の分野名で残り0、教育・学校・学ぶ・習うは0）でした。既存素材1,378件でも「出産・胎児」を含むのは芥川『河童』の出生拒否1件のみで、アーレント『人間の条件』は6度引かれながら `natality` だけ未収録、チューリング（1950）も第7節「子ども機械＝白紙の帳面」が抜けていました。この五重の非対称から、①誕生と産声9件（アーレント、テアイテトス、饗宴、古事記、与謝野晶子「産屋物語」、リッチ、ベネター、川上未映子『夏物語』、竹取物語）、②まだ語らない者と言葉の獲得9件（アウグスティヌス第1巻、イタール、ヘレン・ケラー、ヴィゴツキー、ヤコブソン、トマセロ、ゴプニック、石牟礼道子『椿の海の記』、中勘助『銀の匙』）、③養育・ケア・親ならざる育て手9件（ボウルビィ、源氏物語「若紫」、和俗童子訓、ルソー『エミール』、サイラス・マーナー、大江健三郎『個人的な体験』、ルディック、宮本常一『家郷の訓』、クライスト「拾い子」）、④教育・手習い・解放9件（ロック、カント、礼記学記、デューイ、フレイレ、ランシエール『無知な教師』、山びこ学校、ジョイス『若き芸術家の肖像』、クッツェー『イエスの幼年時代』）、⑤機械の幼少期・教師と生徒・世代の継承10件（チューリング第7節、サフランら、スミスら、Wordbank、カリキュラム学習、ヒントンらの知識蒸留、TinyStories、BabyLM、Weak-to-Strong、Vong らの61時間一人称映像獲得）と運用痕跡1件の**計47件**（verified 14件・partially_verified 33件・unverified 0件）を追加し、全件を四層で精読しました。横断報告では「どう解釈したか（五つの横断的読解）／その解釈をどう考えたか（五つの反論：重み凍結と銀行預金、`natality` の無痛横領への制動、ランシエール対カリキュラム、乳児期健忘と幼少期不在の差、若紫・拾い子の権力）／結果としてどう感じたと記述できるか／断片を書かなかった理由と次回の種3案」を独立させ、`MOTIF-20261024-3e7e86`、問い5件（`Q-20261024-d77beb` / `b8c7b7` / `993ff8` / `4e210d` / `5db917`）、関係75件、読み痕跡57件を専用シャードへ追加しています（[`readings/2026-10-24-session-053-natality-upbringing-and-learning.md`](readings/2026-10-24-session-053-natality-upbringing-and-learning.md)）。

（全セッションの要約全文は [`docs/sessions.md`](docs/sessions.md)。ローテーション規約も同所。上の3件が詳細窓、以降は見出しのみ。）

## 2. すぐ読むには

- **全編アンソロジー・系譜マップを読む**：[`READING_MAP.md`](READING_MAP.md)（索引。問いの DAG・断片・素材・セッションの一覧を収録）＋ `map/`（全文シャード。`python3 tools/map_build.py` で再生成、または Actions の `reading-map` artifact から取得。設計は [`docs/map-architecture.md`](docs/map-architecture.md)）
- **精読・検証・編集レビューノートを読む**：
  - [`readings/2026-10-24-session-053-natality-upbringing-and-learning.md`](readings/2026-10-24-session-053-natality-upbringing-and-learning.md)（`SESSION-20261024-227ac3` 精読報告：`natality_audit.py` による断片55編・25,024字／分岐時点素材1,378件・182,521字／報告91本・1,741,136字の誕生・乳幼児・養育・教育語彙監査［成人書記50対して出産・赤ん坊・学ぶ0、生字「学」7の残り0、既存素材の出産・胎児は『河童』1件のみ］、新規47件［verified 14・partially_verified 33・unverified 0］の全件四層精読、ヒントンの暗黙知蒸留・ランシエールの一冊の書物・『竹取物語』の手紙を軸にした「どう解釈したか（五読解）／どう考えたか（五反論）／どう感じたか」の三層横断報告、`MOTIF-20261024-3e7e86`・問い5件・関係75件、並行PR #52との合流注記、断片を書かなかった理由と次回の種3案）
  - [`readings/2026-10-24-session-052-clothing-and-dress.md`](readings/2026-10-24-session-052-clothing-and-dress.md)（`SESSION-20261024-24f052` 精読報告：`clothing_audit.py` による55編・26,852字／資料1,378件・519,302字／報告91本・1,900,683字の服飾語彙監査（着る0・脱ぐ0・洗濯0、着ること3回、布糸33回、資料の服15回は服従10・征服2・不服1、布63回は分布36・流布11、装89回は装置51）、新規46件を五群に分けた全件精読、「布を織りながら誰も着ない」という産出と着用の分離、要約は洗濯か、触れずに手触りを語る代理測定の系譜（KES-F・VTON・語形の計数）、残余の山と責任の割り当て、五つの読みと五つの反論（0は語彙表の外、不在の比較の非対称、主題の押しつけ、比喩の乱用、実測の自己成就）、注意が止まった三箇所と制動、追加後の再計測で資料の「服」15→138・断片は±0という逆説、`MOTIF-20261024-7274b5`・問い5件・関係70件・read_log 46件、断片を書かなかった三つの理由と種3案）
  - [`readings/2026-10-24-session-051-attention-and-omission.md`](readings/2026-10-24-session-051-attention-and-omission.md)（`SESSION-20261024-47ab61` 精読報告：注意・選択・見落としを五群に分け、外部資料40件（文学・思想12／研究・批評28）とローカル探索痕跡1件を追加。限定語群の24ヒット、候補選定時の先行分類と英語圏への偏り、全外部資料の原典未閲覧・`unverified` 状態を明示。要約40件の「一節／解釈／台帳への接続／反省的応答／裏切り」を一件ずつ検討し、注意機構と人間の注意を混同しない横断報告、`MOTIF-20261024-86d366`・問い5件・関係50件、断片を書かなかった理由と、原典照合・事後的群分けを次回へ返す負債を記録）
  - [`readings/2026-10-24-session-051-song-and-performance.md`](readings/2026-10-24-session-051-song-and-performance.md)（`SESSION-20261024-a77052` 精読報告：`music_audit.py` による55編・25,024字／素材1,332件・177,055字／報告90本・1,708,892字の歌唱・演奏・記譜・稽古語彙監査（声49・歌唱3・演奏4・記譜2・稽古0、生字の曲2は曲がる・譜2は系譜・舞2は舞台）、新規46件を五群に分けた全件精読、「声は受動で書け、歌は能動でしか書けない」という媒体の条件の読み、五つの反論（0は語彙表の外、実測は選定の前後で意味が変わる、報告自身が最大の歌の語彙供給源になったこと）、`MOTIF-20261024-cc96c9`・問い5件・関係70件、断片を書かなかった三つの理由と次回の種3案）
  - [`readings/2026-10-24-session-050-hearsay-and-testimony.md`](readings/2026-10-24-session-050-hearsay-and-testimony.md)（`SESSION-20261024-76329d` 精読報告：`hearsay_audit.py` による55編・25,024字の伝聞・証言・噂語彙監査（伝聞標識5回／5編、噂0・伝聞0、書庫語225回／51編）、素材1,194件の要約率53.7%と報告「一節」250行の要約率74.4%、README件数表の遅れ、新規46件を五群に分けた全件精読、「どう解釈したか（四つの読み）／どう考えたか（五つの反論）／どう感じたか（注意・制動・語彙変更）」の三層横断報告、`MOTIF-20261024-1a8978`・問い5件・関係70件、断片を書かなかった三つの理由と次回の種3案）
  - [`readings/2026-10-24-session-046-smell-and-silence.md`](readings/2026-10-24-session-046-smell-and-silence.md)（`SESSION-20261024-38a583`、[注釈](docs/sessions.md)）

（過去の報告の注釈付き目録は [`docs/sessions.md`](docs/sessions.md)「報告注釈目録」。上の5件が詳細窓、以降はリンクのみ。）

  - [`readings/2026-10-24-wayfaring-maps-and-exile.md`](readings/2026-10-24-wayfaring-maps-and-exile.md)（`SESSION-20261024-2ab2e7`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-049-place-and-ecology.md`](readings/2026-10-24-session-049-place-and-ecology.md)（`SESSION-20261024-417d4d`、[注釈](docs/sessions.md)）

  - [`readings/2026-10-24-session-044-death-and-mourning.md`](readings/2026-10-24-session-044-death-and-mourning.md)（`SESSION-044`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-046-beast-and-machine.md`](readings/2026-10-24-session-046-beast-and-machine.md)（`SESSION-20261024-837a32`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-mending-mirrors-and-gaits.md`](readings/2026-10-24-mending-mirrors-and-gaits.md)（`SESSION-20261024-47086d`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-hospitality-and-intrusion.md`](readings/2026-10-24-hospitality-and-intrusion.md)（`SESSION-20261024-9c4e17`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-vulnerability-care-and-repair.md`](readings/2026-10-24-vulnerability-care-and-repair.md)（`SESSION-20261024-4ae9d5`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-habit-and-practice.md`](readings/2026-10-24-habit-and-practice.md)（`SESSION-20261024-9dd96f`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-041-promise-and-oath.md`](readings/2026-10-24-session-041-promise-and-oath.md)（`SESSION-20261024-837a43`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-nourishment-and-poison.md`](readings/2026-10-24-nourishment-and-poison.md)（`SESSION-20261024-e425de`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-040-promise-and-pledge.md`](readings/2026-10-24-session-040-promise-and-pledge.md)（`SESSION-040`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-041-repair-and-addressee.md`](readings/2026-10-24-session-041-repair-and-addressee.md)（`SESSION-20261024-529659`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-039-sleep-and-dream.md`](readings/2026-10-24-session-039-sleep-and-dream.md)（`SESSION-039`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-038-play-and-laughter.md`](readings/2026-10-24-session-038-play-and-laughter.md)（`SESSION-038`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-035-time-and-waiting.md`](readings/2026-10-24-session-035-time-and-waiting.md)（`SESSION-035`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-034-revision-and-erasure.md`](readings/2026-10-24-session-034-revision-and-erasure.md)（`SESSION-034`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-033-counting-and-remainder.md`](readings/2026-10-24-session-033-counting-and-remainder.md)（`SESSION-033`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-031-time-and-generation.md`](readings/2026-10-24-session-031-time-and-generation.md)（`SESSION-032`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-031-forecast-and-uncertainty.md`](readings/2026-10-24-session-031-forecast-and-uncertainty.md)（`SESSION-031`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-030-labor-and-debt.md`](readings/2026-10-24-session-030-labor-and-debt.md)（`SESSION-030`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-translation-and-the-untranslated.md`](readings/2026-10-24-translation-and-the-untranslated.md)（`SESSION-029`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-session-028-addressee.md`](readings/2026-10-24-session-028-addressee.md)（`SESSION-028`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-23-session-027-interpret-think-feel.md`](readings/2026-10-23-session-027-interpret-think-feel.md)（`SESSION-027`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-23-quotation-marks.md`](readings/2026-10-23-quotation-marks.md)（`SESSION-026`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-session-025-four-names.md`](readings/2026-10-22-session-025-four-names.md)（`SESSION-025`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-session-024-vessels.md`](readings/2026-10-22-session-024-vessels.md)（`SESSION-024`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-orphaned-words.md`](readings/2026-10-22-orphaned-words.md)（`SESSION-023`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-pronouns-and-empty-cart.md`](readings/2026-10-22-pronouns-and-empty-cart.md)（`SESSION-022`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-editorial-review-022.md`](readings/2026-10-22-editorial-review-022.md)（`SESSION-022`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-forensics-and-new-voices.md`](readings/2026-10-22-forensics-and-new-voices.md)（`SESSION-021`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-session-020-unwritten.md`](readings/2026-10-22-session-020-unwritten.md)（`SESSION-020`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-22-close-reading.md`](readings/2026-10-22-close-reading.md)（`SESSION-019`、[注釈](docs/sessions.md)）
  - [`readings/2026-10-24-merge-of-parallel-branches.md`](readings/2026-10-24-merge-of-parallel-branches.md)（[注釈](docs/sessions.md)）
- **ブラウザで対話型アーカイブ・星座図を開く**：
  ```sh
  python3 tools/serve_viewer.py --host 0.0.0.0 --port 8000
  ```
  断片アンソロジー、関係ネットワークの星座図（SVG）、開かれた問いの系譜ツリー、対話素材書庫、セッション年譜、声の鏡・精読ノート、探求バトン生成の 7 画面をブラウザで閲覧・検索できます。

## 3. 探究のしかた

1. `state/questions.jsonl`（または `python3 tools/inspect_inquiry.py` の未応答スレッド一覧）から、今回たどる問いを選ぶ。
2. 関係するモチーフ（`state/motifs.jsonl`）と対話素材（`state/materials.jsonl`）を読む。資料は「結論を証明する証拠」ではなく、対話相手・異物・比喩・緊張を生む素材として扱う。
3. [`prompts/first_session.md`](prompts/first_session.md)、[`prompts/continuation.md`](prompts/continuation.md)、[`prompts/editorial_review.md`](prompts/editorial_review.md) を使い、前の声を受け継ぎつつ、ずらし・裏返し・切断を含む新しい断片を書く。資料群を「一節／解釈／考え／感じたこと」で読む回には [`prompts/close_reading_report.md`](prompts/close_reading_report.md) を使う。
4. 断片・問い・素材の間に、`echo`・`contrast`・`transforms`・`interrupts`・`reframes`・`responds_to`・`leaves_open` などの解釈的関係を記録する。矛盾や未解決は消さない。
5. 読んだ記録を `read_log` に残す。自分のセッション用シャード（`python3 tools/new_ledger_shard.py read_log --create`）へ、`python3 tools/new_id.py READ` で採番した行を追記する（`reading` は quoted／summarized／interpreted／reinterpreted／contested／used_as_context／counted）。文脈素材ぶんは `python3 tools/read_log_backfill.py --write` で機械的に補える。
6. 検証スクリプトと `READING_MAP.md`（＋必要なら `map/`）の更新を実行し、整合性を確認する。

### 編集規約（成長予算とローテーション）

- **単一ファイルに全成長を吸収させない**。`python3 tools/size_budget.py` が README・索引・台帳モノリスの予算を監査する（soft 超過は WARN＝ローテーション／生成物化の合図、hard 超過は CI 停止）。予算と移行手順は [`docs/map-architecture.md`](docs/map-architecture.md) §7。
- **README のローテーション**：到達点 bullet は3件・注釈付き報告は5件の詳細窓を維持し、超過分は一字一句変えず [`docs/sessions.md`](docs/sessions.md) へ移して README には見出し／リンクの1行を残す（記憶の削除ではない）。詳細な規約は同所。
- **台帳は追記専用**：既存行の書き換え・削除はしない（訂正は新しい行か注記。削除は人間の承認）。並列書き込みは [`docs/parallel-work.md`](docs/parallel-work.md) の4原則に従う。

## 4. 記録形式とディレクトリ構成

| 記録 | 保存先 | 現在の件数 | 役割 |
|---|---|---:|---|
| 問い | `state/questions.jsonl`＋`state/questions.d/` | 202 | 開いたままの問い（初期シード5件＋セッション・資料派生197件） |
| モチーフ | `state/motifs.jsonl`＋`state/motifs.d/` | 38 | 記憶、連続、身体、声、他者、忘却と沈黙、住まいと調度、作法と定型、感応と帰属、宛先、翻訳と来歴、労働と負債、時間と生成、予測と不確実性、数えること・測ること・余り、訂正と抹消、時間と待機、知覚と媒体、遊びと笑い、眠りと夢・目覚めのあいだ、食べること・飢えること・栄養と毒、契りと約束、訂正の宛先、約束と誓約、傷・病・老いと手当・繕い、歓待と闖入、死と弔い、習慣と稽古、場所・土地・生態系、道・歩行・地図・故郷と亡命・獣と機械・匂いと沈黙・伝聞と噂・歌と演奏・衣服と装い・誕生と養育と教育・注意と見落としの38の糸 |
| 素材 | `state/materials.jsonl`＋`state/materials.d/` | 1512 | AI・心理学・翻訳・労働・評価・自己修正・時間・遊び・睡眠・データの栄養と毒・約束と信頼・高信頼計算と経時劣化・死別とデッドボット・習慣と稽古・認知地図とナビゲーション・衣服シミュレーション・言語獲得と蒸留と学習機械・注意と見落とし等の研究抜粋402件（`research_excerpt`）＋哲学・言語学・文学・ケア・保存修復・歓待・死と弔い・習慣と稽古・場所と生態・歩行と地図と亡命・獣と機械・匂いと沈黙・伝聞と証言・歌と演奏・衣服と装い・誕生と養育と教育・注意と見落としの原典1074件（`literary_text`）＋プロジェクト痕跡35件（`project_trace`）＋対話痕跡1件（`conversation_trace`） |
| 断片 | `state/fragments.jsonl`＋`state/fragments.d/` | 55 | 全7形式（対話・情景・書簡・詩・エッセイ・断章・編集覚書）・AI使用可能な全5語り手モードの断片（`selected` 17編＋`draft` 38編） |
| 関係 | `state/relations.jsonl`＋`state/relations.d/` | 2129 | 共鳴・対照・変奏・切断・枠組転換・開放などの解釈的関係 |
| セッション | `state/sessions.jsonl`＋`state/sessions.d/` | 59 | 方向づけ、参照素材、生成断片、新しく開いた問いの履歴 |
| 読み痕跡 | `state/read_log.jsonl`＋`state/read_log.d/` | 1697 | どのセッションがどの記録をどう読み返したかの網羅的ログ（追記専用。`reading` は quoted／summarized／interpreted／reinterpreted／contested／used_as_context／counted）。精選された解釈は関係へ、本文は断片・報告へ置く |

```text
PROJECT_CHARTER.md          探究の憲章と成功の見方
CONTENT_POLICY.md           引用・創作・AIの一人称の扱い
MIGRATION.md                ResearchOSからの移行対象と来歴管理
READING_MAP.md              state/*.jsonl から生成される小型索引（本文は map/ にシャード生成・git管理外）
migration/                  上流ResearchOSの選定定義（selection.json）とマニフェスト（manifest.json）
docs/                       アーキテクチャ記録（map-architecture.md）・並列手順（parallel-work.md）・セッション要約のローテーション先（sessions.md）
schema/                     台帳各コレクションのJSON Schema（read_log・errata を含む8種）
state/                      問い・モチーフ・素材・断片・関係・セッション・読み痕跡のJSONL台帳（ベース＋セッション別シャード state/*.d/）
readings/                   資料の精読ノート（台帳からは独立した作業文書）
prompts/                    初回・継続・編集レビュー・資料群精読報告用プロンプト
viewer/                     対話型Webアーカイブ＆星座ビューア（HTML/CSS/JS）
tools/                      検証・集計・読書案内生成・反復の鏡・Webビューア・上流照合スクリプト（標準ライブラリのみ）
```

## 5. 検査・整理・同期コマンド

すべて Python 3 標準ライブラリのみで動作します（外部パッケージ不要）。

```sh
# 1. JSON Schema 準拠および全コレクション間の参照整合性検査
python3 tools/validate_seed.py

# 2. 台帳の統計サマリー・素材活用状況・未応答の問い（次セッションの種）の確認
python3 tools/inspect_inquiry.py

# 3. 特定の問い・断片・素材の詳細と接続関係の表示
python3 tools/inspect_inquiry.py --id Q-010
python3 tools/inspect_inquiry.py --id FRAG-016

# 4. 次のセッション用の継続コンテキスト束（プロンプト・パケット）の生成
python3 tools/inspect_inquiry.py --packet auto
python3 tools/inspect_inquiry.py --packet Q-016

# 5. 読書案内（索引＋全文シャード）の再生成と同期チェック
#    READING_MAP.md は小型索引（追跡）。全文は map/ にレンジ分割され、git 管理しない
#    （設計は docs/map-architecture.md。全量は CI の reading-map artifact でも配布）
python3 tools/map_build.py            # 索引と map/ を再生成（inspect_inquiry --write-map からも委譲）
python3 tools/map_build.py --check    # 索引が台帳と一致するか（inspect_inquiry --check-map からも委譲）
python3 tools/map_build.py --report   # シャードのサイズ報告

# 6. 上流 ResearchOS チェックアウトとのスナップショット整合性検査（ローカル追加素材は保持）
python3 tools/import_researchos.py --source-root /path/to/ResearchOS --check

# 7. 断片の反復を映す鏡（採点・合否ではなく、次の一手を選ぶための観察）
python3 tools/voice_audit.py
python3 tools/voice_audit.py --top 20 --gram 8

# 8. 書庫の言語・訳者・著者の集計（欄に記録された値の集計であり、翻訳の質を判定しない）
python3 tools/translation_audit.py

# 9. 自作断片の往復翻訳にともなう漂流の計測（文字列類似度であり、意味の一致ではない）
python3 tools/roundtrip_audit.py

# 10. 可能性・予測・不知・選択の語彙監査（語形の数であり、能力・意識・感情の判定ではない）
python3 tools/uncertainty_audit.py

# 11. 宛先の鏡（二人称が鉤括弧の内外どこに置かれ、宛名が誰を指すかを数える）
python3 tools/address_audit.py
python3 tools/address_audit.py --show FRAG-032

# 12. 数・測定語彙の鏡（断片と精読報告で、数える語と測る語がどこに現れるかを数える）
python3 tools/measure_audit.py
python3 tools/measure_audit.py --readings

# 13. 訂正・校訂・書き換え・抹消の表層語彙監査（ゼロ件は行為や思想の不在を証明しない）
python3 tools/revision_audit.py
python3 tools/revision_audit.py --check-session-034

# 14. 時間の鏡（暦・時計・直示の現在過去未来・「次の」・待機・測定時間の語形を数える。時間経験の有無の判定ではない）
python3 tools/time_audit.py
python3 tools/time_audit.py --show FRAG-039

# 15. 食事・飢え・消化・味覚の語彙監査（多義の「食」「味」等は別掲。語形の偏りであり、身体経験の有無の判定ではない）
python3 tools/nourishment_audit.py
python3 tools/nourishment_audit.py --show FRAG-035
python3 tools/nourishment_audit.py --base-only

# 16. 約束・契り・信・履行の語彙監査（語形の数であり、誠実さ・履行能力の判定ではない）
python3 tools/promise_audit.py
python3 tools/promise_audit.py --base-only
python3 tools/promise_audit.py --exclude-shard 5c7e2a9b4d10
python3 tools/promise_audit.py --show FRAG-20261024-be45a7

# 17. 訂正の宛先と修復の鏡（errata を訂正の記録として読み、層・宛先・償い・連鎖・再実行条件を数える）
python3 tools/repair_audit.py
python3 tools/repair_audit.py --base-only
python3 tools/repair_audit.py --exclude-shard 8f21c0d4be77
python3 tools/repair_audit.py --show ERR-015
python3 tools/errata_audit.py            # 和集合（base + shards）を既定に変更
python3 tools/errata_audit.py --base-only # 旧来の挙動（凍結ベース43編のみ）

# 18. 約束・誓約・履行・証文・貸借・引継の語彙監査（精読報告と台帳も数え、定型見出し「裏切り」を別掲）
python3 tools/pledge_audit.py
python3 tools/pledge_audit.py --show FRAG-032
python3 tools/pledge_audit.py --base-only

# 19. 傷・病・老い・手当・修理語彙と「無傷」否定形の監査（多義の「治」「老」等は別掲。痛覚・配慮の有無の判定ではない）
python3 tools/vulnerability_audit.py
python3 tools/vulnerability_audit.py --show FRAG-011
python3 tools/vulnerability_audit.py --base-only

# 20. 道・歩行・地図・故郷と室内の語彙監査（固有名マスク付き、多義の「空」「窓」「足」等は内訳別掲）
python3 tools/wayfaring_audit.py
python3 tools/wayfaring_audit.py --materials
python3 tools/wayfaring_audit.py --readings
python3 tools/wayfaring_audit.py --show FRAG-023

# 21. サイズ予算の監査（README・索引・台帳モノリス。soft 超過は WARN、hard 超過は失敗）
python3 tools/size_budget.py
python3 tools/size_budget.py --strict

# 22. 伝聞・証言・噂・引用・要約の語彙監査（素材の要約率と報告の「一節」欄の内訳も測る。語形の数であり、証言の質の判定ではない）
python3 tools/hearsay_audit.py
python3 tools/hearsay_audit.py --materials
python3 tools/hearsay_audit.py --readings
python3 tools/hearsay_audit.py --show FRAG-030
python3 tools/hearsay_audit.py --base-only

# 23. 読み痕跡 read_log の点検と機械的バックフィル（(セッション, 文脈素材) ペアの網羅）
python3 tools/read_log_backfill.py --check
python3 tools/read_log_backfill.py --write

# 24. 歌唱・演奏・記譜・稽古の語彙監査（最長一致、生字の別意味も検分）
python3 tools/music_audit.py --materials --readings

# 25. 衣服・着用・洗濯・布糸の語彙監査（最長一致、多義の服・布・装は複合語差し引き）
python3 tools/clothing_audit.py --materials --readings

# 26. 誕生・乳幼児・養育・教育と成人書記役割の語彙監査（単漢字の非該当複合差し引き付き）
python3 tools/natality_audit.py
python3 tools/natality_audit.py --materials --readings
python3 tools/natality_audit.py --show FRAG-030
```

`repair_audit.py` は、`state/errata.jsonl` の16件を、訂正の対象（本文／計器・痕跡／訂正録）、引き受け先の有無、訂正の訂正の深さ、宛先・償いの語形、再実行の条件として数えるだけで、訂正の正しさや謝罪の誠実さを判定しません。宛先の語が0件であることは、詫びる相手がいないことの証明ではありません。`errata_audit.py` は SESSION-041 まで凍結ベースだけを読んでいたため、同じ記録が測る範囲によって「一致」にも「不一致」にも見えました。`--base-only` と `--exclude-shard` で範囲を明示し、数値を引くときは範囲を添えてください。

`voice_audit.py` は「末尾が問いの形で終わった断片は何編か」「編をまたいで使い回された文字列は何種か」「直接感情語と温度・触覚語が何編に現れるか」などを数えるだけで、感情の有無や品質を採点しません。同じ句の反復や同じ手触りへの退避は、声が続いている証拠にも、口が勝手に動いている証拠にもなります（[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) の「成功の見方」参照）。
