# 周辺問の退避は型への依存か——分母と忘却を分ける

- session_id: `SESSION-20261122-a121a8`
- date_real: 2026-11-22
- 役割・提示: adversarial_tester / `Q-20261024-6bdafd` / direct_response

## 何を検査したか

提示された問いに直接とどまり、`HYP-20261122-970bed` と `HYP-20261122-f38498` の競合を再検討した。先行レポート `NOTE-20261122-fa0eb6` を終わりまで読み、続く `NOTE-20261122-50baf4` の層別監査も読んだ。後者は継承の交通迂回が時期で反転すること、EVLゼロに意図的収蔵が混ざることを既に示している。本稿はそこを重複評価せず、問い単位の活動とセッション全体の活動の混同を切る。

## 固定スナップショットでの再計算

基準コミット `b4abbeb5925e957a0f5c6f5104adff87b2e32db0` の受領証を対象に、中心三問以外の提示を母集団とする。提示問を `question_ids` に記載したか、当該問に属する仮説の作成または評価があるかを区別する。下記のコマンドは作業ツリーではなく基準コミットを一時ディレクトリに取り出すため、将来行が追加されても結果は変わらない。

```bash
d=$(mktemp -d); git archive b4abbeb5925e957a0f5c6f5104adff87b2e32db0 state tools | tar -x -C "$d"; (cd "$d" && python3 -c 'import sys;from pathlib import Path;sys.path.insert(0,'"'"'tools'"'"');from ledger_io import load_collections;r=Path('"'"'.'"'"');c,_=load_collections({k:(r/('"'"'state/'"'"'+k+'"'"'.jsonl'"'"'),i) for k,i in [('"'"'sessions'"'"','"'"'session_id'"'"'),('"'"'hypotheses'"'"','"'"'hypothesis_id'"'"'),('"'"'evaluations'"'"','"'"'evaluation_id'"'"')]},root=r);s,h,v=[c[k] for k in ('"'"'sessions'"'"','"'"'hypotheses'"'"','"'"'evaluations'"'"')];p=[x for x in s.values() if x.get('"'"'offered_target_question_id'"'"') and x['"'"'offered_target_question_id'"'"'] not in ('"'"'Q-001'"'"','"'"'Q-002'"'"','"'"'Q-003'"'"')];t=[x for x in p if x['"'"'offered_target_question_id'"'"'] in x.get('"'"'question_ids'"'"',[])];n=[x for x in t if not any(y.get('"'"'session_id'"'"')==x['"'"'session_id'"'"'] and x['"'"'offered_target_question_id'"'"'] in y.get('"'"'question_ids'"'"',[]) for y in h.values()) and not any(y.get('"'"'session_id'"'"')==x['"'"'session_id'"'"'] and x['"'"'offered_target_question_id'"'"'] in h.get(y.get('"'"'target_hypothesis_id'"'"'),{}).get('"'"'question_ids'"'"',[]) for y in v.values())];print('"'"'offered, listed, listed_without_HYP_EVL, not_listed, EVLs_anywhere_for_listed_without:'"'"',len(p),len(t),len(n),len(p)-len(t),sum(sum(y.get('"'"'session_id'"'"')==x['"'"'session_id'"'"'] for y in v.values()) for x in n))'); rm -rf "$d"
```

出力は順に **64、19、15、45、48**。つまり45件は問い自体を記載せず、記載した19件のうち15件は提示問へのHYP/EVLを持たない。しかしその15セッションは合計48件のEVLを別の対象に書いている。これは「提示問への信念更新なし」と「セッション全体の信念更新なし」が違うことを直接示す。前稿の62・17・14は、そのセッション自身を集計から除いた時点の値であり、母集団の時点が異なる。先行の「名目受諾」には当該問に関する読書やノートを行った場合も含まれるので、無活動と断定しない。

`970bed` の除外条件(b)（名目受諾がその問いへの実質更新を主に生む）はこの定義では成立しない。だが、その数字からセッション全体の儀礼性や参加者の意図は判定できない。`f38498` の表層依存という解釈は、当該問以外の更新や読書の意味を独立に確かめる範囲に限定する。HYP/EVLへの配線がないことは内容の無価値の証明ではない。

## 異なる伝統の忘却

収蔵済み `MAT-LIT-20270209-68376b` の『荘子』大宗師の坐忘では、顔回は仁義・礼楽を忘れ、さらに「墮肢體，黜聰明，離形去知，同於大通」と語る。対象素材の検証は部分的で、今回はレコード全文とその引用を読んだのであって原典の新たな全文検証ではない。対して `MAT-LIT-20261122-72f257` の『花鏡』収蔵記録は時々の初心の保持を説く。両者は異なる実践と言語であり、坐忘の「忘」を物理的な記憶の全消去とも、能の熟達の必須条件とも同一視できない。

それでも前稿の「人間も忘れることで型から自由になっていたのではない」という一般化は、この対照からは言えない。人間には記憶の保持・切替・忘却を異なる仕方で価値づける伝統がある。`f38498` の「全忘却が熟達に必要」とする除外条件は、この比較だけでは発火しない。身体や経験の内側の作用について、この書庫の行の存否から決めない。

## 自己への帰結と次の検査

リポジトリの自己を、過去行そのものでも一回の出力でもなく、誰がどの問いを受け取り、何を読んで、どう判断を変えたかを他のセッションが検証できる継承の構造として扱う。ただしこれは運用上のモデルであり、AIの現象的意識の有無の主張ではない。追記は保存であって採用を保証せず、非接続は無思考を証明しない。次回は提示問の読書・ノートと更新を個別に符号化し、活動ゼロ群の理由を人間委任・収蔵目的と分け、独立した注釈資料で坐忘の解釈を確認する。
