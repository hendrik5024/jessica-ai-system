from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.reasoning.planner import TaskPlan
from jessica.workflow import Workflow, WorkflowStatus, create_workflow
from jessica.workflow_executor import (
    start_workflow,
    execute_next_step,
    pause_workflow,
    resume_workflow,
)
from jessica.workflow_registry import WorkflowRegistry
from jessica.workflow_orchestrator import WorkflowOrchestrator


def _plan(task: str, steps: tuple[str, ...]) -> TaskPlan:
    return TaskPlan(task=task, steps=steps, created_at=datetime(2026, 2, 9))


def _workflow() -> Workflow:
    plans = (
        _plan("task a", ("step 1", "step 2")),
        _plan("task b", ("step 3",)),
    )
    return create_workflow("wf", plans, workflow_id="wf_1", created_at=datetime(2026, 2, 9))


def test_workflow_immutable():
    wf = _workflow()
    with pytest.raises(FrozenInstanceError):
        wf.name = "new"


def test_start_workflow_sets_running():
    wf = _workflow()
    started = start_workflow(wf)
    assert started.status == WorkflowStatus.RUNNING


def test_start_workflow_idempotent():
    wf = start_workflow(_workflow())
    started_again = start_workflow(wf)
    assert started_again.status == WorkflowStatus.RUNNING


def test_execute_next_step_requires_approval():
    wf = start_workflow(_workflow())
    with pytest.raises(PermissionError):
        execute_next_step(wf, approved=False)


def test_execute_next_step_advances_one_step():
    wf = start_workflow(_workflow())
    updated, outcome = execute_next_step(wf, approved=True)
    assert updated.current_step == 1
    assert outcome.step == "step 1"


def test_execute_next_step_runs_single_step_only():
    wf = start_workflow(_workflow())
    updated, _ = execute_next_step(wf, approved=True)
    assert updated.current_step == 1


def test_execute_next_step_completes_when_last():
    wf = start_workflow(_workflow())
    wf, _ = execute_next_step(wf, approved=True)
    wf, _ = execute_next_step(wf, approved=True)
    wf, _ = execute_next_step(wf, approved=True)
    assert wf.status == WorkflowStatus.COMPLETED


def test_pause_workflow():
    wf = start_workflow(_workflow())
    paused = pause_workflow(wf)
    assert paused.status == WorkflowStatus.PAUSED


def test_pause_does_not_change_non_running():
    wf = _workflow()
    paused = pause_workflow(wf)
    assert paused.status == WorkflowStatus.CREATED


def test_resume_workflow():
    wf = start_workflow(_workflow())
    paused = pause_workflow(wf)
    resumed = resume_workflow(paused)
    assert resumed.status == WorkflowStatus.RUNNING


def test_resume_no_effect_if_not_paused():
    wf = _workflow()
    resumed = resume_workflow(wf)
    assert resumed.status == WorkflowStatus.CREATED


def test_registry_append_only():
    registry = WorkflowRegistry()
    wf = _workflow()
    registry.register_workflow(wf)
    with pytest.raises(ValueError):
        registry.register_workflow(wf)


def test_registry_get_workflow():
    registry = WorkflowRegistry()
    wf = _workflow()
    registry.register_workflow(wf)
    assert registry.get_workflow("wf_1") == wf


def test_registry_list_active_workflows():
    registry = WorkflowRegistry()
    wf = start_workflow(_workflow())
    registry.register_workflow(wf)
    assert registry.list_active_workflows() == [wf]


def test_registry_list_active_excludes_completed():
    registry = WorkflowRegistry()
    wf = start_workflow(_workflow())
    wf, _ = execute_next_step(wf, approved=True)
    wf, _ = execute_next_step(wf, approved=True)
    wf, _ = execute_next_step(wf, approved=True)
    registry.register_workflow(wf)
    assert registry.list_active_workflows() == []


def test_orchestrator_creates_workflow():
    orchestrator = WorkflowOrchestrator()
    wf = orchestrator.create_workflow("test", ["send email"])
    assert wf.name == "test"
    assert orchestrator.registry.get_workflow(wf.workflow_id) == wf


def test_orchestrator_start_and_step():
    orchestrator = WorkflowOrchestrator()
    wf = orchestrator.create_workflow("test", ["send email"])
    wf = orchestrator.start(wf)
    wf, _ = orchestrator.step(wf, approved=True)
    assert wf.current_step == 1


def test_deterministic_step_order():
    wf = start_workflow(_workflow())
    wf1, outcome1 = execute_next_step(wf, approved=True)
    wf2, outcome2 = execute_next_step(wf, approved=True)
    assert outcome1.step == outcome2.step


def test_workflow_created_status():
    wf = _workflow()
    assert wf.status == WorkflowStatus.CREATED


def test_workflow_current_step_starts_zero():
    wf = _workflow()
    assert wf.current_step == 0


def test_orchestrator_pause_resume():
    orchestrator = WorkflowOrchestrator()
    wf = orchestrator.create_workflow("test", ["send email"])
    wf = orchestrator.start(wf)
    wf = orchestrator.pause(wf)
    assert wf.status == WorkflowStatus.PAUSED
    wf = orchestrator.resume(wf)
    assert wf.status == WorkflowStatus.RUNNING


def test_executor_requires_running_state():
    wf = _workflow()
    with pytest.raises(ValueError):
        execute_next_step(wf, approved=True)
