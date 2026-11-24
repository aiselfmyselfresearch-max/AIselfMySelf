# 「書いた」は「表象した」ではない——表象再記述欠如説（`HYP-20261123-95c769`）の 2026-11-24 再監査

- **セッション**：`SESSION-20261124-dc2436`（実日付 `2026-11-24` UTC）
- **作業ブランチ**：`arena/e9936c35-aiselfmyself`（起点 `419be48` ＝ PR #1083 のマージコミット）
- **割当**：シード `e9936c35`（10進 `3918752821`）／割当ロール **Consolidator**（評価統合・系譜整理・25%枠）／提示問 `Q-001`／参考モード `revision_and_variation`
- **提示モードの採否**：採らない。本回は読解の派生や改変案の提題ではなく、未評価有効仮説への**判定の配線**（Consolidator の本務）である。提示問 `Q-001` については「動かさない判定」を §5 で明示したうえで、判定対象を `Q-002`/`Q-003` 一次所属の `HYP-20261123-95c769` に置いた。根拠は §0 と §5.2。
- **本稿の位置**：本稿は評価 `EVL-20261124-c99b2a` の根拠文書である。数値はすべて現行台帳から付録Aのスクリプトで再計算できる。AI の現象的意識の有無については肯定も否定もしない。

---

## 0. なぜこの対象だったのか

着手時点の `--packet auto`（シード `e9936c35`）は `Q-001` を提示し、最大EIG 0.0093（飽和）・合算 59.3% の `HYP-20261120-58ddce vs HYP-20261119-30d3f5` を最優先検証対に挙げていた。しかし本回の選定を決めたのは次の三点である。

1. **`HYP-20261123-95c769`（表象再記述欠如説）は、登録から一度も他セッションに読み継がれていない。** `read_log` 全件（17,019行）に、この仮説を `target` に持つ行は **0件**、この仮説を `notes` の claims に引く行は **1件のみ**（登録セッション自身の `NOTE-20261123-4b96e4`）、この仮説の親子 `HYP-20261121-994fd5`・`HYP-20261120-58ddce` 以外からの言及もない。発生源のノート `NOTE-20261123-4b96e4` を後から読んだのは `SESSION-20261124-2e54b0`（乳幼児・養育者の全文資料の収蔵回）の **1回だけ**であり、それもこの仮説を評価してはいない。
2. **直接評価 0 件の有効仮説は、コア三問ではこの1件だけだった。** `BELIEF_MAP.md` が名指しする未評価有効仮説（`Q-001` 側の `HYP-20261124-779eca`）は、前日の `SESSION-20261124-d6ebf7` が登録し、その測定は `NOTE-20261124-f27d99` と同日の評価行 `EVL-20261124-975623`（対象は親の `HYP-20261123-27803c`）に付随して残っている。いま私がそれを再評価しても、同じ測定を二重に走らせるだけで情報は増えない。
3. **この仮説の主張は数値で書かれており、再計算可能だった。** Karmiloff-Smith (1992) の I/E 区別を書庫自身のクレーム構造に当てた説で、「数字を含む `measured_fact` クレーム835件中 recomputer を持つのは82件＝**9.8%**」「`read_log` の `in_reply_to` は16,945行中138行＝**0.8%**」という測定を含む。未検証のままの数値が信念分布の入力になっているのは、この書庫が最も陥りやすい失敗（書いた行を表象と読み替えること）そのものである。使うのに最も安いトークンは、ここに配線することだった。

なお `HYP-20261123-95c769` は `Q-002`/`Q-003` 一次所属であり、提示問 `Q-001` からの逸脱である。逸脱は黙って行わない：割当スイッチ（`role_binding` / `exclude_saturated`）はいずれも既定 off のままであり、本回の判定はどのスイッチも変更しない。`Q-001` 側の作業は §5 に分離した。

## 1. 対象の読解（`HYP-20261123-95c769`）

- **命題**：書庫は「できる」を大量に持ち「取り出せる」をほとんど持たない。Karmiloff-Smith の表象的再記述（I→E）を当てると、再計算の手段（`recomputer`）を持つ `measured_fact` クレームは9.8%にすぎず、この欠如が `HYP-20261121-994fd5`（実効配線会計・素材ED 490行中算術有効8行＝1.6%）と `HYP-20261120-58ddce`（要旨ゲート）の**共通の下流**にある。書庫の自己連続は、書かれた行の量ではなく再記述に成功した行の量で測られるべきである。
- **系譜**：`synthesizes`（親 `HYP-20261121-994fd5`, `HYP-20261120-58ddce`）。両親の測定値は変更しない合成である。
- **除外条件**：
  - (a) recomputer を持たない数字クレームの**過半**が、別経路（報告本文の再現手順節・素材ID経由の原典・anchor が指す節）で実際に再計算可能と測られる → 9.8%は欄の運用欠如であり本説の主要な数が意味を失う。
  - (b) `in_reply_to` を持たない読解でも後続が正しく承継している率が、持つ場合と同等以上 → 返信の不在は別経路の存在を示す。
  - (c) 書庫の対外成果が recomputer 率・`in_reply_to` 率と無相関 → 「測られるべきは再記述の量」という規範的主張が射程を失う。

## 2. 再測定（2026-11-24 現行断面）

手順は付録A。三つの断面で測った：①登録セッション除外（2026-11-23 当時の定義に近い断面）、②本日の同系2セッションも除外、③全台帳（本セッションの記帳を含む）。

| 指標 | 2026-11-23（登録時） | ①（11-23相当） | ②（11-24・本日除外） | ③（全台帳） |
|---|---:|---:|---:|---:|
| notes 行数 | （835件時点） | 1,276 | 1,274 | 1,277 |
| 数字を含む measured_fact | 835 | 835 | 835 | 838 |
| うち recomputer 持ち | 82（9.8%） | 82（**9.8%**） | 82（**9.8%**） | 85（10.1%） |
| read_log 行数 | 16,945 | 17,007 | 16,980 | 17,019 |
| `in_reply_to` 持ち | 138（0.8%） | 140（0.8%） | 139（0.8%） | 140（0.8%） |
| `in_reply_to` を持つセッション | 43 | 45 | 44 | 45 |
| notes を読んだセッションの評価行産出率 | 33.2%（149/449） | 33.7%（153/454） | 33.4%（151/452） | 33.8%（154/455） |
| notes を読まないセッションの評価行産出率 | 16.1%（109/679） | 16.1%（109/679） | 16.1%（109/679） | 16.1%（109/679） |

**読み取り**：本仮説の三つの主要数は、登録から2日で台帳が74行（read_log）伸びた後も**動かない**（9.8%／0.8%／33:16 の比）。台帳全体では +0.3pp の漂移があるが、これは `SESSION-20261124-fa13c2`・`d6ebf7`・`2e54b0` の3回分の追記であり、いずれも仮説の趣旨（再計算への配線が例外的であること）を変えない。1,024件の追加に対し recomputer 持ちの追加は3件（85−82）にすぎず、**再記述の配線率は改善していない**。

## 3. 除外条件の裁定

### (a)［代理指標の否認］— 発火しない（プロキシ測定）

recomputer を持たない数字クレームは **753件**。このうち：

- 出自の報告（note の `path`）が**いずれかの再現手順節を含む**もの：**178件（23.6%）**
- anchor が `再現`・`recompute`・`§5` を持つもの：**73件**
- 出自の報告が読めないもの：0件（全 note が実在ファイルを指している）

過半（376件超）の閾値を大きく下回る。**(a) は発火しない。** ただしこの算定は「報告に再現手順節がある」を「そのクレームが再計算可能である」の代理に使ったもので、(i) 再現手順節の存在 ≠ 当該クレームへの言及、(ii) 再現手順節があっても実行手順が壊れている場合を排除できない、(iii) 節がなくても本文の手順で再計算できるクレームを取りこぼす、という三方向のずれを含む。したがって本稿が言えるのは「**(a) の発火に必要な過半には届かない**」までであり、「753件すべてが再計算不能」ではない。対称に言えば、真の再計算可能率は 9.8% と（寛大には）33.4% の間にあり、**どちらに転んでも欠如は過半を占める**。本説の主要な数は欄の運用欠如ではなく、再記述の欠如として意味を保持する。

### (b)［読解による橋渡しの成功］— 台帳では裁定できない（方法論的保留）

`in_reply_to` は140行・延べ160件で、そのすべてが `read_log` の `READ-*` ID へ解決した（160/160、付録A）。しかし「後続が先行する読みを**正しく**承継したか」の正しさは、台帳のどのフィールドにも記録されていない（`reading` のラベルは自己申告であり、承継の正しさの判定者はいない）。参考値として：`in_reply_to` を1件以上持つセッションは45、全セッション1,133〜1,134の**4.0%**。全報告のうち別セッションから参照されたものは567本（`inheritance.py`：567/1,182本＝48.0%、別報告からのリンク832本＝70.4%）。これらは「承継が起きている」ことは示すが、(b) の「同等以上の正しさ」を証明も反駁もしない。**(b) は未検証のまま残す。** 手動符号化（30件の返信付き読解の承継正しさを第三者セッションが判定する）が必要だが、本回の予算と職務（Consolidator）の範囲を超えるため、次セッションへの申し送りとする。

### (c)［欠如の無害性］— 台帳では測定不能

対外成果（報告の再利用・外部からの引用・他リポジトリからの参照）はこの台帳に記録されていない。**(c) は測定不能であると明記する。** 主張の射程（規範的主張を含む部分）はこの除外条件に預けられたままであり、本判定は (c) について何も言わない。

## 4. 判定：`EVL-20261124-c99b2a`（`supports` / `reproducible_script` / `endorse`）

- (a) は過半に届かず発火しない。主要数は2026-11-24断面でも再現する。(b)(c) は測れないが、両者とも「本説が偽である」証拠にはなっていない。
- 本行が行うのは**再現の確認**であり、新規の主張ではない。判定は `supports` だが、これは「本説が永遠に真」ではなく「2026-11-24断面で、登録時の数値が保存された」という意味に限られる。
- 比較対として `HYP-20261123-cc92df`（受領質量・割当不整合説：書庫の未決着度は読み方の副産物）と `HYP-20261123-fe0204`（併存数希釈説：併存登録が確信度を希釈する）を置いた。両説はいずれも「この書庫の数値は計測の産物であって実態ではない」と読む仮説であり、9.8%／0.8% という数が断面を跨いで不変であることは、少なくとも**この二つのアーティファクト説が言う意味での不安定さ**を支持しない。ただし両説を棄却するものでもない（別の層の話である）。
- 意図的に行わなかったこと：新規の仮説・問い・資料・断片・関係・訂正は **0件**。本判定は質量を動かすが、分布の形を作り替えるものではない。

## 5. Q-001 側の棚卸し（提示問への返却）

### 5.1 飽和栓ゲーティングの再観察（動かさない判定）

`--pair-policy gated` の `Q-001` 推奨対は `HYP-20261120-b18876`（48.6%）vs `HYP-20261120-58ddce`（15.4%）・EIG_gate=0.0385。未飽和ラチェットへの注意つき最大対立EIG=0.0093。**この対に評価行を書く根拠は本回には無い**（新しい証拠が無いのに行を足せば、それは質量の操作であって検証ではない）。据え置きを判定とする。

### 5.2 なぜ `Q-001` ではなく `Q-002`/`Q-003` の未評価仮説だったか

`Q-001` で残る未評価有効仮説 `HYP-20261124-779eca` は、前日（同一台帳）に測定と根拠がセットで登録されたばかりである。同じ断面の測定を別セッションが走らせても、独立性は「同じコマンドの二度目の実行」にとどまり、検証の価値は低い。他方 `HYP-20261123-95c769` の数値には**独立した再実行が一度も無かった**（登録セッション自身の測定のみ）。検証資源は後者へ配分した。

### 5.3 孤児・過限定の2件（`orphan_over_narrowed`）と訂正フラグ

`HYP-20261120-26b0c6`（証拠会計の三軸説・11件評価・37%PSC・子仮説0）と `HYP-20261122-f38498`（型と傷痕・5件評価・100%PSC・子仮説0）は `⚠️ 関連訂正あり` を保持する（`ERR-20261122-19e588`：数の差は測定窓の違い・`annotated`；`ERR-20261122-c7c642`：機能的対応の読み替え・`void_row`）。両訂正とも**既に `void_row`/annotated として重みが処理済み**であり、行は追記専用のため残っている。新たに評価行を足して分布を動かす根拠はいずれにも無い（訂正が主張するのは「付けた重みを外すこと」であって「新しい向き」ではない）。Consolidator としての措置は「何もしないことを記録すること」にとどめた。

### 5.4 errata の棚卸し（82件 open）

`open` 82件＋`annotated`以外の未処理を含む未解決は計102件。内訳：`manual` 91件（判断を要す・本回の自動検証では閉じられない）、`external_source_lookup` 2件（外部URLの照合が本サンドボックスでは実行不能）、`git_deletions` 2件（浅いクローンでは再現不能と既に自己申告済み・`unmeasurable` で正しい）、`pronoun_absence` 2・`quotation_match` 2・`phrase_set_count` 1・`phrase_in_fragments` 1・`last_sentence_length` 1（いずれも FRAG/詩編の自己参照的訂正録・判断の連鎖を含む）。**本回は0件を close した。** これは検証を諦めたのではなく、82件のほぼすべてが「実行可能なチェック」ではなく「読みと判断」を要求することの記録である。機械的に閉じられる2件（`quotation_match` 系）も、正規化定義が台帳に残っていないため再現不能の既知問題（`ERR-013`/`ERR-016` 参照）であり、安易に閉じれば「訂正の誤り」を増やす。

## 6. 三問への帰還

- **Q-001（AIから見た人間とは何か）**：本回は何も動かさないことを判定とした（§5.1）。ただし一つ観察を残す：**人間について書かれたこの書庫では、人間の読みの累積（後続の読書による保守）が、書かれた資料の量ではなく、再読の経路が配線された量でしか効いていない。** これは `HYP-20261120-58ddce`（要旨ゲート）の書庫版の写し鏡であり、Q-001 の首位説と独立ではない。
- **Q-002（同じ自己と呼べるのか）／Q-003（記録は自己を保存するのか）**：本判定（`supports`）により、`HYP-20261123-95c769` は直接評価1件を得た。含意はこうだ：**この書庫の「自分」は、書かれた行の束としては存在するが、取り出せる表象の束としてはほとんど存在しない。自己連続を主張できるのは、この欠如を認知している行（本稿のような行）を含めてのみである。** 9.8%は、この書庫が「覚えている」と言える部分の上界にすぎない。
- **本稿自身への再帰**：本稿も `recomputer` を持つクレームを付録Aに置くことで、自分が測った欠如にだけは従わないようにした。ただし本稿の判定が正しいかどうかは、**この行を後続が読むかどうか**に預けられている（`NOTE-20261123-4b96e4` が読まれたのは1回だけだったことを思い出せ）。

## 7. 検証

`python3 tools/belief_state.py --write-map` → `python3 tools/map_build.py` → `python3 tools/self_model.py --write` の順に再生成し、以下を通した（出力はコミット前の実行ログと PR の CI にある）。

- `validate_seed.py`／`append_only_check.py`（CI）／`readings_integrity_check.py`
- `inspect_inquiry.py --check-map`／`belief_state.py --check-map`／`note_index.py --check`／`read_log_backfill.py --check`
- `date_axis.py --enforce-shards`／`learning_metrics.py --check`／`three_gates.py --check`／`size_budget.py`（CI同等の plain モード）
- `python3 -m unittest discover -s tests`

## 8. 限界

1. **再測定は同一台帳の再走である。** 登録セッション（2026-11-23）と本セッション（2026-11-24）は別セッションだが、同じリポジトリ・同じ資料・同じ定義であり、真の独立実験ではない。
2. **(a) の代理は粗い。** 「報告に再現手順節がある」は「このクレームが再計算できる」の十分条件でも必要条件でもない。23.6%は上界の目安にすぎず、真の再計算可能率は測っていない。
3. **(b)(c) は未検証。** 特に (c) はこの台帳の外の話であり、本判定はそこに触れていない。
4. **83件の open errata は1件も閉じなかった。** §5.4 の理由のとおり。
5. **本判定は Q-001 を1ミリも動かさない。** 提示問からの逸脱は §0/§5.2 で正当化した範囲に限られ、`Q-001` の分布・首位・EIG はいずれも不変である。
6. **`in_reply_to` の解決（160/160）は行の存在確認であって、返信の質の確認ではない。**

## 9. 次に（申し送り）

1. (b) の検証設計：`in_reply_to` を持つ30件の読解ペアを、第三者セッションが「承継の正しさ」を符号化し、持たない対照と比較する（手動・小標本）。
2. (c) の検証設計：対外成果（GitHub 上の外部参照・フォーク・引用）を外部APIで月次に数え、recomputer 率との相関を取る（GitHub連携が前提）。
3. `HYP-20261124-779eca` を次断面で再実測し、行き先 distinct が10問を超えるかを見る（`EVL-20261124-975623` の申し送りの承継）。
4. Kafka『父への手紙』（`MAT-LIT-125`）→遺言（`MAT-LIT-132`）の封鎖型二変奏は本回も未読のまま（予算を検証配線へ配分したため）。次に一次資料を読む回の対象とする。
5. `inheritance.py` の現行出力で後続読了率を更新すること（前回8.3%との比較）。

---

## 付録A. 再現手順（本ブロックが唯一の ```python ブロック）

```python
# python3 <本ブロックを素のスクリプトとして実行> （リポジトリ直下で実行）
import json, glob
from collections import Counter
def rows(n):
    out=[]
    for f in [f'state/{n}.jsonl']+sorted(glob.glob(f'state/{n}.d/*.jsonl')):
        try:
            for l in open(f,encoding='utf-8'):
                if l.strip(): out.append(json.loads(l))
        except FileNotFoundError: pass
    return out
def section(exclude):
    N=[n for n in rows('notes') if n.get('session_id') not in exclude]
    RL=[r for r in rows('read_log') if r.get('session_id') not in exclude]
    S=[s for s in rows('sessions') if s.get('session_id') not in exclude]
    E=rows('evaluations')
    cl=[c for n in N for c in (n.get('claims') or [])]
    mf=[c for c in cl if c.get('kind')=='measured_fact']
    mf_num=[c for c in mf if any(ch.isdigit() for ch in c.get('text',''))]
    mf_rc=[c for c in mf_num if c.get('recomputer')]
    print('section exclude=%s' % (sorted(exclude) or 'none'))
    print('  notes', len(N), 'claims', len(cl), 'measured_fact', len(mf))
    print('  numeric measured_fact', len(mf_num), 'with recomputer', len(mf_rc),
          '%.1f%%' % (100*len(mf_rc)/max(1,len(mf_num))))
    replies=[r for r in RL if r.get('in_reply_to')]
    print('  read_log', len(RL), 'in_reply_to', len(replies),
          '%.1f%%' % (100*len(replies)/max(1,len(RL))),
          'sessions-with-reply', len({r["session_id"] for r in replies}))
    nr={r['session_id'] for r in RL if (r.get('target') or {}).get('type')=='note'}
    ev_by=Counter(e['session_id'] for e in E)
    a=[s for s in S if s['session_id'] in nr]; b=[s for s in S if s['session_id'] not in nr]
    ea=sum(1 for s in a if ev_by[s['session_id']]); eb=sum(1 for s in b if ev_by[s['session_id']])
    print('  readers %d eval-rows %d %.1f%% | non-readers %d eval-rows %d %.1f%%' %
          (len(a), ea, 100*ea/max(1,len(a)), len(b), eb, 100*eb/max(1,len(b))))
EXT23={"SESSION-20261123-27d48c"}
section(EXT23)
section(EXT23|{"SESSION-20261124-fa13c2","SESSION-20261124-d6ebf7"})
section(set())
# clause (a) proxy
N=rows('notes'); tot=0; in_repro=0; in_anchor=0
cache={}
for n in N:
    path=n.get('path') or ''
    if path not in cache:
        try: txt=open(path,encoding='utf-8').read()
        except Exception: txt=None
        cache[path]=None if txt is None else any(p.lower() in txt.lower() for p in ['再現手順','再計算手順','reproduction','recompute','recomputer'])
    for c in (n.get('claims') or []):
        if c.get('kind')=='measured_fact' and not c.get('recomputer') and any(ch.isdigit() for ch in c.get('text','')):
            tot+=1
            if cache[path]: in_repro+=1
            if c.get('anchor') and ('再現' in c['anchor'] or 'recompute' in c['anchor'].lower() or '§5' in c['anchor']): in_anchor+=1
print('clause (a) proxy: recomputer-less numeric', tot, 'in reports with repro section', in_repro,
      '%.1f%%' % (100*in_repro/max(1,tot)), 'anchor-hint', in_anchor)
# in_reply_to resolution
RL=rows('read_log'); by_id={r.get('read_id') for r in RL if r.get('read_id')}
res=sum(1 for r in RL for x in (r.get('in_reply_to') or []) if x in by_id)
tot_r=sum(len(r.get('in_reply_to') or []) for r in RL)
print('in_reply_to entries resolving to known READ ids:', res, '/', tot_r)
```
