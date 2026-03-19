from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceRecord:
    confidence_id: str
    reasoning_id: str
    integrity_passed: bool
    arbitration_confidence: float
    reasoning_paths: int
    stability_passed: bool
    final_confidence: float
