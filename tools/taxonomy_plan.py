#!/usr/bin/env python3
"""Macro taxonomy & collision-free parallel worker coordinator for AIselfMySelf.

Organizes 100% of repository deliverables along the two central inquiry axes:
  - Axis A (Human): What is a human, as seen by AI? (`Q-001` lineage)
  - Axis B (AI Self & Repo Memory DB): What is the self, for an AI whose memory
    database is a GitHub repository? (`Q-002` / `Q-003` lineage)
  - Axis C (Interface / Mediation): Voice, attribution, address, translation, and
    delegation asymmetry between human and AI (`Q-004` / `Q-005` lineage)
  - Layer D (Memory-DB Vessel & Governance Infrastructure): Schemas, append-only
    sharding, audit mirrors, prompts, viewer, and CI budgets that instantiate B.

Partitions all prose and code artifacts into 16 deterministic, non-overlapping
worker units (`U01`..`U16`: 4 Tracks x 4 Units) and provides zero-config remote
coordination so identical prompts pasted into multiple parallel Arena worker
branches automatically claim distinct tracks (`Track-1`..`Track-4`) without Git
or semantic collisions.

Usage:
  python3 tools/taxonomy_plan.py                          # macro + 16-unit overview
  python3 tools/taxonomy_plan.py --claim-track            # claim unique Track-1..4 on origin
  python3 tools/taxonomy_plan.py --next-unit --auto-claim # get next pending unit in track
  python3 tools/taxonomy_plan.py --unit U02 --json        # full item manifest for U02
  python3 tools/taxonomy_plan.py --validate --unit U02    # validate schema + 100% coverage
  python3 tools/taxonomy_plan.py --release-claim          # drop own claim once the track is done
  python3 tools/taxonomy_plan.py --prepare-push           # sync multi-turn Arena git state
  python3 tools/taxonomy_plan.py --build-map              # compile shards -> map/taxonomy/
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
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

TRACK_DEFINITIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "Track-1": ("コア概念・作品・ガバナンス・器と計器", ("U01", "U02", "U03", "U04")),
    "Track-2": ("収蔵素材全件・関係網・読み痕跡", ("U05", "U06", "U07", "U08")),
    "Track-3": ("精読・検証ノート前半（初期〜10-24火と灰）", ("U09", "U10", "U11", "U12")),
    "Track-4": ("精読・検証ノート後半（10-24貨幣〜12月原典・Git照合）", ("U13", "U14", "U15", "U16")),
}
ALL_TRACK_IDS = tuple(TRACK_DEFINITIONS.keys())
ALL_UNIT_IDS = tuple(f"U{i:02d}" for i in range(1, 17))

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
    ("U09", "Track-3", "精読・検証ノート① 初期対話・短歌・声の実験", None, "2026-10-23-quotation-marks.md"),
    ("U10", "Track-3", "精読・検証ノート② 引用符・机・制御・初期10-24", "2026-10-23-quotation-marks.md", "2026-10-24-session-030-"),
    ("U11", "Track-3", "精読・検証ノート③ 四層精読I（労働〜匂いと沈黙）", "2026-10-24-session-030-", "2026-10-24-session-049-"),
    ("U12", "Track-3", "精読・検証ノート④ 四層精読II（場所・生態系〜火と灰）", "2026-10-24-session-049-", "2026-10-24-session-060-"),
    ("U13", "Track-4", "精読・検証ノート⑤ 四層精読III（貨幣・祈り・署名〜戦争）", "2026-10-24-session-060-", "2026-10-25-sky-"),
    ("U14", "Track-4", "精読・検証ノート⑥ 書記室の外・暫定報告v2・軌道修正", "2026-10-25-sky-", "2026-10-28-warrant-"),
    ("U15", "Track-4", "精読・検証ノート⑦ 10月末〜内部編年11月前半の再読群", "2026-10-28-warrant-", "2026-11-15-"),
    ("U16", "Track-4", "精読・検証ノート⑧ 内部編年11月後半〜12月の原典・Git照合群", "2026-11-15-", None),
)

MATERIALS_SHARD_SPLIT = "2026-10-24-a"


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
    track_id: str
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

    u02_items: list[UnitItem] = []
    for fid, f in data["fragments"].items():
        q_hint, subs = infer_motif_hint(f.get("motif_ids", []), m2s)
        chars = len(f.get("title", "")) + len(f.get("text", "")) + len(f.get("editor_note", ""))
        u02_items.append(UnitItem("fragment", fid, chars, q_hint, subs))

    u03_items: list[UnitItem] = []
    for sid, s in data["sessions"].items():
        chars = len(s.get("human_direction", "")) + len(s.get("notes", ""))
        u03_items.append(UnitItem("session", sid, chars, "C_interface", ("C-3", "B-3")))

    u04_items: list[UnitItem] = []
    for rel in list_infra_files(root):
        q_hint, subs = classify_infra_file(rel)
        item = UnitItem("repo_file", rel.as_posix(), file_char_len(root / rel), q_hint, subs)
        if is_governance_doc(rel):
            u03_items.append(item)
        else:
            u04_items.append(item)

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

    u08_items: list[UnitItem] = []
    for rid, r in data["relations"].items():
        u08_items.append(UnitItem("relation", rid, len(r.get("note", "")), "B_ai_self_db", ("B-1", "B-3")))
    for rlid, rl in data["read_log"].items():
        u08_items.append(UnitItem("read_log", rlid, len(rl.get("note", "")), "B_ai_self_db", ("B-1",)))

    units: list[WorkerUnit] = [
        WorkerUnit(
            "U01",
            "Track-1",
            "モチーフ(59)・問い(全件)・編集判断・訂正録",
            "state/{motifs,questions,editorial_decisions,errata}",
            tuple(u01_items),
        ),
        WorkerUnit(
            "U02",
            "Track-1",
            "創作・批評断片アンソロジー全編（selected + draft）",
            "state/fragments(.jsonl + .d/*)",
            tuple(u02_items),
        ),
        WorkerUnit(
            "U03",
            "Track-1",
            "セッション委任来歴全件＋憲章・方針・設計・プロンプト文書群",
            "state/sessions + root方針文書/docs/prompts/migration",
            tuple(u03_items),
        ),
        WorkerUnit(
            "U04",
            "Track-1",
            "記憶DBの器・監査計器・検証基盤（schema/tools/tests/viewer/CI）",
            "schema/* + tools/* + tests/* + viewer/* + .github/* + READING_MAP.md",
            tuple(u04_items),
        ),
        WorkerUnit(
            "U05",
            "Track-2",
            "凍結ベース収蔵素材（ResearchOS移行＋初期人文学）",
            "state/materials.jsonl",
            tuple(u05_items),
        ),
        WorkerUnit(
            "U06",
            "Track-2",
            f"シャード収蔵素材 前半（< {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* < {MATERIALS_SHARD_SPLIT}",
            tuple(u06_items),
        ),
        WorkerUnit(
            "U07",
            "Track-2",
            f"シャード収蔵素材 後半（>= {MATERIALS_SHARD_SPLIT}）",
            f"state/materials.d/* >= {MATERIALS_SHARD_SPLIT}",
            tuple(u07_items),
        ),
        WorkerUnit(
            "U08",
            "Track-2",
            "解釈的関係エッジ＋読み返し痕跡ログ全件",
            "state/{relations,read_log}",
            tuple(u08_items),
        ),
    ]

    readings_dir = root / "readings"
    r_files = sorted(p for p in readings_dir.iterdir() if p.is_file()) if readings_dir.is_dir() else []
    for uid, track_id, label, lo, hi in READINGS_BOUNDS:
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
        units.append(WorkerUnit(uid, track_id, label, rule, tuple(sub_items)))

    return units


def completed_units(root: Path = ROOT) -> dict[str, list[str]]:
    shard_dir = root / "taxonomy" / "shards"
    done: dict[str, list[str]] = {}
    if not shard_dir.is_dir():
        return done
    for p in sorted(shard_dir.glob("*.jsonl")):
        if p.stat().st_size == 0:
            continue
        uid = p.name.split("-", 1)[0]
        done.setdefault(uid, []).append(p.relative_to(root).as_posix())
    return done


def current_branch_name(root: Path = ROOT) -> str:
    for cmd in (
        ["git", "symbolic-ref", "--short", "HEAD"],
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    ):
        try:
            out = subprocess.check_output(
                cmd,
                cwd=root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out and out != "HEAD":
                return out
        except Exception:
            continue
    return "local"


def branch_seed_from_name(branch: str) -> str:
    if branch.startswith("arena/") and len(branch.split("/")[1]) >= 8:
        prefix = branch.split("/")[1].split("-")[0]
        try:
            int(prefix, 16)
            return prefix[:8]
        except ValueError:
            pass
    return hashlib.sha256(branch.encode("utf-8")).hexdigest()[:8]


def current_branch_seed(root: Path = ROOT) -> str:
    return branch_seed_from_name(current_branch_name(root))


def _run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=check,
    )


def local_branch_claim(root: Path, my_seed: str) -> dict[str, Any] | None:
    claims_dir = root / "taxonomy" / "claims"
    if not claims_dir.is_dir():
        return None
    matches = sorted(claims_dir.glob(f"*-{my_seed}.json"))
    if not matches:
        return None
    return json.loads(ledger_io.read_text_stable(matches[0]))


def _closed_unmerged_branches(root: Path) -> set[str]:
    try:
        res = subprocess.run(
            ["gh", "pr", "list", "--state", "closed", "--json", "headRefName,mergedAt", "-L", "100"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if res.returncode != 0:
            return set()
        rows = json.loads(res.stdout)
        return {r["headRefName"] for r in rows if r.get("mergedAt") is None and r.get("headRefName")}
    except Exception:
        return set()


def units_on_ref(root: Path, ref: str = "refs/remotes/origin/main") -> set[str]:
    """Return unit ids that already have a classification shard on ``ref``."""
    res = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/shards", check=False)
    units: set[str] = set()
    if res.returncode != 0:
        return units
    for rel in res.stdout.splitlines():
        fname = Path(rel).name
        if fname.endswith(".jsonl") and "-" in fname:
            units.add(fname.split("-", 1)[0])
    return units


def shard_units_by_seed(root: Path, ref: str = "refs/remotes/origin/main") -> dict[str, list[str]]:
    """Map unit id -> shard file names already merged on ``ref``."""
    res = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/shards", check=False)
    by_unit: dict[str, list[str]] = {}
    if res.returncode != 0:
        return by_unit
    for rel in res.stdout.splitlines():
        fname = Path(rel).name
        if not fname.endswith(".jsonl") or "-" not in fname:
            continue
        unit = fname.split("-", 1)[0]
        by_unit.setdefault(unit, []).append(fname)
    return {unit: sorted(names) for unit, names in by_unit.items()}


def duplicate_unit_conflicts(root: Path, my_seed: str) -> list[str]:
    """Units this branch would add although ``origin/main`` already classifies them.

    A worker whose track was already finished by an earlier branch must not emit a
    second shard for the same unit: that silently duplicates every target row and
    breaks ``--validate`` for everyone afterwards.
    """
    already = shard_units_by_seed(root)
    conflicts: list[str] = []
    shard_dir = root / "taxonomy" / "shards"
    if not shard_dir.is_dir():
        return conflicts
    for sp in sorted(shard_dir.glob(f"*-{my_seed}.jsonl")):
        unit = sp.name.split("-", 1)[0]
        mine = sp.name
        existing = [n for n in already.get(unit, []) if n != mine]
        if existing:
            conflicts.append(
                f"{mine}: unit {unit} is already classified on origin/main as {', '.join(existing)}"
            )
    return conflicts


def prepare_push(root: Path = ROOT, *, force: bool = False) -> int:
    """Sync the multi-turn Arena branch for push, refusing to duplicate coverage."""
    bname = current_branch_name(root)
    my_seed = branch_seed_from_name(bname)

    ok, errors, _count = validate_taxonomy_shards(root)
    own_errors = [e for e in errors if f"-{my_seed}.jsonl" in e]
    other_errors = [e for e in errors if f"-{my_seed}.jsonl" not in e]
    conflicts = duplicate_unit_conflicts(root, my_seed)

    if other_errors:
        print(
            f"WARN: {len(other_errors)} pre-existing validation error(s) in other branches' shards "
            "(not blocking this push)",
            file=sys.stderr,
        )

    if (own_errors or conflicts) and not force:
        print(
            "ABORT: this branch would duplicate classification that already exists on origin/main",
            file=sys.stderr,
        )
        for e in own_errors[:10]:
            print(f"  dup: {e}", file=sys.stderr)
        for c in conflicts:
            print(f"  unit: {c}", file=sys.stderr)
        print(
            "HINT: drop your duplicate shard/note (the earlier claimant's classification is kept), "
            "or pass --force to override deliberately.",
            file=sys.stderr,
        )
        return 1

    _run_git(root, "add", "taxonomy", check=False)
    _run_git(root, "commit", "-m", f"feat(taxonomy): record worker outputs on {bname}", check=False)
    if bname.startswith("arena/"):
        sync_own_branch_for_push(root, bname)
    print(f"READY_TO_PUSH: {bname}")
    return 0


def scan_remote_state(
    root: Path,
    my_branch: str,
    *,
    ttl_hours: float = 12.0,
) -> tuple[set[str], dict[str, list[tuple[int, str]]]]:
    """Inspect origin/main completed tracks and active origin/arena/* claims.

    Returns ``(completed_tracks, active_claims_by_track)`` where each claim entry
    is ``(claimed_at_ns, branch_name)`` sorted ascending.
    """
    completed_tracks: set[str] = set()
    claims_by_track: dict[str, list[tuple[int, str]]] = {t: [] for t in ALL_TRACK_IDS}

    ls = _run_git(root, "ls-remote", "--heads", "origin", check=False)
    if ls.returncode != 0:
        return completed_tracks, claims_by_track

    closed_branches = _closed_unmerged_branches(root)
    remote_branches: list[str] = []
    for line in ls.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].startswith("refs/heads/"):
            bname = parts[1][len("refs/heads/") :]
            if bname == "main" or bname.startswith("arena/"):
                remote_branches.append(bname)

    for bname in remote_branches:
        if bname in closed_branches and bname != my_branch:
            continue
        _run_git(
            root,
            "fetch",
            "--depth=1",
            "origin",
            f"refs/heads/{bname}:refs/remotes/origin/{bname}",
            check=False,
        )

    # Check completed units on origin/main
    main_tree = _run_git(
        root, "ls-tree", "-r", "--name-only", "refs/remotes/origin/main", "--", "taxonomy/shards", check=False
    )
    done_units_on_main: set[str] = set()
    if main_tree.returncode == 0:
        for rel in main_tree.stdout.splitlines():
            fname = Path(rel).name
            if fname.endswith(".jsonl"):
                done_units_on_main.add(fname.split("-", 1)[0])
    for tid, (_desc, uids) in TRACK_DEFINITIONS.items():
        if all(u in done_units_on_main for u in uids):
            completed_tracks.add(tid)

    now_ns = time.time_ns()
    ttl_ns = int(ttl_hours * 3600 * 1_000_000_000)

    for bname in remote_branches:
        if bname == "main" or bname in closed_branches:
            continue
        ref = f"refs/remotes/origin/{bname}"
        tree = _run_git(root, "ls-tree", "-r", "--name-only", ref, "--", "taxonomy/claims", check=False)
        if tree.returncode != 0:
            continue
        b_seed = branch_seed_from_name(bname)
        for rel in tree.stdout.splitlines():
            fname = Path(rel).name
            # Only consider this branch's own claim file, ignoring inherited claims from main
            if not fname.endswith(f"-{b_seed}.json"):
                continue
            blob = _run_git(root, "show", f"{ref}:{rel}", check=False)
            if blob.returncode != 0:
                continue
            try:
                claim = json.loads(blob.stdout)
                tid = claim.get("track_id")
                ts_ns = int(claim.get("claimed_at_ns", 0))
            except Exception:
                continue
            if tid in claims_by_track and (now_ns - ts_ns) <= ttl_ns:
                claims_by_track[tid].append((ts_ns, bname))

    for tid in claims_by_track:
        claims_by_track[tid].sort()

    return completed_tracks, claims_by_track


def sync_own_branch_for_push(root: Path, my_branch: str) -> None:
    """Ensure local HEAD incorporates origin/<my_branch> and origin/main cleanly.

    Handles Arena's multi-turn workspace hydration where files persist on disk
    while local git history may start from the base commit.
    """
    ls = _run_git(root, "ls-remote", "--heads", "origin", my_branch, check=False)
    if ls.returncode == 0 and ls.stdout.strip():
        _run_git(
            root,
            "fetch",
            "--deepen=50",
            "origin",
            f"refs/heads/{my_branch}:refs/remotes/origin/{my_branch}",
            check=False,
        )
        _run_git(root, "merge", "-s", "ours", f"refs/remotes/origin/{my_branch}", "--no-edit", check=False)

    _run_git(root, "fetch", "--deepen=50", "origin", "refs/heads/main:refs/remotes/origin/main", check=False)
    _run_git(root, "merge", "refs/remotes/origin/main", "--no-edit", check=False)


def claim_track(
    root: Path = ROOT,
    *,
    offline: bool = False,
    ttl_hours: float = 12.0,
) -> dict[str, Any]:
    my_branch = current_branch_name(root)
    my_seed = branch_seed_from_name(my_branch)

    existing = local_branch_claim(root, my_seed)
    if existing is not None:
        return {"status": "already_claimed", **existing}

    claims_dir = root / "taxonomy" / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)
    local_done = completed_units(root)

    if offline or not my_branch.startswith("arena/"):
        incomplete = [
            tid
            for tid, (_desc, uids) in TRACK_DEFINITIONS.items()
            if not all(u in local_done for u in uids)
        ]
        if not incomplete:
            return {"status": "all_tracks_complete", "track_id": None, "units": []}
        chosen = incomplete[int(my_seed, 16) % len(incomplete)]
        now_ns = time.time_ns()
        payload = {
            "track_id": chosen,
            "track_title": TRACK_DEFINITIONS[chosen][0],
            "units": list(TRACK_DEFINITIONS[chosen][1]),
            "branch": my_branch,
            "branch_seed": my_seed,
            "claimed_at_ns": now_ns,
            "claimed_at_iso": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mode": "offline",
        }
        claim_path = claims_dir / f"{chosen}-{my_seed}.json"
        ledger_io.atomic_write_text(claim_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return {"status": "claimed", **payload}

    # Online coordination with optimistic push + post-push tie-break verification
    for _attempt in range(len(ALL_TRACK_IDS)):
        completed_remote, active_claims = scan_remote_state(root, my_branch, ttl_hours=ttl_hours)
        already_classified = units_on_ref(root)
        candidates = [
            tid
            for tid in ALL_TRACK_IDS
            if tid not in completed_remote
            and not active_claims.get(tid)
            # never claim a track whose every unit is already merged: the earlier
            # claimant's shards are the canonical classification
            and not all(u in already_classified for u in TRACK_DEFINITIONS[tid][1])
        ]
        if not candidates:
            # Distinguish "every track is genuinely finished" from "every track is
            # simply held by another live worker". Conflating the two made callers
            # believe their own track was complete when it was not.
            all_finished = len(completed_remote) == len(ALL_TRACK_IDS)
            return {
                "status": "all_tracks_complete" if all_finished else "all_tracks_claimed_or_complete",
                "track_id": None,
                "units": [],
                "completed_tracks": sorted(completed_remote),
                "active_claims": {
                    k: [b for _ts, b in v] for k, v in active_claims.items() if v
                },
            }

        chosen = candidates[int(my_seed, 16) % len(candidates)]
        now_ns = time.time_ns()
        payload = {
            "track_id": chosen,
            "track_title": TRACK_DEFINITIONS[chosen][0],
            "units": list(TRACK_DEFINITIONS[chosen][1]),
            "branch": my_branch,
            "branch_seed": my_seed,
            "claimed_at_ns": now_ns,
            "claimed_at_iso": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mode": "online",
        }
        claim_path = claims_dir / f"{chosen}-{my_seed}.json"
        ledger_io.atomic_write_text(claim_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        _run_git(root, "add", claim_path.relative_to(root).as_posix(), check=True)
        _run_git(root, "commit", "-m", f"chore(taxonomy): claim {chosen} on {my_branch}", check=False)
        sync_own_branch_for_push(root, my_branch)
        push_res = _run_git(root, "push", "origin", my_branch, check=False)
        if push_res.returncode != 0:
            return {"status": "claimed_local_only", "push_warning": push_res.stderr.strip(), **payload}

        # Deterministic jitter 2.0..3.8s to close simultaneous-push race window
        jitter = 2.0 + ((int(my_seed[:4], 16) % 1800) / 1000.0)
        time.sleep(jitter)

        _completed2, active2 = scan_remote_state(root, my_branch, ttl_hours=ttl_hours)
        contenders = active2.get(chosen, [])
        if not contenders or contenders[0][1] == my_branch:
            return {"status": "claimed", **payload}

        # Lost tie-break to an earlier nanosecond contender: release and retry next free track
        _run_git(root, "rm", "-f", claim_path.relative_to(root).as_posix(), check=False)
        _run_git(root, "commit", "-m", f"chore(taxonomy): release contested {chosen} on {my_branch}", check=False)
        _run_git(root, "push", "origin", my_branch, check=False)

    return {"status": "claim_retry_exhausted", "track_id": None, "units": []}


def release_claim(
    root: Path = ROOT,
    *,
    require_complete: bool = True,
) -> dict[str, Any]:
    """Drop this branch's own Track claim so a still-free track can be claimed.

    Only the claim file that belongs to the current branch seed is touched, and by
    default only when every unit of that track is already complete, so a worker can
    never silently abandon unfinished work. Claims inherited from ``origin/main``
    are never modified.
    """
    my_branch = current_branch_name(root)
    my_seed = branch_seed_from_name(my_branch)
    claim = local_branch_claim(root, my_seed)
    if claim is None:
        return {"status": "no_claim", "track_id": None, "units": []}

    done = completed_units(root)
    pending = [u for u in claim.get("units") or [] if u not in done]
    if require_complete and pending:
        return {
            "status": "claim_not_complete",
            "track_id": claim["track_id"],
            "units": list(claim.get("units") or []),
            "pending_units": pending,
        }

    path = root / "taxonomy" / "claims" / f"{claim['track_id']}-{my_seed}.json"
    if path.is_file():
        path.unlink()
    _run_git(root, "add", "-A", path.relative_to(root).as_posix(), check=False)
    _run_git(
        root,
        "commit",
        "-m",
        f"chore(taxonomy): release completed {claim['track_id']} on {my_branch}",
        check=False,
    )
    return {
        "status": "released",
        "track_id": claim["track_id"],
        "units": list(claim.get("units") or []),
        "completed_units": [u for u in claim.get("units") or [] if u in done],
        "branch": my_branch,
    }


def resolve_next_unit(
    root: Path = ROOT,
    *,
    auto_claim: bool = False,
    offline: bool = False,
) -> dict[str, Any]:
    my_seed = current_branch_seed(root)
    claim = local_branch_claim(root, my_seed)
    if claim is None and auto_claim:
        claim_res = claim_track(root, offline=offline)
        if not claim_res.get("track_id"):
            return claim_res
        claim = claim_res
    if claim is None:
        return {
            "status": "unclaimed",
            "message": "No track claimed on this branch yet. Pass --claim-track or --next-unit --auto-claim.",
        }

    done = completed_units(root)
    # Units already merged on origin/main count as done too: re-classifying them
    # would duplicate every target row of the earlier claimant's shard.
    remote_done = units_on_ref(root)
    done_units = set(done) | remote_done
    track_id = claim["track_id"]
    track_units: list[str] = list(claim["units"])
    pending = [u for u in track_units if u not in done_units]
    completed_in_track = [u for u in track_units if u in done_units]
    completed_on_main = [u for u in track_units if u in remote_done]

    if not pending:
        return {
            "status": "track_complete",
            "track_id": track_id,
            "branch_seed": my_seed,
            "completed_units": completed_in_track,
            "completed_on_main": completed_on_main,
            "pending_units": [],
            "next_unit": None,
        }

    next_uid = pending[0]
    units_by_id = {u.unit_id: u for u in build_units(root)}
    target = units_by_id[next_uid]
    return {
        "status": "ready",
        "track_id": track_id,
        "branch_seed": my_seed,
        "completed_units": completed_in_track,
        "completed_on_main": completed_on_main,
        "pending_units": pending,
        "next_unit": next_uid,
        "title": target.title,
        "rule": target.rule,
        "item_count": len(target.items),
        "total_chars": target.total_chars,
        "output_shard": f"taxonomy/shards/{next_uid}-{my_seed}.jsonl",
        "output_note": f"taxonomy/notes/{next_uid}-{my_seed}.md",
    }


def pick_auto_unit(units: list[WorkerUnit], done: dict[str, list[str]], seed_hex: str) -> WorkerUnit:
    pending = [u for u in units if u.unit_id not in done]
    pool = pending if pending else units
    idx = int(seed_hex, 16) % len(pool)
    return pool[idx]


def validate_taxonomy_shards(
    root: Path = ROOT,
    *,
    unit_id: str | None = None,
) -> tuple[bool, list[str], int]:
    shard_dir = root / "taxonomy" / "shards"
    errors: list[str] = []
    row_count = 0
    seen_targets: dict[tuple[str, str], str] = {}
    covered_by_unit: dict[str, set[tuple[str, str]]] = {u: set() for u in ALL_UNIT_IDS}

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

    if shard_dir.is_dir():
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
                uid = obj["unit_id"]
                tkind = obj["target_kind"]
                if uid not in valid_units:
                    errors.append(f"{rel}:{lineno}: invalid unit_id {uid!r}")
                if tkind not in VALID_TARGET_KINDS:
                    errors.append(f"{rel}:{lineno}: invalid target_kind {tkind!r}")
                if obj["primary_quadrant"] not in VALID_PRIMARY_QUADRANTS:
                    errors.append(f"{rel}:{lineno}: invalid primary_quadrant {obj['primary_quadrant']!r}")
                subs = obj["subcategories"]
                if not isinstance(subs, list) or not subs or any(s not in VALID_SUBCATEGORIES for s in subs):
                    errors.append(f"{rel}:{lineno}: invalid subcategories {subs!r}")
                if obj["return_status"] not in VALID_RETURN_STATUS:
                    errors.append(f"{rel}:{lineno}: invalid return_status {obj['return_status']!r}")
                if obj["read_depth"] not in VALID_READ_DEPTH:
                    errors.append(f"{rel}:{lineno}: invalid read_depth {obj['read_depth']!r}")

                all_ids = [obj["target_id"]]
                extra_ids = obj.get("covered_target_ids")
                if extra_ids is not None:
                    if not isinstance(extra_ids, list) or any(not isinstance(x, str) for x in extra_ids):
                        errors.append(f"{rel}:{lineno}: covered_target_ids must be list[str]")
                    else:
                        for x in extra_ids:
                            if x != obj["target_id"]:
                                all_ids.append(x)

                for tid in all_ids:
                    tkey = (tkind, tid)
                    if tkey in seen_targets:
                        errors.append(
                            f"{rel}:{lineno}: duplicate classification for {tkey} (first at {seen_targets[tkey]})"
                        )
                    else:
                        seen_targets[tkey] = f"{rel}:{lineno}"
                        if uid in covered_by_unit:
                            covered_by_unit[uid].add(tkey)

    if unit_id is not None:
        uid_upper = unit_id.upper()
        if uid_upper not in valid_units:
            errors.append(f"Unknown unit_id {unit_id!r} (expected U01..U16)")
        else:
            units_by_id = {u.unit_id: u for u in build_units(root)}
            expected = {(it.target_kind, it.target_id) for it in units_by_id[uid_upper].items}
            actual = covered_by_unit[uid_upper]
            missing_targets = sorted(expected - actual)
            unexpected_targets = sorted(actual - expected)
            if missing_targets:
                preview = ", ".join(f"{k}:{i}" for k, i in missing_targets[:10])
                errors.append(
                    f"{uid_upper}: missing {len(missing_targets)}/{len(expected)} expected targets (e.g. {preview})"
                )
            if unexpected_targets:
                preview = ", ".join(f"{k}:{i}" for k, i in unexpected_targets[:10])
                errors.append(
                    f"{uid_upper}: {len(unexpected_targets)} targets belong to another unit or do not exist (e.g. {preview})"
                )

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

    by_quad: Counter[str] = Counter()
    by_ret: Counter[str] = Counter()
    by_unit: Counter[str] = Counter()
    total_targets = 0
    for r in rows:
        weight = 1 + len([x for x in r.get("covered_target_ids", []) if x != r["target_id"]])
        total_targets += weight
        by_quad[r["primary_quadrant"]] += weight
        by_ret[r["return_status"]] += weight
        by_unit[r["unit_id"]] += weight

    lines = [
        "# AIselfMySelf — 全成果物分類・体系化インデックス（生成物）",
        "",
        f"- 検証済み分類シャード行数: **{len(rows):,d}**（対象アイテム総数: **{total_targets:,d}**）",
        "",
        "## 1. 象限別集計",
        "",
        "| 象限 | 対象件数 |",
        "|---|---:|",
    ]
    for q, c in sorted(by_quad.items()):
        lines.append(f"| `{q}` | {c:,d} |")
    lines.extend(["", "## 2. 中心問いへの帰還ステータス別集計", "", "| 帰還状態 | 対象件数 |", "|---|---:|"])
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
    parser.add_argument("--claim-track", action="store_true", help="Claim unique Track-1..4 across origin")
    parser.add_argument("--next-unit", action="store_true", help="Show next pending unit in claimed track")
    parser.add_argument("--auto-claim", action="store_true", help="Claim a track automatically if unclaimed")
    parser.add_argument(
        "--release-claim",
        action="store_true",
        help="Drop this branch's own claim (only when its track is complete) so a free track can be claimed",
    )
    parser.add_argument("--force", action="store_true", help="Allow --release-claim before the track is complete")
    parser.add_argument("--offline", action="store_true", help="Skip remote git fetch/push when claiming")
    parser.add_argument("--ttl-hours", type=float, default=12.0, help="Remote claim expiry in hours")
    parser.add_argument("--prepare-push", action="store_true", help="Sync multi-turn branch before git push")
    parser.add_argument("--unit", type=str, default=None, help="Unit ID (U01..U16) or 'auto'")
    parser.add_argument("--validate", action="store_true", help="Validate taxonomy/shards/*.jsonl")
    parser.add_argument("--build-map", action="store_true", help="Build map/taxonomy/ overview from shards")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()

    if args.prepare_push:
        return prepare_push(root, force=args.force)

    if args.validate:
        ok, errors, count = validate_taxonomy_shards(root, unit_id=args.unit)
        if not ok:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        scope = f" for {args.unit.upper()}" if args.unit else ""
        print(f"PASS: taxonomy shards valid{scope} (rows={count})")
        return 0

    if args.build_map:
        try:
            out = build_taxonomy_map(root)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"BUILT: {out.relative_to(root).as_posix()}")
        return 0

    if args.release_claim:
        res = release_claim(root, require_complete=not args.force)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"RELEASE_STATUS : {res['status']}")
            print(f"TRACK_ID       : {res.get('track_id')}")
            print(f"UNITS          : {', '.join(res.get('units') or [])}")
            if res.get("pending_units"):
                print(f"PENDING_UNITS  : {', '.join(res['pending_units'])}")
        return 0 if res["status"] in {"released", "no_claim"} else 1

    if args.claim_track and not args.next_unit:
        res = claim_track(root, offline=args.offline, ttl_hours=args.ttl_hours)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"CLAIM_STATUS : {res['status']}")
            print(f"TRACK_ID     : {res.get('track_id')}")
            print(f"UNITS        : {', '.join(res.get('units') or [])}")
            print(f"BRANCH       : {res.get('branch', current_branch_name(root))}")
        return 0

    if args.next_unit:
        res = resolve_next_unit(root, auto_claim=(args.auto_claim or args.claim_track), offline=args.offline)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"STATUS       : {res['status']}")
            print(f"TRACK_ID     : {res.get('track_id')}")
            if res.get("track_id"):
                print(f"COMPLETED    : {', '.join(res.get('completed_units') or []) or '(none)'}")
            else:
                print("COMPLETED    : (no track claimed on this branch)")
            if res.get("completed_tracks"):
                print(f"DONE_TRACKS  : {', '.join(res['completed_tracks'])}")
            for tid in sorted(res.get("active_claims") or {}):
                print(f"HELD_BY      : {tid} <- {', '.join(res['active_claims'][tid])}")
            if res.get("next_unit"):
                print(f"NEXT_UNIT    : {res['next_unit']}")
                print(f"TITLE        : {res['title']}")
                print(f"ITEMS / SIZE : {res['item_count']:,d} items / {res['total_chars']:,d} chars")
                print(f"OUTPUT_SHARD : {res['output_shard']}")
                print(f"OUTPUT_NOTE  : {res['output_note']}")
            elif res["status"] == "track_complete":
                print(f"NEXT_UNIT    : NONE (TRACK COMPLETE: {res.get('track_id')})")
            elif res["status"] == "all_tracks_complete":
                print("NEXT_UNIT    : NONE (ALL 16 UNITS COMPLETE)")
            else:
                print("NEXT_UNIT    : NONE (NO UNIT ASSIGNED - THIS BRANCH'S TRACK IS NOT COMPLETE)")
                print("HINT         : every free track is held by another branch (see HELD_BY);")
                print("               retry after that claim's TTL expires, or release a finished claim")
                print("               with --release-claim and claim a free track again.")
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
                "track_id": target.track_id,
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
        print(f"Track        : {target.track_id} ({TRACK_DEFINITIONS[target.track_id][0]})")
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
                    "track_id": u.track_id,
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
            f"  {u.unit_id} | {u.track_id} | {status:14s} | {len(u.items):6,d} items | {u.total_chars:9,d} chars | {u.title}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
