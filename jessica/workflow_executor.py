"""Phase 11 — Supervised Workflow Engine: deterministic executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple

from jessica.workflow import Workflow, WorkflowStatus


@dataclass(frozen=True)
class ExecutionOutcome:
    workflow_id: str
    step_index: int
    step: str
    status: str
    approved: bool
    created_at: datetime


def _flatten_steps(plans: Tuple) -> List[Tuple[str, str]]:
    flattened: List[Tuple[str, str]] = []
    for plan in plans:
        for step in plan.steps:
            flattened.append((plan.task, step))
    return flattened


def start_workflow(workflow: Workflow) -> Workflow:
    if workflow.status != WorkflowStatus.CREATED:
        return workflow
    return Workflow(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        plans=workflow.plans,
        current_step=workflow.current_step,
        status=WorkflowStatus.RUNNING,
        created_at=workflow.created_at,
    )


def execute_next_step(workflow: Workflow, approved: bool) -> Tuple[Workflow, ExecutionOutcome]:
    if not approved:
        raise PermissionError("Human approval required for workflow step")
    if workflow.status not in (WorkflowStatus.RUNNING,):
        raise ValueError("Workflow is not running")

    flattened = _flatten_steps(workflow.plans)
    if workflow.current_step >= len(flattened):
        completed = complete_workflow(workflow)
        outcome = ExecutionOutcome(
            workflow_id=workflow.workflow_id,
            step_index=workflow.current_step,
            step="",
            status="completed",
            approved=True,
            created_at=datetime.now(),
        )
        return completed, outcome

    _, step = flattened[workflow.current_step]
    next_step = workflow.current_step + 1
    status = WorkflowStatus.RUNNING
    if next_step >= len(flattened):
        status = WorkflowStatus.COMPLETED

    updated = Workflow(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        plans=workflow.plans,
        current_step=next_step,
        status=status,
        created_at=workflow.created_at,
    )
    outcome = ExecutionOutcome(
        workflow_id=workflow.workflow_id,
        step_index=workflow.current_step,
        step=step,
        status="executed",
        approved=True,
        created_at=datetime.now(),
    )
    return updated, outcome


def pause_workflow(workflow: Workflow) -> Workflow:
    if workflow.status != WorkflowStatus.RUNNING:
        return workflow
    return Workflow(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        plans=workflow.plans,
        current_step=workflow.current_step,
        status=WorkflowStatus.PAUSED,
        created_at=workflow.created_at,
    )


def resume_workflow(workflow: Workflow) -> Workflow:
    if workflow.status != WorkflowStatus.PAUSED:
        return workflow
    return Workflow(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        plans=workflow.plans,
        current_step=workflow.current_step,
        status=WorkflowStatus.RUNNING,
        created_at=workflow.created_at,
    )


def complete_workflow(workflow: Workflow) -> Workflow:
    return Workflow(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        plans=workflow.plans,
        current_step=workflow.current_step,
        status=WorkflowStatus.COMPLETED,
        created_at=workflow.created_at,
    )
