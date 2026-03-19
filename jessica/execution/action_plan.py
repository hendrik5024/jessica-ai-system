"""Action Plan data structure for Phase 5.5 - Human-Guided Action Composition.

Represents a human-defined, human-controlled sequence of approved atomic actions.
- No logic, no execution capability
- Immutable data structure
- Tracks current step, status, and completion
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class PlanStatus(Enum):
    """Status of an action plan."""
    PENDING = "pending"  # Created, not yet executing
    EXECUTING = "executing"  # Currently in execution
    PAUSED = "paused"  # Execution paused by human
    COMPLETED = "completed"  # All steps executed successfully
    CANCELLED = "cancelled"  # Cancelled by human
    FAILED = "failed"  # Failed at a step, cannot continue


@dataclass(frozen=True)
class StepResult:
    """Result of executing a single plan step."""
    step_index: int
    pipeline_id: str
    execution_id: Optional[str]  # From ExecutionTracker
    status: str  # "pending" | "executing" | "success" | "failed"
    error_message: Optional[str] = None
    duration_ms: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "step_index": self.step_index,
            "pipeline_id": self.pipeline_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class ActionPlan:
    """
    Human-defined, human-controlled action plan.
    
    Represents an ordered sequence of approved intent pipelines to be executed
    step-by-step under full human control.
    
    Constraints:
    - ZERO autonomy: Cannot execute without explicit human confirmation per step
    - ZERO learning: No adaptive behavior, no modification of pipelines
    - ZERO background execution: All execution explicit and synchronous
    - FULL reversibility: Each step independently recordable and reversible
    - FULL auditability: Complete execution history maintained
    """
    plan_id: str
    pipeline_ids: List[str]  # Approved pipeline IDs from Phase 5.1.5
    
    # Execution state
    current_step_index: int = 0  # Next step to execute
    status: PlanStatus = PlanStatus.PENDING
    
    # Execution history
    completed_steps: List[StepResult] = field(default_factory=list)
    failed_step: Optional[StepResult] = None
    
    # Metadata
    created_timestamp: float = field(default_factory=time.time)
    started_timestamp: Optional[float] = None
    completed_timestamp: Optional[float] = None
    human_label: str = "Untitled Plan"
    
    def __post_init__(self):
        """Validate plan structure after initialization."""
        if not self.pipeline_ids:
            raise ValueError("ActionPlan must contain at least one pipeline_id")
        if not isinstance(self.pipeline_ids, list):
            raise ValueError("pipeline_ids must be a list")
        if self.current_step_index < 0:
            raise ValueError("current_step_index cannot be negative")
        if self.current_step_index > len(self.pipeline_ids):
            raise ValueError("current_step_index cannot exceed number of pipelines")

    @property
    def total_steps(self) -> int:
        """Total number of steps in this plan."""
        return len(self.pipeline_ids)

    @property
    def is_at_end(self) -> bool:
        """Whether current step index is at or past the end."""
        return self.current_step_index >= self.total_steps

    @property
    def next_pipeline_id(self) -> Optional[str]:
        """Get the pipeline ID of the next step, or None if at end."""
        if self.is_at_end:
            return None
        return self.pipeline_ids[self.current_step_index]

    @property
    def progress_percent(self) -> float:
        """Percentage of plan completed (0.0 to 100.0)."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step_index / self.total_steps) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "plan_id": self.plan_id,
            "human_label": self.human_label,
            "pipeline_ids": self.pipeline_ids,
            "current_step_index": self.current_step_index,
            "total_steps": self.total_steps,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "completed_steps": [s.to_dict() for s in self.completed_steps],
            "failed_step": self.failed_step.to_dict() if self.failed_step else None,
            "created_timestamp": self.created_timestamp,
            "started_timestamp": self.started_timestamp,
            "completed_timestamp": self.completed_timestamp,
        }


def create_action_plan(
    pipeline_ids: List[str],
    human_label: str = "Untitled Plan",
    plan_id: Optional[str] = None,
) -> ActionPlan:
    """
    Create a new ActionPlan.
    
    Args:
        pipeline_ids: List of approved pipeline IDs from Phase 5.1.5
        human_label: Human-readable label for this plan
        plan_id: Optional custom plan ID (default: auto-generated UUID)
    
    Returns:
        New ActionPlan instance
    
    Raises:
        ValueError: If pipeline_ids is empty or invalid
    """
    if not plan_id:
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
    
    return ActionPlan(
        plan_id=plan_id,
        pipeline_ids=pipeline_ids,
        human_label=human_label,
    )
