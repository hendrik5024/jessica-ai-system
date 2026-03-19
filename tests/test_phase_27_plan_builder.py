from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine, StrategyEvaluator
from jessica.planning import PlanBuilder


def test_plan_builder_creates_steps():
    g_engine = GoalEngine()
    s_engine = StrategyEngine()
    evaluator = StrategyEvaluator()
    builder = PlanBuilder()

    goal = g_engine.create_goal("Learn advanced reasoning")

    strategy = s_engine.create_strategy([goal])
    evaluation = evaluator.evaluate(strategy)

    plan = builder.build(evaluation)

    assert plan.strategy_id == strategy.strategy_id
    assert len(plan.steps) == len(strategy.actions)
    assert plan.steps[0].step_id == 1
