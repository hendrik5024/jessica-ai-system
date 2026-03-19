from .cognitive_stability_engine import CognitiveStabilityEngine
from .cognitive_stability_record import CognitiveStabilityRecord


class CognitiveStabilityOrchestrator:

    def __init__(self):
        self.engine = CognitiveStabilityEngine()

    def evaluate(
        self,
        stability_id: str,
        reasoning_score: float,
        consistency_score: float,
    ) -> CognitiveStabilityRecord:

        return self.engine.evaluate(
            stability_id,
            reasoning_score,
            consistency_score,
        )
