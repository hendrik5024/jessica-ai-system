"""Phase 6: Human-Supervised Decision Support - Data Structures.

Immutable, audit-trail only data structures for decision proposals, evaluations,
and explanations. NO mutable state, NO execution hooks, NO learning.

All decision artifacts are read-only and advisory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class RiskLevel(Enum):
    """Risk assessment for a proposed plan."""
    VERY_LOW = "very_low"      # Minimal risk, high reversibility
    LOW = "low"                 # Low risk, mostly reversible
    MEDIUM = "medium"           # Moderate risk, partially reversible
    HIGH = "high"               # High risk, limited reversibility
    VERY_HIGH = "very_high"     # Extreme risk, minimal reversibility


class ReversibilityScore(Enum):
    """How easily a plan can be undone."""
    FULLY_REVERSIBLE = "fully_reversible"      # Each step can be undone
    MOSTLY_REVERSIBLE = "mostly_reversible"    # Most steps reversible
    PARTIALLY_REVERSIBLE = "partially_reversible"  # Some steps reversible
    BARELY_REVERSIBLE = "barely_reversible"    # Few reversible steps
    IRREVERSIBLE = "irreversible"              # Cannot be undone


@dataclass(frozen=True)
class DecisionProposal:
    """A single candidate ActionPlan proposal from Phase 6 analysis."""
    
    proposal_id: str
    action_plan_id: str  # References Phase 5.5 ActionPlan
    description: str  # Human-readable description of the plan
    step_count: int  # Number of steps in this plan
    estimated_effort: str  # low|medium|high
    rationale: str  # Why this plan was proposed
    
    created_timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "proposal_id": self.proposal_id,
            "action_plan_id": self.action_plan_id,
            "description": self.description,
            "step_count": self.step_count,
            "estimated_effort": self.estimated_effort,
            "rationale": self.rationale,
            "created_timestamp": self.created_timestamp,
        }


@dataclass(frozen=True)
class DecisionEvaluation:
    """Evaluation metrics for a proposed plan (READ-ONLY)."""
    
    proposal_id: str
    risk_level: RiskLevel
    reversibility: ReversibilityScore
    complexity_score: float  # 0.0 to 10.0
    estimated_duration_seconds: Optional[float]  # None if unknown
    confidence: float  # 0.0 to 1.0 (0=very uncertain, 1=very certain)
    
    # Risk factors identified
    risk_factors: List[str] = field(default_factory=list)
    
    # Potential failure modes
    failure_modes: List[str] = field(default_factory=list)
    
    # Opportunities for human intervention
    intervention_points: List[str] = field(default_factory=list)
    
    evaluated_timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "proposal_id": self.proposal_id,
            "risk_level": self.risk_level.value,
            "reversibility": self.reversibility.value,
            "complexity_score": self.complexity_score,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "confidence": self.confidence,
            "risk_factors": self.risk_factors,
            "failure_modes": self.failure_modes,
            "intervention_points": self.intervention_points,
            "evaluated_timestamp": self.evaluated_timestamp,
        }


@dataclass(frozen=True)
class DecisionExplanation:
    """Human-readable explanation of a proposal + evaluation."""
    
    proposal_id: str
    summary: str  # One-sentence summary
    
    # Detailed explanation sections
    what_it_does: str  # What the plan accomplishes
    how_it_works: str  # Step-by-step breakdown
    why_proposed: str  # Rationale for this proposal
    
    # Trade-offs and uncertainties
    advantages: List[str]  # Pros of this plan
    disadvantages: List[str]  # Cons of this plan
    uncertainties: List[str]  # What we're not sure about
    
    # Risk and safety information
    risk_summary: str  # One-sentence risk summary
    safety_notes: List[str]  # Important safety considerations
    
    # Recommendations
    recommendations: List[str]  # Suggested actions/considerations
    when_to_use: str  # Best use case for this plan
    when_not_to_use: str  # When to avoid this plan
    
    created_timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "proposal_id": self.proposal_id,
            "summary": self.summary,
            "what_it_does": self.what_it_does,
            "how_it_works": self.how_it_works,
            "why_proposed": self.why_proposed,
            "advantages": self.advantages,
            "disadvantages": self.disadvantages,
            "uncertainties": self.uncertainties,
            "risk_summary": self.risk_summary,
            "safety_notes": self.safety_notes,
            "recommendations": self.recommendations,
            "when_to_use": self.when_to_use,
            "when_not_to_use": self.when_not_to_use,
            "created_timestamp": self.created_timestamp,
        }


@dataclass(frozen=True)
class DecisionBundle:
    """Complete decision support output: proposals + evaluations + explanations."""
    
    bundle_id: str
    goal_description: str  # Human's original goal
    
    # All proposals with evaluations
    proposals: List[DecisionProposal] = field(default_factory=list)
    evaluations: Dict[str, DecisionEvaluation] = field(default_factory=dict)
    explanations: Dict[str, DecisionExplanation] = field(default_factory=dict)
    
    # Recommendation
    recommended_proposal_id: Optional[str] = None  # Suggested plan (if any)
    recommendation_rationale: Optional[str] = None  # Why recommended
    
    # Clarifying questions asked before analysis
    clarifying_questions: List[str] = field(default_factory=list)
    
    # Analysis notes
    analysis_notes: str = ""  # Additional context
    
    created_timestamp: float = field(default_factory=time.time)
    
    @property
    def proposal_count(self) -> int:
        """Number of proposals in this bundle."""
        return len(self.proposals)
    
    @property
    def sorted_proposals_by_risk(self) -> List[DecisionProposal]:
        """Get proposals sorted by risk level (low to high)."""
        risk_order = {
            RiskLevel.VERY_LOW: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.VERY_HIGH: 4,
        }
        return sorted(
            self.proposals,
            key=lambda p: risk_order.get(
                self.evaluations.get(p.proposal_id, DecisionEvaluation(
                    proposal_id=p.proposal_id,
                    risk_level=RiskLevel.MEDIUM,
                    reversibility=ReversibilityScore.PARTIALLY_REVERSIBLE,
                    complexity_score=5.0,
                    confidence=0.5,
                )).risk_level,
                2
            )
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "bundle_id": self.bundle_id,
            "goal_description": self.goal_description,
            "proposal_count": self.proposal_count,
            "proposals": [p.to_dict() for p in self.proposals],
            "evaluations": {pid: e.to_dict() for pid, e in self.evaluations.items()},
            "explanations": {pid: e.to_dict() for pid, e in self.explanations.items()},
            "recommended_proposal_id": self.recommended_proposal_id,
            "recommendation_rationale": self.recommendation_rationale,
            "clarifying_questions": self.clarifying_questions,
            "analysis_notes": self.analysis_notes,
            "created_timestamp": self.created_timestamp,
        }


def create_decision_bundle(
    goal_description: str,
    bundle_id: Optional[str] = None,
) -> DecisionBundle:
    """
    Create a new DecisionBundle to hold decision support analysis.
    
    Args:
        goal_description: Human's stated goal or request
        bundle_id: Optional custom bundle ID (default: auto-generated)
    
    Returns:
        Empty DecisionBundle ready for proposals/evaluations
    """
    if not bundle_id:
        bundle_id = f"bundle_{uuid.uuid4().hex[:12]}"
    
    return DecisionBundle(
        bundle_id=bundle_id,
        goal_description=goal_description,
    )
