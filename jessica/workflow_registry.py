"""Phase 11 — Supervised Workflow Engine: append-only registry."""

from __future__ import annotations

from typing import Dict, List

from jessica.workflow import Workflow, WorkflowStatus


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: Dict[str, Workflow] = {}
        self._order: List[str] = []

    def register_workflow(self, workflow: Workflow) -> None:
        if workflow.workflow_id in self._workflows:
            raise ValueError("Workflow already registered")
        self._workflows[workflow.workflow_id] = workflow
        self._order.append(workflow.workflow_id)

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def list_active_workflows(self) -> List[Workflow]:
        active = []
        for workflow_id in self._order:
            wf = self._workflows[workflow_id]
            if wf.status in (WorkflowStatus.RUNNING, WorkflowStatus.PAUSED):
                active.append(wf)
        return active
