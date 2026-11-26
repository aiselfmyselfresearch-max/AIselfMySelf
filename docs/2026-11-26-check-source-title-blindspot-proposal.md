# 収蔵前照合（`--check-source`）の題名の見落とし――ツール・記録ルール・MDの改善提案

- 作成: 2026-11-26
- 起点: [`DEVELOPMENTAL_SCIENCE_REPORT_2026-11-26-silence-of-the-teacher.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/DEVELOPMENTAL_SCIENCE_REPORT_2026-11-26-silence-of-the-teacher.md) の選定中に見つかった照合ツールの見落とし（PR [#1136](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/pull/1136)）
- 対象: [`tools/three_gates.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/three_gates.py) の `check_source`、[`tools/validate_seed.py`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/tools/validate_seed.py) の識別子抽出と重複ゲート、[`schema/material.schema.json`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/schema/material.schema.json)、[`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md)、[`README.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/README.md)
- 計測時点: `main` の [`5345585`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/commit/534558511ba49b2629df9d925b421c3bebd29fb7)（素材 6,306 行）

## 0. 結論（先に）

**主たる修正はツールで行う。記録ルールは「今後の行」に軽い規則を足すだけにする。スキーマはまだ変えない。MDは手順書2か所だけを、ツール修正と同じPRで更新する。過去行は書き換えず、必要なものだけ overlay で別名・重複として結ぶ。**

理由は計測にある（§2）。台帳のデータには一切手を入れず、照合側で `source.title`（原題）を索引に加えるだけで、次の改善が得られる。

- 原題による自己想起: 22.4% → 99.9%
- `20261119` の重複ゲート導入後にすり抜けた重複 22 行: 0 行 → 22 行すべてを検知

見落としの大半は「データの書き方」ではなく「ツールの見る場所」から生じている。一方、二作品を一行にまとめた行や、DOI の誤記・不一致は、ツールでは警告止まりになる。この二つは記録ルールで再発を防ぐ必要がある。

## 1. 何が起きたか

PR #1136 の選定中、Oostenbroek et al. (2016) "Comprehensive Longitudinal Study Challenges the Existence of Neonatal Imitation in Humans" について、`python3 tools/three_gates.py --check-source --title "<原題>"` を実行したところ、結果は **CLEAR** だった。しかし同じ論文は、既に [`MAT-EVD-20261106-0c26d2`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/state/materials.d/2026-11-06-7e2fd51117ef.jsonl) の中に収蔵されていた。この行は Meltzoff & Moore (1977) と Oostenbroek (2016) を一行にまとめたもので、`source.url` には 1977 年の PDF しかない。そのため、ID でも題名でも照合をすり抜けた。重複に気づけたのは、本文を読んでいて偶然見つけたからにすぎない。

仕組みは次のとおり。

1. `check_source` の題名照合（[`three_gates.py` L98–L210](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/tools/three_gates.py#L98-L210)）は、各行の**表示用 `title`** だけと Jaccard 類似度（閾値 0.72）で比べている。表示用 `title` は多くの行で日本語の要約題なので、手順書（[`prompts/acquisition.md` L8](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/prompts/acquisition.md#L8)）の指示どおり `--title "<原題>"` を渡しても、英語の原題とは語が重ならない。
2. 原題を持つ `source.title` は索引に入っていない。
3. 識別子の抽出（[`validate_seed.py` L313–L318 以降](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/tools/validate_seed.py#L313-L318)）が見るのは `source.url` と `source.source_id` だけ。`check_source` は `version_note` 中の PMCID だけを補っているが、`version_note` 中の DOI は拾わない。
4. スキーマの `source` は `additionalProperties: false` で、フィールドは `source_id, title, authors, year, url, version_note` しかない。一行に二作品を書くと、二つ目の作品の識別子を置く場所がない。
5. 運用上は、CLEAR が「新規であることの証明」として扱われている（README の [L116](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/README.md#L116) も「収蔵前の重複・既収蔵照合」とだけ書いている）。

## 2. 規模の計測

台帳全体（6,306 行）について、現行の照合を再実装したものと、改善案を入れたものを比べた。計測用の一時スクリプトはリポジトリに入れていない（[`prompts/acquisition.md`](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/prompts/acquisition.md) の「一時スクリプトを増やさない」に従う）。分かち書きと閾値は `three_gates.py` の `_WORD_RE`・`_TITLE_STOP`・0.72 と同じにしている。

### 2.1 台帳の状態

| 項目 | 行数 |
|:---|---:|
| 素材の総数 | 6,306 |
| `url`/`source_id` から DOI・PMID・PMCID のどれかが取れる行 | 2,508（うち DOI 1,987） |
| ID がなく、`version_note` にだけ DOI がある行 | 290 |
| 表示用 `title` に日本語を含む行 | 5,347 |
| `source.title` に日本語を含む行 | 2,376（うち 1,562 は文学テキスト、1,363 は著者名がラテン文字） |
| `source.title` が複数作品の連結（`／`・`；`・` / `・`; `）である行 | 89 |
| `20261119` 以降の `research_excerpt` | 1,056（うち識別子なし 141） |

### 2.2 原題で照合したときの自己想起

ラテン文字の `source.title`（3 語以上）を持つ 3,758 行で、その原題を `--title` に渡したとき、その行自身が見つかるかを数えた。

| 方式 | 自己想起 |
|:---|---:|
| 現行（表示用 `title` のみ） | 840 / 3,758（22.4%） |
| 案A: `source.title` 全体も索引に入れる | 98.7% |
| 案C: さらに連結題を `／ ； / ;` で分割し、末尾の「(誌名 巻, 年)」を外す | 3,756 / 3,758（99.9%） |

Oostenbroek (2016) の原題は、案Cでのみ `MAT-EVD-20261106-0c26d2` に当たる（現行と案Aでは見つからない）。

### 2.3 既知の重複への効き方

- 同じ識別子を共有する既知の重複ペア 71 組のうち、題名だけで見つかる組: 現行 12 → 案C 58。
- 同一資料のクラスタ（識別子の共有、または正規化した成分題の一致）: 文学テキストだけのものを除いて 107 クラスタ、余分な行は 124。
- **`20261119` の識別子ゲート導入後に採番され、既存行と重複している行は 22 行。このうち既存行と識別子が一致するものは 0 行**。ゲートは 22 行すべてを見逃した。原因は二通りある。
  - 既存行に識別子がなかった（11 行）。例: `MAT-20261120-0ea985` と `MAT-20261105-56dc62`、`MAT-20261120-4264b0` と `MAT-EVD-20261024-35`。
  - DOI が食い違っていた（11 行）。例は §2.4 の表。
- 案C の題名索引は、この 22 行の **22 行すべて**で先行行を指す。
- 2 つ以上の異なる DOI を持つクラスタは 11 ある。

### 2.4 DOI の食い違い（監査対象の例）

| 新しい行 | 先行行 | 新しい行の DOI | 先行行の DOI | 見立て |
|:---|:---|:---|:---|:---|
| `MAT-20261120-b66487` | `MAT-20261117-a6e74b` | `10.1037/0033-2909.121.371` | `10.1037/0033-2909.121.3.371` | 号の脱落（誤記） |
| `MAT-20261121-d7e5b2` | `MAT-20261117-670bfe` | `10.1016/j.tics.2013.04.006` | `10.1016/j.tics.2013.09.007` | どちらかが誤記 |
| `MAT-20261119-cbf48e`, `MAT-20261120-608b58` | `MAT-EVD-20261106-4e33a3` | `nn842` / `nn784` | `nn827` | 三行で三つの DOI |
| `MAT-20261124-ffa22e` | `MAT-20261119-4397d9` | `…05000087` | `…05000129` | BBS の本論とコメント群の取り違えの疑い |
| `MAT-20261120-c20319` | `MAT-20261119-e0cef5` | `10.1207/s15516709cog1903_1` | `10.1016/0364-0213(95)90020-9` | 同じ論文に二つの正当な DOI がありうる（出版社の移管） |
| `MAT-20261122-a82fdb` | `MAT-20261120-8bf11f` | `…00042114` | `…00042113` | BBS の隣接番号（本論とコメント） |

DOI の食い違いには、**誤記もあれば、正当な別 DOI もある**。そのため、DOI の一致だけを根拠に重複を判定し、自動で修復することはできない。題名による照合と人間（またはセッション）の判断の両方が要る。

### 2.5 誤検知の見積もり

`20261119` 以降の行（原題を持つ 1,041 行）を、それより前の行だけを相手に案C で照合した。あわせて**番号ロケータのガード**（章・節・讃歌番号など、題に含まれる数字の集合が両方にあって食い違うときは一致としない）を入れた。

- 警報が出た行: 32 / 1,041
- 警報のペア: 同一資料 28 組、別作品 7 組（警報ペアの約 2 割）

別作品 7 組の内訳は次のとおり。

- 『詩のエッダ』の別の歌（「Hávamál」と「Hyndluljoth」。同じ訳者・同じ書名）
- リグ・ヴェーダの別の讃歌（10 巻 14 歌と 135 歌。ローマ数字なのでロケータのガードが効かない）
- Frith の二論文（"Self-consciousness, self-agency, and schizophrenia" と "Schizophrenia, consciousness, and the self"）
- OSC 2015 本論と "Comment on …" / "Response to Comment on …"（3 組）

ロケータのガードがないと、欽定訳聖書の章違いや相応部経典の経違い（同じ訳者・同じ題型で番号だけ違う）が大量に誤検知になる。つまり、題名照合は**ハードゲートにすると約 2 割を誤って拒否する**。助言（SIMILAR_TITLE）として出し、判断を記録させるのが妥当である。

## 3. 選択肢の比較

| 案 | 内容 | 効果 | 費用・リスク |
|:---|:---|:---|:---|
| **A. ツールのみ** | `check_source` の索引に `source.title`（分割・末尾除去）、`version_note` 中の DOI、著者姓と年を加える。ロケータと「Comment on」のガード | 自己想起 99.9%、ゲート後の重複 22/22 を検知。データ変更なし、append-only と無関係 | 二作品の連結行や DOI 誤記は「警告」止まりで、再発は防げない |
| **B. 記録ルールの変更** | 今後の行で `source.title` を単一作品の原題に限る。連結行を禁止（または作品ごとに一行）。DOI は出版社の DOI ページで確認 | 連結行・識別子なし行の新規発生を止める | 過去行には効かない。`validate_seed.py` の新規行ルール（日付カットオフ方式）が必要 |
| B′. スキーマ拡張 | `source.identifiers[]` や `source.alt_titles[]` を追加 | 作品ごとの識別子を構造化できる | `additionalProperties: false` の変更、全バリデータ・テストへの波及、過去行との二重形式。今回の見落としの解消には必要ない |
| **C. MD・プロンプトの更新** | `prompts/acquisition.md` L8 と `README.md` L116 で、CLEAR を新規性の証明として扱わないことを明記し、原題・著者・年を渡す手順にする | 運用の誤解（CLEAR＝新規）を断つ | 文書だけでは機械的に担保されない。A と組み合わせて意味を持つ |
| D. 過去行の修復（overlay） | 重複・別名を `editorial_decisions` 系の overlay で結ぶ（行自体は書き換えない） | 想起や数え上げで二重計上を防ぐ | 判断を一件ずつ行う必要がある（124 余分行、11 DOI 食い違いクラスタ）。新しい overlay 種別のスキーマ設計が要る |

**推奨は A を中心に B と C を最小限で加え、D は監査リストまでにとどめる**組み合わせである。

## 4. 推奨する段階計画

### 第1段階: ツール修正（MD 2 か所の更新を同じ PR で）

`tools/three_gates.py` の `check_source` を次のように変える。

1. **題名索引の拡張**: 各行について、表示用 `title` に加えて `source.title` を索引に入れる。`source.title` は `／`・`；`・` / `・`; ` で成分に分割し、各成分について末尾の「(誌名 巻, 年)」形式（括弧内に 4 桁の年を含むもの）を外した形も入れる。成分は 3 語以上のものに限る。
2. **ロケータのガード**: 照会題と候補成分の両方に数字（年を含む末尾括弧を除いた部分）があり、その集合が食い違うときは、一致から外す。聖典の章・節・経番号の誤検知を抑える。
3. **応答系のガード**: どちらか一方だけが `Comment on` / `Response to` / `Reply to` / `Corrigendum` / `Erratum` / `Retraction` で始まる場合は、SIMILAR_TITLE ではなく **RELATED**（関連資料）として別に表示する。訂正・撤回は手順書が確認を求めている対象なので、捨てずに見せる。
4. **`version_note` 中の DOI**: DOI でも照合する。ただし `version_note` は関連論文（コメント対象・訂正記事）の DOI を含むことがあるので、**`check_source` では `EXACT(version_note)` として区別して表示し、`validate_seed.py` のハードゲートには入れない**。
5. **`--author` / `--year` の補助**: `source.authors` の第一著者の姓（NFKC・小文字化）と `source.year` が一致する行を、題名の類似度とは独立に **AUTHOR_YEAR** 候補として示す。`source.title` が日本語でも著者名はラテン文字、という 1,363 行に届く。候補は最大 10 件に絞る。
6. **出力の文言**: `STATUS: CLEAR` を `STATUS: NO_MATCH_FOUND` に改めるか、CLEAR の後に「題名・識別子の索引で見つからなかっただけで、新規性の証明ではない」という一行を添える。`--json` の `status` 値は互換のため据え置き、`advisories` フィールドを追加する。
7. **ハードゲートは変えない**: `validate_seed.py` の `check_material_duplicate_identifiers` は識別子だけのままにする（§2.5 の誤検知率のため）。

あわせて `tests/test_three_gates.py` に回帰テストを足す。

- 連結行の二つ目の作品の原題で照会すると、その行が SIMILAR_TITLE に出る（Oostenbroek 型）
- 表示用 `title` が日本語で `source.title` が英語の行を、英語の原題で照会すると見つかる
- 「Psalm 23」で照会しても「Psalm 24」の行は出ない（ロケータのガード）
- "Comment on X" は X に対して RELATED になり、SIMILAR_TITLE にはならない
- `version_note` にだけ DOI がある行を `--doi` で照会すると `EXACT(version_note)` になる
- `--author Meltzoff --year 1977` で AUTHOR_YEAR 候補が出る

MD の更新は次の 2 か所。

- [`prompts/acquisition.md` L8](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/prompts/acquisition.md#L8): `--title "<原題（英語など原語の正式題）>" --author <第一著者の姓> --year <年>` を渡すこと。CLEAR／NO_MATCH_FOUND は新規性の証明ではないこと。SIMILAR_TITLE と AUTHOR_YEAR の候補は本文で確かめ、別作品と判断したらその旨を `source.version_note` に残すこと。
- [`README.md` L116](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/README.md#L116): 使用例に `--author` / `--year` を加える。

### 第2段階: 記録ルール（今後の行のみ、スキーマは変えない）

`validate_seed.py` の既存の日付カットオフ方式（`20261119` など）にならい、新しいカットオフ日以降に採番された行に対して次を求める。

1. **`source.title` は単一作品の原語の正式題**とする（翻訳題・要約題は表示用 `title` に置く）。原題がラテン文字以外の言語なら、その言語のままでよい。
2. **一行一作品**: `source.title` に `／`・`；`・` / ` の連結があれば拒否する。二作品を対比したいときは二行に分け、`EVL-*`／`NOTE-*` 側で結ぶ。
3. **識別子の場所**: DOI・PMID・PMCID は `source.url` か `source.source_id` に置く。`version_note` にしか書かれていない識別子は警告とする（拒否はしない）。
4. **SIMILAR_TITLE を見たうえでの判断の記録**（任意。第1段階の運用を見てから決める）: 先行行と題が近いのに新しく採番する場合は、`source.version_note` に `distinct-from: MAT-…（理由）` を書く。

スキーマ拡張（`source.identifiers[]`・`source.alt_titles[]`）は、1〜3 を数か月運用しても一作品一行で足りない事例が出たときに、改めて検討する。

### 第3段階: 過去行の監査と任意の修復

1. 本提案の §2.3・§2.4 にある、ゲート後の重複 22 行と DOI 食い違いの 11 クラスタを監査リストとして扱い、出版社の DOI ページで正しい DOI を確かめる。
2. 修復が必要なら、行は書き換えず、`editorial_decisions` と同じ流儀の overlay を新設する（例: `target: {"type": "material", "id": "MAT-…"}` に `duplicate_of: "MAT-…"` または `corrected_identifier`）。`tools/ledger_io.py` の既存 overlay 適用（[L268 付近・L304 付近](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/tools/ledger_io.py#L268)）が手本になる。仮説には既に `duplicate_of` がある（[`belief_state.py` L576](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/534558511ba49b2629df9d925b421c3bebd29fb7/tools/belief_state.py#L576)）。
3. 連結行 89 行は、二つ目以降の作品にも照合が届くようになる（第1段階）ので、分割はしない。

## 5. 受け入れ基準

第1段階の受け入れ基準は次のとおり。

- [ ] Oostenbroek (2016) の原題で照会すると `MAT-EVD-20261106-0c26d2` が SIMILAR_TITLE に出る
- [ ] ラテン文字の `source.title` を持つ行の自己想起が 99% 以上（計測時点の値は 3,756 / 3,758）
- [ ] §2.3 のゲート後重複 22 行を、それぞれの原題で（先行行だけを相手に）照会すると、22 行すべてで先行行が出る
- [ ] §2.5 と同じ条件で、別作品の警報ペアが 7 組以下。欽定訳聖書・相応部経典の章違い・経違いが出ない
- [ ] 1 回の照会が、現行と同程度の時間で終わる（全件のシミュレーションでも数秒）
- [ ] `validate_seed.py`、`three_gates.py --check`、既存のテストが変わらず通る（ハードゲートの判定は不変）
- [ ] `prompts/acquisition.md` と `README.md` の更新が同じ PR に含まれる

## 6. リスクと未解決点

- **誤検知**: ロケータのガードがあっても、ローマ数字の番号（リグ・ヴェーダの讃歌）、同じ書名・同じ訳者の別の歌（エッダ）、語彙がほぼ重なる別論文（Frith）は残る。助言にとどめる理由はここにある。ローマ数字をアラビア数字に正規化すればリグ・ヴェーダ型は減らせる。
- **見逃し**: `source.title` が日本語で識別子もない行（2,137 行。うち 1,562 は文学テキスト）には、原題の英語照会は届かない。AUTHOR_YEAR 補助で一部を拾う。翻訳題どうしの照合は対象外とする。
- **`version_note` の DOI**: 関連論文の DOI を「その行の DOI」と誤認するおそれがある。表示を分け、ハードゲートには入れない。
- **DOI の正当な複数性**: 出版社の移管などで、一つの論文に複数の DOI がありうる（Hutchins 1995 の例）。DOI の食い違いを自動で誤記とみなさない。
- **運用の慣性**: 手順書が CLEAR だけを確認させている限り、ツールを直しても候補は読まれない。第1段階で MD を同時に直すのはこのためである。
- **二作品の連結行の扱い**: 過去行は append-only のため分割しない。照合は届くようになるが、`read_log` や想起の単位は一行のままになる。

## 7. 実装の記録（2026-11-26、提案の採用を受けて）

第1段階と第2段階を実装し、第3段階は監査一覧の出力（読み取り専用）まで実装した。過去行の書き換えと、重複を結ぶ overlay の新設は行っていない。

### 7.1 実装した内容

| 段階 | 実装 | 場所 |
|:---|:---|:---|
| 1 | `source.title` の題名索引（作品ごとの分割、末尾の「(誌名 巻, 年)」除去、`「」『』“”` 内の題も索引） | `tools/three_gates.py` の `title_variants`・`_material_title_index` |
| 1 | 番号ロケータのガード（アラビア数字とローマ数字。`Hymn XIV` と `Hymn CXXXV` を区別） | `_title_locators` |
| 1 | 応答系のガード（`Comment on`・`Response to`・`Reply to`・`Corrigendum`・`Erratum`・`Correction`・`Retraction` の連鎖が食い違えば `RELATED`） | `_response_chain` |
| 1 | `version_note` にだけある DOI を `NOTE_IDENTIFIER` として区別して表示（ハードゲートには入れない） | `note_dois` |
| 1 | `--author`・`--year` の補助（`AUTHOR_YEAR`、最大10件） | `_author_hit`、CLI |
| 1 | `CLEAR` に「新規の証明ではない」という注記を付け、`--json` に `advisories` を追加（既存の `status` 値は据え置き） | `check_source` |
| 2 | `20261127` 以降の新規 `research_excerpt` で、`source.title` が括弧の外で `／`・`；`・` / ` により2作品以上（各3語以上）をつなぐ場合はエラー。`version_note` に `single-work:` があれば免除 | `tools/validate_seed.py` の `check_material_source_recording`（`three_gates.py --check` からも呼ぶ） |
| 2 | `20261127` 以降の新規行で、識別子が `version_note` にしかない場合は INFO（失敗にしない） | 同上 |
| 3 | 同一資料クラスタ、ゲート後の重複、DOI 食い違いクラスタの一覧 | `python3 tools/three_gates.py --source-audit [--json]` |
| MD | `prompts/acquisition.md`、`README.md`、`prompts/close_reading_report.md`、`docs/parallel-work.md` の照合手順 | — |

連結の判定は括弧の外だけで行う。`（1909／『一隅より』1911）` のような版の併記や、`(VLN / Room-to-Room)` のような略称を誤って拒否しないためである。文学テキストは対象外とした（「巻 / 章」型の題が普通にあるため）。

### 7.2 実装後の計測（`main` 7ec44bf の台帳に対して）

| 受け入れ基準 | 結果 |
|:---|:---|
| Oostenbroek (2016) の原題 → `MAT-EVD-20261106-0c26d2` | SIMILAR_TITLE（sim=1.00、`source.title` 経由） |
| ラテン文字の `source.title` の自己想起 | 3,756 / 3,758（99.9%） |
| ゲート後の重複を、先行行だけを相手に原題で照会 | 23 / 23（`「」` 内の題を索引に加えたため、Bartlett 1932 の1行が増えた） |
| 別作品の警報ペア（§2.5 と同じ条件） | 3 組（提案時の見積もり 7 組から減少）。ローマ数字の読み取りでリグ・ヴェーダ型が、応答系ガードで OSC 2015 の3組（`RELATED` へ移動）が消えた。残りはエッダの別の歌1組と Frith の二論文（両方向で2組） |
| 1回の照会時間 | 約1.2秒（台帳 6,306 行） |
| `validate_seed.py`・`three_gates.py --check`・既存テスト | 変化なし（`tests/test_three_gates.py` に2件追加） |

`--source-audit` の出力（7ec44bf 時点）は、同一資料クラスタ 107（余分な行 124）、ゲート後の重複 23 行、2つ以上の DOI を持つクラスタ 11 である。

### 7.3 残る見落とし

`source.title` が日本語で、識別子からもたどれない行は、題名索引では届かない。例として Meltzoff & Moore (1977) は、`MAT-EVD-20261106-7e9a35`・`MAT-EVD-20261106-0c26d2` のあとに、日本語の `source.title` を持つ `MAT-20261124-191625` として三度目の収蔵をされていた（先行行には DOI がなく、一方は PMID だけ、もう一方は PDF の URL だけだったため、識別子は一致しなかった）。この型は `--author Meltzoff --year 1977` の `AUTHOR_YEAR` で収蔵前に見つかる。過去行については、同じ第一著者・同じ年を機械的に重複とみなすと別論文を大量に拾う（ゲート後の行で 107 件中、どちらかの題が日本語のものが 20 件）ため、`--source-audit` には入れず、本文での確認に委ねる。

（7.3 の見落としは §8 で扱った。）

## 8. 残る見落としの補修（2026-11-26、7.3 を受けて）

### 8.1 方針

過去の資料行は書き換えない。確認結果は `state/errata.d/` に errata 行として追記し、ツールがその行を読んで表示する（オーバーレイ型）。資料についての errata は仮説の重みを動かさない。`belief_state.py` が減点するのは、主語が仮説で判定が `contradicted` の行だけで、資料の errata は目印になるだけである。

### 8.2 source_identity errata の書き方

- 共通項目：`subject_type: "material"`、`check.kind: "manual"`、`weight_effect: "flag"`。
- `check.params.audit: "source_identity"` を置く。
- 同じ作品の行の場合：
  - `duplicate_of`：引用すべき先行行（一つ）。
  - `same_work_as`：同じ作品の、ほかの先行行。
  - 判定は `contradicted`（「新しい資料」という主張が成り立たない）、状態は `open`。
- 記録された DOI が誤っている場合：
  - `recorded_doi`：記録されている DOI。
  - `correct_doi`：Crossref で題・著者・巻・頁を確かめた DOI。
  - `verification`：照会した URL。
  - 登録の有無は doi.org の handle API（`/api/handles/<doi>`）で確かめる。取得できなければ未登録の DOI である。出版社の移管で付いた別名（HS_ALIAS）は誤りとして扱わない。
- 別の作品と確かめた場合：
  - `distinct_from` に相手の行を書く。
  - 判定は `holds`、状態は `annotated`。
- 手順：`--source-audit` で候補を出し、両方の行の `source`（title・authors・year・url・version_note）を読み比べる。そのうえで DOI を上記の方法で照合する。

ツール側の扱い：

- **`--source-audit`**：各行に `reviewed_by` を付け、未確認の件数を `unreviewed` として数える。
- **`--check-source --doi <正しい DOI>`**：`correct_doi` が一致する行も `errata.correct_doi:<doi>` として返し、`ERRAT` 行に `duplicate_of` と `correct_doi` を出す。DOI を誤って記録された行も、正しい DOI で引ける。

### 8.3 日本語題の行（今後の行）

日本語題の行は、第一著者の姓と年の一致で拾うことにした。そのうえで、日本語題の行そのものを今後は作らせない。

**`--source-audit` の `cross_language_suspects`**
- 対象：ゲート後に作られた研究資料の行のうち、第一著者の姓と年が先行行と同じで、`source.title` が片方だけ日本語の組。
- 姓の取り出し：「姓, 名」の形と、ダイアクリティカルマークに対応した。`Jr.` のような接尾辞と 1 文字の語は除く。この改善で、Swann Jr. と Janeway Jr. の組、Crespo-García と Kovacs の組の誤検知が消えた。
- 件数：20 件から 16 件になった。

**`validate_seed.py` の新しい拒否（`20261127` 以降に作られた `research_excerpt` 行）**
- 条件：著者がすべてラテン文字なのに、`source.title` が日本語の行。
- 規模：台帳全体で 621 行、20261120〜25 の行で 72 行あった。
- 例外：本当に日本語題で刊行された作品なら、`version_note` に `original-title: <理由>` と書く。著者に日本語表記がある行は対象外である。

**arXiv ID**
- `arxiv.org/abs|pdf/`、`arXiv:`、`10.48550/arXiv.` の三つの書き方を `2310.13548` の形にそろえ、識別子として扱う（`source.url` と `source_id` だけを見る）。
- 重複の拒否は `20261127` 以降の行に限る。
- これまでは DOI・PMID・PMCID しか比べていなかったため、arXiv だけで記録された同じプレプリントが重複していても止まらなかった。

### 8.4 監査の結果（`main` dd38b33 の台帳）

errata 43 行を追記した（`state/errata.d/2026-11-26-6043705bbd7f.jsonl`、`ERR-20261126-2847a7` ほか）。

| 区分 | 件数 | 内容 |
|---|---|---|
| ゲート後の重複 | 23 | すべて `duplicate_of` を記録 |
| 監査の途中で見つけた行 | 4 | Bartlett `a44ffe`、Nottebohm `73dd8c`（`60bac9` の重複）、Nottebohm `60bac9` と Koriat `8bf11f`（DOI のみ） |
| 日本語題の同一作品 | 10 | Mindblindness、Syntactic Structures、Sparrow 2011、Meltzoff 1977（三度目）、Loftus 1995、Neisser & Harsch、Waddington 1957、Tomasello 1999、Fisher 2015、Piaget 1952 |
| 別の作品と確認 | 6 | R. Klein と M. Klein など、同姓の別人や同じ著者の別論文 |

DOI の食い違い 11 クラスタを Crossref と doi.org で照合した結果：

- 誤った DOI は 11 行あった。
  - 内訳：別の論文の DOI だったもの 7 行（Dodart 2002、Kros 2002、Stickgold 2013、Salmond 2006、Grodzinsky & Santi 2009、Steels & Belpaeme 2005、Tsuchida & Fellows 2009）と、登録されていない DOI 4 行。
  - クラスタの外でも、Sparrow 2011（`3f5775`）の DOI が Crossref に登録されていなかった。正しい DOI は `10.1126/science.1207745` である。
- 誤りのない別名 DOI が 1 組あった（Hutchins 1995。`10.1016/0364-0213(95)90020-9` は `10.1207/s15516709cog1903_1` の別名）。
- 監査の途中で著者名の誤記も見つかったので、`measured_now` に残した。
  - Symons の名は Cynthia が正しい。
  - Yeshurun の名は Yaara が正しい。
  - Heersmink の名は Richard が正しい。
  - Tversky & Kahneman 1974 の第一著者は Tversky である。

追記後の `--source-audit`：

- ゲート後の重複：23 件（未確認 0）
- DOI 食い違い：11 クラスタ（未確認 0）
- 日本語題の疑い：16 件（未確認 0）

### 8.5 残り

- 7.2 の自己想起の取りこぼし 2 件と、アンソロジー容器題の誤警報は、許容した残差のままである。
- `--source-audit` の 107 クラスタのうち、ゲート後の行も DOI の食い違いも含まないものは、errata で確認していない。これらの古い重複は歴史として残し、引用するときに `--check-source` で正典となる行を選ぶ。
