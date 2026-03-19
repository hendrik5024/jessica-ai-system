from dataclasses import dataclass


@dataclass(frozen=True)
class MetaReflectionRecord:
    reflection_id: str
    reasoning_id: str
    reasoning_paths: int
    integrity_passed: bool
    stability_passed: bool
    confidence_score: float
    reasoning_quality: float
    uncertainty_level: float
    notes: str
