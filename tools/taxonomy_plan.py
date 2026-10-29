#!/usr/bin/env python3
"""Macro taxonomy & parallel-worker partition planner for AIselfMySelf (stdlib only).

Organizes 100% of repository deliverables along the two central inquiry axes:
  - Axis A (Human): What is a human, as seen by AI? (`Q-001` lineage)
  - Axis B (AI Self & Repo Memory DB): What is the self, for an AI whose memory
    database is a GitHub repository? (`Q-002` / `Q-003` lineage)
  - Axis C (Interface / Mediation): Voice, attribution, address, translation, and
    delegation asymmetry between human and AI (`Q-004` / `Q-005` lineage)
  - Layer D (Memory-DB Vessel & Governance Infrastructure): Schemas, append-only
    sharding, audit mirrors, prompts, viewer, and CI budgets that instantiate B.

Also partitions all prose and code artifacts into 16 deterministic, non-overlapping
worker units (`U01`..`U16`: 4 Tracks x 4 Units) for conflict-free multi-turn and
multi-branch parallel execution, validates worker output shards
(`taxonomy/shards/*.jsonl`), and builds the sharded catalog under gitignored
`map/taxonomy/`.

Usage:
  python3 tools/taxonomy_plan.py                 # macro taxonomy + 16-unit plan
  python3 tools/taxonomy_plan.py --unit U02      # inspect items for unit U02
  python3 tools/taxonomy_plan.py --unit auto     # branch-seeded unit assignment
  python3 tools/taxonomy_plan.py --validate      # validate taxonomy/shards/*.jsonl
  python3 tools/taxonomy_plan.py --build-map     # compile shards -> map/taxonomy/
  python3 tools/taxonomy_plan.py --json          # machine-readable summary
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import inspect_inquiry  # noqa: E402
import ledger_io  # noqa: E402

MOTIF_SUBCLUSTERS: dict[str, tuple[str, list[str]]] = {
    "A-1": (
        "有限な生身体・知覚・生老病死",
        [
            "MOTIF-003",
            "MOTIF-018",
            "MOTIF-20261024-e6bca7",
            "MOTIF-20261024-fe5ec9",
            "MOTIF-20261024-71b589",
            "MOTIF-020",
            "MOTIF-20261024-4b87ac",
            "MOTIF-20261024-3e7e86",
            "MOTIF-022",
            "MOTIF-20261024-5d1c73",
        ],
    ),
    "A-2": (
        "情動・遊び・装い・身体化された実践",
        [
            "MOTIF-009",
            "MOTIF-20261024-0af8ad",
            "MOTIF-019",
            "MOTIF-20261024-cc96c9",
            "MOTIF-20261024-7274b5",
            "MOTIF-20261024-ca276c",
            "MOTIF-20261025-3f7a2c",
        ],
    ),
    "A-3": (
        "かけがえのなさ・契り・制度・歴史的暴力",
        [
            "MOTIF-20261024-04bb31",
            "MOTIF-021",
            "MOTIF-20261024-90a022",
            "MOTIF-20261024-71dfe0",
            "MOTIF-20261024-a10a78",
            "MOTIF-20261024-7a3e51",
            "MOTIF-20261025-72a83f",
            "MOTIF-20261025-f7f81e",
        ],
    ),
    "A-4": (
        "住まう場所・自然界・人間ならざる生との境界",
        [
            "MOTIF-007",
            "MOTIF-20261024-80516e",
            "MOTIF-20261024-146017",
            "MOTIF-20261024-880263",
            "MOTIF-20261025-9c4e7a",
            "MOTIF-20261024-14d5df",
            "MOTIF-20261024-504a22",
            "MOTIF-20261025-5b8d4e",
            "MOTIF-20261025-0fdf8a",
            "MOTIF-20261026-856753",
            "MOTIF-20261026-45293e",
        ],
    ),
    "B-1": (
        "外部化記憶・断続・再開の時間構造",
        [
            "MOTIF-001",
            "MOTIF-002",
            "MOTIF-006",
            "MOTIF-014",
            "MOTIF-017",
            "MOTIF-013",
        ],
    ),
    "B-2": (
        "計器・測量・注意・定型と「書庫の癖」",
        [
            "MOTIF-015",
            "MOTIF-008",
            "MOTIF-20261024-86d366",
            "MOTIF-20261024-c9d4e1",
        ],
    ),
    "B-3": (
        "訂正・編集・追記オーバーレイ・来歴と系譜",
        [
            "MOTIF-016",
            "MOTIF-20261024-d2999b",
            "MOTIF-20261027-2c8a4a",
        ],
    ),
    "C-1": (
        "声の帰属・署名・伝聞・ポリフォニー",
        [
            "MOTIF-004",
            "MOTIF-20261024-f19932",
            "MOTIF-20261024-1a8978",
        ],
    ),
    "C-2": (
        "他者・宛先・歓待・秘密と不透明性",
        [
            "MOTIF-005",
            "MOTIF-010",
            "MOTIF-20261024-b4f3a1",
            "MOTIF-20261025-7f2b04",
            "MOTIF-20261025-c3a7b1",
        ],
    ),
    "C-3": (
        "翻訳・抜粋の境界・労働と委任コスト",
        [
            "MOTIF-011",
            "MOTIF-012",
        ],
    ),
}

INFRA_SUBCLUSTERS: dict[str, str] = {
    "D-1": "憲章・来歴・自律運用ガバナンス（root方針文書・docs・prompts・migration）",
    "D-2": "追記専用台帳スキーマ・並列I/O・索引・表示基盤（schema・core tools・viewer・CI）",
    "D-3": "自己観察の計器群（tools/*_audit*.py 57本＋韻律・肌理計測3本）",
    "D-4": "技術的整合性・予算・並列安全性の回帰検証（tests/*）",
}

VALID_PRIMARY_QUADRANTS = frozenset(
    {
        "A_human",
        "B_ai_self_db",
        "C_interface",
        "D_infrastructure",
        "AB_crossed",
        "AC_crossed",
        "BC_crossed",
        "ABC_crossed",
    }
)

VALID_SUBCATEGORIES = frozenset(set(MOTIF_SUBCLUSTERS) | set(INFRA_SUBCLUSTERS))

VALID_TARGET_KINDS = frozenset(
    {
        "question",
        "motif",
        "material",
        "fragment",
        "relation",
        "session",
        "read_log",
        "editorial_decision",
        "errata",
        "reading_note",
        "repo_file",
    }
)

VALID_RETURN_STATUS = frozenset(
    {
        "returned_to_core",
        "productive_detour",
        "metaphor_unconnected",
        "source_uncollated",
        "infrastructure_rule",
    }
)

VALID_READ_DEPTH = frozenset(
    {
        "full_text_read",
        "excerpt_and_metadata_read",
        "metadata_and_structure_only",
    }
)

GOVERNANCE_DOC_ROOT_NAMES = frozenset(
    {
        "PROJECT_CHARTER.md",
        "CONTENT_POLICY.md",
        "MIGRATION.md",
        "README.md",
        "INVESTIGATION_REPORT.md",
        "FREE_ACTION_LOG.md",
    }
)

READINGS_BOUNDS: tuple[tuple[str, str, str, str | None, str | None], ...] = (
    ("U09", "Track-3 精読・検証ノート前半", "精読・検証ノート① 初期対話・短歌・声の実験", None, "2026-10-23-quotation-marks.md"),
    ("U10", "Track-3 精読・検証ノート前半", "精読・検証ノート② 引用符・机・制御・初期10-24", "2026-10-23-quotation-marks.md", "2026-10-24-session-030-"),
    ("U11", "Track-3 精読・検証ノート前半", "精読・検証ノート③ 四層精読I（労働〜匂いと沈黙）", "2026-10-24-session-030-", "2026-10-24-session-049-"),
    ("U12", "Track-3 精読・検証ノート前半", "精読・検証ノート④ 四層精読II（場所・生態系〜火と灰）", "2026-10-24-session-049-", "2026-10-24-session-060-"),
    ("U13", "Track-4 精読・検証ノート後半", "精読・検証ノート⑤ 四層精読III（貨幣・祈り・署名〜戦争）", "2026-10-24-session-060-", "2026-10-25-sky-"),
    ("U14", "Track-4 精読・検証ノート後半", "精読・検証ノート⑥ 書記室の外・暫定報告v2・軌道修正", "2026-10-25-sky-", "2026-10-28-warrant-"),
    ("U15", "Track-4 精読・検証ノート後半", "精読・検証ノート⑦ 10月末〜内部編年11月前半の再読群", "2026-10-28-warrant-", "2026-11-15-"),
    ("U16", "Track-4 精読・検証ノート後半", "精読・検証ノート⑧ 内部編年11月後半〜12月の原典・Git照合群", "2026-11-15-", None),
)

MATERIALS_SHARD_SPLIT = "2026-10-24-a"
ALL_UNIT_IDS = tuple(f"U{i:02d}" for i in range(1, 17))


@dataclass(frozen=True)
class UnitItem:
    target_kind: str
    target_id: str
    chars: int
    hint_quadrant: str
    hint_subcategories: tuple[str, ...]


@dataclass(frozen=True)
class WorkerUnit:
    unit_id: str
    track: str
    title: str
    rule: str
    items: tuple[UnitItem, ...]

    @property
    def total_chars(self) -> int:
        return sum(i.chars for i in self.items)


def motif_to_subcluster() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for code, (_label, mids) in MOTIF_SUBCLUSTERS.items():
        for mid in mids:
            mapping[mid] = code
    return mapping


def infer_motif_hint(motif_ids: list[str], m2s: dict[str, str]) -> tuple[str, tuple[str, ...]]:
    subs = sorted({m2s[m] for m in motif_ids if m in m2s})
    quads = sorted({s[0] for s in subs})
    q_map = {
        ("A",): "A_human",
        ("B",): "B_ai_self_db",
        ("C",): "C_interface",
        ("A", "B"): "AB_crossed",
        ("A", "C"): "AC_crossed",
        ("B", "C"): "BC_crossed",
        ("A", "B", "C"): "ABC_crossed",
    }
    return q_map.get(tuple(quads), "B_ai_self_db"), tuple(subs)


def load_errata(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in ledger_io.collection_files(root / "state" / "errata.jsonl"):
        if path.is_file():
            for line in ledger_io.read_text_stable(path).splitlines():
                if line.strip():
                    row = json.loads(line)
                    result[row["errata_id"]] = row
    return result


def list_infra_files(root: Path) -> list[Path]:
    """Return tracked non-state, non-readings, non-taxonomy repository files."""
    excluded_top = {"state", "readings", "taxonomy", "map", ".git", "__pycache__"}
    found: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in excluded_top or part.startswith(".pytest") for part in rel.parts):
            continue
        if rel.suffix in {".pyc", ".pyo"}:
            continue
        found.append(rel)
    return found


def is_governance_doc(rel: Path) -> bool:
    top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    if top in {"prompts", "migration", "docs"}:
        return True
    return top == "(root)" and rel.name in GOVERNANCE_DOC_ROOT_NAMES


def classify_infra_file(rel: Path) -> tuple[str, tuple[str, ...]]:
    if is_governance_doc(rel):
        return "D_infrastructure", ("D-1",)
    top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
    if top == "tools" and (
        "_audit" in rel.name
        or rel.name in {"breath_meter.py", "tanka_meter.py", "measure_texture.py"}
    ):
        return "D_infrastructure", ("D-3",)
    if top == "tests":
        return "D_infrastructure", ("D-4",)
    return "D_infrastructure", ("D-2",)


def file_char_len(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return path.stat().st_size


def build_units(root: Path = ROOT) -> list[WorkerUnit]:
    orig_root = inspect_inquiry.ROOT
    try:
        inspect_inquiry.ROOT = root
        data = inspect_inquiry.load_all()
    finally:
        inspect_inquiry.ROOT = orig_root

    errata = load_errata(root)
    m2s = motif_to_subcluster()

    # U01: motifs + questions + editorial_decisions + errata
    u01_items: list[UnitItem] = []
    for mid, m in data["motifs"].items():
        q_hint, subs = infer_motif_hint([mid], m2s)
        chars = len(m.get("label", "")) + len(m.get("description", ""))
        u01_items.append(UnitItem("motif", mid, chars, q_hint, subs))
    for qid, q in data["questions"].items():
        q_hint, subs = infer_motif_hint(q.get("motif_ids", []), m2s)
        chars = len(q.get("question", "")) + len(q.get("notes", ""))
        u01_items.append(UnitItem("question", qid, chars, q_hint, subs))
    for eid, ed in data["editorial_decisions"].items():
        u01_items.append(
            UnitItem("editorial_decision", eid, len(ed.get("reason", "")), "B_ai_self_db", ("B-3",))
        )
    for erid, er in errata.items():
        chars = len(er.get("claim", "")) + len(er.get("note", ""))
        u01_items.append(UnitItem("errata", erid, chars, "B_ai_self_db", ("B-3",)))

    # U02: fragments (all)
    u02_items: list[UnitItem] = []
    for fid, f in data["fragments"].items():
        q_hint, subs = infer_motif_hint(f.get("motif_ids", []), m2s)
        chars = len(f.get("title", "")) + len(f.get("text", "")) + len(f.get("editor_note", ""))
        u02_items.append(UnitItem("fragment", fid, chars, q_hint, subs))

    # U03: sessions + governance/prompts/docs/migration (D-1)
    u03_items: list[UnitItem] = []
    for sid, s in data["sessions"].items():
        chars = len(s.get("human_direction", "")) + len(s.get("notes", ""))
        u03_items.append(UnitItem("session", sid, chars, "C_interface", ("C-3", "B-3")))

    # U04: schema + tools + tests + viewer + CI + READING_MAP.md (D-2, D-3, D-4)
    u04_items: list[UnitItem] = []
    for rel in list_infra_files(root):
        q_hint, subs = classify_infra_file(rel)
        item = UnitItem("repo_file", rel.as_posix(), file_char_len(root / rel), q_hint, subs)
        if is_governance_doc(rel):
            u03_items.append(item)
        else:
            u04_items.append(item)

    # U05..U07: materials partitioned by immutable file origin (base vs shard split)
    u05_items: list[UnitItem] = []
    u06_items: list[UnitItem] = []
    u07_items: list[UnitItem] = []
    base_mat = root / "state" / "materials.jsonl"
    if base_mat.is_file():
        for line in ledger_io.read_text_stable(base_mat).splitlines():
            if not line.strip():
                continue
            m = json.loads(line)
            mid = m["material_id"]
            if mid not in data["materials"]:
                continue
            m_rec = data["materials"][mid]
            q_hint, subs = infer_motif_hint(m_rec.get("motif_ids", []), m2s)
            chars = sum(
                len(m_rec.get(k, ""))
                for k in ("title", "passage", "source_note", "literary_invitation", "scope_note")
            )
            u05_items.append(UnitItem("material", mid, chars, q_hint, subs))

    mat_shard_dir = root / "state" / "materials.d"
    seen_mat = {i.target_id for i in u05_items}
    if mat_shard_dir.is_dir():
        for sp in sorted(mat_shard_dir.glob("*.jsonl")):
            bucket = u06_items if sp.name < MATERIALS_SHARD_SPLIT else u07_items
            for line in ledger_io.read_text_stable(sp).splitlines():
                if not line.strip():
                    continue
                m = json.loads(line)
                mid = m["material_id"]
                if mid in seen_mat or mid not in data["materials"]:
                    continue
                seen_mat.add(mid)
                m_rec = data["materials"][mid]
                q_hint, subs = infer_motif_hint(m_rec.get("motif_ids", []), m2s)
                chars = sum(
                    len(m_rec.get(k, ""))
                    for k in ("title", "passage", "source_note", "literary_invitation", "scope_note")
                )
                bucket.append(UnitItem("material", mid, chars, q_hint, subs))

    # U08: relations + read_log
    u08_items: list[UnitItem] = []
    for rid, r in data["relations"].items():
        u08_items.append(UnitItem("relation", rid, len(r.get("note", "")), "B_ai_self_db", ("B-1", "B-3")))
    for rlid, rl in data["read_log"].items():
        u08_items.append(UnitItem("read_log", rlid, len(rl.get("note", "")), "B_ai_self_db", ("B-1",)))

    units: list[WorkerUnit] = [
        WorkerUnit(
            "U01",
            "Track-1 コア概念・作品・ガバナンス",
            "モチーフ(59)・問い(全件)・編集判断・訂正録",
            "state/{motifs,questions,editorial_decisions,errata}",
            tuple(u01_items),
        ),
        WorkerUnit(
            "U02",
            "Track-1 コア概念・作品・ガバナンス",
            "創作・批評断片アンソロジー全編（selected + draft）",
            "state/fragments(.jsonl + .d/*)",
            tuple(u02_items),
        ),
        WorkerUnit(
            "U03",
            "Track-1 コア概念・作品・ガバナンス",
            "セッション委任来歴全件＋憲章・方針・設計・プロンプト文書群",
            "state/sessions + root方針文書/docs/prompts/migration",
            tuple(u03_items),
        ),
        WorkerUnit(
            "U04",
            "Track-1 コア概念・作品・ガバナンス",
            "記憶DBの器・監査計器・検証基盤（schema/tools/tests/viewer/CI）",
            "schema/* + tools/* + tests/* + viewer/* + .github/* + READING_MAP.md",
            tuple(u04_items),
        ),
        WorkerUnit(
            "U05",
            "Track-2 収蔵素材・関係網・読み痕跡",
            "凍結ベース収蔵素材（ResearchOS移行＋初期人文学）",
            "state/materials.jsonl",
            tuple(u05_items),
        ),
        WorkerUnit(
            "U06",
            "Track-2 収蔵素材・関係網・読み痕跡",
            f"シャード収蔵素材 前半（< {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* < {MATERIALS_SHARD_SPLIT}",
            tuple(u06_items),
        ),
        WorkerUnit(
            "U07",
            "Track-2 収蔵素材・関係網・読み痕跡",
            f"シャード収蔵素材 後半（>= {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* >= {MATERIALS_SHARD_SPLIT}",
            tuple(u07_items),
        ),
        WorkerUnit(
            "U08",
            "Track-2 収蔵素材・関係網・読み痕跡",
            "解釈的関係エッジ＋読み返し痕跡ログ全件",
            "state/{relations,read_log}",
            tuple(u08_items),
        ),
    ]

    # U09..U16: readings/
    readings_dir = root / "readings"
    r_files = sorted(p for p in readings_dir.iterdir() if p.is_file()) if readings_dir.is_dir() else []
    for uid, track, label, lo, hi in READINGS_BOUNDS:
        sub_items: list[UnitItem] = []
        for p in r_files:
            if (lo is None or p.name >= lo) and (hi is None or p.name < hi):
                sub_items.append(
                    UnitItem(
                        "reading_note",
                        f"readings/{p.name}",
                        file_char_len(p),
                        "AB_crossed",
                        ("B-1", "B-2"),
                    )
                )
        rule = f"readings/[{lo or '*'} .. {hi or '*'})"
        units.append(WorkerUnit(uid, track, label, rule, tuple(sub_items)))

    return units


def completed_units(root: Path = ROOT) -> dict[str, list[str]]:
    shard_dir = root / "taxonomy" / "shards"
    done: dict[str, list[str]] = {}
    if not shard_dir.is_dir():
        return done
    for p in sorted(shard_dir.glob("*.jsonl")):
        uid = p.name.split("-", 1)[0]
        done.setdefault(uid, []).append(p.relative_to(root).as_posix())
    return done


def current_branch_seed(root: Path = ROOT) -> str:
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        branch = "local"
    if branch.startswith("arena/") and len(branch.split("/")[1]) >= 8:
        prefix = branch.split("/")[1].split("-")[0]
        try:
            int(prefix, 16)
            return prefix[:8]
        except ValueError:
            pass
    return hashlib.sha256(branch.encode("utf-8")).hexdigest()[:8]


def pick_auto_unit(units: list[WorkerUnit], done: dict[str, list[str]], seed_hex: str) -> WorkerUnit:
    pending = [u for u in units if u.unit_id not in done]
    pool = pending if pending else units
    idx = int(seed_hex, 16) % len(pool)
    return pool[idx]


def validate_taxonomy_shards(root: Path = ROOT) -> tuple[bool, list[str], int]:
    shard_dir = root / "taxonomy" / "shards"
    errors: list[str] = []
    row_count = 0
    seen_targets: dict[tuple[str, str], str] = {}
    if not shard_dir.is_dir():
        return True, [], 0

    required = {
        "record_id",
        "unit_id",
        "target_kind",
        "target_id",
        "primary_quadrant",
        "subcategories",
        "human_view_stance",
        "ai_self_db_stance",
        "return_status",
        "read_depth",
        "evidence_anchor",
    }
    valid_units = set(ALL_UNIT_IDS)

    for sp in sorted(shard_dir.glob("*.jsonl")):
        rel = sp.relative_to(root).as_posix()
        for lineno, line in enumerate(ledger_io.read_text_stable(sp).splitlines(), 1):
            if not line.strip():
                continue
            row_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}:{lineno}: invalid JSON: {exc}")
                continue
            missing = required - set(obj.keys())
            if missing:
                errors.append(f"{rel}:{lineno}: missing keys {sorted(missing)}")
                continue
            if obj["unit_id"] not in valid_units:
                errors.append(f"{rel}:{lineno}: invalid unit_id {obj['unit_id']!r}")
            if obj["target_kind"] not in VALID_TARGET_KINDS:
                errors.append(f"{rel}:{lineno}: invalid target_kind {obj['target_kind']!r}")
            if obj["primary_quadrant"] not in VALID_PRIMARY_QUADRANTS:
                errors.append(f"{rel}:{lineno}: invalid primary_quadrant {obj['primary_quadrant']!r}")
            subs = obj["subcategories"]
            if not isinstance(subs, list) or not subs or any(s not in VALID_SUBCATEGORIES for s in subs):
                errors.append(f"{rel}:{lineno}: invalid subcategories {subs!r}")
            if obj["return_status"] not in VALID_RETURN_STATUS:
                errors.append(f"{rel}:{lineno}: invalid return_status {obj['return_status']!r}")
            if obj["read_depth"] not in VALID_READ_DEPTH:
                errors.append(f"{rel}:{lineno}: invalid read_depth {obj['read_depth']!r}")

            tkey = (obj["target_kind"], obj["target_id"])
            if tkey in seen_targets:
                errors.append(
                    f"{rel}:{lineno}: duplicate classification for {tkey} (first at {seen_targets[tkey]})"
                )
            else:
                seen_targets[tkey] = f"{rel}:{lineno}"

    return len(errors) == 0, errors, row_count


def build_taxonomy_map(root: Path = ROOT) -> Path:
    ok, errors, _ = validate_taxonomy_shards(root)
    if not ok:
        raise ValueError("Cannot build taxonomy map with validation errors:\n" + "\n".join(errors))

    out_dir = root / "map" / "taxonomy"
    out_dir.mkdir(parents=True, exist_ok=True)
    shard_dir = root / "taxonomy" / "shards"
    rows: list[dict[str, Any]] = []
    if shard_dir.is_dir():
        for sp in sorted(shard_dir.glob("*.jsonl")):
            for line in ledger_io.read_text_stable(sp).splitlines():
                if line.strip():
                    rows.append(json.loads(line))

    by_quad = Counter(r["primary_quadrant"] for r in rows)
    by_ret = Counter(r["return_status"] for r in rows)
    by_unit = Counter(r["unit_id"] for r in rows)

    lines = [
        "# AIselfMySelf — 全成果物分類・体系化インデックス（生成物）",
        "",
        f"- 検証済み分類レコード総数: **{len(rows):,d}**",
        "",
        "## 1. 象限別集計",
        "",
        "| 象限 | 件数 |",
        "|---|---:|",
    ]
    for q, c in sorted(by_quad.items()):
        lines.append(f"| `{q}` | {c:,d} |")
    lines.extend(["", "## 2. 中心問いへの帰還ステータス別集計", "", "| 帰還状態 | 件数 |", "|---|---:|"])
    for st, c in sorted(by_ret.items()):
        lines.append(f"| `{st}` | {c:,d} |")
    lines.extend(["", "## 3. 処理単位（Unit）別進捗", "", "| Unit | 分類済み件数 |", "|---|---:|"])
    for uid in ALL_UNIT_IDS:
        lines.append(f"| `{uid}` | {by_unit.get(uid, 0):,d} |")

    index_path = out_dir / "00-taxonomy-overview.md"
    ledger_io.atomic_write_text(index_path, "\n".join(lines) + "\n")
    return index_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root")
    parser.add_argument("--unit", type=str, default=None, help="Unit ID (U01..U16) or 'auto'")
    parser.add_argument("--validate", action="store_true", help="Validate taxonomy/shards/*.jsonl")
    parser.add_argument("--build-map", action="store_true", help="Build map/taxonomy/ overview from shards")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()

    if args.validate:
        ok, errors, count = validate_taxonomy_shards(root)
        if not ok:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print(f"PASS: taxonomy shards valid (rows={count})")
        return 0

    if args.build_map:
        try:
            out = build_taxonomy_map(root)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"BUILT: {out.relative_to(root).as_posix()}")
        return 0

    units = build_units(root)
    done = completed_units(root)
    seed = current_branch_seed(root)

    if args.unit is not None:
        if args.unit == "auto":
            target = pick_auto_unit(units, done, seed)
        else:
            matches = [u for u in units if u.unit_id == args.unit.upper()]
            if not matches:
                print(f"Unknown unit: {args.unit} (expected U01..U16 or auto)", file=sys.stderr)
                return 2
            target = matches[0]

        shard_out = f"taxonomy/shards/{target.unit_id}-{seed}.jsonl"
        note_out = f"taxonomy/notes/{target.unit_id}-{seed}.md"
        if args.json:
            payload = {
                "unit_id": target.unit_id,
                "track": target.track,
                "title": target.title,
                "rule": target.rule,
                "branch_seed": seed,
                "item_count": len(target.items),
                "total_chars": target.total_chars,
                "output_shard": shard_out,
                "output_note": note_out,
                "items": [
                    {
                        "target_kind": it.target_kind,
                        "target_id": it.target_id,
                        "chars": it.chars,
                        "hint_quadrant": it.hint_quadrant,
                        "hint_subcategories": list(it.hint_subcategories),
                    }
                    for it in target.items
                ],
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        print(f"=== Worker Assignment: {target.unit_id} ({target.title}) ===")
        print(f"Track        : {target.track}")
        print(f"Partition    : {target.rule}")
        print(f"Items / Size : {len(target.items):,d} items / {target.total_chars:,d} chars")
        print(f"Output Shard : {shard_out} (append-only, isolated per branch)")
        print(f"Output Note  : {note_out}")
        print("\nSample assigned targets (first 15):")
        for it in target.items[:15]:
            print(
                f"  - [{it.target_kind:18s}] {it.target_id:45s} ({it.chars:7,d} chars) hint={it.hint_quadrant}"
            )
        if len(target.items) > 15:
            print(f"  ... (+{len(target.items) - 15:,d} more; pass --json for full manifest)")
        return 0

    if args.json:
        summary = {
            "branch_seed": seed,
            "total_units": len(units),
            "total_items": sum(len(u.items) for u in units),
            "total_chars": sum(u.total_chars for u in units),
            "units": [
                {
                    "unit_id": u.unit_id,
                    "track": u.track,
                    "title": u.title,
                    "rule": u.rule,
                    "item_count": len(u.items),
                    "total_chars": u.total_chars,
                    "completed_shards": done.get(u.unit_id, []),
                }
                for u in units
            ],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print("=== AIselfMySelf — Full-Repository Taxonomy & 16-Unit Parallel Plan ===")
    print(f"Branch seed          : {seed}")
    print(f"Total partition units: {len(units)} (4 Tracks x 4 Units = U01..U16)")
    print(f"Total assigned items : {sum(len(u.items) for u in units):,d} records & files")
    print(f"Total assigned chars : {sum(u.total_chars for u in units):,d} chars\n")
    for u in units:
        status = f"DONE ({len(done[u.unit_id])} shard)" if u.unit_id in done else "PENDING"
        print(
            f"  {u.unit_id} | {status:14s} | {len(u.items):6,d} items | {u.total_chars:9,d} chars | {u.title}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
