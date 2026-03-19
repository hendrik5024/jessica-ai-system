from .consistency_validator import ReasoningConsistencyValidator
from .consistency_record import ConsistencyRecord


class ReasoningConsistencyOrchestrator:

    def __init__(self):
        self.validator = ReasoningConsistencyValidator()

    def analyze(self, reasoning_id: str, reasoning_steps: list[str]) -> ConsistencyRecord:
        return self.validator.validate(reasoning_id, reasoning_steps)
