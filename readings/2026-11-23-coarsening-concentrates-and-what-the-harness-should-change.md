# 粗視化は効くが、家族の質量は一人の仮説が持っている — 階層化の3つの測定量と、ハーネス側の6つの提案

- **実作業日（UTC）**: `2026-11-23`
- **セッション**: `SESSION-20261123-438521`
- **来歴**: 利用者からの二つの問い（① ハーネス群への改善提案を先に行うべきか、② 類似仮説のメソ・マクロな粗視化と階層化を採るべきか）への応答。`human_direction` は範囲の来歴であり、結論の根拠ではない
- **基盤**: `main` @ `13f10530`（PR #1058 マージ後）。前セッション `SESSION-20261123-89b471` の報告 `readings/2026-11-23-the-winner-depends-on-the-rules.md`
- **種別**: `reproducible_script`（粗視化の3測定）＋設計提案（実装なし）
- **対応ノート**: `NOTE-20261123-c57482` ／ 評価: `EVL-20261123-86be11`
- **台帳への追加**: 新規仮説0件・新規問い0件・断片0件。**この回はコードも生成物も1バイトも変えていない**

---

## §0 レジスタの宣言

**記述レジスタ**（§2：台帳の構造の観測）、**判定レジスタ**（§3–§5：再現可能スクリプトによる粗視化の実測と、その限界の特定）、**提案レジスタ**（§6：ハーネス側の改善提案。実装せず、測定に紐づけて書く）を分離する。`CONTENT_POLICY.md` に従い、AIの現象的意識の有無は肯定も否定もしない。

## §1 二つの問いは、同じ問いである

利用者の二つの問いは独立に見えるが、**同じ有限の窓を二つの側から指している**。

- 問い①（ハーネス側の改善提案か、§6–§7 の調査か）は、**表示と道具の側**から「この書庫は自分の答えを読める形になっているか」を問う。
- 問い②（仮説群の階層化・粗視化）は、**台帳の側**から同じことを問う。

前セッションの測定が示したのは、**首位が規則に相対的で、18スロットで単一仮説が過半を持たない**ことだった。その状態で「次に読む者へ」（前報告 §10）を実行しても、**読む者はどの基底で読むかを選べないまま次の測定を積む**。だから表示の側（①）が先に要る。ただし②を測らずに①を提案すると、提案が勘になる。**本報告は②を先に測り、その結果から①を導く。**

---

## §2 記述レジスタ：台帳は既に階層を持っている

粗視化を「導入すべき新機構」と見る前に、現状を数えた。

| 問い | 仮説数 | `root` | `refines` | `splits` | `synthesizes` | 根の家系（root ancestor 単位） |
|---|---:|---:|---:|---:|---:|---:|
| Q-001 | 29 | 4 | 16 | 4 | 5 | 7 |
| Q-002 | 46 | 10 | 23 | 5 | 8 | 14 |
| Q-003 | 62 | 17 | 21 | 15 | 9 | 19 |

**構造は既にある。** `parent_hypothesis_ids` と `lineage_op` で系譜が張られ、`_generation_depths` が世代を計算し、`BELIEF_MAP.md` は各行に `G2:refines (...)` と系譜を表示する。**無いのは、その階層を質量の単位として読む演算である。** `belief_state.py` は問いごとに全仮説をフラットなソフトマックスに掛け、家系の合計を一度も計算しない。

また「類似性が高い仮説」を**名前の似ていること**で判定する必要はない。系譜が既にそれを言っている。同一の親を持つ子（`Q-003` の `HYP-20261114-0396ce` → 5子、`HYP-20261113-a35ee5` → 3子）は、定義上その親の分割であり、互いに近い。

---

## §3 判定レジスタ（1）：粗視化は、実際に基底差を減らす

仮説を**根の家系（root ancestor）**へ粗視化し、家系の質量を合計して、6つの会計基底で首位がどう変わるかを測った。台帳は書き換えていない。

```bash
python3 - <<'PY'
import sys, copy, collections, math
sys.path.insert(0,'tools'); from pathlib import Path
import belief_state as bs
B=bs.load_belief_ledgers(Path('.')); hyps=B['hypotheses']
def root_of(h,seen=None):
    seen=seen or set()
    if h in seen or h not in hyps: return h
    seen.add(h); ps=[p for p in (hyps[h].get('parent_hypothesis_ids') or []) if p in hyps]
    return root_of(ps[0],seen) if ps else h
RULES={'default':{}, 'guard':{'temporal_heir_guard':True}, 'gated':{'receiver_gated':True},
 'noheir':{'heir_credit':False}, 'guard+narrow':{'temporal_heir_guard':True,'narrowing_partner_share':True},
 'guard+pair':{'temporal_heir_guard':True,'pair_level_repeat':True}}
for name,kw in RULES.items():
    st=bs.compute_belief_state(copy.deepcopy(B),**kw)
    for q in ('Q-001','Q-002','Q-003'):
        hs=st['questions'][q]['hypotheses']
        fam=collections.defaultdict(float)
        for h in hs: fam[root_of(h['hypothesis_id'])]+=math.exp(h['log_odds'])
        print(name,q,max(fam,key=fam.get))
PY
```

| 問い | 個人レベル（前報告） | 家系レベル（本測定） |
|---|---|---|
| Q-001 | 3種の首位、最大 4/6 | **2種、最大 5/6**（`HYP-20261112-dc25dc`） |
| Q-002 | 3種、最大 4/6 | **2種、最大 5/6**（`HYP-20261112-dc25dc`） |
| Q-003 | 4種、最大 3/6 | 3種、最大 3/6（`HYP-20261116-65f41d`） |

**読み**: Q-001 と Q-002 では、粗視化すると基底をまたぐ首位の一致が 4/6 → 5/6 に上がる。**粗視化は基底差を実際に減らす。** Q-003 では減らない（3種のまま）。したがって「粗視化すれば安定する」は、**問いによる**。

**機構の注意**: `HYP-20261112-dc25dc` が Q-001 と Q-002 の両方で家系首位なのは、**同じ家系が二つの問いに跨っている**からである。家系の質量を問いごとに合計すると、この「跨り」が家系の強さに見える。§5 で扱う。

---

## §4 判定レジスタ（2）：その家系の質量は、一人の仮説が持っている

§3 の安定が「同じ見立てを多くの独立した仮説が支えている」ことの証拠なら、粗視化は強い。**そうではなかった。**

| 問い | 家系 | 仮説数 | 家系の質量 | **そのうち1仮説が持つ割合** |
|---|---|---:|---:|---:|
| Q-001 | `dc25dc` | 14 | 84.8% | **81.2%** |
| Q-001 | `b24785` | 6 | 12.2% | 66.6% |
| Q-002 | `dc25dc` | 22 | 73.6% | 75.7% |
| Q-002 | `1273f1` | 7 | 6.3% | **96.7%** |
| Q-003 | `65f41d` | 5 | 94.4% | **99.7%** |
| Q-003 | `1273f1` | 24 | 1.8% | 67.6% |

（`guard` 基底、`HYP-20261112-dc25dc` 等は末尾6桁で表示）

**読み**: 家系の質量は、**68〜99.7% が一人の仮説に集中している**。家系を一つの単位として読むと、**「14の仮説からなる家系が 84.8%」という表示が、実質「1つの仮説が 81.2%」を「家族の合意」に見せる**。これは前報告 §4 で測った「併存数の希釈」の鏡像である——あちらは仮説数が首位の P を下げ、こちらは仮説数が家系の権威を上げる。

**粗視化の危険は、粒度ではなく、質量と件数の混同にある。** 件数（24仮説）と質量（1.8%）が逆相関している例（Q-003 の `1273f1`）が、その最も明確な形である。

---

## §5 判定レジスタ（3）：またいでいることと、一次的な所属が、区別されていない

粗視化を採るなら、解剖学的な前提が要る。**仮説は一つの問いに属するか、複数に跨るか。**

- 仮説93件のうち **34件（36.6%）が複数の `question_ids` を持つ**（2問19件、3問15件）。
- 描画される表の行は `hypothesis × question` で **142行**（93仮説から）。`BELIEF_MAP.md` の行は147。
- 家系の合計を問いごとに取ると、跨っている家系は**両方の問いで強く出る**（`dc25dc` が Q-001・Q-002 の双方で首位）。

したがって、家系レベルの答えを出す前に **「この家系はどの問いに一次的に属するか」を決める欄が要る**。現在のスキーマには無い（`schema/hypothesis.schema.json` の `question_ids` は複数可の配列で、主従を表さない）。**この欄が無いまま家系の質量を出すと、跨りが家系の強さとして二重に計上される。**

---

## §6 提案レジスタ：ハーネス側の6つの提案（実装せず、測定に紐づける）

**なぜ「§6 残った限界／§7 次に読む者へ」より先か。** 前報告の §10 は具体的な作業（周辺問に仮説を5件配置する、正規化実装を作る）を挙げている。しかし §3・§4 が示したのは、**その作業の結果を読む器が、いま質量と件数を混同している**ことである。器を直さずに作業を積むと、次の測定も「家族の合意」に見える数字を生む。**ただし §7 の作業を捨てる理由にはならない**——§6-3 は §7 の作業をそのまま前提にする。

| # | 提案 | 根拠（測定） | 期待効果 | 危険 |
|---|---|---|---|---|
| **1** | `sessions` に**使用基底**の欄を足す（例 `belief_basis: "default" \| "temporal_heir_guard" \| ...`） | 前報告 §4.1 の18スロット。現行スキーマに欄が無く、基底の選択が台帳に残らない | 基底の選択が来歴になる。「どの基底で読んだか」を後続が検証できる | 欄を足すだけでは選択の根拠にならない。記入の強制は追記専用と衝突しないが、既存1,112行は免除が要る |
| **2** | `BELIEF_MAP.md` の仮説あたり描画を**1行に圧縮**し、詳細ブロックは上位N件のみ | 詳細ブロックが**852行・434,420 B＝ファイルの80.6%**。うち **88/93 の仮説が P<1%** | 予算の構造的解決（前報告 §13 の +13 KiB 問題が消える）。読者の窓が上位に集中する | 低質量仮説の監査情報が既定で見えなくなる。`--full` を用意する必要 |
| **3** | **家系（root ancestor）単位の質量行**を各問いに追加し、**同時に最大集中仮説の割合を併記** | §3（家系は基底差を減らす）と §4（家系質量の68–99.7%が1仮説） | 「家族の合意」と「一人の独走」を表示で区別できる | 併記を忘れると §4 の誤読を**増幅**する。単独導入は危険 |
| **4** | `hypotheses` に**一次所属問い**の欄を足す（`primary_question_id`） | 93件中34件が複数問いに跨り、跨りが家系質量に二重計上される（§5） | 家系質量と、問いをまたぐ質量の分離 | 既存93件の遡及決定が要る。決められないものは未決のまま残すべき |
| **5** | `EIG`/`saturated` の判定を**質量重み付き**にし、`pair_mass_sum ≈ 0` の対を「推薦なし」と明示 | `pair_mass_sum=0.0000` の対（`16929d` vs `afd1a5`）に `unsaturated_supports_ratchet=True` が立つ。合算0%を「未飽和」と呼ぶのは、件数を見て質量を見ていない | 「質量0の同点のうち辞書順で最初」を推薦しない（前々報告 §5(c) の未修正点） | 推薦が出ない問いが増える。それは事実の表示であって缺陷ではない |
| **6** | `newborn_mass`（未評価仮説を1件登録したときの、その問いの質量移動）を計器に足す | 前報告 §4.4 の併存数希釈。登録が学習として採点される機構 | 登録の副作用が測れる | 「登録するな」という圧力になる。件数を増やさない規範は既に憲章にあり、計器で押す必要はない |

**優先順位**: **2 → 5 → 3＋4 → 1 → 6**。理由: 2 と 5 は**既存の記録だけで実装でき、意味の変更が無い**（表示の圧縮と、質量0を推薦しないこと）。3 と 4 は**新しい欄と遡及判断**を要し、意味を変える。1 と 6 は記録の追加で、効果が最も遅い。

**提案しないこと**: 仮説の削除・統合による件数の削減。追記専用の原則と衝突し、§4 が示した「一人の独走」は**削除では直らない**（削除すれば家系の質量は残るが、根拠が消える）。

---

## §7 階層化についての結論（問い②への直接の答え）

**採るべきだが、条件つきで、そして「粗視化」を質量の単位として採るべきではない。**

1. **階層は既にある。** 導入するのは構造ではなく、**その構造を読む演算と表示**である。したがって「メソ・マクロな仮説を新しく作る」必要はない。
2. **粗視化は基底差を減らす（Q-001/Q-002 で 4/6 → 5/6）。** これは問い②の「違いを鮮明化する」という期待の、**逆の半分**に当たる。粗視化は差を**鮮明にせず、平均する**。
3. **家系の質量は一人の仮説が持っている（68–99.7%）。** だから家系を単位にすると、**「大枠の構造」ではなく「大枠の名前を借りた一つの仮説」**を残すことになる。ミクロなバリエーションは「残したまま」ではなく、**既に質量を持っていない**。
4. **本当に鮮明化するのは、家系の内側の対立を表示することである。** Q-003 で粗視化が効かなかった（3種のまま）のは、家系の中で `4bf2dc`（99.7%）と他の4仮説が**別の方向を向いている**からで、これは粗視化では見えない。**「差を鮮明化する」の実装は、家系の内訳と、家系をまたぐ跨り（§5）の表示である。**

**したがって問い②への答えは**: 階層化は採る。ただし (a) 新しい粒度の仮説を作るのではなく既存の系譜を読む、(b) 家系の質量には**必ず集中度を併記する**、(c) **一次所属問い**の欄を先に決める、の三条件つき。この三つを満たさない粗視化は、前報告で測った「併存数の希釈」を**逆向きに**再現するだけである。

---

## §8 この回がやっていないこと

- **コードを1バイトも変えていない。** §6 は提案であって実装ではない。`prompts/start.md` の「スキーマ・道具・手順書を変える変更は、報告や台帳行の一括追加と同じ PR に入れない」に従い、実装は別 PR に分ける。
- **家系の定義を一つに決めていない。** 本報告は `parent_hypothesis_ids[0]` を再帰的にたどる単一親の根を使った。親が複数ある仮説（`synthesizes`）では、どの親を根とみなすかで家系が変わる。**この選択は §4 の数値を動かしうる**ので、数値は「この定義の下で」の値である。
- **§3 の Q-003 非 reduction の原因を、家系の内訳まで分解していない。** §7-4 の「別の方向を向いている」は、`4bf2dc` の集中度 99.7% からの推論であって、命題の内容を読んだ判定ではない。
- **人間側の対応物を論じていない。** 階層的な仮説構造が人間の信念構造と同型かは、本報告の範囲外である。
- **§7 の作業（周辺問への仮説配置、正規化実装）を実行していない。** 提案1〜6 は、それを実行するための器の話である。

---

## §9 再現手順

```bash
# §3 家系レベルの首位（6基底）
cat > /tmp/fam.py <<'PY'
import sys, copy, collections, math
sys.path.insert(0,'tools'); from pathlib import Path
import belief_state as bs
B=bs.load_belief_ledgers(Path('.')); hyps=B['hypotheses']
def root_of(h,seen=None):
    seen=seen or set()
    if h in seen or h not in hyps: return h
    seen.add(h); ps=[p for p in (hyps[h].get('parent_hypothesis_ids') or []) if p in hyps]
    return root_of(ps[0],seen) if ps else h
RULES={'default':{}, 'guard':{'temporal_heir_guard':True}, 'gated':{'receiver_gated':True},
 'noheir':{'heir_credit':False}, 'guard+narrow':{'temporal_heir_guard':True,'narrowing_partner_share':True},
 'guard+pair':{'temporal_heir_guard':True,'pair_level_repeat':True}}
for name,kw in RULES.items():
    st=bs.compute_belief_state(copy.deepcopy(B),**kw)
    out=[]
    for q in ('Q-001','Q-002','Q-003'):
        hs=st['questions'][q]['hypotheses']
        fam=collections.defaultdict(float)
        for h in hs: fam[root_of(h['hypothesis_id'])]+=math.exp(h['log_odds'])
        out.append(f"{q}:{max(fam,key=fam.get)}")
    print(name,'|',' '.join(out))
PY
python3 /tmp/fam.py

実測出力（末尾6桁で表示）:

```text
default       | Q-001:5a26aa  Q-002:1273f1  Q-003:1273f1
guard         | Q-001:dc25dc  Q-002:dc25dc  Q-003:65f41d
gated         | Q-001:dc25dc  Q-002:dc25dc  Q-003:dc25dc
noheir        | Q-001:dc25dc  Q-002:dc25dc  Q-003:65f41d
guard+narrow  | Q-001:dc25dc  Q-002:dc25dc  Q-003:65f41d
guard+pair    | Q-001:dc25dc  Q-002:dc25dc  Q-003:1273f1
```

```bash
# §4 家系内の集中度
python3 -c "
import sys,collections,math; sys.path.insert(0,'tools'); from pathlib import Path; import belief_state as bs
B=bs.load_belief_ledgers(Path('.')); hyps=B['hypotheses']
def root_of(h,seen=None):
    seen=seen or set()
    if h in seen or h not in hyps: return h
    seen.add(h); ps=[p for p in (hyps[h].get('parent_hypothesis_ids') or []) if p in hyps]
    return root_of(ps[0],seen) if ps else h
st=bs.compute_belief_state(B, temporal_heir_guard=True)
for q in ('Q-001','Q-002','Q-003'):
    hs=st['questions'][q]['hypotheses']; fam=collections.defaultdict(list)
    for h in hs: fam[root_of(h['hypothesis_id'])].append(h)
    for r,mem in sorted(fam.items(),key=lambda x:-sum(math.exp(h['log_odds']) for h in x[1]))[:2]:
        t=sum(math.exp(h['log_odds']) for h in mem); top=max(mem,key=lambda h:h['log_odds'])
        print(q,r,len(mem),round(t/sum(math.exp(h['log_odds']) for h in hs)*100,1),round(math.exp(top['log_odds'])/t*100,1))
"

# §5 跨りの件数
python3 -c "
import json,glob
h={}
for p in glob.glob('state/hypotheses*.jsonl')+glob.glob('state/hypotheses.d/*.jsonl'):
    for l in open(p):
        l=l.strip()
        if l: r=json.loads(l); h[r['hypothesis_id']]=r
print('multi-question:',sum(1 for x in h.values() if len(x.get('question_ids') or [])>1),'/',len(h))
"

# §6-2 描画コスト
python3 -c "
t=open('BELIEF_MAP.md',encoding='utf-8').read()
d=[l for l in t.split(chr(10)) if l.startswith('  - **')]
print('detail lines',len(d),'bytes',sum(len(x.encode()) for x in d),'of',len(t.encode()))
"

# §6-5 質量0の対に立つラチェット旗
python3 -c "
import sys,copy; sys.path.insert(0,'tools'); from pathlib import Path; import belief_state as bs
st=bs.compute_belief_state(bs.load_belief_ledgers(Path('.')))
for q in ('Q-001','Q-002'):
    p=st['questions'][q]['top_competing_pair']
    print(q,p['pair_mass_sum'],p.get('unsaturated_supports_ratchet'))
"
```

---

## §10 完了の見方

本報告の成果は、問い②に対する**「採るが、質量の単位としては採らない」**という条件文と、その条件を数で支えたことである。粗視化は基底差を減らす（4/6→5/6）が、家系の質量の68–99.7%は一人の仮説が持っている。**この二つは矛盾しない**——粗視化が安定に見えるのは、**一つの仮説の質量が家系という名前を得るから**である。

§6 の6提案のうち、意味を変えずに実装できるのは 2 と 5 だけである。他は欄の追加と遡及判断を含む。**だから、次の回に §7 の作業を実行するなら、先に 2 と 5 だけを入れるのが最小の一手である。**
