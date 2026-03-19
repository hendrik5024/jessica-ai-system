from .oversight_record import ExecutiveOversightRecord
from jessica.reasoning.guardrail_reflex_record import GuardrailReflexRecord
from jessica.reasoning.equilibrium_record import CognitiveEquilibriumRecord
from jessica.reasoning.strategy_record import ReasoningStrategyRecord


class ExecutiveOversightEngine:

    def generate(
        self,
        oversight_id: str,
        guardrail: GuardrailReflexRecord,
        equilibrium: CognitiveEquilibriumRecord,
        strategy: ReasoningStrategyRecord,
    ) -> ExecutiveOversightRecord:

        return ExecutiveOversightRecord(
            oversight_id,
            guardrail.reflex_state,
            equilibrium.equilibrium_state,
            strategy.recommended_strategy,
            "Executive cognitive oversight advisory",
        )
