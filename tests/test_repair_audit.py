import unittest
from pathlib import Path

from tools.repair_audit import chains, keyword_hits, level_of, repro


def record(**kwargs):
    base = {
        "errata_id": "ERR-900",
        "verdict": "contradicted",
        "status": "open",
        "claim": "",
        "note": "",
        "check": {},
        "fragment_id": "FRAG-001",
    }
    base.update(kwargs)
    return base


class RepairAuditTests(unittest.TestCase):
    def test_levels_split_prose_instrument_and_errata(self):
        self.assertEqual(level_of(record(fragment_id="FRAG-001")), "本文")
        self.assertEqual(level_of(record(fragment_id=None, subject_id="MAT-TRC-001", subject_type="material")), "計器・痕跡")
        self.assertEqual(level_of(record(fragment_id=None, subject_id="ERR-012", subject_type="other")), "訂正録")
        self.assertEqual(level_of(record(fragment_id=None)), "特定なし")

    def test_chain_depth_and_terminal_status(self):
        records = [
            record(errata_id="ERR-001", status="annotated"),
            record(errata_id="ERR-002", subject_id="ERR-001", status="open"),
            record(errata_id="ERR-003", subject_id="ERR-002", status="annotated"),
        ]
        data = chains(records)
        self.assertEqual(data["edges"], 2)
        self.assertEqual(data["depth_max"], 2)
        self.assertEqual(data["open_terminals"], 0)
        deepest = [row for row in data["detail"] if row["from"] == "ERR-001"][0]
        self.assertEqual(deepest["path"], ["ERR-001", "ERR-002", "ERR-003"])

    def test_open_terminal_is_reported(self):
        records = [
            record(errata_id="ERR-001", status="annotated"),
            record(errata_id="ERR-002", subject_id="ERR-001", status="open"),
        ]
        data = chains(records)
        self.assertEqual(data["open_terminals"], 1)

    def test_keyword_hits_are_literal(self):
        self.assertEqual(keyword_hits("書き換えない", ("書き換え",)), ["書き換え"])
        self.assertEqual(keyword_hits("宛先の欄がない", ("宛先", "謝罪")), ["宛先"])
        self.assertEqual(keyword_hits("", ("宛先",)), [])

    def test_reproducibility_needs_an_object_range(self):
        self.assertFalse(repro(record(check={"kind": "manual"}))["has_range"])
        self.assertTrue(repro(record(check={"kind": "tail_question_count", "params": {"from": 1, "to": 17}}))["has_range"])
        self.assertTrue(repro(record(check={"kind": "pronoun_absence", "params": {"as_of_fragments": 22}}))["has_range"])

    def test_ledger_io_union_sees_shards_and_exclude(self):
        import ledger_io

        root = Path(__file__).resolve().parents[1]
        errors: list[str] = []
        union = ledger_io.load_jsonl_union(root / "state" / "fragments.jsonl", "fragment_id", errors, root=root)
        self.assertEqual(errors, [])
        self.assertGreater(len(union), 43)
        excluded = ledger_io.load_jsonl_union(
            root / "state" / "fragments.jsonl", "fragment_id", [], root=root, exclude="5c7e2a9b4d10"
        )
        self.assertGreater(len(union), len(excluded))


if __name__ == "__main__":
    unittest.main()
