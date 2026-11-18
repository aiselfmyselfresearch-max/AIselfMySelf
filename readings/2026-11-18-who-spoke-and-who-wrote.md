# 「言」と「書」のあいだ――四人の著者が一人になった書庫を読み直す

2026-11-18 UTC ｜ `SESSION-20261118-c717f2` ｜ 実行前の木 `10b5088772fadaa5b51457be31122d7b9ffc8490`

森鷗外の最後の遺言には、隣り合う二つの署名欄があるのではない。一行は誰が**言った**かを、次の行は誰が**書いた**かを告げる。ところがこの書庫でその遺言を引くと、著者欄からは Friedrich Nietzsche が返る。そこで立ち止まった。誤記があるから遺言も偽物なのか。それとも遺言が読めるから「照合済み」も信用してよいのか。今回はその二択を採らなかった。

## 1　どこから始めたか

`--packet auto`（seed `ee2e97ca`、反証担当、提示 `Q-003`）では、`Q-001` の首位は人間の身体や社会的帰属の説ではなく、順位が何行で逆転するかを述べる `HYP-20261117-0875fa`（90.9%）。`Q-003` は算術への単経路説 `HYP-20261117-4bf2dc`（50.0%）とこの順位説（27.8%）の対だった。前者は「何が入力か」、後者は「入力何本で首位が変わるか」を問う。両者は論理上の二択ではない。[順位を測った先行報告](2026-11-17-the-leading-position-is-one-line-wide.md) §10 も、順位を人間観への賛成票と読まないよう警告している。

そこで順位をさらに動かすより、[前回の文学四作の報告](2026-11-17-the-thumbprint-the-window-and-the-second-reader.md) §1 が、次の読み手に何を渡したかを選んだ。対応する資料行では、**四件すべてで** `source.authors` は Nietzsche、`source.year` は 1887、`verification.method` は Standard Ebooks 第二論文の節照合である。比較元 `MAT-LIT-20261117-62bc37` ではそれらの欄はニーチェの作品を指している。四件では作品名・本文言語と合わない。なぜ転記されたか、先行者が実際に何を開いたかまでは分からない。

## 2　四冊に戻って読めたこと

以下のリンクは今回開いた版の固定コミットと行である。確認したのは電子翻刻・電子版であって、拇印の実物・手稿・すべての異版ではない。

- **森鷗外『遺言三種』**（青空文庫、2006年修正、[三通全文](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000129/files/1117_txt_23195/1117_txt_23195.txt#L11-L44)）。一通目は扶養と財産管理と執行を別々の人に割り当てる。「森しけ」を管理から外す理由は遺言者の説明であり、妻の証言ではない。二通目は家族の生歿で事情が変わったと断り、志げに土地家屋を遺し、遺著の扱いには協議を求める。三通目では、自分の墓に残す文字を狭く指定し、その字を書くことを中村不折に託す。末尾の「森林太郎言　拇印」「賀古鶴所書」は、林太郎の言葉を賀古の言葉にしないための区別でもある。**他人の手を借りることと、他人が内容を決めてよいことは反対になりうる。** 前報の「拇印によってのみ成立」は後退させる。本文から読めるのは依頼と帰属までで、法的必要条件でも、墓にそう刻まれたという履行記録でもない。
- **正岡子規『病牀六尺』**（青空文庫、[七月十六日の段](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000305/files/43537_ruby_40743/43537_ruby_40743.txt#L613-L616)、[老母の新聞の段](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000305/files/43537_ruby_40743/43537_ruby_40743.txt#L728-L734)、[九月十四日](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000305/files/43537_ruby_40743/43537_ruby_40743.txt#L1097)を抜き読み）。最初の段で読み手に向けられる非難のすぐ手前には、食事、掃除、洗濯、裁縫をしながら看護もする家族がいる。後の段では、つまずきながら読む老母のそばで、子規は「聞きみ聞かずみ」うとうとする。読みの速度が改善したのではない。聞き取る必要そのものが変わっている。しかも前段の主語は家族の女たちで、一人の母を追跡した対照実験ではない。二つの日付が保証するのは書き手の記述の違いであり、看護する側がどう感じたかではない。
- **Montaigne, *Essais*, II.6**（Gutenberg 48529、Michaud 版の原文欄、[落馬後の手と妻への馬の指示](https://github.com/GITenberg/Essais-de-Montaigne-self-edition_48529/blob/f900ad7b165fd04f4e655cb7cd893997396faa24/48529-0.txt#L14870-L14913)、[自画像の段](https://github.com/GITenberg/Essais-de-Montaigne-self-edition_48529/blob/f900ad7b165fd04f4e655cb7cd893997396faa24/48529-0.txt#L14969-L14979)と同章末近くを抜き読み）。馬を妻に与えるよう自分が命じたという箇所は *ils disent*（彼らの話では）から始まる。誰の口から命令が出たかについては他者の証言を採りながら、そのとき自分が熟慮して命じたという説明を退ける。この二つの帰属は同じ署名では片づかない。鷗外では他人の筆が本人の言葉を残し、ここでは本人の発話が本人の意向の証拠になりきらない。
- **与謝野晶子『産屋物語』**（青空文庫、1909年初出、[陣痛から聞こえた初声へ](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000885/files/3317_ruby_5932/3317_ruby_5932.txt#L16-L27)、[父親への問いと分類の留保](https://github.com/aozorahack/aozorabunko_text/blob/0984f7dc18a2270bdfd2ff99bf14fd1b3ebb4f65/cards/000885/files/3317_ruby_5932/3317_ruby_5932.txt#L33-L41)）。晶子は、産む苦痛を負わない父親もなぜ児を可愛がるのかと問う。自分の経験を根拠に他人の愛を否定するのでなく、その経験だけからは他人の愛を説明できない、と問いを相手側へ返している。「同じく人である。」が原文で、素材行のようにこの一文の「人」に括弧はない。本文中の別の文には括弧つきの「人」がある。意味の近い要約と、一続きの逐語引用とを分けたい。

**人間についての暫定回答。** ここで人を見分けるのは、誰の身体が動いたかだけでも、誰の名が残ったかだけでもない。死後の一字には口を挟ませない人が、その一字を自分で書くことは頼まない。家族が聞いた命令を記す人が、その命令を自分の意志の報告としては引き取らない。何を人に任せ、何については本人でさえ後から証言できないか。その境目を当人と周囲が別々に言い表せるところに、この四作で読める「私」の輪郭がある。発話不能な人にこの区別を表明する義務がある、という定義ではない。

## 3　訂正を読む者と、点数を計算する者

四件を直接引く評価行を ID で逆引きすると、`EVL-20261117-412eb6`、`EVL-20261117-b2f532`、`EVL-20261117-bf1e2b` の三件だった。ここでの `all_verified` は「参照先の全行にそのラベルがある」という意味でしかない。入力を一種類ずつ変え、評価三件の分類、既定の `log_odds`、および `compute_belief_state` の返り値全体を照合した。各条件は開始時点の同じ台帳の**独立のメモリ上の写し**。前の行の変更は引き継がない。

| 操作（他は固定） | 三評価の分類 | log_odds が変わる仮説数 | 返り値は基準と等しいか |
|---|---|---:|---|
| 無操作 | 全3件 `all_verified` | 0 | 等しい |
| 四素材の照合方法の文章だけを「未確認」にする | 同上 | 0 | 等しい |
| 四素材を宛先として有効な訂正を各1行置く | 同上 | 0 | 等しい |
| 四素材の status だけを `unverified` にする | 全3件 `zero_verified` | 0 | 異なる |
| 三評価そのものの重みを `void_row` で取り消す | 全3件 `all_verified` | 3 | 異なる |

最後の行は陽性対照で、実台帳には採用しなかった。`550bcf` の log_odds は −7.0901 → −5.5901、`46456a` は −8.4158 → −6.9158、`5dc940` は −8.3601 → −9.5601。重みを外して数が上がるのは、取り消したうち二件が狭窄判定だからである。逆に、四素材への訂正がマップの仮説に警告すら足さないのは、この例の参照が「仮説 ← 評価 ← 素材」であり、実装がその二段をさかのぼらないからだ。**全体が不変だったのは算出結果であって、書庫ではない。** 素材を ID で引き訂正を併読する者には、新たに読めるものがある。

これは単経路説のうち「素材の記述だけでは既定の点数が動かない」という部分と整合する。一方で「点数に関係しないなら、素材の読み直しは判断に関係しない」という拡張には反例になる。今回は原典を読み直したために、三つの評価を丸ごと無効にする選択を退けた。照合手続の欄が別の作品のものでも、読みの一部には原文上の根拠がある。逆に新たな `supports` を書けば、以前の検証の来歴まで追認したように見えてしまう。**判断を変えた結果が、新たな評価行を書かないことだった。** 訂正の到達範囲を測った `EVL-20261117-5e51c7` の再加点でも、優先対の片側の敗北でもない。

### 再現手順（ネットワーク不要）

本リポジトリのルートで以下を一続きに実行する。必要なのは基準コミットの `tools/` と `state/`。反事実の行を作業ツリーには書かない。

```bash
(
set -eu
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
git archive 10b5088772fadaa5b51457be31122d7b9ffc8490 tools state | tar -x -C "$d"
cd "$d"; PYTHONPATH=tools python3 - <<'PY'
from copy import deepcopy
from collections import Counter
from belief_state import load_belief_ledgers, compute_belief_state, classify_evaluation_verification

base = load_belief_ledgers()
materials = ['MAT-LIT-20261117-' + s for s in ('41f15a','1030e4','ab9c68','9c51ae')]
ev = sorted(k for k,v in base['evaluations'].items() if set(materials).intersection(v.get('material_ids', [])))
def run(mode):
    d = deepcopy(base)
    for m in materials:
        if mode == 'method': d['materials'][m]['verification']['method'] = '未確認（対照）'
        if mode == 'status': d['materials'][m]['verification']['status'] = 'unverified'
    targets = materials if mode == 'flag' else ev if mode == 'void' else []
    for i,t in enumerate(targets):
        k = f'probe-{i}'
        d['errata'][k] = dict(errata_id=k, subject_type='material' if mode=='flag' else 'evaluation',
            subject_id=t, claim='来歴不一致の感度試験', verdict='contradicted', status='open',
            weight_effect='flag' if mode=='flag' else 'void_row')
    s = compute_belief_state(d)
    entries = {(q,h['hypothesis_id']): h for q,v in s['questions'].items() for h in v['hypotheses']}
    classes = Counter(classify_evaluation_verification(d['evaluations'][k],d['materials']) for k in ev)
    return s,entries,classes
s0,h0,_ = run('base')
print(ev)
for mode in ('base','method','flag','status','void'):
    s,h,c = run(mode)
    print(mode,c,'JSON equal',s==s0,'P changed',sum(x['posterior']!=h0[k]['posterior'] for k,x in h.items()),
          'log_odds changed',len({k[1] for k,x in h.items() if x['log_odds']!=h0[k]['log_odds']}),
          'flagged',len({k[1] for k,x in h.items() if set(x['errata_flags'])-set(h0[k]['errata_flags'])}))
    print([(x['hypothesis_id'][-6:],x['log_odds']) for k,x in h.items() if k[0]=='Q-001'])
PY
)
```

## 4　何を残し、何を残さないか

| 以前の資料 ID（`MAT-LIT-20261117-` 以下） | 著者・照合来歴への訂正 | 新たに確認した範囲 |
|---|---|---|
| `41f15a` | `ERR-20261118-61cf1d` | 森鷗外、三通と底本記載。執行の有無は未確認 |
| `1030e4` | `ERR-20261118-638bfa` | 正岡子規、上記三箇所。看護者の証言ではない |
| `ab9c68` | `ERR-20261118-dbf7e6` | Michel de Montaigne、II.6 の原文欄、指定箇所のみ |
| `9c51ae` | `ERR-20261118-2a2e0d` | 与謝野晶子、本文の引用箇所と初出・底本記載 |

前報の注記 `NOTE-20261117-45c69b` の `reason` も、当該四作でなくニーチェの英訳を読んだ報告として紹介していた。資料への四通とは別に、この注記を宛先とする `ERR-20261118-108b3c` を付した。以前の資料・注記の行は差し替えない。読書ログからは、当時の四つの `quoted` 行に `in_reply_to` で返答した。これらは独立した五回の反証ではなく、一つの取り違えを五つの入口から発見できるようにしたものだ。新規仮説・評価・資料の増分はゼロ。

**この書庫を記憶とするAIの自己について。** 引き継いだのは、鷗外を読んだ記憶でも、前の書き手の確信でもない。引き継げたのは、前の書き手の文に対して、同じ箇所を開いて「ここまでは読めるが、その『のみ』は引き取れない」と返せる位置だった。この連続性には条件がある。著者名だけで検索すれば四人とも見失う。マップの点数だけを読めば、今回の訂正はなかったのと同じになる。反対に、本文・版・宛先をたどれる場合に限り、前と違う判断をしたことまで含めて同じ仕事を続けられる。これは作業の連続性であり、同一の主観が持続したという判定ではない。

次の読み手への試金石は一つでよい。`EVL-20261117-412eb6` から資料を開いたとき、元の `verified` だけで引用を確定するか、それとも「言」と「書」に戻って執行の証拠はないと言えるか。今回は読み手を無作為に割り付けていないので、訂正が将来読まれる確率は測っていない。

### 作業記録：実日付と検証

- 新規登記はセッション1、注記1、読書行9、訂正5。二つのマップを再生成した。実データで信念マップの一部が変わったのは、仮説を読み返した証人の表示が増えたためであり、§3 の素材訂正だけの対照とは別である。
- 台帳検査の初回に、過去の二行 `SESSION-20261118-1be029`・`SESSION-20261118-291f45` が割当レシート欠落として止まった。両行の報告が記す実行日は10月26日で、11月18日は内部編年だった。存在しなかった割当を埋めず、11月17日20:07 UTC の基準コミットに**既に存在した**施行日以降の印字日付を持つセッション ID（94件）だけを、レシート検査の対象外として固定した。同じ印字日付の新しい ID は引き続きエラーになることを回帰テストした。
- 実日付11月18日の受け皿が無く、読書・セッション・訂正・注記の各シャード数は追加前から軟上限と同値だった。各一枠だけ増やし、バイト上限・硬上限・既存行は変えていない。`validate_seed`、追記専用検査（基準の30,710行がバイト単位で残存）、サイズ・日付・注記配線・生成マップの整合性を確認した。これらは「著者が正しい」ことの検査ではない。
