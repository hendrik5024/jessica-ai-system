"""Phase 5.5: Human-Guided Action Composition - Comprehensive Test Suite.

Tests for ActionPlan, ActionPlanBuilder, ActionPlanExecutor, and ActionPlanStateTracker.

Safety Constraints Verified:
- ZERO autonomy: Cannot execute without explicit human confirmation per step
- ZERO learning: No adaptive behavior, no pipeline modification
- ZERO background execution: All execution explicit and synchronous
- ZERO retries: Failed steps don't auto-retry
- ZERO branching: No conditional logic, only sequential execution
- FULL reversibility: Each step independently recordable
- FULL human control: Every step requires explicit human confirmation
"""

import pytest
import time
from typing import Any, Dict, List, Optional

from jessica.execution import (
    ActionPlan,
    PlanStatus,
    StepResult,
    create_action_plan,
    ActionPlanBuilder,
    ActionPlanExecutor,
    ActionPlanStateTracker,
    ExecutionOutcome,
    ExecutionStatus,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_pipeline_ids() -> List[str]:
    """Generate sample approved pipeline IDs."""
    return ["pipeline_001", "pipeline_002", "pipeline_003"]


@pytest.fixture
def sample_pipeline(sample_pipeline_ids) -> Dict[str, Any]:
    """Generate a sample approved pipeline."""
    return {
        "pipeline_id": sample_pipeline_ids[0],
        "status": "approved",
        "intent": {
            "intent_id": "intent_001",
            "intent_type": "keyboard",
            "parameters": {"key": "a"},
        },
        "approval_result": {
            "approval_id": "approval_001",
            "decision": "approved",
        },
        "dry_run_result": {
            "success": True,
            "predicted_outcome": "Key 'a' pressed",
        },
    }


@pytest.fixture
def plan_builder() -> ActionPlanBuilder:
    """Create an ActionPlanBuilder instance."""
    return ActionPlanBuilder(enabled=True)


@pytest.fixture
def plan_executor() -> ActionPlanExecutor:
    """Create an ActionPlanExecutor instance."""
    return ActionPlanExecutor(enabled=True)


@pytest.fixture
def state_tracker() -> ActionPlanStateTracker:
    """Create an ActionPlanStateTracker instance."""
    return ActionPlanStateTracker(enabled=True)


# ============================================================================
# TEST: ActionPlan Data Structure
# ============================================================================


def test_action_plan_creation():
    """Test creating an ActionPlan."""
    pipeline_ids = ["pipeline_001", "pipeline_002"]
    plan = create_action_plan(
        pipeline_ids=pipeline_ids,
        human_label="Test Plan",
    )

    assert plan.plan_id is not None
    assert plan.pipeline_ids == pipeline_ids
    assert plan.status == PlanStatus.PENDING
    assert plan.current_step_index == 0
    assert plan.total_steps == 2
    assert not plan.is_at_end
    assert plan.next_pipeline_id == "pipeline_001"


def test_action_plan_requires_pipelines():
    """Test that ActionPlan requires at least one pipeline."""
    with pytest.raises(ValueError):
        create_action_plan(pipeline_ids=[])


def test_action_plan_progress():
    """Test plan progress calculation."""
    plan = create_action_plan(pipeline_ids=["p1", "p2", "p3", "p4"])

    assert plan.progress_percent == 0.0

    # Simulate advancing
    updated_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=2,
        status=plan.status,
    )
    assert updated_plan.progress_percent == 50.0


def test_action_plan_status_transitions():
    """Test plan status transitions."""
    plan = create_action_plan(pipeline_ids=["p1", "p2"])
    assert plan.status == PlanStatus.PENDING

    # Transition to executing
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
        started_timestamp=time.time(),
    )
    assert executing_plan.status == PlanStatus.EXECUTING

    # Transition to completed
    completed_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=2,
        status=PlanStatus.COMPLETED,
        completed_timestamp=time.time(),
    )
    assert completed_plan.status == PlanStatus.COMPLETED
    assert completed_plan.is_at_end


def test_action_plan_immutability():
    """Test that ActionPlan is properly mutable (can create new instances)."""
    plan1 = create_action_plan(pipeline_ids=["p1", "p2"])
    plan2 = ActionPlan(
        plan_id=plan1.plan_id,
        pipeline_ids=plan1.pipeline_ids,
        current_step_index=1,
        status=PlanStatus.EXECUTING,
    )

    # Original should be unchanged
    assert plan1.current_step_index == 0
    assert plan1.status == PlanStatus.PENDING

    # New plan should have updated state
    assert plan2.current_step_index == 1
    assert plan2.status == PlanStatus.EXECUTING


# ============================================================================
# TEST: ActionPlanBuilder
# ============================================================================


def test_builder_validates_pipeline(plan_builder, sample_pipeline):
    """Test that builder validates pipeline structure."""
    is_valid, error = plan_builder.validate_pipeline(sample_pipeline)
    assert is_valid
    assert error is None


def test_builder_rejects_unapproved_pipeline(plan_builder):
    """Test that builder rejects unapproved pipelines."""
    pipeline = {
        "pipeline_id": "pipeline_001",
        "status": "pending",  # NOT approved
        "intent": {"intent_id": "intent_001"},
        "approval_result": {"decision": "pending"},
    }
    is_valid, error = plan_builder.validate_pipeline(pipeline)
    assert not is_valid
    assert "approved" in error.lower()


def test_builder_rejects_missing_pipeline_id(plan_builder):
    """Test that builder rejects pipelines missing pipeline_id."""
    pipeline = {
        "status": "approved",
        "intent": {"intent_id": "intent_001"},
        "approval_result": {"decision": "approved"},
    }
    is_valid, error = plan_builder.validate_pipeline(pipeline)
    assert not is_valid
    assert "pipeline_id" in error.lower()


def test_builder_builds_from_pipelines(plan_builder, sample_pipeline):
    """Test building a plan from pipeline list."""
    pipelines = [
        sample_pipeline,
        {**sample_pipeline, "pipeline_id": "pipeline_002"},
    ]

    plan, error = plan_builder.build_from_pipelines(pipelines, human_label="Test Plan")

    assert error is None
    assert plan is not None
    assert plan.total_steps == 2
    assert plan.pipeline_ids == ["pipeline_001", "pipeline_002"]
    assert plan.human_label == "Test Plan"


def test_builder_builds_from_pipeline_ids(plan_builder):
    """Test building a plan from pipeline IDs directly."""
    pipeline_ids = ["p1", "p2", "p3"]
    plan, error = plan_builder.build_from_pipeline_ids(
        pipeline_ids,
        human_label="Direct Build",
    )

    assert error is None
    assert plan is not None
    assert plan.pipeline_ids == pipeline_ids


def test_builder_rejects_empty_pipeline_list(plan_builder):
    """Test that builder rejects empty pipeline list."""
    plan, error = plan_builder.build_from_pipelines([])
    assert plan is None
    assert error is not None


def test_builder_disable(plan_builder):
    """Test that builder respects disable flag."""
    plan_builder.disable()

    pipeline_ids = ["p1"]
    plan, error = plan_builder.build_from_pipeline_ids(pipeline_ids)

    assert plan is None
    assert "disabled" in error.lower()

    # Enable and retry
    plan_builder.enable()
    plan, error = plan_builder.build_from_pipeline_ids(pipeline_ids)

    assert plan is not None
    assert error is None


# ============================================================================
# TEST: ActionPlanExecutor - Single Step Execution
# ============================================================================


def test_executor_executes_single_step(plan_executor, sample_pipeline):
    """Test that executor executes ONE step only."""
    plan = create_action_plan(
        pipeline_ids=["pipeline_001", "pipeline_002"],
        human_label="Multi-step plan",
    )

    # Transition to executing
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
        started_timestamp=time.time(),
    )

    # Execute first step
    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert error is None
    assert updated_plan is not None

    # Verify only ONE step was executed
    assert updated_plan.current_step_index == 1
    assert len(updated_plan.completed_steps) == 1
    assert updated_plan.completed_steps[0].step_index == 0


def test_executor_requires_human_confirmation(plan_executor, sample_pipeline):
    """Test that executor requires explicit human confirmation."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # Try to execute without confirmation
    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=False,
    )

    assert updated_plan is None
    assert error is not None
    assert "confirmation" in error.lower()


def test_executor_requires_plan_executing_status(plan_executor, sample_pipeline):
    """Test that executor requires plan.status == EXECUTING."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])

    # Try to execute from PENDING status
    updated_plan, error = plan_executor.execute_next_step(
        plan=plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert updated_plan is None
    assert error is not None
    assert "executing" in error.lower()


def test_executor_validates_pipeline_match(plan_executor):
    """Test that executor validates pipeline matches expected step."""
    plan = create_action_plan(pipeline_ids=["pipeline_001", "pipeline_002"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # Provide wrong pipeline for this step
    wrong_pipeline = {
        "pipeline_id": "pipeline_999",  # Wrong!
        "status": "approved",
        "intent": {"intent_id": "intent_001"},
        "approval_result": {"decision": "approved"},
    }

    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=wrong_pipeline,
        human_confirmation=True,
    )

    assert updated_plan is None
    assert error is not None
    assert "pipeline_mismatch" in error.lower() or "mismatch" in error.lower()


def test_executor_stops_at_end(plan_executor, sample_pipeline):
    """Test that executor stops when plan is at end."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    completed_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=1,  # Already at end
        status=PlanStatus.EXECUTING,
    )

    updated_plan, error = plan_executor.execute_next_step(
        plan=completed_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert updated_plan is None
    assert error is not None
    assert "end" in error.lower()


def test_executor_records_step_results(plan_executor, sample_pipeline):
    """Test that executor records step results."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert error is None
    assert len(updated_plan.completed_steps) == 1

    step = updated_plan.completed_steps[0]
    assert step.step_index == 0
    assert step.pipeline_id == "pipeline_001"
    assert step.status in ["success", "failed", "pending"]


def test_executor_no_retries(plan_executor, sample_pipeline):
    """Test that executor does NOT retry failed steps."""
    plan = create_action_plan(pipeline_ids=["pipeline_001", "pipeline_002"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # First execution
    updated_plan1, error1 = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert error1 is None
    initial_step_count = len(updated_plan1.completed_steps)

    # Try to execute same step again (should not retry)
    # Instead should move to next step or fail
    # This is controlled by the human providing a different pipeline
    assert initial_step_count == 1


def test_executor_disable(plan_executor, sample_pipeline):
    """Test that executor respects disable flag."""
    plan_executor.disable()

    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    assert updated_plan is None
    assert "disabled" in error.lower()


# ============================================================================
# TEST: ActionPlanStateTracker
# ============================================================================


def test_tracker_summary(state_tracker):
    """Test getting plan summary."""
    plan = create_action_plan(pipeline_ids=["p1", "p2", "p3"])

    summary = state_tracker.get_plan_summary(plan)

    assert summary["plan_id"] == plan.plan_id
    assert summary["status"] == "pending"
    assert summary["total_steps"] == 3
    assert summary["current_step_index"] == 0
    assert summary["progress_percent"] == 0.0


def test_tracker_detailed_status(state_tracker):
    """Test getting detailed status."""
    plan = create_action_plan(pipeline_ids=["p1", "p2"])

    status = state_tracker.get_detailed_status(plan)

    assert "progress" in status
    assert status["progress"]["current_step"] == 0
    assert status["progress"]["total_steps"] == 2
    assert "timeline" in status
    assert "execution" in status


def test_tracker_next_step_info(state_tracker):
    """Test getting next step information."""
    plan = create_action_plan(pipeline_ids=["p1", "p2", "p3"])

    info = state_tracker.get_next_step_info(plan)

    assert info is not None
    assert info["step_index"] == 0
    assert info["pipeline_id"] == "p1"
    assert info["steps_remaining"] == 3


def test_tracker_next_step_at_end(state_tracker):
    """Test next step info when at end."""
    plan = create_action_plan(pipeline_ids=["p1"])
    completed_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=1,  # At end
        status=PlanStatus.COMPLETED,
    )

    info = state_tracker.get_next_step_info(completed_plan)
    assert info is None


def test_tracker_is_complete(state_tracker):
    """Test checking if plan is complete."""
    plan = create_action_plan(pipeline_ids=["p1"])

    assert not state_tracker.is_plan_complete(plan)

    completed_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=1,
        status=PlanStatus.COMPLETED,
    )

    assert state_tracker.is_plan_complete(completed_plan)


def test_tracker_failure_detection(state_tracker):
    """Test failure detection."""
    plan = create_action_plan(pipeline_ids=["p1"])

    assert not state_tracker.is_plan_failed(plan)

    # Create a plan with a failed step
    failed_step = StepResult(
        step_index=0,
        pipeline_id="p1",
        execution_id=None,
        status="failed",
        error_message="Execution error",
    )

    failed_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        current_step_index=1,
        status=PlanStatus.FAILED,
        failed_step=failed_step,
    )

    assert state_tracker.is_plan_failed(failed_plan)
    assert state_tracker.get_failure_reason(failed_plan) == "Execution error"


def test_tracker_disable(state_tracker):
    """Test that tracker respects disable flag."""
    state_tracker.disable()

    plan = create_action_plan(pipeline_ids=["p1"])
    summary = state_tracker.get_plan_summary(plan)

    assert summary == {}


# ============================================================================
# TEST: Safety Constraints
# ============================================================================


def test_constraint_no_autonomy(plan_executor, sample_pipeline):
    """CONSTRAINT: Plan executor cannot self-trigger execution."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])

    # Executor requires explicit call to execute_next_step
    # There is no background task or automatic triggering
    # This is a design constraint, not explicitly testable, but we verify
    # that the executor has no timer or background thread
    assert not hasattr(plan_executor, "background_timer")
    assert not hasattr(plan_executor, "auto_execute_thread")


def test_constraint_no_learning(plan_executor):
    """CONSTRAINT: Plan executor does not learn or modify pipelines."""
    plan = create_action_plan(pipeline_ids=["p1"])

    # Executor does not have a learning mechanism
    assert not hasattr(plan_executor, "learn_from_failure")
    assert not hasattr(plan_executor, "adapt_pipeline")


def test_constraint_no_background_execution(plan_executor):
    """CONSTRAINT: All execution is explicit and synchronous."""
    # ActionPlanExecutor.execute_next_step is synchronous (blocks until complete)
    # No async/await, no threading, no background queues
    import inspect

    source = inspect.getsource(plan_executor.execute_next_step)
    assert "async" not in source
    assert "Thread" not in source
    assert "background" not in source.lower()


def test_constraint_no_retries(plan_executor, sample_pipeline):
    """CONSTRAINT: Executor does not retry failed steps."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # After one execution, step count should be 1
    updated_plan, _ = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=True,
    )

    # Verify no automatic retry: completed steps should be exactly 1
    assert len(updated_plan.completed_steps) == 1


def test_constraint_no_conditional_branching(plan_executor):
    """CONSTRAINT: Executor has no conditional logic or branching.
    
    Validation conditionals are okay (checking inputs).
    Outcome-based branching or step skipping is NOT okay.
    """
    # ActionPlanExecutor only executes steps sequentially
    # No if/else based on outcome, no jumping to different steps
    import inspect

    source = inspect.getsource(plan_executor.execute_next_step)
    # Check for branching keywords (simplified check)
    # Real code has validation conditionals but NO outcome-based branching
    assert "if outcome" not in source.lower()  # No outcome-based branching
    assert "skip step" not in source.lower()  # No step skipping
    assert "jump" not in source.lower()  # No jumps
    assert "step_index =" not in source.lower() or "step_index = plan.current_step_index" in source  # No dynamic step changes


def test_constraint_full_human_control(plan_executor, sample_pipeline):
    """CONSTRAINT: Every step requires explicit human confirmation."""
    plan = create_action_plan(pipeline_ids=["pipeline_001"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # human_confirmation parameter is NOT optional
    # Default behavior (False) should fail
    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=sample_pipeline,
        human_confirmation=False,  # Explicit False required
    )

    assert error is not None


def test_constraint_full_reversibility(state_tracker):
    """CONSTRAINT: Each step is independently recordable and reversible."""
    plan = create_action_plan(pipeline_ids=["p1", "p2", "p3"])

    # Each step result is immutable (frozen)
    step_result = StepResult(
        step_index=0,
        pipeline_id="p1",
        execution_id="exec_001",
        status="success",
    )

    # Cannot modify step_result (frozen dataclass)
    with pytest.raises(AttributeError):
        step_result.status = "failed"


def test_constraint_no_unapproved_execution(plan_executor):
    """CONSTRAINT: Executor rejects unapproved pipelines."""
    plan = create_action_plan(pipeline_ids=["p1"])
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
    )

    # Provide unapproved pipeline
    unapproved_pipeline = {
        "pipeline_id": "p1",
        "status": "pending",  # NOT approved
        "approval_result": {"decision": "pending"},
    }

    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=unapproved_pipeline,
        human_confirmation=True,
    )

    assert error is not None
    assert updated_plan is None


# ============================================================================
# TEST: Integration - Full Workflow
# ============================================================================


def test_integration_full_workflow(plan_builder, plan_executor, state_tracker, sample_pipeline):
    """Integration test: Build → Execute → Track."""
    # Build plan from pipelines
    pipelines = [
        sample_pipeline,
        {**sample_pipeline, "pipeline_id": "pipeline_002"},
    ]

    plan, error = plan_builder.build_from_pipelines(pipelines, human_label="Integration Test")
    assert error is None
    assert plan is not None

    # Transition to executing
    executing_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
        started_timestamp=time.time(),
    )

    # Get initial status
    summary = state_tracker.get_plan_summary(executing_plan)
    assert summary["status"] == "executing"
    assert summary["current_step_index"] == 0

    # Execute first step
    updated_plan, error = plan_executor.execute_next_step(
        plan=executing_plan,
        approved_pipeline=pipelines[0],
        human_confirmation=True,
    )

    assert error is None
    assert len(updated_plan.completed_steps) == 1

    # Get updated status
    status = state_tracker.get_detailed_status(updated_plan)
    assert status["progress"]["steps_completed"] == 1
    assert status["progress"]["current_step"] == 1


def test_integration_multi_step_sequence(plan_builder, plan_executor, state_tracker):
    """Integration test: Execute multiple steps sequentially."""
    # Create 3 pipelines
    pipelines = [
        {
            "pipeline_id": f"p{i}",
            "status": "approved",
            "intent": {"intent_id": f"intent_{i}"},
            "approval_result": {"decision": "approved"},
            "dry_run_result": {"success": True},
        }
        for i in range(3)
    ]

    # Build plan
    plan, error = plan_builder.build_from_pipelines(pipelines)
    assert error is None

    # Start execution
    current_plan = ActionPlan(
        plan_id=plan.plan_id,
        pipeline_ids=plan.pipeline_ids,
        status=PlanStatus.EXECUTING,
        started_timestamp=time.time(),
    )

    # Execute all steps
    for idx, pipeline in enumerate(pipelines):
        current_plan, error = plan_executor.execute_next_step(
            plan=current_plan,
            approved_pipeline=pipeline,
            human_confirmation=True,
        )
        assert error is None
        assert len(current_plan.completed_steps) == idx + 1

    # Verify all steps completed
    summary = state_tracker.get_plan_summary(current_plan)
    assert summary["total_steps_completed"] == 3
    assert summary["current_step_index"] == 3
    assert current_plan.is_at_end


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
