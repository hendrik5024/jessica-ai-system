from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine, StrategyEvaluator


def test_strategy_evaluation():
    g_engine = GoalEngine()
    s_engine = StrategyEngine()
    evaluator = StrategyEvaluator()

    g1 = g_engine.create_goal("Improve learning speed")

    strategy = s_engine.create_strategy([g1])

    evaluation = evaluator.evaluate(strategy)

    assert evaluation.strategy_id == strategy.strategy_id
    assert evaluation.estimated_impact > 0
