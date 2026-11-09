"""Tests for tools/peripheralisation.py — the archive-level Rp+/Rp-/Nrp mirror.

These fixtures are synthetic.  The real ledger is deliberately *not* read here:
the decision rule in
``readings/2026-11-08-a-pre-registered-count-of-what-was-not-mentioned.md`` §4
was committed before the instrument was first pointed at ``state/``, and a test
that asserted a real-corpus number would quietly turn a pre-registered design
into a post-hoc one.

What is pinned:

  * the three conditions are assigned by *mention* and by *shared motif*, not by
    recency or by order inside a file;
  * materials without ``motif_ids`` can never be Rp- (no category-mate exists);
  * the outcome window is strictly later in ``started_at`` date — same-day
    sessions are neither pool nor outcome, because 583 of 602 rows are date-only
    and the archive cannot rank them;
  * ``next_day`` and ``any_later`` really differ;
  * rows marked 機械的バックフィル never reach the secondary outcome;
  * the verdict reports ``underpowered`` instead of deciding on a thin sample.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import peripheralisation  # noqa: E402

COLLECTIONS = (
    "questions", "motifs", "materials", "fragments", "relations",
    "sessions", "read_log", "editorial_decisions", "errata", "notes",
)


def material(mid: str, motifs: tuple[str, ...]) -> dict:
    return {
        "material_id": mid,
        "kind": "research_excerpt",
        "title": mid,
        "source": {"source_id": mid, "title": mid, "authors": [], "year": 2026, "url": "https://example.invalid"},
        "passage": "p",
        "passage_language": "ja",
        "context": "c",
        "source_note": "s",
        "literary_invitation": "l",
        "scope_note": "s",
        "motif_ids": list(motifs),
    }


def session(sid: str, day: str, questions: tuple[str, ...], ctx: tuple[str, ...]) -> dict:
    return {
        "session_id": sid,
        "started_at": day,
        "human_direction": "委任",
        "question_ids": list(questions),
        "context_material_ids": list(ctx),
        "produced_fragment_ids": [],
        "new_question_ids": [],
        "prompt_template": "prompts/start.md",
    }


def read_row(rid: str, sid: str, mid: str, note: str) -> dict:
    return {
        "read_id": rid,
        "session_id": sid,
        "target": {"type": "material", "id": mid},
        "reading": "used_as_context",
        "note": note,
        "created_at": "2026-01-03",
    }


def make_repo(tmp: Path, *, read_log: tuple[dict, ...] = ()) -> Path:
    root = Path(tmp) / "repo"
    (root / "state").mkdir(parents=True)
    for name in COLLECTIONS:
        (root / "state" / f"{name}.jsonl").write_text("", encoding="utf-8")

    materials = [
        material("MAT-A1", ("MOTIF-A",)),
        material("MAT-A2", ("MOTIF-A",)),
        material("MAT-B1", ("MOTIF-B",)),
        material("MAT-N1", ()),
    ]
    sessions = [
        # A seeds the pool.  B mentions only MAT-A1.  C is the next active day.
        # D is a later day, visible to --outcome any_later only.
        session("SESSION-A", "2026-01-01", ("Q-001",), ("MAT-A1", "MAT-A2", "MAT-B1", "MAT-N1")),
        session("SESSION-B", "2026-01-02", ("Q-001",), ("MAT-A1",)),
        session("SESSION-C", "2026-01-03", ("Q-001",), ("MAT-A2",)),
        session("SESSION-D", "2026-01-05", ("Q-001",), ("MAT-B1",)),
    ]
    (root / "state" / "materials.jsonl").write_text(
        "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in materials), encoding="utf-8"
    )
    (root / "state" / "sessions.jsonl").write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in sessions), encoding="utf-8"
    )
    if read_log:
        (root / "state" / "read_log.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in read_log), encoding="utf-8"
        )
    return root


class PeripheralisationTests(unittest.TestCase):
    def clusters_by_session(self, root: Path, **kwargs) -> dict[str, peripheralisation.Cluster]:
        clusters, _meta = peripheralisation.collect(root, **kwargs)
        return {c.session_id: c for c in clusters}

    def test_conditions_are_assigned_by_mention_and_shared_motif(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            cluster = self.clusters_by_session(root)["SESSION-B"]
            # pool from SESSION-A = {A1, A2, B1, N1}; B mentions only A1.
            self.assertEqual(cluster.n["Rp+"], 1)   # MAT-A1
            self.assertEqual(cluster.n["Rp-"], 1)   # MAT-A2 shares MOTIF-A
            self.assertEqual(cluster.n["Nrp"], 2)   # MAT-B1 and motif-less MAT-N1
            self.assertEqual(cluster.outcome_day, "2026-01-03")

    def test_material_without_motifs_can_never_be_rp_minus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            # Give the motif-less material a second category-mate-free twin and
            # confirm it still lands in Nrp rather than Rp-.
            cluster = self.clusters_by_session(root)["SESSION-C"]
            # pool = A ∪ B mentions = {A1, A2, B1, N1}; C mentions MAT-A2.
            self.assertEqual(cluster.n["Rp+"], 1)   # MAT-A2
            self.assertEqual(cluster.n["Rp-"], 1)   # MAT-A1 shares MOTIF-A
            self.assertEqual(cluster.n["Nrp"], 2)   # MAT-B1, MAT-N1

    def test_outcome_counts_only_the_next_active_day(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            cluster = self.clusters_by_session(root)["SESSION-B"]
            # Next active day (2026-01-03) returns MAT-A2 only.
            self.assertEqual(cluster.hit["Rp+"], 0)   # MAT-A1 not returned
            self.assertEqual(cluster.hit["Rp-"], 1)   # MAT-A2 returned
            self.assertEqual(cluster.hit["Nrp"], 0)   # MAT-B1 returns only on 01-05

    def test_any_later_widens_the_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            cluster = self.clusters_by_session(root, outcome="any_later")["SESSION-B"]
            self.assertEqual(cluster.hit["Nrp"], 1)   # MAT-B1 returns on 2026-01-05
            self.assertEqual(cluster.outcome_day, "2026-01-03..2026-01-05")

    def test_same_day_sessions_are_neither_pool_nor_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            extra = root / "state" / "sessions.d"
            extra.mkdir()
            twin = session("SESSION-B2", "2026-01-02", ("Q-001",), ("MAT-B1",))
            (extra / "2026-01-02-aaaaaaaaaaaa.jsonl").write_text(
                json.dumps(twin, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            cluster = self.clusters_by_session(root)["SESSION-B"]
            # MAT-B1 was mentioned by a same-day session, which cannot be "earlier".
            self.assertEqual(cluster.n["Nrp"], 2)
            # ... and the same-day session cannot serve as the outcome window.
            self.assertEqual(cluster.outcome_day, "2026-01-03")
            self.assertEqual(cluster.hit["Nrp"], 0)

    def test_sessions_without_a_shared_question_do_not_open_a_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            extra = root / "state" / "sessions.d"
            extra.mkdir()
            other = session("SESSION-X", "2026-01-03", ("Q-999",), ("MAT-A1",))
            (extra / "2026-01-03-bbbbbbbbbbbb.jsonl").write_text(
                json.dumps(other, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            clusters = self.clusters_by_session(root)
            # SESSION-C still owns 2026-01-03 for Q-001, so B's window is unchanged.
            self.assertEqual(clusters["SESSION-B"].outcome_day, "2026-01-03")
            self.assertEqual(clusters["SESSION-B"].hit["Rp+"], 0)
            # SESSION-X shares no question with anything, so it has no pool.
            self.assertNotIn("SESSION-X", clusters)

    def test_backfill_rows_never_reach_the_secondary_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(
                Path(tmp),
                read_log=(
                    read_row("READ-1", "SESSION-C", "MAT-B1", "機械的バックフィル"),
                    read_row("READ-2", "SESSION-C", "MAT-N1", "手で書いた読み"),
                ),
            )
            primary = self.clusters_by_session(root)["SESSION-B"]
            self.assertEqual(primary.hit_secondary["Nrp"], 1)   # MAT-N1 hand-written only
            clusters, _meta = peripheralisation.collect(root)
            by_id = {c.session_id: c for c in clusters}
            self.assertEqual(by_id["SESSION-B"].hit["Nrp"], 0)  # MAT-B1 backfill excluded

    def test_verdict_is_underpowered_on_a_thin_sample(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            clusters, _meta = peripheralisation.collect(root)
            self.assertLess(len(clusters), 10)
            self.assertEqual(peripheralisation.verdict(clusters)["status"], "underpowered")

    def test_bootstrap_is_deterministic_for_a_fixed_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            clusters, _meta = peripheralisation.collect(root)
            first = peripheralisation.clustered_bootstrap(clusters, "Rp-", "Nrp", reps=200, seed=7)
            second = peripheralisation.clustered_bootstrap(clusters, "Rp-", "Nrp", reps=200, seed=7)
            self.assertEqual(first, second)

    def test_summary_reports_confound_distributions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            clusters, meta = peripheralisation.collect(root)
            summary = peripheralisation.summarize(clusters, meta, reps=50)
            self.assertEqual(summary["meta"]["outcome"], "next_day")
            self.assertIn("Rp-", summary["age_histogram"])
            self.assertGreaterEqual(summary["conditions"]["Nrp"]["mean_motif_count"], 0.0)
            self.assertEqual(summary["conditions"]["Rp-"]["mean_motif_count"], 1.0)

    def test_render_names_the_mirror_and_not_a_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            clusters, meta = peripheralisation.collect(root)
            text = peripheralisation.render(peripheralisation.summarize(clusters, meta, reps=50))
            self.assertIn("鏡であって判定ではない", text)
            self.assertIn("Rp+", text)

    def test_main_runs_on_a_synthetic_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            self.assertEqual(peripheralisation.main(["--root", str(root), "--bootstrap", "20"]), 0)
            self.assertEqual(
                peripheralisation.main(
                    ["--root", str(root), "--bootstrap", "20", "--outcome", "any_later", "--json"]
                ),
                0,
            )
            self.assertEqual(
                peripheralisation.main(["--root", str(root), "--bootstrap", "20", "--secondary"]), 0
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
