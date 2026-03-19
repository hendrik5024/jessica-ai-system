"""Phase 6: Decision Proposer - Generates candidate ActionPlan proposals.

Analyzes human goals and generates multiple candidate ActionPlans using
existing approved pipelines. NO execution, NO approval, NO learning.

Read-only analysis layer only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import uuid

from jessica.execution.action_plan import ActionPlan, create_action_plan
from jessica.execution.decision_structures import DecisionProposal


class DecisionProposer:
    """Generates candidate ActionPlan proposals from human goals."""

    def __init__(self, enabled: bool = True):
        """Initialize decision proposer.
        
        Args:
            enabled: Whether proposer is enabled (reversible disable flag)
        """
        self.enabled = enabled

    def propose_plans_from_goal(
        self,
        goal_description: str,
        available_pipelines: Dict[str, Dict[str, Any]],
        max_proposals: int = 3,
    ) -> Tuple[List[DecisionProposal], Optional[str]]:
        """
        Generate candidate ActionPlan proposals from a human goal.
        
        Args:
            goal_description: Human's stated goal or request
            available_pipelines: Dict of approved pipelines:
                {
                    "pipeline_id": {
                        "pipeline_id": str,
                        "status": "approved",
                        "intent": {...},
                        ...
                    },
                    ...
                }
            max_proposals: Maximum number of proposals to generate
        
        Returns:
            (proposals, error) tuple:
            - On success: List of DecisionProposal objects, error=None
            - On failure: Empty list, error message
        """
        if not self.enabled:
            return [], "Decision proposer is disabled"

        if not goal_description or not goal_description.strip():
            return [], "Goal description cannot be empty"

        if not available_pipelines:
            return [], "No available pipelines provided"

        if not isinstance(available_pipelines, dict):
            return [], "Available pipelines must be a dict"

        # Validate that all pipelines are approved
        pipeline_ids = []
        for pid, pipeline in available_pipelines.items():
            if not isinstance(pipeline, dict):
                return [], f"Pipeline {pid} is not a dict"
            
            if pipeline.get("status") != "approved":
                return [], f"Pipeline {pid} has status {pipeline.get('status')}, expected 'approved'"
            
            pipeline_ids.append(pid)

        if not pipeline_ids:
            return [], "No approved pipelines available"

        # Generate proposals (deterministic, based on goal keywords and pipeline availability)
        proposals = []
        
        # Strategy 1: Direct approach - use available pipelines as-is
        if len(pipeline_ids) >= 1:
            proposal1, error = self._create_proposal(
                goal_description=goal_description,
                pipeline_ids=pipeline_ids,
                strategy="direct",
                available_pipelines=available_pipelines,
            )
            if error is None:
                proposals.append(proposal1)

        # Strategy 2: Sequential combination - create more granular plan if possible
        if len(pipeline_ids) >= 2 and len(proposals) < max_proposals:
            proposal2, error = self._create_proposal(
                goal_description=goal_description,
                pipeline_ids=pipeline_ids[:len(pipeline_ids)//2 + 1],  # Use first half
                strategy="sequential",
                available_pipelines=available_pipelines,
            )
            if error is None:
                proposals.append(proposal2)

        # Strategy 3: Conservative approach - minimal steps if available
        if len(pipeline_ids) >= 1 and len(proposals) < max_proposals:
            proposal3, error = self._create_proposal(
                goal_description=goal_description,
                pipeline_ids=[pipeline_ids[0]],  # Minimal approach
                strategy="conservative",
                available_pipelines=available_pipelines,
            )
            if error is None:
                proposals.append(proposal3)

        if not proposals:
            return [], "Failed to generate any proposals"

        return proposals[:max_proposals], None

    def _create_proposal(
        self,
        goal_description: str,
        pipeline_ids: List[str],
        strategy: str,
        available_pipelines: Dict[str, Dict[str, Any]],
    ) -> Tuple[Optional[DecisionProposal], Optional[str]]:
        """
        Create a single DecisionProposal.
        
        Args:
            goal_description: Human's goal
            pipeline_ids: Pipelines to use in this proposal
            strategy: Strategy name (direct, sequential, conservative)
            available_pipelines: Available approved pipelines
        
        Returns:
            (proposal, error) tuple
        """
        try:
            proposal_id = f"proposal_{uuid.uuid4().hex[:12]}"
            action_plan_id = f"plan_{uuid.uuid4().hex[:12]}"
            
            # Estimate effort based on strategy and number of steps
            if strategy == "conservative":
                estimated_effort = "low"
            elif strategy == "direct":
                estimated_effort = "medium"
            else:  # sequential
                estimated_effort = "high"
            
            # Create rationale based on strategy
            rationale = self._generate_rationale(
                goal_description=goal_description,
                strategy=strategy,
                step_count=len(pipeline_ids),
            )
            
            # Create description
            description = self._generate_description(
                strategy=strategy,
                step_count=len(pipeline_ids),
                goal=goal_description,
            )
            
            proposal = DecisionProposal(
                proposal_id=proposal_id,
                action_plan_id=action_plan_id,
                description=description,
                step_count=len(pipeline_ids),
                estimated_effort=estimated_effort,
                rationale=rationale,
            )
            
            return proposal, None
        
        except Exception as e:
            return None, f"Failed to create proposal: {str(e)}"

    def _generate_rationale(
        self,
        goal_description: str,
        strategy: str,
        step_count: int,
    ) -> str:
        """Generate human-readable rationale for a proposal."""
        if strategy == "conservative":
            return (
                f"Minimal approach: Uses {step_count} critical step(s) to achieve '{goal_description}'. "
                "Lowest risk, easiest to verify and undo. Best if you want certainty."
            )
        elif strategy == "direct":
            return (
                f"Direct approach: Uses {step_count} steps to achieve '{goal_description}'. "
                "Balance of completeness and risk. Recommended for most goals."
            )
        else:  # sequential
            return (
                f"Sequential approach: Uses {step_count} steps to achieve '{goal_description}'. "
                "More thorough and comprehensive. Best if you need detail and certainty."
            )

    def _generate_description(
        self,
        strategy: str,
        step_count: int,
        goal: str,
    ) -> str:
        """Generate human-readable description of a proposal."""
        if strategy == "conservative":
            return f"Conservative plan ({step_count} step) to: {goal}"
        elif strategy == "direct":
            return f"Direct plan ({step_count} steps) to: {goal}"
        else:  # sequential
            return f"Sequential plan ({step_count} steps) to: {goal}"

    def ask_clarifying_questions(
        self,
        goal_description: str,
    ) -> List[str]:
        """
        Ask clarifying questions about the goal before proposing plans.
        
        Args:
            goal_description: Human's stated goal
        
        Returns:
            List of clarifying questions (advisory only)
        """
        if not self.enabled:
            return []

        questions = []
        
        # Always ask about constraints
        questions.append(
            "What constraints or limitations should this plan respect? "
            "(e.g., time, resources, safety)"
        )
        
        # Ask about preferences
        questions.append(
            "Do you prefer a quick solution (fewer steps) or a thorough one (more verification)?"
        )
        
        # Ask about risk tolerance
        questions.append(
            "What is your risk tolerance? Are you comfortable with trial-and-error, "
            "or do you need high certainty?"
        )
        
        # Ask about reversibility needs
        questions.append(
            "How important is reversibility? Can this be undone if something goes wrong?"
        )
        
        return questions

    def disable(self):
        """Disable proposal generation (global safety switch)."""
        self.enabled = False

    def enable(self):
        """Enable proposal generation (reversible)."""
        self.enabled = True
