from dataclasses import dataclass
from typing import List, Tuple

from jessica.reasoning.goal_decomposer import Goal


@dataclass(frozen=True)
class PlanCandidate:
    plan_id: str
    estimated_success: float
    estimated_cost: float
    risk_score: float
    description: str


@dataclass(frozen=True)
class PlanEvaluation:
    selected_plan_id: str
    score: float
    evaluation_reason: str


class MetaPlanner:

    def generate_candidates(self, goal: Goal) -> List[PlanCandidate]:
        base = goal.description.strip() or "Goal"
        return [
            PlanCandidate(
                plan_id=f"{goal.goal_id}-plan-1",
                estimated_success=0.8,
                estimated_cost=0.4,
                risk_score=0.2,
                description=f"Conservative plan for {base}",
            ),
            PlanCandidate(
                plan_id=f"{goal.goal_id}-plan-2",
                estimated_success=0.6,
                estimated_cost=0.2,
                risk_score=0.3,
                description=f"Lean plan for {base}",
            ),
            PlanCandidate(
                plan_id=f"{goal.goal_id}-plan-3",
                estimated_success=0.9,
                estimated_cost=0.7,
                risk_score=0.4,
                description=f"Aggressive plan for {base}",
            ),
        ]

    def evaluate_candidates(self, candidates: List[PlanCandidate]) -> PlanEvaluation:
        best = None
        best_score = None

        for candidate in candidates:
            score = self._score_candidate(candidate)
            if best is None or score > best_score:
                best = candidate
                best_score = score

        return PlanEvaluation(
            selected_plan_id=best.plan_id,
            score=best_score,
            evaluation_reason="Selected highest scoring plan.",
        )

    def select_plan(self, goal: Goal) -> Tuple[PlanCandidate, PlanEvaluation]:
        candidates = self.generate_candidates(goal)
        evaluation = self.evaluate_candidates(candidates)
        selected = next(c for c in candidates if c.plan_id == evaluation.selected_plan_id)
        return selected, evaluation

    def _score_candidate(self, candidate: PlanCandidate) -> float:
        return (
            (candidate.estimated_success * 0.6)
            - (candidate.risk_score * 0.3)
            - (candidate.estimated_cost * 0.1)
        )
