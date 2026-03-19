"""Phase 10 — Planning Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


@dataclass(frozen=True)
class TaskPlan:
    task: str
    steps: Tuple[str, ...]
    created_at: datetime


class Planner:
    """Deterministic task planner with simple heuristics."""

    def __init__(self) -> None:
        pass

    def create_plan(self, task: str) -> TaskPlan:
        task_text = (task or "").strip()
        lowered = task_text.lower()

        if "send email" in lowered:
            steps = (
                "gather recipient",
                "compose message",
                "confirm approval",
                "send email",
            )
        else:
            steps = (
                "understand task",
                "prepare resources",
                "execute action",
                "verify result",
            )

        return TaskPlan(task=task_text, steps=steps, created_at=datetime.now())

    def create_memory_aware_plan(self, task: str, memory_items: List[str]) -> TaskPlan:
        task_text = (task or "").strip()
        lowered_task = task_text.lower()
        normalized_items = [item.lower() for item in memory_items if item]

        relevant = any(
            token in item
            for item in normalized_items
            for token in lowered_task.split()
            if token
        )

        base_plan = self.create_plan(task_text)
        if relevant:
            steps = ("consult stored knowledge",) + base_plan.steps
        else:
            steps = base_plan.steps

        return TaskPlan(task=task_text, steps=steps, created_at=base_plan.created_at)
