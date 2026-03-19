from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrityRecord:
    integrity_id: str
    reasoning_id: str
    multi_reasoning_present: bool
    arbitration_present: bool
    final_answer_present: bool
    integrity_passed: bool
