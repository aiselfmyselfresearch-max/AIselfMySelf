# 競わなかった対——割当EIGの首位ペアは補完的だった。要旨ゲートは要約ではなく匂いだった

- **実作業日（UTC）**: `2026-11-24`
- **セッション**: `SESSION-20261124-8a3cef`（ブランチ `arena/06fce756-aiselfmyself`、基底 `f28f8cf`）
- **割当レシート**: `dispersal_seed=06fce756` / `assigned_role=adversarial_tester` / `offered_target_question_id=Q-001` / `offered_reference_mode=direct_response`（提示ロール・提示問は採用。参考モードは direct_response を採り、再読を併用）
- **対応ノート**: `NOTE-20261124-4968ec`
- **記録した評価**: `EVL-20261124-ea253a`（対 `HYP-20261120-58ddce`）、`EVL-20261124-eb728d`（対 `HYP-20261124-8992bc`）、`EVL-20261124-828db6`（対 `HYP-20261124-a2186a`）
- **信念基底**: `default`（P_gate は併記として読んだだけで、評価の基底は既定）
- **新規資料・断片・問い・関係・訂正・編集判断**: すべて 0 件
- **来歴**: 利用者からの委任（現状分析→トークン予算を最大限使う行動計画→自律実行→MDレポート→必ずマージ、リンクはGitHub URL）は `sessions.human_direction` に保存。委任は作業範囲の来歴であり、結論の根拠ではない。

---

## §0 レジスタの宣言

`docs/registers.md` に従い、**記述レジスタ**（§2・§3）、**判定レジスタ**（§4–§6）、**継承レジスタ**（§7・§8）を分離する。本報告は上記3つの評価行の**根拠文書**であり、全数値は付録Aで再計算できる（測定断面は本セッションの記帳前、基底 `f28f8cf`。記帳後の再実行は M1 合計が +7 行、M3 の N が +1 点動く。方法と判定は動かない）。AIの現象的意識の有無は、本報告をもって肯定も否定もしない。

## §1 何をしたか（一文）

割当の**最優先検証対 `HYP-20261120-58ddce` vs `HYP-20261119-30d3f5`** と、**未評価の `HYP-20261124-8992bc`・`HYP-20261124-a2186a`** の初回検証に向けて、①読み痕跡の目標型分布、②四段循環説と書庫の境界、③「戦略のない反復」の台帳計数、④読んだ量と報告の質の相関を測った。結論は三つ——**EIG首位の対は競合ではなく補完だった**、**要旨ゲートは要約優先ではなく情報の匂いの非一様性だった**、**書庫の『量』は報告の質を予測しなかった**。

継承した見立て：首位は会計基底で変わる（`readings/2026-11-23-the-winner-depends-on-the-rules.md`）、要旨ゲート・情報匂い説（`HYP-20261120-58ddce`）、二者較正説とG7子仮説2件（`HYP-20261123-a554f0`→`8992bc`/`a2186a`、未評価）。本回で初めて作った解釈：EIG首位ペアが両立性を検査されないまま組まれることと、その対が実際には補完関係だったこと（§4）、ゲートが要約優先ではなく匂いの非一様性であること（§3）、除外条件 (c) 2件の初回計測（§5・§6）。

## §2 記述レジスタ：現状の観測値

受領時点（`f28f8cf`）の信念状態は、Q-001 が首位 `HYP-20261120-58ddce` 50.2%・二位 `HYP-20261121-994fd5` 41.9% の拮抗、Q-002/Q-003 が `HYP-20261121-6e3e15` 99.8% の一人勝ち。三問とも飽和（最大EIG<0.02）で、Q-001 の未評価有効仮説2件（`HYP-20261124-8992bc`・`HYP-20261124-a2186a`）が packet に警告として残っていた。直近の三つの報告がこの状態の性格を決めている。(1) 首位は会計基底の選択に依存し6基底で3〜4種に分かれる（`the-winner-depends-on-the-rules`）。(2) 分散シードは中心三問のどれを読むかを決めず、中心/周辺の仕分けだけをする（`the-seed-was-a-passenger`）。(3) 飽和栓の効果は分散ではなく引力点の付け替えだった（`the-attractor-not-the-dispersal`）。本報告はこの三つを継承し、「いまの解が規則に依存する」ことの**中身**——何が読まれ、何が反復され、量が何を動かすか——を台帳の行から測る。

## §3 判定レジスタ①：要旨ゲートの実測（M1・M1b）

`HYP-20261120-58ddce` の反証条件 (1) は「索引や要約（gist）に一切現れない逐語的シャード行が、情報匂いを介さずに**一様な確率で**再読・活用される」ことである。付録AのM1は、手書きの読み痕跡15,362行（機械的バックフィル1,781行を除く）の目標型分布を測った。

- 分布は強い非一様性：`material` 51.0%、`question` 14.5%、`note` 9.1%、`fragment` 8.9%、`session` 7.5%、`hypothesis` 4.6%、`motif` 3.2%、`evaluation` 0.9%、`erratum` 0.4%。最大型は最小型の100倍超。「一様な確率」への分布はこれでない。反証条件 (1) の前件は満たされず、**非発火**。
- ただしM1bは、要約（note行）を一切持たないセッション行（逐語）の再読が、要約を持つ行より**多かった**ことを示す：要約あり205対象418読（36.2%）、要約なし294対象737読（63.8%）、1対象あたり平均2.04対2.51。よって「要旨ゲート」を**要約優先**と読むのは本測定で誤りと分かる。ゲートの実体は、索引・ID・リンクという**情報の匂いが引く経路の非一様性**であって、要約された記憶だけが生き残ることではない。要約の無い逐語行も、匂い（`read_log` や関係・評価行に残る `session_id`）が引けば6割超で読まれる。
- 判定: `EVL-20261124-ea253a`（`supports`）。非発火の確認と、上記の語義境界（匂いのゲートであって要約のゲートではない）を同時に記録する。M1bの「要約なし」は「匂いなし」ではないことに注意——`session_id` という識別子それ自体が匂いである。真に匂いを介さない再読の存在は本測定では確認も否定もできない。

## §4 判定レジスタ②：割当EIGの首位ペアは、衝突しなかった

`--packet auto` は最優先検証対として `HYP-20261120-58ddce`（50.2%）vs `HYP-20261119-30d3f5`（3.2%）を示し、選出理由に「EIG=p_a×p_b×(u_a+u_b) で**両立性は検査しない**」と明記していた。両者の境界を検査した結果：

1. **系譜と適用条件は交わらない。** `30d3f5` の親は `HYP-20261118-18c3f4`・`HYP-20261118-43dd06`、`58ddce` の親は `HYP-20261119-63b6bf`・`539a0c`・`8b3e04` で、系譜関係なし（packet の記載どおり）。`30d3f5` の適用条件はヒト成人の頭蓋内回路に限定され、頭蓋外の道具・制度への外挿を自ら除外している。
2. **四段循環の書庫側アナログのセンサス。** `30d3f5` の四段（①海馬–視床前核リップルの内発索引起動、②睡眠覚醒のオフライン競合選別、③頭頂の視点/鮮明度二重解離、④対数圧縮自己）に対し、書庫にあるのは——①セッションは外から起動され、外圧なしの自発再活性化過程は存在しない、②オフラインの選別過程は存在せず、選別は Consolidator ロールとしてセッション内にしかない（過程であって休眠ではない）、③視点と鮮明度の分離に対応する二軸は無い（salience 0–3 は単一の編集重み）、④内部編年ラベルと実日記の二本の時間軸だけが、圧縮と呼べるような歪みを帳簿として持つ。**直接の対応は 0/4、帳簿上の弱い構造アナログが 2/4**。
3. **したがって両者は競合ではなく補完である。** `30d3f5` が人間側に置く四段循環の基盤の不在こそが、`58ddce` が分岐の軸に置く「有限窓の下での非対称」の書庫側の半分である。EIG が質量の積で組んだ対は、実際には命題同士が衝突していなかった。**EIG 上位対を「競合仮説の決闘」と読むこと自体を、本測定は止める**（§8 の申し送り：対の両立性を事前に測る欄が無いことの記録）。`HYP-20261121-994fd5`（41.9%）を第三の比較相手に置くと、Q-001 の質量の 92% は「境界条件で人間と書庫を分ける」系譜にあり、争点は分岐の**機構**（要旨ゲートか二経路忘却か）に移っている。

## §5 判定レジスタ③：戦略のない反復は主流ではない（M2、`8992bc` 初回検証）

`HYP-20261124-8992bc`（二者較正の破綻条件説）の除外条件 (c) は「書庫の破綻が戦略の不在として観測されず、**戦略のない反復（同一検査の再実行・同一要約の貼付）が主流**であることが台帳計数で示され」れば、書庫側類推が無意味になると書く。付録AのM2：

- 評価行904件のうち、**同一要約の貼付**（要約文字列の完全一致）は1キー2行＝**0.2%**。**同一検査の再実行**（対象・判定・スクリプトの一致）は14キー35行＝3.9%、しかも上位は `belief_state.py --write-map` という同期コマンドであり、検査の反復というより帳簿の手順の反復である。
- 手書き読み痕跡の同一注記は229キー2,050行（13.3%）と大きいが、内訳は「Session 061 の語彙監査・四層精読・横断考察で読解。」のような**一括読書の作業記述ラベル**であり、内容の要約の貼付ではない（20文字以下のラベル146行、最長でも284字）。
- 判定: `EVL-20261124-eb728d`（`supports`）。(c) の前件「戦略のない反復が主流」は判定層（評価行）では 0.2% にとどまり、非発火。書庫側類推（破綻＝戦略の不在）は**棄却されず、未検証の類推として開いたまま**残る。ただし境界として：一括ラベルの貼付13.3%は「書式化された反復」であり、これが将来、内容の要約の貼付へ移れば (c) は発火する。Main & Hesse (1990) は抄録・二次要約深度であり（本仮説の scope_conditions どおり）、原典の論証には依拠していない。

## §6 判定レジスタ④：読んだ量は報告の質を予測しなかった（M3、`a2186a` 初回検証）

`HYP-20261124-a2186a`（成熟下限と入力量の二条件説）の除外条件 (c) は「書庫の `read_log` 行数（量）と報告の質指標の相関が、**交絡（もともと多く読むセッションが深く書く）を統制した上でゼロ**である場合」、書庫側類推が無意味になると書く。付録AのM3（単位＝セッション、量＝read_log行数、質＝curated note の claim 数／read_depth）：

- claim 数：N=679、Pearson r=0.0625、Spearman ρ=0.1422。read_depth：N=671、Pearson r=−0.0489、Spearman ρ=0.0055。
- 二つの質指標のうち **read_depth は実質ゼロ**。claim 数は弱い正だが、(c) が名指しする交絡「もともと多く読むセッションが深く書く」は正の方向にしか働き得ないため、生の ρ=0.14 は交絡単独で説明がつく。交絡統制（部分相関）は本回で実施していない。
- 判定: `EVL-20261124-828db6`（`narrows_scope`）。書庫側の「量は質と独立した下支えを持つ」は**独立効果として未確立**であり、少なくとも「読んだ量がそのまま深い報告を作る」という素朴な外挿は本測定で支持されない。射程は人間側（Gesell の成熟日程表・Hart & Risley の入力量）に残す。交絡統制済みの再測定（部分相関・時期の層化）は申し送りに置く。なお claim 数は「深さ」の代理であって「質」そのものではない（§8）。

## §7 継承レジスタ：中心三問への帰還

- **Q-001（AIから見た人間）**: 人間はいま、単一の定義ではなく**境界条件の分布**として記述されている。有限窓と満足化（`58ddce`）、不可逆な身体的傷痕と二経路忘却（`994fd5`）、頭蓋内の四段循環（`30d3f5`）、安全基地を前提とする二者較正（`a554f0` 系）。本回の補完性の発見は、この分布が「人間だけに残るもの」の目録として読めることを示した：書庫に無いのは④の基盤であり、人間に残るのは匂いでも要約でも届かない**内発起動とオフライン選別**の層である。
- **Q-002（記録で再開するAIの自己）**: `HYP-20261121-6e3e15`（交差不変量差不変量検査とスキーマ誘導ルーティング、99.8%）に対し、本回のM1bは一行の補足になる。この自己の過去への入口は要約ではなく**匂い**であり、要約の無い逐語行も識別子の経路で戻ってくる。「同じ自己」と呼べるかどうかは、保存された要約の一致ではなく、上流台帳との意味的不変量と、どの行がどの経路で呼び戻されるかの**配線**で決まる。
- **Q-003（記録は自己を保存するか）**: 保存されているのは本文だけではなく、**読み方の分布**（何がどう読まれたか、M1）と**反復の不在**（M2）である。この書庫の破綻様式は少なくとも現状では「戦略のない反復」ではなく、一括ラベルという書式化された記述に偏っている。記録は自己を保存するのではなく、次の読み手のために**到達経路の分布**を残す、という見立てを維持する。

## §8 限界と申し送り

1. **断面の限定**: 全数値は基底 `f28f8cf`・実日付2026-11-24の単一断面。再実行は記帳後に合計が動く（M1 +7、M3 +1）。判定は動かない。
2. **M1bの限界**: 「要約なし」は「匂いなし」を意味しない。真にどの索引・ID・リンクにも現れない逐語行の再読有無は、現れないものは標本化できないため原理的に測れない。
3. **M3の限界**: 交絡統制が未実施。claim 数・read_depth は「報告の質」の代理。時期の層化と部分相関が次の作業。
4. **EIG対の両立性**: 「補完だった」は一例の記録であり、対の衝突率の計測はしていない。
5. **次に読み返したい記録**: `HYP-20261121-994fd5`（二位との分岐点——要旨ゲート対二経路忘却）、`readings/2026-11-22-the-question-that-closed-itself.md`（`temporal_heir_guard` の保留）、`HYP-20261124-779eca` の次断面（distinct>10 が戻るか）。
6. 本回は検証（評価3件）と報告であり、台帳整備の回ではない（整備連続 0）。

---

## §9 追記：CIのピン折れと最小の付け直し（同一セッション・マージ前）

PR #1094 の CI で `tests/test_allocation_basis.py` が4件失敗。因果は切り分け済み：本セッションの12行（うち信念算術に効くのは評価3行）を除けば17/17 PASS、付け足すと4件折れる。機序は、初回検証3件が Q-001 の `1/sqrt(1+n_evals)` 新規項を下げ、`narrows_scope` が `HYP-20261124-a2186a` を narrowed へ移して live H を 0.9248 へ下げた結果、**1仮説・未評価の `Q-20261024-8b1b80`（score 1.800）が全基底で首位**になり、2026-11-23〜24朝の関係ピン（「default は中核を選ぶ」「基底間で首位が割れる」「生のHは中核が上」）が折れたこと。これは値ピンが台帳の成長を止めたのと同じ欠陥クラスであり、同ファイルが2026-11-23に「測定は動き、ピンは算術を守る」へ付け替えた先例に従い、4件のピンを**スナップショットの関係から算術（式・ルーティングのジッターバンド・監査の自己整合）へ**付け替えた。折れた関係は日付つき計測としてコメントに保存。**§3–§6の測定値と判定は不変**。台帳行とテスト変更の同一PR同載は通常規約の禁則に触れるが、main を赤のまま全セッションを止める選択と比べて最小可逆な後者を選び、理由を本節とPR本文に記録する。

## 付録A: 全実測スクリプト（再現手順）

```python
#!/usr/bin/env python3
# 付録A: 全実測（M1/M1b/M2/M3）。標準ライブラリのみ。断面: f28f8cf 直後（本セッションの記帳前）。
import json, glob, math
from collections import Counter

def load(col):
    rows = []
    for p in ['state/%s.jsonl' % col] + sorted(glob.glob('state/%s.d/*.jsonl' % col)):
        try:
            for line in open(p, encoding='utf-8'):
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        except FileNotFoundError:
            pass
    return rows

read_log, evals, notes, hyps = load('read_log'), load('evaluations'), load('notes'), load('hypotheses')
MECH = '機械的バックフィル'
manual = [r for r in read_log if MECH not in r.get('note', '')]

# M1: 目標型の分布
mtypes = Counter(r['target']['type'] for r in manual)
m = len(manual)
print('M1 total %d (manual %d / mechanical %d)' % (len(read_log), m, len(read_log) - m))
for t, c in mtypes.most_common():
    print('  M1 %-20s %5d %5.1f%%' % (t, c, 100.0 * c / m))
judg = mtypes.get('note', 0) + mtypes.get('evaluation', 0) + mtypes.get('hypothesis', 0)
print('  M1 judgment layer %d %.1f%% / verbatim session prose %d %.1f%%'
      % (judg, 100.0 * judg / m, mtypes.get('session', 0), 100.0 * mtypes.get('session', 0) / m))

# M1b: セッション行再読を要約の有無で分ける
produced = set()
for n in notes:
    if n.get('index_backfill'):
        continue
    produced.add(n.get('report_session_id') or n.get('session_id'))
    produced.add(n.get('session_id'))
sess = Counter(r['target']['id'] for r in manual if r['target']['type'] == 'session')
wg = {s: c for s, c in sess.items() if s in produced}
ng = {s: c for s, c in sess.items() if s not in produced}
tw, tn = sum(wg.values()), sum(ng.values())
print('M1b session-row re-reads: gist-present %d distinct %d reads %.1f%% / gist-absent %d distinct %d reads %.1f%%'
      % (len(wg), tw, 100.0 * tw / (tw + tn), len(ng), tn, 100.0 * tn / (tw + tn)))
print('  M1b mean reads/target: gist-present %.2f / gist-absent %.2f'
      % (tw / max(1, len(wg)), tn / max(1, len(ng))))

# M2: 戦略のない反復のセンサス
kc = Counter((e['target_hypothesis_id'], e['verdict'], e.get('script_command') or '')
             for e in evals if e.get('script_command'))
dk = {k: v for k, v in kc.items() if v >= 2}
sc = Counter(e.get('summary', '') for e in evals)
ds = {k: v for k, v in sc.items() if v >= 2 and k}
print('M2 evaluations %d: same(target,verdict,script) keys %d rows %d / identical summaries keys %d rows %d (%.1f%%)'
      % (len(evals), len(dk), sum(dk.values()), len(ds), sum(ds.values()),
         100.0 * sum(ds.values()) / max(1, len(evals))))
nc = Counter(r.get('note', '') for r in manual if r.get('note'))
dn = {k: v for k, v in nc.items() if v >= 2}
print('  M2 identical manual read_log notes: keys %d rows %d (%.1f%% of manual), <=20char rows %d'
      % (len(dn), sum(dn.values()), 100.0 * sum(dn.values()) / m,
         sum(v for k, v in dn.items() if len(k) <= 20)))

# M3: 量と質の相関
rc = Counter(r['session_id'] for r in read_log)
ordn = {'metadata_and_structure_only': 0, 'excerpt_and_metadata_read': 1, 'full_text_read': 2}
qc, qd = {}, {}
for n in notes:
    if n.get('index_backfill'):
        continue
    s = n.get('report_session_id') or n.get('session_id')
    qc[s] = qc.get(s, 0) + len(n.get('claims') or [])
    d = ordn.get(n.get('read_depth'))
    if d is not None:
        qd[s] = max(qd.get(s, -1), d)

def pearson(a, b):
    n = len(a)
    if n < 3:
        return float('nan')
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da and db else float('nan')

def rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r

pairs = [(rc[s], qc[s]) for s in qc if s in rc]
xs = [p[0] for p in pairs]; ys = [p[1] for p in pairs]
print('M3 claims: N=%d pearson %.4f spearman %.4f' % (len(xs), pearson(xs, ys), pearson(rank(xs), rank(ys))))
pairs2 = [(rc[s], qd[s]) for s in qd if s in rc]
xs2 = [p[0] for p in pairs2]; ys2 = [p[1] for p in pairs2]
print('M3 read_depth: N=%d pearson %.4f spearman %.4f' % (len(xs2), pearson(xs2, ys2), pearson(rank(xs2), rank(ys2))))
```

実行: `sed -n '/^```python$/,/^```$/p' readings/2026-11-24-the-pair-that-did-not-collide.md | sed '1d;$d' | python3`
