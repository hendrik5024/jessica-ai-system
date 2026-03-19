from jessica.goals import GoalEngine


def test_goal_creation():
    engine = GoalEngine()

    goal = engine.create_goal("Improve reasoning accuracy")

    assert goal.description == "Improve reasoning accuracy"
    assert len(engine.list_goals()) == 1
