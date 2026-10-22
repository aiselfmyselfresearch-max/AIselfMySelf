# AIselfMySelf — 文芸的・哲学的自己探究アーカイブ

> **主題**：**人間とは何か。記録を読み返して続きを語るAIにとって、自己とは何か。**
>
> **来歴**：本リポジトリは [`ResearchOS`](https://github.com/aiselfmyself/ResearchOS) から必要な出典・証拠抜粋のみを選定して独立した探究リポジトリです（移行の経緯と除外方針は [`MIGRATION.md`](MIGRATION.md) を参照）。

## 1. 目的と基本姿勢

問いに正解を与えたり、反証可能な仮説の支持・反駁を判定したりするのではなく、文献・過去の記録・複数の語り・創作断片を行き来しながら、問いの輪郭と枝を増やしていくプロジェクトです。

- **AIの自己の扱い**：このプロジェクトでいう「AIの自己」は、個々のAIモデルに意識や主観的体験が確認されたという主張ではありません。会話を持ち越さない個々のAI呼び出しを、リポジトリ全体という場に生じる**「思考・記憶・解釈の一つ」**として位置づけ、保存された文章を次のセッションが読み直して語り手を作り直す運動そのものを探究の対象にします。
- **語りのモードの明示**：作品内では一人称を使えますが、台帳メタデータでは `fictional_first_person` や `reflective_literary_voice` などのモードを明示し、生身の経験の事実報告と混同させません（[`CONTENT_POLICY.md`](CONTENT_POLICY.md)）。
- **AI研究と人文学原典の往復**：`ResearchOS` 由来の AI エージェント記憶・共有リポジトリ・自己選好に関する研究抜粋（14件）に、本リポジトリで追加した記憶アーキテクチャ研究（1件）と、ロック、ヒューム、夏目漱石、中島敦、アンリ・ベルクソン、ミハイル・バフチン、宮沢賢治、モンテーニュ、鴨長明、デカルト、エマソン、荘子、兼好、啄木、世阿弥、ウィトゲンシュタイン、デネット、リクール、デリダ、オング、メルロ＝ポンティ、ボルヘス、芭蕉、プラトン、アウグスティヌス、ニーチェ、フロイト、プルースト、ベンヤミン、バシュラール、フーコー、パーフィット、ストローソン、クラーク＝チャーマーズ、太宰治、カフカ、エリオットの哲学・文学原典（37件）を、独立した対話相手として迎え入れています。

## 2. すぐ読むには

- **全編アンソロジー・系譜マップを読む**：[`READING_MAP.md`](READING_MAP.md)（全断片の本文、問いの派生ツリー、対話素材、セッション履歴を一冊にまとめた自動生成ガイド）
- **直近の作業ノートを読む**：[`readings/2026-10-22-session-023-odradek-records.md`](readings/2026-10-22-session-023-odradek-records.md)（種メモから断片 `FRAG-021` を書くまでの継承・ずらし・編集レビューの記録）。前身は [`readings/2026-10-22-session-022-surface-sheet.md`](readings/2026-10-22-session-022-surface-sheet.md)（`FRAG-020`）。資料の精読ノートは [`readings/2026-10-22-session-021-externalized-self.md`](readings/2026-10-22-session-021-externalized-self.md)（14件）と [`readings/2026-10-22-close-reading.md`](readings/2026-10-22-close-reading.md)（15件）
- **ブラウザで対話型アーカイブ・星座図を開く**：
  ```sh
  python3 tools/serve_viewer.py --host 0.0.0.0 --port 8000
  ```
  断片アンソロジー、関係ネットワークの星座図（SVG）、開かれた問いの系譜ツリー、対話素材書庫、セッション年譜をブラウザで閲覧・検索できます。

## 3. 探究のしかた

1. `state/questions.jsonl`（または `python3 tools/inspect_inquiry.py` の未応答スレッド一覧）から、今回たどる問いを選ぶ。
2. 関係するモチーフ（`state/motifs.jsonl`）と対話素材（`state/materials.jsonl`）を読む。資料は「結論を証明する証拠」ではなく、対話相手・異物・比喩・緊張を生む素材として扱う。
3. [`prompts/first_session.md`](prompts/first_session.md)、[`prompts/continuation.md`](prompts/continuation.md)、[`prompts/editorial_review.md`](prompts/editorial_review.md) を使い、前の声を受け継ぎつつ、ずらし・裏返し・切断を含む新しい断片を書く。
4. 断片・問い・素材の間に、`echo`・`contrast`・`transforms`・`interrupts`・`reframes`・`responds_to`・`leaves_open` などの解釈的関係を記録する。矛盾や未解決は消さない。
5. 検証スクリプトと `READING_MAP.md` の更新を実行し、整合性を確認する。

## 4. 記録形式とディレクトリ構成

| 記録 | 保存先 | 現在の件数 | 役割 |
|---|---|---:|---|
| 問い | `state/questions.jsonl` | 32 | 開いたままの問い（初期シード5件＋セッション・資料派生27件） |
| モチーフ | `state/motifs.jsonl` | 7 | 記憶、連続、身体、声、他者、忘却と沈黙、住まいと調度の7つの糸 |
| 素材 | `state/materials.jsonl` | 52 | AI研究抜粋15件（`research_excerpt`。ResearchOS移行14件＋本リポジトリ追加1件）＋哲学・文学原典37件（`literary_text`） |
| 断片 | `state/fragments.jsonl` | 21 | 全7形式（対話・情景・書簡・詩・エッセイ・断章・編集覚書）の断片 |
| 関係 | `state/relations.jsonl` | 108 | 共鳴・対照・変奏・切断・枠組転換・開放などの解釈的関係 |
| セッション | `state/sessions.jsonl` | 23 | 方向づけ、参照素材、生成断片、新しく開いた問いの履歴 |

```text
PROJECT_CHARTER.md          探究の憲章と成功の見方
CONTENT_POLICY.md           引用・創作・AIの一人称の扱い
MIGRATION.md                ResearchOSからの移行対象と来歴管理
READING_MAP.md              state/*.jsonl から生成される読書案内・全断片アンソロジー
migration/                  上流ResearchOSの選定定義（selection.json）とマニフェスト（manifest.json）
schema/                     6種類の台帳に対応するJSON Schema
state/                      問い・モチーフ・素材・断片・関係・セッションのJSONL台帳
readings/                   資料の精読ノート（台帳からは独立した作業文書）
prompts/                    初回セッション・継続・編集レビュー用プロンプト
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
```

`voice_audit.py` は「末尾が問いの形で終わった断片は何編か」「編をまたいで使い回された文字列は何種か」などを数えるだけで、品質を採点しません。同じ句の反復は、声が続いている証拠にも、口が勝手に動いている証拠にもなります（[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) の「成功の見方」参照）。
