from dataclasses import FrozenInstanceError
from datetime import datetime
import inspect

import pytest

from jessica.reasoning.goal_decomposer import Goal, GoalDecomposer, SubGoal


def test_goal_dataclasses_frozen():

    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    subgoal = SubGoal("sg1", "g1", "Define scope", 1)

    with pytest.raises(FrozenInstanceError):
        goal.description = "Change"

    with pytest.raises(FrozenInstanceError):
        subgoal.description = "Change"


def test_deterministic_decomposition():

    decomposer = GoalDecomposer()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))

    first = decomposer.decompose_goal(goal)
    second = decomposer.decompose_goal(goal)

    assert first == second


def test_ordering_correctness():

    decomposer = GoalDecomposer()
    goal = Goal("g1", "Design process and document steps", 1, datetime(2026, 2, 10, 12, 0, 0))

    subgoals = decomposer.decompose_goal(goal)

    assert subgoals[0].sequence_order == 1
    assert subgoals[1].sequence_order == 2
    assert subgoals[0].parent_goal_id == "g1"
    assert decomposer.validate_subgoals(subgoals) is True


def test_no_execution_methods_present():

    decomposer = GoalDecomposer()

    for name, _ in inspect.getmembers(decomposer, predicate=inspect.ismethod):
        assert "execute" not in name.lower()
