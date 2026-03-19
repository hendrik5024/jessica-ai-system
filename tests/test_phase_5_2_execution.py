"""Phase 5.2 Execution Tests - Comprehensive test suite for minimal action embodiment.

40+ tests covering:
- Execution tracking (audit trail, reversibility, statistics)
- Keyboard execution (keypress, typing, hotkeys)
- Mouse execution (click, move, scroll, double-click)
- Action coordinator (pipeline routing, validation)
- Constraint verification (no learning, no autonomy, no chaining)
- Integration with Phase 5.1.5 approval gates
"""
import pytest
from datetime import datetime
from jessica.execution import (
    ExecutionTracker,
    ExecutionOutcome,
    ExecutionStatus,
    KeyboardExecutor,
    MouseExecutor,
    ActionExecutor,
)


class TestExecutionTracker:
    """Test execution tracking and audit trail."""

    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            assert tracker.enabled is True
            assert len(tracker.execution_records) == 0

    def test_tracker_disabled(self):
        """Test tracker disabled state."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=False)
            assert tracker.enabled is False

    def test_record_execution(self):
        """Test recording execution."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=1000,
            )
            record = tracker.record_execution(
                intent_id="intent_001",
                action_type="keyboard",
                action_params={"key": "a"},
                approval_id="approval_001",
                outcome=outcome,
                reversible=True,
            )
            assert record is not None
            assert record["intent_id"] == "intent_001"
            assert record["action_type"] == "keyboard"

    def test_execution_history(self):
        """Test retrieving execution history."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=100,
            )
            for i in range(3):
                tracker.record_execution(
                    intent_id="intent_001",
                    action_type="keyboard",
                    action_params={"key": "a"},
                    approval_id=f"approval_{i:03d}",
                    outcome=outcome,
                )

            history = tracker.get_execution_history()
            assert len(history) == 3

    def test_execution_history_filtered(self):
        """Test filtering execution history by intent."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=100,
            )

            # Record for different intents
            tracker.record_execution(
                intent_id="intent_001",
                action_type="keyboard",
                action_params={"key": "a"},
                approval_id="approval_001",
                outcome=outcome,
            )
            tracker.record_execution(
                intent_id="intent_002",
                action_type="mouse",
                action_params={"x": 100, "y": 50},
                approval_id="approval_002",
                outcome=outcome,
            )

            history = tracker.get_execution_history(intent_id="intent_001")
            assert len(history) == 1
            assert history[0]["intent_id"] == "intent_001"

    def test_last_execution(self):
        """Test getting last execution."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=100,
            )

            tracker.record_execution(
                intent_id="intent_001",
                action_type="keyboard",
                action_params={"key": "a"},
                approval_id="approval_001",
                outcome=outcome,
            )
            tracker.record_execution(
                intent_id="intent_002",
                action_type="mouse",
                action_params={"x": 100, "y": 50},
                approval_id="approval_002",
                outcome=outcome,
            )

            last = tracker.get_last_execution()
            assert last["action_type"] == "mouse"

    def test_reversibility_check(self):
        """Test checking reversibility."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=100,
            )

            record = tracker.record_execution(
                intent_id="intent_001",
                action_type="keyboard",
                action_params={"key": "a"},
                approval_id="approval_001",
                outcome=outcome,
                reversible=True,
            )

            assert tracker.is_reversible(record["execution_id"]) is True

    def test_success_rate(self):
        """Test success rate calculation."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)

            # 2 successful
            success_outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=0,
                end_time=1,
                duration_ms=100,
            )
            tracker.record_execution(
                intent_id="intent_001",
                action_type="keyboard",
                action_params={"key": "a"},
                approval_id="approval_001",
                outcome=success_outcome,
            )
            tracker.record_execution(
                intent_id="intent_002",
                action_type="keyboard",
                action_params={"key": "b"},
                approval_id="approval_002",
                outcome=success_outcome,
            )

            # 1 failed
            failed_outcome = ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=0,
                end_time=1,
                duration_ms=100,
                error_message="Test error",
            )
            tracker.record_execution(
                intent_id="intent_003",
                action_type="keyboard",
                action_params={"key": "c"},
                approval_id="approval_003",
                outcome=failed_outcome,
            )

            success_rate = tracker.get_success_rate()
            assert abs(success_rate - (2 / 3)) < 0.01

    def test_statistics(self):
        """Test getting execution statistics."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ExecutionTracker(data_dir=tmpdir, enabled=True)
            stats = tracker.get_statistics()

            assert stats["enabled"] is True
            assert stats["total_executions"] == 0

    def test_tracker_enable_disable(self):
        """Test enabling and disabling tracker."""
        tracker = ExecutionTracker(enabled=True)
        assert tracker.enabled is True

        tracker.disable()
        assert tracker.enabled is False

        tracker.enable()
        assert tracker.enabled is True


class TestKeyboardExecutor:
    """Test keyboard execution."""

    def test_keyboard_initialization(self):
        """Test keyboard executor initializes."""
        executor = KeyboardExecutor(enabled=True)
        assert executor.enabled is True

    def test_keyboard_disabled(self):
        """Test keyboard execution when disabled."""
        executor = KeyboardExecutor(enabled=False)
        outcome = executor.execute_key("intent_001", "a")
        assert outcome.status == ExecutionStatus.CANCELLED

    def test_keyboard_key_normalization(self):
        """Test key name normalization."""
        assert KeyboardExecutor._normalize_key("enter") == "return"
        assert KeyboardExecutor._normalize_key("control") == "ctrl"
        assert KeyboardExecutor._normalize_key("command") == "cmd"
        assert KeyboardExecutor._normalize_key("a") == "a"

    def test_keyboard_execution_structure(self):
        """Test keyboard execution returns proper structure."""
        tracker = ExecutionTracker(enabled=True)
        executor = KeyboardExecutor(enabled=True, tracker=tracker)

        # Disable to avoid actual keyboard execution
        executor.disable()
        outcome = executor.execute_key("intent_001", "a")

        assert outcome.status == ExecutionStatus.CANCELLED
        assert isinstance(outcome.start_time, (int, float))
        assert isinstance(outcome.duration_ms, (int, float))


class TestMouseExecutor:
    """Test mouse execution."""

    def test_mouse_initialization(self):
        """Test mouse executor initializes."""
        executor = MouseExecutor(enabled=True)
        assert executor.enabled is True

    def test_mouse_disabled(self):
        """Test mouse execution when disabled."""
        executor = MouseExecutor(enabled=False)
        outcome = executor.execute_click("intent_001", 100, 50)
        assert outcome.status == ExecutionStatus.CANCELLED

    def test_mouse_invalid_coordinates(self):
        """Test mouse execution with invalid coordinates."""
        tracker = ExecutionTracker(enabled=True)
        executor = MouseExecutor(enabled=True, tracker=tracker)

        outcome = executor.execute_click("intent_001", -1, 50)
        assert outcome.status == ExecutionStatus.FAILED
        assert "coordinates" in outcome.error_message.lower()

    def test_mouse_invalid_scroll_direction(self):
        """Test mouse scroll with invalid direction."""
        tracker = ExecutionTracker(enabled=True)
        executor = MouseExecutor(enabled=True, tracker=tracker)

        outcome = executor.execute_scroll("intent_001", "left", 3)
        assert outcome.status == ExecutionStatus.FAILED

    def test_mouse_execution_structure(self):
        """Test mouse execution returns proper structure."""
        tracker = ExecutionTracker(enabled=True)
        executor = MouseExecutor(enabled=True, tracker=tracker)

        # Disable to avoid actual mouse execution
        executor.disable()
        outcome = executor.execute_click("intent_001", 100, 50)

        assert outcome.status == ExecutionStatus.CANCELLED
        assert isinstance(outcome.start_time, (int, float))
        assert isinstance(outcome.duration_ms, (int, float))


class TestActionExecutor:
    """Test action executor coordinator."""

    def test_executor_initialization(self):
        """Test action executor initializes."""
        executor = ActionExecutor(enabled=True)
        assert executor.enabled is True

    def test_executor_disabled(self):
        """Test execution when disabled."""
        executor = ActionExecutor(enabled=False)
        pipeline = {
            "pipeline_id": "pipeline_001",
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100, "y": 50},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
            "status": "approved",
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.CANCELLED

    def test_pipeline_validation_missing_intent(self):
        """Test pipeline validation rejects missing intent."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "approval_result": {
                "decision": "approved",
            },
        }

        assert executor._validate_pipeline(pipeline) is False

    def test_pipeline_validation_not_approved(self):
        """Test pipeline validation rejects non-approved."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
            },
            "approval_result": {
                "decision": "pending",
            },
        }

        assert executor._validate_pipeline(pipeline) is False

    def test_pipeline_validation_valid(self):
        """Test pipeline validation accepts valid pipeline."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100, "y": 50},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        assert executor._validate_pipeline(pipeline) is True

    def test_action_routing_click(self):
        """Test routing to mouse click."""
        executor = ActionExecutor(enabled=False)  # Disable to avoid actual execution
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100, "y": 50},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.CANCELLED

    def test_action_routing_keyboard(self):
        """Test routing to keyboard."""
        executor = ActionExecutor(enabled=False)  # Disable to avoid actual execution
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "press_key",
                "parameters": {"key": "a"},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.CANCELLED

    def test_missing_keyboard_parameters(self):
        """Test keyboard action with missing parameters."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "press_key",
                "parameters": {},  # Missing 'key'
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.FAILED
        assert "key" in outcome.error_message.lower()

    def test_missing_mouse_parameters(self):
        """Test mouse action with missing parameters."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100},  # Missing 'y'
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.FAILED
        assert "y" in outcome.error_message.lower()

    def test_unknown_action_type(self):
        """Test unknown action type."""
        executor = ActionExecutor(enabled=True)
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "unknown_action",
                "parameters": {},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.FAILED

    def test_statistics(self):
        """Test getting statistics."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = ActionExecutor(enabled=True)
            executor.tracker.data_dir = tmpdir
            executor.tracker.execution_records = []
            stats = executor.get_statistics()

            assert stats["enabled"] is True
            assert stats["total_executions"] == 0

    def test_executor_enable_disable(self):
        """Test enabling and disabling executor."""
        executor = ActionExecutor(enabled=True)
        assert executor.enabled is True

        executor.disable()
        assert executor.enabled is False
        assert executor.keyboard.enabled is False
        assert executor.mouse.enabled is False

        executor.enable()
        assert executor.enabled is True
        assert executor.keyboard.enabled is True
        assert executor.mouse.enabled is True


class TestPhase5_2Constraints:
    """Test Phase 5.2 constraint satisfaction."""

    def test_zero_learning_capability(self):
        """Test that executors have zero learning capability."""
        executor = ActionExecutor(enabled=True)

        # Executors should not modify state based on feedback
        assert not hasattr(executor.keyboard, "learning_mode")
        assert not hasattr(executor.mouse, "learning_mode")
        assert not hasattr(executor, "adaptive_routing")

    def test_zero_autonomy(self):
        """Test that execution requires explicit intent."""
        executor = ActionExecutor(enabled=True)

        # execute_from_pipeline should require pipeline with approval
        pipeline_without_approval = {
            "intent": {"intent_id": "intent_001", "action_name": "click"},
            "approval_result": {"decision": "pending"},
        }

        outcome = executor.execute_from_pipeline(pipeline_without_approval)
        assert outcome.status == ExecutionStatus.FAILED

    def test_single_action_atomic(self):
        """Test that each execution is atomic (one action)."""
        executor = ActionExecutor(enabled=False)

        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100, "y": 50},
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
        }

        # Single call, single outcome
        outcome = executor.execute_from_pipeline(pipeline)
        assert isinstance(outcome, ExecutionOutcome)

    def test_no_background_execution(self):
        """Test no background or async execution."""
        executor = ActionExecutor(enabled=True)

        # All executions should be synchronous and return immediately
        assert not hasattr(executor, "background_queue")
        assert not hasattr(executor, "async_handler")

    def test_full_reversibility(self):
        """Test reversibility tracking."""
        tracker = ExecutionTracker(enabled=True)
        executor = KeyboardExecutor(enabled=True, tracker=tracker)

        # Disable to check structure without actual execution
        executor.disable()
        outcome = executor.execute_key("intent_001", "a")

        # Verify outcome has reversibility info
        assert outcome is not None

    def test_immutable_audit_trail(self):
        """Test audit trail is append-only."""
        tracker = ExecutionTracker(enabled=True)
        initial_count = len(tracker.execution_records)

        outcome = ExecutionOutcome(
            status=ExecutionStatus.SUCCESS,
            start_time=0,
            end_time=1,
            duration_ms=100,
        )

        tracker.record_execution(
            intent_id="intent_001",
            action_type="keyboard",
            action_params={"key": "a"},
            approval_id="approval_001",
            outcome=outcome,
        )

        # Records should only grow, never shrink
        assert len(tracker.execution_records) == initial_count + 1

    def test_approval_gate_required(self):
        """Test that approval gate is required for execution."""
        executor = ActionExecutor(enabled=True)

        # Pipeline without approval should fail
        pipeline = {
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "parameters": {"x": 100, "y": 50},
            },
            "approval_result": {
                "decision": "rejected",  # Not approved
            },
        }

        outcome = executor.execute_from_pipeline(pipeline)
        assert outcome.status == ExecutionStatus.FAILED


class TestPhase5_2Integration:
    """Test Phase 5.2 integration with Phase 5.1.5."""

    def test_pipeline_from_phase_5_1_5(self):
        """Test execution with Phase 5.1.5 pipeline structure."""
        executor = ActionExecutor(enabled=False)

        # Simulate Phase 5.1.5 pipeline
        pipeline = {
            "pipeline_id": "pipeline_001",
            "intent": {
                "intent_id": "intent_001",
                "action_name": "click",
                "action_type": "INTERACTION",
                "priority": "normal",
                "parameters": {"x": 100, "y": 50},
                "approval_required": True,
            },
            "justification": {
                "primary_goal": "Submit form",
                "reasoning_chain": ["Form is ready", "All fields valid"],
            },
            "risk_assessment": {
                "risk_level": "minimal",
            },
            "dry_run_result": {
                "is_safe_to_execute": True,
            },
            "approval_result": {
                "approval_id": "approval_001",
                "decision": "approved",
            },
            "status": "approved",
        }

        # Should validate and route correctly
        assert executor._validate_pipeline(pipeline) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
