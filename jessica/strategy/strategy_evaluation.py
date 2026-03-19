from dataclasses import dataclass

from .strategy_record import StrategyRecord


@dataclass(frozen=True)
class StrategyEvaluation:
    strategy_id: str
    strategy: StrategyRecord
    estimated_impact: float
    evaluation_notes: str
