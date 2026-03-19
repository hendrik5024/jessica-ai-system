from .strategy_record import ReasoningStrategyRecord
from .equilibrium_record import CognitiveEquilibriumRecord


class ReasoningStrategyEngine:

    def recommend(
        self,
        strategy_id: str,
        equilibrium: CognitiveEquilibriumRecord,
    ) -> ReasoningStrategyRecord:

        if equilibrium.equilibrium_state == "UNSTABLE":
            strategy = "INCREASE_VERIFICATION"
            mode = "CAREFUL"
        elif equilibrium.equilibrium_state == "MODERATE":
            strategy = "MAINTAIN_BALANCE"
            mode = "NORMAL"
        else:
            strategy = "OPTIMAL_OPERATION"
            mode = "FULL"

        return ReasoningStrategyRecord(
            strategy_id,
            strategy,
            mode,
            "Strategic reasoning regulation advisory",
        )
