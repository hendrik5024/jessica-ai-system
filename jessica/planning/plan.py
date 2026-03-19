from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PlanStep:
    step_id: int
    description: str


@dataclass(frozen=True)
class Plan:
    plan_id: str
    strategy_id: str
    steps: List[PlanStep]
