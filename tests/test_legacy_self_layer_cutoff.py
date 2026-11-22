"""Frozen pre-rule provenance must survive the wall clock catching up."""
import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_seed import check_session_self_layer


class LegacySelfLayerCutoffTest(unittest.TestCase):
    def test_frozen_legacy_id_is_still_legacy(self):
        errors = []
        counts = check_session_self_layer(
            {"SESSION-20261122-11b1d3": {}}, errors,
            today=datetime.date(2026, 11, 22),
        )
        self.assertEqual(errors, [])
        self.assertEqual(counts, (0, 1, 0, 1))

    def test_new_id_still_requires_both_hooks(self):
        errors = []
        check_session_self_layer(
            {"SESSION-20261122-abcdef": {}}, errors,
            today=datetime.date(2026, 11, 22),
        )
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("session_type" in e for e in errors))
        self.assertTrue(any("self_layer_checks" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
