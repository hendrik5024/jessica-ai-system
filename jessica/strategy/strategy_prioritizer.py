from typing import List
from .strategy_evaluation import StrategyEvaluation


class StrategyPrioritizer:
    def prioritize(self, evaluations: List[StrategyEvaluation]) -> List[StrategyEvaluation]:
        return sorted(evaluations, key=lambda e: e.estimated_impact, reverse=True)
