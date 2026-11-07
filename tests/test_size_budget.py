import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import size_budget


def make_repo(root: Path, overrides: dict[str, int] | None = None) -> None:
    sizes = {b.rel_path: 128 for b in size_budget.BUDGETS}
    if overrides:
        sizes.update(overrides)
    for rel, num_bytes in sizes.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * num_bytes)


class SizeBudgetTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = size_budget.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_within_soft_limits_passes_even_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            code, out, _ = self.run_cli("--strict", "--root", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("PASS", out)

    def test_soft_exceeded_warns_by_default_and_fails_in_strict_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root, {"README.md": 40 * 1024})  # > 32 KiB soft, < 96 KiB hard
            code, out, _ = self.run_cli("--root", str(root))
            self.assertEqual(code, 0, out)
            self.assertIn("WARN", out)

            strict_code, _, strict_err = self.run_cli("--strict", "--root", str(root))
            self.assertEqual(strict_code, 1)
            self.assertIn("--strict", strict_err)

    def test_hard_exceeded_always_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root, {"README.md": 120 * 1024})  # > 96 KiB hard
            code, _, err = self.run_cli("--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("hard", err)

    def test_scratch_script_in_tools_immediately_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            tools_dir = root / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)
            (tools_dir / "_session99_data.py").write_text("x = 1\n", encoding="utf-8")
            code, out, err = self.run_cli("--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("_session99_data.py", out)
            self.assertIn("FAIL", err)

    def test_shard_directory_count_and_bytes_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            mat_d = root / "state" / "materials.d"
            mat_d.mkdir(parents=True, exist_ok=True)
            for idx in range(85):  # > 80 soft_shards, < 160 hard_shards
                (mat_d / f"2026-10-25-{idx:012x}.jsonl").write_text("{}", encoding="utf-8")
            code, out, _ = self.run_cli("--root", str(root))
            self.assertEqual(code, 0)
            self.assertIn("WARN", out)
            strict_code, _, _ = self.run_cli("--strict", "--root", str(root))
            self.assertEqual(strict_code, 1)

    def test_json_output_is_well_formed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            code, out, _ = self.run_cli("--json", "--root", str(root))
            self.assertEqual(code, 0, out)
            parsed = json.loads(out)
            rels = {row["rel_path"] for row in parsed}
            for b in size_budget.BUDGETS:
                self.assertIn(b.rel_path, rels)

    def test_sessions_dir_leaves_room_for_one_more_row(self):
        """The repository must always be able to accept one more session row.

        A session adds exactly one row to `state/sessions.d/`, so a state with
        less headroom than one row is a state in which *no* session can pass
        `--strict` — and it cannot be escaped by compacting shards, because
        merging preserves every row's bytes (it only reduces the file count).
        That is exactly what happened on 2026-11-07: 2,096,967 B against a 2 MiB
        soft limit left 185 B, while the smallest schema-valid session row is
        217 B.  The remedy was to rescale the budget, not to shorten every row
        (see ERR-20261107-259d5f).  This test fails if the margin vanishes again.
        """
        required = {
            "session_id", "started_at", "human_direction", "question_ids",
            "context_material_ids", "produced_fragment_ids", "new_question_ids",
            "prompt_template",
        }
        row = {
            "session_id": "SESSION-20261107-6ffb13",
            "started_at": "2026-11-07",
            "human_direction": "",
            "question_ids": [],
            "context_material_ids": [],
            "produced_fragment_ids": [],
            "new_question_ids": [],
            "prompt_template": "",
        }
        self.assertEqual(set(row), required)
        minimal = len((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode())

        budget = next(b for b in size_budget.SHARD_BUDGETS if b.rel_dir == "state/sessions.d")
        shard_dir = size_budget.ROOT / budget.rel_dir
        if not shard_dir.is_dir():
            self.skipTest("no state/sessions.d in this checkout")
        used = sum(p.stat().st_size for p in shard_dir.glob("*.jsonl"))
        headroom = budget.soft_bytes - used

        self.assertGreaterEqual(
            headroom,
            minimal,
            f"state/sessions.d/ uses {used:,} B against a {budget.soft_bytes:,} B "
            f"soft budget, leaving {headroom:,} B — less than one minimal session "
            f"row ({minimal:,} B). No session can pass --strict, and shard "
            f"compaction cannot help (it preserves bytes). Shorten rows or "
            f"rescale the budget.",
        )

    def test_real_repository_is_within_strict_limits(self):
        code, out, err = self.run_cli("--strict", "--root", str(size_budget.ROOT))
        self.assertEqual(code, 0, out + err)


if __name__ == "__main__":
    unittest.main()
