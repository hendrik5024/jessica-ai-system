"""Phase 6: Decision Explainer - Converts proposals + evaluations into human-readable explanations.

Generates clear, unbiased explanations of proposed plans and their trade-offs.
NO persuasion, NO coercion, NO execution. Read-only advisory layer only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from jessica.execution.decision_structures import (
    DecisionProposal,
    DecisionEvaluation,
    DecisionExplanation,
    RiskLevel,
    ReversibilityScore,
)


class DecisionExplainer:
    """Generates human-readable explanations of proposals and evaluations."""

    def __init__(self, enabled: bool = True):
        """Initialize decision explainer.
        
        Args:
            enabled: Whether explainer is enabled (reversible disable flag)
        """
        self.enabled = enabled

    def explain_proposal(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> Tuple[Optional[DecisionExplanation], Optional[str]]:
        """
        Generate human-readable explanation of a proposal + evaluation.
        
        Args:
            proposal: DecisionProposal to explain
            evaluation: DecisionEvaluation for this proposal
        
        Returns:
            (explanation, error) tuple
        """
        if not self.enabled:
            return None, "Decision explainer is disabled"

        if proposal.proposal_id != evaluation.proposal_id:
            return None, "Proposal and evaluation IDs must match"

        try:
            explanation = DecisionExplanation(
                proposal_id=proposal.proposal_id,
                summary=self._generate_summary(proposal, evaluation),
                what_it_does=self._generate_what_it_does(proposal),
                how_it_works=self._generate_how_it_works(proposal),
                why_proposed=proposal.rationale,
                advantages=self._generate_advantages(proposal, evaluation),
                disadvantages=self._generate_disadvantages(proposal, evaluation),
                uncertainties=self._generate_uncertainties(evaluation),
                risk_summary=self._generate_risk_summary(evaluation),
                safety_notes=self._generate_safety_notes(proposal, evaluation),
                recommendations=self._generate_recommendations(proposal, evaluation),
                when_to_use=self._generate_when_to_use(proposal, evaluation),
                when_not_to_use=self._generate_when_not_to_use(proposal, evaluation),
            )
            
            return explanation, None
        
        except Exception as e:
            return None, f"Failed to generate explanation: {str(e)}"

    def _generate_summary(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> str:
        """Generate one-sentence summary."""
        risk_word = {
            RiskLevel.VERY_LOW: "very safe",
            RiskLevel.LOW: "safe",
            RiskLevel.MEDIUM: "moderate-risk",
            RiskLevel.HIGH: "risky",
            RiskLevel.VERY_HIGH: "very risky",
        }.get(evaluation.risk_level, "moderate")
        
        return (
            f"A {risk_word} plan with {proposal.step_count} step(s), "
            f"estimated {proposal.estimated_effort} effort."
        )

    def _generate_what_it_does(
        self,
        proposal: DecisionProposal,
    ) -> str:
        """Explain what the plan accomplishes."""
        return f"This plan accomplishes the goal: {proposal.description}"

    def _generate_how_it_works(
        self,
        proposal: DecisionProposal,
    ) -> str:
        """Explain step-by-step breakdown."""
        if proposal.step_count == 1:
            return f"This plan executes a single action to achieve the goal."
        elif proposal.step_count <= 3:
            return (
                f"This plan executes {proposal.step_count} sequential steps: "
                f"each step builds on the previous one to achieve the goal."
            )
        else:
            return (
                f"This plan executes {proposal.step_count} sequential steps "
                f"in a structured sequence to achieve the goal. "
                f"Each step must complete successfully before the next begins."
            )

    def _generate_advantages(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> List[str]:
        """Generate list of advantages."""
        advantages = []
        
        if evaluation.risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW]:
            advantages.append("Low risk - well-understood approach")
        
        if evaluation.reversibility in [
            ReversibilityScore.FULLY_REVERSIBLE,
            ReversibilityScore.MOSTLY_REVERSIBLE,
        ]:
            advantages.append("Highly reversible - can be undone if needed")
        
        if proposal.estimated_effort == "low":
            advantages.append("Low effort - quick to execute and verify")
        
        if evaluation.complexity_score < 4.0:
            advantages.append("Simple to understand and verify")
        
        if proposal.step_count == 1:
            advantages.append("Single-step plan - minimal complexity")
        
        if evaluation.confidence > 0.80:
            advantages.append("High confidence in this evaluation")
        
        return advantages

    def _generate_disadvantages(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> List[str]:
        """Generate list of disadvantages."""
        disadvantages = []
        
        if evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            disadvantages.append("High risk - potential for significant consequences")
        
        if evaluation.reversibility in [
            ReversibilityScore.BARELY_REVERSIBLE,
            ReversibilityScore.IRREVERSIBLE,
        ]:
            disadvantages.append("Limited reversibility - may be difficult to undo")
        
        if proposal.estimated_effort == "high":
            disadvantages.append("High effort - time-consuming to execute and verify")
        
        if evaluation.complexity_score > 7.0:
            disadvantages.append("Complex plan - harder to verify and understand")
        
        if proposal.step_count > 5:
            disadvantages.append("Many steps - more opportunities for failures")
        
        if evaluation.confidence < 0.60:
            disadvantages.append("Low confidence in this evaluation - many unknowns")
        
        return disadvantages

    def _generate_uncertainties(
        self,
        evaluation: DecisionEvaluation,
    ) -> List[str]:
        """Generate list of uncertainties and unknowns."""
        uncertainties = []
        
        if evaluation.confidence < 1.0:
            uncertainties.append(
                f"Evaluation confidence is {evaluation.confidence:.0%} - "
                f"some aspects were estimated"
            )
        
        if evaluation.estimated_duration_seconds is None:
            uncertainties.append("Actual duration is uncertain")
        
        if len(evaluation.failure_modes) > 0:
            uncertainties.append(
                "Potential failure modes identified (see 'Safety Notes')"
            )
        
        if len(evaluation.risk_factors) > 0:
            uncertainties.append(
                "Risk factors present - external conditions may affect outcome"
            )
        
        return uncertainties

    def _generate_risk_summary(
        self,
        evaluation: DecisionEvaluation,
    ) -> str:
        """Generate one-sentence risk summary."""
        risk_descriptions = {
            RiskLevel.VERY_LOW: "Minimal risk - this is a well-established, safe approach.",
            RiskLevel.LOW: "Low risk - this approach is relatively safe with minor concerns.",
            RiskLevel.MEDIUM: "Moderate risk - this approach has manageable concerns.",
            RiskLevel.HIGH: "High risk - this approach has significant concerns and consequences.",
            RiskLevel.VERY_HIGH: "Very high risk - this approach may cause significant harm.",
        }
        
        return risk_descriptions.get(
            evaluation.risk_level,
            "Risk level unclear - human judgment recommended."
        )

    def _generate_safety_notes(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> List[str]:
        """Generate safety considerations."""
        notes = []
        
        # Add risk factors
        for factor in evaluation.risk_factors:
            notes.append(f"Risk: {factor}")
        
        # Add failure modes
        for mode in evaluation.failure_modes:
            notes.append(f"Potential failure: {mode}")
        
        # Add reversibility information
        if evaluation.reversibility == ReversibilityScore.IRREVERSIBLE:
            notes.append("⚠ This plan may NOT be reversible - verify before executing")
        elif evaluation.reversibility == ReversibilityScore.BARELY_REVERSIBLE:
            notes.append("⚠ Limited reversibility - significant effort to undo")
        
        return notes

    def _generate_recommendations(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> List[str]:
        """Generate specific recommendations for human decision-making."""
        recommendations = []
        
        # Intervention point recommendations
        for point in evaluation.intervention_points:
            recommendations.append(point)
        
        # Additional recommendations based on risk
        if evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append(
                "STRONGLY recommend testing with limited scope first"
            )
        
        if evaluation.reversibility == ReversibilityScore.IRREVERSIBLE:
            recommendations.append(
                "STRONGLY recommend backup/rollback plan before executing"
            )
        
        if proposal.step_count > 5:
            recommendations.append(
                "Consider breaking this plan into smaller, independently-verifiable steps"
            )
        
        return recommendations

    def _generate_when_to_use(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> str:
        """Explain when this plan should be used."""
        if evaluation.risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW]:
            return (
                "Use this plan when you want high confidence and low risk. "
                "Recommended for routine tasks or when safety is paramount."
            )
        elif proposal.estimated_effort == "low":
            return (
                "Use this plan when you want a quick solution with acceptable risk. "
                "Recommended when time is a factor."
            )
        else:
            return (
                "Use this plan when you need completeness and are willing to accept "
                "higher effort and complexity."
            )

    def _generate_when_not_to_use(
        self,
        proposal: DecisionProposal,
        evaluation: DecisionEvaluation,
    ) -> str:
        """Explain when this plan should NOT be used."""
        if evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            return (
                "Avoid this plan if you need high confidence and low risk. "
                "Consider simpler alternatives first."
            )
        elif evaluation.reversibility in [
            ReversibilityScore.BARELY_REVERSIBLE,
            ReversibilityScore.IRREVERSIBLE,
        ]:
            return (
                "Avoid this plan if reversibility is critical. "
                "Cannot easily undo if something goes wrong."
            )
        elif proposal.step_count > 5:
            return (
                "Avoid this plan if you prefer simplicity. "
                "Consider breaking into smaller plans."
            )
        else:
            return (
                "This plan has limited drawbacks - use when appropriate for your goals."
            )

    def explain_proposals(
        self,
        proposals: List[DecisionProposal],
        evaluations: Dict[str, DecisionEvaluation],
    ) -> Tuple[Dict[str, DecisionExplanation], Optional[str]]:
        """
        Generate explanations for multiple proposals.
        
        Args:
            proposals: List of DecisionProposal objects
            evaluations: Dict of proposal_id → DecisionEvaluation
        
        Returns:
            (explanations_dict, error) tuple where keys are proposal_ids
        """
        if not self.enabled:
            return {}, "Decision explainer is disabled"

        explanations = {}
        
        for proposal in proposals:
            evaluation = evaluations.get(proposal.proposal_id)
            if evaluation:
                explanation, error = self.explain_proposal(proposal, evaluation)
                if error is None and explanation:
                    explanations[proposal.proposal_id] = explanation
        
        return explanations, None

    def disable(self):
        """Disable explanation generation (global safety switch)."""
        self.enabled = False

    def enable(self):
        """Enable explanation generation (reversible)."""
        self.enabled = True
