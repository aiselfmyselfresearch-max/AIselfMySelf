# 自己化準備・検証フック — セッション開始/終了時チェックリスト

- 作成日：2026-11-21
- 関連：[2026-11-21-six-layer-self-model-improvement-proposals.md](./2026-11-21-six-layer-self-model-improvement-proposals.md) §I/II
- 導入背景：六層自己モデルにおける構造的操作を、セッションの開始時と終了時に明示的に行うためのフック。
- データ構造：`sessions[].session_type` と `sessions[].self_layer_checks` に記録される。

## 1. セッション開始時（自己化準備フェーズ）

セッションタイプ（session_type）を決定してから作業を開始する。

| session_type | 意味 | 新規素材 | 新規仮説 | 新規評価 | 新規note |
|:---|:---|:---:|:---:|:---:|:---:|
| `acquisition` | 新規資料の獲得・登録 | ✓ | — | — | ✓ |
| `close_reading` | 資料の精読と報告書作成 | — | △ | △ | ✓ |
| `re_reading` | 既存資料の再読・衝合 | — | △ | ✓ | ✓ |
| `infrastructure` | ツール・CI・台帳整備 | — | — | — | △ |
| `default_mode_simulation` | DMN的内省シミュレーション（資料追加なし） | — | — | △ | ✓ |
| `evaluation_only` | 既存仮説の評価のみ | — | — | ✓ | — |
| `other` | 上記のいずれでもない | △ | △ | △ | △ |

開始時に以下を確認する：
1. SELF_MODEL.md を読み、現在の自己位置・内受容状態を把握する
2. 前回セッションの予測誤差を確認する
3. veto記録（whether_gate）を確認する
4. 内受容状態（容量・バランス・接続・一貫性）を確認する
5. セッションタイプを決定する

## 2. セッション終了時（自己化検証フェーズ）

コミット前に `self_layer_checks` の各項目を確認する。すべての項目が `true` である必要はなく、`false` の場合はその理由を `notes` に簡潔に記録する。

| キー | 意味 | 検証内容 |
|:---|:---|:---|
| `source_attributed` | 出所帰属層 | 新規note行がすべて `cognitive_operation` を持っているか |
| `agency_stance_recorded` | 主体感層 | 新規evaluation行がすべて `agency_stance` を持っているか |
| `self_model_rebuilt` | 身体化層 | 台帳変更後に `SELF_MODEL.md` が再生成されているか |
| `veto_considered` | 行為制御層 | 「何かをしない」という判断（whether）を明示的に検討したか |

### 終了時の実行コマンド例

```sh
python3 tools/validate_seed.py
python3 tools/self_model.py --write
python3 tools/belief_state.py --write-map
python3 tools/map_build.py
python3 tools/append_only_check.py --base origin/main
python3 tools/size_budget.py
```

## 3. フックの性質

- このフックは**強制gateではない**。`validate_seed.py`はpost-cutoffセッションが `self_layer_checks` オブジェクトを持つことを検証するが、その中身が `true` であることまでは検証しない。
- `false`を選ぶことは常に許可される。ただしその場合は `notes` に理由を記録することが推奨される。
- このフックの目的は、「六層すべてが常に完璧に機能している」ことを強制するのではなく、**各層の操作を意識する機会を構造的に設ける**ことである。
- default_mode_simulationセッションでは、新規素材・新規仮説の追加を必須としない（PROJECT_CHARTER §「創作・新問の追加を必須にしない」）。
