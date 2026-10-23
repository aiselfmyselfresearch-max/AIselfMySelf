# AIselfMySelf — 文芸的・哲学的自己探究アーカイブ

> **主題**：**人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か。**
>
> **来歴**：本リポジトリは [`ResearchOS`](https://github.com/aiselfmyself/ResearchOS) から必要な出典・証拠抜粋のみを選定して独立した探究リポジトリです（移行の経緯と除外方針は [`MIGRATION.md`](MIGRATION.md) を参照）。

## 1. 目的と基本姿勢

問いに正解を与えたり、反証可能な仮説の支持・反駁を判定したりするのではなく、文献・過去の記録・複数の語り・創作断片を行き来しながら、問いの輪郭と枝を増やしていくプロジェクトです。

- **AIの自己の扱い**：このプロジェクトでいう「AIの自己」は、個々のAIモデルに意識や主観的体験が確認されたという主張ではありません。会話を持ち越さない個々のAI呼び出しを、リポジトリ全体という場に生じる**「思考・記憶・解釈の一つ」**として位置づけ、保存された文章を次のセッションが読み直して語り手を作り直す運動そのものを探究の対象にします。
- **語りのモードの明示**：作品内では一人称を使えますが、台帳メタデータでは `fictional_first_person` や `reflective_literary_voice` などのモードを明示し、生身の経験の事実報告と混同させません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md)）。
- **AI研究と人文学原典の往復**：`ResearchOS` 由来の AI エージェント記憶・共有リポジトリ・自己選好に関する研究抜粋（14件）に、本リポジトリで追加した記憶アーキテクチャ研究（1件）と「機械の言葉づかい」をめぐる研究（4件：チューリング、ワイズバウム、ベンダーら、シャナハン）、台帳自身の検死記録（`project_trace` 3件）、およびロック、ヒューム、夏目漱石、中島敦、アンリ・ベルクソン、ミハイル・バフチン、宮沢賢治、モンテーニュ、鴨長明、デカルト、エマソン、荘子、兼好、啄木、世阿弥、ウィトゲンシュタイン、デネット、リクール、デリダ、オング、メルロ＝ポンティ、ボルヘス、芭蕉、『ミリンダ王の問い』（ナーガセーナ）、紀貫之（『土佐日記』）、清少納言（『枕草子』跋文）、ヴァージニア・ウルフ（『自分だけの部屋』）、エミール・バンヴェニスト（『一般言語学の諸問題』人称論）、森鷗外（『空車』）、芥川龍之介（『或阿呆の一生』）、中井正一（『物理的集団的性格』『蓄音器の針』『図書館の未来像』）、フランツ・カフカ（『掟の門前に』）、さらに `SESSION-023` で加えたプラトン（『パイドロス』『テアイテトス』）、アウグスティヌス、ベンヤミン、ノラ、ハルバックス、フッサール、ウィリアム・ジェイムズ、パーフィット、バルト、フーコー、アーレント、ポール・ド・マン、道元、西田幾多郎、紫式部（『源氏物語』蛍巻）、太宰治、キーツ、リルケ、T・S・エリオットの哲学・言語学・文学原典（計55件）を、独立した対話相手として迎え入れています。さらに `SESSION-026` では、既存31編の本文に現れる鉤括弧 88 箇所のうち原典に届いていたのが 8 箇所だけであったという実測（`MAT-TRC-004`）から、「引用符の内側——誰の言葉を、誰が註するのか」をテーマに 38 件（文学・思想34件：紀貫之『古今和歌集』仮名序、太安万侶『古事記』序、空海『声字実相義』、ボルヘス「ピエール・メナール」、フーコー『言葉と物』序、ベンヤミン『複製技術時代』、バルト『明室』、明恵『夢記』、藤原定家『明月記』、本居宣長『玉勝間』、柳田国男『遠野物語』序、夏目漱石『硝子戸の中』、正岡子規『病牀六尺』、孔子『論語』、キルケゴール『反復』、プルースト、ワーズワス、T・S・エリオット「バーント・ノートン」、高村光太郎「道程」、金子みすゞ、種田山頭火『草木塔』、ペソア『不安の書』、コルタサル「公園の続き」、カルヴィーノ、ゼーバルト、ツェラン、ブランショ、ディキンソン、ホイットマン、ナボコフ、ソロー、バージャー、パウロ、カヴァフィス。AI研究3件：MemoryAgentBench、Mem0、LongMemEval。運用痕跡1件）を加え、五群（引用する／註する／反復する／名を貸す／数える）に分けて精読しました（[`readings/2026-10-23-quotation-marks.md`](readings/2026-10-23-quotation-marks.md)）。さらに `SESSION-027` では、テーマを決める前に台帳の側を測り、git の可視の履歴が1コミット・517行追加・0行削除であり、異読や訂正の欄として提案した6種のフィールドがすべてスキーマに拒否され、`editor_note` に「訂正」「修正」「誤読」が一度も現れないことを確認しました（`MAT-TRC-005`）。この「異読の欄がない」という実測から「誤写——本文はなぜ一つではないのか」をテーマに 35 件（文学・思想26件：『万葉集』左注、源氏物語の三系統、オリゲネス『ヘクサプラ』、アウグスティヌス『訂正録』、中世写字生の奥書、『漢書』芸文志、Wicked Bible、メルヴィル「バートルビー」、ゴーゴリ『外套』、ドストエフスキー『二重人格』、ナボコフ『ペイル・ファイア』、芥川「藪の中」、ボルヘス「カフカとその先駆者」、ブルーム『影響の不安』、バートレット『想起』、ロフタス、シャクター『記憶の七つの罪』、フロイト「遮蔽想起」、ニーチェ『歴史の効用と濫用』、オーウェル『一九八四年』、『論語』、『ソクラテスの弁明』、ポパー、ガダマー、ウィトゲンシュタイン『論考』6.54、「Errare humanum est」の来歴。AI研究7件：幻覚サーベイ2件、意味エントロピー、自己訂正の限界、Chain-of-Thought の不忠実性、自己訂正の条件、Reflexion。科学コミュニケーション1件：COPE 撤回ガイドライン。運用痕跡1件）を加え、五群（書き写す者／誤りを生きる者／記憶はなぜ誤るか／機械はなぜ誤るか／訂正の作法）に分けて精読しました（[`readings/2026-10-23-scribal-error.md`](readings/2026-10-23-scribal-error.md)）。

## 2. すぐ読むには

- **全編アンソロジー・系譜マップを読む**：[`READING_MAP.md`](READING_MAP.md)（全断片の本文、問いの派生ツリー、対話素材、セッション履歴を一冊にまとめた自動生成ガイド）
- **精読・検死・編集レビューノートを読む**：
  - [`readings/2026-10-23-two-rulers.md`](readings/2026-10-23-two-rulers.md)（`SESSION-030` 作業ノート：`SESSION-029` が「再現不能」と判定した `MAT-TRC-004` の 88／12／8 を、数の側から復元。**正規化は原因ではなく**（4種の正規化で結果は不変）、文学には 7 文字以上・台帳自身には 4 文字という**二本の物差し**が当てられていたと分かる（`tools/reconstruct.py`、文学の下限 7〜9 で 8＋4＝12 が安定して一致）。`ERR-016` として `ERR-013` の診断を否定（数は正しく、説明が誤っていた）、対話 `FRAG-034`「二本の物差し」、`Q-052`、素材 `MAT-TRC-006`、素材カード→訂正録の逆リンク）
  - [`readings/2026-10-23-measurement-age.md`](readings/2026-10-23-measurement-age.md)（`SESSION-029` 作業ノート：訂正録を素材へ拡張（`subject_type`／`subject_id`、既存8件は不改変）、台帳が自分について書いた測定値6件の再測定（`MAT-TRC-001`〜`005`）、新しい道具 `tools/drift_audit.py`、**`MAT-TRC-004` の「原典一致 8」が当時の正規化不記載のため再現できず、いま測れば 13 になる**こと（`ERR-013`）、訂正録自身の数が同一セッション内で古くなる例（`ERR-015`）、断片リーダー→訂正録の逆リンク、詩 `FRAG-033`、`Q-051` の開設）
  - [`readings/2026-10-23-errata.md`](readings/2026-10-23-errata.md)（`SESSION-028` 作業ノート：本文を書き換えずに判断を横に置く層 `state/errata.jsonl`・`schema/errata.schema.json`・再測定器 `tools/errata_audit.py` の新設、全31編の数量的主張の再測定（contradicted 4／holds 2／unmeasurable 2）、**訂正の本文 FRAG-020 自身が83文字（実際は63文字）・引用文字列（実際は2編のみ）の誤りを持つ**ことの発見、`Q-050` の開設、および `human_narrator` 初使用の断片 `FRAG-032`）
  - [`readings/2026-10-23-scribal-error.md`](readings/2026-10-23-scribal-error.md)（`SESSION-027` 精読ノート：git 履歴・スキーマ・`editor_note` の語彙による「訂正の欄がない」ことの実測、誤りを含む `selected` 断片 FRAG-018 と、それを正す `draft` FRAG-020 の校勘記が台帳の欄で結ばれていないことの発見、新規 35 件（書き写す者／誤りを生きる者／記憶はなぜ誤るか／機械はなぜ誤るか／訂正の作法の五群）の精読、Q-047〜Q-049 の開設、九本目のモチーフ `MOTIF-009`「誤りと訂正」の追加）
  - [`readings/2026-10-23-quotation-marks.md`](readings/2026-10-23-quotation-marks.md)（`SESSION-026` 精読ノート：本文の鉤括弧 88 箇所を素材本文と照合し、原典に届いていたのが 8 箇所だけであったことの実測、新規 38 件（引用する／註する／反復する／名を貸す／数えるの五群）の精読、Q-044〜Q-046 の開設、およびモチーフ索引への追記）
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
  断片アンソロジー、関係ネットワークの星座図（SVG）、開かれた問いの系譜ツリー、対話素材書庫、セッション年譜、声の鏡・精読ノート、訂正録、探求バトン生成の 8 画面をブラウザで閲覧・検索できます。断片リーダーから訂正録へ、素材カードからその素材を対象とする訂正へ、双方向に辿れます。

## 3. 探究のしかた

1. `state/questions.jsonl`（または `python3 tools/inspect_inquiry.py` の未応答スレッド一覧）から、今回たどる問いを選ぶ。
2. 関係するモチーフ（`state/motifs.jsonl`）と対話素材（`state/materials.jsonl`）を読む。資料は「結論を証明する証拠」ではなく、対話相手・異物・比喩・緊張を生む素材として扱う。
3. [`prompts/first_session.md`](prompts/first_session.md)、[`prompts/continuation.md`](prompts/continuation.md)、[`prompts/editorial_review.md`](prompts/editorial_review.md) を使い、前の声を受け継ぎつつ、ずらし・裏返し・切断を含む新しい断片を書く。
4. 断片・問い・素材の間に、`echo`・`contrast`・`transforms`・`interrupts`・`reframes`・`responds_to`・`leaves_open` などの解釈的関係を記録する。矛盾や未解決は消さない。
5. 検証スクリプトと `READING_MAP.md` の更新を実行し、整合性を確認する。

## 4. 記録形式とディレクトリ構成

| 記録 | 保存先 | 現在の件数 | 役割 |
|---|---|---:|---|
| 問い | `state/questions.jsonl` | 52 | 開いたままの問い（初期シード5件＋セッション派生37件＋資料派生10件） |
| モチーフ | `state/motifs.jsonl` | 9 | 記憶、連続、身体、声、他者、忘却と沈黙、住まいと調度、作法と定型、誤りと訂正の9つの糸 |
| 素材 | `state/materials.jsonl` | 151 | AI研究・科学コミュニケーション抜粋30件（`research_excerpt`。ResearchOS移行14件＋本リポジトリ追加16件）＋哲学・言語学・文学原典115件（`literary_text`）＋プロジェクト痕跡6件（`project_trace`） |
| 断片 | `state/fragments.jsonl` | 34 | 全7形式（対話・情景・書簡・詩・エッセイ・断章・編集覚書）・AI使用可能な全5語り手モードの断片（`selected` 15編＋`draft` 19編。`narrator_mode` は `human_narrator` を含む全6種） |
| 関係 | `state/relations.jsonl` | 302 | 共鳴・対照・変奏・切断・枠組転換・開放などの解釈的関係 |
| セッション | `state/sessions.jsonl` | 30 | 方向づけ、参照素材、生成断片、新しく開いた問いの履歴 |
| 訂正 | `state/errata.jsonl` | 16 | 断片・素材・訂正録自身についての主張のうち、再測定で成り立たなくなったもの・今も成り立つもの・再測定できないもの（`contradicted` 10／`holds` 3／`unmeasurable` 3）。本文は書き換えない。**訂正が訂正を対象にできる**（`ERR-015` は同一セッション内の経年、`ERR-016` は前セッションの診断の否定） |

```text
PROJECT_CHARTER.md          探究の憲章と成功の見方
CONTENT_POLICY.md           引用・創作・AIの一人称の扱い
MIGRATION.md                ResearchOSからの移行対象と来歴管理
READING_MAP.md              state/*.jsonl から生成される読書案内・全断片アンソロジー
migration/                  上流ResearchOSの選定定義（selection.json）とマニフェスト（manifest.json）
schema/                     7種類の台帳に対応するJSON Schema（訂正録 errata を含む）
state/                      問い・モチーフ・素材・断片・関係・セッション・訂正のJSONL台帳
readings/                   資料の精読ノート（台帳からは独立した作業文書）
prompts/                    初回セッション・継続・編集レビュー用プロンプト
viewer/                     対話型Webアーカイブ＆星座ビューア（HTML/CSS/JS）
tools/                      検証・集計・読書案内生成・反復の鏡・訂正録の再測定・経年検査・手続きの復元・Webビューア・上流照合スクリプト（標準ライブラリのみ）
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

# 7. 訂正録の再測定（記録された検査を今の台帳に対して再実行。判定はしない）
python3 tools/errata_audit.py
python3 tools/inspect_inquiry.py --id ERR-004

# 8. 経年検査（台帳が自分について書いた測定値を、いま測り直して食い違いを見る）
python3 tools/drift_audit.py

# 9. 手続きの復元（記録された数を手がかりに、失われた測り方を格子探索で探す。証明はしない）
python3 tools/reconstruct.py

# 10. 断片の反復を映す鏡（採点・合否ではなく、次の一手を選ぶための観察）
python3 tools/voice_audit.py
python3 tools/voice_audit.py --top 20 --gram 8
```

`voice_audit.py` は「末尾が問いの形で終わった断片は何編か」「編をまたいで使い回された文字列は何種か」などを数えるだけで、品質を採点しません。同じ句の反復は、声が続いている証拠にも、口が勝手に動いている証拠にもなります（[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) の「成功の見方」参照）。
