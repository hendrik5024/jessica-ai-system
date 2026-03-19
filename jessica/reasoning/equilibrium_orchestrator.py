from .equilibrium_engine import CognitiveEquilibriumEngine
from .equilibrium_record import CognitiveEquilibriumRecord
from .guardrail_record import GuardrailRecord
from .metacognition_record import MetaCognitionRecord


class CognitiveEquilibriumOrchestrator:

    def __init__(self):
        self.engine = CognitiveEquilibriumEngine()

    def evaluate(
        self,
        equilibrium_id: str,
        meta: MetaCognitionRecord,
        guard: GuardrailRecord,
    ) -> CognitiveEquilibriumRecord:

        return self.engine.evaluate(equilibrium_id, meta, guard)
