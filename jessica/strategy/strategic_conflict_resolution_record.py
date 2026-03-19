from dataclasses import dataclass


@dataclass(frozen=True)
class StrategicConflictResolutionRecord:
    resolution_id: str
    conflicting_plan_count: int
    resolution_strategy: str
    advisory: str
