"""Action Plan Executor for Phase 5.5 - Human-Guided Action Composition.

Executes ActionPlans step-by-step with full human control and explicit confirmation.
- Executes ONE step per explicit human call (no auto-advancement)
- Requires human confirmation before each step
- Uses Phase 5.2 ActionExecutor for atomic action execution
- Records all steps to ExecutionTracker
- NO retries, NO branching, NO conditional logic
- NO autonomy: Cannot trigger own execution
"""
from __future__ import annotations

from typing import Any, Dict, Optional
import time

from jessica.execution.action_plan import ActionPlan, PlanStatus, StepResult
from jessica.execution.keyboard_mouse_executor import ActionExecutor
from jessica.execution.execution_tracker import ExecutionTracker, ExecutionStatus


class ActionPlanExecutor:
    """Executes ActionPlans with full human control, one step at a time."""

    def __init__(self, enabled: bool = True):
        """Initialize plan executor.
        
        Args:
            enabled: Whether plan execution is enabled (reversible disable flag)
        """
        self.enabled = enabled
        self.action_executor = ActionExecutor(enabled=enabled)
        self.tracker = self.action_executor.tracker

    def execute_next_step(
        self,
        plan: ActionPlan,
        approved_pipeline: Dict[str, Any],
        human_confirmation: bool = True,
    ) -> tuple[Optional[ActionPlan], Optional[str]]:
        """
        Execute the next step in an ActionPlan (ONE step only).
        
        CONSTRAINTS:
        - MUST have plan.status == "executing" (human must start the plan first)
        - MUST have human_confirmation == True (explicit human approval required)
        - MUST be at a valid step (current_step_index < total_steps)
        - WILL NOT auto-advance, retry, or branch
        - WILL NOT modify plan status (caller is responsible)
        
        Args:
            plan: The ActionPlan to execute a step from
            approved_pipeline: The approved pipeline dict for the next step:
                {
                    "pipeline_id": str,
                    "status": "approved",
                    "intent": {...},
                    "approval_result": {...},
                    "dry_run_result": {...},
                }
            human_confirmation: MUST be True (explicit confirmation required)
        
        Returns:
            (updated_plan, error) tuple:
            - On success: updated plan with step result recorded, no error
            - On failure: None, error message
        """
        if not self.enabled:
            return None, "Plan executor is disabled"

        # Check preconditions
        if plan.status != PlanStatus.EXECUTING:
            return None, f"Plan status is {plan.status.value}, expected 'executing'"

        if not human_confirmation:
            return None, "Human confirmation is required to execute a step (safety constraint)"

        if plan.is_at_end:
            return None, "Plan is at end, no more steps to execute"

        # Validate that the provided pipeline matches the next expected step
        if "pipeline_id" not in approved_pipeline:
            return None, "Pipeline missing 'pipeline_id'"

        expected_pipeline_id = plan.next_pipeline_id
        provided_pipeline_id = approved_pipeline["pipeline_id"]

        if provided_pipeline_id != expected_pipeline_id:
            return None, (
                f"Pipeline mismatch: provided {provided_pipeline_id}, "
                f"expected {expected_pipeline_id}"
            )

        # Validate that the pipeline is approved
        if approved_pipeline.get("status") != "approved":
            return None, f"Pipeline status is '{approved_pipeline.get('status')}', expected 'approved'"

        if approved_pipeline.get("approval_result", {}).get("decision") != "approved":
            return None, "Pipeline approval decision is not 'approved'"

        # Execute the step using Phase 5.2 ActionExecutor
        step_index = plan.current_step_index
        start_time = time.time()

        try:
            execution_outcome = self.action_executor.execute_from_pipeline(approved_pipeline)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Determine step result status
            if execution_outcome.status == ExecutionStatus.SUCCESS:
                step_status = "success"
            elif execution_outcome.status == ExecutionStatus.FAILED:
                step_status = "failed"
            else:
                step_status = execution_outcome.status.value

            # Create step result (immutable)
            step_result = StepResult(
                step_index=step_index,
                pipeline_id=provided_pipeline_id,
                execution_id=execution_outcome.system_state_after.get("execution_id")
                if execution_outcome.system_state_after
                else None,
                status=step_status,
                error_message=execution_outcome.error_message,
                duration_ms=duration_ms,
            )

            # Update plan with step result
            # Note: We don't modify plan.status here (caller decides if plan continues or stops)
            updated_completed_steps = plan.completed_steps + [step_result]
            updated_plan = ActionPlan(
                plan_id=plan.plan_id,
                pipeline_ids=plan.pipeline_ids,
                current_step_index=plan.current_step_index + 1,  # Advance to next step
                status=plan.status,  # Preserve status (caller controls it)
                completed_steps=updated_completed_steps,
                failed_step=step_result if step_status == "failed" else None,
                created_timestamp=plan.created_timestamp,
                started_timestamp=plan.started_timestamp,
                completed_timestamp=plan.completed_timestamp,
                human_label=plan.human_label,
            )

            return updated_plan, None

        except Exception as e:
            # Execution error
            step_result = StepResult(
                step_index=step_index,
                pipeline_id=provided_pipeline_id,
                execution_id=None,
                status="failed",
                error_message=f"Execution error: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000,
            )

            updated_plan = ActionPlan(
                plan_id=plan.plan_id,
                pipeline_ids=plan.pipeline_ids,
                current_step_index=plan.current_step_index + 1,  # Still advance index
                status=plan.status,
                completed_steps=plan.completed_steps + [step_result],
                failed_step=step_result,
                created_timestamp=plan.created_timestamp,
                started_timestamp=plan.started_timestamp,
                completed_timestamp=plan.completed_timestamp,
                human_label=plan.human_label,
            )

            return updated_plan, f"Step {step_index} execution failed: {str(e)}"

    def disable(self):
        """Disable plan execution (global safety switch)."""
        self.enabled = False
        self.action_executor.enabled = False

    def enable(self):
        """Enable plan execution (reversible)."""
        self.enabled = True
        self.action_executor.enabled = True

    def get_execution_history(
        self,
        plan: ActionPlan,
    ) -> Dict[str, Any]:
        """
        Get read-only execution history for a plan.
        
        Args:
            plan: The ActionPlan to get history for
        
        Returns:
            Dict with completed steps and failure info (read-only)
        """
        return {
            "plan_id": plan.plan_id,
            "completed_steps": [s.to_dict() for s in plan.completed_steps],
            "failed_step": plan.failed_step.to_dict() if plan.failed_step else None,
            "total_steps_completed": len(plan.completed_steps),
            "total_steps": plan.total_steps,
        }
