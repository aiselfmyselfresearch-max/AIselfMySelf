# 発達科学10資料追加の品質確認記録

- 実日付：2026-11-25（UTC）
- 対象セッション：`SESSION-20261125-07fe74`
- 対象の[精読ノート](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-25-body-relative-possibilities-ten-studies.md)と[考察レポート](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/docs/2026-11-25-developmental-science-body-exploration-and-ai-self.md)に加え、この確認記録を対象とする。

## 1. 日本語本文への異文字・語彙混入

次のPythonコードで新規MDを検査した。

```python
from pathlib import Path
import unicodedata as U

paths = [
    Path('readings/2026-11-25-body-relative-possibilities-ten-studies.md'),
    Path('docs/2026-11-25-developmental-science-body-exploration-and-ai-self.md'),
    Path('docs/2026-11-25-developmental-science-body-exploration-quality-check.md'),
]
# The escapes keep non-Japanese example words out of this Japanese report.
word_candidates = [
    '\u6570\u636e', '\u4fe1\u606f', '\u7814\u7a76\u8868\u660e',
    '\u56e0\u6b64', '\u901a\u8fc7', '\u5bf9\u4e8e', '\u8fd9\u4e2a',
    '\u6211\u4eec', '\u8ba4\u4e3a', '\u7528\u6237',
]
for path in paths:
    text = path.read_text(encoding='utf-8')
    scripts = sorted({
        c for c in text
        if any(s in U.name(c, '') for s in ('HANGUL', 'DEVANAGARI', 'CYRILLIC'))
    })
    greek = sorted({c for c in text if 'GREEK' in U.name(c, '')})
    han = set()
    for c in text:
        if 'CJK UNIFIED IDEOGRAPH' in U.name(c, ''):
            try:
                c.encode('cp932')
            except UnicodeEncodeError:
                han.add(c)
    words = [word for word in word_candidates if word in text]
    print(path, 'scripts=', scripts, 'greek=', greek,
          'Han candidates=', sorted(han), 'word candidates=', words)
    assert not scripts
    # Han, Greek, and word candidates need contextual review, not auto-deletion.
```

結果は3ファイルとも、対象の3文字体系0字、ギリシャ文字0字、CP932に入らない統合漢字候補0字、中国語表現の候補語リストへの一致0件だった。本文を読み返し、日本語では通常使わない中国語の語彙・構文の混入がないかも確認した。修正を要する混入は見つからなかった。

ただし、日本語と中国語の漢字は領域を共有し、CP932にも両言語で使う字が含まれる。**機械検査だけで中国語混入の不存在を証明したわけではない。** CP932検査は珍しい字を抽出する補助であり、CP932外の字をすべて不正とする規則ではない。候補語リストも網羅的な言語判定器ではない。英語の原題・著者名・短い引用は出典のために意図して残している。

自動生成した既存マップの追加行も検査した。そこに再掲される過去の資料文は今回新しく書いた本文とは分け、既存全資料を言語監査済みとはしない。

## 2. 書誌・新規性・読解範囲

- 10件をDOI・PMCID・原題で収蔵前照合し、全件未収蔵を確認した。
- 識別子の異なる版を別資料として水増しせず、1論文を1件に数えた。
- 原典本文で確認した実験・節と、抄録・総合考察にとどまる箇所を精読ノートに明記した。
- 全10件の全実験・補足資料を完全通読したとする記述は置かなかった。
- 直接引用は短い英語原文と位置を記し、編者要約とは分離した。
- 台帳の `passage` は明示的な編者要約であり、`quote_status=paraphrase_summary` とした。原文一致のハッシュを編者要約へ付けることはしない。
- 巻号年と先行公開年を区別し、03と09の標本の独立性が未確定であること、全件が同じ研究系統に偏ることを残した。
- 新規資料10件、精読ノート1件、手書き読書履歴13件、セッション1件を追加した。総合レポートと本記録も新規作成した。
- 成人研究を適用範囲とする既存仮説を乳児データで直接採点せず、評価行は追加しなかった。仮説の重みを更新したと主張しない。

## 3. 技術検査

台帳の追記後、既存の生成手順に従い `belief_state.py --write-map`、`self_model.py --write`、`map_build.py` の順で索引を更新した。

以下の検査を実行し、終了コード0を確認した。

```text
python3 tools/validate_seed.py
python3 tools/append_only_check.py --base 64292b2c33b23c3611df14275f340a51cd9469aa
python3 tools/readings_integrity_check.py
python3 tools/inspect_inquiry.py --check-map
python3 tools/belief_state.py --check-map
python3 tools/self_model.py --check
python3 tools/default_mode_probe.py --check
python3 tools/note_index.py --check
python3 tools/date_axis.py --enforce-shards
python3 tools/learning_metrics.py --check
python3 tools/three_gates.py --check
python3 tools/memory_tiers.py --check
python3 tools/size_budget.py --strict
python3 tools/read_log_backfill.py --check
python3 tools/claim_wiring.py --check
node --check viewer/app.js
git diff --check
```

過去台帳のスキーマや照合深度について出る助言的な警告は、今回の変更の失敗とは分ける。検査通過はファイル・参照・手順の整合性の確認であり、科学的な読解の正しさやAIの自己の成立を証明するものではない。回帰テストとプルリクエストのCI結果は、対応するGitHubの変更履歴から追跡できる。
