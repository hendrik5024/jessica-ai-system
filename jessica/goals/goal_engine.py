from datetime import datetime
from typing import List
import uuid

from .goal_record import GoalRecord


class GoalEngine:
    def __init__(self):
        self._goals: List[GoalRecord] = []

    def create_goal(self, description: str) -> GoalRecord:
        goal = GoalRecord(
            goal_id=str(uuid.uuid4()),
            description=description,
            created_at=datetime.utcnow(),
        )

        self._goals.append(goal)
        return goal

    def list_goals(self):
        return list(self._goals)
