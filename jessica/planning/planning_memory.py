from typing import List
from jessica.strategy.strategy_evaluation import StrategyEvaluation


class PlanningMemory:
    def __init__(self):
        self.history: List[StrategyEvaluation] = []

    def record(self, evaluation: StrategyEvaluation):
        self.history.append(evaluation)

    def get_history(self) -> List[StrategyEvaluation]:
        return list(self.history)
