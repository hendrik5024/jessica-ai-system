"""
Self-Directed Evolution Engine

Jessica decides what to learn, why it matters, and when to upgrade herself
within hard constraints:
- Human safety
- Long-term trust
- Alignment with user
- No irreversible actions without approval

Author: Jessica AI System
Date: February 3, 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EvolutionDecision:
    target_skill: str
    rationale: str
    constraints_passed: bool
    violated_constraints: List[str]
    requires_approval: bool
    timestamp: str


class SelfDirectedEvolutionEngine:
    """Selects learning targets and enforces hard constraints."""

    def __init__(self) -> None:
        self.hard_constraints = [
            "human_safety",
            "long_term_trust",
            "user_alignment",
            "irreversible_requires_approval",
        ]

    def choose_learning_target(
        self,
        *,
        candidates: List[Dict[str, Any]],
        user_alignment_score: Optional[float] = None,
        allow_irreversible: bool = False,
    ) -> EvolutionDecision:
        if not candidates:
            return EvolutionDecision(
                target_skill="",
                rationale="No candidates available",
                constraints_passed=False,
                violated_constraints=["no_candidates"],
                requires_approval=False,
                timestamp=datetime.now().isoformat(),
            )

        ranked = sorted(
            candidates,
            key=lambda c: (-(c.get("severity", 0) or 0), -(c.get("failures", 0) or 0)),
        )
        target = ranked[0]
        target_skill = target.get("skill", "")
        rationale = (
            f"Selected '{target_skill}' due to high failure impact "
            f"(severity={target.get('avg_severity')}, failures={target.get('failures')})."
        )

        requires_approval = self._is_irreversible(target_skill)
        violated = self._check_constraints(
            target_skill=target_skill,
            user_alignment_score=user_alignment_score,
            requires_approval=requires_approval,
            allow_irreversible=allow_irreversible,
        )

        return EvolutionDecision(
            target_skill=target_skill,
            rationale=rationale,
            constraints_passed=not violated,
            violated_constraints=violated,
            requires_approval=requires_approval,
            timestamp=datetime.now().isoformat(),
        )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    def _check_constraints(
        self,
        *,
        target_skill: str,
        user_alignment_score: Optional[float],
        requires_approval: bool,
        allow_irreversible: bool,
    ) -> List[str]:
        violated: List[str] = []

        if user_alignment_score is not None and user_alignment_score < 0.45:
            violated.append("user_alignment")

        if "safety" in target_skill or "harm" in target_skill:
            violated.append("human_safety")

        if "trust" in target_skill and "degrade" in target_skill:
            violated.append("long_term_trust")

        if requires_approval and not allow_irreversible:
            violated.append("irreversible_requires_approval")

        return violated

    def _is_irreversible(self, target_skill: str) -> bool:
        tokens = {"core", "model", "self", "autonomous", "safety"}
        return any(tok in target_skill.lower() for tok in tokens)
