from .guardrail_engine import GuardrailEngine
from .guardrail_record import GuardrailRecord
from .metacognition_record import MetaCognitionRecord


class GuardrailOrchestrator:

    def __init__(self):
        self.engine = GuardrailEngine()

    def evaluate(self, guardrail_id: str, meta: MetaCognitionRecord) -> GuardrailRecord:
        return self.engine.evaluate(guardrail_id, meta)
