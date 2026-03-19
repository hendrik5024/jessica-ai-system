from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Goal:
    goal_id: str
    description: str
    priority: int
    created_at: datetime


@dataclass(frozen=True)
class SubGoal:
    subgoal_id: str
    parent_goal_id: str
    description: str
    sequence_order: int


class GoalDecomposer:

    def decompose_goal(self, goal: Goal) -> List[SubGoal]:
        """
        Deterministic rule-based decomposition.
        """
        parts = self._split_description(goal.description)
        if not parts:
            parts = [
                f"Define scope for: {goal.description}",
                f"Outline steps for: {goal.description}",
                f"Review plan for: {goal.description}",
            ]

        subgoals: List[SubGoal] = []
        for index, part in enumerate(parts, start=1):
            subgoals.append(
                SubGoal(
                    subgoal_id=f"{goal.goal_id}-sg{index}",
                    parent_goal_id=goal.goal_id,
                    description=part,
                    sequence_order=index,
                )
            )

        return subgoals

    def validate_subgoals(self, subgoals: List[SubGoal]) -> bool:
        if not subgoals:
            return False

        parent_id = subgoals[0].parent_goal_id
        expected_order = 1

        for subgoal in subgoals:
            if subgoal.parent_goal_id != parent_id:
                return False
            if subgoal.sequence_order != expected_order:
                return False
            expected_order += 1

        return True

    def _split_description(self, description: str) -> List[str]:
        cleaned = description.strip()
        if not cleaned:
            return []

        for delimiter in [" and ", ","]:
            if delimiter in cleaned:
                parts = [part.strip() for part in cleaned.split(delimiter)]
                return [part for part in parts if part]

        return []
