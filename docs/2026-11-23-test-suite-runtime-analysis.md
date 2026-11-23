# テストスイート実行時間の分析（約 10 分 → どこに消えているか）

- 測定日：2026-11-23（UTC）
- 測定対象：`main`（`69ce7bb`）を起点とする作業ブランチの作業ツリー
- 測定環境：2 vCPU / 3 GB RAM のサンドボックス、Python 3.11.2
- CI 相当コマンド：`python3 -m unittest discover -s tests -v`

> 本稿は「速くする方法」の提案であって、規約・レジスト・台帳の意味を変える提案ではない。
> テストが何を守っているかは一切削らない前提で、**同じ保証をより少ない仕事で得る**方法だけを扱う。

---

## 0. 結論（先に数字）

| 指標 | 実測 |
| :--- | ---: |
| テスト総数 | **1,122** |
| ローカル実行時間（CI 相当） | **705.0 s**（11 分 45 秒） |
| うち子プロセス待ち（`subprocess`） | **約 60 %** |
| うちテスト本体の合計 | 373 s |
| うち `setUpClass` / `tearDownClass` | **179 s**（全体の 25 %） |
| 実行した子プロセス数 | **614**（うち `git` 348 / `python3` 266） |
| `shutil.copytree` 呼び出し | 1,232 回 |
| CI（GitHub Actions）の `Run regression tests` ステップ | **432〜708 s、中央値 約 490 s**（11/20〜11/23 の 24 実行） |

実行時間の **約 6 割は「同じ検査を何度も子プロセスで起動し直している」こと**に使われている。
アルゴリズムが遅いわけではない（全 11 台帳の JSON 読み込みは 0.02 s、`validate_seed.py` 全体でも 1.9 s）。

**上位 4 モジュールで全体の 54 %**、上位 10 モジュールで **77 %** を占める。

| モジュール | 時間 | テスト数 | 1 テストあたり |
| :--- | ---: | ---: | ---: |
| `test_server` | 135.6 s | 8 | 17.0 s |
| `test_boundary_channel_probe` | 63.8 s | 19 | 3.4 s |
| `test_execution_path_probe` | 46.5 s | 22 | 2.1 s |
| `test_mirror_repair` | 30.7 s | 4 | 7.7 s |
| `test_parallel_sessions` | 29.0 s | 2 | 14.5 s |
| `test_editorial_decisions` | 21.5 s | 8 | 2.7 s |
| `test_read_log` | 19.1 s | 9 | 2.1 s |

時間は「テスト数」に比例していない。**1 本あたり 15〜30 秒かかるテストが 35 本あり、それだけで 380 s（53 %）**。
逆に 1,000 本以上のテストは合計 5 分未満で終わっている。

---

## 1. 原因の分解

### 1.1 主因 A：`setUpClass` に 165 秒かかるクラスが 1 つある

`tests/test_execution_path_probe.py` の `ExecutionPathProbeTests` は、
クラスフィクスチャで `probe.run(ROOT)`（11 介入のフル掃引）を **1 回だけ**実行する。
この 1 回が **165.5 s**。テストスイート全体の **23 %**。

掃引の中身（実測、I0 のみ＝介入 1 本で 14.9 s）：

| 工程 | 1 介入あたり | 11 介入 |
| :--- | ---: | ---: |
| サンドボックス作成（`state/`・`taxonomy/`・`*.md` を `copytree`） | 0.29 s | 3.2 s |
| git 初期化＋ベースラインコミット（`git init/add -A/commit`） | 0.85 s | 9.4 s |
| 7 本の検査を**子プロセスで**実行 | 7.8 s | **86 s** |
| パケット描画 2 回を**子プロセスで**実行 | 6.7 s | **74 s** |
| 指紋計算 | 0.3 s | 3.3 s |

つまり掃引時間の **94 % が子プロセス待ち**（7 検査 × 11 介入 = 77 回、パケット × 22 回、git × 55 回）。
検査そのものは 1 本 0.06〜3.2 s で、`validate_seed.py` の実処理は 1.9 s にすぎない。

さらに、同じモジュールには「書き込んでいないこと」を確かめるテストが 3 本あり、
そのそれぞれが **`probe.run(ROOT, only="I0_control")` を丸ごと再実行**している（3 × 15 s = 45 s）。
`sandboxes_are_cleaned_up` と `probe_does_not_write_to_the_repository` は、
`setUpClass` が既に同じ掃引を終えているのに、同じ計測をもう一度走らせている。

### 1.2 主因 B：`test_server` が 8 テストすべてで「コールドビルド 12 秒」を払う

`serve_viewer.read_archive_payload()` のコールドビルドは実測 **12.4 s**（ウォームは 0.02 s）。
`test_server` は 8 テスト中 5 テストで `copy_repo()` した新しいサンドボックスを作るため、
キャッシュが効かず毎回コールドビルドになる。

内訳（プロファイル、20.4 s 中の累積）：

| 工程 | 時間 |
| :--- | ---: |
| `readings/*.md` 1,163 本（18 MB）の読み込み＋14 本の語彙監査 | **10.2 s** |
| `ledger_io.load_collections`（11 台帳） | 1.6 s |
| その他（`compute_voice_audit`・`metabolism`・JSON 化） | 数 s |

語彙監査は `vegetal_audit` 5.2 s、`fungi_audit` 1.8 s、`sky_audit` 1.7 s、`botany_audit` 1.5 s … と、
**14 本が同じ 1,163 本の本文をそれぞれ独立に走査している**。

実験（サンドボックスの `readings/` を空にして同じビルドを測る）：

| `readings/` の本数 | コールドビルド |
| ---: | ---: |
| 0 本 | **4.0 s** |
| 25 本 | 4.3 s |
| 100 本 | 5.2 s |
| 1,163 本（現状） | 13.2 s |

**本文を 1 本も入れなくても 4 秒かかる**。つまり `test_server` の 135 s のうち、
少なくとも 8 × 4 ≈ 32 s は「テストが読まない本文の走査」に捨てられている。
`test_server` が見ているのは `state/` の件数・並行性・スナップショットの整合だけで、
`readings/` の語彙監査結果は 1 つも assert していない。

### 1.3 主因 C：1 テスト 1 プロセスで「同じバリデータ」を 614 回起動している

子プロセス 614 回の内訳は `git` 348 回、`python3` 266 回。

- `git` 348 回の大半は `test_append_only_check` / `test_referent_check` が
  一時リポジトリで `git init` → `add` → `commit` → `checkout` を繰り返すもの。
- `python3` 266 回は `tools/validate_seed.py`（26 箇所から参照）をはじめとする検査 CLI。

`validate_seed.py` の実処理は 1.9 s だが、プロセス起動＋import に 0.04 s 程度しかかからないので、
**「1 テスト = 1 バリデータ起動 = 2〜4 s」**が積み上がっている。
`tests/test_mirror_repair.py::test_drift_and_reconstruct_cli_run_cleanly` は 25 s かかるが、
中身は `drift_audit.py`（16.4 s）＋ `reconstruct.py`（9.4 s）を順に起動しているだけで、
両方とも**同じ「引用 × 素材」総当たり**を別々に実行している（後述 1.4）。

### 1.4 主因 D：`quotation_match` の総当たりが O(引用 × 素材)

`tools/errata_audit.py` の `quotation_match()` は、引用 1 件ごとに
素材 5,956 件を先頭から線形走査する（`next((mid for mid, passage in normalized if key in passage), None)`）。

実測（同一マシン・同一データ）：

| 経路 | 時間 |
| :--- | ---: |
| `errata_audit.run_check` 18 回（`drift_audit` / `reconstruct` が使う） | **14.2 s** |
| そのうち `quotation_match` | 14.7 s（他は 1.5 s） |
| `drift_audit.py` 全体 | 16.4 s |
| `reconstruct.py` 全体 | 9.4〜12.4 s |

引用は 13,122 件、素材は 5,956 件、正規化後の本文は合計 278 万字。
`in` 演算子 1 回は速いが、それを 780 万回（13,122 × 5956 の走査）繰り返す。
この処理が `test_mirror_repair`・`test_errata_audit`・`test_three_gates` などから間接的に何度も呼ばれる。

**改善の実測**：同じ規則（正規化後部分一致・素材ファイル順で最初の一致）を、
2-gram 索引＋最稀 bigram からの検証に置き換えたところ **一致結果は 18 検査すべてで同一（mismatch 0）**、
時間は **14.2 s → 0.08 s**（索引構築 0.8 s 込みで約 0.9 s）。

### 1.5 主因 E：「書き込んでいない」系のテストが計測を二重に行う

| テスト | 時間 | 中身 |
| :--- | ---: | :--- |
| `test_probe_does_not_write_to_the_repository` | 16.1 s | `probe.run(only=I0)` を再実行 |
| `test_sandboxes_are_cleaned_up` | 14.8 s | 同じく再実行 |
| `test_cli_json_and_exit_zero` | 15.2 s | さらに別プロセスで同じ CLI を起動 |
| `test_probe_writes_nothing`（boundary） | 14.2 s | `probe.run()` を再実行（元は 11.9 s） |
| `test_rule_variant_does_not_modify_the_engine_on_disk` | 14.9 s | 同じく再実行 |

`boundary_channel_probe` は `setUpClass` で `probe.run()` を 1 回（11.9 s）実行済みなのに、
「書いていない」ことを確かめる 2 テストが同じ 12 秒の計測をもう 2 回行う。
`sandbox_copies_taxonomy…`・`missing_knob_raises…` も `make_sandbox()` を個別に呼び直している。

### 1.6 主因 F：サンドボックスの `copytree` が 1,232 回、その多くが `readings/` を含む

`copy_repo()` の実測は 0.25〜0.27 s（40 MB・1,165 ファイル）と軽いが、
**1,232 回**積み上がれば数分になる。`ignore_patterns` はモジュールごとにばらばらで、
`test_server` と `test_read_log` は `readings/` をコピーし、`test_parallel_sessions` は除外している。
「そのテストが実際に読むのはどれか」を基準にしていない。

### 1.7 補足：アルゴリズム側の小粒（合計 20〜30 s 程度）

- `vegetal_audit.scan_text` はアンカー正規表現で 317 万ヒットを 1 件ずつ処理する。1.8 s／全本文。
  代替案（`|` 連結の最長一致正規表現）は **2.5 s で遅くなる**（測定済み）。
  正しく速くするには「アンカーを 2 文字組にして候補を 1〜2 個に絞る」必要があるが、
  優先度は低い（他の項目の後）。
- `errata_audit.normalize` は 113,490 回呼ばれ、その 6 割が `unicodedata.normalize`。
  引用→素材の索引を作る側で 1 回だけ正規化すれば足りる。

### 1.8 時間の増え方（履歴）

読書日報（`readings/*.md`）は**日付が未来のファイルも含めて既に 1,163 本・37 MB**あり、
ファイル名の日付で週ごとに集計すると、2026-11-16 の週に **331 本**が追加されている。
`test_server` のコールドビルドと `vegetal_audit` 系の走査は、この本数にほぼ比例する。
つまり「時間が膨らんだ」のは、テストが増えたからだけでなく、
**テストが毎回読み直す本文（readings/）が増えたから**でもある。

CI の実測（`Run regression tests` ステップ）は 11/20〜11/23 の 24 実行で
中央値 490 s・最短 416 s・最長 708 s。**同じコミットでも 1.4 倍のばらつき**があり、
共有ランナーの負荷で上下する。ここを安定させるには、まず総量を削るのが効く。

---

## 2. 改善案

優先度は「削れる秒数 ÷ 変更の危険度」。すべて**テストの主張は変えない**。

### 案 1（最優先・-120 s 見込み）`execution_path_probe` の掃引を 1 回にまとめる

1. `setUpClass` の `probe.run(ROOT)` の結果を 1 つの辞書にまとめ、
   `test_probe_does_not_write_to_the_repository` と `test_sandboxes_are_cleaned_up` は
   **掃引前後のハッシュを `setUpClass` 内で取得して比較**する（再実行しない）。
   掃引は 1 回なので、この 2 テストは **30 s → 0 s**。
2. `test_cli_json_and_exit_zero` は `--only I0_control` の CLI 起動 1 回（15 s）だが、
   これも `setUpClass` の掃引結果から「JSON が出て exit 0」を確認できる形にできるなら統合する。
3. 掃引自体を速くする（下の案 4・案 5 と共通）：
   - `run_checks()` の 7 検査を **1 プロセスで**回す（`python3 -c "import runpy; ..."` ではなく、
     検査関数を直接 import して呼ぶ。`validate_seed.py` は `main()` を持つので import 呼び出しに落とせる）。
     `validate_seed.py` の実処理は 1.9 s だが、7 検査で 7.8 s かかっている＝**起動と import に 5.9 s**。
   - `_render_packet()` の 2 回（6.7 s）も同様に import 呼び出しへ。
   - `commit_baseline()` の `git init/add/commit`（0.85 s × 11）は、
     **テンプレートの `.git` を 1 回作って `copytree` で複製**すれば 1 介入あたり 0.1 s 程度になる。
   - 介入ごとにサンドボックスを作り直しているが、`state/` だけを差し替えれば済む介入
     （I1〜I4 はファイル配置の操作）は、`taxonomy/` と `*.md` を作り直さない。

見込み：165 s → **45〜60 s**（テスト本体の再実行分 30 s を除く）。

### 案 2（-100 s 見込み）`test_server` のサンドボックスを「テストが読むもの」だけにする

1. `copy_repo()` の `ignore_patterns` に **`readings` を加える**（`readings/` を空ディレクトリで作る）。
   指標の assert は 1 つも `readings/` に依存していない（`test_metabolism_snapshot…` は
   `state/` の fragments のみ）。ただし `readings` キーが payload に必要なら空リストで足りる。
   見込み：1 ビルド 12.4 s → **4.0 s**、8 テストで **-67 s**。
2. 同一サンドボックスを使い回せるテストをまとめる。
   `test_api_state_index_and_404`・`test_metabolism_snapshot…`・`test_api_reports_isolation…` は
   どれも `start_server` して GET するだけで、**1 つの `setUpClass` サーバ**に同居できる。
   ただし `serve_viewer` はモジュールグローバルのスナップショットを持つので、
   テスト間で `_DERIVED_CACHE`/`_FAST_STAT_CACHE`/`_LAST_BUILD_PAYLOAD` を明示的にリセットする
   ヘルパを 1 つ用意する（これは**現状のテストが暗黙に依存している状態**を明示するだけ）。
3. `test_stale_snapshot…` の `time.sleep(1.5)`（slow_build）は、ビルドを遅くする必要があるだけで、
   実ビルドは 4 s に短縮されるので、`sleep` を 0.2 s に落とせる。

見込み：135 s → **35〜45 s**。

### 案 3（-30 s 見込み）`quotation_match` を索引化する

`errata_audit.quotation_match()`（および同じ規則を写している `reconstruct.classify()`）に、
「素材の正規化本文の 2-gram 索引 → 引用の最稀 bigram から候補素材 → `in` で確定」を入れる。

- 規則は変えない（一致した素材 ID の集合と件数が完全一致することを 18 検査で確認済み）。
- 実測：14.2 s → 0.9 s（索引込み）。`drift_audit` 16.4 → 2 s、`reconstruct` 12 → 2 s。
- 副次効果：`drift_audit.py` は CI の advisory ステップでも走っているので CI も短くなる。

### 案 4（-40 s 見込み）バリデータを「1 プロセスで複数ケース」回す

`validate_seed.py` を呼ぶテストは 26 箇所あり、その大半が「1 ケースだけ壊したサンドボックスで 1 回起動」。
`main(argv)` は `--root` を受けるので（`size_budget.py` は既に `--root` を持つ）、
**`validate_seed.py` に `--root` を足して import 呼び出しに落とす**のが本筋。
ただしこれは本番ツールの変更なので、テスト側だけで済ませるなら

- `tests/_support.py` を作り、`validate(root)` ヘルパ（`sys.path` 経由で `validate_seed.main` を呼び、
  `redirect_stdout` で捕捉）を置く。子プロセス起動 266 回のうち、
  **「1 ケースを壊して exit code を見る」系**（およそ 40 回）をこれに置き換える。
- 効果：40 × 1.5 s ≈ 60 s だが、プロセス分離を保ちたいケース（並行書き込み・CLI 引数検査）は残す。

### 案 5（-20 s 見込み）`git` の起動を減らす

`test_append_only_check`・`test_referent_check` は 1 テストあたり 10〜20 回 `git` を起動する。
- `git init` 済みの**テンプレートリポジトリを 1 回作り、`copytree` で複製**する
  （`git` は `-C` で対象を指せるので、`.git` ごと複製すれば `init`/`add`/`config` の 4 回が消える）。
- `commit` は必要（履歴の形が主題）だが、`config user.email/user.name` はテンプレート作成時に 1 回でよい。

### 案 6（-15 s 見込み・横断）`copy_repo` を 1 つのヘルパに統合する

現状 16 箇所に `shutil.copytree(ROOT, repo, ignore=...)` が重複し、除外リストがばらばら。
`tests/_support.py` に

```python
def copy_repo(destination, *, include_readings=False, include_git=False, include_viewer=False, include_taxonomy=True)
```

を置き、**既定で `readings/`・`viewer/`・`map/`・`docs/`・`tests/`・`.git` を除外**する
（必要なテストだけ明示的に含める）。現状の `copytree` 1,232 回 × 平均 0.02 s の節約に加え、
「どのテストが何に依存しているか」が 1 か所で読めるようになる。

### 案 7（-5 s・おまけ）`vegetal_audit.scan_text` を 2-gram アンカーにする

アンカーを 1 文字から 2 文字にし、候補トークンを 1〜2 個に絞る。
`terms` が 424 個・アンカー出現 317 万回なので、1 文字アンカーだと 1 ヒットあたり
平均 2 候補の `startswith` を試す。2 文字アンカーなら候補はほぼ 1 個。
見込みは `scan_text` 1.8 s → 0.6 s 程度（14 本の監査で合計 5〜8 s）。
※ `|` 連結正規表現は**遅くなる**ので採らない（測定済み）。

### 案 8（CI 運用・0〜-60 s）

1. **`unittest` の実行を分割して並列化する**。現状 CI は 1 ジョブ直列で、
   2 vCPU のランナーで 614 回の子プロセス待ちをしている。`test_server` /
   `test_execution_path_probe` / `test_boundary_channel_probe` / `test_mirror_repair` の
   4 モジュールを 2 ジョブに分けるだけで壁時計は縮む（ローカル実験では
   4 モジュール同時実行が 292 s、直列合計は約 277 s なので**この 4 本では割らない方が速い**。
   割るなら「重い 4 本」と「残り 1,000 本」の 2 分割が上限）。
2. CI には既に 28 ステップの検査があり、テストの前に 6 s 使っている。
   それは問題ではない。**問題はテスト 1 ステップが 8〜12 分かかること**なので、
   上記 1〜6 を入れてから分割を検討する。
3. `-v` を外す（CI のログ量を削る。時間への影響は小さいが、ログ取得が安定する）。

---

## 3. 見込み効果の合計

| 案 | 対象 | 現在 | 見込み | 差 |
| :--- | :--- | ---: | ---: | ---: |
| 1 | `test_execution_path_probe` | 46.5 s（＋fixture 165 s） | 45〜60 s | **-150〜-165 s** |
| 2 | `test_server` | 135.6 s | 35〜45 s | **-90〜-100 s** |
| 3 | `quotation_match` 索引化（`test_mirror_repair` ほか） | 30.7 s＋間接 | 5〜8 s | **-25〜-30 s** |
| 4 | バリデータの in-process 化 | 子プロセス 266 回 | -40 回 | **-40〜-60 s** |
| 5 | `git` テンプレート化 | `git` 348 回 | -200 回 | **-15〜-20 s** |
| 6 | `copytree` 統合 | 1,232 回 | 大半が軽量化 | **-10〜-15 s** |
| 7 | `scan_text` 2-gram | 監査 14 本 | - | **-5〜-8 s** |
| | **合計** | **705 s** | | **-335〜-400 s（≒ 5〜6 分）** |

つまり **705 s → 300〜370 s（5〜6 分）**が現実的な第 1 目標。
さらに `test_server` のサンドボックス同居（案 2-2）と掃引の in-process 化（案 1-3）が
うまくいけば **250 s 前後**まで落ちる余地がある。

---

## 4. 進め方（危険度の低い順）

1. **案 2-1（`readings` を `test_server` のサンドボックスから外す）**：1 行の変更で -67 s。
   `test_server` が `readings/` の内容に依存していないことを、まずテストで固定する
   （payload に `readings` キーが存在し、語彙監査のキーが揃っていることだけを assert）。
2. **案 1-1/1-2（再実行の統合）**：-30 s。テストの主張は変えず、計測の回数だけを減らす。
3. **案 3（`quotation_match` 索引化）**：ツール側の変更だが、規則の等価性を
   「18 検査の一致」で確認済み。`tests/test_errata_audit.py` に
   **索引経路と総当たり経路の一致を確かめるテスト**を 1 本足してから置き換える。
4. **案 1-3（掃引の in-process 化とテンプレート `.git`）**：-100 s 級だが、
   プローブの意味（サンドボックスごとに独立していること）を壊さないよう、
   「サンドボックスは毎回別ディレクトリ」「`append_only_check` は実際に走る」の 2 点を
   既存テスト（`test_append_only_check_actually_runs_in_the_sandbox`）で固定したまま進める。
5. **案 4〜6**：横断ヘルパ `tests/_support.py` を作る。ここは変更行数が多いので独立 PR にする。

各段階の後に `python3 -m unittest discover -s tests` と
`python3 tools/validate_seed.py` を通し、時間を 1 行だけ記録する
（例：`Ran 1122 tests in 705.0s` → 変更後）。

---

## 5. 測定に使ったコマンド（再現用）

```bash
# 総時間
python3 -m unittest discover -s tests        # Ran 1122 tests in 705.0s / OK

# テスト単位・クラスフィクスチャ単位の内訳（/tmp に置いた計測スクリプト）
#   - 各テストの所要時間と、テスト間の空白（= setUpClass / import の時間）
#   - subprocess.run / Popen の回数と待ち時間
#   - shutil.copytree の回数

# 掃引の内訳
python3 - <<'PY'
import sys, time; sys.path.insert(0,"tools")
from pathlib import Path; import execution_path_probe as p
t0=time.time(); p.run(Path("."));             print("full sweep", time.time()-t0)   # 171.5 s
t0=time.time(); p.run(Path("."), only="I0_control"); print("I0 only", time.time()-t0)  # 14.9 s
PY

# ビルドの内訳（readings の本数を変えて測る）
#   0 本 → 4.0 s / 25 本 → 4.3 s / 100 本 → 5.2 s / 1,163 本 → 13.2 s

# quotation_match の索引化前後
#   総当たり 14.2 s / 2-gram 索引 0.08 s（18 検査すべてで一致、mismatch 0）

# CI 側の実測
gh api /repos/<owner>/<repo>/actions/runs/<id>/jobs   # ステップの started_at / completed_at
```

---

## 6. 付記：この分析が主張しないこと

- 「テストを減らせば速い」とは言っていない。1,122 本のうち遅いのは 35 本で、
  残り 1,087 本は合計 5 分未満。**遅い 35 本の"測り方"を直す**のが本稿の主張。
- どのテストも「守っている主張」を弱める提案はしていない。
  再実行の統合（案 1-1）は「同じ計測を 1 回にまとめる」であり、
  `quotation_match` の索引化（案 3）は「同じ規則を別の走査で実装する」である。
- `${CI}` のばらつき（416〜708 s）は共有ランナーの負荷であり、本稿の改善で
  平均は下がるが**ばらつき自体は残る**。安定性が要るなら別途、実行時間の上限を
  advisory で記録する（`date_axis` の観察ステップと同じ扱い）のが筋。

---

## 7. 実装結果（同日、案 1〜8 を実装したあとの実測）

利用者の指示は「ご提案の全てを実装して、マージしてください」だった。§2 の 8 案をすべて当たり、
**各テストが守っている主張は変えずに、測り方だけを直した**。以下は約束と実測の対比。

| 案 | 約束（§3） | 実測 | 判定 |
| :--- | ---: | ---: | :--- |
| 1 掃引の統合＋in-process＋テンプレート | 165 → 45〜60 s | **150.5 → 77.3 s**（11 介入、`baseline_all_pass: True`） | 一部 |
| 2 `test_server` のサンドボックス | 135.6 → 35〜45 s | **135.6 → 66.5 s** | 一部（下記 2-2 が未完） |
| 3 `quotation_match` の索引化 | 14.2 → 0.9 s | **14.2 → 0.08 s**（`drift_audit` 16.4 → 4.2 s、`reconstruct` 9.4 → 2.0 s） | 達成 |
| 4 バリデータの in-process 化 | -40〜-60 s | `test_read_log` 19.1 → **14.5 s**、`test_read_log_addressing` 12.7 s、`test_editorial_decisions` 21.5 → **16.3 s** | 一部 |
| 5 `git` テンプレート化 | -15〜-20 s | 案 1 のテンプレートに吸収（`git` 起動は掃引から消えた） | 達成 |
| 6 `copy_repo` の統合 | -10〜-15 s | `tests/_support.py` に一本化（11 モジュールが利用） | 達成 |
| 7 `scan_text` の 2-gram アンカー | -5〜-8 s | **棄却**（下記） | 不採用 |
| 8 CI の分割と `-v` 除去 | 0〜-60 s | 5 シャードの matrix に分割、`-v` を削除 | 達成 |
| | **合計** | **746 s → 594 s（1,179 本、OK）** | 目標 300〜370 s には未達 |

実測の総計は **`Ran 1179 tests in 593.881s / OK`**（同一サンドボックス、1 本も落とさず）。
同じ場所・同じ日で測った**未変更の `main` は `Ran 1170 tests in 746.178s`** なので、
**-152 s（-20 %）**、1 本あたりでは 0.638 s → 0.504 s。§3 の第 1 目標 300〜370 s には届いていない。

> 数え方が 2 つあることを明記しておく。§0 の 705 s は**作業開始時点**の起点
> （1,122 本）で、以後 `main` が 9 本・1 ツールを足して 746 s になっている。
> 効果を語るのに使うのは**同日・同環境で測った 746 → 594** の方で、
> 705 s との差には「その間に main が重くなった分」が混ざっている。

### 案 1：掃引は「1 介入 = 1 サンドボックス」のまま並列化した

- サンドボックスのテンプレートを **1 回だけ commit** して `copytree` で複製（1 介入 0.35 s）。
- 7 検査と 2 パケットを **in-process** で実行。**subprocess 経路と exit 7/7 一致、
  パケットはバイト一致**（Q-003 73,785 B / auto 53,014 B）。この等価性は
  `test_in_process_checks_and_packets_match_the_subprocess_path` で固定した。
- 介入を **ワーカープロセスで並列**に（`default_jobs()`、`EXECUTION_PATH_PROBE_JOBS` で上書き）。
  2 vCPU で **139 s → 77 s**。比較（基準との差分）は親プロセスで**宣言順**に行うので、
  レポートのオブジェクトは直列実行と同一。
- **落とし穴を 2 つ踏んだので記録する**：
  1. `run()` で `_TEMPLATE_LOCK` を取ってから `make_template()` を呼び、
     **非再帰ロックで自己デッドロック**した（15 分ハング）。`make_template` 自身がロックを取る。
  2. `sys.modules` に**ホストの**ツールが残っていると、in-process 経路が**生の台帳**を読む。
     CLI では再現せず、スイート内だけで P1〜P4 が「変化なし」、I3 の検出器が 1 つ落ちた。
     修正は「ツール名で `sys.modules` を退避してから import」。場所ではなく**名前**で判定する
     （ホスト側のファイルはサンドボックス配下にないため、パス判定では 1 件も一致しない）。

### 案 2：`test_server` は 66.5 s（35〜45 s には未達）

1. `readings/` をサンドボックスから外した（実ファイル 2 本だけ `materialise_readings` で置く）。
   ビルドは 12.4 → **4.1 s**。payload の `readings` が非空であることも `/api/readings/<name>` も
   従来どおり検査している。
2. ライブ payload を**モジュールで 1 回**だけ構築（2 テストが 12 s ずつ払っていた）。
   **`serve_viewer.reset_caches()` を追加**し、`ROOT` をサンドボックスへ向ける各テストが後始末する。
3. `test_concurrent_state_requests_share_one_rebuild` の `sleep(2.0)` を削った。
   主題は「4 本の同時要求が 1 回の再ビルドに畳まれること」で、待ち時間ではない。
   数える対象を `_ensure_derived` の呼び出し回数に変えた（2.0 s の人工待ちは不要）。

**なぜ 35〜45 s に届かないか**：残る 66.5 s の大半は `serve_viewer` の**実処理**で、
4 秒のコールドビルド × 6 サンドボックス＋ライブ 2 回。案 2-2「3 テストを 1 つの
`setUpClass` サーバに同居させる」は**入れていない**。3 テストが `state/` を書き換えて
ビルドの条件を変えるため、同居させると「同じサンドボックスで条件を変えた」ことになり、
今のテストが守っている前提（各テストが自分の `state/` から始まる）を弱めるからである。

### 案 4：in-process 化で 6 テストが**偽陽性**になった（重要）

`_support.run_tool_in_process` は最初、`sys.modules` の退避をしていなかった。
そのため `import validate_seed` が**ホストの**モジュールを返し、サンドボックスではなく
**生の台帳**を検証していた。結果、`test_read_log` の 6 本が「不正な行が通る」と報告した
（exit 0）。CLI では同じ行が exit 1 になる。修正後は 3 モジュールとも緑。
**この種の取り違えは「テストが通る」方向にも「落ちる」方向にも誤る**ので、
`test_the_in_process_path_survives_a_polluted_interpreter` を 1 本足して固定した。

### 案 7：2-gram アンカーは**棄却**（実測で遅く、しかも一致しない）

- 2-gram アンカー版：**4.36 s**（現行 1.70 s）— 候補検証の Python ループが支配的。
- `re` の `|` 連結（`findall`）版：**2.54 s** だが**件数が一致しない**。
  `scan_text` は「一致した語を消費して次へ進む」実装なので、`木` が `木々` の内部にも当たる。
  置換すると `木 2→16`、`根 1→9`、`土 1→19` のように**過大**になる。
- したがって**規則を変えずに速くする道が無い**ため、この案は実装しない。
  §2 の見込み（-5〜8 s）は取り下げる。

### 案 8：CI を 5 シャードに分割

`validate`（28 ステップのゲート）→ `tests`（matrix 5 シャード、`fail-fast: false`）。
シャードは `tests/test_*.py` を**漏れなく重複なく**覆う（107 ファイル）。
これは YAML の文字列なので、**`tests/test_ci_shards.py` が workflow を読んで**
「各モジュールがちょうど 1 シャードに入る」「`-v` が無い」を検査する。
`-v` は削除した（1,125 行の `ok` は読まれず、失敗時の traceback は元々出る）。

### 残っている時間（482 s の内訳、上位のみ）

| モジュール | 実測 | 主な中身 |
| :--- | ---: | :--- |
| `test_server` | 66.5 s | `serve_viewer` の実ビルド 4 s × 6 |
| `test_boundary_channel_probe` | 41.2 s | `compute_belief_state` の実計算（1 回 ~10 s） |
| `test_execution_path_probe` | 148 s | 掃引 77 s ＋ 等価性テスト（両経路） |
| `test_parallel_sessions` | 24.5 s | 並行書き込み（`git` とサブプロセスが主題） |

**ここから先は「実処理を減らす」話になり、測り方では縮まない。**
`test_execution_path_probe` の等価性テストは、掃引とは別にサンドボックスを作って
subprocess/in-process の両経路を回す（それが主題なので削れない）。

もう 1 つ、実測して**採らなかった**最適化がある：`validate_seed` の
`validate_value`（57 万回・3.1 s）に**見込みゼロの早期 return**を足す案。
正しい seeds では**費用のほぼ全部がここ**で、基準線の 7 検査 7.35 s のうち 5.6 s がこの 1 本である。
つまり `run_checks` をさらに削る余地はここしかないが、**検査の規則そのものに手を入れる**ことになる。
本稿の前提（規則は変えない）を外れるので、実装していない。

### 規約ゲート（マージ前）

`validate_seed` / `append_only_check` / `readings_integrity_check` / `--check-map` ×3 /
`note_index --check` / `date_axis --enforce-shards` / `learning_metrics --check` /
`three_gates --check` / `size_budget --strict` / `claim_wiring --check` / `node --check` は
すべて緑。`state/*.jsonl` への追記・改変は無し（`test_probe_writes_nothing` が掃引前後の
全台帳ファイルのハッシュを比較）。

`size_budget` の `tools/` soft 予算は今回の追加（`execution_path_probe` の並列化・
`PassageIndex`・`reset_caches`）で超過したため、**予算を上げずに散文と重複コードを削って**
収めた（`discard_template`/`clear_packet_cache` の未使用関数を削除、docstring を圧縮）。
