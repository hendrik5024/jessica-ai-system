from dataclasses import dataclass


@dataclass(frozen=True)
class ConsistencyMonitorRecord:
    monitor_id: str
    evaluated_items: int
    consistency_score: float
    contradiction_detected: bool
    drift_detected: bool
    notes: str
