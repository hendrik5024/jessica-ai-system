from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DriftAssessment:
    drift_detected: bool
    drift_score: float
    explanation: str
    assessed_at: datetime
