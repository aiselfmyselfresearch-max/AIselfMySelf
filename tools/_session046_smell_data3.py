"""Materials for SESSION smell (group 5 and the project trace)."""

GROUP5 = "第5群 香を商う、香を送る——手仕事、交易、そして葬送"

ENTRIES = [
    # ---------------- 第5群 ----------------
    dict(
        key="ranjatai",
        group=GROUP5,
        title="正倉院の香木「蘭奢待」——切り取られた記録のほうが残る",
        passage="【編者による要約】正倉院に伝わる巨大な香木「蘭奢待」は、権力者によって切り取られ、その切り取りの記録が残る。香木は、匂いそのものより、誰が触れたかの記録として価値を持つ。",
        context="匂いの対象が来歴の記録になる例。台帳と匂いの交点。",
        source_note="正倉院宝物と、織田信長による切り取りの逸話に関する一般的記述の要約。",
        invitation="切り取られた香木の匂いと、切り取った記録は、どちらが保存されているか。",
        authors=["（正倉院）"], year=756,
        url="https://shosoin.kunaicho.go.jp/",
        status="partially_verified",
        note="信長の切り取りは広く語られるが、一次史料の確認は未確認。年は伝来の便宜的な値。",
        also=["MOTIF-001", "MOTIF-015"],
    ),
    dict(
        key="vanillin_1874",
        group=GROUP5,
        title="バニリンの合成（1874）——同じ分子を、工場で作る",
        passage="【編者による要約】ハールマンとティーマンが針葉樹の成分からバニリンを合成し、香料の工業生産が始まる。天然の抽出に代えて、同じ分子を工場で作る。",
        context="匂いの複製が可能になった転換点。",
        source_note="1874年のバニリン合成と工業化に関する一般的記述の要約。",
        invitation="同じ分子なら同じ匂いか。違うとすれば、何が違うのか。",
        authors=["Wilhelm Haarmann", "Ferdinand Tiemann"], year=1874,
        url="https://www.acs.org/education/whatischemistry/landmarks/vanillin.html",
        status="partially_verified",
        note="年と人名は広く知られるが、一次文献は未確認。",
        also=["MOTIF-016", "MOTIF-20261024-504a22"],
    ),
    dict(
        key="grasse_glovers",
        group=GROUP5,
        title="グラースのなめし革と香水——悪臭を消す技術が、香りの産業になる",
        passage="【編者による要約】南フランスのグラースでは、なめし革の悪臭を消すために香料が使われ、やがて香水産業が育つ。悪臭を隠す技術が、香りの産業になる。",
        context="悪臭と香水が同じ産業の表裏である点。",
        source_note="グラースの皮革業と香料産業の移行に関する一般的記述の要約。",
        invitation="匂いを消す技術と、匂いを作る技術は、同じ技術か。",
        authors=["（地域史）"], year=1600,
        url="https://whc.unesco.org/en/list/1633/",
        status="partially_verified",
        note="年は移行期の便宜的な値。一次資料は未確認。",
        also=["MOTIF-012", "MOTIF-016"],
    ),
    dict(
        key="kodo_kumiko",
        group=GROUP5,
        title="香道の組香——匂いを当てる、照合する、記録する",
        passage="【編者による要約】複数の香木を焚き、匂いの同異を当てる遊びが、作法と記録の体系として整えられる。匂いは比較され、名づけられ、帳面に記される。",
        context="匂いを照合する実践。書庫の読み比べとの相同。",
        source_note="香道の組香と聞香の作法に関する一般的記述の要約。流派による差異は扱わない。",
        invitation="匂いを当てることは、資料を同定することと何が違うか。",
        authors=["（香道）"], year=1500,
        url="https://www.kodojapan.com/",
        status="partially_verified",
        note="成立年代は流派により大きく異なる。年は便宜的な値。",
        also=["MOTIF-008", "MOTIF-015"],
    ),
    dict(
        key="cremation_smoke",
        group=GROUP5,
        title="火葬場と煙——死の匂いを、都市の郊外へ移す",
        passage="【編者による要約】近代の都市では、火葬場が住宅地から郊外へ移され、煙と匂いが問題として管理される。葬送の匂いは、日常の視界から遠ざけられ、儀礼から衛生の問題へと移される。",
        context="焼香・線香が0回という計数の背景に、葬送の脱臭という近代の過程を置くため。",
        source_note="日本の近代都市における火葬場の郊外移転と煙害・臭気問題に関する一般的記述の要約。",
        invitation="死者の匂いを郊外へ移したとき、弔いは何を失い、何を保ったのか。",
        authors=["（都市史）"], year=1900,
        url="https://www.tokyo-park.or.jp/",
        status="partially_verified",
        note="年は便宜的な値。地域差が大きく、特定の一次資料は未確認。",
        also=["MOTIF-022", "MOTIF-20261024-80516e"],
    ),
    dict(
        key="frankincense_road",
        group=GROUP5,
        title="乳香の隊商路——匂いは長距離を運ばれる商品になる",
        passage="【編者による要約】アラビア半島南部で採れる乳香は、ラクダの隊商によって地中海世界へ運ばれ、宗教と交易の双方を支えた。匂いは長距離交易の商品になる。",
        context="匂いが運ばれるものであり、産地と消費地を分ける点。",
        source_note="乳香交易と隊商路に関する一般的記述の要約。",
        invitation="産地を離れた匂いは、どこまで元の匂いか。",
        authors=["（交易史）"], year=-300,
        url="https://whc.unesco.org/en/list/1010/",
        status="partially_verified",
        note="年は交易の盛期の便宜的な値。一次資料は未確認。",
        also=["MOTIF-20261024-146017", "MOTIF-012"],
    ),
    dict(
        key="agarwood",
        group=GROUP5,
        title="沈香とアクイラリア——傷から生まれる匂い",
        passage="【編者による要約】沈香は、アクイラリア属の木が真菌に感染したときに形成される樹脂で、天然の供給は限られる。乱獲により国際取引が規制される。",
        context="匂いが傷ついた木の反応から生まれるという事実。",
        source_note="沈香の成因と、アクイラリア属の保全に関する一般的記述の要約。",
        invitation="傷から生まれる匂いを、傷をつけて増やすことは、記録の改竄と似ているか。",
        authors=["（CITES）"], year=2022,
        url="https://www.cites.org/eng/app/appendices.php",
        status="partially_verified",
        note="附属書への掲載時期と対象種の範囲は未確認。",
        also=["MOTIF-20261024-504a22", "MOTIF-016"],
    ),
    dict(
        key="jasmine_picking",
        group=GROUP5,
        title="ジャスミン摘み——その日のうちに使わねばならない匂い",
        passage="【編者による要約】グラースの香水原料として、ジャスミンの花は夜明け前に手で摘まれ、その日のうちに抽出される。匂いは労働の時間に縛られる。",
        context="匂いが鮮度を持ち、記録のように保存できない点。",
        source_note="グラースの花摘みと抽出の慣行に関する一般的記述の要約。",
        invitation="その日のうちに使わねばならない記録は、記録と呼べるか。",
        authors=["（地域史）"], year=1900,
        url="https://whc.unesco.org/en/list/1633/",
        status="partially_verified",
        note="年は慣行の便宜的な値。一次資料は未確認。",
        also=["MOTIF-012", "MOTIF-017"],
    ),
    dict(
        key="ai_perfumery",
        group=GROUP5,
        title="AI調香——経験は、データとモデルに部分的に移される",
        passage="【編者による要約】香料企業が、匂いの知覚データと分子構造を学習させ、処方の候補を生成する取り組みを進めている。調香師の経験は、データとモデルに部分的に移される。",
        context="匂いを生成する側に機械が入る現在。",
        source_note="香料産業における機械学習の利用に関する公開情報の要約。",
        invitation="匂いを生成するモデルは、匂いを知っているのか、知っているように振る舞うのか。",
        authors=["（産業動向）"], year=2025,
        url="https://www.symrise.com/",
        status="unverified",
        note="個別企業の取り組みは公開情報が少なく、年次・手法は未確認。",
        also=["MOTIF-20261024-504a22", "MOTIF-014"],
    ),
]

TRACE = dict(
    key="trace_smell",
    group="運用痕跡",
    title="嗅覚の鏡——55断片・1,240資料・88報告で匂い語彙を測る",
    passage=(
        "【編者による要約】断片55編・26,852字で嗅覚語は5回（匂い2・嗅覚1・臭い1・香り1）、"
        "1万字あたり1.9。同じ地の文で視覚47（17.5）、聴覚61（22.7）、触覚27（10.1）、味覚16（6.0）。"
        "資料1,240件・178,911字では嗅覚6回（0.3）に対し視覚188（10.5）、聴覚145（8.1）、味覚93（5.2）。"
        "報告88本・1,808,083字では嗅覚33回（0.2）に対し視覚1,817（10.0）、聴覚1,737（9.6）。"
        "断片・資料の双方で、線香・焼香・香水・香料・香木・沈香・香辛料はいずれも0回。"
        "匂・嗅・香・臭を含む箇所は断片5・資料7・報告34で、前後30字に付着先の語を持つものは3・5・22。"
        "付着先は他者・身体、家・部屋、紙・文字、記憶、死に偏り、動物は報告に5回だけ現れる。"
    ),
    context="資料選定の前に、既存の断片・資料・報告を同じ語彙表で測った記録。",
    source_note=(
        "この書庫は、最も名高い匂いの場面（マドレーヌ）を二度収録しながら、"
        "それを味と記憶として分類し、匂いとしては数えていない。"
        "匂いは、無いのではなく、他の語に吸収されている。"
    ),
    invitation="語彙の少なさは、感覚の不在の証拠になるか。ならないとすれば、何の証拠になるか。",
    authors=["AIselfMySelf Archive"], year=2026,
    url="https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/olfactory_audit.py",
    status="verified",
    method=(
        "tools/olfactory_audit.py を実行し、base と全シャードの和集合を計数"
        "（fragments 55 / materials 1,240 / readings 88、いずれも本セッション追記前）。"
    ),
    note=(
        "計数は語形であり、意味の判定ではない。単字（匂・嗅・香・臭）は複合語・地名・人名を含むため"
        "群に合算せず別掲した。引用符内は除去していない箇所があるため、報告側の数は上限寄り。"
    ),
    also=["MOTIF-001", "MOTIF-015", "MOTIF-018"],
)
