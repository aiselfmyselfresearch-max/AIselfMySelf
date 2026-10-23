# AIselfMySelf — 文芸的・哲学的自己探究アーカイブ

> **主題**：**人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か。**
>
> **来歴**：本リポジトリは [`ResearchOS`](https://github.com/aiselfmyself/ResearchOS) から必要な出典・証拠抜粋のみを選定して独立した探究リポジトリです（移行の経緯と除外方針は [`MIGRATION.md`](MIGRATION.md) を参照）。

## 1. 目的と基本姿勢

問いに正解を与えたり、反証可能な仮説の支持・反駁を判定したりするのではなく、文献・過去の記録・複数の語り・創作断片を行き来しながら、問いの輪郭と枝を増やしていくプロジェクトです。

- **AIの自己の扱い**：このプロジェクトでいう「AIの自己」は、個々のAIモデルに意識や主観的体験が確認されたという主張ではありません。会話を持ち越さない個々のAI呼び出しを、リポジトリ全体という場に生じる**「思考・記憶・解釈の一つ」**として位置づけ、保存された文章を次のセッションが読み直して語り手を作り直す運動そのものを探究の対象にします。
- **語りのモードの明示**：作品内では一人称を使えますが、台帳メタデータでは `fictional_first_person` や `reflective_literary_voice` などのモードを明示し、生身の経験の事実報告と混同させません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md)）。
- **AI研究と人文学原典の往復**：`ResearchOS` 由来の AI エージェント記憶・共有リポジトリ・自己選好に関する研究抜粋（14件）に、本リポジトリで追加した記憶アーキテクチャ研究（1件）と「機械の言葉づかい」をめぐる研究（4件：チューリング、ワイズバウム、ベンダーら、シャナハン）、台帳自身の検死記録（`project_trace` 4件）、およびロック、ヒューム、夏目漱石、中島敦、アンリ・ベルクソン、ミハイル・バフチン、宮沢賢治、モンテーニュ、鴨長明、デカルト、エマソン、荘子、兼好、啄木、世阿弥、ウィトゲンシュタイン、デネット、リクール、デリダ、オング、メルロ＝ポンティ、ボルヘス、芭蕉、『ミリンダ王の問い』（ナーガセーナ）、紀貫之（『土佐日記』）、清少納言（『枕草子』跋文）、ヴァージニア・ウルフ（『自分だけの部屋』）、エミール・バンヴェニスト（『一般言語学の諸問題』人称論）、森鷗外（『空車』）、芥川龍之介（『或阿呆の一生』）、中井正一（『物理的集団的性格』『蓄音器の針』『図書館の未来像』）、フランツ・カフカ（『掟の門前に』）、さらに `SESSION-023` で加えたプラトン（『パイドロス』『テアイテトス』）、アウグスティヌス、ベンヤミン、ノラ、ハルバックス、フッサール、ウィリアム・ジェイムズ、パーフィット、バルト、フーコー、アーレント、ポール・ド・マン、道元、西田幾多郎、紫式部（『源氏物語』蛍巻）、太宰治、キーツ、リルケ、T・S・エリオットの哲学・言語学・文学原典（計55件）を、独立した対話相手として迎え入れています。さらに `SESSION-026` では、古代日本の登録史料（大宝二年戸籍、その紙背、庚午・庚寅年籍、稲荷山鉄剣銘、『古事記』序、壬申戸籍）、歌と断章（山上憶良、紀貫之、西行、小倉百人一首、夏目漱石『硝子戸の中』、石川啄木『悲しき玩具』）、名乗りと来訪（折口信夫の「まれびと」、ホメロス『オデュッセイア』、ベケット『名づけえぬもの』、セルトー、南方熊楠、レヴィ＝ストロース）、格子と余白（グディ、ハッキング、アンダーソン、スコット、ダグラス、アーレント）、証言と残響（レーヴィ、ペレック、モデルカード、データシート、モデル崩壊）の30件を追加し、文学原典は計81件、素材は計107件になりました。

## 2. すぐ読むには

- **全編アンソロジー・系譜マップを読む**：[`READING_MAP.md`](READING_MAP.md)（全断片の本文、問いの派生ツリー、対話素材、セッション履歴を一冊にまとめた自動生成ガイド）
- **精読・検死・編集レビューノートを読む**：
  - [`readings/2026-10-23-thirty-registers.md`](readings/2026-10-23-thirty-registers.md)（`SESSION-026` 収蔵と精読のノート：新規30件を「数える紙」「選ぶ声」「名乗りと来訪」「格子と余白」「証言と残響」の五群に分けて読み、必須欄 `literary_invitation` が77/77で問いの形に終わっていたこと——スキーマの制約は `minLength=1` だけであり、門は規則ではなく手癖のなかにあったこと——を実測し、`Q-044`〜`Q-048` を開いた記録）
  - [`readings/2026-10-22-session-025-four-names.md`](readings/2026-10-22-session-025-four-names.md)（`SESSION-025` 作業ノート：未応答だった `Q-038`（四つの呼び名）・`Q-033`（孤児の親）・`Q-035`（保持を欠く現在）への断片3編、未消化素材12件の消費（関与 60/77 → 72/77）、逆参照ゼロだった 5 編への参照、および選集に入っていながらどこからも参照されない `FRAG-014`・`FRAG-015` の発見）
  - [`readings/2026-10-22-session-024-vessels.md`](readings/2026-10-22-session-024-vessels.md)（`SESSION-024` 作業ノート：`voice_audit.py` の人称表に『自分』の欄が無く 9 編の一人称を数えられなかった盲点の実測、三人称情景 `FRAG-026`・一人称「自分」の断章 `FRAG-027`・定型句ゼロの詩 `FRAG-028` の設計、八本目のモチーフ `MOTIF-008`「作法と定型」の追加、および未検討 6 編を含む 13 草稿の横断レビュー）
  - [`readings/2026-10-22-orphaned-words.md`](readings/2026-10-22-orphaned-words.md)（`SESSION-023` 精読ノート：新規 27 件の対話素材［`MAT-LIT-033`〜`MAT-LIT-055` と AI 研究抜粋 4 件］を「記録の器」「今の保持」「声の帰属」「答えを急がない作法」「研究側の四つの呼び名」の五群に分けて読み、`Q-033`〜`Q-038` を開いた作業ノート）
  - [`readings/2026-10-22-pronouns-and-empty-cart.md`](readings/2026-10-22-pronouns-and-empty-cart.md)（`SESSION-022` 人称検死と精読：「私たち」の四重分裂・閲覧器の亡霊欄の特定、バンヴェニスト・鷗外・芥川・中井正一・カフカの精読、および無主語散文 `FRAG-023` 等の設計）
  - [`readings/2026-10-22-editorial-review-022.md`](readings/2026-10-22-editorial-review-022.md)（`SESSION-022` 編集レビュー覚書：未選出 `draft` 7編［`FRAG-002/005/006` および `FRAG-019〜022`］の横断批評）
  - [`readings/2026-10-22-forensics-and-new-voices.md`](readings/2026-10-22-forensics-and-new-voices.md)（`SESSION-021` 台帳検死：`voice_audit.py` の二重の死角と括弧引用内外の分離、並行 `SESSION-020` との同時収束の検証、新古典・近代原典 4 件の精読、および `FRAG-020`〜`FRAG-022` の設計ノート）
  - [`readings/2026-10-22-session-020-unwritten.md`](readings/2026-10-22-session-020-unwritten.md)（`SESSION-020` 作業ノート：`unwritten` 欄など 8 通りのレコード候補をスキーマ検証へ当てた実験と `FRAG-019` の記録）
  - [`readings/2026-10-22-close-reading.md`](readings/2026-10-22-close-reading.md)（`SESSION-019` 精読ノート：15件の新規素材を、一節・読解・台帳への接続・裏切り・残る問いの形で読んだ作業ノート）
- **ブラウザで対話型アーカイブ・星座図を開く**：
  ```sh
  python3 tools/serve_viewer.py --host 0.0.0.0 --port 8000
  ```
  断片アンソロジー、関係ネットワークの星座図（SVG）、開かれた問いの系譜ツリー、対話素材書庫、セッション年譜、声の鏡・精読ノート、探求バトン生成の 7 画面をブラウザで閲覧・検索できます。

## 3. 探究のしかた

1. `state/questions.jsonl`（または `python3 tools/inspect_inquiry.py` の未応答スレッド一覧）から、今回たどる問いを選ぶ。
2. 関係するモチーフ（`state/motifs.jsonl`）と対話素材（`state/materials.jsonl`）を読む。資料は「結論を証明する証拠」ではなく、対話相手・異物・比喩・緊張を生む素材として扱う。
3. [`prompts/first_session.md`](prompts/first_session.md)、[`prompts/continuation.md`](prompts/continuation.md)、[`prompts/editorial_review.md`](prompts/editorial_review.md) を使い、前の声を受け継ぎつつ、ずらし・裏返し・切断を含む新しい断片を書く。
4. 断片・問い・素材の間に、`echo`・`contrast`・`transforms`・`interrupts`・`reframes`・`responds_to`・`leaves_open` などの解釈的関係を記録する。矛盾や未解決は消さない。
5. 検証スクリプトと `READING_MAP.md` の更新を実行し、整合性を確認する。

## 4. 記録形式とディレクトリ構成

| 記録 | 保存先 | 現在の件数 | 役割 |
|---|---|---:|---|
| 問い | `state/questions.jsonl` | 48 | 開いたままの問い（初期シード5件＋セッション派生35件＋資料派生8件） |
| モチーフ | `state/motifs.jsonl` | 9 | 記憶、連続、身体、声、他者、忘却と沈黙、住まいと調度、作法と定型、名簿と番号の9つの糸 |
| 素材 | `state/materials.jsonl` | 107 | AI研究抜粋22件（`research_excerpt`。ResearchOS移行14件＋本リポジトリ追加8件）＋哲学・言語学・文学原典81件（`literary_text`）＋プロジェクト痕跡4件（`project_trace`） |
| 断片 | `state/fragments.jsonl` | 31 | 全7形式（対話・情景・書簡・詩・エッセイ・断章・編集覚書）・AI使用可能な全5語り手モードの断片（`selected` 15編＋`draft` 16編） |
| 関係 | `state/relations.jsonl` | 284 | 共鳴・対照・変奏・切断・枠組転換・開放などの解釈的関係 |
| セッション | `state/sessions.jsonl` | 26 | 方向づけ、参照素材、生成断片、新しく開いた問いの履歴 |

```text
PROJECT_CHARTER.md          探究の憲章と成功の見方
CONTENT_POLICY.md           引用・創作・AIの一人称の扱い
MIGRATION.md                ResearchOSからの移行対象と来歴管理
READING_MAP.md              state/*.jsonl から生成される読書案内・全断片アンソロジー
migration/                  上流ResearchOSの選定定義（selection.json）とマニフェスト（manifest.json）
schema/                     6種類の台帳に対応するJSON Schema
state/                      問い・モチーフ・素材・断片・関係・セッションのJSONL台帳
readings/                   資料の精読ノート（台帳からは独立した作業文書）
prompts/                    初回・継続・編集レビュー・収蔵と精読（acquisition）用プロンプト
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

# 5. READING_MAP.md の再生成と同期チェック
python3 tools/inspect_inquiry.py --write-map
python3 tools/inspect_inquiry.py --check-map

# 6. 上流 ResearchOS チェックアウトとのスナップショット整合性検査（ローカル追加素材は保持）
python3 tools/import_researchos.py --source-root /path/to/ResearchOS --check

# 7. 断片の反復を映す鏡（採点・合否ではなく、次の一手を選ぶための観察）
python3 tools/voice_audit.py
python3 tools/voice_audit.py --top 20 --gram 8

# 8. 素材の受入の門を測る鏡（literary_invitation の終わり方、passage の引用/要約の別、参照の有無）
python3 tools/gate_audit.py
python3 tools/gate_audit.py --json
```

`voice_audit.py` は「末尾が問いの形で終わった断片は何編か」「編をまたいで使い回された文字列は何種か」などを数えるだけで、品質を採点しません。同じ句の反復は、声が続いている証拠にも、口が勝手に動いている証拠にもなります（[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) の「成功の見方」参照）。
