"""Action Plan Builder for Phase 5.5 - Human-Guided Action Composition.

Validates and constructs ActionPlans from human-provided pipeline lists.
- Validates that all pipelines are approved
- Validates that each pipeline represents a single atomic action
- Produces immutable ActionPlan instances
- NO execution capability, NO approval logic
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from jessica.execution.action_plan import ActionPlan, PlanStatus, create_action_plan


class ActionPlanBuilder:
    """Builder for ActionPlan instances with validation."""

    def __init__(self, enabled: bool = True):
        """Initialize plan builder.
        
        Args:
            enabled: Whether plan building is enabled (reversible disable flag)
        """
        self.enabled = enabled

    def validate_pipeline(
        self,
        pipeline: Dict[str, Any],
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that a pipeline is approved and atomic.
        
        Args:
            pipeline: Pipeline dict from Phase 5.1.5 with structure:
                {
                    "pipeline_id": str,
                    "status": "approved",  # MUST be "approved"
                    "intent": {...},
                    "approval_result": {...},
                    "dry_run_result": {...},
                }
        
        Returns:
            (is_valid, error_message) tuple
        """
        if not self.enabled:
            return False, "Plan builder is disabled"

        # Check for required fields
        if not isinstance(pipeline, dict):
            return False, "Pipeline must be a dict"

        if "pipeline_id" not in pipeline:
            return False, "Pipeline missing 'pipeline_id'"

        if "status" not in pipeline:
            return False, "Pipeline missing 'status'"

        # Check approval status
        if pipeline["status"] != "approved":
            return False, f"Pipeline status is '{pipeline['status']}', expected 'approved'"

        # Check for intent
        if "intent" not in pipeline:
            return False, "Pipeline missing 'intent' (no action to execute)"

        intent = pipeline["intent"]
        if not isinstance(intent, dict) and not hasattr(intent, "intent_id"):
            return False, "Pipeline intent is invalid"

        # Check for approval result
        if "approval_result" not in pipeline:
            return False, "Pipeline missing 'approval_result'"

        approval_result = pipeline["approval_result"]
        if not isinstance(approval_result, dict):
            return False, "Approval result must be a dict"

        if "decision" not in approval_result:
            return False, "Approval result missing 'decision'"

        if approval_result["decision"] != "approved":
            return False, f"Approval decision is '{approval_result['decision']}', expected 'approved'"

        # All checks passed
        return True, None

    def build_from_pipelines(
        self,
        pipelines: List[Dict[str, Any]],
        human_label: str = "Untitled Plan",
        plan_id: Optional[str] = None,
    ) -> tuple[Optional[ActionPlan], Optional[str]]:
        """
        Build an ActionPlan from a list of approved pipelines.
        
        Args:
            pipelines: List of approved pipelines from Phase 5.1.5
            human_label: Human-readable label for the plan
            plan_id: Optional custom plan ID
        
        Returns:
            (plan, error) tuple where error is None if successful
        """
        if not self.enabled:
            return None, "Plan builder is disabled"

        if not isinstance(pipelines, list):
            return None, "Pipelines must be a list"

        if not pipelines:
            return None, "At least one pipeline is required to build a plan"

        # Validate each pipeline
        pipeline_ids = []
        for idx, pipeline in enumerate(pipelines):
            is_valid, error_msg = self.validate_pipeline(pipeline)
            if not is_valid:
                return None, f"Pipeline {idx}: {error_msg}"

            pipeline_ids.append(pipeline["pipeline_id"])

        # Create the plan
        try:
            plan = create_action_plan(
                pipeline_ids=pipeline_ids,
                human_label=human_label,
                plan_id=plan_id,
            )
            return plan, None
        except Exception as e:
            return None, f"Failed to create plan: {str(e)}"

    def build_from_pipeline_ids(
        self,
        pipeline_ids: List[str],
        human_label: str = "Untitled Plan",
        plan_id: Optional[str] = None,
    ) -> tuple[Optional[ActionPlan], Optional[str]]:
        """
        Build an ActionPlan directly from pipeline IDs.
        
        Use this when you already have validated pipeline IDs and don't need
        to re-validate the full pipeline structures.
        
        Args:
            pipeline_ids: List of approved pipeline IDs
            human_label: Human-readable label for the plan
            plan_id: Optional custom plan ID
        
        Returns:
            (plan, error) tuple where error is None if successful
        """
        if not self.enabled:
            return None, "Plan builder is disabled"

        if not isinstance(pipeline_ids, list):
            return None, "Pipeline IDs must be a list"

        if not pipeline_ids:
            return None, "At least one pipeline ID is required"

        # Validate that all items are strings (pipeline IDs)
        for idx, pid in enumerate(pipeline_ids):
            if not isinstance(pid, str):
                return None, f"Pipeline ID {idx} is not a string: {pid}"

            if not pid:
                return None, f"Pipeline ID {idx} is empty"

        # Create the plan
        try:
            plan = create_action_plan(
                pipeline_ids=pipeline_ids,
                human_label=human_label,
                plan_id=plan_id,
            )
            return plan, None
        except Exception as e:
            return None, f"Failed to create plan: {str(e)}"

    def disable(self):
        """Disable plan building (global safety switch)."""
        self.enabled = False

    def enable(self):
        """Enable plan building (reversible)."""
        self.enabled = True
