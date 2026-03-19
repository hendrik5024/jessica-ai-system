from dataclasses import dataclass


@dataclass(frozen=True)
class MetaCognitionRecord:
    record_id: str
    reasoning_score: float
    consistency_score: float
    stability_level: str
    drift_detected: bool
    overall_status: str
    notes: str
