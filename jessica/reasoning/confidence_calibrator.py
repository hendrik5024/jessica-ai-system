from .confidence_record import ConfidenceRecord


class ConfidenceCalibrator:

    def calibrate(
        self,
        confidence_id: str,
        reasoning_id: str,
        integrity_passed: bool,
        arbitration_confidence: float,
        reasoning_paths: int,
        stability_passed: bool,
    ) -> ConfidenceRecord:

        base = arbitration_confidence

        if not integrity_passed:
            base *= 0.6

        if not stability_passed:
            base *= 0.7

        if reasoning_paths >= 3:
            base *= 1.05

        final_confidence = max(0.0, min(1.0, base))

        return ConfidenceRecord(
            confidence_id=confidence_id,
            reasoning_id=reasoning_id,
            integrity_passed=integrity_passed,
            arbitration_confidence=arbitration_confidence,
            reasoning_paths=reasoning_paths,
            stability_passed=stability_passed,
            final_confidence=final_confidence,
        )
