from dataclasses import FrozenInstanceError

import pytest

from jessica.reasoning.planner import Planner, TaskPlan


def test_deterministic_output():
    planner = Planner()
    plan1 = planner.create_plan("send email to client")
    plan2 = planner.create_plan("send email to client")

    assert plan1.steps == plan2.steps


def test_taskplan_immutable():
    planner = Planner()
    plan = planner.create_plan("send email to client")

    with pytest.raises(FrozenInstanceError):
        plan.task = "new task"


def test_steps_always_produced():
    planner = Planner()
    plan = planner.create_plan("")

    assert isinstance(plan, TaskPlan)
    assert len(plan.steps) > 0


def test_known_task_expected_steps():
    planner = Planner()
    plan = planner.create_plan("Please send email to team")

    assert plan.steps == (
        "gather recipient",
        "compose message",
        "confirm approval",
        "send email",
    )
