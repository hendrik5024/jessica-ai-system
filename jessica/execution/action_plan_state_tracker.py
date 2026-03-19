"""Action Plan State Tracker for Phase 5.5 - Human-Guided Action Composition.

Read-only state tracking and reporting for ActionPlans.
- Tracks execution progress without modifying state
- Generates human-readable status reports
- NO automated decisions, NO modifications to plan state
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from jessica.execution.action_plan import ActionPlan, PlanStatus, StepResult


class ActionPlanStateTracker:
    """Read-only tracker for ActionPlan execution state."""

    def __init__(self, enabled: bool = True):
        """Initialize state tracker.
        
        Args:
            enabled: Whether tracking is enabled (reversible disable flag)
        """
        self.enabled = enabled

    def get_plan_summary(
        self,
        plan: ActionPlan,
    ) -> Dict[str, Any]:
        """
        Get read-only summary of plan state.
        
        Args:
            plan: The ActionPlan to summarize
        
        Returns:
            Dict with plan metadata and state (read-only, no side effects)
        """
        if not self.enabled:
            return {}

        return {
            "plan_id": plan.plan_id,
            "human_label": plan.human_label,
            "status": plan.status.value,
            "current_step_index": plan.current_step_index,
            "total_steps": plan.total_steps,
            "progress_percent": plan.progress_percent,
            "is_at_end": plan.is_at_end,
            "next_pipeline_id": plan.next_pipeline_id,
            "total_steps_completed": len(plan.completed_steps),
            "has_failed": plan.failed_step is not None,
        }

    def get_detailed_status(
        self,
        plan: ActionPlan,
    ) -> Dict[str, Any]:
        """
        Get detailed status report including timestamps and history.
        
        Args:
            plan: The ActionPlan to analyze
        
        Returns:
            Dict with comprehensive status information
        """
        if not self.enabled:
            return {}

        elapsed_seconds = None
        if plan.started_timestamp is not None:
            if plan.completed_timestamp is not None:
                elapsed_seconds = plan.completed_timestamp - plan.started_timestamp
            else:
                import time

                elapsed_seconds = time.time() - plan.started_timestamp

        return {
            "plan_id": plan.plan_id,
            "human_label": plan.human_label,
            "status": plan.status.value,
            "progress": {
                "current_step": plan.current_step_index,
                "total_steps": plan.total_steps,
                "percent_complete": plan.progress_percent,
                "steps_completed": len(plan.completed_steps),
            },
            "timeline": {
                "created_timestamp": plan.created_timestamp,
                "started_timestamp": plan.started_timestamp,
                "completed_timestamp": plan.completed_timestamp,
                "elapsed_seconds": elapsed_seconds,
            },
            "execution": {
                "completed_steps": [s.to_dict() for s in plan.completed_steps],
                "failed_step": plan.failed_step.to_dict() if plan.failed_step else None,
            },
        }

    def get_next_step_info(
        self,
        plan: ActionPlan,
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about the next step to execute.
        
        Args:
            plan: The ActionPlan to query
        
        Returns:
            Dict with next step info, or None if at end
        """
        if not self.enabled:
            return None

        if plan.is_at_end:
            return None

        return {
            "step_index": plan.current_step_index,
            "pipeline_id": plan.next_pipeline_id,
            "steps_remaining": plan.total_steps - plan.current_step_index,
        }

    def get_completed_steps(
        self,
        plan: ActionPlan,
    ) -> List[Dict[str, Any]]:
        """
        Get list of all completed steps.
        
        Args:
            plan: The ActionPlan to query
        
        Returns:
            List of completed step dicts (read-only)
        """
        if not self.enabled:
            return []

        return [s.to_dict() for s in plan.completed_steps]

    def get_step_result(
        self,
        plan: ActionPlan,
        step_index: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get result for a specific completed step.
        
        Args:
            plan: The ActionPlan to query
            step_index: Index of the step to retrieve
        
        Returns:
            Step result dict, or None if not found
        """
        if not self.enabled:
            return None

        for step in plan.completed_steps:
            if step.step_index == step_index:
                return step.to_dict()

        return None

    def is_plan_complete(
        self,
        plan: ActionPlan,
    ) -> bool:
        """
        Check if plan has completed all steps.
        
        Args:
            plan: The ActionPlan to check
        
        Returns:
            True if all steps are completed, False otherwise
        """
        if not self.enabled:
            return False

        return plan.status == PlanStatus.COMPLETED or plan.is_at_end

    def is_plan_failed(
        self,
        plan: ActionPlan,
    ) -> bool:
        """
        Check if plan has failed.
        
        Args:
            plan: The ActionPlan to check
        
        Returns:
            True if plan has a failed step, False otherwise
        """
        if not self.enabled:
            return False

        return plan.failed_step is not None or plan.status == PlanStatus.FAILED

    def get_failure_reason(
        self,
        plan: ActionPlan,
    ) -> Optional[str]:
        """
        Get the reason for plan failure, if any.
        
        Args:
            plan: The ActionPlan to query
        
        Returns:
            Failure reason string, or None if not failed
        """
        if not self.enabled:
            return None

        if plan.failed_step is None:
            return None

        return plan.failed_step.error_message

    def disable(self):
        """Disable state tracking (global flag)."""
        self.enabled = False

    def enable(self):
        """Enable state tracking (reversible)."""
        self.enabled = True
