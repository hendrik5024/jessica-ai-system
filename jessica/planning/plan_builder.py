import uuid
from typing import List

from jessica.strategy.strategy_evaluation import StrategyEvaluation
from jessica.planning.plan import Plan, PlanStep


class PlanBuilder:
    def build(self, evaluation: StrategyEvaluation) -> Plan:
        """
        Convert a strategy evaluation into a structured plan.
        Advisory-only. No execution.
        """
        steps: List[PlanStep] = []

        for i, action in enumerate(evaluation.strategy.actions):
            steps.append(
                PlanStep(
                    step_id=i + 1,
                    description=action,
                )
            )

        return Plan(
            plan_id=str(uuid.uuid4()),
            strategy_id=evaluation.strategy.strategy_id,
            steps=steps,
        )
