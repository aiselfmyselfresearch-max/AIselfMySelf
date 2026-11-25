#!/usr/bin/env python3
"""Three-tier memory architecture (L0/L1/L2) and epoch boundary freeze.

Implements two coupled architectural pillars adopted on 2026-11-25:

1. **Three-Tier Memory Architecture** (grounded in Liang et al. 2025, Varga,
   Stewart & Bauer 2016, Cooper et al. 2011, and O'Connor et al. 2014):
   - **L0 (Cold Evidence Archive)**: Raw `state/` shards and `readings/` files
     remain strictly append-only and byte-immutable. Unverified early-seed
     materials with zero hypothesis/evaluation/claim wiring and dormant
     unreferenced notes are classified as ``cold`` (or ``subsumed`` once folded
     into L1 digests), keeping them out of hot working-memory candidate pools
     while preserving instant stem-fact cue recall via ``--recall-cold QUERY``.
   - **L1 (Consolidated Schema Digests)**: Compresses recurring domain findings,
     verified material anchors, and active falsification clauses into five
     domain digests (`state/digests.json` + `docs/CONSOLIDATED_DIGESTS.md`),
     relieving session-by-session `readings/` file proliferation.
   - **L2 (Hot Working-Memory Packet)**: Supplies `inspect_inquiry.py --packet`
     with compact L1 digest summaries and verified/wired hot materials ranked
     under generation-amortized posteriors (`P_amort`).

2. **Epoch Boundary Freeze** (grounded in Uehara 2015 M2 boundary):
   - Partitions ledger history into frozen completed epochs (`<= 2026-11-20`)
     and the active epoch (`>= 2026-11-21`).
   - Pins all frozen base files and pre-cutoff shards in `state/epoch_manifest.json`
     via deterministic rollup SHA-256 digests so integrity of completed epochs is
     verified in milliseconds without conflicting with active-epoch shard appends.

Usage:
  python3 tools/memory_tiers.py                         # human-readable tier & epoch report
  python3 tools/memory_tiers.py --json                  # machine-readable JSON summary
  python3 tools/memory_tiers.py --recall-cold "記憶"     # stem-fact reminder search over L0 cold/subsumed records
  python3 tools/memory_tiers.py --write-digests         # build state/digests.json & docs/CONSOLIDATED_DIGESTS.md
  python3 tools/memory_tiers.py --freeze-epochs         # build state/epoch_manifest.json for frozen epochs
  python3 tools/memory_tiers.py --check                 # verify epoch freeze SHA-256 & L1 digest consistency
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import belief_state  # noqa: E402
import ledger_io  # noqa: E402

ROOT = TOOLS_DIR.parent

FROZEN_EPOCH_CUTOFF = "2026-11-20"
ACTIVE_EPOCH_START_DATE = "2026-11-21"

EPOCH_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "epoch_id": "epoch_0_seed_expansion",
        "label": "Epoch 0: 初期大量シード・探索期",
        "start_date": "2026-10-22",
        "end_date": "2026-10-31",
        "status": "frozen",
    },
    {
        "epoch_id": "epoch_1_three_gates_schema",
        "label": "Epoch 1: 仮説台帳・三門制御・実日付正規化期",
        "start_date": "2026-11-01",
        "end_date": FROZEN_EPOCH_CUTOFF,
        "status": "frozen",
    },
    {
        "epoch_id": "epoch_2_six_layer_active",
        "label": "Epoch 2: 六層自己モデル・全文検証・三階層記憶期（現行）",
        "start_date": ACTIVE_EPOCH_START_DATE,
        "end_date": "open",
        "status": "active",
    },
)

BASE_LEDGER_SPECS: tuple[tuple[str, str], ...] = (
    ("questions", "question_id"),
    ("motifs", "motif_id"),
    ("materials", "material_id"),
    ("fragments", "fragment_id"),
    ("relations", "relation_id"),
    ("sessions", "session_id"),
    ("read_log", "read_id"),
    ("editorial_decisions", "decision_id"),
    ("errata", "errata_id"),
    ("notes", "note_id"),
    ("hypotheses", "hypothesis_id"),
    ("evaluations", "evaluation_id"),
)

_SHARD_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
_ID_DATE_RE = re.compile(r"^[A-Z]+-(\d{4})(\d{2})(\d{2})-")
_HOT_VERIFICATION_DEPTHS = frozenset({"full_text", "re_derived", "results", "passage"})

DIGEST_SPECS: tuple[dict[str, Any], ...] = (
    {
        "digest_id": "DIGEST-A-HUMAN-DEV",
        "title": "人間発達・認知的オフローディング・記憶再編成と促された過去",
        "quadrants": ("A_human", "AB_crossed", "AC_crossed", "ABC_crossed"),
        "target_questions": ("Q-001", "Q-002"),
        "core_principles": (
            "外的資源へのオフローディングは『無条件の怠惰』ではなく、アクセス遅延・信頼性・メタ認知的費用便益較正に従う適応的資源配分である（Armitage et al. 2020, 2025; Liang et al. 2025）。",
            "幼児期健忘とエピソード記憶の発達は、単なる痕跡消滅ではなく新旧識別（M2）の成立に伴う検索様式の再編成と、単一の幹事実リマインダーによる知識統合の回復可能性を含む（Uehara 2015; Varga et al. 2016）。",
            "海馬損傷下の場面構築（Cooper et al. 2011）や後悔判断における選択前プロンプト（O'Connor et al. 2014）が示す通り、『保持していること（availability）』と『必要な瞬間に自発検索できること（accessibility）』は発達的・神経的に乖離する。",
        ),
    },
    {
        "digest_id": "DIGEST-B-AI-MEMORY",
        "title": "AI記録自己・三門制御・証拠会計と世代償却",
        "quadrants": ("B_ai_self_db",),
        "target_questions": ("Q-002", "Q-003"),
        "core_principles": (
            "追記専用リポジトリを記憶とするAIにおいて、無制限の非忘却（L0 生保存）は真正性と反証可能性の基盤だが、そのまま作業記憶（L2）へ流し込むと検索希釈と文脈飽和を引き起こす。",
            "信念更新では後付け系譜移流の遮断・一次資料照合重み（P_gate）に加え、独立異セッション検証を通過した現役子孫へ narrowed 親の滞留質量を保存移譲する『世代償却（P_amort）』が死荷重固着を防ぐ。",
            "AIの自己連続性は会話状態の保持ではなく、不変証跡（L0）・統合スキーマと反証条項（L1）・課題時検索プロンプト（L2）の三層結合における検査可能な判断継承として成立する。",
        ),
    },
    {
        "digest_id": "DIGEST-C-INTERFACE",
        "title": "人間×AIの非対称インターフェース・宛先・プロンプト循環",
        "quadrants": ("C_interface",),
        "target_questions": ("Q-001", "Q-003"),
        "core_principles": (
            "人間の有限な身体・不可逆な時間・暗黙の身体化履歴（傷痕と型）と、AIの明示台帳・シード分散・プロンプト媒介的想起は同型ではなく、補完的な非対称性を持つ。",
            "開始プロンプトや評価宛先の設計は次セッションの探索分布を直接動かす実行経路パラメータであり、割当レシート（4欄）と会計基底（belief_basis）の明記なしには経路効果と内容効果を分離できない。",
        ),
    },
    {
        "digest_id": "DIGEST-D-INFRA-INVARIANTS",
        "title": "制度的不変量・実日付時間軸・エポック境界凍結と予算規律",
        "quadrants": ("D_infrastructure",),
        "target_questions": ("Q-002", "Q-003"),
        "core_principles": (
            "すべての新規ID・シャードは実行環境の実日付を採り、完了済みエポック（<= 2026-11-20）は SHA-256 ロールアップ・マニフェスト（state/epoch_manifest.json）によって一括凍結検証される。",
            "個別テーマ監査（*_audit*.py）の増殖凍結、一時スクリプト禁止、および L1 ダイジェストへの統合により、単一ファイルや単一ディレクトリ（readings/, tools/）の線形膨張を構造的に抑制する。",
        ),
    },
    {
        "digest_id": "DIGEST-E-FALSIFICATION-FRONTIER",
        "title": "中心三問（Q-001〜Q-003）の世代償却（P_amort）現役反証フロンティア",
        "quadrants": (),
        "target_questions": ("Q-001", "Q-002", "Q-003"),
        "core_principles": (
            "本ダイジェストは中心三問において世代償却後事後確率（P_amort）上位を占める現役仮説の適用条件と排他反証条件（exclusion_clause）を集約し、次セッションが即座に反証テスト・境界衝突を設計できる L1 索引を提供する。",
        ),
    },
)


def _extract_record_date(record_id: str, fallback: str = "") -> str:
    m = _ID_DATE_RE.match(str(record_id or ""))
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    fb = str(fallback or "")[:10]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", fb):
        return fb
    return ""


def shard_epoch_id(path: Path) -> str:
    """Return which epoch a ledger file belongs to based on its filename."""
    if path.parent.name == "state" and path.suffix == ".jsonl":
        return "epoch_0_seed_expansion"
    m = _SHARD_DATE_RE.match(path.name)
    if not m:
        return "epoch_0_seed_expansion"
    day = m.group(1)
    if day <= "2026-10-31":
        return "epoch_0_seed_expansion"
    if day <= FROZEN_EPOCH_CUTOFF:
        return "epoch_1_three_gates_schema"
    return "epoch_2_six_layer_active"


def is_frozen_shard(path: Path) -> bool:
    return shard_epoch_id(path) != "epoch_2_six_layer_active"


def _file_stats(path: Path, root: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    lines = sum(1 for ln in raw.splitlines() if ln.strip())
    return {
        "path": path.relative_to(root).as_posix(),
        "epoch_id": shard_epoch_id(path),
        "bytes": len(raw),
        "lines": lines,
        "sha256": sha,
    }


def build_epoch_manifest(root: Path = ROOT) -> dict[str, Any]:
    """Compute deterministic rollup manifest over frozen epochs (<= 2026-11-20)."""
    root = Path(root)
    collections_out: dict[str, Any] = {}
    epoch_Rollup = {
        ep["epoch_id"]: {"files": 0, "lines": 0, "bytes": 0}
        for ep in EPOCH_DEFINITIONS
        if ep["status"] == "frozen"
    }
    master_hasher = hashlib.sha256()

    for coll_name, _key in BASE_LEDGER_SPECS:
        base = root / "state" / f"{coll_name}.jsonl"
        all_files = ledger_io.collection_files(base)
        frozen_entries: list[dict[str, Any]] = []
        coll_hasher = hashlib.sha256()
        for fpath in all_files:
            if not fpath.is_file() or not is_frozen_shard(fpath):
                continue
            st = _file_stats(fpath, root)
            frozen_entries.append(st)
            rec_line = f"{st['path']}:{st['bytes']}:{st['lines']}:{st['sha256']}\n".encode("utf-8")
            coll_hasher.update(rec_line)
            master_hasher.update(rec_line)
            ep_bucket = epoch_Rollup[st["epoch_id"]]
            ep_bucket["files"] += 1
            ep_bucket["lines"] += st["lines"]
            ep_bucket["bytes"] += st["bytes"]

        collections_out[coll_name] = {
            "frozen_file_count": len(frozen_entries),
            "frozen_line_count": sum(e["lines"] for e in frozen_entries),
            "frozen_bytes": sum(e["bytes"] for e in frozen_entries),
            "rollup_sha256": coll_hasher.hexdigest(),
            "files": frozen_entries,
        }

    return {
        "schema_version": 1,
        "frozen_cutoff_date": FROZEN_EPOCH_CUTOFF,
        "active_epoch_start_date": ACTIVE_EPOCH_START_DATE,
        "epochs": list(EPOCH_DEFINITIONS),
        "frozen_epoch_totals": epoch_Rollup,
        "master_rollup_sha256": master_hasher.hexdigest(),
        "collections": collections_out,
    }


def epoch_manifest_path(root: Path = ROOT) -> Path:
    return Path(root) / "state" / "epoch_manifest.json"


def write_epoch_manifest(root: Path = ROOT) -> Path:
    manifest = build_epoch_manifest(root)
    target = epoch_manifest_path(root)
    ledger_io.atomic_write_text(
        target, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    return target


def check_epoch_manifest(root: Path = ROOT) -> tuple[bool, str]:
    root = Path(root)
    target = epoch_manifest_path(root)
    if not target.is_file():
        return False, "state/epoch_manifest.json is missing (run: python3 tools/memory_tiers.py --freeze-epochs)"
    try:
        stored = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"state/epoch_manifest.json is invalid JSON: {exc}"
    live = build_epoch_manifest(root)
    if stored.get("master_rollup_sha256") != live.get("master_rollup_sha256"):
        # Pinpoint which collection / shard drifted
        drifted: list[str] = []
        s_colls = stored.get("collections") or {}
        l_colls = live.get("collections") or {}
        for cname in sorted(set(s_colls) | set(l_colls)):
            if (s_colls.get(cname) or {}).get("rollup_sha256") != (l_colls.get(cname) or {}).get("rollup_sha256"):
                drifted.append(cname)
        return (
            False,
            f"Epoch freeze mismatch on collections {drifted}: frozen shards (<= {FROZEN_EPOCH_CUTOFF}) "
            "were modified, added, or compacted without refreshing state/epoch_manifest.json",
        )
    total_files = sum(c["frozen_file_count"] for c in live["collections"].values())
    total_lines = sum(c["frozen_line_count"] for c in live["collections"].values())
    return (
        True,
        f"PASS: epoch_manifest verified ({total_files} frozen files, {total_lines:,} lines, "
        f"cutoff <= {FROZEN_EPOCH_CUTOFF}, sha256={live['master_rollup_sha256'][:12]}...)",
    )


def _load_effective_ledgers(root: Path = ROOT) -> dict[str, dict[str, dict[str, Any]]]:
    root = Path(root)
    spec = {
        cname: (root / "state" / f"{cname}.jsonl", key)
        for cname, key in BASE_LEDGER_SPECS
    }
    cols, _ = ledger_io.load_collections(spec, root=root)
    # Apply editorial_decisions material verification overlays
    materials = {mid: dict(m) for mid, m in cols.get("materials", {}).items()}
    for dec in cols.get("editorial_decisions", {}).values():
        tgt = dec.get("target") or {}
        if tgt.get("type") == "material" and tgt.get("id") in materials and dec.get("status"):
            mcopy = dict(materials[tgt["id"]])
            ver = dict(mcopy.get("verification") or {})
            ver["status"] = dec["status"]
            if dec.get("verification_method"):
                ver["method"] = dec["verification_method"]
            mcopy["verification"] = ver
            materials[tgt["id"]] = mcopy
    cols["materials"] = materials
    return cols


def classify_materials(
    cols: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """Classify every material into ``hot``, ``cold``, or ``suppressed``."""
    materials = cols.get("materials") or {}
    hypotheses = cols.get("hypotheses") or {}
    evaluations = cols.get("evaluations") or {}
    notes = cols.get("notes") or {}
    errata = cols.get("errata") or {}

    suppressed_ids: set[str] = set()
    for er in errata.values():
        if er.get("status") == "open" and er.get("weight_effect") == "suppress_retrieval":
            if er.get("subject_type") == "material" and er.get("subject_id"):
                suppressed_ids.add(str(er["subject_id"]))

    wired_ids: set[str] = set()
    for hyp in hypotheses.values():
        if hyp.get("status") == "refuted":
            continue
        for k in ("supporting_material_ids", "counter_material_ids"):
            for mid in hyp.get(k) or ():
                wired_ids.add(str(mid))
    for evl in evaluations.values():
        for mid in evl.get("evidence_material_ids") or ():
            wired_ids.add(str(mid))
    for nrec in notes.values():
        for cl in nrec.get("claims") or ():
            if isinstance(cl, dict):
                for mid in cl.get("material_ids") or ():
                    wired_ids.add(str(mid))

    out: dict[str, dict[str, Any]] = {}
    for mid, mat in materials.items():
        if mid in suppressed_ids:
            out[mid] = {"tier": "suppressed", "reason": "suppress_retrieval erratum"}
            continue
        ver = mat.get("verification") or {}
        vstat = str(ver.get("status") or "unverified")
        vdepth = str(ver.get("depth") or "")
        mdate = _extract_record_date(mid, str(ver.get("checked_at") or ""))
        is_wired = mid in wired_ids
        is_deep_verified = vstat == "verified" and (
            vdepth in _HOT_VERIFICATION_DEPTHS or mdate >= ACTIVE_EPOCH_START_DATE
        )
        if is_wired or is_deep_verified or mdate >= ACTIVE_EPOCH_START_DATE:
            reason = (
                "wired_to_belief_or_claim"
                if is_wired
                else ("deep_verified" if is_deep_verified else "active_epoch")
            )
            out[mid] = {"tier": "hot", "reason": reason, "verification_status": vstat}
        else:
            out[mid] = {"tier": "cold", "reason": "dormant_unwired_pre_active_epoch", "verification_status": vstat}
    return out


def is_hot_material(
    mid: str,
    mat: dict[str, Any],
    *,
    wired_ids: set[str] | None = None,
) -> bool:
    """Lightweight per-material predicate for packet ordering."""
    if wired_ids and mid in wired_ids:
        return True
    ver = mat.get("verification") or {}
    vstat = str(ver.get("status") or "")
    vdepth = str(ver.get("depth") or "")
    mdate = _extract_record_date(mid, str(ver.get("checked_at") or ""))
    if vstat == "verified" and (vdepth in _HOT_VERIFICATION_DEPTHS or mdate >= ACTIVE_EPOCH_START_DATE):
        return True
    return mdate >= ACTIVE_EPOCH_START_DATE


def classify_notes(
    cols: dict[str, dict[str, dict[str, Any]]],
    *,
    root: Path = ROOT,
) -> dict[str, dict[str, Any]]:
    """Classify every note record into ``hot``, ``subsumed``, or ``cold``."""
    notes = cols.get("notes") or {}
    hypotheses = cols.get("hypotheses") or {}
    read_log = cols.get("read_log") or {}

    superseded_ids: set[str] = set()
    for nrec in notes.values():
        for sid in nrec.get("supersedes") or ():
            superseded_ids.add(str(sid))

    hyp_note_ids: set[str] = set()
    for hyp in hypotheses.values():
        for nid in hyp.get("source_note_ids") or ():
            hyp_note_ids.add(str(nid))

    cross_read_note_ids: set[str] = set()
    for rl in read_log.values():
        tgt = rl.get("target") or {}
        if tgt.get("type") == "note" and rl.get("reading") not in ("used_as_context", "counted", "declined"):
            nid = str(tgt.get("id") or "")
            if nid:
                cross_read_note_ids.add(nid)

    out: dict[str, dict[str, Any]] = {}
    for nid, nrec in notes.items():
        explicit = nrec.get("memory_tier")
        if explicit in ("hot", "cold", "subsumed"):
            out[nid] = {
                "tier": explicit,
                "reason": "explicit_memory_tier",
                "consolidated_into": nrec.get("consolidated_into") or "",
            }
            continue
        if nid in superseded_ids:
            out[nid] = {"tier": "subsumed", "reason": "superseded_by_later_note", "consolidated_into": ""}
            continue
        ndate = _extract_record_date(nid, str(nrec.get("date_real") or nrec.get("created_at") or ""))
        salience = int(nrec.get("salience") or 0)
        claims = nrec.get("claims") or []
        is_active_epoch = ndate >= ACTIVE_EPOCH_START_DATE
        if is_active_epoch or nid in hyp_note_ids or salience >= 3:
            out[nid] = {"tier": "hot", "reason": "active_or_load_bearing", "consolidated_into": ""}
        elif claims and ndate <= FROZEN_EPOCH_CUTOFF:
            quad = str(nrec.get("quadrant") or "")
            digest_id = _digest_for_quadrant(quad)
            out[nid] = {
                "tier": "subsumed",
                "reason": "consolidated_into_l1_domain_digest",
                "consolidated_into": digest_id,
            }
        elif nid in cross_read_note_ids:
            out[nid] = {"tier": "hot", "reason": "cross_session_reread", "consolidated_into": ""}
        else:
            out[nid] = {"tier": "cold", "reason": "dormant_backfill_or_unreferenced", "consolidated_into": ""}
    return out


def _digest_for_quadrant(quadrant: str) -> str:
    for spec in DIGEST_SPECS:
        if quadrant and quadrant in spec["quadrants"]:
            return spec["digest_id"]
    return "DIGEST-B-AI-MEMORY"


def compute_tier_summary(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root)
    cols = _load_effective_ledgers(root)
    mat_classes = classify_materials(cols)
    note_classes = classify_notes(cols, root=root)
    mat_counts = Counter(v["tier"] for v in mat_classes.values())
    note_counts = Counter(v["tier"] for v in note_classes.values())

    state_bytes = sum(
        p.stat().st_size for p in (root / "state").rglob("*.jsonl") if p.is_file()
    ) if (root / "state").is_dir() else 0
    readings_files = (
        [p for p in (root / "readings").glob("*.md") if p.is_file()]
        if (root / "readings").is_dir()
        else []
    )
    readings_bytes = sum(p.stat().st_size for p in readings_files)
    digest_md = root / "docs" / "CONSOLIDATED_DIGESTS.md"
    l1_bytes = digest_md.stat().st_size if digest_md.is_file() else 0

    ep_ok, ep_msg = check_epoch_manifest(root)
    return {
        "materials": {
            "total": len(mat_classes),
            "hot": mat_counts.get("hot", 0),
            "cold": mat_counts.get("cold", 0),
            "suppressed": mat_counts.get("suppressed", 0),
            "hot_ratio": round(mat_counts.get("hot", 0) / max(1, len(mat_classes)), 4),
        },
        "notes": {
            "total": len(note_classes),
            "hot": note_counts.get("hot", 0),
            "subsumed": note_counts.get("subsumed", 0),
            "cold": note_counts.get("cold", 0),
            "hot_ratio": round(note_counts.get("hot", 0) / max(1, len(note_classes)), 4),
        },
        "storage_bytes": {
            "l0_state_jsonl_bytes": state_bytes,
            "l0_readings_bytes": readings_bytes,
            "l0_readings_file_count": len(readings_files),
            "l1_consolidated_digests_bytes": l1_bytes,
        },
        "epoch_freeze": {
            "cutoff_date": FROZEN_EPOCH_CUTOFF,
            "active_start_date": ACTIVE_EPOCH_START_DATE,
            "manifest_valid": ep_ok,
            "message": ep_msg,
        },
    }


def recall_cold_records(
    root: Path = ROOT,
    query: str = "",
    *,
    limit: int = 15,
) -> dict[str, Any]:
    """Varga, Stewart & Bauer (2016) stem-fact reminder search over L0 cold/subsumed records."""
    root = Path(root)
    cols = _load_effective_ledgers(root)
    mat_classes = classify_materials(cols)
    note_classes = classify_notes(cols, root=root)
    terms = [t.lower() for t in re.split(r"\s+", query.strip()) if t]

    mat_hits: list[dict[str, Any]] = []
    for mid, info in sorted(mat_classes.items()):
        if info["tier"] == "hot":
            continue
        mat = cols["materials"][mid]
        src = mat.get("source") or {}
        haystack = " ".join([
            mid,
            str(mat.get("title") or ""),
            " ".join(str(a) for a in (src.get("authors") or [])),
            str(mat.get("passage") or ""),
            str(mat.get("scope_note") or ""),
            " ".join(str(m) for m in (mat.get("motif_ids") or [])),
        ]).lower()
        if terms and not all(t in haystack for t in terms):
            continue
        score = sum(haystack.count(t) for t in terms) if terms else 1
        mat_hits.append({
            "material_id": mid,
            "tier": info["tier"],
            "title": mat.get("title", ""),
            "authors": (src.get("authors") or [])[:3],
            "year": src.get("year"),
            "verification": info.get("verification_status", "unverified"),
            "score": score,
            "fetch_command": f"python3 tools/inspect_inquiry.py --id {mid}",
        })
    mat_hits.sort(key=lambda r: (-r["score"], r["material_id"]))

    note_hits: list[dict[str, Any]] = []
    for nid, info in sorted(note_classes.items()):
        if info["tier"] == "hot":
            continue
        nrec = cols["notes"][nid]
        claims_txt = " ".join(
            str(c.get("text") or "") for c in (nrec.get("claims") or []) if isinstance(c, dict)
        )
        haystack = " ".join([
            nid,
            str(nrec.get("path") or ""),
            str(nrec.get("title") or ""),
            str(nrec.get("reason") or ""),
            claims_txt,
        ]).lower()
        if terms and not all(t in haystack for t in terms):
            continue
        score = sum(haystack.count(t) for t in terms) if terms else 1
        note_hits.append({
            "note_id": nid,
            "tier": info["tier"],
            "consolidated_into": info.get("consolidated_into", ""),
            "path": nrec.get("path", ""),
            "title": nrec.get("title", ""),
            "score": score,
        })
    note_hits.sort(key=lambda r: (-r["score"], r["note_id"]))

    return {
        "query": query,
        "cold_material_total_matches": len(mat_hits),
        "cold_note_total_matches": len(note_hits),
        "materials": mat_hits[:limit],
        "notes": note_hits[:limit],
    }


def build_domain_digests(root: Path = ROOT) -> dict[str, Any]:
    """Compile the deterministic L1 domain digest registry from ledger state."""
    root = Path(root)
    cols = _load_effective_ledgers(root)
    note_classes = classify_notes(cols, root=root)
    mat_classes = classify_materials(cols)
    bstate = belief_state.compute_belief_state(root=root)

    notes = cols.get("notes") or {}
    materials = cols.get("materials") or {}

    # Latest session stamp for deterministic provenance without volatile wall-clock
    sessions = cols.get("sessions") or {}
    latest_sid = sorted(sessions.keys())[-1] if sessions else ""

    digests_list: list[dict[str, Any]] = []
    for spec in DIGEST_SPECS:
        did = spec["digest_id"]
        quads = set(spec["quadrants"])
        t_qids = list(spec["target_questions"])

        subsumed_nids = sorted(
            nid
            for nid, nc in note_classes.items()
            if nc.get("consolidated_into") == did
            or (quads and str(notes[nid].get("quadrant") or "") in quads and nc["tier"] == "subsumed")
        )
        hot_domain_nids = sorted(
            nid
            for nid, nc in note_classes.items()
            if quads and str(notes[nid].get("quadrant") or "") in quads and nc["tier"] == "hot"
        )

        # Representative high-salience durable claims from notes in this domain
        domain_claims: list[dict[str, str]] = []
        candidate_nids = sorted(
            (nid for nid in notes if quads and str(notes[nid].get("quadrant") or "") in quads),
            key=lambda nid: (
                -int(notes[nid].get("salience") or 0),
                -_extract_record_date(nid, str(notes[nid].get("date_real") or "")).replace("-", "").isdigit(),
                _extract_record_date(nid, str(notes[nid].get("date_real") or "")),
                nid,
            ),
            reverse=False,
        )
        # Sort newest high-salience first deterministically
        candidate_nids = sorted(
            (nid for nid in notes if quads and str(notes[nid].get("quadrant") or "") in quads),
            key=lambda nid: (
                -int(notes[nid].get("salience") or 0),
                "" if not _extract_record_date(nid, str(notes[nid].get("date_real") or "")) else
                f"{99999999 - int(_extract_record_date(nid, str(notes[nid].get('date_real') or '')).replace('-', ''))}",
                nid,
            ),
        )
        seen_texts: set[str] = set()
        for nid in candidate_nids:
            for cl in notes[nid].get("claims") or ():
                if not isinstance(cl, dict):
                    continue
                if cl.get("kind") not in ("reading_revised", "method_change", "measured_fact", "reading_maintained"):
                    continue
                txt = str(cl.get("text") or "").strip()
                if not txt or txt[:40] in seen_texts:
                    continue
                seen_texts.add(txt[:40])
                domain_claims.append({
                    "note_id": nid,
                    "claim_id": str(cl.get("claim_id") or ""),
                    "kind": str(cl.get("kind") or ""),
                    "text": txt[:260] + ("…" if len(txt) > 260 else ""),
                })
                if len(domain_claims) >= 6:
                    break
            if len(domain_claims) >= 6:
                break

        # Active generation-amortized frontier hypotheses for target questions
        frontier_hyps: list[dict[str, Any]] = []
        seen_hids: set[str] = set()
        per_q_limit = 4 if did == "DIGEST-E-FALSIFICATION-FRONTIER" else 2
        for qid in t_qids:
            qs = bstate["questions"].get(qid) or {}
            amort_sorted = sorted(
                (h for h in (qs.get("hypotheses") or []) if h.get("effective_status") == "active"),
                key=lambda h: (-float(h.get("amortized_posterior", 0.0)), h["hypothesis_id"]),
            )
            count_q = 0
            for h in amort_sorted:
                hid = h["hypothesis_id"]
                if hid in seen_hids and did != "DIGEST-E-FALSIFICATION-FRONTIER":
                    continue
                seen_hids.add(hid)
                frontier_hyps.append({
                    "question_id": qid,
                    "hypothesis_id": hid,
                    "title": h.get("title", ""),
                    "amortized_posterior": h.get("amortized_posterior", 0.0),
                    "gated_posterior": h.get("gated_posterior", 0.0),
                    "uncertainty": h.get("uncertainty", 0.0),
                    "scope_conditions": list(h.get("scope_conditions") or [])[:3],
                    "exclusion_clause": str(h.get("exclusion_clause") or ""),
                    "supporting_material_ids": [
                        m for m in (h.get("supporting_material_ids") or [])
                        if (mat_classes.get(m) or {}).get("tier") == "hot"
                    ][:4],
                })
                count_q += 1
                if count_q >= per_q_limit:
                    break

        # Pinpoint verified primary-source anchors referenced by these frontier hypotheses
        anchor_mids: list[str] = []
        for fh in frontier_hyps:
            for mid in fh["supporting_material_ids"]:
                if mid not in anchor_mids and mid in materials:
                    anchor_mids.append(mid)
        anchors = [
            {
                "material_id": mid,
                "title": materials[mid].get("title", ""),
                "year": (materials[mid].get("source") or {}).get("year"),
            }
            for mid in anchor_mids[:8]
        ]

        digests_list.append({
            "digest_id": did,
            "title": spec["title"],
            "target_questions": t_qids,
            "quadrants": list(spec["quadrants"]),
            "subsumed_note_count": len(subsumed_nids),
            "hot_note_count": len(hot_domain_nids),
            "core_principles": list(spec["core_principles"]),
            "consolidated_claims": domain_claims,
            "active_falsification_frontier": frontier_hyps,
            "verified_primary_anchors": anchors,
        })

    return {
        "schema_version": 1,
        "basis_session_id": latest_sid,
        "hot_material_count": sum(1 for v in mat_classes.values() if v["tier"] == "hot"),
        "cold_material_count": sum(1 for v in mat_classes.values() if v["tier"] == "cold"),
        "subsumed_note_total": sum(1 for v in note_classes.values() if v["tier"] == "subsumed"),
        "hot_note_total": sum(1 for v in note_classes.values() if v["tier"] == "hot"),
        "cold_note_total": sum(1 for v in note_classes.values() if v["tier"] == "cold"),
        "digests": digests_list,
    }


def render_consolidated_digests_md(registry: dict[str, Any]) -> str:
    """Render tracked `docs/CONSOLIDATED_DIGESTS.md` strictly from `state/digests.json`."""
    lines: list[str] = [
        "# CONSOLIDATED_DIGESTS — L1 統合スキーマ・ドメインダイジェストと反証フロンティア",
        "",
        "> 本ファイルは三階層記憶アーキテクチャの **L1（統合スキーマ層）** であり、`python3 tools/memory_tiers.py --write-digests` により `state/digests.json` と完全同期で決定論的に生成される。",
        "> 生の証跡（`state/` 全シャードと `readings/*.md` 全編）は **L0（コールド証跡層）** に追記専用のまま1バイトも削らず保存される。休眠行のオンデマンド検索には `python3 tools/memory_tiers.py --recall-cold <検索語>` を使う。",
        "",
        "## 0. 三階層記憶サマリー（スナップショット基準）",
        "",
        f"- **基準セッション来歴**: `{registry.get('basis_session_id') or '—'}`",
        f"- **素材 (`materials`) 階層内訳**: Hot（現役検証・配線済） **{registry.get('hot_material_count', 0)}** 件 ／ Cold（L0 休眠証跡） **{registry.get('cold_material_count', 0)}** 件",
        f"- **精読ノート (`notes`) 階層内訳**: Hot（現役参照） **{registry.get('hot_note_total', 0)}** 件 ／ Subsumed（L1 統合卒業済） **{registry.get('subsumed_note_total', 0)}** 件 ／ Cold（L0 構造スタブ等） **{registry.get('cold_note_total', 0)}** 件",
        "",
    ]

    for dg in registry.get("digests") or []:
        q_str = ", ".join(f"`{q}`" for q in dg.get("target_questions") or [])
        quad_str = ", ".join(f"`{q}`" for q in dg.get("quadrants") or []) or "全象限横断"
        lines.extend([
            f"## {dg['digest_id']}: {dg['title']}",
            "",
            f"- **対応中心問い**: {q_str} ｜ **対象象限**: {quad_str} ｜ **L1 統合卒業ノート数**: {dg.get('subsumed_note_count', 0)} 件（現役 Hot: {dg.get('hot_note_count', 0)} 件）",
            "",
            "### 統合スキーマ原則",
            "",
        ])
        for pr in dg.get("core_principles") or []:
            lines.append(f"- {pr}")
        lines.append("")

        claims = dg.get("consolidated_claims") or []
        if claims:
            lines.extend(["### 代表的統合知見（L0 ノートからの抽出アンカー）", ""])
            for cl in claims:
                lines.append(
                    f"- [`{cl['note_id']}` / `{cl['kind']}`] {cl['text']}"
                )
            lines.append("")

        frontier = dg.get("active_falsification_frontier") or []
        if frontier:
            lines.extend(["### 現役仮説と反証条項（`P_amort` 上位フロンティア）", ""])
            for fh in frontier:
                scs = " ／ ".join(fh.get("scope_conditions") or [])
                lines.append(
                    f"- **`{fh['hypothesis_id']}`**（`{fh['question_id']}`, **P_amort={fh['amortized_posterior']*100:.1f}%**, "
                    f"P_gate={fh['gated_posterior']*100:.1f}%, u={fh['uncertainty']:.3f}）: {fh['title']}"
                )
                if scs:
                    lines.append(f"  - 適用条件: {scs}")
                lines.append(f"  - **反証・限定条件 (`exclusion_clause`)**: {fh['exclusion_clause']}")
            lines.append("")

        anchors = dg.get("verified_primary_anchors") or []
        if anchors:
            anc_txt = "、".join(
                f"`{a['material_id']}`（{a['title'][:36]}{'…' if len(a['title']) > 36 else ''}, {a.get('year') or '?'}）"
                for a in anchors
            )
            lines.append(f"- **検証済一次文献アンカー**: {anc_txt}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def digests_json_path(root: Path = ROOT) -> Path:
    return Path(root) / "state" / "digests.json"


def digests_md_path(root: Path = ROOT) -> Path:
    return Path(root) / "docs" / "CONSOLIDATED_DIGESTS.md"


def write_digests(root: Path = ROOT) -> tuple[Path, Path]:
    root = Path(root)
    reg = build_domain_digests(root)
    jpath = digests_json_path(root)
    mpath = digests_md_path(root)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    ledger_io.atomic_write_text(
        jpath, json.dumps(reg, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    ledger_io.atomic_write_text(mpath, render_consolidated_digests_md(reg))
    return jpath, mpath


def check_digests(root: Path = ROOT) -> tuple[bool, str]:
    """Verify `state/digests.json` and `docs/CONSOLIDATED_DIGESTS.md` are valid and mutually synced."""
    root = Path(root)
    jpath = digests_json_path(root)
    mpath = digests_md_path(root)
    if not jpath.is_file() or not mpath.is_file():
        return (
            False,
            "L1 digest files missing (`state/digests.json` or `docs/CONSOLIDATED_DIGESTS.md`); "
            "run `python3 tools/memory_tiers.py --write-digests`",
        )
    try:
        reg = json.loads(jpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"state/digests.json is invalid JSON: {exc}"

    expected_md = render_consolidated_digests_md(reg)
    actual_md = mpath.read_text(encoding="utf-8")
    if actual_md != expected_md:
        return (
            False,
            "docs/CONSOLIDATED_DIGESTS.md is out of sync with state/digests.json "
            "(run: python3 tools/memory_tiers.py --write-digests)",
        )

    # Referential sanity: every frontier hypothesis named in the L1 registry must exist in hypotheses ledger
    hyps = ledger_io.load_jsonl_union(root / "state" / "hypotheses.jsonl", "hypothesis_id", root=root)
    for dg in reg.get("digests") or []:
        if not dg.get("core_principles"):
            return False, f"L1 digest {dg.get('digest_id')} has empty core_principles"
        for fh in dg.get("active_falsification_frontier") or []:
            hid = fh.get("hypothesis_id")
            if hid not in hyps:
                return False, f"L1 digest {dg.get('digest_id')} references unknown hypothesis {hid!r}"
            if not str(fh.get("exclusion_clause") or "").strip():
                return False, f"L1 digest {dg.get('digest_id')} hypothesis {hid} lacks exclusion_clause"

    return (
        True,
        f"PASS: L1 digests verified ({len(reg.get('digests') or [])} domain digests, "
        f"{len(expected_md.encode('utf-8')):,} bytes)",
    )


def for_question_digest_lines(question_id: str, root: Path = ROOT) -> list[str]:
    """Return compact L1 domain digest lines for L2 session packets (`--hot-only`)."""
    jpath = digests_json_path(root)
    if not jpath.is_file():
        return []
    try:
        reg = json.loads(jpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    matched = [
        dg for dg in (reg.get("digests") or [])
        if question_id in (dg.get("target_questions") or [])
        and dg.get("digest_id") != "DIGEST-E-FALSIFICATION-FRONTIER"
    ]
    if not matched:
        matched = [
            dg for dg in (reg.get("digests") or [])
            if dg.get("digest_id") != "DIGEST-E-FALSIFICATION-FRONTIER"
        ][:2]
    lines: list[str] = [
        "## 2.5 統合スキーマ・ダイジェスト（L1 圧縮記憶 — `docs/CONSOLIDATED_DIGESTS.md`）",
        "- **役割**: 過去エポックの個別報告群（L0）から抽出された領域別の不変原則と検証済アンカー。休眠 L0 証跡の引き上げは `python3 tools/memory_tiers.py --recall-cold <検索語>`。",
    ]
    for dg in matched[:3]:
        lines.append(f"- **`{dg['digest_id']}`（{dg['title']}）**:")
        for pr in (dg.get("core_principles") or [])[:2]:
            lines.append(f"  - {pr}")
    lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--json", action="store_true", help="output JSON")
    parser.add_argument(
        "--recall-cold",
        metavar="QUERY",
        help="stem-fact cue search across L0 cold/subsumed materials and notes",
    )
    parser.add_argument("--limit", type=int, default=15, help="max results for --recall-cold")
    parser.add_argument(
        "--write-digests",
        action="store_true",
        help="compile and write state/digests.json and docs/CONSOLIDATED_DIGESTS.md",
    )
    parser.add_argument(
        "--freeze-epochs",
        action="store_true",
        help="compute and write state/epoch_manifest.json for completed frozen epochs",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify both state/epoch_manifest.json SHA-256 freeze and L1 digest consistency",
    )
    args = parser.parse_args(argv)

    if args.freeze_epochs:
        path = write_epoch_manifest(args.root)
        print(f"WROTE {path.relative_to(Path(args.root))} ({path.stat().st_size:,} bytes)")
        return 0

    if args.write_digests:
        jpath, mpath = write_digests(args.root)
        print(
            f"WROTE {jpath.relative_to(Path(args.root))} ({jpath.stat().st_size:,} bytes) "
            f"and {mpath.relative_to(Path(args.root))} ({mpath.stat().st_size:,} bytes)"
        )
        return 0

    if args.check:
        ok1, msg1 = check_epoch_manifest(args.root)
        ok2, msg2 = check_digests(args.root)
        for ok, msg in ((ok1, msg1), (ok2, msg2)):
            print(msg, file=sys.stdout if ok else sys.stderr)
        return 0 if (ok1 and ok2) else 1

    if args.recall_cold is not None:
        res = recall_cold_records(args.root, args.recall_cold, limit=args.limit)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0
        print(
            f"=== L0 コールド／卒業証跡の幹事実リマインダー検索 (query={res['query']!r}) ===\n"
            f"一致: 素材 {res['cold_material_total_matches']} 件 ／ ノート {res['cold_note_total_matches']} 件"
        )
        for m in res["materials"]:
            print(
                f"  [MAT/{m['tier']}] {m['material_id']} ({m.get('year') or '?'}, {m['verification']}) "
                f"{m['title']}  -> `{m['fetch_command']}`"
            )
        for n in res["notes"]:
            into = f" -> {n['consolidated_into']}" if n.get("consolidated_into") else ""
            print(f"  [NOTE/{n['tier']}{into}] {n['note_id']} {n['path']} {n['title']}")
        return 0

    summary = compute_tier_summary(args.root)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    mats = summary["materials"]
    nts = summary["notes"]
    st = summary["storage_bytes"]
    ep = summary["epoch_freeze"]
    print("=== 三階層記憶（L0/L1/L2）＆ エポック境界凍結レポート ===")
    print(
        f"  素材 (materials): 総数 {mats['total']:,} ｜ Hot {mats['hot']:,} ({mats['hot_ratio']*100:.1f}%) "
        f"｜ L0 Cold {mats['cold']:,} ｜ 抑制 {mats['suppressed']:,}"
    )
    print(
        f"  ノート (notes):   総数 {nts['total']:,} ｜ Hot {nts['hot']:,} ({nts['hot_ratio']*100:.1f}%) "
        f"｜ L1 統合卒業(subsumed) {nts['subsumed']:,} ｜ L0 Cold {nts['cold']:,}"
    )
    print(
        f"  記憶容量: L0 state/*.jsonl={st['l0_state_jsonl_bytes']/1048576:.2f} MiB, "
        f"L0 readings/={st['l0_readings_bytes']/1048576:.2f} MiB ({st['l0_readings_file_count']} files) "
        f"-> L1 CONSOLIDATED_DIGESTS.md={st['l1_consolidated_digests_bytes']/1024:.1f} KiB"
    )
    print(f"  エポック凍結: {ep['message']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
