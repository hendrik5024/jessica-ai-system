from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine, StrategyEvaluator
from jessica.planning import PlanBuilder, PlanEvaluator


def test_plan_evaluation():

    g_engine = GoalEngine()
    s_engine = StrategyEngine()
    evaluator = StrategyEvaluator()
    builder = PlanBuilder()
    plan_eval = PlanEvaluator()

    goal = g_engine.create_goal("Build AI systems")

    strategy = s_engine.create_strategy([goal])
    strat_eval = evaluator.evaluate(strategy)

    plan = builder.build(strat_eval)

    evaluation = plan_eval.evaluate(plan)

    assert evaluation.plan_id == plan.plan_id
    assert evaluation.score > 0
