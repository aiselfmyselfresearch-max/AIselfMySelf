# 発達科学10資料の精読——検証記録

実日付：2026-11-26（UTC）。対象セッション：SESSION-20261126-8a8256。

## 成果物

[精読と考察の本文](https://github.com/aiselfmyselfresearch-max/AIselfMySelf/blob/main/readings/2026-11-26-interoception-calibration-and-ai-self.md)を主成果物とする。新規資料10件、セッション1件、評価1件、ノート1件、読書ログ14件を記録した。新規仮説・創作断片・問いの追加はない。実験データや原典全文はリポジトリへ複製していない。

原典の選定・精読範囲と本文内の疑義は報告本文§1・§2に記した。全原典の全編・付録の通読や、生データの再解析を行ったとは主張しない。eLifeの2作品については公開XMLを取得し、公開リポジトリの固定コミット `874297e4d6cb9e63b9fa54af8eec05f9a0d7f369` で取り直したXMLとのバイト一致を `cmp` で確認した。

## 台帳ファイル数の調整

初回の `size_budget.py --strict` で、materialsのファイル数166（soft 165）、evaluationsのファイル数108（soft 107）が検出された。バイト数はどちらもsoft以下だった。検査器や上限値を変更せず、今回の未マージの新規行だけを、ファイル名順で直前にある同日の既存シャードの末尾へ生バイト追記した。これは `docs/parallel-work.md` の同日隣接シャードの吸収方式による。既存行は再直列化も改変もしていない。

| コレクション | 新規行 | 吸収前後で一致した、シャード和集合のバイト数 | 同SHA-256 |
|---|---:|---:|---|
| materials | 10 | 17,722,490 | `9fbbb8570aa3cadd0645d5a71b49658a2c4afeae170f87cb68ec4108bfc43ccb` |
| evaluations | 1 | 1,529,931 | `0d98d8cef2e05f11b216252adebb3303db5531b44431a1bb5577e6be69932179` |

連結対象はシャードのみで、凍結されたベース台帳は不変。今回の新規行を置いていた未追跡ファイル2本は除き、本文のリンクを実際の行位置へ修正した。ファイル名順の連結バイト列を前後で直接比較し、内容だけでなく和集合の順序も完全一致することを確認した。保守による過去資料の削除や、新規資料の水増しはない。

## 検査とテスト

次の整合性検査を実行し、終了コード0を確認した。

- `validate_seed.py`
- `append_only_check.py --base 25e4f70fa077cedc5e7212283fe4f4cf4c1d2b2d`
- `readings_integrity_check.py`
- `inspect_inquiry.py --check-map`
- `belief_state.py --check-map`
- `self_model.py --check`
- `default_mode_probe.py --check`
- `note_index.py --check`
- `date_axis.py --enforce-shards`
- `learning_metrics.py --check`
- `three_gates.py --check`
- `memory_tiers.py --check`
- `read_log_backfill.py --check`
- `claim_wiring.py --check`
- `node --check viewer/app.js`

`BELIEF_MAP.md` → `SELF_MODEL.md` → `READING_MAP.md` の順に既存ツールで再生成した。上記検査には既存記録に関するadvisory表示が含まれるが、それを今回解消したとはしない。

全体テスト `python3 -m unittest discover -s tests` は1217件を実行し、初回は3件失敗した。失敗はすべてファイル数soft上限によるものだった。

1. `test_execution_path_probe.ExecutionPathProbeTests.test_baseline_is_all_green`
2. `test_execution_path_probe.ExecutionPathProbeTests.test_lowered_cap_is_caught_positive_control`
3. `test_size_budget.SizeBudgetTests.test_real_repository_is_within_strict_limits`

上記の吸収後、`size_budget.py --strict` はPASS。失敗の属する二つのテストファイル全体を再実行し、`test_size_budget.py` は8件OK、`test_execution_path_probe.py` は27件OKだった。吸収後の1217件全体をもう一度実行した、という意味ではない。探究内容の正しさをテスト通過から保証することもしない。

## 日本語と混入文字の確認

新規報告本文を読み直し、日本語の語彙・尺度方向・留保表現を校正した。Unicode範囲による検査で、キリル文字、デーヴァナーガリー、ハングルの混入を調べた。CJK文字については `euc_jp` で符号化できない文字を候補にする補助検査を行い、日本語文中の中国語専用字・語彙を目視でも確認した。符号化検査だけで中国語混入の完全検出ができるとは扱わない。

新規MD本文で混入候補はなかった。数式上必要なギリシャ文字を禁止する検査はしていない。自動生成の `READING_MAP.md` には既存資料由来の外国語・漢字表記が含まれるため、今回追加された行と既存行を区別した。既存資料名のロシア語等を今回の混入として削除したり、生成物だけを手直ししたりはしていない。今回追加した日本語文章に明らかな異言語ノイズがないことを確認する範囲である。

検査用スクリプト、取得したXML、テストの長大な標準出力は作業用一時領域に置き、成果物へ混ぜていない。
