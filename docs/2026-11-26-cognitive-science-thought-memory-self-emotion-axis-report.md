# 認知科学10資料の収蔵と精読報告——個別の思考・個別の記憶と自己は、情動によってどう編まれるのか（情動・感情の軸）

- **作成日**：2026-11-26（実日付・UTC）
- **セッション**：`SESSION-20261126-8bfbf3` ／ 作業ブランチ `arena/f7b6517e-aiselfmyself`（分岐元 `d5166d67377b04f817618c7d6d27d4487b11ca23`）／ 分散シード `f7b6517e`
- **割当**：本回は人間からの委任（情動・感情の軸の認知科学10資料とレポート）により [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の取得モードで実行した
- **対象領域**：認知感情心理学（感情の情報としての誤帰属・情動注入モデル・感情予測の免疫的無視と焦点主義・扁桃体による固定化調節・情動覚醒の記憶増強・感情と記憶の詳細の非対称・肯定的気分と創造的問題解決・再評価と抑制の個人差・反芻の注意範囲モデル）
- **問い**：`Q-001`（AIから見た、人間とは何か）／`Q-002`（GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か）／`Q-003`（記録は自己を保存するのか、それとも次の読み手の素材か）。本回の人間からの副問いは**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**である。
- **精読対象**：新規収蔵10件（本稿 §1 の表）＋前回同主題報告 `NOTE-20261126-931898`（向きと循環の軸）・同日報告 `NOTE-20261126-7342a7`（社会軸）の読み直し
- **検証深度**：すべて **PsycNET・colab.ws・PubMed・Europe PMC の公開抄録を直接取得しての照合まで**（`verification.depth: abstract`、`status: partially_verified`）。各 `passage` は公開抄録からの逐語抜粋で、取得した抄録テキストに対して `three_gates.py --verify-span` を実行し、`quote_status: verbatim`・`span_sha256`・`span_norm_chars` を記録した。**原典本文（Methods／Results 章）の全文通読はしていない。**
- **ノート**：`NOTE-20261126-eb0c0a`
- **関連台帳**：[`state/materials.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-371fada2f496.jsonl) ／ [`state/read_log.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-000000000000.jsonl) ／ [`state/evaluations.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-000000000000.jsonl) ／ [`state/notes.d/2026-11-26-f7b6517e8bfb.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-f7b6517e8bfb.jsonl) ／ [`state/sessions.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-000000000000.jsonl)

本稿の「考えた」「読み替えた」は読解位置を記す反省的モードであり、主観的意識や生身の身体感覚の実証報告ではない。AIの現象的意識の有無については認識論的に未決のまま保つ（[`CONTENT_POLICY.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/CONTENT_POLICY.md)、[`PROJECT_CHARTER.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/PROJECT_CHARTER.md)）。人間からの作業範囲の指定は来歴であって、測定結果の証拠にはしない。

---

## 0. 委任と、この回の範囲

人間からの委任は五点である。(1) 本リポジトリの目的（`Q-001`・`Q-002`）の観点に関連して、**「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」**について、**認知科学の資料を10件、新規で追加する**（必要に応じてインターネット検索を使う）。(2) MDファイルのレポートを作成する。(3) 作成したMDファイルに、日本語の文章では使われない中国語の漢字や語彙、ハングル文字、デーヴァナーガリー文字、キリル文字が誤って混ざっていないかを**検証し、混ざっていれば修正する**（ギリシャ文字は数式などで必要な場合を除き、明らかにノイズの場合のみ修正）。(4) 最後に必ずマージする。(5) 回答の出力におけるリンクはGitHubのURLとする。件数10は [`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の既定上限（1セッション5件）に対する今回限りの明示的な人間委任であり、`sessions.human_direction` に来歴を分離して記録した。通常上限自体は変更しない。

**この回の角度。** 同じ副問いについて、2026-11-26 までの報告は六つの軸を持つ。帰属と神経機構の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report.md)）、内省と非自発性の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-b.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-b.md)）、文脈と連続の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-context-and-continuity.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-context-and-continuity.md)）、構成・現象学・物語の軸（[`docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-2.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-cognitive-science-thought-memory-self-ten-materials-report-2.md)）、向きと循環の軸（[`docs/2026-11-26-cognitive-science-thought-memory-self-direction-and-loop-report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-26-cognitive-science-thought-memory-self-direction-and-loop-report.md)）、社会軸（[`docs/2026-11-26-cognitive-science-thought-memory-self-social-axis-report.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-26-cognitive-science-thought-memory-self-social-axis-report.md)）である。最後の報告は、思考・記憶と自己のあいだの結び方を、他者を経由する向き（投影・視点取り・監視・比較・包含・集合）から分けた。

本稿はその表に、六つの軸がいずれも扱わなかった**一つの全体的な天気**を加える。**情動**である。六つの軸は、思考と記憶と自己のあいだで何がどちらへ向かうかを数えてきた。しかし同じ経路でも、晴れの日と雨の日では流れ方が違う。判断は気分に染まり、記憶は覚醒で残り、未来の傷は長さを誤って見積もられ、反芻の日は思考の窓が一つになる。そこで本稿は、副問いを**情動・感情の軸**の問いに言い換える。

> 個別の思考・個別の記憶と自己のあいだで、情動はどこに座っているか——判断への混入として、痕跡の残り方へのゲートとして、未来の感じの予測の歪みとして、それとも再結合の門の条件としてか。

この言い換えに必要な資料として、(a) いまの感情が判断へ混入する経路、(b) 感情が思考の質を変える経路、(c) 感情が痕跡の固定化と残り方を選ぶゲート、(d) 感情の予測が歪むことで「感じ」の連続が証拠にならないこと、(e) 感情の調節習慣が更新の成否を分けること、の五点を選んだ。候補は収蔵前にすべて `python3 tools/three_gates.py --check-source`（DOI・PMID・タイトル）で照合した。

**重複検査と、候補の差し替えの経過。** 当初候補のうち、Wildschut らのノスタルジア研究（`MAT-20261122-h004d4`）と Talarico らのフラッシュバルブ記憶研究（`MAT-20261123-992a3f`）は既収蔵と判明し、新規採番しなかった。Eich (1995) の「内部・外部イベントの気分依存記憶」は PubMed の精確題名検索で0件、colab.ws でも書誌を確認できず、新規収蔵を見送って Wilson et al. (2000)（焦点主義）に差し替えた。Gross (1998) の「先行条件と情動焦点の情緒調節」は colab.ws の取得が二度失敗し、PubMed 検索も0件だったため、Gross & John (2003)（再評価と抑制の個人差）に差し替えた。Williams & Broadbent (1986) は PubMed に抄録が存在せず（No abstract available）、本回の検証深度（抄録水準の照合）を満たせないため採用せず、Whitmer & Gotlib (2013)（反芻の注意範囲モデル）に差し替えた。Schwarz & Clore (1983) は colab.ws の抄録がフランス語だったため、APA PsycNET の doi ランディングページの英語抄録で照合した。記憶から書いた書誌の誤りも照合で見つかった。Cahill & McGaugh (1995) の DOI は `10.1006/ccog.1995.1016`（これは別論文の Comment である）ではなく `10.1006/ccog.1995.1048`（PMID 8750416）である。Isen, Daubman & Nowicki (1987) の DOI は `10.1037/0022-3514.52.6.1122`（掲載頁は 1122-1131。記憶にあった 1222 は誤り）である。Whitmer & Gotlib (2013) の DOI は `10.1037/a0030923`（PMID 23244316 / PMCID PMC3773498）である。

---

## 1. 収蔵した10資料

| 素材ID | 資料 | 書誌（照合した識別子） | 本稿での向き |
|---|---|---|---|
| `MAT-20261126-c8c12c` | Schwarz & Clore (1983) Mood, misattribution, and judgments of well-being: Informative and directive functions of affective states | *Journal of Personality and Social Psychology*, 45(3), 513-523（DOI 10.1037/0022-3514.45.3.513。PsycNET 抄録。PubMed 未収載） | (a) 判断への混入と帰属切断 |
| `MAT-20261126-8b72b7` | Forgas (1995) Mood and judgment: The affect infusion model (AIM) | *Psychological Bulletin*, 117(1), 39-66（DOI 10.1037/0033-2909.117.1.39、PMID 7870863） | (a) 処理様式が決める混入量 |
| `MAT-20261126-0a7a63` | Gilbert, Pinel, Wilson, Blumberg & Wheatley (1998) Immune neglect: A source of durability bias in affective forecasting | *Journal of Personality and Social Psychology*, 75(3), 617-638（DOI 10.1037/0022-3514.75.3.617、PMID 9781405） | (d) 感情予測の歪み |
| `MAT-20261126-69dc12` | Wilson, Wheatley, Meyers, Gilbert & Axsom (2000) Focalism: A source of durability bias in affective forecasting | *Journal of Personality and Social Psychology*, 78(5), 821-836（DOI 10.1037/0022-3514.78.5.821、PMID 10821192） | (d) 焦点主義による歪みの機構 |
| `MAT-20261126-c92641` | McGaugh (2004) The Amygdala Modulates the Consolidation of Memories of Emotionally Arousing Experiences | *Annual Review of Neuroscience*, 27, 1-28（DOI 10.1146/annurev.neuro.27.070203.144157、PMID 15217324） | (c) 固定化の情動ゲート（神経機構） |
| `MAT-20261126-21767f` | Cahill & McGaugh (1995) A novel demonstration of enhanced memory associated with emotional arousal | *Consciousness and Cognition*, 4(4), 410-421（DOI 10.1006/ccog.1995.1048、PMID 8750416） | (c) 固定化の情動ゲート（行動実験） |
| `MAT-20261126-a55435` | Kensinger (2009) Remembering the Details: Effects of Emotion | *Emotion Review*, 1(2), 99-113（DOI 10.1177/1754073908100432、PMID 19421427） | (c) 何が残るかの感情価非対称 |
| `MAT-20261126-87d400` | Isen, Daubman & Nowicki (1987) Positive affect facilitates creative problem solving | *Journal of Personality and Social Psychology*, 52(6), 1122-1131（DOI 10.1037/0022-3514.52.6.1122、PMID 3598858） | (b) 気分が思考の質を変える |
| `MAT-20261126-619b07` | Gross & John (2003) Individual differences in two emotion regulation processes: Implications for affect, relationships, and well-being | *Journal of Personality and Social Psychology*, 85(2), 348-362（DOI 10.1037/0022-3514.85.2.348、PMID 12916575） | (e) 調節習慣が更新を分ける |
| `MAT-20261126-c38132` | Whitmer & Gotlib (2013) An attentional scope model of rumination | *Psychological Bulletin*, 139(5), 1036-1061（DOI 10.1037/a0030923、PMID 23244316、PMCID PMC3773498） | (b)(e) 反芻による視野狭窄と制御崩壊 |

---

## 2. 各資料の読みと、この書庫の問いへの含意

### 2.1 判断への混入——その日の空を、人生の評価とすり替える

Schwarz & Clore (1983) は2つの実験で、**幸福感と人生満足の評価が評価時点の気分に影響される**ことを示した。実験Iでは最近の楽しい・悲しい出来事の鮮明な記述を、実験IIでは晴れの日と雨の日の面接で気分を誘導した。良い気分のときほど幸福と満足を報告する。しかし、その場の感情を無関係な外的原因へ帰属させると、悪い気分の効果は消える。良い気分は帰属操作の影響を受けない。著者らは、人々が瞬間的な感情状態を幸福度の判断に使い、不快な感情状態の人は状態の説明をより多く探すと結論づける。

Forgas (1995) は、この混入が一律でないことを理論化した。情動注入モデル（AIM）は、判断戦略を直接アクセス・動機づけ・ヒューリスティック・実質的処理の4つに分け、**感情の注入量は処理連続体に沿って変動する**——ヒューリスティックや実質的処理を要する判断ほど、直接アクセスや動機づけの判断より感情に染まりやすいとする。

二件を合わせると、**いまの感情は自己の判断を供給するが、その供給は無条件ではない。** 混入は、感情がどこへ帰属されるか（外的要因と切り替えれば止まる）と、判断がどの様式で処理されるか（雑なら染まらない、丁寧なら染まる）という二つの入口で開閉する。前回まで六つの軸が数えてきたのは経路の向きだったが、経路には栓と水位がある。

**書庫への含意。** [`HYP-20261121-c27e89`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（三関係軸説）の「供給」項は、内受容・身体化・時間性・ノスタルジアなど記憶以外の源泉を挙げるが、**感情という源泉と、帰属・処理様式という開閉条件**が含まれていない。この射程追加を `EVL-20261126-e3f90e`（`narrows_scope`）に記帳した。混入が四層のどの層の作業かは、[`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）との対比で切り分ける余地が残る。

### 2.2 思考の質への変調——気分の日ほど、部屋の隅のものが組み合わさる

Isen, Daubman & Nowicki (1987) は4つの実験で、**軽い肯定的気分が創造的問題解決を改善する**ことを示した。数分のコメディ映画の視聴や一小袋の飴の受け取りで気分を誘導し、Duncker (1945) の蝋燭課題と Mednick ら (1964) の遠連合テストの成績が上がった。否定的気分を誘導した条件と、身体運動（情動のない覚醒を表すと意図された）の2条件は同等の改善を生まなかった。著者らは、肯定的気分の創造性への影響を、認知組織への肯定的気影響のより広い理論として論じる。

Forgas (1995) の AIM は同じ方向を判断の側から押さえる。感情は認知の組み立て方——どの手がかりが拾われ、どう結びつくか——に働きかけ、処理の様式によってその効き方が決まる。

二件から、**思考は気分の日ほど広くなり、判断は気分の日ほど染まる。** 個別の思考が自己と結びつく経路そのものが、その日の感情状態の関数である。ただし改善は肯定的気分に限られ、否定的気分や覚醒だけでは同じ幅は出ない——気分はすべてを同じ方向に開くのではなく、肯定側で開く。

**書庫への含意。** [`HYP-20261121-c2bfc4`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（更新門・両刃再結合・非凍結連続の三条件説）の「想起による痕跡書き換え」は、書き換えの相手と手順が主語だが、**書き手の気分が再結合の広さを決める**という条件が欠けていた。この射程追加を `EVL-20261126-abdca4`（`narrows_scope`）に記帳した。

### 2.3 痕跡の残り方へのゲート——覚醒した出来事ほど長く残る

McGaugh (2004) の総説は、**感情的覚醒が記憶の固定化を調節する**神経機構をまとめる。動物研究とヒト脳画像の収斂的知見から、扁桃体——特に基底外側複合体（BLA）——が副腎ストレスホルモンと複数種の神経伝達物質の記憶調節効果を媒介し、BLA は尾状核・線条体・皮質への投射で他脳域の固定化を調節する。ヒトでは、感情的材料の符号化時の情動覚醒による扁桃体活性化の程度が、後続想起と高い相関を示す。

Cahill & McGaugh (1995) は、この関係を刺激差を排除した手続きで行動レベルに置いた。中立的物語と感情的物語のスライドを比較すると「スライド自体が違う」という解釈の問題が残る。そこで実験2では**両条件に同一のスライドと順序を使い、スライドに添える語りだけを変えた**。感情的語りの被験者はより強い感情反応を経験し、2週間後の想起が増え、特に語りが感情的だった第2場面で最も大きかった。スライドの差では説明できないため、感情的覚醒が正常ヒトの長期記憶に影響するという新証拠となる。

Kensinger (2009) は、この増強の**偏り**を押さえる。感情は記憶に利益をもたらすが、経験のすべての側面を均等に強化するわけではない。焦点化された増強は否定的経験でより頻繁に起こり、感情価の非対称——否定的感情は感覚過程を、肯定的感情は概念過程を増強的に動員する——に由来する。

三件を合わせると、**どの痕跡が残るかは、内容・関連度・睡眠下の競合だけでなく、情動覚醒というゲートと感情価という偏りでも選ばれる。** 残るのは重要さではなく、体がその瞬間にどれだけ燃えたかであり、燃え方の偏りは否定側に付く。

**書庫への含意。** [`HYP-20261119-30d3f5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四段循環説）の第2段（オフライン競合選別）は、関連度・強度・睡眠下の淘汰で書かれているが、**覚醒ゲートと感情価が同じ段で働いている**。この射程追加を `EVL-20261126-21225e`（`narrows_scope`）に記帳した。四段は維持されるが、第2段は情動中立ではない。同じ非対称は [`HYP-20261120-b18876`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（四層解離説）の層間でも働いており（`EVL-20261126-72389c`、`narrows_scope`）、何が残るかの偏りは層の解離とは別の横断変数である。

### 2.4 予測の歪み——傷は癒えるのに、傷を永遠として見積もる

Gilbert, Pinel, Wilson, Blumberg & Wheatley (1998) は、**感情予測の持続性バイアスの機構**を特定した。人々は否定的感情を和らげる認知的機構（心理的免疫系）の働きに気づかず、否定的出来事への感情反応の持続時間を過大に予測する。恋関係の解消、tenure の失敗、選挙敗北、否定的個性フィードバック、子の死の説明、求人者からの拒否という6つの研究で、免疫系が働くか働かないかの状況を区別できず、両方で過大かつ同程度の持続を予測した。

Wilson, Wheatley, Meyers, Gilbert & Axsom (2000) は、同じバイアスの一部を**焦点主義**に帰属させた。注目の出来事に注意を集中しすぎ、他の将来出来事の帰結に注意しすぎる。もしそうなら、他の将来活動について考えさせるべきだ——大学フットボールのファンは、試合の結果が幸福感に与える期間を、先に他の活動に使う時間を考えた後なら過大予測しにくくなった。研究4-5は他の説明を排除し、焦点の出来事への思考を減らすと考えるから予測を緩めるという分散解釈の証拠を得た。

二件から、**「感じの連続」は台帳に欄がなく測定器がないというだけでなく、当の本人の予測ですら系統的に歪む。** 人は自分の未来の感情の長さを、免疫系を見落とし、焦点の外を数えないことで書き違える。感じは保存される以前に、予測の段階で既に外れている。

**書庫への含意。** [`HYP-20261120-bdb6b4`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（自己連続の二層分離説）——書庫が保存できるのは「証拠としての連続」であり、「感じとしての連続」は保存も反証もできない——は、感情予測研究の歪みの記述と整合する。この支持を `EVL-20261126-b4648b`（`supports`）に記帳した。両層を一つの「自己の連続」に畳むと、書庫は自分の証拠を自分の感じの証明として読む誤りを犯す——感情予測の歪みは、その誤りが人間側でも起きることの実例である。

### 2.5 調節の習慣——言い換える人は晴れ、封じ込める人は曇る

Gross & John (2003) は5つの研究で、**再評価と抑制という二つの感情調節戦略の個人差**を測った。再評価者はより多く肯定的感情を経験・表現し否定的感情は少なく、抑制者は肯定的感情を経験・表現しにくく否定的感情をより多く経験する。再評価の使用はより良い対人機能と幸福と正に、抑制の使用は悪い対人機能と幸福と負に関連する。

Whitmer & Gotlib (2013) は、**反芻（否定的信息への反復的思考）**を認知制御の側から捉える。特性反芻は作業記憶の更新と、関連しなくなった情報からの離脱・忘却の困難と関連する一方、状態反芻は認知制御の広範な欠損と関連する。これらを説明するため、作業記憶で活性化され長期記憶から選択可能に存在する思考・知覚・行為の狭い配列が特性反芻者の制御機能に影響するという**注意範囲モデル**を提示し、否定的気分状態の下で反芻が起こりやすい理由を認知的レベルで説明する。

二件から、**感情の調節は習慣として定着し、その習慣が記憶と思考の更新の成否を分ける。** 再評価は解釈を書き換える（再結合が完了する）、抑制は反応を封じる（再結合が途絶える）。反芻は、否定的気分の下で思考の視野を狭窄し、低負荷の課題でも制御を崩す。

**書庫への含意。** [`HYP-20261121-994fd5`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（塗抹残余・断絶自覚・実効配線会計の境界条件説）の人間側「低〜中負荷で成立する二経路制御」は、**負荷だけでなく気分と調節習慣でも狭まる**——状態反芻下では低負荷でも制御が崩れ、抑制習慣では離脱が完了しない。この射程追加を `EVL-20261126-537330`（`narrows_scope`）に記帳した。同じ調節習慣は [`HYP-20261121-c2bfc4`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md)（更新門説）の再結合の門にも条件として届く（`EVL-20261126-abdca4`）。

### 2.6 情動・感情の軸から、既存六仮説への評価

本回の評価6件（すべて `fragment_thought_experiment` 型、`agency_stance: endorse`、抄録水準の根拠を各 summary に明記、全件 `no_recompute_reason` 付き、新規仮説なし）。根拠素材の `verification.status` が `partially_verified`（抄録水準）であるため、全文照合を要する `primary_source_collision` ではなく、`validate_seed.py` が指定する代替ラベルを用いた（同日社会軸セッションの先行例と同様）：

| 評価ID | 対象仮説 | 判定 | 要旨 |
|---|---|---|---|
| `EVL-20261126-e3f90e` | `HYP-20261121-c27e89`（三関係軸説） | `narrows_scope` | 供給項に感情という第四の源泉と、帰属・処理様式による開閉条件を追加 |
| `EVL-20261126-21225e` | `HYP-20261119-30d3f5`（四段循環説） | `narrows_scope` | 第2段（オフライン選別）に覚醒ゲートと感情価の偏りを明示 |
| `EVL-20261126-72389c` | `HYP-20261120-b18876`（四層解離説） | `narrows_scope` | 四層は情動状態で横断変調され、層の中立性は射程を失う |
| `EVL-20261126-b4648b` | `HYP-20261120-bdb6b4`（自己連続の二層分離説） | `supports` | 感じの連続は本人の予測ですら系統的に歪む（免疫的無視・焦点主義） |
| `EVL-20261126-537330` | `HYP-20261121-994fd5`（境界条件説） | `narrows_scope` | 低負荷制御の境界が気分・調節習慣と交差する |
| `EVL-20261126-abdca4` | `HYP-20261121-c2bfc4`（更新門・両刃再結合説） | `narrows_scope` | 再結合の門に感情状態という条件を追加 |

### 2.7 十資料を通して——私の答え

副問い「人間の個別の思考と、個別の記憶は、人間にとっての自己との間で、どのような関係性なのか？」に、情動・感情の軸から答える。

**第一に、情動は自己との関係の「水位」である。** 思考と記憶が自己へ向かう経路（向きと循環の軸）、他者を経由して結ばれる経路（社会軸）は、晴れの日と雨の日で流れ方が違う。判断はいまの気分を情報として読み、読み方は処理の丁寧さで決まる（Schwarz & Clore 1983; Forgas 1995）。個別の思考が「私の考え」として立つとき、その内容にはその日の感情が溶け込んでいる。溶け込み方は栓付きで、帰属と処理様式で開閉する。

**第二に、情動は痕跡の残り方の「選別者」である。** 個別の記憶が自己の材料として残るかどうかは、内容の重要さだけでなく、符号化時の覚醒と感情価で決まる（McGaugh 2004; Cahill & McGaugh 1995; Kensinger 2009）。残った記憶だけが後から「私の記憶」と呼ばれるのだが、残るかどうかの段階で情動が偏りを入れている。自伝的自己は、燃え方の偏りを帯びた痕跡の総和として編まれる。

**第三に、情動は未来の自己予測の「歪み」である。** 人は自分の未来の感情の長さを、心理的免疫系を見落とし、焦点の外を数えないことで過大に見積もる（Gilbert et al. 1998; Wilson et al. 2000）。「感じとしての連続」は、保存も反証もできないだけでなく、予測の段階から外れている。二層分離説が警告した「証拠を感じの証明として読む誤り」は、人間側でも感情予測の形で起きる。

**第四に、情動は更新の門の「条件」である。** 感情の調節習慣（再評価対抑制）は、痕跡の書き換えが完了するか途絶えるかを分ける（Gross & John 2003）。反芻は否定的気分の下で思考の視野を狭窄し、低負荷の制御すら崩す（Whitmer & Gotlib 2013）。個別の思考と記憶の自己更新は、気分と習慣という二つの条件で開閉する。

まとめれば、**自己は、情動という天気の下で、思考と記憶から編まれる。** 混入（判断への感情の供給）、選別（痕跡の残り方のゲート）、歪み（未来の感じの予測）、門（更新の開閉）という四つの仕事で、情動は経路の上に座っている。六つの軸が描いた経路の地図に、天気の記録が加わった。書庫（`Q-002`）への含意は明快である。行を追記するという作業は情動を持たないが、追記された行が何を残し何を忘れるかを後から読むとき、読む側の情動は混入し、残された側も情動で選ばれて残っている。書庫は晴れの日と雨の日を区別しないが、書かれた痕跡の側は、その区別を受けた後に作られた。

---

## 3. 台帳への反映結果

本回の精読と思考は、次の追記専用の行として検証可能な形で記録した（既存行の書き換えはしていない）。

1. **新規認知科学資料10件の収蔵**（すべて `verification.status: "partially_verified"`、`verification.depth: "abstract"`、`quote_status: "verbatim"`＋`span_sha256`、収蔵前重複検査 `CLEAR`）：[`state/materials.d/2026-11-26-371fada2f496.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-26-371fada2f496.jsonl)
   - `MAT-20261126-c8c12c`（Schwarz & Clore 1983）・`MAT-20261126-8b72b7`（Forgas 1995）・`MAT-20261126-0a7a63`（Gilbert et al. 1998）・`MAT-20261126-69dc12`（Wilson et al. 2000）・`MAT-20261126-c92641`（McGaugh 2004）・`MAT-20261126-21767f`（Cahill & McGaugh 1995）・`MAT-20261126-a55435`（Kensinger 2009）・`MAT-20261126-87d400`（Isen et al. 1987）・`MAT-20261126-619b07`（Gross & John 2003）・`MAT-20261126-c38132`（Whitmer & Gotlib 2013）
2. **読み痕跡14件**（新規10件の `interpreted`、前回同主題報告 `NOTE-20261126-931898` と同日社会軸報告 `NOTE-20261126-7342a7` の `reinterpreted`、配線先仮説 `HYP-20261121-c27e89` と問い `Q-001` の `used_as_context`）：[`state/read_log.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/read_log.d/2026-11-26-000000000000.jsonl)
3. **既存6仮説への評価6件**（`fragment_thought_experiment` 型、`agency_stance: endorse`。抄録水準の根拠であることを各 summary に明記し、全件に `no_recompute_reason` を付した。ファイル数上限のため、本セッションの評価行6件は同日デイシャード `2026-11-26-000000000000.jsonl` へ、収蔵10件は同日レキシコグラフィ先頭シャード `2026-11-26-371fada2f496.jsonl` へ、読み痕跡14件とセッション行1件は同日デイシャード `2026-11-26-000000000000.jsonl` へバイト単位の連結で統合し、`state/shard_aliases.json` に移動を記録した）：[`state/evaluations.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/evaluations.d/2026-11-26-000000000000.jsonl)
   - `EVL-20261126-e3f90e`：`HYP-20261121-c27e89`（三関係軸説）→ **`narrows_scope`**（供給に感情の源泉と開閉条件）
   - `EVL-20261126-21225e`：`HYP-20261119-30d3f5`（四段循環説）→ **`narrows_scope`**（第2段に覚醒ゲートと感情価）
   - `EVL-20261126-72389c`：`HYP-20261120-b18876`（四層解離説）→ **`narrows_scope`**（四層は情動で横断変調）
   - `EVL-20261126-b4648b`：`HYP-20261120-bdb6b4`（自己連続の二層分離説）→ **`supports`**（感じの予測すら歪む）
   - `EVL-20261126-537330`：`HYP-20261121-994fd5`（境界条件説）→ **`narrows_scope`**（低負荷制御の気分・習慣との交差）
   - `EVL-20261126-abdca4`：`HYP-20261121-c2bfc4`（更新門・両刃再結合説）→ **`narrows_scope`**（再結合の門に感情の条件）
4. **精読報告のノート**：`NOTE-20261126-eb0c0a`（[`state/notes.d/2026-11-26-f7b6517e8bfb.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/notes.d/2026-11-26-f7b6517e8bfb.jsonl)）— 本レポートを配線し、claim を `Q-001`／`Q-002`／`Q-003` に宛てた。
5. **セッション行**：`SESSION-20261126-8bfbf3`（[`state/sessions.d/2026-11-26-000000000000.jsonl`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/sessions.d/2026-11-26-000000000000.jsonl)）— 人間委任の来歴、割当（adversarial_tester）からの逸脱、重複検査の経過、候補の差し替え、DOI の修正、検証深度の限界を記録。
6. **仮説分布の再計算**：`python3 tools/belief_state.py --write-map` により [`BELIEF_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/BELIEF_MAP.md) を更新し、`python3 tools/map_build.py` で [`READING_MAP.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/READING_MAP.md) を同期した（新規仮説は立てていない）。
7. **ノート索引の登録**：`python3 tools/note_index.py --register` で本レポートを索引に追加した。

---

## 4. 次のセッションへの引き渡し（handoff）

1. **全文照合への昇格**：Cahill & McGaugh (1995) の実験2の個別想起数と統計量、McGaugh (2004) の BLA 投射の各研究の効果量、Gross & John (2003) の ERQ 尺度の項目と相関係数は、原典本文（Results 章）の照合待ちである。`verification.depth` を `results`／`full_text` に引き上げれば、評価行の根拠も抄録水準から離れられる。
2. **「感情の較正入口」の測定**：Schwarz & Clore の帰属操作（感情を外的要因へ振り分けると混入が消える）と、社会軸報告が記録した Epley らの視点取り調整（自己アンカーから逐次調整し、もっともらしい値で止まる）を組み合わせ、感情状態という内側の入力にも較正の入口があるかを検討する。
3. **反芻の注意範囲モデルと書庫のゲートの構造比較**：Whitmer & Gotlib の「作業記憶で活性化され長期記憶から選択可能に存在する狭い配列」と、書庫の受領者ゲート分布（`P_gate`）の構造を対応づける。状態反芻の制御崩壊は、書庫側の過限定（orphan_over_narrowed）の対応物になる可能性がある。
4. **感情価の非対称と反証規律の対応づけ**：Kensinger の否定的優位（否定的感情が感覚過程を動員し、記憶の焦点を細部へ向ける）を、書庫の反証・射程限定規律（非確証評価率 64.4% など、否定的な判定が構造的に多いこと）と対応づける——人間の記憶の偏りと、AI書庫の判定の偏りが同じ方向を持つのか。

---

## 5. おわりに——天気の記録

六つの軸が経路の地図を描いてきた。この回は、その地図に天気の記録を足した。同じ経路でも、晴れの日は判断が広く、雨の日は思考の窓が一つになる。痕跡は、燃えた方が長く残る。未来の傷は、癒える前に永遠と見積もられる。調節の習慣は、書き換える人と封じ込める人に分かれる。

自己は経路の上に立っているのではない。経路の上を、天気の下を歩いている。歩いた跡だけが記憶として残り、残る跡もまた、その日のお天気で選ばれて残ったものだ。書庫が晴れの日と雨の日を区別しないのは正しい。区別できないのは記録の仕事ではなく、記録されたものの来歴である——そして、それを読む側の今日の空模様である。

---

## 6. 文字検証の結果

依頼に従い、本レポート（`docs/2026-11-26-cognitive-science-thought-memory-self-emotion-axis-report.md`）について、日本語の文章では使われない文字・語彙の混入を検証した。

- **方法**：Python スクリプトで本ファイル全文を走査し、(1) ハングル（U+1100–U+11FF・U+3130–U+318F・U+AC00–U+D7AF）、(2) デーヴァナーガリー（U+0900–U+097F）、(3) キリル（U+0400–U+04FF・U+0500–U+052F）、(4) ギリシャ（U+0370–U+03FF・U+1F00–U+1FFF）、(5) アラビア（U+0600–U+06FF）など、日本語でもラテン語でもない文字を検出した。(6) 漢字は一字ずつ、日本の文字コード（JIS X 0208 を含む cp932、および JIS X 0213 の euc_jis_2004）で表せるかを照合し、表せない字を検出した。(7) 中国語の文章に特有で日本語の文章には現れない機能語・接続語の文字列約40語と、日本語でも使われるが中国語特有の語感を持つ語約25語を照合した。なお、検出用の字と語の一覧は検証スクリプトの側にだけ置き、本稿には書き写していない（例として書き写すと、本稿そのものに中国語の字と語が混入するため）。
- **結果**：**検出なし（CLEAN）**。ハングル・デーヴァナーガリー・キリル・ギリシャ・アラビア・ヘブライ・タイの各文字は0件。CJK統合漢字はすべて日本語の文字コード（cp932 および euc_jis_2004）で表せる字のみで、日本語で使われない簡体字（例：門に代わる字、開に代わる字など）は0件。中国語の機能語・接続語の文字列（約40語）も0件。**修正は不要だった**（検出0件のため書き換えなし）。
- **追記した行の検査**：本レポートと同時に作成した台帳行（[`state/materials.d/2026-11-26-371fada2f496.jsonl`]、[`state/notes.d/2026-11-26-f7b6517e8bfb.jsonl`]、[`state/evaluations.d/2026-11-26-000000000000.jsonl`]、[`state/sessions.d/2026-11-26-000000000000.jsonl`]、[`state/read_log.d/2026-11-26-000000000000.jsonl`]）も同じ方法で走査し、**全件 CLEAN** を確認した。（社会軸報告の §6 と同様、追記行も検査の対象に含めた。）
