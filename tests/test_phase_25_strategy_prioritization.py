from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine, StrategyEvaluator, StrategyPrioritizer


def test_strategy_prioritization():
    g_engine = GoalEngine()
    s_engine = StrategyEngine()
    evaluator = StrategyEvaluator()
    prioritizer = StrategyPrioritizer()

    g1 = g_engine.create_goal("Improve reasoning")
    g2 = g_engine.create_goal("Improve memory")

    s1 = s_engine.create_strategy([g1])
    s2 = s_engine.create_strategy([g1, g2])

    e1 = evaluator.evaluate(s1)
    e2 = evaluator.evaluate(s2)

    ranked = prioritizer.prioritize([e1, e2])

    assert ranked[0].estimated_impact >= ranked[1].estimated_impact
