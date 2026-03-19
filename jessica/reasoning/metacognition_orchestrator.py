from .metacognition_engine import MetaCognitionEngine
from .metacognition_record import MetaCognitionRecord


class MetaCognitionOrchestrator:

    def __init__(self):
        self.engine = MetaCognitionEngine()

    def evaluate(
        self,
        record_id: str,
        reasoning_score: float,
        consistency_score: float,
        stability_level: str,
        drift_detected: bool,
    ) -> MetaCognitionRecord:

        return self.engine.evaluate(
            record_id,
            reasoning_score,
            consistency_score,
            stability_level,
            drift_detected,
        )
