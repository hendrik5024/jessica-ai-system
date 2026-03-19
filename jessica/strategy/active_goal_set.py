from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from .goal_record import GoalRecord


@dataclass(frozen=True)
class ActiveGoalSet:
    set_id: str
    active_goals: Tuple[GoalRecord, ...]
    timestamp: datetime
