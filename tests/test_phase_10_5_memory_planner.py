from dataclasses import FrozenInstanceError

import pytest

from jessica.reasoning.planner import Planner


def test_memory_aware_step_appears_when_relevant():
    planner = Planner()
    task = "prepare monthly logistics report"
    memory_items = ["monthly warehouse KPI template"]

    plan = planner.create_memory_aware_plan(task, memory_items)

    assert plan.steps[0] == "consult stored knowledge"


def test_deterministic_output():
    planner = Planner()
    task = "prepare monthly logistics report"
    memory_items = ["monthly warehouse KPI template"]

    plan1 = planner.create_memory_aware_plan(task, memory_items)
    plan2 = planner.create_memory_aware_plan(task, memory_items)

    assert plan1.steps == plan2.steps


def test_taskplan_immutable():
    planner = Planner()
    plan = planner.create_memory_aware_plan("send email", ["template"])

    with pytest.raises(FrozenInstanceError):
        plan.task = "new task"


def test_normal_planning_unchanged_when_no_relevant_memory():
    planner = Planner()
    task = "prepare monthly logistics report"
    memory_items = ["unrelated note"]

    plan = planner.create_memory_aware_plan(task, memory_items)

    assert plan.steps == (
        "understand task",
        "prepare resources",
        "execute action",
        "verify result",
    )
