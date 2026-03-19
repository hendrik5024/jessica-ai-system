from jessica.goals import GoalEngine
from jessica.strategy import StrategyEngine, StrategyEvaluator
from jessica.planning import PlanningMemory


def test_planning_memory_records_history():
    g_engine = GoalEngine()
    s_engine = StrategyEngine()
    evaluator = StrategyEvaluator()
    memory = PlanningMemory()

    goal = g_engine.create_goal("Improve reasoning")

    strategy = s_engine.create_strategy([goal])
    evaluation = evaluator.evaluate(strategy)

    memory.record(evaluation)

    history = memory.get_history()

    assert len(history) == 1
    assert history[0].strategy.strategy_id == strategy.strategy_id
