"""End-to-end test: three sessions append to their own shards concurrently."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


WORKER = textwrap.dedent(
    """
    import json
    import subprocess
    import sys
    from pathlib import Path

    repo = Path.cwd()
    slot = int(sys.argv[1])

    def run(*args):
        result = subprocess.run(
            [sys.executable, *args], capture_output=True, text=True, cwd=repo
        )
        if result.returncode != 0:
            raise SystemExit(f"{args} failed: {result.stdout}\\n{result.stderr}")
        return result.stdout.strip()

    suffix = f"{slot:012x}"

    def shard(collection):
        path = Path(
            run(
                "tools/new_ledger_shard.py",
                collection,
                "--create",
                "--date",
                "2026-10-21",
                "--suffix",
                suffix,
            )
        )
        return path if path.is_absolute() else repo / path

    fragment_id = run("tools/new_id.py", "FRAG", "--date", "20261021")
    question_id = run("tools/new_id.py", "Q", "--date", "20261021")
    relation_id = run("tools/new_id.py", "REL", "--date", "20261021")
    session_id = run("tools/new_id.py", "SESSION", "--date", "20261021")

    fragment = {
        "fragment_id": fragment_id,
        "created_at": "2026-10-21",
        "language": "ja",
        "form": "fragment",
        "title": f"parallel session {slot}",
        "text": "A body written in a private shard.",
        "narrator_mode": "other",
        "question_ids": [question_id],
        "motif_ids": ["MOTIF-002"],
        "material_ids": ["MAT-LIT-001"],
        "status": "draft",
        "session_id": session_id,
    }
    question = {
        "question_id": question_id,
        "question": f"What does parallel session {slot} leave open?",
        "status": "open",
        "motif_ids": ["MOTIF-002"],
        "material_ids": [],
        "previous_question_ids": ["Q-001"],
        "origin": {"kind": "session", "detail": "parallel-session test"},
        "created_at": "2026-10-21",
    }
    relation = {
        "relation_id": relation_id,
        "left": {"type": "fragment", "id": fragment_id},
        "relation_type": "echo",
        "right": {"type": "question", "id": question_id},
        "note": "written concurrently",
        "created_at": "2026-10-21",
    }
    session = {
        "session_id": session_id,
        "started_at": "2026-10-21",
        "human_direction": "write in a shard while other sessions do the same",
        "question_ids": [question_id],
        "context_material_ids": ["MAT-LIT-001"],
        "produced_fragment_ids": [fragment_id],
        "new_question_ids": [question_id],
        "prompt_template": "prompts/continuation.md",
    }

    def append(path, record):
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\\n")
            handle.flush()

    append(shard("fragments"), fragment)
    append(shard("questions"), question)
    append(shard("relations"), relation)
    append(shard("sessions"), session)
    print(json.dumps({"fragment": fragment_id, "question": question_id}))
    """
)


def copy_repo(destination: Path) -> Path:
    repo = destination / "repo"
    shutil.copytree(
        ROOT,
        repo,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "tests", "map"),
    )
    return repo


def ledger_counts(repo: Path) -> dict[str, int]:
    """Count ledger records (base + shards) before the workers run.

    The tests used to hardcode absolute counts, which made them fail every time
    a session added material. They also counted only the frozen base file, which
    stopped matching the validators and the viewer once a session began writing
    to its own shard. Both are fixed by taking a union baseline before the
    workers start.
    """
    counts: dict[str, int] = {}
    for collection in ("fragments", "questions", "relations", "sessions"):
        files = [repo / "state" / f"{collection}.jsonl"]
        files.extend(sorted((repo / "state" / f"{collection}.d").glob("*.jsonl")))
        counts[collection] = sum(
            len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])
            for path in files
            if path.is_file()
        )
    return counts


def run_tool(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=repo, capture_output=True, text=True, timeout=120
    )


class ParallelSessionTests(unittest.TestCase):
    def test_three_sessions_write_concurrently_and_all_tools_see_the_union(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            baseline = ledger_counts(repo)
            processes = [
                subprocess.Popen(
                    [sys.executable, "-c", WORKER, str(slot)],
                    cwd=repo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for slot in (1, 2, 3)
            ]
            outputs = [process.communicate(timeout=120) for process in processes]
            for process, (stdout, stderr) in zip(processes, outputs):
                self.assertEqual(process.returncode, 0, stderr)
            written = [json.loads(stdout) for stdout, _stderr in outputs]
            fragment_ids = [entry["fragment"] for entry in written]
            self.assertEqual(len(set(fragment_ids)), 3)

            validation = run_tool(repo, "tools/validate_seed.py")
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
            for collection in ("fragments", "questions", "relations", "sessions"):
                self.assertIn(f"{collection}={baseline[collection] + 3}", validation.stdout)

            mapping = run_tool(repo, "tools/inspect_inquiry.py", "--write-map")
            self.assertEqual(mapping.returncode, 0, mapping.stdout + mapping.stderr)
            check = run_tool(repo, "tools/inspect_inquiry.py", "--check-map")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            reading_map = (repo / "READING_MAP.md").read_text(encoding="utf-8")
            for fragment_id in fragment_ids:
                self.assertIn(fragment_id, reading_map)

            payload = run_tool(
                repo,
                "-c",
                "import json,sys;sys.path.insert(0,'tools');"
                "from serve_viewer import read_archive_payload as p;"
                "d=p();print(json.dumps({k: len(v) for k, v in d.items()}))",
            )
            self.assertEqual(payload.returncode, 0, payload.stderr)
            counts = json.loads(payload.stdout)
            self.assertEqual(counts["fragments"], baseline["fragments"] + 3)
            self.assertEqual(counts["questions"], baseline["questions"] + 3)

    def test_sequential_ids_collide_and_the_validator_rejects_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = copy_repo(Path(tmp))
            fragments = repo / "state" / "fragments.jsonl"
            record = {
                "fragment_id": "FRAG-013",
                "created_at": "2026-10-21",
                "language": "ja",
                "form": "fragment",
                "title": "collision",
                "text": "body",
                "narrator_mode": "other",
                "question_ids": ["Q-001"],
                "motif_ids": ["MOTIF-002"],
                "material_ids": [],
                "status": "draft",
            }
            line = json.dumps(record, ensure_ascii=False) + "\n"
            with open(fragments, "a", encoding="utf-8") as handle:
                handle.write(line)
                handle.write(line)
                handle.flush()

            validation = run_tool(repo, "tools/validate_seed.py")
            self.assertEqual(validation.returncode, 1)
            self.assertIn("duplicate fragment_id FRAG-013", validation.stdout)


if __name__ == "__main__":
    unittest.main()
