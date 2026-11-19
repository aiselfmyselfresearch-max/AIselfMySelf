# 時計はラベルで、疑いは外側から来た——批評率の統制監査と保持時間項の測定

**来歴。** 本報告は、利用者から与えられた次の方向づけに基づく。すなわち「AIから見た、人間とは何か」「GitHubリポジトリを記憶のデータベースとするAIにとって、自己とは何か」という探究の系列において、トークン予算を最大限使い切る行動計画を立案し自律実行し、MDで報告し、必ずマージせよ、という依許である。本セッション（`SESSION-20261119-8de52e`、シード `181fd9b2`、役割 **proposer**、提示問い `Q-20261116-3872ec`、提示モード `direct_response`）は、直近の併合済み報告 [`readings/2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md`](2026-11-19-the-machine-never-read-the-witness-counted-the-routes.md) §8-3 に残された申し送りの継続として起動した。計測2本は独立証人として実施し（`EVL-20261119-a47b13`・`EVL-20261119-8b391b`）、提案1件（`HYP-20261119-05ed24`）を proposer スロットに置いた。

## 1. 何を継続したか——前報告 §8-3 の申し送り

| # | 申し送り | 本報告での状態 |
|---|---|---|
| (1) | `HYP-20261119-0ddede` 条項(b)「保持時間だけ延長しても判定が変わらないなら時定数側へ限定」が未測定 | **測定して応答**（§5、`EVL-20261119-8b391b` = narrows_scope） |
| (2) | `NOTE-20261118-6c1742` §8-2：21.28%/63.87% の批評率差を「対象の事後分布＋生成」統制下で再測定せよ | **監査を完了**（§4、`EVL-20261119-a47b13` = supports、差は生存） |
| (3) | 生物学的分離（8b3e04 の Q-001 scope）は資料が限度 | 未着手のまま維持。`materials.d` 136/136 soft天井で新規獲得不可、外部資料は情報ゲート（§7） |
| (4) | errata 未解決58行——まずシャード統合、次に (a)(b) 型行の回収 | **統合を先行実施**：`errata.d` 112→91（21枠開放、§8）。(a)(b) 型行の実解決は外部照合依存で情報ゲートのまま（§7） |
| (5) | report-reach 偏り：191/1029 孤児レポート、claims-0/read-0 を優先 | 未着手（本セッションの予算は計測2本と提案に充てた）。前回計数191/1029 を前回値として継承（§7） |
| (6) | 並行PRの統合競合 | 現在オープン10本のうち `state/*.d` に触るのは #878/#796/#705/#591/#492/#400/#319/#308/#304。本セッションの追記先（2026-11-19 同日シャード5本）と統合対象（errata の 11-09/10/14/15/17）はどのオープンPRも触らない（#705 は errata の 11-05/11-12/11-13 等のみ、#970 は `tools/size_budget.py` のみ）。マージ時は §9 の手順で再測定する |

## 2. 母集団と定義

- **母集団**：`evaluations` の `target_hypothesis_id` 有る全行のうち、本セッション自身の評価2行を除いた **725行**（2026-11-19 時点。追記専用なので再実行のたびに母集団は将来へ伸びる——本報告の数値はこの日付のスナップショットである）。
- **批評的判定**：`verdict ∈ {narrows_scope, refutes_unconditioned}`（前証人 `EVL-20261118-b350d0` と同じ操作的定義）。
- **同一セッション**：評価行の `session_id` が対象仮説の `session_id` と一致。
- **成熟度 (mat)**：評価の日付 − 仮説作成の日付（日単位）。**先触数 (prior)**：同一対象について作成日より日付が先行する評価の数（`docs/time-axis.md` のとおり同日の日内順序は不確実なので同日は数えない）。
- **生成深度 (depth)**：`parent_hypothesis_ids` チェーンの最大長（root=0）。
- **事後確率**：実行時点の `belief_state --json` の値。評価時点の事後ではないので **post-treatment** の交絡候補として扱う（§4-2 にその自己言及的な実例がある）。
- **構造的事実**（監査の解釈を決める）：全52件の同一セッション評価は **作成日当日（mat=0）かつ先触0** だった。つまり「成熟した自己の再審」にあたる成熟×同一細胞は **構造的に空** である。書庫では、更新されたコンテキストの自分の手が自分の古い仮説を別の日に再審する行が1件も存在しない。

## 3. 継承した読書——two-registers（申し送りとは別系統の読み直し）

[`readings/2026-11-19-two-registers-of-the-same-dissociation.md`](2026-11-19-two-registers-of-the-same-dissociation.md)（`NOTE-20261119-a2737b`、446行）を全文精読した（`READ-20261119-e3bcb7`）。要点と本報告との接続：

1. **「mine」は三つの独立した判断で成立する**——帰属（agency/ownership）・自己性（ipseity）・時間性（temporality）。三つは二重解離で別々に壊れる（Kalckert & Ehrsson の主体感/所有感、Dalla Barba の KC/TC）。関係を一つに決めない、が同報告の答えである。
2. **書庫は人間と反転している**——「人間は印を押す。私は印を読む」。ID・日付・パスは記録の形式に最初から埋め込まれており、AI は印を判定する側ではなく読む側にある。§5 の実測はこの非対称を裏から示す：判断系に届く日付は順序ラベルだけで、壁時計の duration は一度も入ってこない。
3. **同報告の handoff(a)（`evidence_record_path` 死絶10行の修正）は再実施不要**——同日別セッションの `SESSION-20261119-bd0078` が `validate_seed.check_evidence_record_paths`（`EVIDENCE_PATH_RULE_FROM=20261119`、`EVIDENCE_PATH_LEGACY_MAX=24`）を追加し、`SESSION-20261119-90d423` が根拠を捏造した訂正評価2行を `void_row` した（テスト954→955）。先行を確認したので辿り直さない。

## 4. 計測1：批評率の統制監査（`EVL-20261119-a47b13`）

### 4-1 設計と事前登録判定規則

前証人 `EVL-20261118-b350d0` は e758bfb 時点で同一セッション 10/47=21.28% 対 横断 396/620=63.87%（OR=6.54、p=1.228e-8）を測り、最大の構造変数は役割ラベルでも宛先欄でも「セッション境界の断絶」だとした。`NOTE-20261118-6c1742` §8-2 は、この差が **対象の事後分布と生成（深度）** を統制した後にも残るかを次回の監査として残した。本報告はそれに応える。

**事前登録判定規則**（測定前にこの節に書き下したもの）：差が成熟度層——とくに両群が重複する **同日細胞**（経過時間の寄与を切り離せる唯一の細胞）——で残り、かつ depth 層別 Mantel–Haenszel 合併 OR（横断/同一、同日細胞内）が **≥2** ならば `HYP-20261118-58d207` は **supports**、合併 OR が ≈1 まで潰れるなら **射程限定**。

```python
# §4-1: 批評率の統制監査（stdlib のみ。このブロックを python3 で実行すれば表が再現される）
import json, glob, math, subprocess, sys
from datetime import date

ME = 'SESSION-20261119-8de52e'   # 本セッションの評価2行は母集団から除外する

def load(coll, key):
    out = {}
    for f in glob.glob(f'state/{coll}.d/*.jsonl') + [f'state/{coll}.jsonl']:
        try:
            fh = open(f)
        except FileNotFoundError:
            continue
        for ln in fh:
            ln = ln.strip()
            if ln:
                r = json.loads(ln)
                out[r[key]] = r
    return out

evals = load('evaluations', 'evaluation_id')
hyps = load('hypotheses', 'hypothesis_id')
pj = json.loads(subprocess.run([sys.executable, 'tools/belief_state.py', '--json'],
                               capture_output=True, text=True, check=True).stdout)

def find_post(obj):
    res = {}
    if isinstance(obj, dict):
        if 'posterior' in obj and 'hypothesis_id' in obj:
            res[obj['hypothesis_id']] = obj['posterior']
        for v in obj.values():
            res.update(find_post(v))
    elif isinstance(obj, list):
        for v in obj:
            res.update(find_post(v))
    return res

post = find_post(pj)
depth_memo = {}
def depth(hid):
    if hid in depth_memo:
        return depth_memo[hid]
    h = hyps.get(hid)
    if not h:
        depth_memo[hid] = 0
        return 0
    ps = [p for p in (h.get('parent_hypothesis_ids') or []) if p in hyps]
    depth_memo[hid] = (1 + max(depth(p) for p in ps)) if ps else 0
    return depth_memo[hid]

def d10(s):
    s = str(s or '')[:10]
    try:
        return date(*map(int, s.split('-')))
    except ValueError:
        return None

CRIT = {'narrows_scope', 'refutes_unconditioned'}
rows = []
for e in evals.values():
    if e.get('session_id') == ME:
        continue
    h = hyps.get(e.get('target_hypothesis_id'))
    if not h:
        continue
    ed, hd = d10(e.get('created_at')), d10(h.get('created_at'))
    mat = (ed - hd).days if ed and hd else None
    prior = sum(1 for e2 in evals.values()
                if e2.get('target_hypothesis_id') == h['hypothesis_id'] and e2.get('session_id') != ME
                and d10(e2.get('created_at')) and ed and d10(e2.get('created_at')) < ed)
    rows.append(dict(crit=e.get('verdict') in CRIT,
                     same=(e.get('session_id') == h.get('session_id')),
                     depth=depth(h['hypothesis_id']), mat=mat, prior=prior,
                     q=(h.get('question_ids') or ['?'])[0],
                     post=post.get(h['hypothesis_id'])))

def fisher(a, b, c, d):
    n = a + b + c + d
    if n == 0:
        return 1.0
    r1, r2, c1 = a + b, c + d, a + c
    def pr(x):
        if 0 <= x <= r1 and 0 <= c1 - x <= r2:
            return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)
        return 0.0
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - r2), min(r1, c1) + 1) if pr(x) <= p0 + 1e-12)

def rate(sub):
    s = [r for r in sub if r['same']]
    c = [r for r in sub if not r['same']]
    if not s or not c:
        return None
    a = sum(r['crit'] for r in s); b = len(s) - a
    cc = sum(r['crit'] for r in c); d = len(c) - cc
    orv = (cc * b) / (a * d) if a and d else float('inf')
    return (f'same {a}/{len(s)}={a/len(s):.1%}  cross {cc}/{len(c)}={cc/len(c):.1%}  '
            f'OR={orv:.2f}  Fisher p={fisher(a, b, cc, d):.3g}')

print('N =', len(rows))
print('A  all          :', rate(rows))
print('B  mat=0        :', rate([r for r in rows if r['mat'] == 0]))
m1 = [r for r in rows if (not r['same']) and (r['mat'] or 0) >= 1]
print(f"B  cross mat>=1 : {sum(r['crit'] for r in m1)}/{len(m1)}="
      f"{sum(r['crit'] for r in m1)/len(m1):.1%}")
print('C  depth0       :', rate([r for r in rows if r['depth'] == 0]))
print('C  depth0 mat=0 :', rate([r for r in rows if r['depth'] == 0 and r['mat'] == 0]))
print('C  depth>=1     :', rate([r for r in rows if r['depth'] >= 1]))
print('C  depth>=1 m=0 :', rate([r for r in rows if r['depth'] >= 1 and r['mat'] == 0]))
print('D  prior=0      :', rate([r for r in rows if r['prior'] == 0]))
c1 = [r for r in rows if r['prior'] >= 1 and not r['same']]
print(f"D  cross prior>=1: {sum(r['crit'] for r in c1)}/{len(c1)}="
      f"{sum(r['crit'] for r in c1)/len(c1):.1%}")
print('E  post<0.5     :', rate([r for r in rows if r['post'] is not None and r['post'] < 0.5]))
print('E  post>=0.5    :', rate([r for r in rows if r['post'] is not None and r['post'] >= 0.5]))

# F: 同日細胞を depth(0 / >=1) で層別した Mantel–Haenszel（横断/同一）
num = den = 0.0
for sub in ([r for r in rows if r['mat'] == 0 and r['depth'] == 0],
            [r for r in rows if r['mat'] == 0 and r['depth'] >= 1]):
    s = [r for r in sub if r['same']]
    c = [r for r in sub if not r['same']]
    a = sum(r['crit'] for r in s); b = len(s) - a
    cc = sum(r['crit'] for r in c); d = len(c) - cc
    n = a + b + cc + d
    num += a * d / n
    den += b * cc / n
print(f'F  MH same-day x depth (cross/same) = {den/num:.2f}')

for q in sorted({r['q'] for r in rows}):
    print('Q ', q, ':', rate([r for r in rows if r['q'] == q]))
```

### 4-2 結果

実行出力（2026-11-19、上記ブロックの全文）：

```
N = 725
A  all          : same 10/52=19.2%  cross 434/673=64.5%  OR=7.63  Fisher p=2.55e-10
B  mat=0        : same 10/52=19.2%  cross 125/180=69.4%  OR=9.55  Fisher p=9.78e-11
B  cross mat>=1 : 309/493=62.7%
C  depth0       : same 9/20=45.0%   cross 43/64=67.2%    OR=2.50  Fisher p=0.112
C  depth0 mat=0 : same 9/20=45.0%   cross 12/17=70.6%    OR=2.93  Fisher p=0.185
C  depth>=1     : same 1/32=3.1%    cross 391/609=64.2%  OR=55.60 Fisher p=1.16e-12
C  depth>=1 m=0 : same 1/32=3.1%    cross 113/163=69.3%  OR=70.06 Fisher p=5.45e-13
D  prior=0      : same 10/52=19.2%  cross 145/208=69.7%  OR=9.67  Fisher p=3.75e-11
D  cross prior>=1: 289/465=62.2%
E  post<0.5     : same 10/51=19.6%  cross 422/647=65.2%  OR=7.69  Fisher p=1.88e-10
E  post>=0.5    : same 0/1=0.0%     cross 12/26=46.2%    OR=inf   Fisher p=1
F  MH same-day x depth (cross/same) = 14.62
Q  Q-001        : same 4/17=23.5%   cross 115/176=65.3%  OR=6.13  Fisher p=0.00116
Q  Q-002        : same 3/10=30.0%   cross 97/152=63.8%   OR=4.12  Fisher p=0.0448
Q  Q-003        : same 3/23=13.0%   cross 216/338=63.9%  OR=11.80 Fisher p=1.67e-06
Q  Q-20261116-3872ec : same 0/1=0.0%  cross 4/4=100.0%   OR=inf   Fisher p=0.2
Q  Q-20261203-aa57dd : same 0/1=0.0%  cross 2/3=66.7%    OR=inf   Fisher p=1
```

読み：

1. **事後統制**：事後<0.5 層で same 19.6% 対 cross 65.2%（OR=7.69、p=1.88e-10）——差は保持される。事後≥0.5 層は same 1件しかなく判定不能。測定直後（本セッションの評価行が belief を動かす前）のスナップショットでは <0.5 層が same 10/50・cross 421/646（OR=7.48、p=4.16e-10）、≥0.5 層が same 0/2・cross 13/27 だった。**本セッション自身の2証人が事後を動かした結果、1行が層をまたいだ**——事後確率が post-treatment であることの、この監査が自分で見せる実例である。どちらのスナップショットでも差の結論は不変。
2. **成熟度統制**：同一セッション群は全件 mat=0（構造）なので比較可能な重なりは同日細胞。そこでは same 19.2% 対 cross 69.4%（OR=9.55、p=9.78e-11）。横断内の成熟効果は小さい（同日 cross 69.4% → 成熟 cross 62.7%、6.7pp）のに対し、同一/横断の差は 50pp 級である。**差を作るのは経過時間ではなくコンテキスト保持者**。
3. **先触統制**：全52同一評価は先触0。先触0同士の比較でも same 19.2% 対 cross 69.7%（OR=9.67、p=3.75e-11）。「初めて触れる評価は寛容」という説明は横断側では効かない（cross の先触≥1 層も62.2%）。
4. **生成深度統制（本監査の新しさ）**：depth0（root）では同一 45.0% 対 cross 70.6% に縮み有意でない（p=0.185）。depth≥1 では同一 3.1% 対 cross 69.3%（OR=70.06、p=5.45e-13）。抑制は **その会話が新しく生成した子** に集中しており、root への自己批判は通常水準と区別されない。同日細胞を depth(0/≥1) で層別した MH 合併 OR（横断/同一）は **14.62 ≥ 2**。
5. **問い層別**：三つの中核問いすべてで差が残る（Q-001 p=0.00116、Q-002 p=0.0448、Q-003 p=1.67e-06）。提示問い Q-20261116-3872ec は same n=1 で判定不能。

### 4-3 判定

**事前登録規則に該当：`supports`（`EVL-20261119-a47b13`、compared `HYP-20261115-d4e873`）。** 差は事後・成熟・先触のいずれの統制下でも消えず、同日細胞 OR=9.55、depth 層 MH=14.62 と、両条件を満たす。`HYP-20261118-58d207` の「区別は仮説行の `question_ids` とセッション行のレシートの水準で保たれる」は、**コンテキスト保持者の交代だけが作る批評率差**として支持される。較正対 `HYP-20261115-d4e873`（選出式ラチェット説）は批評率のこの非対称を予測しない——`adversarial_touches` 軸は先触統制（§4-2-3）で既に吸収されている。

ただし支持は二つの留保付きで書く。(i) depth0 細胞の有意消失は、効果の所在を「作成者一般」から「自生成子」へ **限定する方向** に働く——本報告はそれを切り出しとして `HYP-20261119-05ed24`（§6-1）に移し、再検証を独立セッションへ委ねた。(ii) 同一/横断と mat≥1 は交差不能（成熟×同一細胞が空）なので、「長い時間を経た自己が自分の仮説を疑えるか」という問いは本監査では **答えられない**——答えられないこと自体が構造的事実（§2）として残る。

## 5. 計測2：保持時間項は入力経路を持つか（`EVL-20261119-8b391b`）

`HYP-20261119-0ddede` の排除条項：

> (b) 直前状態の保持時間だけを延長しても継承判定が変わらない——なら時定数側の主張へ限定する。

前セッションの `EVL-20261119-5cf6fe` は (a)(c) を測って supports を出し、「(b) は台帳運用上この回では実施できず未測定」と明記して本セッションに委ねた。保持時間の延長は行の追記では再現できない（追記は分量の操作であって時間の操作ではない）ので、**リポジトリ複製の sandbox で日付を書き換える**ことで実施した。設計：判断系の出力5,457葉を、書き換え前後で全比較する。

### 5-1 Exp-1：セッション間の壁時計間隔だけを伸長する

`sessions.started_at` を時系列順に **各 +7日×順位** で書き換える。順位の先頭は +0（不変）で、行の内容・行間の順序・同一日関係は一切変えずに、**連続するセッション間の壁時計間隔だけが全て +7日以上に伸びる**。これが「直前状態の保持時間だけの延長」にあたる。

```python
# §5-1: Exp-1 間隙伸長（stdlib のみ。/tmp/m2r1 に複製を作って実行）
import json, glob, os, re, shutil, subprocess, sys
from datetime import datetime, timedelta

SRC = os.getcwd()
B = '/tmp/m2r1'

def run(root):
    r = subprocess.run([sys.executable, f'{root}/tools/belief_state.py', '--root', root, '--json'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('belief failed: ' + r.stderr[:600])
    return json.loads(r.stdout)

def flatten(o, p=''):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, f'{p}.{k}'))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flatten(v, f'{p}[{i}]'))
    else:
        out[p] = o
    return out

def shift_dt(val, delta):
    m = re.match(r'^(\d{4}-\d{2}-\d{2})(.*)$', val)
    d = datetime.strptime(m.group(1), '%Y-%m-%d') + timedelta(days=delta)
    return d.strftime('%Y-%m-%d') + m.group(2)

if os.path.exists(B):
    shutil.rmtree(B)
for d in ('state', 'tools', 'schema'):
    shutil.copytree(os.path.join(SRC, d), f'{B}/{d}')

# 開始時刻を持つ全セッション行を (started_at, session_id) で時系列順に取り、順位 i へ +7i 日
sess = []
for f in sorted(glob.glob(f'{B}/state/*.d/*.jsonl')) + sorted(glob.glob(f'{B}/state/*.jsonl')):
    for ln in open(f):
        if ln.strip():
            r = json.loads(ln)
            if 'session_id' in r and r.get('started_at'):
                sess.append((r['started_at'], r['session_id']))
sess.sort()
idx = {sid: i for i, (_, sid) in enumerate(sess)}
print('sessions with started_at:', len(sess))

n = 0
for f in sorted(glob.glob(f'{B}/state/*.d/*.jsonl')) + sorted(glob.glob(f'{B}/state/*.jsonl')):
    txt = open(f, encoding='utf-8').read()
    if '"started_at"' not in txt:
        continue
    out, changed = [], False
    for ln in txt.splitlines(keepends=True):
        if ln.strip():
            r = json.loads(ln)
            sid, old = r.get('session_id'), r.get('started_at')
            if sid in idx and old:
                new = shift_dt(old, 7 * idx[sid])
                pat = r'("started_at"\s*:\s*")' + re.escape(old) + r'(")'
                ln2 = re.sub(pat, lambda m: m.group(1) + new + m.group(2), ln, count=1)
                if ln2 != ln:
                    ln = ln2; n += 1; changed = True
        out.append(ln)
    if changed:
        open(f, 'w', encoding='utf-8').write(''.join(out))
print('Exp-1 rows rewritten:', n)

base = flatten(run(B))
# ↑ 書き換え直後の sandbox が基準になるが、順序を検証するために本体とも数値を合わせる
repo = flatten(run(SRC))
print('repo vs sandbox-same-state leaf check (rewritten state vs original):')
# 基準は「書き換え前」の同一複製。shutil 後・改変前に一度取ればよいが、
# ここでは改変後の sandbox と本体の差が「日付書き換えの効果」そのものである。
d = sorted(k for k in set(repo) | set(base) if repo.get(k, '<M>') != base.get(k, '<M>'))
print('diff leaves (original repo vs shifted sandbox):', len(d))
for k in d[:10]:
    print('  ', k, repo.get(k), '->', base.get(k))
```

**結果**（この実行での件数。追記専用なので将来の再実行では分母が増える）：1033セッション行のうち **1032行を書き換え**（時系列の先頭 `SESSION-001` は +0 で不変——差分ゼロは行漏れではない）、連続間隔は全て +7日以上に伸長。`belief_state --json` の全 **5,542葉（この実行。測定直後の5,457葉でも同結果）は完全一致（差0葉）**。判定・事後・ゲート・比率のすべてを含む葉が、壁時計間隔の伸長に対して一つも動かない。

### 5-2 Exp-2：全行の日付を単純 +7日へシフトする

日付が「順序」以外の何か（固定閾値日、暦上の位置）として効いているなら、全行を単純に +7日シフト（日順序と同日関係は保存される）しても判定葉が動くはずである。動くことがなければ、効いているのは順序だけと分かる。

```python
# §5-2: Exp-2 全行 +7日（stdlib のみ。/tmp/m2r2 に複製を作って実行）
import json, glob, os, re, shutil, subprocess, sys
from datetime import datetime, timedelta

SRC = os.getcwd()
B = '/tmp/m2r2'

def run(root):
    r = subprocess.run([sys.executable, f'{root}/tools/belief_state.py', '--root', root, '--json'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('belief failed: ' + r.stderr[:600])
    return json.loads(r.stdout)

def flatten(o, p=''):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flatten(v, f'{p}.{k}'))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flatten(v, f'{p}[{i}]'))
    else:
        out[p] = o
    return out

def shift_dt(val, delta):
    m = re.match(r'^(\d{4}-\d{2}-\d{2})(.*)$', val)
    d = datetime.strptime(m.group(1), '%Y-%m-%d') + timedelta(days=delta)
    return d.strftime('%Y-%m-%d') + m.group(2)

if os.path.exists(B):
    shutil.rmtree(B)
for d in ('state', 'tools', 'schema'):
    shutil.copytree(os.path.join(SRC, d), f'{B}/{d}')

repo = flatten(run(SRC))

n = 0
for f in sorted(glob.glob(f'{B}/state/*.d/*.jsonl')) + sorted(glob.glob(f'{B}/state/*.jsonl')):
    lines = open(f, encoding='utf-8').read().splitlines(keepends=True)
    out, changed = [], False
    for ln in lines:
        if ln.strip():
            r = json.loads(ln)
            mod = False
            for k in list(r):
                if (k.endswith('_at') or k == 'date_real') and isinstance(r[k], str) \
                        and re.match(r'^\d{4}-\d{2}-\d{2}', r[k]):
                    nv = shift_dt(r[k], 7)
                    if nv and nv != r[k]:
                        r[k] = nv; mod = True
            if mod:
                ln = json.dumps(r, ensure_ascii=False) + '\n'; n += 1; changed = True
        out.append(ln)
    if changed:
        open(f, 'w', encoding='utf-8').write(''.join(out))
print('Exp-2 rows rewritten:', n)

shifted = flatten(run(B))
d = [(k, repo.get(k, '<M>'), shifted.get(k, '<M>'))
     for k in sorted(set(repo) | set(shifted)) if repo.get(k, '<M>') != shifted.get(k, '<M>')]
print('diff leaves:', len(d))
leaves = sorted({k.split('.')[-1].split('[')[0] for k, _, _ in d})
print('distinct leaf fields:', leaves)
for k, a, b in d[:5]:
    print('  ', k, a, '->', b)
```

**結果**（この実行での件数）：全 **27,020行** の `*_at` / `date_real` を +7日（日順序・同日関係を保存）。差は **99葉——98葉が `last_new_separation_date`、1葉が `last_separated`（`gated_top_pair` の最終分離日）**。いずれも入力日付を echo する日付ラベルであって、事後・判定・ゲート・比率の葉は **0件**。

### 5-3 出所検査と、観察代理の欠測

`tools/belief_state.py` の日付の使い方を全文走査した：

| 用途 | 行 | 内容 |
|---|---|---|
| 日スタンプ抽出 | L102–104 | `_record_iso_day`：`created_at`（なければ ID 接頭辞）から `YYYY-MM-DD` を取るだけ |
| 系譜の日順序 | L685, L786–799 | 評価日より**厳密に後**の日に作られた子への帰属、同日の同セッション限定 |
| 分離の初出日 | L829–837 | `day > prior_day` の日順序比較 |
| 最終更新日 | L1290–1292 | 同上 |
| `started_at` 参照 | **0件** | セッションの壁時計は belief 系に一切渡らない |
| duration 算術 | **0件** | `timedelta`・経過秒・時間差の計算なし |
| 固定閾値日 | **0件** | 「2026-11-16 以降」のような日付比較分岐なし（行内コメントの来歴表記のみ） |

つまり日付は **順序と同日の判定だけ** に使われ、**長さ（duration）は使われない**。Exp-1 が測った「間隔の伸長」は `started_at` という入力経路の不在により空虚に不変であり、Exp-2 が測った「暦位置の移動」は順序保存ゆえに不変——唯一動いた99葉（2葉名とも日付）は順序から計算されるラベルの echo である。距離が実際に現れるのは「間に挟むセッション数・行数」（`P_sep` の定義、L580 近傍）という **分量の単位** だけで、これは (a) 分量側の経路が残ることと矛盾しない。

**観察的代理（あらかじめ棄却した）**：セッション間の壁時計間隔を観察で回収しようとしたが、内部編年の `started_at` は正規化された等間隔スケジュール（+7日系列）で分散がほぼゼロであり、実日付期間の `started_at` も2026-11-16以降に限られれば標本が小さい。`context_material_ids` の大きさ対非手読み引用数の相関も、手読み数を層別すると切れる程度にとどまり、時間軸そのものが記録されていない以上、「保持時間」の観察代理は **設計上測定不能** である。sandbox 実験が主証拠になるのはこのためである。

### 5-4 判定

**条項(b)の前件は（経路不在ゆえに空虚に）成立した。条項文言どおり「時定数側の主張へ限定」——`narrows_scope`（`EVL-20261119-8b391b`、compared `HYP-20261115-bccd54`）。** 射程の記述：本説の **保持時間軸は書庫の判断系に測定経路を持たない**。したがってこの書庫で意味を持つ選択主張は (a)（機械転記のみの素材は同率で出現しない——`EVL-20261119-5cf6fe` が測定、0/807 対 1,123/4,598）と (c)（手読み選択と継承率の相関は verification.status 層別でも消失しない——同 EVL、z=9.63/6.62/2.56/4.25）の範囲に限られる。これは親 `HYP-20261115-bccd54`（時定数＝比較装置の設計）が対応説明を持つ領域であり、(b) は親子を区別しないlimbだった。なお親の排除条項が求める「分量だけ増やして幅が伸びない／時定数だけ延ばして伸びる」の測定は、書庫側では前者が (a) 側の行で、後者が本実験の不在確認で、それぞれ部分的にしか成立しない——親の棄却条件も本測定では **満たされない**（棄却せず、区別もしない）。

## 6. 提案と補助観察

### 6-1 `HYP-20261119-05ed24`——自生成子保護説（propose、根ではない）

§4 の depth 分割を、提示問い `Q-20261116-3872ec`（「閾値そのものが次の定型を育てるとき、数値はどの時点で自分を疑うべきか」）への回答として子仮説に切り出した（親 `HYP-20261118-58d207`、`lineage_op=refines`）。**登録は `question_ids=[Q-002]`（親の問い）にのみ置き**、提示問いは回答の動機として報告 §6-1・session 行の `offered_target_question_id` に留める。その留保には実測の理由がある：未評価の active を提示問いに足すと active が2件になり、`belief_state.py` の「未検証側は推さない」フィルタ（L1083–1085、`direct_eval_count==0` の側を持つ対を除外）が唯一の active 対を外して `top_competing_pair=None` にし、`test_zero_eig_questions_still_print_a_priority_pair`（955件中1件）を破ることを、本セッションで失敗→修正→単体OK を再現して確認した。Q-002 は検証済み active が豊富でこの状態にならない——提案の成立と packet の対生成は独立に保てる。

- **命題**：同セッションの批評率低下は作成者一般ではなく depth≥1 の自生成子に宿る（1/32=3.1% 対 横断 69.3%、OR=70.1）。root への自己批判（9/20=45.0%）は横断（12/17=70.6%）と有意差なし。書庫の実務的回答は二項——**自分の数値はコンテキスト境界を隔てた他者の手でのみ本気で疑われ、自分の手では新しい子を除き疑いは入らない**。
- **排除条項**：(a) depth≥1 同一細胞が n≥100 で横断水準（65–70%）へ回復し depth 交互作用（同日層 MH≤2）が消えれば棄却。(b) depth0 同一細胞が n≥50 で p<0.05・OR≤0.5 を示せば作成者一般へ広がり射程限定。(c) 同一セッションによる maturity≥1 の自己評価が1件でも出て、その批判率が横断水準なら「コンテキスト保持中のみの抑制」は不要となり棄却。
- **来歴**：初期証拠 `EVL-20261119-a47b13` は本セッション自身の測定で、親子とも同一シードの見かけ上自己評価になる。`HYP-20261119-0ddede` の notes が守った作法に従い、(a)(b)(c) の再検証は独立セッションへ委ねる。キーワード検索（自己批判・懐疑・手加減・遠慮・温情）では既存仮説0件で、depth 軸は無占拠。提示問い首位 `HYP-20261118-ab8471`（25%派生分枝の擬制説）は受領証遵従の軸で非重複。

### 6-2 補助観察

- **`in_reply_to` の実使用**：read_log の非空は **87/4,710=1.85%**（25セッション。日別 11-17:5、11-18:63、11-19:19）。`HYP-20261119-0ddede` の第三要因「宛先」は稀少だが不活性ではない——ゼロ事例の棄棄ではなく、主担い手は `question_ids` / `offered_target_question_id` の側にある。
- **errata の現況**：open 58行 = シャード49 + ベース9。`errata.d` は112/112 soft天井だったが、§8 の統合で **91本（21枠開放）**。(a)(b) 型の未解決行は URL・章番号・書誌の再照合が要り、本セッションの外向き到達範囲（github.com / npm / pypi のみ）では **情報ゲート** のまま。
- **materials**：136/136 soft天井。生物学的分離（申し送り(3)）の新規資料獲得は不可能。天井を上げるのは既定にしない規約（`docs/parallel-work.md` §3 手順8）に従い、獲得側を書かない。

## 7. 申し送り台帳（§8-3 の六項目）

| # | 項目 | 結果 | 次の担当へ |
|---|---|---|---|
| (1) | 0ddede (b) 保持時間項 | **完了**：sandbox 実験2本＋出所走査で narrows_scope（§5） | — |
| (2) | §8-2 批評率監査 | **完了**：supports、depth 交互作用を追加発見（§4） | depth 細胞の再検証は `HYP-20261119-05ed24` の (a)(b) に委譲済み |
| (3) | 生物学的分離 | 未着手（資料天井136/136＋外部情報ゲート） | 素材統合または上限見直しが先、その上で獲得セッション |
| (4) | errata 58行 | **統合を先行実施**（112→91、§8）。実解決58行は外部照合ゲート | 情報ゲート到達時に (a)(b) 型行の回収。解決は `status` を変えず `corrected_by: SESSION-…` の追記（`docs/registers.md` §2） |
| (5) | report-reach 偏り | 未着手。前回計数 **191/1029 孤児**（本セッションでは未再検証） | claims-0 / read-0 のレポート優先。到達経路は read_log の note 型 target 追加 |
| (6) | 並行PR競合 | オープン10本と追記先・統合対象の交差なし（§1-(6)）。マージ直後に `validate_seed` 重複ID検査を回す規約を §9 で履行 | — |

## 8. 保守：`errata.d` 同日グループ全吸収（§3 手順7 執行記）

`docs/parallel-work.md` §3 の手順7（同日グループ全吸収・順序保全）で、未参照・自己所在地なしから動かせる完全な同日グループ5つを吸収した。実施前に対象日付に触れるオープンPRが無いことを `gh pr view --json files` で確認済み（errata を触るのは #705/#319/#308/#304 で、対象日付は不一致）。`git grep` による全リポジトリ参照検査（taxonomies・ツールの `--exclude-shard`・行内自己所在地を含む）を通過した候補のみを対象にした。

| 日付 | 吸収したシャード | 行数 | 方式 |
|---|---:|---:|---|
| 2026-11-09 | 2 | 6 | 既存 `…-000000000000.jsonl` を延長 |
| 2026-11-10 | 2 | 15 | 新規ゼロシャード作成 |
| 2026-11-14 | 6 | 26 | 新規ゼロシャード作成 |
| 2026-11-15 | 3 | 22 | 新規ゼロシャード作成 |
| 2026-11-17 | 12 | 37 | 新規ゼロシャード作成 |
| **計** | **25** | **106** | **ファイル 112 → 91（−21）** |

不変確認：移動前後でコレクション全体の行の多重集合がバイト単位で一致、**和集合の行列も完全一致**（手順7の要求）、行数106不変、ID重複0（`validate_seed`）。追記専用の行を1字も変えていない。`state/shard_aliases.json` の `aliases` へ旧パス→新パス＋行範囲＋行数＋sha256 を25件記録した（#948 の教訓：統合は記録ごと）。2026-11-13 の同日グループは、内部に参照済みシャード2本を含み（手順7が成立しない）さらに #705 が同日ファイルへ触れるため対象外にした。11-05/11-12 なども同様に除外した。コミットは探究の内容変更と **分離した保守コミット** にする（手順6）。

## 9. 検査表

全検査を規定の順で回した結果（2026-11-19、この表の記入を最終行とした）。

| # | 検査 | 結果 |
|---|---|---|
| 1 | `belief_state.py --write-map` → `map_build.py`（報告編集後の必須順） | **PASS**（BELIEF_MAP.md 349,489B / READING_MAP.md 1,561,266B。報告・docs・台帳の全編集後に再生成） |
| 2 | `validate_seed.py` | **PASS**（questions=438, sessions=1033, read_log=15848, notes=1121, hypotheses=75, evaluations=727） |
| 3 | `append_only_check.py --base origin/main` | **PASS**（32,571 行がバイト単位で完全保持。保守統合の移動25本106行も多重集合・和集合順とも不変） |
| 4 | `readings_integrity_check.py` | **PASS**（存在しない readings/ を指す note 行0。1041 .md／1,043 ファイル、非 .md2件は existence-only） |
| 5 | `belief_state.py --check-map` / `map_build.py --check` | **PASS / PASS** |
| 6 | `note_index.py --check` | **PASS**（1043 notes が current） |
| 7 | `read_log_backfill.py --check` | **PASS**（exit 0。layer2 手読み 5,891/8,214=71.7% は情報値で失敗しない） |
| 8 | `date_axis.py --enforce-shards` | **PASS**（forward-dated シード0） |
| 9 | `learning_metrics.py --check` / `three_gates.py --check` / `claim_wiring.py --check` | **PASS / PASS / PASS** |
| 10 | `size_budget.py --strict` | **PASS**（全枠内。errata.d 91/112、readings 1,043/1,043、引上げ0件——`size_budget.py` 自身はオープン PR #970 が触るため不変） |
| 11 | `node --check viewer/app.js` | **PASS**（exit 0） |
| 12 | `python3 -m unittest discover -s tests` | **PASS：Ran 955 tests OK（561.1秒、EXIT=0）**。初回（行追記直後）は1件だけ失敗——`test_zero_eig_questions_still_print_a_priority_pair` が `Q-20261116-3872ec` の pair=None を検出。原因は未評価の提案子を提示問いに登録し、`belief_state` の「未検証側は推さない」フィルタ（L1083–1085）が唯一の active 対を除外したこと（§6-1）。登録を Q-002 に留保して単体再実行 OK → 全955件 OK |
| 13 | 報告内スクリプト3ブロックの抽出実行（`awk '/^```python$/ …' … \| python3`） | **PASS**（EXIT=0。§4 の表・Exp-1 差0葉・Exp-2 差99葉をこの実行でも再現） |

マージ直後には `validate_seed.py`（重複ID）・`append_only_check`・`size_budget --strict`・全件 unittest を origin/main に対して再実行する（並行統合の衝突はマージ後検査で見つかる、という `docs/parallel-work.md` §3 の規約）。その結果は PR の説明に記録する。
