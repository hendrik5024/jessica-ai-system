from .equilibrium_record import CognitiveEquilibriumRecord
from .guardrail_record import GuardrailRecord
from .metacognition_record import MetaCognitionRecord


class CognitiveEquilibriumEngine:

    def evaluate(
        self,
        equilibrium_id: str,
        meta: MetaCognitionRecord,
        guard: GuardrailRecord,
    ) -> CognitiveEquilibriumRecord:

        if guard.reflex_level == "HIGH":
            state = "UNSTABLE"
            score = 0.4
        elif guard.reflex_level == "MEDIUM":
            state = "MODERATE"
            score = 0.7
        else:
            state = "STABLE"
            score = 0.95

        return CognitiveEquilibriumRecord(
            equilibrium_id,
            state,
            score,
            "System cognitive equilibrium advisory",
        )
