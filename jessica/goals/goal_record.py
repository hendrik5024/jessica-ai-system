from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GoalRecord:
    goal_id: str
    description: str
    created_at: datetime
