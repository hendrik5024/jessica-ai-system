"""Phase 11 — Supervised Workflow Engine: immutable workflow structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple, Optional

from jessica.reasoning.planner import TaskPlan as Plan


class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass(frozen=True)
class Workflow:
    workflow_id: str
    name: str
    plans: Tuple[Plan, ...]
    current_step: int
    status: WorkflowStatus
    created_at: datetime


def create_workflow(
    name: str,
    plans: Tuple[Plan, ...],
    workflow_id: Optional[str] = None,
    created_at: Optional[datetime] = None,
) -> Workflow:
    created_at = created_at or datetime.now()
    workflow_id = workflow_id or f"wf_{created_at.strftime('%Y%m%d%H%M%S%f')}"
    return Workflow(
        workflow_id=workflow_id,
        name=name,
        plans=plans,
        current_step=0,
        status=WorkflowStatus.CREATED,
        created_at=created_at,
    )
