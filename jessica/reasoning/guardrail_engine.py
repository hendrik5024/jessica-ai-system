from .guardrail_record import GuardrailRecord
from .metacognition_record import MetaCognitionRecord


class GuardrailEngine:

    def evaluate(self, guardrail_id: str, meta: MetaCognitionRecord) -> GuardrailRecord:

        if meta.overall_status == "ATTENTION_REQUIRED":
            level = "HIGH"
            verify = True
            monitor = True
        elif meta.overall_status == "STABLE":
            level = "MEDIUM"
            verify = True
            monitor = False
        else:
            level = "LOW"
            verify = False
            monitor = False

        return GuardrailRecord(
            guardrail_id,
            level,
            verify,
            monitor,
            "Deterministic cognitive guardrail advisory",
        )
