from typing import List

from jessica.planning.plan import Plan
from jessica.planning.plan_evaluation import PlanEvaluation


class PlanEvaluator:

    def evaluate(self, plan: Plan) -> PlanEvaluation:
        """
        Deterministic scoring based on number of steps.
        Fewer steps = higher score.
        """

        score = 1.0 / (1 + len(plan.steps))

        reasoning = f"Plan contains {len(plan.steps)} steps."

        return PlanEvaluation(
            plan_id=plan.plan_id,
            score=score,
            reasoning=reasoning
        )

    def rank(self, plans: List[Plan]) -> List[PlanEvaluation]:

        evaluations = [self.evaluate(p) for p in plans]

        return sorted(
            evaluations,
            key=lambda e: e.score,
            reverse=True
        )
