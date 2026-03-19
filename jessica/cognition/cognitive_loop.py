from jessica.planning import (
    PlanBuilder,
    PlanEvaluator,
    PlanPerformanceMemory,
)
from jessica.strategy import StrategyEngine, StrategyEvaluator


class CognitiveLoop:
    """
    Deterministic cognition pipeline for Jessica.
    Produces reasoning → planning → evaluation outputs.
    Advisory only.
    """

    def __init__(self):

        self.strategy_engine = StrategyEngine()
        self.strategy_evaluator = StrategyEvaluator()
        self.plan_builder = PlanBuilder()
        self.plan_evaluator = PlanEvaluator()
        self.performance_memory = PlanPerformanceMemory()

    def run(self, goal):

        strategy = self.strategy_engine.create_strategy([goal])

        evaluation = self.strategy_evaluator.evaluate(strategy)

        plan = self.plan_builder.build(evaluation)

        plan_evaluation = self.plan_evaluator.evaluate(plan)

        self.performance_memory.record(goal.goal_id, plan_evaluation)

        best = self.performance_memory.best_plan(goal.goal_id)

        return {
            "strategy": strategy,
            "plan": plan,
            "evaluation": plan_evaluation,
            "best_plan": best,
        }
