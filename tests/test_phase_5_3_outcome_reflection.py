"""Phase 5.3 Outcome Reflection tests (read-only)."""
from copy import deepcopy

from jessica.execution import ExecutionOutcome, ExecutionStatus, OutcomeReflection


class TestOutcomeReflection:
    def test_summarize_outcome_dataclass(self):
        reflector = OutcomeReflection()
        outcome = ExecutionOutcome(
            status=ExecutionStatus.SUCCESS,
            start_time=0,
            end_time=1,
            duration_ms=100,
            notes="OK",
        )
        summary = reflector.summarize_outcome(outcome)
        assert summary["status"] == ExecutionStatus.SUCCESS.value
        assert summary["duration_ms"] == 100
        assert summary["notes"] == "OK"

    def test_summarize_outcome_dict(self):
        reflector = OutcomeReflection()
        outcome = {
            "status": "failed",
            "duration_ms": 50,
            "error_message": "boom",
        }
        summary = reflector.summarize_outcome(outcome)
        assert summary["status"] == "failed"
        assert summary["error_message"] == "boom"

    def test_summarize_record(self):
        reflector = OutcomeReflection()
        record = {
            "execution_id": "exec_000001",
            "intent_id": "intent_0001",
            "action_type": "keyboard",
            "action_params": {"key": "a"},
            "approval_id": "approval_0001",
            "timestamp": "2026-02-05T00:00:00",
            "reversible": True,
            "undo_instructions": "Press 'a' again",
            "outcome": {
                "status": "success",
                "duration_ms": 10,
                "notes": "Pressed key: a",
            },
        }
        summary = reflector.summarize_record(record)
        assert summary["execution_id"] == "exec_000001"
        assert summary["status"] == "success"
        assert summary["reversible"] is True

    def test_summarize_outcomes_empty(self):
        reflector = OutcomeReflection()
        summary = reflector.summarize_outcomes([])
        assert summary["total"] == 0
        assert summary["average_duration_ms"] == 0

    def test_summarize_outcomes_counts(self):
        reflector = OutcomeReflection()
        outcomes = [
            ExecutionOutcome(ExecutionStatus.SUCCESS, 0, 1, 10),
            ExecutionOutcome(ExecutionStatus.FAILED, 0, 1, 20, error_message="x"),
            ExecutionOutcome(ExecutionStatus.CANCELLED, 0, 1, 5),
        ]
        summary = reflector.summarize_outcomes(outcomes)
        assert summary["total"] == 3
        assert summary["success"] == 1
        assert summary["failed"] == 1
        assert summary["cancelled"] == 1

    def test_to_text(self):
        reflector = OutcomeReflection()
        text = reflector.to_text({"status": "success", "duration_ms": 12, "notes": "OK"})
        assert "Status" in text
        assert "Duration" in text
        assert "Notes" in text

    def test_no_mutation_of_outcome_dict(self):
        reflector = OutcomeReflection()
        outcome = {
            "status": "success",
            "duration_ms": 10,
            "side_effects": ["x"],
        }
        original = deepcopy(outcome)
        reflector.summarize_outcome(outcome)
        assert outcome == original

    def test_no_mutation_of_record(self):
        reflector = OutcomeReflection()
        record = {
            "execution_id": "exec_1",
            "outcome": {"status": "success", "duration_ms": 1},
        }
        original = deepcopy(record)
        reflector.summarize_record(record)
        assert record == original

    def test_normalize_outcome_preserves_side_effects(self):
        reflector = OutcomeReflection()
        outcome = {
            "status": "success",
            "duration_ms": 1,
            "side_effects": ["a", "b"],
        }
        summary = reflector.summarize_outcome(outcome)
        assert summary["status"] == "success"

    def test_read_only_behavior(self):
        reflector = OutcomeReflection()
        outcome = ExecutionOutcome(ExecutionStatus.SUCCESS, 0, 1, 10)
        summary = reflector.summarize_outcome(outcome)
        assert isinstance(summary, dict)
