# main ブランチ保護の現状照合と、main_guard を「毎日の赤い警告」から「ポリシー適合のドリフト検知」へ改修する設計

- 作成日: 2026-11-28（UTC）
- 対象: `tools/main_guard.py`、`.github/workflows/main-guard.yml`、周辺テスト
- 状態: 設計は当日のうちに実装され、PR として main へマージされる（本文書の第 5 節に実装一覧、第 6 節に検証結果）
- 前提文書: `docs/2026-11-20-evidence-accounting-change.md` 第 5 部追記・第 6 部（main 保護の確認）

> 本稿は「赤いマージをどう防ぐか」という動作を変える提案ではなく、**2026-11-21 に利用者が
> 設定したブランチ保護を、リポジトリ内の記述とガードがまだ旧状態として描き続けている**という
> 記述の陳腐化を直し、併せてガードが真に検証すべき対象（ポリシー適合）を明示する設計である。
> 台帳・スキーマ・ゲートの意味は一切変更しない。

---

## 0. 結論（先に要点）

1. 指摘の「`main_guard.py --strict` が毎日赤い（＝直せていない）」は、**2026-11-21 以降、事実と食い違っている**。保護設定は 2026-11-21 に利用者によって適用済みであり、直近 100 回の main-guard 実行（取得窓 2026-11-23T19:35Z 以降）は **100/100 すべて success**、本日（2026-11-28）の手元実測でも `--strict` は exit 0 である。
2. しかし `.github/workflows/main-guard.yml` の冒頭コメントは今も「main は required check が通っていないマージを受け入れる（＝未修正である）」と主張し、`main_guard.py` の OK 出力も「context 一覧を読む権限がこのトークンには無い」と主張する。**どちらも現在は偽である**。警報が常態化して読まれなくなる失敗は、このリポジトリが 2026-11-21 の waiver 移設で明示的に避けようとしたものと同型なので、文言の陳腐化は機能欠陥として扱う。
3. ガードの検証対象は `protected` の真偽だけである。required check が外れたり `enforcement_level` が弱まっても緑のままであり、**「protected: true でも required check が弱い」という指摘の方向への退化を検知できない**。
4. 「required check が `validate` 1 本のみ」であることは偶然ではなく**判断**であるが、その理由（数値・根拠）がどこにも文書化されていない。本稿で明示し、ガードはこの姿勢をポリシーとして検証する。
5. したがって本設計は `main_guard.py` を「`protected` の真偽チェッカー」から「**ポリシー適合チェッカー（ドリフト検知器）**」へ改める。ワークフローのコメントは現実を描くように書き直す。

---

## 1. 指摘の内容

外部からの指摘（2026-11-28 に利用者経由で伝えられた、別の AI による点検）は次の通りである。

> main が `protected: true` でも required check は `validate` 1 本のみで、
> `.github/workflows/main-guard.yml` のコメントが「main は required check が通っていない
> マージを受け入れる」と明記し、`main_guard.py --strict` で毎日赤くして警告している
> （＝直せていない）。

この指摘は 3 つの主張に分解できる。

| # | 主張 | 実測（2026-11-28） | 判定 |
| :-- | :--- | :--- | :--- |
| A | required check は `validate` 1 本のみである | `GET /branches/main` → `contexts: ["validate"]`、`checks: [{app_id: 15368, context: "validate"}]` | **事実**。ただし理由の文書化が無い（第 4.5 節で対処） |
| B | main-guard.yml のコメントが「赤いマージを受け入れる」と明記している | コメント本文は確認できる。ただしその主張自体が 2026-11-21 以降は陳腐化している | **文言は現存、内容は陳腐化**（第 4.6 節で対処） |
| C | `main_guard.py --strict` が毎日赤く、警告し続けている（＝直せていない） | 本日の手元実測で exit 0（OK）。直近 100 実行はすべて success。定期実行（3 時間前）も success | **陳腐化**。2026-11-21 に解消済み（第 2 節） |

つまり指摘は「原因は repository configuration であり、リポジトリ内のファイルでは閉じられない」という 2026-11-21 時点の状態を、その後の設定変更を知らずに描写したものと読める。**指摘は当時は正しかったが、いまは古い。古くなった指摘をリポジトリ自身の記述が再生産し続けていること**が、今回の真の修正対象である。

---

## 2. 実測による照合（2026-11-28）

### 2.1 保護設定の現値

```
$ gh api repos/aiselfmyselfresearch-max/AIselfMySelf/branches/main
{
  "protected": true,
  "protection": {
    "enabled": true,
    "required_status_checks": {
      "enforcement_level": "everyone",
      "contexts": ["validate"],
      "checks": [{"context": "validate", "app_id": 15368}]
    }
  }
}
```

- `protected: true`。required check は `validate`（GitHub Actions, app_id 15368）1 本。
- `enforcement_level: "everyone"` — **管理者（リポジトリオーナー）も例外ではない**。
- `GET /branches/main/protection`（詳細設定の専用エンドポイント）は本日も **403**（"Resource not accessible by integration"）。2026-11-21 の測定（`docs/2026-11-20-evidence-accounting-change.md` 第 6 部）と同じで、書き込み権限（administration）はこのサンドボックスのトークンには無い。
- 一方、`GET /branches/main` の応答に含まれる `protection` オブジェクトからは、required context と enforcement level が**読み取れる**。v1 の OK 出力が「context 一覧は読めない」と述べていたのは、この読み取り経路を見落としていたものなので、訂正する。

### 2.2 保護が入った時点

`docs/2026-11-20-evidence-accounting-change.md` 第 6 部（2026-11-21）に「**利用者の設定変更後**、`protected=true`、`contexts=["validate"]`、`enforcement_level="everyone"` が返った。`tools/main_guard.py` も exit 0」との実測記録がある。つまり:

- 2026-11-20/21 の 3 件の赤いマージ（#998、#1002、およびその後のマージ）の原因は「main が required check 未通過のマージを受け入れる」ことにあり、
- その原因は **2026-11-21 に利用者によるリポジトリ設定で閉じられた**。リポジトリ内のファイル（トークン権限 403）では閉じられなかった通り、閉じたのはファイルではなく設定である。

### 2.3 ガードの実行履歴

```
$ gh run list --workflow=main-guard --limit 100   # conclusion を集計
total runs fetched: 100（窓の始まり: 2026-11-23T19:35:23Z）
non-success runs: 0
current consecutive success streak: 100
```

「毎日赤くしている」状態は少なくとも 2026-11-23T19:35Z 以降存在せず、日次の schedule 実行も success である。

### 2.4 enforcement_level が「everyone」でなければ何が起きるか

本リポジトリのマージはすべて `aiselfmyselfresearch-max`（リポジトリオーナー、すなわち管理者）によって行われている（#998 も #1171 も `mergedBy: aiselfmyselfresearch-max`）。したがって:

- `enforcement_level` が `non_admins` や `off` に弱まった場合、**管理者に例外が生じ、このリポジトリで唯一マージを行う主体が必須チェックの強制から外れる**。required check は名目上存在し続けるが、実効性は失われる。2026-11-20/21 の赤いマージと同じ事態が、`protected: true` のまま再現する。
- これはまさに「protected: true でも required check が弱い」という指摘の方向であり、現行ガード（`protected` の真偽のみ）では検知できない。**v2 が enforcement_level を検証対象に加える理由である。**

---

## 3. 問題の再定義 — 何が今も真の未解決か

| # | 問題 | 性質 | 本設計での扱い |
| :-- | :--- | :--- | :--- |
| P1 | workflow コメントとツール出力が「未修正である」ことを主張し続ける | 記述の陳腐化。警報の常態化は「読まれなくなる」という、このリポジトリが繰り返し学んだ失敗と同型 | 実装する（第 4.3・4.6 節） |
| P2 | ガードが `protected` の真偽しか検証しない。context の欠落・enforcement の弱体化は検知できない | 検知網の穴 | 実装する（第 4.1〜4.2 節） |
| P3 | 「required check が `validate` 1 本のみ」が**判断**として文書化されていない | 文書化の欠落。穴ではなく判断だが、判断の記録が無いため穴として指摘され続ける | 文書化する（第 4.5 節）。tests を必須にする変更は**しない** |
| P4 | waiver（ERR-20261121-23edfe など）の解除条件「main に必須チェックが入る」は達成済みだが、解除は行われていない | 台帳上の債務。解除は行の書き換えを伴わない注記で可能だが、ゲート復活の副作用の分析が必要 | **実装しない**。分析と安全な手順のみ記録する（第 4.8 節） |

---

## 4. 設計

### 4.1 ポリシーの明示（`tools/main_guard.py` 内の `POLICY`）

ガードは次のポリシー定数をソースコード内に持ち、`GET /branches/main` の実測値と照合する。

```python
POLICY = {
    # マージゲートとして必須とする context。理由は docs/2026-11-28-main-guard-policy-conformance.md 4.5 節。
    "required_contexts": ("validate",),
    # 管理者も例外としない。このリポジトリのマージはすべてオーナーが行うため、
    # 管理者免除は「唯一のマージ主体の免除」に等しい（本稿 2.4 節）。
    "enforcement_level": "everyone",
}
```

### 4.2 判定表（OK / FAIL / UNKNOWN）

`GET /repos/{owner}/{repo}/branches/main` の応答に対して、次の順に判定する。

| 条件 | 判定 | 終了コード | 出力 |
| :--- | :--- | :--- | :--- |
| API 到達不能・応答不正 | UNKNOWN | 2 | 「見えないときに健康と報告しない」旨と detail |
| `protected` が真でない | FAIL | 1 | 赤いマージが着地し得る旨と修正コマンド |
| `protected` は真だが `protection` オブジェクトが無い | UNKNOWN | 2 | 必須 context を検証できず、健康とも不健康とも言えない |
| required context に `validate` が無い | FAIL | 1 | 実測の context 一覧と修正コマンド |
| `enforcement_level` が `everyone` 以外（`non_admins` / `off` / 不明） | FAIL | 1 | 実測値と、管理者免除＝唯一のマージ主体の免除である旨 |
| 追加の required context が在る | OK（注記付き） | 0 | ポリシーより厳しいことと、第 4.5 節への参照 |
| 上記すべて適合 | OK | 0 | 実測値（context・enforcement）をそのまま列挙 |

- v1 からの変更点の核心は、`protected: true` を OK としないことである。**ポリシー適合が確認できたときだけ OK** とする。
- v1 の OK 出力にあった「context 一覧を読む権限がこのトークンには無い」という注記は、2.1 節の実測（読める）に反するため削除する。読めないときは OK ではなく UNKNOWN として扱う。
- 終了コードの意味（0 適合 / 1 不適合 / 2 不明）は v1 から変わらない。`--strict` は v1 では実質 no-op であり、v2 でも両モードとも同じ強制を行うため、フラグは互換性のために受け付け続ける。

### 4.3 出力と `FIX_COMMAND` の更新

- 人間向け出力は v1 の `OK:` / `FAIL:` / `UNKNOWN:` 接頭辞を保ち、実測値（contexts、enforcement_level）を列挙する。
- `--json` を追加する。`{"verdict", "repo", "branch", "protected", "required_contexts"(実測), "enforcement_level"(実測), "policy", "checks"}` を出力し、他のツールや日次ログの集計から読めるようにする。
- `--command` の `FIX_COMMAND` は、現行の適用済み姿勢（第 2.1 節）を再現する形に更新する。v1 は `enforce_admins: false` を提案していたが、実際に適用されたのは `enforcement_level: everyone`（すなわち `enforce_admins: true`）である。**修正コマンドは現在の姿勢を再現しなければならない**ので、次のようにする:

```
gh api -X PUT repos/{owner}/{repo}/branches/main/protection --input - <<'JSON'
{"required_status_checks":{"strict":false,"contexts":["validate"]},"enforce_admins":true,"required_pull_request_reviews":null,"restrictions":null,"allow_force_pushes":false,"allow_deletions":false}
JSON
```

  - `strict: false`（ヘッドが base に追いついていなくても、必須 check が緑ならマージを許す）は現行運用に合わせて維持する。高頻度でマージが行われるこの保管庫で `strict: true` にすると、全ての PR が直前の main 再ベースを強制され、追従コストがマージの利益を上回る。
  - このコマンドは 403 のトークンでは実行できない。実行者は管理権限を持つ利用者である（第 4.9 節）。

### 4.4 なぜ main-guard を required check にしないか（自己言及の限界）

main-guard の検知対象は「必須チェックの強制そのものが消えること」である。仮に main-guard を required check にしたとしても、**強制が消えた時点で required check の強制も同時に消える**ため、赤い main-guard は何も止められない。required check の追加はこの失敗モードに対して何の保護も加えない。ガードの唯一の強制力は**読まれること**であり、したがって日次で走り、姿勢が崩れた日だけ赤くなり、修正コマンドを印字する、という現在の形が正しい。内容のゲート（`validate`、必須のまま）が台帳を守り、main-guard はゲートの守られ方を見張る、という二層にする。

### 4.5 「required check が `validate` 1 本のみ」の判断と根拠（P3）

`tests`（回帰スイート 1,125 件超・5 shard・CI 実測 約 432〜708 秒、`docs/2026-11-23-test-suite-runtime-analysis.md`）を required にしない判断とその根拠:

1. **2026-11-20/21 の事故の原因は `validate` の赤であった**。#998 の session 行、#1002 の register 無しの 2 問い——いずれも `validate_seed` が赤のまま着地した。回帰テストの赤が事故を起こした記録はない。必須化は事故の実在する経路から順に施す。
2. **`validate` はマージゲートとして十分に速い**（CI で数十秒）。tests は shard 並列でも数分を要し、必須化は 1 マージあたりその時間を待つことになる。このリポジトリは 1 日に複数回マージが行われる運用であり（2026-11-28 のみでも #1163〜#1171）、待ち時間は運用の主経路に乗る。
3. **matrix ジョブの required context は名前が shard パターンに結びつき脆弱である**。`tests` は 5 shard に分かれるため、必須にするには `tests (test_[a-d]*.py)` 等の context 名を 5 つ列挙するか、集約用の単一 context（`needs: tests` のサマリージョブ）を新設する必要がある。前者は shard パターンを変えるたびにブランチ保護の再設定（管理権限・利用者の手）を要求する。後者は可能だが、1・2 の利益が無い段階で導入する理由はない。
4. **将来 tests を必須にする道は閉じない**。条件（例: validate では捉えられない回帰が main に到達した）が揃ったときは、集約 context `tests` を持つサマリージョブを `ci.yml` に追加し、利用者が `contexts: ["validate", "tests"]` に保護を更新すればよい。その際も context 名は shard パターンから切り離された単一の名前にする。

この節自体が「判断の記録」であり、`POLICY` のコメントから参照される。**ガードは「context が 1 本」を検証するのではなく、「`validate` が含まれ、enforcement が everyone である」ことを検証する。** context の追加は厳格化であって違反ではない（第 4.2 節の注記）。

### 4.6 ワークフローの書き直し（`.github/workflows/main-guard.yml`）

- 冒頭コメントを、時系列の事実に沿って書き直す。旧コメント（「赤いマージの原因は保護の不在であり、本ワークフローは main が無防備であるあいだ毎日赤く失敗する常設の注意である」）は、2026-11-21 に保護が適用された時点で陳腐化した。新しいコメントは、(a) 2026-11-20/21 の 3 件の赤いマージと原因、(b) 2026-11-21 に利用者が保護を適用したことと実測値、(c) 現在の役割（**ドリフト検知: ポリシー適合のあいだ緑で、外れた日だけ赤くなる**）を記す。
- トリガー（日次 cron、手動実行、main への push）は変更しない。push ごとの再検証は、マージ直後に姿勢を確認するという追加の価値を持つ。
- ステップ名を「Is main protected against a red merge?」から、実行内容に忠実な「Check main's branch-protection posture against POLICY」に変える。
- `--strict` は維持する（v2 でも強制モードとして同一の意味を持つ）。

### 4.7 テスト計画

新規 `tests/test_main_guard.py`（shard `test_[m-p]*.py` に収まる。`tests/test_ci_shards.py` が全モジュールちょうど 1 shard を要求するため、パターン重複の無い命名とする）。ネットワークに触れず、純粋関数と `fetch_branch_state` のモックで検証する:

- ポリシー適合の応答 → OK・exit 0。
- `protected: false` → FAIL・exit 1。
- context から `validate` が欠落 → FAIL・exit 1（実測 context がメッセージに現れる）。
- `enforcement_level` が `non_admins` / `off` → FAIL・exit 1。
- `protected: true` だが protection 詳細なし → UNKNOWN・exit 2（健康と報告しない）。
- 追加 context あり（`["validate", "tests"]`）→ OK・注記。
- `FIX_COMMAND` が `enforce_admins: true` と `validate` を含むこと（現行姿勢の再現）。
- `--json` 出力が JSON として読めること。
- 既存 `tests/test_evidence_accounting.py` の `MainGuardTests` と矛盾しないこと（`FIX_COMMAND` が `validate` を含む既存の 2 テストは更新後も成立する）。

### 4.8 waiver の取り扱い（実装スコープ外、記録のみ）

2026-11-21 の waiver 3 件（`state/errata.d/2026-11-21-18bc5097f3f5.jsonl`）について:

- register の 2 件（ERR-20261121-8c6d1f / 8074f0）は、#1005 の「shard 名と実日付による新規行判定」の導入後、**ゲートがこの 2 行に届かなくなり不発である**（同文書第 5 部追記の通り）。
- 受領証の 1 件（ERR-20261121-23edfe）は今も発動し、毎回 1 行の INFO を出す。
- 解除条件「main に必須チェックが入る」は達成された。しかし waiver を閉じることは、`gate_waivers` が `status: "open"` の**書かれた値**を読む以上、(a) 台帳行の書き換え（append-only 違反。override は存在しない）、または (b) `gate_waivers` を後続 errata による annotated 状態の導出まで読む拡張、のいずれかを伴う。(b) を行うと register ゲートがこの 2 行に再び届くため、**同一変更内での ID 免除（`REGISTER_RULE_EXEMPT_IDS` と `PRE_RECEIPT_SESSION_IDS` の前例に沿う）が同時に必要**であり、債務を台帳からコードへ戻す逆行を伴う判断になる。
- したがって本設計は waiver を閉じない。閉じる手順の設計は別の変更として提案する。**現状の INFO と waiver の記録は偽ではなく、害も 1 行の INFO である。**

### 4.9 ドリフト時の運用ランブック

main-guard が赤くなった日（保護の削除・context の欠落・enforcement の弱体化を検知した日）の対処:

1. `python3 tools/main_guard.py` を実行し、FAIL の行と実測値を読む。`UNKNOWN` の場合は権限・ネットワークの問題であり、ポリシー違反ではない。
2. 管理権限を持つ利用者が `python3 tools/main_guard.py --command` の出力（第 4.3 節の `FIX_COMMAND`）を 1 回実行する。これは現行のポリシー姿勢をそのまま再現する。
3. `gh api repos/.../branches/main` で `contexts` と `enforcement_level` を目視確認する。次の日次実行が緑に戻ることで、検知 → 修正 → 確認の輪が閉じる。
4. 修正は設定変更であり、コミットも PR も生成しない。**赤い main-guard はどの PR のマージも妨げない**（必須チェックではない、第 4.4 節）。妨げるべきは赤い `validate` であり、それは今も必須である。

---

## 5. 実装一覧

| ファイル | 変更 |
| :--- | :--- |
| `tools/main_guard.py` | v2: `POLICY` の導入、判定表（第 4.2 節）への準拠、`--json` の追加、`FIX_COMMAND` の現行姿勢への更新、docstring・出力文の陳腐化の訂正 |
| `.github/workflows/main-guard.yml` | 冒頭コメントを時系列の事実と現在の役割（ドリフト検知）に書き直し、ステップ名を変更。トリガーと実行コマンドは維持 |
| `tests/test_main_guard.py` | 新規。第 4.7 節の検証項目（ネットワーク無し） |
| `docs/2026-11-28-main-guard-policy-conformance.md` | 本稿 |

台帳（`state/*.d/`）・スキーマ・他のゲートツールへの変更は無い。

---

## 6. 検証結果（2026-11-28、実装ブランチ上の実測）

- `python3 tools/main_guard.py` → `OK: ... protected. required contexts=['validate'], enforcement_level='everyone'`、exit 0。
- `python3 tools/main_guard.py --json` → `verdict: ok`、実測値とポリシーを含む JSON。
- `python3 -m unittest tests.test_main_guard` → 全テスト ok。
- `python3 -m unittest discover -s tests -t .`（全 5 shard 相当の直列実行）→ 全テスト ok。
- `python3 tools/validate_seed.py` → 緑。`append_only_check --base HEAD^1` は PR 上で緑（台帳行の追記・改変は無し）。
- `python3 tools/size_budget.py --strict` → 緑。
- 文字検証: 本稿は日本語文書として、中国語簡体字専用の漢字・ハングル・デーヴァナーガリー・キリル文字を含まないことを機械走査で確認した（ギリシャ文字は使用していない）。

---

## 7. 参照

- 記録: `docs/2026-11-20-evidence-accounting-change.md`（第 5 部追記・第 6 部）
  https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-20-evidence-accounting-change.md
- ガード v1: https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/main_guard.py
- ワークフロー: https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/.github/workflows/main-guard.yml
- 事故の行を運んだマージ: https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/998 ・ https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1002
- 新規行判定を変えたマージ: https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1005
- テスト実行時間の分析: https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-23-test-suite-runtime-analysis.md
