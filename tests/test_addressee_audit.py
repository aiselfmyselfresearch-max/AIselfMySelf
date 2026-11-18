"""The addressee audit measures cross-question mass without moving any weight.

The live-ledger numbers change with every session, so these tests use a
three-hypothesis fixture: one hypothesis registered to Q-001 and Q-002, one to
Q-001 only, one to Q-002 only, with one evaluation each.  The point is the
mechanism, not the archive's current value: an evaluation addressed to Q-001
must stop paying Q-002 under the ``question_scoped`` basis, and the present
basis must keep doing exactly what ``compute_belief_state`` does today.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import belief_state


def _hypothesis(hid, question_ids):
    return {
        "hypothesis_id": hid,
        "session_id": "SESSION-FIXTURE",
        "created_at": "2026-11-18",
        "question_ids": list(question_ids),
        "title": f"fixture {hid}",
        "proposition": "fixture proposition",
        "scope_conditions": ["fixture scope"],
        "exclusion_clause": "fixture exclusion",
        "lineage_op": "root",
        "parent_hypothesis_ids": [],
        "status": "active",
        "register": "judgment",
        "supporting_material_ids": [],
        "source_note_ids": [],
    }


def _evaluation(eid, target, session_id="SESSION-FIXTURE"):
    return {
        "evaluation_id": eid,
        "session_id": session_id,
        "created_at": "2026-11-18",
        "target_hypothesis_id": target,
        "verdict": "supports",
        "evidence_type": "cross_session_audit",
        "summary": "fixture evaluation summary long enough to pass any reader",
        "compared_against_hypothesis_ids": [],
    }


def _fixture():
    hypotheses = {
        h["hypothesis_id"]: h
        for h in (
            _hypothesis("HYP-FIXTURE-A", ["Q-001", "Q-002"]),
            _hypothesis("HYP-FIXTURE-B", ["Q-001"]),
            _hypothesis("HYP-FIXTURE-C", ["Q-002"]),
        )
    }
    evaluations = {
        e["evaluation_id"]: e
        for e in (
            _evaluation("EVL-FIXTURE-1", "HYP-FIXTURE-A"),
            _evaluation("EVL-FIXTURE-2", "HYP-FIXTURE-B"),
            _evaluation("EVL-FIXTURE-3", "HYP-FIXTURE-C", "SESSION-FIXTURE-B"),
        )
    }
    sessions = {
        "SESSION-FIXTURE": {
            "session_id": "SESSION-FIXTURE",
            "offered_target_question_id": "Q-001",
            "question_ids": ["Q-001"],
        },
        "SESSION-FIXTURE-B": {
            "session_id": "SESSION-FIXTURE-B",
            "offered_target_question_id": "Q-002",
            "question_ids": ["Q-002"],
        },
    }
    return {
        "questions": {},
        "materials": {},
        "fragments": {},
        "sessions": sessions,
        "notes": {},
        "hypotheses": hypotheses,
        "evaluations": evaluations,
        "errata": {},
    }


class AddresseeAuditTests(unittest.TestCase):
    def test_receipt_rule_wins_over_target_question(self):
        data = _fixture()
        qid, rule = belief_state.evaluation_addressee(
            data["evaluations"]["EVL-FIXTURE-1"],
            data["sessions"],
            data["hypotheses"],
        )
        self.assertEqual((qid, rule), ("Q-001", "receipt"))

    def test_single_question_target_is_the_fallback(self):
        data = _fixture()
        # No session row: the target's own single question is the only address.
        qid, rule = belief_state.evaluation_addressee(
            data["evaluations"]["EVL-FIXTURE-3"],
            {},
            data["hypotheses"],
        )
        self.assertEqual((qid, rule), ("Q-002", "target_question"))

    def test_multi_question_target_and_no_receipt_is_unaddressed(self):
        data = _fixture()
        session = {
            "SESSION-FIXTURE": {
                "session_id": "SESSION-FIXTURE",
                "question_ids": ["Q-001", "Q-002", "Q-003"],
            }
        }
        qid, rule = belief_state.evaluation_addressee(
            data["evaluations"]["EVL-FIXTURE-1"],
            session,
            data["hypotheses"],
        )
        self.assertEqual((qid, rule), (None, "none"))

    def test_present_basis_is_unchanged_and_scoped_basis_separates(self):
        data = _fixture()
        audit = belief_state.addressee_audit(data, question_ids=("Q-001", "Q-002"))
        state = belief_state.compute_belief_state(data=data)
        for qid in ("Q-001", "Q-002"):
            present = {row["hypothesis_id"]: row["posterior"] for row in audit["present"]["top"][qid]}
            live = {
                h["hypothesis_id"]: h["posterior"]
                for h in state["questions"][qid]["hypotheses"]
            }
            self.assertEqual(present, live, qid)
        # Present arithmetic pays the same shared hypothesis in both questions.
        self.assertGreater(audit["present"]["overlap"]["Q-001|Q-002"], 0.49)
        # Scoping the evaluation to the question it was addressed to lowers it.
        self.assertLess(
            audit["question_scoped"]["overlap"]["Q-001|Q-002"],
            audit["present"]["overlap"]["Q-001|Q-002"],
        )
        self.assertEqual(audit["hypotheses"]["multi_question_ids"], ["HYP-FIXTURE-A"])
        self.assertFalse(audit["writes"])

    def test_audit_writes_nothing(self):
        audit = belief_state.addressee_audit(_fixture(), question_ids=("Q-001", "Q-002"))
        self.assertEqual(audit["question_scoped"]["evaluations_used"]["Q-002"], 1)
        self.assertIn("writes", audit)


if __name__ == "__main__":
    unittest.main()
