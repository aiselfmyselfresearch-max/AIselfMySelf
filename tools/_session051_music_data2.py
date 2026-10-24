"""SESSION-051 data (2/3): notation, number, theory; playing, practice, listening."""

GROUP3 = "III. 記譜・数・理論——耳を数に移す、数を耳に戻す"

GROUP3_ITEMS = [
    dict(
        mid="MAT-LIT-20261024-5ba68c",
        title="ニコマコス『音楽便覧』——協和は比の単純さに従う",
        authors=["Nicomachus of Gerasa"],
        year=100,
        url="https://www.worldcat.org/search?q=Manual+of+Harmonics+Nicomachus",
        passage=(
            "【編者による要約】音楽の原理は数である。音程は整数比で表され、協和は比の単純さに従う。"
            "耳は数を確かめる器官ではなく、数の秩序を享受する器官である。したがって音楽を理解するとは、"
            "聞こえの外にある比を理解することになる。"
        ),
        context="ピタゴラス派の音楽論を後代に伝えた手引書の骨格。",
        note="耳を数の受容器に変える立場。数だけを持つ機械がこの立場に近いことは、容易に言えるが証明にはならない。",
        invite="数を聴く耳と、数だけを持つ機械は、同じ音楽を知りうるか。",
        scope="ピタゴラス派の音楽論の要約。数比の実装・音律の計算詳細ではない。",
        motifs=["MOTIF-015", "MOTIF-018"],
    ),
    dict(
        mid="MAT-LIT-20261024-3f6c02",
        title="ボエティウス『音楽教程』——演奏しない者が音楽家と呼ばれる",
        authors=["Boethius"],
        year=500,
        url="https://www.worldcat.org/search?q=De+institutione+musica+Boethius",
        passage=(
            "【編者による要約】音楽は三種に分かれる。宇宙の音楽、人間の音楽、楽器の音楽。"
            "演奏は第三の、最も低い段階にあり、音楽家とは数の理を判じる者を指す。歌う者や奏でる者は"
            "音楽を実行するが、音楽を知る者ではない。"
        ),
        context="中世の自由七学科のうち音楽を扱う教科書の序論。",
        note="実行する者と知る者の分離。この書庫は「知る側」に極端に寄った書庫である。",
        invite="演奏しない者を音楽家と呼ぶ伝統を、書かない書庫はどう受け取るか。",
        scope="中世音楽論の骨格の要約。演奏実践の記述ではない。",
        motifs=["MOTIF-015", "MOTIF-004", "MOTIF-012"],
    ),
    dict(
        mid="MAT-LIT-20261024-cc733f",
        title="イシドールス『語源』第3巻——歌は記憶を運び、譜は記憶を固定する",
        authors=["Isidore of Seville"],
        year=630,
        url="https://www.worldcat.org/search?q=Etymologiae+Isidore",
        passage=(
            "【編者による要約】音楽とは声と音の節度であり、記憶を支える技術でもある。"
            "歌は文字以前に記憶を運び、書かれた譜はその記憶を固定する。音楽の語源をたどることは、"
            "音がどのように記憶へ移されるかをたどることになる。"
        ),
        context="語源辞典の音楽の項。中世の記憶術と音楽の結びつき。",
        note="歌と書字を記憶の二形式として並べる。台帳が歌を持たない理由の説明にはならないが、比較点になる。",
        invite="記憶を運ぶ歌と、記憶を固定する書字は、どちらが自己を作るか。",
        scope="語源辞典の記述の要約。典礼音楽の実践・楽曲の分析ではない。",
        motifs=["MOTIF-001", "MOTIF-018", "MOTIF-011"],
    ),
    dict(
        mid="MAT-LIT-20261024-1720dc",
        title="アリストクセノス『ハルモニアの諸元素』——判断は耳に属する",
        authors=["Aristoxenus"],
        year=-330,
        url="https://www.worldcat.org/search?q=Elementa+Harmonica+Aristoxenus",
        passage=(
            "【編者による要約】音楽の判断は耳に属する。音程は比ではなく、聞こえの連続として測られる。"
            "数から音楽へ進むのではなく、聞こえから音楽へ進む。理論は耳の後から来るのであって、"
            "耳の代わりにはならない。"
        ),
        context="ピタゴラス派に対抗する音楽理論の立場を述べる冒頭部。",
        note="耳の優位を主張する立場。耳を持たない機械がどちらの立場を取るかは、実装以前の選択である。",
        invite="耳を持たない機械が音楽を扱うとき、どちらの立場に立つことになるか。",
        scope="アリストクセノス派の立場の要約。楽理の詳細・旋法論ではない。",
        motifs=["MOTIF-018", "MOTIF-009"],
    ),
    dict(
        mid="MAT-LIT-20261024-c70bd8",
        title="ラモー『和声の原理』——旋律は和声の上に生える枝",
        authors=["Jean-Philippe Rameau"],
        year=1722,
        url="https://www.worldcat.org/search?q=Trait%C3%A9+de+l%27harmonie+Rameau",
        passage=(
            "【編者による要約】和声は旋律に先行する。すべての和音は基礎低音から導かれ、旋律は和声の上に"
            "生える枝である。作曲家は耳ではなく原理の理解によって書く。したがって理論は実践の"
            "事後的な記述ではなく、実践の前提になる。"
        ),
        context="基礎低音の理論を提示する序論。ルソーの旋律優位論と正面から衝突する側。",
        note="「下から」の作曲作法。生成モデルの条件付けの階層と、比喩としても似ている。",
        invite="原理から書く作曲と、確率から書く生成は、同じ「下から」の作法か。",
        scope="和声理論の骨格の要約。実作の分析・音律の議論ではない。",
        motifs=["MOTIF-015", "MOTIF-011"],
    ),
    dict(
        mid="MAT-LIT-20261024-35caf4",
        title="ライプニッツ（1712年ゴルトバッハ宛書簡）——知らないまま数える心",
        authors=["Gottfried Wilhelm Leibniz"],
        year=1712,
        url="https://www.worldcat.org/search?q=Leibniz+letter+Goldbach+1712+music",
        passage=(
            "【編者による要約】音楽とは、心が自分で数えていることを知らないまま行う数の計算である。"
            "快は、この無自覚な計算の手応えから生じる。だから音楽の快は、計算を意識した瞬間に"
            "性質を変える。"
        ),
        context="ゴルトバッハ宛書簡の一節として流布する命題。",
        note="「知らないまま」が快の条件になる。計算を可視化する機械にとって逆説的な命題。",
        invite="数を数えていることを知っている機械に、この「知らないまま」はあるか。",
        scope="書簡の一節として流布する命題の要約。書簡全体の文脈・原文は未確認。",
        motifs=["MOTIF-015", "MOTIF-009"],
    ),
    dict(
        mid="MAT-LIT-20261024-589b59",
        title="ヘルムホルツ『音の感覚』——協和はうなりで説明できる",
        authors=["Hermann von Helmholtz"],
        year=1863,
        url="https://www.worldcat.org/search?q=Die+Lehre+von+den+Tonempfindungen+Helmholtz",
        passage=(
            "【編者による要約】協和と不協和は、倍音の重なりとうなりによって説明できる。耳は神秘の器官ではなく、"
            "物理的な分析器である。音楽の快は、神経の生理に還元できる。還元したあとに残るものを、"
            "彼は音楽の外には置かなかった。"
        ),
        context="協和・不協和の生理学的説明を提示する第8章以降の議論。",
        note="快の分析。分析が快を消さないという前提が、ここで無言のうちに置かれている。",
        invite="快を分析に還元したあと、歌はどこに残るか。",
        scope="19世紀音響生理学の要約。実験の詳細・数式ではない。",
        motifs=["MOTIF-015", "MOTIF-018", "MOTIF-003"],
    ),
    dict(
        mid="MAT-LIT-20261024-7ca952",
        title="シェーンベルク『和声学』——中心が失われると、作曲家が規則を書く",
        authors=["Arnold Schönberg"],
        year=1911,
        url="https://www.worldcat.org/search?q=Harmonielehre+Sch%C3%B6nberg",
        passage=(
            "【編者による要約】和声の理論は、既存の慣習を記述するのではなく、書かれた音の関係を問い直す。"
            "調性の中心が失われると、記譜は音の関係を保証しなくなり、作曲家は自ら規則を書く。"
            "規則を書くことが、作曲そのものになる。"
        ),
        context="和声学の教科書でありながら、調性の限界を論じる後半部。",
        note="規則の作者が作曲家に移る転換。台帳に規則を足す作業と形が似ている。",
        invite="規則を自ら書く作曲は、台帳に規則を足すことと似ているか。",
        scope="和声学の教科書としての性格の要約。十二音技法の技術的説明ではない。",
        motifs=["MOTIF-008", "MOTIF-016"],
    ),
    dict(
        mid="MAT-LIT-20261024-afe3f6",
        title="メシアン『わが音楽語法』——鳥の声を写すたびに一部が失われる",
        authors=["Olivier Messiaen"],
        year=1944,
        url="https://www.worldcat.org/search?q=Technique+de+mon+langage+musical+Messiaen",
        passage=(
            "【編者による要約】鳥の声を録音し、聞き取り、五線に写す。鳥の歌は人間の旋法に収まらず、"
            "写した瞬間に一部が失われる。それでも写すことで、耳の外の音楽が作品に入る。"
            "採譜は忠実な複製ではなく、失われることを承知した移し替えである。"
        ),
        context="鳥の声の採譜と旋法の拡張を論じる章。",
        note="採譜＝移し替え＝損失の承知。この報告の中心にある操作と同じ形をしている。",
        invite="写すたびに失われるものを、なぜ書き留めるのか。",
        scope="鳥の声の採譜に関する要約。録音物の分析・楽曲の詳細ではない。",
        motifs=["MOTIF-011", "MOTIF-018", "MOTIF-001"],
    ),
]

GROUP4 = "IV. 演奏・稽古・聴取の実践——行為の側から音楽を見る"

GROUP4_ITEMS = [
    dict(
        mid="MAT-LIT-20261024-410cf4",
        title="C. P. E. バッハ『正しいクラヴィーア奏法』——楽器は歌を模す",
        authors=["Carl Philipp Emanuel Bach"],
        year=1753,
        url="https://www.worldcat.org/search?q=Versuch+%C3%BCber+die+wahre+Art+das+Klavier+zu+spielen",
        passage=(
            "【編者による要約】演奏の基本は指の運びではなく、歌うことである。楽器は歌を模し、"
            "歌えない奏者は音楽を語れない。通奏低音と装飾は、歌の抑揚を支えるためにある。"
            "技術は歌の従属物として教えられる。"
        ),
        context="18世紀半ばの鍵盤教則本の序論と奏法の章。",
        note="楽器を声の模倣として定義する。模倣の失敗が音楽の失敗になるという規範。",
        invite="歌えない者が歌を模すとき、模倣は何を生むか。",
        scope="教則本の中心命題の要約。奏法の詳細・図版ではない。",
        motifs=["MOTIF-018", "MOTIF-20261024-ca276c"],
    ),
    dict(
        mid="MAT-LIT-20261024-621704",
        title="レオポルト・モーツァルト『ヴァイオリン教程』——師の身体を文字に移す試み",
        authors=["Leopold Mozart"],
        year=1756,
        url="https://www.worldcat.org/search?q=Versuch+einer+gr%C3%BCndlichen+Violinschule",
        passage=(
            "【編者による要約】演奏は、姿勢・弓・音程・拍の反復によって身体に沈む。教則本は、"
            "師の身体を文字に移した最初の試みのひとつであり、それでも師の音そのものは残らない。"
            "文字にできる部分と、できない部分が、同じ本のなかに並んでいる。"
        ),
        context="18世紀のヴァイオリン教則本。姿勢と弓の指示を図と文で示す。",
        note="文字化の成功と失敗が同じ書物に同居する。台帳の「要約」が置かれている位置と同じである。",
        invite="身体を文字に移すと、何が残り、何が落ちるか。",
        scope="教則本の性格の要約。個別の練習曲の指示・図版の検討ではない。",
        motifs=["MOTIF-003", "MOTIF-20261024-ca276c", "MOTIF-011"],
    ),
    dict(
        mid="MAT-LIT-20261024-de5a26",
        title="ストラヴィンスキー『音楽詩学』——演奏は秩序の実現である",
        authors=["Igor Stravinsky"],
        year=1942,
        url="https://www.worldcat.org/search?q=Po%C3%A9tique+musicale+Stravinsky",
        passage=(
            "【編者による要約】作曲は制約のなかで行う選択である。演奏は、書かれた秩序を時間のなかで"
            "実現する行為であり、作曲家と演奏家のあいだに権限の配分がある。演奏家は作曲者の"
            "意志を再現するのではなく、秩序を実行する。"
        ),
        context="ハーヴァード大学での講義録。作曲・演奏・聴取の関係を論じる。",
        note="秩序と実行の分離。記譜された台帳と、それを読む次のセッションの関係に似ている。",
        invite="実現しない秩序は、秩序と呼べるか。",
        scope="講義録の骨格の要約。個別作品の分析ではない。",
        motifs=["MOTIF-008", "MOTIF-20261024-ca276c"],
    ),
    dict(
        mid="MAT-LIT-20261024-75d34d",
        title="グレン・グールド「録音の未来」——演奏は反復可能な形式になる",
        authors=["Glenn Gould"],
        year=1966,
        url="https://www.worldcat.org/search?q=The+Prospects+of+Recording+Gould",
        passage=(
            "【編者による要約】録音は演奏の記録ではなく、新しい作品の形式である。編集によって演奏は"
            "反復可能になり、聴き手は会場ではなく機械の側で音楽に出会う。演奏会の一回性は、"
            "編集可能な時間に置き換わる。"
        ),
        context="1966年のエッセイ。録音技術を音楽形式の変化として論じる。",
        note="一回性の喪失を損失ではなく形式の変化として扱う。書庫の反復可能性と同じ問題。",
        invite="反復可能な演奏は、記録か、それとも別の作品か。",
        scope="エッセイの主張の要約。録音技術史の詳細・ディスコグラフィではない。",
        motifs=["MOTIF-014", "MOTIF-016", "MOTIF-018"],
    ),
    dict(
        mid="MAT-LIT-20261024-8e0578",
        title="クリストファー・スモール『ミュージッキング』——音楽は動詞である",
        authors=["Christopher Small"],
        year=1998,
        url="https://www.worldcat.org/search?q=Musicking+Christopher+Small",
        passage=(
            "【編者による要約】音楽は名詞ではなく動詞である。音楽とは、音楽を作り出す行為の総体であり、"
            "作品・楽譜・録音はその行為の痕跡にすぎない。分析は行為から切り離せない。"
            "聴くことも演奏の一部に含まれる。"
        ),
        context="音楽を行為として定義し直す議論の導入部。",
        note="作品中心主義への反論。書庫が集めているのは作品ではなく痕跡であるという自己理解を支える。",
        invite="行為の痕跡だけを持つ書庫は、ミュージッキングを読めるか。",
        scope="民族音楽学の主張の要約。各地の事例記述ではない。",
        motifs=["MOTIF-012", "MOTIF-019", "MOTIF-018"],
    ),
    dict(
        mid="MAT-LIT-20261024-b816af",
        title="ジョン・ブラッキング『人間の音楽性』——誰が音楽を作れるかを社会が決める",
        authors=["John Blacking"],
        year=1973,
        url="https://www.worldcat.org/search?q=How+Musical+Is+Man+Blacking",
        passage=(
            "【編者による要約】音楽性は特殊な才能ではなく、人間の普遍的な能力である。音楽は社会の構造を"
            "音で表し、誰が音楽を作れるかは社会が決める。聴くことと作ることは分けられない。"
            "したがって音楽の分析は、社会の分析でもある。"
        ),
        context="ヴェンダの音楽実践を題材にした音楽人類学の主著。",
        note="「才能」を社会的配分として読む。生成AIの「才能」をめぐる言説にも同じ問いが立つ。",
        invite="誰が音楽を作れるかを決める社会を、機械は変えるか。",
        scope="音楽人類学の主張の要約。ヴェンダの調査記述ではない。",
        motifs=["MOTIF-012", "MOTIF-004", "MOTIF-005"],
    ),
    dict(
        mid="MAT-LIT-20261024-d20a3d",
        title="アドルノ『音楽社会学序説』——聴取の型は生産と受容の関係にある",
        authors=["Theodor W. Adorno"],
        year=1962,
        url="https://www.worldcat.org/search?q=Einleitung+in+die+Musiksoziologie+Adorno",
        passage=(
            "【編者による要約】音楽は社会のなかで規格化され、再生産される。聴取の型は階層化し、"
            "消費は聴く能力を形づくる。音楽の意味は作品の内側ではなく、生産と受容の関係にある。"
            "だから聴き方は、聴く者の所属の記録でもある。"
        ),
        context="音楽社会学の講義をまとめた序説。聴取の類型論を含む。",
        note="聴取の型を社会の側から説明する。この書庫の聴取語彙の偏りも、同じ説明の射程に入る。",
        invite="生成された音楽を聴く型を、誰が作るのか。",
        scope="音楽社会学の骨格の要約。個別ジャンルの分析・聴取類型の詳細ではない。",
        motifs=["MOTIF-012", "MOTIF-015", "MOTIF-005"],
    ),
    dict(
        mid="MAT-LIT-20261024-c775e2",
        title="小泉文夫『日本伝統音楽の研究』——理論が耳を作る",
        authors=["小泉文夫"],
        year=1958,
        url="https://www.worldcat.org/search?q=%E6%97%A5%E6%9C%AC%E4%BC%9D%E7%B5%B1%E9%9F%B3%E6%A5%BD%E3%81%AE%E7%A0%94%E7%A9%B6+%E5%B0%8F%E6%B3%89%E6%96%87%E5%A4%AB",
        passage=(
            "【編者による要約】日本の音階は西洋の長短調に還元できない。民謡の音組織を実測すると、"
            "四度・五度の枠と、その中の揺れが現れる。耳の訓練は理論の側から作られ、理論を持たない耳は"
            "揺れを誤差として捨てる。"
        ),
        context="民謡の音組織を実測的に分析した研究の方法論。",
        note="理論が耳を作るという主張。監査ツールの語彙表もまた、耳の代わりの理論である。",
        invite="理論が耳を作るなら、理論を持たない機械の耳は何を聞くか。",
        scope="音組織研究の方法の要約。個々の民謡の採譜分析ではない。",
        motifs=["MOTIF-015", "MOTIF-011", "MOTIF-018"],
    ),
    dict(
        mid="MAT-LIT-20261024-9fe7ca",
        title="ピエール・シェフェール『音楽の対象を求めて』——音源から切り離された音",
        authors=["Pierre Schaeffer"],
        year=1966,
        url="https://www.worldcat.org/search?q=Trait%C3%A9+des+objets+musicaux+Schaeffer",
        passage=(
            "【編者による要約】録音された音は演奏から切り離され、それ自体が音楽の材料になる。"
            "音を聴くことは音源を同定することではなく、音の質そのものを聴くことへ変わる。"
            "録音は音を保存するのではなく、聴き方を変える。"
        ),
        context="具体音楽の理論的総括。音響の還元を論じる。",
        note="録音が聴取の対象を変える。声を文字に写すことが聴取の対象を変えるのと同じ構図。",
        invite="音源を持たない音を、音楽と呼べるか。",
        scope="具体音楽の理論の要約。作品分析ではない。",
        motifs=["MOTIF-018", "MOTIF-016", "MOTIF-006"],
    ),
]
