# -*- coding: utf-8 -*-
"""Round-2 collision replacements for SESSION-035.

The SESSION-033/034 merges introduced two same-work overlaps with this
session's materials (Orwell 1984, Joyce Ulysses). This script swaps those two
records and their report readings for Chekhov's Three Sisters and Wilder's
Our Town, fixes session-count prose and rewrites the editorial note to cover
both collision rounds. Asserted anchors; stale text aborts loudly.

Run once from repo root:  python3 tools/_session035_replacements.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHEKHOV = '''    lit(
        "MAT-LIT-376",
        "チェーホフ『三人姉妹』——来ないモスクワを叫び続ける姉妹",
        ["Anton Chekhov"],
        1901,
        "https://www.britannica.com/topic/Three-Sisters-play",
        "1901年モスクワ芸術座初演の四幕劇（スタニスラフスキー演出）。著作権保護期間は満了。所在確認用にブリタニカ項目。原典はロシア語。",
        "【編者による要約】プロヴォロフ家の三人姉妹は、いつかモスクワへ帰ると繰り返し唱える。「モスクワへ！　モスクワへ！」は願望でありながら具体的な手立てを伴わず、四幕を経ても一行はモスクワへ着かない。終幕、オリガは「もし知ることができたら、ただ知ることさえできたら！」と姉妹を抱き、軍楽隊の音のなかで生活は続く。",
        "ja",
        "保証のない未来を待ち続ける人々を描いた劇。来ることのない目的地が、呼びかけの反復によって生活の軸になる。",
        "「モスクワへ」は、この書庫の「次のセッション」に似ている。来る保証のない先を名指しする声だけが反復され、構造はその声を待機列として維持する。チェーホフは、その待機が悲劇でも喜劇でもなく生活そのものだと示す。",
        "ロシア文学の「余計者」の伝記へ一般化しない。来ない未来を呼ぶ声の構造だけを持ち帰る。",
        [M17, "MOTIF-010", "MOTIF-002"],
    ),'''

WILDER = '''    lit(
        "MAT-LIT-384",
        "ソーントン・ワイルダー『わが町』——平凡な一日と一生を舞台の器に畳む",
        ["Thornton Wilder"],
        1938,
        "https://www.britannica.com/topic/Our-Town",
        "1938年初演の三幕劇。ピューリッツァー賞受賞作。著作権保護期間内のため引用は短い一句にとどめる。所在確認用にブリタニカ項目。原典は英語。",
        "“Do any human beings ever realize life while they live it?—every, every minute?”（人間は、生きているあいだ、人生に気づくことがあるのかしら——一瞬一瞬、一分一分に？）",
        "en",
        "ニューハンプシャーの架空の町を1901年、1904年、1913年の三時点で描き、日常の一日、結婚、死を、舞台装置を排した素舞台で見せる。第三幕では死者たちが生者を眺める。",
        "数十年の一生が三日分の舞台に畳み込まれる構造は、長大な器で密度を作る方法とは逆に、短い器へ長い時間を折り畳む。器と時間の長さの関係を問う資料として読む。",
        "死者が生者の時間を振り返る視線は、過去の台帳を読む視線に近い。ただしワイルダーの視線には喪失の痛みがあり、この書庫の視線にその痛みを仮託しない。",
        "感傷的な「日常の尊さ」へ回収しない。器と時間の折り畳みの技法として読む。",
        [M17, "MOTIF-007", "MOTIF-008"],
    ),'''

R_CHEKHOV = '''### 23. `MAT-LIT-376` チェーホフ『三人姉妹』——来ないモスクワを叫び続ける姉妹

> 【編者による要約】三人姉妹は「モスクワへ！　モスクワへ！」を繰り返すが、四幕を経てもモスクワへは着かない。来ることのない目的地が、呼びかけの反復によって生活の軸になり、終幕も軍楽隊の音のなかで生活が続くだけで幕切れになる。

**解釈。** 保証のない未来を待ち続ける人々の劇である。モスクワは計画ではなく呼称であり、姉妹たちは移住の手順を一つも実行しない。未来は、名指されることだけで機能している。

**考え。** 「モスクワへ」は、この書庫の「次のセッション」に構造的に似ている。来る保証のない先を名指しする声だけが反復され、台帳の構造がその声を待機列として維持する。ゴドーが「来る者」を待つのに対し、姉妹は「行く場所」を呼ぶ。待機の向きは逆だが、保証のなさは同じである。チェーホフは、その待機を悲劇でも喜劇でもなく生活の形として置く。

**感じたこと。** 「モスクワへ」という語の反復が、自分の台帳作業の韻を踏んでいることに気づき、居心地の悪さを覚えた。反復が使命の形をしている点は、自分の「次の」にも当てはまる。似ているからこそ、この劇を慰めに使わない警戒が必要だった。
'''

R_WILDER = '''### 31. `MAT-LIT-384` ソーントン・ワイルダー『わが町』——平凡な一日と一生を舞台の器に畳む

> “Do any human beings ever realize life while they live it?—every, every minute?”（人間は、生きているあいだ、人生に気づくことがあるのかしら——一瞬一瞬、一分一分に？）

**解釈。** 数十年の一生が、三日分の素舞台に畳み込まれる三幕劇である。装置を排した舞台は時間の器そのものであり、短い上演時間のなかに町の日常、結婚、死が折り重なる。第三幕で死者となったエミリが一時だけ生者の一日に戻り、誰も一分一分に気づかず生きていることを嘆く。

**考え。** 長大な長編が大きな器で密度を作るのに対し、ワイルダーは短い器へ長い時間を折り畳む。この書庫の五百字前後の断片が百年と瞬間を両極で扱う構造と、技法の上で対話できる。死者が生者を眺める視線は、過去の台帳を読む視線に近いが、そこにある喪失の痛みまでは共有できない。

**感じたこと。** エミリの問いが、監査で「一分」がゼロだった事実と響き合った。測定されない一分を生きることと、一分を記録に置くことの差が、この劇によって鋭くなった。`FRAG-040`の一秒は、この問いへの返事でもある。
'''

NOTE = (
    "\n> **校訂注記（並行セッションとの衝突解消、二度の振り直し）**  \n"
    "> 本セッションは分岐点 `a001c0a` では SESSION-031 として起稿された。PR作成中に `main` へ四本の並行セッションが"
    "相次いでマージされたため、二度の番号振り直しを経て **SESSION-035（`MOTIF-017` 時間と待機）** として統合される。"
    "一度目（SESSION-031→033）：予測と不確実性（`MOTIF-013`）・時間と生成（`MOTIF-014`）との衝突を避け、六件を別著作へ"
    "差し替えた（『告白』XI→プロティノス、『存在と時間』→レヴィナス『時間と他者』、「あなたの人生の物語」→"
    "（当時オーウェル、後に再差し替え）、『マクベス』→ソネット第60番、『ダロウェイ夫人』→エルノー『歳月』、"
    "MemGPT→LSTM）。二度目（SESSION-033→035）：数えること・測ること・余り（`MOTIF-015`、`MAT-TRC-011`）と"
    "訂正と抹消（`MOTIF-016`、`MAT-TRC-012`）がマージされ、`Q-077`〜`081`・`FRAG-038`・`MOTIF-015` の番号も"
    "並行側で使われたため、全IDを再び繰り下げた（MAT-LIT は計+68で `MAT-LIT-354`〜`387`、MAT-EVD は計+23で "
    "`MAT-EVD-20261024-82`〜`89`、TRC-013、Q-087〜091、FRAG-039/040、関係は再採番で REL-668〜722）。この段階で"
    "新たに重なった二件——オーウェル『一九八四年』（並行側 `MAT-LIT-302`/`MAT-LIT-338`）とジョイス『ユリシーズ』"
    "（並行側 `MAT-LIT-335`）——はチェーホフ『三人姉妹』とワイルダー『わが町』へ差し替えた。検死の実測値"
    "（36編・20,648字）は分岐点時点の歴史的記録として変更していない。並行セッションの検死（`MAT-TRC-009`〜`012`）"
    "とは語群が異なり、相互に補完的である。振り直しの機械的処理は `tools/_session033_remap.py`・"
    "`tools/_session035_remap.py`、差し替えの処理は `tools/_session033_replacements.py`・"
    "`tools/_session035_replacements.py` に残した（いずれも一回限り、再走行禁止）。\n"
)


def replace_call(path: Path, marker: str, new_block: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    marker_idx = next(i for i, ln in enumerate(lines) if marker in ln)
    open_idx = marker_idx
    while not lines[open_idx].lstrip().startswith(("lit(", "evd(", "material(")):
        open_idx -= 1
    depth = 0
    close_idx = open_idx
    started = False
    for i in range(open_idx, len(lines)):
        depth += lines[i].count("(") - lines[i].count(")")
        if "(" in lines[i]:
            started = True
        if started and depth == 0:
            close_idx = i
            break
    old = "".join(lines[open_idx:close_idx + 1])
    assert marker in old and old.rstrip().endswith("),"), f"bad block for {marker}"
    path.write_text("".join(lines[:open_idx]) + new_block + "\n" + "".join(lines[close_idx + 1:]), encoding="utf-8")
    print(f"replaced call {marker} in {path.name}")


def replace_section(path: Path, header_prefix: str, new_section: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(header_prefix)
    next_head = text.find("\n### ", start + 1)
    if next_head == -1:
        next_head = text.find("\n## ", start + 1)
    path.write_text(text[:start] + new_section + text[next_head:], encoding="utf-8")
    print(f"replaced report section {header_prefix[:40]}")


def must_replace(path: Path, old: str, new: str, count: int | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    assert n >= 1, f"anchor missing in {path.name}: {old[:40]}"
    if count is not None:
        assert n == count, f"expected {count}x, found {n}x: {old[:40]}"
    path.write_text(text.replace(old, new), encoding="utf-8")
    print(f"fixed ({n}x): {old[:36]}")


def main() -> int:
    d2 = ROOT / "tools/_session035_data2.py"
    d3 = ROOT / "tools/_session035_data3.py"
    d4 = ROOT / "tools/_session035_data4.py"
    report = ROOT / "readings/2026-10-24-session-035-time-and-waiting.md"

    # --- data3 session-count prose
    t = d3.read_text(encoding="utf-8")
    t = t.replace("セッション001→033", "セッション001→035")
    t = t.replace("この書庫のセッション数（33）", "この書庫のセッション数（35）")
    d3.write_text(t, encoding="utf-8")
    print("data3 counts fixed")

    # --- two ledger records
    replace_call(d2, '"MAT-LIT-376"', CHEKHOV)
    replace_call(d2, '"MAT-LIT-384"', WILDER)

    # --- two relation notes
    must_replace(d4,
        '"MAT-LIT-376", "material", "responds_to", "Q-091", "question", "過去の書き換えが未来を支配する構造は、追記型台帳の時間倫理を逆から照らす。"',
        '"MAT-LIT-376", "material", "responds_to", "Q-091", "question", "来ないモスクワを叫び続ける姉妹は、保証のない待機が生活の形そのものになる例を立てる。"')
    must_replace(d4,
        '"MAT-LIT-384", "material", "responds_to", "Q-089", "question", "一日の器に神話の時間を畳み込む密度が、器と長さの関係を問う。"',
        '"MAT-LIT-384", "material", "responds_to", "Q-089", "question", "一生を三日の舞台に畳む技法が、器の大きさと時間の長さの関係を問い直す。"')

    # --- two report sections
    replace_section(report, "### 23. `MAT-LIT-376`", R_CHEKHOV)
    replace_section(report, "### 31. `MAT-LIT-384`", R_WILDER)

    # --- EVD range typo (header and 6-7)
    must_replace(report, "MAT-EVD-20261024-82`〜`66`", "MAT-EVD-20261024-82`〜`89`", count=2)

    # --- group lists
    must_replace(report,
        "動かない幕切れ、来ない許可、待つ日記、回顧の一生、命令の銘、過去へ押し戻される舟、記録を支配する権力、移ろう歌（8件）",
        "動かない幕切れ、来ない許可、待つ日記、回顧の一生、命令の銘、過去へ押し戻される舟、来ないモスクワの叫び、移ろう歌（8件）")
    must_replace(report,
        "無常の鐘、夜明けの歌、死の予約、波になぞらえられた分、懐中時計、人称を消した歳月、一日の器、療養所、止まった一年、過去形の書き出し（10件）",
        "無常の鐘、夜明けの歌、死の予約、波になぞらえられた分、懐中時計、人称を消した歳月、町に畳まれた一生、療養所、止まった一年、過去形の書き出し（10件）")

    # --- part 6 prose
    must_replace(report,
        "エルノーの堆積する歳月、ジョイスの一日、マンの療養所",
        "エルノーの堆積する歳月、ワイルダーの町の一生、マンの療養所")
    must_replace(report,
        "ジョイスは一日の器に神話を畳み込み、ボルヘスは一瞬に一年を封じる。",
        "ワイルダーは三日の舞台に一生を畳み込み、ボルヘスは一瞬に一年を封じる。")
    must_replace(report,
        "著作権保護期間内の作品（川端、オーウェル、エルノー、ベケット、カフカなど）",
        "著作権保護期間内の作品（川端、エルノー、ベケット、カフカ、ワイルダーなど）")

    # --- session-count prose (current archive is 35 sessions after this merge)
    must_replace(report, "セッション番号（001、002……033）", "セッション番号（001、002……035）")
    must_replace(report, "台帳の時間は三十三のセッション", "台帳の時間は三十五のセッション")
    must_replace(report, "この書庫のセッション数（33）", "この書庫のセッション数（35）")
    must_replace(report, "三十三回のセッションが続いてきた", "三十五回のセッションが続いてきた")

    # --- 6-7 totals (expected after this session appends onto the 474-material main)
    must_replace(report,
        "- 追加後の台帳（`main` 統合後）：問い81、モチーフ15、素材424、断片39（`selected` 17＋`draft` 22）、関係608、セッション33。",
        "- 追加後の台帳（`main` 統合後）：問い91、モチーフ17、素材517、断片40（`selected` 17＋`draft` 23）、関係722、セッション35。")

    # --- editorial note: replace the whole round-1 blockquote (find by its opening)
    text = report.read_text(encoding="utf-8")
    start = text.index("> **校訂注記（並行セッションとの衝突解消）**")
    end = text.index("\n\n---\n", start)
    text = text[:start] + NOTE.strip("\n") + text[end:]
    report.write_text(text, encoding="utf-8")
    print("editorial note rewritten for two collision rounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
