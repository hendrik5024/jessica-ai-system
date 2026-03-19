from .reasoning_arbitrator import ReasoningArbitrator
from .arbitration_record import ArbitrationRecord


class ArbitrationOrchestrator:

    def __init__(self):
        self.arbitrator = ReasoningArbitrator()

    def decide(
        self,
        arbitration_id: str,
        answers: list[str],
        alignment_score: float,
        confidence_scores: list[float],
    ) -> ArbitrationRecord:

        return self.arbitrator.arbitrate(
            arbitration_id,
            answers,
            alignment_score,
            confidence_scores,
        )
