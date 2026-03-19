import uuid
from typing import List

from .strategy_record import StrategyRecord
from jessica.goals.goal_record import GoalRecord


class StrategyEngine:
    def create_strategy(self, goals: List[GoalRecord]) -> StrategyRecord:
        steps = [f"Strategic step aligned to goal: {g.description}" for g in goals]

        return StrategyRecord(
            strategy_id=str(uuid.uuid4()),
            goal_ids=[g.goal_id for g in goals],
            strategy_steps=steps,
        )
