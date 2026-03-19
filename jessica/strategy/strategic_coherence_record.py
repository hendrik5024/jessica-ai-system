from dataclasses import dataclass


@dataclass(frozen=True)
class StrategicCoherenceRecord:
    cycle_id: str
    strategic_direction: str
