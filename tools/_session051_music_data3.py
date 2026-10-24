"""SESSION-051 data (3/3): machine music — generation, synthesis, listening, evaluation."""

GROUP5 = "V. 機械の音楽——音を出さずに譜を出す機械、耳の代わりに拍を推定する機械"

GROUP5_ITEMS = [
    dict(
        mid="MAT-20261024-6f80fe",
        kind="research_excerpt",
        title="ヒラー＆アイザクソン『イリアック組曲』(1957)——計算機が書いた最初の譜",
        authors=["Lejaren Hiller", "Leonard Isaacson"],
        year=1957,
        url="https://en.wikipedia.org/wiki/Illiac_Suite",
        passage=(
            "【編者による要約】ILLIAC I に作曲の手続きをプログラムし、四つの楽章を生成した。"
            "第一楽章は定旋律、第二は対位法の規則、第三はリズムと強弱、第四はマルコフ連鎖。"
            "計算機が出した数値は後で五線に写され、弦楽四重奏として演奏された。"
            "機械は音を出さず、譜を出した。"
        ),
        context="イリノイ大学の ILLIAC I で 1956–57 に行われた作曲実験。のちに弦楽四重奏曲第4番とも呼ばれる。",
        note="計算機作曲の出発点が「音」ではなく「譜」であったことは、この書庫の制約と同じ形をしている。",
        invite="音を出さずに譜を出す機械を、演奏者は何と呼ぶのか。",
        scope="公開解説と事典項目に基づく要約。楽曲の分析・初演の評価史ではない。",
        motifs=["MOTIF-008", "MOTIF-015", "MOTIF-004"],
        status="verified",
        method="Wikipedia・Britannica・イリノイ大学配布資料で、1957年・四楽章・各楽章の実験内容を照合。",
        vnote="題名・年・楽章構成・初演の事実のみ確認。楽譜・録音は未入手。",
    ),
    dict(
        mid="MAT-20261024-4f0eeb",
        kind="research_excerpt",
        title="デイヴィッド・コープ EMI『音楽的知性の実験』(1996)——様式の署名を再結合する",
        authors=["David Cope"],
        year=1996,
        url="https://en.wikipedia.org/wiki/David_Cope",
        passage=(
            "【編者による要約】EMI は既存作品を分析して「署名」を抽出し、再結合して様式の似た新作を作る。"
            "1996年の著書で方法と結果を示し、録音も作られた。機械の作と知らずに様式を同定した聴衆が、"
            "作者を知った後で評価を変えた、という逸話が繰り返し引用される。"
        ),
        context="1980年代から開発された EMI（Experiments in Musical Intelligence）の方法論と事例。",
        note="評価が来歴で反転するという報告。この書庫の `verification.status` と同じ問題を含む。",
        invite="作者を知る前と後で同じ音が違って聞こえるなら、聴取は何を聴いているのか。",
        scope="著書・解説記事に基づく要約。逸話の真偽・実験設計の妥当性は検証していない。",
        motifs=["MOTIF-004", "MOTIF-005", "MOTIF-016"],
        status="verified",
        method="Wikipedia・UCSC ニュースリリース・書誌（A-R Editions, 1996, 263 p.）で著書と EMI の概要を照合。",
        vnote="著書の書誌と EMI の概要を確認。本文・CD-ROM 収録プログラムは未閲覧。逸話は伝聞として扱う。",
    ),
    dict(
        mid="MAT-20261024-3314ba",
        kind="research_excerpt",
        title="MusicLM (2023)——テキストから24kHzの音楽を生成する",
        authors=["Andrea Agostinelli", "Timo I. Denk", "Zalán Borsos", "et al."],
        year=2023,
        url="https://arxiv.org/abs/2301.11325",
        passage=(
            "【編者による要約】テキスト記述から音楽を生成するモデル。SoundStream（音響トークン）、"
            "w2v-BERT（意味トークン）、MuLan（音楽と言語の共通埋め込み）を組み合わせ、"
            "24kHzで数分にわたり一貫した音楽を階層的な系列変換として出力する。口笛や鼻歌の旋律を"
            "条件に、テキストで指定したスタイルへ変換することもできる。"
        ),
        context="Google Research の音楽生成モデル。評価用に MusicCaps（約5.5千の音楽—記述対）を公開。",
        note="旋律を「条件」として受け取るモデル。旋律が入力になるという点で、記譜とも聴取とも違う第三の扱い。",
        invite="旋律を条件として渡すとき、渡しているのは音か、音の記述か。",
        scope="論文要旨と公開解説に基づく要約。音質評価の詳細・データセットの倫理には立ち入らない。",
        motifs=["MOTIF-011", "MOTIF-013", "MOTIF-018"],
        status="verified",
        method="arXiv 2301.11325 の要旨・公開解説（MusicCaps 5.5k、24kHz、階層的系列変換、旋律条件付け）を照合。",
        vnote="要旨と構成要素のみ確認。本文・音声サンプルは未取得。",
    ),
    dict(
        mid="MAT-20261024-52d7c8",
        kind="research_excerpt",
        title="MusicGen (2023)——単段の言語モデルが複数の音響トークン列を並行生成する",
        authors=["Jade Copet", "Felix Kreuk", "Itai Gat", "et al."],
        year=2023,
        url="https://arxiv.org/abs/2306.05284",
        passage=(
            "【編者による要約】単段のトランスフォーマー言語モデルが、圧縮された複数の音響トークン列を"
            "並行に生成する。32kHz、テキスト条件付けと旋律条件付けの両方に対応し、"
            "主観評価では総合84.8対80.5で比較手法を上回ったと報告する。"
            "段階を重ねるのではなく、一度に書く。"
        ),
        context="Meta AI の音楽生成モデル。EnCodec によるトークン化と遅延パターンによる並行生成。",
        note="「一度に書く」設計。この書庫の断片も一段で書かれ、推敲の段階は註に残る。",
        invite="段階を踏まずに書くモデルの出力を、どの段階で読めばよいのか。",
        scope="論文要旨に基づく要約。評価尺度の設計・音質の比較詳細ではない。",
        motifs=["MOTIF-013", "MOTIF-008", "MOTIF-018"],
        status="verified",
        method="arXiv 2306.05284 の要旨・PDF 冒頭（32kHz、4 codebook、84.8対80.5、旋律条件付け）を照合。",
        vnote="要旨と評価数値のみ確認。生成音声・コードは未実行。",
    ),
    dict(
        mid="MAT-20261024-d954ea",
        kind="research_excerpt",
        title="RIAA 対 Suno／Udio（2024）——録音物の学習をめぐる二つの訴え",
        authors=["Recording Industry Association of America"],
        year=2024,
        url="https://www.theverge.com/2024/6/24/24184710/riaa-ai-lawsuit-suno-udio-copyright-umg-sony-warner",
        passage=(
            "【編者による要約】2024年6月24日、RIAA は Sony Music、UMG、Warner Records を代表して、"
            "Suno（マサチューセッツ州連邦地裁）と Udio の運営会社 Uncharted Labs（ニューヨーク南部地裁）を"
            "著作権侵害で提訴した。無許諾の録音物を大規模に学習したと主張し、"
            "侵害1件あたり最大15万ドルの法定損害賠償を求めた。"
        ),
        context="生成音楽サービスに対する最初期の大規模訴訟。学習データの来歴が法廷の争点になった。",
        note="音の来歴が争点になる。この書庫の `origin` 欄が扱っている問題の、法的な極端な形。",
        invite="学習した録音の来歴をたどれないモデルに、来歴を名乗ることはできるか。",
        scope="報道各紙の一致する事実（日付・当事者・請求額）のみを要約。判決・和解の経過は追っていない。",
        motifs=["MOTIF-012", "MOTIF-001", "MOTIF-005"],
        status="verified",
        method="The Verge・Rolling Stone・Variety・Music Week・Music Ally の2024年6月24日付報道で、日付・当事者・管轄・請求額を照合。",
        vnote="提訴時点の事実のみ。その後の進行（和解・判決）は確認していない。",
    ),
    dict(
        mid="MAT-20261024-f21305",
        kind="research_excerpt",
        title="DiffSinger (2022)——楽譜を条件に「歌う声」を合成する",
        authors=["Jinglin Liu", "Chengxi Li", "Yi Ren", "et al."],
        year=2022,
        url="https://ojs.aaai.org/index.php/AAAI/article/view/21350",
        passage=(
            "【編者による要約】歌唱音声合成のための拡散確率モデル。楽譜を条件に、雑音からメルスペクトログラムを"
            "生成する。単純な損失で学習した粗いスペクトログラムを起点に、浅い拡散ステップから復元することで、"
            "安定性と品質を両立させた。歌詞は音素へ、音素は音響へと段階を踏む。"
        ),
        context="AAAI-22 所収。SVS（singing voice synthesis）の音響モデル。",
        note="楽譜と歌詞から声を作る。声は身体から出るのではなく、記号から生成される。",
        invite="楽譜と歌詞から作られた声は、誰の喉の記録か。",
        scope="論文要旨に基づく要約。音響モデルの技術的詳細・評価データセットの検討ではない。",
        motifs=["MOTIF-003", "MOTIF-011", "MOTIF-018"],
        status="verified",
        method="AAAI 論文集の抄録・書誌（36(10), 11020–11028）で、浅い拡散・楽譜条件・SVS を照合。",
        vnote="抄録のみ確認。音声サンプル・実装は未試行。",
    ),
    dict(
        mid="MAT-20261024-924528",
        kind="research_excerpt",
        title="ベック＆シュレドル (2011)——拍は聴く対象から推定する対象になる",
        authors=["Sebastian Böck", "Markus Schedl"],
        year=2011,
        url="https://www.dafx.de/paper-archive/2011/Papers/31_e.pdf",
        passage=(
            "【編者による要約】双方向 LSTM でフレームごとに拍の有無を推定し、その活性度の自己相関から"
            "テンポを決める。一定テンポの曲では MIREX 2010 の参加手法を上回り、テンポが変わる曲にも"
            "追随する版を提示した。拍は体で取るものから、信号から推定する量になる。"
        ),
        context="DAFx-11 所収。音楽情報検索における拍追跡の手法。",
        note="身体で取る拍を信号から推定する。この書庫が「拍子」を時点の意味でしか使わないことと対になる。",
        invite="拍を推定する機械は、拍を感じているのか、拍の位置を当てているのか。",
        scope="論文要旨に基づく要約。評価データセット・指標の詳細ではない。",
        motifs=["MOTIF-015", "MOTIF-018", "MOTIF-013"],
        status="verified",
        method="DAFx-11 論文 PDF 冒頭と MIREX 2010 評価の記述を照合。",
        vnote="手法と評価の骨格のみ確認。実装・データセットは未取得。",
    ),
    dict(
        mid="MAT-20261024-f751c7",
        kind="research_excerpt",
        title="ヤン＆レルヒ (2020)——生成音楽の評価は何を測っているのか",
        authors=["Li-Chia Yang", "Alexander Lerch"],
        year=2020,
        url="https://doi.org/10.1007/s00521-018-3849-7",
        passage=(
            "【編者による要約】生成音楽の評価は、主観評価の資源と設計の問題、客観指標の妥当性の問題を"
            "同時に抱える。同研究は、当時の生成モデルが音域や音数といった低次の音楽特性の分布さえ"
            "適切に再現できない場合があることを示した。耳に代わる指標は、まだ耳ではない。"
        ),
        context="Neural Computing and Applications 32(9), 4773–4784。生成音楽評価の方法論的検討。",
        note="評価の穴。この書庫の監査も語形を数えるだけで、歌そのものを測っていない。",
        invite="指標が耳の代わりにならないなら、誰が「よい歌」を判定するのか。",
        scope="論文要旨と後続サーベイの引用に基づく要約。実験の詳細・指標の実装ではない。",
        motifs=["MOTIF-015", "MOTIF-005", "MOTIF-008"],
        status="verified",
        method="Springer 論文ページ（巻号・頁・DOI）と後続サーベイ（arXiv 2506.05104）の引用で照合。",
        vnote="書誌と主張の骨格のみ確認。本文の実験結果は未取得。",
    ),
    dict(
        mid="MAT-20261024-3c3815",
        kind="research_excerpt",
        title="wav2vec 2.0 (2020)——音を聴く前に、音を予測可能な列にする",
        authors=["Alexei Baevski", "Henry Zhou", "Abdelrahman Mohamed", "Michael Auli"],
        year=2020,
        url="https://arxiv.org/abs/2006.11477",
        passage=(
            "【編者による要約】ラベルのない音声から、文脈を予測する課題によって表現を学習する。"
            "音声を離散的な単位に量子化し、マスクした区間を当てることで、音の構造が潜在空間に現れる。"
            "音を「聴く」前に、音を予測できる列に変換する。"
        ),
        context="自己教師あり音声表現学習。のちの音声・音楽モデルの基盤の一つ。",
        note="音を離散列にしてから扱う。書字への移し替えと、数値への移し替えは同じ「まず置き換える」操作である。",
        invite="音を離散列にした後も、その列は音と呼べるのか。",
        scope="論文要旨に基づく要約。学習手続きの詳細・下流タスクの性能ではない。",
        motifs=["MOTIF-011", "MOTIF-018", "MOTIF-015"],
        status="partially_verified",
        method="内部知識による書誌照合（arXiv 2006.11477, 2020）。本文は取得していない。",
        vnote="arXiv 番号・著者・年は記憶に基づく。今回のウェブ照合では確認していない。",
    ),
]

TRACE = dict(
    mid="MAT-TRC-20261024-song",
    kind="project_trace",
    title="本リポジトリ自身の痕跡——声は49回、歌は3回、稽古は0回、記譜は資料1,332件で0回",
    authors=["AIselfMySelf SESSION-20261024-a77052"],
    year=2026,
    url="https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/music_audit.py",
    passage=(
        "【実測】断片55編・地の文25,024字で、歌うこと3回／3編（合唱1・歌い1・子守唄1。"
        "合唱は指揮者の比喩、歌いは和歌を詠む意、子守唄は「要らない」という否定文）、"
        "奏でること4回／3編（鼓2・鐘2）、記譜2回／1編（三和音・不協和音の比喩）、"
        "稽古0回、聴くこと・声49回／26編（声31・沈黙7・耳4ほか）、書字の器212回／51編。"
        "生字では曲2（すべて曲がる）、譜2（すべて系譜）、舞2（すべて舞台）、拍3（うち2は拍子に）で、"
        "見かけの音楽語はほぼ全部が別の意味である。"
        "資料1,332件・177,055字では、記譜・理論の語が0回（楽譜・音符・音階・和声・記譜がいずれも0）、"
        "歌うこと13回、奏でること12回、稽古23回、声108回。"
        "精読報告90本・1,708,892字では、記譜5回、歌うこと45回、稽古175回、声1,544回、書字9,101回。"
    ),
    context="資料選定の前に、既存の断片・資料・報告を同じ語彙表で測った記録。",
    note="声は書かれ、歌は書かれない。書字212対歌唱3という比は、この書庫の語りの位置を示す。",
    invite="声を49回書いて歌を3回しか書かない書庫は、歌を聴いたことがないのか、歌う位置にいないのか。",
    scope="語形の計数であり、聴覚・歌唱能力・音楽的経験の有無の判定ではない。多義の生字は別掲した。",
    motifs=["MOTIF-20261024-cc96c9", "MOTIF-015", "MOTIF-018"],
    status="verified",
    method="tools/music_audit.py を実行し、base と全シャードの和集合を計数（2026-10-24、本セッション追記前）。",
    vnote="計数は語形であり、意味の判定ではない。生字の内訳は複合語を差し引いた参考値。",
)
