from dataclasses import dataclass


@dataclass(frozen=True)
class StrategicCorrectionRecord:
    correction_id: str
    stability_level: str
    recommendation: str
