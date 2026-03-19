from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class StrategyRecord:
    strategy_id: str
    goal_ids: List[str]
    strategy_steps: List[str]

    @property
    def actions(self) -> List[str]:
        return list(self.strategy_steps)
