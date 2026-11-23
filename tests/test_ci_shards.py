"""The CI test matrix must cover every test module exactly once.

The regression suite is split into five shards in ``.github/workflows/ci.yml`` so
the shards can run at the same time (measured 2026-11-23: 705 s serially before
the runtime work, 482 s after). A pattern that misses a module makes that module
invisible to CI -- a green run that tested less -- and a pattern that overlaps
another runs the same file twice for no extra evidence.

The shard list is read out of the workflow file itself, not copied here: a test
that hard-codes the list only pins the test. PyYAML is not a dependency of this
repository (CI installs nothing), so the patterns are read by a small scan for
the ``- "test_..."`` items under ``strategy.matrix.shard``.
"""
from __future__ import annotations

import fnmatch
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def shard_patterns() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    block = text.split("strategy:", 1)[1]
    matrix = block.split("matrix:", 1)[1]
    return re.findall(r'^\s+- "(test_[^"]+)"\s*$', matrix, re.M)


def test_modules() -> list[str]:
    return sorted(p.name for p in (ROOT / "tests").glob("test_*.py"))


class CiShardTests(unittest.TestCase):
    def test_the_workflow_declares_more_than_one_shard(self):
        patterns = shard_patterns()
        self.assertGreater(len(patterns), 1, f"no shard matrix found in {WORKFLOW}")

    def test_every_test_module_runs_in_exactly_one_shard(self):
        patterns = shard_patterns()
        owners: dict[str, list[str]] = {}
        for pattern in patterns:
            for name in test_modules():
                if fnmatch.fnmatch(name, pattern):
                    owners.setdefault(name, []).append(pattern)
        missing = [name for name in test_modules() if name not in owners]
        doubled = {name: pats for name, pats in owners.items() if len(pats) > 1}
        self.assertEqual(missing, [], "modules no shard runs:")
        self.assertEqual(doubled, {}, "modules more than one shard runs:")

    def test_shards_run_the_suite_rather_than_a_named_module(self):
        """Each shard uses ``discover -p``, so a new module is picked up by name."""
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover -s tests -t . -p", text)

    def test_the_suite_no_longer_runs_verbosely(self):
        """1,125 lines of "ok" is not read; tracebacks print either way."""
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("discover -s tests -v", text)


if __name__ == "__main__":
    unittest.main()
