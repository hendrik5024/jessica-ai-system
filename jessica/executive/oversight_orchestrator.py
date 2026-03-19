from .oversight_engine import ExecutiveOversightEngine
from .oversight_record import ExecutiveOversightRecord
from jessica.reasoning.guardrail_reflex_record import GuardrailReflexRecord
from jessica.reasoning.equilibrium_record import CognitiveEquilibriumRecord
from jessica.reasoning.strategy_record import ReasoningStrategyRecord


class ExecutiveOversightOrchestrator:

    def __init__(self):
        self.engine = ExecutiveOversightEngine()

    def generate(
        self,
        oversight_id: str,
        guardrail: GuardrailReflexRecord,
        equilibrium: CognitiveEquilibriumRecord,
        strategy: ReasoningStrategyRecord,
    ) -> ExecutiveOversightRecord:

        return self.engine.generate(
            oversight_id,
            guardrail,
            equilibrium,
            strategy,
        )
