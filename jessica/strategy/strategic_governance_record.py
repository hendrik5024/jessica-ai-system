from dataclasses import dataclass


@dataclass(frozen=True)
class StrategicGovernanceRecord:
    governance_id: str
    plan_count: int
    stability_state: str
    advisory: str
