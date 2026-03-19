"""Phase 6: Decision Orchestrator - Coordinates proposal → evaluation → explanation.

Master coordinator for decision support pipeline. NO execution, NO approval hooks.
Purely read-only advisory layer.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from jessica.execution.decision_structures import (
    DecisionBundle,
    DecisionProposal,
    create_decision_bundle,
)
from jessica.execution.decision_proposer import DecisionProposer
from jessica.execution.decision_evaluator import DecisionEvaluator
from jessica.execution.decision_explainer import DecisionExplainer


class DecisionOrchestrator:
    """Coordinates complete decision support workflow."""

    def __init__(self, enabled: bool = True):
        """Initialize decision orchestrator.
        
        Args:
            enabled: Whether orchestrator is enabled (reversible disable flag)
        """
        self.enabled = enabled
        self.proposer = DecisionProposer(enabled=enabled)
        self.evaluator = DecisionEvaluator(enabled=enabled)
        self.explainer = DecisionExplainer(enabled=enabled)

    def analyze_goal(
        self,
        goal_description: str,
        available_pipelines: Dict[str, Dict[str, Any]],
        max_proposals: int = 3,
        ask_questions: bool = True,
    ) -> Tuple[Optional[DecisionBundle], Optional[str]]:
        """
        Complete decision support analysis: propose → evaluate → explain.
        
        This is the main entry point for Phase 6 decision support.
        
        Args:
            goal_description: Human's stated goal or request
            available_pipelines: Dict of approved pipelines from Phase 5.1.5:
                {
                    "pipeline_id": {
                        "pipeline_id": str,
                        "status": "approved",
                        "intent": {...},
                        "approval_result": {...},
                        ...
                    },
                    ...
                }
            max_proposals: Maximum number of proposals to generate (1-10)
            ask_questions: Whether to ask clarifying questions first
        
        Returns:
            (bundle, error) tuple:
            - On success: DecisionBundle with proposals/evaluations/explanations
            - On failure: None, error message
        """
        if not self.enabled:
            return None, "Decision orchestrator is disabled"

        # Validate inputs
        if not goal_description or not goal_description.strip():
            return None, "Goal description cannot be empty"

        if not available_pipelines:
            return None, "No available pipelines provided"

        if not isinstance(max_proposals, int) or max_proposals < 1 or max_proposals > 10:
            return None, "max_proposals must be between 1 and 10"

        # Create bundle to hold all analysis results
        bundle = create_decision_bundle(goal_description)

        # Step 1: Ask clarifying questions (optional)
        if ask_questions:
            questions = self.proposer.ask_clarifying_questions(goal_description)
            bundle = DecisionBundle(
                bundle_id=bundle.bundle_id,
                goal_description=bundle.goal_description,
                clarifying_questions=questions,
            )

        # Step 2: Propose candidate plans
        proposals, error = self.proposer.propose_plans_from_goal(
            goal_description=goal_description,
            available_pipelines=available_pipelines,
            max_proposals=max_proposals,
        )

        if error:
            return None, f"Proposal generation failed: {error}"

        if not proposals:
            return None, "No proposals could be generated"

        # Step 3: Evaluate each proposal
        evaluations, error = self.evaluator.evaluate_proposals(proposals)

        if error:
            return None, f"Evaluation failed: {error}"

        if not evaluations:
            return None, "No evaluations could be generated"

        # Step 4: Generate explanations
        explanations, error = self.explainer.explain_proposals(proposals, evaluations)

        if error:
            return None, f"Explanation generation failed: {error}"

        # Step 5: Identify best recommendation
        comparison = self.evaluator.compare_proposals(evaluations)
        recommended_id = comparison.get("safest_proposal_id")
        recommendation_rationale = None
        
        if recommended_id:
            recommendation_rationale = (
                f"Recommended: proposal {recommended_id} "
                f"(safest option with lowest risk)"
            )

        # Step 6: Assemble final bundle
        final_bundle = DecisionBundle(
            bundle_id=bundle.bundle_id,
            goal_description=goal_description,
            proposals=proposals,
            evaluations=evaluations,
            explanations=explanations,
            recommended_proposal_id=recommended_id,
            recommendation_rationale=recommendation_rationale,
            clarifying_questions=bundle.clarifying_questions,
            analysis_notes=(
                f"Generated {len(proposals)} proposal(s) from {len(available_pipelines)} "
                f"available pipeline(s). All proposals are advisory-only. "
                f"Execution requires explicit human approval."
            ),
        )

        return final_bundle, None

    def get_proposal_details(
        self,
        bundle: DecisionBundle,
        proposal_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete details for a single proposal (read-only).
        
        Args:
            bundle: DecisionBundle containing proposals
            proposal_id: ID of proposal to retrieve
        
        Returns:
            Dict with proposal details, or None if not found
        """
        if not self.enabled:
            return None

        # Find proposal
        proposal = None
        for p in bundle.proposals:
            if p.proposal_id == proposal_id:
                proposal = p
                break

        if not proposal:
            return None

        # Get evaluation and explanation
        evaluation = bundle.evaluations.get(proposal_id)
        explanation = bundle.explanations.get(proposal_id)

        if not evaluation or not explanation:
            return None

        return {
            "proposal": proposal.to_dict(),
            "evaluation": evaluation.to_dict(),
            "explanation": explanation.to_dict(),
        }

    def rank_proposals_by_criterion(
        self,
        bundle: DecisionBundle,
        criterion: str = "risk",
    ) -> List[Dict[str, Any]]:
        """
        Rank proposals by specified criterion (read-only).
        
        Args:
            bundle: DecisionBundle containing proposals
            criterion: One of: "risk", "complexity", "effort", "reversibility"
        
        Returns:
            Ranked list of proposal summaries
        """
        if not self.enabled:
            return []

        if criterion == "risk":
            sorted_proposals = bundle.sorted_proposals_by_risk
        else:
            # Default: sort by complexity
            sorted_proposals = sorted(
                bundle.proposals,
                key=lambda p: bundle.evaluations.get(p.proposal_id, None) and
                             bundle.evaluations[p.proposal_id].complexity_score or 999
            )

        result = []
        for proposal in sorted_proposals:
            evaluation = bundle.evaluations.get(proposal.proposal_id)
            if evaluation:
                result.append({
                    "proposal_id": proposal.proposal_id,
                    "description": proposal.description,
                    "risk": evaluation.risk_level.value,
                    "complexity": f"{evaluation.complexity_score:.1f}",
                    "estimated_effort": proposal.estimated_effort,
                })

        return result

    def format_bundle_for_human(
        self,
        bundle: DecisionBundle,
    ) -> str:
        """
        Format DecisionBundle as human-readable text report.
        
        Args:
            bundle: DecisionBundle to format
        
        Returns:
            Formatted text suitable for display to human
        """
        if not self.enabled:
            return ""

        lines = []
        lines.append("=" * 70)
        lines.append("DECISION SUPPORT ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"\nGoal: {bundle.goal_description}\n")

        if bundle.clarifying_questions:
            lines.append("CLARIFYING QUESTIONS:")
            for q in bundle.clarifying_questions:
                lines.append(f"  • {q}")
            lines.append("")

        lines.append(f"PROPOSALS: {bundle.proposal_count} option(s) identified\n")

        for i, proposal in enumerate(bundle.proposals, 1):
            evaluation = bundle.evaluations.get(proposal.proposal_id)
            explanation = bundle.explanations.get(proposal.proposal_id)

            lines.append(f"--- Option {i}: {proposal.description} ---")
            if explanation:
                lines.append(f"Summary: {explanation.summary}")
                lines.append(f"Effort: {proposal.estimated_effort}")
                if evaluation:
                    lines.append(f"Risk: {evaluation.risk_level.value}")
                    lines.append(f"Complexity: {evaluation.complexity_score:.1f}/10")
            lines.append("")

        if bundle.recommended_proposal_id:
            lines.append("RECOMMENDATION:")
            lines.append(f"  {bundle.recommendation_rationale}")
            lines.append("")

        lines.append("NOTE: These are advisory suggestions only. ")
        lines.append("Execution requires explicit human approval.")
        lines.append("=" * 70)

        return "\n".join(lines)

    def disable(self):
        """Disable decision support (global safety switch)."""
        self.enabled = False
        self.proposer.disable()
        self.evaluator.disable()
        self.explainer.disable()

    def enable(self):
        """Enable decision support (reversible)."""
        self.enabled = True
        self.proposer.enable()
        self.evaluator.enable()
        self.explainer.enable()
