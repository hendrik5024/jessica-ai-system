from dataclasses import dataclass


@dataclass(frozen=True)
class StrategicStabilityRecord:
    stability_id: str
    monitored_plan_count: int
    stability_level: str
    advisory: str
