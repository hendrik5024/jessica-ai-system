from .strategic_correction_engine import StrategicCorrectionEngine
from .strategic_correction_record import StrategicCorrectionRecord


class StrategicCorrectionOrchestrator:

    def __init__(self):
        self.engine = StrategicCorrectionEngine()

    def recommend(
        self,
        correction_id: str,
        stability_level: str,
    ) -> StrategicCorrectionRecord:

        return self.engine.recommend(correction_id, stability_level)
