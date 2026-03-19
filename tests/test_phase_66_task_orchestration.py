from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.orchestration.task_orchestrator import TaskOrchestrator
from jessica.reasoning.goal_decomposer import Goal, SubGoal


def test_plan_immutability():

    orchestrator = TaskOrchestrator()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    subgoals = [
        SubGoal("g1-sg1", "g1", "Define scope", 1),
        SubGoal("g1-sg2", "g1", "Draft plan", 2),
    ]

    plan = orchestrator.create_plan(goal, subgoals)

    with pytest.raises(FrozenInstanceError):
        plan.current_index = 1


def test_correct_sequencing_and_completion():

    orchestrator = TaskOrchestrator()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    subgoals = [
        SubGoal("g1-sg1", "g1", "Define scope", 1),
        SubGoal("g1-sg2", "g1", "Draft plan", 2),
    ]

    plan = orchestrator.create_plan(goal, subgoals)

    assert orchestrator.get_current_subgoal(plan).subgoal_id == "g1-sg1"

    plan = orchestrator.advance_plan(plan)
    assert orchestrator.get_current_subgoal(plan).subgoal_id == "g1-sg2"

    plan = orchestrator.advance_plan(plan)
    assert orchestrator.is_complete(plan) is True


def test_deterministic_behavior():

    orchestrator = TaskOrchestrator()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    subgoals = [
        SubGoal("g1-sg1", "g1", "Define scope", 1),
        SubGoal("g1-sg2", "g1", "Draft plan", 2),
    ]

    first = orchestrator.create_plan(goal, subgoals)
    second = orchestrator.create_plan(goal, subgoals)

    assert first == second
