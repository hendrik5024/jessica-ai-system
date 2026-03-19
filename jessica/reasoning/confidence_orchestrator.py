from .confidence_calibrator import ConfidenceCalibrator
from .confidence_record import ConfidenceRecord


class ConfidenceOrchestrator:

    def __init__(self):
        self.calibrator = ConfidenceCalibrator()

    def compute(
        self,
        confidence_id: str,
        reasoning_id: str,
        integrity_passed: bool,
        arbitration_confidence: float,
        reasoning_paths: int,
        stability_passed: bool,
    ) -> ConfidenceRecord:

        return self.calibrator.calibrate(
            confidence_id,
            reasoning_id,
            integrity_passed,
            arbitration_confidence,
            reasoning_paths,
            stability_passed,
        )
