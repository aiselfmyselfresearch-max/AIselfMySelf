import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import whether_gate


class WhetherGateTests(unittest.TestCase):
    def test_editorial_decision_id_is_loaded_and_in_denominator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "state"
            state.mkdir()
            rows = {
                "read_log": [{"read_id": "READ-1", "session_id": "SESSION-1", "reading": "declined"}],
                "editorial_decisions": [{"decision_id": "ED-1", "session_id": "SESSION-1", "status": "corrected"}],
                "sessions": [{"session_id": "SESSION-1"}],
            }
            for name, records in rows.items():
                (state / f"{name}.jsonl").write_text(
                    "".join(json.dumps(row) + "\n" for row in records), encoding="utf-8"
                )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(whether_gate.run_audit(root=root), 0)
            self.assertIn("Total editorial_decisions rows: 1", output.getvalue())
            self.assertIn("Veto/action ratio: 1/2 = 50.00%", output.getvalue())

    def test_load_errors_are_not_silently_counted_as_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state").mkdir()
            (root / "state" / "editorial_decisions.jsonl").write_text(
                '{"wrong_id": "ED-1"}\n', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "Could not load editorial_decisions"):
                whether_gate._load_coll("editorial_decisions", "decision_id", root)


if __name__ == "__main__":
    unittest.main()
