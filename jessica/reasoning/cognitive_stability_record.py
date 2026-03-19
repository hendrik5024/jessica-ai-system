from dataclasses import dataclass


@dataclass(frozen=True)
class CognitiveStabilityRecord:
    stability_id: str
    reasoning_score: float
    consistency_score: float
    stability_level: str
    instability_detected: bool
    notes: str
