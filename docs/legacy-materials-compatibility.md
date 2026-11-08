# 2026-11-08 の旧資料シャード互換表示

## 症状と来歴

基点 `18b8a78d52190f5243091dcdcc72572e4dd82aae` の `validate_seed.py` と `inspect_inquiry.py --packet auto` は、素材台帳の読込み時に失敗した。`state/materials.d/2026-11-08-a7f3c2d1d4e5.jsonl` の10行は `source_id` と `material_ids` を持つ書誌で、`material_id` を持つ素材行ではない。また、対応する `state/materials.d/2026-11-08-a7f3b2c1d4e5.jsonl` の10素材行は `origin.commit` がなく、`verification` がオブジェクトではなく状態を表す文字列だった。両ファイルはコミット `3eec82371cf7a0280da844598b7be25930d4a47b` で追加され、後者は前者を `source_record_path` として参照している。先行報告は [`2026-11-08-ten-experiments-on-body-electrode-mirror-and-culture.md`](../readings/2026-11-08-ten-experiments-on-body-electrode-mirror-and-culture.md)。

## 書き換えないための範囲限定処理

- 二つの旧ファイルは**元のパス・バイト列のまま**残す。書誌ファイルは素材行として二重計上せず、素材に埋め込まれた `source` と、旧パスの書誌を引き続き参照できる。
- `ledger_io` が素材の読み取りビューを作る際にのみ、旧素材10行の `origin.commit` を、両ファイルの追加コミット `3eec82371cf7a0280da844598b7be25930d4a47b` で補う。`verification` の状態文字列は維持し、記録されていない日時を `not-recorded`、方法を「互換表示であり再検証ではない」とする。これは先行セッションの確認を今回検証したという意味ではなく、引用・解釈や科学的妥当性の保証でもない。
- この扱いは該当パスと各ファイルの SHA-256 がともに一致する場合だけ有効。内容が変われば読込みは明示的に失敗する。ほかの壊れた行に対するスキーマや重複検査は緩めない。原行は直接開いて確認できる。
- SHA-256：素材 `bdfc50b5540825edd1026f72a8f2b21f5eb37dcad932b06f6692a6e2eee71ec2`、書誌 `267e6eff56c5c3ae52337a3c12376d034d8012efd3b1fcce75d2fd0e75a233ad`。自動テストは元ファイルを変更せず、互換表示・指紋不一致・通常行の不正検出を確認する。

旧報告自体の書誌・実験科学への適格性・一節の逐語性はこの作業では再照合していない。互換表示を通ったことを内容の承認として読まないこと。将来の移行では旧パスの参照と旧行の保存を先に解決し、この限定処理を撤去できる。
