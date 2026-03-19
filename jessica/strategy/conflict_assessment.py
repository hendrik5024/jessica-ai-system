from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ConflictAssessment:
    conflict_detected: bool
    conflicting_goal_pairs: Tuple[Tuple[str, str], ...]
    explanation: str
    assessed_at: datetime
