"""Phase 6: Decision Evaluator - Evaluates candidate proposals for risk, reversibility, etc.

Scores proposals on multiple dimensions using deterministic, stateless analysis.
NO execution, NO learning, NO modification. Read-only analysis layer only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from jessica.execution.decision_structures import (
    DecisionProposal,
    DecisionEvaluation,
    RiskLevel,
    ReversibilityScore,
)


class DecisionEvaluator:
    """Evaluates candidate proposals on safety, risk, reversibility, and complexity."""

    def __init__(self, enabled: bool = True):
        """Initialize decision evaluator.
        
        Args:
            enabled: Whether evaluator is enabled (reversible disable flag)
        """
        self.enabled = enabled

    def evaluate_proposal(
        self,
        proposal: DecisionProposal,
        pipeline_count: int = 1,
    ) -> Tuple[Optional[DecisionEvaluation], Optional[str]]:
        """
        Evaluate a single proposal for risk, reversibility, complexity.
        
        Args:
            proposal: DecisionProposal to evaluate
            pipeline_count: Number of pipelines in the proposal
        
        Returns:
            (evaluation, error) tuple:
            - On success: DecisionEvaluation, error=None
            - On failure: None, error message
        """
        if not self.enabled:
            return None, "Decision evaluator is disabled"

        if not isinstance(proposal, DecisionProposal):
            return None, "Proposal must be a DecisionProposal instance"

        try:
            # Determine risk level based on effort and step count
            risk_level = self._assess_risk_level(
                estimated_effort=proposal.estimated_effort,
                step_count=proposal.step_count,
            )
            
            # Determine reversibility based on step count
            reversibility = self._assess_reversibility(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Calculate complexity score (0.0 to 10.0)
            complexity_score = self._calculate_complexity_score(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Estimate duration (None if unknown)
            estimated_duration = self._estimate_duration(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Confidence in this evaluation
            confidence = self._assess_confidence(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Identify potential failure modes
            failure_modes = self._identify_failure_modes(
                step_count=proposal.step_count,
                estimated_effort=proposal.estimated_effort,
            )
            
            # Identify intervention points
            intervention_points = self._identify_intervention_points(
                step_count=proposal.step_count,
            )
            
            evaluation = DecisionEvaluation(
                proposal_id=proposal.proposal_id,
                risk_level=risk_level,
                reversibility=reversibility,
                complexity_score=complexity_score,
                estimated_duration_seconds=estimated_duration,
                confidence=confidence,
                risk_factors=risk_factors,
                failure_modes=failure_modes,
                intervention_points=intervention_points,
            )
            
            return evaluation, None
        
        except Exception as e:
            return None, f"Failed to evaluate proposal: {str(e)}"

    def _assess_risk_level(
        self,
        estimated_effort: str,
        step_count: int,
    ) -> RiskLevel:
        """Assess overall risk level (deterministic)."""
        if estimated_effort == "low" and step_count <= 1:
            return RiskLevel.VERY_LOW
        elif estimated_effort == "low" or step_count <= 2:
            return RiskLevel.LOW
        elif estimated_effort == "medium" and step_count <= 3:
            return RiskLevel.MEDIUM
        elif estimated_effort == "high" or step_count > 5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM

    def _assess_reversibility(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> ReversibilityScore:
        """Assess reversibility of the plan (deterministic)."""
        if step_count <= 1:
            return ReversibilityScore.FULLY_REVERSIBLE
        elif step_count <= 2 and estimated_effort != "high":
            return ReversibilityScore.MOSTLY_REVERSIBLE
        elif step_count <= 3:
            return ReversibilityScore.PARTIALLY_REVERSIBLE
        elif step_count <= 5 or estimated_effort == "high":
            return ReversibilityScore.BARELY_REVERSIBLE
        else:
            return ReversibilityScore.IRREVERSIBLE

    def _calculate_complexity_score(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> float:
        """Calculate complexity as float from 0.0 to 10.0 (deterministic)."""
        # Base score from step count
        base = min(step_count * 2.0, 8.0)
        
        # Adjust for effort
        if estimated_effort == "low":
            adjustment = -1.0
        elif estimated_effort == "high":
            adjustment = 2.0
        else:
            adjustment = 0.0
        
        score = base + adjustment
        return max(0.0, min(10.0, score))

    def _estimate_duration(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> Optional[float]:
        """Estimate duration in seconds (deterministic, None if very uncertain)."""
        if estimated_effort == "low":
            return step_count * 5.0  # ~5 seconds per step
        elif estimated_effort == "medium":
            return step_count * 15.0  # ~15 seconds per step
        elif estimated_effort == "high":
            return step_count * 30.0  # ~30 seconds per step
        else:
            return None

    def _assess_confidence(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> float:
        """Confidence in evaluation (0.0 to 1.0, deterministic)."""
        # Higher confidence for simple plans
        if step_count <= 2 and estimated_effort == "low":
            return 0.95
        elif step_count <= 3:
            return 0.85
        elif step_count <= 5:
            return 0.70
        else:
            return 0.50

    def _identify_risk_factors(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> List[str]:
        """Identify specific risk factors (deterministic)."""
        factors = []
        
        if step_count > 1:
            factors.append("Multiple steps increase cumulative risk")
        
        if step_count > 3:
            factors.append("Plan complexity makes it harder to verify")
        
        if estimated_effort == "high":
            factors.append("High effort required; more opportunities for error")
        
        if step_count > 5:
            factors.append("Many steps; difficult to undo if something fails")
        
        return factors

    def _identify_failure_modes(
        self,
        step_count: int,
        estimated_effort: str,
    ) -> List[str]:
        """Identify potential failure modes (deterministic)."""
        modes = []
        
        if step_count >= 1:
            modes.append("Step execution could timeout or hang")
        
        if step_count >= 2:
            modes.append("Partial failure: some steps succeed, others fail")
        
        if step_count >= 3:
            modes.append("State mismatch: plan assumes state that may have changed")
        
        if estimated_effort == "high":
            modes.append("System resource exhaustion from prolonged execution")
        
        return modes

    def _identify_intervention_points(
        self,
        step_count: int,
    ) -> List[str]:
        """Identify recommended intervention points (deterministic)."""
        points = []
        
        if step_count >= 1:
            points.append("After each step: verify completion before proceeding")
        
        if step_count >= 2:
            points.append("At halfway point: assess progress and confirm continuation")
        
        if step_count >= 3:
            points.append("Before final step: validate that all prerequisites met")
        
        if step_count > 5:
            points.append("Consider breaking into multiple smaller plans")
        
        return points

    def evaluate_proposals(
        self,
        proposals: List[DecisionProposal],
    ) -> Tuple[Dict[str, DecisionEvaluation], Optional[str]]:
        """
        Evaluate multiple proposals.
        
        Args:
            proposals: List of DecisionProposal objects
        
        Returns:
            (evaluations_dict, error) tuple where keys are proposal_ids
        """
        if not self.enabled:
            return {}, "Decision evaluator is disabled"

        evaluations = {}
        
        for proposal in proposals:
            evaluation, error = self.evaluate_proposal(proposal)
            if error is None and evaluation:
                evaluations[proposal.proposal_id] = evaluation
        
        return evaluations, None

    def compare_proposals(
        self,
        evaluations: Dict[str, DecisionEvaluation],
    ) -> Dict[str, Any]:
        """
        Generate comparison summary across multiple evaluations.
        
        Args:
            evaluations: Dict of proposal_id → DecisionEvaluation
        
        Returns:
            Dict with comparison data (safest, simplest, fastest, etc.)
        """
        if not evaluations:
            return {}

        # Find extremes (all read-only, no modification)
        risk_order = {
            RiskLevel.VERY_LOW: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.VERY_HIGH: 4,
        }
        
        safest = min(
            evaluations.values(),
            key=lambda e: risk_order.get(e.risk_level, 2)
        )
        
        simplest = min(
            evaluations.values(),
            key=lambda e: e.complexity_score
        )
        
        fastest = min(
            evaluations.values(),
            key=lambda e: e.estimated_duration_seconds or float('inf')
        )
        
        return {
            "safest_proposal_id": safest.proposal_id,
            "simplest_proposal_id": simplest.proposal_id,
            "fastest_proposal_id": fastest.proposal_id,
            "total_evaluations": len(evaluations),
        }

    def disable(self):
        """Disable proposal evaluation (global safety switch)."""
        self.enabled = False

    def enable(self):
        """Enable proposal evaluation (reversible)."""
        self.enabled = True
