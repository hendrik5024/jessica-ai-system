from .strategy_engine import ReasoningStrategyEngine
from .strategy_record import ReasoningStrategyRecord
from .equilibrium_record import CognitiveEquilibriumRecord


class ReasoningStrategyOrchestrator:

    def __init__(self):
        self.engine = ReasoningStrategyEngine()

    def recommend(
        self,
        strategy_id: str,
        equilibrium: CognitiveEquilibriumRecord,
    ) -> ReasoningStrategyRecord:

        return self.engine.recommend(strategy_id, equilibrium)
