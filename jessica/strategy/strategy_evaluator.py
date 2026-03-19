from .strategy_record import StrategyRecord
from .strategy_evaluation import StrategyEvaluation


class StrategyEvaluator:
    def evaluate(self, strategy: StrategyRecord) -> StrategyEvaluation:
        impact = len(strategy.strategy_steps) * 0.5

        return StrategyEvaluation(
            strategy_id=strategy.strategy_id,
            strategy=strategy,
            estimated_impact=impact,
            evaluation_notes="Impact estimated from strategy complexity.",
        )
