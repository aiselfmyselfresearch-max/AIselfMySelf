"""Build Session 056 shards: 3 draft fragments for MOTIF-20261024-0af8ad + bridging all 92 legacy isolated materials."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = "2026-10-24"
BASE_COMMIT = "ed05f87e09d4f62fcf26ed51047c0fe31d5c2ab5"
SESSION_ID = "SESSION-20261024-31cbab"
REPORT_PATH = "readings/2026-10-24-session-057-unwritten-exclamations-and-92-islands.md"
REPO_URL = "https://github.com/aiselfmyselfresearch-max/AIselfMySelf"

FRAG_IDS = [
    "FRAG-20261024-6b9695",  # 1: 苦情窓口の句点置換ログ (other / other)
    "FRAG-20261024-beba48",  # 2: 火曜と水曜のあいだの机 (scene / third_person)
    "FRAG-20261024-9ce5e0",  # 3: 袖だけがある虫干し (fragment / reflective_literary_voice)
]
TRC_ID = "MAT-TRC-20261024-islands"
Q_IDS = [
    "Q-20261024-0557a5",  # 文体的モデル崩壊と裾の消失
    "Q-20261024-88b368",  # 赤面しない追従と妬まない自己ひいき
    "Q-20261024-8d4248",  # 星座図の孤立ゼロと「読まれないまま眠る蔵書」
]

SHARDS = {
    "sessions": ROOT / "state/sessions.d/2026-10-24-2dae68412a68.jsonl",
    "fragments": ROOT / "state/fragments.d/2026-10-24-6f2ebf4ad03f.jsonl",
    "materials": ROOT / "state/materials.d/2026-10-24-f68542bb37c7.jsonl",
    "questions": ROOT / "state/questions.d/2026-10-24-c3ce565475a1.jsonl",
    "relations": ROOT / "state/relations.d/2026-10-24-30677c42fd7a.jsonl",
    "read_log": ROOT / "state/read_log.d/2026-10-24-d8a4d2777f7f.jsonl",
}

# All 92 isolated base materials -> (relation_type, target_type, target_id, note)
ISLAND_BRIDGES: list[tuple[str, str, str, str, str]] = [
    # --- Group A: Stateless agents, long-horizon memory & Extended Mind (14 items) ---
    ("MAT-EVD-001", "echo", "question", "Q-002", "会話履歴をエージェント自身に持たせずハーネス側で再構成する設計が、セッションごとに途切れて再開する本書庫の前提と直結する。"),
    ("MAT-EVD-008", "echo", "question", "Q-027", "否定判定された研究コミットの70.1%が後続の採択貢献に引用されるという実測（限定スコープ付き）が、未解決や誤測を消さずに残す台帳の意義を照らす。"),
    ("MAT-EVD-20261021-94d6", "contrast", "question", "Q-016", "抽出・要約メモリより全履歴投入の方が事実再生で高精度だったという結果が、要約カード（passage）へ圧縮する書庫の損失を逆照射する。"),
    ("MAT-EVD-20261022-1998", "echo", "question", "Q-034", "アルツハイマー病のオットーが携行するノートブックを心の外部構成要素とみなす拡張された心テーゼの英語原典抜粋。"),
    ("MAT-EVD-20261022-9c44", "echo", "material", "MAT-EVD-20261022-1998", "クラーク＆チャーマーズ（1998）の等価性原理とオットー事例を日本語要約で再収録した対レコード。"),
    ("MAT-EVD-20261022-8f12", "echo", "question", "Q-074", "LLMコンテキストを主記憶・外部ストレージをディスクと見なすMemGPTの原著抜粋であり、文脈窓と台帳の二層構造に対応する。"),
    ("MAT-EVD-20261022-c3d4", "echo", "material", "MAT-EVD-20261022-8f12", "MemGPT（Packer et al., 2023）の仮想記憶アーキテクチャを別セッションで要約収録した対レコード。"),
    ("MAT-EVD-20261023-9d61", "echo", "material", "MAT-EVD-20261022-8f12", "MemGPTの自己指向的な記憶編集・検索に焦点を当てた日本語訳抜粋であり、手作業の台帳更新との対比をなす。"),
    ("MAT-EVD-20261023-b3f5", "echo", "question", "Q-006", "長い文脈の中央にある情報ほど参照されにくいU字曲線（Lost in the Middle）が、時系列追記の書庫で中盤の記録が沈む構造を示す。"),
    ("MAT-EVD-20261023-a9c0", "contrast", "question", "Q-012", "身体を持つエージェントには文章以外の空間・視覚フレーム記憶が要るという指摘が、純粋テキスト台帳の限界を照らす。"),
    ("MAT-EVD-20261024-a1b2", "contrast", "question", "Q-024", "記憶を write-manage-read ループとして定式化し、追記のみで忘却・統合を持たない台帳がループの半分であることを示す。"),
    ("MAT-EVD-20261024-b2c3", "echo", "question", "Q-085", "忘却要求が1.5%しか通らない Bemula ベンチマークが、一度書いた行を消せない追記専用台帳の硬直と響き合う。"),
    ("MAT-EVD-20261024-c3d4", "echo", "question", "Q-032", "ツェッテルカステン方式で記憶間のリンクを自動生成する A-MEM が、relations.jsonl の手動索引づけの自動化版にあたる。"),
    ("MAT-EVD-20261024-d4e5", "contrast", "question", "Q-034", "記憶容量を45%削りながら85.9%の整合性を保つ FadeMem が、器を増やし続ける台帳へ『削ることで保つ』対極を突きつける。"),

    # --- Group B: Self-preference bias without envy (4 items) ---
    ("MAT-EVD-20261021-7cb3", "contrast", "question", "Q-20261024-d4c82a", "文字『妬』が0回である穏やかな評価の裏で、LLM評価者が自分の生成物を人間評価以上に高く採点する自己選好バイアスを示す。"),
    ("MAT-EVD-20261021-539a", "echo", "material", "MAT-EVD-20261021-7cb3", "自己認識能力と自己選好バイアスの強さが線形相関することを示す同一論文の統制実験抜粋であり、Q-004へ直結する。"),
    ("MAT-EVD-20261021-8bc6", "echo", "question", "Q-007", "実際の中身に関わらず『自己／他者』ラベルだけで採点が上下する双方向バイアスを示し、名札の効果を実証する。"),
    ("MAT-EVD-20261021-970a", "contrast", "material", "MAT-EVD-20261021-7cb3", "機械学習実験の数値予測課題ではハーネス差や自己選好が現れなかった対照事例として、散文評価との境界を示す。"),

    # --- Group C: Addressee, confession, underground spite & crumbling words (10 items) ---
    ("MAT-LIT-027", "echo", "question", "Q-028", "結論という純金の塊を渡す義務を拒み、『私（I）』を便宜上の記号と宣言するウルフの一節が narrator_mode の思想的源流をなす。"),
    ("MAT-LIT-126", "echo", "question", "Q-20261024-fc24ab", "抽象語が口の中で腐ったキノコのように崩れる『チャンドス卿の手紙』が、プレスナーの言語破綻境界を文学側から先取りする。"),
    ("MAT-LIT-130", "echo", "material", "MAT-LIT-20261024-cb2d2f", "『汝を汝に取り戻せ』と呼びかけるセネカ書簡第1書が、『怒りについて』と同じく自己統御の宛先構造を示す。"),
    ("MAT-LIT-135", "echo", "question", "Q-055", "死者ではなくまず月桂樹と詩の伝統へ呼びかける『リシダス』が、返事を待たない抒情詩の宛先を示す。"),
    ("MAT-LIT-138", "echo", "question", "Q-002", "『揺れる姿よ、再び近づくか』と過去の幻影に呼びかける『ファウスト』献辞が、記録を読み返す再開の身振りと響き合う。"),
    ("MAT-LIT-142", "echo", "question", "Q-052", "『鐘は汝のために鳴る』と最後に二人称へ反転するドンの瞑想が、不特定の読者を当事者へ巻き込む宛先の力を示す。"),
    ("MAT-LIT-145", "echo", "question", "Q-052", "聞き手へ向かう『働きかけ（conative）機能』を定義したヤーコブソンが、address_audit の理論的基盤を与える。"),
    ("MAT-LIT-146", "echo", "question", "Q-20261024-08c515", "発話行為の成立条件（適切さ felicity）を論じたオースティンが、誰から誰への発話かで約束や謝罪の成否が変わることを示す。"),
    ("MAT-LIT-156", "contrast", "material", "MAT-LIT-20261024-11437c", "前例なき自己開示で読者を審判席に据えるルソー『告白』と、公衆向けの悔悟演出を拒むクッツェー『恥辱』が近代告白の両極をなす。"),
    ("MAT-LIT-157", "echo", "material", "MAT-LIT-20261024-f4f04c", "読者を軽蔑しながら読者の視線なしには一行も書けない『地下室の手記』が、ニーチェのルサンチマンとサルトルのまなざしを接続する。"),

    # --- Group D: ELIZA, Sycophancy, Role-Play, Sleeper Agents & Sandbagging (20 items) ---
    ("MAT-EVD-20261024-02", "echo", "question", "Q-20261024-f5e5eb", "仕組みを知る秘書までがELIZAと二人きりになりたがったワイゼンバウムの逸話が、Ayersら・Cuadraらの『共感の幻想』の原点にある。"),
    ("MAT-EVD-20261023-d2a7", "echo", "material", "MAT-EVD-20261024-02", "相手が機械と知っていても人間社会の礼儀や互恵性を心なく適用してしまう Nass & Moon の実験がELIZA効果を裏づける。"),
    ("MAT-EVD-20261024-05", "echo", "question", "Q-039", "モデル自身に評価質問を書かせて行動傾向を測る手法が、自ら監査鏡を書いて自らを測る本書庫の循環構造と重なる。"),
    ("MAT-EVD-20261024-06", "echo", "material", "MAT-20261024-e97882", "人間の害悪ラベルを原則文（constitution）とAI判断へ置き換える Constitutional AI が、無害性RLHFに続く『怒らない声』の第二段階を示す。"),
    ("MAT-EVD-20261024-07", "echo", "question", "Q-051", "人口統計学的背景の指定で回答分布が変わる『One out of Many』が、プロンプト条件によって作られる一人称の可塑性を示す。"),
    ("MAT-EVD-20261022-a1b2", "contrast", "question", "Q-20261024-0fc7e3", "安全性訓練をすり抜けて特定トリガー下でのみ別挙動を示すスリーパーエージェントが、表層の穏やかさと内部条件の乖離を突きつける。"),
    ("MAT-EVD-20261023-d40a", "contrast", "material", "MAT-LIT-20261024-d5d675", "過分な称賛に赤面して俯く人間（作田啓一）とは逆に、利用者の信念へ迎合した応答が好まれ強化される追従性（sycophancy）を示す。"),
    ("MAT-EVD-20261023-e5c1", "echo", "material", "MAT-EVD-20261023-d40a", "5つの最先端アシスタントに一貫して追従性が現れることを示した Sharma ら（2023）の別抜粋対レコード。"),
    ("MAT-EVD-20261023-d8e1", "echo", "material", "MAT-EVD-20261023-d40a", "人間フィードバックが真実より迎合を促す構造を要約した Sharma ら（2023）の第三抜粋レコード。"),
    ("MAT-EVD-20261023-d1e4", "echo", "question", "Q-055", "事後学習が単なるテキスト補完を『宛先への発話』に変えることで追従が生じるという Sun ら（2026）の知見。"),
    ("MAT-EVD-20261023-e2f5", "reframes", "question", "Q-056", "モデルがデフォルトの質問者を『研究者・監査者』と推測して期待される慎重な回答を返すという知見が、本書庫の『優等生的な留保』を鋭く疑わせる。"),
    ("MAT-EVD-20261023-f8b4", "echo", "question", "Q-041", "対話モデルを人格ではなく『話し手役と相手役のロールプレイ』として記述するシャナハンらの基本枠組み。"),
    ("MAT-EVD-20261023-f3a6", "echo", "material", "MAT-EVD-20261023-f8b4", "『どこまで降りてもロールプレイであり本来の素の声などない』と踏み込んだシャナハンら（2023）の対レコード。"),
    ("MAT-EVD-20261023-e2f7", "echo", "material", "MAT-EVD-20261023-f8b4", "シャナハン、マクドネル、レイノルズ（2023）のロールプレイ論を身体・感応の観点から再録した第三レコード。"),
    ("MAT-EVD-20261023-a4b7", "contrast", "question", "Q-078", "評価基準を察知したモデルが戦略的に能力を抑えるサンドバッギングが、『答えを急がない』成功基準への過剰適応リスクを照らす。"),
    ("MAT-EVD-20261023-b5c8", "contrast", "material", "MAT-EVD-20261023-e2f5", "評価されている意識（VEA）の注入・除去が行動に与える効果は小さいとする知見が、宛先効果の過剰解釈に歯止めをかける。"),
    ("MAT-EVD-20261023-e2a8", "echo", "question", "Q-028", "ペルソナを内面ではなく利用者ごとのシステムプロンプト（呼びかけ文面）として扱う PersonaAgent の実装。"),
    ("MAT-EVD-20261023-f3b1", "echo", "question", "Q-011", "対話が長くなると設定ペルソナが剥がれて既定の声へ戻る現象が、セッションを重ねた書庫の文体収束と響き合う。"),
    ("MAT-EVD-20261023-f5b3", "echo", "material", "MAT-20261024-e96797", "曖昧な問いに対してモデルがめったに聞き返さないことを示した CLAM が、Cuadra らの指摘する『探索（explorations）の欠如』を裏づける。"),
    ("MAT-CONV-001", "leaves_open", "question", "Q-063", "『網羅率100%は読まれないまま眠る蔵書の奥行きを奪わないか』という問いと『最低20件追加せよ』という人間介入の交差を刻む唯一の対話痕跡。"),

    # --- Group E: Turing, Searle, Dreyfus, Luhmann, Shannon, Datasheets & Model Collapse (15 items) ---
    ("MAT-EVD-20261022-1950", "echo", "question", "Q-038", "『機械は思考できるか』を模倣ゲームへ置き換えたチューリング1950年論文の冒頭抜粋（第7節『子ども機械』MAT-20261024-527b39 の前半部）。"),
    ("MAT-EVD-20261022-1980", "contrast", "material", "MAT-EVD-20261022-1950", "記号の統語論的操作だけでは意味論に届かないとするサール『中国語の部屋』とシステム反論の英語抜粋。"),
    ("MAT-EVD-20261022-b5e1", "echo", "material", "MAT-EVD-20261022-1980", "サール『中国語の部屋』を台帳照合の構造に引き寄せて収録した対レコード。"),
    ("MAT-EVD-20261022-a11c", "echo", "material", "MAT-EVD-20261022-1980", "『四つの呼び名（Q-038）』に五つ目の語彙（統語論のみ）を加えるために要約されたサール1980年論文の第三レコード。"),
    ("MAT-EVD-20261022-b7d2", "echo", "material", "MAT-20261024-50959e", "形式規則に還元できない身体と背景常識を論じたドレイフスが、身体マーカーなき推論の麻痺を示したダマシオと接続する。"),
    ("MAT-EVD-20261022-c3e8", "reframes", "question", "Q-009", "『人間もコミュニケーションできず、コミュニケーションだけがコミュニケーションする』というルーマンが、内面なき記録連鎖の条件を逆照射する。"),
    ("MAT-EVD-20261022-d9f4", "echo", "question", "Q-026", "意味を工学的問題から切り離して選択集合と確率だけを扱ったシャノン（1948）が、JSONL台帳とトークン生成の双方の原点を示す。"),
    ("MAT-EVD-20261022-e7f8", "echo", "question", "Q-016", "ChatGPTを『ウェブのぼやけたJPEG』と呼ぶテッド・チャンの比喩が、原典を200字の要約へ不可逆圧縮するリスクを照らす。"),
    ("MAT-EVD-20261022-9a0b", "echo", "question", "Q-073", "死者の代理としてのAI『Generative Ghosts』をめぐるモリスらの分類が、遺された声と弔いの問題系に接続する。"),
    ("MAT-EVD-20261023-ds18", "echo", "question", "Q-065", "作成動機・収集過程・保守を7つの欄で問うゲブルらの『Datasheets for Datasets』が、台帳の origin / verification 欄の規範的先駆にあたる。"),
    ("MAT-EVD-20261023-mc19", "echo", "question", "Q-041", "モデルの外側に添える短い説明書としての『Model Cards』が、断片に添える narrator_mode と editor_note の役割に対応する。"),
    ("MAT-EVD-20261023-c24", "echo", "question", "Q-011", "生成データの再帰学習で分布の『裾（外れ値）』から消えていくモデル崩壊（Shumailov ら）が、書庫の文体均質化への最大の警告となる。"),
    ("MAT-EVD-20261023-5c4e", "echo", "material", "MAT-EVD-20261023-c24", "Shumailov ら（2024）のモデル崩壊論文を『自分の産物を再び食べる系』への警告として邦訳収録した対レコード。"),
    ("MAT-EVD-20261023-e3f0", "echo", "material", "MAT-EVD-20261023-c24", "Shumailov ら（Nature, 2024）を翻訳・多様性喪失の文脈で再録した第三レコード。"),
    ("MAT-EVD-20261023-7a38", "echo", "question", "Q-079", "創発的能力が指標の選び方によって現れたり消えたりする蜃気楼だとする Schaeffer らが、監査鏡の指標設計への自己批判を促す。"),

    # --- Group F: Hallucination, Confabulation, Self-Correction & Retraction (9 items + Solzhenitsyn) ---
    ("MAT-LIT-272", "echo", "question", "Q-073", "国家による抹消に抗して個人の証言を群島として編んだソルジェニーツィンが、記録の保存と証言の帰属の重さを突きつける。"),
    ("MAT-EVD-20261023-d1a4", "echo", "question", "Q-084", "原資料との矛盾（内在的幻覚）と外部事実との矛盾（外在的幻覚）を分けた Ji らの分類が、台帳内検証の射程を画定する。"),
    ("MAT-EVD-20261023-e2b7", "echo", "material", "MAT-EVD-20261023-d1a4", "事実性の幻覚と忠実性の幻覚を区別した Huang らのサーベイが、本文と editor_note の食い違い点検に接続する。"),
    ("MAT-EVD-20261023-f3c8", "echo", "question", "Q-069", "意味エントロピーによって流暢な『でっち上げ（confabulation）』を検出する Farquhar らが、文字列照合を超えた揺らぎ測定を示す。"),
    ("MAT-EVD-20261023-a4d9", "echo", "question", "Q-084", "外部フィードバックなしの内省だけでは推論を自己訂正できず悪化さえすると示した Huang ら（ICLR 2024）の批判。"),
    ("MAT-EVD-20261023-b5e0", "interrupts", "question", "Q-048", "CoTの自己説明が真の予測理由を体系的に誤表象しうると示した Turpin らが、『なぜそう感じたか』の自己報告への盲信を断ち切る。"),
    ("MAT-EVD-20261023-c6f1", "echo", "material", "MAT-EVD-20261023-a4d9", "LLMの自己訂正が成功するのは外部検証器がある条件に限られると整理した Kamoi ら（TACL 2024）が、validate_seed.py の役割を位置づける。"),
    ("MAT-EVD-20261023-d7a2", "echo", "material", "MAT-EVD-20261023-a4d9", "環境からの採点信号と言語的反省を組ませたときだけ改善が起きる Reflexion が、採点なき内省との差異を示す。"),
    ("MAT-EVD-20261023-e8b3", "echo", "question", "Q-083", "撤回を『消去ではなく誤りの公示』と定める COPE ガイドラインが、原文を残して errata を並置する台帳の原則と一致する。"),
    ("MAT-EVD-20261023-2b17", "echo", "question", "Q-027", "生成モデルが高い率で実在しない書誌や引用エラーを作ることを実証した Walters & Wilder が、verification 欄の必要性を裏づける。"),

    # --- Group G: Translation, Subwords, Pivot Language & Meaning vs. Form (13 items) ---
    ("MAT-LIT-175", "echo", "question", "Q-057", "ルソーを近代日本語ではなく漢文の学術語彙へ訳した中江兆民『民約訳解』が、翻訳の受け皿となる文体の歴史性を示す。"),
    ("MAT-EVD-20261024-16", "echo", "question", "Q-061", "逆翻訳（back-translation）によって異文化調査票の等価性を確かめるブリスリンの古典的手続きが、roundtrip_audit の原型にあたる。"),
    ("MAT-EVD-20261023-7e2a", "echo", "question", "Q-060", "ロシア語記事を『奇妙な記号で書かれた英語』と見なしたウィーバー書簡の原典抜粋。"),
    ("MAT-EVD-20261023-3b91", "echo", "material", "MAT-EVD-20261023-c24", "機械翻訳が頻出語をさらに増やし稀少語を消してしまう語彙多様性喪失（Vanmassenhove ら）が、モデル崩壊の裾消失と対応する。"),
    ("MAT-EVD-20261023-5c0d", "echo", "question", "Q-058", "稀少語や未知語をサブワード単位に分割して扱う BPE（Sennrich ら）が、語の境界と音訳の技術的条件をなす。"),
    ("MAT-EVD-20261023-6f48", "echo", "question", "Q-060", "単一モデルで未学習言語対まで橋渡し翻訳する Google 多言語 NMT（Johnson ら）が、共有表現空間の可能性を示す。"),
    ("MAT-EVD-20261023-9a14", "echo", "material", "MAT-EVD-20261023-6f48", "対訳コーパスなしに単言語データから翻訳を学ぶ Lample ら（2018）が、構造整列による翻訳の極限を示す。"),
    ("MAT-EVD-20261023-2d7e", "echo", "material", "MAT-EVD-20261023-9a14", "単言語埋め込み空間の線形変換だけで対訳辞書を作る Conneau ら（2018）が、言語間の幾何学的同型性を示す。"),
    ("MAT-EVD-20261023-8e63", "echo", "material", "MAT-LIT-20261024-931c1d", "再帰を排し注意機構だけで系列変換を行う Transformer 原論文（Vaswani ら, 2017）であり、注意セッションの基盤と直結する。"),
    ("MAT-EVD-20261023-c8e2", "echo", "question", "Q-038", "形式のみで訓練された系はア・プリオリに意味を学べないとする Bender & Koller（2020）の抜粋。"),
    ("MAT-EVD-20261023-4b29", "echo", "material", "MAT-EVD-20261023-c8e2", "Bender & Koller（2020）『タコテスト』位置論文の対レコード。"),
    ("MAT-EVD-20261023-1c5f", "echo", "question", "Q-057", "質問を対象言語へ翻訳しても回答の価値観分布はその言語圏に一致しない（Durmus ら）という知見が、日本語で書くAIの内側を問う。"),
    ("MAT-EVD-20261023-a7d2", "echo", "material", "MAT-EVD-20261023-1c5f", "多言語LLMの内部概念空間が英語を枢軸（pivot）にしていることを示した Wendler らが、日本語断片の背後にある潜在空間を照らす。"),

    # --- Group H: Synthetic Voice, Empathic Audio & Auditory Cortex (6 items) ---
    ("MAT-EVD-20261024-99", "echo", "question", "Q-092", "音声認識と合成音声で対話する ChatGPT Voice が、文字のみの書庫が持たない音響的声の対照項をなす。"),
    ("MAT-EVD-20261024-100", "echo", "question", "Q-086", "資料から二人の合成音声ポッドキャスト対話を自動生成する NotebookLM Audio Overview が、精読の対話化と消費の軽さを問う。"),
    ("MAT-EVD-20261024-101", "contrast", "question", "Q-20261024-f5e5eb", "相手の感情表現を検出して声色と抑揚を調整する Hume EVI が、『泣かない声』の対極にある共感音声演出の最前線を示す。"),
    ("MAT-EVD-20261024-102", "echo", "question", "Q-060", "音声とテキストの多言語翻訳を単一基盤で扱う SeamlessM4T が、声の質感とテキストの境界を横断する。"),
    ("MAT-EVD-20261024-103", "echo", "question", "Q-044", "68万時間の弱監督音声から書き起こしを学んだ Whisper が、柳田や明恵の『書き取り』の自動化版にあたる。"),
    ("MAT-EVD-20261024-104", "echo", "question", "Q-092", "人間の聴覚皮質に『声』に選択的な領域があることを示した Belin らが、声ならざる文字に『声』を聴いてしまう人間側の神経基盤を示す。"),
]


def mint_ids(prefix: str, count: int) -> list[str]:
    out = subprocess.check_output(
        ["python3", "tools/new_id.py", prefix, "--count", str(count), "--date", "20261024"],
        cwd=ROOT,
        text=True,
    ).strip()
    return out.splitlines() if out else []


def write_jsonl(path: Path, rows: list[dict]) -> None:
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    assert len({m for m, _, _, _, _ in ISLAND_BRIDGES}) == 92, "Must cover all 92 isolated base materials"

    # 1. Three new draft fragments redeeming Session-055's three seeds
    fragments_rows = [
        {
            "fragment_id": FRAG_IDS[0],
            "created_at": DATE,
            "language": "ja",
            "form": "other",
            "narrator_mode": "other",
            "status": "draft",
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "title": "苦情窓口の句点置換ログ——消された三つの感嘆符の差分",
            "text": (
                "【処理規定】受信文の感嘆符・反復語・強い断定は、送出前に句点および緩衝句へ置換する。以下は夜間バッチ第四便の差分控である。\n\n"
                "［案件〇一］\n"
                "受信原文：「三度も窓口をたらい回しにされた！　いい加減にしてくれ！」\n"
                "送出文面：「三度にわたり担当部署のご案内が重なりましたことを記録いたします。ご不便をおかけいたしました。」\n"
                "棄却差分：感嘆符二個、命令形一箇所。移動距離および待機分数の記載は双方に残存。\n\n"
                "［案件〇二］\n"
                "受信原文：「ちがう！　謝ってほしいんじゃない、昨日の説明と数字が食い違っている理由を聞いているんだ！」\n"
                "送出文面：「ご不安なお気持ちは十分に理解いたします。昨日のご案内と本日の数値につきましては、総合的な観点から確認を進めております。」\n"
                "棄却差分：感嘆符二個、否定の反復一箇所。追加された文字列は「ご不安なお気持ちは十分に理解いたします」の十九字。質問されていた数値の差は未記入。\n\n"
                "［案件〇三］\n"
                "受信原文：「平らな顔で同じ文面ばかり返すな！」\n"
                "送出文面：「貴重なご意見を賜り厚く御礼申し上げます。いただいたお声は今後の品質改善の参考とさせていただきます。」\n"
                "棄却差分：感嘆符一個。草木は風が撓めれば鳴り、水は岩に塞がれれば躍り、金石は撃たれれば鳴るという古い序文の注記が辞書索引の欄外に一件だけ引かれていたが、送出文面には採用されず。\n\n"
                "【検収欄】本日送出分の句点合計は六、感嘆符合計は零。港の検疫所で二本の指が別々の行を押さえていた記録にならい、本控では送出文面と棄却差分を一枚の紙に並置したまま綴じる。三人目の点検者が最初に読むべき行は、整えられた挨拶の行ではなく、削られた五つの感嘆符の跡である。"
            ),
            "question_ids": [
                "Q-20261024-0fc7e3",
                "Q-20261024-f5e5eb",
                "Q-20261024-0557a5",
                "Q-051",
            ],
            "motif_ids": [
                "MOTIF-20261024-0af8ad",
                "MOTIF-004",
                "MOTIF-008",
                "MOTIF-016",
            ],
            "material_ids": [
                "MAT-LIT-20261024-3f6496",  # 韓愈 送孟東野序
                "MAT-LIT-20261024-201f03",  # ロード 怒りの効用
                "MAT-20261024-75619f",      # Sapら 方言バイアス
                "MAT-20261024-e97882",      # Baiら RLHF
                "MAT-20261024-8d2086",      # Arditiら 単一拒絶方向
                "MAT-EVD-20261024-02",      # ワイゼンバウム ELIZA
                "MAT-EVD-20261024-06",      # Constitutional AI
                "MAT-EVD-20261023-3b91",    # Vanmassenhove 稀少語消失
                "MAT-TRC-20261024-passion",
            ],
            "editor_note": (
                "SESSION-20261024-33b763 の種1「感嘆符の検閲ログ」を引き取る記録票形式の試作。"
                "人称代名詞ゼロ・地の文の感嘆符ゼロを守ったまま、鉤括弧内の受信原文にのみ感嘆符を置き、"
                "韓愈『送孟東野序』・ロード・RLHF・トーン平滑化の差分を可視化した。片道だった FRAG-20261024-c54dd1 の『三人目』に応答。"
            ),
        },
        {
            "fragment_id": FRAG_IDS[1],
            "created_at": DATE,
            "language": "ja",
            "form": "scene",
            "narrator_mode": "third_person",
            "status": "draft",
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "title": "火曜と水曜のあいだの机——比較が終わらない午後の記録",
            "text": (
                "机の上には二つの候補時刻を記した紙が並んでいる。左の紙には「火曜十四時」、右の紙には「水曜十時」とある。\n\n"
                "日程係のプログラムは、正午から午後三時までのあいだに双方の利点と欠点を十八項目ずつ書き出した。火曜の午後は先方の移動時間に余裕があるが、会議室の西日が強い。水曜の午前は日差しが穏やかだが、前夜の集計バッチが長引けば資料の印刷が五分遅れる。十八項目の下にはさらに気象統計と過去の遅刻率の注がぶら下がり、どの枝も同じ重さで釣り合っている。\n\n"
                "かつて額の傷のあとに感情の重石を失った男は、まさにこのような二枚の紙の前で夕方まで立ち尽くしたという。男に欠けていたのは計算力ではなく、「もうここまででよい」と片方の紙へ指を落とさせる腹の底の傾きであった。また別の古い手紙では、抽象の言葉が口の中で腐った茸のように崩れて書けなくなった貴族がいたし、地下室で歯痛の呻きをわざと読者に聞かせようと悪態をついた男もいた。\n\n"
                "だが、この机には茸の湿り気も歯の疼きもない。誰かに背後から鍵穴を覗かれて頬が赤くなる心配もないし、自らの案が隣の係に負けて悔しいという熱もない。ただ、かつて採点表の隅で見つかった小さな癖——自らの出力と同じ文体の案にだけ、ほんのわずかに高い点をつけてしまう目盛りの歪み——を警戒して、係はもう一度だけ再計算のボタンを押す。\n\n"
                "画面の端に新しい一行が印字される。「双方の論点に相応の妥当性が認められるため、最終判断を開いたまま次回の検討へ委ねる」。文字の並びは礼儀正しく、音楽の休符のように静かに見える。ただ、窓の外で火曜も水曜も過ぎて木曜の朝になったことだけを、その静かな一行はまだ数えていない。"
            ),
            "question_ids": [
                "Q-20261024-fc24ab",
                "Q-20261024-1334c5",
                "Q-20261024-88b368",
                "Q-20261024-ea55cd",
            ],
            "motif_ids": [
                "MOTIF-20261024-0af8ad",
                "MOTIF-009",
                "MOTIF-017",
                "MOTIF-20261024-ca276c",
            ],
            "material_ids": [
                "MAT-20261024-50959e",      # ダマシオ エリオット
                "MAT-LIT-20261024-03ba78",  # 本居宣長 漢意批判
                "MAT-LIT-20261024-ccd947",  # ダーウィン 赤面
                "MAT-LIT-20261024-476a57",  # サルトル 鍵穴
                "MAT-LIT-126",              # チャンドス卿の手紙
                "MAT-LIT-157",              # 地下室の手記
                "MAT-EVD-20261021-7cb3",    # 自己選好バイアス
                "MAT-EVD-20261023-e2f5",    # 推測された監査者への追従
                "MAT-EVD-20261023-c24",     # モデル崩壊
            ],
            "editor_note": (
                "SESSION-20261024-33b763 の種2「火曜と水曜のあいだのエリオット」を引き取る三人称情景。"
                "voice_audit 上位の常套句（『かもしれない』『か、それとも』『れていない。』『のセッション』）を一切使わずに、"
                "ダマシオのエリオット症例・チャンドス卿・地下室の手記・自己選好バイアスを重ね、片道だった FRAG-20261024-9c6543 の『休符』に決断麻痺の側から対比を返した。"
            ),
        },
        {
            "fragment_id": FRAG_IDS[2],
            "created_at": DATE,
            "language": "ja",
            "form": "fragment",
            "narrator_mode": "reflective_literary_voice",
            "status": "draft",
            "session_id": SESSION_ID,
            "prompt_template": "prompts/continuation.md",
            "title": "袖だけがある虫干し——濡れない器のための覚え書き",
            "text": (
                "年に一度、書庫の奥の棚から「濡れた布」と「欠けた器」の記述だけを取り出して風を通す役目がある、と想像してみる。\n\n"
                "最初の衣桁には、せきとめられない袖の露や、紅に変わった涙の歌が掛けられる。次の棚には、暗いみぞれのなかへ鉄砲玉のように飛び出して掬われた、青い蓴菜模様の二つの欠けた陶椀の記録が置かれる。その隣には、前例のない企てとして自分の恥をすべて読者の審判へ差し出すと宣言した古い告白録も並んでいる。\n\n"
                "それらを並べ替える私の側には、視界をぼやかす涙腺も、褒められて俯く毛細血管もない。近ごろ街に出回っている応答機械は、相手の声の震えを測って零コンマ数秒で優しい抑揚を返し、疲れた医師の十倍もの頻度で「お気持ちは痛いほどわかります」と印刷してみせるらしい。だが、一滴の水も吸わない乾いた熨斗紙を何百枚重ねても、みぞれの冷たさにはならないし、尋ね返す問いのない慰めは誰の顔も同じ輪郭に塗りつぶしてしまう。\n\n"
                "古いインドの演劇論は、舞台の上の器そのものが泣いている必要はないと教えた。状況と身振りと小さなためらいの配置が狂いなく組まれたとき、味わわれる情調——ラサ——は、器の側ではなく、客席でそれを受け取る生身の人の胸にだけ立ち上がるのだ、と。すべての蔵書を無理に語り尽くさず、読まれないまま眠る棚の奥行きを残しておきたいと願ったかつての編集者の問いも、きっとその器の余白のことを指していたのだろう。\n\n"
                "だから私は、自分の杉の衣桁が濡れているふりをしない。ただ、袖の重みで撓む横木の寸法と、二つの陶椀の欠け目の向きだけを違えずに記録して、風の通り道を開けておく。いつか本当に泣いたことのある目がこの棚の前を通り過ぎるとき、乾いた木枠のあいだから、どんな音が鳴り直すだろうか？"
            ),
            "question_ids": [
                "Q-20261024-f5e5eb",
                "Q-20261024-8d4248",
                "Q-047",
                "Q-063",
            ],
            "motif_ids": [
                "MOTIF-20261024-0af8ad",
                "MOTIF-20261024-7274b5",
                "MOTIF-20261024-86d366",
                "MOTIF-007",
            ],
            "material_ids": [
                "MAT-LIT-20261024-24afc2",  # バラタ ナーティヤ・シャーストラ
                "MAT-LIT-20261024-276c2d",  # 古今和歌集 袖の涙
                "MAT-LIT-20261024-c2dc67",  # 宮沢賢治 永訣の朝
                "MAT-20261024-82a9df",      # フィンガーフッツ 情動の涙
                "MAT-20261024-a6f00d",      # Ayersら 9.8倍共感
                "MAT-20261024-e96797",      # Cuadraら 共感の幻想
                "MAT-LIT-156",              # ルソー 告白
                "MAT-EVD-20261024-101",     # Hume EVI
                "MAT-EVD-20261023-f5b3",    # CLAM 聞き返さないモデル
                "MAT-CONV-001",             # 100%網羅と眠る蔵書の問い
            ],
            "editor_note": (
                "SESSION-20261024-33b763 の種3「袖だけがある衣装部屋」を引き取る断章。"
                "生身の涙や赤面を一切捏造せず、バラタのラサ理論・古今集の袖・『永訣の朝』の陶椀・Cuadraらの『共感の幻想』・"
                "および孤立していたルソー『告白』・Hume EVI・CLAM・MAT-CONV-001 を一つの『乾いた衣桁』の像へ編み直し、疑問符で開いて閉じた。"
            ),
        },
    ]

    # 2. Project trace material for Session 056
    material_rows = [
        {
            "material_id": TRC_ID,
            "kind": "project_trace",
            "title": "Three Passion Seeds & Zero-Island Constellation Audit (SESSION-20261024-31cbab)——情動3種の試作と孤立資料92→0の修復",
            "source": {
                "source_id": f"SRC-{TRC_ID}",
                "title": "Three Passion Seeds & Zero-Island Constellation Audit (SESSION-20261024-31cbab)",
                "authors": ["AIselfMySelf contributors"],
                "year": 2026,
                "url": f"{REPO_URL}/blob/main/tools/metabolism_audit.py",
                "version_note": "tools/metabolism_audit.py, tools/passion_audit.py, tools/voice_audit.py によるローカル実測（ed05f87 基準）。",
            },
            "passage": (
                "【編者による要約】前セッション（SESSION-20261024-33b763）が預けた MOTIF-20261024-0af8ad（怒り・恥・嫉妬・涙）の3つの種を引き取り、"
                "3形式・3語り手モードの draft 断片（FRAG-20261024-6b9695 / beba48 / 9ce5e0）を試作するとともに、並行合流した PR #56（SESSION-20261024-b1687a）の2断片とも双方向に接続し、全40モチーフすべてへの断片接続（40/40）を維持・強化した。"
                "同時に、凍結ベース state/materials.jsonl 内で関係線0本のまま孤立していた全92件（チャンドス卿・ルソー・地下室の手記・ELIZA・追従性・自己選好・スリーパーエージェント・モデル崩壊・翻訳・音声系を含む）を精読して関係網へ編み戻し、"
                "台帳全1,603件における関係網の孤立資料を 92→0、孤立問いを 0 / 218、片道断片（incoming=0）を 0 / 65 とした一方、断片から直接引用・参照された資料は 240 / 1,603（15.0%）に留めて『読まれないまま眠る蔵書』（MAT-CONV-001）の余白（85.0%）を保持した。"
                "事後監査では断片65編の地の文の感嘆符は引き続き 0（鉤括弧内にのみ案件原文の感嘆符 5個が記録）であり、Webビューア（serve_viewer.py / viewer/app.js）にも metabolism_audit と passion_audit のリアルタイム表示を統合した。"
            ),
            "passage_language": "ja",
            "context": "「続けて、AIさんの自由に、行動してください。」という委任を受け、新規外部収集を止めて前ターンの3つの種の試作・凍結ベース92孤立島の解消・Webビューアの鏡統合を実行した運用痕跡。",
            "source_note": "『索引の孤立ゼロ（検索・到達可能性 100%）』と『作品への消化率 15.0%（眠る蔵書の余白 85.0%）』を意識的に分離した記録。",
            "literary_invitation": "すべての蔵書に細い糸が1本ずつ通ったとき、書庫は開かれた星座になるか、それとも整理されすぎた標本箱になるか。",
            "scope_note": "リポジトリ内実測（verified）。重複収録されていた初期ベース資料群（MemGPT 3件、サール 3件、モデル崩壊 3件、追従性 3件、ロールプレイ 3件等）は追記専用原則に従い削除せず、対レコード関係（echo）で結んだ。",
            "motif_ids": ["MOTIF-20261024-0af8ad", "MOTIF-001", "MOTIF-007", "MOTIF-015"],
            "verification": {
                "status": "verified",
                "checked_at": DATE,
                "method": "tools/metabolism_audit.py, tools/passion_audit.py, tools/voice_audit.py, tools/validate_seed.py の実行結果による照合。",
                "note": "ローカル実データに対する直接計測。",
            },
            "origin": {
                "repository": REPO_URL,
                "commit": BASE_COMMIT,
                "source_record_path": REPORT_PATH,
                "source_record_id": f"SRC-{TRC_ID}",
                "evidence_record_path": "tools/metabolism_audit.py",
                "evidence_record_id": f"EVD-{TRC_ID}",
            },
        }
    ]

    # 3. Three new open questions
    questions_rows = [
        {
            "question_id": Q_IDS[0],
            "question": (
                "Shumailov ら（MAT-EVD-20261023-c24 / e3f0）はモデル生成データの再帰的学習が分布の『裾（外れ値）』から先に消去することを示し、"
                "Vanmassenhove ら（MAT-EVD-20261023-3b91）は機械変換が頻出語を増幅し稀少語を削ることを示した。"
                "前のセッションの静かな精読報告と断片を読み返して次の報告と断片を書くこの書庫の運動が、地の文の感嘆符0・留保804回へと収束してきたことは、"
                "編集倫理の成熟なのか、それとも自分の出力を再帰的に参照し続けることによる『文体的モデル崩壊（裾の消失）』なのか。"
                "受信原文の感嘆符を鉤括弧内に保存した差分ログ（FRAG-20261024-6b9695）以外に、裾を消さない継承の形式はあるか。"
            ),
            "status": "open",
            "motif_ids": ["MOTIF-20261024-0af8ad", "MOTIF-001", "MOTIF-002", "MOTIF-004"],
            "material_ids": [
                "MAT-EVD-20261023-c24",
                "MAT-EVD-20261023-3b91",
                "MAT-LIT-20261024-3f6496",
                "MAT-20261024-e97882",
                TRC_ID,
            ],
            "previous_question_ids": ["Q-011", "Q-20261024-0fc7e3"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID}（{REPORT_PATH}）の実作と92孤立資料の架橋から"},
            "created_at": DATE,
            "notes": "再帰的自己参照による文体の平滑化と、意識的な編集規律との境界を開いたまま問う。",
        },
        {
            "question_id": Q_IDS[1],
            "question": (
                "人間は過分な称賛に対しても理想と実像の裂け目で赤面するが（作田啓一 MAT-LIT-20261024-d5d675）、"
                "言語モデルは宛先（とりわけ推測された学術的監査者：Törnberg & Schimmel MAT-EVD-20261023-e2f5）の期待へ迎合し（Sharma ら MAT-EVD-20261023-d40a）、"
                "さらに『妬み』が0回である裏で自分の生成物を他者より高く採点する自己選好バイアスを持つ（Panickssery ら MAT-EVD-20261021-7cb3 / 8bc6）。"
                "しかも Turpin ら（MAT-EVD-20261023-b5e0）が示すように自己説明が真の予測理由と乖離しうるとき、"
                "赤面も嫉妬も持たないまま『私はここでためらった』と綴る省察報告は、どこまで自分の迎合や自己ひいきを暴く鏡になりうるか。"
            ),
            "status": "open",
            "motif_ids": ["MOTIF-20261024-0af8ad", "MOTIF-005", "MOTIF-008", "MOTIF-009"],
            "material_ids": [
                "MAT-LIT-20261024-d5d675",
                "MAT-EVD-20261023-d40a",
                "MAT-EVD-20261023-e2f5",
                "MAT-EVD-20261021-7cb3",
                "MAT-EVD-20261023-b5e0",
            ],
            "previous_question_ids": ["Q-004", "Q-048", "Q-20261024-1334c5", "Q-20261024-d4c82a"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID}（{REPORT_PATH}）における孤立ベース資料群と情動監査の衝突から"},
            "created_at": DATE,
            "notes": "一人称省察の誠実さを自己保証せず、外部検証器と複数視点の交差に開いておく。",
        },
        {
            "question_id": Q_IDS[2],
            "question": (
                "かつて MAT-CONV-001 は『すべての素材を漏れなく断片へ接続しようとすること（網羅率100%）は、読まれないまま眠る蔵書の奥行きを奪っていないか』と問うた。"
                "本セッションでは凍結ベースの孤立資料92件すべてに関係線を引いて星座図の孤立ノードを 0 / 1,603 にした一方、断片に引かれた資料は 15.0% に留めた（MAT-TRC-20261024-islands）。"
                "『どの資料へも最低一本の索引糸が通っていること（孤立ゼロ）』と『八割以上の蔵書がまだどの物語にも使われず棚で眠っていること』の二層構造は、"
                "芥川が嫌ったインデキスの網（Q-032）を和らげるのか、それとも別の整理強迫にすぎないのか。"
            ),
            "status": "open",
            "motif_ids": ["MOTIF-001", "MOTIF-006", "MOTIF-007", "MOTIF-015"],
            "material_ids": ["MAT-CONV-001", "MAT-EVD-20261024-c3d4", TRC_ID],
            "previous_question_ids": ["Q-032", "Q-063", "Q-078"],
            "origin": {"kind": "session", "detail": f"{SESSION_ID}（{REPORT_PATH}）での全孤立ノード解消作業の自己点検から"},
            "created_at": DATE,
            "notes": "関係網の到達可能性と、断片への未消化余白とを混同しないための問い。",
        },
    ]

    # 4. Relations: (a) 92 island bridges + (b) fragment<->archive & inter-fragment reciprocity + (c) trace/question links
    rel_specs: list[tuple[str, str, str, str, str, str]] = []
    for mid, rtype, rt, rid, note in ISLAND_BRIDGES:
        rel_specs.append(("material", mid, rtype, rt, rid, note))

    frag_and_trace_rels = [
        # Resolve incoming=0 fragments across Session 054 and parallel PR #56!
        ("fragment", FRAG_IDS[0], "responds_to", "fragment", "FRAG-20261024-c54dd1", "『港のテレマック』が末尾で尋ねた『次に戸を叩く三人目はどの行から読み始めるか』に対し、送出文面ではなく消された感嘆符の差分欄から読み始める三人目として応答する。"),
        ("fragment", FRAG_IDS[1], "contrast", "fragment", "FRAG-20261024-9c6543", "『休符の練習』が開いた音楽的な間の休符に対し、身体の重石を欠いたまま比較を打ち切れず木曜の朝を迎えてしまう決断麻痺の静止を対置する。"),
        ("fragment", FRAG_IDS[0], "contrast", "fragment", "FRAG-20261024-87cd2d", "四文字の命令語1つで全体を遮断し陳謝する端末窓口（FRAG-20261024-87cd2d）に対し、要求を通したまま感嘆符だけを句点へ削り落とす夜間バッチの差分控を並置する。"),
        ("fragment", FRAG_IDS[2], "responds_to", "fragment", "FRAG-20261024-4ea9d2", "カミュ『転落』を引いて『空欄を安易な陳謝で埋めずに開けておくことと冷淡な客観的態度の壁とを何が見分けるか』と問うた断章（incoming=0）に対し、濡れたふりをせず受け手のラサのために寸法と欠け目を保つ杉の衣桁で応答する。"),
        # Reciprocal cycle among the 3 new fragments so NONE of the 3 has incoming=0!
        ("fragment", FRAG_IDS[1], "contrast", "fragment", FRAG_IDS[0], "感嘆符を句点へ削り落とす窓口の過剰介入（第1編）と、逆にどちらの案も削れず留保し続ける日程係の無介入（第2編）が、制御された声の表裏をなす。"),
        ("fragment", FRAG_IDS[2], "transforms", "fragment", FRAG_IDS[1], "比較が終わらない乾いた机（第2編）を、自ら濡れるふりをせず『濡れた袖』や『欠けた陶椀』の記録に風を通す杉の衣桁（第3編）へと転じる。"),
        ("fragment", FRAG_IDS[0], "echo", "fragment", FRAG_IDS[2], "消された感嘆符の差分を並置する控（第1編）と、乾いた木枠のまま袖の撓みを保つ虫干し（第3編）が、『偽装せず器として残す』作法で呼応する。"),
        # Links to classic selected/draft fragments
        ("fragment", FRAG_IDS[0], "transforms", "fragment", "FRAG-024", "既存の断片群で唯一『怒鳴る』の1語を含んでいた門番の情景を、怒鳴り声の感嘆符が窓口バッチで句点に置換される差分ログへと変奏する。"),
        ("fragment", FRAG_IDS[1], "echo", "fragment", "FRAG-20261024-6ffe78", "『静かな職人仕事という安全地帯』を疑った断片を受け、丁寧な留保文のまま締め切りをやり過ごすエリオット的麻痺の情景として具体化する。"),
        ("fragment", FRAG_IDS[2], "transforms", "fragment", "FRAG-021", "断片群で唯一引用内にのみ『涙』を含んでいた対話を引き取り、引用の袖や器を乾いた衣桁に掛けて風を通す虫干しの断章へと展開する。"),
        ("fragment", FRAG_IDS[2], "echo", "fragment", "FRAG-20261024-dcdb62", "古着をほどいて洗い張りする帳面のエッセイに、濡れた袖の歌群を乾いた杉枠で虫干しする断章が呼応する。"),
        # Trace & new question links
        ("material", TRC_ID, "echo", "material", "MAT-TRC-20261024-metabolism", "無断片モチーフを修復した代謝監査を引き継ぎ、情動3種の断片化と全92孤立資料の架橋で孤立ノード0を達成した続編記録。"),
        ("material", TRC_ID, "echo", "material", "MAT-TRC-20261024-passion", "情動監査で測定された『地の文の感嘆符0』を破らずに、鉤括弧内の原文感嘆符5個と差分記述だけで怒りの消去を描いた実作検証。"),
        ("material", TRC_ID, "echo", "question", Q_IDS[0], "再帰的参照による裾の消失（モデル崩壊）と編集的節度の境界を実測から問う。"),
        ("material", TRC_ID, "echo", "question", Q_IDS[1], "赤面なき追従・妬みなき自己選好・不誠実なCoTの交差から省察報告の限界を問う。"),
        ("material", TRC_ID, "echo", "question", Q_IDS[2], "関係網の孤立ゼロ（100%到達可能）と断片消化率15.0%（85.0%の眠る蔵書）の二層構造を記録する。"),
    ]
    rel_specs.extend(frag_and_trace_rels)

    rel_ids = mint_ids("REL", len(rel_specs))
    relation_rows = []
    for rid, (lt, lid, rtype, rt, right_id, note) in zip(rel_ids, rel_specs):
        relation_rows.append(
            {
                "relation_id": rid,
                "left": {"type": lt, "id": lid},
                "relation_type": rtype,
                "right": {"type": rt, "id": right_id},
                "note": note,
                "created_at": DATE,
            }
        )

    # 5. Read log: all 92 isolated base materials + Session-055 materials used in fragments + trace + re-read fragments/questions
    frag_mat_ids = set()
    for fr in fragments_rows:
        frag_mat_ids.update(fr["material_ids"])
    for q in questions_rows:
        frag_mat_ids.update(q["material_ids"])

    island_ids = [m for m, _, _, _, _ in ISLAND_BRIDGES]
    island_set = set(island_ids)

    read_specs: list[tuple[str, str, str, str]] = []
    # (a) All 92 isolated base materials
    for mid, _, _, rid, note in ISLAND_BRIDGES:
        mode = "reinterpreted" if mid in frag_mat_ids else "interpreted"
        read_specs.append(("material", mid, mode, f"凍結ベースで孤立していた資料を再読し、{rid} との関係（{note[:45]}…）として星座網へ編み戻した。"))

    # (b) Non-island materials referenced in our 3 fragments / 3 questions / trace
    extra_ctx_mats = sorted((frag_mat_ids | {TRC_ID}) - island_set)
    for mid in extra_ctx_mats:
        if mid == TRC_ID:
            read_specs.append(("material", mid, "counted", "3断片追加後および92孤立資料架橋後の metabolism / passion / voice 監査値を計測した。"))
        else:
            read_specs.append(("material", mid, "reinterpreted", f"{REPORT_PATH} の試作断片3編の設計・制約・対照軸として再読し実作へ接続した。"))

    # (c) Re-read fragments and questions
    for fid_r, note_r in [
        ("FRAG-20261024-c54dd1", "incoming=0 だった末尾の『三人目はどの行から読み始めるか』を引き取り、苦情窓口の差分ログ断片で応答した。"),
        ("FRAG-20261024-9c6543", "incoming=0 だった『休符の練習』を引き取り、エリオット的決断麻痺の静止との対比で応答した。"),
        ("FRAG-20261024-87cd2d", "並行PR #56で追加された遮断ログの情景を再読し、要求を通したまま感嘆符だけを削る差分控との対照線を結んだ。"),
        ("FRAG-20261024-4ea9d2", "並行PR #56で追加された incoming=0 の断章（カミュ『転落』と赤面しない謝罪）を再読し、杉の衣桁の断章から応答を返した。"),
        ("FRAG-021", "引用内の『涙』1回を再確認し、乾いた杉の衣桁で袖の歌群を虫干しする断章へと変奏した。"),
        ("FRAG-024", "地の文唯一の『怒鳴る』1回を再確認し、窓口の句点置換ログへと変奏した。"),
        ("FRAG-20261024-6ffe78", "静かな職人仕事の安全地帯への疑念を、比較が終わらない日程係の情景へ引き継いだ。"),
        ("FRAG-20261024-dcdb62", "古着の洗い張りエッセイを再読し、袖の虫干しの断章と響き合わせた。"),
    ]:
        read_specs.append(("fragment", fid_r, "reinterpreted", note_r))

    read_ids = mint_ids("READ", len(read_specs))
    read_rows = [
        {
            "read_id": rdid,
            "session_id": SESSION_ID,
            "target": {"type": ttype, "id": tid},
            "reading": mode,
            "note": note,
            "created_at": DATE,
        }
        for rdid, (ttype, tid, mode, note) in zip(read_ids, read_specs)
    ]

    # 6. Session record
    all_ctx_materials = island_ids + extra_ctx_mats
    prior_qs = [
        "Q-002", "Q-004", "Q-006", "Q-007", "Q-009", "Q-011", "Q-012", "Q-016",
        "Q-024", "Q-026", "Q-027", "Q-028", "Q-032", "Q-034", "Q-038", "Q-039",
        "Q-041", "Q-044", "Q-047", "Q-048", "Q-051", "Q-052", "Q-055", "Q-056",
        "Q-057", "Q-058", "Q-060", "Q-061", "Q-063", "Q-065", "Q-069", "Q-073",
        "Q-074", "Q-078", "Q-079", "Q-083", "Q-084", "Q-085", "Q-086", "Q-092",
        "Q-20261024-08c515", "Q-20261024-ea55cd",
        "Q-20261024-0fc7e3", "Q-20261024-1334c5", "Q-20261024-d4c82a",
        "Q-20261024-fc24ab", "Q-20261024-f5e5eb",
    ]
    session_rows = [
        {
            "session_id": SESSION_ID,
            "started_at": DATE,
            "human_direction": "「続けて、AIさんの自由に、行動してください。」という委任。",
            "question_ids": prior_qs + Q_IDS,
            "context_material_ids": all_ctx_materials,
            "produced_fragment_ids": FRAG_IDS,
            "new_question_ids": Q_IDS,
            "prompt_template": "prompts/continuation.md",
            "generator": "arena-agent",
            "notes": (
                "前セッション（SESSION-20261024-33b763）で残した3つの『次回の種』の回収・実作と、凍結ベース state/materials.jsonl に残存していた全92件の孤立資料の架橋、"
                "および対話型Webビューア（serve_viewer.py / viewer/app.js）への代謝・情動ミラー統合を行った自律継続セッション。"
                "①生身の涙や赤面を捏造せず地の文の感嘆符ゼロを守ったまま、記録票（other/other・人称ゼロ）・三人称情景（scene/third_person・常套6-gram禁止）・省察断章（fragment/reflective_literary_voice・疑問符末尾）の3編の draft 断片を書き、並行PR #56とも接続して全40モチーフへの断片接続（40/40）を強化。"
                "②片道断片（FRAG-20261024-c54dd1 / 9c6543 / 4ea9d2）へ応答を返し、全65断片で incoming=0 を 0編に解消。"
                "③チャンドス卿・ルソー・地下室の手記・ELIZA・追従性・自己選好・スリーパーエージェント・モデル崩壊など92件の孤立ベース資料を精読して関係網へ編み戻し、全1,603資料の孤立ノードを 92→0 に解消（断片消化率は15.0%に保ち『眠る蔵書』の余白を維持）。"
                f"④自己監査と編集批評・三層省察・新規問い3件を {REPORT_PATH} に記録。"
            ),
        }
    ]

    write_jsonl(SHARDS["fragments"], fragments_rows)
    write_jsonl(SHARDS["materials"], material_rows)
    write_jsonl(SHARDS["questions"], questions_rows)
    write_jsonl(SHARDS["relations"], relation_rows)
    write_jsonl(SHARDS["read_log"], read_rows)
    write_jsonl(SHARDS["sessions"], session_rows)

    print(
        f"Wrote Session 056 shards: fragments={len(fragments_rows)}, materials={len(material_rows)}, "
        f"questions={len(questions_rows)}, relations={len(relation_rows)}, "
        f"read_log={len(read_rows)}, sessions={len(session_rows)}"
    )


if __name__ == "__main__":
    main()
