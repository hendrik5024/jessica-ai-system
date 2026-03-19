from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from jessica.reasoning.goal_decomposer import Goal, SubGoal


@dataclass(frozen=True)
class TaskPlan:
    plan_id: str
    goal_id: str
    subgoals: Tuple[SubGoal, ...]
    created_at: datetime
    current_index: int


class TaskOrchestrator:

    def create_plan(self, goal: Goal, subgoals: List[SubGoal]) -> TaskPlan:
        self._validate_ordering(goal.goal_id, subgoals)
        return TaskPlan(
            plan_id=f"plan-{goal.goal_id}",
            goal_id=goal.goal_id,
            subgoals=tuple(subgoals),
            created_at=goal.created_at,
            current_index=0,
        )

    def get_current_subgoal(self, plan: TaskPlan) -> Optional[SubGoal]:
        if plan.current_index < 0 or plan.current_index >= len(plan.subgoals):
            return None
        return plan.subgoals[plan.current_index]

    def advance_plan(self, plan: TaskPlan) -> TaskPlan:
        next_index = plan.current_index + 1
        if next_index > len(plan.subgoals):
            next_index = len(plan.subgoals)
        return TaskPlan(
            plan_id=plan.plan_id,
            goal_id=plan.goal_id,
            subgoals=plan.subgoals,
            created_at=plan.created_at,
            current_index=next_index,
        )

    def is_complete(self, plan: TaskPlan) -> bool:
        return plan.current_index >= len(plan.subgoals)

    def _validate_ordering(self, goal_id: str, subgoals: List[SubGoal]) -> None:
        expected = 1
        for subgoal in subgoals:
            if subgoal.parent_goal_id != goal_id:
                raise ValueError("Subgoal parent mismatch")
            if subgoal.sequence_order != expected:
                raise ValueError("Subgoal order invalid")
            expected += 1
