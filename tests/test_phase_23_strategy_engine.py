from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine


def test_strategy_creation():
    goal_engine = GoalEngine()
    strategy_engine = StrategyEngine()

    g1 = goal_engine.create_goal("Improve reasoning")
    g2 = goal_engine.create_goal("Improve knowledge")

    strategy = strategy_engine.create_strategy([g1, g2])

    assert len(strategy.goal_ids) == 2
    assert len(strategy.strategy_steps) == 2
