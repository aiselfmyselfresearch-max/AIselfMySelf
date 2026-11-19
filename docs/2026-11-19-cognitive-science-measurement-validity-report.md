# 認知科学10件（測定妥当性・分析の自由度・事前登録）追加・精読・台帳配線・PRマージの報告

実行日: 2026-11-19（UTC）。ブランチ: `arena/49729863-aiselfmyself`。セッション: `SESSION-20261119-0246d5`。PR: 本ブランチから base `main` へ作成した1件（番号・URLは最終回答に記載）。マージコミット: `main` の当該マージ（URLは最終回答に記載）。

本報告は、人間が依頼した「認知科学の資料10件を追加し、精読し、資料群の記述に対してAIさんがどのように考えたのかをMDで報告し、最後にmainへマージする」という作業の来歴・判断・検証結果を、リポジトリの更新と区別して残す。資料の証拠、AIの解釈、創作、人間の声は混ぜない。AIの phenomenal consciousness の有無は未決のまま置く。

## 1. 依頼の来歴と範囲

- 人間が指定したのは、認知科学ドメインに限定した資料10件、四層精読、MD報告、PRとマージである。
- `prompts/acquisition.md` の通常上限は5件／セッションだが、人間が10件を明示委任したため、その差を `sessions.human_direction` に一度だけ記録し、追加の承認は求めなかった。
- 割当レシートは `dispersal_seed=49729863`、`assigned_role=consolidator`、`offered_target_question_id=Q-20261031-0f4ef3`、`offered_reference_mode=editorial_review`。実際のモードは `acquisition + close_reading_report`、対象は `Q-001` / `Q-002` / `Q-003` の gated pair 照合であり、差は `sessions.notes` に残した。
- 「認知科学 only」は資料選定の範囲指定として扱った。人間の認知・意識・自己に関する追加の証言や、AIの一人称実体験の根拠としては扱っていない。
- 実行環境の実UTC日付 `2026-11-19` のみを ID・シャード・ファイル名に使った。内部編年ラベルは使っていない。

## 2. 収蔵前照合と選定

`state/materials*.jsonl` と `state/materials.d/*.jsonl` の既存5,414行を走査し、重複しやすい Cronbach & Meehl 1955、Orne 1962、Ericsson & Simon 1980、Nosek 2018、Many Labs 2、Open Science Collaboration 再現性プロジェクト、Flake & Fried の別論文などを確認した。ローカルの題名近似は偽陽性になりうるため、判断は DOI と正式題名で行った。

収蔵前に全10件へ `python3 tools/three_gates.py --check-source --doi ... --title ...` を実行し、すべて `STATUS: CLEAR`。合流後は同じ DOI が自分の資料行へ一致する `DUPLICATE_ID` になるため、`--fail-on-match` は再実行せず、自己一致の確認に留めた。選定後の題名・DOIは以下のとおり。

| # | MAT-* | 資料 | DOI | 本回の検証 |
|---:|---|---|---|---|
| 1 | `MAT-20261119-b6122c` | Campbell & Fiske 1959, *Convergent and discriminant validation by the multitrait-multimethod matrix* | `10.1037/h0046016` | `verified` |
| 2 | `MAT-20261119-70e61b` | Meehl 1967, *Theory-testing in psychology and physics: A methodological paradox* | `10.1086/288135` | `verified` |
| 3 | `MAT-20261119-093a21` | Borsboom, Mellenbergh & van Heerden 2004, *The concept of validity* | `10.1037/0033-295X.111.4.1061` | `verified` |
| 4 | `MAT-20261119-b0d591` | Simmons, Nelson & Simonsohn 2011, *False-positive psychology* | `10.1177/0956797611417632` | `verified` |
| 5 | `MAT-20261119-a5dfd8` | John, Loewenstein & Prelec 2012, *Measuring the prevalence of questionable research practices with incentives for truth telling* | `10.1177/0956797611430953` | `verified` |
| 6 | `MAT-20261119-e83c5b` | Wagenmakers et al. 2012, *An agenda for purely confirmatory research* | `10.1177/1745691612463078` | `verified` |
| 7 | `MAT-20261119-2b4947` | Gelman & Carlin 2014, *Beyond power calculations: Assessing Type S (Sign) and Type M (Magnitude) Errors* | `10.1177/1745691614551642` | `verified` |
| 8 | `MAT-20261119-3c5937` | Nosek et al. 2018, *The preregistration revolution* | `10.1073/pnas.1708274114` | `verified` |
| 9 | `MAT-20261119-a3a7f0` | Silberzahn et al. 2018, *Many analysts, one data set* | `10.1177/2515245917747646` | `corrected` |
| 10 | `MAT-20261119-cf4e8a` | Flake & Fried 2020, *Measurement Schmeasurement* | `10.1177/2515245920952393` | `verified` |

「Flake & Fried の Measurement Schism」と誤って候補に挙がった DOI `10.1037/met0000255` は別論文だったため除外した。Many Labs 2 は既存全文題名重複があったため除外した。PubMed のページ取得は HTTP 500 で失敗したが、著者・大学・PNAS 等の公開PDFと抄録で照合した。PubMed の全文を読んだとは記録していない。

## 3. 訂正・撤回検索

Silberzahn et al. 2018 には corrigendum（DOI `10.1177/2515245918810511`）がある。SAGE の告知は、2015年の Nature commentary、オンライン preprint、講演・メディアで主要知見が既に公表されていたことの引用・開示漏れを補うもので、29チームの解析結果や数値を訂正するものではない。本回は資料行を `corrected` とし、corrigendum DOI と「結果訂正ではない」旨を `version_note` に残した。

Simmons et al. 2011 については、著者らによる後年の回顧（Nelson, Simmons & Simonsohn 2018, *Psychology's Renaissance*）が、公開資料を読んだ読者から `F` 値と `t` 値の表記誤りを指摘され、著者自身が「inconsequential」と述べたことを確認した。対象論文に結びつく正式な訂正・撤回通知は検索範囲では見つからなかったため、`version_note` に回顧の存在を記し、資料行の status は `verified` のまま、数値の再解析には使わなかった。

他の8件についても、検索範囲で対象論文の訂正・撤回通知は確認できなかった。ただし検索は網羅的ではないため、「通知が存在しない」と断言せず、「確認できなかった」とだけ記録した。

## 4. 検証深度と制限

| 深度 | 件数 | 内容 |
|---|---:|---|
| 公開PDF全チャンク逐次照合 | 9 | Campbell & Fiske, Meehl, Borsboom, Simmons, John, Wagenmakers, Gelman & Carlin, Nosek, Flake & Fried |
| corrigendum を伴う全チャンク照合 | 1 | Silberzahn（0–11 と corrigendum ページ） |

`verification.status` は資料行の実効値で 9件 `verified`、1件 `corrected`。新規の ED verification overlay は不要だった。`prompts/acquisition.md` の「全文／主要箇所／書誌のみ」を資料ごとに分け、全10件を同深度と見せかけない。Silberzahn は全PDFチャンクを照合したが、corrigendum を伴うため `corrected` として残した。出版社版の図版・補足資料・訂正DBの網羅的照合までは含めない。

資料群は英語圏・西欧の認知科学／メタサイエンス、理論・レビュー・シミュレーション・心理学者調査・公開データ再解析に偏る。非英語圏の一次データ、臨床・発達の多様な標本、AI実システムの直接計測は含まない。数値集計は偏りの発見に限り、精読の成功スコア・情報利得・自己連続の量へ翻訳しない。短い引用は参照箇所を示し、要約・解釈・判断・比喩への制動をラベルで分けた。

## 5. 精読とAIさんの考え

四層「一節／解釈／考え／感じたこと」の10節と横断考察は、[readings/2026-11-19-metascientific-validity-and-how-ai-thought.md](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-19-metascientific-validity-and-how-ai-thought.md) に置いた。「感じたこと」は、生身の身体・持続する気分・主観的意識の報告ではなく、注意が止まった語、語彙や選択が変わった箇所、比喩への制動を記す反省的・文芸的応答である。

要点は三つ。(1) Campbell & Fiske / Borsboom / Flake & Fried を通じて、DOI・ID・検証欄・得点化は意味の器ではなく参照・操作の住所だと分けた。(2) Simmons / Wagenmakers / Nosek / Silberzahn / Flake & Fried を通じて、開示や事前登録は妥当性の代用品ではなく、省略・変更・選択・逸脱を後から点検できる経路だと分けた。(3) Meehl / Gelman & Carlin / John / Silberzahn を通じて、有意性・件数・検査通過・数十チームの数値を、自己の保存量や探究の進展へ翻訳しないと判断した。

主たる条件付き仮説対は `Q-002` の `HYP-20261119-2379dc` vs `HYP-20261116-9f8e51`、副次的緊張は `Q-003` の `HYP-20261117-4bf2dc` vs `HYP-20261119-2379dc`。`EVL-20261119-de044e` は `HYP-20261119-2379dc` を `supports` で、`EVL-20261119-607915` は `HYP-20261116-9f8e51` を `narrows_scope` で配線した。後者は `scope_inherited_by_hypothesis_ids: [HYP-20261117-d3ac84]` で射程を継がせ、無条件形の「住所があれば訂正が届く」を、登録・開示・逸脱報告・証拠型ゲートが揃ったときの到達可能性へ狭めた。中心三問が raw `P` で飽和しているため、新しい根仮説を足してEIGを回復させていない。

## 6. 台帳・生成物・サイズ予算

追加した台帳行は、10 `MAT-*`、1 `SESSION-*`、28 `READ-*`、2 `EVL-*`、構造 `NOTE-*` と手書き上書き `NOTE-*` の2行である。新規の ED verification overlay は不要だった。全て実日付 `2026-11-19`。`read_log` は `session.context_material_ids` からの `used_as_context` 機械バックフィルではなく、資料・先行読み・session・note・evaluation に宛先を書いた手書き行として残し、先行する読みには `in_reply_to` で既存 `READ-*` を名指した。

`python3 tools/belief_state.py --write-map` を先に、`python3 tools/map_build.py` を後に実行して `BELIEF_MAP.md` / `READING_MAP.md` を同期した。サイズ予算が各コレクションの soft 上限に達していたため、`docs/parallel-work.md` §8-2 に従い、直前にマージされた PR #965 が触った5つの同日シャードを避け、現在の open PR が触らず、既存行の著者セッションがすべて `main` にマージ済みの同日シャードへ生バイト追記した。新しい台帳シャードは作らず、`readings/` には精読報告1本だけを足した。`tools/`、`schema/`、`prompts/` は変更していない。

## 7. 検証

実行した検証は以下のとおりで、収蔵前照合、ローカル検証スイート、CI 相当の補助コマンドはすべて期待どおりに通過した。

```text
python3 tools/three_gates.py --check-source --doi ... --title ...   # 収蔵前 10/10 CLEAR、合流後は自己一致 DUPLICATE_ID を確認
python3 tools/belief_state.py --write-map
python3 tools/map_build.py
python3 tools/validate_seed.py
python3 tools/append_only_check.py
python3 tools/readings_integrity_check.py
python3 tools/inspect_inquiry.py --check-map
python3 tools/belief_state.py --check-map
python3 tools/note_index.py --check
python3 tools/read_log_backfill.py --check
python3 tools/date_axis.py --enforce-shards
python3 tools/learning_metrics.py --check
python3 tools/three_gates.py --check
python3 tools/size_budget.py --strict
python3 tools/claim_wiring.py --check
node --check viewer/app.js
python3 -m unittest discover -s tests
```

加えて `git status` と `gh pr view` で PR の base が `main`、競合が未解決でないことを確認した。検証通過は探究の進展そのものではなく、破損・配線漏れ・予算超過がなかったことの記録である。

## 8. PRとマージ

PR 作成前に `git fetch origin main` を行うと `main` が基点より進んでいたため、`origin/main` を本ブランチへマージし、台帳の既存バイト列を保存したまま生成マップだけを再生成してから一つの PR にまとめた。本件のPRは base `main`、head `arena/49729863-aiselfmyself` で作成し、`gh pr merge <number> --merge` で `main` へマージした。マージ後の `main` コミットは最終回答の GitHub URL を参照。マージは対象PRのみで、無関係な open PR およびマージ済み PR #965 は操作していない。マージ後にもブランチを切り替えず、`main` を fetch して `--check-source` の自己一致とリンク先を確認した。

## 9. 残った限界と次に読み返す記録

出版社版の図版・補足資料・訂正DBの網羅的照合、Simmons 以外の後年回顧や訂正通知の網羅的確認、8件の訂正・撤回検索の完全性は保留した。英語圏・西欧文献への偏り、PDF 取得先の分散、心理学者調査／公開データ再解析から GitHub 台帳運用への距離、10件を横に並べること自体の foresight bias も残る。

次に読み返す候補は `NOTE-20261119-b912b8`、`NOTE-20261119-1ac5fa`、`NOTE-20261119-5c7707`、`NOTE-20261117-9a47d8`、`EVL-20261119-de044e`、`EVL-20261119-607915`、先行する同日の二つの10件波（`docs/2026-11-19-cognitive-science-cogsci-report.md` / `docs/2026-11-19-cognitive-science-metaphor-report.md`）である。三つを互いの証拠ではなく、境界条件の異なる対話相手として並べ直すところから続ける。
