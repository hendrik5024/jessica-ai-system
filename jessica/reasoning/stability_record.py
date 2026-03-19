from dataclasses import dataclass


@dataclass(frozen=True)
class StabilityRecord:
    stability_id: str
    arbitration_id: str
    consistent: bool
    previous_answer: str
    current_answer: str
    note: str
