from jessica.cognition import CognitiveLoop
from jessica.goals import GoalEngine


def test_cognitive_loop_runs():

    loop = CognitiveLoop()
    g_engine = GoalEngine()

    goal = g_engine.create_goal("Optimize warehouse workflow")

    result = loop.run(goal)

    assert "strategy" in result
    assert "plan" in result
    assert "evaluation" in result
    assert "best_plan" in result
