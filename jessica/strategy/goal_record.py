from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class GoalRecord:
    goal_id: str
    description: str
    required_resources: Tuple[str, ...]
    priority_level: int
    created_at: datetime
