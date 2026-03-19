"""Phase 11 — Supervised Workflow Engine: orchestrator."""

from __future__ import annotations

from typing import List, Tuple

from jessica.reasoning.planner import Planner
from jessica.workflow import Workflow, create_workflow
from jessica.workflow_executor import (
    ExecutionOutcome,
    start_workflow,
    execute_next_step,
    pause_workflow,
    resume_workflow,
    complete_workflow,
)
from jessica.workflow_registry import WorkflowRegistry


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.registry = WorkflowRegistry()
        self.executor = {
            "start": start_workflow,
            "step": execute_next_step,
            "pause": pause_workflow,
            "resume": resume_workflow,
            "complete": complete_workflow,
        }
        self.planner = Planner()

    def create_workflow(self, name: str, tasks: List[str]) -> Workflow:
        plans = tuple(self.planner.create_plan(task) for task in tasks)
        workflow = create_workflow(name=name, plans=plans)
        self.registry.register_workflow(workflow)
        return workflow

    def start(self, workflow: Workflow) -> Workflow:
        return self.executor["start"](workflow)

    def step(self, workflow: Workflow, approved: bool) -> Tuple[Workflow, ExecutionOutcome]:
        return self.executor["step"](workflow, approved)

    def pause(self, workflow: Workflow) -> Workflow:
        return self.executor["pause"](workflow)

    def resume(self, workflow: Workflow) -> Workflow:
        return self.executor["resume"](workflow)

    def complete(self, workflow: Workflow) -> Workflow:
        return self.executor["complete"](workflow)
